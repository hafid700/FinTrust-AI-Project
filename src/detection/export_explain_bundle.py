"""A6b - Paquet d'explication pour la Personne B (SHAP / Integrated Gradients).

Pour chaque alerte : embeddings h_src et h_dst (contexte réseau fixé par le GNN), features x,
logit du modèle. + un jeu de fond (background) de transactions de test pour SHAP.
Vérifie que le logit recalculé à partir du paquet égale celui du fichier de scores.

    python -m src.detection.export_explain_bundle
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from src.common.alert import load_alerts
from src.detection.fed_data import build_client_views
from src.detection.federated import ClientData
from src.detection.gnn import EdgeGNN


@torch.no_grad()
def build_bundle(df, ckpt_path, tx_ids, n_background=500, seed=42, device="cpu"):
    ck = torch.load(ckpt_path, map_location=device, weights_only=True)
    model = EdgeGNN(ck["edge_dim"], ck["hidden"], ck["layers"]).to(device)
    model.load_state_dict(ck["state_dict"])
    model.eval()
    views, info = build_client_views(df, ck["n_clients"], ck["partition"], ck["seed"])
    if info["feature_names"] != ck["feature_names"]:
        raise ValueError("Les features reconstruites ne correspondent pas au checkpoint (données différentes ?).")

    wanted = np.asarray(tx_ids, dtype=np.int64)
    rng = np.random.default_rng(seed)
    cols = ("tx_id", "client", "h_src", "h_dst", "x", "logit")
    alert, bg = {c: [] for c in cols}, {c: [] for c in cols}
    for v in views:
        cd = ClientData(v, device)
        ei, ea, sel, _, tx = cd.graph(2)                    # graphe complet, arêtes de test possédées
        if len(sel) == 0:
            continue
        h = model.embed(cd.n, ei, ea)
        hs, hd, x = h[ei[0][sel]], h[ei[1][sel]], ea[sel]
        logit = model.cls(torch.cat([hs, hd, x], dim=1)).squeeze(-1)
        tx_np = tx.cpu().numpy()
        take_alert = np.isin(tx_np, wanted)
        rest = np.where(~take_alert)[0]
        take_bg = rest[rng.choice(len(rest), min(len(rest), n_background // len(views) + 1), replace=False)]
        for store, idx in ((alert, np.where(take_alert)[0]), (bg, take_bg)):
            it = torch.as_tensor(idx, dtype=torch.long, device=hs.device)
            store["tx_id"].append(tx_np[idx])
            store["client"].append(np.full(len(idx), v.client))
            store["h_src"].append(hs[it].cpu().numpy())
            store["h_dst"].append(hd[it].cpu().numpy())
            store["x"].append(x[it].cpu().numpy())
            store["logit"].append(logit[it].cpu().numpy())
    cat = lambda d: {k: np.concatenate(v) for k, v in d.items()}
    return cat(alert), cat(bg), ck


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="checkpoints/fed3_balanced_fedavg_seed42.pt")
    ap.add_argument("--parquet", default="data/processed/hi_small_sub.parquet")
    ap.add_argument("--alerts", default="reports/a6/alerts_fedavg.jsonl")
    ap.add_argument("--scores", default="reports/a4/fed3_balanced_fedavg_scores.npz")
    ap.add_argument("--out", default="reports/a6")
    a = ap.parse_args()

    df = pd.read_parquet(a.parquet)
    if not df["timestamp"].is_monotonic_increasing:
        df = df.sort_values("timestamp", kind="stable").reset_index(drop=True)
    tx_ids = [al.tx_id for al in load_alerts(a.alerts)]
    alert, bg, ck = build_bundle(df, a.ckpt, tx_ids)

    s = np.load(a.scores)
    ref = dict(zip(s["test_tx_id"], s["test_logit"]))
    dev = float(np.max(np.abs(alert["logit"] - np.array([ref[t] for t in alert["tx_id"]]))))
    print(f"alertes retrouvées : {len(alert['tx_id'])}/{len(tx_ids)} | écart max de logit vs scores : {dev:.2e}")
    if len(alert["tx_id"]) != len(tx_ids) or dev > 1e-3:
        print("ATTENTION : le checkpoint ne correspond pas au fichier de scores / aux alertes. "
              "Régénérez scores, alertes et paquet depuis le même entraînement.")

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "explain_bundle_fedavg.npz", feature_names=np.array(ck["feature_names"]),
                        hidden=ck["hidden"], **alert, **{f"bg_{k}": v for k, v in bg.items()})
    (out / "feature_names.json").write_text(json.dumps(ck["feature_names"], indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
