#!/usr/bin/env python3
"""B6 - Agent d'investigation : une alerte entre, un rapport d'audit sort.

Boucle (cahier des charges : « lire l'alerte, appeler les outils, rédiger via
le LLM-LoRA ») :

    1. LIRE      l'alerte (contrat d'interface de A)
    2. OUTILS    voisinage, explication, statistiques, recherche réglementaire
    3. RÉDIGER   le LLM-LoRA écrit le rapport en 5 sections
    4. CONTRÔLER chaque déduction du rapport (niveau de risque, fiabilité, note de
                 prudence, action du schéma, recommandations GAFI) est comparée
                 aux règles déterministes ; une section fausse est REMPLACÉE par
                 la version calculée, et la correction est tracée
    5. ANNEXER   les éléments recueillis par les outils (section 6) + la traçabilité

Pourquoi l'étape 4 : B4 a montré que le LoRA recopie bien les faits (100 %) mais
déduit mal (14 % de rapports cohérents à r=16). Ces déductions sont des fonctions
déterministes de l'alerte : on les calcule au lieu de les faire deviner.

Limites à connaître (à écrire dans l'analyse) :
  * la planification est FIXE (mêmes outils, même ordre) : ce n'est pas un LLM qui
    choisit ses outils ;
  * les règles de contrôle sont celles du jeu de données synthétique de B3 ;
  * avec le backend factice, voisinage et statistiques sont simulés.

Trois modes pour la comparaison avec / sans RAG :
    "off"    : pas de RAG
    "prompt" : extraits ajoutés au prompt du LLM (comme B4 « LoRA + RAG »)
    "annex"  : extraits copiés tels quels dans la section 6 du rapport, hors du LLM
"""
import random
from collections import Counter

from build_instruction_dataset import build_report
from lora_utils import SECTIONS, check_derived, score_report
from report_checks import check_report

TOOL_ORDER = ["neighbors", "explain", "stats", "regulation"]
RAG_MODES = ("off", "prompt", "annex")
SHORT = {s: s.split(". ", 1)[1] for s in SECTIONS}  # "1. Résumé" -> "Résumé"


# --- Formats -----------------------------------------------------------------

def _fr_num(x: float) -> str:
    return f"{x:,.2f}".replace(",", " ").replace(".", ",")


# --- 1-2. Lire l'alerte et appeler les outils --------------------------------

def gather(alert: dict, tools: dict) -> dict:
    """Appelle chaque outil disponible ; renvoie {evidence, trace}."""
    evidence, trace = {}, []
    for key in TOOL_ORDER:
        if key not in tools:
            continue
        res = tools[key](alert)
        evidence[key] = res
        trace.append({"tool": res["tool"], "ok": res["ok"], "source": res["source"],
                      "summary": res["summary"]})
    return {"evidence": evidence, "trace": trace}


# --- 4. Contrôle et réparation -----------------------------------------------

def parse_sections(report: str):
    """Découpe un rapport en {titre_section: bloc}. None si structure invalide."""
    pos = [report.find(s) for s in SECTIONS]
    if any(p < 0 for p in pos) or pos != sorted(pos):
        return None
    head = report[:pos[0]].strip()
    blocks = {}
    for i, s in enumerate(SECTIONS):
        end = pos[i + 1] if i + 1 < len(SECTIONS) else len(report)
        blocks[s] = report[pos[i]:end].strip()
    return head, blocks


def _assemble(head: str, blocks: dict) -> str:
    return head + "\n\n" + "\n\n".join(blocks[s] for s in SECTIONS)


def _failing_sections(alert: dict, report: str, finished: bool) -> set:
    """Sections à remplacer d'après les contrôles qui échouent."""
    d = check_derived(alert, report)
    bad = set()
    if not (d["level_ok"] and d["reliab_ok"] and d["note_ok"]):
        bad.add(SECTIONS[0])
    if not (d["refs_ok"] and d["cite_labels_ok"]):
        bad.add(SECTIONS[3])
    if not d["action_ok"]:
        bad.add(SECTIONS[4])
    ok, _ = check_report(alert, report)
    if not ok:
        bad.update({SECTIONS[1], SECTIONS[2]})
    return bad


def reference_report(alert: dict) -> str:
    """Rapport calculé par les règles (même générateur que B3, graine = tx_id)."""
    return build_report(alert, random.Random(alert["tx_id"]))


def verify_and_repair(alert: dict, draft: str, finished: bool = True):
    """Compare le brouillon du LLM aux règles ; remplace ce qui est faux.

    Retourne (rapport, sections_remplacées, 'complet' si tout a été remplacé).
    On procède par étapes : on remplace d'abord les sections fautives, puis on
    revérifie ; si le rapport reste faux, on remplace tout.
    """
    ref = reference_report(alert)
    ref_head, ref_blocks = parse_sections(ref)
    parsed = parse_sections(draft) if draft else None
    if parsed is None or not finished or score_report(alert, draft, finished)["echo"]:
        return ref, list(SECTIONS), True  # brouillon inexploitable : tout recalculer

    head, blocks = parsed
    replaced = []
    for _ in range(2):  # remplace, revérifie, remplace encore si besoin
        bad = _failing_sections(alert, _assemble(head, blocks), True) - set(replaced)
        if not bad:
            break
        for s in SECTIONS:
            if s in bad:
                blocks[s] = ref_blocks[s]
                replaced.append(s)
    final = _assemble(head, blocks)
    if _failing_sections(alert, final, True):
        return ref, list(SECTIONS), True
    return final, [s for s in SECTIONS if s in replaced], False


# --- 5. Annexe (éléments recueillis par les outils) --------------------------

def build_annex(evidence: dict, trace: list, replaced: list, simulated: bool,
                full: bool) -> str:
    lines = ["6. Éléments d'investigation (outils)"]
    tag = " [données simulées]" if simulated else ""

    nb = evidence.get("neighbors")
    if nb and nb["ok"] and nb["data"]:
        lines.append(f"Voisinage{tag} :")
        for r in nb["data"]:
            same = "oui" if r["same_pattern"] else "non"
            lines.append(f"- Transaction {r['tx_id']} : montant {_fr_num(r['amount'])}, "
                         f"sens {r['direction']}, même schéma que l'alerte : {same}")
    st = evidence.get("stats")
    if st and st["ok"]:
        s = st["data"]
        lines.append(f"Statistiques du compte{tag} :")
        lines.append(f"- Ancienneté {s['account_age_days']} jours ; "
                     f"{s['tx_count_30d']} transactions sur 30 jours ; "
                     f"volume {_fr_num(s['volume_30d'])} ; montant moyen {_fr_num(s['mean_amount'])} ; "
                     f"{s['distinct_counterparties_30d']} contreparties distinctes")
    rg = evidence.get("regulation")
    if rg and rg["ok"] and rg["data"]:
        lines.append("Extraits réglementaires consultés (texte copié de l'index, non reformulé) :")
        for i, h in enumerate(rg["data"], 1):
            lines.append(f"- [{i}] {h['source']}, p.{h['pages']} : {h['text']}")

    called = ", ".join(t["tool"] + ("" if t["ok"] else " (échec)") for t in trace)
    lines.append("Traçabilité :")
    lines.append(f"- Outils appelés : {called if called else 'aucun'}")
    if full:
        lines.append("- Le brouillon du modèle étant inexploitable, le rapport a été "
                     "intégralement recalculé par les règles.")
    elif replaced:
        names = ", ".join(SHORT[s] for s in replaced)
        lines.append(f"- Rédaction par le LLM-LoRA ; sections remplacées car incohérentes "
                     f"avec les règles : {names}")
    else:
        lines.append("- Rédaction par le LLM-LoRA ; toutes les déductions vérifiées conformes.")
    return "\n".join(lines)


# --- Agent complet -----------------------------------------------------------

def finalize(alert: dict, draft: str, finished: bool, gathered: dict,
             simulated: bool = True, repair: bool = True) -> dict:
    """Étapes 4 et 5 pour une alerte, à partir du brouillon du LLM."""
    before = score_report(alert, draft, finished)
    if repair:
        core, replaced, full = verify_and_repair(alert, draft, finished)
    else:
        core, replaced, full = draft, [], False
    after = score_report(alert, core, True)
    annex = build_annex(gathered["evidence"], gathered["trace"], replaced,
                        simulated, full)
    return {
        "id": f"alert-{alert['tx_id']}",
        "draft": draft, "finished": bool(finished),
        "core": core, "report": core + "\n\n" + annex,
        "replaced": replaced, "full_replacement": full,
        "before": before, "after": after, "trace": gathered["trace"],
        "n_sources": len(gathered["evidence"].get("regulation", {}).get("data") or []),
    }


def run_agent(alerts: list, tools: dict, generate_fn, rag_mode: str = "annex", *,
              contexts: dict = None, simulated: bool = True, repair: bool = True) -> list:
    """Traite une liste d'alertes.

    generate_fn(alerts, contexts) -> [(texte, terminé)]  (LLM-LoRA, par lots)
      contexts : {tx_id: texte} en mode "prompt", sinon None.
    """
    if rag_mode not in RAG_MODES:
        raise ValueError(f"rag_mode doit être dans {RAG_MODES}")
    use = {k: v for k, v in tools.items() if not (k == "regulation" and rag_mode != "annex")}
    gathered = [gather(a, use) for a in alerts]
    ctx = contexts if rag_mode == "prompt" else None
    if rag_mode == "prompt" and not contexts:
        raise ValueError("mode 'prompt' : fournir contexts={tx_id: texte}")
    drafts = generate_fn(alerts, ctx)
    return [finalize(a, d, f, g, simulated, repair)
            for a, (d, f), g in zip(alerts, drafts, gathered)]


def summarize_agent(results: list) -> dict:
    """Tableau de comparaison : brouillon du LLM seul vs rapport final."""
    n = len(results)
    pct = lambda c: round(100 * c / n, 1)
    kept = sum(len(SECTIONS) - len(r["replaced"]) for r in results)
    out = {
        "n": n,
        "draft_usable_%": pct(sum(r["before"]["usable"] for r in results)),
        "draft_strict_%": pct(sum(r["before"]["strict_ok"] for r in results)),
        "final_strict_%": pct(sum(r["after"]["strict_ok"] for r in results)),
        "full_replacement_%": pct(sum(r["full_replacement"] for r in results)),
        "sections_kept_from_llm_%": round(100 * kept / (n * len(SECTIONS)), 1),
        "avg_sources": round(sum(r["n_sources"] for r in results) / n, 2),
    }
    c = Counter(s for r in results for s in r["replaced"])
    for s in SECTIONS:
        out[f"replaced_{SHORT[s]}_%"] = pct(c[s])
    return out
