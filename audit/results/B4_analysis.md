# B4 — Fine-tuning LoRA sur les alertes réelles d'A : analyse (v2)

Modèle : Qwen2.5-0.5B-Instruct, LoRA sur les projections d'attention et MLP (rangs 4, 8, 16, alpha = 2 × rang). Données : jeu v2 (`build_instruction_dataset.py`, 1 795 exemples d'entraînement, 223 de validation), construit sur les **vraies alertes d'A** (confiance calibrée et explications de B5). Les rapports de référence restent des **cibles synthétiques** (gabarits calculés par des règles). Évaluation : 60 alertes de test réparties sur les 4 schémas, génération déterministe, une graine. 2 époques, lot effectif 8, T4 (≈ 23 min d'entraînement par rang, pic mémoire 6,5 Go, ≈ 15 min de génération par configuration). Résultats : `b4_comparison.csv`, `b4_comparison.png`, rapports complets `b4_reports_*.jsonl`.

## 1. Résultats (n = 60)

| Configuration | Faits exacts | Exploitable | Cohérent (strict) | Recopie du prompt | Perte validation |
|---|---|---|---|---|---|
| Prompt seul | 0 % | 0 % | 0 % | 53 % | — |
| Prompt seul + RAG | 0 % | 0 % | 0 % | 0 % | — |
| LoRA r=4 | 96,7 % | 96,7 % | 96,7 % | 0 % | 0,0041 |
| LoRA r=8 | 98,3 % | 98,3 % | 98,3 % | 0 % | 0,0039 |
| LoRA r=16 | 98,3 % | 98,3 % | 98,3 % | 0 % | 0,0037 |
| LoRA r=4 + RAG | 78,3 % | 70,0 % | 0 % | 0 % | 0,0041 |
| LoRA r=8 + RAG | 93,3 % | 93,3 % | 0 % | 0 % | 0,0039 |
| LoRA r=16 + RAG | 96,7 % | 96,7 % | 18,3 % | 0 % | 0,0037 |

« Cohérent (strict) » = faits exacts + 5 sections + niveau de risque, fiabilité du schéma, note de prudence, action du schéma, références GAFI et facteurs aggravants/atténuants conformes aux règles. Intervalle de Wilson à 95 % pour 58/60 : 88,7–99,1 % ; pour 59/60 : 91,1–99,7 %.

## 2. Analyse

1. **Le fine-tuning change tout, et le résultat contredit celui de la première version.** Le modèle de base ne produit aucun rapport exploitable (il recopie le prompt dans 53 % des cas). Le LoRA, quel que soit le rang, produit des rapports cohérents dans 97–98 % des cas. En B4 v1 (400 exemples synthétiques), le LoRA recopiait les faits mais ratait les déductions (cohérent : 0 / 6 / 14 % selon le rang). Ici les déductions sont apprises. Deux changements l'expliquent probablement : 4,5 fois plus d'exemples, et des règles plus simples (seuils sur une seule grandeur, la confiance calibrée). Je n'ai pas isolé la part de chaque cause.
2. **Le rang n'a pas d'effet mesurable.** 58/60 contre 59/60 : un rapport d'écart, intervalles qui se recouvrent presque entièrement. La perte de validation baisse légèrement avec le rang (0,0041 → 0,0037) sans effet visible sur les rapports. Le rang 4 (2,2 M de paramètres) suffit sur ces données.
3. **Le seul défaut observé à rang 8/16 est une erreur de recopie de nombre.** À r=16, une alerte écrit « 1 279 137 834,34 » au lieu de « 12 791 378,34 » pour le montant. C'est le même type d'erreur que dans la v1 (valeurs inventées) mais devenu rare (1 cas sur 60). À r=4, 2 cas. Les montants atteignent 70 millions : les grands nombres sont le point faible.
4. **Le RAG ajouté au prompt dégrade nettement le LoRA, comme en v1.** Le cohérent tombe de 97–98 % à 0 / 0 / 18 %. Les défauts viennent des déductions (références GAFI, action du schéma, niveau) et non du format : l'adaptateur n'a jamais vu de contexte à l'entraînement, et le contexte déplace ses sorties. Plus le rang est élevé, moins la dégradation est forte (r=16 : 18 % cohérent, 96,7 % de faits exacts) ; ce gradient est cohérent avec une plus grande capacité à ignorer le contexte, sans être démontré avec une seule graine.
5. **Le RAG n'aide pas le modèle de base non plus** : le prompt seul + RAG produit 0 % de rapports exploitables (le modèle ne termine que 17 % des générations).
6. **Coût.** Entraînement ≈ 23 min par rang, indépendant du rang (la machine est limitée par la longueur des séquences, pas par les paramètres). Génération ≈ 15 min pour 60 rapports.

## 3. Limites (à écrire telles quelles dans le rapport)

- **Cibles synthétiques et très régulières.** Le test mesure la fidélité à un gabarit calculé par des règles, pas la qualité rédactionnelle. 97–98 % de cohérence prouve que le modèle imite le générateur ; cela ne dit pas qu'il rédige mieux qu'un analyste. Aucune lecture manuelle n'a encore été faite (grille dans `b4_samples.md`).
- **Même distribution en entraînement et en test.** Les alertes de test viennent du même modèle d'A, sous le même seuil, et les rapports suivent les mêmes règles. Pas de test sur un autre modèle d'A, ni sur d'autres règles.
- **60 alertes, une graine.** Écarts de un ou deux rapports non significatifs.
- **Règles = conventions** (seuils 0,90 / 0,70 / 0,50 sur la confiance calibrée), non validées par un expert conformité.
- **Contexte RAG par schéma** : peu varié, et jamais vu à l'entraînement : la conclusion sur le RAG vaut pour cette façon de l'injecter, pas pour le RAG en général. Un entraînement avec contexte reste à tester.
- **Explications partielles** : 55 % du poids du modèle d'A vient du contexte réseau, hors des 3 facteurs du rapport.

## 4. Conséquence pour B6

Le garde-fou de l'agent (contrôle des déductions + remplacement par le gabarit) devient moins nécessaire pour la cohérence, mais reste utile contre les erreurs de recopie de nombres et pour la traçabilité. Les résultats B6 v2 diront combien de sections il remplace réellement ; l'attente raisonnable est un taux de remplacement bien plus faible qu'en v1 (45–75 % par section).
