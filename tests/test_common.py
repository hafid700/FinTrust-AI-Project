import numpy as np
import pytest

from src.common.alert import Alert, load_alerts, save_alerts
from src.common.metrics import ece, pr_auc, recall_at_precision


def test_alert_roundtrip(tmp_path):
    a = Alert(tx_id=1, score=0.9, confidence=0.8, top_features=[("amount", 0.3)],
              neighbors=[2, 3], pattern="cycle")
    save_alerts([a], tmp_path / "alerts.jsonl")
    assert load_alerts(tmp_path / "alerts.jsonl")[0].tx_id == 1


def test_alert_validation():
    with pytest.raises(ValueError):
        Alert(tx_id=1, score=1.5, confidence=0.5)
    with pytest.raises(ValueError):
        Alert(tx_id=1, score=0.5, confidence=0.5, pattern="bizarre")


def test_metrics_perfect_and_calibration():
    y = np.array([0, 0, 0, 1, 1])
    s = np.array([0.1, 0.2, 0.3, 0.8, 0.9])
    assert pr_auc(y, s) == 1.0
    assert recall_at_precision(y, s, 0.9) == 1.0
    assert ece(np.array([0, 1] * 50), np.full(100, 0.5)) < 1e-9
