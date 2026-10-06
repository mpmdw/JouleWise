"""The HAZARD_PACK branch of ``scripts/run_night.py`` (block 5; gate-prune plan L2).

Ed's ruling of 2026-10-05: an arm refuses only on a physical hazard, measured
directly; every other check is a recorded flag and never stops collection.
Inside the launchd job, after t0, this branch runs:

1. the agent census (``pgrep`` must exit 1 with empty output; doctrine keeps it);
2. the hazard arm (``joulewise.hazards.arm``): instant reads, network time OFF
   as an action, the record-only collectors, the cadence probe, the dwell and
   the final reads. Only PASS from all six modules -- clock, battery, thermal,
   contention, disk, instrument -- is GO. A REFUSE or an UNMEASURED verdict is
   a NULL window: nothing is published, started or launched;
3. a final census, then the launch-lineage files (``joulewise.window_lineage``)
   into both runs roots;
4. the executed-file inventory of the measurement checkout (local reads only);
5. the hazard monitor (``scripts/hazard_monitor.py``) in its own process group
   under ``taskpolicy -b``; a one-second supervision pass restarts it if it dies;
6. the chain, launched once through the driver's no-pack path
   (``_claim_chain_start`` / ``_run_chain_once`` / ``_WindowDeadline`` /
   ``_terminate_process_group``), with the in-chain agent census kept as an
   abort and a driver stop when free disk falls under the in-window floor;
7. G10 (``scripts/g10_clock_step_control.py``) when the plan asks for it, after
   the chain's process group is proven gone, with the monitor still journaling;
8. the monitor stop, then the terminal records (``night/hazard_result.json``,
   ``night/result.json``) and the structure-only courier.

Facts that are not physics -- the chain's bytes against its sidecar, the OFF
setter's wording, a lineage publication failure, a disk stop -- are written as
``joulewise.flag.v1`` records to ``<custody>/flags/driver.jsonl``.

Every hardware or other-lane dependency is a field of :class:`Seams`, so tests
drive the real branch with fakes only at those seams.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from joulewise import night_gate
from joulewise.b5 import chain as b5_chain

HAZARD_RESULT_SCHEMA = "joulewise.b5_hazard_night.v1"
ARM_DECISION_SCHEMA = "joulewise.b5_arm_decision.v1"
DRY_ARM_SCHEMA = "joulewise.b5_dry_arm.v1"
INVENTORY_SCHEMA = "joulewise.b5_executed_inventory.v1"
NETWORK_TIME_ACTION_SCHEMA = "joulewise.b5_network_time_off_action.v1"
COLLECTORS_SCHEMA = "joulewise.b5_arm_collectors.v1"
LINEAGE_SCHEMA = "joulewise.b5_lineage_publication.v1"
MONITOR_JOURNAL_SCHEMA = "joulewise.b5_monitor_supervision.v1"
G10_DRIVER_SCHEMA = "joulewise.b5_g10_driver.v1"
FLAG_SCHEMA = "joulewise.flag.v1"

PASS, REFUSE, UNMEASURED = "PASS", "REFUSE", "UNMEASURED"
HAZARD_MODULES = night_gate.HAZARD_MODULES
REFUSED_HAZARD = "night_refused_hazard"
STOPPED_DISK_LOW = "night_stopped_disk_low"
if {REFUSED_HAZARD, STOPPED_DISK_LOW} != set(night_gate.HAZARD_DRIVER_REASON_CODES):
    raise RuntimeError("hazard driver codes drifted from night_gate.HAZARD_DRIVER_REASON_CODES")

NETWORK_TIME_OFF_ARGV = ("/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-setusingnetworktime", "off")
TASKPOLICY_ARGV = ("/usr/sbin/taskpolicy", "-b")
OFF_TIMEOUT_S = 30.0
COLLECTOR_TIMEOUT_S = 120.0
ARM_RETURN_GRACE_S = 300.0
MONITOR_STOP_GRACE_S = 10.0
MONITOR_RESTART_INTERVAL_S = 1.0
MONITOR_RESTART_BACKOFF_S = 30.0
MONITOR_BACKOFF_AFTER = 5
DISK_CHECK_INTERVAL_S = 60.0
DISK_LOW_BYTES_DEFAULT = 10 * 1024 ** 3
G10_TIMEOUT_S = 300.0 + 900.0 + 300.0
G10_TERM_GRACE_S = 120.0
GIT_TIMEOUT_S = 60.0

ARM_DECISION = "arm_decision.json"
HAZARD_RESULT = "hazard_result.json"
NETWORK_TIME_ACTION = "network_time_off.action.json"
COLLECTORS_RECORD = "arm_collectors.json"
INVENTORY_RECORD = "executed_inventory.json"
LINEAGE_RECORD = "lineage.json"
MONITOR_JOURNAL = "monitor_supervision.jsonl"
G10_RECORD = "g10.json"
G10_DRIVER_RECORD = "g10.driver.json"
DRIVER_FLAGS = "driver.jsonl"


# --------------------------------------------------------------------------
# Small shared pieces


def stamp() -> dict[str, Any]:
    """One instant on the wall, ``time.monotonic_ns`` and CLOCK_MONOTONIC_RAW clocks."""

    try:
        raw = time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
    except (AttributeError, OSError):
        raw = None
    return {"wall_s": time.time(), "monotonic_ns": time.monotonic_ns(), "monotonic_raw_ns": raw}


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, default=str) + "\n").encode("utf-8")


def _create_once(path: Path, value: Any) -> Path:
    """Create ``path`` exclusively (``name-NN`` if taken) and fsync it; return the name used."""

    raw = _json_bytes(value)
    index = 0
    while True:
        candidate = path if index == 0 else path.with_name(f"{path.stem}-{index:02d}{path.suffix}")
        try:
            descriptor = os.open(candidate, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            index += 1
            continue
        try:
            view = memoryview(raw)
            while view:
                written = os.write(descriptor, view)
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return candidate


def _append_line(path: Path, value: Any) -> None:
    payload = (json.dumps(value, sort_keys=True, default=str) + "\n").encode("utf-8")
    descriptor = os.open(path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
    try:
        os.write(descriptor, payload)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def _error_text(error: BaseException) -> str:
    try:
        return f"{type(error).__name__}: {error}"
    except Exception:  # noqa: BLE001
        return type(error).__name__


@dataclasses.dataclass(frozen=True)
class CommandResult:
    argv: tuple[str, ...]
    returncode: int | None
    stdout: str
    stderr: str
    timed_out: bool
    error: str | None
    started: Mapping[str, Any]
    ended: Mapping[str, Any]

    def record(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def run_bounded(argv: Sequence[str], timeout_s: float) -> CommandResult:
    """Run one command in its own process group; kill the group at the timeout."""

    started = stamp()
    command = tuple(str(item) for item in argv)
    try:
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
    except OSError as error:
        return CommandResult(command, None, "", "", False, _error_text(error), started, stamp())
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        stdout, stderr = process.communicate()
    return CommandResult(command, process.returncode, stdout.decode("utf-8", "replace"),
                         stderr.decode("utf-8", "replace"), timed_out, None, started, stamp())


def _statvfs_free_bytes(path: Path) -> int:
    """Free bytes available to this user on the volume holding ``path`` or its nearest ancestor."""

    candidate = Path(path)
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    stats = os.statvfs(candidate)
    return int(stats.f_bavail) * int(stats.f_frsize)


def _git(root: Path, args: Sequence[str]) -> bytes:
    completed = subprocess.run(
        ["/usr/bin/git", "-c", "core.fsmonitor=false", "-C", str(root), "--no-optional-locks", *args],
        stdin=subprocess.DEVNULL, capture_output=True, timeout=GIT_TIMEOUT_S, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} exited {completed.returncode}: "
                           f"{completed.stderr.decode('utf-8', 'replace').strip()}")
    return completed.stdout


def _boot_session_uuid() -> str | None:
    try:
        completed = subprocess.run(["/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"],
                                   capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    value = completed.stdout.strip()
    return value or None


# --------------------------------------------------------------------------
# Flags (joulewise.flag.v1); the L4 flags package when present


_SCOPE_KEYS = ("level", "plan_id", "attempt", "stage_id", "run_id", "bundle_id")
_SOURCE_KEYS = ("stage", "collector", "legacy_site", "legacy_code")


def build_flag(fields: Mapping[str, Any], *, boot_session_uuid: str | None = None) -> dict[str, Any]:
    """A ``joulewise.flag.v1`` record built exactly as ``joulewise.flags.schema.make_flag`` builds it.

    Used only when the flags package cannot be imported; the harvest re-reads
    and validates every flag line either way.
    """

    scope = {key: (fields.get("scope") or {}).get(key) for key in _SCOPE_KEYS}
    source = {key: (fields.get("source") or {}).get(key) for key in _SOURCE_KEYS}
    observed = fields.get("observed")
    interval = dict(fields.get("interval") or {"monotonic_ns": None, "monotonic_raw_ns": None, "wall_s": None})
    # The identity includes the interval, as joulewise.flags.schema.compute_flag_id does.
    identity = json.dumps({"code": fields["code"], "scope": scope, "observed": observed, "source": source,
                           "interval": interval},
                          sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return {
        "schema_version": FLAG_SCHEMA,
        "flag_id": hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20],
        "code": fields["code"], "family": fields["family"], "klass": fields["klass"],
        "scope": scope,
        "interval": interval,
        "source": source, "observed": observed, "expected": fields.get("expected"),
        "evidence": [dict(item) for item in fields.get("evidence") or ()],
        "detail": " ".join(str(fields.get("detail", "")).split())[:2000],
        "emitted": {"wall_s": time.time(), "monotonic_ns": time.monotonic_ns(),
                    "boot_session_uuid": boot_session_uuid},
        "catalog_sha256": None, "blinding": fields.get("blinding", "STRUCTURE"),
    }


def _emit_flag_production(custody_root: Path, fields: Mapping[str, Any]) -> None:
    path = Path(custody_root) / "flags" / DRIVER_FLAGS
    try:
        from joulewise.flags.schema import make_flag
        from joulewise.flags.sink import FlagSink
    except ImportError:
        path.parent.mkdir(parents=True, exist_ok=True)
        _append_line(path, build_flag(fields, boot_session_uuid=_boot_session_uuid()))
        return
    FlagSink(path).append(make_flag(**fields))


# --------------------------------------------------------------------------
# The seams


@dataclasses.dataclass(frozen=True)
class ArmContext:
    """Everything ``joulewise.hazards.arm`` needs; the arm returns a decision.

    Order (gate-prune plan section 2.2): census (done, ``census``), instant
    reads, network time OFF as an action, the record-only collectors, the
    cadence probe, the dwell, the final reads. An arm may run OFF and the
    collectors itself (``joulewise.hazards.arm.run`` does, from
    ``record_only_argv``) and return their records as ``network_time_off`` and
    ``record_only``, or call the two hooks. The hooks never raise and never
    change the decision; whatever the arm did not run, the driver runs before
    launch. ``record_root`` is where ``arm.json`` goes (``<custody>/hazards``
    for a window, a fresh directory for a dry-arm).
    """

    plan: Any
    plan_path: Path
    custody_root: Path
    night_dir: Path
    record_root: Path
    hazard_window: Mapping[str, Any]
    thresholds: Mapping[str, Mapping[str, Any]]
    t_stream_max_s: float
    planned_bytes: int
    disk_volumes: tuple[Path, ...]
    disk_targets: tuple[Mapping[str, Any], ...]
    measurement_tree_pids: tuple[int, ...]
    census: Mapping[str, Any]
    arm_deadline_epoch_s: float
    dry_arm: bool
    record_only_argv: tuple[str, ...]
    network_time_off: Callable[[], Mapping[str, Any]]
    record_only_collectors: Callable[[], Mapping[str, Any]]
    agent_census: Callable[[], Mapping[str, Any]]


@dataclasses.dataclass(frozen=True)
class LineageRequest:
    """Input of ``joulewise.window_lineage`` publication into both runs roots."""

    plan: Any
    plan_path: Path
    custody_root: Path
    night_dir: Path
    hazard_window: Mapping[str, Any]
    claim_runs_root: Path
    bound_runs_root: Path
    arm_record_path: Path | None
    arm_decision_path: Path | None
    boot_session_uuid: str | None


@dataclasses.dataclass(frozen=True)
class MonitorRequest:
    plan: Any
    plan_path: Path
    custody_root: Path
    night_dir: Path
    driver_pid: int


@dataclasses.dataclass(frozen=True)
class CollectorRequest:
    plan: Any
    plan_path: Path
    custody_root: Path
    stage: str  # "arm"


@dataclasses.dataclass
class Seams:
    arm: Callable[[ArmContext], Any]
    publish_lineage: Callable[[LineageRequest], Any]
    monitor_argv: Callable[[MonitorRequest], Sequence[str]]
    collectors_argv: Callable[[CollectorRequest], Sequence[str]]
    g10_argv: Callable[[Path, float], Sequence[str]]
    run_command: Callable[[Sequence[str], float], CommandResult] = run_bounded
    popen: Callable[..., Any] = subprocess.Popen
    disk_free_bytes: Callable[[Path], int] = _statvfs_free_bytes
    git: Callable[[Path, Sequence[str]], bytes] = _git
    emit_flag: Callable[[Path, Mapping[str, Any]], None] = _emit_flag_production
    boot_session_uuid: Callable[[], str | None] = _boot_session_uuid


_STATUS_ORDER = {PASS: 0, "NOT_EVALUATED": 1, UNMEASURED: 2, REFUSE: 3}


def _nearest_existing(path: Path) -> Path:
    candidate = Path(path)
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    return candidate


def disk_targets(window: Mapping[str, Any], *, arm: bool) -> list[dict[str, Any]]:
    """The disk module's targets: ``[{"path", "copies"}]``, runs root first.

    At arm the claim runs root holds one copy of the planned bytes and each
    backup destination one more; the bound root and the custody root need only
    headroom. In the window only the volumes the chain writes to are watched,
    so a full backup volume never stops a chain. A path that does not exist yet
    is read on its nearest existing ancestor (same volume unless a mount sits
    lower), and the requested path is kept beside it.
    """

    roots, bindings = window["runs_roots"], window["bindings"]
    custody = Path(window["window_env"]["path"]).parent
    rows = [(roots["claim"], 1), (roots["bound"], 0), (str(custody), 0)]
    if arm:
        rows += [(bindings["claim_backup_destination"], 1), (bindings["bound_backup_destination"], 1)]
    return [{"path": str(_nearest_existing(Path(path))), "requested_path": str(path), "copies": copies}
            for path, copies in rows]


def _arm_thresholds(context: ArmContext) -> dict[str, dict[str, Any]]:
    """The window plan's thresholds, with the window's own sizing in the two sized keys.

    ``disk.planned_bytes`` and ``clock.t_stream_max_s`` always come from the
    window (its member count times bytes per member, and its sourced sizing),
    never from a copied threshold value, so a stale copy can neither loosen nor
    misstate either gate. The plan writer records any copy it replaced.
    """

    thresholds = json.loads(json.dumps(context.thresholds))
    thresholds.setdefault("disk", {})["planned_bytes"] = int(context.planned_bytes)
    thresholds.setdefault("clock", {})["t_stream_max_s"] = float(context.t_stream_max_s)
    return thresholds


def _production_arm(context: ArmContext) -> dict[str, Any]:
    """``joulewise.hazards.arm.run`` (lane L1), read back into the driver's decision shape."""

    from joulewise.hazards import arm as hazard_arm
    config = hazard_arm.ArmConfig(
        custody_dir=context.record_root.parent, thresholds=_arm_thresholds(context),
        disk_targets=[dict(item) for item in context.disk_targets],
        tree_roots=tuple(context.measurement_tree_pids),
        record_only=[{"name": "flags.arm", "argv": list(context.record_only_argv),
                      "timeout_s": COLLECTOR_TIMEOUT_S}] if context.record_only_argv else [])
    result = hazard_arm.run(config)
    document = result.document if isinstance(result.document, Mapping) else {}
    verdicts: dict[str, str] = {}
    for module, entries in (document.get("hazards") or {}).items():
        statuses = [_verdict_status(entry.get("verdict")) or UNMEASURED
                    for entry in entries if isinstance(entry, Mapping)]
        if statuses:
            verdicts[str(module)] = max(statuses, key=lambda status: _STATUS_ORDER.get(status, 2))
    for module in HAZARD_MODULES:
        verdicts.setdefault(module, "NOT_EVALUATED")
    return {"go": bool(result.go), "verdicts": verdicts, "reasons": list(result.reasons),
            "refused_at": result.refused_at, "record_path": str(result.path),
            "network_time_off": document.get("network_time_off"),
            "record_only": document.get("record_only")}


def _production_lineage(request: LineageRequest) -> Any:
    """``joulewise.window_lineage.publish_window_lineage`` (lane L3).

    The lineage carries the pack's own plan and window ids: the controller's
    pre-slot route compares them with the bracket session the chain reserves
    (``--plan-id``/``--window-id`` from the plan tree).
    """

    from joulewise import window_lineage
    window = request.hazard_window
    pack = window["pack"]
    return window_lineage.publish_window_lineage(
        pack_root=pack["pack_root"], pack_id=pack["pack_id"], plan_id=pack["pack_plan_id"],
        window_id=pack["window_id"], bracket_session_id=window["bracket_session_id"],
        pre_attempt_id=window["bindings"]["pre_attempt_id"],
        post_attempt_id=window["bindings"]["post_attempt_id"],
        claim_runs_root=request.claim_runs_root, bound_runs_root=request.bound_runs_root,
        custody_root=request.custody_root, night_dir=request.night_dir,
        pack_sha256=pack["pack_sha256"], arm_decision_path=request.arm_decision_path,
        boot_session_id=request.boot_session_uuid)


def production_seams(repo_root: Path) -> Seams:
    """The production seams; ``repo_root`` is the driver's own checkout."""

    repo_root = Path(repo_root)

    def monitor_argv(request: MonitorRequest) -> list[str]:
        """Write the monitor's config once (lane L1's format) and return its command line."""

        from joulewise.hazards import monitor as hazard_monitor
        window = request.plan.hazard_window
        thresholds = window["thresholds"]
        config = hazard_monitor.build_config(
            custody_dir=request.custody_root, tree_roots=(request.driver_pid,),
            disk_targets=disk_targets(window, arm=False),
            low_bytes=int(thresholds.get("disk", {}).get("low_bytes", DISK_LOW_BYTES_DEFAULT)),
            cpu_limit_s_per_s=float(thresholds.get("contention", {}).get("cpu_limit_s_per_s", 0.05)))
        path = hazard_monitor.monitor_dir(request.custody_root) / "config.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            _create_once(path, hazard_monitor.validate_config(config))
        return [*TASKPOLICY_ARGV, sys.executable, "-B", str(repo_root / "scripts/hazard_monitor.py"),
                "--config", str(path)]

    def collectors_argv(request: CollectorRequest) -> list[str]:
        plan, window = request.plan, request.plan.hazard_window
        measurement = Path(plan.measurement_root)
        bindings = window["bindings"]
        argv = [sys.executable, "-B", str(repo_root / "scripts/collect_window_flags.py"),
                "--stage", request.stage, "--custody", str(request.custody_root),
                "--repo", str(measurement), "--pack", window["pack"]["pack_root"],
                "--plan-id", plan.plan_id, "--attempt", str(window["attempt"]),
                "--h-claim", plan.measurement_head,
                "--chain", plan.chain_path, "--chain-sidecar", plan.chain_sha256_path,
                "--ledger", bindings["ledger_path"],
                "--head-pin", str(measurement / "configs/calibration/calibration_ledger_head.json"),
                "--session-id", window["bracket_session_id"]]
        if window["pack"]["pack_sha256"]:
            argv += ["--expected-pack-tree-sha256", window["pack"]["pack_sha256"]]
        calibration_plan = Path(window["pack"]["pack_root"]) / "calibration_plan.json"
        if calibration_plan.is_file():
            argv += ["--calibration-plan", str(calibration_plan)]
        # The sealed files, when the measurement checkout holds them. Without the
        # identity pins the model collector records model.identity_unpinned.
        for flag, relative in (("--catalog", "configs/campaigns/v5_claim_25g83/flag_catalog.json"),
                               ("--sealed-inventory", "configs/campaigns/v5_claim_25g83/sealed_inventory.json"),
                               ("--identity-pins", "configs/campaigns/v5_claim_25g83/identity_pins.json")):
            if (measurement / relative).is_file():
                argv += [flag, str(measurement / relative)]
        return argv

    def g10_argv(night_dir: Path, t_stream_max_s: float) -> list[str]:
        return [sys.executable, "-B", str(repo_root / "scripts/g10_clock_step_control.py"),
                "--night-dir", str(night_dir), "--t-stream-max-s", repr(float(t_stream_max_s))]

    return Seams(arm=_production_arm, publish_lineage=_production_lineage,
                 monitor_argv=monitor_argv, collectors_argv=collectors_argv, g10_argv=g10_argv)


# --------------------------------------------------------------------------
# The arm decision


def _verdict_status(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        for key in ("status", "verdict"):
            if isinstance(value.get(key), str):
                return value[key]
    status = getattr(value, "status", None) or getattr(value, "verdict", None)
    return status if isinstance(status, str) else None


def normalize_decision(raw: Any) -> dict[str, Any]:
    """Read an arm result conservatively: GO needs ``go`` true AND six PASS verdicts.

    Anything unreadable is UNMEASURED, which refuses (plan section 2.1).
    """

    def get(name: str) -> Any:
        return raw.get(name) if isinstance(raw, Mapping) else getattr(raw, name, None)

    go = get("go")
    if go is None and isinstance(get("verdict"), str):
        go = get("verdict") == "GO"
    verdicts_raw = get("verdicts")
    verdicts: dict[str, str] = {}
    if isinstance(verdicts_raw, Mapping):
        for name, value in verdicts_raw.items():
            verdicts[str(name)] = _verdict_status(value) or UNMEASURED
    for name in HAZARD_MODULES:
        verdicts.setdefault(name, UNMEASURED)
    reasons_raw = get("reasons")
    reasons = [str(item) for item in reasons_raw] if isinstance(reasons_raw, (list, tuple)) else []
    not_pass = sorted(name for name in HAZARD_MODULES if verdicts[name] != PASS)
    record_path = get("record_path") or get("path")
    decision_go = go is True and not not_pass
    if go is True and not_pass:
        reasons.append("arm reported GO without PASS from: " + ", ".join(not_pass))
    refused_at = get("refused_at")
    return {"go": decision_go, "verdicts": verdicts, "not_pass": not_pass,
            "reasons": reasons, "record_path": str(record_path) if record_path else None,
            "refused_at": refused_at if isinstance(refused_at, str) else None,
            "network_time_off": get("network_time_off"), "record_only": get("record_only")}


# --------------------------------------------------------------------------
# Monitor supervision and the in-window disk floor


class MonitorSupervisor:
    """Start, supervise and stop the hazard monitor in its own process group."""

    def __init__(self, argv: Sequence[str] | Callable[[], Sequence[str]], *, night_dir: Path,
                 popen: Callable[..., Any],
                 group_census: Callable[[int, float], tuple[bool, list[str]]] | None = None,
                 identity: Callable[[int], Any] | None = None) -> None:
        self.argv_factory = argv if callable(argv) else (lambda: argv)
        self.argv: list[str] = []
        self.night_dir = Path(night_dir)
        self.journal = self.night_dir / MONITOR_JOURNAL
        self.popen = popen
        self.group_census = group_census
        self.identity = identity
        self.process: Any = None
        self.starts = 0
        self.start_failures = 0
        self.consecutive_failures = 0
        self.exits: list[dict[str, Any]] = []
        self.gaps: list[dict[str, Any]] = []
        self.last_attempt = -float("inf")
        self.down_since: dict[str, Any] | None = None
        self.stopped = False
        self.stop_record: dict[str, Any] | None = None
        self.errors: list[str] = []

    def _record(self, event: str, **fields: Any) -> None:
        try:
            _append_line(self.journal, {"schema": MONITOR_JOURNAL_SCHEMA, "event": event,
                                        "at": stamp(), **fields})
        except OSError as error:
            self.errors.append(_error_text(error))

    def start(self) -> bool:
        self.last_attempt = time.monotonic()
        try:
            self.argv = [str(item) for item in self.argv_factory()]
            with open(self.night_dir / "monitor.stdout.log", "ab") as out, \
                    open(self.night_dir / "monitor.stderr.log", "ab") as err:
                process = self.popen(self.argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                     start_new_session=True, close_fds=True)
        except Exception as error:  # noqa: BLE001 - recorded; the chain is never held for it
            self.start_failures += 1
            self.consecutive_failures += 1
            self._record("start_failed", argv=self.argv, error=_error_text(error))
            if self.down_since is None:
                self.down_since = stamp()
            return False
        self.process = process
        self.starts += 1
        self.consecutive_failures = 0
        start_time = None
        if self.identity is not None:
            try:
                observed = self.identity(process.pid)
                start_time = getattr(observed, "start_time", None)
            except Exception:  # noqa: BLE001
                start_time = None
        now = stamp()
        if self.down_since is not None:
            self.gaps.append({"down_from": self.down_since, "up_at": now})
            self._record("restart", pid=process.pid, pgid=process.pid, start_time=start_time,
                         argv=self.argv, gap={"down_from": self.down_since, "up_at": now})
            self.down_since = None
        else:
            self._record("start", pid=process.pid, pgid=process.pid, start_time=start_time, argv=self.argv)
        return True

    def poll(self) -> None:
        """One supervision pass: observe an exit, restart when the interval allows."""

        if self.stopped:
            return
        if self.process is not None:
            code = self.process.poll()
            if code is None:
                return
            self.exits.append({"pid": self.process.pid, "returncode": code, "at": stamp()})
            self._record("exit", pid=self.process.pid, returncode=code)
            self.process = None
            self.down_since = stamp()
        interval = (MONITOR_RESTART_BACKOFF_S if self.consecutive_failures >= MONITOR_BACKOFF_AFTER
                    else MONITOR_RESTART_INTERVAL_S)
        if time.monotonic() - self.last_attempt >= interval:
            self.start()

    def stop(self) -> dict[str, Any]:
        """TERM the group, KILL after a grace period, and census it; return the summary."""

        if self.stopped:
            return self.summary()
        self.stopped = True
        record: dict[str, Any] = {"requested": stamp(), "was_running": False}
        process = self.process
        if process is not None and process.poll() is None:
            record["was_running"] = True
            pgid = process.pid
            for number, grace in ((signal.SIGTERM, MONITOR_STOP_GRACE_S), (signal.SIGKILL, MONITOR_STOP_GRACE_S)):
                try:
                    os.killpg(pgid, number)
                except (ProcessLookupError, PermissionError):
                    pass
                try:
                    process.wait(timeout=grace)
                    break
                except subprocess.TimeoutExpired:
                    record["escalated_to_kill"] = True
            record["returncode"] = process.poll()
            if self.group_census is not None:
                try:
                    absent, census = self.group_census(pgid, 1.0)
                except Exception as error:  # noqa: BLE001
                    absent, census = False, [_error_text(error)]
                if not absent:
                    try:
                        os.killpg(pgid, signal.SIGKILL)
                    except (ProcessLookupError, PermissionError):
                        pass
                    try:
                        absent, census = self.group_census(pgid, 1.0)
                    except Exception as error:  # noqa: BLE001
                        absent, census = False, [_error_text(error)]
                record.update(group_absent=absent, group_census=census)
        elif process is not None:
            record["returncode"] = process.poll()
            self._record("exit", pid=process.pid, returncode=record["returncode"])
        record["proven_stopped"] = (not record["was_running"]) or record.get("group_absent", record.get("returncode") is not None)
        self.stop_record = record
        self._record("stop", **record)
        return self.summary()

    def summary(self) -> dict[str, Any]:
        return {"schema": MONITOR_JOURNAL_SCHEMA, "argv": self.argv, "starts": self.starts,
                "restarts": max(0, self.starts - 1), "start_failures": self.start_failures,
                "exits": self.exits, "gaps": self.gaps, "stop": self.stop_record,
                "journal": MONITOR_JOURNAL, "errors": self.errors}


class DiskFloor:
    """Free space on the window's write volumes, read every ``DISK_CHECK_INTERVAL_S``."""

    def __init__(self, volumes: Sequence[Path], low_bytes: int, free_bytes: Callable[[Path], int],
                 *, marker: Path | None = None) -> None:
        self.volumes = [Path(item) for item in volumes]
        self.low_bytes = int(low_bytes)
        self.free_bytes = free_bytes
        self.marker = marker
        self.next_check = 0.0
        self.readings: list[dict[str, Any]] = []
        self.errors: list[str] = []

    def check(self) -> dict[str, Any] | None:
        """Every pass: the monitor's ``disk.low`` marker; every 60 s: a direct statvfs."""

        if self.marker is not None and self.marker.exists():
            try:
                low = json.loads(self.marker.read_text(encoding="utf-8")).get("low") or [{}]
            except (OSError, ValueError, AttributeError):
                low = [{}]
            first = low[0] if isinstance(low, list) and low and isinstance(low[0], Mapping) else {}
            reading = {"volume": str(first.get("path", "monitor disk.low marker")),
                       "free_bytes": first.get("free_bytes"), "low_bytes": self.low_bytes,
                       "source": str(self.marker), "at": stamp()}
            self.readings.append(reading)
            return reading
        now = time.monotonic()
        if now < self.next_check:
            return None
        self.next_check = now + DISK_CHECK_INTERVAL_S
        for volume in self.volumes:
            try:
                free = int(self.free_bytes(volume))
            except Exception as error:  # noqa: BLE001 - an unmeasured disk never stops the chain
                self.errors.append(f"{volume}: {_error_text(error)}")
                continue
            if free < self.low_bytes:
                reading = {"volume": str(volume), "free_bytes": free, "low_bytes": self.low_bytes, "at": stamp()}
                self.readings.append(reading)
                return reading
        return None


# --------------------------------------------------------------------------
# The executed-file inventory


def executed_inventory(*, measurement_root: Path, driver_root: Path | None, pack_root: Path,
                       chain_path: Path, git: Callable[[Path, Sequence[str]], bytes]) -> dict[str, Any]:
    """SHA-256 of the tracked files under ``joulewise/``, ``scripts/`` and the pack,
    plus the chain bytes, ``git rev-parse HEAD`` and ``git status --porcelain``.

    Local reads only; every failure is recorded in place of its value.
    """

    def checkout(root: Path, paths: Sequence[str]) -> dict[str, Any]:
        entry: dict[str, Any] = {"root": str(root), "head": None, "status_porcelain": None,
                                 "status_clean": None, "files": {}, "errors": []}
        try:
            entry["head"] = git(root, ["rev-parse", "HEAD"]).decode("utf-8", "replace").strip()
        except Exception as error:  # noqa: BLE001
            entry["errors"].append("head: " + _error_text(error))
        try:
            status = git(root, ["status", "--porcelain=v1", "--untracked-files=all"]).decode("utf-8", "replace")
            entry.update(status_porcelain=status, status_clean=status.strip() == "")
        except Exception as error:  # noqa: BLE001
            entry["errors"].append("status: " + _error_text(error))
        try:
            listed = git(root, ["ls-files", "-z", "--", *paths]).split(b"\0")
            for item in listed:
                if not item:
                    continue
                relative = item.decode("utf-8", "replace")
                entry["files"][relative] = _sha256_file(root / relative)
        except Exception as error:  # noqa: BLE001
            entry["errors"].append("ls-files: " + _error_text(error))
        canonical = json.dumps(entry["files"], sort_keys=True, separators=(",", ":")).encode("utf-8")
        entry.update(file_count=len(entry["files"]), files_sha256=hashlib.sha256(canonical).hexdigest())
        return entry

    measurement_root = Path(measurement_root)
    try:
        pack_relative = Path(pack_root).relative_to(measurement_root).as_posix()
    except ValueError:
        pack_relative = None
    paths = ["joulewise", "scripts"] + ([pack_relative] if pack_relative else [])
    record = {"schema": INVENTORY_SCHEMA, "taken": stamp(),
              "measurement_checkout": checkout(measurement_root, paths),
              "chain": {"path": str(chain_path), "sha256": _sha256_file(chain_path)},
              "pack_root": str(pack_root)}
    if driver_root is not None and Path(driver_root).resolve() != measurement_root.resolve():
        record["driver_checkout"] = checkout(Path(driver_root), ["joulewise", "scripts"])
    return record


# --------------------------------------------------------------------------
# One window


class _Window:
    """State of one HAZARD_PACK driver run; every record it writes is in custody."""

    def __init__(self, rt: Any, plan: Any, plan_path: Path, probes: Any, seams: Seams,
                 *, record_root: Path | None = None, dry_arm: bool = False) -> None:
        self.rt = rt
        self.plan = plan
        self.plan_path = Path(plan_path)
        self.probes = probes
        self.seams = seams
        self.window = plan.hazard_window
        self.custody = Path(plan.custody_root)
        self.night = self.custody / "night"
        self.record_root = record_root if record_root is not None else self.custody / "hazards"
        self.dry_arm = dry_arm
        self.flags: list[str] = []
        self.diagnostics: list[str] = []
        self.off_calls: list[dict[str, Any]] = []
        self.collector_calls: list[dict[str, Any]] = []
        self.boot: str | None = None

    # --- records ---------------------------------------------------------

    def note(self, message: str) -> None:
        self.diagnostics.append(message)
        if not self.dry_arm:
            try:
                self.rt._append_log(self.custody, "hazard: " + message)
            except OSError:
                pass

    def flag(self, code: str, family: str, klass: str, *, stage: str = "arm", observed: Any = None,
             expected: Any = None, detail: str = "", legacy_site: str | None = None,
             legacy_code: str | None = None, evidence: Sequence[Mapping[str, str]] = (),
             interval: Mapping[str, Any] | None = None) -> None:
        if self.dry_arm:
            return  # a desk control records into its own directory, never into window flags
        fields = {
            "code": code, "family": family, "klass": klass,
            "scope": {"level": "window", "plan_id": self.plan.plan_id, "attempt": self.window["attempt"],
                      "stage_id": None, "run_id": None, "bundle_id": None},
            "source": {"stage": stage, "collector": "b5.driver", "legacy_site": legacy_site,
                       "legacy_code": legacy_code},
            "observed": observed, "expected": expected, "evidence": list(evidence), "detail": detail,
        }
        if interval is not None:
            fields["interval"] = dict(interval)
        try:
            self.seams.emit_flag(self.custody, fields)
            self.flags.append(code)
        except Exception as error:  # noqa: BLE001 - a flag is a record; it never stops collection
            self.note(f"flag {code} could not be written: {_error_text(error)}")

    def census_record(self, probe: Any, refusal: Any) -> dict[str, Any]:
        record = self.rt._census_record(probe, refusal)
        record["clean"] = refusal is None and probe.exit_code == 1 and probe.stdout == ""
        return record

    # --- arm hooks -------------------------------------------------------

    def network_time_off(self) -> dict[str, Any]:
        """Network time OFF, run as an action: the output is recorded, never read for wording."""

        try:
            result = self.seams.run_command(NETWORK_TIME_OFF_ARGV, OFF_TIMEOUT_S)
            record = result.record()
        except Exception as error:  # noqa: BLE001
            record = {"argv": list(NETWORK_TIME_OFF_ARGV), "error": _error_text(error), "at": stamp()}
        return self.record_network_time_off(record, ran_by="driver")

    def record_network_time_off(self, record: dict[str, Any], *, ran_by: str) -> dict[str, Any]:
        record = {"schema": NETWORK_TIME_ACTION_SCHEMA, "call": len(self.off_calls) + 1, "ran_by": ran_by, **record}
        self.off_calls.append(record)
        try:
            path = _create_once((self.record_root.parent if self.dry_arm else self.night) / NETWORK_TIME_ACTION, record)
            record["record_path"] = str(path)
        except OSError as error:
            self.note(f"network time OFF record could not be written: {_error_text(error)}")
        self.flag("network_time.off_output", "DIAGNOSTIC", "REPRESENTATION",
                  observed={"returncode": record.get("returncode"), "stdout": record.get("stdout"),
                            "stderr": record.get("stderr"), "timed_out": record.get("timed_out"),
                            "error": record.get("error")},
                  detail="network time OFF ran as an arm action; its output is recorded only",
                  legacy_site="joulewise/network_time_off.py", legacy_code="network_time_off_admission")
        return record

    def record_only_collectors(self) -> dict[str, Any]:
        """The L4 arm collectors in a subprocess with a timeout; never raises, never decides."""

        custody = self.record_root.parent if self.dry_arm else self.custody
        try:
            argv = list(self.seams.collectors_argv(CollectorRequest(self.plan, self.plan_path, custody, "arm")))
            result = self.seams.run_command(argv, COLLECTOR_TIMEOUT_S)
            record = result.record()
            if result.timed_out or result.error or result.returncode != 0:
                record["collector_error"] = (result.error or ("timed out" if result.timed_out
                                                              else f"exit {result.returncode}"))
        except Exception as error:  # noqa: BLE001
            record = {"collector_error": _error_text(error), "at": stamp()}
        return self.record_collectors(record, ran_by="driver")

    def record_collectors(self, record: dict[str, Any], *, ran_by: str) -> dict[str, Any]:
        record = {"schema": COLLECTORS_SCHEMA, "call": len(self.collector_calls) + 1, "ran_by": ran_by, **record}
        if ran_by == "arm":
            errors = [item.get("error") or ("timed out" if item.get("timed_out") else
                                            f"exit {item.get('returncode')}" if item.get("returncode") else None)
                      for item in record.get("results", []) if isinstance(item, Mapping)]
            if any(errors):
                record["collector_error"] = "; ".join(str(item) for item in errors if item)
        self.collector_calls.append(record)
        try:
            target = (self.record_root.parent if self.dry_arm else self.night) / COLLECTORS_RECORD
            record["record_path"] = str(_create_once(target, record))
        except OSError as error:
            self.note(f"collector record could not be written: {_error_text(error)}")
        return record

    def agent_census(self) -> dict[str, Any]:
        probe, refusal = self.rt.agent_census(self.probes)
        if not self.dry_arm:
            try:
                self.rt._append_census(self.night / "censuses.jsonl", probe, refusal)
            except OSError as error:
                self.note(f"census journal append failed: {_error_text(error)}")
        return self.census_record(probe, refusal)

    def _guard(self, hook: Callable[[], dict[str, Any]], label: str) -> Callable[[], dict[str, Any]]:
        def guarded() -> dict[str, Any]:
            try:
                return hook()
            except Exception as error:  # noqa: BLE001
                self.note(f"{label} hook raised {_error_text(error)}")
                return {"error": _error_text(error)}
        return guarded

    # --- arm -------------------------------------------------------------

    def run_arm(self, census: Mapping[str, Any]) -> dict[str, Any]:
        self.record_root.mkdir(parents=True, exist_ok=True)
        thresholds = self.window["thresholds"]
        try:
            record_only_argv = tuple(str(item) for item in self.seams.collectors_argv(
                CollectorRequest(self.plan, self.plan_path, self.record_root.parent, "arm")))
        except Exception as error:  # noqa: BLE001 - the collectors are records; the arm goes on
            self.note(f"record-only collector command unavailable: {_error_text(error)}")
            record_only_argv = ()
        context = ArmContext(
            plan=self.plan, plan_path=self.plan_path, custody_root=self.custody, night_dir=self.night,
            record_root=self.record_root, hazard_window=self.window, thresholds=thresholds,
            t_stream_max_s=float(self.window["T_stream_max_s"]), planned_bytes=int(self.window["planned_bytes"]),
            disk_volumes=tuple(Path(item) for item in self.window["disk_volumes"]),
            disk_targets=tuple(disk_targets(self.window, arm=True)),
            measurement_tree_pids=(os.getpid(),), census=dict(census),
            arm_deadline_epoch_s=float(self.plan.t0_epoch_s) + float(self.window["t0_stage_cap_s"]),
            dry_arm=self.dry_arm, record_only_argv=record_only_argv,
            network_time_off=self._guard(self.network_time_off, "network time OFF"),
            record_only_collectors=self._guard(self.record_only_collectors, "record-only collectors"),
            agent_census=self._guard(self.agent_census, "agent census"))
        started = stamp()
        outcome: dict[str, Any] = {}

        def target() -> None:
            try:
                outcome["raw"] = self.seams.arm(context)
            except BaseException as error:  # noqa: BLE001 - UNMEASURED, never a crash
                outcome["error"] = _error_text(error)

        thread = threading.Thread(target=target, name="hazard-arm", daemon=True)
        thread.start()
        thread.join(float(self.window["t0_stage_cap_s"]) + ARM_RETURN_GRACE_S)
        ended = stamp()
        if thread.is_alive():
            decision = normalize_decision({"go": False})
            decision["reasons"].append("the hazard arm did not return within the T-0 stage cap plus grace")
            decision["arm_error"] = "timeout"
        elif "error" in outcome:
            decision = normalize_decision({"go": False})
            decision["reasons"].append("the hazard arm raised: " + outcome["error"])
            decision["arm_error"] = outcome["error"]
        else:
            decision = normalize_decision(outcome.get("raw"))
        go_after_cap = ended["wall_s"] > context.arm_deadline_epoch_s
        # An arm that ran OFF and the collectors itself hands back their records.
        if isinstance(decision.get("network_time_off"), Mapping) and not self.off_calls:
            self.record_network_time_off(dict(decision["network_time_off"]), ran_by="arm")
        if isinstance(decision.get("record_only"), list) and not self.collector_calls:
            self.record_collectors({"results": decision["record_only"]}, ran_by="arm")
        if decision["go"]:
            # Both hooks run before any launch even if the arm layer skipped them.
            if not self.off_calls:
                self.note("the arm returned GO without running network time OFF; the driver ran it")
                self.network_time_off()
            if not self.collector_calls:
                self.note("the arm returned GO without running the record-only collectors; the driver ran them")
                self.record_only_collectors()
        record = {
            "schema": ARM_DECISION_SCHEMA, "plan_id": self.plan.plan_id, "dry_arm": self.dry_arm,
            "go": decision["go"], "verdicts": decision["verdicts"], "not_pass": decision["not_pass"],
            "reasons": decision["reasons"], "arm_error": decision.get("arm_error"),
            "arm_record": {"path": decision["record_path"],
                           "sha256": _sha256_file(Path(decision["record_path"])) if decision["record_path"] else None},
            "census": dict(census), "started": started, "ended": ended,
            "arm_deadline_epoch_s": context.arm_deadline_epoch_s, "go_after_t0_stage_cap": go_after_cap,
            "network_time_off_calls": len(self.off_calls), "collector_calls": len(self.collector_calls),
        }
        decision["record"] = record
        return decision


def _report(plan: Any, base_exit_code: int, facts: Mapping[str, Any], diagnostics: Sequence[str]) -> dict[str, Any]:
    return {"facts": {"plan_id": plan.plan_id, "receipt_class": plan.receipt_class, **facts},
            "diagnostics": list(diagnostics), "result_unavailable": False,
            "base_exit_code": base_exit_code, "prepared": False}


def run_hazard_night(rt: Any, plan_path: Path, plan: Any, probes: Any, initial_census: tuple[Any, Any], *,
                     started_epoch_s: float, started_monotonic_ns: int, courier_bin: Path | None,
                     seams: Seams) -> int:
    """Drive one HAZARD_PACK window from its launchd job; return the driver exit code."""

    window = _Window(rt, plan, plan_path, probes, seams)
    custody, night = window.custody, window.night
    courier, courier_error, substitution = rt._resolve_courier_bin(courier_bin)
    rt._record_courier_substitution(custody, substitution)
    if courier is None:
        window.note(f"courier unavailable ({courier_error}); collection proceeds, reporting is durable-record only")
    deadman = rt.deadman_epoch(plan)
    hazard: dict[str, Any] = {"schema": HAZARD_RESULT_SCHEMA, "plan_id": plan.plan_id,
                              "receipt_class": plan.receipt_class, "attempt": plan.hazard_window["attempt"],
                              "pack_id": plan.hazard_window["pack"]["pack_id"], "started": stamp()}

    def refuse(stage: str, reason: str, detail: str, evidence: Any) -> int:
        hazard.update(verdict="REFUSED", stage_reached=stage, refusal={"reason": reason, "detail": detail},
                      flags_emitted=list(window.flags), diagnostics=list(window.diagnostics), ended=stamp())
        try:
            _create_once(night / HAZARD_RESULT, hazard)
        except OSError as error:
            window.note(f"hazard result could not be written: {_error_text(error)}")
        rt._write_standard_refusal_result(custody, night, plan, reason, detail, started_epoch_s,
                                          started_monotonic_ns, evidence=evidence)
        rt._append_log(custody, f"hazard window refused at {stage}: {reason}")
        report = _report(plan, rt.EXIT_REFUSED, {"verdict": "REFUSED", "stage_reached": stage,
                                                 "refusal_reason": reason, "detail": detail,
                                                 "arm_verdicts": hazard.get("arm", {}).get("verdicts")},
                         window.diagnostics)
        return rt._finish_reporting(custody, night, plan, rt.EXIT_REFUSED, courier,
                                    courier_error=courier_error, deadman_epoch_s=deadman,
                                    courier_bin_substitution=substitution, report=report,
                                    allow_courier=courier is not None)

    # 1. Agent census: the driver's first probe, taken before the plan was read.
    probe, census_refusal = initial_census
    census = window.census_record(probe, census_refusal)
    hazard["census"] = {"clean": census["clean"], "exit_code": probe.exit_code}
    if not census["clean"]:
        reason = census_refusal.reason if census_refusal is not None else rt._CODES["probe_error"]
        detail = census_refusal.detail if census_refusal is not None else "agent census stdout must be empty"
        return refuse("census", reason, detail, census)

    # 2. The hazard arm.
    try:
        decision = window.run_arm(census)
    except Exception as error:  # noqa: BLE001 - an arm the driver cannot run is UNMEASURED
        decision = normalize_decision({"go": False})
        decision["reasons"].append("the driver could not run the hazard arm: " + _error_text(error))
        decision["record"] = {"schema": ARM_DECISION_SCHEMA, "plan_id": plan.plan_id, "go": False,
                              "verdicts": decision["verdicts"], "reasons": decision["reasons"]}
    try:
        _create_once(night / ARM_DECISION, decision["record"])
    except OSError as error:
        window.note(f"arm decision record could not be written: {_error_text(error)}")
    hazard["arm"] = {"go": decision["go"], "verdicts": decision["verdicts"], "reasons": decision["reasons"],
                     "record_path": decision["record_path"]}
    if not decision["go"]:
        detail = ("hazard arm did not return GO; non-PASS: "
                  + (", ".join(f"{name}={decision['verdicts'][name]}" for name in decision["not_pass"]) or "none")
                  + ("; " + "; ".join(decision["reasons"]) if decision["reasons"] else ""))
        return refuse("arm", REFUSED_HAZARD, detail,
                      {"verdicts": decision["verdicts"], "reasons": decision["reasons"],
                       "arm_decision": f"night/{ARM_DECISION}"})

    # Final census immediately before any publication or launch.
    final = window.agent_census()
    hazard["final_census"] = {"clean": final["clean"], "exit_code": final.get("exit_code")}
    if not final["clean"]:
        refusal = final.get("refusal") or {}
        return refuse("final_census", refusal.get("reason") or rt._CODES["probe_error"],
                      refusal.get("detail") or "final agent census stdout must be empty", final)

    # The chain's bytes against its sidecar: a flag, never a refusal.
    chain_path = Path(plan.chain_path)
    chain_sha256 = _sha256_file(chain_path)
    if chain_sha256 is None:
        return refuse("launch", rt._CODES["chain_launch_failed"], "the chain file is missing or unreadable",
                      {"chain_path": str(chain_path)})
    try:
        sidecar_text = Path(plan.chain_sha256_path).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        sidecar_text = ""
    expected = rt._sidecar_digest(sidecar_text, chain_path.name)
    hazard["chain"] = {"sha256": chain_sha256, "sidecar_sha256": expected, "matches_sidecar": chain_sha256 == expected}
    if chain_sha256 != expected:
        window.flag("code.executed_differs_from_sealed", "CODE_IDENTITY", "NUMBER",
                    observed={"chain_sha256": chain_sha256}, expected={"sidecar_sha256": expected},
                    detail="the chain bytes differ from their arm-time SHA-256 sidecar; the chain ran anyway",
                    legacy_site="scripts/run_night.py:4022", legacy_code="night_chain_digest_mismatch",
                    evidence=[{"path": os.path.relpath(chain_path, custody) if chain_path.is_relative_to(custody)
                               else str(chain_path), "sha256": chain_sha256}])

    # 3. Launch lineage into both runs roots: a record; its failure is a flag.
    if window.boot is None:
        window.boot = seams.boot_session_uuid()
    roots = plan.hazard_window["runs_roots"]
    lineage_record: dict[str, Any] = {"schema": LINEAGE_SCHEMA, "requested": stamp()}
    try:
        published = seams.publish_lineage(LineageRequest(
            plan=plan, plan_path=Path(plan_path), custody_root=custody, night_dir=night,
            hazard_window=plan.hazard_window, claim_runs_root=Path(roots["claim"]),
            bound_runs_root=Path(roots["bound"]),
            arm_record_path=Path(decision["record_path"]) if decision["record_path"] else None,
            arm_decision_path=night / ARM_DECISION if (night / ARM_DECISION).exists() else None,
            boot_session_uuid=window.boot))
        lineage_record.update(published=True, result=json.loads(json.dumps(published, default=str)))
    except Exception as error:  # noqa: BLE001
        lineage_record.update(published=False, error=_error_text(error))
        window.flag("records.lineage_formality", "RECORDS", "REPRESENTATION",
                    observed={"error": _error_text(error)},
                    detail="the hazard-window lineage could not be published before launch; the chain ran anyway")
    lineage_record["ended"] = stamp()
    try:
        _create_once(night / LINEAGE_RECORD, lineage_record)
    except OSError as error:
        window.note(f"lineage record could not be written: {_error_text(error)}")
    hazard["lineage"] = {"published": lineage_record["published"], "error": lineage_record.get("error")}

    # 4. The executed-file inventory.
    try:
        inventory = executed_inventory(
            measurement_root=Path(plan.measurement_root), driver_root=getattr(rt, "REPO_ROOT", None),
            pack_root=Path(plan.hazard_window["pack"]["pack_root"]), chain_path=chain_path, git=seams.git)
        path = _create_once(night / INVENTORY_RECORD, inventory)
        checkout = inventory["measurement_checkout"]
        hazard["inventory"] = {"path": str(path), "sha256": _sha256_file(path), "head": checkout["head"],
                               "status_clean": checkout["status_clean"], "file_count": checkout["file_count"],
                               "errors": checkout["errors"]}
    except Exception as error:  # noqa: BLE001 - a record; never a refusal
        window.note(f"executed-file inventory failed: {_error_text(error)}")
        hazard["inventory"] = {"error": _error_text(error)}

    # 5. The monitor.
    monitor_request = MonitorRequest(plan, Path(plan_path), custody, night, os.getpid())
    monitor = MonitorSupervisor(
        lambda: seams.monitor_argv(monitor_request),
        night_dir=night, popen=seams.popen, group_census=getattr(rt, "_group_census", None),
        identity=getattr(rt, "observe_identity", None))
    if not monitor.start():
        window.note("the hazard monitor did not start; supervision keeps retrying while the chain runs")
    thresholds = plan.hazard_window["thresholds"].get("disk", {})
    low = thresholds.get("low_bytes", DISK_LOW_BYTES_DEFAULT) if isinstance(thresholds, Mapping) else DISK_LOW_BYTES_DEFAULT
    disk = DiskFloor([Path(roots["claim"]), Path(roots["bound"]), custody], int(low), seams.disk_free_bytes,
                     marker=custody / "hazards" / "monitor" / "disk.low")

    def supervise() -> dict[str, Any] | None:
        monitor.poll()
        reading = disk.check()
        if reading is None:
            return None
        window.flag("disk.low", "DIAGNOSTIC", "PHYSICS", stage="window",
                    observed={"volume": reading["volume"], "free_bytes": reading["free_bytes"]},
                    expected={"low_bytes": reading["low_bytes"]},
                    detail="free space fell under the in-window floor; the driver stopped the chain")
        return rt._refusal_mapping(
            STOPPED_DISK_LOW,
            f"free space {reading['free_bytes']} B on {reading['volume']} is under the "
            f"{reading['low_bytes']} B in-window floor; the driver stopped the chain", reading)

    # 6. The chain, once.
    claim = rt._claim_chain_start(night)
    if claim is None:
        hazard["monitor"] = monitor.stop()
        return refuse("launch", rt._CODES["chain_already_started"],
                      "chain.started already exists; the night chain is once-only", None)
    exit_code: int | None = None
    abort: dict[str, Any] | None = None
    census_count, census_hits, proven = 0, [], False
    try:
        exit_code, abort, census_count, census_hits, proven = rt._run_chain_once(
            chain_path, plan, probes, night, claim, command=["/bin/zsh", "-f", str(chain_path)],
            abort_on_census=True, supervise=supervise, census_group_on_exit=True)
    except Exception as error:  # noqa: BLE001 - recorded; the terminal record must still be written
        window.note(f"chain supervision raised {_error_text(error)}")
        abort = rt._refusal_mapping(rt._CODES["chain_alive"],
                                    f"the driver's chain supervision raised {_error_text(error)}", None)
        proven = False
    started = (night / "chain.started").exists()
    hazard["chain"].update(exit_code=exit_code, started=started, termination_proven=proven,
                           stages=[{"stage_id": row.get("stage_id"), "kind": row.get("kind"), "rc": row.get("rc")}
                                   for row in b5_chain.stage_journal(night)])
    # The NEG-8 manifest the derivation read: a locator for the harvest, which
    # needs the custodied bytes when the copy was pruned (chain DEVIATIONS).
    try:
        hazard["neg8_corpus"] = b5_chain.neg8_corpus_record(night)
    except Exception as error:  # noqa: BLE001 - a record; never a refusal
        hazard["neg8_corpus"] = {"errors": [_error_text(error)]}

    # 7. G10, with the monitor still journaling, only after a natural exit proven gone.
    want_g10 = bool(plan.hazard_window.get("g10"))
    if want_g10 and started and proven and abort is None:
        hazard["g10"] = _run_g10(window, night, float(plan.hazard_window["T_stream_max_s"]))
    else:
        hazard["g10"] = {"ran": False, "requested": want_g10,
                         "reason": ("not requested" if not want_g10 else
                                    "chain not started" if not started else
                                    "chain termination not proven" if not proven else
                                    "chain stopped by the driver")}

    # 8. The monitor stops only once the chain's process group is proven gone;
    # otherwise it keeps journaling and the dead-man stops it after its own proof.
    if proven or not started:
        hazard["monitor"] = monitor.stop()
    else:
        window.note("chain termination not proven: the hazard monitor is left running for the dead-man")
        hazard["monitor"] = {**monitor.summary(), "left_running": True}
    hazard["disk_floor"] = {"low_bytes": disk.low_bytes, "stops": disk.readings, "errors": disk.errors}
    if abort is not None:
        reason = str(abort["reason"])
        if "document" not in abort:
            rt._write_driver_refusal(night / "refusal.json", plan, reason, str(abort["detail"]), abort["evidence"])
        refused = (reason in {rt._CODES["chain_launch_failed"], rt._CODES["chain_already_started"]}
                   or not proven or not started)
        verdict = "REFUSED" if refused else "ABORTED"
        base_exit = rt.EXIT_REFUSED if refused else rt.EXIT_ABORTED
        aborted_reason: str | None = reason
    else:
        verdict = "GO"
        base_exit = rt.EXIT_GO if exit_code == 0 else rt.EXIT_CHAIN_FAILED
        aborted_reason = None
    stages = hazard["chain"]["stages"]
    hazard.update(verdict=verdict, stage_reached="chain", aborted_reason=aborted_reason,
                  flags_emitted=list(window.flags), diagnostics=list(window.diagnostics), ended=stamp())
    try:
        _create_once(night / HAZARD_RESULT, hazard)
    except OSError as error:
        window.note(f"hazard result could not be written: {_error_text(error)}")
    report = _report(plan, base_exit, {
        "verdict": verdict, "aborted_reason": aborted_reason, "chain_exit_code": exit_code,
        "termination_proven": proven, "census_count": census_count, "arm_verdicts": decision["verdicts"],
        "stages_total": len(stages), "stages_nonzero": sum(1 for row in stages if row.get("rc") not in (0, None)),
        "chain_stop": next((row.get("kind") for row in stages if row.get("stage_id") == "chain.stop"), None),
        "g10_ran": hazard["g10"].get("ran"), "g10_returncode": hazard["g10"].get("returncode"),
        "monitor_restarts": hazard["monitor"]["restarts"], "flags": sorted(set(window.flags))},
        window.diagnostics)
    try:
        rt._write_result(custody, night, plan, verdict, exit_code, aborted_reason, started_epoch_s,
                         started_monotonic_ns, chain_sha256, census_count, census_hits, None)
    except Exception as error:  # noqa: BLE001
        report["result_unavailable"] = True
        report["diagnostics"].append(f"result.json could not be written: {_error_text(error)}")
        report["base_exit_code"] = rt.EXIT_REFUSED
    rt._append_log(custody, f"hazard window result verdict={verdict}")
    if not proven:
        return rt._finish_reporting(custody, night, plan, report["base_exit_code"], courier,
                                    courier_error="chain termination was not proven", allow_courier=False,
                                    report=report, courier_bin_substitution=substitution)
    return rt._finish_reporting(custody, night, plan, report["base_exit_code"], courier,
                                courier_error=courier_error, deadman_epoch_s=deadman, report=report,
                                courier_bin_substitution=substitution, allow_courier=courier is not None)


def _run_g10(window: _Window, night: Path, t_stream_max_s: float) -> dict[str, Any]:
    """Run G10 with its fixed argv in its own group; bound it; record the driver's view."""

    record: dict[str, Any] = {"schema": G10_DRIVER_SCHEMA, "ran": True, "started": stamp()}
    try:
        argv = [str(item) for item in window.seams.g10_argv(night, t_stream_max_s)]
        record["argv"] = argv
        with open(night / "g10.stdout.log", "ab") as out, open(night / "g10.stderr.log", "ab") as err:
            process = window.seams.popen(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                         start_new_session=True, close_fds=True)
        try:
            record["returncode"] = process.wait(timeout=G10_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            record["timed_out"] = True
            for number, grace in ((signal.SIGTERM, G10_TERM_GRACE_S), (signal.SIGKILL, 10.0)):
                try:
                    os.killpg(process.pid, number)
                except (ProcessLookupError, PermissionError):
                    pass
                try:
                    record["returncode"] = process.wait(timeout=grace)
                    break
                except subprocess.TimeoutExpired:
                    continue
    except Exception as error:  # noqa: BLE001 - G10 is a diagnostic; it never changes the window
        record["error"] = _error_text(error)
    record["ended"] = stamp()
    g10 = night / G10_RECORD
    record["g10_record"] = {"path": str(g10), "sha256": _sha256_file(g10)}
    try:
        result = json.loads(g10.read_text(encoding="utf-8")).get("result")
        record["result"] = result if isinstance(result, str) else None
    except (OSError, ValueError, AttributeError):
        record["result"] = None
    try:
        _create_once(night / G10_DRIVER_RECORD, record)
    except OSError as error:
        window.note(f"G10 driver record could not be written: {_error_text(error)}")
    return record


def dry_arm(rt: Any, plan_path: Path, plan: Any, probes: Any, initial_census: tuple[Any, Any], *,
            seams: Seams) -> int:
    """The desk dry-arm negative control: census, then the arm, never a launch.

    It writes only under ``<custody>/dry-arm/dry-arm-NN/``; the night's
    write-once records, the runs roots and the window flags are never touched.
    While an agent is alive (always, at the desk) it refuses at the census
    before any action: no OFF, no collector, no probe.
    """

    base = Path(plan.custody_root) / "dry-arm"
    base.mkdir(parents=True, exist_ok=True)
    index = 1
    while True:
        directory = base / f"dry-arm-{index:02d}"
        try:
            directory.mkdir()
            break
        except FileExistsError:
            index += 1
    window = _Window(rt, plan, plan_path, probes, seams, record_root=directory / "hazards", dry_arm=True)
    probe, refusal = initial_census
    census = window.census_record(probe, refusal)
    record: dict[str, Any] = {"schema": DRY_ARM_SCHEMA, "plan_id": plan.plan_id, "census": census,
                              "started": stamp(), "launched": False}
    if not census["clean"]:
        record.update(verdict="REFUSED", stage="census", arm_ran=False, network_time_off_calls=0,
                      collector_calls=0,
                      reason=(refusal.reason if refusal is not None else rt._CODES["probe_error"]),
                      detail=(refusal.detail if refusal is not None else "agent census stdout must be empty"))
    else:
        decision = window.run_arm(census)
        record.update(verdict="GO" if decision["go"] else "REFUSED", stage="arm", arm_ran=True,
                      arm=decision["record"], network_time_off_calls=len(window.off_calls),
                      collector_calls=len(window.collector_calls))
    record["ended"] = stamp()
    path = _create_once(directory / "dry-arm.json", record)
    sys.stdout.write(json.dumps({"verdict": record["verdict"], "stage": record["stage"],
                                 "record": str(path)}, sort_keys=True) + "\n")
    return 0 if record["verdict"] == "GO" else rt.EXIT_REFUSED


def reap_orphan_monitor(night_dir: Path, *, identity: Callable[[int], Any] | None = None) -> dict[str, Any] | None:
    """Dead-man helper: stop a monitor group the driver started and never proved stopped.

    The group is signalled only when its leader is still the process the
    journal recorded (same start time), so a reused pid is never touched.
    """

    try:
        lines = (Path(night_dir) / MONITOR_JOURNAL).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return None
    last_start, stopped = None, False
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("event") in {"start", "restart"}:
            last_start, stopped = event, False
        elif event.get("event") == "stop" and event.get("proven_stopped"):
            stopped = True
    if last_start is None or stopped:
        return None
    pgid = last_start.get("pgid")
    if type(pgid) is not int or pgid <= 1:
        return None
    if identity is not None and last_start.get("start_time"):
        observed = identity(pgid)
        if getattr(observed, "state", None) != "LIVE" or getattr(observed, "start_time", None) != last_start["start_time"]:
            return {"pgid": pgid, "signalled": False, "reason": "recorded monitor is not the live process"}
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return {"pgid": pgid, "signalled": False, "reason": "group already gone"}
    except PermissionError:
        return {"pgid": pgid, "signalled": False, "reason": "permission denied"}
    return {"pgid": pgid, "signalled": True}
