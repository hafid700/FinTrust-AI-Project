"""A4 - Simulation de banques : répartition en clients et VUE LOCALE de chaque client.

Règles (réalistes) :
  * une banque appartient à un seul client ; un compte appartient à la banque indiquée ;
  * un client voit TOUTES les transactions qui touchent un de ses comptes (émises ou reçues).
    Les comptes des autres clients apparaissent, mais sans leur historique ;
  * chaque transaction a UN client propriétaire = le client de la banque émettrice.
    C'est lui qui l'évalue et qui s'entraîne dessus -> pas de doublon dans l'entraînement ;
  * les features de graphe sont calculées à partir de la vue locale uniquement ;
  * les features de graphe sont normalisées avec des statistiques (moyenne/écart-type)
    mises en commun sur le train : hypothèse de « prétraitement fédéré », à citer dans les limites.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.data.graph import build_edge_features, temporal_split
from src.data.graph_features import build_graph_features
from src.data.load import assign_node_ids


@dataclass
class ClientView:
    client: int
    tx_pos: np.ndarray       # positions des transactions dans le DataFrame global
    edge_src: np.ndarray     # indices de noeuds LOCAUX
    edge_dst: np.ndarray
    num_nodes: int
    edge_attr: np.ndarray    # float32 [E_local, F]
    y: np.ndarray
    split: np.ndarray        # 0 train, 1 val, 2 test
    owner: np.ndarray        # True si le client est la banque émettrice
    tx_id: np.ndarray


def assign_banks_to_clients(df: pd.DataFrame, n_clients: int = 3, strategy: str = "balanced",
                            seed: int = 42) -> pd.Series:
    """Répartit les banques entre clients (glouton, selon le volume de transactions).

    balanced : ~1/n du volume par client.   skewed : parts 1/2, 1/4, 1/8... (clients très inégaux).
    """
    counts = pd.concat([df["from_bank"], df["to_bank"]]).value_counts()
    if strategy == "balanced":
        shares = np.ones(n_clients)
    elif strategy == "skewed":
        shares = 0.5 ** np.arange(n_clients)
    else:
        raise ValueError(f"strategy inconnue : {strategy}")
    shares = shares / shares.sum()

    rng = np.random.default_rng(seed)
    order = np.lexsort((rng.random(len(counts)), -counts.to_numpy()))   # tri décroissant, égalités aléatoires
    target = shares * counts.sum()
    load = np.zeros(n_clients)
    assign = np.zeros(len(counts), dtype=np.int64)
    for i in order:
        c = int(np.argmax(target - load))
        assign[i] = c
        load[c] += counts.iloc[i]
    return pd.Series(assign, index=counts.index)


def build_client_views(df: pd.DataFrame, n_clients: int = 3, strategy: str = "balanced",
                       seed: int = 42) -> tuple[list[ClientView], dict]:
    bank_client = assign_banks_to_clients(df, n_clients, strategy, seed)
    sc = df["from_bank"].map(bank_client).to_numpy().astype(np.int64)
    dc = df["to_bank"].map(bank_client).to_numpy().astype(np.int64)
    split = temporal_split(df)
    X_base, _ = build_edge_features(df, split)
    y_all = df["is_laundering"].to_numpy()
    tx_all = df["tx_id"].to_numpy()

    raw = []
    for c in range(n_clients):
        mask = (sc == c) | (dc == c)
        sub = assign_node_ids(df[mask].drop(columns=["src", "dst"]).reset_index(drop=True))
        G, gnames = build_graph_features(sub)            # historique visible par ce client seulement
        raw.append({"mask": mask, "sub": sub, "G": G})

    # Statistiques communes (train, transactions possédées) pour normaliser les features de graphe
    pool = np.vstack([r["G"][(sc[r["mask"]] == c) & (split[r["mask"]] == 0)] for c, r in enumerate(raw)])
    mu, sd = pool.mean(axis=0), pool.std(axis=0) + 1e-6

    views = []
    for c, r in enumerate(raw):
        mask, sub = r["mask"], r["sub"]
        Gs = ((r["G"] - mu) / sd).astype(np.float32)
        views.append(ClientView(
            client=c, tx_pos=np.where(mask)[0],
            edge_src=sub["src"].to_numpy(np.int64), edge_dst=sub["dst"].to_numpy(np.int64),
            num_nodes=int(max(sub["src"].max(), sub["dst"].max())) + 1,
            edge_attr=np.hstack([X_base[mask], Gs]).astype(np.float32),
            y=y_all[mask], split=split[mask], owner=sc[mask] == c, tx_id=tx_all[mask]))

    cross = sc != dc
    info = {
        "partition": strategy, "n_clients": n_clients,
        "n_edge_features": int(views[0].edge_attr.shape[1]),
        "cross_client_share_pct": round(100 * float(cross.mean()), 2),
        "illicit_cross_client_share_pct": round(100 * float(cross[y_all == 1].mean()), 2),
        "clients": [{
            "client": v.client,
            "n_banks": int((bank_client == v.client).sum()),
            "n_local_edges": int(len(v.y)),
            "n_owner_edges": int(v.owner.sum()),
            "owner_share_pct": round(100 * float(v.owner.sum()) / len(df), 2),
            **{f"illicit_owner_{n}": int(((v.y == 1) & v.owner & (v.split == k)).sum())
               for n, k in (("train", 0), ("val", 1), ("test", 2))},
        } for v in views],
    }
    return views, info
