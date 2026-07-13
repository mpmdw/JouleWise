"""Response-hash determinism gate for repeated run bundles (P2-028).

The gate compares response identities only after every input passes the shared
strict bundle validator.  Suite bundles carry one recorded ``response_sha256``
per item.  Non-suite bundles have one logical response and no stored hash
field, so their identity is SHA-256 over the exact ``outputs/response.txt``
bytes.  Configuration equality is exact after removing only the per-repetition
``run_id`` field.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from joulewise.bundle_read import BundleReadError, BundleReader

STRICT_PROBLEMS = Callable[[Path], list[str]]

SCHEMA_VERSION = "determinism_gate.v1"

VERDICT_SUPPORTED = "determinism_supported"
VERDICT_VIOLATED = "determinism_violated(response_hash_mismatch)"
VERDICT_REFUSED = "bundle_refused"

REASON_RESPONSE_HASH_MISMATCH = "response_hash_mismatch"
REASON_FEWER_THAN_TWO_BUNDLES = "fewer_than_two_bundles"
REASON_DUPLICATE_BUNDLE = "duplicate_bundle"
REASON_BUNDLE_NOT_STRICT_VALID = "bundle_not_strict_valid"
REASON_BUNDLE_NOT_SUCCEEDED = "bundle_not_succeeded"
REASON_BUNDLE_READ_ERROR = "bundle_read_error"
REASON_NOT_REPETITION_BUNDLE = "not_repetition_bundle"
REASON_DIFFERENT_REPETITION_GROUPS = "different_repetition_groups"
REASON_DUPLICATE_REPETITION = "duplicate_repetition"
REASON_DIFFERENT_CONFIGS = "different_configs"
REASON_IDENTITY_EVIDENCE_MISMATCH = "identity_evidence_mismatch"
REASON_IDENTITY_EVIDENCE_MALFORMED = "identity_evidence_malformed"
REASON_ITEM_SET_MISMATCH = "item_set_mismatch"
REASON_ITEM_NOT_SUCCEEDED = "item_not_succeeded"
REASON_ITEM_STATUS_MISMATCH = "item_status_mismatch"
REASON_NO_ITEMS_TO_COMPARE = "no_items_to_compare"
REASON_DUPLICATE_JSON_KEY = "duplicate_json_key"
REASON_RESPONSE_HASH_MISSING = "response_hash_missing"
REASON_RESPONSE_HASH_MALFORMED = "response_hash_malformed"
REASON_RESPONSE_HASH_EVIDENCE_MISMATCH = "response_hash_evidence_mismatch"
REASON_RESPONSE_HASH_CONTENT_MISMATCH = "response_hash_content_mismatch"
REASON_RESPONSE_TEXT_MALFORMED = "response_text_missing_or_malformed"
REASON_RESPONSE_EVIDENCE_PROFILE_MISMATCH = "response_evidence_profile_mismatch"
REASON_OUTPUT_INSIDE_INPUT_BUNDLE = "output_inside_input_bundle"

_SHA256_HEX = re.compile(r"[0-9a-f]{64}\Z")
_REPETITION_RUN_ID = re.compile(r"(.+)__r([1-9][0-9]*)\Z")
_MISSING = object()
_ELIGIBLE_ITEM_STATUSES = frozenset({"succeeded", "capped"})

IDENTITY_FIELD_NAMES = (
    "metadata.environment.python_packages",
    "metadata.workload_provenance.generator",
    "metadata.workload_provenance.model.artifact_identity.folded_sha256",
    "metadata.workload_provenance.model.artifact_identity.sha256",
    "metadata.workload_provenance.sampler",
    "metadata.workload_provenance.tokenizer",
)

_IDENTITY_FIELD_PATHS = {
    "metadata.environment.python_packages": ("environment", "python_packages"),
    "metadata.workload_provenance.generator": ("workload_provenance", "generator"),
    "metadata.workload_provenance.model.artifact_identity.folded_sha256": (
        "workload_provenance",
        "model",
        "artifact_identity",
        "folded_sha256",
    ),
    "metadata.workload_provenance.model.artifact_identity.sha256": (
        "workload_provenance",
        "model",
        "artifact_identity",
        "sha256",
    ),
    "metadata.workload_provenance.sampler": ("workload_provenance", "sampler"),
    "metadata.workload_provenance.tokenizer": ("workload_provenance", "tokenizer"),
}

_TOKENIZER_IDENTITY_KEYS = ("backend", "identifier", "revision", "class", "vocab_size")
_GENERATOR_IDENTITY_KEYS = ("name", "version")
_PACKAGE_IDENTITIES = ("mlx", "mlx-lm", "transformers")
_PACKAGE_IDENTITY_KEYS = ("present", "version")
#: Identity fields whose values must be sha256 hex to count as evidence;
#: equal-but-malformed values must refuse, never support (DRA-001).
_HASH_SHAPED_IDENTITY_FIELDS = frozenset(
    {
        "metadata.workload_provenance.model.artifact_identity.folded_sha256",
        "metadata.workload_provenance.model.artifact_identity.sha256",
    }
)


class _DuplicateJsonKeyError(ValueError):
    """A gate-read JSON object contained the same member name twice."""


@dataclass(frozen=True)
class _Inspection:
    record: dict[str, Any]
    items: dict[tuple[int, str], str]
    item_statuses: dict[tuple[int, str], str]
    identity_evidence: dict[str, Any]


def analyze_determinism_gate(
    bundle_dirs: list[Path],
    strict_problems: STRICT_PROBLEMS,
    *,
    preflight_reason_codes: list[str] | None = None,
) -> dict[str, Any]:
    """Return a JSON-serializable named verdict for one repetition group."""
    paths = [Path(path) for path in bundle_dirs]
    reason_codes = list(preflight_reason_codes or [])
    if len(paths) < 2:
        reason_codes.append(REASON_FEWER_THAN_TWO_BUNDLES)

    resolved_paths = [str(path.absolute()) for path in paths]
    if len(set(resolved_paths)) != len(resolved_paths):
        reason_codes.append(REASON_DUPLICATE_BUNDLE)

    records: list[dict[str, Any]] = []
    inspections: list[_Inspection] = []
    for path in paths:
        record = _empty_bundle_record(path)
        records.append(record)
        try:
            problems = list(strict_problems(path))
        except Exception as exc:  # noqa: BLE001 - validator failures become refusals.
            problems = [f"strict validator raised {type(exc).__name__}: {exc}"]
        record["strict_problems"] = problems
        record["strict_valid"] = not problems
        if problems:
            reason_codes.append(REASON_BUNDLE_NOT_STRICT_VALID)
            continue

        try:
            inspection, bundle_reasons = _inspect_strict_valid_bundle(path, record)
        except _DuplicateJsonKeyError as exc:
            record["evidence_problems"].append(str(exc))
            reason_codes.append(REASON_DUPLICATE_JSON_KEY)
            continue
        except (BundleReadError, OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            record["evidence_problems"].append(f"{type(exc).__name__}: {exc}")
            reason_codes.append(REASON_BUNDLE_READ_ERROR)
            continue
        inspections.append(inspection)
        reason_codes.extend(bundle_reasons)

    identity_fields_compared: list[str] = []
    identity_fields_absent: list[str] = []
    identity_fields_malformed: list[str] = []
    item_status_mismatches: list[dict[str, Any]] = []
    if len(inspections) == len(paths) and len(inspections) >= 2:
        (
            identity_fields_compared,
            identity_fields_absent,
            identity_fields_mismatched,
            identity_fields_malformed,
        ) = _identity_field_classification(inspections)
        if identity_fields_mismatched:
            reason_codes.append(REASON_IDENTITY_EVIDENCE_MISMATCH)
        if identity_fields_malformed:
            reason_codes.append(REASON_IDENTITY_EVIDENCE_MALFORMED)
        comparability_reasons, item_status_mismatches = _comparability_reasons(
            inspections
        )
        reason_codes.extend(comparability_reasons)

    if reason_codes:
        return _refused(
            records,
            reason_codes,
            identity_fields_compared=identity_fields_compared,
            identity_fields_absent=identity_fields_absent,
            identity_fields_malformed=identity_fields_malformed,
            item_status_mismatches=item_status_mismatches,
        )

    first = inspections[0]
    mismatches: list[dict[str, Any]] = []
    for item_key in sorted(first.items):
        observed = [
            {
                "path": inspection.record["path"],
                "run_id": inspection.record["run_id"],
                "response_sha256": inspection.items[item_key],
            }
            for inspection in inspections
        ]
        if len({entry["response_sha256"] for entry in observed}) > 1:
            item_index, item_id = item_key
            mismatches.append(
                {
                    "item_index": item_index,
                    "item_id": item_id,
                    "observed": observed,
                }
            )

    verdict = VERDICT_SUPPORTED if not mismatches else VERDICT_VIOLATED
    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": verdict,
        "reason_codes": [] if not mismatches else [REASON_RESPONSE_HASH_MISMATCH],
        "bundle_count": len(records),
        "bundles": records,
        "comparison": {
            "repetition_group": first.record["repetition_group"],
            "normalized_config_sha256": first.record["normalized_config_sha256"],
            "item_count": len(first.items),
            "response_hash_source": first.record["response_hash_source"],
        },
        "mismatches": mismatches,
        "item_status_mismatches": [],
        "identity_fields_compared": identity_fields_compared,
        "identity_fields_absent": identity_fields_absent,
        "identity_fields_malformed": [],
    }


def _empty_bundle_record(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "strict_valid": False,
        "strict_problems": [],
        "status": None,
        "run_id": None,
        "repetition_group": None,
        "repetition_index": None,
        "config_sha256": None,
        "normalized_config_sha256": None,
        "response_hash_source": None,
        "item_count": None,
        "item_status_counts": {},
        "items": [],
        "evidence_problems": [],
    }


def _inspect_strict_valid_bundle(
    path: Path,
    record: dict[str, Any],
) -> tuple[_Inspection, list[str]]:
    _check_gate_json_evidence_for_duplicate_keys(path)
    reader = BundleReader(path)
    reader.config()  # Retain the shared typed-validation boundary.
    config = reader.raw_config()
    if not isinstance(config, dict):
        raise BundleReadError("config.json is not a JSON object")
    metadata = reader.metadata()
    summary = reader.raw_summary()
    reasons: list[str] = []

    run_id = config.get("run_id")
    record["run_id"] = run_id if isinstance(run_id, str) else None
    match = _REPETITION_RUN_ID.fullmatch(run_id) if isinstance(run_id, str) else None
    if match is None:
        reasons.append(REASON_NOT_REPETITION_BUNDLE)
    else:
        record["repetition_group"] = match.group(1)
        record["repetition_index"] = int(match.group(2))

    normalized_config = dict(config)
    normalized_config.pop("run_id", None)
    record["normalized_config_sha256"] = _normalized_config_sha256(normalized_config)
    config_sha256 = metadata.get("config_sha256")
    record["config_sha256"] = config_sha256 if isinstance(config_sha256, str) else None

    status = summary.get("status") if isinstance(summary, dict) else None
    record["status"] = status if isinstance(status, str) else None
    if status != "succeeded":
        reasons.append(REASON_BUNDLE_NOT_SUCCEEDED)
        return _Inspection(record, {}, {}, _identity_evidence(metadata)), reasons

    if reader.suite_manifest() is not None:
        items, item_statuses, evidence_reasons = _suite_response_hashes(reader, record)
        record["response_hash_source"] = "recorded_suite_item"
    else:
        items, evidence_reasons = _single_response_hash(path, record)
        item_statuses = {}
        record["response_hash_source"] = "derived_response_bytes"
    record["item_count"] = len(items)
    record["item_status_counts"] = _item_status_counts(item_statuses)
    record["items"] = [
        {
            "item_index": item_index,
            "item_id": item_id,
            "response_sha256": response_hash,
            "status": item_statuses.get((item_index, item_id)),
        }
        for (item_index, item_id), response_hash in sorted(items.items())
    ]
    reasons.extend(evidence_reasons)
    return _Inspection(
        record,
        items,
        item_statuses,
        _identity_evidence(metadata),
    ), reasons


def _suite_response_hashes(
    reader: BundleReader,
    record: dict[str, Any],
) -> tuple[
    dict[tuple[int, str], str],
    dict[tuple[int, str], str],
    list[str],
]:
    items: dict[tuple[int, str], str] = {}
    item_statuses: dict[tuple[int, str], str] = {}
    reasons: list[str] = []
    manifest = reader.suite_manifest()
    if manifest is None:
        record["evidence_problems"].append("suite manifest disappeared during inspection")
        return {}, {}, [REASON_BUNDLE_READ_ERROR]
    output_path = reader.path / "outputs" / "suite_items.jsonl"
    try:
        lines = output_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        record["evidence_problems"].append(f"outputs/suite_items.jsonl cannot be read: {exc}")
        return {}, {}, [REASON_RESPONSE_HASH_MISSING]

    event_hashes: dict[int, str] = {}
    event_statuses: dict[int, str] = {}
    seen_event_indexes: set[int] = set()
    for window in reader.item_windows():
        item_index = window.item_index
        expected_item_id = (
            manifest.items[item_index].item_id
            if 0 <= item_index < len(manifest.items)
            else None
        )
        if expected_item_id is None or window.item_id != expected_item_id:
            reasons.append(REASON_ITEM_SET_MISMATCH)
            record["evidence_problems"].append(
                f"item_end item_index={item_index} item_id={window.item_id!r}, "
                f"expected {expected_item_id!r}"
            )
            continue
        if item_index in seen_event_indexes:
            reasons.append(REASON_ITEM_SET_MISMATCH)
            record["evidence_problems"].append(
                f"duplicate item_end response hash for item_index={item_index}"
            )
            continue
        seen_event_indexes.add(item_index)
        if (
            not isinstance(window.status, str)
            or window.status not in _ELIGIBLE_ITEM_STATUSES
        ):
            reasons.append(REASON_ITEM_NOT_SUCCEEDED)
            record["evidence_problems"].append(
                f"item_end item_index={item_index} has comparison-ineligible "
                f"status={window.status!r}"
            )
            continue
        event_statuses[item_index] = window.status
        if "response_sha256" not in window.end_metadata:
            reasons.append(REASON_RESPONSE_HASH_MISSING)
            record["evidence_problems"].append(
                f"item_end item_index={item_index} lacks response_sha256"
            )
            continue
        event_hash = window.end_metadata["response_sha256"]
        if not isinstance(event_hash, str) or _SHA256_HEX.fullmatch(event_hash) is None:
            reasons.append(REASON_RESPONSE_HASH_MALFORMED)
            record["evidence_problems"].append(
                f"item_end item_index={item_index} has malformed "
                f"response_sha256={event_hash!r}"
            )
            continue
        event_hashes[item_index] = event_hash

    missing_event_indexes = sorted(set(range(len(manifest.items))) - seen_event_indexes)
    if missing_event_indexes:
        reasons.append(REASON_ITEM_SET_MISMATCH)
        record["evidence_problems"].append(
            f"item_end response hashes omit manifest item_index values {missing_event_indexes}"
        )

    seen_output_indexes: set[int] = set()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            output = json.loads(line, object_pairs_hook=_reject_duplicate_json_pairs)
        except _DuplicateJsonKeyError as exc:
            raise _DuplicateJsonKeyError(
                f"outputs/suite_items.jsonl line {line_number}: {exc}"
            ) from exc
        except json.JSONDecodeError as exc:
            record["evidence_problems"].append(
                f"outputs/suite_items.jsonl line {line_number} is malformed: {exc}"
            )
            reasons.append(REASON_BUNDLE_READ_ERROR)
            continue
        if not isinstance(output, dict):
            record["evidence_problems"].append(
                f"outputs/suite_items.jsonl line {line_number} is not an object"
            )
            reasons.append(REASON_BUNDLE_READ_ERROR)
            continue
        item_index = output.get("item_index")
        if (
            isinstance(item_index, bool)
            or not isinstance(item_index, int)
            or item_index < 0
            or item_index >= len(manifest.items)
        ):
            reasons.append(REASON_ITEM_SET_MISMATCH)
            record["evidence_problems"].append(
                f"outputs/suite_items.jsonl line {line_number} has invalid "
                f"item_index={item_index!r}"
            )
            continue
        expected_item_id = manifest.items[item_index].item_id
        if output.get("item_id") != expected_item_id:
            reasons.append(REASON_ITEM_SET_MISMATCH)
            record["evidence_problems"].append(
                f"item_index={item_index} item_id={output.get('item_id')!r}, "
                f"expected {expected_item_id!r}"
            )
            continue
        if item_index in seen_output_indexes:
            reasons.append(REASON_ITEM_SET_MISMATCH)
            record["evidence_problems"].append(
                f"duplicate suite response hash for item_index={item_index}"
            )
            continue
        seen_output_indexes.add(item_index)
        output_status = output.get("status")
        if (
            not isinstance(output_status, str)
            or output_status not in _ELIGIBLE_ITEM_STATUSES
        ):
            reasons.append(REASON_ITEM_NOT_SUCCEEDED)
            record["evidence_problems"].append(
                f"outputs/suite_items.jsonl item_index={item_index} has "
                f"comparison-ineligible status={output_status!r}"
            )
            continue
        event_status = event_statuses.get(item_index)
        if event_status is not None and output_status != event_status:
            reasons.append(REASON_ITEM_STATUS_MISMATCH)
            record["evidence_problems"].append(
                f"item_index={item_index} item_id={expected_item_id!r} status differs "
                f"between outputs/suite_items.jsonl ({output_status!r}) and "
                f"item_end ({event_status!r})"
            )
            continue
        item_key = (item_index, expected_item_id)
        if event_status is not None:
            item_statuses[item_key] = output_status
        if "response_sha256" not in output:
            reasons.append(REASON_RESPONSE_HASH_MISSING)
            record["evidence_problems"].append(
                f"item_index={item_index} item_id={expected_item_id!r} lacks response_sha256"
            )
            continue
        response_hash = output["response_sha256"]
        if not isinstance(response_hash, str) or _SHA256_HEX.fullmatch(response_hash) is None:
            reasons.append(REASON_RESPONSE_HASH_MALFORMED)
            record["evidence_problems"].append(
                f"item_index={item_index} item_id={expected_item_id!r} "
                f"has malformed response_sha256={response_hash!r}"
            )
            continue
        response_text = output.get("response_text")
        if not isinstance(response_text, str):
            reasons.append(REASON_RESPONSE_TEXT_MALFORMED)
            record["evidence_problems"].append(
                f"item_index={item_index} item_id={expected_item_id!r} "
                "lacks string response_text"
            )
            continue
        derived_hash = hashlib.sha256(response_text.encode("utf-8")).hexdigest()
        if response_hash != derived_hash:
            reasons.append(REASON_RESPONSE_HASH_CONTENT_MISMATCH)
            record["evidence_problems"].append(
                f"item_index={item_index} response_sha256 does not match "
                f"UTF-8 response_text bytes: recorded {response_hash}, derived {derived_hash}"
            )
            continue
        event_hash = event_hashes.get(item_index)
        if event_hash is None:
            continue
        if response_hash != event_hash:
            reasons.append(REASON_RESPONSE_HASH_EVIDENCE_MISMATCH)
            record["evidence_problems"].append(
                f"item_index={item_index} response_sha256 differs between "
                f"outputs/suite_items.jsonl ({response_hash}) and item_end ({event_hash})"
            )
            continue
        items[item_key] = response_hash

    missing_output_indexes = sorted(set(range(len(manifest.items))) - seen_output_indexes)
    if missing_output_indexes:
        reasons.append(REASON_ITEM_SET_MISMATCH)
        record["evidence_problems"].append(
            f"suite response hashes omit manifest item_index values {missing_output_indexes}"
        )
    return items, item_statuses, reasons


def _single_response_hash(
    path: Path,
    record: dict[str, Any],
) -> tuple[dict[tuple[int, str], str], list[str]]:
    response_path = path / "outputs" / "response.txt"
    if not response_path.is_file():
        record["evidence_problems"].append("outputs/response.txt is missing")
        return {}, [REASON_RESPONSE_HASH_MISSING]
    response_hash = hashlib.sha256(response_path.read_bytes()).hexdigest()
    return {(0, "response"): response_hash}, []


def _item_status_counts(
    item_statuses: dict[tuple[int, str], str],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for status in sorted(item_statuses.values()):
        counts[status] = counts.get(status, 0) + 1
    return counts


def _comparability_reasons(
    inspections: list[_Inspection],
) -> tuple[list[str], list[dict[str, Any]]]:
    reasons: list[str] = []
    groups = {inspection.record["repetition_group"] for inspection in inspections}
    if len(groups) != 1:
        reasons.append(REASON_DIFFERENT_REPETITION_GROUPS)

    repetitions = [
        inspection.record["repetition_index"]
        for inspection in inspections
        if isinstance(inspection.record["repetition_index"], int)
    ]
    if len(set(repetitions)) != len(repetitions):
        reasons.append(REASON_DUPLICATE_REPETITION)

    normalized_config_hashes = {
        inspection.record["normalized_config_sha256"] for inspection in inspections
    }
    if len(normalized_config_hashes) != 1:
        reasons.append(REASON_DIFFERENT_CONFIGS)

    first_items = set(inspections[0].items)
    if not first_items:
        reasons.append(REASON_NO_ITEMS_TO_COMPARE)
    if any(set(inspection.items) != first_items for inspection in inspections[1:]):
        reasons.append(REASON_ITEM_SET_MISMATCH)

    sources = {inspection.record["response_hash_source"] for inspection in inspections}
    if len(sources) != 1:
        reasons.append(REASON_RESPONSE_EVIDENCE_PROFILE_MISMATCH)

    shared_status_items = set(inspections[0].item_statuses)
    for inspection in inspections[1:]:
        shared_status_items.intersection_update(inspection.item_statuses)
    item_status_mismatches: list[dict[str, Any]] = []
    for item_key in sorted(shared_status_items):
        observed = [
            {
                "path": inspection.record["path"],
                "run_id": inspection.record["run_id"],
                "status": inspection.item_statuses[item_key],
            }
            for inspection in inspections
        ]
        if len({entry["status"] for entry in observed}) > 1:
            item_index, item_id = item_key
            item_status_mismatches.append(
                {
                    "item_index": item_index,
                    "item_id": item_id,
                    "observed": observed,
                }
            )
    if item_status_mismatches:
        reasons.append(REASON_ITEM_STATUS_MISMATCH)
    return reasons, item_status_mismatches


def _normalized_config_sha256(config: dict[str, Any]) -> str:
    payload = json.dumps(
        config,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _identity_evidence(metadata: dict[str, Any]) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    for field_name in IDENTITY_FIELD_NAMES:
        value = _nested_value(metadata, _IDENTITY_FIELD_PATHS[field_name])
        if value is _MISSING:
            continue
        evidence[field_name] = _project_identity_value(field_name, value)
    return evidence


def _nested_value(root: Any, path: tuple[str, ...]) -> Any:
    value = root
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return _MISSING
        value = value[key]
    return value


def _project_identity_value(field_name: str, value: Any) -> Any:
    if field_name == "metadata.workload_provenance.tokenizer" and isinstance(
        value, dict
    ):
        return {key: value[key] for key in _TOKENIZER_IDENTITY_KEYS if key in value}
    if field_name == "metadata.workload_provenance.generator" and isinstance(
        value, dict
    ):
        return {key: value[key] for key in _GENERATOR_IDENTITY_KEYS if key in value}
    if field_name == "metadata.environment.python_packages" and isinstance(
        value, dict
    ):
        packages: dict[str, Any] = {}
        for package in _PACKAGE_IDENTITIES:
            if package not in value:
                continue
            record = value[package]
            packages[package] = (
                {
                    key: record[key]
                    for key in _PACKAGE_IDENTITY_KEYS
                    if isinstance(record, dict) and key in record
                }
                if isinstance(record, dict)
                else record
            )
        return packages
    return value


def _identity_field_classification(
    inspections: list[_Inspection],
) -> tuple[list[str], list[str], list[str], list[str]]:
    compared: list[str] = []
    absent: list[str] = []
    mismatched: list[str] = []
    malformed: list[str] = []
    for field_name in IDENTITY_FIELD_NAMES:
        present = [
            (inspection, inspection.identity_evidence[field_name])
            for inspection in inspections
            if field_name in inspection.identity_evidence
        ]
        if not present:
            absent.append(field_name)
            continue
        if field_name in _HASH_SHAPED_IDENTITY_FIELDS:
            bad = [
                (inspection, value)
                for inspection, value in present
                if not isinstance(value, str) or _SHA256_HEX.fullmatch(value) is None
            ]
            if bad:
                malformed.append(field_name)
                for inspection, value in bad:
                    inspection.record["evidence_problems"].append(
                        f"identity field {field_name} has malformed "
                        f"sha256 value {value!r}"
                    )
                continue
        if len(present) != len(inspections):
            mismatched.append(field_name)
            continue
        hashes = {_canonical_json_sha256(value) for _, value in present}
        if len(hashes) == 1:
            compared.append(field_name)
        else:
            mismatched.append(field_name)
    return compared, absent, mismatched, malformed


def _canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _reject_duplicate_json_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJsonKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _check_gate_json_evidence_for_duplicate_keys(path: Path) -> None:
    for relative in (
        "config.json",
        "metadata.json",
        "summary_metrics.json",
        "suite_manifest.json",
    ):
        evidence_path = path / relative
        if not evidence_path.is_file():
            continue
        _load_json_without_duplicate_keys(evidence_path, relative)
    for relative in ("events.jsonl", "outputs/suite_items.jsonl"):
        evidence_path = path / relative
        if not evidence_path.is_file():
            continue
        _load_jsonl_without_duplicate_keys(evidence_path, relative)


def _load_json_without_duplicate_keys(path: Path, label: str) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text, object_pairs_hook=_reject_duplicate_json_pairs)
    except _DuplicateJsonKeyError as exc:
        raise _DuplicateJsonKeyError(f"{label}: {exc}") from exc


def _load_jsonl_without_duplicate_keys(path: Path, label: str) -> None:
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            json.loads(line, object_pairs_hook=_reject_duplicate_json_pairs)
        except _DuplicateJsonKeyError as exc:
            raise _DuplicateJsonKeyError(
                f"{label} line {line_number}: {exc}"
            ) from exc


def _refused(
    records: list[dict[str, Any]],
    reason_codes: list[str],
    *,
    identity_fields_compared: list[str] | None = None,
    identity_fields_absent: list[str] | None = None,
    identity_fields_malformed: list[str] | None = None,
    item_status_mismatches: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": VERDICT_REFUSED,
        "reason_codes": sorted(set(reason_codes)),
        "bundle_count": len(records),
        "bundles": records,
        "comparison": None,
        "mismatches": [],
        "item_status_mismatches": item_status_mismatches or [],
        "refusal_message": "inputs are not comparable strict-valid repetition bundles",
        "identity_fields_compared": identity_fields_compared or [],
        "identity_fields_absent": identity_fields_absent or [],
        "identity_fields_malformed": identity_fields_malformed or [],
    }
