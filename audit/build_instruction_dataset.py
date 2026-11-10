#!/usr/bin/env python3
"""B3 - Dataset d'instruction (alerte -> rapport d'audit) pour le LoRA.

Entrée  : audit/mock_alerts.json (B2) ; plus tard, les vraies alertes de A.
Sortie  : audit/instruction_data/{train,val,test}.jsonl (80/10/10, seed fixée).

DATASET SYNTHÉTIQUE : les rapports sont produits par des modèles de texte avec
variations (pas par un LLM), à partir d'alertes factices. À signaler dans le
README. Un rapport n'utilise QUE les informations de l'alerte (pas de montant,
de nom ou de date inventés) : cette règle est vérifiée automatiquement par
audit/report_checks.py.

Usage :
    python audit/build_instruction_dataset.py
    python audit/build_instruction_dataset.py --alerts audit/mock_alerts.json --seed 42
"""
import argparse
import json
import random
from collections import Counter
from pathlib import Path

try:
    from report_checks import check_report, fr
except ImportError:  # import depuis la racine du dépôt (notebooks Colab)
    from audit.report_checks import check_report, fr

HERE = Path(__file__).parent

INSTRUCTION = (
    "Tu es un analyste conformité LAB/FT. Rédige un rapport d'audit en français "
    "à partir de l'alerte suivante. N'utilise que les informations présentes "
    "dans l'alerte et n'invente aucune valeur."
)

# --- Vocabulaire ------------------------------------------------------------

FEATURE_LABELS = {
    "amount": "le montant de la transaction",
    "cross_bank": "le caractère inter-bancaire de la transaction",
    "cycle_length": "la longueur du circuit de fonds",
    "time_gap_hours": "le délai entre les mouvements successifs",
    "in_degree": "le nombre de comptes qui versent vers ce compte",
    "out_degree": "le nombre de comptes vers lesquels ce compte verse",
    "payment_format": "le format de paiement utilisé",
    "same_day_inflows": "le nombre de virements entrants le même jour",
    "same_day_outflows": "le nombre de virements sortants le même jour",
    "currency_mismatch": "l'écart entre la devise payée et la devise reçue",
    "hour_of_day": "l'heure de la transaction",
}

# NB : seul le pattern annoncé doit contenir son code (cycle, fan-in, fan-out) ;
# les autres textes n'emploient pas ces mots (contrôlé par report_checks).
PATTERN_DESC = {
    "cycle": (
        "circuit fermé de fonds : l'argent revient vers son point de départ "
        "après plusieurs transferts, schéma typique de l'empilement (layering)"
    ),
    "fan-in": (
        "concentration de fonds : de nombreux comptes versent vers un même "
        "compte, schéma compatible avec un compte « mule » collecteur"
    ),
    "fan-out": (
        "dispersion de fonds : un compte redistribue rapidement des fonds vers "
        "de nombreux comptes, schéma compatible avec un fractionnement des montants"
    ),
    "none": (
        "aucun schéma structurel connu (circuit fermé, concentration, dispersion) "
        "n'a été détecté dans le voisinage ; l'alerte repose sur les "
        "caractéristiques propres de la transaction"
    ),
}

INTROS = [
    "La transaction {tx} a été signalée par le détecteur avec un score de risque "
    "de {score} (niveau {risk}) et un indice de confiance de {conf} "
    "(fiabilité {clabel}).",
    "Le modèle de détection a levé une alerte sur la transaction {tx} : score "
    "de risque {score}, niveau {risk}, confiance {conf} (fiabilité {clabel}).",
    "Alerte sur la transaction {tx} : score {score}, niveau de risque {risk}, "
    "confiance {conf}, fiabilité {clabel}.",
]

LOW_CONF_NOTES = [
    "La confiance est nettement inférieure au score : l'alerte doit être "
    "confirmée par un analyste avant toute décision.",
    "L'écart entre le score et la confiance invite à la prudence : une "
    "validation humaine est nécessaire.",
]

# Références : formulations fidèles au corpus consulté en B1 (GAFI 2012, loi
# marocaine LAB/FT). Ce sont des synthèses : à faire relire (cf. B3 du cahier).
REFS = {
    "R10": (
        "Recommandation 10 du GAFI (vigilance à l'égard de la clientèle) : les "
        "institutions financières exercent une vigilance constante sur la "
        "relation d'affaires et examinent les transactions pour s'assurer "
        "qu'elles sont cohérentes avec leur connaissance du client."
    ),
    "R16": (
        "Recommandation 16 du GAFI (virements électroniques) : les informations "
        "sur le donneur d'ordre et le bénéficiaire doivent accompagner les "
        "virements afin de pouvoir retracer l'opération."
    ),
    "R20": (
        "Recommandation 20 du GAFI (déclaration des opérations suspectes) : "
        "lorsqu'une institution financière soupçonne, ou a des motifs "
        "raisonnables de soupçonner, que des fonds proviennent d'une activité "
        "criminelle ou sont liés au financement du terrorisme, elle doit "
        "déclarer sans délai ses soupçons à la cellule de renseignement "
        "financier (CRF)."
    ),
    "R21": (
        "Recommandation 21 du GAFI (divulgation et confidentialité) : il est "
        "interdit de révéler au client ou à un tiers qu'une déclaration de "
        "soupçon ou une information connexe est transmise à la CRF."
    ),
    "MA": (
        "Droit marocain (loi relative à la lutte contre le blanchiment de "
        "capitaux) : les personnes assujetties doivent déclarer à l'autorité "
        "compétente les opérations qu'elles soupçonnent d'être liées au "
        "blanchiment de capitaux ou au financement du terrorisme."
    ),
}
REF_ORDER = ["R10", "R16", "R20", "R21", "MA"]

ACTIONS_BY_RISK = {
    "critique": [
        "Escalade immédiate au responsable conformité.",
        "Revue manuelle prioritaire de la transaction et des transactions voisines.",
        "Préparation d'une déclaration de soupçon si les éléments sont confirmés.",
    ],
    "élevé": [
        "Revue manuelle prioritaire de la transaction et de son voisinage.",
        "Vérification de la cohérence avec le profil et l'historique du client.",
        "Déclaration de soupçon à envisager si l'analyse confirme le doute.",
    ],
    "modéré à élevé": [
        "Revue manuelle dans le cadre du traitement normal des alertes.",
        "Vérification de la cohérence avec le profil du client.",
        "Pas de déclaration à ce stade sans élément complémentaire.",
    ],
    "modéré": [
        "Surveillance renforcée du compte concerné.",
        "Revue manuelle si de nouvelles alertes apparaissent.",
        "Pas de déclaration à ce stade.",
    ],
}

PATTERN_ACTION = {
    "cycle": "Reconstituer le circuit complet des fonds et identifier les comptes impliqués.",
    "fan-in": "Identifier les comptes émetteurs et vérifier si le compte collecteur est un compte mule.",
    "fan-out": "Identifier les bénéficiaires des dispersions et vérifier leur justification économique.",
    "none": "Examiner l'historique du client pour confirmer ou écarter le caractère inhabituel.",
}

NO_TIPPING_OFF = (
    "Ne pas informer le client de l'existence de cette alerte (interdiction de divulgation)."
)

CLOSINGS = [
    "Ce rapport est généré automatiquement pour assister l'analyste ; la décision "
    "finale de déclaration lui appartient.",
    "Rapport d'aide à la décision, généré automatiquement : la décision finale "
    "relève de l'analyste conformité.",
]


# --- Niveaux ---------------------------------------------------------------

def risk_level(score: float) -> str:
    if score >= 0.90:
        return "critique"
    if score >= 0.80:
        return "élevé"
    if score >= 0.65:
        return "modéré à élevé"
    return "modéré"


def confidence_label(conf: float) -> str:
    if conf >= 0.80:
        return "élevée"
    if conf >= 0.65:
        return "moyenne"
    return "limitée"


def pick_references(alert: dict, rng: random.Random) -> list:
    keys = ["R16" if alert["pattern"] == "fan-out" else "R10", "R20"]
    if alert["score"] >= 0.85:
        keys.append("R21")
    if rng.random() < 0.7:
        keys.append("MA")
    return sorted(keys, key=REF_ORDER.index)


# --- Rapport ---------------------------------------------------------------

def build_report(alert: dict, rng: random.Random) -> str:
    score, conf, pattern = alert["score"], alert["confidence"], alert["pattern"]
    risk, clabel = risk_level(score), confidence_label(conf)

    intro = rng.choice(INTROS).format(
        tx=alert["tx_id"], score=fr(score), risk=risk, conf=fr(conf), clabel=clabel
    )
    if conf < score - 0.10:
        intro += " " + rng.choice(LOW_CONF_NOTES)

    k = len(alert["neighbors"])
    if k == 0:
        voisinage = "aucune transaction voisine n'est associée à cette alerte."
    else:
        s = "s" if k > 1 else ""
        ids = ", ".join(str(n) for n in alert["neighbors"])
        voisinage = f"{k} transaction{s} voisine{s} dans le graphe ({ids})."

    feature_lines = []
    for rank, (name, weight) in enumerate(alert["top_features"]):
        label = FEATURE_LABELS.get(name, name.replace("_", " "))
        label = label[0].upper() + label[1:]
        suffix = " — facteur principal" if rank == 0 else ""
        feature_lines.append(f"- {label} ({name}) : poids {fr(weight)}{suffix}")

    refs = pick_references(alert, rng)
    ref_lines = [f"- {REFS[key]}" for key in refs]

    actions = list(ACTIONS_BY_RISK[risk]) + [PATTERN_ACTION[pattern]]
    if "R21" in refs:
        actions.append(NO_TIPPING_OFF)
    action_lines = [f"- {a}" for a in actions]

    return "\n".join([
        f"RAPPORT D'AUDIT — Transaction {alert['tx_id']}",
        "",
        "1. Résumé",
        intro,
        "",
        "2. Schéma détecté",
        f"Schéma : {pattern} — {PATTERN_DESC[pattern]}.",
        f"Voisinage : {voisinage}",
        "",
        "3. Facteurs explicatifs",
        *feature_lines,
        "",
        "4. Références réglementaires",
        *ref_lines,
        "",
        "5. Recommandations",
        *action_lines,
        "",
        rng.choice(CLOSINGS),
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--alerts", type=Path, default=HERE / "mock_alerts.json")
    parser.add_argument("--out-dir", type=Path, default=HERE / "instruction_data")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    alerts = json.loads(args.alerts.read_text(encoding="utf-8"))

    # Rapport reproductible : le hasard dépend de la seed ET du tx_id.
    records = []
    for alert in alerts:
        report = build_report(alert, random.Random(f"{args.seed}-{alert['tx_id']}"))
        ok, problems = check_report(alert, report)
        if not ok:
            raise SystemExit(f"Rapport incohérent pour {alert['tx_id']} : {problems}")
        records.append({
            "id": f"alert-{alert['tx_id']}",
            "instruction": INSTRUCTION,
            "input": json.dumps(alert, ensure_ascii=False),
            "output": report,
            "meta": {"synthetic": True, "generator": "templates-v1"},
        })

    # Découpage 80/10/10, mélangé avec la seed (chaque alerte est unique).
    order = list(range(len(records)))
    random.Random(args.seed).shuffle(order)
    n_train, n_val = int(0.8 * len(order)), int(0.1 * len(order))
    splits = {
        "train": order[:n_train],
        "val": order[n_train:n_train + n_val],
        "test": order[n_train + n_val:],
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, idxs in splits.items():
        with open(args.out_dir / f"{name}.jsonl", "w", encoding="utf-8") as f:
            for i in idxs:
                rec = dict(records[i], meta={**records[i]["meta"], "split": name})
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    words = [len(r["output"].split()) for r in records]
    print(f"{len(records)} exemples, tous cohérents avec leur alerte")
    for name, idxs in splits.items():
        pats = Counter(json.loads(records[i]["input"])["pattern"] for i in idxs)
        print(f"  {name}: {len(idxs)} | patterns {dict(pats)}")
    print(f"longueur des rapports : moyenne {sum(words) / len(words):.0f} mots, "
          f"max {max(words)} mots")
    print(f"fichiers écrits dans {args.out_dir}")


if __name__ == "__main__":
    main()
