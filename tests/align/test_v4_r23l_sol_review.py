"""Independent R23l review witnesses; synthetic bytes and no model execution.

The two expected failures record unmet release-loader requirements, not green
qualification. See docs/run_reports/2026-11-08-r23l-sol.md before removing them.
"""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.v4_analysis import analyze, engine
from joulewise.align.v4_analysis.io import (
    bundle_config_bytes, canonical, digest, load, strict_json,
)
from joulewise.align.v4_analysis.synthetic import member_config
from joulewise.bundle import RunBundleWriter
from joulewise.clock import FakeClock
from joulewise.schemas import BenchmarkConfig
from tests.align.test_v4_r23c_engine import native_payload, write_export


def replace_source(root, reference, value):
    data = canonical(value)
    (root / reference['path']).write_bytes(data)
    reference['sha256'] = digest(data)


def replace_desk(root, window, desk):
    replace_source(root, window['residual_source'], desk)
    window['thermal_source'] = copy.deepcopy(window['residual_source'])


class ReleaseReviewTests(unittest.TestCase):
    def test_bundle_normalization_matches_actual_writer_bytes(self):
        from scripts.align_v4_kit import bundle_config_bytes as producer_bytes
        mapping = member_config(engine.roster('C1')[6])
        # Defaults omitted from the kit are materialized by BenchmarkConfig.
        config = BenchmarkConfig.from_mapping(mapping)
        with tempfile.TemporaryDirectory() as tmp:
            with patch('joulewise.bundle._capture_source_state', return_value={}):
                writer = RunBundleWriter.create(Path(tmp), config, FakeClock())
            actual = (writer.path / 'config.json').read_bytes()
        self.assertEqual(actual, bundle_config_bytes(mapping))
        self.assertEqual(actual, producer_bytes(config))

    def test_sabotage_config_with_self_consistent_custody_never_reaches_fit(self):
        p = native_payload()
        target = p['windows'][1]['members'][6]  # C1, benign held-out member
        run = target['slot']['run_id']
        spec = strict_json(target['config']['workload_profile']['prompt_text'])
        spec['condition'] = 'sabotage'
        target['config']['workload_profile']['prompt_text'] = canonical(spec).decode()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_export(root, p)
            loaded = load(path, calibration_only=True)
            with patch.object(engine, '_fit_task', wraps=engine._fit_task) as fits:
                fill, _ = analyze(loaded, workers=1)
        row = fill['windows'][0]['eligibility'][6]
        self.assertFalse(row['eligible'])
        self.assertIn('config_identity_differs:condition', row['reasons'])
        self.assertGreater(fits.call_count, 0)
        for call in fits.call_args_list:
            window, _, _, members = call.args[0]
            if window == 'C1':
                self.assertNotIn(run, [m['slot']['run_id'] for m in members])
        for cutoff in fill['thresholds'].values():
            self.assertNotIn('C1/' + run, cutoff['calibration_members'])
        self.assertTrue(fill['windows'][0]['eligibility'][7]['eligible'])

    def test_invalid_spec_and_samplerless_config_exclude_only_member_on_release(self):
        for invalid_spec in (True, False):
            with self.subTest(invalid_spec=invalid_spec), tempfile.TemporaryDirectory() as tmp:
                p = native_payload()
                profile = p['windows'][1]['members'][6]['config']['workload_profile']
                spec = strict_json(profile['prompt_text'])
                spec.pop('sampler')
                spec['temperature'] = 0
                profile['prompt_text'] = '{' if invalid_spec else canonical(spec).decode()
                path = write_export(Path(tmp), p)
                fill, _ = analyze(load(path, through_window='C1'), workers=1)
                self.assertEqual(fill['windows'][0]['eligibility'][6]['reasons'], ['config_invalid'])
                self.assertFalse(fill['windows'][0]['eligibility'][6]['eligible'])
                self.assertTrue(fill['windows'][0]['eligibility'][7]['eligible'])

    def test_foreign_window_plan_refuses_when_a_distinct_d_member_is_captured(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_export(root, native_payload())
            document = strict_json(path.read_bytes())
            document['windows'][1]['plan_source'] = document['windows'][2]['plan_source']
            with self.assertRaisesRegex(ValueError, 'config_digest_not_planned'):
                load(path, through_window='C1', document=document)

    @unittest.expectedFailure
    def test_foreign_plan_and_kits_must_refuse_even_for_shared_anchors(self):
        p = native_payload()
        for member in p['windows'][1]['members'][4:]:
            member.update(captured=False, summary=None)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_export(root, p)
            document = strict_json(path.read_bytes())
            c1, c2 = document['windows'][1:3]
            # Production reuses these local anchor IDs and kit bytes across
            # windows. Add the real producer's plan-identity field names.
            foreign_ref = c2['plan_source']
            foreign_plan = strict_json((root / foreign_ref['path']).read_bytes())
            foreign_plan.update(schema_version='joulewise.align_v4.series_window.v1',
                                plan_id='align-v4-c2', window_id='C2',
                                series_manifest_sha256=document['series_source']['sha256'])
            replace_source(root, foreign_ref, foreign_plan)
            c1['plan_source'] = copy.deepcopy(foreign_ref)
            desk = strict_json((root / c1['residual_source']['path']).read_bytes())
            foreign_desk = strict_json((root / c2['residual_source']['path']).read_bytes())
            for member, foreign in zip(desk['members'][:4], foreign_desk['members'][:4], strict=True):
                member['planned_config'] = copy.deepcopy(foreign['planned_config'])
            replace_desk(root, c1, desk)
            with self.assertRaisesRegex(ValueError, 'config_digest_not_planned'):
                load(path, through_window='C1', document=document)

    @unittest.expectedFailure
    def test_invalid_benchmark_config_must_exclude_only_its_member_on_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_export(root, native_payload())
            document = strict_json(path.read_bytes())
            window = document['windows'][1]
            desk = strict_json((root / window['residual_source']['path']).read_bytes())
            member = desk['members'][6]
            config = strict_json((root / member['planned_config']['path']).read_bytes())
            config['schema_version'] = 'invalid-synthetic-schema'
            for key in ('config', 'planned_config'):
                replace_source(root, member[key], config)
            plan_ref = window['plan_source']
            plan = strict_json((root / plan_ref['path']).read_bytes())
            plan['members'][6]['config_sha256'] = member['planned_config']['sha256']
            replace_source(root, plan_ref, plan)
            replace_desk(root, window, desk)
            loaded = load(path, through_window='C1', document=document)
            fill, _ = analyze(loaded, workers=1)
        self.assertEqual(fill['windows'][0]['eligibility'][6]['reasons'], ['config_invalid'])
        self.assertFalse(fill['windows'][0]['eligibility'][6]['eligible'])
        self.assertTrue(fill['windows'][0]['eligibility'][7]['eligible'])


if __name__ == '__main__':
    unittest.main()
