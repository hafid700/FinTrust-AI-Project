import numpy as np

from src.data.graph_features import build_graph_features
from src.data.load import load_transactions


def test_matches_naive_implementation(fake_csv):
    df = load_transactions(str(fake_csv)).iloc[:400].reset_index(drop=True)
    G, names = build_graph_features(df, windows=(60, None))
    ts = ((df["timestamp"] - df["timestamp"].min()).dt.total_seconds() // 60).to_numpy()
    src, dst = df["src"].to_numpy(), df["dst"].to_numpy()
    pay = df["amount_paid"].to_numpy()

    def naive(i, role_nodes, W):
        j = np.arange(len(df)) < i
        if W is not None:
            j &= ts >= ts[i] - W
        return j

    for i in (0, 7, 150, 399):
        for W, tag in ((60, "1h"), (None, "all")):
            j = naive(i, None, W)
            cnt = np.log1p((j & (src == src[i])).sum())
            amt = np.log1p(pay[j & (src == src[i])].sum())
            din = np.log1p((j & (dst == dst[i])).sum())
            assert np.isclose(G[i, names.index(f"src_out_cnt_{tag}")], cnt, atol=1e-5)
            assert np.isclose(G[i, names.index(f"src_out_amt_{tag}")], amt, rtol=1e-4)
            assert np.isclose(G[i, names.index(f"dst_in_cnt_{tag}")], din, atol=1e-5)
        pair = np.log1p(((np.arange(len(df)) < i) & (src == src[i]) & (dst == dst[i])).sum())
        rev = np.log1p(((np.arange(len(df)) < i) & (src == dst[i]) & (dst == src[i])).sum())
        assert np.isclose(G[i, names.index("pair_prev")], pair, atol=1e-5)
        assert np.isclose(G[i, names.index("rev_pair_prev")], rev, atol=1e-5)


def test_causal_first_row_is_zero(fake_csv):
    df = load_transactions(str(fake_csv))
    G, _ = build_graph_features(df)
    assert (G[0] == 0).all() and not np.isnan(G).any()
