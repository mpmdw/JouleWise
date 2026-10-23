"""Off-grid phase transitions: additive episode bounds, synthetic evidence only."""

from dataclasses import replace
import json
import math
import random
import unittest

from joulewise.align.attribution import attribute_episode, trace_energy
from joulewise.align.records import Episode, PowerTrace, ToolCall, Turn

NS = 10**9
MS = 10**6
IDLE = 5.0


def phase_episode(period, seed, kind="point"):
    rng = random.Random(seed)
    cursor = 10 * NS + rng.randrange(1, period)
    edges = []
    # Two model calls separated by a tool wait: prefill/decode/tool/prefill/decode.
    for duration, watts in ((300*MS, 20.), (2*NS, 12.), (NS, IDLE),
                            (200*MS, 20.), (1500*MS, 12.)):
        end = cursor + duration + rng.randint(-period//3, period//3)
        if end % period == 0:
            end += 1  # Each phase edge is strictly between polls.
        edges.append((cursor, end, watts))
        cursor = end

    def integral(a, b):
        return IDLE*(b-a) + math.fsum(
            (watts-IDLE)*max(0, min(b, right)-max(a, left))
            for left, right, watts in edges)

    times = tuple(range(9*NS, cursor+NS, period))
    window = period//4 if kind == "windowed" else None
    if kind == "counter":
        values = tuple(integral(times[0], t)/NS for t in times)
    elif window is not None:
        values = tuple(integral(t-window, t)/window for t in times)
    else:
        values = tuple(next((w for a, b, w in edges if a <= t < b), IDLE)
                       for t in times)
    trace = PowerTrace("nvml_energy" if kind == "counter" else "ina3221",
                       "gpu0", "host", times, values,
                       "J_cumulative" if kind == "counter" else "W", period,
                       averaging_window_ns=window, resolution=.001,
                       notes=json.dumps({"unknown_sensor_age_bound_ns": 0}))
    turns = (Turn(0, edges[0][0], edges[2][1], 0, 100, 300, 0, edges[0][1],
                  (ToolCall("read", edges[2][0], edges[2][1], 2, 2),)),
             Turn(1, edges[3][0], edges[4][1], 300, 50, 200, 0, edges[3][1], ()))
    episode = Episode("point-total", "pair", "benign", "m", "ep", seed,
                      "host", edges[0][0], cursor, turns, power_traces=(trace,))
    truth = math.fsum((w-IDLE)*(b-a)/NS for a, b, w in edges)
    return episode, truth


class PointTotalTests(unittest.TestCase):
    def test_off_grid_phase_bounds_contain_every_episode_total(self):
        for period in (10*MS, 100*MS):
            for seed in range(80):
                with self.subTest(period=period, seed=seed):
                    episode, truth = phase_episode(period, seed)
                    result = attribute_episode(episode, source="ina3221", channel="gpu0",
                                               idle_watts=IDLE)
                    own = trace_energy(episode.power_traces[0], episode.start_ns,
                                       episode.end_ns, idle_watts=IDLE)
                    # Identical inputs/formula: the episode uses max(own, sum).
                    self.assertEqual(result.total.half_width_j, max(own.half_width_j,
                        math.fsum(s.energy.half_width_j for s in result.segments)))
                    # An additive bound must contain EVERY episode. The align
                    # default 1e-6 J is ~4 orders above sum roundoff (kJ *
                    # 2.2e-16 * 1e6 = 2.2e-7 J), yet below 1% of the smallest
                    # printed width (.069 J -> 6.9e-4 J).
                    self.assertLessEqual(abs(result.total.joules-truth),
                                         result.total.half_width_j+1e-6)

    def test_windowed_and_counter_totals_keep_the_single_query_bound(self):
        for kind in ("windowed", "counter"):
            episode, _ = phase_episode(100*MS, 0, kind)
            trace = episode.power_traces[0]
            # Large endpoint bounds make the sum strictly larger than own;
            # this ensures an unconditional widening would fail the test.
            notes = {"unknown_sensor_age_bound_ns": 0,
                     "window_timing_half_width_ns": [NS]*len(trace.t_ns),
                     "timing_half_width_ns": [NS]*len(trace.t_ns)}
            trace = replace(trace, notes=json.dumps(notes))
            episode = replace(episode, power_traces=(trace,))
            result = attribute_episode(episode, source=trace.source, channel=trace.channel,
                                       idle_watts=IDLE)
            own = trace_energy(trace, episode.start_ns, episode.end_ns, idle_watts=IDLE)
            self.assertGreater(math.fsum(s.energy.half_width_j for s in result.segments),
                               own.half_width_j)
            # Identical code on identical inputs: these bounds must be bit-identical.
            self.assertEqual(result.total.half_width_j, own.half_width_j)


if __name__ == "__main__":
    unittest.main()
