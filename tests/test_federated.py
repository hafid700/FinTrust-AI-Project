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


def test_explain_bundle_matches_scores(fake_csv, tmp_path):
    pytest.importorskip("torch")
    from src.detection.export_explain_bundle import build_bundle
    from src.detection.federated import run_experiment
    from src.detection.fedavg_head import head_logit, load_head

    df = load_transactions(str(fake_csv))
    run_experiment(df, scenarios=("fedavg",), rounds=2, local_epochs=1, hidden=8, layers=1, patience=5,
                   out_dir=str(tmp_path), device="cpu", ckpt_dir=str(tmp_path / "ck"))
    ckpt = str(tmp_path / "ck" / "fed3_balanced_fedavg_seed42.pt")
    sc = np.load(tmp_path / "fed3_balanced_fedavg_scores.npz")
    wanted = sc["test_tx_id"][:25]
    alert, bg, ck = build_bundle(df, ckpt, wanted, n_background=30)
    ref = dict(zip(sc["test_tx_id"], sc["test_logit"]))
    assert len(alert["tx_id"]) == len(wanted)
    assert np.max(np.abs(alert["logit"] - np.array([ref[t] for t in alert["tx_id"]]))) < 1e-4
    assert alert["x"].shape[1] == len(ck["feature_names"]) and alert["h_src"].shape[1] == ck["hidden"]
    assert len(bg["tx_id"]) > 0
    head, names, _ = load_head(ckpt)
    rec = head_logit(head, alert["h_src"], alert["h_dst"], alert["x"])
    assert np.max(np.abs(rec - alert["logit"])) < 1e-4
