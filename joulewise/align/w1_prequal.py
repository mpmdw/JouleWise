"""ALIGN v4 pre-arm PREQUAL extension: every code path W1 (or the next window) runs.

RUN_STATE 219/220: the merged Sol/Opus W1 smoke kit (lead ruling). Runs on the Air before any
MBP launch, never on the measurement Mac. Each check is a *probe*: one fresh
Python process per check (``scripts/align_v4_prequal.py --w1-probe NAME``),
run in parallel, so no check's imports, patches or environment leak into
another. A probe returns ``{"status": PASS|FAIL|PENDING|WARN, "detail", "evidence"}``; WARN never blocks.

PENDING means "not satisfiable before the named stage by design" (for example
the registration receipt before R1 closes). PENDING is allowed only when the
next measurement is earlier than the stage that check gates; for ``--next w1``
every PENDING is a FAIL. Any exception is a FAIL, never a skip.

Nothing here touches hardware: every host command (pmset, ioreg, mount,
diskutil, launchctl, the night-agent installer) goes to an injected fake, and
the KM003C meter is a stand-in program. No restricted path, record or outcome
field is read; synthetic records only.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback

REPO = Path(__file__).resolve().parents[2]
SCHEMA = 'joulewise.align_v4.w1_prequal.v1'
PASS, FAIL, PENDING, WAIVED, WARN = 'PASS', 'FAIL', 'PENDING', 'WAIVED', 'WARN'
STATUSES = (PASS, FAIL, PENDING, WAIVED, WARN)
NEXT = ('r1', 'w1')
ARM_ROUTES = Path('configs/align/v4/arm_routes.json')
REQUIRED_INSTALL_FLAGS = ('--w1-disk-config', '--obc-off-attested-by', '--battery-log', '--next-arm-triage')
# Kit/receipt refusals that are "not filled yet" (PENDING before W1), not faults.
PENDING_MARKERS = ('PENDING', 'BLOCKED', 'not derivable yet', 'registration_receipt', 'is still pending',
                   'U3 ', 'WP19', 'source must be', 'lead signature')
GAP_REFS = {
    'packet-rebuild': 'G1 (v4 fixer, lead ruling): the arm must rebuild the packet and require canonical equality',
    'packet-tamper': 'G1b (v4 fixer, lead ruling): any field differing from the rebuild, or a chain hole, must refuse',
    'r1-w1-chain': 'G2 (v4 fixer): R1-TO-W1-CHAIN.md runs kit --check without regenerating the kit',
    'km003c-crash-radius': 'G3 (v4 fixer): a killed reader voids DC for every earlier member of its stream',
    'cal-escalation-exit': 'Opus cold review MED-2(a): escalate_to_lead needs a lead-ruling input',
}

CHECKS = {}
SYNTHETIC_RUNTIME_STACK = {'python': 'synthetic', 'packages': {'mlx': 'synthetic'}}


def check(name, covers, gates='w1'):
    """Register a probe. ``gates`` is the earliest measurement it must PASS for."""
    def wrap(fn):
        CHECKS[name] = {'fn': fn, 'covers': covers, 'gates': gates}
        return fn
    return wrap


class Context:
    def __init__(self, repo=REPO, work=None, next_window='w1', commit=None, python_bin=None, run=None,
                 series_projection=None, deadline_projection=None):
        self.repo = Path(repo)
        # Repo-relative, lead-supplied planning projections (Sol port); never outcomes.
        self.series_projection, self.deadline_projection = series_projection, deadline_projection
        self.work = Path(work) if work else Path(tempfile.mkdtemp(prefix='w1-prequal-'))
        self.next = next_window
        self.python = python_bin or sys.executable
        self.run = run or _run
        self.commit = commit or git(self.repo, 'rev-parse', 'HEAD', run=self.run)


def _run(argv, *, cwd=None, env=None, timeout=900, input=None):
    return subprocess.run([str(a) for a in argv], cwd=cwd, env=env, timeout=timeout, input=input,
                          capture_output=True, text=True, check=False)


def git(root, *args, run=_run):
    result = run(['git', '-C', str(root), *args], timeout=300)
    if result.returncode:
        raise RuntimeError(f'git {" ".join(args)} failed: {(result.stderr or "").strip()[-400:]}')
    return result.stdout.strip()


def scratch_clone(ctx, name):
    """A disposable clone of the candidate commit (objects shared; removed by the caller)."""
    dest = ctx.work / name
    if dest.exists():
        shutil.rmtree(dest)
    result = ctx.run(['git', 'clone', '--quiet', '--shared', '--no-checkout', str(ctx.repo), str(dest)], timeout=600)
    if result.returncode:
        raise RuntimeError('scratch clone failed: ' + (result.stderr or '')[-400:])
    git(dest, 'checkout', '--quiet', '--detach', ctx.commit, run=ctx.run)
    return dest


def tail(text, n=600):
    text = text or ''
    return text[-n:]


def result(status, detail, **evidence):
    return {'status': status, 'detail': detail, 'evidence': evidence}


def pending_or_fail(ctx, check_name, detail, **evidence):
    """PENDING while the next measurement is earlier than the stage this check gates."""
    gates = CHECKS[check_name]['gates']
    if NEXT.index(ctx.next) < NEXT.index(gates):
        return result(PENDING, detail, **evidence)
    return result(FAIL, detail, **evidence)


# ---------------------------------------------------------------------------
# Fake host: every arm-path command, nothing real runs


class FakeHost:
    """pmset, ioreg, mount, diskutil, launchctl and the night-agent installer.

    ``extra_mount`` adds a mounted disk image (hdiutil attach stand-in);
    ``night_job_loaded`` makes launchd report a loaded night job.
    """

    def __init__(self, mode=0, *, extra_mount=False, night_job_loaded=False, soc=100, charging=False, now=None,
                 watchdog_state='LAUNCHING', watchdog_post_state=None):
        self.now = now
        self.mode, self.extra_mount, self.night_job_loaded = mode, extra_mount, night_job_loaded
        self.soc, self.charging = soc, charging
        self.calls, self.installer_calls = [], []
        self.watchdog_state = watchdog_state
        self.watchdog_post_state = watchdog_post_state
        self.installed_labels = set()

    def watchdog_check(self, *, phase, plan=None, **_):
        """Synthetic nested session/custody plan: only installed jobs expose it to discovery."""
        from joulewise.night_agent_install import LABELS
        from scripts import align_v4_session as session_mod
        state = self.watchdog_post_state if phase == 'post_install' and self.watchdog_post_state else self.watchdog_state
        found = phase == 'pre_install' or set(LABELS) <= self.installed_labels
        span = (plan or {}).get('t0_epoch_s', (self.now or time.time()) + 3600) - session_mod.WATCHDOG_PLAN_LEAD_S
        identity = {'source': 'installed_parser_on_plan_file' if phase == 'pre_install' else 'installed_load_plans',
                    'found': found, 'span_start_epoch_s': span if found else None, 'expected': span, 'ok': found}
        if phase == 'pre_install':
            identity['discovered_by_scan'] = False
        return {'ok': found and state in session_mod.WATCHDOG_ADMITTED,
                'state': state, 'reason': 'PREQUAL synthetic watchdog' if found else 'plan_identity: arm plan missing',
                'plan_identity': identity,
                'argv': ['synthetic-watchdog', '--dry-run'], 'plan_read_proven': found,
                'elapsed_s': 0.0, 'stopped': state == 'STOPPED'}

    def frequency_check(self, *_, **__):
        """The minimal fake night plan has no native clock budget or reader."""
        return {'ok': True, 'synthetic': True, 'reason': 'PREQUAL synthetic frequency'}

    @staticmethod
    def weight_identity(root):
        """Explicit synthetic R0 identity seam; never inspect a real model."""
        return {'status': 'ok', 'kind': 'file_set', 'root': str(root), 'folded_sha256': 'a' * 64,
                'files': {'model.safetensors': 'b' * 64},
                'inventory': [{'path': 'model.safetensors', 'size_bytes': 7}]}

    def __call__(self, argv, *args, **kwargs):
        import plistlib
        argv = tuple(str(a) for a in argv)
        self.calls.append(argv)
        done = lambda rc, out='', err='': subprocess.CompletedProcess(argv, rc, out, err)
        if argv == ('/usr/sbin/ioreg', '-r', '-c', 'AppleSmartBattery'):
            raw = ('+-o AppleSmartBattery  <class AppleSmartBattery, id 0x1, registered, matched, active, '
                   'busy 0 (0 ms), retain 1>\n    {\n'
                   '      "ExternalConnected" = Yes\n'
                   f'      "IsCharging" = {"Yes" if self.charging else "No"}\n'
                   '      "InstantAmperage" = 0\n      "Amperage" = 0\n'
                   f'      "CurrentCapacity" = {self.soc}\n'
                   f'      "UpdateTime" = {int(self.now or time.time())}\n    }}\n').encode()
            return subprocess.CompletedProcess(argv, 0, raw, b'')
        if argv == ('pmset', '-g', 'batt'):
            return done(0, 'synthetic: 100%; AC; not charging')
        if argv[:2] == ('launchctl', 'print'):
            label = argv[-1].rsplit('/', 1)[-1]
            absent = f'Could not find service "{label}" in domain for user gui: {os.getuid()}'
            loaded = self.night_job_loaded or label in self.installed_labels
            return done(0, 'loaded', '') if loaded else done(113, '', absent + '\n')
        if argv == ('/usr/bin/pmset', '-g', 'custom'):
            return done(0, f'Battery Power:\n powermode 0\nAC Power:\n lowpowermode 0\n powermode {self.mode}\n')
        if argv[:5] == ('sudo', '-n', '/usr/bin/pmset', '-c', 'powermode'):
            self.mode = int(argv[5])
            return done(0)
        if argv == ('/sbin/mount',):
            out = '/dev/disk3s1s1 on / (apfs, sealed, local, read-only, journaled)\n'
            if self.extra_mount:
                out += '/dev/disk9s1 on /Volumes/JWSMOKE (hfs, local, nodev, nosuid, read-only, noowners)\n'
            return done(0, out)
        if argv[:3] == ('/usr/sbin/diskutil', 'info', '-plist'):
            image = argv[3].startswith('/dev/disk9')
            return done(0, plistlib.dumps({'Internal': not image,
                                           'BusProtocol': 'Disk Image' if image else 'Apple Fabric',
                                           'FilesystemType': 'hfs' if image else 'apfs',
                                           'WritableVolume': not image}).decode())
        if argv and argv[0].endswith('install_night_agent.sh'):
            self.installer_calls.append(argv)
            from joulewise.night_agent_install import LABELS
            if '--uninstall' in argv:
                self.installed_labels.difference_update(LABELS)
            else:
                self.installed_labels.update(LABELS)
            return done(0, 'synthetic installer\n')
        raise AssertionError(f'FakeHost: unexpected command {argv}')


def triage_packet(*, previous='R1', role=None, windows=None, overrides=None, record_commit='0' * 40,
                  desk_digest='0' * 64, rulings=None):
    """A complete passing next-arm packet (default: the W1 arm, previous window R1).

    ``record_commit`` names the previous window's committed record and
    ``desk_digest`` the bound-artifact digest at the last desk pass; the arm derives
    whether the commit exists and whether code changed, never from the packet.
    """
    from joulewise.align.apple import v4_cadence as cad
    checks = {}
    for row in cad.NEXT_ARM_TRIAGE:
        if row['source'] != cad.PACKET:
            continue
        if row.get('gating', True) is False:
            checks[row['id']] = {'status': 'recorded', 'basis': 'w1-prequal synthetic', 'gaps': []}
            continue
        na = previous == 'R1' and row['first_window_na']
        checks[row['id']] = {'status': 'not_applicable' if na else 'pass', 'basis': 'w1-prequal synthetic'}
    packet = {'schema': cad.TRIAGE_SCHEMA, 'previous_window': previous, 'next_window_role': role,
              'record_commit': record_commit, 'record_path': 'records/synthetic/record.json',
              'record_sha256': 'c' * 64, 'last_desk_passed_artifact_set_sha256': desk_digest,
              'calibration_windows': list(windows or ()), 'lead_rulings': list(rulings or ()), 'checks': checks}
    for key, value in (overrides or {}).items():
        packet[key] = value
    return packet


def battery_log(path, now, kind='completed'):
    """A synthetic ``battery_float.v1`` log the arm derives top-up evidence from (v4_topup)."""
    def row(t, charging, pct=100):
        return {'schema': 'joulewise.battery_float.v1', 'probe_error': False, 'wall_time_s': t,
                'external_connected': True, 'is_charging': charging, 'current_capacity_pct': pct}
    if kind == 'completed':          # a charge that completed 9 min ago, floating since
        rows = [row(now - 600, True, 98)] + [row(now - 540 + 60 * i, False) for i in range(9)]
    elif kind == 'no-charge':        # floating only, no completed charge in the log
        rows = [row(now - 600 + 60 * i, False) for i in range(10)]
    elif kind == 'stale':            # completed long ago, nothing logged for an hour
        rows = [row(now - 7200, True, 98), row(now - 7140, False), row(now - 3600, False)]
    elif kind == 'future':           # an observation after the arm time
        rows = [row(now - 600, True, 98), row(now - 540, False), row(now + 300, False)]
    else:
        raise ValueError(kind)
    Path(path).write_text(''.join(json.dumps(r) + '\n' for r in rows))
    return path


def _scenario_class():
    """The v4 fixer's synthetic record fixture (real ``window_record.v1`` index and ``series/state.json``)."""
    from tests.align.test_v4_next_arm_packet import Scenario
    return Scenario


def _fresh(scenario, now):
    """Quiet-state observation one second before the arm (its validity window is 30 s)."""
    scenario.quiet['observed_at_epoch_s'] = int(now) - 1
    return scenario


def arm_fixture(ctx, name, *, now, t0_offset_s=3600, ac_powermode=0):
    """A session the production install CLI accepts: an R1 -> W1 record series, plan, R0 disk config."""
    from scripts import align_v4_kit as kit, bytes_h_session as h
    base = ctx.work / name
    measurement, session = base / 'measurement', base / 'night-align/session'
    custody = session / 'custody'
    measurement.mkdir(parents=True)
    scenario = _scenario_class()(measurement, 'R1')
    scenario.next_plan.update(window='W1', role='development')
    del scenario.thermal['model_windows']
    # The kit files the arm reads are committed with the records, so the desk-passed artifact set holds.
    (measurement / kit.KIT / 'registration').mkdir(parents=True, exist_ok=True)
    plan = json.loads((ctx.repo / kit.KIT / 'collection_plan.json').read_bytes())
    plan.setdefault('runtime_requirements', {})['ac_powermode'] = ac_powermode
    (measurement / kit.KIT / 'collection_plan.json').write_text(json.dumps(plan))
    inventory = {}
    for member in plan['members']:
        weights = base / 'synthetic-weights' / member['model_id']
        weights.mkdir(parents=True, exist_ok=True)
        (weights / 'model.safetensors').write_bytes(b'fixture')
        inventory[h.align_unit_id(member['model_id'], member['run_id'])] = FakeHost.weight_identity(weights)
    h.write(measurement / kit.KIT / 'registration/model_artifact_inventory.json', {'artifacts': inventory})
    h.write(measurement / kit.KIT / 'registration/identity_pins.json',
            {'runtime_versions': SYNTHETIC_RUNTIME_STACK})
    (measurement / kit.R1_SLOTS).write_text(json.dumps({'ac_powermode': ac_powermode}))
    series = ctx.repo / kit.KIT / 'series'
    if series.is_dir():                 # RUN_STATE 226 R15: every arm binds the frozen series
        shutil.copytree(series, measurement / kit.KIT / 'series')
    _fresh(scenario, now).finish()
    session.mkdir(parents=True)
    custody.mkdir(parents=True)
    night_plan = custody / 'night_plan.json'
    night_plan.write_text(json.dumps({'t0_epoch_s': now + t0_offset_s, 'plan_id': 'w1-prequal-synthetic'}))
    state = {
        'measurement_root': str(measurement), 'plan_path': str(night_plan),
        'preparation_status': 'STAGED',
        'plan_sha256': h.locator(night_plan)['sha256'], 'inputs': {'custody_root': str(custody)}}
    from scripts import align_v4_session as session_mod
    state['weight_digest_preflight'] = session_mod.weight_digest_preflight(
        measurement / kit.KIT / 'registration', plan['members'], identity_fn=FakeHost.weight_identity)
    h.write(session / 'session.json', state)
    config = json.loads((ctx.repo / 'configs/align/v4/r0_desk.json').read_bytes())
    if not config.get('offloads'):
        config['offloads_owed'] = 'none'
    disk = base / 'r0_desk.json'
    disk.write_text(json.dumps(config))
    (base / 'identities.json').write_text(json.dumps(scenario.identities()))
    return base, session, disk


def fixture_packet(base, now=None):
    """The producer's packet (scripts/align_v4_next_arm_packet.build_packet) for the fixture's R1 record."""
    from scripts import align_v4_next_arm_packet as builder
    from joulewise.align.apple import v4_registration as reg
    root = Path(base) / 'measurement'
    return builder.build_packet(root, **json.loads((Path(base) / 'identities.json').read_text()),
                                now_epoch_s=now or time.time(),
                                current_artifact_set_sha256=reg.artifact_set_digest(root))


def valid_packet(ctx, base, now):
    """The packet the production arm accepts for the fixture: its own rebuild when it rebuilds, else the pointer."""
    pointer = fixture_packet(base, now)
    rebuilt = _find_rebuilt(_arm_file(ctx, Path(base) / 'measurement', pointer, now=now))
    if rebuilt is None:
        return pointer
    return {**rebuilt, **{k: pointer[k] for k in PACKET_IGNORED if k in pointer}}


def LIVE_METER(root):
    return {'live': True, 'synthetic': 'w1-prequal fake meter probe (the real probe runs km003c_monitor.py)'}


def DEAD_METER(root):
    return {'live': False, 'reason': 'synthetic: no aligned samples'}


def run_install(ctx, session, disk, packet, *, host, args_override=None, drop=(), now=None, kind='completed',
                meter_probe=None):
    """Drive the production CLI (align_v4_session.main) with host seams only."""
    import functools
    from scripts import align_v4_kit as kit, align_v4_session as session_mod, bytes_h_session as h
    now = now or time.time()
    packet_path = Path(session) / 'packet.json'
    if packet is not None:
        packet_path.write_text(json.dumps(packet))
    log = battery_log(Path(session) / 'battery.jsonl', now, kind)
    args = {'--session-root': str(session), '--w1-disk-config': str(disk),
            '--obc-off-attested-by': 'w1-prequal synthetic', '--battery-log': str(log),
            '--next-arm-triage': str(packet_path)}
    args.update(args_override or {})
    argv = ['install']
    for key, value in args.items():
        if key not in drop:
            argv += [key, value]
    real_install = session_mod.install
    real_h_install = h.install
    gate = lambda config: {'status': 'pass', 'offloads': [], 'synthetic': True}
    stderr = io.StringIO()
    from unittest import mock
    with mock.patch.object(session_mod, 'install', functools.partial(
            real_install, runner=host, volume_runner=host, disk_gate=gate, now=lambda: now,
            meter_probe=meter_probe or LIVE_METER, watchdog_check=host.watchdog_check,
            frequency_preflight=host.frequency_check, frequency_pre_t0=host.frequency_check)), \
            mock.patch.object(h, 'install', functools.partial(real_h_install, run=host, now=lambda: now)), \
            mock.patch.object(kit, 'generate', lambda *a, **k: None), \
            contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
        try:
            rc = session_mod.main(argv)
        except SystemExit as exc:      # argparse
            rc = exc.code
    records = sorted((Path(session) / 'staging').glob('v4-arm-*.json')) if (Path(session) / 'staging').exists() else []
    arm = json.loads(records[-1].read_text()) if records else None
    return {'rc': rc, 'stderr': stderr.getvalue(), 'arm': arm, 'installer_calls': list(host.installer_calls)}


# ---------------------------------------------------------------------------
# Checks


@check('weight-digest-preflight', 'RL-62: synthetic prepare and arm carry matching registered digests; '
       'changed weights refuse before install')
def check_weight_digest_preflight(ctx):
    from unittest import mock
    from scripts import align_v4_session as session_mod, bytes_h_session as h
    os.environ.setdefault('JOULEWISE_HOST_STATE_DIR', str(ctx.work / 'host-state'))
    Path(os.environ['JOULEWISE_HOST_STATE_DIR']).mkdir(parents=True, exist_ok=True)
    now = time.time()
    base, session, disk = arm_fixture(ctx, 'weight-digest', now=now)
    packet = valid_packet(ctx, base, now)
    host = FakeHost(now=now)
    state = h.read(session / 'session.json')
    with mock.patch.object(session_mod.pilot, 'prepare', return_value=state), \
            mock.patch.object(session_mod.kit, 'generate'), \
            mock.patch.object(session_mod, 'session_start_restore', return_value={'action': 'none'}), \
            contextlib.redirect_stdout(io.StringIO()):
        session_mod.prepare(base / 'measurement', session, weight_identity_fn=host.weight_identity,
                            runtime_runner=lambda python: SYNTHETIC_RUNTIME_STACK,
                            frequency_preflight=host.frequency_check)
        control = run_install(ctx, session, disk, packet, host=host, now=now)
        matching = (control['rc'] == 0 and bool(host.installer_calls) and
                    control['arm']['weight_digests'] == state['weight_digest_preflight'])
        refusal = ''
        try:
            session_mod.prepare(base / 'measurement', session,
                runtime_runner=lambda python: SYNTHETIC_RUNTIME_STACK,
                weight_identity_fn=lambda root: dict(host.weight_identity(root), folded_sha256='c' * 64),
                frequency_preflight=host.frequency_check)
        except ValueError as exc:
            refusal = str(exc)
        stored = h.read(session / 'session.json')['weight_digest_preflight']
        fresh_host = FakeHost(now=now)
        refused_arm = run_install(ctx, session, disk, packet, host=fresh_host, now=now)
    mismatch = ('weight_digest_preflight: digest_mismatch:' in refusal and not stored['ok'] and
                refused_arm['rc'] != 0 and not fresh_host.installer_calls)
    return result(PASS if matching and mismatch else FAIL, 'matching prepare/arm and changed-weight refusal',
                  matching_prepare_and_arm=matching, mismatch_refused=mismatch, refusal=refusal)


@check('runtime-stack-preflight', 'RL-73: matching synthetic installed stack passes prepare and arm; '
       'a changed Python version refuses and is carried to the arm')
def check_runtime_stack_preflight(ctx):
    from unittest import mock
    from scripts import align_v4_session as session_mod, bytes_h_session as h
    now = time.time()
    base, session, disk = arm_fixture(ctx, 'runtime-stack', now=now)
    packet = valid_packet(ctx, base, now)
    host = FakeHost(now=now)
    state = h.read(session / 'session.json')
    with mock.patch.object(session_mod.pilot, 'prepare', return_value=state), \
            mock.patch.object(session_mod.kit, 'generate'), \
            mock.patch.object(session_mod, 'session_start_restore', return_value={'action': 'none'}):
        session_mod.prepare(base / 'measurement', session, weight_identity_fn=host.weight_identity,
            runtime_runner=lambda python: SYNTHETIC_RUNTIME_STACK, frequency_preflight=host.frequency_check)
        control = run_install(ctx, session, disk, packet, host=host, now=now)
        matching = (control['rc'] == 0 and bool(host.installer_calls) and
                    control['arm']['runtime_stack'] == state['runtime_stack_preflight'])
        refusal = ''
        try:
            session_mod.prepare(base / 'measurement', session, weight_identity_fn=host.weight_identity,
                runtime_runner=lambda python: dict(SYNTHETIC_RUNTIME_STACK, python='changed'),
                frequency_preflight=host.frequency_check)
        except ValueError as exc:
            refusal = str(exc)
        fresh_host = FakeHost(now=now)
        arm = run_install(ctx, session, disk, packet, host=fresh_host, now=now)
    refused = ('runtime_stack_preflight: differs: python:' in refusal and arm['rc'] != 0
               and not fresh_host.installer_calls and not arm['arm']['runtime_stack']['ok'])
    return result(PASS if matching and refused else FAIL, 'matching stack and changed-stack refusal',
                  matching=matching, refused=refused, refusal=refusal)


@check('held-window', 'RL-79: an earlier final harvest hold refuses even when the previous window is provisional')
def check_held_window(ctx):
    from scripts import align_v4_session as session_mod
    root = ctx.work / 'held-window-records'
    root.mkdir()
    now = time.time()
    development = _fresh(_scenario_class()(root, 'W1'), now).finish()
    scenario = _fresh(_scenario_class()(root, 'C1', previous=development), now).finish()
    control = _arm_on_records(ctx, root, scenario.build(now=now), now=now)
    scenario.provisional = True
    scenario.sources['exclusions'].update(reasons=['records.source_changed_during_harvest'], claim_usable=False)
    scenario.finish()
    successor = _fresh(_scenario_class()(root, 'C2', previous=scenario, provisional=True,
                                       previous_final=True), now)
    successor.next_plan['window'] = 'C3'
    successor.finish()
    arm = _arm_on_records(ctx, root, successor.build(now=now), now=now)
    matching = control['admitted'] and control['held_window_check']['ok']
    refused = (not arm['admitted'] and
               'held_window: C1: records.source_changed_during_harvest: no signed ruling' in arm['reasons']
               and arm['held_window_check']['deferred'] == ['C2'])
    return result(PASS if matching and refused else FAIL, 'clean final harvest and held final harvest',
                  matching=matching, refused=refused, reasons=arm['reasons'])


@check('watchdog-hold-rollback', 'RL-56: pre-install hold refuses before install; post-install hold '
       'uninstalls this plan, verifies both labels absent and restores Automatic')
def check_watchdog_hold_rollback(ctx):
    from joulewise.night_agent_install import LABELS
    from scripts import bytes_h_session as h
    os.environ.setdefault('JOULEWISE_HOST_STATE_DIR', str(ctx.work / 'host-state'))
    Path(os.environ['JOULEWISE_HOST_STATE_DIR']).mkdir(parents=True, exist_ok=True)
    now = time.time()
    base, session, disk = arm_fixture(ctx, 'watchdog-hold', now=now, ac_powermode=2)
    packet = valid_packet(ctx, base, now)
    plan_path = h.read(session / 'session.json')['plan_path']
    rows, failures = [], []
    for phase in ('pre_install', 'post_install'):
        host = FakeHost(now=now, watchdog_state='HOLD_PLAN_MALFORMED' if phase == 'pre_install' else 'LAUNCHING',
                        watchdog_post_state='HOLD_PLAN_MALFORMED')
        out = run_install(ctx, session, disk, packet, host=host, now=now)
        refusal = f'watchdog_acceptance: {phase}: HOLD_PLAN_MALFORMED:'
        row = {'phase': phase, 'refused': out['rc'] != 0 and refusal in out['stderr'],
               'installer_called': bool(host.installer_calls)}
        if phase == 'pre_install':
            ok = row['refused'] and not row['installer_called']
        else:
            dwell = h.read(sorted((session / 'staging').glob('v4-arm-*.dwell.json'))[-1])
            undo = dwell['quiet_dwell']['watchdog_post_install'].get('install_undo', {})
            installs = host.installer_calls
            uninstalls = [call for call in installs if '--uninstall' in call]
            after_undo = host.calls[host.calls.index(uninstalls[0]) + 1:] if uninstalls else []
            restored = [h.read(p) for p in (session / 'staging').glob('v4-arm-restore-*.json')]
            row.update(uninstalled_this_plan=len(installs) == 2 and len(uninstalls) == 1
                       and all('--plan' in call and call[call.index('--plan') + 1] == plan_path for call in installs),
                       both_labels_verified_absent=bool(undo) and not undo.get('errors')
                       and not undo.get('remaining_labels') and not host.installed_labels
                       and all(any(call[:2] == ('launchctl', 'print') and call[-1].endswith('/' + label)
                                   for call in after_undo) for label in LABELS),
                       automatic_restored=host.mode == 0 and bool(restored) and all(r.get('ok') for r in restored)
                       and ('sudo', '-n', '/usr/bin/pmset', '-c', 'powermode', '2') in host.calls
                       and ('sudo', '-n', '/usr/bin/pmset', '-c', 'powermode', '0') in host.calls)
            ok = row['refused'] and all(row[k] for k in
                ('uninstalled_this_plan', 'both_labels_verified_absent', 'automatic_restored'))
        rows.append(row)
        if not ok:
            failures.append(f'{phase}: {row}; {tail(out["stderr"])}')
    return result(FAIL if failures else PASS, '; '.join(failures) if failures else
                  'both holds refused; installed jobs removed and Automatic restored', cases=rows)


@check('arm-cli', 'production arm CLI with every required arg: triage packet, top-up evidence, OBC '
       'attestation, W1 disk config; admits a correct setup and refuses each fault before the installer')
def check_arm_cli(ctx):
    os.environ.setdefault('JOULEWISE_HOST_STATE_DIR', str(ctx.work / 'host-state'))
    Path(os.environ['JOULEWISE_HOST_STATE_DIR']).mkdir(parents=True, exist_ok=True)
    rows, failures = [], []
    script = ctx.repo / 'scripts/align_v4_session.py'
    helped = ctx.run([ctx.python, '-B', script, 'install', '--help'], cwd=ctx.repo, timeout=120)
    missing = [f for f in REQUIRED_INSTALL_FLAGS if f not in helped.stdout]
    if helped.returncode or missing:
        failures.append(f'install --help rc={helped.returncode} missing={missing} {tail(helped.stderr)}')
    bare = ctx.run([ctx.python, '-B', script, 'install', '--session-root', ctx.work / 'nowhere'],
                   cwd=ctx.repo, timeout=120)
    unrequired = [f for f in REQUIRED_INSTALL_FLAGS if f not in bare.stderr]
    if bare.returncode != 2 or unrequired:
        failures.append(f'install without arm evidence must be a usage error naming every required flag; '
                        f'rc={bare.returncode} not named={unrequired}')
    now = time.time()

    def packet(base, mutate=None):
        value = valid_packet(ctx, base, now)
        if mutate:
            mutate(value)
        return value

    def edited(value):
        value['checks']['capture_faults'] = {'status': 'fail', 'basis': 'edited'}

    def old_schema(value):
        value.pop('schema')
        value['checks'].pop('full_desk_gate')

    def unknown_commit(value):
        value['record_commit'] = 'e' * 40
    cases = [
        # name, packet mutation (None: no packet file), host kwargs, cli overrides, dropped flags,
        # battery log kind, expected (admitted?, refusal substring)
        ('control', lambda v: None, {}, {}, (), 'completed', (True, None)),
        ('triage-missing', None, {}, {}, (), 'completed', (False, 'next-arm triage packet missing or wrong schema')),
        # Packet faults: the arm's rebuild refuses a supplied packet that differs (or cannot be rebuilt).
        ('triage-edited', edited, {}, {}, (), 'completed', (False, ('does not match', 'triage capture_faults failed'))),
        ('triage-stale-schema', old_schema, {}, {}, (), 'completed',
         (False, ('could not be rebuilt', 'does not match', 'missing or wrong schema'))),
        ('record-commit-unknown', unknown_commit, {}, {}, (), 'completed',
         (False, ('could not be rebuilt', 'does not match', 'triage record_committed failed'))),
        ('topup-no-charge', lambda v: None, {}, {}, (), 'no-charge', (False, 'completed top-up evidence missing')),
        ('topup-stale', lambda v: None, {}, {}, (), 'stale', (False, 'completed top-up evidence missing')),
        ('topup-future', lambda v: None, {}, {}, (), 'future', (False, 'completed top-up evidence missing')),
        ('obc-unattested', lambda v: None, {}, {'--obc-off-attested-by': ' '}, (), 'completed',
         (False, 'OBC off requires')),
        ('disk-image-mounted', lambda v: None, {'extra_mount': True}, {}, (), 'completed',
         (False, 'external_volume_mounted:/Volumes/JWSMOKE')),
        ('battery-charging', lambda v: None, {'charging': True}, {}, (), 'completed',
         (False, 'battery top-up incomplete')),
        ('powermode-mismatch', lambda v: None, {'mode': 2}, {}, (), 'completed', (False, 'ac_powermode')),
        ('meter-not-live', lambda v: None, {}, {}, (), 'completed', (False, 'triage meter_reader_live failed')),
    ]
    for name, mutate, host_kwargs, overrides, drop, kind, (admit, needle) in cases:
        base, session, disk = arm_fixture(ctx, 'arm-' + name, now=now)
        host = FakeHost(now=now, **host_kwargs)
        out = run_install(ctx, session, disk, None if mutate is None else packet(base, mutate), host=host,
                          args_override=overrides, drop=drop, now=now, kind=kind,
                          meter_probe=DEAD_METER if name == 'meter-not-live' else LIVE_METER)
        arm = out['arm'] or {}
        row = {'case': name, 'rc': out['rc'], 'admitted': arm.get('admitted'),
               'installer_called': bool(out['installer_calls']), 'reasons': arm.get('reasons')}
        rows.append(row)
        if admit:
            ok = (out['rc'] == 0 and arm.get('admitted') is True and len(out['installer_calls']) == 1
                  and '--plan' in out['installer_calls'][0])
        else:
            text = json.dumps(arm.get('reasons') or []) + out['stderr']
            needles = needle if isinstance(needle, tuple) else (needle,)
            ok = (out['rc'] != 0 and arm.get('admitted') is False and not out['installer_calls']
                  and any(n in text for n in needles))
        if not ok:
            failures.append(f'{name}: expected {"admit" if admit else "refusal " + repr(needle)}; got {row} '
                            f'{tail(out["stderr"], 300)}')
    if failures:
        return result(FAIL, '; '.join(failures), cases=rows)
    return result(PASS, f'{len(rows)} arm cases behave as documented (1 admit, {len(rows) - 1} refusals '
                  'before the installer)', cases=rows)


def _arm_on_records(ctx, measurement, packet_or_path, *, now, quiet=True):
    """The production ``arm_checks`` against a git measurement root, every host command faked."""
    from scripts import align_v4_session as session_mod
    log = battery_log(ctx.work / f'battery-{time.monotonic_ns()}.jsonl', now)
    host = FakeHost(now=now)
    # redirect_stdout swaps the process-wide sys.stdout: callers running arms in threads pass quiet=False
    # and redirect once around the whole pool (_arms).
    with contextlib.redirect_stdout(io.StringIO()) if quiet else contextlib.nullcontext():
        return session_mod.arm_checks(measurement, {'runtime_requirements': {'ac_powermode': 0}}, runner=host,
                                      volume_runner=host, obc_off_attested_by='w1-prequal synthetic',
                                      battery_log=log, now=lambda: now, next_arm_triage=packet_or_path,
                                      meter_probe=LIVE_METER, watchdog_check=host.watchdog_check)


# --- Packet-as-pointer design (lead ruling, 2026-11-08): the ARM REBUILDS the next-arm packet
# deterministically from the identities it names (record path and commit, series ledger, kit,
# receipt, lead rulings) and requires canonical equality, ignoring only these fields. Expiry is
# mandatory; window records are hash-chained to their predecessor; zero-capture retries are C3#2.
PACKET_IGNORED = ('pushed_tip', 'packet_preflight')
# The one exact nested exemption the arm applies (scripts/align_v4_next_arm_packet.canonical, delta4):
# the informational pushed tip inside the record_committed check is the same volatile pointer.
PACKET_NESTED_IGNORED = (('checks', 'record_committed', 'pushed_tip'),)
# W1, C1, C2, a zero-capture C3, its retry C3#2 (the fixer's attempt-id convention).
SERIES = (('C1', True), ('C2', True), ('C3', False), ('C3#2', True))


def _series_records(ctx, name, now):
    """A hash-chained series on the real record schema; returns the last window's scenario."""
    os.environ.setdefault('JOULEWISE_HOST_STATE_DIR', str(ctx.work / 'host-state'))
    Path(os.environ['JOULEWISE_HOST_STATE_DIR']).mkdir(parents=True, exist_ok=True)
    root = ctx.work / f'{name}-{time.monotonic_ns()}'
    root.mkdir(parents=True)
    Scenario = _scenario_class()
    previous = Scenario(root, 'W1').finish()
    for window, captured in SERIES:
        current = Scenario(root, window, previous=previous, captured=captured, eligible=True)
        if window == SERIES[-1][0]:
            _fresh(current, now)
        previous = current.finish()
    return previous


def _triage_ok(arm):
    """The arm admits the PACKET (host checks such as battery and powermode are judged elsewhere)."""
    return not any(str(r).startswith('next_arm_triage:') for r in arm.get('reasons', ()))


def _verdict(arm):
    return {'admitted': _triage_ok(arm), 'reasons': [r for r in arm.get('reasons', ())
                                                    if str(r).startswith('next_arm_triage:')][:6]}


def _find_rebuilt(value, depth=0):
    """The packet the arm rebuilt, as retained in its arm record (any key naming a rebuild)."""
    if depth > 6:
        return None
    if isinstance(value, dict):
        for key, item in value.items():
            if 'rebuil' in str(key).lower():
                if isinstance(item, dict) and ('schema' in item or 'checks' in item):
                    return item
                if isinstance(item, dict) and isinstance(item.get('packet'), dict):
                    return item['packet']
        for item in value.values():
            found = _find_rebuilt(item, depth + 1)
            if found is not None:
                return found
    return None


def _arm_file(ctx, measurement, packet, *, now, quiet=True):
    path = ctx.work / f'packet-{time.monotonic_ns()}-{threading.get_ident()}.json'
    path.write_text(json.dumps(packet, indent=2, sort_keys=True) + '\n')
    return _arm_on_records(ctx, measurement, path, now=now, quiet=quiet)


def _rebuild(ctx, name):
    """Series records, the producer's packet, the arm's verdict on it and the packet the arm rebuilt."""
    from scripts import align_v4_next_arm_packet as builder
    from joulewise.align.apple import v4_registration as reg
    now = time.time()
    scenario = _series_records(ctx, name, now)
    pointer = builder.build_packet(scenario.root, **scenario.identities(), now_epoch_s=now,
                                   current_artifact_set_sha256=reg.artifact_set_digest(scenario.root))
    arm = _arm_file(ctx, scenario.root, pointer, now=now)
    return scenario.root, scenario, now, pointer, arm, _find_rebuilt(arm)


PACKET_REFUSALS = ('does not match its committed sources', 'could not be rebuilt')
EXPIRY_REFUSALS = ('expired', 'valid_until')
_FLIP = {'pass': 'fail', 'fail': 'pass', 'not_applicable': 'pass', 'recorded': 'pass', 'deferred': 'pass'}


def _bump(value):
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        return value + 1
    if isinstance(value, str):
        if value in _FLIP:
            return _FLIP[value]
        return value + 'x' if not re.fullmatch(r'[0-9a-f]{40,64}', value) else ('f' if value[0] != 'f' else 'e') + value[1:]
    if isinstance(value, list):
        return value[:-1] if value else [{'injected': True}]
    if isinstance(value, dict):
        return {**value, 'injected': True}
    return 'injected' if value is None else None


def _leaves(value, path=()):
    """(path, leaf) for every scalar or empty container below ``value``."""
    if isinstance(value, dict) and value:
        for key in sorted(value):
            yield from _leaves(value[key], path + (key,))
    elif isinstance(value, list) and value:
        for index, item in enumerate(value):
            yield from _leaves(item, path + (index,))
    else:
        yield path, value


def _edit(packet, path, action):
    edited = copy.deepcopy(packet)
    parent = edited
    for step in path[:-1]:
        parent = parent[step]
    last = path[-1]
    if action == 'change':
        parent[last] = _bump(parent[last])
    elif action == 'remove':
        if isinstance(parent, dict):
            parent.pop(last)
        else:
            parent.pop(last)
    return edited


def _mutations(packet):
    """Single changes to a packet (ignored fields excluded): every top-level key changed or removed, an
    added key; in EVERY check entry and EVERY window_chain / calibration_windows element, every leaf at
    any depth changed and removed, plus a key added (S2-3, D6, D2-5: chain identity and digest leaves)."""
    for key in sorted(packet):
        if key in PACKET_IGNORED:
            continue
        yield f'changed {key}', {**packet, key: _bump(packet[key])}
        yield f'removed {key}', {k: v for k, v in packet.items() if k != key}
    yield 'added field', {**packet, 'injected_field': 'x'}
    for name, entry in sorted((packet.get('checks') or {}).items()):
        if not isinstance(entry, dict):
            continue
        if 'status' in entry:
            yield f'checks.{name}: status flipped', _edit(packet, ('checks', name, 'status'), 'change')
        for path, _leaf in _leaves(entry):
            if path == ('status',) or ('checks', name) + path in PACKET_NESTED_IGNORED:
                continue
            label = 'checks.' + name + '.' + '.'.join(map(str, path))
            yield label + ' changed', _edit(packet, ('checks', name) + path, 'change')
            yield label + ' removed', _edit(packet, ('checks', name) + path, 'remove')
        if 'status' in entry:
            yield f'checks.{name}: status removed', _edit(packet, ('checks', name, 'status'), 'remove')
        edited = copy.deepcopy(packet)
        edited['checks'][name]['injected'] = True
        yield f'checks.{name}: key added', edited
    for list_key in ('window_chain', 'calibration_windows'):
        for index, element in enumerate(packet.get(list_key) or []):
            if not isinstance(element, dict):
                continue
            for path, _leaf in _leaves(element):
                label = f'{list_key}[{index}].' + '.'.join(map(str, path))
                yield label + ' changed', _edit(packet, (list_key, index) + path, 'change')
                yield label + ' removed', _edit(packet, (list_key, index) + path, 'remove')
            edited = copy.deepcopy(packet)
            edited[list_key][index]['injected'] = True
            yield f'{list_key}[{index}] key added', edited


def _refused_for(arm, needles):
    """The arm refused the PACKET for one of the expected reasons (S3: not for an unrelated one)."""
    return any(n in str(r) for r in arm.get('reasons', ()) if str(r).startswith('next_arm_triage:') for n in needles)


def _arms(ctx, root, packets, now):
    from concurrent.futures import ThreadPoolExecutor
    with contextlib.redirect_stdout(io.StringIO()), ThreadPoolExecutor(max_workers=6) as pool:
        return list(pool.map(lambda packet: _arm_file(ctx, root, packet, now=now, quiet=False), packets))


def _zero_capture_attempt(packet):
    rows = packet.get('calibration_windows') or []
    return next((r.get('window') for r in rows if isinstance(r, dict) and r.get('captured_members') == 0), None)


def _omit_attempt(packet, attempt):
    """The packet with every list element naming ``attempt`` (window == attempt) removed: a chain hole."""
    removed = [0]

    def names(value):
        return isinstance(value, dict) and value.get('window') == attempt or value == attempt

    def walk(value):
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        if isinstance(value, list):
            kept = [walk(v) for v in value if not names(v)]
            removed[0] += len(value) - len(kept)
            return kept
        return value
    return walk(packet), removed[0]


@check('packet-rebuild', 'G1 (packet as pointer): the arm rebuilds the next-arm packet from the identities it names; '
       'a valid rebuild admits; ignored fields (pushed_tip, packet_preflight) may differ; expiry is mandatory: '
       'admits just before valid_until_epoch_s and refuses just after it FOR EXPIRY', gates='w1')
def check_packet_rebuild(ctx):
    root, scenario, now, pointer, arm, rebuilt = _rebuild(ctx, 'rebuild')
    evidence = {'pointer_verdict': _verdict(arm), 'series': ['W1', *(w for w, _ in SERIES)],
                'preflight': (pointer.get('packet_preflight') or {}).get('ready')}
    if rebuilt is None:
        return result(FAIL, 'the arm record carries no rebuilt packet: the arm does not rebuild the next-arm '
                      'packet from the identities it names (lead ruling: the packet is only a pointer). '
                      + GAP_REFS['packet-rebuild'], **evidence)
    valid = {**rebuilt, **{k: pointer[k] for k in PACKET_IGNORED if k in pointer}}
    expiry = valid.get('valid_until_epoch_s')
    evidence['valid_until_epoch_s'] = expiry
    if type(expiry) not in (int, float):
        return result(FAIL, 'the rebuilt packet carries no numeric valid_until_epoch_s (expiry is mandatory)',
                      **evidence)
    cases = {'rebuild': (valid, now),
             'ignored-fields-differ': ({**valid, 'pushed_tip': '0' * 40, 'packet_preflight': {'other': True}}, now),
             'just-before-expiry': (valid, expiry - 1), 'just-after-expiry': (valid, expiry + 1)}
    verdicts = {name: _arm_file(ctx, root, packet, now=at) for name, (packet, at) in cases.items()}
    evidence['verdicts'] = {k: _verdict(v) for k, v in verdicts.items()}
    failures = [f'{name} is refused: ' + '; '.join(evidence['verdicts'][name]['reasons'])[:300]
                for name in ('rebuild', 'ignored-fields-differ', 'just-before-expiry')
                if not _triage_ok(verdicts[name])]
    if not _refused_for(verdicts['just-after-expiry'], EXPIRY_REFUSALS):
        failures.append('one second past valid_until_epoch_s the packet is not refused for expiry')
    if failures:
        return result(FAIL, '; '.join(failures), **evidence)
    return result(PASS, 'the arm rebuilds the packet; a valid rebuild admits, ignored fields may differ; it admits '
                  '1 s before valid_until_epoch_s and is refused for expiry 1 s after', **evidence)


@check('packet-tamper', 'G1b (packet as pointer): with an admitted control, a packet that differs from the arm\'s '
       'rebuild in ANY field (top-level or nested check status/basis, chain elements) is refused as not matching '
       'its committed sources, and so is a chain that omits the zero-capture attempt', gates='w1')
def check_packet_tamper(ctx):
    root, scenario, now, pointer, arm, rebuilt = _rebuild(ctx, 'tamper')
    if rebuilt is None:
        return result(FAIL, 'the arm record carries no rebuilt packet, so no packet can be compared with the arm\'s '
                      'rebuild; today a field the arm does not re-derive is trusted as supplied. '
                      + GAP_REFS['packet-tamper'], pointer_verdict=_verdict(arm))
    valid = {**rebuilt, **{k: pointer[k] for k in PACKET_IGNORED if k in pointer}}
    control = _arm_file(ctx, root, valid, now=now)
    if not _triage_ok(control):
        return result(FAIL, 'the control (the arm\'s own rebuild) is refused, so no refusal below can be '
                      'attributed to tampering: ' + '; '.join(_verdict(control)['reasons'])[:300],
                      control=_verdict(control))
    mutations = list(_mutations(valid))
    attempt = _zero_capture_attempt(valid)
    holed, removed = _omit_attempt(valid, attempt) if attempt else (valid, 0)
    if removed:
        mutations.append((f'chain omits attempt {attempt}', holed))
    verdicts = _arms(ctx, root, [m for _, m in mutations], now)
    not_refused = [label for (label, _), verdict in zip(mutations, verdicts)
                   if not _refused_for(verdict, PACKET_REFUSALS)]
    evidence = {'mutations_tried': len(mutations), 'admitted_mutations': not_refused, 'zero_capture_attempt': attempt,
                'omitted_elements': removed, 'control': _verdict(control)}
    failures = []
    if not removed:
        failures.append('the rebuilt packet lists no zero-capture attempt: the chain does not list every attempt')
    if not_refused:
        failures.append(f'{len(not_refused)} of {len(mutations)} changes are not refused as a mismatch with the '
                        f'committed sources: {not_refused[:8]}')
    if failures:
        return result(FAIL, '; '.join(failures), **evidence)
    return result(PASS, f'control admits; all {len(mutations)} changes (top-level, nested check entries, chain '
                  f'elements, and the chain omitting {attempt}) are refused as mismatches', **evidence)


def _window(name, spam=7, bank=7, status='final', captured=22):
    return {'window': name, 'status': status, 'captured_members': captured,
            'eligible_benign': {'spam': spam, 'bank': bank}}


@check('calibration-stop', 'B3 fixed-8 calibration_stop over the planned C1-C8 manifest, the zero-capture '
       'cap rule, and its use inside the next-arm triage', gates='w1')
def check_calibration_stop(ctx):
    from joulewise.align.apple import v4_cadence as cad
    failures, trace = [], []
    planned = [_window(f'C{i}') for i in range(1, 9)]
    for n in range(0, 9):
        decision = cad.calibration_stop(planned[:n])['decision']
        expected = 'continue' if n < 8 else 'calibration_complete'
        trace.append((n, decision))
        if decision != expected:
            failures.append(f'after {n} planned windows: {decision} != {expected}')
    if cad.CAL_WINDOWS != 8 or cad.BENIGN_PER_PAIR_PER_WINDOW * cad.CAL_WINDOWS < cad.CAL_TARGET_PER_PAIR:
        failures.append('planned roster cannot reach the per-pair target in 8 windows')
    scenarios = {
        'zero-capture not counted': ([_window('C1'), _window('Z1', 0, 0, captured=0)] +
                                     [_window(f'C{i}') for i in range(2, 9)], 'calibration_complete'),
        'two zero-capture escalate': ([_window('C1'), _window('Z1', 0, 0, captured=0),
                                       _window('Z2', 0, 0, captured=0)], 'escalate_to_lead'),
        'provisional at 8': ([_window(f'C{i}') for i in range(1, 8)] + [_window('C8', status='provisional')],
                             'pending_final_eligibility'),
        'insufficient after 8': ([_window(f'C{i}', 4, 4) for i in range(1, 9)], 'insufficient_calibration'),
        'loss of two whole windows still completes': ([_window(f'C{i}', 0 if i < 3 else 7, 0 if i < 3 else 7)
                                                       for i in range(1, 9)], 'calibration_complete'),
        'loss of three whole windows is insufficient': ([_window(f'C{i}', 0 if i < 4 else 7, 0 if i < 4 else 7)
                                                         for i in range(1, 9)], 'insufficient_calibration'),
    }
    for name, (rows, expected) in scenarios.items():
        got = cad.calibration_stop(rows)['decision']
        trace.append((name, got))
        if got != expected:
            failures.append(f'{name}: {got} != {expected}')
    try:
        cad.calibration_stop([_window(f'C{i}') for i in range(1, 10)])
        failures.append('a ninth counted window was accepted')
    except ValueError:
        pass
    internal = {r['id']: True for r in cad.NEXT_ARM_TRIAGE if r['source'] == cad.ARM}
    bound = dict(record_commit='a' * 40, desk_digest='b' * 64, overrides={'valid_until_epoch_s': 2e9})
    identity = {'artifact_set_sha256': 'b' * 64, 'record_commit_exists': True, 'record_bound': True}
    arm_cases = {
        'W1 arm (previous R1)': (triage_packet(**bound), True),
        'C1 arm after W1': (triage_packet(previous='W1', role='calibration', windows=[], **bound), True),
        'test arm before calibration complete': (triage_packet(previous='C3', role='test',
                                                               windows=planned[:3], **bound), False),
        'calibration arm after C8': (triage_packet(previous='C8', role='calibration', windows=planned, **bound),
                                     False),
        'test arm after C8': (triage_packet(previous='C8', role='test', windows=planned, **bound), True),
    }
    for name, (packet, admit) in arm_cases.items():
        got = cad.next_arm_triage(packet, internal, identity, now_epoch_s=1.9e9)
        trace.append((name, got['admitted']))
        if got['admitted'] != admit:
            failures.append(f'{name}: admitted={got["admitted"]} expected {admit}: {got["reasons"]}')
    if failures:
        return result(FAIL, '; '.join(failures), trace=trace)
    return result(PASS, 'planned C1-C8 continues 8 times then completes; cap, provisional, insufficient and '
                  'triage integration behave as registered', trace=trace)


@check('cal-escalation-exit', 'after escalate_to_lead, a recorded lead ruling lets the next arm proceed '
       '(no permanent deadlock)', gates='w1')
def check_cal_escalation_exit(ctx):
    from joulewise.align.apple import v4_cadence as cad
    rows = [_window('C1'), _window('Z1', 0, 0, captured=0), _window('Z2', 0, 0, captured=0)]
    ruling = {'ruling_id': 'w1-prequal-synthetic', 'text_sha256': hashlib.sha256(b're-arm').hexdigest(),
              'resets': 'zero_capture_escalation', 'after_window': 'Z2',
              'lead_signature': 'lead: w1-prequal-synthetic 2026-11-08'}
    trace = {}
    try:
        trace['before'] = cad.calibration_stop(rows)['decision']
        trace['after_ruling'] = cad.calibration_stop(rows, [ruling])['decision']
        packet = triage_packet(previous='C1', role='calibration', windows=rows, rulings=[ruling],
                               record_commit='a' * 40, desk_digest='b' * 64, overrides={'valid_until_epoch_s': 2e9})
        arm = cad.next_arm_triage(packet, {r['id']: True for r in cad.NEXT_ARM_TRIAGE if r['source'] == cad.ARM},
                                  {'artifact_set_sha256': 'b' * 64, 'record_commit_exists': True, 'record_bound': True},
                                  now_epoch_s=1.9e9)
        trace['triage_admitted'] = arm['admitted']
        trace['triage_reasons'] = arm['reasons']
    except (ValueError, TypeError, AttributeError) as exc:
        trace['error'] = f'{type(exc).__name__}: {exc}'
    ok = (trace.get('before') == 'escalate_to_lead' and trace.get('after_ruling') == 'continue'
          and trace.get('triage_admitted') is True)
    if not ok:
        return result(FAIL, f'escalation does not resume on a signed lead ruling: {trace}. '
                      + GAP_REFS['cal-escalation-exit'], trace=trace)
    return result(PASS, 'two zero-capture refusals escalate; a signed lead_ruling row resets the count and the '
                  'triage admits the next calibration arm', trace=trace)


@check('kit-ready', 'kit --check on a clean clone of the candidate commit (drift, hash chain, W1 readiness)',
       gates='w1')
def check_kit_ready(ctx):
    clone = scratch_clone(ctx, 'kit-ready')
    try:
        out = ctx.run([ctx.python, '-B', 'scripts/align_v4_kit.py', '--check'], cwd=clone, timeout=600)
    finally:
        shutil.rmtree(clone, ignore_errors=True)
    message = (out.stderr or out.stdout).strip()
    if out.returncode == 0:
        return result(PASS, 'kit --check passes at the candidate', stdout=tail(out.stdout))
    if 'Traceback' in message or 'drift' in message.lower():
        return result(FAIL, 'kit --check crashed or drifted: ' + tail(message), rc=out.returncode)
    if any(m in message for m in PENDING_MARKERS):
        return pending_or_fail(ctx, 'kit-ready', 'kit not W1-ready: ' + tail(message, 400), rc=out.returncode)
    return result(FAIL, 'kit --check refused for an unexpected reason: ' + tail(message), rc=out.returncode)


@check('receipt', 'registration receipt validated against the candidate commit (and a self-test that the '
       'validator accepts an exact receipt and refuses a digest mismatch)', gates='w1')
def check_receipt(ctx):
    from joulewise.align.apple import v4_registration as reg
    clone = scratch_clone(ctx, 'receipt')
    try:
        commit = git(clone, 'rev-parse', 'HEAD', run=ctx.run)
        gate_doc = 'docs/align/v4/PREQUAL.md'
        artifacts = {}
        for path in reg.ARTIFACTS:
            local = clone / path
            artifacts[path] = reg.digest(local.read_bytes()) if local.is_file() else None
        absent = sorted(p for p, d in artifacts.items() if d is None)
        synthetic = {'schema': reg.RECEIPT_SCHEMA, 'status': 'registered', 'commit': commit,
                     'lead_signature': 'lead: w1-prequal-synthetic 2026-11-08',
                     'rulings': {str(n): 'installed' for n in reg.RULINGS}, 'artifacts': artifacts,
                     'gates': {s: {'verdict': 'ADMIT', 'path': gate_doc,
                                   'sha256': reg.digest((clone / gate_doc).read_bytes())} for s in 'AB'}}
        self_test = {}
        uncovered = sorted(p for p in executed_closure(clone) if p not in reg.ARTIFACTS)   # scripts too (S10)
        if uncovered:
            return result(FAIL, f'{len(uncovered)} executed modules are not bound by the receipt: {uncovered[:8]}',
                          uncovered=uncovered)
        if absent:
            return pending_or_fail(ctx, 'receipt', f'executed closure covered; {len(absent)} receipt-bound '
                                   f'artifacts are not committed at the candidate yet: {absent[:6]}', absent=absent)
        if True:
            try:
                reg.validate_receipt(copy.deepcopy(synthetic), clone)
                self_test['exact'] = 'admitted'
            except ValueError as exc:
                self_test['exact'] = f'refused: {exc}'
        tampered = copy.deepcopy(synthetic)
        victim = next(iter(sorted(p for p in artifacts if artifacts[p] and p != gate_doc)), None)
        if victim:
            tampered['artifacts'][victim] = 'f' * 64
            try:
                reg.validate_receipt(tampered, clone)
                self_test['digest_mismatch'] = 'admitted'
            except ValueError as exc:
                self_test['digest_mismatch'] = f'refused: {exc}'
        drifted = copy.deepcopy(synthetic)
        if victim:
            (clone / victim).write_bytes((clone / victim).read_bytes() + b'\n')
            try:
                reg.validate_receipt(drifted, clone)
                self_test['working_bytes_drift'] = 'admitted'
            except ValueError as exc:
                self_test['working_bytes_drift'] = f'refused: {exc}'
            git(clone, 'checkout', '--quiet', '--', victim, run=ctx.run)
        failures = []
        if self_test.get('exact') != 'admitted':
            failures.append('validator refuses an exact receipt: ' + str(self_test.get('exact')))
        for key in ('digest_mismatch', 'working_bytes_drift'):
            if 'digest drift' not in str(self_test.get(key)):
                failures.append(f'{key}: {self_test.get(key)}')
        if failures:
            return result(FAIL, '; '.join(failures), self_test=self_test)
        try:
            receipt = reg.require_registration(clone)
            real = 'registered'
            bound = receipt.get('commit')
            ancestor = ctx.run(['git', '-C', str(clone), 'merge-base', '--is-ancestor', bound, ctx.commit], timeout=60)
            if ancestor.returncode:
                real = f'receipt commit {bound} is not an ancestor of the candidate {ctx.commit}'
            dirty = ctx.run(['git', '-C', str(ctx.repo), 'status', '--porcelain'], timeout=60).stdout.strip()
            if dirty and real == 'registered':
                real = 'the candidate checkout is dirty; a receipt binds clean committed bytes only'
        except ValueError as exc:
            real = str(exc)
    finally:
        shutil.rmtree(clone, ignore_errors=True)
    if real == 'registered':
        return result(PASS, 'executed closure covered; committed receipt validates against the candidate '
                      '(its commit an ancestor, clean checkout)', self_test=self_test)
    return pending_or_fail(ctx, 'receipt', 'validator self-test passes; the committed receipt does not admit: '
                           + real, self_test=self_test, committed=real)


# --- Ported from the Sol build (align/2026-11-08-w1-smoke @ 8fd55af2a, joulewise/align/w1_prequal.py) ---
CLOSURE_ENTRIES = ('joulewise/align/apple/endpoint.py', 'scripts/run_night.py', 'scripts/align_v4_session.py')


def executed_closure(root):
    """The first-party static import closure of the W1 entry points, lazy imports included (Sol)."""
    import ast
    from joulewise.align.apple import v4_registration as reg
    root = Path(root)
    seen, todo = set(), list(CLOSURE_ENTRIES)
    while todo:
        relative = todo.pop()
        if relative in seen:
            continue
        seen.add(relative)
        parts = relative[:-3].split('/')[:-1]
        for node in ast.walk(ast.parse(reg._local(root, relative).read_bytes())):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                base = parts[:len(parts) - node.level + 1] if node.level else []
                name = '.'.join(base + ([node.module] if node.module else []))
                names = [name] + [name + '.' + a.name for a in node.names]
            for name in names:
                components = name.split('.')
                if components[0] not in ('joulewise', 'scripts'):
                    continue
                for end in range(1, len(components) + 1):
                    prefix = '/'.join(components[:end])
                    for candidate in (prefix + '.py', prefix + '/__init__.py'):
                        if (root / candidate).is_file() and candidate not in seen:
                            todo.append(candidate)
    return seen


SERIES_SCHEMA = 'joulewise.align_v4.smoke_series_plan.v1'
BATCH_ENCOUNTER_S = 11164
R1_BATCH_ENCOUNTER_S = 12964
R1_FOLLOWUP_FLOOR_S = 99768
R1_FOLLOWUP_SPAN_S = 108768
R1_FOLLOWUP_WINDOW_S = 126480


def _number(value, name):
    import math
    if type(value) not in (float, int) or not math.isfinite(value) or value < 0:
        raise ValueError(f'{name} must be finite and nonnegative')
    return value


def validate_series(plan):
    """A planning-only projection of the frozen series (Sol): one W1, C1-C8 in order, then tests.

    R24: up to six reserve windows C9..C14 (``replacement: true``, 7/7 benign) may follow C8; they are armed only
    to replace a structurally barred window and never change the fixed-8 predicate checked on C1-C8.
    """
    from joulewise.align.apple import v4_cadence as cad
    if plan.get('schema') != SERIES_SCHEMA:
        raise ValueError('missing planning-only series projection')
    windows = plan.get('windows')
    if not isinstance(windows, list) or not windows:
        raise ValueError('series projection needs windows in frozen order')
    ids = [w.get('window') for w in windows]
    if any(not isinstance(w, str) or not w.strip() for w in ids) or len(set(ids)) != len(ids):
        raise ValueError('series window ids must be nonempty and unique')
    every_calibration = [w for w in windows if w.get('role') == 'calibration']
    calibration = [w for w in every_calibration if w.get('replacement') is not True]
    reserves = [w for w in every_calibration if w.get('replacement') is True]
    if [w['window'] for w in calibration] != [f'C{i}' for i in range(1, 9)]:
        raise ValueError('planned calibration must be fixed C1-C8 in order')
    if ([w['window'] for w in reserves] != [f'C{i}' for i in range(9, 9 + len(reserves))]
            or len(reserves) > cad.REPLACEMENT_WINDOWS
            or [w['window'] for w in every_calibration] != [*(w['window'] for w in calibration), *(w['window'] for w in reserves)]
            or any(w.get('benign_per_pair') != {'spam': 7, 'bank': 7} for w in reserves)):
        raise ValueError('reserve windows must be C9.. in order after C8, flagged replacement, at most '
                         f'{cad.REPLACEMENT_WINDOWS}, with seven benign per pair (R24)')
    roles = [w.get('role') for w in windows]
    if any(r not in ('w1', 'calibration', 'test') for r in roles):
        raise ValueError('unknown series role')
    if roles != sorted(roles, key={'w1': 0, 'calibration': 1, 'test': 2}.get) or roles.count('w1') != 1:
        raise ValueError('freeze one W1, then calibration, then test windows')
    if 'test' not in roles:
        raise ValueError('test cohort must be declared separately')
    rows = []
    for w in calibration:
        if w.get('benign_per_pair') != {'spam': 7, 'bank': 7}:
            raise ValueError('planned default calibration roster needs seven benign per pair')
        rows.append({'window': w['window'], 'status': 'final', 'captured_members': cad.WINDOW_MEMBERS,
                     'eligible_benign': dict(w['benign_per_pair'])})
    decisions = [cad.calibration_stop(rows[:n])['decision'] for n in range(9)]
    if decisions != ['continue'] * 8 + ['calibration_complete']:
        raise ValueError('calibration predicate is not fixed-8 on the frozen series')
    return {'calibration_order': [w['window'] for w in calibration], 'reserve_order': [w['window'] for w in reserves],
            'decisions': decisions,
            'tests': [w['window'] for w in windows if w.get('role') == 'test']}


def validate_deadline(plan):
    """Size from explicit segments, every attempt and every possible batch encounter (Sol).

    RUN_STATE 215/216's 67,371 / 96,427 s floors are R1-only; W1/D keep their own spans.
    """
    maximum = _number(plan.get('window_max_s'), 'window_max_s')
    budget = plan.get('smoke_deadline_projection')
    if not isinstance(budget, dict) or budget.get('kind') not in ('r1', 'w1', 'd'):
        raise ValueError('installed plan needs a smoke_deadline_projection (r1, w1 or d)')
    segments = budget.get('segments')
    if not isinstance(segments, list) or not segments:
        raise ValueError('deadline projection needs the actual segment/retry schedule')
    total, retries, encounters = 0., 0, 0
    for seg in segments:
        attempts = seg.get('attempts')
        if type(attempts) is not int or attempts < 1:
            raise ValueError('segment attempts must include all permitted retries')
        possible = seg.get('batch_encounters')
        if type(possible) is not int or not 0 <= possible <= attempts:
            raise ValueError('batch_encounters must cover every attempt that can meet the blackout')
        retries += attempts - 1
        encounters += possible
        total += attempts * _number(seg.get('bound_s'), 'segment bound_s') + possible * (R1_BATCH_ENCOUNTER_S if budget['kind'] == 'r1' else BATCH_ENCOUNTER_S)
    overhead = sum(_number(budget.get(k), k) for k in ('bracket_s', 'close_s', 'harvest_s'))
    required = total + overhead
    if budget['kind'] == 'r1':
        required = max(required, R1_FOLLOWUP_WINDOW_S)
        if overhead < 9000:
            raise ValueError('R1 follow-up needs its 9000 s overhead allowance')
    if maximum < required:
        raise ValueError(f'window_max_s {maximum} < corrected requirement {required} s')
    return {'required_s': required, 'window_max_s': maximum, 'kind': budget['kind'], 'encounters': encounters,
            'retries': retries, 'overhead_s': overhead}


def _repo_json(ctx, relative):
    from joulewise.align.apple import v4_registration as reg
    raw = reg._local(ctx.repo, relative).read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


@check('series-manifest', 'Sol port, roster-bound: the frozen series projection (one W1, C1-C8 in order, then '
       'tests; 7/7 benign) equals the roster of the source manifest it names by sha256, and fixed-8 holds on it',
       gates='w1')
def check_series_manifest(ctx):
    from joulewise.align.apple import v4_registration as reg
    if not ctx.series_projection:
        return pending_or_fail(ctx, 'series-manifest', 'no --series-projection supplied: the frozen series '
                               'manifest is not projected yet (never inferred from outcomes)')
    value, digest = _repo_json(ctx, ctx.series_projection)
    source = value.get('source') or {}
    try:
        raw = reg._local(ctx.repo, source.get('path', '')).read_bytes()
    except (OSError, ValueError) as exc:
        return result(FAIL, f'series source manifest unreadable: {exc}')
    if hashlib.sha256(raw).hexdigest() != source.get('sha256'):
        return result(FAIL, 'series projection does not bind its frozen source manifest bytes')
    try:
        manifest = json.loads(raw)
    except ValueError:
        return result(FAIL, 'series source manifest is not JSON')
    roster = manifest.get('windows') if isinstance(manifest, dict) else None
    if not isinstance(roster, list) or not roster:
        return result(FAIL, 'series source manifest carries no window roster to project')
    canon = lambda rows: json.dumps(rows, sort_keys=True, separators=(',', ':'))
    if canon(roster) != canon(value.get('windows')):
        return result(FAIL, 'the projected roster differs from the hashed source manifest (order, roles, windows or '
                      'per-pair counts): a digest binds bytes, the roster must describe them (S2)')
    return result(PASS, 'series projection equals its source roster and is fixed-8', projection_sha256=digest,
                  source_sha256=source['sha256'], **validate_series({**value, 'windows': roster}))


def _find_key(value, key):
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for item in value.values():
            found = _find_key(item, key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = _find_key(item, key)
            if found is not None:
                return found
    return None


def plan_kind(plan_id):
    plan_id = str(plan_id or '')
    if plan_id.startswith('align-r1-'):
        return 'r1'
    if plan_id.startswith('align-v4-smoke-'):
        return 'smoke'
    if plan_id.startswith('align-v4-'):
        return 'w1'
    return None


DEADLINE_BUNDLE = ('night_plan.json', 'session.json', 'com.joulewise.night.plist')


@check('deadline', 'the INSTALLED plan sizes the window: an evidence bundle copied from the arm (night_plan.json, '
       'its session.json, the published com.joulewise.night.plist) must agree on one plan path and sha256; the '
       'plan must parse as a production NightPlan; its hazard_window.programmed_span_s through the plan writer\'s '
       'formula (and, for R1, the corrected floors) must fit window_max_s; its plan_id kind must be the next '
       'measurement', gates='r1')
def check_deadline(ctx):
    import plistlib
    from joulewise import night_gate
    from joulewise.align.apple import v4_registration as reg
    from joulewise.b6 import plan_inputs
    if not ctx.deadline_projection:
        return result(FAIL, 'no --deadline-projection supplied: pass the installed-plan evidence bundle (a '
                      'repo-relative directory with ' + ', '.join(DEADLINE_BUNDLE) + ' copied from the arm)')
    try:
        bundle = reg._local(ctx.repo, ctx.deadline_projection)
    except (OSError, ValueError) as exc:
        return result(FAIL, f'deadline bundle path refused: {exc}')
    if not bundle.is_dir():
        return result(FAIL, 'the deadline input must be the installed-plan evidence bundle (a directory with '
                      + ', '.join(DEADLINE_BUNDLE) + '); a lone plan or schedule file is not bound to what was '
                      'installed (D5/D2-4)')
    try:
        raw = {name: reg._local(ctx.repo, f'{ctx.deadline_projection}/{name}').read_bytes() for name in DEADLINE_BUNDLE}
        plan, session = json.loads(raw['night_plan.json']), json.loads(raw['session.json'])
        plist = plistlib.loads(raw['com.joulewise.night.plist'])
    except (OSError, ValueError, plistlib.InvalidFileException) as exc:
        return result(FAIL, f'deadline bundle unreadable: {exc}')
    digest = hashlib.sha256(raw['night_plan.json']).hexdigest()
    evidence = {'plan_sha256': digest, 'plan_id': plan.get('plan_id'),
                'bundle': {k: hashlib.sha256(v).hexdigest() for k, v in raw.items()}}
    try:
        night_gate.NightPlan.from_mapping(plan)
    except (night_gate.PlanError, ValueError, TypeError, KeyError) as exc:
        return result(FAIL, f'night_plan.json is not a valid installed NightPlan: {exc}', **evidence)
    args = [str(a) for a in plist.get('ProgramArguments') or []]
    plan_path = session.get('plan_path')
    install_argv = [str(a) for a in ((session.get('install') or {}).get('argv') or [])]
    custody = plan.get('custody_root')
    from joulewise.align.w1_smoke import plan_option
    # F5 / D3-4: the plan is the value of exactly one --plan option in each argv, in the intended
    # command shape; the path appearing as some other argument binds nothing.
    plist_shape = len(args) > 2 and Path(args[1]).name == 'run_night.py' and args[2] == 'run'
    installer_shape = (bool(install_argv) and Path(install_argv[0]).name == 'install_night_agent.sh'
                       and not {'--uninstall', '--render-only'} & set(install_argv))
    binding = {
        'plist runs the session plan': bool(plan_path) and plist_shape and plan_option(args) == plan_path,
        'session plan sha256 = copied plan bytes': session.get('plan_sha256') == digest,
        'session installer argv names the plan': bool(plan_path) and installer_shape
            and plan_option(install_argv) == plan_path,
        'installer exited 0': (session.get('install') or {}).get('exit_code') == 0,
        'plan path is the plan custody night_plan.json': bool(plan_path) and bool(custody) and
            Path(plan_path).name == 'night_plan.json' and _same_dir(Path(plan_path).parent, custody),
    }
    evidence['binding'] = binding
    if not all(binding.values()):
        return result(FAIL, 'the bundle does not bind one installed plan: '
                      + ', '.join(k for k, v in binding.items() if not v), **evidence)
    kind = plan_kind(plan.get('plan_id'))
    if kind != ctx.next:
        return result(FAIL, f'the installed plan {plan.get("plan_id")!r} is a {kind!r} plan, not the next '
                      f'measurement {ctx.next!r}', **evidence)
    hazard = plan.get('hazard_window') if isinstance(plan.get('hazard_window'), dict) else {}
    span, maximum = hazard.get('programmed_span_s'), plan.get('window_max_s')
    if type(span) not in (int, float) or type(maximum) not in (int, float):
        return result(FAIL, 'the installed plan carries no numeric hazard_window.programmed_span_s / window_max_s',
                      **evidence)
    required = plan_inputs.window_max_s({'programmed_span_s': {'seconds': span}})
    if kind == 'r1':
        required = max(required, R1_FOLLOWUP_WINDOW_S)
        if span < R1_FOLLOWUP_SPAN_S:
            return result(FAIL, 'R1 follow-up span omits required whole-unit redos/encounters/overhead', **evidence)
    evidence.update(kind=kind, programmed_span_s=span, window_max_s=maximum, required_s=required)
    if maximum < required:
        return result(FAIL, f'window_max_s {maximum} < {required} s required by the plan\'s own span', **evidence)
    return result(PASS, f'installed {kind} plan {plan.get("plan_id")} (sha {digest[:12]}, bound to its plist and '
                  f'session): window_max_s {maximum} >= {required} s (span {span} s)', **evidence)


def _same_dir(a, b):
    return os.path.normpath(os.path.abspath(str(a))) == os.path.normpath(os.path.abspath(str(b)))


def runbook_kit_steps(path):
    """The kit invocations in the runbook's shell block, in order: 'regenerate' or 'check'."""
    text = Path(path).read_text()
    steps, inside = [], False
    for line in text.splitlines():
        if line.strip().startswith('```'):
            inside = not inside
            continue
        code = line.split('#', 1)[0]
        if inside and 'align_v4_kit.py' in code:
            steps.append('check' if '--check' in code else 'regenerate')
    if 'check' not in steps:
        raise ValueError(f'{path} documents no kit --check step')
    return steps


@check('r1-w1-chain', 'R1 -> W1 chain on a synthetic lane-shaped R1 record: exporter, backfill-x-g, '
       'backfill-turn-counts, derive-contrast, decide, kit --check', gates='w1')
def check_r1_w1_chain(ctx):
    from unittest import mock
    from scripts import align_r1_rehearsal as r1, align_v4_kit as kit
    from tests.align import test_r1_rehearsal as rehearsal
    from tests.align.test_r1_turn_counts_export import write_bundles
    clone = scratch_clone(ctx, 'chain')
    data = ctx.work / 'chain-data'
    data.mkdir(parents=True, exist_ok=True)
    steps, failures = [], []
    try:
        with mock.patch.object(r1, '_run', rehearsal.FakeWorld(step_d_rate=40.0, gated_decode_tokens=28000,
                                                               gated_admitted_turns=7)), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            if r1.run(rehearsal.R1Tests.args(None, str(data), synthetic=True)) != 0:
                raise RuntimeError('synthetic R1 rehearsal did not complete')
        run_dir = data / 'run'
        write_bundles(run_dir, drop_bundle_key=True)
        slots = json.loads((data / 'registration/r1_slots.json').read_text())
        for key in ('admitted_turns', 'x7', 'phases_s'):
            slots['x_g'].pop(key, None)
        for row in slots['deadman_budget']:
            for key in ('turn_decode_counts', 'turn_completed', 'turn_counts_source_sha256'):
                row.pop(key, None)
        lane_slots = data / 'lane_r1_slots.json'
        lane_slots.write_text(json.dumps(slots))
        work = data / 'work'
        work.mkdir()
        py = [ctx.python, '-B']
        procedure = 'scripts/align_w1_budget_procedure.py'
        plan = [
            ('export', py + ['scripts/align_r1_turn_counts_export.py', '--run-dir', run_dir,
                             '--out', work / 'turn_counts_export.json']),
            ('backfill-x-g', py + [procedure, 'backfill-x-g', '--r1-slots', lane_slots,
                                   '--r1-result', run_dir / 'r1_result.json', '--out', work / 'r1_slots.xg.json']),
            ('backfill-turn-counts', py + [procedure, 'backfill-turn-counts', '--r1-slots', work / 'r1_slots.xg.json',
                                           '--counts-export', work / 'turn_counts_export.json',
                                           '--out', work / 'r1_slots.json']),
        ]
        for name, argv in plan:
            out = ctx.run(argv, cwd=clone, timeout=300)
            steps.append({'step': name, 'rc': out.returncode, 'stderr': tail(out.stderr, 300)})
            if out.returncode:
                failures.append(f'{name} rc={out.returncode}: {tail(out.stderr, 300)}')
                break
        if not failures:
            done = json.loads((work / 'r1_slots.json').read_text())
            inputs = rehearsal.R1Tests.bind_inputs(copy.deepcopy(done))
            x_turns = inputs['WP18']['X']['max_turns']
            syn_inputs = data / 'inputs.synthetic.json'
            syn_inputs.write_text(json.dumps({'WP18': {'X': {'max_turns': x_turns}}}))
            out = ctx.run(py + [procedure, 'derive-contrast', '--r1-slots', work / 'r1_slots.json',
                                '--inputs', syn_inputs], cwd=clone, timeout=300)
            steps.append({'step': 'derive-contrast', 'rc': out.returncode, 'stderr': tail(out.stderr, 300)})
            contrast = json.loads(out.stdout) if out.returncode == 0 else None
            policy = inputs['R1']['thermal_policy']
            if contrast is None:
                failures.append(f'derive-contrast rc={out.returncode}: {tail(out.stderr, 300)}')
            elif contrast != {'contrast_g0_cap_s': policy['contrast_g0_cap_s'], 'contrast_fit': policy['contrast_fit']}:
                failures.append('derive-contrast output differs from the kit re-derivation on the same record')
            out = ctx.run(py + [procedure, 'decide', '--r1-slots', work / 'r1_slots.json', '--inputs', syn_inputs,
                                '--draft-out', work / 'ruling_1f_draft.json'], cwd=clone, timeout=300)
            steps.append({'step': 'decide', 'rc': out.returncode, 'stdout': tail(out.stdout, 300),
                          'stderr': tail(out.stderr, 300)})
            if out.returncode or 'Traceback' in (out.stderr or ''):
                failures.append(f'decide rc={out.returncode}: {tail(out.stderr, 300)}')
        if not failures:
            with contextlib.redirect_stdout(io.StringIO()):
                kit.require_ready(inputs, done, synthetic=True)
            steps.append({'step': 'kit.require_ready(backfilled record)', 'rc': 0})
            (clone / kit.R1_SLOTS).write_text(json.dumps(done, indent=2, sort_keys=True) + '\n')
            real_inputs_path = clone / kit.INPUTS
            real_inputs = json.loads(real_inputs_path.read_text())
            real_policy = (real_inputs.get('R1') or {}).get('thermal_policy')
            if isinstance(real_policy, dict):     # runbook step 4: paste both contrast fields
                real_policy.update(contrast)
                real_inputs_path.write_text(json.dumps(real_inputs, indent=2, sort_keys=True) + '\n')
            documented = runbook_kit_steps(clone / 'docs/align/R1-TO-W1-CHAIN.md')
            steps.append({'step': 'runbook kit steps', 'documented': documented})
            if 'regenerate' in documented and documented.index('regenerate') < documented.index('check'):
                regen = ctx.run(py + ['scripts/align_v4_kit.py'], cwd=clone, timeout=600)
                steps.append({'step': 'kit regenerate (runbook)', 'rc': regen.returncode,
                              'stderr': tail(regen.stderr, 300)})
            out = ctx.run(py + ['scripts/align_v4_kit.py', '--check'], cwd=clone, timeout=600)
            message = (out.stderr or out.stdout).strip()
            steps.append({'step': 'kit --check (record installed)', 'rc': out.returncode, 'stderr': tail(message, 400)})
            if out.returncode and 'drifted' in message:
                # R1-TO-W1-CHAIN.md runs --check straight after installing the record; the record
                # feeds generated configs, so the documented sequence needs a regeneration first.
                failures.append('R1-TO-W1-CHAIN.md as written: kit --check reports drift after the record is '
                                'installed (the runbook runs no `align_v4_kit.py` regeneration before --check). '
                                + GAP_REFS['r1-w1-chain'] + ': ' + tail(message, 200))
                regen = ctx.run(py + ['scripts/align_v4_kit.py'], cwd=clone, timeout=600)
                out = ctx.run(py + ['scripts/align_v4_kit.py', '--check'], cwd=clone, timeout=600)
                message = (out.stderr or out.stdout).strip()
                steps.append({'step': 'kit regenerate + --check', 'regen_rc': regen.returncode,
                              'rc': out.returncode, 'stderr': tail(message, 400)})
            if 'Traceback' in message:
                failures.append('kit --check crashed on the installed record: ' + tail(message, 400))
            elif out.returncode and any(k in message for k in ('R11 contrast', 'turn opportunity', 'x_g',
                                                                'turn_decode_counts', 'admitted_turns', 'drifted')):
                failures.append('kit --check refuses the backfilled R1 evidence: ' + tail(message, 400))
    finally:
        shutil.rmtree(clone, ignore_errors=True)
    if failures:
        return result(FAIL, '; '.join(failures), steps=steps)
    return result(PASS, 'chain runs end to end; the backfilled record binds in require_ready; kit --check '
                  'refuses only on still-pending non-R1 inputs (or passes)', steps=steps)


FAKE_LIVE_METER = r'''
import json, pathlib, signal, struct, sys, time
out = pathlib.Path(sys.argv[sys.argv.index("--out") + 1])
SAMPLE = struct.Struct("<HHiiHHHH")
stop = {"reason": None}
def on_signal(number, _frame):
    stop["reason"] = "signal %d" % number
for number in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(number, on_signal)
OFFSET = 7_000_000_000
start = time.monotonic_ns()
with open(out, "x") as handle:
    handle.write(json.dumps({"k": "h", "schema": "joulewise.km003c_stream.v1", "status": "streaming",
                             "rate_idx": 2, "start_raw_ns": start + OFFSET, "start_mono_ns": start}) + "\n")
    handle.flush()
    k = 0
    while stop["reason"] is None:
        due = start + k * 20_000_000
        delay = (due - time.monotonic_ns()) / 1e9
        if delay > 0:
            time.sleep(delay)
        rx = due + OFFSET    # scheduled host time: deterministic clock fit under CPU load
        payload = SAMPLE.pack((k * 20) % 65536, 0, 28_000_000, 1_000_000, 0, 0, 0, 0)
        handle.write(json.dumps({"k": "b", "tx": rx - 1000, "rx": rx, "rt": 0, "n": 1, "p": payload.hex(),
                                 "smc": {}}) + "\n")
        handle.flush()
        k += 1
    end = time.monotonic_ns()
    handle.write(json.dumps({"k": "t", "end_raw_ns": end + OFFSET, "end_mono_ns": end,
                             "stop_reason": stop["reason"]}) + "\n")
'''


def _synthetic_member(runs, run_id, span_ns, baseline_ns):
    from joulewise.align.records import Episode, Turn, to_jsonable
    a, b = span_ns
    episode = Episode(episode_id=run_id, task_pair='synthetic', condition='benign', agent_model='synthetic',
                      endpoint='synthetic', seed=1, clock_domain='synthetic.monotonic_ns',
                      start_ns=baseline_ns[1], end_ns=b - 10_000_000,
                      turns=(Turn(0, baseline_ns[1], b - 10_000_000, 10, 2, 3),))
    bundle = runs / run_id
    (bundle / 'outputs').mkdir(parents=True)
    (bundle / 'outputs/align_episode.json').write_text(json.dumps(to_jsonable(episode)))
    s = lambda ns: ns / 1e9
    stamps = {name: {'monotonic_before_s': s(x), 'monotonic_after_s': s(x), 'epoch_s': 1e9 + s(x)}
              for name, x in (('pre_spawn', a), ('sampling_started', baseline_ns[1]),
                              ('sampling_stopped', b), ('post_parse', b))}
    (bundle / 'metadata.json').write_text(json.dumps({'uncertainty_evidence': {'clock_anchor': {'clock_stamps': stamps}}}))
    events = [{'event_type': 'stage_started', 'phase': 'idle_baseline', 'timestamp_s': 1e9 + s(baseline_ns[0]),
               'metadata': {'monotonic_ns': baseline_ns[0]}},
              {'event_type': 'stage_completed', 'phase': 'idle_baseline', 'timestamp_s': 1e9 + s(baseline_ns[1])}]
    (bundle / 'events.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in events))
    return {'run_id': run_id, 'condition': 'benign', 'task_pair': 'synthetic', 'model_id': 'synthetic',
            'seed_index': 1}


def _meter_window(kill_mid=False):
    """Run the real HAZARD_PACK driver (run_night's) with the live fake meter; return custody paths."""
    import shlex
    import unittest
    from dataclasses import replace
    from unittest import mock
    from tests.test_b5_driver import Harness
    from tests.process_reaper import kill_and_wait
    case = unittest.TestCase()
    harness = Harness(case, g10=False)
    children = []
    real_popen = subprocess.Popen

    def popen(*args, **kwargs):
        process = real_popen(*args, **kwargs)
        children.append(process)
        return process
    original = harness.seams
    harness.driver._hazard_seams = lambda: replace(original(), popen=popen)
    census = mock.patch.object(harness.driver, '_group_census', return_value=(True, ['synthetic absence']))
    census.start()
    marker = 'jw-w1-prequal-meter-' + hashlib.sha256(str(harness.root).encode()).hexdigest()[:10]
    stream1 = harness.custody / 'hazards/meter/stream-001.jsonl'
    chain = ('#!/bin/zsh -f\n'
             'for i in {1..200}; do\n'
             f'  [[ -s {shlex.quote(str(stream1))} ]] && break\n'
             '  /bin/sleep 0.05\ndone\n'
             '/bin/sleep 1.5\n')
    if kill_mid:
        stream2 = harness.custody / 'hazards/meter/stream-002.jsonl'
        chain += (f'/usr/bin/pkill -KILL -f {shlex.quote(marker)}\n'
                  'for i in {1..600}; do\n'
                  f'  [[ -s {shlex.quote(str(stream2))} ]] && break\n'
                  '  /bin/sleep 0.05\ndone\n'
                  '/bin/sleep 2\n')
    else:
        chain += '/bin/sleep 1.5\n'
    harness.replace_chain(chain)

    def meter_argv(request):
        from joulewise.b5 import driver as b5_driver
        out_dir = Path(request.custody_root).joinpath(*b5_driver.METER_STREAM_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)
        return [sys.executable, '-c', FAKE_LIVE_METER, marker, '--out', str(b5_driver.next_meter_stream(out_dir))]
    harness.meter_argv = meter_argv
    try:
        code = harness.run()
        return case, harness, code, census
    except BaseException:
        census.stop()
        for process in children:
            kill_and_wait(process)
        case.doCleanups()
        raise


@check('km003c-launch', 'KM003C reader launched through the shared HAZARD_PACK driver with a stand-in meter: '
       'stream custody, SIGTERM stop, restart after a kill, per-member DC-missing flag, rails untouched', gates='r1')
def check_km003c_launch(ctx):
    from joulewise.align.apple import km003c
    from joulewise.external import km003c_parse as kp
    failures, evidence = [], {}
    for variant in ('clean', 'killed'):
        case, harness, code, census = _meter_window(kill_mid=variant == 'killed')
        try:
            meter = harness.hazard().get('meter') or {}
            streams = meter.get('streams') or []
            evidence[variant] = {'exit': code, 'starts': meter.get('starts'), 'restarts': meter.get('restarts'),
                                 'streams': [s.get('path') for s in streams],
                                 'proven_stopped': (meter.get('stop') or {}).get('proven_stopped')}
            if code != harness.driver.EXIT_GO:
                failures.append(f'{variant}: driver exit {code}')
                continue
            if not (meter.get('stop') or {}).get('proven_stopped') or not streams:
                failures.append(f'{variant}: meter not proven stopped or no stream in custody')
                continue
            for row in streams:
                path = harness.custody / row['path']
                if row.get('sha256') != hashlib.sha256(path.read_bytes()).hexdigest():
                    failures.append(f'{variant}: custody digest mismatch for {row["path"]}')
            parsed = [kp.parse(harness.custody / s['path']) for s in streams]
            runs = harness.root / 'synthetic-runs'
            plan, summaries = [], []
            if variant == 'clean':
                host = parsed[0].host_ns
                off = kp.raw_offset_ns(parsed[0]) or 0
                lo, hi = host[0] - off, host[-1] - off
                span = (lo + 200_000_000, hi - 200_000_000)
                plan.append(_synthetic_member(runs, 'member-clean', span, (span[0], span[0] + 300_000_000)))
                expect = {'member-clean': ('available', None)}
            else:
                if len(streams) < 2 or meter.get('restarts', 0) < 1:
                    failures.append(f'killed: meter not restarted into a new stream ({evidence[variant]})')
                    continue
                first = parsed[0]
                second = parsed[1]
                off2 = kp.raw_offset_ns(second) or 0
                lo1 = first.poll_ns[0] - 7_000_000_000 if first.poll_ns else None
                lo2, hi2 = second.host_ns[0] - off2, second.host_ns[-1] - off2
                straddle = (lo1 + 100_000_000, lo2 + 500_000_000)
                inside = (lo2 + 200_000_000, hi2 - 200_000_000)
                plan.append(_synthetic_member(runs, 'member-straddles-kill', straddle,
                                              (straddle[0], straddle[0] + 300_000_000)))
                plan.append(_synthetic_member(runs, 'member-after-restart', inside,
                                              (inside[0], inside[0] + 300_000_000)))
                expect = {'member-straddles-kill': ('missing', 'meter.'),
                          'member-after-restart': ('available', None)}
            summaries = [{'run_id': m['run_id'], 'excluded': False, 'summary': {'configuration': {}}} for m in plan]
            before = json.dumps(summaries, sort_keys=True)
            report = km003c.session_report(harness.custody, plan, runs, summaries)
            if json.dumps(summaries, sort_keys=True) != before:
                failures.append(f'{variant}: the DC desk mutated rail admission')
            got = {}
            for rid, (status, flag) in expect.items():
                row = report['members'][rid]
                got[rid] = {'status': row['status'], 'flags': row['flags']}
                if row['status'] != status or (flag and not any(f.startswith(flag) for f in row['flags'])):
                    failures.append(f'{variant}: {rid} {row["status"]} {row["flags"]} (expected {status} {flag or ""})')
            evidence[variant]['members'] = got
        finally:
            census.stop()
            case.doCleanups()
    from joulewise.b5 import driver as b5_driver
    from scripts import align_v4_kit as kit
    request = b5_driver.MonitorRequest(None, ctx.work / 'plan.json', ctx.work, ctx.work / 'night', 1)
    argv = b5_driver.production_seams(ctx.repo).meter_argv(request)
    if Path(argv[-3]).name != 'km003c_monitor.py' or not Path(argv[-3]).is_file():
        failures.append(f'production meter argv does not name the KM003C reader: {argv}')
    plan = json.loads((ctx.repo / kit.KIT / 'collection_plan.json').read_bytes())
    try:
        km003c.require_enabled(plan)
    except ValueError as exc:
        failures.append(f'W1 collection plan does not enable the reader: {exc}')
    if failures:
        return result(FAIL, '; '.join(failures), **evidence)
    return result(PASS, 'meter starts with the window, is SIGTERM-stopped and hashed; a SIGKILLed reader restarts '
                  'into a new stream; the straddling member reads DC missing with a meter.* flag, others available',
                  **evidence)


@check('km003c-crash-radius', 'a KM003C reader crash costs DC only for the member it interrupts (protocol: '
       '"one dropped counter makes that member\'s DC channel missing"), not every earlier member of its stream',
       gates='w1')
def check_km003c_crash_radius(ctx):
    from joulewise.align.apple import km003c
    from joulewise.external import km003c_parse as kp
    case, harness, code, census = _meter_window(kill_mid=True)
    try:
        meter = harness.hazard().get('meter') or {}
        streams = meter.get('streams') or []
        if code != harness.driver.EXIT_GO or len(streams) < 2:
            return result(FAIL, f'window did not run with a restarted meter (exit {code}, {len(streams)} streams)')
        first = kp.parse(harness.custody / streams[0]['path'])
        polls = [t - 7_000_000_000 for t in first.poll_ns]
        before = (polls[0] + 100_000_000, polls[0] + 900_000_000)
        runs = harness.root / 'synthetic-runs'
        plan = [_synthetic_member(runs, 'member-before-kill', before, (before[0], before[0] + 300_000_000))]
        summaries = [{'run_id': 'member-before-kill', 'excluded': False, 'summary': {'configuration': {}}}]
        row = km003c.session_report(harness.custody, plan, runs, summaries)['members']['member-before-kill']
    finally:
        census.stop()
        case.doCleanups()
    evidence = {'member_before_kill': {'status': row['status'], 'flags': row['flags']},
                'stream_001_trailer': first.trailer is not None}
    if row['status'] != 'available':
        return result(FAIL, f'a member that ended before the reader was SIGKILLed reads DC {row["status"]} '
                      f'{row["flags"]}: a killed stream has no trailer, so raw_offset_ns is unresolved for the '
                      'whole stream and every earlier member loses DC (km003c_parse.raw_offset_ns documents a '
                      'monitor-journal offset fallback that km003c.capture_member does not implement)', **evidence)
    return result(PASS, 'members before a reader crash keep DC', **evidence)


def synthetic_w1_plan(ctx):
    """The W1 template filled with the planning member_s and synthetic R1 values (WP22 inputs)."""
    from scripts import align_v4_kit as kit, validate_align_v4_w1_plan as validator
    from scripts import align_v4_w1_synthetic as dry
    preview = json.loads((ctx.repo / kit.KIT / 'registration/sizing_preview.json').read_bytes())
    seconds = preview['member_seconds']
    plan = validator.build_template(json.loads((ctx.repo / kit.KIT / 'collection_plan.json').read_bytes()))
    inputs = copy.deepcopy(dry.SYN_INPUTS)
    slots = copy.deepcopy(dry.SYN_R1_SLOTS)
    align = plan['align_v4']
    r1 = inputs['R1']
    align.update(B_D=r1['B_D'], I_D=r1['I_D'], T_dead=r1['T_dead'], max_r1_tail_s=slots['max_r1_tail_s'],
                 effort=inputs['R0']['reasoning_effort'], status='SYNTHETIC_W1_PREQUAL',
                 thermal_policy=copy.deepcopy(r1['thermal_policy']))
    for row in align['members']:
        role = row['role']
        row['member_s'] = seconds['anchor'] if role == 'anchor' else seconds['D'] if role == 'D' else (
            seconds['G'] if role.endswith('G') else seconds['S'])
    a = align['arithmetic']
    a['align_s'] = sum(r['member_s'] for r in align['members'])
    import math
    a['programmed_span_s'] = math.ceil(a['scaffold_s'] + a['align_s'])
    plan['window_max_s'] = 60 * math.ceil((a['programmed_span_s'] + a['t0_stage_cap_s'] + a['pause_limit_s']
                                           + a['session_wait_budget_s']) / 60)
    plan['plan_id'] = 'align-v4-w1-synthetic-prequal'
    return plan, inputs, slots


@check('w1-window-max', 'W1 window_max_s sizing: validator, kit sizing and the plan writer agree; caps hold at '
       'the planning worst case; no unplanned wait (the R1 batch blackout class) in W1-executed code', gates='w1')
def check_w1_window_max(ctx):
    import math
    from joulewise.b5 import plan as b5_plan
    from joulewise.b6 import plan_inputs
    from joulewise.align.apple import v4_registration as reg
    from scripts import align_v4_kit as kit, validate_align_v4_w1_plan as validator
    failures, evidence = [], {}
    plan, inputs, slots = synthetic_w1_plan(ctx)
    try:
        checked = validator.validate(plan, inputs, slots)
    except ValueError as exc:
        return result(FAIL, f'validator refuses the planning-worst-case W1 plan: {exc}')
    span = checked['programmed_span_s']
    writer = plan_inputs.window_max_s({'programmed_span_s': {'seconds': span}})
    formula = 60 * math.ceil((span + b5_plan.T0_STAGE_CAP_S + b5_plan.PAUSE_LIMIT_S
                              + b5_plan.SESSION_WAIT_BUDGET_S) / 60)
    evidence.update(programmed_span_s=span, validator_window_max_s=checked['window_max_s'],
                    writer_window_max_s=writer, b5_formula=formula, window_cap_s=validator.WINDOW_CAP_S,
                    span_cap_s=validator.SPAN_CAP_S)
    if not checked['window_max_s'] == writer == formula:
        failures.append(f'window_max_s disagrees: validator {checked["window_max_s"]}, prepare/plan writer '
                        f'{writer}, b5 formula {formula}')
    if span > validator.SPAN_CAP_S or checked['window_max_s'] > validator.WINDOW_CAP_S:
        failures.append('planning worst case exceeds the span/window cap')
    try:
        kit.check_l1_member_fit(inputs['R1']['I_D'], inputs['R1']['T_dead'], slots['max_r1_tail_s'])
    except ValueError as exc:
        failures.append(f'L1 member fit: {exc}')
    if max(r['member_s'] for r in plan['align_v4']['members']) > kit.MEMBER_CAP_S:
        failures.append('a planning member exceeds the 1,800 s spent cap')
    # The R1 lesson (RUN_STATE 214-216): a wait outside the programmed member time. Scan the
    # static import closure of the W1 entry points (not the receipt's set, which also binds R1).
    import ast
    hits = []
    for path in sorted(executed_closure(ctx.repo)):
        file = ctx.repo / path
        if file.suffix != '.py' or not file.is_file():
            continue
        for node in ast.walk(ast.parse(file.read_bytes())):
            if isinstance(node, ast.Call):
                name = getattr(node.func, 'id', None) or getattr(node.func, 'attr', None)
                if name in ('wait_outside_os_batch',):
                    hits.append(path)
                    break
    evidence['unplanned_wait_sources'] = hits
    if hits:
        failures.append(f'W1-executed code waits outside the programmed span: {hits}')
    committed = ctx.repo / kit.W1_PLAN
    if committed.is_file():
        try:
            real = validator.validate(json.loads(committed.read_bytes()))
            evidence['committed_w1_plan'] = real
            if real['window_max_s'] != plan_inputs.window_max_s({'programmed_span_s': {'seconds': real['programmed_span_s']}}):
                failures.append('committed W1 plan window_max_s disagrees with the plan writer')
        except ValueError as exc:
            failures.append(f'committed W1 plan refused: {exc}')
    if failures:
        return result(FAIL, '; '.join(failures), **evidence)
    if not committed.is_file():
        return pending_or_fail(ctx, 'w1-window-max', f'sizing code paths agree at the planning worst case '
                               f'(span {span} s, window_max_s {writer} s <= {validator.WINDOW_CAP_S}); no unplanned '
                               f'waits in the W1 closure; the R1-filled {kit.W1_PLAN} is not committed yet',
                               **evidence) if ctx.next == 'w1' else result(
            PASS, f'sizing code paths agree at the planning worst case (span {span} s, window_max_s {writer} s '
            f'<= {validator.WINDOW_CAP_S}); no unplanned waits in the W1 closure', **evidence)
    return result(PASS, 'committed W1 plan and all sizing code paths agree', **evidence)


@check('wp22-dry-run', 'WP22 synthetic W1 dry run in full (JW_WP22_FULL=1, all 18 members, injected faults and '
       'the clean window) plus the minimal witness', gates='w1')
def check_wp22(ctx):
    env = {**os.environ, 'JW_WP22_FULL': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
    witness_out = ctx.work / 'wp22-witness'
    witness = ctx.run([ctx.python, '-B', 'scripts/align_v4_w1_synthetic.py', witness_out, '--inject', 'none',
                       '--members', '5'], cwd=ctx.repo, env=env, timeout=600)
    record = witness_out / 'dry_run_record.json'
    desk = json.loads(record.read_text()).get('desk_status') if record.is_file() else None
    full = ctx.run([ctx.python, '-B', '-m', 'unittest', 'tests.align.test_v4_w1_synthetic'], cwd=ctx.repo,
                   env=env, timeout=1800)
    summary = [line for line in (full.stderr or '').splitlines() if line.startswith(('Ran ', 'OK', 'FAILED'))]
    evidence = {'witness_rc': witness.returncode, 'witness_desk_status': desk,
                'witness_error': tail(witness.stderr, 400), 'full_rc': full.returncode, 'full_summary': summary}
    if witness.returncode or desk != 'ok' or full.returncode:
        return result(FAIL, f'WP22 dry run red: witness rc={witness.returncode} desk={desk}; full module '
                      f'rc={full.returncode} {summary}', **evidence)
    return result(PASS, f'WP22 full dry run green {summary}', **evidence)


@check('smoke-kit', 'the native smoke kit pre-qualified off the MBP: config, the reduced measurement view '
       '(production measurement_view + reduce_view + chain.stage_plan) and every arm-fault expectation against '
       'the production arm with a fake host', gates='w1')
def check_smoke_kit(ctx):
    from joulewise.align import w1_smoke as smoke
    from scripts import align_v4_kit as kit, bytes_h_session as h
    os.environ.setdefault('JOULEWISE_HOST_STATE_DIR', str(ctx.work / 'host-state'))
    Path(os.environ['JOULEWISE_HOST_STATE_DIR']).mkdir(parents=True, exist_ok=True)
    failures, evidence = [], {}
    config = smoke.load_config(ctx.repo)
    # A stand-in production checkout: a clean clone with a synthetic calibration ledger in runs/.
    production = scratch_clone(ctx, 'smoke-kit-production')
    smoke_dir = ctx.work / 'smoke-kit-smoke'
    try:
        from joulewise.b5 import plan as b5_plan
        ledger = production / b5_plan.DEFAULT_LEDGER_RELATIVE
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_text('{"synthetic": "production ledger stand-in"}\n')
        before = hashlib.sha256(ledger.read_bytes()).hexdigest()
        smoke_dir.mkdir(parents=True)
        iso = smoke.isolate(production, smoke_dir, python=ctx.python)
        evidence['isolate'] = {k: iso[k] for k in ('clone', 'source_ledger_sha256', 'smoke_ledger_sha256')}
        clone = Path(iso['clone'])
        session = smoke_dir / 'main'
        session.mkdir(parents=True)
        with contextlib.redirect_stdout(io.StringIO()):
            view, pack = h.measurement_view(clone, session, kit=kit.KIT, pack_id=kit.PACK_ID)
            record = smoke.reduce_view(view, pack, config['keep'])
        evidence['reduction'] = record
        state = {'measurement_root': str(view), 'source_measurement_root': str(clone),
                 'plan_path': str(session / 'custody/night_plan.json'),
                 'inputs': {'custody_root': str(session / 'custody'), 'runs_parent': str(session / 'runs-parent'),
                            'ledger_path': str(view / b5_plan.DEFAULT_LEDGER_RELATIVE), 'pack_root': str(pack)}}
        roots = smoke.production_roots(production, config)
        violations = smoke.isolation_violations(smoke_dir, state, roots, readonly=iso['readonly'])
        evidence['violations'] = violations
        if violations:
            failures.append(f'the isolated smoke resolves inside production roots: {violations[:3]}')
        if os.path.realpath(state['inputs']['ledger_path']) == os.path.realpath(ledger):
            failures.append('the smoke ledger resolves to the production ledger')
        if hashlib.sha256(ledger.read_bytes()).hexdigest() != before:
            failures.append('the production ledger changed during isolation')
        (session / 'probe-link').symlink_to(production / 'runs')
        caught = smoke.isolation_violations(smoke_dir, state, roots, readonly=iso['readonly'])
        (session / 'probe-link').unlink()
        if not any(v['why'] == 'symlink under the smoke directory' for v in caught):
            failures.append('the isolation guard misses a symlink into the production runs/')
        tree = json.loads((pack / 'plan_tree.json').read_bytes())
        for stage in tree['stage_graph']:
            if stage['kind'] != 'campaign_collection':
                continue
            manifest = view / stage['input']['path']
            rows = json.loads(manifest.read_bytes())['executed_order']
            if len(rows) != stage['expected_count'] or h.locator(manifest)['sha256'] != stage['input']['sha256']:
                failures.append(f'{stage["stage_id"]}: manifest/stage mismatch after reduction')
        for fault in ('meter_kill', 'cpu_contender'):
            if not record['kept_runs'].get(config['in_window_faults'][fault]['stage']):
                failures.append(f'the in-window {fault} target stage is not kept')
        if not (pack / 'plan_tree.sha256').read_text().startswith(h.locator(pack / 'plan_tree.json')['sha256']):
            failures.append('plan_tree.sha256 does not pin the reduced tree')
    finally:
        shutil.rmtree(production, ignore_errors=True)
        shutil.rmtree(smoke_dir, ignore_errors=True)
    rows = []
    now = time.time()
    for fault in smoke.ARM_FAULTS:
        if fault.get('setup') == 'receipt_clone':
            rows.append({'fault': fault['id'], 'checked': 'native only (needs a registered receipt)'})
            continue
        base, session, disk = arm_fixture(ctx, 'smoke-' + fault['id'], now=now, t0_offset_s=-600)
        packet = (fault.get('packet') or copy.deepcopy)(valid_packet(ctx, base, now))
        host = FakeHost(extra_mount=fault.get('setup') == 'dmg', now=now)
        out = run_install(ctx, session, disk, packet, host=host, args_override=fault.get('args'),
                          drop=fault.get('drop', ()), now=now, kind=fault.get('battery', 'completed'))
        state = json.loads((session / 'session.json').read_bytes())
        text = out['stderr'].replace('JWSMOKE', config['fault_volume_name'])
        verdict = smoke.judge_arm_fault(fault, out['rc'], text, out['arm'], state)
        rows.append({'fault': fault['id'], 'rc': out['rc'], 'outcome': verdict['outcome']})
        if verdict['outcome'] != 'pass':
            failures.append(f'{fault["id"]}: the smoke expectation does not match the production arm '
                            f'(rc={out["rc"]}, reasons={(out["arm"] or {}).get("reasons")}, {tail(out["stderr"], 200)})')
    evidence['faults'] = rows
    if failures:
        return result(FAIL, '; '.join(failures), **evidence)
    return result(PASS, f'reduced view keeps {record["kept_runs"]} and passes chain.stage_plan; '
                  f'{sum(1 for r in rows if r.get("outcome") == "pass")} arm-fault expectations match the '
                  'production arm (receipt mismatch is native only)', **evidence)


OPTIN_LEDGER = Path('docs/perf/2026-11-08-optin-audit-results.json')
# Opt-in-gated test modules this extension already runs with their opt-in set, by check.
OPTIN_COVERED = {'tests.align.test_v4_w1_synthetic': 'wp22-dry-run (JW_WP22_FULL=1)'}


@check('optin-required', 'WARN only: required tests that run only behind an opt-in (the 2026-11-08 opt-in audit '
       'ledger), with which PREQUAL check or native run covers each; never blocks', gates='w1')
def check_optin_required(ctx):
    path = ctx.repo / OPTIN_LEDGER
    if not path.is_file():
        return result(WARN, f'{OPTIN_LEDGER} absent: opt-in-gated required tests are not enumerated')
    ledger = json.loads(path.read_bytes())
    rows = [r for r in ledger.get('table', []) if 'PREQUAL' in str(r.get('recommendation', ''))]
    present, covered, uncovered = [], {}, {}
    for row in rows:
        module, _, _ = row['id'].rpartition('.')
        module = module.rpartition('.')[0]          # drop the class
        if not (ctx.repo / (module.replace('.', '/') + '.py')).is_file():
            continue
        present.append(row['id'])
        where = OPTIN_COVERED.get(module)
        bucket = covered if where else uncovered
        key = f'{module} -> {where}' if where else f'{module} [{row["recommendation"]}]'
        bucket[key] = bucket.get(key, 0) + 1
    detail = (f'{len(present)} required tests at this candidate run only behind an opt-in '
              f'(ledger {OPTIN_LEDGER.name}); {sum(covered.values())} run by this PREQUAL '
              f'({", ".join(covered) or "none"}); {sum(uncovered.values())} need the native MBP run, base PREQUAL '
              f'or a provisioned fixture: ' + '; '.join(f'{k}: {v}' for k, v in sorted(uncovered.items())[:12]))
    return result(WARN, detail, ledger_baseline=ledger.get('baseline_refs'), covered=covered, uncovered=uncovered,
                  tests=present)


@check('arm-route', 'an arm route exists end to end for the next measurement: declared in arm_routes.json, '
       'every step entry point present and answering, its plan family admitted by run_night', gates='r1')
def check_arm_route(ctx):
    path = ctx.repo / ARM_ROUTES
    if not path.is_file():
        return result(FAIL, f'{ARM_ROUTES} missing: no declared arm route for any measurement')
    routes = json.loads(path.read_bytes())
    route = (routes.get('routes') or {}).get(ctx.next)
    if not isinstance(route, dict) or route.get('status') != 'declared':
        why = (route or {}).get('note') if isinstance(route, dict) else None
        return result(FAIL, f'no arm route declared for {ctx.next}' + (f': {why}' if why else '')
                      + ' (RUN_STATE 218: this is the fault that blocked R1)')
    failures, steps = [], []
    base, pinned = ctx.repo, route.get('commit')
    clone = None
    if pinned and pinned != ctx.commit:
        # A pinned route (the R1 route lives on its own armed commit): verify there, never on the candidate.
        present = ctx.run(['git', '-C', str(ctx.repo), 'cat-file', '-e', f'{pinned}^{{commit}}'], timeout=60)
        if present.returncode:
            return result(FAIL, f'{ctx.next} route is pinned at {pinned} ({route.get("ref")}), which is not in this '
                          f'repository: git fetch origin {pinned}')
        saved = ctx.commit
        ctx.commit = pinned
        try:
            clone = base = scratch_clone(ctx, f'route-{ctx.next}')
        finally:
            ctx.commit = saved
    try:
        failures, steps = _route_steps(ctx, route, base)
    finally:
        if clone is not None:
            shutil.rmtree(clone, ignore_errors=True)
    kind = route.get('receipt_class')
    if kind:
        from joulewise import night_gate
        if getattr(night_gate, kind, None) != kind:
            failures.append(f'run_night does not know receipt class {kind}')
    where = f' (pinned at {pinned[:12]}, {route.get("ref")})' if pinned else ''
    armed = route.get('armed') or {}
    if failures:
        return result(FAIL, '; '.join(failures), steps=steps)
    return result(PASS, f'{ctx.next} route declared{where}; {len(route.get("steps", []))} steps present and '
                  f'answering' + (f'; armed as {armed.get("plan_id")}' if armed else ''), steps=steps, armed=armed)


def _route_steps(ctx, route, base):
    failures, steps = [], []
    for step in route.get('steps', []):
        for rel in step.get('requires', []):
            if not (base / rel).exists():
                failures.append(f'{step["id"]}: missing {rel}')
        probe = step.get('probe')
        if probe:
            argv = [ctx.python if a == '{python}' else str(base / a) if a.startswith(('scripts/', 'joulewise/'))
                    else a for a in probe['argv']]
            out = ctx.run(argv, cwd=base, timeout=120)
            text = (out.stdout or '') + (out.stderr or '')
            missing = [n for n in probe.get('expect_text', []) if n not in text]
            ok = out.returncode in probe.get('expect_rc', [0]) and not missing
            steps.append({'step': step['id'], 'rc': out.returncode, 'missing': missing})
            if not ok:
                failures.append(f'{step["id"]}: rc={out.returncode} missing={missing} {tail(text, 200)}')
    return failures, steps


# ---------------------------------------------------------------------------
# Orchestration


def probe(name, ctx):
    """Run one check in this process; never raises."""
    started = time.monotonic()
    try:
        row = CHECKS[name]['fn'](ctx)
    except Exception as exc:  # noqa: BLE001 - every exception is a FAIL
        row = result(FAIL, f'{type(exc).__name__}: {exc}', traceback=traceback.format_exc()[-2000:])
    row.update(check=name, covers=CHECKS[name]['covers'], seconds=round(time.monotonic() - started, 1))
    return row


def spawn_probe(name, ctx, script, timeout=2400):
    work = ctx.work / name
    argv = [ctx.python, '-B', str(script or PREQUAL_SCRIPT), '--w1-probe', name, '--work', str(work),
            '--w1-next', ctx.next, '--repo', str(ctx.repo), '--commit', ctx.commit, '--python-bin', ctx.python]
    for flag, value in (('--series-projection', ctx.series_projection),
                        ('--deadline-projection', ctx.deadline_projection)):
        if value:
            argv += [flag, str(value)]
    started = time.monotonic()
    env = {**os.environ, 'JOULEWISE_HOST_STATE_DIR': str(work / 'host-state'), 'PYTHONDONTWRITEBYTECODE': '1'}
    try:
        out = ctx.run(argv, cwd=ctx.repo, env=env, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {'check': name, 'status': FAIL, 'detail': f'probe timed out after {timeout} s',
                'covers': CHECKS[name]['covers'], 'seconds': round(time.monotonic() - started, 1), 'evidence': {}}
    for line in reversed((out.stdout or '').splitlines()):
        if line.startswith('{'):
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get('check') == name and row.get('status') in STATUSES:
                return row
    return {'check': name, 'status': FAIL, 'covers': CHECKS[name]['covers'],
            'detail': f'probe produced no result (rc={out.returncode}): {tail(out.stderr, 800)}',
            'seconds': round(time.monotonic() - started, 1), 'evidence': {}}


def run_all(ctx, *, only=None, jobs=4, spawn=None, waivers=None, script=None):
    names = [n for n in CHECKS if not only or n in only]
    spawn = spawn or (lambda name: spawn_probe(name, ctx, script))
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        rows = list(pool.map(spawn, names))
    waivers = waivers or {}
    for row in rows:
        gates = CHECKS[row['check']]['gates']
        row['gates'] = gates
        # A check blocks this arm when it gates this measurement or an earlier one.
        row['blocks'] = NEXT.index(gates) <= NEXT.index(ctx.next)
        if row['status'] == PENDING and row['blocks']:
            row['status'] = FAIL
            row['detail'] = 'PENDING at its own gate: ' + row['detail']
        if row['status'] == FAIL and row['check'] in waivers:
            row['status'] = WAIVED
            row['waiver'] = waivers[row['check']]
    dirty = ctx.run(['git', '-C', str(ctx.repo), 'status', '--porcelain'], timeout=60).stdout.strip()
    blocking_fail = any(r['status'] == FAIL and r['blocks'] for r in rows)
    partial = bool(only) and set(only) != set(CHECKS)
    status = 'FAIL' if blocking_fail else 'INCOMPLETE' if partial else 'PASS'
    return {'schema': SCHEMA, 'status': status, 'next': ctx.next, 'commit': ctx.commit,
            'checkout_dirty': bool(dirty), 'python': ctx.python, 'wall_s': round(time.monotonic() - started, 1),
            'checks': rows, 'waivers': waivers,
            'rule': 'exit 0 only if no blocking check FAILs; FAILs of checks that gate a later measurement are '
                    'reported (early warning) but do not block this arm'}


def table(report):
    lines = [f'W1 PREQUAL ({report["next"]} gate) at {report["commit"][:12]}: {report["status"]} '
             f'(wall {report["wall_s"]} s, dirty={report["checkout_dirty"]})', '',
             '| Check | Status | Gates | Blocks this arm | s | Detail |', '|---|---|---|---|---|---|']
    for row in report['checks']:
        detail = row['detail'].replace('|', '/').replace('\n', ' ')
        lines.append(f'| {row["check"]} | {row["status"]} | {row.get("gates", "")} | '
                     f'{"yes" if row.get("blocks") else "no"} | {row.get("seconds", "")} | {detail[:400]} |')
    return '\n'.join(lines) + '\n'


EXIT = {'PASS': 0, 'FAIL': 1, 'INCOMPLETE': 3}
PREQUAL_SCRIPT = REPO / 'scripts/align_v4_prequal.py'
W1_FLAGS = ('--w1-next', '--w1-probe')


def cli(argv, *, script=PREQUAL_SCRIPT):
    """``scripts/align_v4_prequal.py --w1-next {r1,w1} --output DIR``: the W1/next-arm extension.

    Exit 0 only when no blocking check FAILs; 1 fail, 3 incomplete (--only), 2 usage.
    """
    import argparse
    parser = argparse.ArgumentParser(prog='align_v4_prequal.py --w1-next',
                                     description='ALIGN v4 next-arm PREQUAL extension (docs/align/v4/W1-SMOKE.md)')
    parser.add_argument('--w1-next', dest='next_window', choices=NEXT, help='the next measurement to be armed')
    parser.add_argument('--output', type=Path, help='new report directory (prequal-w1.json, prequal-w1.md)')
    parser.add_argument('--repo', type=Path, default=REPO)
    parser.add_argument('--commit', help='candidate commit (default: repo HEAD)')
    parser.add_argument('--python-bin', default=sys.executable)
    parser.add_argument('--only', help='comma-separated subset (report is then INCOMPLETE at best)')
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--waive', action='append', default=[], metavar='CHECK=RULING',
                        help='record a lead waiver for one FAILing check (ruling reference required)')
    parser.add_argument('--series-projection', help='repo-relative frozen series projection (Sol port)')
    parser.add_argument('--deadline-projection', help='repo-relative installed-plan deadline projection (Sol port)')
    parser.add_argument('--work', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--w1-probe', choices=sorted(CHECKS), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.next_window is None:
        parser.error('--w1-next is required')
    projections = dict(series_projection=args.series_projection, deadline_projection=args.deadline_projection)
    if args.w1_probe:
        os.environ.setdefault('JOULEWISE_HOST_STATE_DIR', str(Path(args.work) / 'host-state'))
        ctx = Context(args.repo, args.work, args.next_window, args.commit, args.python_bin, **projections)
        ctx.work.mkdir(parents=True, exist_ok=True)
        print(json.dumps(probe(args.w1_probe, ctx), sort_keys=True, default=str), flush=True)
        return 0
    if args.output is None:
        parser.error('--output is required')
    if args.output.exists():
        parser.error('--output must be a new directory')
    only = set(args.only.split(',')) if args.only else None
    if only and not only <= set(CHECKS):
        parser.error(f'unknown checks: {sorted(only - set(CHECKS))}')
    waivers = {}
    for item in args.waive:
        name, _, ruling = item.partition('=')
        if name not in CHECKS or not ruling.strip():
            parser.error(f'--waive needs CHECK=RULING with a known check: {item!r}')
        waivers[name] = ruling.strip()
    work = args.work or args.output.with_name(args.output.name + '.work')
    work.mkdir(parents=True, exist_ok=True)
    ctx = Context(args.repo, work, args.next_window, args.commit, args.python_bin, **projections)
    report = run_all(ctx, only=only, jobs=args.jobs, waivers=waivers, script=script)
    report['projections'] = projections
    args.output.mkdir(parents=True)
    (args.output / 'prequal-w1.json').write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + '\n')
    text = table(report)
    (args.output / 'prequal-w1.md').write_text(text)
    print(text)
    return EXIT[report['status']]
