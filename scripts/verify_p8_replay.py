#!/usr/bin/env python3
"""Recorded raw-byte checks N-1/N-2 for CAP-COUNCIL-25G83-01-A2-E1.

Read-only against the retained corpus; no sampler or capture is started.
N-1 stops immediately on missing bytes, a refusal, or a changed member B.
N-2 uses the 38-record anchor baseline replayed for R7; member detection
admission is additionally established by N-1. Nonmembers are never added.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from joulewise import calibration_bracketing as bracket
from joulewise import powermetrics_fiducial as fiducial
from joulewise.uncertainty_evidence import CLOCK_METHOD_V3
from scripts.paper_anchor_correction_quantified import _derive_anchors, _rederive_under
from tests.verify_calibration_acceptance_corpus import EXPECTED_BY_ACCEPTANCE_ID

ARCHIVE = Path.home() / 'Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup'
R7_BASELINE_SHA256 = 'ec5172274ef0ab2d863eae7703c6845f79cdd0926330a29cfb8973aabdd6f469'


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_primary(directory: Path, expected_raw: str | None = None) -> tuple:
    evidence_raw = (directory / 'instrument_evidence.json').read_bytes()
    evidence = json.loads(evidence_raw)
    expected = evidence['artifact_sha256']['raw/powermetrics.plist']
    if expected_raw is not None and expected_raw != expected:
        raise ValueError('baseline raw digest differs from authenticated evidence')
    candidates = [directory / 'raw/powermetrics.plist']
    # Duplicate small-evidence bundles can have pruned raw directories.
    # Search every local copy by hash before consulting the archive.
    candidates.extend(sorted(directory.parents[2].glob(
        f'runs*/instrument_validation/{directory.name}/raw/powermetrics.plist')))
    candidates.extend(sorted(ARCHIVE.glob(
        f'*/instrument_validation/{directory.name}/raw/powermetrics.plist')))
    candidates.extend(sorted(ARCHIVE.glob(
        f'*/runs/instrument_validation/{directory.name}/raw/powermetrics.plist')))
    for path in candidates:
        if path.is_file():
            raw = path.read_bytes()
            if sha(raw) == expected:
                events = (directory / 'events.jsonl').read_bytes()
                if sha(events) != evidence['artifact_sha256']['events.jsonl']:
                    raise ValueError('events digest mismatch')
                return evidence_raw, evidence, events, raw, path
    raise FileNotFoundError(f'{directory.name}: no raw bytes matching {expected}')


def statistics(members: list[dict]) -> dict:
    values = [(r['member_id'], Decimal(r['replayed_b_fiducial_s'])) for r in members]
    low, high = min(values, key=lambda v: v[1]), max(values, key=lambda v: v[1])
    with localcontext() as ctx:
        ctx.prec = 80
        mean = sum((v for _, v in values), Decimal(0)) / len(values)
        sd = (sum((v - mean) ** 2 for _, v in values) / (len(values) - 1)).sqrt()
        q = Decimal('0.000000000000000001')
        return dict(n=len(values), minimum_s=low[1], minimum_member_id=low[0],
                    maximum_s=high[1], maximum_member_id=high[0], range_s=high[1]-low[1],
                    mean_s=mean.quantize(q, rounding=ROUND_HALF_EVEN),
                    sample_sd_s=sd.quantize(q, rounding=ROUND_HALF_EVEN))


def check_members(root: Path, artifact: dict) -> dict:
    rows = []
    report = {'check': 'N-1', 'estimator_code_sha256': bracket._current_estimator_code_sha256(),
              'cap': fiducial.DETECTION_PROJECTION_CELL_BUDGET, 'members': rows, 'result': 'STOP'}
    for member in artifact['derivation_corpus']['members']:
        row = {'member_id': member['member_id'], 'stored_b_fiducial_s': member['b_fiducial_s']}
        rows.append(row)
        try:
            directory = root / member['source_directory']
            ev_raw, ev, events, raw, path = load_primary(directory)
            if sha(ev_raw) != member['instrument_evidence_sha256']:
                raise ValueError('R7 evidence digest mismatch')
            if sha((directory / 'manifest.json').read_bytes()) != member['manifest_sha256']:
                raise ValueError('R7 manifest digest mismatch')
            row.update(bytes_source='archive' if path.is_relative_to(ARCHIVE) else 'local',
                       raw_path=str(path), raw_sha256=sha(raw), events_sha256=sha(events))
            derived = _rederive_under(raw, events, ev['clock_anchor'], CLOCK_METHOD_V3)
            row['detection'] = derived
            row['replayed_b_fiducial_s'] = str(derived['b_fiducial_s'])
            row['result'] = ('EQUAL' if derived.get('admissible') and
                             row['replayed_b_fiducial_s'] == member['b_fiducial_s'] else 'DIFF')
        except (OSError, ValueError, KeyError) as exc:
            row.update(result='NOT_EXECUTED', error=str(exc))
        print(json.dumps(row, sort_keys=True), flush=True)
        if row['result'] != 'EQUAL':
            return report
    observed = statistics(rows)
    expected = {k: v for k, v in EXPECTED_BY_ACCEPTANCE_ID[artifact['acceptance_id']].items()
                if k != 'stored_lexeme_is_member_value'}
    report['statistics'] = {k: str(v) if isinstance(v, Decimal) else v for k, v in observed.items()}
    report['statistics_equal'] = observed == expected
    # The preserved decimal derivation and registered operatives are validated
    # independently by the production validator, rather than redefined here.
    report['r7_valid_acceptance_bound'] = bracket._valid_acceptance_bound(artifact)
    report['result'] = 'PASS' if observed == expected and report['r7_valid_acceptance_bound'] else 'STOP'
    return report


def check_corpus(root: Path, artifact: dict, baseline_path: Path, n1_path: Path) -> dict:
    baseline_raw = baseline_path.read_bytes()
    if sha(baseline_raw) != R7_BASELINE_SHA256:
        raise ValueError('N-2 baseline differs from the frozen R7 corpus')
    baseline = json.loads(baseline_raw)
    n1 = json.loads(n1_path.read_text())
    if len(baseline) != 38 or n1['result'] != 'PASS':
        raise ValueError('N-2 requires the R7 38-record baseline and passed N-1')
    if n1['estimator_code_sha256'] != bracket._current_estimator_code_sha256():
        raise ValueError('N-1 estimator pins changed')
    members = {m['member_id'] for m in artifact['derivation_corpus']['members']}
    directories = {p.parent.name: p.parent for p in sorted(root.glob(
        'runs_window_*/instrument_validation/*/instrument_evidence.json'))}
    rows, newly_completed = [], []
    for vid, expected in sorted(baseline.items()):
        row = {'member_id': vid, 'is_member': vid in members}
        rows.append(row)
        try:
            _, ev, events, raw, path = load_primary(directories[vid], expected['raw_sha256'])
            anchor = _derive_anchors(raw, ev['clock_anchor'])['v3']
            row.update(raw_path=str(path), raw_sha256=sha(raw), v3=anchor,
                       anchor_equal=anchor == expected['v3'])
            if vid in members:
                row['disposition_equal'] = next(r for r in n1['members'] if r['member_id'] == vid)['result'] == 'EQUAL'
            else:
                # The R7 baseline banks anchors, not nonmember B values.
                # N-2 requires full detection disposition equality for MEMBERS
                # (N-1), and disclosure of any recorded nonmember cap stop
                # that now completes. No recorded stop is silently promoted.
                old_reasons = ev.get('reasons') or []
                recorded_cap_stop = any(
                    token in str(reason) for reason in old_reasons
                    for token in ('detection_nonconvergent', 'projection_nonconvergent'))
                row['recorded_nonmember_cap_stop'] = recorded_cap_stop
                if recorded_cap_stop:
                    new = _rederive_under(raw, events, ev['clock_anchor'], CLOCK_METHOD_V3)
                    row['new_cap_detection'] = new
                    if new.get('admissible'):
                        newly_completed.append(vid)
                row['disposition_equal'] = anchor['status'] == expected['v3']['status']
            # Nonmember cap admission changes are disclosed, never membership.
            row['result'] = 'EQUAL' if row['anchor_equal'] and (row['disposition_equal'] or vid in newly_completed) else 'DIFF'
        except (OSError, ValueError, KeyError) as exc:
            row.update(result='NOT_EXECUTED', error=str(exc))
        print(json.dumps(row, sort_keys=True), flush=True)
    return {'check': 'N-2', 'baseline_sha256': sha(baseline_path.read_bytes()),
            'estimator_code_sha256': bracket._current_estimator_code_sha256(),
            'members': rows, 'nonmembers_newly_completed': newly_completed,
            'result': 'PASS' if all(r['result'] == 'EQUAL' for r in rows) else 'STOP'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('check', choices=['members', 'corpus'])
    parser.add_argument('--corpus-root', type=Path, default=Path('/Users/edr/code/JouleWise'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, default=ROOT / 'scripts/p8_evidence/r7_corpus_baseline.json')
    parser.add_argument('--n1', type=Path, default=ROOT / 'scripts/p8_evidence/n1.json')
    args = parser.parse_args()
    artifact = bracket.load_calibration_acceptance_bound(bracket.ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH)
    if artifact is None:
        raise ValueError('R7 failed registry authentication')
    pins = bracket._current_estimator_code_sha256()
    report = (check_members(args.corpus_root, artifact) if args.check == 'members' else
              check_corpus(args.corpus_root, artifact, args.baseline, args.n1))
    if pins != bracket._current_estimator_code_sha256():
        report['result'] = 'STOP'
        report['error'] = 'estimator pins changed during replay'
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f"{report['check']}={report['result']} records={len(report['members'])}", flush=True)
    return 0 if report['result'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
