"""Shared synthetic integration suite for docs/ops/cluster_contract.md §3.

Import ClusterScenarios, inherit it alongside unittest.TestCase, and supply
the fixture hooks on the leaf class. See the contract for the wiring example.
"""

from __future__ import annotations

import ast
import errno
import hashlib
import importlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from collections.abc import Callable
from contextlib import ExitStack, redirect_stderr, redirect_stdout, suppress
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from joulewise import durable
from scripts import gen_current, launch_align_r0 as fence
from scripts.air import night_results_watch
from tests.git_fixture import init_git_fixture

SOURCE = Path(__file__).resolve().parents[2]
REAL_MONOTONIC = time.monotonic
REAL_TIME = time.time
REAL_KILL, REAL_KILLPG = os.kill, os.killpg
REAL_SLEEP = time.sleep
FAKE_PID = 810001
CRASH_EXIT = 77
PORT_MODULES = {
    "O": (804, "joulewise.span_offload"),
    "C": (807, "joulewise.close_offload"),
    "D": (799, "joulewise.cadence.desk_transport"),
    "Q": (800, "scripts.cadence_controller"),
}
ENTRY_POINTS = {
    "O": SOURCE / "scripts/span_offload.py",
    "C": SOURCE / "scripts/close_offload.py",
    "D": SOURCE / "scripts/air/cadence_desk.py",
}


class Crash(BaseException):
    """Restart fixture. Bypasses application handlers for ordinary errors."""


class DuplicatePointerAccepted(AssertionError):
    """Main selected a pointer despite duplicate numbered items."""


@dataclass(frozen=True)
class Span:
    plan: str
    output: Path

    @property
    def receipt(self) -> Path:
        return self.output / "runner_receipt.json"


@dataclass(frozen=True)
class Result:
    code: int
    stdout: str
    stderr: str

    @property
    def record(self) -> dict:
        document = json.loads(self.stdout.splitlines()[-1])
        if not isinstance(document, dict):
            raise AssertionError("last stdout line must be a JSON object")
        return document


def _dump(path: Path, value) -> None:
    # This channel is fixture input and instrumentation, never an artifact
    # under test. Each subprocess gets a private event directory.
    path.write_text(json.dumps(value), encoding="utf-8")


class Boundary:
    """Clock and PID namespace shared by the member's external fixtures."""

    def __init__(self, root: Path):
        self.root = root

    def get(self, key):
        return json.loads((self.root / key).read_text(encoding="utf-8"))

    def put(self, key, value):
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.root,
                                         delete=False) as pending:
            json.dump(value, pending)
        os.replace(pending.name, self.root / key)

    def now(self):
        return self.get("wall")

    def monotonic(self):
        return self.get("monotonic")

    def step(self, *, wall=0, mono=0):
        self.put("wall", self.now() + wall)
        self.put("monotonic", self.monotonic() + mono)

    def pid_alive(self, pid):
        return pid in self.get("pids") or (self.root / f"owned-{pid}").exists()

    def kill(self, pid, sig):
        pids = self.get("pids")
        if not self.pid_alive(pid):
            raise ProcessLookupError(errno.ESRCH, "no synthetic process", pid)
        if sig:
            self.put("signals", [*self.get("signals"), [pid, sig]])
            self.put("pids", [item for item in pids if item != pid])
            (self.root / f"owned-{pid}").unlink(missing_ok=True)


@dataclass
class FixtureHooks:
    """Bind synthetic inputs and observations to the particular member build.

    configure creates configs, keys and authority records under World.root.
    prepare adds synthetic input facts or changes external responses.
    observe reads production records, refs, and captured boundary calls.
    invoke adapts production entry points that have no fixed signature yet.
    child_setup supplies platform observations inside a real CLI subprocess.
    controller constructs the imported production Controller with real
    neighbours. Its environment must route external commands into World.
    """

    configure: Callable[[World], None] | None = None
    prepare: Callable[..., None] | None = None
    observe: Callable[..., object] | None = None
    controller: Callable[[World, ModuleType], object] | None = None
    invoke: Callable[..., object] | None = None
    child_setup: Callable[[Boundary], None] | None = None


@dataclass
class World:
    test: unittest.TestCase
    stack: ExitStack
    hooks: FixtureHooks
    ports: dict[str, ModuleType]
    root: Path = field(init=False)
    boundary: Boundary = field(init=False)

    def __post_init__(self):
        self.root = Path(self.stack.enter_context(
            tempfile.TemporaryDirectory(prefix="jw-cluster-"))).resolve()
        self.host, self.state = self.root / "host", self.root / "state"
        self.stage, self.markers = self.root / "stage", self.root / "markers"
        self.cloud, self.ssd = self.root / "cloud", self.root / "ssd"
        self.outputs, self.controls = self.root / "outputs", self.root / "boundary"
        self.bin = self.root / "bin"
        self.campaign, self.worktrees = self.root / "campaign", self.root / "worktrees"
        for directory in (self.host, self.state, self.stage, self.markers, self.cloud,
                          self.ssd, self.outputs, self.controls, self.bin,
                          self.campaign, self.worktrees):
            directory.mkdir()
        self.boundary = Boundary(self.controls)
        for key, value in (("wall", 1794950000), ("monotonic", 1000),
                           ("pids", [FAKE_PID]), ("signals", [])):
            self.boundary.put(key, value)
        self.repo, self.remote = self.root / "repo", self.root / "remote.git"
        self.offload_config = self.root / "offload.json"
        self.air_config = self.root / "air.json"
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("GIT_", "GH_", "SSH_", "PYTHON"))}
        self.env.update(HOME=str(self.root), TMPDIR=str(self.root),
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull,
                        GIT_ALLOW_PROTOCOL="file", JW_CLUSTER_BOUNDARY=str(self.controls))
        self.env["PATH"] = os.pathsep.join((str(self.bin), os.defpath, "/opt/homebrew/bin"))
        if hook := self.hooks.child_setup:
            # Discovery can import leaves relative to tests/. The child
            # starts at the repository root and imports them as tests.*.
            hook_file = Path(sys.modules[hook.__module__].__file__).resolve()
            hook_module = ".".join(hook_file.relative_to(SOURCE).with_suffix("").parts)
            self.env["JW_CLUSTER_CHILD_SETUP"] = f"{hook_module}:{hook.__name__}"
        self.command("pgrep", "raise SystemExit(1)")
        self.repo.mkdir()
        self.remote.mkdir()
        with patch.dict(os.environ, self.env, clear=True):
            init_git_fixture(self.repo, "-q", "--template=")
            init_git_fixture(self.remote, "-q", "--bare", "--template=")
        self.git("remote", "add", "origin", str(self.remote), repo=self.repo)
        self.checkpoints = []
        self.invocations = []
        self.actions = {}
        self.controller = None
        self.stack.enter_context(patch.object(durable, "checkpoint", self.checkpoint))
        self.stack.enter_context(patch.object(os, "kill", self.boundary.kill))
        self.stack.enter_context(patch.object(os, "killpg", self.boundary.kill))
        self.stack.enter_context(patch.object(time, "time", self.boundary.now))
        self.stack.enter_context(patch.object(time, "monotonic", self.boundary.monotonic))
        if self.hooks.configure:
            self.hooks.configure(self)

    def git(self, *args, repo=None, check=True):
        env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull,
                   GIT_ALLOW_PROTOCOL="file", GIT_TERMINAL_PROMPT="0")
        return subprocess.run(["git", "-C", str(repo or self.root), *args], env=env,
                              capture_output=True, text=True, check=check)

    def command(self, name, body):
        """Install a synthetic external command and return its absolute path."""
        if name != Path(name).name or name in {"", ".", ".."}:
            raise ValueError("expected a synthetic command basename")
        script = self.bin / name
        script.write_text(f"#!{sys.executable}\n{body}\n", encoding="utf-8")
        script.chmod(0o700)
        return script

    def span(self, plan="synthetic-s01", *, receipt=True):
        output = self.outputs / plan
        output.mkdir()
        (output / "synthetic.txt").write_bytes(b"synthetic span bytes\n")
        span = Span(plan, output)
        if receipt:
            _dump(span.receipt, {"plan": plan})
        return span

    def prepare(self, **inputs):
        if not self.hooks.prepare:
            raise AssertionError(f"missing fixture.prepare for {', '.join(inputs)}")
        self.hooks.prepare(self, **inputs)

    def observe(self, name, **context):
        if not self.hooks.observe:
            raise AssertionError(f"missing fixture.observe for {name}")
        return self.hooks.observe(self, name, **context)

    def invoke(self, name, **inputs):
        if not self.hooks.invoke:
            raise AssertionError(f"missing fixture.invoke for {name}")
        return self.hooks.invoke(self, name, **inputs)

    def checkpoint(self, name):
        self.checkpoints.append(name)
        if action := self.actions.pop(name, None):
            action()

    def at(self, name, action):
        if name in self.actions:
            raise AssertionError(f"checkpoint already armed: {name}")
        self.actions[name] = action

    def fault_at(self, name, code):
        def fail():
            raise OSError(code, os.strerror(code))
        self.at(name, fail)

    def crash_at(self, name):
        def crash():
            raise Crash(name)
        self.at(name, crash)

    def check_checkpoints(self):
        self.test.assertFalse(self.actions, f"production did not reach checkpoints: {sorted(self.actions)}")

    def stand(self, *, purpose="cadence-controller:synthetic", pid=FAKE_PID):
        record = {"purpose": purpose, "pid": pid, "deadline": self.boundary.now() + 900}
        with fence.fence_lock(self.host):
            fence.write_fence(self.host, record)
        return record

    def read_fence(self):
        with fence.fence_lock(self.host):
            return fence.read_fence(self.host)

    def marker(self, span):
        return self.markers / f"{span.plan}.ok"

    def record(self, span, name):
        path = self.state / "spans" / span.plan / f"{name}.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def config(self):
        return self.ports["O"].load_mbp_config(self.offload_config)

    def evidence(self, span, *, require_closed=True):
        return self.ports["O"].copy_evidence(self.config(), span.plan, out_path=span.output,
                                               require_closed=require_closed)

    def pending(self):
        return self.ports["O"].pending_transfers(self.config())

    def offload(self, span, *args):
        return self.cli("O", "offload", "--config", self.offload_config,
                        "--plan", span.plan, "--span-dir", span.output, *args)

    def close(self, span, *args, owner=None, mode="self", receipt=None, retire=()):
        verb = "reclaim" if receipt is not None else "after-check"
        argv = [verb, "--config", self.offload_config, "--span-dir", span.output,
                "--deadline-epoch", str(self.boundary.now() + 300)]
        if receipt is not None:
            argv.extend(["--ssd-receipt", receipt])
        else:
            argv.extend(["--plan", span.plan])
        if mode is not None:
            argv.extend(["--fence-mode", mode])
        if owner is not None:
            argv.extend(["--fence-purpose", owner["purpose"], "--fence-pid", str(owner["pid"]),
                         "--fence-deadline-epoch", str(owner["deadline"])])
        for plan in retire:
            argv.extend(["--retire", plan])
        return self.cli("C", *argv, *args)

    def ssd_copy(self, span):
        result = self.cli("O", "ssd-copy", "--config", self.air_config, "--plan", span.plan,
                          "--marker", self.marker(span), "--ssd-root", self.ssd)
        self.test.assertEqual(result.code, 0, result)
        return self.ssd / "span-archives" / span.plan / "ssd.ok.json"

    def hold(self, *args):
        return self.cli("C", "hold", *args)

    def cli(self, port, *args):
        script = ENTRY_POINTS[port]
        if port not in self.ports:
            raise AssertionError(f"production port {port} is not bound")
        args = [os.fspath(arg) for arg in args]
        if port == "C" and args[:1] in (["after-check"], ["reclaim"]):
            for flag, path in (("--campaign-root", self.campaign),
                               ("--work-root", self.worktrees),
                               ("--fence", self.host / fence.FENCE_NAME)):
                supplied = []
                for index, arg in enumerate(args):
                    option, sep, value = arg.partition("=")
                    if option == flag:
                        supplied.append(value if sep else args[index + 1])
                if supplied:
                    self.test.assertEqual(supplied, [str(path)])
                else:
                    args.extend((flag, str(path)))
        work = Path(tempfile.mkdtemp(prefix="invocation-", dir=self.root))
        result = self.process(_child_argv(script, self.controls, work, args), work)
        self.invocations.append((port, tuple(args), result))
        return result

    def member_argv(self, argv):
        """Run the controller's real member command with shared checkpoints."""
        argv = [os.fspath(arg) for arg in argv]
        for port, script in ENTRY_POINTS.items():
            matches = [index for index, arg in enumerate(argv[:3])
                       if Path(arg).name == script.name and
                       (SOURCE / arg).resolve() == script]
            if matches:
                return self.cli(port, *argv[matches[0] + 1:])
        raise AssertionError("expected a production offload, close, or desk command")

    def close_call(self, span=None):
        for port, argv, result in reversed(self.invocations):
            if port == "C" and (span is None or str(span.output) in argv):
                return argv, result
        raise AssertionError("real close subprocess was not observed")

    def process(self, argv, work):
        # A close remains a real subprocess. Checkpoint responses are sent
        # over private files, so the test never sends a Unix signal.
        deadline = REAL_MONOTONIC() + 45
        with ExitStack() as process_stack:
            stdout = process_stack.enter_context((work / "stdout").open("w+"))
            stderr = process_stack.enter_context((work / "stderr").open("w+"))
            proc = subprocess.Popen(argv, cwd=SOURCE, env=self.env, stdout=stdout, stderr=stderr)
            pid_ticket = self.controls / f"owned-{proc.pid}"
            pid_ticket.touch()
            process_stack.callback(pid_ticket.unlink, missing_ok=True)
            sequences = {work: 0}
            while True:
                exited = proc.poll() is not None
                for worker in work.rglob("worker-*"):
                    sequences.setdefault(worker, 0)
                for channel, sequence in sequences.items():
                    event = channel / f"event-{sequence}"
                    if event.exists():
                        response = {}
                        try:
                            self.checkpoint(event.read_text(encoding="utf-8"))
                        except Crash:
                            response["crash"] = True
                        except OSError as error:
                            response["errno"] = error.errno
                        finally:
                            pending = channel / "reply-tmp"
                            _dump(pending, response)
                            pending.rename(channel / f"reply-{sequence}")
                        sequences[channel] += 1
                if exited:
                    break
                if REAL_MONOTONIC() > deadline:
                    raise AssertionError(f"synthetic subprocess exceeded its deadline: {argv[4]}")
                REAL_SLEEP(0.005)
            for channel in sequences:
                violation = channel / "boundary-violation"
                self.test.assertFalse(violation.exists(),
                                      violation.read_text() if violation.exists() else "")
                if channel != work:
                    if (pid := channel / "pid").exists():
                        ticket = self.controls / f"owned-{int(pid.read_text())}"
                        ticket.unlink(missing_ok=True)
                    self.test.assertTrue((channel / "boundary-ready").is_file(),
                                         "close worker did not install the synthetic boundary")
            stdout.seek(0)
            stderr.seek(0)
            return Result(proc.returncode, stdout.read(), stderr.read())

    def restart(self):
        if not self.hooks.controller:
            raise AssertionError("missing fixture.controller")
        module = self.ports["Q"]
        self.controller = self.hooks.controller(self, module)
        self.test.assertIsInstance(self.controller, module.Controller)
        self.test.assertIs(type(self.controller).tick, module.Controller.tick)
        return self.controller

    def tick(self):
        return (self.controller or self.restart()).tick()

    def assert_gate(self, state, reason=None):
        self.test.assertEqual(self.observe("gate_state"), state)
        if reason:
            self.test.assertIn(reason, self.observe("gate_reasons"))

    def no_arm(self, span):
        self.test.assertIsNone(self.record(span, "intent"))
        self.test.assertFalse(self.observe("bootstraps"))

    def fence_probe(self):
        program = (
            "from pathlib import Path; from scripts.launch_align_r0 import fence_lock, read_fence;"
            "\ndef probe(root):\n with fence_lock(root):\n  print(read_fence(root))"
            "\nimport sys\nprobe(Path(sys.argv[1]))"
        )
        start = REAL_MONOTONIC()
        process = subprocess.Popen([sys.executable, "-B", "-c", program, str(self.host)],
                                   cwd=SOURCE, env=self.env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
        output, error = process.communicate(timeout=5)
        self.test.assertEqual(process.returncode, 0, error)
        self.test.assertLessEqual(REAL_MONOTONIC() - start, 5)
        record = ast.literal_eval(output)
        self.test.assertEqual(record, fence.read_fence(self.host))
        return record


def _child_argv(script, controls, work, args):
    return [sys.executable, "-B", "-c", "from tests.contract.cluster import _child; _child()",
            str(script), str(controls), str(work), *args]


def _worker_boundary(boundary, work):
    """Trip before an escaped native clock or process signal can run."""
    def refuse(name):
        (work / "boundary-violation").write_text(name, encoding="utf-8")
        raise AssertionError(f"close worker escaped the synthetic boundary: {name}")

    def audit(event, args):
        if event in {"os.kill", "os.killpg"}:
            refuse(event)

    def profile(frame, event, target):
        if event != "c_call":
            return
        if target in (REAL_KILL, REAL_KILLPG):
            refuse(target.__name__)
        if target in (REAL_TIME, REAL_MONOTONIC) and frame.f_globals is not globals():
            refuse(target.__name__)

    import threading

    subprocess._time = threading._time = boundary.monotonic
    sys.addaudithook(audit)
    threading.setprofile(profile)
    sys.setprofile(profile)

    def verify():
        if (time.time != boundary.now or time.monotonic != boundary.monotonic
                or os.kill != boundary.kill or os.killpg != boundary.kill):
            refuse("clock or signal implementation changed")

    return verify


def _child():
    """Enter a real CLI with a synthetic PID namespace and checkpoint IPC."""
    import runpy

    script, controls, work, *args = sys.argv[1:]
    work = Path(work)
    boundary = Boundary(Path(controls))
    os.kill = os.killpg = boundary.kill
    # Member fixtures can additionally inject provider components using
    # external-command paths, never by replacing the production CLI.
    from tests import host_command_guard
    host_command_guard.install()
    time.time, time.monotonic = boundary.now, boundary.monotonic
    verify_worker = _worker_boundary(boundary, work) if "--_worker" in args else None
    sequence = 0

    def checkpoint(name):
        nonlocal sequence
        if verify_worker:
            verify_worker()
        pending = work / "event-tmp"
        pending.write_text(name, encoding="utf-8")
        pending.rename(work / f"event-{sequence}")
        reply = work / f"reply-{sequence}"
        sequence += 1
        deadline = REAL_MONOTONIC() + 10
        while not reply.exists():
            if REAL_MONOTONIC() > deadline:
                raise RuntimeError("checkpoint response timed out")
            REAL_SLEEP(0.005)
        response = json.loads(reply.read_text(encoding="utf-8"))
        if response.get("crash"):
            os._exit(CRASH_EXIT)
        if "errno" in response:
            code = response["errno"]
            raise OSError(code, os.strerror(code))

    durable.checkpoint = checkpoint
    popen = subprocess.Popen

    def check_worker_launch(event, arguments):
        if event == "subprocess.Popen":
            _, argv, _, _ = arguments
            if isinstance(argv, (list, tuple)) and "--_worker" in argv:
                if list(argv[:4]) != _child_argv(script, controls, work, [])[:4]:
                    (work / "boundary-violation").write_text("unwrapped close worker")
                    raise AssertionError("close worker launch bypassed the synthetic boundary")

    def supervised_worker(argv, *positional, **kwargs):
        if not isinstance(argv, (list, tuple)) or "--_worker" not in argv:
            return popen(argv, *positional, **kwargs)
        executable, flag, entry, *worker_args = map(os.fspath, argv)
        if (executable, flag, Path(entry).name) != (sys.executable, "-B", "close_offload.py"):
            (work / "boundary-violation").write_text("unexpected close worker command")
            raise AssertionError("unexpected close worker command")
        channel = Path(tempfile.mkdtemp(prefix="worker-", dir=work))
        child = popen(_child_argv(entry, controls, channel, worker_args), *positional, **kwargs)
        (boundary.root / f"owned-{child.pid}").touch()
        (channel / "pid").write_text(str(child.pid))
        return child

    sys.addaudithook(check_worker_launch)
    subprocess.Popen = supervised_worker
    if setup := os.environ.get("JW_CLUSTER_CHILD_SETUP"):
        module, _, name = setup.partition(":")
        getattr(importlib.import_module(module), name)(boundary)
    sys.argv = [script, *args]
    if verify_worker:
        verify_worker()
        (work / "boundary-ready").touch()
    try:
        runpy.run_path(script, run_name="__main__")
    finally:
        if verify_worker:
            verify_worker()


SCENARIOS = {}


def scenario(identifier, ports, *dependencies):
    def register(function):
        if identifier in SCENARIOS:
            raise RuntimeError(f"duplicate scenario {identifier}")
        SCENARIOS[identifier] = (tuple(ports), tuple("".join(dependencies)), function)
        return function
    return register


def _present(name):
    try:
        return importlib.util.find_spec(name) is not None
    except ModuleNotFoundError as error:
        if error.name == name or name.startswith(f"{error.name}."):
            return False
        raise


class ClusterScenarios:
    """Discovery mixin. Each leaf class names the ports it requires."""

    required_ports = ()
    select_main = False
    fixture_hooks = FixtureHooks()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        unknown = set(cls.required_ports).difference(PORT_MODULES)
        if unknown:
            raise ValueError(f"unrecognized cluster ports: {sorted(unknown)}")
        for identifier, (ports, dependencies, exercise) in SCENARIOS.items():
            if cls.select_main and identifier not in MAIN_CASES:
                continue
            if cls.required_ports and identifier in MAIN_CASES:
                continue
            name = f"test_{identifier.replace('-', '_')}"
            setattr(cls, name, cls._case(identifier, ports + dependencies, exercise))

    @classmethod
    def _case(cls, identifier, ports, exercise):
        missing = tuple(port for port in ports if not _present(PORT_MODULES[port][1]))
        required = set(missing) & set(cls.required_ports)
        absent = next(iter(missing), None)
        reason = f"seam owner PR #{PORT_MODULES[absent][0]} not merged" if absent else None

        def run(self):
            if required:
                self.fail(f"required production ports absent: {', '.join(sorted(required))}")
            if reason:
                self.fail(reason)
            if (identifier not in MAIN_CASES and not cls.fixture_hooks.configure
                    and identifier not in {"X-16", "X-18"}):
                self.fail("present production ports require fixture_hooks.configure")
            modules = {port: importlib.import_module(PORT_MODULES[port][1]) for port in ports}
            with ExitStack() as stack:
                world = World(self, stack, cls.fixture_hooks, modules)
                exercise(self, world)
                world.check_checkpoints()

        run.__name__ = f"test_{identifier.replace('-', '_')}"
        run.__doc__ = f"{identifier}" + (f" ({reason})" if reason else "")
        if reason and not required:
            # Limit expected failure to the absent-owner result. Tree
            # inspection for X-16 has a separate entry below.
            def unavailable(self):
                self.fail(reason)
            unavailable.__name__ = run.__name__
            unavailable.__doc__ = run.__doc__
            return unittest.expectedFailure(unavailable)
        if identifier == "A-12":
            def known_failure(self):
                try:
                    run(self)
                except DuplicatePointerAccepted:
                    raise
                except BaseException:
                    # Infrastructure failures must remain real failures.
                    self._outcome.expecting_failure = False
                    raise
            known_failure.__name__ = run.__name__
            known_failure.__doc__ = "A-12 (main accepts duplicate numbered pointer items)"
            return unittest.expectedFailure(known_failure)
        return run


MAIN_CASES = {"A-09", "A-12"}


def _offload_sources():
    # Read-only inventory of production source filenames. No branch contents
    # or tracked fixture bytes are read by this check.
    tracked = subprocess.run(["git", "-C", str(SOURCE), "ls-files", "-z", "--",
                              "joulewise", "scripts"], text=True, capture_output=True,
                             check=True).stdout.split("\0")
    return [path for path in tracked if Path(path).name == "span_offload.py"
            and not path.startswith("scripts/")]


def _ok(test, result):
    test.assertEqual(result.code, 0, result)
    return result


def _clear(test, world, span, *, require_closed=True):
    test.assertEqual(world.evidence(span, require_closed=require_closed).status, "CLEAR")


def _copied(test, world, span):
    _clear(test, world, span)
    test.assertTrue(world.marker(span).is_file())
    test.assertEqual(world.record(span, "close")["copy"]["marker_sha256"],
                     hashlib.sha256(world.marker(span).read_bytes()).hexdigest())
    test.assertNotIn(span.plan, world.observe("copy_due"))


def _armed(test, world, span):
    test.assertEqual(world.record(span, "arm")["status"], "LIVE")
    test.assertIn(span.plan, world.observe("bootstraps"))


def _closed(test, result):
    test.assertEqual(result.code, 0, result)
    test.assertEqual(result.record["status"], "CLOSE_OK")
    test.assertIs(result.record["pending"]["clear"], True)


def _old_output(world):
    older = world.span("synthetic-s01")
    recent = world.span("synthetic-s02")
    check = world.span("synthetic-s03")
    world.prepare(gap=(older, recent, check))
    return older, recent, check


@scenario("X-01", "OCQ")
def _clean_close(test, w):
    closed, successor = w.span(), w.span("synthetic-s02")
    w.prepare(closed=closed, queued=successor)
    w.tick()
    argv, result = w.close_call(closed)
    _closed(test, result)
    test.assertIn("--fence-mode", argv)
    test.assertEqual(argv[argv.index("--fence-mode") + 1], "owner")
    _copied(test, w, closed)
    w.tick()
    _armed(test, w, successor)


@scenario("X-02", "OQ")
def _marker_gate(test, w):
    span = w.span()
    w.prepare(closed=span)
    _ok(test, w.offload(span))
    _clear(test, w, span)
    test.assertEqual(w.invoke("copy_gate_problems", span=span), [])
    # A maliciously underspecified input is intentional in this negative case.
    w.marker(span).unlink()
    _dump(w.marker(span), {"plan": span.plan, "ciphertext": {"size": 1}})
    test.assertEqual(w.evidence(span).status, "INVALID")
    test.assertTrue(w.invoke("copy_gate_problems", span=span))


@scenario("X-03", "CQ", "O")
def _owner_close(test, w, *, retry=False):
    span = w.span()
    w.prepare(closed=span)
    ctl = w.restart()
    ctl.hold_fence()
    owner = w.read_fence()
    original = (w.host / fence.FENCE_NAME).read_bytes()
    test.assertTrue(owner["purpose"].startswith("cadence-controller:"))
    result = w.close(span, mode="owner", owner=owner)
    _closed(test, result)
    test.assertEqual((w.host / fence.FENCE_NAME).read_bytes(), original)
    if retry:
        _closed(test, w.close(span, mode="owner", owner=owner))
        test.assertEqual((w.host / fence.FENCE_NAME).read_bytes(), original)


@scenario("X-04", "C", "O")
def _mutex(test, w):
    span = w.span()
    owner = w.stand()
    # Probe from a separate process while the real close is at every
    # instrumented boundary between acquisition and completion.
    points = ("close.fence_acquired", "close.before_offload", "close.before_exit")
    for name in points:
        w.at(name, w.fence_probe)
    _closed(test, w.close(span, mode="owner", owner=owner))
    test.assertEqual(w.read_fence(), owner)


@scenario("X-05", "CQ", "O")
def _changed_fence(test, w):
    for change in ("replacement", "expiry", "dead_pid"):
        with test.subTest(change=change), ExitStack() as stack:
            case = World(test, stack, w.hooks, w.ports)
            _fence_lapse(test, case, change)


def _fence_lapse(test, w, change):
    w.prepare(retirement_batch=True)
    def lapse():
        if change == "replacement":
            w.stand(purpose="cadence-controller:other")
        elif change == "expiry":
            owner = w.read_fence()
            w.boundary.step(wall=owner["deadline"] - w.boundary.now() + 1)
        else:
            owner = w.read_fence()
            w.boundary.put("pids", [pid for pid in w.boundary.get("pids") if pid != owner["pid"]])
    w.at("close.between_destructive_steps", lapse)
    w.tick()
    result = w.close_call()[1]
    test.assertEqual(result.code, 4, result)
    test.assertIn("FENCE_CHANGED", result.stdout + result.stderr)
    test.assertFalse(w.observe("deletions_after", checkpoint="close.between_destructive_steps"))
    w.assert_gate("HALT", "ARM_INDETERMINATE")
    w.check_checkpoints()


@scenario("X-06", "C", "O")
def _self_close(test, w):
    span = w.span()
    test.assertIsNone(w.read_fence())
    for name in ("close.fence_acquired", "close.before_offload", "close.before_exit"):
        w.at(name, lambda: test.assertTrue(w.fence_probe()["purpose"].startswith("close-offload:")))
    _closed(test, w.close(span))
    test.assertIsNone(w.read_fence())
    blocked = w.span("synthetic-s02")
    owner = w.stand()
    result = w.close(blocked)
    test.assertEqual(result.code, 4, result)
    test.assertIn("DESK_FENCE_PRESENT", result.stdout + result.stderr)
    test.assertEqual(w.read_fence(), owner)
    test.assertFalse(w.marker(blocked).exists())
    test.assertFalse((w.stage / blocked.plan).exists())


@scenario("X-07", "OC")
def _required_mode(test, w):
    span = w.span()
    test.assertEqual(w.close(span, mode=None).code, 2)
    owner = w.stand()
    test.assertEqual(w.close(span, mode=None, owner=owner).code, 2)
    test.assertEqual(w.close(span, mode="self").code, 4)
    _closed(test, w.close(span, mode="owner", owner=owner))


@scenario("X-08", "OCQ", "D")
def _desk_debt(test, w):
    old, recent, check = _old_output(w)
    w.prepare(closed=recent, earlier=old, hand_gates="open")
    w.tick()
    test.assertTrue(old.output.is_dir())
    test.assertNotIn(old.plan, w.observe("retire_plans"))
    w.prepare(closed=check, earlier=old, q1=True, hand_gates="released", real_verdict=True)
    w.tick()
    test.assertIn(old.plan, w.observe("retire_plans"))
    test.assertFalse(old.output.exists())


@scenario("X-09", "CQ", "O")
def _campaign_hold(test, w):
    _ok(test, w.hold("add", "--id", "look", "--campaign", "cl-dev-05",
                     "--reason", "synthetic hold", "--by", "contract"))
    span = w.span("cl-dev-05-s01")
    check = w.span("cl-dev-05-s02")
    w.prepare(campaign="cl-dev-05", gap=(span, check))
    _closed(test, w.close(span))
    ctl = w.restart()
    ctl.hold_fence()
    result = w.close(check, mode="owner", owner=w.read_fence(), retire=(span.plan,))
    _closed(test, result)
    test.assertTrue(span.output.is_dir())
    may_retire, reason = w.ports["C"].may_retire(
        w.config(), span.output, span.plan, named={span.plan})
    test.assertFalse(may_retire)
    test.assertTrue(reason)
    test.assertIn(reason, result.stdout)


@scenario("X-10", "OC")
def _deleting_verbs(test, w):
    span = w.span()
    result = w.cli("O", "--help")
    _ok(test, result)
    test.assertEqual(set(re.findall(r"[a-z][a-z-]+", re.search(r"\{([^{}]+)\}", result.stdout)[1])),
                     {"offload", "pending", "evidence", "ssd-copy", "pull", "keygen"})
    for verb in ("close", "offload", "pending", "bogus"):
        test.assertEqual(w.cli("C", verb, "--span-dir", span.output).code, 2)
    test.assertEqual(w.cli("O", "close", "--span-dir", span.output).code, 2)
    test.assertTrue(span.output.is_dir())


@scenario("X-11", "OQ", "C")
def _stranded_copy(test, w):
    span = w.span(receipt=False)
    w.prepare(stranded=span, require_file="synthetic.txt")
    w.tick()
    test.assertEqual(w.record(span, "close")["status"], "STRANDED")
    test.assertIn("--require-file", w.close_call(span)[0])
    _clear(test, w, span, require_closed=False)
    test.assertNotIn(span.plan, w.observe("copy_due"))


@scenario("X-12", "OQ")
def _fresh_pending(test, w):
    span = w.span()
    w.prepare(queued=span)
    for pending in ("pending", "unknown", "failed"):
        w.prepare(pending=pending)
        w.tick()
        w.no_arm(span)
        w.assert_gate("HOLD")
    w.prepare(pending="clear")
    w.tick()
    _armed(test, w, span)
    calls = w.observe("arm_boundary_log")
    test.assertLess(calls.index("authority:2"), calls.index("pending:clear"))
    test.assertLess(calls.index("pending:clear"), calls.index("bootstrap"))


@scenario("X-13", "Q", "O")
def _preflight(test, w):
    span = w.span()
    for field, fault, diagnostic in (
        ("offload_config", "missing", "PREFLIGHT: missing offload_config"),
        ("key_second_copy_attested_sha256", "mismatch",
         "PREFLIGHT: key_second_copy_attested_sha256 does not match recipient_sha256"),
    ):
        with test.subTest(field=field):
            w.prepare(queued=span, bad_preflight=(field, fault))
            result = w.invoke("controller_startup")
            test.assertNotEqual(result.code, 0)
            test.assertIn(diagnostic, (result.stderr + "\n" + result.stdout).splitlines())
            w.no_arm(span)


@scenario("X-14", "DQ")
def _warning_listing(test, w):
    w.prepare(desk_due=True, ref_listing="warning-empty")
    w.tick()
    w.assert_gate("HOLD", "FETCH_FAILED")
    test.assertNotIn("--history-empty", w.observe("desk_argv"))


@scenario("X-15", "DQ")
def _missing_mbp_ref(test, w):
    span = w.span()
    w.prepare(bundle_pushed=span, real_verdict=True)
    w.tick()
    ref = f"refs/heads/cadence-desk-mbp/{span.plan}"
    first = w.observe("verdict_sha256", span=span)
    test.assertTrue(w.record(span, "close")["mbp_desk"]["published"])
    for differs in (False, True):
        w.git("update-ref", "-d", ref, repo=w.repo)
        w.prepare(change_real_desk_input=differs)
        w.tick()
        if differs:
            w.assert_gate("HALT")
        else:
            test.assertEqual(w.observe("verdict_sha256", span=span), first)
            w.git("rev-parse", "--verify", ref, repo=w.repo)


@scenario("X-16", "OCDQ")
def _one_backend(test, w):
    test.assertEqual(_offload_sources(), ["joulewise/span_offload.py"])
    code = ast.parse(Path(w.ports["Q"].__file__).read_text(encoding="utf-8"))
    imports = any(
        isinstance(node, ast.ImportFrom) and
        (node.module == "joulewise.span_offload" or
         node.module == "joulewise" and any(alias.name == "span_offload" for alias in node.names))
        or isinstance(node, ast.Import) and any(alias.name == "joulewise.span_offload" for alias in node.names)
        for node in ast.walk(code)
    )
    test.assertTrue(imports, "controller must import the canonical offload module")


@scenario("X-17", "OCQ", "D")
def _cycle(test, w):
    spans = (w.span(), w.span("synthetic-f0"), w.span("synthetic-s02"))
    w.prepare(queue=spans, real_verdict=True)
    for span in spans:
        w.tick()
        _armed(test, w, span)
        w.prepare(runner_ended=span)
        w.tick()
        _copied(test, w, span)
        points = w.observe("commit_points", span=span)
        expected = ["notice", "intent", "launch_fence", "bootstrap", "arm",
                    "check", "bundle_ref", "verdict_ref", "marker", "copy_accepted"]
        test.assertEqual([point for point in points if point in expected], expected)


@scenario("X-18", "D")
def _desk_history_warning(test, w):
    prefix = "refs/heads/cadence-desk-final"
    with patch.dict(os.environ, w.env, clear=True):
        w.git("-c", "user.name=Contract Fixture", "-c", "user.email=contract@example.invalid",
              "commit", "--allow-empty", "-m", "Synthetic desk fixture", repo=w.repo)
        ref = f"{prefix}/synthetic-s01"
        w.git("update-ref", ref, "HEAD", repo=w.repo)
        transport = w.ports["D"]
        test.assertEqual(transport.list_history_refs(w.repo, prefix), [ref])
        (w.repo / ".git" / prefix / "synthetic-s02").write_text("broken synthetic ref\n")
        with test.assertRaisesRegex(transport.TransportRefusal, "history listing .* failed"):
            transport.list_history_refs(w.repo, prefix)


@scenario("A-01", "OQ")
def _astra_marker(test, w):
    _marker_gate(test, w)


@scenario("A-02", "CQ", "O")
def _astra_owner(test, w):
    _owner_close(test, w, retry=True)


@scenario("A-03", "Q")
def _notice_deadline(test, w):
    span = w.span()
    w.prepare(queued=span)
    w.tick()
    _armed(test, w, span)
    notice = w.observe("arm_notice", span=span)
    test.assertEqual(notice["plan_id"], span.plan)
    test.assertGreater(notice["close_deadline_epoch"], notice["t0"])
    w.prepare(watcher_advance_to=notice["close_deadline_epoch"] + 301)
    test.assertIn(span.plan, w.observe("watcher_alarm_subjects"))


@scenario("A-04", "DQ")
def _ref_lock(test, w):
    span = w.span()
    w.prepare(bundle_pushed=span)
    lock = w.repo / ".git" / "refs" / "heads" / "cadence-desk-mbp" / f"{span.plan}.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.touch()
    try:
        kwargs = w.observe("publish_kwargs", span=span)
        desk = w.ports["D"]
        with test.assertRaises(desk.TransportRefusal):
            desk.publish_verdict(**kwargs)
        w.tick()
        test.assertFalse(w.record(span, "close").get("mbp_desk", {}).get("published"))
    finally:
        lock.unlink()
    w.tick()
    test.assertTrue(w.record(span, "close")["mbp_desk"]["published"])


@scenario("A-05", "Q")
def _monotonic_lease(test, w):
    span = w.span()
    w.prepare(queued=span)
    w.at("controller.authority_read_complete", lambda: w.boundary.step(wall=-60, mono=130))
    w.tick()
    test.assertFalse(w.observe("bootstraps"))


@scenario("A-06", "DQ")
def _remote_disappears(test, w):
    span = w.span()
    w.prepare(remote_verdict=span)
    w.tick()
    w.git("update-ref", "-d", f"refs/heads/cadence-desk-final/{span.plan}", repo=w.remote)
    w.tick()
    test.assertEqual(w.observe("remote_verdict_state", span=span), "DISAPPEARED")
    test.assertFalse(w.observe("tracking_ref_exists", span=span))
    w.assert_gate("HALT")


@scenario("A-07", "OC")
def _stream_reclaim(test, w):
    for corrupt in (False, True):
        with test.subTest(corrupt=corrupt), ExitStack() as stack:
            case = World(test, stack, w.hooks, w.ports)
            old, _, check = _old_output(case)
            case.prepare(large_archive=old)
            _closed(test, case.close(old))
            receipt = case.ssd_copy(old)
            _closed(test, case.close(check, retire=(old.plan,)))
            case.prepare(free_space_less_than_archive=old, same_size_cloud_corruption=corrupt)
            archive = case.stage / old.plan / f"{old.plan}.tgz.enc"
            test.assertTrue(archive.is_file())
            result = case.close(old, receipt=receipt)
            test.assertEqual(result.code, 6 if corrupt else 0, result)
            test.assertEqual(archive.exists(), corrupt)
            test.assertFalse(case.observe("second_local_archive", span=old))


@scenario("A-08", "O")
def _marker_interrupted(test, w):
    span = w.span()
    w.at("durable.linked", lambda: _crash_marker(w, span))
    result = w.offload(span)
    test.assertEqual(result.code, CRASH_EXIT, result)
    names = set(w.markers.iterdir())
    test.assertTrue(w.marker(span).is_file())
    test.assertEqual(w.evidence(span).status, "BUSY")
    test.assertEqual(set(w.markers.iterdir()), names)
    _ok(test, w.offload(span))
    _clear(test, w, span)
    test.assertEqual(set(w.markers.iterdir()), {w.marker(span)})


def _crash_marker(world, span):
    if world.marker(span).exists():
        raise Crash("marker linked")
    world.at("durable.linked", lambda: _crash_marker(world, span))


@scenario("A-09", "")
def _retry_notification(test, w):
    watcher = night_results_watch
    state, current = w.root / "watch-state.json", w.root / "current.json"
    delivered, fail = w.root / "delivered", w.root / "fail"
    fail.touch()
    _dump(current, {"armed": {"plan_id": "synthetic", "t0": 10, "latest_end": 20}})
    notifier = (
        "from pathlib import Path; import sys\n"
        "fail, log = map(Path, sys.argv[1:3])\n"
        "if fail.exists(): raise SystemExit(7)\n"
        "with log.open('a') as handle: print(sys.argv[3], file=handle)\n"
    )
    args = ["--once", "--repo", str(w.repo), "--state", str(state), "--current",
            str(current), "--grace", "0", "--notify-cmd", sys.executable, "-B", "-c",
            notifier, str(fail), str(delivered)]
    def run():
        output = StringIO()
        with redirect_stdout(output), patch.object(watcher.time, "time", return_value=30):
            code = watcher.main(args)
        return code, output.getvalue().splitlines()
    code, first = run()
    test.assertEqual(code, watcher.EXIT_CODES["error"])
    test.assertFalse(state.exists())
    test.assertFalse(delivered.exists())
    fail.unlink()
    code, second = run()
    test.assertEqual(code, watcher.EXIT_CODES["alarm"])
    test.assertIn("ARMED_NO_RESULT_PAST_LATEST_END synthetic", second[0])
    test.assertEqual(first[0], second[0])
    test.assertEqual(delivered.read_text().splitlines(), second)
    test.assertEqual(run(), (watcher.EXIT_CODES["quiet"], []))


@scenario("A-10", "C", "O")
def _hold_middle(test, w):
    older, middle, checked = _old_output(w)
    _closed(test, w.close(older))
    _closed(test, w.close(middle))
    _ok(test, w.hold("add", "--id", "middle", "--path", middle.output,
                     "--reason", "synthetic hold", "--by", "contract"))
    _closed(test, w.close(checked))
    _closed(test, w.close(checked, retire=(middle.plan,)))
    test.assertTrue(middle.output.is_dir())
    test.assertFalse((w.stage / middle.plan / ".retirement.json").exists())
    _ok(test, w.hold("remove", "--id", "middle", "--by", "contract"))
    w.crash_at("close.retirement_record_published")
    result = w.close(checked, retire=(middle.plan,))
    test.assertEqual(result.code, CRASH_EXIT, result)
    test.assertTrue(middle.output.is_dir())
    # Simulate watchdog stale-fence removal with the canonical primitive.
    fence.clear_owned(w.host, w.read_fence()["purpose"])
    _ok(test, w.hold("add", "--id", "middle", "--path", middle.output,
                     "--reason", "synthetic hold", "--by", "contract"))
    _closed(test, w.close(checked))
    result = w.close(checked, retire=(middle.plan,))
    test.assertEqual(result.code, 4, result)
    test.assertIn("RETENTION_CONFLICT", result.stdout + result.stderr)
    test.assertTrue(middle.output.is_dir())


@scenario("A-11", "Q")
def _intent_enospc(test, w):
    span = w.span()
    w.prepare(queued=span)
    w.fault_at("controller.intent_write", errno.ENOSPC)
    w.tick()
    test.assertIsNone(w.record(span, "intent"))
    w.no_arm(span)

    def late_failure():
        test.assertIsNotNone(w.record(span, "intent"))
        test.assertFalse(w.observe("bootstraps"))
        w.at("durable.directory_synced", lambda: test.assertFalse(w.observe("bootstraps")))
        raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC))

    w.at("controller.intent_write", lambda: w.at("durable.temp_unlinked", late_failure))
    w.tick()
    if not w.observe("bootstraps"):
        w.tick()
    test.assertNotIn("durable.directory_synced", w.actions, "intent was never re-synced")
    _armed(test, w, span)
    torn = w.span("synthetic-s02")
    endpoint = w.state / "spans" / torn.plan / "intent.json"
    endpoint.parent.mkdir(parents=True, exist_ok=True)
    endpoint.write_bytes(b'{"plan_id":')
    w.restart()
    w.tick()
    w.assert_gate("HALT", "ARM_INDETERMINATE")
    test.assertNotIn(torn.plan, w.observe("bootstraps"))


@scenario("A-12", "")
def _duplicate_pointer_number(test, w):
    source, out = w.root / "RUN_STATE.md", w.root / "CURRENT.json"
    first = "42. **First synthetic item.**\n\n```pointer\nowner: lead\nwait: none\nnext_observable: first\n```\n"
    second = first.replace("First", "Second").replace("observable: first", "observable: second")
    source.write_text(first + "\n" + second, encoding="utf-8")
    out.write_bytes(b"previous")
    stderr = StringIO()
    with redirect_stderr(stderr):
        code = gen_current.main(["--run-state", str(source), "--out", str(out)])
    if code == 0 and out.read_bytes() == gen_current.render(first):
        raise DuplicatePointerAccepted("main accepts duplicate numbered pointer items")
    test.assertEqual(code, 2, stderr.getvalue())
    test.assertEqual(out.read_bytes(), b"previous")


@scenario("R9-F1", "OQ")
def _hand_predecessor(test, w):
    old = w.span("unrelated-s01")
    previous = w.span("hand-s01", receipt=False)
    span = w.span("synthetic-s02")
    w.prepare(unrelated_receipt=old, ledger_predecessor=previous, queued=span)
    w.tick()
    w.no_arm(span)
    w.assert_gate("HOLD", "JOURNAL_COPY")


@scenario("R9-F2", "Q")
def _lost_arm_fence(test, w):
    for fault in ("absent_at_entry", "removed_after_read", "replaced_before_bootstrap"):
        with test.subTest(fault=fault), ExitStack() as stack:
            case = World(test, stack, w.hooks, w.ports)
            span = case.span()
            case.prepare(queued=span, qualification_launcher=True)
            if fault == "absent_at_entry":
                point = "controller.before_arm_child"
            elif fault == "removed_after_read":
                point = "launcher.standing_read"
            else:
                point = "launcher.before_bootstrap"
            def change():
                if fault == "replaced_before_bootstrap":
                    case.stand(purpose="align-r0:other")
                else:
                    fence.clear_owned(case.host, case.read_fence()["purpose"])
            case.at(point, change)
            case.tick()
            test.assertEqual(case.observe("arm_child_exit"), 3)
            test.assertFalse(case.observe("bootstraps"))
            case.assert_gate("HALT", "ARM_INDETERMINATE")
            case.check_checkpoints()


@scenario("R9-F3", "Q")
def _duplicate_restore(test, w):
    span = w.span()
    w.prepare(closed=span, restore_lines=(9, 0))
    w.tick()
    w.assert_gate("HALT")
    test.assertNotEqual(w.record(span, "close")["status"], "CLOSED_OK")


@scenario("R9-F4", "DQ")
def _probe_not_inventory(test, w):
    w.prepare(desk_due=True, ref_listing="probe-ok-full-failed")
    w.tick()
    test.assertIn("probe", w.observe("ref_listing_calls"))
    test.assertIn("inventory", w.observe("ref_listing_calls"))
    for verdict in w.observe("verdicts"):
        test.assertFalse(verdict["desk_final"] and verdict["history_source"] == "signed-records")


def _interrupted_tick(test, w, point):
    w.crash_at(point)
    with test.assertRaises(Crash):
        w.tick()
    w.restart()
    w.tick()


@scenario("K-01", "Q")
def _intent_no_spawn(test, w):
    span = w.span()
    w.prepare(queued=span)
    _interrupted_tick(test, w, "controller.intent_published")
    test.assertIsNotNone(w.record(span, "intent"))
    test.assertFalse(w.observe("bootstraps"))
    w.assert_gate("HALT", "ARM_INDETERMINATE")


@scenario("K-02", "Q")
def _adopt_live(test, w):
    span = w.span()
    w.prepare(queued=span)
    _interrupted_tick(test, w, "controller.bootstrap_returned")
    _armed(test, w, span)
    test.assertEqual(w.observe("bootstraps").count(span.plan), 1)


@scenario("K-03", "Q")
def _transfer_without_bootstrap(test, w):
    span = w.span(receipt=False)
    w.prepare(queued=span, no_runner_output=True)
    _interrupted_tick(test, w, "launcher.fence_transferred")
    test.assertTrue(w.read_fence()["purpose"].startswith("align-r0:"))
    test.assertFalse(w.observe("bootstraps"))
    w.assert_gate("HOLD")
    w.prepare(launcher_timeout=True)
    w.tick()
    w.assert_gate("HALT", "ARM_INDETERMINATE")


@scenario("K-04", "QC", "O")
def _controller_dies_in_close(test, w):
    w.prepare(retirement_batch=True)
    def owner_died():
        pid = w.read_fence()["pid"]
        w.boundary.put("pids", [active for active in w.boundary.get("pids") if active != pid])
        w.prepare(old_close_worker_alive=True, replacement_controller=True)
    w.at("close.between_destructive_steps", owner_died)
    w.tick()
    test.assertIn("FENCE_CHANGED", w.close_call()[1].stdout)
    test.assertFalse(w.observe("deletions_after", checkpoint="close.between_destructive_steps"))
    w.restart()
    w.tick()
    test.assertIn("BUSY", w.close_call()[1].stdout)
    w.prepare(old_close_worker_alive=False)
    w.tick()
    _closed(test, w.close_call()[1])


@scenario("K-05", "O")
def _provider_readback_crash(test, w):
    span = w.span()
    w.crash_at("offload.provider_verified")
    result = w.offload(span)
    test.assertEqual(result.code, CRASH_EXIT, result)
    test.assertFalse(w.marker(span).exists())
    stage = w.stage / span.plan
    inode = stage.stat().st_ino
    first = w.observe("provider_readbacks", span=span)
    test.assertGreater(len(first), 0)
    _ok(test, w.offload(span))
    test.assertEqual(stage.stat().st_ino, inode)
    test.assertGreater(len(w.observe("provider_readbacks", span=span)), len(first))
    _clear(test, w, span)
    test.assertEqual(set(w.markers.glob("*.ok")), {w.marker(span)})


@scenario("K-06", "C", "O")
def _resume_retire(test, w):
    for point, new_hold in (("close.retirement_record_published", False),
                            ("close.retirement_renamed", False),
                            ("close.retirement_record_published", True),
                            ("close.retirement_renamed", True)):
        with test.subTest(point=point, new_hold=new_hold), ExitStack() as stack:
            case = World(test, stack, w.hooks, w.ports)
            old, _, checked = _old_output(case)
            _closed(test, case.close(old))
            case.crash_at(point)
            result = case.close(checked, retire=(old.plan,))
            test.assertEqual(result.code, CRASH_EXIT, result)
            record = case.stage / old.plan / ".retirement.json"
            intent = json.loads(record.read_bytes())
            test.assertTrue(intent["inventory"])
            fence.clear_owned(case.host, case.read_fence()["purpose"])
            if new_hold:
                _ok(test, case.hold("add", "--id", "late", "--path", old.output,
                                    "--reason", "synthetic hold", "--by", "contract"))
            result = case.close(checked, retire=(old.plan,))
            if new_hold:
                test.assertEqual(result.code, 4)
                test.assertIn("RETENTION_CONFLICT", result.stdout + result.stderr)
                test.assertEqual(old.output.exists(), point == "close.retirement_record_published")
            else:
                _closed(test, result)
                test.assertFalse(old.output.exists())
                test.assertFalse(case.observe("retirement_in_progress", span=old))
            test.assertEqual(json.loads(record.read_bytes()), intent)
            case.check_checkpoints()


@scenario("K-07", "DQ")
def _verdict_commit_crash(test, w):
    span = w.span()
    w.prepare(bundle_pushed=span, real_verdict=True)
    w.crash_at("desk.verdict_commit_created")
    with suppress(Crash):
        w.tick()
    ref = f"refs/heads/cadence-desk-mbp/{span.plan}"
    test.assertNotEqual(w.git("show-ref", "--verify", ref, repo=w.repo, check=False).returncode, 0)
    w.restart()
    w.tick()
    test.assertTrue(w.record(span, "close")["mbp_desk"]["published"])
    test.assertEqual(w.git("for-each-ref", "--format=%(refname)", ref, repo=w.repo).stdout.splitlines(), [ref])


@scenario("K-08", "Q")
def _bundle_push_crash(test, w):
    span = w.span()
    w.prepare(closed=span)
    ref = f"refs/heads/desk-bundles/{span.plan}"
    before = []
    w.at("controller.bundle_pushed", lambda: _capture_ref_and_crash(w, ref, before))
    with test.assertRaises(Crash):
        w.tick()
    test.assertFalse(w.record(span, "close").get("bundle_commit"))
    w.restart()
    w.tick()
    test.assertEqual(w.git("rev-parse", ref, repo=w.remote).stdout.strip(), before[0])
    test.assertEqual(w.record(span, "close")["bundle_commit"], before[0])


def _capture_ref_and_crash(w, ref, before):
    before.append(w.git("rev-parse", ref, repo=w.remote).stdout.strip())
    raise Crash(ref)


@scenario("K-09", "QCO")
def _reboot_live(test, w):
    span = w.span(receipt=False)
    w.prepare(queued=span)
    w.tick()
    _armed(test, w, span)
    w.prepare(reboot=True, stranded=span, require_file="synthetic.txt")
    w.restart()
    w.tick()
    test.assertEqual(w.record(span, "close")["status"], "STRANDED")
    w.assert_gate("HALT")
    _clear(test, w, span, require_closed=False)


@scenario("K-10", "Q", "OC")
def _offload_unrecorded(test, w, *, enospc=False):
    span = w.span()
    w.prepare(closed=span)
    if enospc:
        w.fault_at("controller.close_record_write", errno.ENOSPC)
        w.tick()
    else:
        w.crash_at("controller.offload_returned")
        with test.assertRaises(Crash):
            w.tick()
    _clear(test, w, span)
    test.assertFalse(w.record(span, "close").get("copy"))
    before = w.marker(span).stat().st_ino
    readbacks = len(w.observe("provider_readbacks", span=span))
    w.restart()
    w.tick()
    _closed(test, w.close_call(span)[1])
    _copied(test, w, span)
    test.assertEqual(w.marker(span).stat().st_ino, before)
    test.assertGreater(len(w.observe("provider_readbacks", span=span)), readbacks)


@scenario("T-01", "Q")
def _clock_monotonic(test, w):
    _monotonic_lease(test, w)


@scenario("T-02", "OQ")
def _provider_wall_back(test, w):
    span = w.span()
    w.prepare(closed=span)
    w.at("offload.provider_verified", lambda: w.boundary.step(wall=-600))
    _ok(test, w.offload(span))
    _clear(test, w, span)
    test.assertEqual(w.invoke("copy_gate_problems", span=span), [])


@scenario("T-03", "CQ", "O")
def _clock_fence(test, w):
    _fence_lapse(test, w, "expiry")


@scenario("T-04", "Q")
def _server_clock(test, w, *, first_only=False):
    cases = ("once_then_success",) if first_only else ("once_then_success", "lease_unavailable", "skew_over_120")
    for fault in cases:
        with test.subTest(fault=fault), ExitStack() as stack:
            case = World(test, stack, w.hooks, w.ports)
            span = case.span()
            case.prepare(queued=span, server_time=fault)
            case.tick()
            if fault == "once_then_success":
                case.no_arm(span)
                case.tick()
                _armed(test, case, span)
            else:
                case.no_arm(span)
                test.assertFalse(case.observe("arm_notices"))
                case.assert_gate("HOLD" if fault == "lease_unavailable" else "HALT")


@scenario("T-05", "Q")
def _date_end(test, w):
    span = w.span()
    w.prepare(queued=span)
    w.at("controller.authority_read_complete", lambda: w.boundary.step(wall=86400))
    w.tick()
    test.assertFalse(w.observe("bootstraps"))


@scenario("T-06", "OQ")
def _future_marker(test, w):
    span = w.span()
    w.prepare(closed=span)
    _ok(test, w.offload(span))
    w.boundary.step(wall=-600)
    test.assertEqual(w.evidence(span).status, "BUSY")
    w.tick()
    w.assert_gate("HOLD", "JOURNAL_COPY")
    w.boundary.step(wall=601)
    _clear(test, w, span)


@scenario("E-01", "Q")
def _disk_full_intent(test, w):
    _intent_enospc(test, w)


@scenario("E-02", "O")
def _disk_full_marker(test, w):
    span = w.span()
    w.fault_at("offload.marker_write", errno.ENOSPC)
    result = w.offload(span)
    test.assertEqual(result.code, 5, result)
    test.assertFalse(w.marker(span).exists())
    _ok(test, w.offload(span))
    _clear(test, w, span)
    test.assertEqual(set(w.markers.glob("*.ok")), {w.marker(span)})

    late = w.span("synthetic-s02")
    marker = w.marker(late)

    def late_failure():
        published = marker.read_bytes()
        w.at("durable.directory_synced", lambda: test.assertEqual(marker.read_bytes(), published))
        raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC))

    w.at("offload.marker_write", lambda: w.at("durable.temp_unlinked", late_failure))
    result = w.offload(late)
    if result.code == 5:
        result = w.offload(late)
    _ok(test, result)
    _clear(test, w, late)
    test.assertEqual(set(w.markers.glob("*.ok")), {w.marker(span), marker})


@scenario("E-03", "OC")
def _disk_full_reclaim(test, w):
    _stream_reclaim(test, w)


@scenario("E-04", "Q")
def _disk_full_fence(test, w):
    ctl = w.restart()
    ctl.hold_fence()
    record = w.read_fence()
    raw = (w.host / fence.FENCE_NAME).read_bytes()
    fsync = os.fsync
    failed_writes = []
    def no_space_on_fence(fd):
        written = os.fstat(fd)
        for temporary in w.host.glob(f".{fence.FENCE_NAME}.*.tmp"):
            if os.path.samestat(temporary.stat(), written):
                failed_writes.append(temporary)
                raise OSError(errno.ENOSPC, "synthetic disk full")
        fsync(fd)

    w.prepare(fence_renewal_due=True)
    with patch.object(os, "fsync", side_effect=no_space_on_fence):
        ctl.refresh_fence()
        test.assertTrue(failed_writes)
        test.assertEqual((w.host / fence.FENCE_NAME).read_bytes(), raw)
        test.assertFalse(w.observe("lease_lapsed"))
        w.boundary.step(wall=record["deadline"] - w.boundary.now() + 1)
        ctl.refresh_fence()
        test.assertTrue(w.observe("lease_lapsed"))


@scenario("E-05", "Q", "OC")
def _disk_full_close_record(test, w):
    _offload_unrecorded(test, w, enospc=True)


@scenario("E-06", "C", "O")
def _disk_full_retirement(test, w):
    old, _, checked = _old_output(w)
    _closed(test, w.close(old))
    inventory = {entry.name: entry.read_bytes() for entry in old.output.iterdir()}
    w.fault_at("close.retirement_record_write", errno.ENOSPC)
    w.close(checked, retire=(old.plan,))
    test.assertEqual({entry.name: entry.read_bytes() for entry in old.output.iterdir()}, inventory)
    test.assertFalse((w.stage / old.plan / ".retirement.json").exists())


@scenario("E-07", "O")
def _disk_full_stage(test, w):
    span = w.span()
    w.fault_at("offload.stage_build", errno.ENOSPC)
    result = w.offload(span)
    test.assertNotEqual(result.code, 0, result)
    test.assertFalse((w.stage / span.plan).exists())
    test.assertFalse(w.marker(span).exists())
    test.assertNotEqual(w.evidence(span).status, "CLEAR")


@scenario("I-01", "O")
def _upload_not_idle(test, w):
    span = w.span()
    w.prepare(provider_upload_idle=False)
    result = w.offload(span, "--deadline-epoch", str(w.boundary.now() + 2))
    test.assertEqual(result.code, 5, result)
    test.assertIn("DEADLINE", result.stderr + result.stdout)
    test.assertEqual(list(w.markers.iterdir()), [])
    test.assertGreater(w.observe("provider_upload_polls"), 0)


@scenario("I-07", "OCQ")
def _unconfirmed(test, w):
    span, regular, f0 = w.span(), w.span("synthetic-s02"), w.span("synthetic-f0")
    w.prepare(closed=span, queued=(regular, f0), provider_verifies=False)
    w.tick()
    test.assertEqual(w.close_call(span)[1].code, 8)
    test.assertTrue(w.marker(span).with_suffix(".ok.unconfirmed").is_file())
    test.assertFalse(w.marker(span).exists())
    for minutes in (0, 5, 15):
        w.boundary.step(wall=minutes * 60, mono=minutes * 60)
        w.tick()
        w.no_arm(regular)
        w.no_arm(f0)
    test.assertEqual(w.observe("copy_retry_delays"), [300, 900])
    w.assert_gate("HALT", "OFFLOAD_FAILED")


@scenario("I-02", "O")
def _no_dataless(test, w):
    span = w.span()
    w.prepare(provider_evicts=False)
    result = w.offload(span)
    test.assertEqual(result.code, 8, result)
    test.assertFalse(w.marker(span).exists())
    test.assertTrue(w.marker(span).with_suffix(".ok.unconfirmed").is_file())


@scenario("I-03", "OCQ")
def _readback_hash(test, w):
    span = w.span()
    w.prepare(closed=span, provider_readback_corrupt=True)
    w.tick()
    test.assertEqual(w.close_call(span)[1].code, 6)
    w.assert_gate("HALT", "OFFLOAD_FAILED")
    test.assertFalse(w.marker(span).exists())


@scenario("I-04", "OQ")
def _bad_pending(test, w):
    span = w.span()
    w.prepare(queued=span)
    for pending in ("pending", "offline", "error", "empty"):
        with test.subTest(pending=pending):
            w.prepare(pending=pending)
            result = w.pending()
            clear = result["clear"] if isinstance(result, dict) else result.clear
            test.assertIsNot(clear, True)
            w.tick()
            w.no_arm(span)
            w.assert_gate("HOLD")


@scenario("I-05", "C", "O")
def _provider_orphan(test, w):
    span = w.span()
    w.prepare(provider_orphan=span, pending="pending")
    result = w.close(span)
    group = w.observe("provider_group", span=span)
    test.assertIn(group, [pid for pid, sig in w.boundary.get("signals") if sig])
    test.assertNotEqual(result.record["status"], "CLOSE_OK")
    w.prepare(pending="clear", provider_orphan=None)
    _closed(test, w.close(span))


@scenario("I-06", "O")
def _cloud_unavailable(test, w):
    span = w.span()
    for availability in ("signed_out", "missing_container"):
        with test.subTest(availability=availability):
            w.prepare(cloud_availability=availability)
            before = {entry.name: entry.read_bytes() for entry in span.output.iterdir()}
            codes = []
            for _ in range(2):
                result = w.offload(span)
                test.assertEqual(result.code, 5, result)
                # The offload CLI exposes the OffloadError code in its
                # one-line diagnostic. The contract leaves naming to #804.
                diagnostic = re.fullmatch(r"OFFLOAD_UNVERIFIED ([A-Z][A-Z0-9_]*)(?: .*)?",
                                          result.stderr.strip())
                test.assertIsNotNone(diagnostic, result)
                codes.append(diagnostic[1])
                test.assertFalse(w.marker(span).exists())
                test.assertEqual({entry.name: entry.read_bytes() for entry in span.output.iterdir()}, before)
            test.assertEqual(codes[0], codes[1])


@scenario("G-01", "QCOD")
def _bundle_outage(test, w):
    span = w.span()
    w.prepare(closed=span, bundle_push="failed")
    w.tick()
    _copied(test, w, span)
    test.assertFalse(w.observe("verdict_counted", span=span))
    test.assertNotIn(span.plan, w.observe("retire_plans"))
    w.prepare(bundle_push="available")
    w.tick()
    test.assertTrue(w.record(span, "close")["bundle_commit"])
    test.assertTrue(w.observe("verdict_counted", span=span))


@scenario("G-02", "Q")
def _audit_outage(test, w):
    span = w.span()
    w.prepare(queued=span, audit_fetch="failed")
    w.tick()
    w.no_arm(span)
    w.assert_gate("HOLD", "FETCH_FAILED")
    test.assertTrue(w.read_fence()["purpose"].startswith("cadence-controller:"))


@scenario("G-03", "Q")
def _server_outage_recovers(test, w):
    _server_clock(test, w, first_only=True)


@scenario("G-04", "Q")
def _notice_outage(test, w):
    span = w.span()
    w.prepare(queued=span, notice_post="failed")
    w.tick()
    w.no_arm(span)


@scenario("G-05", "DQ")
def _remote_removed(test, w):
    _remote_disappears(test, w)


@scenario("G-06", "Q")
def _post_intent_outage(test, w):
    span = w.span()
    w.prepare(queued=span)
    w.at("controller.intent_published", lambda: w.prepare(network_available=False))
    w.tick()
    _armed(test, w, span)
    test.assertEqual(w.observe("network_after_intent_before_bootstrap"), [])


@scenario("G-07", "Q")
def _watcher_outage(test, w):
    span = w.span()
    w.prepare(queued=span, actions_api="unreachable")
    for _ in range(2):
        w.tick()
        w.no_arm(span)
        w.assert_gate("HOLD")
    test.assertGreaterEqual(len(w.observe("watcher_reads")), 2)
    test.assertFalse(w.observe("watcher_fresh"))


@scenario("N-01", "OCDQ")
def _air_absent(test, w):
    spans = tuple(w.span(f"synthetic-s{i:02}") for i in range(1, 5))
    w.prepare(queue=spans, air_available=False, real_verdict=True)
    for span in spans[:3]:
        w.tick()
        _armed(test, w, span)
        w.prepare(runner_ended=span)
        w.tick()
        _copied(test, w, span)
        test.assertTrue(w.observe("verdict_counted", span=span))
        test.assertNotIn("Air", w.observe("gate_reasons"))
    w.tick()
    _armed(test, w, spans[3])
    test.assertEqual(w.observe("air_waits"), [])


@scenario("N-02", "OC")
def _no_ssd(test, w):
    old, _, checked = _old_output(w)
    _closed(test, w.close(old))
    w.prepare(free_space_bytes=60_000_000_000, air_available=False)
    _closed(test, w.close(checked, retire=(old.plan,)))
    result = w.cli("C", "reclaim", "--config", w.offload_config, "--span-dir", old.output,
                   "--fence-mode", "self", "--deadline-epoch", str(w.boundary.now() + 300))
    test.assertEqual(result.code, 2)
    test.assertTrue((w.stage / old.plan / f"{old.plan}.tgz.enc").exists())
    test.assertTrue(w.observe("low_space_mail"))


@scenario("N-03", "CQ", "O")
def _hand_gate_air_absent(test, w):
    old, recent, _ = _old_output(w)
    w.prepare(closed=recent, earlier=old, hand_gates="open", air_available=False)
    w.tick()
    test.assertTrue(old.output.is_dir())
    test.assertNotIn(old.plan, w.observe("retire_plans"))


@scenario("N-04", "OC")
def _valid_ssd(test, w):
    old, _, checked = _old_output(w)
    _closed(test, w.close(old))
    _closed(test, w.close(checked, retire=(old.plan,)))
    receipt = w.ssd_copy(old)
    archive = w.stage / old.plan / f"{old.plan}.tgz.enc"
    test.assertTrue(archive.exists())
    _closed(test, w.close(old, receipt=receipt))
    test.assertFalse(archive.exists())
    test.assertIn("cloud", w.observe("reclaim_verified", span=old))
    test.assertIn("ssd", w.observe("reclaim_verified", span=old))


@scenario("N-05", "DQ")
def _desk_disagreement(test, w):
    span = w.span()
    w.prepare(bundle_pushed=span, real_verdict=True, air_available=False)
    w.tick()
    test.assertTrue(w.observe("verdict_counted", span=span))
    w.prepare(remote_different_verdict=span, air_available=True)
    w.tick()
    w.assert_gate("HALT", "DESK_DISAGREEMENT")


@scenario("N-06", "O")
def _public_key_only(test, w):
    span = w.span()
    w.prepare(air_available=False, forbid_private_inputs=True)
    result = _ok(test, w.offload(span))
    _clear(test, w, span)
    test.assertEqual(w.observe("encryption_recipient"), w.config()["recipient_sha256"])
    test.assertEqual(w.observe("air_input_reads"), [], result)
