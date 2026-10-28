"""Synthetic point streams comparing the independent fit with parser fit."""
import random

from independent_recompute.support import recompute as own
from joulewise.external import km003c_parse as parser


def compare(points):
    s = parser.Samples([p[0] for p in points], [1.] * len(points), [1.] * len(points),
                       list(range(len(points))), 0, 20)
    batches = [{"rx": p[1], "tx": p[1] - round(p[2] * 1e6), "n": p[3]} for p in points]
    a, b = own.meter_clock_fit(points), parser.clock_fit(s, batches)
    if a is None:
        return None
    return max(abs(round(a["intercept_ns"] + a["slope_ns_per_ms"] * p[0]) - b.host_ns(p[0])) for p in points)


if __name__ == "__main__":
    rng = random.Random(1743)
    largest = (0, None)
    for base in (10**12, 10**15, 10**17):
        for trial in range(2000):
            n = rng.randrange(20, 101)
            step = rng.choice((20, 100, 1000, 10000))
            ppm = rng.uniform(-150, 150)
            points = []
            for i in range(n):
                device = i * step
                jitter = rng.randrange(0, 3_000_000)
                rx = base + round(device * 1e6 * (1 + ppm * 1e-6)) + jitter
                count = 63 if rng.random() < .1 else 1
                rtt = rng.uniform(0, 5)
                points.append((device, rx, rtt, count))
            difference = compare(points)
            if difference is not None and difference > largest[0]:
                largest = (difference, (base, trial, n, step, ppm, points))
            if difference is not None and difference > 1:
                print("first_gt_1ns", "base=", base, "trial=", trial, "n=", n,
                      "step=", step, "max_ns=", difference)
                print("points=", repr(points))
                raise SystemExit(0)
    print("largest", largest[0], "base_trial=", largest[1][:2] if largest[1] else None)
