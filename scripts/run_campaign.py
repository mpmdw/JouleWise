#!/usr/bin/env python3
"""Run a generated Slice 2M config directory sequentially.

The JouleWise CLI has two bundle layouts. A config with
``workload_profile.repetitions == 1`` creates one bundle at
``<runs_dir>/<run_id>/``. A config with repetitions greater than one dispatches
to the experiment runner and creates one member bundle per repetition at
``<runs_dir>/<run_id>__r1`` ... ``<runs_dir>/<run_id>__rN`` plus an incremental
manifest at ``<runs_dir>/experiments/<run_id>.json``.

The manifest is not a completion marker. Completion is detected only from each
member bundle's ``summary_metrics.json``. If a process is interrupted after some
members have been created, a later campaign sees those partial members as
``incomplete_existing`` and does not re-run; the operator must inspect or move
the member bundles before retrying because the real CLI would collide on the
existing run IDs.

Dry-run mode prints the exact plan and invokes nothing. It also writes no
campaign log entries; JSONL logging is reserved for actual campaign attempts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shlex
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.bundle import sanitize_id_component  # noqa: E402
from joulewise.cli import validate_bundle  # noqa: E402
from joulewise.bundle_read import (  # noqa: E402
    AXI_VALIDATOR_REASON_CODES,
    BundleReader,
    BundleReadError,
)
from joulewise.analysis_manifest import validate_analysis_manifest  # noqa: E402
from joulewise.analysis_engine.registry import (  # noqa: E402
    ATTEMPT_LEDGER_SCHEMA_VERSION,
    AnalysisManifestError,
    MANIFEST_SCHEMA_VERSION as AXI_MANIFEST_SCHEMA_VERSION,
    STRICT_EVIDENCE_SCHEMA_VERSION,
    canonical_json_bytes as axi_canonical_json_bytes,
    load_and_validate_analysis_manifest_v2,
    render_attempt_ledger,
    render_strict_validation_evidence,
    sha256_bytes as axi_sha256_bytes,
    validate_attempt_ledger,
)
from joulewise.controller import finalize_dispatch_receipt  # noqa: E402
from joulewise.controller import (  # noqa: E402
    CAMPAIGN_POLICY_PATH_ENV,
    CAMPAIGN_POLICY_SHA256_ENV,
    CAMPAIGN_PREFLIGHT_JSON_ENV,
)
from joulewise.cooldown_anchor import cooldown_anchor_eligibility  # noqa: E402
from joulewise.doctor import SCHEMA_VERSION as DOCTOR_SCHEMA_VERSION  # noqa: E402
from joulewise.doctor import config_warning_gate  # noqa: E402
from joulewise.environment import (  # noqa: E402
    collect_environment_snapshot,
    empty_environment_snapshot,
    evaluate_environment_policy,
)
from joulewise.analysis_engine.inputs import (  # noqa: E402
    cleanup_claim_evidence_flags,
    token_provenance_from_artifacts,
)
from joulewise.analysis_engine.ratio import (  # noqa: E402
    estimation_metric,
    ratio_collection_evidence_reasons,
    ratio_evidence_reasons,
)
from joulewise.schemas import (  # noqa: E402
    CampaignPolicy,
    CooldownPolicy,
    PromptTokenEvidencePolicy,
    RunStatus,
    RuntimeBackend,
    TelemetryBackend,
)
from joulewise.interfaces import AttemptIdentity  # noqa: E402
from joulewise.output_identity import (  # noqa: E402
    build_output_identity_report,
    render_output_identity_report,
)


STATUSES = (
    "ok",
    "failed",
    "skipped",
    "waived",
    "incomplete_existing",
    "config_error",
    "dry_run",
)
ORDER_MANIFEST_NAME = "order_manifest.json"
ANALYSIS_MANIFEST_NAME = "analysis_manifest.json"
NON_CONFIG_SIDECARS = frozenset({ORDER_MANIFEST_NAME, ANALYSIS_MANIFEST_NAME})
CAMPAIGN_VERDICT_SCHEMA = "joulewise.campaign_verdict.v2"
CAMPAIGN_PROVENANCE_SCHEMA = "joulewise.campaign_provenance.v1"
CLAIM_READINESS_NOTE = (
    "This verdict checks analysis inputs only; P2-037 decides claim outcomes."
)
ACCEPTED_CAMPAIGN_COOLDOWN_RESULTS = frozenset({"recovered", "first_run_exempt"})
DEFAULT_CAMPAIGN_POLICY = (
    ROOT / "configs" / "campaign_policies" / "quiet_mac_p2_production.json"
)
KNOWN_NON_PROMPT_SIDECAR_SCHEMAS = frozenset(
    {
        "affine_smoke_annotations.v1",
    }
)


@dataclass(frozen=True)
class ConfigInfo:
    path: Path
    run_id: str
    raw_run_id: str
    repetitions: int
    generator_sidecar_ref: str | None = None
    suite_manifest_ref: str | None = None
    prompt_token_evidence_policy: PromptTokenEvidencePolicy | None = None


@dataclass(frozen=True)
class ConfigError:
    path: Path
    message: str
    run_id: str | None = None


@dataclass(frozen=True)
class ExistingState:
    action: str
    members_succeeded: int | None = None
    members_total: int | None = None
    non_succeeded_members: tuple[str, ...] = ()
    inspect_members: tuple[str, ...] = ()
    malformed_summaries: tuple[str, ...] = ()


@dataclass(frozen=True)
class Waiver:
    target_kind: str
    target: str
    reason: str
    approver: str
    timestamp: str
    scope: str


@dataclass(frozen=True)
class CampaignPolicyBinding:
    path: Path
    policy: CampaignPolicy
    sha256: str

    def to_metadata(self) -> dict[str, Any]:
        return {
            "schema_version": self.policy.schema_version,
            "policy_id": self.policy.policy_id,
            "policy_version": self.policy.policy_version,
            "profile": self.policy.profile.value,
            "sha256": self.sha256,
            "source": str(self.path),
        }


@dataclass(frozen=True)
class PromptHashCheck:
    status: str
    sidecar_path: str | None = None
    checked_items: int = 0
    matches: tuple[dict[str, Any], ...] = ()
    problems: tuple[str, ...] = ()

    def collection_integrity_flags(self) -> tuple[str, ...]:
        if self.status == "mismatch":
            return ("prompt_hash_mismatch",)
        if self.status == "error":
            return ("prompt_hash_check_error",)
        if self.status == "missing_evidence":
            return ("prompt_token_evidence_missing",)
        return ()

    def to_log(self) -> dict[str, Any]:
        row: dict[str, Any] = {
            "status": self.status,
            "checked_items": self.checked_items,
        }
        if self.sidecar_path is not None:
            row["sidecar_path"] = self.sidecar_path
        if self.matches:
            row["matches"] = list(self.matches)
        if self.problems:
            row["problems"] = list(self.problems)
        return row


@dataclass(frozen=True)
class MemberEvaluation:
    bundle_id: str
    bundle_path: Path
    config_name: str
    status: str | None
    strict_valid: bool
    validation_problems: tuple[str, ...] = ()
    collection_integrity_flags: tuple[str, ...] = ()
    claim_evidence_flags: tuple[str, ...] = ()
    runtime_cleanup_ok: bool | None = None
    remote_cleanup_failed: tuple[str, ...] = ()
    ratio_token_provenance: dict[str, Any] = field(
        default_factory=dict, repr=False, compare=False
    )
    prompt_hash_check: PromptHashCheck = field(
        default_factory=lambda: PromptHashCheck("not_applicable")
    )
    suite_order_policy: str | None = None
    suite_order_row: int | None = None
    suite_order_seed: str | None = None
    waiver: Waiver | None = None
    summary: dict[str, Any] | None = field(default=None, repr=False, compare=False)
    metadata: dict[str, Any] | None = field(default=None, repr=False, compare=False)
    preceding_campaign_cooldown: dict[str, Any] | None = field(
        default=None, repr=False, compare=False
    )

    def failure_classes(self) -> tuple[str, ...]:
        classes: list[str] = []
        if self.status is not None and self.status != "succeeded":
            classes.append("status_failed")
        if not self.strict_valid:
            classes.append("strict_invalid")
        classes.extend(self.collection_integrity_flags)
        return tuple(dict.fromkeys(classes))

    def waiver_classes(self) -> tuple[str, ...]:
        return self.failure_classes()

    def unwaived_claim_evidence_flags(self) -> tuple[str, ...]:
        # Claim-scope waivers are collection audit context only. They never
        # clear a claim-evidence flag or support readiness.
        return self.claim_evidence_flags

    @property
    def usable(self) -> bool:
        return (
            self.status == "succeeded"
            and self.strict_valid
            and not self.collection_integrity_flags
        )

    @property
    def waived(self) -> bool:
        if self.waiver is None:
            return False
        classes = self.waiver_classes()
        if not classes:
            return False
        if self.waiver.scope == "any":
            return True
        scopes = {part.strip() for part in self.waiver.scope.split(",") if part.strip()}
        return all(failure_class in scopes for failure_class in classes)

    @property
    def failed(self) -> bool:
        return not self.usable and not self.waived

    def to_log(self) -> dict[str, Any]:
        row: dict[str, Any] = {
            "bundle_id": self.bundle_id,
            "bundle_path": str(self.bundle_path),
            "status": self.status,
            "strict_valid": self.strict_valid,
            "validation_problems": list(self.validation_problems),
            "collection_integrity_flags": list(self.collection_integrity_flags),
            "claim_evidence_flags": list(self.claim_evidence_flags),
            "runtime_cleanup_ok": self.runtime_cleanup_ok,
            "remote_cleanup_failed": list(self.remote_cleanup_failed),
            "prompt_hash_check": self.prompt_hash_check.to_log(),
            "collection_classification": (
                "usable" if self.usable else "waived" if self.waived else "failed"
            ),
            "claim_evidence_classification": (
                "flagged" if self.claim_evidence_flags else "clean"
            ),
        }
        if self.waiver is not None:
            row["waiver"] = {
                "target_kind": self.waiver.target_kind,
                "target": self.waiver.target,
                "reason": self.waiver.reason,
                "approver": self.waiver.approver,
                "timestamp": self.waiver.timestamp,
                "scope": self.waiver.scope,
            }
        if self.suite_order_policy is not None:
            row["suite_order_policy"] = self.suite_order_policy
        if self.suite_order_row is not None:
            row["suite_order_row"] = self.suite_order_row
        if self.suite_order_seed is not None:
            row["suite_order_seed"] = self.suite_order_seed
        if self.preceding_campaign_cooldown is not None:
            row["preceding_campaign_cooldown"] = self.preceding_campaign_cooldown
        return row


@dataclass(frozen=True)
class AnalysisManifestState:
    path: Path
    raw: dict[str, Any]
    manifest_id: str | None
    file_sha256: str
    problems: tuple[str, ...] = ()

    @property
    def valid(self) -> bool:
        return not self.problems

    @property
    def is_axi_v2(self) -> bool:
        return self.raw.get("schema_version") == AXI_MANIFEST_SCHEMA_VERSION

    def to_log(self) -> dict[str, Any]:
        row = {
            "manifest_id": self.manifest_id,
            "file_sha256": self.file_sha256,
            "validation": "valid" if self.valid else "invalid",
        }
        if self.problems:
            row["problems"] = list(self.problems)
        return row


@dataclass(frozen=True)
class OrderEntry:
    index: int
    config: str
    run_id: str | None = None
    model_tag: str | None = None
    rep: int | None = None
    workload: str | None = None
    role: str | None = None
    block_index: int | None = None
    position_in_block: int | None = None
    sentinel_position: str | None = None

    def to_log(self) -> dict[str, Any]:
        row: dict[str, Any] = {
            "index": self.index,
            "config": self.config,
            "model_tag": self.model_tag,
            "rep": self.rep,
            "workload": self.workload,
        }
        for field_name in (
            "run_id",
            "role",
            "block_index",
            "position_in_block",
            "sentinel_position",
        ):
            value = getattr(self, field_name)
            if value is not None:
                row[field_name] = value
        return row


VALID_WAIVER_SCOPES = {
    "any",
    "status_failed",
    "strict_invalid",
    "idle_window_suspect",
    "prompt_hash_mismatch",
    "prompt_hash_check_error",
    "runtime_cleanup_ok",
    "remote_cleanup_failed",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config_dir", nargs="?", help="Directory containing generated JSON configs")
    parser.add_argument("--runs-dir", default="runs", help="Bundle output directory")
    parser.add_argument("--log", help="JSONL campaign log path")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without invoking benchmarks")
    parser.add_argument(
        "--backup",
        nargs="?",
        const="",
        help="Run scripts/backup_runs.sh, or a supplied backup command path, after each success",
    )
    parser.add_argument(
        "--shakedown-gate",
        choices=("production_uncertainty_v1",),
        help="Require the P2-038 single-bundle strict/reduce/evidence/backup gate",
    )
    parser.add_argument("--max-failures", type=int, default=1, help="Stop after this many failures")
    parser.add_argument(
        "--cli-cmd",
        help="Command prefix replacing '<python> -m joulewise'; 'run <config> --runs-dir <dir>' is appended",
    )
    parser.add_argument(
        "--waivers",
        help="Optional JSON file listing campaign waivers; waivers are never written into bundles",
    )
    parser.add_argument(
        "--ack-config-warnings",
        action="store_true",
        help="Acknowledge doctor-reported ignored config keys and record that fact in the campaign verdict",
    )
    parser.add_argument(
        "--campaign-policy",
        default=str(DEFAULT_CAMPAIGN_POLICY),
        help=(
            "Hash-bound campaign policy sidecar "
            f"(default: {DEFAULT_CAMPAIGN_POLICY})"
        ),
    )
    parser.add_argument(
        "--arm-quiet-mode",
        action="store_true",
        help=(
            "Explicitly count down, request transient display sleep with "
            "pmset displaysleepnow, then re-probe; persistent settings are unchanged"
        ),
    )
    parser.add_argument(
        "--arm-countdown-s",
        type=int,
        default=5,
        help="Countdown seconds used only with --arm-quiet-mode (default: 5)",
    )
    parser.add_argument(
        "--environment-override",
        help=(
            "JSON acknowledgement bound to the exact preflight snapshot and findings; "
            "overridden members are universally claim-ineligible"
        ),
    )
    parser.add_argument(
        "--check-prompt-hashes",
        nargs=2,
        metavar=("BUNDLE_DIR", "SIDECAR_JSON"),
        help="Post-hoc expected-vs-realized prompt-hash check for one suite bundle",
    )
    args = parser.parse_args(argv)
    if args.config_dir is None and args.check_prompt_hashes is None:
        parser.error("config_dir is required unless --check-prompt-hashes is used")
    if args.config_dir is not None and args.check_prompt_hashes is not None:
        parser.error("config_dir cannot be combined with --check-prompt-hashes")
    if args.arm_countdown_s < 0:
        parser.error("--arm-countdown-s must be >= 0")
    return args


def load_campaign_policy(path_text: str) -> CampaignPolicyBinding:
    path = Path(path_text)
    raw = path.read_bytes()
    payload = json.loads(raw)
    policy = CampaignPolicy.from_mapping(payload)
    return CampaignPolicyBinding(
        path=path,
        policy=policy,
        sha256=hashlib.sha256(raw).hexdigest(),
    )


def _load_environment_override(
    path_text: str | None, evaluation: dict[str, Any]
) -> dict[str, Any] | None:
    if path_text is None:
        return None
    path = Path(path_text)
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("environment override must be a JSON object")
    required = {
        "schema_version",
        "snapshot_sha256",
        "findings_sha256",
        "reason",
        "approver",
        "timestamp",
    }
    if set(raw) != required:
        raise ValueError(
            "environment override requires exactly: " + ", ".join(sorted(required))
        )
    if raw.get("schema_version") != "joulewise.environment_override.v1":
        raise ValueError(
            "environment override schema_version must be "
            "'joulewise.environment_override.v1'"
        )
    for key in ("reason", "approver", "timestamp"):
        if not isinstance(raw.get(key), str) or not raw[key].strip():
            raise ValueError(f"environment override {key} must be a non-empty string")
    for key in ("snapshot_sha256", "findings_sha256"):
        if raw.get(key) != evaluation.get(key):
            raise ValueError(
                f"environment override {key} does not match this exact preflight"
            )
    return {
        **raw,
        "source": str(path),
        "classification": "override",
        "claim_eligible": False,
    }


def campaign_environment_preflight(
    binding: CampaignPolicyBinding,
    *,
    arm_quiet_mode: bool,
    arm_countdown_s: int,
    override_path: str | None,
) -> dict[str, Any]:
    """Collect and enforce the campaign environment after lock acquisition."""

    guard = binding.policy.environment_guard
    probe_required = any(
        (
            guard.require_ac_power,
            guard.require_external_connected,
            guard.require_low_power_mode_off,
            guard.require_displays_asleep,
            guard.require_screensaver_disengaged,
            guard.require_thermal_nominal,
        )
    )
    if probe_required:
        initial_snapshot = collect_environment_snapshot()
    else:
        initial_snapshot = empty_environment_snapshot()
        initial_snapshot.update(
            {
                "capture_skipped": True,
                "skip_reason": "policy_has_no_required_environment_probes",
            }
        )
    initial_evaluation = evaluate_environment_policy(
        initial_snapshot, binding.policy.environment_guard
    )
    arm_record: dict[str, Any] = {
        "requested": arm_quiet_mode,
        "countdown_s": arm_countdown_s if arm_quiet_mode else None,
        "command": None,
        "command_returncode": None,
        "verified_by_reprobe": False,
    }
    snapshot = initial_snapshot
    evaluation = initial_evaluation
    if arm_quiet_mode:
        for remaining in range(arm_countdown_s, 0, -1):
            print(f"Arming quiet mode in {remaining}...")
            time.sleep(1.0)
        command = ["pmset", "displaysleepnow"]
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        arm_record.update(
            {
                "command": command,
                "command_returncode": completed.returncode,
            }
        )
        snapshot = collect_environment_snapshot()
        evaluation = evaluate_environment_policy(
            snapshot, binding.policy.environment_guard
        )
        arm_record["verified_by_reprobe"] = bool(
            completed.returncode == 0 and evaluation.get("eligible") is True
        )
    override = _load_environment_override(override_path, evaluation)
    if override is not None and evaluation.get("eligible") is True:
        raise ValueError("environment override is unnecessary for a passing preflight")
    return {
        "schema_version": "joulewise.campaign_environment_preflight.v1",
        "policy_sha256": binding.sha256,
        "captured_at": utc_timestamp(),
        "snapshot": snapshot,
        "evaluation": evaluation,
        "initial_snapshot_sha256": initial_evaluation["snapshot_sha256"],
        "initial_findings_sha256": initial_evaluation["findings_sha256"],
        "arm_quiet_mode": arm_record,
        "override": override,
        "enforced": True,
        "admitted": bool(evaluation.get("eligible") is True or override is not None),
    }


def utc_timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def best_effort_run_id(config_path: Path) -> str | None:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    run_id = data.get("run_id")
    return run_id if isinstance(run_id, str) else None


def generator_sidecar_ref_from_config(data: dict[str, Any]) -> str | None:
    candidate_keys = (
        "generator_sidecar_ref",
        "suite_annotations_ref",
        "suite_sidecar_ref",
        "suite_generator_sidecar_ref",
    )
    for key in candidate_keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    workload_profile = data.get("workload_profile")
    if isinstance(workload_profile, dict):
        for key in candidate_keys:
            value = workload_profile.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def suite_manifest_ref_from_config(data: dict[str, Any]) -> str | None:
    workload_profile = data.get("workload_profile")
    if not isinstance(workload_profile, dict):
        return None
    value = workload_profile.get("suite_manifest_ref")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def prompt_token_evidence_policy_from_config(
    data: dict[str, Any],
) -> PromptTokenEvidencePolicy | None:
    workload_profile = data.get("workload_profile")
    if not isinstance(workload_profile, dict):
        return None
    value = workload_profile.get("prompt_token_evidence_policy")
    if value is None:
        return None
    try:
        return PromptTokenEvidencePolicy(value)
    except ValueError as exc:
        allowed = ", ".join(policy.value for policy in PromptTokenEvidencePolicy)
        raise ValueError(
            "workload_profile.prompt_token_evidence_policy must be one of: "
            f"{allowed}"
        ) from exc


def load_config_info(config_path: Path) -> ConfigInfo:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"failed to read config {config_path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"config is not valid JSON: {config_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"config must be a JSON object: {config_path}")
    run_id = data.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError(f"config missing non-empty run_id: {config_path}")
    sanitized_run_id = sanitize_id_component(run_id)
    if sanitized_run_id != run_id:
        print(
            f"note: sanitized run_id for {config_path}: {run_id!r} -> {sanitized_run_id!r}",
            file=sys.stderr,
        )
    workload_profile = data.get("workload_profile", {})
    if workload_profile is None:
        workload_profile = {}
    if not isinstance(workload_profile, dict):
        raise ValueError(f"workload_profile must be an object: {config_path}")
    repetitions = workload_profile.get("repetitions", 1)
    if isinstance(repetitions, bool) or not isinstance(repetitions, int) or repetitions < 1:
        raise ValueError(f"workload_profile.repetitions must be a positive integer: {config_path}")
    return ConfigInfo(
        path=config_path,
        run_id=sanitized_run_id,
        raw_run_id=run_id,
        repetitions=repetitions,
        generator_sidecar_ref=generator_sidecar_ref_from_config(data),
        suite_manifest_ref=suite_manifest_ref_from_config(data),
        prompt_token_evidence_policy=prompt_token_evidence_policy_from_config(data),
    )


def _normalized_benchmark_config(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    try:
        from joulewise.schemas import BenchmarkConfig

        return BenchmarkConfig.from_mapping(value).to_dict()
    except Exception:  # noqa: BLE001 - malformed identities fail closed at callers.
        return None


def _bundle_config_binding_problem(
    bundle_dir: Path,
    info: ConfigInfo,
) -> str | None:
    try:
        expected_raw = json.loads(info.path.read_text(encoding="utf-8"))
        observed_raw = json.loads(
            (bundle_dir / "config.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return f"bundle/config manifest identity cannot be read: {exc}"
    expected = _normalized_benchmark_config(expected_raw)
    observed = _normalized_benchmark_config(observed_raw)
    if expected is None or observed is None:
        return "bundle/config manifest identity is not a valid normalized config"
    observed_run_id = observed.get("run_id")
    if (
        not isinstance(observed_run_id, str)
        or sanitize_id_component(observed_run_id) != bundle_dir.name
    ):
        return "bundle config run_id does not match its bundle directory"
    if info.repetitions == 1 and observed_run_id != expected.get("run_id"):
        return "bundle config run_id does not match its frozen config identity"
    expected.pop("run_id", None)
    observed.pop("run_id", None)
    if observed != expected:
        return "bundle config does not match its registered campaign config"
    return None


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_analysis_manifest(config_dir: Path) -> AnalysisManifestState | None:
    """Load P2-042's sidecar and run its authoritative strict validator."""
    path = config_dir / ANALYSIS_MANIFEST_NAME
    if not path.is_file():
        return None
    problems: list[str] = []
    try:
        file_bytes = path.read_bytes()
    except OSError as exc:
        file_bytes = b""
        raw: dict[str, Any] = {}
        problems.append(f"analysis manifest cannot be read: {exc}")
    else:
        try:
            parsed = json.loads(file_bytes)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raw = {}
            problems.append(f"analysis manifest is not valid JSON: {exc}")
        else:
            if not isinstance(parsed, dict):
                raw = {}
                problems.append("analysis manifest is not a JSON object")
            else:
                raw = parsed

    manifest_id = raw.get("manifest_id") if isinstance(raw.get("manifest_id"), str) else None
    if raw.get("schema_version") == AXI_MANIFEST_SCHEMA_VERSION:
        reference = raw.get("registry")
        reference_path = reference.get("path") if isinstance(reference, dict) else None
        if not isinstance(reference_path, str):
            problems.append("AXI analysis manifest registry path is unavailable")
        else:
            registry_path = _resolve_analysis_reference(config_dir, reference_path)
            try:
                load_and_validate_analysis_manifest_v2(path, registry_path)
            except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
                problems.append(f"AXI analysis manifest validation failed: {exc}")
    else:
        problems.extend(validate_analysis_manifest(raw, manifest_dir=config_dir))

    return AnalysisManifestState(
        path=path,
        raw=raw,
        manifest_id=manifest_id,
        file_sha256=_sha256_bytes(file_bytes),
        problems=tuple(problems),
    )


def _resolve_analysis_reference(manifest_dir: Path, reference: str) -> Path:
    """Resolve the v2 contract's normalized repository-relative references."""

    path = Path(reference)
    if path.is_file():
        return path
    return manifest_dir / path


def command_for(
    config_path: Path,
    runs_dir: Path,
    cli_cmd: str | None,
    *,
    frozen_cooldown_anchor: dict[str, Any] | None = None,
) -> list[str]:
    prefix = shlex.split(cli_cmd) if cli_cmd else [sys.executable, "-m", "joulewise"]
    command = prefix + ["run", str(config_path), "--runs-dir", str(runs_dir)]
    if frozen_cooldown_anchor is not None:
        command.extend(
            [
                "--frozen-cooldown-anchor-json",
                json.dumps(
                    frozen_cooldown_anchor,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            ]
        )
    return command


def shell_quote(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def append_log(log_path: Path, row: dict[str, Any]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists() and log_path.stat().st_size > 0:
        with log_path.open("rb+") as handle:
            handle.seek(-1, os.SEEK_END)
            if handle.read(1) != b"\n":
                handle.write(b"\n")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def log_row(
    *,
    config_path: Path,
    run_id: str | None,
    status: str,
    exit_code: int | None,
    duration_s: float | None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = {
        "timestamp": utc_timestamp(),
        "config": str(config_path),
        "run_id": run_id,
        "status": status,
        "exit_code": exit_code,
        "duration_s": duration_s,
    }
    if extra:
        row.update(extra)
    return row


def print_quiet_machine_warning() -> None:
    print("WARNING: This campaign needs a quiet machine with no other workloads.")
    print("WARNING: Benchmarks are run strictly sequentially; energy measurements must not overlap.")


def discover_configs(config_dir: Path) -> list[Path]:
    if not config_dir.is_dir():
        raise ValueError(f"config_dir is not a directory: {config_dir}")
    return sorted(
        path
        for path in config_dir.glob("*.json")
        if path.name not in NON_CONFIG_SIDECARS
    )


def print_config_file_list(configs: list[Path]) -> None:
    print("Config files to execute:")
    if not configs:
        print("  <none>")
        return
    for config in configs:
        print(f"  {config}")


def backup_script_path(backup_arg: str) -> Path:
    if backup_arg:
        return Path(backup_arg)
    return Path(__file__).resolve().parent / "backup_runs.sh"


def backup_runs(runs_dir: Path, script: Path) -> int:
    result = subprocess.run([str(script), str(runs_dir)], check=False)
    if result.returncode != 0:
        print(
            f"warning: backup command failed with exit {result.returncode}: {script} {runs_dir}",
            file=sys.stderr,
        )
    return result.returncode


class ShakedownGateError(ValueError):
    def __init__(self, code: str, bundle_id: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.bundle_id = bundle_id
        self.detail = detail


def _shakedown_fail(code: str, bundle: Path, detail: str) -> ShakedownGateError:
    return ShakedownGateError(code, bundle.name, detail)


def assert_production_uncertainty(
    bundle_path: Path, *, allow_mock_runtime: bool = False
) -> dict[str, Any]:
    """Assert the P2-038 evidence and P2-029/P2-040 request gates."""

    bundle = Path(bundle_path)
    reader = BundleReader(bundle)
    try:
        config = reader.config()
        metadata = reader.metadata()
        summary = reader.raw_summary()
    except BundleReadError as exc:
        raise _shakedown_fail("strict_pre_reduce_failed", bundle, str(exc)) from exc
    target = config.hardware_target
    if target.telemetry_backend != TelemetryBackend.POWERMETRICS:
        raise _shakedown_fail(
            "not_production_backend", bundle, "telemetry backend is not powermetrics"
        )
    if target.runtime_backend == RuntimeBackend.MOCK and not allow_mock_runtime:
        raise _shakedown_fail(
            "not_production_backend", bundle, "runtime backend is mock"
        )
    if not isinstance(summary, dict) or summary.get("status") != RunStatus.SUCCEEDED.value:
        raise _shakedown_fail(
            "request_ineligible",
            bundle,
            f"bundle status is {summary.get('status') if isinstance(summary, dict) else None}",
        )
    for name in (
        "powermetrics_idle.plist",
        "powermetrics.plist",
        "powermetrics_idle_post.plist",
    ):
        if not (bundle / "raw" / name).is_file():
            raise _shakedown_fail(
                "drift_evidence_missing" if "idle" in name else "clock_evidence_missing",
                bundle,
                f"missing raw/{name}",
            )
    evidence = metadata.get("uncertainty_evidence")
    if not isinstance(evidence, dict) or evidence.get("schema_version") != "p2-038.1":
        raise _shakedown_fail(
            "clock_evidence_missing", bundle, "missing p2-038.1 uncertainty evidence"
        )
    clock = evidence.get("clock_anchor")
    phase = evidence.get("sample_phase")
    idle = evidence.get("idle_drift")
    if not isinstance(clock, dict) or clock.get("status") != "bounded":
        raise _shakedown_fail("clock_evidence_invalid", bundle, "clock evidence is not bounded")
    if clock.get("method") != "powermetrics_spawn_ready_wall_monotonic_envelope_v1":
        raise _shakedown_fail("clock_evidence_invalid", bundle, "unexpected clock method")
    if not isinstance(phase, dict) or phase.get("status") != "bounded":
        raise _shakedown_fail("phase_evidence_missing", bundle, "phase evidence is not bounded")
    if not isinstance(idle, dict) or idle.get("status") != "bounded":
        raise _shakedown_fail("drift_evidence_missing", bundle, "idle drift is not bounded")
    if idle.get("method") != "pre_post_idle_observed_envelope_v1":
        raise _shakedown_fail("drift_evidence_missing", bundle, "unexpected drift method")
    for key in (
        "clock_anchor_bound_s",
        "marker_to_first_sample_phase_bound_s",
        "marker_to_last_sample_phase_bound_s",
        "idle_drift_bound_w",
    ):
        value = metadata.get(key)
        if (
            isinstance(value, bool)
            or not isinstance(value, int | float)
            or not math.isfinite(float(value))
            or float(value) < 0.0
        ):
            raise _shakedown_fail(
                "phase_evidence_missing" if key.startswith("marker") else "clock_evidence_invalid",
                bundle,
                f"metadata.{key} is missing or invalid",
            )
    extra = metadata.get("extra")
    if isinstance(extra, dict) and any(
        key in extra for key in ("clock_anchor_bound_s", "idle_drift_bound_w")
    ):
        raise _shakedown_fail(
            "synthetic_metadata_present", bundle, "caller-supplied uncertainty bound present"
        )
    raw_summary = reader.raw_summary()
    request = (
        raw_summary.get("window_evidence_precheck", {}).get(
            "idle_subtracted_request"
        )
        if isinstance(raw_summary, dict)
        else None
    )
    if not isinstance(request, dict) or request.get("eligible") is not True or request.get("reasons") != []:
        raise _shakedown_fail(
            "request_ineligible", bundle, f"request gate is {request!r}"
        )
    drift_j = (
        raw_summary.get("energy_bound_terms_j", {}).get("E_drift_bound_j")
        if isinstance(raw_summary, dict)
        else None
    )
    if not isinstance(drift_j, int | float) or not math.isfinite(float(drift_j)):
        raise _shakedown_fail(
            "drift_evidence_missing", bundle, "E_drift_bound_j is missing"
        )
    return {
        "bundle_id": bundle.name,
        "clock_method": clock["method"],
        "idle_method": idle["method"],
        "request_eligible": True,
        "request_reasons": [],
    }


def execute_production_uncertainty_gate(
    bundle: Path, runs_dir: Path, backup_arg: str
) -> dict[str, Any]:
    """Run the strict -> reduce -> strict -> assertion -> backup sequence."""

    pre_problems = validate_bundle(bundle, strict=True)
    if pre_problems:
        raise _shakedown_fail(
            "strict_pre_reduce_failed", bundle, "; ".join(pre_problems)
        )
    reduce_result = subprocess.run(
        [sys.executable, "-m", "joulewise", "reduce", str(bundle)],
        check=False,
    )
    if reduce_result.returncode != 0:
        raise _shakedown_fail(
            "reduce_failed", bundle, f"reduce exit {reduce_result.returncode}"
        )
    post_problems = validate_bundle(bundle, strict=True)
    if post_problems:
        raise _shakedown_fail(
            "strict_post_reduce_failed", bundle, "; ".join(post_problems)
        )
    assertion = assert_production_uncertainty(bundle)
    backup_script = backup_script_path(backup_arg)
    try:
        backup_exit = backup_runs(runs_dir, backup_script)
    except OSError as exc:
        raise _shakedown_fail(
            "backup_failed",
            bundle,
            f"backup launch failed: {type(exc).__name__}: {exc}",
        ) from exc
    if backup_exit != 0:
        raise _shakedown_fail("backup_failed", bundle, f"backup exit {backup_exit}")
    return {
        "timestamp": utc_timestamp(),
        "record_type": "shakedown_gate",
        "gate": "production_uncertainty_v1",
        "status": "passed",
        "strict_pre_reduce": "passed",
        "reduce_exit": reduce_result.returncode,
        "strict_post_reduce": "passed",
        "backup_command": str(backup_script),
        "backup_exit": backup_exit,
        **assertion,
    }


def failed_shakedown_record(
    gate: str, error: ShakedownGateError
) -> dict[str, Any]:
    return {
        "timestamp": utc_timestamp(),
        "record_type": "shakedown_gate",
        "gate": gate,
        "status": "failed",
        "bundle_id": error.bundle_id,
        "code": error.code,
        "detail": error.detail,
    }


def member_bundle_dirs(runs_dir: Path, run_id: str, repetitions: int) -> list[Path]:
    return [runs_dir / f"{run_id}__r{rep}" for rep in range(1, repetitions + 1)]


def expected_member_dirs(info: ConfigInfo, runs_dir: Path) -> list[Path]:
    if info.repetitions == 1:
        return [runs_dir / info.run_id]
    return member_bundle_dirs(runs_dir, info.run_id, info.repetitions)


WaiverMap = dict[tuple[str, str], Waiver]


def load_waivers(path_text: str | None) -> WaiverMap:
    if path_text is None:
        return {}
    path = Path(path_text)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"failed to read waiver file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"waiver file is not valid JSON: {path}: {exc}") from exc
    if not isinstance(raw, list):
        raise ValueError(f"waiver file must be a JSON list: {path}")
    waivers: WaiverMap = {}
    seen_targets: set[tuple[str, str]] = set()
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"waiver {index} must be an object")
        target_fields = [field for field in ("bundle_id", "config", "run_id") if field in item]
        if len(target_fields) != 1:
            raise ValueError(
                f"waiver {index} requires exactly one of bundle_id, config, or run_id"
            )
        target_kind = target_fields[0]
        raw_target = item[target_kind]
        if not isinstance(raw_target, str) or not raw_target.strip():
            raise ValueError(f"waiver {index} requires non-empty {target_kind}")
        target = raw_target.strip()
        for key in ("reason", "approver", "timestamp", "scope"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f"waiver {index} requires non-empty {key}")
        scope_value = item["scope"].strip()
        scope_tokens = (
            {"any"}
            if scope_value == "any"
            else {part.strip() for part in scope_value.split(",") if part.strip()}
        )
        unknown_scopes = scope_tokens - VALID_WAIVER_SCOPES
        if unknown_scopes:
            raise ValueError(
                f"waiver {index} has unknown scope class(es) "
                f"{sorted(unknown_scopes)}; valid: {sorted(VALID_WAIVER_SCOPES)}"
            )
        duplicate_key = (
            target_kind,
            Path(target).stem if target_kind == "config" else target,
        )
        if duplicate_key in seen_targets:
            raise ValueError(f"duplicate waiver target: {target_kind}={target}")
        seen_targets.add(duplicate_key)
        key = (target_kind, target)
        waivers[key] = Waiver(
            target_kind=target_kind,
            target=target,
            reason=item["reason"],
            approver=item["approver"],
            timestamp=item["timestamp"],
            scope=item["scope"].strip(),
        )
    return waivers


def matching_waiver(
    waivers: WaiverMap,
    *,
    bundle_id: str,
    config_name: str,
    config_stem: str,
    run_id: str,
) -> Waiver | None:
    candidates = (
        ("bundle_id", bundle_id),
        ("config", config_name),
        ("config", config_stem),
        ("run_id", run_id),
    )
    for target_kind, target in candidates:
        waiver = waivers.get((target_kind, target))
        if waiver is not None:
            return waiver
    return None


def resolve_sidecar_path(config_path: Path, sidecar_ref: str | None) -> Path | None:
    if sidecar_ref is None:
        return None
    path = Path(sidecar_ref)
    if path.is_absolute():
        return path
    root_relative = ROOT / path
    if root_relative.is_file():
        return root_relative
    config_relative = config_path.parent / path
    if config_relative.is_file():
        return config_relative
    return root_relative


def resolve_config_ref_path(config_path: Path, ref: str | None) -> Path | None:
    if ref is None:
        return None
    path = Path(ref)
    if path.is_absolute():
        return path
    root_relative = ROOT / path
    if root_relative.is_file():
        return root_relative
    config_relative = config_path.parent / path
    if config_relative.is_file():
        return config_relative
    return root_relative


def inferred_prompt_sidecar_path(config_path: Path, suite_manifest_ref: str | None) -> Path | None:
    manifest_path = resolve_config_ref_path(config_path, suite_manifest_ref)
    if manifest_path is None:
        return None
    candidate = manifest_path.with_name(f"{manifest_path.stem}_annotations.json")
    if candidate.is_file():
        return candidate
    return None


def _sidecar_schema_string(sidecar: dict[str, Any]) -> str | None:
    for key in ("schema", "schema_version"):
        value = sidecar.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _is_recognizable_other_sidecar(sidecar: dict[str, Any]) -> bool:
    if "annotations" in sidecar:
        return True
    schema = _sidecar_schema_string(sidecar)
    return schema in KNOWN_NON_PROMPT_SIDECAR_SCHEMAS


def _classify_inferred_prompt_sidecar(sidecar_path: Path) -> PromptHashCheck | None:
    sidecar_label = str(sidecar_path)
    sidecar, sidecar_problem = _load_json_object(sidecar_path, "inferred generator sidecar")
    if sidecar_problem is not None:
        return PromptHashCheck("error", sidecar_label, problems=(sidecar_problem,))
    assert sidecar is not None
    if isinstance(sidecar.get("items"), dict):
        return None
    if "items" in sidecar:
        return PromptHashCheck(
            "error",
            sidecar_label,
            problems=("inferred generator sidecar items is not an object",),
        )
    if _is_recognizable_other_sidecar(sidecar):
        return PromptHashCheck("not_applicable", sidecar_label)
    return PromptHashCheck(
        "error",
        sidecar_label,
        problems=(
            "inferred generator sidecar is ambiguous: "
            "missing prompt-hash items and no recognized other-type marker",
        ),
    )


def _check_prompt_token_evidence_policy(
    bundle_dir: Path,
    info: ConfigInfo,
    *,
    neighboring_sidecar: Path | None = None,
) -> PromptHashCheck:
    sidecar_label = str(neighboring_sidecar) if neighboring_sidecar is not None else None
    _, text_items, manifest_problems = _manifest_text_items(bundle_dir)
    if text_items is None or manifest_problems:
        return PromptHashCheck(
            "error",
            sidecar_label,
            problems=tuple(manifest_problems),
        )
    if not text_items:
        return PromptHashCheck("not_applicable", sidecar_label)
    if (
        info.prompt_token_evidence_policy
        == PromptTokenEvidencePolicy.EXEMPT_AFFINE_GENERATED_TEXT
    ):
        return PromptHashCheck("policy_exempt", sidecar_label)
    return PromptHashCheck(
        "missing_evidence",
        sidecar_label,
        problems=(
            "text-tokenized suite is missing prompt-token evidence: provide an "
            "explicit prompt-token sidecar or set the validated "
            "exempt_affine_generated_text policy",
        ),
    )


def _load_json_object(path: Path, label: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, f"{label} cannot be read: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"{label} is not valid JSON: {exc}"
    if not isinstance(raw, dict):
        return None, f"{label} is not a JSON object"
    return raw, None


def _load_suite_item_records_for_prompt_check(
    bundle_dir: Path,
) -> tuple[list[dict[str, Any]] | None, list[str]]:
    path = bundle_dir / "outputs" / "suite_items.jsonl"
    if not path.is_file():
        return None, ["outputs/suite_items.jsonl is missing for prompt-hash check"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, [f"outputs/suite_items.jsonl cannot be read: {exc}"]
    records: list[dict[str, Any]] = []
    problems: list[str] = []
    for line_index, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            problems.append(
                f"outputs/suite_items.jsonl line {line_index} is not valid JSON: {exc}"
            )
            continue
        if not isinstance(record, dict):
            problems.append(
                f"outputs/suite_items.jsonl line {line_index} is not a JSON object"
            )
            continue
        records.append(record)
    return records, problems


def _manifest_text_items(
    bundle_dir: Path,
) -> tuple[dict[str, Any] | None, list[tuple[int, str]] | None, list[str]]:
    manifest, problem = _load_json_object(bundle_dir / "suite_manifest.json", "suite_manifest.json")
    if problem is not None:
        return None, None, [problem]
    assert manifest is not None
    raw_items = manifest.get("items")
    if not isinstance(raw_items, list):
        return manifest, None, ["suite_manifest.json items is not a list"]
    text_items: list[tuple[int, str]] = []
    problems: list[str] = []
    for item_index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, dict):
            problems.append(f"suite_manifest.json items[{item_index}] is not an object")
            continue
        item_id = raw_item.get("item_id")
        if not isinstance(item_id, str) or not item_id:
            problems.append(f"suite_manifest.json items[{item_index}].item_id is missing")
            continue
        source = raw_item.get("source")
        if not isinstance(source, dict):
            problems.append(f"suite_manifest.json items[{item_index}].source is not an object")
            continue
        # Match SuiteItem.prompt_source_kind() and the runtime adapters: an
        # explicit prompt_text is text-tokenized regardless of item_type.
        if source.get("prompt_text") is None:
            continue
        text_items.append((item_index, item_id))
    return manifest, text_items, problems


def _sidecar_manifest_pairing_problems(
    sidecar: dict[str, Any],
    manifest: dict[str, Any],
) -> list[str]:
    sidecar_source = sidecar.get("source_manifest")
    if sidecar_source is None:
        return ["generator sidecar source_manifest is missing"]
    if not isinstance(sidecar_source, dict):
        return ["generator sidecar source_manifest is not an object"]
    manifest_source = manifest.get("source_manifest")
    if not isinstance(manifest_source, dict):
        return ["suite_manifest.json source_manifest is not an object"]
    problems: list[str] = []
    for key in ("source_id", "subset_sha256"):
        sidecar_value = sidecar_source.get(key)
        manifest_value = manifest_source.get(key)
        if not isinstance(sidecar_value, str) or not sidecar_value:
            problems.append(f"generator sidecar source_manifest.{key} is missing")
        elif sidecar_value != manifest_value:
            problems.append(
                f"generator sidecar source_manifest.{key} mismatch: "
                f"sidecar has {sidecar_value!r}, suite_manifest.json has {manifest_value!r}"
            )
    return problems


def check_prompt_hashes_for_bundle(bundle_dir: Path, sidecar_path: Path | None) -> PromptHashCheck:
    if sidecar_path is None:
        return PromptHashCheck("not_applicable")
    sidecar_label = str(sidecar_path)
    sidecar, sidecar_problem = _load_json_object(sidecar_path, "generator sidecar")
    if sidecar_problem is not None:
        return PromptHashCheck("error", sidecar_label, problems=(sidecar_problem,))
    assert sidecar is not None
    expected_items = sidecar.get("items")
    if not isinstance(expected_items, dict):
        return PromptHashCheck(
            "error",
            sidecar_label,
            problems=("generator sidecar items is not an object",),
        )

    records, record_problems = _load_suite_item_records_for_prompt_check(bundle_dir)
    manifest, text_items, manifest_problems = _manifest_text_items(bundle_dir)
    problems = [*record_problems, *manifest_problems]
    if records is None or text_items is None:
        return PromptHashCheck("error", sidecar_label, problems=tuple(problems))
    assert manifest is not None
    problems.extend(_sidecar_manifest_pairing_problems(sidecar, manifest))

    records_by_index: dict[int, dict[str, Any]] = {}
    for line_index, record in enumerate(records, start=1):
        item_index = record.get("item_index")
        if isinstance(item_index, bool) or not isinstance(item_index, int):
            problems.append(
                f"outputs/suite_items.jsonl line {line_index} item_index is not an integer"
            )
            continue
        if item_index in records_by_index:
            problems.append(f"outputs/suite_items.jsonl duplicates item_index {item_index}")
            continue
        records_by_index[item_index] = record

    matches: list[dict[str, Any]] = []
    mismatches: list[str] = []
    for item_index, item_id in text_items:
        expected_row = expected_items.get(item_id)
        if not isinstance(expected_row, dict):
            problems.append(
                f"item {item_id!r} index {item_index} is missing from generator sidecar"
            )
            continue
        expected_hash = expected_row.get("token_ids_sha256")
        if not isinstance(expected_hash, str) or not expected_hash:
            problems.append(
                f"item {item_id!r} index {item_index} sidecar token_ids_sha256 is missing"
            )
            continue
        record = records_by_index.get(item_index)
        if record is None:
            problems.append(
                f"item {item_id!r} index {item_index} is missing from outputs/suite_items.jsonl"
            )
            continue
        realized_item_id = record.get("item_id")
        if realized_item_id != item_id:
            problems.append(
                f"item index {item_index} item_id mismatch: manifest has {item_id!r}, "
                f"outputs/suite_items.jsonl has {realized_item_id!r}"
            )
            continue
        prompt = record.get("prompt")
        realized_hash = prompt.get("token_ids_sha256") if isinstance(prompt, dict) else None
        if realized_hash != expected_hash:
            mismatches.append(
                f"item {item_id!r} index {item_index} prompt.token_ids_sha256 mismatch: "
                f"expected {expected_hash!r}, realized {realized_hash!r}"
            )
            continue
        matches.append(
            {
                "item_id": item_id,
                "item_index": item_index,
                "expected": expected_hash,
                "realized": realized_hash,
            }
        )

    if problems:
        return PromptHashCheck(
            "error",
            sidecar_label,
            checked_items=len(matches) + len(mismatches),
            matches=tuple(matches),
            problems=tuple([*problems, *mismatches]),
        )
    if mismatches:
        return PromptHashCheck(
            "mismatch",
            sidecar_label,
            checked_items=len(matches) + len(mismatches),
            matches=tuple(matches),
            problems=tuple(mismatches),
        )
    return PromptHashCheck(
        "matched",
        sidecar_label,
        checked_items=len(matches),
        matches=tuple(matches),
    )


def check_prompt_hashes_for_config_bundle(bundle_dir: Path, info: ConfigInfo) -> PromptHashCheck:
    explicit = resolve_sidecar_path(info.path, info.generator_sidecar_ref)
    if explicit is not None:
        return check_prompt_hashes_for_bundle(bundle_dir, explicit)
    if info.suite_manifest_ref is None:
        return PromptHashCheck("not_applicable")
    inferred = inferred_prompt_sidecar_path(info.path, info.suite_manifest_ref)
    if inferred is None:
        return _check_prompt_token_evidence_policy(bundle_dir, info)
    inferred_classification = _classify_inferred_prompt_sidecar(inferred)
    if inferred_classification is not None:
        if inferred_classification.status == "not_applicable":
            return _check_prompt_token_evidence_policy(
                bundle_dir,
                info,
                neighboring_sidecar=inferred,
            )
        return inferred_classification
    return check_prompt_hashes_for_bundle(bundle_dir, inferred)


def _stable_precheck_reasons(value: Any) -> set[str]:
    reasons: set[str] = set()
    if isinstance(value, dict):
        raw_reasons = value.get("reasons")
        if isinstance(raw_reasons, list):
            reasons.update(reason for reason in raw_reasons if isinstance(reason, str))
        for child in value.values():
            reasons.update(_stable_precheck_reasons(child))
    elif isinstance(value, list):
        for child in value:
            reasons.update(_stable_precheck_reasons(child))
    return reasons


def claim_evidence_flags(summary: dict[str, Any] | None) -> tuple[str, ...]:
    if not isinstance(summary, dict):
        return ()
    flags = _stable_precheck_reasons(
        summary.get("window_evidence_precheck", summary.get("claim_eligibility"))
    )
    quality = summary.get("measurement_quality")
    if isinstance(quality, dict):
        if quality.get("idle_window_suspect") is True:
            flags.add("idle_window_suspect")
        if quality.get("cooldown_cap_hit") is True:
            flags.add("cooldown_cap_hit")
    flags.update(cleanup_claim_evidence_flags(summary))
    return tuple(sorted(flags))


def suite_order_evidence(bundle_dir: Path) -> tuple[str | None, int | None, str | None]:
    policy: str | None = None
    row: int | None = None
    seed: str | None = None
    manifest, _ = _load_json_object(bundle_dir / "suite_manifest.json", "suite_manifest.json")
    if manifest is not None:
        execution_policy = manifest.get("execution_policy")
        if isinstance(execution_policy, dict) and isinstance(
            execution_policy.get("order_policy"), str
        ):
            policy = execution_policy["order_policy"]
    metadata, _ = _load_json_object(bundle_dir / "metadata.json", "metadata.json")
    if metadata is not None:
        suite = metadata.get("suite")
        if isinstance(suite, dict):
            if policy is None and isinstance(suite.get("order_policy"), str):
                policy = suite["order_policy"]
            if isinstance(suite.get("order_row"), int) and not isinstance(
                suite.get("order_row"), bool
            ):
                row = suite["order_row"]
            if isinstance(suite.get("order_seed"), str):
                seed = suite["order_seed"]
    return policy, row, seed


def evaluate_member(
    bundle_dir: Path,
    *,
    info: ConfigInfo,
    waivers: WaiverMap,
    cooldown_evidence: dict[str, Any] | None = None,
) -> MemberEvaluation:
    status, malformed = summary_status(bundle_dir / "summary_metrics.json")
    problems: list[str] = []
    strict_valid = False
    if bundle_dir.exists():
        try:
            problems = validate_bundle(bundle_dir, strict=True)
        except Exception as exc:
            problems = [f"strict validation raised {type(exc).__name__}: {exc}"]
        strict_valid = not problems
    else:
        problems = ["bundle directory is missing"]
    if malformed is not None:
        problems = [malformed, *problems]
    summary: dict[str, Any] | None = None
    if (bundle_dir / "summary_metrics.json").is_file():
        try:
            parsed = json.loads((bundle_dir / "summary_metrics.json").read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                summary = parsed
        except (OSError, json.JSONDecodeError):
            summary = None
    metadata: dict[str, Any] | None = None
    if (bundle_dir / "metadata.json").is_file():
        try:
            parsed_metadata = json.loads(
                (bundle_dir / "metadata.json").read_text(encoding="utf-8")
            )
            if isinstance(parsed_metadata, dict):
                metadata = parsed_metadata
        except (OSError, json.JSONDecodeError):
            metadata = None
    prompt_hash_check = check_prompt_hashes_for_config_bundle(bundle_dir, info)
    binding_problem = (
        _bundle_config_binding_problem(bundle_dir, info)
        if bundle_dir.exists()
        else None
    )
    collection_flags = set(prompt_hash_check.collection_integrity_flags())
    if binding_problem is not None:
        problems.append(binding_problem)
        collection_flags.add("config_manifest_mismatch")
    suite_order_policy, suite_order_row, suite_order_seed = suite_order_evidence(bundle_dir)
    waiver = matching_waiver(
        waivers,
        bundle_id=bundle_dir.name,
        config_name=info.path.name,
        config_stem=info.path.stem,
        run_id=info.run_id,
    )
    quality = summary.get("measurement_quality") if isinstance(summary, dict) else None
    runtime_cleanup_ok = (
        quality.get("runtime_cleanup_ok")
        if isinstance(quality, dict)
        and isinstance(quality.get("runtime_cleanup_ok"), bool)
        else None
    )
    remote_cleanup = (
        quality.get("remote_cleanup_failed") if isinstance(quality, dict) else None
    )
    remote_cleanup_failed = (
        tuple(path for path in remote_cleanup if isinstance(path, str))
        if isinstance(remote_cleanup, list)
        else ()
    )
    return MemberEvaluation(
        bundle_id=bundle_dir.name,
        bundle_path=bundle_dir,
        config_name=info.path.name,
        status=status,
        strict_valid=strict_valid,
        validation_problems=tuple(problems),
        collection_integrity_flags=tuple(sorted(collection_flags)),
        claim_evidence_flags=claim_evidence_flags(summary),
        runtime_cleanup_ok=runtime_cleanup_ok,
        remote_cleanup_failed=remote_cleanup_failed,
        ratio_token_provenance=token_provenance_from_artifacts(summary, metadata),
        prompt_hash_check=prompt_hash_check,
        suite_order_policy=suite_order_policy,
        suite_order_row=suite_order_row,
        suite_order_seed=suite_order_seed,
        waiver=waiver,
        summary=summary,
        metadata=metadata,
        preceding_campaign_cooldown=cooldown_evidence,
    )


def evaluate_members(
    info: ConfigInfo,
    runs_dir: Path,
    waivers: WaiverMap,
    cooldown_by_bundle: dict[str, dict[str, Any]] | None = None,
) -> list[MemberEvaluation]:
    cooldown_by_bundle = cooldown_by_bundle or {}
    return [
        evaluate_member(
            bundle_dir,
            info=info,
            waivers=waivers,
            cooldown_evidence=cooldown_by_bundle.get(bundle_dir.name),
        )
        for bundle_dir in expected_member_dirs(info, runs_dir)
    ]


def summary_status(summary_path: Path) -> tuple[str | None, str | None]:
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, f"{summary_path}: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"{summary_path}: malformed JSON ({exc.msg})"
    if not isinstance(summary, dict):
        return None, f"{summary_path}: summary_metrics.json is not a JSON object"
    status = summary.get("status")
    if not isinstance(status, str):
        return None, f"{summary_path}: summary_metrics.json lacks string status"
    return status, None


def existing_state(info: ConfigInfo, runs_dir: Path) -> ExistingState:
    if info.repetitions == 1:
        bundle_dir = runs_dir / info.run_id
        summary_path = bundle_dir / "summary_metrics.json"
        if summary_path.is_file():
            status, malformed = summary_status(summary_path)
            if malformed is not None:
                return ExistingState(
                    action="incomplete existing",
                    inspect_members=(bundle_dir.name,),
                    malformed_summaries=(malformed,),
                )
            return ExistingState(action="skip complete")
        if bundle_dir.exists():
            return ExistingState(action="incomplete existing", inspect_members=(bundle_dir.name,))
        return ExistingState(action="would run")

    members = member_bundle_dirs(runs_dir, info.run_id, info.repetitions)
    summary_paths = [member / "summary_metrics.json" for member in members]
    malformed_summaries: list[str] = []
    statuses: list[str | None] = []
    for summary_path in summary_paths:
        if summary_path.is_file():
            status, malformed = summary_status(summary_path)
            statuses.append(status)
            if malformed is not None:
                malformed_summaries.append(malformed)
        else:
            statuses.append(None)
    if malformed_summaries:
        inspect = tuple(member.name for member in members if member.exists())
        return ExistingState(
            action="incomplete existing",
            inspect_members=inspect,
            malformed_summaries=tuple(malformed_summaries),
        )
    if all(summary_path.is_file() for summary_path in summary_paths):
        non_succeeded = tuple(
            member.name
            for member, status in zip(members, statuses, strict=True)
            if status != "succeeded"
        )
        return ExistingState(
            action="skip complete",
            members_succeeded=sum(status == "succeeded" for status in statuses),
            members_total=len(members),
            non_succeeded_members=non_succeeded,
        )
    if any(member.exists() for member in members):
        inspect = tuple(member.name for member in members if member.exists())
        return ExistingState(action="incomplete existing", inspect_members=inspect)
    return ExistingState(action="would run")


def read_config_infos(config_paths: list[Path]) -> list[ConfigInfo | ConfigError]:
    items: list[ConfigInfo | ConfigError] = []
    for config_path in config_paths:
        try:
            items.append(load_config_info(config_path))
        except Exception as exc:
            items.append(
                ConfigError(
                    path=config_path,
                    message=str(exc),
                    run_id=best_effort_run_id(config_path),
                )
            )
    return items


def load_order_entries(config_dir: Path) -> tuple[list[OrderEntry], str | None]:
    path = config_dir / ORDER_MANIFEST_NAME
    if not path.is_file():
        return [], (
            f"WARNING: no {ORDER_MANIFEST_NAME} found; falling back to sorted "
            "config order. D-014 forbids silent sorted model blocks."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"failed to read order manifest {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"order manifest is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"order manifest must be a JSON object: {path}")
    raw_order = data.get("executed_order")
    if not isinstance(raw_order, list):
        raise ValueError(f"order manifest missing executed_order list: {path}")
    entries: list[OrderEntry] = []
    seen_configs: set[str] = set()
    seen_indexes: set[int] = set()
    for index, raw in enumerate(raw_order, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"order manifest entry {index} is not an object")
        config = raw.get("config")
        if not isinstance(config, str) or not config:
            raise ValueError(f"order manifest entry {index} missing config")
        raw_index = raw.get("index", index)
        if isinstance(raw_index, bool) or not isinstance(raw_index, int):
            raise ValueError(f"order manifest entry {index} has invalid index")
        if config in seen_configs:
            raise ValueError(f"order manifest has duplicate config entry: {config}")
        if raw_index in seen_indexes:
            raise ValueError(f"order manifest has duplicate index: {raw_index}")
        seen_configs.add(config)
        seen_indexes.add(raw_index)
        rep = raw.get("rep")
        if rep is not None and (isinstance(rep, bool) or not isinstance(rep, int)):
            raise ValueError(f"order manifest entry {index} has invalid rep")
        block_index = raw.get("block_index")
        if block_index is not None and (
            isinstance(block_index, bool) or not isinstance(block_index, int)
        ):
            raise ValueError(f"order manifest entry {index} has invalid block_index")
        position_in_block = raw.get("position_in_block")
        if position_in_block is not None and (
            isinstance(position_in_block, bool) or not isinstance(position_in_block, int)
        ):
            raise ValueError(f"order manifest entry {index} has invalid position_in_block")
        entries.append(
            OrderEntry(
                index=raw_index,
                config=config,
                run_id=raw.get("run_id") if isinstance(raw.get("run_id"), str) else None,
                model_tag=raw.get("model_tag") if isinstance(raw.get("model_tag"), str) else None,
                rep=rep,
                workload=raw.get("workload") if isinstance(raw.get("workload"), str) else None,
                role=raw.get("role") if isinstance(raw.get("role"), str) else None,
                block_index=block_index,
                position_in_block=position_in_block,
                sentinel_position=(
                    raw.get("sentinel_position")
                    if isinstance(raw.get("sentinel_position"), str)
                    else None
                ),
            )
        )
    expected_indexes = set(range(1, len(entries) + 1))
    if seen_indexes != expected_indexes:
        raise ValueError(
            "order manifest indexes must be contiguous 1.."
            f"{len(entries)} (found {sorted(seen_indexes)})"
        )
    return entries, None


def apply_order_manifest(
    config_paths: list[Path],
    order_entries: list[OrderEntry],
) -> list[Path]:
    if not order_entries:
        return config_paths
    by_name = {path.name: path for path in config_paths}
    ordered: list[Path] = []
    missing: list[str] = []
    seen: set[str] = set()
    for entry in order_entries:
        path = by_name.get(entry.config)
        if path is None:
            missing.append(entry.config)
            continue
        ordered.append(path)
        seen.add(entry.config)
    extras = sorted(name for name in by_name if name not in seen)
    if missing or extras:
        parts: list[str] = []
        if missing:
            parts.append("manifest references missing config(s): " + ", ".join(missing))
        if extras:
            parts.append("config(s) absent from manifest: " + ", ".join(extras))
        raise ValueError("; ".join(parts))
    return ordered


def order_entry_by_config(order_entries: list[OrderEntry]) -> dict[str, OrderEntry]:
    return {entry.config: entry for entry in order_entries}


def duplicate_run_id_error(items: list[ConfigInfo | ConfigError]) -> str | None:
    by_run_id: dict[str, list[Path]] = {}
    for item in items:
        if isinstance(item, ConfigInfo):
            by_run_id.setdefault(item.run_id, []).append(item.path)
    collisions = {run_id: paths for run_id, paths in by_run_id.items() if len(paths) > 1}
    if not collisions:
        return None
    parts = [
        f"{run_id}: {', '.join(str(path) for path in paths)}"
        for run_id, paths in sorted(collisions.items())
    ]
    return "duplicate sanitized run_id(s): " + "; ".join(parts)


def acquire_campaign_lock(runs_dir: Path) -> Path:
    runs_dir.mkdir(parents=True, exist_ok=True)
    lock_path = runs_dir / "campaign.lock"
    content = f"pid={os.getpid()} created_at={utc_timestamp()}\n"
    try:
        fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        try:
            existing = lock_path.read_text(encoding="utf-8").strip()
        except OSError:
            existing = "<unreadable>"
        raise RuntimeError(
            f"another campaign appears to be running (lock {lock_path}, created {existing}); "
            "if no campaign is running, delete the lock file and retry"
        ) from exc
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(content)
    return lock_path


def new_campaign_provenance(
    config_dir: Path,
    runs_dir: Path,
    analysis_manifest: AnalysisManifestState | None,
    policy_binding: CampaignPolicyBinding | None = None,
) -> tuple[Path, dict[str, Any]]:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    session_id = f"campaign-{stamp}-p{os.getpid()}"
    path = runs_dir / "campaign_manifests" / f"{session_id}.json"
    manifest = {
        "schema_version": CAMPAIGN_PROVENANCE_SCHEMA,
        "session_id": session_id,
        "created_at": utc_timestamp(),
        "config_dir": str(config_dir),
        "analysis_manifest_id": (
            analysis_manifest.manifest_id if analysis_manifest is not None else None
        ),
        "campaign_policy": (
            policy_binding.to_metadata() if policy_binding is not None else None
        ),
        "environment_preflight": None,
        "cooldown_anchor": None,
        "first_physical_run_id": None,
        "members": [],
        "cooldown_gates": [],
    }
    write_campaign_provenance(path, manifest)
    return path, manifest


def write_campaign_provenance(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def verify_cooldown_raw_provenance(
    cooldown: dict[str, Any], manifest_dir: Path
) -> bool:
    """Re-verify a cooldown JSONL descriptor against its current raw bytes."""
    raw_artifact = cooldown.get("raw_artifact")
    if not isinstance(raw_artifact, dict):
        return False
    raw_path_text = raw_artifact.get("path")
    raw_sha = raw_artifact.get("sha256")
    raw_records = raw_artifact.get("records")
    if (
        not isinstance(raw_path_text, str)
        or not raw_path_text
        or Path(raw_path_text).is_absolute()
        or Path(raw_path_text).name == raw_path_text
        or ".." in Path(raw_path_text).parts
        or not isinstance(raw_sha, str)
        or len(raw_sha) != 64
        or any(character not in "0123456789abcdef" for character in raw_sha)
        or isinstance(raw_records, bool)
        or not isinstance(raw_records, int)
        or raw_records <= 0
    ):
        return False
    try:
        manifest_dir = manifest_dir.resolve()
        raw_path = (manifest_dir / raw_path_text).resolve()
    except (OSError, RuntimeError):
        return False
    if manifest_dir not in raw_path.parents:
        return False
    try:
        payload = raw_path.read_bytes()
    except OSError:
        return False
    if _sha256_bytes(payload) != raw_sha:
        return False
    try:
        lines = payload.decode("utf-8").splitlines()
        parsed_rows = [json.loads(line) for line in lines]
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False
    return len(parsed_rows) == raw_records


def prior_campaign_cooldown_evidence(
    runs_dir: Path, analysis_manifest_id: str | None
) -> dict[str, dict[str, Any]]:
    """Recover persistent per-member gate evidence from earlier invocations."""
    evidence: dict[str, dict[str, Any]] = {}
    manifest_dir = runs_dir / "campaign_manifests"
    if not manifest_dir.is_dir():
        return evidence
    for path in sorted(manifest_dir.glob("*.json")):
        raw, problem = _load_json_object(path, "campaign provenance")
        if problem is not None or raw is None:
            continue
        if raw.get("schema_version") != CAMPAIGN_PROVENANCE_SCHEMA:
            continue
        if (
            analysis_manifest_id is not None
            and raw.get("analysis_manifest_id") != analysis_manifest_id
        ):
            continue
        members = raw.get("members")
        if not isinstance(members, list):
            continue
        session_id = raw.get("session_id")
        first_physical_run_id = raw.get("first_physical_run_id")
        first_exemption_accepted = False
        for member in members:
            if not isinstance(member, dict):
                continue
            if member.get("execution") != "invoked":
                # Existing-member rows are bookkeeping copies, not physical
                # evidence origins. Ignoring them prevents a copied exemption
                # from shadowing its valid originating session on resume.
                continue
            physical_members = member.get("physical_members")
            if isinstance(physical_members, list):
                for physical in physical_members:
                    if not isinstance(physical, dict):
                        continue
                    bundle_id = physical.get("bundle_id")
                    cooldown = physical.get("preceding_campaign_cooldown")
                    if not isinstance(bundle_id, str) or not isinstance(cooldown, dict):
                        continue
                    cooldown = dict(cooldown)
                    if cooldown.get("result") == "first_run_exempt":
                        valid_exemption = (
                            not first_exemption_accepted
                            and isinstance(session_id, str)
                            and bool(session_id)
                            and cooldown.get("session_id") == session_id
                            and bundle_id == first_physical_run_id
                            and cooldown.get("following_run_id") == bundle_id
                        )
                        if valid_exemption:
                            first_exemption_accepted = True
                        else:
                            cooldown.update(
                                {
                                    "result": "unknown",
                                    "reason": (
                                        "first-run exemption is not unique or does not "
                                        "match physical-session provenance"
                                    ),
                                }
                            )
                    evidence[bundle_id] = cooldown
                continue
            cooldown = member.get("preceding_campaign_cooldown")
            bundle_ids = member.get("bundle_ids")
            if not isinstance(cooldown, dict) or not isinstance(bundle_ids, list):
                continue
            cooldown = dict(cooldown)
            if cooldown.get("result") == "first_run_exempt":
                member_run_id = member.get("run_id")
                bundle_ids_match_member = (
                    isinstance(member_run_id, str)
                    and bool(member_run_id)
                    and bool(bundle_ids)
                    and all(
                        isinstance(bundle_id, str)
                        and (
                            bundle_id == member_run_id
                            or (
                                bundle_id.startswith(f"{member_run_id}__r")
                                and bundle_id[len(f"{member_run_id}__r") :].isdigit()
                            )
                        )
                        for bundle_id in bundle_ids
                    )
                )
                valid_exemption = (
                    not first_exemption_accepted
                    and isinstance(session_id, str)
                    and bool(session_id)
                    and cooldown.get("session_id") == session_id
                    and isinstance(first_physical_run_id, str)
                    and bool(first_physical_run_id)
                    and member_run_id == first_physical_run_id
                    and cooldown.get("following_run_id") == first_physical_run_id
                    and bundle_ids_match_member
                )
                if valid_exemption:
                    first_exemption_accepted = True
                else:
                    cooldown.update(
                        {
                            "result": "unknown",
                            "reason": (
                                "first-run exemption is not unique or does not "
                                "match physical-session provenance"
                            ),
                        }
                    )
            for bundle_id in bundle_ids:
                if isinstance(bundle_id, str):
                    evidence[bundle_id] = cooldown
    return evidence


def _physical_cooldown_evidence_for_config(
    info: ConfigInfo,
    runs_dir: Path,
    first_cooldown: dict[str, Any],
    provenance_path: Path,
    policy: CooldownPolicy,
) -> dict[str, dict[str, Any]]:
    """Map one config invocation's physical repetitions to their own gate."""

    bundle_dirs = expected_member_dirs(info, runs_dir)
    if not bundle_dirs:
        return {}
    evidence = {bundle_dirs[0].name: dict(first_cooldown)}
    if len(bundle_dirs) == 1:
        return evidence
    manifest_path = runs_dir / "experiments" / f"{sanitize_id_component(info.run_id)}.json"
    manifest, problem = _load_json_object(manifest_path, "experiment manifest")
    cooldown_rows = manifest.get("cooldown") if isinstance(manifest, dict) else None
    for index, bundle_dir in enumerate(bundle_dirs[1:], start=1):
        row = (
            cooldown_rows[index - 1]
            if isinstance(cooldown_rows, list)
            and index - 1 < len(cooldown_rows)
            and isinstance(cooldown_rows[index - 1], dict)
            else None
        )
        if row is None:
            evidence[bundle_dir.name] = {
                **_cooldown_policy_decision_surface(policy),
                "result": "unknown",
                "reason": problem or "per-repetition cooldown evidence is missing",
                "session_id": first_cooldown.get("session_id"),
                "following_run_id": bundle_dir.name,
                "recorded_at": utc_timestamp(),
            }
            continue
        note = dict(row)
        note.setdefault("session_id", first_cooldown.get("session_id"))
        note["following_run_id"] = bundle_dir.name
        note.setdefault("recorded_at", utc_timestamp())
        raw_artifact = note.get("raw_artifact")
        if isinstance(raw_artifact, str):
            try:
                trace_path = manifest_path.parent / raw_artifact
                trace = [
                    json.loads(line)
                    for line in trace_path.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
                if not trace or not all(isinstance(item, dict) for item in trace):
                    raise ValueError("cooldown trace is empty or malformed")
                note["experiment_raw_artifact"] = raw_artifact
                note["raw_artifact"] = _write_campaign_cooldown_trace(
                    provenance_path, bundle_dir.name, trace
                )
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                note.pop("raw_artifact", None)
                note["raw_artifact_error"] = f"{type(exc).__name__}: {exc}"
        evidence[bundle_dir.name] = note
    return evidence


def _idle_baseline_from_summary(summary: dict[str, Any] | None):
    if not isinstance(summary, dict):
        return None
    raw = summary.get("idle_baseline")
    if not isinstance(raw, dict):
        return None
    try:
        from joulewise.schemas import IdleBaseline, TelemetryBackend

        gpu_freq_mhz_mean = (
            raw.get("gpu_freq_mhz_mean")
            if "gpu_freq_mhz_mean" in raw
            else raw.get("gpu_freq_hz_mean")
        )
        return IdleBaseline(
            power_w_mean=float(raw["power_w_mean"]),
            power_w_stddev=float(raw["power_w_stddev"]),
            duration_s=float(raw["duration_s"]),
            sample_count=int(raw["sample_count"]),
            telemetry_backend=TelemetryBackend(raw["telemetry_backend"]),
            gpu_idle_ratio_mean=raw.get("gpu_idle_ratio_mean"),
            gpu_idle_ratio_min=raw.get("gpu_idle_ratio_min"),
            gpu_freq_mhz_mean=gpu_freq_mhz_mean,
            gpu_freq_hz_mean=raw.get("gpu_freq_hz_mean"),
            idle_window_suspect=raw.get("idle_window_suspect"),
        )
    except (KeyError, TypeError, ValueError):
        return None


def cooldown_reference_eligibility(
    evaluation: MemberEvaluation,
) -> dict[str, Any]:
    """Return fail-closed eligibility for a baseline used by cooldown v2."""

    reasons: list[str] = []
    baseline = _idle_baseline_from_summary(evaluation.summary)
    if baseline is None:
        reasons.append("idle_baseline_unavailable")
    elif baseline.idle_window_suspect is not False:
        reasons.append("idle_window_not_clean")
    metadata = evaluation.metadata
    admission = metadata.get("environment_admission") if isinstance(metadata, dict) else None
    policy_binding = metadata.get("campaign_policy") if isinstance(metadata, dict) else None
    if not isinstance(admission, dict):
        reasons.append("environment_admission_provenance_missing")
    else:
        if admission.get("critical_environment_passed") is not True:
            reasons.append("critical_environment_not_passed")
        if admission.get("decision") != "admitted":
            reasons.append("idle_admission_not_passed")
        if admission.get("reference_provenance_present") is not True:
            reasons.append("reference_provenance_incomplete")
    if (
        not isinstance(policy_binding, dict)
        or not isinstance(policy_binding.get("sha256"), str)
        or not policy_binding.get("sha256")
    ):
        reasons.append("campaign_policy_provenance_missing")
    return {
        "bundle_id": evaluation.bundle_id,
        "eligible": baseline is not None and not reasons,
        "reasons": sorted(reasons),
        "idle_window_suspect": (
            baseline.idle_window_suspect if baseline is not None else None
        ),
        "critical_environment_passed": (
            admission.get("critical_environment_passed")
            if isinstance(admission, dict)
            else None
        ),
        "provenance_present": bool(
            isinstance(admission, dict)
            and admission.get("reference_provenance_present") is True
            and isinstance(policy_binding, dict)
            and policy_binding.get("sha256")
        ),
    }


def _anchor_from_evaluation(
    evaluation: MemberEvaluation,
    info: ConfigInfo,
    policy_binding: CampaignPolicyBinding,
    *,
    source_kind: str,
) -> dict[str, Any] | None:
    eligibility = cooldown_reference_eligibility(evaluation)
    baseline = _idle_baseline_from_summary(evaluation.summary)
    if not eligibility["eligible"] or baseline is None:
        return None
    admission = evaluation.metadata.get("environment_admission", {})  # type: ignore[union-attr]
    per_run = admission.get("per_run_environment_evaluation", {})
    return {
        "schema_version": "joulewise.cooldown_anchor.v1",
        "source_kind": source_kind,
        "bundle_id": evaluation.bundle_id,
        "run_id": info.run_id,
        "frozen_at": utc_timestamp(),
        "policy_sha256": policy_binding.sha256,
        "baseline": evaluation.summary["idle_baseline"],  # type: ignore[index]
        "eligibility": eligibility,
        "environment_snapshot_sha256": (
            per_run.get("snapshot_sha256") if isinstance(per_run, dict) else None
        ),
        "immutable_after_freeze": True,
    }


def _first_eligible_cooldown_anchor(
    evaluations: Sequence[MemberEvaluation],
    info: ConfigInfo,
    policy_binding: CampaignPolicyBinding,
    *,
    source_kind: str,
) -> dict[str, Any] | None:
    """Freeze the first eligible physical repetition in execution order."""

    for evaluation in evaluations:
        anchor = _anchor_from_evaluation(
            evaluation,
            info,
            policy_binding,
            source_kind=source_kind,
        )
        if anchor is not None:
            return anchor
    return None


def _is_neg8_reference_start(info: ConfigInfo) -> bool:
    normalized = info.run_id.lower().replace("_", "-")
    return "neg8-reference-start" in normalized


def _cooldown_anchor_eligibility(
    anchor: dict[str, Any] | None,
    policy_sha256: str,
) -> dict[str, Any]:
    return cooldown_anchor_eligibility(anchor, policy_sha256)


def prior_campaign_cooldown_anchor(
    runs_dir: Path,
    analysis_manifest_id: str | None,
    policy_sha256: str,
) -> dict[str, Any] | None:
    manifest_dir = runs_dir / "campaign_manifests"
    candidates: list[dict[str, Any]] = []
    if not manifest_dir.is_dir():
        return None
    for path in sorted(manifest_dir.glob("*.json")):
        raw, problem = _load_json_object(path, "campaign provenance")
        if problem is not None or raw is None:
            continue
        if raw.get("schema_version") != CAMPAIGN_PROVENANCE_SCHEMA:
            continue
        if (
            analysis_manifest_id is not None
            and raw.get("analysis_manifest_id") != analysis_manifest_id
        ):
            continue
        anchor = raw.get("cooldown_anchor")
        if (
            isinstance(anchor, dict)
            and _cooldown_anchor_eligibility(anchor, policy_sha256)["eligible"]
        ):
            candidates.append(dict(anchor))
    if not candidates:
        return None
    return next(
        (
            anchor
            for anchor in candidates
            if anchor.get("source_kind") == "neg8_reference_start"
        ),
        candidates[0],
    )


def _write_campaign_cooldown_trace(
    provenance_path: Path,
    following_run_id: str,
    trace: list[dict[str, Any]],
) -> dict[str, Any]:
    raw_dir = provenance_path.parent / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    filename = (
        f"{provenance_path.stem}__cooldown_before_"
        f"{sanitize_id_component(following_run_id)}.jsonl"
    )
    path = raw_dir / filename
    payload = "".join(json.dumps(row, sort_keys=True) + "\n" for row in trace)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(payload)
    return {
        "path": f"raw/{filename}",
        "sha256": _sha256_bytes(payload.encode("utf-8")),
        "records": len(trace),
    }


def campaign_cooldown_before_member(
    *,
    previous_info: ConfigInfo,
    previous_evaluation: MemberEvaluation,
    following_info: ConfigInfo,
    provenance_path: Path,
    session_id: str,
    policy_binding: CampaignPolicyBinding | None = None,
    frozen_anchor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Measure D-014 recovery and attach its tri-state result to the next run."""
    note: dict[str, Any] = {
        "session_id": session_id,
        "after_bundle_id": previous_evaluation.bundle_id,
        "following_run_id": following_info.run_id,
        "recorded_at": utc_timestamp(),
    }
    baseline = _idle_baseline_from_summary(previous_evaluation.summary)
    if policy_binding is not None and policy_binding.policy.idle_admission.enabled:
        note.update(_cooldown_policy_decision_surface(policy_binding.policy.cooldown))
        reference_eligibility = cooldown_reference_eligibility(previous_evaluation)
        anchor_eligibility = _cooldown_anchor_eligibility(
            frozen_anchor, policy_binding.sha256
        )
        note["policy_version"] = policy_binding.policy.cooldown.policy_version
        note["reference_eligibility"] = reference_eligibility
        note["anchor_eligibility"] = anchor_eligibility
        note["anchor_provenance"] = frozen_anchor
        if reference_eligibility["eligible"]:
            note["reference_selection"] = "preceding_eligible_baseline"
        else:
            anchor_baseline = (
                frozen_anchor.get("baseline")
                if isinstance(frozen_anchor, dict)
                and anchor_eligibility["eligible"]
                else None
            )
            if isinstance(anchor_baseline, dict):
                baseline = _idle_baseline_from_summary(
                    {"idle_baseline": anchor_baseline}
                )
                note["reference_selection"] = "frozen_clean_anchor"
            else:
                baseline = None
            if baseline is None:
                note.update(
                    {
                        "result": "unknown",
                        "reason": (
                            "preceding baseline is ineligible and no eligible frozen "
                            "clean cooldown anchor is available"
                        ),
                    }
                )
                return note
    elif baseline is None:
        note.update({"result": "unknown", "reason": "previous idle baseline unavailable"})
        return note
    try:
        config_raw = json.loads(previous_info.path.read_text(encoding="utf-8"))
        from joulewise import adapters
        from joulewise.clock import SystemClock
        from joulewise.controller import cooldown_gate
        from joulewise.interfaces import AdapterFailure
        from joulewise.schemas import BenchmarkConfig, TelemetryBackend

        config = BenchmarkConfig.from_mapping(config_raw)
        if config.hardware_target.telemetry_backend == TelemetryBackend.MOCK:
            note.update(
                {
                    "result": "unknown",
                    "reason": "mock telemetry has no thermal recovery evidence",
                }
            )
            return note
        clock = SystemClock()
        telemetry, failure = adapters.resolve_telemetry(config, clock)
        if telemetry is None:
            reason = failure.message if failure is not None else "telemetry adapter unavailable"
            note.update({"result": "unknown", "reason": reason})
            return note
        cooldown_run_id = (
            f"{sanitize_id_component(session_id)}-cooldown-before-"
            f"{sanitize_id_component(following_info.run_id)}"
        )
        note["cooldown_run_id"] = cooldown_run_id
        try:
            gate = cooldown_gate(
                telemetry,
                baseline,
                config,
                clock,
                run_id=cooldown_run_id,
                policy=(
                    policy_binding.policy.cooldown
                    if policy_binding is not None
                    else None
                ),
            )
        except AdapterFailure as exc:
            note.update(
                {
                    "result": "unknown",
                    "reason": exc.message,
                    "failure_reason": exc.failure_reason.value,
                }
            )
            return note
        trace = gate.pop("_trace", [])
        note.update(gate)
        if trace:
            note["raw_artifact"] = _write_campaign_cooldown_trace(
                provenance_path, following_info.run_id, trace
            )
        else:
            note.update({"result": "unknown", "reason": "cooldown trace was empty"})
    except Exception as exc:  # noqa: BLE001 - evidence failure must stay fail-closed.
        note.update({"result": "unknown", "reason": f"{type(exc).__name__}: {exc}"})
    return note


def _cooldown_policy_decision_surface(policy: CooldownPolicy) -> dict[str, Any]:
    """Return the v2 fields recorded even when evidence fails before capture."""

    return {
        "policy_version": policy.policy_version,
        "thresholds": {
            "subwindow_s": policy.subwindow_s,
            "sustained_window_s": policy.sustained_window_s,
            "coverage_fraction": policy.coverage_fraction,
            "tolerance_fraction": policy.tolerance_fraction,
            "cap_s": policy.cap_s,
            "absolute_ceiling_w": policy.absolute_ceiling_w,
            "require_thermal_nominal": policy.require_thermal_nominal,
        },
        "reference_power_w": None,
        "decision_rolling_mean_power_w": None,
        "window_required_s": policy.sustained_window_s,
        "window_span_s": 0.0,
        "window_coverage_s": 0.0,
        "required_coverage_s": (
            policy.coverage_fraction * policy.sustained_window_s
        ),
        "span_complete": False,
        "coverage_complete": False,
        "window_complete": False,
        "thermal_pressure": None,
        "thermal_nominal": None,
        "release_criterion": {
            "power": "duration_weighted_rolling_mean <= effective_upper_w",
            "reference_bound": "reference_power_w * (1 + tolerance_fraction)",
            "absolute_ceiling_role": "additional_upper_cap",
            "window": "complete_sustained_span_and_minimum_coverage",
            "coverage": (
                "window_coverage_s >= coverage_fraction * sustained_window_s"
            ),
            "thermal": (
                "nominal_required"
                if policy.require_thermal_nominal
                else "not_required"
            ),
        },
    }


def record_campaign_member_provenance(
    path: Path,
    manifest: dict[str, Any],
    *,
    info: ConfigInfo,
    bundle_ids: list[str],
    evaluations: list[MemberEvaluation],
    execution: str,
    cooldown: dict[str, Any] | None,
    cooldowns_by_bundle: dict[str, dict[str, Any]] | None = None,
) -> None:
    recorded_cooldown = (
        cooldown if execution in {"invoked", "blocked_before_invoke"} else None
    )
    claim_evidence: list[dict[str, Any]] = []
    for evaluation in evaluations:
        waiver = evaluation.waiver
        claim_evidence.append(
            {
                "bundle_id": evaluation.bundle_id,
                "claim_evidence_flags": list(evaluation.claim_evidence_flags),
                "waiver": (
                    {
                        "target_kind": waiver.target_kind,
                        "target": waiver.target,
                        "reason": waiver.reason,
                        "approver": waiver.approver,
                        "timestamp": waiver.timestamp,
                        "scope": waiver.scope,
                    }
                    if waiver is not None
                    else None
                ),
            }
        )
    member_row = {
            "config": info.path.name,
            "run_id": info.run_id,
            "bundle_ids": bundle_ids,
            "execution": execution,
            "preceding_campaign_cooldown": recorded_cooldown,
            "claim_evidence": claim_evidence,
        }
    if cooldowns_by_bundle is not None:
        member_row["physical_members"] = [
            {
                "bundle_id": bundle_id,
                "preceding_campaign_cooldown": cooldowns_by_bundle.get(bundle_id),
            }
            for bundle_id in bundle_ids
        ]
    manifest["members"].append(member_row)
    gate_candidates = (
        [cooldowns_by_bundle.get(bundle_id) for bundle_id in bundle_ids]
        if cooldowns_by_bundle is not None
        else [recorded_cooldown]
    )
    manifest["cooldown_gates"].extend(
        gate
        for gate in gate_candidates
        if isinstance(gate, dict) and gate.get("result") != "first_run_exempt"
    )
    write_campaign_provenance(path, manifest)


def skipped_log_extra(state: ExistingState) -> dict[str, Any] | None:
    if state.members_total is None:
        return None
    return {
        "members_succeeded": state.members_succeeded,
        "members_total": state.members_total,
    }


def classify_campaign_members(
    evaluations: list[MemberEvaluation],
    missing: list[str],
) -> dict[str, list[str]]:
    categories = {"usable": [], "waived": [], "failed": [], "missing": []}
    for evaluation in evaluations:
        if evaluation.usable:
            categories["usable"].append(evaluation.bundle_id)
        elif evaluation.waived:
            categories["waived"].append(evaluation.bundle_id)
        else:
            categories["failed"].append(evaluation.bundle_id)
    categories["missing"].extend(missing)
    return categories


def evaluation_failure_detail(evaluation: MemberEvaluation) -> str:
    parts = [
        f"{evaluation.bundle_id}: status={evaluation.status!r}",
        f"strict_valid={evaluation.strict_valid}",
        f"collection_integrity_flags={list(evaluation.collection_integrity_flags)}",
        f"claim_evidence_flags={list(evaluation.claim_evidence_flags)}",
        f"validation_problems={list(evaluation.validation_problems)}",
    ]
    if evaluation.prompt_hash_check.status != "not_applicable":
        parts.append(f"prompt_hash_check={evaluation.prompt_hash_check.to_log()!r}")
    return ", ".join(parts)


def collection_verdict_for(categories: dict[str, list[str]]) -> tuple[str, list[str]]:
    usable = categories["usable"]
    waived = categories["waived"]
    failed = categories["failed"]
    missing = categories["missing"]
    reasons: list[str] = []
    if missing:
        reasons.append("missing member bundle(s): " + ", ".join(missing))
    if failed:
        reasons.append("invalid unwaived member bundle(s): " + ", ".join(failed))
    if waived:
        reasons.append("waived member bundle(s): " + ", ".join(waived))
    if not usable and not waived and not failed and not missing:
        return "invalid", ["no campaign members were evaluated"]
    if missing:
        return "blocked", reasons
    if failed:
        return "invalid", reasons
    if usable and not waived:
        return "usable", []
    if usable and waived:
        return "partial", reasons
    if waived:
        return "invalid", reasons + ["no usable unwaived members"]
    return "invalid", reasons or ["no usable members"]


def _manifest_readiness_reasons(state: AnalysisManifestState) -> list[str]:
    reasons = {"analysis_manifest_invalid"}
    for problem in state.problems:
        if "freeze_status" in problem or "not frozen" in problem:
            reasons.add("analysis_manifest_not_frozen")
        if "order_manifest.sha256" in problem and (
            "mismatch" in problem or "source hash mismatch" in problem
        ):
            reasons.add("order_manifest_hash_mismatch")
        if "config_sha256" in problem and (
            "mismatch" in problem or "does not match config bytes" in problem
        ):
            reasons.add("config_hash_mismatch")
    return sorted(reasons)


def _precheck_for_contrast(
    summary: dict[str, Any] | None, contrast: dict[str, Any]
) -> dict[str, Any] | None:
    if not isinstance(summary, dict):
        return None
    root = summary.get("window_evidence_precheck")
    if not isinstance(root, dict):
        return None
    metric = contrast.get("metric")
    if not isinstance(metric, dict):
        return None
    metric = estimation_metric(metric)
    metric_name = metric.get("name")
    metric_tag = metric.get("metric_tag")
    if metric_tag == "gross_request" or metric_name == "gross_energy_j":
        value = root.get("gross_request")
        return value if isinstance(value, dict) else None
    if metric_tag == "idle_request" or metric_name in {
        "energy_request_j",
        "idle_subtracted_energy_j",
    }:
        value = root.get("idle_subtracted_request")
        return value if isinstance(value, dict) else None
    if isinstance(metric_name, str) and metric_name.startswith("phase_energy_j."):
        phase = root.get("phase")
        phase_name = metric_name.rsplit(".", 1)[-1]
        value = phase.get(phase_name) if isinstance(phase, dict) and phase_name else None
        return value if isinstance(value, dict) else None
    return None


def _metric_is_finite(summary: dict[str, Any] | None, contrast: dict[str, Any]) -> bool:
    if not isinstance(summary, dict):
        return False
    metric = contrast.get("metric")
    metric = estimation_metric(metric) if isinstance(metric, dict) else metric
    metric_name = metric.get("name") if isinstance(metric, dict) else None
    if not isinstance(metric_name, str) or not metric_name:
        return False
    value: Any = summary
    for part in metric_name.split("."):
        if not isinstance(value, dict) or part not in value:
            return False
        value = value[part]
    return (
        not isinstance(value, bool)
        and isinstance(value, int | float)
        and math.isfinite(float(value))
    )


def _contrast_uses_idle_subtraction(contrast: dict[str, Any]) -> bool:
    metric = contrast.get("metric")
    if not isinstance(metric, dict):
        return False
    metric = estimation_metric(metric)
    return metric.get("metric_tag") == "idle_request" or metric.get("name") in {
        "energy_request_j",
        "idle_subtracted_energy_j",
    }


def _member_readiness_reasons(
    evaluation: MemberEvaluation, contrast: dict[str, Any]
) -> list[str]:
    reasons: set[str] = set()
    if not evaluation.strict_valid:
        reasons.add("bundle_strict_invalid")
    if evaluation.status != "succeeded":
        reasons.add("bundle_status_not_succeeded")
    cleanup_flags = {
        "runtime_cleanup_ok",
        "remote_cleanup_failed",
    }
    if cleanup_flags & set(evaluation.unwaived_claim_evidence_flags()):
        reasons.add("required_error_term_unknown")
    if "config_manifest_mismatch" in evaluation.collection_integrity_flags:
        reasons.add("config_hash_mismatch")
    if not _metric_is_finite(evaluation.summary, contrast):
        reasons.add("metric_missing_or_nonfinite")
    precheck = _precheck_for_contrast(evaluation.summary, contrast)
    if precheck is None:
        reasons.add("window_evidence_precheck_missing")
    else:
        embedded = precheck.get("reasons")
        if isinstance(embedded, list):
            reasons.update(reason for reason in embedded if isinstance(reason, str))
        else:
            reasons.add("window_evidence_precheck_missing")
        if precheck.get("eligible") is not True and not embedded:
            reasons.add("window_evidence_precheck_missing")

    cooldown = evaluation.preceding_campaign_cooldown
    cooldown_result = cooldown.get("result") if isinstance(cooldown, dict) else None
    raw_verified = (
        isinstance(cooldown, dict)
        and verify_cooldown_raw_provenance(
            cooldown, evaluation.bundle_path.parent / "campaign_manifests"
        )
    )
    if cooldown_result == "cap_hit":
        reasons.add("cooldown_cap_hit")
        if not raw_verified:
            reasons.add("campaign_cooldown_evidence_missing")
    elif cooldown_result == "recovered" and not raw_verified:
        reasons.add("campaign_cooldown_evidence_missing")
    elif cooldown_result not in ACCEPTED_CAMPAIGN_COOLDOWN_RESULTS:
        reasons.add("campaign_cooldown_evidence_missing")

    quality = evaluation.summary.get("measurement_quality") if evaluation.summary else None
    if isinstance(quality, dict) and quality.get("cooldown_cap_hit") is True:
        reasons.add("cooldown_cap_hit")

    if _contrast_uses_idle_subtraction(contrast):
        idle_state = quality.get("idle_window_suspect") if isinstance(quality, dict) else None
        if idle_state is True:
            reasons.add("idle_window_suspect")
        elif idle_state is not False:
            reasons.add("idle_window_suspect_unknown")
    metric = contrast.get("metric")
    if isinstance(metric, dict) and metric.get("ratio_estimand") is not None:
        reasons.update(
            ratio_evidence_reasons(
                evaluation.ratio_token_provenance,
                evaluation.ratio_token_provenance,
            )
        )
    return sorted(reasons)


def claim_readiness_for(
    analysis_manifest: AnalysisManifestState | None,
    collection_verdict: str,
    evaluations: list[MemberEvaluation],
) -> dict[str, Any]:
    base = {
        "verdict": "not_assessed",
        "reasons": [],
        "required_contrast_ids": [],
        "ready_contrast_ids": [],
        "not_ready_contrasts": [],
        "note": CLAIM_READINESS_NOTE,
    }
    if analysis_manifest is None:
        return base
    if not analysis_manifest.valid:
        base.update(
            {
                "verdict": "not_ready_for_analysis",
                "reasons": _manifest_readiness_reasons(analysis_manifest),
            }
        )
        return base
    contrasts = analysis_manifest.raw.get("contrasts")
    if not isinstance(contrasts, list) or not contrasts:
        return base
    required_ids = [
        contrast.get("contrast_id")
        for contrast in contrasts
        if isinstance(contrast, dict) and isinstance(contrast.get("contrast_id"), str)
    ]
    base["required_contrast_ids"] = required_ids
    entries = analysis_manifest.raw.get("entries")
    assert isinstance(entries, list)
    evaluation_by_bundle = {evaluation.bundle_id: evaluation for evaluation in evaluations}
    ready_ids: list[str] = []
    not_ready: list[dict[str, Any]] = []
    all_reasons: set[str] = set()

    for contrast in contrasts:
        if not isinstance(contrast, dict):
            continue
        contrast_id = contrast.get("contrast_id")
        if not isinstance(contrast_id, str):
            continue
        reasons: set[str] = set()
        affected: list[str] = []
        ratio_pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
        if collection_verdict != "usable":
            reasons.add("fixed_n_plan_incomplete")
        block_ids = contrast.get("block_ids")
        cell_a = contrast.get("cell_a_id")
        cell_b = contrast.get("cell_b_id")
        if not isinstance(block_ids, list) or not all(isinstance(item, str) for item in block_ids):
            reasons.add("fixed_n_plan_incomplete")
            block_ids = []
        complete_blocks = 0
        for block_id in block_ids:
            pair: list[MemberEvaluation] = []
            for cell_id in (cell_a, cell_b):
                matches = [
                    entry
                    for entry in entries
                    if isinstance(entry, dict)
                    and entry.get("block_id") == block_id
                    and entry.get("cell_id") == cell_id
                ]
                if len(matches) != 1:
                    reasons.update({"bundle_missing", "paired_block_incomplete"})
                    continue
                run_id = matches[0].get("run_id")
                evaluation = evaluation_by_bundle.get(run_id)
                if evaluation is None:
                    reasons.update({"bundle_missing", "paired_block_incomplete"})
                    if isinstance(run_id, str):
                        affected.append(run_id)
                    continue
                affected.append(evaluation.bundle_id)
                pair.append(evaluation)
                reasons.update(_member_readiness_reasons(evaluation, contrast))
            if len(pair) == 2:
                metric = contrast.get("metric")
                if isinstance(metric, dict) and metric.get("ratio_estimand") is not None:
                    ratio_pairs.append(
                        (
                            pair[0].ratio_token_provenance,
                            pair[1].ratio_token_provenance,
                        )
                    )
                    reasons.update(
                        ratio_evidence_reasons(
                            pair[0].ratio_token_provenance,
                            pair[1].ratio_token_provenance,
                        )
                    )
                complete_blocks += 1
        if ratio_pairs:
            reasons.update(ratio_collection_evidence_reasons(tuple(ratio_pairs)))
        design = analysis_manifest.raw.get("design")
        sampling_plan = design.get("sampling_plan") if isinstance(design, dict) else None
        planned_n = (
            sampling_plan.get("planned_n_blocks") if isinstance(sampling_plan, dict) else None
        )
        if (
            isinstance(planned_n, bool)
            or not isinstance(planned_n, int)
            or planned_n < 1
            or len(block_ids) != planned_n
            or complete_blocks != planned_n
        ):
            reasons.add("fixed_n_plan_incomplete")
        if reasons:
            ordered = sorted(reasons)
            all_reasons.update(ordered)
            not_ready.append(
                {
                    "contrast_id": contrast_id,
                    "affected_member_ids": sorted(set(affected)),
                    "reasons": ordered,
                }
            )
        else:
            ready_ids.append(contrast_id)

    base.update(
        {
            "verdict": (
                "ready_for_analysis"
                if len(ready_ids) == len(required_ids) and required_ids
                else "not_ready_for_analysis"
            ),
            "reasons": sorted(all_reasons),
            "ready_contrast_ids": ready_ids,
            "not_ready_contrasts": not_ready,
        }
    )
    return base


def sampling_audit_for(analysis_manifest: AnalysisManifestState | None) -> dict[str, Any]:
    planned_n: int | None = None
    design_name: str | None = None
    registered: list[str] = []
    if analysis_manifest is not None:
        design = analysis_manifest.raw.get("design")
        sampling = design.get("sampling_plan") if isinstance(design, dict) else None
        if isinstance(sampling, dict):
            design_name = (
                sampling.get("design")
                if isinstance(sampling.get("design"), str)
                else None
            )
            value = sampling.get("planned_n_blocks")
            planned_n = value if isinstance(value, int) and not isinstance(value, bool) else None
        entries = analysis_manifest.raw.get("entries")
        if isinstance(entries, list):
            registered = sorted(
                entry["run_id"]
                for entry in entries
                if isinstance(entry, dict) and isinstance(entry.get("run_id"), str)
            )
    return {
        "design": design_name,
        "planned_n_blocks": planned_n,
        "registered_bundle_ids": registered,
        "unregistered_matching_bundle_ids": [],
        "valid_replacements": [],
        "top_up_suspected": False,
    }


def print_verdict(
    collection_verdict: str,
    collection_reasons: list[str],
    categories: dict[str, list[str]],
    claim_readiness: dict[str, Any],
) -> None:
    print("COLLECTION VERDICT:")
    print(f"  verdict: {collection_verdict}")
    for reason in collection_reasons:
        print(f"  reason: {reason}")
    for key in ("usable", "waived", "failed", "missing"):
        members = ", ".join(categories[key]) if categories[key] else "<none>"
        print(f"  {key}: {members}")
    print("CLAIM-INPUT READINESS:")
    print(f"  verdict: {claim_readiness['verdict']}")
    for reason in claim_readiness["reasons"]:
        print(f"  reason: {reason}")
    print(f"  note: {claim_readiness['note']}")


def append_verdict(
    log_path: Path,
    *,
    collection_verdict: str,
    collection_reasons: list[str],
    categories: dict[str, list[str]],
    claim_readiness: dict[str, Any],
    analysis_manifest: AnalysisManifestState | None,
    sampling_audit: dict[str, Any],
    members: list[MemberEvaluation],
    campaign_provenance_path: Path | None,
    warning: str | None,
    preflight: dict[str, Any],
) -> None:
    row: dict[str, Any] = {
        "schema_version": CAMPAIGN_VERDICT_SCHEMA,
        "timestamp": utc_timestamp(),
        "record_type": "campaign_verdict",
        "status": "verdict",
        "analysis_manifest": (
            analysis_manifest.to_log() if analysis_manifest is not None else None
        ),
        "collection": {
            "verdict": collection_verdict,
            "reasons": collection_reasons,
            "categories": categories,
        },
        "claim_readiness": claim_readiness,
        "sampling_audit": sampling_audit,
        "members": [member.to_log() for member in members],
        "campaign_provenance": (
            {"manifest_path": str(campaign_provenance_path)}
            if campaign_provenance_path is not None
            else None
        ),
        "preflight": preflight,
    }
    if warning is not None:
        row["block_order_warning"] = warning
    append_log(log_path, row)


def append_environment_preflight_verdict(
    log_path: Path,
    *,
    analysis_manifest: AnalysisManifestState | None,
    campaign_provenance_path: Path | None,
    preflight: dict[str, Any],
    environment_guard: dict[str, Any],
    reason: str,
) -> None:
    """Always terminate a rejected environment preflight with a v2 verdict."""

    recorded_preflight = dict(preflight)
    recorded_preflight["environment_guard"] = environment_guard
    categories = {"usable": [], "waived": [], "failed": [], "missing": []}
    append_verdict(
        log_path,
        collection_verdict="invalid",
        collection_reasons=[reason],
        categories=categories,
        claim_readiness=claim_readiness_for(analysis_manifest, "invalid", []),
        analysis_manifest=analysis_manifest,
        sampling_audit=sampling_audit_for(analysis_manifest),
        members=[],
        campaign_provenance_path=campaign_provenance_path,
        warning=None,
        preflight=recorded_preflight,
    )


def _write_immutable_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(value)


def _axi_bundle_digest(path: Path) -> str:
    inventory = {
        file.relative_to(path).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
        for file in sorted(candidate for candidate in path.rglob("*") if candidate.is_file())
    }
    return axi_sha256_bytes(axi_canonical_json_bytes(inventory))


def _axi_entry_config_paths(state: AnalysisManifestState) -> list[Path]:
    result: list[Path] = []
    seen: set[Path] = set()
    for entry in sorted(state.raw.get("entries", []), key=lambda row: row["order_index"]):
        path = _resolve_analysis_reference(state.path.parent, entry["config"])
        if path not in seen:
            result.append(path)
            seen.add(path)
    return result


def _axi_attempt_bundle_path(
    runs_dir: Path,
    manifest_id: str,
    entry_id: str,
    attempt_ordinal: int,
    run_id: str,
) -> Path:
    return (
        runs_dir
        / "axi_attempt_bundles"
        / manifest_id
        / sanitize_id_component(entry_id)
        / f"a{attempt_ordinal}"
        / sanitize_id_component(run_id)
    )


def _axi_discover_finalized_bundles(
    runs_dir: Path,
    manifest: dict[str, Any],
) -> dict[tuple[str, int, str], Path]:
    """Discover finalized attempts from the bundle store, independently of the ledger."""

    root = runs_dir / "axi_attempt_bundles" / manifest["manifest_id"]
    if not root.is_dir():
        return {}
    entry_by_component: dict[str, str] = {}
    for entry in manifest["entries"]:
        component = sanitize_id_component(entry["entry_id"])
        if component in entry_by_component:
            raise AnalysisManifestError(
                "analysis_attempt_ledger_gap",
                "manifest entry identifiers collide in the bundle store",
            )
        entry_by_component[component] = entry["entry_id"]

    result: dict[tuple[str, int, str], Path] = {}
    for summary_path in sorted(root.rglob("summary_metrics.json")):
        bundle_path = summary_path.parent
        relative = summary_path.relative_to(root)
        if len(relative.parts) != 4:
            raise AnalysisManifestError(
                "analysis_attempt_ledger_gap",
                f"finalized bundle has an invalid store location: {bundle_path}",
            )
        entry_component, attempt_component, run_component, marker = relative.parts
        if marker != "summary_metrics.json" or entry_component not in entry_by_component:
            raise AnalysisManifestError(
                "analysis_attempt_ledger_gap",
                f"finalized bundle is outside a manifest entry: {bundle_path}",
            )
        if not attempt_component.startswith("a") or not attempt_component[1:].isdigit():
            raise AnalysisManifestError(
                "analysis_attempt_ledger_gap",
                f"finalized bundle has an invalid attempt location: {bundle_path}",
            )
        attempt_ordinal = int(attempt_component[1:])
        try:
            metadata = json.loads((bundle_path / "metadata.json").read_bytes())
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AnalysisManifestError(
                "analysis_attempt_ledger_gap",
                f"finalized bundle metadata is unavailable: {bundle_path}",
            ) from exc
        run_id = metadata.get("run_id") if isinstance(metadata, dict) else None
        if not isinstance(run_id, str) or not run_id or sanitize_id_component(run_id) != run_component:
            raise AnalysisManifestError(
                "analysis_attempt_ledger_gap",
                f"finalized bundle run identity does not match its store location: {bundle_path}",
            )
        key = (entry_by_component[entry_component], attempt_ordinal, run_id)
        if key in result:
            raise AnalysisManifestError(
                "analysis_attempt_ledger_gap",
                f"duplicate finalized bundle identity: {key}",
            )
        result[key] = bundle_path
    return result


def _axi_load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_dir():
        return rows
    for row_path in sorted(path.glob("*.jsonl")):
        lines = [line for line in row_path.read_text(encoding="utf-8").splitlines() if line]
        if len(lines) != 1:
            raise ValueError(f"attempt row artifact must contain one row: {row_path}")
        value = json.loads(lines[0])
        if not isinstance(value, dict):
            raise ValueError(f"attempt row artifact is not an object: {row_path}")
        rows.append(value)
    return rows


def _axi_evidence_map(path: Path, pattern: str) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    if not path.is_dir():
        return result
    for evidence_path in sorted(path.glob(pattern)):
        raw = evidence_path.read_bytes()
        digest = axi_sha256_bytes(raw)
        if digest in result:
            raise ValueError(f"duplicate AXI attempt evidence digest: {digest}")
        result[digest] = raw
    return result


def _axi_strict_reason_codes(problems: Sequence[str]) -> list[str]:
    """Project strict validator diagnostics onto its frozen reason enum."""

    codes = {
        problem.split(":", 2)[1]
        for problem in problems
        if problem.startswith("axi:") and len(problem.split(":", 2)) == 3
    }
    unknown = sorted(codes - AXI_VALIDATOR_REASON_CODES)
    if unknown:
        raise ValueError(
            "strict validator returned reason codes outside "
            f"AXI_VALIDATOR_REASON_CODES: {unknown}"
        )
    if problems and not codes:
        raise ValueError(
            "strict-invalid AXI bundle produced no AXI_VALIDATOR_REASON_CODES value"
        )
    return sorted(codes)


def run_axi_spec_campaign(
    args: argparse.Namespace,
    state: AnalysisManifestState,
    *,
    runs_dir: Path,
    policy_binding: CampaignPolicyBinding | None = None,
    log_path: Path | None = None,
    preflight: dict[str, Any] | None = None,
) -> int:
    """Dispatch a frozen v2 manifest with immutable per-attempt evidence.

    Each Entry receives an isolated runs directory because paired configs keep
    the same normalized ``run_id``.  The isolation path is campaign custody,
    not a new runtime-support claim.
    """

    if not state.valid:
        print("error: AXI analysis manifest is invalid: " + "; ".join(state.problems), file=sys.stderr)
        return 2
    manifest = state.raw
    manifest_id = manifest["manifest_id"]
    entries = sorted(manifest["entries"], key=lambda row: row["order_index"])
    config_infos: dict[str, ConfigInfo] = {}
    for entry in entries:
        path = _resolve_analysis_reference(state.path.parent, entry["config"])
        loaded = load_config_info(path)
        if isinstance(loaded, ConfigError):
            print(f"error: {loaded.message}", file=sys.stderr)
            return 2
        if loaded.repetitions != 1:
            print("error: AXI manifest entries require repetitions == 1", file=sys.stderr)
            return 2
        config_infos[entry["entry_id"]] = loaded

    evidence_root = runs_dir / "axi_attempt_evidence" / manifest_id
    identities_dir = evidence_root / "attempt_identities"
    receipts_dir = evidence_root / "dispatch_receipts"
    strict_dir = evidence_root / "strict_validation"
    rows_dir = evidence_root / "ledger_rows"
    reports_dir = evidence_root / "output_identity_reports"
    if args.dry_run:
        if policy_binding is not None:
            print(
                "Campaign policy: "
                f"{policy_binding.policy.policy_id} sha256={policy_binding.sha256}"
            )
        for entry in entries:
            info = config_infos[entry["entry_id"]]
            command = command_for(
                info.path,
                runs_dir / "axi_attempt_bundles" / manifest_id / entry["entry_id"] / "a0",
                args.cli_cmd,
            )
            print(f"dry_run {entry['entry_id']} attempt=0: {shell_quote(command)}")
        return 0

    lock_path: Path | None = None
    try:
        lock_path = acquire_campaign_lock(runs_dir)
        child_environment: dict[str, str] | None = None
        campaign_provenance_path: Path | None = None
        campaign_provenance: dict[str, Any] | None = None
        previous_physical_info: ConfigInfo | None = None
        previous_physical_evaluation: MemberEvaluation | None = None
        frozen_cooldown_anchor: dict[str, Any] | None = None
        if policy_binding is not None:
            campaign_provenance_path, campaign_provenance = new_campaign_provenance(
                state.path.parent, runs_dir, state, policy_binding
            )
            frozen_cooldown_anchor = prior_campaign_cooldown_anchor(
                runs_dir, state.manifest_id, policy_binding.sha256
            )
            campaign_provenance["cooldown_anchor"] = frozen_cooldown_anchor
            campaign_provenance["cooldown_anchor_strategy"] = (
                "first_admission_passing"
            )
            write_campaign_provenance(
                campaign_provenance_path, campaign_provenance
            )
            try:
                environment_preflight = campaign_environment_preflight(
                    policy_binding,
                    arm_quiet_mode=bool(getattr(args, "arm_quiet_mode", False)),
                    arm_countdown_s=int(getattr(args, "arm_countdown_s", 5)),
                    override_path=getattr(args, "environment_override", None),
                )
            except Exception as exc:  # noqa: BLE001 - fail before AXI member 1
                environment_error = {
                    "status": "error",
                    "reason": f"{type(exc).__name__}: {exc}",
                }
                assert campaign_provenance_path is not None
                assert campaign_provenance is not None
                campaign_provenance["environment_preflight"] = environment_error
                write_campaign_provenance(
                    campaign_provenance_path, campaign_provenance
                )
                if log_path is not None:
                    append_environment_preflight_verdict(
                        log_path,
                        analysis_manifest=state,
                        campaign_provenance_path=campaign_provenance_path,
                        preflight=preflight or {},
                        environment_guard=environment_error,
                        reason="environment preflight failed before AXI entry 1",
                    )
                print(f"error: environment preflight failed: {exc}", file=sys.stderr)
                return 2
            assert campaign_provenance_path is not None
            assert campaign_provenance is not None
            campaign_provenance["environment_preflight"] = environment_preflight
            write_campaign_provenance(campaign_provenance_path, campaign_provenance)
            if not environment_preflight["admitted"]:
                evaluation = environment_preflight["evaluation"]
                print(
                    "ENVIRONMENT PREFLIGHT FAILED: "
                    + "; ".join(
                        f"{row['field']}={row['actual']!r} ({row['status']})"
                        for row in evaluation["findings"]
                        if row["status"] != "pass"
                    ),
                    file=sys.stderr,
                )
                print(
                    "override binding: "
                    f"snapshot_sha256={evaluation['snapshot_sha256']} "
                    f"findings_sha256={evaluation['findings_sha256']}",
                    file=sys.stderr,
                )
                if log_path is not None:
                    append_environment_preflight_verdict(
                        log_path,
                        analysis_manifest=state,
                        campaign_provenance_path=campaign_provenance_path,
                        preflight=preflight or {},
                        environment_guard=environment_preflight,
                        reason="environment preflight rejected before AXI entry 1",
                    )
                return 1
            child_environment = os.environ.copy()
            child_environment[CAMPAIGN_POLICY_PATH_ENV] = str(policy_binding.path)
            child_environment[CAMPAIGN_POLICY_SHA256_ENV] = policy_binding.sha256
            child_environment[CAMPAIGN_PREFLIGHT_JSON_ENV] = json.dumps(
                environment_preflight,
                sort_keys=True,
                separators=(",", ":"),
            )
        rows = _axi_load_rows(rows_dir)
        by_entry: dict[str, list[dict[str, Any]]] = {
            entry["entry_id"]: [] for entry in entries
        }
        for row in rows:
            by_entry.setdefault(str(row.get("entry_id")), []).append(row)

        for entry in entries:
            entry_id = entry["entry_id"]
            prior = sorted(by_entry[entry_id], key=lambda row: row["attempt_ordinal"])
            eligible = [row for row in prior if row["eligible_for_analysis"]]
            if eligible:
                continue
            attempt_ordinal = len(prior)
            identity = AttemptIdentity(
                manifest_id=manifest_id,
                entry_id=entry_id,
                pair_id=entry["pair_id"],
                arm=entry["arm"],
                attempt_ordinal=attempt_ordinal,
            )
            stem = f"{entry['order_index']:06d}__{sanitize_id_component(entry_id)}__a{attempt_ordinal}"
            identity_value = {
                "manifest_id": identity.manifest_id,
                "entry_id": identity.entry_id,
                "pair_id": identity.pair_id,
                "arm": identity.arm,
                "attempt_ordinal": identity.attempt_ordinal,
            }
            _write_immutable_bytes(
                identities_dir / f"{stem}.json",
                (json.dumps(identity_value, indent=2, sort_keys=True) + "\n").encode("utf-8"),
            )

            info = config_infos[entry_id]
            physical_run_id = (
                f"{sanitize_id_component(entry_id)}__a{attempt_ordinal}__"
                f"{sanitize_id_component(info.run_id)}"
            )
            physical_info = replace(
                info,
                run_id=physical_run_id,
                raw_run_id=physical_run_id,
                repetitions=1,
            )
            attempt_runs_dir = (
                runs_dir
                / "axi_attempt_bundles"
                / manifest_id
                / sanitize_id_component(entry_id)
                / f"a{attempt_ordinal}"
            )
            command = command_for(info.path, attempt_runs_dir, args.cli_cmd)
            cooldown_note: dict[str, Any] | None = None
            if policy_binding is not None:
                assert campaign_provenance_path is not None
                assert campaign_provenance is not None
                if campaign_provenance.get("first_physical_run_id") is None:
                    cooldown_note = {
                        **_cooldown_policy_decision_surface(
                            policy_binding.policy.cooldown
                        ),
                        "result": "first_run_exempt",
                        "session_id": campaign_provenance["session_id"],
                        "following_run_id": physical_run_id,
                        "recorded_at": utc_timestamp(),
                    }
                    campaign_provenance["first_physical_run_id"] = physical_run_id
                    write_campaign_provenance(
                        campaign_provenance_path, campaign_provenance
                    )
                elif (
                    previous_physical_info is not None
                    and previous_physical_evaluation is not None
                ):
                    cooldown_note = campaign_cooldown_before_member(
                        previous_info=previous_physical_info,
                        previous_evaluation=previous_physical_evaluation,
                        following_info=physical_info,
                        provenance_path=campaign_provenance_path,
                        session_id=campaign_provenance["session_id"],
                        policy_binding=policy_binding,
                        frozen_anchor=frozen_cooldown_anchor,
                    )
                else:
                    cooldown_note = {
                        **_cooldown_policy_decision_surface(
                            policy_binding.policy.cooldown
                        ),
                        "result": "unknown",
                        "reason": "previous physical AXI entry evaluation unavailable",
                        "session_id": campaign_provenance["session_id"],
                        "following_run_id": physical_run_id,
                        "recorded_at": utc_timestamp(),
                    }
                if (
                    policy_binding.policy.idle_admission.enabled
                    and cooldown_note.get("result") == "unknown"
                ):
                    record_campaign_member_provenance(
                        campaign_provenance_path,
                        campaign_provenance,
                        info=info,
                        bundle_ids=[physical_run_id],
                        evaluations=[],
                        execution="blocked_before_invoke",
                        cooldown=cooldown_note,
                        cooldowns_by_bundle={physical_run_id: cooldown_note},
                    )
                    print(
                        f"failed {entry_id}: cooldown v2 failed closed before "
                        f"invoke: {cooldown_note.get('reason', 'unknown reference')}",
                        file=sys.stderr,
                    )
                    return 1
            dispatch_error: OSError | None = None
            try:
                completed = subprocess.run(
                    command, check=False, env=child_environment
                )
                exit_code: int | None = completed.returncode
            except OSError as exc:
                dispatch_error = exc
                exit_code = None

            bundle_path = _axi_attempt_bundle_path(
                runs_dir, manifest_id, entry_id, attempt_ordinal, info.run_id
            )
            finalized = bundle_path.is_dir() and (bundle_path / "summary_metrics.json").is_file()
            metadata: dict[str, Any] = {}
            if finalized:
                try:
                    parsed = json.loads((bundle_path / "metadata.json").read_bytes())
                    if isinstance(parsed, dict):
                        metadata = parsed
                except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                    metadata = {}
            batch = metadata.get("batch")
            admitted = (
                batch.get("admitted_request_count", 0)
                if isinstance(batch, dict)
                else 0
            )
            if not isinstance(admitted, int) or isinstance(admitted, bool) or admitted < 0:
                admitted = 0
            receipt_path = receipts_dir / f"{stem}.json"
            finalize_dispatch_receipt(
                receipt_path,
                identity,
                dispatch_started=True,
                transport_status=(
                    "ok" if exit_code == 0 and finalized else "failed"
                ),
                process_exit_code=exit_code,
                admitted_request_count=admitted,
                finalized_run_id=(info.run_id if finalized else None),
            )
            receipt_raw = receipt_path.read_bytes()
            receipt_sha = axi_sha256_bytes(receipt_raw)

            strict_problems = validate_bundle(bundle_path, strict=True) if finalized else []
            reason: str | None = None
            reason_sha: str | None = None
            eligible_for_analysis = True
            if not finalized:
                reason = "dispatch_failed_before_bundle_creation"
                reason_sha = receipt_sha
                eligible_for_analysis = False
            elif finalized and strict_problems:
                evidence = {
                    "schema_version": STRICT_EVIDENCE_SCHEMA_VERSION,
                    **identity_value,
                    "run_id": info.run_id,
                    "validated_bundle_sha256": _axi_bundle_digest(bundle_path),
                    "valid": False,
                    "validator_reason_codes": _axi_strict_reason_codes(
                        strict_problems
                    ),
                }
                evidence_raw = render_strict_validation_evidence(evidence)
                reason_sha = axi_sha256_bytes(evidence_raw)
                _write_immutable_bytes(strict_dir / f"{stem}__{reason_sha}.json", evidence_raw)
                reason = "strict_bundle_invalid"
                eligible_for_analysis = False

            ledger_row = {
                "schema_version": ATTEMPT_LEDGER_SCHEMA_VERSION,
                **identity_value,
                "run_id": info.run_id if finalized else None,
                "dispatch_receipt_sha256": receipt_sha,
                "technical_invalid_reason_code": reason,
                "reason_evidence_sha256": reason_sha,
                "eligible_for_analysis": eligible_for_analysis,
            }
            _write_immutable_bytes(
                rows_dir / f"{stem}.jsonl",
                render_attempt_ledger([ledger_row]),
            )
            by_entry[entry_id].append(ledger_row)
            if not eligible_for_analysis:
                if policy_binding is not None:
                    assert campaign_provenance_path is not None
                    assert campaign_provenance is not None
                    failed_evaluations: list[MemberEvaluation] = []
                    if finalized:
                        failed_evaluation = evaluate_member(
                            bundle_path,
                            info=info,
                            waivers={},
                            cooldown_evidence=cooldown_note,
                        )
                        failed_evaluations.append(
                            replace(failed_evaluation, bundle_id=physical_run_id)
                        )
                    record_campaign_member_provenance(
                        campaign_provenance_path,
                        campaign_provenance,
                        info=info,
                        bundle_ids=[physical_run_id],
                        evaluations=failed_evaluations,
                        execution="invoked",
                        cooldown=cooldown_note,
                        cooldowns_by_bundle=(
                            {physical_run_id: cooldown_note}
                            if cooldown_note is not None
                            else None
                        ),
                    )
                detail = str(dispatch_error) if dispatch_error is not None else reason
                print(f"failed {entry_id} attempt={attempt_ordinal}: {detail}", file=sys.stderr)
                return 1
            if policy_binding is not None:
                assert campaign_provenance_path is not None
                assert campaign_provenance is not None
                evaluation = evaluate_member(
                    bundle_path,
                    info=info,
                    waivers={},
                    cooldown_evidence=cooldown_note,
                )
                evaluation = replace(evaluation, bundle_id=physical_run_id)
                record_campaign_member_provenance(
                    campaign_provenance_path,
                    campaign_provenance,
                    info=info,
                    bundle_ids=[physical_run_id],
                    evaluations=[evaluation],
                    execution="invoked",
                    cooldown=cooldown_note,
                    cooldowns_by_bundle=(
                        {physical_run_id: cooldown_note}
                        if cooldown_note is not None
                        else None
                    ),
                )
                previous_physical_info = info
                previous_physical_evaluation = evaluation
                if (
                    policy_binding.policy.idle_admission.enabled
                    and frozen_cooldown_anchor is None
                ):
                    candidate_anchor = _first_eligible_cooldown_anchor(
                        [evaluation],
                        info,
                        policy_binding,
                        source_kind="first_admission_passing_baseline",
                    )
                    if candidate_anchor is not None:
                        frozen_cooldown_anchor = candidate_anchor
                        campaign_provenance["cooldown_anchor"] = candidate_anchor
                        write_campaign_provenance(
                            campaign_provenance_path, campaign_provenance
                        )
            print(f"ok {entry_id} attempt={attempt_ordinal}: bundle={bundle_path}")

        rows = _axi_load_rows(rows_dir)
        if any(not any(row["eligible_for_analysis"] for row in rows if row["entry_id"] == entry["entry_id"]) for entry in entries):
            print("error: AXI attempt ledger has an unresolved manifest entry", file=sys.stderr)
            return 1
        receipts = _axi_evidence_map(receipts_dir, "*.json")
        strict_evidence = _axi_evidence_map(strict_dir, "*.json")
        finalized_bundles = _axi_discover_finalized_bundles(runs_dir, manifest)
        selected = validate_attempt_ledger(
            rows,
            manifest,
            receipts=receipts,
            strict_evidence=strict_evidence,
            finalized_bundles=finalized_bundles,
        )
        ledger_raw = render_attempt_ledger(rows)
        ledger_path = evidence_root / "attempt_ledger.jsonl"
        if ledger_path.exists():
            if ledger_path.read_bytes() != ledger_raw:
                raise FileExistsError("immutable AXI attempt ledger differs")
        else:
            _write_immutable_bytes(ledger_path, ledger_raw)

        entry_by_id = {entry["entry_id"]: entry for entry in entries}
        for pair in manifest["pairs"]:
            bundles: dict[str, Path | None] = {}
            for arm, entry_key in (
                ("spec_off", "spec_off_entry_id"),
                ("spec_on", "spec_on_entry_id"),
            ):
                entry_id = pair[entry_key]
                row = selected[entry_id]
                entry = entry_by_id[entry_id]
                bundles[arm] = (
                    finalized_bundles[(
                        entry_id,
                        row["attempt_ordinal"],
                        row["run_id"],
                    )]
                    if row is not None and row["run_id"] is not None
                    else None
                )
            report = build_output_identity_report(
                manifest_id=manifest_id,
                pair_id=pair["pair_id"],
                spec_off_bundle=bundles["spec_off"],
                spec_on_bundle=bundles["spec_on"],
                strict_validator=validate_bundle,
            )
            report_path = reports_dir / f"{sanitize_id_component(pair['pair_id'])}.json"
            report_raw = render_output_identity_report(report)
            if report_path.exists():
                if report_path.read_bytes() != report_raw:
                    raise FileExistsError("immutable output identity report differs")
            else:
                _write_immutable_bytes(report_path, report_raw)
        print(f"AXI attempt ledger: {ledger_path} sha256={axi_sha256_bytes(ledger_raw)}")
        return 0
    finally:
        if lock_path is not None:
            lock_path.unlink(missing_ok=True)


def run_campaign(args: argparse.Namespace) -> int:
    assert args.config_dir is not None
    config_dir = Path(args.config_dir)
    runs_dir = Path(args.runs_dir)
    log_path = Path(args.log) if args.log else runs_dir / "campaign_log.jsonl"

    policy_binding = load_campaign_policy(args.campaign_policy)

    if args.max_failures < 1:
        raise ValueError("--max-failures must be >= 1")

    analysis_manifest = load_analysis_manifest(config_dir)
    if analysis_manifest is not None and analysis_manifest.is_axi_v2:
        order_entries = []
        order_warning = None
        configs = _axi_entry_config_paths(analysis_manifest)
    else:
        order_entries, order_warning = load_order_entries(config_dir)
        if order_warning is not None:
            print(order_warning, file=sys.stderr)
        configs = apply_order_manifest(discover_configs(config_dir), order_entries)
    order_by_config = order_entry_by_config(order_entries)
    print_config_file_list(configs)
    doctor_gate = config_warning_gate(
        configs,
        acknowledge=args.ack_config_warnings,
        mode="campaign",
    )
    doctor_gate.pop("inspection")
    preflight = {
        "schema_version": DOCTOR_SCHEMA_VERSION,
        "check": "config",
        "status": doctor_gate["status"],
        "summary": doctor_gate["summary"],
        "config_warning_acknowledgement": doctor_gate["details"]["acknowledgement"],
        "campaign_policy": policy_binding.to_metadata(),
    }
    for error in doctor_gate["details"]["errors"]:
        print(
            f"error: doctor config preflight failed for {error['config']}: {error['message']}",
            file=sys.stderr,
        )
    if doctor_gate["details"]["errors"]:
        return 2
    acknowledgement = preflight["config_warning_acknowledgement"]
    if acknowledgement["warning_count"]:
        disposition = "acknowledged" if acknowledgement["acknowledged"] else "unacknowledged"
        print(
            f"DOCTOR CONFIG PREFLIGHT: {acknowledgement['warning_count']} warning(s), {disposition}"
        )
    if doctor_gate["status"] == "fail":
        categories = {"usable": [], "waived": [], "failed": [], "missing": []}
        collection_reasons = ["doctor config warnings were not acknowledged"]
        readiness = claim_readiness_for(analysis_manifest, "invalid", [])
        if not args.dry_run:
            print_verdict("invalid", collection_reasons, categories, readiness)
            append_verdict(
                log_path,
                collection_verdict="invalid",
                collection_reasons=collection_reasons,
                categories=categories,
                claim_readiness=readiness,
                analysis_manifest=analysis_manifest,
                sampling_audit=sampling_audit_for(analysis_manifest),
                members=[],
                campaign_provenance_path=None,
                warning=order_warning,
                preflight=preflight,
            )
        return 1
    if analysis_manifest is not None and analysis_manifest.is_axi_v2:
        return run_axi_spec_campaign(
            args,
            analysis_manifest,
            runs_dir=runs_dir,
            policy_binding=policy_binding,
            log_path=log_path,
            preflight=preflight,
        )
    items = read_config_infos(configs)
    waivers = load_waivers(args.waivers)
    config_errors = [item for item in items if isinstance(item, ConfigError)]
    if config_errors:
        for item in config_errors:
            print(f"error: {item.message}", file=sys.stderr)
        return 2
    duplicate_error = duplicate_run_id_error(items)
    if duplicate_error is not None:
        print(f"error: {duplicate_error}", file=sys.stderr)
        return 2
    if args.shakedown_gate is not None:
        if args.backup is None:
            print("error: --shakedown-gate requires --backup", file=sys.stderr)
            return 2
        if len(items) != 1 or not isinstance(items[0], ConfigInfo) or items[0].repetitions != 1:
            print(
                "error: --shakedown-gate requires exactly one single-repetition config",
                file=sys.stderr,
            )
            return 2

    if analysis_manifest is not None and not analysis_manifest.valid and not args.dry_run:
        categories = {"usable": [], "waived": [], "failed": [], "missing": []}
        collection_reasons = ["analysis manifest validation failed before execution"]
        readiness = claim_readiness_for(analysis_manifest, "invalid", [])
        print_verdict("invalid", collection_reasons, categories, readiness)
        append_verdict(
            log_path,
            collection_verdict="invalid",
            collection_reasons=collection_reasons,
            categories=categories,
            claim_readiness=readiness,
            analysis_manifest=analysis_manifest,
            sampling_audit=sampling_audit_for(analysis_manifest),
            members=[],
            campaign_provenance_path=None,
            warning=order_warning,
            preflight=preflight,
        )
        return 1

    counts: Counter[str] = Counter()
    failures = 0
    lock_path: Path | None = None
    all_evaluations: list[MemberEvaluation] = []
    missing_members: list[str] = []
    previous_model_tag: str | None = None
    previous_physical_info: ConfigInfo | None = None
    previous_physical_evaluation: MemberEvaluation | None = None
    cooldown_by_bundle = prior_campaign_cooldown_evidence(
        runs_dir,
        analysis_manifest.manifest_id if analysis_manifest is not None else None,
    )
    frozen_cooldown_anchor = prior_campaign_cooldown_anchor(
        runs_dir,
        analysis_manifest.manifest_id if analysis_manifest is not None else None,
        policy_binding.sha256,
    )
    neg8_reference_expected = any(
        isinstance(item, ConfigInfo) and _is_neg8_reference_start(item)
        for item in items
    )
    campaign_provenance_path: Path | None = None
    campaign_provenance: dict[str, Any] | None = None

    print_quiet_machine_warning()
    if args.dry_run:
        print(
            "Campaign policy: "
            f"{policy_binding.policy.policy_id} sha256={policy_binding.sha256}"
        )
        print("Dry run: no commands will be invoked and no campaign log will be written.")
    else:
        try:
            lock_path = acquire_campaign_lock(runs_dir)
        except RuntimeError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        campaign_provenance_path, campaign_provenance = new_campaign_provenance(
            config_dir, runs_dir, analysis_manifest, policy_binding
        )
        campaign_provenance["cooldown_anchor"] = frozen_cooldown_anchor
        campaign_provenance["cooldown_anchor_strategy"] = (
            "neg8_reference_start_then_first_admission_passing"
            if neg8_reference_expected
            else "first_admission_passing"
        )
        write_campaign_provenance(campaign_provenance_path, campaign_provenance)
        try:
            environment_preflight = campaign_environment_preflight(
                policy_binding,
                arm_quiet_mode=args.arm_quiet_mode,
                arm_countdown_s=args.arm_countdown_s,
                override_path=args.environment_override,
            )
        except Exception as exc:  # noqa: BLE001 - preflight errors fail before member 1
            environment_error = {
                "status": "error",
                "reason": f"{type(exc).__name__}: {exc}",
            }
            campaign_provenance["environment_preflight"] = environment_error
            write_campaign_provenance(campaign_provenance_path, campaign_provenance)
            append_environment_preflight_verdict(
                log_path,
                analysis_manifest=analysis_manifest,
                campaign_provenance_path=campaign_provenance_path,
                preflight=preflight,
                environment_guard=environment_error,
                reason="environment preflight failed before member 1",
            )
            print(f"error: environment preflight failed: {exc}", file=sys.stderr)
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass
            return 2
        campaign_provenance["environment_preflight"] = environment_preflight
        write_campaign_provenance(campaign_provenance_path, campaign_provenance)
        preflight["environment_guard"] = environment_preflight
        if not environment_preflight["admitted"]:
            evaluation = environment_preflight["evaluation"]
            failed_findings = [
                finding
                for finding in evaluation["findings"]
                if finding["status"] != "pass"
            ]
            print(
                "ENVIRONMENT PREFLIGHT FAILED: "
                + "; ".join(
                    f"{row['field']}={row['actual']!r} ({row['status']})"
                    for row in failed_findings
                ),
                file=sys.stderr,
            )
            print(
                "override binding: "
                f"snapshot_sha256={evaluation['snapshot_sha256']} "
                f"findings_sha256={evaluation['findings_sha256']}",
                file=sys.stderr,
            )
            append_environment_preflight_verdict(
                log_path,
                analysis_manifest=analysis_manifest,
                campaign_provenance_path=campaign_provenance_path,
                preflight=preflight,
                environment_guard=environment_preflight,
                reason="environment preflight rejected before member 1",
            )
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass
            return 1

    child_environment = os.environ.copy()
    child_environment[CAMPAIGN_POLICY_PATH_ENV] = str(policy_binding.path)
    child_environment[CAMPAIGN_POLICY_SHA256_ENV] = policy_binding.sha256
    if campaign_provenance is not None:
        child_environment[CAMPAIGN_PREFLIGHT_JSON_ENV] = json.dumps(
            campaign_provenance["environment_preflight"],
            sort_keys=True,
            separators=(",", ":"),
        )

    try:
        for item in items:
            if isinstance(item, ConfigError):
                if args.dry_run:
                    counts["dry_run"] += 1
                    print(f"dry_run {item.path}: config error: {item.message}", file=sys.stderr)
                    continue
                failures += 1
                print(f"error: {item.message}", file=sys.stderr)
                append_log(
                    log_path,
                    log_row(
                        config_path=item.path,
                        run_id=item.run_id,
                        status="config_error",
                        exit_code=None,
                        duration_s=None,
                        extra={"error": item.message},
                    ),
                )
                counts["config_error"] += 1
                if failures >= args.max_failures:
                    break
                continue

            info = item
            config_path = info.path
            order_entry = order_by_config.get(config_path.name)
            model_boundary = (
                order_entry is not None
                and order_entry.model_tag is not None
                and order_entry.model_tag != previous_model_tag
            )
            if order_entry is not None and order_entry.model_tag is not None:
                previous_model_tag = order_entry.model_tag
            order_extra: dict[str, Any] = {}
            if order_entry is not None:
                order_extra = {
                    "run_index": order_entry.index,
                    "executed_order": order_entry.to_log(),
                    "model_load_boundary": model_boundary,
                }
            elif order_warning is not None:
                order_extra = {"block_order_warning": order_warning}
            state = existing_state(info, runs_dir)
            command = command_for(
                config_path,
                runs_dir,
                args.cli_cmd,
                frozen_cooldown_anchor=(
                    frozen_cooldown_anchor if info.repetitions > 1 else None
                ),
            )

            if args.dry_run:
                counts["dry_run"] += 1
                print(f"dry_run {info.run_id}: {state.action}: {shell_quote(command)}")
                continue

            if state.action == "skip complete":
                evaluations = evaluate_members(
                    info, runs_dir, waivers, cooldown_by_bundle
                )
                all_evaluations.extend(evaluations)
                failed = [evaluation for evaluation in evaluations if evaluation.failed]
                if failed:
                    failures += 1
                    status = "failed"
                    details = "; ".join(
                        evaluation_failure_detail(evaluation) for evaluation in failed
                    )
                    print(
                        f"failed {info.run_id}: existing bundle(s) are not skippable: "
                        f"{details}; inspect or move those bundle(s), or provide an "
                        "explicit campaign waiver",
                        file=sys.stderr,
                    )
                else:
                    status = (
                        "waived"
                        if any(evaluation.waived for evaluation in evaluations)
                        else "skipped"
                    )
                if (
                    status == "skipped"
                    and args.shakedown_gate == "production_uncertainty_v1"
                ):
                    bundle = evaluations[0].bundle_path
                    try:
                        gate_record = execute_production_uncertainty_gate(
                            bundle, runs_dir, args.backup
                        )
                    except ShakedownGateError as exc:
                        failures += 1
                        status = "failed"
                        gate_record = failed_shakedown_record(
                            args.shakedown_gate, exc
                        )
                        print(
                            f"SHAKEDOWN_GATE_FAILED[{exc.code}] "
                            f"bundle={exc.bundle_id} detail={exc.detail}",
                            file=sys.stderr,
                        )
                    append_log(log_path, gate_record)
                exit_code = None
                duration_s = None
                if status != "failed" and state.members_total is None:
                    print(f"skipped {info.run_id}: complete bundle already exists")
                elif status != "failed":
                    print(
                        f"skipped {info.run_id}: complete experiment already exists "
                        f"({state.members_succeeded}/{state.members_total} members succeeded)"
                    )
                    waived = [
                        evaluation.bundle_id
                        for evaluation in evaluations
                        if evaluation.waived
                    ]
                    if waived:
                        print(
                            f"note: skipped experiment {info.run_id} has waived member(s): "
                            f"{', '.join(waived)}",
                            file=sys.stderr,
                        )
                extra = {
                    **(skipped_log_extra(state) or {}),
                    **order_extra,
                    "members": [evaluation.to_log() for evaluation in evaluations],
                    "campaign_provenance_manifest": str(campaign_provenance_path),
                }
                assert campaign_provenance_path is not None
                assert campaign_provenance is not None
                record_campaign_member_provenance(
                    campaign_provenance_path,
                    campaign_provenance,
                    info=info,
                    bundle_ids=[evaluation.bundle_id for evaluation in evaluations],
                    evaluations=evaluations,
                    execution="existing",
                    cooldown=(
                        evaluations[0].preceding_campaign_cooldown
                        if evaluations
                        else None
                    ),
                )
                append_log(
                    log_path,
                    log_row(
                        config_path=config_path,
                        run_id=info.run_id,
                        status=status,
                        exit_code=exit_code,
                        duration_s=duration_s,
                        extra=extra,
                    ),
                )
                counts[status] += 1
                if failures >= args.max_failures:
                    break
                continue

            if state.action == "incomplete existing":
                status = "incomplete_existing"
                exit_code = None
                duration_s = None
                failures += 1
                expected_members = expected_member_dirs(info, runs_dir)
                existing_evaluations = [
                    evaluate_member(
                        member,
                        info=info,
                        waivers=waivers,
                        cooldown_evidence=cooldown_by_bundle.get(member.name),
                    )
                    for member in expected_members
                    if member.exists()
                ]
                all_evaluations.extend(existing_evaluations)
                missing_members.extend(
                    member.name for member in expected_members if not member.exists()
                )
                inspect = ", ".join(state.inspect_members) if state.inspect_members else info.run_id
                if state.malformed_summaries:
                    detail = "malformed summary_metrics.json: " + "; ".join(state.malformed_summaries)
                elif info.repetitions == 1:
                    detail = f"{inspect} lacks summary_metrics.json"
                else:
                    detail = f"partial experiment members exist: {inspect}"
                print(
                    f"incomplete_existing {info.run_id}: {detail}; inspect or move those "
                    "bundle(s) before retrying",
                    file=sys.stderr,
                )
                extra = {
                    **order_extra,
                    "members": [
                        evaluation.to_log() for evaluation in existing_evaluations
                    ],
                    "campaign_provenance_manifest": str(campaign_provenance_path),
                }
                assert campaign_provenance_path is not None
                assert campaign_provenance is not None
                record_campaign_member_provenance(
                    campaign_provenance_path,
                    campaign_provenance,
                    info=info,
                    bundle_ids=[
                        evaluation.bundle_id for evaluation in existing_evaluations
                    ],
                    evaluations=existing_evaluations,
                    execution="existing",
                    cooldown=None,
                )
                append_log(
                    log_path,
                    log_row(
                        config_path=config_path,
                        run_id=info.run_id,
                        status=status,
                        exit_code=exit_code,
                        duration_s=duration_s,
                        extra=extra,
                    ),
                )
                counts[status] += 1
                if failures >= args.max_failures:
                    break
                continue

            assert campaign_provenance_path is not None
            assert campaign_provenance is not None
            physical_bundle_dirs = expected_member_dirs(info, runs_dir)
            first_physical_bundle_id = physical_bundle_dirs[0].name
            following_physical_info = replace(
                info,
                run_id=first_physical_bundle_id,
                raw_run_id=first_physical_bundle_id,
                repetitions=1,
            )
            if campaign_provenance.get("first_physical_run_id") is None:
                cooldown_note = {
                    **_cooldown_policy_decision_surface(
                        policy_binding.policy.cooldown
                    ),
                    "result": "first_run_exempt",
                    "session_id": campaign_provenance["session_id"],
                    "following_run_id": first_physical_bundle_id,
                    "recorded_at": utc_timestamp(),
                }
                campaign_provenance["first_physical_run_id"] = first_physical_bundle_id
                write_campaign_provenance(campaign_provenance_path, campaign_provenance)
            elif previous_physical_info is not None and previous_physical_evaluation is not None:
                cooldown_note = campaign_cooldown_before_member(
                    previous_info=previous_physical_info,
                    previous_evaluation=previous_physical_evaluation,
                    following_info=following_physical_info,
                    provenance_path=campaign_provenance_path,
                    session_id=campaign_provenance["session_id"],
                    policy_binding=policy_binding,
                    frozen_anchor=frozen_cooldown_anchor,
                )
            else:
                cooldown_note = {
                    "result": "unknown",
                    "reason": "previous physical member evaluation unavailable",
                    "session_id": campaign_provenance["session_id"],
                    "following_run_id": first_physical_bundle_id,
                    "recorded_at": utc_timestamp(),
                }
            cooldown_by_bundle[first_physical_bundle_id] = cooldown_note

            if (
                policy_binding.policy.idle_admission.enabled
                and cooldown_note.get("result") == "unknown"
            ):
                blocked_bundle_ids = [path.name for path in physical_bundle_dirs]
                missing_members.extend(blocked_bundle_ids)
                failures += 1
                counts["failed"] += 1
                print(
                    f"failed {info.run_id}: cooldown v2 failed closed before invoke: "
                    f"{cooldown_note.get('reason', 'unknown reference')}",
                    file=sys.stderr,
                )
                record_campaign_member_provenance(
                    campaign_provenance_path,
                    campaign_provenance,
                    info=info,
                    bundle_ids=blocked_bundle_ids,
                    evaluations=[],
                    execution="blocked_before_invoke",
                    cooldown=cooldown_note,
                )
                append_log(
                    log_path,
                    log_row(
                        config_path=config_path,
                        run_id=info.run_id,
                        status="failed",
                        exit_code=None,
                        duration_s=None,
                        extra={
                            **order_extra,
                            "preceding_campaign_cooldown": cooldown_note,
                            "blocked_before_invoke": True,
                            "campaign_provenance_manifest": str(
                                campaign_provenance_path
                            ),
                        },
                    ),
                )
                if failures >= args.max_failures:
                    break
                continue

            start = time.monotonic()
            result = subprocess.run(command, check=False, env=child_environment)
            duration_s = time.monotonic() - start
            exit_code = result.returncode
            physical_cooldowns = _physical_cooldown_evidence_for_config(
                info,
                runs_dir,
                cooldown_note,
                campaign_provenance_path,
                policy_binding.policy.cooldown,
            )
            cooldown_by_bundle.update(physical_cooldowns)
            evaluations = evaluate_members(
                info, runs_dir, waivers, cooldown_by_bundle
            )
            all_evaluations.extend(evaluations)
            if evaluations:
                previous_physical_info = info
                previous_physical_evaluation = evaluations[-1]
                if (
                    policy_binding.policy.idle_admission.enabled
                    and frozen_cooldown_anchor is None
                    and (
                        not neg8_reference_expected
                        or _is_neg8_reference_start(info)
                    )
                ):
                    source_kind = (
                        "neg8_reference_start"
                        if _is_neg8_reference_start(info)
                        else "first_admission_passing_baseline"
                    )
                    candidate_anchor = _first_eligible_cooldown_anchor(
                        evaluations,
                        info,
                        policy_binding,
                        source_kind=source_kind,
                    )
                    if candidate_anchor is not None:
                        frozen_cooldown_anchor = candidate_anchor
                        campaign_provenance["cooldown_anchor"] = candidate_anchor
                        write_campaign_provenance(
                            campaign_provenance_path, campaign_provenance
                        )
            missing_after_run = [
                evaluation.bundle_id
                for evaluation in evaluations
                if not evaluation.bundle_path.exists()
            ]
            missing_members.extend(missing_after_run)
            failed_members = [evaluation for evaluation in evaluations if evaluation.failed]
            if exit_code == 0 and not failed_members and not missing_after_run:
                status = (
                    "waived"
                    if any(evaluation.waived for evaluation in evaluations)
                    else "ok"
                )
            else:
                status = "failed"
            shakedown_record: dict[str, Any] | None = None
            if status == "ok" and args.shakedown_gate == "production_uncertainty_v1":
                bundle = evaluations[0].bundle_path
                try:
                    shakedown_record = execute_production_uncertainty_gate(
                        bundle, runs_dir, args.backup
                    )
                except ShakedownGateError as exc:
                    status = "failed"
                    shakedown_record = failed_shakedown_record(
                        args.shakedown_gate, exc
                    )
                    print(
                        f"SHAKEDOWN_GATE_FAILED[{exc.code}] bundle={exc.bundle_id} "
                        f"detail={exc.detail}",
                        file=sys.stderr,
                    )
                append_log(log_path, shakedown_record)
            if status == "failed":
                failures += 1
                if exit_code == 0:
                    details = "; ".join(
                        evaluation_failure_detail(evaluation)
                        for evaluation in failed_members
                    )
                    if missing_after_run:
                        details = (details + "; " if details else "") + (
                            "missing: " + ", ".join(missing_after_run)
                        )
                    print(
                        f"failed {info.run_id}: exit=0 but strict campaign validation "
                        f"did not pass: {details}",
                        file=sys.stderr,
                    )
            extra = {
                **order_extra,
                "members": [evaluation.to_log() for evaluation in evaluations],
                "preceding_campaign_cooldown": cooldown_note,
                "campaign_provenance_manifest": str(campaign_provenance_path),
            }
            record_campaign_member_provenance(
                campaign_provenance_path,
                campaign_provenance,
                info=info,
                bundle_ids=[evaluation.bundle_id for evaluation in evaluations],
                evaluations=evaluations,
                execution="invoked",
                cooldown=cooldown_note,
                cooldowns_by_bundle=physical_cooldowns,
            )
            append_log(
                log_path,
                log_row(
                    config_path=config_path,
                    run_id=info.run_id,
                    status=status,
                    exit_code=exit_code,
                    duration_s=duration_s,
                    extra=extra,
                ),
            )
            counts[status] += 1
            print(f"{status} {info.run_id}: exit={exit_code} duration_s={duration_s:.3f}")

            if (
                status == "ok"
                and args.backup is not None
                and args.shakedown_gate is None
            ):
                backup_runs(runs_dir, backup_script_path(args.backup))

            if failures >= args.max_failures:
                break
    finally:
        if lock_path is not None:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass

    print("Summary:")
    for status in STATUSES:
        if counts[status]:
            print(f"  {status}: {counts[status]}")
    if args.dry_run:
        return 0
    categories = classify_campaign_members(all_evaluations, missing_members)
    collection_verdict, collection_reasons = collection_verdict_for(categories)
    claim_readiness = claim_readiness_for(
        analysis_manifest, collection_verdict, all_evaluations
    )
    sampling_audit = sampling_audit_for(analysis_manifest)
    print_verdict(
        collection_verdict,
        collection_reasons,
        categories,
        claim_readiness,
    )
    if not args.dry_run:
        append_verdict(
            log_path,
            collection_verdict=collection_verdict,
            collection_reasons=collection_reasons,
            categories=categories,
            claim_readiness=claim_readiness,
            analysis_manifest=analysis_manifest,
            sampling_audit=sampling_audit,
            members=all_evaluations,
            campaign_provenance_path=campaign_provenance_path,
            warning=order_warning,
            preflight=preflight,
        )
    return 1 if failures or collection_verdict in {"blocked", "invalid"} else 0


def run_prompt_hash_check(args: argparse.Namespace) -> int:
    bundle_text, sidecar_text = args.check_prompt_hashes
    result = check_prompt_hashes_for_bundle(Path(bundle_text), Path(sidecar_text))
    print(json.dumps(result.to_log(), sort_keys=True))
    if result.status in {"matched", "not_applicable"}:
        return 0
    if result.status == "mismatch":
        return 1
    return 2


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.check_prompt_hashes is not None:
            return run_prompt_hash_check(args)
        return run_campaign(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
