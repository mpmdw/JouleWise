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
   under ``taskpolicy -b``; a one-second supervision pass restarts it if it dies.
   Then the KM003C wall meter (``scripts/km003c_monitor.py``, plain QoS), a
   disclosed diagnostic supervised the same way except that its exit 0 (meter
   absent) is final; it never refuses or stops the window;
6. the chain, launched once through the driver's no-pack path
   (``_claim_chain_start`` / ``_run_chain_once`` / ``_WindowDeadline`` /
   ``_terminate_process_group``), with the in-chain agent census kept as an
   abort and a driver stop when free disk falls under the in-window floor;
7. G10 (``scripts/g10_clock_step_control.py``) when the plan asks for it, after
   the chain's process group is proven gone, with the monitor still journaling;
8. the monitor and meter stop (SIGTERM to each group, proven gone), no sooner
   than ``MONITOR_POST_CHAIN_HOLD_S`` after the chain returned, then the
   terminal records (``night/hazard_result.json``, ``night/result.json``) and
   the structure-only courier.

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
import re
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
# PLAN2 P2-DRV (gate prune round 2).
STOPPED_CENSUS_UNMEASURED = "night_stopped_census_unmeasured"
STOPPED_MONITOR_OUTAGE = "night_stopped_monitor_outage"
REFUSED_INSTRUMENT_NOT_SAMPLING = "night_refused_instrument_not_sampling"
# The one lineage refusal left is physics: the boot changed since the lineage
# was published, so monotonic clocks do not join (doctrine 2026-10-05).
REFUSED_BOOT_CHANGED = "night_refused_boot_changed"
REFUSED_LAUNCH_ABANDONED = "night_refused_launch_abandoned"
if {REFUSED_HAZARD, STOPPED_DISK_LOW, STOPPED_CENSUS_UNMEASURED, STOPPED_MONITOR_OUTAGE,
        REFUSED_INSTRUMENT_NOT_SAMPLING, REFUSED_BOOT_CHANGED,
        REFUSED_LAUNCH_ABANDONED} != set(night_gate.HAZARD_DRIVER_REASON_CODES):
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
# Cold pass N7: while G10 runs, the driver polls it this often and runs the
# same supervision pass as during the chain (monitor and meter restarts,
# outages, disk), instead of blocking in one wait for up to 25 minutes.
G10_POLL_S = 5.0
GIT_TIMEOUT_S = 60.0
# PLAN2 row 7: the in-window census. A probe that is neither clean (exit 1,
# empty stdout) nor a detection (any stdout) is unmeasured: retried, then a
# flag; this many unmeasured censuses in a row (about 2 min) stop the chain.
CENSUS_RETRIES = 3
CENSUS_RETRY_S = 1.0
CENSUS_UNMEASURED_STOP_AFTER = 4
# PLAN2 row 11: the monitor must journal before launch, and keep journaling.
MONITOR_READY_TRIES = 3
MONITOR_READY_TIMEOUT_S = 20.0
MONITOR_READY_POLL_S = 0.2
MONITOR_RAPID_EXIT_S = 30.0
MONITOR_OUTAGE_S = 600.0
MONITOR_LIVENESS_CHECK_S = 10.0
MONITOR_JOURNAL_DIR = ("hazards", "monitor")
# P3-DRV (mock rehearsal R3-5): the hazard monitor and the meter are stopped no
# sooner than this after the chain returns, so the 1 Hz SMC battery reads cover
# the end of the post capture (the battery join needs a read at most
# battery.SMC_MAX_GAP_S = 5 s after the span it judges).
MONITOR_POST_CHAIN_HOLD_S = 5.0
# The KM003C wall meter (scripts/km003c_monitor.py; WIRING.md): a disclosed
# diagnostic supervised like the monitor. It never refuses or stops a window.
METER_NAME = "meter"
METER_STREAM_DIR = ("hazards", "meter")
# PLAN2 row 9 (interim): one publication retry, then both locators re-read.
LINEAGE_RETRY_S = 5.0
# PLAN2 yield tripwire (section 2.2).
YIELD_STALL_S = 3600.0
YIELD_STALL_CHECK_S = 60.0
# Sol review F3: a stage is counted in the window only inside the settle that
# follows it (registered 60 s): its journal line must be at most this old, and
# the next in-chain stage must not be a capture. Otherwise it is counted at the
# terminal record, after the chain group is gone.
YIELD_COUNT_FRESH_S = 30.0
YIELD_PRE_BUNDLE_RUN = 3
CORPUS_MIN_VALID = 10
# A science stage's share of the analysis plan's 8-of-10 cell minimum.
SCIENCE_MIN_NUMERATOR, SCIENCE_MIN_DENOMINATOR = 4, 5

ARM_DECISION = "arm_decision.json"
HAZARD_RESULT = "hazard_result.json"
NETWORK_TIME_ACTION = "network_time_off.action.json"
COLLECTORS_RECORD = "arm_collectors.json"
INVENTORY_RECORD = "executed_inventory.json"
LINEAGE_RECORD = "lineage.json"
MONITOR_JOURNAL = "monitor_supervision.jsonl"
METER_JOURNAL = "meter_supervision.jsonl"
G10_RECORD = "g10.json"
G10_DRIVER_RECORD = "g10.driver.json"
DRIVER_FLAGS = "driver.jsonl"
YIELD_PLAN = "yield_plan.json"
STAGE_YIELD = "stage_yield.jsonl"
YIELD_ALERT = "yield_alert-{ordinal}.json"
LAUNCH_ABANDONED_MARKER = "launch_abandoned.json"
YIELD_PLAN_SCHEMA = "joulewise.b5_yield_plan.v1"
STAGE_YIELD_SCHEMA = "joulewise.b5_stage_yield.v1"
YIELD_ALERT_SCHEMA = "joulewise.b5_yield_alert.v1"
YIELD_SCHEMA = "joulewise.b5_window_yield.v1"


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
    """``kern.bootsessionuuid`` in the one canonical form members compare.

    This is ``window_lineage.current_boot_session_id`` itself (a lowercase
    canonical UUID, or None when unreadable), so the boot the driver publishes
    and the boot the pre-launch check reads are the members' own reading.
    sysctl prints the UUID in uppercase; a raw reading never equals the
    lineage's canonical id (cooldown smoke run 1, 2026-10-06).
    """

    from joulewise import window_lineage
    return window_lineage.current_boot_session_id()


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


# The flag for every pre-launch lineage disagreement that is not physics.
LINEAGE_PRELAUNCH_MISMATCH = "records.lineage_prelaunch_mismatch"


def lineage_identity(window: Mapping[str, Any]) -> dict[str, Any]:
    """The identity the window's lineage carries, from the fields publication writes.

    ``plan_id`` is the PACK plan id: members compare it with the pack's plan
    tree (``controller``: ``plan["plan_id"] != lineage["plan_id"]`` refuses),
    and the chain reserves the bracket session under it. A window plan id is
    a different string (cooldown smoke run 2, 2026-10-06).
    """

    pack = window["pack"]
    return {"plan_id": pack["pack_plan_id"], "window_id": pack["window_id"],
            "bracket_session_id": window["bracket_session_id"]}


def _production_lineage_check(request: LineageRequest) -> dict[str, Any]:
    """Re-read both runs roots' lineage locators before launch (PLAN2 row 9).

    Each root is read the way a member reads it: the members' own
    window-level authenticator (``window_lineage.authenticate_campaign``, with
    its default boot reader ``window_lineage.current_boot_session_id``), and
    the lineage's identity compared with the identity this window publishes
    (:func:`lineage_identity`). Returns ``{"claim": {...}, "bound": {...}}``;
    each entry has ``valid``, ``boot_changed`` and, when not valid, ``error``
    and ``mismatches`` (``{field: {"observed", "expected"}}``).

    Only ``boot_changed`` is physics: the lineage records a boot and the
    canonical reader now reads a different one, so monotonic clocks do not
    join. Every other disagreement is bookkeeping, which the driver records
    as a flag and launches anyway (doctrine 2026-10-05).
    """

    from joulewise import window_lineage
    try:
        current_boot = window_lineage.current_boot_session_id()
    except Exception:  # noqa: BLE001 - an unreadable boot judges nothing, as for members
        current_boot = None
    window = request.hazard_window
    checks: dict[str, Any] = {}
    for role, root in (("claim", request.claim_runs_root), ("bound", request.bound_runs_root)):
        entry: dict[str, Any] = {"root": str(root), "valid": False, "boot_changed": False,
                                 "current_boot_session_id": current_boot}
        errors: list[str] = []
        try:
            locator, digest = window_lineage.read_locator(Path(root) / window_lineage.LOCATOR_BASENAME)
        except Exception as error:  # noqa: BLE001 - an unreadable locator is a record
            entry.update(locator_absent=isinstance(error, window_lineage.HazardLineageError)
                         and error.reason_code == "launch_consumption_missing",
                         error=_error_text(error))
            checks[role] = entry
            continue
        lineage = locator.get("launch_lineage") if isinstance(locator, Mapping) else None
        lineage = lineage if isinstance(lineage, Mapping) else {}
        recorded_boot = lineage.get("collection_boot_session_id")
        entry.update(sha256=digest, recorded_boot_session_id=recorded_boot,
                     boot_changed=recorded_boot is not None and current_boot is not None
                     and recorded_boot != current_boot)
        try:
            window_lineage.authenticate_campaign(Path(root))
        except Exception as error:  # noqa: BLE001 - a member would refuse; the driver records it
            errors.append(_error_text(error))
        mismatches: dict[str, Any] = {}
        try:
            expected = lineage_identity(window)
        except Exception as error:  # noqa: BLE001 - an unreadable window identity is a record
            errors.append(f"window identity unreadable: {_error_text(error)}")
            expected = {}
        for field, value in expected.items():
            if lineage.get(field) != value:
                mismatches[field] = {"observed": lineage.get(field), "expected": value}
        if mismatches:
            errors.append("the locator names " + ", ".join(
                f"{field} {item['observed']!r}, not this window's {item['expected']!r}"
                for field, item in sorted(mismatches.items())))
            entry["mismatches"] = mismatches
        if errors:
            entry["error"] = "; ".join(errors)
        else:
            entry["valid"] = True
        checks[role] = entry
    return checks


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
    verify_lineage: Callable[[LineageRequest], Mapping[str, Any]] = _production_lineage_check
    # The KM003C wall meter's command line; None runs the window without it.
    meter_argv: Callable[[MonitorRequest], Sequence[str]] | None = None


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
    # ARM-OS (gate-prune core lane VPF): the epochs the pre-slot writer's kept
    # epoch check judges against, so an OS or machine no acceptance judges
    # refuses at arm instead of after the dwell.  The writer runs from the
    # measurement checkout with its default acceptance (the chain passes
    # none), so that file is read here.  Continuations are authenticated
    # WITHOUT the ledger session cross-check (snapshot None): that can only add
    # epochs, never remove one, so the arm never refuses a window the writer
    # would accept (for example when a stale head pin makes the cross-check
    # fail; review F2).  Any failure to load passes None, and the arm then
    # reads no identity.
    expected_epochs: list[dict[str, Any]] | None = None
    try:
        from joulewise.calibration_bracketing import (
            DEFAULT_ACCEPTANCE_BOUND_PATH, load_calibration_acceptance_bound)
        from joulewise.calibration_epoch_continuation import acceptance_judged_epochs
        code_root = Path(__file__).resolve().parents[2]
        measurement = getattr(context.plan, "measurement_root", None)
        root = Path(measurement) if measurement else code_root
        artifact = load_calibration_acceptance_bound(
            root / DEFAULT_ACCEPTANCE_BOUND_PATH.relative_to(code_root))
        if artifact is not None:
            expected_epochs = [dict(epoch) for epoch in acceptance_judged_epochs(artifact, None)]
    except Exception:  # noqa: BLE001 - an unloadable epoch list adds no refusal
        expected_epochs = None
    config = hazard_arm.ArmConfig(
        custody_dir=context.record_root.parent, thresholds=_arm_thresholds(context),
        disk_targets=[dict(item) for item in context.disk_targets],
        tree_roots=tuple(context.measurement_tree_pids),
        record_only=[{"name": "flags.arm", "argv": list(context.record_only_argv),
                      "timeout_s": COLLECTOR_TIMEOUT_S}] if context.record_only_argv else [],
        expected_epochs=expected_epochs)
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
    identity = lineage_identity(window)
    return window_lineage.publish_window_lineage(
        pack_root=pack["pack_root"], pack_id=pack["pack_id"], plan_id=identity["plan_id"],
        window_id=identity["window_id"], bracket_session_id=identity["bracket_session_id"],
        pre_attempt_id=window["bindings"]["pre_attempt_id"],
        post_attempt_id=window["bindings"]["post_attempt_id"],
        claim_runs_root=request.claim_runs_root, bound_runs_root=request.bound_runs_root,
        custody_root=request.custody_root, night_dir=request.night_dir,
        pack_sha256=pack["pack_sha256"], arm_decision_path=request.arm_decision_path,
        boot_session_id=request.boot_session_uuid)


def _plan_clock_step_ns(window: Mapping[str, Any]) -> int | None:
    """The plan's clock-step threshold for the monitor's skew bound (cold pass N5), or None.

    The harvest judges steps with ``hazard_window.harvest_thresholds.clock_step_ns``;
    the arm's block carries the same registered value as ``thresholds.clock.step_ns``.
    """

    for value in ((window.get("harvest_thresholds") or {}).get("clock_step_ns"),
                  ((window.get("thresholds") or {}).get("clock") or {}).get("step_ns")):
        if not isinstance(value, bool) and isinstance(value, (int, float)) and value > 0 \
                and float(value) == int(value):
            return int(value)
    return None


def production_seams(repo_root: Path) -> Seams:
    """The production seams; ``repo_root`` is the driver's own checkout."""

    repo_root = Path(repo_root)

    def monitor_argv(request: MonitorRequest) -> list[str]:
        """Write the monitor's config once (lane L1's format) and return its command line."""

        from joulewise.hazards import monitor as hazard_monitor
        window = request.plan.hazard_window
        thresholds = window["thresholds"]
        # PLAN2 row 10: the chain's process-group leader (night/chain.started)
        # is a tree root beside the driver, so the chain's own CPU stays inside
        # the tree even if the driver dies and the chain is reparented.
        config = hazard_monitor.build_config(
            custody_dir=request.custody_root, tree_roots=(request.driver_pid,),
            disk_targets=disk_targets(window, arm=False),
            low_bytes=int(thresholds.get("disk", {}).get("low_bytes", DISK_LOW_BYTES_DEFAULT)),
            cpu_limit_s_per_s=float(thresholds.get("contention", {}).get("cpu_limit_s_per_s", 0.05)),
            tree_root_files=(str(Path(request.night_dir) / "chain.started"),),
            clock_step_ns=_plan_clock_step_ns(window))
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

    def meter_argv(request: MonitorRequest) -> list[str]:
        """The meter's command line; a new create-once stream file per (re)start.

        Plain QoS, no ``taskpolicy -b``: the 2026-10-06 probe found 200 ms
        polls clean at plain QoS and rejected the background configuration.
        """

        out_dir = Path(request.custody_root).joinpath(*METER_STREAM_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)
        return [sys.executable, "-B", str(repo_root / "scripts/km003c_monitor.py"),
                "--out", str(next_meter_stream(out_dir))]

    return Seams(arm=_production_arm, publish_lineage=_production_lineage,
                 monitor_argv=monitor_argv, collectors_argv=collectors_argv, g10_argv=g10_argv,
                 meter_argv=meter_argv)


def next_meter_stream(out_dir: Path) -> Path:
    """The first ``stream-NNN.jsonl`` not yet in ``out_dir`` (the meter's ``--out`` is create-once)."""

    index = 1
    while (Path(out_dir) / f"stream-{index:03d}.jsonl").exists():
        index += 1
    return Path(out_dir) / f"stream-{index:03d}.jsonl"


def meter_streams(custody: Path, *, digests: bool) -> list[dict[str, Any]]:
    """The meter's stream files in custody: path, header status and (once stopped) SHA-256.

    Structure only. The stream bytes (power samples) stay in custody, where
    the harvest archives them with the rest of the custody root.
    """

    rows: list[dict[str, Any]] = []
    custody = Path(custody)
    for path in sorted(custody.joinpath(*METER_STREAM_DIR).glob("stream-*.jsonl")):
        status = None
        try:
            with path.open("rb") as handle:
                header = json.loads(handle.readline() or b"null")
            if isinstance(header, dict) and header.get("k") == "h" and isinstance(header.get("status"), str):
                status = header["status"]
        except (OSError, ValueError):
            status = None
        row: dict[str, Any] = {"path": path.relative_to(custody).as_posix(), "status": status}
        if digests:
            row["sha256"] = _sha256_file(path)
        rows.append(row)
    return rows


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
    """Start, supervise and stop a monitor process in its own process group.

    ``name`` names its journal (``<name>_supervision.jsonl``) and logs
    (``<name>.stdout.log``, ``<name>.stderr.log``) under the night directory;
    the default is the hazard monitor's. With ``restart_on_clean_exit`` false
    an exit with code 0 is final (the meter's recorded "absent" exit): it is
    journaled and never restarted. A nonzero exit or a signal death is
    restarted either way.
    """

    def __init__(self, argv: Sequence[str] | Callable[[], Sequence[str]], *, night_dir: Path,
                 popen: Callable[..., Any],
                 group_census: Callable[[int, float], tuple[bool, list[str]]] | None = None,
                 identity: Callable[[int], Any] | None = None, name: str = "monitor",
                 restart_on_clean_exit: bool = True) -> None:
        self.argv_factory = argv if callable(argv) else (lambda: argv)
        self.argv: list[str] = []
        self.night_dir = Path(night_dir)
        self.name = name
        self.journal = self.night_dir / f"{name}_supervision.jsonl"
        self.restart_on_clean_exit = restart_on_clean_exit
        self.final_exit: dict[str, Any] | None = None
        self.last_start_error: str | None = None
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
        # PLAN2 row 11: an exit within MONITOR_RAPID_EXIT_S of its start counts
        # as a failure for the backoff; a crash loop is flagged once, and the
        # supervisor never stops respawning.
        self.started_at: float | None = None
        self.crash_loop = False
        self.on_crash_loop: Callable[[dict[str, Any]], None] | None = None

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
            with open(self.night_dir / f"{self.name}.stdout.log", "ab") as out, \
                    open(self.night_dir / f"{self.name}.stderr.log", "ab") as err:
                process = self.popen(self.argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                     start_new_session=True, close_fds=True)
        except Exception as error:  # noqa: BLE001 - recorded; the chain is never held for it
            self.start_failures += 1
            self.consecutive_failures += 1
            self.last_start_error = _error_text(error)
            self._record("start_failed", argv=self.argv, error=self.last_start_error)
            if self.down_since is None:
                self.down_since = stamp()
            return False
        self.process = process
        self.starts += 1
        self.started_at = time.monotonic()
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

        if self.stopped or self.final_exit is not None:
            return
        if self.process is not None:
            code = self.process.poll()
            lived = time.monotonic() - (self.started_at if self.started_at is not None else time.monotonic())
            if code is None:
                if lived >= MONITOR_RAPID_EXIT_S:
                    self.consecutive_failures = 0
                return
            if code == 0 and not self.restart_on_clean_exit:
                self.final_exit = {"pid": self.process.pid, "returncode": code, "at": stamp(),
                                   "lived_s": round(lived, 3), "final": True}
                self.exits.append(self.final_exit)
                self._record("exit", pid=self.process.pid, returncode=code, lived_s=round(lived, 3), final=True)
                self.process = None
                return
            self.exits.append({"pid": self.process.pid, "returncode": code, "at": stamp(),
                               "lived_s": round(lived, 3)})
            self._record("exit", pid=self.process.pid, returncode=code, lived_s=round(lived, 3))
            self.consecutive_failures = self.consecutive_failures + 1 if lived < MONITOR_RAPID_EXIT_S else 0
            self.process = None
            self.down_since = stamp()
        self._note_crash_loop()
        interval = (MONITOR_RESTART_BACKOFF_S if self.consecutive_failures >= MONITOR_BACKOFF_AFTER
                    else MONITOR_RESTART_INTERVAL_S)
        if time.monotonic() - self.last_attempt >= interval:
            self.start()

    def _note_crash_loop(self) -> None:
        if self.crash_loop or self.consecutive_failures < MONITOR_BACKOFF_AFTER:
            return
        self.crash_loop = True
        details = {"consecutive_failures": self.consecutive_failures, "starts": self.starts,
                   "start_failures": self.start_failures, "backoff_s": MONITOR_RESTART_BACKOFF_S}
        self._record("crash_loop", **details)
        if self.on_crash_loop is not None:
            try:
                self.on_crash_loop(details)
            except Exception as error:  # noqa: BLE001 - a flag is a record
                self.errors.append(_error_text(error))

    def discard(self, reason: str) -> None:
        """Stop the current process (readiness retry); the supervisor itself stays live."""

        process, self.process = self.process, None
        if process is None:
            return
        if process.poll() is None:
            for number, grace in ((signal.SIGTERM, 2.0), (signal.SIGKILL, MONITOR_STOP_GRACE_S)):
                try:
                    os.killpg(process.pid, number)
                except (ProcessLookupError, PermissionError):
                    pass
                try:
                    process.wait(timeout=grace)
                    break
                except subprocess.TimeoutExpired:
                    continue
        self.exits.append({"pid": process.pid, "returncode": process.poll(), "at": stamp(),
                           "discarded": reason})
        self._record("discard", pid=process.pid, returncode=process.poll(), reason=reason)
        if self.down_since is None:
            self.down_since = stamp()

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
        summary = {"schema": MONITOR_JOURNAL_SCHEMA, "argv": self.argv, "starts": self.starts,
                   "restarts": max(0, self.starts - 1), "start_failures": self.start_failures,
                   "exits": self.exits, "gaps": self.gaps, "stop": self.stop_record,
                   "journal": self.journal.name, "errors": self.errors, "crash_loop": self.crash_loop}
        if not self.restart_on_clean_exit:
            summary["final_exit"] = self.final_exit
        return summary


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
# PLAN2 rows 10 and 11: monitor readiness before launch and liveness in the window


_GOOD_MONITOR_KINDS = {"battery": frozenset({"reading"}), "contention": frozenset({"snapshot", "interval"})}


def _journal_lines(path: Path) -> list[dict[str, Any]]:
    """Complete JSON lines of one monitor journal; a torn or foreign line is skipped."""

    try:
        data = Path(path).read_bytes()
    except OSError:
        return []
    rows = []
    for raw in data.split(b"\n")[:-1]:
        try:
            value = json.loads(raw)
        except ValueError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def _session_pid(line: Mapping[str, Any]) -> str:
    return str(line.get("session", "")).split("-", 1)[0]


def monitor_readiness(directory: Path, pid: int) -> dict[str, Any]:
    """Has monitor process ``pid`` journaled a session start, one battery reading and one
    contention snapshot, each without error? (Counts and booleans only.)"""

    status = {"session_start": False, "battery": False, "contention": False}
    for name, kinds in _GOOD_MONITOR_KINDS.items():
        for line in _journal_lines(Path(directory) / f"{name}.jsonl"):
            if _session_pid(line) != str(pid):
                continue
            if line.get("kind") == "session_start":
                status["session_start"] = True
            elif isinstance(line.get("kind"), str) and line["kind"] in kinds and line.get("error") is None:
                status[name] = True
    status["ready"] = all(status.values())
    return status


def await_monitor_ready(monitor: "MonitorSupervisor", directory: Path) -> tuple[bool, list[dict[str, Any]]]:
    """Start the monitor and wait for it to journal; up to MONITOR_READY_TRIES starts.

    The hazard "the instrument not sampling" measured directly: a monitor that
    never writes a session start plus one battery and one contention line
    without error leaves every member battery- and contention-unmeasured.
    """

    attempts: list[dict[str, Any]] = []
    for attempt in range(MONITOR_READY_TRIES):
        if attempt:
            monitor.discard("not ready")
        started = monitor.start()
        entry: dict[str, Any] = {"attempt": attempt + 1, "started": started, "at": stamp()}
        if not started:
            attempts.append(entry)
            continue
        deadline = time.monotonic() + MONITOR_READY_TIMEOUT_S
        status: dict[str, Any] = {}
        while True:
            process = monitor.process
            status = monitor_readiness(directory, process.pid)
            alive = process.poll() is None
            if status["ready"] and alive:
                entry.update(status=status, ready=True, waited_s=round(
                    MONITOR_READY_TIMEOUT_S - (deadline - time.monotonic()), 3))
                attempts.append(entry)
                return True, attempts
            if not alive or time.monotonic() >= deadline:
                break
            time.sleep(MONITOR_READY_POLL_S)
        entry.update(status=status, ready=False, alive=monitor.process.poll() is None
                     if monitor.process is not None else False)
        attempts.append(entry)
    return False, attempts


class MonitorLiveness:
    """Mid-window instrument outage: no error-free battery or contention line for MONITOR_OUTAGE_S.

    Reads only the bytes each journal gained since the last check (every
    MONITOR_LIVENESS_CHECK_S), so the cost does not grow with the window.
    """

    def __init__(self, directory: Path, *, clock: Callable[[], float] = time.monotonic) -> None:
        self.directory = Path(directory)
        self.clock = clock
        now = clock()
        self.offsets = {name: 0 for name in _GOOD_MONITOR_KINDS}
        self.partial = {name: b"" for name in _GOOD_MONITOR_KINDS}
        self.last_good = {name: now for name in _GOOD_MONITOR_KINDS}
        self.next_check = now
        self.errors: list[str] = []

    def check(self) -> dict[str, Any] | None:
        now = self.clock()
        if now < self.next_check:
            return None
        self.next_check = now + MONITOR_LIVENESS_CHECK_S
        for name, kinds in _GOOD_MONITOR_KINDS.items():
            # Sol review F1: a journal that cannot be read or parsed is not a
            # good reading. The fault stays inside this journal's read, never
            # skips the silence computation below, so an unreadable journal
            # runs into the outage bound like a silent one.
            try:
                self._read(name, kinds, now)
            except Exception as error:  # noqa: BLE001 - unreadable is not sampling
                if len(self.errors) < 20:
                    self.errors.append(f"{name}: {_error_text(error)}")
        return self.silent(now)

    def silent(self, now: float) -> dict[str, Any] | None:
        silent = {name: round(now - seen, 1) for name, seen in self.last_good.items()
                  if now - seen >= MONITOR_OUTAGE_S}
        return {"silent_s": silent, "outage_s": MONITOR_OUTAGE_S} if silent else None

    def _read(self, name: str, kinds: frozenset[str], now: float) -> None:
        path = self.directory / f"{name}.jsonl"
        size = path.stat().st_size
        if size < self.offsets[name]:
            self.offsets[name], self.partial[name] = 0, b""
        if size == self.offsets[name]:
            return
        with path.open("rb") as handle:
            handle.seek(self.offsets[name])
            data = handle.read(size - self.offsets[name])
        self.offsets[name] += len(data)
        lines = (self.partial[name] + data).split(b"\n")
        self.partial[name] = lines.pop()
        for raw in lines:
            try:
                line = json.loads(raw)
            except ValueError:
                continue
            if (isinstance(line, dict) and isinstance(line.get("kind"), str) and line["kind"] in kinds
                    and line.get("error") is None):
                self.last_good[name] = now


# --------------------------------------------------------------------------
# PLAN2 row 7: the in-window agent census


class HazardCensus:
    """The HAZARD in-window census (PLAN2 row 7), classified on the raw probe.

    POSITIVE (any stdout, whatever the exit code): the gate's own refusal, so
    the chain stops as today. CLEAN (exit 1, empty stdout): nothing. Anything
    else (a timeout 124 or spawn failure 127 with empty output, exit 0/2/3
    with empty output, a probe error) is UNMEASURED: retried CENSUS_RETRIES
    times CENSUS_RETRY_S apart, then flagged ``census.unmeasured`` and the
    chain goes on. CENSUS_UNMEASURED_STOP_AFTER unmeasured censuses in a row
    stop the chain under ``night_stopped_census_unmeasured``. The arm and
    pre-GO censuses are not this class: they stay strict.
    """

    def __init__(self, window: "_Window", probes: Any, *, sleep: Callable[[float], None] = time.sleep) -> None:
        self.window = window
        self.probes = probes
        self.sleep = sleep
        self.consecutive_unmeasured = 0
        self.unmeasured_censuses = 0
        self.retried_probes = 0
        self.journal_failures = 0
        self.journal_flagged = False

    @staticmethod
    def classify(probe: Any) -> str:
        stdout = str(getattr(probe, "stdout", "") or "")
        if stdout.strip():
            return "positive"
        if getattr(probe, "exit_code", None) == 1:
            return "clean"
        return "unmeasured"

    def _probe(self) -> tuple[Any, Any]:
        try:
            return self.window.rt.agent_census(self.probes, own_tree_root=os.getpid())
        except Exception as error:  # noqa: BLE001 - an unreadable census is unmeasured, never a crash
            probe = night_gate.ProbeResult(tuple(night_gate.AGENT_CENSUS_ARGV), -1, "", _error_text(error),
                                           time.monotonic_ns())
            return probe, night_gate.Refusal("night_probe_error", _error_text(error), (probe,))

    def __call__(self) -> tuple[Any, Any]:
        first = stamp()
        observed = []
        probe = refusal = None
        for attempt in range(1 + CENSUS_RETRIES):
            if attempt:
                self.retried_probes += 1
                self.sleep(CENSUS_RETRY_S)
            probe, refusal = self._probe()
            kind = self.classify(probe)
            if kind == "positive":
                self.consecutive_unmeasured = 0
                if refusal is None:  # a defensive case: the gate always refuses on output
                    refusal = night_gate.Refusal("night_refused_agent_present",
                                                 f"pgrep exit {probe.exit_code}; forbidden process output",
                                                 (probe,))
                return probe, refusal
            if kind == "clean":
                self.consecutive_unmeasured = 0
                return probe, None
            observed.append({"exit_code": getattr(probe, "exit_code", None),
                             "refusal": getattr(refusal, "reason", None)})
        last = stamp()
        self.consecutive_unmeasured += 1
        self.unmeasured_censuses += 1
        self.window.flag(
            "census.unmeasured", "DIAGNOSTIC", "PHYSICS", stage="window",
            observed={"attempts": observed, "consecutive": self.consecutive_unmeasured,
                      "stop_after": CENSUS_UNMEASURED_STOP_AFTER},
            detail="the in-window agent census could not be read on any retry; collection continued",
            legacy_site="scripts/run_night.py:_run_chain_once_impl", legacy_code="night_refused_agent_present",
            interval={"monotonic_ns": [first["monotonic_ns"], last["monotonic_ns"]],
                      "monotonic_raw_ns": ([first["monotonic_raw_ns"], last["monotonic_raw_ns"]]
                                           if first["monotonic_raw_ns"] is not None
                                           and last["monotonic_raw_ns"] is not None else None),
                      "wall_s": [first["wall_s"], last["wall_s"]]})
        if self.consecutive_unmeasured >= CENSUS_UNMEASURED_STOP_AFTER:
            detail = (f"{self.consecutive_unmeasured} consecutive in-window agent censuses were unmeasured "
                      f"(each after {CENSUS_RETRIES} retries); the driver stopped the chain")
            return probe, night_gate.Refusal(STOPPED_CENSUS_UNMEASURED, detail, (probe,))
        return probe, None

    def append(self, path: Path, probe: Any, refusal: Any) -> None:
        """The census journal append: a record, so a write fault is a flag, never a stop (row 10)."""

        try:
            self.window.rt._append_census(path, probe, refusal)
        except Exception as error:  # noqa: BLE001
            self.journal_failures += 1
            if not self.journal_flagged:
                self.journal_flagged = True
                self.window.flag("census.journal_write_failed", "RECORDS", "REPRESENTATION", stage="window",
                                 observed={"error": _error_text(error)},
                                 detail="an in-window census line could not be journaled; the census "
                                        "decision used the probe and collection continued")

    def summary(self) -> dict[str, Any]:
        return {"unmeasured_censuses": self.unmeasured_censuses, "retried_probes": self.retried_probes,
                "consecutive_unmeasured": self.consecutive_unmeasured,
                "journal_failures": self.journal_failures}


# --------------------------------------------------------------------------
# PLAN2 section 2.2: the yield plan, the in-window tripwire and the terminal count


_RUN_ID_SAFE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def _stage_role(runs_root: str, bound_root: str, roles: Sequence[Any]) -> str:
    if str(runs_root) == str(bound_root) or any(role == "neg8_reference_corpus_member" for role in roles):
        return "corpus"
    if roles and all(isinstance(role, str) and role.startswith("neg8_daily_reference") for role in roles):
        return "reference"
    return "science"


def _min_valid(role: str, planned: int) -> int:
    if role == "corpus":
        return min(CORPUS_MIN_VALID, planned)
    if role == "reference":
        return planned
    return -(-planned * SCIENCE_MIN_NUMERATOR // SCIENCE_MIN_DENOMINATOR)


def _local_stage_dispatch(stage: Any, *, tree: Mapping[str, Any], bindings: Mapping[str, str],
                          measurement_root: Path) -> tuple[str, list[str], list[Any]]:
    """J3's contract, read the way the chain runs the stage: argv[0]'s order manifest and ``--runs-dir``."""

    argv = b5_chain.stage_argv(stage, bindings, tree, Path(measurement_root))
    arguments = argv[2:]
    config_dir = Path(arguments[0])
    runs_root = arguments[arguments.index("--runs-dir") + 1]
    order = json.loads((config_dir / "order_manifest.json").read_bytes())["executed_order"]
    run_ids = [row["run_id"] for row in order]
    roles = [row.get("role") for row in order if isinstance(row, Mapping)]
    return runs_root, run_ids, roles


def yield_plan(plan: Any) -> dict[str, Any]:
    """{stage_id, ordinal, root, run_ids, planned, min_valid} for each in-chain collection stage.

    ``run_ids`` are net of run ids an earlier stage already launched into the
    same root (run_campaign skips a complete bundle, so those positions are
    never measured again). Uses the J3 resolver (``joulewise.b5.plan.
    resolve_stage_dispatch``) when it is present and answers, else reads the
    stage's own argv the same way.
    """

    from joulewise.b5 import plan as b5_plan
    window = plan.hazard_window
    pack_root = Path(window["pack"]["pack_root"])
    tree = json.loads((pack_root / "plan_tree.json").read_bytes())
    bindings = window["bindings"]
    measurement = Path(plan.measurement_root)
    bound_root = str(window["runs_roots"]["bound"])
    resolver = getattr(b5_plan, "resolve_stage_dispatch", None)
    launched: dict[str, set[str]] = {}
    stages, sources = [], set()
    chain_stages = [stage for stage in b5_chain.stage_plan(tree) if stage.in_chain]
    for position, stage in enumerate(chain_stages):
        if stage.kind != "campaign_collection":
            continue
        # Sol review F3: counting in the window is allowed only when the next
        # in-chain stage begins with a settle (a collection) or captures
        # nothing (the bound derivation); the last collection stage runs
        # straight into the post-calibration capture, so it counts at the end.
        following = chain_stages[position + 1] if position + 1 < len(chain_stages) else None
        count_in_window = following is not None and following.kind in {"campaign_collection",
                                                                          "bound_derivation"}
        runs_root = run_ids = None
        roles: list[Any] = []
        if callable(resolver):
            try:
                resolved = resolver(stage, tree=tree, bindings=bindings, measurement_root=measurement)
                runs_root, run_ids = str(resolved[0]), [str(item) for item in resolved[1]]
                sources.add("J3")
            except Exception:  # noqa: BLE001 - a resolver of another shape: read the argv
                runs_root = run_ids = None
        local_root, local_ids, roles = _local_stage_dispatch(stage, tree=tree, bindings=bindings,
                                                             measurement_root=measurement)
        if run_ids is None:
            runs_root, run_ids = local_root, local_ids
            sources.add("driver")
        for run_id in run_ids:
            if not isinstance(run_id, str) or _RUN_ID_SAFE.fullmatch(run_id) is None:
                raise ValueError(f"{stage.stage_id}: run id {run_id!r} is not a bundle directory name")
        seen = launched.setdefault(str(runs_root), set())
        fresh = []
        for run_id in run_ids:
            if run_id not in seen and run_id not in fresh:
                fresh.append(run_id)
        seen.update(fresh)
        role = _stage_role(str(runs_root), bound_root, roles)
        stages.append({"stage_id": stage.stage_id, "ordinal": stage.ordinal, "role": role,
                       "root": "bound" if str(runs_root) == bound_root else "claim",
                       "runs_root": str(runs_root), "run_ids": fresh, "planned": len(fresh),
                       "listed": len(run_ids), "min_valid": _min_valid(role, len(fresh)),
                       "count_in_window": count_in_window})
    return {"schema": YIELD_PLAN_SCHEMA, "plan_id": plan.plan_id, "source": sorted(sources),
            "stages": stages, "planned": sum(row["planned"] for row in stages)}


def _bundle_state(runs_root: Path, run_id: str) -> tuple[bool, bool]:
    """(present, succeeded) from structure only: a bundle directory with metadata or a summary."""

    bundle = Path(runs_root) / run_id
    summary = bundle / "summary_metrics.json"
    present = (bundle / "metadata.json").is_file() or summary.is_file()
    succeeded = False
    if summary.is_file():
        try:
            succeeded = json.loads(summary.read_bytes()).get("status") == "succeeded"
        except (OSError, ValueError, AttributeError):
            succeeded = False
    return present, succeeded


def count_stage(row: Mapping[str, Any]) -> dict[str, Any]:
    present = succeeded = 0
    for run_id in row["run_ids"]:
        has, ok = _bundle_state(Path(row["runs_root"]), run_id)
        present += has
        succeeded += ok
    planned = row["planned"]
    status = ("ZERO" if planned > 0 and present == 0 else
              "LOW" if succeeded < row["min_valid"] else "OK")
    return {"stage_id": row["stage_id"], "ordinal": row["ordinal"], "role": row["role"],
            "planned": planned, "present": present, "succeeded": succeeded,
            "min_valid": row["min_valid"], "status": status}


def _member_rows(raw: bytes) -> list[dict[str, Any]]:
    rows = []
    for line in raw.split(b"\n"):
        try:
            value = json.loads(line)
        except ValueError:
            continue
        if (isinstance(value, dict) and isinstance(value.get("run_id"), str) and value["run_id"]
                and isinstance(value.get("status"), str)):
            rows.append(value)
    return rows


def _redact(text: str) -> str:
    return "".join("#" if character.isdigit() else character for character in text)


class YieldTripwire:
    """PLAN2 yield B: counts at each stage boundary, a pre-bundle refusal run, a stall.

    Never stops anything and runs no subprocess. Its output is
    ``night/stage_yield.jsonl``, ``night/yield_alert-<ordinal>.json`` and
    window flags. Structure only: counts, statuses, return codes.

    Each supervision pass only stats the stage journal (and, once a minute,
    lists the runs roots for the stall check). Bundle counting and the member
    log tail run only in the settle right after a stage's journal line (Sol
    review F3); a stage whose line is stale, or that runs straight into a
    capture, is counted by :meth:`final` after the chain group is gone.
    """

    def __init__(self, window: "_Window", night: Path, plan_rows: Sequence[Mapping[str, Any]], *,
                 clock: Callable[[], float] = time.monotonic, wall: Callable[[], float] = time.time) -> None:
        self.window = window
        self.wall = wall
        self.deferred: dict[str, Any] = {}
        self.night = Path(night)
        self.rows = {row["stage_id"]: dict(row) for row in plan_rows}
        self.clock = clock
        self.journal_offset = 0
        self.journal_partial = b""
        self.counted: dict[str, dict[str, Any]] = {}
        self.roots = sorted({row["runs_root"] for row in plan_rows})
        self.planned_ids = {row["runs_root"]: set() for row in plan_rows}
        for row in plan_rows:
            self.planned_ids[row["runs_root"]].update(row["run_ids"])
        self.log_offsets = {root: 0 for root in self.roots}
        self.log_partial = {root: b"" for root in self.roots}
        self.run_cause: str | None = None
        self.run_length = 0
        self.flagged_causes: set[str] = set()
        self.attempted = 0
        now = clock()
        self.next_stall = now + YIELD_STALL_CHECK_S
        self.last_progress = now
        self.entries = {root: self._entries(root) for root in self.roots}
        self.stalled = False
        self.errors: list[str] = []

    @staticmethod
    def _entries(root: str) -> int:
        try:
            with os.scandir(root) as listing:
                return sum(1 for item in listing if item.is_dir(follow_symlinks=False))
        except OSError:
            return -1

    def _guard(self, label: str, operation: Callable[[], None]) -> None:
        try:
            operation()
        except Exception as error:  # noqa: BLE001 - the tripwire is a record; it never stops collection
            if len(self.errors) < 20:
                self.errors.append(f"{label}: {_error_text(error)}")

    def poll(self) -> None:
        self._guard("journal", self._journal)
        now = self.clock()
        if now >= self.next_stall:
            self.next_stall = now + YIELD_STALL_CHECK_S
            self._guard("stall", lambda: self._stall(now))

    def final(self) -> None:
        """After the chain group is gone: count every journaled stage not yet counted."""

        self._guard("journal", lambda: self._journal(terminal=True))
        for stage_id in sorted(self.deferred, key=lambda item: self.rows[item]["ordinal"]):
            rc = self.deferred[stage_id]
            if stage_id not in self.counted:
                self._guard("count", lambda stage_id=stage_id, rc=rc: self._count(
                    self.rows[stage_id], rc, counted_at="terminal"))
        self._guard("campaign_log", self._campaign_logs)

    def _in_settle(self, stage_id: str, row: Mapping[str, Any]) -> bool:
        """Is it now the settle right after this stage (Sol review F3)?"""

        if not self.rows[stage_id].get("count_in_window", True):
            return False
        ended = row.get("ended_epoch_s")
        if isinstance(ended, bool) or not isinstance(ended, (int, float)):
            return False
        age = self.wall() - float(ended)
        return -2.0 <= age <= YIELD_COUNT_FRESH_S

    def _journal(self, terminal: bool = False) -> None:
        path = self.night / b5_chain.STAGE_JOURNAL
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            return
        if size <= self.journal_offset:
            return
        with path.open("rb") as handle:
            handle.seek(self.journal_offset)
            data = handle.read(size - self.journal_offset)
        self.journal_offset += len(data)
        self.last_progress = self.clock()
        lines = (self.journal_partial + data).split(b"\n")
        self.journal_partial = lines.pop()
        for raw in lines:
            try:
                row = json.loads(raw)
            except ValueError:
                continue
            if (isinstance(row, dict) and row.get("kind") == "campaign_collection"
                    and row.get("stage_id") in self.rows and row["stage_id"] not in self.counted):
                if not terminal and self._in_settle(row["stage_id"], row):
                    self._count(self.rows[row["stage_id"]], row.get("rc"), counted_at="settle")
                    # The member log is tailed at the same boundary, never
                    # during a capture.
                    self._guard("campaign_log", self._campaign_logs)
                else:
                    self.deferred[row["stage_id"]] = row.get("rc")

    def _count(self, row: Mapping[str, Any], rc: Any, *, counted_at: str = "settle") -> None:
        self.deferred.pop(row["stage_id"], None)
        counted = count_stage(row)
        counted.update(schema=STAGE_YIELD_SCHEMA, rc=rc, at=stamp(), counted_at=counted_at)
        self.counted[row["stage_id"]] = counted
        _append_line(self.night / STAGE_YIELD, counted)
        if counted["status"] == "OK":
            return
        code = "yield.stage_zero" if counted["status"] == "ZERO" else "yield.stage_low"
        facts = {key: counted[key] for key in ("stage_id", "ordinal", "role", "planned", "present",
                                               "succeeded", "min_valid", "status", "rc")}
        self.window.flag(code, "DIAGNOSTIC", "REPRESENTATION", stage="window", observed=facts,
                         expected={"min_valid": counted["min_valid"]},
                         detail=f"stage {row['stage_id']}: {counted['succeeded']} of {counted['planned']} "
                                f"planned members succeeded ({counted['present']} bundles present); "
                                "collection continues")
        try:
            _create_once(self.night / YIELD_ALERT.format(ordinal=counted["ordinal"]),
                         {"schema": YIELD_ALERT_SCHEMA, "plan_id": self.window.plan.plan_id,
                          "code": code, **facts, "at": counted["at"]})
        except OSError as error:
            self.errors.append(f"alert: {_error_text(error)}")

    def _campaign_logs(self) -> None:
        for root in self.roots:
            path = Path(root) / "campaign_log.jsonl"
            try:
                size = path.stat().st_size
            except FileNotFoundError:
                continue
            if size <= self.log_offsets[root]:
                continue
            with path.open("rb") as handle:
                handle.seek(self.log_offsets[root])
                data = handle.read(size - self.log_offsets[root])
            self.log_offsets[root] += len(data)
            lines = (self.log_partial[root] + data).split(b"\n")
            self.log_partial[root] = lines.pop()
            for member in _member_rows(b"\n".join(lines)):
                self._member(root, member)

    def _member(self, root: str, member: Mapping[str, Any]) -> None:
        if member["run_id"] not in self.planned_ids.get(root, ()):
            return
        self.attempted += 1
        present, _ok = _bundle_state(Path(root), member["run_id"])
        if present:
            self.run_cause, self.run_length = None, 0
            return
        refusal = member.get("child_refusal")
        if isinstance(refusal, str) and refusal.strip():
            cause, kind = _redact(refusal.strip()), "child_refusal"
        else:
            cause = (f"exit_code={member.get('exit_code')!r} "
                     f"blocked_before_invoke={bool(member.get('blocked_before_invoke'))}")
            kind = "exit_code"
        if cause == self.run_cause:
            self.run_length += 1
        else:
            self.run_cause, self.run_length = cause, 1
        if self.run_length >= YIELD_PRE_BUNDLE_RUN and cause not in self.flagged_causes:
            self.flagged_causes.add(cause)
            observed = {"consecutive": self.run_length, "cause_kind": kind,
                        "cause_sha256": hashlib.sha256(cause.encode("utf-8")).hexdigest(),
                        "exit_code": member.get("exit_code"),
                        "blocked_before_invoke": bool(member.get("blocked_before_invoke"))}
            if kind == "exit_code":
                observed["cause"] = cause
            self.window.flag("stage.members_refused_pre_bundle_identical", "DIAGNOSTIC", "REPRESENTATION",
                             stage="window", observed=observed,
                             detail=f"{self.run_length} consecutive members ended without a bundle for one "
                                    "shared cause; collection continues")

    def _stall(self, now: float) -> None:
        entries = {root: self._entries(root) for root in self.roots}
        if entries != self.entries:
            self.entries, self.last_progress = entries, now
        if not self.stalled and now - self.last_progress >= YIELD_STALL_S:
            self.stalled = True
            self.window.flag("yield.stage_stalled", "DIAGNOSTIC", "REPRESENTATION", stage="window",
                             observed={"silent_s": round(now - self.last_progress, 1),
                                       "stall_s": YIELD_STALL_S,
                                       "stages_counted": len(self.counted)},
                             detail="no new bundle directory and no new stage journal line for the stall "
                                    "bound; collection continues")

    def summary(self) -> dict[str, Any]:
        return {"stages_counted": len(self.counted), "attempted_seen": self.attempted,
                "counted_in_settle": sum(1 for item in self.counted.values() if item.get("counted_at") == "settle"),
                "stalled": self.stalled, "pre_bundle_runs_flagged": len(self.flagged_causes),
                "errors": list(self.errors)}


def terminal_yield(night: Path, rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """PLAN2 yield D: the window's yield from the campaign logs and the bundles, counts only."""

    journal = {row.get("stage_id"): row for row in b5_chain.stage_journal(night)}
    logs: dict[str, dict[str, Mapping[str, Any]]] = {}
    for root in sorted({row["runs_root"] for row in rows}):
        try:
            raw = (Path(root) / "campaign_log.jsonl").read_bytes()
        except FileNotFoundError:
            raw = b""
        last: dict[str, Mapping[str, Any]] = {}
        for member in _member_rows(raw):
            last[member["run_id"]] = member
        logs[root] = last
    per_stage = []
    for row in rows:
        counted = count_stage(row)
        members = [logs[row["runs_root"]].get(run_id) for run_id in row["run_ids"]]
        counted.update(logged=sum(1 for item in members if item is not None),
                       ok=sum(1 for item in members if item is not None and item.get("status") == "succeeded"),
                       failed=sum(1 for item in members if item is not None and item.get("status") == "failed"),
                       rc=(journal.get(row["stage_id"]) or {}).get("rc"),
                       journaled=row["stage_id"] in journal)
        per_stage.append(counted)
    totals = {key: sum(item[key] for item in per_stage)
              for key in ("planned", "logged", "ok", "failed", "present", "succeeded")}
    if totals["planned"] == 0:
        status = "UNKNOWN"
    elif totals["present"] == 0:
        status = "EMPTY"
    elif any(item["planned"] > 0 and item["succeeded"] < item["min_valid"] for item in per_stage):
        status = "LOW"
    elif totals["succeeded"] == totals["planned"]:
        status = "FULL"
    else:
        status = "PARTIAL"
    return {"schema": YIELD_SCHEMA, "planned": totals["planned"], "logged": totals["logged"],
            "ok": totals["ok"], "failed": totals["failed"], "bundles_present": totals["present"],
            "succeeded": totals["succeeded"], "per_stage": per_stage, "yield_status": status}


def _stage_fault(journal: Sequence[Mapping[str, Any]], stage_ids: Sequence[str]) -> bool | str:
    """True when a journaled row of these stages failed; "not_run" when none ran; else False."""

    rows = [row for row in journal if row.get("stage_id") in stage_ids]
    if not rows:
        return "not_run"
    return any(row.get("rc") not in (0, None) for row in rows)


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
        probe, refusal = self.rt.agent_census(self.probes, own_tree_root=os.getpid())
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

    def refuse(stage: str, reason: str, detail: str, evidence: Any, *,
               fault_reasons: Sequence[str] = ()) -> int:
        hazard.update(verdict="REFUSED", stage_reached=stage, refusal={"reason": reason, "detail": detail},
                      flags_emitted=list(window.flags), diagnostics=list(window.diagnostics), ended=stamp())
        if fault_reasons:
            hazard["faults"] = {"reasons": list(fault_reasons)}
        try:
            _create_once(night / HAZARD_RESULT, hazard)
        except OSError as error:
            window.note(f"hazard result could not be written: {_error_text(error)}")
        rt._write_standard_refusal_result(custody, night, plan, reason, detail, started_epoch_s,
                                          started_monotonic_ns, evidence=evidence)
        rt._append_log(custody, f"hazard window refused at {stage}: {reason}")
        report = _report(plan, rt.EXIT_REFUSED, {"verdict": "REFUSED", "stage_reached": stage,
                                                 "refusal_reason": reason, "detail": detail,
                                                 "arm_verdicts": hazard.get("arm", {}).get("verdicts"),
                                                 "yield_line": "collected 0 members: the window was refused "
                                                               "before the chain launched",
                                                 **({"fault": True, "fault_reasons": list(fault_reasons)}
                                                    if fault_reasons else {})},
                         window.diagnostics)
        return rt._finish_reporting(custody, night, plan, rt.EXIT_REFUSED, courier,
                                    courier_error=courier_error, deadman_epoch_s=deadman,
                                    courier_bin_substitution=substitution, report=report,
                                    allow_courier=courier is not None)

    # J4 (PLAN2 X1, Sol review R3): run_night journaled this night's first
    # record (censuses.jsonl) before calling here. The watchdog writes its
    # launch-abandoned marker first and then re-checks for driver records, so
    # re-checking the marker after our first record closes the race: a marker
    # seen here means the span was released, and nothing is armed.
    if (night / LAUNCH_ABANDONED_MARKER).exists():
        return refuse("launch_liveness", REFUSED_LAUNCH_ABANDONED,
                      "the watchdog marked this launch abandoned (night/launch_abandoned.json) before "
                      "the arm; nothing was measured", {"marker": f"night/{LAUNCH_ABANDONED_MARKER}"})

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

    # 3. Launch lineage into both runs roots, then re-read both locators the
    # way members read them (PLAN2 row 9). Physics refuses; everything else is
    # a flag (doctrine 2026-10-05): a publication failure, an absent locator or
    # any bookkeeping disagreement is recorded and the chain launches. A
    # publication that failed, or left a locator absent, is retried once. The
    # one refusal is a boot that changed since the lineage was published:
    # monotonic clocks do not join across a reboot.
    if window.boot is None:
        window.boot = seams.boot_session_uuid()
    roots = plan.hazard_window["runs_roots"]
    lineage_request = LineageRequest(
        plan=plan, plan_path=Path(plan_path), custody_root=custody, night_dir=night,
        hazard_window=plan.hazard_window, claim_runs_root=Path(roots["claim"]),
        bound_runs_root=Path(roots["bound"]),
        arm_record_path=Path(decision["record_path"]) if decision["record_path"] else None,
        arm_decision_path=night / ARM_DECISION if (night / ARM_DECISION).exists() else None,
        boot_session_uuid=window.boot)
    lineage_record: dict[str, Any] = {"schema": LINEAGE_SCHEMA, "requested": stamp(), "attempts": []}
    lineage_error: str | None = None

    def publish(attempt: int) -> None:
        nonlocal lineage_error
        try:
            published = seams.publish_lineage(lineage_request)
            lineage_record.update(published=True, result=json.loads(json.dumps(published, default=str)))
            lineage_record["attempts"].append({"attempt": attempt, "published": True})
            lineage_error = None
        except Exception as error:  # noqa: BLE001
            lineage_error = _error_text(error)
            lineage_record["attempts"].append({"attempt": attempt, "published": False, "error": lineage_error})

    def verify() -> Any:
        try:
            return seams.verify_lineage(lineage_request)
        except Exception as error:  # noqa: BLE001 - an unreadable check is not a valid locator
            return {"error": _error_text(error)}

    def role_entry(found: Any, role: str) -> Mapping[str, Any]:
        entry = found.get(role) if isinstance(found, Mapping) else None
        return entry if isinstance(entry, Mapping) else {}

    publish(1)
    if lineage_error is not None:
        time.sleep(LINEAGE_RETRY_S)
        publish(2)
        locators = verify()
    else:
        locators = verify()
        if any(role_entry(locators, role).get("locator_absent") for role in ("claim", "bound")):
            time.sleep(LINEAGE_RETRY_S)
            publish(2)
            locators = verify()
    if lineage_error is not None:
        lineage_record.update(published=False, error=lineage_error)
        window.flag("records.lineage_formality", "RECORDS", "REPRESENTATION",
                    observed={"error": lineage_error, "attempts": len(lineage_record["attempts"])},
                    detail="the hazard-window lineage could not be published before launch")
    else:
        lineage_record["published"] = True
    invalid = sorted(role for role in ("claim", "bound") if role_entry(locators, role).get("valid") is not True)
    boot_changed = sorted(role for role in ("claim", "bound") if role_entry(locators, role).get("boot_changed") is True)
    locators_valid = not invalid
    lineage_record.update(locators=json.loads(json.dumps(locators, default=str)),
                          locators_valid=locators_valid, boot_changed=boot_changed, ended=stamp())
    try:
        _create_once(night / LINEAGE_RECORD, lineage_record)
    except OSError as error:
        window.note(f"lineage record could not be written: {_error_text(error)}")
    hazard["lineage"] = {"published": lineage_record["published"], "error": lineage_record.get("error"),
                         "locators_valid": locators_valid, "boot_changed": boot_changed}
    if boot_changed:
        boots = {role: {"recorded": role_entry(locators, role).get("recorded_boot_session_id"),
                        "current": role_entry(locators, role).get("current_boot_session_id")}
                 for role in boot_changed}
        return refuse("lineage", REFUSED_BOOT_CHANGED,
                      "the boot changed since the launch lineage was published in the "
                      + " and ".join(boot_changed) + " runs root; monotonic clocks do not join across a "
                      "reboot, so the chain was not launched",
                      {"roots": boot_changed, "boots": boots, "lineage_record": f"night/{LINEAGE_RECORD}"})
    if invalid:
        try:
            expected = lineage_identity(plan.hazard_window)
        except Exception as error:  # noqa: BLE001 - a record
            expected = {"error": _error_text(error)}
        observed = {role: {key: role_entry(locators, role).get(key)
                           for key in ("error", "mismatches", "locator_absent", "sha256",
                                       "recorded_boot_session_id")}
                    for role in invalid}
        if isinstance(locators, Mapping) and "error" in locators:
            observed["check_error"] = locators["error"]
        window.flag(LINEAGE_PRELAUNCH_MISMATCH, "RECORDS", "REPRESENTATION", observed=observed,
                    expected={**expected, "boot_session_id": window.boot},
                    detail="the pre-launch lineage check disagrees with this window in the "
                           + " and ".join(invalid) + " runs root; recorded, and the chain launched",
                    evidence=[{"path": f"night/{LINEAGE_RECORD}", "sha256": digest}
                              for digest in (_sha256_file(night / LINEAGE_RECORD),) if digest])

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

    # 5. The monitor. It must journal before launch (PLAN2 row 11): without
    # its battery and contention journals every member is unmeasured.
    monitor_request = MonitorRequest(plan, Path(plan_path), custody, night, os.getpid())
    monitor = MonitorSupervisor(
        lambda: seams.monitor_argv(monitor_request),
        night_dir=night, popen=seams.popen, group_census=getattr(rt, "_group_census", None),
        identity=getattr(rt, "observe_identity", None))
    monitor.on_crash_loop = lambda details: window.flag(
        "monitor.crash_loop", "DIAGNOSTIC", "PHYSICS", stage="window", observed=details,
        detail="the hazard monitor kept exiting within 30 s of its start; it is restarted with backoff")
    journal_dir = custody.joinpath(*MONITOR_JOURNAL_DIR)
    ready, readiness = await_monitor_ready(monitor, journal_dir)
    hazard["monitor_readiness"] = {"ready": ready, "attempts": readiness}
    if not ready:
        hazard["monitor"] = monitor.stop()
        return refuse("monitor", REFUSED_INSTRUMENT_NOT_SAMPLING,
                      f"the hazard monitor did not journal a session start, a battery reading and a "
                      f"contention snapshot within {MONITOR_READY_TIMEOUT_S:g} s on any of "
                      f"{MONITOR_READY_TRIES} starts; the instrument is not sampling",
                      {"attempts": readiness}, fault_reasons=("instrument_not_sampling",))
    liveness = MonitorLiveness(journal_dir)

    # 5b. The KM003C wall meter (WIRING.md), supervised like the monitor but
    # never awaited and never a refusal: an absent meter exits 0 once and is
    # not restarted; its supervision failures are DISCLOSE flags.
    meter: MonitorSupervisor | None = None
    meter_faults: set[str] = set()

    def meter_fault(event: str, observed: Mapping[str, Any]) -> None:
        if event in meter_faults:
            return
        meter_faults.add(event)
        window.flag("meter.supervision_fault", "DIAGNOSTIC", "PHYSICS", stage="window",
                    observed={"event": event, **observed},
                    detail="the wall-meter process could not be supervised as planned (" + event + "); the "
                           "meter is a disclosed diagnostic and collection went on")

    if seams.meter_argv is not None:
        meter_argv = seams.meter_argv
        meter = MonitorSupervisor(
            lambda: meter_argv(monitor_request), night_dir=night, popen=seams.popen,
            group_census=getattr(rt, "_group_census", None), identity=getattr(rt, "observe_identity", None),
            name=METER_NAME, restart_on_clean_exit=False)
        meter.on_crash_loop = lambda details: meter_fault("crash_loop", details)
        meter.start()

    def meter_records() -> None:
        """Disclose what the meter's supervisor recorded and never flagged (Sol review F2, F3).

        Any failed start (the first or a restart in ``poll``) is a
        ``start_failed`` event. Anything in the supervisor's ``errors`` (a
        failed journal append, which is the dead-man's locator for an orphaned
        meter, or a failed crash-loop callback) is a ``record_failed`` event.
        Each is flagged once.
        """

        if meter is None:
            return
        if meter.start_failures:
            meter_fault("start_failed", {"error": meter.last_start_error, "start_failures": meter.start_failures})
        if meter.errors:
            meter_fault("record_failed", {"errors": list(meter.errors[:3]), "count": len(meter.errors)})

    def poll_meter() -> None:
        if meter is not None:
            meter.poll()
            meter_records()

    meter_records()

    def stop_meter(*, left_running: bool = False) -> dict[str, Any] | None:
        if meter is None:
            return None
        if left_running:
            meter_records()
            return {**meter.summary(), "left_running": True, "streams": meter_streams(custody, digests=False)}
        summary = meter.stop()
        meter_records()
        stop_record = summary.get("stop") or {}
        if not stop_record.get("proven_stopped"):
            meter_fault("not_proven_stopped", {"returncode": stop_record.get("returncode"),
                                               "group_absent": stop_record.get("group_absent")})
        return {**summary, "streams": meter_streams(custody, digests=True)}

    thresholds = plan.hazard_window["thresholds"].get("disk", {})
    low = thresholds.get("low_bytes", DISK_LOW_BYTES_DEFAULT) if isinstance(thresholds, Mapping) else DISK_LOW_BYTES_DEFAULT
    disk = DiskFloor([Path(roots["claim"]), Path(roots["bound"]), custody], int(low), seams.disk_free_bytes,
                     marker=custody / "hazards" / "monitor" / "disk.low")

    # The yield plan and its tripwire (PLAN2 section 2.2): records, never stops.
    yield_rows: list[dict[str, Any]] | None = None
    try:
        yield_record_plan = yield_plan(plan)
        yield_rows = yield_record_plan["stages"]
        hazard["yield_plan"] = {"planned": yield_record_plan["planned"], "stages": len(yield_rows),
                                "source": yield_record_plan["source"]}
        try:
            _create_once(night / YIELD_PLAN, yield_record_plan)
        except OSError as error:
            window.note(f"yield plan could not be written: {_error_text(error)}")
    except Exception as error:  # noqa: BLE001 - a record; never a refusal
        hazard["yield_plan"] = {"error": _error_text(error)}
        window.note(f"yield plan unavailable: {_error_text(error)}")
    tripwire = YieldTripwire(window, night, yield_rows) if yield_rows is not None else None

    # PLAN2 row 10: every supervision step is guarded; a fault in a record
    # never ends the chain, it is flagged once per step and the pass goes on.
    supervision_faults: dict[str, int] = {}
    liveness_failing_since: list[float | None] = [None]

    def supervision_fault(label: str, error: BaseException) -> None:
        supervision_faults[label] = supervision_faults.get(label, 0) + 1
        if supervision_faults[label] == 1:
            window.flag("supervision.pass_failed", "RECORDS", "REPRESENTATION", stage="window",
                        observed={"step": label, "error": _error_text(error)},
                        detail="a supervision step raised; the pass went on and collection continued")

    def guarded(label: str, operation: Callable[[], Any]) -> Any:
        try:
            return operation()
        except Exception as error:  # noqa: BLE001
            supervision_fault(label, error)
            return None

    def supervise() -> dict[str, Any] | None:
        guarded("monitor", monitor.poll)
        if meter is not None:
            guarded("meter", poll_meter)
        reading = guarded("disk", disk.check)
        if reading is not None:
            window.flag("disk.low", "DIAGNOSTIC", "PHYSICS", stage="window",
                        observed={"volume": reading["volume"], "free_bytes": reading["free_bytes"]},
                        expected={"low_bytes": reading["low_bytes"]},
                        detail="free space fell under the in-window floor; the driver stopped the chain")
            return rt._refusal_mapping(
                STOPPED_DISK_LOW,
                f"free space {reading['free_bytes']} B on {reading['volume']} is under the "
                f"{reading['low_bytes']} B in-window floor; the driver stopped the chain", reading)
        # Sol review F1: the liveness evaluation is a physics check. If it
        # raises, the instrument's sampling is unmeasured; that counts toward
        # the outage bound exactly like silence, never as "no outage".
        try:
            outage = liveness.check()
            liveness_failing_since[0] = None
        except Exception as error:  # noqa: BLE001
            supervision_fault("monitor_liveness", error)
            now = time.monotonic()
            if liveness_failing_since[0] is None:
                liveness_failing_since[0] = now
            failing = now - liveness_failing_since[0]
            outage = ({"silent_s": {"liveness_check": round(failing, 1)}, "outage_s": MONITOR_OUTAGE_S,
                       "unmeasured": True} if failing >= MONITOR_OUTAGE_S else None)
        if outage is not None:
            window.flag("monitor.outage", "DIAGNOSTIC", "PHYSICS", stage="window", observed=outage,
                        expected={"outage_s": MONITOR_OUTAGE_S},
                        detail="the hazard monitor wrote no battery or contention reading for the outage "
                               "bound; the driver stopped the chain")
            return rt._refusal_mapping(
                STOPPED_MONITOR_OUTAGE,
                "no error-free " + " or ".join(sorted(outage["silent_s"])) + " reading from the hazard "
                f"monitor for {MONITOR_OUTAGE_S:g} s; the instrument is not sampling, so the driver "
                "stopped the chain", outage)
        if tripwire is not None:
            guarded("yield", tripwire.poll)
        return None

    hazard_census = HazardCensus(window, probes)

    # 6. The chain, once.
    claim = rt._claim_chain_start(night)
    if claim is None:
        hazard["monitor"] = monitor.stop()
        if meter is not None:
            hazard["meter"] = stop_meter()
        return refuse("launch", rt._CODES["chain_already_started"],
                      "chain.started already exists; the night chain is once-only", None)
    exit_code: int | None = None
    abort: dict[str, Any] | None = None
    census_count, census_hits, proven = 0, [], False
    try:
        exit_code, abort, census_count, census_hits, proven = rt._run_chain_once(
            chain_path, plan, probes, night, claim, command=["/bin/zsh", "-f", str(chain_path)],
            abort_on_census=True, supervise=supervise, census_group_on_exit=True,
            census=hazard_census, append_census=hazard_census.append)
    except Exception as error:  # noqa: BLE001 - recorded; the terminal record must still be written
        window.note(f"chain supervision raised {_error_text(error)}")
        abort = rt._refusal_mapping(rt._CODES["chain_alive"],
                                    f"the driver's chain supervision raised {_error_text(error)}", None)
        proven = False
    # The chain exited no later than this instant (R3-5: the monitor stop is held from here).
    chain_returned = stamp()
    started = (night / "chain.started").exists()
    journal = b5_chain.stage_journal(night)
    hazard["chain"].update(exit_code=exit_code, started=started, termination_proven=proven,
                           stages=[{"stage_id": row.get("stage_id"), "kind": row.get("kind"), "rc": row.get("rc")}
                                   for row in journal])
    if tripwire is not None:
        guarded("yield", tripwire.final)
        hazard["yield_tripwire"] = tripwire.summary()
    hazard["census_supervision"] = hazard_census.summary()
    hazard["supervision_faults"] = dict(supervision_faults)
    # PLAN2 yield D: counts only, after the chain group is proven gone or never started.
    try:
        yield_record = (terminal_yield(night, yield_rows) if yield_rows is not None else
                        {"schema": YIELD_SCHEMA, "yield_status": "UNKNOWN",
                         "error": hazard["yield_plan"].get("error")})
    except Exception as error:  # noqa: BLE001 - a counting failure changes nothing else
        yield_record = {"schema": YIELD_SCHEMA, "yield_status": "UNKNOWN", "error": _error_text(error)}
    hazard["yield"] = yield_record
    # The NEG-8 manifest the derivation read: a locator for the harvest, which
    # needs the custodied bytes when the copy was pruned (chain DEVIATIONS).
    try:
        hazard["neg8_corpus"] = b5_chain.neg8_corpus_record(night)
    except Exception as error:  # noqa: BLE001 - a record; never a refusal
        hazard["neg8_corpus"] = {"errors": [_error_text(error)]}

    # 7. G10, with the monitor still journaling, only after a natural exit proven gone.
    want_g10 = bool(plan.hazard_window.get("g10"))
    if want_g10 and started and proven and abort is None:
        hazard["g10"] = _run_g10(window, night, float(plan.hazard_window["T_stream_max_s"]),
                                 supervise=supervise)
    else:
        hazard["g10"] = {"ran": False, "requested": want_g10,
                         "reason": ("not requested" if not want_g10 else
                                    "chain not started" if not started else
                                    "chain termination not proven" if not proven else
                                    "chain stopped by the driver")}

    # 8. The monitor (and the meter) stop only once the chain's process group is
    # proven gone, and no sooner than MONITOR_POST_CHAIN_HOLD_S after the chain
    # returned (R3-5: the SMC battery reads must cover the end of the post
    # capture); otherwise they keep journaling and the dead-man stops them
    # after its own proof.
    if proven or not started:
        if started:
            hazard["monitor_stop"] = hold_monitors_after_chain(
                chain_returned, lambda: (guarded("monitor", monitor.poll),
                                         meter is not None and guarded("meter", poll_meter)))
        hazard["monitor"] = monitor.stop()
        if started:
            hazard["monitor_stop"]["monitor_stop_requested"] = (hazard["monitor"].get("stop") or {}).get("requested")
        if meter is not None:
            hazard["meter"] = stop_meter()
    else:
        window.note("chain termination not proven: the hazard monitor is left running for the dead-man")
        hazard["monitor"] = {**monitor.summary(), "left_running": True}
        if meter is not None:
            hazard["meter"] = stop_meter(left_running=True)
    hazard["disk_floor"] = {"low_bytes": disk.low_bytes, "stops": disk.readings, "errors": disk.errors}
    chain_stop = next((row for row in journal if row.get("stage_id") == "chain.stop"), None)
    # The chain's stop exits (10/11/12) come only from its stop_chain, which
    # journals chain.stop first. A stop exit whose journal line is missing (an
    # append that failed) is still a stop, never a GO: the exit code names it.
    stop_kinds = {code: kind for kind, code in b5_chain.STOP_EXITS.items()}
    if chain_stop is None and abort is None and started and exit_code in stop_kinds:
        chain_stop = {"stage_id": "chain.stop", "kind": stop_kinds[exit_code], "rc": exit_code,
                      "source": "exit_code"}
        hazard["chain"]["stop_from_exit_code"] = chain_stop
        window.note(f"the chain exited {exit_code} ({stop_kinds[exit_code]}) without a chain.stop journal "
                    "line; the window is recorded as CHAIN_STOPPED from the exit code")
    stage_reached = "chain"
    yield_status = yield_record.get("yield_status")
    if abort is not None:
        reason = str(abort["reason"])
        if "document" not in abort:
            rt._write_driver_refusal(night / "refusal.json", plan, reason, str(abort["detail"]), abort["evidence"])
        refused = (reason in {rt._CODES["chain_launch_failed"], rt._CODES["chain_already_started"]}
                   or not proven or not started)
        verdict = "REFUSED" if refused else "ABORTED"
        base_exit = rt.EXIT_REFUSED if refused else rt.EXIT_ABORTED
        aborted_reason: str | None = reason
    elif chain_stop is not None:
        # PLAN2 yield D: a stop at exit 10/11/12 collected nothing; it is not a
        # GO (it hid an empty window) and not a REFUSED (that holds the fence).
        verdict = "CHAIN_STOPPED"
        base_exit = rt.EXIT_CHAIN_FAILED
        aborted_reason = None
        stage_reached = f"chain:{chain_stop.get('kind')}"
    else:
        verdict = "GO"  # it describes the arm; the yield says what was collected
        base_exit = rt.EXIT_GO if exit_code == 0 else rt.EXIT_CHAIN_FAILED
        if yield_status == "EMPTY":
            base_exit = rt.EXIT_CHAIN_FAILED
        aborted_reason = None
    summaries = [row for row in plan.hazard_window.get("stages") or [] if isinstance(row, Mapping)]
    captures = sorted((row for row in summaries if row.get("kind") == "calibration_capture"),
                      key=lambda row: row.get("ordinal") or 0)
    derivations = [str(row.get("stage_id")) for row in summaries if row.get("kind") == "bound_derivation"]
    post_bracket_failed = (_stage_fault(journal, [str(captures[-1].get("stage_id"))])
                           if len(captures) >= 2 else "not_run")
    bound_derivation_failed = _stage_fault(journal, [*derivations, *(item + ".corpus" for item in derivations)])
    fault_reasons = []
    if yield_status in {"EMPTY", "LOW"}:
        fault_reasons.append(f"yield_{yield_status.lower()}")
    if verdict == "CHAIN_STOPPED":
        fault_reasons.append(f"chain_stopped:{chain_stop.get('kind')}")
    if monitor.crash_loop:
        fault_reasons.append("monitor_crash_loop")
    # Sol review F1: a physics supervision step (monitor respawn, disk floor,
    # instrument liveness) that raised left that hazard unwatched for a while.
    for step in ("monitor", "disk", "monitor_liveness"):
        if supervision_faults.get(step):
            fault_reasons.append(f"supervision_failed:{step}")
    if post_bracket_failed is True:
        fault_reasons.append("post_bracket_failed")
    if bound_derivation_failed is True:
        fault_reasons.append("bound_derivation_failed")
    hazard["faults"] = {"post_bracket_failed": post_bracket_failed,
                        "bound_derivation_failed": bound_derivation_failed, "reasons": fault_reasons}
    stages = hazard["chain"]["stages"]
    hazard.update(verdict=verdict, stage_reached=stage_reached, aborted_reason=aborted_reason,
                  flags_emitted=list(window.flags), diagnostics=list(window.diagnostics), ended=stamp())
    try:
        _create_once(night / HAZARD_RESULT, hazard)
    except OSError as error:
        window.note(f"hazard result could not be written: {_error_text(error)}")
    if isinstance(yield_record.get("planned"), int):
        yield_line = (f"collected {yield_record['bundles_present']} of {yield_record['planned']} planned members "
                      f"({yield_record['succeeded']} succeeded; yield {yield_status})")
    else:
        yield_line = "collected an unknown number of the planned members (yield UNKNOWN)"
    report = _report(plan, base_exit, {
        "verdict": verdict, "stage_reached": stage_reached, "aborted_reason": aborted_reason,
        "chain_exit_code": exit_code,
        "termination_proven": proven, "census_count": census_count, "arm_verdicts": decision["verdicts"],
        "stages_total": len(stages), "stages_nonzero": sum(1 for row in stages if row.get("rc") not in (0, None)),
        "chain_stop": chain_stop.get("kind") if chain_stop is not None else None,
        "g10_ran": hazard["g10"].get("ran"), "g10_returncode": hazard["g10"].get("returncode"),
        "monitor_restarts": hazard["monitor"]["restarts"], "flags": sorted(set(window.flags)),
        "yield_line": yield_line, "yield_status": yield_status,
        "yield": {key: yield_record.get(key) for key in ("planned", "logged", "ok", "failed",
                                                          "bundles_present", "succeeded")}
                 | {"per_stage": [{key: row.get(key) for key in ("stage_id", "role", "planned", "present",
                                                                 "succeeded", "min_valid", "status", "rc")}
                                  for row in yield_record.get("per_stage") or []]},
        "fault": bool(fault_reasons), "fault_reasons": fault_reasons,
        "post_bracket_failed": post_bracket_failed, "bound_derivation_failed": bound_derivation_failed,
        "census_unmeasured": hazard_census.unmeasured_censuses},
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


def hold_monitors_after_chain(chain_returned: Mapping[str, Any], poll: Callable[[], Any], *,
                              hold_s: float | None = None) -> dict[str, Any]:
    """Wait until ``hold_s`` (MONITOR_POST_CHAIN_HOLD_S) has passed since the chain returned.

    ``chain_returned`` is the driver's stamp taken when the chain supervision
    returned, which is no earlier than the chain's exit, so a stop after the
    hold is at least ``hold_s`` after the exit. ``poll`` keeps the supervisors
    respawning about once a second while waiting. Returns the record kept in
    ``hazard_result.json`` under ``monitor_stop``.
    """

    hold = MONITOR_POST_CHAIN_HOLD_S if hold_s is None else float(hold_s)
    start_ns = int(chain_returned["monotonic_ns"])
    deadline_ns = start_ns + int(hold * 1e9)
    while True:
        remaining = (deadline_ns - time.monotonic_ns()) / 1e9
        if remaining <= 0:
            break
        poll()
        time.sleep(min(1.0, max(remaining, 0.0)))
    released = stamp()
    return {"chain_returned": dict(chain_returned), "hold_s": hold, "released": released,
            "released_after_chain_s": round((released["monotonic_ns"] - start_ns) / 1e9, 3)}


def _wait_supervised(process: Any, record: dict[str, Any], supervise: Callable[[], Any] | None) -> int:
    """``process.wait(timeout=G10_TIMEOUT_S)``, polling every G10_POLL_S and supervising between polls.

    A supervision pass that raises is recorded and the wait goes on; one that
    returns a stop (disk low, monitor outage: its flag is already written) is
    recorded and supervision ends, while G10, a diagnostic, runs to its end.
    """

    deadline = time.monotonic() + G10_TIMEOUT_S
    record["supervision_passes"] = 0
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise subprocess.TimeoutExpired(getattr(process, "args", "g10"), G10_TIMEOUT_S)
        try:
            return process.wait(timeout=max(0.001, min(G10_POLL_S, remaining)))
        except subprocess.TimeoutExpired:
            pass
        if supervise is not None:
            record["supervision_passes"] += 1
            try:
                stop = supervise()
            except Exception as error:  # noqa: BLE001 - supervision is a record here, never a stop
                record.setdefault("supervision_errors", []).append(_error_text(error))
                stop = None
            if stop is not None:
                record["supervision_stop"] = stop
                supervise = None


def _run_g10(window: _Window, night: Path, t_stream_max_s: float, *,
             supervise: Callable[[], Any] | None = None) -> dict[str, Any]:
    """Run G10 with its fixed argv in its own group; bound it; record the driver's view."""

    record: dict[str, Any] = {"schema": G10_DRIVER_SCHEMA, "ran": True, "started": stamp()}
    try:
        argv = [str(item) for item in window.seams.g10_argv(night, t_stream_max_s)]
        record["argv"] = argv
        with open(night / "g10.stdout.log", "ab") as out, open(night / "g10.stderr.log", "ab") as err:
            process = window.seams.popen(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                         start_new_session=True, close_fds=True)
        try:
            record["returncode"] = _wait_supervised(process, record, supervise)
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


def reap_orphan_monitor(night_dir: Path, *, identity: Callable[[int], Any] | None = None,
                        journal: str = MONITOR_JOURNAL) -> dict[str, Any] | None:
    """Dead-man helper: stop a monitor group the driver started and never proved stopped.

    ``journal`` names the supervision journal: the hazard monitor's by
    default, ``METER_JOURNAL`` for the wall meter. The group is signalled only
    when its leader is still the process the journal recorded (same start
    time), so a reused pid is never touched.
    """

    try:
        lines = (Path(night_dir) / journal).read_text(encoding="utf-8").splitlines()
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
        elif event.get("event") == "exit" and event.get("final") is True:
            # A final exit (the meter's "absent" exit 0) ended the recorded
            # process and nothing restarted it: there is no group to stop, and
            # its pid may since have been reused (Sol review F1).
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
