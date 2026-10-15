from __future__ import annotations

import dataclasses
import fcntl
import hashlib
import json
import signal
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.quiet_kit.cli import complete, main
from joulewise.quiet_kit.paths import atomic_json, read_json
from joulewise.quiet_kit.runner import Runner, Seams
from joulewise.quiet_kit.schedule import PLANS, TestPlan
from .fakes import FakeHardware

REPO = Path(__file__).resolve().parents[2]
SHORT = tuple(TestPlan(p.test_id, (dict(kind='idle',duration_s=2),dict(kind='cpu',duty=.05,duration_s=2),
                                 dict(kind='idle',duration_s=2))) for p in PLANS[:3])


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='quiet-kit-runner-')
        self.root = Path(self.temp.name)/'archive'
        self.addCleanup(self.temp.cleanup)
        self.hw = FakeHardware()

    def runner(self, plans=SHORT, deadline_hours=10):
        return Runner(REPO, self.root, '/fake/model-python', self.hw.seams(), plans=plans,
                      scale=.01, deadline_hours=deadline_hours, emit=lambda _:None)

    def test_full_schedule_production_readers_results_done_wake_once_and_rerun(self):
        self.root.mkdir()
        (self.root/'WAKE_CMD').write_text('director-wake-placeholder')
        plans=tuple(p for p in PLANS if not p.ruling_required)
        self.assertEqual(self.runner(plans).run(), 0)
        self.assertEqual(self.hw.collected, [p.test_id for p in plans if p.test_id!='m3-clock-rate'])
        for p in plans:
            self.assertTrue(complete(self.root,p.test_id), (p.test_id, read_json(self.root/'DONE')))
            result = read_json(self.root/p.test_id/'result.json')
            self.assertEqual(result['schema'], 'joulewise.quiet_kit.result.v1')
            self.assertEqual(result['kind'], 'measurement')
            self.assertTrue(result['raw'])
            self.assertTrue((self.root/p.test_id/'summary.md').read_text().endswith('\n'))
        self.assertEqual(read_json(self.root/'DONE')['incomplete_tests'], [])
        self.assertEqual(len(self.hw.wakes),1)
        self.assertTrue((self.root/'WAKE_DONE').is_file())
        before = list(self.hw.collected)
        self.assertEqual(self.runner(plans).run(), 0)
        self.assertEqual(self.hw.collected,before)
        self.assertEqual(len(self.hw.wakes),1)
        self.assertEqual(self.hw.actions.count('network_time_off'),1)

    def test_signal_during_third_test_resumes_without_touching_first_two(self):
        self.hw.interrupt_test = SHORT[2].test_id
        self.assertEqual(self.runner().run(),128+signal.SIGTERM)
        preserved = {p.test_id:(self.root/p.test_id/'result.json').read_bytes() for p in SHORT[:2]}
        attempt = self.root/SHORT[2].test_id/'attempts/1/attempt.json'
        self.assertEqual(read_json(attempt)['state'],'interrupted')
        self.assertTrue(read_json(attempt)['process_groups'][0]['gone'])
        self.assertEqual(self.runner().run(),0)
        for p in SHORT[:2]:
            self.assertEqual((self.root/p.test_id/'result.json').read_bytes(),preserved[p.test_id])
        self.assertTrue((self.root/SHORT[2].test_id/'attempts/2').is_dir())
        self.assertEqual(self.hw.collected.count(SHORT[0].test_id),1)

    def test_hazards_wait_and_are_in_journal_and_preflight(self):
        self.hw.dirty_census_calls={1,2}
        self.hw.bad_probes={'battery':['REFUSE']}
        self.assertEqual(self.runner(SHORT[:1]).run(),0)
        journal = [json.loads(line) for line in (self.root/'journal.jsonl').read_text().splitlines()]
        self.assertTrue(any(r['hazard']=='agents' for r in journal))
        self.assertTrue(any(r['hazard']=='battery' for r in journal))
        record = read_json(self.root/SHORT[0].test_id/'attempts/1/preflight.json')
        self.assertTrue(any(r['hazard']=='battery' for r in record['waits']))
        self.assertTrue(all('start' in r and 'end' in r and 'verdict_reasons' in r for r in journal))

    def test_agent_mid_test_interrupts_attempt_and_retries_after_clean_wait(self):
        self.hw.agent_in_test = SHORT[0].test_id
        self.assertEqual(self.runner(SHORT[:1]).run(),0)
        self.assertEqual(read_json(self.root/SHORT[0].test_id/'attempts/1/attempt.json')['reason'],'agent')
        self.assertTrue(complete(self.root,SHORT[0].test_id))
        self.assertTrue((self.root/SHORT[0].test_id/'attempts/2').is_dir())
        waits = [json.loads(line)['hazard'] for line in (self.root/'journal.jsonl').read_text().splitlines()]
        self.assertIn('agent_handoff',waits)

    def test_clock_agent_retry_allocates_a_new_attempt_and_keeps_the_logger(self):
        plan=next(p for p in PLANS if p.test_id=='m3-clock-rate')
        watch=self.hw.watch
        census=self.hw.census
        pending=False
        seen=False
        def watched(directory):
            nonlocal pending,seen
            if not seen and directory.parent.parent.name==plan.test_id:
                pending=True
                seen=True
            return watch(directory)
        def censused(directory):
            nonlocal pending
            if pending:
                pending=False
                return {'clean':False,'stdout':'4242 agent','detail':'agent present'}
            return census(directory)
        self.hw.watch=watched
        self.hw.census=censused
        self.assertEqual(self.runner((plan,)).run(),0)
        attempts=self.root/plan.test_id/'attempts'
        self.assertEqual(read_json(attempts/'1/attempt.json')['state'],'interrupted')
        self.assertEqual(read_json(attempts/'1/attempt.json')['reason'],'agent')
        self.assertTrue((attempts/'1/clock.jsonl').is_file())
        self.assertFalse((attempts/'2/clock.jsonl').exists())
        result=read_json(self.root/plan.test_id/'result.json')
        self.assertEqual(result['attempt'],2)
        self.assertTrue(result['complete'])
        self.assertEqual(result['conditions']['clock_sources'][0]['attempt'],1)

    def test_clock_resume_retains_previous_segments_and_updates_stream_budget(self):
        clock=next(p for p in PLANS if p.test_id=='m3-clock-rate')
        meter=TestPlan('m14-meter-idle-power',SHORT[0].segments,meter=True)
        self.hw.meter_present=False
        self.assertEqual(self.runner((clock,meter)).run(),0)
        source=self.root/clock.test_id/'attempts/1'
        previous={p.name:p.read_bytes() for p in source.iterdir() if p.is_file()}
        self.assertTrue(complete(self.root,clock.test_id))
        self.hw.sleep(70.)  # a real gap creates another continuous segment
        self.hw.meter_present=True
        collect=self.hw.collect
        def collect_longer(*args):
            collect(*args)
            attempt=args[1]
            doc=read_json(attempt/'collection.json')
            atomic_json(attempt/'collection.json',{**doc,'sampler_spans_s':[5000.]})
        self.hw.collect=collect_longer
        self.assertEqual(self.runner((clock,meter)).run(),0)
        for name,raw in previous.items():
            self.assertEqual((source/name).read_bytes(),raw,name)
        result=read_json(self.root/clock.test_id/'result.json')
        self.assertTrue(result['complete'])
        self.assertEqual(result['attempt'],2)
        self.assertEqual(len(result['conditions']['clock_sources']),2)
        segments=result['measured']['segments']
        self.assertEqual(len(segments),2)
        self.assertEqual([r['source_attempts'] for r in segments],[[1],[2]])
        self.assertTrue(all(r['budgets'][0]['L_s']==5000. for r in segments))
        self.assertEqual(len(read_json(self.root/'DONE')['incomplete_tests']),0)

    def test_deadline_on_never_clearing_hazard_writes_incomplete_and_wakes(self):
        self.root.mkdir()
        (self.root/'WAKE_CMD').write_text('wake-on-deadline')
        self.hw.dirty_census_calls=set(range(1,10000))
        self.assertEqual(self.runner(deadline_hours=.0001).run(),0)
        done = read_json(self.root/'DONE')
        self.assertEqual(len(done['incomplete_tests']),len(SHORT))
        self.assertEqual(self.hw.wakes,['wake-on-deadline'])
        self.assertFalse(self.hw.collected)

    def test_wall_deadline_advances_when_sleep_blind_monotonic_is_frozen(self):
        self.hw.dirty_census_calls=set(range(1,10000))
        default_now=Seams.__dataclass_fields__['now'].default
        seams=dataclasses.replace(self.hw.seams(),now=default_now)
        calls=0
        def sleep(seconds):
            nonlocal calls
            calls+=1
            if calls>100:
                raise AssertionError('deadline used a sleep-blind clock')
            self.hw.sleep(seconds)
        seams.sleep=sleep
        with (patch('joulewise.quiet_kit.runner.time.monotonic',return_value=0.),
              patch('joulewise.quiet_kit.runner.time.clock_gettime',side_effect=lambda clock_id:self.hw.time)):
            runner=Runner(REPO,self.root,'/fake/model-python',seams,plans=SHORT[:1],scale=.01,
                          deadline_hours=.0001,emit=lambda _:None)
            self.assertEqual(runner.run(),0)
        self.assertTrue(read_json(self.root/'DONE')['incomplete_tests'])

    def test_second_instance_exits_zero_without_starting_children(self):
        self.root.mkdir()
        with (self.root/'.lock').open('a+b') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            self.assertEqual(self.runner().run(),0)
        self.assertFalse(self.hw.actions)
        self.assertFalse(self.hw.collected)

    def test_signal_callback_sets_cancel_without_waiting_in_a_popen_lock(self):
        runner=self.runner()
        runner.seams.cleanup=lambda:self.fail('signal callback reaped a process')
        runner._signal(signal.SIGTERM,None)
        self.assertEqual(runner.stop,'SIGTERM')

    def test_signal_inside_probe_cancellation_does_not_become_a_deadline_wake(self):
        from joulewise.quiet_kit.runner import Deadline
        self.root.mkdir()
        (self.root/'WAKE_CMD').write_text('must-not-wake-on-signal')
        runner=self.runner(SHORT[:1])
        probe=self.hw.probe
        def cancelled(name,directory,parameters):
            if name=='contention':
                runner._signal(signal.SIGTERM,None)
                raise Deadline('stopped during contention dwell')
            return probe(name,directory,parameters)
        runner.seams.probe=cancelled
        self.assertEqual(runner.run(),128+signal.SIGTERM)
        self.assertFalse((self.root/'DONE').exists())
        self.assertFalse(self.hw.wakes)
        attempt=self.root/SHORT[0].test_id/'attempts/1/attempt.json'
        self.assertEqual(read_json(attempt)['state'],'interrupted')
        self.assertEqual(read_json(attempt)['reason'],'SIGTERM')
        self.assertEqual(read_json(self.root/'STATUS.json')['state'],'stopped')

    def test_signal_induced_collector_error_is_an_interruption(self):
        runner=self.runner(SHORT[:1])
        def cancelled(*args):
            runner._signal(signal.SIGINT,None)
            raise RuntimeError('sampler ended after cancellation')
        runner.seams.collect=cancelled
        self.assertEqual(runner.run(),128+signal.SIGINT)
        attempt=self.root/SHORT[0].test_id/'attempts/1/attempt.json'
        self.assertEqual(read_json(attempt)['state'],'interrupted')
        self.assertEqual(read_json(attempt)['reason'],'SIGINT')
        self.assertFalse((self.root/'DONE').exists())

    def test_wake_marker_is_created_before_launch_even_if_launch_fails(self):
        self.root.mkdir()
        (self.root/'WAKE_CMD').write_text('one-shot')
        def wake(content,logfile):
            self.assertTrue((self.root/'WAKE_DONE').is_file())
            raise OSError('simulated launch failure')
        self.hw.wake=wake
        with self.assertRaises(OSError):
            self.runner(SHORT[:1]).run()
        self.hw.wake=lambda *_:self.fail('wake was repeated')
        self.assertEqual(self.runner(SHORT[:1]).run(),0)

    def test_explicit_missing_spec_is_recorded_without_collecting(self):
        plan=TestPlan('m4-contention-watts',(),ruling_required='synthetic missing order')
        self.assertTrue(plan.ruling_required)
        self.assertEqual(self.runner((plan,)).run(),0)
        self.assertFalse(self.hw.collected)
        self.assertIn('needs_ruling',read_json(self.root/'DONE')['incomplete_tests'][0]['last_reason'])

    def test_interrupted_raw_attempt_cannot_be_reanalyzed_as_complete(self):
        self.assertEqual(self.runner(SHORT[:1]).run(),0)
        attempt=self.root/SHORT[0].test_id/'attempts/1'
        atomic_json(attempt/'attempt.json',{**read_json(attempt/'attempt.json'),'state':'interrupted','reason':'agent'})
        result=self.runner(SHORT[:1]).publish(SHORT[0],attempt)
        self.assertFalse(result['complete'])
        self.assertEqual(result['incomplete_reason'],'interrupted: agent')

    def test_collector_crash_cannot_promote_partial_raw_data_on_reanalysis(self):
        collect=self.hw.collect
        def crash(*args):
            collect(*args)
            raise RuntimeError('simulated collection crash')
        self.hw.collect=crash
        self.assertEqual(self.runner(SHORT[:1]).run(),0)
        self.assertFalse(complete(self.root,SHORT[0].test_id))
        self.assertEqual(self.runner(SHORT[:1]).reanalyze(SHORT[0].test_id),1)
        self.assertFalse(complete(self.root,SHORT[0].test_id))

    def test_hard_crash_without_exception_cannot_promote_partial_collection(self):
        from .fixtures import power_attempt
        runner=self.runner(SHORT[:1])
        attempt=runner.new_attempt(SHORT[0].test_id)
        power_attempt(attempt,[{'kind':'idle','power':.05},
                               {'kind':'cpu','power':.3,'duty':.05,'cpu_seconds':.1},
                               {'kind':'idle','power':.05}])
        # SIGKILL can leave a readable, partially flushed manifest but no
        # exception handler or completed endpoint-condition record.
        atomic_json(attempt/'conditions.json',{'start':self.hw.observe(attempt)})
        self.assertEqual(runner.reanalyze(SHORT[0].test_id),1)
        result=read_json(attempt/'analysis.result.json')
        self.assertFalse(result['complete'])
        self.assertEqual(result['incomplete_reason'],'collection_not_finished')
        self.assertFalse(complete(self.root,SHORT[0].test_id))

    def test_three_unmeasured_probes_flag_and_instrument_keeps_waiting(self):
        self.hw.bad_probes={'battery':['UNMEASURED']*3}
        self.assertEqual(self.runner(SHORT[:1]).run(),0)
        record = read_json(self.root/SHORT[0].test_id/'result.json')['conditions']['preflight']
        self.assertTrue(any('3 consecutive' in f['reason'] for f in record['flags']))
        self.hw = FakeHardware()
        self.root = Path(self.temp.name)/'second-archive'
        self.hw.bad_probes={'instrument':['UNMEASURED']*100}
        self.assertEqual(self.runner(SHORT[:1],deadline_hours=.005).run(),0)
        self.assertFalse(complete(self.root,SHORT[0].test_id))
        self.assertGreaterEqual(sum(name=='instrument' for name,_,_ in self.hw.probes),3)

    def test_reanalyze_uses_saved_bytes_without_any_hardware(self):
        self.assertEqual(self.runner(SHORT[:1]).run(),0)
        path = self.root/SHORT[0].test_id/'result.json'
        before = read_json(path)['measured']
        for name in ('census','probe','observe','watch','collect','clock_start','action','wake','code'):
            def forbidden(*_,name=name,**__):
                raise AssertionError(f'reanalyze hardware {name}')
            setattr(self.hw,name,forbidden)
        self.assertEqual(self.runner(SHORT[:1]).reanalyze(SHORT[0].test_id),0)
        self.assertEqual(read_json(path)['measured'],before)

    def test_plumbing_only_touches_own_subdirectory_and_sleeps_no_display(self):
        self.root.mkdir()
        (self.root/'WAKE_CMD').write_text('never-wake')
        atomic_json(self.root/'STATUS.json',{'sentinel':1})
        atomic_json(self.root/'DONE',{'sentinel':2})
        originals = {p.name:p.read_bytes() for p in self.root.iterdir()}
        self.assertEqual(self.runner().plumbing('m5-gpu-rail',.01),0)
        self.assertEqual({p.name:p.read_bytes() for p in self.root.iterdir() if p.is_file()},originals)
        self.assertEqual({p.name for p in self.root.iterdir() if p.is_dir()},{'_plumbing'})
        self.assertNotIn('display_sleep',self.hw.actions)
        self.assertFalse(self.hw.wakes)
        result = next((self.root/'_plumbing').rglob('result.json'))
        self.assertEqual(read_json(result)['kind'],'plumbing_check')
        self.assertTrue(all(record_only for _,_,record_only in self.hw.probes))
        self.assertEqual([d for name,d,_ in self.hw.probes if name in ('contention','instrument','clock')],[20,20,20])

    def test_meter_absent_is_incomplete_and_is_retried_once_on_later_pass(self):
        self.hw.meter_present=False
        plan=next(p for p in PLANS if p.test_id=='m14-meter-idle-power')
        self.assertEqual(self.runner((plan,)).run(),0)
        done=read_json(self.root/'DONE')
        self.assertEqual(done['incomplete_tests'][0]['last_reason'],'meter_absent')
        self.assertEqual(self.hw.collected,[plan.test_id,plan.test_id])
        self.assertFalse(complete(self.root,plan.test_id))

    def test_atomic_completion_and_raw_integrity(self):
        self.assertEqual(self.runner(SHORT[:1]).run(),0)
        result=read_json(self.root/SHORT[0].test_id/'result.json')
        attempt=self.root/SHORT[0].test_id/'attempts/1'
        for raw in result['raw']:
            # attempt state is mutable; primary captures and journals are kept.
            if raw['path'] in ('attempt.json','analysis.result.json'):
                continue
            data=(attempt/raw['path']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(),raw['sha256'])
            self.assertEqual(len(data),raw['size'])
