import json

import numpy as np
import pandas as pd

from src.common.alert import load_alerts
from src.data.load import assign_node_ids, load_transactions
from src.detection.export_alerts import GraphIndex, export


def _tiny(edges):
    """edges : liste de (src_compte, dst_compte) ; une transaction par minute."""
    n = len(edges)
    df = pd.DataFrame({
        "tx_id": np.arange(n), "timestamp": pd.date_range("2022-09-01", periods=n, freq="min"),
        "from_bank": 1, "from_account": [e[0] for e in edges], "to_bank": 1, "to_account": [e[1] for e in edges],
        "amount_paid": 10.0, "amount_received": 10.0, "payment_currency": "Euro",
        "receiving_currency": "Euro", "payment_format": "ACH", "is_laundering": 0})
    return assign_node_ids(df)


def test_pattern_cycle2_cycle3_fan():
    assert GraphIndex(_tiny([("A", "B"), ("B", "A")])).pattern(1) == "cycle"
    assert GraphIndex(_tiny([("A", "B"), ("B", "C"), ("C", "A")])).pattern(2) == "cycle"
    out = [("S", f"D{i}") for i in range(6)]
    assert GraphIndex(_tiny(out)).pattern(5) == "fan_out"
    inn = [(f"S{i}", "D") for i in range(6)]
    assert GraphIndex(_tiny(inn)).pattern(5) == "fan_in"
    assert GraphIndex(_tiny([("A", "B"), ("C", "D")])).pattern(1) == "none"


def test_neighbors_are_strictly_earlier():
    df = _tiny([("A", "B"), ("A", "C"), ("B", "D"), ("A", "B")])
    nb = GraphIndex(df).neighbors(3, k=5)
    assert nb and all(n < 3 for n in nb)


def test_export_end_to_end(fake_csv, tmp_path):
    df = load_transactions(str(fake_csv))
    s = (df["timestamp"] <= df["timestamp"].quantile(0.8)) & (df["timestamp"] > df["timestamp"].quantile(0.6))
    t = df["timestamp"] > df["timestamp"].quantile(0.8)
    rng = np.random.default_rng(0)
    mk = lambda m: (df.loc[m, "tx_id"].to_numpy(), df.loc[m, "is_laundering"].to_numpy())
    (vi, vy), (ti, ty) = mk(s), mk(t)
    scores = {"val_tx_id": vi, "val_y": vy, "val_logit": vy * 3.0 + rng.normal(size=len(vy)),
              "test_tx_id": ti, "test_y": ty, "test_logit": ty * 3.0 + rng.normal(size=len(ty))}
    summ = export(df, scores, "demo", str(tmp_path), max_alerts=500, n_sample=10)
    alerts = load_alerts(tmp_path / "alerts_demo.jsonl")
    assert len(alerts) == summ["n_alerts"] > 0
    assert all("is_laundering" not in a.context and "label" not in a.context for a in alerts)
    assert (tmp_path / "alerts_labels.csv").exists() and (tmp_path / "neighbor_transactions.csv").exists()
    assert json.loads((tmp_path / "export_summary_demo.json").read_text())["model"] == "demo"
