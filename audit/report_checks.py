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
     et chaque voisin de l'alerte apparaissent dans le rapport ;
  2. aucun nombre décimal (0,xx ou 0.xx) absent de l'alerte n'apparaît ;
  3. aucun identifiant de 4-5 chiffres absent de l'alerte n'apparaît ;
  4. aucun AUTRE pattern (cycle, fan-in, fan-out) n'est cité.
Les nombres sont comparés par VALEUR : 0,8 / 0,80 / 0.8 sont équivalents
(un modèle qui recopie « 0.8 » depuis l'alerte n'est donc pas pénalisé).
"""
import re

PATTERN_CODES = ["cycle", "fan-in", "fan-out"]


def fr(x: float) -> str:
    """0.84 -> '0,84' (deux décimales, virgule)."""
    return f"{x:.2f}".replace(".", ",")


def _numbers(text: str) -> list:
    """Tous les décimaux du texte (0,84 ou 0.84) sous forme de float."""
    pattern = r"(?<![\d.,])\d[.,]\d+(?!\d)"
    return [float(m.replace(",", ".")) for m in re.findall(pattern, text)]


def _present(value: float, found: list) -> bool:
    return any(abs(f - value) < 1e-6 for f in found)


def _has_code(code: str, text: str) -> bool:
    # « cycle » ne doit pas être trouvé dans « cycle_length » : on exclut \w et -
    return re.search(rf"(?<![\w-]){re.escape(code)}(?![\w-])", text) is not None


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

    allowed = [alert["score"], alert["confidence"]]
    allowed += [w for _, w in alert["top_features"]]
    for f in found:
        if not _present(f, allowed):
            problems.append(f"valeur inventée : {fr(f)}")

    allowed_ids = {str(alert["tx_id"])} | {str(n) for n in alert["neighbors"]}
    for i in re.findall(r"(?<!\d)\d{4,5}(?!\d)", report):
        if i not in allowed_ids:
            problems.append(f"identifiant inventé : {i}")

    for code in PATTERN_CODES:
        if code != alert["pattern"] and _has_code(code, report):
            problems.append(f"pattern incohérent : {code} cité")

    problems = list(dict.fromkeys(problems))  # sans doublons, ordre conservé
    return (not problems, problems)
