"""A5 - VAE de rééquilibrage + ablation (thème 5).

Question : un VAE entraîné sur les transactions illicites, qui génère des exemples
synthétiques, améliore-t-il la détection par rapport à d'autres façons de traiter le
déséquilibre ?

Variantes (même classifieur XGBoost, mêmes 50 features, mêmes val/test RÉELS) :
  none          : aucun traitement
  class_weight  : pondération de la classe rare (= xgb_graph de A3)
  oversample    : duplication aléatoire des positifs
  smote         : SMOTE
  vae           : positifs synthétiques générés par un VAE (une variante par dimension latente)

Le VAE génère des FEATURES de transaction (pas de arêtes, pas de graphe). Entraînement sur les
positifs du TRAIN uniquement ; la validation et le test ne contiennent jamais de données synthétiques.

    python -m src.detection.vae_ablation --seeds 42 43 44
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
from src.data.graph_features import build_graph_features

METRIC_KEYS = ("pr_auc", "lift", "f1_at_threshold", "recall_at_precision_0.5")


def prepare(df: pd.DataFrame):
    split = temporal_split(df)
    X, names = build_edge_features(df, split)
    G, gnames = build_graph_features(df)
    return np.hstack([X, G]), names + gnames, df["is_laundering"].to_numpy(), split


class Standardizer:
    def fit(self, X):
        self.mu, self.sd = X.mean(axis=0), X.std(axis=0) + 1e-6
        return self

    def transform(self, X):
        return (X - self.mu) / self.sd

    def inverse(self, Z):
        return Z * self.sd + self.mu


def repair(X: np.ndarray, names: list[str]) -> np.ndarray:
    """Remet les échantillons synthétiques dans des valeurs valides."""
    X = X.copy()
    for prefix in ("payment_format_", "payment_currency_"):       # one-hot : une seule colonne à 1
        idx = np.array([i for i, n in enumerate(names) if n.startswith(prefix)])
        if len(idx):
            am = np.argmax(X[:, idx], axis=1)
            X[:, idx] = 0.0
            X[np.arange(len(X)), idx[am]] = 1.0
    for n in ("same_currency", "cross_bank"):                     # indicateurs binaires
        if n in names:
            i = names.index(n)
            X[:, i] = (X[:, i] > 0.5).astype(X.dtype)
    for i, n in enumerate(names):                                  # log1p(comptes/montants) >= 0
        if "_cnt_" in n or "_amt_" in n or n in ("pair_prev", "rev_pair_prev"):
            X[:, i] = np.clip(X[:, i], 0.0, None)
    return X


# ---------------------------------------------------------------- VAE (PyTorch)
def build_vae(d_in: int, latent: int, hidden: int = 64):
    import torch.nn as nn

    class VAE(nn.Module):
        def __init__(self):
            super().__init__()
            h2 = hidden // 2
            self.enc = nn.Sequential(nn.Linear(d_in, hidden), nn.ReLU(), nn.Linear(hidden, h2), nn.ReLU())
            self.mu, self.logvar = nn.Linear(h2, latent), nn.Linear(h2, latent)
            self.dec = nn.Sequential(nn.Linear(latent, h2), nn.ReLU(), nn.Linear(h2, hidden), nn.ReLU(),
                                     nn.Linear(hidden, d_in))

        def encode(self, x):
            h = self.enc(x)
            return self.mu(h), self.logvar(h)

        def reparameterize(self, mu, logvar):            # astuce de reparamétrisation
            import torch
            return mu + torch.randn_like(mu) * torch.exp(0.5 * logvar)

        def forward(self, x):
            mu, logvar = self.encode(x)
            return self.dec(self.reparameterize(mu, logvar)), mu, logvar

    return VAE()


def train_vae(Z: np.ndarray, latent: int = 8, epochs: int = 200, lr: float = 1e-3, batch: int = 128,
              beta: float = 1.0, seed: int = 42):
    """Perte = reconstruction (MSE) + beta * KL(q(z|x) || N(0, I)). Retourne (modèle, historique)."""
    import torch

    torch.manual_seed(seed)
    model = build_vae(Z.shape[1], latent)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    data = torch.from_numpy(Z.astype(np.float32))
    hist = []
    for ep in range(1, epochs + 1):
        model.train()
        perm = torch.randperm(len(data))
        tot = mse_t = kl_t = 0.0
        for i in range(0, len(data), batch):
            x = data[perm[i:i + batch]]
            rec, mu, logvar = model(x)
            mse = ((rec - x) ** 2).sum(dim=1).mean()
            kl = (-0.5 * (1 + logvar - mu ** 2 - logvar.exp()).sum(dim=1)).mean()
            loss = mse + beta * kl
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item() * len(x); mse_t += mse.item() * len(x); kl_t += kl.item() * len(x)
        n = len(data)
        hist.append({"epoch": ep, "loss": tot / n, "mse": mse_t / n, "kl": kl_t / n})
    return model, hist


def sample_vae(model, n: int, latent: int, seed: int = 0) -> np.ndarray:
    import torch

    g = torch.Generator().manual_seed(seed)
    model.eval()
    with torch.no_grad():
        return model.dec(torch.randn(n, latent, generator=g)).numpy()   # échantillonnage depuis le prior N(0, I)


def realism_auc(real: np.ndarray, synth: np.ndarray, seed: int = 0) -> float:
    """Test à deux échantillons : un classifieur sépare-t-il réel et synthétique ?
    AUC ~ 0.5 = indiscernables ; AUC ~ 1.0 = synthétique facilement détectable."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.model_selection import cross_val_score

    n = min(len(real), len(synth), 2000)
    rng = np.random.default_rng(seed)
    X = np.vstack([real[rng.choice(len(real), n, replace=False)], synth[rng.choice(len(synth), n, replace=False)]])
    y = np.r_[np.zeros(n), np.ones(n)]
    return float(cross_val_score(HistGradientBoostingClassifier(max_iter=100, random_state=seed),
                                 X, y, cv=3, scoring="roc_auc").mean())


# ---------------------------------------------------------------- variantes
def make_training_set(variant, Xtr, ytr, names, ratio, seed, vae_cfg, artifacts=None):
    pos, neg = int((ytr == 1).sum()), int((ytr == 0).sum())
    extra = {}
    if variant == "none":
        return Xtr, ytr, 1.0, extra
    if variant == "class_weight":
        return Xtr, ytr, neg / max(pos, 1), extra
    if variant == "oversample":
        from imblearn.over_sampling import RandomOverSampler
        X, y = RandomOverSampler(sampling_strategy=ratio, random_state=seed).fit_resample(Xtr, ytr)
        return X, y, 1.0, extra
    if variant == "smote":
        from imblearn.over_sampling import SMOTE
        X, y = SMOTE(sampling_strategy=ratio, k_neighbors=max(1, min(5, pos - 1)),
                     random_state=seed).fit_resample(Xtr, ytr)
        return X, y, 1.0, extra
    if variant.startswith("vae_d"):
        latent = int(variant[5:])
        std = Standardizer().fit(Xtr)
        Zpos = std.transform(Xtr[ytr == 1]).astype(np.float32)
        t0 = time.time()
        model, hist = train_vae(Zpos, latent=latent, epochs=vae_cfg["epochs"], beta=vae_cfg["beta"], seed=seed)
        n_syn = max(int(ratio * neg) - pos, 0)
        Xs = repair(std.inverse(sample_vae(model, n_syn, latent, seed)), names)
        extra = {"n_synthetic": int(n_syn), "vae_train_time_s": round(time.time() - t0, 1),
                 "final_mse": hist[-1]["mse"], "final_kl": hist[-1]["kl"],
                 "realism_auc": realism_auc(Xtr[ytr == 1], Xs, seed) if n_syn > 0 else None}
        if artifacts is not None and "vae" not in artifacts:
            artifacts["vae"] = {"model": model, "hist": hist, "latent": latent, "std": std,
                                "Zpos": Zpos, "Xs": Xs, "Xneg": Xtr[ytr == 0]}
        return np.vstack([Xtr, Xs]), np.r_[ytr, np.ones(n_syn, dtype=ytr.dtype)], 1.0, extra
    raise ValueError(f"variante inconnue : {variant}")


def fit_eval(Xtr, ytr, Xva, yva, Xte, yte, spw, seed, n_estimators=500):
    import xgboost as xgb

    clf = xgb.XGBClassifier(n_estimators=n_estimators, max_depth=6, learning_rate=0.1, subsample=0.8,
                            colsample_bytree=0.8, scale_pos_weight=spw, eval_metric="aucpr",
                            early_stopping_rounds=30, tree_method="hist", random_state=seed, n_jobs=-1)
    clf.fit(Xtr, ytr, eval_set=[(Xva, yva)], verbose=False)
    p_va, p_te = clf.predict_proba(Xva)[:, 1], clf.predict_proba(Xte)[:, 1]
    thr = best_f1_threshold(yva, p_va)                        # seuil choisi sur la val RÉELLE
    return {"val": summarize(yva, p_va, thr), "test": summarize(yte, p_te, thr),
            "best_iteration": int(getattr(clf, "best_iteration", -1))}


def plot_vae(art, out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import torch
    from sklearn.decomposition import PCA

    out.mkdir(parents=True, exist_ok=True)
    model, std = art["model"], art["std"]
    rng = np.random.default_rng(0)
    neg = std.transform(art["Xneg"][rng.choice(len(art["Xneg"]), 2000, replace=False)]).astype(np.float32)
    syn = std.transform(art["Xs"][:2000]).astype(np.float32)
    model.eval()
    with torch.no_grad():
        mu_pos = model.encode(torch.from_numpy(art["Zpos"]))[0].numpy()
        mu_neg = model.encode(torch.from_numpy(neg))[0].numpy()
        mu_syn = model.encode(torch.from_numpy(syn))[0].numpy()
    pts = np.vstack([mu_pos, mu_neg, mu_syn])
    p2 = PCA(n_components=2).fit(pts) if pts.shape[1] > 1 else None
    proj = (lambda a: p2.transform(a)) if p2 is not None else (lambda a: np.c_[a, np.zeros(len(a))])
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(*proj(mu_neg).T, s=5, alpha=0.25, label="légitimes (réelles)", color="#2E6DA4")
    ax.scatter(*proj(mu_pos).T, s=8, alpha=0.6, label="illicites (réelles)", color="#B8651B")
    ax.scatter(*proj(mu_syn).T, s=5, alpha=0.25, label="illicites (synthétiques)", color="#1E7B5C")
    ax.set_title(f"Espace latent du VAE (dim {art['latent']}, projection PCA)")
    ax.legend(markerscale=3); fig.tight_layout(); fig.savefig(out / "latent_space.png", dpi=130); plt.close(fig)

    h = art["hist"]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot([e["epoch"] for e in h], [e["mse"] for e in h], label="reconstruction (MSE)")
    ax.plot([e["epoch"] for e in h], [e["kl"] for e in h], label="KL")
    ax.set_xlabel("époque"); ax.legend(); ax.set_title("Entraînement du VAE")
    fig.tight_layout(); fig.savefig(out / "vae_training.png", dpi=130); plt.close(fig)


def run_ablation(df, variants=("none", "class_weight", "oversample", "smote", "vae"), seeds=(42,),
                 ratio=0.1, latent_dims=(8,), epochs=200, beta=1.0, out_dir="reports/a5"):
    variants = [v for var in variants for v in ([f"vae_d{d}" for d in latent_dims] if var == "vae" else [var])]
    X, names, y, split = prepare(df)
    tr, va, te = split == 0, split == 1, split == 2
    rows = {v: [] for v in variants}
    artifacts: dict = {}
    for seed in seeds:
        set_seed(seed)
        for v in variants:
            Xt, yt, spw, extra = make_training_set(v, X[tr], y[tr], names, ratio, seed,
                                                   {"epochs": epochs, "beta": beta}, artifacts)
            res = fit_eval(Xt, yt, X[va], y[va], X[te], y[te], spw, seed)
            res.update({"seed": seed, "n_train": int(len(yt)), "n_pos_train": int((yt == 1).sum()), **extra})
            rows[v].append(res)
            print(f"[seed {seed}] {v:14s} test PR-AUC {res['test']['pr_auc']:.3f} | lift {res['test']['lift']:.1f}x | "
                  f"F1 {res['test']['f1_at_threshold']:.3f}" + (f" | realism AUC {extra['realism_auc']:.2f}"
                                                                if extra.get("realism_auc") is not None else ""))
    summary = {}
    for v, rs in rows.items():
        summary[v] = {k: {"mean": float(np.mean([r["test"][k] for r in rs])),
                          "std": float(np.std([r["test"][k] for r in rs]))} for k in METRIC_KEYS}
        summary[v]["per_seed"] = rs
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    cfg = {"seeds": list(seeds), "ratio": ratio, "latent_dims": list(latent_dims), "epochs": epochs, "beta": beta,
           "n_features": len(names)}
    (out / "ablation.json").write_text(json.dumps({"config": cfg, "results": summary}, indent=2), encoding="utf-8")
    if "vae" in artifacts:
        plot_vae(artifacts["vae"], out)
    return summary


def print_table(summary) -> None:
    print("\n| Variante | PR-AUC | Lift | F1 (seuil val) | Recall@P0.5 |\n|---|---|---|---|---|")
    for v, s in summary.items():
        print(f"| {v} | " + " | ".join(f"{s[k]['mean']:.3f} ± {s[k]['std']:.3f}" for k in METRIC_KEYS) + " |")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", default="data/processed/hi_small_sub.parquet")
    ap.add_argument("--out", default="reports/a5")
    ap.add_argument("--variants", nargs="+", default=["none", "class_weight", "oversample", "smote", "vae"])
    ap.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44])
    ap.add_argument("--ratio", type=float, default=0.1, help="part positifs/négatifs visée après rééquilibrage")
    ap.add_argument("--latent-dims", nargs="+", type=int, default=[8])
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--beta", type=float, default=1.0)
    a = ap.parse_args()
    s = run_ablation(pd.read_parquet(a.parquet), a.variants, a.seeds, a.ratio, a.latent_dims, a.epochs, a.beta, a.out)
    print_table(s)


if __name__ == "__main__":
    main()
