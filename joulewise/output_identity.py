"""C-023 cross-bundle decoded-output identity report (AXI-SA §10)."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from joulewise.analysis_engine.registry import (
    ALLOWED_CONFIG_DIFFERENCE_POINTERS,
    canonical_json_bytes,
    normalized_json_bytes,
    sha256_bytes,
)
from joulewise.axi_decode_config import AxiSchemaError, TargetTokenizerIdentity


SCHEMA_VERSION = "joulewise.output_identity_report.v1"
STATES = {
    "exact_token_match",
    "text_match_token_divergent",
    "output_divergent",
    "unassessable",
}
DISPOSITIONS = {
    "exact_token_match": "matched_decoded_work",
    "text_match_token_divergent": "text_matched_descriptive_or_predeclared_quality_matched",
    "output_divergent": "descriptive_only",
    "unassessable": "refuse_efficiency_claim",
}
MISSING_EVIDENCE_REASONS = (
    "config_projection_unavailable",
    "config_sha256_unavailable",
    "output_count_comparison_unavailable",
    "request_roster_key_unavailable",
    "request_tokens_artifact_unavailable",
    "requests_artifact_unavailable",
    "run_id_unavailable",
    "spec_off_request_id_unavailable",
    "spec_off_response_text_unavailable",
    "spec_off_token_ids_unavailable",
    "spec_on_request_id_unavailable",
    "spec_on_response_text_unavailable",
    "spec_on_token_ids_unavailable",
    "stop_reason_comparison_unavailable",
    "strict_validation_report_unavailable",
    "summary_artifact_unavailable",
    "target_tokenizer_identity_unavailable",
)
REASON_CODES = (
    "output_count_differs",
    "request_roster_mismatch",
    "response_text_differs",
    "response_text_unavailable",
    "single_bundle_invalid",
    "stop_reason_differs",
    "target_tokenizer_identity_mismatch",
    "target_tokenizer_identity_unavailable",
    "token_ids_differ",
    "token_ids_unavailable",
    "unexpected_config_difference",
)
BUNDLE_KEYS = {
    "run_id", "config_sha256", "requests_artifact_sha256",
    "request_tokens_artifact_sha256", "summary_sha256",
    "strict_validation_state", "strict_validation_report_sha256",
    "target_tokenizer_identity", "missing_evidence_reasons",
}
CONFIG_GATE_KEYS = {
    "allowed_difference_pointers", "spec_off_projection_sha256",
    "spec_on_projection_sha256", "projections_equal",
    "unexpected_difference_pointers", "missing_evidence_reasons",
}
REQUEST_KEYS = {
    "request_ordinal", "request_input_id", "spec_off_request_id",
    "spec_on_request_id", "spec_off_token_ids_sha256",
    "spec_on_token_ids_sha256", "spec_off_text_sha256",
    "spec_on_text_sha256", "output_token_count_equal",
    "stop_reason_equal", "state", "missing_evidence_reasons", "reason_codes",
}
REPORT_KEYS = {
    "schema_version", "report_id", "manifest_id", "pair_id",
    "spec_off_bundle", "spec_on_bundle", "config_gate",
    "target_tokenizer_comparison", "requests", "overall_state",
    "claim_disposition",
}
_SHA_RE = re.compile(r"[0-9a-f]{64}")
_REPORT_ID_RE = re.compile(r"oir-[0-9a-f]{64}")


class OutputIdentityError(ValueError):
    """Malformed C-023 report or report input."""


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and _SHA_RE.fullmatch(value) is not None


def _hash_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _json_object(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _jsonl_objects(path: Path) -> list[dict[str, Any]] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    result: list[dict[str, Any]] = []
    for line in text.splitlines():
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            return None
        if not isinstance(value, dict):
            return None
        result.append(value)
    return result


def _strict_report(
    path: Path | None,
    strict_validator: Callable[[Path, bool], list[str]] | None,
) -> tuple[str, str | None]:
    if path is None or not path.is_dir() or strict_validator is None:
        return "unavailable", None
    try:
        problems = sorted(set(strict_validator(path, True)))
    except (OSError, ValueError, TypeError):
        return "unavailable", None
    payload = {"problems": problems, "valid": not problems}
    return (
        "valid" if not problems else "invalid",
        sha256_bytes(canonical_json_bytes(payload)),
    )


def _bundle_reference(
    path: Path | None,
    strict_validator: Callable[[Path, bool], list[str]] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    metadata = _json_object(path / "metadata.json") if path is not None else None
    config = _json_object(path / "config.json") if path is not None else None
    summary = _json_object(path / "summary_metrics.json") if path is not None else None
    request_rows = _jsonl_objects(path / "outputs" / "requests.jsonl") if path is not None else None
    token_rows = _jsonl_objects(path / "outputs" / "request_tokens.jsonl") if path is not None else None
    roster = _json_object(path / "request_roster.json") if path is not None else None
    run_id = metadata.get("run_id") if isinstance(metadata, dict) else None
    if not isinstance(run_id, str) or not run_id:
        run_id = None
    strict_state, strict_hash = _strict_report(path, strict_validator)
    identity = None
    if isinstance(metadata, dict):
        runtime = metadata.get("runtime")
        if isinstance(runtime, dict):
            try:
                identity = TargetTokenizerIdentity.from_mapping(
                    runtime.get("target_tokenizer_identity")
                ).to_dict()
            except AxiSchemaError:
                identity = None
    config_hash = _hash_file(path / "config.json") if config is not None and path is not None else None
    requests_hash = _hash_file(path / "outputs" / "requests.jsonl") if request_rows is not None and path is not None else None
    tokens_hash = _hash_file(path / "outputs" / "request_tokens.jsonl") if token_rows is not None and path is not None else None
    summary_hash = _hash_file(path / "summary_metrics.json") if summary is not None and path is not None else None
    reasons: list[str] = []
    for missing, reason in (
        (run_id is None, "run_id_unavailable"),
        (config_hash is None, "config_sha256_unavailable"),
        (requests_hash is None, "requests_artifact_unavailable"),
        (tokens_hash is None, "request_tokens_artifact_unavailable"),
        (summary_hash is None, "summary_artifact_unavailable"),
        (strict_hash is None, "strict_validation_report_unavailable"),
        (identity is None, "target_tokenizer_identity_unavailable"),
    ):
        if missing:
            reasons.append(reason)
    reference = {
        "run_id": run_id,
        "config_sha256": config_hash,
        "requests_artifact_sha256": requests_hash,
        "request_tokens_artifact_sha256": tokens_hash,
        "summary_sha256": summary_hash,
        "strict_validation_state": strict_state,
        "strict_validation_report_sha256": strict_hash,
        "target_tokenizer_identity": identity,
        "missing_evidence_reasons": sorted(reasons),
    }
    evidence = {
        "config": config,
        "request_rows": request_rows,
        "token_rows": token_rows,
        "roster": roster,
    }
    return reference, evidence


def _remove_pointer(value: dict[str, Any], pointer: str) -> None:
    components = pointer.removeprefix("/").split("/")
    target: Any = value
    for component in components[:-1]:
        if not isinstance(target, dict) or component not in target:
            return
        target = target[component]
    if isinstance(target, dict):
        target.pop(components[-1], None)


def config_projection(value: Mapping[str, Any]) -> dict[str, Any]:
    projected = copy.deepcopy(dict(value))
    for pointer in ALLOWED_CONFIG_DIFFERENCE_POINTERS:
        _remove_pointer(projected, pointer)
    return projected


def _escape_pointer(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _difference_pointers(left: Any, right: Any, path: str = "") -> list[str]:
    if isinstance(left, dict) and isinstance(right, dict):
        result: list[str] = []
        for key in sorted(set(left) | set(right)):
            child = path + "/" + _escape_pointer(str(key))
            if key not in left or key not in right:
                result.append(child)
            else:
                result.extend(_difference_pointers(left[key], right[key], child))
        return result
    if isinstance(left, list) and isinstance(right, list):
        result = []
        for index in range(max(len(left), len(right))):
            child = path + f"/{index}"
            if index >= len(left) or index >= len(right):
                result.append(child)
            else:
                result.extend(_difference_pointers(left[index], right[index], child))
        return result
    return [] if left == right else [path or "/"]


def _config_gate(off: Mapping[str, Any] | None, on: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(off, Mapping) or not isinstance(on, Mapping):
        return {
            "allowed_difference_pointers": list(ALLOWED_CONFIG_DIFFERENCE_POINTERS),
            "spec_off_projection_sha256": None,
            "spec_on_projection_sha256": None,
            "projections_equal": None,
            "unexpected_difference_pointers": [],
            "missing_evidence_reasons": ["config_projection_unavailable"],
        }
    off_projection = config_projection(off)
    on_projection = config_projection(on)
    off_hash = sha256_bytes(canonical_json_bytes(off_projection))
    on_hash = sha256_bytes(canonical_json_bytes(on_projection))
    differences = sorted(set(_difference_pointers(off_projection, on_projection)))
    return {
        "allowed_difference_pointers": list(ALLOWED_CONFIG_DIFFERENCE_POINTERS),
        "spec_off_projection_sha256": off_hash,
        "spec_on_projection_sha256": on_hash,
        "projections_equal": off_hash == on_hash,
        "unexpected_difference_pointers": differences,
        "missing_evidence_reasons": [],
    }


def _target_tokenizer_comparison(off: Any, on: Any) -> str:
    if not isinstance(off, dict) or not isinstance(on, dict):
        return "unassessable"
    return "exact_match" if off == on else "mismatch"


def _roster_keys(roster: Any) -> list[tuple[int, str]] | None:
    if not isinstance(roster, dict) or set(roster) != {"schema_version", "requests"}:
        return None
    requests = roster.get("requests")
    if not isinstance(requests, list):
        return None
    result: list[tuple[int, str]] = []
    for row in requests:
        if not isinstance(row, dict):
            return None
        ordinal = row.get("request_ordinal")
        input_id = row.get("request_input_id")
        if not isinstance(ordinal, int) or isinstance(ordinal, bool) or ordinal < 0 or not isinstance(input_id, str) or not input_id:
            return None
        result.append((ordinal, input_id))
    return result


def _by_roster_key(rows: Any) -> dict[tuple[int, str], dict[str, Any]]:
    if not isinstance(rows, list):
        return {}
    return {
        (row.get("request_ordinal"), row.get("request_input_id")): row
        for row in rows
        if isinstance(row, dict)
        and isinstance(row.get("request_ordinal"), int)
        and isinstance(row.get("request_input_id"), str)
    }


def _request_comparison(
    key: tuple[int, str] | None,
    off: Mapping[str, Any] | None,
    on: Mapping[str, Any] | None,
    *,
    global_precondition: bool,
    roster_match: bool,
    off_strict: str,
    on_strict: str,
    tokenizer_comparison: str,
    config_equal: bool | None,
) -> dict[str, Any]:
    missing: list[str] = []
    if key is None:
        ordinal = input_id = None
        missing.append("request_roster_key_unavailable")
    else:
        ordinal, input_id = key
    off_id = off.get("request_id") if isinstance(off, Mapping) else None
    on_id = on.get("request_id") if isinstance(on, Mapping) else None
    off_tokens = off.get("emitted_token_ids_sha256") if isinstance(off, Mapping) else None
    on_tokens = on.get("emitted_token_ids_sha256") if isinstance(on, Mapping) else None
    off_text = off.get("response_text_sha256") if isinstance(off, Mapping) else None
    on_text = on.get("response_text_sha256") if isinstance(on, Mapping) else None
    nullable = (
        (not isinstance(off_id, str) or not off_id, "spec_off_request_id_unavailable", "off_id"),
        (not isinstance(on_id, str) or not on_id, "spec_on_request_id_unavailable", "on_id"),
        (not _is_sha(off_tokens), "spec_off_token_ids_unavailable", "off_tokens"),
        (not _is_sha(on_tokens), "spec_on_token_ids_unavailable", "on_tokens"),
        (not _is_sha(off_text), "spec_off_response_text_unavailable", "off_text"),
        (not _is_sha(on_text), "spec_on_response_text_unavailable", "on_text"),
    )
    values: dict[str, Any] = {
        "off_id": off_id, "on_id": on_id, "off_tokens": off_tokens,
        "on_tokens": on_tokens, "off_text": off_text, "on_text": on_text,
    }
    for absent, reason, name in nullable:
        if absent:
            values[name] = None
            missing.append(reason)
    counts_available = isinstance(off, Mapping) and isinstance(on, Mapping) and all(
        isinstance(row.get("output_token_count"), int)
        and not isinstance(row.get("output_token_count"), bool)
        for row in (off, on)
    )
    count_equal = off["output_token_count"] == on["output_token_count"] if counts_available else None
    if count_equal is None:
        missing.append("output_count_comparison_unavailable")
    stops_available = isinstance(off, Mapping) and isinstance(on, Mapping) and all(
        isinstance(row.get("stop_reason"), str) and row.get("stop_reason")
        for row in (off, on)
    )
    stop_equal = off["stop_reason"] == on["stop_reason"] if stops_available else None
    if stop_equal is None:
        missing.append("stop_reason_comparison_unavailable")

    reasons: set[str] = set()
    if off_strict != "valid" or on_strict != "valid":
        reasons.add("single_bundle_invalid")
    if not roster_match or key is None:
        reasons.add("request_roster_mismatch")
    if tokenizer_comparison == "unassessable":
        reasons.add("target_tokenizer_identity_unavailable")
    elif tokenizer_comparison == "mismatch":
        reasons.add("target_tokenizer_identity_mismatch")
    if config_equal is not True:
        reasons.add("unexpected_config_difference")
    if values["off_tokens"] is None or values["on_tokens"] is None:
        reasons.add("token_ids_unavailable")
    elif values["off_tokens"] != values["on_tokens"]:
        reasons.add("token_ids_differ")
    if values["off_text"] is None or values["on_text"] is None:
        reasons.add("response_text_unavailable")
    elif values["off_text"] != values["on_text"]:
        reasons.add("response_text_differs")
    if count_equal is False:
        reasons.add("output_count_differs")
    if stop_equal is False:
        reasons.add("stop_reason_differs")
    if any(
        reason in missing
        for reason in (
            "spec_off_request_id_unavailable", "spec_on_request_id_unavailable",
            "output_count_comparison_unavailable", "stop_reason_comparison_unavailable",
        )
    ):
        reasons.add("single_bundle_invalid")

    request_precondition = (
        global_precondition and "single_bundle_invalid" not in reasons
    )
    if not request_precondition:
        state = "unassessable"
    elif stop_equal is False:
        state = "output_divergent"
    elif values["off_text"] is not None and values["on_text"] is not None:
        if values["off_text"] != values["on_text"]:
            state = "output_divergent"
        elif values["off_tokens"] is None or values["on_tokens"] is None:
            state = "unassessable"
        elif values["off_tokens"] == values["on_tokens"] and count_equal is True:
            state = "exact_token_match"
        else:
            state = "text_match_token_divergent"
    elif values["off_tokens"] is not None and values["off_tokens"] == values["on_tokens"] and count_equal is True:
        state = "exact_token_match"
    else:
        state = "unassessable"
    return {
        "request_ordinal": ordinal,
        "request_input_id": input_id,
        "spec_off_request_id": values["off_id"],
        "spec_on_request_id": values["on_id"],
        "spec_off_token_ids_sha256": values["off_tokens"],
        "spec_on_token_ids_sha256": values["on_tokens"],
        "spec_off_text_sha256": values["off_text"],
        "spec_on_text_sha256": values["on_text"],
        "output_token_count_equal": count_equal,
        "stop_reason_equal": stop_equal,
        "state": state,
        "missing_evidence_reasons": sorted(set(missing)),
        "reason_codes": sorted(reasons),
    }


def calculate_report_id(report: Mapping[str, Any]) -> str:
    content = dict(report)
    content.pop("report_id", None)
    return "oir-" + sha256_bytes(canonical_json_bytes(content))


def _derive_output_identity_report(
    *,
    manifest_id: str,
    pair_id: str,
    spec_off_bundle: Path | None,
    spec_on_bundle: Path | None,
    strict_validator: Callable[[Path, bool], list[str]] | None,
) -> dict[str, Any]:
    off_ref, off_evidence = _bundle_reference(spec_off_bundle, strict_validator)
    on_ref, on_evidence = _bundle_reference(spec_on_bundle, strict_validator)
    config_gate = _config_gate(off_evidence["config"], on_evidence["config"])
    tokenizer_comparison = _target_tokenizer_comparison(
        off_ref["target_tokenizer_identity"], on_ref["target_tokenizer_identity"]
    )
    off_keys = _roster_keys(off_evidence["roster"])
    on_keys = _roster_keys(on_evidence["roster"])
    roster_match = off_keys is not None and on_keys is not None and off_keys == on_keys
    keys = off_keys if off_keys is not None else on_keys if on_keys is not None else []
    off_rows = _by_roster_key(off_evidence["request_rows"])
    on_rows = _by_roster_key(on_evidence["request_rows"])
    global_precondition = (
        off_ref["strict_validation_state"] == "valid"
        and on_ref["strict_validation_state"] == "valid"
        and roster_match
        and config_gate["projections_equal"] is True
        and tokenizer_comparison == "exact_match"
    )
    requests = [
        _request_comparison(
            key,
            off_rows.get(key),
            on_rows.get(key),
            global_precondition=global_precondition,
            roster_match=roster_match,
            off_strict=off_ref["strict_validation_state"],
            on_strict=on_ref["strict_validation_state"],
            tokenizer_comparison=tokenizer_comparison,
            config_equal=config_gate["projections_equal"],
        )
        for key in keys
    ]
    if not global_precondition or not requests:
        overall = "unassessable"
    elif any(row["state"] == "output_divergent" for row in requests):
        overall = "output_divergent"
    elif any(row["state"] == "unassessable" for row in requests):
        overall = "unassessable"
    elif any(row["state"] == "text_match_token_divergent" for row in requests):
        overall = "text_match_token_divergent"
    else:
        overall = "exact_token_match"
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": manifest_id,
        "pair_id": pair_id,
        "spec_off_bundle": off_ref,
        "spec_on_bundle": on_ref,
        "config_gate": config_gate,
        "target_tokenizer_comparison": tokenizer_comparison,
        "requests": requests,
        "overall_state": overall,
        "claim_disposition": DISPOSITIONS[overall],
    }
    report["report_id"] = calculate_report_id(report)
    return report


def build_output_identity_report(
    *,
    manifest_id: str,
    pair_id: str,
    spec_off_bundle: Path | None,
    spec_on_bundle: Path | None,
    strict_validator: Callable[[Path, bool], list[str]] | None,
) -> dict[str, Any]:
    report = _derive_output_identity_report(
        manifest_id=manifest_id,
        pair_id=pair_id,
        spec_off_bundle=spec_off_bundle,
        spec_on_bundle=spec_on_bundle,
        strict_validator=strict_validator,
    )
    validate_output_identity_report(
        report,
        spec_off_bundle=spec_off_bundle,
        spec_on_bundle=spec_on_bundle,
        strict_validator=strict_validator,
    )
    return report


def _exact(value: Any, keys: set[str], where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise OutputIdentityError(f"{where} exact keys mismatch")
    return value


def _ordered_enum_array(value: Any, allowed: Sequence[str], where: str) -> None:
    if not isinstance(value, list) or any(item not in allowed for item in value):
        raise OutputIdentityError(f"{where} contains invalid value")
    if value != sorted(set(value)):
        raise OutputIdentityError(f"{where} must be unique and lexicographically sorted")


_EVIDENCE_UNSET = object()


def _rederived_request_assertions(
    request: Mapping[str, Any],
    *,
    off_strict: str,
    on_strict: str,
    tokenizer_comparison: str,
    config_equal: bool | None,
    roster_match: bool,
    global_precondition: bool,
) -> tuple[list[str], list[str], str]:
    missing: set[str] = set()
    if request["request_ordinal"] is None or request["request_input_id"] is None:
        missing.add("request_roster_key_unavailable")
    nullable_reasons = (
        ("spec_off_request_id", "spec_off_request_id_unavailable"),
        ("spec_on_request_id", "spec_on_request_id_unavailable"),
        ("spec_off_token_ids_sha256", "spec_off_token_ids_unavailable"),
        ("spec_on_token_ids_sha256", "spec_on_token_ids_unavailable"),
        ("spec_off_text_sha256", "spec_off_response_text_unavailable"),
        ("spec_on_text_sha256", "spec_on_response_text_unavailable"),
        ("output_token_count_equal", "output_count_comparison_unavailable"),
        ("stop_reason_equal", "stop_reason_comparison_unavailable"),
    )
    for key, reason in nullable_reasons:
        if request[key] is None:
            missing.add(reason)

    reasons: set[str] = set()
    if off_strict != "valid" or on_strict != "valid":
        reasons.add("single_bundle_invalid")
    if not roster_match or "request_roster_key_unavailable" in missing:
        reasons.add("request_roster_mismatch")
    if tokenizer_comparison == "unassessable":
        reasons.add("target_tokenizer_identity_unavailable")
    elif tokenizer_comparison == "mismatch":
        reasons.add("target_tokenizer_identity_mismatch")
    if config_equal is not True:
        reasons.add("unexpected_config_difference")

    off_tokens = request["spec_off_token_ids_sha256"]
    on_tokens = request["spec_on_token_ids_sha256"]
    off_text = request["spec_off_text_sha256"]
    on_text = request["spec_on_text_sha256"]
    count_equal = request["output_token_count_equal"]
    stop_equal = request["stop_reason_equal"]
    if off_tokens is None or on_tokens is None:
        reasons.add("token_ids_unavailable")
    elif off_tokens != on_tokens:
        reasons.add("token_ids_differ")
    if off_text is None or on_text is None:
        reasons.add("response_text_unavailable")
    elif off_text != on_text:
        reasons.add("response_text_differs")
    if count_equal is False:
        reasons.add("output_count_differs")
    if stop_equal is False:
        reasons.add("stop_reason_differs")
    if any(
        reason in missing
        for reason in (
            "spec_off_request_id_unavailable",
            "spec_on_request_id_unavailable",
            "output_count_comparison_unavailable",
            "stop_reason_comparison_unavailable",
        )
    ):
        reasons.add("single_bundle_invalid")

    request_precondition = global_precondition and "single_bundle_invalid" not in reasons
    if not request_precondition:
        state = "unassessable"
    elif stop_equal is False:
        state = "output_divergent"
    elif off_text is not None and on_text is not None:
        if off_text != on_text:
            state = "output_divergent"
        elif off_tokens is None or on_tokens is None:
            state = "unassessable"
        elif off_tokens == on_tokens and count_equal is True:
            state = "exact_token_match"
        else:
            state = "text_match_token_divergent"
    elif off_tokens is not None and off_tokens == on_tokens and count_equal is True:
        state = "exact_token_match"
    else:
        state = "unassessable"
    return sorted(missing), sorted(reasons), state


def validate_output_identity_report(
    report: Mapping[str, Any],
    *,
    spec_off_bundle: Path | None | object = _EVIDENCE_UNSET,
    spec_on_bundle: Path | None | object = _EVIDENCE_UNSET,
    strict_validator: Callable[[Path, bool], list[str]] | None = None,
) -> None:
    row = _exact(report, REPORT_KEYS, "report")
    if row["schema_version"] != SCHEMA_VERSION:
        raise OutputIdentityError("report schema version invalid")
    if not isinstance(row["manifest_id"], str) or not row["manifest_id"] or not isinstance(row["pair_id"], str) or not row["pair_id"]:
        raise OutputIdentityError("report manifest/pair identity invalid")
    if not isinstance(row["report_id"], str) or _REPORT_ID_RE.fullmatch(row["report_id"]) is None:
        raise OutputIdentityError("report ID shape invalid")
    if row["report_id"] != calculate_report_id(row):
        raise OutputIdentityError("report ID hash mismatch")
    for label in ("spec_off_bundle", "spec_on_bundle"):
        bundle = _exact(row[label], BUNDLE_KEYS, label)
        for key in ("run_id",):
            if bundle[key] is not None and (not isinstance(bundle[key], str) or not bundle[key]):
                raise OutputIdentityError(f"{label}.{key} invalid")
        for key in (
            "config_sha256", "requests_artifact_sha256",
            "request_tokens_artifact_sha256", "summary_sha256",
            "strict_validation_report_sha256",
        ):
            if bundle[key] is not None and not _is_sha(bundle[key]):
                raise OutputIdentityError(f"{label}.{key} invalid")
        if bundle["strict_validation_state"] not in {"valid", "invalid", "unavailable"}:
            raise OutputIdentityError(f"{label} strict state invalid")
        try:
            if bundle["target_tokenizer_identity"] is not None:
                TargetTokenizerIdentity.from_mapping(bundle["target_tokenizer_identity"])
        except AxiSchemaError as exc:
            raise OutputIdentityError(f"{label} tokenizer identity invalid") from exc
        _ordered_enum_array(bundle["missing_evidence_reasons"], MISSING_EVIDENCE_REASONS, f"{label}.missing_evidence_reasons")
        biconditionals = (
            ("run_id", "run_id_unavailable"),
            ("config_sha256", "config_sha256_unavailable"),
            ("requests_artifact_sha256", "requests_artifact_unavailable"),
            ("request_tokens_artifact_sha256", "request_tokens_artifact_unavailable"),
            ("summary_sha256", "summary_artifact_unavailable"),
            ("target_tokenizer_identity", "target_tokenizer_identity_unavailable"),
        )
        for key, reason in biconditionals:
            if (bundle[key] is None) != (reason in bundle["missing_evidence_reasons"]):
                raise OutputIdentityError(f"{label}.{key} missing-reason biconditional failed")
        strict_missing = "strict_validation_report_unavailable" in bundle["missing_evidence_reasons"]
        if (bundle["strict_validation_report_sha256"] is None) != strict_missing or (bundle["strict_validation_state"] == "unavailable") != strict_missing:
            raise OutputIdentityError(f"{label} strict report biconditional failed")

    gate = _exact(row["config_gate"], CONFIG_GATE_KEYS, "config_gate")
    if gate["allowed_difference_pointers"] != list(ALLOWED_CONFIG_DIFFERENCE_POINTERS):
        raise OutputIdentityError("config gate allowed pointers mismatch")
    for key in ("spec_off_projection_sha256", "spec_on_projection_sha256"):
        if gate[key] is not None and not _is_sha(gate[key]):
            raise OutputIdentityError(f"config_gate.{key} invalid")
    if gate["projections_equal"] is not None and not isinstance(gate["projections_equal"], bool):
        raise OutputIdentityError("config gate equality invalid")
    _ordered_enum_array(gate["missing_evidence_reasons"], MISSING_EVIDENCE_REASONS, "config_gate.missing_evidence_reasons")
    pointers = gate["unexpected_difference_pointers"]
    if not isinstance(pointers, list) or any(not isinstance(item, str) for item in pointers) or pointers != sorted(set(pointers)):
        raise OutputIdentityError("unexpected difference pointers must be unique and sorted")
    projection_missing = any(gate[key] is None for key in ("spec_off_projection_sha256", "spec_on_projection_sha256", "projections_equal"))
    if projection_missing != ("config_projection_unavailable" in gate["missing_evidence_reasons"]):
        raise OutputIdentityError("config projection missing-reason biconditional failed")
    projection_hashes = (
        gate["spec_off_projection_sha256"],
        gate["spec_on_projection_sha256"],
    )
    if projection_missing:
        if projection_hashes != (None, None) or gate["projections_equal"] is not None:
            raise OutputIdentityError("config gate partial projection evidence")
        if gate["unexpected_difference_pointers"]:
            raise OutputIdentityError("config gate unavailable projection has difference pointers")
    else:
        expected_equal = projection_hashes[0] == projection_hashes[1]
        if gate["projections_equal"] is not expected_equal:
            raise OutputIdentityError("config gate equality is not re-derived from projection hashes")
        if expected_equal != (not gate["unexpected_difference_pointers"]):
            raise OutputIdentityError("config gate difference pointers disagree with projection equality")

    expected_tokenizer_comparison = _target_tokenizer_comparison(
        row["spec_off_bundle"]["target_tokenizer_identity"],
        row["spec_on_bundle"]["target_tokenizer_identity"],
    )
    if row["target_tokenizer_comparison"] not in {"exact_match", "mismatch", "unassessable"}:
        raise OutputIdentityError("target tokenizer comparison invalid")
    if row["target_tokenizer_comparison"] != expected_tokenizer_comparison:
        raise OutputIdentityError("target tokenizer comparison is not re-derived from bundle identities")
    requests = row["requests"]
    if not isinstance(requests, list):
        raise OutputIdentityError("requests must be an array")
    for index, request in enumerate(requests):
        request = _exact(request, REQUEST_KEYS, f"requests[{index}]")
        _ordered_enum_array(request["missing_evidence_reasons"], MISSING_EVIDENCE_REASONS, f"requests[{index}].missing_evidence_reasons")
        _ordered_enum_array(request["reason_codes"], REASON_CODES, f"requests[{index}].reason_codes")
        if request["state"] not in STATES:
            raise OutputIdentityError(f"requests[{index}] state invalid")
        key_missing = "request_roster_key_unavailable" in request["missing_evidence_reasons"]
        if (request["request_ordinal"] is None) != key_missing or (request["request_input_id"] is None) != key_missing:
            raise OutputIdentityError("request roster key biconditional failed")
        nullable_reasons = (
            ("spec_off_request_id", "spec_off_request_id_unavailable"),
            ("spec_on_request_id", "spec_on_request_id_unavailable"),
            ("spec_off_token_ids_sha256", "spec_off_token_ids_unavailable"),
            ("spec_on_token_ids_sha256", "spec_on_token_ids_unavailable"),
            ("spec_off_text_sha256", "spec_off_response_text_unavailable"),
            ("spec_on_text_sha256", "spec_on_response_text_unavailable"),
            ("output_token_count_equal", "output_count_comparison_unavailable"),
            ("stop_reason_equal", "stop_reason_comparison_unavailable"),
        )
        for key, reason in nullable_reasons:
            if (request[key] is None) != (reason in request["missing_evidence_reasons"]):
                raise OutputIdentityError(f"request {key} missing-reason biconditional failed")
        if request["request_ordinal"] is not None and (
            not isinstance(request["request_ordinal"], int)
            or isinstance(request["request_ordinal"], bool)
            or request["request_ordinal"] < 0
        ):
            raise OutputIdentityError("request ordinal invalid")
        if request["request_input_id"] is not None and (
            not isinstance(request["request_input_id"], str)
            or not request["request_input_id"]
        ):
            raise OutputIdentityError("request input identity invalid")
        for key in ("spec_off_request_id", "spec_on_request_id"):
            if request[key] is not None and (
                not isinstance(request[key], str) or not request[key]
            ):
                raise OutputIdentityError(f"request {key} invalid")
        for key in (
            "spec_off_token_ids_sha256",
            "spec_on_token_ids_sha256",
            "spec_off_text_sha256",
            "spec_on_text_sha256",
        ):
            if request[key] is not None and not _is_sha(request[key]):
                raise OutputIdentityError(f"request {key} invalid")
        for key in ("output_token_count_equal", "stop_reason_equal"):
            if request[key] is not None and not isinstance(request[key], bool):
                raise OutputIdentityError(f"request {key} invalid")

    roster_match = not any(
        "request_roster_mismatch" in request["reason_codes"]
        for request in requests
    )
    global_precondition = (
        row["spec_off_bundle"]["strict_validation_state"] == "valid"
        and row["spec_on_bundle"]["strict_validation_state"] == "valid"
        and roster_match
        and gate["projections_equal"] is True
        and expected_tokenizer_comparison == "exact_match"
    )
    for index, request in enumerate(requests):
        expected_missing, expected_reasons, expected_state = (
            _rederived_request_assertions(
                request,
                off_strict=row["spec_off_bundle"]["strict_validation_state"],
                on_strict=row["spec_on_bundle"]["strict_validation_state"],
                tokenizer_comparison=expected_tokenizer_comparison,
                config_equal=gate["projections_equal"],
                roster_match=roster_match,
                global_precondition=global_precondition,
            )
        )
        if request["missing_evidence_reasons"] != expected_missing:
            raise OutputIdentityError(f"requests[{index}] missing reasons are not re-derived")
        if request["reason_codes"] != expected_reasons:
            raise OutputIdentityError(f"requests[{index}] reason codes are not re-derived")
        if request["state"] != expected_state:
            raise OutputIdentityError(f"requests[{index}] state is not re-derived")

    if not global_precondition or not requests:
        expected_overall = "unassessable"
    elif any(request["state"] == "output_divergent" for request in requests):
        expected_overall = "output_divergent"
    elif any(request["state"] == "unassessable" for request in requests):
        expected_overall = "unassessable"
    elif any(
        request["state"] == "text_match_token_divergent"
        for request in requests
    ):
        expected_overall = "text_match_token_divergent"
    else:
        expected_overall = "exact_token_match"
    if row["overall_state"] != expected_overall:
        raise OutputIdentityError("overall state is not re-derived from request states")
    if row["overall_state"] not in STATES or row["claim_disposition"] != DISPOSITIONS.get(row["overall_state"]):
        raise OutputIdentityError("overall state/disposition mismatch")

    evidence_supplied = (
        spec_off_bundle is not _EVIDENCE_UNSET
        or spec_on_bundle is not _EVIDENCE_UNSET
    )
    if evidence_supplied:
        if (
            spec_off_bundle is _EVIDENCE_UNSET
            or spec_on_bundle is _EVIDENCE_UNSET
        ):
            raise OutputIdentityError("both bundle evidence paths are required")
        expected_report = _derive_output_identity_report(
            manifest_id=row["manifest_id"],
            pair_id=row["pair_id"],
            spec_off_bundle=spec_off_bundle,
            spec_on_bundle=spec_on_bundle,
            strict_validator=strict_validator,
        )
        if dict(row) != expected_report:
            raise OutputIdentityError(
                "report does not re-derive from underlying bundle evidence"
            )


def render_output_identity_report(report: Mapping[str, Any]) -> bytes:
    validate_output_identity_report(report)
    return normalized_json_bytes(report)


__all__ = [
    "DISPOSITIONS", "MISSING_EVIDENCE_REASONS", "OutputIdentityError",
    "REASON_CODES", "SCHEMA_VERSION", "STATES", "build_output_identity_report",
    "calculate_report_id", "config_projection", "render_output_identity_report",
    "validate_output_identity_report",
]
