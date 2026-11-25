#!/usr/bin/env python3
"""B5 (partie 1) - Calibration du score de A : ECE, diagramme de fiabilité, temperature scaling.

Entrée  : fichier de scores de A (npz) avec val_logit, val_y, test_logit, test_y,
          val_tx_id, test_tx_id  (ex. reports/a4/fed3_balanced_fedavg_scores.npz)
Sorties (dossier --out) :
    calibration_summary.json     ECE, NLL, Brier avant / après, température T, IC bootstrap
    calibration_bins.csv         une ligne par intervalle (diagramme de fiabilité)
    reliability_before_after.png diagramme de fiabilité avant / après calibration
    alerts_calibrated.jsonl      (si --alerts) alertes de A avec `confidence` calibrée (--method)

Méthodes comparées (toutes ajustées sur la VALIDATION uniquement, mesurées sur le TEST) :
  * temperature : p = sigmoid(logit / T)            1 paramètre  (Guo et al. 2017, demandé par le cahier)
  * platt       : p = sigmoid(a * logit + b)        2 paramètres (corrige aussi un décalage de base)
  * isotonic    : régression isotone du label sur le logit (non paramétrique)
Les trois sont monotones : l'ordre des scores, donc la PR-AUC, ne change pas.

Pièges propres à ces données (à écrire dans l'analyse) :
  * ~2 % de transactions illicites : l'ECE à intervalles de même largeur est dominée par
    l'intervalle des petits scores. On donne donc aussi l'ECE restreinte aux ALERTES
    (score >= seuil), qui est ce que l'analyste voit, et une ECE à intervalles de même effectif ;
  * le temperature scaling ne corrige qu'un excès ou un manque de confiance GLOBAL (pente) ;
    si le modèle est décalé (biais), il peut améliorer l'ECE globale tout en AGGRAVER la
    confiance sur les alertes : on mesure donc aussi l'écart confiance - précision sur les alertes.

    python audit/calibration.py --scores reports/a4/fed3_balanced_fedavg_scores.npz \
        --alerts reports/a6/alerts_fedavg.jsonl --out audit/results/b5 --method platt
"""
import argparse
import json
from pathlib import Path

import numpy as np

EPS = 1e-12


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -60, 60)))


# --- Métriques ---------------------------------------------------------------

def ece(y, p, n_bins: int = 10) -> float:
    """ECE à intervalles de même largeur (même définition que src/common/metrics.py de A)."""
    y, p = np.asarray(y, float), np.asarray(p, float)
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, n_bins - 1)
    total = 0.0
    for b in range(n_bins):
        m = idx == b
        if m.any():
            total += m.mean() * abs(y[m].mean() - p[m].mean())
    return float(total)


def ece_equal_mass(y, p, n_bins: int = 10) -> float:
    """ECE à intervalles de même effectif (robuste quand presque tous les scores sont proches de 0)."""
    y, p = np.asarray(y, float), np.asarray(p, float)
    order = np.argsort(p, kind="stable")
    total = 0.0
    for chunk in np.array_split(order, n_bins):
        if len(chunk):
            total += len(chunk) / len(y) * abs(y[chunk].mean() - p[chunk].mean())
    return float(total)


def nll(y, p) -> float:
    y, p = np.asarray(y, float), np.clip(np.asarray(p, float), EPS, 1 - EPS)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def brier(y, p) -> float:
    return float(np.mean((np.asarray(p, float) - np.asarray(y, float)) ** 2))


def reliability_bins(y, p, n_bins: int = 10) -> list:
    """Par intervalle : effectif, confiance moyenne, fréquence observée."""
    y, p = np.asarray(y, float), np.asarray(p, float)
    edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, n_bins - 1)
    rows = []
    for b in range(n_bins):
        m = idx == b
        rows.append({
            "bin": f"[{edges[b]:.1f}, {edges[b + 1]:.1f})", "n": int(m.sum()),
            "mean_confidence": float(p[m].mean()) if m.any() else None,
            "observed_rate": float(y[m].mean()) if m.any() else None,
        })
    return rows


# --- Temperature scaling -----------------------------------------------------

def fit_temperature(logits, y, bounds=(0.05, 20.0)) -> float:
    """T qui minimise la NLL sur (logits, y). Recherche sur log T : T reste > 0."""
    from scipy.optimize import minimize_scalar

    logits, y = np.asarray(logits, float), np.asarray(y, float)

    def loss(log_t):
        return nll(y, sigmoid(logits / np.exp(log_t)))

    res = minimize_scalar(loss, bounds=(np.log(bounds[0]), np.log(bounds[1])),
                          method="bounded", options={"xatol": 1e-6})
    return float(np.exp(res.x))


def bootstrap_ci(y, p, fn, n_boot: int = 200, seed: int = 42, alpha: float = 0.05):
    """Intervalle de confiance bootstrap (rééchantillonnage des transactions)."""
    rng = np.random.default_rng(seed)
    y, p = np.asarray(y), np.asarray(p)
    vals = []
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        vals.append(fn(y[i], p[i]))
    lo, hi = np.quantile(vals, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)


def evaluate(y, p, label: str) -> dict:
    return {
        "set": label, "n": int(len(y)), "prevalence": float(np.mean(y)),
        "ece_10bins": ece(y, p), "ece_equal_mass": ece_equal_mass(y, p),
        "nll": nll(y, p), "brier": brier(y, p),
    }


def fit_platt(logits, y):
    """(a, b) qui minimisent la NLL de sigmoid(a * logit + b), sans régularisation."""
    from scipy.optimize import minimize

    logits, y = np.asarray(logits, float), np.asarray(y, float)
    res = minimize(lambda w: nll(y, sigmoid(w[0] * logits + w[1])), x0=np.array([1.0, 0.0]),
                   method="BFGS")
    return float(res.x[0]), float(res.x[1])


def fit_isotonic(logits, y):
    from sklearn.isotonic import IsotonicRegression

    return IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0).fit(
        np.asarray(logits, float), np.asarray(y, float))


METHODS = ("temperature", "platt", "isotonic")


def alert_block(y, p_raw, p_cal, threshold):
    """Confiance moyenne vs précision observée sur les alertes (score brut >= seuil de A)."""
    m = p_raw >= threshold
    prec = float(y[m].mean())
    return {"n": int(m.sum()), "observed_precision": prec,
            "mean_confidence": float(p_cal[m].mean()), "gap": float(p_cal[m].mean() - prec)}


def run(scores_path, out_dir, alerts_path=None, method: str = "platt",
        n_bins: int = 10, n_boot: int = 200) -> dict:
    if method not in METHODS:
        raise ValueError(f"method doit être dans {METHODS}")
    z = np.load(scores_path)
    val_l, val_y = z["val_logit"].astype(float), z["val_y"].astype(int)
    test_l, test_y = z["test_logit"].astype(float), z["test_y"].astype(int)
    test_id = z["test_tx_id"]

    T = fit_temperature(val_l, val_y)
    a, b = fit_platt(val_l, val_y)
    iso = fit_isotonic(val_l, val_y)
    maps = {
        "raw": lambda l: sigmoid(l),
        "temperature": lambda l: sigmoid(l / T),
        "platt": lambda l: sigmoid(a * l + b),
        "isotonic": lambda l: np.asarray(iso.predict(l), float),
    }
    params = {"temperature": {"T": T}, "platt": {"a": a, "b": b}, "isotonic": {}, "raw": {}}

    alerts, threshold = None, None
    if alerts_path:
        alerts = [json.loads(l) for l in open(alerts_path, encoding="utf-8") if l.strip()]
        threshold = min(x["score"] for x in alerts) - 1e-6  # seuil de A (choisi sur sa validation)

    summary = {"exported_method": method, "alert_threshold_raw_score": threshold,
               "prevalence": {"val": float(val_y.mean()), "test": float(test_y.mean())},
               "methods": {}}
    bins = {}
    for name, f in maps.items():
        pv, pt = f(val_l), f(test_l)
        info = {"params": params[name], "val": evaluate(val_y, pv, "val"),
                "test": evaluate(test_y, pt, "test")}
        lo, hi = bootstrap_ci(test_y, pt, lambda u, v: ece(u, v, n_bins), n_boot)
        info["test"]["ece_10bins_ci95"] = [lo, hi]
        if threshold is not None:
            info["alerts_test"] = alert_block(test_y, maps["raw"](test_l), pt, threshold)
            info["alerts_val"] = alert_block(val_y, maps["raw"](val_l), pv, threshold)
        summary["methods"][name] = info
        bins[name] = reliability_bins(test_y, pt, n_bins)
    summary["monotone_order_preserved"] = bool(all(
        np.all(np.diff(maps[k](np.sort(test_l))) >= -1e-12) for k in METHODS))

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    import csv
    with open(out / "calibration_bins.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["version", "bin", "n", "mean_confidence", "observed_rate"])
        for ver, rows in bins.items():
            for r in rows:
                w.writerow([ver, r["bin"], r["n"], r["mean_confidence"], r["observed_rate"]])
    plot_reliability(bins, summary, out / "reliability_before_after.png")

    if alerts is not None:
        by_tx = dict(zip(test_id.tolist(), test_l.tolist()))
        missing = 0
        with open(out / "alerts_calibrated.jsonl", "w", encoding="utf-8") as f:
            for al in alerts:
                logit = by_tx.get(al["tx_id"])
                if logit is None:
                    missing += 1
                    continue  # alerte sans logit : on ne devine pas sa confiance
                al["confidence"] = float(maps[method](np.array([logit]))[0])
                f.write(json.dumps(al, ensure_ascii=False) + "\n")
        summary["alerts_without_logit"] = missing
    (out / "calibration_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def plot_reliability(bins: dict, summary: dict, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = ["raw", "temperature", "platt"]
    titles = {"raw": "Avant calibration", "temperature": "Temperature scaling", "platt": "Platt (a·logit + b)"}
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6), sharey=True)
    for ax, ver in zip(axes, names):
        rows = [r for r in bins[ver] if r["n"] > 0]
        ax.plot([0, 1], [0, 1], "--", color="gray", label="calibration parfaite")
        ax.plot([r["mean_confidence"] for r in rows], [r["observed_rate"] for r in rows],
                "o-", color="#1f77b4", label="observé")
        for r in rows:  # effectif de chaque intervalle : un point à 3 transactions ne prouve rien
            ax.annotate(f"n={r['n']}", (r["mean_confidence"], r["observed_rate"]),
                        textcoords="offset points", xytext=(4, -10), fontsize=7)
        e = summary["methods"][ver]["test"]["ece_10bins"]
        ax.set_title(f"{titles[ver]} (ECE = {e:.4f})")
        ax.set_xlabel("confiance moyenne de l'intervalle")
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.grid(alpha=.3)
    axes[0].set_ylabel("fréquence observée de transactions illicites")
    axes[0].legend(loc="upper left", fontsize=8)
    fig.suptitle("Diagramme de fiabilité sur le TEST (paramètres ajustés sur la validation)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--scores", required=True)
    ap.add_argument("--alerts", default=None)
    ap.add_argument("--out", default="audit/results/b5")
    ap.add_argument("--method", default="platt", choices=METHODS,
                    help="méthode utilisée pour la confiance des alertes exportées")
    ap.add_argument("--bins", type=int, default=10)
    ap.add_argument("--boot", type=int, default=200)
    a = ap.parse_args()
    s = run(a.scores, a.out, a.alerts, a.method, a.bins, a.boot)
    print("prévalence :", {k: round(v, 4) for k, v in s["prevalence"].items()})
    for name, m in s["methods"].items():
        t = m["test"]
        line = (f"{name:12s} test ECE={t['ece_10bins']:.4f} "
                f"[{t['ece_10bins_ci95'][0]:.4f}-{t['ece_10bins_ci95'][1]:.4f}] "
                f"NLL={t['nll']:.4f} Brier={t['brier']:.5f}")
        if "alerts_test" in m:
            al = m["alerts_test"]
            line += f" | alertes: confiance {al['mean_confidence']:.3f} vs précision {al['observed_precision']:.3f}"
        print(line, m["params"])
    print("export :", s["exported_method"])


if __name__ == "__main__":
    main()
