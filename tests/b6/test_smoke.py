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
        self.assertIn(str(prepared.measurement / 'scripts/b6_courier.sh'),
                      (prepared.smoke_dir / 'bin/smoke-courier').read_text())
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

    def production_prepared(self):
        import shutil
        seed, state, _, inputs = self.claim()
        # A full checkout retains every production script, sidecar and pack
        # inventory. Only the synthetic ledger/pin and sizing inputs are seeded.
        claim = self.root / 'production-checkout'
        s.clone_checkout(ROOT, s._git(ROOT, 'rev-parse', 'HEAD'), claim)
        for relative in (plan.DEFAULT_LEDGER_RELATIVE, plan.HEAD_PIN_RELATIVE,
                         'configs/sizing/synthetic.json'):
            destination = claim / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(seed / relative, destination)
        s._git(claim, 'add', plan.HEAD_PIN_RELATIVE, 'configs/sizing/synthetic.json')
        s._git(claim, 'commit', '-qm', 'synthetic ledger and sizing')
        commit = s._git(claim, 'rev-parse', 'HEAD')
        (claim / '.venv/lib/python3.13/site-packages').mkdir(parents=True)
        return s.prepare(PACKS['alpha'], commit, claim, self.root / 'smokes',
            plan_inputs=inputs, fp=fp(), state_root=state,
            plan_writer=lambda value: plan.write_window_plan(value,
                threshold_defaults=fake_window.threshold_defaults),
            wrapper_writer=lambda *a, **kw: s.write_wrapper(*a, **kw, python=sys.executable))

    def test_prepare_authenticates_production_tree_and_controller_pre_slot(self):
        from joulewise import arm_readiness, controller
        prepared = self.production_prepared()
        site, = (prepared.measurement / '.venv/lib').glob('python*/site-packages')
        self.assertTrue((prepared.measurement / '.venv/bin' / site.parent.name).is_file())
        # Operational startup bound: the same 5 s scheduling floor used by
        # the partial-reader probe, with no sampler or workload involved.
        interpreter = subprocess.run([str(prepared.measurement / '.venv/bin/python'),
            '-c', 'import sys; print(sys.prefix)'], capture_output=True, text=True, timeout=5)
        self.assertEqual(interpreter.returncode, 0, interpreter.stderr)
        self.assertEqual(Path(interpreter.stdout.strip()), prepared.measurement / '.venv')
        pack = prepared.measurement / 'configs/campaigns' / PACKS['alpha']
        reduced, raw = arm_readiness._plan_tree(pack)
        self.assertEqual(sum(r['expected_count'] for r in reduced['stage_graph']
                             if r['kind'] == 'campaign_collection'), 4)
        self.assertEqual(s._git(prepared.measurement, 'status', '--porcelain', '--',
                                str(pack.relative_to(prepared.measurement))), '')
        for sidecar in pack.glob('*.sha256'):
            digest, name = sidecar.read_text().strip().split('  ')
            self.assertEqual(digest, s._sha256(pack / name))
        record = json.loads(prepared.plan_path.read_text())
        self.assertEqual(record['hazard_window']['pack']['plan_tree_sha256'],
                         hashlib.sha256(raw).hexdigest())
        self.assertEqual(record['hazard_window']['pack']['pack_sha256'],
                         arm_readiness.committed_pack_tree_sha256(pack))
        # Only the earlier launch-locator seam is supplied. The controller must
        # authenticate the real reduced bytes before reaching the hardware's
        # finalized calibration slot (which this Linux fixture cannot collect).
        context = {'pack_root': str(pack), 'launch_lineage': {'bracket_session_id': 'synthetic'}}
        class ReachedLedger(Exception):
            pass
        with (mock.patch.object(arm_readiness, 'authenticate_campaign_launch_lineage', return_value=context),
              mock.patch.object(controller, '_writer_launch_lineage', return_value={}),
              mock.patch('joulewise.calibration_ledger.calibration_session_status', side_effect=ReachedLedger)):
            with self.assertRaises(ReachedLedger):
                controller._authenticate_g2b_pre_slot_attachment(self.root, {}, None, self.root,
                                                                object(), hazard=object())

    def test_stage_crash_dominates_injected_physics_with_or_without_bundles(self):
        # Smoke acceptance also calls an incidental member exclusion a
        # physics_stop. Only physical_stop_kind identifies an actual stop.
        for produced in (False, True):
            for record in ({}, {'physics_stop': True, 'physical_stop_kind': None}):
                with self.subTest(record=record, bundles_produced=produced):
                    self.assertEqual(s.classify(stages_ok=False, driver_exit=1, harvest_exit=0,
                        acceptance_result=AcceptanceResult('EXCLUDE', (), (), False, record=record),
                        flags=['agent.presence'], bundles_produced=produced), 'fail')
        self.assertEqual(s.classify(stages_ok=False, driver_exit=1, harvest_exit=0,
            acceptance_result=AcceptanceResult('EXCLUDE', (), (), False,
                record={'physics_stop': True, 'physical_stop_kind': 'disk'}), flags=[]), 'physics')

    def test_report_collection_uses_production_smoke_dispatch_not_full_harvest_roster(self):
        # Adapted from the review's production_roster_report.py replay: keep
        # smoke.prepare's real reduced plan and all real order manifests.
        from joulewise.b5 import harvest
        from joulewise.flags.catalog import load_catalog
        from joulewise.flags.exclusions import compute
        from joulewise.flags.schema import make_flag, make_scope, make_source
        from scripts import b6_machine_test as mt
        from tests.test_b6_machine_test import put, append, clock_row
        prepared = self.production_prepared()
        pack = prepared.measurement / 'configs/campaigns' / prepared.pack_id
        reduced = json.loads((pack / 'plan_tree.json').read_text())
        counts = {row['stage_id']: row['expected_count'] for row in reduced['stage_graph']
                  if row['kind'] == 'campaign_collection'}
        ids = [run_id for dispatch in plan.resolve_stage_dispatches(reduced, prepared.measurement)
               for run_id in dispatch.run_ids[:counts[dispatch.stage_id]]]
        self.assertEqual(len(ids), 4)
        reference, cap, prefill, last = ids
        archive = prepared.smoke_dir / 'archive'
        at = lambda second: {'monotonic_ns': second * 10**9, 'wall_s': 1800000000 + second}
        episode = {'start': at(1), 'end': at(40), 'since': at(20), 'last_sighting': at(20),
                   'pause_end': at(620), 'pause_s': 600}
        put(prepared.custody / 'night/result.json', {'verdict': 'GO', 'chain_exit_code': 0})
        put(prepared.custody / 'night/hazard_result.json', {'chain': {'exit_code': 0},
            'agent_pause': {'episodes': [episode], 'stopped_by_limit': False}})
        # Replay's fixture clocks: the pause ends before the cap run; later
        # stages use the same fixture member spans plus the real settle gap.
        for run_id, start, end in ((reference, 1, 50), (cap, 621, 2121),
                                  (prefill, 2121 + chain.SETTLE_S, 2199 + chain.SETTLE_S),
                                  (last, 2199 + 2 * chain.SETTLE_S, 2248 + 2 * chain.SETTLE_S)):
            for event, second in (('start', start), ('end', end)):
                append(prepared.custody / 'collection/run_clock.jsonl', clock_row(event, run_id, second))
        catalog = load_catalog(s.CATALOG_PATH)
        flags = []
        for code, run_id in (('agent.presence', None), ('agent.presence_overlap', reference),
                             ('idle.wait_cap_skip', cap)):
            entry = catalog.entry(code)
            flags.append(make_flag(code=code, family=entry['family'], klass=entry['klass'],
                scope=make_scope('member' if run_id else 'window', run_id=run_id),
                source=make_source('window', 'b6-machine-test'),
                interval={'monotonic_ns': [10**9, 40 * 10**9], 'monotonic_raw_ns': None,
                          'wall_s': [1800000001, 1800000040]} if run_id is None else None))
            append(archive / 'derived/flags.jsonl', flags[-1])
        for run_id in ids:
            put(archive / 'sources/claim-runs' / run_id / 'summary_metrics.json',
                {'status': 'failed' if run_id == cap else 'succeeded'})
        put(archive / 'sources/claim-runs' / cap / 'metadata.json',
            {'environment_admission': {'skip_reason': 'wait_cap_reached'}})
        put(prepared.smoke_dir / 'smoke-result.json',
            {'status': 'physics', 'errors': [], 'harvest_exit': 0, 'archive': str(archive)})
        state_path = prepared.smoke_dir / 'machine-test.json'
        put(state_path, {'smoke_state': str(prepared.smoke_dir / 'smoke-state.json'),
                         'out': str(prepared.smoke_dir)})
        spans = {start['run_id']: {'member': [start['clock']['monotonic_ns'], end['clock']['monotonic_ns']]}
                 for start, end in mt.agent_pause.paired_run_clocks(
                     mt.read_rows(prepared.custody / 'collection/run_clock.jsonl'))}
        roster, l4spans = harvest.l4_exclusion_inputs(harvest.build_roster(pack, prepared.measurement),
                                                    spans, plan_id=None, attempt=None)
        self.assertEqual(len(roster['members']), 125)
        for full in (False, True):
            with self.subTest(full_harvest_roster=full):
                selected = roster if full else {**roster, 'members': [
                    member for member in roster['members'] if member['run_id'] in ids]}
                effects = compute(flags, selected, l4spans, catalog)
                put(archive / 'derived/exclusions.json', effects)
                item = next(item for item in mt.report(state_path)['items'] if item['item'] == 'collection ran')
                excluded = {row['run_id'] for row in effects['members_excluded']}
                self.assertEqual(len(excluded - set(ids)), 121 if full else 0)
                self.assertEqual(item['detail']['actual_exclusions'], sorted(excluded))
                self.assertTrue(item['observed'], 'unselected harvest members must not fail the smoke collection check')
                if full:
                    self.assertEqual(item['detail']['exclusion_detail'], effects['members_excluded'])

    def desk_exit_case(self, name, *, stage_crash=False, harvest=0, code='agent.presence',
                       bundles=True, stop=None, arm=False, acceptance_record=True):
        # Real desk/journal/archive path from desk_crash.py; only harvest and
        # pin advancement are injected. No process or physical probe is run.
        from tests.test_b6_machine_test import put, append
        base = self.root / name
        measurement = base / 'measurement'
        reduced = s.reduce_tree(tree('alpha'), json.loads(s.KEEP_PATH.read_text())[PACKS['alpha']])
        put(measurement / 'configs/campaigns' / PACKS['alpha'] / 'plan_tree.json', reduced)
        night = base / 'custody/night'
        stages = [stage for stage in chain.stage_plan(reduced) if stage.in_chain]
        for stage in stages:
            if arm:
                break  # An arm refusal never launches the chain.
            # Two prior bundles remain when the next collection crashes.
            crash = stage_crash and (not bundles or stage.stage_id == 'alpha-science-prefill-p2048-absolute')
            append(night / chain.STAGE_JOURNAL, {'stage_id': stage.stage_id, 'rc': 1 if crash else 0})
            if crash:
                break
        put(night / 'hazard_result.json', {'flags': [{'code': code}],
            **({'chain': {'exit_code': 1, 'stop_reason': 'night_stopped_disk_low'}} if stop else {}),
            **({'arm': {'go': False, 'verdicts': {'battery': {'status': 'REFUSE'}}}} if arm else {})})
        archive = base / 'archive'
        append(archive / 'derived/flags.jsonl', {'code': code})
        if acceptance_record:
            record = {'verdict': 'EXCLUDE', 'flag_counts': {code: 1},
                'physics_stop': True, 'physical_stop_kind': None, 'excluding': [{'code': code, 'scope': 'member'}]}
            if stop:
                # Derive the named disk stop using the real acceptance rule,
                # with no captures or members, rather than inventing a label.
                from joulewise.b6.acceptance import ACCEPTANCE
                evidence = SessionEvidence(PACKS['alpha'], (), (), {'_b6': {'smoke': True}}, False, (),
                                           stop_reason='night_stopped_disk_low')
                record = ACCEPTANCE.evaluate(support.prepared(base / 'acceptance'), evidence).record
                self.assertEqual(record['physical_stop_kind'], stop)
            put(archive / 'derived/b6-acceptance.json', record)
        if bundles:
            for run_id in ('earlier-reference', 'earlier-science'):
                put(archive / 'sources/claim-runs' / run_id / 'metadata.json',
                    {'run_id': run_id, 'status': 'succeeded'})
        self.assertEqual(len(list((archive / 'sources/claim-runs').glob('*/metadata.json'))),
                         2 if bundles else 0)
        prepared = s.SmokePrepared(base, measurement, base / 'plan.json', base / 'custody',
            base / 'state', PACKS['alpha'], 'SMOKE-test-calibration', fp(), {}, base / 'registration')
        return s.desk(prepared, driver_exit=1 if stage_crash or arm else 0,
            advance_pin=lambda *a, **kw: None, run=lambda *a, **kw: SimpleNamespace(returncode=harvest))

    def test_desk_crash_after_two_bundles_is_not_explained_by_incidental_physics(self):
        for code in ('agent.presence', 'thermal.os_level_nonzero'):
            with self.subTest(code=code):
                result = self.desk_exit_case(code, stage_crash=True, code=code)
                self.assertEqual(result['errors'], [])
                self.assertIsNone(result['acceptance']['record']['physical_stop_kind'])
                self.assertEqual(result['status'], 'fail')

    def test_desk_idle_loss_requires_exact_dispatch_records_and_campaign_exit(self):
        from joulewise.b6 import acceptance
        from tests.test_b6_machine_test import put, append

        for case in ('cap', 'budget', 'mixed', 'reason_absent', 'flag_absent',
                     'budget_reason_absent', 'budget_flag_absent', 'budget_wrong_reason', 'cap_wrong_reason',
                     'wrong_member', 'wrong_dispatch', 'other_exit', 'other_crash', 'missing_dispatch'):
            with self.subTest(case=case):
                base = self.root / case
                measurement = base / 'measurement'
                archive = base / 'archive'
                reduced = s.reduce_tree(tree('alpha'), json.loads(s.KEEP_PATH.read_text())[PACKS['alpha']])
                cap_stage = 'alpha-science-absolute'
                if case == 'mixed':
                    next(st for st in reduced['stage_graph'] if st['stage_id'] == cap_stage)['expected_count'] = 2
                    reduced['smoke_reduction']['keep'][cap_stage] = 2
                pack_rel = Path('configs/campaigns') / PACKS['alpha']
                put(measurement / pack_rel / 'plan_tree.json', reduced)
                put(archive / 'sources/repo' / pack_rel / 'plan_tree.json', reduced)
                # Use exactly the manifests launched by the reduced campaign,
                # including the runner's run-id sanitization.
                for dispatch in plan.resolve_stage_dispatches(reduced, ROOT):
                    manifest = json.loads((ROOT / dispatch.config_dir / 'order_manifest.json').read_text())
                    put(measurement / dispatch.config_dir / 'order_manifest.json', manifest)
                dispatches = plan.resolve_stage_dispatches(reduced, measurement)
                cap_id = next(d.run_ids[0] for d in dispatches if d.stage_id == cap_stage)
                if case == 'wrong_dispatch':
                    cap_id = next(d.run_ids[1] for d in dispatches if d.stage_id == cap_stage)
                members = []
                skips = []
                for dispatch in dispatches:
                    selected = (dispatch.run_ids[:2] if case == 'mixed' else (cap_id,)
                                ) if dispatch.stage_id == cap_stage else dispatch.run_ids[:1]
                    for rid in selected:
                        members.append({'run_id': rid, 'stage_id': dispatch.stage_id})
                        bundle = archive / 'sources/claim-runs' / rid
                        skipped = dispatch.stage_id == cap_stage
                        status = 'failed' if skipped else 'succeeded'
                        budget = case.startswith('budget') or (case == 'mixed' and rid != cap_id)
                        skip_code = 'idle.wait_budget_skip' if budget else 'idle.wait_cap_skip'
                        reason = 'wait_budget_exhausted' if budget else 'wait_cap_reached'
                        if case.endswith('wrong_reason'):
                            reason = 'wait_cap_reached' if budget else 'wait_budget_exhausted'
                        if skipped:
                            skips.append((rid, skip_code))
                        put(bundle / 'summary_metrics.json', {'status': status})
                        put(bundle / 'status.json', {'status': status})
                        put(bundle / 'metadata.json', {'environment_admission': {
                            'skip_reason': reason if skipped and not case.endswith('reason_absent') else None}})
                        if not skipped:
                            (bundle / 'raw').mkdir()
                            (bundle / 'raw/powermetrics.plist').write_bytes(b'fixture measured record')
                put(archive / 'derived/roster.json', {'pack_id': PACKS['alpha'], 'members': members})
                catalog = support.prepared(base / 'acceptance').catalog
                for rid, skip_code in skips:
                    flag_id = 'undispatched' if case == 'wrong_member' else rid
                    if not case.endswith('flag_absent'):
                        append(archive / 'derived/flags.jsonl', acceptance._flag(skip_code, catalog, run_id=flag_id))
                    append(archive / 'derived/flags.jsonl', acceptance._flag('member.bytes_missing', catalog,
                        run_id=rid, observed={'files_missing': ['raw/powermetrics.plist']}))
                self.assertFalse((archive / 'sources/claim-runs' / cap_id / 'raw/powermetrics.plist').exists())
                night = base / 'custody/night'
                for stage in chain.stage_plan(reduced):
                    if stage.in_chain:
                        rc = 1 if stage.stage_id == cap_stage else 0
                        if case == 'other_exit' and stage.stage_id == cap_stage:
                            rc = 2
                        if case == 'other_crash' and stage.stage_id == 'alpha-science-prefill-p2048-absolute':
                            rc = 1
                        append(night / chain.STAGE_JOURNAL, {'stage_id': stage.stage_id, 'rc': rc})
                put(archive / 'derived/b6-acceptance.json', {'verdict': 'EXCLUDE', 'flag_counts': {code: 1 for _, code in skips},
                    'physics_stop': True, 'physical_stop_kind': None, 'excluding': []})
                put(base / 'plan.json', {'pack_id': PACKS['alpha'], 'chain_exit_code': 0})
                if case == 'missing_dispatch':
                    manifest = measurement / next(d.config_dir for d in dispatches if d.stage_id == cap_stage) / 'order_manifest.json'
                    manifest.unlink()
                prepared = s.SmokePrepared(base, measurement, base / 'plan.json', base / 'custody',
                    base / 'state', PACKS['alpha'], 'SMOKE-test', fp(), {}, base / 'registration')
                result = s.desk(prepared, driver_exit=0, advance_pin=lambda *a, **kw: None,
                                run=lambda *a, **kw: SimpleNamespace(returncode=0))
                self.assertEqual(result['errors'], [])
                self.assertEqual(result['status'], 'physics' if case in ('cap', 'budget', 'mixed') else 'fail')

    def test_structural_acceptance_is_not_excused_by_incidental_physics(self):
        result = AcceptanceResult('EXCLUDE', ('structure.missing_stage_bundles',), (), True,
                                  record={'physics_stop': True})
        self.assertEqual(s.classify(stages_ok=True, driver_exit=0, harvest_exit=0,
                                   acceptance_result=result, flags=['idle.wait_cap_skip']), 'fail')

    def test_desk_nonzero_harvest_is_not_explained_by_incidental_physics(self):
        # Harvest faults (queue.outcome: any exit but 0 and 6); 6 is registration pending.
        for harvest in (1, 2):
            with self.subTest(harvest=harvest):
                result = self.desk_exit_case(str(harvest), harvest=harvest)
                self.assertTrue(all(row['rc'] in row['success_exit_codes'] for row in result['stages']))
                self.assertEqual(result['status'], 'fail')

    def test_harvest_exit_six_is_registration_pending_not_a_fault(self):
        # Delta review N3: exit 6 passes clean stages and does not rescue a failed stage.
        clean = AcceptanceResult('UNAVAILABLE', ('precheck.acceptance_unavailable',),
                                 ('precheck.acceptance_unavailable',), False, record={})
        self.assertEqual(s.classify(stages_ok=True, driver_exit=0, harvest_exit=6,
                                    acceptance_result=clean, flags=[]), 'pass')
        self.assertEqual(s.classify(stages_ok=False, driver_exit=1, harvest_exit=6,
                                    acceptance_result=clean, flags=['agent.presence']), 'fail')

    def test_pending_registration_record_keeps_a_physical_chain_stop(self):
        # Delta review M2: with no acceptance.json the UNAVAILABLE record still names
        # the chain's physical stop, so classify keeps it physics.
        from joulewise.b6 import session
        base = self.root / 'pending-stop'
        (base / 'registration').mkdir(parents=True)
        evidence = SimpleNamespace(pack_id=PACKS['alpha'], stop_reason='night_stopped_disk_low')
        with mock.patch.object(session, 'bindings', return_value={}), \
                mock.patch.object(session, 'evidence_from_archive', return_value=evidence), \
                mock.patch.object(session, '_write_result'):
            result, _ = session.accept_archive(base / 'archive', {'plan_id': 'p'}, base / 'registration',
                                               smoke=True)
        self.assertEqual(result.verdict, 'UNAVAILABLE')
        self.assertEqual(result.record['physical_stop_kind'], 'disk')
        self.assertEqual(s.classify(stages_ok=False, driver_exit=1, harvest_exit=6, acceptance_result=result,
                                    flags=['disk.low']), 'physics')

    def test_desk_named_physical_failures_and_missing_acceptance_controls(self):
        for name, options, expected in (
                ('disk', {'stop': 'disk', 'code': 'disk.low', 'bundles': False, 'stage_crash': True}, 'physics'),
                ('battery', {'arm': True, 'code': 'battery.float', 'stage_crash': True, 'bundles': False}, 'physics'),
                ('missing-acceptance', {'stop': 'disk', 'code': 'disk.low', 'bundles': False, 'stage_crash': True,
                                        'acceptance_record': False}, 'fail')):
            with self.subTest(name=name):
                result = self.desk_exit_case(name, **options)
                self.assertEqual(result['status'], expected)
                self.assertEqual(bool(result['errors']), name == 'missing-acceptance')

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
                ('arm-battery', 1, 0, FakeAcceptance(), [], 'physics'),
                ('stage', 1, 0, FakeAcceptance(), [], 'fail'),
                ('stage-physics', 1, 0, FakeAcceptance(), [{'code': 'agent.presence'}], 'fail')):
            base = self.root / name
            measurement = base / 'measurement'
            pack = measurement / 'configs/campaigns' / PACKS['alpha']
            pack.mkdir(parents=True)
            reduced = s.reduce_tree(tree('alpha'), json.loads(s.KEEP_PATH.read_text())[PACKS['alpha']])
            (pack / 'plan_tree.json').write_text(json.dumps(reduced))
            night = base / 'custody/night'
            night.mkdir(parents=True)
            journal = [{'stage_id': st.stage_id, 'rc': 99 if name in ('stage', 'stage-physics', 'arm-battery') else 0}
                       for st in chain.stage_plan(reduced) if st.in_chain]
            (night / chain.STAGE_JOURNAL).write_text(''.join(json.dumps(row)+'\n' for row in journal))
            (night / 'hazard_result.json').write_text(json.dumps({'flags': flags,
                **({'arm': {'go': False, 'verdicts': {'battery': {'status': 'REFUSE'}}}}
                   if name == 'arm-battery' else {})}))
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
