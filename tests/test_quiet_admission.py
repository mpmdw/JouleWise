"""CPU accounting tests use counters, never live sampling or interval sleeps."""
import unittest
from joulewise import quiet_admission as qa

POLICY = dict(policy_id='cpu_interval_v1', bind_max_s=600, sample_interval_s=30,
              consecutive_quiet_samples=2, busy_core_max=0.05, post_bind_budget_s=9000)


def row(pid, cpu, *, start='old', epoch=0, ppid=1, command='fseventsd'):
    return dict(pid=pid, ppid=ppid, start_identity=start, start_epoch_s=epoch,
                command=command, cumulative_cpu_seconds=cpu)


def metrics(busy, *, load=1.2):
    return qa.interval_metrics({(2, 'old'): row(2, 0)}, {(2, 'old'): row(2, busy * 30)},
        interval_s=30, idle_fraction=1, logical_cpu=16, observer_pid=99, wall_start=100)


class CpuIntervalTests(unittest.TestCase):
    def test_low_load_busy_daemon_never_admits(self):
        self.assertFalse(qa.is_quiet(metrics(0.9, load=1.2), POLICY))

    def test_finished_burst_admits_despite_high_load(self):
        self.assertTrue(qa.is_quiet(metrics(0.02, load=3.7), POLICY))

    def test_cpu_aggregate_identity_and_observer_accounting(self):
        before = {(pid, 'old'): row(pid, 1) for pid in range(10, 20)}
        after = {(pid, 'old'): row(pid, 1.6) for pid in range(10, 20)}
        result = qa.interval_metrics(before, after, interval_s=30, idle_fraction=1,
            logical_cpu=16, observer_pid=10, wall_start=100)
        self.assertAlmostEqual(result['process_busy_cores'], 0.2)
        self.assertFalse(qa.is_quiet(result, POLICY))
        self.assertTrue(next(p for p in result['top_consumers'] if p['pid'] == 10)['observer'])
        before = {(2, 'old'): row(2, 100), (3, 'old'): row(3, 5)}
        after = {(2, 'new'): row(2, 6, start='new', epoch=110)}
        last = {(3, 'old'): row(3, 8)}
        result = qa.interval_metrics(before, after, interval_s=30, idle_fraction=1,
            logical_cpu=16, observer_pid=3, wall_start=100, last_seen=last)
        self.assertAlmostEqual(result['process_busy_cores'], 0.3)
        self.assertEqual(result['unaccounted'][0]['pid'], 2)
        self.assertEqual(result['unaccounted'][0]['start_identity'], 'old')
        self.assertTrue(next(p for p in result['top_consumers'] if p['pid'] == 3)['observer'])

    def test_host_busy_counts_unattributed_and_kernel_work(self):
        result = qa.interval_metrics({}, {}, interval_s=30, idle_fraction=.95,
            logical_cpu=16, observer_pid=1, wall_start=100)
        self.assertAlmostEqual(result['busy_cores'], .8)
        self.assertFalse(qa.is_quiet(result, POLICY))

    def test_parsers_use_identity_cumulative_cpu_and_only_second_top_sample(self):
        parsed = qa.parse_ps('  PID PPID STARTED TIME COMM\n'
            ' 42 1 Thu Sep 17 19:00:00 2026 2-01:02:03.45 /command with spaces\n')
        item = next(iter(parsed.values()))
        self.assertEqual(item['cumulative_cpu_seconds'], 176523.45)
        self.assertEqual(item['command'], '/command with spaces')
        self.assertEqual(qa.second_top_idle_fraction(
            'CPU usage: 99% user, 1% sys, 0% idle\nCPU usage: 0% user, 0% sys, 100% idle'), 1)
        with self.assertRaises(ValueError):
            qa.second_top_idle_fraction('CPU usage: 0% user, 0% sys, 100% idle')
        with self.assertRaises(ValueError):
            qa.parse_ps('bad output')


def legacy_counterfactual():
    """Replay the requested failing assertions against the actual base source.

    Intentionally exits nonzero when both scientifically wrong legacy decisions
    are demonstrated. Not part of unittest discovery's passing acceptance set.
    """
    import dataclasses
    import hashlib
    import subprocess
    import sys
    import types
    from pathlib import Path
    from tests.test_night_gate import FakeProbeSource, make_plan, REGISTRATION_TEXT
    from joulewise import night_gate
    baseline = types.ModuleType('quiet_counterfactual_base_gate')
    baseline.__file__ = str(Path(night_gate.__file__))
    sys.modules[baseline.__name__] = baseline
    exec(subprocess.check_output(['git', 'show', 'a90ab4e8:joulewise/night_gate.py'], text=True), baseline.__dict__)
    baseline.D166_REGISTRATION_SHA256 = hashlib.sha256(REGISTRATION_TEXT.encode()).hexdigest()
    failures = 0
    for name, load, busy, expected in [
        ('test_low_load_busy_daemon_never_admits', 1.2, .9, 'REFUSED'),
        ('test_finished_burst_admits_despite_high_load', 3.7, .02, 'GO'),
    ]:
        source = FakeProbeSource()
        source.results[night_gate.LOAD_AVG_ARGV] = night_gate.ProbeResult(
            night_gate.LOAD_AVG_ARGV, 0, f'{{ {load:.2f} 1.00 1.00 }}\n', '', 10)
        # The interval evidence is available through the same injected runner;
        # the baseline path never asks for it and instead uses only loadavg.
        source.results[qa.PS_ARGV] = night_gate.ProbeResult(
            qa.PS_ARGV, 0,
            'PID PPID STARTED TIME COMM\n'
            f'2 1 Thu Sep 17 19:00:00 2026 0:{busy * 30:05.2f} fseventsd\n', '', 10)
        def run(argv):
            result = source.run(argv)
            return baseline.ProbeResult(**dataclasses.asdict(result))
        probes = dataclasses.replace(source.probes(), run=run)
        receipt = baseline.evaluate_night(make_plan(), probes)
        try:
            unittest.TestCase().assertEqual(receipt.verdict, expected)
        except AssertionError as error:
            failures += 1
            print(f'{name}: load={load}, process_busy_cores={busy}; AssertionError: {error}')
        else:
            raise AssertionError(f'{name}: counterfactual unexpectedly passed')
    raise AssertionError(f'{failures} legacy counterfactual assertions failed as expected')
