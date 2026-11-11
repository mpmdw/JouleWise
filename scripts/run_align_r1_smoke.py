#!/usr/bin/env python3
"""One agent-free R1 follow-up smoke: feeds, display dwell, A then B, cleanup.

Launch ONLY through launch_align_r0.py launch --runner-kind r1-smoke. This
runner neither arms a night nor changes the kit or condition-13 sources.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
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
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.align.apple import powermode, v4_registration as reg
from joulewise.b5 import driver
from scripts import align_r1_rehearsal as r1, launch_align_r0 as launcher, run_night as night

PART_LIMIT_S = 1800
# The parent reserves another 190 s for emergency teardown before the fence
# expires. Work stops 180 s earlier still: part-group proof (70 s), meter
# proof (up to 90 s), and bounded Automatic setter/readback (20 s).
WORK_RESERVE_S = 2 * launcher.R1_CLEANUP_GRACE_S + 10
SIGNALS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)


def stamp():
    return {"epoch_s": time.time(), "monotonic_ns": time.monotonic_ns()}


@contextmanager
def register_child_before_interrupt():
    """Defer an arriving signal until Popen's owned handle is registered.

    Do not block the signal mask: an exec'd meter must inherit normal signal
    delivery. Exec resets these temporary Python handlers in the child.
    """
    pending = []
    handlers = {s: signal.signal(s, lambda number, _frame: pending.append(number)) for s in SIGNALS}
    try:
        yield
    finally:
        for s, handler in handlers.items():
            signal.signal(s, handler)
        if pending:
            handler = handlers[pending[0]]
            if callable(handler):
                handler(pending[0], None)
            elif handler == signal.SIG_DFL:
                signal.raise_signal(pending[0])


def host_run(argv):
    return subprocess.run(argv, capture_output=True, text=True, timeout=15,
                          env={**os.environ, "LC_ALL": "C"})


def ac_power():
    result = host_run(["/usr/bin/pmset", "-g", "batt"])
    if result.returncode or "Now drawing from 'AC Power'" not in result.stdout.splitlines():
        raise ValueError("R1 smoke requires AC power")
    return {"rc": result.returncode, "stdout": result.stdout}


def night_agents():
    result = host_run(["/bin/launchctl", "list"])
    if result.returncode or re.search(r"(?:^|\s)com\.joulewise\.night\S*", result.stdout):
        raise ValueError("loaded night agent or unreadable launchctl list")
    return {"rc": result.returncode, "stdout": result.stdout}


def condition13():
    result = host_run(["git", "-C", str(ROOT), "rev-parse", "HEAD"])
    commit = reg.verify_r1_executed_sources(ROOT, {"executed_commit": result.stdout.strip()})
    return {"rc": result.returncode, "executed_commit": commit}


def read_power():
    value = powermode.observe_ac_powermode(host_run)
    if value != 0:
        raise ValueError(f"R1 smoke requires observed Automatic (AC powermode 0); got {value}")
    return {"rc": 0, "ac_powermode": value, "automatic": True}


def restore_power():
    # Same host exclusion as the ordinary procedure: never set a mode under
    # another measuring night's lock, even on an early preflight refusal.
    lock = powermode.HostLock(role="r1-smoke-close")
    try:
        if not lock.acquire():
            raise ValueError("Automatic restore blocked by another host night lock")
        result = powermode.restore_automatic()
        return {**result, "rc": 0 if result["ok"] else 2}
    finally:
        lock.release()


class CensusFeed:
    """Cooperative journal producer; no extra thread or child to strand.

    Start takes the first sample, poll follows the night's 30 s census grid,
    and stop is idempotent. Mark active before sampling so partial starts
    remain inside the runner's cleanup boundary.
    """
    interval = night.CENSUS_INTERVAL_S

    def __init__(self, output):
        self.output = Path(output)
        self.active = False
        self.started = False
        self.closed = False
        self.next_sample = 0

    def start(self):
        if not self.started and not self.closed:
            self.started = self.active = True
            self.poll()
        return {"rc": 0}

    def poll(self):
        if self.active and time.monotonic() >= self.next_sample:
            self.sample()
            self.next_sample = time.monotonic() + self.interval

    def stop(self):
        self.active = False
        self.closed = True
        return {"rc": 0, "proven_stopped": True}

    def files(self):
        return [self.path]


class AgentFeed(CensusFeed):
    name = "agents"

    def __init__(self, output):
        super().__init__(output)
        self.path = self.output / "censuses.jsonl"

    def sample(self):
        def probe(argv):
            result = host_run(argv)
            return night.ProbeResult(tuple(argv), result.returncode, result.stdout, result.stderr, time.monotonic_ns())
        probes = SimpleNamespace(run=probe, monotonic_ns=time.monotonic_ns)
        observed, refusal = night.agent_census(probes, own_tree_root=os.getpid())
        night._append_census(self.path, observed, refusal)
        if refusal is not None:
            raise ValueError(f"agent census refused: {refusal}")


class VolumeFeed(CensusFeed):
    name = "volumes"
    interval = 60

    def __init__(self, output):
        super().__init__(output)
        self.path = self.output / "volume_censuses.jsonl"
        self.watch = r1.VolumeWatch(runner=host_run)

    def sample(self):
        verdict = self.watch.census("r1-smoke")
        with self.path.open("a") as handle:
            handle.write(json.dumps({**stamp(), **self.watch.records[-1]}, sort_keys=True) + "\n")
        # The journal lives on disk rather than retaining an unbounded list.
        self.watch.records.clear()
        if verdict["verdict"] != "PASS":
            raise ValueError(f"volume census refused: {verdict}")


class MeterFeed:
    name = "meter"

    def __init__(self, output):
        self.output = Path(output)
        self.supervisor = None
        self.stopped = False
        self.stop_record = None

    def start(self):
        if self.stopped:
            return self.stop_record
        if self.supervisor is None:
            seams = driver.production_seams(ROOT)
            request = driver.MonitorRequest(None, None, self.output, self.output, os.getpid())
            # Same plain-QoS KM003C argv, create-once streams and supervisor
            # used by HAZARD_PACK. Never use a different channel/parser.
            self.supervisor = driver.MonitorSupervisor(
                lambda: seams.meter_argv(request), night_dir=self.output, popen=subprocess.Popen,
                group_census=night._group_census, name=driver.METER_NAME)
            with register_child_before_interrupt():
                started = self.supervisor.start()
            if not started:
                raise ValueError("KM003C supervisor could not start")
            with register_child_before_interrupt():
                readiness = driver.await_meter_ready(self.supervisor, driver.MeterLiveness(
                    self.output.joinpath(*driver.METER_STREAM_DIR)))
            if not readiness["ready"]:
                raise ValueError(f"KM003C has no fresh DC-in sample batch: {readiness}")
        return {"rc": 0}

    def poll(self):
        if self.supervisor is not None and not self.stopped:
            with register_child_before_interrupt():
                self.supervisor.poll()

    def stop(self):
        if self.stopped:
            return self.stop_record
        self.stopped = True
        self.stop_record = {"rc": 0, "proven_stopped": True}
        if self.supervisor is not None:
            try:
                self.stop_record["supervisor"] = self.supervisor.stop()
            finally:
                # Supervisor.stop's already-exited-leader path doesn't census
                # descendants. The night's group teardown covers that too.
                process = self.supervisor.process
                if process is not None:
                    evidence = {}
                    proven = night._terminate_process_group(process, evidence=evidence)
                    self.stop_record.update(proven_stopped=proven, rc=0 if proven else 2, group=evidence)
        return self.stop_record

    def files(self):
        return [self.output / driver.METER_JOURNAL, self.output / "meter.stdout.log",
                self.output / "meter.stderr.log", *sorted(self.output.joinpath(*driver.METER_STREAM_DIR).glob("stream-*.jsonl"))]


def poll_feeds(feeds):
    for feed in feeds:
        feed.poll()


def work_remaining(args):
    remaining = args.deadline - WORK_RESERVE_S - time.time()
    if remaining <= 0:
        raise TimeoutError("R1 smoke work deadline reached; cleanup reserve retained")
    return remaining


def display():
    record = launcher.sleep_display("/usr/bin/pmset")
    return {"rc": record["exit_code"] if record["exit_code"] is not None else 2, **record}


def dwell(args, feeds):
    seconds = launcher.display_dwell_seconds()
    until = time.monotonic() + seconds
    while time.monotonic() < until:
        work_remaining(args)
        poll_feeds(feeds)
        time.sleep(min(.25, max(0, until - time.monotonic())))
    return {"rc": 0, "dwell_s": seconds, "dwell_constant_s": launcher.DISPLAY_SLEEP_DWELL_S}


def part_argv(args, which):
    return [sys.executable, "-B", str(ROOT / "scripts/align_r1_followup_kit.py"), "smoke", "--part", which,
            "--output", str(args.output / ("part-" + which.lower())), "--soak-reference", str(args.soak_reference)]


class PartDeadline(night._WindowDeadline):
    """Reuse the night's independent deadline enforcer with a smoke receipt.

    This is not a night plan. Only the terminal writer differs; the lock,
    monotonic watchdog, cancellation and process-group teardown are shared.
    """
    def fire(self):
        with self._lock:
            if self.outcome is not None or self._cancelled:
                return self.outcome
            proof = {}
            proven = night._terminate_process_group(self.process, evidence=proof)
            self.outcome = {"proven": proven, "fired": stamp(), **proof}
            night._write_json(self.night_dir / "deadline.json", self.outcome)
            return self.outcome


def part(args, which, feeds, *, on_start=lambda: None):
    argv = part_argv(args, which)
    until = time.monotonic() + min(PART_LIMIT_S, work_remaining(args))
    child = None
    deadline = None
    proof = {}
    try:
        with (args.output / f"part-{which.lower()}.stdout.log").open("ab") as out, \
             (args.output / f"part-{which.lower()}.stderr.log").open("ab") as err:
            with register_child_before_interrupt():
                child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                         start_new_session=True, close_fds=True)
                on_start()
                deadline_dir = args.output / "deadlines" / ("part-" + which.lower())
                deadline_dir.mkdir(parents=True)
                deadline = PartDeadline(child, pgid=child.pid, night_dir=deadline_dir, plan=None,
                    deadline_epoch_s=time.time() + max(0, until - time.monotonic()), deadline_monotonic=until)
                deadline.start()
            while child.poll() is None:
                work_remaining(args)
                if time.monotonic() >= until:
                    raise TimeoutError(f"Part {which} exceeded its single {PART_LIMIT_S} s budget")
                poll_feeds(feeds)
                time.sleep(.1)
            if deadline.expired() or deadline.cancel() is not None:
                raise TimeoutError(f"Part {which} exceeded its single {PART_LIMIT_S} s budget")
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
            finally:
                for s, handler in handlers.items():
                    signal.signal(s, handler)
            if not proven:
                raise RuntimeError(f"Part {which} process group not proven stopped: {proof}")
    return {"rc": code, "argv": argv, "group": proof, "proven_stopped": True}


class StepFailed(RuntimeError):
    def __init__(self, code):
        self.code = code


def run(args, *, feeds=None):
    # Create-once: a retry cannot overwrite even a refused/partial smoke.
    args.output.mkdir(parents=True, exist_ok=False)
    feeds = feeds if feeds is not None else [MeterFeed(args.output), AgentFeed(args.output), VolumeFeed(args.output)]
    record = {"schema": "joulewise.align.r1_smoke_runner.v1", "started": stamp(),
              "deadline": args.deadline, "work_reserve_s": WORK_RESERVE_S,
              "soak_reference": str(args.soak_reference), "parts": {"A": False, "B": False},
              "steps": [], "feeds": {}, "rc": 0}

    def step(name, operation, *, fatal=True):
        row = {"name": name, "started": stamp(), "rc": None}
        record["steps"].append(row)
        try:
            result = operation() or {}
            row.update(rc=result.get("rc", 0), result=result)
            if fatal and row["rc"]:
                raise StepFailed(row["rc"])
            return result
        except BaseException as exc:
            row.update(rc=exc.code if isinstance(exc, (StepFailed, SystemExit)) and isinstance(exc.code, int) else 2,
                       error=f"{type(exc).__name__}: {exc}")
            raise
        finally:
            row["ended"] = stamp()

    def interrupted(signum, _frame):
        raise SystemExit(128 + signum)

    handlers = {s: signal.signal(s, interrupted) for s in SIGNALS}
    try:
        step("deadline", lambda: {"remaining_s": work_remaining(args)})
        step("ac_power", ac_power)
        step("night_agents", night_agents)
        step("condition13", condition13)
        def soak():
            if not args.soak_reference.is_file():
                raise ValueError("soak reference file is missing")
            return {"rc": 0, "path": str(args.soak_reference)}
        step("soak_reference", soak)
        for feed in feeds:
            step("start-" + feed.name, feed.start)
        step("read_power", read_power)
        # Match R0: a failed display sleep is recorded, not a refusal.
        step("display", display, fatal=False)
        step("dwell", lambda: dwell(args, feeds))
        for which in ("A", "B"):
            def run_part():
                result = part(args, which, feeds, on_start=lambda: record["parts"].__setitem__(which, True))
                record["parts"][which] = True
                return result
            step("part-" + which, run_part)
    except BaseException as exc:
        record.update(rc=exc.code if isinstance(exc, (StepFailed, SystemExit)) and isinstance(exc.code, int) else 2,
                      error=f"{type(exc).__name__}: {exc}")
    finally:
        for s in SIGNALS:
            signal.signal(s, signal.SIG_IGN)
        try:
            cleanup = [("restore", restore_power), *(("stop-" + f.name, f.stop) for f in reversed(feeds))]
            for name, operation in cleanup:
                try:
                    result = step(name, operation)
                    if name.startswith("stop-"):
                        record["feeds"].setdefault(name[5:], {})["stop"] = result
                except BaseException:
                    record["rc"] = record["rc"] or 2
            for feed in feeds:
                files = []
                try:
                    for path in feed.files():
                        if path.is_file():
                            with path.open("rb") as handle:
                                digest = hashlib.file_digest(handle, "sha256").hexdigest()
                            files.append({"path": path.relative_to(args.output).as_posix(), "sha256": digest})
                except Exception as exc:
                    record["rc"] = record["rc"] or 2
                    record["feeds"].setdefault(feed.name, {})["error"] = str(exc)
                record["feeds"].setdefault(feed.name, {})["files"] = files
            record["ended"] = stamp()
            with (args.output / "runner_receipt.json").open("x") as handle:
                json.dump(record, handle, indent=2, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
        finally:
            for s, handler in handlers.items():
                signal.signal(s, handler)
    return record["rc"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--soak-reference", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args(argv)
    if not math.isfinite(args.deadline):
        parser.error("deadline must be finite")
    args.output = args.output.resolve()
    args.soak_reference = args.soak_reference.resolve()
    return run(args)


if __name__ == "__main__":
    powermode.mark_production_entry(__file__)
    raise SystemExit(main())
