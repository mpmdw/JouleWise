#!/usr/bin/env python3
"""ALIGN v4 R1 rehearsal-window driver.

This is a non-claim qualification program intended to be the chain executed by
``run_night``.  The runtime command is deliberately an argv seam: WP15 owns
the production runtime/custody implementation and replaces that seam without
putting model logic in this driver.  The fields each runtime kind returns are
declared in ``joulewise/align/apple/r1_runtime_contract.py`` and
``docs/align/r1_runtime_contract.md`` and checked at the seam.
"""
from __future__ import annotations

import argparse
import hashlib
from contextlib import AbstractContextManager
from datetime import datetime, time as wall_time, timedelta
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Callable, Sequence
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align.apple import r1_runtime_contract as contract  # noqa: E402
from joulewise.align.apple.powermode import parse_ac_powermode  # noqa: E402,F401  (re-exported)
from joulewise.align.apple import external_volume  # noqa: E402
from joulewise.align.apple.r1_phase_table import (  # noqa: E402,F401  (re-exported)
    COOLDOWN_AFTER_D_MAX_S, GATED_D_RUNS, HIGH_POWER_LEGS,
    PLANNING_RUN_ORDER_C, PRECOOL_SUFFIX, STEP_D_NAME, phase_plan,
)

SCHEMA = "joulewise.align.r1_slots.v1"
SLOT_NAMES = tuple(f"S{i}" for i in range(1, 10)) + (
    "S5_fast", "B_D", "I_D", "T_dead", "N_chunk", "t_decline", "class",
)
PLANNING_START_OFFSETS_C = (0.0, 2.0, 4.0)
REPLAY_PAIR = ("D_spam_benign_s1_gated_held_a", "D_spam_benign_s1_gated_held_b")
PRECOOL_RETRY_SUFFIX = ".precool_retry"
G0_TIMEOUT_SUFFIX = ".g0_timeout1"
W1_PLAN_TEMPLATE = Path("configs/campaigns/align_v4/night_plan.template.json")   # = align_v4_kit.W1_PLAN_TEMPLATE
# The W1 roster role each R1 gated member stands for, and the R1 runtime
# config template it runs (R6-1: its configured idle must be W1's).
W1_SCHEDULE_ROLES = {"d_spam": "D", "d_bank": "D", "x_g": "X-G"}
DEADMAN_PHASES = ("G0", "G1", "H", "decode", "prefill", "tool", "tail")  # ruling 1(a)
# Ruling 1(d): pre-declared duty bar, fixed here before any R1 data are read.
DUTY_BAR = {"x7": False, "min_admitted_turns": 3, "max_gate_hold_fraction_of_T_dead": 0.40}
# RL-149 section 1.5 (cited rebind of ruling 1(d)'s turn check; DEVIATIONS RL149-DUTY-TURNS): a run
# that returned by its own stop (no deadman, no gate timeout, no X7) before a third admission is judged
# on its other two checks, and its turn check prints "not_applicable: episode returned at turn k". The
# judged set must still hold at least one D run with three admitted turns. A run ended by any of these
# episode flags did not return by its own stop: the deadman (X7), a G0/G1/H gate timeout, or another
# runtime cut or fault (decode budget, time guard, context limit, episode or endpoint error, collector).
EPISODE_CUT_FLAGS = ("episode.deadman:", "episode.g0_unreleased:", "thermal.start_gate_timeout",
                     "thermal.gate_timeout:", "thermal.hold_timeout:", "episode.decode_budget:",
                     "episode.time_guard:", "episode.context_limit:", "episode_error:", "endpoint_error:",
                     "thermal.collector_failed")
# k is the 0-based index of the run's last admitted turn: a two-turn run prints "turn 1" (RL-149 section 1.1:
# D_bank seed 1 "ended at turn 1").
TURN_CHECK_NOT_APPLICABLE = "not_applicable: episode returned at turn {k}"


def returned_by_own_stop(admitted_turns, x7, episode_flags):
    """RL-149 section 1.5: ``(True, None)`` when the run returned by its own stop (it admitted a turn, no
    X7, and no flag in ``EPISODE_CUT_FLAGS``); ``(False, why)`` when it was cut; ``(None, why)`` when the
    record does not carry its episode flags, so the stop cannot be read (the turn check stays judged)."""
    if not isinstance(episode_flags, (list, tuple)) or not all(isinstance(f, str) for f in episode_flags):
        return None, "episode_flags not recorded: the stop reason cannot be read"
    if x7 is not False:
        return False, "x7"
    cut = sorted({f for f in episode_flags if f.startswith(EPISODE_CUT_FLAGS)})
    if cut:
        return False, ", ".join(cut)
    if type(admitted_turns) is not int or admitted_turns < 1:
        return False, "no admitted turn"
    return True, None


def turn_check(admitted_turns, x7, episode_flags, minimum=DUTY_BAR["min_admitted_turns"]):
    """RL-149 section 1.5: ``True``/``False`` when the turn check is judged, or the ``not_applicable``
    string when the run returned by its own stop before ``minimum`` admissions; and the stop reading."""
    own, why = returned_by_own_stop(admitted_turns, x7, episode_flags)
    if type(admitted_turns) is int and admitted_turns >= minimum:
        return True, {"own_stop": own, "why": why}
    if own is True:
        return TURN_CHECK_NOT_APPLICABLE.format(k=admitted_turns - 1), {"own_stop": True, "why": None}
    return False, {"own_stop": own, "why": why}

# Ruling 1(e): named fallback order if the duty bar fails (lead applies it).
DUTY_FALLBACK_ORDER = (
    "S6 tuning jointly for G1 and hold waits (median <= 90 s each), delta_slow capped at 2.0 C",
    "idle 300 -> 450 s after D predecessors only",
    "4-bit at the same rung (quantization rule trigger extended to 'duty bar fails')",
    "D screen-only; return to council",
)
# Ruling 8: OS daily-batch avoidance and load journal. The window is local
# wall time on the measurement Mac (Pacific); a zoneinfo zone keeps the
# boundaries right across a DST transition (cold pass LOW 8).
# RL-149 section 2.9 item 4 (cited rebind; DEVIATIONS RL149-BATCH-WINDOW): ruling 8's
# sentence now reads "Soak and step tests outside 02:00-02:35 local". Three days of
# dasd logs put the daily batch at about 02:08 (XProtect's periodic scan 02:08-02:25)
# and nothing above 0.65 core in 11:45-13:15 on any day inspected. RL-72 E2's two
# load redos and two batch encounters stand; the blackout term of night_worst_case_s
# follows this window, and window_max_s is recomputed by the registered construction.
OS_BATCH_WINDOW_LOCAL = ((2, 0), (2, 35))
LOCAL_ZONE = ZoneInfo("America/Los_Angeles")
# Ruling 8 load-journal completeness (executing review MEDIUM-1): about one
# sample per wall second of the segment, and no gap longer than this.
CPU_JOURNAL_MIN_RATE = 0.9
CPU_JOURNAL_SLACK_S = 5
CPU_JOURNAL_MAX_GAP_S = 5.0
QUIET_SEGMENT_BOUND_S = 1800           # planning bound for an unscheduled step segment
# Sol critique of round 5: segments that run past the member cap need their
# full bound for the ruling 8 batch-window admission. The 30B/D steps add the
# fixed 600 s recovery after the member (the 300 s quiet is inside it); the
# designed start states add the 900 s preheat cap (R5-2: the deadman no longer
# bounds preheat + G0 + turn).
STEP_RECOVERY_S = 600
PLANNING_PREHEAT_CAP_S = 900
# Round-5 executing review: R5-2 re-arms the deadman after the G0 (its own
# 600 s cap) and, for the 30B/D steps, after the 300 s quiet as well, so the
# 1,800 s member bound no longer contains either; both are added here.
STEP_G0_CAP_S = 600
STEP_QUIET_S = 300
# LEAD-RULINGS-2 R7-2: step-d, the gated D runs and X-G arm the R1 G0 timeout,
# the runtime config's g0_timeout_s (1,200 s). RL-59 ("1,200 s stays, for every
# R1 gate"; follow-up kit a85ee8ec6): step-30b, the A-B-A legs and d-4bit arm it too.
# The gated runs and X-G arm their G0 inside the member deadman, so their
# 1,800 s member bound already contains it.
G0_TIMEOUT_KEY = "g0_timeout_s"
W1_G0_CAP_FLOOR_S = 600       # R7-2: G0_cap_W1 = clamp(ceil(1.25 x max wait), 600 s, R1 G0 timeout)
W1_G0_CAP_FACTOR = 1.25
W1_G0_CAP_RUNS = ("D_bank_benign_s1_gated_held", "D_spam_benign_s1_gated_held_a",
                  "D_spam_benign_s1_gated_held_b", "X_G_contrast")


def rearmed_member_bound_s(step_deadman_s):
    """LEAD-RULINGS-2 R8-4 (round-7 science Sol MEDIUM-1): the wall of a step
    member whose deadman R5-2 re-arms after its G0 (and quiet or preheat),
    without those pre-deadman phases: the member's start-up and close (the
    member law's intercept, at the largest I_D the runtime admits,
    ``ABA_LEG_I_D_BOUND_S``, since step-d's own I_D is what step-d measures),
    plus 1.13544 x the re-armed step deadman, plus the margin for the deadman
    tail and process start-up -- the A-B-A leg law (round-3 LOW-1)."""
    from scripts.align_v4_kit import DEADMAN_FACTOR
    return ABA_LEG_I_D_BOUND_S + DEADMAN_FACTOR * step_deadman_s + LEG_BOUND_MARGIN_S


def segment_bounds(g0_timeout_s, step_deadman_s):
    """Ruling 8 batch-window bounds of the quiet model segments, with the R1
    G0 timeout (R7-2) for step-d and the designed start states.

    R8-4: step-d and the designed start states are bounded by their re-armed
    member (start-up and close around the re-armed deadman,
    ``rearmed_member_bound_s``) plus their pre-deadman phases (G0 timeout and
    the 300 s quiet, or the 900 s preheat cap and the G0 timeout) and, for
    step-d, the 600 s recovery.

    Round-8 disposition D8-3 (R1 round-8 exec LOW-2): step-30b's deadman is
    re-armed after its G0 and quiet too, so it takes the same construction:
    the re-armed member plus its pre-deadman phases (the R1 G0 timeout, 1,200 s
    under RL-59, the 300 s quiet) and the 600 s recovery."""
    member = rearmed_member_bound_s(step_deadman_s)
    return {"step-30b": member + g0_timeout_s + STEP_QUIET_S + STEP_RECOVERY_S,
            "step-d": member + g0_timeout_s + STEP_QUIET_S + STEP_RECOVERY_S,
            **{f"d-planning-turn-r-plus-{int(o)}c": member + PLANNING_PREHEAT_CAP_S + g0_timeout_s
               for o in PLANNING_START_OFFSETS_C}}
CPU_BUSY_CORES_LIMIT = 0.5
CPU_BUSY_SUSTAINED_S = 60
MAX_SEGMENT_REDOS = 2
SOAK_TAIL_S = 1200
SOAK_MAX_SLOPE_C_PER_MIN = 0.2
# Ruling 6 (U5): one-sided 90 % bound on |beta_T| uses the two-sided 90 % t.
T_90_DF1 = 6.313751514675043
T_95_DF1 = 12.706204736432095
# Ruling 16: High Power adoption.
HIGH_POWER_GAIN = 1.25
HIGH_POWER_A_LEG_SPREAD = 0.25
# Earlier rounds: a G0-style release against the soak preceded every A-B-A leg
# (ruling 16) and every redo of a heavy quiet segment (ruling 8); FD:489 caps
# that G0 at 600 s. The follow-up night drops the leg release (RL-59) and redoes
# whole admission units (RL-72 E2); only release_segment_bound_s keeps this.
G0_RELEASE_BOUND_S = 600
SOAK_REFERENCE_SCHEMA = "joulewise.align.r1_soak_reference.v1"
# Lead ruling L2 (LEAD-RULINGS-1): U5 is |beta_T|_90 x delta_slow <= c x sigma_pair
# with c = 1.0; sigma_pair = max(observed R1 replay-pair difference, 2.97 J).
U5_C = 1.0
U5_SIGMA_PAIR_FLOOR_J = 2.97


class Refusal(RuntimeError):
    pass


# Fable cold pass MEDIUM-1: on the first signal the runtime (which owns the SMC
# sidecar, the thermal journal, powermetrics and its output custody) gets TERM
# and up to 20 s to close them, inside run_night's 30 s; only then KILL.
RUNTIME_TERM_GRACE_S = 20.0


# Lead ruling R8-1: after the runtime is reaped, every process of its tree
# seen while it lived is TERMed, then KILLed, each step bounded, and proven gone.
# A process is identified by its pid AND its start time (``lstart``), so an
# exec into another program is still the same process and a reused pid is not
# (round-8 Sol critique).
PS_TREE = ("/bin/ps", "-A", "-o", "pid=,ppid=,lstart=,command=")
TREE_STOP_WAIT_S = 5.0
TREE_POLL_S = 0.1
REAP_AFTER_KILL_S = 30.0


def _process_table():
    """``{pid: (ppid, lstart, command)}`` of every process, or None when ``ps`` fails."""
    try:
        rows = subprocess.run(list(PS_TREE), text=True, capture_output=True, check=False, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    if rows.returncode != 0:
        return None
    table = {}
    for row in rows.stdout.splitlines():
        parts = row.split(None, 7)
        if len(parts) >= 7 and parts[0].isdigit() and parts[1].isdigit():
            table[int(parts[0])] = (int(parts[1]), " ".join(parts[2:7]), parts[7] if len(parts) > 7 else "")
    return table


def _descendants(table, root_pid):
    """``{pid: (lstart, command)}`` of every descendant of ``root_pid`` in ``table``."""
    children = {}
    for pid, (ppid, _start, _command) in table.items():
        children.setdefault(ppid, []).append(pid)
    found, stack = {}, [root_pid]
    while stack:
        for child in children.get(stack.pop(), ()):
            if child not in found and child != root_pid:
                found[child] = table[child][1:]
                stack.append(child)
    return found


def _tree_survivors(tree):
    """The recorded descendants still alive with the same start time (None: no census)."""
    table = _process_table()
    if table is None:
        return None
    return {pid: ident for pid, ident in tree.items() if pid in table and table[pid][1] == ident[0]}


def _stop_tree(tree):
    """TERM, bounded wait, KILL, bounded wait, then the proof: no recorded
    descendant is alive with its recorded start time. Never raises."""
    outcome = {"descendants": {str(pid): ident[1] for pid, ident in sorted(tree.items())}}
    survivors = _tree_survivors(tree) if tree else {}
    for number in (signal.SIGTERM, signal.SIGKILL):
        if not survivors:
            break
        for pid in survivors:
            try:
                os.kill(pid, number)
            except OSError:
                pass
        deadline = time.monotonic() + TREE_STOP_WAIT_S
        while True:
            survivors = _tree_survivors(survivors)
            if survivors == {} or time.monotonic() >= deadline:
                break
            time.sleep(TREE_POLL_S)
    outcome["survivors"] = None if survivors is None else {str(pid): ident[1] for pid, ident
                                                           in sorted(survivors.items())}
    outcome["proven"] = survivors == {}
    return outcome


def _terminate(process: subprocess.Popen, grace_s: float | None = None) -> dict:
    """TERM, wait at most ``grace_s`` (default RUNTIME_TERM_GRACE_S), then KILL.

    Lead ruling R8-1: the runtime's own children (the heater, powermetrics
    through sudo) are recorded from the process table while the runtime
    lives (before the TERM, about once a second during the grace, and before
    a KILL), and once the runtime is reaped every one still alive is TERMed,
    then KILLed, and proven gone. Returns the proof; ``proven`` is False when
    a census failed, a descendant survived, the child was not reaped within
    REAP_AFTER_KILL_S of its KILL, or its output pipes are still held open
    after the tree was ended (a holder that was never seen as a descendant).
    The guard then defers the restore."""
    grace_s = RUNTIME_TERM_GRACE_S if grace_s is None else grace_s
    tree, census_failed = {}, False

    def snapshot():
        nonlocal census_failed
        if process.poll() is not None:
            return
        table = _process_table()
        if table is None:
            census_failed = True
        else:
            tree.update(_descendants(table, process.pid))
    snapshot()
    drained = reaped = False
    if process.poll() is None:
        try:
            process.send_signal(signal.SIGTERM)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + grace_s
        while True:
            try:
                process.communicate(timeout=max(0.01, min(1.0, deadline - time.monotonic())))
                drained = True
                break
            except subprocess.TimeoutExpired:
                snapshot()
                if time.monotonic() >= deadline:
                    break
        if not drained and process.poll() is None:
            snapshot()
            process.kill()
    # KILL bounds this, unless the child sits in uninterruptible I/O;
    # communicate() alone could wait forever on a pipe an orphan inherited.
    try:
        process.wait(timeout=REAP_AFTER_KILL_S)
        reaped = True
    except subprocess.TimeoutExpired:
        pass
    proof = _stop_tree(tree)
    if not drained:
        try:
            process.communicate(timeout=TREE_STOP_WAIT_S)
        except subprocess.TimeoutExpired:
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    stream.close()
            proof.update(proven=False, pipes_held_open=True)
    if census_failed:
        proof.update(proven=False, census_failed=True)
    if not reaped:
        proof.update(proven=False, unreaped=True)
    proof.update(pid=process.pid, returncode=process.returncode, authority="lead ruling R8-1")
    return proof


# Lead ruling R7-5: while the driver holds the host night lock, every child it
# starts (the runtime above all) inherits the lock's descriptor, so the lock
# lives as long as the R1 process tree, not the driver alone.
_CHILD_HOST_LOCK = None
# Lead ruling R8-1: the proof of every child terminated on an interrupt; an
# unproven one makes the guard defer the restore (R7-5's rule: never restore
# under a live process of this run).
_CHILD_TERMINATIONS: list = []


_R1_WORK_DEADLINE = None


def _run(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    # Not subprocess.run: on any exception (the one-shot signal handler raises
    # KeyboardInterrupt here) it SIGKILLs the child at once.
    lock = _CHILD_HOST_LOCK
    pass_fds = lock.pass_fds() if lock is not None and lock.held else ()
    process = subprocess.Popen(list(argv), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               pass_fds=pass_fds)
    try:
        cap = 10.0
        if "--r1-kind" in argv:
            kind = argv[argv.index("--r1-kind") + 1]
            cap = {"calibration-pre": 1800, "calibration-post": 1800, "harvest": 4500}.get(kind)
            if cap is None:
                bounds = segment_bounds(runtime_g0_timeout_s(argv), runtime_step_deadman_s(argv))
                cap = (float(argv[argv.index("--duration-s") + 1]) + 30 if "--duration-s" in argv else
                       bounds.get(kind, aba_leg_bound_s(argv) if kind in contract.HIGH_POWER_KINDS else 1800))
        if "--r1-kind" in argv and _R1_WORK_DEADLINE is not None:
            cap = min(cap, max(.001, _R1_WORK_DEADLINE - time.monotonic()))
        stdout, stderr = process.communicate(timeout=cap)
    except BaseException:
        try:
            proof = _terminate(process)
        except BaseException as error:  # noqa: BLE001 - unproven; the original exception stands
            proof = {"pid": process.pid, "proven": False, "error": f"{type(error).__name__}: {error}",
                     "authority": "lead ruling R8-1"}
        _CHILD_TERMINATIONS.append({"argv": [str(a) for a in argv][:6], **proof})
        raise
    return subprocess.CompletedProcess(list(argv), process.returncode, stdout, stderr)


class PowerModeGuard(AbstractContextManager):
    """Narrow High-Power guard; Automatic restoration is attempted always."""

    AUTO = ("sudo", "-n", "/usr/bin/pmset", "-c", "powermode", "0")
    HIGH = ("sudo", "-n", "/usr/bin/pmset", "-c", "powermode", "2")
    LIST = ("sudo", "-n", "-l")
    QUERY = ("/usr/bin/pmset", "-g", "custom")

    def __init__(self, runner: Callable = _run, marker: Path | None = None, host_marker: Path | None = None,
                 lock=None):
        self.runner = runner
        self.marker = marker
        # Lead ruling R6-7: the same obligation at the host-level path every
        # later session, night admission and the watchdog read.
        self.host_marker = host_marker
        # Lead ruling R7-5: the driver's host night lock (its children inherit
        # it); a restore runs only after the guard has retaken it.
        self.lock = lock
        self.deferred = False
        self.records: list[dict] = []
        self.armed = False

    def _must(self, argv, label):
        result = self.runner(argv)
        if result.returncode:
            raise Refusal(f"powermode.{label}: exit {result.returncode}: {result.stderr.strip()}")
        return result

    def query(self, point):
        result = self._must(self.QUERY, "query_failed")
        self.records.append({"point": point, "stdout": result.stdout})

    def restore(self):
        # Do not condition this on setup completion: every possible exit tries 0.
        unproven = [t for t in _CHILD_TERMINATIONS if not t.get("proven")]
        if self.armed and unproven:
            # Lead ruling R8-1: a child this run terminated on an interrupt
            # (the runtime or one of its descendants) is not proven gone; no
            # restore runs under it. The markers stay for the dead-man or the
            # next session start.
            self.deferred = True
            self.armed = False
            self.records.append({"point": "restore_deferred", "unproven": unproven,
                                 "reason": "a child this run terminated on an interrupt could not be proven gone "
                                           "(lead ruling R8-1); markers kept"})
            return False
        if self.lock is not None and self.armed:
            # Lead ruling R7-5: the close of an armed guard (children may have
            # run) first retakes the host night lock on a fresh descriptor;
            # that proves no child of this run still holds it. Otherwise the
            # markers stay for the dead-man or the next session start, and
            # nothing is restored here.
            try:
                proven, error = self.lock.retake(), None
            except Exception as exc:  # noqa: BLE001 - not proven
                proven, error = False, f"{type(exc).__name__}: {exc}"
            if not proven:
                self.deferred = True
                self.armed = False
                self.records.append({"point": "restore_deferred", "lock_error": error,
                                     "reason": "the host night lock could not be retaken; a child of this run "
                                               "may still hold it (lead ruling R7-5); markers kept"})
                return False
            from joulewise.align.apple import powermode
            if self.host_marker is not None and powermode.w1_marker(self.host_marker):
                # Round-7 Sol critique: a W1 session installed its own High
                # Power span between the release and the retake; never undo it.
                self.deferred = True
                self.armed = False
                self.records.append({"point": "restore_deferred",
                                     "reason": "a W1 session's marker holds the host path after the retake; "
                                               "its High Power span is not this run's"})
                return False
        result = self.runner(self.AUTO)
        self.records.append({"point": "restore_automatic", "exit_code": result.returncode,
                             "stdout": result.stdout, "stderr": result.stderr})
        self.armed = False
        if result.returncode != 0:
            return False
        # Lead ruling R7-7 (round-6 exec LOW-2, cold LOW-1): read the mode back
        # before clearing any marker; anything but AC powermode 0 keeps them.
        try:
            query = self.runner(self.QUERY)
            observed = parse_ac_powermode(query.stdout) if query.returncode == 0 else None
            self.records.append({"point": "after_restore_automatic", "exit_code": query.returncode,
                                 "stdout": query.stdout, "observed": observed})
        except Exception as exc:  # noqa: BLE001 - an unread mode is not 0
            observed = None
            self.records.append({"point": "after_restore_automatic", "error": f"{type(exc).__name__}: {exc}"})
        if observed != 0:
            return False
        for marker in (self.marker, self.host_marker):
            if marker is not None:
                marker.unlink(missing_ok=True)
        return True

    def __enter__(self):
        # Ed ruling 2026-11-05 (PLAN "High Power A-B-A is IN R1"): verify the
        # narrow rule with ``sudo -n -l`` before any work.
        listing = self._must(self.LIST, "sudo_list_refused")
        text = listing.stdout + listing.stderr
        for required in ("/usr/bin/pmset -c powermode 0", "/usr/bin/pmset -c powermode 2"):
            if required not in text:
                raise Refusal("powermode.sudo_rule_missing: " + required)
        # Prove restore before any work, and leave the host Automatic.
        if not self.restore():
            raise Refusal("powermode.cannot_restore")
        self.armed = True
        return self

    def high(self):
        self.query("before_high")
        if self.marker is not None:
            self.marker.parent.mkdir(parents=True, exist_ok=True)
            self.marker.write_text("high-power restoration required\n")
        if self.host_marker is not None:
            from joulewise.align.apple import powermode
            powermode.write_host_marker(self.host_marker, tag=powermode.R1_MARKER_TEXT,
                                        owner={"writer": "R1 driver"})
        # The marker must predate High Power: SIGKILL at any later instruction
        # leaves a durable host-level restoration obligation.
        self._must(self.HIGH, "high_failed")
        self.query("after_high")

    def automatic(self, label="after_automatic"):
        self.query("before_automatic")
        self._must(self.AUTO, "automatic_failed")
        self.query(label)

    def __exit__(self, typ, value, traceback):
        if not self.restore() and typ is None:
            raise Refusal("powermode.restore_failed")
        return False


def _invoke(runtime, kind, output, duration=None, *, soak_reference=None, quiet=False, contract_key=None,
            watch=None):
    if watch is not None:
        # Ruling 20: no external volume may be mounted between t0 and the
        # terminal record; check before every runtime invocation.
        watch.check(f"before:{kind}:{Path(output).name}")
    argv = list(runtime) + ["--r1-kind", kind, "--output", str(output)]
    if _CHILD_HOST_LOCK is not None and _CHILD_HOST_LOCK.held:
        argv += ["--host-lock-fd", str(_CHILD_HOST_LOCK.pass_fds()[0])]
    if duration is not None:
        argv += ["--duration-s", str(duration)]
    # Every segment after the accepted soak is handed its reference R; the
    # releases, the post-D cooldown, designed start states and A-B-A legs need it.
    if soak_reference is not None:
        argv += ["--soak-reference", str(soak_reference)]
    elif (contract_key or kind) in contract.NEEDS_SOAK_REFERENCE:
        raise Refusal(f"runtime.{kind}: no soak reference exists yet")
    result = _run(argv)
    if result.returncode:
        raise Refusal(f"runtime.{kind}: exit {result.returncode}: {result.stderr.strip()}")
    try:
        value = json.loads(result.stdout)
    except (ValueError, TypeError) as error:
        raise Refusal(f"runtime.{kind}.invalid_json: {error}") from error
    if not isinstance(value, dict):
        raise Refusal(f"runtime.{kind}: result is not a JSON object")
    missing = contract.missing_fields(kind, value, quiet=quiet, contract_key=contract_key)
    if missing:
        raise Refusal(f"runtime.{kind}: contract fields missing: " + ", ".join(missing))
    return value


def derive_slots(observations):
    """Freeze the council slot vocabulary from measured runtime observations."""
    raw = observations.get("slots")
    if not isinstance(raw, dict):
        raise Refusal("runtime did not return slots")
    missing = [name for name in SLOT_NAMES if name not in raw]
    if missing:
        raise Refusal("runtime omitted slots: " + ", ".join(missing))
    slots = {name: raw[name] for name in SLOT_NAMES}
    for name in SLOT_NAMES[:-1]:
        if isinstance(slots[name], bool) or not isinstance(slots[name], (int, float)) or not math.isfinite(slots[name]):
            raise Refusal(f"slot {name} is not finite numeric evidence")
    if slots["class"] not in ("heavy", "light"):
        raise Refusal("slot class must be heavy or light")
    return slots


def high_power_adoption(t_a1, t_b, t_a2):
    """Ruling 16 adoption rule; ``None`` means no decline observed (infinite)."""
    inf = math.inf
    for value in (t_a1, t_b, t_a2):
        # Round-4 LOW: a JSON true is not 1 s of t_decline.
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))):
            raise Refusal("high_power.t_decline must be positive or null (infinite)")
    a1, b, a2 = (inf if v is None else float(v) for v in (t_a1, t_b, t_a2))
    for value in (a1, b, a2):
        if math.isnan(value) or value <= 0:
            raise Refusal("high_power.t_decline must be positive or null (infinite)")
    if a1 == inf and a2 == inf:
        if b == inf:
            return {"verdict": "not_adopted", "reason": "all legs infinite"}
        # Ruling 16 adopts only when B outlasts both A legs; a finite B that
        # declined while neither Automatic leg did is not an adoption.
        return {"verdict": "not_adopted", "reason": "A legs infinite, B finite"}
    if (a1 == inf) != (a2 == inf) or abs(a1 - a2) > HIGH_POWER_A_LEG_SPREAD * max(a1, a2):
        return {"verdict": "inconclusive", "reason": "Automatic legs differ by more than 25 %"}
    if b == inf:
        return {"verdict": "adopt", "reason": "B infinite, both A legs finite"}
    if b >= HIGH_POWER_GAIN * max(a1, a2):
        return {"verdict": "adopt", "reason": "t_decline(B) >= 1.25 x max(A1, A2)"}
    return {"verdict": "not_adopted", "reason": "t_decline(B) < 1.25 x max(A1, A2)"}


def planning_temperature_summary(results):
    """Print-only R1 secondary path; it does not alter frozen analysis code.

    Each designed start state is a G0 release at R + offset. The runtime
    reports the S_slow it measured at release (``g0_release_c``) and the gate
    band ``delta_slow_c`` it released within; a release outside
    R + offset +/- delta_slow is not the designed state and is refused.
    beta_T is fitted on the measured release temperatures, not the design.
    """
    if len(results) != 3:
        raise Refusal("planning-turn requires exactly three designed start states")
    points = []
    reference = delta = None
    for offset, result in zip(PLANNING_START_OFFSETS_C, results, strict=True):
        try:
            r = float(result["reference_c"])
            release = float(result["g0_release_c"])
            band = float(result["delta_slow_c"])
            energy = float(result["energy_j"])
        except (KeyError, TypeError, ValueError) as error:
            raise Refusal(f"planning-turn invalid temperature evidence: {error}") from error
        if not all(math.isfinite(v) for v in (r, release, band, energy)) or band <= 0:
            raise Refusal("planning-turn temperature evidence must be finite (delta_slow_c > 0)")
        reference = r if reference is None else reference
        delta = band if delta is None else delta
        if not math.isclose(r, reference, abs_tol=1e-9):
            raise Refusal("planning-turn start states do not share one soak reference R")
        if not math.isclose(band, delta, abs_tol=1e-9):
            raise Refusal("planning-turn start states do not share one gate band delta_slow")
        if abs(release - (r + offset)) > band:
            raise Refusal(f"planning-turn G0 release {release} C is outside R + designed offset "
                          f"{r + offset} C +/- delta_slow {band} C")
        points.append({"offset_c": offset, "reference_c": r, "g0_release_c": release,
                       "release_error_c": release - (r + offset), "energy_j": energy})
    xs = [p["g0_release_c"] for p in points]
    ys = [p["energy_j"] for p in points]
    xbar, ybar = math.fsum(xs) / 3, math.fsum(ys) / 3
    sxx = math.fsum((x - xbar) ** 2 for x in xs)
    if sxx <= 0:
        raise Refusal("planning-turn measured release temperatures give beta_T no leverage")
    beta = math.fsum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / sxx
    intercept = ybar - beta * xbar
    residual = math.fsum((y - (intercept + beta * x)) ** 2 for x, y in zip(xs, ys))
    se = math.sqrt(residual / sxx)  # n-2 = 1
    ci90 = [beta - T_90_DF1 * se, beta + T_90_DF1 * se]
    return {"label": "PRINT_ONLY_R1_PLANNING_TEMPERATURE_SECONDARY", "points": points,
            "designed_release_range_c": [reference, reference + PLANNING_START_OFFSETS_C[-1]],
            "measured_release_range_c": [min(xs), max(xs)], "delta_slow_c": delta,
            "beta_T_j_per_c": beta, "beta_T_se_j_per_c": se,
            "beta_T_ci90_j_per_c": ci90,
            "beta_T_ci95_j_per_c": [beta - T_95_DF1 * se, beta + T_95_DF1 * se],
            # Ruling 6: the U5 bar is |beta_T|_90 x delta_slow <= c x sigma_pair.
            "abs_beta_T_90_j_per_c": max(abs(ci90[0]), abs(ci90[1])),
            "u5_bar_form": "|beta_T|_90 * delta_slow <= c * sigma_pair, c = 1.0 (lead ruling L2)"}


def battery_report(results, harvested):
    """Council ruling 4(b): drain rate (%/h) under D and under the 30B, and the
    SoC at which charging resumed, to predict top-ups per window."""
    def drain(name):
        # R6-2: a segment that did not run (step-d INCONCLUSIVE skips the
        # gated runs) has no drain rate.
        value = (results.get(name) or {}).get("battery_drain_pct_per_h")
        # null: the segment charged throughout or had too few samples.
        return None if value is None else _finite_number(value, f"{name}.battery_drain_pct_per_h")
    d_names = ("step_D_prefill_10k_decode_4096", *(name for name, _ in GATED_D_RUNS))
    per_segment = {name: drain(name) for name in ("step_30b", *d_names)}
    d_values = [per_segment[name] for name in d_names if per_segment[name] is not None]
    soc = harvested.get("charge_resume_soc_pct")
    if soc is not None:
        soc = _finite_number(soc, "harvest.charge_resume_soc_pct")
        if not 0 <= soc <= 100:
            raise Refusal("harvest.charge_resume_soc_pct must be within [0, 100]")
    return {"authority": "CHAIR ruling 4(b)",
            "drain_pct_per_h": {"D": math.fsum(d_values) / len(d_values) if d_values else None,
                                "30B": per_segment["step_30b"]},
            "drain_pct_per_h_by_segment": per_segment, "charge_resume_soc_pct": soc,
            "charge_resume_events": harvested.get("charge_resume_events", [])}


def u5_verdict(temperature, gated, inconclusive_runs=()):
    """Ruling 6 U5 with lead ruling L2 (c = 1.0), evaluated on R1.

    sigma_pair is the identical-work pair-difference SD: the R1 replay pair
    gives one difference |E_a - E_b| (its RMS, n = 1), combined with the
    pilots 4-5 value as max(observed, 2.97 J). The verdict is PASS when the
    90 % bound clears the bar, FAIL when the point estimate exceeds it, and
    INCONCLUSIVE when only the bound exceeds it.
    """
    energies = [_finite_number(gated[name].get("energy_j"), f"{name}.energy_j") for name in REPLAY_PAIR]
    observed = abs(energies[0] - energies[1])
    sigma = max(observed, U5_SIGMA_PAIR_FLOOR_J)
    delta = _finite_number(temperature["delta_slow_c"], "planning.delta_slow_c")
    point = abs(temperature["beta_T_j_per_c"]) * delta
    bound = temperature["abs_beta_T_90_j_per_c"] * delta
    bar = U5_C * sigma
    verdict = "pass" if bound <= bar else "fail" if point > bar else "inconclusive"
    # Round-4 executing review HIGH-2: a replay run whose G0 did not release
    # ends with no turn (episode.g0_unreleased), so its turn-owned energy_j is
    # 0 and |E_a - E_b| is the whole other episode, not identical-work noise.
    # That inflates sigma_pair and can turn U5 into a false PASS. Such a pair
    # cannot decide U5.
    empty = [name for name in REPLAY_PAIR
             if type(gated[name].get("admitted_turns")) is int and gated[name]["admitted_turns"] == 0]
    sigma_reason = None
    if empty:
        verdict = "inconclusive"
        sigma_reason = ("replay-pair run(s) " + ", ".join(empty) + " admitted no turn (G0 not released); "
                        "|E_a - E_b| is not an identical-work pair difference")
    # LEAD-RULINGS-2 R6-1 (superseding R5-1's precool): a replay run that is
    # INCONCLUSIVE (its G0 did not release after W1's schedule, or it did not
    # follow a gated D episode, R7-1) cannot decide U5 either.
    uncooled = [name for name in REPLAY_PAIR if name in set(inconclusive_runs)]
    if uncooled:
        verdict = "inconclusive"
        reason = ("replay-pair run(s) " + ", ".join(uncooled) + " are INCONCLUSIVE (R6-1): the G0 did not "
                  "release after W1's inter-member schedule, or the run did not follow a D turn")
        sigma_reason = reason if sigma_reason is None else sigma_reason + "; " + reason
        empty = empty or uncooled
    return {"criterion": "U5", "c": U5_C, "authority": "LEAD-RULINGS-1 L2",
            "sigma_pair_valid": not empty, "sigma_pair_invalid_reason": sigma_reason,
            "sigma_pair_observed_j": observed, "sigma_pair_floor_j": U5_SIGMA_PAIR_FLOOR_J,
            "sigma_pair_j": sigma, "delta_slow_c": delta,
            "beta_T_j_per_c": temperature["beta_T_j_per_c"],
            "beta_T_ci90_j_per_c": temperature["beta_T_ci90_j_per_c"],
            "state_shift_point_j": point, "state_shift_bound90_j": bound, "bar_j": bar,
            "verdict": verdict}


def _finite_number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise Refusal(f"{label} must be finite numeric evidence")
    return float(value)


def deadman_summary(name, result, duty_t_dead=None, *, inconclusive_reason=None):
    """Ruling 1(a)/(d): deadman consumption by phase, predicted turns, duty bar.

    The 40 % share is judged against ``duty_t_dead`` when given: min(armed
    T_dead, L1 T_dead) on the R1 record (executing review MEDIUM-2), because
    W1 arms the L1 value, which is shorter than the armed one once the R1
    tail exceeds 40 s.
    """
    block = result.get("deadman")
    if not isinstance(block, dict) or not isinstance(block.get("phases_s"), dict):
        raise Refusal(f"{name}: runtime omitted deadman consumption by phase")
    t_dead = _finite_number(block.get("T_dead_s"), f"{name}.deadman.T_dead_s")
    if t_dead <= 0:
        raise Refusal(f"{name}.deadman.T_dead_s must be positive")
    phases = {key: _finite_number(block["phases_s"].get(key), f"{name}.deadman.{key}")
              for key in DEADMAN_PHASES}
    turns = result.get("admitted_turns")
    if isinstance(turns, bool) or not isinstance(turns, int) or turns < 0:
        raise Refusal(f"{name}: admitted_turns must be a non-negative integer")
    x7 = result.get("x7")
    if not isinstance(x7, bool):
        raise Refusal(f"{name}: x7 flag must be boolean")
    gate_hold = phases["G0"] + phases["G1"] + phases["H"]
    duty = t_dead if duty_t_dead is None else duty_t_dead
    per_turn = ((phases["G1"] + phases["H"] + phases["decode"] + phases["prefill"] + phases["tool"]) / turns
                if turns else None)
    predicted = ((t_dead - phases["G0"] - phases["tail"]) / per_turn) if per_turn else None
    # RL-149 section 1.5: a run that returned by its own stop before a third admission is judged on its
    # other two checks; its turn check prints not_applicable and is not judged.
    turns_ok, stop = turn_check(turns, x7, result.get("episode_flags"))
    checks = {"no_x7": not x7, "admitted_turns_ge_3": turns_ok,
              "gate_hold_le_40pct_T_dead": gate_hold <= DUTY_BAR["max_gate_hold_fraction_of_T_dead"] * duty}
    judged = [v for v in checks.values() if type(v) is bool]
    bar = {"checks": checks, "pass": all(judged), "verdict": "pass" if all(judged) else "fail",
           "stop": stop, "turn_check_authority": "RL-149 section 1.5"}
    if inconclusive_reason is not None:
        # LEAD-RULINGS-2 R6-1: the run's G0 timed out after W1's inter-member
        # schedule, or it did not follow a D turn; it is INCONCLUSIVE
        # (recorded), never judged and never a night refusal.
        bar.update(**{"pass": False, "verdict": "inconclusive", "reason": inconclusive_reason})
    # R6-3: the decode tokens with phases_s.decode give the run's observed
    # decode rate (none when it decoded nothing), an input of ruling 1(f).
    tokens = result.get("decode_tokens")
    if tokens is not None and (type(tokens) is not int or tokens < 0):
        raise Refusal(f"{name}: decode_tokens must be a non-negative integer")
    if tokens and phases["decode"] <= 0:
        raise Refusal(f"{name}: {tokens} decode tokens in {phases['decode']} s of decode")
    rate = tokens / phases["decode"] if tokens else None
    # RL-148 section 2 / RL-149 section 1.5: the kit's typical-case bar needs each run's own G1 waits and
    # whether a G1 timed out (then the G_turn cap is the G1 term). Recorded as the runtime returned them.
    waits = (result.get("gate_waits_s") or {}).get("G1") if isinstance(result.get("gate_waits_s"), dict) else None
    flags = result.get("episode_flags")
    g1_waits = ([_finite_number(v, f"{name}.gate_waits_s.G1") for v in waits] if isinstance(waits, list) else None)
    g1_timeouts = (sum(1 for f in flags if str(f).startswith("thermal.gate_timeout:"))
                   if isinstance(flags, list) else None)
    return {"run": name, "T_dead_s": t_dead, "duty_T_dead_s": duty, "phases_s": phases,
            "gate_waits_s": {"G1": g1_waits}, "g1_timeouts": g1_timeouts,
            # R7-2: the G0 outcome decides whether phases_s.G0 is a measured
            # wait or a censored one in G0_cap_W1.
            "g0_outcome": result.get("g0_outcome"),
            "fraction_of_T_dead": {k: v / t_dead for k, v in phases.items()},
            "gate_hold_s": gate_hold, "admitted_turns": turns, "x7": x7,
            "predicted_turns_per_episode": predicted, "inconclusive_reason": inconclusive_reason,
            "decode_tokens": tokens, "r_decode_tok_per_s": rate,
            "duty_bar": bar}


def three_turn_run_present(rows):
    """RL-149 section 1.5: the judged set still holds at least one D run with three admitted turns."""
    return any(row["duty_bar"]["verdict"] == "pass" and type(row.get("admitted_turns")) is int
               and row["admitted_turns"] >= DUTY_BAR["min_admitted_turns"] for row in rows)


def duty_verdict(rows):
    """Ruling 1(d) over the gated runs: FAIL if any judged run fails, else
    INCONCLUSIVE if any run is inconclusive (R5-1), else PASS. RL-149 section
    1.5: a PASS also needs one passing run with three admitted turns."""
    verdicts = [row["duty_bar"]["verdict"] for row in rows]
    verdict = "fail" if "fail" in verdicts else "inconclusive" if "inconclusive" in verdicts else "pass"
    if verdict == "pass" and not three_turn_run_present(rows):
        return "fail"
    return verdict


def gate_wait_medians(gated):
    """R5-7: S6 stays delta_slow until the FD 2.6 tuning, which the lead ties to
    the gated runs' median G1 (and hold) wait; recorded here as the TODO input."""
    waits = {"G1": [], "H": []}
    for name, result in gated.items():
        block = result.get("gate_waits_s")
        if not isinstance(block, dict):
            raise Refusal(f"{name}: runtime omitted gate_waits_s (per-gate G1/H waits)")
        for kind in waits:
            values = block.get(kind)
            if not isinstance(values, list):
                raise Refusal(f"{name}.gate_waits_s.{kind} must be a list of seconds")
            waits[kind] += [_finite_number(v, f"{name}.gate_waits_s.{kind}") for v in values]

    def median(values):
        ordered = sorted(values)
        n = len(ordered)
        return None if not n else ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    return {f"{kind}_median_s": median(values) for kind, values in waits.items()} | {
        f"{kind}_waits": len(values) for kind, values in waits.items()}


def thermometry_record(name, result):
    """Protocol v4 :243-251 (R5-5): the R1 full-inventory classification of a step."""
    block = result.get("thermometry")
    if result.get("segment_status") == "inconclusive" and block is None:
        return {"status": "fail", "reasons": ["no turn; classification not measured"], "flags": [],
                "s_fast": None, "s_slow": None}
    if not isinstance(block, dict) or block.get("status") not in ("pass", "fail"):
        raise Refusal(f"{name}: runtime omitted the full-inventory classification (thermometry.status)")
    digest = block.get("classification_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise Refusal(f"{name}: thermometry.classification_sha256 must be a sha256 hex digest")
    keep = ("status", "s_fast", "s_slow", "r0_sensors", "sensor_pick_changed", "flags", "reasons",
            "die_candidates", "heatsink_candidates", "classification_sha256", "classification_file",
            "s7_for_r1_picks", "alias_groups", "alias_rule", "night_confirmation", "registered_picks")
    record = {key: block.get(key) for key in keep}
    if isinstance(record.get("s7_for_r1_picks"), dict):
        # LEAD-RULINGS-2 R6-4: the changed-pick S7's reference R comes from the
        # quiet window (the soak journal lacks the R1-pick keys): ACCEPTED.
        # R9-2: on the classifier's D2 baseline (last 60 s; OLS residual SD).
        record["s7_for_r1_picks"] = {
            **record["s7_for_r1_picks"],
            "reference_rule": ("median of the last 60 s of the 300 s quiet window before prefill, band "
                               "max(1.0 C, 3 x that window's OLS residual SD), the classifier's D2 baseline "
                               "(the soak journal lacks these keys)"),
            "reference_rule_status": "ACCEPTED", "reference_rule_authority": "LEAD-RULINGS-2 R6-4, R9-2"}
    return record


def picks_aliased(classification):
    """LEAD-RULINGS-2 R8-6: True when the classification's two picks are one
    key or sit in one of its ``alias_groups`` (R7-13). A missing or malformed
    group list is the kit's refusal, not this bar's."""
    fast, slow = classification.get("s_fast"), classification.get("s_slow")
    if fast is None or slow is None:
        return False
    groups = classification.get("alias_groups")
    return fast == slow or any(isinstance(group, list) and fast in group and slow in group
                               for group in (groups if isinstance(groups, list) else ()))


def ruled_alias_pair(classification):
    """RL-145 close sections 5 and 10, RL-149 section 5 item 12 (cited rebind of R8-6's bar for one pair):
    the fast pick and the lexically first other member of its alias group, read as one thermometer under
    two key names, on an ok RL-145 night confirmation that names both picks. For this pair only the close
    replaced "aliases do not fill both roles"; any other aliased pair still fails the bar. The same test as
    the W1 kit's ``ruled_alias_pair`` (``scripts/align_v4_kit.py``)."""
    fast, slow = classification.get("s_fast"), classification.get("s_slow")
    groups = classification.get("alias_groups")
    group = next((g for g in (groups if isinstance(groups, list) else ()) if isinstance(g, list) and fast in g),
                 None)
    confirmation = classification.get("night_confirmation")
    confirmation = confirmation if isinstance(confirmation, dict) else {}
    return (fast is not None and group is not None and slow in group and slow != fast
            and slow == min(k for k in group if k != fast)
            and confirmation.get("ok") is True and confirmation.get("second_key_rule") == "RL-145"
            and confirmation.get("s_fast") == fast and confirmation.get("s_slow") == slow)


def _sustained_busy(samples):
    run_length = 0
    for value in samples:
        run_length = run_length + 1 if value > CPU_BUSY_CORES_LIMIT else 0
        if run_length >= CPU_BUSY_SUSTAINED_S:
            return True
    return False


def os_load_verdict(name, result, wall_s=None):
    """Ruling 8: a per-second CPU journal and census are required; redo on load.

    The journal must cover the segment (executing review MEDIUM-1): at least
    0.9 samples per wall second of the invocation, less 5 s of start-up
    slack, with sample times (``cpu_busy_t_s``) nondecreasing and no gap over
    5 s. Otherwise the 60 s-sustained rule is vacuous, so R1 refuses.
    """
    samples = result.get("cpu_busy_cores")
    if not isinstance(samples, list) or not samples:
        raise Refusal(f"{name}: runtime omitted the per-second CPU load journal")
    values = [_finite_number(v, f"{name}.cpu_busy_cores") for v in samples]
    if not result.get("census"):
        raise Refusal(f"{name}: runtime omitted the process census")
    times = result.get("cpu_busy_t_s")
    if not isinstance(times, list) or len(times) != len(values):
        raise Refusal(f"{name}: cpu_busy_t_s must give one sample time per cpu_busy_cores value")
    times = [_finite_number(v, f"{name}.cpu_busy_t_s") for v in times]
    gaps = [b - a for a, b in zip(times, times[1:])]
    if any(gap < 0 for gap in gaps):
        raise Refusal(f"{name}: cpu_busy_t_s is not nondecreasing")
    max_gap = max(gaps, default=0.0)
    if max_gap > CPU_JOURNAL_MAX_GAP_S:
        raise Refusal(f"{name}: CPU load journal has a {max_gap:.1f} s gap (> {CPU_JOURNAL_MAX_GAP_S} s)")
    required = None
    if wall_s is not None:
        required = CPU_JOURNAL_MIN_RATE * wall_s - CPU_JOURNAL_SLACK_S
        if len(values) < required:
            raise Refusal(f"{name}: CPU load journal has {len(values)} samples over {wall_s:.1f} s "
                          f"of wall time (needs >= {required:.1f})")
    return {"redo": _sustained_busy(values), "seconds": len(values), "max_busy_cores": max(values),
            "wall_s": wall_s, "required_samples": required, "max_gap_s": max_gap}


SOAK_TAIL_MIN_RATE = 0.9   # valid reads per second inside the last 1,200 s


def soak_detrended(series_by_key, times_by_key, end_t_s=None):
    """Ruling 8: soak SD on the detrended last 20 min, only if |slope| <= 0.2 C/min.

    The window is the last 1,200 **seconds** of the soak (Fable cold pass
    round 4 LOW-2), selected by each valid read's time (``sensor_series_t_s``,
    seconds on the segment clock): failed reads are dropped by the runtime, so
    the last 1,200 samples would reach further back than 20 min. The window
    ends at the soak's own end (``sensor_series_end_t_s``, common to every
    key), not at a key's last valid read, so a sensor that stopped reading
    near the end cannot substitute an earlier window. The series must span at
    least 1,200 s and the window must hold at least 0.9 valid reads per
    second; the slope is fitted against time.
    """
    end = _finite_number(end_t_s, "idle_soak.sensor_series_end_t_s")
    if not isinstance(series_by_key, dict) or not series_by_key:
        raise Refusal("idle_soak: runtime omitted per-second sensor series")
    if not isinstance(times_by_key, dict):
        raise Refusal("idle_soak: runtime omitted sensor_series_t_s (read times)")
    out = {}
    for key, series in series_by_key.items():
        times = times_by_key.get(key)
        if not isinstance(series, list) or not isinstance(times, list) or len(times) != len(series) or not series:
            raise Refusal(f"idle_soak.{key}: sensor_series_t_s must give one time per value")
        ts = [_finite_number(t, f"idle_soak.{key}.t") for t in times]
        if any(b < a for a, b in zip(ts, ts[1:])):
            raise Refusal(f"idle_soak.{key}: read times are not nondecreasing")
        if ts[-1] > end + 1e-9:
            raise Refusal(f"idle_soak.{key}: a read lies after the soak's end")
        if end - ts[0] < SOAK_TAIL_S - 1:
            raise Refusal(f"idle_soak.{key}: the soak spans {end - ts[0]:.1f} s, under {SOAK_TAIL_S} s")
        start = end - SOAK_TAIL_S
        window = [(t, _finite_number(v, f"idle_soak.{key}")) for t, v in zip(ts, series) if t > start]
        if len(window) < SOAK_TAIL_MIN_RATE * SOAK_TAIL_S:
            raise Refusal(f"idle_soak.{key}: {len(window)} valid reads in the last {SOAK_TAIL_S} s "
                          f"(needs >= {SOAK_TAIL_MIN_RATE * SOAK_TAIL_S:.0f})")
        n = len(window)
        xbar, ybar = math.fsum(t for t, _ in window) / n, math.fsum(y for _, y in window) / n
        sxx = math.fsum((t - xbar) ** 2 for t, _ in window)
        slope = math.fsum((t - xbar) * (y - ybar) for t, y in window) / sxx   # C per s
        resid = [y - (ybar + slope * (t - xbar)) for t, y in window]
        out[key] = {"slope_c_per_min": slope * 60.0, "mean_c": ybar,
                    "settled": abs(slope * 60.0) <= SOAK_MAX_SLOPE_C_PER_MIN,
                    "detrended_sd_c": math.sqrt(math.fsum(r * r for r in resid) / (n - 2)),
                    "window_s": SOAK_TAIL_S, "window_reads": n}
    return out


def os_batch_blackout_s():
    """The blackout's length in wall seconds on an ordinary day (RL-149: 02:00-02:35, 2,100 s)."""
    (h0, m0), (h1, m1) = OS_BATCH_WINDOW_LOCAL
    return ((h1 * 60 + m1) - (h0 * 60 + m0)) * 60


def os_batch_window_text():
    """``"HH:MM-HH:MM"`` of ``OS_BATCH_WINDOW_LOCAL``, for messages."""
    (h0, m0), (h1, m1) = OS_BATCH_WINDOW_LOCAL
    return f"{h0:02d}:{m0:02d}-{h1:02d}:{m1:02d}"


def _batch_windows(moment):
    """Today's and tomorrow's OS-batch windows (``OS_BATCH_WINDOW_LOCAL``,
    02:00-02:35 Pacific under RL-149) as epoch seconds.

    Each boundary is built from the local calendar date in LOCAL_ZONE, so on
    a DST transition day it still means the same wall times (on a spring-forward
    day 02:00-02:35 does not exist as wall time; zoneinfo maps it forward, so the
    window still lies at the transition); all comparisons are on absolute (epoch)
    time, never on fixed-offset wall time.
    """
    (h0, m0), (h1, m1) = OS_BATCH_WINDOW_LOCAL
    day = moment.astimezone(LOCAL_ZONE).date()
    windows = []
    for offset in (0, 1):
        date = day + timedelta(days=offset)
        start = datetime.combine(date, wall_time(h0, m0), tzinfo=LOCAL_ZONE).timestamp()
        end = datetime.combine(date, wall_time(h1, m1), tzinfo=LOCAL_ZONE).timestamp()
        windows.append((start, end))
    return windows


def wait_outside_os_batch(expected_s, *, now=None, sleep=None):
    """Ruling 8 (RL-149 window): start a quiet segment only if it ends before the batch window's start or
    starts after its end, local time (``OS_BATCH_WINDOW_LOCAL``)."""
    now = now or _now_local
    sleep = sleep or time.sleep
    waited = 0.0
    while True:
        moment = now()
        if moment.tzinfo is None:
            raise ValueError("wait_outside_os_batch needs an aware datetime")
        t = moment.timestamp()
        finish = t + expected_s
        hit = next(((s0, e) for s0, e in _batch_windows(moment) if t < e and finish > s0), None)
        if hit is None:
            return waited
        delay = max(1.0, hit[1] - t)
        sleep(delay)
        waited += delay


def _now_local():
    return datetime.now(LOCAL_ZONE)


def projected_mde(e_d, gated):
    """Ruling 28: print-only projected MDE from measured e_D, E_D and the R1 replay pair."""
    e_d = _finite_number(e_d, "step-d.e_D_j_per_token")
    if e_d <= 0:
        raise Refusal("step-d.e_D_j_per_token must be positive")
    energies = {name: _finite_number(r.get("energy_j"), f"{name}.energy_j") for name, r in gated.items()}
    e_episode = math.fsum(energies.values()) / len(energies)
    pair_diff = abs(energies[REPLAY_PAIR[0]] - energies[REPLAY_PAIR[1]])
    scenarios = {}
    for label, fraction in (("B_low_1.2pct", 0.012), ("B_high_1.7pct", 0.017)):
        s_r = fraction * e_episode
        scenarios[label] = {"s_r_j": s_r, **{f"q={q}": q * s_r / e_d for q in (2.5, 3.0, 7.0)}}
    return {"label": "PRINT_ONLY_R1_PROJECTED_MDE", "formula": "MDE ~= q * s_r,D / e_D (CHAIR section C)",
            "e_D_j_per_token": e_d, "E_D_j": e_episode, "replay_pair_abs_diff_j": pair_diff,
            "replay_pair_floor_tokens": pair_diff / e_d, "energy_scaled_misfit": scenarios}


def write_soak_reference(output, soak_row):
    """The accepted soak's detrended last-20-min means: the reference R handed
    to every later runtime release, cooldown and designed start state."""
    path = output / "soak_reference.json"
    detrended = soak_row["soak_detrended"]
    value = {"schema": SOAK_REFERENCE_SCHEMA, "source_segment": soak_row["name"],
             "source_output": soak_row["output_dir"], "attempt": soak_row["attempt"],
             "window_s": SOAK_TAIL_S, "sensors_c": {k: v["mean_c"] for k, v in detrended.items()},
             "detrended": detrended, "sensor_roles": (soak_row.get("result") or {}).get("sensor_roles")}
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    return path


def _release_against_soak(args, output, label, soak_reference):
    """A G0-style release against the soak before a leg or a heavy redo."""
    release = _invoke(args.runtime, "g0-release-soak", output / label, soak_reference=soak_reference,
                      watch=getattr(args, "volume_watch", None))
    if not isinstance(release.get("released"), bool):
        raise Refusal(f"{label}: G0 release status missing")
    return release


def _fresh_name(output, stem, start):
    """``stem`` + the first index from ``start`` that names no existing entry."""
    index = start
    while (output / f"{stem}{index}").exists():
        index += 1
    return f"{stem}{index}"


def admission_units(runtime_argv=None):
    """RL-72 E2: pair and precool+planning recipes are indivisible on redo."""
    phases = phase_plan(precool_cap_s=runtime_precool_cap_s(runtime_argv))
    units, index = [], 0
    while index < len(phases):
        row = phases[index]
        count = 2 if row[1] == "capture-predecessor-30b" or row[1] == "idle-until-soak" else 1
        units.append(phases[index:index + count])
        index += count
    return units


def phase_bound(phase, runtime_argv=None):
    _name, kind, duration, _class = phase
    if kind in ("calibration-pre", "calibration-post"):
        return 1800.0
    if duration is not None:
        return float(duration)
    if kind in contract.HIGH_POWER_KINDS:
        return aba_leg_bound_s(runtime_argv)
    return segment_bounds(runtime_g0_timeout_s(runtime_argv), runtime_step_deadman_s(runtime_argv)).get(
        kind, QUIET_SEGMENT_BOUND_S)


def _admission_unit(args, output, unit, record, *, soak_reference=None, extra=None):
    """Two CPU-load redos total; never wait or precool inside the capture pair."""
    bound = math.fsum(phase_bound(p, args.runtime) for p in unit)
    attempts = []
    while True:
        waited = wait_outside_os_batch(bound)
        if waited:
            args.batch_encounters = getattr(args, "batch_encounters", 0) + 1
            if args.batch_encounters > 2:
                raise Refusal("RL-72 E2: two OS-batch encounters exhausted")
        rows, reasons = [], []
        for name, kind, duration, workload_class in unit:
            start = time.time_ns()
            quiet = kind in QUIET_KINDS or kind in contract.HIGH_POWER_KINDS or kind == "capture-predecessor-30b"
            print(f"R1 segment: {name}", flush=True)
            result = _invoke(args.runtime, kind, output / name, duration, soak_reference=soak_reference,
                             quiet=quiet, contract_key="idle_soak" if name == "idle_soak" else None,
                             watch=getattr(args, "volume_watch", None))
            row = {"name": name, "class": workload_class, "started_ns": start, "ended_ns": time.time_ns(),
                   "attempt": len(attempts), "os_batch_wait_s": waited if not rows else 0,
                   "output_dir": str(output / name), "result": result, **(extra or {})}
            if quiet:
                verdict = os_load_verdict(name, result, wall_s=(row["ended_ns"] - start) / 1e9)
                row["os_load"] = verdict
                if verdict["redo"]:
                    reasons.append(name + ":cpu_load")
            if name == "idle_soak":
                row["soak_detrended"] = soak_detrended(result.get("sensor_series_c"), result.get("sensor_series_t_s"),
                                                       result.get("sensor_series_end_t_s"))
                if not all(v["settled"] for v in row["soak_detrended"].values()):
                    raise Refusal("idle soak has unresolved slope")
            rows.append(row)
        if not reasons:
            for row in rows:
                row["superseded_attempts"] = [r for recipe in attempts for r in recipe if r["name"] == row["name"]]
                record["phases"].append(row)
            return {row["name"]: (row["result"], row) for row in rows}
        # Preserve every rejected recipe, including an otherwise clean predecessor.
        for row in rows:
            target = Path(row["output_dir"])
            rejected = output / _fresh_name(output, row["name"] + ".rejected", len(attempts) + 1)
            if target.exists():
                target.rename(rejected)
            row.update(output_dir=str(rejected), redo_reason=reasons)
        attempts.append(rows)
        args.load_redos_used = getattr(args, "load_redos_used", 0) + 1
        record["load_redos_used"] = args.load_redos_used
        if args.load_redos_used > 2:
            record["phases"].extend(rows)
            raise Refusal("RL-72 E2: two whole-unit load redos exhausted")


def _segment(args, output, name, kind, duration, workload_class, record, *, quiet,
             soak_reference=None, release_first=False, contract_key=None, extra=None, bound_s=None):
    # Compatibility for existing callers; there are no soak releases or G0 redos.
    return _admission_unit(args, output, [(name, kind, duration, workload_class)], record,
                           soak_reference=soak_reference, extra=extra)[name]


GATED_NAMES = frozenset(name for name, _ in GATED_D_RUNS)
DEFAULT_RUNTIME_CONFIG = Path("configs/align/v4/r1_runtime.json")
# Executing review round 3 LOW-1: an A-B-A leg's batch-window bound comes from
# the configured values, not an assumed 1,800 + 600 s. The leg is one step
# member (member law I_D + 1.13544 x the step deadman, which the runtime arms
# at G0 entry and which covers G0 and the decode) after a G0 release segment
# (65 s pre-roll + the 600 s G0 cap), plus this margin for the deadman tail and
# process start-up.
LEG_BOUND_MARGIN_S = 120
G0_PREROLL_S = 65
# Integration of round 5: the legs run before step-d (R5-5), so the member
# intercept in the bound is the runtime's admissible maximum, not step-d's I_D.
ABA_LEG_I_D_BOUND_S = 1750


def release_segment_bound_s():
    """R8-4: a G0 release against the soak (before a heavy redo or a leg) is
    the runtime's 65 s pre-roll plus the 600 s G0 cap."""
    return G0_PREROLL_S + G0_RELEASE_BOUND_S


def _check_step_d(result):
    """Right after step-d, not after the night (Mac time): the slots must be
    finite evidence (LOW-9: a no-rise t63 is null, so it refuses here) and B_D
    must be a budget the gated D runs can arm (lead ruling R5-4: a gated D
    never runs unbudgeted; step-d floors a small budget to 0)."""
    slots = derive_slots(result)
    b_d = slots["B_D"]
    if type(b_d) is not int or not 1024 <= b_d <= 40960 or b_d % 1024:
        raise Refusal(f"step-d.B_D {b_d!r} is not an admissible decode budget (a multiple of 1024 in "
                      "[1024, 40960]); the gated D runs would run unbudgeted")
    return slots


def runtime_config_path(runtime_argv):
    """The runtime config the runtime argv names (``--config``), or the committed default."""
    argv = list(runtime_argv or ())
    path = Path(argv[argv.index("--config") + 1]) if "--config" in argv[:-1] else DEFAULT_RUNTIME_CONFIG
    return path if path.is_absolute() else ROOT / path


def _runtime_config_value(runtime_argv, keys, purpose):
    path = runtime_config_path(runtime_argv)
    try:
        value = json.loads(path.read_text())
        for key in keys:
            value = value[key]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise Refusal(f"runtime config {path}: no {'.'.join(keys)} for {purpose}: {error}") from error
    return path, value


def runtime_step_deadman_s(runtime_argv):
    """``step.deadman_s`` of the runtime config the runtime argv names
    (``--config``), or of the committed default config."""
    _, value = _runtime_config_value(runtime_argv, ("step", "deadman_s"), "the A-B-A leg bound")
    value = _finite_number(value, "runtime config step.deadman_s")
    if value <= 0:
        raise Refusal("runtime config step.deadman_s must be positive")
    return value


def runtime_g0_timeout_s(runtime_argv):
    """LEAD-RULINGS-2 R7-2: the R1 G0 timeout, one runtime-config constant."""
    from joulewise.align.apple.thermal_gates import G0_CAP_DEFAULT_S, G0_CAP_MAX_S
    _, value = _runtime_config_value(runtime_argv, (G0_TIMEOUT_KEY,), "the R7-2 G0 timeout")
    value = _finite_number(value, f"runtime config {G0_TIMEOUT_KEY}")
    if not G0_CAP_DEFAULT_S <= value <= G0_CAP_MAX_S:
        raise Refusal(f"runtime config {G0_TIMEOUT_KEY} {value} is outside [{G0_CAP_DEFAULT_S}, {G0_CAP_MAX_S}] s")
    return value


def runtime_precool_cap_s(runtime_argv):
    """LEAD-RULINGS-2 R6-2: the calibration precool cap, from the runtime config."""
    _, value = _runtime_config_value(runtime_argv, ("calibration_precool_cap_s",), "the R6-2 precool cap")
    value = _finite_number(value, "runtime config calibration_precool_cap_s")
    if value <= 0:
        raise Refusal("runtime config calibration_precool_cap_s must be positive")
    return value


def w1_inter_member_idle_s(root=ROOT):
    """LEAD-RULINGS-2 R6-1: W1's inter-member schedule per roster role, taken
    from the W1 plan (``night_plan.template.json``): each member's configured
    idle (``sampling.idle_seconds`` of its kit config). The kit's reading, so
    the driver and the kit binding share one source."""
    from scripts.align_v4_kit import w1_inter_member_idle_s as read
    try:
        return read(root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise Refusal(f"W1 plan {W1_PLAN_TEMPLATE}: no inter-member schedule: {error}") from error


def check_w1_schedule(runtime_argv, root=ROOT):
    """R6-1 at t0 (before any powermode or runtime work): the members the R1
    gated D runs and X-G run (the runtime config's templates) must carry
    exactly W1's configured idle for their roster role."""
    expected = w1_inter_member_idle_s(root)
    path, templates = _runtime_config_value(runtime_argv, ("templates",), "the R6-1 schedule")
    configured = {}
    for key, role in W1_SCHEDULE_ROLES.items():
        target = Path(templates.get(key, "")) if isinstance(templates, dict) else Path()
        target = target if target.is_absolute() else ROOT / target
        try:
            idle = json.loads(target.read_text())["sampling"]["idle_seconds"]
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise Refusal(f"runtime config {path}: template {key} has no sampling.idle_seconds: {error}") from error
        configured[key] = _finite_number(idle, f"runtime template {key} sampling.idle_seconds")
        if configured[key] != expected[role]:
            raise Refusal(f"R6-1: runtime template {key} idles {configured[key]} s, but W1 {role} members idle "
                          f"{expected[role]} s; the gated runs would not reproduce W1's inter-member schedule")
    return {"authority": "LEAD-RULINGS-2 R6-1", "inter_member_idle_s": expected, "templates_idle_s": configured,
            "source": f"{W1_PLAN_TEMPLATE} member configs, sampling.idle_seconds",
            "rule": ("each gated D run and X-G follows a D turn with only W1's inter-member schedule "
                     "(the member's own configured idle); no cool-to-band")}


def _check_schedule(name, result, schedule, role):
    """R6-1 per run: the member idled exactly W1's schedule and reported its G0."""
    idle = _finite_number(result.get("inter_member_idle_s"), f"{name}.inter_member_idle_s")
    if idle != schedule["inter_member_idle_s"][role]:
        raise Refusal(f"{name}: idled {idle} s before warmup, not W1's {role} schedule "
                      f"{schedule['inter_member_idle_s'][role]} s (R6-1)")
    if not isinstance(result.get("g0_outcome"), str):
        raise Refusal(f"{name}: g0_outcome must name the G0 outcome (R6-1)")
    return result["g0_outcome"] == "released"


# R6-1: the segments that end with a D turn (when their G0 released).
D_TURN_KINDS = frozenset(("step-d", "d-4bit", *contract.GATED_D_KINDS, *contract.PLANNING_KINDS))


def schedule_inconclusive_reason(g0_released, follows_d_turn):
    """R6-1: why a gated run or X-G is INCONCLUSIVE (None when it is judged)."""
    if not g0_released:
        return "G0 did not release after W1's inter-member schedule (LEAD-RULINGS-2 R6-1)"
    if follows_d_turn is None:
        return ("the preceding member dispatched no D turn (its G0 timed out), so this run did not test "
                "W1's D-after-D G0 (LEAD-RULINGS-2 R6-1)")
    return None


def _check_precool(name, result):
    """An idle-until-soak segment: the ruling 1(c) recovery curve and its release flag."""
    curve = result.get("recovery_curve")
    if not isinstance(curve, list) or not curve:
        raise Refusal(f"{name}: runtime omitted the recovery curve (ruling 1(c))")
    _check_recovery_curve(name, curve)
    if not isinstance(result.get("released"), bool):
        raise Refusal(f"{name}: idle-until-soak must report released (bool)")
    return result["released"]


def _g0_inconclusive(name, kind, result):
    """R6-2: the runtime reported the calibration segment INCONCLUSIVE (G0 timeout)."""
    if not contract.is_g0_inconclusive(kind, result):
        return False
    if result.get("g0_released") is not False:
        raise Refusal(f"{name}: an INCONCLUSIVE segment must report g0_released false")
    return True


def _calibration_segment(args, output, name, kind, record, *, quiet, soak_reference, extra, precool_cap_s,
                         precools):
    result, row = _segment(args, output, name, kind, None, "heavy", record, quiet=quiet,
                          soak_reference=soak_reference, extra=extra)
    return result, row, "inconclusive" if _g0_inconclusive(name, kind, result) else "measured"


def aba_leg_bound_s(runtime_argv):
    return rearmed_member_bound_s(runtime_step_deadman_s(runtime_argv)) + runtime_g0_timeout_s(runtime_argv)


def night_worst_case_s(runtime_argv=None, include_4bit=False):
    """RL-72 E2 bounds, not a prediction. Exactly two whole-unit load redos."""
    units = [{"names": [p[0] for p in unit], "bound_s": math.fsum(phase_bound(p, runtime_argv) for p in unit)}
             for unit in admission_units(runtime_argv) if unit[0][1] not in ("calibration-pre", "calibration-post")]
    total = math.fsum(u["bound_s"] for u in units)
    largest = max(u["bound_s"] for u in units)
    # RL-149 section 2.9 item 4: the blackout is the 02:00-02:35 window (2,100 s; RL-72 E2 had 5,400 s).
    blackout, encounters, redos, overhead = os_batch_blackout_s(), 2, 2, 9000
    encounter = largest + blackout
    floor = math.ceil(total + redos * largest + encounters * encounter)
    span = floor + overhead
    from joulewise.b6.plan_inputs import window_max_s
    maximum = window_max_s({"programmed_span_s": {"seconds": span}})
    return {"admission_units": units, "no_redo_s": total, "largest_unit_s": largest,
            "redo_quota": redos, "encounters": encounters, "batch_blackout_s": blackout,
            "batch_encounter_max_s": encounter, "overhead_s": overhead,
            "overhead_caps_s": {"pre_bracket": 1800, "post_bracket": 1800, "close": 900, "harvest": 4500},
            "floor_s": floor, "programmed_span_s": span, "window_max_s": maximum}


def budget_fit_inputs(step_d, gated, deadman_rows=()):
    """What the kit needs to assert ruling 1(f) for the B_D it freezes (lead
    ruling R5-4): the decode rate and the per-turn decode cap the gated D runs
    armed (an admitted last turn keeps its full cap, FD:263). The G0, hold,
    prefill and tool seconds are in ``deadman_budget``.

    LEAD-RULINGS-2 R6-3: the worst-case decode term uses min(step-d's decode
    rate, every gated run's observed decode rate); a run that decoded nothing
    (its G0 timed out) has no rate. The kit re-derives the minimum from
    ``r_decode_step_d_tok_per_s`` and the ``deadman_budget`` rows."""
    step_rate = _finite_number(((step_d or {}).get("slot_detail") or {}).get("r_decode_tok_per_s"),
                               "step-d.slot_detail.r_decode_tok_per_s")
    caps = {_finite_number(result.get("turn_cap_tokens"), f"{name}.turn_cap_tokens")
            for name, result in gated.items()}
    if step_rate <= 0 or len(caps) != 1 or min(caps) <= 0:
        raise Refusal("ruling 1(f) inputs: the decode rate must be positive and every gated D run must arm "
                      "the same positive per-turn decode cap")
    observed = {row["run"]: row.get("r_decode_tok_per_s") for row in deadman_rows}
    rates = [step_rate, *(rate for rate in observed.values() if rate is not None)]
    return {"authority": "CHAIR ruling 1(f); lead rulings R5-4, R6-3, R7-2", "r_decode_tok_per_s": min(rates),
            "r_decode_step_d_tok_per_s": step_rate, "r_decode_gated_tok_per_s": observed,
            "turn_cap_tokens": int(caps.pop()),
            "rule": ("G0_cap_W1 (r1_slots.g0_cap_w1.value_s, R7-2) + max (G1 + H) + max (prefill + tool) over "
                     "the gated D runs + (B_D + turn_cap_tokens) / r_decode <= T_dead, r_decode = min(step-d rate, "
                     "every gated run's observed rate) (scripts/align_v4_kit.py ruling_1f_fit)")}


def x_g_evidence(result):
    """LEAD-RULINGS-2 R10-4: the timing and count fields of X-G that prove the
    contrast members' W1 G0 cap fits their deadman (R10-2(a)): its admitted
    turns, whether it hit the deadman (x7) and its phase seconds. Recorded as
    the runtime returned them (None when absent); the kit judges them."""
    flags = result.get("episode_flags")
    phases = result.get("phases_s")
    return {"admitted_turns": result.get("admitted_turns"),
            "x7": (any(str(flag).startswith("episode.deadman:") for flag in flags)
                   if isinstance(flags, list) else None),
            "phases_s": dict(phases) if isinstance(phases, dict) else None}


def w1_g0_cap(deadman_rows, x_g, g0_timeout_s):
    """LEAD-RULINGS-2 R7-2 and R7-12: W1's G0 cap, an R1-derived slot.

    G0_cap_W1 = clamp(ceil(1.25 x max G0 wait over D_bank, D_spam a, D_spam b
    and X-G), 600 s, the R1 G0 timeout). A G0 that did not release (timeout,
    deadman or unobserved) is censored and counts at the full R1 timeout
    (builder decision (d), confirmed by R7-2). An X-G that is not ``measured``
    counts at the R1 timeout too, with ``x_g_fallback`` (R7-12). The kit
    re-derives this from deadman_budget and x_g, binds
    inputs.R1.thermal_policy.g0_cap_s to ``value_s`` and uses it as ruling
    1(f)'s G0 term."""
    waits, censored = {}, []
    for row in deadman_rows:
        if row["g0_outcome"] == "released":
            waits[row["run"]] = row["phases_s"]["G0"]
        else:
            waits[row["run"]] = float(g0_timeout_s)
            censored.append(row["run"])
    fallback = x_g.get("status") != "measured"     # measured implies a released G0 (R6-1)
    if fallback:
        waits["X_G_contrast"] = float(g0_timeout_s)
        if x_g.get("g0_outcome") != "released":
            censored.append("X_G_contrast")
    else:
        waits["X_G_contrast"] = _finite_number(x_g.get("g0_wait_s"), "X_G_contrast.g0_wait_s")
    if sorted(waits) != sorted(W1_G0_CAP_RUNS):
        raise Refusal(f"R7-2: G0_cap_W1 needs exactly {list(W1_G0_CAP_RUNS)}, got {sorted(waits)}")
    peak = max(waits.values())
    value = int(min(max(math.ceil(W1_G0_CAP_FACTOR * peak), W1_G0_CAP_FLOOR_S), g0_timeout_s))
    return {"authority": "LEAD-RULINGS-2 R7-2, R7-12", "r1_g0_timeout_s": float(g0_timeout_s),
            "floor_s": float(W1_G0_CAP_FLOOR_S), "factor": W1_G0_CAP_FACTOR, "waits_s": waits,
            "censored": sorted(censored), "x_g_fallback": fallback, "max_g0_s": peak, "value_s": value,
            "rule": ("G0_cap_W1 = clamp(ceil(1.25 x max G0 wait over D_bank, D_spam a, D_spam b, X-G), 600 s, "
                     "R1 G0 timeout); an unreleased G0, or an X-G that is not measured (x_g_fallback), counts "
                     "at the R1 G0 timeout; ruling 1(f) uses value_s as its G0 term")}


def g0_wait_record(phases):
    """R7-2: every G0 wait of the night, superseded attempts and the releases
    before the A-B-A legs and redos included, in run order."""
    rows = []

    def add(row):
        # The release (when one preceded the attempt) ran first.
        release = row.get("g0_release")
        if isinstance(release, dict) and "g0_wait_s" in release:
            rows.append({"segment": row["name"] + ".g0_release", "output_dir": None,
                         "g0_outcome": (release.get("g0") or {}).get("outcome"),
                         "g0_wait_s": release.get("g0_wait_s"), "g0_timeout_s": release.get("g0_timeout_s")})
        result = row.get("result")
        if isinstance(result, dict) and "g0_wait_s" in result:
            rows.append({"segment": row["name"], "output_dir": row.get("output_dir"),
                         "g0_outcome": result.get("g0_outcome"), "g0_wait_s": result.get("g0_wait_s"),
                         "g0_timeout_s": result.get("g0_timeout_s")})

    for row in phases:
        for earlier in row.get("superseded_attempts") or ():
            add(earlier)
        add(row)
    return rows


def _check_gated_t_dead(name, result, step_d):
    """Ruling 1 / L1: one deadman, armed at G0 entry and consumed by G0, G1
    and H, is the T_dead R1 freezes. A gated run that armed any other value
    makes its duty-bar share and its tail meaningless, so refuse at once."""
    t_dead = _finite_number(((step_d or {}).get("slots") or {}).get("T_dead"), "step-d.slots.T_dead")
    armed = _finite_number((result.get("deadman") or {}).get("T_dead_s"), f"{name}.deadman.T_dead_s")
    if not math.isclose(armed, t_dead, rel_tol=1e-9, abs_tol=1e-6):
        raise Refusal(f"{name}: deadman armed T_dead_s {armed} differs from the step-d T_dead slot {t_dead}")


class VolumeWatch:
    """Ruling 20 for R1: no external volume between t0 and the terminal record.

    Reuses ``joulewise.align.apple.external_volume`` with its configuration
    pinned to status ``off`` (today's rule: any external volume refuses; the
    SSD amendment is not adopted). Every census is recorded.
    """

    def __init__(self, runner=None):
        self.runner = runner
        self.config = external_volume.validate_config(None)
        self.records = []

    def census(self, point):
        run = self.runner or (lambda argv: _run(argv))
        taken = external_volume.census(run)
        verdict = external_volume.arm_check(self.config, taken, run=run)
        self.records.append({"point": point, "verdict": verdict["verdict"], "reasons": verdict["reasons"],
                             "external": verdict["external"],
                             "mounts": [{k: row.get(k) for k in ("device", "mount_point", "fs_type", "class")}
                                        for row in taken.get("mounts", [])]})
        return verdict

    def check(self, point):
        verdict = self.census(point)
        if verdict["verdict"] != external_volume.PASS:
            raise Refusal(f"external_volume.{point}: " + "; ".join(verdict["reasons"]))


def l1_evaluation(i_d, armed_t_dead, max_tail_s):
    """Lead ruling L1 on the R1 record (executing review MEDIUM-2).

    L1 T_dead = min((1750 - I_D)/1.13544, (1800 - I_D - max_R1_tail - 10)/1.13544)
    is what W1 will arm. The duty bar's 40 % share is judged against
    min(armed, L1), and the member fit I_D + 1.13544 T_dead + tail + 10 <= 1800
    is printed for both the armed and the effective value.
    """
    from scripts.align_v4_kit import DEADMAN_FACTOR, L1_MARGIN_S, MEMBER_CAP_S, l1_t_dead
    i_d = _finite_number(i_d, "step-d.slots.I_D")
    armed = _finite_number(armed_t_dead, "step-d.slots.T_dead")
    tail = _finite_number(max_tail_s, "max_r1_tail_s")
    l1 = l1_t_dead(i_d, tail)
    effective = min(armed, l1)

    def worst(t_dead):
        return i_d + DEADMAN_FACTOR * t_dead + tail + L1_MARGIN_S

    return {"authority": "LEAD-RULINGS-1 L1", "I_D": i_d, "max_r1_tail_s": tail,
            "armed_T_dead_s": armed, "l1_T_dead_s": l1, "effective_T_dead_s": effective,
            "member_fit_worst_armed_s": worst(armed), "member_fit_worst_effective_s": worst(effective),
            "member_cap_s": MEMBER_CAP_S,
            "armed_fits": worst(armed) <= MEMBER_CAP_S + 1e-6,
            "member_fit_ok": effective > 0 and worst(effective) <= MEMBER_CAP_S + 1e-6}


def aba_adoption(legs, releases, leg_g0):
    """Ruling 16 with LEAD-RULINGS-2 R5-3: a leg whose release against the soak
    timed out, or whose own G0 did not release (so its t_decline was never
    measured), makes adoption INCONCLUSIVE; the series stays Automatic and R1
    continues."""
    unmeasured = sorted(label for label, ok in leg_g0.items() if not ok)
    rule = (high_power_adoption(legs["A1"], legs["B"], legs["A2"]) if not unmeasured else
            {"verdict": "not_evaluated", "reason": "leg(s) " + ", ".join(unmeasured) + " measured no t_decline"})
    unreleased = sorted(label for label, ok in releases.items() if not ok)
    reasons = []
    if unreleased:
        reasons.append("leg(s) " + ", ".join(unreleased) + " started without a G0 release against the soak (timeout)")
    if unmeasured:
        reasons.append("leg(s) " + ", ".join(unmeasured) + " did not release their own G0 (no turn, no t_decline)")
    if reasons:
        return {"verdict": "inconclusive", "reason": "; ".join(reasons) + "; setting stays Automatic",
                "rule_outcome": rule, "inconclusive_legs": sorted(set(unreleased) | set(unmeasured))}
    return rule


def aba_start_bars(legs):
    """RL-72 E4: one-sided cross bands and B capture bracket are acceptance bars."""
    cross = []
    try:
        for label, leg in legs.items():
            if not leg.get("g0_released"):
                raise ValueError("unreleased leg")
            for other, baseline in legs.items():
                if label == other:
                    continue
                for role in ("fast", "slow"):
                    reading = _finite_number(leg["g0_release"][role + "_c"], "release")
                    reference = _finite_number(baseline["operating_reference"][role + "_c"], "capture")
                    band = _finite_number(baseline["bands_c"]["delta_" + role + "_c"], "band")
                    cross.append({"leg": label, "against": other, "role": role,
                                  "margin_c": reference + band - reading,
                                  "pass": reading <= reference + band})
        a1, b, a2 = [legs[k]["operating_reference"]["slow_c"] for k in ("A1", "B", "A2")]
        bracket = min(a1, a2) - .5 <= b <= max(a1, a2) + .5
        return {"pass": all(row["pass"] for row in cross) and bracket,
                "cross_band": cross, "slow_capture_bracket": bracket}
    except (KeyError, TypeError, ValueError, Refusal) as error:
        return {"pass": False, "reason": str(error), "cross_band": cross, "slow_capture_bracket": False}


def executed_commit(root):
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def require_prepare_packet(path, root=ROOT):
    """Bind RL-62/73 prepare evidence to this driver's committed sources."""
    cause = "r1.prepare_packet"
    if path is None:
        raise Refusal(f"{cause}.missing: --prepare-packet is required")
    path = Path(path).resolve()
    try:
        raw = path.read_bytes()
        packet = json.loads(raw)
    except (OSError, ValueError) as error:
        raise Refusal(f"{cause}.unreadable: {error}") from error
    if (not isinstance(packet, dict) or packet.get("schema") != "joulewise.align.r1_followup_prepare.v1"
            or packet.get("status") != "FOR_LEAD_ARM"):
        raise Refusal(f"{cause}.status: requires FOR_LEAD_ARM prepare evidence")
    if packet.get("executed_commit") != executed_commit(root):
        raise Refusal(f"{cause}.executed_commit: prepare does not name this commit")
    for name in ("weight_digests", "runtime_stack"):
        check = packet.get(name)
        if not isinstance(check, dict) or check.get("ok") is not True:
            raise Refusal(f"{cause}.{name}: missing or not ok")
    from joulewise.align.apple import v4_registration
    bound = packet.get("bound_files")
    if not isinstance(bound, dict):
        raise Refusal(f"{cause}.bound_files: missing source hashes")
    for name in v4_registration.R1_EXECUTED_SOURCES:
        try:
            digest = hashlib.sha256((Path(root) / name).read_bytes()).hexdigest()
        except OSError as error:
            raise Refusal(f"{cause}.bound_files: source unavailable: {name}") from error
        if bound.get(name) != digest:
            raise Refusal(f"{cause}.bound_files: source differs: {name}")
    return {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
            "executed_commit": packet["executed_commit"],
            **{name: packet[name] for name in ("weight_digests", "runtime_stack")}}


def inadmissible_slots(results, inconclusive, thermometry, duty, u5, g0_cap):
    """The plan's per-slot bars; candidates never become admitted evidence by omission."""
    step = results.get(STEP_D_NAME, {})
    step_flags = list(step.get("episode_flags", []))
    detail = step.get("slot_detail", {})
    reasons = [f for f in step_flags if f == "r1.g0_timeout_run"]
    if not step.get("slots"):
        reasons.append("r1.step_incomplete")
    if detail.get("recovery_censored"):
        reasons.append("recovery_censored")
    if any(v.get("tau_censored") for v in detail.get("responses", {}).values()):
        reasons.append("tau_censored")
    if step.get("t_decline_status") == "unobserved":
        reasons.append("t_decline_unobserved")
    out = {name: list(reasons) for name in ("S1", "S2", "S3", "S4", "S7", "S8", "S9", "N_chunk",
                                           "t_decline", "B_D", "I_D", "T_dead", "class", "e_D")}
    out.update(S5=[], S5_fast=[], S6=[], ac_powermode=[], planning_temperature=[], U5=[],
               duty_bar=[], deadman_budget=[], l1=[], max_r1_tail_s=[], budget_fit_inputs=[], projected_mde=[],
               x_g=[], g0_cap_w1=[], **{"thermometry.D": list(reasons)})
    for name, reason in inconclusive.items():
        if name.startswith("high_power") or name == "ac_powermode":
            out["ac_powermode"].append(reason)
        if name.startswith("planning"):
            out["planning_temperature"].append(reason)
            out["U5"].append(reason)
    gated_timeout = any(results.get(name, {}).get("g0_outcome") != "released" for name, _ in GATED_D_RUNS)
    if gated_timeout or any("thermal.hold_suppressed" in str(results.get(name, {}).get("episode_flags"))
                            for name, _ in GATED_D_RUNS):
        out["S6"].append("r1.gated_timeout_or_hold_suppression")
    if u5.get("verdict") == "inconclusive":
        out["U5"].append("r1.u5_inconclusive")
    if duty.get("verdict") != "pass" or reasons:
        for name in ("duty_bar", "deadman_budget", "l1", "max_r1_tail_s", "budget_fit_inputs", "projected_mde"):
            out[name].append("r1.candidate_budget_or_duty_fallback")
    if gated_timeout or results.get("X_G_contrast", {}).get("g0_outcome") != "released":
        out["x_g"].append("r1.g0_cap_saturated")
        out["g0_cap_w1"].append("r1.g0_cap_saturated")
    if thermometry.get("bar") != "pass":
        out["thermometry.D"].append("r1.thermometry_failed")
    # The driver refuses structural failures; these feeds can make an otherwise
    # complete night provisional. Keep their exact summary codes on every slot.
    universal = []
    if any("r1.battery_feed_invalid" in r.get("feed_flags", []) for r in results.values()):
        universal.append("r1.battery_feed_invalid")
    if any("r1.agent_feed_overlap" in r.get("feed_flags", []) for r in results.values()):
        universal.append("r1.agent_feed_overlap")
    return {name: sorted(set(flags + universal)) for name, flags in out.items()}


def _set_powermode(guard, mode, label, refusal):
    guard.automatic(label) if mode == 0 else guard.high()
    observed = parse_ac_powermode(guard.records[-1].get("stdout"))
    if observed != mode:
        raise Refusal(f"{refusal}: AC powermode reads {observed}, expected {mode}")


def _check_member_powermode(name, result, mode):
    """R5-5: a model member after the A-B-A decision (and each A-B-A leg) must
    have recorded, at episode start, the AC powermode it was meant to run in
    (ruling 7). An unobserved value is not evidence (Sol critique HIGH)."""
    record = result.get("ac_powermode")
    value = record.get("value") if isinstance(record, dict) else None
    if type(value) is not int or value != mode:
        raise Refusal(f"{name}: member recorded AC powermode {value!r}, series mode is {mode}")


def _check_d_reference_consumed(name, result, step_d):
    reference = step_d.get("operating_reference") or {}
    if (result.get("reference_source") != reference.get("source_member") or
            result.get("reference_c") != reference.get("slow_c")):
        raise Refusal(f"{name}: did not consume authenticated step-D R_D")


def _check_recovery_curve(name, curve):
    """Ruling 1(c): finite [t_s, S_slow] pairs in acquisition order."""
    previous = -math.inf
    for row in curve:
        if (not isinstance(row, list) or len(row) != 2
                or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in row)
                or row[0] < previous):
            raise Refusal(f"{name}: recovery curve must contain finite [t_s, S_slow] rows with non-decreasing t_s")
        previous = row[0]


QUIET_KINDS = ("idle", "step-30b", "step-d") + tuple(
    f"d-planning-turn-r-plus-{int(offset)}c" for offset in PLANNING_START_OFFSETS_C)


def run(args):
    global _R1_WORK_DEADLINE
    chain_started = time.monotonic()
    span_cap = None   # set inside the refusal-handled region below (R7-2: a refusal is exit 3 with a record)
    marker = getattr(args, 'power_marker', None) or (args.output.parent / '.align-r1-high-power')
    marker = Path(marker).resolve()
    output = args.output.resolve()
    created = False
    record = {"schema": SCHEMA, "status": "running", "phases": [], "powermode": [], "external_volumes": []}
    watch = args.volume_watch = VolumeWatch(getattr(args, "volume_runner", None))
    results = {}
    # Resolve the runner at call time so synthetic rehearsals can replace the
    # complete command boundary (runtime, SMC journal, sudo and pmset).
    from joulewise.align.apple import powermode
    global _CHILD_HOST_LOCK
    # Lead ruling R6-7: R1 measures holding the host night lock, so no session
    # start or late launchd fire restores Automatic under its High Power legs.
    host_lock = powermode.HostLock(role="R1 driver")
    guard = PowerModeGuard(_run, marker, Path(powermode.host_marker_path()), lock=host_lock)
    record["host_state_dir"] = powermode.host_state_dir()   # lead ruling R7-10
    staged_registration = None
    old_handlers = {}
    _CHILD_TERMINATIONS.clear()   # R8-1: this run's own terminations only

    stopping = []

    def stop(signum, _frame):
        # One-shot: the first signal starts teardown. Later signals are
        # ignored so they cannot interrupt the Automatic restore (the sudo
        # child inherits SIG_IGN); the old handlers return in ``finally``.
        if stopping:
            return
        stopping.append(signum)
        for sig in old_handlers:
            signal.signal(sig, signal.SIG_IGN)
        raise KeyboardInterrupt(f"signal {signum}")

    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        old_handlers[sig] = signal.signal(sig, stop)
    try:
        # Inside the guard's try (cold pass LOW 2): a rerun into an existing
        # output directory is a recorded refusal, not a traceback.
        try:
            output.mkdir(parents=True, exist_ok=False)
        except FileExistsError as error:
            raise Refusal(f"output directory already exists: {output}") from error
        created = True
        # RL-72 E2: complete records must fit the exact span, including startup,
        # bracket/harvest/restore overhead. Reserve the declared 900 s for close.
        # Read here, inside the handler, so a config error is a recorded refusal (R7-2).
        span_cap = night_worst_case_s(args.runtime)["programmed_span_s"]
        _R1_WORK_DEADLINE = chain_started + span_cap - 900
        if not args.synthetic:
            record["prepare_packet"] = require_prepare_packet(getattr(args, "prepare_packet", None))
            from joulewise.align.apple import v4_registration
            v4_registration.verify_r1_executed_sources(ROOT, {"executed_commit": executed_commit(ROOT)})
            if runtime_config_path(args.runtime).read_bytes() != (ROOT / DEFAULT_RUNTIME_CONFIG).read_bytes():
                raise Refusal("condition 13: runtime config differs from the bound config")
        try:
            locked = host_lock.acquire()
        except OSError as error:
            raise Refusal(f"powermode.host_lock_unavailable: {error}") from error
        if not locked:
            raise Refusal("powermode.host_lock_held: another night holds the host night lock")
        _CHILD_HOST_LOCK = host_lock   # R7-5: children inherit the lock
        # Ruling 20 at t0, before any powermode or runtime work.
        watch.check("t0")
        # R6-1/R6-2 inputs, also before any powermode or runtime work.
        schedule = check_w1_schedule(args.runtime)
        precool_cap = runtime_precool_cap_s(args.runtime)
        # R7-2: the R1 G0 timeout bounds step-d and the designed start states.
        g0_timeout = runtime_g0_timeout_s(args.runtime)
        from scripts.align_v4_kit import r1_g0_timeout_s as kit_g0_timeout_s
        if g0_timeout != kit_g0_timeout_s(ROOT):
            # One constant (R7-2): the kit re-derives G0_cap_W1 with the
            # committed config's value, so a runtime config that overrides it
            # would yield a record the kit refuses after the whole night.
            raise Refusal(f"R7-2: runtime config {G0_TIMEOUT_KEY} {g0_timeout} differs from the committed "
                          f"{DEFAULT_RUNTIME_CONFIG} value {kit_g0_timeout_s(ROOT)}")
        args.segment_bounds = segment_bounds(g0_timeout, runtime_step_deadman_s(args.runtime))
        with guard:
            soak_reference = None
            legs, releases, leg_g0, adoption, series_mode = {}, {}, {}, None, None
            precool = {}
            inconclusive = {}     # R6-2: calibration segment -> reason
            skipped = {}          # gated runs and X-G not run without step-d slots
            g0_ok = {}            # R6-1: gated run / X-G -> its G0 released
            follows = {}          # R6-1: gated run / X-G -> the D turn it follows (None: no D turn)
            pending = {}
            units = {unit[0][0]: unit for unit in admission_units(args.runtime)}
            last_d_turn = None    # the latest model segment, if it dispatched a D turn
            for name, kind, duration, workload_class in phase_plan(args.include_4bit, precool_cap_s=precool_cap):
                if kind in contract.HIGH_POWER_KINDS:
                    # Ed ruling: A-B-A, Automatic / High Power / Automatic.
                    # Ruling 16: each leg starts only after a G0-style release
                    # against the soak; ruling 8: each leg avoids the OS batch
                    # window, journals load and is redone (after another
                    # release) on sustained background load.
                    label = name.rsplit("_", 1)[-1]
                    mode = dict(HIGH_POWER_LEGS)[label]
                    _set_powermode(guard, mode, f"{label}.after_set", f"high_power.{label}")
                    results[name], row = _segment(args, output, name, kind, None, "heavy", record, quiet=True,
                                                  soak_reference=soak_reference, release_first=False,
                                                  extra={"powermode": mode},
                                                  bound_s=aba_leg_bound_s(args.runtime))
                    _check_member_powermode(name, results[name], mode)
                    releases[label] = True
                    leg_g0[label] = results[name].get("g0_released")
                    if not isinstance(leg_g0[label], bool):
                        raise Refusal(f"{name}: g0_released must be boolean")
                    legs[label] = results[name]["t_decline_s"] if leg_g0[label] else None
                    if not leg_g0[label]:
                        inconclusive[name] = "r1.g0_timeout_run" if "r1.g0_timeout_run" in results[name].get(
                            "episode_flags", []) else "G0 unreleased"
                    if label == HIGH_POWER_LEGS[-1][0]:
                        adoption = aba_adoption(legs, releases, leg_g0)
                        starts = aba_start_bars({label: results[f"high_power_{label}"] for label, _ in HIGH_POWER_LEGS})
                        adoption["start_state_bars"] = starts
                        if not starts["pass"]:
                            adoption.update(verdict="inconclusive", reason="RL-72 E4: A-B-A start-state bars failed")
                        if adoption["verdict"] == "inconclusive":
                            inconclusive["ac_powermode"] = adoption["reason"]
                        # R5-5: the rest of R1's D measurements run under the
                        # adopted series mode (ruling 7 + 16).
                        series_mode = 2 if adoption["verdict"] == "adopt" else 0
                        _set_powermode(guard, series_mode, "series.after_set", "series")
                    continue
                if kind == "calibration-post" and series_mode == 2:
                    _set_powermode(guard, 0, "series.restored", "series_restore")
                if (kind in contract.PLANNING_KINDS or kind in contract.GATED_D_KINDS or
                    kind in ("x-g", "idle-until-soak")) and results.get(STEP_D_NAME, {}).get("reference_unobserved"):
                    skipped[name] = "thermal.window_reference_unobserved"
                    inconclusive[name] = skipped[name]
                    record["phases"].append({"name": name, "class": workload_class, "skipped": skipped[name]})
                    continue
                if (name in GATED_NAMES or kind == "x-g") and not results.get(STEP_D_NAME, {}).get("slots"):
                    skipped[name] = "step-D incomplete: no candidate budgets"
                    inconclusive[name] = skipped[name]
                    record["phases"].append({"name": name, "class": workload_class, "skipped": skipped[name]})
                    continue
                quiet = kind in QUIET_KINDS and not (kind == "idle" and name != "idle_soak")
                model = kind not in ("calibration-pre", "calibration-post", "idle", "idle-until-soak")
                extra = {"powermode": series_mode} if model and series_mode is not None else None
                # (step_30b runs before the decision, in Automatic, unchecked as before.)
                if name not in pending:
                    pending.update(_admission_unit(args, output, units[name], record,
                                                   soak_reference=soak_reference, extra=extra))
                results[name], row = pending.pop(name)
                flags = results[name].get("episode_flags", [])
                if "r1.g0_timeout_run" in flags or "r1.preheat_cap_reached" in flags:
                    inconclusive[name] = ",".join(f for f in flags if f.startswith("r1."))
                if _g0_inconclusive(name, kind, results[name]):
                    inconclusive[name] = results[name].get("reason", "G0 unreleased")
                if name == "idle_soak":
                    soak_reference = write_soak_reference(output, row)
                if model and series_mode is not None:
                    _check_member_powermode(name, results[name], series_mode)
                if name in GATED_NAMES or kind == "x-g":
                    _check_d_reference_consumed(name, results[name], results[STEP_D_NAME])
                    g0_ok[name] = _check_schedule(name, results[name], schedule,
                                                  "X-G" if kind == "x-g" else "D")
                    follows[name] = last_d_turn
                    reason = schedule_inconclusive_reason(g0_ok[name], follows[name])
                    if reason:
                        inconclusive[name] = reason
                if model:
                    # R6-1: did this segment end with a D turn? (A timed-out G0
                    # dispatches none, so the next gated run would not follow one.)
                    # A gated run counts only with observed D work (decode
                    # tokens): a released G0 alone may still dispatch nothing
                    # (Sol critique of round 6).
                    last_d_turn = name if (kind in D_TURN_KINDS and not results[name].get("reference_unobserved")
                                           and not (name in GATED_NAMES and not (
                                               g0_ok[name] and type(results[name].get("decode_tokens")) is int
                                               and results[name]["decode_tokens"] > 0))) else None
                if name == STEP_D_NAME and not results[name].get("reference_unobserved"):
                    _check_step_d(results[name])
                if name in GATED_NAMES:
                    _check_gated_t_dead(name, results[name], results.get(STEP_D_NAME))
                if kind == "idle-until-soak":
                    precool[name] = _check_precool(name, results[name])

            # Same thin runtime seam owns the pilot-style authenticated harvest;
            # the driver records but never re-implements calibration custody.
            harvested = _invoke(args.runtime, "harvest", output / "harvest", soak_reference=soak_reference,
                                watch=args.volume_watch)
            record["phases"].append({"name": "harvest", "class": "light", "result": harvested})
        step_d_ok = isinstance(results.get(STEP_D_NAME, {}).get("slots"), dict)
        planning = {offset: f"planning_turn_R_plus_{int(offset)}C" for offset in PLANNING_START_OFFSETS_C}
        planning_inconclusive = sorted(name for name in planning.values() if name in inconclusive)
        if planning_inconclusive:
            # R6-2: a designed start state that was not reached gives beta_T no
            # point; U5 is INCONCLUSIVE and the kit decides downstream.
            temperature_summary = {"label": "PRINT_ONLY_R1_PLANNING_TEMPERATURE_SECONDARY", "status": "inconclusive",
                                   "inconclusive_states": planning_inconclusive}
        else:
            try:
                temperature_summary = planning_temperature_summary([results[planning[o]] for o in PLANNING_START_OFFSETS_C])
            except Refusal as error:
                inconclusive["planning_temperature"] = str(error)
                planning_inconclusive = ["planning_temperature"]
                temperature_summary = {"status": "inconclusive", "reason": str(error)}
        temperature_summary["run_order_offsets_c"] = list(PLANNING_RUN_ORDER_C)
        if step_d_ok:
            slots = derive_slots(results.get(STEP_D_NAME) or {})
            gated = {name: results[name] for name, _ in GATED_D_RUNS}
            reasons = {name: schedule_inconclusive_reason(g0_ok[name], follows[name]) for name in g0_ok}
            uncooled = sorted(name for name in gated if reasons[name])
            max_tail = max(deadman_summary(name, result)["phases_s"]["tail"] for name, result in gated.items())
            l1 = l1_evaluation(slots["I_D"], slots["T_dead"], max_tail)
            print("R1 L1: " + json.dumps(l1, sort_keys=True), flush=True)
            deadman = [deadman_summary(name, result, duty_t_dead=l1["effective_T_dead_s"],
                                       inconclusive_reason=reasons[name]) | {"follows_d_turn": follows[name]}
                       for name, result in gated.items()]
            verdict = duty_verdict(deadman)
            duty = {"declared": DUTY_BAR, "pass": verdict == "pass", "verdict": verdict,
                    "three_turn_run_present": three_turn_run_present(deadman),
                    "turn_check_authority": "RL-149 section 1.5",
                    "inconclusive_runs": uncooled, "reference": "step-D R_D (RL-59)",
                    "schedule": schedule, "duty_T_dead_s": l1["effective_T_dead_s"],
                    "fallback_order": list(DUTY_FALLBACK_ORDER)}
            mde = projected_mde(results[STEP_D_NAME].get("e_D_j_per_token"), gated)
            u5 = (u5_verdict(temperature_summary, gated, inconclusive_runs=uncooled) if not planning_inconclusive else
                  {"criterion": "U5", "c": U5_C, "authority": "LEAD-RULINGS-1 L2", "verdict": "inconclusive",
                   "reason": "designed start state(s) INCONCLUSIVE (R6-2): " + ", ".join(planning_inconclusive)})
            from joulewise.align.apple.r1_runtime import registered_s6
            s6 = {**registered_s6()["s6_tuning"], "S6_c": slots["S6"], **gate_wait_medians(gated)}
            if not args.synthetic and results[STEP_D_NAME].get("slot_detail", {}).get("S6_tuning", {}).get(
                    "status") == "new_sensor_default":
                s6 = {**results[STEP_D_NAME]["slot_detail"]["S6_tuning"], **gate_wait_medians(gated)}
            fit_inputs = budget_fit_inputs(results[STEP_D_NAME], gated, deadman)
            thermometry_d = thermometry_record(STEP_D_NAME, results[STEP_D_NAME])
            x_g = {"status": "inconclusive" if reasons["X_G_contrast"] else "measured",
                   "inconclusive_reason": reasons["X_G_contrast"],
                   "g0_outcome": results["X_G_contrast"]["g0_outcome"], "follows_d_turn": follows["X_G_contrast"],
                   "inter_member_idle_s": results["X_G_contrast"]["inter_member_idle_s"],
                   "g0_wait_s": results["X_G_contrast"].get("g0_wait_s"),
                   "authority": "LEAD-RULINGS-2 R6-1", **x_g_evidence(results["X_G_contrast"])}
            g0_cap = w1_g0_cap(deadman, x_g, g0_timeout)
        else:
            # R6-2: recorded, not refused mid-night. With no step-d slots the
            # kit refuses W1 (no slots, no thermometry bar, no duty bar).
            l1 = max_tail = mde = fit_inputs = thermometry_d = None
            from joulewise.align.apple.r1_runtime import registered_s6
            s6 = registered_s6()["s6_tuning"]
            slots = {"S6": registered_s6()["slots"]["S6"]}
            arm_config = json.loads(runtime_config_path(args.runtime).read_text())
            if not args.synthetic:
                slots = {"S6": arm_config.get("slow_band_floor_c", 1.0)}
                s6 = {"status": "new_sensor_default", "authority": "RL-78 default band",
                      "S6_c": slots["S6"], "receipt_transferred": False}
            deadman = []
            duty = {"declared": DUTY_BAR, "pass": False, "verdict": "inconclusive", "inconclusive_runs": [],
                    "reason": "step-d INCONCLUSIVE: the gated D runs did not run", "schedule": schedule,
                    "fallback_order": list(DUTY_FALLBACK_ORDER)}
            u5 = {"criterion": "U5", "c": U5_C, "authority": "LEAD-RULINGS-1 L2", "verdict": "inconclusive",
                  "reason": "step-d INCONCLUSIVE (R6-2): no replay pair ran"}
            x_g = {"status": "not_run", "reason": skipped.get("X_G_contrast")}
            g0_cap = None
        # Ruling 20: the last census before the slots are frozen.
        watch.check("before_registration")
        battery = battery_report(results, harvested)
        thermometry = {"D": thermometry_d,
                       "30B_record_only": thermometry_record("step_30b", results["step_30b"]),
                       "authority": "protocol v4 WP14(a) R1 paragraph (LEAD-RULINGS-2 R5-5)"}
        # Either null pick fails R1's thermometry bar (D only; the 30B is record-only).
        thermometry["bar"] = thermometry_d["status"] if thermometry_d else "inconclusive"
        thermometry["flags"] = list((thermometry_d or {}).get("flags") or [])
        if thermometry_d and picks_aliased(thermometry_d) and ruled_alias_pair(thermometry_d):
            # RL-145 close sections 5 and 10, RL-149 section 5 item 12: the one ruled alias pair
            # (the fast key and its lexically first alias, confirmed this session) keeps the bar.
            thermometry["bar_basis"] = ("RL-145 ruled alias pair: one thermometer under two key names, "
                                        "confirmed by the session's RL-145 night confirmation")
            thermometry["flags"].append("r1.picks_alias_pair_rl145")
        elif thermometry_d and picks_aliased(thermometry_d):
            # LEAD-RULINGS-2 R8-6 (round-7 cold LOW-3): two picks that are one
            # sensor (R7-13) are not two thermometers; the bar fails at R1, not
            # only at the kit after the night.
            thermometry["bar"] = "fail"
            thermometry["bar_reason"] = ("s_fast and s_slow are one key or in one alias group "
                                         "(LEAD-RULINGS-2 R7-13, R8-6)")
            thermometry["flags"].append("r1.picks_aliased")
        if thermometry_d and thermometry_d.get("sensor_pick_changed"):
            inconclusive["thermometry.D"] = "r1.sensor_pick_changed: smoke selection not reproduced"
        if thermometry["bar"] != "pass":
            inconclusive["thermometry.D"] = "r1.thermometry_failed: research lead ruling required"
        # Ruling 7 + 16: the frozen series AC powermode is the A-B-A outcome.
        ac_powermode = None if adoption["verdict"] == "inconclusive" else (2 if adoption["verdict"] == "adopt" else 0)
        for name, result in results.items():
            feed_flags = []
            battery_feed = result.get("battery")
            if isinstance(battery_feed, dict) and (battery_feed.get("valid_samples", 0) == 0 or any(
                    not (battery_feed.get(edge) or {}).get("ac") or
                    (battery_feed.get(edge) or {}).get("state") == "discharging" for edge in ("first", "last"))):
                feed_flags.append("r1.battery_feed_invalid")
            for census in result.get("census", []):
                if any(Path(proc.get("comm", "")).name.lower().startswith(("codex", "claude", "t3"))
                       for proc in census.get("processes", [])):
                    feed_flags.append("r1.agent_feed_overlap")
            result["feed_flags"] = sorted(set(feed_flags))
            if feed_flags:
                inconclusive[name] = ",".join(sorted(set(feed_flags + [inconclusive[name]] if name in inconclusive else feed_flags)))
        registration = {"schema": SCHEMA, "source": "R1 synthetic rehearsal" if args.synthetic else "R1 hardware rehearsal",
                        "executed_commit": executed_commit(ROOT),
                        "slots": slots, "slot_names": list(SLOT_NAMES),
                        "slots_ac_powermode": series_mode,
                        "mode_adoption_provisional": adoption["verdict"] == "inconclusive",
                        "planning_temperature": temperature_summary, "u5": u5, "ac_powermode": ac_powermode,
                        "high_power": {"t_decline_s": legs, "g0_released": releases, "leg_g0_released": leg_g0,
                                       **adoption},
                        "deadman_budget": deadman, "duty_bar": duty, "l1": l1,
                        "max_r1_tail_s": max_tail, "budget_fit_inputs": fit_inputs,
                        "x_g": x_g, "g0_cap_w1": g0_cap, "g0_waits": g0_wait_record(record["phases"]),
                        "inconclusive_segments": inconclusive, "skipped_segments": skipped,
                        "calibration_precools": {name: released for name, released in precool.items()},
                        "thermometry": thermometry, "s6_tuning": s6,
                        "inadmissible_slots": inadmissible_slots(results, inconclusive, thermometry, duty, u5, g0_cap),
                        "external_volumes": watch.records,
                        "projected_mde": mde, "battery": battery}
        reg = args.registration.resolve()
        reg.parent.mkdir(parents=True, exist_ok=True)
        # Round-5 executing review LOW-6 (lead ruling R6-8): r1_result.status
        # is the authority for committing r1_slots, so the registration is
        # written only after a terminal record that says complete (finally).
        staged_registration = (reg, json.dumps(registration, indent=2, sort_keys=True) + "\n")
        record.update(status="complete", registration_path=str(reg),
                      registration_sha256=hashlib.sha256(staged_registration[1].encode()).hexdigest(),
                      **{k: v for k, v in registration.items() if k not in ("schema", "source")})
        return 0
    except BaseException as error:
        record.update(status="refused" if isinstance(error, Refusal) else "aborted",
                      error=f"{type(error).__name__}: {error}")
        return 3 if isinstance(error, Refusal) else 4
    finally:
        # Fable cold pass round 4 LOW-4: a first signal that arrives in this
        # teardown (after a normal completion or refusal) must not skip the
        # restore or r1_result.json. From here on signals are ignored, as
        # after a first signal, so the sudo restore child inherits SIG_IGN.
        if not stopping:
            stopping.append("teardown")
            for sig in old_handlers:
                signal.signal(sig, signal.SIG_IGN)
        # A second idempotent attempt covers setup failures before __enter__ and
        # exceptions raised by context teardown itself.
        _CHILD_HOST_LOCK = None
        close_started = time.monotonic()
        try:
            if host_lock.held and not guard.deferred:
                # Round-7 executing review: a deferred guard (no retake, or a
                # W1 session's marker after the retake) is never restored by
                # this second attempt, which would bypass both checks.
                guard.restore()
            if guard.deferred:
                record["restore_deferred"] = next(
                    (r["reason"] for r in reversed(guard.records) if r.get("point") == "restore_deferred"),
                    "the host night lock could not be retaken (a child of this run may still hold it); the "
                    "markers are left for the dead-man or the next session start (lead ruling R7-5)")
            elif not host_lock.held:
                # R6-7 (round-6 Sol critique): without the host night lock this
                # run never changed the mode, and another night may be
                # measuring under High Power; never restore under it.
                record["restore_skipped"] = "host night lock not held: this run never changed the AC powermode"
        except BaseException as error:  # noqa: BLE001 - the terminal record must still be written
            record.setdefault("teardown_errors", []).append(f"restore: {type(error).__name__}: {error}")
        record["powermode"] = guard.records
        if _CHILD_TERMINATIONS:
            record["child_terminations"] = list(_CHILD_TERMINATIONS)   # lead ruling R8-1
        try:
            watch.census("terminal")  # recorded, never judged here
        except Exception as error:  # noqa: BLE001 - the terminal record must still be written
            watch.records.append({"point": "terminal", "verdict": "UNMEASURED",
                                  "reasons": [f"{type(error).__name__}: {error}"]})
        record["external_volumes"] = watch.records
        record["close_s"] = time.monotonic() - close_started
        record["chain_wall_s"] = time.monotonic() - chain_started
        if record["close_s"] > 900 or (span_cap is not None and record["chain_wall_s"] > span_cap):
            record.update(status="aborted", error="RL-72 E2: close/span overhead cap exceeded")
        _R1_WORK_DEADLINE = None
        _write_result(output, record, created)
        if staged_registration is not None and record.get("status") == "complete":
            _commit_registration(*staged_registration)
        host_lock.release()
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)
        if staged_registration is not None and record.get("status") != "complete":
            return 4


def _commit_registration(path, text):
    """Exec LOW-6: r1_slots.json appears (atomically) only beside a complete
    r1_result.json; a run that ends any other way never leaves one."""
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(text)
    os.replace(temporary, path)


def _write_result(output, record, created):
    """r1_result.json; never overwrites an earlier run's terminal record."""
    text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    path = output / "r1_result.json"
    if created:
        path.write_text(text)
        return
    try:
        with path.open("x") as handle:
            handle.write(text)
    except (FileExistsError, FileNotFoundError, NotADirectoryError):
        sys.stderr.write("R1 refused without a writable new r1_result.json: " + record.get("error", "") + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--registration", type=Path,
                        help="default: <output>/r1_slots.json")
    parser.add_argument("--power-marker", type=Path,
                        help="persistent SIGKILL recovery marker (default: beside output)")
    runtime = parser.add_mutually_exclusive_group(required=True)
    runtime.add_argument("--runtime", nargs="+",
                         help="WP15 runtime argv override; receives --r1-kind/--output[/--duration-s]"
                              "[/--soak-reference] (docs/align/r1_runtime_contract.md)")
    runtime.add_argument("--runtime-entrypoint", type=Path, metavar="INPUTS_JSON",
                         help="read the runtime argv list from INPUTS_JSON WP15.runtime_entrypoint")
    parser.add_argument("--include-4bit", action="store_true")
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--prepare-packet", type=Path,
                        help="RL-62/73 FOR_LEAD_ARM packet from align_r1_followup_kit prepare")
    args = parser.parse_args(argv)
    if args.registration is None:
        args.registration = args.output / "r1_slots.json"
    if args.runtime_entrypoint is not None:
        try:
            args.runtime = runtime_argv_from_inputs(args.runtime_entrypoint)
        except (OSError, ValueError, Refusal) as error:
            print(f"align_r1_rehearsal: refused: {error}", file=sys.stderr)
            return 3
    from joulewise.align.apple import powermode
    try:
        powermode.host_state_dir()   # lead ruling R7-10: refuses an override in production
    except powermode.HostStateOverrideRefused as error:
        print(f"align_r1_rehearsal: refused: {error}", file=sys.stderr)
        return 3
    return run(args)


def runtime_argv_from_inputs(path):
    """``inputs.WP15.runtime_entrypoint`` is the runtime argv as a list (Fable LOW-3).

    Element 0 is a repo-relative Python script, run by this driver's own
    interpreter (``$PY``, the pinned venv) with ``-B``; the remaining elements
    are passed verbatim (repo-relative paths are resolved by the runtime).
    """
    inputs = json.loads(Path(path).read_text())
    argv = (inputs.get("WP15") or {}).get("runtime_entrypoint")
    if not isinstance(argv, list) or not argv or not all(isinstance(a, str) and a for a in argv):
        raise Refusal("inputs.WP15.runtime_entrypoint must be a non-empty argv list of strings")
    script = Path(argv[0])
    if script.is_absolute() or ".." in script.parts or script.suffix != ".py" or not (ROOT / script).is_file():
        raise Refusal("inputs.WP15.runtime_entrypoint[0] must be a repo-relative Python script")
    return [sys.executable, "-B", str(ROOT / script), *argv[1:]]


if __name__ == "__main__":
    from joulewise.align.apple import powermode as _powermode
    _powermode.mark_production_entry("align_r1_rehearsal")   # lead ruling R7-10
    raise SystemExit(main())
