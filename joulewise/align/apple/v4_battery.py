"""R02 window consequence proposal; existing battery physics are unchanged."""
import json
from pathlib import Path

EXCLUDE = ('battery.member_span', 'battery.accumulator_excursion')
MISSING = ('battery.unmeasured', 'battery.capture_pair_missing', 'battery.capture_pair_failed')


def validate_policy(policy):
    from scripts.align_v4_kit import valid_lead_signature
    if (not isinstance(policy, dict) or policy.get('schema') != 'joulewise.align_v4.battery_window.v1'
            or policy.get('status') != 'registered' or policy.get('rule') != 'zero_B_disclose_assist_v1'
            or not valid_lead_signature(policy.get('lead_signature'))):
        raise ValueError('B window consequence PENDING lead adoption')
    return policy


def load_journal(path):
    """Explicit closed journal only; compressed copies use the common reader."""
    from joulewise.b5.harvest import read_monitor_journal
    from joulewise.desk_compress import read_bytes
    from joulewise.align.apple.v4_registration import digest
    try:
        raw = read_bytes(Path(path))
        readings, malformed = read_monitor_journal(Path(path), 'battery')
        return readings, digest(raw), malformed
    except (OSError, ValueError, TypeError):
        return [], None, 1


def bundle_evidence(bundle, journal):
    """Replay the shared span join from raw journal and controller clock bounds.

    Never infer a clean battery from empty flags or an arm float observation.
    """
    from joulewise.b5.harvest import member_spans, battery_join
    from joulewise.desk_compress import read_bytes
    from joulewise.align.apple.v4_registration import digest
    readings, source, malformed = journal
    result = dict(status='unavailable', source_sha256=source, flags=[],
                  soc_pct=None, charger_w=None)
    try:
        metadata_raw = read_bytes(Path(bundle)/'metadata.json')
        events_raw = read_bytes(Path(bundle)/'events.jsonl')
        spans = member_spans(json.loads(metadata_raw),
                             [json.loads(line) for line in events_raw.splitlines() if line.strip()])
        if not readings or malformed or spans['member'] is None:
            result['reason'] = 'missing/malformed journal or controller span'
            return result
        findings, assist = battery_join(spans['member'], readings,
            {'battery_limit_ma': 200, 'battery_unmeasured_gap_s': 120,
             'battery_accumulator_watts_per_unit': .001}, request=spans['request'])
        codes = [code for code, _, _ in findings]
        selected = [r.values for r in readings if spans['member'][0] <= r.monotonic_ns <= spans['member'][1]]
        result.update(status='unavailable' if any(c in MISSING for c in codes) else 'observed',
                      flags=codes, assist=assist, spans=spans,
                      metadata_sha256=digest(metadata_raw), events_sha256=digest(events_raw),
                      soc_pct=[r.get('current_capacity_pct') for r in selected],
                      charger_w=[r.get('adapter_watts') for r in selected])
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result['reason'] = type(exc).__name__+': '+str(exc)
    return result


def attach(record, bundle, journal):
    evidence = bundle_evidence(bundle, journal)
    record['battery'] = evidence
    record.setdefault('flags', []).extend(c for c in evidence['flags'] if c not in record.get('flags', []))
    exclusions = [c for c in evidence['flags'] if c in EXCLUDE+MISSING]
    if evidence['status'] != 'observed' and not exclusions:
        exclusions = ['battery.unmeasured']
    record.setdefault('calibration_exclusions', []).extend(
        c for c in exclusions if c not in record.get('calibration_exclusions', []))
    record['excluded'] = bool(record['calibration_exclusions'])
    return record


def window_consequences(members, policy):
    from joulewise.align.apple.v4_registration import is_digest
    try:
        validate_policy(policy)
        adopted = True
    except ValueError:
        adopted = False
    windows = {}
    for row in members:
        windows.setdefault(f"{row.get('model')}/{row.get('window', 'W1')}", []).append(row)
    reports = {}
    for key, rows in windows.items():
        count = missing = assist = outside = 0
        unassisted = []
        for row in rows:
            evidence = row.get('battery') or {}
            codes = set(row.get('flags', [])) | set(row.get('calibration_exclusions', [])) | set(evidence.get('flags', []))
            count += any(c in EXCLUDE for c in codes)
            missing += (evidence.get('status') != 'observed' or not is_digest(evidence.get('source_sha256'))
                        or any(c in MISSING for c in codes))
            assist += 'battery.assist' in codes
            outside += 'battery.assist_outside_request' in codes
            if 'battery.assist' not in codes and evidence.get('status') == 'observed' and not row.get('excluded'):
                unassisted.append(row['id'])
        passed = None if not adopted else False if count else None if missing else True
        reports[key] = dict(B_count=count, unobserved_count=missing, assist_count=assist,
            assist_outside_request_count=outside, bar_pass=passed,
            no_assist_sensitivity={'status': 'print_only', 'member_ids': unassisted},
            status='pass' if passed is True else 'fail' if passed is False else 'inconclusive',
            consequence=('B window consequence PENDING lead adoption' if not adopted else
                         'battery window invalid; retain/exclude B members; no pool entry; remedy before next arm' if count else
                         'battery evidence unavailable; no pool entry until adjudicated' if missing else
                         'retain GPU members; disclose assist; print no-assist sensitivity; DC-in remains secondary'),
            members=[{'id': r['id'], **r.get('battery', {})} for r in rows])
    return reports
