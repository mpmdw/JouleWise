import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.quiet_kit import analysis, readers
from joulewise.quiet_kit.paths import atomic_json, read_json
from joulewise.quiet_kit.runner import Runner
from joulewise.quiet_kit.schedule import BY_ID
from .fakes import FakeHardware

REPO = Path(__file__).resolve().parents[2]


class CompletenessTests(unittest.TestCase):
    def test_every_analysis_declares_incomplete_on_empty_observations(self):
        for name, fn in analysis.FUNCTIONS.items():
            with self.subTest(test_id=name):
                self.assertTrue(fn({})['incomplete_reason'])

    def test_m1_minimum_bounded_counts_and_missing_data_retained(self):
        captures = [{'id': f'{condition}-{i}', 'condition': condition,
                     'bound_s': .03 if i < bounded else None}
                    for condition, count, bounded in [('quiet', 10, 8), ('load', 4, 3), ('utility', 4, 3)]
                    for i in range(count)]
        self.assertIsNone(analysis.m1({'captures': captures})['incomplete_reason'])
        for condition in ('quiet', 'load'):
            bad = copy.deepcopy(captures)
            next(c for c in bad if c['condition'] == condition)['bound_s'] = None
            out = analysis.m1({'captures': bad})
            self.assertEqual(out['incomplete_reason'], 'captures_unbounded')
            self.assertEqual(sum(c['capture_count'] for c in out['conditions'].values()), 18)
        for capture in captures:
            if capture['condition'] == 'utility': capture['bound_s'] = None
        self.assertIsNone(analysis.m1({'captures': captures})['incomplete_reason'])

    def test_m13_many_meter_edges_cannot_hide_failed_sampler_captures(self):
        edges = [{'capture': f'capture-{i//118}', 'command_s': i,
                  'meter_s': i+.012, 'sampler_s': None} for i in range(354)]
        out = analysis.m13({'edges': edges})
        self.assertEqual(out['meter_edge_count'], 354)
        self.assertIsNotNone(out['meter_lag_mean']['value'])
        self.assertIsNone(out['sampler_lag_mean']['value'])
        self.assertTrue(out['incomplete_reason'])
        edges[0]['sampler_s'] = .02
        self.assertTrue(analysis.m13({'edges': edges})['incomplete_reason'])
        edges[118]['sampler_s'] = 118.02
        self.assertIsNone(analysis.m13({'edges': edges})['incomplete_reason'])
        for i, edge in enumerate(edges):
            edge['meter_s'] = edge['meter_s'] if i < 99 else None
        self.assertTrue(analysis.m13({'edges': edges})['incomplete_reason'])
        edges[99]['meter_s'] = 99.012
        self.assertIsNone(analysis.m13({'edges': edges})['incomplete_reason'])

    def test_m2_missing_quad_or_phase_cannot_be_complete(self):
        runs = [{'id': f'{q}-{i}', 'quad': q, 'arm': arm,
                 'phase_energy_j': {'prefill': 10., 'decode': 20.}}
                for q in range(5) for i, arm in enumerate('NLLN')]
        self.assertIsNone(analysis.m2({'runs': runs})['incomplete_reason'])
        for mutate in ('missing_run', 'missing_phase', 'failed_run'):
            bad = copy.deepcopy(runs)
            if mutate == 'missing_run': bad.pop()
            if mutate == 'missing_phase': del bad[0]['phase_energy_j']['decode']
            if mutate == 'failed_run': bad[0]['failure_reasons'] = [{'reason': 'failed'}]
            self.assertEqual(analysis.m2({'runs': bad})['incomplete_reason'], 'five_complete_quads_required')
        for run in runs: del run['phase_energy_j']['decode']
        self.assertTrue(analysis.m2({'runs': runs})['incomplete_reason'])

    def test_runner_retries_undefined_m1_m13_m2_and_keeps_both_attempts(self):
        for test_id in ('m1-capture-stop-line', 'm13-meter-edges', 'm2-long-wait'):
            with self.subTest(test_id=test_id), tempfile.TemporaryDirectory(prefix='quiet-kit-incomplete-') as tmp:
                root = Path(tmp)
                hw = FakeHardware()
                def collect(plan, attempt, scale, control, kind):
                    hw.collected.append(plan.test_id)
                    atomic_json(attempt/'collection.json', {'kind': kind, 'test_id': test_id})
                    (attempt/'kept.raw').write_bytes(b'undefined measurement still retained\n')
                seams = hw.seams()
                seams.collect = collect
                # Meter presence alone cannot rescue an undefined timing result.
                data = {'meter_present': True, 'segments': [], 'runs': [], 'captures': []}
                with patch.object(readers, 'read_attempt', return_value=data):
                    runner = Runner(REPO, root, '/fake/model-python', seams,
                        plans=(BY_ID[test_id],), scale=.001, emit=lambda _: None)
                    self.assertEqual(runner.run(), 0)
                self.assertEqual(hw.collected, [test_id, test_id])
                for n in (1, 2):
                    attempt = root/test_id/'attempts'/str(n)
                    self.assertEqual((attempt/'kept.raw').read_bytes(), b'undefined measurement still retained\n')
                    result = read_json(attempt/'analysis.result.json')
                    self.assertFalse(result['complete'])
                    self.assertEqual(result['incomplete_reason'], result['measured']['incomplete_reason'])
                self.assertFalse((root/test_id/'result.json').exists())

    def test_failed_capture_flag_includes_child_reason(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-capture-failure-') as tmp:
            root = Path(tmp)
            cap = root/'capture-000'
            cap.mkdir()
            (cap/'child.stderr').write_text('ValueError: capture trace anchor unresolved: clock_fit_span_insufficient\n')
            row = readers.capture(root, {'id': 'capture-000', 'condition': 'quiet',
                'directory': 'capture-000', 'returncode': 1, 'child_stderr': 'child.stderr'})
            self.assertIsNone(row['bound_s'])
            self.assertIn('clock_fit_span_insufficient', str(row['flags']))
