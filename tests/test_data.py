import numpy as np
import pandas as pd
import pytest

from src.data.load import load_transactions
from src.data.subsample import subsample_by_accounts


def test_load(fake_csv):
    df = load_transactions(str(fake_csv))
    assert {"src", "dst", "tx_id", "is_laundering"} <= set(df.columns)
    assert df["timestamp"].is_monotonic_increasing
    assert df["src"].min() >= 0


def test_subsample_keeps_illicit_accounts(fake_csv):
    df = load_transactions(str(fake_csv))
    sub = subsample_by_accounts(df, target_tx=1500, seed=1)
    assert len(sub) < len(df)
    # Toutes les transactions illicites dont les deux extrémités sont illicites par définition sont gardées
    assert sub["is_laundering"].sum() == df["is_laundering"].sum()
    n_nodes = max(sub["src"].max(), sub["dst"].max()) + 1
    assert n_nodes <= pd.concat([sub["src"], sub["dst"]]).nunique() + 1
