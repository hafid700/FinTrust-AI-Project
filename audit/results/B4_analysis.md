# B4 — Fine-tuning LoRA : analyse des résultats

Modèle de base : Qwen2.5-0.5B-Instruct (Colab T4). Jeu de test : 50 alertes synthétiques (génération déterministe, voir `build_instruction_dataset.py`). Une seule graine (42), une seule exécution par configuration.

## 1. Protocole

Trois approches comparées sur les mêmes 50 alertes :
- **Prompt seul** : le modèle de base reçoit l'alerte et la structure attendue, sans exemple.
- **LoRA** : adaptateurs de rang 4, 8, 16 (alpha = 2 × rang, modules q, k, v, o, gate, up, down), 3 époques, taux d'apprentissage 2e-4, lot effectif 8.
- **+ RAG** : ajout de 2 extraits réglementaires retrouvés (FAISS, multilingual-e5-small) dans le prompt, sans réentraîner.

Métriques automatiques :
- `facts_ok` : tx_id, score, confiance, schéma, facteurs, poids et voisins recopiés sans valeur inventée.
- `usable` : faits exacts, 5 sections présentes, rapport terminé, pas de recopie du prompt.
- `strict` : `usable` + règles de cohérence (niveau de risque, fiabilité, note de prudence, action propre au schéma, recommandations citées).

Les règles de cohérence sont des seuils que j'ai fixés dans le générateur du jeu de données ; elles ne proviennent pas des textes réglementaires. Elles mesurent donc la cohérence interne du modèle avec ce jeu.

## 2. Résultats (n = 50)

| Configuration | Faits exacts | Exploitables | Cite la R20 | Terminés | Cohérence (logic_ok) | Strict |
|---|---|---|---|---|---|---|
| Prompt seul | 30 % | 0 % | 0 % | 86 % | 0 % | 0 % |
| Prompt seul + RAG | 14 % | 2 % | 0 % | 32 % | 0 % | 0 % |
| LoRA r=4 | 76 % | 74 % | 94 % | 100 % | 0 % | 0 % |
| LoRA r=4 + RAG | 26 % | 18 % | 0 % | 80 % | 0 % | 0 % |
| LoRA r=8 | 94 % | 94 % | 100 % | 100 % | 6 % | 6 % |
| LoRA r=8 + RAG | 88 % | 82 % | 0 % | 100 % | 0 % | 0 % |
| LoRA r=16 | 100 % | 100 % | 100 % | 100 % | 14 % | 14 % |
| LoRA r=16 + RAG | 96 % | 86 % | 96 % | 88 % | 0 % | 0 % |

Coût d'entraînement (première exécution) : ≈ 203–213 s par rang, pic mémoire GPU 8,3–8,4 Go. Paramètres entraînables : 2 199 552 (r=4), 4 399 104 (r=8), 8 798 208 (r=16). Perte de validation : 0,125, 0,030, 0,015.

Échecs par règle de cohérence (rapports en échec sur 50) :

| Règle | r=4 | r=8 | r=16 | r=16 + RAG |
|---|---|---|---|---|
| Niveau de risque | 36 | 26 | 18 | 28 |
| Fiabilité | 23 | 10 | 5 | 23 |
| Note de prudence | 15 | 14 | 11 | 17 |
| Action propre au schéma | 49 | 26 | 14 | 45 |
| Recommandations citées | 32 | 27 | 30 | 30 |

## 3. Analyse

1. **Le fine-tuning est indispensable.** Le modèle de base, avec prompt seul, ne produit aucun rapport exploitable : il recopie le prompt dans 40 % des cas et invente des sources (par exemple un « GAFI » défini comme « Gouvernemental Administratif de la France », avec une fausse URL).
2. **Le rang améliore la qualité, à coût d'entraînement quasi constant.** Les rapports exploitables passent de 74 % à 94 % puis 100 %, et la perte de validation est divisée par huit entre r=4 et r=16. Le temps d'entraînement ne change pas visiblement. Réserves : 50 alertes, une graine, un seul taux d'apprentissage. L'écart r=8 / r=16 (3 rapports) n'est pas concluant, et capacité et vitesse de convergence ne sont pas séparées.
3. **Le LoRA apprend la forme et la recopie, pas les déductions.** À r=16, tous les rapports recopient correctement les faits, mais 43 sur 50 enfreignent au moins une règle de cohérence. Le modèle doit comparer un nombre à un seuil (0,80 ; 0,90 ; 0,85 pour la R21) et n'y arrive pas de façon fiable avec 400 exemples. Le rang réduit ces erreurs (niveau de risque : 36 → 26 → 18 échecs) mais n'est pas suffisant. Un taux « exploitable » de 100 % surestime donc la fiabilité.
4. **Le RAG n'améliore pas dans ce montage.** Les rapports de référence contiennent déjà les paragraphes réglementaires, que le LoRA a mémorisés : le contexte récupéré n'apporte rien de plus. De plus, les adaptateurs n'ont jamais vu de contexte à l'entraînement, ce qui les perturbe (citation de la R20 à 0 % pour r=4 et r=8 avec RAG, 12 % de rapports non terminés à r=16). Ce résultat ne démontre pas que le RAG est inutile ; il montre que ce montage ne permet pas de le mesurer. Pour le tester, il faudrait entraîner avec du contexte et retirer les textes réglementaires figés des rapports de référence.
5. **Conséquence pour la suite (B6).** Le niveau de risque, la fiabilité et les recommandations à citer sont des fonctions déterministes de l'alerte. Plutôt que de les faire déduire par le modèle, l'agent les calculera avec des outils, et le modèle se limitera à la rédaction.

## 4. Limites

- Données synthétiques générées par gabarits : le modèle apprend en partie les gabarits, pas la tâche d'audit en conditions réelles.
- 50 alertes de test, une graine, une exécution : pas d'intervalle de confiance, écarts de quelques rapports non significatifs.
- Les règles de cohérence sont celles du générateur (seuils choisis par l'auteur), non validées par un expert conformité.
- Relecture humaine non faite à ce stade (grille clarté / citations justes dans `b4_samples.md`).
- Observations qualitatives à signaler : caractère étranger intrus (« 庶 ») dans un rapport LoRA + RAG, et étiquette erronée « Recommandation 10 (virements électroniques) » (c'est la R16).

## 5. Reproduction

Notebook `notebooks/B4_lora_finetuning.ipynb` (`QUICK = False` ; `REUSE_ADAPTERS = True` pour réévaluer sans réentraîner). Résultats dans `audit/results/` : `b4_comparison.csv`, `b4_reports_*.jsonl`, `b4_samples.md`.
