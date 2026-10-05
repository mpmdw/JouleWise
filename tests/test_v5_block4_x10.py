"""Ruling 76 addendum E sizing falsifiers; fixture checks, no live gate."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest
from unittest import mock

from joulewise import kernel_clock, night_gate
from scripts import run_night, write_v5_qualification_plan as writer
from tests import test_v5_qualification_plan as fixtures
from tests.test_kernel_clock import frequency_probe


class StageAndStreamSizingTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.SizingTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)

    def test_source_bound_stage_cap_refuses_3179_and_3481(self):
        for cap in (3179, 3481):
            with self.subTest(cap=cap):
                sizing = copy.deepcopy(self.f.sizing)
                sizing['fixed']['t0_stage_cap'] = self.f.allow(cap)
                with self.assertRaisesRegex(writer.QualificationError, 't0_stage_cap_band'):
                    self.f.size(sizing)

    def test_stage_cap_band_edges_change_window_without_charging_span(self):
        span = self.f.size()['programmed_span_s']
        for cap, window in ((3180, 4080), (3480, 4380)):
            sizing = copy.deepcopy(self.f.sizing)
            sizing['fixed']['t0_stage_cap'] = self.f.allow(cap)
            sized = self.f.size(sizing)
            self.assertEqual(sized['programmed_span_s'], span)
            self.assertEqual(sized['t0_stage_cap_s'], cap)
            self.assertEqual(sized['window_max_s'], window)
            self.assertGreaterEqual(window - span, cap)

    def test_each_anchor_bearing_stream_refuses_59_and_accepts_60(self):
        # Science, NEG-8, all reference stages, and both brackets are obligated.
        for stream in self.f.sizing['streams']:
            with self.subTest(stream=stream):
                sizing = copy.deepcopy(self.f.sizing)
                sizing['streams'][stream] = self.f.allow(59)
                with self.assertRaisesRegex(writer.QualificationError, 'anchor_stream_minimum'):
                    self.f.size(sizing)
                sizing['streams'][stream] = self.f.allow(60)
                self.f.size(sizing)

    def test_cooldown_remains_wall_time_and_is_excluded_from_member_stream(self):
        before = self.f.size()
        sizing = copy.deepcopy(self.f.sizing)
        sizing['members']['a1']['cooldown'] = self.f.allow(600)
        after = self.f.size(sizing)
        self.assertEqual(after['programmed_span_s'], before['programmed_span_s'] + 590)
        self.assertEqual(after['longest_sampler_stream_s'], before['longest_sampler_stream_s'])

    def test_unanchored_auxiliary_helper_uses_nonsampling_roster(self):
        sizing = copy.deepcopy(self.f.sizing)
        sizing['auxiliary']['helper'] = self.f.allow(5)
        arguments = dict(roster=self.f.roster, auxiliary=[*self.f.aux, 'helper'], brackets=self.f.brackets)
        writer.size_window('s1', sizing, nonsampling=['helper'], **arguments)
        with self.assertRaisesRegex(writer.QualificationError, 'stream_inventory'):
            writer.size_window('s1', sizing, **arguments)
        sizing['streams']['helper'] = self.f.allow(5)
        with self.assertRaisesRegex(writer.QualificationError, 'anchor_stream_minimum'):
            writer.size_window('s1', sizing, **arguments)

    def production(self, adapter=None):
        if adapter is None:
            adapter = json.loads((writer.REPO_ROOT /
                'configs/campaigns/v5_qualification_25g83/sizing_allowances.json').read_bytes())
        roster, auxiliary, brackets, nonsampling = writer.pack_roster(
            writer.REPO_ROOT / 'configs/campaigns' / writer.GAMMA, 's1')
        return writer.size_window('s1', adapter, roster=roster, auxiliary=auxiliary,
                                  brackets=brackets, nonsampling=nonsampling)

    def test_production_335_seconds_passes_without_charging_separate_cooldown(self):
        sized = self.production()
        self.assertEqual(sized['longest_sampler_stream_s'], 335)
        self.assertEqual(sized['programmed_span_s'], 25434 - 3300 + 360)
        self.assertEqual(sized['programmed_span_s'], 22494)
        self.assertEqual(sized['window_max_s'], 25800)
        self.assertEqual(sized['t0_stage_cap_s'], 3300)
        gate = kernel_clock.frequency_gate(frequency_probe(-207749), sized['longest_sampler_stream_s'])
        self.assertTrue(gate['passes'])
        self.assertAlmostEqual(gate['bound_ms'], 4.84570, places=5)

    def test_source_authenticated_334_second_maximum_is_refused(self):
        adapter = json.loads((writer.REPO_ROOT /
            'configs/campaigns/v5_qualification_25g83/sizing_allowances.json').read_bytes())
        for stream, value in adapter['sizing']['streams'].items():
            if value['seconds'] > 334:
                adapter['sizing']['streams'][stream] = self.f.allow(334)
        # These 334 s replacements have valid source locators: the independent
        # source-bound maximum (335 s) catches the missing sampler custody.
        for sizing in (adapter, adapter['sizing']):
            with self.subTest(adapter='schema_version' in sizing), self.assertRaisesRegex(
                    writer.QualificationError, 'source_stream_maximum_omitted'):
                self.production(sizing)

    def test_production_latest_start_and_three_deadlines_follow_new_window(self):
        sized = self.production()
        for t0, deadman in ((60000., 89700.), (60001., 89760.)):
            plan = night_gate.NightPlan('s1-fixture', 'TRANSACTION_PACK', t0,
                sized['window_max_s'], 0., 'a' * 40, str(self.f.root), 'a' * 40,
                '/chain', '/chain.sha256', str(self.f.root), None)
            bounds = {'latest_chain_start_epoch_s': t0 + 3306,
                      'shutdown_epoch_s': t0 + 26100,
                      'courier_epoch_s': t0 + 26400,
                      'deadman_epoch_s': deadman}
            self.assertEqual(writer.deadlines(plan, sized['programmed_span_s'], bounds), bounds)
            self.assertEqual(run_night.deadman_epoch(plan), deadman)

    def test_prerequisite_boundary_and_capture_share_authenticated_stage_cap(self):
        from joulewise import v5_qualification
        from scripts import capture_t0_step
        fixture = fixtures.PlanWriterTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.write()
        self.assertEqual(writer.prerequisites.call_args.args[3], 1000 - 3300)
        plan = night_gate.NightPlan.from_mapping(writer.read_object(fixture.output))
        inputs = fixture.custody / fixture.pack.name / 'arm_readiness.t0.inputs'
        maximum, _ = v5_qualification.authenticated_clock_budget(inputs, fixture.pack)
        self.assertEqual(maximum, 100.)
        (fixture.custody / 'night').mkdir()
        def complete(argv, **kwargs):
            import subprocess
            self.assertEqual(kwargs['timeout'], 3300)
            for name in capture_t0_step.STEP_FILENAMES.values():
                (inputs / name).write_bytes(b'{}\n')
            return subprocess.CompletedProcess(argv, 0, b'{}', b'')
        with mock.patch.object(run_night, '_chain_environment', return_value={}), \
             mock.patch.object(run_night.t0_rehearsal, 'observed_run', side_effect=complete) as run:
            run_night._capture_qualification_t0(plan)
        run.assert_called_once()


class WindowValidatorTests(unittest.TestCase):
    def setUp(self):
        from dataclasses import replace
        self.replace = replace
        self.f = fixtures.SizingTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.plan = night_gate.NightPlan('gate-fixture', 'TRANSACTION_PACK',
            1000., 4200, 0., 'a' * 40, str(self.f.root), 'a' * 40,
            '/chain', '/chain.sha256', str(self.f.root), None,
            pack_night={'pack_id': 'qualification'})
        self.path = self.f.root / 'qualification/arm_readiness.t0.inputs/kernel-frequency-sizing.json'
        self.path.parent.mkdir(parents=True)

    def chain(self, sizing, *, window=None, marker='s1'):
        from joulewise import arm_readiness as readiness
        window = self.plan.window_max_s if window is None else window
        return (f'export V5_QUALIFICATION_OCCURRENCE={marker}\n'
                'export NIGHT_PROGRAMMED_SPAN_S=860\n'
                f'export NIGHT_LATEST_CHAIN_START_EPOCH_S={1000 + window - 860}\n'
                f'export NIGHT_CLOCK_SIZING_SHA256={readiness.sha256_bytes(readiness.render_json(sizing))}\n')

    def publish(self, sizing):
        from joulewise import arm_readiness as readiness
        self.path.write_bytes(readiness.render_json(sizing))

    def test_initial_and_runtime_validation_use_the_same_authenticated_cap(self):
        for cap, window in ((3180, 4080), (3300, 4200), (3480, 4380)):
            with self.subTest(cap=cap):
                sizing = copy.deepcopy(self.f.sizing)
                sizing['fixed']['t0_stage_cap'] = self.f.allow(cap)
                plan = self.replace(self.plan, window_max_s=window)
                chain = self.chain(sizing, window=window)
                self.assertEqual(night_gate.qualification_start_deadline(
                    plan, chain, 'G2B_SHAKEDOWN', sizing=sizing), 1000 + window - 860)
                self.publish(sizing)
                self.assertEqual(night_gate.qualification_start_deadline(
                    plan, chain, 'G2B_SHAKEDOWN'), 1000 + window - 860)

    def test_cap_is_pinned_to_the_whole_sizing_input(self):
        chain = self.chain(self.f.sizing)
        altered = copy.deepcopy(self.f.sizing)
        altered['fixed']['t0_stage_cap'] = self.f.allow(3480)
        with self.assertRaisesRegex(night_gate.PackNightRefusal, 'sizing sha256 mismatch'):
            night_gate.qualification_start_deadline(self.plan, chain, 'G2B_SHAKEDOWN', sizing=altered)
        self.publish(self.f.sizing)
        self.path.write_bytes(self.path.read_bytes() + b'\n')
        with self.assertRaisesRegex(night_gate.PackNightRefusal, 'qualification_stage_sizing: sha256 mismatch'):
            night_gate.qualification_start_deadline(self.plan, chain, 'G2B_SHAKEDOWN')

    def test_gate_rejects_authenticated_caps_outside_the_band(self):
        for cap in (3179, 3481):
            with self.subTest(cap=cap):
                sizing = copy.deepcopy(self.f.sizing)
                sizing['fixed']['t0_stage_cap'] = self.f.allow(cap)
                with self.assertRaisesRegex(night_gate.PackNightRefusal, 't0_stage_cap_band'):
                    night_gate.qualification_start_deadline(
                        self.plan, self.chain(sizing), 'G2B_SHAKEDOWN', sizing=sizing)

    def test_valid_cap_refuses_the_superseded_2700_second_window(self):
        legacy = self.replace(self.plan, window_max_s=3600)
        with self.assertRaisesRegex(night_gate.PackNightRefusal, 'window/dwell cap'):
            night_gate.qualification_start_deadline(
                legacy, self.chain(self.f.sizing, window=3600), 'G2B_SHAKEDOWN', sizing=self.f.sizing)

    def test_earlier_pack_without_stage_cap_keeps_2700_even_with_irrelevant_bad_pin(self):
        sizing = {'fixed': {'pack_t0': 3300}}
        plan = self.replace(self.plan, window_max_s=3600)
        self.publish(sizing)
        chain = self.chain(sizing, window=3600).replace(
            'export NIGHT_CLOCK_SIZING_SHA256=', 'export UNUSED_SIZING_SHA256=')
        self.assertEqual(night_gate.qualification_start_deadline(plan, chain, 'G2B_SHAKEDOWN'), 3740)
        self.path.write_bytes(b'invalid unrelated legacy JSON\n')
        self.assertEqual(night_gate.qualification_start_deadline(plan, chain, 'G2B_SHAKEDOWN'), 3740)
        with self.assertRaisesRegex(night_gate.PackNightRefusal, 'window/dwell cap'):
            night_gate.qualification_start_deadline(self.plan, chain, 'G2B_SHAKEDOWN')

    def test_other_plan_classes_and_rehearsal_keep_legacy_window(self):
        self.publish(self.f.sizing)
        for receipt_class in ('DIAGNOSTIC_NO_PACK', 'REHEARSAL_STUB'):
            plan = self.replace(self.plan, receipt_class=receipt_class, window_max_s=3600)
            self.assertEqual(night_gate.qualification_start_deadline(
                plan, self.chain(self.f.sizing, window=3600), 'G2B_SHAKEDOWN', sizing=self.f.sizing), 3740)
        plan = self.replace(self.plan, window_max_s=3600)
        self.assertEqual(night_gate.qualification_start_deadline(
            plan, self.chain(self.f.sizing, window=3600, marker='r1'),
            'T0_REHEARSAL', sizing=self.f.sizing), 3740)
        self.assertIsNone(night_gate.qualification_start_deadline(
            self.plan, 'export NIGHT_PROGRAMMED_SPAN_S=860\n', 'G2B_SHAKEDOWN', sizing=self.f.sizing))
        plan = self.replace(plan, pack_night=None)
        self.assertEqual(night_gate.qualification_start_deadline(
            plan, self.chain({}, window=3600), 'G2B_SHAKEDOWN'), 3740)

    def test_runtime_uses_authenticated_bytes_after_detection_not_an_untrusted_preview(self):
        from joulewise import arm_readiness as readiness
        self.publish(self.f.sizing)
        preview = copy.deepcopy(self.f.sizing)
        preview['fixed']['t0_stage_cap'] = self.f.allow(3480)
        preview_bytes = readiness.render_json(preview)
        read = Path.read_bytes
        count = 0
        def changing(path):
            nonlocal count
            if path == self.path:
                count += 1
                if count == 1:
                    return preview_bytes
            return read(path)
        plan = self.replace(self.plan, window_max_s=4380)
        with mock.patch.object(Path, 'read_bytes', changing), self.assertRaisesRegex(
                night_gate.PackNightRefusal, 'window/dwell cap'):
            night_gate.qualification_start_deadline(
                plan, self.chain(self.f.sizing, window=4380), 'G2B_SHAKEDOWN')


if __name__ == '__main__':
    unittest.main()
