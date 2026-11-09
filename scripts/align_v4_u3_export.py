#!/usr/bin/env python3
"""Lead export for the U3 bar (W1-BLOCKERS-AGREEMENT, lead rulings 1-11).

Builds the explicit ``pairs`` + ``policy`` input that ``align_v4_u3_bar.py``
derives from. Reads only the bundle directories named on the command line; no
discovery. Pilot replay energies are pilot data, not v4 outcomes (lead ruling).

policy-template  Write the ruled policy (beta .05, N = 22 after R25, f = 1.5) with the
                 three configuration/justification digests left to fill.
pilot            One prespecified pair per session (ruling 3). The selection file
                 lists each session's candidate replay pairs IN DESIGN ORDER; the
                 first candidate whose ordinals are >= 3 apart is selected BEFORE
                 any energy is read. If that pair is ineligible the session is
                 reported unavailable; it is never substituted.
r1               R1's adjacent D_spam a/b pair as the transfer screen (ruling 6).
assemble         pilot + r1 + policy -> pairs.json for ``align_v4_u3_bar.py --input``.

Outputs use exclusive creation. See docs/align/v4/W1-BLOCKERS-merged.md for the
machine and order of every command.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# R25 (pre-signature design change, the U3 bar is not signed yet): the roster expands PROSPECTIVELY to every
# window that can be run, including the six armable R24 reserve windows C9-C14, so the familywise false-fail
# budget (beta over N comparisons) holds for every possible comparison. N = W1 (30B 4 + D 1) + C1-C14 (D 1 each)
# + T1-T3 (D 1 each) = 5 + 14 + 3 = 22 (it was 16 = 5 + 8 + 3 before the reserve windows, RUN_STATE 226 R15).
ROSTER = {'W1': {'30B': 4, 'D': 1}, **{f'C{i}': {'30B': 0, 'D': 1} for i in range(1, 15)},
          **{f'T{i}': {'30B': 0, 'D': 1} for i in range(1, 4)}}
FILL = 'FILL_SHA256'


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _write_new(path, value):
    with Path(path).open('x') as f:
        f.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def policy_template():
    from joulewise.align.apple.v4_u3 import METHOD
    return {'method': METHOD, 'selection': 'one_prespecified_pair_per_session',
            'series_alpha': .05, 'd_transfer_factor': 1.5, 'checks_by_window': ROSTER,
            'r1_D_qualification': 'adjacent_matched_predecessor_screen_only',
            'd_configuration_sha256': FILL, 'r1_configuration_sha256': FILL,
            'transfer_justification_sha256': FILL, 'seed': 20261108, 'simulations': 20000}


def bundle_source_sha256(bundle):
    """Digest of the bundle files the energy and identity come from."""
    from joulewise.desk_compress import read_bytes
    parts = {}
    for name in ('config.json', 'metadata.json', 'outputs/align_episode.json', 'outputs/align_turns.jsonl'):
        try:
            parts[name] = _sha(read_bytes(Path(bundle) / name))
        except OSError:
            parts[name] = None
    return _sha(json.dumps(parts, sort_keys=True).encode())


def configuration_sha256(bundle):
    """cohort_identity fingerprint (model, observed stack, effective policy), as the desk binds it."""
    from joulewise.align.apple.v4_registration import cohort_identity
    from joulewise.align.apple.workload import EpisodeSpec, read_episode_bundle
    from joulewise.desk_compress import read_bytes
    config = json.loads(read_bytes(Path(bundle) / 'config.json'))
    spec = EpisodeSpec.from_text(config['workload_profile']['prompt_text'])
    runtime = read_episode_bundle(bundle).hardware.get('runtime_identity') or {}
    identity = cohort_identity(config, spec, runtime)
    return _sha(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode())


def measure_pair(early, late):
    """Desk estimator on two named bundles: energies, identity, clock and eligibility evidence."""
    from joulewise.align.apple.thermal_desk import read_bundle_record, energy_exclusions
    rows, reasons = [], []
    for bundle in (early, late):
        try:
            rows.append(read_bundle_record(Path(bundle)))
        except (OSError, ValueError, KeyError) as exc:
            reasons.append(f'{Path(bundle).name}: unreadable ({type(exc).__name__})')
            rows.append(None)
    if None in rows:
        return {'eligible': False, 'reasons': reasons}
    a, b = rows
    energies = [r.get('turn_owned_j') for r in rows]
    clocks = [r.get('decode_clock_mhz') for r in rows]
    clock = (abs(clocks[1] - clocks[0]) / ((clocks[0] + clocks[1]) / 2)
             if all(type(c) in (int, float) and c > 0 for c in clocks) else None)
    if a.get('tokens') is None or a.get('tokens') != b.get('tokens'):
        reasons.append('token identity unavailable or divergent')
    for r in rows:
        reasons += [f"{r['id']}: {c}" for c in (r.get('calibration_exclusions') or [])]
        reasons += [f"{r['id']}: {c}" for c in energy_exclusions(r)]
    if any(type(e) not in (int, float) or not math.isfinite(e) or e <= 0 for e in energies):
        reasons.append('energy unavailable')
    if clock is None or clock > .005:
        reasons.append('decode clock difference unavailable or above 0.5%')
    try:
        configs = [configuration_sha256(early), configuration_sha256(late)]
        if configs[0] != configs[1]:
            reasons.append('configuration identity differs within the pair')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        configs = [None, None]
        reasons.append(f'configuration identity unavailable ({type(exc).__name__})')
    return {'eligible': not reasons, 'reasons': reasons, 'energies_j': energies,
            'clock_difference_fraction': clock, 'token_identical': not any('token' in r for r in reasons),
            'configuration_sha256': configs[0],
            'source_sha256': _sha((bundle_source_sha256(early) + bundle_source_sha256(late)).encode())}


def pilot_pairs(selection):
    pairs, unavailable = [], []
    for session in selection['sessions']:
        name = session['session']
        chosen = next((c for c in session['candidates']
                       if c['ordinals'][1] - c['ordinals'][0] >= 3), None)   # design position only
        if chosen is None:
            unavailable.append({'session': name, 'reason': 'no candidate with ordinals >= 3 apart'})
            continue
        m = measure_pair(chosen['early_bundle'], chosen['late_bundle'])
        if not m['eligible']:
            unavailable.append({'session': name, 'ordinals': chosen['ordinals'], 'reasons': m['reasons']})
            continue
        pairs.append({'session': name, 'population': '30B', 'phase': 'pilot', 'ordinals': chosen['ordinals'],
                      'token_identical': True, 'eligible': True, 'energies_j': m['energies_j'],
                      'clock_difference_fraction': m['clock_difference_fraction'],
                      'configuration_sha256': m['configuration_sha256'], 'source_sha256': m['source_sha256']})
    return {'pairs': pairs, 'unavailable_sessions': unavailable,
            'selection_sha256': _sha(json.dumps(selection, sort_keys=True).encode())}


def r1_pair(early, late, ordinals):
    m = measure_pair(early, late)
    if not m['eligible']:
        # Ruling 6: a failed or missing screen leaves D U3 inconclusive; record why.
        return {'pairs': [], 'unavailable': m['reasons']}
    return {'pairs': [{'session': 'R1', 'population': 'D', 'phase': 'R1', 'qualification_only': True,
                       'ordinals': list(ordinals), 'token_identical': True, 'eligible': True,
                       'energies_j': m['energies_j'], 'clock_difference_fraction': m['clock_difference_fraction'],
                       'configuration_sha256': m['configuration_sha256'], 'source_sha256': m['source_sha256']}],
            'unavailable': []}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='command', required=True)
    t = sub.add_parser('policy-template')
    t.add_argument('--output', type=Path, required=True)
    s = sub.add_parser('pilot')
    s.add_argument('--selection', type=Path, required=True)
    s.add_argument('--output', type=Path, required=True)
    r = sub.add_parser('r1')
    r.add_argument('--early-bundle', type=Path, required=True, help='R1 D_spam a run bundle')
    r.add_argument('--late-bundle', type=Path, required=True, help='R1 D_spam b run bundle')
    r.add_argument('--ordinals', type=int, nargs=2, required=True, help='their R1 run positions, e.g. 2 3')
    r.add_argument('--output', type=Path, required=True)
    a = sub.add_parser('assemble')
    a.add_argument('--pilot', type=Path, required=True)
    a.add_argument('--r1', type=Path, required=True)
    a.add_argument('--policy', type=Path, required=True)
    a.add_argument('--output', type=Path, required=True)
    args = p.parse_args(argv)
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.command == 'policy-template':
        result = policy_template()
    elif args.command == 'pilot':
        result = pilot_pairs(json.loads(args.selection.read_bytes()))
    elif args.command == 'r1':
        result = r1_pair(args.early_bundle, args.late_bundle, args.ordinals)
    else:
        policy = json.loads(args.policy.read_bytes())
        if FILL in json.dumps(policy):
            raise ValueError('policy still has FILL_SHA256 placeholders')
        result = {'pairs': json.loads(args.pilot.read_bytes())['pairs'] + json.loads(args.r1.read_bytes())['pairs'],
                  'policy': policy}
    _write_new(args.output, result)
    if args.command in ('pilot', 'r1'):
        print(json.dumps({'pairs': len(result['pairs']),
                          'unavailable': result.get('unavailable_sessions', result.get('unavailable'))}, default=str))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
