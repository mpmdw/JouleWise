#!/usr/bin/env python3
"""Additive thermal desk: explicit bundle manifest in, PILOT.json + desk out.

No discovery, calibration refit, measurement launch, or v3 desk alteration.
Manifest members carry bundle, window, identical_work_group and contrast tags.
Optional os_journal/temperature_journal name explicit JSONL evidence files.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align.apple.thermal_desk import (read_bundle_record, window_report,
                                                markdown_report, session_desk_evidence)
from joulewise.align.apple import v4_registration as registration


def registration_evidence(directory):
    try:
        bar = json.loads((directory/'u3_bar.json').read_bytes())
    except (OSError, ValueError) as exc:
        raise ValueError('v4 desk requires registered u3_bar.json') from exc
    registration.validate_u3(bar)
    wp19 = json.loads((directory/'wp19_receipt.json').read_bytes())
    registration.validate_wp19(wp19)
    return bar, wp19


def contrast_predeclaration(wp19, policy):
    reasons = [wp19.get('contrast_predeclared'), (policy.get('contrast_fit') or {}).get('predeclared')]
    return '; '.join(r for r in reasons if r) or None


def r1_soak_c(directory):
    from joulewise.align.apple.r1_runtime import read_soak_reference, reference_c
    inputs = json.loads((directory/'inputs.json').read_bytes())
    return reference_c(read_soak_reference(directory/'r1_soak_reference.json'),
                       inputs['R1']['thermal_policy']['sensors'])


def enrich_record(record, bundle, *, episode=None):
    """V4-only metadata from immutable bundle bytes, never manifest overrides."""
    from joulewise.align.apple.workload import read_episode_bundle, EpisodeSpec
    from joulewise.align.apple.diagnostics import cache_statistics
    from joulewise.desk_compress import read_bytes
    ep = read_episode_bundle(bundle) if episode is None else episode
    config = json.loads(read_bytes(Path(bundle)/'config.json'))
    spec = EpisodeSpec.from_text(config['workload_profile']['prompt_text'])
    turns = [json.loads(line) for line in read_bytes(Path(bundle)/'outputs/align_turns.jsonl').splitlines() if line.strip()]
    thermal = ep.hardware.get('thermal') or {}
    record['cohort_identity'] = registration.cohort_identity(config, spec, ep.hardware.get('runtime_identity') or {})
    record.update(configuration={k: getattr(spec, k) for k in
        ('max_episode_decode_tokens', 'deadman_s', 'max_tokens', 'max_turns')},
        status='incomplete' if ep.hardware.get('token_budget', {}).get('incomplete', True) else 'completed',
        turns=len(ep.turns), x_flags=list(record.get('calibration_exclusions', [])),
        cache_statistics=cache_statistics(turns), window_reference=thermal.get('window_reference'),
        admission_slow_c=record.get('g0_slow_c'),
        g1_wait_s_by_turn=[sum(i.get('duration_s', 0) for i in record['intervals']
                             if i['kind'] == 'G1' and i.get('turn') == t.index) for t in ep.turns])
    return record


def enriched_bundle_record(bundle, **kwargs):
    """Share one immutable decode within this read only; no cross-run cache."""
    from joulewise.align.apple.workload import read_episode_bundle
    episode = read_episode_bundle(bundle)
    return enrich_record(read_bundle_record(bundle, episode=episode, **kwargs), bundle, episode=episode)


def _manifest_member(task):
    root, item = task
    def journal(name):
        return [json.loads(line) for line in (root/name).read_text().splitlines() if line.strip()]
    kwargs = {k: journal(item[k]) for k in ('os_journal', 'temperature_journal') if k in item}
    if 'registered_span_ns' in item:
        kwargs['registered_span_ns'] = item['registered_span_ns']
    try:
        record = enriched_bundle_record(root/item['bundle'], **kwargs)
    except FileNotFoundError as exc:
        record = {'id': item.get('id', Path(item['bundle']).name),
                  'model': item.get('model'), 'gated': item.get('gated', False),
                  'flags': ['member.artifact_missing', f'member.runtime_failure:{exc.filename}'],
                  'calibration_exclusions': ['member.runtime_failure'],
                  'intervals': [], 'tokens': None}
    record.update({k: item[k] for k in ('window', 'identical_work_group', 'compare_reference_id', 'template', 'arm',
                                      'ordinal', 'role', 'stage') if k in item})
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='new desk directory')
    parser.add_argument('--registration-dir', type=Path, default=ROOT/registration.REGISTRATION)
    parser.add_argument('--compare-session', type=Path, action='append', default=[],
                        metavar='PILOT.json', help='repeat for the K-session desk read')
    parser.add_argument('--workers', type=int, default=1, help='1 (serial reference) through 8 read workers')
    parser.add_argument('--profile', type=Path, help='separate stage timing receipt')
    args = parser.parse_args(argv)
    from joulewise.align.apple.desk_execution import DeskExecution, host_desk_guard
    with host_desk_guard(args.workers), DeskExecution(args.workers, args.profile) as execution:
        return _main(args, execution)


def _main(args, execution):
    bar, wp19 = registration_evidence(args.registration_dir)
    policy = json.loads((args.registration_dir/'inputs.json').read_bytes())['R1']['thermal_policy']
    manifest = json.loads(args.manifest.read_text())
    root = args.manifest.resolve().parent
    members = execution.map('thermal.members', _manifest_member,
                            ((root, item) for item in manifest['members']))
    by_id = {m['id']: m for m in members}
    for item, record in zip(manifest['members'], members):
        reference_id = item.get('pilot7_reference_id')
        reference = by_id.get(reference_id)
        if reference_id and reference is None:
            raise ValueError(f'unresolved pilot7_reference_id: {reference_id}')
        if reference is not None:
            record['pilot7_token_identical'] = record.get('tokens') is not None and record['tokens'] == reference.get('tokens')
        record['excluded'] = bool(record['calibration_exclusions'])
        compare_id = item.get('compare_reference_id')
        if compare_id and compare_id not in by_id:
            raise ValueError(f'unresolved compare_reference_id: {compare_id}')
    compared = session_desk_evidence(args.compare_session, v4=True) if args.compare_session else None
    inputs = compared if compared and compared.get('status') == 'pass' else {}
    result = window_report(members, cross_windows=inputs.get('cross_windows'),
                           sensitivity=inputs.get('sensitivity'), monitoring=inputs.get('monitoring'),
                           u3_bar=bar, v4=True, delta_slow_c=manifest.get('delta_slow_c'),
                           contrast_predeclared=contrast_predeclaration(wp19, policy))
    soak = r1_soak_c(args.registration_dir) if (args.registration_dir/'r1_soak_reference.json').is_file() else None
    result['registration_diagnostics'] = registration.desk_diagnostics(members, r1_soak=soak)
    result['u3_bar'] = bar
    result['wp19'] = wp19
    result['K_session_read'] = compared or {'status': 'inconclusive', 'reason': 'no --compare-session inputs'}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/'PILOT.json').write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    (args.output/'THERMAL.md').write_text(markdown_report(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
