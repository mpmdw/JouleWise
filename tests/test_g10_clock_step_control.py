"""G10 clock-step positive control: discharge logic, OFF guarantees, settling.

Every test drives the real control code. Only the hardware seams are fakes:
a simulated Mac supplies the command runner (it never runs sudo or
systemsetup), the RAW/REALTIME anchor reader, the kernel frequency word, the
clocks and sleep. Signals are real: tests deliver SIGTERM and SIGHUP to this
process with os.kill.
"""
from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest

from joulewise import kernel_clock, network_time_off

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "g10_clock_step_control.py"
_spec = importlib.util.spec_from_file_location("g10_clock_step_control_under_test", SCRIPT)
g10 = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = g10
_spec.loader.exec_module(g10)

_REAL_SUBPROCESS_RUN = subprocess.run
NS = 1_000_000_000
WORD_TODAY = -207_749      # -3.17 ppm in the kernel's 2**-16 ppm units
STEP_NS = 1_300_000_000     # one night of accumulated wall-clock error


def probe(word: int) -> dict:
    """A kernel frequency probe whose raw bytes authenticate (validate_probe)."""
    value = kernel_clock.Timex()
    value.freq = word
    value.status = 0
    return {"schema_version": kernel_clock.PROBE_SCHEMA, "modes": 0, "raw_word": word,
            "ppm": word / kernel_clock.FREQUENCY_SCALE, "call_status": 0,
            "timex_status": 0, "errno": 0, "raw_hex": bytes(value).hex()}


class FakeMac:
    """Simulated clocks and network-time switch.

    The anchor (wall minus RAW) drifts at the current frequency word. While
    network time is ON, the wall clock steps by ``step_ns`` after
    ``step_delay_s`` and the word follows ``f_after_on(seconds_since_on)``.
    """

    def __init__(self, *, word=WORD_TODAY, step_ns=STEP_NS, step_delay_s=4.0, steps=True,
                 f_after_on=None, on_result=None, on_raises=None, off_results=None,
                 skew_ns=20_000, sleep_hook=None, run_hook=None, frequency_raises=None):
        self.raw = 5_000 * NS
        self.offset = Fraction(1_790_000_000 * NS)
        self.word = word
        self.step_ns = step_ns
        self.step_delay_s = step_delay_s
        self.steps = steps
        self.f_after_on = f_after_on
        self.on_result = on_result
        self.on_raises = on_raises
        self.off_results = list(off_results or [])
        self.skew_ns = skew_ns
        self.sleep_hook = sleep_hook
        self.run_hook = run_hook
        self.frequency_raises = frequency_raises
        self.network_on = False
        self.on_raw = None
        self.stepped = False
        self.calls = []
        self.frequency_reads = 0
        self.sleeps = []

    # clocks
    def _advance(self, ns):
        while ns > 0:
            chunk = min(ns, NS // 4)
            self.raw += chunk
            self.offset += Fraction(self.word * chunk, kernel_clock.FREQUENCY_SCALE * 10**6)
            ns -= chunk
            if self.network_on:
                since = (self.raw - self.on_raw) / NS
                if self.steps and not self.stepped and since >= self.step_delay_s:
                    self.offset += self.step_ns
                    self.stepped = True
                if self.f_after_on is not None:
                    self.word = self.f_after_on(since)

    def since_on(self):
        return None if self.on_raw is None else (self.raw - self.on_raw) / NS

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        if self.sleep_hook is not None:
            self.sleep_hook(self, seconds)
        self._advance(int(round(seconds * NS)))

    def read_anchor(self):
        return {"realtime_ns": self.raw + int(self.offset // 1),
                "monotonic_raw_ns": self.raw, "read_skew_ns": self.skew_ns}

    def read_frequency(self):
        self.frequency_reads += 1
        if self.frequency_raises is not None and self.frequency_raises(self):
            raise OSError("ntp_adjtime unavailable")
        return probe(self.word)

    def run(self, argv, timeout):
        self.calls.append({"argv": tuple(argv), "timeout": timeout, "raw": self.raw,
                           "since_on": self.since_on()})
        if self.run_hook is not None:
            self.run_hook(self, tuple(argv))
        if tuple(argv) == g10.ON_ARGV:
            self.on_raw = self.raw
            if self.on_raises is not None:
                raise self.on_raises
            self.network_on = True
            return self.on_result or {"returncode": 0, "stdout": "setUsingNetworkTime: On\n",
                                      "stderr": ""}
        if tuple(argv) == g10.OFF_ARGV:
            result = self.off_results.pop(0) if self.off_results else {
                "returncode": 0, "stdout": "setUsingNetworkTime: Off\n", "stderr": ""}
            if isinstance(result, BaseException):
                raise result
            if result["returncode"] == 0:
                self.network_on = False
            return result
        raise AssertionError(f"unexpected command {argv!r}")

    def env(self):
        return g10.Env(run=self.run, read_anchor=self.read_anchor,
                       read_frequency=self.read_frequency, sleep=self.sleep,
                       monotonic_raw_ns=lambda: self.raw,
                       monotonic_ns=lambda: self.raw + 17,
                       wall_s=lambda: (self.raw + self.offset) / NS,
                       boot_session_uuid=lambda: "0f1e2d3c-aaaa-bbbb-cccc-000000000001")

    def commands(self):
        names = {g10.ON_ARGV: "on", g10.OFF_ARGV: "off"}
        return [names[c["argv"]] for c in self.calls]


@pytest.fixture(autouse=True)
def no_real_machine_calls(monkeypatch):
    """The control under test must reach the Mac only through the fakes."""

    def refuse(*args, **kwargs):
        raise AssertionError(f"real subprocess call attempted: {args!r}")

    def refuse_sleep(*_):
        raise AssertionError("real time.sleep called")

    monkeypatch.setattr(subprocess, "run", refuse)
    monkeypatch.setattr(time, "sleep", refuse_sleep)
    before = {s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGHUP)}
    yield
    after = {s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGHUP)}
    assert after == before, "signal handlers were not restored"


def run(mac, tmp_path, **params):
    out = tmp_path / "night" / "g10.json"
    out.parent.mkdir(exist_ok=True)
    record, code = g10.run_control(g10.Params(**params), mac.env(), out,
                                   ["g10_clock_step_control.py", "--night-dir", str(out.parent)])
    return record, code, out


# --------------------------------------------------------------------------
# Discharge


def test_step_trace_discharges_and_writes_the_record(tmp_path):
    mac = FakeMac(f_after_on=lambda since: WORD_TODAY if since < 170 else -190_054)
    record, code, out = run(mac, tmp_path)

    assert code == g10.EXIT_OK
    assert record["result"] == g10.DISCHARGED
    assert record["flag_code"] == "g10.discharged"
    assert record["verdict"]["verdict"] == g10.REFUSE
    assert record["verdict"]["reasons"] == [g10.REASON_RESIDUAL]
    assert mac.commands() == ["on", "off"]
    step = record["step"]
    assert step["detected"] is True
    assert step["elapsed_since_on_s"] == pytest.approx(4.0, abs=1.01)
    assert abs(step["residual_ns"] - STEP_NS) < 2_000_000
    # Before the step every 1 Hz sample sits on the drift line.
    assert all(abs(p["residual_ns"]) <= 1 for p in record["trace"][:-1])
    assert record["f0"]["raw_word"] == WORD_TODAY
    assert record["f1"]["raw_word"] == -190_054
    assert record["off_ok"] is True
    assert record["boot_session_uuid"].startswith("0f1e2d3c")
    assert record["argv"][1:] == ["--night-dir", str(out.parent)]
    assert record["commands"][0]["argv"] == list(g10.ON_ARGV)
    assert record["commands"][0]["stdout"] == "setUsingNetworkTime: On\n"
    on_entry = record["commands"][0]
    assert {"wall_s", "monotonic_ns", "monotonic_raw_ns"} <= set(on_entry["started"])
    assert json.loads(out.read_text()) == record
    assert out.read_bytes() == g10.render(record)


def test_flat_trace_is_not_discharged(tmp_path):
    mac = FakeMac(steps=False)
    record, code, _ = run(mac, tmp_path)

    assert code == g10.EXIT_OK
    assert record["result"] == g10.NOT_DISCHARGED
    assert record["flag_code"] == "g10.not_discharged"
    assert record["verdict"]["verdict"] == g10.PASS
    assert record["step"]["detected"] is False
    assert len(record["trace"]) == 300
    assert record["trace"][-1]["elapsed_since_on_s"] == pytest.approx(300.0)
    assert max(abs(p["residual_ns"]) for p in record["trace"]) <= 1
    assert mac.commands() == ["on", "off"]
    assert mac.network_on is False


def test_frequency_change_alone_does_not_discharge(tmp_path):
    mac = FakeMac(steps=False, f_after_on=lambda since: -150_000)
    record, code, _ = run(mac, tmp_path)

    assert record["verdict"]["verdict"] == g10.REFUSE
    assert record["verdict"]["reasons"] == [g10.REASON_FREQUENCY]
    assert record["result"] == g10.NOT_DISCHARGED
    assert code == g10.EXIT_OK


def test_sub_threshold_slew_still_refused_by_the_residual_check(tmp_path):
    # A 3 ms correction never crosses the 5 ms poll threshold, but the
    # clock module's 1 ms residual check refuses the pair: REFUSE is DISCHARGED.
    mac = FakeMac(step_ns=3_000_000)
    record, _, _ = run(mac, tmp_path)
    assert record["step"]["detected"] is False
    assert record["verdict"]["reasons"] == [g10.REASON_RESIDUAL]
    assert record["result"] == g10.DISCHARGED


def test_on_wording_and_return_code_are_recorded_not_read(tmp_path):
    text = "You need administrator access to run this tool... exiting!\n"
    for result in ({"returncode": 0, "stdout": text, "stderr": ""},
                   {"returncode": 1, "stdout": "", "stderr": "sudo: a password is required\n"}):
        mac = FakeMac(on_result=result)
        sub = tmp_path / str(result["returncode"])
        sub.mkdir()
        record, code, _ = run(mac, sub)
        assert record["result"] == g10.DISCHARGED, "the clock trace decides, not the wording"
        assert record["commands"][0]["returncode"] == result["returncode"]
        assert record["commands"][0]["stdout"] == result["stdout"]
        assert record["commands"][0]["stderr"] == result["stderr"]
        assert code == g10.EXIT_OK


def test_on_command_that_cannot_start_still_polls_and_runs_off(tmp_path):
    mac = FakeMac(on_raises=FileNotFoundError("/usr/bin/sudo"))
    record, code, _ = run(mac, tmp_path)
    assert "FileNotFoundError" in record["commands"][0]["error"]
    assert record["result"] == g10.NOT_DISCHARGED
    assert mac.commands() == ["on", "off"]
    assert code == g10.EXIT_OK


def test_unreadable_frequency_before_on_spends_nothing_but_off(tmp_path):
    mac = FakeMac(frequency_raises=lambda m: m.frequency_reads == 1)
    record, code, _ = run(mac, tmp_path)
    assert mac.commands() == ["off"]
    assert record["result"] == g10.RESULT_UNMEASURED
    assert record["flag_code"] == "g10.unmeasured"
    assert record["verdict"]["reasons"] == [g10.REASON_NO_FREQUENCY]
    assert code == g10.EXIT_OK


def test_wide_anchor_read_skew_before_on_is_unmeasured(tmp_path):
    mac = FakeMac(skew_ns=1_500_000)
    record, _, _ = run(mac, tmp_path)
    assert mac.commands() == ["off"]
    assert record["verdict"]["verdict"] == g10.UNMEASURED
    assert record["verdict"]["reasons"] == [g10.REASON_SKEW]
    assert record["result"] == g10.RESULT_UNMEASURED


# --------------------------------------------------------------------------
# OFF always runs


def test_off_runs_on_exception(tmp_path):
    def boom(mac, _seconds):
        if mac.since_on() is not None and mac.since_on() >= 2:
            raise RuntimeError("anchor reader exploded")

    mac = FakeMac(steps=False, sleep_hook=boom)
    record, code, out = run(mac, tmp_path)
    assert mac.commands() == ["on", "off"]
    assert mac.network_on is False
    assert code == g10.EXIT_ERROR
    assert record["result"] == g10.ERROR
    assert record["error"]["phase"] == "poll"
    assert "anchor reader exploded" in record["error"]["repr"]
    assert out.exists()


@pytest.mark.parametrize("signum", [signal.SIGTERM, signal.SIGHUP])
def test_off_runs_under_signal_during_poll(tmp_path, signum):
    sent = []

    def deliver(mac, _seconds):
        if not sent and mac.since_on() is not None and mac.since_on() >= 2:
            sent.append(signum)
            os.kill(os.getpid(), signum)

    mac = FakeMac(steps=False, sleep_hook=deliver)
    record, code, out = run(mac, tmp_path)
    assert sent == [signum]
    assert mac.commands() == ["on", "off"]
    assert mac.network_on is False
    assert code == 128 + signum
    assert record["interrupted"] == {"signum": int(signum),
                                     "signal": signal.Signals(signum).name, "phase": "poll"}
    assert record["result"] == g10.INTERRUPTED
    assert record["flag_code"] == "g10.interrupted"
    assert json.loads(out.read_text())["off_ok"] is True


def test_signal_during_settling_keeps_the_verdict(tmp_path):
    sent = []

    def deliver(mac, _seconds):
        if not sent and mac.since_on() is not None and mac.since_on() >= 100:
            sent.append(1)
            os.kill(os.getpid(), signal.SIGHUP)

    mac = FakeMac(sleep_hook=deliver)
    record, code, _ = run(mac, tmp_path)
    assert record["result"] == g10.DISCHARGED
    assert record["interrupted"]["phase"] == "settle"
    assert record["settling"]["stop_reason"] == "interrupted"
    assert mac.commands() == ["on", "off"]
    assert code == 128 + signal.SIGHUP


def test_signal_arriving_during_off_is_deferred_and_off_completes(tmp_path):
    def hook(mac, argv):
        if argv == g10.OFF_ARGV:
            os.kill(os.getpid(), signal.SIGTERM)

    mac = FakeMac(run_hook=hook)
    record, code, _ = run(mac, tmp_path)
    assert record["off_ok"] is True
    assert record["deferred_signals"] == ["SIGTERM"]
    assert record["interrupted"] is None
    assert record["f1"] is not None
    assert code == g10.EXIT_OK


def test_signals_during_on_and_before_the_body_still_run_off(tmp_path):
    def hook(mac, argv):
        if argv == g10.ON_ARGV:
            os.kill(os.getpid(), signal.SIGTERM)

    mac = FakeMac(run_hook=hook)
    record, code, _ = run(mac, tmp_path)
    assert mac.commands() == ["on", "off"]
    assert record["interrupted"]["phase"] == "on"
    assert record["commands"][0]["finished"]["monotonic_raw_ns"] is not None
    assert code == 128 + signal.SIGTERM

    mac2 = FakeMac()
    env = mac2.env()

    def boot():
        os.kill(os.getpid(), signal.SIGHUP)
        return "never"

    env.boot_session_uuid = boot
    out = tmp_path / "early" / "g10.json"
    out.parent.mkdir()
    record2, code2 = g10.run_control(g10.Params(), env, out, ["x"])
    assert mac2.commands() == ["off"]
    assert record2["interrupted"]["signal"] == "SIGHUP"
    assert record2["result"] == g10.INTERRUPTED
    assert code2 == 128 + signal.SIGHUP


def test_repeated_signals_raise_once_and_the_rest_are_deferred(tmp_path):
    sent = []

    def deliver(mac, _seconds):
        if not sent and mac.since_on() is not None and mac.since_on() >= 2:
            sent.append(1)
            os.kill(os.getpid(), signal.SIGTERM)

    def hook(mac, argv):
        if argv == g10.OFF_ARGV:
            os.kill(os.getpid(), signal.SIGHUP)
            os.kill(os.getpid(), signal.SIGTERM)

    mac = FakeMac(steps=False, sleep_hook=deliver, run_hook=hook)
    record, code, _ = run(mac, tmp_path)
    assert record["interrupted"]["signal"] == "SIGTERM"
    assert record["deferred_signals"] == ["SIGHUP", "SIGTERM"]
    assert record["off_ok"] is True and mac.network_on is False
    assert code == 128 + signal.SIGTERM


def test_keyboard_interrupt_still_runs_off(tmp_path):
    def hook(mac, _seconds):
        if mac.since_on() is not None and mac.since_on() >= 1:
            raise KeyboardInterrupt

    mac = FakeMac(sleep_hook=hook)
    record, code, _ = run(mac, tmp_path)
    assert mac.commands() == ["on", "off"]
    assert record["error"]["phase"] == "poll"
    assert code == g10.EXIT_ERROR


def test_failed_off_is_retried_and_reported(tmp_path):
    fail = {"returncode": 1, "stdout": "", "stderr": "sudo: a password is required\n"}
    mac = FakeMac(off_results=[fail, subprocess.TimeoutExpired(g10.OFF_ARGV, 60), fail])
    record, code, out = run(mac, tmp_path)
    offs = [c for c in record["commands"] if c["name"] == "off"]
    assert [c["attempt"] for c in offs] == [1, 2, 3]
    assert offs[1]["timed_out"] is True
    assert record["off_ok"] is False
    assert code == g10.EXIT_OFF_FAILED
    assert out.exists()
    assert record["result"] == g10.DISCHARGED


def test_off_succeeding_on_retry_is_ok(tmp_path):
    mac = FakeMac(off_results=[{"returncode": 1, "stdout": "", "stderr": "x"}])
    record, code, _ = run(mac, tmp_path)
    assert [c["name"] for c in record["commands"]] == ["on", "off", "off"]
    assert record["off_ok"] is True
    assert code == g10.EXIT_OK


# --------------------------------------------------------------------------
# Frequency settling


def test_off_when_frequency_reaches_target(tmp_path):
    mac = FakeMac(f_after_on=lambda since: WORD_TODAY if since < 170 else -190_054)
    record, _, _ = run(mac, tmp_path)
    settling = record["settling"]
    assert settling["stop_reason"] == "target"
    assert [r["elapsed_since_on_s"] for r in settling["reads"]] == [60.0, 120.0, 180.0]
    off_call = [c for c in mac.calls if c["argv"] == g10.OFF_ARGV][0]
    assert off_call["since_on"] == pytest.approx(180.0)
    assert record["next_arm_frequency_gate"]["passes"] is True


def test_off_at_fifteen_minutes_when_frequency_stays_high(tmp_path):
    mac = FakeMac()
    record, _, _ = run(mac, tmp_path)
    settling = record["settling"]
    assert settling["stop_reason"] == "timeout"
    assert [r["elapsed_since_on_s"] for r in settling["reads"]] == [
        60.0 * k for k in range(1, 16)]
    off_call = [c for c in mac.calls if c["argv"] == g10.OFF_ARGV][0]
    assert off_call["since_on"] == pytest.approx(900.0)
    # -3.17 ppm still passes the next arm's gate (4.846 ms <= 5 ms).
    gate = record["next_arm_frequency_gate"]
    assert gate["passes"] is True and gate["bound_ms"] == pytest.approx(4.8457, abs=1e-3)


def test_settling_cap_is_honoured_off_the_minute_grid(tmp_path):
    mac = FakeMac()
    record, _, _ = run(mac, tmp_path, settle_max_s=150.0)
    assert [r["elapsed_since_on_s"] for r in record["settling"]["reads"]] == [60.0, 120.0, 150.0]
    off_call = [c for c in mac.calls if c["argv"] == g10.OFF_ARGV][0]
    assert off_call["since_on"] == pytest.approx(150.0)


def test_signal_guard_raises_once_then_defers():
    guard = g10.SignalGuard()
    guard.install()
    try:
        with pytest.raises(g10.Interrupted):
            os.kill(os.getpid(), signal.SIGTERM)
            time.monotonic()  # a bytecode boundary for the handler to run at
        os.kill(os.getpid(), signal.SIGHUP)
        os.kill(os.getpid(), signal.SIGTERM)
        time.monotonic()
        assert guard.received == [signal.SIGTERM, signal.SIGHUP, signal.SIGTERM]
        assert guard.deferred == [signal.SIGHUP, signal.SIGTERM]
    finally:
        guard.restore()


def test_frequency_target_is_inclusive_and_exact():
    bound = 3 * kernel_clock.FREQUENCY_SCALE
    assert g10.frequency_within(probe(bound), 3.0)
    assert g10.frequency_within(probe(-bound), 3.0)
    assert not g10.frequency_within(probe(bound + 1), 3.0)
    assert not g10.frequency_within(probe(-bound - 1), 3.0)


def test_word_just_above_target_runs_to_timeout(tmp_path):
    mac = FakeMac(f_after_on=lambda since: -(3 * kernel_clock.FREQUENCY_SCALE + 1))
    record, _, _ = run(mac, tmp_path)
    assert record["settling"]["stop_reason"] == "timeout"
    mac2 = FakeMac(f_after_on=lambda since: -(3 * kernel_clock.FREQUENCY_SCALE))
    sub = tmp_path / "b"
    sub.mkdir()
    record2, _, _ = run(mac2, sub)
    assert record2["settling"]["stop_reason"] == "target"
    assert len(record2["settling"]["reads"]) == 1


def test_high_frequency_after_off_is_reported_for_the_next_arm(tmp_path):
    mac = FakeMac(f_after_on=lambda since: 239_862)  # 3.66 ppm > 3.63 ppm allowed
    record, code, _ = run(mac, tmp_path)
    assert record["next_arm_frequency_gate"]["passes"] is False
    assert code == g10.EXIT_OK  # a diagnostic, never a stop


def test_unreadable_frequency_during_settling_is_recorded_and_times_out(tmp_path):
    mac = FakeMac(frequency_raises=lambda m: m.frequency_reads > 2 and m.network_on)
    record, code, _ = run(mac, tmp_path)
    reads = record["settling"]["reads"]
    assert reads and all(r["probe"] is None and "OSError" in r["error"] for r in reads)
    assert record["settling"]["stop_reason"] == "timeout"
    assert mac.commands() == ["on", "off"]
    assert code == g10.EXIT_OK


# --------------------------------------------------------------------------
# The pair verdict


def _pair(span_s, word, step_ns=0, skew_ns=1000):
    before = {"realtime_ns": 10**18, "monotonic_raw_ns": 10**12, "read_skew_ns": skew_ns}
    drift = Fraction(word * span_s * NS, kernel_clock.FREQUENCY_SCALE * 10**6)
    after = {"realtime_ns": 10**18 + span_s * NS + int(round(drift)) + step_ns,
             "monotonic_raw_ns": 10**12 + span_s * NS, "read_skew_ns": skew_ns}
    return before, after


def test_pair_verdict_residual_form():
    params = g10.Params()
    before, after = _pair(1600, WORD_TODAY)
    verdict = g10.evaluate_pair(before, after, probe(WORD_TODAY), probe(WORD_TODAY), params)
    assert verdict["verdict"] == g10.PASS and verdict["residual_ns"] <= 1
    before, after = _pair(1600, WORD_TODAY, step_ns=6_000_000)
    verdict = g10.evaluate_pair(before, after, probe(WORD_TODAY), probe(WORD_TODAY), params)
    assert verdict["verdict"] == g10.REFUSE and verdict["reasons"] == [g10.REASON_RESIDUAL]
    assert g10.result_from_verdict(verdict) == g10.DISCHARGED
    # Exactly 1 ms is inside the limit; 1 ms + 1 ns is not.
    before, after = _pair(10, 0, step_ns=1_000_000)
    assert g10.evaluate_pair(before, after, probe(0), probe(0), params)["verdict"] == g10.PASS
    before, after = _pair(10, 0, step_ns=1_000_001)
    assert g10.evaluate_pair(before, after, probe(0), probe(0), params)["verdict"] == g10.REFUSE


def test_pair_verdict_unmeasured_cases():
    params = g10.Params()
    before, after = _pair(10, 0, skew_ns=1_000_001)
    assert g10.evaluate_pair(before, after, probe(0), probe(0), params)["verdict"] == \
        g10.UNMEASURED
    before, after = _pair(10, 0)
    assert g10.evaluate_pair(before, None, probe(0), probe(0), params)["reasons"] == \
        [g10.REASON_NO_ANCHOR]
    assert g10.evaluate_pair(before, after, probe(0), None, params)["reasons"] == \
        [g10.REASON_NO_FREQUENCY]
    assert g10.result_from_verdict({"verdict": g10.UNMEASURED}) == g10.RESULT_UNMEASURED


def test_injected_evaluator_is_used(tmp_path):
    seen = []

    def evaluate(before, after, f_before, f_after, params):
        seen.append((before, after))
        return {"evaluator": "hazards.clock", "verdict": g10.REFUSE,
                "reasons": [g10.REASON_RESIDUAL]}

    mac = FakeMac(steps=False)
    out = tmp_path / "g10.json"
    record, code = g10.run_control(g10.Params(), mac.env(), out, ["x"], evaluate=evaluate)
    assert len(seen) == 1 and record["verdict"]["evaluator"] == "hazards.clock"
    assert record["result"] == g10.DISCHARGED and code == g10.EXIT_OK


# --------------------------------------------------------------------------
# Create-once and CLI


def test_existing_record_runs_nothing(tmp_path):
    out = tmp_path / "g10.json"
    out.write_bytes(b"{}\n")
    mac = FakeMac()
    record, code = g10.run_control(g10.Params(), mac.env(), out, ["x"])
    assert record is None and code == g10.EXIT_EXISTS
    assert mac.calls == [] and out.read_bytes() == b"{}\n"
    dangling = tmp_path / "other"
    dangling.mkdir()
    (dangling / "g10.json").symlink_to(dangling / "missing")
    assert g10.run_control(g10.Params(), mac.env(), dangling / "g10.json", ["x"])[1] == \
        g10.EXIT_EXISTS
    assert mac.calls == []


def test_missing_night_dir_is_a_usage_error(tmp_path):
    mac = FakeMac()
    _, code = g10.run_control(g10.Params(), mac.env(), tmp_path / "nope" / "g10.json", ["x"])
    assert code == g10.EXIT_USAGE and mac.calls == []


def test_record_written_after_a_racing_writer_reports_write_failure(tmp_path, capsys):
    out = tmp_path / "g10.json"

    def hook(mac, argv):
        if argv == g10.OFF_ARGV:
            out.write_text("{}")

    mac = FakeMac(run_hook=hook)
    record, code = g10.run_control(g10.Params(), mac.env(), out, ["x"])
    assert code == g10.EXIT_WRITE_FAILED
    assert out.read_text() == "{}"
    assert json.loads(capsys.readouterr().err.split("\n", 1)[1]) == record


def test_main_uses_the_fixed_argv_and_writes_the_night_record(tmp_path, capsys):
    mac = FakeMac()
    code = g10.main(["--night-dir", str(tmp_path), "--t-stream-max-s", "335"], env=mac.env())
    assert code == g10.EXIT_OK
    record = json.loads((tmp_path / "g10.json").read_text())
    assert record["argv"][1:] == ["--night-dir", str(tmp_path), "--t-stream-max-s", "335"]
    assert record["parameters"]["t_stream_max_s"] == 335.0
    assert "DISCHARGED" in capsys.readouterr().out


def test_main_rejects_bad_arguments(tmp_path):
    mac = FakeMac()
    assert g10.main([], env=mac.env()) == g10.EXIT_USAGE
    assert g10.main(["--night-dir", str(tmp_path), "--settle-max-s", "0"],
                    env=mac.env()) == g10.EXIT_USAGE
    assert mac.calls == []


def test_network_time_argv_matches_the_sudoers_slice():
    assert g10.ON_ARGV == ("/usr/bin/sudo", "-n", "/usr/sbin/systemsetup",
                           "-setusingnetworktime", "on")
    assert g10.OFF_ARGV == network_time_off.OFF_ARGV
    env = g10.Env()
    assert env.run is g10.real_run and env.read_frequency is g10.real_read_frequency


def test_script_help_and_import_stay_off_the_retired_path():
    help_result = _REAL_SUBPROCESS_RUN([sys.executable, "-B", str(SCRIPT), "--help"],
                                       capture_output=True, text=True, timeout=60,
                                       cwd=str(REPO_ROOT))
    assert help_result.returncode == 0 and "--night-dir" in help_result.stdout
    probe_code = (
        "import importlib.util, sys\n"
        f"spec = importlib.util.spec_from_file_location('g10', {str(SCRIPT)!r})\n"
        "mod = importlib.util.module_from_spec(spec); sys.modules['g10'] = mod\n"
        "spec.loader.exec_module(mod)\n"
        "bad = [m for m in sys.modules if m.startswith(('joulewise.arm_readiness',"
        " 'joulewise.t0_rehearsal', 'joulewise.v5_qualification', 'joulewise.flags',"
        " 'scripts.capture_t0_step', 'scripts.launch_window'))]\n"
        "print(bad)\n")
    result = _REAL_SUBPROCESS_RUN([sys.executable, "-B", "-c", probe_code], capture_output=True,
                                  text=True, timeout=60, cwd=str(REPO_ROOT))
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[]"


@pytest.mark.skipif(sys.platform != "darwin", reason="reads the macOS kernel clock")
def test_real_readers_are_read_only_probes():
    # ntp_adjtime(modes=0) and clock_gettime only; nothing changes machine state.
    frequency = g10.real_read_frequency()
    assert frequency["modes"] == 0
    anchor = g10.real_read_anchor()
    assert set(anchor) == {"realtime_ns", "monotonic_raw_ns", "read_skew_ns"}
