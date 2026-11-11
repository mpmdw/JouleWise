#!/usr/bin/env python3
"""RL-72/74/76 R1 follow-up: prepare, bounded native smoke, temperature-only desk.

Preparing does not install or arm a night. The lead supplies the ordinary
night-plan machine/custody fields using this exact sizing and chain. RL-62
and RL-73 refuse-only checks plug in at prepare_checks(), before any dwell.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import align_r1_rehearsal as r1
from scripts import align_r1_thermal_replay as replay
from joulewise.align.apple import r1_runtime as rt, v4_registration as reg
from joulewise.align.apple.thermal import Coverage

R0_FAST = {"TV0h", "TV1h", "TV0m", "TV0s", "TV1s"}  # RL-75


def prepare_checks(root, config, *, weight_digest_check=None, runtime_stack_check=None):
    """Integration sites for ops/2026-11-11-w1-armcheck, RL-62 and RL-73.

    No placeholder success: the lead wires both actual refuse-only checks
    here before a native prepare. Neither check is implemented in this lane.
    """
    if weight_digest_check is None or runtime_stack_check is None:
        raise ValueError("prepare awaits RL-62 weight_digest_check and RL-73 runtime_stack_check integration")
    return {"weights": weight_digest_check(root, config), "runtime_stack": runtime_stack_check(root, config)}


def validate_sensor_ruling(config, ruling, smoke_sha256):
    if (not ruling.get("research_lead_ruling") or ruling.get("smoke_part_b_sha256") != smoke_sha256
            or ruling.get("sensors") != config["sensors"]):
        raise ValueError("arm requires the research lead's ruling on this smoke D table and this policy")
    outcome = ruling.get("outcome")
    slow = config["sensors"]["s_slow"]
    if outcome == 1:
        if (config["sensors"]["s_fast"], slow) != ("TV0h", "Tf08"):
            raise ValueError("RL-74 outcome 1 requires R0 picks")
    elif outcome == 2:
        if slow in R0_FAST or not slow or not ruling.get("stable_with_borderline_reads"):
            raise ValueError("RL-75 narrows outcome 2; R0-fast or unstable/null slow pick needs outcome 3 ruling")
        if config.get("slow_band_floor_c") != 1.0:
            raise ValueError("new slow key starts max(1 C, 3 soak SD); Tf08 S6 receipt does not transfer")
    elif outcome == 3:
        if ruling.get("authorizes_night") is not True:
            raise ValueError("outcome 3 holds the night for the research lead")
    else:
        raise ValueError("unknown RL-74 sensor outcome")
    return ruling


def prepare(output, *, root=ROOT, config_path=None, ruling=None, smoke_table=None,
            weight_digest_check=None, runtime_stack_check=None):
    root = Path(root)
    path = Path(config_path or root / r1.DEFAULT_RUNTIME_CONFIG)
    config, _ = rt.load_config(path)
    checks = prepare_checks(root, config, weight_digest_check=weight_digest_check,
                            runtime_stack_check=runtime_stack_check)
    if ruling is None or smoke_table is None:
        raise ValueError("arm waits for smoke Part B and RL-74/75 sensor ruling")
    validate_sensor_ruling(config, ruling, hashlib.sha256(Path(smoke_table).read_bytes()).hexdigest())
    commit = r1.executed_commit(root)
    reg.verify_r1_executed_sources(root, {"executed_commit": commit})
    gate = "joulewise/align/apple/thermal_gates.py"
    expected = reg._committed_bytes(root, "82c14c9ea", [gate])[gate]
    if (root / gate).read_bytes() != expected:
        raise ValueError("W1 thermal gate bytes changed")
    bounds = r1.night_worst_case_s(["--config", str(path)])
    if bounds["window_max_s"] != 126480 or bounds["overhead_s"] != 9000:
        raise ValueError("follow-up sizing differs from RL-72 E2")
    packet = {"schema": "joulewise.align.r1_followup_prepare.v1", "status": "FOR_LEAD_ARM",
              "executed_commit": commit, "sensors": config["sensors"], "sensor_ruling": ruling,
              "prepare_checks": checks, "chain_script": "scripts/night_chains/align_r1_rehearsal.zsh",
              **bounds, "bound_files": {p: rt.sha256_file(root / p) for p in reg.R1_EXECUTED_SOURCES}}
    with Path(output).open("x") as handle:
        handle.write(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    return packet


def phase_coverage(rows, keys, phases):
    """Registered half-period cell accounting, additionally for pre-warmup idle."""
    report = {}
    for name, (start, end) in phases.items():
        per_key = {}
        for key in keys:
            counter = Coverage(start, [key], tolerance_ns=rt.NS // 2)
            selected = [r for r in rows if start - rt.NS <= r["started"]["monotonic_ns"] <= end + rt.NS]
            failures = 0
            for row in selected:
                values = row["values"]
                failures += key in values.get("errors", {}) or values.get("sensors", {}).get(key) is None
                counter.observe(row["started"]["monotonic_ns"], row["finished"]["monotonic_ns"], values)
            cell = counter.report(end)["all_keys"]
            error_fraction = failures / len(selected) if selected else 1.0
            per_key[key] = {**cell, "read_error_fraction": error_fraction,
                           "pass": (cell["sample_fraction"] is not None and cell["sample_fraction"] >= .99
                                    and error_fraction < .01 and cell["max_consecutive_empty_cells"] < 2)}
        report[name] = per_key
    return {"phases": report, "pass": all(v["pass"] for p in report.values() for v in p.values())}


def smoke_table(segment_dir):
    """Part B: classifier verbatim plus candidate/band/ref-sensitivity table."""
    segment = Path(segment_dir)
    fields = json.loads((segment / rt.RESULT_NAME).read_text())
    bundle = segment / fields["bundle"]
    journal = replay.read_journal(bundle / "outputs/align_thermal.jsonl")
    session = replay.Session(journal["rows"], journal["s_fast"], journal["s_slow"])
    anchor = replay.warmup_anchor(bundle, session)
    saved = json.loads((segment / "inventory/r1_classification.json").read_text())
    rows = [json.loads(line) for line in (segment / "inventory/inventory_journal.jsonl").read_text().splitlines() if line.strip()]
    bounds = saved["classification"]["phase_bounds_ns"]
    idle_start = anchor - 300 * rt.NS
    for line in (bundle / "events.jsonl").read_text().splitlines():
        event = json.loads(line)
        if event.get("event_type") == "stage_started" and event.get("phase") == "idle_baseline":
            idle_start = session.mono_from_epoch(event["timestamp_s"])
            break
    spans = {"pre_warmup_idle": (idle_start, anchor),
             **{name: tuple(span) for name, span in bounds.items()}}
    keys = [k["key"] for k in saved["inventory"]["keys"] if k.get("unit") == "degC"]
    coverage = phase_coverage(rows, keys, spans)
    g0 = journal["g0"][0]
    candidates = replay.candidate_replays(rows, journal["rows"], keys, journal["s_fast"], anchor,
                                          g0["start_ns"], g0["end_ns"])
    return {"schema": "joulewise.align.r1_smoke_b.v1", "classification_table": saved,
            "coverage": coverage, "candidate_replays": candidates,
            "status": "FOR_RESEARCH_LEAD_RULING" if coverage["pass"] else "COVERAGE_FAILED",
            "note": "No automatic sensor adoption. RL-74/75/76; unchanged registered classifier."}


def smoke(output, part, runtime, *, soak_reference, invoke=r1._invoke):
    """Native only when explicitly run by the lead in an agent-free session.

    B runs the same admission followed by the D step, in one member. Its
    inventory process spans idle/quiet/load/recovery. A stops after G0.
    """
    reg.verify_r1_executed_sources(ROOT, {"executed_commit": r1.executed_commit(ROOT)})
    gate = "joulewise/align/apple/thermal_gates.py"
    if (ROOT / gate).read_bytes() != reg._committed_bytes(ROOT, "82c14c9ea", [gate])[gate]:
        raise ValueError("smoke requires W1's exact thermal gate module")
    config_path = r1.runtime_config_path(runtime)
    if config_path.read_bytes() != (ROOT / r1.DEFAULT_RUNTIME_CONFIG).read_bytes():
        raise ValueError("condition 13: smoke config differs from the bound runtime config")
    config, _ = rt.load_config(config_path)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    predecessor = invoke(runtime, "capture-predecessor-30b", output / "capture_predecessor_30b",
                         soak_reference=soak_reference)
    if time.monotonic() - started >= 1800:
        raise ValueError("Part A exhausted at predecessor; partial smoke is not a pass")
    command = list(runtime) + ["--smoke-part", part, "--smoke-started", str(started)]
    fields = invoke(command, "step-d", output / rt.STEP_D_SEGMENT, soak_reference=soak_reference)
    segment = output / rt.STEP_D_SEGMENT
    receipt = json.loads((segment / "smoke_part_a.json").read_text())
    # Desk authentication through the exact W1 verifier, with the source
    # config digest from completed runtime custody. Never recapture here.
    from joulewise.align.apple.thermal_gates import load_window_reference
    source = segment / fields["bundle"]
    custody = json.loads((segment / rt.CUSTODY_NAME).read_text())
    policy = {"sensors": config["sensors"], "window_reference": {"role": "consume",
        "source_run_id": source.name,
        "source_config_sha256": custody["files"][(Path(fields["bundle"]) / "config.json").as_posix()]}}
    reference, verified = load_window_reference(policy, SimpleNamespace(
        bundle_path=source.parent / "smoke-reference-consumer", run_id="smoke-reference-consumer"))
    if part == "A" and time.monotonic() - started > 1800:
        raise ValueError("Part A exceeded 1800 s including close; partial smoke is not a pass")
    result = {"part": part, "predecessor": predecessor, "capture_and_gate": receipt, "member": fields,
              "verified_reference": reference, "reference_custody": verified}
    if part == "B":
        result["part_b"] = smoke_table(segment)
    (output / "smoke.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--sensor-ruling", type=Path, required=True)
    p.add_argument("--smoke-table", type=Path, required=True)
    p = sub.add_parser("smoke")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--part", choices=("A", "B"), required=True)
    p.add_argument("--soak-reference", type=Path, required=True)
    p.add_argument("--inputs", type=Path, default=ROOT / reg.REGISTRATION / "inputs.json")
    p = sub.add_parser("desk")
    p.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        prepare(args.output, ruling=json.loads(args.sensor_ruling.read_text()), smoke_table=args.smoke_table)
    elif args.command == "smoke":
        smoke(args.output, args.part, r1.runtime_argv_from_inputs(args.inputs), soak_reference=args.soak_reference)
    else:
        print(json.dumps(replay.night_desk(args.run_dir), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
