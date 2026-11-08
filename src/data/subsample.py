"""A1 - Sous-échantillonnage par comptes, qui préserve la structure du graphe.

Principe : on garde TOUS les comptes impliqués dans une transaction illicite
(pour ne pas perdre les circuits de blanchiment), plus une fraction p des autres
comptes, puis on ne garde que les transactions dont les deux extrémités sont
conservées (sous-graphe induit). p est ajusté par dichotomie pour viser
`target_tx` transactions.

Attention : le taux d'illicite du sous-échantillon est PLUS ÉLEVÉ que celui du
jeu complet. À documenter dans les résultats (et à garder en tête pour la
calibration).
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from .load import assign_node_ids


def subsample_by_accounts(df: pd.DataFrame, target_tx: int, seed: int = 42) -> pd.DataFrame:
    n_nodes = int(max(df["src"].max(), df["dst"].max())) + 1
    src, dst = df["src"].to_numpy(), df["dst"].to_numpy()
    ill = df["is_laundering"].to_numpy() == 1

    illicit_nodes = np.zeros(n_nodes, dtype=bool)
    illicit_nodes[src[ill]] = True
    illicit_nodes[dst[ill]] = True

    u = np.random.default_rng(seed).random(n_nodes)  # tirage fixe -> monotone en p

    def keep_mask(p: float) -> np.ndarray:
        return illicit_nodes | (u < p)

    def n_edges(p: float) -> int:
        k = keep_mask(p)
        return int((k[src] & k[dst]).sum())

    if n_edges(0.0) >= target_tx:
        warnings.warn(f"Les seuls comptes illicites donnent déjà {n_edges(0.0)} transactions "
                      f"(cible {target_tx}). Sous-échantillon = comptes illicites uniquement.")
        p = 0.0
    elif n_edges(1.0) <= target_tx:
        p = 1.0
    else:
        lo, hi = 0.0, 1.0
        for _ in range(30):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if n_edges(mid) < target_tx else (lo, mid)
        p = hi

    k = keep_mask(p)
    out = df[k[src] & k[dst]].reset_index(drop=True)
    # Ré-indexation des noeuds 0..n-1
    return assign_node_ids(out.drop(columns=["src", "dst"]))
