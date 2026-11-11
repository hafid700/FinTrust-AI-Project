"""A3 - Tableau comparatif (Markdown) de tous les résultats de reports/a3/*.json."""
import json
import sys
from pathlib import Path


def main(*folders: str) -> None:
    rows = []
    files = [p for f in (folders or ("reports/a3",)) for p in sorted(Path(f).glob("*.json"))]
    for p in files:
        r = json.loads(p.read_text(encoding="utf-8"))
        if "test" not in r or "model" not in r:
            continue
        t = r["test"]
        rows.append((r["model"], t["pr_auc"], t["lift"], t["best_f1_oracle"],
                     t.get("f1_at_threshold", float("nan")),
                     t.get("recall_at_precision_0.5", float("nan")), r.get("train_time_s", float("nan"))))
    print("| Modèle | PR-AUC | Lift | F1 oracle | F1 (seuil val) | Recall@P0.5 | Temps (s) |")
    print("|---|---|---|---|---|---|---|")
    for m, ap, lift, f1o, f1v, rec, tt in rows:
        print(f"| {m} | {ap:.3f} | {lift:.1f}x | {f1o:.3f} | {f1v:.3f} | {rec:.3f} | {tt:.0f} |")


if __name__ == "__main__":
    main(*sys.argv[1:])
