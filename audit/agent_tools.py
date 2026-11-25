#!/usr/bin/env python3
"""B6 - Les 4 outils de l'agent d'investigation (cahier des charges, section B6).

    1. neighbors_tool   : voisinage d'un compte dans le graphe
    2. explain_tool     : explication de l'alerte (SHAP / GNNExplainer)
    3. regulation_tool  : recherche réglementaire (RAG, base FAISS de B1)
    4. stats_tool       : statistiques du compte

Chaque outil prend UNE alerte (contrat d'interface) et renvoie un dict
sérialisable : {"tool", "ok", "source", "data", "summary"}. Un outil qui échoue
ne fait jamais planter l'agent : il renvoie ok=False et un message.

Les données du graphe et du compte viennent d'un « backend ». Tant que le
modèle de A n'est pas disponible, on utilise MockBackend (valeurs SIMULÉES,
déterministes, signalées comme telles dans le rapport). Pour l'intégration,
il suffit d'écrire un backend avec les mêmes 3 méthodes branché sur le GNN de A.
"""
import random

from build_instruction_dataset import FEATURE_LABELS


class MockBackend:
    """Backend simulé : valeurs inventées mais déterministes (même alerte -> mêmes valeurs).

    Interface à reproduire pour le vrai backend (modèle de A / B5) :
        neighbors(alert)      -> list[dict(tx_id, amount, direction, same_pattern)]
        account_stats(alert)  -> dict(...)
        explain(alert)        -> list[(nom_feature, poids)]
    """

    name = "données simulées (backend factice)"
    simulated = True

    def __init__(self, seed: int = 42):
        self.seed = seed

    def _rng(self, *key):
        return random.Random("-".join(str(k) for k in (self.seed, *key)))

    def neighbors(self, alert: dict) -> list:
        out = []
        for n in alert["neighbors"]:
            rng = self._rng("nb", alert["tx_id"], n)
            out.append({
                "tx_id": n,
                "amount": round(rng.uniform(500, 90_000), 2),
                "direction": rng.choice(["entrante", "sortante"]),
                "same_pattern": rng.random() < 0.6,
            })
        return out

    def account_stats(self, alert: dict) -> dict:
        rng = self._rng("acct", alert["tx_id"])
        n30 = rng.randint(2, 140)
        mean = rng.uniform(800, 25_000)
        return {
            "account_age_days": rng.randint(15, 3000),
            "tx_count_30d": n30,
            "volume_30d": round(n30 * mean, 2),
            "mean_amount": round(mean, 2),
            "distinct_counterparties_30d": rng.randint(1, max(2, n30 // 2)),
        }

    def explain(self, alert: dict) -> list:
        # Les features de l'alerte sont déjà l'explication fournie par le détecteur.
        # Le vrai backend recalculera SHAP / GNNExplainer (B5).
        return [(n, w) for n, w in alert["top_features"]]


class RealBackend:
    """Backend branché sur les données réelles d'A et de B5 (aucune valeur simulée).

    neighbors     : transactions voisines lues dans neighbor_transactions.csv (A)
    account_stats : agrégats calculés sur ces mêmes voisines, pour les comptes de
                    l'alerte (ce n'est PAS l'historique complet du compte : le fichier
                    d'A ne contient que le voisinage des alertes)
    explain       : top_features et signes de alerts_explained.jsonl (B5)
    """

    name = "données réelles (alertes d'A, explications B5)"
    simulated = False

    def __init__(self, neighbor_csv: str, explained_alerts: list = None):
        import csv
        with open(neighbor_csv, newline="", encoding="utf-8") as f:
            self.tx = {int(r["tx_id"]): r for r in csv.DictReader(f)}
        self.expl = {a["tx_id"]: a for a in (explained_alerts or [])}

    @staticmethod
    def _accounts(alert):
        c = alert.get("context") or {}
        return {c.get("from_account"), c.get("to_account")} - {None}

    def neighbors(self, alert: dict) -> list:
        mine, out = self._accounts(alert), []
        for n in alert["neighbors"]:
            r = self.tx.get(int(n))
            if r is None:
                continue
            if r["to_account"] in mine:
                direction = "entrante"
            elif r["from_account"] in mine:
                direction = "sortante"
            else:
                direction = "autre"
            out.append({"tx_id": int(n), "date": r["timestamp"],
                        "amount": float(r["amount_paid"]), "currency": r["payment_currency"],
                        "direction": direction, "format": r["payment_format"],
                        "from_account": r["from_account"], "to_account": r["to_account"]})
        return out

    def account_stats(self, alert: dict) -> dict:
        rows = self.neighbors(alert)
        mine = self._accounts(alert)
        amounts = [r["amount"] for r in rows]
        cps = {r["to_account"] if r["from_account"] in mine else r["from_account"] for r in rows}
        cps -= mine
        return {"n_neighbors": len(rows), "n_incoming": sum(r["direction"] == "entrante" for r in rows),
                "n_outgoing": sum(r["direction"] == "sortante" for r in rows),
                "total_amount": round(sum(amounts), 2),
                "mean_amount": round(sum(amounts) / len(amounts), 2) if amounts else 0.0,
                "distinct_counterparties": len(cps)}

    def explain(self, alert: dict) -> list:
        a = self.expl.get(alert["tx_id"], alert)
        return [(n, w) for n, w in a["top_features"]]


# --- Outils ------------------------------------------------------------------

def _result(tool, ok, source, data, summary):
    return {"tool": tool, "ok": ok, "source": source, "data": data, "summary": summary}


def neighbors_tool(alert: dict, backend) -> dict:
    name = "voisinage"
    try:
        rows = backend.neighbors(alert)
        if not rows:
            return _result(name, True, backend.name, [],
                           "aucune transaction voisine")
        if all("same_pattern" in r for r in rows):
            same = sum(1 for r in rows if r["same_pattern"])
            return _result(name, True, backend.name, rows,
                           f"{len(rows)} voisines, dont {same} dans le même schéma")
        return _result(name, True, backend.name, rows, f"{len(rows)} transactions voisines")
    except Exception as e:  # un outil en panne ne doit pas bloquer le rapport
        return _result(name, False, backend.name, None, f"échec : {e}")


def explain_tool(alert: dict, backend) -> dict:
    name = "explication"
    try:
        feats = backend.explain(alert)
        if not feats:
            return _result(name, True, backend.name, [], "aucune explication")
        top = feats[0]
        return _result(name, True, backend.name, [list(f) for f in feats],
                       f"facteur principal : {top[0]} (poids {top[1]})")
    except Exception as e:
        return _result(name, False, backend.name, None, f"échec : {e}")


def stats_tool(alert: dict, backend) -> dict:
    name = "statistiques du voisinage" if not getattr(backend, "simulated", False) else "statistiques du compte"
    try:
        s = backend.account_stats(alert)
        return _result(name, True, backend.name, s,
                       (f"{s['tx_count_30d']} transactions sur 30 jours" if "tx_count_30d" in s
                        else f"{s['n_neighbors']} transactions voisines analysées"))
    except Exception as e:
        return _result(name, False, backend.name, None, f"échec : {e}")


def regulation_tool(alert: dict, search_fn, k: int = 2, max_words: int = 60) -> dict:
    """Extraits réglementaires (verbatim, avec source et pages) pour cette alerte.

    On réutilise les mêmes requêtes que B4 (RAG_QUERIES : une par schéma + la
    déclaration de soupçon). Les extraits sont COPIÉS depuis l'index, jamais
    reformulés : ils ne peuvent donc pas être inventés.
    """
    name = "recherche réglementaire"
    try:
        from lora_utils import RAG_QUERIES, STR_QUERY

        results = [search_fn(q, k) for q in (RAG_QUERIES[alert["pattern"]], STR_QUERY)]
        seen, hits = set(), []
        for rank in range(k):
            for res in results:
                if rank >= len(res) or len(hits) >= k:
                    continue
                h = res[rank]
                key = (h["source"], h["pages"])
                if key in seen:
                    continue
                seen.add(key)
                words = h["text"].split()
                hits.append({
                    "source": h["source"], "pages": h["pages"], "score": h.get("score"),
                    "text": " ".join(words[:max_words]) + (" […]" if len(words) > max_words else ""),
                })
        return _result(name, True, "index FAISS (B1)", hits,
                       f"{len(hits)} extraits : " + "; ".join(
                           f"{h['source']} p.{h['pages']}" for h in hits))
    except Exception as e:
        return _result(name, False, "index FAISS (B1)", None, f"échec : {e}")


def make_tools(backend, search_fn=None, k: int = 2) -> dict:
    """{nom_court: fonction(alert) -> résultat}. search_fn=None désactive le RAG."""
    tools = {
        "neighbors": lambda a: neighbors_tool(a, backend),
        "explain": lambda a: explain_tool(a, backend),
        "stats": lambda a: stats_tool(a, backend),
    }
    if search_fn is not None:
        tools["regulation"] = lambda a: regulation_tool(a, search_fn, k=k)
    return tools


def feature_label(name: str) -> str:
    return FEATURE_LABELS.get(name, name.replace("_", " "))
