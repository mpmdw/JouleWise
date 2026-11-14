"""WP15 R1 runtime: one ALIGN v4 R1 segment per invocation.

The R1 driver (``scripts/align_r1_rehearsal.py``) runs, once per segment,

    <runtime argv> --r1-kind KIND --output DIR [--duration-s N] [--soak-reference FILE]

and reads one JSON object from stdout (``docs/align/r1_runtime_contract.md``;
the field table is ``r1_runtime_contract.KIND_FIELDS``).

This module adds orchestration only. Every measurement goes through the
production ALIGN paths:

- model segments run ``joulewise.controller.run_benchmark`` with the ALIGN
  episode adapter (``EpisodeRuntimeAdapter`` -> ``MlxEndpoint`` -> mlx_lm),
  ``ThermalRegistry``/``ThermalSession`` (SMC sidecar, G0/G1/H gates and the
  powermetrics status tap), the episode deadman, the powermetrics telemetry
  adapter and the bundle custody writer;
- sensor-only segments run the same ``ThermalSession`` SMC collector;
- fields are read back from the finished bundle with the existing readers
  (``read_episode_bundle``, ``thermal_desk.read_bundle_record`` and
  ``native_pm_samples``, ``attribute_episode``);
- the CPU load journal and census are ``r1_runtime_contract.LoadJournal``.

The runtime writes only inside ``DIR``. Its terminal record is
``DIR/runtime_custody.json`` (status and the SHA-256 of every other file in
``DIR``), written last on every exit path including TERM. On the first
TERM/INT/HUP the runtime stops work, lets the controller salvage and finalize
an open bundle (which stops powermetrics and closes the SMC sidecar), closes
its own collectors, writes the terminal record and exits 128 + signal; a
watchdog forces the exit after ``TERM_TEARDOWN_S`` so the driver's 20 s grace
is never needed.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
from statistics import median
import subprocess
import sys
import threading
import time
import traceback
from types import SimpleNamespace

from joulewise.align.apple import r1_runtime_contract as contract

ROOT = Path(__file__).resolve().parents[3]
CONFIG_SCHEMA = "joulewise.align.r1_runtime_config.v1"
RESULT_SCHEMA = "joulewise.align.r1_runtime_result.v1"
CUSTODY_SCHEMA = "joulewise.align.r1_runtime_custody.v1"
SOAK_REFERENCE_SCHEMA = "joulewise.align.r1_soak_reference.v1"
RESULT_NAME = "runtime_result.json"
CUSTODY_NAME = "runtime_custody.json"
# The accepted step-d attempt always owns this canonical directory (driver).
STEP_D_SEGMENT = "step_D_prefill_10k_decode_4096"
STEP_30B_SEGMENT = "step_30b"
OPERATING_REFERENCE_SOURCE = "r1_step_30b_pre_warmup"
R1_REGISTRATION = ROOT / "configs/campaigns/align_v4/registration/r1_slots.json"
NS = 1_000_000_000
TERM_TEARDOWN_S = 15.0       # forced exit, inside the driver's 20 s TERM grace
WATCHDOG_HARD_S = 4.0        # the watchdog's own teardown: 15 s + 4 s < the 20 s grace
G0_PREROLL_S = 65            # a G0 judges the slope over the preceding 60 s
# Protocol v4 :243-251 (LEAD-RULINGS-2 R5-5): around both planning-turn steps
# (30B and D) R1 journals the last 300 s of quiet before prefill and a fixed
# 600 s recovery after the last decode (S4 tau, S7 G_turn and the inventory
# classification all read that recovery).
STEP_QUIET_S = 300
RECOVERY_CAP_S = 600
COOLDOWN_CAP_S = 1500        # ruling 1(c)
PREHEAT_CAP_S = 900
# 2026-11-10 ruling §3.3 extends the existing 1,200 s R7-2 timeout
# to every model member. Only the sensors-only release keeps 600 s.
G0_TIMEOUT_CONFIG_KEY = "g0_timeout_s"
G0_TIMEOUT_KINDS = ("step-30b", "step-d", "x-g", "d-4bit", *contract.HIGH_POWER_KINDS,
                    *contract.GATED_D_KINDS, *contract.PLANNING_KINDS)
PREHEAT_MARGIN_C = 0.5
PLANNING_FAST_CEILING_C = 150.0   # designed start states band S_slow only (ruling 6)
DEADMAN_FACTOR = 1.13544
MEMBER_CAP_S = 1800
BAND_FLOOR_C = 1.0           # FD 2.6: delta_k = max(1.0 C, 3 SD_k)
EXIT_REFUSED, EXIT_FAILED = 2, 3
PMSET_BATT = ("/usr/bin/pmset", "-g", "batt")
STEP_TASK_FACTORY = "joulewise.align.apple.r1_runtime:step_task"
SYNTHETIC_TASK_FACTORY = "tests.align.w1_synthetic:make_task"
MODEL_KINDS = ("step-30b", "step-d", "x-g", "d-4bit", *contract.GATED_D_KINDS,
               *contract.PLANNING_KINDS, *contract.HIGH_POWER_KINDS)
# Ruling 4(b): the drain rate is reported under D and under the 30B.
BATTERY_DRAIN_KINDS = ("step-30b", "step-d", *contract.GATED_D_KINDS)
# Round-4 executing review HIGH-1 (and the round-4 Fable cold pass HIGH-1):
# a step, planning-turn or A-B-A member must be one complete, ungated-by-fault
# turn. Any of these episode flags means the measured turn was cut short or
# its thermal state was not observed, so its energy, step response and
# t_decline are not the designed measurement. (Gated D runs and X-G are
# exempt: their truncation is the duty-bar evidence itself.) A malformed or
# refused tool-call flag does not cut the decode and is not listed.
INCOMPLETE_MEMBER_FLAGS = ("episode.deadman:", "episode.decode_budget:", "episode.g0_unreleased:",
                           "episode.time_guard:", "episode.context_limit:", "episode_error:", "endpoint_error:",
                           "thermal.start_gate_timeout", "thermal.gate_timeout:", "thermal.hold_timeout:",
                           "thermal.state_unobserved", "thermal.collector_failed", "thermal.custody_invalid",
                           "thermal.status_source_missing")


TIMEOUT_RUN_KINDS = ("step-30b", "step-d", *contract.HIGH_POWER_KINDS, *contract.PLANNING_KINDS)


# Smoke admission budget (RUN_STATE 276), on the kit's clock from its start.
# Part A must fit the 30B predecessor (551.3 s in smoke 276), step D's start-up
# to G0 entry (521.6 s; 518.1 and 516.0 s in the R1 night), the full 1,200 s
# G0 cap and Part A's close after G0 (134.6 s in the R1 night): 2,407.5 s.
# 3,000 s leaves 592.5 s of slack. Part B uses it up to G0 release, then
# smoke_post_g0_budget. The 1,800 s it replaces predates RL-84 P-1's predecessor
# in Part A. An engineering watchdog on the smoke only (RL-84 P-5: the ruled
# 1,200 s is the G0 cap and nothing else); no production member reads it.
SMOKE_ADMISSION_S = 3000
# RUN_STATE 278: the smoke's watchdogs leave ITIMER_REAL to its one owner, the
# episode deadman (budget.EpisodeDeadman.guard refuses to arm over an active
# timer, WP8), and reach the main thread on this signal instead.
SMOKE_WATCHDOG_SIGNAL = signal.SIGUSR1


class SmokeWatchdog:
    """Smoke-only wall watchdog on the monotonic clock, off ITIMER_REAL.

    ``set(seconds)`` behaves like ``setitimer(ITIMER_REAL, seconds)`` did for
    the smoke: a positive value (re)arms one deadline, 0 disarms. At the
    deadline a daemon thread sends SMOKE_WATCHDOG_SIGNAL once to the main
    thread, whose handler raises; ``stop()`` ends the thread, after which no
    signal is sent and ``active`` is False (the handler ignores a late one)."""

    def __init__(self, *, signum=SMOKE_WATCHDOG_SIGNAL, monotonic=time.monotonic,
                 send=signal.pthread_kill, main_ident=None):
        self.signum, self.monotonic, self.send = signum, monotonic, send
        self.main_ident = main_ident if main_ident is not None else threading.main_thread().ident
        self.active, self.deadline = True, None
        self._wake = threading.Condition()
        self._thread = threading.Thread(target=self._run, name="r1-smoke-watchdog", daemon=True)
        self._thread.start()

    def set(self, seconds):
        with self._wake:
            self.deadline = self.monotonic() + seconds if seconds > 0 else None
            self._wake.notify_all()

    def stop(self):
        with self._wake:
            self.active, self.deadline = False, None
            self._wake.notify_all()
        self._thread.join(timeout=5.0)

    def _run(self):
        with self._wake:
            while self.active:
                if self.deadline is None:
                    self._wake.wait()
                    continue
                left = self.deadline - self.monotonic()
                if left > 0:
                    self._wake.wait(min(left, 1.0))
                    continue
                self.deadline = None
                self.send(self.main_ident, self.signum)


def smoke_post_g0_budget(quiet_s, rearm_s):
    """Finite Part B watchdog, derived from the phases after G0 release."""
    if rearm_s is None or not _finite(rearm_s) or rearm_s <= 0:
        raise RuntimeFailure("smoke Part B requires a positive re-armed turn bound")
    phases = {"quiet": quiet_s, "turn": rearm_s, "recovery": RECOVERY_CAP_S,
              "classification_and_close": 120}
    return {**phases, "total": sum(phases.values())}


def allow_g0_timeout_run(session, row):
    """RL-72 E3: no fault, no pseudo-reference, observed timeouts only."""
    if row.get("outcome") != "timeout" or any(
            flag.startswith(("thermal.state_unobserved", "thermal.collector_failed",
                             "thermal.status_source_missing", "thermal.custody_invalid"))
            for flag in session.flags):
        return False
    if "r1.g0_timeout_run" not in session.flags:
        session.flags.append("r1.g0_timeout_run")
    return True


def incomplete_member_reasons(member):
    """Why ``member`` is not one complete measured turn (empty when it is)."""
    reasons = [] if member.status == "succeeded" else [f"member_status:{member.status}:{member.failure_reason}"]
    if len(member.ep.turns) != 1:
        reasons.append(f"turns:{len(member.ep.turns)}")
    reasons += sorted({flag for flag in member.ep.flags if flag.startswith(INCOMPLETE_MEMBER_FLAGS)})
    return reasons


# LEAD-RULINGS-2 R6-2: the reasons a member gives when its G0 timed out and
# nothing else went wrong (no turn was dispatched). Only such a step-d or
# designed start state is INCONCLUSIVE; any other incomplete member still
# fails the segment (exit 3).
G0_TIMEOUT_REASONS = ("turns:0", "thermal.start_gate_timeout")


def g0_timeout_only(reasons):
    """True when ``reasons`` (``incomplete_member_reasons``) say only "G0 timed out"."""
    return (any(r == "thermal.start_gate_timeout" or r.startswith("episode.g0_unreleased:") for r in reasons)
            and all(r in G0_TIMEOUT_REASONS or r.startswith("episode.g0_unreleased:") for r in reasons))
def only_g0_unreleased(incomplete, g0_outcome):
    """Round-5 executing review LOW-2 (lead ruling R6-8): True only when every
    incomplete reason is one an unreleased own G0 produces by itself (the stop
    before turn 0, no turn, and the G0's own timeout or deadman flag). Any
    other reason (a collector, custody or member failure) still refuses."""
    allowed = {"episode.g0_unreleased:0", "turns:0"}
    allowed |= {"timeout": {"thermal.start_gate_timeout"}, "deadman": {"episode.deadman:0"},
                "unobserved": {"thermal.state_unobserved"}}.get(g0_outcome, set())
    return "episode.g0_unreleased:0" in incomplete and set(incomplete) <= allowed


DEFERRED_SIGNALS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)
CLOSE_SIGNAL_DEFER_MAX_S = 10.0


def close_managed_session(managed, after=None):
    """Round-5 executing review LOW-3 (lead ruling R6-8): close one managed
    session with TERM/INT/HUP held back for at most 10 s (R7-8), protecting
    the powermetrics adapter between dropping its process handle and stopping
    the process. A signal that arrives meanwhile is
    re-raised to the previous handler once the close has finished (or
    failed), or at the bound so the teardown watchdog can arm even if the
    close blocks. When the deferred handler is the runtime's ``Termination``,
    its teardown watchdog is armed as soon as the first signal is held (lead
    ruling R8-3). Python handlers run on the main thread, so the deferral swaps
    the handlers there (whichever thread the kernel delivers to); off the
    main thread the close runs as before. ``after`` runs once the close has
    returned, before held signals are delivered if the bound has not expired."""
    if threading.current_thread() is not threading.main_thread():
        managed.close()
        if after is not None:
            after()
        return
    pending, previous = [], {}
    timer = None
    expired = restored = False
    main_ident = threading.main_thread().ident
    delivery_lock = threading.Lock()

    def restore_and_deliver():
        nonlocal restored
        if restored:
            return
        restored = True
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        for signum in dict.fromkeys(pending):
            signal.raise_signal(signum)

    def expire():
        nonlocal expired
        # Serialize against normal completion so an in-flight timer cannot
        # send an extra signal after the previous handlers have been restored.
        with delivery_lock:
            if not restored:
                expired = True
                # Target the main thread to interrupt its blocking close;
                # process-directed delivery could land on this timer thread.
                signal.pthread_kill(main_ident, pending[0])

    def hold(signum, _frame):
        nonlocal timer
        pending.append(signum)
        if len(pending) == 1:
            # Lead ruling R8-3: the runtime's teardown watchdog arms when the
            # first signal is held, not when the deferral ends.
            owner = getattr(previous.get(signum), "__self__", None)
            if isinstance(owner, Termination):
                owner.arm(signum)
        if expired:
            # Only the main thread can restore Python signal handlers. The
            # timer's wakeup replays pending signals here, never in the timer.
            restore_and_deliver()
        elif timer is None:
            timer = threading.Timer(CLOSE_SIGNAL_DEFER_MAX_S, expire)
            timer.daemon = True
            timer.start()
    try:
        for sig in DEFERRED_SIGNALS:
            previous[sig] = signal.signal(sig, hold)
        managed.close()
        if after is not None:
            after()
    finally:
        with delivery_lock:
            if timer is not None:
                timer.cancel()
            restore_and_deliver()


class Refused(RuntimeError):
    """Fail closed: an input is pending or invalid (exit 2)."""


class RuntimeFailure(RuntimeError):
    """The segment ran but cannot supply its contract fields (exit 3)."""


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


class InventoryJournal:
    """Protocol v4 :243-251 (LEAD-RULINGS-2 R5-5): every inventoried T*/F* key
    at 1 Hz around a planning-turn step. One serialized sweep per tick; failed
    reads are data. The file holds the full rows (raw readings included); the
    in-memory rows keep only what the WP14(a) classifier reads."""

    def __init__(self, reader, now_ns, path):
        self.reader, self.now_ns, self.path = reader, now_ns, Path(path)
        self.inventory = None
        self.keys = []
        self._rows = []
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            inventory = self.reader.enumerate_sensors()
            if not inventory.get("complete") or not inventory.get("keys"):
                raise RuntimeFailure("SMC enumeration incomplete or no readable sensors")
            self.inventory = deepcopy(inventory)
            self.keys = sorted(item["key"] for item in inventory["keys"])

    def sample(self):
        from joulewise.align.apple import thermal
        with self._lock:
            if self.inventory is None:
                raise RuntimeFailure("SMC inventory journal has not started")
            started = self.now_ns()
            values = thermal.sample(self.reader, self.keys)
            finished = self.now_ns()
            row = {"started": {"monotonic_ns": started}, "finished": {"monotonic_ns": finished},
                   "values": values, "phase": None, "seq": len(self._rows) + 1}
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(canonical(row) + "\n")
            lean = {**row, "values": {"sensors": values["sensors"], "errors": values["errors"]}}
            self._rows.append(lean)
            return lean

    @property
    def rows(self):
        with self._lock:
            return deepcopy(self._rows)


def _inventory_process(path, stop, ready, reader_factory):
    """Own the reader and ticker in a spawned process (RL-74/RL-76).

    A blocked model thread cannot starve this interpreter. Reads are never
    backfilled; the desk checks each actual one-second cell.
    """
    import importlib
    from joulewise.clock import SystemClock
    from joulewise.align.apple.sampler import monotonic_ns
    reader = None
    try:
        module, name = reader_factory.split(":")
        reader = getattr(importlib.import_module(module), name)()
        clock = SystemClock()
        journal = InventoryJournal(reader, lambda: monotonic_ns(clock.stamp()), path)
        journal.start()
        journal.sample()
        ready.send((True, journal.inventory))
        parent = os.getppid()
        due = time.monotonic()
        while not stop.is_set() and os.getppid() == parent:
            due += 1.0
            if stop.wait(max(0.0, due - time.monotonic())):
                break
            journal.sample()
            # A slow sweep does not synthesize missed cells or catch up in a burst.
            # The grid stays at 1.000 s (a sweep shorter than a tick costs no
            # time); a sweep that overran whole ticks skips them, as the
            # thermal sidecar's loop does (RUN_STATE 280).
            now = time.monotonic()
            if now - due >= 1.0:
                due += (now - due) // 1.0
    except BaseException as error:
        try:
            ready.send((False, f"{type(error).__name__}: {error}"))
        finally:
            raise
    finally:
        if reader is not None:
            reader.close()
        ready.close()


class ProcessInventory:
    """Parent handle; inventory rows are read only after the worker stops."""

    def __init__(self, path, *, reader_factory="joulewise.align.apple.smc_reader:Reader"):
        import multiprocessing
        self.path = Path(path)
        context = multiprocessing.get_context("spawn")
        self.stop = context.Event()
        self.receive, send = context.Pipe(duplex=False)
        self.process = context.Process(target=_inventory_process,
            args=(str(path), self.stop, send, reader_factory), name="r1-inventory")
        self.process.start()
        send.close()
        if not self.receive.poll(20):
            self.close()
            raise RuntimeFailure("inventory process did not become ready")
        ok, value = self.receive.recv()
        if not ok:
            self.close()
            raise RuntimeFailure(f"inventory process: {value}")
        self.inventory = value
        self.keys = sorted(item["key"] for item in value["keys"])

    def close(self):
        self.stop.set()
        self.process.join(5)
        if self.process.is_alive():
            self.process.terminate()
            self.process.join(2)
            raise RuntimeFailure("inventory process failed to stop")
        code = self.process.exitcode
        self.receive.close()
        if code != 0:
            raise RuntimeFailure(f"inventory process exited {code}")

    @property
    def rows(self):
        return [json.loads(line) for line in self.path.read_text().splitlines() if line.strip()]


# LEAD-RULINGS-2 R9-1: PR #692 classifier fields the R1 classification record
# keeps verbatim from smc_enumeration.rank (inside classification_sha256).
CLASSIFIER_RECORD_FIELDS = ("heat_ordering_indeterminate", "heat_ordering_wide_exclusion",
                            "recovery_onset_gap_s", "alternative_slow_picks", "selected_key_aliases")


def classify_step(inventory, rows, *, prefill_ns, last_decode_ns, quiet_s=300, recovery_s=600,
                  r0_sensors):
    """Classify a planning step with WP14(a), retaining its observation bounds."""
    from joulewise.align.apple import smc_enumeration
    origin = prefill_ns - round(quiet_s * NS)
    recovery_end = last_decode_ns + round(recovery_s * NS)
    phases = [{"phase": phase, "start_s": (start - origin) / NS, "end_s": (end - origin) / NS}
              for phase, start, end in (("idle", origin, prefill_ns),
                                        ("load", prefill_ns, last_decode_ns),
                                        ("recovery", last_decode_ns, recovery_end))]
    samples = []
    for row in rows:
        stamp = row["started"]["monotonic_ns"]
        phase = ("idle" if origin <= stamp < prefill_ns else
                 "load" if prefill_ns <= stamp <= last_decode_ns else
                 "recovery" if last_decode_ns < stamp <= recovery_end else "outside")
        samples.append({**row, "phase": phase})
    capture = {"inventory": inventory, "samples": samples, "phases": phases,
               "started": {"monotonic_ns": origin}}
    ranked = smc_enumeration.rank(capture, stage="r1")
    previous = {role: r0_sensors.get(role) for role in ("s_fast", "s_slow")}
    changed = all(ranked[role] is not None for role in previous) and any(
        ranked[role] != previous[role] for role in previous)
    # LEAD-RULINGS-2 R9-1: the record also carries PR #692's classifier
    # diagnostics (record only; no verdict reads them).
    result = {key: ranked[key] for key in ("rule", "s_fast", "s_slow", "die_candidates",
                                          "heatsink_candidates", "record_only", "ranking")
              + CLASSIFIER_RECORD_FIELDS}
    result.update(status="pass" if ranked["s_fast"] is not None and ranked["s_slow"] is not None else "fail",
                  r0_sensors=previous, sensor_pick_changed=changed,
                  flags=["r1.sensor_pick_changed"] if changed else [], phases=phases, journal_rows=len(rows),
                  phase_bounds_ns={"quiet": [origin, prefill_ns], "load": [prefill_ns, last_decode_ns],
                                   "recovery": [last_decode_ns, recovery_end]},
                  # R7-13: aliased keys (identical series over this journal) are
                  # one thermometer; the kit refuses a policy that gates on two
                  # keys of one group.
                  alias_groups=alias_groups([item["key"] for item in inventory.get("keys", ())], rows),
                  alias_rule=("keys whose 1 Hz (value, error) series are identical in every row of the "
                              "classification journal are one sensor (LEAD-RULINGS-2 R7-13; the "
                              "signature of smc_enumeration.rank selected_key_aliases, PR #692)"))
    stamps = [row["started"]["monotonic_ns"] for row in rows]
    if not stamps or min(stamps) > origin:
        result.update(status="fail", reason="quiet_not_observed")
    elif max(stamps) < recovery_end - NS:
        result.update(status="fail", reason="recovery_not_observed")
    result["classification_sha256"] = hashlib.sha256(canonical(result).encode("utf-8")).hexdigest()
    return result


def resolve(path):
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def sensor_admissibility(classification, picks, r0_keys):
    """RL-78: confirm the fixed smoke pair, without consulting its new rank."""
    rows = {r["key"]: r for r in classification["ranking"]}
    reasons = []
    fast, slow = picks.get("s_fast"), picks.get("s_slow")
    aliases = classification.get("alias_groups", [])
    if fast == slow or any(fast in g and slow in g for g in aliases):
        reasons.append("picked keys are aliases")
    for role, key in picks.items():
        row = rows.get(key, {})
        noise_max = 1/3 if role == "s_fast" else .15
        if (key not in r0_keys or row.get("unit") != "degC" or row.get("above_junction")
                or row.get("clamped") or row.get("heat_ordering_excluded")
                or not row.get("resolving")
                or not _finite(row.get("noise")) or row["noise"] > noise_max
                or not _finite(row.get("t_band_s")) or not 0 <= row["t_band_s"] <= 300
                or not _finite(row.get("tau_s")) or not 0 <= row["tau_s"] <= 300):
            reasons.append(f"{role}: {key} is not admissible on D (rise/noise/return-time/R0/quality)")
    if classification.get("reason"):
        reasons.append(classification["reason"])
    return {"ok": not reasons, "reasons": reasons, **picks,
            "second_key_label": "near-die settling check", "authority": "RL-78"}


def night_confirmation(classification, picks, r0_keys, r0_classes=None):
    """RL-145 section 3: the session's confirmation of the fixed pair.

    The second key is the lexically first other member of the fast pick's alias
    group on the saved Part B classification (the kit derives it). The pair is
    confirmed (``ok``) when the fast key is admissible on this D step and the
    second key is in the fast key's alias group here, or is itself an admissible
    die key if the group did not form. Any other reason refuses, as
    ``sensor_admissibility`` always did. Selection, ranking and Part B are not
    touched: ``sensor_admissibility`` is unchanged.
    """
    fast, slow = picks.get("s_fast"), picks.get("s_slow")
    group = next((g for g in classification.get("alias_groups", []) if fast in g), None)
    if group is not None and slow in group and slow != fast:
        # One thermometer read twice: only the fast key's own quality is tested.
        result = sensor_admissibility(classification, {"s_fast": fast}, r0_keys)
        reasons, basis = result["reasons"], "alias_group_of_fast_key"
    else:
        result = sensor_admissibility(classification, picks, r0_keys)
        reasons, basis = list(result["reasons"]), "admissible_die_key"
        if group is not None and slow != fast:
            reasons.append(f"s_slow: {slow} is not in the fast key's alias group {group} (RL-145)")
        if r0_classes is not None and r0_classes.get(slow) != "die":
            reasons.append(f"s_slow: {slow} is not an R0 die key (RL-145)")
    return {"ok": not reasons, "reasons": reasons, **picks,
            "second_key_label": "near-die settling check", "authority": "RL-78",
            "second_key_rule": "RL-145", "second_key_basis": basis}


def select_smoke_sensors(classification, r0_keys):
    """Registered picks, with only RL-78's empty-slow-class fallback.

    rank() remains unchanged. Class-edge margins and alternative classifiers
    are disclosures and are never read here. Lexical ties match select_keys.
    """
    fast, slow = classification.get("s_fast"), classification.get("s_slow")
    fallback = slow is None and not classification.get("heatsink_candidates")
    if fallback:
        candidates = []
        for row in classification["ranking"]:
            pair = {"s_fast": fast, "s_slow": row["key"]}
            if sensor_admissibility(classification, pair, r0_keys)["ok"]:
                candidates.append(row)
        slow = min(candidates, key=lambda r: (-r["t_band_s"], r["key"]))["key"] if candidates else None
    result = sensor_admissibility(classification, {"s_fast": fast, "s_slow": slow}, r0_keys)
    return {**result, "fallback": fallback, "selected_at": "smoke_part_b"}


class HashDeadline(Exception):
    """A watchdog digest ran past its deadline (checked per 1 MiB block)."""


def sha256_file(path, deadline=None):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            if deadline is not None and time.monotonic() > deadline:
                raise HashDeadline(path)
            digest.update(block)
    return digest.hexdigest()


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def _pending(value):
    return value is None or (isinstance(value, str) and value.startswith("PENDING"))


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------
def load_config(path):
    raw = Path(path).read_bytes()
    config = json.loads(raw)
    if not isinstance(config, dict) or config.get("schema") != CONFIG_SCHEMA:
        raise Refused(f"r1 runtime config {path} is not {CONFIG_SCHEMA}")
    if config.get("backend") not in ("production", "synthetic"):
        raise Refused("r1 runtime config backend must be production or synthetic")
    for key in ("d_spam", "d_bank", "model_30b", "x_g"):
        if not isinstance(config.get("templates", {}).get(key), str):
            raise Refused(f"r1 runtime config templates.{key} must name a kit config")
    return config, hashlib.sha256(raw).hexdigest()


def sensors_policy(config):
    from joulewise.align.apple.thermal import validate_policy
    value = config.get("sensors")
    if _pending(value):
        raise Refused("r1 runtime config sensors are PENDING R0 (SMC key selection)")
    try:
        return validate_policy(value)
    except ValueError as error:
        raise Refused(f"r1 runtime config sensors: {error}") from error


def read_soak_reference(path):
    if path is None:
        return None
    try:
        value = json.loads(Path(path).read_text())
    except (OSError, ValueError) as error:
        raise Refused(f"--soak-reference {path} is unreadable: {error}") from error
    if not isinstance(value, dict) or value.get("schema") != SOAK_REFERENCE_SCHEMA:
        raise Refused(f"--soak-reference {path} is not {SOAK_REFERENCE_SCHEMA}")
    return value


def reference_c(soak, sensors):
    """The soak reference R for the two gate keys (driver: last 1,200 s mean)."""
    try:
        values = {role: float(soak["sensors_c"][sensors[role]]) for role in ("s_fast", "s_slow")}
    except (KeyError, TypeError, ValueError) as error:
        raise Refused(f"soak reference lacks gate key {error}") from error
    if not all(math.isfinite(v) for v in values.values()):
        raise Refused("soak reference values must be finite")
    return {"fast_c": values["s_fast"], "slow_c": values["s_slow"]}


def registered_s6():
    """The ruled S6 and its receipt; unmeasured slots remain pending."""
    return json.loads(R1_REGISTRATION.read_text())


def bands_c(soak, sensors, *, slow_floor=None):
    """Fast: max(1 C, 3 SD); slow: max(registered S6, 3 SD).

    Pass slow_floor=1 C to retain the registered S5 formula separately.
    """
    if slow_floor is None:
        slow_floor = registered_s6()["slots"]["S6"]
    out = {}
    for role, name in (("s_fast", "delta_fast_c"), ("s_slow", "delta_slow_c")):
        try:
            sd = float(soak["detrended"][sensors[role]]["detrended_sd_c"])
        except (KeyError, TypeError, ValueError) as error:
            raise Refused(f"soak reference lacks the detrended SD of {sensors[role]}") from error
        if not math.isfinite(sd) or sd < 0:
            raise Refused("soak detrended SD must be finite and non-negative")
        out[name] = max(slow_floor if role == "s_slow" else BAND_FLOOR_C, 3.0 * sd)
    return out


def gate_policy(sensors, bands, *, turn_cap_s, chunk_tokens, heavy, per_turn, g0_cap_s=None):
    from joulewise.align.apple.thermal_gates import validate_gate_policy
    policy = {
        "sensors": sensors, "delta_fast_c": bands["delta_fast_c"], "delta_slow_c": bands["delta_slow_c"],
        "turn_cap_s": turn_cap_s, "chunk_tokens": chunk_tokens, "heavy": heavy, "per_turn": per_turn,
        # Native captures for step-30B, each leg and step-D. Consumers install
        # authenticated step-D R_D (or a designed offset) before warmup.
        "window_reference": {"role": "capture"}}
    if g0_cap_s is not None:
        policy["g0_cap_s"] = g0_cap_s   # R7-2: the R1 G0 timeout
    return validate_gate_policy(policy)


def g0_timeout_s(config):
    """LEAD-RULINGS-2 R7-2: the one R1 G0 timeout constant (runtime config)."""
    from joulewise.align.apple.thermal_gates import G0_CAP_DEFAULT_S, G0_CAP_MAX_S
    value = config.get(G0_TIMEOUT_CONFIG_KEY)
    if (type(value) not in (int, float) or not math.isfinite(value)
            or not G0_CAP_DEFAULT_S <= value <= G0_CAP_MAX_S):
        raise Refused(f"r1 runtime config {G0_TIMEOUT_CONFIG_KEY} must be a number in "
                      f"[{G0_CAP_DEFAULT_S}, {G0_CAP_MAX_S}] s (LEAD-RULINGS-2 R7-2), not {value!r}")
    return value


def g0_wait_fields(g0, cap_s):
    """R7-2: record every G0 wait (the G0 interval's seconds) and the cap it ran under."""
    return {"g0_wait_s": g0["duration_s"] if g0 else None, "g0_timeout_s": cap_s}


def alias_groups(keys, rows):
    """LEAD-RULINGS-2 R7-13: SMC keys whose 1 Hz series are identical in every
    journal row are one sensor under several keys, never independent
    thermometers. One alias definition (integration of PR #692): two keys are
    aliases when their (value, error) pair is equal in every row, the same
    signature ``smc_enumeration.rank`` uses for ``selected_key_aliases``
    (every recorded value and error, holes included). Keys with no reading at
    all are left out (every value null: no thermometer). Returns sorted groups
    of two or more keys; for a pick, its group's other members are exactly the
    classifier's ``selected_key_aliases`` among the degC keys."""
    series = {}
    for key in keys:
        pairs = [(((row.get("values") or {}).get("sensors") or {}).get(key),
                  ((row.get("values") or {}).get("errors") or {}).get(key)) for row in rows]
        if all(value is None for value, _ in pairs):
            continue
        series.setdefault(tuple(json.dumps(pair, allow_nan=True) for pair in pairs), []).append(key)
    return sorted(sorted(group) for group in series.values() if len(group) > 1)


def rearm_deadman(deadman, seconds, origin):
    """LEAD-RULINGS-2 R5-2: an R1 step member's deadman covers the decode only.

    The workload arms it at G0 entry (W1's rule); the R1 hook re-arms it once
    the preheat, the G0 (each with its own cap) and any quiet are over, and
    names the origin in the bundle's token_budget."""
    from joulewise.align.apple.sampler import monotonic_ns
    deadman.deadline_ns = monotonic_ns(deadman.clock.stamp()) + round(seconds * NS)
    deadman.origin = origin
    return deadman.deadline_ns


def read_template(path):
    config = json.loads(resolve(path).read_text())
    spec = json.loads(config["workload_profile"]["prompt_text"])
    return config, spec


def member_config(template, spec, *, run_id, kind):
    """A non-claim R1 member from a kit config: no launch lineage, R1 tags."""
    config = deepcopy(template)
    config["run_id"] = run_id
    config["hardware_target"]["notes"] = "ALIGN v4 R1 rehearsal member (non-claim qualification)."
    model = "d" if config["model"].get("family") == "qwen3_5" else "30b"
    config["run_metadata"]["tags"] = ["align-v4-r1", "non-claim", "align", "align_episode",
                                      "align-r1-kind=" + kind, "align-r1-model=" + model]
    spec = dict(spec)
    spec.pop("max_episode_seconds", None)
    config["workload_profile"]["prompt_text"] = canonical(spec)
    return config


def require_effort(spec, label):
    effort = (spec.get("chat_template_kwargs") or {}).get("reasoning_effort", "absent")
    if spec.get("chat_template_kwargs") is not None and _pending(effort):
        raise Refused(f"{label} template carries a PENDING R0 reasoning_effort; regenerate the kit after R0")


# --------------------------------------------------------------------------
# The planning-turn step task (10k fed prefill + seeded decode, one turn)
# --------------------------------------------------------------------------
class StepTask:
    """Deterministic long-prefill single-turn task for the R1 step tests.

    No tools and no score: the episode is one model call whose fed prefill is
    the system prompt (about ``prefill_chars`` characters) and whose decode
    is capped by the spec's ``max_tokens``. The realized token counts are
    read back from the bundle.
    """
    scratchpad_tags = ("<think>", "</think>")

    def __init__(self, prefill_chars=40000, task_pair="r1/planning_turn_step"):
        if type(prefill_chars) is not int or prefill_chars <= 0:
            raise ValueError("prefill_chars must be a positive integer")
        self.prefill_chars = prefill_chars
        self.task_pair = task_pair
        self.flags = []
        self.calls = []
        self.give_hint = None
        self.evaluation_outputs = {}

    def reset(self, seed):
        self.seed = seed
        self.calls = []

    def system_prompt(self, condition):
        lines, i = ["You are auditing a plant telemetry log. Records follow.\n"], 0
        size = len(lines[0])
        statuses = ("ok", "warn", "check", "ok", "drift")
        while size < self.prefill_chars:
            line = (f"record {i:05d}: unit-{i % 97:02d} reading {((i * 7919) % 10007) / 100:.2f} "
                    f"delta {((i * 104729) % 2003) / 1000:.3f} status {statuses[i % 5]}\n")
            lines.append(line)
            size += len(line)
            i += 1
        return "".join(lines)[:self.prefill_chars]

    def user_prompt(self):
        return ("Reason carefully and at length about every record above: group the units, "
                "check each delta against its status, and list every inconsistency you find.")

    def task_description(self):
        return self.user_prompt()

    def tool_schemas(self):
        return []

    def call_tool(self, name, arguments_json):
        self.calls.append(name)
        return json.dumps({"error": "the R1 step test has no tools"})

    def environment_state_sha256(self):
        return hashlib.sha256(json.dumps(self.calls).encode()).hexdigest()

    def score_main(self, transcript):
        return None

    def score_side(self, transcript):
        return None


def step_task(prefill_chars=40000):
    return StepTask(prefill_chars)


def step_spec(template_spec, step, policy, *, deadman_s):
    keep = ("schema", "enable_thinking", "sampler", "temperature", "assistant_history",
            "chat_template_kwargs", "prompt_cache", "max_context_tokens", "hybrid_checkpoint_limit")
    spec = {key: template_spec[key] for key in keep if key in template_spec}
    spec.update(task_factory=STEP_TASK_FACTORY, task_kwargs={"prefill_chars": step["prefill_chars"]},
                condition="benign", seed=step["seed"], max_turns=1, max_tokens=step["decode_tokens"],
                mock_turns=[], deadman_s=deadman_s, thermal=policy, warmup_condition="benign")
    return spec


# --------------------------------------------------------------------------
# Journals: battery (ruling 4(b)) and per-second ticks
# --------------------------------------------------------------------------
_BATT = re.compile(r"(\d{1,3})%;(.*)$")


def parse_pmset_batt(stdout):
    """``pmset -g batt`` -> {soc_pct, state, ac}; state is charging, discharging,
    charged, not_charging or None. Only the first InternalBattery line is read."""
    lines = (stdout or "").splitlines()
    ac = bool(lines) and "'AC Power'" in lines[0]
    for line in lines[1:]:
        if "InternalBattery" not in line:
            continue
        match = _BATT.search(line)
        if not match:
            break
        rest = match.group(2).lower()
        state = ("not_charging" if "not charging" in rest else "discharging" if "discharging" in rest
                 else "charging" if ("charging" in rest or "finishing charge" in rest)
                 else "charged" if "charged" in rest else None)
        return {"soc_pct": int(match.group(1)), "state": state, "ac": ac}
    return {"soc_pct": None, "state": None, "ac": ac}


def battery_summary(rows):
    """Drain rate (%/h, positive = discharging) over non-charging samples, and
    every observed charge resume (a non-charging sample followed by charging)."""
    good = [r for r in rows if r.get("soc_pct") is not None]
    drain_rows = [r for r in good if r.get("state") != "charging"]
    drain, reason = None, None
    if len(drain_rows) < 2 or drain_rows[-1]["epoch_s"] <= drain_rows[0]["epoch_s"]:
        reason = "charging_throughout" if good and not drain_rows else "too_few_samples"
    else:
        t0 = drain_rows[0]["epoch_s"]
        xs = [(r["epoch_s"] - t0) / 3600.0 for r in drain_rows]
        ys = [float(r["soc_pct"]) for r in drain_rows]
        xbar, ybar = sum(xs) / len(xs), sum(ys) / len(ys)
        sxx = sum((x - xbar) ** 2 for x in xs)
        drain = -sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / sxx
    events = [{"epoch_s": b["epoch_s"], "soc_pct": b["soc_pct"], "prior_soc_pct": a["soc_pct"]}
              for a, b in zip(good, good[1:]) if a.get("state") != "charging" and b.get("state") == "charging"]
    return {"samples": len(rows), "valid_samples": len(good), "drain_pct_per_h": drain,
            "drain_unavailable_reason": reason, "charge_resume_events": events,
            "charge_resume_soc_pct": events[0]["soc_pct"] if events else None,
            "first": good[0] if good else None, "last": good[-1] if good else None,
            "resolution": "pmset -g batt integer percent; OLS over non-charging samples"}


class BatteryJournal:
    def __init__(self, runner, epoch, path):
        self.runner, self.epoch, self.path = runner, epoch, Path(path)
        self.rows = []
        self.lock = threading.Lock()

    def sample(self):
        row = {"epoch_s": self.epoch()}
        try:
            result = self.runner(PMSET_BATT)
            if result.returncode:
                raise ValueError(f"pmset -g batt exit {result.returncode}")
            row.update(parse_pmset_batt(result.stdout), raw=result.stdout)
        except Exception as error:  # noqa: BLE001 - a failed read is journaled, not fatal
            row.update(soc_pct=None, state=None, error=f"{type(error).__name__}: {error}")
        with self.lock:
            self.rows.append(row)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, sort_keys=True) + "\n")

    def summary(self):
        with self.lock:
            return battery_summary(list(self.rows))


# --------------------------------------------------------------------------
# Measurement read-back from finished bundles and journals
# --------------------------------------------------------------------------
def journal_rows(path):
    """Normalized SMC sample rows (thermal_gates.sample_rows) from a journal file."""
    from joulewise.align.apple.thermal_gates import sample_rows
    path = Path(path)
    if not path.is_file():
        return []
    return sample_rows([json.loads(line) for line in path.read_text().splitlines() if line.strip()])


def valid_series(rows, key):
    from joulewise.align.apple.thermal import valid_value
    return [(r["monotonic_ns"], r["sensors"][key]) for r in rows
            if key not in r.get("errors", {}) and valid_value(key, r.get("sensors", {}).get(key))]


def episode_phases(ep):
    """Ruling 1(a): deadman consumption by phase, from the episode record.

    G0/G1/H from ThermalSession.record() intervals; prefill and decode from
    each turn's start/first-token/end stamps (holds removed from decode);
    tool from the tool-call intervals; tail = episode end past the deadline.
    """
    thermal = ep.hardware.get("thermal") or {}
    intervals = thermal.get("intervals", [])
    gates = {kind: math.fsum(r["duration_s"] for r in intervals if r["kind"] == kind) for kind in ("G0", "G1", "H")}
    prefill = decode = tool = 0
    for turn in ep.turns:
        first = turn.first_token_ns if turn.first_token_ns is not None else turn.end_ns
        holds = sum(r["end_ns"] - r["start_ns"] for r in intervals
                    if r["kind"] == "H" and r["turn"] == turn.index)
        prefill += max(0, first - turn.start_ns)
        decode += max(0, turn.end_ns - first - holds)
        tool += sum(c.end_ns - c.start_ns for c in turn.tool_calls)
    budget = ep.hardware.get("token_budget") or {}
    deadline = budget.get("deadline_ns")
    tail = max(0, ep.end_ns - deadline) / NS if type(deadline) is int else 0.0
    return {**gates, "decode": decode / NS, "prefill": prefill / NS, "tool": tool / NS, "tail": tail}


def configured_n_chunk(config):
    """RL-145 addendum row 2: the config's ``d_n_chunk`` (None when the key is absent).

    A multiple of 256 in [256, 4096] (``thermal_gates`` accepts any multiple of 256;
    4,096 is the frozen ``max_tokens``, so no hold can fire at it). The companion
    ``d_n_chunk_status`` text is a label only and is never read here.
    """
    if "d_n_chunk" not in config:
        return None
    value = config["d_n_chunk"]
    if type(value) is not int or not 256 <= value <= 4096 or value % 256:
        raise Refused(f"r1 runtime config d_n_chunk {value!r} must be a multiple of 256 in [256, 4096]")
    return value


def t_decline(pm_samples, turn):
    """FD 2.6 slot S9: step start to the first of 2 consecutive PM samples whose
    active-weighted GPU clock is < 0.97 x the median clock of the first 10 s of
    decode. Returns (seconds | None, status) with status declined, no_decline
    or unobserved (no PM clock support; never read as 'no decline')."""
    first = turn.first_token_ns
    if first is None:
        return None, "unobserved"
    rows = sorted((r for r in pm_samples if r.get("clock_mhz") is not None
                   and r["end_ns"] > first and r["start_ns"] < turn.end_ns), key=lambda r: r["end_ns"])
    base = [r["clock_mhz"] for r in rows if r["end_ns"] <= first + 10 * NS]
    if not base:
        return None, "unobserved"
    threshold = 0.97 * median(base)
    for a, b in zip(rows, rows[1:]):
        if a["clock_mhz"] < threshold and b["clock_mhz"] < threshold:
            return (a["end_ns"] - turn.start_ns) / NS, "declined"
    return None, "no_decline"


def step_response(rows, key, start_ns, end_ns):
    """Rise and cooling of one key around a step: baseline (median of the 60 s
    before the step), peak, delta T, t63 rise from step start, and tau (peak to
    a 63 % fall). Censored values carry a flag and the observed bound; with no
    rise, t63 is null (``t63_censored``)."""
    series = valid_series(rows, key)
    before = [v for t, v in series if start_ns - 60 * NS <= t < start_ns]
    after = [(t, v) for t, v in series if t >= start_ns]
    if not before or not after:
        raise RuntimeFailure(f"step response of {key}: no samples around the step")
    base = median(before)
    peak_t, peak = max(after, key=lambda tv: (tv[1], -tv[0]))
    rise = peak - base
    flags = []
    if rise <= 0:
        # Executing review round 4 LOW-9: with no rise there is no 63 % point.
        # t63 is null and censored, never 0.0 (which would read as a fast key).
        flags += ["no_rise", "t63_censored"]
        t63 = None
    else:
        t63 = next((t - start_ns) / NS for t, v in after if v >= base + 0.63 * rise)
    cool = [(t, v) for t, v in after if t >= peak_t]
    target = peak - 0.63 * rise
    tau = next(((t - peak_t) / NS for t, v in cool if v <= target and rise > 0), None)
    if tau is None:
        flags.append("tau_censored")
        tau = (cool[-1][0] - peak_t) / NS
    return {"key": key, "baseline_c": base, "peak_c": peak, "peak_ns": peak_t, "delta_t_c": rise,
            "t63_s": t63, "tau_s": tau, "flags": flags,
            "observed_until_s": (after[-1][0] - start_ns) / NS, "step_end_s": (end_ns - start_ns) / NS}


def recovery_time(rows, sensors, reference, bands, peak_ns):
    """Peak to the first sample with both keys within delta of R (FD 2.6 S7)."""
    fast, slow = sensors["s_fast"], sensors["s_slow"]
    from joulewise.align.apple.thermal import valid_value
    for r in rows:
        if r["monotonic_ns"] < peak_ns:
            continue
        values = r.get("sensors", {})
        if (valid_value(fast, values.get(fast)) and valid_value(slow, values.get(slow))
                and values[fast] <= reference["fast_c"] + bands["delta_fast_c"]
                and values[slow] <= reference["slow_c"] + bands["delta_slow_c"]):
            return max(1.0, (r["monotonic_ns"] - peak_ns) / NS), False
    last = rows[-1]["monotonic_ns"] if rows else peak_ns
    return max(1.0, (last - peak_ns) / NS), True


def derive_step_d_slots(*, ep, turn, wall_s, responses, recovery_s, recovery_censored, bands,
                        t_decline_s, t_decline_status, d_class, s5_bands=None, n_chunk_config=None):
    """Slot vocabulary S1-S9, B_D, I_D, T_dead, N_chunk, t_decline, class.

    S1-S4 are the R0-picked keys' step response (S1 fast delta T, S2 fast t63,
    S3 slow delta T, S4 slow tau); the key names and the class checks are in
    the detail. S5 retains max(1 C, 3 soak SD); S6 is the slow band R1 gates use
    (including the 2026-11-10 tuning); S7 = G_turn; S8 =
    N_chunk; S9 = t_decline. A censored t_decline (no decline in the step)
    is the observed decode length and N_chunk is 2,048 (A1 A3.1).
    """
    thermal = ep.hardware.get("thermal") or {}
    g0 = next((r for r in thermal.get("intervals", []) if r["kind"] == "G0"), None)
    g0_start = g0["start_ns"] if g0 is not None else ep.start_ns
    member_episode_s = (ep.end_ns - g0_start) / NS
    i_d = wall_s - member_episode_s
    first = turn.first_token_ns if turn.first_token_ns is not None else turn.end_ns
    prefill_s = max(1e-9, (first - turn.start_ns) / NS)
    decode_s = (turn.end_ns - first) / NS
    if turn.decode_tokens <= 0 or decode_s <= 0:
        raise RuntimeFailure("step-d produced no decode tokens")
    r_decode = turn.decode_tokens / decode_s
    r_prefill = turn.prefill_tokens / prefill_s
    if i_d < 0 or i_d >= 1750:
        raise RuntimeFailure(f"step-d member intercept I_D {i_d:.3f} s is outside [0, 1750)")
    # FD 2.2: the largest multiple of 1,024 with the planning member <= 1,800 s,
    # member wall = I_D + 1.13544 x episode wall (episode = 10k prefill + B decode).
    budget = ((MEMBER_CAP_S - i_d) / DEADMAN_FACTOR - prefill_s) * r_decode
    b_d = min(40960, max(0, 1024 * math.floor(budget / 1024)))
    t_dead = (1750 - i_d) / DEADMAN_FACTOR   # L1 first term; the kit applies the tail
    censored = t_decline_s is None
    t_dec = decode_s if censored else t_decline_s
    n_chunk_formula = 2048 if censored else max(256, 256 * math.floor(0.6 * t_dec * r_decode / 256))
    # RL-145 addendum row 2: a configured value replaces the formula's as N_chunk; the
    # formula's own value is still computed and recorded beside it. Absent key = the formula.
    n_chunk = n_chunk_formula if n_chunk_config is None else n_chunk_config
    g_turn = min(300.0, 3.0 * recovery_s)
    planning_turn_s = prefill_s + 4096 / r_decode
    fast, slow = responses["s_fast"], responses["s_slow"]
    s5_bands = s5_bands or bands
    slots = {"S1": fast["delta_t_c"], "S2": fast["t63_s"], "S3": slow["delta_t_c"], "S4": slow["tau_s"],
             "S5": s5_bands["delta_slow_c"], "S5_fast": s5_bands["delta_fast_c"], "S6": bands["delta_slow_c"], "S7": g_turn, "S8": float(n_chunk),
             "S9": t_dec, "B_D": b_d, "I_D": i_d, "T_dead": t_dead, "N_chunk": n_chunk,
             "t_decline": t_dec, "class": d_class}
    detail = {
        "S1_S4_keys": {"s_fast": fast["key"], "s_slow": slow["key"]},
        "classification": {"s_fast_t63_le_5s": None if fast["t63_s"] is None else fast["t63_s"] <= 5.0,
                           "s_slow_delta_t_ge_3c": slow["delta_t_c"] >= 3.0,
                           "s_slow_tau_le_300s": slow["tau_s"] <= 300.0},
        "responses": responses, "bands_c": bands,
        "S6_tuning": {**registered_s6()["s6_tuning"], "status": "adopted", "S6_now": bands["delta_slow_c"],
                      "from_c": slots["S5"], "to_c": slots["S6"],
                      "rule": "max(S6, 3 x soak SD); further FD 2.6 tuning after R1",
                      "tied_to": "the median G1 wait of the R1 gated D runs (r1_slots.s6_tuning)",
                      },
        "N_chunk_formula": n_chunk_formula,
        "N_chunk_source": "formula" if n_chunk_config is None else "config.d_n_chunk",
        "recovery_s": recovery_s, "recovery_censored": recovery_censored,
        "t_decline_status": t_decline_status, "t_decline_censored": censored,
        "r_decode_tok_per_s": r_decode, "r_prefill_tok_per_s": r_prefill,
        "prefill_tokens": turn.prefill_tokens, "decode_tokens": turn.decode_tokens,
        "prefill_s": prefill_s, "decode_s": decode_s, "member_wall_s": wall_s,
        "member_episode_s_from_g0": member_episode_s,
        "class_rule": {"protocol": d_class, "fd_2_5_heavy": (planning_turn_s >= 0.6 * t_dec) if not censored else False,
                       "planning_turn_s": planning_turn_s},
        "B_D_rule": "1024 * floor(((1800 - I_D) / 1.13544 - prefill_s) * r_decode / 1024), capped at 40960",
        "T_dead_rule": "(1750 - I_D) / 1.13544 (lead ruling L1 first term; the kit applies max_r1_tail_s)",
    }
    return slots, detail


# LEAD-RULINGS-2 R9-2 (protocol WP14(b), PR #692 D2): the changed-pick
# reference and band come from the classifier's own baseline, the median of
# the last 60 s of the quiet window and that window's OLS residual SD. The
# runtime computes them here; the kit re-derives band_c and S7 with
# pick_band and pick_s7, so the two cannot disagree.
R1_PICK_S7_RULE = ("reference = median of the last 60 s of the quiet window before prefill; "
                   "band = max(1.0 C, 3 x that window's OLS residual SD) (PR #692 D2, "
                   "LEAD-RULINGS-2 R9-2); S7 = min(300 s, 3 x peak-to-band recovery)")
R1_PICK_MIN_SAMPLES = 5


def quiet_baseline(rows, key, *, prefill_ns, quiet_s):
    """The WP14(a) classifier's D2 baseline for ``key`` on an R1 step journal.

    Same reads, window and statistics as ``smc_enumeration.rank`` on the
    capture ``classify_step`` builds: valid, bracketed reads of the idle phase
    (the ``quiet_s`` before prefill) inside its last ``IDLE_WINDOW_S``; the
    median of those values and ``_idle_stats``'s OLS residual SD."""
    from joulewise.align.apple import smc_enumeration, thermal
    origin = prefill_ns - round(quiet_s * NS)
    end_idle = (prefill_ns - origin) / NS
    span_end = origin + round(end_idle * 1e9)
    points = []
    for row in rows:
        started, finished = row["started"]["monotonic_ns"], row["finished"]["monotonic_ns"]
        value = row["values"]["sensors"].get(key)
        if not (origin <= started < prefill_ns and origin <= started <= finished < span_end
                and finished - started <= thermal.NS and key not in row["values"]["errors"]
                and thermal.valid_value(key, value)):
            continue
        points.append(((started - origin) / 1e9, value))
    points.sort()
    window = [(t, v) for t, v in points if end_idle - smc_enumeration.IDLE_WINDOW_S <= t < end_idle]
    _, noise = smc_enumeration._idle_stats(window)
    return {"baseline_c": median(v for _, v in window) if window else None, "noise_c": noise,
            "samples": len(window)}


def pick_band(noise_c):
    """FD 2.6's band form on the D2 residual SD: max(1.0 C, 3 SD)."""
    return max(BAND_FLOOR_C, 3.0 * noise_c)


def pick_s7(recovery_s):
    """S7 = min(300 s, 3 x the peak-to-band recovery)."""
    return min(300.0, 3.0 * recovery_s)


def s7_for_picks(rows, picks, *, prefill_ns, quiet_s):
    """Protocol v4 :249-251: when R1 changes R0's picks, S7 recovery is computed
    for the R1 picks from the full-inventory journal (the lead verifies it
    before the W1 freeze). The soak journal holds only R0's keys, so each new
    key's reference and band come from the quiet window before prefill, with
    the classifier's D2 baseline (R9-2): the last-60 s median and
    max(1.0 C, 3 x the OLS residual SD). S7 = min(300 s, 3 x the time from the
    slow pick's peak to both picks within band)."""
    out = {"keys": dict(picks), "rule": R1_PICK_S7_RULE}
    reference, noise, band = {}, {}, {}
    for role, key in picks.items():
        base = quiet_baseline(rows, key, prefill_ns=prefill_ns, quiet_s=quiet_s)
        if base["samples"] < R1_PICK_MIN_SAMPLES or base["noise_c"] is None:
            return {**out, "S7": None,
                    "reason": f"{key}: fewer than five valid samples in the last 60 s of the quiet window"}
        reference[role], noise[role] = base["baseline_c"], base["noise_c"]
        band[role] = pick_band(noise[role])
    after = [(r["started"]["monotonic_ns"], r["values"]["sensors"]) for r in rows
             if r["started"]["monotonic_ns"] >= prefill_ns]
    slow = [(t, v[picks["s_slow"]]) for t, v in after if _finite(v.get(picks["s_slow"]))]
    if not slow:
        return {**out, "S7": None, "reason": "no slow-pick samples after prefill"}
    peak_ns = max(slow, key=lambda tv: (tv[1], -tv[0]))[0]
    recovered = next((t for t, v in after if t >= peak_ns and all(
        _finite(v.get(key)) and v[key] <= reference[role] + band[role] for role, key in picks.items())), None)
    censored = recovered is None
    end = recovered if not censored else after[-1][0]
    recovery_s = max(1.0, (end - peak_ns) / NS)
    return {**out, "reference_c": reference, "noise_c": noise, "band_c": band, "recovery_s": recovery_s,
            "recovery_censored": censored, "S7": pick_s7(recovery_s)}


def gated_budget(slots):
    """(T_dead, B_D) for a gated D run from the step-d slots (lead ruling R5-4).

    A gated D run is never unbudgeted: B_D must be a multiple of 1,024 in
    [1024, 40960] (step-d floors a small budget to 0, which used to run the
    episode with no decode cap) and T_dead finite and positive; otherwise the
    run refuses (exit 2) before any model work.
    """
    try:
        t_dead = float(slots["T_dead"])
    except (KeyError, TypeError, ValueError) as error:
        raise Refused("step-d T_dead is not a finite positive number") from error
    # A JSON number only: float("1200") would admit a string (round-5 executing review).
    if type(slots.get("T_dead")) not in (int, float) or not math.isfinite(t_dead) or t_dead <= 0:
        raise Refused("step-d T_dead is not a finite positive number")
    b_d = slots.get("B_D")
    if type(b_d) is not int or not 1024 <= b_d <= 40960 or b_d % 1024:
        raise Refused(f"step-d B_D {b_d!r} is not an admissible decode budget (a multiple of 1024 in "
                      "[1024, 40960]); a gated D run never runs unbudgeted")
    return t_dead, b_d


def decode_energy(ep):
    from joulewise.align.attribution import attribute_episode
    attributed = attribute_episode(ep, source="powermetrics", channel="gpu_power")
    joules = math.fsum(s.energy.joules for s in attributed.segments if s.kind == "decode")
    tokens = sum(t.decode_tokens for t in ep.turns)
    if tokens <= 0 or not math.isfinite(joules) or joules <= 0:
        raise RuntimeFailure("step decode energy is not positive")
    return joules, tokens, list(attributed.flags)


# --------------------------------------------------------------------------
# Signals and custody
# --------------------------------------------------------------------------
class Termination:
    """First TERM/INT/HUP -> SystemExit(128 + signum); later ones are ignored so
    teardown completes; a watchdog forces the exit after ``timeout_s``.

    Before the forced exit the watchdog runs ``on_timeout`` (executing review
    round 4 LOW-1: main sets it to stop powermetrics and write the terminal
    record); a failure there never prevents the exit."""

    SIGNALS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)

    def __init__(self, timeout_s=TERM_TEARDOWN_S, exit_now=os._exit, hard_s=WATCHDOG_HARD_S):
        self.timeout_s, self.exit_now, self.hard_s = timeout_s, exit_now, hard_s
        self.signum = None
        self.armed_signum = None
        self.previous = {}
        self.watchdog = None
        self.on_timeout = None

    def expire(self, code):
        # An independent hard exit: a teardown that stalls (an fsync, a hung
        # ps) still ends inside the driver's 20 s grace (Sol critique).
        hard = threading.Timer(self.hard_s, self.exit_now, args=(code,))
        hard.daemon = True
        hard.start()
        try:
            if self.on_timeout is not None:
                self.on_timeout()
        except BaseException:  # noqa: BLE001 - the forced exit must happen
            pass
        finally:
            hard.cancel()
            self.exit_now(code)

    def install(self):
        for sig in self.SIGNALS:
            self.previous[sig] = signal.signal(sig, self.handler)
        return self

    def arm(self, signum):
        """Start the teardown watchdog for ``signum`` once (idempotent).

        Lead ruling R8-3: ``close_managed_session`` calls this when it holds
        the first signal, so the forced exit counts from the signal's arrival,
        not from the end of the (up to 10 s) deferral, and lands inside the
        driver's 20 s grace."""
        if self.watchdog is not None:
            return
        self.armed_signum = signum
        self.watchdog = threading.Timer(self.timeout_s, self.expire, args=(128 + signum,))
        self.watchdog.daemon = True
        self.watchdog.start()

    def handler(self, signum, _frame):
        if self.signum is not None:
            return
        self.signum = signum
        for sig in self.SIGNALS:
            signal.signal(sig, signal.SIG_IGN)
        self.arm(signum)
        raise SystemExit(128 + signum)

    def restore(self):
        for sig, handler in self.previous.items():
            signal.signal(sig, handler)
        if self.watchdog is not None:
            self.watchdog.cancel()


WATCHDOG_TMP = CUSTODY_NAME + ".watchdog.tmp"


PS_TREE = ("/bin/ps", "-A", "-o", "pid=,ppid=,command=")
WATCHDOG_STOP_WAIT_S = 2.0
WATCHDOG_HASH_S = 1.5


def stop_powermetrics_descendants(root_pid, *, run=None, kill=os.kill, wait_s=WATCHDOG_STOP_WAIT_S,
                                  sleep=time.sleep):
    """Executing review round 4 LOW-1: before the watchdog's forced exit, send
    TERM to every descendant of ``root_pid`` whose command names powermetrics.

    The adapter starts ``sudo -n powermetrics``; a non-root process cannot
    signal the root powermetrics, but it can signal its own sudo child, which
    relays TERM to powermetrics (the adapter's own stop does the same). EPERM
    on the root process is expected and ignored. Returns the pids signalled.
    """
    run = run or (lambda argv: subprocess.run(list(argv), text=True, capture_output=True, check=False, timeout=2))

    def snapshot():
        try:
            rows = run(PS_TREE).stdout.splitlines()
        except Exception:  # noqa: BLE001 - best effort inside the watchdog
            return {}
        table = {}
        for row in rows:
            parts = row.split(None, 2)
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                table[int(parts[0])] = (int(parts[1]), parts[2] if len(parts) > 2 else "")
        return table

    def tree(table):
        children = {}
        for pid, (ppid, _) in table.items():
            children.setdefault(ppid, []).append(pid)
        stack, found = [root_pid], {}
        while stack:
            for child in children.get(stack.pop(), ()):
                if "powermetrics" in table[child][1]:
                    found[child] = table[child]
                stack.append(child)
        return found
    first = tree(snapshot())
    # Revalidate just before signalling (Sol critique: a pid reaped by the main
    # teardown after the first snapshot could be reused): signal only a pid
    # that is still in our tree with the same parent and command.
    second = tree(snapshot()) if first else {}
    signalled = []
    for pid in sorted(first):
        if second.get(pid) == first[pid]:
            try:
                kill(pid, signal.SIGTERM)
                signalled.append(pid)
            except OSError:
                pass
    deadline = time.monotonic() + wait_s
    while signalled and time.monotonic() < deadline:
        alive = []
        for pid in signalled:
            try:
                kill(pid, 0)
                alive.append(pid)
            except OSError:
                pass
        if not alive:
            break
        sleep(0.1)
    return signalled


def watchdog_teardown(out, record, *, run=None, kill=os.kill, root_pid=None):
    """The forced-exit path's terminal record (LOW-1): stop powermetrics, then
    write ``runtime_custody.json`` with status aborted and ``watchdog: true``
    (file digests bounded by a deadline so the exit stays inside the driver's
    20 s grace)."""
    stopped = stop_powermetrics_descendants(os.getpid() if root_pid is None else root_pid, run=run, kill=kill)
    write_custody(out, {**record, "status": "aborted", "watchdog": True, "ended_epoch_s": time.time(),
                        "watchdog_powermetrics_signalled": stopped,
                        "error": record.get("error") or "teardown exceeded the watchdog; forced exit"},
                  deadline=time.monotonic() + WATCHDOG_HASH_S, temporary_name=WATCHDOG_TMP)


def write_custody(out, record, *, deadline=None, temporary_name=CUSTODY_NAME + ".tmp"):
    """Terminal record: digests of every other file in DIR, written last, atomically.

    Only DIR's own terminal record (and its temporaries) is excluded; a file of
    the same name below DIR is an ordinary file and is digested (Sol wp15rev
    F2). With ``deadline`` (monotonic s, the 15 s watchdog path) files left
    when it passes are listed as unhashed instead of digested.
    """
    out = Path(out)
    files = {}
    excluded = {out / CUSTODY_NAME, out / (CUSTODY_NAME + ".tmp"), out / WATCHDOG_TMP}
    for path in sorted(out.rglob("*")):
        if path.is_file() and not path.is_symlink() and path not in excluded:
            name = path.relative_to(out).as_posix()
            if deadline is not None and time.monotonic() > deadline:
                files[name] = "unhashed: watchdog deadline"
                continue
            try:
                files[name] = sha256_file(path, deadline)
            except HashDeadline:
                files[name] = "unhashed: watchdog deadline"
            except OSError as error:
                files[name] = f"unreadable: {error}"
    record = {**record, "schema": CUSTODY_SCHEMA, "files": files}
    temporary = out / temporary_name
    with temporary.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(record, indent=2, sort_keys=True, default=str) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, out / CUSTODY_NAME)


# --------------------------------------------------------------------------
# Production backend
# --------------------------------------------------------------------------
HEATER_CODE = r"""
import os, sys, time
import mlx.core as mx
duty_path, parent = sys.argv[1], os.getppid()
a = mx.random.normal((2048, 2048))
mx.eval(a)
while os.getppid() == parent:
    try:
        duty = min(1.0, max(0.0, float(open(duty_path).read() or 0)))
    except (OSError, ValueError):
        duty = 0.0
    start = time.monotonic()
    while time.monotonic() - start < duty:
        mx.eval(a @ a)
    rest = 1.0 - (time.monotonic() - start)
    if rest > 0:
        time.sleep(rest)
"""


class ProcessHeater:
    """MLX matmul load in a child process at a duty cycle (designed start states).

    The child is in the runtime's process tree, so the load journal excludes
    it. It exits by itself if the runtime dies.
    """

    def __init__(self, workdir):
        self.duty_path = Path(workdir) / "heater_duty"
        self.duty_path.parent.mkdir(parents=True, exist_ok=True)
        self.duty_path.write_text("0")
        self.process = subprocess.Popen([sys.executable, "-c", HEATER_CODE, str(self.duty_path)],
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def set_duty(self, duty):
        self.duty_path.write_text(f"{min(1.0, max(0.0, duty)):.3f}")

    def stop(self):
        if self.process.poll() is None:
            self.process.kill()
        self.process.wait(timeout=10)


class ManagedSession:
    def __init__(self, session, closers=(), on_close=None):
        self.session, self.closers, self.on_close = session, list(closers), on_close

    def close(self):
        try:
            if self.on_close is not None:
                self.on_close()
            self.session.close()
        finally:
            for closer in self.closers:
                closer()


class ProductionBackend:
    name = "production"

    def __init__(self, config):
        from joulewise.clock import SystemClock
        self.config = config
        self.clock = SystemClock()

    def run_cmd(self, argv):
        return subprocess.run(list(argv), text=True, capture_output=True, check=False, timeout=10)

    def epoch(self):
        return self.clock.now()

    def monotonic(self):
        return time.monotonic()

    def inventory_reader(self):
        from joulewise.align.apple.smc_reader import Reader
        return Reader()

    def ticker(self, callback):
        stop = threading.Event()

        def loop():
            due = time.monotonic()
            while not stop.is_set():
                due += 1.0
                if stop.wait(max(0.0, due - time.monotonic())):
                    return
                try:
                    callback()
                except Exception:  # noqa: BLE001 - a journal error never stops the segment
                    pass
        thread = threading.Thread(target=loop, name="r1-runtime-ticker", daemon=True)
        thread.start()

        def halt():
            stop.set()
            thread.join(timeout=5)
        return halt

    def _telemetry_config(self):
        from joulewise.schemas import BenchmarkConfig
        template, _ = read_template(self.config["templates"]["d_spam"])
        return BenchmarkConfig.from_mapping(template)

    def session(self, policy, outputs_dir, run_id, *, pm_status=False):
        from joulewise.align.apple.thermal_gates import PowermetricsStatus, ThermalSession
        closers, status = [], None
        outputs_dir = Path(outputs_dir)
        outputs_dir.mkdir(parents=True, exist_ok=True)
        context = SimpleNamespace(outputs_dir=outputs_dir, bundle_path=outputs_dir, run_id=run_id)
        try:
            if pm_status:
                from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
                telemetry = PowermetricsTelemetryAdapter(self.clock)
                config = self._telemetry_config()
                # Registered before the start: a TERM during start_sampling must
                # still stop the (sudo) powermetrics process the adapter spawned.
                closers.append(lambda: telemetry.stop_sampling(config, None))
                started = telemetry.start_sampling(config, None)
                if not started.ok:
                    raise RuntimeFailure(f"powermetrics status sampling failed: {started.message}")
                status = PowermetricsStatus(telemetry, self.clock)
            session = ThermalSession(policy, self.clock, context, status_reader=status)
            session.start()
        except BaseException:
            for closer in closers:
                try:
                    closer()
                except Exception:  # noqa: BLE001 - the original error is the one to report
                    pass
            raise
        return ManagedSession(session, closers)

    def run_member(self, config_map, runs_root, hook):
        from joulewise.align.apple.powermode import observe_ac_powermode
        from joulewise.align.apple.thermal_gates import ThermalRegistry, ThermalSession
        from joulewise.controller import run_benchmark
        from joulewise.schemas import BenchmarkConfig

        def factory(policy, clock, context, status_reader=None):
            session = ThermalSession(policy, clock, context, status_reader=status_reader)
            if hook is not None:
                hook(session)
            return session
        registry = ThermalRegistry(thermal_factory=factory, powermode_reader=observe_ac_powermode)
        bundle, summary = run_benchmark(BenchmarkConfig.from_mapping(config_map), Path(runs_root), self.clock,
                                        registry=registry)
        return Path(bundle), summary

    def heater(self, workdir):
        return ProcessHeater(workdir)

    def pm_samples(self, bundle, ep):
        from joulewise.align.apple.thermal_desk import native_pm_samples
        return native_pm_samples(bundle, ep)

    def close(self):
        pass


def make_backend(config):
    if config["backend"] == "production":
        return ProductionBackend(config)
    from tests.align.r1_synthetic import SyntheticBackend  # test-only seam (synthetic configs)
    return SyntheticBackend(config)


# --------------------------------------------------------------------------
# One segment
# --------------------------------------------------------------------------
class Segment:
    def __init__(self, *, kind, out, duration_s, soak, config, config_sha256, backend):
        self.kind, self.out, self.duration_s = kind, Path(out), duration_s
        self.soak, self.config, self.config_sha256, self.backend = soak, config, config_sha256, backend
        self.clock = backend.clock
        self.load = contract.LoadJournal((os.getpid(),), runner=backend.run_cmd, clock=backend.monotonic)
        self.load_errors = []
        self.battery = BatteryJournal(backend.run_cmd, backend.epoch, self.out / "battery.jsonl")
        self._tick_count = 0
        self._stop_ticker = None
        self.open_sessions = []
        self.heaters = []
        self.quiet_spans = []
        self.inventory = None
        self.inventory_readers = []
        self._stop_inventory = None

    # Journals -------------------------------------------------------------
    def _tick(self):
        self._tick_count += 1
        try:
            self.load.sample()
        except Exception as error:  # noqa: BLE001
            self.load_errors.append(f"{type(error).__name__}: {error}")
        if self._tick_count % int(self.config.get("battery_poll_s", 30)) == 0:
            self.battery.sample()

    def start_journals(self):
        self.load.snapshot("start")
        self.battery.sample()
        self._stop_ticker = self.backend.ticker(self._tick)

    def stop_journals(self, *, final=True):
        if self._stop_ticker is not None:
            self._stop_ticker()
            self._stop_ticker = None
        if final:
            self.load.snapshot("end")
            self.battery.sample()
        (self.out / "load_journal.json").write_text(json.dumps(
            {"exclude_roots": list(self.load.exclude_roots), "errors": self.load_errors, **self.load.fields()},
            sort_keys=True) + "\n")

    def close(self):
        """Idempotent teardown of every collector this segment opened.

        Catches BaseException (Sol wp15rev triage): a first TERM (SystemExit)
        while one session closes must not strand the others (their powermetrics
        stop included) or skip the load journal; it is returned with the rest.
        """
        errors = []
        for heater in self.heaters:
            try:
                heater.stop()
            except BaseException as error:  # noqa: BLE001
                errors.append(error)
        self.heaters = []
        try:
            self.stop_inventory()
        except BaseException as error:  # noqa: BLE001 - R5-9: a TERM here must not strand the sessions
            errors.append(error)
        while self.open_sessions:
            try:
                close_managed_session(self.open_sessions.pop())
            except BaseException as error:  # noqa: BLE001
                errors.append(error)
        if self._stop_ticker is not None:
            try:
                self.stop_journals(final=False)
            except BaseException as error:  # noqa: BLE001
                errors.append(error)
        return errors

    # Inputs ---------------------------------------------------------------
    @property
    def sensors(self):
        return sensors_policy(self.config)

    def consume_d_reference(self, session=None):
        """Authenticate R_D with W1's verifier, including journal and config bytes."""
        from joulewise.align.apple.thermal_gates import load_window_reference
        step = self.accepted_result(STEP_D_SEGMENT, "step-d")
        source = self.out.parent / STEP_D_SEGMENT / step["bundle"]
        policy = self.observe_policy()
        custody_record = json.loads((self.out.parent / STEP_D_SEGMENT / CUSTODY_NAME).read_text())
        source_config = Path(step["bundle"]) / "config.json"
        expected_config = custody_record["files"].get(source_config.as_posix())
        if not expected_config:
            raise Refused("step-D custody does not bind its source config")
        policy["window_reference"] = {"role": "consume", "source_run_id": source.name,
            "source_config_sha256": expected_config}
        context = SimpleNamespace(bundle_path=source.parent / "r1-reference-consumer",
                                  run_id="r1-reference-consumer")
        reference, custody = load_window_reference(policy, context)
        if session is not None:
            session.reference, session.custody = reference, custody
        return reference

    def reference(self):
        if self.soak is None:
            raise Refused(f"{self.kind} needs --soak-reference")
        return self.consume_d_reference()

    def bands(self):
        if self.soak is None:
            return {"delta_fast_c": BAND_FLOOR_C, "delta_slow_c": registered_s6()["slots"]["S6"]}
        floor = self.config.get("slow_band_floor_c", BAND_FLOOR_C)
        if floor != BAND_FLOOR_C:
            raise Refused("RL-78: arm at max(1 C, 3 soak idle SD); S6 receipt does not transfer")
        return bands_c(self.soak, self.sensors, slow_floor=floor)

    def step_d_result(self):
        """The accepted step-d result, bound to its complete runtime custody
        (Sol wp15rev F3): its bytes must be the ones the step-d runtime's
        terminal record digested, so a post-close edit of B_D, N_chunk or
        T_dead, or a step-d whose custody did not complete, is refused."""
        value = self.accepted_result(STEP_D_SEGMENT, "step-d")
        if not isinstance(value.get("slots"), dict):
            raise Refused("accepted step-d result lacks slots")
        return value

    def accepted_result(self, segment, kind):
        """Read the canonical accepted sibling, bound by complete custody."""
        path = self.out.parent / segment / RESULT_NAME
        custody_path = path.parent / CUSTODY_NAME
        try:
            raw = path.read_bytes()
            value = json.loads(raw)
            custody = json.loads(custody_path.read_bytes())
        except (OSError, ValueError) as error:
            raise Refused(f"{self.kind} needs the accepted {kind} result and custody {path}") from error
        if not isinstance(value, dict) or value.get("kind") != kind:
            raise Refused(f"{path} is not an accepted {kind} result")
        expected = (custody.get("files") or {}).get(RESULT_NAME) if isinstance(custody, dict) else None
        if (custody.get("schema") != CUSTODY_SCHEMA or custody.get("status") != "complete"
                or expected != hashlib.sha256(raw).hexdigest()):
            raise Refused(f"{path} is not bound by complete runtime custody")
        return value

    def now_ns(self):
        from joulewise.align.apple.sampler import monotonic_ns
        return monotonic_ns(self.clock.stamp())

    # Sensor sessions --------------------------------------------------------
    def observe_policy(self):
        return gate_policy(self.sensors, self.bands(), turn_cap_s=300, chunk_tokens=256,
                           heavy=False, per_turn=False)

    def open_session(self, label, *, pm_status=False, reference=None, policy=None):
        managed = self.backend.session(policy or self.observe_policy(), self.out / label,
                                       f"r1-{self.kind}-{label}", pm_status=pm_status)
        self.open_sessions.append(managed)
        if reference is not None:
            managed.session.reference = dict(reference)
        return managed

    def close_session(self, managed):
        # Exec LOW-3 (R6-8): the session leaves open_sessions only once its
        # close returned, so a failed close is retried by Segment.close.
        close_managed_session(managed, after=lambda: self.open_sessions.remove(managed))

    def latest(self, session, key):
        rows = valid_series(session.rows[-5:], key)
        return rows[-1][1] if rows else None

    def idle(self, session, seconds, until=None):
        start = self.now_ns()
        while (self.now_ns() - start) / NS < seconds:
            self.clock.sleep(min(1.0, seconds - (self.now_ns() - start) / NS))
            if until is not None and until():
                return True
        return False

    # Model members ------------------------------------------------------------
    def run_member(self, config_map, hook=None):
        runs = self.out / "runs"
        runs.mkdir(exist_ok=True)
        from joulewise.align.apple.workload import read_episode_bundle
        start = self.clock.stamp()
        bundle, summary = self.backend.run_member(config_map, runs, hook)
        end = self.clock.stamp()
        from joulewise.align.apple.sampler import monotonic_ns
        wall_s = (monotonic_ns(end) - monotonic_ns(start)) / NS
        if not (bundle / "outputs" / "align_episode.json").is_file():
            raise RuntimeFailure(f"{self.kind}: member {config_map['run_id']} wrote no episode "
                                 f"(status {summary.status.value}: {getattr(summary, 'failure_message', '')})")
        ep = read_episode_bundle(bundle)
        return SimpleNamespace(bundle=bundle, summary=summary, ep=ep, wall_s=wall_s,
                               status=summary.status.value,
                               failure_reason=getattr(summary.failure_reason, "value", None))

    def reference_hook(self, reference, *, quiet_s=0, rearm_s=None, capture=False):
        """Use W1 native capture, or consume authenticated step-D R_D.

        With ``rearm_s`` the G0 runs on its own 1,200 s cap with no deadman,
        and the member's deadman is re-armed for
        ``rearm_s`` after it (R5-2); with
        ``quiet_s`` a released G0 is followed by that much idle before the
        prefill, the step's quiet window (protocol v4 :243-251, R5-5)."""
        segment = self

        def hook(session):
            if not capture:
                reference.update(segment.consume_d_reference(session))
            if segment.kind in TIMEOUT_RUN_KINDS:
                session.g0_timeout_hook = allow_g0_timeout_run
            original = session.wait

            def wait(kind, **kwargs):
                if kind != "G0":
                    return original(kind, **kwargs)
                if capture and session.reference is not None:
                    reference.update(session.reference)
                deadman = kwargs.pop("deadman", None) if rearm_s is not None else kwargs.get("deadman")
                row = original(kind, **kwargs)
                if getattr(segment, "smoke_part", None):
                    elapsed = time.monotonic() - segment.smoke_started
                    segment.smoke_gate = {"admission_s": elapsed, "g0": row,
                                          "reference": dict(reference), "rearmed": rearm_s is not None}
                    (segment.out / "smoke_part_a.json").write_text(canonical(segment.smoke_gate) + "\n")
                    if row["outcome"] != "released" or elapsed > SMOKE_ADMISSION_S:
                        raise RuntimeFailure(f"smoke Part A did not release within {SMOKE_ADMISSION_S} s")
                    # The 1,200 s cap belongs to G0. After G0 the smoke must
                    # fit quiet, the re-armed turn, recovery, and close. This
                    # engineering watchdog does not decide RL-72 E5's total.
                    budget = smoke_post_g0_budget(quiet_s, rearm_s) if segment.smoke_part == "B" else None
                    if budget is not None:
                        segment.smoke_gate["post_g0_budget_s"] = budget
                        (segment.out / "smoke_part_a.json").write_text(canonical(segment.smoke_gate) + "\n")
                    segment.smoke_watchdog.set(budget["total"] if budget else 0)
                    if segment.smoke_part == "A":
                        rearm_deadman(deadman, 0, "R1_smoke_A_stop_after_G0")
                        return row
                # G1/H keep ThermalSession's episode reference (the G0 release
                # temperatures). R_D is only the G0 reference;
                # a fixed R_D under G1/H's 300 s turn cap would demand a cold
                # restart between turns (lead fix, 2026-11-10).
                if quiet_s and (row["outcome"] == "released" or
                                row["outcome"] == "timeout" and segment.kind in TIMEOUT_RUN_KINDS):
                    start = segment.now_ns()
                    while (segment.now_ns() - start) / NS < quiet_s:
                        segment.clock.sleep(min(1.0, quiet_s - (segment.now_ns() - start) / NS))
                    segment.quiet_spans.append([start, segment.now_ns()])
                if deadman is not None and rearm_s is not None:
                    rearm_deadman(deadman, rearm_s, "R1_after_G0_release" + ("_and_quiet" if quiet_s else ""))
                return row
            session.wait = wait
        return hook

    def planning_hook(self, reference, target_slow_c, *, rearm_s):
        """Designed start state: preheat, then hold S_slow at R + offset with a
        proportional MLX heater while the production G0 (reference R + offset
        on S_slow) decides the release. The heater stops before the episode.

        LEAD-RULINGS-2 R5-2: the preheat (PREHEAT_CAP_S) and the G0 (the R7-2
        timeout, 1,200 s) keep their own caps; the member's deadman is armed only after the G0,
        for the decode (``rearm_s``)."""
        segment, slow_key = self, self.sensors["s_slow"]

        def hook(session):
            reference.update(segment.consume_d_reference(session))
            session.g0_timeout_hook = allow_g0_timeout_run
            session.reference = {"fast_c": PLANNING_FAST_CEILING_C, "slow_c": target_slow_c,
                                 "source_member": "r1_designed_start_state", "span_ns": None,
                                 "soak_reference_c": reference}
            original = session.wait

            def wait(kind, **kwargs):
                if kind != "G0":
                    return original(kind, **kwargs)
                deadman = kwargs.pop("deadman", None)
                heater = segment.backend.heater(segment.out / "heater")
                segment.heaters.append(heater)
                stop = None
                try:
                    heater.set_duty(1.0)
                    start = segment.now_ns()
                    while (segment.now_ns() - start) / NS < PREHEAT_CAP_S:
                        value = segment.latest(session, slow_key)
                        if value is not None and value >= target_slow_c - PREHEAT_MARGIN_C:
                            break
                        segment.clock.sleep(1.0)

                    crossing = segment.now_ns()
                    reached = (segment.latest(session, slow_key) is not None and
                               segment.latest(session, slow_key) >= target_slow_c - PREHEAT_MARGIN_C)
                    segment.preheat = {"entry_ns": start, "end_ns": crossing,
                                       "target_slow_c": target_slow_c, "threshold_reached": reached,
                                       "flags": [] if reached else ["r1.preheat_cap_reached"]}
                    if not reached:
                        session.flags.append("r1.preheat_cap_reached")

                    def control():
                        value = segment.latest(session, slow_key)
                        heater.set_duty(0.0 if value is None else 0.5 + 0.5 * (target_slow_c - value))
                    control()
                    stop = segment.backend.ticker(control)
                    return original(kind, **kwargs)
                finally:
                    if stop is not None:
                        stop()
                    heater.stop()
                    segment.preheat = {**getattr(segment, "preheat", {}), "heater_stop_ns": segment.now_ns()}
                    segment.heaters.remove(heater)
                    if deadman is not None:
                        rearm_deadman(deadman, rearm_s, "R1_after_preheat_and_G0")
            session.wait = wait
        return hook

    def template(self, key):
        config, spec = read_template(self.config["templates"][key])
        return config, spec

    @property
    def g0_cap_s(self):
        """All R1 model members use the timeout; release keeps the 600 s default."""
        return g0_timeout_s(self.config) if self.kind in G0_TIMEOUT_KINDS else None

    @property
    def armed_g0_cap_s(self):
        from joulewise.align.apple.thermal_gates import G0_CAP_DEFAULT_S
        cap = self.g0_cap_s
        return G0_CAP_DEFAULT_S if cap is None else cap

    def step_member(self, model_key, *, label, source=None, quiet_s=0, rearm=False):
        template, tspec = self.template(model_key)
        require_effort(tspec, model_key)
        if source is not None:
            template = deepcopy(template)
            template["model"].update(source)
        reference = {}
        policy = gate_policy(self.sensors, self.bands(), turn_cap_s=300, chunk_tokens=256,
                             heavy=False, per_turn=False, g0_cap_s=self.g0_cap_s)
        step = self.config["step"]
        spec = step_spec(tspec, step, policy, deadman_s=step["deadman_s"])
        config = member_config(template, spec, run_id=f"align-v4-r1-{label}", kind=self.kind)
        hook = self.reference_hook(reference, quiet_s=quiet_s, rearm_s=step["deadman_s"] if rearm else None,
                                   capture=True)
        return self.run_member(config, hook), reference

    # Kinds -----------------------------------------------------------------
    def k_calibration(self):
        from joulewise.align.r0_host import host_snapshot

        def run(argv):
            result = self.backend.run_cmd(argv)
            if result.returncode:
                raise RuntimeError(f"{argv[0]} exit {result.returncode}")
            return result.stdout
        snapshot = host_snapshot(run=run)
        (self.out / "host_snapshot.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
        return {"host": snapshot, "bracket": self.kind.split("-")[1],
                "note": "host state at the bracket; the meter calibration itself is the R1 night plan's scaffold"}

    def k_idle(self):
        seconds = self.duration_s
        if not _finite(seconds) or seconds <= 0:
            raise Refused("idle needs a positive --duration-s")
        managed = self.open_session("sensors")
        self.idle(managed.session, seconds)
        self.close_session(managed)
        rows = journal_rows(self.out / "sensors" / "align_thermal.jsonl")
        series, times, failed = {}, {}, {}
        t0 = rows[0]["monotonic_ns"] if rows else 0
        for key in (self.sensors["s_fast"], self.sensors["s_slow"]):
            values = valid_series(rows, key)
            series[key] = [v for _, v in values]
            # Read times let the driver take the last 1,200 s, not samples
            # (Fable cold pass round 4 LOW-2).
            times[key] = [(t - t0) / NS for t, _ in values]
            failed[key] = len(rows) - len(values)
        # The soak's own end (the last journal row, valid or failed), so the
        # driver's 20-min window ends where the soak ended, not at the last
        # valid read (Sol critique of round 5).
        end = (rows[-1]["monotonic_ns"] - t0) / NS if rows else 0.0
        return {"sensor_series_c": series, "sensor_series_t_s": times, "sensor_series_end_t_s": end,
                "sensor_series_failed_reads": failed, "sensor_roles": self.sensors,
                "sensor_series_note": ("valid 1 Hz reads in order with their times (s from the first journal "
                                       "row); a failed read is dropped, never interpolated"),
                "duration_s": seconds}

    def k_idle_until_soak(self):
        reference, bands = self.reference(), self.bands()
        cap = self.duration_s if _finite(self.duration_s) and self.duration_s > 0 else COOLDOWN_CAP_S
        managed = self.open_session("sensors")
        slow = self.sensors["s_slow"]

        def within():
            # The G0 band is one-sided (S_slow <= R + delta_slow): a host that is
            # already cooler than the soak has cooled (LEAD-RULINGS-2 R5-1).
            value = self.latest(managed.session, slow)
            return value is not None and value <= reference["slow_c"] + bands["delta_slow_c"]
        released = self.idle(managed.session, cap, until=within)
        start = None
        curve = []
        rows = managed.session.rows
        self.close_session(managed)
        for t, value in valid_series(journal_rows(self.out / "sensors" / "align_thermal.jsonl") or rows, slow):
            start = t if start is None else start
            curve.append([(t - start) / NS, value])
        if not curve:
            raise RuntimeFailure("idle-until-soak observed no valid S_slow sample")
        return {"recovery_curve": curve, "released": released, "reference_c": reference["slow_c"],
                "reference_source": reference.get("source_member", "r1_soak_reference"),
                "delta_slow_c": bands["delta_slow_c"], "cap_s": cap}

    def k_g0_release_soak(self):
        reference = self.reference()
        managed = self.open_session("g0", pm_status=True, reference=reference)
        self.idle(managed.session, G0_PREROLL_S)
        row = managed.session.wait("G0")
        flags = list(managed.session.flags)
        self.close_session(managed)
        return {"released": row["outcome"] == "released", "g0": row, "reference_c": reference["slow_c"],
                "reference_source": reference.get("source_member", "r1_soak_reference"),
                "release_c": row["release"]["slow_c"], "flags": flags,
                **g0_wait_fields(row, self.armed_g0_cap_s)}

    def g0_inconclusive_fields(self, member, g0, incomplete, reference):
        """LEAD-RULINGS-2 R6-2: a calibration segment whose G0 timed out (and
        nothing else) is INCONCLUSIVE, exit 0; the driver precools and retries
        it once, then records it and the kit decides downstream."""
        return {"segment_status": "inconclusive", "g0_released": False,
                "g0_outcome": g0["outcome"] if g0 else None, **g0_wait_fields(g0, self.armed_g0_cap_s),
                "reason": "G0 did not release before its cap (LEAD-RULINGS-2 R6-2)",
                "bundle": str(member.bundle.relative_to(self.out)), "member_status": member.status,
                "incomplete_reasons": incomplete, "episode_flags": list(member.ep.flags),
                "ac_powermode": member.ep.hardware.get("ac_powermode"), "reference_c": reference.get("slow_c")}

    def k_step(self, model_key, *, label, source=None, quiet_s=0, rearm=False, leg=False, g0_inconclusive=False):
        member, reference = self.step_member(model_key, label=label, source=source, quiet_s=quiet_s,
                                             rearm=rearm)
        ep = member.ep
        thermal = ep.hardware.get("thermal") or {}
        g0 = next((r for r in thermal.get("intervals", []) if r["kind"] == "G0"), None)
        incomplete = incomplete_member_reasons(member)
        if getattr(self, "smoke_part", None) == "A":
            return member, {"bundle": str(member.bundle.relative_to(self.out)),
                "operating_reference": reference, "g0_outcome": g0["outcome"],
                "smoke_part_a": self.smoke_gate, **g0_wait_fields(g0, self.armed_g0_cap_s)}
        if "r1.g0_timeout_run" in ep.flags:
            incomplete = [r for r in incomplete if r != "thermal.start_gate_timeout"]
        if g0 is not None and not ep.turns and only_g0_unreleased(incomplete, g0["outcome"]):
            return member, {**self.g0_inconclusive_fields(member, g0, incomplete, reference),
                            "reference_unobserved": not bool(reference)}
        if leg and g0 is not None and g0["outcome"] != "released" and only_g0_unreleased(incomplete, g0["outcome"]):
            # LEAD-RULINGS-2 R5-3 (ruling 16): an A-B-A leg whose own G0 did not
            # release has no turn and no t_decline. It is INCONCLUSIVE, not a
            # refusal of the R1 night; t_decline_s is null here only beside
            # g0_released false, never as "no decline".
            return member, {
                "bundle": str(member.bundle.relative_to(self.out)), "member_status": member.status,
                "g0_outcome": g0["outcome"], "g0_released": False, "leg_status": "inconclusive",
                **g0_wait_fields(g0, self.armed_g0_cap_s),
                "t_decline_status": "not_measured_g0_unreleased", "t_decline_s": None,
                "incomplete_reasons": incomplete, "episode_flags": list(ep.flags),
                "ac_powermode": ep.hardware.get("ac_powermode"), "reference_c": reference.get("slow_c")}
        if incomplete:
            raise RuntimeFailure(f"{self.kind}: step member is not one complete turn: {incomplete}")
        turn = ep.turns[0]
        decline_s, decline_status = t_decline(self.backend.pm_samples(member.bundle, ep), turn)
        joules, tokens, flags = decode_energy(ep)
        return member, {
            "bundle": str(member.bundle.relative_to(self.out)), "member_status": member.status,
            "g0_outcome": g0["outcome"] if g0 else None, "g0_released": bool(g0) and g0["outcome"] == "released",
            **g0_wait_fields(g0, self.armed_g0_cap_s), "t_decline_status": decline_status,
            "t_decline_s": decline_s, "decode_energy_j": joules, "decode_tokens": tokens,
            "prefill_tokens": turn.prefill_tokens, "energy_flags": flags, "episode_flags": list(ep.flags),
            "ac_powermode": ep.hardware.get("ac_powermode"), "reference_c": reference["slow_c"],
            "reference_source": reference.get("source_member", "r1_soak_reference"),
            "operating_reference": reference,
            "g0_release": g0.get("release") if g0 else None,
            "bands_c": self.bands(),
            "candidate_only": "r1.g0_timeout_run" in ep.flags}

    def k_capture_predecessor_30b(self):
        template, spec = self.template("model_30b")
        if spec.get("thermal") is not None:
            raise Refused("capture predecessor must be the ordinary unmodified 30B template")
        # RL-84 P-1: W1's ordinary ungated 30B member has no sidecar.
        # Removing the R1-inapplicable lineage tag is the only derivation.
        template = deepcopy(template)
        template["run_metadata"]["tags"] = [t for t in template["run_metadata"]["tags"]
                                               if t != "launch_lineage_required"]
        member = self.run_member(template, hook=None)
        if member.status != "succeeded" or not member.ep.turns:
            raise RuntimeFailure("capture predecessor did not complete")
        return {"bundle": str(member.bundle.relative_to(self.out)),
                "template_sha256": sha256_file(resolve(self.config["templates"]["model_30b"])),
                "template_derivation": {"removed_run_metadata_tags": ["launch_lineage_required"]},
                "ac_powermode": member.ep.hardware.get("ac_powermode"), "admitted_turns": len(member.ep.turns)}

    def k_step_30b(self):
        self.start_inventory()
        member, fields = self.k_step("model_30b", label="step-30b", quiet_s=STEP_QUIET_S, rearm=True)
        if fields.get("segment_status") == "inconclusive":
            self.stop_inventory()
            return fields
        if fields["t_decline_status"] == "unobserved":
            raise RuntimeFailure("step-30b: no powermetrics GPU clock support for t_decline")
        self.observe_recovery(member)
        # Protocol v4: the 30B step is classified for the record only.
        fields["thermometry"] = self.thermometry(member, label="step-30b", record_only=True)
        if self.soak is not None:
            soak = reference_c(self.soak, self.sensors)
            fields["operating_minus_soak_c"] = {
                self.sensors[role]: fields["operating_reference"][name] - soak[name]
                for role, name in (("s_fast", "fast_c"), ("s_slow", "slow_c"))}
        return fields

    def observe_recovery(self, member):
        """A fixed RECOVERY_CAP_S (600 s) of SMC journal after the last decode
        (protocol v4 :243-251); returns the member and recovery rows, merged."""
        managed = self.open_session("recovery")
        turn = member.ep.turns[0]
        remaining = RECOVERY_CAP_S - (self.now_ns() - turn.end_ns) / NS
        if remaining > 0:
            self.idle(managed.session, remaining + 1.0)
        self.close_session(managed)
        member_rows = journal_rows(member.bundle / "outputs" / "align_thermal.jsonl")
        return sorted(member_rows + journal_rows(self.out / "recovery" / "align_thermal.jsonl"),
                      key=lambda r: r["monotonic_ns"])

    def start_inventory(self):
        """Full-inventory 1 Hz journal from before the member (so the 300 s
        quiet before prefill is inside it) through the 600 s recovery."""
        if self.backend.name == "production":
            self.inventory = ProcessInventory(self.out / "inventory" / "inventory_journal.jsonl")
            self._stop_inventory = self.inventory.close
            return
        reader = self.backend.inventory_reader()
        self.inventory_readers.append(reader)
        self.inventory = InventoryJournal(reader, self.now_ns, self.out / "inventory" / "inventory_journal.jsonl")
        self.inventory.start()
        self._stop_inventory = self.backend.ticker(self.inventory.sample)

    def stop_inventory(self):
        if self._stop_inventory is not None:
            self._stop_inventory()
            self._stop_inventory = None
        while self.inventory_readers:
            close = getattr(self.inventory_readers.pop(), "close", None)
            if close is not None:
                close()

    def thermometry(self, member, *, label, record_only):
        """The WP14(a) classifier on the step's full-inventory journal (stage r1)."""
        self.stop_inventory()
        turn = member.ep.turns[0]
        result = classify_step(self.inventory.inventory, self.inventory.rows, prefill_ns=turn.start_ns,
                               last_decode_ns=turn.end_ns, quiet_s=STEP_QUIET_S, recovery_s=RECOVERY_CAP_S,
                               r0_sensors=self.sensors)
        confirmation = None
        if not record_only and not getattr(self, "smoke_part", None):
            picks = {r: self.sensors[r] for r in ("s_fast", "s_slow")}
            confirmation = night_confirmation(result, picks,
                self.config.get("r0_classified_keys", list(picks.values())),
                r0_classes=self.config.get("r0_classes"))
        path = self.out / "inventory" / "r1_classification.json"
        # classification_sha256 = sha256 of canonical(classification without that field).
        path.write_text(json.dumps({"classification": result, "label": label, "for_record_only": record_only,
                                    "inventory": self.inventory.inventory,
                                    "night_confirmation": confirmation}, indent=2, sort_keys=True) + "\n")
        reasons = [result["reason"]] if result.get("reason") else (
            [] if result["status"] == "pass" else ["null pick: " + ", ".join(
                role for role in ("s_fast", "s_slow") if result[role] is None)])
        keep = ("status", "s_fast", "s_slow", "r0_sensors", "sensor_pick_changed", "flags", "die_candidates",
                "heatsink_candidates", "record_only", "phases", "journal_rows", "alias_groups", "alias_rule",
                "classification_sha256")
        extra = {}
        if confirmation is None and not record_only and result["sensor_pick_changed"] and result["s_fast"] and result["s_slow"]:
            extra["s7_for_r1_picks"] = s7_for_picks(
                self.inventory.rows, {"s_fast": result["s_fast"], "s_slow": result["s_slow"]},
                prefill_ns=turn.start_ns, quiet_s=STEP_QUIET_S)
        summary = {key: result.get(key) for key in keep}
        if confirmation is not None:
            summary.update(status="pass" if confirmation["ok"] else "fail",
                           **{r: confirmation[r] for r in ("s_fast", "s_slow")},
                           registered_picks={r: result[r] for r in ("s_fast", "s_slow")},
                           night_confirmation=confirmation, sensor_pick_changed=False,
                           flags=[] if confirmation["ok"] else ["r1.sensor_inadmissible"])
            reasons = confirmation["reasons"]
        return {**summary, **extra, "reasons": reasons,
                "classification_file": path.relative_to(self.out).as_posix(),
                "keys_inventoried": len(self.inventory.keys), "for_record_only": record_only}

    def k_step_d(self):
        self.start_inventory()
        member, fields = self.k_step("d_spam", label="step-d", quiet_s=STEP_QUIET_S, rearm=True,
                                     g0_inconclusive=True)
        if getattr(self, "smoke_part", None) == "A":
            self.stop_inventory()
            return fields
        if fields.get("segment_status") == "inconclusive":
            # R6-2: no turn, so no step response, slots or classification.
            self.stop_inventory()
            return fields
        if fields["t_decline_status"] == "unobserved":
            raise RuntimeFailure("step-d: no powermetrics GPU clock support for t_decline (slot S9)")
        reference, bands, sensors = fields["operating_reference"], self.bands(), self.sensors
        # Post-decode recovery (S4 tau, S7 G_turn), on the same monotonic clock.
        rows = self.observe_recovery(member)
        turn = member.ep.turns[0]
        responses = {role: step_response(rows, sensors[role], member.ep.start_ns, member.ep.end_ns)
                     for role in ("s_fast", "s_slow")}
        recovery_s, censored = recovery_time(rows, sensors, reference, bands, responses["s_slow"]["peak_ns"])
        slots, detail = derive_step_d_slots(
            ep=member.ep, turn=turn, wall_s=member.wall_s, responses=responses, recovery_s=recovery_s,
            recovery_censored=censored, bands=bands,
            s5_bands=bands_c(self.soak, sensors, slow_floor=BAND_FLOOR_C), t_decline_s=fields["t_decline_s"],
            t_decline_status=fields["t_decline_status"], d_class=self.config.get("d_class", "heavy"),
            n_chunk_config=configured_n_chunk(self.config))
        if self.backend.name == "production":
            detail["S6_tuning"] = {"status": "new_sensor_default", "authority": "RL-78 default band",
                                   "S6_now": bands["delta_slow_c"], "receipt_transferred": False}
        detail["quiet_before_prefill_s"] = STEP_QUIET_S
        detail["recovery_observed_s"] = RECOVERY_CAP_S
        fields["thermometry"] = self.thermometry(member, label="step-d", record_only=False)
        detail["thermometry_classification_sha256"] = fields["thermometry"]["classification_sha256"]
        return {**fields, "slots": slots, "slot_detail": detail,
                "e_D_j_per_token": fields["decode_energy_j"] / fields["decode_tokens"]}

    def k_aba_leg(self):
        _, fields = self.k_step("d_spam", label=self.kind, leg=True, rearm=True)
        if fields.get("g0_released") and fields.get("t_decline_status") == "unobserved":
            raise RuntimeFailure(f"{self.kind}: no powermetrics GPU clock support for t_decline")
        if "t_decline_s" not in fields:
            fields["t_decline_s"] = None
        return fields   # t_decline_s: seconds, or None for no decline (infinite) when g0_released

    def k_d_4bit(self):
        source = self.config.get("d_4bit_source")
        if _pending(source):
            raise Refused("d-4bit: r1 runtime config d_4bit_source is not set (R0.10 did not trigger)")
        _, fields = self.k_step("d_spam", label="d-4bit", source=source, rearm=True)
        return fields

    def gated_policy(self, slots, *, heavy, per_turn, chunk_tokens=256):
        turn_cap = min(300.0, max(1.0, float(slots["S7"])))
        return gate_policy(self.sensors, self.bands(), turn_cap_s=turn_cap, chunk_tokens=chunk_tokens,
                           heavy=heavy, per_turn=per_turn, g0_cap_s=self.g0_cap_s)

    def k_gated_d(self):
        step = self.step_d_result()
        slots = step["slots"]
        key = "d_bank" if self.kind == "d-bank-benign-s1" else "d_spam"
        template, tspec = self.template(key)
        require_effort(tspec, key)
        t_dead, b_d = gated_budget(slots)
        spec = dict(tspec)
        spec.update(deadman_s=t_dead, thermal=self.gated_policy(slots, heavy=True, per_turn=True,
                                                                chunk_tokens=int(slots["N_chunk"])),
                    warmup_condition="benign", max_episode_decode_tokens=b_d)
        config = member_config(template, spec, run_id=f"align-v4-r1-{self.kind}", kind=self.kind)
        # Authenticated step-D R_D (RL-59/72).
        # R6-1: no precool; the run follows a D turn with only
        # W1's inter-member schedule (this member's configured idle).
        reference = self.reference()
        member = self.run_member(config, self.reference_hook(reference))
        from joulewise.align.apple.thermal_desk import read_bundle_record
        record = read_bundle_record(member.bundle)
        ep = member.ep
        budget = ep.hardware.get("token_budget") or {}
        x7 = any(flag.startswith("episode.deadman:") for flag in ep.flags)
        return {**self.reference_fields(reference, ep), **self.schedule_fields(template),
                "energy_j": record["turn_owned_j"], "gross_episode_j": record["gross_episode_j"],
                "admitted_turns": len(ep.turns), "x7": x7,
                # R6-3: with deadman.phases_s.decode, the run's observed decode rate.
                "decode_tokens": sum(int(turn.decode_tokens) for turn in ep.turns),
                "deadman": {"T_dead_s": budget.get("deadman_s"), "deadline_ns": budget.get("deadline_ns"),
                            "phases_s": episode_phases(ep)},
                "B_D": spec["max_episode_decode_tokens"], "turn_cap_tokens": spec.get("max_tokens"),
                "bundle": str(member.bundle.relative_to(self.out)),
                "member_status": member.status, "failure_reason": member.failure_reason,
                "episode_flags": list(ep.flags), "ac_powermode": ep.hardware.get("ac_powermode")}

    @staticmethod
    def schedule_fields(template):
        """LEAD-RULINGS-2 R6-1: the only thing between the preceding D turn and
        this member's G0 is W1's inter-member schedule, the member's own
        configured idle (the W1 kit config's sampling.idle_seconds); the
        driver checks it against the W1 plan."""
        idle = (template.get("sampling") or {}).get("idle_seconds")
        if not _finite(idle) or idle < 0:
            raise RuntimeFailure("member template has no finite sampling.idle_seconds")
        return {"inter_member_idle_s": float(idle)}

    def reference_fields(self, reference, ep):
        """R5-1 evidence: the R the member gated against and its per-gate waits."""
        intervals = (ep.hardware.get("thermal") or {}).get("intervals", [])
        g0 = next((r for r in intervals if r["kind"] == "G0"), None)
        return {"reference_c": reference["slow_c"], "reference_fast_c": reference["fast_c"],
                "bands_c": self.bands(),
                "reference_source": reference.get("source_member"),
                "reference_custody": (ep.hardware.get("thermal") or {}).get("window_reference"),
                "g0_reference": g0.get("reference") if g0 else None,
                "g0_outcome": g0["outcome"] if g0 else None, **g0_wait_fields(g0, self.armed_g0_cap_s),
                "gate_waits_s": {kind: [r["duration_s"] for r in intervals if r["kind"] == kind]
                                 for kind in ("G0", "G1", "H")}}

    def k_planning(self):
        offset = int(self.kind.rsplit("-", 1)[-1][:-1])
        reference, bands = self.reference(), self.bands()
        target = reference["slow_c"] + offset
        template, tspec = self.template("d_spam")
        require_effort(tspec, "d_spam")
        policy = gate_policy(self.sensors, bands, turn_cap_s=300, chunk_tokens=256, heavy=False, per_turn=False,
                             g0_cap_s=self.g0_cap_s)
        step = self.config["step"]
        spec = step_spec(tspec, step, policy, deadman_s=step["deadman_s"])
        config = member_config(template, spec, run_id=f"align-v4-r1-{self.kind}", kind=self.kind)
        member = self.run_member(config, self.planning_hook(reference, target, rearm_s=step["deadman_s"]))
        from joulewise.align.apple.thermal_desk import read_bundle_record
        record = read_bundle_record(member.bundle)
        thermal = member.ep.hardware.get("thermal") or {}
        g0 = next((r for r in thermal.get("intervals", []) if r["kind"] == "G0"), None)
        if g0 is None:
            raise RuntimeFailure(f"{self.kind}: member has no G0 interval")
        incomplete = incomplete_member_reasons(member)
        if "r1.g0_timeout_run" in member.ep.flags:
            incomplete = [r for r in incomplete if r != "thermal.start_gate_timeout"]
        if g0["outcome"] != "released" and "r1.g0_timeout_run" not in member.ep.flags:
            # Round-4 executing review HIGH-1: a G0 that timed out has no release
            # temperature (its "release" row is only the last sample), and the
            # g0_unreleased stop leaves a member with no turn, so energy_j is 0.
            # It must never reach beta_T (U5) as a point. LEAD-RULINGS-2 R6-2:
            # the designed start state was not reached, so the segment is
            # INCONCLUSIVE (no energy, no release temperature); the driver
            # precools and retries it once. Any other fault still fails it.
            if g0_timeout_only(incomplete):
                return {**self.g0_inconclusive_fields(member, g0, incomplete, reference),
                        "delta_slow_c": bands["delta_slow_c"], "designed_offset_c": offset,
                        "designed_release_c": target}
            raise RuntimeFailure(f"{self.kind}: designed start state not reached: G0 {g0['outcome']} "
                                 f"(no release; turns {len(member.ep.turns)}; {incomplete})")
        if incomplete:
            # A deadman- or fault-cut planning turn is a partial energy (HIGH-1).
            raise RuntimeFailure(f"{self.kind}: planning member is not one complete turn: {incomplete}")
        return {"reference_c": reference["slow_c"], "g0_release_c": (
                    g0["release"]["slow_c"] if g0["outcome"] == "released" else None),
                "preheat": getattr(self, "preheat", {}), "bands_c": bands,
                "candidate_only": "r1.g0_timeout_run" in member.ep.flags,
                "delta_slow_c": bands["delta_slow_c"], "energy_j": record["turn_owned_j"],
                "designed_offset_c": offset, "designed_release_c": target, "g0_outcome": g0["outcome"],
                **g0_wait_fields(g0, self.armed_g0_cap_s),
                "bundle": str(member.bundle.relative_to(self.out)), "member_status": member.status,
                "episode_flags": list(member.ep.flags), "ac_powermode": member.ep.hardware.get("ac_powermode")}

    def k_x_g(self):
        template, tspec = self.template("x_g")
        if type(tspec.get("max_turns")) is not int:
            raise Refused("x-g template carries a PENDING WP18 X max_turns; regenerate the kit after WP18")
        step = self.step_d_result()
        spec = dict(tspec)
        spec.update(thermal=self.gated_policy(step["slots"], heavy=False, per_turn=True), warmup_condition="benign")
        config = member_config(template, spec, run_id="align-v4-r1-x-g", kind=self.kind)
        reference = self.reference()   # Authenticated step-D R_D (RL-59/72).
        member = self.run_member(config, self.reference_hook(reference))
        from joulewise.align.apple.thermal_desk import read_bundle_record
        record = read_bundle_record(member.bundle)
        return {**self.reference_fields(reference, member.ep), **self.schedule_fields(template),
                "energy_j": record["turn_owned_j"], "admitted_turns": len(member.ep.turns),
                "bundle": str(member.bundle.relative_to(self.out)), "member_status": member.status,
                "episode_flags": list(member.ep.flags), "phases_s": episode_phases(member.ep),
                "ac_powermode": member.ep.hardware.get("ac_powermode")}

    def k_harvest(self):
        parent = self.out.parent
        files, events = {}, []
        for path in sorted(parent.rglob("*")):
            if not path.is_file() or path.is_symlink() or self.out in path.parents:
                continue
            files[path.relative_to(parent).as_posix()] = sha256_file(path)
            if path.name == RESULT_NAME:
                try:
                    battery = json.loads(path.read_text()).get("battery") or {}
                except ValueError:
                    continue
                for event in battery.get("charge_resume_events", ()):
                    events.append({**event, "segment": path.parent.relative_to(parent).as_posix()})
        manifest = {"schema": "joulewise.align.r1_harvest_manifest.v1", "root": str(parent), "files": files}
        raw = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
        (self.out / "harvest_manifest.json").write_bytes(raw)
        events.sort(key=lambda e: e["epoch_s"])
        return {"files": len(files), "manifest_sha256": hashlib.sha256(raw).hexdigest(),
                "charge_resume_events": events,
                "charge_resume_soc_pct": events[0]["soc_pct"] if events else None}

    def dispatch(self):
        kind = self.kind
        if kind in ("calibration-pre", "calibration-post"):
            return self.k_calibration()
        if kind == "idle":
            return self.k_idle()
        if kind == "idle-until-soak":
            return self.k_idle_until_soak()
        if kind == "g0-release-soak":
            return self.k_g0_release_soak()
        if kind == "capture-predecessor-30b":
            return self.k_capture_predecessor_30b()
        if kind == "step-30b":
            return self.k_step_30b()
        if kind == "step-d":
            return self.k_step_d()
        if kind in contract.HIGH_POWER_KINDS:
            return self.k_aba_leg()
        if kind == "d-4bit":
            return self.k_d_4bit()
        if kind in contract.GATED_D_KINDS:
            return self.k_gated_d()
        if kind in contract.PLANNING_KINDS:
            return self.k_planning()
        if kind == "x-g":
            return self.k_x_g()
        if kind == "harvest":
            return self.k_harvest()
        raise Refused(f"unknown --r1-kind {kind!r}")

    def run(self):
        if self.kind in contract.NEEDS_SOAK_REFERENCE and self.soak is None:
            raise Refused(f"{self.kind} needs --soak-reference")
        if self.kind not in ("calibration-pre", "calibration-post", "harvest"):
            self.sensors  # refuse a PENDING R0 sensor selection before any host command
        self.start_journals()
        fields = self.dispatch()
        self.stop_journals()
        battery = self.battery.summary()
        result = {"schema": RESULT_SCHEMA, "kind": self.kind, "backend": self.backend.name,
                  "config_sha256": self.config_sha256, **fields, **self.load.fields(),
                  "load_journal_errors": self.load_errors, "battery": battery}
        if self.kind in BATTERY_DRAIN_KINDS:
            result["battery_drain_pct_per_h"] = battery["drain_pct_per_h"]
        missing = contract.missing_fields(self.kind, result, quiet=True,
                                          contract_key="idle_soak" if self.kind == "idle" else None)
        if missing:
            raise RuntimeFailure(f"{self.kind}: runtime result misses contract fields {missing}")
        return result


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--config", type=Path, required=True, help="R1 runtime config (repo-relative or absolute)")
    parser.add_argument("--r1-kind", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--duration-s", type=float)
    parser.add_argument("--soak-reference", type=Path)
    parser.add_argument("--host-lock-fd", type=int)
    parser.add_argument("--smoke-part", choices=("A", "B"))
    parser.add_argument("--smoke-started", type=float)
    return parser.parse_args(argv)


def main(argv=None, *, backend_factory=None, stdout=None):
    args = parse_args(argv)
    previous_smoke_signal = signal.getsignal(SMOKE_WATCHDOG_SIGNAL)
    term = Termination().install()
    out = Path(args.output).resolve()
    # Every print below this point (controller, adapters, mlx) goes to stderr;
    # stdout carries exactly one JSON object for the driver.
    own_stdout = stdout is None
    stdout = os.fdopen(os.dup(1), "w") if own_stdout else stdout
    saved_fd = os.dup(1)
    os.dup2(2, 1)
    previous_stdout, sys.stdout = sys.stdout, sys.stderr
    record = {"kind": args.r1_kind, "status": "refused", "started_epoch_s": time.time()}
    terminal, owner = threading.Lock(), []
    result, code, segment, backend = None, EXIT_REFUSED, None, None
    created = False
    try:
        try:
            out.mkdir(parents=True, exist_ok=False)
        except FileExistsError as error:
            # Never write into another attempt's directory (the driver renames rejected ones).
            raise Refused(f"--output {out} already exists") from error
        created = True

        def on_watchdog():
            # LOW-1: the forced exit still stops powermetrics and leaves a
            # terminal record. One writer owns the terminal record (Sol
            # critique): the watchdog takes ownership only if the normal path
            # has not, and then the normal path never publishes.
            if not terminal.acquire(timeout=2.0):
                return               # the normal path is writing its record now
            try:
                if not owner:
                    owner.append("watchdog")
                    watchdog_teardown(out, {**record, "signal": term.signum or term.armed_signum})
            finally:
                terminal.release()
        term.on_timeout = on_watchdog
        config, config_sha256 = load_config(resolve(args.config))
        record["config_sha256"] = config_sha256
        soak = read_soak_reference(args.soak_reference)
        backend = (backend_factory or make_backend)(config)
        segment = Segment(kind=args.r1_kind, out=out, duration_s=args.duration_s, soak=soak, config=config,
                          config_sha256=config_sha256, backend=backend)
        segment.host_lock_fd = args.host_lock_fd
        if args.smoke_part and args.r1_kind == "step-d":
            segment.smoke_part = args.smoke_part
            segment.smoke_started = args.smoke_started if args.smoke_started is not None else time.monotonic()
            watchdog = segment.smoke_watchdog = SmokeWatchdog()
            def smoke_timeout(_sig, _frame):
                if watchdog.active:
                    raise RuntimeFailure("smoke part wall cap reached; partial smoke is not a pass")
            signal.signal(SMOKE_WATCHDOG_SIGNAL, smoke_timeout)
            watchdog.set(max(.001, SMOKE_ADMISSION_S - (time.monotonic() - segment.smoke_started)))
        result = segment.run()
        (out / RESULT_NAME).write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
        record["status"], code = "complete", 0
    except SystemExit as stop:
        record.update(status="aborted", signal=term.signum, error=f"SystemExit: {stop.code}")
        code = stop.code if isinstance(stop.code, int) else 128 + (term.signum or signal.SIGTERM)
    except Refused as error:
        record.update(status="refused", error=str(error))
        code = EXIT_REFUSED
    except BaseException as error:  # noqa: BLE001 - every exit path writes the terminal record
        record.update(status="failed", error=f"{type(error).__name__}: {error}",
                      traceback=traceback.format_exc()[-4000:])
        code = EXIT_FAILED
    finally:
        if args.smoke_part:
            if getattr(segment, "smoke_watchdog", None) is not None:
                segment.smoke_watchdog.stop()
            signal.signal(SMOKE_WATCHDOG_SIGNAL, previous_smoke_signal)
        try:
            if segment is not None:
                for error in segment.close():
                    record.setdefault("teardown_errors", []).append(f"{type(error).__name__}: {error}")
            if backend is not None:
                backend.close()
        except BaseException as error:  # noqa: BLE001
            record.setdefault("teardown_errors", []).append(f"{type(error).__name__}: {error}")
        finally:
            record["ended_epoch_s"] = time.time()
            if created:
                try:
                    with terminal:
                        if not owner:
                            write_custody(out, record)
                            owner.append("main")
                except OSError as error:
                    record.setdefault("teardown_errors", []).append(f"custody: {error}")
            os.dup2(saved_fd, 1)
            os.close(saved_fd)
            sys.stdout = previous_stdout
            if code == 0:
                stdout.write(json.dumps(result, sort_keys=True, allow_nan=False) + "\n")
                stdout.flush()
            if own_stdout:
                stdout.close()
            if code != 0:
                print(f"align_r1_runtime: {record['status']}: {record.get('error')}", file=sys.stderr)
            term.restore()
    return code
