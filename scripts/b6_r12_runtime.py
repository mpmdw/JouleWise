"""Synthetic external sources for the R12 isolated, unmodified collection pin.

Imported only by the fixture bootstrap, never by production collection code.
The clock is shared by all fixture children; sleepers advance it without a
wall-time scale factor. Native launches are checked before they reach exec.
"""
from __future__ import annotations

import argparse
import base64
import builtins
from contextlib import contextmanager
import datetime
import fcntl
import hashlib
import inspect
import io
import json
import mmap
import os
from pathlib import Path
import runpy
import struct
import subprocess
import sys
import tempfile
import threading
import time
import types
from types import SimpleNamespace

REAL_SLEEP = time.sleep
REAL_MONOTONIC = time.monotonic
REAL_POPEN = subprocess.Popen
REAL_RUN = subprocess.run
REAL_EXECUTE = subprocess.Popen._execute_child
REAL_KILL = os.kill
WALL_NS = 1_800_000_000_000_000_000
MONO_NS = 1_000_000_000_000


def source_root(root):
    active = os.environ.get("R12_ACTIVE_SOURCE_ROOT")
    if active:
        path = Path(active)
        if not path.is_relative_to(root):
            raise ValueError("active code root escapes fixture")
        return path
    pointer = Path(root) / "source-root.json"
    if not pointer.exists():
        return Path(root) / "pin"
    path = Path(json.loads(pointer.read_text())["path"])
    if not path.is_relative_to(root):
        raise ValueError("source root escapes fixture")
    return path


def fixture_python_wrapper(root, value):
    path = Path(value)
    if not path.is_absolute() or not path.is_relative_to(root) or ".venv" not in path.parts:
        return False
    if path.name not in {"python", "python3", "python3.13"}:
        return False
    try:
        return path.read_bytes().startswith(b"#!/bin/sh\n")
    except FileNotFoundError:
        return False


def fixture_codec(root, argv):
    if not argv or argv[0] not in {"zstd", "/opt/homebrew/bin/zstd", "/usr/local/bin/zstd", "/usr/bin/zstd"}:
        return False
    return all(value in {"--version", "-3", "-q", "-T0", "-o", "-d", "-c"}
               or (Path(value).is_absolute() and Path(value).is_relative_to(root)) for value in argv[1:])


def fixture_filecopy(root, argv):
    """The chain's own APFS copy writer, limited to non-symlink fixture paths."""
    if len(argv) != 5 or list(argv[:3]) != ["/bin/cp", "-c", "-pR"]:
        return False
    for value in argv[3:]:
        path = Path(value)
        if not path.is_absolute() or not path.is_relative_to(root) or ".." in path.parts:
            return False
        cursor = root
        for part in path.relative_to(root).parts:
            cursor /= part
            if cursor.is_symlink():
                return False
    return True


class SharedClock:
    """Integer nanosecond clock; a file lock serializes child advances.

    Every read uses the same shared frontier. A sleep advances the frontier by
    its requested duration. Sources can subscribe to advances in their own
    process, and receive each due sample before the sleep returns.
    """

    def __init__(self, path):
        self.path = Path(path)
        self.file = self.path.open("r+b", buffering=0)
        self.map = mmap.mmap(self.file.fileno(), 8)
        self.listeners = []
        self.passive = False
        self.foreground = None
        self.foregrounds = {}
        self.replay = False
        self.local = threading.local()
        self.stopping = False
        self.processes = {}
        self.stop_callbacks = []
        self.stop_delivered = False
        self.stop_input = self.path.parent / "source-stop.json"
        self.signal_input = self.path.parent / "signal-inputs" / f"{os.getpid()}-{os.environ.get('R12_PROCESS_TOKEN', 'top')}.json"
        self.next_control_check = 0.0

    def frontier(self):
        # Only input receivers need notification polling. The nominal 10 ms
        # transport poll interval is not a clock-value cache:
        # every read below still acquires the lock and reads the shared ns.
        if (self.stop_callbacks and not self.stop_delivered
                and REAL_MONOTONIC() >= self.next_control_check):
            self.next_control_check = REAL_MONOTONIC() + .01
            if self.stop_input.exists() or self.signal_input.exists():
                self.stop_delivered = True
                self.stopping = True
                for callback in tuple(self.stop_callbacks):
                    callback()
        with self.lock():
            return struct.unpack("!Q", self.map[:])[0]

    @classmethod
    def create(cls, path):
        Path(path).write_bytes(struct.pack("!Q", MONO_NS))
        return cls(path)

    def close(self):
        self.map.close()
        self.file.close()

    def monotonic_ns(self):
        if self.replay:
            if not hasattr(self.local, "ns"):
                self.local.ns = self.frontier()
            return self.local.ns
        return self.frontier()

    @contextmanager
    def lock(self):
        fcntl.flock(self.file, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(self.file, fcntl.LOCK_UN)

    monotonic_raw_ns = monotonic_ns

    @property
    def ns(self):
        return self.monotonic_ns()

    @property
    def wall_offset(self):
        return WALL_NS - MONO_NS

    def stamp(self):
        from joulewise.hazards.base import Stamp
        return Stamp(self.realtime_ns(), self.monotonic_ns(), self.monotonic_ns())

    def realtime_ns(self):
        return WALL_NS + self.monotonic_ns() - MONO_NS

    def time(self):
        return self.realtime_ns() / 1e9

    def monotonic(self):
        return self.monotonic_ns() / 1e9

    def clock_gettime_ns(self, which):
        if which == time.CLOCK_REALTIME:
            return self.realtime_ns()
        if which in (time.CLOCK_MONOTONIC, time.CLOCK_MONOTONIC_RAW):
            return self.monotonic_ns()
        raise ValueError("undeclared synthetic clock")

    def sleep(self, seconds):
        if seconds < 0:
            raise ValueError("negative synthetic sleep")
        if self.replay:
            target = self.monotonic_ns() + round(seconds * 1e9)
            directory = self.path.parent / "passive"
            directory.mkdir(exist_ok=True)
            marker = directory / f"{os.getpid()}-{threading.get_ident()}.json"
            temporary = marker.with_suffix(".tmp")
            temporary.write_text(json.dumps({"pid": os.getpid(), "next_ns": target}))
            temporary.replace(marker)
            self.local.marker = marker
            while self.frontier() < target and not self.stopping:
                REAL_SLEEP(0.001)
            self.local.ns = min(target, self.frontier())
            if self.stopping:
                marker.unlink(missing_ok=True)
            return
        if self.passive:
            active = any(process.poll() is None for process in self.foregrounds.values())
            if not active and self.foregrounds:
                self.passive = False
            else:
            # Supervisor/background waits never move the foreground clock.
                REAL_SLEEP(0.002)
                return
        with self.lock():
            previous = struct.unpack("!Q", self.map[:])[0]
            current = previous + round(seconds * 1e9)
            self.map[:] = struct.pack("!Q", current)
        for listener in tuple(self.listeners):
            listener(previous, current)
        self.await_sources(current)
        REAL_SLEEP(0)

    def await_sources(self, current):
        """Wait for real background writers to consume the advanced timeline."""
        directory = self.path.parent / "passive"
        deadline = REAL_MONOTONIC() + 30
        while directory.exists():
            pending = False
            for marker in directory.glob("*.json"):
                try:
                    value = json.loads(marker.read_text())
                    if value["next_ns"] <= current:
                        process = self.processes.get(value["pid"])
                        if process is not None and process.poll() is not None:
                            marker.unlink(missing_ok=True)
                            continue
                        try:
                            os.kill(value["pid"], 0)  # only fixture-registered PIDs; observation only
                        except ProcessLookupError:
                            marker.unlink(missing_ok=True)
                        else:
                            pending = True
                except FileNotFoundError:
                    pass
            if not pending:
                return
            if REAL_MONOTONIC() >= deadline:
                raise TimeoutError("synthetic background source did not consume logical frontier")
            REAL_SLEEP(0.001)

    def install(self):
        time.time, time.time_ns = self.time, self.realtime_ns
        time.monotonic, time.monotonic_ns = self.monotonic, self.monotonic_ns
        time.perf_counter, time.perf_counter_ns = self.monotonic, self.monotonic_ns
        time.clock_gettime_ns, time.sleep = self.clock_gettime_ns, self.sleep
        # stdlib imported these aliases before the source clock was installed.
        # Their deadlines must use the same timeline as the pinned Clock.
        subprocess._time = self.monotonic
        # Popen's polling sleep is a transport wait, not a producer advancing
        # the scenario. Keep its clock reads shared, and yield real CPU while
        # its actual child consumes the current logical frontier.
        subprocess.time = SimpleNamespace(sleep=lambda seconds: REAL_SLEEP(min(.002, seconds)))
        threading._time = self.monotonic
        # datetime.now is a separate OS clock entry point, not time.time().
        original = datetime.datetime
        clock = self

        class FixtureDatetime(original):
            @classmethod
            def now(cls, tz=None):
                return cls.fromtimestamp(clock.time(), tz)

            @classmethod
            def utcnow(cls):
                return cls.fromtimestamp(clock.time(), datetime.UTC).replace(tzinfo=None)

        datetime.datetime = FixtureDatetime


def audit_guard(root, pin):
    """Deny forbidden reads, escaping writes, network and undeclared execs."""
    root, pin = Path(root), Path(pin)
    opened_code = set()

    def path_check(value, write=False):
        if not isinstance(value, (str, bytes, os.PathLike)):
            return
        path = Path(os.path.abspath(os.fsdecode(value)))
        # This check is lexical: no stat/resolve on an unauthorized locator.
        if path.is_relative_to("/Users/edr") or ("restricted" in path.parts and not path.is_relative_to(root)):
            with (root / "denials.jsonl").open("a") as out:
                frames = []
                frame = sys._getframe(1)
                for _ in range(8):
                    if frame is None:
                        break
                    frames.append([frame.f_code.co_filename, frame.f_code.co_name, frame.f_lineno])
                    frame = frame.f_back
                out.write(json.dumps({"path": str(path), "write": write, "frames": frames}) + "\n")
            raise PermissionError("R12 forbidden locator")
        if write and not path.is_relative_to(root):
            raise PermissionError("R12 write outside fixture root: " + str(path))

    # Python has no audit event for stat/lstat/access. Intercept those native
    # calls explicitly, before they can probe a forbidden locator.
    for name in ("stat", "lstat", "access", "readlink"):
        original = getattr(os, name)
        def checked(path, *args, _original=original, **kwargs):
            path_check(path)
            return _original(path, *args, **kwargs)
        setattr(os, name, checked)

    def audit(event, args):
        if event == "open":
            path_check(args[0], bool(args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)))
            if isinstance(args[0], (str, bytes, os.PathLike)):
                path = Path(os.path.abspath(os.fsdecode(args[0])))
                if path.is_relative_to(root) and path.suffix in {".py", ".sh", ".zsh"} and str(path) not in opened_code:
                    opened_code.add(str(path))
                    with (root / f"source-reads-{os.getpid()}.jsonl").open("a") as stream:
                        stream.write(json.dumps({"path": str(path)}) + "\n")
        elif event in {"os.listdir", "os.scandir"}:
            path_check(args[0])
        elif event in {"os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.truncate", "os.utime", "os.chown"}:
            path_check(args[0], True)
        elif event == "os.rename":
            path_check(args[0], True)
            path_check(args[1], True)
        elif event == "os.symlink":
            source, destination = map(os.fsdecode, args[:2])
            path_check(destination, True)
            allowed = source in {sys.executable, "python", "python3", "python3.13", str(root / "interpreter/python3.13")}
            if not allowed or ".venv" not in Path(destination).parts:
                raise PermissionError("R12 symlink is not a fixture interpreter alias")
        elif event in {"socket.connect", "socket.bind", "socket.sendto", "socket.getaddrinfo", "socket.gethostbyname",
                       "socket.gethostbyaddr", "socket.getnameinfo", "os.system", "os.posix_spawn", "os.exec", "os.fork", "os.link"}:
            raise PermissionError("R12 native action denied: " + event)
        elif event == "os.killpg" or (event == "os.kill" and args[1] != 0):
            raise PermissionError("R12 native signal denied")
        elif event == "subprocess.Popen":
            executable, argv, cwd, env = args
            exe = str(executable)
            # Only the fixture's explicit Python bootstrap may start Python.
            python = exe == sys.executable and len(argv) >= 3 and argv[1:3] == ["-B", str(root / "bootstrap.py")]
            zsh = exe == "/bin/zsh" and len(argv) > 2 and str(argv[2]) == str(root / "shell.zsh")
            git_root = str(argv[argv.index("-C") + 1]) if "-C" in argv else str(cwd or os.getcwd())
            git = exe in ("git", "/usr/bin/git") and Path(git_root).is_relative_to(root)
            if git and any(value in argv for value in ("push", "fetch", "pull", "ls-remote")):
                raise PermissionError("R12 network Git command denied")
            if git and "clone" in argv:
                from urllib.parse import urlparse, unquote
                operands = [str(value) for value in argv if str(value).startswith("file://")]
                if len(operands) != 1 or not Path(unquote(urlparse(operands[0]).path)).is_relative_to(root):
                    raise PermissionError("R12 clone must use fixture-local source objects")
            wrapper = fixture_python_wrapper(root, exe)
            if not (python or zsh or git or wrapper or fixture_codec(root, argv) or fixture_filecopy(root, argv)):
                raise PermissionError("R12 undeclared native argv: " + repr(argv))

    sys.addaudithook(audit)


def bootstrap(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("kind", choices=("clock", "script", "module", "code", "probe", "plan", "loop-probe", "seed-probe", "returned", "sampler", "dispatch", "make-inputs", "guard-probe", "meter-probe", "j1-schema-probe"))
    parser.add_argument("rest", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    root = args.root
    if not root.is_absolute() or root.is_relative_to("/Users/edr") or "restricted" in root.parts:
        raise ValueError("forbidden bootstrap root")
    clock = SharedClock(root / "clock.bin")
    clock.install()
    pin = source_root(root)
    sys.path.insert(0, str(pin))
    (root / "tmp").mkdir(exist_ok=True)
    tempfile.tempdir = str(root / "tmp")
    os.environ["JOULEWISE_CUSTODY_PARENT"] = str(root / "host-state")
    os.environ.pop("JOULEWISE_ADDITIONAL_CUSTODY_PARENTS", None)
    os.environ["PYTHONNOUSERSITE"] = "1"
    # The pinned verdict writer exposes this execution-concurrency input.
    # Its spawn pool cannot inherit the fixture's Python source bootstrap;
    # serial validation runs the same validator inside the isolated process.
    os.environ["JOULEWISE_WHOLE_WINDOW_WORKERS"] = "1"
    os.environ["PATH"] = "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    overlay_path = root / "input-overlays.json"
    if overlay_path.exists():
        overlays = json.loads(overlay_path.read_text())
        for owner, name in ((builtins, "open"), (io, "open"), (os, "stat"), (os, "lstat")):
            original = getattr(owner, name)
            def overlay(path, *args, _original=original, **kwargs):
                if isinstance(path, (str, bytes, os.PathLike)):
                    path = overlays.get(os.path.abspath(os.fsdecode(path)), path)
                return _original(path, *args, **kwargs)
            setattr(owner, name, overlay)
    # subprocess.DEVNULL is a writable external destination too. Keep the
    # sink inside the fixture rather than exempting it from the write fence.
    os.devnull = str(root / "null-sink")
    (root / "null-sink").touch(exist_ok=True)
    audit_guard(root, pin)
    if os.environ.get("R12_TRACE_STACKS") == "1":
        import faulthandler
        import signal
        trace = (root / f"debug-stack-{os.getpid()}.txt").open("w")
        faulthandler.register(signal.SIGUSR1, file=trace, all_threads=True)
        faulthandler.dump_traceback_later(15, repeat=True, file=trace)
    if args.kind == "guard-probe":
        denied = []
        # The wrappers reject these lexical requests before native access.
        for operation in (os.stat, os.lstat, os.access, os.readlink):
            try:
                if operation is os.access:
                    operation("/Users/edr/R12-never-access", os.F_OK)
                else:
                    operation("/Users/edr/R12-never-access")
            except PermissionError:
                denied.append(operation.__name__)
        try:
            subprocess.Popen([sys.executable, "-B", "-c", "raise SystemExit(99)"])
        except PermissionError:
            denied.append("native")
        try:
            (root.parent / "R12-outside-write").write_bytes(b"must not be written")
        except PermissionError:
            denied.append("write")
        print(json.dumps(denied))
        return 0 if len(denied) == 6 else 1
    if args.kind == "returned":
        result = json.loads(base64.b64decode(args.rest[0]))
        sys.stdout.buffer.write(base64.b64decode(result["stdout"]))
        sys.stderr.buffer.write(base64.b64decode(result["stderr"]))
        return result["rc"]
    if args.kind == "sampler":
        return sampler_source(root, clock, args.rest)
    if args.kind == "make-inputs":
        return make_synthetic_inputs(root)
    if args.kind == "dispatch":
        while args.rest and args.rest[0] in ("-B", "-u"):
            args.rest.pop(0)
        if args.rest[0] in ("-c", "-m"):
            args.kind = "code" if args.rest.pop(0) == "-c" else "module"
        else:
            args.kind = "script"
    if args.kind == "script":
        for argument in args.rest[:2]:
            candidate = Path(argument)
            if candidate.is_absolute() and candidate.is_relative_to(root) and candidate.parent.name == "scripts":
                selected = candidate.parent.parent
                if (selected / "joulewise").is_dir():
                    os.environ["R12_ACTIVE_SOURCE_ROOT"] = str(selected)
                    pin = selected
                    sys.path.insert(0, str(pin))
                    break
    if args.kind == "module" and args.rest[:1] == ["venv"]:
        sys._base_executable = str(root / "interpreter/python3.13")
    if args.kind == "clock":
        if args.rest[0] == "sleep":
            clock.sleep(float(args.rest[1]))
        elif args.rest[0] == "+%s":
            print(int(clock.time()))
        else:
            print(datetime.datetime.now(datetime.UTC).strftime(args.rest[0].lstrip("+")))
        return 0
    if args.kind == "probe":
        from joulewise.clock import SystemClock
        source = SystemClock()
        before = source.stamp()
        source.sleep(float(args.rest[0]))
        after = source.stamp()
        print(json.dumps({"before": before.__dict__, "after": after.__dict__,
                          "source": str(sys.modules["joulewise.clock"].__file__)}))
        return 0
    if args.kind == "plan":
        return plan_fixture(root, clock, *args.rest)
    if args.kind == "loop-probe":
        from b6_r12_orchestrate import loop_fixture
        return loop_fixture(root, clock, *args.rest)
    if args.kind == "seed-probe":
        from b6_r12_orchestrate import seed_calibration
        seed_calibration(root, clock, install_sources(root, clock), source_root(root))
        return 0
    install_sources(root, clock)
    if args.kind == "script" and args.rest and Path(args.rest[0]).name == "validate_powermetrics_fiducial.py":
        # A declared clock phase at calibration-program entry. Preserve
        # exact integer ns instead of accumulating binary-float sleep tails.
        target = ((clock.ns + 999_999_999) // 1_000_000_000) * 1_000_000_000 + 132
        clock.sleep((target - clock.ns) / 1e9)
    if args.kind == "j1-schema-probe":
        from joulewise import controller
        producer = runpy.run_path(str(pin / "scripts/b5_window_calibration_verdict.py"), run_name="r12_j1_probe")
        unit = root / "j1-unit"
        unit.mkdir()
        capture = unit / "absent-slot"
        record = producer["build_verdict"](capture)
        producer["write_create_once"](unit / producer["VERDICT_BASENAME"], record)
        _, miss = controller._window_calibration_verdict_bound(capture, {}, stored_bound=0.0)
        print(json.dumps({"producer": producer["SCHEMA"], "consumer": controller.WINDOW_CALIBRATION_VERDICT_SCHEMA,
                          "miss": miss}))
        return 0
    if args.kind == "meter-probe":
        import ctypes
        original_cdll = ctypes.CDLL
        def no_native_usb(name, *args, **kwargs):
            if "libusb" in str(name).lower():
                raise AssertionError("native USB library load reached")
            return original_cdll(name, *args, **kwargs)
        ctypes.CDLL = no_native_usb
        module = runpy.run_path(str(pin / "scripts/km003c_monitor.py"), run_name="r12_meter_probe")
        return module["main"](["--out", str(root / "source-only-meter.jsonl"), "--duration", "2"])
    if args.rest and Path(args.rest[0]).name in {"hazard_monitor.py", "km003c_monitor.py"}:
        clock.passive = True
        clock.replay = True
        import signal
        original_signal = signal.signal
        def register_signal(number, handler):
            if not callable(handler):
                return original_signal(number, handler)
            def received(signum, frame):
                clock.stopping = True
                return handler(signum, frame)
            if number == signal.SIGTERM:
                clock.stop_callbacks.append(lambda: received(signal.SIGTERM, None))
            return original_signal(number, received)
        signal.signal = register_signal
    sys.argv = args.rest
    if args.kind == "script":
        runpy.run_path(args.rest[0], run_name="__main__")
    elif args.kind == "module":
        runpy.run_module(args.rest[0], run_name="__main__")
    else:
        exec(compile(args.rest[0], "<pinned-chain-inline>", "exec"), {"__name__": "__main__"})
    return 0


def plan_fixture(root, clock, pack="alpha", mode="plan"):
    """Run the pinned plan writer on pre-session, synthetic ledger inputs."""
    from joulewise.b5 import plan
    from joulewise.b6 import plan_inputs
    from joulewise.calibration_ledger import GENESIS_DIGEST, LEDGER_SCHEMA
    pin = source_root(root)
    # These are generator-owned inputs, before the chain writes its tree.
    ledger = pin / plan.DEFAULT_LEDGER_RELATIVE
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_bytes(b"")
    head = pin / plan.HEAD_PIN_RELATIVE
    head.parent.mkdir(parents=True, exist_ok=True)
    head.write_text(json.dumps({"sequence": 0, "head_digest": GENESIS_DIGEST, "ledger_schema": LEDGER_SCHEMA}))
    sources = install_sources(root, clock)
    from scripts.write_derivation_night_inputs import _derive_planned_vectors
    epoch, t1 = _derive_planned_vectors(plan.POWER_POLICY)
    identities = {}
    for name, value in (("identity-epoch.json", epoch), ("t1-bindings.json", t1)):
        path = root / "inputs" / name
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True) + "\n")
        identities[name] = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    session = root / "sessions" / ("R12-" + pack)
    session.mkdir(parents=True)
    runs = session / "runs-parent"
    runs.mkdir()
    packs = {"alpha": "d117_floor_qwen3-1p7b_v5", "beta": "d117_floor_qwen3-8b_v5",
             "gamma": "d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5"}
    head_value = REAL_RUN(["git", "rev-parse", "HEAD"], cwd=pin, capture_output=True, text=True, check=True).stdout.strip()
    inputs = plan_inputs.build(pin, pin / "configs/b6/registration", packs[pack], "R12-" + pack,
                              identities, custody_root=session / "custody", runs_parent=runs,
                              claim_backup=session / "backup-claim", bound_backup=session / "backup-bound", head=head_value)
    inputs["t0_epoch_s"] = 60 * ((int(clock.time()) + 420 + 59) // 60)
    record = plan.write_window_plan(inputs, now=clock.time)
    (root / "plan-receipt.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print("plan", pack, record["member_count"], record["plan"]["path"])
    if mode == "driver":
        from scripts import run_night
        clock.sleep(inputs["t0_epoch_s"] - clock.time())
        code = run_night.run_night(Path(record["plan"]["path"]))
        print("driver_exit", code)
        return code
    return 0


class ReturnedProcess:
    """A declared host-action result, with no native process behind it."""
    def __init__(self, result=(0, b"", b""), *, alive=False, pid=987654320):
        self.pid, self.returncode = pid, None if alive else result[0]
        self.result = result

    def poll(self):
        return self.returncode

    def communicate(self, **kwargs):
        self.returncode = self.result[0]
        return self.result[1:]

    def wait(self, **kwargs):
        self.returncode = self.result[0]
        return self.returncode

    def terminate(self):
        self.returncode = 0

    kill = terminate

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def install_sources(root, clock):
    """Supply defaults at the pinned code's existing external-input seams."""
    from arm_sources import Sources, BOOT
    from joulewise.hazards import arm, base, monitor, thermal, battery
    from joulewise.b5 import driver
    from joulewise.b6 import sleep_guard
    from joulewise import kernel_clock
    import dataclasses
    install_engine(root, clock)
    # The sampler executable's identity is an external byte input too. Hash
    # the declared synthetic identity bytes through the unchanged hash code.
    sampler_identity = root / "sampler-identity.bin"
    if not sampler_identity.exists():
        sampler_identity.write_bytes(b"R12 synthetic powermetrics identity\n")
    for owner, name in ((builtins, "open"), (io, "open"), (os, "stat"), (os, "lstat")):
        original = getattr(owner, name)
        def redirected(path, *args, _original=original, **kwargs):
            if isinstance(path, (str, bytes, os.PathLike)) and os.fsdecode(path) == "/usr/bin/powermetrics":
                path = sampler_identity
            return _original(path, *args, **kwargs)
        setattr(owner, name, redirected)

    class ChainSources(Sources):
        def __init__(self):
            policy = json.loads((root / "source-policy.json").read_text()) if (root / "source-policy.json").exists() else {}
            super().__init__(root, clock, denied_off=policy.get("denied_off", False))
            self.processes = {}
            self.rules.update({
                ("/usr/bin/pmset", "-g", "assertions"): (0, b"PreventSystemSleep 1\npid 987654320(caffeinate): [0x1] PreventUserIdleSystemSleep named: 'caffeinate'\n", b""),
                ("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"): (0, (BOOT + "\n").encode(), b""),
                ("sysctl", "-n", "kern.bootsessionuuid"): (0, (BOOT + "\n").encode(), b""),
                ("/usr/sbin/sysctl", "-n", "kern.osversion"): (0, b"25G83\n", b""),
                ("/usr/sbin/sysctl", "-n", "hw.model"): (0, b"Mac15,9\n", b""),
                ("/sbin/mount",): (0, b"/dev/disk-fixture on / (apfs, local)\n", b""),
                ("/usr/bin/pmset", "displaysleepnow"): (0, b"", b""),
                ("pmset", "displaysleepnow"): (0, b"", b""),
                ("/usr/sbin/ioreg", "-p", "IOUSB", "-l", "-w0"): (0,
                    b'+-o KM003C\n "idVendor" = 24521\n "idProduct" = 99\n "USB Serial Number" = "R12-NO-HARDWARE"\n "bcdDevice" = 512\n', b""),
            })
            readings = {
                ("pmset", "-g", "batt"): "Now drawing from 'AC Power'\n -InternalBattery-0 100%; charged; 0:00 remaining\n",
                ("pmset", "-g"): "System-wide power settings:\n lowpowermode 0\n",
                ("pmset", "-g", "assertions"): "PreventUserIdleDisplaySleep 0\nPreventUserIdleSystemSleep 1\n",
                ("pmset", "-g", "therm"): "Note: No thermal warning level has been recorded\n",
                ("pmset", "-g", "systemstate"): "Current System Capabilities are: CPU Audio Network\n",
                ("defaults", "-currentHost", "read", "com.apple.screensaver"): "{ moduleDict = { moduleName = R12; }; idleTime = 86400; }\n",
                ("ioreg", "-c", "IOHIDSystem"): '"HIDIdleTime" = 1000000000000\n',
                ("ioreg", "-r", "-c", "IOMobileFramebuffer"): '"IOMFBPowerState" = 0\n',
                ("system_profiler", "SPDisplaysDataType", "-json"): json.dumps({"SPDisplaysDataType": [{"spdisplays_ndrvs": [{
                    "spdisplays_online": "spdisplays_yes", "spdisplays_connection_type": "spdisplays_internal",
                    "spdisplays_asleep": "spdisplays_yes"}]}]}),
                ("memory_pressure", "-Q"): "System-wide memory free percentage: 90%\n",
                ("vm_stat",): "Mach Virtual Memory Statistics: (page size of 16384 bytes)\nPages free: 2000000.\nPages active: 1000.\nPageouts: 0.\n",
                ("sysctl", "-n", "hw.memsize"): "68719476736\n",
                ("sysctl", "vm.swapusage"): "vm.swapusage: total = 0.00M used = 0.00M free = 0.00M\n",
                ("sysctl", "-n", "kern.boottime"): "{ sec = 1799999000, usec = 0 }\n",
                ("sysctl", "-n", "hw.model", "hw.ncpu", "machdep.cpu.brand_string"): "Mac15,9\n16\nR12 synthetic CPU\n",
                ("uptime",): "1 day, 1 user, load averages: 0.00 0.00 0.00\n",
                ("sw_vers",): "ProductName: macOS\nProductVersion: 26.0\nBuildVersion: 25G83\n",
            }
            self.rules.update({argv: (0, value.encode(), b"") for argv, value in readings.items()})
            self.rules[("ioreg", "-r", "-c", "AppleSmartBattery", "-d", "1")] = self.battery

        def battery(self):
            rc, raw, err = super().battery()
            raw = raw.replace(b'      "Voltage"', b'      "FullyCharged" = Yes\n      "Watts" = 140\n'
                              b'      "Description" = "R12 synthetic adapter"\n      "Voltage"')
            return rc, raw, err

        def completed(self, argv, result, kind):
            value = super().completed(argv, result, kind)
            self.calls[-1]["source_monotonic_ns"] = clock.ns
            with (root / f"source-calls-{os.getpid()}.jsonl").open("a") as out:
                out.write(json.dumps(self.calls[-1], sort_keys=True) + "\n")
            return value

        def run(self, argv, timeout_s):
            argv = tuple(map(str, argv))
            from joulewise.hazards import instrument
            if argv == self.off:
                policy = json.loads((root / "source-policy.json").read_text())
                result = (126, b"", b"RL-49 declared denied OFF action") if policy.get("denied_off") else (
                    0, b"Network Time is already off.\n", b"")
                return self.completed(argv, result, "declared_action_denied" if result[0] else "declared_action_success")
            if argv and argv[0] in ("git", "/usr/bin/git"):
                result = REAL_RUN(argv, capture_output=True, timeout=timeout_s, check=False)
                from joulewise.hazards.base import Completed
                return Completed(argv, result.returncode, result.stdout, result.stderr)
            if argv and argv[0] == str(source_root(root) / "scripts/install_night_agent.sh"):
                return self.completed(argv, (0, b"R12 declared installer success; no host action executed\n", b""), "declared_action_success")
            if len(argv) == 3 and argv[:2] == ("launchctl", "print"):
                label = argv[-1].rsplit("/", 1)[-1]
                return self.completed(argv, (113, b"", f'Could not find service "{label}" in domain for user gui: {os.getuid()}\n'.encode()), "declared_job_absent")
            if len(argv) >= 4 and argv[:4] == (sys.executable, "-B", "-c", instrument.CHILD_BOOTSTRAP):
                return super().run(argv, timeout_s)
            if (len(argv) == 7 and argv[:2] == ("/bin/ps", "-p") and argv[3:] == ("-o", "lstart=", "-o", "stat=")):
                return self.completed(argv, (0, b"Mon Nov  2 00:00:00 2026 S\n", b""), "declared_process_identity")
            if argv and argv[0] == "/usr/bin/pgrep" and "-g" in argv:
                pid = int(argv[argv.index("-g") + 1])
                process = self.processes.get(pid)
                return self.completed(argv, (1, b"", b"") if process is None or process.poll() is not None
                                      else (0, f"{pid} R12-pinned-child\n".encode(), b""), "declared_owned_group_census")
            rewrite = self.rewritten(argv)
            if rewrite:
                value = REAL_RUN(rewrite, capture_output=True, timeout=timeout_s, check=False)
                from joulewise.hazards.base import Completed
                return Completed(argv, value.returncode, value.stdout, value.stderr)
            return super().run(argv, timeout_s)

        def rewritten(self, argv):
            argv = list(map(str, argv))
            if argv[:2] in (["/usr/bin/taskpolicy", "-b"], ["/usr/sbin/taskpolicy", "-b"]):
                argv = argv[2:]
            if argv and fixture_python_wrapper(root, argv[0]):
                return argv
            if argv and (argv[0] in {sys.executable, "/opt/homebrew/bin/python3.13"} or argv[0] == str(source_root(root) / ".venv/bin/python")):
                rest = argv[1:]
                while rest and rest[0] in ("-B", "-u"):
                    rest.pop(0)
                if rest[:1] == ["-c"]:
                    kind, rest = "code", rest[1:]
                elif rest[:1] == ["-m"]:
                    kind, rest = "module", rest[1:]
                else:
                    kind = "script"
                return [sys.executable, "-B", str(root / "bootstrap.py"), "--root", str(root), kind, *rest]
            if argv[:1] == ["/bin/zsh"]:
                rest = argv[1:]
                if rest[:1] == ["-f"]:
                    rest = rest[1:]
                return ["/bin/zsh", "-f", str(root / "shell.zsh"), *rest]
            return None

        def subprocess_run(self, argv, **kwargs):
            argv = tuple(map(str, argv))
            # Git only reads fixture code/config objects. It is neither a
            # simulated host action nor a read of the original checkout.
            if argv and argv[0] in ("git", "/usr/bin/git"):
                return REAL_RUN(argv, **kwargs)
            from joulewise.hazards import instrument
            if len(argv) >= 4 and argv[:4] == (sys.executable, "-B", "-c", instrument.CHILD_BOOTSTRAP):
                return super().subprocess_run(argv, **kwargs)
            rewrite = self.rewritten(argv)
            if rewrite:
                return REAL_RUN(rewrite, **kwargs)
            if argv and argv[0] == "/usr/bin/pgrep" and "-g" in argv:
                pid = int(argv[argv.index("-g") + 1])
                process = self.processes.get(pid)
                result = self.completed(argv, (1, b"", b"") if process is None or process.poll() is not None
                                        else (0, f"{pid} R12-pinned-child\n".encode(), b""), "declared_owned_group_census")
            else:
                result = self.run(argv, kwargs.get("timeout", 10))
            out, err = result.stdout, result.stderr
            if kwargs.get("text") or kwargs.get("universal_newlines"):
                out, err = out.decode(), err.decode()
            value = subprocess.CompletedProcess(argv, result.returncode, out, err)
            if kwargs.get("check"):
                value.check_returncode()
            return value

        def popen(self, argv, **kwargs):
            argv = tuple(map(str, argv))
            if argv[:3] == (sys.executable, "-B", str(root / "bootstrap.py")) or (argv and argv[0] in ("git", "/usr/bin/git")):
                return REAL_POPEN(argv, **kwargs)
            if argv in self.sampler_commands:
                return super().popen(argv, **kwargs)
            rewrite = self.rewritten(argv)
            if rewrite:
                value = REAL_POPEN(rewrite, **kwargs)
                self.processes[value.pid] = value
                if argv[:1] == ("/bin/zsh",):
                    clock.passive = True
                    clock.foreground = value
                    clock.foregrounds[value.pid] = value
                return value
            if argv[:4] == ("/usr/bin/caffeinate", "-i", "-s", "-w"):
                self.completed(argv, (0, b"", b""), "declared_action_success")
                return ReturnedProcess(alive=True)
            value = self.run(argv, 10)
            return ReturnedProcess((value.returncode, value.stdout, value.stderr))

    sources = ChainSources()
    clock.processes = sources.processes
    def signal_result(pid, number, *, group=False):
        import signal
        if number == 0 and not group:
            return REAL_KILL(pid, 0)  # read-only existence check of a fixture marker's PID
        argv = ("os.killpg" if group else "os.kill", str(pid), str(number))
        process = sources.processes.get(pid)
        if number == 0 and group:
            # A probe is a process observation, not a requested action. The
            # unchanged harvest interprets EPERM as "may still be alive";
            # the declared absent observation must therefore return ESRCH.
            alive = process is not None and process.poll() is None
            sources.completed(argv, (0, b"", b"") if alive else (3, b"", b"declared fixture group absent"),
                              "declared_owned_group_census")
            if not alive:
                raise ProcessLookupError(pid)
            return None
        if process is None or number != signal.SIGTERM:
            sources.completed(argv, (126, b"", b"RL-49 undeclared signal denied"), "declared_action_denied")
            raise PermissionError("undeclared fixture signal")
        if process.poll() is not None:
            sources.completed(argv, (3, b"", b"fixture child already gone"), "declared_child_absent")
            raise ProcessLookupError(pid)
        # The return value of the host action is synthetic. Incoming signal
        # delivery is an external OS input to the pinned handler. Its actual
        # meter/monitor writer, not this caller, writes the shutdown records.
        directory = root / "signal-inputs"
        directory.mkdir(exist_ok=True)
        (directory / f"{pid}-{process._r12_signal_token}.json").write_text(json.dumps({"signum": int(number),
            "declared_result": 0, "executed": False}) + "\n")
        sources.completed(argv, (0, b"", b""), "declared_action_success")
    os.kill = lambda pid, number: signal_result(pid, number)
    os.killpg = lambda pid, number: signal_result(pid, number, group=True)
    # A dataclass may already have captured the OS default during imports.
    from joulewise.b5 import harvest
    parameters = list(inspect.signature(harvest.Seams).parameters)
    defaults = list(harvest.Seams.__init__.__defaults__)
    names = parameters[-len(defaults):]
    defaults[names.index("killpg")] = os.killpg
    harvest.Seams.__init__.__defaults__ = tuple(defaults)
    install_usb_source(root, clock)
    word = kernel_clock.Timex()
    frequency = {"schema_version": kernel_clock.PROBE_SCHEMA, "modes": 0, "raw_word": 0,
                 "ppm": 0., "call_status": 0, "timex_status": 0, "errno": 0, "raw_hex": bytes(word).hex()}
    ctx = base.Context(run=sources.run, clocks=clock)
    disk = lambda path: SimpleNamespace(f_bavail=1024 ** 3, f_frsize=4096, f_blocks=2 ** 40)
    stat = lambda path: SimpleNamespace(st_dev=1)
    host = lambda: [[0, 0, clock.ns // 10_000_000, 0]]
    sources.frequency_reader = lambda: frequency
    sources.stat, sources.statvfs, sources.host_reader = stat, disk, host
    # Substitute the default object, not the arm or its run/judge/writers.
    arm.run.__defaults__ = (arm.Seams(ctx=ctx, frequency_reader=lambda: frequency,
                                   statvfs=disk, stat=stat, host_cpu=host, smc_read=None),)
    defaults = list(driver.Seams.__init__.__defaults__)
    defaults[1] = sources.popen
    defaults[2] = lambda path: 1 << 60
    driver.Seams.__init__.__defaults__ = tuple(defaults)
    sleep_guard.KeepAwake.__init__.__defaults__ = (sources.popen, sources.subprocess_run, None)
    monitor.Monitor.__init__.__kwdefaults__.update(ctx=ctx, frequency_reader=lambda: frequency,
                                                  statvfs=disk, stat=stat, host_reader=host)
    class ThermalSource:
        def read(self):
            return 0
        def close(self):
            pass
    class BatterySource:
        def read(self):
            return {"UpdateTime": int(clock.time()), "ExternalConnected": True, "IsCharging": False,
                    "InstantAmperage": 0, "Amperage": 0, "Voltage": 12000}
        def close(self):
            pass
    class SmcSource:
        def read(self, *args):
            from joulewise.hazards import smc
            return {"values": {key: 0.0 for key in smc.KEYS}, "errors": {}}
        def close(self):
            pass
    from joulewise.hazards import smc
    thermal.NotifyReader, battery.RegistryReader, smc.Reader = ThermalSource, BatterySource, SmcSource
    from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
    # Existing post-marker clock seam. A declared 200 ms scheduler quantum
    # lets the real drain judge see a native right edge after the stop marker.
    PowermetricsTelemetryAdapter.__init__.__kwdefaults__["drain_sleep"] = lambda seconds: clock.sleep(max(seconds, 0.2))
    signature = inspect.signature(REAL_EXECUTE)
    def execute_child(process, *args, **kwargs):
        bound = signature.bind(process, *args, **kwargs)
        argv = tuple(map(str, bound.arguments["args"]))
        rewrite = sources.rewritten(argv)
        if argv[:3] == (sys.executable, "-B", str(root / "bootstrap.py")):
            rewrite = list(argv)
        elif argv[:3] == ("/bin/zsh", "-f", str(root / "shell.zsh")):
            rewrite = list(argv)
        elif argv and argv[0] in ("git", "/usr/bin/git"):
            rewrite = list(argv)
        elif fixture_codec(root, argv):
            rewrite = list(argv)
        elif fixture_filecopy(root, argv):
            rewrite = list(argv)
        elif any(value == "/usr/bin/powermetrics" for value in argv) and "-o" in argv:
            rewrite = [sys.executable, "-B", str(root / "bootstrap.py"), "--root", str(root), "sampler", *argv]
        elif rewrite is None:
            result = sources.run(argv, 10)
            payload = base64.b64encode(json.dumps({"rc": result.returncode,
                "stdout": base64.b64encode(result.stdout).decode(),
                "stderr": base64.b64encode(result.stderr).decode()}).encode()).decode()
            rewrite = [sys.executable, "-B", str(root / "bootstrap.py"), "--root", str(root), "returned", payload]
        bound.arguments["args"] = rewrite
        bound.arguments["executable"] = rewrite[0]
        import secrets
        token = secrets.token_hex(12)
        bound.arguments["env"] = {**(bound.arguments.get("env") or os.environ), "R12_PROCESS_TOKEN": token}
        result = REAL_EXECUTE(*bound.args, **bound.kwargs)
        process._r12_signal_token = token
        sources.processes[process.pid] = process
        background = any(Path(value).name in {"hazard_monitor.py", "km003c_monitor.py"} for value in argv)
        sampler = "sampler" in rewrite[5:7]
        returned = rewrite[:3] == [sys.executable, "-B", str(root / "bootstrap.py")] and rewrite[5:6] == ["returned"]
        python_foreground = (rewrite[:3] == [sys.executable, "-B", str(root / "bootstrap.py")]
                             or fixture_python_wrapper(root, rewrite[0]))
        if not background and not sampler and not returned and python_foreground:
            clock.passive, clock.foreground = True, process
            clock.foregrounds[process.pid] = process
        if any(Path(value).name in {"hazard_monitor.py", "km003c_monitor.py"} for value in argv):
            # Process transport startup is a source seam. Do not let the
            # foreground exhaust a logical readiness deadline while a fresh
            # interpreter has not yet scheduled its first real writer tick.
            deadline = REAL_MONOTONIC() + 30
            while not list((root / "passive").glob(f"{process.pid}-*.json")) and process.poll() is None:
                if REAL_MONOTONIC() >= deadline:
                    raise TimeoutError("synthetic instrument process did not register its first sleep")
                REAL_SLEEP(.001)
        if "sampler" in rewrite[5:7]:
            # The process source has an explicit startup barrier. Logical
            # time does not race ahead while its interpreter boots. The
            # unchanged adapter still parses and judges the first frame.
            ready = root / f"sampler-ready-{process.pid}"
            deadline = REAL_MONOTONIC() + 30
            while not ready.exists() and process.poll() is None:
                if REAL_MONOTONIC() >= deadline:
                    raise TimeoutError("synthetic sampler bootstrap did not become ready")
                REAL_SLEEP(0.001)
        if argv[:1] == ("/bin/zsh",):
            clock.passive = True
            clock.foreground = process
            clock.foregrounds[process.pid] = process
        return result
    subprocess.Popen._execute_child = execute_child
    return sources


def make_synthetic_inputs(root):
    """Prepare external JSON inputs, without editing an exported pinned file.

    The overlays rebind model files and library identities. File digests are
    recomputed from the resulting input bytes. No session file exists yet.
    """
    from joulewise.provenance import model_artifact_identity
    pin = root / "pin"
    inputs = root / "inputs"
    inputs.mkdir(exist_ok=True)
    replacements = {}
    token_map = {}
    for label in ("Qwen3-1.7B-4bit", "Qwen3-8B-4bit", "Qwen2.5-1.5B-Instruct-4bit"):
        directory = inputs / "models" / label
        directory.mkdir(parents=True)
        (directory / "model.safetensors").write_bytes(b"R12 synthetic bytes; never loaded as weights\n")
        tokenizer = b'{"synthetic":true,"vocab_size":151643}\n'
        (directory / "tokenizer.json").write_bytes(tokenizer)
        (directory / "tokenizer_config.json").write_text(json.dumps({"chat_template": "R12 synthetic template"}))
        replacements["/Users/edr/jw_models/mlx-community/" + label] = str(directory)
    old_pins = json.loads((pin / "configs/b6/registration/identity_pins.json").read_text())
    for unit in old_pins["units"].values():
        source = unit["model_source"]
        if source in replacements:
            identity = model_artifact_identity(replacements[source])
            replacements[unit["model_artifact_sha256"]] = identity.get("folded_sha256", identity.get("sha256"))
    replacements["aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4"] = hashlib.sha256(tokenizer).hexdigest()
    replacements["87a2728cb8dc9fe424d624542f6060ec05a1d285ebbec578bb078900e33396b5"] = hashlib.sha256(b"R12 synthetic template").hexdigest()
    originals = {path.relative_to(pin).as_posix(): path.read_bytes() for path in (pin / "configs").rglob("*")
                 if path.is_file() and path.suffix in (".json", ".sha256")}
    policy = json.loads((root / "source-policy.json").read_text())

    def transform(value):
        if isinstance(value, dict):
            result = {replacements.get(key, key): transform(item) for key, item in value.items()}
            if policy.get("volume") == "reduced" and all(key in result for key in ("model", "sampling", "hardware_target")):
                result["sampling"]["warmup_seconds"] = 0.0
            if result.get("schema_version") == "joulewise.b6_pack_registration.v1":
                result["stopping"]["end_t0_before"] = "2030-01-01T00:00:00+00:00"
            if isinstance(result.get("ledger_cutoff"), dict):
                result["ledger_cutoff"] = {**result["ledger_cutoff"], "sequence": 0, "head_digest": "0" * 64}
            if "tokenizer_identity" in result and isinstance(result["tokenizer_identity"], dict):
                result["tokenizer_identity"]["class"] = "Tokenizer"
            if "runtime_version" in result and isinstance(result["runtime_version"], dict):
                result["runtime_version"]["version"] = "r12-synthetic"
            if result.get("schema", result.get("schema_version")) == "joulewise.b5_identity_pins.v1":
                result["runtime_versions"] = {"python": ".".join(map(str, sys.version_info[:3])),
                    "packages": {key: "r12-synthetic" for key in result["runtime_versions"]["packages"]}}
            if isinstance(result.get("prompt_text"), str) and isinstance(result.get("prompt_token_ids"), list):
                token_map[result["prompt_text"]] = result["prompt_token_ids"]
            return result
        if isinstance(value, list):
            return [transform(item) for item in value]
        if isinstance(value, str):
            for old, new in replacements.items():
                value = value.replace(old, new)
            return value
        return value

    # Suite configs bind a canonical semantic digest, unlike the raw-file
    # digests in the surrounding input graph. Recompute it with the pinned
    # canonicalizer when identity-bearing prompt metadata changes.
    from joulewise.suite import canonical_effective_manifest, migrate_suite_manifest, suite_manifest_sha256
    for relative, raw in originals.items():
        if relative.endswith(".json"):
            value = json.loads(raw)
            if isinstance(value, dict) and str(value.get("schema_version", "")).startswith("suite_manifest.v"):
                changed = transform(value)
                for canonical in (canonical_effective_manifest, migrate_suite_manifest):
                    replacements[suite_manifest_sha256(canonical(value))] = suite_manifest_sha256(canonical(changed))
    payloads = {}
    for relative, raw in originals.items():
        if not relative.endswith(".json"):
            payloads[relative] = raw
            continue
        value = transform(json.loads(raw))
        encoded = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
        # Preserve all input bytes that did not need a synthetic substitution.
        payloads[relative] = raw if value == json.loads(raw) else encoded
    # Propagate byte references in the input graph (not judgments or outcomes).
    aliases = {hashlib.sha256(raw).hexdigest(): relative for relative, raw in originals.items()}
    for _ in range(20):
        latest = {relative: hashlib.sha256(raw).hexdigest() for relative, raw in payloads.items()}
        digest_map = {digest: latest[relative] for digest, relative in aliases.items()}
        aliases.update({digest: relative for relative, digest in latest.items()})
        changed = False
        for relative, raw in list(payloads.items()):
            text = raw.decode()
            for old, new in digest_map.items():
                text = text.replace(old, new)
            encoded = text.encode()
            if encoded != raw:
                changed = True
                payloads[relative] = encoded
        if not changed:
            break
    else:
        raise ValueError("synthetic input digest graph did not converge")
    overlays = {}
    for relative, raw in payloads.items():
        if raw == originals[relative]:
            continue
        path = inputs / "overlays" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        overlays[str(pin / relative)] = str(path)
    (root / "input-overlays.json").write_text(json.dumps(overlays, indent=2, sort_keys=True) + "\n")
    (inputs / "token-map.json").write_text(json.dumps(token_map, sort_keys=True) + "\n")
    print("synthetic input overlays", len(overlays))
    return 0


def install_engine(root, clock):
    """A tiny synthetic engine library; pinned runtime/event writers remain real."""
    mx = types.ModuleType("mlx.core")
    import importlib.machinery
    import importlib.metadata
    original_version = importlib.metadata.version
    packages = {"mlx", "mlx-lm", "mlx-metal", "numpy", "safetensors", "tokenizers", "transformers"}
    importlib.metadata.version = lambda name: "r12-synthetic" if name in packages else original_version(name)
    mx.__version__ = "r12-synthetic"
    mx.__spec__ = importlib.machinery.ModuleSpec("mlx.core", loader=None)
    class Array:
        def astype(self, dtype):
            return self
    mx.random = SimpleNamespace(normal=lambda shape: Array())
    mx.float16 = object()
    mx.matmul = lambda left, right: Array()
    def active(seconds, power_mw):
        start = clock.ns
        with (root / "engine-intervals.jsonl").open("a") as out:
            out.write(json.dumps({"start_ns": start, "end_ns": start + round(seconds * 1e9), "power_mw": power_mw}) + "\n")
        clock.sleep(seconds)
    def evaluate(*values):
        if len(values) == 1:
            active(0.1, 50000)
    mx.eval = evaluate
    mx.clear_cache = lambda: None
    mx.metal = SimpleNamespace(get_active_memory=lambda: 0, get_peak_memory=lambda: 0,
                               get_cache_memory=lambda: 0, clear_cache=lambda: None)
    package = types.ModuleType("mlx")
    package.__spec__ = importlib.machinery.ModuleSpec("mlx", loader=None, is_package=True)
    package.__path__ = []
    package.core = mx
    sys.modules["mlx"], sys.modules["mlx.core"] = package, mx
    lm = types.ModuleType("mlx_lm")
    lm.__spec__ = importlib.machinery.ModuleSpec("mlx_lm", loader=None)
    lm.__version__ = "r12-synthetic"
    class Tokenizer:
        eos_token_ids = {0}
        vocab_size = 151643
        def __init__(self, source):
            self.name_or_path = source
        def encode(self, text, **kwargs):
            clock.sleep(.001)  # external engine's tokenization latency
            path = root / "inputs/token-map.json"
            if path.exists():
                mapping = json.loads(path.read_text())
                if text in mapping:
                    return mapping[text]
            return [1] * max(1, len(text.split()))
        def decode(self, ids, **kwargs):
            clock.sleep(.001)  # external engine's detokenization latency
            return "x " * len(ids)
    Tokenizer.__module__, Tokenizer.__qualname__ = "r12_engine", "Tokenizer"
    def load(source, **kwargs):
        # The engine's public input, not any controller decision or context.
        # The declared sensor script can keep reference-model requests clean
        # while presenting non-GO idle readings for science-model requests.
        (root / f"model-source-{os.getpid()}.json").write_text(json.dumps({"source": str(source)}) + "\n")
        return SimpleNamespace(source=str(source)), Tokenizer(source), {"eos_token_id": 0}
    lm.load = load
    lm.make_sampler = lambda *args, **kwargs: (lambda x: x)
    policy_path = root / "source-policy.json"
    policy = json.loads(policy_path.read_text()) if policy_path.exists() else {}
    def generate(model, tokenizer, prompt, max_tokens, **kwargs):
        for index in range(max_tokens):
            duration = policy.get("token_first_s", 1.0) if index == 0 else policy.get("token_next_s", .05)
            primary = root / f"primary-{os.getpid()}.json"
            if index == max_tokens - 1 and (max_tokens >= 256 or max_tokens == 1) and policy.get("primary_stream_duration_s") and primary.exists():
                start = json.loads(primary.read_text())["start_ns"]
                target = start + round((policy["primary_stream_duration_s"] - 1.0) * 1e9)
                duration = max(duration, (target - clock.ns) / 1e9)
            active(duration, 10000 if index == 0 else 6000)
            yield SimpleNamespace(token=2, text="x", finish_reason="length" if index == max_tokens - 1 else None)
    lm.stream_generate = generate
    sys.modules["mlx_lm"] = lm


def install_usb_source(root, clock):
    """Supply a libusb object, below the unchanged UsbDevice and Meter code."""
    import ctypes
    from joulewise.external import km003c_usb as usb
    class Library:
        def __init__(self):
            self.queue = []
            self.origin = clock.ns
            self.offset = 0
            self.intervals = []

        def libusb_init(self, pointer):
            pointer._obj.value = 1
            return 0

        def libusb_open_device_with_vid_pid(self, *args):
            return 7

        def libusb_get_device(self, handle):
            return 7

        def libusb_get_device_descriptor(self, device, pointer):
            value = pointer._obj
            value.bcdDevice = 0x0200
            value.iManufacturer, value.iProduct, value.iSerialNumber = 1, 2, 3
            return 0

        def libusb_get_string_descriptor_ascii(self, handle, index, buffer, length):
            raw = {1: b"R12 synthetic", 2: b"KM003C", 3: b"R12-NO-HARDWARE"}[index]
            ctypes.memmove(buffer, raw, len(raw))
            return len(raw)

        def __getattr__(self, name):
            if name in {"libusb_set_configuration", "libusb_claim_interface", "libusb_release_interface",
                        "libusb_close", "libusb_exit", "libusb_reset_device"}:
                return lambda *args: 0
            raise AttributeError(name)

        def libusb_bulk_transfer(self, handle, endpoint, buffer, length, transferred, timeout):
            if endpoint == usb.EP_OUT:
                raw = bytes(buffer[:length])
                kind, tid = raw[0] & 0x7f, raw[1]
                if kind == 0x44:
                    plain = usb.aes_decrypt(usb.MEMORY_KEY, raw[4:])
                    address, size = struct.unpack("<II", plain[:8])
                    data = bytearray((size + 15) // 16 * 16)
                    if address == usb.HWID_ADDR:
                        data[:12] = b"R12-FAKE-USB"
                    elif address == usb.DEVICE_INFO_ADDR:
                        data[16:22] = b"KM003C"
                    elif address == usb.FIRMWARE_INFO_ADDR:
                        data[28:31] = b"2.0"
                    self.queue.extend([bytes([0xc4, tid, 0, 0]) + bytes(16), bytes(data)])
                elif kind == 0x4c:
                    self.queue.append(bytes([0x4c, tid, 2, 0]))
                elif kind == 0x0c:
                    path = root / "engine-intervals.jsonl"
                    if path.exists():
                        with path.open() as source:
                            source.seek(self.offset)
                            for line in source:
                                self.intervals.append(json.loads(line))
                            self.offset = source.tell()
                    self.intervals = [row for row in self.intervals if row["end_ns"] > clock.ns - 180_000_000]
                    payload = bytearray()
                    for index in range(10):
                        point = clock.ns - (9 - index) * 20_000_000
                        power = 10 + sum(row["power_mw"] / 1000 for row in self.intervals
                                         if row["start_ns"] <= point < row["end_ns"])
                        payload.extend(struct.pack("<HHiiHHHH", ((point - self.origin) // 1_000_000) % 65536,
                                                   0, 20_000_000, round(power * 50_000), 0, 0, 0, 0))
                    self.queue.append(bytes([0x41, tid, 0, 0]) + struct.pack("<I", 2 | (10 << 16)) + payload)
                else:
                    self.queue.append(bytes([0x05, tid, 0, 0]))
                transferred._obj.value = length
                return 0
            if not self.queue:
                return usb.LIBUSB_ERROR_TIMEOUT
            raw = self.queue.pop(0)
            ctypes.memmove(buffer, raw, len(raw))
            transferred._obj.value = len(raw)
            return 0
    usb.load_libusb = lambda path=None: Library()


def sampler_source(root, clock, argv):
    """Raw native-format plist stream at the process boundary below its parser."""
    import plistlib
    output = Path(argv[argv.index("-o") + 1])
    interval = int(argv[argv.index("-i") + 1]) * 1_000_000 if "-i" in argv else 100_000_000
    # sudo's -n is not the sampler's finite-count option.
    options = argv[argv.index("/usr/bin/powermetrics") + 1:]
    count = int(options[options.index("-n") + 1]) if "-n" in options else None
    policy = json.loads((root / "source-policy.json").read_text())
    ordinal = 0
    if count is None and "instrument_validation" not in output.parts:
        counter = root / ("source-counter-" + policy.get("scenario", "prerequisite") + ".txt")
        with counter.open("a+") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            stream.seek(0)
            ordinal = int(stream.read() or "0") + 1
            stream.seek(0)
            stream.truncate()
            stream.write(str(ordinal))
    busy = ordinal in policy.get("gpu_busy_primary_ordinals", []) or (
        ordinal > policy.get("gpu_busy_after_primary", float("inf")))
    model_source = root / f"model-source-{os.getppid()}.json"
    if ordinal and policy.get("gpu_busy_science") and model_source.exists():
        busy |= Path(json.loads(model_source.read_text())["source"]).name.startswith("Qwen3-")
    native_offset = policy.get("native_timestamp_offsets_s", {}).get(str(ordinal), 0)
    start = clock.monotonic_ns()
    if count is None:
        (root / f"primary-{os.getppid()}.json").write_text(json.dumps({"start_ns": start, "output": str(output)}) + "\n")
    import signal
    stopping = [False]
    clock.stop_callbacks.append(lambda: stopping.__setitem__(0, True))
    signal.signal(signal.SIGTERM, lambda *args: stopping.__setitem__(0, True))
    signal.signal(signal.SIGINT, lambda *args: stopping.__setitem__(0, True))
    signal_path = root / "engine-intervals.jsonl"
    intervals = []
    offset = 0
    with output.open("wb") as out:
        index = 0
        while count is None or index < count:
            endpoint = start + (index + 1) * interval
            if count is None:
                if index == 0:
                    clock.sleep(interval / 1e9)
                while clock.ns < endpoint and not stopping[0]:
                    REAL_SLEEP(0.001)
                if stopping[0] and clock.ns < endpoint:
                    break
            if signal_path.exists():
                with signal_path.open() as source:
                    source.seek(offset)
                    for line in source:
                        intervals.append(json.loads(line))
                    offset = source.tell()
            gpu_mw = sum(row["power_mw"] * max(0, min(endpoint, row["end_ns"]) - max(endpoint - interval, row["start_ns"]))
                         / interval for row in intervals if row["end_ns"] > endpoint - interval and row["start_ns"] < endpoint)
            if busy:
                gpu_mw += 6000.
            intervals = [row for row in intervals if row["end_ns"] > endpoint]
            wall = (WALL_NS + endpoint - MONO_NS) / 1e9 + native_offset
            document = {"timestamp": datetime.datetime.fromtimestamp(wall, datetime.UTC), "is_delta": True,
                        "elapsed_ns": interval, "thermal_pressure": "Nominal", "hw_model": "Mac15,9",
                        "kern_osversion": "25G83", "processor": {"cpu_power": 500., "gpu_power": gpu_mw, "ane_power": 0.,
                        "combined_power": 500. + gpu_mw,
                        "cpu_energy": 500 * interval / 1e9, "gpu_energy": gpu_mw * interval / 1e9, "ane_energy": 0.,
                        "clusters": [{"name": "E-Cluster", "idle_ratio": .99, "down_ratio": 0., "online_ratio": 1.,
                                      "cpus": [{"cpu": i, "idle_ratio": .99, "down_ratio": 0., "freq_hz": 1020000000.}
                                               for i in range(16)]}]}, "gpu": {"idle_ratio": .999, "freq_hz": 0.}}
            if busy:
                document["gpu"] = {"idle_ratio": 0., "freq_hz": 1500.}
            if "instrument_validation" in output.parts:
                # Calibration's requested source contains rails/thermal and
                # native times; CPU admission is not sampled in that capture.
                document["processor"].pop("clusters")
                document.pop("gpu")
            elif policy.get("volume") == "reduced":
                document["processor"]["clusters"][0]["cpus"] = document["processor"]["clusters"][0]["cpus"][:1]
            if index:
                out.write(b"\0")
            out.write(plistlib.dumps(document))
            out.flush()
            if count is None:
                directory = root / "passive"
                directory.mkdir(exist_ok=True)
                marker = directory / f"{os.getpid()}-sampler.json"
                temporary = marker.with_suffix(".tmp")
                temporary.write_text(json.dumps({"pid": os.getpid(), "next_ns": endpoint + interval}))
                temporary.replace(marker)
            if index == 0:
                (root / f"sampler-ready-{os.getpid()}").write_text("first native frame flushed\n")
            index += 1
    if count is not None:
        clock.sleep(count * interval / 1e9)
    else:
        marker.unlink(missing_ok=True)
    return 0
