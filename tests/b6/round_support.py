"""Tiny real-shaped windows; only launchd, hardware probes and mail are fakes."""
from __future__ import annotations

import base64
import contextlib
import io
import json
import os
from pathlib import Path
import plistlib
import shutil
import signal
import subprocess
import sys
import time
from types import SimpleNamespace
from unittest import mock

from joulewise import calibration_ledger as ledger
from joulewise.b5 import chain, plan
from joulewise.b6 import compose, smoke
from joulewise.b6.driver_lane import read, write
from joulewise.b6.lanes import Waker, resolve
from joulewise.b6.loop import Loop
from joulewise.b6.mailer import Mailer
from joulewise.b6.pack_registration import Registration
from tests import test_harvest_b5_window as windows
from tests.b6.support import ROOT, PACKS, fake_environment, tree
from tests.git_fixture import init_git_fixture
from tests.test_b6_loop import Transport

PYTHON = '/opt/homebrew/bin/python3.13'


class Clock:
    def __init__(self):
        self.value = time.time()
    def __call__(self):
        return self.value


class Round:
    def __init__(self, root, *, refuse=False, lost=False):
        assert os.environ.get('JW_B5_SYNTHETIC_ONLY') == '1'
        self.root, self.clock = root, Clock()
        self.window = windows.Window(root / 'seed')
        self.measurement = self.window.measurement
        # Real program files, including the installer and all its imports, run
        # only from this disposable checkout. No source checkout is modified.
        for directory in ('configs', 'joulewise', 'scripts'):
            shutil.copytree(ROOT / directory, self.measurement / directory, dirs_exist_ok=True)
        runbook = chain.RUNBOOK_RELATIVE
        target = self.measurement / runbook
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / runbook, target)
        target = self.measurement / 'tests/fixtures/night_plan_v1_retired.json'
        target.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / 'tests/fixtures/night_plan_v1_retired.json', target)
        self.campaign = PACKS['alpha']
        target_pack = self.measurement / 'configs/campaigns' / self.campaign
        shutil.rmtree(target_pack)
        shutil.copytree(self.window.pack, target_pack)
        for path in target_pack.rglob('*.json'):
            path.write_text(path.read_text().replace(windows.PACK_ID, self.campaign))
        miniature = self.make_tree(target_pack)
        write(target_pack / 'plan_tree.json', miniature)
        self.window.ledger.write_bytes(b'')
        write(self.window.pin, {'sequence': 0, 'head_digest': ledger.GENESIS_DIGEST, 'ledger_schema': ledger.LEDGER_SCHEMA})
        # Each fixture keeps acceptance absent, exercising the actual pending
        # registration export. Neither a corpus threshold nor a count is lowered.
        (self.measurement / 'configs/b6/registration/acceptance.json').unlink(missing_ok=True)
        bin_dir = self.measurement / '.venv/bin'
        bin_dir.mkdir(parents=True)
        (bin_dir / 'python').symlink_to(PYTHON)
        (self.measurement / '.venv/lib/python3.13/site-packages').mkdir(parents=True)
        (self.measurement / '.gitignore').write_text('.venv/\nruns/\n')
        init_git_fixture(self.measurement)
        for args in (('config', 'user.name', 'B6 Desk'), ('config', 'user.email', 'desk@invalid'),
                     ('config', 'commit.gpgsign', 'false'), ('add', '.'), ('commit', '-qm', 'synthetic measurement')):
            subprocess.run(['git', '-C', str(self.measurement), *args], check=True, capture_output=True)
        self.home = root / 'home'
        self.home.mkdir()
        self.jobs = root / 'jobs'
        self.jobs.mkdir()
        self.control = root / 'instrument.json'
        write(self.control, {'refuse': refuse, 'lost': lost, 'events': []})
        self.launchctl = root / 'bin/launchctl'
        self.launchctl.parent.mkdir()
        self.launchctl.write_text(f'#!{PYTHON}\n' + FAKE_LAUNCHCTL.replace('__ROOT__', repr(str(ROOT))))
        self.launchctl.chmod(0o755)
        self.env = {**os.environ, 'HOME': str(self.home), 'JW_B6_DESK_JOBS': str(self.jobs),
                    'JW_B6_DESK_CONTROL': str(self.control), 'JW_B5_SYNTHETIC_ONLY': '1',
                    'JW_B6_BUNDLE_TEMPLATE': str(windows.template()),
                    'PYTHONDONTWRITEBYTECODE': '1'}
        self.calls = []
        self.loop_root = root / 'loop'
        config = read(self.measurement / 'configs/b6/loop.json')
        config['wake_argv'] = []
        regs = {}
        for p in ('alpha', 'beta', 'gamma'):
            value = read(self.measurement / f'configs/b6/packs/{p}/registration.json')
            # The fixed-pack queue uses only its own tree; beta's NEXT is a
            # rotation assertion and never starts another measured session.
            value['status'] = 'registered'
            regs[p] = Registration(value, commit_time=0)
        lanes = resolve(self.measurement, self.loop_root, run=self.run, config=config, clock=self.clock)
        lanes.driver.launchctl_bin = str(self.launchctl)
        lanes.driver.env = self.env
        lanes.desk.env = self.env
        def fresh_context(out):
            ctx, seams, _ = fake_environment(self.measurement)
            lanes.precheck.seams = seams
            return ctx
        lanes.precheck.context_factory = fresh_context
        self.lanes = lanes
        transport = Transport()
        mailer = Mailer(self.loop_root, lanes.precheck_catalog if hasattr(lanes, 'precheck_catalog') else
                        __import__('joulewise.flags.catalog', fromlist=['load_catalog']).load_catalog(
                            self.measurement / config['flag_catalog']), clock=self.clock, transport=transport)
        self.loop = Loop(self.measurement, self.loop_root, config=config, regs=regs, clock=self.clock,
            run=self.run, lanes=lanes, mailer=mailer, waker=Waker(self.loop_root))

    def make_tree(self, pack):
        tiny = smoke.reduce_tree(tree('alpha'), compose.registered_smoke_keep(self.campaign))
        old = read(pack / 'plan_tree.json')
        # Keep the real chain's reservation, captures, verdict, backup and all
        # launch bindings. Six strict bundles cover references and both science
        # halves; smoke keeps four. The registered estimator minimum remains 5.
        tiny.update(plan=old['plan'], window_identity=old['window_identity'],
                    science=old['science'], external_inputs={'manifests': [], 'artifacts': []},
                    downstream_contract=old['downstream_contract'])
        tiny['arm_attachments']['identity_pin_projection'] = old['arm_attachments']['identity_pin_projection']
        ids = [row[0] for row in windows.MEMBERS]
        groups = [[ids[0]], ids[2:4], ids[4:6], [ids[1]]]
        by_id = {m['run_id']: m for m in old['science']}
        for i, (stage, group) in enumerate(zip((s for s in tiny['stage_graph'] if s['kind'] == 'campaign_collection'), groups)):
            directory = pack / f'round-{i}'
            directory.mkdir()
            rows = []
            for ordinal, run_id in enumerate(group, 1):
                config = next(pack.rglob(run_id + '.json'))
                shutil.copyfile(config, directory / config.name)
                rows.append({'ordinal': ordinal, 'run_id': run_id, 'config': config.name,
                             'config_sha256': windows.sha(config)})
                by_id[run_id]['stage_id'] = stage['stage_id']
                by_id[run_id]['config_path'] = (directory / config.name).relative_to(self.measurement).as_posix()
            manifest = {'manifest_id': f'round-{i}', 'executed_order': rows}
            write(directory / 'order_manifest.json', manifest)
            relative = directory.relative_to(self.measurement).as_posix()
            stage['expected_count'] = len(group)
            stage['input'] = {'path': relative + '/order_manifest.json', 'manifest_id': f'round-{i}',
                              'sha256': windows.sha(directory / 'order_manifest.json')}
            stage['launch']['commands'][0]['argv_template']['arguments'][0]['value'] = relative
        return tiny

    def run(self, argv, **kwargs):
        argv = list(map(str, argv))
        self.calls.append(argv)
        if 'ls-remote' in argv:
            return SimpleNamespace(returncode=0, stdout='', stderr='')
        if '-c' in argv and 'base64' in argv[argv.index('-c') + 1]:
            epoch = dict(zip(ledger.IDENTITY_EPOCH_FIELDS, ('25F84', 'Mac15,9', 'ac_high_power', 100,
                                                          'estimator-v1', 'pulse-v3')))
            from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
            t1 = {**{key: 'value-' + key for key in V2_BINDING_FIELDS}, **epoch}
            return SimpleNamespace(returncode=0, stdout=json.dumps({name: base64.b64encode(
                json.dumps(value).encode()).decode() for name, value in
                (('identity-epoch.json', epoch), ('t1-bindings.json', t1))}), stderr='')
        if argv[0].endswith('install_night_agent.sh'):
            assert '--launchctl-bin' in argv and argv[argv.index('--launchctl-bin') + 1] == str(self.launchctl)
            assert '--courier-bin' in argv
            return self.install(argv)
        if argv[0] == str(self.launchctl) and argv[1] == 'print' and read(self.control).get('lost'):
            # Lose a job only after install has completed, at the loop's first
            # poll. The installer's own liveness checks still see the job.
            (self.jobs / 'com.joulewise.night').unlink(missing_ok=True)
        if any(arg.endswith('/scripts/harvest_b6_session.py') for arg in argv):
            # Use the real CLI's worker pool for the six strict bundles. Every
            # assessment still runs; no validator or reduction is substituted.
            argv.extend(['--workers', '2'])
        # Exhaustive allowlist: an absolute host-tool path cannot bypass a
        # basename denylist, and new subprocesses must earn a fixture seam.
        allowed = (argv[0] == str(self.launchctl) or Path(argv[0]).name == 'git' or
                   (Path(argv[0]).name.startswith('python') and
                    (argv[1:4] == ['-m', 'venv', '--without-pip'] or
                     any(arg.endswith('/scripts/harvest_b6_session.py') for arg in argv))))
        if not allowed:
            raise AssertionError('unexpected round subprocess: ' + str(argv))
        kwargs['env'] = self.env
        return subprocess.run(argv, **kwargs)

    def install(self, argv):
        from joulewise import night_agent_install as installer
        from tests import battery_float_fixture
        from joulewise.night_gate import NightPlan
        real_run = subprocess.run
        def subprocess_at_seam(args, **kwargs):
            args = list(map(str, args))
            if any(arg.endswith('/scripts/run_night.py') for arg in args):
                # The installer's preflight only imports the driver and parses
                # NightPlan. Do that in process: never execute run_night.py.
                assert 'preflight' in args
                from scripts import run_night
                NightPlan.from_mapping(read(args[args.index('--plan') + 1]))
                return subprocess.CompletedProcess(args, 0)
            allowed = (args[0] == str(self.launchctl) or Path(args[0]).name == 'git' or
                       (args[1:3] == ['-B', '-c'] and
                        args[3].startswith('import hashlib,json,sys; from pathlib import Path; ') and
                        "'path':sys.executable" in args[3]))
            if not allowed:
                raise AssertionError('unexpected installer subprocess: ' + str(args))
            return real_run(args, **kwargs)
        out, err = io.StringIO(), io.StringIO()
        saved = {number: signal.getsignal(number) for number in installer.SIGNALS}
        try:
            with mock.patch.dict(os.environ, self.env), \
                 mock.patch.object(installer, '__file__', str(self.measurement / 'joulewise/night_agent_install.py')), \
                 mock.patch.object(installer, 'BATTERY_PROBE_RUNNER', battery_float_fixture.runner()), \
                 mock.patch.object(installer.time, 'time', self.clock), \
                 mock.patch.object(subprocess, 'run', side_effect=subprocess_at_seam), \
                 contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = installer.main(argv[1:])
        finally:
            for number, handler in saved.items():
                signal.signal(number, handler)
        return subprocess.CompletedProcess(argv, rc, out.getvalue(), err.getvalue())

    def state(self):
        return self.loop.read_state()

    def until(self, state, limit=40):
        for _ in range(limit):
            if self.state()['state'] == state:
                return self.state()
            if self.state()['state'] == 'ARM_WAIT':
                self.clock.value += 1801
            elif self.state()['state'] == 'WAIT_PHYSICS':
                self.clock.value += 301
            self.loop.tick()
            if self.state()['state'] == 'HOLD_LOOP' and state != 'HOLD_LOOP':
                raise AssertionError(str(self.state().get('last_exception') or self.state().get('hold_reason')) + '\n' +
                    str([row['line'] for row in self.state()['attempts']]) + '\n' +
                    '\n'.join(path.read_text() for path in self.loop_root.rglob('install.stderr')))
        raise AssertionError(f'did not reach {state}: {self.state()["state"]} {self.state().get("wait")}\n' +
            '\n'.join(str({key: read(path).get(key) for key in ('status', 'flags', 'errors')})
                      for path in self.loop_root.rglob('smoke-result.json')))


FAKE_LAUNCHCTL = '''import json, os, sys
from pathlib import Path
argv = sys.argv[1:]
jobs, control = Path(os.environ['JW_B6_DESK_JOBS']), Path(os.environ['JW_B6_DESK_CONTROL'])
verb, target = argv[0], argv[-1]
label = Path(target).stem if verb == 'bootstrap' else target.rsplit('/', 1)[-1]
marker = jobs / label
if verb == 'print':
    if marker.exists():
        print('state = waiting')
        raise SystemExit(0)
    print(f'Could not find service "{label}" in domain for user gui: {os.getuid()}', file=sys.stderr)
    raise SystemExit(113)
state = json.loads(control.read_text())
state['events'].append([verb, label])
control.write_text(json.dumps(state))
if verb == 'bootout':
    marker.unlink(missing_ok=True)
elif verb == 'bootstrap':
    marker.write_text(target)
    if label == 'com.joulewise.night':
        import plistlib
        sys.path.insert(0, __ROOT__)
        from tests.b6.round_support import synthesize
        args = plistlib.loads(Path(target).read_bytes())['ProgramArguments']
        synthesize(Path(args[args.index('--plan') + 1]), state)
        control.write_text(json.dumps(state))
else:
    raise AssertionError(argv)
'''


def synthesize(plan_path, state):
    p = read(plan_path)
    custody = Path(p['custody_root'])
    night = custody / 'night'
    b = p['hazard_window']['bindings']
    if state.get('refuse'):
        state['refuse'] = False
        write(night / 'result.json', {'verdict': 'REFUSED', 'chain_exit_code': None,
                                    'aborted_reason': 'night_refused_hazard'})
        write(night / 'hazard_result.json', {'arm': {'go': False, 'verdicts': {'battery': {'status': 'REFUSE'}}}})
        return
    measurement = Path(p['measurement_root'])
    pack = Path(p['hazard_window']['pack']['pack_root'])
    t = read(pack / 'plan_tree.json')
    write(night / 'chain.started', {'epoch_s': 1786206000, 'pgid': 999999, 'monotonic_ns': windows.CHAIN_STARTED_NS})
    claim = Path(b['claim_runs_root'])
    dispatches = plan.resolve_stage_dispatches(t, measurement)
    for dispatch in dispatches[:2] if state.get('lost') else dispatches:
        for run_id in dispatch.run_ids[:next(s['expected_count'] for s in t['stage_graph'] if s['stage_id'] == dispatch.stage_id)]:
            windows.copy_member(Path(os.environ['JW_B6_BUNDLE_TEMPLATE']) / run_id, claim / run_id)
    # Real ledger appends and finalization, retaining the builder's capture
    # shapes, so pin advance must make a real pin-only Git commit.
    epoch = read(Path(b['identity_epoch_json']))
    t1 = read(Path(b['t1_bindings_json']))
    slots = {}
    for slot in ('pre', 'post'):
        capture = Path(b[slot + '_calibration_dir'])
        slots[slot] = {'attempt_id': b[slot + '_attempt_id'], 'custody_locator': str(capture),
                       'identity_epoch': epoch, 't1_bindings': t1}
        if state.get('lost') and slot == 'post':
            continue
        (capture / 'raw').mkdir(parents=True)
        (capture / 'raw/powermetrics.plist').write_bytes(f'raw-{slot}'.encode())
        (capture / 'events.jsonl').write_text('{"timestamp_s":99.0}\n')
        anchor = read(Path(os.environ['JW_B6_BUNDLE_TEMPLATE']) / windows.MEMBERS[0][0] / 'metadata.json')[
            'uncertainty_evidence']['clock_anchor']
        write(capture / 'instrument_evidence.json', {'slot': slot, 'clock_anchor': anchor})
        write(capture / 'manifest.json', {'slot': slot})
    ledger_path = measurement / plan.DEFAULT_LEDGER_RELATIVE
    ledger.append_bracket_session_receipt(ledger_path, session_id=b['bracket_session_id'],
        window_id=t['window_identity']['window_id'], plan_id=t['plan']['plan_id'],
        plan_sha256=windows.sha(pack / t['plan']['path']), evidence_root_id=t['window_identity']['evidence_root_id'],
        runs_root=claim, slots=slots, head_pin_path=measurement / plan.HEAD_PIN_RELATIVE, require_committed_pin=True,
        repo_root=measurement)
    for slot in ('pre',) if state.get('lost') else ('pre', 'post'):
        capture = Path(slots[slot]['custody_locator'])
        ledger.finalize_bracket_session_slot(ledger_path, session_id=b['bracket_session_id'], slot=slot,
            disposition='valid', custody_locator=str(capture), artifact_sha256=ledger.artifact_hashes(capture),
            identity_epoch=epoch, t1_bindings=t1, capture_wall_time_s='99.0', exact_bound_lexeme_s='0.025')
    rows = [{'stage_id': s.stage_id, 'kind': s.kind, 'rc': 0, 'started_epoch_s': 1786206000,
             'ended_epoch_s': 1786206001} for s in chain.stage_plan(t) if s.in_chain]
    if state.get('lost'):
        cutoff = next(i for i, row in enumerate(rows) if row['stage_id'] == dispatches[1].stage_id)
        rows = rows[:cutoff + 1]
    (night / chain.STAGE_JOURNAL).write_text(''.join(json.dumps(row) + '\n' for row in rows))
    windows.write_journals(custody / 'hazards/monitor')
    # An eligible raw file ensures compression really writes and verifies zstd.
    (custody / 'raw-transcript.txt').write_bytes(b'synthetic transcript\n' * 60000)
    write(night / 'executed_inventory.json', {'measurement_checkout': {'head': p['measurement_head'],
        'status_porcelain': '', 'root': str(measurement), 'files': {}}, 'pack_root': str(pack)})
    if state.get('lost'):
        return
    write(night / 'chain.exited', {'epoch_s': 1786216000, 'exit_code': 0})
    write(night / 'result.json', {'verdict': 'GO', 'aborted_reason': None, 'chain_exit_code': 0, 'artifacts': []})
