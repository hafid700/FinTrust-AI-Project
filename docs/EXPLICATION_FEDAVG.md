# Expliquer une alerte FedAvg (pour la partie B)

Fichiers fournis par A : `checkpoints/fed3_balanced_fedavg_seed42.pt` (poids, ~200 Ko) et
`reports/a6/explain_bundle_fedavg.npz`.

Le modèle calcule `logit = tête([h_src, h_dst, x])` :
- `x` : 50 features de la transaction (noms dans `feature_names`) dont 22 features de graphe causales ;
- `h_src`, `h_dst` : embeddings des deux comptes (contexte réseau du GNN, 64 dimensions chacun).

On explique donc la contribution des 50 features de `x`, le contexte réseau (embeddings) étant fixé.
C'est une explication « au niveau de la tête » : elle ne passe pas par GNNExplainer (qui suppose les
couches PyG standard), mais SHAP et Integrated Gradients s'appliquent directement.

## Exemple KernelSHAP (à adapter ; non testé)
```python
import numpy as np, shap
from src.detection.fedavg_head import load_head, head_logit

b = np.load("reports/a6/explain_bundle_fedavg.npz")
head, names, _ = load_head("checkpoints/fed3_balanced_fedavg_seed42.pt")
i = 0                                                # une alerte
hs, hd, x = b["h_src"][i:i+1], b["h_dst"][i:i+1], b["x"][i:i+1]
f = lambda X: head_logit(head, np.repeat(hs, len(X), 0), np.repeat(hd, len(X), 0), X)
expl = shap.KernelExplainer(f, b["bg_x"][:100])
sv = expl.shap_values(x, nsamples=200)[0]
top = sorted(zip(names, sv), key=lambda t: -abs(t[1]))[:5]    # -> top_features de l'alerte
```
Vérification utile : `f(x)` doit égaler `b["logit"][i]`.

## Integrated Gradients (Captum)
La tête est un `nn.Sequential` : on peut utiliser `captum.attr.IntegratedGradients` sur l'entrée
`z = [h_src, h_dst, x]` (178 dims), puis ne garder que les 50 dernières composantes (ou regrouper
les 128 premières en « contexte réseau »).
