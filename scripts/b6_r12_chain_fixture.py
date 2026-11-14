#!/usr/bin/env python3
"""RL-49 source-only feasibility witnesses, with no host probe execution.

This is deliberately not a session generator yet. The arm witness runs pinned
code, including its instrument child, on synthetic external inputs. No result
of a judgment is injected. Run in a fresh interpreter to isolate the pin from
the checkout's package imports.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack, redirect_stdout
from datetime import datetime, UTC
import hashlib
import io
import json
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
from unittest.mock import patch

PIN = "f31aca19f90473231c41cb31643afb0d6c85d355"
REPO = Path(__file__).resolve().parents[1]
BOOT = "00000000-0000-4000-8000-000000000012"


def git_bytes(relative):
    """Read code objects only, never a worktree or a study-data locator."""
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or path.parts[0] != "joulewise" or path.suffix != ".py":
        raise ValueError("only pinned Python package source may be exported")
    return subprocess.check_output(["git", "show", f"{PIN}:{path.as_posix()}"], cwd=REPO)


def export_package(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    names = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", PIN, "joulewise"],
                                    cwd=REPO, text=True).splitlines()
    hashes = {}
    for name in names:
        if not name.endswith(".py"):
            continue
        raw = git_bytes(name)
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        hashes[name] = hashlib.sha256(raw).hexdigest()
    return hashes


class Clock:
    """Three synthetic kernel readings; sleep advances logical time only."""

    def __init__(self):
        self.ns = 1_000_000_000_000
        self.origin = self.ns
        self.wall_offset = 1_700_000_000_000_000_000 - self.ns

    def tick(self):
        self.ns += 100
        return self.ns

    def monotonic_ns(self):
        return self.tick()

    monotonic_raw_ns = monotonic_ns

    def realtime_ns(self):
        return self.tick() + self.wall_offset

    def clock_gettime_ns(self, clock_id):
        if clock_id == time.CLOCK_REALTIME:
            return self.realtime_ns()
        if clock_id == time.CLOCK_MONOTONIC_RAW:
            return self.monotonic_raw_ns()
        raise ValueError("undeclared clock")

    def stamp(self):
        from joulewise.hazards.base import Stamp
        raw, mono, wall = self.monotonic_raw_ns(), self.monotonic_ns(), self.realtime_ns()
        return Stamp(wall, mono, raw)

    def sleep(self, seconds):
        self.ns += round(seconds * 1_000_000_000)


class Sources:
    """Declared argv results; unknown commands are denied and recorded."""

    def __init__(self, root, clock, denied_off=False):
        from joulewise.hazards import arm, battery, clock as clock_module, contention, thermal
        self.root, self.clock, self.calls = Path(root).resolve(), clock, []
        self.off = arm.NETWORK_TIME_OFF_ARGV
        self.denied_off = denied_off
        self.rules = {
            arm.AGENT_CENSUS_ARGV: (1, b"", b""),
            battery.IOREG_BATTERY_ARGV: self.battery,
            thermal.NOTIFYUTIL_ARGV: (0, f"{thermal.NOTIFY_KEY} 0\n".encode(), b""),
            thermal.PMSET_THERM_ARGV: (0, b"Note: No thermal warning level has been recorded\n", b""),
            clock_module.BOOT_ARGV: (0, (BOOT + "\n").encode(), b""),
            contention.PS_ARGV: (0, b"  PID  PPID                  STARTED     TIME COMMAND\n"
                                     b" 4000     1 Mon Nov  2 00:00:00 2026 00:00.00 fixture\n", b""),
            arm.DIAGNOSTIC_ARGVS[0]: (0, b"System-wide power settings:\n lowpowermode 0\n", b""),
        }
        if not denied_off:
            self.rules[self.off] = (0, b"Network Time is already off.\n", b"")
        self.sampler_commands = {}

    def battery(self):
        stamp = int((self.clock.ns + self.clock.wall_offset) / 1e9)
        return 0, ("+-o AppleSmartBattery  <class AppleSmartBattery, id 0x123, registered, "
                   "matched, active, busy 0 (0 ms), retain 1>\n"
                   "    {\n"
                   '      "ExternalConnected" = Yes\n'
                   '      "IsCharging" = No\n'
                   '      "InstantAmperage" = 0\n'
                   f'      "UpdateTime" = {stamp}\n'
                   '      "Amperage" = 0\n'
                   '      "Voltage" = 12000\n'
                   "    }\n").encode(), b""

    def completed(self, argv, result, kind):
        from joulewise.hazards.base import Completed
        rc, out, err = result
        self.calls.append({"argv": list(argv), "kind": kind, "returncode": rc,
                           "stdout": out.decode(), "stderr": err.decode(), "executed": False})
        return Completed(tuple(argv), rc, out, err)

    def run(self, argv, timeout_s):
        from joulewise.hazards import instrument
        argv = tuple(map(str, argv))
        # Dispatch the *real pinned* instrument child, not a fabricated child report.
        if (len(argv) >= 5 and argv[:4] == (sys.executable, "-B", "-c", instrument.CHILD_BOOTSTRAP)
                and argv[4] == str(instrument.REPO_ROOT)):
            child_args = argv[5:]
            output = Path(child_args[child_args.index("--output") + 1]).resolve()
            if not output.is_relative_to(self.root):
                raise PermissionError("instrument output outside fixture root")
            from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
            config = SimpleNamespace(sampling=SimpleNamespace(power_hz=10., idle_seconds=30.))
            executable = child_args[child_args.index("--executable") + 1]
            prefix = json.loads(child_args[child_args.index("--privilege-prefix") + 1])
            adapter = PowermetricsTelemetryAdapter(None, executable=executable, privilege_prefix=prefix)
            command = tuple(adapter._command(config, output, count=adapter._idle_count(config)))
            self.sampler_commands[command] = output
            out = io.StringIO()
            with redirect_stdout(out):
                rc = instrument._child_main(child_args)
            self.calls.append({"argv": list(argv), "kind": "pinned_instrument_child", "returncode": rc,
                               "executed": True})
            from joulewise.hazards.base import Completed
            return Completed(argv, rc, out.getvalue().encode(), b"")
        result = self.rules.get(argv)
        if result is None:
            return self.completed(argv, (126, b"", b"RL-49 default deny"), "denied")
        return self.completed(argv, result() if callable(result) else result, "declared")

    def subprocess_run(self, argv, **kwargs):
        # The instrument child's group census is an external process observation.
        argv = tuple(map(str, argv))
        if argv == ("/usr/bin/pgrep", "-lf", "-g", "987654321", "."):
            result = self.completed(argv, (1, b"", b""), "declared_group_absent")
        else:
            result = self.run(argv, kwargs.get("timeout", 10))
        out, err = result.stdout, result.stderr
        if kwargs.get("text"):
            out, err = out.decode(), err.decode()
        return subprocess.CompletedProcess(argv, result.returncode, out, err)

    def popen(self, argv, **kwargs):
        argv = tuple(map(str, argv))
        path = self.sampler_commands.get(argv)
        if path is None:
            self.calls.append({"argv": list(argv), "kind": "denied_popen", "executed": False})
            raise PermissionError("RL-49 undeclared process")
        count_index = max(i for i, value in enumerate(argv) if value == "-n")
        count = int(argv[count_index + 1])
        interval_ns = int(argv[argv.index("-i") + 1]) * 1_000_000
        frames = [plistlib.dumps({
            "timestamp": datetime.fromtimestamp(1_700_000_000 + (i + 1) * interval_ns / 1e9, UTC),
            "elapsed_ns": interval_ns, "thermal_pressure": "Nominal", "is_delta": True,
            "processor": {"cpu_power": 500., "gpu_power": 0., "ane_power": 0.,
                          "cpu_energy": 500. * interval_ns / 1e9, "gpu_energy": 0., "ane_energy": 0.}})
                  for i in range(count)]
        path.write_bytes(b"\0".join(frames))
        self.calls.append({"argv": list(argv), "kind": "synthetic_sampler", "executed": False,
                           "frames": count, "interval_ns": interval_ns})
        # Only the external sampler is simulated. The child owns parsing and statistics.
        return SimpleNamespace(pid=987654321, returncode=0,
                               communicate=lambda **kw: (b"", b""), poll=lambda: 0)


def guard(root):
    """Refuse native launches and writes escaping the resolved synthetic root."""
    root = Path(root).resolve()
    write_events = {"os.mkdir", "os.remove", "os.rmdir", "os.rename", "os.chmod", "os.truncate"}

    def check(event, args):
        if event in {"subprocess.Popen", "os.system", "os.posix_spawn", "os.exec", "os.fork",
                     "os.symlink", "os.link", "socket.connect", "socket.bind"}:
            raise PermissionError(f"RL-49 native action denied: {event}")
        paths = []
        write = event in write_events
        if event == "open" and isinstance(args[0], (str, bytes)):
            paths = [args[0]]
            write = bool(args[2] & (1 | 2 | 64 | 512 | 1024))
        elif write:
            paths = list(args[:2] if event == "os.rename" else args[:1])
        elif event in {"os.listdir", "os.scandir"}:
            paths = list(args[:1])
        for value in paths:
            if not isinstance(value, (str, bytes)):
                continue
            # abspath avoids probing any forbidden target during the safety check.
            import os
            path = Path(os.path.abspath(os.fsdecode(value)))
            if path.is_relative_to("/Users/edr") or ("restricted" in path.parts and not path.is_relative_to(root)):
                raise PermissionError("forbidden read/write path")
            if write and not path.is_relative_to(root):
                raise PermissionError("write outside fixture root")

    sys.addaudithook(check)


def safety_witness(root, sources):
    """Check native-action and output-root denials without executing either."""
    denied = sources.run(("/fixture/undeclared-action",), 1)
    if denied.returncode != 126:
        raise AssertionError("undeclared action did not fail closed")
    # This attempts a Python launch, not a host probe or privileged action.
    # The audit hook must reject it before the native Popen event can execute.
    native_denied = outside_denied = False
    try:
        subprocess.Popen([sys.executable, "-B", "-c", "raise SystemExit(0)"])
    except PermissionError as error:
        native_denied = "RL-49 native action denied" in str(error)
    outside = Path(root).parent / "r12-must-not-create"
    try:
        outside.open("x")
    except PermissionError as error:
        outside_denied = "write outside fixture root" in str(error)
    if not (native_denied and outside_denied):
        raise AssertionError("fixture guard did not fail closed")
    return {"native_launch_denied": native_denied, "outside_write_denied": outside_denied,
            "outside_write_target": str(outside)}


def arm_witness(root, denied_off=False):
    """Predicted: both OFF results are record-only; the pinned arm returns GO."""
    from joulewise.hazards import arm, base
    from joulewise import kernel_clock
    clock = Clock()
    sources = Sources(root, clock, denied_off)
    safety = safety_witness(root, sources)
    word = kernel_clock.Timex()
    word.freq = 0
    frequency = {"schema_version": kernel_clock.PROBE_SCHEMA, "modes": 0, "raw_word": 0,
                 "ppm": 0., "call_status": 0, "timex_status": 0, "errno": 0, "raw_hex": bytes(word).hex()}
    ctx = base.Context(run=sources.run, clocks=clock)
    seams = arm.Seams(ctx=ctx, frequency_reader=lambda: frequency,
                      statvfs=lambda path: SimpleNamespace(f_bavail=1024**3, f_frsize=4096, f_blocks=2**40),
                      stat=lambda path: SimpleNamespace(st_dev=1),
                      host_cpu=lambda: [[0, 0, clock.ns // 10_000_000, 0]], smc_read=None)
    config = arm.ArmConfig(custody_dir=Path(root) / "arm", thresholds=arm.default_thresholds(), tree_roots=(4000,),
                           disk_targets=[{"path": str(root), "copies": 1}])
    with ExitStack() as stack:
        stack.enter_context(patch.object(subprocess, "Popen", sources.popen))
        stack.enter_context(patch.object(subprocess, "run", sources.subprocess_run))
        result = arm.run(config, seams)
    return {"decision": result.decision, "reasons": list(result.reasons),
            "arm_path": str(result.path), "calls": sources.calls,
            "logical_seconds": (clock.ns - clock.origin) / 1e9, "safety": safety}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--denied-off", action="store_true")
    args = parser.parse_args(argv)
    lexical_root = args.out.absolute()
    if lexical_root.is_relative_to("/Users/edr") or "restricted" in lexical_root.parts:
        parser.error("--out must be a new synthetic temp destination")
    if args.worker:
        root = args.out.resolve(strict=True)
        sys.path.insert(0, str(root / "pin"))
        guard(root)
        result = arm_witness(root, args.denied_off)
        result["loaded_chain_sha256"] = {
            Path(m.__file__).relative_to(root / "pin").as_posix(): hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()
            for name, m in list(sys.modules.items()) if name.startswith("joulewise") and getattr(m, "__file__", None)
        }
        (root / "receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(result["decision"], result["logical_seconds"], result["reasons"])
        return 0 if result["decision"] == "GO" else 2
    root = args.out.absolute()
    # Reject forbidden locators lexically, before resolving or probing them.
    temp_text = Path(tempfile.gettempdir()).absolute()
    if temp_text.is_relative_to("/Users/edr") or "restricted" in temp_text.parts:
        parser.error("TMPDIR is not an allowed synthetic destination")
    temp_root = temp_text.resolve()
    if not root.is_relative_to(temp_root):
        parser.error("--out must be under the resolved TMPDIR")
    if root != root.resolve() or root.exists():
        parser.error("--out must be new and have a resolved, non-symlinked parent")
    root.mkdir()
    hashes = export_package(root / "pin")
    manifest = {"pin": PIN, "source_sha256": hashes, "synthetic_only": True,
                "kind": "arm_feasibility_only_not_a_session", "expected": "GO",
                "clock_mode": "logical_sleep_advances", "denied_off": args.denied_off,
                "generator_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
                "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    manifest["volume"] = "prerequisite_only: one 300-frame 10-Hz arm probe; no session"
    manifest["seams"] = {
        "joulewise.hazards.arm.Seams.ctx": "Context with Sources.run and logical Clock",
        "joulewise.hazards.arm.Seams.frequency_reader": "kernel word 0; ppm 0; errno 0",
        "joulewise.hazards.arm.Seams.statvfs": {"f_bavail": 1024**3, "f_frsize": 4096, "f_blocks": 2**40},
        "joulewise.hazards.arm.Seams.stat": {"st_dev": 1},
        "joulewise.hazards.arm.Seams.host_cpu": "one idle CPU: ticks [0,0,logical_ns//10000000,0]",
        "joulewise.hazards.arm.Seams.smc_read": "None; use synthetic registry current (0 mA)",
        "joulewise.hazards.base.Context.run": "exact declared argv; default-deny; real pinned instrument child dispatched synchronously",
        "joulewise.hazards.base.Context.clocks": {"wall_origin_ns": 1700000000000000000,
            "monotonic_origin_ns": 1000000000000, "read_cost_ns": 100, "sleep": "advance logical ns"},
        "joulewise.hazards.instrument.subprocess.Popen": "only exact adapter-built sampler argv; synthetic plist frames",
        "joulewise.hazards.instrument.subprocess.run": "declared group-absence result for synthetic pid; otherwise default-deny",
    }
    manifest["declared_inputs"] = {
        "battery": {"ExternalConnected": "Yes", "IsCharging": "No", "InstantAmperage": 0,
            "Amperage": 0, "Voltage": 12000, "UpdateTime": "current synthetic wall second"},
        "thermal": 0, "boot_uuid": BOOT, "census": {"returncode": 1, "stdout": ""},
        "process_table": "pid 4000, parent 1, zero CPU time, command fixture",
        "sampler": {"frames": 300, "interval_ns": 100000000, "cpu_power_mw": 500,
            "gpu_power_mw": 0, "ane_power_mw": 0, "thermal_pressure": "Nominal"},
        "network_time_off": {"returncode": 126 if args.denied_off else 0,
            "stdout": "" if args.denied_off else "Network Time is already off.\n",
            "stderr": "RL-49 default deny" if args.denied_off else "", "executed": False},
    }
    manifest["guard_checks"] = {
        "undeclared_argv": ["/fixture/undeclared-action"],
        "native_argv": [sys.executable, "-B", "-c", "raise SystemExit(0)"],
        "outside_write": str(root.parent / "r12-must-not-create"),
        "expected": "deny all three before native execution or file creation",
    }
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    command = [sys.executable, "-B", str(Path(__file__).resolve()), "--worker", "--out", str(root)]
    if args.denied_off:
        command.append("--denied-off")
    return subprocess.run(command, cwd=root, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
