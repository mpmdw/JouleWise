import sys
from pathlib import Path
ROOT = Path("/Users/edr/code/JouleWise-wt-d138-hold2-d528efb2"); sys.path.insert(0, str(ROOT))
import joulewise.calibration_bracketing as b
from scripts import mint_floor_artifact_generalized as g
core = g._fresh_original_core()
print("mint core loader is bracketing loader:", core.load_calibration_acceptance_bound is b.load_calibration_acceptance_bound)
print("mint core loader(held) ->", core.load_calibration_acceptance_bound(b.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH))
held = b.load_calibration_acceptance_bound(b.EPOCH_25G83_R1_ACCEPTANCE_BOUND_PATH, allow_claim_held=True)
print("allowance projection(held content) ->", b.issued_calibration_allowance_projection(held, pre_exact_bound_lexeme_s="0.030", post_exact_bound_lexeme_s="0.036"))
from joulewise import calibration_epoch_continuation as c
print("continuation registry:", dict(b.EPOCH_CONTINUATION_REGISTRY))
from scripts import epoch_equivalence_check as e, reissue_calibration_acceptance as r, issue_calibration_acceptance_generation as i, issue_epoch_continuation as ie
for m in (e, r, i):
    print(m.__name__, "loader is bracketing loader:", m.load_calibration_acceptance_bound is b.load_calibration_acceptance_bound)
print("issue_epoch_continuation acceptance_module loader:", ie.acceptance_module.load_calibration_acceptance_bound is b.load_calibration_acceptance_bound)
