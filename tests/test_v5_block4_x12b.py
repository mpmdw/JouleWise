"""Ruling 76 F.1/F.2/F.6 desk compositions; no live hardware qualification.

Ambient OS probes/clocks and the miniature pack's metadata, roster and ARM
row semantics are fixtures. The author, journal, GO/T0/capability replay,
plan loader, desk closeout, assembler, gates and sizing replay are production
code. No privileged command is executed; none of this is live qualification.
"""
import ast
import base64
import inspect
import io
import itertools
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import unittest
from unittest import mock

from joulewise import arm_readiness as readiness, arm_readiness_evidence_t0 as author
from joulewise import clock_reference, kernel_clock, night_gate, t0_rehearsal as t0
from joulewise import v5_qualification as q
from scripts import capture_t0_step as capture, write_v5_qualification_plan as writer
from scripts import produce_t0_rehearsal_bundle as producer
from tests import test_arm_readiness_evidence_t0 as af
from tests import test_t0_anchor_positive_control as physical
from tests import test_v5_pack_rehearsal as mapping_fixture
from tests import test_v5_qualification_plan as sizing_fixture
from tests import test_arm_readiness as consumption_fixture
from tests import test_run_night as driver_fixture
from scripts import run_night as driver, v5_s1_desk_closeout as desk

ROOT = Path(__file__).resolve().parents[1]


def governed_callsite_inventory():
    """Retain argv expressions at launch sinks and their dynamic builders.

    Literal argv also have to resolve into the table. This inventory closes
    the dynamic-expression gap: adding/changing a forwarded builder or launch
    cannot silently escape that census. Lines are deliberately not identity.
    """
    sinks = {'observed_run', 'observed_popen', 'Popen', '_fresh_probe',
             '_execute_probe', '_probe_runner', 'execute', '_run'}
    builders = {'_command_for_step', '_courier_argv', '_pack_launcher_argv', '_bind_argv'}
    result = {}
    for module in (author, capture, driver, night_gate):
        rows = []
        tree = ast.parse(inspect.getsource(module))
        for function in ast.walk(tree):
            if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if function.name in builders:
                rows.append([function.name, 'builder', ast.unparse(function)])
            for node in ast.walk(function):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node is not function:
                    continue
                if isinstance(node, ast.Call):
                    name = node.func.attr if isinstance(node.func, ast.Attribute) else (
                        node.func.id if isinstance(node.func, ast.Name) else '')
                    if name in sinks and node.args:
                        # _fresh_probe has context, kind and label before argv.
                        index = 3 if name == '_fresh_probe' else 1 if name == '_run' else 0
                        if len(node.args) > index:
                            rows.append([function.name, name, ast.unparse(node.args[index])])
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    if any(isinstance(target, ast.Name) and target.id in {'argv', 'command'} for target in targets):
                        rows.append([function.name, 'argv assignment', ast.unparse(node.value)])
        result[module.__name__] = sorted(rows)
    return result


class RegisteredRosterTests(unittest.TestCase):
    def test_governed_calls_and_dynamic_builders_have_reviewed_inventory(self):
        expected = q.read(ROOT / 'tests/fixtures/v5_qualification/process_argv_inventory.json')
        self.assertEqual(governed_callsite_inventory(), expected,
            'governed argv changed: derive its consumer outcome and register it beside G1, then refresh the inventory')

    def test_exact_argv_outcomes_follow_consumers(self):
        cases = [(('/usr/bin/pgrep', '-lf', af.t0._prewindow.CONTAMINANTS), (0, 1)),
                 (('/usr/bin/pgrep', '-lf', '-g', '123,456', '.'), (0, 1))]
        for argv, codes in cases:
            for code in (*codes, 2):
                row = dict(argv=argv, expected_outcome=t0.qualification_process_outcome(argv),
                           state='EXITED', exit_code=code, timed_out=False, stdout='17 resident matches\n')
                self.assertEqual(t0.qualification_process_completed(row), code in codes)
        for server in clock_reference.SERVER_ROSTER:
            argv = clock_reference.build_sntp_argv(server)
            for code in (0, 1, 2, -9):
                row = dict(argv=argv, expected_outcome=t0.qualification_process_outcome(argv),
                           state='EXITED', exit_code=code, timed_out=False)
                self.assertTrue(t0.qualification_process_completed(row))
                row['timed_out'] = True
                self.assertFalse(t0.qualification_process_completed(row))
        unknown = ['/usr/bin/pgrep', '-lf', 'unregistered-pattern']
        self.assertEqual(t0.qualification_process_outcome(unknown), {'unregistered': True})
        census = cases[0][0]
        outcome = t0.qualification_process_outcome(census)
        outcome['exit_codes'].append(2)
        self.assertEqual(t0.qualification_process_outcome(census), {'exit_codes': [0, 1]})

    def test_ast_literal_argv_census_has_no_missing_registration(self):
        """Census source expressions, including new probes in existing functions.

        Dynamic slots use representative values. Forwarded argv are separately
        exercised through the real stage builders and full author below.
        """
        from scripts import run_night
        modules = (author, capture, run_night, night_gate)
        seen = []
        for module in modules:
            tree = ast.parse(inspect.getsource(module))
            def value(node):
                if isinstance(node, ast.Constant):
                    return node.value
                if isinstance(node, ast.Name):
                    known = vars(module).get(node.id)
                    if isinstance(known, (str, tuple)):
                        return known
                    if node.id == 'expected_prewindow_script':
                        return '/fixture/joulewise/prewindow.py'
                    return ('time.apple.com' if node.id == 'server' else '123' if node.id in {'pgid', 'pids'}
                            else '/fixture/.venv/bin/python' if node.id == 'python' else '/fixture')
                if isinstance(node, ast.Attribute):
                    try:
                        return eval(ast.unparse(node), vars(module))
                    except (NameError, AttributeError):
                        return '/fixture'
                if isinstance(node, ast.Subscript):
                    return '/fixture'
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                    return str(Path(value(node.left)) / str(value(node.right)))
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute) and node.func.attr in {'absolute', 'resolve'}:
                        return value(node.func.value)
                    if isinstance(node.func, ast.Attribute) and node.func.attr == 'join':
                        return '123,456'
                    if node.args:
                        return str(value(node.args[0]))
                    return '/fixture'
                return '/fixture'
            for node in ast.walk(tree):
                if not isinstance(node, (ast.List, ast.Tuple)) or not node.elts:
                    continue
                # Every literal executable vector, plus the stage's python
                # vectors. Plain data arrays are outside the launch census.
                first = node.elts[0]
                dynamic_executable = (isinstance(first, ast.Attribute) and ast.unparse(first) == 'sys.executable'
                    or isinstance(first, ast.Call) and isinstance(first.func, ast.Name) and first.func.id == 'str'
                    and len(node.elts) > 1 and (str(value(first)).endswith('/python')
                        or isinstance(node.elts[1], ast.Constant) and isinstance(node.elts[1].value, str)
                        and node.elts[1].value.startswith('-')))
                if not (isinstance(first, ast.Constant) and isinstance(first.value, str)
                        and (first.value.startswith(('/bin/', '/usr/bin/', '/usr/sbin/')) or first.value == 'git')
                        or isinstance(first, ast.Name) and first.id == 'python' or dynamic_executable):
                    continue
                argv = tuple(str(value(item)) for item in node.elts)
                # Known concatenations (resync prefix, power adapter) are
                # represented by the complete builder test, not a partial argv.
                if any(isinstance(item, ast.Starred) for item in node.elts):
                    continue
                seen.append((module.__name__, node.lineno, argv))
                self.assertIsNotNone(t0.qualification_process_registration(argv),
                                     f'{module.__name__}:{node.lineno}: {argv}')
        self.assertGreater(len(seen), 25)

    def test_stage_builder_roster_is_registered(self):
        from types import SimpleNamespace
        assignments = {name: '/fixture/' + name for name in capture.WINDOW_ENV_KEYS}
        context = SimpleNamespace(repository=Path('/fixture'), assignments=assignments,
            frozen_plan_path=Path('/fixture/calibration_plan.json'), plan_id='plan', plan_sha256='a'*64,
            prewindow_command=('/fixture/.venv/bin/python', '/fixture/joulewise/prewindow.py',
                               '--t0-wait', '--timeout-min', '45', '--window', 'GAMMA'))
        for step in capture.STEP_ORDER:
            argv = capture._command_for_step(context, step)
            self.assertIsNotNone(t0.qualification_process_registration(argv), (step, argv))
        for kind in ('sample', 'arm'):
            argv = driver._bind_argv(kind, 'job', 5, {'interval': 1, 'observer_pid': 123})
            self.assertIsNotNone(t0.qualification_process_registration(argv), argv)
        plan = SimpleNamespace(measurement_root='/fixture', custody_root='/fixture/custody', plan_id='fixture',
                               pack_night={'pack_root': '/fixture/pack'})
        argv = driver._pack_launcher_argv(plan, Path('/fixture/plan.json'), Path('/fixture/arm.json'),
            Path('/fixture/manifest.json'), Path('/fixture/go.json'),
            {'table_path': '/fixture/confirmation.json', 'table_sha256': 'a'*64})
        self.assertIsNotNone(t0.qualification_process_registration(argv), argv)
        with mock.patch.object(driver, '_watchdog_liveness_for_courier', return_value=('/fixture/watchdog', 0, 'idle')):
            argv = driver._courier_argv(Path('/fixture/custody'), plan, Path('/fixture/courier'))
        self.assertIsNotNone(t0.qualification_process_registration(argv), argv)
        from types import SimpleNamespace
        from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
        adapter = PowermetricsTelemetryAdapter(None, privilege_prefix=('sudo', '-n'))
        argv = adapter._command(SimpleNamespace(sampling=SimpleNamespace(power_hz=10.)),
                                Path('/fixture/powermetrics-idle.plist'), count=300)
        self.assertIsNotNone(t0.qualification_process_registration(argv), argv)

    def test_missing_table_row_and_new_governed_argv_are_detected(self):
        argv = ('/usr/bin/pgrep', '-lf', af.t0._prewindow.CONTAMINANTS)
        shortened = tuple(row for row in t0.QUALIFICATION_PROCESS_OUTCOMES if row[0] != argv)
        with mock.patch.object(t0, 'QUALIFICATION_PROCESS_OUTCOMES', shortened):
            with self.assertRaises(AssertionError):
                self.test_ast_literal_argv_census_has_no_missing_registration()
        with mock.patch.object(author, 'AGENT_CENSUS_ARGV', ('/usr/bin/pgrep', '-lf', 'new census'), create=True):
            self.assertIsNone(t0.qualification_process_registration(author.AGENT_CENSUS_ARGV))


class NativeAuthorJournalTests(unittest.TestCase):
    def test_entire_real_author_roster_to_journal_assembler_and_g1(self):
        temporary, repository, pack, custody, _, _inputs = af.make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        mapping = mapping_fixture.ObservedDeskMappingTests()
        mapping.setUp()
        self.addCleanup(mapping.doCleanups)
        closeout = prepare_native_qualification(mapping)
        journal = mapping.night / 'process-observations.jsonl'
        journal.unlink()
        stub = Path(temporary.name).resolve() / 'ambient-probe'
        stub.write_text('#!' + sys.executable + '\nimport os,base64,sys\n'
            'sys.stdout.buffer.write(base64.b64decode(os.environ["PROBE_STDOUT"]))\n'
            'sys.stderr.buffer.write(base64.b64decode(os.environ["PROBE_STDERR"]))\n'
            'sys.exit(int(os.environ["PROBE_EXIT"]))\n')
        stub.chmod(0o700)
        real_init = subprocess.Popen.__init__
        probes = []
        def ambient(process, argv, **options):
            if not isinstance(process, t0.ObservedProcess):
                return real_init(process, argv, **options)
            if any(str(arg).endswith('/scripts/run_night.py') for arg in argv):
                answer = subprocess.CompletedProcess(argv, 0, b'', b'')
            else:
                probes.append(tuple(argv))
                answer = af.passing_probe(argv, cwd=repository)
                if tuple(argv) == ('/usr/bin/pgrep', '-lf', af.t0._prewindow.CONTAMINANTS):
                    answer = af._probe_result(argv, repository, exit_code=0,
                        stdout=''.join(f'{100+i} mds_stores\n' for i in range(17)))
                if tuple(argv) == tuple(clock_reference.build_sntp_argv(clock_reference.SERVER_ROSTER[-1])):
                    answer = af._probe_result(argv, repository, exit_code=2)
            stdout = answer.stdout.encode() if isinstance(answer.stdout, str) else answer.stdout
            stderr = answer.stderr.encode() if isinstance(answer.stderr, str) else answer.stderr
            options['executable'] = str(stub)
            options['env'] = dict(options.get('env') or os.environ,
                PROBE_STDOUT=base64.b64encode(stdout).decode(),
                PROBE_STDERR=base64.b64encode(stderr).decode(),
                PROBE_EXIT=str(answer.exit_code if hasattr(answer, 'exit_code') else answer.returncode))
            return real_init(process, argv, **options)
        with (af.author_environment(repository, probe=None),
              mock.patch.object(subprocess.Popen, '__init__', ambient),
              t0.process_journal(journal)):
            driver_argv = [sys.executable, '-B', '/fixture/scripts/run_night.py', 'run', '--plan', '/fixture/plan.json']
            self.assertEqual(t0.observed_run(driver_argv, capture_output=True).returncode, 0)
            result = author.author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(result['status'], 'PASS')
        self.assertGreaterEqual(len(probes), 18)
        for argv in probes:
            self.assertIsNotNone(t0.qualification_process_registration(argv), argv)
        closeout()
        # No process records are manufactured or mapped by the test.
        verdict = mapping.assemble(g7_locator=None)
        execution = producer.read(mapping.records / 'execution.json')
        self.assertTrue(execution['sequence_completed'])
        maintenance = [row for row in execution['processes'] if row['argv'] ==
                       ['/usr/bin/pgrep', '-lf', af.t0._prewindow.CONTAMINANTS]]
        self.assertEqual(len(maintenance), 1)
        self.assertEqual(maintenance[0]['exit_code'], 0)
        self.assertEqual(len(maintenance[0]['stdout'].splitlines()), 17)
        bundle = producer.reader.load_evidence_bundle(mapping.root, home=mapping.root.parents[1],
            inventory=mapping_fixture.fixture_inventory(mapping.root),
            manifest_name=producer.reader.QUALIFICATION_MANIFEST_NAME)
        self.assertEqual(t0.evaluate_g1(bundle).status, t0.GateStatus.PASS)
        gates = {row['gate_id']: row for row in verdict['gates']}
        for gate in ('G1', 'G3', 'G5', 'G8', 'G9'):
            self.assertEqual(gates[gate]['status'], 'PASS', gates[gate])


def prepare_native_qualification(mapping):
    """Regenerate GO/consumption after the old mapping fixture changes inputs.

    No journal, assembly, GO/T0 replay, consumption, plan-loading, closeout or
    gate seam is patched. The tiny pack's ARM semantics and metadata are
    synthetic; clock/boot/census observations are ambient fixture inputs.
    """
    from dataclasses import replace
    from tests.test_network_time_off import receipt as off_receipt
    from tests.test_t0_rehearsal import REAL_G5_T0_AUTHENTICATOR
    case = consumption_fixture.LaunchConsumptionV2Tests()
    case.custody = mapping.root
    case.arm_path = next(mapping.root.glob('*/arm_readiness.receipts/arm-0001.json'))
    case.arm = q.read(case.arm_path)
    case.pack = Path(case.arm['pack']['pack_root'])
    namespace = case.arm_path.parent.parent
    case.manifest_path = namespace / 'arm_readiness.t0.inputs/launch-manifest.json'
    manifest = q.read(case.manifest_path)
    case.window_root = Path(manifest['window_plan_root'])
    case.chain_path = case.window_root / 'window-chain.zsh'
    case.exec_argv = manifest['launch_command']
    measurement = mapping.base
    for relative in ('scripts/backup_runs.sh', desk.RUNSHEET):
        target = measurement / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    # All custody and observations live outside the tracked measurement tree.
    (measurement / '.git/info/exclude').write_text('*\n')
    subprocess.run(['git', '-C', str(measurement), 'add', '-f', 'scripts/backup_runs.sh', desk.RUNSHEET], check=True)
    subprocess.run(['git', '-C', str(measurement), '-c', 'user.name=Fixture',
        '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'desk fixture sources'], check=True)
    head = subprocess.check_output(['git', '-C', str(measurement), 'rev-parse', 'HEAD'], text=True).strip()
    case.arm['reviewed_main']['head_commit'] = head
    chain = case.chain_path.read_text()
    case.chain_path.write_text('export V5_QUALIFICATION_OCCURRENCE=s1\n' + chain)
    Path(str(case.chain_path) + '.sha256').write_bytes(readiness.gnu_sidecar(q.sha(case.chain_path), case.chain_path.name))
    now = time.monotonic_ns()
    for index, name in enumerate(author._CAPTURE_FILES.values()):
        path = namespace / author._INPUT_DIRECTORY / name
        row = q.read(path)
        row.update(started_monotonic_ns=now-1000+index*100,
                   finished_monotonic_ns=now-990+index*100, boot_session_id=case.arm['boot_session_id'])
        path.write_bytes(readiness.render_json(row))
    for path in (namespace / author._SOURCE_DIRECTORY).glob('*.json'):
        row = q.read(path)
        row['head_commit'] = head
        for ref in row.get('input_artifacts', []):
            ref.update(producer.reference(ref['path']))
        path.write_bytes(readiness.render_json(row))
    for item in case.arm['evidence']:
        path = namespace / item['path']
        row = q.read(path)
        row.update(boot_session_id=case.arm['boot_session_id'], pack_sha256=case.arm['pack']['pack_sha256'],
                   head_commit=head, valid_until_monotonic_ns=case.arm['valid_until_monotonic_ns'])
        for fact in row['facts']:
            source = namespace / fact['source_path']
            if source.exists():
                fact['source_sha256'] = q.sha(source)
        path.write_bytes(readiness.render_json(row))
        item['sha256'] = q.sha(path)
        Path(str(path)+'.sha256').write_bytes(readiness.gnu_sidecar(item['sha256'], path.name))
    case._rewrite_arm()
    args = case._consumer_inputs()
    plan_path = mapping.root / 'night_plan.json'
    plan_body = q.read(args['night_plan'])
    plan_body.update(measurement_root=str(measurement), block_archive_root=str(mapping.base / 'archive'), previous_attempt={'none': True})
    auth_path = Path(plan_body['pack_night']['authorization_record']['path'])
    authorization = q.read(auth_path)
    authorization.update(previous_attempt=plan_body['previous_attempt'], block_archive_root=plan_body['block_archive_root'])
    auth_path.write_bytes(readiness.render_json(authorization))
    plan_body['pack_night']['authorization_record'] = producer.reference(auth_path)
    plan_path.write_bytes(readiness.render_json(plan_body))
    plan = night_gate.NightPlan.from_mapping(plan_body)
    for path in mapping.root.rglob('*.consumed.json*'):
        path.unlink()
    for name in ('go_receipt.json', 'go-census.json'):
        (mapping.night / name).unlink()
    source = driver_fixture.ProbeSource(plan.t0_epoch_s + 1)
    probes = replace(source.probes(), checkout_head=lambda: head)
    gate_receipt = night_gate.Receipt(night_gate.SCHEMA, 'TRANSACTION_PACK', plan.plan_id, 'GO',
        tuple(night_gate.ConditionRow(f'C{i}', 'PASS', None, (),
            {'boot_session_uuid': case.arm['boot_session_id']} if i == 4 else {}) for i in range(1, 6)), None, now)
    with (mock.patch.object(readiness, '_authenticate_launcher_identity', return_value=measurement),
          mock.patch.object(readiness, '_pack_record', return_value=case.arm['pack']),
          mock.patch.object(readiness, '_verify_arm_receipt'),
          mock.patch.object(readiness, '_current_boot_session_id', return_value=case.arm['boot_session_id'])):
        prepared = driver._prepare_pack_night(plan, plan_path, plan_path.read_bytes())
        state = dict(path=case.arm_path, arm=case.arm, sha256=q.sha(case.arm_path))
        driver._produce_pack_go(plan, plan_path, plan_path.read_bytes(), prepared, state, gate_receipt, probes)
        args.update(night_plan=plan_path, authenticated_go_receipt=q.read(mapping.night / 'go_receipt.json'),
                    go_receipt_sha256=q.sha(mapping.night / 'go_receipt.json'), window_chain_sha256=q.sha(case.chain_path))
        with mock.patch.object(readiness, '_authenticate_go_t0_evidence', REAL_G5_T0_AUTHENTICATOR):
            case._invoke_consumer(args)
    context = case.arm['arm_context']
    roots = t0.qualification_backup_sources(mapping.root, context)
    Path(roots['custody'], 'identity.json').write_text('{"fixture":"separate ARM custody"}\n')
    Path(roots['bound_runs'], 'fixture-sentinel.txt').write_text('no bound bundles in miniature roster\n')
    claims = Path(roots['claim_runs'])
    bundle = claims / 'science-fixture'
    bundle.mkdir()
    (bundle / 'metadata.json').write_bytes(readiness.render_json({'run_id': bundle.name}))
    (bundle / 'powermetrics.raw.txt').write_text('synthetic sampler bytes; no hardware claim\n')
    (claims / 'campaign_log.jsonl').write_bytes(readiness.render_json(
        {'record_type': 'idle_admission_whole_window_verdict'}).replace(b'\n', b'') + b'\n')
    record = dict(schema_version=writer.OUTPUT_SCHEMA, occurrence='s1', head=head,
        plan=producer.reference(plan_path), window_id=case.arm['pack']['window_id'],
        terminal_boundary_path=str(mapping.night / 'transcript/post-bracket-terminal-boundary.json'),
        desk_sources=roots, backup_destinations=writer.backup_destinations(context), pack_night=plan.pack_night)
    producer.write(mapping.root / 'qualification-plan-record.json', record)
    producer.write(Path(record['terminal_boundary_path']), dict(session_state='finalized', pin_relation='physical_ahead',
        refusal_code='calibration_ledger_head_mismatch', terminal_head_pin_candidate={'fixture': True}))
    off = off_receipt()
    off.update(plan_id=plan.plan_id, window_id=record['window_id'], boot_id=case.arm['boot_session_id'])
    producer.write(namespace / author._INPUT_DIRECTORY / 'network_time_off.json', off)
    standdown_path = mapping.night / 'standdown-observed.json'
    standdown = q.read(standdown_path)
    standdown.update(boot_session_id=case.arm['boot_session_id'], after={'processes': []})
    standdown_path.write_bytes(readiness.render_json(standdown))
    (mapping.night / 'courier.sent').write_text('fixture delivered\n')
    stage_dir = mapping.night / 'rehearsal-lifecycle'
    for name in t0._LIFECYCLE_STAGES:
        (stage_dir / (name + '.json')).unlink()
    producer.observe_s1_lifecycle(plan)
    def closeout():
        actual_run = subprocess.run
        def ambient(argv, **kwargs):
            if tuple(argv) == tuple(capture.network_time_off.OFF_ARGV):
                return subprocess.CompletedProcess(argv, 0, 'Network Time is already off.\n', '')
            return actual_run(argv, **kwargs)
        with (mock.patch.object(readiness, '_authenticate_launcher_identity', return_value=measurement),
              mock.patch.object(writer, 'pack_roster', return_value=([{'run_id': 'science-fixture', 'stage_id': 'science'}], [], [], [])),
              mock.patch.object(readiness, '_plan_tree', return_value=({'stage_graph': []}, None)),
              mock.patch.object(writer, 'dispatched_stages', return_value=[]),
              mock.patch.object(subprocess, 'run', side_effect=ambient)):
            desk.closeout(plan_path, now=lambda: plan.t0_epoch_s + plan.window_max_s + 1000,
                          clear=lambda *_args, **_kwargs: True)
    return closeout


class LatestChainStartTests(unittest.TestCase):
    def test_full_stage_cap_and_author_allowance_still_start(self):
        sizing = sizing_fixture.SizingTests()
        sizing.setUp()
        self.addCleanup(sizing.doCleanups)
        sizing.sizing['fixed']['pack_t0'] = sizing.allow(360)
        sized = sizing.size()
        template = sizing.root / 'template.zsh'
        template.write_text('echo fixture\n')
        pack = ROOT / 'configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5'
        out = sizing.root / 'chain.zsh'
        with (mock.patch.object(writer, 'pack_roster', return_value=(
                [{'config_path': 'science/member.json'}], [], [], [])),
              mock.patch.object(writer, 'size_window', return_value=sized),
              mock.patch.object(writer, 'g2b_body', return_value='echo fixture\n')):
            result = writer.render_qualification_chain('s1', template, sizing.sizing, pack, 1000., out)
        self.assertEqual(result['latest_chain_start_epoch_s'], 4660)
        plan = night_gate.NightPlan('fixture', 'TRANSACTION_PACK', 1000., sized['window_max_s'],
            0., 'a'*40, str(ROOT), 'a'*40, str(out), str(out)+'.sha256', str(sizing.root), None,
            pack_night={'pack_id': 'fixture'})
        self.assertEqual(night_gate.qualification_start_deadline(plan, out.read_text(), 'G2B_SHAKEDOWN',
                                                               sizing=sizing.sizing), 4660)
        self.assertEqual(sized['remaining_chain_span_s'], sized['programmed_span_s'] - 360)
        self.assertLessEqual(4660 + sized['remaining_chain_span_s'], 1000 + sized['window_max_s'])
        inputs = sizing.root / 'fixture' / author._INPUT_DIRECTORY
        inputs.mkdir(parents=True)
        sizing_path = inputs / 'kernel-frequency-sizing.json'
        sizing_path.write_bytes(readiness.render_json(sizing.sizing))
        authorization = sizing.root / 'authorization.json'
        authorization.write_bytes(readiness.render_json({'purpose': 'G2B_SHAKEDOWN'}))
        plan.pack_night['authorization_record'] = q.reference(authorization)
        command = ['/fixture/prewindow', '--t0-wait']
        (inputs / 'launch-manifest.json').write_bytes(readiness.render_json({'prewindow_command': command}))
        (inputs / 'prewindow-check.json').write_bytes(readiness.render_json({
            'step_id': 'prewindow-check', 'exit_code': 0, 'argv': command,
            'boot_session_id': af.TEST_BOOT_SESSION_ID,
            'started_monotonic_ns': 1, 'finished_monotonic_ns': 2_700_000_000_001}))
        night = sizing.root / 'night'
        night.mkdir()
        with (mock.patch.object(driver.time, 'time', return_value=4660.),
              mock.patch.object(driver.time, 'monotonic', return_value=100.),
              mock.patch.object(readiness, '_current_boot_session_id', return_value=af.TEST_BOOT_SESSION_ID)):
            budget = driver._derivation_start_budget(plan)
            self.assertEqual(budget['latest_chain_start_epoch_s'], 4660)
            self.assertEqual(budget['remaining_chain_span_s'], sized['remaining_chain_span_s'])
            self.assertEqual(driver._derivation_budget_remaining(budget), 0)
            driver._admit_qualification_clean_dwell(plan, night, budget)
            with mock.patch.object(driver.time, 'time', return_value=4661.):
                with self.assertRaisesRegex(night_gate.PackNightRefusal, 'start budget'):
                    driver._admit_qualification_clean_dwell(plan, night, budget)
            sizing_path.write_bytes(b'{}\n')
            with self.assertRaisesRegex(night_gate.PackNightRefusal, 'sha256'):
                driver._derivation_start_budget(plan)
        # Execute the emitted in-chain deadline literal with a fixture date.
        check = next(line for line in out.read_text().splitlines() if '$(/bin/date +%s)' in line)
        check = check.replace('$(/bin/date +%s)', '4660')
        completed = subprocess.run(['/bin/sh', '-c', 'NIGHT_LATEST_CHAIN_START_EPOCH_S=4660\n' + check])
        self.assertEqual(completed.returncode, 0)
        # Older qualified packs without a staged stage-cap sizing file retain
        # their original budget, including when they carry a clock-sizing pin.
        out.write_text('export V5_QUALIFICATION_OCCURRENCE=s1\n'
            'export NIGHT_PROGRAMMED_SPAN_S=900\n'
            'export NIGHT_LATEST_CHAIN_START_EPOCH_S=3700\n'
            'export NIGHT_CLOCK_SIZING_SHA256=' + 'a'*64 + '\n')
        from dataclasses import replace
        legacy = replace(plan, window_max_s=3600, pack_night={'pack_id': 'legacy'})
        budget = driver._derivation_start_budget(legacy)
        self.assertEqual(budget['latest_chain_start_epoch_s'], 3700)
        self.assertNotIn('remaining_chain_span_s', budget)


class RefusalOrderTests(unittest.TestCase):
    def test_missing_chain_precedes_invalid_sizing_and_anchor(self):
        temporary, repository, pack, custody, _, inputs = af.make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        chain = Path(q.read(inputs / 'launch-manifest.json')['window_plan_root']) / 'window-chain.zsh'
        chain.unlink()
        (inputs / 'kernel-frequency-binding.json').write_bytes(b'{}\n')
        with af.author_environment(repository, real_clock_budget=True):
            with self.assertRaises(author.T0EvidenceAuthoringError) as raised:
                author.author_arm_readiness_evidence_t0(pack, custody)
        self.assertEqual(raised.exception.reason_code, 'evidence_author_t0_window_chain_missing')

    def test_valid_anchor_cannot_skip_binding_on_new_or_idempotent_pass(self):
        temporary, repository, pack, custody, _, inputs = af.make_t0_fixture()
        self.addCleanup(temporary.cleanup)
        real_binding = (inputs / 'kernel-frequency-binding.json').read_bytes()
        with (af.author_environment(repository, real_clock_budget=True),
              mock.patch.object(writer, 'pack_roster', return_value=([], [], ['pre', 'post'], [])),
              mock.patch.object(readiness, '_authenticate_launcher_identity', return_value=repository)):
            self.assertTrue(readiness.requires_t0_frequency_gate(pack))
            for published in (False, True):
                if published:
                    (inputs / 'kernel-frequency-binding.json').write_bytes(real_binding)
                    self.assertEqual(author.author_arm_readiness_evidence_t0(pack, custody)['status'], 'PASS')
                    receipt = q.read(custody / pack.name / 'arm_readiness.evidence/evidence-t0-clock-correct-and-prior-state.json')
                    self.assertIn('clock_sizing_binding', receipt['facts'][0]['value'])
                (inputs / 'kernel-frequency-binding.json').write_bytes(b'{}\n')
                with self.assertRaises(author.T0EvidenceAuthoringError):
                    author.author_arm_readiness_evidence_t0(pack, custody)
                (inputs / 'kernel-frequency-binding.json').unlink()
                with self.assertRaises(author.T0EvidenceAuthoringError):
                    author.author_arm_readiness_evidence_t0(pack, custody)


def stage_g10_inputs(case):
    """Writer-stage the small author fixture, then capture R0 natively.

    The miniature pack has two specified streams instead of the production
    GAMMA roster. Only pack metadata/confirmation prerequisites are fixtures;
    the writer's publication, binding, capture, and budget replay stay real.
    """
    source = case.inputs
    binding = q.read(source / 'kernel-frequency-binding.json')
    plan = q.read(Path(binding['plan']['path']))
    sizing = q.read(Path(binding['sizing']['path']))
    custody = Path(case.temporary.name).resolve() / 'g10-preparation'
    custody.mkdir()
    window = custody / 'window-plan'
    window.mkdir()
    old_window = Path(q.read(source / 'launch-manifest.json')['window_plan_root'])
    shutil.copyfile(old_window / 'window.env', window / 'window.env')
    env = (window / 'window.env').read_text()
    import shlex
    env = re.sub(r'(?m)^ARM_READINESS_CUSTODY_ROOT=.*$',
                 'ARM_READINESS_CUSTODY_ROOT=' + shlex.quote(str(custody)), env)
    (window / 'window.env').write_text(env)
    chain = window / 'window-chain.zsh'
    summary = writer.size_window('a1', sizing, brackets=['pre', 'post'])
    original = (old_window / 'window-chain.zsh').read_text()
    original = re.sub(r'(?m)^export (?:NIGHT_PROGRAMMED_SPAN_S|NIGHT_LATEST_CHAIN_START_EPOCH_S|V5_QUALIFICATION_OCCURRENCE)=.*\n', '', original)
    chain.write_text(f'export NIGHT_PROGRAMMED_SPAN_S={summary["programmed_span_s"]}\n'
        f'export NIGHT_LATEST_CHAIN_START_EPOCH_S={math.floor(plan["t0_epoch_s"] + 3660)}\n'
        'export V5_QUALIFICATION_OCCURRENCE=s1\n' + original)
    sidecar = Path(str(chain) + '.sha256')
    sidecar.write_bytes(readiness.gnu_sidecar(q.sha(chain), chain.name))
    authorization = q.read(Path(plan['pack_night']['authorization_record']['path']))
    authorization['permitted_chain_sha256'] = q.sha(chain)
    confirmation = q.read(Path(plan['pack_night']['confirmation_record']['path']))
    transcript = custody / 'confirmation-transcript.txt'
    transcript.write_text('YES ' + confirmation['table_sha256'] + '\n')
    confirmation['transcript_sha256'] = q.sha(transcript)
    confirmation_path = custody / 'prior-confirmation.json'
    confirmation_path.write_bytes(readiness.render_json(confirmation))
    plan.pop('pack_night')
    plan.update(custody_root=str(custody), chain_path=str(chain), chain_sha256_path=str(sidecar))
    from scripts.run_night import COURIER_DEADLINE_S, WINDOW_SHUTDOWN_GRACE_S, deadman_epoch
    end = plan['t0_epoch_s'] + plan['window_max_s']
    parsed = night_gate.NightPlan.from_mapping({**plan, 'pack_night': {
        'pack_id': case.pack.name, 'pack_root': str(case.pack), 'pack_sha256': binding['pack_sha256'],
        'attempt_ordinal': 1, 'authorization_record': q.reference(confirmation_path),
        'confirmation_record': q.reference(confirmation_path)}})
    inputs = dict(schema_version=writer.INPUT_SCHEMA, head=plan['repo_head'], plan=plan,
        pack=dict(root=str(case.pack), sha256=binding['pack_sha256'], attempt_ordinal=1),
        authorization=authorization, confirmation=dict(record=q.reference(confirmation_path),
            transcript=q.reference(transcript), expected_confirmation_digest=confirmation['table_sha256']),
        sizing=sizing, deadlines=dict(latest_chain_start_epoch_s=plan['t0_epoch_s']+3660,
            shutdown_epoch_s=end+WINDOW_SHUTDOWN_GRACE_S,
            courier_epoch_s=end+WINDOW_SHUTDOWN_GRACE_S+COURIER_DEADLINE_S,
            deadman_epoch_s=deadman_epoch(parsed)),
        other_custody_roots=[str(case.control)], arm_context=q.read(source / 'arm-context.json'),
        prerequisites={}, kernel_frequency=case.frequency)
    output = custody / 'g10-input-context.json'
    writer_inputs = custody / 'g10-writer-inputs.json'
    writer_inputs.write_bytes(readiness.render_json(inputs))
    with (mock.patch.object(writer, 'pack_roster', return_value=([], [], ['pre', 'post'], [])),
          mock.patch.object(writer, 'g2b_body', return_value=original),
          mock.patch.object(readiness, '_authenticate_confirmation_table'),
          mock.patch.object(writer, 'authenticate_frozen_pack', return_value=binding['plan']),
          mock.patch.object(readiness, '_authenticate_launcher_identity', return_value=case.repository)):
        stdout = io.BytesIO()
        with mock.patch.object(writer.sys, 'stdout', af._cli_stdout(stdout)):
            case.assertEqual(writer.main(['g10-inputs', '--inputs', str(writer_inputs), '--output', str(output)]), 0)
        result = readiness.parse_json_bytes(stdout.getvalue())
        staged = custody / case.pack.name / author._INPUT_DIRECTORY
        case.assertEqual(result['occurrence'], 'g10-inputs')
        case.assertEqual(q.read(output)['mode'], 'G10_INPUT_CAPTURE_NO_LAUNCH')
        from scripts import check_v5_arm_abort
        with case.assertRaisesRegex(ValueError, 'a1_context'):
            check_v5_arm_abort.context_at(output)
        case.assertEqual(q.authenticated_clock_budget(staged, case.pack)[0], 320.)
        # Capture R0 through the production context loader and stage workflow.
        captured = q.read(source / 'clock-reference.json')
        count = itertools.count(captured['started_monotonic_ns'] + 1)
        def execute(argv, *, cwd):
            if tuple(argv) == tuple(capture._command_for_step(
                    capture._load_context(case.pack, custody, window), 'clock-reference')):
                return subprocess.CompletedProcess(argv, 0, captured['stdout'].encode(), b'')
            if tuple(argv) == tuple(capture.network_time_off.OFF_ARGV):
                return subprocess.CompletedProcess(argv, 0, b'Network Time is already off.\n', b'')
            raise AssertionError(argv)
        with (mock.patch.object(capture, 'REPO_ROOT', case.repository),
              mock.patch.object(capture, '_current_boot_session_id', return_value=af.TEST_BOOT_SESSION_ID),
              mock.patch.object(capture.network_time_off, 'boot_id', return_value=af.TEST_BOOT_SESSION_ID),
              mock.patch.object(kernel_clock, 'read_kernel_frequency', return_value=case.frequency)):
            capture._capture_step_for_test('clock-reference', case.pack, custody, window,
                                      execute=execute, monotonic_ns=lambda: next(count))
            capture._capture_step_for_test('clock-disable', case.pack, custody, window,
                                      execute=execute, monotonic_ns=lambda: next(count))
        for filename in author._CAPTURE_FILES.values():
            if filename not in {'clock-reference.json', 'clock-disable.json'}:
                shutil.copyfile(source / filename, staged / filename)
    case.inputs = staged
    case.custody = custody
    return output


class NativeG10BudgetTests(unittest.TestCase):
    def fixture(self):
        case = physical.PositiveControlTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        stage_g10_inputs(case)
        return case

    def test_writer_staged_real_budget_author_discharges_resync(self):
        case = self.fixture()
        case.frequency = physical.frequency_probe(-207749)
        case.after_frequency = physical.frequency_probe(-190000)
        case.drift_word = -207749
        case.base_ns = case.r0_ns + 1600 * 10**9
        case.movement = 500_000_000
        path = case.inputs / 'clock-reference.json'
        record = q.read(path)
        record['kernel_frequency'] = case.frequency
        path.write_bytes(readiness.render_json(record))
        result = case.run_control()
        self.assertEqual(result['status'], 'DISCHARGED', result)
        detail = q.read(case.control / 'author.stdout.json')['detail']
        self.assertEqual(detail, physical.helper.ANCHOR_DETAIL)
        case.verify_custody()

    def test_real_author_under_five_ms_refuses_copied_binding(self):
        case = self.fixture()
        case.movement = 5_000_000
        argv = [str(case.repository / '.venv/bin/python'), str(case.repository / 'scripts/author_arm_evidence_t0.py'),
                '--pack-root', str(case.pack), '--custody-root', str(case.custody)]
        # At the original path this real binding authenticates. The helper's
        # isolated copy must refuse when the anchor cannot falsify continuity.
        copied = case.control / 'author-custody' / case.pack.name / author._INPUT_DIRECTORY
        shutil.copytree(case.inputs, copied)
        argv[-1] = str(case.control / 'author-custody')
        completed = case.runner(argv, timeout=30)
        self.assertEqual(completed.returncode, 2)
        refusal = readiness.parse_json_bytes(completed.stdout)
        self.assertEqual(refusal['detail'], 'clock_sizing_plan_mismatch')
        self.assertFalse((copied.parent / author._EVIDENCE_DIRECTORY).exists())


if __name__ == '__main__':
    unittest.main()
