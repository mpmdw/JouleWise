"""Disposable committed historical ledger and a real blocked artifact reader."""
from contextlib import contextmanager
import errno
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time

from joulewise import calibration_ledger as ledger
from tests import test_calibration_exits as exits
from tests import test_calibration_ledger as ledger_tests


TEST_WATCHDOG_S = 30.0

# Only the disposable CLI and its worker use this clock. The test
# runner's subprocess watchdog and the worker cleanup waits still use real time.
_CLOCK_HOOK = '''import os, selectors, sys, time
from pathlib import Path
from types import SimpleNamespace

_clock = Path(os.environ["JW_CUSTODY_TEST_CLOCK"])

def _now():
    return sum(map(float, _clock.read_text().splitlines()))

def _advance(seconds):
    with _clock.open("a") as stream:
        stream.write(f"{seconds}\\n")

if sys.argv[0] == "-m":
    time.monotonic = _now
elif Path(sys.argv[0]).name in (
    "reserve_calibration_window_bracket.py", "recover_calibration_ledger.py",
):
    from joulewise import calibration_ledger as ledger
    ledger.time = SimpleNamespace(monotonic=_now, time=time.time)

    class PollingSelector(selectors.DefaultSelector):
        def select(self, timeout=None):
            # A FIFO event can advance the clock without waking the selector.
            return super().select(min(timeout, 0.02) if timeout is not None else 0.02)

    ledger.selectors = SimpleNamespace(DefaultSelector=PollingSelector,
                                       EVENT_READ=selectors.EVENT_READ,
                                       EVENT_WRITE=selectors.EVENT_WRITE)
    if "JW_CUSTODY_EXPIRE_ON_CHECK" in os.environ:
        _check = ledger.CustodyDeadline.check
        def _expire_on_check(deadline):
            _advance(deadline.budget_s + 0.03)
            _check(deadline)
        ledger.CustodyDeadline.check = _expire_on_check
'''


class CustodyFixture:
    def __init__(self, *, control_clock=False):
        self.control_clock = control_clock

    def __enter__(self):
        self.witness = exits.PublicGovernedExitWitnessTests(methodName="runTest")
        self.witness.setUp()
        w = self.witness
        self.repo, self.ledger, self.pin = w.repo, w.ledger, w.pin
        builder = ledger_tests.CalibrationLedgerTests(methodName="runTest")
        builder.root = self.repo / "historical-fixture"
        builder.epoch, builder.t1 = w.epoch, w.t1
        checkout, root, self.custodies, table = builder._historical_fixture()
        plan = ledger.bootstrap_historical_import(
            self.ledger, head_pin_path=self.pin, roots=[root], checkout_root=checkout,
            **builder._historical_import_args(table, self.custodies),
            execute=True, require_committed_pin=False,
        )
        self.pin.write_text(json.dumps(dict(plan.head_pin)) + "\n")
        w._commit_fixture("committed finalized historical custody fixture")
        snapshot = ledger.load_calibration_ledger_snapshot(
            self.ledger, self.pin, repo_root=self.repo)
        assert snapshot.valid and len(snapshot.observations) == 3
        assert all(item.is_historical_import for item in snapshot.observations)
        self.state = w._state_reservation_inputs()
        self.process_group = None
        self.refusal = self.repo / "calibration-refusal.json"
        self.env = exits._fresh_cli_env() | {
            "JOULEWISE_CALIBRATION_REFUSAL_PATH": str(self.refusal),
            "JOULEWISE_NIGHT_PLAN_ID": "custody-hang-plan",
        }
        self.clock = self.repo / "custody-clock" if self.control_clock else None
        if self.clock is not None:
            (self.repo / "sitecustomize.py").write_text(_CLOCK_HOOK)
            self.env.update(PYTHONPATH=str(self.repo), JW_CUSTODY_TEST_CLOCK=str(self.clock))
        return self

    def __exit__(self, *_args):
        self.witness.tearDown()
        self.witness.doCleanups()

    def bytes(self):
        return self.ledger.read_bytes(), self.pin.read_bytes()

    def reservation(self, *, mode="--execute", budget=3.0, env=None, extra=()):
        args = self.witness._reservation_args(self.state)
        args += [mode, *extra]
        # The same blocked-read test runs against the base implementation:
        # omission there reaches the actual defect, not an unknown-flag error.
        if "--custody-budget-s" in self.witness.reserve_script.read_text():
            args += ["--custody-budget-s", str(budget)]
        return self.run([sys.executable, str(self.witness.reserve_script), *args],
                        budget=budget, env=env)

    def advance_on_read(self, seconds):
        with self.clock.open("a") as stream:
            stream.write(f"{self.budget if seconds is None else seconds}\n")

    def run(self, command, *, budget=3.0, env=None):
        env = env or self.env
        watchdog = budget + 2.0
        if self.clock is not None:
            self.budget = budget
            self.clock.write_text("")
            env = dict(env, JW_CUSTODY_TEST_BUDGET=str(budget))
            watchdog = TEST_WATCHDOG_S
        started = time.monotonic()
        process = subprocess.Popen(command, cwd=self.repo, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, start_new_session=True)
        # start_new_session makes this process the leader of a brand-new
        # process group whose identifier equals its own process identifier.
        # Every custody worker it spawns inherits that group, so the group is
        # the exact set of processes this run is responsible for reaping.
        self.process_group = process.pid
        try:
            stdout, stderr = process.communicate(timeout=watchdog)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate(timeout=2)
            raise AssertionError(
                f"custody CLI exceeded the {watchdog:.1f}s watchdog (budget {budget:g}s); "
                f"CLI remained blocked in the governed artifact read; stderr={stderr[-500:]}"
            )
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=2)
        elapsed = (time.monotonic() - started if self.clock is None
                   else sum(map(float, self.clock.read_text().splitlines())))
        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr), elapsed

    def assert_lease_reacquirable(self):
        completed = subprocess.run([
            sys.executable, "-B", "-c",
            "from pathlib import Path; from joulewise.calibration_ledger import CalibrationWriterLease; "
            f"lease=CalibrationWriterLease(Path({str(self.ledger)!r})); "
            "lease.acquire(); lease.release(); print('reacquired')",
        ], cwd=self.repo, env=self.env, text=True, capture_output=True,
            timeout=TEST_WATCHDOG_S if self.control_clock else 2)
        assert completed.returncode == 0, completed.stderr
        assert completed.stdout.strip() == "reacquired"

    def assert_workers_gone(self, completed):
        # Any worker named by a progress diagnostic must be gone. Commands
        # whose standard error carries exactly one JSON refusal line (the
        # capture writer) emit no such diagnostics, so the process group is
        # the authority: after the leader has exited and been reaped, a
        # surviving group member can only be a leaked custody worker.
        pids = {row["pid"] for line in completed.stderr.splitlines()
                if line.startswith("{") and (row := json.loads(line)).get("event") == "calibration_custody_progress"}
        for pid in pids:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                continue
            raise AssertionError(f"custody worker {pid} survived its caller")
        assert self.process_group is not None, "no run to check for leaked workers"
        try:
            os.killpg(self.process_group, 0)
        except ProcessLookupError:
            return
        raise AssertionError(
            f"a custody worker survived its caller in process group {self.process_group}"
        )


class BlockedArtifact:
    """Send the exact original bytes through a FIFO, then withhold EOF."""
    def __init__(self, path, delay=None, advance=None):
        self.path, self.delay = path, delay
        self.advance = advance
        self.entered = threading.Event()
        self.release = threading.Event()
        self.finished = threading.Event()

    def __enter__(self):
        self.original = self.path.read_bytes()
        self.path.unlink()
        os.mkfifo(self.path)

        def supply():
            fd = None
            try:
                while not self.release.is_set():
                    try:
                        fd = os.open(self.path, os.O_WRONLY | os.O_NONBLOCK)
                        break
                    except OSError as exc:
                        if exc.errno != errno.ENXIO:
                            raise
                        self.release.wait(0.01)
                if fd is None:
                    return
                os.write(fd, self.original)
                self.entered.set()
                if self.advance is not None:
                    self.advance(self.delay)
                if self.advance is None or self.delay is None:
                    self.release.wait(self.delay)
            finally:
                if fd is not None:
                    os.close(fd)
                self.finished.set()

        self.thread = threading.Thread(target=supply, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *_args):
        self.release.set()
        self.thread.join(2)
        assert not self.thread.is_alive()
        self.path.unlink()
        self.path.write_bytes(self.original)


def install_reservation_append_expiry(fixture):
    """Expire only after the CLI checks readiness, inside receipt preparation."""
    marker = fixture.repo / "reservation-append-expiry.json"
    custom = fixture.repo / "sitecustomize.py"
    with custom.open("a") as hook:
        hook.write('''import json, os, sys
from pathlib import Path
# Worker subprocesses retain their normal read-only import surface.
if sys.argv[0].endswith("reserve_calibration_window_bracket.py"):
    from joulewise import calibration_ledger as ledger
    _append = ledger.append_bracket_session_receipt
    _target_core = ledger._target_core
    _deadline = None
    _paused = False
    def append(*args, **kwargs):
        global _deadline
        _deadline = kwargs["custody_deadline"]
        return _append(*args, **kwargs)
    def target_core(receipt):
        global _paused
        result = _target_core(receipt)
        if not _paused and _deadline is not None and receipt["event"] == ledger.BRACKET_SESSION_OPEN_EVENT:
            _paused = True
            _deadline.check()
            record = {"elapsed_before_pause": _deadline.elapsed_s,
                      "budget_s": _deadline.budget_s,
                      "observations": _deadline.observations}
            _advance(_deadline.remaining() + 0.03)
            record["elapsed_after_pause"] = _deadline.elapsed_s
            Path(os.environ["JW_APPEND_EXPIRY_MARKER"]).write_text(json.dumps(record))
        return result
    ledger.append_bracket_session_receipt = append
    ledger._target_core = target_core
''')
    fixture.env.update({"PYTHONPATH": str(fixture.repo),
                        "JW_APPEND_EXPIRY_MARKER": str(marker)})
    return marker


def install_read_barrier(fixture, *, after_reads=0, delay=60.0, metadata=False):
    """Instrument only the filesystem read seam in a disposable CLI checkout."""
    target = fixture.custodies[0] / "events.jsonl"
    marker = fixture.repo / "custody-read-barrier.jsonl"
    custom = fixture.repo / "sitecustomize.py"
    with custom.open("a" if fixture.control_clock else "w") as hook:
        hook.write('''import json, os, time
from pathlib import Path
_original = Path.read_bytes
_target = os.environ.get("JW_CUSTODY_BARRIER_TARGET")
_marker = os.environ.get("JW_CUSTODY_BARRIER_MARKER")
def _stall():
    if "JW_CUSTODY_TEST_CLOCK" in os.environ:
        _advance(float(os.environ["JW_CUSTODY_TEST_BUDGET"]))
    time.sleep(float(os.environ["JW_CUSTODY_BARRIER_DELAY"]))
def read_bytes(self):
    if _target and str(self) == _target:
        with open(_marker, "a+") as handle:
            handle.seek(0)
            count = len(handle.readlines())
            handle.write(json.dumps({"pid": os.getpid(), "read": count + 1}) + "\\n")
            handle.flush()
        if count >= int(os.environ["JW_CUSTODY_BARRIER_AFTER"]):
            _stall()
    return _original(self)
Path.read_bytes = read_bytes
''')
    if metadata:
        custom.write_text(custom.read_text() + '''
_original_exists = Path.exists
def exists(self, *args, **kwargs):
    if _target and str(self) == str(Path(_target).parent):
        with open(_marker, "a") as handle:
            handle.write(json.dumps({"pid": os.getpid(), "metadata": True}) + "\\n")
        _stall()
    return _original_exists(self, *args, **kwargs)
Path.exists = exists
''')
    fixture.env.update({"PYTHONPATH": str(fixture.repo),
                        "JW_CUSTODY_BARRIER_TARGET": str(target),
                        "JW_CUSTODY_BARRIER_MARKER": str(marker),
                        "JW_CUSTODY_BARRIER_AFTER": str(after_reads),
                        "JW_CUSTODY_BARRIER_DELAY": str(delay)})
    return marker
