"""RC-CMP-OPUS-REV-2 Q3: recompute MeterStream fit vs km003c_parse on adversarial synthetic streams.

Run from the repo root:
TMPDIR=/tmp/rcopusrev2 PYTHONPATH=.:tests PYTHONDONTWRITEBYTECODE=1 python3.13 .codex-report/rc-cmp-opus-rev-2/probe_meter_adversarial.py
"""
import collections
import json
import random
import struct
import sys
import tempfile
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[2]), str(Path(__file__).resolve().parents[2] / "tests")]
from tests.independent_recompute import test_meter_fit as tm  # noqa: E402
from joulewise.external import km003c_parse as primary  # noqa: E402  (reference only)

r = tm.r
root = Path(tempfile.mkdtemp())


def write(path, base, polls, header_extra=None):
    """polls: (device_ms_of_newest, n, rx_ns_offset, rtt_ns)."""
    rows = [{"k": "h", "schema": "joulewise.km003c_stream.v1", "rate_idx": 2,
             "start_raw_ns": base, "start_mono_ns": base, **(header_extra or {})}]
    for newest, n, rx_off, rtt in polls:
        first = newest - (n - 1) * 20
        payload = b"".join(struct.pack("<HHiiHHHH", (first + k * 20) % 65536, 0, 10_000_000, 1_000_000, 0, 0, 0, 0)
                           for k in range(n))
        rx = base + rx_off
        rows.append({"k": "b", "tx": rx - rtt, "rx": rx, "n": n, "p": payload.hex()})
    last = max(row["rx"] for row in rows[1:])
    rows.append({"k": "t", "end_raw_ns": last + 1, "end_mono_ns": last + 1})
    path.write_text("".join(json.dumps(x) + "\n" for x in rows))


def compare(path):
    try:
        diff, same = tm.fit_agreement(path)
    except Exception as exc:  # either side raising is reported, not hidden
        return "raised " + type(exc).__name__
    own = r.MeterStream(path, r.Reader("synthetic", []))
    ref = primary.parse(path)
    if diff is None:
        return f"not_compared own_fit={own.fit is not None} ref_fit={ref.fit is not None} own_n={len(own.times)} ref_n={len(ref.host_ns)}"
    return diff, same


def family(name, make, seeds):
    results = collections.Counter()
    worst = 0
    for seed in range(seeds):
        rng = random.Random(seed)
        path = root / f"{name}-{seed}.jsonl"
        make(path, rng)
        out = compare(path)
        if isinstance(out, tuple):
            worst = max(worst, out[0])
            results["diff>0" if out[0] else ("same_env" if out[1] else "env_differs")] += 1
        else:
            results[out.split(" ")[0] + ("" if out.startswith("raised") else "")] += 1
            if out.startswith("not_compared") and results["shown_" + name] == 0:
                results["shown_" + name] += 1
                print("   ", name, seed, out)
    print(f"{name}: streams={seeds} max_host_diff_ns={worst} {dict(results)}")


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
        write(path, base, polls)
    return make


family("int64_scale_origin_9e18", stream(9 * 10**18, 800), 60)
family("origin_2p53_plus", stream(2**53 + 12345, 800), 60)
family("exact_ties_no_jitter_1e16", stream(10**16, 800, tie=True), 30)
family("rtt_at_3ms_cap", stream(10**15, 600, rtt=(2_999_000, 3_001_000)), 60)
family("n_at_63_cap", stream(10**15, 600, n=(60, 64)), 40)
family("negative_rtt", stream(10**15, 600, rtt=(-2_000_000, 2_000_000)), 60)
family("rx_out_of_order", stream(10**15, 600, shuffle=True), 60)
family("duplicated_polls", stream(10**15, 600, dup=True), 40)
family("device_wrap_gaps", stream(10**15, 1500, gap_every=97), 40)
family("fallback_19_eligible", stream(10**15, 19), 60)
family("two_polls", stream(10**15, 2), 30)
family("negative_drift_ppm", stream(4 * 10**15, 800, ppm=-80.), 40)
