"""Render and run balanced OSCTX blocks. Live execution belongs to the lead."""
from __future__ import annotations

import argparse
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

try:
    from .common import blocks, load_config, write_json
    from .cell import display_state, hid_idle_seconds
    from .analyze import bundle_evidence
except ImportError:
    from common import blocks, load_config, write_json
    from cell import display_state, hid_idle_seconds
    from analyze import bundle_evidence

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
                         "gate": "HIDIdleTime >= 600 s" if block["state"] == "U" and stage != "stage0" else None,
                         "starts": [a["start"] for a in actions if a["block"] == block["id"]],
                         "interrupted": "discard entire block and retry in same order"})
    write_json(out / "command_sequence.json", {"stage": stage, "seed": config["seed"], "actions": actions,
                                                    "sequence": sequence})
    return actions


class SystemBackend:
    """Small live boundary; offline tests inject a fake in its place."""
    def run(self, argv):
        return subprocess.run(argv, capture_output=True, text=True, check=False)

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
        # macOS returns EPERM from killpg when the group holds only exited
        # (zombie) members, so a finished SH cell is reaped first and any
        # survivor is proven by pgrep over the process group, not by killpg.
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                pass
        process.wait(timeout=15)
        survivors = subprocess.run(["/usr/bin/pgrep", "-g", str(process.pid)],
                                   capture_output=True, text=True, check=False)
        if survivors.returncode == 1 and not survivors.stdout.strip():
            return
        raise RuntimeError(f"shell process-group survivor {process.pid}: {survivors.stdout.strip()}")


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
    before = backend.run(["/usr/bin/pmset", "-g", "log"])
    if before.returncode:
        raise RuntimeError("display transition log unreadable before request")
    argv = ["/usr/bin/pmset", "displaysleepnow"] if target == "asleep" else ["/usr/bin/caffeinate", "-u", "-t", "1"]
    result = backend.run(argv)
    if result.returncode:
        raise RuntimeError(f"display transition failed: {argv}")
    deadline = backend.now() + 30
    unknown_polls = 0
    while True:
        after = backend.run(["/usr/bin/pmset", "-g", "log"])
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


def execute(out: Path, config_path: Path, config: dict, stage: str, python: str,
            *, backend=None, existing_actions=None, extra_allow_pids=None) -> None:
    backend = backend or SystemBackend()
    ownership: dict[str, tuple[dict, object | None]] = {}
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
        owned = ownership.pop(action["label"], None)
        if owned is None:
            return
        _, process = owned
        if action["context"] == "SH":
            backend.stop_shell(process)
        else:
            result = backend.run(action["stop"])
            registered = backend.run(["/bin/launchctl", "print", f"gui/{os.getuid()}/{action['label']}"])
            survivor = backend.run(["/usr/bin/pgrep", "-f", re.escape(action["cell_dir"])])
            if registered.returncode == 0:
                raise RuntimeError(f"launchd job survived bootout: {action['label']}")
            if survivor.returncode != 1:
                raise RuntimeError(f"launchd survivor or pgrep error: {action['label']}")
            if result.returncode:
                log(event="bootout_unneeded_or_failed", label=action["label"], returncode=result.returncode)
        log(event="cleanup_proved", label=action["label"])
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
                        if action["context"] == "SH":
                            process = backend.spawn_shell(action["start"], directory)
                        else:
                            ownership[action["label"]] = action, None
                            result = backend.run(action["start"])
                            if result.returncode:
                                raise RuntimeError(f"bootstrap failed: {action['label']}")
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
                    break
                failed_label = action["label"]
                for discarded_action in actions:
                    write_json(Path(discarded_action["cell_dir"]) / "discarded.json",
                               {"reason": reason if discarded_action["label"] == failed_label else "block_peer_discard",
                                "trigger": failed_label, "block": block["id"], "attempt": attempt})
                log(event="block_discarded", block=block["id"], attempt=attempt, reason=reason)
                if attempt >= 3:
                    log(event="stage_stopped", reason="block_attempt_limit", block=block["id"], attempts=attempt)
                    raise RuntimeError(f"stage stopped: block {block['id']} failed three times")
                attempt = retry_block(block, attempt)["attempt"]
        log(event="stage_done", stage=stage)
    finally:
        for signum in old_handlers:
            signal.signal(signum, signal.SIG_IGN)
        errors = []
        for action, _ in list(ownership.values()):
            try:
                cleanup(action)
            except Exception as exc:
                errors.append(str(exc))
        if stage == "S" and backend.display() == "asleep":
            try:
                transition(backend, "on", config, log)
            except Exception as exc:
                errors.append(str(exc))
        for signum, handler in old_handlers.items():
            signal.signal(signum, handler)
        if errors:
            raise RuntimeError("cleanup failed: " + "; ".join(errors))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--render-only", type=Path)
    mode.add_argument("--out", type=Path)
    parser.add_argument("--stage", choices=("stage0", "U1", "U2", "S"), required=True)
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--u1-summary", type=Path)
    parser.add_argument("--allow-pid", action="append", type=int, default=[])
    args = parser.parse_args(argv)
    config = load_config(args.config)
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
        if not any(value.startswith("INCONCLUSIVE") for value in verdicts.values()):
            parser.error("U2 runs only after an INCONCLUSIVE U1 verdict")
    out = (args.render_only or args.out).resolve()
    actions = plan(out, args.config.resolve(), config, args.stage, args.python)
    if args.out:
        execute(out, args.config.resolve(), config, args.stage, args.python,
                existing_actions=actions, extra_allow_pids=args.allow_pid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
