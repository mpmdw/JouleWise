#!/usr/bin/env python3
"""Hand R0 to a one-shot LaunchAgent; never run a measurement in an agent tree."""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import math
import os
from pathlib import Path
import plistlib
import re
import signal
import stat
import subprocess
import sys
import time
import uuid


FENCE_NAME = "desk_fence.json"
# R0 is planned at ~3-6.5 h. The deadline bounds both the runner and the
# watchdog fence; a cap stops a unit slip (ms for s) or a typo from fencing
# the magistrate for days if the job hangs or its PID is reused.
MAX_DESK_SECONDS = 12 * 3600
# R0-L3 item 3: a comma list of runner check names (the runner validates
# the names themselves); nothing else may reach the runner's argv.
CHECKS_PATTERN = re.compile(r"[a-z][a-z-]*(?:,[a-z][a-z-]*)*")
# R0-L3 display ruling (RUN_STATE 206): with the display on, menu-bar redraws
# every 3-4 min wake WindowServer and ControlCenter and trip the census. The
# launcher sleeps the display (no sudo) and dwells this long before the
# runner's first census-checked segment.
DISPLAY_SLEEP_DWELL_S = 300
# Test seam only: the LaunchAgent harness cannot wait 300 s. Never set it for
# a real run; the record carries both the dwell used and the constant.
DISPLAY_DWELL_TEST_ENV = "JOULEWISE_R0_TEST_DISPLAY_DWELL_S"
DISPLAY_PREP_ENV = "JOULEWISE_R0_DISPLAY_PREP"
# R1 has two separately owned groups (part and meter) and an Automatic
# restore. Leave the fence up while their ordinary teardown proves absence.
R1_CLEANUP_GRACE_S = 180
# RL-149 section 5 item 6: the conditionless calibration campaign's span runner
# (scripts/cadence_legs_runner.py). Like r1-smoke it is agent-free: it starts
# its own feeds, display sleep and dwell, and owns an Automatic restore.
CADENCE_RUNNER_KIND = "cadence-legs-v1"
AGENT_FREE_RUNNER_KINDS = ("r1-smoke", CADENCE_RUNNER_KIND)
LEG_IDS_PATTERN = re.compile(r"L\d{3,4}(?:,L\d{3,4})*")
BATCH_WINDOW_PATTERN = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d-(?:[01]\d|2[0-3]):[0-5]\d")


def r1_part_caps() -> dict[str, float]:
    """Read the kit's bound config; never load weights or measurement data."""
    repo = Path(__file__).resolve().parents[1]
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from joulewise.align.apple import r1_runtime as rt

    config = json.loads((repo / "configs/align/v4/r1_runtime.json").read_text())
    post_g0 = rt.smoke_post_g0_budget(rt.STEP_QUIET_S, config["step"]["deadman_s"])["total"]
    # The kit starts its own admission clock AFTER its source/config checks.
    # Keep 120 s outside that admission verdict (rt.SMOKE_ADMISSION_S, RUN_STATE
    # 276) for startup and final table work.
    return {"A": rt.SMOKE_ADMISSION_S + 120, "B": rt.SMOKE_ADMISSION_S + post_g0 + 120}


def r1_part_c_cap_s() -> float:
    """RL-145 addendum Part C: Part B's span (the 30B predecessor and a full step-D), then the gated
    D_bank member and X_G, each bounded by the runtime's member cap, plus 120 s each for start-up
    and the result writes."""
    repo = Path(__file__).resolve().parents[1]
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from joulewise.align.apple import r1_runtime as rt

    return r1_part_caps()["B"] + 2 * (rt.MEMBER_CAP_S + 120)


def r1_soak_cap_s() -> float:
    """RL-94 fresh soak: the night's idle_soak duration plus the runtime's
    own 30 s child margin and 120 s for start-up and the reference write."""
    repo = Path(__file__).resolve().parents[1]
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from joulewise.align.apple.r1_phase_table import phase_plan

    return float(next(d for name, _kind, d, _c in phase_plan() if name == "idle_soak")) + 30 + 120


def r1_minimum_seconds(parts: str = "AB", fresh_soak: bool = False) -> float:
    caps = {**r1_part_caps(), "C": r1_part_c_cap_s() if "C" in parts else 0}
    return (sum(caps[p] for p in parts) + (r1_soak_cap_s() if fresh_soak else 0)
            + DISPLAY_SLEEP_DWELL_S + 2 * R1_CLEANUP_GRACE_S + 10)


def cadence_plan(kit: Path, legs: str | None = None, batch_window: str | None = None,
                 t0: float | None = None) -> dict:
    """The campaign runner's plan for this span (kit roster and template; no host contact)."""
    repo = Path(__file__).resolve().parents[1]
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from joulewise.cadence import kit as kitmod, legs as legsmod
    from scripts import cadence_legs_runner as runner

    loaded, _sha = kitmod.load_kit(kit)
    if loaded["runner"]["kind"] != CADENCE_RUNNER_KIND:
        raise ValueError(f"kit runner.kind is not {CADENCE_RUNNER_KIND}")
    windows = [legsmod.parse_window(batch_window)] if batch_window else runner.default_windows()
    return legsmod.plan_span(loaded, t0_epoch=time.time() if t0 is None else t0, windows=windows,
                             leg_ids=legs.split(",") if legs else None, max_span_s=runner.max_span_s())


def cadence_minimum_seconds(plan: dict) -> float:
    """The span's worst case plus the runner's work reserve and this launcher's cleanup grace."""
    from scripts import cadence_legs_runner as runner
    return runner.launch_deadline(plan) - plan["t0_epoch_s"]


def positive_seconds(value: str) -> float:
    seconds = float(value)
    if not math.isfinite(seconds) or seconds <= 0:
        raise argparse.ArgumentTypeError("seconds must be positive and finite")
    return seconds


@contextlib.contextmanager
def fence_lock(root: Path, *, dry_run: bool = False):
    """Serialize stale removal, publication, ownership transfer and cleanup.

    This is separate from watchdog.lock, which a resident holds for its life.
    Callers that publish a new fence must create the custody directory first.
    """
    if dry_run:
        yield
        return
    fd = os.open(root / ".desk-fence.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def read_fence(root: Path) -> dict | None:
    path = root / FENCE_NAME
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None
    with os.fdopen(fd, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ValueError("desk fence must be a regular file")
        raw = handle.read(4097)
        if len(raw) > 4096:
            raise ValueError("desk fence exceeds 4096 bytes")
        record = json.loads(raw)
    if (not isinstance(record, dict) or set(record) != {"purpose", "pid", "deadline"}
            or not isinstance(record["purpose"], str) or not record["purpose"].strip()
            or type(record["pid"]) is not int or record["pid"] <= 1
            or type(record["deadline"]) not in (int, float)
            or not math.isfinite(record["deadline"]) or record["deadline"] <= 0):
        raise ValueError("invalid desk fence: expected purpose, positive pid and finite epoch deadline")
    return record


def write_fence(root: Path, record: dict) -> None:
    temporary = root / f".{FENCE_NAME}.{uuid.uuid4().hex}.tmp"
    fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(record, handle, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, root / FENCE_NAME)
        sync_directory(root)
    finally:
        temporary.unlink(missing_ok=True)


def sync_directory(root: Path) -> None:
    fd = os.open(root, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def clear_owned(root: Path, purpose: str, pid: int | None = None) -> None:
    with fence_lock(root):
        current = read_fence(root)
        if current and current["purpose"] == purpose and (pid is None or current["pid"] == pid):
            (root / FENCE_NAME).unlink()
            sync_directory(root)


def handoff(args) -> None:
    root = args.custody_root
    with fence_lock(root):
        current = read_fence(root)
        expected = {"purpose": args.purpose, "pid": args.magistrate_pid, "deadline": args.deadline}
        if current != expected or time.time() >= args.deadline:
            raise ValueError("desk fence changed or expired before LaunchAgent handoff")
        write_fence(root, {**current, "pid": args.pid})
    # The magistrate must end its session. QuietGuard still performs its full
    # independent agent, custody and installed-night-agent census afterwards.
    until = min(args.deadline, time.time() + args.exit_wait_seconds)
    while pid_alive(args.magistrate_pid):
        if time.time() >= until:
            raise TimeoutError("magistrate did not exit before the handoff timeout")
        time.sleep(0.1)


def preflight(args) -> None:
    import shutil

    result = subprocess.run([args.pmset_bin, "-g", "batt"], check=True,
                            capture_output=True, text=True, timeout=15,
                            env={**os.environ, "LC_ALL": "C"})
    if "Now drawing from 'AC Power'" not in result.stdout.splitlines():
        raise ValueError("R0 requires AC power (pmset -g batt)")
    free = shutil.disk_usage(args.disk_path).free
    # ALIGN v4 ruling 6: the >=80 GB bar belongs to W1, not this engineering desk.
    print(json.dumps({"ac_power": True, "free_bytes": free, "disk_check": "report_only"}), flush=True)


def display_dwell_seconds() -> float:
    override = os.environ.get(DISPLAY_DWELL_TEST_ENV)
    return DISPLAY_SLEEP_DWELL_S if override is None else positive_seconds(override)


def sleep_display(pmset_bin) -> dict:
    """`pmset displaysleepnow` (no sudo). A failure is recorded, never a refusal."""
    record = {"argv": [str(pmset_bin), "displaysleepnow"], "epoch_s": time.time()}
    try:
        result = subprocess.run(record["argv"], capture_output=True, text=True, timeout=15,
                                env={**os.environ, "LC_ALL": "C"})
        record.update(exit_code=result.returncode, stderr=result.stderr.strip())
    except (OSError, subprocess.SubprocessError) as exc:
        record.update(exit_code=None, stderr=f"{type(exc).__name__}: {exc}")
    return record


def run_until_deadline(args) -> int:
    """Bound the runner by the same deadline that releases the watchdog fence."""
    # Leave time to terminate a stuck runner and resume Spotlight before the
    # watchdog's deadline fallback permits another activation.
    remaining = args.deadline - time.time() - 10
    if remaining <= 0:
        raise TimeoutError("R0 desk deadline already passed")
    dwell = display_dwell_seconds()
    if remaining <= dwell:
        raise TimeoutError(f"R0 desk deadline leaves no room for the {dwell:g} s display dwell")
    child = None
    runner = json.loads(args.runner_spec.read_text())
    r1_smoke = isinstance(runner, dict) and runner.get("kind") in AGENT_FREE_RUNNER_KINDS

    def interrupted(signum, _frame):
        raise SystemExit(128 + signum)

    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(signum, interrupted)
    try:
        if r1_smoke:
            # R1 starts its feeds BEFORE display sleep/dwell. The same absolute
            # fence deadline is passed through; both layers reserve cleanup.
            remaining = args.deadline - time.time() - R1_CLEANUP_GRACE_S - 10
            child = subprocess.Popen(runner["argv"], env=os.environ.copy())
            return child.wait(timeout=max(0, remaining))
        # RUN_STATE 206: display off, then dwell, before any census-checked
        # segment. The runner records the display state and any wake.
        prep = {"displaysleepnow": sleep_display(args.pmset_bin), "dwell_s": dwell,
                "dwell_constant_s": DISPLAY_SLEEP_DWELL_S}
        time.sleep(dwell)
        prep["dwell_end_epoch_s"] = time.time()
        print(json.dumps({"display_prep": prep}), flush=True)
        remaining = args.deadline - time.time() - 10
        if remaining <= 0:
            raise TimeoutError("R0 desk deadline passed during the display dwell")
        runner = json.loads(args.runner_spec.read_text())
        child = subprocess.Popen(runner, env={**os.environ, DISPLAY_PREP_ENV: json.dumps(prep)})
        return child.wait(timeout=remaining)
    finally:
        # launchd and the shell may both deliver TERM. Finish reaping before
        # the shell resumes Spotlight and releases its fence.
        for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            signal.signal(signum, signal.SIG_IGN)
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=R1_CLEANUP_GRACE_S if r1_smoke else 5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


def runner_argv(args) -> list[str]:
    if getattr(args, "runner_kind", "r0") == CADENCE_RUNNER_KIND:
        legs, window = getattr(args, "legs", None), getattr(args, "batch_window", None)
        return [str(args.python_bin), str(args.repo / "scripts/cadence_legs_runner.py"), "run",
                "--kit", str(args.kit), "--output", str(args.output),
                *(["--legs", legs] if legs else []), *(["--batch-window", window] if window else []),
                "--deadline", str(args.deadline), "--pmset-bin", str(args.pmset_bin)]
    if getattr(args, "runner_kind", "r0") == "r1-smoke":
        fresh = getattr(args, "fresh_soak", False)
        parts = getattr(args, "parts", "AB")
        return [str(args.python_bin), str(args.repo / "scripts/run_align_r1_smoke.py"),
                "--output", str(args.output),
                *(["--fresh-soak"] if fresh else ["--soak-reference", str(args.soak_reference)]),
                *(["--parts", parts] if parts != "AB" else []),
                "--deadline", str(args.deadline), "--pmset-bin", str(args.pmset_bin)]
    return [str(args.python_bin), str(args.repo / "scripts/align_r0_checks.py"),
            "--config", str(args.config), "--output", str(args.output),
            *(["--checks", args.checks] if args.checks is not None else []),
            *(["--keep-going"] if args.keep_going else [])]


def launch(args) -> None:
    args.runner_kind = getattr(args, "runner_kind", "r0")
    if (args.magistrate_pid <= 1 or not pid_alive(args.magistrate_pid)
            or not math.isfinite(args.deadline) or args.deadline <= time.time()):
        raise ValueError("live magistrate PID and future finite epoch deadline required")
    if args.deadline > time.time() + MAX_DESK_SECONDS:
        raise ValueError(f"desk deadline is more than {MAX_DESK_SECONDS} s ahead")
    if args.output.exists():
        raise ValueError("R0 output must be a new record directory")
    if args.checks is not None and not CHECKS_PATTERN.fullmatch(args.checks):
        raise ValueError("--checks must be comma-separated runner check names")
    fresh = getattr(args, "fresh_soak", False)
    parts = getattr(args, "parts", "AB")
    cadence = args.runner_kind == CADENCE_RUNNER_KIND
    kit, legs, window = getattr(args, "kit", None), getattr(args, "legs", None), getattr(args, "batch_window", None)
    if not cadence and (kit is not None or legs is not None or window is not None):
        raise ValueError("--kit, --legs and --batch-window apply to cadence-legs-v1 only")
    if cadence:
        if kit is None or not kit.is_file():
            raise ValueError("cadence-legs-v1 requires an existing --kit")
        if args.soak_reference is not None:
            raise ValueError("cadence-legs-v1 runs its own fresh soak; no --soak-reference")
        if legs is not None and not LEG_IDS_PATTERN.fullmatch(legs):
            raise ValueError("--legs must be comma-separated kit leg ids (L001,L002,...)")
        if window is not None and not BATCH_WINDOW_PATTERN.fullmatch(window):
            raise ValueError("--batch-window must be HH:MM-HH:MM")
        plan = cadence_plan(kit, legs, window)
        if args.deadline - time.time() < cadence_minimum_seconds(plan):
            raise ValueError("cadence-legs-v1 deadline cannot fit the span's worst case, work reserve and cleanup grace")
    if args.runner_kind != "r1-smoke" and (fresh or parts != "AB"):
        raise ValueError("--fresh-soak and --parts apply to r1-smoke only")
    if parts == "C" and not fresh:
        raise ValueError("--parts C runs on a fresh soak (RL-145 addendum): give --fresh-soak")
    if args.runner_kind == "r1-smoke" and fresh and args.soak_reference is not None:
        raise ValueError("r1-smoke takes --soak-reference or --fresh-soak, not both")
    if args.runner_kind == "r1-smoke" and not fresh and (args.soak_reference is None or not args.soak_reference.is_file()):
        raise ValueError("r1-smoke requires an existing --soak-reference")
    if args.runner_kind == "r1-smoke" and args.deadline - time.time() < r1_minimum_seconds(parts, fresh):
        raise ValueError("r1-smoke deadline cannot fit both part caps, display dwell and cleanup grace")
    runner = Path(runner_argv(args)[1])
    if (not runner.is_file() or not os.access(args.python_bin, os.X_OK)
            or (args.runner_kind == "r0" and (args.config is None or not args.config.is_file()))):
        raise ValueError("measurement checkout runner, config and executable interpreter required")
    root = args.custody_root
    root.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    purpose = f"align-r0:{token}"
    label = f"com.joulewise.align-r0.{token}"
    domain = f"gui/{os.getuid()}"
    job = root / "r0-launches" / token
    job.mkdir(parents=True)
    plist = job / f"{label}.plist"
    wrapper = Path(__file__).with_name("run_align_r0_launchagent.sh").resolve()
    runner_spec = job / "runner.json"
    # R0-L3 item 3: pass a check subset (R0-L1) and --keep-going (the desk
    # default) through; the runner's prerequisite gates still apply.
    spec = runner_argv(args)
    if args.runner_kind in AGENT_FREE_RUNNER_KINDS:
        spec = {"kind": args.runner_kind, "argv": spec}
    runner_spec.write_text(json.dumps(spec) + "\n")
    # Keep the measurement entry-point name out of the launcher ancestors'
    # argv: QuietGuard correctly refuses a second align_r0_checks process.
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
    }
    if args.runner_kind in AGENT_FREE_RUNNER_KINDS:
        # Cover the runner's teardown plus the outer helper's TERM grace.
        job_spec["ExitTimeOut"] = 2 * R1_CLEANUP_GRACE_S + 40
        # The night, dead-man and probe templates run Interactive: the default
        # ProcessType coalesces timers and slows `powermetrics -i 100` to ~240 ms
        # a frame (the 09-19 slow-cadence class), so a 300 s idle capture
        # overruns its 460 s timeout (RUN_STATE 274). The smoke runs as W1 runs.
        job_spec["ProcessType"] = "Interactive"
    plist.write_bytes(plistlib.dumps(job_spec))
    with fence_lock(root):
        current = read_fence(root)
        if current and current["deadline"] > time.time() and pid_alive(current["pid"]):
            raise ValueError("an active desk fence already exists")
        write_fence(root, {"purpose": purpose, "pid": args.magistrate_pid, "deadline": args.deadline})
    try:
        subprocess.run([args.launchctl_bin, "bootstrap", domain, str(plist)], check=True, timeout=30)
        until = time.monotonic() + args.start_wait_seconds
        while time.monotonic() < until:
            with fence_lock(root):
                current = read_fence(root)
            if (current and current["purpose"] == purpose and current["pid"] != args.magistrate_pid
                    and pid_alive(current["pid"])):
                print(json.dumps({"label": label, "plist": str(plist), "fence": current,
                                  "next": "exit the magistrate session now"}), flush=True)
                return
            time.sleep(0.1)
        raise TimeoutError("LaunchAgent did not claim the desk fence")
    except BaseException:
        # Do not release the fence until launchd has stopped this job. If
        # bootout is indeterminate, the dead-PID/deadline rule remains the fallback.
        stopped = subprocess.run([args.launchctl_bin, "bootout", f"{domain}/{label}"],
                                 capture_output=True, timeout=30)
        if stopped.returncode == 0 or (stopped.returncode == 113 and
                                       b"could not find service" in stopped.stderr.lower()):
            clear_owned(root, purpose)
        raise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("launch", help="magistrate: publish fence, bootstrap once, then exit session")
    start.add_argument("--repo", type=Path, required=True)
    start.add_argument("--config", type=Path, help="required for the default r0 runner")
    start.add_argument("--runner-kind", choices=("r0", "r1-smoke", CADENCE_RUNNER_KIND), default="r0")
    start.add_argument("--kit", type=Path, help="cadence-legs-v1: the frozen campaign kit (RL-149 section 2)")
    start.add_argument("--legs", help="cadence-legs-v1: the queue span's roster, comma-separated kit leg ids")
    start.add_argument("--batch-window", help="cadence-legs-v1: HH:MM-HH:MM blackout (default: the R1 driver's)")
    start.add_argument("--soak-reference", type=Path, help="required for r1-smoke unless --fresh-soak")
    start.add_argument("--fresh-soak", action="store_true",
                       help="r1-smoke: run the night's idle soak first and use its reference (RL-94)")
    start.add_argument("--parts", choices=("AB", "A", "C"), default="AB",
                       help="r1-smoke: AB (default), A only (RL-89), or C (RL-145 addendum; needs --fresh-soak)")
    start.add_argument("--output", type=Path, required=True)
    start.add_argument("--python-bin", type=Path, required=True)
    start.add_argument("--disk-path", type=Path, required=True)
    start.add_argument("--checks", help="comma-separated runner check subset (R0-L1); default: the runner's full list")
    start.add_argument("--keep-going", action=argparse.BooleanOptionalAction, default=True,
                       help="continue after a failed check (R0-L3 desk default; --no-keep-going stops at the first)")
    start.add_argument("--launchctl-bin", default="/bin/launchctl")
    start.add_argument("--pmset-bin", default="/usr/bin/pmset")
    start.add_argument("--pgrep-bin", default="/usr/bin/pgrep")
    start.add_argument("--kill-bin", default="/bin/kill")
    start.add_argument("--start-wait-seconds", type=positive_seconds, default=30)
    start.add_argument("--exit-wait-seconds", type=positive_seconds, default=180)
    take = sub.add_parser("handoff")
    take.add_argument("--magistrate-pid", type=int, required=True)
    take.add_argument("--exit-wait-seconds", type=positive_seconds, required=True)
    for command in (start, take):
        if command is start:
            command.add_argument("--magistrate-pid", type=int, required=True)
        command.add_argument("--deadline", type=float, required=True)
    clear = sub.add_parser("clear")
    for command in (take, clear):
        command.add_argument("--purpose", required=True)
        command.add_argument("--pid", type=int, required=True)
    for command in (start, take, clear):
        command.add_argument("--custody-root", type=Path, required=True)
    check = sub.add_parser("preflight")
    check.add_argument("--pmset-bin", default="/usr/bin/pmset")
    check.add_argument("--disk-path", type=Path, required=True)
    run = sub.add_parser("run")
    run.add_argument("--deadline", type=float, required=True)
    run.add_argument("--runner-spec", type=Path, required=True)
    run.add_argument("--pmset-bin", default="/usr/bin/pmset")
    args = parser.parse_args(argv)
    for name in ("repo", "config", "output", "disk_path", "custody_root", "soak_reference", "kit"):
        if getattr(args, name, None) is not None:
            setattr(args, name, getattr(args, name).expanduser().resolve())
    # Absolute but NOT symlink-resolved: a venv interpreter is a symlink to its
    # base Python, and Python finds the venv (pyvenv.cfg) from the invoked path.
    # Resolving it ran R0 on 2026-11-06 under bare Homebrew 3.13 (no mlx).
    if hasattr(args, "python_bin"):
        args.python_bin = Path(os.path.abspath(args.python_bin.expanduser()))
    try:
        if args.command == "launch":
            launch(args)
        elif args.command == "handoff":
            handoff(args)
        elif args.command == "clear":
            clear_owned(args.custody_root, args.purpose, args.pid)
        elif args.command == "preflight":
            preflight(args)
        else:
            return run_until_deadline(args)
        return 0
    except (OSError, ValueError, subprocess.SubprocessError, TimeoutError) as exc:
        print(f"R0 launch refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
