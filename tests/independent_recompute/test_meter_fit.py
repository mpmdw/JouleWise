"""RC-CMP-2 M1/M2: the recompute's meter clock fit follows the registered parser definition.

The parser (joulewise.external.km003c_parse) is imported here as the reference
only; the recompute itself imports nothing from it.
"""
import json
from pathlib import Path
import random
import struct
import tempfile
import unittest
from unittest import mock

from .support import recompute as r

SEEDS = 240
DEVICE_STEP_MS = 20


def old_clock_fit(points):
    """The pre-RC-CMP-2 recompute fit, kept only as the counterfactual.

    Eligible polls 0 < n < 63 and 0 <= RTT < 3 ms, no fallback below 20, and
    10 s bins keyed from device time 0 (commit 7e322b767).
    """
    eligible = [(x, y) for x, y, rtt, n in points if 0 < n < 63 and 0 <= rtt < 3.]
    initial = r.fit_line(eligible) if len(eligible) >= 20 else None
    minima = {}
    if initial:
        a, b = initial
        for x, y in eligible:
            residual = y - (a + b * x)
            if x // 10000 not in minima or residual < minima[x // 10000][0]:
                minima[x // 10000] = (residual, (x, y))
    final = r.fit_line([minima[k][1] for k in sorted(minima)]) if len(minima) >= 2 else None
    if final is None or final[1] <= 0:
        return None
    a, b = final
    return {"intercept_ns": a, "slope_ns_per_ms": b, "fit_points": len(points),
            "max_above_envelope_ns": max(y - (a + b * x) for x, y in eligible)}


def jitter_stream(path, seed):
    """A synthetic KM003C stream with seeded batch sizes, drift, arrival jitter and RTTs.

    kind "within": every RTT below the 3 ms eligible cap; "mixed": some polls
    above it or capped at 63 samples; "fallback": fewer than 20 eligible polls,
    so the parser fits every poll.
    """
    rng = random.Random(seed)
    kind = ("within", "mixed", "fallback")[seed % 3]
    base = 10**12 + rng.randrange(10**9)
    ppm = rng.uniform(-80., 80.)
    rows = [{"k": "h", "schema": "joulewise.km003c_stream.v1", "rate_idx": 2,
             "start_raw_ns": base, "start_mono_ns": base}]
    device = 0
    polls = rng.randrange(150, 2600)
    for _ in range(polls):
        n = 63 if kind != "within" and rng.random() < .04 else rng.randrange(1, 6)
        payload = b"".join(struct.pack("<HHiiHHHH", (device + k * DEVICE_STEP_MS) % 65536, 0,
                                       10_000_000 + rng.randrange(-5000, 5000),
                                       rng.randrange(0, 5_000_000), 0, 0, 0, 0)
                           for k in range(n))
        newest = device + (n - 1) * DEVICE_STEP_MS
        device += n * DEVICE_STEP_MS
        latency = rng.randrange(0, 2_900_000)
        if kind == "within":
            rtt = rng.randrange(50_000, 2_999_999)
        elif kind == "mixed":
            rtt = rng.randrange(50_000, 2_999_999) if rng.random() < .7 else rng.randrange(3_000_000, 9_000_000)
        else:
            rtt = rng.randrange(3_000_000, 9_000_000) if rng.random() < .995 else rng.randrange(50_000, 2_999_999)
            latency += rtt // 2
        rx = base + round(newest * 1e6 * (1 + ppm * 1e-6)) + latency
        rows.append({"k": "b", "tx": rx - rtt, "rx": rx, "n": n, "p": payload.hex()})
    rows.append({"k": "t", "end_raw_ns": rows[-1]["rx"] + 1, "end_mono_ns": rows[-1]["rx"] + 1})
    path.write_text("".join(json.dumps(x) + "\n" for x in rows))
    return kind


def host_difference_ns(path):
    """Largest |recompute - parser| per-sample host time, or None when the sample sets differ."""
    from joulewise.external import km003c_parse as primary

    own = r.MeterStream(path, r.Reader("synthetic", []))
    reference = primary.parse(path)
    if reference.fit is None or len(own.times) != len(reference.host_ns) or not own.times:
        return None, own, reference
    return max(abs(a - b) for a, b in zip(own.times, reference.host_ns)), own, reference


class MeterFitDefinitionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def sweep(self):
        results, kinds, fallbacks = {}, {}, 0
        for seed in range(SEEDS):
            path = self.root / f"stream-{seed:03d}.jsonl"
            kinds[seed] = jitter_stream(path, seed)
            difference, own, reference = host_difference_ns(path)
            results[seed] = difference
            fallbacks += not reference.fit.stats["filtered"]
        return results, kinds, fallbacks

    def test_host_times_equal_parser_within_1ns_over_seeded_jitter(self):
        results, kinds, fallbacks = self.sweep()
        # The sweep reaches the fallback and both eligible-cap sides.
        self.assertGreaterEqual(fallbacks, SEEDS // 3)
        self.assertEqual(set(kinds.values()), {"within", "mixed", "fallback"})
        bad = {seed: d for seed, d in results.items() if d is None or d > 1}
        self.assertEqual(bad, {})
        print("meter_fit_property=" + json.dumps({
            "patterns": SEEDS, "fallback_patterns": fallbacks,
            "max_host_difference_ns": max(results.values())}, sort_keys=True))

    def test_counterfactual_old_binning_fails_the_property(self):
        with mock.patch.object(r, "meter_clock_fit", old_clock_fit):
            results, kinds, _ = self.sweep()
        bad = {seed for seed, d in results.items() if d is None or d > 1}
        self.assertTrue(bad)
        # The fallback alone is enough to fail: the old fit refuses those streams.
        self.assertTrue(any(kinds[seed] == "fallback" for seed in bad))
        self.assertTrue(any(kinds[seed] == "within" for seed in bad))
        print("meter_fit_counterfactual=" + json.dumps({
            "patterns": SEEDS, "failing_patterns": len(bad),
            "failing_within_cap": sum(kinds[s] == "within" for s in bad)}, sort_keys=True))

    def test_recompute_imports_no_pipeline_module(self):
        for name in ("independent_recompute_b5.py", "compare_b5_recompute.py"):
            text = (Path(r.__file__).parent / name).read_text()
            self.assertNotRegex(text, r"joulewise\.(external|b5_analysis)")


if __name__ == "__main__":
    unittest.main()
