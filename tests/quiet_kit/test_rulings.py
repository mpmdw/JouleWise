import math
from pathlib import Path
import statistics
import tempfile
import unittest
from unittest.mock import patch

from joulewise.quiet_kit import analysis
from joulewise.quiet_kit.collectors import model_config, WORKLOADS
from joulewise.quiet_kit.paths import atomic_json, read_json
from joulewise.quiet_kit.readers import run_bundle
from joulewise.quiet_kit.runner import Runner
from joulewise.quiet_kit.schedule import BY_ID, PLANS
from .collector_fakes import CollectorHardware, FakeChild
from .fixtures import plist_stream, EPOCH

REPO = Path(__file__).resolve().parents[2]


class RuledScheduleTests(unittest.TestCase):
    def test_palindrome_and_short_baseline_plan_estimates(self):
        m10 = BY_ID['m10-rails-vs-wall']
        self.assertIsNone(m10.ruling_required)
        for repeat in range(2):
            segments = [s for s in m10.segments if s['repeat'] == repeat]
            self.assertEqual([s['kind'] for s in segments],
                ['idle','cpu','idle','gpu','idle','mixed','idle','mixed','idle','gpu','idle','cpu','idle'])
            self.assertEqual(sum(s['duration_s'] for s in segments), 1140)
            self.assertTrue(all(s.get('duty') == 1. for s in segments if s['kind'] != 'idle'))
        self.assertEqual(m10.estimate_s, 2*1140+300)
        m2b = BY_ID['m2b-short-baseline']
        ids = [p.test_id for p in PLANS]
        self.assertEqual(ids[ids.index('m2-long-wait')+1], 'm2b-short-baseline')
        self.assertEqual([s['arm'] for s in m2b.segments], list('NSSN'*5))
        self.assertEqual(m2b.estimate_s, 20*150+300)
        self.assertTrue(all(s.get('sampling_idle_seconds') == 50. for s in m2b.segments if s['arm'] == 'S'))
        self.assertTrue(all('sampling_idle_seconds' not in s for s in m2b.segments if s['arm'] == 'N'))

    def test_S_config_has_exactly_one_additional_change(self):
        before = read_json(REPO/WORKLOADS['R'])
        short = model_config(REPO, 'R', 'qk-short', short_baseline=True)
        self.assertEqual(short['sampling']['idle_seconds'], 50.)
        short['run_id'] = before['run_id']
        short['run_metadata']['tags'] = before['run_metadata']['tags']
        short['sampling']['idle_seconds'] = before['sampling']['idle_seconds']
        self.assertEqual(short, before)
        self.assertEqual(model_config(REPO, 'R', 'qk-normal')['sampling']['idle_seconds'], 57.6)

    def test_short_baseline_quad_arithmetic_and_interval_independent(self):
        runs = []
        for quad, difference in enumerate([.1, .2, .3, .4, .5]):
            # A linear drift [-.3,-.1,.1,.3] cancels inside each N/S/S/N quad.
            for i, (arm, drift) in enumerate(zip('NSSN', [-.3,-.1,.1,.3])):
                energy = 10+drift+(difference if arm == 'S' else 0)
                runs.append({'id':f'q{quad}-{i}', 'quad':quad, 'arm':arm, 'returncode':0,
                             'phase_energy_j':{'prefill':energy, 'decode':2*energy}})
        out = analysis.m2b({'runs':runs})
        expected_se = math.sqrt((.04+.01+0+.01+.04)/4/5)
        for phase, factor in [('prefill',1.), ('decode',2.)]:
            measured = out['phases'][phase]['short_minus_ordinary']
            self.assertAlmostEqual(measured['value'], .3*factor)
            self.assertAlmostEqual(measured['uncertainty']['standard_error'], expected_se*factor)
            self.assertAlmostEqual(measured['uncertainty']['value'][0], (.3-2.776*expected_se)*factor)
            self.assertAlmostEqual(measured['uncertainty']['value'][1], (.3+2.776*expected_se)*factor)
            self.assertAlmostEqual(out['phases'][phase]['percent']['value'], 3.)
            self.assertAlmostEqual(out['phases'][phase]['percent']['uncertainty']['value'][0],
                                   100*(.3-2.776*expected_se)/10)
        self.assertIsNone(out['incomplete_reason'])
        runs[1]['failure_reasons'] = [{'reason':'idle_admission_failed'}]
        runs[1]['returncode'] = 1
        refused = analysis.m2b({'runs':runs})
        self.assertEqual(refused['incomplete_reason'], 'short_baseline_refused_by_run_path')
        self.assertEqual(refused['short_baseline_refusals'][0]['run'], 'q0-1')
        self.assertIsNone(refused['phases']['prefill']['short_minus_ordinary']['value'])
        self.assertEqual(refused['phases']['prefill']['complete_quad_count'], 4)

    def test_delivered_idle_baseline_is_sum_of_raw_record_durations(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-short-raw-') as tmp:
            attempt = Path(tmp)
            raw = attempt/'runs/qk-short/raw'
            raw.mkdir(parents=True)
            durations = [.1305, .132, .129, .131]
            cursor, records = EPOCH, []
            for duration in durations:
                records.append({'start_s':cursor,'end_s':cursor+duration,'cpu_power':.05,'gpu_power':0.,'ane_power':0.})
                cursor += duration
            (raw/'powermetrics_idle.plist').write_bytes(plist_stream(records))
            atomic_json(raw.parent/'summary_metrics.json', {'status':'succeeded','phase_energy_j':{'prefill':10.}})
            row = run_bundle(attempt, {'bundle':'runs/qk-short','returncode':0,'sampling_idle_seconds':50.})
            self.assertAlmostEqual(row['idle_baseline_delivered_s'], sum(durations), places=6)
            self.assertEqual(row['idle_baseline_record_count'],4)
            self.assertIsNone(row['idle_baseline_undefined'])
            self.assertEqual(row['failure_reasons'],[])

    def test_m10_palindrome_level_means_cancel_linear_drift(self):
        segments, cursor = [], 0.
        for i, spec in enumerate(BY_ID['m10-rails-vs-wall'].segments):
            mid = cursor+spec['duration_s']/2
            drift_time = mid-(570+1140*spec['repeat'])
            base = {'idle':1., 'cpu':2., 'gpu':4., 'mixed':6.}[spec['kind']]
            segments.append({**spec,'id':f's{i}', 'battery_current_ma':[0.],
                'records':[{'total':base+.001*drift_time,'meter':3+2.5*base+.01*drift_time}]*2})
            cursor += spec['duration_s']
        out = analysis.m10({'segments':segments})
        self.assertEqual(len(out['palindrome_level_means']),8)
        for row in out['palindrome_level_means']:
            base = {'idle':1., 'cpu':2., 'gpu':4., 'mixed':6.}[row['level']]
            self.assertAlmostEqual(row['rails']['value'],base)
            self.assertAlmostEqual(row['meter']['value'],3+2.5*base)
            self.assertEqual(row['segment_count'],7 if row['level']=='idle' else 2)
        fit = out['palindrome_charger_supplied_fit']
        self.assertAlmostEqual(fit['slope']['value'],2.5)
        self.assertAlmostEqual(fit['intercept']['value'],3.)
        self.assertEqual(fit['slope']['uncertainty']['n'],8)
        self.assertNotAlmostEqual(out['charger_supplied_fit']['slope']['value'],2.5,places=5)
        # One assisted segment excludes its entire paired level from the
        # charger-supplied means fit, while retaining it on the labelled line.
        bad = next(s for s in segments if s['repeat']==1 and s['kind']=='gpu')
        bad['battery_current_ma'] = [250.]
        excluded = analysis.m10({'segments':segments})
        self.assertEqual(excluded['palindrome_charger_supplied_fit']['slope']['uncertainty']['n'],7)
        self.assertEqual(excluded['palindrome_all_levels_fit']['slope']['uncertainty']['n'],8)
        pair = next(r for r in excluded['palindrome_level_means'] if r['repeat']==1 and r['level']=='gpu')
        self.assertFalse(pair['charger_supplied'])
        segments.remove(bad)
        incomplete = analysis.m10({'segments':segments})
        pair = next(r for r in incomplete['palindrome_level_means'] if r['repeat']==1 and r['level']=='gpu')
        self.assertIsNone(pair['meter']['value'])

    def test_controller_S_refusal_retains_all_exit_statuses_and_marks_incomplete(self):
        original = FakeChild.__init__
        def fail_short(child, manager, pid, argv, directory):
            original(child, manager, pid, argv, directory)
            if 'joulewise' in argv and 'run' in argv:
                config = read_json(Path(argv[argv.index('run')+1]))
                if config['sampling']['idle_seconds'] == 50.:
                    bundle = Path(argv[argv.index('--runs-dir')+1])/config['run_id']
                    atomic_json(bundle/'summary_metrics.json', {'status':'failed',
                        'failure_reason':'idle_admission_failed','phase_energy_j':{}})
                    child.returncode = 1
                    child.quiet_kit_stderr.write_text('idle baseline rejected by run path')
        with tempfile.TemporaryDirectory(prefix='quiet-kit-short-refusal-') as tmp:
            root = Path(tmp)
            hw = CollectorHardware(scale=.001)
            with patch.object(FakeChild, '__init__', fail_short):
                runner = Runner(REPO, root, '/fake/model-python', hw.seams(), plans=(BY_ID['m2b-short-baseline'],),
                                scale=.001, emit=lambda _:None)
                self.assertEqual(runner.run(),0)
            done = read_json(root/'DONE')
            self.assertEqual(done['incomplete_tests'][0]['last_reason'],'short_baseline_refused_by_run_path')
            result = read_json(root/'m2b-short-baseline/attempts/2/analysis.result.json')
            self.assertFalse(result['complete'])
            self.assertEqual(len(result['measured']['run_table']),20)
            self.assertEqual(len(result['measured']['short_baseline_refusals']),10)
            rows = result['measured']['run_table']
            self.assertEqual([r['returncode'] for r in rows],[0,1,1,0]*5)
            for row in rows:
                config = read_json(root/'m2b-short-baseline/attempts/2/configs'/f"{row['id']}.json")
                self.assertEqual(row['sampling_idle_seconds'],50. if row['arm']=='S' else 57.6)
                self.assertEqual(config['sampling']['idle_seconds'],row['sampling_idle_seconds'])
            self.assertIn('idle_admission_failed',str(result['measured']['short_baseline_refusals']))
            self.assertIn('idle baseline rejected by run path',str(result['measured']['short_baseline_refusals']))

    def test_S_launch_error_and_timeout_are_retained_as_run_path_failures(self):
        for failure in ('spawn', 'timeout'):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory(prefix='quiet-kit-short-errors-') as tmp:
                root = Path(tmp)
                hw = CollectorHardware(scale=.001)
                spawn, wait = hw.processes.spawn, hw.processes.wait
                def short(argv):
                    return 'joulewise' in argv and 'run' in argv and read_json(
                        Path(argv[argv.index('run')+1]))['sampling']['idle_seconds'] == 50.
                def fail_spawn(argv, directory, **kw):
                    if failure == 'spawn' and short(argv): raise OSError('injected launch failure')
                    return spawn(argv, directory, **kw)
                def fail_wait(child, control, timeout=3600):
                    if failure == 'timeout' and short(child.argv): raise TimeoutError('injected controller timeout')
                    return wait(child, control, timeout=timeout)
                hw.processes.spawn, hw.processes.wait = fail_spawn, fail_wait
                runner = Runner(REPO, root, '/fake/model-python', hw.seams(), plans=(BY_ID['m2b-short-baseline'],),
                                scale=.001, emit=lambda _:None)
                self.assertEqual(runner.run(),0)
                result = read_json(root/'m2b-short-baseline/attempts/2/analysis.result.json')
                self.assertEqual(result['incomplete_reason'],'short_baseline_refused_by_run_path')
                self.assertEqual(len(result['measured']['short_baseline_refusals']),10)
                shorts = [r for r in result['measured']['run_table'] if r['arm']=='S']
                self.assertTrue(all(r['run_path_error'] for r in shorts))
                self.assertTrue(all(r['returncode'] == (-15 if failure=='timeout' else None) for r in shorts))
                self.assertTrue(all(c.returncode is not None for c in hw.processes.children))
