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


def best_f1_threshold(y_true, y_score) -> float:
    """Seuil qui maximise le F1 (à choisir sur la VALIDATION, pas sur le test)."""
    p, r, t = precision_recall_curve(y_true, y_score)
    f = 2 * p[:-1] * r[:-1] / np.clip(p[:-1] + r[:-1], 1e-12, None)
    return float(t[int(np.argmax(f))])


def summarize(y_true, y_score, threshold: float | None = None, min_precision: float = 0.5) -> dict:
    """Résumé standard. `lift` = PR-AUC / taux d'illicite : comparable entre splits
    dont le taux de base diffère (0,65 % en train, 2 % en test...)."""
    y_true = np.asarray(y_true)
    prev = float(y_true.mean())
    ap = pr_auc(y_true, y_score)
    out = {
        "n": int(len(y_true)), "n_pos": int(y_true.sum()), "prevalence": prev,
        "pr_auc": ap, "lift": ap / prev if prev > 0 else None,
        "best_f1_oracle": best_f1(y_true, y_score),
        f"recall_at_precision_{min_precision}": recall_at_precision(y_true, y_score, min_precision),
    }
    if threshold is not None:
        out["threshold"] = float(threshold)
        out["f1_at_threshold"] = f1_at_threshold(y_true, y_score, threshold)
    return out
