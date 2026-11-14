#!/usr/bin/env python3
"""Harvest off the MBP for one finalized ALIGN v4 window (docs/align/v4/HARVEST-OFF-opus.md).

MBP, at finalize:      finalize-manifest --session-root S --out M.json (commit M.json's sha256 with the record)
MBP, after finalize:   pack    --session-root S --out O --finalized-manifest M.json (the window's one pack; zstd -3 -T4)
Air, during cool-down: unpack  --offload O --finalized-manifest M.json --finalized-sha256 H (same path, record-bound)
The record binding is REQUIRED on pack and unpack (R17 review F2): without it they refuse.
                       triage  --session-root S --window-id W (light: thermal_escalation, member_eligibility)
Air, next window:      desk    --session-root S --workers auto|N (unchanged harvest + full desk, timed)
                       sweep   --session-root S --out D       (harvest at 2/4/6/8/10 workers: wall, peak RSS)
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


def _mirror_root(state):
    """The measurement checkout the session's links point into (absolute text; never resolved)."""
    return str(Path(state.get('source_measurement_root', state['measurement_root'])).absolute())


def _usable_identity(identity):
    return bool(identity.get('tracked_clean')) and identity.get('head') is not None and identity.get('python') is not None


def _ledger_input(session, plan):
    """The calibration ledger the window appended: a declared input, bound by bytes and real path, transported.

    The plan may name it through the session's measurement view (a link into the checkout's runs/);
    the declared input is then its resolved path, which is outside the session.
    """
    import os
    named = ((plan.get('hazard_window') or {}).get('bindings') or {}).get('ledger_path')
    if not named or not Path(named).is_absolute():
        return ()
    ledger = Path(os.path.realpath(named))
    session_real = Path(os.path.realpath(session))
    return (ledger,) if ledger.is_file() and session_real not in ledger.parents else ()


TERMINAL_EVIDENCE = ('result.json', 'chain.*', 'courier.sent')   # under <custody_root>/night/


def _terminal_inputs(session, plan):
    """The terminal evidence, declared as byte-bound inputs when custody lies outside the session (S1-04)."""
    import os
    custody = Path(os.path.realpath(plan['custody_root']))
    session_real = Path(os.path.realpath(session))
    if custody == session_real or session_real in custody.parents:
        return ()
    night = custody / 'night'
    found = {Path(os.path.realpath(p)) for pattern in TERMINAL_EVIDENCE for p in night.glob(pattern)}
    return tuple(sorted(p for p in found if p.is_file() and session_real not in p.parents))


def _consumed_inputs(session, plan_path, mirror):
    """Every file the harvest selects for this plan that the mirror identity does not cover (delta2, ruling 1).

    ``harvest.resolve_inputs`` is the harvest's own selector. A selected file outside the session is
    returned (to be declared and bound by bytes) when it lies outside the mirror, or inside it but
    ignored by Git. A selected directory outside the session that the identity does not cover refuses:
    its consumed files cannot be enumerated here. ``None`` when the plan cannot be resolved.
    """
    import dataclasses
    import os
    from joulewise.b5 import harvest
    try:
        selected = harvest.resolve_inputs(plan_path)
    except Exception:  # noqa: BLE001 - an unresolvable plan: the caller binds declared directories whole
        return None
    session_real = Path(os.path.realpath(session))
    mirror_real = Path(os.path.realpath(mirror))
    consumed = []
    for field in dataclasses.fields(selected):
        value = getattr(selected, field.name)
        if not isinstance(value, Path) or not os.path.lexists(value):
            continue
        real = Path(os.path.realpath(value))
        if real == session_real or session_real in real.parents:
            continue
        under_mirror = real == mirror_real or mirror_real in real.parents
        relative = real.relative_to(mirror_real).as_posix() if under_mirror and real != mirror_real else ''
        # Ignored itself (or below an ignored ancestor), not merely containing ignored content.
        ignored = under_mirror and any((relative + '/').startswith(entry if entry.endswith('/') else entry + '/')
                                       for entry in harvest_offload._git_ignored(mirror_real, relative))
        if real.is_dir():
            if not under_mirror or ignored:
                raise harvest_offload.OffloadRefused(
                    f'the harvest consumes the directory {value} ({field.name}) outside the session and the '
                    'mirror identity; its files cannot be bound')
            continue
        if not under_mirror or ignored:
            consumed.append(real)
    return sorted(set(consumed))


def _require(args, *names):
    missing = [name for name in names if getattr(args, name.replace('-', '_'), None) in (None, '')]
    if missing:
        raise harvest_offload.OffloadRefused(args.command + ' requires the record binding: '
                                             + ', '.join('--' + name for name in missing)
                                             + ' (R17 review F2: no unbound transfer on the production route)')


def cmd_pack(args, run=subprocess.run):
    _require(args, 'finalized-manifest')
    session, state, plan = _session(args.session_root)
    if not (Path(plan['custody_root']) / 'night/result.json').is_file():
        raise harvest_offload.OffloadRefused('terminal record absent; pack only a finalized window')
    finalized = _read(args.finalized_manifest)
    identity = checkout_identity(_mirror_root(state), run=run)
    started = time.time()
    # Air-offload S1-04 (lead ruling): carry EVERY byte-bound closure input (the ledger, external terminal
    # evidence, any byte-bound link target), so the Air copy restores without the MBP.
    manifest = harvest_offload.pack(session.absolute(), args.out, level=args.level, threads=args.threads,
                                    external=tuple(harvest_offload.byte_bound_inputs(finalized)),
                                    finalized=finalized, mirror_identity=identity)
    return {'packed': manifest['source_root'], 'files': manifest['files'], 'bytes': manifest['bytes'],
            'payload_bytes': manifest['payload']['size'], 'payload_sha256': manifest['payload']['sha256'],
            'external': [row['path'] for row in manifest['external'].values()],
            'finalized_manifest_sha256': manifest['finalized_manifest_sha256'],
            'elapsed_s': round(time.time() - started, 3), 'identity': identity}


def cmd_unpack(args, run=subprocess.run):
    _require(args, 'finalized-manifest', 'finalized-sha256')
    offload = Path(args.offload)
    finalized = _read(args.finalized_manifest)
    mirror = ((finalized.get('closure') or {}).get('mirror') if isinstance(finalized, dict) else None)
    if not isinstance(mirror, dict) or not isinstance(mirror.get('root'), str):
        raise harvest_offload.OffloadRefused('finalized record manifest binds no measurement checkout mirror')
    here = checkout_identity(mirror['root'], run=run)
    if here != mirror.get('identity') or not _usable_identity(here):
        raise harvest_offload.OffloadRefused('measurement checkout mirror differs from the MBP: '
                                             + json.dumps({'mbp': mirror.get('identity'), 'here': here}, sort_keys=True))
    started = time.time()
    manifest = harvest_offload.unpack(offload, finalized=finalized, finalized_sha256=args.finalized_sha256,
                                      mirror_identity=here)
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
    # Desk release guard (protocol B0/B2/B9/R27; RL-149 section 3, RL-151 section 4): the triage's record source
    # carries the same thermal and meter sections the sealed desk records (the allowlist the packet builder
    # reads), never member energy, and its verdicts are computed from that sealed section, so an exclusion's
    # suffix text never reaches the eligibility reasons (RL-151 C1(a)).
    from joulewise.align.apple import v4_desk_seal
    scope = v4_desk_seal.sealed_scope(state)
    thermal, meter = report['thermal'], report.get('km003c')
    if scope is not None:
        sealed = v4_desk_seal.seal_extra({'thermal': thermal, 'km003c': meter}, rows, scope)
        thermal, meter = sealed['thermal'], sealed['km003c']
    eligibility = light_triage.member_eligibility(thermal['members'], rows, captured=captured, final=False)
    result = {'schema': light_triage.SCHEMA, 'window': args.window_id,
              'thermal_escalation': light_triage.thermal_escalation(thermal,
                                                                     ladder_recorded=args.ladder_recorded),
              'member_eligibility': eligibility,
              'calibration_row': light_triage.calibration_row(args.window_id, rows, eligibility),
              'series_desk_row': report.get('series_desk_row'),
              # The desk's own checks without harvest codes (v4_B_bar for the arm's battery_window row)
              # and its SECONDARY meter tabulation, both read by the packet builder (R17).
              'checks': checks, 'km003c': meter,
              'thermal': thermal}
    if args.out:
        # The record source the arm's packet builder reads for the provisional adjudication (R17).
        from joulewise.align.apple.pilot_analysis import finite_json
        with Path(args.out).open('x', encoding='utf-8') as sink:
            sink.write(json.dumps(finite_json(result), indent=2, sort_keys=True, allow_nan=False) + '\n')
    return {k: v for k, v in result.items() if k not in ('thermal', 'km003c')}


# The shared finality predicate (delta D9): the packet builder's WindowRecord applies the same one.
COMPLETED_HARVEST = light_triage.COMPLETED_HARVEST
IGNORED_INPUTS = ROOT / 'configs/align/v4/harvest_off_ignored_inputs.json'


def cmd_final(args, run=subprocess.run):
    """Final eligibility row from the full desk's PILOT.json on the verified copy.

    Refuses unless ``light_triage.final_adjudication_error`` passes: a completed harvest (or, with no
    capture at all, no harvest needed), a completed desk adjudication, both of this session's plan,
    and agreeing exclusions. The packet builder applies the same predicate to the committed sources.
    """
    session, state, plan = _session(args.session_root)
    pilot = _read(args.pilot or session / 'PILOT.json')
    desk = _read(session / 'desk.json')
    rows = _plan_rows(state)
    runs_root = _runs_root(state)
    captured = {row['run_id'] for row in rows if (runs_root / row['run_id']).is_dir()}
    exclusions_path = session / 'archive/derived/exclusions.json'
    exclusions = (_read(exclusions_path) if exclusions_path.is_file() else
                  {'members_excluded': desk.get('members_excluded', pilot.get('members_excluded', []))})
    error = light_triage.final_adjudication_error(desk, pilot, exclusions, state.get('session_id'),
                                                  captured=bool(captured))
    if error is not None:
        raise ValueError('final eligibility refused: ' + error)
    thermal = pilot['extra_checks']['thermal']
    eligibility = light_triage.member_eligibility(thermal['members'], rows, captured=captured, final=True)
    return {'thermal_escalation': light_triage.thermal_escalation(thermal),
            'member_eligibility': eligibility,
            'calibration_row': light_triage.calibration_row(args.window_id, rows, eligibility),
            'pilot_status': pilot.get('status'), 'harvest_status': desk.get('harvest_status'),
            'pilot_sha256': hashlib.sha256((Path(args.pilot or session / 'PILOT.json')).read_bytes()).hexdigest()}


def cmd_desk(args, run=subprocess.run):
    """The unchanged v4 desk with the harvest's member pool; wall time recorded outside the session."""
    sizing = None
    workers = args.workers
    if workers == 'auto':
        peak, basis = sweep_basis(args.sweep, args.session_root) if args.sweep else (None, None)
        sizing = auto_workers(peak_bytes=peak, session_root=args.session_root)   # refuses when no worker fits
        if basis is not None:
            sizing['sweep'] = basis
            if peak is None:
                sizing['peak_basis'] += ' (sweep not used: ' + basis['reason'] + ')'
        workers = sizing['workers']
    workers = int(workers)
    if workers < 1:
        raise ValueError('desk workers must be a positive integer')
    started = time.time()
    result = run([sys.executable, str(ROOT / 'scripts/align_v4_session.py'), 'desk', '--session-root',
                  str(args.session_root), '--harvest-workers', str(workers)], check=False)
    return {'desk_exit': result.returncode, 'workers': workers, 'sizing': sizing,
            'elapsed_s': round(time.time() - started, 3)}


# R17 worker sizing: min(free cores, free memory / measured peak per worker).
PEAK_PER_PLIST_BYTE = 8          # measured: parsed documents resident about 8x the largest plist (sec. 2.3)
SWEEP_WORKERS = (2, 4, 6, 8, 10)


def free_memory_bytes(run=subprocess.run):
    """Free + inactive + speculative + purgeable pages (``vm_stat``), the memory a worker can take without swap."""
    import re
    out = run(['/usr/bin/vm_stat'], capture_output=True, text=True, check=False).stdout
    page = int(re.search(r'page size of (\d+) bytes', out).group(1))
    pages = sum(int(m.group(2)) for m in re.finditer(r'Pages (free|inactive|speculative|purgeable):\s+(\d+)', out))
    return pages * page


def free_cores(load_average=None, cpu_count=None):
    import os as _os
    load = (_os.getloadavg()[0] if load_average is None else load_average)
    cores = _os.cpu_count() if cpu_count is None else cpu_count
    return max(1, int(cores - load))


def largest_plist_bytes(session_root):
    session, state, _plan = _session(session_root)
    runs = _runs_root(state)
    sizes = [p.stat().st_size for p in runs.glob('*/raw/powermetrics*.plist') if p.is_file()]
    return max(sizes, default=0)


def auto_workers(*, peak_bytes=None, session_root=None, memory=None, cores=None, reserve_bytes=4 << 30):
    """Workers = min(free cores, (free memory - reserve) // peak per worker); refuses (postpone) at zero.

    ``peak_bytes`` is the measured per-worker peak from a bound sweep receipt (:func:`sweep_basis`);
    without one it is the conservative 8x the window's largest raw plist (recorded as ``peak_basis``).
    R17 review F5: when not even one worker fits after the reserve, the desk is POSTPONED (ValueError,
    exit 1), never launched over the memory budget.
    """
    basis = 'sweep'
    if peak_bytes is None:
        peak_bytes, basis = PEAK_PER_PLIST_BYTE * max(largest_plist_bytes(session_root), 1 << 20), '8x_largest_plist'
    if type(peak_bytes) is not int or peak_bytes <= 0:
        raise ValueError(f'per-worker peak must be a positive byte count, got {peak_bytes!r}')
    memory = free_memory_bytes() if memory is None else memory
    cores = free_cores() if cores is None else cores
    by_memory = (memory - reserve_bytes) // peak_bytes
    workers = int(min(cores, by_memory))
    if workers < 1:
        raise ValueError(f'postpone the desk: no harvest worker fits (free {memory} B - reserve {reserve_bytes} B '
                         f'< one worker peak {peak_bytes} B, basis {basis})')
    return {'workers': workers, 'free_cores': cores, 'free_memory_bytes': memory,
            'peak_bytes_per_worker': peak_bytes, 'peak_basis': basis, 'reserve_bytes': reserve_bytes}


SWEEP_SCHEMA = 'joulewise.align_v4.harvest_sweep.v2'


def _sweep_peak(path):
    """The largest successful per-worker peak of a sweep receipt; refuses a failed or nonpositive run."""
    receipt = _read(path)
    rows = receipt.get('runs') if isinstance(receipt, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError('sweep receipt has no runs')
    for row in rows:
        if not isinstance(row, dict) or row.get('exit') != 0:
            raise ValueError(f'sweep run failed ({row!r}); a failed run is not a measured worker peak')
        peak = row.get('peak_child_rss_bytes')
        if type(peak) is not int or peak <= 0:
            raise ValueError(f'sweep run has a nonpositive or missing peak ({peak!r})')
    return max(row['peak_child_rss_bytes'] for row in rows)


def sweep_code_identity(session_root, run=subprocess.run):  # run: the git/interpreter probe, never a harvest runner
    """The harvest program a sweep measures (delta D6): the SOURCE checkout behind the measurement view,
    its head, whether its tracked and untracked files are clean, and the interpreter/package identity."""
    _session_dir, state, _plan = _session(session_root)
    root = _mirror_root(state)
    identity = checkout_identity(root, run=run)
    return {'root': root, 'head': identity['head'], 'tracked_clean': identity['tracked_clean'],
            'python': identity['python']}


def _identified_code(code):
    """A usable code identity: a head, not dirty, and an interpreter identity that was actually read."""
    return (isinstance(code, dict) and isinstance(code.get('head'), str) and code['head']
            and code.get('tracked_clean') is not False
            and isinstance(code.get('python'), list) and bool(code['python']))


def sweep_basis(path, session_root):
    """``(peak_bytes or None, basis)`` for auto sizing from a sweep receipt (R17 review F5).

    The receipt must be a successful v2 sweep bound to the SAME harvest code (checkout head and
    interpreter) as this desk, and to an input size: its peak is scaled up linearly when this
    window's largest raw plist exceeds the swept one (never scaled down). A receipt without that
    binding, or for other code, is not used (``None``: the conservative 8x fallback applies).
    """
    peak = _sweep_peak(path)
    receipt = _read(path)
    swept, code = receipt.get('largest_plist_bytes'), receipt.get('code')
    if receipt.get('schema') != SWEEP_SCHEMA or type(swept) is not int or swept <= 0 or not isinstance(code, dict):
        return None, {'reason': 'receipt not bound to an input size and code', 'path': str(path)}
    if not _identified_code(code):
        return None, {'reason': 'receipt code identity incomplete (head, clean tree, interpreter)', 'path': str(path)}
    current_code = sweep_code_identity(session_root)
    if not _identified_code(current_code):
        return None, {'reason': 'this harvest code is unidentified or dirty', 'path': str(path)}
    if code != current_code:
        return None, {'reason': 'receipt measured other harvest code', 'path': str(path)}
    current = largest_plist_bytes(session_root)
    scaled = peak if current <= swept else -(-peak * current // swept)
    return scaled, {'reason': 'bound', 'path': str(path), 'measured_peak_bytes': peak,
                    'swept_largest_plist_bytes': swept, 'largest_plist_bytes': current}


def measure_harvest(argv, *, run=subprocess.run):
    """Wall time and the largest descendant RSS (macOS ru_maxrss is bytes) of one harvest run."""
    import resource
    before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    started = time.monotonic()
    result = run(argv, check=False, capture_output=True, text=True)
    wall = time.monotonic() - started
    after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    return {'exit': result.returncode, 'wall_s': round(wall, 3), 'peak_child_rss_bytes': max(after, before),
            'peak_is_new': after > before}


def cmd_sweep(args, run=subprocess.run):
    """Harvest the restored window at each worker count into separate archives (R17 knee)."""
    session, state, plan = _session(args.session_root)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    measurement = Path(state['measurement_root'])
    largest = largest_plist_bytes(args.session_root)
    code = sweep_code_identity(args.session_root)
    rows = []
    for workers in args.workers:
        target = out / f'w{workers:02d}'
        argv = [str(measurement / '.venv/bin/python'), str(measurement / 'scripts/harvest_b6_session.py'),
                '--plan', state['plan_path'], '--archive-root', str(target / 'archive'),
                '--registration-dir', state['registration_dir'], '--pack-records-root', str(target / 'private'),
                '--export-dir', str(target / 'export'), '--non-claim', '--workers', str(workers),
                '--io-workers', '2', '--profile', str(target / 'profile.jsonl')]
        target.mkdir()
        rows.append({'workers': workers, **measure_harvest(argv, run=run)})
    receipt = {'schema': SWEEP_SCHEMA, 'session_id': state.get('session_id'), 'runs': rows,
               'largest_plist_bytes': largest, 'code': code,
               'note': 'peak_child_rss_bytes is the largest single descendant, i.e. the per-worker peak; '
                       'bound to largest_plist_bytes and the harvest code (sweep_basis)'}
    (out / 'SWEEP.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    return receipt


def cmd_finalize_manifest(args, run=subprocess.run):
    session, state, plan = _session(args.session_root)
    if not (Path(plan['custody_root']) / 'night/result.json').is_file():
        raise harvest_offload.OffloadRefused('terminal record absent; finalize only a terminal window')
    # The external closure (R17 review F1): links into the measurement checkout are bound by its
    # identity (the mirror the Air must reproduce); the calibration ledger by its bytes; any other
    # external link target by the bytes it reaches, within the finite bounds, or the finalize refuses.
    mirror = _mirror_root(state)
    identity = checkout_identity(mirror, run=run)
    if not _usable_identity(identity):
        raise harvest_offload.OffloadRefused('measurement checkout is not a clean, identified mirror source: '
                                             + json.dumps(identity, sort_keys=True))
    declared = _read(IGNORED_INPUTS)
    policy = {key: declared[key] for key in harvest_offload.DEFAULT_IGNORED_POLICY if key in declared}
    inputs = list(_ledger_input(session, plan)) + [p for p in _terminal_inputs(session, plan)]
    consumed = _consumed_inputs(session, state['plan_path'], mirror)
    if consumed is None:
        # The harvest's selection cannot be enumerated from this plan: nothing below a declared directory is
        # assumed unconsumed; each is bound by bytes and membership within the bounds (delta2, ruling 1).
        policy['declared_directory_mode'] = 'bind'
    else:
        policy['declared_directory_mode'] = 'consumed'
        inputs += [path for path in consumed if path not in inputs]
    manifest = harvest_offload.finalized_manifest(session.absolute(), mirror={'root': mirror, 'identity': identity},
                                                  inputs=tuple(inputs), ignored_policy=policy)
    # Canonical bytes, so the file's own SHA-256 (the record's raw_evidence descriptor) IS the
    # digest unpack checks (manifest_sha256): one number in the record, not two.
    with Path(args.out).open('xb') as sink:
        sink.write(json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode())
    return {'finalized_manifest': str(args.out), 'sha256': harvest_offload.manifest_sha256(manifest),
            'entries': len(manifest)}


def cmd_reduce(args, run=subprocess.run):
    """Reduce each member's raw plists once into a sibling directory (never into the archive)."""
    from joulewise.align.apple import pm_reduce
    session, state, plan = _session(args.session_root)
    runs_root = _runs_root(state)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    tasks = [{'run_id': row['run_id'], 'bundle_path': str(runs_root / row['run_id']), 'out_dir': str(out),
              'turn_table': True}
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
    # Lead ruling 2026-11-08 (one pack per window): zstd -3 with 4 threads, not every core, to limit
    # cool-down CPU and heat on the MBP; the Air-offload tool consumes this pack.
    p.add_argument('--threads', type=int, default=4)
    p.add_argument('--finalized-manifest', type=Path)
    p = sub.add_parser('unpack')
    p.add_argument('--offload', type=Path, required=True)
    p.add_argument('--finalized-manifest', type=Path)
    p.add_argument('--finalized-sha256')
    p = sub.add_parser('finalize-manifest')
    p.add_argument('--session-root', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p = sub.add_parser('sweep')
    p.add_argument('--session-root', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--workers', type=lambda v: [int(x) for x in v.split(',')], default=list(SWEEP_WORKERS))
    for name in ('triage', 'final'):
        p = sub.add_parser(name)
        p.add_argument('--session-root', type=Path, required=True)
        p.add_argument('--window-id', required=True)
    sub.choices['triage'].add_argument('--ladder-recorded', action='store_true')
    sub.choices['triage'].add_argument('--out', type=Path, help='write the light-triage record source (new file)')
    sub.choices['final'].add_argument('--pilot', type=Path)
    p = sub.add_parser('reduce')
    p.add_argument('--session-root', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--workers', type=int, default=2)
    p = sub.add_parser('desk')
    p.add_argument('--session-root', type=Path, required=True)
    p.add_argument('--workers', default='auto', help="'auto' (R17 sizing) or a positive integer")
    p.add_argument('--sweep', type=Path, help='SWEEP.json whose measured peak sizes auto workers')
    args = parser.parse_args(argv)
    handler = {'pack': cmd_pack, 'unpack': cmd_unpack, 'triage': cmd_triage, 'final': cmd_final,
               'desk': cmd_desk, 'reduce': cmd_reduce, 'sweep': cmd_sweep,
               'finalize-manifest': cmd_finalize_manifest}[args.command]
    try:
        print(json.dumps(handler(args, run=run), sort_keys=True))
    except (OSError, ValueError, KeyError) as exc:
        print('align_v4_harvest_off: ' + f'{type(exc).__name__}: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
