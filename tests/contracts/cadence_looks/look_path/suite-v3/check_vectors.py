"""Check the frozen bundle mutations against public, hash-identified decoder and kernel source."""
from bisect import bisect_left, bisect_right
from fractions import Fraction
from importlib import import_module
import math
from pathlib import Path
import tempfile

from bundle_cases import TARGET, catalog, expected_candidates, leg_codes, materialize, old, v1

ORDER = ("boot_mismatch", "stream_unclosed", "anchor_unusable", "half_width_over_cap", "not_bracketed")


def classify(kp, streams, episode):
    start, end = episode["start_ns"], episode["end_ns"]
    stamps = episode["hardware"]["paired_clock_stamps_ns"][0]
    midpoint = (stamps["monotonic_before_ns"] + stamps["monotonic_after_ns"]) // 2
    epoch_offset = stamps["epoch_ns"] - midpoint
    failures = {}
    widths = {}
    for name, s in streams.items():
        if not s.present:
            continue
        h, t = s.header, s.trailer or {}
        lo, hi = h.get("start_mono_ns"), t.get("end_mono_ns")
        ra, rb = h.get("start_raw_ns"), t.get("end_raw_ns")
        anchors = all(type(x) is int for x in (lo, hi, ra, rb))
        if anchors and (hi < start or lo > end):
            continue
        failed = []
        if lo is not None and abs(h["start_real_ns"] - lo - epoch_offset) > 5 * old.NS:
            failed.append("boot_mismatch")
        if not t:
            failed.append("stream_unclosed")
        offset = kp.raw_offset_ns(s)
        if offset is None or s.fit is None:
            failed.append("anchor_unusable")
        else:
            stats = s.fit.stats
            rtt = kp.FIT_MAX_RTT_MS if stats["filtered"] else stats["request_rtt_ms_max"]
            half = abs(rb - hi - offset) + 1_000_000 + kp.STEP_MS[h["rate_idx"]] * 1_000_000
            half += math.ceil(1_000_000 * (max(0, -Fraction(stats["excess_latency_ms_min"])) + Fraction(rtt)))
            widths[name] = half
            if half > 100_000_000:
                failed.append("half_width_over_cap")
        if ((lo is not None and lo > start) or (hi is not None and hi < end)
                or (offset is not None and s.host_ns and
                    (s.host_ns[0] - offset > start or s.host_ns[-1] - offset < end))):
            failed.append("not_bracketed")
        failures[name] = sorted(failed)
    passed = [name for name, failed in failures.items() if not failed]
    if passed:
        code = "ok" if len(passed) == 1 else "ambiguous_overlap"
    elif not any(s.present for s in streams.values()):
        code = "meter_absent"
    elif not failures:
        code = "not_bracketed"
    else:
        code = next(token for token in ORDER if any(token in faults for faults in failures.values()))
    return code, failures, widths


def kernel_probe(stream, world, width):
    from joulewise.align import attribution as kernel
    from joulewise.align.records import ClockMapping, PowerTrace
    pin = "805d5d5e0dde33ab54ed943b883f95e5f738bf2391a8c21300f569a0cabb014d"
    v1.require(v1.sha(Path(kernel.__file__)) == pin, "attribution source")
    _, runtime, bundle = v1.location(world, TARGET)
    ep = v1.read(bundle / "outputs/align_episode.json")
    times = [raw - old.RAW_OFFSET for raw in stream.host_ns]
    a = bisect_right(times, ep["start_ns"]) - 1
    b = bisect_left(times, ep["end_ns"]) + 1
    tr = PowerTrace("wall_meter", "dc_in", "fixture.raw", tuple(stream.host_ns[a:b]),
                    tuple(stream.watts[a:b]), "W", old.STEP)
    stop = v1.read(runtime / "script-work.json")["steps"][-1]["ended_ns"] - 40 * old.NS
    start = stop - 40 * old.NS
    estimates = []
    for h in (width, 0):
        mapping = ClockMapping(tr.clock_domain, ep["clock_domain"], -old.RAW_OFFSET, h,
                               "km003c_raw_monotonic_pairs.v1")
        estimates.append(kernel.trace_energy(tr, start, stop, mapping=mapping))
    ruled, zero = estimates
    v1.require(width == 24_000_000 and ruled.flags == zero.flags and
               "trace.partial_coverage" not in ruled.flags and ruled.joules == zero.joules,
               "central result/coverage")
    v1.numeric(ruled.joules, 480, "40 s at 12 W")
    v1.require(math.isclose(ruled.half_width_j-zero.half_width_j, 24 * width / old.NS,
                            rel_tol=0, abs_tol=1e-12), "endpoint bound")
    return ruled.half_width_j - zero.half_width_j


def main():
    from check_inputs import READER_PINS
    kp = import_module("joulewise.external.km003c_parse")
    v1.require(v1.sha(Path(kp.__file__)) == READER_PINS[kp.__name__], "decoder source")
    for name, profile in catalog()["profiles"].items():
        with tempfile.TemporaryDirectory(prefix="ctl3-source-") as workspace:
            world = Path(workspace)
            v1.unpack(world)
            materialize(world, name, profile)
            expected = leg_codes(name, profile)
            checks = v1.read(world / "authority/check.json")
            for span_id, inventory in checks.items():
                span = world / "spans" / span_id
                v1.require(v1.sha(span / "runner_receipt.json") == inventory["runner_receipt.json"], "close")
                receipt = v1.read(span / "runner_receipt.json")
                streams = {}
                for entry in receipt["feeds"]["meter"]["files"]:
                    path = span / entry["path"]
                    v1.require(v1.sha(path) == entry["sha256"], "stream binding")
                    streams[entry["path"]] = kp.parse(path)
                for leg in receipt["roster"]:
                    _, _, bundle = v1.location(world, leg)
                    ep = v1.read(bundle / "outputs/align_episode.json")
                    v1.require(ep["power_traces"] == ep["clock_mappings"] == [], "episode shape")
                    code, members, widths = classify(kp, streams, ep)
                    v1.require(code == expected.get(leg, "ok"), f"{name}/{leg} condition {code}")
                    if leg == TARGET:
                        v1.require(members == expected_candidates(profile), f"{name} candidate failures {members}")
                        if name == "pair":
                            picked, = members
                            delta = kernel_probe(streams[picked], world, widths[picked])
                            print(f"L002 synthetic kernel bound difference {delta:.3f} J", flush=True)
        print("PASS fixture", name, flush=True)


if __name__ == "__main__":
    main()
