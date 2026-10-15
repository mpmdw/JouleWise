from __future__ import annotations

import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path

from joulewise.quiet_kit import analysis, readers
from .fixtures import EPOCH, RAW, meter_stream, power_attempt, ps_bytes, synthetic_capture


class ProductionReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='quiet-kit-reader-')
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def test_stored_production_format_fixtures(self):
        from joulewise.adapters.powermetrics import parse_powermetrics_records, samples_from_records
        from joulewise.hazards.contention import parse
        fixture=Path(__file__).resolve().parents[1]/'fixtures/quiet_kit'
        records=parse_powermetrics_records((fixture/'powermetrics.plist').read_bytes())
        self.assertEqual(len(records),3)
        self.assertTrue(samples_from_records(records))
        self.assertAlmostEqual(records[0].combined_power_w,.05)
        self.assertEqual(len(parse((fixture/'ps.txt').read_bytes())),1)
        self.assertEqual(readers.parse_sntp((fixture/'sntp.txt').read_text()),.012345)
        self.assertTrue(readers.meter(fixture/'meter.jsonl')[1].present)
        self.assertEqual(readers.run_bundle(fixture,{'bundle':'run_bundle'})['phase_energy_j']['decode'],1.2)

    def test_real_plist_rails_chain_and_cpu_time(self):
        power_attempt(self.root/'attempt', [
            {'kind': 'idle', 'power': .05},
            {'kind': 'cpu', 'power': .30, 'duty': .05, 'cpu_seconds': .1},
            {'kind': 'idle', 'power': .05}])
        data = readers.read_attempt(self.root/'attempt')
        self.assertGreater(len(data['segments'][0]['records']), 10)
        out = analysis.m4(data)['arms'][0]
        self.assertAlmostEqual(out['watts_per_cpu_rate']['value'], (.30-.05)/(.1/2.), places=5)

    def test_real_meter_layout_clock_fit_and_dropped_sample(self):
        path = self.root/'meter.jsonl'
        path.write_bytes(meter_stream([28.]*100, drop=20))
        rows, stream, fit, flags = readers.meter(path)
        self.assertTrue(stream.present)
        self.assertEqual(len(rows), 99)
        self.assertAlmostEqual(rows[0]['meter'], 28.)
        self.assertAlmostEqual(fit['rate_ppm'], 0., places=6)
        self.assertTrue(any(f['reason'] == 'meter lost samples' for f in flags))

    def test_meter_absent_and_lost_every_sample_give_recorded_undefined(self):
        path = self.root/'meter.jsonl'
        path.write_text('{"k":"h","status":"absent","reason":"unplugged"}\n')
        rows, stream, _, _ = readers.meter(path)
        self.assertFalse(stream.present)
        self.assertEqual(rows, [])
        path.write_bytes(meter_stream([28.]))
        rows, stream, fit, _ = readers.meter(path)
        self.assertTrue(stream.present)
        self.assertIsNone(fit)
        self.assertEqual(rows, [])
        self.assertIn('fewer than two', stream.fit_error)
        path.write_text('{"k":"h","status":"streaming","rate_idx":2}\n'
                        '{"k":"b","rx":1,"tx":0,"n":1,"p":"00"}\n')
        rows,stream,fit,flags=readers.meter(path)
        self.assertFalse(stream.present)
        self.assertIsNotNone(stream.fit_error)
        self.assertFalse(rows)

    def test_meter_and_rails_steps_go_through_real_parsers(self):
        power_attempt(self.root/'attempt', [
            {'kind': 'idle', 'power': 1., 'meter_power': 28.},
            {'kind': 'gpu', 'power': 5., 'meter_power': 36., 'duty': .2, 'cpu_seconds': .01},
            {'kind': 'idle', 'power': 1., 'meter_power': 28.}], meter=True)
        data = readers.read_attempt(self.root/'attempt')
        self.assertTrue(data['meter_present'])
        out = analysis.m14(data)['levels'][0]
        self.assertAlmostEqual(out['rail_step']['value'], 4., places=5)
        self.assertAlmostEqual(out['meter_step']['value'], 8., places=4)
        self.assertAlmostEqual(out['rails_over_meter']['value'], .5, places=4)

    def test_run_bundle_shape(self):
        path = self.root/'runs/qk-example'
        path.mkdir(parents=True)
        path.joinpath('summary_metrics.json').write_text(json.dumps({
            'status': 'ok', 'phase_energy_j': {'prefill': .3, 'decode': 1.2},
            'ttft_s': 1., 'decode_latency_s': 149., 'throughput_tokens_s': 24.}))
        row = readers.run_bundle(self.root, {'bundle': 'runs/qk-example'})
        self.assertEqual(row['phase_energy_j']['prefill'], .3)
        self.assertEqual(row['duration_s'], 150.)
        self.assertEqual(row['token_rate'], 24.)

    def test_ps_layout_library_cpu_seconds(self):
        from joulewise.hazards.contention import parse
        before = parse(ps_bytes(10.))
        after = parse(ps_bytes(10.5))
        self.assertEqual(next(iter(after.values()))['cumulative_cpu_seconds']-
                         next(iter(before.values()))['cumulative_cpu_seconds'], .5)

    def test_sntp_actual_lines_and_unmeasured_output(self):
        self.assertEqual(readers.parse_sntp('+0.012345 +/- 0.000134 time.apple.com 17.1.1.1'), .012345)
        self.assertEqual(readers.parse_sntp('sntp: offset -0.001234 seconds'), -.001234)
        self.assertIsNone(readers.parse_sntp('server failed after 12 seconds'))

    def test_resumed_clock_flags_do_not_cross_job_or_reboot_boundaries(self):
        rows=[{'source_job_id':job,'boot_session_uuid':boot,
               'anchor':{'monotonic_raw_ns':105_000_000_000,'realtime_ns':200_000_000_000}}
              for job,boot in [('old','boot-one'),('new','boot-two')]]
        watch=[{'source_job_id':'old','stamp':{'monotonic_raw_ns':100_000_000_000},
                'physics':{'thermal_level':1,'battery_current_ma':0}},
               {'source_job_id':'new','stamp':{'monotonic_raw_ns':100_000_000_000},
                'physics':{'thermal_level':0,'battery_current_ma':0}}]
        result=readers.flag_segments({'clock':rows},watch)
        self.assertEqual([r['source_job_id'] for r in result['clock_clean']],['new'])

    def test_meter_edge_interpolation_independent_lag(self):
        points = [(0., 0.), (.02, 10.), (.04, 10.)]
        # Half crossing is 10 ms; command was 2 ms before zero => 12 ms lag.
        crossing = readers.half_crossing(points, -.002, 'on', 0., 10.)
        self.assertAlmostEqual((crossing-(-.002))*1000, 12.)
        self.assertIsNone(readers.half_crossing([(0.,0.), (.1,10.)], -.002, 'on', 0.,10.))

    def test_hazard_spans_keep_both_analysis_versions(self):
        data = {'segments': [{'kind':'cpu', 'start': {'raw_s':10}, 'end': {'raw_s':20}}]}
        watch = [{'stamp': {'monotonic_raw_ns': 5_000_000_000},
                  'physics': {'thermal_level': 1, 'battery_current_ma': 250}}]
        out = readers.flag_segments(data, watch)
        self.assertEqual(out['segments'][0]['hazard_flags'], ['battery current over 200 mA','thermal pressure'])

    def test_raw_descriptor_cannot_escape_attempt(self):
        with self.assertRaises(ValueError):
            readers.relative(self.root, '../elsewhere')


class FiducialParityTests(unittest.TestCase):
    def test_real_meter_bytes_pulse_events_and_analysis_recover_twelve_ms_lag(self):
        from .fixtures import meter_stream
        raw,events,anchor,protocol=synthetic_capture(offset=.012)
        event_rows=[json.loads(line) for line in events.splitlines()]
        raw_shift=.123  # a legacy epoch/RAW offset must not replace direct RAW stamps
        pairs=[]
        pending={}
        for row in event_rows:
            kind,edge=row['event_type'].split('_command_')
            t=row['timestamp_s']-EPOCH
            row['metadata']['monotonic_raw_ns']=round((RAW+raw_shift+t)*1e9)
            if edge=='on':pending[kind]=t
            else:pairs.append((pending.pop(kind),t))
        duration=max(off for _,off in pairs)+5
        powers=[]
        for i in range(math.ceil(duration/.02)):
            t=i*.02
            power=28.
            for on,off in pairs:
                rise=max(0.,min(1.,(t-(on+.012-.02))/.04))
                fall=max(0.,min(1.,((off+.012+.02)-t)/.04))
                power+=10*min(rise,fall)
            powers.append(power)
        with tempfile.TemporaryDirectory(prefix='quiet-kit-meter-edge-') as tmp:
            root=Path(tmp)
            capture=root/'capture-0'
            (capture/'raw').mkdir(parents=True)
            (capture/'raw/powermetrics.plist').write_bytes(raw)
            (capture/'events.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in event_rows))
            (capture/'raw/sampler.json').write_text(json.dumps({'clock_anchor':anchor,'start':{'epoch_s':EPOCH,'raw_s':RAW}}))
            (capture/'capture.json').write_text(json.dumps({'protocol_id':protocol,'scale':1.,'cadence_median_ms':100.}))
            (root/'meter.jsonl').write_bytes(meter_stream(powers,start_raw=RAW+raw_shift))
            (root/'collection.json').write_text(json.dumps({'test_id':'m13-meter-edges','meter_file':'meter.jsonl',
                'captures':[{'id':'capture-0','directory':'capture-0','condition':'quiet'}]}))
            data=readers.read_attempt(root)
            result=analysis.m13(data)
        self.assertEqual(len(data['edges']),118)
        self.assertTrue(all(e['command_clock']=='CLOCK_MONOTONIC_RAW' for e in data['edges']))
        self.assertAlmostEqual(result['meter_lag_mean']['value'],12.,places=3)
        self.assertEqual(result['meter_lag_mean']['uncertainty']['n'],118)

    def test_existing_g2b_fixture_capture_library_parity(self):
        import gzip
        from joulewise.powermetrics_fiducial import rederive_detection_from_artifacts
        from joulewise.quiet_kit.fiducial import derive, report
        fixture=Path(__file__).resolve().parents[1]/'fixtures/controller_g2b/block3-pre'
        raw=gzip.decompress((fixture/'raw/powermetrics.plist.gz').read_bytes())
        events=gzip.decompress((fixture/'events.jsonl.gz').read_bytes())
        evidence=json.loads(gzip.decompress((fixture/'instrument_evidence.json.gz').read_bytes()))
        direct=derive(raw,events,evidence['clock_anchor'],protocol_id=evidence['protocol_id'])
        replay=rederive_detection_from_artifacts(raw,events,evidence['clock_anchor'],protocol_id=evidence['protocol_id'])
        self.assertEqual(report(direct)['bound_s'],report(replay)['bound_s'])
        self.assertIsNotNone(report(direct)['bound_s'])

    def test_library_composition_equals_library_rederivation_on_known_offset(self):
        from joulewise.powermetrics_fiducial import rederive_detection_from_artifacts
        from joulewise.quiet_kit.fiducial import derive, report
        raw, events, anchor, protocol = synthetic_capture(offset=.012)
        direct = derive(raw, events, anchor, protocol_id=protocol)
        replay = rederive_detection_from_artifacts(raw, events, anchor, protocol_id=protocol)
        self.assertEqual(report(direct)['bound_s'], report(replay)['bound_s'])
        self.assertTrue(direct.all_pulses_detected, direct.reasons)
        self.assertGreaterEqual(report(direct)['bound_s'], .012)
        self.assertLess(report(direct)['bound_s'], .05)
        # Every fit must cover the independently constructed +12 ms delay.
        for fit in direct.fits:
            self.assertLessEqual(fit.onset_residual_lower_s, .012+.000002)
            self.assertGreaterEqual(fit.onset_residual_upper_s, .012-.000002)
        self.assertEqual(len(direct.fits), 59)
