# Échantillon B6 pour relecture manuelle

## Mode RAG : off

### alert-60470
Sections remplacées : ['1. Résumé', '4. Références réglementaires', '5. Recommandations'] | complet : False

```
RAPPORT D'AUDIT — Transaction 60470

1. Résumé
La transaction 60470 a été signalée par le détecteur avec un score de risque de 0,80 (niveau élevé) et un indice de confiance de 0,68 (fiabilité moyenne). La confiance est nettement inférieure au score : l'alerte doit être confirmée par un analyste avant toute décision.

2. Schéma détecté
Schéma : fan-in — concentration de fonds : de nombreux comptes versent vers un même compte, schéma compatible avec un compte « mule » collecteur.
Voisinage : 4 transactions voisines dans le graphe (16704, 51026, 66598, 90220).

3. Facteurs explicatifs
- Le nombre de comptes qui versent vers ce compte (in_degree) : poids 0,32 — facteur principal
- Le montant de la transaction (amount) : poids 0,32
- Le nombre de virements entrants le même jour (same_day_inflows) : poids 0,16

4. Références réglementaires
- Recommandation 10 du GAFI (vigilance à l'égard de la clientèle) : les institutions financières exercent une vigilance constante sur la relation d'affaires et examinent les transactions pour s'assurer qu'elles sont cohérentes avec leur connaissance du client.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).

5. Recommandations
- Revue manuelle prioritaire de la transaction et de son voisinage.
- Vérification de la cohérence avec le profil et l'historique du client.
- Déclaration de soupçon à envisager si l'analyse confirme le doute.
- Identifier les comptes émetteurs et vérifier si le compte collecteur est un compte mule.

Rapport d'aide à la décision, généré automatiquement : la décision finale relève de l'analyste conformité.

6. Éléments d'investigation (outils)
Voisinage [données simulées] :
- Transaction 16704 : montant 75 671,03, sens entrante, même schéma que l'alerte : oui
- Transaction 51026 : montant 9 688,94, sens sortante, même schéma que l'alerte : non
- Transaction 66598 : montant 8 282,75, sens sortante, même schéma que l'alerte : non
- Transaction 90220 : montant 57 783,85, sens sortante, même schéma que l'alerte : non
Statistiques du compte [données simulées] :
- Ancienneté 1751 jours ; 63 transactions sur 30 jours ; volume 946 645,12 ; montant moyen 15 026,11 ; 7 contreparties distinctes
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du compte
- Rédaction par le LLM-LoRA ; sections remplacées car incohérentes avec les règles : Résumé, Références réglementaires, Recommandations
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### alert-10508
Sections remplacées : ['1. Résumé', '5. Recommandations'] | complet : False

```
RAPPORT D'AUDIT — Transaction 10508

1. Résumé
Le modèle de détection a levé une alerte sur la transaction 10508 : score de risque 0,97, niveau critique, confiance 0,89 (fiabilité élevée).

2. Schéma détecté
Schéma : cycle — circuit fermé de fonds : l'argent revient vers son point de départ après plusieurs transferts, schéma typique de l'empilement (layering).
Voisinage : 3 transactions voisines dans le graphe (50454, 63289, 95376).

3. Facteurs explicatifs
- Le délai entre les mouvements successifs (time_gap_hours) : poids 0,51 — facteur principal
- La longueur du circuit de fonds (cycle_length) : poids 0,23

4. Références réglementaires
- Recommandation 10 du GAFI (vigilance à l'égard de la clientèle) : les institutions financières exercent une vigilance constante sur la relation d'affaires et examinent les transactions pour s'assurer qu'elles sont cohérentes avec leur connaissance du client.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).
- Recommandation 21 du GAFI (divulgation et confidentialité) : il est interdit de révéler au client ou à un tiers qu'une déclaration de soupçon ou une information connexe est transmise à la CRF.
- Droit marocain (loi relative à la lutte contre le blanchiment de capitaux) : les personnes assujetties doivent déclarer à l'autorité compétente les opérations qu'elles soupçonnent d'être liées au blanchiment de capitaux ou au financement du terrorisme.

5. Recommandations
- Escalade immédiate au responsable conformité.
- Revue manuelle prioritaire de la transaction et des transactions voisines.
- Préparation d'une déclaration de soupçon si les éléments sont confirmés.
- Reconstituer le circuit complet des fonds et identifier les comptes impliqués.
- Ne pas informer le client de l'existence de cette alerte (interdiction de divulgation).

Rapport d'aide à la décision, généré automatiquement : la décision finale relève de l'analyste conformité.

6. Éléments d'investigation (outils)
Voisinage [données simulées] :
- Transaction 50454 : montant 47 555,42, sens sortante, même schéma que l'alerte : non
- Transaction 63289 : montant 29 992,30, sens sortante, même schéma que l'alerte : oui
- Transaction 95376 : montant 89 254,16, sens entrante, même schéma que l'alerte : oui
Statistiques du compte [données simulées] :
- Ancienneté 2990 jours ; 119 transactions sur 30 jours ; volume 700 480,44 ; montant moyen 5 886,39 ; 11 contreparties distinctes
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du compte
- Rédaction par le LLM-LoRA ; sections remplacées car incohérentes avec les règles : Résumé, Recommandations
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### alert-53581
Sections remplacées : ['4. Références réglementaires', '5. Recommandations'] | complet : False

```
RAPPORT D'AUDIT — Transaction 53581

1. Résumé
Le modèle de détection a levé une alerte sur la transaction 53581 : score de risque 0,91, niveau critique, confiance 0,93 (fiabilité élevée).

2. Schéma détecté
Schéma : fan-out — dispersion de fonds : un compte redistribue rapidement des fonds vers de nombreux comptes, schéma compatible avec un fractionnement des montants.
Voisinage : 5 transactions voisines dans le graphe (12442, 14399, 18367, 25561, 36358).

3. Facteurs explicatifs
- Le nombre de comptes vers lesquels ce compte verse (out_degree) : poids 0,36 — facteur principal
- Le nombre de virements sortants le même jour (same_day_outflows) : poids 0,17
- L'écart entre la devise payée et la devise reçue (currency_mismatch) : poids 0,16

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
Voisinage [données simulées] :
- Transaction 12442 : montant 45 011,00, sens sortante, même schéma que l'alerte : oui
- Transaction 14399 : montant 50 532,83, sens entrante, même schéma que l'alerte : oui
- Transaction 18367 : montant 59 139,97, sens entrante, même schéma que l'alerte : non
- Transaction 25561 : montant 78 068,87, sens sortante, même schéma que l'alerte : oui
- Transaction 36358 : montant 60 158,36, sens entrante, même schéma que l'alerte : non
Statistiques du compte [données simulées] :
- Ancienneté 1816 jours ; 70 transactions sur 30 jours ; volume 784 976,97 ; montant moyen 11 213,96 ; 32 contreparties distinctes
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du compte
- Rédaction par le LLM-LoRA ; sections remplacées car incohérentes avec les règles : Références réglementaires, Recommandations
```

Grille : clarté __/5 | citations justes __/5 | remarques :

## Mode RAG : prompt

### alert-60470
Sections remplacées : ['1. Résumé', '4. Références réglementaires', '5. Recommandations'] | complet : False

```
RAPPORT D'AUDIT — Transaction 60470

1. Résumé
La transaction 60470 a été signalée par le détecteur avec un score de risque de 0,80 (niveau élevé) et un indice de confiance de 0,68 (fiabilité moyenne). La confiance est nettement inférieure au score : l'alerte doit être confirmée par un analyste avant toute décision.

2. Schéma détecté
Schéma : fan-in — concentration de fonds : de nombreux comptes versent vers un même compte, schéma compatible avec un compte « mule » collecteur.
Voisinage : 4 transactions voisines dans le graphe (16704, 51026, 66598, 90220).

3. Facteurs explicatifs
- Le nombre de comptes qui versent vers ce compte (in_degree) : poids 0,32 — facteur principal
- Le montant de la transaction (amount) : poids 0,32
- Le nombre de virements entrants le même jour (same_day_inflows) : poids 0,16

4. Références réglementaires
- Recommandation 10 du GAFI (vigilance à l'égard de la clientèle) : les institutions financières exercent une vigilance constante sur la relation d'affaires et examinent les transactions pour s'assurer qu'elles sont cohérentes avec leur connaissance du client.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).

5. Recommandations
- Revue manuelle prioritaire de la transaction et de son voisinage.
- Vérification de la cohérence avec le profil et l'historique du client.
- Déclaration de soupçon à envisager si l'analyse confirme le doute.
- Identifier les comptes émetteurs et vérifier si le compte collecteur est un compte mule.

Rapport d'aide à la décision, généré automatiquement : la décision finale relève de l'analyste conformité.

6. Éléments d'investigation (outils)
Voisinage [données simulées] :
- Transaction 16704 : montant 75 671,03, sens entrante, même schéma que l'alerte : oui
- Transaction 51026 : montant 9 688,94, sens sortante, même schéma que l'alerte : non
- Transaction 66598 : montant 8 282,75, sens sortante, même schéma que l'alerte : non
- Transaction 90220 : montant 57 783,85, sens sortante, même schéma que l'alerte : non
Statistiques du compte [données simulées] :
- Ancienneté 1751 jours ; 63 transactions sur 30 jours ; volume 946 645,12 ; montant moyen 15 026,11 ; 7 contreparties distinctes
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du compte
- Rédaction par le LLM-LoRA ; sections remplacées car incohérentes avec les règles : Résumé, Références réglementaires, Recommandations
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### alert-10508
Sections remplacées : ['1. Résumé', '4. Références réglementaires', '5. Recommandations'] | complet : False

```
RAPPORT D'AUDIT — Transaction 10508

1. Résumé
Le modèle de détection a levé une alerte sur la transaction 10508 : score de risque 0,97, niveau critique, confiance 0,89 (fiabilité élevée).

2. Schéma détecté
Schéma : cycle — circuit fermé de fonds : l'argent revient vers son point de départ après plusieurs transferts, schéma typique de l'empilement (layering).
Voisinage : 3 transactions voisines dans le graphe (50454, 63289, 95376).

3. Facteurs explicatifs
- Le délai entre les mouvements successifs (time_gap_hours) : poids 0,51 — facteur principal
- La longueur du circuit de fonds (cycle_length) : poids 0,23

4. Références réglementaires
- Recommandation 10 du GAFI (vigilance à l'égard de la clientèle) : les institutions financières exercent une vigilance constante sur la relation d'affaires et examinent les transactions pour s'assurer qu'elles sont cohérentes avec leur connaissance du client.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).
- Recommandation 21 du GAFI (divulgation et confidentialité) : il est interdit de révéler au client ou à un tiers qu'une déclaration de soupçon ou une information connexe est transmise à la CRF.

5. Recommandations
- Escalade immédiate au responsable conformité.
- Revue manuelle prioritaire de la transaction et des transactions voisines.
- Préparation d'une déclaration de soupçon si les éléments sont confirmés.
- Reconstituer le circuit complet des fonds et identifier les comptes impliqués.
- Ne pas informer le client de l'existence de cette alerte (interdiction de divulgation).

Rapport d'aide à la décision, généré automatiquement : la décision finale relève de l'analyste conformité.

6. Éléments d'investigation (outils)
Voisinage [données simulées] :
- Transaction 50454 : montant 47 555,42, sens sortante, même schéma que l'alerte : non
- Transaction 63289 : montant 29 992,30, sens sortante, même schéma que l'alerte : oui
- Transaction 95376 : montant 89 254,16, sens entrante, même schéma que l'alerte : oui
Statistiques du compte [données simulées] :
- Ancienneté 2990 jours ; 119 transactions sur 30 jours ; volume 700 480,44 ; montant moyen 5 886,39 ; 11 contreparties distinctes
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du compte
- Rédaction par le LLM-LoRA ; sections remplacées car incohérentes avec les règles : Résumé, Références réglementaires, Recommandations
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### alert-53581
Sections remplacées : ['1. Résumé', '3. Facteurs explicatifs', '4. Références réglementaires', '5. Recommandations'] | complet : False

```
RAPPORT D'AUDIT — Transaction 53581

1. Résumé
Le modèle de détection a levé une alerte sur la transaction 53581 : score de risque 0,91, niveau critique, confiance 0,93 (fiabilité élevée).

2. Schéma détecté
Schéma : fan-out — dispersion de fonds : un compte redistribue rapidement des fonds vers de nombreux comptes, schéma compatible avec un fractionnement des montants.
Voisinage : 5 transactions voisines dans le graphe (12442, 14399, 18367, 25561, 36358).

3. Facteurs explicatifs
- Le nombre de comptes vers lesquels ce compte verse (out_degree) : poids 0,36 — facteur principal
- Le nombre de virements sortants le même jour (same_day_outflows) : poids 0,17
- L'écart entre la devise payée et la devise reçue (currency_mismatch) : poids 0,16

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
Voisinage [données simulées] :
- Transaction 12442 : montant 45 011,00, sens sortante, même schéma que l'alerte : oui
- Transaction 14399 : montant 50 532,83, sens entrante, même schéma que l'alerte : oui
- Transaction 18367 : montant 59 139,97, sens entrante, même schéma que l'alerte : non
- Transaction 25561 : montant 78 068,87, sens sortante, même schéma que l'alerte : oui
- Transaction 36358 : montant 60 158,36, sens entrante, même schéma que l'alerte : non
Statistiques du compte [données simulées] :
- Ancienneté 1816 jours ; 70 transactions sur 30 jours ; volume 784 976,97 ; montant moyen 11 213,96 ; 32 contreparties distinctes
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du compte
- Rédaction par le LLM-LoRA ; sections remplacées car incohérentes avec les règles : Résumé, Facteurs explicatifs, Références réglementaires, Recommandations
```

Grille : clarté __/5 | citations justes __/5 | remarques :

## Mode RAG : annex

### alert-60470
Sections remplacées : ['1. Résumé', '4. Références réglementaires', '5. Recommandations'] | complet : False

```
RAPPORT D'AUDIT — Transaction 60470

1. Résumé
La transaction 60470 a été signalée par le détecteur avec un score de risque de 0,80 (niveau élevé) et un indice de confiance de 0,68 (fiabilité moyenne). La confiance est nettement inférieure au score : l'alerte doit être confirmée par un analyste avant toute décision.

2. Schéma détecté
Schéma : fan-in — concentration de fonds : de nombreux comptes versent vers un même compte, schéma compatible avec un compte « mule » collecteur.
Voisinage : 4 transactions voisines dans le graphe (16704, 51026, 66598, 90220).

3. Facteurs explicatifs
- Le nombre de comptes qui versent vers ce compte (in_degree) : poids 0,32 — facteur principal
- Le montant de la transaction (amount) : poids 0,32
- Le nombre de virements entrants le même jour (same_day_inflows) : poids 0,16

4. Références réglementaires
- Recommandation 10 du GAFI (vigilance à l'égard de la clientèle) : les institutions financières exercent une vigilance constante sur la relation d'affaires et examinent les transactions pour s'assurer qu'elles sont cohérentes avec leur connaissance du client.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).

5. Recommandations
- Revue manuelle prioritaire de la transaction et de son voisinage.
- Vérification de la cohérence avec le profil et l'historique du client.
- Déclaration de soupçon à envisager si l'analyse confirme le doute.
- Identifier les comptes émetteurs et vérifier si le compte collecteur est un compte mule.

Rapport d'aide à la décision, généré automatiquement : la décision finale relève de l'analyste conformité.

6. Éléments d'investigation (outils)
Voisinage [données simulées] :
- Transaction 16704 : montant 75 671,03, sens entrante, même schéma que l'alerte : oui
- Transaction 51026 : montant 9 688,94, sens sortante, même schéma que l'alerte : non
- Transaction 66598 : montant 8 282,75, sens sortante, même schéma que l'alerte : non
- Transaction 90220 : montant 57 783,85, sens sortante, même schéma que l'alerte : non
Statistiques du compte [données simulées] :
- Ancienneté 1751 jours ; 63 transactions sur 30 jours ; volume 946 645,12 ; montant moyen 15 026,11 ; 7 contreparties distinctes
Extraits réglementaires consultés (texte copié de l'index, non reformulé) :
- [1] Lutte-contre-le-blanchiment-de-capitaux.pdf, p.11-12 : 1 : Obligations de vigilance Article 39 Les personnes assujetties sont tenues de mettre en place des politiques et des règles de contrôle interne, des mesures de vigilance et de détection ainsi que des procédures de lutte contre le blanchiment de capitaux et le financement du terrorisme selon une approche basée sur les risques, adaptées à la nature et à […]
- [2] Guide-LBC-FT-FR-03_25.pdf, p.18-18 : inhabituelles ou suspectes qui pourraient éventuellement constituer du blanchiment de capitaux ou du financement du terrorisme. La réglementation oblige les établissements de crédit à avoir une connaissance approfondie de leurs clients ; Ainsi, ils doivent mettre en place un dispositif de vigilance et de veille interne. • Doter le dispositif de vigilance et de veille interne de ressources et moyens […]
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du compte, recherche réglementaire
- Rédaction par le LLM-LoRA ; sections remplacées car incohérentes avec les règles : Résumé, Références réglementaires, Recommandations
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### alert-10508
Sections remplacées : ['1. Résumé', '5. Recommandations'] | complet : False

```
RAPPORT D'AUDIT — Transaction 10508

1. Résumé
Le modèle de détection a levé une alerte sur la transaction 10508 : score de risque 0,97, niveau critique, confiance 0,89 (fiabilité élevée).

2. Schéma détecté
Schéma : cycle — circuit fermé de fonds : l'argent revient vers son point de départ après plusieurs transferts, schéma typique de l'empilement (layering).
Voisinage : 3 transactions voisines dans le graphe (50454, 63289, 95376).

3. Facteurs explicatifs
- Le délai entre les mouvements successifs (time_gap_hours) : poids 0,51 — facteur principal
- La longueur du circuit de fonds (cycle_length) : poids 0,23

4. Références réglementaires
- Recommandation 10 du GAFI (vigilance à l'égard de la clientèle) : les institutions financières exercent une vigilance constante sur la relation d'affaires et examinent les transactions pour s'assurer qu'elles sont cohérentes avec leur connaissance du client.
- Recommandation 20 du GAFI (déclaration des opérations suspectes) : lorsqu'une institution financière soupçonne, ou a des motifs raisonnables de soupçonner, que des fonds proviennent d'une activité criminelle ou sont liés au financement du terrorisme, elle doit déclarer sans délai ses soupçons à la cellule de renseignement financier (CRF).
- Recommandation 21 du GAFI (divulgation et confidentialité) : il est interdit de révéler au client ou à un tiers qu'une déclaration de soupçon ou une information connexe est transmise à la CRF.
- Droit marocain (loi relative à la lutte contre le blanchiment de capitaux) : les personnes assujetties doivent déclarer à l'autorité compétente les opérations qu'elles soupçonnent d'être liées au blanchiment de capitaux ou au financement du terrorisme.

5. Recommandations
- Escalade immédiate au responsable conformité.
- Revue manuelle prioritaire de la transaction et des transactions voisines.
- Préparation d'une déclaration de soupçon si les éléments sont confirmés.
- Reconstituer le circuit complet des fonds et identifier les comptes impliqués.
- Ne pas informer le client de l'existence de cette alerte (interdiction de divulgation).

Rapport d'aide à la décision, généré automatiquement : la décision finale relève de l'analyste conformité.

6. Éléments d'investigation (outils)
Voisinage [données simulées] :
- Transaction 50454 : montant 47 555,42, sens sortante, même schéma que l'alerte : non
- Transaction 63289 : montant 29 992,30, sens sortante, même schéma que l'alerte : oui
- Transaction 95376 : montant 89 254,16, sens entrante, même schéma que l'alerte : oui
Statistiques du compte [données simulées] :
- Ancienneté 2990 jours ; 119 transactions sur 30 jours ; volume 700 480,44 ; montant moyen 5 886,39 ; 11 contreparties distinctes
Extraits réglementaires consultés (texte copié de l'index, non reformulé) :
- [1] Lutte-contre-le-blanchiment-de-capitaux.pdf, p.11-12 : 1 : Obligations de vigilance Article 39 Les personnes assujetties sont tenues de mettre en place des politiques et des règles de contrôle interne, des mesures de vigilance et de détection ainsi que des procédures de lutte contre le blanchiment de capitaux et le financement du terrorisme selon une approche basée sur les risques, adaptées à la nature et à […]
- [2] Guide-LBC-FT-FR-03_25.pdf, p.18-18 : inhabituelles ou suspectes qui pourraient éventuellement constituer du blanchiment de capitaux ou du financement du terrorisme. La réglementation oblige les établissements de crédit à avoir une connaissance approfondie de leurs clients ; Ainsi, ils doivent mettre en place un dispositif de vigilance et de veille interne. • Doter le dispositif de vigilance et de veille interne de ressources et moyens […]
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du compte, recherche réglementaire
- Rédaction par le LLM-LoRA ; sections remplacées car incohérentes avec les règles : Résumé, Recommandations
```

Grille : clarté __/5 | citations justes __/5 | remarques :

### alert-53581
Sections remplacées : ['4. Références réglementaires', '5. Recommandations'] | complet : False

```
RAPPORT D'AUDIT — Transaction 53581

1. Résumé
Le modèle de détection a levé une alerte sur la transaction 53581 : score de risque 0,91, niveau critique, confiance 0,93 (fiabilité élevée).

2. Schéma détecté
Schéma : fan-out — dispersion de fonds : un compte redistribue rapidement des fonds vers de nombreux comptes, schéma compatible avec un fractionnement des montants.
Voisinage : 5 transactions voisines dans le graphe (12442, 14399, 18367, 25561, 36358).

3. Facteurs explicatifs
- Le nombre de comptes vers lesquels ce compte verse (out_degree) : poids 0,36 — facteur principal
- Le nombre de virements sortants le même jour (same_day_outflows) : poids 0,17
- L'écart entre la devise payée et la devise reçue (currency_mismatch) : poids 0,16

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
Voisinage [données simulées] :
- Transaction 12442 : montant 45 011,00, sens sortante, même schéma que l'alerte : oui
- Transaction 14399 : montant 50 532,83, sens entrante, même schéma que l'alerte : oui
- Transaction 18367 : montant 59 139,97, sens entrante, même schéma que l'alerte : non
- Transaction 25561 : montant 78 068,87, sens sortante, même schéma que l'alerte : oui
- Transaction 36358 : montant 60 158,36, sens entrante, même schéma que l'alerte : non
Statistiques du compte [données simulées] :
- Ancienneté 1816 jours ; 70 transactions sur 30 jours ; volume 784 976,97 ; montant moyen 11 213,96 ; 32 contreparties distinctes
Extraits réglementaires consultés (texte copié de l'index, non reformulé) :
- [1] Lutte-contre-le-blanchiment-de-capitaux.pdf, p.14-15 : des opérations relatives aux activités suivantes : -L’achat ou la vente de biens immobiliers, d’actifs commerciaux ou de l’un de leurs éléments ; -La gestion de fonds, de titres, de comptes bancaires, de dépôt ou d’autres actifs appartenant au client ; -L’organisation et l’évaluation des parts nécessaires à la constitution des capitaux des sociétés ou à leur gestion ou exploitation […]
- [2] Guide-LBC-FT-FR-03_25.pdf, p.18-18 : inhabituelles ou suspectes qui pourraient éventuellement constituer du blanchiment de capitaux ou du financement du terrorisme. La réglementation oblige les établissements de crédit à avoir une connaissance approfondie de leurs clients ; Ainsi, ils doivent mettre en place un dispositif de vigilance et de veille interne. • Doter le dispositif de vigilance et de veille interne de ressources et moyens […]
Traçabilité :
- Outils appelés : voisinage, explication, statistiques du compte, recherche réglementaire
- Rédaction par le LLM-LoRA ; sections remplacées car incohérentes avec les règles : Références réglementaires, Recommandations
```

Grille : clarté __/5 | citations justes __/5 | remarques :
