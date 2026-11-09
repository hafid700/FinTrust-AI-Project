"""A2 - Construction du graphe PyTorch Geometric + split temporel.

Modèle : noeud = compte, arête orientée = transaction. La tâche est la
classification d'ARÊTES (chaque transaction est licite ou illicite).

Règles anti-fuite :
  * split par date (train < val < test), jamais aléatoire ;
  * normalisation calculée sur le train uniquement ;
  * pendant l'entraînement/évaluation, on n'utilise que le graphe des arêtes
    dont le split est <= au split évalué (`subgraph_up_to`).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

SPLITS = {"train": 0, "val": 1, "test": 2}


def temporal_split(df: pd.DataFrame, train_frac: float = 0.6, val_frac: float = 0.2) -> np.ndarray:
    """0 = train, 1 = val, 2 = test, selon les quantiles de la date."""
    ts = df["timestamp"].astype("int64").to_numpy()
    t_train = np.quantile(ts, train_frac, method="lower")
    t_val = np.quantile(ts, train_frac + val_frac, method="lower")
    return np.where(ts <= t_train, 0, np.where(ts <= t_val, 1, 2)).astype(np.int8)


def build_edge_features(df: pd.DataFrame, split: np.ndarray) -> tuple[np.ndarray, list[str]]:
    """Matrice de features d'arêtes (float32) et noms des colonnes."""
    cols, names = [], []
    train = split == 0

    # Montants : log1p puis standardisation avec les stats du TRAIN uniquement
    for c in ("amount_paid", "amount_received"):
        v = np.log1p(df[c].to_numpy(dtype=np.float64))
        mu, sd = v[train].mean(), v[train].std() + 1e-8
        cols.append(((v - mu) / sd)[:, None]); names.append(f"log_{c}")

    cols.append((df["payment_currency"] == df["receiving_currency"]).to_numpy(np.float32)[:, None])
    names.append("same_currency")
    cols.append((df["from_bank"] != df["to_bank"]).to_numpy(np.float32)[:, None])
    names.append("cross_bank")

    hour = df["timestamp"].dt.hour.to_numpy() + df["timestamp"].dt.minute.to_numpy() / 60.0
    cols.append(np.sin(2 * np.pi * hour / 24)[:, None]); names.append("hour_sin")
    cols.append(np.cos(2 * np.pi * hour / 24)[:, None]); names.append("hour_cos")

    # One-hot (catégories = valeurs présentes ; pas de fuite de labels)
    for c in ("payment_format", "payment_currency"):
        d = pd.get_dummies(df[c], prefix=c, dtype=np.float32)
        cols.append(d.to_numpy()); names += list(d.columns)

    return np.hstack(cols).astype(np.float32), names


def standardize_with_train(X: np.ndarray, split: np.ndarray) -> np.ndarray:
    """Centre/réduit chaque colonne avec la moyenne et l'écart-type du TRAIN uniquement."""
    mu = X[split == 0].mean(axis=0)
    sd = X[split == 0].std(axis=0) + 1e-6
    return ((X - mu) / sd).astype(np.float32)


def build_pyg_data(df: pd.DataFrame, train_frac: float = 0.6, val_frac: float = 0.2,
                   graph_features: bool = False):
    import torch
    from torch_geometric.data import Data

    split = temporal_split(df, train_frac, val_frac)
    X, names = build_edge_features(df, split)
    if graph_features:
        from .graph_features import build_graph_features
        G, gnames = build_graph_features(df)
        X = np.hstack([X, standardize_with_train(G, split)])
        names = names + gnames
    n_nodes = int(max(df["src"].max(), df["dst"].max())) + 1
    data = Data(
        x=torch.ones(n_nodes, 1),   # pas de features de noeud pour l'instant (voir A3)
        edge_index=torch.tensor(np.vstack([df["src"].to_numpy(), df["dst"].to_numpy()]), dtype=torch.long),
        edge_attr=torch.from_numpy(X),
        y=torch.tensor(df["is_laundering"].to_numpy(), dtype=torch.long),
        edge_split=torch.from_numpy(split.astype(np.int64)),
        tx_id=torch.tensor(df["tx_id"].to_numpy(), dtype=torch.long),
        from_bank=torch.tensor(df["from_bank"].to_numpy(), dtype=torch.long),
        to_bank=torch.tensor(df["to_bank"].to_numpy(), dtype=torch.long),
    )
    data.edge_feature_names = names
    return data


EDGE_KEYS = ("edge_attr", "y", "edge_split", "tx_id", "from_bank", "to_bank")


def subgraph_up_to(data, split_name: str):
    """Graphe contenant uniquement les arêtes de split <= split_name.

    train -> graphe train ; val -> train+val ; test -> tout le graphe.
    Les étiquettes à évaluer se sélectionnent ensuite avec `sub.edge_split == SPLITS[split_name]`.
    """
    from torch_geometric.data import Data

    mask = data.edge_split <= SPLITS[split_name]
    sub = Data(x=data.x, edge_index=data.edge_index[:, mask])
    for k in EDGE_KEYS:
        sub[k] = data[k][mask]
    sub.edge_feature_names = data.edge_feature_names
    return sub


def split_summary(df: pd.DataFrame, split: np.ndarray) -> dict:
    out = {}
    for name, k in SPLITS.items():
        m = split == k
        sub = df[m]
        out[name] = {
            "n_transactions": int(m.sum()),
            "n_illicit": int(sub["is_laundering"].sum()),
            "illicit_rate_pct": round(100 * float(sub["is_laundering"].mean()), 4) if m.any() else None,
            "from": str(sub["timestamp"].min()), "to": str(sub["timestamp"].max()),
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", default="data/processed/hi_small_sub.parquet")
    ap.add_argument("--out", default=None)
    ap.add_argument("--report", default=None)
    ap.add_argument("--graph-features", action="store_true",
                    help="ajoute les features de graphe causales aux features d'arête")
    a = ap.parse_args()
    suffix = "_gf" if a.graph_features else ""
    a.out = a.out or f"data/processed/graph{suffix}.pt"
    a.report = a.report or f"reports/a2/split_summary{suffix}.json"

    import torch

    df = pd.read_parquet(a.parquet)
    data = build_pyg_data(df, graph_features=a.graph_features)
    summary = split_summary(df, data.edge_split.numpy())
    summary["n_nodes"] = int(data.num_nodes)
    summary["n_edges"] = int(data.edge_index.shape[1])
    summary["edge_features"] = data.edge_feature_names

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    torch.save(data, a.out)
    Path(a.report).parent.mkdir(parents=True, exist_ok=True)
    Path(a.report).write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
