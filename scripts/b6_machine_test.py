#!/opt/homebrew/bin/python3.13
"""Prepare, inject and desk the non-claim block-6 machine smoke.

Prepare only renders jobs unless --install is requested. Injection runs in a
separate launchd job after the arm and owns only its own fault children.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import plistlib
import shlex
import shutil
import signal
import subprocess
import sys
import time
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.b6 import agent_pause, fingerprint, precheck, smoke
from joulewise.b6 import registration, desk_identity, plan_inputs
from joulewise.b6.desk_identity import EXPECTED, IDENTITY_SOURCE
from joulewise.b6.plan_inputs import PACK_LABELS, SEALED_DIR, REGISTRATION, SIZING, registered_thresholds
from joulewise.hazards.arm import AGENT_CENSUS_ARGV
from joulewise.hazards.base import Completed, Context

PYTHON = "/opt/homebrew/bin/python3.13"
PACK = "d117_floor_qwen3-1p7b_v5"
INJECT_LABEL = "com.joulewise.b6mt.inject"
# run_night.CENSUS_INTERVAL_S fixes the census cadence at 30 s. A 45 s
# lifetime contains a snapshot if jitter is < 15 s; hazards.arm's 10 s
# CENSUS_TIMEOUT_S is inside that slack (45 - 30 = 15 s).
AGENT_LIFETIME_S = 45


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def guard_path(path):
    """Check both the supplied spelling and symlink-resolved process argument."""
    path = Path(path).expanduser()
    resolved = path.resolve()
    if any(word in str(p).lower() for p in (path, resolved) for word in ("claude", "codex")):
        raise ValueError(f"agent-census substring in path: {path}")
    return resolved


@dataclasses.dataclass
class PrepareSeams:
    run: Callable = subprocess.run
    now: Callable = time.time
    ctx: Context | None = None
    model_files: Callable = precheck.model_files
    runtime_versions: Callable = precheck.runtime_versions
    fingerprint_collect: Callable = fingerprint.collect
    smoke_prepare: Callable = smoke.prepare


def probe_runner(run):
    """Use the same injected tool seam, forbidding optional Git checkout writes."""
    def probe(argv, timeout_s):
        argv = tuple(map(str, argv))
        try:
            value = run(argv, check=False, capture_output=True, timeout=timeout_s,
                        env={**os.environ, "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0",
                             "PYTHONDONTWRITEBYTECODE": "1"})
            return Completed(argv, value.returncode, value.stdout, value.stderr)
        except subprocess.TimeoutExpired as exc:
            return Completed(argv, None, exc.stdout or b"", exc.stderr or b"", timed_out=True)
        except OSError as exc:
            return Completed(argv, None, b"", b"", error=f"{type(exc).__name__}: {exc}")
    return probe


def installer_argv(measurement, plan_path, courier):
    # --courier-bin: the smoke's production program courier wrapper. Without it the installer
    # renders `claude` (block 5's courier, an agent session) into the night job,
    # which design 3.1 forbids for a smoke.
    return [str(Path(measurement) / "scripts/install_night_agent.sh"), "--plan", str(plan_path),
            "--python", str(Path(measurement) / ".venv/bin/python"), "--courier-bin", str(courier)]


def prepare(measurement_root, out, *, pack=PACK, lead_s=900, busy_cores=1,
            agent_s=AGENT_LIFETIME_S, busy_s=1620, install=False, seams=None):
    seams = seams or PrepareSeams()
    if os.path.lexists(Path(out).expanduser()):
        raise FileExistsError(out)
    measurement, out = guard_path(measurement_root), guard_path(out)
    if out.is_relative_to(measurement):
        raise ValueError("output must be outside the measurement checkout")
    if os.path.lexists(out):
        raise FileExistsError(out)
    if pack not in PACK_LABELS:
        raise ValueError("unknown smoke pack")
    if (not math.isfinite(lead_s) or lead_s < 0 or not math.isfinite(agent_s) or agent_s <= 0
            or not math.isfinite(busy_s) or busy_s <= 0 or type(busy_cores) is not int or busy_cores < 1):
        raise ValueError("invalid injection parameters")
    head = seams.run(["git", "-C", str(measurement), "rev-parse", "HEAD"],
                     check=True, capture_output=True, text=True, timeout=30,
                     env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}).stdout.strip()
    dirty = seams.run(["git", "-C", str(measurement), "status", "--porcelain"],
                      check=True, capture_output=True, text=True, timeout=30,
                      env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}).stdout
    when = seams.now()
    stamp = dt.datetime.fromtimestamp(when, dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    t0 = 60 * math.ceil((when + lead_s) / 60)
    plan_id = f"MT-{PACK_LABELS[pack]}-{stamp}"
    notes = []
    if dirty.strip():
        notes.append({"kind": "measurement_dirty", "status_porcelain": dirty})
    out.mkdir(parents=True, exist_ok=False)
    reg = out / "registration"
    write_json(reg / "acceptance.json", {
        "schema": registration.SCHEMA, "pack_id": pack, "registered_commit": head,
        "non_claim": True,
        "calibration": {"alignment_reference_s": "0.036462861644980",
                        "bracket_screen_s": "0.014531", "max_budgetable_drift_s": "0.015502",
                        "operative_bound_stop_s": None, "acceptance_corpus": []}})
    for name in ("identity_pins.json", "sizing_b5.json"):
        shutil.copyfile(measurement / SEALED_DIR / name, reg / name)
    identities, identity_notes = desk_identity.collect(measurement, out / "inputs", run=seams.run)
    notes.extend(identity_notes)
    inputs = plan_inputs.build(measurement, reg, pack, plan_id, identities,
                               custody_root=out / "custody", runs_parent=out / "runs-parent",
                               claim_backup=out / "backup-claim", bound_backup=out / "backup-bound", head=head)
    inputs["t0_epoch_s"] = t0
    write_json(out / "plan-inputs.json", inputs)
    pins = json.loads((reg / "identity_pins.json").read_text())
    tree = json.loads((measurement / "configs/campaigns" / pack / "plan_tree.json").read_text())
    ctx = seams.ctx or Context(run=probe_runner(seams.run), raw_dir=out / "fingerprint-raw")
    models, model_errors = seams.model_files(tree, measurement, pins)
    if model_errors:
        notes.append({"kind": "model_identity", "errors": model_errors})
    runtime = seams.runtime_versions(measurement, pins, ctx=ctx)
    fp = seams.fingerprint_collect(measurement, pack, models["measured"], runtime, ctx=ctx)
    write_json(out / "fingerprint.json", fp)
    prepared = seams.smoke_prepare(pack, head, measurement, out / "smoke", plan_inputs=inputs, fp=fp,
                                   state_root=out / "state", registration_dir=reg,
                                   now=dt.datetime.fromtimestamp(when, dt.timezone.utc), run=seams.run)
    smoke_state = prepared.smoke_dir / "smoke-state.json"
    actual_plan = json.loads(prepared.plan_path.read_text())
    installer = installer_argv(measurement, prepared.plan_path, smoke.driver_argv(prepared)[-1])
    plists = out / "plists"
    seams.run([*installer, "--render-only", str(plists)], check=True, timeout=120)
    night_argv = plistlib.loads((plists / "com.joulewise.night.plist").read_bytes())["ProgramArguments"]
    courier_index = night_argv.index("--courier-bin") + 1
    if night_argv[courier_index] != smoke.driver_argv(prepared)[-1]:
        # An agent courier would be an agent process inside the smoke's night job.
        raise ValueError("rendered night job does not name the smoke's courier wrapper: "
                         + night_argv[courier_index])
    state_path = out / "machine-test.json"
    injector = plists / (INJECT_LABEL + ".plist")
    injector.parent.mkdir(parents=True, exist_ok=True)
    inject_argv = [PYTHON, "-B", str(measurement / "scripts/b6_machine_test.py"),
                   "inject", "--state", str(state_path)]
    # ProcessType Standard, not Background: the busy-core children inherit the job's
    # policy, and a Background job is held to the efficiency cores at low priority,
    # where one spinning core may stay under the idle admission's 1.0 W combined
    # processor-power line and never make the next run wait (design 3.4's "one busy
    # core"). The injector's own polling is a few small reads a second.
    injector.write_bytes(plistlib.dumps({"Label": INJECT_LABEL, "RunAtLoad": True,
        "ProcessType": "Standard", "ProgramArguments": inject_argv,
        "StandardOutPath": str(out / "inject.stdout"), "StandardErrorPath": str(out / "inject.stderr")}))
    # Design 3.1's reduced smoke plus the requested settle and disturbance.
    expected_s = math.ceil((28.4 if PACK_LABELS[pack] == "GAMMA" else 23.4) * 60
                           + agent_pause.PAUSE_RESUME_S + agent_s + busy_s)
    state = {"schema": "joulewise.b6_machine_test.v1", "non_claim": True,
             "measurement_root": str(measurement), "measurement_head": head, "status_porcelain": dirty,
             "out": str(out), "registration_dir": str(reg), "plan_inputs": str(out / "plan-inputs.json"),
             "fingerprint": str(out / "fingerprint.json"), "identities": identities,
             "pack_id": pack, "requested_plan_id": plan_id, "plan_id": actual_plan["plan_id"],
             "t0_epoch_s": actual_plan["t0_epoch_s"], "window_max_s": actual_plan["window_max_s"],
             "smoke_state": str(smoke_state), "plan_path": str(prepared.plan_path),
             "custody_root": str(prepared.custody), "smoke_dir": str(prepared.smoke_dir),
             "state_root": str(prepared.state_root), "injector_plist": str(injector),
             "plists_dir": str(plists), "rendered_plists": sorted(str(p) for p in plists.glob("*.plist")),
             "injector_argv": inject_argv, "installer_argv": installer,
             "rendered_night_argv": night_argv,
             "injections_path": str(out / "injections.jsonl"), "install_script": str(out / "install.zsh"),
             "injection": {"agent_s": agent_s, "busy_s": busy_s, "busy_cores": busy_cores},
             "expected_collection_s": expected_s, "notes": notes}
    write_json(state_path, state)
    script = out / "install.zsh"
    script.write_text("#!/bin/zsh\nset -euo pipefail\n" + shlex.join(installer) + "\n"
                      + "/bin/launchctl bootstrap gui/$(id -u) " + shlex.quote(str(injector)) + "\n"
                      + "print -r -- " + shlex.quote(
                          "Leave the meter connected (its absent path is desk-tested). Exit all agents before the arm. "
                          "After the chain ends, check injections.jsonl and run report --state " + str(state_path))
                      + "\n", encoding="utf-8")
    script.chmod(0o755)
    if install:
        seams.run(["/bin/zsh", str(script)], check=True, timeout=120)
    return state


@dataclasses.dataclass
class InjectSeams:
    now: Callable = time.time
    monotonic_ns: Callable = time.monotonic_ns
    sleep: Callable = time.sleep
    spawn: Callable = subprocess.Popen
    run: Callable = subprocess.run


class Journal:
    """Incremental cheap reads; incomplete final lines wait for the next poll."""
    def __init__(self, path):
        self.path, self.offset, self.pending, self.rows = Path(path), 0, b"", []

    def read(self):
        try:
            with self.path.open("rb") as handle:
                handle.seek(self.offset)
                raw = handle.read()
                self.offset = handle.tell()
        except FileNotFoundError:
            return self.rows
        lines = (self.pending + raw).split(b"\n")
        self.pending = lines.pop()
        for line in lines:
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"journal row is not an object: {self.path}")
                self.rows.append(value)
        return self.rows


def stop_child(child):
    if child.poll() is None:
        child.terminate()
    try:
        child.wait(timeout=5)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait()


def cap_skip_rows(rows):
    # idle_wait.jsonl does not name skip_reason. The controller chooses a cap
    # skip only when the remaining session budget still covers the full cap.
    spent, skipped = 0.0, []
    for row in rows:
        if (row.get("outcome") == "skipped" and row.get("budget_exhausted") is not True
                and 7200 - spent >= 1500):
            skipped.append(row)
        spent += row.get("wait_s", 0)
    return skipped


def inject(state_path, *, seams=None):
    seams = seams or InjectSeams()
    state = json.loads(Path(state_path).read_text())
    out, custody = Path(state["out"]), Path(state["custody_root"])
    children = []
    log = out / "injections.jsonl"

    def record(event, **fields):
        with log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"event": event, "monotonic_ns": seams.monotonic_ns(),
                                     "wall_s": seams.now(), **fields}, sort_keys=True) + "\n")

    def reap(child):
        stop_child(child)
        children.remove(child)

    clocks = Journal(custody / "collection/run_clock.jsonl")
    presence = Journal(custody / "collection/agent_presence.jsonl")
    waits = Journal(custody / "collection/idle_wait.jsonl")
    pause = custody / "collection/pause.json"
    deadline = state["t0_epoch_s"] + state["window_max_s"]
    mono_deadline = seams.monotonic_ns() + max(0, deadline - seams.now()) * 1e9
    phase, agent, saw_pause, agent_end_ns, busy_end_ns = "first_run", None, False, None, None
    busy = []
    rc = 0
    previous_handlers = {}

    def interrupted(signum, _frame):
        # SIGTERM's default action would end the process without the finally
        # below, leaving the agent and busy children running (stage-3 review F2).
        raise InterruptedError(f"injector received signal {signum}")

    try:
        for signum in (signal.SIGTERM, signal.SIGINT):
            previous_handlers[signum] = signal.signal(signum, interrupted)
        record("waiting_first_run")
        while True:
            if (custody / "night/result.json").exists():
                if phase == "busy":
                    for child in busy:
                        reap(child)
                    record("busy_ended", reason="night_result", run_ids=[])
                record("exit", reason="night_result")
                break
            if seams.now() >= deadline or seams.monotonic_ns() >= mono_deadline:
                record("exit", reason="hard_limit")
                break
            rows, wait_rows = clocks.read(), waits.read()
            presence.read()
            # A hazard terminal means no more faults can be injected, even if
            # the courier has not yet published the night result.
            hazard_terminal = (custody / "night/hazard_result.json").exists()
            if phase == "first_run":
                pairs = agent_pause.paired_run_clocks(rows)
                active = next((start for start, end in pairs if end is None), None)
                if active is not None and not hazard_terminal:
                    record("first_run_started", run_id=active["run_id"],
                           record="collection/run_clock.jsonl")
                    # arm.agent_census filters substring hits by executable
                    # identity OR argv[0]. A Python argument suffix is ignored.
                    argv = ["claude-b6-machine-test", str(state["injection"]["agent_s"])]
                    agent = seams.spawn(argv, executable="/bin/sleep", stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL)
                    children.append(agent)
                    agent_due = seams.monotonic_ns() + state["injection"]["agent_s"] * 1e9
                    record("agent_started", pid=agent.pid, argv=argv, executable="/bin/sleep")
                    census = seams.run(list(AGENT_CENSUS_ARGV), check=False, capture_output=True,
                                       text=True, timeout=5)
                    listed = any(line.split() and line.split()[0] == str(agent.pid)
                                 for line in census.stdout.splitlines())
                    record("agent_census", argv=list(AGENT_CENSUS_ARGV), returncode=census.returncode,
                           listed=listed, stdout=census.stdout)
                    if census.returncode != 0 or not listed:
                        raise RuntimeError("injected agent not listed by the production census")
                    phase = "agent"
            elif phase == "agent":
                saw_pause |= pause.exists()
                if seams.monotonic_ns() >= agent_due or agent.poll() is not None:
                    reap(agent)
                    agent_end_ns = seams.monotonic_ns()
                    record("agent_ended", pid=agent.pid)
                    phase = "resume"
            elif phase == "resume":
                saw_pause |= pause.exists()
                later_run = any(row.get("event") == "start"
                                and row["clock"]["monotonic_ns"] > agent_end_ns for row in rows)
                if ((saw_pause and not pause.exists()) or later_run) and not hazard_terminal:
                    record("pause_ended", evidence="pause_marker_removed" if saw_pause else "later_run_start")
                    for _ in range(state["injection"]["busy_cores"]):
                        child = seams.spawn([PYTHON, "-B", "-c", "while True: pass"],
                                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL)
                        children.append(child)
                        busy.append(child)
                    busy_end_ns = seams.monotonic_ns() + state["injection"]["busy_s"] * 1e9
                    record("busy_started", pids=[child.pid for child in busy])
                    # Only a NEW cap skip can stop this disturbance.
                    wait_offset = len(wait_rows)
                    phase = "busy"
            elif phase == "busy":
                cap_rows = [row for row in cap_skip_rows(wait_rows) if row in wait_rows[wait_offset:]]
                if cap_rows or seams.monotonic_ns() >= busy_end_ns or hazard_terminal:
                    for child in busy:
                        reap(child)
                    record("busy_ended", reason="idle_cap_skip" if cap_rows else
                           "hazard_terminal" if hazard_terminal else "duration",
                           run_ids=[row["run_id"] for row in cap_rows])
                    phase = "terminal"
            seams.sleep(1)
    except BaseException as exc:
        rc = 1
        try:
            record("exception", error=f"{type(exc).__name__}: {exc}")
        except BaseException:
            pass  # Failure of the clock or journal cannot stop child cleanup.
    finally:
        # A repeated TERM/INT (launchd bootout, an impatient operator) must not
        # interrupt the reaping of another child; handlers come back afterwards.
        for signum in previous_handlers:
            signal.signal(signum, signal.SIG_IGN)
        for child in list(children):
            try:
                reap(child)
            except BaseException as exc:
                rc = 1
                # Journal failures must never prevent cleanup of another child.
                try:
                    record("cleanup_exception", pid=child.pid, error=f"{type(exc).__name__}: {exc}")
                except BaseException:
                    pass
            else:
                try:
                    record("child_reaped", pid=child.pid)
                except BaseException:
                    rc = 1
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)
    return rc


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def read_rows(path):
    try:
        return Journal(path).read()
    except (OSError, ValueError):
        return []


def report(state_path, *, uninstall=False, desk=smoke.desk, run=subprocess.run):
    state = json.loads(Path(state_path).read_text())
    prepared = smoke.SmokePrepared.from_json(json.loads(Path(state["smoke_state"]).read_text()))
    custody, out = prepared.custody, Path(state["out"])
    terminal = read_json(custody / "night/result.json")
    if not isinstance(terminal, dict):
        raise ValueError("report requires the chain's terminal night/result.json")
    hazard = read_json(custody / "night/hazard_result.json", {})
    driver_exit = terminal.get("exit_code", hazard.get("driver_exit_code"))
    # The production night result's exit is the chain exit; courier failure is
    # independently resolved by smoke.desk when no driver code is supplied.
    desk_result_path = prepared.smoke_dir / "smoke-result.json"
    result = read_json(desk_result_path)
    if result is None:
        result = desk(prepared, driver_exit=driver_exit, run=run)
    archive = Path(result["archive"])
    flags = read_rows(archive / "derived/flags.jsonl")
    exclusions = read_json(archive / "derived/exclusions.json", {})
    excluded = {r["run_id"] for r in exclusions.get("members_excluded", [])}
    clocks = read_rows(custody / "collection/run_clock.jsonl")
    pairs = agent_pause.paired_run_clocks(clocks)
    waits = read_rows(custody / "collection/idle_wait.jsonl")
    episodes = hazard.get("agent_pause", {}).get("episodes", [])
    items = []

    def item(name, observed, evidence, detail=None):
        items.append({"item": name, "observed": bool(observed), "evidence": evidence, "detail": detail})

    pause_ok = bool(episodes) and all(ep.get("pause_end", {}).get("monotonic_ns", -1)
        - ep.get("last_sighting", {}).get("monotonic_ns", 0) >= agent_pause.PAUSE_RESUME_S * 1e9
        for ep in episodes)
    overlap_ids = {r.get("scope", {}).get("run_id") for r in flags if r.get("code") == "agent.presence_overlap"}
    expected_overlap = {r["run_id"] for r in agent_pause.overlap_flags(episodes, clocks)} if episodes else set()
    overlap_ok = bool(expected_overlap) and expected_overlap <= overlap_ids and expected_overlap <= excluded
    chain_ok = terminal.get("chain_exit_code") == 0 and hazard.get("chain", {}).get("exit_code") == 0
    chain_kept = chain_ok and hazard.get("agent_pause", {}).get("stopped_by_limit") is False
    presence_rows = read_rows(custody / "collection/agent_presence.jsonl")
    journal_ok = bool(episodes) and all(
        any(r.get("event") == "sighting" and r.get("at") == ep.get("last_sighting") for r in presence_rows)
        and any(r.get("event") == "resume" and r.get("at") == ep.get("pause_end") for r in presence_rows)
        for ep in episodes)
    flags_written = {"agent.presence", "agent.presence_overlap"} <= {r.get("code") for r in flags}
    item("agent pause", pause_ok and overlap_ok and chain_kept and journal_ok and flags_written,
         ["night/hazard_result.json:agent_pause", "collection/agent_presence.jsonl",
          "derived/flags.jsonl", "derived/exclusions.json"],
         {"episode": bool(episodes), "settle": pause_ok, "overlapping_unit_excluded": overlap_ok,
          "chain_continued": chain_kept, "journal": journal_ok, "flags_written": flags_written})
    item("agent census", any(r.get("event") == "agent_census" and r.get("listed") is True
                             for r in read_rows(out / "injections.jsonl")), ["injections.jsonl:agent_census"])
    runner_paused = pause_ok and journal_ok and all(
        not (ep["since"]["monotonic_ns"] <= start["clock"]["monotonic_ns"]
             < ep["pause_end"]["monotonic_ns"]) for start, _ in pairs for ep in episodes)
    item("runner pause", runner_paused
         and any(start["clock"]["monotonic_ns"] > ep["pause_end"]["monotonic_ns"]
                 for start, end in pairs if end is not None for ep in episodes),
         ["collection/agent_presence.jsonl", "collection/run_clock.jsonl"])
    fresh_evidence = []
    fresh_idle = bool(episodes)
    for ep in episodes:
        resumed = next((start for start, _ in pairs
                        if start["clock"]["monotonic_ns"] > ep["pause_end"]["monotonic_ns"]), None)
        metadata = (archive / "sources/claim-runs" / resumed["run_id"] / "metadata.json") if resumed else None
        admission = read_json(metadata, {}).get("environment_admission", {}) if metadata else {}
        attempts = admission.get("attempts", [])
        fresh_idle &= bool(attempts) and isinstance(attempts[0].get("sampler_start_s"), (int, float)) \
            and attempts[0]["sampler_start_s"] >= ep["pause_end"].get("wall_s", float("inf"))
        if metadata and attempts:
            fresh_evidence.append(str(metadata.relative_to(archive)) + ":environment_admission.attempts")
    item("fresh idle admission", runner_paused and fresh_idle, fresh_evidence)
    skip_flags = [r for r in flags if r.get("code") == "idle.wait_cap_skip"]
    skips = {r.get("scope", {}).get("run_id") for r in skip_flags} - {None}
    skipped_pairs = [(start, end) for start, end in pairs if start["run_id"] in skips and end]
    later = any(start["clock"]["monotonic_ns"] > end["clock"]["monotonic_ns"]
                and any(w.get("run_id") == start["run_id"] and w.get("outcome") == "admitted" for w in waits)
                and read_json(archive / "sources/claim-runs" / start["run_id"] / "summary_metrics.json", {}).get("status") == "succeeded"
                for start, finish in pairs if finish and start["run_id"] not in skips
                for _, end in skipped_pairs)
    # Controller records consumed WAIT (excluding the first ordinary slice),
    # and skips before another slice would cross the cap. Consult metadata to
    # establish that boundary; do not demand wait_s >= 1500 (never its contract).
    retry_evidence = []
    cap_ok = False
    retry_attempts = []
    for run_id in sorted(skips):
        meta_path = archive / "sources/claim-runs" / run_id / "metadata.json"
        admission = read_json(meta_path, {}).get("environment_admission", {})
        attempts = admission.get("attempts", [])
        cap = admission.get("effective_wait_cap_s")
        if len(attempts) > 1:
            retry_evidence.append(str(meta_path.relative_to(archive)) + ":environment_admission.attempts")
            retry_attempts.extend(attempts)
        if (admission.get("skip_reason") == "wait_cap_reached" and isinstance(cap, (int, float))
                and cap == 1500 and attempts):
            first, last = attempts[0], attempts[-1]
            if all(isinstance(a.get(k), (int, float)) for a in (first, last) for k in ("start_s", "end_s", "sampler_start_s")):
                boundary = last["end_s"] - first["sampler_start_s"] + last["end_s"] - last["sampler_start_s"]
                cap_ok |= boundary > cap and any(w.get("run_id") == run_id and w.get("outcome") == "skipped"
                    and w.get("wait_s") == admission.get("wait_s") for w in waits)
    item("idle cap", len(skips) == 1 and cap_ok and later,
         ["derived/flags.jsonl:idle.wait_cap_skip", "collection/idle_wait.jsonl", *retry_evidence],
         {"exactly_one_run": len(skips) == 1, "cap_boundary": cap_ok, "later_runs_measured": later})
    starts = [a.get("sampler_start_s") for a in retry_attempts]
    item("sampler restarts", len(starts) > 1 and all(isinstance(s, (int, float)) for s in starts)
         and all(b > a for a, b in zip(starts, starts[1:])), retry_evidence)
    item("sampler startup readings", bool(retry_attempts) and all(
         isinstance(a.get("start_s"), (int, float)) and isinstance(a.get("sampler_start_s"), (int, float))
         and a["start_s"] >= a["sampler_start_s"] for a in retry_attempts), retry_evidence)
    teardown_proofs = [a.get("sampler_teardown", {}) for a in retry_attempts]
    item("sampler clean termination and no survivor", bool(teardown_proofs) and all(
         p.get("status") == "clean" and p.get("spawn_observed") is True and p.get("leader_reaped") is True
         and p.get("census_completed") is True and p.get("group_survivors") == []
         and p.get("escaped_candidates") == [] for p in teardown_proofs), retry_evidence)
    meter_paths = sorted((custody / "hazards/meter").glob("stream-*.jsonl"))
    headers = [(p, read_rows(p)) for p in meter_paths]
    absent = any(rows and rows[0].get("status") == "absent" for _, rows in headers)
    present = any(rows and rows[0].get("status") == "streaming" for _, rows in headers)
    item("meter unplugged", absent and not present and any(r.get("code") == "meter.absent" for r in flags),
         ["hazards/meter/stream-*.jsonl:status", "derived/flags.jsonl:meter.absent"],
         "meter present: not exercised" if present else None)
    awake = hazard.get("keep_awake", {})
    sleep_flags = [r for r in flags if str(r.get("code", "")).startswith("sleep.")
                   and (r.get("code") == "sleep.in_run" or r.get("scope", {}).get("run_id") in excluded)]
    sleep_exclusions = any(str(code).startswith("sleep.") for r in exclusions.get("members_excluded", [])
                           for code in r.get("codes", []))
    expected_run_ids, roster_error = set(), None
    try:
        from joulewise.b5 import plan as window_plan
        pack_root = prepared.measurement / "configs/campaigns" / prepared.pack_id
        tree = json.loads((pack_root / "plan_tree.json").read_text())
        dispatches = window_plan.resolve_stage_dispatches(tree, prepared.measurement)
        counts = {row["stage_id"]: row["expected_count"] for row in tree["stage_graph"]
                  if row["kind"] == "campaign_collection"}
        if not dispatches or any(d.error or d.run_ids is None for d in dispatches):
            raise ValueError("smoke plan collection roster is unresolved")
        for dispatch in dispatches:
            count = counts[dispatch.stage_id]
            if type(count) is not int or count <= 0 or len(dispatch.run_ids) < count:
                raise ValueError("smoke plan collection count is invalid")
            expected_run_ids.update(dispatch.run_ids[:count])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        roster_error = f"{type(exc).__name__}: {exc}"
    summaries = {run_id: read_json(archive / "sources/claim-runs" / run_id / "summary_metrics.json")
                 for run_id in sorted(expected_run_ids)}
    statuses = {run_id: value.get("status") if isinstance(value, dict) else None
                for run_id, value in summaries.items()}
    # The controller records an idle cap as a FAILED bundle, with the reason
    # in environment_admission; "skipped" belongs to idle_wait.jsonl only.
    cap_failures = {run_id for run_id in skips if read_json(
        archive / "sources/claim-runs" / run_id / "metadata.json", {}).get(
            "environment_admission", {}).get("skip_reason") == "wait_cap_reached"}
    expected_exceptions = expected_overlap | skips
    collection_problems = {run_id: status for run_id, status in statuses.items()
                           if not ((status == "failed" and run_id in cap_failures)
                                   if run_id in skips else status == "succeeded")}
    # Harvest retains the full campaign roster, including unselected members
    # without spans. Only the members dispatched by the reduced plan ran.
    smoke_excluded = excluded & expected_run_ids
    unexpected_exclusions = {row["run_id"]: row.get("codes", [])
                             for row in exclusions.get("members_excluded", [])
                             if row["run_id"] in smoke_excluded - expected_exceptions}
    physical_exclusions = bool(unexpected_exclusions) and all(
        codes and all(smoke._is_physical(code) for code in codes)
        for codes in unexpected_exclusions.values())
    item("collection ran", bool(expected_run_ids) and roster_error is None
         and expected_exceptions <= expected_run_ids and not collection_problems
         and smoke_excluded == expected_exceptions,
         ["measurement:plan_tree.json and order_manifest.json", "sources/claim-runs/*/summary_metrics.json",
          "sources/claim-runs/*/metadata.json:environment_admission", "derived/exclusions.json"],
         {"member_status": statuses, "unexpected_status": collection_problems,
          "expected_exclusions": sorted(expected_exceptions), "actual_exclusions": sorted(excluded),
          "exclusion_detail": exclusions.get("members_excluded", []),
          "unexpected_exclusions": unexpected_exclusions,
          "guidance": "physical exclusion: rerun the test" if physical_exclusions else None,
          "roster_error": roster_error})
    complete_ids = {start["run_id"] for start, end in pairs if end and all(
        isinstance(row.get("clock", {}).get("sleep_offset_ns"), int) for row in (start, end))}
    missing_ids = sorted(expected_run_ids - complete_ids)
    # M-2 (stage-3 review): every run the reduced smoke plan dispatches needs its
    # start and end reading; a run with no clock row at all is not observed.
    readings = (bool(expected_run_ids) and roster_error is None and not missing_ids and bool(pairs)
                and all(end and all(isinstance(row.get("clock", {}).get("sleep_offset_ns"), int)
                                    for row in (start, end)) for start, end in pairs))
    no_run_sleep = readings and all(end["clock"]["sleep_offset_ns"] - start["clock"]["sleep_offset_ns"] <= 1_000_000
                                    for start, end in pairs)
    item("keep-awake", awake.get("verified_start") is True and awake.get("verified_end") is True
         and not sleep_flags and not sleep_exclusions and not hazard.get("sleep", {}).get("runs_excluded") and no_run_sleep,
         ["night/hazard_result.json:keep_awake", "collection/run_clock.jsonl", "derived/exclusions.json"])
    item("per-run sleep readings", readings, ["collection/run_clock.jsonl:clock.sleep_offset_ns",
         "measurement:plan_tree.json and order_manifest.json"],
         {"missing_or_incomplete_run_ids": missing_ids, "roster_error": roster_error})
    item("chain exit", chain_ok, ["night/result.json:chain_exit_code", "night/hazard_result.json:chain.exit_code"])
    item("smoke desk", result.get("status") == "physics", ["smoke-result.json:status"], result.get("status"))
    item("smoke errors absent", result.get("errors") == [], ["smoke-result.json:errors"])
    item("harvest exit", result.get("harvest_exit") == 0, ["smoke-result.json:harvest_exit"])
    report_value = {"schema": "joulewise.b6_machine_test_report.v1", "non_claim": True,
                    "items": items, "smoke_result": str(desk_result_path)}
    # Desk can be repeated; the smoke/harvest evidence stays create-once.
    temp = out / ".report.json.tmp"
    temp.write_text(json.dumps(report_value, indent=2, sort_keys=True) + "\n")
    temp.replace(out / "report.json")
    if uninstall:
        run([*state["installer_argv"], "--uninstall"], check=True, timeout=120)
        run(["/bin/launchctl", "bootout", f"gui/{os.getuid()}", state["injector_plist"]],
            check=True, timeout=30)
    return report_value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare")
    p.add_argument("--measurement-root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--pack", default=PACK, choices=sorted(PACK_LABELS))
    p.add_argument("--lead-s", type=float, default=900)
    p.add_argument("--busy-cores", type=int, default=1)
    p.add_argument("--agent-s", type=float, default=AGENT_LIFETIME_S)
    p.add_argument("--busy-s", type=float, default=1620)
    p.add_argument("--install", action="store_true")
    i = commands.add_parser("inject")
    i.add_argument("--state", type=Path, required=True)
    r = commands.add_parser("report")
    r.add_argument("--state", type=Path, required=True)
    r.add_argument("--uninstall", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            state = prepare(args.measurement_root, args.out, pack=args.pack, lead_s=args.lead_s,
                            busy_cores=args.busy_cores, agent_s=args.agent_s, busy_s=args.busy_s,
                            install=args.install)
            print(state["install_script"])
            print(f"Expected collection: about {math.ceil(state['expected_collection_s'] / 60)} minutes "
                  "after launch; launch lead and desk harvest are additional.")
            return 0
        if args.command == "inject":
            return inject(args.state)
        value = report(args.state, uninstall=args.uninstall)
        for item in value["items"]:
            status = "observed" if item["observed"] else "not observed"
            detail = item["detail"] if isinstance(item["detail"], str) else None
            if item["item"] in {"agent pause", "collection ran"} and isinstance(item["detail"], dict):
                detail = ", ".join(f"{key}={value}" for key, value in item["detail"].items())
            print(f"{item['item']}: {status}" + (f"; {detail}" if detail else "")
                  + (" [" + ", ".join(item["evidence"]) + "]" if item["evidence"] else ""))
        return 0
    except Exception as exc:
        print(f"machine test error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
