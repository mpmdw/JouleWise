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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='new desk directory')
    parser.add_argument('--compare-session', type=Path, action='append', default=[],
                        metavar='PILOT.json', help='repeat for the K-session desk read')
    args = parser.parse_args(argv)
    manifest = json.loads(args.manifest.read_text())
    root = args.manifest.resolve().parent
    members = []
    def journal(name):
        return [json.loads(line) for line in (root/name).read_text().splitlines() if line.strip()]
    for item in manifest['members']:
        kwargs = {k: journal(item[k]) for k in ('os_journal', 'temperature_journal') if k in item}
        if 'registered_span_ns' in item:
            kwargs['registered_span_ns'] = item['registered_span_ns']
        try:
            record = read_bundle_record(root/item['bundle'], **kwargs)
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
        record.update({k: item[k] for k in ('window', 'identical_work_group', 'compare_reference_id', 'template', 'arm') if k in item})
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
    compared = session_desk_evidence(args.compare_session) if args.compare_session else None
    inputs = compared if compared and compared.get('status') == 'pass' else {}
    result = window_report(members, cross_windows=inputs.get('cross_windows'),
                           sensitivity=inputs.get('sensitivity'), monitoring=inputs.get('monitoring'))
    result['K_session_read'] = compared or {'status': 'inconclusive', 'reason': 'no --compare-session inputs'}
    # All equality/thermal checks above use original evidence. The exported
    # desk must not provide a decodable copy of the sealed v4 transcript.
    from joulewise.align.apple.transcript_custody import withhold_desk_transcripts
    withhold_desk_transcripts(result['members'])
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/'PILOT.json').write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    (args.output/'THERMAL.md').write_text(markdown_report(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
