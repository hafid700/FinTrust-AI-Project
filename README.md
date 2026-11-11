# FinTrust-AI

Détection fédérée de blanchiment d'argent par GNN avec audit agentique explicable.
Projet intégrateur - IA avancée - ENSA de Fès - A.U 2026/2027.

## Idée
Plusieurs banques simulées entraînent ensemble un GNN de détection (apprentissage fédéré),
le score est calibré et expliqué (SHAP), puis un agent (LLM + LoRA + RAG) rédige un rapport d'audit.

## Équipe et rôles
| Personne | Rôle | Dossiers |
|---|---|---|
| A - Rmiki Abdelhafid| Détection : GNN, fédéré, VAE | `src/data`, `src/detection` |
| B - Soufiane Tadlaoui | Confiance et audit : calibration/XAI, LoRA, RAG, agent | `src/audit` |
| Commun | Contrat d'alerte, métriques, seeds | `src/common` |

## Installation
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pytest                           # doit passer avant de commencer
```

## Règles de travail
- Une branche par personne (`feature-A`, `feature-B`), fusion par pull request relue par l'autre.
- Jamais de données, modèles ou clés (`.env`) dans Git.
- Split **temporel** uniquement ; seed 42 (`src/common/seed.py`).
- Métriques : PR-AUC, F1, recall à précision fixée, ECE. Pas d'accuracy.
- Le format d'alerte (`src/common/alert.py`) est un contrat : toute modification est annoncée à l'autre.

## Avancement
- [ ] Étape 0 : dépôt, contrat, versions
- [ ] A1 : exploration IBM AML (`python -m src.data.explore ...`)
- [ ] A2 : graphe PyG + split temporel (`python -m src.data.graph`)
- [ ] A3 : XGBoost tabulaire vs XGBoost + features de graphe vs GNN
- [ ] A3b : GNN avec features de graphe (`python -m src.data.graph --graph-features`)
- [ ] A4 : apprentissage fédéré (`python -m src.detection.federated`)
- [ ] A5 : VAE + ablation du rééquilibrage (`python -m src.detection.vae_ablation`)
- [ ] A6 : export des alertes vers B
- [ ] B1-B6 : confiance et audit
- [ ] Intégration et analyse

