"""Bounded M2 waits and whole-quad retries through the production executor."""
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.hazards.base import Completed
from joulewise.quiet_kit import analysis, collectors, readers
from joulewise.quiet_kit.paths import atomic_json, read_json
from joulewise.quiet_kit.runner import Runner
from joulewise.quiet_kit.schedule import BY_ID
from .collector_fakes import CollectorHardware, FakeChild
from .fixtures import ps_bytes

REPO = Path(__file__).resolve().parents[2]


class WaitRetryTests(unittest.TestCase):
    def test_long_wait_caps_total_wait_and_records_achieved_quiet(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-wait-cap-') as tmp:
            attempt = Path(tmp)
            hw = CollectorHardware(scale=1.)
            original = hw.ctx
            def ctx(directory=None):
                out = original(directory)
                out.run = lambda argv, timeout: Completed(tuple(argv), 0, ps_bytes(.3*hw.time), b'')
                return out
            hw.ctx = ctx
            control = SimpleNamespace(wait=hw.sleep, runner=SimpleNamespace(state=lambda *a, **kw: None))
            summary = collectors.long_wait(hw, {'duration_s': 1200, 'quad': 0, 'arm': 'L'}, attempt, 1., control)
            self.assertEqual(summary['waited_s'], 2700.)
            self.assertEqual(summary['achieved_continuous_quiet_s'], 0.)
            self.assertEqual(summary['restarts'], 270)
            self.assertTrue(summary['capped'])
            # The exact returned row makes the run a hazard in the real
            # reader/flag path, without changing its measured phase energy.
            bundle = attempt/'runs/r'
            bundle.mkdir(parents=True)
            atomic_json(bundle/'summary_metrics.json', {'status': 'succeeded',
                        'phase_energy_j': {'prefill': 10., 'decode': 20.}})
            atomic_json(attempt/'collection.json', {'runs': [{'id': 'r', 'bundle': 'runs/r',
                'long_wait': summary, 'quad': 0, 'arm': 'L', 'returncode': 0}]})
            data = readers.flag_segments(readers.read_attempt(attempt), [])
            self.assertEqual(data['runs'][0]['phase_energy_j']['decode'], 20.)
            self.assertIn('long wait capped before 20 quiet minutes', data['runs'][0]['hazard_flags'])

    def test_clean_long_wait_finishes_after_twenty_minutes(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-wait-clean-') as tmp:
            hw = CollectorHardware(scale=1.)
            control = SimpleNamespace(wait=hw.sleep, runner=SimpleNamespace(state=lambda *a, **kw: None))
            summary = collectors.long_wait(hw, {'duration_s': 1200, 'quad': 0, 'arm': 'L'}, Path(tmp), 1., control)
            self.assertEqual(summary['waited_s'], 1200.)
            self.assertEqual(summary['achieved_continuous_quiet_s'], 1200.)
            self.assertEqual(summary['restarts'], 0)
            self.assertFalse(summary['capped'])

    def run_failed_quad(self, test_id, fail_indices):
        root = self.root/test_id
        hw = CollectorHardware(scale=.001)
        original = FakeChild.__init__
        calls = []
        def inject(child, manager, pid, argv, directory):
            original(child, manager, pid, argv, directory)
            if 'joulewise' not in argv or 'run' not in argv: return
            calls.append(child)
            if len(calls)-1 in fail_indices:
                config = read_json(Path(argv[argv.index('run')+1]))
                bundle = Path(argv[argv.index('--runs-dir')+1])/config['run_id']
                atomic_json(bundle/'summary_metrics.json', {'status': 'failed',
                    'failure_reason': 'injected_first_try', 'phase_energy_j': {}})
                child.returncode = 1
        plan = BY_ID[test_id]
        runner = Runner(REPO, root, sys.executable, hw.seams(), plans=(plan,), scale=.001, emit=lambda _: None)
        # Exercise one attempt; the job's later-pass retry is separately
        # covered by runner tests. This is the full real collect -> publish path.
        with patch.object(FakeChild, '__init__', inject):
            out = runner.test(plan)
        return out, calls, root/plan.test_id/'attempts/1'

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='quiet-kit-quad-retry-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_m2_failed_N_retries_quad_with_long_waits_and_first_complete_try(self):
        out, calls, attempt = self.run_failed_quad('m2-long-wait', {0})
        self.assertTrue(out['complete'])
        self.assertEqual(len(calls), 24)
        rows = out['measured']['run_table']
        self.assertEqual([r['quad_try'] for r in rows[:8]], [0]*4+[1]*4)
        self.assertEqual([r['arm'] for r in rows[:8]], list('NLLNNLLN'))
        self.assertTrue(all('long_wait' in r for r in rows if r['arm'] == 'L'))
        self.assertEqual(out['measured']['selected_quad_tries'], {'0': 1, '1': 0, '2': 0, '3': 0, '4': 0})
        self.assertEqual(out['measured']['phases']['decode']['long_minus_ordinary']['value'], 0.)

    def test_m2b_short_failure_retried_ok_stays_in_table_but_counts_retry(self):
        out, calls, attempt = self.run_failed_quad('m2b-short-baseline', {1})
        self.assertTrue(out['complete'])
        self.assertEqual(len(calls), 24)
        refusal = out['measured']['short_baseline_refusals']
        self.assertEqual(len(refusal), 1)
        self.assertTrue(refusal[0]['retried_ok'])
        self.assertEqual(out['measured']['selected_quad_tries']['0'], 1)
        # Each child has exactly 10/20 J in both arms, hence zero quad contrast.
        self.assertEqual(out['measured']['phases']['decode']['short_minus_ordinary']['value'], 0.)

    def test_m2b_short_failure_in_both_tries_refuses_and_retry_is_bounded(self):
        out, calls, attempt = self.run_failed_quad('m2b-short-baseline', {1, 5})
        self.assertFalse(out['complete'])
        self.assertEqual(len(calls), 24)
        self.assertEqual(out['incomplete_reason'], 'short_baseline_refused_by_run_path')
        self.assertTrue(all(not r['retried_ok'] for r in out['measured']['short_baseline_refusals']))
        self.assertEqual(out['measured']['phases']['decode']['complete_quad_count'], 4)
        self.assertIsNone(out['measured']['phases']['decode']['short_minus_ordinary']['value'])

    def test_m2b_retry_with_only_N_failure_is_generic_incomplete(self):
        out, calls, attempt = self.run_failed_quad('m2b-short-baseline', {1, 4})
        self.assertFalse(out['complete'])
        self.assertEqual(len(calls), 24)
        self.assertEqual(out['incomplete_reason'], 'short_baseline_run_table_incomplete')
        self.assertEqual(len(out['measured']['short_baseline_refusals']), 1)
        self.assertFalse(out['measured']['short_baseline_refusals'][0]['retried_ok'])

    def test_first_complete_try_is_selected_consistently_across_phases(self):
        rows = [{'quad': q, 'quad_try': attempt, 'arm': arm,
                 'phase_energy_j': {phase: 10+(difference if arm == 'L' else 0)
                                    for phase in ('prefill', 'decode')}}
                for q, attempt, difference in [(q, 0, .2) for q in range(5)]+[(0, 1, .8)]
                for arm in 'NLLN']
        self.assertAlmostEqual(analysis.m2({'runs': rows})['phases']['decode']['long_minus_ordinary']['value'], .2)
        del rows[0]['phase_energy_j']['decode']
        out = analysis.m2({'runs': rows})
        self.assertEqual(out['selected_quad_tries']['0'], 1)
        self.assertAlmostEqual(out['phases']['prefill']['long_minus_ordinary']['value'], (.8+4*.2)/5)
        self.assertAlmostEqual(out['phases']['decode']['long_minus_ordinary']['value'], (.8+4*.2)/5)

