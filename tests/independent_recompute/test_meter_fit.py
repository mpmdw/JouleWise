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
# Host CLOCK_MONOTONIC_RAW origins: about 17 minutes, 12 days, 46 days and 116 days of uptime.
ORIGINS_NS = (10**12, 10**15, 4 * 10**15, 10**16)
SOL_STREAM = Path(__file__).with_name("meter_streams") / "sol-long-origin-three-polls.jsonl"


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


def absolute_clock_fit(points):
    """The RC-CMP-2 recompute fit (3bf93b25e), kept only as the counterfactual.

    Its residuals, bins and envelope use absolute host ns and fsum/fmean sums,
    so at long uptimes a near-tie can pick another envelope point.
    """
    eligible = [p for p in points if p[3] < r.FIT_RESPONSE_CAP and p[2] < r.FIT_MAX_RTT_MS]
    used = eligible if len(eligible) >= r.FIT_MIN_POINTS else points
    pairs = [(p[0], p[1]) for p in used]
    initial = r.fit_line(pairs)
    if len(pairs) < 2 or initial is None:
        return None
    a0, b0 = initial
    origin, span = pairs[0][0], pairs[-1][0] - pairs[0][0]
    bins = max(r.FIT_MIN_BINS, int(span / r.FIT_BIN_DEVICE_MS))
    width = (span + 1) / bins
    minima = {}
    for x, y in pairs:
        residual = y - (a0 + b0 * x)
        key = min(int((x - origin) / width), bins - 1)
        if key not in minima or residual < minima[key][0]:
            minima[key] = (residual, (x, y))
    envelope = r.fit_line([minima[k][1] for k in sorted(minima)]) if len(minima) >= 2 else None
    a, b = envelope if envelope is not None else initial
    if b <= 0:
        return None
    return {"intercept_ns": a, "slope_ns_per_ms": b, "fit_points": len(points),
            "envelope_offsets_ms": [minima[k][1][0] - pairs[0][0] for k in sorted(minima)],
            "max_above_envelope_ns": max(y - (a + b * x) for x, y in pairs)}


def fit_agreement(path):
    """(max |host difference| ns or None, envelope points identical) against the parser."""
    from joulewise.external import km003c_parse as primary

    calls = []
    original = primary._linear_fit

    def recording(xs, ys):
        calls.append(list(xs))
        return original(xs, ys)
    with mock.patch.object(primary, "_linear_fit", recording):
        difference, own, reference = host_difference_ns(path)
    # The parser's second line fit is the envelope fit, over offsets from its first fit point.
    same_envelope = own.fit is not None and len(calls) == 2 and own.fit["envelope_offsets_ms"] == calls[1]
    return difference, same_envelope


def shifted(path, origin):
    """The same stream later in uptime: every host stamp moved by origin - 10**12 ns."""
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    for row in rows:
        for key in ("tx", "rx", "start_raw_ns", "start_mono_ns", "end_raw_ns", "end_mono_ns"):
            if key in row:
                row[key] += origin - 10**12
    path.write_text("".join(json.dumps(x) + "\n" for x in rows))


def near_tie_stream(path, base, seed, target_ns):
    """RC-CMP-OPUS-REV probe B: two polls in envelope bin 1 whose parser residuals differ by about target_ns.

    A latency trend makes the first-pass slope differ from the envelope slope.
    """
    from joulewise.external import km003c_parse as primary

    rng = random.Random(seed)
    polls, device = [], 0
    for i in range(400):
        newest = device + 2 * DEVICE_STEP_MS
        device += 3 * DEVICE_STEP_MS
        latency = 200_000 + rng.randrange(0, 900_000) + (i * 1500 if i > 200 else 0)
        polls.append([newest, base + newest * 1_000_000 + latency])
    xs = [p[0] for p in polls]

    def residuals():
        x0, y0 = polls[0]
        X, Y = [p[0] - x0 for p in polls], [p[1] - y0 for p in polls]
        a0, b0 = primary._linear_fit(X, Y)
        return [y - (a0 + b0 * x) for x, y in zip(X, Y)]
    span = xs[-1] - xs[0]
    bins = max(4, int(span / 10000))
    width = (span + 1) / bins
    members = [i for i, x in enumerate(xs) if min(int((x - xs[0]) / width), bins - 1) == 1]
    first, last = members[0], members[-1]
    for _ in range(6):
        res = residuals()
        polls[first][1] += round(min(res[i] for i in members) - 50 - res[first])
        res = residuals()
        polls[last][1] += round(res[first] + target_ns - res[last])
    rows = [{"k": "h", "schema": "joulewise.km003c_stream.v1", "rate_idx": 2, "start_raw_ns": base, "start_mono_ns": base}]
    for newest, rx in polls:
        payload = b"".join(struct.pack("<HHiiHHHH", (newest - 40 + 20 * k) % 65536, 0, 10_000_000, 1_000_000, 0, 0, 0, 0)
                           for k in range(3))
        rows.append({"k": "b", "tx": rx - 500_000, "rx": rx, "n": 3, "p": payload.hex()})
    path.write_text("".join(json.dumps(x) + "\n" for x in rows))


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

    def long_origin_streams(self):
        """Seeded jitter at each host origin, the Opus probe's planted near-ties and Sol's three-poll stream."""
        streams = {}
        for origin in ORIGINS_NS:
            for seed in range(0, SEEDS, 4):
                path = self.root / f"jitter-{origin}-{seed:03d}.jsonl"
                jitter_stream(path, seed)
                shifted(path, origin)
                streams[path.name] = path
            for seed in range(40):
                for target in (-0.3, -0.1, 0.0, 0.1, 0.3):
                    path = self.root / f"tie-{origin}-{seed:02d}-{target:+.1f}.jsonl"
                    near_tie_stream(path, origin, seed, target)
                    streams[path.name] = path
        streams[SOL_STREAM.name] = SOL_STREAM
        return streams

    def test_host_times_and_envelope_equal_parser_at_long_host_origins(self):
        # RC-CMP-3 X4: residuals, envelope and height above it relative to the first fit point.
        bad = {}
        for name, path in self.long_origin_streams().items():
            difference, same_envelope = fit_agreement(path)
            if difference is None or difference > 1 or not same_envelope:
                bad[name] = (difference, same_envelope)
        self.assertEqual(bad, {})
        own = r.MeterStream(SOL_STREAM, r.Reader("synthetic", []))
        self.assertEqual(own.times, [10000000001257250, 10000010001119820, 10000020000982388])

    def test_counterfactual_absolute_coordinates_fail_at_long_origins(self):
        # The 3bf93b25e fit (absolute host ns) differs on near-ties and on Sol's stream.
        with mock.patch.object(r, "meter_clock_fit", absolute_clock_fit):
            results = {name: fit_agreement(path) for name, path in self.long_origin_streams().items()}
        bad = {name for name, (difference, same) in results.items() if difference is None or difference > 1 or not same}
        self.assertIn(SOL_STREAM.name, bad)
        self.assertTrue(any(name.startswith("tie-") for name in bad))
        self.assertFalse(any(name.startswith(f"tie-{10**12}-") for name in bad))
        print("meter_fit_long_origin_counterfactual=" + json.dumps({
            "streams": len(results), "failing": len(bad),
            "failing_near_ties": sum(name.startswith("tie-") for name in bad)}, sort_keys=True))

    def test_recompute_imports_no_pipeline_module(self):
        for name in ("independent_recompute_b5.py", "compare_b5_recompute.py"):
            text = (Path(r.__file__).parent / name).read_text()
            self.assertNotRegex(text, r"joulewise\.(external|b5_analysis)")


if __name__ == "__main__":
    unittest.main()
