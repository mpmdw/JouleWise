"""ALIGN v4 native W1 smoke (Opus build): a labelled, non-registrable `smoke` window.

Run by the magistrate on the MBP in a gap between windows, never during one, in
at most 45 minutes (``budget_s`` in ``configs/align/v4/w1_smoke.json``). It is
never pooled, analysed or cited as data; its plan id, session id and custody
carry ``align-v4-smoke-``.

Sequence (``SmokeRunner.run``):

1. Gap guards: no night job loaded, no host night lock, no run_night process,
   and an Air PREQUAL report that PASSes at this exact commit.
2. Isolate (lead ruling, HARD): an isolated clone of the measurement commit
   inside the smoke directory, with a COPIED calibration ledger and head pin
   (distinct inodes, ``b6.smoke.copy_ledger``), its own ``runs/``, custody and
   runs roots, and a venv whose interpreter is the base Python. Every path the
   smoke can write is checked against the production roots
   (``isolation_violations``) before any arm; one hit aborts the smoke.
   Prepare: the production ``align_v4_session.prepare`` on that clone, with one
   seam: the session-local measurement view's pack is reduced to the smoke keep
   (``reduce_view``). The kit directory is never edited.
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
import sys
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
    session = view.parent

    def writable(path):
        """A reduction write target: a regular file (or new path) inside this session, never via a link."""
        path = Path(path)
        if path.is_symlink() or not _within(path.parent, session) or (path.exists() and not path.is_file()):
            raise IsolationAbort(f'reduction refuses to write {path}: not a regular file inside {session}')
        if path.exists() and not _within(path, session):
            raise IsolationAbort(f'reduction refuses to write {path}: it resolves outside {session}')
        return path
    tree = json.loads(tree_path.read_bytes())
    before = sha256(tree_path)
    reduced = b6_smoke.reduce_tree(tree, keep)
    kept_runs, repinned = {}, {}
    for stage in reduced['stage_graph']:
        if stage['kind'] != 'campaign_collection':
            continue
        path = writable(view / stage['input']['path'])
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
    writable(tree_path).write_text(json.dumps(reduced, indent=2, sort_keys=True) + '\n')
    writable(pack / 'plan_tree.sha256').write_text(sha256(tree_path) + '  plan_tree.json\n')
    return {'keep': dict(keep), 'stages': [s['stage_id'] for s in reduced['stage_graph']],
            'kept_runs': kept_runs, 'tree_sha256_before': before, 'tree_sha256_after': sha256(tree_path),
            'removed': reduced['smoke_reduction']['removed']}


def materialize_kit(view):
    """Replace the view's symlinked kit directory with a regular copy.

    ``v4_registration._local`` refuses a symlink anywhere in a receipt locator
    (``configs/campaigns/align_v4/registration/...``); the production view links the
    kit, so a receipt check rooted at the view would refuse before reading it (S9).
    """
    import shutil
    kit = Path(view) / 'configs/campaigns/align_v4'
    if kit.is_symlink():
        source = Path(os.path.realpath(kit))
        kit.unlink()
        shutil.copytree(source, kit, symlinks=False)
    return kit


def prepare_smoke(measurement_root, session_root, keep, *, prepare_fn=None, **kwargs):
    """The production v4 prepare with the reduced view; the kit and checkout are untouched.

    The session's ``measurement_root`` becomes the isolated clone itself (a real
    checkout: the production install's kit/receipt check and installer paths resolve
    without symlinks); the reduced view stays the plan's measurement root.
    """
    from unittest import mock
    from scripts import align_v4_session as session, bytes_h_session as h
    original = h.measurement_view
    record = {}

    def view_then_reduce(source, session_dir, **kw):
        view, pack = original(source, session_dir, **kw)
        materialize_kit(view)
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
    if state.get('measurement_root') and Path(measurement_root).is_dir():
        state['view_root'] = state['measurement_root']
        state['measurement_root'] = str(Path(measurement_root).resolve())
        h.write(Path(session_root) / 'session.json', state)
    return state


class IsolationAbort(RuntimeError):
    """A smoke path resolves inside a production root (or outside the smoke): the whole smoke stops."""


class TeardownFailure(RuntimeError):
    """A fault's teardown could not be proven: the host is not back in its start state; the smoke stops."""


_FIRMLINKS = ('/private/var/', '/private/tmp/', '/private/etc/')


def _norm(path):
    """Absolute, normalized, with the macOS /private firmlinks folded (lexical; nothing is opened)."""
    text = os.path.normpath(os.path.abspath(os.path.expanduser(str(path))))
    for prefix in _FIRMLINKS:
        if (text + '/').startswith(prefix):
            text = text[len('/private'):]
            break
    return text


def _forms(path):
    """The lexical and the symlink-resolved form of a path (realpath reads only link metadata)."""
    return {_norm(path), _norm(os.path.realpath(path))}


def _under(text, root):
    return text == root or text.startswith(root.rstrip('/') + '/')


def _within(path, base):
    """Every form of ``path`` lies under a form of ``base``."""
    bases = _forms(base)
    return all(any(_under(form, b) for b in bases) for form in _forms(path))


def production_roots(measurement_root, config):
    """Every root a smoke must never write: the checkout, wherever its runs/ resolves, configured roots.

    Configured roots are taken in both their lexical and their resolved form (an alias
    protects its real directory). Resolution reads link metadata only; no root is
    opened, listed or read.
    """
    m = Path(measurement_root)
    roots = set(_forms(m)) | set(_forms(m / 'runs'))
    for root in config.get('production_roots', ()):
        roots |= _forms(os.path.expanduser(root))
    return sorted(roots)


def _inside(path, roots):
    for form in _forms(path):
        for root in roots:
            if _under(form, _norm(root)):
                return root
    return None


def _absolute_strings(value):
    if isinstance(value, str):
        if value.startswith('/'):
            yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _absolute_strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _absolute_strings(item)


# Keys whose values the smoke (or the window it arms) WRITES. Every such value must be an
# absolute path inside the smoke directory; anything else is a violation.
SMOKE_WRITE_KEYS = ('custody_root', 'runs_parent', 'claim_backup_destination', 'bound_backup_destination',
                    'ledger_path', 'measurement_root', 'pack_root', 'registration_dir', 'plan_path',
                    'session_root', 'source_measurement_root', 'view_root', 'claim_runs_root', 'bound_runs_root',
                    'runs_root', 'output_root', 'chain_path', 'tmpdir', 'TMPDIR', 'runs_roots', 'backups',
                    'disk_volumes')


def _write_values(value, path=''):
    """(locator, value) for every write key anywhere in a nested state/plan document."""
    if isinstance(value, dict):
        for key, item in value.items():
            here = f'{path}.{key}' if path else str(key)
            if key in SMOKE_WRITE_KEYS:
                for leaf in (item if isinstance(item, (list, tuple)) else
                             item.values() if isinstance(item, dict) else [item]):
                    if isinstance(leaf, str):
                        yield here, leaf
            yield from _write_values(item, here)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            yield from _write_values(item, f'{path}[{index}]')


def isolation_violations(smoke_dir, state, roots, *, plan=None, readonly=(), env=None):
    """Every smoke path that escapes (an empty list means isolated).

    * the smoke directory itself inside a production root;
    * any WRITE locator (``SMOKE_WRITE_KEYS``, in the state, its inputs and the plan, at any
      depth) that is relative, or not inside the smoke directory in every form;
    * any other absolute path that resolves inside a production root, except a declared
      read-only path (component-bounded; it never excuses a write locator);
    * ``TMPDIR`` (this process's, or the command environment's) outside the smoke directory;
    * every symlink under the smoke directory that resolves inside a production root.
    """
    found = []
    smoke_dir = Path(smoke_dir)
    hit = _inside(smoke_dir, roots)
    if hit:
        found.append({'path': str(smoke_dir), 'root': hit, 'why': 'smoke directory inside a production root'})
    readonly = [_norm(r) for r in readonly]
    allowed = lambda path: any(_under(form, r) for form in _forms(path) for r in readonly)
    for label, document in (('state', state or {}), ('plan', plan or {})):
        writes = set()
        for locator, value in _write_values(document):
            writes.add(value)
            if not value.startswith('/'):
                found.append({'path': value, 'why': f'{label} write locator {locator} is relative'})
            elif not _within(value, smoke_dir):
                found.append({'path': value, 'resolves_to': os.path.realpath(value), 'root': _inside(value, roots),
                              'why': f'{label} write locator {locator} is outside the smoke directory'})
        for path in sorted(set(_absolute_strings(document)) - writes):
            hit = _inside(path, roots)
            if hit and not allowed(path):
                found.append({'path': path, 'resolves_to': os.path.realpath(path), 'root': hit, 'why': label})
    for name, value in (('process TMPDIR', os.environ.get('TMPDIR')), ('command TMPDIR', (env or {}).get('TMPDIR'))):
        if name == 'process TMPDIR' and value and _inside(value, roots):
            found.append({'path': value, 'root': _inside(value, roots), 'why': f'{name} inside a production root'})
        if name == 'command TMPDIR' and env is not None and (not value or not _within(value, smoke_dir)):
            found.append({'path': value, 'why': f'{name} is not inside the smoke directory'})
    if smoke_dir.is_dir():
        for directory, dirs, files in os.walk(smoke_dir):
            for name in dirs + files:
                path = Path(directory) / name
                if path.is_symlink():
                    hit = _inside(path, roots)
                    if hit:
                        found.append({'path': str(path), 'resolves_to': os.path.realpath(path), 'root': hit,
                                      'why': 'symlink under the smoke directory'})
            dirs[:] = [d for d in dirs if not (Path(directory) / d).is_symlink() and d != '.git']
    unique = {json.dumps(f, sort_keys=True, default=str): f for f in found}
    return list(unique.values())


def destination_violations(smoke_dir, roots):
    """Before ANY write: the smoke directory is new, and neither it nor its nearest existing
    ancestor (in any form) lies inside a production root."""
    smoke_dir = Path(smoke_dir)
    found = []
    if smoke_dir.exists():
        found.append({'path': str(smoke_dir), 'why': 'smoke directory already exists'})
    ancestor = smoke_dir
    while not ancestor.exists() and ancestor != ancestor.parent:
        ancestor = ancestor.parent
    for candidate in (smoke_dir, ancestor):
        hit = _inside(candidate, roots)
        if hit:
            found.append({'path': str(candidate), 'root': hit, 'why': 'smoke destination inside a production root'})
    return found


def isolate(measurement_root, smoke_dir, *, python=None, run=None):
    """The isolated measurement for the smoke: a clone of HEAD inside ``smoke_dir`` with a copied ledger.

    ``git clone --shared`` reads the checkout's objects and writes only the clone. The
    calibration ledger and head pin are copied (``b6.smoke.copy_ledger``: distinct
    inodes, destination inside ``smoke_dir``, source bytes unchanged), and the pin copy
    is committed in the clone so the plan writer's committed-pin check binds the copy.
    ``runs/`` holds only the copied ledger. The venv is created from the checkout's
    interpreter, so it resolves to the base Python, and reads the checkout's
    site-packages through a .pth (read only).
    """
    from joulewise.b5 import plan as b5_plan
    from joulewise.b6 import smoke as b6_smoke
    run = run or (lambda argv, **kw: subprocess.run([str(a) for a in argv], capture_output=True, text=True,
                                                    check=True, timeout=600, **kw))
    m, smoke_dir = Path(measurement_root).resolve(), Path(smoke_dir).resolve()
    clone = smoke_dir / 'measurement'
    head = run(['git', '-C', str(m), 'rev-parse', 'HEAD']).stdout.strip()
    run(['git', 'clone', '--quiet', '--shared', '--no-checkout', str(m), str(clone)])
    git = lambda *a: run(['git', '-C', str(clone), *a])
    git('checkout', '--quiet', '--detach', head)
    git('remote', 'remove', 'origin')
    for key, value in (('user.name', 'W1 Smoke'), ('user.email', 'smoke@invalid'), ('commit.gpgsign', 'false'),
                       ('maintenance.auto', 'false'), ('gc.auto', '0'), ('core.hooksPath', '/dev/null')):
        git('config', '--local', key, value)
    copied = b6_smoke.copy_ledger(m, clone, smoke_dir)
    git('add', b5_plan.HEAD_PIN_RELATIVE)
    git('commit', '--quiet', '--allow-empty', '-m', 'SMOKE ledger pin copy (non-registrable)')
    base_python = python or str(m / '.venv/bin/python')
    run([base_python, '-m', 'venv', '--without-pip', str(clone / '.venv')])
    sites = list((clone / '.venv/lib').glob('python*/site-packages'))
    source_sites = list((m / '.venv/lib').glob('python*/site-packages'))
    if len(sites) != 1:
        raise ValueError('smoke venv site-packages cannot be resolved uniquely')
    if len(source_sites) == 1:
        (sites[0] / 'smoke_measurement_packages.pth').write_text(str(source_sites[0].resolve()) + '\n')
    ledger = clone / b5_plan.DEFAULT_LEDGER_RELATIVE
    source = m / b5_plan.DEFAULT_LEDGER_RELATIVE
    if os.stat(ledger).st_ino == os.stat(source).st_ino:
        raise ValueError('smoke ledger shares the production inode')
    return {'clone': str(clone), 'head': head, 'ledger': str(ledger), 'copied': list(copied),
            'source_ledger_sha256': sha256(source), 'smoke_ledger_sha256': sha256(ledger),
            'readonly': [str(p.resolve()) for p in source_sites]}


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
    # Needles: the packet-as-pointer refusals (the supplied packet differs from, or cannot be, the arm's rebuild).
    {'id': 'triage-edited', 'packet': _edited, 'expect': 'refuse', 'needle': ('does not match its committed sources', 'triage capture_faults failed'),
     'doc': 'a gating packet entry edited to fail'},
    {'id': 'triage-stale', 'packet': _stale, 'expect': 'refuse', 'needle': ('could not be rebuilt', 'does not match its committed sources', 'missing or wrong schema'),
     'doc': 'a pre-R12 packet (no schema, no full_desk_gate)'},
    {'id': 'receipt-digest-mismatch', 'setup': 'receipt_clone', 'expect': 'refuse_before_arm',
     'needle': 'digest drift', 'doc': 'one receipt-bound file differs by one byte in a disposable clone'},
    {'id': 'disk-image-mounted', 'setup': 'dmg', 'expect': 'refuse', 'needle': 'external_volume_mounted:',
     'doc': 'hdiutil attach of a 2 MB read-only disk image'},
    {'id': 'topup-missing', 'battery': 'no-charge', 'expect': 'refuse',
     'needle': 'completed top-up evidence missing',
     'doc': 'a battery log with no completed charge (floating only); v4_topup derives no evidence'},
    {'id': 'topup-omitted', 'drop': ('--battery-log',), 'expect': 'usage',
     'needle': '--battery-log', 'doc': 'the --battery-log flag itself omitted (argparse usage error)'},
)


def _group_alive(pgid):
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def bounded_run(argv, *, timeout=600, env=None, cwd=None):
    """Run in its own process group; on timeout TERM, then KILL the WHOLE group regardless of the
    leader's exit (a TERM-ignoring descendant can outlive it), reap the leader, and report
    whether any member of the group survived."""
    import signal
    process = subprocess.Popen([str(a) for a in argv], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                               start_new_session=True, env=env, cwd=cwd)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        stdout = stderr = ''
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        reaped = False
        try:
            stdout, stderr = process.communicate(timeout=5)
            reaped = True
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(process.pid, signal.SIGKILL)       # unconditionally: descendants share the group
        except ProcessLookupError:
            pass
        if not reaped:
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        survivors = False
        for _ in range(20):
            survivors = _group_alive(process.pid)
            if not survivors:
                break
            time.sleep(0.05)
        note = f'\n[timed out after {timeout} s; process group {process.pid} ' + (
            'SURVIVED SIGKILL' if survivors else 'killed and gone') + ']'
        result = subprocess.CompletedProcess(argv, 124, stdout or '', (stderr or '') + note)
        result.pgid, result.group_survived = process.pid, survivors
        return result
    result = subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)
    result.pgid, result.group_survived = process.pid, False
    return result


_run = bounded_run


class BudgetExpired(RuntimeError):
    """The smoke's single elapsed-time budget is spent: nothing further is armed; owned work is torn down."""


METER_JOURNAL = 'meter_supervision.jsonl'


class SmokeRunner:
    """Executes the smoke; every host action goes through ``run``/``popen``/``sleep``/``clock``.

    Hard limits (not reports): the destination is validated before the first write; every
    isolation hit, failed fault teardown or spent budget stops the smoke before any further
    arm; one deadline clips every command timeout and sleep; whatever this smoke installed
    or started is torn down in ``finally`` and proven gone, or a recoverable record is left.
    """

    def __init__(self, measurement_root, smoke_dir, *, packet, battery_log, obc_off_attested_by,
                 w1_disk_config, prequal_report, python=None, config=None, run=_run, popen=subprocess.Popen,
                 sleep=time.sleep, clock=time.time, prepare=prepare_smoke, isolate_fn=isolate, poll_s=5.0):
        self.m = Path(measurement_root)
        self.dir = Path(smoke_dir)
        self.packet = packet
        self.battery_log, self.obc = Path(battery_log), obc_off_attested_by
        self.disk_config, self.prequal = Path(w1_disk_config), Path(prequal_report)
        self.base_python = python or str(self.m / '.venv/bin/python')
        self.config = config or load_config(self.m)
        self.run_cmd, self.popen, self.sleep_fn, self.clock = run, popen, sleep, clock
        self.prepare_fn, self.isolate_fn, self.poll_s = prepare, isolate_fn, poll_s
        self.roots = production_roots(self.m, self.config)
        self.clone, self.readonly, self.started, self.transcripts = None, (), None, 0
        self.deadline, self.installed, self.contender = None, None, None
        self.env = {**os.environ, 'TMPDIR': str(self.dir / 'tmp')}

    @property
    def python(self):
        """Every smoke command runs from the isolated clone's venv once it exists."""
        return str(self.clone / '.venv/bin/python') if self.clone else self.base_python

    @property
    def code(self):
        return self.clone or self.m

    # -- budget ---------------------------------------------------------------
    def remaining(self):
        return float('inf') if self.deadline is None else self.deadline - self.clock()

    def require_budget(self, need_s, what):
        if self.remaining() < need_s:
            raise BudgetExpired(f'{what}: {self.remaining():.0f} s left of the smoke budget, {need_s:.0f} s needed')

    def sleep(self, seconds):
        self.require_budget(seconds, f'sleep {seconds:.0f} s')
        self.sleep_fn(seconds)

    # -- log -----------------------------------------------------------------
    def log(self, step, outcome, **fields):
        row = {'t': self.clock(), 'elapsed_s': round(self.clock() - (self.started or self.clock()), 1),
               'step': step, 'outcome': outcome, **fields}
        with (self.dir / LOG).open('a') as handle:
            handle.write(json.dumps(row, sort_keys=True, default=str) + '\n')
        return row

    def cmd(self, argv, timeout=600, *, teardown=False, **kw):
        """One bounded command, clipped to the remaining budget (teardown commands excepted); its
        transcript is written create-once (Sol's discipline). A process group that survives its
        timeout is a teardown failure."""
        argv = [str(a) for a in argv]
        if not teardown:
            self.require_budget(1, 'command ' + Path(argv[0]).name)
            timeout = max(1, min(timeout, self.remaining()))
        kw.setdefault('env', self.env)
        started = self.clock()
        out = self.run_cmd(argv, timeout=timeout, **kw)
        self.transcripts += 1
        path = self.dir / 'transcripts' / f'{self.transcripts:04d}-{Path(argv[0]).name}.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {'argv': argv, 'rc': out.returncode, 'stdout': out.stdout or '', 'stderr': out.stderr or '',
                  'started': started, 'ended': self.clock(), 'timeout_s': timeout,
                  'group_survived': getattr(out, 'group_survived', False)}
        with path.open('x') as handle:
            handle.write(json.dumps(record, indent=2, sort_keys=True, default=str) + '\n')
        if getattr(out, 'group_survived', False) is True:
            raise TeardownFailure(f'process group of {argv[0]} survived SIGKILL after its timeout')
        return out.returncode, out.stdout or '', out.stderr or ''

    # -- 1. guards -----------------------------------------------------------
    def guards(self):
        rc, _, err = self.cmd(['launchctl', 'print', f'gui/{os.getuid()}/{NIGHT_LABEL}'], timeout=10)
        job_absent = rc == 113 and 'Could not find service' in err
        rc_p, out_p, _ = self.cmd(['/usr/bin/pgrep', '-f', 'scripts/run_night.py'], timeout=10)
        # S6: a published production plan is installed even when launchd has not loaded it.
        agents = Path.home() / 'Library/LaunchAgents'
        published = [str(agents / f'{name}.plist') for name in (NIGHT_LABEL, NIGHT_LABEL + '.deadman')
                     if (agents / f'{name}.plist').exists()]
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
        ok = job_absent and rc_p == 1 and not published and lock_free and not dirty and prequal_ok
        self.log('guards', 'pass' if ok else 'abort', night_job_absent=job_absent,
                 run_night_processes=out_p.split(), published_night_plists=published, night_lock_free=lock_free,
                 head=head, dirty=bool(dirty),
                 prequal={k: report.get(k) for k in ('status', 'commit', 'next', 'checkout_dirty')})
        return ok, head

    # -- 2. isolate and prepare --------------------------------------------------
    def isolate(self):
        record = self.isolate_fn(self.m, self.dir, python=self.base_python)
        self.clone, self.readonly = Path(record['clone']), tuple(record.get('readonly', ()))
        self.log('isolate', 'pass', production_roots=self.roots, **record)
        self.check_isolation({'source_measurement_root': str(self.clone)}, 'isolate')

    def check_isolation(self, state, step, *, plan=None):
        """Raises IsolationAbort on any violation (a hit is terminal for the whole smoke)."""
        if plan is None and state.get('plan_path') and Path(state['plan_path']).is_file():
            plan = json.loads(Path(state['plan_path']).read_bytes())
        violations = isolation_violations(self.dir, state, self.roots, plan=plan, readonly=self.readonly,
                                          env=self.env)
        self.log('isolation', 'pass' if not violations else 'abort', at=step, violations=violations[:20],
                 production_roots=self.roots)
        if violations:
            raise IsolationAbort(f'isolation violations at {step}: {violations[:3]}')

    def prepare_main(self):
        session = self.dir / 'main'
        state = self.prepare_fn(self.clone, session, self.config['keep'])
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
                  '--obc-off-attested-by': self.obc, '--battery-log': str(self.battery_log),
                  '--next-arm-triage': str(packet_path)}
        values.update(args or {})
        argv = [self.python, '-B', str(self.code / 'scripts/align_v4_session.py'), 'install']
        for key, value in values.items():
            if key not in drop:
                argv += [key, value]
        return argv

    def arm_fault(self, fault, main_session):
        name = fault['id']
        self.require_budget(1, f'fault {name}')
        root = self.dir / 'faults'
        session = fault_session(main_session, name, root, now=self.clock())
        packet = (fault.get('packet') or (lambda p: copy.deepcopy(p)))(self.packet)
        packet_path = session / 'packet.json'
        packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True))
        teardown, setup = [], {}
        rc, out, err = None, '', ''
        try:
            # The fault session's state AND its plan copy, before any setup or command.
            self.check_isolation(json.loads((session / 'session.json').read_bytes()), 'fault ' + name)
            if fault.get('setup') == 'receipt_clone':
                setup = self._receipt_clone(session, root / name / 'clone', teardown)
                self.check_isolation(json.loads((session / 'session.json').read_bytes()), 'fault ' + name)
            elif fault.get('setup') == 'dmg':
                setup = self._attach_dmg(root / name, teardown)
            args = dict(fault.get('args') or {})
            if fault.get('battery'):
                from joulewise.align.w1_prequal import battery_log
                args['--battery-log'] = str(battery_log(root / name / 'battery.jsonl', self.clock(), fault['battery']))
            argv = self.install_argv(session, packet_path=packet_path, args=args, drop=fault.get('drop', ()))
            rc, out, err = self.cmd(argv, timeout=300)
        finally:
            failed = []
            for step in reversed(teardown):
                try:
                    outcome = step()
                except Exception as exc:  # noqa: BLE001 - an unprovable teardown stops the smoke below
                    outcome = {'error': f'{type(exc).__name__}: {exc}', 'ok': False}
                setup.setdefault('teardown', []).append(outcome)
                if outcome.get('ok') is False:
                    failed.append(outcome)
            if failed:
                self.log('arm-fault:' + name, 'fail', error='teardown failed', setup=setup, doc=fault['doc'])
                raise TeardownFailure(f'fault {name} teardown failed: {failed}')
        records = sorted((session / 'staging').glob('v4-arm-*.json'))
        arm = json.loads(records[-1].read_bytes()) if records else None
        state = json.loads((session / 'session.json').read_bytes())
        verdict = judge_arm_fault(fault, rc, out + err, arm, state)
        self.log('arm-fault:' + name, verdict['outcome'], expected=fault['expect'], needle=fault['needle'],
                 rc=rc, stderr=err[-800:], arm_admitted=(arm or {}).get('admitted'),
                 arm_reasons=(arm or {}).get('reasons'), installer_called=verdict['installer_called'],
                 setup=setup, doc=fault['doc'])
        if verdict['installer_called']:
            raise TeardownFailure(f'fault {name} reached the installer')
        return verdict['outcome'] == 'pass'

    def _receipt_clone(self, session, clone, teardown):
        from joulewise.align.apple import v4_registration as reg

        def remove():
            code = self.cmd(['/bin/rm', '-rf', str(clone)], timeout=600, teardown=True)[0]
            return {'rm_clone': code, 'ok': code == 0 and not Path(clone).exists()}
        teardown.append(remove)
        rc, _, err = self.cmd(['git', 'clone', '--quiet', '--shared', str(self.code), str(clone)], timeout=600)
        if rc:
            raise RuntimeError('receipt clone failed: ' + err[-300:])
        head = self.cmd(['git', '-C', str(self.code), 'rev-parse', 'HEAD'], timeout=30)[1].strip()
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

        def detach():
            code = self.cmd(['/usr/bin/hdiutil', 'detach', volume], timeout=120, teardown=True)[0]
            if code:
                code = self.cmd(['/usr/bin/hdiutil', 'detach', '-force', volume], timeout=120, teardown=True)[0]
            mounts = self.cmd(['/sbin/mount'], timeout=30, teardown=True)[1]
            still = volume in mounts
            return {'detach_rc': code, 'still_mounted': still, 'ok': not still}
        teardown.append(detach)
        rc, _, err = self.cmd(['/usr/bin/hdiutil', 'attach', '-nobrowse', '-readonly', '-mountpoint', volume,
                               str(image)], timeout=120)
        if rc:
            raise RuntimeError('hdiutil attach failed: ' + err[-300:])
        return {'volume': volume}

    def arm_main(self, session):
        packet_path = session / 'staging/smoke-next-arm-triage.json'
        packet_path.write_text(json.dumps(self.packet, indent=2, sort_keys=True))
        rc, out, err = self.cmd(self.install_argv(session, packet_path=packet_path), timeout=600)
        state = json.loads((session / 'session.json').read_bytes())
        ok = rc == 0 and (state.get('install') or {}).get('exit_code') == 0
        if (state.get('install') or {}).get('argv'):
            self.installed = state          # owned from here on: torn down in run()'s finally
        self.log('arm-main', 'pass' if ok else 'fail', rc=rc, stdout=out[-800:], stderr=err[-800:],
                 arm_records=state.get('v4_arm_records'), t0_epoch_s=state.get('t0_epoch_s'))
        return ok, state

    # -- 5. in-window faults -------------------------------------------------
    def wait_for(self, predicate, deadline, what):
        deadline = min(deadline, self.deadline) if self.deadline is not None else deadline
        while self.clock() < deadline:
            value = predicate()
            if value:
                return value
            self.sleep_fn(min(self.poll_s, max(0.0, deadline - self.clock())))
        self.log('wait:' + what, 'timeout')
        return None

    def owned_reader_pgid(self, state):
        """The KM003C reader this smoke's window started (the Block driver's meter journal), or None."""
        journal = Path(state['inputs']['custody_root']) / 'night' / METER_JOURNAL
        try:
            lines = [json.loads(line) for line in journal.read_text().splitlines() if line.strip()]
        except (OSError, ValueError):
            return None
        starts = [row for row in lines if row.get('event') == 'start' and type(row.get('pgid')) is int]
        return starts[-1]['pgid'] if starts else None

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
        pgid = self.owned_reader_pgid(state)
        if pgid is None:
            self.log('meter-kill', 'no_reader_identity', run_id=first,
                     detail='no reader start in this window\'s meter journal; nothing killed (never a global kill)')
        else:
            rc, _, _ = self.cmd(['/bin/kill', '-KILL', '--', f'-{pgid}'], timeout=10)
            self.log('meter-kill', 'sent' if rc == 0 else 'no_process', rc=rc, run_id=first, pgid=pgid)
        target = kept[busy['stage']][0]
        bundle = self.wait_for(lambda: find_bundle(state, target), deadline, 'contender-member')
        if bundle is None:
            return False
        self.log('contender-member-started', 'observed', run_id=target, bundle=str(bundle))
        self.sleep(busy['after_bundle_s'])
        self.contender = self.popen(['/usr/bin/yes'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                    start_new_session=True)
        self.log('cpu-contender', 'started', pid=self.contender.pid, duration_s=busy['duration_s'], run_id=target)
        try:
            self.sleep(busy['duration_s'])
        finally:
            self.stop_contender()
        return True

    def stop_contender(self):
        """TERM, then KILL, and always reap: the contender is proven stopped before it is logged stopped."""
        contender, self.contender = self.contender, None
        if contender is None:
            return
        contender.terminate()
        try:
            contender.wait(timeout=10)
        except subprocess.TimeoutExpired:
            contender.kill()
            try:
                contender.wait(timeout=10)
            except subprocess.TimeoutExpired as exc:
                self.log('cpu-contender', 'unreaped', pid=contender.pid)
                raise TeardownFailure(f'contender {contender.pid} did not exit after SIGKILL') from exc
        self.log('cpu-contender', 'stopped', pid=contender.pid)

    # -- 6/7. terminal and finalize --------------------------------------------
    def terminal(self, state, deadline):
        custody = Path(state['inputs']['custody_root'])
        result = self.wait_for(lambda: (custody / 'night/result.json').is_file() and custody / 'night/result.json',
                               deadline, 'terminal-marker')
        gone = bool(result) and self.wait_for(
            lambda: self.cmd(['launchctl', 'print', f'gui/{os.getuid()}/{NIGHT_LABEL}'], timeout=10,
                             teardown=True)[0] == 113, deadline, 'night-job-unloaded')
        self.log('terminal', 'pass' if result and gone else 'fail', result=str(result) if result else None,
                 night_job_unloaded=bool(gone))
        if result and gone:
            self.installed = None           # the window closed itself: nothing left to tear down
        return bool(result and gone)

    def teardown_owned(self):
        """Uninstall ONLY the job this smoke installed (its own plan path), stop its contender, and
        prove both gone; otherwise leave a recoverable record."""
        record = {'plan_path': None, 'steps': []}
        ok = True
        try:
            self.stop_contender()
        except TeardownFailure as exc:
            ok = False
            record['steps'].append({'contender': str(exc)})
        state = self.installed
        if state is not None:
            plan = state.get('plan_path')
            record['plan_path'] = plan
            argv = [str(Path(state['measurement_root']) / 'scripts/install_night_agent.sh'), '--plan', plan,
                    '--uninstall', '--launchctl-bin', 'launchctl']
            for name, command in (('uninstall', argv),):
                try:
                    rc = self.cmd(command, timeout=180, teardown=True)[0]
                except Exception as exc:  # noqa: BLE001
                    rc = f'{type(exc).__name__}: {exc}'
                record['steps'].append({name: rc})
            try:
                loaded = self.cmd(['launchctl', 'print', f'gui/{os.getuid()}/{NIGHT_LABEL}'], timeout=10,
                                  teardown=True)[0] != 113
                running = self.cmd(['/usr/bin/pgrep', '-f', str(plan)], timeout=10, teardown=True)[0] == 0
            except Exception as exc:  # noqa: BLE001
                loaded = running = True
                record['steps'].append({'verify': f'{type(exc).__name__}: {exc}'})
            record.update(job_loaded=loaded, plan_processes_running=running)
            ok = ok and not loaded and not running
            if ok:
                self.installed = None
        self.log('teardown', 'pass' if ok else 'unproven', **record)
        if not ok:
            path = self.dir / 'teardown-unproven.json'
            path.write_text(json.dumps({'schema': SCHEMA + '.teardown_unproven', 'label': NIGHT_LABEL,
                                        **record}, indent=2, sort_keys=True, default=str) + '\n')
        return ok

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
        argv = [self.python, '-B', str(self.code / 'scripts/align_v4_prequal.py'), '--w1-probe', 'r1-w1-chain',
                '--work', str(work), '--w1-next', 'w1', '--repo', str(self.code), '--python-bin', self.python]
        rc, out, err = self.cmd(argv, timeout=900)
        row = next((json.loads(line) for line in reversed(out.splitlines()) if line.startswith('{')), {})
        self.log('r1-w1-chain', 'pass' if row.get('status') == 'PASS' else 'fail', rc=rc,
                 detail=row.get('detail'), stderr=err[-400:])
        return row.get('status') == 'PASS'

    # -- the whole sequence ----------------------------------------------------
    def run(self):
        violations = destination_violations(self.dir, self.roots)
        if violations:                       # refused before ANY write: no directory, no log
            print(json.dumps({'smoke': 'refused', 'reason': 'destination', 'violations': violations},
                             default=str), file=sys.stderr)
            return 2
        self.dir.mkdir(parents=True)
        (self.dir / 'tmp').mkdir()
        self.started = self.clock()
        budget = self.config['budget_s']
        self.deadline = self.started + budget
        self.log('start', 'info', measurement_root=str(self.m), budget_s=budget, label='smoke',
                 registrable=False, config_sha256=sha256(self.m / CONFIG) if (self.m / CONFIG).is_file() else None)
        code = 0
        try:
            code = self._sequence()
        except IsolationAbort as exc:
            self.log('end-reason', 'abort', reason='isolation', error=str(exc))
            code = 2
        except TeardownFailure as exc:
            self.log('end-reason', 'abort', reason='teardown', error=str(exc))
            code = 1
        except BudgetExpired as exc:
            self.log('end-reason', 'abort', reason='budget', error=str(exc))
            code = 1
        finally:
            if self.installed is not None or self.contender is not None:
                if not self.teardown_owned():
                    code = code or 1
            self.log('end', 'done' if code == 0 else 'abort', code=code,
                     wall_s=round(self.clock() - self.started, 1))
        return code

    def _sequence(self):
        ok, _head = self.guards()
        if not ok:
            return 2
        self.isolate()
        ok, session, state = self.prepare_main()
        if not ok:
            return 1
        self.check_isolation(state, 'prepare')
        for fault in ARM_FAULTS:
            try:
                self.arm_fault(fault, session)
            except (IsolationAbort, TeardownFailure, BudgetExpired):
                raise
            except Exception as exc:  # noqa: BLE001 - a fault that cannot be staged is a FAIL row
                self.log('arm-fault:' + fault['id'], 'fail', error=f'{type(exc).__name__}: {exc}')
        t0 = state.get('t0_epoch_s')
        if not isinstance(t0, (int, float)) or self.clock() > t0 - self.config['min_lead_at_arm_s']:
            # The fault attempts outlasted the prepared lead: stage a fresh session (same reduction).
            self.dir.joinpath('main').rename(self.dir / 'main.superseded')
            self.log('prepare-again', 'info', reason='t0 too close after the fault attempts', t0_epoch_s=t0)
            ok, session, state = self.prepare_main()
            if not ok:
                return 1
            self.check_isolation(state, 'prepare-again')
        # The window itself must fit in what is left of the budget.
        self.require_budget(self.config['arm_reserve_s'], 'arm the smoke window')
        self.check_isolation(json.loads((session / 'session.json').read_bytes()), 'arm-main')
        ok, state = self.arm_main(session)
        if ok:
            self.in_window_faults(state, self.deadline)
            if self.terminal(state, self.deadline):
                self.finalize(state)
        if self.remaining() > 60:
            self.chain()
        else:
            self.log('r1-w1-chain', 'fail', detail='skipped: no smoke budget left')
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
    needles = fault['needle'] if isinstance(fault['needle'], (tuple, list)) else (fault['needle'],)
    found = lambda haystack: any(n in haystack for n in needles)
    if expect == 'admit':
        ok = rc != 0 and bool(arm and arm.get('admitted')) and found(text) and not installed
    elif expect == 'refuse':
        ok = (rc != 0 and arm is not None and arm.get('admitted') is False and not installed
              and found(json.dumps(arm.get('reasons') or []) + text))
    elif expect == 'refuse_before_arm':
        ok = rc != 0 and arm is None and not installed and found(text)
    elif expect == 'usage':
        ok = rc == 2 and arm is None and not installed and found(text)
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
    isolation = by.get('isolation') or [{}]
    isolated = (by.get('isolate') or [{}])[-1]
    add('isolated-clone', isolated.get('outcome') == 'pass' and bool(by.get('isolation'))
        and all(r.get('outcome') == 'pass' for r in isolation),
        f'clone={isolated.get("clone")} ledger copied={isolated.get("smoke_ledger_sha256") is not None}; '
        f'violations={[v for r in isolation for v in (r.get("violations") or [])][:3]}')
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
        source = Path(state.get('source_measurement_root') or REPO)
        config = load_config(source if (source / CONFIG).is_file() else REPO)
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
