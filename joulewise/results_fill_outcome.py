"""Fail-closed renderer for registered Results fills OB-01 and OR-01.

Both evidence lanes cross path-and-digest boundaries and replay their owning
validators.  A close-out additionally requires a digest-bound validation
receipt that binds the close-out and all three source files.  Callers must
branch on :class:`OutcomeFillRefusal`; only ``OutcomeFillResult.fills`` may be
substituted into a draft, and those values never contain the ``STOP_FILL``
token.  Refusal reasons and secondary close-out diagnostics are non-paper
metadata.  The current whole-window validator remains unable to distinguish
failed admission from failed provenance, so that lane refuses until a governed
structured receipt exists.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any

from joulewise import (
    analysis_manifest_v3,
    dominance_closeout,
    identity_pins,
    whole_window,
)
from joulewise.campaign_provenance import load_authenticated_campaign_manifest


STOP_FILL = "STOP_FILL"
OB_01 = "OB-01"
OR_01 = "OR-01"
IDENTITY_NOT_V5 = "identity_not_v5"
CLOSEOUT_VALIDATION_RECEIPT_SCHEMA = (
    "joulewise.d165_closeout_validation_receipt.v1"
)
CLOSEOUT_VALIDATOR = "joulewise.dominance_closeout.validate_d165_closeout"
CLOSEOUT_REASON_UNREGISTERED = "closeout_reason_unregistered"
CLOSEOUT_EVIDENCE_INVALID = "closeout_evidence_invalid"
CLOSEOUT_PROSE_UNSAFE = "closeout_prose_unsafe"
EVIDENCE_ABSENT = "evidence_absent"
BEFORE_COMPARISON_INVALID = "before_comparison_invalid"
BEFORE_COMPARISON_UNRENDERABLE = "before_comparison_unrenderable"

_AT_CLOSE_OUT = "at close-out"
_FORBIDDEN_PUBLIC_MARKERS = ("[FILL:", "[PENDING]", "[VALUE]", STOP_FILL)
_PUBLIC_CELL_ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_V5_CLOSEOUT_PINS = {
    "A": {
        "model_tag": "qwen3-1p7b",
        "public_name": "Qwen3-1.7B",
        "model": {
            "context_window": 40960,
            "family": "qwen3",
            "name": "Qwen3-1.7B-4bit",
            "revision": "3b1b1768f8f8cf8351c712464f906e86c2b8269e",
            "source": "/Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit",
            "weight_format": "mlx",
        },
        "tokenizer": {
            "backend": "mlx",
            "class": "TokenizerWrapper",
            "identifier": "/Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit",
            "revision": "3b1b1768f8f8cf8351c712464f906e86c2b8269e",
            "vocab_size": 151936,
        },
    },
    "B": {
        "model_tag": "qwen3-8b",
        "public_name": "Qwen3-8B",
        "model": {
            "context_window": 40960,
            "family": "qwen3",
            "name": "Qwen3-8B-4bit",
            "revision": "545dc4251c05440727734bcd94334791f6ab0192",
            "source": "/Users/edr/jw_models/mlx-community/Qwen3-8B-4bit",
            "weight_format": "mlx",
        },
        "tokenizer": {
            "backend": "mlx",
            "class": "TokenizerWrapper",
            "identifier": "/Users/edr/jw_models/mlx-community/Qwen3-8B-4bit",
            "revision": "545dc4251c05440727734bcd94334791f6ab0192",
            "vocab_size": 151936,
        },
    },
}
_V5_IDENTITIES = {
    (
        pin["model"]["name"],
        pin["model"]["revision"],
        pin["model"]["family"],
    ): pin["public_name"]
    for pin in _V5_CLOSEOUT_PINS.values()
}

CLOSEOUT_REASON_SENTENCES: Mapping[str, str] = MappingProxyType({
    dominance_closeout.CLOSEOUT_INPUT_MALFORMED:
        "the dominance close-out inputs were malformed",
    dominance_closeout.CLOSEOUT_INPUT_MALFORMED_ADAPTER:
        "the dominance replay block identities were malformed",
    dominance_closeout.CLOSEOUT_INPUT_MALFORMED_RECORDS:
        "the dominance close-out ratio records were malformed",
    dominance_closeout.CLOSEOUT_INPUT_MALFORMED_SOURCE:
        "the dominance close-out source census or block membership was malformed",
    dominance_closeout.DOMINANCE_ZERO_DENOMINATOR_REASON:
        "a required attribution-dominance ratio could not be evaluated because its repeatability floor was zero",
    dominance_closeout.FLOOR_ARTIFACT_SOURCE_HASH_MISMATCH:
        "the detection-floor source did not match the finalized campaign record",
    "cell_not_common_mode":
        "a required comparison lacks its registered common-mode replay",
    "common_mode_replay_authenticated_operative_bound_invalid":
        "the common-mode replay lacks its authenticated timing bound",
    "common_mode_replay_block_count_invalid":
        "the common-mode replay has an invalid block count",
    "common_mode_replay_input_invalid":
        "the common-mode replay inputs were invalid",
    "common_mode_replay_window_domain_invalid":
        "a common-mode replay window fell outside the registered domain",
    "common_mode_replay_zero_point_divergence_out_of_domain":
        "a common-mode replay zero point fell outside the registered tolerance",
    "common_mode_replay_zero_point_membership_invalid":
        "a common-mode replay zero point was absent from its registered sweeps",
    "d165_mint_adapter_input_invalid":
        "the dominance replay inputs could not be adapted from the detection-floor record",
    "dominance_ratio_nonfinite_or_negative_denominator":
        "a required attribution-dominance denominator was invalid",
    "dominance_ratio_nonfinite_or_negative_numerator":
        "a required attribution-dominance numerator was invalid",
    "dominance_ratio_nonfinite_result":
        "a required attribution-dominance ratio was not finite",
    "finalized_manifest_id_mismatch":
        "the finalized campaign record did not match its content-derived identity",
    "floor_cell_unresolved":
        "a required detection-floor cell could not be resolved",
    "floor_member_census_mismatch":
        "the replay membership did not match the detection-floor membership",
    "manifest_lacks_replay_sidecar":
        "the finalized campaign record lacks the required dominance replay",
    "point_floor_parent_nonfinite_or_negative":
        "a required repeatability-floor input was invalid",
    "replay_sidecar_digest_mismatch":
        "the dominance replay did not match its registered digest",
    "replay_sidecar_identity_mismatch":
        "the dominance replay did not match its registered identity",
})
_V5_IDENTITY_BY_ARM = {
    "A": next(
        identity
        for identity, name in _V5_IDENTITIES.items()
        if name == "Qwen3-1.7B"
    ),
    "B": next(
        identity
        for identity, name in _V5_IDENTITIES.items()
        if name == "Qwen3-8B"
    ),
}
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_BEFORE_ABSENT = "absent"
_BEFORE_INVALID = "invalid"
_BEFORE_IDENTITY_NOT_V5 = "identity_not_v5"
_BEFORE_WHOLE_WINDOW_UNRENDERABLE = "whole_window_unrenderable"
_CLOSEOUT_ABSENT = "absent"
_CLOSEOUT_INVALID = "invalid"
_CLOSEOUT_AUTHENTICATED = "authenticated"
_CLOSEOUT_RECEIPT_KEYS = {
    "schema_version",
    "validator",
    "status",
    "closeout_sha256",
    "source_sha256",
    "errors",
}
_CLOSEOUT_SOURCE_RECEIPT_KEYS = {
    "finalized_manifest",
    "floor_artifact",
    "replay_sidecar",
}


@dataclass(frozen=True)
class OutcomeFillRefusal:
    """Out-of-band refusal metadata; never substitute this into paper prose."""

    reason_code: str
    secondary_closeout_reason: str | None = None


@dataclass(frozen=True)
class OutcomeFillResult:
    """Authorized fill values; every stopped outcome uses the sibling type."""

    fills: Mapping[str, str]

    def __post_init__(self) -> None:
        object.__setattr__(self, "fills", MappingProxyType(dict(self.fills)))


def _refused(
    reason_code: str,
    *,
    secondary_closeout_reason: str | None = None,
) -> OutcomeFillRefusal:
    return OutcomeFillRefusal(
        reason_code=reason_code,
        secondary_closeout_reason=secondary_closeout_reason,
    )


def _issued(fills: Mapping[str, str]) -> OutcomeFillResult | OutcomeFillRefusal:
    copied = dict(fills)
    if any(
        key not in {OB_01, OR_01}
        or _safe_public_string(value) is None
        or value == STOP_FILL
        for key, value in copied.items()
    ):
        return _refused(CLOSEOUT_PROSE_UNSAFE)
    return OutcomeFillResult(fills=copied)


def _safe_public_string(value: object) -> str | None:
    if not isinstance(value, str) or not value or "\n" in value or "\r" in value:
        return None
    if any(marker in value for marker in _FORBIDDEN_PUBLIC_MARKERS):
        return None
    return value


def _english_list(values: Sequence[str]) -> str:
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return ", ".join(values[:-1]) + f", and {values[-1]}"


def _decode_json_object_bytes(value: object) -> Mapping[str, Any] | None:
    if not isinstance(value, bytes):
        return None

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = item
        return result

    def reject_nonfinite(value: str) -> None:
        raise ValueError(f"non-finite JSON number: {value}")

    try:
        decoded = json.loads(
            value.decode("utf-8"),
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_nonfinite,
        )
    except (UnicodeError, ValueError):
        return None
    return decoded if isinstance(decoded, Mapping) else None


def _path(value: object) -> Path | None:
    if isinstance(value, bytes):
        return None
    try:
        path = Path(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return path if path.is_absolute() and ".." not in path.parts else None


def _read_bound_regular(
    value: object,
    expected_sha256: object,
    *,
    within: Path | None = None,
) -> tuple[Path, bytes] | None:
    """Read one digest-bound regular file without following its final link."""

    path = _path(value)
    if (
        path is None
        or not isinstance(expected_sha256, str)
        or _SHA256_RE.fullmatch(expected_sha256) is None
    ):
        return None
    try:
        if path.is_symlink():
            return None
        if within is not None:
            root = Path(within).resolve(strict=True)
            lexical_root = Path(within).absolute()
            lexical_path = path.absolute()
            relative = lexical_path.relative_to(lexical_root)
            if not relative.parts:
                return None
            current = lexical_root
            for part in relative.parts:
                current /= part
                if stat.S_ISLNK(current.lstat().st_mode):
                    return None
            resolved = path.resolve(strict=True)
            if resolved == root or root not in resolved.parents:
                return None
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(
            os, "O_NOFOLLOW", 0
        )
        descriptor = os.open(path, flags)
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                return None
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
        finally:
            os.close(descriptor)
    except (OSError, RuntimeError, ValueError):
        return None
    raw = b"".join(chunks)
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        return None
    return path, raw


def _authenticated_closeout_path(
    *,
    closeout_path: object,
    closeout_sha256: object,
    finalized_manifest_path: object,
    finalized_manifest_sha256: object,
    floor_artifact_path: object,
    floor_artifact_sha256: object,
    replay_sidecar_path: object,
    replay_sidecar_sha256: object,
    closeout_validation_receipt_path: object,
    closeout_validation_receipt_sha256: object,
) -> tuple[str, Mapping[str, Any] | None, bytes | None]:
    """Open and replay one receipt-bound close-out evidence chain."""

    bindings = (
        (closeout_path, closeout_sha256),
        (finalized_manifest_path, finalized_manifest_sha256),
        (floor_artifact_path, floor_artifact_sha256),
        (replay_sidecar_path, replay_sidecar_sha256),
        (
            closeout_validation_receipt_path,
            closeout_validation_receipt_sha256,
        ),
    )
    supplied = tuple(value is not None for binding in bindings for value in binding)
    if not any(supplied):
        return _CLOSEOUT_ABSENT, None, None
    if not all(supplied):
        return _CLOSEOUT_INVALID, None, None

    opened = tuple(
        _read_bound_regular(path, digest) for path, digest in bindings
    )
    if any(source is None for source in opened):
        return _CLOSEOUT_INVALID, None, None
    closeout_source, manifest_source, floor_source, sidecar_source, receipt_source = (
        source for source in opened if source is not None
    )
    closeout = _decode_json_object_bytes(closeout_source[1])
    manifest = _decode_json_object_bytes(manifest_source[1])
    receipt = _decode_json_object_bytes(receipt_source[1])
    receipt_sources = (
        receipt.get("source_sha256") if isinstance(receipt, Mapping) else None
    )
    if (
        closeout is None
        or manifest is None
        or receipt is None
        or set(receipt) != _CLOSEOUT_RECEIPT_KEYS
        or receipt.get("schema_version") != CLOSEOUT_VALIDATION_RECEIPT_SCHEMA
        or receipt.get("validator") != CLOSEOUT_VALIDATOR
        or receipt.get("status") != "PASS"
        or receipt.get("errors") != []
        or receipt.get("closeout_sha256") != closeout_sha256
        or not isinstance(receipt_sources, Mapping)
        or set(receipt_sources) != _CLOSEOUT_SOURCE_RECEIPT_KEYS
        or receipt_sources.get("finalized_manifest")
        != finalized_manifest_sha256
        or receipt_sources.get("floor_artifact") != floor_artifact_sha256
        or receipt_sources.get("replay_sidecar") != replay_sidecar_sha256
    ):
        return _CLOSEOUT_INVALID, None, None
    try:
        errors = dominance_closeout.validate_d165_closeout(
            closeout,
            finalized_manifest_bytes=manifest_source[1],
            floor_artifact_bytes=floor_source[1],
            replay_sidecar_bytes=sidecar_source[1],
        )
    except (KeyError, TypeError, ValueError):
        return _CLOSEOUT_INVALID, None, None
    if errors:
        return _CLOSEOUT_INVALID, None, None

    # Reopen every path after validator replay so a replacement must still
    # match the out-of-band digest and the receipt that bound it.
    if any(
        _read_bound_regular(path, digest) is None
        for path, digest in bindings
    ):
        return _CLOSEOUT_INVALID, None, None
    return _CLOSEOUT_AUTHENTICATED, closeout, manifest_source[1]


def _safe_relative_path(root: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    pure = PurePosixPath(value)
    if (
        pure.is_absolute()
        or pure.as_posix() != value
        or any(part in {"", ".", ".."} for part in pure.parts)
    ):
        return None
    candidate = root.joinpath(*pure.parts)
    try:
        candidate.absolute().relative_to(root.absolute())
    except ValueError:
        return None
    return candidate


def _exactly_once_in_log(row_raw: bytes, log_raw: bytes) -> bool:
    count = 0
    for line in log_raw.splitlines(keepends=True):
        if not line.strip():
            continue
        if not line.endswith(b"\n"):
            return False
        if _decode_json_object_bytes(line) is None:
            return False
        if line == row_raw:
            count += 1
    return count == 1


def _validated_prospective_v5_members(
    manifest: Mapping[str, Any],
    *,
    manifest_path: Path,
    plan_tree_path: Path,
) -> set[str] | str | None:
    try:
        refusals = analysis_manifest_v3.validate_prospective_analysis_manifest_v3(
            manifest,
            manifest_dir=manifest_path.parent,
            plan_tree_path=plan_tree_path,
        )
    except (OSError, RuntimeError, TypeError, ValueError):
        return None
    if type(refusals) is not tuple or refusals:
        return None

    contrasts = manifest.get("contrasts")
    if not isinstance(contrasts, list):
        return None
    member_ids: set[str] = set()
    phases: set[str] = set()
    identities: set[tuple[str, str, str]] = set()
    for contrast in contrasts:
        if not isinstance(contrast, Mapping):
            return None
        phase = contrast.get("measurement_arm")
        members = contrast.get("members")
        if not isinstance(phase, str) or not isinstance(members, list):
            return None
        phases.add(phase)
        for member in members:
            if not isinstance(member, Mapping):
                return None
            run_id = member.get("run_id")
            arm = member.get("arm")
            relative = member.get("config")
            expected_sha256 = member.get("config_sha256")
            config_path = _safe_relative_path(manifest_path.parent, relative)
            config_source = (
                _read_bound_regular(
                    config_path,
                    expected_sha256,
                    within=manifest_path.parent,
                )
                if config_path is not None
                else None
            )
            config = (
                _decode_json_object_bytes(config_source[1])
                if config_source is not None
                else None
            )
            model = config.get("model") if isinstance(config, Mapping) else None
            metadata = (
                config.get("run_metadata") if isinstance(config, Mapping) else None
            )
            tags = metadata.get("tags") if isinstance(metadata, Mapping) else None
            identity = (
                model.get("name"),
                model.get("revision"),
                model.get("family"),
            ) if isinstance(model, Mapping) else None
            if (
                not isinstance(run_id, str)
                or not run_id
                or run_id in member_ids
                or arm not in _V5_IDENTITY_BY_ARM
                or not isinstance(config, Mapping)
                or config.get("run_id") != run_id
                or identity != _V5_IDENTITY_BY_ARM[arm]
                or not isinstance(tags, list)
                or f"measurement-arm={phase}" not in tags
            ):
                return _BEFORE_IDENTITY_NOT_V5
            member_ids.add(run_id)
            identities.add(identity)
    if (
        len(phases) != 2
        or "decode" not in phases
        or len(phases - {"decode"}) != 1
        or not next(iter(phases - {"decode"})).startswith("prefill_")
        or identities != set(_V5_IDENTITIES)
    ):
        return _BEFORE_IDENTITY_NOT_V5
    return member_ids


def _row_matches_prospective_custody(
    row: Mapping[str, Any],
    *,
    runs_root: Path,
    campaign_log_path: Path,
    manifest: Mapping[str, Any],
    manifest_sha256: str,
    expected_member_ids: set[str],
) -> bool:
    provenance = row.get("row_provenance")
    descriptors = (
        provenance.get("source_campaign_manifests")
        if isinstance(provenance, Mapping)
        else None
    )
    if (
        not isinstance(descriptors, list)
        or not descriptors
        or row.get("source_campaign_manifests") != descriptors
    ):
        return False
    observed_bundle_ids: list[str] = []
    observed_run_ids: list[str] = []
    for descriptor in descriptors:
        if not isinstance(descriptor, Mapping):
            return False
        source_path = _safe_relative_path(runs_root, descriptor.get("path"))
        source = (
            _read_bound_regular(
                source_path,
                descriptor.get("sha256"),
                within=runs_root,
            )
            if source_path is not None
            else None
        )
        if source is None:
            return False
        authenticated = load_authenticated_campaign_manifest(
            runs_root, source[0], campaign_log_path
        )
        if (
            authenticated is None
            or authenticated.raw_bytes != source[1]
            or authenticated.value.get("analysis_manifest_id")
            != manifest.get("manifest_id")
            or authenticated.value.get("analysis_manifest_sha256")
            != manifest_sha256
        ):
            return False
        members = authenticated.value.get("members")
        if not isinstance(members, list):
            return False
        for member in members:
            if not isinstance(member, Mapping):
                return False
            run_id = member.get("run_id")
            bundle_ids = member.get("bundle_ids")
            if not isinstance(run_id, str) or not isinstance(bundle_ids, list):
                return False
            observed_run_ids.append(run_id)
            observed_bundle_ids.extend(bundle_ids)
    return (
        len(observed_run_ids) == len(set(observed_run_ids))
        and len(observed_bundle_ids) == len(set(observed_bundle_ids))
        and set(observed_run_ids) == expected_member_ids
        and set(observed_bundle_ids) == expected_member_ids
    )


def _validated_before_comparison_path(
    *,
    runs_root_path: object,
    campaign_log_path: object,
    campaign_log_sha256: object,
    whole_window_verdict_path: object,
    whole_window_verdict_sha256: object,
    prospective_manifest_path: object,
    prospective_manifest_sha256: object,
    plan_tree_path: object,
    plan_tree_sha256: object,
) -> str:
    values = (
        runs_root_path,
        campaign_log_path,
        campaign_log_sha256,
        whole_window_verdict_path,
        whole_window_verdict_sha256,
        prospective_manifest_path,
        prospective_manifest_sha256,
        plan_tree_path,
        plan_tree_sha256,
    )
    supplied = tuple(value is not None for value in values)
    if not any(supplied):
        return _BEFORE_ABSENT
    if not all(supplied):
        return _BEFORE_INVALID

    runs_root = _path(runs_root_path)
    log_path = _path(campaign_log_path)
    verdict_path = _path(whole_window_verdict_path)
    manifest_path = _path(prospective_manifest_path)
    tree_path = _path(plan_tree_path)
    try:
        if (
            runs_root is None
            or runs_root.is_symlink()
            or not runs_root.is_dir()
            or log_path is None
            or log_path.absolute() != (runs_root / "campaign_log.jsonl").absolute()
            or verdict_path is None
            or manifest_path is None
            or tree_path is None
            or tree_path.parent.absolute() != manifest_path.parent.absolute()
        ):
            return _BEFORE_INVALID
    except (OSError, RuntimeError):
        return _BEFORE_INVALID

    log_source = _read_bound_regular(
        log_path, campaign_log_sha256, within=runs_root
    )
    verdict_source = _read_bound_regular(
        verdict_path, whole_window_verdict_sha256
    )
    manifest_source = _read_bound_regular(
        manifest_path, prospective_manifest_sha256
    )
    tree_source = _read_bound_regular(tree_path, plan_tree_sha256)
    if None in (log_source, verdict_source, manifest_source, tree_source):
        return _BEFORE_INVALID
    assert log_source is not None
    assert verdict_source is not None
    assert manifest_source is not None
    assert tree_source is not None
    row = _decode_json_object_bytes(verdict_source[1])
    manifest = _decode_json_object_bytes(manifest_source[1])
    if (
        row is None
        or manifest is None
        or not _exactly_once_in_log(verdict_source[1], log_source[1])
        or verdict_source[1]
        != (json.dumps(row, sort_keys=True) + "\n").encode("utf-8")
        or row.get("schema_version") != whole_window.WHOLE_WINDOW_SCHEMA
        or row.get("record_type") != "idle_admission_whole_window_verdict"
        or row.get("status") not in {"invalid", "failed", "flagged"}
    ):
        return _BEFORE_INVALID

    expected_member_ids = _validated_prospective_v5_members(
        manifest,
        manifest_path=manifest_path,
        plan_tree_path=tree_path,
    )
    if expected_member_ids == _BEFORE_IDENTITY_NOT_V5:
        return _BEFORE_IDENTITY_NOT_V5
    if not isinstance(expected_member_ids, set) or not expected_member_ids:
        return _BEFORE_INVALID

    basis = row.get("evaluation_basis")
    row_bundle_ids = row.get("bundle_ids")
    occurrences = (
        basis.get("member_occurrences") if isinstance(basis, Mapping) else None
    )
    occurrence_ids = (
        [
            occurrence.get("bundle_id")
            for occurrence in occurrences
            if isinstance(occurrence, Mapping)
        ]
        if isinstance(occurrences, list)
        else []
    )
    evaluation_basis_sha256 = (
        basis.get("sha256") if isinstance(basis, Mapping) else None
    )
    consumption_semantics_id = (
        basis.get("consumption_semantics_id")
        if isinstance(basis, Mapping)
        else None
    )
    if (
        not isinstance(row_bundle_ids, list)
        or any(
            not isinstance(bundle_id, str) or not bundle_id
            for bundle_id in row_bundle_ids
        )
        or len(row_bundle_ids) != len(set(row_bundle_ids))
        or set(row_bundle_ids) != expected_member_ids
        or not isinstance(occurrences, list)
        or len(occurrence_ids) != len(occurrences)
        or any(
            not isinstance(bundle_id, str) or not bundle_id
            for bundle_id in occurrence_ids
        )
        or len(occurrence_ids) != len(set(occurrence_ids))
        or set(occurrence_ids) != expected_member_ids
        or not isinstance(evaluation_basis_sha256, str)
        or _SHA256_RE.fullmatch(evaluation_basis_sha256) is None
        or not isinstance(consumption_semantics_id, str)
        or not _row_matches_prospective_custody(
            row,
            runs_root=runs_root,
            campaign_log_path=log_path,
            manifest=manifest,
            manifest_sha256=str(prospective_manifest_sha256),
            expected_member_ids=expected_member_ids,
        )
    ):
        return _BEFORE_INVALID

    try:
        result = whole_window.whole_window_refusal_reasons(
            runs_root,
            expected_member_ids,
            evaluation_basis_sha256=evaluation_basis_sha256,
            consumption_semantics_id=consumption_semantics_id,
        )
    except (OSError, RuntimeError, TypeError, ValueError):
        return _BEFORE_INVALID
    if (
        type(result) is not tuple
        or not result
        or any(not isinstance(reason, str) or not reason for reason in result)
    ):
        return _BEFORE_INVALID

    # Reopen every caller-supplied file after validator replay.  A replacement
    # must still match its expected digest; the tuple itself is not authority.
    for path_value, digest, within in (
        (log_path, campaign_log_sha256, runs_root),
        (verdict_path, whole_window_verdict_sha256, None),
        (manifest_path, prospective_manifest_sha256, None),
        (tree_path, plan_tree_sha256, None),
    ):
        if _read_bound_regular(path_value, digest, within=within) is None:
            return _BEFORE_INVALID
    return _BEFORE_WHOLE_WINDOW_UNRENDERABLE


def _v5_manifest_model_names(
    finalized_manifest_bytes: object,
) -> dict[str, str] | None:
    manifest = _decode_json_object_bytes(finalized_manifest_bytes)
    if manifest is None or not isinstance(manifest.get("arms"), list):
        return None

    seen_arm_labels: list[str] = []
    model_by_floor_cell: dict[str, str] = {}
    for arm in manifest["arms"]:
        if not isinstance(arm, Mapping):
            return None
        arm_id = arm.get("arm_id")
        arm_label = (
            arm_id.rsplit(":", 1)[1]
            if isinstance(arm_id, str) and ":" in arm_id
            else None
        )
        pin = _V5_CLOSEOUT_PINS.get(arm_label)
        floor_cell_id = _safe_public_string(arm.get("floor_cell_id"))
        stack = arm.get("realized_stack_identity")
        model = stack.get("model") if isinstance(stack, Mapping) else None
        tokenizer = stack.get("tokenizer") if isinstance(stack, Mapping) else None
        artifact = stack.get("model_artifact") if isinstance(stack, Mapping) else None
        floor_stack = arm.get("floor_stack_identity")
        if (
            pin is None
            or floor_cell_id is None
            or not isinstance(stack, Mapping)
            or not isinstance(model, Mapping)
            or not isinstance(tokenizer, Mapping)
            or not isinstance(artifact, Mapping)
            or not isinstance(floor_stack, Mapping)
        ):
            return None
        try:
            identity_pins.stack_identity_sha256(floor_stack)
        except (TypeError, ValueError):
            return None
        floor_tokenizer = floor_stack.get("tokenizer_identity")
        expected_floor_tokenizer = dict(pin["tokenizer"])
        expected_floor_tokenizer["identifier"] = pin["model"]["name"]
        artifact_digest = artifact.get("sha256") or artifact.get("folded_sha256")
        runtime = stack.get("runtime")
        floor_runtime = floor_stack.get("runtime_version")
        telemetry = stack.get("telemetry")
        if (
            arm.get("model_tag") != pin["model_tag"]
            or dict(model) != pin["model"]
            or dict(tokenizer) != pin["tokenizer"]
            or floor_tokenizer != expected_floor_tokenizer
            or floor_stack.get("model_artifact_sha256") != artifact_digest
            or floor_stack.get("quantization") != stack.get("quantization")
            or not isinstance(runtime, Mapping)
            or not isinstance(floor_runtime, Mapping)
            or {
                "name": runtime.get("name"),
                "adapter": runtime.get("adapter"),
                "version": runtime.get("version"),
            }
            != dict(floor_runtime)
            or not isinstance(telemetry, Mapping)
            or floor_stack.get("telemetry_backend") != telemetry.get("name")
        ):
            return None
        seen_arm_labels.append(str(arm_label))
        public_name = str(pin["public_name"])
        existing = model_by_floor_cell.get(floor_cell_id)
        if existing is not None and existing != public_name:
            return None
        model_by_floor_cell[floor_cell_id] = public_name
    if sorted(seen_arm_labels) != ["A", "A", "B", "B"]:
        return None
    return model_by_floor_cell


def _record_label(record: Mapping[str, Any], *, common_mode: bool) -> str | None:
    cell_id = _safe_public_string(record.get("cell_id"))
    component = record.get("component")
    if (
        cell_id is None
        or _PUBLIC_CELL_ID_RE.fullmatch(cell_id) is None
        or component not in {"absolute", "comparative"}
    ):
        return None
    suffix = "comparative common-mode" if common_mode else str(component)
    return f"{cell_id} {suffix}"


def _render_ob01(closeout: Mapping[str, Any]) -> str | None:
    if closeout.get("branch") != "B":
        return None
    labels: list[str] = []
    for key, common_mode in (
        ("independent_ratios", False),
        ("comparative_common_mode_ratios", True),
    ):
        records = closeout.get(key)
        if not isinstance(records, list):
            return None
        for record in records:
            if not isinstance(record, Mapping):
                return None
            if record.get("passes") is False:
                label = _record_label(record, common_mode=common_mode)
                if label is None:
                    return None
                labels.append(label)
    return _english_list(labels) if labels else None


def _render_closeout_refusal(closeout: Mapping[str, Any]) -> str | None:
    reason_code = closeout.get("refusal_reason")
    if not isinstance(reason_code, str):
        return None
    reason = CLOSEOUT_REASON_SENTENCES.get(reason_code)
    if reason is None or _safe_public_string(reason) is None:
        return None
    affected: list[str] = []
    for key, common_mode in (
        ("independent_ratios", False),
        ("comparative_common_mode_ratios", True),
    ):
        records = closeout.get(key)
        if not isinstance(records, list):
            return None
        for record in records:
            if not isinstance(record, Mapping):
                return None
            if record.get("status") != "refused":
                continue
            record_label = _record_label(record, common_mode=common_mode)
            if record_label is None:
                return None
            affected.append(record_label)
    affected_text = _english_list(affected) if affected else "none recorded"
    return f"{_AT_CLOSE_OUT}: {reason}; affected: {affected_text}"


def render_outcome_fills(
    *,
    closeout_path: Path | str | None = None,
    closeout_sha256: str | None = None,
    finalized_manifest_path: Path | str | None = None,
    finalized_manifest_sha256: str | None = None,
    floor_artifact_path: Path | str | None = None,
    floor_artifact_sha256: str | None = None,
    replay_sidecar_path: Path | str | None = None,
    replay_sidecar_sha256: str | None = None,
    closeout_validation_receipt_path: Path | str | None = None,
    closeout_validation_receipt_sha256: str | None = None,
    runs_root_path: Path | str | None = None,
    campaign_log_path: Path | str | None = None,
    campaign_log_sha256: str | None = None,
    whole_window_verdict_path: Path | str | None = None,
    whole_window_verdict_sha256: str | None = None,
    prospective_manifest_path: Path | str | None = None,
    prospective_manifest_sha256: str | None = None,
    plan_tree_path: Path | str | None = None,
    plan_tree_sha256: str | None = None,
) -> OutcomeFillResult | OutcomeFillRefusal:
    """Return only authorized OB-01/OR-01 strings, with refusal out of band.

    Before-comparison sources have registered precedence over an authenticated
    close-out refusal.  Until the whole-window validator exposes the ruled
    admission/provenance distinction, that winning stage returns a structured
    refusal; a later close-out reason remains secondary non-paper metadata.
    The successor must substitute only ``result.fills`` and translate any
    ``OutcomeFillRefusal`` to stderr plus exit status 2.
    """

    closeout_state, closeout, finalized_manifest_bytes = (
        _authenticated_closeout_path(
            closeout_path=closeout_path,
            closeout_sha256=closeout_sha256,
            finalized_manifest_path=finalized_manifest_path,
            finalized_manifest_sha256=finalized_manifest_sha256,
            floor_artifact_path=floor_artifact_path,
            floor_artifact_sha256=floor_artifact_sha256,
            replay_sidecar_path=replay_sidecar_path,
            replay_sidecar_sha256=replay_sidecar_sha256,
            closeout_validation_receipt_path=closeout_validation_receipt_path,
            closeout_validation_receipt_sha256=(
                closeout_validation_receipt_sha256
            ),
        )
    )
    if closeout_state == _CLOSEOUT_INVALID:
        return _refused(CLOSEOUT_EVIDENCE_INVALID)

    before_state = _validated_before_comparison_path(
        runs_root_path=runs_root_path,
        campaign_log_path=campaign_log_path,
        campaign_log_sha256=campaign_log_sha256,
        whole_window_verdict_path=whole_window_verdict_path,
        whole_window_verdict_sha256=whole_window_verdict_sha256,
        prospective_manifest_path=prospective_manifest_path,
        prospective_manifest_sha256=prospective_manifest_sha256,
        plan_tree_path=plan_tree_path,
        plan_tree_sha256=plan_tree_sha256,
    )
    if before_state == _BEFORE_IDENTITY_NOT_V5:
        return _refused(IDENTITY_NOT_V5)
    if before_state == _BEFORE_INVALID:
        return _refused(BEFORE_COMPARISON_INVALID)
    if before_state == _BEFORE_WHOLE_WINDOW_UNRENDERABLE:
        secondary_reason = None
        if closeout is not None and closeout.get("branch") is None:
            secondary_reason = closeout.get("refusal_reason")
            if not isinstance(secondary_reason, str) or not secondary_reason:
                return _refused(CLOSEOUT_EVIDENCE_INVALID)
        return _refused(
            BEFORE_COMPARISON_UNRENDERABLE,
            secondary_closeout_reason=secondary_reason,
        )
    if closeout_state != _CLOSEOUT_AUTHENTICATED:
        return _refused(EVIDENCE_ABSENT)

    model_by_floor_cell = _v5_manifest_model_names(finalized_manifest_bytes)
    if model_by_floor_cell is None:
        return _refused(IDENTITY_NOT_V5)

    assert closeout is not None
    branch = closeout.get("branch")
    if branch == "A":
        return _issued({})
    if branch == "B":
        ob01 = _render_ob01(closeout)
        return _issued({OB_01: ob01}) if ob01 is not None else _refused(
            CLOSEOUT_PROSE_UNSAFE
        )
    if branch is None:
        refusal = _render_closeout_refusal(closeout)
        if refusal is not None:
            return _issued({OR_01: refusal})
        reason = closeout.get("refusal_reason")
        return _refused(
            CLOSEOUT_REASON_UNREGISTERED
            if isinstance(reason, str) and reason
            else CLOSEOUT_EVIDENCE_INVALID
        )
    return _refused(CLOSEOUT_EVIDENCE_INVALID)


__all__ = [
    "BEFORE_COMPARISON_INVALID",
    "BEFORE_COMPARISON_UNRENDERABLE",
    "CLOSEOUT_EVIDENCE_INVALID",
    "CLOSEOUT_PROSE_UNSAFE",
    "CLOSEOUT_REASON_SENTENCES",
    "CLOSEOUT_REASON_UNREGISTERED",
    "CLOSEOUT_VALIDATION_RECEIPT_SCHEMA",
    "CLOSEOUT_VALIDATOR",
    "EVIDENCE_ABSENT",
    "IDENTITY_NOT_V5",
    "OB_01",
    "OR_01",
    "OutcomeFillRefusal",
    "OutcomeFillResult",
    "STOP_FILL",
    "render_outcome_fills",
]
