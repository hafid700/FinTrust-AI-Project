import numpy as np
import pytest

from src.data.graph import build_edge_features, split_summary, temporal_split
from src.data.load import load_transactions


def _df(fake_csv):
    return load_transactions(str(fake_csv))


def test_temporal_split_is_ordered(fake_csv):
    df = _df(fake_csv)
    s = temporal_split(df)
    ts = df["timestamp"]
    assert ts[s == 0].max() <= ts[s == 1].min()
    assert ts[s == 1].max() <= ts[s == 2].min()
    frac = [(s == k).mean() for k in range(3)]
    assert abs(frac[0] - 0.6) < 0.02 and abs(frac[1] - 0.2) < 0.02


def test_features_clean_and_train_normalised(fake_csv):
    df = _df(fake_csv)
    s = temporal_split(df)
    X, names = build_edge_features(df, s)
    assert X.shape == (len(df), len(names)) and X.dtype == np.float32
    assert not np.isnan(X).any()
    i = names.index("log_amount_paid")
    assert abs(X[s == 0, i].mean()) < 1e-3          # centré sur le train
    assert split_summary(df, s)["train"]["n_transactions"] == (s == 0).sum()


def test_pyg_data_and_subgraph(fake_csv):
    pytest.importorskip("torch_geometric")
    from src.data.graph import SPLITS, build_pyg_data, subgraph_up_to

    df = _df(fake_csv)
    data = build_pyg_data(df)
    tr, va, te = (subgraph_up_to(data, n) for n in ("train", "val", "test"))
    assert tr.edge_index.shape[1] < va.edge_index.shape[1] < te.edge_index.shape[1]
    assert te.edge_index.shape[1] == data.edge_index.shape[1]
    assert (tr.edge_split == SPLITS["train"]).all()


def test_standardize_with_train_only(fake_csv):
    from src.data.graph import standardize_with_train
    from src.data.graph_features import build_graph_features

    df = _df(fake_csv)
    s = temporal_split(df)
    G, _ = build_graph_features(df)
    Z = standardize_with_train(G, s)
    assert np.abs(Z[s == 0].mean(axis=0)).max() < 1e-3       # centré sur le train
    assert not np.isnan(Z).any()


def test_pyg_with_graph_features(fake_csv):
    pytest.importorskip("torch_geometric")
    from src.data.graph import build_pyg_data

    df = _df(fake_csv)
    base, gf = build_pyg_data(df), build_pyg_data(df, graph_features=True)
    assert gf.edge_attr.shape[1] == base.edge_attr.shape[1] + 22
    assert len(gf.edge_feature_names) == gf.edge_attr.shape[1]
