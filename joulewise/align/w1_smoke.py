"""ALIGN v4 native W1 smoke (Opus build): a labelled, non-registrable `smoke` window.

Run by the magistrate on the MBP in a gap between windows, never during one, in
at most 45 minutes (``budget_s`` in ``configs/align/v4/w1_smoke.json``). It is
never pooled, analysed or cited as data; its plan id, session id and custody
carry ``align-v4-smoke-``.

Sequence (``SmokeRunner.run``):

1. Gap guards: no night job loaded, no host night lock, no run_night process,
   and an Air PREQUAL report that PASSes at this exact commit.
2. Prepare: the production ``align_v4_session.prepare`` (kit W1-ready check,
   models present, disk snapshot, identities, plan writer) with one seam: the
   session-local measurement view's pack is reduced to the smoke keep
   (``reduce_view``). The kit directory and the measurement checkout are never
   edited.
3. Arm fault injections, each its own production arm attempt
   (``align_v4_session.py install``) on a session copy whose plan copy has t0
   in the past, so the installer is unreachable even if an arm admits; each
   expects the documented refusal and is torn down.
4. The real arm: the production install of the reduced plan (launchd night job,
   run_night, HAZARD_PACK driver, KM003C reader, chain).
5. In-window faults on the W1 member: a short out-of-tree CPU contender during
   its request, then the KM003C reader SIGKILLed mid-member.
6. Terminal: night/result.json, hazard_result.json, the launchd job gone (B1).
7. Finalize: a sha256 inventory of the smoke custody (never pushed).
8. The R1 -> W1 chain dry run natively (the PREQUAL probe, in the MBP venv).

``parse`` turns the log and custody into a PASS/FAIL table. Every host command
goes through an injectable runner; tests drive the whole sequence with fakes.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

REPO = Path(__file__).resolve().parents[2]
CONFIG = Path('configs/align/v4/w1_smoke.json')
SCHEMA = 'joulewise.align_v4.w1_smoke.v1'
LOG = 'smoke-log.jsonl'
LABEL_PREFIX = 'align-v4-smoke-'
NIGHT_LABEL = 'com.joulewise.night'


def load_config(root=REPO):
    config = json.loads((Path(root) / CONFIG).read_bytes())
    if config.get('schema') != SCHEMA or config.get('label') != 'smoke' or config.get('registrable') is not False:
        raise ValueError('w1_smoke.json must be the labelled, non-registrable smoke config')
    return config


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# The one prepare seam: reduce the session-local view's pack


def reduce_view(view, pack, keep):
    """Reduce ``pack/plan_tree.json`` (a session-local copy) to ``keep`` members per stage.

    Uses the B6 smoke reducer (``joulewise.b6.smoke.reduce_tree``, which runs
    ``chain.stage_plan``), truncates each kept stage's pack-local order manifest
    to its first N members, re-pins the stage input and the external manifest
    descriptors, and rewrites the tree's sha256 file. Returns the record.
    """
    from joulewise.b6 import smoke as b6_smoke
    view, pack = Path(view), Path(pack)
    tree_path = pack / 'plan_tree.json'
    tree = json.loads(tree_path.read_bytes())
    before = sha256(tree_path)
    reduced = b6_smoke.reduce_tree(tree, keep)
    kept_runs, repinned = {}, {}
    for stage in reduced['stage_graph']:
        if stage['kind'] != 'campaign_collection':
            continue
        path = view / stage['input']['path']
        manifest = json.loads(path.read_bytes())
        n = keep[stage['stage_id']]
        manifest['executed_order'] = manifest['executed_order'][:n]
        if 'planned_n_bundles' in manifest:
            manifest['planned_n_bundles'] = n
        path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
        digest = sha256(path)
        repinned[stage['input']['path']] = digest
        stage['input']['sha256'] = digest
        kept_runs[stage['stage_id']] = [row['run_id'] for row in manifest['executed_order']]
    manifests = []
    for entry in (reduced.get('external_inputs') or {}).get('manifests', []):
        path = entry['manifest']['path']
        if path not in repinned:
            continue
        runs = {r for rows in kept_runs.values() for r in rows}
        entry = copy.deepcopy(entry)
        entry['manifest']['sha256'] = repinned[path]
        entry['members'] = [m for m in entry['members'] if m['run_id'] in runs]
        entry['expected_count'] = len(entry['members'])
        if entry['members']:
            manifests.append(entry)
    reduced.setdefault('external_inputs', {})['manifests'] = manifests
    reduced['smoke_label'] = {'label': 'smoke', 'registrable': False, 'pooled': False, 'analysed': False}
    from joulewise.b5 import chain
    chain.stage_plan(reduced)
    tree_path.write_text(json.dumps(reduced, indent=2, sort_keys=True) + '\n')
    (pack / 'plan_tree.sha256').write_text(sha256(tree_path) + '  plan_tree.json\n')
    return {'keep': dict(keep), 'stages': [s['stage_id'] for s in reduced['stage_graph']],
            'kept_runs': kept_runs, 'tree_sha256_before': before, 'tree_sha256_after': sha256(tree_path),
            'removed': reduced['smoke_reduction']['removed']}


def prepare_smoke(measurement_root, session_root, keep, *, prepare_fn=None, **kwargs):
    """The production v4 prepare with the reduced view; the kit and checkout are untouched."""
    from unittest import mock
    from scripts import align_v4_session as session, bytes_h_session as h
    original = h.measurement_view
    record = {}

    def view_then_reduce(source, session_dir, **kw):
        view, pack = original(source, session_dir, **kw)
        record.update(reduce_view(view, pack, keep))
        h.write(Path(session_dir) / 'staging/smoke-reduction.json', record)
        return view, pack
    kwargs.setdefault('session_prefix', LABEL_PREFIX)
    with mock.patch.object(h, 'measurement_view', view_then_reduce):
        state = (prepare_fn or session.prepare)(measurement_root, session_root, **kwargs)
    if not record:
        raise ValueError('smoke prepare did not reach the measurement view; nothing was reduced')
    state = dict(state)
    state['smoke_reduction'] = record
    return state


def fault_session(main_session, name, root, *, now):
    """A disposable arm session: the main session's state, a fresh custody and a past-t0 plan copy.

    h.install refuses a passed t0 after the arm, so no fault attempt can install
    the night job, even one whose arm unexpectedly admits.
    """
    from scripts import bytes_h_session as h
    main = Path(main_session)
    state = json.loads((main / 'session.json').read_bytes())
    for key in ('install', 'install_attempts', 'v4_arm_records'):
        state.pop(key, None)
    base = Path(root) / name
    session, custody = base / 'session', base / 'custody'
    (session / 'staging').mkdir(parents=True)
    custody.mkdir(parents=True)
    plan = json.loads(Path(state['plan_path']).read_bytes())
    plan['t0_epoch_s'] = int(now) - 600
    plan_path = custody / 'night_plan.past-t0.json'
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + '\n')
    state['plan_path'] = str(plan_path)
    state['plan_sha256'] = h.locator(plan_path)['sha256']
    state.setdefault('inputs', {})['custody_root'] = str(custody)
    state['smoke_fault'] = name
    h.write(session / 'session.json', state)
    return session


# ---------------------------------------------------------------------------
# Arm fault catalogue: each expects the documented refusal before any install


def _edited(packet):
    packet = copy.deepcopy(packet)
    packet['checks']['capture_faults'] = {'status': 'fail', 'basis': 'smoke: edited packet'}
    return packet


def _stale(packet):
    packet = copy.deepcopy(packet)
    packet.pop('schema', None)
    packet['checks'].pop('full_desk_gate', None)
    return packet


ARM_FAULTS = (
    {'id': 'arm-control', 'expect': 'admit', 'needle': 'plan t0 has passed',
     'doc': 'no fault: the arm admits, the W1 disk gate passes, the installer guard refuses the past t0'},
    {'id': 'triage-edited', 'packet': _edited, 'expect': 'refuse', 'needle': 'triage capture_faults failed',
     'doc': 'a gating packet entry edited to fail'},
    {'id': 'triage-stale', 'packet': _stale, 'expect': 'refuse', 'needle': 'missing or wrong schema',
     'doc': 'a pre-R12 packet (no schema, no full_desk_gate)'},
    {'id': 'receipt-digest-mismatch', 'setup': 'receipt_clone', 'expect': 'refuse_before_arm',
     'needle': 'digest drift', 'doc': 'one receipt-bound file differs by one byte in a disposable clone'},
    {'id': 'disk-image-mounted', 'setup': 'dmg', 'expect': 'refuse', 'needle': 'external_volume_mounted:',
     'doc': 'hdiutil attach of a 2 MB read-only disk image'},
    {'id': 'topup-missing', 'args': {'--topup-completed-at': 'missing'}, 'expect': 'refuse',
     'needle': 'completed top-up evidence missing', 'doc': 'no completed top-up time'},
    {'id': 'topup-omitted', 'drop': ('--topup-completed-at',), 'expect': 'usage',
     'needle': '--topup-completed-at', 'doc': 'the flag itself omitted (argparse usage error)'},
)


def _run(argv, *, timeout=600, env=None, cwd=None):
    return subprocess.run([str(a) for a in argv], capture_output=True, text=True, check=False,
                          timeout=timeout, env=env, cwd=cwd)


class SmokeRunner:
    """Executes the smoke; every host action goes through ``run``/``popen``/``sleep``/``clock``."""

    def __init__(self, measurement_root, smoke_dir, *, packet, topup_completed_at, topup_source,
                 obc_off_attested_by, w1_disk_config, prequal_report, python=None, config=None,
                 run=_run, popen=subprocess.Popen, sleep=time.sleep, clock=time.time,
                 prepare=prepare_smoke, poll_s=5.0):
        self.m = Path(measurement_root)
        self.dir = Path(smoke_dir)
        self.packet = packet
        self.topup_at, self.topup_source, self.obc = topup_completed_at, topup_source, obc_off_attested_by
        self.disk_config, self.prequal = Path(w1_disk_config), Path(prequal_report)
        self.python = python or str(self.m / '.venv/bin/python')
        self.config = config or load_config(self.m)
        self.run_cmd, self.popen, self.sleep, self.clock = run, popen, sleep, clock
        self.prepare_fn, self.poll_s = prepare, poll_s
        self.started = None

    # -- log -----------------------------------------------------------------
    def log(self, step, outcome, **fields):
        row = {'t': self.clock(), 'elapsed_s': round(self.clock() - (self.started or self.clock()), 1),
               'step': step, 'outcome': outcome, **fields}
        with (self.dir / LOG).open('a') as handle:
            handle.write(json.dumps(row, sort_keys=True, default=str) + '\n')
        return row

    def cmd(self, argv, timeout=600, **kw):
        out = self.run_cmd(argv, timeout=timeout, **kw)
        return out.returncode, out.stdout or '', out.stderr or ''

    # -- 1. guards -----------------------------------------------------------
    def guards(self):
        rc, _, err = self.cmd(['launchctl', 'print', f'gui/{os.getuid()}/{NIGHT_LABEL}'], timeout=10)
        job_absent = rc == 113 and 'Could not find service' in err
        rc_p, out_p, _ = self.cmd(['/usr/bin/pgrep', '-f', 'scripts/run_night.py'], timeout=10)
        from joulewise.align.apple import powermode
        lock = Path(powermode.night_lock_path())
        lock_free = True
        if lock.exists():
            held = powermode.HostLock(role='w1-smoke-probe')
            lock_free = bool(held.acquire())
            if lock_free:
                held.release()
        head = self.cmd(['git', '-C', str(self.m), 'rev-parse', 'HEAD'], timeout=30)[1].strip()
        dirty = self.cmd(['git', '-C', str(self.m), 'status', '--porcelain'], timeout=60)[1].strip()
        try:
            report = json.loads(self.prequal.read_bytes())
        except (OSError, ValueError):
            report = {}
        prequal_ok = (report.get('status') == 'PASS' and report.get('commit') == head
                      and report.get('next') == 'w1' and report.get('checkout_dirty') is False)
        ok = job_absent and rc_p == 1 and lock_free and not dirty and prequal_ok
        self.log('guards', 'pass' if ok else 'abort', night_job_absent=job_absent,
                 run_night_processes=out_p.split(), night_lock_free=lock_free, head=head, dirty=bool(dirty),
                 prequal={k: report.get(k) for k in ('status', 'commit', 'next', 'checkout_dirty')})
        return ok, head

    # -- 2. prepare ----------------------------------------------------------
    def prepare_main(self):
        session = self.dir / 'main'
        state = self.prepare_fn(self.m, session, self.config['keep'])
        plan_id = json.loads(Path(state['plan_path']).read_bytes()).get('plan_id') if state.get('plan_path') else None
        labelled = str(state.get('session_id', '')).startswith(LABEL_PREFIX)
        ok = state.get('preparation_status') == 'STAGED' and labelled
        self.log('prepare', 'pass' if ok else 'fail', session_id=state.get('session_id'), plan_id=plan_id,
                 plan_path=state.get('plan_path'), reduction=state.get('smoke_reduction'),
                 t0_epoch_s=state.get('t0_epoch_s'), window_max_s=state.get('window_max_s'))
        return ok, session, state

    # -- 3 and 4. arm attempts --------------------------------------------------
    def install_argv(self, session, *, packet_path, args=None, drop=()):
        values = {'--session-root': str(session), '--w1-disk-config': str(self.disk_config),
                  '--obc-off-attested-by': self.obc, '--topup-completed-at': str(self.topup_at),
                  '--topup-source': self.topup_source, '--next-arm-triage': str(packet_path)}
        values.update(args or {})
        argv = [self.python, '-B', str(self.m / 'scripts/align_v4_session.py'), 'install']
        for key, value in values.items():
            if key not in drop:
                argv += [key, value]
        return argv

    def arm_fault(self, fault, main_session):
        name = fault['id']
        root = self.dir / 'faults'
        session = fault_session(main_session, name, root, now=self.clock())
        packet = (fault.get('packet') or (lambda p: copy.deepcopy(p)))(self.packet)
        packet_path = session / 'packet.json'
        packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True))
        teardown = []
        setup = {}
        try:
            if fault.get('setup') == 'receipt_clone':
                setup = self._receipt_clone(session, root / name / 'clone', teardown)
            elif fault.get('setup') == 'dmg':
                setup = self._attach_dmg(root / name, teardown)
            argv = self.install_argv(session, packet_path=packet_path, args=fault.get('args'),
                                     drop=fault.get('drop', ()))
            rc, out, err = self.cmd(argv, timeout=300)
        finally:
            for step in reversed(teardown):
                setup.setdefault('teardown', []).append(step())
        records = sorted((session / 'staging').glob('v4-arm-*.json'))
        arm = json.loads(records[-1].read_bytes()) if records else None
        state = json.loads((session / 'session.json').read_bytes())
        verdict = judge_arm_fault(fault, rc, out + err, arm, state)
        self.log('arm-fault:' + name, verdict['outcome'], expected=fault['expect'], needle=fault['needle'],
                 rc=rc, stderr=err[-800:], arm_admitted=(arm or {}).get('admitted'),
                 arm_reasons=(arm or {}).get('reasons'), installer_called=verdict['installer_called'],
                 setup=setup, doc=fault['doc'])
        return verdict['outcome'] == 'pass'

    def _receipt_clone(self, session, clone, teardown):
        from joulewise.align.apple import v4_registration as reg
        rc, _, err = self.cmd(['git', 'clone', '--quiet', '--shared', str(self.m), str(clone)], timeout=600)
        teardown.append(lambda: {'rm_clone': self.cmd(['/bin/rm', '-rf', str(clone)], timeout=600)[0]})
        if rc:
            raise RuntimeError('receipt clone failed: ' + err[-300:])
        head = self.cmd(['git', '-C', str(self.m), 'rev-parse', 'HEAD'], timeout=30)[1].strip()
        self.cmd(['git', '-C', str(clone), 'checkout', '--quiet', '--detach', head], timeout=600)
        victim = next((p for p in reg.ARTIFACTS if p.endswith('.md') and (clone / p).is_file()), None)
        if victim is None:
            raise RuntimeError('no receipt-bound markdown artifact in the clone to perturb')
        with (clone / victim).open('ab') as handle:
            handle.write(b'\n')
        state = json.loads((session / 'session.json').read_bytes())
        state['measurement_root'] = str(clone)
        (session / 'session.json').write_text(json.dumps(state, indent=2, sort_keys=True) + '\n')
        return {'clone': str(clone), 'edited': victim}

    def _attach_dmg(self, base, teardown):
        image = base / 'jwsmoke.dmg'
        volume = '/Volumes/' + self.config['fault_volume_name']
        rc, _, err = self.cmd(['/usr/bin/hdiutil', 'create', '-size', '2m', '-fs', 'HFS+', '-volname',
                               self.config['fault_volume_name'], '-ov', str(image)], timeout=120)
        if rc:
            raise RuntimeError('hdiutil create failed: ' + err[-300:])
        rc, _, err = self.cmd(['/usr/bin/hdiutil', 'attach', '-nobrowse', '-readonly', '-mountpoint', volume,
                               str(image)], timeout=120)

        def detach():
            code = self.cmd(['/usr/bin/hdiutil', 'detach', volume], timeout=120)[0]
            if code:
                code = self.cmd(['/usr/bin/hdiutil', 'detach', '-force', volume], timeout=120)[0]
            mounts = self.cmd(['/sbin/mount'], timeout=30)[1]
            return {'detach_rc': code, 'still_mounted': volume in mounts}
        teardown.append(detach)
        if rc:
            raise RuntimeError('hdiutil attach failed: ' + err[-300:])
        return {'volume': volume}

    def arm_main(self, session):
        packet_path = session / 'staging/smoke-next-arm-triage.json'
        packet_path.write_text(json.dumps(self.packet, indent=2, sort_keys=True))
        rc, out, err = self.cmd(self.install_argv(session, packet_path=packet_path), timeout=600)
        state = json.loads((session / 'session.json').read_bytes())
        ok = rc == 0 and (state.get('install') or {}).get('exit_code') == 0
        self.log('arm-main', 'pass' if ok else 'fail', rc=rc, stdout=out[-800:], stderr=err[-800:],
                 arm_records=state.get('v4_arm_records'), t0_epoch_s=state.get('t0_epoch_s'))
        return ok, state

    # -- 5. in-window faults -------------------------------------------------
    def wait_for(self, predicate, deadline, what):
        while self.clock() < deadline:
            value = predicate()
            if value:
                return value
            self.sleep(self.poll_s)
        self.log('wait:' + what, 'timeout')
        return None

    def in_window_faults(self, state, deadline):
        spec = self.config['in_window_faults']
        kept = state['smoke_reduction']['kept_runs']
        kill, busy = spec['meter_kill'], spec['cpu_contender']
        first = kept[kill['stage']][0]
        bundle = self.wait_for(lambda: find_bundle(state, first), deadline, 'meter-kill-member')
        if bundle is None:
            return False
        self.log('meter-kill-member-started', 'observed', run_id=first, bundle=str(bundle))
        self.sleep(kill['after_bundle_s'])
        rc, _, _ = self.cmd(['/usr/bin/pkill', '-KILL', '-f', 'scripts/km003c_monitor.py'], timeout=10)
        self.log('meter-kill', 'sent' if rc == 0 else 'no_process', rc=rc, run_id=first)
        target = kept[busy['stage']][0]
        bundle = self.wait_for(lambda: find_bundle(state, target), deadline, 'contender-member')
        if bundle is None:
            return False
        self.log('contender-member-started', 'observed', run_id=target, bundle=str(bundle))
        self.sleep(busy['after_bundle_s'])
        contender = self.popen(['/usr/bin/yes'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               start_new_session=True)
        self.log('cpu-contender', 'started', pid=contender.pid, duration_s=busy['duration_s'], run_id=target)
        try:
            self.sleep(busy['duration_s'])
        finally:
            contender.terminate()
            try:
                contender.wait(timeout=10)
            except subprocess.TimeoutExpired:
                contender.kill()
        self.log('cpu-contender', 'stopped', pid=contender.pid)
        return True

    # -- 6/7. terminal and finalize --------------------------------------------
    def terminal(self, state, deadline):
        custody = Path(state['inputs']['custody_root'])
        result = self.wait_for(lambda: (custody / 'night/result.json').is_file() and custody / 'night/result.json',
                               deadline, 'terminal-marker')
        gone = self.wait_for(lambda: self.cmd(['launchctl', 'print', f'gui/{os.getuid()}/{NIGHT_LABEL}'],
                                              timeout=10)[0] == 113, deadline + 300, 'night-job-unloaded')
        self.log('terminal', 'pass' if result and gone else 'fail', result=str(result) if result else None,
                 night_job_unloaded=bool(gone))
        return bool(result and gone)

    def finalize(self, state):
        custody = Path(state['inputs']['custody_root'])
        rows = []
        for path in sorted(p for p in custody.rglob('*') if p.is_file() and not p.is_symlink()):
            rows.append({'path': path.relative_to(custody).as_posix(), 'sha256': sha256(path),
                         'bytes': path.stat().st_size})
        record = {'schema': SCHEMA + '.finalize', 'label': 'smoke', 'registrable': False,
                  'custody_root': str(custody), 'files': rows,
                  'inventory_sha256': hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()}
        (self.dir / 'finalize.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
        self.log('finalize', 'pass' if rows else 'fail', files=len(rows), inventory_sha256=record['inventory_sha256'])
        return bool(rows)

    # -- 8. R1 -> W1 chain ---------------------------------------------------
    def chain(self):
        work = self.dir / 'chain'
        argv = [self.python, '-B', str(self.m / 'scripts/align_v4_w1_prequal.py'), '--probe', 'r1-w1-chain',
                '--work', str(work), '--next', 'w1', '--repo', str(self.m), '--python-bin', self.python]
        rc, out, err = self.cmd(argv, timeout=900)
        row = next((json.loads(line) for line in reversed(out.splitlines()) if line.startswith('{')), {})
        self.log('r1-w1-chain', 'pass' if row.get('status') == 'PASS' else 'fail', rc=rc,
                 detail=row.get('detail'), stderr=err[-400:])
        return row.get('status') == 'PASS'

    # -- the whole sequence ----------------------------------------------------
    def run(self):
        self.dir.mkdir(parents=True, exist_ok=False)
        self.started = self.clock()
        budget = self.config['budget_s']
        deadline = self.started + budget
        self.log('start', 'info', measurement_root=str(self.m), budget_s=budget, label='smoke',
                 registrable=False, config_sha256=sha256(self.m / CONFIG))
        ok, _head = self.guards()
        if not ok:
            self.log('end', 'abort', reason='gap guards')
            return 2
        try:
            ok, session, state = self.prepare_main()
        except Exception as exc:  # noqa: BLE001 - a prepare refusal ends the smoke, recorded
            self.log('prepare', 'fail', error=f'{type(exc).__name__}: {exc}')
            self.log('end', 'fail', reason='prepare')
            return 1
        if not ok:
            self.log('end', 'fail', reason='prepare')
            return 1
        for fault in ARM_FAULTS:
            try:
                self.arm_fault(fault, session)
            except Exception as exc:  # noqa: BLE001 - a fault that cannot be staged is a FAIL row
                self.log('arm-fault:' + fault['id'], 'fail', error=f'{type(exc).__name__}: {exc}')
        t0 = state.get('t0_epoch_s')
        if not isinstance(t0, (int, float)) or self.clock() > t0 - self.config['min_lead_at_arm_s']:
            # The fault attempts outlasted the prepared lead: stage a fresh session (same reduction).
            self.dir.joinpath('main').rename(self.dir / 'main.superseded')
            self.log('prepare-again', 'info', reason='t0 too close after the fault attempts', t0_epoch_s=t0)
            try:
                ok, session, state = self.prepare_main()
            except Exception as exc:  # noqa: BLE001
                self.log('prepare', 'fail', error=f'{type(exc).__name__}: {exc}')
                ok = False
            if not ok:
                self.log('end', 'fail', reason='prepare-again', wall_s=round(self.clock() - self.started, 1))
                return 1
        ok, state = self.arm_main(session)
        if ok:
            self.in_window_faults(state, deadline)
            if self.terminal(state, deadline):
                self.finalize(state)
        self.chain()
        self.log('end', 'done', wall_s=round(self.clock() - self.started, 1))
        return 0


def find_bundle(state, run_id):
    """The member's bundle directory under the session's runs roots, or None."""
    roots = [Path(p) for p in (state.get('runs_roots') or {}).values() if isinstance(p, str)]
    parent = (state.get('inputs') or {}).get('runs_parent')
    if parent:
        roots.append(Path(parent))
    for root in roots:
        if (root / run_id).is_dir():
            return root / run_id
        if root.is_dir():
            for hit in sorted(root.glob(f'*/{run_id}')):
                if hit.is_dir():
                    return hit
    return None


def judge_arm_fault(fault, rc, text, arm, state):
    installed = bool((state.get('install') or {}).get('argv'))
    expect = fault['expect']
    needle = fault['needle']
    if expect == 'admit':
        ok = rc != 0 and bool(arm and arm.get('admitted')) and needle in text and not installed
    elif expect == 'refuse':
        ok = (rc != 0 and arm is not None and arm.get('admitted') is False and not installed
              and needle in json.dumps(arm.get('reasons') or []) + text)
    elif expect == 'refuse_before_arm':
        ok = rc != 0 and arm is None and not installed and needle in text
    elif expect == 'usage':
        ok = rc == 2 and arm is None and not installed and needle in text
    else:
        ok = False
    return {'outcome': 'pass' if ok else 'fail', 'installer_called': installed}


# ---------------------------------------------------------------------------
# Parser: log + custody -> PASS/FAIL table


def _rows(log_path):
    rows = []
    for line in Path(log_path).read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def member_dc_and_contention(state, killed, others):
    """KM003C DC status and contention findings for the kept members, via the production readers."""
    from joulewise.align.apple import km003c
    from joulewise.b5.harvest import member_spans
    from joulewise.hazards import monitor
    from joulewise.desk_compress import read_bytes
    custody = Path(state['inputs']['custody_root'])
    runs, plan = {}, []
    for run_id in (killed, *others):
        bundle = find_bundle(state, run_id)
        if bundle is not None:
            runs[run_id] = bundle
            plan.append({'run_id': run_id, 'condition': 'benign', 'task_pair': 'smoke', 'model_id': 'smoke'})
    out = {}
    if not runs:
        return out
    roots = {b.parent for b in runs.values()}
    summaries = [{'run_id': r, 'excluded': True, 'summary': {}} for r in runs]
    reports = {}
    for root in roots:
        rows = [p for p in plan if runs[p['run_id']].parent == root]
        reports.update(km003c.session_report(custody, rows, root, summaries)['members'])
    journals = monitor.load_journals(custody)
    for run_id, bundle in runs.items():
        metadata = json.loads(read_bytes(bundle / 'metadata.json'))
        events = [json.loads(line) for line in read_bytes(bundle / 'events.jsonl').splitlines() if line.strip()]
        spans = member_spans(metadata, events)
        found = []
        if spans.get('member') and spans.get('request'):
            found = monitor.member_findings(journals, span={'monotonic_ns': spans['member']},
                                            request={'monotonic_ns': spans['request']})
        dc = reports.get(run_id, {})
        out[run_id] = {'dc_status': dc.get('status'), 'dc_flags': dc.get('flags'),
                       'findings': sorted({f.get('code') for f in found})}
    return out


def parse(smoke_dir, *, member_reader=member_dc_and_contention):
    smoke_dir = Path(smoke_dir)
    rows = _rows(smoke_dir / LOG)
    by = {}
    for row in rows:
        by.setdefault(row['step'], []).append(row)
    table = []

    def add(check, ok, detail):
        table.append({'check': check, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})
    start = (by.get('start') or [{}])[0]
    end = (by.get('end') or [{}])[-1]
    budget = start.get('budget_s', 2700)
    add('labelled-non-registrable', start.get('label') == 'smoke' and start.get('registrable') is False,
        f'label={start.get("label")} registrable={start.get("registrable")}')
    guards = (by.get('guards') or [{}])[-1]
    add('gap-guards', guards.get('outcome') == 'pass', json.dumps({k: guards.get(k) for k in (
        'night_job_absent', 'run_night_processes', 'night_lock_free', 'dirty', 'prequal')}, default=str))
    prepare = (by.get('prepare') or [{}])[-1]
    add('prepare-reduced', prepare.get('outcome') == 'pass' and str(prepare.get('session_id', '')).startswith(LABEL_PREFIX),
        f'session {prepare.get("session_id")}; kept {(prepare.get("reduction") or {}).get("kept_runs")}'
        + (f'; error {prepare.get("error")}' if prepare.get('error') else ''))
    for fault in ARM_FAULTS:
        row = (by.get('arm-fault:' + fault['id']) or [{}])[-1]
        detail = (f'expected {fault["expect"]} ({fault["needle"]!r}); rc={row.get("rc")} '
                  f'admitted={row.get("arm_admitted")} installer_called={row.get("installer_called")}')
        teardown = (row.get('setup') or {}).get('teardown') or []
        if any(t.get('still_mounted') for t in teardown if isinstance(t, dict)):
            detail += '; DISK IMAGE STILL MOUNTED'
        if row.get('error'):
            detail += f'; error {row["error"]}'
        add('arm-fault:' + fault['id'], row.get('outcome') == 'pass'
            and not any(isinstance(t, dict) and t.get('still_mounted') for t in teardown), detail)
    main = (by.get('arm-main') or [{}])[-1]
    add('arm-main', main.get('outcome') == 'pass', f'rc={main.get("rc")} {str(main.get("stderr", ""))[-200:]}')
    terminal = (by.get('terminal') or [{}])[-1]
    add('terminal-marker', terminal.get('outcome') == 'pass',
        f'result={terminal.get("result")} night_job_unloaded={terminal.get("night_job_unloaded")}')
    finalize = (by.get('finalize') or [{}])[-1]
    add('finalize', finalize.get('outcome') == 'pass', f'files={finalize.get("files")}')
    contender = [r for r in by.get('cpu-contender', []) if r['outcome'] in ('started', 'stopped')]
    kill = (by.get('meter-kill') or [{}])[-1]
    state_path = smoke_dir / 'main/session.json'
    members = {}
    if state_path.is_file() and main.get('outcome') == 'pass':
        state = json.loads(state_path.read_bytes())
        reduction = json.loads((smoke_dir / 'main/staging/smoke-reduction.json').read_bytes())
        config = load_config(Path(state.get('source_measurement_root', REPO)))
        spec = config['in_window_faults']
        killed = reduction['kept_runs'][spec['meter_kill']['stage']][0]
        target = reduction['kept_runs'][spec['cpu_contender']['stage']][0]
        try:
            members = member_reader(state, killed, [target])
        except Exception as exc:  # noqa: BLE001 - unreadable custody is a FAIL row
            members = {'error': f'{type(exc).__name__}: {exc}'}
        custody = Path(state['inputs']['custody_root'])
        hazard = custody / 'night/hazard_result.json'
        meter = json.loads(hazard.read_bytes()).get('meter', {}) if hazard.is_file() else {}
        streams_ok = bool(meter.get('streams')) and all(
            (custody / s['path']).is_file() and s.get('sha256') == sha256(custody / s['path'])
            for s in meter.get('streams', []))
        add('km003c-reader', streams_ok and (meter.get('stop') or {}).get('proven_stopped') is True
            and meter.get('restarts', 0) >= 1,
            f'starts={meter.get("starts")} restarts={meter.get("restarts")} streams={len(meter.get("streams", []))} '
            f'stopped={(meter.get("stop") or {}).get("proven_stopped")} hashes_ok={streams_ok}')
        k = members.get(killed, {}) if isinstance(members, dict) else {}
        t = members.get(target, {}) if isinstance(members, dict) else {}
        add('meter-kill-flags-member', kill.get('outcome') == 'sent' and k.get('dc_status') == 'missing'
            and any(str(f).startswith('meter.') for f in k.get('dc_flags') or ()),
            f'{killed}: DC {k.get("dc_status")} {k.get("dc_flags")}')
        add('cpu-contender-flagged', len(contender) == 2 and 'contention.request_overlap' in (t.get('findings') or ()),
            f'{target}: findings {t.get("findings")}')
        add('w1-member-dc-available', t.get('dc_status') == 'available',
            f'{target}: DC {t.get("dc_status")} {t.get("dc_flags")}')
    else:
        for name in ('km003c-reader', 'meter-kill-flags-member', 'cpu-contender-flagged', 'w1-member-dc-available'):
            add(name, False, 'main window did not arm')
    chain = (by.get('r1-w1-chain') or [{}])[-1]
    add('r1-w1-chain-native', chain.get('outcome') == 'pass', str(chain.get('detail'))[:300])
    wall = end.get('wall_s')
    add('wall-time', isinstance(wall, (int, float)) and wall <= budget, f'{wall} s (budget {budget} s)')
    status = 'PASS' if all(r['status'] == 'PASS' for r in table) else 'FAIL'
    return {'schema': SCHEMA + '.report', 'status': status, 'smoke_dir': str(smoke_dir), 'wall_s': wall,
            'checks': table, 'members': members}


def render(report):
    lines = [f'W1 SMOKE {report["status"]} (wall {report["wall_s"]} s) {report["smoke_dir"]}', '',
             '| Check | Status | Detail |', '|---|---|---|']
    for row in report['checks']:
        lines.append(f'| {row["check"]} | {row["status"]} | {row["detail"].replace("|", "/")[:300]} |')
    return '\n'.join(lines) + '\n'


def detach(argv, log_path):
    """Re-run ``argv`` in a new session (not a descendant the agent census can see once the agent exits)."""
    handle = open(log_path, 'a')
    process = subprocess.Popen(argv, stdout=handle, stderr=handle, stdin=subprocess.DEVNULL,
                               start_new_session=True, close_fds=True)
    return process.pid


__all__ = ['ARM_FAULTS', 'SmokeRunner', 'detach', 'fault_session', 'find_bundle', 'judge_arm_fault', 'load_config',
           'parse', 'prepare_smoke', 'reduce_view', 'render']
