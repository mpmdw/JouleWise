"""Span adapters preserve pass-1 integration and the reader's native rows."""
import copy
from decimal import Decimal
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.b6 import calibration
from joulewise.bytes_stream_capture import write, read
from joulewise.external import km003c_parse as kp
from scripts import bytes_stream_harvest as h
from scripts import bytes_stream_test as bt
from tests.test_bytes_stream_capture import write_meter


class HarvestTests(unittest.TestCase):
    def test_native_support_integral_and_anchor_envelope(self):
        # Compare identical governed functions on identical inputs: exact is
        # appropriate here, not an approximate test of a new estimator.
        from joulewise.bundle_read import TracePoint, Window
        from joulewise.reduce import _integrate, _anchor_shift_envelope
        rows=[dict(start_ns=i*10**8,end_ns=(i+1)*10**8,power_w=2+i%3) for i in range(100)]
        span=(123456789,9123456789)
        actual,env=h.rail_energy(rows,span,.03)
        curve=[TracePoint((r['end_ns']-span[0])/1e9,r['power_w'],
                          (r['start_ns']-span[0])/1e9,(r['end_ns']-span[0])/1e9) for r in rows]
        window=Window(0,(span[1]-span[0])/1e9)
        self.assertEqual(actual,_integrate(curve,window.start_s,window.end_s))
        self.assertEqual(env,_anchor_shift_envelope([(curve,[window])],.03)['max_abs_delta_j'])
        self.assertIsNone(h.rail_energy(rows,(-1,9*10**9),.03)[0])
        self.assertIsNone(h.rail_energy(rows,span,None)[1])

    def stream(self,root):
        r={'start_ns':10*10**9,'end_ns':20*10**9,'bytes_per_read':2**32,
           'repeats':10,'duration_s':10}
        path=root/'meter.jsonl'
        write_meter(path,[r],0,30*10**9)
        return kp.parse(path)

    def test_meter_is_already_raw_and_signed_battery_and_gap_survive(self):
        with tempfile.TemporaryDirectory() as tmp:
            stream=self.stream(Path(tmp))
            spans={'pre':(2*10**9,5*10**9),'stream':(10*10**9,20*10**9),'post':(24*10**9,27*10**9)}
            result=h.meter_fields(stream,spans)
            # Identical integrator, identical RAW inputs, not offset twice.
            self.assertEqual(result['energy_j']['meter'],kp.integrate(stream.host_ns,stream.watts,*spans['stream'])[0])
            times,watts=stream.battery_watts()
            self.assertEqual(result['energy_j']['battery'],kp.integrate(times,watts,*spans['stream'])[0])
            self.assertGreater(result['energy_j']['battery'],0)
            self.assertEqual(sum(g['missing_samples'] for g in result['meter_gaps']),2)
            self.assertEqual(result['tau_s'],2.34)  # 2×1 s SMC + 340 ms gap-bearing poll.
            self.assertEqual(result['idle']['pre']['meter'],h.points(stream.host_ns,stream.watts,spans['pre']))
            # Charging is retained signed, never clamped to zero.
            stream.smc=[dict(B0AC=250,B0AV=12000) for _ in stream.smc]
            self.assertLess(h.meter_fields(stream,spans)['energy_j']['battery'],0)

    def test_missing_battery_readings_remain_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            stream=self.stream(Path(tmp))
            stream.smc=[{} for _ in stream.smc]
            spans={'pre':(2*10**9,5*10**9),'stream':(10*10**9,20*10**9),'post':(24*10**9,27*10**9)}
            result=h.meter_fields(stream,spans)
            self.assertIsNone(result['energy_j']['battery'])
            self.assertIsNone(result['battery_edge_j'])
            self.assertEqual(result['battery_samples'],[])

    def test_absent_and_restarted_meter_never_get_silently_refit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            write(root/'SESSION.json',dict(adapter_max_w=140,adapter_source='synthetic',
                calibration_registration={'calibration':dict(alignment_reference_s='.03',acceptance_corpus=[],
                    bracket_screen_s='.01',operative_bound_stop_s=None,max_budgetable_drift_s='.02')}))
            capture=root/'runs_bytes_stream_test/capture'
            write(capture/'SCAN.json',dict(status='knee not found',K=None,reason='synthetic scan refusal'))
            for count in (0,2):
                directory=root/'custody/hazards/meter'
                directory.mkdir(parents=True,exist_ok=True)
                for i in range(count):
                    (directory/f'stream-{i:03d}.jsonl').write_text('{}\n')
                with patch.object(kp,'clock_fit',side_effect=AssertionError('must not fit multiple streams')):
                    out=h.harvest(root)
                self.assertEqual(out['provenance']['meter_stream_count'],count)
                result=bt.read_known_bytes(out['records'],out['scan'])
                self.assertEqual(result['boundaries']['dc']['class'],'UNDETERMINED')


if __name__ == '__main__':
    unittest.main()
