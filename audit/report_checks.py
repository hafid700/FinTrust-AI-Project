#!/usr/bin/env python3
"""Contrôle automatique de cohérence entre une alerte et un rapport d'audit.

Sert à deux endroits :
  - B3 : vérifier que chaque rapport du dataset d'instruction est fidèle à son alerte ;
  - B4 : mesurer l'« exactitude des faits » des rapports générés (prompt seul,
    LoRA, LoRA + RAG) : un rapport est exact s'il reprend les valeurs de
    l'alerte et n'en invente aucune.

Usage :
    from audit.report_checks import check_report
    ok, problems = check_report(alert, rapport)

Règles vérifiées :
  1. le tx_id, le score, la confiance, le pattern, chaque feature (nom + poids)
     et chaque voisin de l'alerte apparaissent dans le rapport ; si l'alerte a un
     `context` : la date et l'heure, les montants, devises, format de paiement,
     comptes et banques y figurent aussi ;
  2. aucun nombre décimal compris entre 0 et 1 (0,xx ou 0.xx) absent de
     l'alerte n'apparaît (les autres nombres, ex. « 4,1 » dans une citation
     d'article, ne sont pas des scores et sont tolérés) ;
  3. aucun identifiant de 4-5 chiffres absent de l'alerte n'apparaît ; les
     années 1900-2099 sont tolérées (« règlement 2016/679 », « GAFI 2012 »),
     sinon citer un texte réglementaire serait compté comme une invention ;
  4. aucun AUTRE pattern (cycle, fan_in, fan_out) n'est cité.
Les nombres sont comparés par VALEUR : 0,8 / 0,80 / 0.8 sont équivalents
(un modèle qui recopie « 0.8 » depuis l'alerte n'est donc pas pénalisé).
"""
import re

PATTERN_CODES = ["cycle", "fan_in", "fan_out"]


def fr(x: float) -> str:
    """0.842 -> '0,842' (trois décimales, virgule)."""
    return f"{x:.3f}".replace(".", ",")


def fmt_amount(x: float) -> str:
    """71886577.98 -> '71 886 577,98' (espace entre les milliers, virgule décimale).
    Les montants inférieurs à 1 (ex. des bitcoins) gardent 6 décimales : 0.121719 -> '0,121719'."""
    if x < 1:
        return f"{x:.6f}".replace(".", ",")
    return f"{x:,.2f}".replace(",", " ").replace(".", ",")


def fmt_date(timestamp: str) -> tuple:
    """'2022-09-13 06:14:00' -> ('13/09/2022', '06:14')."""
    d, t = timestamp.split(" ")
    y, m, day = d.split("-")
    return f"{day}/{m}/{y}", t[:5]


def _numbers(text: str) -> list:
    """Tous les décimaux du texte (0,84 ou 0.84) sous forme de float."""
    pattern = r"(?<![\d.,])\d[.,]\d+(?!\d)"
    return [float(m.replace(",", ".")) for m in re.findall(pattern, text)]


def _present(value: float, found: list) -> bool:
    return any(abs(f - value) < 1e-6 for f in found)


def _has_code(code: str, text: str) -> bool:
    # « cycle » ne doit pas être trouvé dans « cycle_length » : on exclut \w et -
    return re.search(rf"(?<![\w-]){re.escape(code)}(?![\w-])", text) is not None


def _context_problems(ctx: dict, report: str) -> list:
    """Le contexte (date, montants, devises, format, comptes, banques) doit être repris tel quel."""
    out = []
    date, hour = fmt_date(ctx["timestamp"])
    if date not in report or hour not in report:
        out.append(f"date/heure {date} {hour} absentes")
    for key in ("amount_paid", "amount_received"):
        if fmt_amount(ctx[key]) not in report:
            out.append(f"{key} {fmt_amount(ctx[key])} absent")
    for key in ("payment_currency", "receiving_currency", "payment_format",
                "from_account", "to_account", "from_bank", "to_bank"):
        if str(ctx[key]) not in report:
            out.append(f"{key} {ctx[key]} absent")
    return out


def check_report(alert: dict, report: str) -> tuple:
    """Retourne (ok, liste_de_problèmes)."""
    problems = []
    found = _numbers(report)

    if str(alert["tx_id"]) not in report:
        problems.append(f"tx_id {alert['tx_id']} absent")
    for key in ("score", "confidence"):
        if not _present(alert[key], found):
            problems.append(f"{key} {fr(alert[key])} absent")
    if not _has_code(alert["pattern"], report):
        problems.append(f"pattern {alert['pattern']} absent")
    for name, weight in alert["top_features"]:
        if name not in report:
            problems.append(f"feature {name} absente")
        if not _present(weight, found):
            problems.append(f"poids {fr(weight)} ({name}) absent")
    for n in alert["neighbors"]:
        if str(n) not in report:
            problems.append(f"voisin {n} absent")

    ctx = alert.get("context")
    if ctx:
        problems += _context_problems(ctx, report)

    allowed = [alert["score"], alert["confidence"]]
    allowed += [w for _, w in alert["top_features"]]
    if ctx:
        allowed += [ctx["amount_paid"], ctx["amount_received"]]
    for f in found:
        if f <= 1.0 and not _present(f, allowed):
            problems.append(f"valeur inventée : {fr(f)}")

    allowed_ids = {str(alert["tx_id"])} | {str(n) for n in alert["neighbors"]}
    scan = report
    if ctx:  # identifiants du contexte (comptes alphanumériques, banques) : copiés, pas inventés
        for v in (ctx["from_account"], ctx["to_account"], ctx["from_bank"], ctx["to_bank"]):
            scan = re.sub(rf"(?<!\w){re.escape(str(v))}(?!\w)", " ", scan)
    for i in re.findall(r"(?<!\d)\d{4,5}(?!\d)", scan):
        is_year = len(i) == 4 and 1900 <= int(i) <= 2099
        if i not in allowed_ids and not is_year:
            problems.append(f"identifiant inventé : {i}")

    for code in PATTERN_CODES:
        if code != alert["pattern"] and _has_code(code, report):
            problems.append(f"pattern incohérent : {code} cité")

    problems = list(dict.fromkeys(problems))  # sans doublons, ordre conservé
    return (not problems, problems)
