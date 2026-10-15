import dataclasses
import gzip
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from joulewise.quiet_kit.collectors import Sampler


class SamplerCompositionTests(unittest.TestCase):
    def test_adapter_argv_anchor_deriver_and_raw_capture_are_reused(self):
        from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter, SAMPLERS
        from joulewise.clock import ClockStamp
        fixture=Path(__file__).resolve().parents[1]/'fixtures/controller_g2b/block3-pre'
        raw=gzip.decompress((fixture/'raw/powermetrics.plist.gz').read_bytes())
        evidence=json.loads(gzip.decompress((fixture/'instrument_evidence.json.gz').read_bytes()))
        stamps={k:ClockStamp(**v) for k,v in evidence['clock_anchor']['clock_stamps'].items()}
        with tempfile.TemporaryDirectory(prefix='quiet-kit-sampler-') as tmp:
            out=Path(tmp)
            commands=[]
            def spawn(argv,directory):
                commands.append(argv)
                Path(argv[argv.index('-o')+1]).write_bytes(raw)
                return SimpleNamespace(pid=4242)
            hw=SimpleNamespace(processes=SimpleNamespace(spawn=spawn,stop=lambda p:[{'pgid':p.pid,'gone':True}]))
            fake_clock=SimpleNamespace(stamp=__import__('unittest').mock.Mock(side_effect=[stamps[k] for k in
                ('pre_spawn','sampling_started','sampling_stopped','post_parse')]))
            def ready(adapter,*_):
                adapter._first_parse_stamp=stamps['first_parse']
                return SimpleNamespace(ok=True)
            with (patch('joulewise.clock.SystemClock',return_value=fake_clock),
                  patch('joulewise.quiet_kit.collectors.stamp',return_value={'epoch_s':stamps['pre_spawn'].epoch_s,'raw_s':10.}),
                  patch.object(PowermetricsTelemetryAdapter,'_wait_until_ready',ready),
                  patch.object(PowermetricsTelemetryAdapter,'_wait_for_native_rollover',return_value=SimpleNamespace(ok=True))):
                sampler=Sampler(hw,out,None)
                report=sampler.close()
            self.assertEqual(commands[0][:3],['/usr/bin/sudo','-n','/usr/bin/powermetrics'])
            self.assertEqual(commands[0][commands[0].index('--samplers')+1],SAMPLERS)
            self.assertEqual(commands[0][commands[0].index('-i')+1],'100')
            self.assertEqual((out/'powermetrics.plist').read_bytes(),raw)
            self.assertEqual(report['clock_anchor']['method'],evidence['clock_anchor']['method'])
            self.assertAlmostEqual(report['first_record_endpoint_s'],evidence['clock_anchor']['first_sample_end_point_epoch_s'])
