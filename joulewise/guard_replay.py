"""Offline, outcome-free guard replay. No live sampler is constructed here.

Adapters consume a Tape and return one decision for one independently labelled
run. Historical adapters execute the original Git class/function ASTs, with
samplers injected; they do not maintain copies of the guard predicates.
"""
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from functools import lru_cache
import hashlib
import importlib
import importlib.util
import json
import math
from pathlib import Path, PurePosixPath
import re
import subprocess
from types import SimpleNamespace
from typing import Any

from joulewise import prewindow
from joulewise.hazards import contention
from joulewise.hazards.base import Stamp

SCHEMA = "joulewise.guard_replay.corpus.v1"
REPO = Path(__file__).absolute().parent.parent
HOST_PATH = "joulewise/align/r0_host.py"
SMC_PATH = "joulewise/align/apple/smc_enumeration.py"
# Resolve these to full object ids in every report. No fetch, checkout or model imports.
PINS = {"pre691": "165e1287290794bf4e3854997d2291651c784134",
        "prel3": "5f817856b33f65b269a44ea52811dbbed28d02a8",
        "l3": "9c40e4e5d9fa453cce3c70984e11fa382b7d4591"}
DEPENDENCY_PATHS = ("joulewise/hazards/contention.py", "joulewise/prewindow.py")
JOURNAL_FIXTURES = ("tests/fixtures/b5_harvest/l1_monitor/contention.jsonl",
                    "tests/fixtures/b5_harvest/l1_monitor/thermal.jsonl")
STATUSES = {"PASS", "REFUSE", "UNMEASURED", "UNSUPPORTED"}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "--no-optional-locks", *args], cwd=REPO,
                                   env={"PATH": "/usr/bin:/bin", "TMPDIR": "/private/tmp",
                                        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
                                        "GIT_NO_LAZY_FETCH": "1"})


def blob(revision: str, path: str) -> tuple[bytes, dict]:
    """Only explicit repository code or allowlisted host receipts, never data locators."""
    if path not in (HOST_PATH, SMC_PATH, *JOURNAL_FIXTURES, *DEPENDENCY_PATHS) and not re.fullmatch(
            r"docs/align/r0/2026-11-0[678](?:-rerun\d*)?/report.json", path):
        raise ValueError("not an allowlisted code/host-receipt blob")
    commit = git("rev-parse", "--verify", revision + "^{commit}").decode().strip()
    raw = git("show", f"{commit}:{path}")
    return raw, {"commit": commit, "path": path,
                 "blob": git("rev-parse", f"{commit}:{path}").decode().strip(),
                 "sha256": hashlib.sha256(raw).hexdigest()}


@lru_cache(maxsize=16)
def _code_blob(revision, path):
    # Immutable historical pins only; guard instances/globals are never cached.
    return blob(revision, path)


@lru_cache(maxsize=3)
def historical_dependencies(era):
    sources = []
    for path in DEPENDENCY_PATHS:
        old, source = _code_blob(PINS[era], path)
        current = (REPO / path).read_bytes()
        # The clone's contention source differs from the kit only in comments.
        # Refuse future executable dependency drift rather than silently mixing versions.
        if ast.dump(ast.parse(old)) != ast.dump(ast.parse(current)):
            raise ValueError(f"historical replay dependency differs: {path}; add a pinned dependency adapter")
        sources.append({**source, "historical_dependency_ast_matches_current": True})
    return sources


class MissingSample(ValueError):
    pass


@dataclass(frozen=True)
class Decision:
    status: str
    reason: str = ""
    evaluated: int = 0
    coverage_complete: bool = False

    def __post_init__(self):
        if self.status not in STATUSES:
            raise ValueError(f"invalid decision: {self.status}")
        if (not isinstance(self.reason, str) or type(self.evaluated) is not int or self.evaluated < 0
                or type(self.coverage_complete) is not bool):
            raise ValueError("decision needs a reason string, nonnegative count and explicit coverage boolean")


class Tape:
    """An injected sampler and virtual clock. Missing channels never become clean.

    A plugin may call sample(channel), clock(), sleep(seconds), or iterate
    frames(channel). Each adapter invocation gets a fresh Tape and fresh guard.
    sleep advances virtual time only; it cannot read the host or wait in real time.
    """
    def __init__(self, run: dict):
        self.run = run
        self.now = run["frames"][0]["t"] if run["frames"] else 0.0
        self.position: dict[str, int] = {}

    def frames(self, channel: str):
        frames = [f for f in self.run["frames"] if channel in f]
        if not frames:
            raise MissingSample(f"missing channel: {channel}")
        return frames

    def sample(self, channel: str):
        frames = self.frames(channel)
        i = self.position.get(channel, 0)
        # A guard's virtual sleep may pass collector samples it never requested.
        # Use the next actual observation; never fabricate a sample at the deadline.
        while i < len(frames) and frames[i]["t"] < self.now:
            i += 1
        if i >= len(frames):
            raise MissingSample(f"exhausted channel: {channel}")
        frame = frames[i]
        self.position[channel] = i + 1
        self.now = frame["t"]
        return frame[channel]

    def clock(self):
        return self.now

    def sleep(self, seconds):
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError("invalid virtual sleep")
        self.now += seconds


def _coverage(tape: Tape, channel: str, cadence_s: float):
    """Completeness must be supported by the adapter's channel, not just a label."""
    frames = tape.frames(channel)
    if not tape.run["complete"] or len(frames) < 2:
        return False
    span = frames[-1]["t"] - frames[0]["t"]
    return (abs(span - tape.run["duration_s"]) <= 1e-6
            and all(0 <= b["t"] - a["t"] <= cadence_s * 1.1
                    for a, b in zip(frames, frames[1:])))


def validate(corpus: dict):
    if corpus.get("schema") != SCHEMA or not isinstance(corpus.get("runs"), list):
        raise ValueError("invalid replay corpus schema")
    seen = set()
    for run in corpus["runs"]:
        if not isinstance(run.get("id"), str) or not run["id"] or run["id"] in seen:
            raise ValueError("run ids must be nonempty and unique")
        seen.add(run["id"])
        if run.get("label") not in ("benign", "contended", "unknown"):
            raise ValueError("label must be benign, contended or unknown")
        if not run.get("label_basis") or not run.get("stratum"):
            raise ValueError("independent label basis and stratum required")
        if type(run.get("complete")) is not bool:
            raise ValueError("explicit complete flag required")
        duration = run.get("duration_s")
        if type(duration) not in (int, float) or not math.isfinite(duration) or duration < 0:
            raise ValueError("invalid run duration")
        last = -math.inf
        if not isinstance(run.get("frames"), list):
            raise ValueError("frames must be a list")
        for frame in run["frames"]:
            t = frame.get("t")
            if type(t) not in (int, float) or not math.isfinite(t) or t < last:
                raise ValueError("frame times must be finite and nondecreasing")
            last = t
        if run["frames"] and last - run["frames"][0]["t"] > duration + 1e-6:
            raise ValueError("frame span exceeds run duration")


class _NeutralPath(PurePosixPath):
    """CPU-only replays neutralise ALL custody/filesystem observations, without I/O."""
    @classmethod
    def home(cls):
        return cls("/replay")

    def resolve(self):
        return self

    def expanduser(self):
        return self

    def is_dir(self):
        return True

    def glob(self, pattern):
        return ()


@dataclass
class _Owners:
    clear: bool = True
    warnings: tuple = ()
    refusals: tuple = ()


@dataclass
class _Agent:
    exit_code: int = 1


def _unexpected(*args, **kwargs):
    raise AssertionError("replay attempted an uninjected live operation")


def historical(era: str, path: str, names: tuple[str, ...]):
    """Import only the requested definitions, not module import-time/model code.

    Original ASTs (including method bodies and internal imports) execute unchanged.
    Dependencies and defaults are explicitly injected. Unexpected I/O fails loudly.
    """
    historical_dependencies(era)
    raw, source = _code_blob(PINS[era], path)
    tree = ast.parse(raw, filename=path)
    nodes = [node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef))
             and node.name in names]
    if {node.name for node in nodes} != set(names):
        raise ValueError("historical guard definition missing")
    from joulewise.night_gate import ProbeResult
    ns = {"__name__": "guard_replay_historical", "Any": Any,
          "Path": _NeutralPath, "os": SimpleNamespace(environ={}, getpid=lambda: 2_000_000_000,
                                                       getuid=lambda: 0),
          "subprocess": SimpleNamespace(run=_unexpected), "json": json, "math": math, "re": re,
          "time": SimpleNamespace(monotonic=lambda: 0., monotonic_ns=lambda: 0,
                                  time_ns=lambda: 0, sleep=_unexpected),
          "census": lambda **kw: _Owners(), "custody_parent": lambda: _NeutralPath("/replay"),
          "ADDITIONAL_PARENTS_ENV": "REPLAY_EXTRA_PARENTS", "asdict": asdict,
          "ProbeResult": ProbeResult, "SimpleNamespace": SimpleNamespace,
          "agent_census": lambda *a, **kw: (_Agent(), None),
          "PS_ARGV": prewindow.PS_ARGV, "busy_contaminants": prewindow.busy_contaminants,
          "prewindow": prewindow, "contention": contention,
          "Context": _unexpected, "_cpu_quiet": None,
          "SUSTAINED_CORES": .5, "SUSTAINED_S": 60, "CONTENTION_REDO_EXIT": 4}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ("SUSTAINED_CORES", "SUSTAINED_S", "CONTENTION_REDO_EXIT"):
                ns[node.targets[0].id] = ast.literal_eval(node.value)
    # Preserve postponed annotations without importing any historical module dependencies.
    tree = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0),
                            *nodes], type_ignores=[])
    exec(compile(ast.fix_missing_locations(tree), f"{source['commit']}:{path}", "exec"), ns)
    return ns, source


def _quiet(tape: Tape, era: str):
    ns, _ = historical(era, HOST_PATH, ("Refused", "QuietGuard"))
    channel = "pcpu_busy" if era == "pre691" else "quiet_busy"
    frames = tape.frames(channel)
    current = frames[0]

    def run(argv, **kwargs):
        if argv[0] == "/bin/launchctl":
            return SimpleNamespace(returncode=113, stdout="", stderr="could not find service")
        if tuple(argv) != prewindow.PS_ARGV:
            raise AssertionError(f"unexpected sampler argv: {argv}")
        # A busy-only receipt is a sufficient statistic ONLY for this CPU predicate.
        rows = current.get("pcpu_busy", [])
        text = "1 0 launchd\n" + "\n".join(f"{pid} {cpu} {cmd}" for pid, cpu, cmd in rows)
        return SimpleNamespace(returncode=0, stdout=text, stderr="")

    guard = ns["QuietGuard"]([], run=run, inspect_custody=lambda **kw: _Owners(), clock=tape.clock)
    if era != "pre691":
        # Receipt decision replay: _cpu_interval already recorded the sampled interval.
        def interval(receipt):
            receipt["cpu_interval"] = current.get("quiet_interval", {})
            return current["quiet_busy"]
        guard._cpu_interval = interval
    n = 0
    for current in frames:
        tape.now = current["t"]
        n += 1
        try:
            guard.check(force=True)
        except ns["Refused"] as exc:
            if not ((era == "pre691" and guard.receipts[-1].get("busy"))
                    or str(exc).startswith("contaminating CPU contention:")):
                raise ValueError("unexpected non-CPU refusal in CPU-only adapter") from exc
            return Decision("REFUSE", "historical QuietGuard CPU refusal (other censuses neutral)", n,
                            _coverage(tape, channel, 15))
    return Decision("PASS", "CPU predicate only; other censuses neutral", n, _coverage(tape, channel, 15))


def _snapshot(frame):
    """Normalized raw counters, not ps %CPU. Explicit identity is required."""
    sample = frame["snapshot"]
    rows = {}
    for p in sample["processes"]:
        identity = (p["pid"], p["start"])
        if identity in rows:
            raise ValueError("duplicate process identity")
        rows[identity] = {"pid": p["pid"], "ppid": p["ppid"], "start_identity": p["start"],
                          "start_epoch_s": p["start_epoch_s"], "command": p["command"],
                          "cumulative_cpu_seconds": p["cpu_s"]}
    stamp = Stamp(int(sample["wall_s"] * 1e9), int(frame["t"] * 1e9), int(frame["t"] * 1e9))
    return contention.Snapshot(stamp, stamp, rows, None, error=sample.get("error"),
                               host=sample.get("host_ticks"), host_error=sample.get("host_error"))


def _smc(tape: Tape, era: str):
    names = ("NotQuiet", "CpuQuietProbe", "require_quiet")
    if era == "l3":
        names += ("ContentionRedo", "Ruling8Quiet")
    ns, _ = historical(era, SMC_PATH, names)
    if any("snapshot" in f for f in tape.run["frames"]):
        snapshots = tape.frames("snapshot")
        complete = _coverage(tape, "snapshot", 5)
        def take():
            frame = {"t": tape.now, "snapshot": tape.sample("snapshot")}
            # sample advances the clock to the recorded sample's actual time.
            frame["t"] = tape.now
            return _snapshot(frame)
        ctx = SimpleNamespace(clocks=SimpleNamespace(monotonic_ns=lambda: int(tape.now * 1e9),
                                                      sleep=tape.sleep))
        probe = ns["CpuQuietProbe"](ctx=ctx, snapshot=take)
        count = len(snapshots) - 1  # startup consumes >=2; exhaustion is unmeasured
    else:
        frames = tape.frames("smc_cpu")
        complete = _coverage(tape, "smc_cpu", 5)
        if era == "pre691" and any(f.get("cpu_era") != "pre691" for f in frames):
            return Decision("UNSUPPORTED", "old 1 s/aggregate probe requires matching receipt or raw counters")
        if era != "pre691" and any(f["smc_cpu"].get("elapsed_s", 0) < 30 for f in frames):
            return Decision("UNSUPPORTED", "30 s baseline absent in old receipt")
        probe = lambda: tape.sample("smc_cpu")
        count = len(frames)

    last_cpu = None
    def read_cpu():
        nonlocal last_cpu
        last_cpu = probe()
        return last_cpu

    def census():
        kw = {"record_contention": True} if era == "l3" else {}
        return ns["require_quiet"](
            agent_probe=lambda: (_Agent(), None), measurement_probe=lambda: _Owners(),
            process_probe=lambda: SimpleNamespace(returncode=0, stderr="", stdout="1 launchd launchd\n"),
            contention_probe=read_cpu, custody_parents=["/replay"], **kw)

    check = ns["Ruling8Quiet"]("redo", census=census) if era == "l3" else census
    n = 0
    for _ in range(count):
        # CpuQuietProbe's startup can consume >2 snapshots; do not call it after EOF.
        if "snapshot" in tape.position and tape.position["snapshot"] >= len(snapshots):
            break
        try:
            check()
            n += 1
        except MissingSample:
            return Decision("UNMEASURED", "incomplete CPU baseline", n)
        except ns["NotQuiet"] as exc:
            # require_quiet wraps missing-sample exceptions; never score them as contention.
            if isinstance(exc.__cause__, MissingSample):
                return Decision("UNMEASURED", "incomplete CPU baseline", n)
            if exc.__cause__ is not None and not isinstance(exc.__cause__, MissingSample):
                raise exc.__cause__
            missing = last_cpu is None or last_cpu.get("error") or last_cpu.get("clean") is None
            return Decision("UNMEASURED" if missing else "REFUSE", "historical SMC admission refusal", n + 1,
                            complete and not missing)
        except ((ns["ContentionRedo"],) if "ContentionRedo" in ns else ()):
            return Decision("REFUSE", "R0-L3 sustained episode requested redo", n + 1, complete)
    return Decision("PASS" if n else "UNMEASURED", "SMC CPU predicate; other censuses neutral", n, complete and n > 0)


def contention_arm(tape: Tape):
    frames = tape.frames("snapshot")
    thresholds = {**contention.DEFAULT_THRESHOLDS, **tape.run.get("thresholds", {})}
    snapshots = [_snapshot(f) for f in frames]
    dwell = contention.Dwell(thresholds, started_ns=snapshots[0].midpoint_ns)
    previous_over = None
    for a, b in zip(snapshots, snapshots[1:]):
        if (b.midpoint_ns - a.midpoint_ns) / 1e9 > thresholds["interval_s"] * 1.1:
            return Decision("UNMEASURED", "snapshot gap exceeds arm cadence", len(dwell.intervals))
        result = contention.interval(a, b, tree_roots=tape.run.get("tree_roots", []),
                                     include_kernel_task=True, limit=thresholds["cpu_limit_s_per_s"],
                                     aggregate_limit=thresholds["aggregate_cpu_limit_s_per_s"],
                                     previous_over=previous_over)
        previous_over = contention.over_limit(result)
        dwell.add(result)
        if dwell.ready or dwell.expired(b.midpoint_ns):
            verdict = contention.judge(dwell.measurement(started=snapshots[0].started,
                                                        finished=b.finished), thresholds)
            return Decision(verdict.status, "; ".join(verdict.reasons), len(dwell.intervals),
                            _coverage(tape, "snapshot", thresholds["interval_s"]))
    return Decision("UNMEASURED", "trace ended before arm READY or cap", len(dwell.intervals))


def display(tape: Tape):
    from joulewise.environment_admission import environment_observation_failure
    frames = tape.frames("environment")
    for i, frame in enumerate(frames, 1):
        reason = environment_observation_failure(frame["environment"])
        if reason:
            return Decision("REFUSE", reason, i, _coverage(tape, "environment", 5))
    return Decision("PASS", "", len(frames), _coverage(tape, "environment", 5))


def contention_request(tape: Tape):
    """Request finding predicate, not a claim that the hazard driver stops on a flag."""
    frames = tape.frames("contention_interval")
    intervals = [f["contention_interval"] for f in frames]
    request = tape.run.get("request") or {"monotonic_ns": [
        intervals[0]["interval"]["monotonic_ns"][0], intervals[-1]["interval"]["monotonic_ns"][1]]}
    findings = contention.span_findings(intervals, request)
    codes = [f["code"] for f in findings]
    status = ("REFUSE" if "contention.request_overlap" in codes else
              "UNMEASURED" if "contention.unmeasured" in codes else "PASS")
    return Decision(status, "request predicate: " + ", ".join(codes), len(intervals))


def thermal(tape: Tape):
    from joulewise.hazards import thermal as guard
    from joulewise.hazards.base import Measurement
    frames = tape.frames("thermal")
    for i, frame in enumerate(frames, 1):
        sample = frame["thermal"]
        stamp = Stamp(0, int(frame["t"] * 1e9), int(frame["t"] * 1e9))
        measurement = Measurement("thermal", "instant", {"level": sample.get("level")}, (),
                                  stamp, stamp, sample.get("error"))
        if sample.get("level") is None and not sample.get("error"):
            return Decision("UNMEASURED", "missing thermal level", i)
        verdict = guard.judge(measurement, guard.DEFAULT_THRESHOLDS)
        if verdict.status != "PASS":
            return Decision(verdict.status, "; ".join(verdict.reasons), i, _coverage(tape, "thermal", 5))
    return Decision("PASS", "", len(frames), _coverage(tape, "thermal", 5))


BUILTINS = {
    "quiet-pre691": lambda t: _quiet(t, "pre691"),
    "quiet-prel3": lambda t: _quiet(t, "prel3"),
    "quiet-l3": lambda t: _quiet(t, "l3"),
    "smc-pre691": lambda t: _smc(t, "pre691"),
    "smc-prel3": lambda t: _smc(t, "prel3"),
    "smc-l3-redo": lambda t: _smc(t, "l3"),
    "contention-arm": contention_arm, "contention-request": contention_request,
    "display": display, "thermal": thermal,
}


def wilson(k: int, n: int):
    """Two-sided 95% Wilson score interval, null for no measured trials."""
    if not n:
        return None
    z = 1.959963984540054
    p, z2 = k / n, z * z
    center = (p + z2 / (2 * n)) / (1 + z2 / n)
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / (1 + z2 / n)
    return [max(0., center - half), min(1., center + half)]


def replay(corpus: dict, adapters: list[str], *, run_seconds: float, bound: float = .05):
    validate(corpus)
    if not math.isfinite(run_seconds) or run_seconds <= 0 or not 0 <= bound <= 1:
        raise ValueError("positive finite run length and bound in [0,1] required")
    reports = []
    for name in adapters:
        adapter = BUILTINS.get(name)
        source = []
        if adapter is None:
            module_name, function = name.split(":", 1)
            spec = importlib.util.find_spec(module_name)
            if spec is None or not spec.origin or not Path(spec.origin).absolute().is_relative_to(REPO):
                raise ValueError("custom adapters must be trusted modules inside this clone")
            module = importlib.import_module(module_name)
            adapter = getattr(module, function)
            raw = Path(module.__file__).read_bytes()
            source.append({"module": module_name, "sha256": hashlib.sha256(raw).hexdigest()})
        elif name.startswith(("quiet-", "smc-")):
            era = "l3" if name.endswith(("-l3", "-l3-redo")) else name.split("-")[1]
            _, pin = _code_blob(PINS[era], HOST_PATH if name.startswith("quiet") else SMC_PATH)
            source.append(pin)
            source.extend(historical_dependencies(era))
        else:
            filename = {"contention-arm": "hazards/contention.py", "contention-request": "hazards/contention.py",
                        "display": "environment_admission.py",
                        "thermal": "hazards/thermal.py"}[name]
            raw = (REPO / "joulewise" / filename).read_bytes()
            source.append({"path": "joulewise/" + filename, "sha256": hashlib.sha256(raw).hexdigest()})
        decisions = []
        for run in corpus["runs"]:
            try:
                result = adapter(Tape(run))
            except MissingSample as exc:
                result = Decision("UNSUPPORTED", str(exc))
            if not isinstance(result, Decision):
                raise ValueError("adapter must return Decision, not a boolean")
            decisions.append({"run": run["id"], "label": run["label"], "stratum": run["stratum"],
                              "complete": run["complete"], "duration_s": run["duration_s"],
                              **asdict(result)})
        strata = []
        for stratum in sorted({d["stratum"] for d in decisions}):
            for label in ("benign", "contended", "unknown"):
                rows = [d for d in decisions if d["stratum"] == stratum and d["label"] == label]
                if not rows:
                    continue
                measured = [d for d in rows if d["status"] in ("PASS", "REFUSE")]
                k = sum(d["status"] == "REFUSE" for d in measured)
                rate = k / len(measured) if measured else None
                full = [d for d in measured if d["complete"] and d["coverage_complete"]
                        and d["duration_s"] >= run_seconds]
                full_k = sum(d["status"] == "REFUSE" for d in full)
                full_ci = wilson(full_k, len(full))
                # Synthetic and selected incidents can refute a rule, never license a live gate.
                qualified = (stratum == "recorded_representative" and len(full) == len(rows)
                             and full_ci is not None and full_ci[1] <= bound)
                strata.append({"stratum": stratum, "label": label, "total": len(rows),
                               "measured": len(measured), "refused": k, "refusal_rate": rate,
                               "wilson_95": wilson(k, len(measured)),
                               "unmeasured": sum(d["status"] == "UNMEASURED" for d in rows),
                               "unsupported": sum(d["status"] == "UNSUPPORTED" for d in rows),
                               "complete_run_trials": len(full), "complete_run_refused": full_k,
                               "complete_run_wilson_95": full_ci,
                               "metric": {"benign": "false_refusal", "contended": "true_refusal",
                                          "unknown": "unlabelled_refusal"}[label],
                               "assessment": ("ABOVE_BOUND" if label == "benign" and rate is not None and rate > bound
                                              else "WITHIN_BOUND" if label == "benign" and qualified
                                              else "INSUFFICIENT" if label == "benign" else "DESCRIPTIVE")})
        reports.append({"guard": name, "sources": source, "strata": strata, "decisions": decisions})
    return {"schema": "joulewise.guard_replay.report.v1", "run_seconds": run_seconds,
            "idle_bound": bound, "interval": "two-sided 95% Wilson, run as trial; selected incidents descriptive only",
            "implementation_sha256": {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in (REPO / "joulewise/guard_replay.py",
                                                REPO / "joulewise/guard_replay_corpus.py",
                                                REPO / "scripts/guard_replay.py",
                                                REPO / "joulewise/hazards/base.py",
                                                REPO / "joulewise/prewindow.py",
                                                REPO / "joulewise/hazards/contention.py")},
            "limitations": ["No live host validation; CPU-only historical replay neutralises other censuses.",
                            "Unknown labels, missing channels and incomplete runs cannot establish safety.",
                            "Serial/correlated windows violate binomial independence; report host/day clusters separately."],
            "guards": reports}
