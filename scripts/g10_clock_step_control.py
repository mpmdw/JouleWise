#!/usr/bin/env python3
"""G10: the clock-step positive control, run by the driver at a window's tail.

What it shows: when the wall clock is stepped, the clock hazard's residual
check refuses the stepped before/after anchor pair. That is the physical
evidence that the arm-time clock check can see a step at all.

The anchor is CLOCK_REALTIME minus CLOCK_MONOTONIC_RAW. With network time OFF
it drifts linearly at the kernel frequency word f (read without privileges by
``ntp_adjtime(modes=0)``). The residual is the anchor's movement minus
f x elapsed RAW time; a wall-clock step shows up as a residual jump.

Steps (gate-prune plan section 4, "G10"):

1. Read f0 and the anchor before anything changes.
2. ``sudo -n systemsetup -setusingnetworktime on`` (the sudoers slice argv).
   Its return code and output are recorded only; nothing reads its wording.
3. Poll the anchor at 1 Hz for up to 300 s from the ON, until the residual
   moves more than 5 ms.
4. Evaluate the clock residual verdict on the before/after pair. A REFUSE
   whose reasons include the residual is DISCHARGED.
5. Keep network time ON while reading f once a minute; switch OFF as soon as
   |f| <= 3.0 ppm, or 15 min after the ON. OFF always runs in ``finally``;
   SIGTERM and SIGHUP raise into it, and signals arriving during OFF are
   deferred so OFF completes.
6. Write ``<night-dir>/g10.json`` create-once (O_EXCL, fsync).

The result never stops anything: it is a disclosed diagnostic
(``g10.discharged`` / ``g10.not_discharged``). A NOT_DISCHARGED result goes to
one consult before BETA arms. A failed OFF is a fault (exit 4); the next arm
runs OFF as an action anyway.

Fixed driver argv::

    <python> scripts/g10_clock_step_control.py --night-dir <night_dir> \
        [--t-stream-max-s <hazard_window.T_stream_max_s>]

Exit codes: 0 record written and OFF succeeded; 1 unexpected error (record
written, OFF ran); 2 usage error; 3 the record already exists (nothing run);
4 OFF failed on every attempt (record written); 5 the record could not be
written (it is printed to stderr); 128+N interrupted by signal N (record
written, OFF ran).

Every hardware seam (command runner, anchor reader, frequency reader, sleep,
clocks, boot id) is injected through ``Env`` so tests never touch the Mac.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback
from typing import Any, Callable, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import clock_reference, kernel_clock  # noqa: E402

SCHEMA = "joulewise.g10_clock_step_control.v1"
EVALUATOR = "g10-residual-pair/v1"
RECORD_BASENAME = "g10.json"

SUDO = "/usr/bin/sudo"
SYSTEMSETUP = "/usr/sbin/systemsetup"
ON_ARGV = (SUDO, "-n", SYSTEMSETUP, "-setusingnetworktime", "on")
OFF_ARGV = (SUDO, "-n", SYSTEMSETUP, "-setusingnetworktime", "off")
BOOT_ARGV = ("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid")

PASS = "PASS"
REFUSE = "REFUSE"
UNMEASURED = "UNMEASURED"

DISCHARGED = "DISCHARGED"
NOT_DISCHARGED = "NOT_DISCHARGED"
RESULT_UNMEASURED = "UNMEASURED"
INTERRUPTED = "INTERRUPTED"
ERROR = "ERROR"

REASON_RESIDUAL = "clock.residual_exceeds_limit"
REASON_FREQUENCY = "clock.frequency_changed"
REASON_SKEW = "clock.read_skew_exceeds_limit"
REASON_NO_ANCHOR = "clock.anchor_unread"
REASON_NO_FREQUENCY = "clock.frequency_unread"

FLAG_CODES = {
    DISCHARGED: "g10.discharged",
    NOT_DISCHARGED: "g10.not_discharged",
    RESULT_UNMEASURED: "g10.unmeasured",
    INTERRUPTED: "g10.interrupted",
    ERROR: "g10.error",
}

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2
EXIT_EXISTS = 3
EXIT_OFF_FAILED = 4
EXIT_WRITE_FAILED = 5

NS = 1_000_000_000


@dataclass(frozen=True)
class Params:
    """Thresholds and timings. Defaults are the plan's registered values."""

    t_stream_max_s: float = 335.0
    step_threshold_ns: int = 5_000_000
    poll_interval_s: float = 1.0
    poll_timeout_s: float = 300.0
    residual_limit_ns: int = 1_000_000
    skew_limit_ns: int = 1_000_000
    anchor_read_attempts: int = 3
    settle_target_ppm: float = 3.0
    settle_read_interval_s: float = 60.0
    settle_max_s: float = 900.0
    command_timeout_s: float = 60.0
    off_attempts: int = 3
    off_retry_delay_s: float = 5.0

    def validate(self) -> None:
        for name in ("t_stream_max_s", "poll_interval_s", "poll_timeout_s",
                     "settle_read_interval_s", "settle_max_s", "command_timeout_s"):
            value = getattr(self, name)
            if not (isinstance(value, (int, float)) and math.isfinite(value) and value > 0):
                raise ValueError(f"{name} must be a positive finite number")
        for name in ("step_threshold_ns", "residual_limit_ns", "skew_limit_ns",
                     "anchor_read_attempts", "off_attempts"):
            if type(getattr(self, name)) is not int or getattr(self, name) <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not (math.isfinite(self.settle_target_ppm) and self.settle_target_ppm >= 0):
            raise ValueError("settle_target_ppm must be a non-negative finite number")
        if not (math.isfinite(self.off_retry_delay_s) and self.off_retry_delay_s >= 0):
            raise ValueError("off_retry_delay_s must be non-negative")


# --------------------------------------------------------------------------
# Hardware seams


def _text(value: Any) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", "surrogateescape") if isinstance(value, bytes) else str(value)


def real_run(argv: Sequence[str], timeout: float) -> Mapping[str, Any]:
    """Run one command in its own session, so a group signal aimed at this
    process does not also kill the OFF it is running."""
    result = subprocess.run(list(argv), capture_output=True, timeout=timeout, check=False,
                            stdin=subprocess.DEVNULL, start_new_session=True)
    return {"returncode": int(result.returncode), "stdout": _text(result.stdout),
            "stderr": _text(result.stderr)}


def real_read_anchor() -> Mapping[str, int]:
    return asdict(clock_reference.sample_anchor())


def real_read_frequency() -> Mapping[str, Any]:
    return kernel_clock.validate_probe(kernel_clock.read_kernel_frequency())


def real_boot_session_uuid() -> str | None:
    try:
        result = subprocess.run(list(BOOT_ARGV), capture_output=True, timeout=10, check=False,
                                stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return None
    value = _text(result.stdout).strip().lower()
    return value if result.returncode == 0 and value else None


@dataclass
class Env:
    run: Callable[[Sequence[str], float], Mapping[str, Any]] = real_run
    read_anchor: Callable[[], Mapping[str, int]] = real_read_anchor
    read_frequency: Callable[[], Mapping[str, Any]] = real_read_frequency
    sleep: Callable[[float], None] = time.sleep
    monotonic_raw_ns: Callable[[], int] = field(
        default=lambda: time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW))
    monotonic_ns: Callable[[], int] = time.monotonic_ns
    wall_s: Callable[[], float] = time.time
    boot_session_uuid: Callable[[], str | None] = real_boot_session_uuid


# --------------------------------------------------------------------------
# Clock arithmetic


def anchor_ns(sample: Mapping[str, int]) -> int:
    return int(sample["realtime_ns"]) - int(sample["monotonic_raw_ns"])


def signed_residual(before: Mapping[str, int], after: Mapping[str, int],
                    frequency: Mapping[str, Any]) -> Fraction:
    """Anchor movement minus f x RAW span, signed and exact."""
    delta = anchor_ns(after) - anchor_ns(before)
    span = int(after["monotonic_raw_ns"]) - int(before["monotonic_raw_ns"])
    return Fraction(delta) - Fraction(int(frequency["raw_word"]) * span,
                                      kernel_clock.FREQUENCY_SCALE * 1_000_000)


def _ns_int(value: Fraction) -> int:
    return int(round(value))


def evaluate_pair(before: Mapping[str, int] | None, after: Mapping[str, int] | None,
                  f_before: Mapping[str, Any] | None, f_after: Mapping[str, Any] | None,
                  params: Params) -> dict[str, Any]:
    """The clock hazard's residual verdict on one before/after pair.

    Same physics as the arm-time clock check: each anchor read pair must have
    skew <= 1 ms (else UNMEASURED); the residual must stay within 1 ms; the
    frequency word must not change. Either of the last two refuses.
    """
    reasons: list[str] = []
    if before is None or after is None:
        return {"evaluator": EVALUATOR, "verdict": UNMEASURED, "reasons": [REASON_NO_ANCHOR],
                "residual_ns": None}
    if f_before is None or f_after is None:
        return {"evaluator": EVALUATOR, "verdict": UNMEASURED,
                "reasons": [REASON_NO_FREQUENCY], "residual_ns": None}
    if max(int(before["read_skew_ns"]), int(after["read_skew_ns"])) > params.skew_limit_ns:
        return {"evaluator": EVALUATOR, "verdict": UNMEASURED, "reasons": [REASON_SKEW],
                "residual_ns": None}
    delta = anchor_ns(after) - anchor_ns(before)
    span = int(after["monotonic_raw_ns"]) - int(before["monotonic_raw_ns"])
    residual = kernel_clock.anchor_residual_ns(delta, span, f_before)
    if residual > params.residual_limit_ns:
        reasons.append(REASON_RESIDUAL)
    if int(f_before["raw_word"]) != int(f_after["raw_word"]):
        reasons.append(REASON_FREQUENCY)
    return {"evaluator": EVALUATOR, "verdict": REFUSE if reasons else PASS,
            "reasons": reasons, "residual_ns": _ns_int(residual),
            "residual_limit_ns": params.residual_limit_ns, "span_ns": span,
            "f_before_raw_word": int(f_before["raw_word"]),
            "f_after_raw_word": int(f_after["raw_word"])}


def result_from_verdict(verdict: Mapping[str, Any]) -> str:
    """REFUSE because of the residual is DISCHARGED. A refusal only for a
    changed frequency word does not show that a step was seen."""
    if verdict.get("verdict") == UNMEASURED:
        return RESULT_UNMEASURED
    if verdict.get("verdict") == REFUSE and REASON_RESIDUAL in verdict.get("reasons", ()):
        return DISCHARGED
    return NOT_DISCHARGED


def frequency_within(probe: Mapping[str, Any], target_ppm: float) -> bool:
    """|f| <= target, exact on the raw word."""
    bound = Fraction(str(target_ppm)) * kernel_clock.FREQUENCY_SCALE
    return abs(int(probe["raw_word"])) <= bound


# --------------------------------------------------------------------------
# Signals


class Interrupted(BaseException):
    """Raised by the SIGTERM/SIGHUP handler so control unwinds into finally."""

    def __init__(self, signum: int):
        super().__init__(signum)
        self.signum = signum


class SignalGuard:
    HANDLED = (signal.SIGTERM, signal.SIGHUP)

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.deferring = False
        self.deferred: list[int] = []
        self.received: list[int] = []
        self._previous: dict[int, Any] = {}

    def _handler(self, signum, _frame):
        # One-shot: the first signal raises; every later one is only
        # recorded, so nothing can interrupt the unwinding into OFF.
        self.received.append(signum)
        if self.deferring:
            self.deferred.append(signum)
            return
        self.deferring = True
        raise Interrupted(signum)

    def install(self) -> None:
        if not self.enabled:
            return
        for signum in self.HANDLED:
            self._previous[signum] = signal.signal(signum, self._handler)

    def defer(self) -> None:
        self.deferring = True

    def restore(self) -> None:
        for signum, previous in self._previous.items():
            signal.signal(signum, previous)
        self._previous.clear()


def _signal_name(signum: int) -> str:
    try:
        return signal.Signals(signum).name
    except ValueError:
        return str(signum)


# --------------------------------------------------------------------------
# The control


class Control:
    def __init__(self, params: Params, env: Env, out_path: Path, argv: Sequence[str],
                 evaluate: Callable[..., Mapping[str, Any]] = evaluate_pair):
        self.params = params
        self.env = env
        self.out_path = out_path
        self.evaluate = evaluate
        self.phase = "start"
        self.on_raw_ns: int | None = None
        self.record: dict[str, Any] = {
            "schema_version": SCHEMA,
            "argv": list(argv),
            "out_path": str(out_path),
            "pid": os.getpid(),
            "parameters": asdict(params),
            "network_time_argv": {"on": list(ON_ARGV), "off": list(OFF_ARGV)},
            "boot_session_uuid": None,
            "started": None,
            "finished": None,
            "f0": None,
            "anchor_before": None,
            "commands": [],
            "trace": [],
            "step": None,
            "f_after_step": None,
            "verdict": None,
            "settling": {"reads": [], "stop_reason": None},
            "f1": None,
            "next_arm_frequency_gate": None,
            "off_ok": False,
            "result": None,
            "flag_code": None,
            "interrupted": None,
            "deferred_signals": [],
            "error": None,
            "notes": [],
        }

    # -- small helpers -----------------------------------------------------

    def stamp(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, reader, kind in (("wall_s", self.env.wall_s, float),
                                  ("monotonic_ns", self.env.monotonic_ns, int),
                                  ("monotonic_raw_ns", self.env.monotonic_raw_ns, int)):
            try:
                out[key] = kind(reader())
            except Exception as exc:  # a stamp never stops the control
                out[key] = None
                out.setdefault("errors", []).append(f"{key}: {exc!r}")
        return out

    def sleep_until_raw(self, target_ns: int) -> None:
        remaining = target_ns - self.env.monotonic_raw_ns()
        if remaining > 0:
            self.env.sleep(remaining / NS)

    def read_anchor(self) -> dict[str, Any] | None:
        """Best-skew anchor over a few tries; None when every try failed."""
        best: dict[str, Any] | None = None
        errors: list[str] = []
        for _ in range(self.params.anchor_read_attempts):
            try:
                sample = dict(self.env.read_anchor())
                sample = {"realtime_ns": int(sample["realtime_ns"]),
                          "monotonic_raw_ns": int(sample["monotonic_raw_ns"]),
                          "read_skew_ns": int(sample["read_skew_ns"])}
            except Exception as exc:
                errors.append(repr(exc))
                continue
            if best is None or sample["read_skew_ns"] < best["read_skew_ns"]:
                best = sample
            if sample["read_skew_ns"] <= self.params.skew_limit_ns:
                break
        if best is not None and errors:
            best["read_errors"] = errors
        return best

    def read_frequency(self) -> tuple[dict[str, Any] | None, str | None]:
        try:
            probe = kernel_clock.validate_probe(dict(self.env.read_frequency()))
            return dict(probe), None
        except Exception as exc:
            return None, repr(exc)

    def command(self, name: str, argv: Sequence[str]) -> dict[str, Any]:
        entry: dict[str, Any] = {"name": name, "argv": list(argv), "started": self.stamp(),
                                 "returncode": None, "stdout": None, "stderr": None,
                                 "timed_out": False, "error": None}
        self.record["commands"].append(entry)
        try:
            result = self.env.run(tuple(argv), self.params.command_timeout_s)
            entry["returncode"] = int(result["returncode"])
            entry["stdout"] = _text(result.get("stdout"))
            entry["stderr"] = _text(result.get("stderr"))
        except subprocess.TimeoutExpired as exc:
            entry["timed_out"] = True
            entry["error"] = repr(exc)
            entry["stdout"] = _text(exc.stdout)
            entry["stderr"] = _text(exc.stderr)
        except Exception as exc:
            entry["error"] = repr(exc)
        finally:
            entry["finished"] = self.stamp()
        return entry

    # -- phases --------------------------------------------------------------

    def body(self) -> None:
        params = self.params
        self.phase = "before"
        f0, f0_error = self.read_frequency()
        self.record["f0"] = f0
        before = self.read_anchor()
        self.record["anchor_before"] = before
        if f0 is None or before is None or before["read_skew_ns"] > params.skew_limit_ns:
            # Nothing to compare a step against: spend no ON. The pair
            # verdict on (before, before) names what was missing.
            self.record["verdict"] = evaluate_pair(before, before, f0, f0, params)
            self.record["notes"].append(
                "network time ON not run: the before state could not be measured"
                + (f" ({f0_error})" if f0_error else ""))
            return

        self.phase = "on"
        self.on_raw_ns = self.env.monotonic_raw_ns()
        self.command("on", ON_ARGV)

        self.phase = "poll"
        on_ns = self.on_raw_ns
        timeout_ns = int(round(params.poll_timeout_s * NS))
        interval_ns = int(round(params.poll_interval_s * NS))
        detected = None
        k = 1
        while k * interval_ns <= timeout_ns:
            self.sleep_until_raw(on_ns + k * interval_ns)
            k += 1
            sample = self.read_anchor()
            if sample is None:
                self.record["trace"].append({"elapsed_since_on_s": None, "error": "anchor unread"})
                continue
            residual = signed_residual(before, sample, f0)
            point = {**sample,
                     "elapsed_since_on_s": (sample["monotonic_raw_ns"] - on_ns) / NS,
                     "residual_ns": _ns_int(residual)}
            self.record["trace"].append(point)
            if abs(residual) > params.step_threshold_ns:
                detected = len(self.record["trace"]) - 1
                break
            # Fast-forward the index if a slow read overran later slots.
            k = max(k, (self.env.monotonic_raw_ns() - on_ns) // interval_ns + 1)
        measured = [p for p in self.record["trace"] if "residual_ns" in p]
        after = self.record["trace"][detected] if detected is not None else (
            measured[-1] if measured else None)
        after_anchor = None if after is None else {
            key: after[key] for key in ("realtime_ns", "monotonic_raw_ns", "read_skew_ns")}
        self.record["step"] = {
            "detected": detected is not None,
            "trace_index": detected,
            "threshold_ns": params.step_threshold_ns,
            "after": after_anchor,
            "residual_ns": None if after is None else after["residual_ns"],
            "elapsed_since_on_s": None if after is None else after["elapsed_since_on_s"],
        }

        self.phase = "evaluate"
        f_after, f_after_error = self.read_frequency()
        self.record["f_after_step"] = f_after
        if f_after_error:
            self.record["notes"].append(f"frequency after step unread: {f_after_error}")
        self.record["verdict"] = dict(self.evaluate(before, after_anchor, f0, f_after, params))

        self.phase = "settle"
        self.settle()

    def settle(self) -> None:
        params = self.params
        on_ns = self.on_raw_ns
        assert on_ns is not None
        reads = self.record["settling"]["reads"]
        step_ns = int(round(params.settle_read_interval_s * NS))
        limit_ns = int(round(params.settle_max_s * NS))
        k = max(1, -(-(self.env.monotonic_raw_ns() - on_ns) // step_ns))
        while True:
            offset = min(k * step_ns, limit_ns)
            self.sleep_until_raw(on_ns + offset)
            probe, error = self.read_frequency()
            now = self.env.monotonic_raw_ns()
            reads.append({"elapsed_since_on_s": (now - on_ns) / NS, "probe": probe,
                          "error": error})
            if probe is not None and frequency_within(probe, params.settle_target_ppm):
                self.record["settling"]["stop_reason"] = "target"
                return
            if offset >= limit_ns or now - on_ns >= limit_ns:
                self.record["settling"]["stop_reason"] = "timeout"
                return
            k = max(k + 1, -(-(now - on_ns) // step_ns))

    def off(self) -> None:
        self.phase = "off"
        for attempt in range(1, self.params.off_attempts + 1):
            entry = self.command("off", OFF_ARGV)
            entry["attempt"] = attempt
            if entry["returncode"] == 0 and entry["error"] is None:
                self.record["off_ok"] = True
                return
            if attempt < self.params.off_attempts and self.params.off_retry_delay_s > 0:
                try:
                    self.env.sleep(self.params.off_retry_delay_s)
                except Exception as exc:
                    self.record["notes"].append(f"OFF retry sleep failed: {exc!r}")

    def after_off(self) -> None:
        f1, error = self.read_frequency()
        self.record["f1"] = f1
        if f1 is None:
            self.record["notes"].append(f"f1 unread: {error}")
            return
        try:
            gate = kernel_clock.frequency_gate(f1, self.params.t_stream_max_s)
            self.record["next_arm_frequency_gate"] = {
                "t_stream_max_s": gate["t_stream_max_s"], "bound_ms": gate["bound_ms"],
                "margin_ms": gate["margin_ms"], "passes": bool(gate["passes"])}
        except Exception as exc:
            self.record["notes"].append(f"next-arm frequency gate not computed: {exc!r}")

    # -- the whole run ---------------------------------------------------------

    def note_interrupted(self, exc: Interrupted) -> None:
        if self.record["interrupted"] is None:
            self.record["interrupted"] = {"signum": exc.signum,
                                          "signal": _signal_name(exc.signum),
                                          "phase": self.phase}
        if self.phase == "settle":
            self.record["settling"]["stop_reason"] = "interrupted"

    def run(self, guard: SignalGuard) -> None:
        try:
            try:
                self.record["boot_session_uuid"] = self.env.boot_session_uuid()
            except Exception as exc:
                self.record["notes"].append(f"boot session uuid unread: {exc!r}")
            self.record["started"] = self.stamp()
            self.body()
        except Interrupted as exc:
            self.note_interrupted(exc)
        except BaseException as exc:  # noqa: BLE001 - record everything, then OFF
            self.record["error"] = {"phase": self.phase, "repr": repr(exc),
                                    "traceback": traceback.format_exc()}
            if self.phase == "settle":
                self.record["settling"]["stop_reason"] = "error"
        finally:
            # The handler is one-shot, so at most one Interrupted can land
            # here before deferral is on; catch it and go on to OFF.
            while True:
                try:
                    guard.defer()
                    break
                except Interrupted as exc:
                    self.note_interrupted(exc)
            try:
                self.off()
            finally:
                try:
                    self.after_off()
                except BaseException as exc:  # noqa: BLE001
                    self.record["notes"].append(f"after-OFF read failed: {exc!r}")

    def finalize(self, guard: SignalGuard) -> None:
        self.record["deferred_signals"] = [_signal_name(s) for s in guard.deferred]
        self.record["finished"] = self.stamp()
        # A verdict reached before an interruption (for example during the
        # frequency settling) stands; the interruption is recorded beside it.
        verdict = self.record["verdict"]
        if verdict is not None:
            result = result_from_verdict(verdict)
        elif self.record["interrupted"] is not None:
            result = INTERRUPTED
        else:
            result = ERROR
        self.record["result"] = result
        self.record["flag_code"] = FLAG_CODES[result]


def render(record: Mapping[str, Any]) -> bytes:
    return (json.dumps(record, sort_keys=True, indent=2, ensure_ascii=True,
                       allow_nan=False) + "\n").encode("ascii")


def write_create_once(path: Path, raw: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        view = memoryview(raw)
        while view:
            written = os.write(fd, view)
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    try:
        dir_fd = os.open(path.parent, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(dir_fd)
    except OSError:
        pass
    finally:
        os.close(dir_fd)


def run_control(params: Params, env: Env, out_path: Path, argv: Sequence[str], *,
                evaluate: Callable[..., Mapping[str, Any]] = evaluate_pair,
                handle_signals: bool = True,
                stderr=None) -> tuple[dict[str, Any] | None, int]:
    """Run G10 once. Returns (record, exit code). Nothing is run, not even
    OFF, when the record already exists."""
    stderr = stderr if stderr is not None else sys.stderr
    params.validate()
    out_path = Path(out_path)
    if os.path.lexists(out_path):
        print(f"g10: {out_path} already exists; G10 runs once per night", file=stderr)
        return None, EXIT_EXISTS
    if not out_path.parent.is_dir():
        print(f"g10: night directory {out_path.parent} does not exist", file=stderr)
        return None, EXIT_USAGE
    control = Control(params, env, out_path, argv, evaluate=evaluate)
    guard = SignalGuard(enabled=handle_signals)
    guard.install()
    try:
        try:
            control.run(guard)
        except Interrupted as exc:
            # The first signal landed inside an exception handler; OFF has
            # already run in run()'s finally.
            control.note_interrupted(exc)
        control.finalize(guard)
    finally:
        guard.restore()
    record = control.record
    raw = render(record)
    try:
        write_create_once(out_path, raw)
    except OSError as exc:
        print(f"g10: cannot write {out_path}: {exc!r}", file=stderr)
        stderr.write(raw.decode("ascii"))
        return record, EXIT_WRITE_FAILED
    if not record["off_ok"]:
        return record, EXIT_OFF_FAILED
    if record["interrupted"] is not None:
        return record, 128 + int(record["interrupted"]["signum"])
    if record["error"] is not None:
        return record, EXIT_ERROR
    return record, EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="G10 clock-step positive control (network time ON, detect the step, OFF).")
    parser.add_argument("--night-dir", required=True, type=Path,
                        help="the driver's night directory; the record is <night-dir>/g10.json")
    defaults = Params()
    parser.add_argument("--t-stream-max-s", type=float, default=defaults.t_stream_max_s,
                        help="longest sampler stream, for the next-arm frequency gate")
    parser.add_argument("--poll-timeout-s", type=float, default=defaults.poll_timeout_s)
    parser.add_argument("--settle-max-s", type=float, default=defaults.settle_max_s)
    parser.add_argument("--settle-target-ppm", type=float, default=defaults.settle_target_ppm)
    return parser


def main(argv: Sequence[str] | None = None, *, env: Env | None = None,
         stdout=None, stderr=None) -> int:
    stdout = stdout if stdout is not None else sys.stdout
    if argv is None:
        full_argv = [sys.argv[0] if sys.argv else __file__, *sys.argv[1:]]
    else:
        full_argv = [__file__, *argv]
    try:
        args = build_parser().parse_args(full_argv[1:])
    except SystemExit as exc:
        return EXIT_USAGE if exc.code else EXIT_OK
    params = Params(t_stream_max_s=args.t_stream_max_s, poll_timeout_s=args.poll_timeout_s,
                    settle_max_s=args.settle_max_s, settle_target_ppm=args.settle_target_ppm)
    try:
        params.validate()
    except ValueError as exc:
        print(f"g10: {exc}", file=stderr if stderr is not None else sys.stderr)
        return EXIT_USAGE
    out_path = Path(args.night_dir) / RECORD_BASENAME
    record, code = run_control(params, env if env is not None else Env(), out_path, full_argv,
                               stderr=stderr)
    if record is not None:
        print(f"g10: {record['result']} off_ok={record['off_ok']} record={out_path}",
              file=stdout)
    return code


if __name__ == "__main__":
    sys.exit(main())
