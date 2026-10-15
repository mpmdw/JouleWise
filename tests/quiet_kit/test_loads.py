from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.quiet_kit import loads


class LoadSeamTests(unittest.TestCase):
    def test_reports_whole_child_resource_time_and_load_time_separately(self):
        usage=[SimpleNamespace(ru_utime=1.,ru_stime=.5),SimpleNamespace(ru_utime=5.,ru_stime=1.5)]
        with (patch.object(loads.resource,'getrusage',side_effect=usage),
              patch.object(loads.time,'monotonic',side_effect=[0.,1.,1.]),
              patch.object(loads.time,'clock_gettime_ns',side_effect=[10,20])):
            result=loads.run('cpu',0.,.05,0.)
        self.assertEqual(result['cpu_seconds'],6.5)
        self.assertEqual(result['load_cpu_seconds'],5.)
        self.assertEqual(result['start_raw_ns'],10)
        self.assertEqual(result['end_raw_ns'],20)

    def test_invalid_parameters_fail_before_any_load(self):
        for duty,period,duration in [(-.1,.05,1.),(1.1,.05,1.),(.5,0.,1.),(.5,.05,-1.)]:
            with self.subTest(duty=duty),self.assertRaises(ValueError):
                loads.run('cpu',duty,period,duration)
