"""A3 - Baseline tabulaire : XGBoost sur les features de transaction SEULES (pas de graphe).

    python -m src.detection.baseline --parquet data/processed/hi_small_sub.parquet
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.metrics import best_f1_threshold, summarize
from src.common.seed import set_seed
from src.data.graph import build_edge_features, temporal_split


def run(df: pd.DataFrame, seed: int = 42, n_estimators: int = 500) -> tuple[dict, dict]:
    import xgboost as xgb

    set_seed(seed)
    split = temporal_split(df)
    X, names = build_edge_features(df, split)
    y = df["is_laundering"].to_numpy()
    tr, va, te = split == 0, split == 1, split == 2

    pw = float((y[tr] == 0).sum() / max((y[tr] == 1).sum(), 1))
    model = xgb.XGBClassifier(
        n_estimators=n_estimators, max_depth=6, learning_rate=0.1, subsample=0.8,
        colsample_bytree=0.8, scale_pos_weight=pw, eval_metric="aucpr",
        early_stopping_rounds=30, tree_method="hist", random_state=seed, n_jobs=-1,
    )
    t0 = time.time()
    model.fit(X[tr], y[tr], eval_set=[(X[va], y[va])], verbose=False)
    train_time = time.time() - t0

    p_va, p_te = model.predict_proba(X[va])[:, 1], model.predict_proba(X[te])[:, 1]
    thr = best_f1_threshold(y[va], p_va)       # seuil choisi sur la val uniquement
    res = {
        "model": "xgboost_tabular", "n_features": len(names), "train_time_s": round(train_time, 1),
        "best_iteration": int(getattr(model, "best_iteration", -1)),
        "val": summarize(y[va], p_va, thr), "test": summarize(y[te], p_te, thr),
    }
    logit = lambda p: np.log(np.clip(p, 1e-7, 1 - 1e-7) / (1 - np.clip(p, 1e-7, 1 - 1e-7)))
    scores = {
        "val_tx_id": df["tx_id"].to_numpy()[va], "val_y": y[va], "val_logit": logit(p_va),
        "test_tx_id": df["tx_id"].to_numpy()[te], "test_y": y[te], "test_logit": logit(p_te),
    }
    return res, scores


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", default="data/processed/hi_small_sub.parquet")
    ap.add_argument("--out", default="reports/a3")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    res, scores = run(pd.read_parquet(a.parquet), seed=a.seed)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "baseline_xgb.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    np.savez(out / "baseline_xgb_scores.npz", **scores)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
