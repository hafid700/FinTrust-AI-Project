"""A6 - Export des alertes vers la Personne B (format du contrat `Alert`).

Entrée : fichier de scores d'un modèle (reports/a3|a4/*_scores.npz) + transactions (parquet).
Sorties (reports/a6/) :
  alerts_<name>.jsonl          alertes (transactions de TEST au-dessus du seuil choisi sur la VALIDATION)
  alerts_<name>_sample.jsonl   échantillon équilibré (vrais positifs / faux positifs) pour tester l'agent
  alerts_labels.csv            vérité terrain, SÉPARÉE des alertes (l'agent ne doit jamais la voir)
  neighbor_transactions.csv    détails des transactions citées comme voisines (outil « voisinage » de l'agent)
  export_summary_<name>.json   précision, rappel, répartition des patterns

`score` = probabilité brute du modèle ; `confidence` = score pour l'instant : B le remplace par le
score calibré (temperature scaling). `top_features` est laissé vide : B le remplit (SHAP).

    python -m src.detection.export_alerts --scores reports/a4/fed3_balanced_fedavg_scores.npz --name fedavg
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.alert import Alert
from src.common.metrics import best_f1_threshold
from src.data.load import assign_node_ids

EMPTY = np.array([], dtype=np.int64)


class GraphIndex:
    """Index positionnel du graphe global (df trié par date)."""

    def __init__(self, df: pd.DataFrame):
        self.src = df["src"].to_numpy(np.int64)
        self.dst = df["dst"].to_numpy(np.int64)
        self.tx_id = df["tx_id"].to_numpy(np.int64)
        self.ts = ((df["timestamp"] - df["timestamp"].min()).dt.total_seconds().to_numpy() // 60).astype(np.int64)
        self.out_pos = {k: np.asarray(v) for k, v in df.groupby("src").indices.items()}
        self.in_pos = {k: np.asarray(v) for k, v in df.groupby("dst").indices.items()}

    def _recent(self, arr, p, window):
        if arr is None:
            return EMPTY
        a = arr[:np.searchsorted(arr, p)]                       # strictement avant p (causal)
        return a if window is None else a[self.ts[a] >= self.ts[p] - window]

    def pattern(self, p: int, window: int = 2880, fan_k: int = 5, max_hops: int = 30) -> str:
        s, d = self.src[p], self.dst[p]
        out_d = self._recent(self.out_pos.get(d), p, window)
        if (self.dst[out_d] == s).any():                        # cycle de longueur 2 : d -> s déjà vu
            return "cycle"
        for x in np.unique(self.dst[out_d])[:max_hops]:         # cycle de longueur 3 : d -> x -> s
            if x != s and (self.dst[self._recent(self.out_pos.get(x), p, window)] == s).any():
                return "cycle"
        n_out = np.unique(np.r_[self.dst[self._recent(self.out_pos.get(s), p, window)], d]).size
        n_in = np.unique(np.r_[self.src[self._recent(self.in_pos.get(d), p, window)], s]).size
        if max(n_out, n_in) >= fan_k:
            return "fan_out" if n_out >= n_in else "fan_in"
        return "none"

    def neighbors(self, p: int, k: int = 5) -> list[int]:
        """tx_id des k dernières transactions antérieures de chacun des deux comptes."""
        ids = []
        for a in (self.src[p], self.dst[p]):
            pos = np.union1d(self.out_pos.get(a, EMPTY), self.in_pos.get(a, EMPTY))
            pos = pos[pos < p][-k:]
            ids += [int(t) for t in self.tx_id[pos]]
        return sorted(set(ids))


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


CONTEXT_COLS = ["timestamp", "from_bank", "from_account", "to_bank", "to_account", "amount_paid",
                "payment_currency", "amount_received", "receiving_currency", "payment_format"]


def _context(row) -> dict:
    c = {k: (str(row[k]) if k in ("timestamp", "from_account", "to_account") else
             (int(row[k]) if k.endswith("bank") else row[k] if isinstance(row[k], str) else float(row[k])))
         for k in CONTEXT_COLS}
    c["payment_currency"], c["receiving_currency"] = str(row["payment_currency"]), str(row["receiving_currency"])
    c["payment_format"] = str(row["payment_format"])
    return c


def export(df: pd.DataFrame, scores: dict, name: str, out_dir: str, max_alerts: int = 2000,
           n_sample: int = 60, seed: int = 42) -> dict:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    thr = best_f1_threshold(scores["val_y"], sigmoid(scores["val_logit"]))
    p_te = sigmoid(scores["test_logit"])
    keep = np.where(p_te >= thr)[0]
    keep = keep[np.argsort(-p_te[keep])][:max_alerts]

    gi = GraphIndex(df)
    pos_of = pd.Series(np.arange(len(df)), index=df["tx_id"].to_numpy())
    alerts, labels = [], []
    for i in keep:
        tx = int(scores["test_tx_id"][i]); p = int(pos_of[tx])
        a = Alert(tx_id=tx, score=float(p_te[i]), confidence=float(p_te[i]), top_features=[],
                  neighbors=gi.neighbors(p), pattern=gi.pattern(p), context=_context(df.iloc[p]))
        alerts.append(a); labels.append({"tx_id": tx, "label": int(scores["test_y"][i]), "score": float(p_te[i])})

    lab = pd.DataFrame(labels)
    rng = np.random.default_rng(seed)
    tp, fp = lab.index[lab.label == 1].to_numpy(), lab.index[lab.label == 0].to_numpy()
    pick = np.r_[rng.choice(tp, min(len(tp), n_sample // 2), replace=False),
                 rng.choice(fp, min(len(fp), n_sample // 2), replace=False)].astype(int)

    dump = lambda items, path: Path(path).write_text(
        "".join(json.dumps(x.to_dict(), ensure_ascii=False) + "\n" for x in items), encoding="utf-8")
    dump(alerts, out / f"alerts_{name}.jsonl")
    dump([alerts[i] for i in sorted(pick)], out / f"alerts_{name}_sample.jsonl")
    lab.to_csv(out / "alerts_labels.csv", index=False)

    nb_ids = sorted({n for a in alerts for n in a.neighbors})
    nb = df[df["tx_id"].isin(nb_ids)][["tx_id"] + CONTEXT_COLS]
    nb.to_csv(out / "neighbor_transactions.csv", index=False)

    n_pos_test = int(np.sum(scores["test_y"]))
    pat = pd.DataFrame({"pattern": [a.pattern for a in alerts], "label": lab.label})
    summary = {
        "model": name, "threshold_chosen_on_val": float(thr), "n_alerts": len(alerts),
        "precision": float(lab.label.mean()) if len(lab) else None,
        "recall": float(lab.label.sum() / n_pos_test) if n_pos_test else None,
        "n_true_positive": int(lab.label.sum()), "n_test_positive": n_pos_test,
        "pattern_counts": pat.pattern.value_counts().to_dict(),
        "share_true_positive_by_pattern": pat.groupby("pattern").label.mean().round(3).to_dict(),
        "n_neighbor_transactions": int(len(nb)),
    }
    (out / f"export_summary_{name}.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", default="reports/a4/fed3_balanced_fedavg_scores.npz")
    ap.add_argument("--parquet", default="data/processed/hi_small_sub.parquet")
    ap.add_argument("--name", default="fedavg")
    ap.add_argument("--out", default="reports/a6")
    ap.add_argument("--max-alerts", type=int, default=2000)
    ap.add_argument("--n-sample", type=int, default=60)
    a = ap.parse_args()
    df = pd.read_parquet(a.parquet)
    if not df["timestamp"].is_monotonic_increasing:
        df = df.sort_values("timestamp", kind="stable").reset_index(drop=True)
    s = export(df, dict(np.load(a.scores)), a.name, a.out, a.max_alerts, a.n_sample)
    print(json.dumps(s, indent=2))


if __name__ == "__main__":
    main()
