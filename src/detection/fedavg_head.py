"""Tête de classification du modèle FedAvg, utilisable SANS graphe ni données (pour SHAP / Captum).

Le modèle calcule  logit = tête([h_src, h_dst, x])  où
  x      = 50 features de la transaction (28 de base + 22 features de graphe causales) ;
  h_src, h_dst = embeddings des deux comptes (contexte réseau, issus du message passing).
Le paquet d'explication (`export_explain_bundle.py`) fournit h_src, h_dst et x pour chaque alerte.
"""
from __future__ import annotations

import numpy as np
import torch

from src.detection.gnn import EdgeGNN


def load_head(ckpt_path: str):
    """Retourne (tête nn.Module en mode eval, noms des features, dimension des embeddings)."""
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=True)
    model = EdgeGNN(ck["edge_dim"], ck["hidden"], ck["layers"])
    model.load_state_dict(ck["state_dict"])
    model.eval()
    return model.cls, ck["feature_names"], ck["hidden"]


@torch.no_grad()
def head_logit(head, h_src: np.ndarray, h_dst: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Logits pour des tableaux (n, hidden), (n, hidden), (n, n_features)."""
    z = torch.from_numpy(np.concatenate([h_src, h_dst, x], axis=1).astype(np.float32))
    return head(z).squeeze(-1).numpy()
