"""R26/A21 hand witnesses, built entirely from synthetic records."""
import io
import json
import plistlib
import unittest
from unittest.mock import patch

from joulewise.adapters.powermetrics import (
    decode_rich_telemetry, parse_powermetrics_records, samples_from_records,
)
from joulewise.align.apple import reduce_sol as sol, thermal_desk as td, v4_estimands as est
from joulewise.align.apple.sampler import seconds_ns, stamp_mapping
from joulewise.align.attribution import trace_energy
from joulewise.align.v4_analysis import analyze, engine as e
from joulewise.align.v4_analysis.synthetic import series
from joulewise.clock import ClockStamp
from tests.align.test_attribution import episode, turn
from tests.align.v4_synthetic import synthetic_frames

NS = 10**9
CURVE_GRID = [0, 128, 256, 300, 384, 512, 768, 1024, 1536, 2048]


def pm_bytes(widths):
    frames = []
    for i, frame in enumerate(synthetic_frames(len(widths))):
        document = plistlib.loads(frame.rstrip(b'\0'))
        document['elapsed_ns'] = widths[i]
        document['processor']['gpu_power'] = 10_000. * (i+1)
        frames.append(plistlib.dumps(document) + b'\0')
    return b''.join(frames)


class HStarAndFullTests(unittest.TestCase):
    def test_h_star_is_only_c_benign_and_t_sabotage(self):
        fill, _ = analyze(series(turns=4))
        seen = set()
        for fit in fill['fits']:
            for row in fit['scores']:
                expected = fit['convention'] == 'counts_logged' and (
                    (fit['window'].startswith('C') and row['condition'] == 'benign') or
                    (fit['window'].startswith('T') and row['condition'] == 'sabotage'))
                self.assertEqual('H_star' in row, expected,
                                 (fit['window'], fit['convention'], row['condition']))
                seen.add((fit['window'][0], row['condition']))
        self.assertEqual(seen, {('C', 'benign'), ('T', 'benign'), ('T', 'sabotage')})

    def test_r26_strict_crossing_missing_doses_no_crossing_and_off_grid(self):
        crossed = est.subturn_h_star([(128, 1.), (256, 2.), (300, 9.)], 1.)
        self.assertEqual(crossed['h_star'], 256)  # equality at 128 is not a crossing
        self.assertTrue(crossed['bounded_above'])
        self.assertEqual(crossed['off_grid_doses'], [300])
        missing = est.subturn_h_star([(128, 1.), (384, 2.)], 1.)
        self.assertIsNone(missing['h_star'])
        self.assertEqual(missing['undefined_missing_grid_doses'], [256])
        self.assertFalse(missing['bounded_above'])
        never = est.subturn_h_star([(h, 1.) for h in est.H_STAR_GRID], 1.)
        self.assertIsNone(never['h_star'])
        self.assertFalse(never['bounded_above'])
        self.assertEqual(never['undefined_missing_grid_doses'], [])

    def test_full_cell_uses_pair_cutoff_and_never_enters_curve_or_crossings(self):
        original_fit, original_threshold = e._fit_task, e.threshold

        def fit(task):
            result = original_fit(task)
            if result['window'].startswith('C'):
                for row in result['scores']:
                    for dose in row['H_grid']:
                        if dose['score'] is not None:
                            # All numeric doses stay below threshold. Half of
                            # full scores tie it, half strictly exceed it.
                            dose['score'] = (1. if int(result['window'][1:]) % 2 else 2.
                                             ) if dose['nominal_H'] == 'full' else 0.
            return result

        def cutoff(*args, **kwargs):
            return {**original_threshold(*args, **kwargs), 'threshold': 1.}

        with patch.object(e, '_fit_task', side_effect=fit), patch.object(e, 'threshold', side_effect=cutoff):
            fill, _ = analyze(series(turns=4))
        for pair in fill['benign_carriers']['pairs'].values():
            self.assertEqual(pair['full_cell'], dict(status='print_only', fraction=.5, n=56))
            self.assertEqual([h for h, _ in pair['curve']], CURVE_GRID)
            self.assertEqual([int(h) for h in pair['n_by_h']], CURVE_GRID)
            self.assertNotIn('full', pair['all_carrier_prefix'])
            self.assertIsNone(pair['H50'])
            self.assertIsNone(pair['H90'])
            self.assertEqual(pair['bootstrap_undefined_replicates'], dict(H50=1000, H90=1000))

    def test_full_cell_without_pair_threshold_stays_null_with_observed_n(self):
        payload = series(turns=4)
        payload['windows'] = payload['windows'][:1]
        fill, _ = analyze(payload)
        for pair in fill['benign_carriers']['pairs'].values():
            self.assertEqual(pair['full_cell'], dict(status='print_only', fraction=None, n=7))


class AdapterFloatTimeTests(unittest.TestCase):
    def test_2026_endpoints_and_supports_match_production_bits_then_exact_ns(self):
        anchor = 1767225600.4445496
        data = pm_bytes([100_000_000, 100_000_500, 100_000_001, 99_999_999, 100_000_003])
        records = parse_powermetrics_records(data, first_record_endpoint_s=anchor)
        rich = decode_rich_telemetry(data, first_record_endpoint_s=anchor)
        native = samples_from_records(records)[::3]
        samples = sol.reduce_stream(io.BytesIO(data))
        expected = [r.timestamp_s for r in records]
        self.assertEqual([t.hex() for t in samples.endpoint_seconds(anchor)], [t.hex() for t in expected])
        self.assertEqual([r['timestamp_s'].hex() for r in rich], [t.hex() for t in expected])
        stamp = ClockStamp(anchor, 1000.000000059547, 1000.000000059547, 0., 0.)
        mapping, _ = stamp_mapping([stamp], episode_domain='host')
        self.assertEqual(mapping.offset_ns, -1767224600444549501)
        ends = [seconds_ns(t) for t in expected]
        starts = [seconds_ns(r.interval_start_s) for r in native]
        # Literal 2026-epoch adapter endpoints, before/after A37 interior snap.
        self.assertEqual(ends, [1767225600444549561, 1767225600544549942,
                               1767225600644550085, 1767225600744549990, 1767225600844550133])
        self.assertEqual(starts, [1767225600344549656, 1767225600444549561,
                                 1767225600544550180, 1767225600644550085, 1767225600744550228])
        starts[1:] = ends[:-1]  # all four interior seams are <=1000ns
        mapped = samples.mapped_columns(anchor, mapping.offset_ns)
        self.assertEqual(list(mapped['t_ns']), [t+mapping.offset_ns for t in ends])
        for key in ('power_start_ns', 'thermal_start_ns'):
            self.assertEqual(list(mapped[key]), [t+mapping.offset_ns for t in starts])
        self.assertEqual([r['start_ns'] for r in samples.native_pm_samples(anchor, mapping.offset_ns)],
                         list(mapped['power_start_ns']))
        traces = samples.power_traces(anchor, nominal_interval_ns=100_000_000)[0]
        for trace in traces:
            self.assertEqual(trace.t_ns, tuple(ends))
            self.assertEqual(json.loads(trace.notes)['sample_support_ns'], [list(s) for s in zip(starts, ends)])

    def test_real_float_accumulation_large_epoch_gaps_stay_uncovered_and_exclude(self):
        # .099997 rounds down on the 9e9s float grid; records 4/8/13
        # therefore start 1907/1907/1908ns after their predecessor ends.
        anchor, base = 9_000_000_000., 9_000_000_000*NS
        data = pm_bytes([99_997_000]*15)
        samples = sol.reduce_stream(io.BytesIO(data))
        adapter = samples_from_records(parse_powermetrics_records(data, first_record_endpoint_s=anchor))[::3]
        expected = [[seconds_ns(r.interval_start_s)-base, seconds_ns(r.timestamp_s)-base] for r in adapter]
        gaps = [a-b for (_, b), (a, _) in zip(expected, expected[1:])]
        self.assertEqual(gaps, [0, 0, 1907, 0, 0, 0, 1907, 0, 0, 0, 0, 1908, 0, 0])
        traces = samples.power_traces(anchor, nominal_interval_ns=100_000_000)[0]
        trace = next(t for t in traces if t.channel == 'gpu_power')
        self.assertEqual(json.loads(trace.notes)['sample_support_ns'],
                         [[a+base, b+base] for a, b in expected])
        self.assertEqual(json.loads(trace.notes)['support_policy'], 'A37')
        gap = trace_energy(trace, base+expected[2][1], base+expected[3][0])
        self.assertEqual(gap.joules, 0.)
        self.assertIn('duty.uncovered', gap.flags)
        start, end = expected[0][0], expected[-1][1]
        mapping, _ = stamp_mapping([ClockStamp(anchor, 0., 0., 0., 0.)], episode_domain='host')
        ep = episode(start_ns=start, end_ns=end, turns=(turn(0, start, end, start+1),),
            power_traces=traces, clock_mappings=(mapping,))
        record = td.member_record(ep, [], os_readings=[], pm_samples=[], pm_period_s=.1)
        payload = series(turns=4)
        member = payload['windows'][0]['members'][5]
        member['thermal'].update({k: record[k] for k in ('energy_flags', 'owned_energy_flags')})
        e._screen_member(member, payload['cohort'])
        self.assertIn('duty.uncovered', member['thermal']['owned_energy_flags'])
        self.assertIn('energy_unavailable', member['rederived_classes'])
        self.assertFalse(member['eligible'])

    def test_c5_style_2026_energy_is_float_accumulation_value(self):
        anchor = 1767225600.4445496
        samples = sol.reduce_stream(io.BytesIO(pm_bytes(
            [100_000_000, 100_000_500, 100_000_001, 99_999_999, 100_000_003])))
        trace = next(t for t in samples.power_traces(anchor, nominal_interval_ns=100_000_000)[0]
                     if t.channel == 'gpu_power')
        energy = trace_energy(trace, 1767225600344549656, 1767225600844550133)
        self.assertEqual(energy.joules, 15.000014310000001)
        # The reverted integer-ns reconstruction gives a different value.
        self.assertNotEqual(energy.joules, 15.00000919)
        self.assertNotIn('duty.uncovered', energy.flags)


if __name__ == '__main__':
    unittest.main()
