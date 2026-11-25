# B6 — Agent d'investigation sur les alertes réelles d'A : analyse (v2)

Agent : `audit/agent.py` + `audit/agent_tools.py`. Rédaction par le LLM-LoRA de B4 v2 (Qwen2.5-0.5B-Instruct, rang 16, entraîné sur le jeu v2). Test : **20 alertes réelles** du jeu de test, réparties sur les schémas, une graine, génération déterministe. Outils sans donnée simulée : voisines lues dans `neighbor_transactions.csv` (A), explications de `alerts_explained.jsonl` (B5), extraits réglementaires de l'index FAISS (B1). Résultats : `b6_comparison.csv`, `b6_reports_*.jsonl`, `b6_samples.md`.

## 1. Fonctionnement

1. Lecture de l'alerte (contrat d'interface de A).
2. Appel de 4 outils : voisinage, explication, statistiques du voisinage, recherche réglementaire.
3. Rédaction du rapport en 5 sections par le LLM-LoRA.
4. Contrôle : niveau de risque, fiabilité, note de prudence, valeurs de l'alerte, caractères hors alphabet latin, et comparaison des sections 2 à 5 au gabarit calculé. Toute section en écart est remplacée par la version calculée, et la correction est tracée.
5. Annexe (section 6) : éléments des outils et traçabilité.

Trois modes pour la comparaison avec / sans RAG : `off` (pas de RAG), `prompt` (extraits dans le prompt du LLM), `annex` (extraits copiés tels quels en section 6, hors du LLM).

## 2. Résultats (n = 20)

| Mode RAG | Brouillon exploitable | Brouillon cohérent | Rapport final cohérent | Rapports recalculés en entier | Sections écrites correctement par le LLM | Sources en section 6 | Durée |
|---|---|---|---|---|---|---|---|
| off | 100 % | 100 % | 100 % | 0 % | 100 % | 0 | 190 s |
| prompt | 100 % | 20 % | 100 % | 0 % | 63 % | 0 | 197 s |
| annex | 100 % | 100 % | 100 % | 0 % | 100 % | 2 | 190 s |

Sections remplacées dans le mode `prompt` : références 100 %, recommandations 80 %, schéma 5 %, résumé et facteurs 0 %. Aucune section n'est remplacée dans les modes `off` et `annex`. Intervalle de Wilson à 95 % pour 20/20 : 83–100 %.

## 3. Analyse

1. **Avec le LoRA v2, le garde-fou n'a presque rien à corriger sans RAG.** 20 brouillons sur 20 sont cohérents, aucune section remplacée. En v1 le même contrôle remplaçait 45 à 75 % des sections de déduction. Ce n'est pas un résultat de l'agent : il reflète le LoRA de B4 v2, qui apprend les règles (voir B4). Le « 100 % final » reste vrai par construction ; la mesure du LLM est le brouillon cohérent.
2. **Le contrôle reste utile mais n'a pas été mis à l'épreuve ici.** Le défaut observé en B4 (un grand montant mal recopié, 1 cas sur 60) n'est pas apparu sur ces 20 alertes. Le taux d'erreur résiduel (1 à 3 % en B4) est trop faible pour qu'un échantillon de 20 le fasse voir. La détection a été vérifiée séparément par des tests de mutation (niveau, fiabilité, caractère étranger, brouillon vide ou coupé : tous corrigés), pas sur des sorties de modèle.
3. **Le RAG dans le prompt dégrade le LLM, comme en B4 et en v1.** Brouillons cohérents : 100 % → 20 %. Les références et recommandations sont réécrites par le modèle perturbé (par exemple « institutions de crédit » au lieu de « institutions financières », intitulé de la R20 modifié, R21 absente, une ligne de recommandation en anglais). Les 63 % de sections correctes viennent surtout des sections qui recopient l'alerte (résumé, facteurs). Durée quasi identique (197 s contre 190 s).
4. **Le RAG en annexe ne change pas la rédaction et ajoute de la traçabilité.** Les modes `off` et `annex` donnent les mêmes sections. L'annexe apporte 2 extraits cités avec source et pages, copiés de l'index (non reformulés). **Leur pertinence est faible dans l'échantillon relu** : l'extrait de la loi marocaine porte sur les professions soumises (opérations immobilières, gestion de fonds), et celui du guide sur le dispositif de vigilance en général. Les requêtes ne dépendent que du schéma : toutes les alertes d'un même schéma reçoivent les mêmes extraits. Pertinence à juger à la main dans `b6_samples.md`.
5. **Réponse à la question du cahier (avec ou sans RAG).** Dans ce montage, le RAG utilisé comme contexte du LLM nuit à la qualité ; utilisé comme source citée hors du LLM, il est neutre pour la rédaction et utile pour l'auditabilité. Montrer qu'il améliore la rédaction demanderait un entraînement avec contexte.

## 4. Limites

- **Planification fixe** : les outils sont appelés dans un ordre prédéfini ; le LLM ne choisit pas ses outils.
- **Contrôle = gabarit du jeu de B3** : les sections 2 à 5 sont des fonctions de l'alerte dans ce jeu. Les seuils (0,90 / 0,70 / 0,50 sur la confiance calibrée) sont des conventions, non validées par un expert.
- **20 cas, une graine** : le 100 % sans RAG est compatible avec 83–100 %. L'écart entre `off` et `prompt` (100 % contre 20 %) est en revanche net.
- **Statistiques du voisinage** : calculées sur les voisines fournies par A, pas sur l'historique complet du compte. Dans le run analysé, la section 6 additionnait des montants de devises différentes (USD, CAD, EUR) ; **corrigé depuis** (agrégat limité à la devise de l'alerte, nombre de voisines concernées indiqué), à vérifier lors du prochain run.
- **Explication partielle** : 55 % du poids du modèle d'A vient du contexte réseau, hors des facteurs listés (voir B5).
- **Section 1** : seuls le niveau, la fiabilité, la note de prudence et les valeurs sont contrôlés.
- **Relecture manuelle** (clarté, citations justes) toujours à remplir dans `b6_samples.md`.

## 5. Suite possible

Faire tourner l'agent sur plus d'alertes (60 à 228) pour estimer le taux de remplacement réel ; entraîner un LoRA avec contexte réglementaire ; faire dépendre la requête de recherche des facteurs de l'alerte (pas seulement du schéma).
