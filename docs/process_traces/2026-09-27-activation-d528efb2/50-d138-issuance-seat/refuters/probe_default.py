import sys, json, copy
from pathlib import Path
from unittest.mock import patch
ROOT = Path("/Users/edr/code/JouleWise-wt-d138-final-d528efb2"); sys.path.insert(0, str(ROOT)); sys.dont_write_bytecode = True
import joulewise.calibration_bracketing as B
import joulewise.arm_readiness as A
from joulewise.calibration_epoch_continuation import acceptance_judged_epochs
new = B.load_calibration_acceptance_bound(); r7 = B.load_calibration_acceptance_bound(B.ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH)
e_new = dict(new["identity_epoch"]); e_r7 = dict(r7["identity_epoch"])
print("E0 new epoch", e_new["os_build"], "| R7 epoch", e_r7["os_build"], "| differing fields", [k for k in e_new if e_new[k]!=e_r7[k]])
print("E1 new judges", [dict(e)["os_build"] for e in acceptance_judged_epochs(new)], "| R7 judges", [dict(e)["os_build"] for e in acceptance_judged_epochs(r7)])
# admission
for name in sorted(p.name for p in (ROOT/"configs/campaigns").iterdir() if (p/"plan_tree.json").exists()):
    t = json.loads((ROOT/"configs/campaigns"/name/"plan_tree.json").read_text())
    pol = t.get("acceptance_policy", {}); ia = pol.get("issued_acceptance") or {}
    print("H pack", name, "declares", ia.get("acceptance_id") or pol.get("issued") or pol.get("issued_artifact_id"), "_issued_d079 ->", A._issued_d079(t))
for aid in (B.ANCHOR_V3_R7_ACCEPTANCE_ID, B.EPOCH_25G83_R1_ACCEPTANCE_ID):
    for shape in ({"issued": aid}, {"issued_acceptance": {"acceptance_id": aid}}, {"issued_artifact_id": aid}):
        print("H synthetic", aid[-10:], list(shape)[0], "->", A._issued_d079({"acceptance_policy": {"selection": "issued_d116_artifact_only", **shape}}))
# capture preflight (validate_powermetrics_fiducial) at a 25G83 machine: head vs main-equivalent (default = R7)
sys.modules.setdefault("mlx", type(sys)("mlx")); 
import importlib.util
spec = importlib.util.spec_from_file_location("vpf", ROOT/"scripts/validate_powermetrics_fiducial.py")
try:
    vpf = importlib.util.module_from_spec(spec); spec.loader.exec_module(vpf)
    try: print("PF head: preflight level screen at 25G83 ->", vpf._derive_preflight_systematic_screen_s(e_new))
    except vpf._AcceptancePreflightError as e: print("PF head refuses", e.reason)
    with patch.object(vpf, "DEFAULT_ACCEPTANCE_BOUND_PATH", B.ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH):
        try: print("PF main-equivalent (default=R7) at 25G83 ->", vpf._derive_preflight_systematic_screen_s(e_new))
        except vpf._AcceptancePreflightError as e: print("PF main-equivalent (default=R7) at 25G83 refuses:", e.reason, e.context.get("stale_fields"))
    print("PF module constant PREFLIGHT_SYSTEMATIC_SCREEN_S =", vpf.PREFLIGHT_SYSTEMATIC_SCREEN_S)
except Exception as ex:
    print("PF import failed", type(ex).__name__, ex)
