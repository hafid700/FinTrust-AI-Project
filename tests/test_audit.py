"""Tests de la partie B (audit) : jeu d'instruction, contrôles, agent. Sans GPU ni réseau."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audit"))

import agent as A  # noqa: E402
import agent_tools as T  # noqa: E402
import lora_utils as L  # noqa: E402
from build_instruction_dataset import risk_level  # noqa: E402

DATA = ROOT / "audit" / "instruction_data"


def _rows(split="test", n=40):
    return L.load_jsonl(str(DATA / f"{split}.jsonl"))[:n]


def test_risk_levels_follow_calibrated_confidence():
    assert risk_level(0.95) == "critique" and risk_level(0.75) == "élevé"
    assert risk_level(0.55) == "modéré à élevé" and risk_level(0.30) == "modéré"


def test_reference_reports_pass_all_checks():
    for split in ("train", "val", "test"):
        for r in _rows(split, 200):
            s = L.score_report(json.loads(r["input"]), r["output"])
            assert s["strict_ok"], (r["id"], s)


def test_each_rule_detects_its_mutation():
    r = _rows("test", 1)[0]
    a = json.loads(r["input"])
    bad = re.sub(r"niveau( de risque)? (critique|élevé|modéré à élevé|modéré)",
                 "niveau de risque inexistant", r["output"], count=1)
    assert not L.score_report(a, bad)["strict_ok"]
    wrong_head = r["output"].replace(f"Transaction {a['tx_id']}", "Transaction 999", 1)
    fixed, _, _ = A.verify_and_repair(a, wrong_head, True)  # l'agent remet le bon numéro en en-tête
    assert fixed.startswith(f"RAPPORT D'AUDIT — Transaction {a['tx_id']}")


def test_agent_keeps_good_drafts_and_repairs_bad_ones():
    rows = _rows("test", 20)
    alerts = [json.loads(r["input"]) for r in rows]
    tools = T.make_tools(T.MockBackend(), None)
    good = A.run_agent(alerts, tools, lambda a, c: [(r["output"], True) for r in rows], "off")
    assert all(not g["replaced"] and g["after"]["strict_ok"] for g in good)
    for draft, finished in [("", True), ("blabla", True), (rows[0]["output"][:300], False)]:
        res = A.finalize(alerts[0], draft, finished, A.gather(alerts[0], tools))
        assert res["after"]["strict_ok"] and res["full_replacement"]
    foreign = rows[0]["output"].replace("Schéma :", "Schéma 庶 :", 1)
    res = A.finalize(alerts[0], foreign, True, A.gather(alerts[0], tools))
    assert res["after"]["strict_ok"] and res["replaced"]


def test_failing_tool_does_not_stop_the_agent():
    class Broken(T.MockBackend):
        def neighbors(self, alert):
            raise RuntimeError("hors ligne")

    rows = _rows("test", 1)
    a = json.loads(rows[0]["input"])
    res = A.run_agent([a], T.make_tools(Broken(), None), lambda al, c: [(rows[0]["output"], True)], "off")[0]
    assert "échec" in res["report"] and res["after"]["strict_ok"]
