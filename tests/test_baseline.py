import numpy as np
import pandas as pd

from src.common.metrics import best_f1_threshold, summarize
from src.data.load import load_transactions
from src.detection.baseline import run


def test_summarize_keys():
    y = np.array([0] * 90 + [1] * 10)
    s = np.r_[np.linspace(0, 0.5, 90), np.linspace(0.5, 1, 10)]
    r = summarize(y, s, best_f1_threshold(y, s))
    assert r["prevalence"] == 0.1 and r["lift"] > 1 and "f1_at_threshold" in r


def test_baseline_runs(fake_csv):
    df = load_transactions(str(fake_csv))
    res, scores = run(df, n_estimators=20)
    assert res["test"]["n"] == len(scores["test_y"])
    assert 0.0 <= res["test"]["pr_auc"] <= 1.0


def test_baseline_with_graph_features(fake_csv):
    df = load_transactions(str(fake_csv))
    res, _ = run(df, n_estimators=20, graph_features=True)
    assert res["model"] == "xgboost_graph_features" and res["n_features"] > 28
