"""Oracles read actual synthetic outputs and observations from the installed worker."""
import json
import math

from bundle_cases import TARGET, old, v1


def outputs(bench):
    parent = bench / "private/lm-ctl-01"
    return parent / "RESTRICTED/controls.json", bench / "public/lm-ctl-01/PUBLIC.json"


def check_outputs(bench, stage_pin, affected):
    private, public = outputs(bench)
    events = [json.loads(s) for s in (bench / "events.jsonl").read_text().splitlines()]
    v1.require(events[:3] == ["claim", "start", "first_read"] and "ctl_value_decode" in events[3:]
               and all(events.count(tag) == 1 for tag in events[:3]), "once-only boundary")
    v1.require((private.parent.parent / "read-started").is_file() and
               {p.name for p in private.parent.iterdir()} == {"controls.json", "stdout", "stderr"}
               and list(public.parent.iterdir()) == [public], "actual release files")
    public_doc = v1.read(public)
    report = v1.read(private)
    v1.require(public_doc == v1.read(bench / "registered-public.json") and
               set(public_doc) == {"look_id", "stage1_sha256", "manifest_sha256", "commit", "n_legs"}
               and public_doc["stage1_sha256"] == stage_pin and public_doc["n_legs"] == 12
               and public_doc["look_id"] == "lm-ctl-01", "public evidence")
    if not affected:
        v1.check_report(public_doc, report, stage_pin, {})
        return
    v1.require([r["leg_id"] for r in report["legs"]] == v1.IDS and
               report["aligned_power"]["qualified"] == "yes", "exception changed rail qualification")
    for row in report["legs"]:
        leg = row["leg_id"]
        v1.require(set(row["channels"]) == set(v1.EXCESS), "four channels")
        for key, channel in row["channels"].items():
            if key == "dc_in" and leg in affected:
                v1.require(channel["reason"] == "trace_or_clock_unavailable" and channel["baseline_w"] is None
                           and "absolute" not in channel, "wrong local DC absence")
            else:
                base = 10 + int(leg[1:]) if key == "dc_in" else v1.BASE[key]
                v1.numeric(channel["baseline_w"], base, "surviving baseline")
                v1.require(channel["absolute"]["phases"]["prefill"]["joules"] > 0, "missing integral")
    for key, fit in report["dose_response"].items():
        kept = set(v1.HIDDEN) - (set(affected) if key == "dc_in" else set())
        v1.require(set(fit["legs"]) == kept, "surviving fit membership")
        v1.numeric(fit["slope"], v1.EXCESS[key] * .01, "surviving slope")


def inspect_pair(world, normal, zero):
    for left, right in zip(outputs(normal), outputs(zero), strict=True):
        v1.require(left.read_bytes() == right.read_bytes(), "H changed serialized " + left.name)
    _, runtime, _ = v1.location(world, TARGET)
    end = v1.read(runtime / "script-work.json")["steps"][-1]["ended_ns"] - 40 * old.NS
    bounds, flags = [], []
    for bench, forced in ((normal, False), (zero, True)):
        observed = v1.read(bench / "kernel-observed.json")
        v1.require(set(observed["dc_mappings"]) == set(v1.IDS), "all delivered DC maps")
        for leg, mapping in observed["dc_mappings"].items():
            cert = v1.read(bench / "private/lm-ctl-01/certificates" / (leg + ".json"))
            v1.require(type(mapping["uncertainty_ns"]) is int and cert["H_ns"] == 24_000_000 and
                       mapping["uncertainty_ns"] == (0 if forced else cert["H_ns"]) and
                       mapping["offset_ns"] == -old.RAW_OFFSET and
                       mapping["method"] == "km003c_raw_monotonic_pairs.v1", "actual kernel input")
        interval = observed["interval"]
        v1.require((interval["leg_id"], interval["source"], interval["channel"], interval["start_ns"],
                    interval["end_ns"]) == (TARGET, "wall_meter", "dc_in", end - 40 * old.NS, end),
                   "observed real baseline check interval")
        v1.numeric(interval["joules"], 480, "12 W check window")
        v1.require(interval["adjacent_peak_w"] == [12, 12] and "trace.partial_coverage" not in interval["flags"],
                   "endpoint peaks or coverage")
        bounds.append(interval["half_width_j"])
        flags.append((interval["flags"], interval["joules"]))
    v1.require(flags[0] == flags[1] and math.isclose(bounds[0] - bounds[1], 24 * 24_000_000 / old.NS,
               rel_tol=0, abs_tol=1e-12), "frozen interval uncertainty response")
