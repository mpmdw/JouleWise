import copy
import dataclasses
import datetime as dt
import hashlib
import importlib.abc
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise.b5 import chain, plan
from joulewise.b6 import smoke as s
from joulewise.b6 import acceptance_interface as ai
from joulewise.b6.acceptance_interface import AcceptanceResult, SessionEvidence, StubAcceptance
from tests.b6.support import DeskCase, ROOT, PACKS, tree, fp, synthetic_checkout
from tests.b6.test_precheck import FakeAcceptance
from tests.b6 import support
from tests.git_fixture import init_git_fixture
from tests.fixtures.b5_plan import fake_window


class SmokeTests(DeskCase):
    def test_f2_catalogue_class_and_effect_override_prefixes(self):
        expected = {'clock.sntp_offset': 'pass', 'instrument.binary_identity_rederived': 'pass',
                    'env.member_quiet_state_violated': 'physics',
                    'calibration.capture_battery_span': 'physics', 'meter.absent': 'pass',
                    'clock.rate': 'physics'}
        for code, status in expected.items():
            with self.subTest(code=code):
                self.assertEqual(s.classify(stages_ok=True, driver_exit=0, harvest_exit=0,
                                           acceptance_result=AcceptanceResult('ACCEPT', (), (), False),
                                           flags=[code]), status)

    def test_f2_unreadable_catalogue_uses_prefixes_and_hook_wins(self):
        with mock.patch.object(s, 'CATALOG_PATH', self.root / 'missing-catalogue.json'):
            _, physical = s._harvest_hooks()
            self.assertTrue(physical('clock.sntp_offset'))
            self.assertFalse(physical('env.member_quiet_state_violated'))
        self.assertEqual(s.classify(stages_ok=True, driver_exit=0, harvest_exit=0,
                                   acceptance_result=AcceptanceResult('ACCEPT', (), (), False),
                                   flags=['clock.rate'], is_physical=lambda code: False), 'pass')

    def test_f3_installed_acceptance_dependency_error_propagates(self):
        name = 'joulewise.b6.acceptance'

        class BrokenAcceptance(importlib.abc.MetaPathFinder, importlib.abc.Loader):
            def find_spec(self, fullname, path=None, target=None):
                if fullname == name:
                    return importlib.util.spec_from_loader(fullname, self)

            def create_module(self, spec):
                return None

            def exec_module(self, module):
                raise ModuleNotFoundError("No module named 'scipy'", name='scipy')

        with mock.patch.dict(sys.modules), mock.patch.object(sys, 'meta_path', [BrokenAcceptance(), *sys.meta_path]):
            sys.modules.pop(name, None)
            for load in (ai.load_acceptance, s._harvest_hooks):
                with self.subTest(load=load.__name__):
                    with self.assertRaises(ModuleNotFoundError) as caught:
                        load()
                    self.assertEqual(caught.exception.name, 'scipy')

    def test_f3_absent_module_and_optional_hooks(self):
        with mock.patch('importlib.util.find_spec', return_value=None):
            self.assertIsInstance(ai.load_acceptance(), StubAcceptance)
            loader, physical = s._harvest_hooks()
            self.assertIsNone(loader)
            self.assertTrue(physical('clock.rate'))
        module = SimpleNamespace(ACCEPTANCE=FakeAcceptance())
        with mock.patch('importlib.util.find_spec', return_value=object()), \
                mock.patch.dict(sys.modules, {'joulewise.b6.acceptance': module}):
            self.assertIs(ai.load_acceptance(), module.ACCEPTANCE)
            loader, physical = s._harvest_hooks()
            self.assertIsNone(loader)
            self.assertFalse(physical('clock.sntp_offset'))
            module.is_physical = lambda code: code == 'custom.physical'
            module.evidence_from_archive = lambda archive: archive
            self.assertEqual(s._harvest_hooks(), (module.evidence_from_archive, module.is_physical))

    def test_f9c_bare_strings_must_be_flag_codes(self):
        record = {'verdict': 'GO', 'reasons': ['REFUSED', 'clock.rate', 'a free-text reason',
                                             'Clock.rate', 'clock.rate trailing'],
                  'arm': {'verdict': 'REFUSED', 'flags': ['battery.float', 'module_1.arm_refusal']}}
        self.assertEqual(list(s._flag_codes(record)), ['clock.rate', 'battery.float', 'module_1.arm_refusal'])

    def test_17_exact_reduced_graphs_and_gamma_member_order(self):
        keeps = json.loads(s.KEEP_PATH.read_text())
        expected_science = {
            'alpha': ['alpha-reference-start', 'alpha-science-absolute',
                      'alpha-science-prefill-p2048-absolute', 'alpha-reference-end'],
            'beta': ['beta-reference-start', 'beta-science-absolute',
                     'beta-science-prefill-p2048-absolute', 'beta-reference-end'],
            'gamma': ['gamma-reference-start', 'gamma-science-01-decode-contrast-blocks-01-05',
                      'gamma-science-03-prefill-p2048-contrast-blocks-01-05', 'gamma-reference-end']}
        for pack, count in (('alpha', 4), ('beta', 4), ('gamma', 6)):
            original = tree(pack)
            saved = copy.deepcopy(original)
            reduced = s.reduce_tree(original, keeps[PACKS[pack]])
            self.assertEqual(original, saved)
            graph = reduced['stage_graph']
            captures = ([f'{pack}-calibration-pre', f'{pack}-calibration-post'] if pack == 'gamma'
                        else [f'{pack}-pre-calibration', f'{pack}-post-calibration'])
            expected = [f'{pack}-bracket-reservation', captures[0], *expected_science[pack], captures[1],
                        f'{pack}-whole-window-verdict', f'{pack}-backup']
            self.assertEqual([row['stage_id'] for row in graph], expected)
            self.assertEqual([row['ordinal'] for row in graph], list(range(1, len(graph)+1)))
            self.assertEqual(sum(row['expected_count'] for row in graph if row['kind']=='campaign_collection'), count)
            for i, row in enumerate(graph):
                self.assertEqual(row['predecessor'], expected[i-1] if i else None)
                self.assertEqual(row['successor'], expected[i+1] if i+1 < len(graph) else None)
                self.assertNotIn('spare_retry', row)
                self.assertNotEqual(row['kind'], 'bound_derivation')
            chain.stage_plan(reduced)
            del reduced['smoke_reduction']
            with self.assertRaises(chain.ChainRenderError):
                chain.stage_plan(reduced)
        for dispatch in plan.resolve_stage_dispatches(tree('gamma'), ROOT):
            if dispatch.stage_id not in expected_science['gamma'][1:3]:
                continue
            manifest = json.loads((ROOT / dispatch.config_dir / 'order_manifest.json').read_text())
            first, second = manifest['executed_order'][:2]
            self.assertTrue(first['run_id'].endswith('-b01-a1'))
            self.assertTrue(second['run_id'].endswith('-b01-b1'))
            for entry, model in ((first, 'Qwen3-1.7B'), (second, 'Qwen3-8B')):
                config = json.loads((ROOT / dispatch.config_dir / entry['config']).read_text())
                self.assertIn(model, config['model']['source'])

    def test_18_reduction_errors(self):
        original = tree('alpha')
        for keep in ({'unknown': 1}, {'alpha-science-absolute': 11}):
            with self.assertRaises(s.SmokePrepareError):
                s.reduce_tree(original, keep)
        changed = copy.deepcopy(original)
        collections = [row for row in changed['stage_graph'] if row['kind'] == 'campaign_collection']
        s._arguments(collections[1])[0]['value'] = s._arguments(collections[0])[0]['value']
        with self.assertRaises(s.SmokePrepareError):
            s.reduce_tree(changed, {collections[0]['stage_id']: 1, collections[1]['stage_id']: 2})

    def claim(self):
        measurement, state, _ = synthetic_checkout(self.root)
        pin = measurement / plan.HEAD_PIN_RELATIVE
        pin.parent.mkdir(parents=True)
        pin.write_text(json.dumps(fake_window.GENESIS_PIN))
        # Only synthetic files are committed; this is never a JouleWise clone.
        init_git_fixture(measurement, '-q')
        s._git(measurement, 'config', '--local', 'user.name', 'fixture')
        s._git(measurement, 'config', '--local', 'user.email', 'fixture@invalid')
        s._git(measurement, 'config', '--local', 'commit.gpgsign', 'false')
        runbook = measurement / chain.RUNBOOK_RELATIVE
        runbook.parent.mkdir(parents=True)
        runbook.write_text((ROOT / chain.RUNBOOK_RELATIVE).read_text())
        sizing = measurement / fake_window.FIXTURE_SIZING_RELATIVE
        sizing.parent.mkdir(parents=True)
        sizing.write_text(json.dumps(fake_window.FIXTURE_SIZING))
        # A small committed sizing file, with both allowances resolved by the
        # real plan writer, replaces every measurement-dependent source.
        allowance_file = measurement / 'configs/sizing/synthetic.json'
        allowance_file.write_text(json.dumps({'span': 3600, 'stream': 335}))
        pack_root = measurement / 'configs/campaigns' / PACKS['alpha']
        (pack_root / 'calibration_plan.json').write_text('{}')
        s._git(measurement, 'add', 'configs', 'docs')
        s._git(measurement, 'commit', '-qm', 'synthetic')
        commit = s._git(measurement, 'rev-parse', 'HEAD')
        inputs = fake_window.inputs(self.root, measurement, 'alpha', plan_id='synthetic', t0_epoch_s=1800000000)
        for name, pointer in (('programmed_span_s', '/span'), ('T_stream_max_s', '/stream')):
            inputs[name] = {'seconds': 3600 if name == 'programmed_span_s' else 335,
                            'source': {'path': 'configs/sizing/synthetic.json', 'sha256': s._sha256(allowance_file)},
                            'source_pointer': pointer}
        return measurement, state, commit, inputs

    def test_19_ledger_copy_guards_and_plan_binding(self):
        claim, state, commit, inputs = self.claim()
        source = claim / plan.DEFAULT_LEDGER_RELATIVE
        original = s._sha256(source)
        with mock.patch('joulewise.b5.plan.ledger_head_status', return_value={'blocking': []}):
            def writer(value):
                return plan.write_window_plan(value, pack_digest=lambda path: 'e'*64,
                                              threshold_defaults=fake_window.threshold_defaults)
            prepared = s.prepare(PACKS['alpha'], commit, claim, self.root / 'smokes', plan_inputs=inputs,
                                 state_root=state, fp=fp(), plan_writer=writer,
                                 wrapper_writer=lambda *args, **kwargs: None,
                                 now=dt.datetime(2026, 10, 14, tzinfo=dt.timezone.utc))
        target = prepared.measurement / plan.DEFAULT_LEDGER_RELATIVE
        self.assertEqual(s._sha256(source), original)
        self.assertNotEqual(source.stat().st_ino, target.stat().st_ino)
        record = json.loads(prepared.plan_path.read_text())
        self.assertEqual(record['hazard_window']['bindings']['ledger_path'], str(target))
        environment = (prepared.custody / 'window.env').read_text()
        self.assertIn('CALIBRATION_LEDGER=' + str(target), environment)
        self.assertNotIn(str(source), json.dumps(record))
        self.assertTrue(record['plan_id'].startswith('SMOKE-'))
        self.assertEqual(record['hazard_window']['settle_s'], chain.SETTLE_S)
        self.assertEqual(s._git(prepared.measurement, 'remote'), '')
        self.assertEqual(s.driver_argv(prepared)[2:4], ['run', '--plan'])
        with self.assertRaises(s.SmokePrepareError):
            s.copy_ledger(claim, self.root / 'outside', prepared.smoke_dir)
        with self.assertRaises(s.SmokePrepareError):
            s.copy_ledger(claim, claim, self.root)
        inside = self.root / 'isolation'
        inside.mkdir()
        clone = inside / 'measurement'
        copy2 = s.shutil.copy2
        def changed_source(src, dest):
            copied = copy2(src, dest)
            Path(src).write_bytes(b'changed while copying')
            return copied
        with mock.patch.object(s.shutil, 'copy2', side_effect=changed_source), self.assertRaises(s.SmokePrepareError):
            s.copy_ledger(claim, clone, inside)

    def test_20_wrapper_and_executable_member_interposition(self):
        wrapper = s.wrapper_text('/synthetic/.venv/bin/python3.13', self.root / 'runner.py', {'configs/stage': 2},
                                 self.root / 'reduction.jsonl')
        for forbidden in ('PYTHONPATH', 'sitecustomize', 'JW_REHR_', 'PATH='):
            self.assertNotIn(forbidden, wrapper)
            self.assertNotIn(forbidden, s.REDUCED_RUNNER)
        ordered = [Path(f'{i}.json') for i in range(20)]
        self.assertEqual(s.reduce_ordered(ordered, 'configs/stage', {'configs/stage': 2}), ordered[:2])
        self.assertEqual(s.reduce_ordered(ordered, 'unmapped', {'configs/stage': 2}), ordered)
        # Execute the generated runner over a synthetic run_campaign module;
        # original ordering must run before truncation, with no other override.
        root = self.root / 'runner-checkout'
        scripts = root / 'scripts'
        scripts.mkdir(parents=True)
        # The generated runner imports its helper from the clone. This fixture
        # supplies only that module, without cloning the real repository.
        package = root / 'joulewise/b6'
        package.mkdir(parents=True)
        (package.parent / '__init__.py').write_text('')
        (package / '__init__.py').write_text('')
        import inspect
        (package / 'smoke.py').write_text('import json\nfrom pathlib import Path\n' + inspect.getsource(s.reduce_ordered))
        config = root / 'configs/stage'
        config.mkdir(parents=True)
        campaign = scripts / 'run_campaign.py'
        campaign.write_text('''import json, sys
from pathlib import Path
def apply_order_manifest(configs, order_entries):
    return list(reversed(configs))
def main():
    directory = Path(sys.argv[1])
    ordered = apply_order_manifest([directory / f"{i}.json" for i in range(20)], [])
    print(json.dumps([p.name for p in ordered]))
    return 0
''')
        runner = self.root / 'runner.py'
        runner.write_text(s.REDUCED_RUNNER)
        import os
        import sys
        environment = {**os.environ, 'JW_B6_SMOKE_KEEP': json.dumps({'configs/stage': 2}),
                       'JW_B6_SMOKE_REDUCTION_LOG': str(self.root / 'reduction.jsonl')}
        result = subprocess.run([sys.executable, str(runner), str(campaign), str(config)],
                                env=environment, check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout), ['19.json', '18.json'])
        environment['JW_B6_SMOKE_KEEP'] = '{}'
        result = subprocess.run([sys.executable, str(runner), str(campaign), str(config)],
                                env=environment, check=True, capture_output=True, text=True)
        self.assertEqual(len(json.loads(result.stdout)), 20)

    def test_21_synthetic_clone_has_no_origin(self):
        source = self.root / 'source'
        source.mkdir()
        init_git_fixture(source, '-q')
        (source / 'synthetic.txt').write_text('synthetic\n')
        s._git(source, 'add', 'synthetic.txt')
        s._git(source, '-c', 'user.name=fixture', '-c', 'user.email=fixture@invalid',
               '-c', 'commit.gpgsign=false', 'commit', '-qm', 'synthetic')
        commit = s._git(source, 'rev-parse', 'HEAD')
        destination = self.root / 'clone'
        s.clone_checkout(source, commit, destination)
        self.assertEqual(s._git(destination, 'remote'), '')
        self.assertEqual(s._git(destination, 'rev-parse', 'HEAD'), commit)

    def test_22_desk_pass_physics_fail_and_index(self):
        for name, driver, harvest, a, flags, expected in (
                ('pass', 0, 0, FakeAcceptance(), [], 'pass'),
                ('courier', 6, 0, FakeAcceptance(), [], 'pass'),
                ('implicit', None, 0, FakeAcceptance(), [], 'pass'),
                ('physics', 0, 0, FakeAcceptance(flags=('battery.member_span',)), [], 'physics'),
                ('archive-physics', 0, 0, FakeAcceptance(), [], 'physics'),
                ('harvest', 0, 1, FakeAcceptance(), [], 'fail'),
                ('structural', 0, 0, FakeAcceptance(structural=True), [], 'fail'),
                ('arm', 1, 0, FakeAcceptance(), [{'code': 'battery.float'}], 'physics'),
                ('stage', 1, 0, FakeAcceptance(), [], 'fail')):
            base = self.root / name
            measurement = base / 'measurement'
            pack = measurement / 'configs/campaigns' / PACKS['alpha']
            pack.mkdir(parents=True)
            reduced = s.reduce_tree(tree('alpha'), json.loads(s.KEEP_PATH.read_text())[PACKS['alpha']])
            (pack / 'plan_tree.json').write_text(json.dumps(reduced))
            night = base / 'custody/night'
            night.mkdir(parents=True)
            journal = [{'stage_id': st.stage_id, 'rc': 0 if name != 'stage' else 99}
                       for st in chain.stage_plan(reduced) if st.in_chain]
            (night / chain.STAGE_JOURNAL).write_text(''.join(json.dumps(row)+'\n' for row in journal))
            (night / 'hazard_result.json').write_text(json.dumps({'flags': flags}))
            if name == 'implicit':
                (night / 'result.json').write_text(json.dumps({'verdict': 'GO', 'chain_exit_code': 0}))
                (night / 'courier.json').write_text(json.dumps({'sent': True}))
            if name == 'archive-physics':
                derived = base / 'archive/derived'
                derived.mkdir(parents=True)
                (derived / 'window_flags.json').write_text(json.dumps({'flags': {'by_code': {'battery.member_span': 1}}}))
            prepared = s.SmokePrepared(base, measurement, base / 'plan.json', base / 'custody',
                                       base / 'state', PACKS['alpha'], 'SMOKE-test-calibration', fp(), {}, pack)
            pin_calls = []
            report = s.desk(prepared, driver_exit=driver, run=lambda *args, **kwargs: SimpleNamespace(returncode=harvest),
                            advance_pin=lambda *args, **kwargs: pin_calls.append(kwargs), acceptance=a,
                            evidence_loader=lambda archive: SessionEvidence(PACKS['alpha'], (), (), {}, False, ()))
            self.assertEqual(report['status'], expected)
            self.assertEqual(len(pin_calls), 1)
            index = base / 'state/smoke-passes.jsonl'
            self.assertEqual(index.exists(), expected == 'pass')
            if index.exists():
                self.assertEqual(len(index.read_text().splitlines()), 1)
            if driver == 6:
                self.assertEqual(report['driver_reason'], 'courier_failed_but_collected')

    def test_desk_acceptance_uses_session_pack_roster_with_alpha_registration(self):
        from joulewise.b5.harvest import build_roster, l4_exclusion_inputs
        from joulewise.b6.acceptance import ACCEPTANCE
        from joulewise.b6.precheck import synthetic_session

        registration = support.registration_dir(self.root / 'cross-pack')
        document = support.document()
        document['pack_id'] = PACKS['alpha']
        support.write_json(registration / 'acceptance.json', document)
        rows = [{'sequence': i, 'disposition': 'valid', 'exact_bound_lexeme_s': '0.028'}
                for i in range(1, 25)]
        for pack in ('beta', 'gamma'):
            with self.subTest(pack=pack):
                base = self.root / pack
                night = base / 'custody/night'
                night.mkdir(parents=True)
                journal = [{'stage_id': stage.stage_id, 'rc': 0}
                           for stage in chain.stage_plan(tree(pack)) if stage.in_chain]
                (night / chain.STAGE_JOURNAL).write_text(''.join(json.dumps(row) + '\n' for row in journal))
                pack_root = ROOT / 'configs/campaigns' / PACKS[pack]
                prepared = s.SmokePrepared(base, ROOT, base / 'plan.json', base / 'custody',
                    base / 'state', PACKS[pack], 'SMOKE-test-calibration',
                    {**fp(PACKS[pack]), 'repo_root': str(ROOT)}, {}, registration)
                evidence = synthetic_session(pack_root, ROOT, rows, {})
                acceptance = mock.Mock(wraps=ACCEPTANCE)
                report = s.desk(prepared, driver_exit=0,
                    run=lambda *args, **kwargs: SimpleNamespace(returncode=0),
                    advance_pin=lambda *args, **kwargs: None, acceptance=acceptance,
                    evidence_loader=lambda archive: evidence)
                self.assertEqual(report['acceptance']['verdict'], 'ACCEPT')
                self.assertEqual(report['status'], 'pass')
                acceptance.prepare.assert_called_once()
                self.assertEqual(acceptance.prepare.call_args.kwargs['pack_root'], pack_root)
                prepared_a = acceptance.evaluate.call_args.args[0]
                expected, _ = l4_exclusion_inputs(build_roster(pack_root, ROOT), {}, plan_id=None, attempt=None)
                self.assertEqual(prepared_a.roster, expected)
                self.assertTrue(prepared_a.roster['cells'])
