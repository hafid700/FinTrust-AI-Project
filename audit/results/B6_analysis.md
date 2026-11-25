# B6 — Agent d'investigation : analyse des résultats

Agent : `audit/agent.py` + `audit/agent_tools.py`. Rédaction par le LLM-LoRA de B4 (Qwen2.5-0.5B-Instruct, rang 16). Test : 20 alertes synthétiques du jeu de test de B3, une graine, génération déterministe. Voisinage et statistiques du compte viennent d'un backend factice (marqués « [données simulées] » dans les rapports).

## 1. Fonctionnement

1. Lecture de l'alerte (contrat d'interface de A).
2. Appel de 4 outils : voisinage, explication (features de l'alerte ; SHAP à brancher avec B5), statistiques du compte, recherche réglementaire (FAISS, B1).
3. Rédaction du rapport en 5 sections par le LLM-LoRA.
4. Contrôle : niveau de risque, fiabilité, note de prudence, valeurs de l'alerte, caractères hors alphabet latin, et comparaison des sections 2 à 5 au gabarit calculé du jeu de données. Toute section en écart est remplacée par la version calculée, et la correction est tracée.
5. Annexe (section 6) : éléments des outils et traçabilité (outils appelés, sections remplacées).

Trois modes pour la comparaison avec / sans RAG : `off` (pas de RAG), `prompt` (extraits dans le prompt du LLM, comme B4), `annex` (extraits copiés tels quels dans la section 6, hors du LLM).

## 2. Résultats (n = 20)

| Mode RAG | Brouillon exploitable | Brouillon cohérent | Rapport final cohérent | Rapports entièrement recalculés | Sections écrites correctement par le LLM | Sources en section 6 | Durée |
|---|---|---|---|---|---|---|---|
| off | 100 % | 15 % | 100 % | 0 % | 65 % | 0 | 145 s |
| prompt | 85 % | 0 % | 100 % | 10 % | 32 % | 0 | 195 s |
| annex | 100 % | 15 % | 100 % | 0 % | 65 % | 2 | 146 s |

Sections remplacées, par section :

| Mode RAG | Résumé | Schéma | Facteurs | Références | Recommandations |
|---|---|---|---|---|---|
| off | 55 % | 0 % | 0 % | 45 % | 75 % |
| prompt | 80 % | 20 % | 40 % | 100 % | 100 % |
| annex | 55 % | 0 % | 0 % | 45 % | 75 % |

## 3. Analyse

1. **Le rapport final est cohérent à 100 % par construction.** Ce n'est pas une performance du LLM. Les mesures qui évaluent le LLM sont le brouillon cohérent (15 %, en ligne avec les 14 % de B4 sur 50 alertes) et la part de sections écrites correctement (65 %).
2. **Le LLM recopie bien les faits, déduit mal.** Les sections 2 et 3 (schéma, voisinage, facteurs : valeurs de l'alerte) ne sont jamais remplacées sans RAG. Les sections qui dépendent de seuils (résumé : niveau de risque ; références : R16 ou R10, R21 selon le score ; recommandations : actions selon le niveau) sont remplacées dans 45 à 75 % des cas.
3. **Le RAG dans le prompt dégrade le LLM.** Sections correctes : 65 % → 32 %, brouillon exploitable 100 % → 85 %, 10 % de rapports à recalculer en entier, et même les sections de recopie de faits (schéma, facteurs) se dégradent (20 % et 40 % de remplacements). Cause probable, déjà vue en B4 : l'adaptateur n'a jamais vu de contexte à l'entraînement. Le prompt plus long coûte aussi ≈ 35 % de temps en plus (195 s contre 145 s).
4. **Le RAG en annexe n'améliore pas la rédaction, mais ajoute de la traçabilité.** Les deux modes donnent exactement les mêmes sections, car le LLM reçoit le même prompt. L'annexe apporte 2 extraits cités avec source et pages, copiés de l'index (non reformulés, donc non inventés). Leur pertinence reste à juger à la main : dans l'échantillon, un extrait de la loi marocaine associé à l'alerte fan-out (53581) porte sur des opérations immobilières, ce qui est peu lié à la dispersion de fonds. Toutes les alertes d'un même schéma reçoivent les mêmes requêtes.
5. **Réponse à la question du cahier (avec ou sans RAG).** Dans ce montage, le RAG utilisé comme contexte du LLM nuit à la qualité ; utilisé comme source citée hors du LLM, il est neutre pour la rédaction et utile pour l'auditabilité. Montrer qu'il améliore la rédaction demanderait un entraînement avec contexte et des rapports de référence sans paragraphes réglementaires figés.

## 4. Limites

- **Planification fixe** : les outils sont appelés dans un ordre prédéfini ; le LLM ne choisit pas ses outils.
- **Contrôle = gabarit du jeu synthétique** : les sections 2 à 5 sont des fonctions de l'alerte dans le jeu de B3, donc le LLM les recopie surtout de mémoire. Les seuils (0,65 / 0,80 / 0,90 / 0,85) sont des conventions, pas des règles réglementaires validées par un expert.
- **Outils simulés** : voisinage et statistiques viennent du backend factice. L'outil d'explication relit les features de l'alerte.
- **20 cas, une graine** : écarts de quelques rapports non significatifs.
- **Section 1** : seuls le niveau, la fiabilité, la note de prudence et les valeurs sont contrôlés ; le reste du texte du résumé n'est pas vérifié.
- **Relecture manuelle** (clarté, citations justes) à remplir dans `b6_samples.md`.

## 5. Intégration avec A et B5

Écrire un backend branché sur le GNN de A (3 méthodes : `neighbors`, `account_stats`, `explain`) et le passer à `make_tools`. Brancher les explications SHAP de B5 dans `explain`. Relancer sur 10 à 20 alertes réelles.
