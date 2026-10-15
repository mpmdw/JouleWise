from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from joulewise.quiet_kit.processes import Processes


class ProcessOwnershipTests(unittest.TestCase):
    def test_imported_probe_children_are_owned_and_cancellation_reaps_them(self):
        from joulewise.quiet_kit.hardware import Hardware
        with tempfile.TemporaryDirectory(prefix='quiet-kit-probes-') as tmp:
            root=Path(tmp)
            hw=Hardware(root,'/fake/model-python')
            hw.now=lambda:0.
            out,err=root/'stdout',root/'stderr'
            out.write_bytes(b'partial probe output')
            err.write_bytes(b'')
            child=SimpleNamespace(pid=42420,returncode=-15,quiet_kit_stdout=out,quiet_kit_stderr=err,poll=lambda:None)
            hw.bind_cancel(lambda:True)
            with (patch.object(hw.processes,'spawn',return_value=child),
                  patch.object(hw.processes,'stop',return_value=[{'pgid':42420,'gone':True}]) as stop):
                completed=hw._owned_probe(['/fake/probe'],10.,root)
            self.assertEqual(completed.error,'probe cancelled')
            self.assertEqual(completed.stdout,b'partial probe output')
            self.assertTrue(stop.called)

    def test_teardown_kills_owned_descendant_groups_and_proves_absence(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-groups-') as tmp:
            manager=Processes(Path(tmp))
            child=SimpleNamespace(pid=42420,returncode=0,wait=lambda timeout:0)
            manager.processes[child.pid]=(child,'test',Path(tmp))
            rows={(42421,'born'):{'pid':42421,'ppid':42420},
                  (1,'system'):{'pid':1,'ppid':0}}
            with (patch('joulewise.hazards.contention.take_snapshot',return_value=SimpleNamespace(rows=rows,error=None)),
                  patch('os.getpgid',side_effect=lambda pid:{42420:42420,42421:42421}[pid]),
                  patch('os.getpgrp',return_value=123),patch('os.killpg') as kill,
                  patch('joulewise.hazards.instrument.group_absent',return_value=(True,[])) as census):
                evidence=manager.stop(child)
            self.assertEqual({a.args[0] for a in kill.call_args_list},{42420,42421})
            self.assertEqual({a.args[0] for a in census.call_args_list},{42420,42421})
            self.assertTrue(all(e['gone'] for e in evidence))
            self.assertFalse(manager.processes)

    def test_cleanup_cannot_kill_job_wide_logger_or_rekill_reaped_pid(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-groups-') as tmp:
            manager=Processes(Path(tmp))
            logger=SimpleNamespace(pid=42420)
            manager.processes[logger.pid]=(logger,'job',Path(tmp))
            with patch('os.killpg',side_effect=AssertionError('unowned signal')):
                self.assertEqual(manager.cleanup(role='test'),[])
                self.assertTrue(manager.stop(SimpleNamespace(pid=99999))[0]['already_reaped'])
