"""The thin arm: physics refuses, nothing else enters the decision (plan §2.1, §2.2).

Runs inside the launchd job after t0, in this fixed order:

1. **Agent census** ``pgrep -lf '[c]odex|[c]laude|[t]3'``: it must exit 1 with
   empty output, or the arm refuses before any action (kept by doctrine:
   never start [QUIET-MAC] work while an agent session is alive).
2. **Instant reads**: battery (state from ioreg, current from SMC B0AC),
   thermal (with ``pmset -g therm`` kept as a diagnostic), disk, and the
   clock's frequency gate.  When the config names
   the acceptance's judged epochs (``expected_epochs``), ``kern.osversion`` and
   ``hw.model`` are read too: an epoch no acceptance judges refuses here,
   before the dwell, instead of at the pre-slot writer's epoch check after it.
   A failed read is recorded and never refuses.
3. **Network time OFF, run as an action**: ``sudo -n systemsetup
   -setusingnetworktime off``.  It removes the hazard, so it runs whatever the
   current state is; its output is recorded only, with no wording check.
4. **Record-only collectors** (the flag package's desk/arm collectors), each
   a child process with a timeout.  Their result never changes the decision.
5. **Instrument cadence probe** (about 40 s).
6. **Dwell** (600-2700 s): contention in 30 s intervals; the clock sampled at
   1 Hz for its linearity.
7. **Final reads** of battery, thermal and the frequency word (f must equal
   its dwell value), then the **agent census again** (an agent that started
   during the dwell must not get GO), then GO.

GO only if every verdict is PASS and both censuses are clean; otherwise NULL.
UNMEASURED refuses.  The record is ``<custody>/hazards/arm.json``, written
create-once with fsync; every step is also appended to
``<custody>/hazards/arm.steps.jsonl`` as it happens, and raw probe bytes go to
``<custody>/hazards/arm-raw/``.

This module imports no flag code and nothing from ``arm_readiness*``,
``capture_t0_step``, ``launch_window``, ``t0_rehearsal`` or
``v5_qualification`` (tests/hazards/test_import_graph.py).
"""

from __future__ import annotations

import dataclasses
import json
import os
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from joulewise.hazards import battery, clock, contention, disk, instrument, smc, thermal
from joulewise.hazards.base import (
    PASS, Context, Measurement, Verdict, canonical_json, row, write_create_once,
)

ARM_SCHEMA = "joulewise.hazard_arm.v1"
# Ported from night_gate.AGENT_CENSUS_ARGV (night_gate.py:178); the brackets keep
# a peer pgrep from matching itself.  tests/hazards/test_arm.py pins equality.
AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "[c]odex|[c]laude|[t]3")
NETWORK_TIME_OFF_ARGV = ("/usr/bin/sudo", "-n", "/usr/sbin/systemsetup",
                         "-setusingnetworktime", "off")
# The writer's own identity reads (validate_powermetrics_fiducial._sysctl_identity).
OS_BUILD_ARGV = ("/usr/sbin/sysctl", "-n", "kern.osversion")
HARDWARE_MODEL_ARGV = ("/usr/sbin/sysctl", "-n", "hw.model")
IDENTITY_FIELDS = ("os_build", "hardware_model")
# Recorded with the instant reads, never judged: the power mode is not one of
# the six hazards (doctrine), but a changed mode changes performance, so the
# raw settings are kept beside the numbers.
DIAGNOSTIC_ARGVS = (("/usr/bin/pmset", "-g", "custom"),)
CENSUS_TIMEOUT_S = 10.0
NETWORK_TIME_OFF_TIMEOUT_S = 30.0
DEFAULT_COLLECTOR_TIMEOUT_S = 120.0
MODULES = ("clock", "battery", "thermal", "contention", "disk", "instrument")
GO, NULL = "GO", "NULL"


def default_thresholds() -> dict[str, dict[str, Any]]:
    """The plan's §2.3 values.  A window plan carries its own copy from the
    sealed registration and passes that instead."""

    return {"clock": dict(clock.DEFAULT_THRESHOLDS), "battery": dict(battery.DEFAULT_THRESHOLDS),
            "thermal": dict(thermal.DEFAULT_THRESHOLDS),
            "contention": dict(contention.DEFAULT_THRESHOLDS),
            "disk": dict(disk.DEFAULT_THRESHOLDS),
            "instrument": dict(instrument.DEFAULT_THRESHOLDS)}


@dataclasses.dataclass
class ArmConfig:
    custody_dir: Path
    thresholds: Mapping[str, Mapping[str, Any]]
    disk_targets: Sequence[Mapping[str, Any]]
    tree_roots: Sequence[int] = dataclasses.field(default_factory=lambda: (os.getpid(),))
    record_only: Sequence[Mapping[str, Any]] = ()  # [{"name", "argv", "timeout_s"}]
    powermetrics_executable: str = instrument.POWERMETRICS
    privilege_prefix: Sequence[str] = instrument.PRIVILEGE_PREFIX
    network_time_off_argv: Sequence[str] = NETWORK_TIME_OFF_ARGV
    dwell_tick_s: float = 1.0
    # The acceptance's judged identity epochs (calibration_epoch_continuation.
    # acceptance_judged_epochs); None skips the identity read entirely.
    expected_epochs: Sequence[Mapping[str, Any]] | None = None


@dataclasses.dataclass
class Seams:
    """Hardware seams.  Production uses the defaults; tests replace them."""

    ctx: Context | None = None
    frequency_reader: Callable[[], Mapping[str, Any]] = clock.read_frequency
    boot_reader: Callable[[Context], str] = clock.read_boot_session
    statvfs: Callable[[str], Any] = os.statvfs
    stat: Callable[[str], Any] = os.stat
    python: str = sys.executable
    host_cpu: contention.HostReader | None = contention.read_host_cpu
    # The battery current (SMC B0AC) at the instant and final battery reads;
    # None judges the registry InstantAmperage instead (battery.smc_unavailable).
    smc_read: Callable[[], Mapping[str, Any]] | None = smc.read_once


@dataclasses.dataclass(frozen=True)
class ArmResult:
    decision: str
    reasons: tuple[str, ...]
    refused_at: str | None
    path: Path
    document: Mapping[str, Any]

    @property
    def go(self) -> bool:
        return self.decision == GO


class _Recorder:
    def __init__(self, custody_dir: Path, ctx: Context) -> None:
        self.directory = Path(custody_dir) / "hazards"
        self.directory.mkdir(parents=True, exist_ok=True)
        self.steps_path = self.directory / "arm.steps.jsonl"
        self.ctx = ctx
        self.steps: list[dict[str, Any]] = []
        self.hazards: dict[str, list[dict[str, Any]]] = {name: [] for name in MODULES}

    def step(self, name: str, **fields: Any) -> dict[str, Any]:
        record = {"step": name, "stamp": self.ctx.stamp().to_json(), **fields}
        self.steps.append(record)
        line = json.dumps(record, sort_keys=True, default=str) + "\n"
        descriptor = os.open(self.steps_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            os.write(descriptor, line.encode())
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return record

    def hazard(self, phase: str, measurement: Measurement, verdict: Verdict) -> Verdict:
        self.hazards[verdict.module].append({"phase": phase, "verdict": verdict.to_json(),
                                             "measurement": measurement.to_json()})
        self.step(f"{verdict.module}.{phase}", status=verdict.status, reasons=list(verdict.reasons))
        return verdict


def run(config: ArmConfig, seams: Seams | None = None) -> ArmResult:
    """Run the arm sequence and write ``arm.json``.  Never raises for physics;
    raises only for a misuse (thresholds missing, ``arm.json`` already present)."""

    seams = seams or Seams()
    custody = Path(config.custody_dir)
    arm_path = custody / "hazards" / "arm.json"
    if arm_path.exists():
        raise FileExistsError(f"{arm_path} already exists; an arm record is written once")
    thresholds = {name: dict(config.thresholds[name]) for name in MODULES}
    base_ctx = seams.ctx or Context()
    ctx = dataclasses.replace(base_ctx, raw_dir=custody / "hazards" / "arm-raw",
                              custody_root=custody)
    recorder = _Recorder(custody, ctx)
    started = ctx.stamp()
    record: dict[str, Any] = {
        "schema": ARM_SCHEMA, "started": started.to_json(), "thresholds": thresholds,
        "process": {"pid": os.getpid(), "argv": list(sys.argv), "python": sys.executable},
        "tree_roots": list(config.tree_roots), "census": None, "census_at_go": None,
        "network_time_off": None,
        "record_only": [], "diagnostics": [], "decision": None, "refused_at": None,
        "reasons": []}

    def finish(decision: str, refused_at: str | None, reasons: Sequence[str]) -> ArmResult:
        record.update(decision=decision, refused_at=refused_at, reasons=list(reasons),
                      hazards=recorder.hazards, steps=recorder.steps,
                      finished=ctx.stamp().to_json())
        recorder.step("decision", decision=decision, refused_at=refused_at, reasons=list(reasons))
        write_create_once(arm_path, canonical_json(record) + b"\n")
        return ArmResult(decision, tuple(reasons), refused_at, arm_path, record)

    # 1. Agent census: refuse before any action.
    census = agent_census(ctx)
    record["census"] = census
    recorder.step("census", clean=census["clean"])
    if not census["clean"]:
        return finish(NULL, "census", [census["detail"]])

    # 2. Instant reads.
    def instant(name: str, measurement: Measurement) -> Verdict:
        module = _module(name)
        return recorder.hazard("instant", measurement, module.judge(measurement, thresholds[name]))

    verdicts = [
        instant("battery", battery.measure(_labelled(ctx, "instant"), smc_read=seams.smc_read)),
        instant("thermal", thermal.measure(_labelled(ctx, "instant"), diagnostics=True)),
        instant("disk", disk.measure(ctx, targets=config.disk_targets, statvfs=seams.statvfs,
                                     stat=seams.stat)),
        instant("clock", clock.measure(_labelled(ctx, "instant"),
                                       frequency_reader=seams.frequency_reader,
                                       boot_reader=seams.boot_reader)),
    ]
    for argv in DIAGNOSTIC_ARGVS:
        record["diagnostics"].append(_completed_json(ctx.run(argv, CENSUS_TIMEOUT_S)))
    refused = _refusals(verdicts)
    if refused:
        return finish(NULL, "instant", refused)
    if config.expected_epochs is not None:
        identity = identity_read(ctx, config.expected_epochs)
        record["identity"] = identity
        recorder.step("identity", measured=identity["measured"], judged=identity["judged"])
        if identity["judged"] is False:
            return finish(NULL, "identity", [identity["detail"]])

    # 3. Network time OFF: an action whose output is recorded only.
    off = ctx.run(tuple(config.network_time_off_argv), NETWORK_TIME_OFF_TIMEOUT_S)
    record["network_time_off"] = _completed_json(off)
    recorder.step("network_time_off", returncode=off.returncode, timed_out=off.timed_out)

    # 4. Record-only collectors: never part of the decision.
    for collector in config.record_only:
        record["record_only"].append(_run_collector(ctx, collector))
        recorder.step("record_only", collector=collector.get("name"))

    # 5. Instrument cadence probe.
    probe = instrument.measure(_labelled(ctx, "cadence"), executable=config.powermetrics_executable,
                               privilege_prefix=config.privilege_prefix, python=seams.python)
    verdict = recorder.hazard("probe", probe, instrument.judge(probe, thresholds["instrument"]))
    if not verdict.passed:
        return finish(NULL, "instrument", _refusals([verdict]))

    # 6. Dwell: contention in 30 s intervals, the clock at 1 Hz.
    dwell_started = ctx.stamp()
    boot_start = _boot(seams, ctx)
    samples = [clock.sample(ctx, frequency_reader=seams.frequency_reader)]
    dwell = contention.run_dwell(
        ctx, thresholds["contention"], tree_roots=config.tree_roots,
        on_tick=lambda: samples.append(clock.sample(ctx, frequency_reader=seams.frequency_reader)),
        tick_s=config.dwell_tick_s, host_reader=seams.host_cpu)
    samples.append(clock.sample(ctx, frequency_reader=seams.frequency_reader))
    boot_end = _boot(seams, ctx)
    contention_verdict = recorder.hazard(
        "dwell", dwell, contention.judge(dwell, thresholds["contention"]))
    if not contention_verdict.passed:
        series = clock.series(samples, boot_start=boot_start, boot_end=boot_end,
                              started=dwell_started, finished=ctx.stamp())
        recorder.hazard("dwell", series, clock.judge(series, thresholds["clock"]))
        return finish(NULL, "dwell", _refusals([contention_verdict]))

    # 7. Final reads, then GO.  The GO clock sample closes the dwell series, so
    # f is compared at dwell start, dwell end and GO.
    final_battery = battery.measure(_labelled(ctx, "final"), smc_read=seams.smc_read)
    final_thermal = thermal.measure(_labelled(ctx, "final"))
    finals = [
        recorder.hazard("final", final_battery,
                        battery.judge(final_battery, thresholds["battery"])),
        recorder.hazard("final", final_thermal,
                        thermal.judge(final_thermal, thresholds["thermal"])),
    ]
    samples.append(clock.sample(ctx, frequency_reader=seams.frequency_reader))
    series = clock.series(samples, boot_start=boot_start, boot_end=_boot(seams, ctx),
                          started=dwell_started, finished=ctx.stamp())
    finals.append(recorder.hazard("dwell_and_go", series, clock.judge(series, thresholds["clock"])))
    refused = _refusals(finals)
    if refused:
        return finish(NULL, "final", refused)

    # The census again, last: step 1 ran up to ~47 min earlier (cadence probe
    # plus a dwell of up to 2700 s), and doctrine says never start [QUIET-MAC]
    # work while an agent session is alive.
    census_at_go = agent_census(ctx)
    record["census_at_go"] = census_at_go
    recorder.step("census_at_go", clean=census_at_go["clean"])
    if not census_at_go["clean"]:
        return finish(NULL, "census_at_go", [census_at_go["detail"]])
    return finish(GO, None, [])


def agent_census(ctx: Context) -> dict[str, Any]:
    """Clean only when pgrep exits 1 with empty output (night_gate.agent_census's rule)."""

    completed = ctx.run(AGENT_CENSUS_ARGV, CENSUS_TIMEOUT_S)
    stdout = completed.stdout.decode("utf-8", errors="replace")
    clean = (completed.error is None and not completed.timed_out
             and completed.returncode == 1 and stdout.strip() == "")
    if clean:
        detail = "no agent process"
    elif completed.error or completed.timed_out:
        detail = f"agent census did not run: {completed.error or 'timed out'}"
    else:
        lines = stdout.strip().splitlines()
        detail = f"agent census exit {completed.returncode}"
        if lines:
            detail += "; agent process present: " + "; ".join(lines[:20])
    return {"argv": list(AGENT_CENSUS_ARGV), "returncode": completed.returncode,
            "stdout": stdout, "stderr": completed.stderr.decode("utf-8", errors="replace"),
            "timed_out": completed.timed_out, "error": completed.error, "clean": clean,
            "detail": detail, "stamp": ctx.stamp().to_json()}


def identity_read(ctx: Context, expected_epochs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Read ``kern.osversion`` and ``hw.model``; judge them only when both reads succeed.

    ``judged`` is True when ``{os_build, hardware_model}`` is one of the
    expected epochs (projected to those two fields), False when it is not, and
    None when a read failed: an unread identity is recorded and never refuses.
    """

    measured: dict[str, str | None] = {}
    reads: list[dict[str, Any]] = []
    for field, argv in zip(IDENTITY_FIELDS, (OS_BUILD_ARGV, HARDWARE_MODEL_ARGV)):
        completed = ctx.run(argv, CENSUS_TIMEOUT_S)
        reads.append(_completed_json(completed))
        value = completed.stdout.decode("utf-8", errors="replace").strip()
        ok = (completed.error is None and not completed.timed_out
              and completed.returncode == 0 and bool(value))
        measured[field] = value if ok else None
    expected = [{field: epoch.get(field) for field in IDENTITY_FIELDS}
                for epoch in expected_epochs if isinstance(epoch, Mapping)]
    judged: bool | None = None
    detail = "identity read failed; recorded only"
    if not expected:
        detail = "no judged epoch to compare; recorded only"
    elif all(measured[field] is not None for field in IDENTITY_FIELDS):
        judged = measured in expected
        detail = ("identity epoch judged by the acceptance" if judged else
                  f"identity os_build={measured['os_build']} hardware_model="
                  f"{measured['hardware_model']} is not an epoch the acceptance judges "
                  f"({expected})")
    return {"measured": measured, "expected": expected, "judged": judged, "detail": detail,
            "reads": reads}


def _module(name: str):
    return {"clock": clock, "battery": battery, "thermal": thermal, "contention": contention,
            "disk": disk, "instrument": instrument}[name]


def _labelled(ctx: Context, label: str) -> Context:
    return dataclasses.replace(ctx, label=label)


def _refusals(verdicts: Sequence[Verdict]) -> list[str]:
    return [f"{item.module} {item.status}: {'; '.join(item.reasons)}"
            for item in verdicts if item.status != PASS]


def _boot(seams: Seams, ctx: Context) -> str | None:
    try:
        return seams.boot_reader(ctx)
    except Exception:
        return None


def _completed_json(completed) -> dict[str, Any]:
    return {"argv": list(completed.argv), "returncode": completed.returncode,
            "timed_out": completed.timed_out, "error": completed.error,
            "stdout": completed.stdout.decode("utf-8", errors="replace"),
            "stderr": completed.stderr.decode("utf-8", errors="replace")}


def _run_collector(ctx: Context, collector: Mapping[str, Any]) -> dict[str, Any]:
    name = str(collector.get("name") or "collector")
    started = ctx.stamp()
    entry: dict[str, Any] = {"name": name, "argv": list(collector.get("argv") or ()),
                             "started": started.to_json()}
    try:
        argv = [str(item) for item in collector["argv"]]
        timeout_s = float(collector.get("timeout_s", DEFAULT_COLLECTOR_TIMEOUT_S))
        completed = ctx.run(argv, timeout_s)
        raw = ctx.keep_raw(f"collector-{_safe(name)}.stdout", completed.stdout)
        entry.update(returncode=completed.returncode, timed_out=completed.timed_out,
                     error=completed.error, stdout=raw.to_json(),
                     stderr=completed.stderr.decode("utf-8", errors="replace")[-4000:])
    except Exception as exc:  # a collector never changes the arm decision
        entry.update(error=f"{type(exc).__name__}: {exc}")
    finished = ctx.stamp()
    entry["finished"] = finished.to_json()
    entry["elapsed_s"] = (finished.monotonic_ns - started.monotonic_ns) / 1e9
    return entry


def _safe(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in name)[:64] or "collector"


# Inventory rows the arm as a whole now evaluates: the agent census kept by
# doctrine, and T-0/GO composites whose physics the modules above measure.
PROTECTS: tuple[tuple[str, str, str, int], ...] = (
    # base line 492: A probe binary could not be spawned.
    row("joulewise/arm_readiness_evidence_t0.py", "_execute_probe",
        "ValueError (wrapped at 524/534)", 1),
    # base line 494: A probe exceeded its timeout (45 s default, 5 s for ps, the battery probe's own b...
    row("joulewise/arm_readiness_evidence_t0.py", "_execute_probe",
        "ValueError (wrapped at 524/534)", 2),
    # base line 524: Any fresh live probe could not execute or timed out: sntp R1, pgrep, ps, pmset ba...
    row("joulewise/arm_readiness_evidence_t0.py", "_fresh_probe",
        "evidence_author_t0_<kind>_underivable", 1),
    # base line 3044: Re-observes the census, the machine predicates (C3) and the clock and boot (C4) b...
    row("scripts/run_night.py", "bind_until_quiet.hard_done",
        "stop(dynamic hard refusal reason) from night_gate.evaluate_dynamic_hard", 1),
    # base line 3803: capture_t0_step sequence exits 0.
    row("scripts/run_night.py", "_capture_qualification_t0",
        "PackNightRefusal 'T-0 capture stage refused'", 1),
    # base line 3901: Every derivation admission error maps to one night_probe_error refusal.
    row("scripts/run_night.py", "run_night",
        "night_probe_error funnel for DIAGNOSTIC_NO_PACK derivation admission (manifest, budget, OFF, dwell)", 1),
    # base line 3976: The pack, quiet-binding or legacy night_gate receipt verdict is GO.
    row("scripts/run_night.py", "run_night",
        "gate verdict != GO -> refusal.json, result REFUSED, EXIT_REFUSED", 1),
)

# Proxy rows on paths block 5 no longer runs that this module's direct
# measurement replaces (configs/gates/physics_rows.json, "retired_proxy").
SUPERSEDES: tuple[tuple[str, str, str, int], ...] = (
    # base line 1123: A fresh process census finds no agent, browser, keep_awake or monitor process cla...
    row("joulewise/arm_readiness.py", "<module>",
        "predicate t0.no_stray_keepawake.v1", 1),
    # base line 2860: Each GO condition C1..C5 must be in order with status 'PASS'. C3 is the quiet-mac...
    row("joulewise/arm_readiness.py", "validate_pack_night_go_receipt",
        "readiness_schema_invalid -> launch_go_receipt_invalid (conditions.C{n})", 1),
    # base line 7168: The PROCESS_CENSUS receipt says the agent, browser, keep_awake and monitor proces...
    row("joulewise/arm_readiness.py", "_evaluate_rows",
        "readiness_dependency_refused (row t0.no_stray_keepawake)", 1),
    # base line 10314: the GO records an agent census (pgrep -lf codex|claude|t3) that exited 1 with emp...
    row("joulewise/arm_readiness.py", "_authenticate_pack_launch_go",
        "launch_go_receipt_invalid:census", 1),
    # base line 1414: pgrep finds any caffeinate, agent session, browser app binary, or monitor (powerm...
    row("joulewise/arm_readiness_evidence_t0.py", "_expect_absent",
        "evidence_author_t0_process_census_underivable", 1),
    # base line 105: Count of processes whose comm basename matches ^(codex|claude|t3|mcp-server|run_c...
    row("joulewise/prewindow.py", "t0_check",
        "BLOCK agent/measurement process(es) already running", 1),
    # base line 109: ps -A -o comm= ran.
    row("joulewise/prewindow.py", "t0_check",
        "BLOCK agent process probe failed", 1),
    # base line 818: each process exited with its registered code, incl. pgrep agent/browser/monitor/c...
    row("joulewise/t0_rehearsal.py", "evaluate_g1",
        "G1 FAIL did not complete successfully", 1),
    # base line 1332: agent exit stamp precedes capture start
    row("joulewise/t0_rehearsal.py", "evaluate_g8",
        "G8 agent did not exit before capture began", 1),
    # base line 1366: no argv matching codex|claude|t3 during capture
    row("joulewise/t0_rehearsal.py", "evaluate_g8",
        "G8 agent process existed during capture census N", 1),
    # base line 61: Fifteen T-0 evidence receipts: background quiet, clock anchor, battery, network t...
    row("scripts/author_arm_evidence_t0.py", "main",
        "relay of T0EvidenceAuthoringError / ArmReadinessError -> REFUSE exit 2 (55-70)", 1),
    # base line 107: G8 agent exit ordering and capture-time pgrep censuses
    row("scripts/harvest_v5_qualification.py", "harvest",
        "g8_not_passed", 1),
    # base line 165: Count of processes whose comm matches codex|claude|t3|mcp-server|run_campaign|win...
    row("scripts/prewindow_check.sh", "check_once",
        "BLOCK agent/measurement process(es) already running", 1),
    # base line 99: pgrep agent census returned an exit code other than 0/1 or rc1 with output
    row("scripts/produce_t0_rehearsal_bundle.py", "census",
        "agent census observation failed", 1),
    # base line 131: agents did not exit within timeout
    row("scripts/produce_t0_rehearsal_bundle.py", "observe_standdown",
        "stand-down exit observation timed out", 1),
    # base line 144: pgrep finds an agent name after stand-down
    row("scripts/produce_t0_rehearsal_bundle.py", "observe_standdown",
        "new agent present after stand-down", 1),
    # base line 551: in-capture pgrep census argv/exit code
    row("scripts/produce_t0_rehearsal_bundle.py", "assemble",
        "capture agent census observation failed", 1),
    # base line 2338: Qualification t0 capture, control order, start budget, the network-time-OFF recei...
    row("scripts/run_night.py", "arm_only",
        "refusals from _capture_qualification_t0 (2335), _admit_qualification_control_order (2336), _derivation_start_budget (2337), _admit_network_time_off + _admit_qualification_clean_dwell (2338) (call sites; bodies at 3350-3750)", 1),
    # base line 2419: At GO, 'pgrep -lf [c]odex|[c]laude|[t]3' exits 1 with empty stdout. Any matching...
    row("scripts/run_night.py", "_produce_pack_go",
        "PackNightRefusal census: <agent present | stdout must be empty>", 1),
    # base line 2948: The agent-census pgrep exits 0 with output or 1 with empty output; any other comb...
    row("scripts/run_night.py", "_binding_census",
        "night_probe_error 'binding census probe failed' (also 3060 'initial census probe failed')", 1),
    # base line 3062: The driver's first agent census (pgrep for claude/codex and similar) found no age...
    row("scripts/run_night.py", "bind_until_quiet",
        "stop(initial census refusal, e.g. night_refused_agent_present)", 1),
    # base line 3122: Each periodic agent census during binding finds no agent process.
    row("scripts/run_night.py", "bind_until_quiet",
        "stop(census record refusal), cadenced agent census during binding", 1),
    # base line 3162: The sampler's own census, taken during the sample, found no agent process.
    row("scripts/run_night.py", "bind_until_quiet",
        "night_refused_agent_present 'sampler census hit'", 1),
    # base line 3912: The driver's first agent census on a pack night exits 1 with empty stdout (no age...
    row("scripts/run_night.py", "run_night",
        "PackNightRefusal 'census: ...' / initial_refusal.reason (night_refused_agent_present)", 1),
    # base line 181: stand-down record shows exits and an empty after-census
    row("scripts/v5_s1_desk_closeout.py", "closeout",
        "stand-down observation absent", 1),
)
