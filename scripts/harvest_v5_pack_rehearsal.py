#!/usr/bin/env python3
"""Immutable r1 archive, then a distinct G7-authenticated derived evaluation."""
from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise import arm_readiness as readiness, t0_rehearsal
from joulewise import v5_qualification as q
from scripts import rehearse_t0_unattended as loader

SCHEMA = "joulewise.harvest_v5_pack_rehearsal.v1"


def with_g7(bundle, locator, derived):
    path = q.authenticated_reference(locator)
    expected = bundle.custody_root.with_name(bundle.custody_root.name + "-g7-control") / "night/g7_refusal.json"
    if path != expected:
        raise q.HarvestRefusal("g7_control_not_sibling")
    t0_rehearsal.validate_g7_control(q.read(path))
    artifact = replace(loader._artifact(path.parent, path), relative_path=str(path))
    value = dict(bundle.manifest.value)
    value["records"] = {**value["records"], "g7_control": locator}
    manifest_path = derived / loader.MANIFEST_NAME
    q.write(manifest_path, value)
    manifest = replace(bundle.manifest, path=manifest_path, value=value,
                       raw=manifest_path.read_bytes(), sha256=q.sha(manifest_path))
    artifacts = tuple(item for item in bundle.artifacts
                      if item.relative_path not in {loader.MANIFEST_NAME, str(path)})
    return replace(bundle, manifest=manifest, artifacts=(*artifacts, manifest, artifact),
                   record_paths={**bundle.record_paths, "g7_control": str(path)})


def evaluate(bundle, *, transcript):
    verdict = q.captured_call(t0_rehearsal.evaluate_rehearsal, transcript, bundle)
    # The canonical evaluator is the sole authority for all ten gates. Its
    # messages/evidence are retained privately, never projected recursively.
    q.write(Path(transcript).with_suffix(".json"), verdict)
    gates = [{"gate_id": row["gate_id"], "status": row["status"]}
             for row in verdict["gates"]]
    if ([row["gate_id"] for row in gates] != [f"G{i}" for i in range(1, 11)]
            or any(row["status"] not in {"PASS", "FAIL", "UNRULED"} for row in gates)):
        raise q.HarvestRefusal("rehearsal_evaluator_wire_invalid")
    passed = verdict["overall_verdict"] == "PASS" and all(row["status"] == "PASS" for row in gates)
    return {"schema_version": "joulewise.t0_unattended_rehearsal_verdict.v1",
            "overall_verdict": "PASS" if passed else "FAIL", "gates": gates,
            "gate_counts": {s: sum(row["status"] == s for row in gates) for s in ("PASS", "FAIL", "UNRULED")}}


def harvest(args, *, now=None, clear=q.group_clear, load=loader.load_evidence_bundle):
    kwargs = {"clear": clear}
    if now is not None:
        kwargs["now"] = now
    plan = q.load_plan(args.plan, "T0_REHEARSAL", **kwargs)
    custody = Path(plan.custody_root)
    destination = args.archive_root.absolute()
    sources = {"night-custody": custody, "chain": Path(plan.chain_path),
               "chain-sidecar": Path(plan.chain_sha256_path)}
    boundary = q.authenticated_reference({"path": str(args.battery_evidence.absolute()),
                                          "sha256": args.battery_evidence_sha256})
    sources["battery-boundaries"] = boundary
    sources.update(q.boundary_sources(boundary))
    for i, path in enumerate(getattr(args, "replay_source", []) or []):
        sources[f"replay-{i:03}"] = path.absolute()
    locator = None
    if args.g7_control is not None:
        if args.initial_harvest is None:
            raise q.HarvestRefusal("g7_requires_initial_harvest")
        initial = q.read(args.initial_harvest / "harvest.json")
        if (initial.get("schema") != SCHEMA or initial.get("stage") != "initial"
                or initial.get("plan_sha256") != q.sha(args.plan)
                or initial.get("g7_control_absent_at_initial") is not True):
            raise q.HarvestRefusal("initial_harvest_identity_invalid")
        locator = q.reference(args.g7_control.absolute())
        sources["g7-control"] = q.authenticated_reference(locator).parent.parent
    previous = getattr(args, "previous_harvest", None) or args.initial_harvest
    control_root = custody.with_name(custody.name + "-g7-control")
    if locator is None and previous is None and control_root.exists():
        raise q.HarvestRefusal("initial_harvest_must_precede_g7")
    if locator and getattr(args, "previous_harvest", None):
        old = q.read(args.previous_harvest / "harvest.json")
        if old.get("initial_harvest") != q.reference(args.initial_harvest / "harvest.json"):
            raise q.HarvestRefusal("reharvest_initial_record_changed")
    original = q.archive_sources(sources, destination, previous=previous,
                                 added=("g7-control",) if locator and previous == args.initial_harvest else ())
    record = {"schema": SCHEMA, "occurrence": "r1", "plan_id": q.identifier(plan.plan_id),
              "plan_sha256": q.sha(args.plan), "stage": "final" if locator else "initial",
              "verdict": "REFUSED", "cause_codes": [], "cause_classes": []}
    record["g7_control_absent_at_initial"] = locator is None and not control_root.exists()
    if locator:
        record["initial_harvest"] = q.reference(args.initial_harvest / "harvest.json")
    try:
        derived = destination / "derived"
        derived.mkdir()
        if not (custody / "night/chain.started").exists():
            record.update(verdict="NULL", cause_codes=["chain_never_started"])
        else:
            bundle = load(custody)
            if locator:
                bundle = with_g7(bundle, locator, derived)
            elif "g7_control" in bundle.record_paths:
                raise q.HarvestRefusal("initial_harvest_must_precede_g7")
            verdict = evaluate(bundle, transcript=destination / "withheld/t0-evaluation.txt")
            q.write(derived / "t0-rehearsal-verdict.json", verdict)
            causes = [f"{row['gate_id'].lower()}_not_passed" for row in verdict["gates"] if row["status"] != "PASS"]
            if locator is None and "g7_not_passed" not in causes:
                causes.append("g7_not_passed")
            if not q.battery_boundaries(boundary, args.battery_evidence_sha256, plan.plan_id):
                causes.append("battery_boundary_not_passed")
            record.update(verdict="RECOVER" if causes else "PASS", cause_codes=causes,
                          cause_classes=["qualification"] if causes else [],
                          gate_counts=verdict["gate_counts"],
                          evaluation=q.reference(derived / "t0-rehearsal-verdict.json"))
        q.unchanged(sources, original)
        if not clear(custody / "night", plan_id=plan.plan_id):
            raise q.HarvestRefusal("launcher_group_alive")
    except Exception as error:
        record.update(verdict="REFUSED", cause_codes=[str(error) if isinstance(error, q.HarvestRefusal)
                      else "archive_authentication_or_evaluator_fault"], cause_classes=["tooling"])
    record.update(q.disposition("r1", record["verdict"], record["cause_classes"]))
    if record["stage"] == "initial" and record["cause_codes"] == ["g7_not_passed"]:
        record.update(end_state=False, next_step="external_g7_control_then_final_harvest")
    return q.publish(destination, record)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--replay-source", type=Path, action="append", default=[])
    parser.add_argument("--battery-evidence", type=Path, required=True)
    parser.add_argument("--battery-evidence-sha256", required=True)
    parser.add_argument("--g7-control", type=Path)
    parser.add_argument("--initial-harvest", type=Path)
    parser.add_argument("--previous-harvest", type=Path)
    args = parser.parse_args(argv)
    try:
        record = harvest(args)
    except Exception:
        q.preflight_refusal(SCHEMA)
        return 3
    q.public_print(record)
    return 0 if record["verdict"] in {"PASS", "NULL"} else 3 if record["verdict"] == "REFUSED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
