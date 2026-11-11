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
from scripts import align_v4_session as v4_session
from scripts import align_r1_rehearsal as r1
from scripts import align_r1_thermal_replay as replay
from joulewise.align.apple import r1_runtime as rt, v4_registration as reg
from joulewise.align.apple.thermal import Coverage, valid_value

# R1 changes run IDs; project each explicit member to the registered root,
# retaining the registration's exact digests and file maps (never re-register).
MEMBER_ROOTS = {
    "step-30b": ("model_30b", "qwen3-30b-a3b-align-pilot-v3-episodes-a-e01"),
    "high-power-aba-a1": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "high-power-aba-b": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "high-power-aba-a2": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "capture-predecessor-30b": ("model_30b", "qwen3-30b-a3b-align-pilot-v3-episodes-a-e01"),
    "step-d": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "d-planning-turn-r-plus-4c": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "d-planning-turn-r-plus-2c": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "d-planning-turn-r-plus-0c": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "d-bank-benign-s1": ("d_bank", "qwen3.8-27b-align-v4-episodes-a-e08"),
    "d-spam-benign-s1-a": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "d-spam-benign-s1-b": ("d_spam", "qwen3.8-27b-align-v4-episodes-a-e05"),
    "x-g": ("x_g", "qwen3-30b-a3b-align-v4-episodes-a-e06"),
    "neg8-reference": (None, "neg8_reference"),
}


def prepare_checks(root, config, *, weight_digest_check=None, runtime_stack_check=None,
                   identity_fn=None, runtime_runner=None, reader=None):
    """Both public armcheck APIs run before source checks or any dwell.

    reader/identity_fn/runtime_runner are synthetic-test seams. Production
    uses the real checks; this function does not launch any host setter.
    """
    root = Path(root)
    registration = root / reg.REGISTRATION
    read = reader or (lambda p: json.loads(Path(p).read_bytes()))
    inventory_path = registration / "model_artifact_inventory.json"
    mapping = {}
    try:
        inventory = read(inventory_path)
        projected = dict(inventory["artifacts"])
        members, mapping = [], {}
        for name, (template_key, registered_unit) in MEMBER_ROOTS.items():
            row = projected.get(registered_unit)
            if not isinstance(row, dict):
                raise ValueError(f"weight_digest_preflight: no_inventory_row: {registered_unit}")
            if template_key is not None:
                template_path = Path(config["templates"][template_key])
                template = read(template_path if template_path.is_absolute() else root / template_path)
                if template["model"]["source"] != row["root"]:
                    raise ValueError(f"weight_digest_preflight: no_inventory_row: {name}: template root differs")
            if template_key is None:
                member = {"model_id": "neg8", "run_id": "reference"}
            else:
                member = {"model_id": "qwen3.8-27b" if template_key in ("d_spam", "d_bank") else "qwen3-30b-a3b",
                          "run_id": template["run_id"] if name == "capture-predecessor-30b" else "align-v4-r1-" + name}
            unit = v4_session.pilot.h.align_unit_id(**member)
            projected[unit] = row
            members.append(member)
            mapping[unit] = registered_unit
        def projected_reader(path):
            return {**inventory, "artifacts": projected} if Path(path) == inventory_path else read(path)
        weights = (weight_digest_check or v4_session.weight_digest_preflight)(
            registration, members, identity_fn=identity_fn, reader=projected_reader)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        reason = str(exc)
        if not reason.startswith("weight_digest_preflight:"):
            reason = f"weight_digest_preflight: unavailable: {type(exc).__name__}: {exc}"
        weights = {"ok": False, "reasons": [reason], "roots": {}}
    stack = (runtime_stack_check or v4_session.runtime_stack_preflight)(
        config.get("measurement_python", str(root / ".venv/bin/python")), registration / "identity_pins.json",
        runner=runtime_runner, reader=read)
    checks = {"weight_digests": weights, "runtime_stack": stack, "registered_member_roots": mapping}
    return checks


def validate_sensor_ruling(config, ruling, smoke_sha256, table):
    if (not ruling.get("research_lead_ruling") or ruling.get("smoke_part_b_sha256") != smoke_sha256
            or ruling.get("sensors") != config["sensors"] or ruling.get("authorizes_night") is not True):
        raise ValueError("arm requires the research lead's ruling on this smoke D table and this policy")
    if not table.get("coverage", {}).get("pass"):
        raise ValueError("smoke Part B sampler bar failed")
    if table.get("r0_classified_keys") != config["r0_classified_keys"]:
        raise ValueError("RL-78: smoke R0 key set changed; selection is made once")
    classification = table["classification_table"]["classification"]
    selected = smoke_selection(classification, table["coverage"], config["r0_classified_keys"])
    if not selected["ok"] or any(selected[r] != config["sensors"][r]
                                 or selected[r] != table.get("selection", {}).get(r) for r in ("s_fast", "s_slow")):
        raise ValueError("RL-78: policy must use the fixed smoke Part B selection: " + "; ".join(selected["reasons"]))
    if config.get("slow_band_floor_c") != 1.0:
        raise ValueError("RL-78: default max(1 C, 3 soak idle SD); no S6 receipt transfer")
    if "Tf08" not in config["sensors"].get("record_keys", []):
        raise ValueError("RL-84: Tf08 must be journalled in every member that runs the thermal sidecar")
    return selected


def prepare(output, *, root=ROOT, config_path=None, ruling=None, smoke_table=None,
            weight_digest_check=None, runtime_stack_check=None, identity_fn=None, runtime_runner=None, reader=None):
    root = Path(root)
    path = Path(config_path or root / r1.DEFAULT_RUNTIME_CONFIG)
    config, _ = rt.load_config(path)
    checks = prepare_checks(root, config, weight_digest_check=weight_digest_check,
                            runtime_stack_check=runtime_stack_check, identity_fn=identity_fn,
                            runtime_runner=runtime_runner, reader=reader)
    failures = [reason for key in ("weight_digests", "runtime_stack") if not checks[key]["ok"]
                for reason in (checks[key]["reasons"] or [key + ": preflight refused"])]
    if failures:
        # Keep both refuse-only results reviewable even when prepare refuses.
        with Path(output).open("x") as handle:
            handle.write(json.dumps({"status": "REFUSED", **checks}, indent=2, sort_keys=True) + "\n")
        raise ValueError("; ".join(failures))
    if ruling is None or smoke_table is None:
        raise ValueError("arm waits for smoke Part B and RL-74/75 sensor ruling")
    validate_sensor_ruling(config, ruling, hashlib.sha256(Path(smoke_table).read_bytes()).hexdigest(),
                           json.loads(Path(smoke_table).read_bytes()))
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
              **checks, "chain_script": "scripts/night_chains/align_r1_rehearsal.zsh",
              **bounds, "bound_files": {p: rt.sha256_file(root / p) for p in reg.R1_EXECUTED_SOURCES}}
    with Path(output).open("x") as handle:
        handle.write(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    return packet


def phase_coverage(rows, keys, phases, *, required_keys=("Tf08",)):
    """RL-84: sweep stalls fail smoke; a key's failures reject only that key.

    Tf08 is mandatory for the disclosure. Key accounting follows rank()'s
    half-period grid, bracket validity and phase-local read-error denominator.
    A sweep is counted independently of whether any of its key reads succeed.
    """
    report, sampler = {}, {}
    for name, (start, end) in phases.items():
        selected = [r for r in rows if start <= r["started"]["monotonic_ns"] < end]
        sweeps = Coverage(start, ["sweep"], tolerance_ns=rt.NS // 2)
        for row in selected:
            a, b = row["started"]["monotonic_ns"], row["finished"]["monotonic_ns"]
            if a <= b < end and b-a <= rt.NS:
                sweeps.observe(a, b, {"sensors": {"sweep": 1}, "errors": {}})
        sweep = sweeps.report(end)["all_keys"]
        sampler[name] = {**sweep, "pass": (sweep["sample_fraction"] is not None
                         and sweep["sample_fraction"] >= .99 and sweep["max_consecutive_empty_cells"] < 2)}
        per_key = {}
        for key in keys:
            counter = Coverage(start, [key], tolerance_ns=rt.NS // 2)
            failures = 0
            for row in selected:
                values = row["values"]
                a, b = row["started"]["monotonic_ns"], row["finished"]["monotonic_ns"]
                bracket_valid = a <= b < end and b-a <= rt.NS
                failures += (not bracket_valid or key in values.get("errors", {})
                             or not valid_value(key, values.get("sensors", {}).get(key)))
                if bracket_valid:
                    counter.observe(a, b, values)
            cell = counter.report(end)["all_keys"]
            error_fraction = failures / len(selected) if selected else 1.0
            reasons = []
            if cell["sample_fraction"] is None or cell["sample_fraction"] < .99:
                reasons.append("under 99% of one-second cells")
            if error_fraction >= .01:
                reasons.append(">=1% read errors")
            if cell["max_consecutive_empty_cells"] >= 2:
                reasons.append("two consecutive empty one-second cells")
            per_key[key] = {**cell, "read_error_fraction": error_fraction,
                           "pass": not reasons, "reasons": reasons}
        report[name] = per_key
    return {"phases": report, "sampler": sampler, "required_keys": list(required_keys),
            "pass": bool(report) and all(s["pass"] for s in sampler.values()) and all(
                p.get(key, {}).get("pass", False) for p in report.values() for key in required_keys)}


def smoke_selection(classification, coverage, r0_keys):
    """Run the registered chooser on keys passing every phase, then RL-78's fallback.

    Keep the full classifier result unchanged in the table. Pre-warmup is an
    additional smoke phase; its failures also exclude a key from either role.
    R0 membership is checked after selection, and restricts fallback candidates
    only; an otherwise selected key outside R0 must be held for the lead.
    """
    from joulewise.align.apple.smc_enumeration import select_keys
    phases = coverage["phases"]
    ranking = [row for row in classification["ranking"] if phases
               and all(p.get(row["key"], {}).get("pass", False) for p in phases.values())]
    filtered = {**classification, "ranking": ranking, **select_keys(ranking),
                "heatsink_candidates": [r["key"] for r in ranking if r["class"] == "heatsink"]}
    return rt.select_smoke_sensors(filtered, r0_keys)


def class_edge_margins(classification):
    """Signed headroom, disclosure only; selection never reads this table."""
    result = []
    for row in classification["ranking"]:
        def margin(value, edge, lower=False):
            return None if value is None else value-edge if lower else edge-value
        result.append({"key": row["key"], "rise_above_3_c": margin(row.get("observed_rise"), 3., True),
            "return_time_below_300_s": margin(row.get("t_band_s"), 300.),
            "tau_below_fast_edge_s": margin(row.get("tau_s"), 60.),
            "tau_above_slow_edge_s": margin(row.get("tau_s"), 60., True),
            "noise_below_fast_c": margin(row.get("noise"), 1/3),
            "noise_below_slow_c": margin(row.get("noise"), .15)})
    return result


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
    config = json.loads((ROOT / r1.DEFAULT_RUNTIME_CONFIG).read_bytes())
    coverage = phase_coverage(rows, keys, spans)
    rejected = [{"key": key, "r0_class": config["r0_classes"].get(key, "unclassified"),
                 "phase": phase, "reason": reason}
                for phase, per_key in coverage["phases"].items() for key, cell in per_key.items()
                for reason in cell["reasons"]]
    selection = smoke_selection(saved["classification"], coverage, config["r0_classified_keys"])
    g0 = journal["g0"][0]
    candidates = replay.candidate_replays(rows, journal["rows"], keys, journal["s_fast"], anchor,
                                          g0["start_ns"], g0["end_ns"])
    return {"schema": "joulewise.align.r1_smoke_b.v1", "classification_table": saved,
            "coverage": coverage, "rejected_keys": rejected, "candidate_replays": candidates,
            "status": ("COVERAGE_FAILED" if not coverage["pass"] else
                       "FOR_RESEARCH_LEAD_RULING" if selection["ok"] else "SELECTION_FAILED"),
            "selection": selection, "r0_classified_keys": config["r0_classified_keys"],
            "class_edge_margins": class_edge_margins(saved["classification"]),
            "note": "RL-78/84: margins are disclosures; sweep/Tf08 failures fail smoke; other keys fail individually. Classifier unchanged."}


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
        (output / "smoke_part_b.json").write_text(json.dumps(result["part_b"], indent=2, sort_keys=True) + "\n")
    (output / "smoke.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if part == "B" and not result["part_b"]["coverage"]["pass"]:
        raise ValueError("smoke Part B sampler/Tf08 coverage failed; diagnostics saved in smoke_part_b.json")
    if part == "B" and not result["part_b"]["selection"]["ok"]:
        raise ValueError("smoke Part B has no admissible sensor pair; diagnostics saved in smoke_part_b.json")
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
