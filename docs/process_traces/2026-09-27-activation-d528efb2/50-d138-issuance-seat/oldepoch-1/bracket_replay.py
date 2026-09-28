"""Read-only production bracket evaluation for one recorded 25F84 member."""
import json
import sys
from pathlib import Path

worktree, output = map(Path, sys.argv[1:3])
sys.path.insert(0, str(worktree))
from joulewise.calibration_bracketing import (  # noqa: E402
    calibration_bracket_for_bundles,
    load_calibration_acceptance_bound,
)
from joulewise.calibration_ledger import load_calibration_ledger_snapshot  # noqa: E402
from joulewise.schemas import CalibrationBracketingPolicy  # noqa: E402

runs = Path('/Users/edr/code/JouleWise/runs_window_7bfloor_20260729')
member = runs / 'sw7bfloor-df-ph-decode-abs-r01'
policy_data = json.loads((worktree / 'configs/campaign_policies/quiet_mac_p2_production.json').read_text())
policy = CalibrationBracketingPolicy.from_mapping(policy_data['calibration_bracketing'])
acceptance = load_calibration_acceptance_bound()
cutoff = acceptance.get('ledger_cutoff') if acceptance else None
snapshot = load_calibration_ledger_snapshot(
    ledger_path=Path('/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2/runs/calibration_observation_ledger.jsonl'),
    mode='read_replay',
    baseline_sequence=cutoff.get('sequence') if cutoff else None,
    baseline_digest=cutoff.get('head_digest') if cutoff else None,
)
bracket, reasons = calibration_bracket_for_bundles(
    runs, [member], policy, mode='read_replay', ledger_snapshot=snapshot,
)
result = {'measurement': str(member), 'bracket': bracket, 'reasons': list(reasons)}
output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(json.dumps({'status': bracket.get('status'), 'reasons': list(reasons)}))
raise SystemExit(0 if bracket.get('status') == 'passed' and not reasons else 1)
