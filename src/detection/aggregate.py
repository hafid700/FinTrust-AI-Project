"""Moyenne ± écart-type sur plusieurs graines (dossiers) pour chaque modèle.

    python -m src.detection.aggregate reports/a4 reports/a4_s43 reports/a4_s44
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

METRICS = [("pr_auc", "PR-AUC"), ("lift", "Lift"), ("f1_at_threshold", "F1 (seuil val)"),
           ("recall_at_precision_0.5", "Recall@P0.5")]


def collect(folders):
    groups = defaultdict(list)
    for f in folders:
        for p in sorted(Path(f).glob("*.json")):
            r = json.loads(p.read_text(encoding="utf-8"))
            if "test" in r and "model" in r:
                groups[r["model"]].append(r["test"])
    return groups


def main(*folders: str) -> None:
    groups = collect(folders)
    print("| Modèle | n | " + " | ".join(n for _, n in METRICS) + " |")
    print("|---|---|" + "---|" * len(METRICS))
    for model, tests in sorted(groups.items()):
        cells = []
        for key, _ in METRICS:
            v = np.array([t[key] for t in tests if t.get(key) is not None], dtype=float)
            cells.append(f"{v.mean():.3f} ± {v.std():.3f}" if len(v) else "-")
        print(f"| {model} | {len(tests)} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main(*sys.argv[1:])
