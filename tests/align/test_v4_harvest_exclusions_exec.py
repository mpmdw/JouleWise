"""RL-65: execute the shared harvest on controller-written synthetic W1 bundles.

No native MLX, model download, measurement or custody is used. WP22 supplies
the fake native stream and hardware world; the kit, adapter prepare, controller,
member assessment, model-identity collector and exclusions code remain real.
The missing calibrated scaffold is deliberate and is reported, never a pass.
"""
from __future__ import annotations

import contextlib
from copy import deepcopy
from dataclasses import replace
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from tests.align import synthetic_custody
from joulewise.b5 import harvest as h
from joulewise.b6 import registration
from joulewise.b6.acceptance import evidence_from_archive
from joulewise.identity_pins import derive_model_runtime_config_from_metadata
from scripts import align_v4_kit as kit
from scripts import align_v4_w1_synthetic as dry
from scripts import bytes_h_session

ROOT = Path(__file__).resolve().parents[2]
SCIENCE_IDS = ([f'align-pilot-v3-episodes-a-e{i:02}' for i in range(1, 5)]
               + [f'align-v4-episodes-a-e{i:02}' for i in range(5, 10)]
               + [f'align-v4-episodes-b-e{i:02}' for i in range(10, 19)])
SCIENCE_CODES = ['battery.unmeasured', 'contention.unmeasured',
                 'member.anchor_recompute_mismatch', 'member.bytes_missing',
                 'member.strict_validation_failed']
# Actual auxiliary order in the view's harvest roster, not an inferred count.
MISSING_AUXILIARIES = [
    'neg8-refcorpus-r01', 'neg8-window-end-r1', 'neg8-window-midpoint', 'neg8-window-start-r1',
    'neg8-refcorpus-r02', 'neg8-window-end-r2', 'neg8-window-start-r2',
    'neg8-refcorpus-r03', 'neg8-window-end-r3', 'neg8-window-start-r3',
    *[f'neg8-refcorpus-r{i:02}' for i in range(4, 19)],
]


def setUpModule():
    synthetic_custody.setUpModule()


def tearDownModule():
    synthetic_custody.tearDownModule()


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + '\n')


def session(root):
    """WP22's full roster, with an explicitly synthetic terminal/plan envelope."""
    out = root / 'w1'
    out.mkdir()
    args = SimpleNamespace(leak=.004, variant='kit', inject='none', members='all')
    with contextlib.redirect_stdout(io.StringIO()):
        results, _world = dry.collect(args, out)
    plan, _configs, files = dry.build_kit(results['inputs'], results['r1_slots'])
    source_root = root / 'source'
    for relative, raw in files.items():
        target = source_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    pack = source_root / kit.KIT
    tree = json.loads((pack / 'plan_tree.json').read_bytes())
    # The ONLY config substitutions are WP22's local synthetic model and task.
    # Preserve the kit graph, rows, roles, auxiliary roster and empty attachments.
    for row in tree['science']:
        raw = (out / 'runs' / row['run_id'] / 'config.json').read_bytes()
        (source_root / row['config_path']).write_bytes(raw)
        row['config_sha256'] = hashlib.sha256(raw).hexdigest()
    for directory in (pack / 'stages').iterdir():
        manifest_path = directory / 'order_manifest.json'
        manifest = json.loads(manifest_path.read_bytes())
        for member in manifest['executed_order']:
            member['config_sha256'] = hashlib.sha256((directory / member['config']).read_bytes()).hexdigest()
        put(manifest_path, manifest)
    put(pack / 'plan_tree.json', tree)
    # Reuse the ACTUAL desk measurement-view builder. The kit's source tree
    # intentionally has external-input placeholders; the view expands them.
    # Its input checkout is synthetic and contains no runs or custody links.
    for relative in ('configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json',
                     'configs/campaigns/bytes_v1/roster.json'):
        target = source_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    put(source_root / bytes_h_session.plan.HEAD_PIN_RELATIVE, {'sequence': 0, 'head_digest': '0' * 64})
    for dispatch in bytes_h_session.plan.resolve_stage_dispatches(tree, ROOT):
        if dispatch.config_dir and not (source_root / dispatch.config_dir).exists():
            shutil.copytree(ROOT / dispatch.config_dir, source_root / dispatch.config_dir)
    for row in h.pinned_files(tree, pack_root=pack, repo_root=source_root):
        target = source_root / row['path']
        if not target.exists():
            source = ROOT / row['path']
            if source.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
    view_session = root / 'view-session'
    view_session.mkdir()
    measurement, pack = bytes_h_session.measurement_view(
        source_root, view_session, kit=kit.KIT, pack_id=kit.PACK_ID)
    custody = root / 'custody'
    put(custody / 'night/chain.started', {'pgid': 12345, 'monotonic_ns': 0})
    put(custody / 'night/chain.exited', {'exit_code': 0})
    put(custody / 'night/result.json', {'verdict': 'GO', 'chain_exit_code': 0})
    # No acceptance.json exists in v4's registration directory. Use exactly the
    # desk CLI's fallback, without changing the catalog or its effects.
    directory = pack / 'registration'
    try:
        reg = registration.load(directory)
    except (OSError, ValueError):
        reg = None
    catalog = ROOT / (reg or registration.DEFAULTS)['catalog']
    # Synthetic local paths close every ledger/capture locator before harvest.
    plan_path = root / 'plan.json'
    put(plan_path, dict(plan_id='synthetic-v4-W1', attempt=1,
        custody_root=str(custody), measurement_root=str(measurement),
        pack_root=str(pack), pack_id=kit.PACK_ID, claim_runs_root=str(out / 'runs'),
        ledger_path=str(root / 'absent-ledger.jsonl'),
        head_pin_path=str(root / 'absent-pin.json'),
        acceptance_path=str(root / 'absent-acceptance.json'),
        hazard_window={'bindings': {'capture_screen': {}},
                       'harvest_thresholds': dict(battery_limit_ma=200,
            battery_unmeasured_gap_s=120, battery_accumulator_watts_per_unit=.001,
            thermal_unmeasured_gap_s=15, contention_cpu_s_per_s=.05,
            clock_step_ns=1000000, clock_unmeasured_gap_s=5,
            disk_low_bytes=10737418240, clock_systematic_min_recorded=5)}))
    inputs = h.resolve_inputs(plan_path, overrides={
        'catalog_path': catalog, 'identity_pins_path': directory / 'identity_pins.json'})
    return inputs, results, plan


def execute(inputs, archive):
    assessments = {}
    original = h.assess_member

    def observe(task):
        result = original(task)
        assessments[result['run_id']] = deepcopy(result)
        return result

    seams = h.Seams(group_alive=lambda _: False, workers=1, io_workers=1)
    with mock.patch.object(h, 'assess_member', side_effect=observe):
        record = h.harvest(inputs, archive, seams=seams, prepare_desk=False,
            registration_paths=[inputs.identity_pins_path])
    return dict(record=record, assessments=assessments,
        exclusions=json.loads((archive / 'derived/exclusions.json').read_bytes()),
        window=json.loads((archive / 'derived/window_flags.json').read_bytes()),
        errors=json.loads((archive / 'withheld/collector-errors.json').read_bytes()))


class SyntheticW1HarvestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='rl65-', dir=os.path.realpath(tempfile.gettempdir()))
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name)
        cls.inputs, cls.results, cls.plan = session(cls.root)
        cls.clean = execute(cls.inputs, cls.root / 'archive')
        print('RL65_EXECUTION ' + json.dumps({
            'record': cls.clean['record'], 'catalog': cls.clean['window']['catalog'],
            'exclusions': cls.clean['exclusions'], 'errors': cls.clean['errors'],
            'identities': {k: {'status': v.get('status'), 'identity': v.get('identity'),
                               'errors': v.get('errors')} for k, v in cls.clean['assessments'].items()},
        }, sort_keys=True), flush=True)

    def test_ACTUAL_synthetic_w1_identity_derives_but_missing_physics_excludes(self):
        self.assertEqual(len(self.results['members']), 18)
        self.assertEqual(len(self.clean['assessments']), 18)
        self.assertEqual([m['run_id'] for m in self.results['members']], SCIENCE_IDS)
        self.assertEqual(self.clean['record']['verdict'], 'HARVEST_FAULT')
        self.assertEqual(self.clean['record']['faults'], [{'collector': 'lineage'}])
        self.assertEqual([e['detail'] for e in self.clean['errors']['errors']], ['bound_runs_root_unresolved'])
        self.assertEqual(self.clean['window']['catalog'], dict(
            path=str(ROOT / 'configs/b6/flag_catalog_b6.json'),
            sha256='01767fe4e75ed961798f4e6b68cf055a5b3946a474129e93d2b5e7c239a1dd0c'))
        self.assertEqual(self.clean['exclusions']['reasons'], ['cell.below_minimum'])
        self.assertEqual(self.clean['record']['exclude_window_reasons'], ['cell.below_minimum', 'harvest.fault'])
        self.assertEqual([{k: item[k] for k in ('run_id', 'codes')}
                          for item in self.clean['exclusions']['members_excluded']],
            [dict(run_id=rid, codes=SCIENCE_CODES) for rid in SCIENCE_IDS]
            + [dict(run_id=rid, codes=['member.bytes_missing']) for rid in MISSING_AUXILIARIES])
        for row in self.results['members']:
            with self.subTest(run_id=row['run_id']):
                result = self.clean['assessments'][row['run_id']]
                self.assertEqual(result['status'], 'succeeded')
                self.assertIsInstance(result.get('identity'), dict)
                bundle = Path(row['bundle'])
                metadata = json.loads((bundle / 'metadata.json').read_bytes())
                config = json.loads((bundle / 'config.json').read_bytes())
                recorded = metadata['adapters']['runtime']['prepare_metadata']['model_artifact_identity']
                self.assertEqual(recorded, metadata['workload_provenance']['model']['artifact_identity'])
                self.assertEqual(result['identity']['model_artifact_sha256'], recorded['folded_sha256'])
                triple = derive_model_runtime_config_from_metadata(config, metadata)[1]
                self.assertEqual(result['identity'], {k: triple[k] for k in (
                    'model_artifact_sha256', 'runtime_identity_sha256')})
        self.assertFalse(any('model.identity_underivable' in row['codes']
                             for row in self.clean['exclusions']['members_excluded']))

    def test_one_removed_recorded_identity_is_underivable(self):
        row = self.results['members'][4]
        bundle = self.root / 'negative' / row['run_id']
        shutil.copytree(row['bundle'], bundle)
        metadata = json.loads((bundle / 'metadata.json').read_bytes())
        del metadata['adapters']['runtime']['prepare_metadata']['model_artifact_identity']
        put(bundle / 'metadata.json', metadata)
        prepare_only = h.assess_member(dict(run_id=row['run_id'], bundle_path=str(bundle),
            withheld_dir=str(self.root / 'negative-prepare-withheld'), block_six=True))
        self.assertEqual(prepare_only['identity'], self.clean['assessments'][row['run_id']]['identity'])
        del metadata['workload_provenance']['model']['artifact_identity']
        put(bundle / 'metadata.json', metadata)
        changed = h.assess_member(dict(run_id=row['run_id'], bundle_path=str(bundle),
            withheld_dir=str(self.root / 'negative-withheld'), block_six=True))
        self.assertIsNone(changed['identity'])
        self.assertIn('identity', changed['errors'])
        # Isolate the real model_identity collector and real catalog/exclusion
        # engine from the deliberately absent physics evidence in the full run.
        run = h._Harvest(self.inputs, self.root / 'negative-identity-archive',
                         h.Seams(), prepare_desk=False, run_g3=False)
        run.pack_copy = self.inputs.pack_root
        run.repo_root_copy = self.inputs.measurement_root
        run.roster = h.build_roster(run.pack_copy, run.repo_root_copy)
        run.members = deepcopy(self.clean['assessments'])
        pin_copy = run.archive / 'sources/inputs/identity_pins.json'
        pin_copy.parent.mkdir(parents=True)
        shutil.copyfile(self.inputs.identity_pins_path, pin_copy)
        roster = {'plan_id': self.inputs.plan_id, 'attempt': 1, 'members': [
            {'run_id': m['run_id'], 'units': []} for m in self.results['members']], 'cells': []}
        run.model_identity()
        control = h._l4_exclusions(run.flags.records, roster, {}, run.catalog, pack_scoped=False)
        self.assertEqual(control['members_excluded'], [])
        run.members[row['run_id']] = changed
        run.model_identity()
        self.assertEqual([f['scope']['run_id'] for f in run.flags.records
                          if f['code'] == 'model.identity_underivable'], [row['run_id']])
        excluded = h._l4_exclusions(run.flags.records, roster, {}, run.catalog, pack_scoped=False)
        self.assertEqual([{k: item[k] for k in ('run_id', 'codes')}
                          for item in excluded['members_excluded']], [
            {'run_id': row['run_id'], 'codes': ['model.identity_underivable']}])
        # Also traverse the complete harvest orchestration on a temporary
        # session copy. Removing its model_identity step must fail this test.
        full_copy = self.root / 'negative-all-runs'
        shutil.copytree(self.inputs.claim_runs_root, full_copy)
        put(full_copy / row['run_id'] / 'metadata.json', metadata)
        actual = execute(replace(self.inputs, claim_runs_root=full_copy),
                         self.root / 'negative-full-archive')
        expected = [{k: item[k] for k in ('run_id', 'codes')}
                    for item in self.clean['exclusions']['members_excluded']]
        for item in expected:
            if item['run_id'] == row['run_id']:
                item['codes'] = sorted([*item['codes'], 'model.identity_underivable'])
        self.assertEqual([{k: item[k] for k in ('run_id', 'codes')}
                          for item in actual['exclusions']['members_excluded']], expected)
        self.assertEqual([rid for rid, result in actual['assessments'].items()
                          if result.get('identity') is None], [row['run_id']])
        print('RL65_NEGATIVE ' + json.dumps(dict(
            run_id=row['run_id'], identity=actual['assessments'][row['run_id']]['identity'],
            members_with_underivable=[m for m in actual['exclusions']['members_excluded']
                                     if 'model.identity_underivable' in m['codes']]), sort_keys=True), flush=True)


class TerminalGenerationTests(unittest.TestCase):
    def test_real_evidence_reader_handles_main_and_w1_and_unknown_exits(self):
        # Main's GO is an arm verdict. W1 adds a fault reason and a delivery
        # receipt. Neither addition changes what the actual exit means.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for generation in ('main', 'w1'):
                for code, expected in ((0, 'completed'), (3, 'chain_crashed'),
                                       (917, 'chain_crashed'), (None, 'chain_crashed')):
                    with self.subTest(generation=generation, exit_code=code):
                        archive = root / generation / str(code)
                        plan = dict(pack_id=kit.PACK_ID, custody_root=str(archive),
                            plan_tree={'science': [], 'stage_graph': [],
                                       'external_inputs': {'manifests': []}})
                        record = dict(verdict='GO', chain_exit_code=code)
                        if generation == 'w1':
                            record['fault_reasons'] = ([f'chain_exit_nonzero:{code}']
                                                       if code not in (0, None) else [])
                            put(archive / 'night/courier.delivery.json', {'status': 'delivered'})
                        put(archive / 'night/result.json', record)
                        observed = evidence_from_archive(archive, plan, archive / 'registration')
                        self.assertEqual(observed.stop_reason, expected)


if __name__ == '__main__':
    unittest.main()
