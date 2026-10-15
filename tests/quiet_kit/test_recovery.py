import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.quiet_kit.paths import append, read_json
from joulewise.quiet_kit.processes import CHILD_SCHEMA, Processes
from joulewise.quiet_kit.runner import Runner
from .fakes import FakeHardware
from .test_runner import SHORT, REPO


class RestartRecoveryTests(unittest.TestCase):
    def test_only_matching_birth_and_boot_can_be_reaped(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-recovery-') as tmp:
            root=Path(tmp)
            expected={'pid':4242,'start_time':'born.123456','boot_session_uuid':'boot'}
            journal=root/'children.jsonl'
            append(journal,{'schema':CHILD_SCHEMA,'event':'spawn','pid':4242,'pgid':4242,'identity':expected})
            manager=Processes(root,identity_reader=lambda pid:expected)
            with patch.object(manager,'stop',return_value=[{'pgid':4242,'gone':True}]) as stop:
                rows=manager.recover(root)
            self.assertTrue(rows[0]['gone'])
            self.assertTrue(stop.called)
            self.assertEqual(manager.recover(root),[])

    def test_reused_pid_is_never_signalled_and_unreadable_identity_blocks(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-recovery-') as tmp:
            root=Path(tmp)
            expected={'pid':4242,'start_time':'old','boot_session_uuid':'boot'}
            append(root/'children.jsonl',{'schema':CHILD_SCHEMA,'event':'spawn','pid':4242,'pgid':4242,'identity':expected})
            manager=Processes(root,identity_reader=lambda pid:{**expected,'start_time':'new'})
            with patch('os.killpg',side_effect=AssertionError('PID reuse signal')):
                rows=manager.recover(root)
            self.assertTrue(rows[0]['gone'])
            self.assertIn('replacement not signalled',rows[0]['reason'])
            append(root/'children.jsonl',{'schema':CHILD_SCHEMA,'event':'spawn','pid':4243,'pgid':4243,'identity':expected})
            def unavailable(pid):raise OSError('kernel inventory unavailable')
            manager.identity_reader=unavailable
            with patch('os.killpg',side_effect=AssertionError('unverified signal')):
                rows=manager.recover(root)
            self.assertTrue(rows[0]['blocking'])

    def test_recorded_stop_is_not_recovered_and_dead_leader_is_proven_gone(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-recovery-') as tmp:
            root=Path(tmp)
            append(root/'children.jsonl',{'schema':CHILD_SCHEMA,'event':'spawn','pid':4242,'pgid':4242,'identity':{}})
            manager=Processes(root,identity_reader=lambda pid:None)
            with patch('joulewise.hazards.instrument.group_absent',return_value=(True,[])):
                self.assertTrue(manager.recover(root)[0]['gone'])
                self.assertEqual(manager.recover(root),[])

    def test_resume_recovers_before_test_three_and_preserves_complete_results(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-recovery-') as tmp:
            root=Path(tmp)/'archive'
            hw=FakeHardware()
            make=lambda plans,seams:Runner(REPO,root,'/fake/model-python',seams,plans=plans,scale=.01,emit=lambda _:None)
            self.assertEqual(make(SHORT[:2],hw.seams()).run(),0)
            previous=[(root/p.test_id/'result.json').read_bytes() for p in SHORT[:2]]
            orphan=root/SHORT[2].test_id/'attempts/1'
            orphan.mkdir(parents=True)
            (orphan/'attempt.json').write_text('{"state":"started","job_id":"old"}')
            seams=hw.seams()
            recovered=[]
            def recover(path):
                recovered.append(path)
                return [{'gone':True,'blocking':False,'pid':4242}]
            seams.recover=recover
            collect=hw.collect
            def after_recovery(*args):
                self.assertTrue(recovered)
                return collect(*args)
            seams.collect=after_recovery
            self.assertEqual(make(SHORT,seams).run(),0)
            for p,raw in zip(SHORT[:2],previous):self.assertEqual((root/p.test_id/'result.json').read_bytes(),raw)
            self.assertTrue((root/SHORT[2].test_id/'attempts/2').is_dir())

    def test_unverified_orphan_writes_done_and_wakes_without_new_collection(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-recovery-') as tmp:
            root=Path(tmp)/'archive'
            root.mkdir()
            (root/'WAKE_CMD').write_text('wake-for-recovery')
            hw=FakeHardware()
            seams=hw.seams()
            seams.recover=lambda path:[{'blocking':True,'reason':'identity unmeasured','pid':4242}]
            runner=Runner(REPO,root,'/fake/model-python',seams,plans=SHORT,scale=.01,emit=lambda _:None)
            self.assertEqual(runner.run(),0)
            self.assertFalse(hw.collected)
            self.assertEqual(hw.wakes,['wake-for-recovery'])
            self.assertTrue(all(r['last_reason']=='recovery_needs_director' for r in read_json(root/'DONE')['incomplete_tests']))

    def test_clock_logger_exits_on_parent_death_without_sampling(self):
        from joulewise.quiet_kit import clocklog
        with tempfile.TemporaryDirectory(prefix='quiet-kit-recovery-') as tmp:
            out=Path(tmp)/'clock.jsonl'
            with (patch.object(clocklog.os,'getppid',return_value=1),
                  patch.object(clocklog.signal,'signal'),
                  patch('joulewise.hazards.clock.sample',side_effect=AssertionError('orphan sampled'))):
                self.assertEqual(clocklog.main(['--out',str(out),'--parent-pid','4242']),0)
            self.assertFalse(out.exists())

    def test_unrelated_journal_is_not_process_ownership_authority(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-recovery-') as tmp:
            root=Path(tmp)
            append(root/'children.jsonl',{'event':'spawn','pid':4242,'pgid':4242,'identity':{'start_time':'other'}})
            def forbidden(pid):raise AssertionError('unowned journal was inspected')
            self.assertEqual(Processes(root,identity_reader=forbidden).recover(root),[])

    def test_dead_leader_with_root_member_is_recorded_without_signalling(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-recovery-root-') as tmp:
            root = Path(tmp)
            append(root/'children.jsonl',{'schema':CHILD_SCHEMA,'event':'spawn','pid':4242,'pgid':4242,'identity':{}})
            member = {'pid':4243,'uid':0,'argv':'fixture sampler','pgid':4242}
            manager = Processes(root,identity_reader=lambda pid:None,member_reader=lambda pgid:[member])
            with (patch('joulewise.hazards.instrument.group_absent',return_value=(False,['4243 fixture sampler'])),
                  patch('os.killpg',side_effect=AssertionError('dead leader is not signal authority')),
                  patch('os.kill',side_effect=AssertionError('unverified root was signalled'))):
                rows = manager.recover(root)
            self.assertTrue(rows[0]['blocking'])
            self.assertEqual(rows[0]['director_actions'],[{'director_action':'root_sampler_orphan',**member,'group':4242}])
