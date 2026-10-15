"""Cold-review regressions: real raw readers and publication, desk hardware only."""
from __future__ import annotations

import json
import math
import os
import statistics
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from joulewise.quiet_kit import analysis, cli, collectors, readers
from joulewise.quiet_kit.hardware import Hardware
from joulewise.quiet_kit.paths import atomic_json, read_json
from joulewise.quiet_kit.runner import Runner, Control, read_json_lines
from joulewise.quiet_kit.schedule import BY_ID, TestPlan
from .collector_fakes import CollectorHardware, FakeChild
from .fakes import FakeHardware
from .fixtures import EPOCH, RAW, plist_stream, power_attempt, synthetic_capture

REPO = Path(__file__).resolve().parents[2]


def ps_document(t, cpu, *, error=None, tree_cpu=0.):
    stamp = {'wall_ns': round((EPOCH+t)*1e9), 'monotonic_ns': round((RAW+t)*1e9),
             'monotonic_raw_ns': round((RAW+t)*1e9)}
    def row(pid, parent, name, work):
        return {'pid': pid, 'ppid': parent, 'command': name, 'cumulative_cpu_seconds': work,
                'start_identity': 'Wed Oct 14 00:00:00 2026', 'start_epoch_s': EPOCH-3600}
    return {'started': stamp, 'finished': stamp, 'error': error, 'host_cpu': None, 'host_error': None,
            'rows': [row(500, 1, 'fixture-daemon', cpu), row(901, 900, 'fixture-load', tree_cpu)]}


class RawRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='quiet-kit-round4-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def attempt(self, test_id):
        return self.root/test_id/'attempts/1'

    def publish(self, test_id, attempt):
        atomic_json(attempt/'attempt.json', {'state': 'started', 'test_id': test_id})
        atomic_json(attempt/'conditions.json', {'end_stamp': {'utc': 'desk'}, 'start': {}, 'end': {}})
        return Runner(REPO, self.root, sys.executable, FakeHardware().seams(), emit=lambda _: None).publish(
            BY_ID[test_id], attempt)

    def daemon(self, *, coverage_s=30.):
        attempt = self.attempt('m4-contention-watts')
        (attempt/'rails').mkdir(parents=True)
        # Each busy interval contains a 2 s rectangle of +1 W, away from
        # its midpoint. Integral/10 = .2 W, divided by .2 CPU-s/s = 1 W.
        rows = []
        for i in range(round(coverage_s*10)):
            t = i/10
            rows.append({'start_s': EPOCH+t, 'end_s': EPOCH+(i+1)/10,
                         'cpu_power': .05+(1. if 2 <= t < 4 or 22 <= t < 24 else 0.)})
        (attempt/'rails/powermetrics.plist').write_bytes(plist_stream(rows))
        atomic_json(attempt/'rails/sampler.json', {'first_record_endpoint_s': EPOCH+.1,
                    'start': {'epoch_s': EPOCH, 'raw_s': RAW}})
        segment = {'id': 'idle', 'kind': 'idle', 'start': {'epoch_s': EPOCH, 'raw_s': RAW},
            'end': {'epoch_s': EPOCH+30, 'raw_s': RAW+30},
            'snapshots': [ps_document(0, 100), ps_document(30, 104)],
            'tick_snapshots': [ps_document(10, 102), ps_document(20, 102)]}
        atomic_json(attempt/'collection.json', {'sampler_dir': 'rails', 'segments': [segment], 'tree_roots': [900]})
        return attempt

    def test_daemon_window_full_interval_mean_and_fit_through_publish(self):
        attempt = self.daemon()
        result = self.publish('m4-contention-watts', attempt)
        ticks = result['measured']['daemon_inference'][0]['simultaneous_ticks']
        for row, expected in zip(ticks, (.25, .05, .25)):
            self.assertAlmostEqual(row['rail_power_w'], expected, places=9)
            self.assertAlmostEqual(row['rail_power_coverage_s'], 10., places=5)
            self.assertEqual(row['interval_s'], 10.)
            self.assertIsNone(row['rail_power_undefined'])
        self.assertAlmostEqual(result['measured']['daemon_watts_per_cpu_rate_fit']['slope'], 1., places=9)

    def test_daemon_under_ninety_percent_coverage_is_dropped(self):
        attempt = self.daemon(coverage_s=8.9)
        data = readers.read_attempt(attempt)
        tick = data['segments'][0]['ticks'][0]
        self.assertAlmostEqual(tick['rail_power_coverage_s'], 8.9, places=5)
        self.assertIsNone(tick['rail_power_w'])
        self.assertIn('90%', tick['rail_power_undefined'])
        self.assertIn('undefined', analysis.m4(data)['daemon_watts_per_cpu_rate_fit'])

    def test_daemon_exact_ninety_percent_coverage_is_accepted(self):
        attempt = self.daemon(coverage_s=9.)
        tick = readers.read_attempt(attempt)['segments'][0]['ticks'][0]
        self.assertAlmostEqual(tick['rail_power_coverage_s'], 9., places=5)
        self.assertIsNotNone(tick['rail_power_w'])

    def contended(self, test_id):
        attempt = self.attempt(test_id)
        doc = power_attempt(attempt, [
            {'kind': 'idle', 'duration_s': 10, 'power': .05},
            {'kind': 'cpu', 'duration_s': 10, 'power': 1.05, 'cpu_seconds': 2.,
             'priority': 'background', 'duty': .2},
            {'kind': 'idle', 'duration_s': 10, 'power': .35}], meter=test_id.startswith('m14'))
        for s, a, b, c0, c1 in zip(doc['segments'], (0, 10, 20), (10, 20, 30), (100, 100, 100), (100, 100, 103)):
            s['snapshots'] = [ps_document(a, c0, tree_cpu=a), ps_document(b, c1, tree_cpu=b)]
            s['load_pids'] = [901] if s['kind'] == 'cpu' else []
        doc['tree_roots'] = [900]
        atomic_json(attempt/'collection.json', doc)
        return attempt

    def test_contended_bracket_flag_main_alternative_and_no_clean_arm(self):
        for test_id, field in [('m4-contention-watts', 'arms'), ('m5-gpu-rail', 'levels'),
                               ('m14-meter-idle-power', 'levels')]:
            with self.subTest(test_id=test_id):
                attempt = self.contended(test_id)
                data = readers.flag_segments(readers.read_attempt(attempt), [])
                self.assertEqual(data['segments'][2]['hazard_flags'], ['outside contention during segment'])
                dirty = data['segments'][2]['outside_contention'][0]
                self.assertEqual(dirty['max_outside']['pid'], 500)
                self.assertAlmostEqual(dirty['max_outside']['cpu_s_per_s'], .3)
                result = self.publish(test_id, attempt)
                arm = result['measured'][field][0]
                self.assertEqual(arm['outside_cpu_rate'], {'before': 0., 'load': 0., 'after': .3})
                self.assertAlmostEqual(arm['outside_rate_difference'], -.15)
                self.assertEqual(result['without_flagged_segments'][field], [])
                if field == 'arms':
                    self.assertAlmostEqual(arm['power_step']['value'], 1.05-(.05+.35)/2)
                    self.assertAlmostEqual(arm['watts_per_cpu_rate']['value'], .85/.2)
                    self.assertAlmostEqual(arm['watts_per_total_cpu_rate']['value'], .85/(.2-.15))
                    self.assertIn('not the main result', arm['watts_per_total_cpu_rate']['label'])
                    from joulewise.quiet_kit.runner import summary
                    self.assertIn('background 20%', summary(result))
                    self.assertIn('alternative assuming outside work costs the same watts', summary(result))
                    self.assertNotIn('arms 1 power step', summary(result))

    def test_dirty_accounting_tick_flags_even_when_segment_mean_is_below_limit(self):
        attempt = self.daemon()
        doc = read_json(attempt/'collection.json')
        segment = doc['segments'][0]
        segment.update(snapshots=[ps_document(0, 100), ps_document(30, 100.6)],
                       tick_snapshots=[ps_document(10, 100.6), ps_document(20, 100.6)])
        atomic_json(attempt/'collection.json', doc)
        data = readers.flag_segments(readers.read_attempt(attempt), [])
        self.assertAlmostEqual(data['segments'][0]['outside_cpu_rate'], .02)
        self.assertIn('outside contention during segment', data['segments'][0]['hazard_flags'])

    def test_outside_work_alternative_keeps_signed_formula_and_zero_is_undefined(self):
        attempt = self.contended('m4-contention-watts')
        doc = read_json(attempt/'collection.json')
        doc['segments'][2]['snapshots'][1] = ps_document(30, 110)
        atomic_json(attempt/'collection.json', doc)
        out = self.publish('m4-contention-watts', attempt)['measured']['arms'][0]
        self.assertAlmostEqual(out['watts_per_total_cpu_rate']['value'], .85/(.2-.5))
        doc['segments'][2]['snapshots'][1] = ps_document(30, 104)
        atomic_json(attempt/'collection.json', doc)
        out = self.publish('m4-contention-watts', attempt)['measured']['arms'][0]
        self.assertIsNone(out['watts_per_total_cpu_rate']['value'])

    def test_unread_ps_interval_is_flagged(self):
        attempt = self.contended('m4-contention-watts')
        doc = read_json(attempt/'collection.json')
        doc['segments'][0]['snapshots'][1]['error'] = 'ps unreadable'
        atomic_json(attempt/'collection.json', doc)
        data = readers.flag_segments(readers.read_attempt(attempt), [])
        self.assertIn('outside contention during segment', data['segments'][0]['hazard_flags'])

    def test_burst_and_arms_never_repair_adjacency_after_exclusions(self):
        attempt = self.attempt('m4-contention-watts')
        specs = [{'kind': 'idle', 'power': .1}, {'kind': 'cpu', 'power': 1.1, 'cpu_seconds': .4},
                 {'kind': 'idle', 'power': .3}, {'kind': 'burst', 'duration_s': 10, 'burst_s': .62},
                 {'kind': 'idle', 'power': .2}, {'kind': 'cpu', 'power': 2.2, 'cpu_seconds': .4},
                 {'kind': 'idle', 'power': .2}]
        doc = power_attempt(attempt, specs)
        # Dirty middle idle belongs to both the first arm and the burst;
        # a later clean arm retains its own two .2 W brackets.
        s = doc['segments'][2]
        atomic_json(attempt/'collection.json', doc)
        atomic_json(attempt/'watch.json', {})
        from joulewise.quiet_kit.paths import append
        append(attempt/'watch.jsonl', {'stamp': {'monotonic_raw_ns': round(s['start']['raw_s']*1e9)},
                                      'physics': {'thermal_level': 2}})
        append(attempt/'watch.jsonl', {'stamp': {'monotonic_raw_ns': round(s['end']['raw_s']*1e9)},
                                      'physics': {'thermal_level': 0}})
        out = self.publish('m4-contention-watts', attempt)
        clean = out['without_flagged_segments']
        self.assertEqual([a['segment'] for a in clean['arms']], ['s005'])
        self.assertEqual(clean['bursts'], [])
        self.assertAlmostEqual(clean['arms'][0]['power_step']['value'], 2.)

    def test_distinct_rails_and_asymmetric_brackets_through_real_reader(self):
        attempt = self.attempt('m5-gpu-rail')
        doc = power_attempt(attempt, [{'kind': 'idle', 'power': 1., 'gpu': 2., 'ane': 3.},
            {'kind': 'gpu', 'power': 11., 'gpu': 22., 'ane': 33., 'cpu_seconds': 1.},
            {'kind': 'idle', 'power': 3., 'gpu': 6., 'ane': 9.}])
        result = self.publish('m5-gpu-rail', attempt)
        out = result['measured']
        self.assertAlmostEqual(out['idle_gpu_mean']['value'], (2+6)/2)
        for rail, expected in [('cpu_power', 11-(1+3)/2), ('gpu_power', 22-(2+6)/2),
                               ('ane_power', 33-(3+9)/2), ('total', 66-(6+18)/2)]:
            self.assertAlmostEqual(out['levels'][0]['added_power'][rail]['value'], expected)

    def test_model_run_records_ps_and_outside_work_is_flagged(self):
        hw = CollectorHardware(scale=.01)
        attempt = self.attempt('m2b-short-baseline')
        attempt.mkdir(parents=True)
        runner = Runner(REPO, self.root, sys.executable, hw.seams(), scale=.01, emit=lambda _: None)
        control = Control(runner, attempt, plumbing=True)
        original_ctx = hw.ctx
        from .fixtures import ps_bytes
        def ctx(directory=None):
            context = original_ctx(directory)
            context.run = lambda argv, timeout: __import__('joulewise.hazards.base', fromlist=['Completed']).Completed(
                tuple(argv), 0, ps_bytes(100+.3*hw.time), b'')
            return context
        hw.ctx = ctx
        row = collectors.model_run(hw, {'kind': 'model', 'workload': 'R', 'quad': 0, 'arm': 'S'}, attempt, 0, control)
        self.assertEqual(len(row['snapshots']), 2)
        self.assertEqual(len(list((attempt/'ps').glob('boundary-*.json'))), 2)
        atomic_json(attempt/'collection.json', {'runs': [row], 'tree_roots': [os.getpid()]})
        out = readers.flag_segments(readers.read_attempt(attempt), [])
        self.assertAlmostEqual(out['runs'][0]['outside_cpu_rate'], .3, delta=.01)
        self.assertIn('outside contention during run', out['runs'][0]['hazard_flags'])

    def test_m1_per_condition_and_nonreproduced_utility_raw_capture(self):
        # This is the reviewer's hand block. Pair rule is max + max(delta,14.531).
        quiet = [27.1, 28.4, 30.2, 36.9, 29.5, 28.8, 31.0, 27.7, 38.0, 29.9]
        load = [33., 41.2, 35.5, 39.9]
        utility = [70., 66., 68.5, 72.4]
        caps = [{'id': f'{condition}{i}', 'condition': condition, 'bound_s': v/1000}
                for condition, values in [('quiet', quiet), ('load', load), ('utility', utility)]
                for i, v in enumerate(values)]
        result = analysis.m1({'captures': caps})
        qmax = max(max(a, b)+max(abs(b-a), 14.531)
                   for i, a in enumerate(quiet) for j, b in enumerate(quiet) if i != j)
        for condition, values in [('load', load), ('utility', utility)]:
            dmin = min(max(a, b)+max(abs(b-a), 14.531) for a in quiet for b in values)
            self.assertAlmostEqual(result['separation'][condition]['value'], dmin-qmax)
            self.assertAlmostEqual(result['stop_line_range'][condition]['upper_ms'], dmin)
        self.assertAlmostEqual(result['separation']['load']['value'], -5.)
        self.assertIsNone(analysis.m1({'captures': caps[:14]})['incomplete_reason'])
        # Real capture bytes prove cadence flows through read_attempt into
        # utility_not_reproduced and out of the utility arm before publish.
        attempt = self.attempt('m1-capture-stop-line')
        cap = attempt/'capture-0'
        (cap/'raw').mkdir(parents=True)
        raw, events, anchor, protocol = synthetic_capture(count=3)
        (cap/'raw/powermetrics.plist').write_bytes(raw)
        (cap/'events.jsonl').write_bytes(events)
        atomic_json(cap/'raw/sampler.json', {'clock_anchor': anchor})
        atomic_json(cap/'capture.json', {'protocol_id': protocol, 'cadence_median_ms': 100.})
        atomic_json(attempt/'collection.json', {'captures': [{'id': 'u', 'condition': 'utility', 'directory': 'capture-0'}]})
        result = self.publish('m1-capture-stop-line', attempt)['measured']
        self.assertEqual([r['id'] for r in result['utility_not_reproduced']], ['u'])
        self.assertEqual(result['conditions']['utility']['capture_count'], 0)

    def test_m10_requires_charger_supplied_palindrome_fit(self):
        attempt = self.attempt('m10-rails-vs-wall')
        doc = power_attempt(attempt, [{**s, 'power': {'idle': 1, 'cpu': 2, 'gpu': 4, 'mixed': 6}[s['kind']],
            'duration_s': 2, 'meter_power': 3+2*{'idle': 1, 'cpu': 2, 'gpu': 4, 'mixed': 6}[s['kind']]}
            for s in BY_ID['m10-rails-vs-wall'].segments], meter=True)
        # No meter data means no battery reads, but retain all-levels data
        # via explicit meter raw readings that show assist for every point.
        meter_path = attempt/'meter.jsonl'
        rows = [json.loads(line) for line in meter_path.read_text().splitlines()]
        for row in rows:
            if row.get('k') == 'b': row['smc']['B0AC'] = 500
        meter_path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
        out = self.publish('m10-rails-vs-wall', attempt)
        self.assertFalse(out['complete'])
        self.assertIsNotNone(out['incomplete_reason'])
        self.assertAlmostEqual(out['measured']['palindrome_all_levels_fit']['slope']['value'], 2., places=4)
        self.assertIsNone(out['measured']['palindrome_charger_supplied_fit']['slope']['value'])

    def test_m13_precision_fields_publish_from_real_meter_and_plist_bytes(self):
        hw = FakeHardware(scale=.001)
        runner = Runner(REPO, self.root, sys.executable, hw.seams(), scale=.001, emit=lambda _: None)
        out = runner.test(BY_ID['m13-meter-edges'])
        self.assertTrue(out['complete'])
        measured = out['measured']
        # The fixture meter is a linear rise/fall whose half-amplitude is
        # exactly command+12 ms. Three 59-pulse captures supply 354 edges.
        self.assertAlmostEqual(measured['meter_lag_mean']['value'], 12., places=3)
        self.assertEqual(measured['meter_edge_count'], 3*59*2)
        self.assertLess(measured['meter_lag_sd']['value'], .001)
        self.assertLess(measured['meter_mean_lag_pooled_se']['value'], .001)
        self.assertTrue(measured['precision_below_typical_bound'])
        self.assertEqual(measured['meter_minus_sampler']['n'], 3*59*2)
        self.assertEqual(len(measured['meter_lag_by_capture']), 3)
        for row in measured['meter_lag_by_capture']:
            self.assertEqual(row['n'], 59*2)
            self.assertLess(row['mean_lag_se']['value'], .001)


class RecoveryAndWakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='quiet-kit-handoff-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'WAKE_CMD').write_text('desk wake')
        self.hw = FakeHardware()

    def runner(self):
        return Runner(REPO, self.root, sys.executable, self.hw.seams(), scale=.001,
                      plans=(BY_ID['m9-time-server'],), deadline_hours=.01, emit=lambda _: None)

    def test_rearm_rotates_both_markers_between_bootout_and_bootstrap(self):
        self.assertEqual(self.runner().run(), 0)
        self.assertEqual(self.runner().run(), 0)
        self.assertEqual(len(self.hw.wakes), 1)
        original = {name: (self.root/name).read_bytes() for name in ('DONE', 'WAKE_DONE')}
        def command(argv, **kw):
            if argv[1] == 'bootout':
                self.assertTrue((self.root/'WAKE_DONE').exists())
            if argv[1] == 'bootstrap':
                self.assertFalse((self.root/'WAKE_DONE').exists())
                self.assertFalse((self.root/'DONE').exists())
            return subprocess.CompletedProcess(argv, 0, '', '')
        with patch('joulewise.quiet_kit.cli.mkdir', side_effect=lambda p:
                   Path(p) if str(p) == '/private/tmp/jw-quiet-kit' else Path(p).mkdir(parents=True, exist_ok=True) or Path(p)):
            self.assertEqual(cli.arm(REPO, self.root, sys.executable, command=command, emit=lambda _: None), 0)
        handoffs = list((self.root/'handoffs').iterdir())
        self.assertEqual(len(handoffs), 1)
        for name, raw in original.items(): self.assertEqual((handoffs[0]/name).read_bytes(), raw)
        self.assertEqual(self.runner().run(), 0)
        self.assertEqual(len(self.hw.wakes), 2)

    def test_wake_clean_environment_wrapper_and_launch_failure_in_done(self):
        hw = Hardware(REPO, sys.executable)
        env = {'HOME': '/Users/desk', 'USER': 'desk', 'LOGNAME': 'desk', 'LANG': 'en_US.UTF-8',
               'PYTHONPATH': '/bad', 'TMPDIR': '/bad', 'OTHER': 'discard'}
        with patch.dict(os.environ, env, clear=True), patch('subprocess.Popen', return_value=SimpleNamespace(pid=42)) as popen:
            result = hw.wake('exit 7', self.root/'wake.log')
        self.assertEqual(result['pid'], 42)
        argv = popen.call_args.args[0]
        self.assertEqual(argv[:2], ['/bin/zsh', '-c'])
        self.assertIn('/bin/zsh -c', argv[2])
        self.assertIn('wake_rc=$?', argv[2])
        self.assertIn('wake exit $wake_rc', argv[2])
        self.assertIn('/bin/date -u', argv[2])
        self.assertEqual(popen.call_args.kwargs['env'], {k: env[k] for k in ('HOME', 'USER', 'LOGNAME', 'LANG')} |
            {'PATH': '/Users/desk/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin'})
        runner = self.runner()
        runner.seams.wake = hw.wake
        with patch('subprocess.Popen', side_effect=OSError('injected Popen failure')):
            self.assertEqual(runner.run(), 0)
        self.assertIn('injected Popen failure', read_json(self.root/'DONE')['wake']['error'])
        self.assertIn('Popen failure', (self.root/'wake.log').read_text())

    def test_census_error_waits_thirty_seconds_and_retries(self):
        runner = self.runner()
        census = runner.seams.census
        calls = []
        def fail_once(directory):
            calls.append(directory)
            if len(calls) == 1: raise RuntimeError('bad census')
            return census(directory)
        runner.seams.census = fail_once
        record = {'census': [], 'waits': []}
        runner.clean_agents(self.root, record)
        self.assertFalse(record['census'][0]['clean'])
        self.assertIn('bad census', record['census'][0]['error'])
        self.assertEqual(record['waits'][0]['hazard'], 'agents')
        self.assertAlmostEqual((record['waits'][0]['end']['monotonic_raw_ns']-
                               record['waits'][0]['start']['monotonic_raw_ns'])/1e9, 30*.001)

    def test_git_timeout_and_nonzero_are_recorded(self):
        hw = Hardware(REPO, sys.executable)
        for failure in (subprocess.TimeoutExpired(['git'], 10), OSError('git missing')):
            with patch('subprocess.run', side_effect=failure):
                code = hw.code()
            self.assertIsNone(code['git_commit'])
            self.assertIsNone(code['dirty'])
            self.assertIn(type(failure).__name__, code['git_error'])
        with patch('subprocess.run', return_value=subprocess.CompletedProcess(['git'], 128, b'', b'bad git')):
            self.assertIn('exit 128', hw.code()['git_error'])

    def test_unexpected_test_error_records_traceback_and_continues(self):
        runner = self.runner()
        runner.plans = (BY_ID['m4-contention-watts'], BY_ID['m9-time-server'])
        test = runner.test
        def fail(plan, **kw):
            if plan.test_id == 'm4-contention-watts': raise RuntimeError('outside _test handler')
            return test(plan, **kw)
        runner.test = fail
        self.assertEqual(runner.run(), 0)
        self.assertIn('m9-time-server', read_json(self.root/'DONE')['complete_tests'])
        info = read_json(self.root/'m4-contention-watts/attempts/1/attempt.json')
        self.assertEqual(info['state'], 'incomplete')
        self.assertIn('outside _test handler', info['traceback'])
        self.assertEqual(len(self.hw.wakes), 1)

    def test_persistent_preflight_census_error_reaches_done_and_wake_at_deadline(self):
        runner = self.runner()
        runner.deadline_hours = .001
        runner.plans = (BY_ID['m9-time-server'], BY_ID['m5-gpu-rail'])
        census = runner.seams.census
        def fail_after_first_test(directory):
            if (self.root/'m9-time-server/result.json').exists(): raise RuntimeError('persistent census failure')
            return census(directory)
        runner.seams.census = fail_after_first_test
        self.assertEqual(runner.run(), 0)
        done = read_json(self.root/'DONE')
        self.assertEqual(done['complete_tests'], ['m9-time-server'])
        self.assertEqual(len(self.hw.wakes), 1)
        rows = read_json_lines(self.root/'journal.jsonl')
        self.assertTrue(any('persistent census failure' in str(row.get('reading')) for row in rows))

    def test_broken_census_ends_job_after_twenty_reads_not_at_deadline(self):
        runner = self.runner()
        runner.deadline_hours = 48.
        runner.plans = (BY_ID['m9-time-server'], BY_ID['m5-gpu-rail'])
        census = runner.seams.census
        failures = []
        def fail_after_first_test(directory):
            if (self.root/'m9-time-server/result.json').exists():
                failures.append(directory)
                raise RuntimeError('census broken')
            return census(directory)
        runner.seams.census = fail_after_first_test
        self.assertEqual(runner.run(), 0)
        done = read_json(self.root/'DONE')
        self.assertEqual(len(failures), 20)
        self.assertIn('20 consecutive reads', done['end_reason'])
        self.assertEqual(done['complete_tests'], ['m9-time-server'])
        self.assertEqual(len(self.hw.wakes), 1)
        info = read_json(self.root/'m5-gpu-rail/attempts/1/attempt.json')
        self.assertEqual(info['state'], 'interrupted')

    def test_code_exception_outside_collection_handler_still_done_and_wake(self):
        runner = self.runner()
        code = runner.seams.code
        runner.plans = (BY_ID['m9-time-server'], BY_ID['m5-gpu-rail'])
        def fail_model(model):
            if model: raise subprocess.TimeoutExpired(['git'], 10)
            return code(model)
        runner.seams.code = fail_model
        self.assertEqual(runner.run(), 0)
        self.assertTrue((self.root/'DONE').exists())
        self.assertEqual(len(self.hw.wakes), 1)
        info = read_json(self.root/'m5-gpu-rail/attempts/1/attempt.json')
        self.assertIn('TimeoutExpired', info['reason'])
        self.assertIn('TimeoutExpired', info['traceback'])

    def test_last_resort_and_final_clock_exception_still_done_and_one_wake(self):
        runner = self.runner()
        runner.seams.action = Mock(side_effect=RuntimeError('unexpected action'))
        runner._final_clock = Mock(side_effect=RuntimeError('bad final clock'))
        self.assertEqual(runner.run(), 0)
        self.assertIn('bad final clock', read_json(self.root/'DONE')['final_clock_error']['error'])
        journal = read_json_lines(self.root/'journal.jsonl')
        event = next(r for r in journal if r.get('event') == 'unexpected_exception')
        self.assertIn('unexpected action', event['traceback'])
        self.assertEqual(len(self.hw.wakes), 1)

    def test_cleanup_exception_still_records_done_and_one_wake(self):
        runner = self.runner()
        runner.seams.cleanup = Mock(side_effect=RuntimeError('bad cleanup'))
        self.assertEqual(runner.run(), 0)
        self.assertIn('bad cleanup', read_json(self.root/'DONE')['cleanup_error']['error'])
        self.assertEqual(len(self.hw.wakes), 1)

    def test_plumbing_clock_wait_covers_scaled_span_plus_sample_slack(self):
        runner = self.runner()
        self.assertEqual(runner.plumbing('m3-clock-rate', .01), 0)
        self.assertAlmostEqual(self.hw.time, 10800*.01+15)


class PrecisionTests(unittest.TestCase):
    def test_scheduled_bursts_fit_wholly_inside_accounting_segments(self):
        bursts = [s for s in BY_ID['m4-contention-watts'].segments if s['kind'] == 'burst']
        self.assertEqual(len(bursts), 20)
        for burst in bursts:
            self.assertGreaterEqual(burst['duration_s'], burst['placement_s']+burst['burst_s'])

    def test_m3_step_residual_accounts_for_fitted_slope(self):
        rows = []
        for i in range(1200):
            t = i*10_000_000_000
            rows.append({'boot_session_uuid': 'boot', 'anchor': {'monotonic_raw_ns': t,
                'realtime_ns': 1_790_000_000_000_000_000+t+30_000*i+(2_000_000 if i >= 600 else 0)}})
        out = analysis.m3({'clock': rows})['segments'][0]
        # Closed form for the OLS slope absorbed from a halfway step on
        # 2m uniformly spaced points: 3*m*step/[dt*(4*m*m-1)].
        extra_slope = 3*600*.002/(10*(4*600**2-1))
        self.assertAlmostEqual(out['residual_step_max']['value'], (.002-10*extra_slope)*1000, places=9)

    def test_m13_edge_sd_capture_se_paired_lags_and_bound(self):
        # Per-capture lags [0,80] ms: SD=sqrt(3200), SE=40 ms.
        # Pooling eight edges lowers SE below 30 ms, but SD stays above it.
        edges = [{'capture': f'c{c}', 'command_s': 0., 'meter_s': lag/1000,
                  'sampler_s': sampler/1000}
                 for c in range(4) for lag, sampler in [(0., 10.), (80., 30.)]]
        out = analysis.m13({'edges': edges})
        expected_sd = math.sqrt(8*40**2/7)
        self.assertAlmostEqual(out['meter_lag_sd']['value'], expected_sd)
        self.assertAlmostEqual(out['meter_mean_lag_pooled_se']['value'], expected_sd/math.sqrt(8))
        self.assertFalse(out['precision_below_typical_bound'])
        for capture in out['meter_lag_by_capture']:
            self.assertEqual(capture['n'], 2)
            self.assertAlmostEqual(capture['mean_lag_se']['value'], 40.)
        paired = out['meter_minus_sampler']
        self.assertEqual(paired['n'], 8)
        self.assertEqual(paired['mean']['value'], 20.)
        self.assertAlmostEqual(paired['sd']['value'], math.sqrt(8*30**2/7))
        self.assertIn('earliest-arrival offset', out['interpretation'])

