"""Hash-bound, coverage-complete whole-window idle-admission verdict join.

The verdict is a claim barrier, not an append-log preference.  A consumer must
prove that one internally consistent row covers the exact evaluation basis it
is about to use.  Different bases coexist in append-only history; file order
never grants a later row authority to erase an earlier failure.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from joulewise.aggregate import student_t_critical_95
from joulewise.idle_admission import (
    ADAPTER_CONTINUITY_SCHEMA,
    IdleAdmissionExtension,
    NEG8_BRACKET_SCHEMA,
    Neg8BracketPolicy,
    evaluate_adapter_wattage_continuity,
    evaluate_cpu_idle_admission,
    evaluate_neg8_bracket,
    extract_adapter_observation,
)
from joulewise.bundle import sanitize_id_component
from joulewise.bundle_read import BundleReader, BundleReadError
from joulewise.environment_admission import (
    current_environment_refusals,
    environment_admission_refusals,
)
from joulewise.calibration_bracketing import calibration_bracket_for_bundles
from joulewise.reduce import _verify_instrument_calibration
from joulewise.schemas import BenchmarkConfig, CampaignPolicy

WHOLE_WINDOW_SCHEMA = "joulewise.idle_admission_whole_window_verdict.v1"
IDLE_ADMISSION_CORE_SCHEMA = "joulewise.idle_admission_core_verdict.v1"
WHOLE_WINDOW_PROVENANCE_SCHEMA = (
    "joulewise.idle_admission_whole_window_provenance.v1"
)
WHOLE_WINDOW_EVALUATION_BASIS_SCHEMA = (
    "joulewise.idle_admission_evaluation_basis.v1"
)
OCCURRENCE_SUPERSESSION_SCHEMA = (
    "joulewise.campaign_occurrence_supersession.v1"
)
CURRENT_MINT_REDUCER_VERSIONS = frozenset({"0.5.2", "0.6.2"})
NEG8_DRIFT_BOUND_SCHEMA = "joulewise.neg8_drift_bound.v1"
NEG8_REFERENCE_CORPUS_SCHEMA = "joulewise.neg8_reference_corpus.v1"
NEG8_POINT_DRIFT_ESTIMAND = (
    "abs(end_point_gross_j-start_point_gross_j)"
)
NEG8_DRIFT_ESTIMATOR_ID = "d054_point_contrast_guard_v1"
NEG8_DRIFT_MINIMUM_N = 10
CONDITION_NEG8_DRIFT_BOUND_UNDERIVED = "neg8_drift_bound_underived"


def validate_attempt_ledger(*args: Any, **kwargs: Any) -> Any:
    """Lazily delegate to the single authoritative registry validator."""

    # ``analysis_engine.inputs`` consumes whole-window results, so importing
    # the package-level registry while this module initializes creates a cycle.
    from joulewise.analysis_engine.registry import validate_attempt_ledger as shared

    return shared(*args, **kwargs)


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _sha256_text(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _finite_number(value: Any, *, positive: bool = False) -> float | None:
    if (
        isinstance(value, bool)
        or not isinstance(value, int | float)
        or not math.isfinite(float(value))
    ):
        return None
    number = float(value)
    if positive and number <= 0.0:
        return None
    return number


def build_neg8_drift_bound_artifact(
    *,
    corpus_id: str,
    condition_id: str,
    manifest_sha256: str,
    scientific_config_sha256: str,
    members: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build the predeclared D-054-style point-contrast guard artifact."""

    if not isinstance(corpus_id, str) or not corpus_id.strip():
        raise ValueError("NEG-8 reference corpus_id must be non-empty")
    if not isinstance(condition_id, str) or not condition_id.strip():
        raise ValueError("NEG-8 reference condition_id must be non-empty")
    if not _sha256_text(manifest_sha256):
        raise ValueError("NEG-8 reference manifest_sha256 must be lowercase sha256")
    if not _sha256_text(scientific_config_sha256):
        raise ValueError(
            "NEG-8 reference scientific_config_sha256 must be lowercase sha256"
        )
    normalized_members: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for member in members:
        if not isinstance(member, Mapping) or set(member) != {
            "bundle_id",
            "point_gross_j",
            "bundle_evidence_sha256",
        }:
            raise ValueError(
                "NEG-8 reference members require bundle_id, point_gross_j, "
                "and bundle_evidence_sha256"
            )
        bundle_id = member.get("bundle_id")
        point = _finite_number(member.get("point_gross_j"), positive=True)
        evidence_sha = member.get("bundle_evidence_sha256")
        if (
            not isinstance(bundle_id, str)
            or not bundle_id
            or bundle_id in seen_ids
            or point is None
            or not _sha256_text(evidence_sha)
        ):
            raise ValueError("NEG-8 reference corpus member is invalid or duplicated")
        seen_ids.add(bundle_id)
        normalized_members.append(
            {
                "bundle_id": bundle_id,
                "point_gross_j": point,
                "bundle_evidence_sha256": evidence_sha,
            }
        )
    n = len(normalized_members)
    if n < NEG8_DRIFT_MINIMUM_N:
        raise ValueError(
            f"NEG-8 reference corpus requires n >= {NEG8_DRIFT_MINIMUM_N}"
        )
    points = [member["point_gross_j"] for member in normalized_members]
    sample_range = max(points) - min(points)
    sample_stddev = statistics.stdev(points)
    t_critical = student_t_critical_95(n - 1)
    prediction = t_critical * sample_stddev * math.sqrt(2.0)
    bound = max(sample_range, prediction)
    payload = {
        "schema_version": NEG8_DRIFT_BOUND_SCHEMA,
        "estimand": NEG8_POINT_DRIFT_ESTIMAND,
        "reference_corpus": {
            "schema_version": NEG8_REFERENCE_CORPUS_SCHEMA,
            "corpus_id": corpus_id,
            "freeze_status": "settled_reference",
            "condition_id": condition_id,
            "manifest_sha256": manifest_sha256,
            "scientific_config_sha256": scientific_config_sha256,
            "member_ids": [member["bundle_id"] for member in normalized_members],
            "members": normalized_members,
        },
        "estimator": {
            "id": NEG8_DRIFT_ESTIMATOR_ID,
            "minimum_n": NEG8_DRIFT_MINIMUM_N,
            "n": n,
            "sample_range_j": sample_range,
            "sample_stddev_j": sample_stddev,
            "student_t_critical_95": t_critical,
            "prediction_two_point_j": prediction,
            "formula": (
                "max(sample_range_j,"
                "t_0.975,n-1*sample_stddev_j*sqrt(2))"
            ),
        },
        "bound_j": bound,
    }
    return {**payload, "derivation_sha256": canonical_sha256(payload)}


def validate_neg8_drift_bound_artifact(value: Any) -> bool:
    """Validate the seal, corpus provenance, and estimator arithmetic."""

    if not isinstance(value, Mapping) or set(value) != {
        "schema_version",
        "estimand",
        "reference_corpus",
        "estimator",
        "bound_j",
        "derivation_sha256",
    }:
        return False
    corpus = value.get("reference_corpus")
    estimator = value.get("estimator")
    if (
        value.get("schema_version") != NEG8_DRIFT_BOUND_SCHEMA
        or value.get("estimand") != NEG8_POINT_DRIFT_ESTIMAND
        or not isinstance(corpus, Mapping)
        or not isinstance(estimator, Mapping)
        or set(corpus)
        != {
            "schema_version",
            "corpus_id",
            "freeze_status",
            "condition_id",
            "manifest_sha256",
            "scientific_config_sha256",
            "member_ids",
            "members",
        }
        or corpus.get("schema_version") != NEG8_REFERENCE_CORPUS_SCHEMA
        or corpus.get("freeze_status") != "settled_reference"
        or set(estimator)
        != {
            "id",
            "minimum_n",
            "n",
            "sample_range_j",
            "sample_stddev_j",
            "student_t_critical_95",
            "prediction_two_point_j",
            "formula",
        }
    ):
        return False
    members = corpus.get("members")
    member_ids = corpus.get("member_ids")
    if not isinstance(members, list) or not isinstance(member_ids, list):
        return False
    try:
        expected = build_neg8_drift_bound_artifact(
            corpus_id=corpus.get("corpus_id"),
            condition_id=corpus.get("condition_id"),
            manifest_sha256=corpus.get("manifest_sha256"),
            scientific_config_sha256=corpus.get("scientific_config_sha256"),
            members=members,
        )
    except (TypeError, ValueError, statistics.StatisticsError):
        return False
    return (
        member_ids == [member.get("bundle_id") for member in members]
        and dict(value) == expected
    )


def load_neg8_drift_bound_artifact(path: str | Path | None) -> dict[str, Any] | None:
    """Load a governed derived bound; malformed or absent artifacts are underived."""

    if path is None:
        return None
    try:
        raw = Path(path).read_bytes()
        from joulewise.determinism_gate import (  # noqa: PLC0415
            _reject_duplicate_json_pairs,
        )

        value = json.loads(raw, object_pairs_hook=_reject_duplicate_json_pairs)
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    return dict(value) if validate_neg8_drift_bound_artifact(value) else None


def _admissible_energy_set(value: Any) -> tuple[float, float, float] | None:
    if not isinstance(value, Mapping):
        return None
    fields = (
        _finite_number(value.get("point_j"), positive=True),
        _finite_number(value.get("lower_j"), positive=True),
        _finite_number(value.get("upper_j"), positive=True),
    )
    if any(item is None for item in fields):
        return None
    point, lower, upper = (float(item) for item in fields)
    return (point, lower, upper) if lower <= point <= upper else None


def evaluate_neg8_point_drift(
    start_gross_j: Any,
    end_gross_j: Any,
    policy: Neg8BracketPolicy,
    drift_bound_artifact: Any,
    *,
    start_idle_subtracted_j: Any = None,
    end_idle_subtracted_j: Any = None,
) -> dict[str, Any]:
    """Gate NEG-8 on point drift and retain envelope corners as diagnostics."""

    conditions: set[str] = set()
    start_set = _admissible_energy_set(start_gross_j)
    end_set = _admissible_energy_set(end_gross_j)
    artifact = (
        dict(drift_bound_artifact)
        if validate_neg8_drift_bound_artifact(drift_bound_artifact)
        else None
    )
    if artifact is None:
        conditions.add(CONDITION_NEG8_DRIFT_BOUND_UNDERIVED)
    if start_gross_j is None or end_gross_j is None:
        conditions.add("neg8_bracket_missing")
    elif start_set is None or end_set is None:
        conditions.add("neg8_bracket_reference_invalid")

    point_delta: float | None = None
    point_relative: float | None = None
    corner_delta: float | None = None
    corner_relative: float | None = None
    if start_set is not None and end_set is not None:
        start_point, start_lower, start_upper = start_set
        end_point, end_lower, end_upper = end_set
        point_delta = abs(end_point - start_point)
        point_relative = point_delta / start_point
        corners = [
            (start_edge, end_edge)
            for start_edge in (start_lower, start_upper)
            for end_edge in (end_lower, end_upper)
        ]
        corner_delta = max(
            abs(end_edge - start_edge) for start_edge, end_edge in corners
        )
        corner_relative = max(
            abs(end_edge - start_edge) / start_edge
            for start_edge, end_edge in corners
        )
        if artifact is not None and point_delta > artifact["bound_j"]:
            # Retain the registered v1 failure word while changing the governed
            # estimand.  The additive estimand field disambiguates new rows.
            conditions.add("neg8_bracket_abs_delta_exceeded")

    idle_start = _finite_number(start_idle_subtracted_j)
    idle_end = _finite_number(end_idle_subtracted_j)
    idle_delta = (
        abs(idle_end - idle_start)
        if idle_start is not None and idle_end is not None
        else None
    )
    evidence_failure = conditions & {
        CONDITION_NEG8_DRIFT_BOUND_UNDERIVED,
        "neg8_bracket_missing",
        "neg8_bracket_reference_invalid",
    }
    if evidence_failure:
        decision = "failed" if policy.require_bracket else "flagged"
    elif conditions:
        decision = "failed"
    else:
        decision = "passed"
    return {
        "schema_version": NEG8_BRACKET_SCHEMA,
        "estimand": NEG8_POINT_DRIFT_ESTIMAND,
        "decision": decision,
        "passed": decision == "passed",
        "conditions": sorted(conditions),
        "start_gross_j": start_set[0] if start_set is not None else None,
        "end_gross_j": end_set[0] if end_set is not None else None,
        "start_admissible_set_j": (
            {
                "point_j": start_set[0],
                "lower_j": start_set[1],
                "upper_j": start_set[2],
            }
            if start_set is not None
            else None
        ),
        "end_admissible_set_j": (
            {
                "point_j": end_set[0],
                "lower_j": end_set[1],
                "upper_j": end_set[2],
            }
            if end_set is not None
            else None
        ),
        "abs_delta_j": point_delta,
        "rel_delta": point_relative,
        "corner_abs_delta_j": corner_delta,
        "corner_rel_delta": corner_relative,
        "corner_statistic_role": "diagnostic_not_gating",
        "idle_subtracted_companion": {
            "start_point_j": idle_start,
            "end_point_j": idle_end,
            "abs_delta_j": idle_delta,
            "role": "diagnostic_not_gating",
        },
        # The v1 sidecar fields remain recorded for legacy wire compatibility;
        # neither numeric tolerance gates this amended estimand.
        "policy": {
            "require_bracket": policy.require_bracket,
            "max_abs_delta_j": policy.max_abs_delta_j,
            "max_rel_delta": policy.max_rel_delta,
        },
        "drift_bound_artifact": artifact,
    }


def source_manifest_descriptors(
    runs_root: Path, manifest_paths: Sequence[str | Path]
) -> list[dict[str, str]]:
    """Bind every source campaign manifest by safe runs-root-relative path."""

    root = Path(runs_root).resolve()
    result: list[dict[str, str]] = []
    for value in manifest_paths:
        path = Path(value)
        if not path.is_absolute():
            path = root / path
        resolved = path.resolve()
        if resolved == root or root not in resolved.parents:
            raise ValueError(f"whole-window source manifest escapes runs root: {value}")
        raw = resolved.read_bytes()
        result.append(
            {
                "path": resolved.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    return sorted(result, key=lambda row: row["path"])


def build_row_provenance(
    *,
    policy_sha256: str,
    bundle_ids: Sequence[str],
    source_manifests: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    members = sorted(bundle_ids)
    return {
        "schema_version": WHOLE_WINDOW_PROVENANCE_SCHEMA,
        "policy_sha256": policy_sha256,
        "membership_sha256": canonical_sha256(members),
        "source_campaign_manifests": [dict(row) for row in source_manifests],
    }


def build_evaluation_basis(
    *,
    policy_sha256: str,
    member_occurrences: Sequence[Mapping[str, Any]],
    calibration_bracket: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Bind one verdict to physical member bytes and its calibration pair."""

    occurrences = sorted(
        (dict(value) for value in member_occurrences),
        key=lambda value: (
            str(value.get("bundle_id")),
            str(value.get("bundle_path")),
        ),
    )
    bracket_set = {
        "pre": (
            dict(calibration_bracket["pre"])
            if isinstance(calibration_bracket, Mapping)
            and isinstance(calibration_bracket.get("pre"), Mapping)
            else None
        ),
        "post": (
            dict(calibration_bracket["post"])
            if isinstance(calibration_bracket, Mapping)
            and isinstance(calibration_bracket.get("post"), Mapping)
            else None
        ),
    }
    payload = {
        "schema_version": WHOLE_WINDOW_EVALUATION_BASIS_SCHEMA,
        "policy_sha256": policy_sha256,
        "member_occurrences": occurrences,
        "calibration_bracket_set": bracket_set,
    }
    return {**payload, "sha256": canonical_sha256(payload)}


def supersession_entry_sha256(entry: Mapping[str, Any]) -> str:
    return canonical_sha256(
        {key: value for key, value in entry.items() if key != "entry_sha256"}
    )


def _safe_source_path(root: Path, text: Any) -> Path | None:
    if not isinstance(text, str) or not text:
        return None
    pure = PurePosixPath(text)
    if pure.is_absolute() or ".." in pure.parts:
        return None
    try:
        path = (root / Path(*pure.parts)).resolve()
        resolved_root = root.resolve()
    except (OSError, RuntimeError):
        return None
    if path == resolved_root or resolved_root not in path.parents:
        return None
    return path


def ordinary_present_bundle_paths(runs_root: Path, bundle_id: str) -> list[Path]:
    """Find canonical and moved-in-root copies of one ordinary bundle."""

    root = Path(runs_root).resolve()
    result: list[Path] = []
    try:
        candidates = sorted(path for path in root.iterdir() if path.is_dir())
    except OSError:
        return result
    for path in candidates:
        if path.name == bundle_id:
            result.append(path)
            continue
        if not (path / "summary_metrics.json").is_file():
            continue
        config = _read_json_object(path / "config.json")
        run_id = config.get("run_id") if isinstance(config, Mapping) else None
        if (
            isinstance(run_id, str)
            and sanitize_id_component(run_id) == bundle_id
        ):
            result.append(path)
    return result


def _occurrence_descriptor_valid(
    value: Any, runs_root: Path, *, bundle_id: str
) -> bool:
    if not isinstance(value, Mapping) or value.get("bundle_id") != bundle_id:
        return False
    source = value.get("source_manifest")
    member_index = value.get("member_index")
    bundle_index = value.get("bundle_index")
    if (
        not isinstance(source, Mapping)
        or isinstance(member_index, bool)
        or not isinstance(member_index, int)
        or member_index < 0
        or isinstance(bundle_index, bool)
        or not isinstance(bundle_index, int)
        or bundle_index < 0
    ):
        return False
    path = _safe_source_path(runs_root, source.get("path"))
    expected_sha = source.get("sha256")
    try:
        raw = path.read_bytes() if path is not None else None
        manifest = json.loads(raw) if raw is not None else None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    if (
        raw is None
        or not isinstance(expected_sha, str)
        or hashlib.sha256(raw).hexdigest() != expected_sha
        or not isinstance(manifest, Mapping)
    ):
        return False
    members = manifest.get("members")
    if not isinstance(members, list) or member_index >= len(members):
        return False
    member = members[member_index]
    ids = member.get("bundle_ids") if isinstance(member, Mapping) else None
    return bool(
        isinstance(member, Mapping)
        and member.get("execution") == "invoked"
        and isinstance(ids, list)
        and bundle_index < len(ids)
        and ids[bundle_index] == bundle_id
    )


def validate_occurrence_supersession_entry(
    entry: Mapping[str, Any], runs_root: Path
) -> bool:
    """Validate an explicit operator supersession artifact from current bytes."""

    root = Path(runs_root).resolve()
    bundle_id = entry.get("bundle_id")
    superseded = entry.get("superseded_occurrences")
    quarantine = entry.get("quarantine")
    if (
        entry.get("schema_version") != OCCURRENCE_SUPERSESSION_SCHEMA
        or entry.get("record_type") != "campaign_occurrence_supersession"
        or entry.get("runs_root") != str(root)
        or not isinstance(bundle_id, str)
        or not bundle_id
        or not isinstance(entry.get("reason"), str)
        or not entry["reason"].strip()
        or not isinstance(superseded, list)
        or not superseded
        or not isinstance(quarantine, Mapping)
        or entry.get("entry_sha256") != supersession_entry_sha256(entry)
    ):
        return False
    selected = entry.get("selected_occurrence")
    if not _occurrence_descriptor_valid(selected, root, bundle_id=bundle_id):
        return False
    if any(
        not _occurrence_descriptor_valid(value, root, bundle_id=bundle_id)
        for value in superseded
    ):
        return False
    occurrence_hashes = [canonical_sha256(value) for value in superseded]
    if (
        len(set(occurrence_hashes)) != len(occurrence_hashes)
        or canonical_sha256(selected) in occurrence_hashes
    ):
        return False
    canonical = root / bundle_id
    present = ordinary_present_bundle_paths(root, bundle_id)
    if present != [canonical] or not canonical.is_dir():
        return False
    quarantine_path_text = quarantine.get("path")
    if not isinstance(quarantine_path_text, str) or not quarantine_path_text:
        return False
    try:
        quarantine_path = Path(quarantine_path_text).resolve(strict=True)
    except (OSError, RuntimeError):
        return False
    if quarantine_path == root or root in quarantine_path.parents:
        return False
    for name, field in (
        ("config.json", "config_sha256"),
        ("metadata.json", "metadata_sha256"),
        ("summary_metrics.json", "summary_sha256"),
    ):
        expected = quarantine.get(field)
        try:
            raw = (quarantine_path / name).read_bytes()
        except OSError:
            return False
        if (
            not isinstance(expected, str)
            or len(expected) != 64
            or hashlib.sha256(raw).hexdigest() != expected
        ):
            return False
    return True


def _evidence_map(path: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    if not path.is_dir():
        return result
    for candidate in sorted(path.glob("*.json")):
        raw = candidate.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest in result:
            raise ValueError("duplicate attempt evidence digest")
        result[digest] = raw
    return result


def validated_attempt_selection(
    selection: Mapping[str, Any], runs_root: Path
) -> set[str] | None:
    """Re-run the authoritative attempt-ledger validator at consumption."""

    ledger = _safe_source_path(runs_root, selection.get("attempt_ledger_path"))
    manifest_path = _safe_source_path(
        runs_root, selection.get("analysis_manifest_path")
    )
    if ledger is None or manifest_path is None:
        return None
    try:
        ledger_raw = ledger.read_bytes()
        manifest_raw = manifest_path.read_bytes()
        manifest = json.loads(manifest_raw)
        rows = [
            json.loads(line)
            for line in ledger_raw.decode("utf-8").splitlines()
            if line.strip()
        ]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if (
        hashlib.sha256(ledger_raw).hexdigest()
        != selection.get("attempt_ledger_sha256")
        or hashlib.sha256(manifest_raw).hexdigest()
        != selection.get("analysis_manifest_sha256")
        or not isinstance(manifest, Mapping)
        or not rows
        or any(not isinstance(row, Mapping) for row in rows)
    ):
        return None
    evidence_root = ledger.parent
    try:
        receipts = _evidence_map(evidence_root / "dispatch_receipts")
        strict_evidence = _evidence_map(evidence_root / "strict_validation")
        finalized: dict[tuple[str, int, str], Path] = {}
        for row in rows:
            run_id = row.get("run_id")
            entry_id = row.get("entry_id")
            ordinal = row.get("attempt_ordinal")
            if not isinstance(run_id, str):
                continue
            if (
                not isinstance(entry_id, str)
                or isinstance(ordinal, bool)
                or not isinstance(ordinal, int)
            ):
                return None
            path = (
                runs_root
                / "axi_attempt_bundles"
                / str(manifest.get("manifest_id"))
                / sanitize_id_component(entry_id)
                / f"a{ordinal}"
                / sanitize_id_component(run_id)
            )
            finalized[(entry_id, ordinal, run_id)] = path
        selected = validate_attempt_ledger(
            rows,
            manifest,
            receipts=receipts,
            strict_evidence=strict_evidence,
            finalized_bundles=finalized,
        )
    except (OSError, TypeError, ValueError):
        return None
    expected_descriptors = {
        (
            entry_id,
            row.get("attempt_ordinal"),
            row.get("run_id"),
            (
                f"{sanitize_id_component(entry_id)}__a{row.get('attempt_ordinal')}__"
                f"{sanitize_id_component(str(row.get('run_id')))}"
            ),
            (
                Path("axi_attempt_bundles")
                / str(manifest.get("manifest_id"))
                / sanitize_id_component(entry_id)
                / f"a{row.get('attempt_ordinal')}"
                / sanitize_id_component(str(row.get("run_id")))
            ).as_posix(),
        )
        for entry_id, row in selected.items()
        if row is not None
    }
    descriptors = selection.get("selected_bundles")
    if not isinstance(descriptors, list):
        return None
    actual: set[tuple[Any, Any, Any, Any, Any]] = set()
    selected_ids: set[str] = set()
    selected_paths: set[str] = set()
    for descriptor in descriptors:
        if not isinstance(descriptor, Mapping):
            return None
        identity = (
            descriptor.get("entry_id"),
            descriptor.get("attempt_ordinal"),
            descriptor.get("run_id"),
            descriptor.get("bundle_id"),
            descriptor.get("path"),
        )
        bundle_id = descriptor.get("bundle_id")
        path_text = descriptor.get("path")
        if (
            identity in actual
            or not isinstance(bundle_id, str)
            or bundle_id in selected_ids
            or not isinstance(path_text, str)
            or path_text in selected_paths
        ):
            return None
        actual.add(identity)
        selected_ids.add(bundle_id)
        selected_paths.add(path_text)
    if actual != expected_descriptors:
        return None
    quarantined = selection.get("quarantined_attempts")
    if not isinstance(quarantined, list):
        return None
    expected_quarantined = {
        (row.get("entry_id"), row.get("attempt_ordinal"), row.get("run_id"))
        for row in rows
        if row.get("eligible_for_analysis") is False
    }
    actual_quarantined: set[tuple[Any, Any, Any]] = set()
    for row in quarantined:
        if (
            not isinstance(row, Mapping)
            or row.get("properly_quarantined") is not True
            or row.get("recovery_continuity_verified") is not True
        ):
            return None
        identity = (
            row.get("entry_id"),
            row.get("attempt_ordinal"),
            row.get("run_id"),
        )
        if identity in actual_quarantined:
            return None
        actual_quarantined.add(identity)
    if actual_quarantined != expected_quarantined or {
        identity[:3] for identity in actual
    } & actual_quarantined:
        return None
    return selected_ids


def _manifest_members(
    value: Mapping[str, Any], runs_root: Path
) -> set[str] | None:
    selection = value.get("attempt_ledger_selection")
    if isinstance(selection, Mapping):
        validated_selected = validated_attempt_selection(selection, runs_root)
        if validated_selected is None:
            return None
        selected = selection.get("selected_bundle_ids")
        if not isinstance(selected, list) or any(
            not isinstance(item, str) or not item for item in selected
        ):
            return None
        if canonical_sha256(sorted(selected)) != selection.get(
            "selected_membership_sha256"
        ):
            return None
        if selection.get("schema_version") != "joulewise.attempt_ledger_selection.v1":
            return None
        ledger = _safe_source_path(runs_root, selection.get("attempt_ledger_path"))
        ledger_sha = selection.get("attempt_ledger_sha256")
        try:
            ledger_raw = ledger.read_bytes() if ledger is not None else None
        except OSError:
            return None
        if (
            ledger_raw is None
            or not isinstance(ledger_sha, str)
            or hashlib.sha256(ledger_raw).hexdigest() != ledger_sha
        ):
            return None
        descriptors = selection.get("selected_bundles")
        if not isinstance(descriptors, list) or len(descriptors) != len(selected):
            return None
        descriptor_ids: set[str] = set()
        for descriptor in descriptors:
            if not isinstance(descriptor, Mapping):
                return None
            bundle_id = descriptor.get("bundle_id")
            bundle_path = _safe_source_path(runs_root, descriptor.get("path"))
            if (
                not isinstance(bundle_id, str)
                or not bundle_id
                or bundle_id in descriptor_ids
                or bundle_path is None
                or not bundle_path.is_dir()
            ):
                return None
            descriptor_ids.add(bundle_id)
        quarantined = selection.get("quarantined_attempts")
        if isinstance(quarantined, list) and any(
            not isinstance(row, Mapping)
            or row.get("properly_quarantined") is not True
            or row.get("recovery_continuity_verified") is not True
            for row in quarantined
        ):
            return None
        if descriptor_ids != set(selected) or descriptor_ids != validated_selected:
            return None
        return set(selected)
    members = value.get("members")
    if not isinstance(members, list):
        return None
    result: set[str] = set()
    duplicate_ids: set[str] = set()
    for row in members:
        if not isinstance(row, Mapping) or row.get("execution") != "invoked":
            continue
        bundle_ids = row.get("bundle_ids")
        if not isinstance(bundle_ids, list):
            return None
        if any(not isinstance(item, str) or not item for item in bundle_ids):
            return None
        # G7(a): on the current strict path invoked occurrences are evidence,
        # not a mathematical set.  The check below deliberately leaves frozen
        # replay's committed set-collapse behavior untouched.
        duplicate_ids.update(
            item for item in bundle_ids if bundle_ids.count(item) > 1 or item in result
        )
        result.update(bundle_ids)
    if duplicate_ids and any(
        _current_strict_summary(
            _read_json_object(runs_root / bundle_id / "summary_metrics.json")
        )
        for bundle_id in result
    ):
        return None
    return result


def _neg8_position(role: Any, sentinel_position: Any) -> str | None:
    """Interpret the three campaign-manifest NEG-8 role spellings."""

    if role == "neg8_daily_reference_start":
        return "start" if sentinel_position in (None, "start") else "invalid"
    if role == "neg8_daily_reference_end":
        return "end" if sentinel_position in (None, "end") else "invalid"
    if role == "neg8_daily_reference":
        return sentinel_position if sentinel_position in {"start", "end"} else "invalid"
    return None


def _read_json_object(path: Path) -> Mapping[str, Any] | None:
    try:
        value = json.loads(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, Mapping) else None


def _summary_reducer_version(summary: Any) -> str | None:
    provenance = summary.get("summary_provenance") if isinstance(summary, Mapping) else None
    value = provenance.get("reducer_version") if isinstance(provenance, Mapping) else None
    return value if isinstance(value, str) else None


def _current_strict_summary(summary: Any) -> bool:
    """Identify current-mint, non-mock summaries that can bear strict claims."""

    quality = summary.get("measurement_quality") if isinstance(summary, Mapping) else None
    telemetry_source = (
        quality.get("telemetry_source") if isinstance(quality, Mapping) else None
    )
    return (
        _summary_reducer_version(summary) in CURRENT_MINT_REDUCER_VERSIONS
        and telemetry_source != "mock"
    )


def _gross_fields(summary: Any) -> dict[str, float] | None:
    if not isinstance(summary, Mapping):
        return None
    gross = summary.get("gross_energy_j")
    envelopes = summary.get("energy_anchor_shift_envelopes")
    envelope = (
        envelopes.get("/gross_energy_j") if isinstance(envelopes, Mapping) else None
    )
    if not isinstance(envelope, Mapping):
        return None
    fields = (
        gross,
        envelope.get("point_j"),
        envelope.get("lower_j"),
        envelope.get("upper_j"),
    )
    if any(
        isinstance(value, bool)
        or not isinstance(value, int | float)
        or not math.isfinite(float(value))
        for value in fields
    ):
        return None
    gross_value, point, lower, upper = (float(value) for value in fields)
    if (
        not math.isclose(point, gross_value, rel_tol=1e-9, abs_tol=1e-12)
        or lower <= 0.0
        or not lower <= point <= upper
    ):
        return None
    return {"point_j": point, "lower_j": lower, "upper_j": upper}


def _gross_energy_evidence(
    bundle_path: Path,
) -> tuple[dict[str, float] | None, str | None]:
    """Re-derive current NEG-8 energy from primary bytes; replay stays stored."""

    stored_summary = _read_json_object(bundle_path / "summary_metrics.json")
    stored = _gross_fields(stored_summary)
    reducer_version = _summary_reducer_version(stored_summary)
    if not _current_strict_summary(stored_summary):
        return stored, None if stored is not None else "provenance"
    try:
        # Deliberately output-free: reduce_bundle is pure over the bundle and
        # returns an in-memory summary.  Minutes-scale claim verification cost
        # is accepted for primary-evidence NEG-8 re-derivation.
        from joulewise.reduce import reduce_bundle

        reduced = reduce_bundle(bundle_path, reducer_version=reducer_version).to_dict()
    except Exception:  # noqa: BLE001 - any reducer/evidence failure refuses.
        return None, "provenance"
    fresh = _gross_fields(reduced)
    prechecks = reduced.get("window_evidence_precheck")
    gross_gate = None
    if isinstance(prechecks, Mapping):
        gross_gate = prechecks.get("gross_request")
        if not isinstance(gross_gate, Mapping):
            gross_gate = prechecks.get("gross_batch_group")
    if (
        reduced.get("status") != "succeeded"
        or fresh is None
        or not isinstance(gross_gate, Mapping)
        or gross_gate.get("eligible") is not True
    ):
        return None, "provenance"
    if stored is None or any(
        not math.isclose(
            stored[field], fresh[field], rel_tol=1e-9, abs_tol=1e-9
        )
        for field in ("point_j", "lower_j", "upper_j")
    ):
        return None, "conflict"
    return fresh, None


def _bundle_evidence_sha256(bundle_path: Path) -> str:
    """Seal the complete regular-file inventory used by a reference member."""

    inventory: dict[str, str] = {}
    for path in sorted(bundle_path.rglob("*")):
        if path.is_symlink():
            raise ValueError("NEG-8 reference bundle inventory contains a symlink")
        if path.is_file():
            inventory[path.relative_to(bundle_path).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    if not inventory:
        raise ValueError("NEG-8 reference bundle inventory is empty")
    return canonical_sha256(inventory)


def mint_neg8_drift_bound_artifact(
    runs_root: Path, corpus_manifest_path: Path
) -> dict[str, Any]:
    """Derive a sealed NEG-8 point-drift bound from a settled corpus manifest."""

    root = Path(runs_root).resolve()
    manifest_path = Path(corpus_manifest_path)
    raw = manifest_path.read_bytes()
    try:
        from joulewise.determinism_gate import (  # noqa: PLC0415
            _reject_duplicate_json_pairs,
        )

        manifest = json.loads(raw, object_pairs_hook=_reject_duplicate_json_pairs)
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError("NEG-8 reference corpus manifest is invalid JSON") from exc
    if not isinstance(manifest, Mapping) or set(manifest) != {
        "schema_version",
        "corpus_id",
        "freeze_status",
        "condition_id",
        "members",
    }:
        raise ValueError("NEG-8 reference corpus manifest has invalid keys")
    if (
        manifest.get("schema_version") != NEG8_REFERENCE_CORPUS_SCHEMA
        or manifest.get("freeze_status") != "settled_reference"
    ):
        raise ValueError("NEG-8 reference corpus is not governed and settled")
    members = manifest.get("members")
    if not isinstance(members, list) or len(members) < NEG8_DRIFT_MINIMUM_N:
        raise ValueError(
            f"NEG-8 reference corpus requires n >= {NEG8_DRIFT_MINIMUM_N}"
        )

    evidence_members: list[dict[str, Any]] = []
    scientific_identity: str | None = None
    seen_ids: set[str] = set()
    for member in members:
        if not isinstance(member, Mapping) or set(member) != {
            "bundle_id",
            "bundle_path",
        }:
            raise ValueError("NEG-8 corpus member descriptor has invalid keys")
        bundle_id = member.get("bundle_id")
        bundle_path = _safe_source_path(root, member.get("bundle_path"))
        if (
            not isinstance(bundle_id, str)
            or not bundle_id
            or bundle_id in seen_ids
            or bundle_path is None
            or not bundle_path.is_dir()
        ):
            raise ValueError("NEG-8 corpus member is invalid, duplicated, or unsafe")
        seen_ids.add(bundle_id)
        summary = _read_json_object(bundle_path / "summary_metrics.json")
        if not _current_strict_summary(summary):
            raise ValueError(
                f"NEG-8 corpus member {bundle_id} is not a current strict mint"
            )
        identity, canonical = _scientific_config_identity(bundle_path)
        if identity is None or not canonical:
            raise ValueError(
                f"NEG-8 corpus member {bundle_id} is not the canonical condition"
            )
        if scientific_identity is None:
            scientific_identity = identity
        elif identity != scientific_identity:
            raise ValueError("NEG-8 reference corpus members are not same-condition")
        gross, problem = _gross_energy_evidence(bundle_path)
        if problem is not None or gross is None:
            raise ValueError(
                f"NEG-8 corpus member {bundle_id} gross evidence is invalid"
            )
        evidence_members.append(
            {
                "bundle_id": bundle_id,
                "point_gross_j": gross["point_j"],
                "bundle_evidence_sha256": _bundle_evidence_sha256(bundle_path),
            }
        )
    assert scientific_identity is not None
    return build_neg8_drift_bound_artifact(
        corpus_id=manifest.get("corpus_id"),
        condition_id=manifest.get("condition_id"),
        manifest_sha256=hashlib.sha256(raw).hexdigest(),
        scientific_config_sha256=scientific_identity,
        members=evidence_members,
    )


REGISTERED_POLICY_DIR = (
    Path(__file__).resolve().parents[1] / "configs" / "campaign_policies"
)


def _registered_policy(policy_sha256: Any) -> Mapping[str, Any] | None:
    """Resolve a repo-registered campaign policy by exact file-byte hash.

    The verdict row's ``policy_sha256`` is the hash of the campaign-policy
    file bytes.  Registered policy files are the only trust anchor the
    claim-time verifier has that does not terminate at bundle custody: a
    forged row can rewrite its own tolerances and hashes consistently, but it
    cannot mint a matching tracked policy file.  Unknown hashes fail closed.
    """

    if not isinstance(policy_sha256, str) or len(policy_sha256) != 64:
        return None
    try:
        candidates = sorted(REGISTERED_POLICY_DIR.glob("*.json"))
    except OSError:
        return None
    for path in candidates:
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if hashlib.sha256(raw).hexdigest() != policy_sha256:
            continue
        try:
            # Duplicate JSON keys parse last-key-wins under plain json.loads,
            # so a hash would authenticate ambiguous bytes; the trust anchor
            # must refuse them (confirmation-round-6 P1).
            from joulewise.determinism_gate import (  # noqa: PLC0415
                _reject_duplicate_json_pairs,
            )

            payload = json.loads(
                raw, object_pairs_hook=_reject_duplicate_json_pairs
            )
        except (UnicodeDecodeError, ValueError):
            return None
        return payload if isinstance(payload, Mapping) else None
    return None


def _registered_bracket_policy(policy_sha256: Any) -> Mapping[str, Any] | None:
    payload = _registered_policy(policy_sha256)
    extension = (
        payload.get("idle_admission_extension")
        if isinstance(payload, Mapping)
        else None
    )
    bracket = (
        extension.get("neg8_bracket") if isinstance(extension, Mapping) else None
    )
    return bracket if isinstance(bracket, Mapping) else None


def _scientific_config_identity(bundle_path: Path) -> tuple[str | None, bool]:
    """Recompute canonical NEG-8 identity from custody-bound config bytes."""

    config = _read_json_object(bundle_path / "config.json")
    metadata = _read_json_object(bundle_path / "metadata.json")
    try:
        raw = (bundle_path / "config.json").read_bytes()
        normalized = BenchmarkConfig.from_mapping(dict(config or {})).to_dict()
    except (OSError, TypeError, ValueError):
        return None, False
    if (
        not isinstance(metadata, Mapping)
        or metadata.get("config_sha256") != hashlib.sha256(raw).hexdigest()
    ):
        return None, False
    scientific = dict(normalized)
    scientific.pop("run_id", None)
    digest = hashlib.sha256(
        json.dumps(scientific, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    workload = normalized.get("workload_profile")
    canonical = bool(
        isinstance(workload, Mapping)
        and workload.get("name") == "df_rq_mid"
        and workload.get("prompt_tokens") == 1024
        and workload.get("output_tokens") == 256
        and workload.get("dataset_ref") is None
        and workload.get("suite_manifest_ref") is None
    )
    return digest, canonical


def _derived_neg8_decision(
    manifests: Sequence[Mapping[str, Any]],
    runs_root: Path,
    policy_value: Any,
    *,
    current: bool = True,
    point_drift: bool = False,
    drift_bound_artifact: Any = None,
) -> tuple[str | None, str | None]:
    """Re-derive a verdict from source-member summaries, never the stored row.

    ``current`` selects the evidence-path resolution: current-strict rows use
    selection-custody manifest resolution; frozen replay rows keep the
    committed 0925480 ``runs_root / bundle_id`` resolution unconditionally
    (frozen-arm purity — a custody improvement must never change a frozen
    row's disposition in either direction).
    """

    try:
        policy = Neg8BracketPolicy.from_mapping(policy_value)
    except (TypeError, ValueError):
        return None, "provenance"
    references: dict[str, list[dict[str, float] | None]] = {
        "start": [],
        "end": [],
    }
    invalid_role = False
    for manifest in manifests:
        manifest_paths = (
            _manifest_bundle_paths([manifest], runs_root) if current else None
        )
        if current and manifest_paths is None:
            return None, "provenance"
        members = manifest.get("members")
        if not isinstance(members, list):
            return None, "provenance"
        for member in members:
            if not isinstance(member, Mapping) or member.get("execution") != "invoked":
                continue
            position = _neg8_position(
                member.get("role"), member.get("sentinel_position")
            )
            if position is None:
                continue
            if position == "invalid":
                invalid_role = True
                continue
            bundle_ids = member.get("bundle_ids")
            if not isinstance(bundle_ids, list):
                return None, "provenance"
            for bundle_id in bundle_ids:
                if not isinstance(bundle_id, str) or not bundle_id:
                    return None, "provenance"
                if current:
                    bundle_path = manifest_paths.get(bundle_id)
                    if bundle_path is None:
                        return None, "provenance"
                else:
                    # Frozen replay: committed direct resolution, no custody
                    # requirement, evidence-or-None appended as at 0925480.
                    frozen_evidence, _frozen_problem = _gross_energy_evidence(
                        runs_root / bundle_id
                    )
                    references[position].append(frozen_evidence)
                    continue
                stored_summary = _read_json_object(bundle_path / "summary_metrics.json")
                if _current_strict_summary(stored_summary):
                    scientific_sha, canonical = _scientific_config_identity(bundle_path)
                    if (
                        member.get("canonical_neg8_workload") is not True
                        or not canonical
                        or scientific_sha is None
                        or member.get("scientific_config_sha256") != scientific_sha
                    ):
                        return None, "provenance"
                evidence, problem = _gross_energy_evidence(bundle_path)
                if problem is not None:
                    return None, problem
                references[position].append(evidence)
    start = references["start"][0] if len(references["start"]) == 1 else None
    end = references["end"][0] if len(references["end"]) == 1 else None
    if invalid_role or len(references["start"]) > 1 or len(references["end"]) > 1:
        start = end = None
    if point_drift:
        return (
            evaluate_neg8_point_drift(
                start,
                end,
                policy,
                drift_bound_artifact,
            )["decision"],
            None,
        )
    return evaluate_neg8_bracket(start, end, policy)["decision"], None


def _manifest_bundle_paths(
    manifests: Sequence[Mapping[str, Any]], runs_root: Path
) -> dict[str, Path] | None:
    """Resolve every invoked occurrence without duplicate/set collapse."""

    result: dict[str, Path] = {}
    for manifest in manifests:
        selection = manifest.get("attempt_ledger_selection")
        if isinstance(selection, Mapping):
            descriptors = selection.get("selected_bundles")
            if not isinstance(descriptors, list):
                return None
            occurrences: list[tuple[str, Path]] = []
            for descriptor in descriptors:
                if not isinstance(descriptor, Mapping):
                    return None
                bundle_id = descriptor.get("bundle_id")
                path = _safe_source_path(runs_root, descriptor.get("path"))
                if not isinstance(bundle_id, str) or not bundle_id or path is None:
                    return None
                occurrences.append((bundle_id, path))
        else:
            members = manifest.get("members")
            if not isinstance(members, list):
                return None
            occurrences = []
            for member in members:
                if not isinstance(member, Mapping) or member.get("execution") != "invoked":
                    continue
                ids = member.get("bundle_ids")
                if not isinstance(ids, list):
                    return None
                for bundle_id in ids:
                    if not isinstance(bundle_id, str) or not bundle_id:
                        return None
                    occurrences.append((bundle_id, runs_root / bundle_id))
        for bundle_id, path in occurrences:
            if bundle_id in result:
                # G7(a) is a current strict-path gate.  Frozen replay keeps
                # the committed occurrence-to-set collapse; a mixed/current
                # join refuses as soon as either duplicate path is current.
                if _current_strict_summary(
                    _read_json_object(path / "summary_metrics.json")
                ) or _current_strict_summary(
                    _read_json_object(result[bundle_id] / "summary_metrics.json")
                ):
                    return None
                continue
            result[bundle_id] = path
    return result


def _load_idle_records(bundle_path: Path, attempt: int) -> list[dict[str, Any]] | None:
    name = (
        "rich_telemetry_idle.jsonl"
        if attempt == 1
        else f"rich_telemetry_idle_attempt_{attempt}.jsonl"
    )
    try:
        lines = (bundle_path / name).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    rows: list[dict[str, Any]] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            return None
        if not isinstance(row, dict):
            return None
        rows.append(row)
    return rows


def _adapter_observations(bundle_id: str, metadata: Mapping[str, Any]) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    environment = metadata.get("environment")
    if isinstance(environment, Mapping):
        observations.append(
            extract_adapter_observation(
                environment.get("power") if isinstance(environment.get("power"), Mapping) else None,
                source=f"{bundle_id}:environment",
                power_source=environment.get("power_source"),
            )
        )
    admission = metadata.get("environment_admission")
    guards = admission.get("guard_observations") if isinstance(admission, Mapping) else None
    if isinstance(guards, list):
        for guard in guards:
            if not isinstance(guard, Mapping) or "power" not in guard:
                continue
            phase = guard.get("phase")
            observations.append(
                extract_adapter_observation(
                    guard.get("power") if isinstance(guard.get("power"), Mapping) else None,
                    source=f"{bundle_id}:guard:{phase if isinstance(phase, str) else 'guard'}",
                )
            )
    post = environment.get("post_run_observation") if isinstance(environment, Mapping) else None
    if isinstance(post, Mapping) and post.get("capture_skipped") is not True:
        observations.append(
            extract_adapter_observation(
                post.get("power") if isinstance(post.get("power"), Mapping) else None,
                source=f"{bundle_id}:post_run",
                power_source=post.get("power_source"),
            )
        )
    else:
        observations.append(
            extract_adapter_observation(None, source=f"{bundle_id}:post_run_missing")
        )
    return observations


def _current_core_rederivation_reasons(
    *,
    core: Mapping[str, Any],
    bundle_ids: Sequence[str],
    manifests: Sequence[Mapping[str, Any]],
    runs_root: Path,
    policy_sha256: Any,
) -> set[str]:
    """Recompute current-mint CPU/environment/adapter labels from members."""

    reasons: set[str] = set()
    paths = _manifest_bundle_paths(manifests, runs_root)
    # STRUCTURAL frozen gate (delta-review P2): a frozen-only row must exit
    # before ANY current-gate refusal can fire, including registered-policy
    # parse failures and custody-resolution failures.  The currentness probe
    # therefore falls back to direct resolution when custody paths are
    # unavailable.
    probe_paths = (
        paths
        if paths is not None
        else {bundle_id: runs_root / bundle_id for bundle_id in bundle_ids}
    )
    strict_current_ids = {
        bundle_id
        for bundle_id in bundle_ids
        if (path := probe_paths.get(bundle_id)) is not None
        and _current_strict_summary(_read_json_object(path / "summary_metrics.json"))
    }
    if not strict_current_ids:
        return reasons

    registered = _registered_policy(policy_sha256)
    extension_value = (
        registered.get("idle_admission_extension")
        if isinstance(registered, Mapping)
        else None
    )
    profile = registered.get("profile") if isinstance(registered, Mapping) else None
    # A registered hash authenticates policy bytes, not claim authority. Only
    # a production policy whose extension explicitly bears claims may license
    # a current whole-window row. Exploratory collection remains legal, but
    # its verdict cannot be laundered into claim evidence.
    if (
        profile != "production"
        or not isinstance(extension_value, Mapping)
        or extension_value.get("claim_bearing") is not True
    ):
        return {"whole_window_verdict_provenance_invalid"}
    try:
        extension = IdleAdmissionExtension.from_mapping(
            dict(extension_value) if isinstance(extension_value, Mapping) else None,
            profile=profile,
        )
    except (TypeError, ValueError):
        return {"whole_window_verdict_provenance_invalid"}
    try:
        registered_typed_policy = CampaignPolicy.from_mapping(dict(registered))
    except (TypeError, ValueError):
        return {"whole_window_verdict_provenance_invalid"}
    if paths is None:
        return {"whole_window_verdict_provenance_invalid"}

    derived_members: list[
        tuple[str, Path, Mapping[str, Any], Mapping[str, Any]]
    ] = []
    for bundle_id in bundle_ids:
        path = paths.get(bundle_id)
        if path is None:
            reasons.add("whole_window_verdict_provenance_invalid")
            continue
        metadata = _read_json_object(path / "metadata.json")
        if not isinstance(metadata, Mapping):
            reasons.add("environment_admission_missing")
            continue
        admission = metadata.get("environment_admission")
        if bundle_id in strict_current_ids:
            try:
                window = BundleReader(path).measured_window()
            except (BundleReadError, OSError, TypeError, ValueError):
                window = None
            if window is None:
                reasons.add("environment_admission_missing")
                continue
            reasons.update(
                current_environment_refusals(
                    metadata,
                    bundle_path=path,
                    measured_window_start_s=window.start_s,
                    measured_window_end_s=window.end_s,
                )
            )
        else:
            reasons.update(environment_admission_refusals(admission))
        attempts = admission.get("attempts") if isinstance(admission, Mapping) else None
        final = attempts[-1] if isinstance(attempts, list) and attempts else None
        attempt = final.get("attempt") if isinstance(final, Mapping) else None
        records = (
            _load_idle_records(path, attempt)
            if isinstance(attempt, int) and not isinstance(attempt, bool)
            else None
        )
        decision = admission.get("decision") if isinstance(admission, Mapping) else None
        cpu = evaluate_cpu_idle_admission(
            records,
            extension.cpu_criteria,
            gpu_admitted=(
                True if decision == "admitted" else False if decision in {"flagged", "abort"} else None
            ),
        )
        derived_members.append((bundle_id, path, metadata, cpu))

    stored_members = core.get("members")
    if not isinstance(stored_members, list):
        reasons.add("cpu_admission_core_missing")
    else:
        by_id = {
            row.get("bundle_id"): row
            for row in stored_members
            if isinstance(row, Mapping) and isinstance(row.get("bundle_id"), str)
        }
        for bundle_id, _path, _metadata, cpu in derived_members:
            stored = by_id.get(bundle_id)
            stored_cpu = stored.get("cpu_admission") if isinstance(stored, Mapping) else None
            if not isinstance(stored_cpu, Mapping) or dict(stored_cpu) != cpu:
                reasons.add("cpu_admission_core_failed")

    conditions = core.get("conditions")
    if not isinstance(conditions, list) or conditions:
        reasons.add("whole_window_verdict_provenance_invalid")

    if len(derived_members) == len(bundle_ids):
        observations = [
            observation
            for bundle_id, _path, metadata, _cpu in derived_members
            for observation in _adapter_observations(bundle_id, metadata)
        ]
        derived = evaluate_adapter_wattage_continuity(
            observations, extension.adapter_wattage
        )
        stored = core.get("adapter_wattage_continuity")
        if not isinstance(stored, Mapping) or dict(stored) != derived:
            reasons.add("adapter_continuity_failed")
        calibration_bracket, calibration_reasons = calibration_bracket_for_bundles(
            runs_root,
            [path for _bundle_id, path, _metadata, _cpu in derived_members],
            registered_typed_policy.calibration_bracketing,
        )
        stored_calibration_bracket = core.get("instrument_calibration_bracket")
        if (
            not isinstance(stored_calibration_bracket, Mapping)
            or dict(stored_calibration_bracket) != calibration_bracket
        ):
            reasons.add("whole_window_verdict_conflict")
        reasons.update(calibration_reasons)
        # The contract consumes B_fiducial = max(B_pre, B_post), but member
        # envelopes were minted from each bundle's attached (pre) calibration
        # alone.  A claim is therefore defensible ONLY when every member's
        # minted bound already dominates the bracket maximum; otherwise the
        # envelopes understate the admissible sets under calibration drift
        # (confirmation-round-6 P0) and the members must be re-reduced.
        bracket_bound = (
            calibration_bracket.get("b_fiducial_s")
            if isinstance(calibration_bracket, Mapping)
            else None
        )
        if not isinstance(bracket_bound, bool) and isinstance(
            bracket_bound, int | float
        ):
            physics_cache: dict[str, float] = {}
            for _bundle_id, _path, member_metadata, _cpu in derived_members:
                member_calibration = (
                    member_metadata.get("instrument_calibration")
                    if isinstance(member_metadata, Mapping)
                    else None
                )
                metadata_scalar = (
                    member_calibration.get("verified_effective_b_fiducial_s")
                    if isinstance(member_calibration, Mapping)
                    else None
                )
                authenticated: float | None = None
                detail: str | None = "instrument_calibration_invalid"
                if isinstance(member_calibration, Mapping):
                    try:
                        authenticated, detail = _verify_instrument_calibration(
                            BundleReader(_path),
                            dict(member_metadata),
                            dict(member_calibration),
                            strict_physics=True,
                            physics_cache=physics_cache,
                        )
                    except (BundleReadError, OSError, TypeError, ValueError):
                        authenticated = None
                        detail = "instrument_calibration_invalid"
                if (
                    detail is not None
                    or authenticated is None
                    or not math.isfinite(authenticated)
                    or authenticated < 0.0
                ):
                    reasons.add("whole_window_verdict_provenance_invalid")
                    continue
                if (
                    isinstance(metadata_scalar, bool)
                    or not isinstance(metadata_scalar, int | float)
                    or not math.isfinite(float(metadata_scalar))
                    or abs(float(metadata_scalar) - authenticated) > 1e-9
                ):
                    reasons.add("whole_window_verdict_provenance_invalid")
                if float(bracket_bound) > authenticated + 1e-12:
                    reasons.add("calibration_bracket_exceeds_minted_bound")
    return reasons


def _validated_evaluation_basis(
    row: Mapping[str, Any], runs_root: Path
) -> Mapping[str, Any] | None:
    basis = row.get("evaluation_basis")
    if not isinstance(basis, Mapping):
        return None
    payload = {key: value for key, value in basis.items() if key != "sha256"}
    policy = row.get("campaign_policy")
    policy_sha = policy.get("sha256") if isinstance(policy, Mapping) else None
    occurrences = basis.get("member_occurrences")
    bracket_set = basis.get("calibration_bracket_set")
    core = row.get("idle_admission_core")
    stored_bracket = (
        core.get("instrument_calibration_bracket")
        if isinstance(core, Mapping)
        else None
    )
    expected_bracket_set = {
        "pre": (
            dict(stored_bracket["pre"])
            if isinstance(stored_bracket, Mapping)
            and isinstance(stored_bracket.get("pre"), Mapping)
            else None
        ),
        "post": (
            dict(stored_bracket["post"])
            if isinstance(stored_bracket, Mapping)
            and isinstance(stored_bracket.get("post"), Mapping)
            else None
        ),
    }
    if (
        basis.get("schema_version") != WHOLE_WINDOW_EVALUATION_BASIS_SCHEMA
        or basis.get("policy_sha256") != policy_sha
        or basis.get("sha256") != canonical_sha256(payload)
        or not isinstance(occurrences, list)
        or not occurrences
        or bracket_set != expected_bracket_set
    ):
        return None
    ids: list[str] = []
    root = Path(runs_root).resolve()
    for occurrence in occurrences:
        if not isinstance(occurrence, Mapping):
            return None
        bundle_id = occurrence.get("bundle_id")
        path = _safe_source_path(root, occurrence.get("bundle_path"))
        if not isinstance(bundle_id, str) or not bundle_id or path is None:
            return None
        ids.append(bundle_id)
        for name, field in (
            ("config.json", "config_sha256"),
            ("metadata.json", "metadata_sha256"),
            ("summary_metrics.json", "summary_sha256"),
        ):
            expected = occurrence.get(field)
            try:
                raw = (path / name).read_bytes()
            except OSError:
                return None
            if (
                not isinstance(expected, str)
                or len(expected) != 64
                or hashlib.sha256(raw).hexdigest() != expected
            ):
                return None
    bundle_ids = row.get("bundle_ids")
    scope = row.get("evaluation_scope")
    if (
        len(set(ids)) != len(ids)
        or not isinstance(bundle_ids, list)
        or sorted(ids) != sorted(bundle_ids)
        or not isinstance(scope, Mapping)
        or scope.get("runs_root") != str(root)
        or not isinstance(scope.get("started_at"), str)
        or not isinstance(scope.get("completed_at"), str)
    ):
        return None
    return basis


def _supersession_is_logged(entry: Mapping[str, Any], runs_root: Path) -> bool:
    try:
        lines = (Path(runs_root) / "campaign_log.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
    except (OSError, UnicodeDecodeError):
        return False
    for line in lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, Mapping) and dict(value) == dict(entry):
            return True
    return False


def _basis_source_manifests(
    *,
    basis: Mapping[str, Any],
    verified_sources: Sequence[tuple[Mapping[str, Any], Mapping[str, Any]]],
    row: Mapping[str, Any],
    runs_root: Path,
) -> list[Mapping[str, Any]] | None:
    """Project authenticated source history onto the basis-selected occurrences."""

    wanted = {
        occurrence.get("bundle_id")
        for occurrence in basis.get("member_occurrences", [])
        if isinstance(occurrence, Mapping)
        and isinstance(occurrence.get("bundle_id"), str)
    }
    selected_manifests: list[Mapping[str, Any]] = []
    ordinary: dict[str, list[tuple[dict[str, Any], Mapping[str, Any]]]] = {}
    for descriptor, manifest in verified_sources:
        if isinstance(manifest.get("attempt_ledger_selection"), Mapping):
            members = _manifest_members(manifest, runs_root)
            if members is None:
                return None
            if members & wanted:
                selected_manifests.append(manifest)
            continue
        members = manifest.get("members")
        if not isinstance(members, list):
            return None
        for member_index, member in enumerate(members):
            if (
                not isinstance(member, Mapping)
                or member.get("execution") != "invoked"
            ):
                continue
            ids = member.get("bundle_ids")
            if not isinstance(ids, list):
                return None
            for bundle_index, bundle_id in enumerate(ids):
                if bundle_id in wanted:
                    occurrence = {
                        "bundle_id": bundle_id,
                        "source_manifest": dict(descriptor),
                        "member_index": member_index,
                        "bundle_index": bundle_index,
                    }
                    filtered_member = dict(member)
                    filtered_member["bundle_ids"] = [bundle_id]
                    filtered_manifest = dict(manifest)
                    filtered_manifest["members"] = [filtered_member]
                    ordinary.setdefault(bundle_id, []).append(
                        (occurrence, filtered_manifest)
                    )
    supersessions = row.get("occurrence_supersessions")
    campaign_policy = row.get("campaign_policy")
    policy_sha256 = (
        campaign_policy.get("sha256")
        if isinstance(campaign_policy, Mapping)
        else None
    )
    supplied = (
        [value for value in supersessions if isinstance(value, Mapping)]
        if isinstance(supersessions, list)
        else []
    )
    used_entries: set[str] = set()
    for bundle_id in sorted(wanted):
        occurrences = ordinary.get(bundle_id, [])
        if not occurrences:
            if any(
                bundle_id in (_manifest_members(value, runs_root) or set())
                for value in selected_manifests
            ):
                continue
            return None
        if len(occurrences) == 1:
            selected_manifests.append(occurrences[0][1])
            continue
        matches = [
            entry
            for entry in supplied
            if entry.get("bundle_id") == bundle_id
            and entry.get("campaign_policy_sha256") == policy_sha256
            and entry.get("selected_occurrence") == occurrences[-1][0]
            and entry.get("superseded_occurrences")
            == [value[0] for value in occurrences[:-1]]
            and validate_occurrence_supersession_entry(entry, runs_root)
            and _supersession_is_logged(entry, runs_root)
        ]
        if len(matches) != 1:
            return None
        used_entries.add(str(matches[0].get("entry_sha256")))
        selected_manifests.append(occurrences[-1][1])
    if len(used_entries) != len(supplied):
        return None
    return selected_manifests


def _validate_row(
    row: Mapping[str, Any], runs_root: Path, referenced: set[str]
) -> tuple[bool, tuple[str, ...]]:
    reasons: set[str] = set()
    basis_present = "evaluation_basis" in row
    basis = _validated_evaluation_basis(row, runs_root)
    if basis_present and basis is None:
        reasons.add("whole_window_verdict_provenance_invalid")
    if row.get("schema_version") != WHOLE_WINDOW_SCHEMA:
        reasons.add("whole_window_verdict_provenance_invalid")
    bundle_ids = row.get("bundle_ids")
    if (
        not isinstance(bundle_ids, list)
        or any(not isinstance(item, str) or not item for item in bundle_ids)
        or len(set(bundle_ids)) != len(bundle_ids)
        or not referenced.issubset(set(bundle_ids))
    ):
        reasons.add("whole_window_verdict_coverage_incomplete")
        return False, tuple(sorted(reasons))

    policy = row.get("campaign_policy")
    policy_sha = policy.get("sha256") if isinstance(policy, Mapping) else None
    provenance = row.get("row_provenance")
    if (
        not isinstance(policy_sha, str)
        or len(policy_sha) != 64
        or not isinstance(provenance, Mapping)
        or provenance.get("schema_version") != WHOLE_WINDOW_PROVENANCE_SCHEMA
        or provenance.get("policy_sha256") != policy_sha
        or provenance.get("membership_sha256")
        != canonical_sha256(sorted(bundle_ids))
    ):
        reasons.add("whole_window_verdict_provenance_invalid")

    core = row.get("idle_admission_core")
    if not isinstance(core, Mapping) or core.get("schema_version") != IDLE_ADMISSION_CORE_SCHEMA:
        reasons.add("whole_window_verdict_provenance_invalid")
    elif core.get("policy_sha256") != policy_sha:
        reasons.add("whole_window_verdict_provenance_invalid")

    descriptors = (
        provenance.get("source_campaign_manifests")
        if isinstance(provenance, Mapping)
        else None
    )
    covered_by_sources: set[str] = set()
    verified_source_manifests: list[Mapping[str, Any]] = []
    verified_sources: list[
        tuple[Mapping[str, Any], Mapping[str, Any]]
    ] = []
    if not isinstance(descriptors, list) or not descriptors:
        reasons.add("whole_window_verdict_provenance_invalid")
    else:
        seen_paths: set[str] = set()
        for descriptor in descriptors:
            if not isinstance(descriptor, Mapping):
                reasons.add("whole_window_verdict_provenance_invalid")
                continue
            text = descriptor.get("path")
            expected_sha = descriptor.get("sha256")
            path = _safe_source_path(runs_root, text)
            if (
                path is None
                or not isinstance(text, str)
                or text in seen_paths
                or not isinstance(expected_sha, str)
                or len(expected_sha) != 64
            ):
                reasons.add("whole_window_verdict_provenance_invalid")
                continue
            seen_paths.add(text)
            try:
                raw = path.read_bytes()
                manifest = json.loads(raw)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                reasons.add("whole_window_verdict_provenance_invalid")
                continue
            if hashlib.sha256(raw).hexdigest() != expected_sha or not isinstance(
                manifest, Mapping
            ):
                reasons.add("whole_window_verdict_provenance_invalid")
                continue
            manifest_policy = manifest.get("campaign_policy")
            if (
                manifest.get("schema_version")
                != "joulewise.campaign_provenance.v1"
                or not isinstance(manifest_policy, Mapping)
                or manifest_policy.get("sha256") != policy_sha
            ):
                reasons.add("whole_window_verdict_provenance_invalid")
                continue
            verified_sources.append((descriptor, manifest))
            if basis is None:
                members = _manifest_members(manifest, runs_root)
                if members is None:
                    reasons.add("whole_window_verdict_provenance_invalid")
                    continue
                covered_by_sources.update(members)
                verified_source_manifests.append(manifest)
    if basis is not None:
        projected = _basis_source_manifests(
            basis=basis,
            verified_sources=verified_sources,
            row=row,
            runs_root=runs_root,
        )
        if projected is None:
            reasons.add("whole_window_verdict_provenance_invalid")
        else:
            verified_source_manifests = projected
            covered_by_sources.update(
                occurrence.get("bundle_id")
                for occurrence in basis.get("member_occurrences", [])
                if isinstance(occurrence, Mapping)
                and isinstance(occurrence.get("bundle_id"), str)
            )
    if not set(bundle_ids).issubset(covered_by_sources):
        reasons.add("whole_window_verdict_provenance_invalid")

    if isinstance(core, Mapping):
        reasons.update(
            _current_core_rederivation_reasons(
                core=core,
                bundle_ids=bundle_ids,
                manifests=verified_source_manifests,
                runs_root=runs_root,
                policy_sha256=policy_sha,
            )
        )

    if isinstance(core, Mapping):
        bracket = core.get("neg8_bracket")
        continuity = core.get("adapter_wattage_continuity")
        members = core.get("members")
        if not isinstance(bracket, Mapping) or bracket.get("schema_version") != NEG8_BRACKET_SCHEMA:
            reasons.add("whole_window_neg8_verdict_missing")
        elif row.get("status") != "passed" or bracket.get("decision") != "passed":
            reasons.add("whole_window_neg8_verdict_failed")
        if isinstance(bracket, Mapping):
            # Tolerances come from the repo-registered policy matching the
            # row's policy_sha256, never from the row's self-asserted copy —
            # and the self-asserted copy must agree with the registered one
            # (a loosened-tolerance forgery is provenance-invalid even before
            # re-derivation).
            registered_policy = _registered_bracket_policy(policy_sha)
            if (
                registered_policy is None
                or bracket.get("policy") != registered_policy
            ):
                reasons.add("whole_window_verdict_provenance_invalid")
            else:
                point_drift = "estimand" in bracket
                if (
                    point_drift
                    and bracket.get("estimand") != NEG8_POINT_DRIFT_ESTIMAND
                ):
                    reasons.add("whole_window_verdict_provenance_invalid")
                drift_bound_artifact = bracket.get("drift_bound_artifact")
                if (
                    drift_bound_artifact is not None
                    and not validate_neg8_drift_bound_artifact(
                        drift_bound_artifact
                    )
                ):
                    reasons.add("whole_window_verdict_provenance_invalid")
                derived_decision, derived_problem = _derived_neg8_decision(
                    verified_source_manifests,
                    runs_root,
                    registered_policy,
                    current=(
                        any(
                            isinstance(occurrence, Mapping)
                            and (
                                path := _safe_source_path(
                                    runs_root, occurrence.get("bundle_path")
                                )
                            )
                            is not None
                            and _current_strict_summary(
                                _read_json_object(
                                    path / "summary_metrics.json"
                                )
                            )
                            for occurrence in basis.get(
                                "member_occurrences", []
                            )
                        )
                        if basis is not None
                        else _row_references_current_strict_member(
                            row, runs_root, referenced
                        )
                    ),
                    point_drift=point_drift,
                    drift_bound_artifact=drift_bound_artifact,
                )
                if derived_problem == "conflict":
                    reasons.add("whole_window_verdict_conflict")
                elif derived_problem is not None or derived_decision is None:
                    reasons.add("whole_window_verdict_provenance_invalid")
                elif bracket.get("decision") != derived_decision:
                    reasons.add("whole_window_verdict_conflict")
        if not isinstance(continuity, Mapping) or continuity.get("schema_version") != ADAPTER_CONTINUITY_SCHEMA:
            reasons.add("adapter_continuity_evidence_missing")
        elif continuity.get("decision") != "stable":
            reasons.add("adapter_continuity_failed")
        if not isinstance(members, list) or not members:
            reasons.add("cpu_admission_core_missing")
        else:
            member_ids: list[str] = []
            member_digests: list[str] = []
            for member in members:
                if not isinstance(member, Mapping):
                    continue
                bundle_id = member.get("bundle_id")
                if isinstance(bundle_id, str) and bundle_id:
                    member_ids.append(bundle_id)
                try:
                    member_digests.append(canonical_sha256(member))
                except (TypeError, ValueError):
                    pass
            # Occurrence count is evidence.  Set collapse must not turn two
            # byte-identical or same-ID members into one authoritative row.
            if (
                len(member_ids) != len(members)
                or len(set(member_ids)) != len(member_ids)
                or len(member_digests) != len(members)
                or len(set(member_digests)) != len(member_digests)
            ):
                reasons.add("whole_window_verdict_provenance_invalid")
            if not referenced.issubset(member_ids):
                reasons.add("whole_window_verdict_coverage_incomplete")
            if any(
                not isinstance(member, Mapping)
                or not isinstance(member.get("cpu_admission"), Mapping)
                or member["cpu_admission"].get("decision") != "admitted"
                for member in members
            ):
                reasons.add("cpu_admission_core_failed")
    return not reasons, tuple(sorted(reasons))


def _row_references_current_strict_member(
    row: Mapping[str, Any], runs_root: Path, referenced: set[str]
) -> bool:
    """Find current members in both ordinary and selected-bundle custody."""

    provenance = row.get("row_provenance")
    descriptors = (
        provenance.get("source_campaign_manifests")
        if isinstance(provenance, Mapping)
        else None
    )
    if not isinstance(descriptors, list):
        return False
    manifests: list[Mapping[str, Any]] = []
    for descriptor in descriptors:
        path = (
            _safe_source_path(runs_root, descriptor.get("path"))
            if isinstance(descriptor, Mapping)
            else None
        )
        manifest = _read_json_object(path) if path is not None else None
        if isinstance(manifest, Mapping):
            manifests.append(manifest)
    paths = _manifest_bundle_paths(manifests, runs_root)
    return bool(
        paths is not None
        and any(
            bundle_id in referenced
            and _current_strict_summary(
                _read_json_object(path / "summary_metrics.json")
            )
            for bundle_id, path in paths.items()
        )
    )


def whole_window_refusal_reasons(
    runs_root: Path,
    referenced_bundle_ids: set[str],
    *,
    evaluation_basis_sha256: str | None = None,
) -> tuple[str, ...]:
    """Return refusals from the verdict governing the requested exact basis."""

    missing = (
        "whole_window_neg8_verdict_missing",
        "adapter_continuity_evidence_missing",
        "cpu_admission_core_missing",
    )
    try:
        lines = (Path(runs_root) / "campaign_log.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
    except (OSError, UnicodeDecodeError):
        return missing
    verdict_rows: list[Mapping[str, Any]] = []
    history_malformed = False
    for line in lines:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            history_malformed = True
            continue
        if not isinstance(row, Mapping):
            history_malformed = True
            continue
        if row.get("record_type") != (
            "idle_admission_whole_window_verdict"
        ):
            continue
        bundle_ids = row.get("bundle_ids")
        ids = {
            item for item in bundle_ids or [] if isinstance(item, str)
        } if isinstance(bundle_ids, list) else set()
        if not ids.intersection(referenced_bundle_ids):
            continue
        verdict_rows.append(row)
    basis_rows = [
        row
        for row in verdict_rows
        if isinstance(row.get("evaluation_basis"), Mapping)
    ]
    if basis_rows:
        overlapping = []
        for row in basis_rows:
            basis = row["evaluation_basis"]
            occurrences = basis.get("member_occurrences")
            ids = {
                value.get("bundle_id")
                for value in occurrences or []
                if isinstance(value, Mapping)
                and isinstance(value.get("bundle_id"), str)
            } if isinstance(occurrences, list) else set()
            if evaluation_basis_sha256 is not None:
                if (
                    basis.get("sha256") == evaluation_basis_sha256
                    and referenced_bundle_ids.issubset(ids)
                ):
                    overlapping.append(row)
            elif ids == referenced_bundle_ids:
                overlapping.append(row)
    else:
        # Legacy rows remain replay-readable when no basis-bearing history
        # exists. Once a runner records bases, legacy rows never govern the
        # new claim path.
        overlapping = verdict_rows
    valid: list[Mapping[str, Any]] = []
    invalid_reasons: set[str] = set()
    for row in overlapping:
        ok, reasons = _validate_row(row, Path(runs_root), referenced_bundle_ids)
        if ok:
            valid.append(row)
        else:
            invalid_reasons.update(reasons)
    current_referenced = any(
        _current_strict_summary(
            _read_json_object(Path(runs_root) / bundle_id / "summary_metrics.json")
        )
        for bundle_id in referenced_bundle_ids
    ) or any(
        _row_references_current_strict_member(
            row, Path(runs_root), referenced_bundle_ids
        )
        for row in overlapping
    )
    if history_malformed and current_referenced:
        # Bundle-local custody cannot make append-history erasure impossible:
        # an attacker controlling the whole runs root can still forge a fully
        # consistent replacement corpus.  The attainable goal is narrower:
        # laundering must mint consistent member bundles/manifests/verdicts,
        # not delete or corrupt one cheap campaign-log line.
        return ("whole_window_verdict_conflict",)
    if not overlapping:
        return missing
    if not valid:
        return tuple(sorted(invalid_reasons or set(missing)))
    # Within one selected basis, any malformed/incomplete or semantically
    # different row remains ambiguous. Different bases were filtered above,
    # never ordered as "latest wins".
    if len(valid) != len(overlapping):
        return ("whole_window_verdict_conflict",)
    semantic = {
        canonical_sha256(
            {
                "status": row.get("status"),
                "bundle_ids": sorted(row.get("bundle_ids", [])),
                "campaign_policy": row.get("campaign_policy"),
                "idle_admission_core": row.get("idle_admission_core"),
                "row_provenance": row.get("row_provenance"),
                "evaluation_basis": row.get("evaluation_basis"),
            }
        )
        for row in valid
    }
    if len(semantic) != 1:
        return ("whole_window_verdict_conflict",)
    return ()


__all__ = [
    "CONDITION_NEG8_DRIFT_BOUND_UNDERIVED",
    "NEG8_DRIFT_BOUND_SCHEMA",
    "NEG8_DRIFT_ESTIMATOR_ID",
    "NEG8_POINT_DRIFT_ESTIMAND",
    "NEG8_REFERENCE_CORPUS_SCHEMA",
    "OCCURRENCE_SUPERSESSION_SCHEMA",
    "WHOLE_WINDOW_EVALUATION_BASIS_SCHEMA",
    "WHOLE_WINDOW_PROVENANCE_SCHEMA",
    "WHOLE_WINDOW_SCHEMA",
    "build_evaluation_basis",
    "build_neg8_drift_bound_artifact",
    "build_row_provenance",
    "canonical_sha256",
    "evaluate_neg8_point_drift",
    "load_neg8_drift_bound_artifact",
    "mint_neg8_drift_bound_artifact",
    "ordinary_present_bundle_paths",
    "source_manifest_descriptors",
    "supersession_entry_sha256",
    "validate_occurrence_supersession_entry",
    "validate_neg8_drift_bound_artifact",
    "whole_window_refusal_reasons",
]
