#!/usr/bin/env python3
"""Campaign span runner, runner kind ``cadence-legs-v1`` (RL-149 section 2; section 5 item 6).

    python3.13 -B scripts/cadence_legs_runner.py run --kit KIT.json --output DIR --deadline EPOCH \\
        [--legs L001,L002,L003] [--batch-window HH:MM-HH:MM] [--pmset-bin PATH]
    python3.13 -B scripts/cadence_legs_runner.py plan --kit KIT.json [--legs ...] [--t0 EPOCH] [--batch-window ...]
    python3.13 -B scripts/cadence_legs_runner.py mock --kit KIT.json --output DIR [--legs ...] \\
        [--t0-local 2026-11-15T13:20] [--contaminate L002] [--g0-timeout L005]
    python3.13 -B scripts/cadence_legs_runner.py pin-kit KIT.json --commit SHA [--write]

``run`` is launched ONLY by ``launch_cadence_span.py launch`` (the R0/R1 desk launcher's procedure:
LaunchAgent, the desk fence, Spotlight paused). One span, agent-free:

1. preflight: the kit validates; HEAD is the kit's frozen commit and every frozen path's
   working-tree bytes hash as the kit says; no night agent loaded; AC power; condition-13
   sources at HEAD; the agent census, KM003C and volume feeds start (the R1 smoke's own feeds);
   AC powermode 0 read back; display sleep and dwell;
2. the plan adapter sizes the span from the kit and the roster (``joulewise.cadence.legs.plan_span``)
   and must fit before ``--deadline``;
3. ONE fresh soak (the night's idle_soak path via ``soak_child``: ``run_align_r1_smoke.soak_child``'s steps
   without its OS batch window check, RL-171). A soak that fails its settle or quiet check is retried
   once (``SOAK_RETRIES``; the launch deadline budgets it) before the span stops;
4. the roster's legs in the kit's seeded order. Each leg is one ``cadence-leg`` runtime
   invocation (``scripts/cadence_leg_runtime.py``) that runs its own G0 and is admitted by it.
   Batch admission applies only when ``--batch-window`` names a blackout: then no soak overlaps it
   and no leg starts in it; a leg in flight finishes. Per-leg redo: RL-72 E2's load rule (above 0.5 core for 60 s,
   ``align_r1_rehearsal.os_load_verdict``) redoes the leg, up to the kit's ``redo_quota`` per span;
   a rejected attempt is kept as ``runtime.rejected<N>``. A G0 timeout or a cut turn is recorded
   and the span goes on (the leg is not admitted). A leg runtime that refuses or fails stops the span;
5. close: Automatic restore, feeds stopped and hashed, ``runner_receipt.json``, and the
   ``desk-bundle/`` the close step publishes (``leg-summary-v1``: one ``leg_summary.json`` per leg,
   ``span/result.json``, ``span/meter.json``). NO energy is read or written by this runner.

Stage stamps go to ``DIR/chain-stages.jsonl`` (start and end of every stage) for the RL-128 probe.

RL-171: quiet is a rule about processes, not clock times. With no ``--batch-window`` there is no
blackout, no hold and no launch fence; the per-leg agent census, process census and rule 5's load
journal with redo are the quiet checks. ``--batch-window HH:MM-HH:MM`` still works (backward
compatibility): the plan then refuses a worst case that meets it, and the soak and leg starts hold
outside it.

``mock`` executes a whole span on this machine with a fake clock, fake feeds and a fake leg runtime
(no model, no sensor, no host command), then builds the Air desk table on its bundle.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.cadence import ctl, kit as kitmod, legs as legsmod  # noqa: E402
from joulewise.cadence.kit_v11 import QUAL_LAW  # noqa: E402

RECEIPT_SCHEMA = "joulewise.cadence_span_receipt.v1"
LEG_RECORD_SCHEMA = "joulewise.cadence_leg_record.v1"
LEG_RUNTIME = "scripts/cadence_leg_runtime.py"
RECEIPT_NAME = "runner_receipt.json"
PLAN_NAME = "span_plan.json"
DESK_BUNDLE = "desk-bundle"
SIGNALS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)
POLL_S = 0.25
# The parent launcher's reserves (run_align_r1_smoke.WORK_RESERVE_S; launch_align_r0's cleanup grace).
WORK_RESERVE_S = 2 * 180 + 10
LAUNCH_RESERVE_S = WORK_RESERVE_S + 180 + 10
# RL-171: a soak that fails its settle or quiet check is retried once before the span stops. The launch
# deadline budgets one more soak per retry (``launch_deadline``), so a retry never spends a leg's or a
# redo's time. The soak child exits SOAK_REFUSED_RC on exactly those two refusals.
SOAK_RETRIES = 1
SOAK_REFUSED_RC = 5
NS_PER_SECOND = 1_000_000_000
UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
SPAN_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]*")


class SpanRefusal(RuntimeError):
    """The span stops here: nothing further runs; cleanup and the receipt still happen."""

    def __init__(self, message, code=2):
        super().__init__(message)
        self.code = code


class LegRuntimeError(SpanRefusal):
    pass


class SoakRefusal(SpanRefusal):
    """The fresh soak failed its settle or quiet check (retried up to SOAK_RETRIES times)."""


class SoakQuietRefusal(ValueError):
    """Inside the soak child: the idle soak is unsettled or loaded."""


def _stamp(clock):
    return {"epoch_s": clock.time(), "monotonic_ns": int(clock.monotonic() * 1e9)}


def default_windows():
    """No blackout (RL-171: quiet is enforced per leg, never by a clock window)."""
    return []


def max_span_s():
    from scripts import launch_align_r0 as launcher
    return launcher.MAX_DESK_SECONDS - LAUNCH_RESERVE_S


def soak_retry_budget_s(plan):
    """The time the soak retries may take: one kit soak each (RL-171)."""
    return SOAK_RETRIES * plan["soak_s"]


def launch_deadline(plan):
    """The ``--deadline`` the launcher passes: the plan's work deadline, the soak retry's budget, and
    the runner's and the launcher's cleanup reserves."""
    return plan["deadline_epoch_s"] + soak_retry_budget_s(plan) + LAUNCH_RESERVE_S


# --------------------------------------------------------------------------
# Dependencies: production and mock
# --------------------------------------------------------------------------
class RealClock:
    @staticmethod
    def time():
        return time.time()

    @staticmethod
    def monotonic():
        return time.monotonic()

    @staticmethod
    def continuous_ns():
        # Darwin CLOCK_MONOTONIC_RAW uses mach_continuous_time, including sleep.
        # CLOCK_MONOTONIC is realtime minus boot time in Apple's libc.
        # https://developer.apple.com/documentation/driverkit/mach_continuous_time
        # https://github.com/apple-oss-distributions/Libc/blob/main/gen/clock_gettime.c
        clock_id = time.CLOCK_MONOTONIC_RAW if sys.platform == "darwin" else time.CLOCK_BOOTTIME
        return time.clock_gettime_ns(clock_id)

    @staticmethod
    def epoch_and_monotonic_ns():
        return time.time_ns(), RealClock.continuous_ns()

    @staticmethod
    def arm_anchor_ns():
        before_ns = RealClock.continuous_ns()
        epoch_ns, after_ns = RealClock.epoch_and_monotonic_ns()
        return epoch_ns, before_ns, after_ns

    @staticmethod
    def sleep(seconds):
        time.sleep(seconds)


@dataclass
class Deps:
    clock: object
    feeds: list
    host: object
    run_soak: Callable          # (soak_dir, cap_s, feeds, work_remaining) -> soak_reference Path;
                                #  raises SoakRefusal on a settle or quiet refusal
    run_leg: Callable           # (attempt_dir, spec_path, soak_reference, cap_s, feeds, work_remaining
                                #  [, span_reference=DIR for a span-reference consumer]) -> result
    verify_frozen: Callable     # (kit) -> {"rc": 0, ...}; raises SpanRefusal on a mismatch
    load_verdict: Callable      # (name, result, wall_s) -> {"redo": bool, ...}; raises on a bad journal
    soak_cap_s: float
    mock: bool = False
    max_span_s: float | None = None                     # None: the launcher's ceiling less its reserves
    workload_groups: list | None = None                 # one record per spawned soak or leg group


def run_child(*, name, argv, cap_s, log_dir, feeds, work_remaining, workload_groups=None):
    """One child process group, bounded by ``cap_s`` and the work deadline, feeds polled meanwhile
    (``run_align_r1_smoke.part`` generalized: the same deadline enforcer and group teardown)."""
    from scripts import run_align_r1_smoke as smoke, run_night as night
    if work_remaining() < cap_s:
        raise SpanRefusal(f"{name} not started: its {cap_s:g} s cap cannot fit before the work deadline", 3)
    log_dir = Path(log_dir)
    until = time.monotonic() + cap_s
    child, deadline, proof = None, None, {}
    try:
        with (log_dir / f"{name}.stdout.log").open("ab") as out, (log_dir / f"{name}.stderr.log").open("ab") as err:
            with smoke.register_child_before_interrupt():
                child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                         start_new_session=True, close_fds=True)
                group = {"name": name, "pgid": child.pid, "proven_stopped": False}
                if workload_groups is not None:
                    workload_groups.append(group)
                deadline_dir = log_dir / "deadlines" / name
                deadline_dir.mkdir(parents=True)
                deadline = smoke.PartDeadline(child, pgid=child.pid, night_dir=deadline_dir, plan=None,
                                              deadline_epoch_s=time.time() + max(0, until - time.monotonic()),
                                              deadline_monotonic=until)
                deadline.start()
            while child.poll() is None:
                work_remaining()
                if time.monotonic() >= until:
                    raise SpanRefusal(f"{name} exceeded its {cap_s:g} s cap", 3)
                for feed in feeds:
                    feed.poll()
                time.sleep(.1)
            if deadline.expired() or deadline.cancel() is not None:
                raise SpanRefusal(f"{name} exceeded its {cap_s:g} s cap", 3)
            code = child.wait()
    finally:
        if child is not None:
            handlers = {s: signal.signal(s, signal.SIG_IGN) for s in SIGNALS}
            try:
                fired = deadline.cancel() if deadline is not None else None
                if fired is not None:
                    proof.update(fired)
                    proven = fired["proven"]
                else:
                    proven = night._terminate_process_group(child, evidence=proof)
                group["proven_stopped"] = proven is True and proof.get("reaped") is True and proof.get("group_census") == []
            finally:
                for s, handler in handlers.items():
                    signal.signal(s, handler)
            if not group["proven_stopped"]:
                raise SpanRefusal(f"{name} process group not proven stopped: {proof}")
    return {"rc": code, "argv": [str(a) for a in argv], "cap_s": cap_s, "group": proof, "proven_stopped": True}


def leg_runtime_argv(inputs):
    """The bound runtime argv from the registration inputs, with the leg entry in place of the
    R1 runtime entry: the same interpreter, ``-B`` and the same bound runtime config."""
    from scripts import align_r1_rehearsal as r1
    argv = r1.runtime_argv_from_inputs(inputs)
    if Path(argv[2]).name != "align_r1_runtime.py":
        raise SpanRefusal(f"inputs.WP15.runtime_entrypoint is not the R1 runtime: {argv[2]}")
    return [argv[0], argv[1], str(ROOT / LEG_RUNTIME), *argv[3:]]


def accepted_result(attempt_dir, *, ctl_spec=None):
    """The leg runtime's result, bound by its complete terminal custody (as ``Segment.accepted_result``)."""
    from joulewise.align.apple import r1_runtime as rt
    path = Path(attempt_dir) / rt.RESULT_NAME
    try:
        raw = path.read_bytes()
        custody = json.loads((Path(attempt_dir) / rt.CUSTODY_NAME).read_bytes())
        value = json.loads(raw)
    except (OSError, ValueError) as error:
        raise LegRuntimeError(f"{attempt_dir}: no readable result and custody ({error})") from error
    if (custody.get("schema") != rt.CUSTODY_SCHEMA or custody.get("status") != "complete"
            or (custody.get("files") or {}).get(rt.RESULT_NAME) != hashlib.sha256(raw).hexdigest()):
        raise LegRuntimeError(f"{attempt_dir}: result is not bound by complete runtime custody")
    if value.get("kind") != legsmod.LEG_KIND:
        raise LegRuntimeError(f"{attempt_dir}: result kind {value.get('kind')!r}")
    if ctl_spec is not None:
        try:
            work_raw = (path.parent / ctl.WORK_NAME).read_bytes()
            work = json.loads(work_raw)
        except (OSError, ValueError) as error:
            raise LegRuntimeError(f"{attempt_dir}: no readable ctl work record") from error
        digest = hashlib.sha256(work_raw).hexdigest()
        if (custody["files"].get(ctl.WORK_NAME) != digest or value.get("script_record_sha256") != digest
                or not isinstance(work, dict) or work.get("schema") != ctl.WORK_SCHEMA
                or value.get("leg_id") != ctl_spec["leg_id"] or work.get("leg_id") != ctl_spec["leg_id"]
                or work.get("leg_spec_sha256") != ctl.leg_spec_sha256(ctl_spec)
                or work.get("script") != ctl_spec["script"]):
            raise LegRuntimeError(f"{attempt_dir}: ctl work record does not bind the planned leg spec")
        steps = work.get("steps")
        complete = ctl.work_complete(steps, ctl_spec["script"])
        if (type(value.get("g0_released")) is not bool or (not value["g0_released"] and steps != [])
                or work.get("complete") is not complete or value.get("script_complete") is not complete):
            raise LegRuntimeError(f"{attempt_dir}: inconsistent ctl completion")
        if complete:
            visible = [row for row in steps if row["kind"] == "turn"]
            prefill = sum(row["context_tokens"] - row["cached_prompt_tokens"] for row in visible)
            expected = {"turn_start_ns": visible[0]["started_ns"], "first_token_ns": visible[0]["first_token_ns"],
                        "turn_end_ns": visible[-1]["ended_ns"], "prefill_tokens": prefill,
                        "decode_tokens": sum(r["actual_tokens"] for r in visible)}
            for key, observed in expected.items():
                if type(value.get(key)) is not int or value[key] != observed:
                    raise LegRuntimeError(f"{attempt_dir}: ctl logged envelope disagrees with physical calls on {key}")
        if not complete and value["g0_released"]:
            value.update(leg_status="incomplete", decode_cap_reached=False)
    return value


class ProductionHost:
    def __init__(self, pmset_bin):
        self.pmset_bin = pmset_bin

    def night_agents(self):
        from scripts import run_align_r1_smoke as smoke
        return smoke.night_agents()

    def ac_power(self):
        from scripts import run_align_r1_smoke as smoke
        return smoke.ac_power()

    def condition13(self):
        from scripts import run_align_r1_smoke as smoke
        return smoke.condition13()

    def read_power(self):
        from scripts import run_align_r1_smoke as smoke
        return smoke.read_power()

    def restore_power(self, power_read):
        from scripts import run_align_r1_smoke as smoke
        return smoke.restore_power(power_read=power_read)

    def display(self):
        from scripts import run_align_r1_smoke as smoke
        return smoke.display(self.pmset_bin)

    def dwell_s(self):
        from scripts import launch_align_r0 as launcher
        return launcher.display_dwell_seconds()


def verify_frozen_production(kit, *, repo=None, require_clean=False):
    if kit.get("runner", {}).get("kind") == ctl.RUNNER_KIND:
        try:
            ctl.require_issued(kit)
        except kitmod.KitError as error:
            raise SpanRefusal(str(error)) from error
    checkout = (ROOT if repo is None else Path(repo)).resolve()

    def git_read(*args):
        try:
            return subprocess.run(["git", "--no-optional-locks", "-C", str(checkout), *args],
                                  capture_output=True, text=True, check=True, timeout=60).stdout
        except (OSError, subprocess.SubprocessError) as error:
            raise SpanRefusal(f"could not verify measurement checkout with git {args[0]}") from error

    identity = git_read("rev-parse", "--show-toplevel", "HEAD").splitlines()
    if len(identity) != 2 or Path(identity[0]).resolve() != checkout:
        raise SpanRefusal("--repo must name the measurement checkout root")
    head = identity[1]
    if head != kit["frozen"]["commit"]:
        raise SpanRefusal(f"HEAD {head[:12]} is not the kit's frozen commit {kit['frozen']['commit'][:12]}")
    bad = []
    for path, expected in sorted(kit["frozen"]["paths"].items()):
        try:
            got = hashlib.sha256((checkout / path).read_bytes()).hexdigest()
        except OSError:
            got = None
        if got != expected:
            bad.append(path)
    if bad:
        raise SpanRefusal(f"frozen paths differ from the kit in the working tree: {bad[:5]}")
    if require_clean and git_read("status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=none"):
        raise SpanRefusal("measurement checkout is dirty")
    return {"rc": 0, "head": head, "paths": len(kit["frozen"]["paths"])}


def production_deps(*, inputs, pmset_bin, output, scripted_ctl=False):
    from scripts import align_r1_rehearsal as r1, launch_align_r0 as launcher, run_align_r1_smoke as smoke
    leg_argv = leg_runtime_argv(inputs)
    workload_groups = []
    if scripted_ctl:
        leg_argv.insert(3, "--scripted-ctl")

    def run_soak(soak_dir, cap_s, feeds, work_remaining):
        argv = [sys.executable, "-B", str(ROOT / "scripts/cadence_legs_runner.py"), "soak-child",
                "--output", str(soak_dir), "--inputs", str(inputs)]
        soak_dir = Path(soak_dir)
        attempt = 1 + sum(1 for p in soak_dir.parent.iterdir() if p.name.startswith(soak_dir.name + ".rejected"))
        result = run_child(name="soak" if attempt == 1 else f"soak.a{attempt}", argv=argv, cap_s=cap_s,
                           log_dir=output, feeds=feeds, work_remaining=work_remaining, workload_groups=workload_groups)
        if result["rc"] == SOAK_REFUSED_RC:
            raise SoakRefusal(f"soak exit {result['rc']}: the idle soak failed its settle or quiet check")
        if result["rc"]:
            raise SpanRefusal(f"soak exit {result['rc']}")
        reference = Path(soak_dir) / "soak_reference.json"
        if not reference.is_file():
            raise SpanRefusal("the fresh soak wrote no soak reference")
        return reference

    def run_leg(attempt_dir, spec_path, soak_reference, cap_s, feeds, work_remaining, span_reference=None,
                *, ctl_spec_sha256=None):
        argv = [*leg_argv, "--leg-spec", str(spec_path), "--r1-kind", legsmod.LEG_KIND,
                "--output", str(attempt_dir), "--soak-reference", str(soak_reference),
                *(["--span-reference", str(span_reference)] if span_reference is not None else []),
                *(["--leg-spec-sha256", ctl_spec_sha256] if scripted_ctl else [])]
        leg_dir = Path(attempt_dir).parent
        attempt = 1 + sum(1 for p in leg_dir.iterdir() if p.name.startswith(Path(attempt_dir).name + ".rejected"))
        result = run_child(name=f"{leg_dir.name}.a{attempt}", argv=argv, cap_s=cap_s, log_dir=leg_dir,
                           feeds=feeds, work_remaining=work_remaining, workload_groups=workload_groups)
        if result["rc"]:
            raise LegRuntimeError(f"{Path(attempt_dir).parent.name}: leg runtime exit {result['rc']}")
        if not scripted_ctl:
            return accepted_result(attempt_dir)

    def load_verdict(name, result, wall_s):
        try:
            return r1.os_load_verdict(name, result, wall_s=wall_s)
        except r1.Refusal as error:
            raise LegRuntimeError(f"{name}: {error}") from error

    feeds = [smoke.AgentFeed(output), smoke.MeterFeed(output), smoke.VolumeFeed(output)]
    return Deps(clock=RealClock(), feeds=feeds, host=ProductionHost(pmset_bin), run_soak=run_soak,
                run_leg=run_leg, verify_frozen=verify_frozen_production, load_verdict=load_verdict,
                soak_cap_s=launcher.r1_soak_cap_s(), workload_groups=workload_groups)


# --------------------------------------------------------------------------
# The span
# --------------------------------------------------------------------------
def _parse_t0_anchor(raw):
    fields = raw.split(":")
    if len(fields) != 3 or not all(field.isascii() and field.isdecimal() for field in fields):
        raise argparse.ArgumentTypeError("expected epoch_ns:monotonic_before_ns:monotonic_after_ns")
    epoch_ns, before_ns, after_ns = map(int, fields)
    if epoch_ns <= 0 or before_ns > after_ns:
        raise argparse.ArgumentTypeError("t0 anchor needs a positive epoch and ordered monotonic readings")
    return epoch_ns, before_ns, after_ns


def add_t0_authority_arguments(parser):
    parser.add_argument("--authorized-t0-date", help="authorized America/Los_Angeles calendar date")
    parser.add_argument("--t0-not-before", type=int, help="inclusive earliest start in whole epoch seconds")
    parser.add_argument("--t0-not-before-ns", type=int, help="additional inclusive close bound in epoch nanoseconds")
    parser.add_argument("--t0-before", type=int, help="exclusive start cutoff in whole epoch seconds")
    parser.add_argument("--t0-anchor", type=_parse_t0_anchor,
                        help="arm clock sample as epoch_ns:monotonic_before_ns:monotonic_after_ns")


def validate_t0_authority(kit, authorized_date, t0_not_before, t0_before, t0_anchor, *, require_anchor,
                          t0_not_before_ns=None):
    if kit.get("runner", {}).get("kind") == ctl.RUNNER_KIND:
        if any(value is not None for value in (authorized_date, t0_not_before, t0_before)):
            raise ValueError("ctl has free t0; use the exact close bound without calendar t0 arguments")
        if type(t0_not_before_ns) is not int or t0_not_before_ns <= 0:
            raise ValueError("ctl requires a positive --t0-not-before-ns from the proven close")
        if require_anchor and t0_anchor is None:
            raise ValueError("ctl requires the arm clock anchor from the launcher")
        return
    qualification = kit["seed_law"]["method"] == QUAL_LAW
    if not qualification and all(value is None for value in
                                 (authorized_date, t0_not_before, t0_before, t0_anchor, t0_not_before_ns)):
        return
    if authorized_date is None or t0_not_before is None or t0_before is None:
        raise ValueError("authorized t0 date, earliest start and exclusive cutoff are required together")
    if date.fromisoformat(authorized_date).isoformat() != authorized_date:
        raise ValueError("authorized t0 date must use YYYY-MM-DD")
    if not 0 < t0_not_before < t0_before:
        raise ValueError("t0 bounds must satisfy 0 < earliest start < exclusive cutoff")
    if t0_not_before_ns is not None and not 0 < t0_not_before_ns < t0_before * NS_PER_SECOND:
        raise ValueError("exact close bound must be positive and below the exclusive cutoff")
    if require_anchor and t0_anchor is None:
        raise ValueError("authorized t0 requires the arm clock anchor from the launcher")


def _authorized_start(clock, authorized_date, t0_not_before, t0_before, anchor, t0_not_before_ns=None):
    wall_ns, continuous_ns = clock.epoch_and_monotonic_ns()
    anchor_epoch_ns, before_ns, after_ns = anchor
    if continuous_ns < after_ns:
        return None
    # The arm wall read occurred somewhere between the two monotonic reads.
    # Require the full projected interval to fit even if the sampler was preempted.
    earliest_ns = anchor_epoch_ns + continuous_ns - after_ns
    latest_ns = anchor_epoch_ns + continuous_ns - before_ns
    lower_ns = max((t0_not_before or 0) * NS_PER_SECOND, t0_not_before_ns or 0)
    for epoch_ns in (earliest_ns, latest_ns, wall_ns):
        if epoch_ns < lower_ns:
            return None
        if authorized_date is not None:
            if epoch_ns >= t0_before * NS_PER_SECOND:
                return None
            second = epoch_ns // NS_PER_SECOND
            day = (UNIX_EPOCH + timedelta(seconds=second)).astimezone(legsmod.LOCAL_ZONE).date()
            if day.isoformat() != authorized_date:
                return None
    t0_ns = (earliest_ns + latest_ns) // 2
    epoch_s = t0_ns / NS_PER_SECOND
    # Keep the legacy numeric seconds in the same whole second as the exact stamp.
    if math.floor(epoch_s) > t0_ns // NS_PER_SECOND:
        epoch_s = math.nextafter(epoch_s, -math.inf)
    return {"epoch_s": epoch_s, "epoch_ns": t0_ns, "continuous_ns": continuous_ns,
            "monotonic_ns": int(clock.monotonic() * NS_PER_SECOND)}


def run_span(*, kit, kit_sha256, output, deadline, windows, deps, leg_ids=None,
             authorized_t0_date=None, t0_not_before=None, t0_before=None, t0_anchor=None,
             t0_not_before_ns=None, span_id=None):
    """Run one span. Returns the receipt's rc (0 = every roster leg attempted, cleanup proven)."""
    clock = deps.clock
    authority = {}
    scripted_ctl = kit["runner"]["kind"] == ctl.RUNNER_KIND
    ctl_start = scripted_ctl and (not deps.mock or t0_not_before_ns is not None or t0_anchor is not None)
    if ctl_start:
        try:
            validate_t0_authority(kit, authorized_t0_date, t0_not_before, t0_before, t0_anchor,
                                  require_anchor=True, t0_not_before_ns=t0_not_before_ns)
        except ValueError as error:
            print(f"REFUSE: {error}", file=sys.stderr)
            return 3
    if authorized_t0_date is not None or ctl_start:
        started = _authorized_start(clock, authorized_t0_date, t0_not_before, t0_before, t0_anchor,
                                    t0_not_before_ns)
        if started is None:
            scope = (f" for {authorized_t0_date} within [{t0_not_before}, {t0_before})"
                     if authorized_t0_date is not None else "")
            print(f"REFUSE: t0 clocks must agree on authority{scope} "
                  f"with exact close bound {t0_not_before_ns}", file=sys.stderr)
            return 3
        authority = {"t0_authority": {}}
        if authorized_t0_date is not None:
            authority["t0_authority"].update(authorized_t0_date=authorized_t0_date,
                                             t0_not_before=t0_not_before, t0_before=t0_before)
        if t0_not_before_ns is not None:
            authority["t0_authority"]["t0_not_before_ns"] = t0_not_before_ns
    else:
        started = _stamp(clock)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)   # create-once: a retry cannot overwrite a span
    stages = legsmod.StageJournal(output / legsmod.STAGE_JOURNAL, clock)
    record = {"schema": RECEIPT_SCHEMA, "runner_kind": kit["runner"]["kind"], "mock": deps.mock,
              "started": started, "deadline": deadline, "work_reserve_s": WORK_RESERVE_S,
              "kit": {"campaign_id": kit["campaign_id"], "sha256": kit_sha256, "frozen_commit": kit["frozen"]["commit"]},
              "roster": list(leg_ids) if leg_ids is not None else [leg["leg_id"] for leg in kit["legs"]],
              "batch_windows": [legsmod.format_window(w) for w in windows], "steps": [], "legs": [],
              "soak_attempts": [], "feeds": {}, "rc": 0, **authority}
    if deps.workload_groups is not None:
        record["workload_groups"] = deps.workload_groups
    if span_id is not None:
        record["span_id"] = span_id
    state = {"power_read": False, "plan": None, "summaries": [], "finished": 0, "fault": False, "redos": 0}
    kit_legs = {leg["leg_id"]: leg for leg in kit["legs"]}
    result_keep = _RESULT_KEEP_CTL if scripted_ctl else _RESULT_KEEP

    def work_remaining():
        remaining = deadline - WORK_RESERVE_S - clock.time()
        if remaining <= 0:
            raise SpanRefusal("work deadline reached; cleanup reserve retained", 3)
        return remaining

    def poll():
        for feed in deps.feeds:
            feed.poll()

    def wait(seconds):
        until = clock.monotonic() + seconds
        while clock.monotonic() < until:
            work_remaining()
            poll()
            clock.sleep(min(POLL_S, max(0.0, until - clock.monotonic())))
        return seconds

    def step(name, operation, *, fatal=True, kind="host", cap_s=None, keep=None):
        row = {"name": name, "started": _stamp(clock), "rc": None}
        record["steps"].append(row)
        started = stages.start(name, kind, cap_s)
        try:
            result = operation() or {}
            shown = {k: result[k] for k in keep if k in result} if keep else result
            row.update(rc=result.get("rc", 0) if isinstance(result, dict) else 0,
                       result=shown if isinstance(result, dict) else {"value": str(result)})
            if fatal and row["rc"]:
                raise SpanRefusal(f"{name}: rc {row['rc']}", row["rc"])
            return result
        except BaseException as exc:
            code = exc.code if isinstance(exc, (SpanRefusal, SystemExit)) and isinstance(exc.code, int) else 2
            row.update(rc=code, error=f"{type(exc).__name__}: {exc}")
            raise
        finally:
            row["ended"] = _stamp(clock)
            stages.end(name, kind, row["rc"], started, cap_s)

    def interrupted(signum, _frame):
        raise SystemExit(128 + signum)

    def before_part(label):
        for feed in deps.feeds:
            if hasattr(feed, "before_part"):
                step(f"before-{label}-{feed.name}", feed.before_part)

    def run_leg(spec, soak_reference):
        leg_id = spec["leg_id"]
        budget, cap = spec["budget_s"], state["plan"]["leg_cap_s"]
        leg_dir = output / "legs" / leg_id
        leg_dir.mkdir(parents=True)
        spec_path = leg_dir / "leg_spec.json"
        leg_input = {k: spec[k] for k in legsmod.leg_spec_keys(spec)}
        spec_path.write_text(json.dumps(leg_input, indent=1, sort_keys=True) + "\n")
        # A span-reference consumer reads the span's reference from the span's first leg's accepted
        # attempt (RL-150 R1 part 2; design doc section 14.5). The runtime verifies it with W1's verifier.
        span_kw = {}
        if spec.get("g0_role") == "consume":
            first = state["plan"]["legs"][0]["leg_id"]
            span_kw["span_reference"] = output / "legs" / first / "runtime"
            # Which attempt of the first leg supplies the reference, read by the hand-read's marks
            # (RL-158 Q2: a redo's capture; RL-161 section 4: a first leg that was not admitted).
            supplier = len(record["legs"][0]["attempts"])
            leg_row_source = {"leg_id": first, "dir": str(span_kw["span_reference"].relative_to(output)),
                              "attempt": supplier, "redone": supplier > 1,
                              "excluded": not state["summaries"][0]["admitted"]}
        else:
            leg_row_source = None
        if scripted_ctl:
            span_kw["ctl_spec_sha256"] = ctl.leg_spec_sha256(leg_input)
        attempts, result, first_start = [], None, None
        leg_row = {"leg_id": leg_id, "attempts": attempts, "budget_s": budget,
                   **({"span_reference": leg_row_source} if leg_row_source else {})}
        record["legs"].append(leg_row)
        while True:
            delay = legsmod.leg_start_delay(clock.time(), windows)
            if delay:
                step(f"{leg_id}-blackout-wait", lambda: {"rc": 0, "waited_s": wait(delay)}, kind="wait", cap_s=delay)
            before_part(leg_id)
            attempt_dir = leg_dir / "runtime"
            n = len(attempts) + 1
            started = clock.time()
            first_start = first_start if first_start is not None else started
            def execute_leg():
                produced = deps.run_leg(attempt_dir, spec_path, soak_reference, cap,
                                        deps.feeds, work_remaining, **span_kw)
                return accepted_result(attempt_dir, ctl_spec=leg_input) if scripted_ctl else produced

            result = step(f"{leg_id}.a{n}", execute_leg, kind="leg", cap_s=cap, keep=result_keep)
            ended = clock.time()
            verdict = deps.load_verdict(leg_id, result, ended - started)
            attempt = {"attempt": n, "started_epoch_s": started, "ended_epoch_s": ended, "wall_s": ended - started,
                       "os_batch_wait_s": delay, "contaminated": bool(verdict["redo"]),
                       "redo_reason": "cpu_load" if verdict["redo"] else None, "redone": False,
                       "os_load": {k: verdict.get(k) for k in ("seconds", "max_busy_cores", "max_gap_s")},
                       "leg_status": result.get("leg_status"), "output_dir": str(attempt_dir.relative_to(output))}
            attempts.append(attempt)
            if attempt["contaminated"] and state["redos"] < state["plan"]["redo_quota"]:
                rejected = leg_dir / f"runtime.rejected{n}"
                attempt_dir.rename(rejected)
                attempt.update(redone=True, output_dir=str(rejected.relative_to(output)))
                state["redos"] += 1
                continue
            break
        cell = None
        if "g0_shape" in kit_legs[leg_id]:   # kit v1.1: the cell and the G0 reference go to the desk
            cell = {"prefill_tokens": spec["prefill_tokens"], "g0_shape": kit_legs[leg_id]["g0_shape"],
                    "g0_role": spec.get("g0_role", "capture"),
                    "span_reference": ({k: leg_row_source[k] for k in ("leg_id", "attempt", "redone", "excluded")}
                                       if leg_row_source else None)}
        summary = legsmod.leg_summary(spec=spec, budget_s=budget, attempts=attempts, accepted=result,
                                      started_epoch_s=first_start, ended_epoch_s=clock.time(), cell=cell)
        leg_row["summary"] = summary
        (leg_dir / "leg_record.json").write_text(json.dumps(
            {"schema": LEG_RECORD_SCHEMA, "spec": spec, "attempts": attempts,
             "result": {k: result[k] for k in result_keep if k in result}},
            indent=1, sort_keys=True) + "\n")
        (leg_dir / "leg_summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
        state["summaries"].append(summary)
        state["finished"] += 1

    def run_soak():
        # RL-171: one retry of a soak that failed its settle or quiet check. The retry starts only if it and
        # every roster leg plus the redo quota at the leg cap still fit (the launch deadline budgets it).
        attempts = record["soak_attempts"]
        while True:
            n = len(attempts) + 1
            name = "soak" if n == 1 else f"soak.a{n}"
            delay = legsmod.interval_delay(clock.time(), deps.soak_cap_s, windows)
            if delay:
                step(f"{name}-blackout-wait", lambda: {"rc": 0, "waited_s": wait(delay)}, kind="wait", cap_s=delay)
            before_part(name)
            attempt = {"attempt": n, "started_epoch_s": clock.time(), "refused": None, "output_dir": "soak"}
            attempts.append(attempt)
            try:
                return step(name, lambda: {"rc": 0, "path": str(deps.run_soak(
                    output / "soak", deps.soak_cap_s, deps.feeds, work_remaining))}, kind="soak",
                    cap_s=deps.soak_cap_s)["path"]
            except SoakRefusal as refusal:
                attempt["refused"] = str(refusal)
                if n > SOAK_RETRIES:
                    raise
                plan = state["plan"]
                need = deps.soak_cap_s + (len(plan["legs"]) + plan["redo_quota"]) * plan["leg_cap_s"]
                if clock.time() + need > deadline - WORK_RESERVE_S:
                    raise SoakRefusal(f"{refusal}; no retry: it needs {need:.0f} s and the work deadline leaves "
                                      f"{deadline - WORK_RESERVE_S - clock.time():.0f} s") from refusal
                if (output / "soak").exists():
                    rejected = output / f"soak.rejected{n}"
                    (output / "soak").rename(rejected)
                    attempt["output_dir"] = rejected.name

    handlers = {s: signal.signal(s, interrupted) for s in SIGNALS}
    try:
        step("deadline", lambda: {"rc": 0, "remaining_s": work_remaining()})
        step("frozen", lambda: deps.verify_frozen(kit))
        step("night_agents", deps.host.night_agents)
        step("ac_power", deps.host.ac_power)
        step("condition13", deps.host.condition13)
        for feed in deps.feeds:
            step("start-" + feed.name, feed.start)

        def read_power():
            result = deps.host.read_power()
            state["power_read"] = True
            return result
        step("read_power", read_power)
        step("display", deps.host.display, fatal=False)
        step("dwell", lambda: {"rc": 0, "dwell_s": wait(deps.host.dwell_s())})

        def plan():
            # The plan is the span's, from its start (the launcher sized --deadline from the same kit
            # and roster at the arm). What must still fit now is the rest: the soak and every roster leg
            # plus the redo quota at the leg cap. Preflight and dwell were budgeted in fixed_overhead_s;
            # the close is inside the work reserve.
            value = legsmod.plan_span(kit, t0_epoch=record["started"]["epoch_s"], windows=windows, leg_ids=leg_ids,
                                      max_span_s=deps.max_span_s if deps.max_span_s is not None else max_span_s())
            need = value["soak_s"] + (len(value["legs"]) + value["redo_quota"]) * value["leg_cap_s"]
            if clock.time() + need > deadline - WORK_RESERVE_S:
                raise SpanRefusal(f"plan needs {need:.0f} s from now; the work deadline leaves "
                                  f"{deadline - WORK_RESERVE_S - clock.time():.0f} s")
            if kit["span_template"]["soak_s"] < deps.soak_cap_s:
                raise SpanRefusal(f"kit soak_s {kit['span_template']['soak_s']} < the soak cap {deps.soak_cap_s:g} s")
            state["plan"] = value
            (output / PLAN_NAME).write_text(json.dumps(value, indent=1, sort_keys=True) + "\n")
            return {"rc": 0, "deadline_epoch_s": value["deadline_epoch_s"], "worst_case_s": value["worst_case_s"],
                    "expected_s": value["expected_s"], "legs": [leg["leg_id"] for leg in value["legs"]]}
        step("plan", plan)

        soak_reference = run_soak()
        record["soak_reference"] = soak_reference
        for spec in state["plan"]["legs"]:
            run_leg(spec, soak_reference)
    except BaseException as exc:
        record.update(rc=exc.code if isinstance(exc, (SpanRefusal, SystemExit)) and isinstance(exc.code, int) else 2,
                      error=f"{type(exc).__name__}: {exc}")
    finally:
        for s in SIGNALS:
            signal.signal(s, signal.SIG_IGN)
        try:
            _close(record, state, deps, output, step, kit)
        finally:
            for s, handler in handlers.items():
                signal.signal(s, handler)
    return record["rc"]


# Leg-record fields copied from the runtime result (operational; never energy).
_RESULT_KEEP = ("leg_id", "leg_status", "bundle", "member_status", "g0_outcome", "g0_released", "g0_wait_s",
                "g0_timeout_s", "quiet_s", "prefill_chars", "prefill_tokens", "decode_cap", "decode_tokens",
                "decode_cap_reached", "os_level_max", "pm_nominal", "incomplete_reasons", "ac_powermode",
                "turn_start_ns", "turn_end_ns", "first_token_ns", "quiet_spans_ns", "config_sha256",
                "g0_shape", "g0_role", "g0_reference_source", "g0_reference_record_sha256")
_RESULT_KEEP_CTL = _RESULT_KEEP + ("script_complete", "script_record_sha256")


def _close(record, state, deps, output, step, kit):
    def stop_feed(feed):
        result = feed.stop()
        if feed.name == "meter" and "group" in result:
            # The supervisor starts each generation in its own session.
            process = getattr(getattr(feed, "supervisor", None), "process", None)
            if process is not None:
                result = {**result, "group": {**result["group"], "pgid": process.pid}}
        return result

    cleanup = [("restore", lambda: deps.host.restore_power(state["power_read"])),
               *(("stop-" + f.name, lambda feed=f: stop_feed(feed)) for f in reversed(deps.feeds))]
    for name, operation in cleanup:
        try:
            result = step(name, operation, kind="close")
            if name.startswith("stop-"):
                record["feeds"].setdefault(name[5:], {})["stop"] = result
        except BaseException:
            record["rc"] = record["rc"] or 2
            state["fault"] = state["fault"] or name.startswith("stop-")
    for feed in deps.feeds:
        if hasattr(feed, "close"):
            try:
                step("close-" + feed.name, feed.close, kind="close")
            except BaseException:
                record["rc"] = record["rc"] or 2
    meter_files = []
    for feed in deps.feeds:
        files = []
        try:
            for path in feed.files():
                if path.is_file():
                    with path.open("rb") as handle:
                        files.append({"path": path.relative_to(output).as_posix(),
                                      "sha256": hashlib.file_digest(handle, "sha256").hexdigest()})
                    if feed.name == "meter" and path.name.startswith("stream-"):
                        meter_files.append(path)
        except Exception as exc:  # noqa: BLE001 - recorded; the receipt is still written
            record["rc"] = record["rc"] or 2
            record["feeds"].setdefault(feed.name, {})["error"] = str(exc)
        record["feeds"].setdefault(feed.name, {})["files"] = files
    meter_feed = next((f for f in deps.feeds if f.name == "meter"), None)
    try:
        meter = legsmod.meter_health(meter_files, started=meter_feed is not None,
                                     stop_record=(record["feeds"].get("meter") or {}).get("stop"))
    except Exception as exc:  # noqa: BLE001
        meter = {"present": False, "proven_stopped": False}
        record["meter_health_error"] = str(exc)
    planned = len(state["plan"]["legs"]) if state["plan"] else len(record["roster"])
    result = legsmod.span_result(rc=record["rc"], planned=planned, finished=state["finished"], fault=state["fault"])
    record.update(span_result=result, meter=meter, legs_finished=state["finished"], legs_planned=planned,
                  load_redos_used=state["redos"])
    try:
        legsmod.write_desk_bundle(output / DESK_BUNDLE, summaries=state["summaries"], result=result, meter=meter)
    except Exception as exc:  # noqa: BLE001
        record["rc"] = record["rc"] or 2
        record["desk_bundle_error"] = f"{type(exc).__name__}: {exc}"
    record["ended"] = _stamp(deps.clock)
    if "span_id" in record:
        epoch_ns, _ = deps.clock.epoch_and_monotonic_ns()
        record["ended"].update(epoch_ns=epoch_ns, epoch_s=epoch_ns / NS_PER_SECOND)
    with (output / RECEIPT_NAME).open("x") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


# --------------------------------------------------------------------------
# Mock: the whole span without the MBP
# --------------------------------------------------------------------------
class FakeClock:
    def __init__(self, epoch):
        self.t = float(epoch)
        self.m = 1000.0

    def time(self):
        return self.t

    def monotonic(self):
        return self.m

    def epoch_and_monotonic_ns(self):
        return int(Decimal(str(self.t)) * NS_PER_SECOND), round(self.m * NS_PER_SECOND)

    def sleep(self, seconds):
        self.t += seconds
        self.m += seconds


class FakeHost:
    def __init__(self):
        self.calls = []
        self.mode = 0

    def _ok(self, name, **extra):
        self.calls.append(name)
        return {"rc": 0, "mock": True, **extra}

    def night_agents(self):
        return self._ok("night_agents")

    def ac_power(self):
        return self._ok("ac_power")

    def condition13(self):
        return self._ok("condition13")

    def read_power(self):
        return self._ok("read_power", ac_powermode=self.mode)

    def restore_power(self, power_read):
        return self._ok("restore", action="restore_automatic" if power_read else "no_power_read")

    def display(self):
        return self._ok("display")

    def dwell_s(self):
        return 300.0


class FakeFeed:
    def __init__(self, name, output, clock, meter=False):
        self.name, self.output, self.clock, self.meter = name, Path(output), clock, meter
        self.events, self.polls = [], 0
        self.path = self.output / ("hazards/meter/stream-0001.jsonl" if meter else f"mock-{name}.jsonl")

    def start(self):
        self.events.append("start")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.started_at = self.clock.time()
        if self.meter:   # header only; samples are never written by the mock
            self.path.write_text(json.dumps({"k": "h", "status": "streaming", "mock": True}) + "\n")
        else:
            self.path.write_text("")
        return {"rc": 0}

    def poll(self):
        self.polls += 1

    def before_part(self):
        self.events.append("before_part")
        return {"rc": 0}

    def stop(self):
        self.events.append("stop")
        if self.meter and self.path.is_file():
            elapsed = self.clock.time() - self.started_at
            with self.path.open("a") as handle:
                handle.write(json.dumps({"k": "t", "polls": int(elapsed * 10), "bad": 0, "usb_errors": 0,
                                         "empties": 0, "elapsed_s": elapsed}) + "\n")
        return {"rc": 0, "proven_stopped": True}

    def files(self):
        return [self.path]


class FakeLegRuntime:
    """A deterministic stand-in for the leg runtime: advances the fake clock by the time model with a
    seed-derived G0 and writes a result with the real result's operational fields and journals."""

    def __init__(self, clock, *, contaminate=(), g0_timeout=(), contaminate_attempts=1, soak_refusals=0):
        self.clock = clock
        self.contaminate, self.g0_timeout = set(contaminate), set(g0_timeout)
        self.contaminate_attempts = contaminate_attempts
        self.soak_refusals = soak_refusals     # how many soaks, from the first, fail their settle or quiet check
        self.calls = []
        self.soaks = 0
        self.span_references = []

    def soak(self, soak_dir, cap_s, feeds, work_remaining):
        Path(soak_dir).mkdir(parents=True)
        self.clock.sleep(1800 + 30)
        self.soaks += 1
        if self.soaks <= self.soak_refusals:
            raise SoakRefusal(f"soak exit {SOAK_REFUSED_RC}: the idle soak failed its settle or quiet check (mock)")
        path = Path(soak_dir) / "soak_reference.json"
        path.write_text(json.dumps({"schema": "joulewise.align.r1_soak_reference.v1", "mock": True}) + "\n")
        return path

    def leg(self, attempt_dir, spec_path, soak_reference, cap_s, feeds, work_remaining, span_reference=None,
            *, ctl_spec_sha256=None):
        from joulewise.align.apple import r1_runtime as rt
        spec = legsmod.validate_leg_spec(json.loads(Path(spec_path).read_text()))
        leg_id = spec["leg_id"]
        role = spec.get("g0_role", "capture")
        # The runtime's refusals: a consumer needs the span's first leg's accepted attempt; a capture takes none.
        if (role == "consume") != (span_reference is not None) or (
                span_reference is not None and not (Path(span_reference) / rt.RESULT_NAME).is_file()):
            raise LegRuntimeError(f"{leg_id}: leg runtime exit {rt.EXIT_REFUSED} (span reference)")
        n = sum(1 for c in self.calls if c == leg_id) + 1
        self.calls.append(leg_id)
        self.span_references.append((leg_id, None if span_reference is None else Path(span_reference)))
        Path(attempt_dir).mkdir(parents=True)
        timeout = leg_id in self.g0_timeout
        g0 = 1200.0 if timeout else 90.0 + spec["seed"] % 240 + (300.0 if role == "consume" else 0.0)
        wall = legsmod.leg_expected_s(spec) - legsmod.leg_g0_s(spec) + g0
        if timeout:
            wall -= spec["quiet_s"] + spec["prefill_tokens"] * 0.005 + spec["decode_tokens"] / 12.03
        if work_remaining() < wall:
            raise SpanRefusal(f"{leg_id}: mock leg would overrun the work deadline", 3)
        busy = 0.9 if (leg_id in self.contaminate and n <= self.contaminate_attempts) else 0.1
        seconds = int(wall)
        self.clock.sleep(wall)
        result = {"schema": rt.RESULT_SCHEMA, "kind": legsmod.LEG_KIND, "backend": "mock", "leg_id": leg_id,
                  "leg_status": "g0_unreleased" if timeout else "complete", "bundle": f"runs/mock-{leg_id}",
                  "member_status": "succeeded", "g0_outcome": "timeout" if timeout else "released",
                  "g0_released": not timeout, "g0_wait_s": g0, "g0_timeout_s": 1200, "quiet_s": spec["quiet_s"],
                  "prefill_chars": spec["prefill_chars"], "prefill_tokens": None if timeout else spec["prefill_tokens"],
                  "decode_cap": spec["decode_tokens"], "decode_tokens": None if timeout else spec["decode_tokens"],
                  "decode_cap_reached": not timeout, "os_level_max": 0, "pm_nominal": True,
                  "episode_flags": [], "incomplete_reasons": [], "ac_powermode": {"value": 0},
                  "g0_shape": spec.get("g0_shape", "own"), "g0_role": role,
                  "g0_reference_source": (f"mock-{Path(span_reference).parent.name}" if role == "consume"
                                          else f"mock-{leg_id}"),
                  "g0_reference_record_sha256": "e" * 64 if role == "consume" else None,
                  "cpu_busy_cores": [busy] * seconds, "cpu_busy_t_s": [float(i) for i in range(seconds)],
                  "census": [{"mock": True}]}
        legsmod.guard_projection(result, "mock leg result", values=False)
        result_path = Path(attempt_dir) / rt.RESULT_NAME
        if ctl_spec_sha256 is not None:
            if ctl.leg_spec_sha256(spec) != ctl_spec_sha256:
                raise LegRuntimeError(f"{leg_id}: ctl leg spec differs from the span plan")
            steps = []
            stamp = 0
            if not timeout:
                for kind, dose in ctl.script_steps(spec["script"]):
                    fields = ({"requested_tokens": dose, "actual_tokens": dose,
                               "context_tokens": spec["prefill_tokens"], "cached_prompt_tokens": 0,
                               "first_token_ns": stamp}
                              if kind in ("hidden", "turn") else {"requested_s": dose})
                    elapsed = ctl.duration_ns(dose) if "requested_s" in fields else 1
                    if kind == "cpu":
                        fields["thread_cpu_ns"] = elapsed
                    steps.append({"kind": kind, "started_ns": stamp, "ended_ns": stamp + elapsed,
                                  "complete": True, **fields})
                    stamp += elapsed
                visible = [row for row in steps if row["kind"] == "turn"]
                result.update(turn_start_ns=visible[0]["started_ns"], first_token_ns=visible[0]["first_token_ns"],
                              turn_end_ns=visible[-1]["ended_ns"], prefill_tokens=sum(r["context_tokens"] for r in visible))
            work = {"schema": ctl.WORK_SCHEMA, "leg_id": leg_id, "leg_spec_sha256": ctl_spec_sha256,
                    "script": spec["script"], "complete": not timeout, "steps": steps}
            work_raw = (json.dumps(work, sort_keys=True) + "\n").encode()
            (result_path.parent / ctl.WORK_NAME).write_bytes(work_raw)
            result.update(script_complete=not timeout, script_record_sha256=hashlib.sha256(work_raw).hexdigest())
            result_raw = (json.dumps(result, sort_keys=True) + "\n").encode()
            result_path.write_bytes(result_raw)
            files = {rt.RESULT_NAME: hashlib.sha256(result_raw).hexdigest(), ctl.WORK_NAME: result["script_record_sha256"]}
            (result_path.parent / rt.CUSTODY_NAME).write_text(
                json.dumps({"schema": rt.CUSTODY_SCHEMA, "status": "complete", "files": files}) + "\n")
        else:
            result_path.write_text(json.dumps(result, sort_keys=True) + "\n")
        return result


def mock_load_verdict(name, result, wall_s):
    from scripts import align_r1_rehearsal as r1
    return r1.os_load_verdict(name, result, wall_s=wall_s)


def mock_deps(output, clock, *, contaminate=(), g0_timeout=(), soak_refusals=0):
    fake = FakeLegRuntime(clock, contaminate=contaminate, g0_timeout=g0_timeout, soak_refusals=soak_refusals)
    feeds = [FakeFeed("agents", output, clock), FakeFeed("meter", output, clock, meter=True),
             FakeFeed("volumes", output, clock)]
    deps = Deps(clock=clock, feeds=feeds, host=FakeHost(), run_soak=fake.soak, run_leg=fake.leg,
                verify_frozen=lambda kit: {"rc": 0, "skipped": "mock (no measurement checkout)"},
                load_verdict=mock_load_verdict, soak_cap_s=1950.0, mock=True)
    deps.fake = fake
    return deps


def run_mock(*, kit, kit_sha256, output, t0_epoch, windows, leg_ids=None, contaminate=(), g0_timeout=(),
             soak_refusals=0):
    """A whole span with the fake clock, feeds and leg runtime, then the Air desk on its bundle."""
    from joulewise.cadence import desk
    output = Path(output)
    clock = FakeClock(t0_epoch)
    deps = mock_deps(output, clock, contaminate=contaminate, g0_timeout=g0_timeout, soak_refusals=soak_refusals)
    deps.max_span_s = max_span_s()
    plan = legsmod.plan_span(kit, t0_epoch=t0_epoch, windows=windows, leg_ids=leg_ids, max_span_s=deps.max_span_s)
    rc = run_span(kit=kit, kit_sha256=kit_sha256, output=output, deadline=launch_deadline(plan), windows=windows,
                  deps=deps, leg_ids=leg_ids)
    summary, stops = desk.build_desk(plan_id=f"mock-{kit['campaign_id']}", input_dir=output / DESK_BUNDLE,
                                     out_dir=output / "desk", adapter=kit["desk"]["adapter"],
                                     stop_rules=kit["stop_rules"], now=clock.time())
    return rc, summary, stops, deps


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def _windows(args):
    """``--batch-window`` if given (backward compatibility), else none (RL-171)."""
    if args.batch_window:
        return [legsmod.parse_window(args.batch_window)]
    return default_windows()


def _roster(args):
    return args.legs.split(",") if args.legs else None


def _load(path):
    try:
        return kitmod.load_kit(path)
    except kitmod.KitError as error:
        for problem in error.problems:
            print(f"REFUSE {problem}", file=sys.stderr)
        raise SystemExit(1)


def soak_child(output, inputs):
    """The span's fresh soak: ``run_align_r1_smoke.soak_child`` (parts A and B) step for step, by import of the
    same functions, without its OS batch window check (RL-171; that file is on the Part C path and keeps it).

    Same condition-13 check, idle-soak invocation and contract, load verdict, settled-slope check and
    reference writer. An unsettled or loaded soak raises ``SoakQuietRefusal`` (exit SOAK_REFUSED_RC), the
    one refusal the span retries."""
    from joulewise.align.apple import v4_registration as reg
    from scripts import align_r1_rehearsal as r1, run_align_r1_smoke as smoke
    reg.verify_r1_executed_sources(ROOT, {"executed_commit": r1.executed_commit(ROOT)})
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    started = time.time_ns()
    result = r1._invoke(r1.runtime_argv_from_inputs(inputs), "idle", output / "idle_soak", smoke.soak_seconds(),
                        quiet=True, contract_key="idle_soak")
    row = {"name": "idle_soak", "class": "light", "started_ns": started, "ended_ns": time.time_ns(),
           "attempt": 0, "output_dir": str(output / "idle_soak"), "result": result}
    row["os_load"] = r1.os_load_verdict("idle_soak", result, wall_s=(row["ended_ns"] - started) / 1e9)
    row["soak_detrended"] = r1.soak_detrended(result.get("sensor_series_c"), result.get("sensor_series_t_s"),
                                              result.get("sensor_series_end_t_s"))
    (output / "soak_row.json").write_text(json.dumps(row, indent=2, sort_keys=True) + "\n")
    if not all(v["settled"] for v in row["soak_detrended"].values()):
        raise SoakQuietRefusal("idle soak has unresolved slope")
    if row["os_load"]["redo"]:
        raise SoakQuietRefusal("idle soak: sustained CPU load")
    return r1.write_soak_reference(output, row)


def pin_kit(path, commit, write=False):
    """Re-take every frozen path's sha256 at ``commit`` and set frozen.commit (the re-pin after review)."""
    raw = Path(path).read_text()
    doc = json.loads(raw)
    full = subprocess.run(["git", "-C", str(ROOT), "rev-parse", f"{commit}^{{commit}}"], capture_output=True,
                          text=True, check=True).stdout.strip()
    paths = {}
    for p in sorted(doc["frozen"]["paths"]):
        blob = subprocess.run(["git", "-C", str(ROOT), "cat-file", "blob", f"{full}:{p}"], capture_output=True,
                              check=True).stdout
        paths[p] = hashlib.sha256(blob).hexdigest()
    doc["frozen"] = {"commit": full, "paths": paths}
    text = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
    if write:
        Path(path).write_text(text)
    return doc, text


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "plan", "mock"):
        p = sub.add_parser(name)
        p.add_argument("--kit", type=Path, required=True)
        p.add_argument("--legs", help="the queue span's roster, comma-separated kit leg ids (default: all)")
        p.add_argument("--batch-window", help="HH:MM-HH:MM local blackout (default: none, RL-171)")
        if name == "run":
            p.add_argument("--kit-sha256", help="exact kit bytes approved by the ctl launcher")
            ctl.add_queue_authority_arguments(p)
            p.add_argument("--attempt-ledger", type=Path, help="ctl launch attempt ledger")
            p.add_argument("--output", type=Path, required=True)
            p.add_argument("--deadline", type=float, required=True)
            p.add_argument("--span-id", help="span identity carried into its close receipt")
            add_t0_authority_arguments(p)
            p.add_argument("--pmset-bin", default="/usr/bin/pmset")
            p.add_argument("--inputs", type=Path,
                           default=ROOT / "configs/campaigns/align_v4/registration/inputs.json")
        elif name == "plan":
            p.add_argument("--t0", type=float, help="epoch seconds (default: now)")
        else:
            p.add_argument("--output", type=Path, required=True)
            p.add_argument("--t0-local", help="local start, e.g. 2026-11-15T13:20 (default: now)")
            p.add_argument("--contaminate", default="", help="legs whose first attempt carries load")
            p.add_argument("--g0-timeout", default="", help="legs whose G0 times out")
            p.add_argument("--soak-refusals", type=int, default=0,
                           help="soaks, from the first, that fail their settle or quiet check")
    p = sub.add_parser("soak-child")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--inputs", type=Path, default=ROOT / "configs/campaigns/align_v4/registration/inputs.json")
    p = sub.add_parser("pin-kit")
    p.add_argument("kit", type=Path)
    p.add_argument("--commit", required=True)
    p.add_argument("--write", action="store_true")
    sub.add_parser("t0-anchor", help="sample the wall epoch bracketed by sleep-inclusive monotonic readings")
    args = parser.parse_args(argv)

    if args.command == "t0-anchor":
        print(":".join(map(str, RealClock.arm_anchor_ns())))
        return 0

    if args.command == "soak-child":
        try:
            soak_child(args.output.resolve(), args.inputs)
        except SoakQuietRefusal as refusal:
            print(f"soak refused: {refusal}", file=sys.stderr)
            return SOAK_REFUSED_RC
        return 0
    if args.command == "pin-kit":
        _, text = pin_kit(args.kit, args.commit, write=args.write)
        if not args.write:
            sys.stdout.write(text)
        return 0
    kit, sha = _load(args.kit)
    try:
        windows = _windows(args)
        if args.command == "plan":
            plan = legsmod.plan_span(kit, t0_epoch=args.t0 if args.t0 is not None else time.time(), windows=windows,
                                     leg_ids=_roster(args), max_span_s=max_span_s())
            print(json.dumps({**plan, "kit_sha256": sha, "soak_retry_budget_s": soak_retry_budget_s(plan),
                              "launch_deadline_epoch_s": launch_deadline(plan)}, indent=1, sort_keys=True))
            return 0
        if args.command == "mock":
            t0 = (datetime.fromisoformat(args.t0_local).replace(tzinfo=legsmod.LOCAL_ZONE).timestamp()
                  if args.t0_local else time.time())
            rc, summary, stops, _ = run_mock(kit=kit, kit_sha256=sha, output=args.output, t0_epoch=t0, windows=windows,
                                             leg_ids=_roster(args),
                                             contaminate=[x for x in args.contaminate.split(",") if x],
                                             g0_timeout=[x for x in args.g0_timeout.split(",") if x],
                                             soak_refusals=args.soak_refusals)
            print(json.dumps({"rc": rc, "legs": len(summary["legs"]), "stops": stops,
                              "receipt": str(args.output / RECEIPT_NAME),
                              "table": str(args.output / "desk" / "JOURNAL-TABLE.md")}, indent=1))
            return rc
    except legsmod.PlanError as error:
        for problem in error.problems:
            print(f"REFUSE {problem}", file=sys.stderr)
        return 1
    if not math.isfinite(args.deadline):
        parser.error("deadline must be finite")
    scripted_ctl = kit["runner"]["kind"] == ctl.RUNNER_KIND
    try:
        if scripted_ctl:
            ctl.require_issued(kit)
            if args.kit_sha256 != sha:
                raise ValueError("ctl kit hash differs from the launcher-approved kit")
            if args.span_id is None:
                raise ValueError("ctl requires --span-id from the launch ledger")
            from scripts import launch_cadence_span

            launch_cadence_span.verify_ctl_child(args, kit, sha, sys.modules[__name__])
        elif (args.kit_sha256 is not None or args.attempt_ledger is not None
              or any(getattr(args, key) is not None for key in ctl.QUEUE_AUTHORITY_FLAGS)):
            raise ValueError("launcher-approved ctl kit was replaced by a different runner kind")
        if args.span_id is not None and not SPAN_ID_PATTERN.fullmatch(args.span_id):
            raise ValueError("invalid --span-id")
        validate_t0_authority(kit, args.authorized_t0_date, args.t0_not_before, args.t0_before, args.t0_anchor,
                              require_anchor=True, t0_not_before_ns=args.t0_not_before_ns)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    output = args.output.resolve()
    deps = production_deps(inputs=args.inputs, pmset_bin=args.pmset_bin, output=output,
                           scripted_ctl=scripted_ctl)
    return run_span(kit=kit, kit_sha256=sha, output=output, deadline=args.deadline, windows=windows, deps=deps,
                    leg_ids=_roster(args), authorized_t0_date=args.authorized_t0_date,
                    t0_not_before=args.t0_not_before, t0_before=args.t0_before, t0_anchor=args.t0_anchor,
                    t0_not_before_ns=args.t0_not_before_ns, span_id=args.span_id)


if __name__ == "__main__":
    from joulewise.align.apple import powermode as _powermode
    _powermode.mark_production_entry(__file__)
    raise SystemExit(main())
