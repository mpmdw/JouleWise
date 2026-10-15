import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.quiet_kit.collectors import model_config, WORKLOADS
from joulewise.quiet_kit.paths import read_json
from joulewise.quiet_kit.runner import Runner
from joulewise.quiet_kit.schedule import PLANS, TestPlan
from .collector_fakes import CollectorHardware

REPO=Path(__file__).resolve().parents[2]


class CollectorChainTests(unittest.TestCase):
    def setUp(self):
        self.live_guards=[]
        for target in ('subprocess.Popen','joulewise.hazards.contention._host_functions',
                       'joulewise.hazards.smc.Reader','joulewise.kernel_clock.read_kernel_frequency'):
            patcher=patch(target,side_effect=AssertionError('unfaked hardware seam: '+target))
            guard=patcher.start()
            self.addCleanup(patcher.stop)
            self.live_guards.append(guard)

    def tearDown(self):
        for guard in self.live_guards:
            guard.assert_not_called()

    def test_full_authorized_schedule_through_hardware_only_seams(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-full-chain-') as tmp:
            hw=CollectorHardware(scale=.001)
            plans=tuple(p for p in PLANS if not p.ruling_required)
            root=Path(tmp)/'archive'
            runner=Runner(REPO,root,'/fake/model-python',hw.seams(),plans=plans,scale=.001,emit=lambda _:None)
            self.assertEqual(runner.run(),0)
            self.assertEqual(read_json(root/'DONE')['incomplete_tests'],[])
            self.assertEqual(len(read_json(root/'DONE')['complete_tests']),len(plans))
            self.assertTrue(all(c.returncode is not None for c in hw.processes.children))

    def test_model_copies_change_only_run_id_and_tags(self):
        for w,path in WORKLOADS.items():
            before=read_json(REPO/path)
            after=model_config(REPO,w,'qk-copy-check')
            self.assertEqual(after['run_id'],'qk-copy-check')
            self.assertNotIn('launch_lineage_required',after['run_metadata']['tags'])
            after['run_id']=before['run_id']
            after['run_metadata']['tags']=before['run_metadata']['tags']
            self.assertEqual(after,before)

    def test_real_segment_executor_sampler_load_meter_model_sntp(self):
        with tempfile.TemporaryDirectory(prefix='quiet-kit-collectors-') as tmp:
            hw=CollectorHardware(scale=.01)
            plans=(TestPlan('m4-contention-watts',(
                {'kind':'idle','duration_s':20}, {'kind':'cpu','duty':.05,'duration_s':20,'priority':'background'},
                {'kind':'idle','duration_s':20}, {'kind':'burst','duration_s':20,'duty':1.,'burst_s':2.,'placement_s':9.4},
                {'kind':'idle','duration_s':10})),
                TestPlan('m14-meter-idle-power',({'kind':'idle','duration_s':20},
                    {'kind':'gpu','duty':.2,'duration_s':20},{'kind':'idle','duration_s':20}),meter=True),
                TestPlan('m2-long-wait',tuple({'kind':'model','workload':'R','quad':0,'arm':arm} for arm in 'NLLN'),model_runs=('R',)*4),
                next(p for p in PLANS if p.test_id=='m9-time-server'))
            root=Path(tmp)/'archive'
            runner=Runner(REPO,root,'/fake/model-python',hw.seams(),plans=plans,scale=.01,emit=lambda _:None)
            self.assertEqual(runner.run(),0)
            self.assertEqual(read_json(root/'DONE')['incomplete_tests'],[])
            m4=read_json(root/'m4-contention-watts/result.json')
            self.assertAlmostEqual(m4['measured']['arms'][0]['watts_per_cpu_rate']['value'],5.,delta=.05)
            argv=read_json(root/'m4-contention-watts/attempts/1/collection.json')['segments'][1]['argv'][0]
            self.assertEqual(argv[:2],['/usr/sbin/taskpolicy','-b'])
            self.assertTrue(m4['measured']['bursts'][0]['accounting_intervals'])
            m2=read_json(root/'m2-long-wait/result.json')
            self.assertEqual(len(m2['measured']['run_table']),4)
            self.assertFalse(hw.sample_active)
            self.assertTrue(all(c.returncode is not None for c in hw.processes.children))
