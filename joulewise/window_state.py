"""Read-only, shadow window classification. No existing writer imports this module.

Marker map (relative to custody unless prefixed ``night/``). Writers were read
on origin/main and origin/align/2026-11-08-v4-r11, without opening custody:

State             Files/facts implying it                 Writer
----------------  -------------------------------------  ----------------------------
Prepared          night_plan.json                         night_plan_writer.write_night_plan
Installed         both night labels observed loaded       night_agent_install transaction
DriverStarted     night/censuses.jsonl, receipt.json,      run_night.run/_run,
                  start_conditions.json, go_receipt.json,  b5.driver.run_hazard_night
                  arm_decision.json, hazard_result.json,
                  launch.pending or launch.resolved
RefusedPreChain   night/refusal.json, no chain.*           run_night._write_driver_refusal
ChainOpen         night/chain.started, no chain.exited     run_night._claim_chain_start
ChainExited       night/chain.exited                       run_night._record_chain_exit
ChainUnkilled     night/chain.unkilled, no chain.exited     run_night chain supervision
ResultWritten     night/result.json                       run_night._write_result
Delivered         night/courier.sent (or file-only plan)  courier; W1 _program_courier_delivery
DeadmanTail       result + courier failure or deadline    run_night._write_courier_outcome;
                                                          dead_man retries (no tail marker)
Stranded          delivered result + retained label       inferred; nobody writes this state
Uninstalled       terminal marker + both labels observed  night_agent_install uninstall;
                  absent on disk AND unloaded             no durable uninstall record
LaunchAbandoned   night/launch_abandoned.json              magistrate_watchdog.
                                                          _write_launch_abandoned
UNKNOWN           insufficient facts                      nobody

DriverStarted is evidence that the driver ran, not proof it is still alive.
Prepared does not require hazards/arm.json: that file is written during hazard
admission, not by preparation. We never open hazards/ or measurement artifacts.
Installed/Uninstalled cannot be established from custody files alone. Unknown
plist facts never count as false. Uninstalled describes the current observation,
not proof of a historical install. LaunchAbandoned requires its durable marker;
elapsed time alone is not its watchdog's process-census proof. ChainUnkilled
outranks result/delivery until chain.exited supplies later termination proof.

Completion follows run_night._completion_epoch_s on both refs:
t0_epoch_s + window_max_s + 300. With no plan timing, result.ended_epoch_s is
the fallback. Stranded requires delivery (or a declared file-only courier),
result, and either label loaded/on disk strictly after completion + 3600.
The audit's loaded-label invariant is reported even if delivery is still owed.

Only observe_night_dir performs filesystem I/O. It opens a fixed allowlist,
resolves ancestors once, refuses a symlink in the supplied root's last component
and all symlinks below the root, never enumerates a directory,
and never follows a path embedded in JSON. An explicit payload_path is permitted;
its sibling r1_slots.json is checked for existence only. Default payload locations
are night/r1_result.json and night/align-r1/r1_result.json (the W1 writer).
All present structural records must be objects with recognized field vocabularies.
Unknown extra keys are ignored, never copied into reports. Reasons are fixed
codes/field names, never arbitrary record text or measured values.

Optional caller declarations: plists maps the two LABELS to PlistFacts;
plan courier_mode="file-only" explicitly waives delivery. Neither writer has
such a plan declaration today; a courier's name or sent:true does not imply it.
W1 courier.delivery.json records a git-push (ref, commit, result_sha256), which
counts as recorded delivery, not mail. This shadow reader checks structure,
not remote availability or cryptographic binding. Legacy mail receipts may
record message_id or mail_message_id in courier.json/courier.delivery.json.

Audit 8.3 checks outside these facts (host settings/locks, watchdog dry run,
offload receipts/queue, series finality, harvest journals, analysis admission/
commit identity, kernel freshness) are deliberately not evaluated. Slots
equivalence is evaluated only when an R1 payload/slots location is observed.
Recorded chain_outcome is compared with the derived outcome when present;
COMPLETE matches both measured outcomes. Known measurement summary statuses
invalid, absent and unreadable are not complete. A complete payload with missing
slots fails. Plan timing also exposes silence strictly after t0 + 900 and an open
chain strictly after completion, without inventing a terminal state.
exit_contract words are complete, refused, failed, stopped, usage, hold, aborted. Undeclared
codes fail; unknown words are UNKNOWN. A nonzero code can never be measured,
even if a caller declares it complete. Payload completeness is structural only.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from dataclasses import dataclass, field
import enum
import json
import math
import os
from pathlib import Path
import stat
import time


class WindowOutcome(enum.Enum):
    MEASURED_OK = "MEASURED_OK"
    MEASURED_WITH_FLAGS = "MEASURED_WITH_FLAGS"
    CHAIN_FAILED = "CHAIN_FAILED"
    REFUSED_PRE_CHAIN = "REFUSED_PRE_CHAIN"
    ABORTED = "ABORTED"
    UNKNOWN = "UNKNOWN"


class WindowState(enum.Enum):
    PREPARED = "Prepared"
    INSTALLED = "Installed"
    DRIVER_STARTED = "DriverStarted"
    REFUSED_PRE_CHAIN = "RefusedPreChain"
    CHAIN_OPEN = "ChainOpen"
    CHAIN_EXITED = "ChainExited"
    CHAIN_UNKILLED = "ChainUnkilled"
    RESULT_WRITTEN = "ResultWritten"
    DELIVERED = "Delivered"
    DEADMAN_TAIL = "DeadmanTail"
    STRANDED = "Stranded"
    UNINSTALLED = "Uninstalled"
    LAUNCH_ABANDONED = "LaunchAbandoned"
    UNKNOWN = "UNKNOWN"


LABELS = ("com.joulewise.night", "com.joulewise.night.deadman")
VERDICTS = frozenset({"GO", "REFUSED", "ABORTED", "CHAIN_STOPPED", "REHEARSAL_ONLY"})
PAYLOAD_STATUSES = frozenset({"complete", "refused", "aborted", "running"})
MEASUREMENT_OUTCOMES = PAYLOAD_STATUSES | {"invalid", "absent", "unreadable"}
RECORDED_OUTCOMES = frozenset({"COMPLETE", "CHAIN_FAILED", "REFUSED_PRE_CHAIN", "ABORTED", "UNKNOWN"})
EXIT_WORDS = frozenset({"complete", "refused", "aborted", "failed", "stopped", "usage", "hold"})
DRIVER_MARKERS = frozenset({
    "censuses.jsonl", "receipt.json", "clean_dwell.output.txt", "clean_dwell.json",
    "start_conditions.json", "go_receipt.json", "go-census.json", "arm_decision.json",
    "hazard_result.json", "launch.pending", "launch.resolved", "network_time_off.json",
})
JSON_MARKERS = ("result.json", "refusal.json", "chain.started", "chain.exited",
                "chain.unkilled", "hazard_result.json", "launch_abandoned.json",
                "courier.json", "courier.delivery.json")
EXISTENCE_MARKERS = tuple(sorted(DRIVER_MARKERS - set(JSON_MARKERS))) + (
    "courier.sent", "courier.filed", "courier.lock", "courier.heartbeat")


@dataclass(frozen=True)
class PlistFacts:
    on_disk: bool | None = None
    loaded: bool | None = None

    def __post_init__(self):
        if any(value is not None and type(value) is not bool
               for value in (self.on_disk, self.loaded)):
            raise TypeError("plist facts must be True, False or None")


@dataclass(frozen=True)
class Observation:
    markers: frozenset[str] = frozenset()
    verdict: str | None = None
    chain_exit_code: int | None = None
    fault: bool | None = None
    fault_reasons: tuple[str, ...] = ()
    payload_status: str | None = None
    recorded_outcomes: tuple[str, ...] = ()
    slots_present: bool | None = None
    delivery_recorded: bool = False
    delivery_required: bool = True
    courier_failed: bool = False
    t0_epoch_s: float | None = None
    window_max_s: float | None = None
    completion_epoch_s: float | None = None
    plists: tuple[PlistFacts, PlistFacts] = (PlistFacts(), PlistFacts())
    # Values here are primitives/tuples, not raw JSON or mutable dictionaries.
    evidence: tuple[tuple[str, object], ...] = ()
    errors: tuple[str, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "markers", frozenset(self.markers))
        for name in ("fault_reasons", "recorded_outcomes", "plists", "evidence", "errors"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        if len(self.plists) != 2 or not all(isinstance(p, PlistFacts) for p in self.plists):
            raise TypeError("supply one PlistFacts for each of LABELS")


@dataclass
class OutcomeReport:
    outcome: WindowOutcome
    evidence: dict[str, object]
    reasons: list[str]
    violated_invariants: list[str]


@dataclass
class StateReport:
    state: WindowState
    outcome: OutcomeReport
    reasons: list[str] = field(default_factory=list)
    violated_invariants: list[str] = field(default_factory=list)


def invariant_go_started(o: Observation) -> str | None:
    """Audit 8.3: '`verdict == GO` implies `chain.started` exists.'"""
    if o.verdict == "GO" and "chain.started" not in o.markers:
        return "GO_WITHOUT_CHAIN_STARTED"
    return None


def invariant_exit_started(o: Observation) -> str | None:
    """Audit 8.3: '`chain.exited` implies `chain.started`.'"""
    if "chain.exited" in o.markers and "chain.started" not in o.markers:
        return "CHAIN_EXITED_WITHOUT_CHAIN_STARTED"
    return None


def invariant_nonzero_fault(o: Observation) -> str | None:
    """Audit 8.3: '`chain_exit_code not in (0, None)` implies `fault` is true.'"""
    if o.chain_exit_code not in (0, None) and o.fault is not True:
        return "NONZERO_EXIT_WITHOUT_FAULT"
    return None


def invariant_payload_exit(o: Observation) -> str | None:
    """Audit 8.3: 'Payload record `status == complete` if and only if chain exit is 0'."""
    if o.payload_status in MEASUREMENT_OUTCOMES and (
        (o.payload_status == "complete") != (o.chain_exit_code == 0)
    ):
        return "PAYLOAD_EXIT_MISMATCH"
    return None


def invariant_payload_slots(o: Observation) -> str | None:
    """Audit 8.3: 'chain exit is 0 if and only if the slots file exists.'"""
    if o.slots_present is not None and (o.chain_exit_code == 0) != o.slots_present:
        return "PAYLOAD_SLOTS_MISMATCH"
    return None


def invariant_courier_delivery(o: Observation) -> str | None:
    """Audit 8.3: '`courier.sent` implies a mail message id is recorded, or the plan declares a file-only courier.'

    W1's explicit git-push receipt is also recorded delivery (lane plan Q11).
    """
    if "courier.sent" in o.markers and o.delivery_required and not o.delivery_recorded:
        return "COURIER_SENT_WITHOUT_DELIVERY"
    return None


def invariant_courier_result(o: Observation) -> str | None:
    """Audit 4.1 illegal state: '`courier.sent` without `result.json`.'"""
    if "courier.sent" in o.markers and "result.json" not in o.markers:
        return "COURIER_SENT_WITHOUT_RESULT"
    return None


def invariant_stranded(o: Observation, now_epoch_s: float) -> str | None:
    """Audit 8.3: 'A night label loaded later than `completion epoch + 1 h` with `result.json` present is `STRANDED`.'

    The seat also includes retained on-disk plists in this retention check.
    """
    if ("result.json" in o.markers and o.completion_epoch_s is not None
            and now_epoch_s > o.completion_epoch_s + 3600
            and any(p.loaded is True or p.on_disk is True for p in o.plists)):
        return "LABEL_RETAINED_AFTER_COMPLETION"
    return None


def invariant_recorded_outcome(o: Observation, outcome: WindowOutcome) -> str | None:
    """W1's recorded chain outcome must agree with the shadow classification."""
    expected = ("COMPLETE" if outcome in {WindowOutcome.MEASURED_OK,
                                        WindowOutcome.MEASURED_WITH_FLAGS} else outcome.value)
    if any(word != expected for word in o.recorded_outcomes):
        return "RECORDED_OUTCOME_DISAGREES"
    return None


def invariant_no_night_record(o: Observation, now_epoch_s: float) -> str | None:
    """Known plan timing without any launch/terminal evidence has a 900 s dwell."""
    night_records = DRIVER_MARKERS | {"result.json", "refusal.json", "chain.started",
                                      "chain.exited", "chain.unkilled", "launch_abandoned.json"}
    if (o.t0_epoch_s is not None and o.window_max_s is not None
            and now_epoch_s > o.t0_epoch_s + 900 and not o.markers & night_records):
        return "NO_NIGHT_RECORD_AFTER_T0"
    return None


def invariant_chain_open(o: Observation, now_epoch_s: float) -> str | None:
    """An unclosed chain is overdue strictly after the completion epoch."""
    if ("chain.started" in o.markers and "chain.exited" not in o.markers
            and o.completion_epoch_s is not None and now_epoch_s > o.completion_epoch_s):
        return "CHAIN_OPEN_PAST_COMPLETION"
    return None


def _invariants(o: Observation, now_epoch_s: float | None = None,
                *, outcome: WindowOutcome | None = None) -> list[str]:
    checks = (invariant_go_started, invariant_exit_started, invariant_nonzero_fault,
              invariant_payload_exit, invariant_payload_slots, invariant_courier_delivery,
              invariant_courier_result)
    codes = [code for check in checks if (code := check(o)) is not None]
    if outcome is not None:
        code = invariant_recorded_outcome(o, outcome)
        if code:
            codes.append(code)
    if now_epoch_s is not None:
        for check in (invariant_stranded, invariant_no_night_record, invariant_chain_open):
            code = check(o, now_epoch_s)
            if code:
                codes.append(code)
    return codes


def _outcome(o: Observation, exit_contract: Mapping[int, str] | None = None) -> OutcomeReport:
    evidence = dict(o.evidence)
    evidence.update(markers=sorted(o.markers), verdict=o.verdict,
                    chain_exit_code=o.chain_exit_code, fault=o.fault,
                    fault_reason_count=len(o.fault_reasons), payload_status=o.payload_status)
    def report(outcome, *reasons):
        return OutcomeReport(outcome, evidence, list(reasons), _invariants(o, outcome=outcome))

    if exit_contract is not None:
        if not isinstance(exit_contract, Mapping) or any(type(k) is not int for k in exit_contract):
            raise TypeError("exit_contract must map integers to words")
        if any(not isinstance(word, str) or word not in EXIT_WORDS for word in exit_contract.values()):
            return report(WindowOutcome.UNKNOWN, "UNKNOWN_EXIT_CONTRACT_WORD")
        evidence["exit_contract"] = dict(exit_contract)
    if o.errors:
        return report(WindowOutcome.UNKNOWN, *o.errors)
    if "result.json" not in o.markers:
        return report(WindowOutcome.UNKNOWN, "MISSING_RESULT")
    if o.verdict not in VERDICTS:
        return report(WindowOutcome.UNKNOWN, "UNKNOWN_VERDICT")
    if invariant_go_started(o) or invariant_exit_started(o):
        return report(WindowOutcome.UNKNOWN, "CHAIN_START_NOT_PROVEN")
    if "chain.unkilled" in o.markers and "chain.exited" not in o.markers:
        return report(WindowOutcome.UNKNOWN, "CHAIN_TERMINATION_NOT_PROVEN")
    chain_markers = o.markers & {"chain.started", "chain.exited", "chain.unkilled"}
    if o.verdict == "REFUSED" and not chain_markers:
        if o.chain_exit_code is not None:
            return report(WindowOutcome.UNKNOWN, "PRE_CHAIN_REFUSAL_WITH_EXIT")
        return report(WindowOutcome.REFUSED_PRE_CHAIN, "ARM_REFUSED_BEFORE_CHAIN")
    if o.verdict == "ABORTED":
        return report(WindowOutcome.ABORTED, "DRIVER_ABORTED")
    if exit_contract is not None:
        word = exit_contract.get(o.chain_exit_code)
        if word == "aborted":
            return report(WindowOutcome.ABORTED, "DECLARED_ABORT")
        if word != "complete":
            return report(WindowOutcome.CHAIN_FAILED, "EXIT_NOT_DECLARED_COMPLETE")
    if o.chain_exit_code is not None and o.chain_exit_code != 0:
        return report(WindowOutcome.CHAIN_FAILED, "NONZERO_CHAIN_EXIT")
    if o.verdict in {"REFUSED", "CHAIN_STOPPED"}:
        return report(WindowOutcome.CHAIN_FAILED, "CHAIN_REFUSED_OR_STOPPED")
    if o.verdict == "REHEARSAL_ONLY":
        return report(WindowOutcome.UNKNOWN, "REHEARSAL_IS_NOT_MEASUREMENT")
    if o.chain_exit_code is None or "chain.exited" not in o.markers:
        return report(WindowOutcome.UNKNOWN, "CHAIN_EXIT_NOT_PROVEN")
    if o.payload_status is not None and o.payload_status not in MEASUREMENT_OUTCOMES:
        return report(WindowOutcome.UNKNOWN, "UNKNOWN_PAYLOAD_STATUS")
    if o.payload_status is not None and o.payload_status != "complete":
        return report(WindowOutcome.CHAIN_FAILED, "PAYLOAD_NOT_COMPLETE")
    if o.payload_status == "complete" and o.slots_present is False:
        return report(WindowOutcome.CHAIN_FAILED, "PAYLOAD_SLOTS_MISSING")
    if o.fault is True or o.fault_reasons or invariant_payload_slots(o):
        return report(WindowOutcome.MEASURED_WITH_FLAGS, "STRUCTURAL_FAULTS_PRESENT")
    return report(WindowOutcome.MEASURED_OK, "CHAIN_COMPLETED")


def derive_window_state(observation: Observation, now_epoch_s: float) -> StateReport:
    """Pure precedence over frozen facts; never probes paths, processes or clocks."""
    o = observation
    if not isinstance(o, Observation) or not _number(now_epoch_s):
        raise TypeError("supply an Observation and a finite numeric epoch")
    outcome = _outcome(o)
    invariants = _invariants(o, now_epoch_s, outcome=outcome.outcome)
    outcome.violated_invariants = list(invariants)
    markers = o.markers
    delivered = "courier.sent" in markers or not o.delivery_required
    terminal = bool(markers & {"result.json", "launch_abandoned.json"})
    removed = all(p.on_disk is False and p.loaded is False for p in o.plists)
    if "chain.unkilled" in markers and "chain.exited" not in markers:
        state = WindowState.CHAIN_UNKILLED
    elif "chain.started" in markers and "chain.exited" not in markers:
        state = WindowState.CHAIN_OPEN
    elif terminal and removed:
        state = WindowState.UNINSTALLED
    elif "result.json" in markers:
        if delivered and invariant_stranded(o, now_epoch_s):
            state = WindowState.STRANDED
        elif delivered:
            state = WindowState.DELIVERED
        elif (o.courier_failed or "courier.filed" in markers
              or (o.completion_epoch_s is not None and now_epoch_s >= o.completion_epoch_s)):
            state = WindowState.DEADMAN_TAIL
        else:
            state = WindowState.RESULT_WRITTEN
    elif "chain.exited" in markers:
        state = WindowState.CHAIN_EXITED
    elif "refusal.json" in markers:
        state = WindowState.REFUSED_PRE_CHAIN
    elif markers & DRIVER_MARKERS:
        state = WindowState.DRIVER_STARTED
    elif "launch_abandoned.json" in markers:
        state = WindowState.LAUNCH_ABANDONED
    elif all(p.loaded is True for p in o.plists):
        state = WindowState.INSTALLED
    elif "night_plan.json" in markers:
        state = WindowState.PREPARED
    else:
        state = WindowState.UNKNOWN
    return StateReport(state, outcome, [*o.errors, "STATE_FROM_OBSERVED_MARKERS"], invariants)


def _number(value: object) -> bool:
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def observe_night_dir(custody_root, *, plists=None, payload_path=None,
                      _night_only: bool = False) -> Observation:
    """Observe structure without launchctl. Paths in records are never followed.

    plists is a mapping of LABELS to PlistFacts; missing labels stay unobserved.
    _night_only is used by window_outcome to read exactly its directory, no plan.
    Missing optional records are normal. Present unreadable/invalid inputs are
    errors, as are explicitly requested but missing payloads. No raw values or
    exception messages are returned in diagnostics.
    """
    root = Path(custody_root).absolute()
    if plists is not None and (not isinstance(plists, Mapping)
                              or any(k not in LABELS for k in plists)
                              or any(not isinstance(v, PlistFacts) for v in plists.values())):
        raise TypeError("plists must map LABELS to PlistFacts")
    plist_facts = tuple((plists or {}).get(label, PlistFacts()) for label in LABELS)
    markers, errors, evidence = set(), [], {}
    prefix = "" if _night_only else "night/"

    def open_directory(path):
        # macOS /var and /tmp are legitimate symlinked ancestors. Resolve once,
        # but never accept a symlink naming this root, including a racing swap.
        before = os.lstat(path)
        if not stat.S_ISDIR(before.st_mode):
            raise ValueError("root must be a directory, not a symlink")
        resolved = os.path.realpath(path)
        fd = os.open(resolved, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            after = os.fstat(fd)
            current = os.lstat(path)
            if (not stat.S_ISDIR(current.st_mode)
                    or (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino)
                    or (current.st_dev, current.st_ino) != (after.st_dev, after.st_ino)):
                raise ValueError("root changed during resolution")
            return fd
        except BaseException:
            os.close(fd)
            raise

    def read_at(base_fd, relative, *, parse=True, key=None):
        name = key or relative.removeprefix(prefix)
        fd = os.dup(base_fd)
        try:
            parts = relative.split("/")
            for part in parts[:-1]:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd)
                fd = child
            info = os.stat(parts[-1], dir_fd=fd, follow_symlinks=False)
            markers.add(name)
            if not stat.S_ISREG(info.st_mode):
                errors.append(name + ":NOT_REGULAR_FILE")
                return None
            if not parse:
                return True
            file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            try:
                if not stat.S_ISREG(os.fstat(file_fd).st_mode):
                    errors.append(name + ":NOT_REGULAR_FILE")
                    return None
                with os.fdopen(file_fd, "rb", closefd=False) as stream:
                    raw = stream.read(4 * 1024 * 1024 + 1)
            finally:
                os.close(file_fd)
            if len(raw) > 4 * 1024 * 1024:
                errors.append(name + ":RECORD_TOO_LARGE")
                return None
            value = json.loads(raw, object_pairs_hook=unique_object,
                               parse_constant=invalid_constant)
            if not isinstance(value, dict):
                errors.append(name + ":NOT_OBJECT")
                return None
            return value
        except FileNotFoundError:
            if name in markers:
                errors.append(name + ":DISAPPEARED_DURING_READ")
            return None
        except (OSError, ValueError, UnicodeError, RecursionError, OverflowError):
            errors.append(name + ":UNREADABLE_OR_INVALID")
            return None
        finally:
            os.close(fd)

    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate key")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError("nonfinite JSON")

    def field_value(doc, key, source, valid, *, required=False):
        if key not in doc:
            if required:
                errors.append(source + "." + key + ":MISSING")
            return None
        value = doc[key]
        if not valid(value):
            errors.append(source + "." + key + ":UNKNOWN_OR_INVALID")
            return None
        # Do not retain arbitrary fault strings, identifiers or measurements.
        return value

    try:
        root_fd = open_directory(root)
    except (OSError, ValueError):
        return Observation(errors=("DIRECTORY_UNREADABLE_OR_UNSAFE",), plists=plist_facts)
    documents = {}
    payloads = []
    slots_seen = None
    try:
        if not _night_only:
            documents["night_plan.json"] = read_at(root_fd, "night_plan.json", key="night_plan.json")
        for name in JSON_MARKERS:
            documents[name] = read_at(root_fd, prefix + name, key=name)
        for name in EXISTENCE_MARKERS:
            read_at(root_fd, prefix + name, parse=False, key=name)
        if payload_path is None:
            for location in ("r1_result.json", "align-r1/r1_result.json"):
                doc = read_at(root_fd, prefix + location, key=location)
                slots = read_at(root_fd, prefix + location.replace("r1_result.json", "r1_slots.json"),
                                parse=False, key=location.replace("r1_result.json", "r1_slots.json"))
                if location in markers or slots:
                    payloads.append((location, doc))
                    slots_seen = bool(slots) if slots_seen is None else slots_seen and bool(slots)
        else:
            explicit = Path(payload_path).absolute()
            try:
                payload_fd = open_directory(explicit.parent)
            except (OSError, ValueError):
                errors.append("payload:UNREADABLE_OR_UNSAFE")
            else:
                try:
                    doc = read_at(payload_fd, explicit.name, key="payload")
                    if "payload" not in markers:
                        errors.append("payload:MISSING")
                    payloads.append(("payload", doc))
                    slots_seen = bool(read_at(payload_fd, "r1_slots.json", parse=False, key="r1_slots.json"))
                finally:
                    os.close(payload_fd)
    finally:
        os.close(root_fd)

    verdicts, exits, faults, statuses, recorded_outcomes = [], [], [], [], []
    fault_count = 0
    for name in ("result.json", "hazard_result.json"):
        doc = documents.get(name)
        if doc is None:
            continue
        verdict = field_value(doc, "verdict", name, lambda v: isinstance(v, str) and v in VERDICTS, required=True)
        if verdict is not None:
            verdicts.append(verdict)
            evidence[name + ".verdict"] = verdict
        source = doc.get("chain", {}) if name == "hazard_result.json" else doc
        if not isinstance(source, dict):
            errors.append(name + ".chain:NOT_OBJECT")
            source = {}
        key = "exit_code" if name == "hazard_result.json" else "chain_exit_code"
        exit_code = field_value(source, key, name, lambda v: v is None or type(v) is int,
                                required=name == "result.json")
        if key in source:
            exits.append(exit_code)
            evidence[name + "." + key] = exit_code
        flag = field_value(doc, "fault", name, lambda v: type(v) is bool)
        if flag is not None:
            faults.append(flag)
        fault_doc = doc.get("faults", {})
        if not isinstance(fault_doc, dict):
            errors.append(name + ".faults:NOT_OBJECT")
            fault_doc = {}
        for container, key in ((doc, "fault_reasons"), (fault_doc, "reasons")):
            reasons = field_value(container, key, name, lambda v: isinstance(v, list)
                                  and all(isinstance(r, str) and bool(r) for r in v))
            if reasons is not None:
                fault_count += len(reasons)
        status = field_value(doc, "measurement_outcome", name,
                             lambda v: v is None or isinstance(v, str) and v in MEASUREMENT_OUTCOMES)
        if status is not None:
            statuses.append(status)
        recorded = field_value(doc, "chain_outcome", name,
                               lambda v: isinstance(v, str) and v in RECORDED_OUTCOMES)
        if recorded is not None:
            recorded_outcomes.append(recorded)
            evidence[name + ".chain_outcome"] = recorded
    exited = documents.get("chain.exited")
    if exited is not None:
        code = field_value(exited, "exit_code", "chain.exited", lambda v: v is None or type(v) is int, required=True)
        exits.append(code)
        evidence["chain.exited.exit_code"] = code
    for name, doc in payloads:
        if doc is None:
            errors.append(name + ":PAYLOAD_UNAVAILABLE")
        else:
            status = field_value(doc, "status", name, lambda v: isinstance(v, str) and v in PAYLOAD_STATUSES, required=True)
            if status is not None:
                statuses.append(status)
                evidence[name + ".status"] = status
    for values, code in ((verdicts, "CONFLICTING_VERDICTS"), (exits, "CONFLICTING_CHAIN_EXITS"),
                         (statuses, "CONFLICTING_PAYLOAD_STATUSES")):
        if len(set(values)) > 1:
            errors.append(code)

    plan = documents.get("night_plan.json") or {}
    t0 = field_value(plan, "t0_epoch_s", "night_plan.json", _number, required="night_plan.json" in markers)
    span = field_value(plan, "window_max_s", "night_plan.json", lambda v: _number(v) and v > 0, required="night_plan.json" in markers)
    mode = field_value(plan, "courier_mode", "night_plan.json", lambda v: v in ("file-only", "mail", "git-push"))
    ended = field_value(documents.get("result.json") or {}, "ended_epoch_s", "result.json", _number)
    completion = t0 + span + 300 if t0 is not None and span is not None else ended
    if completion is not None and not _number(completion):
        errors.append("completion_epoch_s:INVALID_SUM")
        completion = None
    courier = documents.get("courier.json") or {}
    sent = field_value(courier, "sent", "courier.json", lambda v: type(v) is bool)
    delivery = documents.get("courier.delivery.json") or {}
    recorded = False
    for name, doc in (("courier.json", courier), ("courier.delivery.json", delivery)):
        for key in ("message_id", "mail_message_id"):
            message_id = field_value(doc, key, name, lambda v: isinstance(v, str) and bool(v.strip()))
            recorded = recorded or message_id is not None
    if "transport" in delivery:
        transport = field_value(delivery, "transport", "courier.delivery.json", lambda v: v in ("git-push", "mail", "file"))
        if transport == "git-push":
            def hex_string(value, sizes):
                return isinstance(value, str) and len(value) in sizes and all(c in "0123456789abcdef" for c in value)
            commit = field_value(delivery, "commit", "courier.delivery.json", lambda v: hex_string(v, (40, 64)), required=True)
            digest = field_value(delivery, "result_sha256", "courier.delivery.json", lambda v: hex_string(v, (64,)), required=True)
            ref = field_value(delivery, "ref", "courier.delivery.json", lambda v: isinstance(v, str) and v.startswith("refs/heads/night-results/") and len(v) > 25, required=True)
            recorded = recorded or all(v is not None for v in (commit, digest, ref))
    evidence.update(delivery_recorded=recorded, delivery_required=mode != "file-only",
                    slots_present=slots_seen, completion_epoch_s=completion)
    return Observation(
        markers=frozenset(markers), verdict=verdicts[0] if verdicts else None,
        chain_exit_code=exits[0] if exits else None, fault=any(faults) if faults else None,
        fault_reasons=tuple("recorded_fault" for _ in range(fault_count)),
        payload_status=statuses[0] if statuses else None, slots_present=slots_seen,
        recorded_outcomes=tuple(recorded_outcomes),
        delivery_recorded=recorded, delivery_required=mode != "file-only",
        courier_failed=sent is False, t0_epoch_s=t0, window_max_s=span,
        completion_epoch_s=completion, plists=plist_facts,
        evidence=tuple(evidence.items()), errors=tuple(dict.fromkeys(errors)))


def window_outcome(night_dir, *, exit_contract=None, payload_path=None) -> OutcomeReport:
    """Classify only the supplied night records, plus an explicit payload if given."""
    return _outcome(observe_night_dir(night_dir, payload_path=payload_path, _night_only=True), exit_contract)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read-only, structure-only shadow window state")
    parser.add_argument("custody_root", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = derive_window_state(observe_night_dir(args.custody_root), time.time())
    result = {"state": report.state.value, "outcome": report.outcome.outcome.value,
              "violated_invariants": report.violated_invariants,
              "reasons": report.outcome.reasons}
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"state={result['state']} outcome={result['outcome']}")
        print("violated_invariants=" + ",".join(report.violated_invariants))
        print("reasons=" + ",".join(report.outcome.reasons))
    if report.state is WindowState.UNKNOWN or report.outcome.outcome is WindowOutcome.UNKNOWN:
        return 2
    return 0 if report.outcome.outcome is WindowOutcome.MEASURED_OK else 1


if __name__ == "__main__":
    raise SystemExit(main())
