"""Compare WI-13's issuer with its saved baseline using the real, old W1/W2.

Only candidate outputs below --scratch are written. No new-window B is read.
Run with python3 -B -m tests.replay_wi13_rev5 --baseline <saved issuer.py>
--scratch <empty scratch directory>.
"""

import argparse
import hashlib
import json
from pathlib import Path
import types

from scripts import issue_calibration_acceptance_generation as issuer


ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = Path("/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    args = parser.parse_args()
    args.scratch.mkdir(parents=True, exist_ok=False)
    baseline = types.ModuleType("wi13_issuer_baseline")
    # Keep both tools' repo-relative pins and source paths identical; only
    # their source bytes differ. No write to a real checkout or its metadata.
    baseline.__file__ = str(ROOT / "scripts/issue_calibration_acceptance_generation.py")
    import sys
    sys.modules[baseline.__name__] = baseline
    exec(compile(args.baseline.read_bytes(), str(args.baseline), "exec"), baseline.__dict__)
    prereg = RUN_ROOT / "configs/calibration/preregistration_d079_epoch_25g83_rev1.md"
    argv = [
        "prepare-candidate", "--ledger", str(RUN_ROOT / "runs/calibration_observation_ledger.jsonl"),
        "--head-pin", str(RUN_ROOT / "configs/calibration/calibration_ledger_head.json"),
        "--repo-root", str(RUN_ROOT), "--preregistration", str(prereg),
        "--preregistration-sha256", hashlib.sha256(prereg.read_bytes()).hexdigest(),
        "--predecessor-acceptance", "configs/calibration/calibration_acceptance_d079_v2_n17_r7.json",
        "--registration-session-id", "d079-epoch-25g83-derivation-w1-20260927",
        "--registration-session-id", "d079-epoch-25g83-derivation-w2-20260927",
        "--d125-ruling", "docs/decision_log.md, D-125 addendum (2026-09-25): Revision 5 screen and ceiling for epoch 25G83/v3 (ACCEPTANCE-25G83-02 §5 R5(i), R9)",
        "--corpus-root", "/Users/edr/night-custody",
    ]
    outputs = []
    for name, tool in (("baseline", baseline), ("current", issuer)):
        path = args.scratch / (name + ".json")
        parsed = tool.build_parser().parse_args(argv + ["--out", str(path)])
        status = tool.prepare_candidate(parsed)
        if status:
            raise SystemExit(f"{name} refused with exit {status}")
        outputs.append(path.read_bytes())
    assert outputs[0] == outputs[1], "WI-13 changed Revision 5 candidate bytes"
    candidate = json.loads(outputs[1])
    assert candidate["derivation_corpus"]["n"] == 12
    assert candidate["registered_generation_row"]["registration_revision"] == 5
    print("WI13_W1W2_REPLAY=PASS byte_identical=true n=12 sha256=" + hashlib.sha256(outputs[1]).hexdigest())


if __name__ == "__main__":
    main()
