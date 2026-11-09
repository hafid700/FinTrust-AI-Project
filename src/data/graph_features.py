"""A3 - Features de graphe CAUSALES calculées à la main (pas de fuite du futur).

Pour chaque transaction i (triée par date), on compte et on somme uniquement les
transactions STRICTEMENT antérieures (position < i), éventuellement limitées à une
fenêtre de temps (ex. 24 h). Ce sont les signaux classiques du blanchiment :
  * activité passée de l'émetteur et du destinataire (entrant / sortant) ;
  * « passthrough » : log(sorties) - log(entrées), signature d'un compte relais (mule) ;
  * répétition de la paire (src, dst) et de la paire inverse (aller-retour, cycle simple).

Calcul vectorisé : index trié par clé (noeud, position) + recherche dichotomique.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


class _EventIndex:
    """Événements (noeud, position, valeur) triés par (noeud, position)."""

    def __init__(self, nodes: np.ndarray, pos: np.ndarray, vals: np.ndarray, M: int):
        key = nodes.astype(np.int64) * M + pos
        order = np.argsort(key, kind="stable")
        self.keys = key[order]
        self.cs = np.concatenate([[0.0], np.cumsum(vals[order], dtype=np.float64)])
        self.M = M

    def query(self, q_nodes: np.ndarray, hi: np.ndarray, lo: np.ndarray):
        """Nb et somme des événements du noeud avec lo <= position < hi."""
        base = q_nodes.astype(np.int64) * self.M
        h = np.searchsorted(self.keys, base + hi, side="left")
        l = np.searchsorted(self.keys, base + lo, side="left")
        return (h - l).astype(np.float64), self.cs[h] - self.cs[l]


def build_graph_features(df: pd.DataFrame, windows=(1440, None)) -> tuple[np.ndarray, list[str]]:
    """windows : tailles de fenêtre en minutes (None = tout l'historique)."""
    if not df["timestamp"].is_monotonic_increasing:
        raise ValueError("df doit être trié par date (load_transactions le fait déjà).")
    E = len(df)
    pos = np.arange(E, dtype=np.int64)
    src, dst = df["src"].to_numpy(np.int64), df["dst"].to_numpy(np.int64)
    ts = ((df["timestamp"] - df["timestamp"].min()).dt.total_seconds().to_numpy() // 60).astype(np.int64)
    M = E + 1

    out_idx = _EventIndex(src, pos, df["amount_paid"].to_numpy(np.float64), M)
    in_idx = _EventIndex(dst, pos, df["amount_received"].to_numpy(np.float64), M)

    feats, names = [], []
    for W in windows:
        tag = "all" if W is None else f"{W // 60}h"
        lo = np.zeros(E, np.int64) if W is None else np.searchsorted(ts, ts - W, side="left").astype(np.int64)
        for role, nodes in (("src", src), ("dst", dst)):
            c_out, s_out = out_idx.query(nodes, pos, lo)
            c_in, s_in = in_idx.query(nodes, pos, lo)
            feats += [np.log1p(c_out), np.log1p(s_out), np.log1p(c_in), np.log1p(s_in),
                      np.log1p(s_out) - np.log1p(s_in)]
            names += [f"{role}_out_cnt_{tag}", f"{role}_out_amt_{tag}", f"{role}_in_cnt_{tag}",
                      f"{role}_in_amt_{tag}", f"{role}_passthrough_{tag}"]

    n_nodes = int(max(src.max(), dst.max())) + 1
    pairs = _EventIndex(src * n_nodes + dst, pos, np.ones(E), M)
    zeros = np.zeros(E, np.int64)
    c_fwd, _ = pairs.query(src * n_nodes + dst, pos, zeros)   # même paire déjà vue
    c_rev, _ = pairs.query(dst * n_nodes + src, pos, zeros)   # paire inverse déjà vue
    feats += [np.log1p(c_fwd), np.log1p(c_rev)]
    names += ["pair_prev", "rev_pair_prev"]
    return np.column_stack(feats).astype(np.float32), names
