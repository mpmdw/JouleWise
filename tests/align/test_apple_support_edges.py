"""Offline Apple edge regressions, including immutable archived smoke records.

The two fixture lines are byte-for-byte copies from
forward-20261021/realsmoke-local/energy, in ARCHIVE order below. This is an
offline arithmetic replay, not live hardware validation or a claim release.
"""

import hashlib
import json
import math
import unittest
from dataclasses import replace
from pathlib import Path

from joulewise.align.apple.sampler import TRACE_DOMAIN, power_records, seconds_ns
from joulewise.align.attribution import attribute_episode
from joulewise.align.budget.energy import episode_energy
from joulewise.align.energy_residual import turn_energy_from_attribution
from joulewise.align.power.windows import window_supports
from joulewise.align.records import Episode, PowerTrace, Turn, from_json, to_json
from joulewise.interfaces import PowerSample

SECOND = 1_000_000_000
ARCHIVE = (
    ('runner_apple_pm_mapped/episode/episodes.jsonl',
     '156c84a9f418216f705ee8f23e12e6a54ef1df45af3900f8c7b97df3e5b046dc'),
    ('apple_inprocess/episodes.jsonl',
     '4261d2427174fd8c4fdd8da33a8791cd884473e26acd96fe7b7aec7fa80907b6'),
)


class AppleSupportEdges(unittest.TestCase):
    def assertAgreement(self, actual, expected):
        # Project agreement rule for different arithmetic: 1e-6 relative,
        # or 1e-6 J absolute below 1 J. No physical accuracy is inferred.
        self.assertLessEqual(abs(actual-expected), 1e-6*max(1., abs(expected)))

    def test_adapter_float_subtraction_produces_finite_flagged_estimates(self):
        epoch = 1_790_000_000.0123
        for widths in ((100_000_000,), (99_000_000, 101_000_000)):
            with self.subTest(widths=widths):
                samples, elapsed = [], 0
                for k in range(60):
                    elapsed_ns = widths[k % len(widths)]
                    elapsed += elapsed_ns
                    timestamp_s = epoch + elapsed/SECOND
                    # Exactly adapters/powermetrics.py's support construction:
                    # subtract the native elapsed duration from the epoch float.
                    samples.append(PowerSample(timestamp_s, 40., 'powermetrics', rail='cpu_power',
                        interval_start_s=timestamp_s-elapsed_ns/SECOND,
                        interval_end_s=timestamp_s))
                traces, _ = power_records(samples, nominal_interval_ns=SECOND//10)
                trace = replace(traces[0], resolution=0.)  # Synthetic exact 40 W.
                original = to_json(trace)
                raw = json.loads(trace.notes)['sample_support_ns']
                discrepancies = [a-b for (_, b), (a, _) in zip(raw, raw[1:])]
                # Uniform and variable adapter windows exercise both signs.
                self.assertIn(256 if len(widths) == 1 else -256, discrepancies)
                count = sum(d != 0 for d in discrepancies)
                flags = []
                supports = window_supports(trace, flags=flags)
                self.assertTrue(all(b == c for (_, b), (c, _) in zip(supports, supports[1:])))
                self.assertEqual(flags, ['support_edge_snapped:cpu_power',
                                        f'support_edge_snap_count:cpu_power:{count}'])
                for (old_start, _), (new_start, _) in zip(raw, supports):
                    # Two half-ulp ns products plus one epoch-second ulp:
                    # 494.42 ns here, hence < 1.98e-5 J moved per snap at 40 W.
                    quantum = math.ulp(epoch*SECOND) + math.ulp(epoch)*SECOND
                    self.assertLessEqual(abs(new_start-old_start)*40./SECOND, quantum*40./SECOND)
                start, end = supports[0][0], supports[-1][1]
                ep = Episode('adapter', 'synthetic', 'benign', 'm', 'e', 0, TRACE_DOMAIN,
                    start, end, (Turn(0, start, end, 0, 0, 1),), power_traces=(trace,))
                attr = attribute_episode(ep, source='powermetrics', channel='cpu_power')
                energy = episode_energy(ep, power_max_w=40.)
                for flag in flags:
                    self.assertIn(flag, attr.flags)
                    self.assertIn(flag, energy.flags)
                self.assertTrue(math.isfinite(attr.total.joules))
                self.assertTrue(math.isfinite(attr.total.half_width_j))
                self.assertTrue(math.isfinite(energy.joules))
                self.assertTrue(math.isfinite(energy.uncertainty_j))
                self.assertAgreement(attr.total.joules, 40.*((end-start)/SECOND))
                self.assertAgreement(energy.joules, attr.total.joules)
                self.assertEqual(to_json(trace), original)

    def test_only_conversion_quantum_disagreements_snap(self):
        edge = seconds_ns(1_790_000_000.)
        # 256 ns product ulp + 238.42 ns seconds ulp: integer discrepancies
        # of 494 ns are within the quantum; 495 ns are real gaps/overlaps.
        for delta in (-495, -494, 0, 494, 495):
            for source in ('powermetrics', 'mock'):
                with self.subTest(delta_ns=delta, source=source):
                    raw = [[edge-SECOND, edge], [edge+delta, edge+SECOND]]
                    trace = PowerTrace(source, 'cpu', 'host', (edge, edge+SECOND),
                        (4., 4.), 'W', SECOND, resolution=0.,
                        notes=json.dumps({'sample_support_ns': raw}))
                    flags = []
                    supports = window_supports(trace, flags=flags)
                    snapped = source == 'powermetrics' and 0 < abs(delta) <= 494
                    self.assertEqual(supports[1][0], edge if snapped else edge+delta)
                    self.assertEqual(flags, ['support_edge_snapped:cpu', 'support_edge_snap_count:cpu:1']
                                     if snapped else [])
                    ep = Episode('edge', 'synthetic', 'benign', 'm', 'e', 0, 'host',
                        edge-SECOND, edge+SECOND, (), power_traces=(trace,))
                    attr = attribute_episode(ep, source=source, channel='cpu')
                    energy = episode_energy(ep, power_max_w=4.)
                    overlap = delta < 0 and not snapped
                    self.assertEqual('window.overlap' in attr.flags, overlap)
                    self.assertEqual('energy_window_overlap' in energy.flags, overlap)
                    self.assertEqual(math.isinf(attr.total.half_width_j), overlap)
                    if overlap:
                        self.assertIsNone(energy.joules)
                    else:
                        self.assertTrue(math.isfinite(energy.joules))
                    self.assertEqual('energy_window_gap' in energy.flags, delta > 0 and not snapped)

    def test_archived_episodes_keep_finite_totals_and_unfloored_segment_bounds(self):
        lines = (Path(__file__).parent/'fixtures/realsmoke_energy.jsonl').read_bytes().splitlines(keepends=True)
        self.assertEqual(len(lines), len(ARCHIVE))
        # Cold replay values after quantum snapping: total J, sum of segment
        # half-widths, sum of turn half-widths. In particular CPU turns sum to
        # 5.0208 J for the runner, and 0.6720 J for apple_inprocess.
        expected = (
            {'cpu_power': (182.0431002033122, 5.039050554677281, 5.020813654014683),
             'gpu_power': (67.8590973682368, 3.9931919671226765, 3.97089634386273),
             'ane_power': (0., 0., 0.)},
            {'cpu_power': (830.613298782772, .6745405480400953, .6720415496282723),
             'gpu_power': (284.2940729959329, .20523058879045106, .20477603702506825),
             'ane_power': (0., 0., 0.)},
        )
        for line, (path, digest), targets, count in zip(lines, ARCHIVE, expected, (15, 57)):
            self.assertEqual(hashlib.sha256(line).hexdigest(), digest, path)
            ep = from_json(Episode, line)
            original = to_json(ep)
            for channel, (joules, segment_bound, turn_bound) in targets.items():
                with self.subTest(archive=path, channel=channel):
                    attr = attribute_episode(ep, source='powermetrics', channel=channel)
                    budget = episode_energy(ep, channels=(('powermetrics', channel),))
                    for flags in (attr.flags, budget.flags):
                        self.assertIn(f'support_edge_snapped:{channel}', flags)
                        self.assertIn(f'support_edge_snap_count:{channel}:{count}', flags)
                    self.assertTrue(math.isfinite(attr.total.joules))
                    self.assertTrue(math.isfinite(budget.joules))
                    self.assertEqual(attr.total.half_width_j, 1.)
                    self.assertAgreement(attr.total.joules, joules)
                    self.assertAgreement(budget.joules, joules)
                    self.assertAgreement(math.fsum(s.energy.joules for s in attr.segments), joules)
                    self.assertAgreement(math.fsum(s.energy.half_width_j for s in attr.segments), segment_bound)
                    turns = turn_energy_from_attribution(attr)
                    self.assertAgreement(math.fsum(h for _, h in turns.values()), turn_bound)
                    for turn, (_, bound) in turns.items():
                        # Identical fsum over that turn's component segments.
                        self.assertEqual(bound, math.fsum(s.energy.half_width_j
                            for s in attr.segments if s.turn == turn))
                    self.assertTrue(all(math.isfinite(s.energy.half_width_j) for s in attr.segments))
                    self.assertTrue(all('powermetrics.attribution_floor' not in s.energy.flags
                                        for s in attr.segments))
                    # These archived records do not establish sensor resolution
                    # or a prospective Pmax. Keep the budget bound unknown.
                    self.assertIsNone(budget.uncertainty_j)
                    self.assertIn('energy_resolution_unknown', budget.flags)
            total = episode_energy(ep, channels=tuple(('powermetrics', c) for c in targets))
            self.assertAgreement(total.joules, math.fsum(v[0] for v in targets.values()))
            self.assertEqual(to_json(ep), original)


if __name__ == '__main__':
    unittest.main()
