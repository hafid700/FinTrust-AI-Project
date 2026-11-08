"""A1 - Chargement d'IBM AML (HI-Small_Trans.csv) dans un DataFrame propre.

Le CSV brut a deux colonnes nommées "Account" (compte émetteur, compte
destinataire) ; pandas renomme la seconde en "Account.1".
"""
from __future__ import annotations

import numpy as np
import pandas as pd

RENAME = {
    "Timestamp": "timestamp",
    "From Bank": "from_bank",
    "Account": "from_account",
    "To Bank": "to_bank",
    "Account.1": "to_account",
    "Amount Received": "amount_received",
    "Receiving Currency": "receiving_currency",
    "Amount Paid": "amount_paid",
    "Payment Currency": "payment_currency",
    "Payment Format": "payment_format",
    "Is Laundering": "is_laundering",
}


def assign_node_ids(df: pd.DataFrame) -> pd.DataFrame:
    """Un noeud = un compte, identifié par le couple (banque, compte).

    Ajoute les colonnes entières `src` et `dst` (indices 0..n_nodes-1).
    """
    keys_src = df["from_bank"].astype(str) + "_" + df["from_account"].astype(str)
    keys_dst = df["to_bank"].astype(str) + "_" + df["to_account"].astype(str)
    codes, _ = pd.factorize(pd.concat([keys_src, keys_dst], ignore_index=True))
    n = len(df)
    df = df.copy()
    df["src"] = codes[:n].astype(np.int64)
    df["dst"] = codes[n:].astype(np.int64)
    return df


def load_transactions(path: str, nrows: int | None = None) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        nrows=nrows,
        dtype={"From Bank": "int32", "To Bank": "int32", "Account": "string",
               "Account.1": "string", "Is Laundering": "int8"},
    )
    missing = set(RENAME) - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes attendues absentes : {sorted(missing)}. "
                         f"Colonnes trouvées : {list(df.columns)}")
    df = df.rename(columns=RENAME)[list(RENAME.values())]
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y/%m/%d %H:%M")
    except ValueError:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp", kind="stable").reset_index(drop=True)
    df.insert(0, "tx_id", np.arange(len(df), dtype=np.int64))
    return assign_node_ids(df)
