"""RC-CMP-OPUS-REV probe: recompute meter_clock_fit vs km003c_parse.clock_fit.

The parser is imported here only as the reference (this probe is not the recompute).
Part A: the shipped seeded jitter generator, but with realistic host CLOCK_MONOTONIC_RAW
magnitudes (days of uptime) instead of base 1e12 ns.
Part B: a planted near-tie between two polls in one envelope bin.
"""
import json, random, struct, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tests.independent_recompute import test_meter_fit as tm
from tests.independent_recompute.support import recompute as r
from joulewise.external import km003c_parse as primary

root = Path(tempfile.mkdtemp())


def sweep(base_offset, seeds=range(240)):
    worst, bad = 0, []
    original = random.Random.randrange
    for seed in seeds:
        path = root / f"a-{base_offset}-{seed}.jsonl"
        tm.jitter_stream(path, seed)
        rows = [json.loads(x) for x in path.read_text().splitlines()]
        for row in rows:  # shift every host stamp by a constant: same stream, later in uptime
            for k in ("tx", "rx", "start_raw_ns", "start_mono_ns", "end_raw_ns", "end_mono_ns"):
                if k in row:
                    row[k] += base_offset
        path.write_text("".join(json.dumps(x) + "\n" for x in rows))
        d, _, _ = tm.host_difference_ns(path)
        if d is None or d > 1:
            bad.append((seed, d))
        worst = max(worst, d or 0)
    return worst, bad


for offset in (0, 10**15, 4 * 10**15):
    worst, bad = sweep(offset)
    print(f"A offset={offset:.0e}ns: max|host diff|={worst} ns; seeds >1ns or refused: {len(bad)} {bad[:5]}")


def planted(base, seed, delta_target):
    """Two candidate minima in bin 1 whose parser residuals differ by about delta_target ns."""
    rng = random.Random(seed)
    polls, device, rows = [], 0, []
    for i in range(400):
        n = 3
        newest = device + (n - 1) * 20
        device += n * 20
        lat = 200_000 + rng.randrange(0, 900_000) + (i * 1500 if i > 200 else 0)  # latency trend: b0 != b1
        polls.append([newest, base + newest * 1_000_000 + lat])
    xs = [p[0] for p in polls]
    def fit_resid():
        x0, y0 = polls[0]
        X = [p[0] - x0 for p in polls]; Y = [p[1] - y0 for p in polls]
        a0, b0 = primary._linear_fit(X, Y)
        return X, [y - (a0 + b0 * x) for x, y in zip(X, Y)]
    span = xs[-1] - xs[0]
    bins = max(4, int(span / 10000)); width = (span + 1) / bins
    bin_of = lambda x: min(int((x - xs[0]) / width), bins - 1)
    members = [i for i, x in enumerate(xs) if bin_of(x) == 1]
    A, B = members[0], members[-1]
    for _ in range(6):
        X, res = fit_resid()
        lo = min(res[i] for i in members)
        polls[A][1] += round(lo - 50 - res[A])      # A becomes the bin minimum
        X, res = fit_resid()
        polls[B][1] += round(res[A] + delta_target - res[B])
    X, res = fit_resid()
    rows.append({"k": "h", "schema": "joulewise.km003c_stream.v1", "rate_idx": 2, "start_raw_ns": base, "start_mono_ns": base})
    for (newest, rx) in polls:
        payload = b"".join(struct.pack("<HHiiHHHH", (newest - 40 + 20 * k) % 65536, 0, 10_000_000, 1_000_000, 0, 0, 0, 0) for k in range(3))
        rows.append({"k": "b", "tx": rx - 500_000, "rx": rx, "n": 3, "p": payload.hex()})
    path = root / f"b-{base}-{seed}.jsonl"
    path.write_text("".join(json.dumps(x) + "\n" for x in rows))
    return path, res[B] - res[A]


hits = []
for base in (10**12, 10**15, 4 * 10**15):
    for seed in range(40):
        for target in (-0.3, -0.1, 0.0, 0.1, 0.3):
            path, gap = planted(base, seed, target)
            d, own, ref = tm.host_difference_ns(path)
            if d is None or d > 1:
                hits.append((base, seed, target, gap, d))
print(f"B planted near-ties: {len(hits)} streams with |host diff| > 1 ns")
for h in hits[:8]:
    print("  base=%.0e seed=%d target=%+.1f parser_residual_gap_ns=%.4f max_host_diff_ns=%s" % h)
from collections import Counter
print("B hits by base:", dict(Counter("%.0e" % h[0] for h in hits)), "of 200 streams per base")
# Cause check: the same planted stream, with the recompute's first-pass residuals taken relative to the first
# point (the parser's coordinates) instead of absolute host ns.
def relative_fit(points):
    x0, y0 = points[0][0], points[0][1]
    shifted = [(x - x0, y - y0, rtt, n) for x, y, rtt, n in points]
    fit = ORIGINAL(shifted)
    if fit:
        fit = {**fit, "intercept_ns": y0 + fit["intercept_ns"] - fit["slope_ns_per_ms"] * x0}
    return fit
ORIGINAL = r.meter_clock_fit
r.meter_clock_fit = relative_fit
still = sum(1 for h in hits if (lambda d: d is None or d > 1)(tm.host_difference_ns(planted(h[0], h[1], h[2])[0])[0]))
print(f"B with relative coordinates in the recompute fit: {still} of {len(hits)} still differ by > 1 ns")
