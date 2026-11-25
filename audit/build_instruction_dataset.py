#!/usr/bin/env python3
"""B3 (v2) - Dataset d'instruction (alerte -> rapport d'audit) pour le LoRA.

Entrée  : les VRAIES alertes du modèle FedAvg de A, calibrées et expliquées par B5
          (audit/results/b5/alerts_explained.jsonl : 2 246 alertes). La v1 utilisait
          les alertes factices de B2 (audit/mock_alerts.json, encore lisibles avec --alerts).
Sortie  : audit/instruction_data/{train,val,test}.jsonl (80/10/10 stratifié par schéma, seed fixée).

Les ALERTES sont réelles ; les RAPPORTS restent produits par des modèles de texte avec
variations (pas par un LLM) : ce sont des cibles d'entraînement synthétiques à signaler dans
le README. Un rapport n'utilise QUE les informations de l'alerte (pas de montant, de nom ou
de date inventés) : règle vérifiée par audit/report_checks.py. Le champ `input` de chaque
exemple est la « vue compacte » de l'alerte (prompt_view) : valeurs arrondies à 3 décimales
et sans les champs techniques (valeurs de l'explication, labels). Les labels vrai/faux
de A ne sont jamais utilisés.

Règles de déduction (v2), toutes déterministes :
  * niveau de risque : d'après la CONFIANCE CALIBRÉE (B5) : critique >= 0,90 ; élevé >= 0,70 ;
    modéré à élevé >= 0,50 ; sinon modéré (le score brut est trop gonflé pour servir de seuil) ;
  * fiabilité du schéma : élevée pour fan_in et fan_out, limitée pour cycle et none
    (précision des alertes par schéma mesurée par A sur son test : 0,56 à 0,98) ;
    une note de prudence accompagne une fiabilité limitée ;
  * recommandations GAFI : R10 (R16 pour fan_out), R20 toujours, R21 si confiance >= 0,70 ;
  * chaque facteur est dit « aggravant » ou « atténuant » d'après le signe de son attribution.

Usage :
    python audit/build_instruction_dataset.py
    python audit/build_instruction_dataset.py --alerts audit/results/b5/alerts_explained.jsonl --seed 42
"""
import argparse
import json
import random
from collections import Counter
from pathlib import Path

try:
    from report_checks import check_report, fr, fmt_amount, fmt_date
except ImportError:  # import depuis la racine du dépôt (notebooks Colab)
    from audit.report_checks import check_report, fr, fmt_amount, fmt_date

HERE = Path(__file__).parent
GENERATOR = "templates-v2"
RISK_THRESHOLDS = (0.90, 0.70, 0.50)   # critique, élevé, modéré à élevé (sur la confiance calibrée)
R21_THRESHOLD = 0.70
RELIABLE_PATTERNS = ("fan_in", "fan_out")

INSTRUCTION = (
    "Tu es un analyste conformité LAB/FT. Rédige un rapport d'audit en français "
    "à partir de l'alerte suivante. N'utilise que les informations présentes "
    "dans l'alerte et n'invente aucune valeur."
)

# --- Vocabulaire ------------------------------------------------------------

# Les 30 groupes de features de l'explication de B5 (noms de A, graph.py et graph_features.py).
# Les features « de graphe » sont des log(1 + nombre) ou log(1 + somme) des transactions
# STRICTEMENT ANTÉRIEURES (24 h glissantes, ou tout l'historique pour `_all`).
FEATURE_LABELS = {
    "log_amount_paid": "le montant payé",
    "log_amount_received": "le montant reçu",
    "same_currency": "l'identité des devises payée et reçue",
    "cross_bank": "le caractère inter-bancaire de la transaction",
    "hour_sin": "l'heure de la transaction (composante sinus)",
    "hour_cos": "l'heure de la transaction (composante cosinus)",
    "payment_format": "le format de paiement utilisé",
    "payment_currency": "la devise de paiement",
    "src_out_cnt_24h": "le nombre de transactions sortantes du compte émetteur sur 24 h",
    "src_out_amt_24h": "le volume sortant du compte émetteur sur 24 h",
    "src_in_cnt_24h": "le nombre de transactions entrantes du compte émetteur sur 24 h",
    "src_in_amt_24h": "le volume entrant du compte émetteur sur 24 h",
    "src_passthrough_24h": "le déséquilibre sorties/entrées du compte émetteur sur 24 h (profil de compte relais)",
    "dst_out_cnt_24h": "le nombre de transactions sortantes du compte destinataire sur 24 h",
    "dst_out_amt_24h": "le volume sortant du compte destinataire sur 24 h",
    "dst_in_cnt_24h": "le nombre de transactions entrantes du compte destinataire sur 24 h",
    "dst_in_amt_24h": "le volume entrant du compte destinataire sur 24 h",
    "dst_passthrough_24h": "le déséquilibre sorties/entrées du compte destinataire sur 24 h (profil de compte relais)",
    "src_out_cnt_all": "le nombre de transactions sortantes passées du compte émetteur",
    "src_out_amt_all": "le volume sortant passé du compte émetteur",
    "src_in_cnt_all": "le nombre de transactions entrantes passées du compte émetteur",
    "src_in_amt_all": "le volume entrant passé du compte émetteur",
    "src_passthrough_all": "le déséquilibre sorties/entrées passé du compte émetteur (profil de compte relais)",
    "dst_out_cnt_all": "le nombre de transactions sortantes passées du compte destinataire",
    "dst_out_amt_all": "le volume sortant passé du compte destinataire",
    "dst_in_cnt_all": "le nombre de transactions entrantes passées du compte destinataire",
    "dst_in_amt_all": "le volume entrant passé du compte destinataire",
    "dst_passthrough_all": "le déséquilibre sorties/entrées passé du compte destinataire (profil de compte relais)",
    "pair_prev": "le nombre de transactions antérieures entre ces deux mêmes comptes",
    "rev_pair_prev": "le nombre de transactions antérieures en sens inverse entre ces deux comptes",
}

# NB : seul le pattern annoncé doit contenir son code (cycle, fan_in, fan_out) ;
# les autres textes n'emploient pas ces mots (contrôlé par report_checks).
PATTERN_DESC = {
    "cycle": (
        "circuit fermé de fonds : l'argent revient vers son point de départ "
        "après plusieurs transferts, schéma typique de l'empilement (layering)"
    ),
    "fan_in": (
        "concentration de fonds : de nombreux comptes versent vers un même "
        "compte, schéma compatible avec un compte « mule » collecteur"
    ),
    "fan_out": (
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
    "La transaction {tx} a été signalée par le détecteur avec un score brut de "
    "{score} et une confiance calibrée de {conf} (niveau de risque {risk}, "
    "fiabilité du schéma {rel}).",
    "Le modèle de détection a levé une alerte sur la transaction {tx} : score "
    "brut {score}, confiance calibrée {conf}, niveau {risk}, fiabilité du "
    "schéma {rel}.",
    "Alerte sur la transaction {tx} : score brut {score}, confiance calibrée "
    "{conf}, niveau de risque {risk}, fiabilité du schéma {rel}.",
]

CAUTION_NOTES = [
    "Ce type de schéma est associé à davantage de fausses alertes : l'alerte "
    "doit être confirmée par un analyste avant toute décision.",
    "Le schéma détecté est moins discriminant : une validation humaine est "
    "nécessaire.",
]

FEATURE_CAVEAT = (
    "Ces facteurs décrivent les caractéristiques de la transaction ; le contexte "
    "réseau des comptes (comptes voisins) n'est pas détaillé."
)

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
    "fan_in": "Identifier les comptes émetteurs et vérifier si le compte collecteur est un compte mule.",
    "fan_out": "Identifier les bénéficiaires des dispersions et vérifier leur justification économique.",
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

def risk_level(confidence: float) -> str:
    """Niveau de risque d'après la CONFIANCE CALIBRÉE (B5), pas le score brut."""
    if confidence >= RISK_THRESHOLDS[0]:
        return "critique"
    if confidence >= RISK_THRESHOLDS[1]:
        return "élevé"
    if confidence >= RISK_THRESHOLDS[2]:
        return "modéré à élevé"
    return "modéré"


def reliability_label(pattern: str) -> str:
    return "élevée" if pattern in RELIABLE_PATTERNS else "limitée"


def pick_references(alert: dict, rng: random.Random) -> list:
    keys = ["R16" if alert["pattern"] == "fan_out" else "R10", "R20"]
    if alert["confidence"] >= R21_THRESHOLD:
        keys.append("R21")
    if rng.random() < 0.7:
        keys.append("MA")
    return sorted(keys, key=REF_ORDER.index)


def transaction_sentence(ctx: dict) -> str:
    """Phrase descriptive de la transaction : uniquement des valeurs de l'alerte."""
    paid = f"{fmt_amount(ctx['amount_paid'])} {ctx['payment_currency']}"
    if ctx["amount_received"] == ctx["amount_paid"] and ctx["receiving_currency"] == ctx["payment_currency"]:
        amount = f"d'un montant de {paid}"
    else:
        recv = f"{fmt_amount(ctx['amount_received'])} {ctx['receiving_currency']}"
        amount = f"d'un montant payé de {paid} (montant reçu : {recv})"
    date, hour = fmt_date(ctx["timestamp"])
    return (f"Transaction du {date} à {hour}, {amount}, du compte {ctx['from_account']} "
            f"(banque {ctx['from_bank']}) vers le compte {ctx['to_account']} "
            f"(banque {ctx['to_bank']}), format de paiement {ctx['payment_format']}.")


# --- Rapport ---------------------------------------------------------------

def build_report(alert: dict, rng: random.Random) -> str:
    score, conf, pattern = alert["score"], alert["confidence"], alert["pattern"]
    risk, rel = risk_level(conf), reliability_label(pattern)

    intro = rng.choice(INTROS).format(
        tx=alert["tx_id"], score=fr(score), risk=risk, conf=fr(conf), rel=rel
    )
    if rel == "limitée":
        intro += " " + rng.choice(CAUTION_NOTES)
    intro += "\n" + transaction_sentence(alert["context"])

    k = len(alert["neighbors"])
    if k == 0:
        voisinage = "aucune transaction voisine n'est associée à cette alerte."
    else:
        s = "s" if k > 1 else ""
        ids = ", ".join(str(n) for n in alert["neighbors"])
        voisinage = f"{k} transaction{s} voisine{s} dans le graphe ({ids})."

    feature_lines = []
    for rank, ((name, weight), sign) in enumerate(zip(alert["top_features"], alert["signs"])):
        label = FEATURE_LABELS.get(name, name.replace("_", " "))
        label = label[0].upper() + label[1:]
        role = "aggravant" if sign > 0 else "atténuant"
        suffix = f"facteur principal, {role}" if rank == 0 else role
        feature_lines.append(f"- {label} ({name}) : poids {fr(weight)} — {suffix}")
    feature_lines.append(FEATURE_CAVEAT)

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


# --- Alertes -> exemples ------------------------------------------------------

CONTEXT_KEYS = ("timestamp", "from_bank", "from_account", "to_bank", "to_account",
                "amount_paid", "payment_currency", "amount_received", "receiving_currency",
                "payment_format")


def prompt_view(alert: dict) -> dict:
    """Vue compacte de l'alerte donnée au modèle : valeurs arrondies à 3 décimales, sans
    champs techniques. Les poids et signes viennent de l'explication de B5."""
    signs = alert.get("signs") or alert.get("explanation", {}).get("signs")
    if signs is None or len(signs) != len(alert["top_features"]):
        raise ValueError(f"alerte {alert['tx_id']} : signes d'attribution manquants (lancer explain.py)")
    return {
        "tx_id": alert["tx_id"],
        "score": round(alert["score"], 3),
        "confidence": round(alert["confidence"], 3),
        "top_features": [[n, round(w, 3)] for n, w in alert["top_features"]],
        "signs": [int(x) for x in signs],
        "neighbors": list(alert["neighbors"]),
        "pattern": alert["pattern"],
        "context": {k: alert["context"][k] for k in CONTEXT_KEYS},
    }


def load_alerts(path: Path) -> list:
    text = Path(path).read_text(encoding="utf-8")
    if str(path).endswith(".jsonl"):
        return [json.loads(l) for l in text.splitlines() if l.strip()]
    return json.loads(text)


def stratified_split(alerts: list, seed: int) -> dict:
    """80/10/10 en gardant la proportion de chaque schéma dans chaque partie."""
    by_pat = {}
    for i, a in enumerate(alerts):
        by_pat.setdefault(a["pattern"], []).append(i)
    out = {"train": [], "val": [], "test": []}
    for pat in sorted(by_pat):
        idx = by_pat[pat]
        random.Random(f"{seed}-{pat}").shuffle(idx)
        n_tr, n_va = int(0.8 * len(idx)), int(0.1 * len(idx))
        out["train"] += idx[:n_tr]
        out["val"] += idx[n_tr:n_tr + n_va]
        out["test"] += idx[n_tr + n_va:]
    for k in out:
        random.Random(f"{seed}-{k}").shuffle(out[k])
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--alerts", type=Path, default=HERE / "results" / "b5" / "alerts_explained.jsonl")
    parser.add_argument("--out-dir", type=Path, default=HERE / "instruction_data")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    alerts = [prompt_view(a) for a in load_alerts(args.alerts)]

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
            "meta": {"synthetic_targets": True, "real_alerts": True, "generator": GENERATOR},
        })

    splits = stratified_split(alerts, args.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, idxs in splits.items():
        with open(args.out_dir / f"{name}.jsonl", "w", encoding="utf-8") as f:
            for i in idxs:
                rec = dict(records[i], meta={**records[i]["meta"], "split": name})
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    words = [len(r["output"].split()) for r in records]
    print(f"{len(records)} exemples, tous cohérents avec leur alerte")
    for name, idxs in splits.items():
        pats = Counter(alerts[i]["pattern"] for i in idxs)
        lv = Counter(risk_level(alerts[i]["confidence"]) for i in idxs)
        print(f"  {name}: {len(idxs)} | schémas {dict(pats)} | niveaux {dict(lv)}")
    print(f"longueur des rapports : moyenne {sum(words) / len(words):.0f} mots, "
          f"max {max(words)} mots")
    print(f"fichiers écrits dans {args.out_dir}")


if __name__ == "__main__":
    main()
