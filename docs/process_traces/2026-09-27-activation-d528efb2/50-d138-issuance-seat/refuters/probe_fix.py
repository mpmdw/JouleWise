import sys, json, subprocess
from pathlib import Path
from collections.abc import Mapping
ROOT = Path("/Users/edr/code/JouleWise-wt-d138-hold2-d528efb2"); sys.path.insert(0, str(ROOT))
import joulewise.arm_readiness as arm
import joulewise.calibration_bracketing as b
def fixed(tree):
    policy = tree.get("acceptance_policy")
    if not isinstance(policy, Mapping) or policy.get("selection") != "issued_d116_artifact_only":
        return False
    nested = policy.get("issued_acceptance")
    declared = {v for v in (policy.get("issued"),
                            nested.get("acceptance_id") if isinstance(nested, Mapping) else None,
                            policy.get("issued_artifact_id")) if v is not None}
    return (len(declared) == 1 and declared <= arm._ISSUED_D079_IDS
            and not declared & set(arm._CLAIM_HELD_ACCEPTANCE_IDS))
sel="issued_d116_artifact_only"; R7=b.ANCHOR_V3_R7_ACCEPTANCE_ID; H=b.EPOCH_25G83_R1_ACCEPTANCE_ID
cases={"issued=R7":{"selection":sel,"issued":R7},"issued=held":{"selection":sel,"issued":H},
 "issued=R7+nested held":{"selection":sel,"issued":R7,"issued_acceptance":{"acceptance_id":H}},
 "issued=R7+flat held":{"selection":sel,"issued":R7,"issued_artifact_id":H}}
for k,v in cases.items(): print("candidate", arm._issued_d079({"acceptance_policy":v}), "| sketch", fixed({"acceptance_policy":v}), "|", k)
files = subprocess.run(["git","-C",str(ROOT),"ls-files","configs/campaigns/*plan_tree.json"],capture_output=True,text=True).stdout.split()
for f in files:
    t=json.load(open(ROOT/f)); print("committed pack", f.split('/')[2], "candidate", arm._issued_d079(t), "sketch", fixed(t))
