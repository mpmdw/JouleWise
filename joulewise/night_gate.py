"""Pure evaluation logic for unattended quiet-machine nights.

The module deliberately owns no machine I/O.  Callers provide every clock,
filesystem, repository, and process observation through :class:`Probes`.
Result records belong to the driver, which defines and validates ``result.json``.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import uuid
from dataclasses import dataclass
from typing import Callable, Mapping


SCHEMA = "joulewise.unattended_night_receipt.v2"
PLAN_SCHEMA = "joulewise.night_plan.v2"
RECEIPT_CLASSES = (
    "DIAGNOSTIC_NO_PACK",
    "REHEARSAL_STUB",
    "TRANSACTION_PACK",
)
D166_REGISTRATION_SHA256 = (
    "1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b"
)
# Tracked file whose bytes are canonical_json_bytes(dominance_criterion_registration());
# a night plan's registration_path points at it (repo-relative or absolute).
D166_REGISTRATION_PATH = (
    "configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json"
)
AGENT_CENSUS_ARGV = ("/usr/bin/pgrep", "-lf", "codex|claude|t3")

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
PLAN_MAX_AGE_S = 36 * 60 * 60

NIGHT_GATE_REASON_CODES = frozenset(
    {
        "night_refused_agent_present",
        "night_refused_not_quiet",
        "night_refused_hid_idle",
        "night_refused_boot_clock",
        "night_refused_registration",
        "night_window_expired",
        "night_plan_stale",
        "night_plan_malformed",
        "night_chain_digest_mismatch",
        "night_refused_class_unbuilt",
        "night_receipt_class_invalid",
        "night_probe_error",
    }
)

# Codes the DRIVER (scripts/run_night.py) emits after the gate has said GO.
# They live here so the registry has one home (ruling R-8); the gate itself
# never emits them.  Cold gate coldgate-e10 (2026-09-01) d.3 and the Opus
# refuter's once-only finding are their forcing problems.
NIGHT_DRIVER_REASON_CODES = frozenset(
    {
        "night_aborted_agent_present",   # census hit while the chain ran; chain group terminated
        "night_chain_already_started",   # O_EXCL claim on chain.started failed: never start the chain twice (D-078)
        "night_chain_alive",             # dead-man refused: the chain has not exited, so no agent may start
        "night_chain_launch_failed",     # chain Popen failed after the once-only start claim
        "night_courier_running",          # dead-man found a fresh courier lock owned by a live process
        "night_courier_unavailable",      # the stamped courier binary is missing or not executable
        "night_plan_overruns_deadman",   # t0 + window_max_s + courier deadline is not before the dead-man hour
        "night_record_exists",            # a write-once record proves this night was already invoked
    }
)
if NIGHT_GATE_REASON_CODES & NIGHT_DRIVER_REASON_CODES:
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
_RECEIPT_KEYS = {
    "schema",
    "receipt_class",
    "plan_id",
    "verdict",
    "conditions",
    "refusal",
    "authored_monotonic_ns",
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

    @staticmethod
    def from_mapping(value: Mapping[str, object]) -> "NightPlan":
        if not isinstance(value, Mapping):
            raise PlanError("night_plan_malformed", "plan must be an object")
        keys = set(value)
        if keys != _PLAN_KEYS:
            missing = sorted(repr(item) for item in _PLAN_KEYS - keys)
            extra = sorted(repr(item) for item in keys - _PLAN_KEYS)
            raise PlanError(
                "night_plan_malformed",
                f"plan keys are not exact (missing={missing}, extra={extra}); "
                "joulewise.night_plan.v1 is retired and the plan must be "
                "re-authored under joulewise.night_plan.v2",
            )
        if value.get("schema") != PLAN_SCHEMA:
            raise PlanError(
                "night_plan_malformed",
                "schema joulewise.night_plan.v1 is retired and the plan must be "
                "re-authored under joulewise.night_plan.v2",
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
                "measurement_root must be an absolute path; "
                "joulewise.night_plan.v1 is retired and the plan must be "
                "re-authored under joulewise.night_plan.v2",
            )
        measurement_head = require_text("measurement_head")
        if _HEAD_RE.fullmatch(measurement_head) is None:
            raise PlanError(
                "night_plan_malformed",
                "measurement_head must be exactly 40 lowercase hexadecimal characters; "
                "joulewise.night_plan.v1 is retired and the plan must be "
                "re-authored under joulewise.night_plan.v2",
            )
        chain_path = require_text("chain_path")
        chain_sha256_path = require_text("chain_sha256_path")
        custody_root = require_text("custody_root")
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


def _run(probes: Probes, argv: tuple[str, ...]) -> ProbeResult:
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


def agent_census(probes: Probes) -> tuple[ProbeResult, Refusal | None]:
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


def evaluate_night(plan: NightPlan, probes: Probes) -> Receipt:
    rows = _initial_conditions(plan.receipt_class)
    evidence: list[ProbeResult] = []

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
    try:
        measurement_checkout_head = probes.measurement_head(plan.measurement_root)
        checkout_head = probes.checkout_head()
    except Exception as exc:
        return _probe_refusal(plan, probes, rows, evidence, exc)
    rows["C5"].measured.update(
        {
            "authored_epoch_s": plan.authored_epoch_s,
            "plan_repo_head": plan.repo_head,
            "driver_checkout_head": checkout_head,
            "measurement_root": plan.measurement_root,
            "plan_measurement_head": plan.measurement_head,
            "measurement_checkout_head": measurement_checkout_head,
        }
    )
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

    census_result, census_refusal = agent_census(probes)
    evidence.append(census_result)
    rows["C3"].evidence.append(_probe_citation(census_result))
    rows["C3"].measured = {
        "agent_census_exit_code": census_result.exit_code,
        "agent_census_stdout": census_result.stdout,
    }
    if census_refusal is not None:
        return _finish(plan, probes, rows, census_refusal)

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
    rows["C5"].status = "PASS"
    rows["C5"].measured["detail"] = (
        "window, plan freshness, measurement HEAD, and chain identity passed"
    )

    if plan.receipt_class == "TRANSACTION_PACK":
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

    # R-6's unattended HID predicate precedes the remaining quiet predicates.
    try:
        hid = _run(probes, HID_IDLE_ARGV)
    except ProbeError as exc:
        return _probe_refusal(plan, probes, rows, evidence, exc)
    evidence.append(hid)
    rows["C3"].evidence.append(_probe_citation(hid))
    rows["C3"].measured["hid_idle_raw"] = hid.stdout
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
    except ProbeError as exc:
        return _probe_refusal(plan, probes, rows, evidence, exc)
    rows["C3"].status = "PASS"
    rows["C3"].measured["detail"] = "agent, HID, AC, display, load, and thermal predicates passed"

    # C4 is deliberately local-only: boot UUID plus an epoch/monotonic pair.
    try:
        boot = _run(probes, BOOT_SESSION_ARGV)
    except ProbeError as exc:
        return _probe_refusal(plan, probes, rows, evidence, exc)
    evidence.append(boot)
    rows["C4"].evidence.append(_probe_citation(boot))
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
    rows["C4"].status = "PASS"
    rows["C4"].measured = {
        "boot_session_uuid": canonical_uuid,
        "clock_epoch_s": clock_epoch_s,
        "clock_monotonic_ns": clock_monotonic_ns,
    }
    rows["C4"].evidence.append("clock:epoch+monotonic")

    if plan.receipt_class in {"DIAGNOSTIC_NO_PACK", "REHEARSAL_STUB"}:
        try:
            registration_text = probes.read_text(plan.registration_path)
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
        if registration_sha256 != D166_REGISTRATION_SHA256:
            return _finish(
                plan,
                probes,
                rows,
                Refusal(
                    "night_refused_registration",
                    f"registration sha256 {registration_sha256} does not match D-166 registration",
                    tuple(evidence),
                ),
                authored_monotonic_ns=clock_monotonic_ns,
            )
        rows["C1"].status = "PASS"
        rows["C1"].measured["detail"] = "D-166 registration hash passed"

    return _finish(
        plan,
        probes,
        rows,
        None,
        authored_monotonic_ns=clock_monotonic_ns,
    )


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


def validate_receipt(value: Mapping[str, object]) -> list[str]:
    defects: list[str] = []
    if not _exact_keys(value, _RECEIPT_KEYS, "receipt", defects):
        return defects
    if value.get("schema") != SCHEMA:
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
            if not isinstance(reason, str) or reason not in NIGHT_GATE_REASON_CODES:
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
        elif refusal_value.get("reason") not in NIGHT_GATE_REASON_CODES:
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
