# B5 — Calibration et explication des alertes du modèle FedAvg de A

Données de A (branche `feature-A`, commit « A6b ») : scores `reports/a4/fed3_balanced_fedavg_scores.npz`, checkpoint `checkpoints/fed3_balanced_fedavg_seed42.pt`, paquet d'explication `reports/a6/explain_bundle_fedavg.npz`, alertes `reports/a6/alerts_fedavg.jsonl` (2 246 alertes de test, seuil de score brut 0,8177 choisi par A sur sa validation). Code : `audit/calibration.py`, `audit/explain.py`. Ces résultats remplacent ceux d'une version précédente des scores d'A (2 065 alertes, seuil 0,917).

Chaîne d'exécution : `calibration.py` (confiance calibrée) → `explain.py` (top_features, lit la sortie précédente) → `alerts_explained.jsonl`, alertes prêtes pour l'agent.

## 1. Calibration

Validation : 99 988 transactions (1,18 % illicites). Test : 99 997 (2,04 %). Paramètres ajustés sur la validation, mesures sur le test.

| Méthode | Paramètres | ECE (IC 95 % bootstrap) | NLL | Brier | Alertes : confiance moyenne (précision réelle : 0,709) |
|---|---|---|---|---|---|
| Score brut de A | — | 0,0222 (0,0214–0,0229) | 0,0525 | 0,0132 | 0,957 |
| Temperature scaling | T = 0,844 | 0,0179 (0,0172–0,0186) | 0,0524 | 0,0133 | 0,972 |
| Platt (a·logit + b) | a = 0,859 ; b = −2,149 | **0,0011** (0,0008–0,0017) | 0,0308 | 0,0078 | 0,699 |
| Isotonique | — | 0,0010 (0,0006–0,0017) | 0,0317 | 0,0078 | 0,699 |

Alertes = les 2 246 transactions de test au-dessus du seuil de A. Diagramme : `reliability_before_after.png`.

1. **Le modèle est très sur-confiant sur les alertes** : 0,957 de confiance moyenne pour 70,9 % de vraies fraudes.
2. **Le temperature scaling, demandé par le cahier, n'y change rien d'utile.** T = 0,844 < 1 rend les scores plus extrêmes : l'ECE globale baisse un peu (0,0222 → 0,0179), mais à cause des 93 000 transactions de score faible. Sur les alertes, la confiance monte de 0,957 à 0,972, et la NLL du test est inchangée (0,0525 → 0,0524). Lire T < 1 comme « le modèle était sous-confiant » serait faux.
3. **La cause est un biais.** Le checkpoint indique `pos_weight = 12,35` (A pondère la classe rare), soit ln = 2,51 en logit ; le biais ajusté par Platt est b = −2,15 avec une pente 0,86. C'est cohérent avec un score gonflé par la pondération, sans être un calcul exact. Un seul paramètre de température ne corrige qu'une pente ; Platt ajoute le biais.
4. **Platt et la régression isotonique corrigent presque tout** : ECE ≈ 0,001, NLL divisée par 1,7 et Brier par 1,7 environ. Platt est retenu pour l'export (2 paramètres, lisse, interprétable, sans paliers).
5. **La calibration tient malgré le changement de base** (1,18 % en validation, 2,04 % en test). Les trois transformations sont monotones : l'ordre des scores et la PR-AUC ne changent pas.

## 2. Explication des alertes

Le modèle de A calcule `logit = tête([h_src, h_dst, x])` : 50 features de transaction `x` et deux embeddings de compte (contexte réseau du GNN). GNNExplainer n'est pas utilisable (message passing sur mesure). On explique la tête, contexte réseau fixé (consigne de A), par **Integrated Gradients moyennés sur 100 transactions de fond**, validés par **KernelSHAP** (bibliothèque `shap`). Les 15 variables de devise et les 7 de format de paiement sont regroupées en deux groupes (leurs attributions s'additionnent exactement) : 30 groupes au total. Les valeurs sont en unités de logit, signées, relatives au fond (≈ 2,7 % d'illicites).

| Vérification | Résultat |
|---|---|
| La tête reconstruite depuis le checkpoint reproduit les logits d'A | écart maximal 1,4e-6 |
| Additivité : somme des attributions = f(x) − fond | erreur maximale 0,005 (logit moyen au-dessus du fond : 3,0) |
| Modèle linéaire de test : attributions exactes (IG et KernelSHAP) | oui, tolérance 1e-3 |
| Accord avec KernelSHAP (300 alertes, 1 000 échantillons) | feature n°1 identique 99,3 % ; 3 premières identiques à 94 % ; corrélation de rang moyenne 0,53 (ordre des petites attributions instable) |
| Test de suppression : baisse moyenne du logit quand on remet au fond les 1 / 3 / 5 groupes jugés importants, contre le même nombre tiré au hasard | 1,98 / 3,90 / 4,40 contre 0,10 / 0,23 / 0,48 |

Figure : `explanations_overview.png`.

1. **Les explications sont fidèles au modèle.** Retirer les features désignées fait chuter le logit 9 à 20 fois plus (selon le nombre de groupes retirés) que retirer des features au hasard, et deux méthodes indépendantes désignent la même feature principale.
2. **Elles sont peu variées.** Dans le top 3, `payment_format` apparaît dans 99,6 % des alertes, `pair_prev` dans 98,5 % et `dst_in_cnt_all` dans 79,1 %. Le modèle s'appuie sur très peu de features, et les rapports auraient presque toujours les mêmes facteurs. Les valeurs de `x` sont standardisées : `pair_prev` ≈ −0,94 signifie une paire de comptes jamais vue avant (à confirmer auprès d'A pour la définition exacte).
3. **29 % des contributions du top 3 vont vers « licite »** (le facteur réduit le soupçon). Le contrat d'interface n'a que des poids positifs : les poids exportés sont |attribution| normalisée sur les 30 groupes (somme = 1), et les signes sont dans `explanation.signs`. Les rapports doivent distinguer « facteur aggravant » et « facteur atténuant ».
4. **Cette explication est partielle : 55 % du poids total vient du contexte réseau** (embeddings du compte émetteur : 26 %, du compte destinataire : 29 %, mesuré sur 200 alertes) et seulement 45 % des 50 features de transaction. Expliquer les 50 features seules, comme demandé, ne dit pas pourquoi le réseau autour des comptes a fait monter le score. Cette limite doit être écrite dans les rapports d'audit.

## 3. Conséquences pour B3, B4 et B6

- **Nouvelles règles de niveau de risque.** Tous les scores bruts des alertes sont ≥ 0,818 : la règle « critique à partir de 0,90 » ne discrimine plus. La confiance calibrée varie de 0,30 à 0,98 sur les alertes (médiane 0,74 ; 41 % ≥ 0,80, 38 % < 0,65) : les seuils doivent s'appuyer dessus.
- **Note de prudence** : avec le critère actuel (confiance plus de 0,10 sous le score), elle concernerait 79 % des alertes ; à redéfinir avec les nouveaux seuils.
- **Noms de features** : les 30 groupes réels (`pair_prev`, `dst_in_cnt_all`, `src_passthrough_24h`…) remplacent les noms synthétiques de B2/B3. Il faut leur écrire des libellés français, et les noms de schémas passent à `fan_in` / `fan_out`.
- **Jeu d'instruction (B3) et LoRA (B4)** : à régénérer à partir des vraies alertes (`alerts_explained.jsonl`) avec ces règles. Le décalage avec les données synthétiques est important (voisins, features, distribution des scores).
- **Outil d'explication de l'agent (B6)** : brancher `alerts_explained.jsonl` (champs `top_features` et `explanation`) à la place de la lecture des features de l'alerte.

## 4. Limites

- Un seul modèle (FedAvg, 3 clients) et une seule graine d'entraînement. La calibration est globale : elle ne dit rien d'éventuelles différences entre schémas ou banques (la précision des alertes varie beaucoup selon le schéma d'après le résumé d'export d'A : de 0,56 pour cycle à 0,98 pour fan_out).
- Les intervalles bootstrap rééchantillonnent les transactions ; ils ne couvrent pas la variabilité entre graines.
- Les attributions dépendent du fond choisi (100 transactions tirées sur 501) et ne sont pas causales : elles décrivent le modèle, pas la fraude.
- Le rapport de rang avec KernelSHAP est modeste (0,53) : seules les 1 à 3 premières features sont à présenter.
