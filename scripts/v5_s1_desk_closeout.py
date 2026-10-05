#!/usr/bin/env python3
"""Lead-run s1 preservation after STOP and the quiet window, before any later arm.

Never called by the night chain. This copies bytes and observes continued OFF;
it neither emits launch completion nor advances a ledger pin.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise import arm_readiness as readiness, network_time_off, t0_rehearsal as t0
from joulewise import v5_qualification as q
from scripts import produce_t0_rehearsal_bundle as producer
from scripts import write_v5_qualification_plan as writer

DESK_STAGES = ("claim_backup", "bound_backup", "close_out", "restore")
RUNSHEET = "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"


def backup_sources(sources, destination, script, *, runner=subprocess.run):
    """Reuse backup_runs.sh's rsync implementation, then independently hash both trees."""
    destination = writer.safe_path(destination, exists=False)
    sources = {role: writer.safe_path(source) for role, source in sources.items()}
    if any(destination == source or destination in source.parents or source in destination.parents
           for source in sources.values()):
        raise ValueError("backup destination overlaps a source")
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError("backup destination already exists")
    destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    copies = {}
    for role, source in sources.items():
        source = writer.safe_path(source)
        before = producer.tree_files(source)
        if not before:
            raise ValueError("backup source is empty")
        target = destination / role
        result = runner(["/bin/bash", str(script), str(source), str(target)],
                        stdin=subprocess.DEVNULL, capture_output=True, check=False)
        if result.returncode != 0:
            raise ValueError("backup command failed")
        copied = target / "runs"
        if producer.tree_files(copied) != before or producer.tree_files(source) != before:
            raise ValueError("backup digest mismatch or source changed")
        copies[role] = {"source": str(source), "destination": str(copied), "files": before}
    return copies


def phase_g(plan, record):
    """Observe the runsheet G1 assertion and preserve its tree/custody/status census."""
    roots = record["desk_sources"]
    claim = Path(roots["claim_runs"])
    log = claim / "campaign_log.jsonl"
    rows = [readiness.parse_json_bytes(line) for line in producer.regular(log).splitlines() if line.strip()]
    if sum(row.get("record_type") == "idle_admission_whole_window_verdict" for row in rows) != 1:
        raise ValueError("Phase G requires exactly one whole-window verdict")
    pack = Path(plan.pack_night["pack_root"])
    # Authenticate the frozen configs, and resolve only the dispatched stages.
    science, _, _, _ = writer.pack_roster(pack, "s1")
    tree, _ = readiness._plan_tree(pack)
    stages = writer.dispatched_stages(pack, tree["stage_graph"], science[0]["stage_id"])
    expected = {"claim_runs": {r["run_id"] for r in science}, "bound_runs": set()}
    from scripts.run_campaign import discover_configs
    for stage in stages:
        if stage["stage_id"] == science[0]["stage_id"] or stage["kind"] != "campaign_collection":
            continue
        commands = stage["launch"]["commands"]
        paths = [arg["value"] for command in commands for arg in command["argv_template"]["arguments"]
                 if arg["kind"] == "repo_path" and arg["value"].startswith("configs/campaigns/")]
        if len(paths) != 1:
            raise ValueError("Phase G collection path is ambiguous")
        role = "bound_runs" if stage.get("input_ref", {}).get("input_id") == "neg8_bound_corpus" else "claim_runs"
        for config in discover_configs(Path(plan.measurement_root) / paths[0]):
            expected[role].add(readiness.parse_json_bytes(config.read_bytes())["run_id"])
    for role in ("claim_runs", "bound_runs"):
        root = Path(roots[role])
        bundles = {p.name for p in root.iterdir() if p.is_dir()
                   and p.name not in {"instrument_validation", "campaign_manifests"}}
        if bundles != expected[role]:
            raise ValueError("Phase G extra or missing bundle")
    plan_custody = Path(getattr(plan, "custody_root", roots["custody"]))
    custody_roots = {Path(roots["custody"]), plan_custody}
    # Scratch has no place in retained custody. The measurement checkout copy
    # is separately pinned by git status and is not a lifecycle scratch root.
    for custody in custody_roots:
        for path in custody.rglob("*"):
            if "results-clone" in path.relative_to(custody).parts:
                continue
            if path.name in {"scratch", "tmp", "__pycache__"} or path.name.endswith((".tmp", ".pyc")):
                raise ValueError("Phase G scratch residue")
    head = subprocess.check_output(["git", "-C", plan.measurement_root, "rev-parse", "HEAD"], text=True).strip()
    status = subprocess.check_output(["git", "-C", plan.measurement_root, "status", "--short", "--branch"], text=True)
    if any(line and not line.startswith("##") for line in status.splitlines()):
        raise ValueError("Phase G modified measurement checkout")
    extension = q.pin_only_head_extension(plan.measurement_root, record["head"], head)
    if readiness.committed_pack_tree_sha256(pack) != plan.pack_night["pack_sha256"]:
        raise ValueError("Phase G modified pack byte")
    assertions = {"whole_window_verdict_count": 1, "campaign_log": producer.reference(log),
            "expected_bundles": {role: sorted(ids) for role, ids in expected.items()},
            "runs_tree": {role: sorted(str(p.relative_to(Path(roots[role])))
                for p in Path(roots[role]).rglob("*")) for role in ("claim_runs", "bound_runs")},
            "custody_files": producer.tree_files(Path(roots["custody"])),
            "night_custody_files": producer.tree_files(plan_custody),
            "git_status": status, "head": head, "pack_sha256": plan.pack_night["pack_sha256"],
            "no_extra_bundles": True, "no_scratch_residue": True, "pack_unchanged": True}
    if extension is not None:
        assertions["head_extension"] = extension
    return assertions


def closeout(plan_path, *, now=time.time, clear=q.group_clear):
    if os.environ.get("V5_QUALIFICATION_OCCURRENCE"):
        raise ValueError("desk closeout cannot run inside the night chain")
    plan = q.load_plan(plan_path, "G2B_SHAKEDOWN", now=now, clear=clear)
    custody = Path(plan.custody_root)
    night = custody / "night"
    stage_dir = night / "rehearsal-lifecycle"
    if any((stage_dir / (name + ".json")).exists() for name in DESK_STAGES):
        raise ValueError("desk lifecycle is create-once")
    record_path = custody / "qualification-plan-record.json"
    record = producer.read(record_path)
    if (record.get("occurrence") != "s1" or record["plan"] != producer.reference(plan_path)
            or record["head"] != plan.measurement_head):
        raise ValueError("desk plan binding mismatch")
    go = readiness.validate_pack_night_go_receipt(producer.read(night / "go_receipt.json"))
    if go["purpose"] != "G2B_SHAKEDOWN" or go["plan_sha256"] != record["plan"]["sha256"]:
        raise ValueError("desk GO binding mismatch")
    arm = custody / go["pack_id"] / "arm_readiness.receipts" / (go["arm_receipt"]["receipt_id"] + ".json")
    if producer.reference(arm)["sha256"] != go["arm_receipt"]["sha256"]:
        raise ValueError("desk ARM digest mismatch")
    context = producer.read(arm)["arm_context"]
    destinations = writer.backup_destinations(context)
    sources = {name: context[key] for name, key in (("custody", "custody_root"),
        ("claim_runs", "claim_runs_root"), ("bound_runs", "bound_runs_root"))}
    if record["backup_destinations"] != destinations or record["desk_sources"] != sources:
        raise ValueError("desk sources/destinations differ from s1 plan")
    stops = list(custody.rglob("post-bracket-terminal-boundary.json"))
    if len(stops) != 1:
        raise ValueError("desk requires one retained STOP boundary")
    q.require_terminal_boundary(plan, stops[0])
    arm_root = writer.safe_path(context["custody_root"])
    if arm_root == custody or arm_root in custody.parents or custody in arm_root.parents:
        raise ValueError("desk requires separate plan and ARM custody roots")
    # The writer pins the original three desk sources. Add the authenticated
    # plan root to both backups without changing that registered source map.
    sources["night_custody"] = str(custody)
    stop = producer.read(stops[0])
    if (stop.get("session_state") != "finalized" or stop.get("pin_relation") != "physical_ahead"
            or stop.get("refusal_code") != "calibration_ledger_head_mismatch"
            or stop.get("terminal_head_pin_candidate") is None):
        raise ValueError("desk requires physical_ahead STOP")
    for name in ("launch", "capability_consumption", "capture"):
        observed = producer.read(stage_dir / (name + ".json"))
        if observed.get("schema_version") != t0.QUALIFICATION_STAGE_SCHEMA or observed.get("stage_id") != name:
            raise ValueError("night lifecycle stage absent")
    assertions = phase_g(plan, record)
    if (assertions.get("head_extension") is not None
            and assertions["head_extension"]["terminal_head_pin"] != stop["terminal_head_pin_candidate"]):
        raise ValueError("Phase G H_pin differs from the STOP terminal candidate")
    assertions["campaign_log"] = producer.reference(producer.copy_record(
        assertions["campaign_log"]["path"], stage_dir / "phase-g-campaign-log.jsonl"))
    runsheet = producer.copy_record(Path(plan.measurement_root) / RUNSHEET, stage_dir / "runsheet.md")
    off_path = q.off_receipt_path(plan)
    off = network_time_off.read_receipt(off_path, plan_id=plan.plan_id, window_id=record["window_id"])
    if off["boot_id"].lower() != go["boot_session_id"].lower():
        raise ValueError("OFF receipt boot mismatch")
    standdown_path = night / "standdown-observed.json"
    standdown = producer.read(standdown_path)
    if (standdown.get("schema_version") != producer.STANDDOWN_SCHEMA
            or standdown.get("boot_session_id") != go["boot_session_id"] or not standdown.get("exits")
            or standdown.get("after", {}).get("processes") != []):
        raise ValueError("stand-down observation absent")
    # Check before any create-once backup/stage writes, so an unavailable
    # witness can be repaired without consuming the backup destinations.
    observation = producer.observe_network_time_off()
    def stage(name, **facts):
        return producer.write(stage_dir / (name + ".json"), {
            "schema_version": t0.QUALIFICATION_STAGE_SCHEMA, "stage_id": name,
            "monotonic_ns": time.monotonic_ns(), "plan_record": producer.reference(record_path), **facts})
    for name, role in (("claim_backup", "claim"), ("bound_backup", "bound")):
        copies = backup_sources(sources, destinations[role], Path(plan.measurement_root) / "scripts/backup_runs.sh")
        stage(name, destination=destinations[role], copies=copies)
    stage("close_out", phase_g=assertions, stop=producer.reference(stops[0]),
          runsheet=producer.reference(runsheet),
          off_receipt=producer.reference(off_path),
          off_identity={key: off[key] for key in ("plan_id", "window_id", "boot_id")})
    stage("restore", network_time="OFF", stand_down=True, observation=observation,
          off_receipt=producer.reference(off_path), standdown=producer.reference(standdown_path))
    return {"status": "COMPLETE", "plan": producer.reference(plan_path),
            "stages": {name: producer.reference(stage_dir / (name + ".json")) for name in DESK_STAGES}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = closeout(args.plan)
    except Exception:
        result, code = {"status": "REFUSED", "reason_code": "s1_desk_closeout_invalid"}, 2
    else:
        code = 0
    sys.stdout.buffer.write(readiness.render_json(result))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
