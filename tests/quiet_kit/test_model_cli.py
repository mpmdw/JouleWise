"""Real single-run CLI bundles, with only the two instrument backends mocked."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.quiet_kit import analysis, collectors, readers
from joulewise.quiet_kit.paths import atomic_json
from joulewise.quiet_kit.processes import Processes
from joulewise.quiet_kit.runner import Runner
from joulewise.quiet_kit.schedule import BY_ID, TestPlan
from .fakes import FakeHardware

REPO = Path(__file__).resolve().parents[2]


def mock_config(config):
    config['hardware_target']['runtime_backend'] = 'mock'
    config['hardware_target']['telemetry_backend'] = 'mock'
    config['sampling']['idle_seconds'] = .5
    config['sampling']['warmup_seconds'] = .1


def kernel_group_absent(pgid, timeout_s=2.):
    """Sandbox-compatible real kernel check; mock CLI has no grandchildren."""
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return True, []
    except PermissionError:
        return False, ['group exists but cannot be signalled']
    return False, ['group still exists']


class DeskControl:
    def __init__(self):
        self.deadline = time.monotonic()+110
        self.runner = SimpleNamespace(state=lambda *a, **kw: None)

    def check(self):
        if time.monotonic() >= self.deadline:
            raise TimeoutError('mock CLI desk test exceeded 110 seconds')

    def wait(self, seconds):
        self.check()
        time.sleep(min(seconds, .01))


class RealModelCLITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='quiet-kit-real-cli-')
        cls.addClassCleanup(cls.temp.cleanup)
        # macOS sandbox denies pgrep's sysmond census. This checks the actual
        # process group instead, without assuming success from an exit code.
        census = patch('joulewise.hazards.instrument.group_absent', kernel_group_absent)
        census.start()
        cls.addClassCleanup(census.stop)
        cls.root = Path(cls.temp.name)
        cls.processes = Processes(REPO)
        cls.addClassCleanup(cls.processes.cleanup)
        cls.hw = SimpleNamespace(repo=REPO, model_python=sys.executable,
            stamp=collectors.stamp, processes=cls.processes)
        cls.control = DeskControl()
        cls.started = time.monotonic()
        cls.attempts = {}
        plans = [BY_ID['m2b-short-baseline'],
            TestPlan('m15-drift-transfer', BY_ID['m15-drift-transfer'].segments[:6], model_runs=tuple('RABBAR')),
            BY_ID['m2-long-wait']]
        # The wait instrument alone is a desk seam; all 46 model children
        # execute the real CLI, controller, reducer, writer, and Processes.
        def scaled_wait(hw, segment, attempt, scale, control):
            control.wait(segment['duration_s']*scale)
        for plan in plans:
            attempt = cls.root/plan.test_id/'attempts/1'
            attempt.mkdir(parents=True)
            cls.attempts[plan.test_id] = attempt
            with patch.object(collectors, 'long_wait', scaled_wait):
                collectors.collect(cls.hw, plan, attempt, .000001, cls.control, 'measurement',
                                   config_transform=mock_config)
            doc = json.loads((attempt/'collection.json').read_text())
            for row in doc['runs']:
                if row['returncode'] != 0:
                    raise AssertionError(row)
        cls.elapsed = time.monotonic()-cls.started

    def test_m2b_twenty_real_bundles_and_independent_quad_arithmetic(self):
        attempt = self.attempts['m2b-short-baseline']
        data = readers.read_attempt(attempt)
        self.assertEqual([r['arm'] for r in data['runs']], list('NSSN'*5))
        self.assertEqual(len(data['runs']), 20)
        self.assertTrue(all(not r['failure_reasons'] and not r['flags'] for r in data['runs']))
        out = analysis.m2b(data)
        self.assertIsNone(out['incomplete_reason'])
        self.assertEqual(out['short_baseline_refusals'], [])
        docs = [json.loads((attempt/r['bundle']/'summary_metrics.json').read_text()) for r in data['runs']]
        for phase in ('prefill', 'decode'):
            expected = []
            for q in range(5):
                n1, s1, s2, n2 = [d['phase_energy_j'][phase] for d in docs[4*q:4*q+4]]
                expected.append((s1+s2-n1-n2)/2)
            self.assertEqual(out['phases'][phase]['quad_differences_j'], expected)
            self.assertEqual(out['phases'][phase]['short_minus_ordinary']['value'], sum(expected)/5)
        self.assertLess(self.elapsed, 120)

    def test_m15_real_start_block_all_three_workloads(self):
        attempt = self.attempts['m15-drift-transfer']
        data = readers.read_attempt(attempt)
        self.assertEqual([r['workload'] for r in data['runs']], list('RABBAR'))
        self.assertTrue(all(not r['failure_reasons'] for r in data['runs']))
        start_only = analysis.m15(data)
        self.assertEqual(start_only['incomplete_reason'], 'workload_drift_undefined')
        # Reuse the start block as a deterministic end-block desk observation.
        # This is labelled synthetic, not an additional collected block.
        paired = {'runs': data['runs'] + [{**r, 'block': 'end'} for r in data['runs']]}
        out = analysis.m15(paired)
        self.assertIsNone(out['incomplete_reason'])
        docs = [(r, json.loads((attempt/r['bundle']/'summary_metrics.json').read_text())) for r in data['runs']]
        for phase in ('prefill', 'decode'):
            reference = [d['phase_energy_j'][phase] for r, d in docs if r['workload'] == 'R']
            for workload in 'RAB':
                energies = [d['phase_energy_j'][phase] for r, d in docs if r['workload'] == workload]
                expected = (sum(energies)/len(energies))/(sum(reference)/len(reference))
                self.assertEqual(out['energy_ratios'][phase][workload]['value'], expected)
                self.assertEqual(out['drift_by_phase'][phase][workload]['value'], 0.)

    def test_m2_real_bundles_publish_complete_plain_summary(self):
        attempt = self.attempts['m2-long-wait']
        data = readers.read_attempt(attempt)
        self.assertTrue(all(not r['failure_reasons'] for r in data['runs']))
        out = analysis.m2(data)
        self.assertIsNone(out['incomplete_reason'])
        for phase in ('prefill', 'decode'):
            values = [json.loads((attempt/r['bundle']/'summary_metrics.json').read_text())['phase_energy_j'][phase]
                      for r in data['runs']]
            expected = [(values[i+1]+values[i+2]-values[i]-values[i+3])/2 for i in range(0, 20, 4)]
            self.assertEqual(out['phases'][phase]['quad_differences_j'], expected)
        atomic_json(attempt/'attempt.json', {'state': 'started'})
        # A nonempty stamp is the runner's collection-finished marker.
        atomic_json(attempt/'conditions.json', {'start': {}, 'end': {}, 'end_stamp': {'utc': 'desk'}})
        fake = FakeHardware()
        runner = Runner(REPO, self.root, sys.executable, fake.seams(), emit=lambda _: None)
        result = runner.publish(BY_ID['m2-long-wait'], attempt)
        self.assertTrue(result['complete'])
        summary = (self.root/'m2-long-wait/summary.md').read_text()
        self.assertTrue(summary.endswith('\n'))
        self.assertEqual(len(summary.strip().splitlines()), 1)
        self.assertIn('joules', summary)
        self.assertNotIn('CPU-s/s', summary)
        self.assertNotIn('```', summary)

    def test_transform_still_fences_model_source_and_production_S_stays_50(self):
        def forbidden(config):
            mock_config(config)
            config['model']['source'] = '/Users/edr/night-custody/forbidden-model'
        for workload in 'RAB':
            with self.assertRaisesRegex(ValueError, 'blinded path'):
                collectors.model_config(REPO, workload, 'qk-fenced', config_transform=forbidden)
        self.assertEqual(collectors.model_config(REPO, 'R', 'qk-production-S',
                         short_baseline=True)['sampling']['idle_seconds'], 50.)
