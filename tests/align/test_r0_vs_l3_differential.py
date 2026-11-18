"""Frozen synthetic R0 versus admitted L3 acceptance, PR 824 / audits 1–8.

Run from the candidate checkout: python3.13 -B /path/to/this_file.py
Also discoverable by unittest and pytest. R0_CANDIDATE can override the cwd.
The reference is commit 9c40e4e5d9fa453cce3c70984e11fa382b7d4591.
Matching local sources and Git blobs suffice offline. R0_L3_SOURCE selects an
admitted checkout; R0_L3_GIT selects a separate bare repo or working tree.
With neither override, shallow checkouts can read missing pinned Python blobs
from public GitHub over HTTPS. Both simulation workers always run offline.

Each lane runs its own real runner.main, QuietGuard, process parser, identity
filter, liveness census and publication code in a separate interpreter. Only
external inputs, work payloads, provenance and the daemon timer are synthetic.
Refusal at an admission is compared there, even if R0 refuses later. A
recorded L3 flag triggers the requested exit-2/no-pass rule, including when
L3 itself published pass. Audit expectations also check facts L3 never
sampled (e.g. a worker seen only at 15 s). Those failures count separately.
At publication the old runner has no hook. On a would-be pass we query its
actual guard at the same final fixture instant, retaining its native CLI exit
and report separately. The candidate gets no extra guard call from this test.
"""
from __future__ import annotations

from contextlib import contextmanager, nullcontext, redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import datetime, timezone
import errno
import hashlib
from io import StringIO
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from urllib.request import urlopen
from unittest.mock import patch


# Git blob IDs for the reference's complete imported project source closure.
# The oracle never imports a candidate dependency based on its filename alone.
ORACLE = """
c9e02c3f0c86f48bfb1e8b6165f264773243143c joulewise/__init__.py
f490f33b1e90abf2419fc27f4a863dd3dc284e52 joulewise/agent_identity.py
e508791dc40df74851ca072baa7baa3e15117da6 joulewise/align/__init__.py
28b2b37d0d72a2d17d4d4ef3e47ef7270f9055b9 joulewise/align/apple/__init__.py
9fffc4b91592413a834de7460f499d9adc702725 joulewise/align/apple/sampling.py
8a1a96dcb10ebb16809717af15918d5366b0d31c joulewise/align/apple/smc_enumeration.py
8ebd4d528bfdd9efab966c927cc01944c5eea6cb joulewise/align/apple/thermal.py
080989353a5b128f29282128ed5233424f4f1b14 joulewise/align/interfaces.py
c51426e52d591375c844c5cc087288ffe1ba8b09 joulewise/align/r0.py
6f7e4ffeb546622410354ee837273e3f2ebf2fe4 joulewise/align/r0_host.py
d60b9270876e1d9379ec404c9796b4480bfabcac joulewise/align/r0_runner.py
25be7c228a5f57f38c8bf682c135827ae6bb9d54 joulewise/align/r0_step.py
e2029a6d2ec1142690bb24a1f05a3913ec989627 joulewise/align/records.py
287a358c4a67a2f39b6e36e866c6460377c75afa joulewise/axi_decode_config.py
216a5caa42f3f6db1c3e516d6c2acfaebbd3524b joulewise/battery_float.py
e81765e5e26093c0155e31ce113d06f4ca450cca joulewise/corecaptured_loop.py
b3118b16710ab9311d4f4f26294513955bbc692b joulewise/hazards/__init__.py
4e6023b56f0a228bc7e6f8fdac7af9394d698d2f joulewise/hazards/base.py
d0639fe16b34450fd2eda0aff560d762f3350c2c joulewise/hazards/contention.py
879ce820e579fe4a08a6c1e2af64f580d58ba2e0 joulewise/idle_admission.py
2340e8d54002ad812795e0d529723de3cf77c348 joulewise/measurement_liveness.py
452da0de9363555dff3cf6f0f65b327b45e354fa joulewise/night_gate.py
104210c2c3d410c60fa6ab744ee28ffafbe19896 joulewise/night_kinds.py
7c82e7812b02c2ca197facfb7edde71af5d3bded joulewise/prewindow.py
f23efb46bac0565cd1ed96cb3c0a7815498aa8e9 joulewise/quiet_admission.py
d832777af088da5b60a261fdb21e7b5ae48f13f0 joulewise/schemas.py
32856ca439e08f1cfd9a028e04b79756635d417e joulewise/validation.py
""".strip()
EPOCH = 1_600_000_000
PID = 7421
TOKEN = "Sun Sep 13 12:25:00 2020"


@dataclass(frozen=True)
class Process:
    args: str
    born: int = -100
    gone: int = 1000
    cpu_at: int = 0
    centiseconds: int = 0
    zombie_at: int = 1000
    lose_args: bool = False
    pid: int = PID

    def row(self, now):
        if not self.born <= now < self.gone:
            return None
        exe = self.args.split()[0]
        name = Path(exe).name
        zombie = now >= self.zombie_at
        return (self.pid, self.born, 0 if zombie or now < self.cpu_at else self.centiseconds,
                name, f"({name})" if zombie and self.lose_args else self.args)


@dataclass(frozen=True)
class Case:
    name: str
    processes: tuple = ()
    schedule: str = "host"
    end: int = 40
    tree: str = "clean"
    tree_at: int = 0
    fault: str = ""
    fault_at: int = 45
    ticks: tuple | None = None
    must_refuse: bool = False
    windows: tuple = ()
    oracle_witness: str = ""
    host_error: bool = False


CLAUDE = "/usr/local/bin/claude"
APP = "/Applications/Claude.app/Contents/MacOS/Claude"
CHAIN = "python3 scripts/run_campaign.py"
WORKER = "mdworker_shared"
ARG_WORKER = "python3 mdworker_task.py"


def scenarios():
    yield Case("clean_host", oracle_witness="clean")
    yield Case("clean_all_admissions", schedule="multi", end=56, oracle_witness="clean")
    yield Case("clean_inventory", schedule="inventory", oracle_witness="clean")
    queued = Process(WORKER, cpu_at=45, centiseconds=180)
    for name, opts in (
        ("audit1_final_host_clock_launchctl", dict(fault="late_host", end=45)),
        ("audit1_final_inventory_eof_launchctl", dict(fault="late_inventory", schedule="inventory")),
        ("audit1_busy45_then_census60", dict(processes=(queued,), fault="launchctl",
                                              fault_at=60, end=60, windows=((15, 45),))),
        ("audit1_busy45_then_stall96", dict(processes=(queued,), ticks=(45,), end=96,
                                            windows=((15, 45),))),
        ("audit1_busy_then_overlong_sampled_window", dict(processes=(queued,), ticks=(45, 105, 120),
                                                          end=120, windows=((15, 45),))),
        ("audit2_installed_agent_readable", dict(tree="installed", tree_at=45, end=45)),
        ("audit2_installed_agent_listing_eacces", dict(tree="installed", tree_at=45,
                                                       fault="agents_eacces", end=45)),
        ("audit2_host_error_busy45_then_bad_census60", dict(processes=(queued,), end=60,
                 fault="launchctl", fault_at=60, host_error=True, windows=((15, 45),))),
        ("audit3_missing_parent_before_census", dict(tree="missing", tree_at=45, end=45)),
        ("audit3_observed_parent_listing_enoent", dict(fault="parent_enoent", end=45)),
        ("audit4_configured_alias_readlink_eio", dict(tree="alias", fault="link_eio", end=45)),
        ("audit4_configured_alias_readlink_enoent", dict(tree="alias", fault="link_enoent", end=45)),
        ("audit4_observed_chain_started_read_enoent", dict(tree="owner", tree_at=45,
                                                           fault="marker_enoent", end=45)),
        ("audit4_observed_chain_started_read_eio", dict(tree="owner", tree_at=45,
                                                        fault="marker_eio", end=45)),
        ("audit4_observed_registry_open_enoent", dict(tree="registry", tree_at=45,
                                                      fault="registry_enoent", end=45)),
        ("audit4_inventory_required_listing_eacces", dict(schedule="inventory",
                                                          fault="parent_eacces", fault_at=0)),
        # Historical concurrent swaps are represented by their observable states
        # at the next census. No second actor mutates a directory during a read.
        ("audit5_configured_alias_removed", dict(tree="removed_alias", tree_at=45, end=45)),
        ("audit5_configured_alias_retargeted_live", dict(tree="retarget", tree_at=45, end=45)),
        ("audit5_configured_alias_live_before_check", dict(tree="retarget")),
        ("audit5_live_owner_stored_Night", dict(tree="capital_night", tree_at=45, end=45)),
        ("audit5_live_owner_stored_night", dict(tree="owner", tree_at=45, end=45)),
        ("audit6_desktop_app_three_censuses", dict(processes=(Process(APP, 45),), end=75)),
        ("audit7_agent_started_at_10", dict(processes=(Process(CLAUDE, 10),),
                                             oracle_witness="host_admit")),
        ("audit7_agent_left_before_next_tick", dict(processes=(Process(CLAUDE, 10, 42),),
                                                    end=75, oracle_witness="host_admit")),
        ("audit7_inventory_census_eio_only", dict(schedule="inventory", fault="inventory_eio")),
        ("audit7_inventory_scan_and_read_eio", dict(schedule="inventory", fault="double_eio")),
        ("audit8_campaign_started_at_10", dict(processes=(Process(CHAIN, 10, centiseconds=2),),
                                                oracle_witness="host_admit")),
    ):
        yield Case(name, must_refuse=True, **opts)

    yield Case("audit1_busy_interval_leaves_later_window_eligible",
               (queued, Process(ARG_WORKER, born=65, cpu_at=75, centiseconds=180, pid=PID+1)),
               end=90, windows=((15, 45, PID), (45, 75, PID+1)))
    for born in (20, 35):
        yield Case(f"audit3_worker_born_{born}_exits_before60",
                   (Process(WORKER, born, 57, 45, 180),), end=60, windows=((15, 45), (30, 60)))
    for name, args, born, gone, zombie, lost in (
        ("audit6_baseline_resident_exited", WORKER, -100, 29, 1000, False),
        ("audit6_baseline_alive_control", WORKER, -100, 1000, 1000, False),
        ("audit7_zeroed_zombie", WORKER, -100, 1000, 30, False),
        ("audit7_zombie_removed_control", WORKER, -100, 29, 1000, False),
        ("audit8_args_only_zombie", ARG_WORKER, 5, 1000, 30, True),
        ("audit8_args_only_still_running", ARG_WORKER, 5, 1000, 1000, False),
        ("audit8_args_only_fully_exited", ARG_WORKER, 5, 29, 1000, False),
    ):
        yield Case(name, (Process(args, born, gone, 15, 180, zombie, lost),),
                   end=30, windows=((0, 30),))

    agents = (CLAUDE, "/usr/local/bin/CoDeX", "/usr/local/bin/codex", APP,
              "/Applications/Codex.app/Contents/MacOS/Codex",
              "/Applications/CLAUDE.APP/Contents/MacOS/CLAUDE")
    chains = (CHAIN, "sh /fixture/run_NIGHT.sh", "/fixture/window-chain.zsh",
              "python3 scripts/align_r1_rehearsal.py", "python3 scripts/align_r0_checks.py",
              "python3 scripts/run_b5_analysis.py", "/fixture/chain", "/usr/bin/powermetrics")
    # Wall times denote input transitions, never precomputed pgrep/ps verdicts.
    # The pulse at 58 starts during terminal report serialization.
    phases = (("baseline_open", -3, 5), ("baseline_mid", 10, 20),
              ("baseline_close", 29, 31), ("first_unit", 31, 33),
              ("host_return", 39, 41), ("disk_admission", 41, 43),
              ("disk_unit", 43, 44.5), ("background", 44.5, 50),
              ("last_forced", 55, 57), ("pre_publication", 57, 1000))
    for family, commands in (("agent", agents), ("chain", chains)):
        for index, cmd in enumerate(commands):
            for label, start, stop in phases:
                yield Case(f"{family}_{index}_{label}", (Process(cmd, start, stop),),
                           schedule="multi", end=56,
                           oracle_witness=("prepass" if label == "pre_publication" and index == 0
                                           else ""))
    # Equal, just below and just above 1.50 CPU seconds / 30 seconds.
    for at in (15, 30, 45, 60):
        for delta in (149, 150, 151, 180):
            for kind, args in (("ucomm", WORKER), ("argv", ARG_WORKER)):
                for state, born, gone, zombie in (
                    ("resident", -100, 1000, 1000), ("born", at-8, 1000, 1000),
                    ("exit", at-8, at+9, 1000), ("zombie", at-8, 1000, at+12),
                ):
                    p = Process(args, born, gone, at, delta, zombie, lose_args=True)
                    witness = ""
                    if at == 30 and state == "resident":
                        witness = "over_limit" if delta > 150 else "within_limit"
                    yield Case(f"cpu_{kind}_{state}_at{at}_{delta}cs", (p,), end=at+30,
                               oracle_witness=witness)
    # Distinct identities coexist; reuse of a PID must not join CPU counters.
    yield Case("two_workers_opposite_thresholds", (
        Process(WORKER, cpu_at=30, centiseconds=149),
        Process(ARG_WORKER, cpu_at=30, centiseconds=151, pid=PID+1)), end=60)
    yield Case("reused_pid_after_exit", (
        Process(WORKER, -100, 39, 15, 180), Process(ARG_WORKER, 40, 1000, 45, 149)), end=75)
    for tree in ("missing", "dangling_alias", "alias", "owner", "registry", "bad_marker",
                 "installed", "capital_night", "closed", "stale", "pending"):
        yield Case("stationary_" + tree, tree=tree,
                   must_refuse=tree not in ("alias", "closed", "stale"))
    for name, option in (("loaded_launchagent", "loaded"), ("bad_launchctl", "launchctl"),
                         ("args_table_unavailable", "bad_args"), ("cpu_table_malformed", "bad_cpu")):
        for start in (0, 30, 40, 45, 56):
            yield Case(f"{name}_at{start}", schedule="multi", end=56, fault=option, fault_at=start)


class FixtureError(BaseException):
    """A broken input driver must escape production's fail-closed exception handling."""


class SamplerTimer:
    """A virtual timer for the real daemon loop. One permit = one elapsed cadence."""
    def __init__(self):
        self.cv = threading.Condition()
        self.issued = self.parked = 0
        self.stopped = False

    def is_set(self):
        with self.cv:
            return self.stopped

    def set(self):
        with self.cv:
            self.stopped = True
            self.cv.notify_all()

    def wait(self, timeout):
        with self.cv:
            self.parked += 1
            self.cv.notify_all()
            self.cv.wait_for(lambda: self.stopped or self.issued >= self.parked)
            return self.stopped

    def pulse(self, asynchronous=False):
        with self.cv:
            if self.stopped:
                return
            self.issued += 1
            self.cv.notify_all()
            if not asynchronous and not self.cv.wait_for(
                    lambda: self.stopped or self.parked > self.issued, timeout=5):
                raise FixtureError("synthetic sampler did not return to its timer")


class Fixture:
    """Both lanes see the same clock, processes, census roots, and work boundaries."""
    def __init__(self, case, root):
        self.case, self.root = case, root
        self.now = 0
        self.timer = None
        self.next_tick = 45
        self.applied = False
        self.accepted = []
        self.phase = "baseline"
        self.work_started = []
        self.faults = []
        self.refused_at = None
        self.probe_waiting = threading.Event()
        self.release_probe = threading.Event()
        self.parent = root / "required"
        self.target = root / "alias-target"
        self.agents = root / "home/Library/LaunchAgents"
        self.agents.mkdir(parents=True)
        self.target.mkdir()
        if case.tree in ("alias", "retarget", "removed_alias", "dangling_alias"):
            self.parent.symlink_to(self.target, target_is_directory=True)
        else:
            self.parent.mkdir()
        self.inventory_blob = root / "input/blob"
        self.inventory_blob.parent.mkdir()
        self.inventory_blob.write_bytes(b"only synthetic inventory bytes")
        self.apply_tree()

    def apply_tree(self):
        c = self.case
        if self.applied or self.now < c.tree_at:
            return
        self.applied = True
        tree = c.tree
        parent = self.parent
        if tree == "missing":
            parent.rmdir()
        elif tree == "removed_alias":
            parent.unlink()
        elif tree == "dangling_alias":
            self.target.rmdir()
        elif tree == "retarget":
            live_target = self.root / "occupied"
            live_target.mkdir()
            parent.unlink()
            parent.symlink_to(live_target, target_is_directory=True)
            tree = "owner"
        if tree == "installed":
            (self.agents / "com.joulewise.night.fixture.plist").write_text("fixture")
        elif tree == "registry":
            registry = parent / "active-campaigns"
            registry.mkdir()
            (registry / "fixture.json").write_text(json.dumps({
                "schema": "joulewise.active_campaign.v1", "pid": PID, "start_time": TOKEN,
                "nonce": "synthetic", "runs_root": str(self.root / "unused")}))
        elif tree in ("owner", "capital_night", "bad_marker", "closed", "stale", "pending"):
            night = parent / "plan" / ("Night" if tree == "capital_night" else "night")
            night.mkdir(parents=True)
            data = json.dumps({"pid": PID, "pgid": PID, "start_time": TOKEN})
            if tree == "pending":
                (night / "launch.pending").write_text(data)
            else:
                (night / "chain.started").write_text("{" if tree == "bad_marker" else data)
                if tree == "closed":
                    (night / "chain.exited").write_text('{"exit_code":0,"epoch_s":1,"monotonic_ns":1}')

    def clock(self):
        if (self.case.fault == "late_host" and self.probe_waiting.is_set()
                and threading.current_thread() is threading.main_thread() and not self.release_probe.is_set()):
            self.release_probe.set()
            with self.timer.cv:
                if not self.timer.cv.wait_for(lambda: self.timer.stopped, timeout=5):
                    raise FixtureError("in-flight launchctl failure did not latch")
        return self.now

    def sleep(self, seconds):
        self.now += seconds
        self.apply_tree()

    def move(self, end):
        if end < self.now:
            raise FixtureError(f"fixture moved backwards at {self.phase}: {self.now} -> {end}")
        while self.next_tick <= end:
            at = self.next_tick
            self.next_tick += 15
            self.now = at
            self.apply_tree()  # Before either lane starts its next census.
            if self.timer and (self.case.ticks is None or at in self.case.ticks):
                late = self.case.fault == "late_host" and at == 45
                self.timer.pulse(asynchronous=late)
                if late and not self.probe_waiting.wait(5):
                    raise FixtureError("background launchctl did not reach fixture")
        self.now = end
        self.apply_tree()

    def processes(self):
        rows = [(1, -300, 100, "launchd", "/sbin/launchd")]
        rows.extend(row for p in self.case.processes if (row := p.row(self.now)) is not None)
        if self.case.tree in ("owner", "capital_night", "registry", "pending", "retarget"):
            if self.now >= self.case.tree_at:
                rows.append((PID, -100, 0, "fixture-owner", "/fixture/owner"))
        return rows

    def identity(self, pid):
        from joulewise import agent_identity
        row = next((r for r in self.processes() if r[0] == pid), None)
        if row is None:
            return None
        args = row[-1].split()
        return agent_identity.ProcessInfo(pid, 1, pid, args[0], tuple(args))

    def observe(self, pid):
        from joulewise.measurement_liveness import Identity
        return Identity("LIVE", TOKEN) if self.identity(pid) else Identity("DEAD")

    def run(self, argv, **kwargs):
        from joulewise import prewindow
        from joulewise.hazards import contention
        fault = self.case.fault if self.now >= self.case.fault_at else ""
        code, out, err = 0, "", ""
        if argv[0] == "/bin/launchctl":
            if fault == "late_host" and threading.current_thread() is not threading.main_thread():
                self.probe_waiting.set()
                if not self.release_probe.wait(5):
                    raise FixtureError("final check did not release the synthetic probe")
            if fault in ("launchctl", "late_host", "late_inventory"):
                self.faults.append("launchctl")
                code, err = 1, "injected indeterminate service census"
            elif fault != "loaded":
                code, err = 113, "Could not find service"
        elif argv[0] == "/usr/bin/pgrep":
            options = "".join(argv[1:-1])
            if "f" not in options or "l" not in options:
                raise FixtureError(f"unsupported pgrep query: {argv!r}")
            regex = re.compile(argv[-1], re.I if "i" in options else 0)
            out = "".join(f"{pid} {args}\n" for pid, _, _, _, args in self.processes() if regex.search(args))
            code = 0 if out else 1
        elif tuple(argv) == tuple(prewindow.PS_ARGV):
            out = "".join(f"{pid} 0.0 {args}\n" for pid, _, _, _, args in self.processes())
            code = int(fault == "bad_args")
        elif tuple(argv) == tuple(contention.PS_ARGV):
            out = "PID PPID STARTED TIME UCOMM\n"
            for pid, born, cs, name, _ in self.processes():
                start = datetime.fromtimestamp(EPOCH + born, timezone.utc).strftime("%a %b %d %H:%M:%S %Y")
                out += f"{pid} {0 if pid == 1 else 1} {start} 0:{cs//100:02}.{cs%100:02} {name}\n"
            if fault == "bad_cpu":
                out += "malformed fixture row\n"
        else:
            raise FixtureError(f"unhandled synthetic command {argv!r}")
        return subprocess.CompletedProcess(argv, code, out, err)

    def factory(self, parents):
        from joulewise import measurement_liveness
        from joulewise.align.r0_host import QuietGuard

        def inspect(**kwargs):
            return measurement_liveness.census(**kwargs, observer=self.observe)

        self.guard = guard = QuietGuard(parents, run=self.run, inspect_custody=inspect,
                                        clock=self.clock, sleep=self.sleep)
        if hasattr(guard, "_stop_sampler"):
            self.timer = guard._stop_sampler = SamplerTimer()
            guard.host_reader = None
            guard.wall_clock_ns = self.wall_ns
        self.real_check = real_check = guard.check

        def scheduled_check(*args, **kwargs):
            phase = self.phase
            try:
                result = real_check(*args, **kwargs)
            except Exception:
                self.refused_at = self.now
                raise
            if kwargs.get("force") and phase not in self.accepted:
                self.accepted.append(phase)
            return result
        guard.check = scheduled_check
        return guard

    def wall_ns(self):
        return int((EPOCH + self.now) * 1_000_000_000)

    def checkout_head(self, argv):
        self.phase = "host_admit"
        return "synthetic-head"

    def host(self):
        self.work_started.append("host")
        self.phase = "host_return"
        self.move(40 if self.case.schedule == "multi" else self.case.end)
        if self.case.host_error:
            raise RuntimeError("injected host failure")
        return {"status": "pass"}

    def disk(self, *args):
        self.work_started.append("disk")
        self.phase = "last_forced"
        self.move(56)
        return {"status": "diagnostic"}

    @contextmanager
    def io_faults(self):
        """Inject syscall results on fixture inodes only; do not race a live read."""
        c = self.case
        real_scan, real_list, real_open, real_link = os.scandir, os.listdir, os.open, os.readlink
        path_open = Path.open

        def points_to(arg, path):
            if isinstance(arg, int):
                try:
                    return os.path.samestat(os.fstat(arg), path.stat())
                except FileNotFoundError:
                    return False
            return isinstance(arg, (str, bytes, os.PathLike)) and Path(os.fsdecode(arg)) == path

        def fail(number, path):
            self.faults.append(c.fault)
            raise OSError(number, "synthetic census fault", str(path))

        def listing(arg):
            if self.now < c.fault_at:
                return
            if c.fault == "agents_eacces" and points_to(arg, self.agents):
                fail(errno.EACCES, self.agents)
            if c.fault in ("parent_eacces", "parent_enoent", "inventory_eio", "double_eio"):
                if points_to(arg, self.parent):
                    n = {"parent_eacces": errno.EACCES, "parent_enoent": errno.ENOENT}
                    fail(n.get(c.fault, errno.EIO), self.parent)

        def scandir(arg="."):
            listing(arg)
            return real_scan(arg)

        def listdir(arg="."):
            listing(arg)
            return real_list(arg)

        def open_fd(path, flags, *args, **kwargs):
            if self.now >= c.fault_at and c.fault in ("marker_eio", "marker_enoent", "registry_enoent"):
                name = "active-campaigns" if c.fault == "registry_enoent" else "chain.started"
                if Path(path).name == name:
                    fail(errno.EIO if c.fault == "marker_eio" else errno.ENOENT, path)
            return real_open(path, flags, *args, **kwargs)

        def readlink(path, *args, **kwargs):
            if self.now >= c.fault_at and c.fault in ("link_eio", "link_enoent") and points_to(path, self.parent):
                fail(errno.EIO if c.fault == "link_eio" else errno.ENOENT, path)
            return real_link(path, *args, **kwargs)

        @contextmanager
        def inventory_file(*args, **kwargs):
            self.work_started.append("inventory")
            with path_open(self.inventory_blob, *args, **kwargs) as stream:
                class Reader:
                    def read(_, size):
                        chunk = stream.read(size)
                        if not chunk and self.now < 45:
                            self.move(45)
                            if c.fault == "double_eio":
                                self.faults.append("inventory read")
                                raise OSError(errno.EIO, "synthetic inventory input failure")
                        return chunk
                yield Reader()

        def opened(path, *args, **kwargs):
            if path == self.inventory_blob:
                return inventory_file(*args, **kwargs)
            # L3 uses Path.read_text; the strict guard opens relative to a held fd.
            mode = args[0] if args else kwargs.get("mode", "r")
            if (mode.startswith("r") and self.now >= c.fault_at and path.name == "chain.started"
                    and c.fault in ("marker_enoent", "marker_eio")):
                fail(errno.ENOENT if c.fault.endswith("enoent") else errno.EIO, path)
            return path_open(path, *args, **kwargs)

        with (patch.object(os, "scandir", scandir), patch.object(os, "listdir", listdir),
              patch.object(os, "open", open_fd), patch.object(os, "readlink", readlink),
              patch.object(Path, "open", opened)):
            yield


def run_case(case, root, provenance, oracle):
    from joulewise import agent_identity, measurement_liveness as live
    from joulewise.align import r0, r0_runner as runner
    f = Fixture(case, root)
    default_root = root / "default-parent"
    default_root.mkdir()
    config = root / "config.json"
    config.write_text(json.dumps({
        "schema": "joulewise.align.r0.config.v1", "models": {"D": {"source": str(root / "D")}},
        "shade_cache": str(root / "unused"), "disk_path": str(root),
        "custody_parents": [str(f.parent)], "offloads": [], "measurement_hw_model": "Synthetic",
        "anchor_source": str(root / "anchor")}))
    out = root / "out"
    argv = ["--config", str(config), "--output", str(out), "--checks",
            "host,disk" if case.schedule == "multi" else "host"]
    inventory = case.schedule == "inventory"
    if inventory:
        argv += ["--inventory", str(f.inventory_blob.parent)]
    real_filter = agent_identity.filter_census
    real_save = runner.save_report

    def save(path, report):
        # Make time a property of the workload and persisted progress, not of
        # the number of guard calls. Extra candidate checks see the same input.
        result = real_save(path, report)
        if report["status"] == "pass":
            f.phase = "publication"
            if case.schedule == "multi":
                f.move(58)
        elif report["checks"]:
            row = report["checks"][-1]
            if row["status"] == "running" and row["check"] in ("host", "disk"):
                f.phase = row["check"] + "_unit"
                if case.schedule == "multi":
                    f.move(32 if row["check"] == "host" else 44)
            elif (row["check"] == "host" and row["status"] == "pass"
                  and case.schedule == "multi" and f.phase == "host_return"):
                f.phase = "disk_admit"
                f.move(42)
        return result

    def backend(*args):
        raise FixtureError("host-only CLI requested a model")

    def synthetic_group(pgid, signal):
        if (pgid, signal) != (PID, 0) or case.tree != "pending":
            raise FixtureError("unexpected process group probe")

    stream = StringIO()
    exception = None
    publication_refused = False
    with (patch.dict(os.environ, {"HOME": str(root / "home"),
                                  live.CUSTODY_PARENT_ENV: str(default_root),
                                  live.ADDITIONAL_PARENTS_ENV: "[]"}),
          patch.object(time, "time_ns", f.wall_ns),
          patch.object(agent_identity, "filter_census",
                       lambda stdout, **kw: real_filter(stdout, inspector=f.identity, **kw)),
          patch.object(os, "killpg", synthetic_group), patch.object(os, "getpid", return_value=8001),
          patch.object(runner, "REPO", provenance),
          patch.object(r0, "NLL_REFERENCE_PATH", provenance / "reference.json"),
          patch.object(runner, "command", f.checkout_head),
          patch.object(runner, "deadline", lambda *_: nullcontext()),
          patch.object(runner, "softwareupdate_scan_forecast", create=True, return_value={"status": "unknown"}),
          patch.object(runner, "host_snapshot", f.host), patch.object(runner, "disk_census", f.disk),
          patch.object(runner, "save_report", save), f.io_faults(),
          redirect_stdout(stream), redirect_stderr(stream)):
        try:
            rc = runner.main(argv, guard_factory=f.factory, backend_factory=backend,
                             display_probe=None, lock_path=root / "lock")
            native_flag_count = len(f.guard.contention_flags)
            if oracle and rc == 0:
                # The legacy CLI has already made its decision. Exercise L3 at
                # the requested pre-pass instant without changing that result.
                try:
                    f.real_check(force=True)
                except runner.Refused:
                    publication_refused = True
        except (runner.Refused, OSError) as exc:
            # These exceptions escaping main give status 1 in the script entry point.
            native_flag_count = len(f.guard.contention_flags)
            exception = f"{type(exc).__name__}: {exc}"
            rc = 1
        finally:
            f.release_probe.set()
            if f.timer:
                f.timer.set()
                f.guard.close()
    report = {}
    if not inventory:
        records = [p for p in [out / "report.json", *root.glob(".out.r0-*/report.json")] if p.is_file()]
        if len(records) != 1:
            raise AssertionError(f"{case.name}: expected one actual terminal report, got {records}")
        report = json.loads(records[0].read_text())
    flags = [(r["interval"]["start_monotonic_s"], r["interval"]["end_monotonic_s"], b["pid"], b["start"])
             for r in f.guard.contention_flags for b in r["busy"]]
    judged = {(w["start_monotonic_s"], w["end_monotonic_s"])
              for receipt in report.get("census", []) for w in receipt.get("cpu_intervals", [])}
    intervals = [(w["start_monotonic_s"], w["end_monotonic_s"])
                 for receipt in report.get("census", []) for w in receipt.get("cpu_intervals", [])
                 if w.get("contention_flag")]
    intervals.extend((flag["interval"]["start_monotonic_s"], flag["interval"]["end_monotonic_s"])
                     for row in report.get("checks", []) for flag in row.get("contention_flags", []))
    reason = report.get("refusal") or f.guard.failure
    refused = bool(reason)
    status = report.get("status")
    if inventory:
        status = "pass" if rc == 0 and out.exists() else "unpublished"
    # An implementation exception is never evidence that a guard is stricter.
    errs = [r["error"] for r in report.get("checks", ()) if r.get("error")]
    if report.get("error"):
        errs.append(report["error"])
    if case.host_error:
        errs = [e for e in errs if "injected host failure" not in e]
    if errs:
        raise AssertionError(f"{case.name}: unexpected runner failure {errs}")
    return dict(rc=rc, status=status, published=out.exists(), refused=refused, accepted=f.accepted,
                work_started=f.work_started,
                flags=flags, reason=str(reason or "")[:250], exception=exception,
                check_status=[r["status"] for r in report.get("checks", ())],
                recorded=report.get("contention", {}).get("guard_flags"),
                guard_count=len(f.guard.contention_flags), faults=f.faults, report_intervals=intervals,
                judged_windows=sorted(judged),
                report_refusal=bool(report.get("refusal")), diagnostic=stream.getvalue()[-450:],
                refused_at=f.refused_at if f.refused_at is not None else f.now if refused else None,
                native_flag_count=native_flag_count, publication_refused=publication_refused)


def restrict_worker(source, work):
    """Reject external commands, host process inspection and out-of-fixture data opens."""
    stdlib = tuple(Path(p).resolve() for p in (sys.base_prefix, sys.prefix))
    roots = (work, source, *stdlib)
    def audit(event, args):
        if event in {"subprocess.Popen", "os.system", "os.kill", "os.killpg",
                     "os.posix_spawn", "socket.connect", "socket.getaddrinfo"}:
            raise FixtureError("unexpected external operation " + event)
        if event not in ("open", "os.listdir", "os.scandir") or not isinstance(args[0], (str, bytes)):
            return
        path = Path(os.path.abspath(os.fsdecode(args[0])))
        if path.is_relative_to(work):
            return
        if event != "open" and any(path.is_relative_to(r) for r in roots):
            return
        if event == "open" and not args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC):
            if path.is_relative_to(source) and path.suffix in (".py", ".pyc"):
                return
            if any(path.is_relative_to(r) for r in stdlib):
                return
        raise FixtureError(f"outside synthetic worker: {event} {path}")
    sys.addaudithook(audit)


def worker(source, work, oracle):
    os.chdir(work)
    sys.path.insert(0, str(source))
    # Prime stdlib locale/time-zone tables before the I/O boundary.
    datetime.strptime("2001-02-03", "%Y-%m-%d")
    restrict_worker(source, work)
    from joulewise.align import r0_runner
    prov = work / "provenance"
    for filename in ("joulewise/align/r0_host.py", "joulewise/align/r0_mlx.py",
                     "joulewise/align/r0_step.py", "scripts/align_r0_checks.py",
                     r0_runner.LOAD_REFERENCE_NOTE, "reference.json"):
        path = prov / filename
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text("synthetic provenance\n")
    result = {}
    for c in scenarios():
        with tempfile.TemporaryDirectory(dir=work) as tmp:
            result[c.name] = run_case(c, Path(tmp), prov, oracle)
    print(json.dumps(result, allow_nan=False))


def blob_id(raw):
    return hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()


def stage_oracle(candidate, destination):
    alternate = os.environ.get("R0_L3_SOURCE")
    checkout = Path(os.environ.get("R0_L3_GIT", candidate))
    for line in ORACLE.splitlines():
        oid, name = line.split()
        for tree in ([Path(alternate), candidate] if alternate else [candidate]):
            path = tree / name
            if path.is_file():
                raw = path.read_bytes()
                if blob_id(raw) == oid:
                    break
        else:
            # Git may read local objects only. HTTPS fallback is limited to these
            # fingerprinted public .py files and runs outside both guard processes.
            result = subprocess.run(["git", "-C", str(checkout), "cat-file", "blob", oid],
                                    env={**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_ALLOW_PROTOCOL": ""},
                                    capture_output=True)
            raw = result.stdout
            if result.returncode:
                if alternate or "R0_L3_GIT" in os.environ:
                    raise RuntimeError(f"missing pinned {name} ({oid}) in the supplied local sources")
                url = ("https://raw.githubusercontent.com/mpmdw/JouleWise/"
                       "9c40e4e5d9fa453cce3c70984e11fa382b7d4591/" + name)
                with urlopen(url, timeout=15) as response:
                    raw = response.read()
            if blob_id(raw) != oid:
                raise RuntimeError(f"wrong admitted source for {name}; expected Git blob {oid}")
        dest = destination / name
        dest.parent.mkdir(exist_ok=True, parents=True)
        dest.write_bytes(raw)


def lane(source, work, role):
    work.mkdir()
    command = [sys.executable, "-I", "-B", str(Path(__file__).resolve()),
               "--synthetic-worker", str(source), str(work), role]
    env = {"HOME": str(work), "TMPDIR": str(work), "LC_ALL": "C", "TZ": "UTC",
           "PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1"}
    return json.loads(subprocess.check_output(command, cwd=work, env=env, text=True, timeout=240))


def check_case(c, old, new):
    diff, audit, oracle_errors = [], [], []
    rejected = (new["rc"] == 2 and new["status"] != "pass"
                and (new["refused"] or new["guard_count"] > 0)
                and not (c.schedule == "inventory" and new["published"]))
    clean = lambda r: r["rc"] == 0 and r["status"] == "pass" and r["published"] and not r["flags"]
    if c.oracle_witness == "clean":
        if not clean(old):
            oracle_errors.append("clean control failed on admitted source")
        if not clean(new):
            audit.append("clean control failed on candidate")
    if c.oracle_witness == "host_admit":
        if not (old["refused"] and old["accepted"] == ["baseline"] and old["rc"] == 2):
            oracle_errors.append("admitted guard did not reproduce the 30 s refusal")
    if c.oracle_witness == "prepass" and not (old["rc"] == 0 and old["publication_refused"]):
        oracle_errors.append("publication-only pulse did not reach the frozen L3 guard")
    if c.oracle_witness in ("over_limit", "within_limit"):
        if old["refused"] or bool(old["flags"]) != (c.oracle_witness == "over_limit"):
            oracle_errors.append("admitted guard did not straddle the strict 0.05 boundary")
    if old["refused"]:
        if not rejected:
            diff.append("L3 refused; R0 did not exit 2 with a non-pass")
        if (set(new["accepted"]) - set(old["accepted"])
                or set(new["work_started"]) - set(old["work_started"])):
            diff.append("R0 admitted a checkpoint beyond the L3 refusal")
    if old["flags"]:
        if not rejected:
            diff.append("L3 flagged; R0 did not exit 2 with a non-pass")
        for start, end, pid, identity in old["flags"]:
            if new["refused"] and new["refused_at"] <= end:
                continue  # A stricter refusal can preclude this window.
            exact = [start, end] in new["judged_windows"]
            found = any(p == pid and birth == identity and
                        ((a, b) == (start, end) if exact else a < end and b > start)
                        for a, b, p, birth in new["flags"])
            if not found:
                diff.append(f"missing L3 flag for PID {pid} in {start:g}-{end:g} s")
                break
    if c.must_refuse and (not rejected or not new["refused"]):
        audit.append("expected a census refusal and exit 2")
    if c.must_refuse and new["published"] and c.name.startswith("audit"):
        audit.append("published after a required census refusal")
    if c.windows:
        expected = {w if len(w) == 3 else (*w, PID) for w in c.windows}
        actual = {(a, b, pid) for a, b, pid, _ in new["flags"]}
        missing = expected - actual
        # Preserve completed windows on a later failure. A genuine earlier
        # refusal may prevent a CPU window from existing in the first place.
        if new["refused"]:
            missing = {w for w in missing if w[1] < new["refused_at"]}
        if missing:
            audit.append(f"missing audited CPU windows {sorted(missing)}")
        persisted = {tuple(interval) for interval in new["report_intervals"]}
        if any((a, b) not in persisted for a, b, pid in expected & actual):
            audit.append("terminal report lost an audited contention interval")
    if c.fault == "late_host" and "pass" in new["check_status"]:
        audit.append("host check retained a pass after the in-flight census failed")
    if c.host_error and (not new["report_refusal"] or "LaunchAgent" not in new["reason"]
                         or "fail" not in new["check_status"]):
        audit.append("host failure lost the separate census refusal")
    if c.schedule != "inventory" and new["recorded"] != new["guard_count"]:
        audit.append("terminal report lost guard flags")
    if c.name.startswith("audit") and c.fault and not new["refused"] and not new["faults"]:
        audit.append("fault never reached the census")
    if c.fault == "double_eio" and ("inventory read" not in new["faults"]
                                    or not new["refused"] or "errno 5" not in new["diagnostic"]):
        audit.append("inventory read failure lost the concurrent census I/O diagnostic")
    if new["rc"] not in (0, 2) or new["exception"]:
        audit.append(f"unhandled CLI outcome {new['rc']} {new['exception']}")
    return diff, audit, oracle_errors


class TestR0VsAdmittedL3(unittest.TestCase):
    def test_frozen_differential(self):
        candidate = Path(os.environ.get("R0_CANDIDATE", Path.cwd())).resolve()
        if not (candidate / "joulewise/align/r0_runner.py").is_file():
            self.fail("run from the R0 checkout or set R0_CANDIDATE")
        cases = list(scenarios())
        self.assertEqual(len(cases), len({c.name for c in cases}))
        with tempfile.TemporaryDirectory(prefix="r0-differential-") as tmp:
            root = Path(tmp).resolve()
            oracle = root / "admitted"
            stage_oracle(candidate, oracle)
            old = lane(oracle, root / "l3-fixtures", "admitted")
            new = lane(candidate, root / "r0-fixtures", "candidate")
        self.assertEqual(set(old), set(new))
        self.assertEqual(set(old), {c.name for c in cases})
        differences, audits, invalid, missing_evidence, flagged_pass = [], [], [], [], []
        for c in cases:
            o, n = old[c.name], new[c.name]
            d, a, errors = check_case(c, o, n)
            if d:
                differences.append(c.name)
                if all(reason.startswith("L3 flagged;") for reason in d) and n["flags"]:
                    flagged_pass.append(c.name)
                else:
                    missing_evidence.append(c.name)
            if a:
                audits.append(c.name)
            if errors:
                invalid.append(c.name)
            with self.subTest(scenario=c.name):
                if d or a or errors:
                    self.fail(" | ".join(d + a + errors) +
                                 f" [L3 {o['rc']}/{o['status']} flags={o['guard_count']};"
                                 f" prepass_refused={o['publication_refused']};"
                                 f" R0 {n['rc']}/{n['status']} flags={n['guard_count']}]")
        print(f"scenarios={len(cases)} laxer_than_L3={len(differences)} "
              f"lost_refusal_admission_or_flag={len(missing_evidence)} "
              f"retained_flag_but_passed={len(flagged_pass)} "
              f"additional_audit_only={len(set(audits)-set(differences))} "
              f"invalid_oracle_controls={len(invalid)}", flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--synthetic-worker"]:
        worker(Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve(), sys.argv[4] == "admitted")
    else:
        unittest.main()
