"""Contrat d'interface entre la partie A (détection) et la partie B (audit).

A produit des alertes, B les consomme. Toute modification de ce format doit
être annoncée à l'autre personne et notée dans le README.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Tuple

PATTERNS = {"cycle", "fan_in", "fan_out", "none"}


@dataclass
class Alert:
    tx_id: int
    score: float                       # probabilité brute du modèle, dans [0, 1]
    confidence: float                  # score calibré, dans [0, 1]
    top_features: List[Tuple[str, float]] = field(default_factory=list)  # (nom, contribution SHAP)
    neighbors: List[int] = field(default_factory=list)                   # comptes ou transactions voisins
    pattern: str = "none"              # cycle | fan_in | fan_out | none
    context: dict = field(default_factory=dict)   # (optionnel) montants, banques, dates... JAMAIS le label

    def __post_init__(self) -> None:
        for name in ("score", "confidence"):
            v = getattr(self, name)
            if not 0.0 <= v <= 1.0:
                raise ValueError(f"{name} doit être dans [0, 1], reçu {v}")
        if self.pattern not in PATTERNS:
            raise ValueError(f"pattern inconnu : {self.pattern} (attendu : {sorted(PATTERNS)})")
        self.top_features = [(str(n), float(w)) for n, w in self.top_features]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Alert":
        return cls(**d)


def save_alerts(alerts: List[Alert], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for a in alerts:
            f.write(json.dumps(a.to_dict(), ensure_ascii=False) + "\n")


def load_alerts(path: str | Path) -> List[Alert]:
    with open(path, encoding="utf-8") as f:
        return [Alert.from_dict(json.loads(line)) for line in f if line.strip()]
