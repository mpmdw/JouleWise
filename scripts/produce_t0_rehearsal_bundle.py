#!/usr/bin/env python3
"""Observe the non-inference rehearsal lifecycle and assemble retained evidence.

This does not author ARM, mint GO, consume capabilities, or invent G7/G10.
Those are inputs from the canonical producers. Fixture mapping is explicit.
"""
from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import arm_readiness as readiness, network_time_off, t0_rehearsal as t0
from joulewise import night_gate, calibration_ledger
from joulewise.measurement_liveness import observe_identity
from scripts import rehearse_t0_unattended as reader

STAGE_SCHEMA = "joulewise.t0_rehearsal_lifecycle_stage.v1"
PROVENANCE_SCHEMA = "joulewise.t0_rehearsal_producer_provenance.v1"
STANDDOWN_SCHEMA = "joulewise.t0_rehearsal_standdown_observation.v1"
OBSERVED = "OBSERVED_REHEARSAL"
FIXTURE = "DESK_FIXTURE_MAPPING_ONLY"
HID_SCHEMA = "joulewise.t0_rehearsal_hid_observation.v1"
HID_ARGV = ("/usr/sbin/ioreg", "-r", "-c", "IOHIDSystem")
HID_TIMEOUT_S = 10


def regular(path):
    path = Path(path)
    if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError("input must be an absolute regular non-symlink file")
    return path.read_bytes()


def read(path):
    return readiness.parse_json_bytes(regular(path), require_canonical=True)


def write(path, value):
    path = Path(path)
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("output custody contains symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = readiness.render_json(value)
    if path.exists():
        if regular(path) != raw:
            raise ValueError("immutable derivation already exists with different bytes")
        return path
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        raise  # Preserve partial bytes as a failed attempt.
    return path


def reference(path):
    return {"path": str(Path(path)), "sha256": readiness.sha256_bytes(regular(path))}


def plan_at(path):
    plan = night_gate.NightPlan.from_mapping(read(path))
    if plan.receipt_class != "TRANSACTION_PACK" or not plan.plan_id.startswith(t0.REHEARSAL_WINDOW_PREFIX):
        raise ValueError("requires prefixed TRANSACTION_PACK rehearsal plan")
    auth = read(plan.pack_night["authorization_record"]["path"])
    if reference(plan.pack_night["authorization_record"]["path"])["sha256"] != plan.pack_night["authorization_record"]["sha256"]:
        raise ValueError("authorization digest mismatch")
    if auth["purpose"] != "T0_REHEARSAL" or auth["claim_eligible"] is not False:
        raise ValueError("requires non-claim T0_REHEARSAL authorization")
    return plan


def processes(stdout):
    result = []
    for line in stdout.splitlines():
        pid, argv = line.strip().split(maxsplit=1)
        result.append({"pid": int(pid), "argv": [argv]})
    return result


def census():
    result = t0.observed_run(night_gate.AGENT_CENSUS_ARGV, capture_output=True,
                             text=True, stdin=-3, timeout=10)
    if result.returncode not in (0, 1) or (result.returncode == 1 and result.stdout):
        raise ValueError("agent census observation failed")
    return {"argv": list(night_gate.AGENT_CENSUS_ARGV), "exit_code": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr,
            "monotonic_ns": time.monotonic_ns(), "processes": processes(result.stdout)}


def observe_standdown(plan_path, timeout_s):
    """A foreground observer starts BEFORE agents exit and observes their death.

    It neither kills agents nor asserts its own future exit. PID reuse is
    treated as the end of the original observed identity, not the new process.
    """
    bounded_timeout(timeout_s)
    plan = plan_at(plan_path)
    night = Path(plan.custody_root) / "night"
    night.mkdir(parents=True, exist_ok=True)
    before = census()
    agents = [p for p in before["processes"] if t0._process_is_agent(p)]
    if not agents:
        raise ValueError("pre-stand-down census contains no observed agent")
    identities = {p["pid"]: observe_identity(p["pid"]) for p in agents}
    if any(i.state != "LIVE" for i in identities.values()):
        raise ValueError("agent identity unavailable at pre-stand-down census")
    write(night / "pre-standdown.json", {"schema_version": STANDDOWN_SCHEMA,
          "plan_sha256": reference(plan_path)["sha256"],
          "boot_session_id": readiness._current_boot_session_id(), "census": before,
          "identities": [{"pid": pid, "start_time": i.start_time} for pid, i in identities.items()]})
    remaining = dict(identities)
    exits = []
    deadline = time.monotonic() + timeout_s
    while remaining:
        if time.monotonic() >= deadline:
            raise ValueError("stand-down exit observation timed out")
        for pid, initial in list(remaining.items()):
            now = observe_identity(pid)
            if now.state == "UNKNOWN":
                raise ValueError("agent exit cannot be observed")
            if now.state == "DEAD" or now.start_time != initial.start_time:
                exits.append({"pid": pid, "start_time": initial.start_time,
                              "observed_exit_monotonic_ns": time.monotonic_ns()})
                del remaining[pid]
        if remaining:
            time.sleep(min(1, max(0, deadline - time.monotonic())))
    after = census()
    if after["processes"]:
        raise ValueError("new agent present after stand-down")
    return write(night / "standdown-observed.json", {"schema_version": STANDDOWN_SCHEMA,
                 "boot_session_id": readiness._current_boot_session_id(),
                 "before": reference(night / "pre-standdown.json"), "exits": exits, "after": after})


def run_driver(plan_path, timeout_s):
    """Foreground supervisor records the real driver's eventual exit."""
    bounded_timeout(timeout_s)
    plan = plan_at(plan_path)
    night = Path(plan.custody_root) / "night"
    night.mkdir(parents=True, exist_ok=True)
    journal = night / "process-observations.jsonl"
    if journal.exists():
        raise ValueError("process observation journal already exists")
    standdown_path = night / "standdown-observed.json"
    standdown = read(standdown_path)
    before = read(standdown["before"]["path"])
    boot = readiness._current_boot_session_id()
    if (standdown.get("schema_version") != STANDDOWN_SCHEMA
            or reference(standdown["before"]["path"]) != standdown["before"]
            or standdown.get("boot_session_id") != boot
            or before.get("boot_session_id") != boot
            or before.get("plan_sha256") != reference(plan_path)["sha256"]):
        raise ValueError("observed stand-down producer record missing")
    write(night / "observation-origin.json", {
        "schema_version": "joulewise.t0_rehearsal_observation_origin.v1",
        "proof_scope": OBSERVED, "plan": reference(plan_path),
        "standdown": reference(standdown_path),
        "producer": reference(Path(__file__).resolve()),
        "boot_session_id": boot})
    environment = os.environ.copy()
    environment["JOULEWISE_REHEARSAL_PROCESS_JOURNAL"] = str(journal)
    command = [str(Path(plan.measurement_root) / ".venv/bin/python"), "-B",
               str(Path(plan.measurement_root) / "scripts/run_night.py"), "run", "--plan", str(plan_path)]
    with t0.process_journal(journal):
        result = t0.observed_run(command, stdin=-3, env=environment, timeout=timeout_s)
    return result.returncode


def bounded_timeout(value):
    if not math.isfinite(value) or value <= 0:
        raise ValueError("timeout must be finite and positive")
    return value


def tree_files(root):
    root = Path(root)
    if any(p.is_symlink() for p in (root, *root.parents)) or not root.is_dir():
        raise ValueError("tree root is not a regular directory")
    result = {}
    for p in sorted(root.rglob("*")):
        if p.is_symlink():
            raise ValueError("tree contains a symlink")
        if p.is_file():
            result[p.relative_to(root).as_posix()] = readiness.sha256_bytes(regular(p))
    return result


def verified_backup(source, destination):
    before = tree_files(source)
    if not before:
        raise ValueError("backup source contains no lifecycle activity")
    if destination.exists():
        raise ValueError("backup destination already exists")
    shutil.copytree(source, destination)
    if tree_files(destination) != before or tree_files(source) != before:
        raise ValueError("backup verification mismatch or source changed")
    return {"source": str(source), "destination": str(destination), "files": before}


def lifecycle(plan_path):
    """Perform actual file activity, two verified copies, close-out and OFF check."""
    plan = plan_at(plan_path)
    custody = Path(plan.custody_root)
    night = custody / "night"
    go = readiness.validate_pack_night_go_receipt(read(night / "go_receipt.json"))
    if go["purpose"] != "T0_REHEARSAL" or go["authorization"]["claim_eligible"] is not False:
        raise ValueError("GO is not non-claim rehearsal authority")
    consumed_paths = list((custody / go["pack_id"]).glob("arm_readiness.consumptions/*.consumed.json"))
    if len(consumed_paths) != 1:
        raise ValueError("requires exactly one consumption")
    consumed = read(consumed_paths[0])
    readiness.verify_consumed_launch(plan.pack_night["pack_root"], consumed_paths[0], require_current_boot=True)
    arm_path = custody / go["pack_id"] / "arm_readiness.receipts" / (go["arm_receipt"]["receipt_id"] + ".json")
    arm = read(arm_path)
    night_gate._pack_rehearsal_roots(plan, arm, go["purpose"])
    context = arm["arm_context"]
    claims, bounds = (Path(context[k]) for k in ("claim_runs_root", "bound_runs_root"))
    destinations = [Path(context[k]) for k in ("claim_backup_destination", "bound_backup_destination")]
    all_roots = [claims, bounds, *destinations]
    if any(t0._contains(a.resolve(), b.resolve()) or t0._contains(b.resolve(), a.resolve())
           for i, a in enumerate(all_roots) for b in all_roots[i+1:]):
        raise ValueError("lifecycle runs/backup roots overlap")
    started = read(night / "chain.started")
    stage_dir = night / "rehearsal-lifecycle"
    def stage(name, **facts):
        return write(stage_dir / (name + ".json"), {"schema_version": STAGE_SCHEMA,
                     "stage_id": name, "monotonic_ns": time.monotonic_ns(), **facts})
    stage("launch", source=reference(night / "chain.started"))
    stage("capability_consumption", source=reference(consumed_paths[0]))
    activity = {"schema_version": "joulewise.t0_rehearsal_activity.v1", "window_id": plan.plan_id,
                "claim_eligible": False, "pid": os.getpid(), "monotonic_ns": time.monotonic_ns(),
                "chain_start": started, "consumption": reference(consumed_paths[0])}
    claim_activity = write(claims / "non-inference-activity.json", activity)
    bound_activity = write(bounds / "non-inference-activity.json", activity)
    retained_activity = [copy_record(source, stage_dir / name) for source, name in
                         ((claim_activity, "claim-activity.json"), (bound_activity, "bound-activity.json"))]
    hid_started = time.monotonic_ns()
    hid_result = t0.observed_run(HID_ARGV, stdin=-3, capture_output=True, text=True, timeout=HID_TIMEOUT_S)
    hid_finished = time.monotonic_ns()
    if hid_result.returncode != 0:
        raise ValueError("HID raw observation failed")
    t0.parse_hid_idle_time(hid_result.stdout)
    write(night / "hid-idle-observation.json", {"schema_version": HID_SCHEMA, "argv": list(HID_ARGV),
        "exit_code": hid_result.returncode, "stdout": hid_result.stdout, "stderr": hid_result.stderr,
        "started_monotonic_ns": hid_started, "finished_monotonic_ns": hid_finished})
    stage("capture", artifacts=[reference(path) for path in retained_activity])
    for name, source, parent in zip(("claim_backup", "bound_backup"), (claims, bounds), destinations):
        stage(name, **verified_backup(source, parent / plan.plan_id))
    # The T-0 bracket reservation is real even though no slot is captured.
    # Close its unused slots through the canonical abort, preserving custody.
    pack_root = Path(plan.pack_night["pack_root"])
    tree, _ = readiness._plan_tree(pack_root)
    frozen_plan, _, _, _ = readiness.resolve_frozen_plan(pack_root, tree)
    closed = calibration_ledger.abort_calibration_session(
        Path(plan.measurement_root) / "runs/calibration_observation_ledger.jsonl",
        Path(plan.measurement_root) / "configs/calibration/calibration_ledger_head.json",
        session_id=context["bracket_session_id"], reason="T0_REHEARSAL non-inference close-out",
        plan_path=frozen_plan, repo_root=Path(plan.measurement_root),
        custody_budget_s=float(os.environ.get("CUSTODY_BUDGET_S", "120")))
    if closed["status"] != "aborted" or closed["terminal_result"] != "session_aborted":
        raise ValueError("unused rehearsal bracket session did not close")
    close_record = write(stage_dir / "ledger-close-out.json", dict(closed))
    stage("close_out", ledger_close_out=reference(close_record),
          sources=[reference(path) for path in retained_activity],
          backup_records=[reference(stage_dir / (name + ".json")) for name in ("claim_backup", "bound_backup")])
    # This step only queries time. It has no ON command and no clock setter.
    query = ["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-getusingnetworktime"]
    result = t0.observed_run(query, stdin=-3, capture_output=True, text=True, timeout=30)
    if result.returncode != 0 or result.stdout.strip() != "Network Time: Off":
        raise ValueError("restore requires observed network time OFF")
    off_path = custody / go["pack_id"] / "arm_readiness.t0.inputs" / network_time_off.RECEIPT_BASENAME
    off = network_time_off.read_receipt(off_path, plan_id=plan.plan_id, window_id=plan.plan_id)
    network_time_off.seconds_since_receipt(off, {**network_time_off._clock(), "boot_id": network_time_off.boot_id()})
    stage("restore", network_time="OFF", stand_down=True, off_receipt=reference(off_path),
          observation={"argv": query, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    return stage_dir


def copy_record(source, target):
    if any(p.is_symlink() for p in (target, *target.parents)):
        raise ValueError("output custody contains symlink")
    raw = regular(source)
    if target.exists():
        if regular(target) != raw:
            raise ValueError("immutable record already exists with different bytes")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(raw)
    return target


def assemble(custody, *, positive_control, positive_sha256, positive_artifacts,
             g7_locator=None, initial=False, fixture_mapping=False, home=None, inventory=None):
    custody = Path(custody)
    if not custody.is_absolute() or any(p.is_symlink() for p in (custody, *custody.parents)):
        raise ValueError("custody root must be absolute and non-symlink")
    custody = custody.resolve(strict=True)
    night, records = custody / "night", custody / "records"
    go_path = night / "go_receipt.json"
    go = readiness.validate_pack_night_go_receipt(read(go_path))
    if go["purpose"] != "T0_REHEARSAL" or go["authorization"]["claim_eligible"] is not False or not custody.name.startswith(t0.REHEARSAL_WINDOW_PREFIX):
        raise ValueError("requires a completed non-claim pack rehearsal")
    if not initial and g7_locator is None:
        raise ValueError("final assembly requires authenticated G7 locator")
    origin_path = night / "observation-origin.json"
    if not fixture_mapping:
        origin = read(origin_path)
        if (origin.get("schema_version") != "joulewise.t0_rehearsal_observation_origin.v1"
                or origin.get("proof_scope") != OBSERVED
                or origin.get("boot_session_id") != go["boot_session_id"]
                or origin["plan"]["sha256"] != go["plan_sha256"]):
            raise ValueError("fixture or unobserved producer inputs cannot be assembled as real")
        for locator in (origin["plan"], origin["standdown"], origin["producer"]):
            if reference(locator["path"]) != locator:
                raise ValueError("observation origin source digest mismatch")
    if reference(positive_control)["sha256"] != positive_sha256:
        raise ValueError("positive control digest mismatch")
    positive = read(positive_control)
    if positive.get("schema_version") != t0.POSITIVE_CONTROL_SCHEMA:
        raise ValueError("positive control schema mismatch")
    if not positive_artifacts:
        raise ValueError("G10 physical control raw supporting artifacts required")
    support = []
    for i, path in enumerate(positive_artifacts):
        target = copy_record(path, records / "positive-control-support" / f"{i:04d}-{Path(path).name}")
        support.append(reference(target))
    positive_path = copy_record(positive_control, records / "positive-control.json")
    # Derive execution from matched spawn/wait events, including negative exits.
    events = [readiness.parse_json_bytes(line) for line in regular(night / "process-observations.jsonl").splitlines()]
    seals = [e for e in events if e.get("event") == "seal"]
    observations = [e for e in events if e.get("event") != "seal"]
    journal_ids = {e.get("journal_id") for e in observations}
    if (len({e.get("journal_id") for e in seals}) != len(seals)
            or not journal_ids.issubset({e.get("journal_id") for e in seals})
            or any(e.get("record_count") != sum(o.get("journal_id") == e.get("journal_id") for o in observations) for e in seals)):
        raise ValueError("process observation missing spawn or observed exit/seal")
    spawns, exits = {}, {}
    for event in observations:
        if event.get("schema_version") != t0.PROCESS_EVENT_SCHEMA:
            raise ValueError("process observation schema mismatch")
        key = (event["pid"], event["spawned_monotonic_ns"])
        target = spawns if event["event"] == "spawn" else exits if event["event"] == "exit" else None
        if target is None or key in target:
            raise ValueError("duplicate or unknown process observation")
        target[key] = event
    if not spawns or spawns.keys() != exits.keys():
        raise ValueError("process observation missing spawn or observed exit")
    processes_record = []
    for i, (key, spawn) in enumerate(sorted(spawns.items(), key=lambda x: x[0][1])):
        exit_event = exits[key]
        if any(exit_event[field] != spawn[field] for field in ("pid", "argv", "stdin_fd0_target", "spawned_monotonic_ns")) or exit_event["monotonic_ns"] < spawn["monotonic_ns"]:
            raise ValueError("process observation was swapped")
        processes_record.append({"role": "top_level" if i == 0 else "governed_subprocess",
            "pid": spawn["pid"], "argv": spawn["argv"], "stdin_fd0_target": spawn["stdin_fd0_target"],
            "state": "EXITED", "exit_code": exit_event["exit_code"],
            # Missing dialogue observations stay unknown. Exit success and
            # DEVNULL alone cannot prove the absence of a surviving prompt.
            "prompt_count": exit_event.get("prompt_count"),
            "eof_refusal": exit_event.get("eof_refusal"),
            "timed_out": exit_event.get("timed_out")})
    execution = write(records / "execution.json", {"schema_version": t0.EXECUTION_SCHEMA,
          "sequence_completed": all(p["exit_code"] == 0 for p in processes_record), "processes": processes_record})
    namespace = custody / go["pack_id"]
    # Observe HID during the non-inference lifecycle, after all T-0 author
    # work. Do not add a probe to the frozen eleven-site post-R1 census.
    hid_observation = read(night / "hid-idle-observation.json")
    if (hid_observation.get("schema_version") != HID_SCHEMA or hid_observation.get("argv") != list(HID_ARGV)
            or hid_observation.get("exit_code") != 0):
        raise ValueError("HID raw witness missing or ambiguous")
    hid = records / "hid-idle.txt"
    hid.parent.mkdir(parents=True, exist_ok=True)
    hid_raw = hid_observation["stdout"].encode()
    t0.parse_hid_idle_time(hid_observation["stdout"])
    if hid.exists():
        if regular(hid) != hid_raw:
            raise ValueError("immutable HID witness changed")
    else:
        with hid.open("xb") as stream:
            stream.write(hid_raw)
    receipt = write(records / "rehearsal-receipt.json", {"schema_version": t0.REHEARSAL_RECEIPT_SCHEMA,
        "receipt_class": t0.REHEARSAL_RECEIPT_CLASS, "claim_eligible": False,
        "window_id": custody.name, "custody_root": str(custody), "acceptance_target": "T0-UNATTENDED-01"})
    standdown = read(night / "standdown-observed.json")
    pre = read(Path(standdown["before"]["path"]))
    if reference(Path(standdown["before"]["path"])) != standdown["before"]:
        raise ValueError("pre-stand-down census digest mismatch")
    if not fixture_mapping and (standdown.get("schema_version") != STANDDOWN_SCHEMA
            or standdown.get("boot_session_id") != go["boot_session_id"]
            or pre.get("boot_session_id") != go["boot_session_id"]
            or pre.get("plan_sha256") != go["plan_sha256"]):
        raise ValueError("stand-down observation is stale or bound to another plan")
    started, ended = read(night / "chain.started"), read(night / "chain.exited")
    if not (started["monotonic_ns"] <= hid_observation["started_monotonic_ns"]
            <= hid_observation["finished_monotonic_ns"] <= ended["monotonic_ns"]):
        raise ValueError("HID raw witness was not observed during the lifecycle")
    censuses = [readiness.parse_json_bytes(line) for line in regular(night / "censuses.jsonl").splitlines()]
    capture_censuses = []
    for c in censuses:
        if started["monotonic_ns"] <= c["monotonic_ns"] <= ended["monotonic_ns"]:
            if c["argv"] != list(night_gate.AGENT_CENSUS_ARGV) or c["exit_code"] not in (0, 1):
                raise ValueError("capture agent census observation failed")
            capture_censuses.append({"processes": processes(c["stdout"])})
    last = max(standdown["exits"], key=lambda e: e["observed_exit_monotonic_ns"])
    lineage = write(records / "process-lineage.json", {"schema_version": t0.PROCESS_LINEAGE_SCHEMA,
        "agent_pid": last["pid"], "agent_exit_monotonic_ns": last["observed_exit_monotonic_ns"],
        "capture_started_monotonic_ns": started["monotonic_ns"], "capture_finished_monotonic_ns": ended["monotonic_ns"],
        "pre_launch_census": {"processes": pre["census"]["processes"]}, "capture_censuses": capture_censuses})
    stages = []
    for stage_id in t0._LIFECYCLE_STAGES:
        path = night / "rehearsal-lifecycle" / (stage_id + ".json")
        stage = read(path)
        if stage.get("schema_version") != STAGE_SCHEMA or stage.get("stage_id") != stage_id:
            raise ValueError("lifecycle evidence was missing or swapped")
        if stage_id == "restore" and (stage.get("network_time") != "OFF" or stage.get("stand_down") is not True):
            raise ValueError("restore-ON is forbidden")
        stages.append({"stage_id": stage_id, "status": "COMPLETE", "evidence": reference(path)})
    lifecycle_record = write(records / "lifecycle.json", {"schema_version": t0.LIFECYCLE_SCHEMA,
        "stages": stages, "operator_actions_at_t0": 0, "human_interventions": []})
    # Software controls are the existing real author/arm boundary replays.
    clock_source = read(namespace / "arm_readiness.t0.sources/clock-correct-and-prior-state.json")
    clock = clock_source["facts"][0]["value"]
    r0capture = read(namespace / "arm_readiness.t0.inputs/clock-reference.json")
    r0 = readiness.parse_json_bytes(r0capture["stdout"].encode("utf-8"))
    disable = read(namespace / "arm_readiness.t0.inputs/clock-disable.json")
    inputs = {"reference_server_count": clock["reference_server_count"],
        "reference_midpoint_seconds": clock["comparison_delta_seconds"], "reference_bound_seconds": clock["reference_bound_seconds"],
        "r0_anchor_realtime_ns": r0["anchor_realtime_ns"], "r0_anchor_monotonic_raw_ns": r0["anchor_monotonic_raw_ns"],
        "r0_anchor_read_skew_ns": r0["anchor_read_skew_ns"], "r0_batch_finished_monotonic_raw_ns": r0["batch_finished_monotonic_raw_ns"],
        "clock_reference_capture_finished_monotonic_ns": r0capture["finished_monotonic_ns"],
        "clock_disable_started_monotonic_ns": disable["started_monotonic_ns"], "clock_disable_finished_monotonic_ns": disable["finished_monotonic_ns"],
        "r1_batch_started_monotonic_ns": clock_source["derivation"]["r1_batch_started_monotonic_ns"],
        "r1_batch_started_monotonic_raw_ns": clock["r1_batch_started_monotonic_raw_ns"],
        "author_anchor_realtime_ns": clock["anchor_monotonic_raw_ns"] + r0["anchor_realtime_ns"] - r0["anchor_monotonic_raw_ns"],
        "author_anchor_monotonic_raw_ns": clock["anchor_monotonic_raw_ns"], "author_anchor_read_skew_ns": clock["anchor_read_skew_ns"],
        "r1_batch_finished_monotonic_ns": clock["r1_batch_finished_monotonic_ns"]}
    # The normalized anchor is used ONLY for software falsifiers. Physical
    # observations stay in the unchanged source; no synthetic physical control.
    clock_receipts = [(path, read(path)) for path in sorted((namespace / "arm_readiness.evidence").glob("*.json"))]
    clock_receipts = [(path, value) for path, value in clock_receipts if value.get("kind") == "CLOCK_ATTESTATION"]
    if len(clock_receipts) != 1:
        raise ValueError("software control clock receipt missing or ambiguous")
    clock_receipt_path, clock_receipt = clock_receipts[0]
    boundary_observations = {}
    def cases(name, runner):
        observed = []
        result = []
        for delta in (4_999_999, 5_000_001):
            outcome = runner(delta)
            observed.append({"delta_ns": delta, "status": outcome[0], "reason_code": outcome[1],
                             **({"detail": outcome[2]} if len(outcome) == 3 else {})})
            result.append({"delta_ns": delta, "expected_status": outcome[0],
                           # These shared helpers run derivations/predicates;
                           # neither owns a namespace publisher.
                           "expected_reason_code": outcome[1], "pass_namespace_published": False})
        boundary_observations[name] = observed
        return result
    falsifiers = write(records / "falsifier-controls.json", {"schema_version": t0.FALSIFIER_SCHEMA,
        "author_inputs": inputs, "author_cases": cases("author", lambda delta: t0._run_real_author_boundary(inputs, delta)),
        "arm_cases": cases("arm", lambda delta: t0._run_real_arm_boundary(clock_receipt, delta))})
    software_observations = write(night / "software-boundary-observations.json", {
        "schema_version": "joulewise.t0_rehearsal_software_boundary_observations.v1",
        "proof_scope": "SOFTWARE_BOUNDARY_REPLAY_ONLY", "clock_receipt": reference(clock_receipt_path),
        "clock_source": reference(namespace / "arm_readiness.t0.sources/clock-correct-and-prior-state.json"),
        "falsifier_controls": reference(falsifiers), "observations": boundary_observations})
    if inventory is None:
        inventory = reader._production_inventory(go)
    roots = readiness.production_custody_roots(home=Path.home() if home is None else home, inventory=inventory)
    record_paths = {name: path.relative_to(custody).as_posix() for name, path in {
        "execution": execution, "hid_idle": hid, "d149_go": go_path, "rehearsal_receipt": receipt,
        "process_lineage": lineage, "lifecycle": lifecycle_record, "falsifier_controls": falsifiers,
        "positive_control": positive_path}.items()}
    if g7_locator is not None:
        record_paths["g7_control"] = read(g7_locator)
    manifest = {"schema_version": reader.MANIFEST_SCHEMA, "t0_namespace": go["pack_id"],
                "records": record_paths, "production_roots": [{"role": r.role, "path": str(r.path)} for r in roots]}
    write(custody / "rehearsal-provenance.json", {"schema_version": PROVENANCE_SCHEMA,
          "proof_scope": FIXTURE if fixture_mapping else OBSERVED, "source_records":
          [reference(night / "process-observations.jsonl"), reference(night / "standdown-observed.json"),
           reference(night / "hid-idle-observation.json"), reference(software_observations),
           *([] if fixture_mapping else [reference(origin_path)]), *support]})
    name = "t0-rehearsal-initial.json" if initial else reader.MANIFEST_NAME
    write(custody / name, manifest)
    write(night / ("assembly-initial.json" if initial else "assembly-final.json"), {
        "schema_version": "joulewise.t0_rehearsal_assembly.v1", "manifest": reference(custody / name),
        "records": [reference(custody / p) for key, p in record_paths.items() if key != "g7_control"],
        "g7_control": record_paths.get("g7_control"),
        "proof_scope": FIXTURE if fixture_mapping else OBSERVED})
    bundle = reader.load_evidence_bundle(custody, home=home, inventory=inventory, manifest_name=name)
    verdict = t0.evaluate_rehearsal(bundle)
    verdict["proof_scope"] = FIXTURE if fixture_mapping else OBSERVED
    return verdict


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("observe-standdown", "run-driver", "lifecycle"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--plan", required=True, type=Path)
        if name != "lifecycle":
            cmd.add_argument("--timeout-s", required=True, type=float)
    cmd = sub.add_parser("assemble")
    cmd.add_argument("--custody-root", required=True, type=Path)
    cmd.add_argument("--positive-control", required=True, type=Path)
    cmd.add_argument("--positive-control-sha256", required=True)
    cmd.add_argument("--positive-control-artifact", required=True, action="append", type=Path)
    cmd.add_argument("--g7-locator", type=Path)
    cmd.add_argument("--initial", action="store_true")
    cmd.add_argument("--fixture-mapping", action="store_true", help="DESK_FIXTURE_MAPPING_ONLY; never live qualification")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "assemble":
            verdict = assemble(args.custody_root, positive_control=args.positive_control,
                positive_sha256=args.positive_control_sha256, positive_artifacts=args.positive_control_artifact,
                g7_locator=args.g7_locator, initial=args.initial, fixture_mapping=args.fixture_mapping)
            sys.stdout.buffer.write(readiness.render_json(verdict))
            return 0 if verdict["overall_verdict"] == "PASS" else 2
        if args.command == "observe-standdown":
            observe_standdown(args.plan, args.timeout_s)
        elif args.command == "run-driver":
            return run_driver(args.plan, args.timeout_s)
        else:
            plan = plan_at(args.plan)
            with t0.process_journal(Path(plan.custody_root) / "night/process-observations.jsonl"):
                lifecycle(args.plan)
        return 0
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
        sys.stdout.buffer.write(readiness.render_json({"status": "REFUSED", "reason_code": "rehearsal_producer_incomplete", "detail": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
