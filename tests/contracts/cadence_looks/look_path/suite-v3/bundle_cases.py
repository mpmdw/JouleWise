"""Freeze-3 synthetic close mutations. All source trees come from the freeze-1 archive."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "suite-v2"))
import fixtures as old

v1 = old.v1
TARGET = "L002"


def catalog():
    return v1.read(Path(__file__).with_name("vectors.json"))


def source_number(number):
    return f"hazards/meter/stream-{int(number):03d}.jsonl"


def rows(path):
    with path.open() as stream:
        return [json.loads(line) for line in stream]


def emit(path, records):
    with path.open("w") as out:
        for row in records:
            out.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def make_stream(base, mode):
    h, *batches, t = base
    half = len(batches) // 2
    if mode.startswith("partial"):
        batches = batches[:half]
    if mode.startswith("open_late_missing_raw") or mode == "no_start_raw_late":
        batches = batches[half:]
    flavor = {"absent": "meter_absent", "boot": "boot_mismatch"}.get(mode, "ok")
    if "cap" in mode:
        flavor = "half_width_over_cap"
    doc = old.document(h, batches, t, flavor)
    if mode.endswith("_boot"):
        doc[0]["start_real_ns"] += 6 * old.NS
        for poll in doc[1:-1]:
            poll["rt"] += 6 * old.NS
    if mode.startswith("open_late_missing_raw") or mode == "no_start_raw_late":
        del doc[0]["start_raw_ns"]
    if mode.startswith("open_late_missing_raw"):
        doc.pop()
    return doc


def materialize(world, profile_name, profile):
    if profile_name == "pair":
        return
    if "legacy" in profile:
        old.make(world, profile["legacy"])
        return
    span, _, _ = v1.location(world, TARGET)
    old.partition(world, span, v1.IDS[:3], {})
    original = rows(span / source_number(2))
    numbers = [1, 2, 3]
    for index, mode in enumerate(profile["members"]):
        number = 2 if index == 0 else 3 + index
        emit(span / source_number(number), make_stream(original, mode))
        if number not in numbers:
            numbers.append(number)
    side = profile.get("side")
    if side == "all_pilot_absent":
        for number in (1, 3):
            path = span / source_number(number)
            emit(path, make_stream(rows(path), "absent"))
    elif side == "L003_remove_end_mono":
        extra = rows(span / source_number(3))
        del extra[-1]["end_mono_ns"]
        emit(span / source_number(4), extra)
        numbers.append(4)
    elif side == "L001_end_at_L002_start":
        path = span / source_number(1)
        extra = rows(path)
        start, _ = old.original_bounds(world, TARGET)
        extra[-1].update(end_mono_ns=start, end_raw_ns=start + old.RAW_OFFSET,
                         elapsed_s=(start - extra[0]["start_mono_ns"]) / old.NS)
        emit(path, extra)
    receipt_path = span / "runner_receipt.json"
    receipt = v1.read(receipt_path)
    receipt["feeds"]["meter"]["files"] = [
        {"path": source_number(n), "sha256": v1.sha(span / source_number(n))} for n in numbers
    ]
    v1.dump(receipt_path, receipt)
    v1.reanchor(world, span)


def leg_codes(profile_name, profile):
    if profile_name == "absent_span":
        return dict.fromkeys(v1.IDS[:3], "meter_absent")
    if "legacy" in profile:
        return dict.fromkeys(old.missing(profile["legacy"]), "not_bracketed")
    return {TARGET: profile["code"]} if profile["code"] != "ok" else {}


def expected_candidates(profile):
    return {source_number(number): sorted(failures)
            for number, failures in profile["candidates"].items()}
