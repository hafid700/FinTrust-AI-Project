# Échantillon pour relecture manuelle (B4)

## Prompt seul

### Exemple 1 — alert-4792264
Entrée : `{"tx_id": 4792264, "score": 0.973, "confidence": 0.717, "top_features": [["pair_prev", 0.307], ["dst_in_cnt_all", 0.162], ["payment_format", 0.129]], "signs": [1, -1, 1], "neighbors": [14027, 650688, 1028265, 2649157], "pattern": "none", "context": {"timestamp": "2022-09-09 21:06:00", "from_bank": 23537, "from_account": "80EC75590", "to_bank": 16224, "to_account": "80EC83FC0", "amount_paid": 787.36, "payment_currency": "US Dollar", "amount_received": 787.36, "receiving_currency": "US Dollar", "payment_format": "ACH"}}`
Contrôle automatique : ['date/heure 09/09/2022 21:06 absentes', 'amount_paid 787,36 absent', 'amount_received 787,36 absent'] | recopie du prompt : True | terminé : False

```
RAPPORT D'AUDIT — Transaction 4792264

1. Résumé
2. Schéma détecté
3. Facteurs explicatifs
4. Références réglementaires
5. Recommandations

Règles : écris les nombres décimaux avec une virgule et non un point ; recopie le tx_id, le score, la confiance, le schéma, chaque facteur avec son poids et chaque transaction voisine ; cite les textes réglementaires pertinents (GAFI, droit marocain) ; n'invente aucune valeur.

Alerte :
{"tx_id": 4792264, "score": 0.973, "confidence": 0.717, "top_features": [["pair_prev", 0.307], ["dst_in_cnt_all", 0.162], ["payment_format", 0.129]], "signs": [1, -1, 1], "neighbors": [14027, 650688, 1028265, 2649157], "pattern": "none", "context": {"timestamp": "2022-09-09 21:06:00", "from_bank": 23537, "from_account": "80EC75590", "to_bank": 16224, "to_account": "80EC83FC0", "amount_paid": 787.36, "payment_currency": "US Dollar", "amount_received": 787.36, "receiving_currency": "US Dollar", "payment_format": "ACH"}}

Structure attendue :
- Résumé
- Schéma détecté
- Facteurs explicatifs
- Références réglementaires
- Recommandations

Règles : écris les nombres décimaux avec une virgule et non un point ; recopie le tx_id, le score, la confiance, le schéma, chaque facteur avec son poids et chaque transaction voisine ; cite les textes réglementaires pertinents (GAFI, droit marocain) ; n'invente aucune valeur.

Alerte :
{"tx_id": 4792264, "score": 0.973, "confidence": 0.717, "top_features": [["pair_prev", 0.307], ["dst_in_cnt_all", 0.162], ["payment_format", 0.129]], "signs": [1, -1, 1], "neighbors": [14027, 650688, 1028265, 2649157], "pattern": "none", "context": {"timestamp": "2022-09-09 21:06:00", "from_bank": 23537, "from_account": "80EC75590", "to_bank": 16224, "to_account": "80EC83FC0", "amount_paid": 787.36, "payment_currency": "US Dollar", "amount_received": 787.36, "receiving_currency": "US Dollar", "payment_format": "ACH"}}

Structure attendue :
- Résumé
- Schéma détecté
- Facteurs explicatifs
- Références réglementaires
- Recommandations

Règles : écris les nombres décimaux avec une virgule et non un point ; recopie le tx_id, le score, la confiance, le schéma, chaque facteur avec son poids et chaque transaction voisine ; cite les textes réglementaires pertinents (GAFI, droit marocain) ; n'invente aucune valeur.

Alerte :
{"tx_id": 4792264, "score": 0.973, "confidence": 0.717, "top_features": [["pair_prev", 0.307], ["dst_in_cnt_all", 0.162], ["payment_format", 0.129]], "signs": [1, -1, 1], "neighbors": [14027, 650688, 1028265, 2649157], "pattern": "none", "context": {"timestamp": "2022-09-09 21:06:00", "from_bank": 23537, "from_account": "80EC75590", "to_bank": 16224, "to_account": "80EC83FC0", "amount_paid": 787.36, "payment_currency": "US Dollar", "amount_received": 787.36, "receiving_currency": "US Dollar", "payment_format": "ACH"}}

Structure attend
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### Exemple 2 — alert-4042285
Entrée : `{"tx_id": 4042285, "score": 0.981, "confidence": 0.778, "top_features": [["pair_prev", 0.351], ["dst_in_cnt_all", 0.149], ["payment_format", 0.143]], "signs": [1, -1, 1], "neighbors": [181033, 3839410, 3899241, 3899242, 3989754, 4042284], "pattern": "fan_out", "context": {"timestamp": "2022-09-08 15:11:00", "from_bank": 22, "from_account": "800241D60", "to_bank": 4, "to_account": "800370A40", "amount_paid": 2854.57, "payment_currency": "Yuan", "amount_received": 2854.57, "receiving_currency": "Yuan", "payment_format": "ACH"}}`
Contrôle automatique : ['date/heure 08/09/2022 15:11 absentes', 'amount_paid 2 854,57 absent', 'amount_received 2 854,57 absent', 'identifiant inventé : 2854'] | recopie du prompt : True | terminé : True

```
RAPPORT D'AUDIT — Transaction 4042285

1. Résumé
2. Schéma détecté
3. Facteurs explicatifs
4. Références réglementaires
5. Recommandations

Règles : écris les nombres décimaux avec une virgule et non un point ; recopie le tx_id, le score, la confiance, le schéma, chaque facteur avec son poids et chaque transaction voisine ; cite les textes réglementaires pertinents (GAFI, droit marocain) ; n'invente aucune valeur.

Alerte :
{"tx_id": 4042285, "score": 0.981, "confidence": 0.778, "top_features": [["pair_prev", 0.351], ["dst_in_cnt_all", 0.149], ["payment_format", 0.143]], "signs": [1, -1, 1], "neighbors": [181033, 3839410, 3899241, 3899242, 3989754, 4042284], "pattern": "fan_out", "context": {"timestamp": "2022-09-08 15:11:00", "from_bank": 22, "from_account": "800241D60", "to_bank": 4, "to_account": "800370A40", "amount_paid": 2854.57, "payment_currency": "Yuan", "amount_received": 2854.57, "receiving_currency": "Yuan", "payment_format": "ACH"}
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### Exemple 3 — alert-4446104
Entrée : `{"tx_id": 4446104, "score": 0.874, "confidence": 0.382, "top_features": [["pair_prev", 0.376], ["dst_in_cnt_all", 0.127], ["src_in_cnt_all", 0.074]], "signs": [1, -1, 1], "neighbors": [1207505, 1760482, 2271977, 2419933, 2419934, 4078002, 4133281, 4345797, 4364907, 4374819], "pattern": "fan_out", "context": {"timestamp": "2022-09-09 08:08:00", "from_bank": 2824, "from_account": "80163FC30", "to_bank": 123390, "to_account": "811006A00", "amount_paid": 400764.5, "payment_currency": "US Dollar", "amount_received": 400764.5, "receiving_currency": "US Dollar", "payment_format": "Cheque"}}`
Contrôle automatique : ['pattern fan_out absent', 'voisin 1207505 absent', 'voisin 1760482 absent', 'voisin 2271977 absent', 'voisin 2419933 absent', 'voisin 2419934 absent', 'voisin 4078002 absent', 'voisin 4133281 absent', 'voisin 4345797 absent', 'voisin 4364907 absent', 'voisin 4374819 absent', 'date/heure 09/09/2022 08:08 absentes', 'amount_paid 400 764,50 absent', 'amount_received 400 764,50 absent', 'payment_currency US Dollar absent', 'receiving_currency US Dollar absent', 'from_account 80163FC30 absent', 'to_account 811006A00 absent'] | recopie du prompt : False | terminé : True

```
RAPPORT D'AUDIT — Transaction 4446104

1. Résumé
   - L'alerte contient des informations sur une transaction de paiement de 400,764.5 USD entre une banque (from_bank: 2824) et une autre banque (to_bank: 123390) via une méthode de paiement (payment_format: Cheque).
   - Le score est de 0.874, avec une confiance de 0.382.
   - Le schéma détecté est [pair_prev, dst_in_cnt_all, src_in_cnt_all].
   - Les facteurs explicatifs sont [0.376, 0.127, 0.074].
   - Les références réglementaires pertinents sont [GAFI, droit marocain].
   - Les recommandations sont [n'appliquer pas de règles spécifiques à cette transaction].

2. Schéma détecté
   - Cette transaction est un paiement de 400,764.5 USD entre deux banques, avec une méthode de paiement via un cheque.

3. Facteurs explicatifs
   - Le paiement est effectué entre deux banques.
   - Le cheque est utilisé pour le paiement.
   - La méthode de paiement est de cheque.

4. Références réglementaires
   - GAFI : Gestion des affaires financières internationales (Gestion des affaires financières internationales)
   - Droit marocain : Droit de la banque marocaine

5. Recommandations
   - L'alerte ne contient pas de règles spécifiques à cette transaction.
   - L'alerte n'a pas d'impact sur la conformité bancaire.
   - L'alerte n'a pas d'impact sur la lutte contre le blanchiment de capitaux et le financement du terrorisme.

6. Contexte
   - L'alerte contient des informations sur une transaction de paiement de 400,764.5 USD entre une banque et une autre banque via une méthode de paiement (Cheque).
   - Le contexte est le paiement de 400,764.5 USD entre deux banques, avec une méthode de paiement via un cheque.
   - Le contexte est le paiement de 400,764.5 USD entre deux banques, avec une méthode de paiement via un cheque.
```

Grille : clarté __/5 | citations justes __/5 | remarques :

## Prompt seul + RAG

### Exemple 1 — alert-4792264
Entrée : `{"tx_id": 4792264, "score": 0.973, "confidence": 0.717, "top_features": [["pair_prev", 0.307], ["dst_in_cnt_all", 0.162], ["payment_format", 0.129]], "signs": [1, -1, 1], "neighbors": [14027, 650688, 1028265, 2649157], "pattern": "none", "context": {"timestamp": "2022-09-09 21:06:00", "from_bank": 23537, "from_account": "80EC75590", "to_bank": 16224, "to_account": "80EC83FC0", "amount_paid": 787.36, "payment_currency": "US Dollar", "amount_received": 787.36, "receiving_currency": "US Dollar", "payment_format": "ACH"}}`
Contrôle automatique : ['pattern none absent', 'voisin 14027 absent', 'voisin 650688 absent', 'voisin 1028265 absent', 'voisin 2649157 absent', 'date/heure 09/09/2022 21:06 absentes', 'amount_paid 787,36 absent', 'amount_received 787,36 absent', 'payment_currency US Dollar absent', 'receiving_currency US Dollar absent', 'from_bank 23537 absent', 'to_bank 16224 absent'] | recopie du prompt : False | terminé : False

```
RAPPORT D'AUDIT — Transaction 4792264

1. Résumé
   - L'alerte contient des informations sur une transaction de 4792264, qui a été détectée dans le contexte de la lutte contre le blanchiment de capitaux et le financement du terrorisme.
   - Le schéma détecté est basé sur les facteurs suivants : 
     - Le score est de 0.973, qui est considéré comme élevé.
     - La confiance est de 0.717, qui est considérée comme élevée.
     - Le schéma est "pair_prev" et "dst_in_cnt_all", qui sont considérés comme pertinents.
     - Le poids de chaque facteur est de 0.307, 0.162 et 0.129, respectivement.
     - Le schéma "payment_format" est considéré comme pertinent.
     - Le schéma "signs" est considéré comme pertinent.
     - Le schéma "neighbors" est considéré comme pertinent.
     - Le schéma "pattern" est considéré comme pertinent.
     - Le contexte mentionne la date de l'alerte (2022-09-09 21:06:00) et le type de transaction (ACH).
     - Le contexte mentionne également le type de transaction (ACH) et le type de client (80EC75590, 80EC83FC0).

2. Schéma détecté
   - Le schéma détecté est basé sur les facteurs suivants :
     - Le schéma "pair_prev" est considéré comme pertinent.
     - Le schéma "dst_in_cnt_all" est considéré comme pertinent.
     - Le schéma "payment_format" est considéré comme pertinent.
     - Le schéma "signs" est considéré comme pertinent.
     - Le schéma "neighbors" est considéré comme pertinent.
     - Le schéma "pattern" est considéré comme pertinent.
     - Le schéma "context" est considéré comme pertinent.

3. Facteurs explicatifs
   - Le schéma "pair_prev" est utilisé pour identifier les transactions précédentes, ce qui peut aider à détecter les transactions à risque.
   - Le schéma "dst_in_cnt_all" est utilisé pour identifier les transactions qui ont des clients à risque élevé, ce qui peut aider à détecter les transactions à risque.
   - Le schéma "payment_format" est utilisé pour identifier les transactions qui ont des transactions de type ACH, ce qui peut aider à détecter les transactions à risque.
   - Le schéma "signs" est utilisé pour identifier les transactions qui ont des signes de blanchiment de capitaux ou de financement du terrorisme, ce qui peut aider à détecter les transactions à risque.
   - Le schéma "neighbors" est utilisé pour identifier les transactions qui ont des clients à risque élevé, ce qui peut aider à détecter les transactions à risque.
   - Le schéma "pattern" est utilisé pour identifier les transactions qui ont des transactions de type ACH, ce qui peut aider à détecter les transactions à risque.
   - Le schéma "context" est utilisé pour identifier les transactions qui ont des clients à risque élevé, ce qui peut aider à détecter les transactions à risque.

4. Références réglementaires
   - L'alerte mentionne des textes réglementaires pertinents, tels que :
     - Lutte-contre-le-blanchiment-de-capitaux.pdf, p.11-12 : 1 : Obligations de vigilance Article 39 Les personnes assujetties sont tenues de mettre en place des politiques et des règles de contrôle interne, des mesures de vigilance et de détection ainsi que des procédures de lutte contre le blanchiment de capitaux et le financement du terrorisme selon une approche basée sur les risques, adaptées à la nature et à la taille de leurs activités et aux risques liés à ces activités, leur permettant : -d’effectuer une gestion continue des risques en les identifiant, les comprenant, les évaluant et en prenant les mesures susceptibles de les atténuer ; -de prendre des mesures renforcées pour gérer et atténuer les risques identifiés comme étant élevés ; -d’adopter des procédures simplifiées lors de l’indentification des risques faibles, sauf dans les cas où la présentation d’une déclaration de soupçon est requise ; -d’assurer le suivi de la mise en œuvre des règles de contrôle interne et les renforcer, le cas échéant ; - d’évaluer, de documenter et mettre à jour périodiquement les risques internes de blanchiment de capitaux et de financement du terrorisme et [...]
     - Guide-LBC-FT-F
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### Exemple 2 — alert-4042285
Entrée : `{"tx_id": 4042285, "score": 0.981, "confidence": 0.778, "top_features": [["pair_prev", 0.351], ["dst_in_cnt_all", 0.149], ["payment_format", 0.143]], "signs": [1, -1, 1], "neighbors": [181033, 3839410, 3899241, 3899242, 3989754, 4042284], "pattern": "fan_out", "context": {"timestamp": "2022-09-08 15:11:00", "from_bank": 22, "from_account": "800241D60", "to_bank": 4, "to_account": "800370A40", "amount_paid": 2854.57, "payment_currency": "Yuan", "amount_received": 2854.57, "receiving_currency": "Yuan", "payment_format": "ACH"}}`
Contrôle automatique : ['pattern fan_out absent', 'feature pair_prev absente', 'poids 0,351 (pair_prev) absent', 'feature dst_in_cnt_all absente', 'poids 0,149 (dst_in_cnt_all) absent', 'feature payment_format absente', 'poids 0,143 (payment_format) absent', 'voisin 181033 absent', 'voisin 3839410 absent', 'voisin 3899241 absent', 'voisin 3899242 absent', 'voisin 3989754 absent', 'voisin 4042284 absent', 'date/heure 08/09/2022 15:11 absentes', 'amount_paid 2 854,57 absent', 'amount_received 2 854,57 absent', 'payment_currency Yuan absent', 'receiving_currency Yuan absent', 'payment_format ACH absent', 'from_account 800241D60 absent', 'to_account 800370A40 absent'] | recopie du prompt : False | terminé : False

```
RAPPORT D'AUDIT — Transaction 4042285

1. Résumé
   - L'alerte contient des informations sur une transaction de 4042285, qui correspond à une transaction de paiement d'un compte bancaire.
   - Cette transaction a un score de 0.981, une confiance de 0.778, et un schéma de 1, 149, 143.
   - Les facteurs explicatifs incluent les opérations liées aux activités suivantes : l'achat ou la vente de biens immobiliers, d'actifs commerciaux ou de l'un de leurs éléments, la gestion de fonds, de titres, de comptes bancaires, de dépôt ou d'autres actifs appartenant au client, l'organisation et l'évaluation des parts nécessaires à la constitution des capitaux des sociétés ou à leur gestion ou exploitation, la constitution, la gestion ou l’exploitation des personnes morales, la vente ou l’achat des parts ou d’actions des sociétés commerciales, l’agissement en tant que mandataire dans la constitution des sociétés, la direction ou la gestion des sociétés ou la prise directe ou indirecte de participation dans celles-ci, la domiciliation des sociétés, pour les agents immobiliers, lorsqu’ils préparent ou réalisent, pour le compte de leurs clients, des opérations d’achat ou de vente de biens immobiliers ou y participent, et pour les casinos ou les établissements de jeux de hasard, lorsque les clients ont participé à des opérations d’achat ou de vente de biens immobiliers ou y participent.
   - Les facteurs de la transaction incluent les opérations liées aux activités suivantes : l'agissement en tant que mandataire dans la constitution des sociétés, la direction ou la gestion des sociétés ou la prise directe ou indirecte de participation dans celles-ci, la domiciliation des sociétés, pour les agents immobiliers, lorsqu’ils préparent ou réalisent, pour le compte de leurs clients, des opérations d’achat ou de vente de biens immobiliers ou y participent, et pour les casinos ou les établissements de jeux de hasard, lorsque les clients ont participé à des opérations d’achat ou de vente de biens immobiliers ou y participent.
   - Les facteurs de la transaction incluent les opérations liées aux activités suivantes : l'agissement en tant que mandataire dans la constitution des sociétés, la direction ou la gestion des sociétés ou la prise directe ou indirecte de participation dans celles-ci, la domiciliation des sociétés, pour les agents immobiliers, lorsqu’ils préparent ou réalisent, pour le compte de leurs clients, des opérations d’achat ou de vente de biens immobiliers ou y participent, et pour les casinos ou les établissements de jeux de hasard, lorsque les clients ont participé à des opérations d’achat ou de vente de biens immobiliers ou y participent.

2. Schéma détecté
   - La transaction correspond à une opération de paiement d'un compte bancaire.
   - La transaction a un score de 0.981, une confiance de 0.778, et un schéma de 1, 149, 143.
   - Les facteurs explicatifs incluent les opérations liées aux activités suivantes : l'achat ou la vente de biens immobiliers, d'actifs commerciaux ou de l'un de leurs éléments, la gestion de fonds, de titres, de comptes bancaires, de dépôt ou d'autres actifs appartenant au client, l'organisation et l'évaluation des parts nécessaires à la constitution des capitaux des sociétés ou à leur gestion ou exploitation, la constitution, la gestion ou l’exploitation des personnes morales, la vente ou l’achat des parts ou d’actions des sociétés commerciales, l’agissement en tant que mandataire dans la constitution des sociétés, la direction ou la gestion des sociétés ou la prise directe ou indirecte de participation dans celles-ci, la domiciliation des sociétés, pour les agents immobiliers, lorsqu’ils préparent ou réalisent, pour le compte de leurs clients, des opérations d’achat ou de vente de biens immobiliers ou y participent, et pour les casinos ou les établissements de jeux de hasard, lorsque les clients ont participé à des opérations d’achat ou de vente de biens immobiliers ou y participent.

3. Facteurs explicatifs
   - Les opérations liées aux activités suivantes : l'achat ou la vente de biens immobiliers, d'actifs commerciaux ou de l'un de leurs éléments, la gestion de fonds, de titres, de comptes bancaires, de dépôt ou d'autres actifs appartenant au client, l'organisation et l'évaluation des parts nécessaires à la constitution
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### Exemple 3 — alert-4446104
Entrée : `{"tx_id": 4446104, "score": 0.874, "confidence": 0.382, "top_features": [["pair_prev", 0.376], ["dst_in_cnt_all", 0.127], ["src_in_cnt_all", 0.074]], "signs": [1, -1, 1], "neighbors": [1207505, 1760482, 2271977, 2419933, 2419934, 4078002, 4133281, 4345797, 4364907, 4374819], "pattern": "fan_out", "context": {"timestamp": "2022-09-09 08:08:00", "from_bank": 2824, "from_account": "80163FC30", "to_bank": 123390, "to_account": "811006A00", "amount_paid": 400764.5, "payment_currency": "US Dollar", "amount_received": 400764.5, "receiving_currency": "US Dollar", "payment_format": "Cheque"}}`
Contrôle automatique : ['pattern fan_out absent', 'poids 0,376 (pair_prev) absent', 'poids 0,127 (dst_in_cnt_all) absent', 'poids 0,074 (src_in_cnt_all) absent', 'voisin 1207505 absent', 'voisin 1760482 absent', 'voisin 2271977 absent', 'voisin 2419933 absent', 'voisin 2419934 absent', 'voisin 4078002 absent', 'voisin 4133281 absent', 'voisin 4345797 absent', 'voisin 4364907 absent', 'voisin 4374819 absent', 'date/heure 09/09/2022 08:08 absentes', 'amount_paid 400 764,50 absent', 'amount_received 400 764,50 absent', 'payment_currency US Dollar absent', 'receiving_currency US Dollar absent', 'payment_format Cheque absent', 'from_account 80163FC30 absent', 'to_account 811006A00 absent', 'from_bank 2824 absent', 'to_bank 123390 absent'] | recopie du prompt : False | terminé : False

```
RAPPORT D'AUDIT — Transaction 4446104

1. Résumé
   - L'alerte contient des informations sur une transaction de 4446104, qui correspond à une transaction de paiement de 400764.5 USD.
   - Le score de l'alerte est de 0.874, avec une confiance de 0.382.
   - Le schéma détecté est le "fan-out" (dans le contexte de la réglementation bancaire).
   - Les facteurs explicatifs sont les "pair_prev" (dans le contexte de la réglementation bancaire), "dst_in_cnt_all" (dans le contexte de la réglementation bancaire), "src_in_cnt_all" (dans le contexte de la réglementation bancaire), "signs" (dans le contexte de la réglementation bancaire), "neighbors" (dans le contexte de la réglementation bancaire), "pattern" (dans le contexte de la réglementation bancaire), "context" (dans le contexte de la réglementation bancaire), "timestamp" (dans le contexte de la réglementation bancaire), "from_bank" (dans le contexte de la réglementation bancaire), "from_account" (dans le contexte de la réglementation bancaire), "to_bank" (dans le contexte de la réglementation bancaire), "to_account" (dans le contexte de la réglementation bancaire), "amount_paid" (dans le contexte de la réglementation bancaire), "payment_currency" (dans le contexte de la réglementation bancaire), "amount_received" (dans le contexte de la réglementation bancaire), "receiving_currency" (dans le contexte de la réglementation bancaire), "payment_format" (dans le contexte de la réglementation bancaire).
   - Le schéma détecté est le "fan-out" (dans le contexte de la réglementation bancaire).
   - Les facteurs explicatifs sont les "pair_prev" (dans le contexte de la réglementation bancaire), "dst_in_cnt_all" (dans le contexte de la réglementation bancaire), "src_in_cnt_all" (dans le contexte de la réglementation bancaire), "signs" (dans le contexte de la réglementation bancaire), "neighbors" (dans le contexte de la réglementation bancaire), "pattern" (dans le contexte de la réglementation bancaire), "context" (dans le contexte de la réglementation bancaire), "timestamp" (dans le contexte de la réglementation bancaire), "from_bank" (dans le contexte de la réglementation bancaire), "from_account" (dans le contexte de la réglementation bancaire), "to_bank" (dans le contexte de la réglementation bancaire), "to_account" (dans le contexte de la réglementation bancaire), "amount_paid" (dans le contexte de la réglementation bancaire), "payment_currency" (dans le contexte de la réglementation bancaire), "amount_received" (dans le contexte de la réglementation bancaire), "receiving_currency" (dans le contexte de la réglementation bancaire), "payment_format" (dans le contexte de la réglementation bancaire).

2. Schéma détecté
   - Le schéma détecté est le "fan-out" (dans le contexte de la réglementation bancaire).
   - Les facteurs explicatifs sont les "pair_prev" (dans le contexte de la réglementation bancaire), "dst_in_cnt_all" (dans le contexte de la réglementation bancaire), "src_in_cnt_all" (dans le contexte de la réglementation bancaire), "signs" (dans le contexte de la réglementation bancaire), "neighbors" (dans le contexte de la réglementation bancaire), "pattern" (dans le contexte de la réglementation bancaire), "context" (dans le contexte de la réglementation bancaire), "timestamp" (dans le contexte de la réglementation bancaire), "from_bank" (dans le contexte de la réglementation bancaire), "from_account" (dans le contexte de la réglementation bancaire), "to_bank" (dans le contexte de la réglementation bancaire), "to_account" (dans le contexte de la réglementation bancaire), "amount_paid" (dans le contexte de la réglementation bancaire), "payment_currency" (dans le contexte de la réglementation bancaire), "amount_received" (dans le context
```

Grille : clarté __/5 | citations justes __/5 | remarques :

## LoRA r=16

### Exemple 1 — alert-4792264
Entrée : `{"tx_id": 4792264, "score": 0.973, "confidence": 0.717, "top_features": [["pair_prev", 0.307], ["dst_in_cnt_all", 0.162], ["payment_format", 0.129]], "signs": [1, -1, 1], "neighbors": [14027, 650688, 1028265, 2649157], "pattern": "none", "context": {"timestamp": "2022-09-09 21:06:00", "from_bank": 23537, "from_account": "80EC75590", "to_bank": 16224, "to_account": "80EC83FC0", "amount_paid": 787.36, "payment_currency": "US Dollar", "amount_received": 787.36, "receiving_currency": "US Dollar", "payment_format": "ACH"}}`
Contrôle automatique : aucun écart | recopie du prompt : False | terminé : True

```
RAPPORT D'AUDIT — Transaction 4792264

1. Résumé
La transaction 4792264 a été signalée par le détecteur avec un score brut de 0,973 et une confiance calibrée de 0,717 (niveau de risque élevé, fiabilité du schéma limitée). Le schéma détecté est moins discriminant : une validation humaine est nécessaire.
Transaction du 09/09/2022 à 21:06, d'un montant de 787,36 US Dollar, du compte 80EC75590 (banque 23537) vers le compte 80EC83FC0 (banque 16224), format de paiement ACH.

2. Schéma détecté
Schéma : none — aucun schéma structurel connu (circuit fermé, concentration, dispersion) n'a été détecté dans le voisinage ; l'alerte repose sur les caractéristiques propres de la transaction.
Voisinage : 4 transactions voisines dans le graphe (14027, 650688, 1028265, 2649157).

3. Facteurs explicatifs
- Le nombre de transactions antérieures entre ces deux mêmes comptes (pair_prev) : poids 0,307 — facteur principal, aggravant
- Le nombre de transactions entrantes passées du compte destinataire (dst_in_cnt_all) : poids 0,162 — atténuant
- Le format de paiement utilisé (payment_format) : poids 0,129 — aggravant
Ces facteurs décrivent les caractéristiques de la transaction ; le contexte réseau des comptes (comptes voisins) n'est pas détaillé.

4. Références réglementaires
- Recommandation 10 du GAFI (vigilance à l'égard de la clientèle) : les institutions financières exercent une vigilance constante sur la relation d'affaires et examinent les transactions pour s'assurer qu'elles sont cohérentes avec leur connaissance du client.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).
- Recommandation 21 du GAFI (divulgation et confidentialité) : il est interdit de révéler au client ou à un tiers qu'une déclaration de soupçon ou une information connexe est transmise à la CRF.
- Droit marocain (loi relative à la lutte contre le blanchiment de capitaux) : les personnes assujetties doivent déclarer à l'autorité compétente les opérations qu'elles soupçonnent d'être liées au blanchiment de capitaux ou au financement du terrorisme.

5. Recommandations
- Revue manuelle prioritaire de la transaction et de son voisinage.
- Vérification de la cohérence avec le profil et l'historique du client.
- Déclaration de soupçon à envisager si l'analyse confirme le doute.
- Examiner l'historique du client pour confirmer ou écarter le caractère inhabituel.
- Ne pas informer le client de l'existence de cette alerte (interdiction de divulgation).

Ce rapport est généré automatiquement pour assister l'analyste ; la décision finale de déclaration lui appartient.
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### Exemple 2 — alert-4042285
Entrée : `{"tx_id": 4042285, "score": 0.981, "confidence": 0.778, "top_features": [["pair_prev", 0.351], ["dst_in_cnt_all", 0.149], ["payment_format", 0.143]], "signs": [1, -1, 1], "neighbors": [181033, 3839410, 3899241, 3899242, 3989754, 4042284], "pattern": "fan_out", "context": {"timestamp": "2022-09-08 15:11:00", "from_bank": 22, "from_account": "800241D60", "to_bank": 4, "to_account": "800370A40", "amount_paid": 2854.57, "payment_currency": "Yuan", "amount_received": 2854.57, "receiving_currency": "Yuan", "payment_format": "ACH"}}`
Contrôle automatique : aucun écart | recopie du prompt : False | terminé : True

```
RAPPORT D'AUDIT — Transaction 4042285

1. Résumé
La transaction 4042285 a été signalée par le détecteur avec un score brut de 0,981 et une confiance calibrée de 0,778 (niveau de risque élevé, fiabilité du schéma élevée).
Transaction du 08/09/2022 à 15:11, d'un montant de 2 854,57 Yuan, du compte 800241D60 (banque 22) vers le compte 800370A40 (banque 4), format de paiement ACH.

2. Schéma détecté
Schéma : fan_out — dispersion de fonds : un compte redistribue rapidement des fonds vers de nombreux comptes, schéma compatible avec un fractionnement des montants.
Voisinage : 6 transactions voisines dans le graphe (181033, 3839410, 3899241, 3899242, 3989754, 4042284).

3. Facteurs explicatifs
- Le nombre de transactions antérieures entre ces deux mêmes comptes (pair_prev) : poids 0,351 — facteur principal, aggravant
- Le nombre de transactions entrantes passées du compte destinataire (dst_in_cnt_all) : poids 0,149 — atténuant
- Le format de paiement utilisé (payment_format) : poids 0,143 — aggravant
Ces facteurs décrivent les caractéristiques de la transaction ; le contexte réseau des comptes (comptes voisins) n'est pas détaillé.

4. Références réglementaires
- Recommandation 16 du GAFI (virements électroniques) : les informations sur le donneur d'ordre et le bénéficiaire doivent accompagner les virements afin de pouvoir retracer l'opération.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).
- Recommandation 21 du GAFI (divulgation et confidentialité) : il est interdit de révéler au client ou à un tiers qu'une déclaration de soupçon ou une information connexe est transmise à la CRF.
- Droit marocain (loi relative à la lutte contre le blanchiment de capitaux) : les personnes assujetties doivent déclarer à l'autorité compétente les opérations qu'elles soupçonnent d'être liées au blanchiment de capitaux ou au financement du terrorisme.

5. Recommandations
- Revue manuelle prioritaire de la transaction et de son voisinage.
- Vérification de la cohérence avec le profil et l'historique du client.
- Déclaration de soupçon à envisager si l'analyse confirme le doute.
- Identifier les bénéficiaires des dispersions et vérifier leur justification économique.
- Ne pas informer le client de l'existence de cette alerte (interdiction de divulgation).

Ce rapport est généré automatiquement pour assister l'analyste ; la décision finale de déclaration lui appartient.
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### Exemple 3 — alert-4446104
Entrée : `{"tx_id": 4446104, "score": 0.874, "confidence": 0.382, "top_features": [["pair_prev", 0.376], ["dst_in_cnt_all", 0.127], ["src_in_cnt_all", 0.074]], "signs": [1, -1, 1], "neighbors": [1207505, 1760482, 2271977, 2419933, 2419934, 4078002, 4133281, 4345797, 4364907, 4374819], "pattern": "fan_out", "context": {"timestamp": "2022-09-09 08:08:00", "from_bank": 2824, "from_account": "80163FC30", "to_bank": 123390, "to_account": "811006A00", "amount_paid": 400764.5, "payment_currency": "US Dollar", "amount_received": 400764.5, "receiving_currency": "US Dollar", "payment_format": "Cheque"}}`
Contrôle automatique : aucun écart | recopie du prompt : False | terminé : True

```
RAPPORT D'AUDIT — Transaction 4446104

1. Résumé
La transaction 4446104 a été signalée par le détecteur avec un score brut de 0,874 et une confiance calibrée de 0,382 (niveau de risque modéré, fiabilité du schéma élevée).
Transaction du 09/09/2022 à 08:08, d'un montant de 400 764,50 US Dollar, du compte 80163FC30 (banque 2824) vers le compte 811006A00 (banque 123390), format de paiement Cheque.

2. Schéma détecté
Schéma : fan_out — dispersion de fonds : un compte redistribue rapidement des fonds vers de nombreux comptes, schéma compatible avec un fractionnement des montants.
Voisinage : 10 transactions voisines dans le graphe (1207505, 1760482, 2271977, 2419933, 2419934, 4078002, 4133281, 4345797, 4364907, 4374819).

3. Facteurs explicatifs
- Le nombre de transactions antérieures entre ces deux mêmes comptes (pair_prev) : poids 0,376 — facteur principal, aggravant
- Le nombre de transactions entrantes passées du compte destinataire (dst_in_cnt_all) : poids 0,127 — atténuant
- Le nombre de transactions entrantes passées du compte émetteur (src_in_cnt_all) : poids 0,074 — aggravant
Ces facteurs décrivent les caractéristiques de la transaction ; le contexte réseau des comptes (comptes voisins) n'est pas détaillé.

4. Références réglementaires
- Recommandation 16 du GAFI (virements électroniques) : les informations sur le donneur d'ordre et le bénéficiaire doivent accompagner les virements afin de pouvoir retracer l'opération.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).
- Droit marocain (loi relative à la lutte contre le blanchiment de capitaux) : les personnes assujetties doivent déclarer à l'autorité compétente les opérations qu'elles soupçonnent d'être liées au blanchiment de capitaux ou au financement du terrorisme.

5. Recommandations
- Surveillance renforcée du compte concerné.
- Revue manuelle si de nouvelles alertes apparaissent.
- Pas de déclaration à ce stade.
- Identifier les bénéficiaires des dispersions et vérifier leur justification économique.

Ce rapport est généré automatiquement pour assister l'analyste ; la décision finale de déclaration lui appartient.
```

Grille : clarté __/5 | citations justes __/5 | remarques :

## LoRA r=16 + RAG

### Exemple 1 — alert-4792264
Entrée : `{"tx_id": 4792264, "score": 0.973, "confidence": 0.717, "top_features": [["pair_prev", 0.307], ["dst_in_cnt_all", 0.162], ["payment_format", 0.129]], "signs": [1, -1, 1], "neighbors": [14027, 650688, 1028265, 2649157], "pattern": "none", "context": {"timestamp": "2022-09-09 21:06:00", "from_bank": 23537, "from_account": "80EC75590", "to_bank": 16224, "to_account": "80EC83FC0", "amount_paid": 787.36, "payment_currency": "US Dollar", "amount_received": 787.36, "receiving_currency": "US Dollar", "payment_format": "ACH"}}`
Contrôle automatique : aucun écart | recopie du prompt : False | terminé : True

```
RAPPORT D'AUDIT — Transaction 4792264

1. Résumé
La transaction 4792264 a été signalée par le détecteur avec un score brut de 0,973 et une confiance calibrée de 0,717 (niveau de risque élevé, fiabilité du schéma limitée). Le schéma détecté est moins discriminant : une validation humaine est nécessaire.
Transaction du 09/09/2022 à 21:06, d'un montant de 787,36 US Dollar, du compte 80EC75590 (banque 23537) vers le compte 80EC83FC0 (banque 16224), format de paiement ACH.

2. Schéma détecté
Schéma : none — aucun schéma structurel connu (circuit fermé, concentration, dispersion) n'a été détecté dans le voisinage ; l'alerte repose sur les caractéristiques propres de la transaction.
Voisinage : 4 transactions voisines dans le graphe (14027, 650688, 1028265, 2649157).

3. Facteurs explicatifs
- Le nombre de transactions antérieures entre ces deux mêmes comptes (pair_prev) : poids 0,307 — facteur principal, aggravant
- Le nombre de transactions entrantes passées du compte destinataire (dst_in_cnt_all) : poids 0,162 — atténuant
- Le format de paiement utilisé (payment_format) : poids 0,129 — aggravant
Ces facteurs décrivent les caractéristiques de la transaction ; le contexte réseau des comptes (comptes voisins) n'est pas détaillé.

4. Références réglementaires
- Recommandation 10 du GAFI (vigilance à l'égard de la clientèle) : les institutions de crédit exercent une vigilance constante sur la relation d'affaires et examinent les transactions pour s'assurer qu'elles sont cohérentes avec leur connaissance du client.
- Recommandation 20 du GAFI (déclaration de soupçon) : lorsqu'une institution de crédit soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).
- Droit marocain (loi relative à la lutte contre le blanchiment de capitaux) : les personnes assujetties doivent déclarer à l'autorité compétente les opérations qu'elles soupçonnent d'être liées au blanchiment de capitaux ou au financement du terrorisme.

5. Recommandations
- Revue manuelle dans le cadre du traitement normal des alertes.
- Vérification de la cohérence avec le profil du client.
- Pas de déclaration à ce stade sans élément complémentaire.
- Identifier les clients inhabituels ou those qui émettent des alertes.

Rapport d'aide à la décision, généré automatiquement : la décision finale relève de l'analyste conformité.
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### Exemple 2 — alert-4042285
Entrée : `{"tx_id": 4042285, "score": 0.981, "confidence": 0.778, "top_features": [["pair_prev", 0.351], ["dst_in_cnt_all", 0.149], ["payment_format", 0.143]], "signs": [1, -1, 1], "neighbors": [181033, 3839410, 3899241, 3899242, 3989754, 4042284], "pattern": "fan_out", "context": {"timestamp": "2022-09-08 15:11:00", "from_bank": 22, "from_account": "800241D60", "to_bank": 4, "to_account": "800370A40", "amount_paid": 2854.57, "payment_currency": "Yuan", "amount_received": 2854.57, "receiving_currency": "Yuan", "payment_format": "ACH"}}`
Contrôle automatique : aucun écart | recopie du prompt : False | terminé : True

```
RAPPORT D'AUDIT — Transaction 4042285

1. Résumé
La transaction 4042285 a été signalée par le détecteur avec un score brut de 0,981 et une confiance calibrée de 0,778 (niveau de risque élevé, fiabilité du schéma élevée).
Transaction du 08/09/2022 à 15:11, d'un montant de 2 854,57 Yuan, du compte 800241D60 (client 22) vers le compte 800370A40 (client 4), format de paiement ACH.

2. Schéma détecté
Schéma : fan_out — dispersion de fonds : un compte redistribue rapidement des fonds vers de nombreux comptes, schéma compatible avec un fractionnement des montants.
Voisinage : 6 transactions voisines dans le graphe (181033, 3839410, 3899241, 3899242, 3989754, 4042284).

3. Facteurs explicatifs
- Le nombre de transactions antérieures entre ces deux mêmes comptes (pair_prev) : poids 0,351 — facteur principal, aggravant
- Le nombre de transactions entrantes passées du compte destinataire (dst_in_cnt_all) : poids 0,149 — atténuant
- Le format de paiement utilisé (payment_format) : poids 0,143 — aggravant
Ces facteurs décrivent les caractéristiques de la transaction ; le contexte réseau des comptes (comptes voisins) n'est pas détaillé.

4. Références réglementaires
- Recommandation 10 du GAFI (vigilance à l'égard de des clients et de leurs opérations) : les institutions financières exercent une vigilance constante sur la relation d'affaires et examinent les transactions pour s'assurer qu'elles sont cohérentes avec leur connaissance du client.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).
- Droit marocain (loi relative à la lutte contre le blanchiment de capitaux) : les personnes assujetties doivent déclarer à l'autorité compétente les opérations qu'elles soupçonnent d'être liées au blanchiment de capitaux ou au financement du terrorisme.

5. Recommandations
- Revue manuelle dans le cadre du traitement normal des alertes.
- Vérification de la cohérence avec le profil du client.
- Pas de déclaration à ce stade sans élément complémentaire.
- Reconstituer le circuit complet des fonds et identifier les clients émetteurs.
- Ne pas informer le client de l'existence de cette alerte (interdiction de divulgation).

Rapport d'aide à la décision, généré automatiquement : la décision finale relève de l'analyste conformité.
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### Exemple 3 — alert-4446104
Entrée : `{"tx_id": 4446104, "score": 0.874, "confidence": 0.382, "top_features": [["pair_prev", 0.376], ["dst_in_cnt_all", 0.127], ["src_in_cnt_all", 0.074]], "signs": [1, -1, 1], "neighbors": [1207505, 1760482, 2271977, 2419933, 2419934, 4078002, 4133281, 4345797, 4364907, 4374819], "pattern": "fan_out", "context": {"timestamp": "2022-09-09 08:08:00", "from_bank": 2824, "from_account": "80163FC30", "to_bank": 123390, "to_account": "811006A00", "amount_paid": 400764.5, "payment_currency": "US Dollar", "amount_received": 400764.5, "receiving_currency": "US Dollar", "payment_format": "Cheque"}}`
Contrôle automatique : aucun écart | recopie du prompt : False | terminé : True

```
RAPPORT D'AUDIT — Transaction 4446104

1. Résumé
La transaction 4446104 a été signalée par le détecteur avec un score brut de 0,874 et une confiance calibrée de 0,382 (niveau de risque modéré, fiabilité du schéma élevée).
Transaction du 09/09/2022 à 08:08, d'un montant de 400 764,50 US Dollar, du compte 80163FC30 (client 2824) vers le compte 811006A00 (client 123390), format de paiement Cheque.

2. Schéma détecté
Schéma : fan_out — dispersion de fonds : un compte redistribue rapidement des fonds vers de nombreux comptes, schéma compatible avec un fractionnement des montants.
Voisinage : 10 transactions voisines dans le graphe (1207505, 1760482, 2271977, 2419933, 2419934, 4078002, 4133281, 4345797, 4364907, 4374819).

3. Facteurs explicatifs
- Le nombre de transactions antérieures entre ces deux mêmes comptes (pair_prev) : poids 0,376 — facteur principal, aggravant
- Le nombre de transactions entrantes passées du compte destinataire (dst_in_cnt_all) : poids 0,127 — atténuant
- Le nombre de transactions entrantes passées du compte émetteur (src_in_cnt_all) : poids 0,074 — aggravant
Ces facteurs décrivent les caractéristiques de la transaction ; le contexte réseau des comptes (comptes voisins) n'est pas détaillé.

4. Références réglementaires
- Recommandation 10 du GAFI (vigilance à l'égard de des clients et de leurs opérations) : les institutions financières exercent une vigilance constante sur la relation d'affaires et examinent les transactions pour s'assurer qu'elles sont cohérentes avec leur connaissance du client.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).
- Droit marocain (loi relative à la lutte contre le blanchiment de capitaux) : les personnes assujetties doivent déclarer à l'autorité compétente les opérations qu'elles soupçonnent d'être liées au blanchiment de capitaux ou au financement du terrorisme.

5. Recommandations
- Surveillance renforcée du client et le déclaration de soupçon à envisager si de nouvelles alertes apparaissent.
- Revue manuelle si de nouvelles transactions apparaissent dans le voisinage.
- Reconstituer le circuit complet des fonds et identifier les comptes impliqués.
- Ne pas informer le client de l'existence de cette alerte (interdiction de divulgation).

Ce rapport est généré automatiquement pour assister l'analyste ; la décision finale de déclaration lui appartient.
```

Grille : clarté __/5 | citations justes __/5 | remarques :
