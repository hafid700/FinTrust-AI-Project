import numpy as np
import pandas as pd
import pytest

from src.data.load import load_transactions
from src.detection.fed_data import assign_banks_to_clients, build_client_views


def _bank_df(n_banks=200, n=20000, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({"from_bank": rng.integers(0, n_banks, n), "to_bank": rng.integers(0, n_banks, n)})


def test_assign_balanced_and_skewed():
    df = _bank_df()
    for strat in ("balanced", "skewed"):
        s = assign_banks_to_clients(df, 3, strat)
        assert set(s.unique()) == {0, 1, 2}
    sc = df["from_bank"].map(assign_banks_to_clients(df, 3, "balanced"))
    shares = sc.value_counts(normalize=True)
    assert shares.max() - shares.min() < 0.05
    sk = df["from_bank"].map(assign_banks_to_clients(df, 3, "skewed")).value_counts(normalize=True)
    assert sk.loc[0] > 0.45 > sk.loc[2]


def test_client_views_structure(fake_csv):
    df = load_transactions(str(fake_csv))
    views, info = build_client_views(df, n_clients=3, strategy="balanced")
    # chaque transaction a exactement un client propriétaire (= émetteur)
    owners = np.concatenate([v.tx_id[v.owner] for v in views])
    assert len(owners) == len(df) and len(set(owners)) == len(df)
    # une transaction inter-clients apparaît dans 2 vues
    n_cross = round(info["cross_client_share_pct"] / 100 * len(df))
    assert abs(sum(len(v.y) for v in views) - (len(df) + n_cross)) <= 1
    for v in views:
        assert v.edge_attr.shape == (len(v.y), info["n_edge_features"])
        assert not np.isnan(v.edge_attr).any()
        assert v.edge_src.max() < v.num_nodes and v.edge_dst.max() < v.num_nodes
    # features de graphe centrées sur le train (toutes vues confondues, arêtes possédées)
    pool = np.vstack([v.edge_attr[v.owner & (v.split == 0)][:, 28:] for v in views])
    assert np.abs(pool.mean(axis=0)).max() < 1e-3


def test_federated_smoke(fake_csv, tmp_path):
    pytest.importorskip("torch")
    from src.detection.federated import run_experiment

    df = load_transactions(str(fake_csv))
    res = run_experiment(df, rounds=2, local_epochs=1, hidden=8, layers=1, patience=5,
                         out_dir=str(tmp_path), device="cpu")
    assert set(res) == {"local", "fedavg", "central_local"}
    for r in res.values():
        assert 0.0 <= r["test"]["pr_auc"] <= 1.0
    assert res["fedavg"]["comm_total_MB"] > 0
