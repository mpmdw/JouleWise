"""Stage-1 integration seams: the pre-session check and the smoke desk call the
harvest lane's real acceptance (block-6 design 3.3: one acceptance function A,
used by the harvest, the smoke desk and the pre-check).

Synthetic data only: the real ALPHA plan tree and its committed configs, a
synthetic model file, a synthetic acceptance registration, fake hardware seams.
"""
import json
import shutil
from pathlib import Path
from unittest import mock

from joulewise.b6 import fingerprint, precheck as p, smoke
from joulewise.b6.acceptance_interface import AcceptanceResult
from joulewise.b6.registration import DEFAULT_DIR_RELATIVE
from tests.b6.support import DeskCase, ROOT, PACKS, document, fp, synthetic_checkout, fake_environment, write_json


class PrecheckRealAcceptanceTests(DeskCase):
    def setUp(self):
        super().setUp()
        self.measurement, self.state, self.model = synthetic_checkout(self.root)
        # A measurement checkout is a full clone: the acceptance reads the
        # block-6 catalog and the reviewed-commits list from it.
        for relative in ("configs/b6/flag_catalog_b6.json", "configs/b6/executing_reviews.json"):
            target = self.measurement / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        fingerprint.record_pass(fp(), self.root, self.state / 'smoke-passes.jsonl')

    def run_precheck(self):
        ctx, seams, _ = fake_environment(self.measurement)
        return p.run_precheck(PACKS['alpha'], self.measurement, self.state, ctx=ctx, seams=seams)

    def test_registration_directory_is_the_shared_one(self):
        self.assertEqual(p.REGISTRATION_RELATIVE, DEFAULT_DIR_RELATIVE)

    def test_missing_acceptance_registration_is_a_flag_not_a_crash(self):
        result = self.run_precheck()
        self.assertEqual(result['acceptance']['status'], 'unavailable')
        self.assertIn('precheck.acceptance_unavailable', [f['code'] for f in result['predicted_flags']])
        self.assertIsNone(result['certain_exclusion'])
        self.assertEqual(p.decision(result), 'START')

    def write_registration(self):
        registration = self.measurement / DEFAULT_DIR_RELATIVE
        reg = document()
        reg.update(pack_id=PACKS['alpha'], registered_commit=fp()['code_commit'])
        write_json(registration / 'acceptance.json', reg)
        return registration

    def test_empty_ledger_is_a_certain_exclusion_by_the_real_acceptance(self):
        # No valid capture anywhere: the bracket cannot be formed, which the
        # registered analysis would exclude; the precheck says so before t0.
        self.write_registration()
        result = self.run_precheck()
        self.assertEqual(result['acceptance']['status'], 'available', result['acceptance'])
        self.assertIn('precheck.no_valid_capture', [f['code'] for f in result['predicted_flags']])
        self.assertEqual(result['certain_exclusion']['reasons'], ['calibration.bracket_incomplete'])
        self.assertEqual(p.decision(result), 'DO_NOT_START')

    def test_full_alpha_session_on_a_production_shaped_ledger_starts(self):
        # The precheck's own nominal evidence (all 125 ALPHA runs succeed,
        # captures at the median of the last 24 valid ledger rows) through the
        # harvest lane's acceptance, with the margin case of 8 lost runs.
        from joulewise.b6.acceptance import ACCEPTANCE
        registration = self.write_registration()
        rows = [{'sequence': i, 'disposition': 'valid', 'exact_bound_lexeme_s': '0.028'} for i in range(1, 31)]
        pack_root = self.measurement / 'configs/campaigns' / PACKS['alpha']
        evidence = p.synthetic_session(pack_root, self.measurement, rows,
                                       {'model_hashes': {}, 'runtime_versions': {}})
        self.assertEqual(sum(len(stage.members) for stage in evidence.stages), 125)
        prepared = ACCEPTANCE.prepare(ledger_path=self.measurement / 'runs/calibration_observation_ledger.jsonl',
                                      plan_tree=json.loads((pack_root / 'plan_tree.json').read_text()),
                                      registration_dir=registration,
                                      code_identity={**fp(), 'repo_root': str(self.measurement),
                                                     'executed_head': fp()['code_commit']})
        acceptance, margin, exclusion, flags = p.acceptance_checks(ACCEPTANCE, prepared, evidence)
        nominal = acceptance['nominal']
        self.assertEqual(nominal['verdict'], 'ACCEPT', nominal['reasons'])
        self.assertIsNone(exclusion)
        # Design 3.3's margin case (8 lost runs clustered in one stage) removes a
        # 10-unit stratum below its 5-unit minimum: a thin margin, which starts
        # anyway and is written in the notice; it is never a certain exclusion.
        self.assertEqual(margin['placements'], 10)
        self.assertIn(margin['status'], ('ok', 'thin'))
        self.assertNotIn('catalog.code_unclassified', set(nominal['flags']))
        self.assertNotIn('model.files_differ_from_registered', set(nominal['flags']))


class SmokeDeskRoutingTests(DeskCase):
    def prepared(self):
        smoke_dir = self.root / 'smoke'
        measurement = smoke_dir / 'measurement'
        pack_root = measurement / 'configs/campaigns' / PACKS['alpha']
        pack_root.mkdir(parents=True)
        shutil.copyfile(ROOT / 'configs/campaigns' / PACKS['alpha'] / 'plan_tree.json', pack_root / 'plan_tree.json')
        plan_path = smoke_dir / 'custody/night_plan.json'
        (smoke_dir / 'custody/night').mkdir(parents=True)
        plan_path.write_text(json.dumps({'plan_id': 'SMOKE-test'}))
        return smoke.SmokePrepared(smoke_dir, measurement, plan_path, smoke_dir / 'custody', self.root / 'state',
                                   PACKS['alpha'], 'SMOKE-test-calibration', fp(), {}, self.root / 'registration')

    def test_desk_uses_the_session_acceptance_in_smoke_mode(self):
        prepared = self.prepared()
        calls = []

        def harvest(argv, **kwargs):
            calls.append(argv)
            write_json(prepared.smoke_dir / 'archive/derived/b6-acceptance.json', {
                'verdict': 'ACCEPT', 'counting': True, 'flag_counts': {}, 'excluding': []})
            return mock.Mock(returncode=0)

        report = smoke.desk(prepared, driver_exit=0, run=harvest, advance_pin=lambda *a, **k: None)
        self.assertEqual(len(calls), 1)
        argv = calls[0]
        self.assertTrue(argv[1].endswith('scripts/harvest_b6_session.py'))
        self.assertIn('--smoke', argv)
        self.assertNotIn('--prepare-desk', argv)
        self.assertEqual(argv[argv.index('--registration-dir') + 1], str(prepared.registration_dir))
        self.assertEqual(report['acceptance']['verdict'], 'ACCEPT')
        self.assertEqual(report['errors'], [])

    def test_smoke_catalog_is_the_block_six_catalog(self):
        self.assertEqual(smoke.CATALOG_PATH, ROOT / 'configs/b6/flag_catalog_b6.json')
        # The driver's collection codes are physical in the block-6 catalog.
        for code in ('agent.presence', 'idle.wait_cap_skip', 'sleep.in_run'):
            self.assertTrue(smoke._is_physical(code), code)
        self.assertFalse(smoke._is_physical('idle.waited'))

    def test_stored_smoke_judgment_keeps_number_exclusions_physics_and_pending_distinct(self):
        from joulewise.b5 import chain
        prepared = self.prepared()
        path = prepared.measurement / 'configs/campaigns' / PACKS['alpha'] / 'plan_tree.json'
        reduced = smoke.reduce_tree(json.loads(path.read_text()), smoke.compose.registered_smoke_keep(PACKS['alpha']))
        path.write_text(json.dumps(reduced))
        journal = prepared.custody / 'night' / chain.STAGE_JOURNAL
        journal.write_text(''.join(json.dumps({'stage_id': stage.stage_id, 'rc': 0}) + '\n'
                                   for stage in chain.stage_plan(reduced) if stage.in_chain))
        for rc, code, expected in ((0, None, 'pass'), (0, 'model.stack_differs_from_registered', 'fail'),
                                    (0, 'calibration.operative_bound_above_stop', 'physics'),
                                    (6, 'precheck.acceptance_unavailable', 'pass')):
            def harvest(argv, **kwargs):
                write_json(prepared.smoke_dir / 'archive/derived/b6-acceptance.json', {
                    'mode': 'smoke', 'verdict': 'UNAVAILABLE' if rc == 6 else 'EXCLUDE' if code else 'ACCEPT',
                    'counting': code is None, 'flag_counts': {code: 1} if code else {},
                    'excluding': [{'code': code, 'scope': 'window'}] if code and rc == 0 else []})
                return mock.Mock(returncode=rc)
            with self.subTest(code=code):
                report = smoke.desk(prepared, driver_exit=0, run=harvest, advance_pin=lambda *a, **k: None)
                self.assertEqual(report['status'], expected)
