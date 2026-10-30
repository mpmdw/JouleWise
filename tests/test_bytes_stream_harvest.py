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


def independent_arithmetic(test, archive, record):
    """Independent arithmetic over raw native streams; no producer integrators."""
    import math
    import plistlib
    r, actual = record['receipt'], record['harvest']
    lo, hi = r['start_ns'], r['end_ns']
    duration = (hi-lo)/1e9
    # 5.7e-6 J/GB * this call's payload GB = comparison bar in joules.
    payload_gb = r['bytes_read']/1e9
    tolerance_j = 5.7e-6 * payload_gb
    message = f"5.7e-6 J/GB * {payload_gb} GB = {tolerance_j} J for this call"
    raw = (archive/'runs_bytes_stream_test/capture/raw/powermetrics.plist').read_bytes()
    # Native plist dates have whole-second precision. Use the capture's
    # precise first endpoint, then advance on raw integer elapsed_ns support.
    stop = read(archive/'runs_bytes_stream_test/capture/capture_stop.json')
    end = round((stop['uncertainty_evidence']['clock_anchor']['first_sample_end_point_epoch_s']
                 - 1_000_000)*1e9)
    rails = []
    for chunk in raw.split(b'\0'):
        if not chunk.strip():
            continue
        doc = plistlib.loads(chunk)
        # Synthetic epoch = 1,000,000 + RAW seconds (Capture's source clock).
        if rails:
            end += doc['elapsed_ns']
        start = end-doc['elapsed_ns']
        power = sum(doc['processor'][k] for k in ('cpu_power','gpu_power','ane_power'))/1000
        rails.append(power*max(0,min(hi,end)-max(lo,start))/1e9)
    test.assertAlmostEqual(actual['energy_j']['rails'], math.fsum(rails), delta=tolerance_j, msg=message)
    # Decode raw meter bytes with the governed single clock fit; integrate
    # independently with a direct half-open sample selection and arithmetic mean.
    stream = kp.parse(next((archive/'custody/hazards/meter').glob('stream-*.jsonl')))
    selected = [w for t,w in zip(stream.host_ns,stream.watts) if lo <= t < hi]
    meter = math.fsum(selected)/len(selected)*duration
    test.assertAlmostEqual(actual['energy_j']['meter'], meter, delta=tolerance_j, msg=message)
    battery = [(t,-s['B0AC']*s['B0AV']/1e6) for t,s in zip(stream.poll_ns,stream.smc)
               if 'B0AC' in s and 'B0AV' in s]
    n = sum(lo <= t < hi for t,w in battery)
    residual_ns = max(abs(stream.fit.stats[k]) for k in
                      ('excess_latency_ms_min','excess_latency_ms_max'))*1e6
    # BAT-2: one second averaged, one held, plus the largest raw poll gap.
    tau_ns = 2_000_000_000 + max(b-a for a,b in zip(stream.poll_ns,stream.poll_ns[1:]))
    # Edge power compared in W at a stricter energy-equivalent bar over T_call.
    for index, edge in enumerate((lo,hi)):
        right = next(i for i,t in enumerate(stream.host_ns) if t >= edge)
        radius = residual_ns
        powers = [w for i,(t,w) in enumerate(zip(stream.host_ns,stream.watts))
                  if i in (right-1,right) or edge-radius <= t <= edge+radius]
        test.assertAlmostEqual(actual['meter_edge_w'][index], max(powers),
                               delta=tolerance_j/duration, msg=message+'; W bar = J bar / T_call')
        charge = duration/n*math.fsum(abs(w) for t,w in battery
                                   if edge <= t < edge+tau_ns)
        test.assertAlmostEqual(actual['battery_edge_j'][index], charge, delta=tolerance_j, msg=message)
    test.assertEqual(sum(g['missing_samples'] for g in actual['meter_gaps'] if g['span']=='stream'),2)
    print(f"Independent arithmetic: {message}; rails={math.fsum(rails)} J; meter={meter} J; "
          f"meter_edge_w={actual['meter_edge_w']}; battery_edge_j={actual['battery_edge_j']}")


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
            from joulewise.bytes_analysis import _battery_delay_ns
            # Same governed function and same stream: exact replay, not a
            # comparison against a separately rounded floating literal.
            self.assertEqual(result['tau_s'],_battery_delay_ns(stream)/1e9)
            self.assertEqual(result['idle']['pre']['meter'],h.points(stream.host_ns,stream.watts,spans['pre']))
            # Charging is retained signed, never clamped to zero.
            stream.smc=[dict(B0AC=250,B0AV=12000) for _ in stream.smc]
            self.assertLess(h.meter_fields(stream,spans)['energy_j']['battery'],0)

    def test_uncovered_idle_is_unavailable_not_a_partial_mean(self):
        with tempfile.TemporaryDirectory() as tmp:
            stream=self.stream(Path(tmp))
            spans={'pre':(-2*10**9,5*10**9),'stream':(10*10**9,20*10**9),'post':(24*10**9,27*10**9)}
            result=h.meter_fields(stream,spans)
            self.assertEqual(result['idle']['pre']['meter'],[])
            self.assertIsNotNone(result['energy_j']['meter'])

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
