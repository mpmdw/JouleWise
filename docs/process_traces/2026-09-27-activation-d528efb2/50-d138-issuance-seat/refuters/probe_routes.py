import sys, json, hashlib
from pathlib import Path
ROOT = Path("/Users/edr/code/JouleWise-wt-d138-hold2-d528efb2")
sys.path.insert(0, str(ROOT))
import joulewise.calibration_bracketing as b
import joulewise.arm_readiness as arm
import joulewise.arm_readiness_evidence as ev

H = b.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH
HID = b.EPOCH_25G83_R1_ACCEPTANCE_ID
R7 = b.ANCHOR_V3_R7_ACCEPTANCE_ID
raw = H.read_bytes()
print("A1 held sha256", hashlib.sha256(raw).hexdigest())
print("A2 default loader id", (b.load_calibration_acceptance_bound() or {}).get("acceptance_id"))
print("A3 held path no kw", b.load_calibration_acceptance_bound(H))
print("A4 held path kw id", (b.load_calibration_acceptance_bound(H, allow_claim_held=True) or {}).get("acceptance_id"))
byp = b._acceptance_bound_from_authenticated_bytes(raw)
print("B1 _acceptance_bound_from_authenticated_bytes(held raw) ->", None if byp is None else byp.get("acceptance_id"))
print("B2 acceptance_generation_operatives(held id) ->", dict(b.acceptance_generation_operatives(HID) or {}))
print("B3 acceptance_bracket_screen_s(held id) ->", b.acceptance_bracket_screen_s(HID), b.acceptance_allowance_rule(HID))
# admission list
sel = "issued_d116_artifact_only"
cases = {
 "nested held only": {"selection": sel, "issued_acceptance": {"acceptance_id": HID}},
 "flat held only": {"selection": sel, "issued_artifact_id": HID},
 "issued=R7 + nested held": {"selection": sel, "issued": R7, "issued_acceptance": {"acceptance_id": HID}},
 "issued=R7 + flat held": {"selection": sel, "issued": R7, "issued_artifact_id": HID},
 "nested R7 acceptance_id but path=held": {"selection": sel, "issued_acceptance": {"acceptance_id": R7, "path": "configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json"}},
}
for k, v in cases.items():
    print("C", k, "-> _issued_d079 =", arm._issued_d079({"acceptance_policy": v}))
# evidence author ACCEPTANCE_OWNER with mixed key pack
rel = "configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json"
sha = hashlib.sha256(raw).hexdigest()
for label, policy in {
  "issued=R7 + nested held (path+sha)": {"selection": sel, "issued": R7,
      "issued_acceptance": {"acceptance_id": HID, "path": rel, "artifact_sha256": sha}},
  "issued=R7 + flat held": {"selection": sel, "issued": R7, "issued_artifact_id": HID, "issued_artifact_sha256": sha},
  "nested held only": {"selection": sel, "issued_acceptance": {"acceptance_id": HID, "path": rel, "artifact_sha256": sha}},
}.items():
    tree = {"acceptance_policy": policy}
    ctx = ev._DerivationContext(pack_root=ROOT/"configs/campaigns", repository=ROOT, tree=tree, pack_sha256="0"*64, head_commit="x")
    try:
        d = ev._derive_acceptance_owner(ctx)
        print("D", label, "admitted=", arm._issued_d079(tree), "ACCEPTANCE_OWNER facts=", json.dumps(d.facts), "checks=", json.dumps(d.checks))
    except Exception as e:
        print("D", label, "admitted=", arm._issued_d079(tree), "RAISED", type(e).__name__, getattr(e, "args", e))
    print("   successor row required?", not arm._issued_d079(tree))
