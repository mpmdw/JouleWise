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
    """(u3 bar or None, wp19 receipt).

    A present ``u3_bar.json`` whose bar is still PENDING (R11/R03: no constant is
    installed, ``validate_u3`` refuses) yields ``None``: the desk then reports U3
    inconclusive and keeps running every other check. Arming stays refused through
    ``require_registration``. A missing or unreadable bar file, or an invalid WP19
    receipt, still raises (Opus cold HIGH-1).
    """
    try:
        bar = json.loads((directory/'u3_bar.json').read_bytes())
    except (OSError, ValueError) as exc:
        raise ValueError('v4 desk requires registered u3_bar.json') from exc
    source_root = ROOT if directory.absolute().is_relative_to(ROOT) else directory
    try:
        registration.validate_u3(bar, root=source_root)
    except ValueError:
        # Cold-review HIGH (b): a pending/invalid bar makes U3 inconclusive at
        # the desk; registration (arm) still refuses through require_registration.
        bar = None
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


def enrich_record(record, bundle):
    """V4-only metadata from immutable bundle bytes, never manifest overrides."""
    from joulewise.align.apple.workload import read_episode_bundle, EpisodeSpec
    from joulewise.align.apple.diagnostics import cache_statistics
    from joulewise.desk_compress import read_bytes
    ep = read_episode_bundle(bundle)
    config = json.loads(read_bytes(Path(bundle)/'config.json'))
    spec = EpisodeSpec.from_text(config['workload_profile']['prompt_text'])
    turns = [json.loads(line) for line in read_bytes(Path(bundle)/'outputs/align_turns.jsonl').splitlines() if line.strip()]
    thermal = ep.hardware.get('thermal') or {}
    record['cohort_identity'] = registration.cohort_identity(config, spec, ep.hardware.get('runtime_identity') or {})
    identity = record['cohort_identity']
    record['u3_configuration_sha256'] = (registration.digest(json.dumps(identity, sort_keys=True,
        separators=(',', ':')).encode()) if all(identity.values()) else None)
    record.update(configuration={k: getattr(spec, k) for k in
        ('max_episode_decode_tokens', 'deadman_s', 'max_tokens', 'max_turns')},
        status='incomplete' if ep.hardware.get('token_budget', {}).get('incomplete', True) else 'completed',
        turns=len(ep.turns), x_flags=list(record.get('calibration_exclusions', [])),
        cache_statistics=cache_statistics(turns), window_reference=thermal.get('window_reference'),
        admission_slow_c=record.get('g0_slow_c'),
        g1_wait_s_by_turn=[sum(i.get('duration_s', 0) for i in record['intervals']
                             if i['kind'] == 'G1' and i.get('turn') == t.index) for t in ep.turns])
    return record


def rl145_prints_report(manifest, root, journal):
    """RL-145 section 2 prints per manifest member (explicit inputs only, no discovery).

    Optional member keys: ``os_journal`` (as for the desk) and ``token_stamps`` (a JSON file
    ``{"<turn index>": [arrival ns of decode token 1, 2, ...]}``). The optional manifest key
    ``residual_rows`` names a JSONL of ``{trajectory, decode_tokens, residual_j[, prefill_s, decode_s]}`` rows
    (the load bins need the two seconds). Token times come from each bundle's token events.
    Without token stamps the token-position fields print as null with ``token_basis`` unavailable.
    """
    from joulewise.align.apple import rl145_prints
    members = []
    for item in manifest['members']:
        stamps = None
        if item.get('token_stamps'):
            stamps = {int(k): v for k, v in json.loads((root/item['token_stamps']).read_text()).items()}
        try:
            row = rl145_prints.bundle_prints(root/item['bundle'], token_stamps_by_turn=stamps,
                                             os_journal=journal(item['os_journal']) if 'os_journal' in item else ())
        except FileNotFoundError as exc:
            row = {'episode': item.get('id', Path(item['bundle']).name), 'turns': [],
                   'unavailable': f'member.artifact_missing:{exc.filename}'}
        members.append({'id': item.get('id'), **row})
    rows = journal(manifest['residual_rows']) if manifest.get('residual_rows') else None
    return {'schema': 'joulewise.align.rl145_prints.v1', 'authority': 'RL-145 section 2, RL-145 addendum row 6',
            'print_only': True, 'members': members,
            'residual_by_decode_bin': None if rows is None else rl145_prints.residual_by_decode_bin(rows),
            'residual_by_load_bin': None if rows is None else rl145_prints.residual_by_load_bin(rows)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='new desk directory')
    parser.add_argument('--registration-dir', type=Path, default=ROOT/registration.REGISTRATION)
    parser.add_argument('--compare-session', type=Path, action='append', default=[],
                        metavar='PILOT.json', help='repeat for the K-session desk read')
    args = parser.parse_args(argv)
    bar, wp19 = registration_evidence(args.registration_dir)
    policy = json.loads((args.registration_dir/'inputs.json').read_bytes())['R1']['thermal_policy']
    manifest = json.loads(args.manifest.read_text())
    root = args.manifest.resolve().parent
    from joulewise.align.apple import v4_battery
    try:
        battery_policy = json.loads((args.registration_dir/'battery_window_policy.json').read_bytes())
    except (OSError, ValueError):
        battery_policy = None
    battery_journal = (v4_battery.load_journal(root/manifest['battery_journal'])
                       if manifest.get('battery_journal') else ([], None, 1))
    members = []
    def journal(name):
        return [json.loads(line) for line in (root/name).read_text().splitlines() if line.strip()]
    for item in manifest['members']:
        kwargs = {k: journal(item[k]) for k in ('os_journal', 'temperature_journal') if k in item}
        if 'registered_span_ns' in item:
            kwargs['registered_span_ns'] = item['registered_span_ns']
        try:
            record = read_bundle_record(root/item['bundle'], **kwargs)
            enrich_record(record, root/item['bundle'])
        except FileNotFoundError as exc:
            # A refused/failed member may legally have no episode artifact.
            # Keep the registered roster row visible instead of losing the
            # entire window desk.
            record = {'id': item.get('id', Path(item['bundle']).name),
                      'model': item.get('model'), 'gated': item.get('gated', False),
                      'flags': ['member.artifact_missing', f'member.runtime_failure:{exc.filename}'],
                      'calibration_exclusions': ['member.runtime_failure'],
                      'intervals': [], 'tokens': None}
        # Scientific measurements and verdicts cannot be overridden by roster tags.
        record.update({k: item[k] for k in ('window', 'identical_work_group', 'compare_reference_id', 'template', 'arm',
                                          'ordinal', 'role', 'stage') if k in item})
        v4_battery.attach(record, root/item['bundle'], battery_journal)
        members.append(record)
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
                           u3_bar=bar, v4=True, delta_slow_c=manifest.get('delta_slow_c', policy.get('delta_slow_c')),
                           contrast_predeclared=contrast_predeclaration(wp19, policy))
    soak = r1_soak_c(args.registration_dir) if (args.registration_dir/'r1_soak_reference.json').is_file() else None
    result['registration_diagnostics'] = registration.desk_diagnostics(members, r1_soak=soak,
                                                                    battery_policy=battery_policy)
    result['u3_bar'] = bar
    result['u3_pending'] = bar is None
    result['wp19'] = wp19
    result['K_session_read'] = compared or {'status': 'inconclusive', 'reason': 'no --compare-session inputs'}
    args.output.mkdir(parents=True, exist_ok=False)
    # RL-145 addendum row 6: per-turn prints for the first W1 thermal desk. Print-only; no verdict.
    (args.output/'RL145_PRINTS.json').write_text(json.dumps(
        rl145_prints_report(manifest, root, journal), indent=2, sort_keys=True, allow_nan=False)+'\n')
    (args.output/'PILOT.json').write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    battery_rows = ['\n## Battery window consequences', '',
                    '| Model/window | B | Missing | Assist | Verdict | Consequence |',
                    '|---|---:|---:|---:|---|---|']
    for name, row in result['registration_diagnostics']['battery_windows'].items():
        battery_rows.append(f"| {name} | {row['B_count']} | {row['unobserved_count']} | {row['assist_count']} | "
                            f"{row['status']} | {row['consequence']} |")
    (args.output/'THERMAL.md').write_text(markdown_report(result)+'\n'.join(battery_rows)+'\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
