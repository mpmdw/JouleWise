"""Variants of the freeze-1 native bundles. Use only in a fresh synthetic tree."""
import csv
import json
from bisect import bisect_right
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "suite"))
import run_suite as v1

NS = v1.NS
RAW_OFFSET = 7 * NS
EPOCH_OFFSET = 18000 * NS
STEP = 20_000_000
LEG = "L002"
ELIGIBLE = {"meter_absent", "stream_unclosed", "anchor_unusable", "half_width_over_cap", "not_bracketed"}
CODES = ELIGIBLE | {"boot_mismatch", "ambiguous_overlap"}


def original_bounds(world, leg):
    _, _, bundle = v1.location(world, leg)
    episode = v1.read(bundle / "outputs/align_episode.json")
    v1.require(episode["power_traces"] == episode["clock_mappings"] == [], "embedded traces")
    return episode["start_ns"], episode["end_ns"]


def missing(profile):
    if profile in CODES:
        return {LEG: profile}
    if profile == "three_left":
        return dict.fromkeys(("L002", "L005", "L008"), "meter_absent")
    if profile == "two_levels":
        return dict.fromkeys(("L005", "L012"), "meter_absent")
    return {}


def document(header, batches, trailer, mode):
    first = batches[0]["rx"] - (batches[0]["n"] - 1) * STEP
    last = batches[-1]["rx"]
    h = dict(header, start_raw_ns=first, start_mono_ns=first-RAW_OFFSET,
             start_real_ns=first-RAW_OFFSET+EPOCH_OFFSET)
    t = dict(trailer, end_raw_ns=last, end_mono_ns=last-RAW_OFFSET,
             elapsed_s=(last-first)/NS, polls=len(batches))
    if mode == "meter_absent":
        h.update(status="absent", reason="synthetic device absent")
        t.update(polls=0, stop_reason="absent")
        batches = []
    elif mode == "stream_unclosed":
        return [h, *batches]
    elif mode == "anchor_unusable":
        t["end_raw_ns"] += 1_000_001
    elif mode == "spread":
        t["end_raw_ns"] += 625_000
    elif mode in {"half_width_over_cap", "cap_equal"}:
        # All RTTs outside the fast filter. Unfiltered R is 80 or 79 ms.
        rtt = 80_000_000 if mode == "half_width_over_cap" else 79_000_000
        batches = [dict(b, tx=b["rx"]-rtt) for b in batches]
    elif mode == "boot_mismatch":
        h["start_real_ns"] += 6*NS
        batches = [dict(b, rt=b["rt"]+6*NS) for b in batches]
    return [h, *batches, t]


def partition(world, span, ids, plan):
    """Use disjoint native monitor lifetimes, with genuine pre/post-leg samples."""
    first_path = v1.meter(span)
    with first_path.open() as f:
        header, *batches, trailer = map(json.loads, f)
    bounds = [original_bounds(world, leg) for leg in ids]
    cuts = [(b+c)//2 for (_, b), (c, _) in zip(bounds, bounds[1:])]
    groups = [[] for _ in ids]
    for batch in batches:
        groups[bisect_right(cuts, batch["rx"] - RAW_OFFSET)].append(batch)
    members = []
    for leg, group in zip(ids, groups):
        mode = plan.get(leg, "ok")
        if mode == "not_bracketed":
            # A real restart in the middle of this episode. Each piece fits on its own.
            mid = len(group)//2
            docs = [document(header, chunk, trailer, "ok") for chunk in (group[:mid], group[mid:])]
        else:
            doc = document(header, group, trailer, mode)
            docs = [doc, doc] if mode == "ambiguous_overlap" else [doc]
        for doc in docs:
            path = first_path.with_name(f"stream-{len(members)+1:03d}.jsonl")
            with path.open("w") as dst:
                for row in doc:
                    dst.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
            members.append({"path":path.relative_to(span).as_posix(), "sha256":v1.sha(path)})
    receipt_path = span / "runner_receipt.json"
    receipt = v1.read(receipt_path)
    receipt["feeds"]["meter"]["files"] = members
    v1.dump(receipt_path, receipt)
    v1.reanchor(world, span)


def make(world, profile):
    if profile in {"hold_unknown", "hold_null", "rail_gap", "zero_sd", "bad_leg"}:
        v1.mutate(world, None, "overlap" if profile == "bad_leg" else profile)
    elif profile == "baseline_gap":
        # Zero-length matched tool phase, null GPU baseline, intact DC.
        span, _, bundle = v1.location(world, LEG)
        end = original_bounds(world, LEG)[1]/NS + EPOCH_OFFSET/NS
        path = bundle / "power_trace.csv"
        with path.open(newline="") as src:
            reader = csv.DictReader(src)
            fields = reader.fieldnames
            rows = [r for r in reader if not end-15 < float(r["timestamp_s"]) <= end-13]
        with path.open("w", newline="") as dst:
            writer = csv.DictWriter(dst, fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        v1.reanchor(world, span)
    elif profile != "original":
        plan = missing(profile)
        if not plan:
            v1.require(profile in {"cap_equal", "restart_ok", "spread"}, profile)
            plan = {LEG:profile}
        for ids in (v1.IDS[:3], v1.IDS[3:]):
            if set(ids) & plan.keys():
                span, _, _ = v1.location(world, ids[0])
                partition(world, span, ids, plan)


def expected_h(profile, leg):
    if leg == LEG:
        if profile == "spread":
            return 24_625_000
        if profile == "cap_equal":
            return 100_000_000
        if profile == "half_width_over_cap":
            return 101_000_000
    # A tiny negative fit residual on these re-partitioned streams rounds up by 1 ns.
    if profile in {"three_left", "two_levels"} and leg in {"L006", "L008", "L009", "L011"}:
        return 24_000_001
    return 24_000_000
