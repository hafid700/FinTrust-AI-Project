"""A1 - Exploration d'IBM AML : statistiques + figures + sous-échantillon.

Exemple :
    python -m src.data.explore --csv data/raw/HI-Small_Trans.csv \
        --out reports/a1 --subsample 500000 --save data/processed/hi_small_sub.parquet
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.common.seed import set_seed
from .load import load_transactions
from .subsample import subsample_by_accounts


def compute_stats(df: pd.DataFrame) -> dict:
    ill = df["is_laundering"] == 1
    cross = df["from_bank"] != df["to_bank"]
    n_nodes = int(max(df["src"].max(), df["dst"].max())) + 1
    banks = pd.concat([df["from_bank"], df["to_bank"]]).nunique()
    return {
        "n_transactions": int(len(df)),
        "n_accounts": n_nodes,
        "n_banks": int(banks),
        "date_min": str(df["timestamp"].min()),
        "date_max": str(df["timestamp"].max()),
        "n_illicit": int(ill.sum()),
        "illicit_rate_pct": round(100 * float(ill.mean()), 4),
        "cross_bank_share_pct": round(100 * float(cross.mean()), 2),
        "illicit_rate_cross_bank_pct": round(100 * float(ill[cross].mean()), 4) if cross.any() else None,
        "illicit_rate_same_bank_pct": round(100 * float(ill[~cross].mean()), 4) if (~cross).any() else None,
        "n_currencies": int(df["payment_currency"].nunique()),
        "payment_formats": sorted(df["payment_format"].unique().tolist()),
        "amount_paid_median": float(df["amount_paid"].median()),
        "amount_paid_median_illicit": float(df.loc[ill, "amount_paid"].median()) if ill.any() else None,
    }


def make_figures(df: pd.DataFrame, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    ill = df["is_laundering"] == 1

    # 1. Volume et taux d'illicite par jour
    day = df["timestamp"].dt.floor("D")
    g = df.groupby(day)["is_laundering"].agg(["size", "mean"])
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.bar(g.index, g["size"], color="#2E6DA4")
    ax.set_ylabel("Transactions / jour")
    ax2 = ax.twinx()
    ax2.plot(g.index, 100 * g["mean"], color="#B8651B", marker="o")
    ax2.set_ylabel("% illicite")
    ax.set_title("Volume et taux d'illicite par jour")
    fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(out / "01_daily.png", dpi=130); plt.close(fig)

    # 2. Illicite par format de paiement
    pf = df.groupby("payment_format")["is_laundering"].agg(["size", "sum", "mean"])
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(pf.index, 100 * pf["mean"], color="#1E7B5C")
    ax.set_ylabel("% illicite"); ax.set_title("Taux d'illicite par format de paiement")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout(); fig.savefig(out / "02_payment_format.png", dpi=130); plt.close(fig)

    # 3. Distribution des montants (échelle log)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    bins = np.logspace(np.log10(max(df["amount_paid"].min(), 1e-2)), np.log10(df["amount_paid"].max()), 50)
    ax.hist(df.loc[~ill, "amount_paid"], bins=bins, alpha=0.6, density=True, label="légitime")
    if ill.any():
        ax.hist(df.loc[ill, "amount_paid"], bins=bins, alpha=0.6, density=True, label="illicite")
    ax.set_xscale("log"); ax.set_xlabel("Montant payé (échelle log)"); ax.legend()
    ax.set_title("Distribution des montants")
    fig.tight_layout(); fig.savefig(out / "03_amounts.png", dpi=130); plt.close(fig)

    # 4. Transactions illicites par banque émettrice (utile pour le découpage fédéré)
    top = df[ill].groupby("from_bank").size().sort_values(ascending=False).head(20)
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.bar(top.index.astype(str), top.values, color="#B8651B")
    ax.set_title("Top 20 banques émettrices par nb de transactions illicites")
    plt.setp(ax.get_xticklabels(), rotation=60, ha="right")
    fig.tight_layout(); fig.savefig(out / "04_banks_illicit.png", dpi=130); plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", default="reports/a1")
    ap.add_argument("--nrows", type=int, default=None, help="lire seulement les N premières lignes (test)")
    ap.add_argument("--subsample", type=int, default=None, help="nb cible de transactions du sous-échantillon")
    ap.add_argument("--save", default=None, help="chemin .parquet du jeu final")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    set_seed(a.seed)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    df = load_transactions(a.csv, nrows=a.nrows)
    stats = {"full": compute_stats(df)}
    make_figures(df, out)

    if a.subsample:
        sub = subsample_by_accounts(df, a.subsample, seed=a.seed)
        stats["subsample"] = compute_stats(sub)
        if a.save:
            Path(a.save).parent.mkdir(parents=True, exist_ok=True)
            sub.to_parquet(a.save, index=False)
    elif a.save:
        Path(a.save).parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(a.save, index=False)

    (out / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
