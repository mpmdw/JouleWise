"""Evaluation and custody authentication for unattended quiet-machine nights.

Callers provide machine observations through :class:`Probes`. Pack C1/C2
re-read plan-bound custody records and replay the exact supplied ARM path.
Result records belong to the driver, which defines and validates ``result.json``.

A ruled registration (``RULED_REGISTRATIONS``) pins PROTOCOL VALUES and, when
``binds_chain``, the zsh chain source named by ``EVIDENCE_CHAIN_PATH``. It
pins no Python: the harness modules are pinned per plan by ``measurement_head``
and the plan's evidence manifest, so a cured executor changes the manifest
digests, never the registration digest.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import uuid
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, Protocol

from joulewise import corecaptured_loop
from joulewise.night_kinds import NIGHT_KINDS, kind_row


SCHEMA = "joulewise.unattended_night_receipt.v2"
PLAN_SCHEMA = "joulewise.night_plan.v2"
PLAN_SCHEMA_VERSION = 2
PACK_PLAN_SCHEMA = "joulewise.night_plan.v3"
PACK_PLAN_SCHEMA_VERSION = 3
QUIET_PLAN_SCHEMA = "joulewise.night_plan.v4"
QUIET_PLAN_SCHEMA_VERSION = 4
QUIET_RECEIPT_SCHEMA = "joulewise.unattended_night_receipt.v3"
RECEIPT_CLASSES = (
    "DIAGNOSTIC_NO_PACK",
    "REHEARSAL_STUB",
    "TRANSACTION_PACK",
)
# 2026-09-05: D-165 v2 relabel supersedes the v1 registration digest
# 1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b (bytes retained in Git history).
D166_REGISTRATION_SHA256 = (
    "dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265"
)
# Tracked file whose bytes are canonical_json_bytes(dominance_criterion_registration());
# a night plan's registration_path points at it (repo-relative or absolute).
D166_REGISTRATION_PATH = (
    "configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json"
)
# 2026-09-22 (A269 cold gate 10 Q2(a), synthesised in 15): the current pilot
# registration is v2.  It adds ``slot_pitch_s`` (the schedule pitch the cure-2
# cadence reads), ``start_drift_abort_s`` (the in-chain abort threshold) and
# the two attestation exclusion reasons A267 Part 3 emits.  A registration
# pins PROTOCOL VALUES and the zsh chain source only (``chain_source_sha256``
# binds EVIDENCE_CHAIN_PATH, never a Python module): the cured Python is
# pinned per plan by ``measurement_head`` and the plan's evidence manifest
# (``quiet_predicate_campaign.MANIFEST_PATHS``), not by this digest.
# 2026-09-23 (cold gate QPE01-DAEMON-CONTAMINATION-01, rulings 10 and 31;
# syntheses 15, 25 and 35): the current pilot registration is v3.  It adds the
# `non_observer_process_busy` exclusion and its per-envelope integral, the
# `t0_non_observer_share_max` gate share, and the corrected `observer_floor`
# (whole-envelope accounting over the collector's own span, with the v2
# statistic named in its supersession note).
QPE01_PILOT_REGISTRATION_PATH = kind_row("quiet_predicate_evidence").protocol_path
QPE01_PILOT_REGISTRATION_SHA256 = "69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616"
# v2's bytes stay in the table as ruled history, for the same reason v1's do:
# the table is KEYED by digest, so re-pointing the constant above would carry
# the v2 entry away with it.  Its own literal keeps the 2026-09-22 night's
# registration readable, and `superseded_by` refuses any new arm against it.
QPE01_PILOT_REGISTRATION_V2_SHA256 = "2c5392401a7956dfbb30f316a084541e0f53f214a4ce98c7d56d595ddb2779f1"
# v1's bytes (``pilot_protocol_v1.json``, never modified) stay in the table as
# ruled history.  The table is KEYED by digest, so re-pointing the constant
# above would have carried the v1 entry away with it; the v1 digest is
# therefore repeated as its own literal and its entry carries
# ``superseded_by``, which the armability readers refuse.
QPE01_PILOT_REGISTRATION_V1_SHA256 = "f59804a9a28b2145f7bb8e91a8f0fe11b21ae6728cee70d8e943fe52a46da6f6"
EVIDENCE_CHAIN_PATH = kind_row("quiet_predicate_evidence").chain_source_path
# Amended only by cold-gate ruling; each entry names its authority ("ruling",
# surfaced in the receipt) and the tracked records that hold it ("records":
# repo-relative paths, optionally "#<heading id>" inside a decision log;
# tests/test_night_gate.py asserts each exists — ruling 61a S4).  A superseded
# entry additionally carries "superseded_by": the digest that replaced it.
# The A269 gate record itself (docs/process_traces/2026-09-22-activation-e4b4ead6/
# 03-coldgate-packet-a269-start-drift/10-coldgate-fable-ruling.md) joins v2's
# records when the magistrate commits that activation's trace; the records
# below are the tracked ones that exist at this head.
RULED_REGISTRATIONS = {
    D166_REGISTRATION_SHA256: {"label": "D-166 dominance criterion", "ruling": "D-165/D-166", "binds_chain": False,
        "records": ("docs/decision_log.md#D-165", "docs/decision_log.md#D-166")},
    QPE01_PILOT_REGISTRATION_V1_SHA256: {"label": "QPE-01 idle-variance pilot protocol v1",
        "ruling": "cold gate 10 Q1/Q2 (2026-09-19); sizing ruling 46b", "binds_chain": True,
        "superseded_by": QPE01_PILOT_REGISTRATION_V2_SHA256,
        "records": ("docs/process_traces/2026-09-19-activation-d0b83820/10-coldgate-packet-stage-a-executor/10-coldgate-fable-ruling.md",
                    "docs/process_traces/2026-09-19-activation-d0b83820/46b-ruling-stage-a-seat-r3.md")},
    QPE01_PILOT_REGISTRATION_V2_SHA256: {"label": "QPE-01 idle-variance pilot protocol v2 (A269 gate 2026-09-22)",
        "ruling": "cold gate 10 Q1/Q2 (2026-09-19); adjudication 10a; sizing ruling 46b; "
                  "A269 cold gate 10 (2026-09-22) Q1(c)/Q2(a)/Q3", "binds_chain": True,
        "superseded_by": QPE01_PILOT_REGISTRATION_SHA256,
        "records": ("docs/process_traces/2026-09-19-activation-d0b83820/10-coldgate-packet-stage-a-executor/10-coldgate-fable-ruling.md",
                    "docs/process_traces/2026-09-19-activation-d0b83820/46b-ruling-stage-a-seat-r3.md",
                    "docs/process_traces/2026-09-22-activation-d9990b3c/02-a269-start-drift-diagnosis.md",
                    "docs/process_traces/2026-09-22-activation-d9990b3c/01-coldgate-packet-a267-clock-discipline-anchor/14-coldgate-fable-rebuttal-ruling.md")},
    QPE01_PILOT_REGISTRATION_SHA256: {
        "label": "QPE-01 idle-variance pilot protocol v3 (QPE01-DAEMON-CONTAMINATION-01 gate 2026-09-23)",
        "ruling": "cold gate 10 Q1/Q2 (2026-09-19); adjudication 10a; sizing ruling 46b; "
                  "A269 cold gate 10 (2026-09-22) Q1(c)/Q2(a)/Q3; "
                  "QPE01-DAEMON-CONTAMINATION-01 ruling 10 (2026-09-23) Q1(c)/Q2/Q3(a), "
                  "ruling 31 reporting limbs as adjudicated by synthesis 35", "binds_chain": True,
        "records": ("docs/process_traces/2026-09-19-activation-d0b83820/10-coldgate-packet-stage-a-executor/10-coldgate-fable-ruling.md",
                    "docs/process_traces/2026-09-19-activation-d0b83820/46b-ruling-stage-a-seat-r3.md",
                    "docs/process_traces/2026-09-22-activation-a022aecc/03-coldgate-packet-daemon-contamination/10-coldgate-fable-ruling.md",
                    "docs/process_traces/2026-09-22-activation-a022aecc/03-coldgate-packet-daemon-contamination/15-magistrate-synthesis.md",
                    "docs/process_traces/2026-09-22-activation-a022aecc/03-coldgate-packet-daemon-contamination/25-magistrate-synthesis-round-2.md",
                    "docs/process_traces/2026-09-22-activation-a022aecc/03-coldgate-packet-daemon-contamination/31-coldgate-fable-observer-floor-design-ruling.md",
                    "docs/process_traces/2026-09-22-activation-a022aecc/03-coldgate-packet-daemon-contamination/35-magistrate-synthesis-round-3.md")},
}


def armable_registration(registration_sha256):
    """The ruled entry for a digest, or None when it can never be armed again.

    A superseded registration stays in the table as history but is refused
    here: no night may be armed against protocol values a later cold gate
    replaced (A269 ruling 10 Q2; refuter 11 on the table's digest key).
    """

    entry = RULED_REGISTRATIONS.get(registration_sha256)
    if entry is None or entry.get("superseded_by"):
        return None
    return entry


def chain_literal(text, name):
    """One shell literal, never expansion or execution of a wrapper."""
    import shlex
    matches = re.findall(r"^export " + re.escape(name) + r"=(.*)$", text, re.MULTILINE)
    if len(matches) != 1:
        raise ValueError(name + " must be one literal export in the pinned chain")
    words = shlex.split(matches[0])
    if len(words) != 1 or any(c in words[0] for c in "$`\n\r"):
        raise ValueError(name + " is not a literal")
    return words[0]


def probe_payload_kind(text):
    """The shared worker/installer discriminant; absence preserves calibration."""
    declarations = re.findall(r"^\s*export\s+NIGHT_PAYLOAD_KIND\b.*$", text, re.MULTILINE)
    if not declarations:
        return kind_row("calibration").kind
    try:
        if (len(declarations) != 1 or
                re.search(r"^\s*export\s+CALIBRATION_LEDGER\b", text, re.MULTILINE)):
            raise ValueError("ambiguous")
        kind = chain_literal(text, "NIGHT_PAYLOAD_KIND")
        if kind not in NIGHT_KINDS or not NIGHT_KINDS[kind].payload_kind:
            raise ValueError("ambiguous")
    except ValueError as exc:
        raise ValueError("probe payload kind ambiguous") from exc
    return kind
# Brackets preserve agent matches but exclude peer pgrep argv: overlapping
# driver/chain censuses self-matched and aborted the 2026-09-20 pilot night.
AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "[c]odex|[c]laude|[t]3")

PMSET_BATT_ARGV = ("/usr/bin/pmset", "-g", "batt")
PMSET_GENERAL_ARGV = ("/usr/bin/pmset", "-g")
HID_IDLE_ARGV = (
    "/usr/bin/defaults",
    "-currentHost",
    "read",
    "com.apple.screensaver",
    "idleTime",
)
LOAD_AVG_ARGV = ("/usr/sbin/sysctl", "-n", "vm.loadavg")
THERMAL_ARGV = ("/usr/bin/pmset", "-g", "therm")
BOOT_SESSION_ARGV = ("/usr/sbin/sysctl", "-n", "kern.bootsessionuuid")

LOAD_MAX = 2.0
# Cold gate 10 QPE01-DAEMON-CONTAMINATION-01 (2026-09-23) Q2(i).  The night of
# 2026-09-22 21:00 ran twelve envelopes while `fseventsd` held a full busy core
# in every sample, and the gate admitted it: the load average was 1.03, under
# LOAD_MAX, because a one-minute host-wide mean cannot name a process.  The
# cure is a PER-PROCESS predicate over one interval observation.  0.5 busy
# cores is five times the largest single-sample transient seen outside the
# daemons on either archived night (`corespotlightd` 0.104) and half the
# runaway signature (1.0); anything admitted below it is caught per envelope by
# the registration's `non_observer_process_busy` integral.  The bar is a GATE
# predicate, not a registration field, so it binds v2 and v3 plans alike.
T0_NON_OBSERVER_SHARE_MAX = 0.5
NON_OBSERVER_OBSERVATION_INTERVAL_S = 30
NON_OBSERVER_EXCLUSION = "non_observer_process_busy"
PLAN_MAX_AGE_S = 36 * 60 * 60
# Acceptance ruling v2.1 R16 (docs/process_traces/2026-09-25-activation-152c9255/
# 05-coldgate-packet-acc2/30-addendum/21-coldgate-fable-acc2-addendum-ruling.md
# §5 R16): newly authored plans must use the dedicated measurement custody.
MEASUREMENT_ROOT_CUSTODY_CUTOFF_EPOCH_S = 1790340000
MEASUREMENT_ROOT_CUSTODY_ROOT = Path("/Users/edr/night-custody/measurement")

NIGHT_GATE_REASON_CODES = frozenset(
    {
        "night_refused_agent_present",
        "night_refused_not_quiet",
        "night_refused_bind_expired",
        "night_refused_hid_idle",
        "night_refused_boot_clock",
        "night_refused_registration",
        "night_window_expired",
        "night_plan_stale",
        "night_plan_malformed",
        "measurement_root_outside_custody",
        "night_chain_digest_mismatch",
        "launch_go_receipt_missing",
        "launch_go_receipt_invalid",
        "night_refused_class_unbuilt",
        "night_receipt_class_invalid",
        "night_probe_error",
    }
)

# Codes the DRIVER (scripts/run_night.py) emits. Bind expiry is the one shared
# admission code: the driver supervises binding and writes a v3 gate receipt.
# They live here so the registry has one home (ruling R-8).
# Cold gate coldgate-e10 (2026-09-01) d.3 and the Opus
# refuter's once-only finding are their forcing problems.
NIGHT_DRIVER_REASON_CODES = frozenset(
    {
        "night_refused_bind_expired",   # v4 bind deadline expired; D-182 successor route
        "night_aborted_agent_present",   # census hit while the chain ran; chain group terminated
        "night_chain_already_started",   # O_EXCL claim on chain.started failed: never start the chain twice (D-078)
        "night_calibration_refused",     # typed reservation/writer refusal, including invalid transport documents
        "night_chain_alive",             # dead-man refused: the chain has not exited, so no agent may start
        "night_chain_launch_failed",     # chain Popen failed after the once-only start claim
        "night_courier_running",          # dead-man found a fresh courier lock owned by a live process
        "night_courier_unavailable",      # the stamped courier binary is missing or not executable
        "night_plan_overruns_deadman",   # t0 + window_max_s + courier deadline is not before the dead-man hour
        "night_record_exists",            # a write-once record proves this night was already invoked
        "night_window_exceeded",  # driver wall-clock deadline: chain terminated after the exclusive window end plus shutdown grace
        NON_OBSERVER_EXCLUSION,  # two consecutive envelopes lost to a busy non-observer process; the chain ends (cold gate 10, 2026-09-23, Q2)
    }
)
if NIGHT_GATE_REASON_CODES & NIGHT_DRIVER_REASON_CODES != {"night_refused_bind_expired"}:
    raise RuntimeError("night gate and driver reason-code registries overlap")

# First-refusal precedence.  Probe failures use ``night_probe_error`` at the
# position of the probe that failed rather than forming a separate phase.
ORDER = (
    "night_window_expired",
    "night_plan_stale",
    "night_refused_agent_present",
    "night_chain_digest_mismatch",
    "night_refused_class_unbuilt",
    "night_refused_hid_idle",
    "night_refused_not_quiet",
    "night_refused_boot_clock",
    "night_refused_registration",
)

_PLAN_KEYS = {
    "schema",
    "schema_version",
    "plan_id",
    "receipt_class",
    "t0_epoch_s",
    "window_max_s",
    "authored_epoch_s",
    "repo_head",
    "measurement_root",
    "measurement_head",
    "chain_path",
    "chain_sha256_path",
    "custody_root",
    "registration_path",
}
_PACK_NIGHT_KEYS = {
    "pack_id", "pack_root", "pack_sha256", "attempt_ordinal",
    "authorization_record", "confirmation_record",
}
_PACK_RECORD_KEYS = {"path", "sha256"}
_RECEIPT_KEYS = {
    "schema",
    "receipt_class",
    "plan_id",
    "verdict",
    "conditions",
    "refusal",
    "authored_monotonic_ns",
}
_QUIET_RECEIPT_KEYS = {
    "quiet_admission", "bind_deadline_epoch_s", "go_epoch_s", "samples_total",
    "samples_quiet_run_at_go", "quiet_samples_sha256", "quiet_samples_lines",
    "top_consumers_at_decision", "load_avg_diagnostic",
    "admission_is_capture_evidence",
}
_CONDITION_KEYS = {"condition_id", "status", "basis", "evidence", "measured"}
_REFUSAL_KEYS = {"reason", "detail", "evidence"}
_PROBE_RESULT_KEYS = {"argv", "exit_code", "stdout", "stderr", "monotonic_ns"}
_CONDITION_IDS = ("C1", "C2", "C3", "C4", "C5")
_STATUSES = {"PASS", "FAIL", "NOT_APPLICABLE"}
_VERDICTS = {"GO", "REFUSED", "REHEARSAL_ONLY"}
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_HEAD_RE = re.compile(r"[0-9a-f]{40}")
_DISPLAY_SLEEP_RE = re.compile(r"^\s*displaysleep\s+(\S+)", re.MULTILINE)
_LOAD_AVG_RE = re.compile(r"^\{ (\d+\.\d+) (\d+\.\d+) (\d+\.\d+) \}$")
_THERMAL_RE = re.compile(r"CPU_Speed_Limit\s*=\s*(\d+)\s*$")


class ProbeError(RuntimeError):
    """A machine probe could not produce a trustworthy observation."""


class PlanError(ValueError):
    """A night plan is not structurally usable."""

    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(detail)
        self.reason = reason
        self.detail = detail


@dataclass(frozen=True)
class ProbeResult:
    argv: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str
    monotonic_ns: int


@dataclass(frozen=True)
class Probes:
    run: Callable[[tuple[str, ...]], ProbeResult]
    now_epoch_s: Callable[[], float]
    monotonic_ns: Callable[[], int]
    read_text: Callable[[str], str]
    checkout_head: Callable[[], str]
    measurement_head: Callable[[str], str]
    # The non-observer machine-state observation (cold gate 10
    # QPE01-DAEMON-CONTAMINATION-01, 2026-09-23, Q2(i)).  It is not one argv,
    # so it cannot travel through ``run``: it is a whole
    # ``quiet_admission.sample_interval`` worker that spends
    # ``NON_OBSERVER_OBSERVATION_INTERVAL_S`` seconds watching the machine.
    # ``None`` means the production sampler; a caller that must not touch the
    # machine (every test) supplies its own observation here.
    observe_interval: Callable[[], Mapping[str, object]] | None = None


class CensusProbes(Protocol):
    """Narrow census dependency, isolated from unrelated plan-pin probes."""

    run: Callable[[tuple[str, ...]], ProbeResult]
    monotonic_ns: Callable[[], int]


@dataclass(frozen=True)
class NightPlan:
    plan_id: str
    receipt_class: str
    t0_epoch_s: float
    window_max_s: int
    authored_epoch_s: float
    repo_head: str
    measurement_root: str
    measurement_head: str
    chain_path: str
    chain_sha256_path: str
    custody_root: str
    registration_path: str | None
    pack_night: dict[str, object] | None = None
    quiet_admission: dict[str, object] | None = None

    @staticmethod
    def from_mapping(value: Mapping[str, object]) -> "NightPlan":
        if not isinstance(value, Mapping):
            raise PlanError("night_plan_malformed", "plan must be an object")
        keys = set(value)
        is_pack = value.get("receipt_class") == "TRANSACTION_PACK"
        is_quiet = value.get("schema") == QUIET_PLAN_SCHEMA and not is_pack
        expected_keys = _PLAN_KEYS | {"pack_night"} if is_pack else _PLAN_KEYS
        if is_quiet:
            expected_keys = expected_keys | {"quiet_admission"}
        expected_schema = PACK_PLAN_SCHEMA if is_pack else PLAN_SCHEMA
        expected_version = PACK_PLAN_SCHEMA_VERSION if is_pack else PLAN_SCHEMA_VERSION
        if is_quiet:
            expected_schema, expected_version = QUIET_PLAN_SCHEMA, QUIET_PLAN_SCHEMA_VERSION
        if keys != expected_keys:
            missing = sorted(repr(item) for item in expected_keys - keys)
            extra = sorted(repr(item) for item in keys - expected_keys)
            retired = (
                "; joulewise.night_plan.v1 is retired and the plan must be "
                f"re-authored under {expected_schema}"
                if value.get("schema") == "joulewise.night_plan.v1"
                else ""
            )
            raise PlanError(
                "night_plan_malformed",
                f"plan keys are not exact (missing={missing}, extra={extra}){retired}",
            )
        if value.get("schema") != expected_schema:
            raise PlanError(
                "night_plan_malformed",
                f"schema must be {expected_schema} for {value.get('receipt_class')}",
            )
        schema_version = value.get("schema_version")
        if (
            isinstance(schema_version, bool)
            or not isinstance(schema_version, int)
            or schema_version != expected_version
        ):
            raise PlanError(
                "night_plan_malformed",
                f"schema_version must be integer {expected_version}",
            )

        def require_text(name: str) -> str:
            item = value.get(name)
            if not isinstance(item, str) or not item:
                raise PlanError("night_plan_malformed", f"{name} must be a non-empty string")
            return item

        def require_number(name: str) -> float:
            item = value.get(name)
            if isinstance(item, bool) or not isinstance(item, (int, float)):
                raise PlanError("night_plan_malformed", f"{name} must be a finite number")
            result = float(item)
            if not math.isfinite(result):
                raise PlanError("night_plan_malformed", f"{name} must be a finite number")
            return result

        plan_id = require_text("plan_id")
        receipt_class = require_text("receipt_class")
        if receipt_class not in RECEIPT_CLASSES:
            raise PlanError("night_plan_malformed", "receipt_class is not registered")
        t0_epoch_s = require_number("t0_epoch_s")
        authored_epoch_s = require_number("authored_epoch_s")
        window_max_s = value.get("window_max_s")
        if isinstance(window_max_s, bool) or not isinstance(window_max_s, int) or window_max_s <= 0:
            raise PlanError("night_plan_malformed", "window_max_s must be a positive integer")
        repo_head = require_text("repo_head")
        if _HEAD_RE.fullmatch(repo_head) is None:
            raise PlanError(
                "night_plan_malformed",
                "repo_head must be exactly 40 lowercase hexadecimal characters",
            )
        measurement_root = require_text("measurement_root")
        if not os.path.isabs(measurement_root):
            raise PlanError(
                "night_plan_malformed",
                "measurement_root must be an absolute path",
            )
        measurement_head = require_text("measurement_head")
        if _HEAD_RE.fullmatch(measurement_head) is None:
            raise PlanError(
                "night_plan_malformed",
                "measurement_head must be exactly 40 lowercase hexadecimal characters",
            )
        chain_path = require_text("chain_path")
        chain_sha256_path = require_text("chain_sha256_path")
        custody_root = require_text("custody_root")
        pack_night = None
        if is_pack:
            binding = value.get("pack_night")
            if not isinstance(binding, Mapping) or set(binding) != _PACK_NIGHT_KEYS:
                raise PlanError("night_plan_malformed", "pack_night keys must be exact")
            pack_id = binding["pack_id"]
            if not isinstance(pack_id, str) or not pack_id:
                raise PlanError("night_plan_malformed", "pack_night.pack_id must be a non-empty string")
            pack_root = binding["pack_root"]
            if (not isinstance(pack_root, str) or not Path(pack_root).is_absolute()
                    or Path(pack_root).name != pack_id
                    or any(part.is_symlink() for part in (Path(pack_root), *Path(pack_root).parents))):
                raise PlanError("night_plan_malformed", "pack_night.pack_root must be absolute, non-symlink, with basename pack_id")
            pack_sha256 = binding["pack_sha256"]
            if not isinstance(pack_sha256, str) or _SHA256_RE.fullmatch(pack_sha256) is None:
                raise PlanError("night_plan_malformed", "pack_night.pack_sha256 must be SHA-256")
            ordinal = binding["attempt_ordinal"]
            if type(ordinal) is not int or ordinal < 1:
                raise PlanError("night_plan_malformed", "pack_night.attempt_ordinal must be integer >= 1")
            if not os.path.isabs(custody_root):
                raise PlanError("night_plan_malformed", "pack custody_root must be an absolute path")
            pack_night = {
                "pack_id": pack_id,
                "pack_root": pack_root,
                "pack_sha256": pack_sha256,
                "attempt_ordinal": ordinal,
            }
            for name in ("authorization_record", "confirmation_record"):
                record = binding[name]
                if not isinstance(record, Mapping) or set(record) != _PACK_RECORD_KEYS:
                    raise PlanError("night_plan_malformed", f"pack_night.{name} keys must be exact")
                path, digest = record["path"], record["sha256"]
                if not isinstance(path, str) or not os.path.isabs(path):
                    raise PlanError("night_plan_malformed", f"pack_night.{name}.path must be absolute")
                try:
                    relative = Path(path).resolve().relative_to(Path(custody_root).resolve())
                    if relative == Path("."):
                        raise ValueError("record is the custody root")
                except (OSError, RuntimeError, ValueError) as exc:
                    raise PlanError("night_plan_malformed", f"pack_night.{name}.path escapes custody") from exc
                if not isinstance(digest, str) or _SHA256_RE.fullmatch(digest) is None:
                    raise PlanError("night_plan_malformed", f"pack_night.{name}.sha256 must be SHA-256")
                pack_night[name] = {"path": path, "sha256": digest}
        registration = value.get("registration_path")
        if registration is not None and (not isinstance(registration, str) or not registration):
            raise PlanError(
                "night_plan_malformed", "registration_path must be null or a non-empty string"
            )
        if receipt_class in {"DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB"} and registration is None:
            raise PlanError(
                "night_plan_malformed",
                f"registration_path is required for {receipt_class}",
            )
        quiet_admission = None
        if is_quiet:
            from joulewise.quiet_admission import validate_policy
            try:
                quiet_admission = validate_policy(value["quiet_admission"], window_max_s=window_max_s)
            except (ValueError, OverflowError) as exc:
                raise PlanError("night_plan_malformed", str(exc)) from exc
        return NightPlan(
            plan_id=plan_id,
            receipt_class=receipt_class,
            t0_epoch_s=t0_epoch_s,
            window_max_s=window_max_s,
            authored_epoch_s=authored_epoch_s,
            repo_head=repo_head,
            measurement_root=measurement_root,
            measurement_head=measurement_head,
            chain_path=chain_path,
            chain_sha256_path=chain_sha256_path,
            custody_root=custody_root,
            registration_path=registration,
            pack_night=pack_night,
            quiet_admission=quiet_admission,
        )


@dataclass(frozen=True)
class Refusal:
    reason: str
    detail: str
    evidence: tuple[ProbeResult, ...]


@dataclass(frozen=True)
class ConditionRow:
    condition_id: str
    status: str
    basis: str | None
    evidence: tuple[str, ...]
    measured: Mapping[str, object]


@dataclass(frozen=True)
class Receipt:
    schema: str
    receipt_class: str
    plan_id: str
    verdict: str
    conditions: tuple[ConditionRow, ...]
    refusal: Refusal | None
    authored_monotonic_ns: int
    admission: Mapping[str, object] | None = None

    def to_json_bytes(self) -> bytes:
        value = {
            "schema": self.schema,
            "receipt_class": self.receipt_class,
            "plan_id": self.plan_id,
            "verdict": self.verdict,
            "conditions": [
                {
                    "condition_id": row.condition_id,
                    "status": row.status,
                    "basis": row.basis,
                    "evidence": list(row.evidence),
                    "measured": dict(row.measured),
                }
                for row in self.conditions
            ],
            "refusal": None
            if self.refusal is None
            else {
                "reason": self.refusal.reason,
                "detail": self.refusal.detail,
                "evidence": [
                    {
                        "argv": list(result.argv),
                        "exit_code": result.exit_code,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "monotonic_ns": result.monotonic_ns,
                    }
                    for result in self.refusal.evidence
                ],
            },
            "authored_monotonic_ns": self.authored_monotonic_ns,
        }
        if self.admission is not None:
            value.update(self.admission)
        return (
            json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
        ).encode("utf-8")


def class_table() -> Mapping[str, Mapping[str, tuple[str, str | None]]]:
    """Return the ruled target status and registered basis for each class.

    ``PASS`` is a requirement, so a well-formed refusal may carry ``FAIL`` in
    that row.  ``NOT_APPLICABLE`` is an exact status/basis pair.
    """

    return {
        "DIAGNOSTIC_NO_PACK": {
            "C1": ("PASS", None),
            "C2": ("NOT_APPLICABLE", "no_pack_by_design"),
            "C3": ("PASS", None),
            "C4": ("PASS", None),
            "C5": ("PASS", None),
        },
        "REHEARSAL_STUB": {
            "C1": ("PASS", None),
            "C2": ("NOT_APPLICABLE", "no_pack_by_design"),
            "C3": ("PASS", None),
            "C4": ("PASS", None),
            "C5": ("PASS", None),
        },
        "TRANSACTION_PACK": {
            "C1": ("PASS", None),
            "C2": ("PASS", None),
            "C3": ("PASS", None),
            "C4": ("PASS", None),
            "C5": ("PASS", None),
        },
    }


def _safe_monotonic_ns(probes: Probes) -> int:
    try:
        value = probes.monotonic_ns()
    except Exception as exc:
        raise ProbeError(
            f"monotonic clock probe failed: {type(exc).__name__}: {exc}"
        ) from exc
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ProbeError("monotonic clock probe did not return a non-negative integer")
    return value


def _run(probes: CensusProbes, argv: tuple[str, ...]) -> ProbeResult:
    try:
        result = probes.run(argv)
    except Exception as exc:
        raise ProbeError(f"{' '.join(argv)}: {type(exc).__name__}: {exc}") from exc
    if not isinstance(result, ProbeResult):
        raise ProbeError(f"{' '.join(argv)}: probe returned a non-ProbeResult value")
    try:
        observed_argv = tuple(result.argv)
    except TypeError as exc:
        raise ProbeError(f"{' '.join(argv)}: probe result argv is malformed") from exc
    if observed_argv != argv:
        raise ProbeError(f"{' '.join(argv)}: probe result argv does not match request")
    if (
        isinstance(result.exit_code, bool)
        or not isinstance(result.exit_code, int)
        or not isinstance(result.stdout, str)
        or not isinstance(result.stderr, str)
        or isinstance(result.monotonic_ns, bool)
        or not isinstance(result.monotonic_ns, int)
        or result.monotonic_ns < 0
    ):
        raise ProbeError(f"{' '.join(argv)}: probe result fields are malformed")
    return result


def agent_census(probes: CensusProbes) -> tuple[ProbeResult, Refusal | None]:
    try:
        result = _run(probes, AGENT_CENSUS_ARGV)
    except ProbeError as exc:
        try:
            observed_monotonic_ns = _safe_monotonic_ns(probes)
        except ProbeError as clock_exc:
            observed_monotonic_ns = 0
            exc = ProbeError(f"{exc}; {clock_exc}")
        result = ProbeResult(
            argv=AGENT_CENSUS_ARGV,
            exit_code=-1,
            stdout="",
            stderr=str(exc),
            monotonic_ns=observed_monotonic_ns,
        )
        return result, Refusal("night_probe_error", str(exc), (result,))
    if result.exit_code == 1 and result.stdout.strip() == "":
        return result, None
    lines = result.stdout.strip().splitlines()
    detail = f"pgrep exit {result.exit_code}"
    if lines:
        shown = lines[:20]
        bounded = "\n".join(shown)
        if len(lines) > len(shown):
            bounded += f"\n… (+{len(lines) - len(shown)} more)"
        detail += f"; forbidden process output: {bounded}"
    return result, Refusal("night_refused_agent_present", detail, (result,))


@dataclass
class _MutableCondition:
    status: str
    basis: str | None
    evidence: list[str]
    measured: dict[str, object]


def _initial_conditions(receipt_class: str) -> dict[str, _MutableCondition]:
    rows: dict[str, _MutableCondition] = {}
    for condition_id, (required, basis) in class_table()[receipt_class].items():
        if required == "NOT_APPLICABLE":
            rows[condition_id] = _MutableCondition(required, basis, [], {})
        else:
            rows[condition_id] = _MutableCondition(
                "FAIL", None, [], {"detail": "not evaluated after refusal"}
            )
    if receipt_class == "TRANSACTION_PACK":
        for condition_id in ("C1", "C2"):
            rows[condition_id].measured = {"detail": "stage 3 not implemented"}
    return rows


def _probe_citation(result: ProbeResult) -> str:
    return "probe:" + " ".join(result.argv)


def _conditions_tuple(rows: Mapping[str, _MutableCondition]) -> tuple[ConditionRow, ...]:
    return tuple(
        ConditionRow(
            condition_id=condition_id,
            status=rows[condition_id].status,
            basis=rows[condition_id].basis,
            evidence=tuple(rows[condition_id].evidence),
            measured=dict(rows[condition_id].measured),
        )
        for condition_id in _CONDITION_IDS
    )


def _target_is_green(receipt_class: str, rows: Mapping[str, _MutableCondition]) -> bool:
    for condition_id, (required, basis) in class_table()[receipt_class].items():
        row = rows[condition_id]
        if row.status != required or row.basis != basis:
            return False
    return True


def _finish(
    plan: NightPlan,
    probes: Probes,
    rows: Mapping[str, _MutableCondition],
    refusal: Refusal | None,
    *,
    authored_monotonic_ns: int | None = None,
) -> Receipt:
    if authored_monotonic_ns is None:
        try:
            authored_monotonic_ns = _safe_monotonic_ns(probes)
        except ProbeError as exc:
            authored_monotonic_ns = 0
            refusal = Refusal("night_probe_error", str(exc), ())
    if refusal is not None:
        verdict = "REFUSED"
    elif plan.receipt_class == "REHEARSAL_STUB":
        verdict = "REHEARSAL_ONLY"
    elif _target_is_green(plan.receipt_class, rows):
        verdict = "GO"
    else:
        verdict = "REFUSED"
    return Receipt(
        schema=SCHEMA,
        receipt_class=plan.receipt_class,
        plan_id=plan.plan_id,
        verdict=verdict,
        conditions=_conditions_tuple(rows),
        refusal=refusal,
        authored_monotonic_ns=authored_monotonic_ns,
    )


def _probe_refusal(
    plan: NightPlan,
    probes: Probes,
    rows: Mapping[str, _MutableCondition],
    evidence: list[ProbeResult],
    exc: Exception,
) -> Receipt:
    refusal = Refusal(
        "night_probe_error",
        f"{type(exc).__name__}: {exc}",
        tuple(evidence),
    )
    return _finish(plan, probes, rows, refusal)


def production_interval_observation(interval_s: float | None = None) -> Mapping[str, object]:
    """One live ``sample_interval`` with THIS process as the observer root.

    No `powermetrics` exists at t0 or at the arm check -- the chain has not
    started -- so the gate's own pid is the whole observer tree (cold gate 10,
    2026-09-23, Q2(i)); the chain-root marking the recorder needs is a separate
    cure in ``quiet_predicate_campaign.record_covariates``.
    """

    from joulewise.quiet_admission import sample_interval

    if interval_s is None:
        interval_s = NON_OBSERVER_OBSERVATION_INTERVAL_S
    return sample_interval(interval_s, observer_pid=os.getpid())


def non_observer_consumers(observation: Mapping[str, object]) -> list[dict]:
    """The observation's non-observer consumers, or a refusal if it is malformed.

    Absent or unreadable evidence is never a pass: an observation with no
    ``observer`` flag on a consumer is precisely the defect the 2026-09-22
    night carried (every row read ``observer: false``, including the power
    sampler), so a consumer that does not carry a real boolean is a ProbeError,
    not a non-observer.
    """

    if not isinstance(observation, Mapping):
        raise ProbeError("non-observer observation must be an object")
    metrics = observation.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ProbeError("non-observer observation carries no metrics")
    consumers = metrics.get("top_consumers")
    if not isinstance(consumers, list):
        raise ProbeError("non-observer observation carries no top_consumers")
    result = []
    for consumer in consumers:
        if (not isinstance(consumer, Mapping)
                or not isinstance(consumer.get("observer"), bool)
                or not isinstance(consumer.get("pid"), int)
                or isinstance(consumer.get("pid"), bool)
                or not isinstance(consumer.get("command"), str)
                or isinstance(consumer.get("busy_cores"), bool)
                or not isinstance(consumer.get("busy_cores"), (int, float))
                or not math.isfinite(float(consumer["busy_cores"]))):
            raise ProbeError("malformed consumer in the non-observer observation")
        if not consumer["observer"]:
            result.append(dict(consumer))
    return result


def non_observer_offender(observation: Mapping[str, object]) -> dict | None:
    """The busiest non-observer consumer at or above the ruled share, or None."""

    busy = [c for c in non_observer_consumers(observation)
            if float(c["busy_cores"]) >= T0_NON_OBSERVER_SHARE_MAX]
    if not busy:
        return None
    return max(busy, key=lambda c: (float(c["busy_cores"]), -c["pid"]))


def non_observer_refusal_detail(offender: Mapping[str, object], interval_s: float) -> str:
    """Cold gate 10 (2026-09-23) Q2(i) refusal text, quoted, not paraphrased."""

    return (f"non-observer process busy: {os.path.basename(offender['command'])} "
            f"pid {offender['pid']} at {float(offender['busy_cores']):.3f} busy cores over "
            f"{float(interval_s):.1f} s (bar {T0_NON_OBSERVER_SHARE_MAX}); "
            "observation in top_consumers_at_decision")


def _completed_ok(result: ProbeResult) -> bool:
    return isinstance(result.exit_code, int) and not isinstance(result.exit_code, bool) and result.exit_code == 0


def _clock_value(probes: Probes, name: str) -> float | int:
    try:
        value = probes.now_epoch_s() if name == "epoch" else probes.monotonic_ns()
    except Exception as exc:
        raise ProbeError(f"{name} clock probe failed: {type(exc).__name__}: {exc}") from exc
    if name == "epoch":
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise ProbeError("epoch clock probe did not return a finite number")
        return float(value)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ProbeError("monotonic clock probe did not return a non-negative integer")
    return value


class PackNightRefusal(ValueError):
    def __init__(self, detail: str, *, missing: bool = False):
        self.reason = "launch_go_receipt_missing" if missing else "launch_go_receipt_invalid"
        super().__init__(detail)


def _pack_bytes(path: Path, field: str, expected: str | None = None) -> bytes:
    from joulewise import arm_readiness as readiness
    try:
        if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)):
            raise PackNightRefusal(field + ": non-absolute or symlinked")
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise PackNightRefusal(field, missing=True) from exc
    except OSError as exc:
        raise PackNightRefusal(field + ": " + str(exc)) from exc
    if expected is not None and readiness.sha256_bytes(raw) != expected:
        raise PackNightRefusal(field + ": sha256 mismatch")
    return raw


def _pack_object(path: Path, field: str, expected: str | None = None):
    from joulewise import arm_readiness as readiness
    raw = _pack_bytes(path, field, expected)
    try:
        value = readiness.parse_json_bytes(raw)
        if not isinstance(value, Mapping):
            raise ValueError("not an object")
    except (ValueError, TypeError) as exc:
        raise PackNightRefusal(field + ": invalid JSON") from exc
    return value


def _pack_digest(plan: NightPlan, arm=None) -> Path:
    from joulewise import arm_readiness as readiness
    binding = plan.pack_night
    root = Path(binding["pack_root"])
    if (not root.is_absolute() or root.name != binding["pack_id"]
            or any(p.is_symlink() for p in (root, *root.parents))):
        raise PackNightRefusal("pack_root")
    try:
        root = root.resolve(strict=True)
        digest = readiness.committed_pack_tree_sha256(root)
    except FileNotFoundError as exc:
        raise PackNightRefusal("pack_root", missing=True) from exc
    except (OSError, ValueError, RuntimeError) as exc:
        raise PackNightRefusal("pack_root: " + str(exc)) from exc
    if digest != binding["pack_sha256"]:
        raise PackNightRefusal("pack_root.pack_sha256")
    if arm is not None and (arm["pack"]["pack_sha256"] != digest
                            or arm["pack"]["pack_root"] != str(root)
                            or arm["pack"]["pack_id"] != binding["pack_id"]):
        raise PackNightRefusal("arm_receipt.pack.pack_root/pack_sha256")
    return root


def _authenticate_pack_records(plan: NightPlan):
    from joulewise import arm_readiness as readiness
    custody = Path(plan.custody_root)
    if not custody.is_absolute() or any(p.is_symlink() for p in (custody, *custody.parents)):
        raise PackNightRefusal("custody_root: non-absolute or symlinked")
    try:
        custody.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise PackNightRefusal("custody_root: resolution_error") from exc
    root = _pack_digest(plan)
    binding = plan.pack_night
    records = {}
    for field in ("authorization_record", "confirmation_record"):
        locator = binding[field]
        path = Path(locator["path"])
        try:
            path.resolve(strict=True).relative_to(Path(plan.custody_root).resolve(strict=True))
        except FileNotFoundError as exc:
            raise PackNightRefusal(field, missing=True) from exc
        except (OSError, ValueError, RuntimeError) as exc:
            raise PackNightRefusal(field + ".path") from exc
        records[field] = _pack_object(path, field, locator["sha256"])
    authorization = records["authorization_record"]
    keys = {"purpose", "attempt_id", "claim_eligible", "pack_sha256", "permitted_chain_sha256", "permitted_blocks", "authority"}
    if set(authorization) != keys:
        raise PackNightRefusal("authorization_record.keys")
    for field in ("pack_sha256", "permitted_chain_sha256"):
        if not isinstance(authorization[field], str) or re.fullmatch("[0-9a-f]{64}", authorization[field]) is None:
            raise PackNightRefusal("authorization_record." + field)
    if authorization["attempt_id"] != f"{plan.plan_id}/{binding['attempt_ordinal']}":
        raise PackNightRefusal("authorization_record.attempt_id")
    if authorization["pack_sha256"] != binding["pack_sha256"]:
        raise PackNightRefusal("authorization_record.pack_sha256")
    purpose = authorization["purpose"]
    if not isinstance(purpose, str) or purpose not in {"G2B_SHAKEDOWN", "CAMPAIGN_TRANSACTION", "T0_REHEARSAL"}:
        raise PackNightRefusal("authorization_record.purpose")
    if (type(authorization["claim_eligible"]) is not bool
            or type(authorization["permitted_blocks"]) is not int or authorization["permitted_blocks"] < 1
            or not isinstance(authorization["authority"], str) or not authorization["authority"].strip()):
        raise PackNightRefusal("authorization_record.claim_eligible/permitted_blocks/authority")
    if purpose != "CAMPAIGN_TRANSACTION" and authorization["claim_eligible"]:
        raise PackNightRefusal("authorization_record.claim_eligible")
    if purpose == "G2B_SHAKEDOWN" and (authorization["permitted_blocks"] != 1 or "D-171" not in authorization["authority"]):
        raise PackNightRefusal("authorization_record.permitted_blocks")
    if purpose == "CAMPAIGN_TRANSACTION" and authorization["authority"] != "V5-TRANSACTION-GO-01":
        raise PackNightRefusal("authorization_record.authority")
    # Reject a wrong-clone launch before consuming a single-use ARM receipt.
    # Keep the gate/GO identity check as a separate reauthentication.
    try:
        readiness._authenticate_launcher_identity(plan.measurement_root)
    except readiness.LaunchLineageError as exc:
        raise PackNightRefusal(str(exc)) from exc
    if purpose == "T0_REHEARSAL":
        # Preparation runs before the T-0 author and ARM mint. Re-read again
        # in the gate/GO and in consumption rather than trusting this result.
        try:
            readiness._production_inventory(plan)
        except (OSError, ValueError, RuntimeError) as exc:
            raise PackNightRefusal(str(exc)) from exc
    confirmation = records["confirmation_record"]
    if set(confirmation) != {"table_path", "table_sha256", "transcript_sha256", "confirmed_at"}:
        raise PackNightRefusal("confirmation_record.keys")
    for field in ("table_sha256", "transcript_sha256"):
        if not isinstance(confirmation[field], str) or re.fullmatch("[0-9a-f]{64}", confirmation[field]) is None:
            raise PackNightRefusal("confirmation_record." + field)
    event = confirmation["confirmed_at"]
    if (not isinstance(event, Mapping) or set(event) != {"epoch_s", "iso8601_utc"}
            or type(event["epoch_s"]) is not float or not math.isfinite(event["epoch_s"])):
        raise PackNightRefusal("confirmation_record.confirmed_at")
    try:
        stamp = datetime.strptime(event["iso8601_utc"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        if abs(stamp.timestamp() - event["epoch_s"]) > 0.000001:
            raise ValueError("timestamps differ")
    except (TypeError, ValueError) as exc:
        raise PackNightRefusal("confirmation_record.confirmed_at") from exc
    if not isinstance(confirmation["table_path"], str):
        raise PackNightRefusal("confirmation_record.table_path")
    _pack_bytes(Path(confirmation["table_path"]), "confirmation_record.table_sha256", confirmation["table_sha256"])
    chain = _pack_bytes(Path(plan.chain_path), "window_chain_sha256", authorization["permitted_chain_sha256"])
    sidecar = _pack_bytes(Path(plan.chain_sha256_path), "chain_sha256_path").decode("utf-8")
    tokens = sidecar.split()
    if (len(tokens) not in (1, 2) or tokens[0] != readiness.sha256_bytes(chain)
            or (len(tokens) == 2 and tokens[1] != Path(plan.chain_path).name)):
        raise PackNightRefusal("window_chain_sha256: sidecar mismatch")
    return {"root": root, **records}


def _pack_no_retry(plan: NightPlan, boot: str, written: Path | None = None):
    from joulewise import arm_readiness as readiness
    pack_custody = Path(plan.custody_root) / plan.pack_night["pack_id"]
    for directory in (pack_custody, pack_custody / "arm_readiness.receipts", pack_custody / "arm_readiness.consumptions"):
        if directory.is_symlink():
            raise PackNightRefusal("arm_receipt: symlinked namespace")
    for path in pack_custody.rglob("*.consumed.json"):
        value = _pack_object(path, "consumption")
        if not isinstance(value.get("boot_session_id"), str):
            raise PackNightRefusal("consumption.boot_session_id")
        if value.get("boot_session_id") == boot:
            raise PackNightRefusal("arm_receipt: consumption this boot")
    namespace = pack_custody / "arm_readiness.receipts"
    if not namespace.exists():
        return
    for entry in readiness.scan_receipt_namespace(namespace, "arm"):
        if entry["receipt"]["boot_session_id"] != boot:
            continue
        if written is None or entry["number"] > int(written.stem.removeprefix("arm-")):
            raise PackNightRefusal("arm_receipt: higher-numbered unconsumed receipt or re-arm this boot")


def _pack_evidence(plan: NightPlan, arm_state):
    from joulewise import arm_readiness as readiness
    from joulewise import arm_readiness_evidence_t0 as t0_author
    custody = Path(plan.custody_root)
    pack_custody = custody / plan.pack_night["pack_id"]
    # Gate replay uses the ARM's recorded inventory, independently of the author
    # row census below. The driver also binds its immediate author result.
    recorded_paths = [str(pack_custody / item["path"]) for item in arm_state["arm"]["evidence"]
                      if item.get("namespace") == "WINDOW_CUSTODY"
                      and Path(item["path"]).parent == Path(t0_author._EVIDENCE_DIRECTORY)]
    paths = arm_state.get("authored", {}).get("receipt_paths", recorded_paths)
    expected_paths = {str(pack_custody / t0_author._EVIDENCE_DIRECTORY / t0_author._receipt_name(row)) for row in t0_author._EXPECTED_ROWS}
    if not isinstance(paths, list) or len(paths) != 15 or any(not isinstance(path, str) for path in paths) or set(paths) != expected_paths or len(recorded_paths) != 15 or set(recorded_paths) != expected_paths:
        raise PackNightRefusal("t0_evidence.receipt_paths")
    arm_paths = {str(pack_custody / item["path"]): item["sha256"]
                 for item in arm_state["arm"]["evidence"] if item.get("namespace") == "WINDOW_CUSTODY"}
    records = []
    inputs = {}
    for text in paths:
        if text not in arm_paths:
            raise PackNightRefusal("t0_evidence: author receipt absent from ARM")
        path = Path(text)
        value = _pack_object(path, "t0_evidence", arm_paths[text])
        for fact in value.get("facts", []):
            if fact.get("source_kind") != "PROBE":
                continue
            source = _pack_object(pack_custody / fact["source_path"], "t0_evidence.source", fact["source_sha256"])
            for item in source.get("input_artifacts", []):
                if item["path"] in inputs and inputs[item["path"]] != item["sha256"]:
                    raise PackNightRefusal("t0_evidence.source: conflicting input digest")
                inputs[item["path"]] = item["sha256"]
        records.append(path)
    # This is the author's exact capture inventory, not a caller glob or subset.
    records.extend(pack_custody / "arm_readiness.t0.inputs" / name for name in t0_author._CAPTURE_FILES.values())
    result = []
    for path in records:
        expected = arm_paths.get(str(path), inputs.get(str(path)))
        if expected is None:
            raise PackNightRefusal("t0_evidence.capture: absent from author attestation")
        raw = _pack_bytes(path, "t0_evidence", expected)
        try:
            relative = path.resolve(strict=True).relative_to(custody.resolve(strict=True)).as_posix()
        except ValueError as exc:
            raise PackNightRefusal("t0_evidence.path") from exc
        result.append({"path": relative, "sha256": readiness.sha256_bytes(raw)})
    return sorted(result, key=lambda item: item["path"])


def _pack_rehearsal_roots(plan, arm, purpose):
    from joulewise import arm_readiness as readiness, t0_rehearsal
    window_id = arm["pack"]["window_id"]
    prefixed = isinstance(window_id, str) and window_id.startswith(t0_rehearsal.REHEARSAL_WINDOW_PREFIX)
    if prefixed != (purpose == "T0_REHEARSAL"):
        raise PackNightRefusal("rehearsal_purpose_on_production_id" if purpose == "T0_REHEARSAL" else "purpose")
    try:
        measurement = readiness._authenticate_launcher_identity(plan.measurement_root)
    except readiness.LaunchLineageError as exc:
        raise PackNightRefusal(str(exc)) from exc
    if not prefixed:
        return
    try:
        production = readiness.production_custody_roots(home=Path.home(), inventory=readiness._production_inventory(plan))
    except (OSError, ValueError, RuntimeError) as exc:
        raise PackNightRefusal("rehearsal_roots_not_disjoint") from exc
    if not production:
        raise PackNightRefusal("rehearsal_roots_not_disjoint")
    roots = {"measurement_root": plan.measurement_root, "custody_root": plan.custody_root}
    roots.update({"arm_context." + key: value for key, value in arm["arm_context"].items()
                  if key in readiness.ARM_CONTEXT_KEYS - readiness.ARM_CONTEXT_NON_PATH_KEYS})
    for field, text in roots.items():
        path = Path(text)
        if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)):
            raise PackNightRefusal(field)
        try:
            path = path.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise PackNightRefusal(field + ": resolution_error") from exc
        for root in production:
            if root.resolution_error is not None:
                raise PackNightRefusal("rehearsal_roots_not_disjoint")
            predicate = next((spec.predicate for spec in readiness.PRODUCTION_CUSTODY_ROOTS
                              if spec.role == root.role.split(":", 1)[0]), None)
            if predicate not in {"DISJOINT", "SIBLING_CHILD"}:
                raise PackNightRefusal("rehearsal_roots_not_disjoint")
            if predicate == "SIBLING_CHILD" and field in {"custody_root", "arm_context.custody_root"}:
                if path.parent != root.path or path.name != window_id:
                    raise PackNightRefusal("rehearsal_roots_not_disjoint")
            elif predicate == "SIBLING_CHILD" and field != "measurement_root":
                continue
            elif t0_rehearsal._contains(root.path, path) or t0_rehearsal._contains(path, root.path):
                detail = "rehearsal_roots_not_disjoint"
                if field == "measurement_root":
                    detail += ": measurement_root"
                raise PackNightRefusal(detail)
    if not measurement.name.startswith(readiness.REHEARSAL_CLONE_PREFIX):
        raise PackNightRefusal("rehearsal_clone_prefix_invalid: measurement_root")


def _evaluate_pack_conditions(plan, probes, rows, arm_path):
    """Derive C1/C2 from bound custody bytes, never caller condition labels."""
    from joulewise import arm_readiness as readiness

    prepared = _authenticate_pack_records(plan)
    rows["C1"] = _MutableCondition("PASS", None,
        [plan.pack_night[key]["path"] for key in ("authorization_record", "confirmation_record")],
        dict(prepared["authorization_record"]))
    if arm_path is None:
        raise PackNightRefusal("arm_receipt: exact driver-written path required", missing=True)
    path = Path(arm_path)
    custody = Path(plan.custody_root) / plan.pack_night["pack_id"]
    if (path.parent != custody / "arm_readiness.receipts"
            or re.fullmatch(r"arm-[0-9]{4,}\.json", path.name) is None):
        raise PackNightRefusal("arm_receipt.path")
    confirmation = prepared["confirmation_record"]
    verified = readiness._verify_arm_receipt(prepared["root"], path, require_unconsumed=True,
        step6_confirmation_table=confirmation["table_path"],
        expected_confirmation_digest=confirmation["table_sha256"])
    if verified.get("status") != "PASS" or verified.get("arm_disposition") != "GO":
        raise PackNightRefusal("arm_receipt: replay did not return PASS/GO")
    arm = _pack_object(path, "arm_receipt", verified["receipt_sha256"])
    _pack_digest(plan, arm)
    if (arm["status"] != "PASS" or arm["arm_disposition"] != "GO"
            or arm["pack"]["plan_id"] != plan.plan_id
            or arm["reviewed_main"]["head_commit"] != plan.repo_head
            or arm["arm_context"]["custody_root"] != plan.custody_root):
        raise PackNightRefusal("arm_receipt.plan/HEAD/custody/disposition")
    if (arm["boot_session_id"] != readiness._current_boot_session_id()
            or _clock_value(probes, "monotonic") >= arm["valid_until_monotonic_ns"]):
        raise PackNightRefusal("arm_receipt.boot/expiry")
    _pack_rehearsal_roots(plan, arm, prepared["authorization_record"]["purpose"])
    _pack_no_retry(plan, arm["boot_session_id"], path)
    evidence = _pack_evidence(plan, {"arm": arm})
    rows["C2"] = _MutableCondition("PASS", None,
        [str(path), *(item["path"] for item in evidence)],
        {"arm_sha256": verified["receipt_sha256"]})
    return arm

def _check_static_start(plan, probes, rows, evidence):
    if (
        plan.receipt_class in {"DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB"}
        and (not isinstance(plan.registration_path, str) or not plan.registration_path)
    ):
        return _finish(
            plan,
            probes,
            rows,
            Refusal(
                "night_plan_malformed",
                "registration_path must be a non-empty string for this receipt class",
                (),
            ),
        )

    # R-6: missed-fire guard.  No command or filesystem probe precedes it.
    try:
        now_epoch_s = float(_clock_value(probes, "epoch"))
    except ProbeError as exc:
        return _probe_refusal(plan, probes, rows, evidence, exc)
    rows["C5"].measured = {
        "t0_epoch_s": plan.t0_epoch_s,
        "window_max_s": plan.window_max_s,
        "observed_epoch_s": now_epoch_s,
    }
    if not (plan.t0_epoch_s <= now_epoch_s <= plan.t0_epoch_s + plan.window_max_s):
        return _finish(
            plan,
            probes,
            rows,
            Refusal(
                "night_window_expired",
                f"now {now_epoch_s} is outside [{plan.t0_epoch_s}, {plan.t0_epoch_s + plan.window_max_s}]",
                (),
            ),
        )

    # R-6 (reinterpreted): freshness and exact measurement-checkout identity.
    rows["C5"].measured["authored_epoch_s"] = plan.authored_epoch_s
    if plan.authored_epoch_s > now_epoch_s:
        return _finish(
            plan,
            probes,
            rows,
            Refusal("night_plan_malformed", "plan authored_epoch_s is in the future", ()),
        )
    if now_epoch_s - plan.authored_epoch_s > PLAN_MAX_AGE_S:
        return _finish(
            plan,
            probes,
            rows,
            Refusal("night_plan_stale", "plan is older than 36 hours", ()),
        )
    # magistrate provisional reading, activation 152c9255 record 00 item 51,
    # pending final pass: T0_REHEARSAL measures nothing and retains its
    # separate production-custody disjointness rule.
    rehearsal = False
    if (plan.authored_epoch_s >= MEASUREMENT_ROOT_CUSTODY_CUTOFF_EPOCH_S
            and plan.receipt_class == "TRANSACTION_PACK" and plan.pack_night is not None):
        locator = plan.pack_night["authorization_record"]
        try:
            authorization = _pack_object(Path(locator["path"]), "authorization_record",
                                         locator["sha256"])
            rehearsal = authorization.get("purpose") == "T0_REHEARSAL"
        except (PackNightRefusal, OSError, ValueError):
            pass  # Unauthenticated purpose cannot exempt a pack plan.
    if plan.authored_epoch_s >= MEASUREMENT_ROOT_CUSTODY_CUTOFF_EPOCH_S and not rehearsal:
        try:
            custody_root = MEASUREMENT_ROOT_CUSTODY_ROOT.resolve(strict=True)
            measurement_root = Path(plan.measurement_root)
            try:
                resolved = measurement_root.resolve(strict=True)
                # Existing paths can have case-variant spellings on macOS.
                inside_custody = any(parent.samefile(custody_root)
                                     for parent in resolved.parents)
            except FileNotFoundError:
                relative = measurement_root.resolve().relative_to(custody_root)
                inside_custody = relative != Path(".")
        except (OSError, RuntimeError, ValueError):
            inside_custody = False
        if not inside_custody:
            return _finish(
                plan,
                probes,
                rows,
                Refusal(
                    "measurement_root_outside_custody",
                    "resolved measurement_root must be strictly inside "
                    f"{MEASUREMENT_ROOT_CUSTODY_ROOT}",
                    (),
                ),
            )
    try:
        measurement_checkout_head = probes.measurement_head(plan.measurement_root)
        checkout_head = probes.checkout_head()
    except Exception as exc:
        return _probe_refusal(plan, probes, rows, evidence, exc)
    rows["C5"].measured.update(
        {
            "plan_repo_head": plan.repo_head,
            "driver_checkout_head": checkout_head,
            "measurement_root": plan.measurement_root,
            "plan_measurement_head": plan.measurement_head,
            "measurement_checkout_head": measurement_checkout_head,
        }
    )
    if measurement_checkout_head != plan.measurement_head:
        return _finish(
            plan,
            probes,
            rows,
            Refusal(
                "night_plan_stale",
                f"plan measurement_head {plan.measurement_head} does not match "
                f"measurement checkout HEAD {measurement_checkout_head} at "
                f"{plan.measurement_root}",
                (),
            ),
        )
    try:
        checkout_status = _run(
            probes,
            ("/usr/bin/git", "-c", "core.fsmonitor=false", "-C", plan.measurement_root, "--no-optional-locks",
             "status", "--porcelain=v1", "--untracked-files=all"),
        )
        evidence.append(checkout_status)
        rows["C5"].evidence.append(_probe_citation(checkout_status))
        porcelain = checkout_status.stdout.splitlines()
        if checkout_status.exit_code != 0:
            rows["C5"].measured["measurement_checkout_porcelain"] = None
            raise ProbeError(
                f"measurement checkout status failed at {plan.measurement_root}: "
                f"exit {checkout_status.exit_code}: {checkout_status.stderr.strip()}"
            )
        rows["C5"].measured["measurement_checkout_porcelain"] = porcelain[:50]
        if len(porcelain) > 50:
            rows["C5"].measured["measurement_checkout_porcelain_truncated"] = True
    except Exception as exc:
        return _probe_refusal(plan, probes, rows, evidence, exc)
    if checkout_status.stdout:
        return _finish(
            plan,
            probes,
            rows,
            Refusal(
                "night_plan_stale",
                f"measurement checkout {plan.measurement_root} has tracked edits or "
                f"untracked files: {'; '.join(porcelain[:5])}",
                tuple(evidence),
            ),
        )


def _check_census(plan, probes, rows, evidence, *, strict=False):
    census_result, census_refusal = agent_census(probes)
    if strict and (census_result.exit_code not in (0, 1)
                   or (census_result.exit_code == 1 and census_result.stdout.strip())
                   or (census_result.exit_code == 0 and not census_result.stdout.strip())):
        census_refusal = Refusal("night_probe_error", "malformed or failed binding census", (census_result,))
    evidence.append(census_result)
    rows["C3"].evidence.append(_probe_citation(census_result))
    rows["C3"].measured = {
        "agent_census_exit_code": census_result.exit_code,
        "agent_census_stdout": census_result.stdout,
    }
    if census_refusal is not None:
        return _finish(plan, probes, rows, census_refusal)


def _check_chain_identity(plan, probes, rows, evidence):
    if plan.receipt_class == "REHEARSAL_STUB":
        rows["C5"].measured.update(
            {
                "chain_path": plan.chain_path,
                "chain_sha256_path": plan.chain_sha256_path,
                "chain_sha256": None,
                "expected_chain_sha256": None,
                "chain_stub": "built_in_stub_by_design",
            }
        )
    else:
        # The chain and sidecar are read as text by the injected adapter; UTF-8 is
        # the ruled byte representation for hashing text observations.
        try:
            chain_text = probes.read_text(plan.chain_path)
            sidecar_text = probes.read_text(plan.chain_sha256_path)
            if not isinstance(chain_text, str) or not isinstance(sidecar_text, str):
                raise ProbeError("chain and sidecar probes must return text")
            observed_chain_sha256 = hashlib.sha256(chain_text.encode("utf-8")).hexdigest()
        except Exception as exc:
            return _probe_refusal(plan, probes, rows, evidence, exc)
        sidecar_tokens = sidecar_text.split()
        expected_chain_sha256 = sidecar_tokens[0] if sidecar_tokens else ""
        rows["C5"].measured.update(
            {
                "chain_path": plan.chain_path,
                "chain_sha256_path": plan.chain_sha256_path,
                "chain_sha256": observed_chain_sha256,
                "expected_chain_sha256": expected_chain_sha256,
            }
        )
        rows["C5"].evidence.extend(
            (f"chain:{plan.chain_path}", f"chain_sha256:{plan.chain_sha256_path}")
        )
        sidecar_defect: str | None = None
        if not sidecar_tokens:
            sidecar_defect = "sidecar token check failed: expected one or two tokens, got zero"
        elif len(sidecar_tokens) >= 3:
            sidecar_defect = (
                f"sidecar token check failed: expected one or two tokens, got {len(sidecar_tokens)}"
            )
        elif _SHA256_RE.fullmatch(expected_chain_sha256) is None:
            sidecar_defect = "sidecar digest check failed: first token must be 64 lowercase hex"
        elif len(sidecar_tokens) == 2:
            chain_basename = plan.chain_path.rsplit("/", 1)[-1]
            if sidecar_tokens[1] != chain_basename:
                sidecar_defect = (
                    "sidecar basename check failed: "
                    f"expected {chain_basename!r}, got {sidecar_tokens[1]!r}"
                )
        if sidecar_defect is None and observed_chain_sha256 != expected_chain_sha256:
            sidecar_defect = (
                f"chain digest check failed: observed {observed_chain_sha256}, "
                f"sidecar {expected_chain_sha256}"
            )
        if sidecar_defect is not None:
            return _finish(
                plan,
                probes,
                rows,
                Refusal(
                    "night_chain_digest_mismatch",
                    sidecar_defect,
                    tuple(evidence),
                ),
            )
        # R1 (record 46a): authenticate the tracked SOURCE, not its advisory
        # sidecar. Calibration wrappers retain their historical path unchanged.
        try:
            kind = probe_payload_kind(chain_text)
            if kind_row(kind).authenticate_chain_source:
                chain_path = kind_row(kind).chain_source_path
                source = _run(probes, ("/usr/bin/git", "-C", plan.measurement_root,
                                      "show", f"{plan.measurement_head}:{chain_path}"))
                if source.exit_code != 0:
                    raise ProbeError("tracked evidence chain source unavailable")
                measured = hashlib.sha256(source.stdout.encode("utf-8")).hexdigest()
                actual = probes.read_text(str(Path(plan.measurement_root) / chain_path))
                if (chain_literal(chain_text, "EVIDENCE_CHAIN_SOURCE_SHA256") != measured or
                        hashlib.sha256(actual.encode("utf-8")).hexdigest() != measured):
                    raise ValueError("evidence chain source differs from measurement_head or pinned wrapper")
                rows["C5"].measured.update(payload_kind=kind, chain_source_sha256=measured)
                rows["C5"].evidence.append(f"chain_source:{plan.measurement_head}:{chain_path}")
        except ValueError as exc:
            return _finish(plan, probes, rows, Refusal("night_chain_digest_mismatch", str(exc), tuple(evidence)))
        except (ProbeError, OSError, subprocess.SubprocessError) as exc:
            return _probe_refusal(plan, probes, rows, evidence, exc)
    rows["C5"].status = "PASS"
    rows["C5"].measured["detail"] = (
        "window, plan freshness, and measurement HEAD passed; chain identity not evaluated "
        "(driver substitutes the built-in stub)"
        if plan.receipt_class == "REHEARSAL_STUB"
        else "window, plan freshness, measurement HEAD, and chain identity passed"
    )


def _check_machine(plan, probes, rows, evidence, *, legacy_load=True):
    # R-6's unattended HID predicate precedes the remaining quiet predicates.
    try:
        hid = _run(probes, HID_IDLE_ARGV)
    except ProbeError as exc:
        return _probe_refusal(plan, probes, rows, evidence, exc)
    evidence.append(hid)
    rows["C3"].evidence.append(_probe_citation(hid))
    rows["C3"].measured["hid_idle_raw"] = hid.stdout
    if not legacy_load and not _completed_ok(hid):
        return _probe_refusal(plan, probes, rows, evidence, ProbeError("screensaver probe failed"))
    if not legacy_load and not re.fullmatch(r"[0-9]+", hid.stdout.strip()):
        return _probe_refusal(plan, probes, rows, evidence, ProbeError("screensaver output malformed"))
    if not _completed_ok(hid) or hid.stdout.strip() != "0":
        return _finish(
            plan,
            probes,
            rows,
            Refusal(
                "night_refused_hid_idle",
                f"screensaver idleTime must be exactly 0 (exit={hid.exit_code}, stdout={hid.stdout.strip()!r})",
                tuple(evidence),
            ),
        )

    # R-11 quiet predicates, in a fixed and reviewable command order.
    try:
        batt = _run(probes, PMSET_BATT_ARGV)
        evidence.append(batt)
        rows["C3"].evidence.append(_probe_citation(batt))
        rows["C3"].measured["ac_power_raw"] = batt.stdout
        if not legacy_load and (not _completed_ok(batt) or not any(
                power in batt.stdout for power in ("AC Power", "Battery Power"))):
            raise ProbeError("power observation malformed or failed")
        if not _completed_ok(batt) or "AC Power" not in batt.stdout:
            return _finish(
                plan,
                probes,
                rows,
                Refusal(
                    "night_refused_not_quiet",
                    "ac_power",
                    tuple(evidence),
                ),
            )

        settings = _run(probes, PMSET_GENERAL_ARGV)
        evidence.append(settings)
        rows["C3"].evidence.append(_probe_citation(settings))
        rows["C3"].measured["pmset_g_raw"] = settings.stdout
        display_match = _DISPLAY_SLEEP_RE.search(settings.stdout)
        rows["C3"].measured["displaysleep"] = (
            None if display_match is None else display_match.group(1)
        )
        if not legacy_load and (not _completed_ok(settings) or display_match is None):
            raise ProbeError("display configuration observation malformed or failed")
        if not _completed_ok(settings) or display_match is None:
            return _finish(
                plan,
                probes,
                rows,
                Refusal(
                    "night_refused_not_quiet",
                    "displaysleep predicate failed",
                    tuple(evidence),
                ),
            )

        if legacy_load:
            load = _run(probes, LOAD_AVG_ARGV)
            evidence.append(load)
            rows["C3"].evidence.append(_probe_citation(load))
            rows["C3"].measured["load_average_raw"] = load.stdout
            load_match = _LOAD_AVG_RE.fullmatch(load.stdout.strip())
            if not _completed_ok(load) or load_match is None:
                raise ProbeError(
                    "load average output malformed: "
                    f"exit={load.exit_code}, stdout={load.stdout[:200]!r}"
                )
            load_1m = float(load_match.group(1))
            rows["C3"].measured["load_1m"] = load_1m
            if load_1m > LOAD_MAX:
                return _finish(
                    plan,
                    probes,
                    rows,
                    Refusal(
                        "night_refused_not_quiet",
                        f"load_average predicate failed (maximum {LOAD_MAX})",
                        tuple(evidence),
                    ),
                )

        thermal = _run(probes, THERMAL_ARGV)
        evidence.append(thermal)
        rows["C3"].evidence.append(_probe_citation(thermal))
        rows["C3"].measured["thermal_raw"] = thermal.stdout
        thermal_limits: list[str] = []
        for thermal_line in thermal.stdout.splitlines():
            stripped_line = thermal_line.strip()
            if not stripped_line.startswith("CPU_Speed_Limit"):
                continue
            thermal_match = _THERMAL_RE.fullmatch(stripped_line)
            if thermal_match is None:
                raise ProbeError(
                    f"thermal output malformed: {thermal.stdout[:200]!r}"
                )
            thermal_limits.append(thermal_match.group(1))
        thermal_limit = thermal_limits[0] if thermal_limits else None
        rows["C3"].measured["cpu_speed_limit"] = thermal_limit
        if not _completed_ok(thermal):
            raise ProbeError(
                f"thermal probe exit {thermal.exit_code}: {thermal.stdout[:200]!r}"
            )
        if any(limit != "100" for limit in thermal_limits):
            return _finish(
                plan,
                probes,
                rows,
                Refusal(
                    "night_refused_not_quiet",
                    "thermal predicate failed",
                    tuple(evidence),
                ),
            )
        if (rows["C5"].measured.get("payload_kind") in NIGHT_KINDS and
                kind_row(rows["C5"].measured["payload_kind"]).corecaptured_at_arm_and_t0):
            # This is the planned t0 boundary. The read adds probe time, but
            # there is no cure, deliberate wait, or process action here.
            try:
                log_started_epoch_s = _clock_value(probes, "epoch")
                log_result = _run(probes, corecaptured_loop.LOG_ARGV)
                log_finished_epoch_s = _clock_value(probes, "epoch")
                evidence.append(log_result)
                rows["C3"].evidence.append(_probe_citation(log_result))
                if not _completed_ok(log_result):
                    raise ValueError(f"log exited {log_result.exit_code}: {log_result.stderr.strip()}")
                spawns = corecaptured_loop.count_spawns(
                    log_result.stdout, log_started_epoch_s,
                    until_epoch_s=log_finished_epoch_s)
            except (ProbeError, ValueError) as exc:
                rows["C3"].measured["corecaptured"] = {
                    "status": "not_measured", "reason": str(exc)}
            else:
                rows["C3"].measured["corecaptured"] = {
                    "status": "measured", "last_10m_spawns": spawns.count,
                    "first_spawn": spawns.first, "last_spawn": spawns.last}
                if spawns.count > corecaptured_loop.SPAWNS_MAX:
                    return _finish(plan, probes, rows, Refusal(
                        "night_refused_not_quiet",
                        f"corecaptured: {spawns.count} launchd spawns in last 10 min "
                        f"(first {spawns.first}, last {spawns.last})",
                        tuple(evidence)))
        # The per-process machine-state predicate (cold gate 10
        # QPE01-DAEMON-CONTAMINATION-01, 2026-09-23, Q2(i)), on BOTH branches
        # -- t0 (`legacy_load=True`, via `evaluate_night`) and the arm check
        # (`legacy_load=False`, via `evaluate_dynamic_hard`).  It runs LAST
        # because it costs thirty seconds and every predicate above it costs
        # milliseconds: a machine that fails the thermal probe should not be
        # watched for half a minute first.
        #
        # It is spent only on a QPE-01 evidence night.  `payload_kind` is set
        # by `_check_chain_identity`, which runs before this check on both
        # paths, and the registration check refuses an evidence payload that
        # is not pinned to a chain-binding QPE-01 registration -- so this
        # condition is exactly "a pilot night, v2 or v3 alike", which is the
        # scope the ruling gives the predicate.
        if (rows["C5"].measured.get("payload_kind") in NIGHT_KINDS and
                kind_row(rows["C5"].measured["payload_kind"]).non_observer_at_arm_and_t0):
            observer = probes.observe_interval or production_interval_observation
            try:
                observation = observer()
            except Exception as exc:  # the sampler owns many failure types
                raise ProbeError(
                    f"non-observer interval observation failed: {type(exc).__name__}: {exc}"
                ) from exc
            offender = non_observer_offender(observation)
            interval_s = (observation.get("interval_s")
                          if isinstance(observation, Mapping) else None)
            if not isinstance(interval_s, (int, float)) or isinstance(interval_s, bool):
                raise ProbeError("non-observer observation carries no interval_s")
            rows["C3"].measured["top_consumers_at_decision"] = list(
                (observation.get("metrics") or {}).get("top_consumers") or [])
            rows["C3"].measured["non_observer_interval_s"] = interval_s
            if offender is not None:
                return _finish(
                    plan,
                    probes,
                    rows,
                    Refusal(
                        "night_refused_not_quiet",
                        non_observer_refusal_detail(offender, interval_s),
                        tuple(evidence),
                    ),
                )
    except ProbeError as exc:
        return _probe_refusal(plan, probes, rows, evidence, exc)
    rows["C3"].status = "PASS"
    # The detail names the non-observer predicate only when it ran (an
    # evidence night; fix round 1, Fable lens N4), so a calibration receipt
    # keeps its historical text and never claims a check it did not make.
    non_observer = ("non_observer_interval_s" in rows["C3"].measured)
    if legacy_load:
        rows["C3"].measured["detail"] = (
            "agent, HID, AC, display, load, thermal and non-observer process predicates passed"
            if non_observer else "agent, HID, AC, display, load, and thermal predicates passed")
    else:
        rows["C3"].measured["detail"] = (
            "agent, screensaver configuration, AC, display, thermal and non-observer process "
            "predicates passed" if non_observer
            else "agent, screensaver configuration, AC, display and thermal predicates passed")


def _check_clock(plan, probes, rows, evidence, *, pack_arm=None, strict_probe=False):
    # C4 is deliberately local-only: boot UUID plus an epoch/monotonic pair.
    try:
        boot = _run(probes, BOOT_SESSION_ARGV)
    except ProbeError as exc:
        return _probe_refusal(plan, probes, rows, evidence, exc)
    evidence.append(boot)
    rows["C4"].evidence.append(_probe_citation(boot))
    if strict_probe and (not _completed_ok(boot) or not boot.stdout.strip()):
        return _probe_refusal(plan, probes, rows, evidence,
                              ProbeError("kern.bootsessionuuid probe failed or returned no identity"))
    boot_session_uuid = boot.stdout.strip().lower()
    canonical_uuid: str | None = None
    if _completed_ok(boot):
        try:
            canonical_uuid = str(uuid.UUID(boot_session_uuid))
        except (ValueError, AttributeError):
            canonical_uuid = None
    if canonical_uuid is None or boot_session_uuid != canonical_uuid:
        rows["C4"].measured = {"boot_session_uuid_raw": boot.stdout}
        return _finish(
            plan,
            probes,
            rows,
            Refusal(
                "night_refused_boot_clock",
                "kern.bootsessionuuid is not a canonical UUID",
                tuple(evidence),
            ),
        )
    try:
        clock_epoch_s = float(_clock_value(probes, "epoch"))
        clock_monotonic_ns = int(_clock_value(probes, "monotonic"))
    except ProbeError as exc:
        return _probe_refusal(plan, probes, rows, evidence, exc)
    if pack_arm is not None and (
        pack_arm["boot_session_id"] != canonical_uuid
        or clock_monotonic_ns >= pack_arm["valid_until_monotonic_ns"]
    ):
        return _finish(plan, probes, rows,
            Refusal("launch_go_receipt_invalid", "conditions.C4: ARM boot/expiry", ()))
    rows["C4"].status = "PASS"
    rows["C4"].measured = {
        "boot_session_uuid": canonical_uuid,
        "clock_epoch_s": clock_epoch_s,
        "clock_monotonic_ns": clock_monotonic_ns,
    }
    rows["C4"].evidence.append("clock:epoch+monotonic")


def _check_registration(plan, probes, rows, evidence):
    clock_monotonic_ns = rows["C4"].measured.get("clock_monotonic_ns")
    if plan.receipt_class in {"DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB"}:
        try:
            registration_path = Path(plan.registration_path)
            if not registration_path.is_absolute():
                registration_path = Path(plan.measurement_root) / registration_path
            registration_text = probes.read_text(str(registration_path))
            if not isinstance(registration_text, str):
                raise ProbeError("registration probe must return text")
            registration_sha256 = hashlib.sha256(
                registration_text.encode("utf-8")
            ).hexdigest()
        except Exception as exc:
            return _probe_refusal(plan, probes, rows, evidence, exc)
        rows["C1"].evidence.append(f"registration:{plan.registration_path}")
        rows["C1"].measured = {
            "registration_path": plan.registration_path,
            "registration_sha256": registration_sha256,
        }
        ruled = armable_registration(registration_sha256)
        superseded = RULED_REGISTRATIONS.get(registration_sha256, {}).get("superseded_by")
        defect = None
        bound = None
        if superseded:
            defect = (f"registration sha256 {registration_sha256} was superseded by "
                      f"{superseded} and is no longer armable")
        elif ruled is None:
            defect = f"registration sha256 {registration_sha256} is not a ruled registration"
        elif ruled["binds_chain"]:
            try:
                bound = json.loads(registration_text)["chain_source_sha256"]
                measured = rows["C5"].measured.get("chain_source_sha256")
                if not isinstance(bound, str) or _SHA256_RE.fullmatch(bound) is None or bound != measured:
                    raise ValueError(f"registration binds chain source {bound}; measured source is {measured}")
            except (ValueError, KeyError, TypeError) as exc:
                defect = str(exc)
        elif (rows["C5"].measured.get("payload_kind") in NIGHT_KINDS and
              kind_row(rows["C5"].measured["payload_kind"]).requires_chain_bound_registration):
            defect = "evidence payload requires its chain-bound ruled registration"
        if defect is not None:
            return _finish(
                plan,
                probes,
                rows,
                Refusal(
                    "night_refused_registration",
                    defect,
                    tuple(evidence),
                ),
                authored_monotonic_ns=clock_monotonic_ns,
            )
        rows["C1"].status = "PASS"
        rows["C1"].measured.update(registration_label=ruled["label"], registration_ruling=ruled["ruling"])
        if ruled["binds_chain"]:
            rows["C1"].measured["registration_bound_chain_source_sha256"] = bound
        rows["C1"].measured["detail"] = ("D-166 registration hash passed"
            if registration_sha256 == D166_REGISTRATION_SHA256 else f"registration hash passed: {ruled['label']}")



def evaluate_static(plan: NightPlan, probes: Probes) -> Receipt:
    """V4 static evidence only; a partial result is never launch authority."""
    from joulewise.quiet_admission import validate_policy
    rows = _initial_conditions(plan.receipt_class)
    evidence = []
    try:
        validate_policy(plan.quiet_admission, window_max_s=plan.window_max_s)
        if plan.receipt_class == "TRANSACTION_PACK":
            raise ValueError("quiet admission is packless only")
    except (ValueError, OverflowError) as error:
        return _finish(plan, probes, rows, Refusal("night_plan_malformed", str(error), ()))
    for check in (_check_static_start, _check_chain_identity, _check_registration):
        refused = check(plan, probes, rows, evidence)
        if refused is not None:
            return refused
    return replace(_finish(plan, probes, rows, None), verdict="PENDING")


def evaluate_dynamic_hard(plan: NightPlan, probes: Probes, static: Receipt) -> Receipt:
    """Re-observe every hard predicate; CPU admission belongs to the driver."""
    rows = {row.condition_id: _MutableCondition(row.status, row.basis, list(row.evidence),
                                               dict(row.measured)) for row in static.conditions}
    evidence = []
    refused = _check_census(plan, probes, rows, evidence, strict=True)
    if refused is not None:
        return refused
    refused = _check_machine(plan, probes, rows, evidence, legacy_load=False)
    if refused is not None:
        return refused
    refused = _check_clock(plan, probes, rows, evidence, strict_probe=True)
    if refused is not None:
        return refused
    return replace(_finish(plan, probes, rows, None,
                   authored_monotonic_ns=rows["C4"].measured["clock_monotonic_ns"]), verdict="PENDING")


def evaluate_night(plan: NightPlan, probes: Probes, *, pack_arm_receipt=None, pack_conditions=None) -> Receipt:
    """Legacy one-shot composition, preserving probe order and receipt bytes.

    A v4 caller must use the supervised driver bind loop; no one-shot call can
    authorize an interval plan.
    """
    del pack_conditions
    rows = _initial_conditions(plan.receipt_class)
    evidence = []
    pack_arm = None
    if plan.quiet_admission is not None:
        raise PlanError("night_probe_error", "v4 requires supervised interval admission in run_night")
    for check in (_check_static_start, _check_census, _check_chain_identity):
        refused = check(plan, probes, rows, evidence)
        if refused is not None:
            return refused
    if plan.receipt_class == "TRANSACTION_PACK" and plan.pack_night is None:
        return _finish(
            plan,
            probes,
            rows,
            Refusal(
                "night_refused_class_unbuilt",
                "stage 3 not implemented: TRANSACTION_PACK is pack-bound and stays under E-10 (ruling R-10)",
                (),
            ),
        )

    if plan.receipt_class == "TRANSACTION_PACK":
        try:
            pack_arm = _evaluate_pack_conditions(plan, probes, rows, pack_arm_receipt)
        except (OSError, ValueError, RuntimeError, KeyError, TypeError, ImportError) as exc:
            return _finish(plan, probes, rows, Refusal(
                getattr(exc, "reason", "launch_go_receipt_invalid"), str(exc), ()))

    refused = _check_machine(plan, probes, rows, evidence)
    if refused is not None:
        return refused
    refused = _check_clock(plan, probes, rows, evidence, pack_arm=pack_arm)
    if refused is not None:
        return refused
    refused = _check_registration(plan, probes, rows, evidence)
    if refused is not None:
        return refused
    return _finish(plan, probes, rows, None,
                   authored_monotonic_ns=rows["C4"].measured["clock_monotonic_ns"])


def _exact_keys(value: object, expected: set[str], where: str, defects: list[str]) -> bool:
    if not isinstance(value, Mapping):
        defects.append(f"{where}: must be an object")
        return False
    keys = set(value)
    if keys != expected:
        defects.append(
            f"{where}: keys are not exact "
            f"(missing={sorted(repr(item) for item in expected - keys)}, "
            f"extra={sorted(repr(item) for item in keys - expected)})"
        )
        return False
    return True


def _validate_probe(value: object, where: str, defects: list[str]) -> None:
    if not _exact_keys(value, _PROBE_RESULT_KEYS, where, defects):
        return
    argv = value.get("argv")
    if not isinstance(argv, list) or not argv or any(not isinstance(item, str) for item in argv):
        defects.append(f"{where}.argv: must be a non-empty array of strings")
    exit_code = value.get("exit_code")
    if isinstance(exit_code, bool) or not isinstance(exit_code, int):
        defects.append(f"{where}.exit_code: must be an integer")
    for field in ("stdout", "stderr"):
        if not isinstance(value.get(field), str):
            defects.append(f"{where}.{field}: must be a string")
    monotonic_ns = value.get("monotonic_ns")
    if isinstance(monotonic_ns, bool) or not isinstance(monotonic_ns, int) or monotonic_ns < 0:
        defects.append(f"{where}.monotonic_ns: must be a non-negative integer")


def _validate_quiet_receipt(value, defects):
    from joulewise.quiet_admission import validate_policy
    if value["admission_is_capture_evidence"] is not False:
        defects.append("admission_is_capture_evidence: must be false")
    if "journal_failure" in value:
        if (not isinstance(value["journal_failure"], str) or not value["journal_failure"].strip()
                or value["verdict"] != "REFUSED"):
            defects.append("journal_failure: requires a reason and REFUSED verdict")
    if "supervision_residue" in value:
        residue = value["supervision_residue"]
        if (value["verdict"] != "REFUSED" or not isinstance(residue, list)
                or not 1 <= len(residue) <= 32):
            defects.append("supervision_residue: requires 1..32 jobs and REFUSED verdict")
        else:
            for job in residue:
                if (not isinstance(job, Mapping) or set(job) != {"job_id", "kind", "pid", "state"}
                        or not isinstance(job["job_id"], str) or not job["job_id"]
                        or not isinstance(job["kind"], str) or job["kind"] not in {"static", "hard", "sample", "census"}
                        or (job["pid"] is not None and (type(job["pid"]) is not int or job["pid"] <= 0))
                        or not isinstance(job["state"], str) or job["state"] not in {"launch_pending", "unreaped"}):
                    defects.append("supervision_residue: malformed job")
    if "observer_cpu_s" in value:
        cost = value["observer_cpu_s"]
        if type(cost) not in (int, float) or not math.isfinite(cost) or cost < 0:
            defects.append("observer_cpu_s: expected nonnegative whole-round CPU seconds")
    if "boot_identity_unavailable" in value:
        if (not isinstance(value["boot_identity_unavailable"], str)
                or not value["boot_identity_unavailable"].strip()
                or value["verdict"] != "REFUSED"):
            defects.append("boot_identity_unavailable: requires a reason and REFUSED verdict")
    try:
        policy = validate_policy(value["quiet_admission"])
    except (ValueError, OverflowError):
        defects.append("quiet_admission: invalid policy")
        policy = None
    if value["receipt_class"] == "TRANSACTION_PACK":
        defects.append("quiet receipt is packless only")
    for key in ("samples_total", "samples_quiet_run_at_go", "quiet_samples_lines"):
        if type(value[key]) is not int or value[key] < 0:
            defects.append(f"{key}: expected nonnegative integer")
    if (type(value["samples_total"]) is int and type(value["samples_quiet_run_at_go"]) is int
            and value["samples_quiet_run_at_go"] > value["samples_total"]):
        defects.append("samples_quiet_run_at_go: exceeds samples_total")
    if value["samples_total"] != value["quiet_samples_lines"]:
        defects.append("quiet_samples_lines: differs from samples_total")
    if not isinstance(value["quiet_samples_sha256"], str) or _SHA256_RE.fullmatch(value["quiet_samples_sha256"]) is None:
        defects.append("quiet_samples_sha256: invalid digest")
    deadline, go = value["bind_deadline_epoch_s"], value["go_epoch_s"]
    def finite(number):
        try:
            return type(number) in (int, float) and math.isfinite(number)
        except OverflowError:
            return False
    if not finite(deadline):
        defects.append("bind_deadline_epoch_s: invalid epoch")
    if value["verdict"] in {"GO", "REHEARSAL_ONLY"}:
        if policy and policy["busy_core_max"] == 0:
            defects.append("quiet_admission: zero cutoff cannot authorize admission")
        if not finite(go) or not finite(deadline) or go > deadline:
            defects.append("go_epoch_s: must complete by bind deadline")
        if policy and (type(value["samples_quiet_run_at_go"]) is not int
                or value["samples_quiet_run_at_go"] < policy["consecutive_quiet_samples"]):
            defects.append("samples_quiet_run_at_go: insufficient consecutive intervals")
    elif go is not None or value["samples_quiet_run_at_go"] != 0:
        defects.append("refusal: GO fields must be null/zero")
    consumers = value["top_consumers_at_decision"]
    if not isinstance(consumers, list) or len(consumers) > 10:
        defects.append("top_consumers_at_decision: expected at most ten consumers")
    elif not consumers and (not isinstance(value.get("attribution_unavailable"), str)
                           or not value["attribution_unavailable"]):
        defects.append("attribution_unavailable: required when no consumers are available")
    else:
        for item in consumers:
            if (not isinstance(item, Mapping) or type(item.get("pid")) is not int
                    or not isinstance(item.get("command"), str)
                    or not finite(item.get("busy_cores")) or item["busy_cores"] < 0
                    or type(item.get("observer")) is not bool):
                defects.append("top_consumers_at_decision: malformed consumer")
    if not isinstance(value["load_avg_diagnostic"], Mapping):
        defects.append("load_avg_diagnostic: expected diagnostic object")


def validate_receipt(value: Mapping[str, object]) -> list[str]:
    defects: list[str] = []
    quiet = isinstance(value, Mapping) and value.get("schema") == QUIET_RECEIPT_SCHEMA
    receipt_codes = NIGHT_GATE_REASON_CODES if quiet else NIGHT_GATE_REASON_CODES - {"night_refused_bind_expired"}
    expected = _RECEIPT_KEYS | _QUIET_RECEIPT_KEYS if quiet else _RECEIPT_KEYS
    if quiet and "attribution_unavailable" in value:
        expected = expected | {"attribution_unavailable"}
    if quiet and "boot_identity_unavailable" in value:
        expected = expected | {"boot_identity_unavailable"}
    if quiet:
        expected = expected | ({"journal_failure", "observer_cpu_s", "supervision_residue"} & set(value))
    if not _exact_keys(value, expected, "receipt", defects):
        return defects
    if quiet:
        _validate_quiet_receipt(value, defects)
    if not quiet and value.get("schema") != SCHEMA:
        defects.append(f"schema: must be {SCHEMA}")
    receipt_class = value.get("receipt_class")
    if receipt_class not in RECEIPT_CLASSES:
        defects.append("receipt_class: is not registered")
        defects.append("night_receipt_class_invalid: unknown receipt_class")
        class_rules = None
    else:
        class_rules = class_table()[receipt_class]
    if not isinstance(value.get("plan_id"), str) or not value.get("plan_id"):
        defects.append("plan_id: must be a non-empty string")
    verdict = value.get("verdict")
    if not isinstance(verdict, str) or verdict not in _VERDICTS:
        defects.append("verdict: must be GO, REFUSED, or REHEARSAL_ONLY")
    authored = value.get("authored_monotonic_ns")
    if isinstance(authored, bool) or not isinstance(authored, int) or authored < 0:
        defects.append("authored_monotonic_ns: must be a non-negative integer")

    condition_values = value.get("conditions")
    parsed_rows: dict[str, Mapping[str, object]] = {}
    if not isinstance(condition_values, list):
        defects.append("conditions: must be an array")
    elif len(condition_values) != len(_CONDITION_IDS):
        defects.append("conditions: must contain exactly C1 through C5")
    else:
        ids = [
            item.get("condition_id") if isinstance(item, Mapping) else None
            for item in condition_values
        ]
        if sorted(ids, key=str) != list(_CONDITION_IDS):
            defects.append("conditions.condition_id: must be exactly C1 through C5")
        for index, item in enumerate(condition_values):
            where = f"conditions[{index}]"
            if not _exact_keys(item, _CONDITION_KEYS, where, defects):
                continue
            status = item.get("status")
            basis = item.get("basis")
            if not isinstance(status, str) or status not in _STATUSES:
                defects.append(f"{where}.status: is not registered")
            if basis is not None and not isinstance(basis, str):
                defects.append(f"{where}.basis: must be null or a string")
            row_evidence = item.get("evidence")
            if not isinstance(row_evidence, list) or any(
                not isinstance(citation, str) for citation in row_evidence
            ):
                defects.append(f"{where}.evidence: must be an array of strings")
            if not isinstance(item.get("measured"), Mapping):
                defects.append(f"{where}.measured: must be an object")
            condition_id = item.get("condition_id")
            if isinstance(condition_id, str) and condition_id in _CONDITION_IDS:
                parsed_rows[condition_id] = item
            if (
                class_rules is not None
                and isinstance(condition_id, str)
                and condition_id in class_rules
            ):
                required, registered_basis = class_rules[str(condition_id)]
                if required == "NOT_APPLICABLE":
                    if status != required or basis != registered_basis:
                        defects.append(
                            f"night_receipt_class_invalid: {receipt_class} {condition_id} must be NOT_APPLICABLE with basis {registered_basis}"
                        )
                elif status == "NOT_APPLICABLE" or basis is not None:
                    defects.append(
                        f"night_receipt_class_invalid: {receipt_class} {condition_id} requires PASS/FAIL with null basis"
                    )

    refusal_value = value.get("refusal")
    if refusal_value is not None:
        if _exact_keys(refusal_value, _REFUSAL_KEYS, "refusal", defects):
            reason = refusal_value.get("reason")
            if not isinstance(reason, str) or reason not in receipt_codes:
                defects.append("refusal.reason: is not registered")
            detail = refusal_value.get("detail")
            if not isinstance(detail, str) or not detail:
                defects.append("refusal.detail: must be a non-empty string")
            refusal_evidence = refusal_value.get("evidence")
            if not isinstance(refusal_evidence, list):
                defects.append("refusal.evidence: must be an array")
            else:
                for index, result in enumerate(refusal_evidence):
                    _validate_probe(result, f"refusal.evidence[{index}]", defects)

    if verdict == "REFUSED":
        if not isinstance(refusal_value, Mapping):
            defects.append("refusal: REFUSED verdict requires a refusal object")
        elif refusal_value.get("reason") not in receipt_codes:
            defects.append("refusal.reason: REFUSED verdict requires a registered gate code")
    elif (
        isinstance(verdict, str)
        and verdict in {"GO", "REHEARSAL_ONLY"}
        and refusal_value is not None
    ):
        defects.append(f"refusal: {verdict} verdict requires null")

    if class_rules is not None and len(parsed_rows) == len(_CONDITION_IDS):
        target_green = all(
            parsed_rows[condition_id].get("status") == required
            and parsed_rows[condition_id].get("basis") == basis
            for condition_id, (required, basis) in class_rules.items()
        )
        no_refusal = refusal_value is None
        if receipt_class == "REHEARSAL_STUB" and target_green and no_refusal:
            expected_verdict = "REHEARSAL_ONLY"
        elif target_green and no_refusal:
            expected_verdict = "GO"
        else:
            expected_verdict = "REFUSED"
        if verdict != expected_verdict:
            defects.append(
                f"verdict: {receipt_class} rows/refusal require {expected_verdict}"
            )
    return defects
