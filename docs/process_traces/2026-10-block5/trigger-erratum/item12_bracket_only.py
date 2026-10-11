"""Erratum 3 item 12: the bracket evaluation alone over a not-governed attempt's archived
ledger copy, terminal pin and binding.  EXPLORATORY; prints status words, reason codes,
trigger names, the doubling count and ledger sequences only.  Changes nothing."""
import json, sys
from pathlib import Path
archive, clone = Path(sys.argv[1]), Path(sys.argv[2])
from joulewise import calibration_bracketing as B
from joulewise.calibration_ledger import load_calibration_ledger_snapshot
from joulewise.schemas import CampaignPolicy
print("program:", B.__file__)
acc = B.load_calibration_acceptance_bound(clone / "configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json")
cut = acc["ledger_cutoff"]
snap = load_calibration_ledger_snapshot(
    archive / "sources/ledger/calibration_observation_ledger.jsonl", archive / "derived/terminal-pin.json",
    require_committed_pin=False, verify_custody=False, mode="issuing", repo_root=clone,
    baseline_sequence=cut["sequence"], baseline_digest=cut["head_digest"])
print("snapshot refusals:", sorted(map(str, snap.refusal_reasons)), "head sequence:", getattr(snap, "head_sequence", None))
binding = json.loads((archive / "derived/bracket-binding.json").read_text())
tree = json.loads((clone / "configs/campaigns" / sys.argv[3] / "plan_tree.json").read_text())
policy = CampaignPolicy.from_mapping(json.loads((clone / tree["campaign_policy"]["path"]).read_text()))
members = json.loads((archive / "withheld/member-assessments.json").read_text())["members"]
runs_root = Path(binding["runs_root"])
valid = [Path(r["bundle_path"]) for _, r in sorted(members.items())
         if r.get("strict_valid") and r.get("status") == "succeeded" and r.get("anchor_recorded") == "bounded"
         and str(r["bundle_path"]).startswith(str(runs_root) + "/")]
print("members passed to the evaluation:", len(valid))
for scope in ("sealed", "window_evidence"):
    a, reasons = B.calibration_bracket_for_bundles(
        runs_root, valid, policy.calibration_bracketing, mode="issuing", ledger_snapshot=snap,
        bracket_binding=binding, bracket_window_id=binding["window_id"], bracket_plan_id=binding["plan_id"],
        bracket_plan_sha256=binding["plan_sha256"], bracket_evidence_root_id=binding["evidence_root_id"],
        trigger_scope=scope)
    acc_r = a.get("acceptance") or {}
    pr = acc_r.get("prospective_rederivation") or {}
    print(json.dumps({"scope": scope, "status": a.get("status"), "reasons": sorted(map(str, reasons)),
                      "freshness": (acc_r.get("freshness") or {}).get("status"),
                      "observed_triggers": pr.get("observed_triggers"),
                      "recorded_only_triggers": pr.get("recorded_only_triggers"),
                      "corpus_doubling": pr.get("corpus_doubling"),
                      "other_session_systematic_sequences": pr.get("other_session_systematic_sequences")}))
