import sys, json, tempfile
sys.path.insert(0, sys.argv[1])
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from scripts import run_night as d
from joulewise import quiet_predicate_campaign as q
PLAN = SimpleNamespace(plan_id="p1-probe", receipt_class="DIAGNOSTIC_NO_PACK", quiet_admission=None)
with tempfile.TemporaryDirectory(dir=sys.argv[2]) as td, \
     mock.patch.object(d.night_gate, "validate_receipt", return_value=[]), \
     mock.patch.object(q, "cleanup_record", return_value={"cleanup_proven": True}):
    root = Path(td); night = root / "night"; night.mkdir()
    (night / "chain.started").write_text(json.dumps({"pid": 4242, "pgid": 4242}))
    (night / "evidence_processes.jsonl").write_text("")
    (night / "receipt.json").write_text(json.dumps({"plan_id": PLAN.plan_id, "conditions": [
        {"condition_id": "C5", "status": "PASS", "measured": {"payload_kind": "quiet_predicate_evidence"}}]}))
    # base order: prepare_result (:3414) writes the driver's abort document, then [K] in courier prelaunch (:1426)
    d._write_driver_refusal(night / "refusal.json", PLAN, d._CODES["aborted_agent_present"], "agent session present", {})
    d._evidence_cleanup_error(PLAN, night)
    print("R3c-BASE 3ad82b43 order:", [(p.name, json.loads(p.read_text())["refusal"]["reason"]) for p in d._refusal_paths(night)],
          "| evidence_outcome:", json.loads((night / "evidence_outcome.json").read_text())["outcome"])
