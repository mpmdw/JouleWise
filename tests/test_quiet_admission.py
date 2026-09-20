"""CPU accounting tests use counters, never live sampling or interval sleeps."""
import unittest
from unittest import mock
from types import SimpleNamespace
from joulewise import quiet_admission as qa

POLICY = dict(policy_id='cpu_interval_v1', bind_max_s=600, sample_interval_s=30,
              consecutive_quiet_samples=2, busy_core_max=0.0, post_bind_budget_s=9000,
              cutoff_authority='TEST-ONLY-NOT-A-RULING')


def row(pid, cpu, *, start='old', epoch=0, ppid=1, command='fseventsd'):
    return dict(pid=pid, ppid=ppid, start_identity=start, start_epoch_s=epoch,
                command=command, cumulative_cpu_seconds=cpu)


def metrics(busy, *, load=1.2):
    return qa.interval_metrics({(2, 'old'): row(2, 0)}, {(2, 'old'): row(2, busy * 30)},
        interval_s=30, idle_fraction=1, logical_cpu=16, observer_pid=99, wall_start=100)


class CpuIntervalTests(unittest.TestCase):
    def test_zero_cutoff_validation_fixture_never_admits(self):
        self.assertEqual(qa.validate_policy(POLICY), POLICY)
        self.assertFalse(qa.is_quiet(metrics(0), POLICY))

    def test_low_load_busy_daemon_never_admits(self):
        self.assertFalse(qa.is_quiet(metrics(0.9, load=1.2), dict(POLICY, busy_core_max=0.05)))
        for command in ('fseventsd', 'mdworker_shared', 'mds', 'mds_stores',
                        'mediaanalysisd', 'deleted_helper', 'cloudd', 'bird',
                        'softwareupdated', 'backupd', 'arbitrary-program'):
            with self.subTest(command=command):
                observed = qa.interval_metrics(
                    {(2, 'old'): row(2, 10, command=command)},
                    {(2, 'old'): row(2, 37, command=command)},
                    interval_s=30, idle_fraction=1, logical_cpu=16, observer_pid=99, wall_start=100)
                self.assertAlmostEqual(observed['process_busy_cores'], 0.9)
                self.assertAlmostEqual(observed['busy_cores'], 0.9)
                self.assertFalse(qa.is_quiet(observed, dict(POLICY, busy_core_max=0.05)))

    def test_finished_burst_admits_despite_high_load(self):
        self.assertTrue(qa.is_quiet(metrics(0.02, load=3.7), dict(POLICY, busy_core_max=0.05)))
        # Deliberately supply stale percent CPU alongside cumulative snapshots.
        # Admission must ignore it in both directions.
        for percent_cpu, delta, expected_quiet in ((90, 0, True), (0, 27, False)):
            with self.subTest(percent_cpu=percent_cpu, delta=delta):
                before = {(2, 'old'): dict(row(2, 100), percent_cpu=percent_cpu)}
                after = {(2, 'old'): dict(row(2, 100 + delta), percent_cpu=percent_cpu)}
                observed = qa.interval_metrics(before, after, interval_s=30,
                    idle_fraction=1, logical_cpu=16, observer_pid=99, wall_start=100)
                self.assertEqual(observed['busy_cores'], delta / 30)
                self.assertEqual(qa.is_quiet(observed, dict(POLICY, busy_core_max=0.05)), expected_quiet)

    def test_cpu_aggregate_identity_and_observer_accounting(self):
        header = 'PID PPID STARTED TIME COMM\n'
        first_start, second_start = 'Thu Sep 17 19:00:00 2026', 'Thu Sep 17 19:00:10 2026'
        first = qa.parse_ps(header + f'42 1 {first_start} 0:10.00 old-command\n')
        second = qa.parse_ps(header + f'42 1 {second_start} 0:01.00 new-command\n')
        self.assertEqual(set(first), {(42, first_start)})
        self.assertEqual(set(second), {(42, second_start)})
        self.assertEqual(len(set(first) | set(second)), 2)
        self.assertFalse(set(first) & set(second))
        observed = qa.interval_metrics(first, second, interval_s=30, idle_fraction=1,
            logical_cpu=16, observer_pid=99, wall_start=first[(42, first_start)]['start_epoch_s'] + 1)
        self.assertAlmostEqual(observed['busy_cores'], 1 / 30)  # new lifetime, not 1 - 10
        self.assertEqual(observed['unaccounted'][0]['start_identity'], first_start)
        before = {(pid, 'old'): row(pid, 1) for pid in range(10, 20)}
        after = {(pid, 'old'): row(pid, 1.6) for pid in range(10, 20)}
        result = qa.interval_metrics(before, after, interval_s=30, idle_fraction=1,
            logical_cpu=16, observer_pid=10, wall_start=100)
        self.assertAlmostEqual(result['process_busy_cores'], 0.2)
        self.assertFalse(qa.is_quiet(result, dict(POLICY, busy_core_max=0.05)))
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
        self.assertFalse(qa.is_quiet(result, dict(POLICY, busy_core_max=0.05)))

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

    def test_second_top_idle_fraction_tolerates_top_rounding_but_not_gaps(self):
        # Live 2026-09-17 20:38 PDT: top printed 9.36% user, 3.6% sys, 87.3% idle (sum 100.26)
        # and the strict 0.1 tolerance refused a valid sample; the "> 0.1" mutant must fail here.
        two = "CPU usage: 0% user, 0% sys, 100% idle\nCPU usage: 9.36% user, 3.6% sys, 87.3% idle \n"
        self.assertAlmostEqual(qa.second_top_idle_fraction(two), 0.873)
        low = "CPU usage: 0% user, 0% sys, 100% idle\nCPU usage: 1.53% user, 7.17% sys, 91.28% idle\n"
        self.assertAlmostEqual(qa.second_top_idle_fraction(low), 0.9128)
        with self.assertRaises(ValueError):
            qa.second_top_idle_fraction("CPU usage: 0% user, 0% sys, 100% idle\nCPU usage: 1.0% user, 1.0% sys, 96.5% idle\n")


class SamplerCommandTests(unittest.TestCase):
    def test_top_argv_uses_integer_seconds(self):
        self.assertEqual(qa.top_argv(30.0), ('/usr/bin/top', '-l', '2', '-s', '30', '-n', '0'))
        for interval in (30.5, 0, -1, True, float('nan')):
            with self.subTest(interval=interval), self.assertRaises(ValueError):
                qa.top_argv(interval)

    def observe(self, *, boot_error=False):
        from joulewise.night_gate import AGENT_CENSUS_ARGV
        import subprocess
        cpu = [0.0]
        def run(argv, **kwargs):
            cpu[0] += 0.4 if argv == AGENT_CENSUS_ARGV else 0.1
            if argv == qa.BOOT_ARGV and boot_error:
                raise OSError('fixture sysctl denied')
            outputs = {
                qa.BOOT_ARGV: '11111111-1111-4111-8111-111111111111\n',
                qa.PS_ARGV: 'PID PPID STARTED TIME COMM\n42 1 Thu Sep 17 19:00:00 2026 0:01.00 observer\n',
                ('/usr/bin/top', '-l', '2', '-s', '30', '-n', '0'):
                    'CPU usage: 99% user, 1% sys, 0% idle\nCPU usage: 0% user, 0% sys, 100% idle\n',
                qa.LOGICAL_CPU_ARGV: '16\n', qa.LOAD_ARGV: '{ 3.70 1.00 1.00 }\n',
                AGENT_CENSUS_ARGV: '',
            }
            return subprocess.CompletedProcess(argv, 1 if argv == AGENT_CENSUS_ARGV else 0,
                                                outputs[argv], '')
        def usage(kind):
            return SimpleNamespace(ru_utime=cpu[0] / 2, ru_stime=0)
        with mock.patch.object(qa.subprocess, 'run', side_effect=run) as command, \
             mock.patch.object(qa.time, 'time', side_effect=[1000, 1030]), \
             mock.patch.object(qa.time, 'monotonic', side_effect=[0, 0, 30, 30]):
            observed = qa.sample_interval(30.0, observer_pid=42)
        return observed, command.call_args_list

    def test_sampler_argv_are_exact_tuples_and_cost_includes_census(self):
        observed, calls = self.observe()
        self.assertEqual([call.args[0] for call in calls], [
            ('/usr/sbin/sysctl', '-n', 'kern.bootsessionuuid'),
            ('/bin/ps', '-Ao', 'pid,ppid,lstart,time,comm'),
            ('/usr/bin/top', '-l', '2', '-s', '30', '-n', '0'),
            ('/bin/ps', '-Ao', 'pid,ppid,lstart,time,comm'),
            ('/usr/sbin/sysctl', '-n', 'hw.logicalcpu'),
            ('/usr/sbin/sysctl', '-n', 'vm.loadavg'),
            ('/usr/bin/pgrep', '-lf', '[c]odex|[c]laude|[t]3'),
        ])
        self.assertEqual(calls[2].kwargs['timeout'], 60)
        self.assertFalse(calls[-1].kwargs['check'])  # pgrep exit 1 is an empty census
        self.assertNotIn('observer_cpu_s', observed)  # parent measures startup + all workers + journal
        qa.validate_observation(observed, POLICY)
        self.assertEqual(set(qa.smoke_metrics(observed, 1.0)), {
            'busy_cores', 'host_busy_cores', 'observer_cpu_s', 'top_consumers', 'load_avg_diagnostic'})

    def test_boot_read_failure_retains_metrics_but_is_never_quiet(self):
        observed, calls = self.observe(boot_error=True)
        self.assertEqual(len(calls), 7)
        self.assertIsNone(observed['boot_identity'])
        self.assertIn('sysctl denied', observed['boot_identity_unavailable'])
        self.assertIn('observer_cpu_s', qa.smoke_metrics(observed, 1.0))
        with self.assertRaisesRegex(ValueError, 'boot_identity_unavailable'):
            qa.validate_observation(observed, dict(POLICY, busy_core_max=1))


class ObservationWorkerCliTests(unittest.TestCase):
    def test_full_observation_mode_uses_framed_publication(self):
        import os
        import json
        read_fd, write_fd = os.pipe()
        self.addCleanup(os.close, read_fd)
        observation = {'fixture': 'full observation'}
        with mock.patch.object(qa, 'sample_interval', return_value=observation) as sample:
            self.assertEqual(qa.main(['--observation', '--sample-interval-s', '30',
                '--observer-pid', '42', '--job-id', 'sample-1', '--result-fd', str(write_fd)]), 0)
        raw = os.read(read_fd, 4096)
        self.assertEqual(int.from_bytes(raw[:4], 'big'), len(raw)-4)
        self.assertEqual(json.loads(raw[4:]), dict(job_id='sample-1', ok=True, result=observation))
        sample.assert_called_once_with(30.0, observer_pid=42)

    def test_smoke_prints_parent_round_cost(self):
        import io
        import json
        from contextlib import redirect_stdout
        observed, _ = SamplerCommandTests().observe()
        out = io.StringIO()
        with mock.patch('scripts.run_night.smoke_observation_round', return_value=(observed, 2.75)) as round_, redirect_stdout(out):
            self.assertEqual(qa.main(['--sample-interval-s', '30']), 0)
        round_.assert_called_once_with(30.0)
        self.assertEqual(json.loads(out.getvalue())['observer_cpu_s'], 2.75)


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
