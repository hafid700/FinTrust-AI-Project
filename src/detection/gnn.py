"""A3 - GNN de classification d'ARÊTES (PyTorch pur, message passing explicite).

Chaque couche envoie des messages dans les DEUX sens (émetteur -> destinataire et
destinataire -> émetteur), en tenant compte des features de l'arête. Les noeuds
démarrent avec leurs log-degrés (entrant/sortant) calculés sur le graphe courant.
Le classifieur d'arête voit [h_src, h_dst, features de l'arête].

    python -m src.detection.gnn --graph data/processed/graph.pt
"""
from __future__ import annotations

import argparse
import copy
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from src.common.metrics import best_f1_threshold, pr_auc, summarize
from src.common.seed import set_seed


class EdgeMPLayer(nn.Module):
    def __init__(self, hidden: int, edge_dim: int):
        super().__init__()
        self.msg_in = nn.Linear(hidden + edge_dim, hidden)    # message src -> dst
        self.msg_out = nn.Linear(hidden + edge_dim, hidden)   # message dst -> src
        self.self_lin = nn.Linear(hidden, hidden)
        self.norm = nn.LayerNorm(hidden)

    def forward(self, h, edge_index, edge_attr):
        src, dst = edge_index
        n = h.size(0)
        m_in = F.relu(self.msg_in(torch.cat([h[src], edge_attr], dim=1)))
        m_out = F.relu(self.msg_out(torch.cat([h[dst], edge_attr], dim=1)))
        agg_in = torch.zeros_like(h).index_add_(0, dst, m_in)
        agg_out = torch.zeros_like(h).index_add_(0, src, m_out)
        deg_in = torch.bincount(dst, minlength=n).clamp(min=1).unsqueeze(1).to(h.dtype)
        deg_out = torch.bincount(src, minlength=n).clamp(min=1).unsqueeze(1).to(h.dtype)
        out = self.self_lin(h) + agg_in / deg_in + agg_out / deg_out   # agrégation par moyenne
        return h + F.relu(self.norm(out))                               # connexion résiduelle


class EdgeGNN(nn.Module):
    def __init__(self, edge_dim: int, hidden: int = 64, layers: int = 2, dropout: float = 0.2):
        super().__init__()
        self.node_in = nn.Linear(2, hidden)
        self.layers = nn.ModuleList([EdgeMPLayer(hidden, edge_dim) for _ in range(layers)])
        self.cls = nn.Sequential(nn.Linear(2 * hidden + edge_dim, hidden), nn.ReLU(),
                                 nn.Dropout(dropout), nn.Linear(hidden, 1))

    def forward(self, num_nodes: int, edge_index, edge_attr, sel):
        src, dst = edge_index
        deg = torch.stack([torch.bincount(dst, minlength=num_nodes),
                           torch.bincount(src, minlength=num_nodes)], dim=1).to(edge_attr.dtype)
        h = F.relu(self.node_in(torch.log1p(deg)))
        for layer in self.layers:
            h = layer(h, edge_index, edge_attr)
        z = torch.cat([h[src[sel]], h[dst[sel]], edge_attr[sel]], dim=1)
        return self.cls(z).squeeze(-1)


@torch.no_grad()
def predict(model, g, sel, device) -> np.ndarray:
    model.eval()
    out = model(g.num_nodes, g.edge_index.to(device), g.edge_attr.to(device), sel.to(device))
    return out.cpu().numpy()


def main() -> None:
    from src.data.graph import SPLITS, subgraph_up_to

    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", default="data/processed/graph.pt")
    ap.add_argument("--out", default="reports/a3")
    ap.add_argument("--hidden", type=int, default=64)
    ap.add_argument("--layers", type=int, default=2)
    ap.add_argument("--epochs", type=int, default=400)
    ap.add_argument("--lr", type=float, default=3e-3)
    ap.add_argument("--patience", type=int, default=8)
    ap.add_argument("--eval-every", type=int, default=5)
    ap.add_argument("--pos-weight-power", type=float, default=0.5,
                    help="pos_weight = (neg/pos)**power ; 0 = pas de pondération")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--name", default="gnn")
    a = ap.parse_args()

    set_seed(a.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    data = torch.load(a.graph, weights_only=False)   # objet PyG : weights_only=False nécessaire

    g_tr, g_va, g_te = (subgraph_up_to(data, s) for s in ("train", "val", "test"))
    sel_tr = torch.where(g_tr.edge_split == SPLITS["train"])[0]
    sel_va = torch.where(g_va.edge_split == SPLITS["val"])[0]
    sel_te = torch.where(g_te.edge_split == SPLITS["test"])[0]
    y_tr, y_va, y_te = g_tr.y[sel_tr], g_va.y[sel_va], g_te.y[sel_te]

    pos, neg = int((y_tr == 1).sum()), int((y_tr == 0).sum())
    pw = (neg / max(pos, 1)) ** a.pos_weight_power
    model = EdgeGNN(g_tr.edge_attr.shape[1], a.hidden, a.layers).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    opt = torch.optim.Adam(model.parameters(), lr=a.lr, weight_decay=1e-5)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(pw, device=device))
    print(f"device={device} | params={n_params:,} | pos_weight={pw:.1f} | "
          f"train {len(sel_tr):,} arêtes ({pos} illicites)")

    ei_tr, ea_tr = g_tr.edge_index.to(device), g_tr.edge_attr.to(device)
    sel_tr_d, y_tr_d = sel_tr.to(device), y_tr.float().to(device)
    best, best_state, bad, history = -1.0, None, 0, []
    t0 = time.time()
    for ep in range(1, a.epochs + 1):
        model.train()
        opt.zero_grad()
        loss = loss_fn(model(g_tr.num_nodes, ei_tr, ea_tr, sel_tr_d), y_tr_d)
        loss.backward()
        opt.step()
        if ep % a.eval_every == 0 or ep == a.epochs:
            ap_val = pr_auc(y_va.numpy(), predict(model, g_va, sel_va, device))
            history.append({"epoch": ep, "loss": float(loss), "val_pr_auc": ap_val})
            print(f"epoch {ep:3d} | loss {loss.item():.4f} | val PR-AUC {ap_val:.4f} | {time.time() - t0:.0f}s")
            if ap_val > best:
                best, best_state, bad = ap_val, copy.deepcopy(model.state_dict()), 0
            else:
                bad += 1
                if bad >= a.patience:
                    print("early stopping"); break
    train_time = time.time() - t0

    model.load_state_dict(best_state)
    l_va, l_te = predict(model, g_va, sel_va, device), predict(model, g_te, sel_te, device)
    p_va, p_te = 1 / (1 + np.exp(-l_va)), 1 / (1 + np.exp(-l_te))
    thr = best_f1_threshold(y_va.numpy(), p_va)
    res = {"model": a.name, "layers": a.layers, "hidden": a.hidden, "n_params": n_params,
           "train_time_s": round(train_time, 1), "device": str(device), "history": history,
           "val": summarize(y_va.numpy(), p_va, thr), "test": summarize(y_te.numpy(), p_te, thr)}

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / f"{a.name}.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    np.savez(out / f"{a.name}_scores.npz",
             val_tx_id=g_va.tx_id[sel_va].numpy(), val_y=y_va.numpy(), val_logit=l_va,
             test_tx_id=g_te.tx_id[sel_te].numpy(), test_y=y_te.numpy(), test_logit=l_te)
    Path("models").mkdir(exist_ok=True)
    torch.save(best_state, f"models/{a.name}.pt")
    print(json.dumps({k: res[k] for k in ("val", "test")}, indent=2))


if __name__ == "__main__":
    main()
