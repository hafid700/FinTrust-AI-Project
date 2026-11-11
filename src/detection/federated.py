"""A4 - Apprentissage fédéré simulé (FedAvg) sur le GNN, avec 3 points de comparaison.

Scénarios (mêmes données, même budget de calcul, même jeu de test) :
  local          : chaque client entraîne son modèle seul, sans collaboration ;
  fedavg         : FedAvg (poids moyennés par le serveur, données jamais échangées) ;
  central_local  : données mises en commun, mais mêmes vues locales (borne haute « sans fédération »).
La référence « centralisé + vue globale » est le résultat `gnn_gf` de l'étape A3.

    python -m src.detection.federated --partition balanced --scenarios local fedavg central_local
"""
from __future__ import annotations

import argparse
import copy
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from src.common.metrics import best_f1_threshold, pr_auc, summarize
from src.common.seed import set_seed
from src.detection.fed_data import build_client_views
from src.detection.gnn import EdgeGNN


class ClientData:
    """Données d'un client sur l'appareil de calcul + graphes « jusqu'à tel split »."""

    def __init__(self, v, device):
        self.n = v.num_nodes
        self.ei = torch.tensor(np.vstack([v.edge_src, v.edge_dst]), dtype=torch.long, device=device)
        self.ea = torch.from_numpy(v.edge_attr).to(device)
        self.y = torch.from_numpy(v.y).long().to(device)
        self.split = torch.from_numpy(v.split.astype(np.int64)).to(device)
        self.owner = torch.from_numpy(v.owner).to(device)
        self.tx_id = torch.from_numpy(v.tx_id).to(device)
        self._cache = {}

    def graph(self, k: int):
        """Graphe des arêtes de split <= k ; `sel` = arêtes à évaluer (split == k, possédées)."""
        if k not in self._cache:
            m = self.split <= k
            sel = torch.where((self.split[m] == k) & self.owner[m])[0]
            self._cache[k] = (self.ei[:, m], self.ea[m], sel, self.y[m][sel], self.tx_id[m][sel])
        return self._cache[k]


def safe_ap(y, logit) -> float:
    return pr_auc(y, logit) if len(y) and y.sum() > 0 else 0.0


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def local_steps(model, opt, cd, steps, loss_fn):
    ei, ea, sel, y, _ = cd.graph(0)
    if len(sel) == 0:
        return
    model.train()
    for _ in range(steps):
        opt.zero_grad()
        loss_fn(model(cd.n, ei, ea, sel), y.float()).backward()
        opt.step()


@torch.no_grad()
def predict_client(model, cd, k):
    ei, ea, sel, y, tx = cd.graph(k)
    if len(sel) == 0:
        return np.array([], dtype=np.int64), np.array([], dtype=np.int64), np.array([], dtype=np.float32)
    model.eval()
    return tx.cpu().numpy(), y.cpu().numpy(), model(cd.n, ei, ea, sel).cpu().numpy()


def concat(parts):
    return tuple(np.concatenate([p[i] for p in parts]) for i in range(3))


def fedavg_aggregate(states, weights):
    tot = float(sum(weights))
    return {k: sum(s[k].float() * (w / tot) for s, w in zip(states, weights)) for k in states[0]}


def run_experiment(df, scenarios=("local", "fedavg", "central_local"), partition="balanced", n_clients=3,
                   rounds=40, local_epochs=5, hidden=64, layers=2, lr=3e-3, patience=10,
                   pos_weight_power=0.5, seed=42, out_dir="reports/a4", device=None):
    set_seed(seed)
    device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    views, info = build_client_views(df, n_clients, partition, seed)
    clients = [ClientData(v, device) for v in views]
    edge_dim = views[0].edge_attr.shape[1]
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    tag = f"fed{n_clients}_{partition}"
    (out / f"{tag}_info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")

    weights = [int(cd.graph(0)[2].numel()) for cd in clients]       # arêtes d'entraînement par client
    pos = sum(int(((v.y == 1) & v.owner & (v.split == 0)).sum()) for v in views)
    neg = sum(weights) - pos
    pw = (neg / max(pos, 1)) ** pos_weight_power
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(pw, device=device))
    make_model = lambda: EdgeGNN(edge_dim, hidden, layers).to(device)
    n_params = sum(p.numel() for p in make_model().parameters())
    print(f"[{tag}] device={device} | params={n_params:,} | pos_weight={pw:.1f} | "
          f"arêtes train par client={weights} | illicites inter-clients={info['illicit_cross_client_share_pct']}%")

    pool = lambda model, k: [predict_client(model, cd, k) for cd in clients]
    results = {}

    def finalize(name, val_parts, test_parts, t0, extra):
        txv, yv, lv = concat(val_parts); txt, yt, lt = concat(test_parts)
        pv, pt = sigmoid(lv), sigmoid(lt)
        thr = best_f1_threshold(yv, pv)
        per_client = [{"client": c, "n_test": int(len(p[1])), "n_pos_test": int(p[1].sum()),
                       "pr_auc": float(pr_auc(p[1], p[2])) if p[1].sum() > 0 else None}
                      for c, p in enumerate(test_parts)]
        res = {"model": f"{tag}_{name}", "scenario": name, "partition": partition, "n_clients": n_clients,
               "layers": layers, "hidden": hidden, "n_params": n_params,
               "train_time_s": round(time.time() - t0, 1), **extra,
               "val": summarize(yv, pv, thr), "test": summarize(yt, pt, thr), "per_client_test": per_client}
        (out / f"{tag}_{name}.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
        np.savez(out / f"{tag}_{name}_scores.npz", val_tx_id=txv, val_y=yv, val_logit=lv,
                 test_tx_id=txt, test_y=yt, test_logit=lt)
        results[name] = res
        print(f"[{tag}] {name:14s} test PR-AUC {res['test']['pr_auc']:.3f} | lift {res['test']['lift']:.1f}x | "
              f"F1 {res['test']['f1_at_threshold']:.3f} | {res['train_time_s']:.0f}s")

    # ---------------- local : chaque client seul ----------------
    if "local" in scenarios:
        t0, vparts, tparts = time.time(), [], []
        for cd in clients:
            model = make_model(); opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
            best, best_state = -1.0, None
            for _ in range(rounds):
                local_steps(model, opt, cd, local_epochs, loss_fn)
                _, y, l = predict_client(model, cd, 1)
                ap = safe_ap(y, l)
                if best_state is None or ap >= best:
                    best, best_state = ap, copy.deepcopy(model.state_dict())
            model.load_state_dict(best_state)
            vparts.append(predict_client(model, cd, 1)); tparts.append(predict_client(model, cd, 2))
        finalize("local", vparts, tparts, t0, {"rounds": rounds, "local_epochs": local_epochs})

    # ---------------- fedavg ----------------
    if "fedavg" in scenarios:
        t0 = time.time()
        gmodel, lmodel = make_model(), make_model()
        best, best_state, bad, history, rounds_run = -1.0, None, 0, [], 0
        for r in range(1, rounds + 1):
            gstate = copy.deepcopy(gmodel.state_dict())
            states, ws = [], []
            for cd, w in zip(clients, weights):
                if w == 0:
                    continue
                lmodel.load_state_dict(gstate)
                opt = torch.optim.Adam(lmodel.parameters(), lr=lr, weight_decay=1e-5)
                local_steps(lmodel, opt, cd, local_epochs, loss_fn)
                states.append({k: v.detach().clone() for k, v in lmodel.state_dict().items()}); ws.append(w)
            gmodel.load_state_dict(fedavg_aggregate(states, ws))
            rounds_run = r
            _, y, l = concat(pool(gmodel, 1))
            ap = safe_ap(y, l)
            history.append({"round": r, "val_pr_auc": ap})
            if r % 5 == 0 or r == 1:
                print(f"[{tag}] fedavg round {r:3d} | val PR-AUC {ap:.4f}")
            if ap > best:
                best, best_state, bad = ap, copy.deepcopy(gmodel.state_dict()), 0
            else:
                bad += 1
                if bad >= patience:
                    print(f"[{tag}] early stopping (round {r})"); break
        gmodel.load_state_dict(best_state)
        comm_mb = 2 * len(clients) * n_params * 4 * rounds_run / 1e6      # envoi + réception, float32
        finalize("fedavg", pool(gmodel, 1), pool(gmodel, 2), t0,
                 {"rounds": rounds_run, "local_epochs": local_epochs, "comm_total_MB": round(comm_mb, 1),
                  "history": history})

    # ---------------- central_local : données poolées, vues locales ----------------
    if "central_local" in scenarios:
        t0 = time.time()
        model = make_model(); opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
        N = float(sum(weights))
        best, best_state, bad, history = -1.0, None, 0, []
        for step in range(1, rounds * local_epochs + 1):
            model.train(); opt.zero_grad()
            for cd, w in zip(clients, weights):
                if w == 0:
                    continue
                ei, ea, sel, y, _ = cd.graph(0)
                (loss_fn(model(cd.n, ei, ea, sel), y.float()) * (w / N)).backward()
            opt.step()
            if step % local_epochs == 0:
                _, y, l = concat(pool(model, 1))
                ap = safe_ap(y, l)
                history.append({"step": step, "val_pr_auc": ap})
                if ap > best:
                    best, best_state, bad = ap, copy.deepcopy(model.state_dict()), 0
                else:
                    bad += 1
                    if bad >= patience:
                        print(f"[{tag}] early stopping (step {step})"); break
        model.load_state_dict(best_state)
        finalize("central_local", pool(model, 1), pool(model, 2), t0, {"history": history})
    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", default="data/processed/hi_small_sub.parquet")
    ap.add_argument("--out", default="reports/a4")
    ap.add_argument("--partition", choices=["balanced", "skewed"], default="balanced")
    ap.add_argument("--clients", type=int, default=3)
    ap.add_argument("--scenarios", nargs="+", default=["local", "fedavg", "central_local"],
                    choices=["local", "fedavg", "central_local"])
    ap.add_argument("--rounds", type=int, default=40)
    ap.add_argument("--local-epochs", type=int, default=5)
    ap.add_argument("--hidden", type=int, default=64)
    ap.add_argument("--layers", type=int, default=2)
    ap.add_argument("--lr", type=float, default=3e-3)
    ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    run_experiment(pd.read_parquet(a.parquet), tuple(a.scenarios), a.partition, a.clients, a.rounds,
                   a.local_epochs, a.hidden, a.layers, a.lr, a.patience, seed=a.seed, out_dir=a.out)


if __name__ == "__main__":
    main()
