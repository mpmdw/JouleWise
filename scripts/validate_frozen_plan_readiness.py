#!/usr/bin/env python3
"""Fail-closed validator for a D-117 frozen-plan readiness record.

The validator consumes three operator-selected locations: a plan directory,
the primary evidence root, and the repository.  The plan directory contains
``readiness-record.json``.  That record binds the frozen plan bytes and their
sidecar, the arm-time acceptance/ledger/waiver attachments, launch commands,
and the unclaimed two-slot bracket identifiers.  The frozen plan declares its
stage manifests and the two fresh physical roots.

Exit status 0 is reserved for an overall PASS.  A failed check, malformed
input, I/O error, or usage error emits one JSON REFUSE receipt and exits 2.
Every validation check is attempted independently so the operator receives a
complete, named refusal set; a check never fails open because another check
already refused.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any, Callable, Iterable, Mapping, Sequence


RECEIPT_SCHEMA = "joulewise.frozen_plan_readiness_receipt.v1"
READINESS_SCHEMA = "joulewise.frozen_plan_readiness.v1"
LEDGER_SCHEMA = "joulewise.calibration_observation_ledger.v1"
REFUSAL_EXIT = 2
HEX_RE = re.compile(r"^[0-9a-f]{64}$")
SIDECAR_RE = re.compile(r"^([0-9a-f]{64})  ([^\r\n]+)\n$")
IDENTITY_EPOCH_FIELDS = frozenset(
    {
        "os_build",
        "hardware_model",
        "power_policy",
        "sampling_interval_ms",
        "estimator_revision",
        "pulse_protocol_id",
    }
)
PATH_OPTIONS = frozenset(
    {
        "--backup-destination",
        "--bound-root",
        "--config",
        "--config-dir",
        "--evidence-root",
        "--manifest",
        "--output",
        "--plan",
        "--plan-dir",
        "--runs-dir",
        "--waivers",
    }
)
FORBIDDEN_LAUNCH_OPTIONS = frozenset({"--environment-override", "--waivers"})


class CliError(Exception):
    """Argument error that must still produce a refusal receipt."""


class ReceiptArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliError(message)


@dataclass(frozen=True)
class CheckResult:
    check: str
    result: str
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "check": self.check,
            "result": self.result,
            "reasons": list(self.reasons),
        }


@dataclass
class Context:
    plan_dir: Path
    evidence_root: Path
    repo: Path
    readiness_path: Path
    readiness: Mapping[str, Any] | None
    plan: Mapping[str, Any] | None = None
    ledger_rows: tuple[Mapping[str, Any], ...] = ()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and HEX_RE.fullmatch(value) is not None


def _mapping(value: object) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None


def _json_file(path: Path) -> tuple[Mapping[str, Any] | list[Any] | None, bytes | None]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None, None
    if isinstance(value, (Mapping, list)):
        return value, raw
    return None, raw


def _safe_relative(base: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        return None
    try:
        resolved = (base / Path(*pure.parts)).resolve()
        resolved.relative_to(base.resolve())
    except (OSError, ValueError):
        return None
    return resolved


def _absolute_path(value: object) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        return None
    try:
        return path.resolve()
    except OSError:
        return None


def _result(check: str, reasons: Iterable[str]) -> CheckResult:
    unique = tuple(sorted(set(reasons)))
    return CheckResult(check, "REFUSE" if unique else "PASS", unique)


def _record_path(ctx: Context, field: str) -> Path | None:
    if ctx.readiness is None:
        return None
    return _safe_relative(ctx.repo, ctx.readiness.get(field))


def check_plan_integrity(ctx: Context) -> CheckResult:
    reasons: set[str] = set()
    record = ctx.readiness
    if record is None:
        return _result("plan_integrity", {"readiness_record_unreadable"})
    if record.get("schema_version") != READINESS_SCHEMA:
        reasons.add("readiness_schema_invalid")
    if record.get("review_status") != "reviewed":
        reasons.add("readiness_record_not_reviewed")

    plan_path = _safe_relative(ctx.plan_dir, record.get("plan_path"))
    sidecar_path = _safe_relative(ctx.plan_dir, record.get("sidecar_path"))
    if plan_path is None or sidecar_path is None:
        reasons.add("plan_path_invalid")
        return _result("plan_integrity", reasons)
    try:
        plan_raw = plan_path.read_bytes()
        sidecar_raw = sidecar_path.read_bytes()
        plan_value = json.loads(plan_raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        reasons.add("plan_or_sidecar_unreadable")
        return _result("plan_integrity", reasons)
    if not isinstance(plan_value, Mapping):
        reasons.add("plan_malformed")
        return _result("plan_integrity", reasons)
    ctx.plan = plan_value

    plan_digest = _sha256(plan_raw)
    sidecar_digest = _sha256(sidecar_raw)
    if not _is_sha256(record.get("plan_sha256")) or record.get("plan_sha256") != plan_digest:
        reasons.add("plan_sha256_mismatch")
    if not _is_sha256(record.get("sidecar_sha256")) or record.get("sidecar_sha256") != sidecar_digest:
        reasons.add("plan_sidecar_sha256_mismatch")
    try:
        sidecar_text = sidecar_raw.decode("utf-8")
    except UnicodeDecodeError:
        sidecar_text = ""
    match = SIDECAR_RE.fullmatch(sidecar_text)
    if match is None:
        reasons.add("plan_sidecar_malformed")
    else:
        target = _safe_relative(ctx.plan_dir, match.group(2))
        if match.group(1) != plan_digest or target != plan_path:
            reasons.add("plan_sidecar_binding_mismatch")
    if not isinstance(record.get("plan_id"), str) or not record.get("plan_id"):
        reasons.add("plan_id_invalid")
    if plan_value.get("plan_id") != record.get("plan_id"):
        reasons.add("plan_id_mismatch")
    if plan_value.get("freeze_status") != "frozen_before_measurement":
        reasons.add("plan_not_frozen")
    return _result("plan_integrity", reasons)


def _load_plan_if_needed(ctx: Context) -> None:
    if ctx.plan is not None or ctx.readiness is None:
        return
    path = _safe_relative(ctx.plan_dir, ctx.readiness.get("plan_path"))
    if path is None:
        return
    value, _raw = _json_file(path)
    if isinstance(value, Mapping):
        ctx.plan = value


def check_stage_manifests(ctx: Context) -> CheckResult:
    reasons: set[str] = set()
    _load_plan_if_needed(ctx)
    if ctx.plan is None:
        return _result("stage_manifests", {"plan_unavailable_for_stage_check"})
    stages = ctx.plan.get("stage_manifests")
    if not isinstance(stages, list) or not stages:
        return _result("stage_manifests", {"stage_manifest_declarations_missing"})
    declared_ids = [
        stage.get("stage_manifest_id") if isinstance(stage, Mapping) else None
        for stage in stages
    ]
    seen_ids: set[str] = set()
    seen_paths: set[Path] = set()
    for stage_index, stage in enumerate(stages):
        if not isinstance(stage, Mapping):
            reasons.add("stage_manifest_declaration_malformed")
            continue
        stage_id = stage.get("stage_manifest_id")
        expected = stage.get("expected_member_count")
        path = _safe_relative(ctx.plan_dir, stage.get("stage_manifest_path"))
        digest = stage.get("stage_manifest_sha256")
        if not isinstance(stage_id, str) or not stage_id or stage_id in seen_ids:
            reasons.add("stage_manifest_id_invalid")
        else:
            seen_ids.add(stage_id)
        expected_predecessor = declared_ids[stage_index - 1] if stage_index else None
        expected_successor = (
            declared_ids[stage_index + 1]
            if stage_index + 1 < len(declared_ids)
            else None
        )
        if (
            stage.get("predecessor") != expected_predecessor
            or stage.get("successor") != expected_successor
        ):
            reasons.add("stage_manifest_chain_mismatch")
        if path is None or path in seen_paths:
            reasons.add("stage_manifest_path_invalid")
            continue
        seen_paths.add(path)
        if isinstance(expected, bool) or not isinstance(expected, int) or expected < 0:
            reasons.add("stage_expected_member_count_invalid")
        value, raw = _json_file(path)
        if not isinstance(value, Mapping) or raw is None:
            reasons.add("stage_manifest_unreadable")
            continue
        if not _is_sha256(digest) or _sha256(raw) != digest:
            reasons.add("stage_manifest_sha256_mismatch")
        if value.get("manifest_id") != stage_id:
            reasons.add("stage_manifest_id_mismatch")
        if value.get("plan_id") != ctx.plan.get("plan_id"):
            reasons.add("stage_manifest_plan_id_mismatch")
        members = value.get("members")
        if not isinstance(members, list):
            reasons.add("stage_members_missing")
            continue
        if len(members) != expected or value.get("expected_member_count") != expected:
            reasons.add("stage_member_count_mismatch")
        member_ids: set[str] = set()
        config_paths: set[Path] = set()
        for member in members:
            if not isinstance(member, Mapping):
                reasons.add("stage_member_malformed")
                continue
            member_id = member.get("member_id")
            config_path = _safe_relative(ctx.plan_dir, member.get("config_path"))
            config_sha = member.get("config_sha256")
            if not isinstance(member_id, str) or not member_id or member_id in member_ids:
                reasons.add("stage_member_id_invalid")
            else:
                member_ids.add(member_id)
            if config_path is None or config_path in config_paths:
                reasons.add("stage_member_config_path_invalid")
                continue
            config_paths.add(config_path)
            try:
                config_raw = config_path.read_bytes()
            except OSError:
                reasons.add("stage_member_config_missing")
                continue
            if not _is_sha256(config_sha) or _sha256(config_raw) != config_sha:
                reasons.add("stage_member_config_sha256_mismatch")
    return _result("stage_manifests", reasons)


def _declared_roots(ctx: Context) -> tuple[Path, ...] | None:
    _load_plan_if_needed(ctx)
    if ctx.plan is None:
        return None
    evidence = _absolute_path(ctx.plan.get("expected_fresh_physical_path"))
    bound = _absolute_path(ctx.plan.get("expected_fresh_bound_physical_path"))
    evidence_root_id = ctx.plan.get("evidence_root_id")
    if (
        not isinstance(evidence_root_id, str)
        or not evidence_root_id
        or evidence is None
        or bound is None
        or evidence == bound
    ):
        return None
    return evidence, bound


def check_fresh_physical_roots(ctx: Context) -> CheckResult:
    roots = _declared_roots(ctx)
    if roots is None:
        return _result("fresh_physical_roots", {"physical_root_declarations_invalid"})
    reasons: set[str] = set()
    if ctx.evidence_root.resolve() != roots[0]:
        reasons.add("evidence_root_argument_mismatch")
    for root in roots:
        try:
            if not root.is_dir():
                reasons.add("physical_root_missing_or_not_directory")
            elif any(root.iterdir()):
                reasons.add("physical_root_not_empty")
        except OSError:
            reasons.add("physical_root_unreadable")
    return _result("fresh_physical_roots", reasons)


def _committed_bytes(repo: Path, path: Path) -> bytes | None:
    try:
        relative = path.resolve().relative_to(repo.resolve()).as_posix()
        completed = subprocess.run(
            ["git", "show", f"HEAD:{relative}"],
            cwd=repo,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, ValueError, subprocess.CalledProcessError):
        return None
    return completed.stdout


def _load_ledger(path: Path) -> tuple[tuple[Mapping[str, Any], ...], set[str]]:
    reasons: set[str] = set()
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return (), {"physical_ledger_missing"}
    except OSError:
        return (), {"physical_ledger_unreadable"}
    if raw and not raw.endswith(b"\n"):
        reasons.add("physical_ledger_malformed")
    rows: list[Mapping[str, Any]] = []
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return (), {"physical_ledger_malformed"}
    for sequence, line in enumerate(text.splitlines(), start=1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            reasons.add("physical_ledger_malformed")
            continue
        if not isinstance(value, Mapping):
            reasons.add("physical_ledger_malformed")
            continue
        if value.get("sequence") != sequence or not _is_sha256(value.get("receipt_digest")):
            reasons.add("physical_ledger_malformed")
        rows.append(value)
    return tuple(rows), reasons


def check_ledger_head(ctx: Context) -> CheckResult:
    reasons: set[str] = set()
    ledger_path = _record_path(ctx, "physical_ledger_path")
    pin_path = _record_path(ctx, "committed_ledger_head_pin_path")
    if ledger_path is None or pin_path is None:
        return _result("ledger_head", {"ledger_paths_invalid"})
    pin_value, pin_raw = _json_file(pin_path)
    if not isinstance(pin_value, Mapping) or pin_raw is None:
        return _result("ledger_head", {"committed_ledger_head_pin_unreadable"})
    if _committed_bytes(ctx.repo, pin_path) != pin_raw:
        reasons.add("ledger_head_pin_not_committed")
    pin_sequence = pin_value.get("sequence")
    pin_digest = pin_value.get("head_digest")
    if (
        pin_value.get("ledger_schema") != LEDGER_SCHEMA
        or isinstance(pin_sequence, bool)
        or not isinstance(pin_sequence, int)
        or pin_sequence < 0
        or not _is_sha256(pin_digest)
        or (pin_sequence == 0 and pin_digest != "0" * 64)
    ):
        reasons.add("committed_ledger_head_pin_malformed")
    rows, ledger_reasons = _load_ledger(ledger_path)
    ctx.ledger_rows = rows
    reasons.update(ledger_reasons)
    physical_sequence = len(rows)
    physical_digest = rows[-1].get("receipt_digest") if rows else "0" * 64
    if (physical_sequence, physical_digest) != (pin_sequence, pin_digest):
        reasons.add("ledger_physical_head_pin_mismatch")
    return _result("ledger_head", reasons)


def check_acceptance_artifact(ctx: Context) -> CheckResult:
    reasons: set[str] = set()
    record = ctx.readiness
    if record is None:
        return _result("acceptance_artifact", {"readiness_record_unreadable"})
    path = _record_path(ctx, "acceptance_artifact_path")
    value, raw = _json_file(path) if path is not None else (None, None)
    if not isinstance(value, Mapping) or raw is None:
        return _result("acceptance_artifact", {"acceptance_artifact_unreadable"})
    expected_sha = record.get("acceptance_artifact_sha256")
    if not _is_sha256(expected_sha) or _sha256(raw) != expected_sha:
        reasons.add("acceptance_artifact_sha256_mismatch")
    if record.get("acceptance_artifact_role") != "issued" or value.get("artifact_role") != "issued":
        reasons.add("acceptance_artifact_not_issued")
    epoch = record.get("identity_epoch")
    if (
        not isinstance(epoch, Mapping)
        or set(epoch) != IDENTITY_EPOCH_FIELDS
        or any(item in (None, "") for item in epoch.values())
        or value.get("identity_epoch") != epoch
    ):
        reasons.add("acceptance_identity_epoch_mismatch")
    return _result("acceptance_artifact", reasons)


def check_waiver_set(ctx: Context) -> CheckResult:
    path = _record_path(ctx, "waiver_set_path")
    value, raw = _json_file(path) if path is not None else (None, None)
    if raw is None:
        return _result("waiver_set", {"waiver_set_unreadable"})
    if value != []:
        return _result("waiver_set", {"waiver_set_not_empty"})
    return _result("waiver_set", ())


def _path_option(option: str) -> bool:
    return option in PATH_OPTIONS or option.endswith(("-dir", "-path", "-root"))


def check_launch_command_paths(ctx: Context) -> CheckResult:
    record = ctx.readiness
    if record is None:
        return _result("launch_command_paths", {"readiness_record_unreadable"})
    commands = record.get("launch_commands")
    if not isinstance(commands, list) or not commands:
        return _result("launch_command_paths", {"launch_commands_missing"})
    reasons: set[str] = set()
    for command in commands:
        argv = command.get("argv") if isinstance(command, Mapping) else None
        if not isinstance(argv, list) or not argv or not all(isinstance(arg, str) and arg for arg in argv):
            reasons.add("launch_command_malformed")
            continue
        saw_runs_dir = False
        index = 0
        while index < len(argv):
            token = argv[index]
            if token.startswith("--") and "=" in token:
                option, value = token.split("=", 1)
                if option in FORBIDDEN_LAUNCH_OPTIONS:
                    reasons.add("launch_command_forbidden_override")
                if _path_option(option):
                    saw_runs_dir = saw_runs_dir or option == "--runs-dir"
                    if not os.path.isabs(value):
                        reasons.add("launch_command_path_not_absolute")
                index += 1
                continue
            if token in FORBIDDEN_LAUNCH_OPTIONS:
                reasons.add("launch_command_forbidden_override")
            if token.startswith("--") and _path_option(token):
                saw_runs_dir = saw_runs_dir or token == "--runs-dir"
                if index + 1 >= len(argv) or not os.path.isabs(argv[index + 1]):
                    reasons.add("launch_command_path_not_absolute")
                index += 2
                continue
            index += 1
        if not saw_runs_dir:
            reasons.add("launch_command_runs_dir_missing")
    return _result("launch_command_paths", reasons)


def check_campaign_lock(ctx: Context) -> CheckResult:
    roots = _declared_roots(ctx)
    if roots is None:
        return _result("campaign_lock", {"physical_root_declarations_invalid"})
    reasons = {
        "campaign_lock_present"
        for root in roots
        if os.path.lexists(root / "campaign.lock")
    }
    return _result("campaign_lock", reasons)


def _all_strings(value: object) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            if isinstance(key, str):
                yield key
            yield from _all_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _all_strings(child)


def check_bracket_session_identifiers(ctx: Context) -> CheckResult:
    record = ctx.readiness
    if record is None:
        return _result("bracket_session_identifiers", {"readiness_record_unreadable"})
    identifiers = record.get("bracket_session_identifiers")
    required = ("session_id", "pre_attempt_id", "post_attempt_id")
    if not isinstance(identifiers, Mapping):
        return _result("bracket_session_identifiers", {"bracket_session_identifiers_invalid"})
    values = [identifiers.get(field) for field in required]
    reasons: set[str] = set()
    if not all(isinstance(value, str) and value for value in values) or len(set(values)) != len(values):
        reasons.add("bracket_session_identifiers_invalid")
    ledger_path = _record_path(ctx, "physical_ledger_path")
    if not ctx.ledger_rows and ledger_path is not None:
        ctx.ledger_rows, load_reasons = _load_ledger(ledger_path)
        if load_reasons:
            reasons.add("bracket_claim_check_error")
    claimed = set(_all_strings(list(ctx.ledger_rows)))
    if any(isinstance(value, str) and value in claimed for value in values):
        reasons.add("bracket_session_identifier_claimed")
    return _result("bracket_session_identifiers", reasons)


CHECKS: tuple[Callable[[Context], CheckResult], ...] = (
    check_plan_integrity,
    check_stage_manifests,
    check_fresh_physical_roots,
    check_ledger_head,
    check_acceptance_artifact,
    check_waiver_set,
    check_launch_command_paths,
    check_campaign_lock,
    check_bracket_session_identifiers,
)


def validate(plan_dir: Path, evidence_root: Path, repo: Path) -> dict[str, Any]:
    plan_dir = plan_dir.resolve()
    evidence_root = evidence_root.resolve()
    repo = repo.resolve()
    readiness_path = plan_dir / "readiness-record.json"
    value, _raw = _json_file(readiness_path)
    readiness = value if isinstance(value, Mapping) else None
    ctx = Context(plan_dir, evidence_root, repo, readiness_path, readiness)
    checks: list[CheckResult] = []
    for checker in CHECKS:
        try:
            checks.append(checker(ctx))
        except Exception:  # fail closed at each independent check boundary
            checks.append(_result(checker.__name__.removeprefix("check_"), {"check_error"}))
    overall = "PASS" if all(check.result == "PASS" for check in checks) else "REFUSE"
    return {
        "schema_version": RECEIPT_SCHEMA,
        "result": overall,
        "inputs": {
            "plan_directory": str(plan_dir),
            "evidence_root": str(evidence_root),
            "repository": str(repo),
        },
        "checks": [check.as_dict() for check in checks],
        "refusal_reasons": sorted(
            {reason for check in checks for reason in check.reasons}
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = ReceiptArgumentParser(
        description=(
            "Validate D-117 frozen-plan readiness. PASS is an arm-time input, "
            "not science launch authorization."
        )
    )
    parser.add_argument("--plan-dir", required=True, type=Path)
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--repo", required=True, type=Path)
    return parser


def _usage_refusal(message: str) -> dict[str, Any]:
    return {
        "schema_version": RECEIPT_SCHEMA,
        "result": "REFUSE",
        "inputs": {"plan_directory": None, "evidence_root": None, "repository": None},
        "checks": [
            {
                "check": "arguments",
                "result": "REFUSE",
                "reasons": ["invalid_arguments"],
            }
        ],
        "refusal_reasons": ["invalid_arguments"],
        "detail": message,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        receipt = validate(args.plan_dir, args.evidence_root, args.repo)
    except CliError as exc:
        receipt = _usage_refusal(str(exc))
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["result"] == "PASS" else REFUSAL_EXIT


if __name__ == "__main__":
    raise SystemExit(main())
