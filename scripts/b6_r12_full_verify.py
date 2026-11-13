#!/usr/bin/env python3
"""Read a completed full-volume courier-profile archive (any pack) at production size.

No session is generated or changed. All analysis/observation receipts live
outside original session/archive trees. An interrupted generator is refused.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys

from b6_r12_finish import agree
from b6_r12_segments import validate_resume
from b6_r12_monitor_coverage import CONTENTION, session_interval_coverage
from b6_r12_verify import (REPO, child, finalize_manifest, run_option_c,
                          safe_root, session_facts, sha, volume_facts)

LOADED_SHA = sha(Path(__file__))
# Per-pack production expectations, predeclared before collection: registered
# roster/primary counts from the pinned plan_tree stage graph and the published
# production key registry label. The full single-pack session is round 1.
PACK_EXPECTATIONS = {"alpha": {"members": 125, "registry_pack": "ALPHA"},
                     "beta": {"members": 125, "registry_pack": "BETA"},
                     "gamma": {"members": 107, "registry_pack": "GAMMA"}}


def session_id(pack):
    return "r1-" + pack


def verify(outer, stem):
    outer = safe_root(outer)
    if sha(Path(__file__)) != LOADED_SHA:
        raise ValueError("reload changed full-volume verifier")
    if not stem or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in stem):
        raise ValueError("plain new verification name required")
    with (outer / "scheduler.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        control = json.loads((outer / "segments.json").read_bytes())
        root = child(outer, control["main"])
        validate_resume(root, control)
        boundary = control["steps"][-1]["boundary"]
        if boundary["state"] != "ROTATE" or boundary["attempt_count"] != 1:
            raise ValueError("one completed original ordinary desk/attempt required")
        profile = json.loads((outer / "profile-inputs.json").read_bytes())
        manifest = json.loads((root / "manifest.json").read_bytes())
        pack = profile["pack"]
        if (pack not in PACK_EXPECTATIONS or (profile["scenario"], profile["volume"]) != ("plain", "full")
                or not manifest["profile_session"]["full_volume_claim"]
                or not manifest["single_pack"]["full_volume_claim"]
                or not manifest.get("courier_profile")
                or (root / "generator-parent-exit.txt").read_text().strip() != "0"):
            raise ValueError("completed pinned full ALPHA/BETA/GAMMA courier-profile parent required")
        sid = session_id(pack)
        view = outer / stem
        view.mkdir(exist_ok=False)
        snapshots = {}
        for key, name in (("loop_state", "state.json"), ("loop_attempts", "attempts.jsonl")):
            source, target = root / "loop" / name, view / name
            target.write_bytes(source.read_bytes())
            if sha(source) != sha(target):
                raise ValueError("literal loop snapshot changed")
            snapshots[key] = {"snapshot": str(target), "sha256": sha(target)}
        declaration = {"synthetic_only": True, "verifier_sha256": LOADED_SHA,
            "verifier_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
            "monitor_coverage_sha256": sha(Path(__file__).with_name("b6_r12_monitor_coverage.py")),
            "source_root": str(root), "source_generator_commit": manifest["generator_commit"],
            "literal_loop_inputs": snapshots, "boundary": boundary,
            "prediction": "the two predeclared FullProductionSessionTests pass at actual full " + pack.upper() + " size",
            "pack": pack, "session_id": sid, "expectations": PACK_EXPECTATIONS[pack],
            "closed_nine_claim": False}
        (view / "declaration.json").write_text(json.dumps(declaration, indent=2, sort_keys=True) + "\n")
        finalize_manifest(root)
        run_option_c(root, 1, stem=stem, session_id=sid)
        receipt = agree(root, stem)
        pins = json.loads((root / (stem + "-inputs.json")).read_bytes())["external"]
        if any(pins[key] != data["sha256"] for key, data in snapshots.items()):
            raise ValueError("program loop pins differ from literal snapshots")
        facts = session_facts(root, sid)
        volume = volume_facts(root, sid)
        volume["monitor"][CONTENTION]["kinds"]["interval"].update(session_interval_coverage(root, sid))
        native = volume["native_generation"]
        meter_seconds = sum(item["span_s"] for item in volume["meter"])
        if not native or native["primary_stream_duration_s"] <= 0 or meter_seconds <= 0:
            raise ValueError("actual complete native and instrument intervals required")
        ratios = {"native_wall_s": native["wall_s"],
            "primary_seconds": native["primary_stream_duration_s"], "sum_meter_span_s": meter_seconds,
            "native_over_primary": native["wall_s"] / native["primary_stream_duration_s"],
            "native_over_meter_span": native["wall_s"] / meter_seconds}
        courier = root / "sessions" / sid / "courier-program"
        courier_records = []
        for path in sorted(courier.glob("*.json")):
            value = json.loads(path.read_bytes())
            stdin = child(root, str(path.parent / value["stdin"]))
            courier_records.append({**value, "record_sha256": sha(path), "stdin_sha256": sha(stdin)})
        numbers = json.loads((root / (stem + "-numbers.json")).read_bytes())
        facts.update(volume=volume, native_time_ratios=ratios, courier_records=courier_records,
                     quantity_keys=sorted(numbers["sessions"][sid]["quantities"]),
                     pack=pack, expectations=PACK_EXPECTATIONS[pack],
                     production_exit=receipt["exit_code"],
                     comparator_agrees=receipt["option_c"]["comparator"]["pass"])
        observations = view / "full-session-observations.json"
        observations.write_text(json.dumps(facts, indent=2, sort_keys=True) + "\n")
        tests = ["tests.test_b6_r12_session_fixture.FullProductionSessionTests"]
        result = subprocess.run([sys.executable, "-B", "-m", "unittest", *tests], cwd=REPO,
            env={**os.environ, "R12_FULL_SESSION": str(view)}, check=False)
        (view / "receipt.json").write_text(json.dumps({**declaration,
            "tests": tests, "test_exit": result.returncode,
            "observations_sha256": sha(observations), "native_time_ratios": ratios,
            "program_receipt_sha256": sha(root / (stem + "-receipt.json")),
            "reader_measurement": receipt["process_measurement"],
            "time_wrapper_exit": receipt["time_wrapper_exit"]}, indent=2, sort_keys=True) + "\n")
        return result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort-root", required=True, type=Path)
    parser.add_argument("--stem", required=True)
    args = parser.parse_args()
    return verify(args.cohort_root, args.stem)


if __name__ == "__main__":
    raise SystemExit(main())
