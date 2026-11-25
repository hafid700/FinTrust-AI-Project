# Échantillon B6 pour relecture manuelle

## Mode RAG : off

### alert-4792264
Sections remplacées : [] | complet : False

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

6. Éléments d'investigation (outils)
Voisinage :
- Transaction 14027 du 2022-09-01 00:01:00 : montant 78 326 856,95 US Dollar, sens entrante, format Reinvestment
- Transaction 650688 du 2022-09-01 10:10:00 : montant 10 341,88 US Dollar, sens entrante, format Reinvestment
- Transaction 1028265 du 2022-09-01 21:25:00 : montant 5,60 US Dollar, sens entrante, format Reinvestment
- Transaction 2649157 du 2022-09-05 17:56:00 : montant 19 504,66 US Dollar, sens sortante, format ACH
Statistiques du voisinage (calculées sur les transactions voisines, pas sur l'historique complet) :
- 4 transactions voisines (3 entrante(s), 1 sortante(s)) ; montant total 78 356 709,09 ; montant moyen 19 589 177,27 ; 1 contrepartie(s) distincte(s)
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du voisinage
- Rédaction par le LLM-LoRA ; toutes les déductions vérifiées conformes.
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### alert-5078133
Sections remplacées : [] | complet : False

```
RAPPORT D'AUDIT — Transaction 5078133

1. Résumé
La transaction 5078133 a été signalée par le détecteur avec un score brut de 0,996 et une confiance calibrée de 0,931 (niveau de risque critique, fiabilité du schéma élevée).
Transaction du 14/09/2022 à 08:07, d'un montant de 10 874,08 Euro, du compte 8051E3B20 (banque 1412) vers le compte 806911FE0 (banque 14663), format de paiement ACH.

2. Schéma détecté
Schéma : fan_out — dispersion de fonds : un compte redistribue rapidement des fonds vers de nombreux comptes, schéma compatible avec un fractionnement des montants.
Voisinage : 10 transactions voisines dans le graphe (1683950, 4312934, 4316938, 4319179, 4320043, 5077973, 5077978, 5078048, 5078057, 5078132).

3. Facteurs explicatifs
- Le nombre de transactions antérieures entre ces deux mêmes comptes (pair_prev) : poids 0,282 — facteur principal, aggravant
- Le nombre de transactions entrantes passées du compte destinataire (dst_in_cnt_all) : poids 0,173 — atténuant
- Le format de paiement utilisé (payment_format) : poids 0,129 — aggravant
Ces facteurs décrivent les caractéristiques de la transaction ; le contexte réseau des comptes (comptes voisins) n'est pas détaillé.

4. Références réglementaires
- Recommandation 16 du GAFI (virements électroniques) : les informations sur le donneur d'ordre et le bénéficiaire doivent accompagner les virements afin de pouvoir retracer l'opération.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).
- Recommandation 21 du GAFI (divulgation et confidentialité) : il est interdit de révéler au client ou à un tiers qu'une déclaration de soupçon ou une information connexe est transmise à la CRF.
- Droit marocain (loi relative à la lutte contre le blanchiment de capitaux) : les personnes assujetties doivent déclarer à l'autorité compétente les opérations qu'elles soupçonnent d'être liées au blanchiment de capitaux ou au financement du terrorisme.

5. Recommandations
- Escalade immédiate au responsable conformité.
- Revue manuelle prioritaire de la transaction et des transactions voisines.
- Préparation d'une déclaration de soupçon si les éléments sont confirmés.
- Identifier les bénéficiaires des dispersions et vérifier leur justification économique.
- Ne pas informer le client de l'existence de cette alerte (interdiction de divulgation).

Rapport d'aide à la décision, généré automatiquement : la décision finale relève de l'analyste conformité.

6. Éléments d'investigation (outils)
Voisinage :
- Transaction 1683950 du 2022-09-02 17:57:00 : montant 9 801,33 Euro, sens sortante, format Cash
- Transaction 4312934 du 2022-09-09 03:08:00 : montant 121,20 Euro, sens sortante, format ACH
- Transaction 4316938 du 2022-09-09 03:17:00 : montant 9 801,33 Euro, sens sortante, format Cash
- Transaction 4319179 du 2022-09-09 03:22:00 : montant 2 036,24 Euro, sens sortante, format Cheque
- Transaction 4320043 du 2022-09-09 03:24:00 : montant 2 102,23 Euro, sens sortante, format Credit Card
- Transaction 5077973 du 2022-09-13 09:15:00 : montant 59 622,07 Yuan, sens sortante, format ACH
- Transaction 5077978 du 2022-09-13 10:06:00 : montant 10 394,61 US Dollar, sens entrante, format ACH
- Transaction 5078048 du 2022-09-13 15:03:00 : montant 14 195,02 US Dollar, sens entrante, format ACH
- Transaction 5078057 du 2022-09-13 15:33:00 : montant 4 035,86 US Dollar, sens entrante, format ACH
- Transaction 5078132 du 2022-09-14 08:07:00 : montant 12 742,06 US Dollar, sens entrante, format ACH
Statistiques du voisinage (calculées sur les transactions voisines, pas sur l'historique complet) :
- 10 transactions voisines (4 entrante(s), 6 sortante(s)) ; montant total 124 851,95 ; montant moyen 12 485,19 ; 5 contrepartie(s) distincte(s)
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du voisinage
- Rédaction par le LLM-LoRA ; toutes les déductions vérifiées conformes.
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### alert-5077842
Sections remplacées : [] | complet : False

```
RAPPORT D'AUDIT — Transaction 5077842

1. Résumé
La transaction 5077842 a été signalée par le détecteur avec un score brut de 0,932 et une confiance calibrée de 0,527 (niveau de risque modéré à élevé, fiabilité du schéma élevée).
Transaction du 12/09/2022 à 16:27, d'un montant de 14 464,64 US Dollar, du compte 809768440 (banque 5175) vers le compte 8041A3440 (banque 29404), format de paiement ACH.

2. Schéma détecté
Schéma : fan_in — concentration de fonds : de nombreux comptes versent vers un même compte, schéma compatible avec un compte « mule » collecteur.
Voisinage : 10 transactions voisines dans le graphe (3446133, 4135761, 4546558, 4964261, 5029849, 5077581, 5077610, 5077732, 5077827, 5077841).

3. Facteurs explicatifs
- Le nombre de transactions antérieures entre ces deux mêmes comptes (pair_prev) : poids 0,419 — facteur principal, aggravant
- Le format de paiement utilisé (payment_format) : poids 0,167 — aggravant
- Le nombre de transactions entrantes passées du compte destinataire (dst_in_cnt_all) : poids 0,110 — atténuant
Ces facteurs décrivent les caractéristiques de la transaction ; le contexte réseau des comptes (comptes voisins) n'est pas détaillé.

4. Références réglementaires
- Recommandation 10 du GAFI (vigilance à l'égard de la clientèle) : les institutions financières exercent une vigilance constante sur la relation d'affaires et examinent les transactions pour s'assurer qu'elles sont cohérentes avec leur connaissance du client.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).
- Droit marocain (loi relative à la lutte contre le blanchiment de capitaux) : les personnes assujetties doivent déclarer à l'autorité compétente les opérations qu'elles soupçonnent d'être liées au blanchiment de capitaux ou au financement du terrorisme.

5. Recommandations
- Revue manuelle dans le cadre du traitement normal des alertes.
- Vérification de la cohérence avec le profil du client.
- Pas de déclaration à ce stade sans élément complémentaire.
- Identifier les comptes émetteurs et vérifier si le compte collecteur est un compte mule.

Rapport d'aide à la décision, généré automatiquement : la décision finale relève de l'analyste conformité.

6. Éléments d'investigation (outils)
Voisinage :
- Transaction 3446133 du 2022-09-07 09:21:00 : montant 11 481,53 Euro, sens sortante, format Cheque
- Transaction 4135761 du 2022-09-08 19:56:00 : montant 11 481,53 Euro, sens sortante, format Cheque
- Transaction 4546558 du 2022-09-09 11:53:00 : montant 11 481,53 Euro, sens sortante, format Cheque
- Transaction 4964261 du 2022-09-10 09:52:00 : montant 11 481,53 Euro, sens sortante, format Cheque
- Transaction 5029849 du 2022-09-10 18:05:00 : montant 6 776,27 US Dollar, sens entrante, format ACH
- Transaction 5077581 du 2022-09-11 18:55:00 : montant 16 408,23 US Dollar, sens entrante, format ACH
- Transaction 5077610 du 2022-09-11 20:33:00 : montant 790,89 US Dollar, sens entrante, format ACH
- Transaction 5077732 du 2022-09-12 10:23:00 : montant 6 090,71 US Dollar, sens entrante, format ACH
- Transaction 5077827 du 2022-09-12 15:55:00 : montant 19 766,30 US Dollar, sens entrante, format ACH
- Transaction 5077841 du 2022-09-12 16:27:00 : montant 12 344,12 Euro, sens entrante, format ACH
Statistiques du voisinage (calculées sur les transactions voisines, pas sur l'historique complet) :
- 10 transactions voisines (6 entrante(s), 4 sortante(s)) ; montant total 108 102,64 ; montant moyen 10 810,26 ; 6 contrepartie(s) distincte(s)
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du voisinage
- Rédaction par le LLM-LoRA ; toutes les déductions vérifiées conformes.
```

Grille : clarté __/5 | citations justes __/5 | remarques :

## Mode RAG : prompt

### alert-4792264
Sections remplacées : ['4. Références réglementaires', '5. Recommandations'] | complet : False

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

Rapport d'aide à la décision, généré automatiquement : la décision finale relève de l'analyste conformité.

6. Éléments d'investigation (outils)
Voisinage :
- Transaction 14027 du 2022-09-01 00:01:00 : montant 78 326 856,95 US Dollar, sens entrante, format Reinvestment
- Transaction 650688 du 2022-09-01 10:10:00 : montant 10 341,88 US Dollar, sens entrante, format Reinvestment
- Transaction 1028265 du 2022-09-01 21:25:00 : montant 5,60 US Dollar, sens entrante, format Reinvestment
- Transaction 2649157 du 2022-09-05 17:56:00 : montant 19 504,66 US Dollar, sens sortante, format ACH
Statistiques du voisinage (calculées sur les transactions voisines, pas sur l'historique complet) :
- 4 transactions voisines (3 entrante(s), 1 sortante(s)) ; montant total 78 356 709,09 ; montant moyen 19 589 177,27 ; 1 contrepartie(s) distincte(s)
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du voisinage
- Rédaction par le LLM-LoRA ; sections remplacées car incohérentes avec les règles : Références réglementaires, Recommandations
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### alert-5078133
Sections remplacées : ['4. Références réglementaires', '5. Recommandations'] | complet : False

```
RAPPORT D'AUDIT — Transaction 5078133

1. Résumé
La transaction 5078133 a été signalée par le détecteur avec un score brut de 0,996 et une confiance calibrée de 0,931 (niveau de risque critique, fiabilité du schéma élevée).
Transaction du 14/09/2022 à 08:07, d'un montant de 10 874,08 Euro, du compte 8051E3B20 (client 1412) vers le compte 806911FE0 (client 14663), format de paiement ACH.

2. Schéma détecté
Schéma : fan_out — dispersion de fonds : un compte redistribue rapidement des fonds vers de nombreux comptes, schéma compatible avec un fractionnement des montants.
Voisinage : 10 transactions voisines dans le graphe (1683950, 4312934, 4316938, 4319179, 4320043, 5077973, 5077978, 5078048, 5078057, 5078132).

3. Facteurs explicatifs
- Le nombre de transactions antérieures entre ces deux mêmes comptes (pair_prev) : poids 0,282 — facteur principal, aggravant
- Le nombre de transactions entrantes passées du compte destinataire (dst_in_cnt_all) : poids 0,173 — atténuant
- Le format de paiement utilisé (payment_format) : poids 0,129 — aggravant
Ces facteurs décrivent les caractéristiques de la transaction ; le contexte réseau des comptes (comptes voisins) n'est pas détaillé.

4. Références réglementaires
- Recommandation 16 du GAFI (virements électroniques) : les informations sur le donneur d'ordre et le bénéficiaire doivent accompagner les virements afin de pouvoir retracer l'opération.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).
- Recommandation 21 du GAFI (divulgation et confidentialité) : il est interdit de révéler au client ou à un tiers qu'une déclaration de soupçon ou une information connexe est transmise à la CRF.
- Droit marocain (loi relative à la lutte contre le blanchiment de capitaux) : les personnes assujetties doivent déclarer à l'autorité compétente les opérations qu'elles soupçonnent d'être liées au blanchiment de capitaux ou au financement du terrorisme.

5. Recommandations
- Escalade immédiate au responsable conformité.
- Revue manuelle prioritaire de la transaction et des transactions voisines.
- Préparation d'une déclaration de soupçon si les éléments sont confirmés.
- Identifier les bénéficiaires des dispersions et vérifier leur justification économique.
- Ne pas informer le client de l'existence de cette alerte (interdiction de divulgation).

Ce rapport est généré automatiquement pour assister l'analyste ; la décision finale de déclaration lui appartient.

6. Éléments d'investigation (outils)
Voisinage :
- Transaction 1683950 du 2022-09-02 17:57:00 : montant 9 801,33 Euro, sens sortante, format Cash
- Transaction 4312934 du 2022-09-09 03:08:00 : montant 121,20 Euro, sens sortante, format ACH
- Transaction 4316938 du 2022-09-09 03:17:00 : montant 9 801,33 Euro, sens sortante, format Cash
- Transaction 4319179 du 2022-09-09 03:22:00 : montant 2 036,24 Euro, sens sortante, format Cheque
- Transaction 4320043 du 2022-09-09 03:24:00 : montant 2 102,23 Euro, sens sortante, format Credit Card
- Transaction 5077973 du 2022-09-13 09:15:00 : montant 59 622,07 Yuan, sens sortante, format ACH
- Transaction 5077978 du 2022-09-13 10:06:00 : montant 10 394,61 US Dollar, sens entrante, format ACH
- Transaction 5078048 du 2022-09-13 15:03:00 : montant 14 195,02 US Dollar, sens entrante, format ACH
- Transaction 5078057 du 2022-09-13 15:33:00 : montant 4 035,86 US Dollar, sens entrante, format ACH
- Transaction 5078132 du 2022-09-14 08:07:00 : montant 12 742,06 US Dollar, sens entrante, format ACH
Statistiques du voisinage (calculées sur les transactions voisines, pas sur l'historique complet) :
- 10 transactions voisines (4 entrante(s), 6 sortante(s)) ; montant total 124 851,95 ; montant moyen 12 485,19 ; 5 contrepartie(s) distincte(s)
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du voisinage
- Rédaction par le LLM-LoRA ; sections remplacées car incohérentes avec les règles : Références réglementaires, Recommandations
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### alert-5077842
Sections remplacées : ['4. Références réglementaires', '5. Recommandations'] | complet : False

```
RAPPORT D'AUDIT — Transaction 5077842

1. Résumé
La transaction 5077842 a été signalée par le détecteur avec un score brut de 0,932 et une confiance calibrée de 0,527 (niveau de risque modéré à élevé, fiabilité du schéma élevée).
Transaction du 12/09/2022 à 16:27, d'un montant de 14 464,64 US Dollar, du compte 809768440 (banque 5175) vers le compte 8041A3440 (banque 29404), format de paiement ACH.

2. Schéma détecté
Schéma : fan_in — concentration de fonds : de nombreux comptes versent vers un même compte, schéma compatible avec un compte « mule » collecteur.
Voisinage : 10 transactions voisines dans le graphe (3446133, 4135761, 4546558, 4964261, 5029849, 5077581, 5077610, 5077732, 5077827, 5077841).

3. Facteurs explicatifs
- Le nombre de transactions antérieures entre ces deux mêmes comptes (pair_prev) : poids 0,419 — facteur principal, aggravant
- Le format de paiement utilisé (payment_format) : poids 0,167 — aggravant
- Le nombre de transactions entrantes passées du compte destinataire (dst_in_cnt_all) : poids 0,110 — atténuant
Ces facteurs décrivent les caractéristiques de la transaction ; le contexte réseau des comptes (comptes voisins) n'est pas détaillé.

4. Références réglementaires
- Recommandation 10 du GAFI (vigilance à l'égard de la clientèle) : les institutions financières exercent une vigilance constante sur la relation d'affaires et examinent les transactions pour s'assurer qu'elles sont cohérentes avec leur connaissance du client.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).

5. Recommandations
- Revue manuelle dans le cadre du traitement normal des alertes.
- Vérification de la cohérence avec le profil du client.
- Pas de déclaration à ce stade sans élément complémentaire.
- Identifier les comptes émetteurs et vérifier si le compte collecteur est un compte mule.

Rapport d'aide à la décision, généré automatiquement : la décision finale relève de l'analyste conformité.

6. Éléments d'investigation (outils)
Voisinage :
- Transaction 3446133 du 2022-09-07 09:21:00 : montant 11 481,53 Euro, sens sortante, format Cheque
- Transaction 4135761 du 2022-09-08 19:56:00 : montant 11 481,53 Euro, sens sortante, format Cheque
- Transaction 4546558 du 2022-09-09 11:53:00 : montant 11 481,53 Euro, sens sortante, format Cheque
- Transaction 4964261 du 2022-09-10 09:52:00 : montant 11 481,53 Euro, sens sortante, format Cheque
- Transaction 5029849 du 2022-09-10 18:05:00 : montant 6 776,27 US Dollar, sens entrante, format ACH
- Transaction 5077581 du 2022-09-11 18:55:00 : montant 16 408,23 US Dollar, sens entrante, format ACH
- Transaction 5077610 du 2022-09-11 20:33:00 : montant 790,89 US Dollar, sens entrante, format ACH
- Transaction 5077732 du 2022-09-12 10:23:00 : montant 6 090,71 US Dollar, sens entrante, format ACH
- Transaction 5077827 du 2022-09-12 15:55:00 : montant 19 766,30 US Dollar, sens entrante, format ACH
- Transaction 5077841 du 2022-09-12 16:27:00 : montant 12 344,12 Euro, sens entrante, format ACH
Statistiques du voisinage (calculées sur les transactions voisines, pas sur l'historique complet) :
- 10 transactions voisines (6 entrante(s), 4 sortante(s)) ; montant total 108 102,64 ; montant moyen 10 810,26 ; 6 contrepartie(s) distincte(s)
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du voisinage
- Rédaction par le LLM-LoRA ; sections remplacées car incohérentes avec les règles : Références réglementaires, Recommandations
```

Grille : clarté __/5 | citations justes __/5 | remarques :

## Mode RAG : annex

### alert-4792264
Sections remplacées : [] | complet : False

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

6. Éléments d'investigation (outils)
Voisinage :
- Transaction 14027 du 2022-09-01 00:01:00 : montant 78 326 856,95 US Dollar, sens entrante, format Reinvestment
- Transaction 650688 du 2022-09-01 10:10:00 : montant 10 341,88 US Dollar, sens entrante, format Reinvestment
- Transaction 1028265 du 2022-09-01 21:25:00 : montant 5,60 US Dollar, sens entrante, format Reinvestment
- Transaction 2649157 du 2022-09-05 17:56:00 : montant 19 504,66 US Dollar, sens sortante, format ACH
Statistiques du voisinage (calculées sur les transactions voisines, pas sur l'historique complet) :
- 4 transactions voisines (3 entrante(s), 1 sortante(s)) ; montant total 78 356 709,09 ; montant moyen 19 589 177,27 ; 1 contrepartie(s) distincte(s)
Extraits réglementaires consultés (texte copié de l'index, non reformulé) :
- [1] Lutte-contre-le-blanchiment-de-capitaux.pdf, p.11-12 : 1 : Obligations de vigilance Article 39 Les personnes assujetties sont tenues de mettre en place des politiques et des règles de contrôle interne, des mesures de vigilance et de détection ainsi que des procédures de lutte contre le blanchiment de capitaux et le financement du terrorisme selon une approche basée sur les risques, adaptées à la nature et à […]
- [2] Guide-LBC-FT-FR-03_25.pdf, p.18-18 : inhabituelles ou suspectes qui pourraient éventuellement constituer du blanchiment de capitaux ou du financement du terrorisme. La réglementation oblige les établissements de crédit à avoir une connaissance approfondie de leurs clients ; Ainsi, ils doivent mettre en place un dispositif de vigilance et de veille interne. • Doter le dispositif de vigilance et de veille interne de ressources et moyens […]
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du voisinage, recherche réglementaire
- Rédaction par le LLM-LoRA ; toutes les déductions vérifiées conformes.
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### alert-5078133
Sections remplacées : [] | complet : False

```
RAPPORT D'AUDIT — Transaction 5078133

1. Résumé
La transaction 5078133 a été signalée par le détecteur avec un score brut de 0,996 et une confiance calibrée de 0,931 (niveau de risque critique, fiabilité du schéma élevée).
Transaction du 14/09/2022 à 08:07, d'un montant de 10 874,08 Euro, du compte 8051E3B20 (banque 1412) vers le compte 806911FE0 (banque 14663), format de paiement ACH.

2. Schéma détecté
Schéma : fan_out — dispersion de fonds : un compte redistribue rapidement des fonds vers de nombreux comptes, schéma compatible avec un fractionnement des montants.
Voisinage : 10 transactions voisines dans le graphe (1683950, 4312934, 4316938, 4319179, 4320043, 5077973, 5077978, 5078048, 5078057, 5078132).

3. Facteurs explicatifs
- Le nombre de transactions antérieures entre ces deux mêmes comptes (pair_prev) : poids 0,282 — facteur principal, aggravant
- Le nombre de transactions entrantes passées du compte destinataire (dst_in_cnt_all) : poids 0,173 — atténuant
- Le format de paiement utilisé (payment_format) : poids 0,129 — aggravant
Ces facteurs décrivent les caractéristiques de la transaction ; le contexte réseau des comptes (comptes voisins) n'est pas détaillé.

4. Références réglementaires
- Recommandation 16 du GAFI (virements électroniques) : les informations sur le donneur d'ordre et le bénéficiaire doivent accompagner les virements afin de pouvoir retracer l'opération.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).
- Recommandation 21 du GAFI (divulgation et confidentialité) : il est interdit de révéler au client ou à un tiers qu'une déclaration de soupçon ou une information connexe est transmise à la CRF.
- Droit marocain (loi relative à la lutte contre le blanchiment de capitaux) : les personnes assujetties doivent déclarer à l'autorité compétente les opérations qu'elles soupçonnent d'être liées au blanchiment de capitaux ou au financement du terrorisme.

5. Recommandations
- Escalade immédiate au responsable conformité.
- Revue manuelle prioritaire de la transaction et des transactions voisines.
- Préparation d'une déclaration de soupçon si les éléments sont confirmés.
- Identifier les bénéficiaires des dispersions et vérifier leur justification économique.
- Ne pas informer le client de l'existence de cette alerte (interdiction de divulgation).

Rapport d'aide à la décision, généré automatiquement : la décision finale relève de l'analyste conformité.

6. Éléments d'investigation (outils)
Voisinage :
- Transaction 1683950 du 2022-09-02 17:57:00 : montant 9 801,33 Euro, sens sortante, format Cash
- Transaction 4312934 du 2022-09-09 03:08:00 : montant 121,20 Euro, sens sortante, format ACH
- Transaction 4316938 du 2022-09-09 03:17:00 : montant 9 801,33 Euro, sens sortante, format Cash
- Transaction 4319179 du 2022-09-09 03:22:00 : montant 2 036,24 Euro, sens sortante, format Cheque
- Transaction 4320043 du 2022-09-09 03:24:00 : montant 2 102,23 Euro, sens sortante, format Credit Card
- Transaction 5077973 du 2022-09-13 09:15:00 : montant 59 622,07 Yuan, sens sortante, format ACH
- Transaction 5077978 du 2022-09-13 10:06:00 : montant 10 394,61 US Dollar, sens entrante, format ACH
- Transaction 5078048 du 2022-09-13 15:03:00 : montant 14 195,02 US Dollar, sens entrante, format ACH
- Transaction 5078057 du 2022-09-13 15:33:00 : montant 4 035,86 US Dollar, sens entrante, format ACH
- Transaction 5078132 du 2022-09-14 08:07:00 : montant 12 742,06 US Dollar, sens entrante, format ACH
Statistiques du voisinage (calculées sur les transactions voisines, pas sur l'historique complet) :
- 10 transactions voisines (4 entrante(s), 6 sortante(s)) ; montant total 124 851,95 ; montant moyen 12 485,19 ; 5 contrepartie(s) distincte(s)
Extraits réglementaires consultés (texte copié de l'index, non reformulé) :
- [1] Lutte-contre-le-blanchiment-de-capitaux.pdf, p.14-15 : des opérations relatives aux activités suivantes : -L’achat ou la vente de biens immobiliers, d’actifs commerciaux ou de l’un de leurs éléments ; -La gestion de fonds, de titres, de comptes bancaires, de dépôt ou d’autres actifs appartenant au client ; -L’organisation et l’évaluation des parts nécessaires à la constitution des capitaux des sociétés ou à leur gestion ou exploitation […]
- [2] Guide-LBC-FT-FR-03_25.pdf, p.18-18 : inhabituelles ou suspectes qui pourraient éventuellement constituer du blanchiment de capitaux ou du financement du terrorisme. La réglementation oblige les établissements de crédit à avoir une connaissance approfondie de leurs clients ; Ainsi, ils doivent mettre en place un dispositif de vigilance et de veille interne. • Doter le dispositif de vigilance et de veille interne de ressources et moyens […]
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du voisinage, recherche réglementaire
- Rédaction par le LLM-LoRA ; toutes les déductions vérifiées conformes.
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### alert-5077842
Sections remplacées : [] | complet : False

```
RAPPORT D'AUDIT — Transaction 5077842

1. Résumé
La transaction 5077842 a été signalée par le détecteur avec un score brut de 0,932 et une confiance calibrée de 0,527 (niveau de risque modéré à élevé, fiabilité du schéma élevée).
Transaction du 12/09/2022 à 16:27, d'un montant de 14 464,64 US Dollar, du compte 809768440 (banque 5175) vers le compte 8041A3440 (banque 29404), format de paiement ACH.

2. Schéma détecté
Schéma : fan_in — concentration de fonds : de nombreux comptes versent vers un même compte, schéma compatible avec un compte « mule » collecteur.
Voisinage : 10 transactions voisines dans le graphe (3446133, 4135761, 4546558, 4964261, 5029849, 5077581, 5077610, 5077732, 5077827, 5077841).

3. Facteurs explicatifs
- Le nombre de transactions antérieures entre ces deux mêmes comptes (pair_prev) : poids 0,419 — facteur principal, aggravant
- Le format de paiement utilisé (payment_format) : poids 0,167 — aggravant
- Le nombre de transactions entrantes passées du compte destinataire (dst_in_cnt_all) : poids 0,110 — atténuant
Ces facteurs décrivent les caractéristiques de la transaction ; le contexte réseau des comptes (comptes voisins) n'est pas détaillé.

4. Références réglementaires
- Recommandation 10 du GAFI (vigilance à l'égard de la clientèle) : les institutions financières exercent une vigilance constante sur la relation d'affaires et examinent les transactions pour s'assurer qu'elles sont cohérentes avec leur connaissance du client.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).
- Droit marocain (loi relative à la lutte contre le blanchiment de capitaux) : les personnes assujetties doivent déclarer à l'autorité compétente les opérations qu'elles soupçonnent d'être liées au blanchiment de capitaux ou au financement du terrorisme.

5. Recommandations
- Revue manuelle dans le cadre du traitement normal des alertes.
- Vérification de la cohérence avec le profil du client.
- Pas de déclaration à ce stade sans élément complémentaire.
- Identifier les comptes émetteurs et vérifier si le compte collecteur est un compte mule.

Rapport d'aide à la décision, généré automatiquement : la décision finale relève de l'analyste conformité.

6. Éléments d'investigation (outils)
Voisinage :
- Transaction 3446133 du 2022-09-07 09:21:00 : montant 11 481,53 Euro, sens sortante, format Cheque
- Transaction 4135761 du 2022-09-08 19:56:00 : montant 11 481,53 Euro, sens sortante, format Cheque
- Transaction 4546558 du 2022-09-09 11:53:00 : montant 11 481,53 Euro, sens sortante, format Cheque
- Transaction 4964261 du 2022-09-10 09:52:00 : montant 11 481,53 Euro, sens sortante, format Cheque
- Transaction 5029849 du 2022-09-10 18:05:00 : montant 6 776,27 US Dollar, sens entrante, format ACH
- Transaction 5077581 du 2022-09-11 18:55:00 : montant 16 408,23 US Dollar, sens entrante, format ACH
- Transaction 5077610 du 2022-09-11 20:33:00 : montant 790,89 US Dollar, sens entrante, format ACH
- Transaction 5077732 du 2022-09-12 10:23:00 : montant 6 090,71 US Dollar, sens entrante, format ACH
- Transaction 5077827 du 2022-09-12 15:55:00 : montant 19 766,30 US Dollar, sens entrante, format ACH
- Transaction 5077841 du 2022-09-12 16:27:00 : montant 12 344,12 Euro, sens entrante, format ACH
Statistiques du voisinage (calculées sur les transactions voisines, pas sur l'historique complet) :
- 10 transactions voisines (6 entrante(s), 4 sortante(s)) ; montant total 108 102,64 ; montant moyen 10 810,26 ; 6 contrepartie(s) distincte(s)
Extraits réglementaires consultés (texte copié de l'index, non reformulé) :
- [1] Lutte-contre-le-blanchiment-de-capitaux.pdf, p.11-12 : 1 : Obligations de vigilance Article 39 Les personnes assujetties sont tenues de mettre en place des politiques et des règles de contrôle interne, des mesures de vigilance et de détection ainsi que des procédures de lutte contre le blanchiment de capitaux et le financement du terrorisme selon une approche basée sur les risques, adaptées à la nature et à […]
- [2] Guide-LBC-FT-FR-03_25.pdf, p.18-18 : inhabituelles ou suspectes qui pourraient éventuellement constituer du blanchiment de capitaux ou du financement du terrorisme. La réglementation oblige les établissements de crédit à avoir une connaissance approfondie de leurs clients ; Ainsi, ils doivent mettre en place un dispositif de vigilance et de veille interne. • Doter le dispositif de vigilance et de veille interne de ressources et moyens […]
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du voisinage, recherche réglementaire
- Rédaction par le LLM-LoRA ; toutes les déductions vérifiées conformes.
```

Grille : clarté __/5 | citations justes __/5 | remarques :
