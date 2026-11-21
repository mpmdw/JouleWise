# Frozen differential acceptance v3 for PR 824.
# Run with python3.13 -B test_r0_vs_l3_differential.py from the candidate
# checkout, or set R0_CANDIDATE and R0_L3_SOURCE as documented below.
# The unchanged v2 module follows. The v3 cases precede its main dispatcher.
# END V3 HEADER
"""Frozen synthetic R0 versus admitted L3 acceptance, v2 (PR 824).

The 341 original cases and their assertions are preserved. Two additional
families exercise single-read process names and per-window CPU evidence.
Each family prints its own denominator and failure count. The threshold
oracle uses integer centiseconds, the printed lstart second and observable
read brackets. A worker's exact fractional lifetime is private to the fixture.
Darwin ps fallback source:
https://github.com/apple-oss-distributions/adv_cmds/blob/6bed8737a34dbb54782a18f47dccf933a9967a12/ps/print.c#L284-L289

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


def run_case(case, root, provenance, oracle, *, fixture_factory=Fixture):
    from joulewise import agent_identity, measurement_liveness as live
    from joulewise.align import r0, r0_runner as runner
    f = fixture_factory(case, root)
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


def worker(source, work, oracle, *, cases=scenarios, execute=run_case):
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
    for c in cases():
        with tempfile.TemporaryDirectory(dir=work) as tmp:
            result[c.name] = execute(c, Path(tmp), prov, oracle)
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


def lane(source, work, role, family=None):
    work.mkdir()
    command = [sys.executable, "-I", "-B", str(Path(__file__).resolve()),
               "--synthetic-worker", str(source), str(work), role]
    if family:
        command.append(family)
    env = {"HOME": str(work), "TMPDIR": str(work), "LC_ALL": "C", "TZ": "UTC",
           "PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1"}
    return json.loads(subprocess.check_output(command, cwd=work, env=env, text=True, timeout=900 if family else 240))


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


# v2. Freeze the class vocabulary here. Deriving the generator or oracle from
# the candidate's matchers would delete coverage when a matcher regressed.
_AGENT_NAMES = (
    ("claude", "/usr/local/bin"), ("codex", "/usr/local/bin"),
    ("Claude", "/Applications/Claude.app/Contents/MacOS"),
    ("Codex", "/Applications/Codex.app/Contents/MacOS"),
    ("codex-aarch64-apple-darwin", "/fixture/bin"), ("claude-code", "/fixture/bin"),
)
_CHAIN_NAMES = tuple(
    stem + suffix
    for stem in ("powermetrics", "run_campaign", "run_night", "window-chain", "window_chain",
                 "align_r1_rehearsal", "align_r0_checks", "run_b5_analysis", "chain")
    for suffix in ("", ".py", ".sh", ".zsh")
)
_CPU_NAMES = (
    "XProtect", "XProtectRemediatorMRT", "mds_stores", "mdworker", "mdworker_shared",
    "mdbulkimport", "backupd", "photoanalysisd", "softwareupdated", "Spotlight", "mediaanalysisd",
)


@dataclass(frozen=True)
class NameSighting:
    name: str
    group: str
    table: str
    spelling: str


def name_scenarios():
    entries = [("agent", name, path) for name, path in _AGENT_NAMES]
    entries += [("chain", name, "/usr/bin" if name == "powermetrics" else "/fixture/scripts")
                for name in _CHAIN_NAMES]
    entries += [("cpu", name, "/fixture/system") for name in _CPU_NAMES]
    # A short comm is already its own 16-byte form. Count each rendered row
    # once per class and table, including when app and CLI basenames coincide.
    seen = set()
    for group, name, directory in entries:
        mixed = "".join(ch.upper() if i % 2 else ch.lower() for i, ch in enumerate(name))
        for case, cased in (("native", name), ("lower", name.lower()),
                            ("upper", name.upper()), ("mixed", mixed)):
            for width, comm in (("full", cased), ("comm16", cased[:16])):
                forms = [("bare", comm), ("path", f"{directory}/{comm}"), ("paren", f"({comm})")]
                if directory.startswith("/Applications/"):
                    forms.append(("app-path-case", f"{directory.swapcase()}/{comm}"))
                for form, value in forms:
                    tables = ["accounting", "census_ps", "cpu_args"]
                    if group == "agent":
                        tables.append("pgrep")
                    for table in tables:
                        key = group, table, value
                        if key in seen:
                            continue
                        seen.add(key)
                        # Include the value so a failure is directly replayable.
                        label = f"name/{group}/{table}/{case}/{width}/{form}/{value}"
                        yield NameSighting(label, group, table, value)


class SingleReadFixture(Fixture):
    """The name is visible on precisely one read at 45 s. The PID then exits."""
    def __init__(self, case, root, spec):
        super().__init__(case, root)
        self.spec = spec
        self.previous_table = None
        self.show = False
        self.delivered = False

    def processes(self):
        rows = super().processes()
        if self.delivered:
            return rows
        worker = self.spec.group == "cpu"
        if self.show or (worker and self.now >= 5):
            # CPU contaminants have independent, same-PID/start TIME evidence:
            # zero at 15 s, 3 CPU-s by 30 s (>0.05 even across 45 s). The
            # earlier executable is neutral. A quiet resident alone is not a
            # positive case. Agents and chains require no CPU evidence.
            text = self.spec.spelling if self.show else "helper"
            cs = 300 if worker and self.now >= 30 else 0
            # A transient named executable was born during this census.
            # Only the CPU worker has the earlier neutral accounting history.
            rows.append((PID, 5 if worker else 45, cs, text, text))
        return rows

    def run(self, argv, **kwargs):
        from joulewise import prewindow
        from joulewise.hazards import contention
        if tuple(argv) == tuple(contention.PS_ARGV):
            table = "accounting"
        elif tuple(argv) == tuple(prewindow.PS_ARGV):
            table = "cpu_args" if self.previous_table == "accounting" else "census_ps"
        elif argv[0] == "/usr/bin/pgrep":
            table = "pgrep"
        else:
            table = "other"
        self.previous_table = table
        self.show = self.now == 45 and not self.delivered and self.spec.table == table
        try:
            reply = super().run(argv, **kwargs)
            if self.show:
                # For pgrep, the real requested regex/options still determine
                # whether the program receives the row. Record that separately.
                self.delivered = True
                self.visible = any(line.split()[:1] == [str(PID)] for line in reply.stdout.splitlines())
        finally:
            self.show = False
        return reply


@dataclass(frozen=True)
class Overlap:
    name: str
    opening_ms: int
    birth_offset_ms: int
    wall_phase_ms: int
    read_ms: int
    exit_mode: str
    level: str

    @property
    def midpoint_read(self):
        return self.opening_ms + self.read_ms + 15_000

    @property
    def close(self):
        # Only the initial dwell sleeps another 15 s after its midpoint argv
        # read. All daemon deadlines are fixed by the virtual timer.
        argv_cost = 200 if self.opening_ms == 0 and self.exit_mode == "short" else 0
        return self.opening_ms + self.read_ms + 30_000 + argv_cost

    @property
    def first_absence(self):
        return self.midpoint_read + 200 if self.exit_mode == "short" else self.close

    @property
    def birth(self):
        # Offsets are relative to the reported window opening (the sample
        # midpoint). The rate oracle separately uses the wider read bracket.
        return self.opening_ms + self.read_ms // 2 + self.birth_offset_ms

    @property
    def birth_floor(self):
        return (self.birth + self.wall_phase_ms) // 1000 * 1000 - self.wall_phase_ms

    @property
    def overlap_max(self):
        # Largest possible intersection of the window and the lifetime. Use
        # the beginning of the opening read, the *floor* of printed lstart,
        # and the first confirmed absence. Actual fractional birth and exit
        # times are available only to the synthetic process producer.
        return self.first_absence - max(self.opening_ms, self.birth_floor)

    @property
    def cpu_growth_cs(self):
        # 0.05 CPU-s/s == one centisecond per 200 ms. Strictly adjacent TIME
        # quanta even when the exact threshold is not representable.
        if self.level == "audit180":
            return 180
        if self.level == "above":
            return self.overlap_max // 200 + 1
        if self.level == "below":
            return (self.overlap_max - 1) // 200
        assert self.overlap_max % 200 == 0
        return self.overlap_max // 200

    @property
    def window(self):
        return (self.opening_ms + self.read_ms / 2, self.close)


def overlap_scenarios():
    # All seven sliding 30-second windows in a two-minute, 15 s cadence
    # timeline. Add openings whose table-read bracket crosses a wall second.
    for opening in range(0, 90_001, 15_000):
        for phase, read in ((0, 0), (700, 400)):
            offsets = {-1000, -750, -500, -250, -1, 0, 1, 100, 250, 400, 450, 750, 1000}
            if read:
                offsets.update((-read//2, read//2))
            for offset in sorted(offsets):
                for exit_mode in ("short", "long"):
                    for level in ("below", "above", "equal"):
                        name = f"overlap/open{opening}/birth{offset:+}/wall{phase}/read{read}/{exit_mode}/{level}"
                        spec = Overlap(name, opening, offset, phase, read, exit_mode, level)
                        if level != "equal" or spec.overlap_max % 200 == 0:
                            yield spec
    for birth in (250, 450):
        yield Overlap(f"overlap/audit4-read-crosses-wall-second/birth{birth}ms",
                      0, birth - 200, 700, 400, "long", "audit180")


class OverlapFixture(Fixture):
    def __init__(self, case, root, spec):
        super().__init__(case, root)
        self.spec = spec
        self.open_read = False
        self.mid_accounted = False
        self.mid_args_done = False
        self.trace = []

    @property
    def ms(self):
        return round(self.now * 1000)

    def wall_ns(self):
        return EPOCH * 10**9 + (self.ms + self.spec.wall_phase_ms) * 10**6

    def processes(self):
        s = self.spec
        rows = super().processes()
        exit_ms = 20_000 if s.level == "audit180" else s.first_absence - 100
        if s.birth <= self.ms < exit_ms:
            # A resident can have CPU before the opening. Put it in both
            # counters so a test that credits the whole last TIME is detectable.
            prior = min(20, max(0, (s.opening_ms - s.birth) // 20))
            cs = prior + (s.cpu_growth_cs if self.ms >= s.midpoint_read else 0)
            lstart_s = (s.birth_floor + s.wall_phase_ms) // 1000
            rows.append((PID, lstart_s, cs, WORKER, WORKER))
        return rows

    def run(self, argv, **kwargs):
        from joulewise import prewindow
        from joulewise.hazards import contention
        s = self.spec
        is_cpu = tuple(argv) == tuple(contention.PS_ARGV)
        is_args = tuple(argv) == tuple(prewindow.PS_ARGV)
        if is_args and self.mid_accounted and not self.mid_args_done and self.ms == s.midpoint_read:
            self.mid_args_done = True
            if s.exit_mode == "short":
                self.now = (self.ms + 200) / 1000
        begin = self.ms
        reply = super().run(argv, **kwargs)
        if is_cpu and begin == s.opening_ms and not self.open_read:
            self.open_read = True
            self.now = (begin + s.read_ms) / 1000
            self.next_tick += s.read_ms / 1000
        if is_cpu and begin == s.midpoint_read:
            self.mid_accounted = True
        if is_cpu or is_args:
            row = next((line for line in reply.stdout.splitlines() if line.split()[:1] == [str(PID)]), None)
            self.trace.append(("cpu" if is_cpu else "args", begin, self.ms, row))
        return reply

    def move(self, end):
        # v1's ticks are instantaneous. Here the daemon may consume a fraction
        # of its target tick before it parks. Never rewind the fixture clock.
        if end >= self.now:
            super().move(end)
        if self.trace:
            self.now = max(self.now, self.trace[-1][2] / 1000)


def observed_overlap(spec, trace):
    """Independent oracle using only returned rows and their read brackets."""
    cpu = [r for r in trace if r[0] == "cpu"]
    opening = next((r for r in cpu if r[1] == spec.opening_ms), None)
    closing = next((r for r in cpu if r[1] == spec.close), None)
    if opening is None or closing is None:
        return None
    within = trace[trace.index(opening):trace.index(closing)+1]
    positive = [r for r in within if r[0] == "cpu" and r[3]]
    if not positive:
        return None
    last = positive[-1]
    absent = next((r for r in within[within.index(last)+1:] if r[3] is None), None)
    if absent is None:
        return None

    def counter(row):
        minutes, seconds = row[3].split()[-2].split(":")
        whole, cents = seconds.split(".")
        return (int(minutes)*60 + int(whole))*100 + int(cents)

    # lstart contains seconds only. An identity absent in the opening table
    # can start within that read bracket, even if its printed second predates
    # the *end* of the read. A resident supplies its actual opening counter.
    stamp = " ".join(last[3].split()[2:7])
    birth_floor = (int(datetime.strptime(stamp, "%a %b %d %H:%M:%S %Y")
                       .replace(tzinfo=timezone.utc).timestamp()) - EPOCH)*1000 - spec.wall_phase_ms
    if not opening[3] and birth_floor + 1000 <= opening[1]:
        raise FixtureError("lstart is incompatible with absence in the opening table")
    cpu_cs = counter(last) - (counter(opening) if opening[3] else 0)
    duration = min(closing[2], absent[2]) - max(opening[1], birth_floor)
    return cpu_cs, duration


def v2_trial(spec, root, prov, oracle):
    captured = []
    if isinstance(spec, NameSighting):
        typ, end = SingleReadFixture, 45
    else:
        typ, end = OverlapFixture, spec.close / 1000

    def factory(case, directory):
        fixture = typ(case, directory, spec)
        captured.append(fixture)
        return fixture

    result = run_case(Case(spec.name, end=end), root, prov, oracle, fixture_factory=factory)
    fixture, = captured
    # The historical lane does not have all of the daemon's observations.
    # Preserve its real verdict for the differential, never invent a sample.
    summary = {k: result[k] for k in ("rc", "status", "published", "refused", "guard_count", "flags",
                                      "refused_at", "accepted", "work_started", "judged_windows",
                                      "report_intervals", "recorded")}
    if isinstance(spec, NameSighting):
        summary.update(delivered=fixture.delivered, visible=getattr(fixture, "visible", False))
    else:
        witness = observed_overlap(spec, fixture.trace)
        summary.update(witness=witness, reached=any(
            abs(a*1000-spec.window[0]) < .001 and abs(b*1000-spec.window[1]) < .001
            for a, b in result["judged_windows"]))
        if not oracle and (witness is None or not summary["reached"]):
            summary["trace"] = [(k, a, b, bool(row)) for k, a, b, row in fixture.trace]
    return summary


def v2_errors(spec, old, new):
    errors = []
    refused = new["rc"] == 2 and new["status"] != "pass" and not new["published"]
    if isinstance(spec, NameSighting):
        if not new["delivered"]:
            errors.append("target table was never queried")
        elif not new["visible"]:
            errors.append("requested query missed the synthetic name")
        if not (refused and (new["refused"] or new["guard_count"])):
            errors.append("single-table sighting did not refuse with exit 2")
    else:
        witness = new["witness"]
        if witness != [spec.cpu_growth_cs, spec.overlap_max] or not new["reached"]:
            errors.append(f"target window or fixture witness missing: {witness}, {new.get('trace')}")
        else:
            above = witness[0]*200 > witness[1]
            start, end = spec.window
            expected_start = datetime.fromtimestamp(
                EPOCH + (spec.birth_floor+spec.wall_phase_ms)//1000, timezone.utc
            ).strftime("%a %b %d %H:%M:%S %Y")
            def is_target(a, b):
                return abs(a*1000-start) < .001 and abs(b*1000-end) < .001
            flags = {(pid, identity) for a, b, pid, identity in new["flags"] if is_target(a, b)}
            if flags != ({(PID, expected_start)} if above else set()):
                errors.append(f"target flags={sorted(flags)}, expected worker flag={above}, "
                              f"{witness[0]} CPU centiseconds / {witness[1]} ms")
            if above and flags and not any(is_target(a, b) for a, b in new["report_intervals"]):
                errors.append("terminal report lost the target interval")
            if above and not refused:
                errors.append("above-threshold evidence allowed publication")
    if new["recorded"] != new["guard_count"]:
        errors.append("terminal report lost contention flags")
    if (old["refused"] or old["flags"]) and not refused:
        errors.append("lost L3 refusal or contention flag")
    return errors


def generated_worker(source, work, oracle, family):
    cases = name_scenarios if family == "names" else overlap_scenarios
    worker(source, work, oracle, cases=cases, execute=v2_trial)


class TestGeneratedR0Families(unittest.TestCase):
    def test_generated_families(self):
        candidate = Path(os.environ.get("R0_CANDIDATE", Path.cwd())).resolve()
        with tempfile.TemporaryDirectory(prefix="r0-generated-") as tmp:
            root = Path(tmp).resolve()
            admitted = root / "admitted"
            stage_oracle(candidate, admitted)
            for family, generate in (("names", name_scenarios), ("overlap", overlap_scenarios)):
                cases = list(generate())
                labels = {s.name for s in cases}
                self.assertEqual(len(cases), len(labels))
                old = lane(admitted, root / (family+"-l3"), "admitted", family)
                new = lane(candidate, root / (family+"-r0"), "candidate", family)
                self.assertEqual(set(old), labels)
                self.assertEqual(set(new), labels)
                failed = unresolved = 0
                for spec in cases:
                    r = new[spec.name]
                    errors = v2_errors(spec, old[spec.name], r)
                    if isinstance(spec, Overlap) and (not r["reached"] or
                            r["witness"] != [spec.cpu_growth_cs, spec.overlap_max]):
                        unresolved += 1
                    if errors:
                        failed += 1
                        with self.subTest(family=family, scenario=spec.name):
                            self.fail(" | ".join(errors))
                print(f"v2 family={family} scenarios={len(cases)} failed={failed} "
                      f"passed={len(cases)-failed} incomplete_window_witnesses={unresolved}", flush=True)




# BEGIN FROZEN V3 ADDITION. Removing this block restores the complete v2 file.
# Run this module exactly as v2. TestR0V3 adds two fixed CLI replays, a
# fast real-guard timing sweep, and CLI histories with scheduled admissions.
# A scenario is one distinct timeline, regardless of how many PIDs it has.

@dataclass(frozen=True)
class TimingCase:
    name: str
    # Milliseconds for accounting and its trailing arguments read, respectively.
    opening_lag: tuple
    closing_lag: tuple
    place: str = "first"
    jitter: int = 0
    missed: str = "none"
    history: str = "resident"
    only_gain: int | None = None
    # Offset in ms about the 30 s eligibility cliff for a second opening.
    alternate_offset: int | None = None
    skip_alternate: bool = False

    @property
    def opening(self):
        return {"first": 0, "interior": 64_000, "last": 96_000}[self.place]

    @property
    def closing(self):
        separation = 30_000 + sum(self.opening_lag) if self.place == "first" else 34_000
        return self.opening + separation + self.jitter

    @property
    def end(self):
        if self.place == "last":
            return self.closing
        return self.closing + sum(self.closing_lag) + 34_000

    @property
    def alternate(self):
        if self.alternate_offset is None or self.skip_alternate:
            return None
        return self.closing + sum(self.closing_lag)//2 - 30_000 + self.alternate_offset

    @property
    def l3_opening(self):
        if self.alternate is not None:
            # L3 stamps int(clock()*1e9). At exactly 30 s on the fixture's
            # decimal clock a representational ns can change eligibility.
            ns = lambda ms: int((ms/1000)*1e9)
            close_mid = (ns(self.closing) + ns(self.closing + sum(self.closing_lag)))//2
            if close_mid - ns(self.alternate) >= 30_000_000_000:
                return self.alternate
        return self.opening

    def boundary_gains(self):
        # Work in microseconds. One CPU centisecond ties 0.05 at 200 ms.
        # At an unrepresentable tie, use the closest legal TIME on each side.
        def points(start, lag):
            cpu, args = lag
            return {start*1000 + offset for offset in
                    (0, cpu*500, cpu*1000, (cpu+args)*500, (cpu+args)*1000)}
        gains = set()
        openings = points(self.opening, self.opening_lag)
        if self.alternate is not None:
            openings.add(self.alternate*1000)
        for a in openings:
            for b in points(self.closing, self.closing_lag):
                quotient, remainder = divmod(b-a, 200_000)
                gains.update((quotient if remainder else quotient-1, quotient+1))
                if not remainder:
                    gains.add(quotient)
        return sorted(gains)

    def pulses(self):
        # Ordinary 15 s timer with bounded alternating wake-up jitter. A
        # skipped interior tick leaves the two admissions and their rows intact.
        first = (self.closing + sum(self.closing_lag) if self.place == "first" else 30_000) + 15_000
        nominal = range(first, self.end+1, 15_000)
        times = [t + (1 if i % 2 == 0 else -1)*self.jitter for i, t in enumerate(nominal)]
        times = [t for t in times if t <= self.end]
        inside = [t for t in times if self.opening < t < self.closing]
        omitted = set()
        if inside and self.missed != "none":
            omitted.add(inside[0] if self.missed == "early" else inside[-1])
        return tuple(t for t in times if t not in omitted)


def split_read(total, mode):
    cpu = (total, 0, total//2)[mode]
    return cpu, total-cpu


def timing_scenarios():
    # Every integral millisecond from 0 to 2,000 occurs at BOTH endpoints.
    # The permutation gives independently varying pairs. A Cartesian edge
    # grid adds symmetric, one-sided, and exactly representable boundaries.
    pairs = set()
    for opening in range(2001):
        closing = (997*opening + 400) % 2001
        pairs.add(((opening, 0), (closing, 0)))
        pairs.add((split_read(opening, opening % 3), split_read(closing, (opening//3) % 3)))
    for opening in (0, 1, 199, 200, 400, 1000, 1999, 2000):
        for closing in (0, 1, 199, 200, 400, 1000, 1999, 2000):
            for left in range(3):
                for right in range(3):
                    pairs.add((split_read(opening, left), split_read(closing, right)))
    for a, b in sorted(pairs):
        yield TimingCase(f"time_o{a[0]}a{a[1]}_c{b[0]}a{b[1]}", a, b)


def endpoint_scenarios():
    profiles = (((0, 0), (0, 0)), ((400, 0), (0, 0)), ((0, 0), (2000, 0)),
                ((2000, 0), (400, 0)), ((0, 800), (0, 2000)), ((200, 200), (800, 400)))
    for place in ("first", "interior", "last"):
        for i, (opening, closing) in enumerate(profiles):
            for jitter in ((0, 400) if place == "first" else (-400, 0, 600)):
                for missed in (("none",) if place == "first" else ("none", "early", "late")):
                    label = f"{place}_p{i}_j{jitter}_{missed}"
                    yield TimingCase("admission_"+label, opening, closing, place, jitter, missed)
    # Solo workers ensure a companion that is far above threshold cannot
    # hide a wrongful CLI pass. The multi-PID matrix checks individual flags.
    for place in ("first", "interior", "last"):
        for history in ("born_inside", "closing_only", "opening_only", "interior_only",
                        "name_at_open", "name_at_close", "pid_reuse"):
            for i, (opening, closing) in enumerate(profiles):
                spec = TimingCase(f"endpoint_{place}_{history}_p{i}", opening, closing, place,
                                  0 if place == "first" else 400, "none", history)
                yield spec
    for place in ("interior", "last"):
        for history in ("prior_flag_exit", "prior_flag_reset"):
            for missed in ("none", "early", "late"):
                yield TimingCase(f"carry_{place}_{history}_{missed}", (400, 0), (0, 0),
                                 place, 0, missed, history)
    for place in ("interior", "last"):
        for i, (opening, closing) in enumerate(profiles):
            for offset in (-1, 0, 1, None):
                # The skipped case omits the near-eligible foreground sample
                # altogether. A daemon tick still occurs inside the interval.
                yield TimingCase(f"choice_{place}_p{i}_{offset}", opening, closing,
                                 place, history="eligible_opening", alternate_offset=offset or 0,
                                 skip_alternate=offset is None)
    for place in ("first", "last"):
        for i, (opening, closing) in enumerate(profiles):
            for history in ("exit_at_close", "exit_after_close", "born_at_open", "born_after_open"):
                yield TimingCase(f"edge_{place}_{history}_p{i}", opening, closing, place,
                                 history=history)
    for place in ("first", "last"):
        for value in (150, 151, 152, 153, 170, 171, 172):
            yield TimingCase(f"solo_{place}_{value}", (400, 0), (0, 0), place,
                             only_gain=value)


class TimingFixture(Fixture):
    def __init__(self, case, root, spec):
        super().__init__(case, root)
        self.spec = spec
        self.gains = [spec.only_gain] if spec.only_gain is not None else spec.boundary_gains()
        self.trace = []
        self.pending = None
        self.lags = {spec.opening: spec.opening_lag, spec.closing: spec.closing_lag}
        self.pulses = list(spec.pulses())
        self.delivered = []

    @property
    def ms(self):
        return round(self.now*1000)

    def sleep(self, seconds):
        end = self.ms + round(seconds*1000)
        if self.spec.place == "first" and end == self.spec.closing - self.spec.jitter:
            end += self.spec.jitter
        self.now = end / 1000

    def wall_ns(self):
        return EPOCH*10**9 + self.ms*10**6

    def processes(self):
        s, now = self.spec, self.ms
        rows = super().processes()
        history = s.history
        # All rows are functions of absolute time, independent of lane, table
        # number or presence of a background timer. lstart has second precision.
        born, gone = -100_000, s.end+60_000
        lo, hi = s.opening+2500, s.closing-1000
        if s.alternate is not None:
            lo = max(lo, s.alternate+200)
        if history in ("exit_at_close", "exit_after_close"):
            # At close is absent from accounting. One ms later can survive
            # only in accounting if the ps read takes at least one ms.
            gone = s.closing + int(history == "exit_after_close")
        if history in ("born_at_open", "born_after_open"):
            born = s.opening + int(history == "born_after_open")
        if history in ("born_inside", "interior_only"):
            born = s.opening+2500
        if history == "closing_only":
            born = lo = s.closing-6000
        if history in ("opening_only", "interior_only"):
            gone, hi = s.closing-6000, s.opening+8000
        if history.startswith("prior_flag_"):
            lo, hi = s.opening-14_000, s.opening-1000
            if history == "prior_flag_exit":
                gone = s.closing-5000
        if history == "pid_reuse":
            if now < s.opening+5000:
                gone = s.opening+5000
            else:
                born = lo = s.opening+8000
        if not born <= now < gone:
            return rows
        name = WORKER
        if ((history == "name_at_open" and now > s.opening + sum(s.opening_lag))
                or (history == "name_at_close" and now < s.closing)):
            name = "fixture-idle"
        for index, gain in enumerate(self.gains):
            if history.startswith("prior_flag_"):
                gain += 300  # the preceding observation is decisively over
            cs = gain*min(max(now-lo, 0), hi-lo)//(hi-lo)
            if history == "prior_flag_reset" and now >= s.closing-5000:
                cs = 0
            rows.append((PID+index, born//1000, cs, name, name))
        return rows

    def run(self, argv, **kwargs):
        from joulewise import prewindow
        from joulewise.hazards import contention
        start = self.ms
        reply = super().run(argv, **kwargs)
        if tuple(argv) == tuple(contention.PS_ARGV):
            if self.pending is not None:
                raise FixtureError("two accounting reads without their paired args read")
            cpu, args = self.lags.pop(start, (0, 0))
            self.now = (start+cpu)/1000
            self.pending = (start, start+cpu, args, reply.stdout)
        elif tuple(argv) == tuple(prewindow.PS_ARGV) and self.pending is not None:
            at, cpu_end, args, cpu_rows = self.pending
            self.pending = None
            self.now = (start+args)/1000
            self.trace.append((at, cpu_end, self.ms, cpu_rows, reply.stdout))
        return reply

    def move(self, end):
        ms = round(end*1000)
        if ms < self.ms:
            raise FixtureError(f"clock reversal {self.ms} -> {ms}")
        while self.pulses and self.pulses[0] <= ms:
            pulse = self.pulses.pop(0)
            if pulse < self.ms:
                raise FixtureError("timer overlaps a scripted admission read")
            self.now = pulse/1000
            if self.timer:
                self.timer.pulse()
                self.delivered.append(pulse)
        self.now = ms/1000

    def host(self):
        s = self.spec
        self.work_started.append("host")
        self.phase = "host_return"
        if s.place != "first":
            self.move(s.opening/1000)
            self.guard.check(force=True)
            if s.alternate is not None:
                self.move(s.alternate/1000)
                self.guard.check(force=True)
            if s.place == "interior":
                self.move(s.closing/1000)
                self.guard.check(force=True)
        self.move(s.end/1000)
        return {"status": "pass"}


def guard_flags(guard):
    return [(f["interval"]["start_monotonic_s"], f["interval"]["end_monotonic_s"],
             b["pid"], b["start"]) for f in guard.contention_flags for b in f["busy"]]


def timing_result(spec, f, oracle, raw_flags):
    # Match the SAME two physical reads. L3 times accounting + args; a
    # candidate can timestamp accounting alone. No overlapping-window match.
    # The parser converts a float second to ns with int on L3 and round on R0.
    # Rounding to us recovers the exact integer/half-ms fixture instant.
    stamps, witnesses = {}, {}
    for start, cpu_end, args_end, cpu, args in f.trace:
        for end in {cpu_end, args_end}:
            stamp = (start+end)*500
            if stamp in stamps and stamps[stamp] != start:
                raise FixtureError("two distinct samples have the same midpoint")
            stamps[stamp] = start
        if start in (spec.opening, spec.alternate, spec.closing) and start not in witnesses:
            witnesses[start] = [cpu_end, args_end, hashlib.sha256(
                (cpu+"\0"+args).encode()).hexdigest()]
    def read(seconds):
        stamp = round(seconds*10**6)
        if stamp not in stamps:
            raise FixtureError(f"reported endpoint {seconds} is not a sampled midpoint")
        return stamps[stamp]
    flags = {(read(a), read(b), pid, birth) for a, b, pid, birth in raw_flags}
    # A baseline with no flags still needs an actual L3 judgement. Read its
    # receipt so a missed window cannot pass as a quiet boundary control.
    judged = set()
    if oracle:
        for receipt in f.guard.receipts:
            interval = receipt.get("cpu_interval", {})
            if "start_monotonic_s" in interval:
                judged.add((read(interval["start_monotonic_s"]), read(interval["end_monotonic_s"])))
    return dict(flags=sorted(flags), witnesses=witnesses,
                target_judged=(spec.l3_opening, spec.closing) in judged,
                delivered=f.delivered, gains=f.gains)


def matrix_trial(spec, root, prov, oracle):
    # The dense sweep stops at the first admission through the normal public
    # guard. CLI tests below independently exercise publication and teardown.
    from joulewise import agent_identity, measurement_liveness as live
    f = TimingFixture(Case(spec.name), root, spec)
    real_filter = agent_identity.filter_census
    with (patch.dict(os.environ, {"HOME": str(root/"home"), live.CUSTODY_PARENT_ENV: str(f.parent),
                                  live.ADDITIONAL_PARENTS_ENV: "[]"}),
          patch.object(time, "time_ns", f.wall_ns), patch.object(os, "getpid", return_value=8001),
          patch.object(agent_identity, "filter_census",
                       lambda stdout, **kw: real_filter(stdout, inspector=f.identity, **kw))):
        guard = f.factory([f.parent])
        try:
            guard.check(force=True)
            return timing_result(spec, f, oracle, guard_flags(guard))
        finally:
            if f.timer:
                f.timer.set()
                guard.close()


def endpoint_trial(spec, root, prov, oracle):
    captured = []
    def factory(case, directory):
        f = TimingFixture(case, directory, spec)
        captured.append(f)
        return f
    row = run_case(Case(spec.name), root, prov, oracle, fixture_factory=factory)
    f, = captured
    result = timing_result(spec, f, oracle, row["flags"])
    result.update({k: row[k] for k in ("rc", "status", "published", "guard_count", "recorded", "exception")})
    return result


def fixed_scenarios():
    for name, worker_name, cpu_at, growth in (
        ("fixed_audit_1_corespotlightd", "corespotlightd", 30, 180),
        ("fixed_audit_2_resident_400ms", WORKER, 10, 152),
    ):
        yield Case(name, (Process(worker_name, cpu_at=cpu_at, centiseconds=growth),), end=60)


def fixed_trial(case, root, prov, oracle):
    # Verbatim timing of audit 2's OpeningRead. Audit 1 uses v2's Fixture.
    class OpeningRead(Fixture):
        def run(self, argv, **kwargs):
            from joulewise.hazards.contention import PS_ARGV
            reply = super().run(argv, **kwargs)
            if tuple(argv) == tuple(PS_ARGV) and self.now == 0:
                self.now = .4
                self.next_tick += .4
            return reply
    fixture = OpeningRead if case.name.startswith("fixed_audit_2") else Fixture
    return run_case(case, root, prov, oracle, fixture_factory=fixture)


def fixed_errors(case, old, new):
    audit2 = case.name.startswith("fixed_audit_2")
    window = (0.2, 30.4) if audit2 else (0., 30.)
    expected = (*window, PID, TOKEN)
    admitted = set(map(tuple, old["flags"]))
    candidate = set(map(tuple, new["flags"]))
    errors = []
    if expected not in admitted or old["refused"]:
        errors.append("invalid L3 audit witness")
    if not admitted <= candidate:
        errors.append(f"missing={sorted(admitted-candidate)}")
    if new["rc"] != 2 or new["status"] == "pass" or new["published"]:
        errors.append(f"rc={new['rc']} status={new['status']} published={new['published']}")
    if new["recorded"] != new["guard_count"]:
        errors.append("terminal report flag count differs from guard")
    return errors


def timing_errors(spec, old, new, cli):
    errors = []
    start, end = spec.opening, spec.closing
    reads = [(start, spec.opening_lag), (end, spec.closing_lag)]
    if spec.alternate is not None:
        reads.append((spec.alternate, (0, 0)))
    for at, lag in reads:
        expected = [at+lag[0], at+sum(lag)]
        a, b = (r["witnesses"].get(str(at)) for r in (old, new))
        if a is None or b is None or a[:2] != expected or a != b:
            errors.append(f"invalid endpoint witness at {at}: {a} / {b}, expected {expected}")
    if not old["target_judged"]:
        errors.append("L3 did not judge the target endpoint pair")
    if cli and tuple(new["delivered"]) != spec.pulses():
        errors.append("scheduled daemon samples differ from the fixture")
    before, after = (set(map(tuple, r["flags"])) for r in (old, new))
    target = {(p, birth) for a,b,p,birth in before if (a,b) == (spec.l3_opening,end)}
    # Controls prove the generated positives are real L3 flags. A lone case
    # tuned below threshold can legitimately lack any target flag.
    positive = spec.history not in ("opening_only", "interior_only", "exit_at_close") and spec.only_gain is None
    if positive and not target:
        errors.append("missing positive L3 endpoint control")
    if spec.history in ("opening_only", "interior_only", "exit_at_close") and target:
        errors.append("unexpected positive L3 endpoint control")
    if spec.history in ("resident", "eligible_opening"):
        # Independently check delivered counters against the observed L3
        # midpoint spacing. Exact ties use the pinned implementation's own
        # flag set in the differential (including its float arithmetic).
        left = spec.l3_opening*1000
        if spec.l3_opening == start:
            left += sum(spec.opening_lag)*500
        elapsed = end*1000 + sum(spec.closing_lag)*500 - left
        for i, gain in enumerate(old["gains"]):
            key = (PID+i, TOKEN)
            if gain*200_000 != elapsed and ((gain*200_000 > elapsed) != (key in target)):
                errors.append(f"invalid L3 boundary control for {key}, {gain} cs/{elapsed} us")
                break
    if not before <= after:
        missing = sorted(before-after)
        errors.append(f"missing {len(missing)} L3 flags, first={missing[0]}")
    if cli:
        if new["exception"] or new["rc"] not in (0, 2) or new["recorded"] != new["guard_count"]:
            errors.append("invalid terminal outcome or lost report count")
        if before or after:
            if new["rc"] != 2 or new["status"] == "pass" or new["published"]:
                errors.append(f"rc={new['rc']} status={new['status']} published={new['published']}")
    return errors


V3_FAMILIES = {"v3-fixed": (fixed_scenarios, fixed_trial),
               "v3-timing": (timing_scenarios, matrix_trial),
               "v3-endpoints": (endpoint_scenarios, endpoint_trial)}


class TestR0V3(unittest.TestCase):
    def compare(self, family):
        candidate = Path(os.environ.get("R0_CANDIDATE", Path.cwd())).resolve()
        generate, _ = V3_FAMILIES[family]
        specs = list(generate())
        labels = {s.name for s in specs}
        self.assertEqual(len(labels), len(specs))
        if family == "v3-timing":
            for key in ("opening_lag", "closing_lag"):
                self.assertEqual({sum(getattr(s, key)) for s in specs}, set(range(2001)))
                self.assertEqual({getattr(s, key)[0] for s in specs}, set(range(2001)))
        with tempfile.TemporaryDirectory(prefix=family+"-") as tmp:
            work = Path(tmp).resolve()
            admitted = work/"admitted"
            stage_oracle(candidate, admitted)
            old = lane(admitted, work/"l3", "admitted", family)
            new = lane(candidate, work/"r0", "candidate", family)
        self.assertEqual(set(old), labels)
        self.assertEqual(set(new), labels)
        failed = invalid = lost = published = 0
        for spec in specs:
            a, b = old[spec.name], new[spec.name]
            if family == "v3-fixed":
                errors = fixed_errors(spec, a, b)
                print(f"{spec.name} L3={a['flags'][:1]} R0={b['flags']} "
                      f"exit={b['rc']} status={b['status']} published={b['published']}", flush=True)
            else:
                errors = timing_errors(spec, a, b, family == "v3-endpoints")
            if errors:
                failed += 1
                invalid += int(any("control" in e or "witness" in e or "did not judge" in e
                                   or "scheduled daemon" in e for e in errors))
                lost += int(any(e.startswith("missing") and "control" not in e for e in errors))
                published += int(bool(a["flags"] and b.get("published")))
                print(f"FAIL {family} {spec.name} | {' | '.join(errors)}")
        publication_count = "n/a" if family == "v3-timing" else str(published)
        print(f"{family} scenarios={len(specs)} failed={failed} passed={len(specs)-failed} "
              f"invalid_controls={invalid} lost_flag_cases={lost} "
              f"published_despite_L3_flag={publication_count}", flush=True)
        self.assertEqual(failed, 0, family)

    def test_v3_fixed(self):
        self.compare("v3-fixed")

    def test_v3_timing(self):
        self.compare("v3-timing")

    def test_v3_endpoints(self):
        self.compare("v3-endpoints")


if (__name__ == "__main__" and sys.argv[1:2] == ["--synthetic-worker"] and
        len(sys.argv) == 6 and sys.argv[5] in V3_FAMILIES):
    generate, execute = V3_FAMILIES[sys.argv[5]]
    worker(Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve(),
           sys.argv[4] == "admitted", cases=generate, execute=execute)
    sys.exit(0)
# END FROZEN V3 ADDITION.

if __name__ == "__main__":
    if sys.argv[1:2] == ["--synthetic-worker"] and len(sys.argv) == 6:
        generated_worker(Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve(),
                         sys.argv[4] == "admitted", sys.argv[5])
    elif sys.argv[1:2] == ["--synthetic-worker"]:
        worker(Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve(), sys.argv[4] == "admitted")
    else:
        unittest.main()
