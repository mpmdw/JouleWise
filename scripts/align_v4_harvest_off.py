#!/usr/bin/env python3
"""Harvest off the MBP for one finalized ALIGN v4 window (docs/align/v4/HARVEST-OFF-opus.md).

MBP, after finalize:   pack    --session-root S --out O       (verified compressed raw copy)
Air, during cool-down: unpack  --offload O                    (same absolute path, every byte checked)
                       triage  --session-root S --window-id W (light: thermal_escalation, member_eligibility)
Air, next window:      desk    --session-root S --workers N   (unchanged harvest + full desk, timed)
                       final   --session-root S --window-id W (final eligibility row from the desk's PILOT.json)
                       reduce  --session-root S --out R --workers N (reduce-once columnar PM files, digest-bound)

Every subcommand prints one JSON line. Exit 0 on success, 1 on refusal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align.apple import harvest_offload, light_triage  # noqa: E402

IDENTITY = 'IDENTITY.json'
PY_IDENTITY = ('import sys, hashlib, importlib.metadata as m; print(sys.version); '
               'print(hashlib.sha256("\\n".join(sorted(f"{d.metadata[\'Name\']}=={d.version}" '
               'for d in m.distributions())).encode()).hexdigest())')


def _read(path):
    return json.loads(Path(path).read_bytes())


def checkout_identity(measurement_root, run=subprocess.run):
    """Head, cleanliness and interpreter/package identity of the measurement checkout.

    Same git probes as ``harvest.harvest_checkout`` (which the archive records), so
    a mirror that passes here gives the same harvest_checkout record on the Air.
    """
    root = Path(measurement_root)
    head = run(['git', '-C', str(root), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=False)
    status = run(['git', '-C', str(root), 'status', '--porcelain=v1', '--untracked-files=all'],
                 capture_output=True, text=True, check=False)
    python = root / '.venv/bin/python'
    interp = run([str(python), '-I', '-c', PY_IDENTITY], capture_output=True, text=True, check=False) \
        if python.exists() else None
    return {'measurement_root': str(root), 'head': head.stdout.strip() if head.returncode == 0 else None,
            'tracked_clean': status.returncode == 0 and not status.stdout.strip(),
            'python': interp.stdout.strip().splitlines() if interp is not None and interp.returncode == 0 else None}


def _session(session_root):
    session = Path(session_root)
    state = _read(session / 'session.json')
    plan = _read(state['plan_path'])
    return session, state, plan


def cmd_pack(args, run=subprocess.run):
    session, state, plan = _session(args.session_root)
    if not (Path(plan['custody_root']) / 'night/result.json').is_file():
        raise harvest_offload.OffloadRefused('terminal record absent; pack only a finalized window')
    ledger = Path(((plan.get('hazard_window') or {}).get('bindings') or {}).get('ledger_path') or '')
    external = (ledger,) if ledger.is_absolute() and ledger.is_file() and session not in ledger.parents else ()
    started = time.time()
    manifest = harvest_offload.pack(session.absolute(), args.out, level=args.level, threads=args.threads,
                                    external=external)
    identity = checkout_identity(state.get('source_measurement_root', state['measurement_root']), run=run)
    (Path(args.out) / IDENTITY).write_text(json.dumps(identity, indent=2, sort_keys=True) + '\n')
    return {'packed': manifest['source_root'], 'files': manifest['files'], 'bytes': manifest['bytes'],
            'payload_bytes': manifest['payload']['size'], 'payload_sha256': manifest['payload']['sha256'],
            'external': [row['path'] for row in manifest['external'].values()],
            'elapsed_s': round(time.time() - started, 3), 'identity': identity}


def cmd_unpack(args, run=subprocess.run):
    offload = Path(args.offload)
    recorded = _read(offload / IDENTITY)
    here = checkout_identity(recorded['measurement_root'], run=run)
    if here != recorded or not here['tracked_clean'] or here['head'] is None or here['python'] is None:
        raise harvest_offload.OffloadRefused('measurement checkout mirror differs from the MBP: '
                                             + json.dumps({'mbp': recorded, 'here': here}, sort_keys=True))
    started = time.time()
    manifest = harvest_offload.unpack(offload)
    return {'restored': manifest['source_root'], 'files': manifest['files'], 'bytes': manifest['bytes'],
            'elapsed_s': round(time.time() - started, 3)}


def _plan_rows(state):
    from scripts import align_pilot_session as pilot, align_v4_kit as kit
    return pilot._member_rows(state, kit=kit.KIT)


def cmd_triage(args, run=subprocess.run):
    """Light triage: the full desk's own record builder and window_report, no harvest."""
    from scripts import align_v4_session as session_mod, align_v4_kit as kit
    session, state, plan = _session(args.session_root)
    runs_root = _runs_root(state)
    import contextlib
    with contextlib.redirect_stdout(sys.stderr):  # the desk's per-member prints; stdout stays one JSON line
        checks, report = session_mod.powermode_desk_check(state=state, members=[], runs_root=runs_root,
                                                          kit_path=kit.KIT)
    if 'thermal' not in report:
        raise ValueError('light triage refused: ' + str(report.get('registration_error')))
    rows = _plan_rows(state)
    captured = {row['run_id'] for row in rows if (runs_root / row['run_id']).is_dir()}
    eligibility = light_triage.member_eligibility(report['thermal']['members'], rows, captured=captured, final=False)
    return {'thermal_escalation': light_triage.thermal_escalation(report['thermal'],
                                                                   ladder_recorded=args.ladder_recorded),
            'member_eligibility': eligibility,
            'calibration_row': light_triage.calibration_row(args.window_id, rows, eligibility)}


def cmd_final(args, run=subprocess.run):
    """Final eligibility row from the full desk's PILOT.json on the verified copy."""
    session, state, plan = _session(args.session_root)
    pilot = _read(args.pilot or session / 'PILOT.json')
    desk = _read(session / 'desk.json')
    if desk.get('harvest_status') in (None, 'not_run', 'program_fault'):
        raise ValueError('final eligibility needs a completed harvest (harvest_status '
                         + str(desk.get('harvest_status')) + ')')
    thermal = pilot['extra_checks']['thermal']
    rows = _plan_rows(state)
    runs_root = _runs_root(state)
    captured = {row['run_id'] for row in rows if (runs_root / row['run_id']).is_dir()}
    eligibility = light_triage.member_eligibility(thermal['members'], rows, captured=captured, final=True)
    return {'thermal_escalation': light_triage.thermal_escalation(thermal),
            'member_eligibility': eligibility,
            'calibration_row': light_triage.calibration_row(args.window_id, rows, eligibility),
            'pilot_status': pilot.get('status'), 'harvest_status': desk.get('harvest_status'),
            'pilot_sha256': hashlib.sha256((Path(args.pilot or session / 'PILOT.json')).read_bytes()).hexdigest()}


def cmd_desk(args, run=subprocess.run):
    """The unchanged v4 desk with the harvest's member pool; wall time recorded outside the session."""
    started = time.time()
    result = run([sys.executable, str(ROOT / 'scripts/align_v4_session.py'), 'desk', '--session-root',
                  str(args.session_root), '--harvest-workers', str(args.workers)], check=False)
    return {'desk_exit': result.returncode, 'workers': args.workers, 'elapsed_s': round(time.time() - started, 3)}


def cmd_reduce(args, run=subprocess.run):
    """Reduce each member's raw plists once into a sibling directory (never into the archive)."""
    from joulewise.align.apple import pm_reduce
    session, state, plan = _session(args.session_root)
    runs_root = _runs_root(state)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    tasks = [{'run_id': row['run_id'], 'bundle_path': str(runs_root / row['run_id']), 'out_dir': str(out)}
             for row in _plan_rows(state) if (runs_root / row['run_id']).is_dir()]
    started = time.time()
    members = pm_reduce.reduce_members(tasks, workers=args.workers)
    manifest = {'schema': 'joulewise.align_v4.reduced_pm.v1', 'extractor': pm_reduce.EXTRACTOR_VERSION,
                'session_id': state.get('session_id'), 'members': members}
    (out / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return {'reduced_members': len(members), 'files': sum(len(m['files']) for m in members),
            'raw_bytes': sum(f['raw_size'] for m in members for f in m['files']),
            'reduced_bytes': sum(f['reduced_size'] for m in members for f in m['files']),
            'elapsed_s': round(time.time() - started, 3), 'workers': args.workers}


def _runs_root(state):
    claim = (state.get('runs_roots') or {}).get('claim')
    if not claim:
        raise ValueError('session has no claim runs root')
    return Path(claim)


def main(argv=None, run=subprocess.run):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('pack')
    p.add_argument('--session-root', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--level', type=int, default=harvest_offload.DEFAULT_LEVEL)
    p.add_argument('--threads', type=int, default=0)
    p = sub.add_parser('unpack')
    p.add_argument('--offload', type=Path, required=True)
    for name in ('triage', 'final'):
        p = sub.add_parser(name)
        p.add_argument('--session-root', type=Path, required=True)
        p.add_argument('--window-id', required=True)
    sub.choices['triage'].add_argument('--ladder-recorded', action='store_true')
    sub.choices['final'].add_argument('--pilot', type=Path)
    p = sub.add_parser('reduce')
    p.add_argument('--session-root', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--workers', type=int, default=2)
    p = sub.add_parser('desk')
    p.add_argument('--session-root', type=Path, required=True)
    p.add_argument('--workers', type=int, default=3)
    args = parser.parse_args(argv)
    handler = {'pack': cmd_pack, 'unpack': cmd_unpack, 'triage': cmd_triage, 'final': cmd_final,
               'desk': cmd_desk, 'reduce': cmd_reduce}[args.command]
    try:
        print(json.dumps(handler(args, run=run), sort_keys=True))
    except (OSError, ValueError, KeyError) as exc:
        print('align_v4_harvest_off: ' + f'{type(exc).__name__}: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
