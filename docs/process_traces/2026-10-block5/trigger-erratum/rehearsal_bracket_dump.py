"""Before/after on the real rehearsal copy (not a claim window): the full bracket assessment as canonical JSON."""
import json, sys, inspect
from pathlib import Path
archive, clone, pack, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
scope = sys.argv[5] if len(sys.argv) > 5 else None
from joulewise import calibration_bracketing as B
from joulewise.calibration_ledger import load_calibration_ledger_snapshot
from joulewise.schemas import CampaignPolicy
acc = B.load_calibration_acceptance_bound(clone / "configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json")
cut = acc["ledger_cutoff"]
snap = load_calibration_ledger_snapshot(
    archive / "sources/ledger/calibration_observation_ledger.jsonl", archive / "derived/terminal-pin.json",
    require_committed_pin=False, verify_custody=False, mode="issuing", repo_root=clone,
    baseline_sequence=cut["sequence"], baseline_digest=cut["head_digest"])
binding = json.loads((archive / "derived/bracket-binding.json").read_text())
tree = json.loads((clone / "configs/campaigns" / pack / "plan_tree.json").read_text())
policy = CampaignPolicy.from_mapping(json.loads((clone / tree["campaign_policy"]["path"]).read_text()))
members = json.loads((archive / "withheld/member-assessments.json").read_text())["members"]
runs_root = Path(binding["runs_root"])
valid = [Path(r["bundle_path"]) for _, r in sorted(members.items())
         if r.get("strict_valid") and r.get("status") == "succeeded" and r.get("anchor_recorded") == "bounded"
         and str(r["bundle_path"]).startswith(str(runs_root) + "/")]
kw = {"trigger_scope": scope} if scope else {}
a, reasons = B.calibration_bracket_for_bundles(
    runs_root, valid, policy.calibration_bracketing, mode="issuing", ledger_snapshot=snap,
    bracket_binding=binding, bracket_window_id=binding["window_id"], bracket_plan_id=binding["plan_id"],
    bracket_plan_sha256=binding["plan_sha256"], bracket_evidence_root_id=binding["evidence_root_id"], **kw)
out.write_text(json.dumps({"assessment": a, "reasons": list(reasons), "members": len(valid)}, sort_keys=True, indent=1))
print(Path(B.__file__).parents[1].name, "scope", scope, "snapshot refusals", sorted(map(str, snap.refusal_reasons)),
      "members", len(valid), "status", a.get("status"), "reasons", sorted(map(str, reasons)),
      "freshness", ((a.get("acceptance") or {}).get("freshness") or {}).get("status"))
