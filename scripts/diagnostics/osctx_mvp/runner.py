"""Render and run balanced OSCTX blocks. Live execution belongs to the lead."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import inspect
import json
import math
import os
from pathlib import Path
import plistlib
import re
import shlex
import signal
import subprocess
import sys
import time
import uuid

try:
    from . import ledger
    from .common import blocks, load_config, write_json
    from .cell import display_state, hid_idle_seconds
    from .analyze import (analyze_directory, bundle_evidence, equivalence_power,
                          power_table, stage0_spread, u_replication_spread)
except ImportError:
    import ledger
    from common import blocks, load_config, write_json
    from cell import display_state, hid_idle_seconds
    from analyze import (analyze_directory, bundle_evidence, equivalence_power,
                         power_table, stage0_spread, u_replication_spread)

ROOT = Path(__file__).resolve().parents[3]
PREFIX = "com.joulewise.dummy.osctx."


def label(block_id: str, arm: str, attempt: int) -> str:
    return PREFIX + f"{block_id}.{arm}.a{attempt}"


def cell_argv(action: dict, config_path: Path, python: str, allow_pids: list[int]) -> list[str]:
    result = [python, str(Path(__file__).with_name("cell.py")), "--out", action["cell_dir"],
              "--state", action["state"], "--context", action["context"],
              "--cell-id", str(action["cell_id"]), "--stage", action["stage"],
              "--config", str(config_path), "--python", python]
    for pid in allow_pids:
        result += ["--allow-pid", str(pid)]
    return result


def zsh_exec(argv: list[str]) -> list[str]:
    return ["/bin/zsh", "-c", "exec " + shlex.join(argv)]


def shell_argv(argv: list[str]) -> list[str]:
    return ["nohup", "caffeinate", "-is", *zsh_exec(argv)]


def plist_for(action: dict, argv: list[str], python: str) -> dict:
    result = {"Label": action["label"], "ProgramArguments": zsh_exec(argv),
              "EnvironmentVariables": {"PATH": os.environ.get("PATH", "/usr/bin:/bin:/usr/sbin:/sbin"),
                                       "HF_HUB_OFFLINE": "1", "HOME": os.environ["HOME"]},
              "WorkingDirectory": str(ROOT), "StandardOutPath": str(Path(action["cell_dir"]) / "stdout.log"),
              "StandardErrorPath": str(Path(action["cell_dir"]) / "stderr.log"), "RunAtLoad": True}
    process_type = {"D": None, "I": "Interactive", "B": "Background"}[action["context"]]
    if process_type:
        result["ProcessType"] = process_type
    return result


def make_action(out: Path, stage: str, block: dict, slot: int, attempt: int, config_path: Path,
                python: str, allow_pids: list[int], *, write: bool = True) -> dict:
    arm = block["arms"][slot]
    directory = (out / f"{block['id']}.{slot+1}.{arm}.a{attempt}").resolve()
    action = {"stage": stage, "block": block["id"], "state": block["state"], "phase": block.get("phase"),
              "context": arm, "cell_id": slot+1, "attempt": attempt, "discard": block["discard"],
              "cell_dir": str(directory), "label": label(block["id"], arm, attempt)}
    argv = cell_argv(action, config_path, python, allow_pids)
    if arm == "SH":
        action["start"] = shell_argv(argv)
        action["detached"] = True
    else:
        action["start"] = ["/bin/launchctl", "bootstrap", f"gui/{os.getuid()}", str(directory / "job.plist")]
        action["stop"] = ["/bin/launchctl", "bootout", f"gui/{os.getuid()}", str(directory / "job.plist")]
        action["detached"] = False
    if write:
        directory.mkdir(parents=True, exist_ok=True)
        if arm != "SH":
            with (directory / "job.plist").open("wb") as stream:
                plistlib.dump(plist_for(action, argv, python), stream)
    return action


def plan(out: Path, config_path: Path, config: dict, stage: str, python: str) -> list[dict]:
    out.mkdir(parents=True, exist_ok=True)
    actions = [make_action(out, stage, block, slot, 1, config_path, python, [], write=True)
               for block in blocks(config, stage) for slot in range(len(block["arms"]))]
    sequence = []
    previous_state = "on"
    for block in blocks(config, stage):
        target = "asleep" if block["state"] == "S" else "on"
        if stage == "S" and target != previous_state:
            sequence.append({"transition": "pmset displaysleepnow" if target == "asleep" else "display wake",
                             "verify": "display state and pmset log", "settle_seconds": config["display_settle_seconds"]})
        previous_state = target
        sequence.append({"block": block["id"], "state": block["state"], "phase": block.get("phase"),
                         "arms": block["arms"], "discard": block["discard"],
                         "gate": "HIDIdleTime >= 600 s" if block["state"] == "U" else None,
                         "starts": [a["start"] for a in actions if a["block"] == block["id"]],
                         "interrupted": "discard entire block and retry in same order"})
    write_json(out / "command_sequence.json", {"stage": stage, "seed": config["seed"], "actions": actions,
                                                    "sequence": sequence})
    return actions


class SystemBackend:
    """Small live boundary; offline tests inject a fake in its place."""
    def run(self, argv, *, timeout=None):
        return subprocess.run(argv, capture_output=True, text=True, check=False, timeout=timeout)

    def spawn_shell(self, argv, directory):
        with (directory / "stdout.log").open("wb") as stdout, (directory / "stderr.log").open("wb") as stderr:
            return subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL,
                                    stdout=stdout, stderr=stderr, start_new_session=True)

    def idle(self):
        return hid_idle_seconds()

    def display(self):
        return display_state()

    def sleep(self, seconds):
        time.sleep(seconds)

    def now(self):
        return time.monotonic()

    def process_exists(self, pid):
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False

    def stop_shell(self, process):
        self.stop_shell_group(process.pid)
        process.wait(timeout=15)

    def stop_shell_group(self, pgid):
        def members():
            result = self.run(["/usr/bin/pgrep", "-g", str(pgid)], timeout=60)
            if result.returncode not in (0, 1):
                raise RuntimeError(f"pgrep failed for shell group {pgid}")
            return [int(pid) for pid in result.stdout.split()]
        for sig in (signal.SIGTERM, signal.SIGKILL):
            deadline = time.monotonic() + 15
            while True:
                current = members()
                if not current:
                    return
                for pid in current:
                    try:
                        os.kill(pid, sig)
                    except ProcessLookupError:
                        pass
                if time.monotonic() >= deadline:
                    break
                time.sleep(.1)
        remaining = members()
        if remaining:
            raise RuntimeError(f"shell process-group survivor {pgid}: {remaining}")


def runner_ancestry() -> list[int]:
    pids = []
    current = os.getpid()
    while current > 1 and current not in pids:
        pids.append(current)
        result = subprocess.run(["/bin/ps", "-p", str(current), "-o", "ppid="], capture_output=True, text=True)
        current = int(result.stdout.strip() or 1)
    return pids


def interrupted(record: dict, state: str, min_idle: float, expected_display: str) -> bool:
    if state == "U" and (not isinstance(record.get("hid_idle_seconds"), (int, float)) or
                         not math.isfinite(record["hid_idle_seconds"]) or
                         record["hid_idle_seconds"] < min_idle):
        return True
    actual = record.get("display_state", "unknown")
    return actual != expected_display


def retry_block(block: dict, attempt: int) -> dict:
    return {**block, "attempt": attempt + 1, "arms": list(block["arms"])}


def wait_gate(backend, config, log, *, state="U"):
    unknown_polls = 0
    expected_display = "asleep" if state == "S" else "on"
    while True:
        try:
            idle = backend.idle() if state == "U" else None
            display = backend.display()
            read_error = None
        except Exception as exc:
            idle, display, read_error = None, "unknown", str(exc)
        unknown = (state == "U" and (not isinstance(idle, (int, float)) or not math.isfinite(idle))) or display not in ("on", "asleep")
        unknown_polls = unknown_polls + 1 if unknown else 0
        log(event="gate", idle_seconds=idle, display_state=display, read_error=read_error,
            unknown_polls=unknown_polls)
        if unknown_polls >= 3:
            raise RuntimeError(f"stage stopped: {state} admission observation unknown after 3 polls")
        if display == expected_display and (state != "U" or idle >= config["hid_idle_seconds"]):
            return
        backend.sleep(config["hid_poll_seconds"])


def known_display(backend, config, log):
    for poll in range(1, 4):
        try:
            display = backend.display()
        except Exception as exc:
            display = "unknown"
            log(event="display_read_error", poll=poll, error=str(exc))
        if display in ("on", "asleep"):
            return display
        log(event="display_unknown", poll=poll)
        if poll < 3:
            backend.sleep(config["hid_poll_seconds"])
    raise RuntimeError("stage stopped: display observation unknown after 3 polls")


def transition(backend, target: str, config: dict, log):
    before = bounded_run(backend, ["/usr/bin/pmset", "-g", "log"])
    if before.returncode:
        raise RuntimeError("display transition log unreadable before request")
    argv = ["/usr/bin/pmset", "displaysleepnow"] if target == "asleep" else ["/usr/bin/caffeinate", "-u", "-t", "1"]
    result = bounded_run(backend, argv)
    if result.returncode:
        raise RuntimeError(f"display transition failed: {argv}")
    deadline = backend.now() + 30
    unknown_polls = 0
    while True:
        after = bounded_run(backend, ["/usr/bin/pmset", "-g", "log"])
        try:
            state = backend.display()
        except Exception as exc:
            state = "unknown"
            log(event="display_read_error", error=str(exc))
        unknown_polls = unknown_polls + 1 if state not in ("on", "asleep") else 0
        if unknown_polls >= 3:
            raise RuntimeError("stage stopped: display transition observation unknown after 3 polls")
        if state == target and after.returncode == 0 and before.stdout != after.stdout:
            break
        if backend.now() >= deadline:
            raise RuntimeError("display transition unverified")
        backend.sleep(1)
    log(event="display_transition", target=target, state=state, before=before.stdout, after=after.stdout)
    backend.sleep(config["display_settle_seconds"])


NETWORK_TIME = ["sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime"]


@contextmanager
def Critical():
    """Finish a bounded cleanup operation before delivering a signal."""
    outer = not _critical_stack
    if outer:
        previous, pending = {}, []
        def defer(signum, frame):
            pending.append(signum)
        for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
            previous[signum] = signal.getsignal(signum)
            signal.signal(signum, defer)
        _critical_stack.append((previous, pending))
    try:
        yield
    finally:
        if outer:
            previous, pending = _critical_stack.pop()
            for signum, handler in previous.items():
                signal.signal(signum, handler)
            if pending:
                raise KeyboardInterrupt(f"signal {pending[0]}")


_critical_stack = []


def bounded_run(backend, argv):
    params = inspect.signature(backend.run).parameters
    if "timeout" in params or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()):
        return backend.run(argv, timeout=60)
    return backend.run(argv)


_active_network_owner = None


def with_network_time(backend, log, body, *, ownership_path=None):
    """Fail closed on off; always attempt on, including after off failure."""
    global _active_network_owner
    owner = None
    if ownership_path is not None:
        if unreleased(ownership_path.parent):
            raise RuntimeError(f"unreleased ownership; run --recover {ownership_path.parent}")
        owner = "network_time:" + uuid.uuid4().hex
        ledger.append(ownership_path, {"event": "acquire", "label": owner,
                                       "action": {"context": "NETWORK_TIME"}})
        _active_network_owner = owner
    def toggle(value):
        argv = [*NETWORK_TIME, value]
        try:
            result = bounded_run(backend, argv)
        except BaseException as exc:
            log(event="network_time", argv=argv, returncode=None, stderr=str(exc))
            raise RuntimeError(f"network time {value} failed: {exc}") from exc
        log(event="network_time", argv=argv, returncode=result.returncode, stderr=result.stderr)
        if result.returncode:
            raise RuntimeError(f"network time {value} failed ({result.returncode}): {result.stderr}")
    try:
        toggle("off")
        return body()
    finally:
        try:
            with Critical():
                toggle("on")
                if owner is not None:
                    ledger.append(ownership_path, {"event": "release", "label": owner})
        finally:
            if owner is not None:
                _active_network_owner = None


def launch_pid(backend, action, log):
    """Capture the job PID while registered, before completion can erase it."""
    target = f"gui/{os.getuid()}/{action['label']}"
    directory = Path(action["cell_dir"])
    for attempt in range(50):
        result = backend.run(["/bin/launchctl", "print", target])
        match = re.search(r"(?m)^\s*pid = (\d+)\s*$", result.stdout) if result.returncode == 0 else None
        if match or (directory / "done.json").exists():
            break
        if attempt < 49:
            backend.sleep(.1)
    if not match and not (directory / "done.json").exists():
        raise RuntimeError(f"launchd PID unavailable while cell is running: {action['label']}")
    pid = int(match.group(1)) if match else None
    pgid = None
    if pid is not None:
        group = backend.run(["/bin/ps", "-p", str(pid), "-o", "pgid="])
        if group.returncode == 0 and group.stdout.strip().isdigit():
            pgid = int(group.stdout.strip())
    proof = {"pid": pid, "pgid": pgid, "print_returncode": result.returncode,
             "print_stderr": result.stderr}
    write_json(directory / "launch_proof.json", proof)
    log(event="launch_pid", label=action["label"], **proof)
    return proof


def prove_bootout(backend, action, proof, log):
    stop = bounded_run(backend, action["stop"])
    registered = bounded_run(backend, ["/bin/launchctl", "print", f"gui/{os.getuid()}/{action['label']}"])
    if proof and proof["pid"] is not None:
        pid = proof["pid"]
        group = bounded_run(backend, ["/usr/bin/pgrep", "-g", str(proof["pgid"] or pid)])
        process = bounded_run(backend, ["/bin/ps", "-p", str(pid), "-o", "pid="])
        survivor = (group.returncode != 1 or bool(group.stdout.strip()) or
                    process.returncode != 1 or bool(process.stdout.strip()))
        check = {"pid": pid, "pgid": proof["pgid"], "pgrep_returncode": group.returncode,
                 "pgrep_stdout": group.stdout, "pgrep_stderr": group.stderr,
                 "ps_returncode": process.returncode, "ps_stdout": process.stdout,
                 "ps_stderr": process.stderr}
    else:
        # Only our cell command carries this script/--out pair. An arbitrary
        # cell-directory match could include the runner or a log viewer.
        literal_dir = re.sub(r"([\\.^$*+?{}\[\]()|])", r"\\\1", action["cell_dir"])
        pattern = (r"^[^[:space:]]+[[:space:]]+[^[:space:]]*/osctx_mvp/cell\.py"
                   r"[[:space:]]+--out[[:space:]]+" + literal_dir + r"([[:space:]]|$)")
        group = bounded_run(backend, ["/usr/bin/pgrep", "-f", pattern])
        survivor = group.returncode != 1 or bool(group.stdout.strip())
        check = {"pid": None, "fallback_pattern": pattern,
                 "pgrep_returncode": group.returncode, "pgrep_stdout": group.stdout,
                 "pgrep_stderr": group.stderr}
    log(event="bootout_proof", label=action["label"], bootout_returncode=stop.returncode,
        bootout_stderr=stop.stderr, print_returncode=registered.returncode,
        print_stdout=registered.stdout, print_stderr=registered.stderr, **check)
    if registered.returncode == 0 or survivor:
        raise RuntimeError(f"launchd survivor or proof error: {action['label']}")
    if stop.returncode:
        log(event="bootout_unneeded_or_failed", label=action["label"], returncode=stop.returncode)


def unreleased(root: Path, *, allow_active_network=False) -> dict[str, dict]:
    pending = {}
    for path in [root / "owned.jsonl", *sorted(root.glob("*/owned.jsonl"))]:
        if path.exists():
            pending.update(ledger.owned(path))
    if allow_active_network and _active_network_owner is not None:
        pending.pop(_active_network_owner, None)
    return pending


def _execute_cells(out: Path, config_path: Path, config: dict, stage: str, python: str,
                   *, backend, existing_actions=None, extra_allow_pids=None,
                   ownership_path=None) -> None:
    backend = backend or SystemBackend()
    ownership_path = ownership_path or out / "owned.jsonl"
    if unreleased(ownership_path.parent, allow_active_network=True):
        raise RuntimeError(f"unreleased ownership; run --recover {ownership_path.parent}")
    ownership: dict[str, tuple[dict, object | None]] = {}
    launch_proofs = {}
    allow_pids = list(dict.fromkeys((runner_ancestry() if isinstance(backend, SystemBackend) else []) +
                                    (extra_allow_pids or [])))
    old_handlers = {}
    stage_reference = None
    invalid_cells = {arm: 0 for arm in config["contexts"]}
    if isinstance(backend, SystemBackend):
        def interrupted_signal(signum, frame):
            raise KeyboardInterrupt(f"signal {signum}")
        for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
            old_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, interrupted_signal)
    def log(**record):
        with (out / "events.jsonl").open("a") as stream:
            stream.write(json.dumps({"wall_ns": time.time_ns(), **record}) + "\n")
    def cleanup(action):
        owned = ownership.get(action["label"])
        if owned is None:
            return
        _, process = owned
        with Critical():
            if action["context"] == "SH":
                backend.stop_shell(process)
            else:
                prove_bootout(backend, action, launch_proofs.get(action["label"]), log)
            ledger.append(ownership_path, {"event": "release", "label": action["label"]})
            ownership.pop(action["label"])
        log(event="cleanup_proved", label=action["label"])
    def ledger_cells(actions):
        return [ledger.cell_entry(Path(a["cell_dir"]), slot=a["cell_id"], arm=a["context"], label=a["label"])
                for a in actions if (Path(a["cell_dir"]) / "cell.json").is_file()]
    def block_record(kind, block, attempt, actions, reference, **extra):
        ledger.append(out / "ledger.jsonl", {"event": kind, "stage": stage, "block": block["id"],
                      "attempt": attempt, "discard": block["discard"],
                      "reference_hash": reference, "cells": ledger_cells(actions), **extra}, sealed=True)
    try:
        previous = "on"
        for block in blocks(config, stage):
            state = block["state"]
            target = "asleep" if state == "S" else "on"
            if stage == "S" and target != previous:
                known_display(backend, config, log)
                transition(backend, target, config, log)
            previous = target
            attempt = 1
            while True:
                pending_reference = stage_reference
                if stage == "S" and state == "S" and known_display(backend, config, log) != "asleep":
                    transition(backend, "asleep", config, log)
                actions = [make_action(out, stage, block, slot, attempt, config_path, python, allow_pids,
                                       write=not (attempt == 1 and existing_actions is not None))
                           for slot in range(len(block["arms"]))]
                if attempt == 1 and existing_actions is not None:
                    # Rendered directories exist. Reuse them, but add the runner PID allowlist to the live argv.
                    for action in actions:
                        if action["context"] != "SH":
                            with (Path(action["cell_dir"]) / "job.plist").open("wb") as stream:
                                plistlib.dump(plist_for(action, cell_argv(action, config_path, python, allow_pids), python), stream)
                bad = False
                for action in actions:
                    if state == "U" and stage != "stage0":
                        wait_gate(backend, config, log)
                    elif state == "S":
                        wait_gate(backend, config, log, state="S")
                    directory = Path(action["cell_dir"])
                    if (directory / "done.json").exists():
                        raise FileExistsError(directory / "done.json")
                    try:
                        ledger.append(ownership_path, {"event": "acquire", "label": action["label"], "action": action})
                        ownership[action["label"]] = action, None
                        if action["context"] == "SH":
                            process = backend.spawn_shell(action["start"], directory)
                            ledger.append(ownership_path, {"event": "update", "label": action["label"],
                                                           "pid": process.pid if hasattr(process, "pid") else None})
                        else:
                            result = backend.run(action["start"])
                            if result.returncode:
                                raise RuntimeError(f"bootstrap failed: {action['label']}")
                            launch_proofs[action["label"]] = launch_pid(backend, action, log)
                            ledger.append(ownership_path, {"event": "update", "label": action["label"],
                                                           "proof": launch_proofs[action["label"]]})
                            process = None
                        ownership[action["label"]] = action, process
                        deadline = backend.now() + config["timeout_seconds"]
                        while not (directory / "done.json").exists():
                            if backend.now() >= deadline:
                                raise TimeoutError(action["label"])
                            backend.sleep(.5)
                        done = json.loads((directory / "done.json").read_text())
                        cell_record = json.loads((directory / "cell.json").read_text())
                        bad = bool(done.get("interrupted") or cell_record.get("interrupted"))
                        reason = "interrupted" if bad else None
                        if done.get("ok") and not bad:
                            try:
                                run_records = [bundle_evidence(Path(run["bundle"]), pending_reference)
                                               for run in cell_record.get("runs", [])]
                            except (OSError, ValueError, KeyError, TypeError) as exc:
                                log(event="bundle_read_error", label=action["label"], error=str(exc))
                                run_records = []
                            if len(run_records) != config["runs_per_cell"][stage] or any(not run["valid"] for run in run_records):
                                bad, reason = True, "bundle_invalid"
                            elif len({run["output_hash"] for run in run_records}) != 1:
                                bad, reason = True, "bundle_invalid"
                            elif pending_reference is None and not block["discard"]:
                                pending_reference = run_records[0]["output_hash"]
                        elif not done.get("ok") and not bad:
                            bad, reason = True, "bundle_invalid"
                        if bad and reason == "bundle_invalid":
                            invalid_cells[action["context"]] += 1
                            if invalid_cells[action["context"]] >= 3:
                                for discarded_action in actions:
                                    write_json(Path(discarded_action["cell_dir"]) / "discarded.json",
                                               {"reason": "bundle_invalid" if discarded_action["label"] == action["label"] else "block_peer_discard",
                                                "trigger": action["label"], "block": block["id"], "attempt": attempt})
                                log(event="stage_stopped", reason="arm_invalid_cell_limit",
                                    arm=action["context"], invalid_cells=3, council_review_required=True)
                                block_record("block_discarded", block, attempt, actions, stage_reference,
                                             reason="arm_invalid_cell_limit", trigger=action["label"])
                                raise RuntimeError(f"stage stopped: 3 invalid cells in {action['context']}; council review required")
                        log(event="cell_end", label=action["label"], interrupted=bad,
                            reason=reason, ok=done.get("ok"),
                            invalid_cells=dict(invalid_cells))
                    finally:
                        cleanup(action)
                    if bad:
                        break
                if not bad:
                    stage_reference = pending_reference
                    block_record("block_accepted", block, attempt, actions, stage_reference)
                    break
                failed_label = action["label"]
                for discarded_action in actions:
                    write_json(Path(discarded_action["cell_dir"]) / "discarded.json",
                               {"reason": reason if discarded_action["label"] == failed_label else "block_peer_discard",
                                "trigger": failed_label, "block": block["id"], "attempt": attempt})
                log(event="block_discarded", block=block["id"], attempt=attempt, reason=reason)
                block_record("block_discarded", block, attempt, actions, stage_reference,
                             reason=reason, trigger=failed_label)
                if attempt >= 3:
                    log(event="stage_stopped", reason="block_attempt_limit", block=block["id"], attempts=attempt)
                    raise RuntimeError(f"stage stopped: block {block['id']} failed three times")
                attempt = retry_block(block, attempt)["attempt"]
        log(event="stage_done", stage=stage)
    finally:
        for signum in old_handlers:
            signal.signal(signum, signal.SIG_IGN)
        errors = []
        try:
            with Critical():
                for action, _ in list(ownership.values()):
                    try:
                        cleanup(action)
                    except Exception as exc:
                        errors.append(str(exc))
                if stage == "S":
                    try:
                        if backend.display() == "asleep":
                            transition(backend, "on", config, log)
                    except Exception as exc:
                        errors.append(str(exc))
        finally:
            for signum, handler in old_handlers.items():
                signal.signal(signum, handler)
        if errors:
            raise RuntimeError("cleanup failed: " + "; ".join(errors))


def execute(out: Path, config_path: Path, config: dict, stage: str, python: str,
            *, backend=None, existing_actions=None, extra_allow_pids=None,
            manage_network=True, ownership_path=None) -> None:
    backend = backend or SystemBackend()
    if unreleased((ownership_path or out / "owned.jsonl").parent, allow_active_network=not manage_network):
        raise RuntimeError(f"unreleased ownership; run --recover {(ownership_path or out / 'owned.jsonl').parent}")
    def body():
        return _execute_cells(out, config_path, config, stage, python, backend=backend,
                              existing_actions=existing_actions, extra_allow_pids=extra_allow_pids,
                              ownership_path=ownership_path)
    if not manage_network:
        return body()
    def log(**record):
        with (out / "events.jsonl").open("a") as stream:
            stream.write(json.dumps({"wall_ns": time.time_ns(), **record}) + "\n")
    old_handlers = {}
    if isinstance(backend, SystemBackend):
        def interrupted_signal(signum, frame):
            raise KeyboardInterrupt(f"signal {signum}")
        for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
            old_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, interrupted_signal)
    try:
        return with_network_time(backend, log, body, ownership_path=ownership_path or out / "owned.jsonl")
    finally:
        for signum, handler in old_handlers.items():
            signal.signal(signum, handler)


def freeze_rule(spread: dict, config: dict) -> dict:
    """Preregistered cheapest eligible U size, using the SH/I D/I proxy."""
    candidates = []
    power_cache = {}
    for block_count in (6, 12):
        for runs in (1, 2):
            sd = u_replication_spread(spread, runs, config["runs_per_cell"]["stage0U"])
            power = {}
            for endpoint in ("E", "R"):
                if sd[endpoint] is None or not math.isfinite(sd[endpoint]) or sd[endpoint] < 0:
                    raise ValueError(f"invalid stage0U paired SD for {endpoint}")
                key = (sd[endpoint], block_count)
                if key not in power_cache:
                    power_cache[key] = equivalence_power(1.5 * sd[endpoint], block_count)
                for contrast in ("D/I", "SH/I"):
                    power[f"{contrast}:{endpoint}"] = power_cache[key]
            cell_minutes = 3.8 if runs == 1 else 6.0
            wall = (3 * block_count + config["sizes"]["background_cells"] +
                    config["sizes"]["u_warmup_cells"]) * cell_minutes
            candidates.append({"blocks": block_count, "runs_per_cell": runs,
                               "estimated_wall_minutes": wall, "power_at_1p5_sd": power,
                               "within_budget": wall <= 180,
                               "powered": all(value >= .80 for value in power.values())})
    candidates.sort(key=lambda item: item["estimated_wall_minutes"])
    selected = next((item for item in candidates if item["within_budget"] and item["powered"]), None)
    reason = "cheapest_powered_within_budget"
    if selected is None:
        selected = next(item for item in candidates if (item["blocks"], item["runs_per_cell"]) == (12, 1))
        reason = "underpowered_by_prereg"
    return {"total_u_blocks": selected["blocks"], "runs_per_cell": selected["runs_per_cell"],
            "estimated_wall_minutes": selected["estimated_wall_minutes"],
            "power_at_1p5_sd": selected["power_at_1p5_sd"], "reason": reason,
            "candidates": candidates, "D_I_sd_proxy": "SH/I stage0U paired spread"}


def run_session(out: Path, config_path: Path, config: dict, python: str, *, backend=None,
                extra_allow_pids=None):
    backend = backend or SystemBackend()
    out.mkdir(parents=True, exist_ok=True)
    if unreleased(out):
        raise RuntimeError(f"unreleased ownership; run --recover {out}")
    session_path = out / "session.json"
    if session_path.exists() or (out / "freeze.json").exists():
        raise FileExistsError("session or freeze already exists; session cannot overwrite a prior freeze")
    session = {"session": "U", "status": "running", "steps": [], "reason": None}
    write_json(session_path, session)
    def log(**record):
        with (out / "events.jsonl").open("a") as stream:
            stream.write(json.dumps({"wall_ns": time.time_ns(), **record}) + "\n")
    def step(name, fn):
        record = {"step": name, "start_wall_ns": time.time_ns(), "end_wall_ns": None,
                  "outcome": "running", "reason": None}
        session["steps"].append(record)
        write_json(session_path, session)
        try:
            result = fn()
            record["outcome"] = "complete"
            return result
        except BaseException as exc:
            record["outcome"] = "stopped"
            record["reason"] = f"{type(exc).__name__}: {exc}"
            session["status"] = "stopped"
            session["reason"] = record["reason"]
            raise
        finally:
            record["end_wall_ns"] = time.time_ns()
            write_json(session_path, session)
    def stage(name, active_config, active_path):
        directory = out / name
        actions = plan(directory, active_path, active_config, name, python)
        execute(directory, active_path, active_config, name, python, backend=backend,
                existing_actions=actions, extra_allow_pids=extra_allow_pids, manage_network=False,
                ownership_path=out / "owned.jsonl")
        report = analyze_directory(directory, active_config)
        if report["errors"]:
            raise RuntimeError(f"{name} analysis errors: {report['errors']}")
        return report
    def body():
        stage0 = step("stage0U", lambda: stage("stage0U", config, config_path))
        def power_step():
            spread = stage0_spread(stage0["cells"])
            if any(spread["paired_block_count_by_endpoint"][e] != config["sizes"]["stage0_blocks"] or
                   spread["between_cell_paired_sd_log"][e] is None or spread["within_run_sd_log"][e] is None
                   for e in ("E", "R")):
                raise RuntimeError("stage0U has insufficient valid paired data for sizing")
            sizing = freeze_rule(spread, config)
            table = []
            for runs in (1, 2):
                sd = u_replication_spread(spread, runs, config["runs_per_cell"]["stage0U"])
                estimates = {contrast: sd for contrast in ("D/I", "SH/I")}
                table.extend(power_table(estimates, None, (6, 12), runs_per_cell_u=runs))
            write_json(out / "power.json", {"spread": spread, "table": table,
                                            "candidates": sizing["candidates"]})
            return sizing
        sizing = step("analyze_power", power_step)
        def freeze_step():
            frozen = json.loads(json.dumps(config))
            frozen["sizes"]["u_blocks"] = 6
            frozen["runs_per_cell"]["U1"] = frozen["runs_per_cell"]["U2"] = sizing["runs_per_cell"]
            with (out / "freeze.json").open("x") as stream:
                json.dump(sizing, stream, indent=2, sort_keys=True)
                stream.write("\n")
            write_json(out / "frozen_config.json", frozen)
            return frozen
        frozen = step("freeze", freeze_step)
        frozen_path = out / "frozen_config.json"
        u1 = step("U1", lambda: stage("U1", frozen, frozen_path))
        if sizing["total_u_blocks"] == 12 or any(value.startswith("INCONCLUSIVE") for value in u1["verdicts"].values()):
            step("U2", lambda: stage("U2", frozen, frozen_path))
        else:
            record = {"step": "U2", "start_wall_ns": time.time_ns(), "end_wall_ns": time.time_ns(),
                      "outcome": "skipped", "reason": "six_block_freeze_and_U1_conclusive"}
            session["steps"].append(record)
            write_json(session_path, session)
        step("S", lambda: stage("S", frozen, frozen_path))
        def final_analysis():
            report = analyze_directory(out, frozen)
            if report["errors"]:
                raise RuntimeError(f"final analysis errors: {report['errors']}")
            return report
        step("final_analyze", final_analysis)
        session["status"] = "complete"
        write_json(session_path, session)
    old_handlers = {}
    if isinstance(backend, SystemBackend):
        def interrupted_signal(signum, frame):
            raise KeyboardInterrupt(f"signal {signum}")
        for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
            old_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, interrupted_signal)
    try:
        return with_network_time(backend, log, body, ownership_path=out / "owned.jsonl")
    except BaseException as exc:
        session["status"] = "stopped"
        reason = f"{type(exc).__name__}: {exc}"
        session["reason"] = reason if session["reason"] is None else (
            session["reason"] if session["reason"] == reason else session["reason"] + "; " + reason)
        write_json(session_path, session)
        raise
    finally:
        for signum, handler in old_handlers.items():
            signal.signal(signum, handler)


def recover(out: Path, *, backend=None):
    """Replay recorded process ownership, then restore network time."""
    backend = backend or SystemBackend()
    paths = [out / "owned.jsonl"] + sorted(out.glob("*/owned.jsonl"))
    paths = [path for path in paths if path.exists()]
    def log(**record):
        ledger.append(out / "recovery.jsonl", record)
    errors = []
    network_owners = []
    with Critical():
        for path in paths:
            for label, record in list(ledger.owned(path).items()):
                action = record["action"]
                if action["context"] == "NETWORK_TIME":
                    network_owners.append((path, label))
                    continue
                try:
                    if action["context"] == "SH":
                        pid = record.get("pid")
                        if pid is None:
                            # The spawn may have completed before its PID update was durable.
                            literal_dir = re.sub(r"([\\.^$*+?{}\[\]()|])", r"\\\1", action["cell_dir"])
                            pattern = (r"^[^[:space:]]+[[:space:]]+[^[:space:]]*/osctx_mvp/cell\.py"
                                       r"[[:space:]]+--out[[:space:]]+" + literal_dir + r"([[:space:]]|$)")
                            found = bounded_run(backend, ["/usr/bin/pgrep", "-f", pattern])
                            if found.returncode not in (0, 1):
                                raise RuntimeError(f"SH recovery lookup failed: {label}")
                            groups = set()
                            for member in found.stdout.split():
                                group = bounded_run(backend, ["/bin/ps", "-p", member, "-o", "pgid="])
                                if group.returncode or not group.stdout.strip().isdigit():
                                    raise RuntimeError(f"SH recovery PGID unavailable: {label}/{member}")
                                groups.add(int(group.stdout.strip()))
                            for group in groups:
                                backend.stop_shell_group(group)
                        else:
                            backend.stop_shell_group(pid)
                    else:
                        prove_bootout(backend, action, record.get("proof"), log)
                    ledger.append(path, {"event": "release", "label": label})
                except Exception as exc:
                    errors.append(str(exc))
        try:
            result = bounded_run(backend, NETWORK_TIME + ["on"])
            log(event="network_time", argv=NETWORK_TIME + ["on"], returncode=result.returncode,
                stderr=result.stderr)
            if result.returncode:
                errors.append(f"network time on failed: {result.stderr}")
            else:
                for path, label in network_owners:
                    ledger.append(path, {"event": "release", "label": label})
        except Exception as exc:
            errors.append(f"network time on failed: {exc}")
    if errors:
        raise RuntimeError("recovery failed: " + "; ".join(errors))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--render-only", type=Path)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--recover", type=Path)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--stage", choices=("stage0", "stage0U", "U1", "U2", "S", "rehearsal"))
    scope.add_argument("--session", choices=("U",))
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--u1-summary", type=Path)
    parser.add_argument("--allow-pid", action="append", type=int, default=[])
    args = parser.parse_args(argv)
    if args.recover:
        if args.stage or args.session:
            parser.error("--recover takes no stage or session")
        recover(args.recover.resolve())
        return 0
    if not (args.stage or args.session):
        parser.error("--stage or --session is required")
    config = load_config(args.config)
    out = (args.render_only or args.out).resolve()
    if args.session:
        if args.render_only:
            for name in ("stage0U", "U1", "U2", "S"):
                plan(out / name, args.config.resolve(), config, name, args.python)
            write_json(out / "session_plan.json", {"session": "U", "stages": ["stage0U", "U1", "U2", "S"],
                                                  "network_time": [NETWORK_TIME + ["off"], NETWORK_TIME + ["on"]],
                                                  "sequence": ["network_time_off", "stage0U",
                                                               "analyze_power", "freeze_json", "U1",
                                                               "U2_if_twelve_blocks_or_U1_inconclusive",
                                                               "S", "final_analyze", "network_time_on"],
                                                  "U1_U2_templates": "provisional; live session re-renders after freeze"})
            return 0
        run_session(out, args.config.resolve(), config, args.python, extra_allow_pids=args.allow_pid)
        return 0
    if args.stage == "U2" and args.out:
        if not args.u1_summary:
            parser.error("U2 execution requires --u1-summary")
        summary = json.loads(args.u1_summary.read_text())
        verdicts = summary["verdicts"]
        if summary.get("stage") != "U1" or summary.get("errors"):
            parser.error("U2 requires a clean U1 analysis")
        expected_blocks = {block["id"] for block in blocks(config, "U1") if len(block["arms"]) == 3}
        observed = {block_id: {row["context"] for row in summary["cells"] if row["block"] == block_id}
                    for block_id in expected_blocks}
        if any(arms != {"D", "I", "SH"} for arms in observed.values()):
            parser.error("U2 requires six complete U1 Williams blocks")
        freeze_path = out.parent / "freeze.json"
        frozen_twelve = freeze_path.is_file() and json.loads(freeze_path.read_text()).get("total_u_blocks") == 12
        if not frozen_twelve and not any(value.startswith("INCONCLUSIVE") for value in verdicts.values()):
            parser.error("U2 runs only after an INCONCLUSIVE U1 verdict")
    actions = plan(out, args.config.resolve(), config, args.stage, args.python)
    if args.out:
        execute(out, args.config.resolve(), config, args.stage, args.python,
                existing_actions=actions, extra_allow_pids=args.allow_pid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
