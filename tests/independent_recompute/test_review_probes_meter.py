"""RC-CMP-5 S4: the reviewers' meter-fit probes not yet in the suite, as regression tests.

Sol's point-level and short-stream fits (rc-cmp-sol-rev probe_meter_fit, probe_meter_short;
the same scripts in round 2) and Opus's twelve adversarial stream families (rc-cmp-opus-rev-2
probe_meter_adversarial). None found a defect at e5ccf720b; each is kept as a guard with the
probe's seeds and sizes. The parser (joulewise.external.km003c_parse) is the reference only.
"""
import json
from pathlib import Path
import random
import struct
import tempfile
import unittest

from joulewise.external import km003c_parse as parser

from .support import recompute as own
from .test_meter_fit import fit_agreement


def point_difference(points):
    """Sol's compare(): the largest host-time difference over the points, or None when the recompute fits nothing."""
    samples = parser.Samples([p[0] for p in points], [1.] * len(points), [1.] * len(points),
                             list(range(len(points))), 0, 20)
    batches = [{"rx": p[1], "tx": p[1] - round(p[2] * 1e6), "n": p[3]} for p in points]
    a, b = own.meter_clock_fit(points), parser.clock_fit(samples, batches)
    if a is None:
        return None
    return max(abs(round(a["intercept_ns"] + a["slope_ns_per_ms"] * p[0]) - b.host_ns(p[0])) for p in points)


class SolPointFitProbeTests(unittest.TestCase):
    def test_probe_meter_fit_seeded_long_origins(self):
        rng = random.Random(1743)
        largest = 0
        for base in (10**12, 10**15, 10**17):
            for _ in range(2000):
                n = rng.randrange(20, 101)
                step = rng.choice((20, 100, 1000, 10000))
                ppm = rng.uniform(-150, 150)
                points = []
                for i in range(n):
                    device = i * step
                    rx = base + round(device * 1e6 * (1 + ppm * 1e-6)) + rng.randrange(0, 3_000_000)
                    count = 63 if rng.random() < .1 else 1
                    points.append((device, rx, rng.uniform(0, 5), count))
                largest = max(largest, point_difference(points) or 0)
        self.assertEqual(largest, 0)

    def test_probe_meter_short_streams(self):
        rng = random.Random(2718)
        for base in (10**15, 10**16, 10**17):
            largest = 0
            for n in (3, 4, 5, 8, 12):
                for _ in range(10000):
                    points = [(i * 10000, base + i * 10000 * 1000000 + rng.randrange(0, 3000000), 1.0, 1)
                              for i in range(n)]
                    largest = max(largest, point_difference(points) or 0)
            self.assertEqual(largest, 0, base)


def write_stream(path, base, polls):
    """Opus's write(): polls are (device ms of the newest sample, n, rx offset ns, rtt ns)."""
    rows = [{"k": "h", "schema": "joulewise.km003c_stream.v1", "rate_idx": 2, "start_raw_ns": base, "start_mono_ns": base}]
    for newest, n, rx_off, rtt in polls:
        first = newest - (n - 1) * 20
        payload = b"".join(struct.pack("<HHiiHHHH", (first + k * 20) % 65536, 0, 10_000_000, 1_000_000, 0, 0, 0, 0)
                           for k in range(n))
        rx = base + rx_off
        rows.append({"k": "b", "tx": rx - rtt, "rx": rx, "n": n, "p": payload.hex()})
    last = max(row["rx"] for row in rows[1:])
    rows.append({"k": "t", "end_raw_ns": last + 1, "end_mono_ns": last + 1})
    path.write_text("".join(json.dumps(x) + "\n" for x in rows))


def stream(base, count, ppm=30., jitter=1_000_000, rtt=(50_000, 2_999_999), n=(1, 6), tie=False, shuffle=False,
           dup=False, gap_every=0):
    def make(path, rng):
        device, polls = 0, []
        for i in range(count):
            k = rng.randrange(*n)
            newest = device + (k - 1) * 20
            device += k * 20 + (40_000 if gap_every and i % gap_every == gap_every - 1 else 0)
            lat = 0 if tie else rng.randrange(0, jitter)
            polls.append((newest, k, round(newest * 1e6 * (1 + ppm * 1e-6)) + lat, rng.randrange(*rtt)))
        if dup:
            polls = [p for p in polls for _ in (0, 1)]
        if shuffle:
            rng.shuffle(polls)
        write_stream(path, base, polls)
    return make


FAMILIES = (("int64_scale_origin_9e18", stream(9 * 10**18, 800), 60),
            ("origin_2p53_plus", stream(2**53 + 12345, 800), 60),
            ("exact_ties_no_jitter_1e16", stream(10**16, 800, tie=True), 30),
            ("rtt_at_3ms_cap", stream(10**15, 600, rtt=(2_999_000, 3_001_000)), 60),
            ("n_at_63_cap", stream(10**15, 600, n=(60, 64)), 40),
            ("negative_rtt", stream(10**15, 600, rtt=(-2_000_000, 2_000_000)), 60),
            ("rx_out_of_order", stream(10**15, 600, shuffle=True), 60),
            ("duplicated_polls", stream(10**15, 600, dup=True), 40),
            ("device_wrap_gaps", stream(10**15, 1500, gap_every=97), 40),
            ("fallback_19_eligible", stream(10**15, 19), 60),
            ("two_polls", stream(10**15, 2), 30),
            ("negative_drift_ppm", stream(4 * 10**15, 800, ppm=-80.), 40))


class OpusAdversarialStreamProbeTests(unittest.TestCase):
    def test_probe_meter_adversarial_families(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = {}
            for name, make, seeds in FAMILIES:
                for seed in range(seeds):
                    path = Path(tmp) / f"{name}-{seed}.jsonl"
                    make(path, random.Random(seed))
                    difference, same_envelope = fit_agreement(path)
                    if difference is None or difference > 0 or not same_envelope:
                        bad[f"{name}/{seed}"] = (difference, same_envelope)
            self.assertEqual(bad, {})
        self.assertEqual(sum(seeds for _, _, seeds in FAMILIES), 580)


if __name__ == "__main__":
    unittest.main()
