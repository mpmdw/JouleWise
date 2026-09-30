#!/usr/bin/env python3
"""Recorded P8 pin-delta issuance, CAP-COUNCIL-25G83-01-A2-E1 §3.1 i–xi.

Run --issue-only to prepare bytes before wiring; after the registry,
generation row and verify table are wired, run without it for checks x–xi.
Existing output must reproduce exactly; no differing artifact is overwritten.
This does not use the re-issue tool's main path or its copied-value semantics.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from joulewise import calibration_bracketing as bracket
from joulewise.powermetrics_fiducial import DETECTION_PROJECTION_CELL_BUDGET
from scripts.reissue_calibration_acceptance import build_member_delta_report
from tests.verify_calibration_acceptance_corpus import verify

P8_ID = 'd079_calibration_acceptance_v2_n17_r8'
P8_PATH = ROOT / 'configs/calibration/calibration_acceptance_d079_v2_n17_r8.json'
# Step 5 freeze, cap commit 34bfea7c90226509df661c2437eec74228152caa.
FROZEN_ESTIMATOR_SHA256 = {
    'joulewise/powermetrics_fiducial.py': 'bcdfeec06a03525cc6f6c700f2e2e6d10341af1323e4f9355b68ee47eb5bd30c',
    'joulewise/uncertainty_evidence.py': 'b583f35affb33394532424295ac70261b895e1b6f2faa6ec87ee89c79cd94ae8',
    'joulewise/adapters/powermetrics.py': '70f47086b2445e88d0cb25ed2d47751dfd99843d0cf1e149f2fe630c5116e5e4',
    'joulewise/reduce.py': '7b9c0d28869040229e113ea2d40ecc69966075fd34052fbb51cfaffbd9ff9fcc',
}


def encode_pin_delta(old_raw: bytes, old: dict, new: dict) -> bytes:
    """Replace only authorized JSON token spans; carry every other byte."""
    text = old_raw.decode('utf-8')
    decoder = json.JSONDecoder()
    spans = {}

    def whitespace(index):
        while index < len(text) and text[index].isspace():
            index += 1
        return index

    def walk(index, path):
        index = whitespace(index)
        first = index
        if text[index] == '{':
            index = whitespace(index + 1)
            while text[index] != '}':
                key, index = decoder.raw_decode(text, index)
                index = whitespace(index)
                if text[index] != ':':
                    raise ValueError('invalid JSON colon')
                index = whitespace(walk(index + 1, (*path, key)))
                if text[index] == ',':
                    index = whitespace(index + 1)
                else:
                    break
            index += 1
        elif text[index] == '[':
            index = whitespace(index + 1)
            count = 0
            while text[index] != ']':
                index = whitespace(walk(index, (*path, str(count))))
                count += 1
                if text[index] == ',':
                    index = whitespace(index + 1)
                else:
                    break
            index += 1
        else:
            _, index = decoder.raw_decode(text, index)
        spans[path] = (first, index)
        return index

    walk(0, ())
    replacements = {
        ('acceptance_id',): json.dumps(new['acceptance_id']),
        ('derivation_sha256',): json.dumps(new['derivation_sha256']),
        ('derivation_notes',): json.dumps(new['derivation_notes'], indent=2,
                                        ensure_ascii=False).replace('\n', '\n  '),
    }
    for key, value in new['prospective_rederivation']['estimator_code_sha256'].items():
        if old['prospective_rederivation']['estimator_code_sha256'][key] != value:
            replacements[('prospective_rederivation', 'estimator_code_sha256', key)] = json.dumps(value)
    for path, replacement in sorted(replacements.items(), key=lambda item: spans[item[0]][0], reverse=True):
        first, last = spans[path]
        text = text[:first] + replacement + text[last:]
    if json.loads(text) != new:
        raise ValueError('byte-preserving serialization changed the document')
    return text.encode('utf-8')


def digest(value: dict) -> None:
    value['derivation_sha256'] = bracket._canonical_sha256(
        {k: v for k, v in value.items() if k != 'derivation_sha256'})


def recursive_diff(old, new, path=()) -> list[str]:
    if type(old) is not type(new):
        return ['/'.join(path)]
    if isinstance(old, dict):
        out = []
        for key in sorted(old.keys() | new.keys()):
            if key not in old or key not in new:
                out.append('/'.join((*path, key)))
            else:
                out.extend(recursive_diff(old[key], new[key], (*path, key)))
        return out
    if isinstance(old, list):
        if len(old) != len(new):
            return ['/'.join(path)]
        return [p for i, (a, b) in enumerate(zip(old, new))
                for p in recursive_diff(a, b, (*path, str(i)))]
    return [] if old == new else ['/'.join(path)]


def build_p8() -> tuple[dict, dict, list[str]]:
    # i: the production loader authenticates the retained R7 file pin.
    old = bracket.load_calibration_acceptance_bound(bracket.ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH)
    if old is None:
        raise ValueError('R7 failed registry authentication')
    # ii–iv: only the four frozen pins, then the canonical derivation digest.
    new = deepcopy(old)
    pins = bracket._current_estimator_code_sha256()
    if pins != FROZEN_ESTIMATOR_SHA256 or DETECTION_PROJECTION_CELL_BUDGET != 1710000:
        raise ValueError('estimator freeze/cap differs from the recorded cap head')
    previous = old['prospective_rederivation']['estimator_code_sha256']
    rotated = {k: {'predecessor': previous[k], 'reissued': pins[k]}
               for k in pins if pins[k] != previous[k]}
    new['prospective_rederivation']['estimator_code_sha256'] = dict(pins)
    digest(new)
    # v: run BEFORE changing either the identity or the notes.
    delta = build_member_delta_report(old, new)
    print('PIN_DELTA_REPORT=' + json.dumps(delta, sort_keys=True))
    if (delta['verdict'] != 'PROCEED' or delta['changed_pin_count'] != len(rotated)
            or not all(delta[k]['identical'] for k in ['member_set', 'thresholds', 'science_facing'])):
        raise ValueError('STOP: tool-shaped pin delta is not neutral')
    # vi–viii: the approved identity and the allowed notes, then the digest.
    new['acceptance_id'] = P8_ID
    notes = new['derivation_notes']
    notes['predecessor'] = {
        'acceptance_id': old['acceptance_id'],
        'relative_path': bracket.ISSUED_ACCEPTANCE_REGISTRY[old['acceptance_id']]['relative_path'],
        'file_sha256': bracket.ANCHOR_V3_R7_ACCEPTANCE_BOUND_SHA256,
        'derivation_sha256': old['derivation_sha256'],
        'relationship': ('retained byte-identical forever as the anchor-v3 generation issued at the '
                         'clock-anchor v3.1 head; P8 supersedes r7 only as the LIVE generation and '
                         'differs from it in governed estimator pins alone'),
    }
    notes['generation'] = ('P8: SCIENCE-NEUTRAL cap-transaction pin reissue of '
        'd079_calibration_acceptance_v2_n17_r7 under CAP-COUNCIL-25G83-01 addendum A2 '
        'and erratum E1. Build 25F84, all 17 members and all operative numbers are retained. '
        'Only joulewise/powermetrics_fiducial.py rotates; the other three frozen pins are unchanged.')
    notes['reissue_delta'] = {
        'kind': 'estimator_pin_rotation_only', 'changed_estimator_pins': rotated,
        'science_neutrality_evidence': (
            'Recorded checks: scripts/p8_evidence/n1.json (all 17 raw-byte member replays '
            'and the five n17 statistics); scripts/p8_evidence/n2.json (the R7 38-record '
            'anchor/disposition replay and disclosure of any newly completing nonmember); '
            'scripts/p8_evidence/issuance.stdout.txt (tool-shaped delta PROCEED, '
            'production validator True, PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK and N-3 recursive diff). '
            'The recorded scripts are scripts/verify_p8_replay.py and scripts/issue_p8_pin_delta.py.'),
    }
    notes['cap_change'] = {
        'cap_in_force': DETECTION_PROJECTION_CELL_BUDGET,
        'historical_member_derivation_cap': 165000,
        'member_largest_need': 137535,
        'note': ('The 1,710,000-cell cap in force is the CAP-RULE-25G83-1 value recorded '
            'at the frozen cap head, versus 165,000 under which these members were derived. '
            'Their largest need, 137,535, lies under both. Historical derivation_method fields, '
            'including governed_projection_cell_budget = 165000, budget_ruling and '
            'budget_probe_status, are retained byte-identical as a record of how the members '
            'were derived and are not statements about the code in force. Addendum A1 §3 B2 '
            'overruled the August admission ruling those fields describe. P8 asserts nothing '
            'about how any capture other than its 17 members, including the validation-only '
            'probe 20260818T182149-a7e8b412, behaves under the cap in force. Any roster replay '
            'result belongs in the replay record.'),
    }
    notes['measurement_licence'] = ('P8 licenses no measurement at 25G83. A claim-bearing '
        'window at 25F84 under P8 requires a council ruling first, because the admitted '
        'population under the enlarged cap has not been validated at that build. '
        'issuance.claim_eligible is retained true as a property of the file, inert at 25G83.')
    digest(new)
    # xi: recursive diff excluding only the expressly permitted notes.
    paths = recursive_diff({k: v for k, v in old.items() if k != 'derivation_notes'},
                           {k: v for k, v in new.items() if k != 'derivation_notes'})
    expected = sorted(['acceptance_id', 'derivation_sha256'] +
        ['prospective_rederivation/estimator_code_sha256/' + k for k in rotated])
    if sorted(paths) != expected:
        raise ValueError(f'Unexpected N-3 difference: {paths}')
    return new, delta, paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--issue-only', action='store_true')
    parser.add_argument('--corpus-root', type=Path, default=Path('/Users/edr/code/JouleWise'))
    args = parser.parse_args()
    artifact, _, paths = build_p8()
    # ix: publish reproducible bytes; wiring is a separate reviewed source edit.
    old = bracket.load_calibration_acceptance_bound(bracket.ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH)
    payload = encode_pin_delta(bracket.ANCHOR_V3_R7_ACCEPTANCE_BOUND_PATH.read_bytes(), old, artifact)
    if P8_PATH.exists():
        if P8_PATH.read_bytes() != payload:
            raise ValueError('Existing P8 differs; refusing overwrite')
    else:
        with P8_PATH.open('xb') as handle:
            handle.write(payload)
    print('P8_FILE_SHA256=' + hashlib.sha256(payload).hexdigest())
    print('P8_DERIVATION_SHA256=' + artifact['derivation_sha256'])
    if not args.issue_only:
        for name in ('n1', 'n2'):
            evidence_path = ROOT / f'scripts/p8_evidence/{name}.json'
            evidence = json.loads(evidence_path.read_text())
            if (evidence['result'] != 'PASS' or
                    evidence['estimator_code_sha256'] != FROZEN_ESTIMATOR_SHA256):
                raise ValueError(f'{name} is not passed under the frozen estimator pins')
            print(name.upper() + '_EVIDENCE_SHA256=' + hashlib.sha256(evidence_path.read_bytes()).hexdigest())
        # x: no temporary registry patches: check the actual shipping wiring.
        if not bracket._valid_acceptance_bound(artifact):
            raise ValueError('_valid_acceptance_bound(P8) is False')
        if bracket.load_calibration_acceptance_bound() != artifact:
            raise ValueError('P8 is not the authenticated active default')
        print('_valid_acceptance_bound(P8)=True')
        verify(args.corpus_root, P8_PATH)
    print('N3_RECURSIVE_DIFF=' + json.dumps(paths))
    print('P8_PIN_DELTA=' + ('ISSUED_WIRING_CHECK_PENDING' if args.issue_only else 'PASS'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
