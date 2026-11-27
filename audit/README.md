# FinTrust-AI — Partie B : confiance et audit

Ce dossier (`audit/`) contient tout le travail de la **Personne B** : rendre les alertes du détecteur de A **fiables** (calibration), **explicables** (SHAP / Integrated Gradients), puis les transformer en **rapports d'audit** rédigés en français par un petit LLM affiné (LoRA) et contrôlés par un agent. Le dossier ne lit que le contrat d'alerte de A : il ne dépend ni du graphe ni des données brutes.

Table des matières
1. [Principe du projet](#1-principe-du-projet)
2. [Vue d'ensemble de la chaîne](#2-vue-densemble-de-la-chaîne)
3. [Contenu du dossier](#3-contenu-du-dossier)
4. [Installation](#4-installation)
5. [Comment tout faire tourner, étape par étape](#5-comment-tout-faire-tourner-étape-par-étape)
6. [Fonctionnement détaillé de chaque brique](#6-fonctionnement-détaillé-de-chaque-brique)
7. [Résultats](#7-résultats)
8. [Limites et honnêteté des résultats](#8-limites-et-honnêteté-des-résultats)
9. [Reproductibilité](#9-reproductibilité)
10. [Tests](#10-tests)
11. [Dépannage](#11-dépannage)

---

## 1. Principe du projet

**FinTrust-AI** détecte du blanchiment d'argent dans des transactions bancaires (jeu IBM AML HI-Small, ≈ 2 % de transactions illicites).

- **Personne A** : un réseau de neurones sur graphe (GNN) entraîné en apprentissage fédéré (3 banques simulées, FedAvg). Il produit un **score** par transaction et des **alertes** au-dessus d'un seuil.
- **Personne B (ce dossier)** : un score brut ne suffit pas à un analyste conformité. Il faut savoir (1) *dans quelle mesure on peut s'y fier*, (2) *pourquoi* le modèle a alerté, (3) *quoi faire* de l'alerte, avec un texte exploitable et traçable.

Réponse de B, en trois couches :

| Couche | Question | Méthode |
|---|---|---|
| Calibration (B5) | Un score de 0,95 signifie-t-il 95 % de vraies fraudes ? | Platt scaling ajusté sur la validation, mesuré sur le test (ECE, NLL, Brier) |
| Explication (B5) | Quelles features ont fait monter le score ? | Integrated Gradients moyennés sur 100 transactions de fond, validés par KernelSHAP |
| Rapport (B1–B4, B6) | Que dire à l'analyste ? | LLM Qwen2.5-0.5B affiné par LoRA, RAG réglementaire (GAFI, textes marocains), agent qui contrôle le texte |

**Contrat d'interface avec A.** Une alerte est une ligne JSON : `tx_id`, `score` (brut), `confidence` (**calibrée par B5**), `top_features` (**remplie par B5**), `neighbors` (identifiants de transactions voisines), `pattern` ∈ {`none`, `fan_in`, `fan_out`, `cycle`}, `context` (date, banques, comptes, montants, devises, format de paiement). Les **labels** (vérité terrain) sont dans un fichier séparé et ne sont **jamais** utilisés par B.

## 2. Vue d'ensemble de la chaîne

```
 Données de A (branche feature-A)
 ├─ reports/a4/…_scores.npz            scores val/test (logits, labels)
 ├─ checkpoints/…fedavg_seed42.pt      modèle GNN
 ├─ reports/a6/explain_bundle_…npz     50 features standardisées + fond (501 transactions)
 ├─ reports/a6/alerts_fedavg.jsonl     2 246 alertes de test
 └─ reports/a6/neighbor_transactions.csv   voisines des alertes
        │
        ▼
 calibration.py ──► alerts_calibrated.jsonl   (confidence calibrée)
        │
        ▼
 explain.py ──────► alerts_explained.jsonl    (top_features, signes, explication)   ◄── entrée de tout le reste
        │
        ├──► build_instruction_dataset.py ──► instruction_data/{train,val,test}.jsonl  (rapports de référence)
        │            │
        │            ▼
        │      notebook B4 (Colab GPU) ──► lora_adapters/rank_{4,8,16}  +  results/b4_*
        │            │
        │            ▼
        └──► notebook B6 (Colab GPU) : agent = outils + LoRA + contrôle ──► results/b6_*
                     ▲
 build_rag_index.py ─┘  (corpus PDF ──► index FAISS, consulté par l'outil réglementaire)
```

## 3. Contenu du dossier

| Fichier | Rôle |
|---|---|
| `calibration.py` | **B5.** ECE, diagramme de fiabilité, temperature / Platt / isotonique, IC bootstrap ; écrit `alerts_calibrated.jsonl` |
| `explain.py` | **B5.** Attributions IG + KernelSHAP sur la tête du modèle de A ; vérifications (additivité, suppression) ; écrit `alerts_explained.jsonl` |
| `build_rag_index.py` | **B1.** PDF → texte nettoyé → chunks → embeddings (`multilingual-e5-small`) → index FAISS |
| `search_rag.py` | **B1.** Fonction `search(question, k)` : extraits cités avec source et pages |
| `generate_mock_alerts.py`, `mock_alerts.json` | **B2.** Alertes factices de la première phase (conservées pour l'historique ; plus utilisées) |
| `build_instruction_dataset.py` | **B3.** Génère les rapports de référence (gabarits + règles) depuis les vraies alertes ; découpage stratifié |
| `report_checks.py` | Contrôle des faits d'un rapport : valeurs de l'alerte reprises, rien d'inventé (années, nombres, identifiants, montants, dates) |
| `lora_utils.py` | **B4.** Entraînement LoRA, génération par lots, métriques (`score_report`, `check_derived`), RAG dans le prompt |
| `agent_tools.py` | **B6.** Les 4 outils (voisinage, explication, statistiques, recherche réglementaire) et les backends (`RealBackend`, `MockBackend`) |
| `agent.py` | **B6.** Boucle de l'agent, contrôle et remplacement des sections fausses, annexe de traçabilité |
| `instruction_data/` | Jeu v2 : 2 246 exemples (1 795 train / 223 val / 228 test) |
| `results/` | `B4_analysis.md`, `B5_calibration_analysis.md`, `B6_analysis.md`, CSV, figures, rapports générés, échantillons de relecture |
| `../notebooks/B4_lora_finetuning.ipynb`, `B6_agent.ipynb` | Exécution sur Colab (GPU T4) |
| `../tests/test_audit.py` | Tests rapides sans GPU |

Fichiers **non versionnés** (trop lourds ou téléchargés) : `audit/corpus/*.pdf`, `audit/rag_index/`, `audit/lora_adapters/` (sauf `rank_16`, voir §9).

## 4. Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt            # partie A (commun)
pip install -r audit/requirements.txt      # partie B
pytest tests/test_audit.py                 # doit passer (≈ 1 s, sans GPU)
```

Entraînement et génération du LLM : **Google Colab, GPU T4** (Exécution → Modifier le type d'exécution). Les notebooks installent eux-mêmes leurs dépendances et affichent les versions utilisées.

## 5. Comment tout faire tourner, étape par étape

Les commandes supposent que la branche `feature-A` de A est récupérée (par exemple `git worktree add ../A_repo feature-A`) ou que ses fichiers `reports/` et `checkpoints/` sont copiés dans le dépôt.

### 5.1 Calibration puis explication (B5, CPU, quelques minutes)

```powershell
python audit/calibration.py --scores reports/a4/fed3_balanced_fedavg_scores.npz `
    --alerts reports/a6/alerts_fedavg.jsonl --out audit/results/b5 --method platt

python audit/explain.py --bundle reports/a6/explain_bundle_fedavg.npz `
    --ckpt checkpoints/fed3_balanced_fedavg_seed42.pt `
    --alerts audit/results/b5/alerts_calibrated.jsonl --out audit/results/b5
```
Sorties dans `audit/results/b5/` : `calibration_summary.json`, `calibration_bins.csv`, `reliability_before_after.png`, `alerts_calibrated.jsonl`, `explain_summary.json`, `explanations_overview.png`, `attributions_fedavg.npz`, et surtout **`alerts_explained.jsonl`**.

### 5.2 Jeu d'instruction (B3, CPU, secondes)

```powershell
python audit/build_instruction_dataset.py
```
Lit `audit/results/b5/alerts_explained.jsonl`, écrit `audit/instruction_data/{train,val,test}.jsonl` (graine 42).

### 5.3 Base RAG (B1, CPU)

Déposer les PDF dans `audit/corpus/` (GAFI : *FATF Recommendations 2012* ; RGPD ; *Guide LBC-FT* et *Lutte contre le blanchiment de capitaux* marocains — les URL de téléchargement sont dans la cellule de construction de l'index du notebook B6), puis :
```powershell
python audit/build_rag_index.py
python audit/search_rag.py "Quelles obligations de vigilance envers la clientèle ?" -k 3
```

### 5.4 Fine-tuning LoRA (B4, Colab GPU)

Ouvrir `notebooks/B4_lora_finetuning.ipynb` sur Colab, GPU T4, brancher `feature-B`.
1. Premier passage avec `QUICK = True` (quelques minutes) pour vérifier l'enchaînement.
2. Vrai run avec `QUICK = False` : 3 rangs × (≈ 23 min d'entraînement + ≈ 15 min de génération par configuration), 8 configurations évaluées. Réglages : `BATCH_SIZE = 1`, `GRAD_ACCUM = 8` (un lot plus grand fait déborder la T4 : les rapports font ≈ 2 600 tokens), `N_TEST = 60`.
3. Télécharger `b4_outputs.zip` (adaptateurs + résultats) et recopier dans le dépôt `audit/lora_adapters/` et `audit/results/`.

### 5.5 Agent (B6, Colab GPU)

Ouvrir `notebooks/B6_agent.ipynb`. Prérequis : adaptateur `audit/lora_adapters/rank_16` entraîné sur le jeu v2 (poussé dans le dépôt, sinon la cellule de chargement de l'adaptateur demande `b4_outputs.zip`), `audit/results/b5/alerts_explained.jsonl`, branche `feature-A` (clonée par le notebook pour `neighbor_transactions.csv`). Durée : ≈ 10 minutes pour 3 modes × 20 alertes. Sorties : `b6_comparison.csv`, `b6_reports_{off,prompt,annex}.jsonl`, `b6_samples.md` ; télécharger `b6_outputs.zip`.

### 5.6 Utiliser l'agent en Python

```python
import sys, json; sys.path.insert(0, "audit")
import agent as A, agent_tools as T, lora_utils as L
from search_rag import search

explained = [json.loads(l) for l in open("audit/results/b5/alerts_explained.jsonl", encoding="utf-8")]
backend = T.RealBackend("reports/a6/neighbor_transactions.csv", explained)
tools = T.make_tools(backend, search, k=2)
# generate_fn(alerts, contexts) -> [(texte, terminé)] : fourni par le LoRA (voir notebook B6)
results = A.run_agent(alerts, tools, generate_fn, rag_mode="annex", simulated=False)
print(results[0]["report"])
```
`alerts` doit être la **vue compacte** du jeu d'instruction (champ `input` de `instruction_data/*.jsonl`, qui contient `signs` et `context`).

## 6. Fonctionnement détaillé de chaque brique

### 6.1 Calibration (`calibration.py`)
- Paramètres ajustés sur la **validation**, mesures sur le **test** (jamais l'inverse).
- Trois méthodes monotones (l'ordre des scores, donc la PR-AUC, ne change pas) : *temperature scaling* (1 paramètre), *Platt* `sigmoid(a·logit + b)` (2 paramètres), *isotonique*.
- Résultat : le modèle est très sur-confiant sur les alertes (confiance moyenne 0,957 pour 70,9 % de vraies fraudes). Le temperature scaling n'y change rien d'utile (T = 0,844 < 1 durcit les scores) ; la cause est un **biais** (classe rare pondérée à l'entraînement), que Platt corrige (ECE 0,022 → 0,001).
- Piège évité : l'ECE globale est dominée par les 93 % de transactions à score faible ; on mesure donc aussi l'écart confiance − précision **sur les alertes**.

### 6.2 Explication (`explain.py`)
- Le modèle de A calcule `logit = tête([h_src, h_dst, x])` (178 → 64 → 1) : 50 features de transaction `x` plus deux embeddings de compte (contexte réseau). GNNExplainer est inutilisable (message passing sur mesure) ; on explique la tête, **embeddings fixés**.
- Integrated Gradients moyennés sur 100 transactions de fond, validés par KernelSHAP. Les 15 devises et les 7 formats de paiement sont regroupés : 30 groupes.
- Vérifications : reconstruction du logit d'A (écart 1,4e-6), additivité, modèle linéaire exact, accord avec KernelSHAP (1re feature identique 99,3 %), test de suppression (retirer les features désignées fait chuter le logit 9 à 20 fois plus que des features au hasard).
- Limite : **55 % du poids vient du contexte réseau**, que les features de transaction n'expliquent pas ; et 3 features (`payment_format`, `pair_prev`, `dst_in_cnt_all`) dominent presque toutes les alertes.

### 6.3 Jeu d'instruction (`build_instruction_dataset.py`)
Chaque alerte donne un rapport de référence **calculé** (gabarits français + règles), en 5 sections : 1 Résumé, 2 Schéma détecté, 3 Facteurs explicatifs, 4 Références réglementaires, 5 Recommandations. Règles :
- **niveau de risque** sur la confiance calibrée : critique ≥ 0,90 ; élevé ≥ 0,70 ; modéré à élevé ≥ 0,50 ; sinon modéré ;
- **fiabilité du schéma** : élevée pour `fan_in` et `fan_out` (précision d'A 0,85 et 0,98), limitée pour `cycle` et `none` (0,56 et 0,63), avec une note de prudence ;
- **références GAFI** : R10 (R16 pour `fan_out`), R20, et R21 si la confiance ≥ 0,70 ;
- **facteurs** « aggravant » / « atténuant » d'après le signe de l'attribution ; libellés français pour les 30 groupes de features ;
- phrase de transaction construite depuis le contexte (date, montant, comptes, format).

> **Les rapports de référence sont des cibles synthétiques** : elles viennent de modèles de texte, pas d'analystes. Les seuils sont des conventions, pas des règles réglementaires validées.

### 6.4 RAG (`build_rag_index.py`, `search_rag.py`)
PDF → texte page par page (ligatures corrompues réparées) → chunks de 250 mots avec 50 de chevauchement → embeddings `intfloat/multilingual-e5-small` (384 dim., corpus anglais + français) → index FAISS avec source et pages. `search()` renvoie des extraits **copiés**, jamais reformulés, donc non inventés.

### 6.5 LoRA (`lora_utils.py`, notebook B4)
Qwen2.5-0.5B-Instruct, LoRA sur les projections d'attention et MLP, rangs 4 / 8 / 16 (alpha = 2 × rang), 2 époques, lot effectif 8, la perte ne porte que sur le rapport (prompt masqué). Huit configurations comparées sur les mêmes alertes : prompt seul, prompt seul + RAG, LoRA r = 4 / 8 / 16 avec et sans RAG dans le prompt.

Métriques automatiques (`score_report`) : faits exacts, 5 sections, citation des textes, **recopie du prompt** (un modèle qui recopie l'alerte « reprend » tous les faits sans rien rédiger), génération **terminée**, et `strict_%` = tout ce qui précède + déductions conformes aux règles.

### 6.6 Agent (`agent.py`, `agent_tools.py`, notebook B6)
Boucle à planification **fixe** :
1. lire l'alerte ;
2. appeler 4 outils : voisinage (transactions voisines réelles d'A), explication (`alerts_explained.jsonl`), statistiques du voisinage, recherche réglementaire ;
3. le LoRA rédige les 5 sections ;
4. **contrôle** : niveau, fiabilité, note de prudence, valeurs de l'alerte, caractères hors alphabet latin, en-tête, et comparaison des sections 2 à 5 au gabarit calculé ; toute section fausse est **remplacée** par la version calculée, et la correction est tracée ;
5. annexe (section 6) : éléments des outils + traçabilité (outils appelés, sections remplacées).

Un outil en panne ne bloque jamais l'agent (résultat `ok=False`, signalé dans le rapport). Trois modes RAG : `off`, `prompt` (extraits dans le prompt du LLM), `annex` (extraits copiés en section 6, hors du LLM).

## 7. Résultats

Détails et limites dans `results/B4_analysis.md`, `B5_calibration_analysis.md`, `B6_analysis.md`.

| Étape | Résultat principal |
|---|---|
| B5 calibration | ECE 0,0222 → 0,0011 (Platt) ; confiance moyenne des alertes 0,957 → 0,699 (précision réelle 0,709) |
| B5 explication | IG et KernelSHAP s'accordent (99,3 % sur la 1re feature) ; fidélité 9 à 20 fois supérieure au hasard ; 55 % du poids hors des features de transaction |
| B4 (n = 60) | Prompt seul : 0 % exploitable. LoRA r = 4 / 8 / 16 : 96,7 / 98,3 / 98,3 % de rapports cohérents. Avec RAG dans le prompt : 0 / 0 / 18 % |
| B6 (n = 20) | Sans RAG et RAG en annexe : 100 % de brouillons cohérents, aucune section remplacée. RAG dans le prompt : 20 % de brouillons cohérents |

## 8. Limites et honnêteté des résultats

- **Cibles synthétiques sur alertes réelles.** Les 97–98 % de B4 mesurent la fidélité à un gabarit calculé par des règles, pas la qualité rédactionnelle. La relecture manuelle (grilles dans `results/b4_samples.md` et `b6_samples.md`) n'est pas encore faite.
- **Même distribution en entraînement et en test** (même modèle d'A, mêmes règles) ; une graine ; 60 et 20 alertes de test : les écarts de un ou deux rapports ne sont pas significatifs.
- **Le « 100 % final » de l'agent est vrai par construction** (les sections fausses sont remplacées). La mesure du LLM est le brouillon cohérent.
- **Règles et seuils = conventions**, non validés par un expert conformité.
- **RAG** : la requête ne dépend que du schéma ; les extraits sont peu pertinents dans l'échantillon relu ; le RAG dans le prompt dégrade le LoRA parce que l'adaptateur n'a jamais vu de contexte. Un RAG qui améliorerait la rédaction demanderait un entraînement avec contexte (non fait).
- **Planification fixe** : ce n'est pas un LLM qui choisit ses outils.
- **Statistiques du voisinage** : calculées sur les voisines fournies par A (pas l'historique complet du compte), dans la devise de l'alerte.
- **Explications partielles** (55 % du poids dans le contexte réseau) et dominées par 3 features.
- Un seul modèle d'A (FedAvg, 3 clients) et une seule graine d'entraînement.

## 9. Reproductibilité

- Graine 42 partout (`L.set_seed`), génération déterministe (greedy).
- Versions : `audit/requirements.txt` donne les bornes ; **les versions exactes du run Colab** sont affichées par la cellule 1 des notebooks. Figer l'environnement du run : dans une cellule Colab, `!pip freeze > requirements-colab.lock.txt`, puis committer ce fichier (encodage UTF-8).
- **Adaptateur LoRA** : `*.safetensors` est ignoré par Git. `audit/lora_adapters/rank_16` (34 Mo, nécessaire à B6) est ajouté de force (`git add -f`) ; les rangs 4 et 8 (8 et 17 Mo) restent hors dépôt (Drive). Sans cet adaptateur, B6 ne peut pas tourner sans refaire B4.
- Le corpus PDF et l'index FAISS ne sont pas versionnés (se reconstruisent en §5.3).
- Les rapports générés (`results/b4_reports_*.jsonl`, `b6_reports_*.jsonl`) contiennent brouillon, rapport final et mesures : on peut recalculer de nouvelles métriques sans GPU.

## 10. Tests

```powershell
pytest tests/test_audit.py
```
Cinq tests rapides, sans GPU : niveaux de risque, 600 rapports de référence conformes à toutes les règles, détection de mutations (niveau, en-tête), réparation des brouillons dégradés par l'agent (vide, coupé, caractère étranger), outil en panne.

## 11. Dépannage

| Symptôme | Cause et remède |
|---|---|
| `ModuleNotFoundError: agent` sur Colab | Les fichiers de `audit/` ne sont pas poussés sur la branche : `git push`, puis relancer la cellule de clonage |
| `CUDA out of memory` en B4 | Rapports longs : `BATCH_SIZE = 1`, `GRAD_ACCUM = 8`, `EVAL_BS = 4` ; redémarrer l'exécution avant de relancer |
| Index FAISS sans GAFI ou sans textes marocains | Téléchargement échoué : déposer les PDF dans `audit/corpus/`, supprimer `audit/rag_index/`, relancer `build_rag_index.py` |
| `pip install -r requirements.lock.txt` échoue | Fichier enregistré en UTF-16 par PowerShell (`>`) : régénérer avec `pip freeze \| Out-File -Encoding utf8 requirements.lock.txt` |
| Adaptateur introuvable en B6 | Pousser `audit/lora_adapters/rank_16` (`git add -f`) ou importer `b4_outputs.zip` quand la cellule le demande |
