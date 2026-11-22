#!/usr/bin/env python3
"""Hand one conditionless-campaign span (runner kind ``cadence-legs-v1``) to a one-shot LaunchAgent.

    python3.13 -B scripts/launch_cadence_span.py launch --repo R --python-bin PY --kit KIT \\
        [--legs L001,L002,L003] [--batch-window HH:MM-HH:MM] --output OUT --disk-path R \\
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
from decimal import Decimal
import hashlib
import json
import math
import os
from pathlib import Path
import plistlib
import re
import signal
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import launch_align_r0 as base  # noqa: E402
from joulewise.cadence import ctl  # noqa: E402

RUNNER_KIND = "cadence-legs-v1"
LEG_IDS_PATTERN = re.compile(r"L\d{3,4}(?:,L\d{3,4})*")
BATCH_WINDOW_PATTERN = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d-(?:[01]\d|2[0-3]):[0-5]\d")
RUNNER = "scripts/cadence_legs_runner.py"


def cadence_plan(kit: Path | dict, legs: str | None = None, batch_window: str | None = None,
                 t0: float | None = None) -> dict:
    """The campaign runner's plan for this span (kit roster and template; no host contact)."""
    from joulewise.cadence import kit as kitmod, legs as legsmod
    from scripts import cadence_legs_runner as runner

    loaded = kit if isinstance(kit, dict) else kitmod.load_kit(kit)[0]
    # The job kind (RUNNER_KIND, the runner spec this launcher writes) is one: the same runner entry runs
    # v1 kits and v1.1 kits (design doc section 14). The kit's own runner kind must be one it executes.
    if loaded["runner"]["kind"] not in legsmod.RUNNER_KINDS:
        raise ValueError(f"kit runner.kind is not one of {list(legsmod.RUNNER_KINDS)}")
    # RL-171: no blackout and no launch fence unless --batch-window names one (backward compatibility).
    windows = [legsmod.parse_window(batch_window)] if batch_window else runner.default_windows()
    plan = legsmod.plan_span(loaded, t0_epoch=time.time() if t0 is None else t0, windows=windows,
                             leg_ids=legs.split(",") if legs else None, max_span_s=runner.max_span_s())
    if cadence_minimum_seconds(plan) > base.MAX_DESK_SECONDS:
        raise ValueError(f"the span's worst case with its soak retry needs {cadence_minimum_seconds(plan):.0f} s, "
                         f"over the {base.MAX_DESK_SECONDS} s desk ceiling")
    return plan


def cadence_minimum_seconds(plan: dict) -> float:
    """The span's worst case plus the soak retry's budget, the runner's work reserve and the launcher's
    cleanup grace."""
    from scripts import cadence_legs_runner as runner
    return runner.launch_deadline(plan) - plan["t0_epoch_s"]


def latest_attempt(ledger, span_pattern):
    """Select an attempt using the recorded sequence or host boot order."""
    if not isinstance(ledger, dict) or not isinstance(ledger.get("attempts"), list) or not ledger["attempts"]:
        raise ValueError("attempt ledger needs a nonempty attempts list")
    attempts = ledger["attempts"]
    receipts = set()
    for row in attempts:
        if not isinstance(row, dict) or not isinstance(row.get("span_id"), str) or not span_pattern.fullmatch(row["span_id"]):
            raise ValueError("attempt ledger has an invalid span id")
        receipt = row.get("close_receipt")
        if not isinstance(receipt, str) or not Path(receipt).is_absolute() or any(c in receipt for c in "\r\n"):
            raise ValueError(f"invalid close receipt path for {row['span_id']}")
        path = Path(receipt).resolve()
        if path in receipts:
            raise ValueError(f"duplicate attempt receipt path for {row['span_id']}")
        receipts.add(path)
    if any("sequence" in row for row in attempts):
        sequences = [row.get("sequence") for row in attempts]
        if any(type(seq) is not int or seq <= 0 for seq in sequences) or len(set(sequences)) != len(sequences):
            raise ValueError("attempt sequences must be present, positive and unique")
        return max(attempts, key=lambda row: row["sequence"])

    boots = [row.get("boot_id") for row in attempts]
    if any(not isinstance(boot, str) or not boot for boot in boots):
        raise ValueError("unsequenced attempts need a boot id")
    order = ledger.get("boot_order", list(dict.fromkeys(boots)) if len(set(boots)) == 1 else None)
    if (not isinstance(order, list) or any(not isinstance(boot, str) or not boot for boot in order)
            or len(set(order)) != len(order) or not set(boots).issubset(order)):
        raise ValueError("unsequenced attempts across boots need an explicit boot order")
    boot = next(boot for boot in reversed(order) if boot in boots)
    candidates = [row for row in attempts if row["boot_id"] == boot]
    if len(candidates) == 1:
        return candidates[0]
    times = [row.get("monotonic_ns") for row in candidates]
    if any(type(t) is not int or t < 0 for t in times) or len(set(times)) != len(times):
        raise ValueError("latest boot has ambiguous attempt order")
    return max(candidates, key=lambda row: row["monotonic_ns"])


def verify_restore(result, *, native):
    def zero(value):
        return type(value) is int and value == 0

    if not isinstance(result, dict) or result.get("ok") is not True:
        raise ValueError("restore lacks a successful readback")
    for field in ("rc", "exit_code"):
        if (field in result or (native and field == "exit_code")) and not zero(result.get(field)):
            raise ValueError("restore command did not pass")
    if (native or "observed" in result) and not zero(result.get("observed")):
        raise ValueError("restore readback must record AC Automatic (0)")
    if "read" in result:
        read = result["read"]
        if not isinstance(read, dict) or not zero(read.get("value")) or read.get("error") is not None:
            raise ValueError("restore has incomplete or contradictory AC readback evidence")


def verify_shutdown(receipt, path, *, require_attestation, runner):
    """Check recorded restore and feed stops against the lead's RL-179 close attestation."""
    pgids = set()

    def record_pgid(pgid):
        if type(pgid) is not int or pgid <= 1:
            raise ValueError("invalid process group ID in close receipt")
        pgids.add(pgid)

    def stopped(result):
        if not isinstance(result, dict) or result.get("proven_stopped") is not True:
            return False
        if "group" in result:
            group = result["group"]
            if not isinstance(group, dict) or group.get("reaped") is not True or group.get("group_census") != []:
                return False
            if "pgid" in group:
                record_pgid(group["pgid"])
        if "supervisor" in result:
            exits = result["supervisor"]["exits"]
            if not isinstance(exits, list):
                return False
            # Each supervisor leader was started in a new session, so its PID was also its PGID.
            for retired in exits:
                record_pgid(retired["pid"])
        return True

    def check_stop_error(row):
        error = row.get("error")
        if isinstance(error, str) and "not proven stopped" in error:
            raise ValueError(f"{row.get('name', 'predecessor')} process group not proven stopped")

    stop_steps = {}
    restore_steps = 0
    native = receipt.get("schema") == runner.RECEIPT_SCHEMA
    for row in receipt.get("steps", []):
        check_stop_error(row)
        name = row["name"]
        if name == "restore" or name.startswith(("stop-", "close-")):
            if type(row.get("rc")) is not int or row["rc"] != 0:
                raise ValueError(f"{name} did not pass")
        if name == "restore":
            restore_steps += 1
            if restore_steps != 1:
                raise ValueError("restore lacks a unique successful readback")
            verify_restore(row.get("result"), native=native)
        if name.startswith("stop-"):
            feed = name[5:]
            result = row.get("result")
            if (feed in stop_steps or not stopped(result)
                    or ("rc" in result and (type(result["rc"]) is not int or result["rc"] != 0))):
                raise ValueError(f"{name} lacks a unique successful stop proof")
            stop_steps[feed] = {"rc": row["rc"], **result}
        elif isinstance(row.get("result"), dict) and "group" in row["result"] and not stopped(row["result"]):
            raise ValueError(f"{name} process group not proven stopped")
    check_stop_error(receipt)
    workload_groups = receipt.get("workload_groups", [])
    if not isinstance(workload_groups, list):
        raise ValueError("invalid workload group records")
    for group in workload_groups:
        if not isinstance(group, dict) or group.get("proven_stopped") is not True:
            raise ValueError("workload process group not proven stopped")
        record_pgid(group.get("pgid"))
    feeds = receipt.get("feeds", {})
    if native:
        if restore_steps != 1 or not {"agents", "meter", "volumes"} <= stop_steps.keys() or feeds.keys() != stop_steps.keys():
            raise ValueError("cadence receipt does not prove every feed stopped")
    if "restore_readbacks" in receipt:
        readbacks = receipt["restore_readbacks"]
        if not isinstance(readbacks, dict) or not readbacks or not all(v is True for v in readbacks.values()):
            raise ValueError("restore readbacks did not pass")
    elif restore_steps != 1:
        raise ValueError("restore readbacks did not pass")
    for name, feed in feeds.items():
        stop = feed.get("stop")
        if (not stopped(stop) or type(stop.get("rc")) is not int or stop["rc"] != 0
                or (name in stop_steps and stop != stop_steps[name])):
            raise ValueError(f"feed {name} has incomplete or contradictory stop evidence")
    if "meter" in receipt and receipt["meter"].get("proven_stopped") is not True:
        raise ValueError("meter stop was not proven")
    if require_attestation:
        proofs = ("HOST_RESTORE_OK", "FEEDS_STOPPED", "GROUPS_ABSENT", "FOREIGN_PROCESSES_ABSENT")
        if os.environ.get("CLOSE_PROOF_RECEIPT") != path or any(os.environ.get(key) != "1" for key in proofs):
            raise ValueError("receipt-bound restore, feed stop, group absence and foreign process proof required")
    if pgids:
        from scripts import run_night

        for pgid in sorted(pgids):
            absent, members = run_night._group_census(pgid)
            if absent is not True or members != []:
                raise ValueError(f"fresh census did not prove process group {pgid} empty")


def proven_close(ledger, runner, *, require_attestation=True):
    attempt = latest_attempt(ledger, runner.SPAN_ID_PATTERN)
    span = attempt["span_id"]
    try:
        receipt = json.loads(Path(attempt["close_receipt"]).read_text(), parse_float=Decimal)
        if receipt.get("span_id") != span:
            raise ValueError("close receipt span id differs from the latest attempt")
        verify_shutdown(receipt, attempt["close_receipt"], require_attestation=require_attestation, runner=runner)
        ended = receipt["ended"]
        if "epoch_ns" in ended:
            epoch_ns = ended["epoch_ns"]
        else:
            epoch = ended["epoch_s"]
            if type(epoch) is not int and (not isinstance(epoch, Decimal) or not epoch.is_finite()):
                raise ValueError("invalid close epoch")
            numerator, denominator = epoch.as_integer_ratio()
            epoch_ns, fraction = divmod(numerator * runner.NS_PER_SECOND, denominator)
            if fraction:
                raise ValueError("close epoch exceeds nanosecond precision")
        if type(epoch_ns) is not int or epoch_ns <= 0:
            raise ValueError("invalid close epoch")
    except FileNotFoundError as error:
        raise ValueError(f"latest attempt {span} has no close receipt") from error
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        raise ValueError(f"latest attempt {span}: {error}") from error
    return attempt, epoch_ns


def require_ctl_pilot_pass(args, kit, span, authority, ledger, runner):
    """Verify the lead-pinned independent PASS against the latest pilot for this kit."""
    path = getattr(args, "pilot_hand_read", None)
    if authority["layout_index"] == 0:
        if path is not None or "pilot_pass_sha256" in span:
            raise ValueError("pilot launch cannot carry span 2's hand-read authority")
        return
    if path is None:
        raise ValueError("ctl span 2 requires --pilot-hand-read with the independent PASS")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != span["pilot_pass_sha256"]:
        raise ValueError("pilot hand-read bytes differ from the lead-approved queue hash")
    proof = json.loads(raw)
    keys = {"schema", "status", "reviewer", "kit_sha256", "pilot_plan_id", "pilot_receipt_sha256"}
    if (not isinstance(proof, dict) or set(proof) != keys or proof["schema"] != ctl.PILOT_PASS_SCHEMA
            or proof["status"] != "PASS" or proof["kit_sha256"] != authority["kit_sha256"]
            or not isinstance(proof["reviewer"], str) or not proof["reviewer"].strip()):
        raise ValueError("ctl span 2 needs an independent pilot PASS for this exact kit")

    candidates = []
    for attempt in ledger["attempts"]:
        bind = attempt.get("ctl")
        if isinstance(bind, dict) and bind.get("layout_index") == 0 and bind.get("kit_sha256") == authority["kit_sha256"]:
            candidates.append(attempt)
    if not candidates:
        raise ValueError("pilot hand-read has no matching pilot attempt in the ledger")
    pilot = latest_attempt({**ledger, "attempts": candidates}, runner.SPAN_ID_PATTERN)
    if pilot["span_id"] != proof["pilot_plan_id"]:
        raise ValueError("pilot hand-read does not name the latest pilot attempt for this kit")
    receipt_raw = Path(pilot["close_receipt"]).read_bytes()
    if hashlib.sha256(receipt_raw).hexdigest() != proof["pilot_receipt_sha256"]:
        raise ValueError("pilot hand-read does not bind the pilot's exact close receipt")
    receipt = json.loads(receipt_raw)
    expected = {
        "schema": runner.RECEIPT_SCHEMA, "runner_kind": ctl.RUNNER_KIND, "mock": False,
        "span_id": pilot["span_id"], "rc": 0, "roster": kit["layout"][0],
        "legs_finished": len(kit["layout"][0]),
        "kit": {"campaign_id": kit["campaign_id"], "sha256": authority["kit_sha256"],
                "frozen_commit": kit["frozen"]["commit"]},
    }
    if not isinstance(receipt, dict) or any(type(receipt.get(key)) is not type(value) or receipt[key] != value
                                           for key, value in expected.items()):
        raise ValueError("pilot hand-read does not bind a clean native close of the full pilot roster")


def verify_ctl_child(args, kit, kit_sha256, runner):
    """Use the same authority at the child entry before its production dependencies."""
    if args.attempt_ledger is None:
        raise ValueError("ctl child requires the launch attempt ledger")
    document, span, authority = ctl.queued_span(args, kit, kit_sha256, time.time())
    ledger = json.loads(args.attempt_ledger.read_bytes())
    current = latest_attempt(ledger, runner.SPAN_ID_PATTERN)
    if (current["span_id"] != args.span_id or current.get("ctl") != authority
            or Path(current["close_receipt"]).resolve() != args.output.resolve() / runner.RECEIPT_NAME):
        raise ValueError("ctl child does not match the published queue-bound launch attempt")
    require_ctl_pilot_pass(args, kit, span, authority, ledger, runner)
    ctl.check_queue_window(document, span, kit, time.time())


def append_attempt(path, ledger, previous, span_id, receipt, span_pattern, *, ctl_authority=None):
    """Publish the start plan under the desk fence lock before bootstrap."""
    row = {"span_id": span_id, "close_receipt": str(receipt)}
    if ctl_authority is not None:
        row["ctl"] = ctl_authority
    if "sequence" in previous:
        row["sequence"] = previous["sequence"] + 1
    else:
        if sys.platform == "darwin":
            boot = subprocess.check_output(["/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"], text=True).strip()
        else:
            boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        order = ledger.setdefault("boot_order", [previous["boot_id"]])
        if boot not in order:
            order.append(boot)
        row.update(boot_id=boot, monotonic_ns=time.monotonic_ns())
    ledger["attempts"].append(row)
    if latest_attempt(ledger, span_pattern) is not row:
        raise ValueError("the new attempt does not follow the recorded attempt order")
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as handle:
        temp = Path(handle.name)
        try:
            json.dump(ledger, handle)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            os.replace(temp, path)
            parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(parent)
            finally:
                os.close(parent)
        finally:
            temp.unlink(missing_ok=True)


def runner_argv(args, *, kit_sha256=None) -> list[str]:
    legs, window = getattr(args, "legs", None), getattr(args, "batch_window", None)
    t0_date = getattr(args, "authorized_t0_date", None)
    anchor = getattr(args, "t0_anchor", None)
    t0_args = []
    if t0_date is not None:
        t0_args = ["--authorized-t0-date", t0_date, "--t0-not-before", str(args.t0_not_before),
                   "--t0-before", str(args.t0_before)]
    if t0_date is not None or anchor is not None:
        t0_args += ["--t0-anchor", ":".join(map(str, anchor))]
    if getattr(args, "t0_not_before_ns", None) is not None:
        t0_args += ["--t0-not-before-ns", str(args.t0_not_before_ns)]
    span_id = getattr(args, "span_id", None)
    authority_args = []
    if kit_sha256 is not None:
        for key in (*ctl.QUEUE_AUTHORITY_FLAGS, "attempt_ledger"):
            value = getattr(args, key, None)
            if value is not None:
                authority_args += ["--" + key.replace("_", "-"), str(value)]
    return [str(args.python_bin), str(args.repo / RUNNER), "run", "--kit", str(args.kit), "--output", str(args.output),
            *(["--kit-sha256", kit_sha256] if kit_sha256 is not None else []),
            *(["--legs", legs] if legs else []), *(["--batch-window", window] if window else []),
            "--deadline", str(args.deadline), "--pmset-bin", str(args.pmset_bin),
            *(["--span-id", span_id] if span_id else []), *t0_args, *authority_args]


def launch(args, *, loaded_kit=None) -> None:
    """``launch_align_r0.launch`` for this runner kind: refuse, publish the fence, bootstrap once."""
    from joulewise.cadence import kit as kitmod
    from scripts import cadence_legs_runner as span_runner

    if args.kit is None or not args.kit.is_file():
        raise ValueError("cadence-legs-v1 requires an existing --kit")
    kit, sha = kitmod.load_kit(args.kit) if loaded_kit is None else loaded_kit
    scripted_ctl = kit["runner"]["kind"] == ctl.RUNNER_KIND
    approved_sha = getattr(args, "kit_sha256", None)
    if scripted_ctl:
        ctl.require_issued(kit)
        ctl.require_queue_kit_hash(approved_sha, sha)
    elif approved_sha is not None or any(getattr(args, key, None) is not None for key in ctl.QUEUE_AUTHORITY_FLAGS):
        raise ValueError("queue-approved ctl kit was replaced by a different runner kind")
    ledger_path = getattr(args, "attempt_ledger", None)
    previous_receipt = getattr(args, "previous_close_receipt", None)
    span_id = getattr(args, "span_id", None)
    close_bound = getattr(args, "t0_not_before_ns", None)
    if span_id is not None and not span_runner.SPAN_ID_PATTERN.fullmatch(span_id):
        raise ValueError("invalid --span-id")
    if (scripted_ctl or kit["seed_law"]["method"] == span_runner.QUAL_LAW
            or ledger_path is not None or previous_receipt is not None):
        if ledger_path is None or not previous_receipt or span_id is None or close_bound is None:
            raise ValueError("ledger-backed launch requires --attempt-ledger, --previous-close-receipt, "
                             "--span-id and --t0-not-before-ns")
    if scripted_ctl:
        span_runner.validate_t0_authority(kit, getattr(args, "authorized_t0_date", None),
                                          getattr(args, "t0_not_before", None), getattr(args, "t0_before", None),
                                          getattr(args, "t0_anchor", None), require_anchor=False,
                                          t0_not_before_ns=close_bound)
        ctl.queued_span(args, kit, sha, time.time())
    if (args.magistrate_pid <= 1 or not base.pid_alive(args.magistrate_pid)
            or not math.isfinite(args.deadline) or args.deadline <= time.time()):
        raise ValueError("live magistrate PID and future finite epoch deadline required")
    if args.deadline > time.time() + base.MAX_DESK_SECONDS:
        raise ValueError(f"desk deadline is more than {base.MAX_DESK_SECONDS} s ahead")
    if args.output.exists():
        raise ValueError("campaign output must be a new record directory")
    if args.legs is not None and not LEG_IDS_PATTERN.fullmatch(args.legs):
        raise ValueError("--legs must be comma-separated kit leg ids (L001,L002,...)")
    if args.batch_window is not None and not BATCH_WINDOW_PATTERN.fullmatch(args.batch_window):
        raise ValueError("--batch-window must be HH:MM-HH:MM")
    plan = cadence_plan(kit, args.legs, args.batch_window)
    if args.deadline - time.time() < cadence_minimum_seconds(plan):
        raise ValueError("cadence-legs-v1 deadline cannot fit the span's worst case, work reserve and cleanup grace")
    if scripted_ctl and getattr(args, "t0_anchor", None) is None:
        args.t0_anchor = span_runner.RealClock.arm_anchor_ns()
    child_argv = runner_argv(args, kit_sha256=approved_sha)
    runner = Path(child_argv[1])
    if not runner.is_file() or not os.access(args.python_bin, os.X_OK):
        raise ValueError("measurement checkout runner and executable interpreter required")
    root = args.custody_root
    root.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    purpose = f"align-r0:{token}"
    label = f"com.joulewise.align-r0.{token}"
    domain = f"gui/{os.getuid()}"
    job = root / "r0-launches" / token
    plist = job / f"{label}.plist"
    wrapper = Path(base.__file__).with_name("run_align_r0_launchagent.sh").resolve()
    runner_spec = job / "runner.json"
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
    with base.fence_lock(root):
        current = base.read_fence(root)
        if current and current["deadline"] > time.time() and base.pid_alive(current["pid"]):
            raise ValueError("an active desk fence already exists")
        if ledger_path is not None:
            ledger = json.loads(ledger_path.read_text())
            previous, close_ns = proven_close(ledger, span_runner, require_attestation=scripted_ctl)
            if previous["close_receipt"] != previous_receipt or close_ns != close_bound:
                raise ValueError(f"close proof changed before launch for {previous['span_id']}")
        authority = None
        if scripted_ctl:
            document, row, authority = ctl.queued_span(args, kit, sha, time.time())
            if any(attempt["span_id"] == span_id for attempt in ledger["attempts"]):
                raise ValueError("ctl queue plan already has a recorded attempt")
            require_ctl_pilot_pass(args, kit, row, authority, ledger, span_runner)
        job.mkdir(parents=True)
        runner_spec.write_text(json.dumps({"kind": RUNNER_KIND, "argv": child_argv}) + "\n")
        plist.write_bytes(plistlib.dumps(job_spec))
        if scripted_ctl:
            ctl.check_queue_window(document, row, kit, time.time())
        if ledger_path is not None:
            append_attempt(ledger_path, ledger, previous, span_id, args.output / span_runner.RECEIPT_NAME,
                           span_runner.SPAN_ID_PATTERN, ctl_authority=authority)
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
    from joulewise.cadence import kit as kitmod
    from scripts import cadence_legs_runner as runner

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("launch", help="magistrate: publish fence, bootstrap once, then exit session")
    start.add_argument("--repo", type=Path, required=True)
    start.add_argument("--kit", type=Path, required=True, help="the frozen campaign kit (RL-149 section 2)")
    start.add_argument("--kit-sha256", help="ctl only: SHA-256 from the validated queue span")
    ctl.add_queue_authority_arguments(start)
    start.add_argument("--legs", help="the queue span's roster, comma-separated kit leg ids")
    start.add_argument("--batch-window", help="HH:MM-HH:MM blackout (default: none, RL-171)")
    start.add_argument("--output", type=Path, required=True)
    start.add_argument("--python-bin", type=Path, required=True)
    start.add_argument("--disk-path", type=Path, required=True)
    start.add_argument("--custody-root", type=Path, required=True)
    start.add_argument("--magistrate-pid", type=int, required=True)
    start.add_argument("--deadline", type=float, required=True)
    start.add_argument("--span-id", help="span identity carried into its close receipt")
    start.add_argument("--attempt-ledger", type=Path, help="shared launch/start-plan ledger, required for qualification and ctl")
    start.add_argument("--previous-close-receipt", help="proved close receipt, required for qualification and ctl")
    runner.add_t0_authority_arguments(start)
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
    close = sub.add_parser("close-proof", help="read the latest attempt and verify its own close receipt")
    close.add_argument("--attempt-ledger", type=Path, required=True)
    args = parser.parse_args(argv)
    for name in ("repo", "kit", "output", "disk_path", "custody_root", "attempt_ledger",
                 "queue", "queue_kits_root", "pilot_hand_read"):
        if getattr(args, name, None) is not None:
            setattr(args, name, getattr(args, name).expanduser().resolve())
    if hasattr(args, "python_bin"):
        args.python_bin = Path(os.path.abspath(args.python_bin.expanduser()))   # not symlink-resolved (venv)
    try:
        if args.command == "close-proof":
            attempt, close_ns = proven_close(json.loads(args.attempt_ledger.read_text()), runner)
            print(attempt["span_id"], close_ns, attempt["close_receipt"], sep="\n")
            return 0
        if args.command == "launch":
            loaded = kitmod.load_kit(args.kit)
            kit, _ = loaded
            if kit["runner"]["kind"] == ctl.RUNNER_KIND or args.kit_sha256 is not None:
                launch(args, loaded_kit=loaded)
                return 0
            try:
                runner.validate_t0_authority(kit, args.authorized_t0_date, args.t0_not_before,
                                             args.t0_before, args.t0_anchor, require_anchor=False,
                                             t0_not_before_ns=args.t0_not_before_ns)
            except ValueError as error:
                parser.error(str(error))
            if args.authorized_t0_date is not None and args.t0_anchor is None:
                args.t0_anchor = runner.RealClock.arm_anchor_ns()
            launch(args)
            return 0
        return run_until_deadline(args)
    except (OSError, ValueError, subprocess.SubprocessError, TimeoutError) as exc:
        print(f"campaign launch refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
