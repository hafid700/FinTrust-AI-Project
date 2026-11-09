#!/usr/bin/env python3
"""B2 - Génération d'alertes factices pour FinTrust-AI (Personne B).

Produit ~500 alertes au format du contrat d'interface (section 6 du cahier
des charges) afin que B puisse travailler (B3 dataset d'instruction, B4 LoRA,
B6 agent) pendant que A construit le vrai détecteur.

Contrat d'interface (une alerte) :
    {
      "tx_id": int,                       # identifiant de la transaction
      "score": float in [0, 1],           # score brut du modèle de A
      "confidence": float in [0, 1],      # niveau de confiance
      "top_features": [[nom, poids], ...],# explication (poids décroissants)
      "neighbors": [int, ...],            # tx_id voisines dans le graphe
      "pattern": "cycle" | "fan-in" | "fan-out" | "none"
    }

Usage :
    python audit/generate_mock_alerts.py                # 500 alertes, seed 42
    python audit/generate_mock_alerts.py --n 800 --seed 7

Les valeurs sont INVENTÉES : elles servent uniquement à développer et tester
la chaîne d'audit. Elles seront remplacées par les vraies sorties de A.
"""
import argparse
import json
import random
from collections import Counter
from pathlib import Path

# --- Paramètres du contrat (à figer avec A, voir README) -------------------

PATTERNS = ["cycle", "fan-in", "fan-out", "none"]
PATTERN_WEIGHTS = [0.30, 0.25, 0.25, 0.20]

# Features proposées (inspirées des colonnes d'IBM AML : montant, devise,
# format de paiement, banque + quelques features de structure du graphe).
# Pour chaque pattern, les features les plus plausibles, la première étant
# la plus fréquente en tête de l'explication.
FEATURES_BY_PATTERN = {
    "cycle": ["cross_bank", "cycle_length", "amount", "time_gap_hours"],
    "fan-in": ["in_degree", "amount", "payment_format", "same_day_inflows"],
    "fan-out": ["out_degree", "amount", "currency_mismatch", "same_day_outflows"],
    "none": ["amount", "payment_format", "hour_of_day", "currency_mismatch"],
}

# Nombre de voisins (min, max) selon le pattern
NEIGHBORS_RANGE = {
    "cycle": (2, 4),
    "fan-in": (3, 6),
    "fan-out": (3, 6),
    "none": (0, 2),
}

TX_ID_MIN, TX_ID_MAX = 1000, 99999
SCORE_THRESHOLD = 0.50  # une alerte n'existe que si le score dépasse ce seuil


def make_top_features(rng: random.Random, pattern: str) -> list:
    """2 ou 3 features, poids décroissants, somme entre 0.45 et 0.85.

    La feature la plus caractéristique du pattern passe en tête avec
    une probabilité élevée, pour que l'explication soit cohérente avec le
    pattern annoncé (sinon le LoRA apprendrait des rapports incohérents).
    """
    pool = FEATURES_BY_PATTERN[pattern]
    k = rng.choice([2, 3])
    first = pool[0] if rng.random() < 0.7 else rng.choice(pool)
    others = [f for f in pool if f != first]
    names = [first] + rng.sample(others, k - 1)

    raw = sorted((rng.random() + 0.3 for _ in range(k)), reverse=True)
    total = rng.uniform(0.45, 0.85)
    weights = [round(r / sum(raw) * total, 2) for r in raw]
    return [[n, w] for n, w in zip(names, weights)]


def make_alert(rng: random.Random, tx_id: int) -> dict:
    pattern = rng.choices(PATTERNS, weights=PATTERN_WEIGHTS, k=1)[0]

    # Score : surtout élevé, mais avec une vraie queue vers le seuil.
    score = SCORE_THRESHOLD + (1 - SCORE_THRESHOLD - 0.01) * rng.betavariate(2.5, 1.2)

    # Confiance : proche du score mais légèrement plus basse en moyenne
    # (un modèle brut est souvent sur-confiant -> motive la calibration B5).
    confidence = min(0.99, max(0.30, score - 0.05 + rng.gauss(0, 0.08)))

    lo, hi = NEIGHBORS_RANGE[pattern]
    n_neighbors = rng.randint(lo, hi)
    neighbors = set()
    while len(neighbors) < n_neighbors:
        candidate = rng.randint(TX_ID_MIN, TX_ID_MAX)
        if candidate != tx_id:
            neighbors.add(candidate)

    return {
        "tx_id": tx_id,
        "score": round(score, 2),
        "confidence": round(confidence, 2),
        "top_features": make_top_features(rng, pattern),
        "neighbors": sorted(neighbors),
        "pattern": pattern,
    }


def validate(alert: dict) -> None:
    """Vérifie qu'une alerte respecte le contrat d'interface."""
    assert set(alert) == {
        "tx_id", "score", "confidence", "top_features", "neighbors", "pattern"
    }, f"champs inattendus : {sorted(alert)}"
    assert isinstance(alert["tx_id"], int)
    assert 0.0 <= alert["score"] <= 1.0
    assert 0.0 <= alert["confidence"] <= 1.0
    assert alert["pattern"] in PATTERNS
    weights = [w for _, w in alert["top_features"]]
    assert weights == sorted(weights, reverse=True), "top_features non triées"
    assert alert["tx_id"] not in alert["neighbors"], "tx_id dans ses voisins"
    assert len(set(alert["neighbors"])) == len(alert["neighbors"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--n", type=int, default=500, help="nombre d'alertes")
    parser.add_argument("--seed", type=int, default=42, help="seed fixée")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parent / "mock_alerts.json",
        help="fichier de sortie (JSON)",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    tx_ids = rng.sample(range(TX_ID_MIN, TX_ID_MAX + 1), args.n)  # uniques
    alerts = [make_alert(rng, tx_id) for tx_id in tx_ids]

    for alert in alerts:
        validate(alert)

    args.out.write_text(
        json.dumps(alerts, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    counts = Counter(a["pattern"] for a in alerts)
    mean_score = sum(a["score"] for a in alerts) / len(alerts)
    mean_conf = sum(a["confidence"] for a in alerts) / len(alerts)
    print(f"{len(alerts)} alertes écrites dans {args.out}")
    print(f"patterns : {dict(counts)}")
    print(f"score moyen = {mean_score:.2f} | confiance moyenne = {mean_conf:.2f}")


if __name__ == "__main__":
    main()
