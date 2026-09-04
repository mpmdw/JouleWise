"""Fail-closed renderer for registered Results fills OB-01 and OR-01.

The D-165 close-out is revalidated against its exact three source byte
strings.  Before-comparison evidence crosses a path-and-digest boundary: the
renderer reopens the real whole-window row, its authoritative campaign log,
and the prospective manifest/plan tree before replaying their owning
validators.  The current whole-window validator returns one undifferentiated
refusal tuple for both failed admission and failed provenance, so that lane
deliberately remains ``STOP_FILL`` until a governed structured receipt exists.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from joulewise import analysis_manifest_v3, dominance_closeout, whole_window
from joulewise.campaign_provenance import load_authenticated_campaign_manifest


STOP_FILL = "STOP_FILL"
OB_01 = "OB-01"
OR_01 = "OR-01"
IDENTITY_NOT_V5 = "identity_not_v5"
STOP_REASON = "_stop_reason"
SECONDARY_CLOSEOUT_REASON = "_secondary_closeout_reason"

_AT_CLOSE_OUT = "at close-out"
_FORBIDDEN_PUBLIC_MARKERS = ("[FILL:", "[PENDING]", "[VALUE]", STOP_FILL)
_V5_IDENTITIES = {
    (
        "Qwen3-1.7B-4bit",
        "3b1b1768f8f8cf8351c712464f906e86c2b8269e",
        "qwen3",
    ): "Qwen3-1.7B",
    (
        "Qwen3-8B-4bit",
        "545dc4251c05440727734bcd94334791f6ab0192",
        "qwen3",
    ): "Qwen3-8B",
}
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


def _stopped(reason: str | None = None) -> dict[str, str]:
    result = {OB_01: STOP_FILL, OR_01: STOP_FILL}
    if reason is not None:
        result[STOP_REASON] = reason
    return result


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


def _authenticated_closeout(
    closeout: object,
    *,
    finalized_manifest_bytes: object,
    floor_artifact_bytes: object,
    replay_sidecar_bytes: object,
) -> bool:
    if not isinstance(closeout, Mapping) or not all(
        isinstance(value, bytes)
        for value in (
            finalized_manifest_bytes,
            floor_artifact_bytes,
            replay_sidecar_bytes,
        )
    ):
        return False
    try:
        errors = dominance_closeout.validate_d165_closeout(
            closeout,
            finalized_manifest_bytes=finalized_manifest_bytes,
            floor_artifact_bytes=floor_artifact_bytes,
            replay_sidecar_bytes=replay_sidecar_bytes,
        )
    except (KeyError, TypeError, ValueError):
        return False
    return not errors


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

    identities: set[tuple[str, str, str]] = set()
    model_by_floor_cell: dict[str, str] = {}
    for arm in manifest["arms"]:
        if not isinstance(arm, Mapping):
            return None
        floor_cell_id = _safe_public_string(arm.get("floor_cell_id"))
        stack = arm.get("realized_stack_identity")
        model = stack.get("model") if isinstance(stack, Mapping) else None
        if floor_cell_id is None or not isinstance(model, Mapping):
            return None
        identity = (model.get("name"), model.get("revision"), model.get("family"))
        if identity not in _V5_IDENTITIES:
            return None
        identities.add(identity)
        public_name = _V5_IDENTITIES[identity]
        existing = model_by_floor_cell.get(floor_cell_id)
        if existing is not None and existing != public_name:
            return None
        model_by_floor_cell[floor_cell_id] = public_name
    if identities != set(_V5_IDENTITIES):
        return None
    return model_by_floor_cell


def _record_label(record: Mapping[str, Any], *, common_mode: bool) -> str | None:
    cell_id = _safe_public_string(record.get("cell_id"))
    component = record.get("component")
    if cell_id is None or component not in {"absolute", "comparative"}:
        return None
    suffix = "comparative common-mode" if common_mode else str(component)
    return f"{cell_id} {suffix}"


def _render_ob01(closeout: Mapping[str, Any]) -> str:
    if closeout.get("branch") != "B":
        return STOP_FILL
    labels: list[str] = []
    for key, common_mode in (
        ("independent_ratios", False),
        ("comparative_common_mode_ratios", True),
    ):
        records = closeout.get(key)
        if not isinstance(records, list):
            return STOP_FILL
        for record in records:
            if not isinstance(record, Mapping):
                return STOP_FILL
            if record.get("passes") is False:
                label = _record_label(record, common_mode=common_mode)
                if label is None:
                    return STOP_FILL
                labels.append(label)
    return _english_list(labels) if labels else STOP_FILL


def _render_closeout_refusal(closeout: Mapping[str, Any]) -> str:
    reason = _safe_public_string(closeout.get("refusal_reason"))
    if reason is None:
        return STOP_FILL
    affected: list[str] = []
    for key, common_mode in (
        ("independent_ratios", False),
        ("comparative_common_mode_ratios", True),
    ):
        records = closeout.get(key)
        if not isinstance(records, list):
            return STOP_FILL
        for record in records:
            if not isinstance(record, Mapping):
                return STOP_FILL
            if record.get("status") != "refused":
                continue
            record_label = _record_label(record, common_mode=common_mode)
            if record_label is None:
                return STOP_FILL
            affected.append(record_label)
    affected_text = _english_list(affected) if affected else "none recorded"
    return f"{_AT_CLOSE_OUT}: {reason}; affected: {affected_text}"


def render_outcome_fills(
    closeout: Mapping[str, Any] | None,
    *,
    finalized_manifest_bytes: bytes | None = None,
    floor_artifact_bytes: bytes | None = None,
    replay_sidecar_bytes: bytes | None = None,
    runs_root_path: Path | str | None = None,
    campaign_log_path: Path | str | None = None,
    campaign_log_sha256: str | None = None,
    whole_window_verdict_path: Path | str | None = None,
    whole_window_verdict_sha256: str | None = None,
    prospective_manifest_path: Path | str | None = None,
    prospective_manifest_sha256: str | None = None,
    plan_tree_path: Path | str | None = None,
    plan_tree_sha256: str | None = None,
) -> dict[str, str]:
    """Return registered OB-01/OR-01 strings, or fail closed.

    Before-comparison sources have registered precedence over an authenticated
    close-out refusal.  Until the whole-window validator exposes the ruled
    admission/provenance distinction, that winning stage emits ``STOP_FILL``;
    a later close-out reason remains secondary non-paper metadata.
    """

    authenticated_closeout = False
    if closeout is not None:
        authenticated_closeout = _authenticated_closeout(
            closeout,
            finalized_manifest_bytes=finalized_manifest_bytes,
            floor_artifact_bytes=floor_artifact_bytes,
            replay_sidecar_bytes=replay_sidecar_bytes,
        )
        if not authenticated_closeout:
            return _stopped()

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
        return _stopped(IDENTITY_NOT_V5)
    if before_state == _BEFORE_INVALID:
        return _stopped()
    if before_state == _BEFORE_WHOLE_WINDOW_UNRENDERABLE:
        result = _stopped()
        if closeout is not None and closeout.get("branch") is None:
            secondary_reason = _safe_public_string(closeout.get("refusal_reason"))
            if secondary_reason is None:
                return _stopped()
            result[SECONDARY_CLOSEOUT_REASON] = secondary_reason
        return result
    if not authenticated_closeout:
        return _stopped()

    model_by_floor_cell = _v5_manifest_model_names(finalized_manifest_bytes)
    if model_by_floor_cell is None:
        return _stopped(IDENTITY_NOT_V5)

    assert closeout is not None
    branch = closeout.get("branch")
    if branch in {"A", "B"}:
        return {OB_01: _render_ob01(closeout), OR_01: STOP_FILL}
    if branch is None:
        refusal = _render_closeout_refusal(closeout)
        if refusal != STOP_FILL:
            return {OB_01: STOP_FILL, OR_01: refusal}
    return _stopped()


__all__ = [
    "IDENTITY_NOT_V5",
    "OB_01",
    "OR_01",
    "SECONDARY_CLOSEOUT_REASON",
    "STOP_FILL",
    "STOP_REASON",
    "render_outcome_fills",
]
