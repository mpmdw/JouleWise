#!/usr/bin/env python3
"""Blind immutable s1 qualification harvest, independent of its G2-b verdict."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise import arm_readiness as readiness, t0_rehearsal
from joulewise import v5_qualification as q
from scripts import rehearse_t0_unattended as loader

SCHEMA = "joulewise.harvest_v5_qualification.v1"


def evaluate(bundle, *, transcript):
    verdict = q.captured_call(t0_rehearsal.evaluate_qualification, transcript, bundle)
    # The canonical evaluator is the sole authority for all ten gates. Its
    # messages/evidence are retained privately, never projected recursively.
    q.write(Path(transcript).with_suffix(".json"), verdict)
    gates = [{"gate_id": row["gate_id"], "status": row["status"],
              **({"basis": row["basis"]} if row["gate_id"] in {"G6", "G7"} else {})}
             for row in verdict["gates"]]
    if ([row["gate_id"] for row in gates] != [f"G{i}" for i in range(1, 11)]
            or any(row["status"] not in {"PASS", "FAIL", "UNRULED", "NOT_APPLICABLE"} for row in gates)
            or any(row != {"gate_id": row["gate_id"], "status": "NOT_APPLICABLE", "basis": "retired_by_ruling_76"}
                   for row in gates if row["gate_id"] in {"G6", "G7"})
            or any(row["status"] == "NOT_APPLICABLE" for row in gates if row["gate_id"] not in {"G6", "G7"})):
        raise q.HarvestRefusal("qualification_evaluator_wire_invalid")
    passed = verdict["overall_verdict"] == "PASS" and all(row["status"] == "PASS" for row in gates if row["gate_id"] not in {"G6", "G7"})
    return {"schema_version": "joulewise.v5_s1_qualification_verdict.v1",
            "purpose": "G2B_SHAKEDOWN", "overall_verdict": "PASS" if passed else "FAIL", "gates": gates,
            "gate_counts": {s: sum(row["status"] == s for row in gates) for s in ("PASS", "FAIL", "UNRULED", "NOT_APPLICABLE")}}


def load_qualification(custody):
    return loader.load_evidence_bundle(custody, manifest_name=loader.QUALIFICATION_MANIFEST_NAME, require_observed=True)


def harvest(args, *, now=None, clear=q.group_clear, load=load_qualification):
    kwargs = {"clear": clear}
    if now is not None:
        kwargs["now"] = now
    plan = q.load_plan(args.plan, "G2B_SHAKEDOWN", **kwargs)
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
    original = q.archive_sources(sources, destination, previous=getattr(args, "previous_harvest", None))
    record = {"schema": SCHEMA, "occurrence": "s1", "verdict_kind": "qualification",
              "purpose": "G2B_SHAKEDOWN", "plan_id": q.identifier(plan.plan_id),
              "plan_sha256": q.sha(args.plan), "verdict": "REFUSED", "cause_codes": [], "cause_classes": []}
    try:
        derived = destination / "derived"
        derived.mkdir()
        if not (custody / "night/chain.started").exists():
            record.update(verdict="NULL", cause_codes=["chain_never_started"])
        else:
            if (custody / "night/producer-faults.jsonl").exists():
                raise q.HarvestRefusal("qualification_observation_producer_fault")
            bundle = load(custody)
            record["desk_stages"] = q.s1_desk_records(bundle)
            verdict = evaluate(bundle, transcript=destination / "withheld/t0-evaluation.txt")
            q.write(derived / "s1-qualification-verdict.json", verdict)
            causes = [f"{row['gate_id'].lower()}_not_passed" for row in verdict["gates"]
                      if row["gate_id"] not in {"G6", "G7"} and row["status"] != "PASS"]
            if not q.battery_boundaries(boundary, args.battery_evidence_sha256, plan.plan_id):
                causes.append("battery_boundary_not_passed")
            record.update(verdict="FAIL" if causes else "PASS", cause_codes=causes,
                          cause_classes=["qualification"] if causes else [],
                          gate_counts=verdict["gate_counts"],
                          evaluation=q.reference(derived / "s1-qualification-verdict.json"))
        q.unchanged(sources, original)
        if not clear(custody / "night", plan_id=plan.plan_id):
            raise q.HarvestRefusal("launcher_group_alive")
    except Exception as error:
        record.update(verdict="REFUSED", cause_codes=[str(error) if isinstance(error, q.HarvestRefusal)
                      else "archive_authentication_or_evaluator_fault"], cause_classes=["tooling"])
    record.update(end_state=record["verdict"] == "FAIL", s2_eligible=False,
                  next_step="lead_adjudication_qualification_failure" if record["verdict"] == "FAIL" else
                            "r3_identical_byte_reharvest" if record["verdict"] == "REFUSED" else "lead_ratification")
    return q.publish(destination, record)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--replay-source", type=Path, action="append", default=[])
    parser.add_argument("--battery-evidence", type=Path, required=True)
    parser.add_argument("--battery-evidence-sha256", required=True)
    parser.add_argument("--previous-harvest", type=Path)
    args = parser.parse_args(argv)
    try:
        record = harvest(args)
    except Exception:
        q.preflight_refusal(SCHEMA, Path("/tmp/dd5-fold"))
        return 3
    q.public_print(record)
    return 0 if record["verdict"] in {"PASS", "NULL"} else 3 if record["verdict"] == "REFUSED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
