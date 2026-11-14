#!/usr/bin/env python3
"""Hand one conditionless-campaign span (runner kind ``cadence-legs-v1``) to a one-shot LaunchAgent.

    python3.13 -B scripts/launch_cadence_span.py launch --repo R --python-bin PY --kit KIT \\
        [--legs L001,L002,L003] --batch-window 02:00-02:35 --output OUT --disk-path R \\
        --custody-root C --magistrate-pid PID --deadline EPOCH

The campaign launcher of RL-149 section 5 item 6. It is the R0/R1 desk launcher's
procedure (``launch_align_r0.py``): the same desk fence, the same LaunchAgent wrapper
(``run_align_r0_launchagent.sh``: handoff, preflight, Spotlight pause, run, clear),
the same agent-free shape as ``--runner-kind r1-smoke`` (the runner starts its own
feeds, display sleep and dwell), ``ProcessType Interactive`` and the same exit
timeout. It reuses that module's functions by import and never changes it.

**Why a separate entry.** ``launch_align_r0.py`` is in the W1 registration's executed
closure (``magistrate_watchdog.py`` imports it). Registering the campaign kind there
would pull the campaign runner, its library and the R1 soak path into W1's receipt
closure. This module is imported by nothing on a W1, R1 or HAZARD_PACK path, so the
campaign stays outside every v4 registration.

The wrapper calls this file back with ``handoff``, ``preflight``, ``run`` and ``clear``.
``handoff``, ``preflight`` and ``clear`` are ``launch_align_r0``'s own; ``run`` is the
agent-free run of ``launch_align_r0.run_until_deadline`` for this runner kind.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import plistlib
import re
import signal
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import launch_align_r0 as base  # noqa: E402

RUNNER_KIND = "cadence-legs-v1"
LEG_IDS_PATTERN = re.compile(r"L\d{3,4}(?:,L\d{3,4})*")
BATCH_WINDOW_PATTERN = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d-(?:[01]\d|2[0-3]):[0-5]\d")
RUNNER = "scripts/cadence_legs_runner.py"


def cadence_plan(kit: Path, legs: str | None = None, batch_window: str | None = None,
                 t0: float | None = None) -> dict:
    """The campaign runner's plan for this span (kit roster and template; no host contact)."""
    from joulewise.cadence import kit as kitmod, legs as legsmod
    from scripts import cadence_legs_runner as runner

    loaded, _sha = kitmod.load_kit(kit)
    if loaded["runner"]["kind"] != RUNNER_KIND:
        raise ValueError(f"kit runner.kind is not {RUNNER_KIND}")
    windows = [legsmod.parse_window(batch_window)] if batch_window else runner.default_windows()
    return legsmod.plan_span(loaded, t0_epoch=time.time() if t0 is None else t0, windows=windows,
                             leg_ids=legs.split(",") if legs else None, max_span_s=runner.max_span_s())


def cadence_minimum_seconds(plan: dict) -> float:
    """The span's worst case plus the runner's work reserve and the launcher's cleanup grace."""
    from scripts import cadence_legs_runner as runner
    return runner.launch_deadline(plan) - plan["t0_epoch_s"]


def runner_argv(args) -> list[str]:
    legs, window = getattr(args, "legs", None), getattr(args, "batch_window", None)
    return [str(args.python_bin), str(args.repo / RUNNER), "run", "--kit", str(args.kit), "--output", str(args.output),
            *(["--legs", legs] if legs else []), *(["--batch-window", window] if window else []),
            "--deadline", str(args.deadline), "--pmset-bin", str(args.pmset_bin)]


def launch(args) -> None:
    """``launch_align_r0.launch`` for this runner kind: refuse, publish the fence, bootstrap once."""
    if (args.magistrate_pid <= 1 or not base.pid_alive(args.magistrate_pid)
            or not math.isfinite(args.deadline) or args.deadline <= time.time()):
        raise ValueError("live magistrate PID and future finite epoch deadline required")
    if args.deadline > time.time() + base.MAX_DESK_SECONDS:
        raise ValueError(f"desk deadline is more than {base.MAX_DESK_SECONDS} s ahead")
    if args.output.exists():
        raise ValueError("campaign output must be a new record directory")
    if args.kit is None or not args.kit.is_file():
        raise ValueError("cadence-legs-v1 requires an existing --kit")
    if args.legs is not None and not LEG_IDS_PATTERN.fullmatch(args.legs):
        raise ValueError("--legs must be comma-separated kit leg ids (L001,L002,...)")
    if args.batch_window is not None and not BATCH_WINDOW_PATTERN.fullmatch(args.batch_window):
        raise ValueError("--batch-window must be HH:MM-HH:MM")
    plan = cadence_plan(args.kit, args.legs, args.batch_window)
    if args.deadline - time.time() < cadence_minimum_seconds(plan):
        raise ValueError("cadence-legs-v1 deadline cannot fit the span's worst case, work reserve and cleanup grace")
    runner = Path(runner_argv(args)[1])
    if not runner.is_file() or not os.access(args.python_bin, os.X_OK):
        raise ValueError("measurement checkout runner and executable interpreter required")
    root = args.custody_root
    root.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    purpose = f"align-r0:{token}"
    label = f"com.joulewise.align-r0.{token}"
    domain = f"gui/{os.getuid()}"
    job = root / "r0-launches" / token
    job.mkdir(parents=True)
    plist = job / f"{label}.plist"
    wrapper = Path(base.__file__).with_name("run_align_r0_launchagent.sh").resolve()
    runner_spec = job / "runner.json"
    runner_spec.write_text(json.dumps({"kind": RUNNER_KIND, "argv": runner_argv(args)}) + "\n")
    arguments = ["/bin/bash", str(wrapper), str(Path(__file__).resolve()),
                 str(args.python_bin), str(root), purpose, str(args.magistrate_pid),
                 str(args.deadline), str(args.exit_wait_seconds), args.pmset_bin,
                 str(args.disk_path), args.pgrep_bin, args.kill_bin, str(runner_spec),
                 args.launchctl_bin, f"{domain}/{label}"]
    job_spec = {
        "Label": label, "ProgramArguments": arguments, "RunAtLoad": True,
        "WorkingDirectory": str(args.repo),
        "EnvironmentVariables": {"PATH": "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin", "LC_ALL": "C"},
        "StandardOutPath": str(job / "stdout.log"), "StandardErrorPath": str(job / "stderr.log"),
        # As r1-smoke: cover the runner's teardown plus the outer helper's TERM grace, and run
        # Interactive like the night templates (RUN_STATE 274).
        "ExitTimeOut": 2 * base.R1_CLEANUP_GRACE_S + 40, "ProcessType": "Interactive",
    }
    plist.write_bytes(plistlib.dumps(job_spec))
    with base.fence_lock(root):
        current = base.read_fence(root)
        if current and current["deadline"] > time.time() and base.pid_alive(current["pid"]):
            raise ValueError("an active desk fence already exists")
        base.write_fence(root, {"purpose": purpose, "pid": args.magistrate_pid, "deadline": args.deadline})
    try:
        subprocess.run([args.launchctl_bin, "bootstrap", domain, str(plist)], check=True, timeout=30)
        until = time.monotonic() + args.start_wait_seconds
        while time.monotonic() < until:
            with base.fence_lock(root):
                current = base.read_fence(root)
            if (current and current["purpose"] == purpose and current["pid"] != args.magistrate_pid
                    and base.pid_alive(current["pid"])):
                print(json.dumps({"label": label, "plist": str(plist), "fence": current,
                                  "plan": {k: plan[k] for k in ("worst_case_s", "expected_s", "batch_windows")},
                                  "next": "exit the magistrate session now"}), flush=True)
                return
            time.sleep(0.1)
        raise TimeoutError("LaunchAgent did not claim the desk fence")
    except BaseException:
        stopped = subprocess.run([args.launchctl_bin, "bootout", f"{domain}/{label}"],
                                 capture_output=True, timeout=30)
        if stopped.returncode == 0 or (stopped.returncode == 113 and
                                       b"could not find service" in stopped.stderr.lower()):
            base.clear_owned(root, purpose)
        raise


def run_until_deadline(args) -> int:
    """The agent-free run of ``launch_align_r0.run_until_deadline`` (its r1-smoke branch) for this
    runner kind: the runner starts its own feeds before display sleep and dwell."""
    remaining = args.deadline - time.time() - 10
    if remaining <= 0:
        raise TimeoutError("campaign desk deadline already passed")
    runner = json.loads(args.runner_spec.read_text())
    if not (isinstance(runner, dict) and runner.get("kind") == RUNNER_KIND):
        raise ValueError(f"runner spec is not a {RUNNER_KIND} spec")
    child = None

    def interrupted(signum, _frame):
        raise SystemExit(128 + signum)

    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(signum, interrupted)
    try:
        remaining = args.deadline - time.time() - base.R1_CLEANUP_GRACE_S - 10
        child = subprocess.Popen(runner["argv"], env=os.environ.copy())
        return child.wait(timeout=max(0, remaining))
    finally:
        for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            signal.signal(signum, signal.SIG_IGN)
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=base.R1_CLEANUP_GRACE_S)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] in (["handoff"], ["preflight"], ["clear"]):
        return base.main(argv)               # the desk launcher's own fence and host steps
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("launch", help="magistrate: publish fence, bootstrap once, then exit session")
    start.add_argument("--repo", type=Path, required=True)
    start.add_argument("--kit", type=Path, required=True, help="the frozen campaign kit (RL-149 section 2)")
    start.add_argument("--legs", help="the queue span's roster, comma-separated kit leg ids")
    start.add_argument("--batch-window", help="HH:MM-HH:MM blackout (RL-149 section 2.9 item 4)")
    start.add_argument("--output", type=Path, required=True)
    start.add_argument("--python-bin", type=Path, required=True)
    start.add_argument("--disk-path", type=Path, required=True)
    start.add_argument("--custody-root", type=Path, required=True)
    start.add_argument("--magistrate-pid", type=int, required=True)
    start.add_argument("--deadline", type=float, required=True)
    start.add_argument("--launchctl-bin", default="/bin/launchctl")
    start.add_argument("--pmset-bin", default="/usr/bin/pmset")
    start.add_argument("--pgrep-bin", default="/usr/bin/pgrep")
    start.add_argument("--kill-bin", default="/bin/kill")
    start.add_argument("--start-wait-seconds", type=base.positive_seconds, default=30)
    start.add_argument("--exit-wait-seconds", type=base.positive_seconds, default=180)
    run = sub.add_parser("run")
    run.add_argument("--deadline", type=float, required=True)
    run.add_argument("--runner-spec", type=Path, required=True)
    run.add_argument("--pmset-bin", default="/usr/bin/pmset")
    args = parser.parse_args(argv)
    for name in ("repo", "kit", "output", "disk_path", "custody_root"):
        if getattr(args, name, None) is not None:
            setattr(args, name, getattr(args, name).expanduser().resolve())
    if hasattr(args, "python_bin"):
        args.python_bin = Path(os.path.abspath(args.python_bin.expanduser()))   # not symlink-resolved (venv)
    try:
        if args.command == "launch":
            launch(args)
            return 0
        return run_until_deadline(args)
    except (OSError, ValueError, subprocess.SubprocessError, TimeoutError) as exc:
        print(f"campaign launch refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
