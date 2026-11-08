"""Métriques communes. Pas d'accuracy : classes extrêmement déséquilibrées."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, f1_score, precision_recall_curve


def pr_auc(y_true, y_score) -> float:
    return float(average_precision_score(y_true, y_score))


def best_f1(y_true, y_score) -> float:
    """F1 maximal sur tous les seuils possibles."""
    p, r, _ = precision_recall_curve(y_true, y_score)
    f = 2 * p * r / np.clip(p + r, 1e-12, None)
    return float(f.max())


def f1_at_threshold(y_true, y_score, threshold: float = 0.5) -> float:
    return float(f1_score(y_true, (np.asarray(y_score) >= threshold).astype(int), zero_division=0))


def recall_at_precision(y_true, y_score, min_precision: float = 0.5) -> float:
    """Meilleur rappel atteignable avec une précision >= min_precision."""
    p, r, _ = precision_recall_curve(y_true, y_score)
    ok = p >= min_precision
    return float(r[ok].max()) if ok.any() else 0.0


def ece(y_true, y_prob, n_bins: int = 10) -> float:
    """Expected Calibration Error pour un score de probabilité binaire."""
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.clip(np.digitize(y_prob, bins[1:-1]), 0, n_bins - 1)
    total = 0.0
    for b in range(n_bins):
        m = idx == b
        if m.any():
            total += m.mean() * abs(y_true[m].mean() - y_prob[m].mean())
    return float(total)
