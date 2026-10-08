#!/usr/bin/env python3
"""Assemble one occurrence's retained arm, publication and T-0 ioreg records.

This performs no probe. T-0 inputs are the observation and exact stdout retained
by the T-0 capture, never a later reconstruction of the author's reading.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise import v5_qualification as q

SCHEMA = "joulewise.v5_qualification_battery_boundaries.v1"


def assemble(plan_id, observations, output, *, lifecycle=None):
    q.identifier(plan_id)
    if set(observations) != set(q.BATTERY_BOUNDARY_PHASES):
        raise q.HarvestRefusal("battery_boundary_census_invalid")
    # Authenticate before publishing a create-once manifest. Failed physics
    # readings remain assemblable, so harvest can classify the recorded result.
    value = {"schema": SCHEMA, "plan_id": plan_id, "observations": observations,
             "lifecycle": lifecycle}
    for role, item in observations.items():
        if set(item) != {"record", "raw"}:
            raise q.HarvestRefusal("battery_boundary_locator_invalid")
        record = q.read(q.authenticated_reference(item["record"]))
        raw = q.authenticated_reference(item["raw"])
        if (record.get("plan_id") != plan_id or record.get("phase") != q.BATTERY_BOUNDARY_PHASES[role]
                or record.get("raw_stdout_sha256") != q.sha(raw)):
            raise q.HarvestRefusal("battery_boundary_digest_or_identity_mismatch")
    # The same replay as both harvesters, using a temporary in-memory-free
    # validation file within the caller's output directory.
    import tempfile
    output = Path(output).absolute()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="battery-boundaries-", dir=output.parent) as directory:
        candidate = Path(directory) / "manifest.json"
        q.write(candidate, value)
        q.battery_boundaries(candidate, q.sha(candidate), plan_id)
    q.write(output, value)
    return q.reference(output)


def retain_t0_capture(path, plan_id, directory):
    path = Path(path).absolute()
    observation, raw = q.captured_battery_observation(path)
    if observation.get("plan_id") != plan_id or observation.get("phase") != q.BATTERY_BOUNDARY_PHASES["t0"]:
        raise q.HarvestRefusal("t0_battery_capture_identity_mismatch")
    observation = {**observation, "source_capture": q.reference(path)}
    return q.persist_battery_observation(directory, "battery-float-t0", observation, raw)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--prepare", type=Path, required=True)
    parser.add_argument("--arm-check", type=Path, required=True)
    parser.add_argument("--publication", type=Path, required=True)
    parser.add_argument("--t0-receipt", type=Path, required=True)
    parser.add_argument("--t0-capture", type=Path, help="Native T-0 observation or C3 receipt with retained raw stdout")
    for role in q.BATTERY_BOUNDARY_PHASES:
        parser.add_argument(f"--{role}-record", type=Path, required=role != "t0")
        parser.add_argument(f"--{role}-raw", type=Path, required=role != "t0")
    args = parser.parse_args(argv)
    if args.t0_capture is not None:
        if args.t0_record is not None or args.t0_raw is not None:
            parser.error("--t0-capture excludes --t0-record/--t0-raw")
    elif args.t0_record is None or args.t0_raw is None:
        parser.error("provide --t0-capture or both --t0-record and --t0-raw")
    observations = {role: {kind: q.reference(getattr(args, f"{role}_{kind}").absolute())
                          for kind in ("record", "raw")} for role in ("arm", "publication")}
    observations["t0"] = (retain_t0_capture(args.t0_capture, args.plan_id, args.output.absolute().parent)
                          if args.t0_capture else {kind: q.reference(getattr(args, f"t0_{kind}").absolute())
                                                  for kind in ("record", "raw")})
    lifecycle = {name: q.reference(getattr(args, name).absolute())
                 for name in ("plan", "prepare", "arm_check", "publication", "t0_receipt")}
    result = assemble(args.plan_id, observations, args.output, lifecycle=lifecycle)
    print(f"battery_boundaries={result['path']} sha256={result['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
