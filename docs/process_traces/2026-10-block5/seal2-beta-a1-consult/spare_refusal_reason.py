# Prints the absent invoked reference's child_refusal only if it is a token of a closed list in the code; else "present_other".
import sys, json
sys.path.insert(0, "/Users/edr/night-custody/desk/b5-harvest")
from pathlib import Path
from joulewise import campaign_provenance as cp, whole_window as ww
from joulewise import arm_readiness as ar
CLOSED = set(getattr(ar, "LAUNCH_LINEAGE_REASON_CODES", ()))
for plan in sys.argv[1:]:
    root = Path(json.load(open("/Users/edr/night-custody/%s/night_plan.json" % plan))["hazard_window"]["runs_roots"]["claim"])
    absent = set()
    for rec in cp.load_authenticated_campaign_catalog(root) or []:
        for m in rec.value["members"]:
            if m.get("execution") != "invoked": continue
            for b in m["bundle_ids"]:
                p = ww._safe_source_path(root, b)
                if p is not None and not p.is_dir(): absent.add(b)
    for row in cp.load_campaign_log_rows(root / "campaign_log.jsonl") or []:
        if row.get("run_id") in absent and "exit_code" in row:
            r = row.get("child_refusal")
            print(plan, "closed_list_size", len(CLOSED), "child_refusal",
                  r if r in CLOSED else ("absent" if r is None else "present_other"),
                  "status", row.get("status") if row.get("status") in {"ok","failed","timeout","drained","config_error","skipped","waived"} else "other",
                  "blocked_before_invoke", bool(row.get("blocked_before_invoke")))
