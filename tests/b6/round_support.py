"""Tiny real-shaped windows; only launchd, hardware probes and mail are fakes."""
from __future__ import annotations

import base64
import contextlib
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import plistlib
import re
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


def reference_template():
    """A strict primary-byte reference with an admitted request and calibration."""
    from tests.test_reduce import D078R01RegressionTests
    from joulewise.reduce import reduce_bundle
    root = windows.template()
    target = root / 'reference-calibrated/bundle'
    if target.exists():
        return target
    source = root / 'reference-source'
    windows.copy_member(root / windows.MEMBERS[0][0], source)
    # Give the synthetic reference a clear request signal on both energy
    # families, rather than the seed's nearly zero idle-subtracted request.
    raw_path = source / 'raw/powermetrics.plist'
    # Preserve native timestamp lexemes: plistlib's serializer truncates the
    # fractional datetime fields on this retained synthetic seed.
    documents = []
    for raw in raw_path.read_bytes().split(b'\0'):
        if not raw.strip():
            continue
        record = plistlib.loads(raw)
        raw = re.sub(rb'(<key>gpu_power</key>\s*<(?:real|integer)>)([-+0-9.eE]+)(</(?:real|integer)>)',
            lambda match: match[1] + str(int(float(match[2]) + 10000) if b'<integer>' in match[1]
                                        else float(match[2]) + 10000).encode() + match[3], raw)
        energy = record['processor']['gpu_energy'] + 10000 * record['elapsed_ns'] / 1e9
        raw = re.sub(rb'<key>gpu_energy</key>\s*<(?:real|integer)>[-+0-9.eE]+</(?:real|integer)>',
                     b'<key>gpu_energy</key><real>' + str(energy).encode() + b'</real>', raw)
        documents.append(raw)
    raw_path.write_bytes(b'\0'.join(documents))
    trace = source / 'power_trace.csv'
    with trace.open() as stream:
        reader = csv.DictReader(stream)
        fields, samples = reader.fieldnames, list(reader)
    for sample in samples:
        if sample['rail'] == 'gpu_power':
            sample['power_w'] = str(float(sample['power_w']) + 10)
    with trace.open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(samples)
    md = read(source / 'metadata.json')
    md['campaign_environment_preflight']['snapshot']['python_packages'] = {'mlx': {'version': '0.31.2'}}
    anchor = md['uncertainty_evidence']['clock_anchor']
    for key in ('epoch_s', 'monotonic_before_s', 'monotonic_after_s'):
        anchor['clock_stamps']['sampling_stopped'][key] += 1
    stamps = {name: windows.stamp_from_mapping(value) for name, value in anchor['clock_stamps'].items()}
    expected, _ = windows.resolve_clock_evidence_deriver(anchor['method'])(stamps=stamps,
        records=windows.anchor_records_from_powermetrics(windows.parse_powermetrics_records((source / 'raw/powermetrics.plist').read_bytes())))
    if expected['sample_phase']['status'] != 'bounded':
        raise AssertionError(expected)
    md['uncertainty_evidence'].update(clock_anchor=expected['clock_anchor'], sample_phase=expected['sample_phase'])
    for key in ('marker_to_first_sample_phase_bound_s', 'marker_to_last_sample_phase_bound_s'):
        md[key] = expected['sample_phase'][key]
    from joulewise.adapters.powermetrics import rich_telemetry_jsonl
    (source / 'rich_telemetry.jsonl').write_text(rich_telemetry_jsonl(raw_path.read_bytes(),
        first_record_endpoint_s=expected['clock_anchor']['first_sample_end_point_epoch_s']))
    write(source / 'metadata.json', md)
    events = [json.loads(line) for line in (source / 'events.jsonl').read_text().splitlines()]
    for event in events:
        if event['event_type'] == 'sampling_stopped' or (event['event_type'] == 'phase_end' and event['phase'] == 'decode'):
            event['timestamp_s'] += 1
    (source / 'events.jsonl').write_text(''.join(json.dumps(event) + '\n' for event in events))
    builder = D078R01RegressionTests()
    evidence = builder._valid_instrument_evidence(first_endpoint_s=1786206200.05,
        anchor_method=md['uncertainty_evidence']['clock_anchor']['method'],
        bindings={'os_build': md['device']['kern_osversion'], 'sampling_interval_ms': 50.0})
    bundle = builder._bundle_with_calibration(root / 'reference-calibrated', evidence=evidence, measurement_fixture=source)
    write(bundle / 'summary_metrics.json', reduce_bundle(bundle).to_dict())
    from joulewise.cli import validate_bundle
    from joulewise.whole_window import _reference_energy_evidence
    problems = validate_bundle(bundle, strict=True)
    if problems or _reference_energy_evidence(bundle)[2] is not None:
        raise AssertionError(problems or 'synthetic reference energy not admitted')
    return bundle


class Clock:
    def __init__(self):
        self.value = time.time()
    def __call__(self):
        return self.value


class Round:
    def __init__(self, root, *, refuse=False, lost=False, full_pack=None):
        assert os.environ.get('JW_B5_SYNTHETIC_ONLY') == '1'
        self.root, self.clock = root, Clock()
        self.full_pack = full_pack
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
        self.campaign = PACKS[full_pack or 'alpha']
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
        write(self.control, {'refuse': refuse, 'lost': lost, 'events': [], 'full': bool(full_pack)})
        self.launchctl = root / 'bin/launchctl'
        self.launchctl.parent.mkdir()
        self.launchctl.write_text(f'#!{PYTHON}\n' + FAKE_LAUNCHCTL.replace('__ROOT__', repr(str(ROOT))))
        self.launchctl.chmod(0o755)
        self.env = {**os.environ, 'HOME': str(self.home), 'JW_B6_DESK_JOBS': str(self.jobs),
                    'JW_B6_DESK_CONTROL': str(self.control), 'JW_B5_SYNTHETIC_ONLY': '1',
                    'JW_B6_BUNDLE_TEMPLATE': str(self.root / 'members' if full_pack else windows.template()),
                    'JW_B6_CAPTURE_TEMPLATE': str(self.root / 'capture'),
                    'PYTHONDONTWRITEBYTECODE': '1'}
        self.calls = []
        self.loop_root = root / 'loop'
        config = read(self.measurement / 'configs/b6/loop.json')
        config['wake_argv'] = []
        if full_pack:
            config['base_order'] = [full_pack] + [p for p in PACKS if p != full_pack]
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
        if self.full_pack:
            return self.make_full_tree(pack)
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

    def make_full_tree(self, pack):
        """Registered stage/member/unit counts, with strict synthetic bundles."""
        from joulewise.b6.acceptance import _stage_roles
        from tests.test_reduce import self_consistent_calibration
        from joulewise.powermetrics_fiducial import verify_stored_evidence_physics
        t = tree(self.full_pack)
        old = read(pack / 'plan_tree.json')
        t.update(plan=old['plan'], window_identity=old['window_identity'],
                 downstream_contract=old['downstream_contract'])
        stages, roles = _stage_roles(t)
        science = {m['run_id']: m for m in t['science']}
        external = t['external_inputs']
        manifests = external['manifests'] if isinstance(external, dict) else external
        external_members = {m['run_id']: (manifest, m) for manifest in manifests for m in manifest.get('members', [])}
        specs, inventory = [], []
        (self.root / 'members').mkdir()
        for stage in t['stage_graph']:
            if stage['kind'] != 'campaign_collection':
                continue
            ids = [rid for rid in stages if stages[rid] == stage['stage_id']]
            directory = pack / ('full-' + stage['stage_id'])
            directory.mkdir()
            family = windows.FAMILY + ('-prefill' if 'prefill' in stage['stage_id'] else '-decode')
            rows, blocks, repeats = [], {}, []
            for ordinal, rid in enumerate(ids, 1):
                bundle = self.root / 'members' / rid
                source_id = windows.MEMBERS[(ordinal - 1) % 6][0] if rid in science else windows.MEMBERS[0][0]
                source = windows.template() / source_id if rid in science else reference_template()
                windows.copy_member(source, bundle)
                config_value = read(bundle / 'config.json')
                config_value['run_id'] = rid
                if rid in science:
                    config_value['run_metadata']['tags'] = [tag for tag in config_value['run_metadata']['tags']
                        if not tag.startswith('df-condition=')] + ['df-condition=' + family]
                (bundle / 'config.json').write_bytes(windows.normalized_config(config_value))
                md = read(bundle / 'metadata.json')
                md.update(run_id=rid, config_sha256=windows.sha(bundle / 'config.json'))
                write(bundle / 'metadata.json', md)
                events = bundle / 'events.jsonl'
                events.write_text(events.read_text().replace('"run_id": "' + source_id + '"', '"run_id": "' + rid + '"'))
                config = directory / (rid + '.json')
                shutil.copyfile(bundle / 'config.json', config)
                rel = config.relative_to(self.measurement).as_posix()
                digest = windows.sha(config)
                rows.append({'ordinal': ordinal, 'run_id': rid, 'config': config.name, 'config_sha256': digest})
                inventory.append({'path': config.relative_to(pack).as_posix(), 'sha256': digest})
                if rid in science:
                    m = science[rid]
                    m.update(config_path=rel, config_sha256=digest, stage_id=stage['stage_id'])
                    if m.get('block_id'):
                        blocks.setdefault(m['block_id'], {})[m['position']] = rid
                    else:
                        repeats.append({'slot': rid, 'bundle_id': rid})
                else:
                    _, m = external_members[rid]
                    m.update(path=rel, sha256=digest)
            manifest_path = directory / 'order_manifest.json'
            write(manifest_path, {'manifest_id': stage['stage_id'], 'executed_order': rows})
            rel = manifest_path.relative_to(self.measurement).as_posix()
            stage['input'] = {'path': rel, 'manifest_id': stage['stage_id'], 'sha256': windows.sha(manifest_path)}
            stage['launch']['commands'][0]['argv_template']['arguments'][0]['value'] = directory.relative_to(self.measurement).as_posix()
            if ids and ids[0] in external_members:
                manifest, _ = external_members[ids[0]]
                manifest['manifest'] = {'path': rel, 'sha256': windows.sha(manifest_path)}
            if repeats or blocks:
                specs.append({'cell_id': stage['stage_id'], 'kind': 'comparative' if blocks else 'absolute',
                              'condition_family_id': family, 'target_precheck_path': None,
                              'expected_n': len(repeats) or len(blocks), 'members': repeats,
                              'blocks': [{'block_id': key, 'members': value} for key, value in blocks.items()]})
        identity = old['arm_attachments']['identity_pin_projection']['identity_units'][0]
        identity['config_inventory'] = inventory
        t['arm_attachments']['identity_pin_projection'] = {'identity_units': [identity]}
        write(pack / 'extraction_spec.json', {'schema_version': 'joulewise.detection_floor_extraction_spec.v1', 'cells': specs})
        t['downstream_contract']['extraction_spec']['sha256'] = windows.sha(pack / 'extraction_spec.json')
        t['downstream_contract']['extraction_spec']['path'] = (pack / 'extraction_spec.json').relative_to(self.measurement).as_posix()
        evidence, raw, events = self_consistent_calibration()
        # This is generated pulse data; its real physics verifier runs both here
        # and at acceptance. No stored value or energy reader is substituted.
        evidence['b_fiducial_s'] = max(evidence['b_fiducial_s'], verify_stored_evidence_physics(evidence, raw, events))
        capture = self.root / 'capture'
        (capture / 'raw').mkdir(parents=True)
        (capture / 'raw/powermetrics.plist').write_bytes(raw)
        (capture / 'events.jsonl').write_bytes(events)
        from tests.test_battery_float import PairAuthenticationTests
        pair = PairAuthenticationTests().pair(capture)
        for slot in ('pre', 'post'):
            pair[slot].update(phase='slot_' + slot, session_id=None)
        evidence['battery_float'] = pair
        write(capture / 'instrument_evidence.json', evidence)
        return t

    def register_acceptance(self):
        from tests.b6.support import document
        from joulewise.b6 import model_files
        md = read(next((self.root / 'members').glob('*/metadata.json')))
        identity = model_files.run_identity(md)
        reg = document()
        reg.update(pack_id=self.campaign, registered_commit=subprocess.run(
            ['git', '-C', str(self.measurement), 'rev-parse', 'HEAD'], check=True, capture_output=True, text=True).stdout.strip())
        target = self.measurement / 'configs/b6/registration'
        write(target / 'acceptance.json', reg)
        write(target / 'identity_pins.json', {'schema': 'joulewise.b5_identity_pins.v1',
            'runtime_versions': {'python': '3.13', 'packages': identity['packages']},
            'units': {'synthetic': {'model_source': identity['model_source'],
                                  'model_artifact_sha256': identity['model_artifact_sha256'], 'stack_identity': {}}}})

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
            argv.extend(['--workers', '4' if self.full_pack else '2'])
            control = read(self.control)
            if control.get('harvest_fault') == 4 and '--smoke' not in argv:
                control.pop('harvest_fault')
                write(self.control, control)
                script = argv[1]
                injected = ('import sys; sys.path.insert(0, ' + repr(str(Path(script).parents[1])) + '); '
                            'from scripts import harvest_b6_session as w\n'
                            'def fault(*args, **kwargs): raise RuntimeError("synthetic acceptance program fault")\n'
                            'w.accept_archive = fault\n'
                            'raise SystemExit(w.main(sys.argv[1:]))\n')
                argv = [argv[0], '-c', injected, *argv[2:]]
        # Exhaustive allowlist: an absolute host-tool path cannot bypass a
        # basename denylist, and new subprocesses must earn a fixture seam.
        allowed = (argv[0] == str(self.launchctl) or Path(argv[0]).name == 'git' or
                   (Path(argv[0]).name.startswith('python') and
                    (argv[1:4] == ['-m', 'venv', '--without-pip'] or
                     any(arg.endswith('/scripts/harvest_b6_session.py') for arg in argv) or
                     any(arg.endswith('/scripts/recover_calibration_ledger.py') for arg in argv) or
                     (argv[1:2] == ['-c'] and 'synthetic acceptance program fault' in argv[2]))))
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


def complete_unfinalized_custody(capture, *, attempt_id, t1, bound="0.040"):
    """Complete synthetic custody authenticated by the real resume-finalize."""
    (capture / 'raw').mkdir(parents=True)
    files = {'raw/powermetrics.plist': b'raw-capture-bytes\n',
             'events.jsonl': b'{"timestamp_s":99.0}\n',
             'power_trace.csv': b'rail,power_w\ncpu_power,1.0\n'}
    for name, raw in files.items():
        (capture / name).write_bytes(raw)
    hashes = {name: hashlib.sha256(raw).hexdigest() for name, raw in files.items()}
    evidence = {'validation_id': attempt_id, 'status': 'valid', 'artifact_sha256': hashes,
                'bindings': t1, 'capture_wall_time_s': 99.0, 'b_fiducial_s': float(bound)}
    raw = (json.dumps(evidence, sort_keys=True) + '\n').encode()
    raw = raw.replace(b'"b_fiducial_s": ' + str(float(bound)).encode(),
                      b'"b_fiducial_s": ' + bound.encode())
    (capture / 'instrument_evidence.json').write_bytes(raw)
    write(capture / 'manifest.json', {'validation_id': attempt_id, 'artifacts': {
        **hashes, 'instrument_evidence.json': hashlib.sha256(raw).hexdigest()}})


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
    opening_stop = state.get('stop') in ('operative_bound_above_stop', 'pre_calibration_screen_failed', 'pre_calibration_capture_failed')
    unfinalized = state.get('unfinalized')
    selected = ([] if opening_stop else dispatches if unfinalized == 'post' else
                dispatches[:2] if state.get('lost') or state.get('stop') else dispatches)
    for dispatch in selected:
        for run_id in dispatch.run_ids[:next(s['expected_count'] for s in t['stage_graph'] if s['stage_id'] == dispatch.stage_id)]:
            if run_id in state.get('missing', ()):
                continue
            source = Path(os.environ['JW_B6_BUNDLE_TEMPLATE']) / run_id
            if not source.exists() and t.get('smoke_reduction'):
                # A Round builds strict bundles for its selected pack only.
                # The next pack's smoke still launches through the installer
                # to exercise ledger reservation at the hand-over. Retain the
                # seed's identity: harvesting it would disclose the mismatch.
                source = next(Path(os.environ['JW_B6_BUNDLE_TEMPLATE']).glob('*/metadata.json')).parent
            windows.copy_member(source, claim / run_id)
    # Real ledger appends and finalization, retaining the builder's capture
    # shapes, so pin advance must make a real pin-only Git commit.
    epoch = read(Path(b['identity_epoch_json']))
    t1 = read(Path(b['t1_bindings_json']))
    slots = {}
    for slot in ('pre', 'post'):
        capture = Path(b[slot + '_calibration_dir'])
        slots[slot] = {'attempt_id': b[slot + '_attempt_id'], 'custody_locator': str(capture),
                       'identity_epoch': epoch, 't1_bindings': t1}
        if (state.get('lost') or state.get('stop')) and slot == 'post' and unfinalized != 'post':
            continue
        if slot == unfinalized:
            complete_unfinalized_custody(capture, attempt_id=b[slot + '_attempt_id'], t1=t1,
                                         bound=state.get('b_fiducial', '0.040'))
            continue
        (capture / 'raw').mkdir(parents=True)
        if state.get('full') and not t.get('smoke_reduction'):
            shutil.copytree(Path(os.environ['JW_B6_CAPTURE_TEMPLATE']), capture, dirs_exist_ok=True)
        else:
            (capture / 'raw/powermetrics.plist').write_bytes(f'raw-{slot}'.encode())
            (capture / 'events.jsonl').write_text('{"timestamp_s":99.0}\n')
        anchor = read(next(Path(os.environ['JW_B6_BUNDLE_TEMPLATE']).glob('*/metadata.json')))[
            'uncertainty_evidence']['clock_anchor']
        if not state.get('full') or t.get('smoke_reduction'):
            write(capture / 'instrument_evidence.json', {'slot': slot, 'clock_anchor': anchor})
        if state.get('stop') == 'pre_calibration_screen_failed':
            evidence = read(capture / 'instrument_evidence.json')
            evidence.pop('b_fiducial_s', None)
            write(capture / 'instrument_evidence.json', evidence)
        write(capture / 'manifest.json', {'slot': slot})
    ledger_path = measurement / plan.DEFAULT_LEDGER_RELATIVE
    ledger.append_bracket_session_receipt(ledger_path, session_id=b['bracket_session_id'],
        window_id=t['window_identity']['window_id'], plan_id=t['plan']['plan_id'],
        plan_sha256=windows.sha(pack / t['plan']['path']), evidence_root_id=t['window_identity']['evidence_root_id'],
        runs_root=claim, slots=slots, head_pin_path=measurement / plan.HEAD_PIN_RELATIVE, require_committed_pin=True,
        repo_root=measurement)
    for slot in ('pre',) if (state.get('lost') or state.get('stop')) and unfinalized != 'post' else ('pre', 'post'):
        if slot == unfinalized:
            ledger.claim_bracket_session_slot(ledger_path, session_id=b['bracket_session_id'],
                slot=slot, attempt_id=b[slot + '_attempt_id'])
            continue
        capture = Path(slots[slot]['custody_locator'])
        ledger.finalize_bracket_session_slot(ledger_path, session_id=b['bracket_session_id'], slot=slot,
            disposition='valid', custody_locator=str(capture), artifact_sha256=ledger.artifact_hashes(capture),
            identity_epoch=epoch, t1_bindings=t1, capture_wall_time_s='99.0', exact_bound_lexeme_s='0.025')
    rows = [{'stage_id': s.stage_id, 'kind': s.kind, 'rc': 0, 'started_epoch_s': 1786206000,
             'ended_epoch_s': 1786206001} for s in chain.stage_plan(t) if s.in_chain]
    if state.get('lost'):
        cutoff = next(i for i, row in enumerate(rows) if row['stage_id'] == dispatches[1].stage_id)
        rows = rows[:cutoff + 1]
    elif unfinalized == 'post':
        rows = [row for row in rows if row['kind'] != 'calibration_capture' or row is rows[1]]
    elif state.get('stop'):
        cutoff = next(i for i, row in enumerate(rows) if row['kind'] == 'calibration_capture')
        rows = rows[:cutoff + 1] if opening_stop else [row for row in rows if row['stage_id'] in
            {s.stage_id for s in dispatches[:2]} or row['kind'] != 'campaign_collection'][:4]
    (night / chain.STAGE_JOURNAL).write_text(''.join(json.dumps(row) + '\n' for row in rows))
    windows.write_journals(custody / 'hazards/monitor')
    # An eligible raw file ensures compression really writes and verifies zstd.
    (custody / 'raw-transcript.txt').write_bytes(b'synthetic transcript\n' * 60000)
    write(night / 'executed_inventory.json', {'measurement_checkout': {'head': p['measurement_head'],
        'status_porcelain': '', 'root': str(measurement), 'files': {}}, 'pack_root': str(pack)})
    if state.get('lost'):
        return
    if state.get('stop'):
        stop = state['stop']
        if stop.startswith('night_') or stop == 'non_observer_process_busy':
            write(night / 'hazard_result.json', {'verdict': 'ABORTED', 'aborted_reason': stop, 'chain': {'exit_code': -15}})
            write(night / 'result.json', {'verdict': 'ABORTED', 'aborted_reason': stop, 'chain_exit_code': -15})
            write(night / 'chain.exited', {'epoch_s': 1786216000, 'exit_code': -15})
        else:
            rc = chain.STOP_EXITS[stop]
            with (night / chain.STAGE_JOURNAL).open('a') as journal:
                journal.write(json.dumps({'stage_id': 'chain.stop', 'kind': stop, 'rc': rc}) + '\n')
            write(night / 'chain.exited', {'epoch_s': 1786216000, 'exit_code': rc})
            write(night / 'result.json', {'verdict': 'CHAIN_STOPPED', 'chain_exit_code': rc})
        return
    write(night / 'chain.exited', {'epoch_s': 1786216000, 'exit_code': 0})
    write(night / 'result.json', {'verdict': 'GO', 'aborted_reason': None, 'chain_exit_code': 0, 'artifacts': []})


def bytes_rehearsal(root):
    """Real CLI ticks, discovery and preparation; synthetic hardware and launch.

    The sizing entries are fixture-only copies of ALPHA's registered allowances,
    not BYTES C5 measurements. No installed job or collection is started.
    """
    import runpy
    from joulewise.b6 import loop as loop_module
    from joulewise.b6.lanes import PrecheckResult, Running
    from tests.fixtures.b5_plan.fake_window import GENESIS_PIN
    assert os.environ.get('JW_B5_SYNTHETIC_ONLY') == '1'
    root = root.resolve()
    measurement = root / 'measurement'
    for directory in ('configs', 'joulewise', 'scripts'):
        shutil.copytree(ROOT / directory, measurement / directory)
    config = read(ROOT / 'configs/b6/loop_bytes.json')
    config.update(loop_root=str(root / 'loop-bytes'), wake_argv=[])
    write(measurement / 'configs/b6/loop_bytes.json', config)
    replication = read(measurement / 'configs/b6/loop.json')
    replication['loop_root'] = str(root / 'loop-replication')
    write(measurement / 'configs/b6/loop.json', replication)
    for pack in config['pack_ids']:
        path = measurement / f'configs/b6/packs/{pack}/registration.json'
        value = read(path)
        value.update(status='registered')
        value.pop('draft_notes', None)
        for estimator in value['estimators']:
            estimator['version'] = 'synthetic-rehearsal'
        write(path, value)
    sizing_path = measurement / 'configs/b6/registration/sizing_b5.json'
    sizing = read(sizing_path)
    # BY-MERGE: BY-C5's R2-3 hold refuses a BYTES pack whose sizing row has no
    # registered P, so the rehearsal carries fixture-only disk terms (the same
    # inputs as tests.b6.test_plan_inputs; not a BYTES C5 measurement).
    b, wait, fixed = 1000001, 7200, 19
    disk_terms = dict(B_bytes=b, extra_wait_raw_bytes=wait, fixed_retained_bytes=fixed,
                      required_free_bytes=2 * (b + wait) + fixed, peak_copies=2,
                      session_wait_budget_s=plan.SESSION_WAIT_BUDGET_S)
    for pack in config['pack_ids']:
        sizing['packs'][pack] = {**sizing['packs']['ALPHA'], 'pack_id': pack, 'disk_derivation': dict(disk_terms)}
    write(sizing_path, sizing)
    ledger_path = measurement / plan.DEFAULT_LEDGER_RELATIVE
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_bytes(b'')
    write(measurement / plan.HEAD_PIN_RELATIVE, GENESIS_PIN)
    sites = measurement / '.venv/lib/python3.13/site-packages'
    sites.mkdir(parents=True)
    (measurement / '.gitignore').write_text('.venv/\nruns/\n')
    init_git_fixture(measurement, '-q')
    # Same fixture identity as Round: CI runners have no global git identity.
    for args in (('config', 'user.name', 'B6 Desk'), ('config', 'user.email', 'desk@invalid'),
                 ('config', 'commit.gpgsign', 'false'), ('add', '.'), ('commit', '-qm', 'synthetic BYTES rehearsal')):
        subprocess.run(['git', '-C', str(measurement), *args], check=True, capture_output=True)
    fake = root / 'bin/launchctl'
    fake.parent.mkdir()
    fake.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> ' + str(root / 'launchctl.argv') + '\nexit 0\n')
    fake.chmod(0o755)
    calls, transitions = [], ['NEXT']
    real_loop = loop_module.Loop
    def runner(argv, **kwargs):
        calls.append(argv)
        if argv[0] == str(measurement / '.venv/bin/python'):
            payload = {name: base64.b64encode(b'{}').decode() for name in
                       ('identity-epoch.json', 't1-bindings.json')}
            return subprocess.CompletedProcess(argv, 0, stdout=json.dumps(payload), stderr='')
        if 'ls-remote' in argv:
            return subprocess.CompletedProcess(argv, 0, stdout='', stderr='')
        return subprocess.run(argv, **{"capture_output": True, "text": True, "timeout": 120,
                                       "check": False, **kwargs})
    def factory(repo, loop_root, **kwargs):
        kwargs.update(run=runner, mailer=Mailer(loop_root, __import__(
            'joulewise.flags.catalog', fromlist=['load_catalog']).load_catalog(measurement / config['flag_catalog']),
            clock=time.time, transport=Transport()))
        loop = real_loop(repo, loop_root, **kwargs)
        loop.lanes.precheck.run = lambda *args: PrecheckResult(fingerprint={'synthetic': True})
        loop.lanes.driver.launchctl_bin = str(fake)
        # This stub proves preparation only. BY-SLOTS/BY-PIN must supply
        # arm_attachments.launch = joulewise.stage_launch_bindings.v1;
        # real DriverLane.launch with scratch HOME/fake launchctl must pass before any BYTES arm.
        def launch(prepared):
            runner([str(fake), 'rehearsal-only', prepared.session_id], check=True)
            return Running('synthetic-no-job')
        loop.lanes.driver.launch = launch
        return loop
    argv = [str(ROOT / 'scripts/b6_loop.py'), '--repo-root', str(measurement),
            'tick', '--loop-root', str(root / 'loop-bytes')]
    with mock.patch.dict(os.environ, {'PATH': str(fake.parent) + ':' + os.environ['PATH']}), \
            mock.patch.object(sys, 'argv', argv), mock.patch.object(loop_module, 'Loop', factory):
        os.environ.pop('JW_B6_LOOP_ROOT', None)
        for _ in range(3):
            try:
                runpy.run_path(str(ROOT / 'scripts/b6_loop.py'), run_name='__main__')
            except SystemExit as exc:
                if exc.code != 0:
                    raise
            state = read(root / 'loop-bytes/state.json')
            transitions.append(state['state'])
            if state['state'] == 'HOLD_LOOP':
                raise AssertionError(state.get('last_exception', state))
    assert transitions == ['NEXT', 'PRECHECK', 'SMOKE_RUN', 'SMOKE_RUN'], transitions
    assert state['session']['packs'] == ['bytes-s1-p1'], state
    prepared = state['session']['smoke_prepared']
    assert Path(prepared['plan_path']).parent.parent.joinpath('session.json').is_file()
    result = {'root': str(root), 'transitions': transitions, 'packs': state['session']['packs'],
              'smoke_prepared': prepared, 'fake_launchctl': (root / 'launchctl.argv').read_text(),
              'discovered': len(state['packs'])}
    write(root / 'rehearsal.json', result)
    return result
