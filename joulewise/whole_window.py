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
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
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
from joulewise.reduce import (
    _rederive_summary_for_authenticated_fiducial_bound,
    _verify_instrument_calibration,
)
from joulewise.schemas import BenchmarkConfig, CampaignPolicy, TelemetryBackend

WHOLE_WINDOW_SCHEMA = "joulewise.idle_admission_whole_window_verdict.v1"
IDLE_ADMISSION_CORE_SCHEMA = "joulewise.idle_admission_core_verdict.v1"
WHOLE_WINDOW_PROVENANCE_SCHEMA = (
    "joulewise.idle_admission_whole_window_provenance.v1"
)
WHOLE_WINDOW_EVALUATION_BASIS_SCHEMA = (
    "joulewise.idle_admission_evaluation_basis.v1"
)
MINTED_CONSUMPTION_SEMANTICS_ID = "d078_minted_envelopes_v1"
MAX_BRACKET_CONSUMPTION_SEMANTICS_ID = (
    "d078_authenticated_max_bracket_rederivation_v1"
)
CONSUMPTION_PROVENANCE_PRECHECK_KEY = "calibration_rebracket_consumption"
OCCURRENCE_SUPERSESSION_SCHEMA = (
    "joulewise.campaign_occurrence_supersession.v1"
)
CURRENT_MINT_REDUCER_VERSIONS = frozenset({"0.5.2", "0.6.2"})
NEG8_DRIFT_BOUND_SCHEMA = "joulewise.neg8_drift_bound.v1"
NEG8_REFERENCE_CORPUS_SCHEMA = "joulewise.neg8_reference_corpus.v1"
NEG8_POINT_DRIFT_ESTIMAND = (
    "abs(end_point_gross_j-start_point_gross_j)"
)
NEG8_IDLE_SUB_POINT_DRIFT_ESTIMAND = (
    "abs(end_point_idle_subtracted_j-start_point_idle_subtracted_j)"
)
NEG8_DRIFT_ESTIMATOR_ID = "d054_point_contrast_guard_v1"
NEG8_DRIFT_MINIMUM_N = 10
NEG8_REPLICATED_ENDPOINT_N = 3
NEG8_DRIFT_BOUND_MAX_AGE_S = 86400
NEG8_CLAIM_FAMILY_GROSS = "gross_energy"
NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED = "idle_subtracted_energy"
CONDITION_NEG8_DRIFT_BOUND_UNDERIVED = "neg8_drift_bound_underived"
CONDITION_NEG8_IDLE_SUB_DRIFT_BOUND_UNDERIVED = (
    "neg8_idle_sub_drift_bound_underived"
)
CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED = (
    "neg8_bracket_abs_delta_exceeded"
)
CONDITION_NEG8_IDLE_SUB_POINT_DRIFT_EXCEEDED = (
    "neg8_bracket_idle_sub_abs_delta_exceeded"
)
CONDITION_NEG8_DRIFT_BOUND_STALE = "neg8_drift_bound_stale"
NEG8_POINT_DRIFT_CONDITION_CODES = frozenset(
    {
        CONDITION_NEG8_DRIFT_BOUND_UNDERIVED,
        CONDITION_NEG8_IDLE_SUB_DRIFT_BOUND_UNDERIVED,
        CONDITION_NEG8_DRIFT_BOUND_STALE,
        CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED,
        CONDITION_NEG8_IDLE_SUB_POINT_DRIFT_EXCEEDED,
        "neg8_bracket_missing",
        "neg8_bracket_reference_invalid",
    }
)
NEG8_WHOLE_WINDOW_ALLOWANCE_TERM = "E_whole_window_drift_allowance_j"


@dataclass(frozen=True)
class WholeWindowDriftAllowanceResult:
    """Discriminate authenticated current allowances from frozen replay."""

    status: str
    allowances: Mapping[str, Mapping[str, Any]]


_REDERIVATION_LEAF_REASONS = frozenset(
    {
        "post_window_trace_tail_shorter_than_anchor_bound",
        "nonpositive_window_duration",
        "insufficient_in_window_samples",
        "cadence_ratio_unrecorded",
        "cadence_ratio_below_threshold",
        "clock_bound_unrecorded",
        "clock_bound_exceeds_quarter_window",
        "interpolation_bound_unrecorded",
        "drift_term_unknown",
        "idle_baseline_unrecorded",
        "cooldown_cap_hit",
        "anchor_energy_envelope_exceeds_quarter_metric",
        "anchor_energy_envelope_unrecorded",
        "clock_anchor_unresolved",
        "instrument_calibration_missing",
        "instrument_calibration_mismatch",
        "instrument_calibration_invalid",
        "instrument_calibration_stale",
        "negative_power_sample",
    }
)

_METRIC_LOCAL_PRECHECK_REASONS = frozenset(
    {
        "nonpositive_window_duration",
        "insufficient_in_window_samples",
        "cadence_ratio_unrecorded",
        "cadence_ratio_below_threshold",
        "clock_bound_unrecorded",
        "clock_bound_exceeds_quarter_window",
        "interpolation_bound_unrecorded",
        "drift_term_unknown",
        "idle_baseline_unrecorded",
        "cooldown_cap_hit",
        "anchor_energy_envelope_exceeds_quarter_metric",
        "anchor_energy_envelope_unrecorded",
    }
)
_ADDRESSABLE_PRECHECK_ROOTS = frozenset(
    {"gross_request", "idle_subtracted_request"}
)
_ADDRESSABLE_PRECHECK_GROUPS = frozenset(
    {"phase", "item", "block", "level"}
)
_GOVERNED_PHASE_PRECHECK_CHILDREN = frozenset(
    {
        "tokenize",
        "setup",
        "prefill",
        "decode",
        "serialize",
        "transfer",
        "deserialize",
    }
)
_PRECHECK_GROUP_METRIC_FIELDS = {
    "phase": "phase_energy_j",
    "item": "suite_item_energy_j",
    "block": "suite_block_energy_j",
    "level": "suite_level_energy_j",
}


def _nested_precheck_refusal_occurrences(
    value: object,
    *,
    path: tuple[str, ...] = (),
) -> tuple[set[tuple[tuple[str, ...], str]], bool]:
    """Locate every refusal occurrence and flag malformed reason containers."""

    reasons: set[tuple[tuple[str, ...], str]] = set()
    malformed = False
    if isinstance(value, Mapping):
        if "reasons" in value:
            raw = value.get("reasons")
            if not isinstance(raw, list) or any(
                not isinstance(reason, str) for reason in raw
            ):
                malformed = True
            else:
                reasons.update((path, reason) for reason in raw)
        for key, child in value.items():
            child_reasons, child_malformed = (
                _nested_precheck_refusal_occurrences(
                    child,
                    path=(*path, str(key)),
                )
            )
            reasons.update(child_reasons)
            malformed = malformed or child_malformed
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            child_reasons, child_malformed = (
                _nested_precheck_refusal_occurrences(
                    child,
                    path=(*path, str(index)),
                )
            )
            reasons.update(child_reasons)
            malformed = malformed or child_malformed
    return reasons, malformed


def _normalize_precheck_refusal_path(
    path: tuple[str, ...],
    *,
    recognized_paths: set[tuple[str, ...]],
) -> tuple[str, ...] | None:
    """Normalize one governed precheck occurrence to its addressable child."""

    canonical: tuple[str, ...] | None = None
    if len(path) >= 1 and path[0] in _ADDRESSABLE_PRECHECK_ROOTS:
        canonical = (path[0],)
    elif (
        len(path) >= 2
        and path[0] in _ADDRESSABLE_PRECHECK_GROUPS
        and path[1]
    ):
        canonical = path[:2]
    if canonical is None or canonical not in recognized_paths:
        return None
    suffix = path[len(canonical) :]
    if not suffix:
        return canonical
    if (
        len(suffix) == 2
        and suffix[0] == "windows"
        and suffix[1].isdigit()
    ):
        return canonical
    return None


def _recognized_precheck_paths(
    summary: Mapping[str, Any],
) -> set[tuple[str, ...]]:
    """Return only metric children the governed consumers can address."""

    recognized = {
        (root,) for root in _ADDRESSABLE_PRECHECK_ROOTS
    }
    recognized.update(
        ("phase", child)
        for child in _GOVERNED_PHASE_PRECHECK_CHILDREN
    )
    for group, field in _PRECHECK_GROUP_METRIC_FIELDS.items():
        values = summary.get(field)
        if not isinstance(values, Mapping):
            continue
        recognized.update(
            (group, child)
            for child in values
            if isinstance(child, str) and child
        )
    return recognized


def _classify_precheck_refusals(
    summary: Mapping[str, Any],
) -> tuple[set[str], dict[tuple[str, ...], tuple[str, ...]]]:
    """Split operative precheck refusals with a closed local allowlist."""

    prechecks = summary.get("window_evidence_precheck")
    if not isinstance(prechecks, Mapping):
        return {"whole_window_verdict_provenance_invalid"}, {}
    occurrences, malformed = _nested_precheck_refusal_occurrences(prechecks)
    global_reasons: set[str] = set()
    local: dict[tuple[str, ...], set[str]] = {}
    if malformed:
        global_reasons.add("whole_window_verdict_provenance_invalid")
    recognized_paths = _recognized_precheck_paths(summary)
    for path, reason in occurrences:
        normalized = _normalize_precheck_refusal_path(
            path,
            recognized_paths=recognized_paths,
        )
        if (
            reason not in _METRIC_LOCAL_PRECHECK_REASONS
            or normalized is None
        ):
            global_reasons.add(reason)
            continue
        local.setdefault(normalized, set()).add(reason)
    return global_reasons, {
        path: tuple(sorted(reasons))
        for path, reasons in sorted(local.items())
    }


def _complete_envelope_record(value: object) -> dict[str, Any] | None:
    """Normalize the complete operative envelope required by GOV-02."""

    if not isinstance(value, Mapping):
        return None
    method = value.get("method")
    numeric: dict[str, float] = {}
    for field_name in (
        "anchor_bound_s",
        "point_j",
        "lower_j",
        "upper_j",
        "max_abs_delta_j",
    ):
        candidate = value.get(field_name)
        if (
            isinstance(candidate, bool)
            or not isinstance(candidate, int | float)
            or not math.isfinite(float(candidate))
        ):
            return None
        numeric[field_name] = float(candidate)
    if (
        not isinstance(method, str)
        or not method
        or numeric["anchor_bound_s"] < 0.0
        or numeric["max_abs_delta_j"] < 0.0
        or not (
            numeric["lower_j"]
            <= numeric["point_j"]
            <= numeric["upper_j"]
        )
    ):
        return None
    half_width_j = max(
        numeric["point_j"] - numeric["lower_j"],
        numeric["upper_j"] - numeric["point_j"],
        numeric["max_abs_delta_j"],
    )
    return {
        "method": method,
        **numeric,
        "half_width_j": half_width_j,
    }


class AuthenticatedConsumptionSession:
    """One collection-scoped authenticated max-bracket consumption session.

    The session owns bracket authentication, computes the operative fiducial
    bound from primary evidence, and memoizes every in-memory member
    re-reduction.  It never persists or substitutes a summary artifact.
    """

    def __init__(
        self,
        runs_root: Path,
        referenced_bundle_ids: set[str],
        *,
        evaluation_basis_sha256: str | None = None,
    ) -> None:
        self.runs_root = Path(runs_root)
        self.referenced_bundle_ids = frozenset(referenced_bundle_ids)
        self.evaluation_basis_sha256 = evaluation_basis_sha256
        self.calibration_bracket: Mapping[str, Any] | None = None
        self.operative_fiducial_bound_s: float | None = None
        self.refusal_reasons: tuple[str, ...] = ()
        self.path_refusal_reasons: dict[
            str,
            dict[tuple[str, ...], tuple[str, ...]],
        ] = {}
        self._prepared = False
        self._preparation_identity: tuple[tuple[str, str], ...] | None = None
        self._summaries: dict[str, Mapping[str, Any]] = {}
        self._provenance: dict[str, Mapping[str, Any]] = {}
        self._row_validation_results: dict[
            tuple[str, str, tuple[str, ...], str | None],
            tuple[bool, tuple[str, ...]],
        ] = {}

    @property
    def ready(self) -> bool:
        return self._prepared and not self.refusal_reasons

    def _fail_global(self, reasons: set[str] | tuple[str, ...]) -> None:
        """Clear every authenticated cache when any global refusal exists."""

        self._summaries.clear()
        self._provenance.clear()
        self.path_refusal_reasons.clear()
        self._row_validation_results.clear()
        self.refusal_reasons = tuple(
            sorted(
                set(reasons)
                or {"whole_window_verdict_provenance_invalid"}
            )
        )

    def _prepare(
        self,
        *,
        bundle_paths: Mapping[str, Path],
        policy: CampaignPolicy,
    ) -> None:
        identity = tuple(
            sorted(
                (bundle_id, str(Path(path).resolve()))
                for bundle_id, path in bundle_paths.items()
            )
        )
        if self._prepared:
            if identity != self._preparation_identity:
                self._fail_global(
                    set(self.refusal_reasons)
                    | {"whole_window_verdict_provenance_invalid"}
                )
            return
        self._prepared = True
        self._preparation_identity = identity
        reasons: set[str] = set()
        if (
            not self.referenced_bundle_ids.issubset(bundle_paths)
            or not bundle_paths
        ):
            self._fail_global(
                {"whole_window_verdict_provenance_invalid"}
            )
            return

        bracket, bracket_reasons = calibration_bracket_for_bundles(
            self.runs_root,
            [bundle_paths[bundle_id] for bundle_id in sorted(bundle_paths)],
            policy.calibration_bracketing,
        )
        self.calibration_bracket = bracket
        reasons.update(bracket_reasons)
        raw_bound = bracket.get("b_fiducial_s")
        if (
            isinstance(raw_bound, bool)
            or not isinstance(raw_bound, int | float)
            or not math.isfinite(float(raw_bound))
            or float(raw_bound) < 0.0
        ):
            if not reasons:
                reasons.add("instrument_calibration_invalid")
            self._fail_global(reasons)
            return
        operative_bound = float(raw_bound)
        self.operative_fiducial_bound_s = operative_bound

        physics_cache: dict[str, float] = {}
        pending: list[
            tuple[
                str,
                Path,
                Mapping[str, Any],
                Mapping[str, Any],
                float,
                bool,
            ]
        ] = []
        for bundle_id, path in sorted(bundle_paths.items()):
            stored_summary = _read_json_object(path / "summary_metrics.json")
            metadata = _read_json_object(path / "metadata.json")
            if not _current_strict_summary(stored_summary, path):
                self._summaries[bundle_id] = stored_summary or {}
                continue
            calibration = (
                metadata.get("instrument_calibration")
                if isinstance(metadata, Mapping)
                else None
            )
            authenticated: float | None = None
            detail: str | None = "instrument_calibration_invalid"
            if isinstance(calibration, Mapping) and isinstance(metadata, Mapping):
                try:
                    authenticated, detail = _verify_instrument_calibration(
                        BundleReader(path),
                        dict(metadata),
                        dict(calibration),
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
                reasons.add(
                    detail
                    if detail in _REDERIVATION_LEAF_REASONS
                    else "instrument_calibration_invalid"
                )
                continue
            metadata_scalar = (
                calibration.get("verified_effective_b_fiducial_s")
                if isinstance(calibration, Mapping)
                else None
            )
            if (
                isinstance(metadata_scalar, bool)
                or not isinstance(metadata_scalar, int | float)
                or not math.isfinite(float(metadata_scalar))
                or abs(float(metadata_scalar) - authenticated) > 1e-9
            ):
                # Preserve the existing provenance taxonomy: widening never
                # cures a stored scalar that disagrees with primary evidence.
                reasons.add("whole_window_verdict_provenance_invalid")
                continue
            pending.append(
                (
                    bundle_id,
                    path,
                    stored_summary or {},
                    metadata,
                    float(authenticated),
                    operative_bound > float(authenticated) + 1e-12,
                )
            )

        if reasons:
            self._fail_global(reasons)
            return

        path_refusals: dict[
            str,
            dict[tuple[str, ...], tuple[str, ...]],
        ] = {}
        for (
            bundle_id,
            path,
            stored_summary,
            _metadata,
            minted_bound,
            dominated,
        ) in pending:
            operative_summary: Mapping[str, Any] = stored_summary
            if dominated:
                try:
                    operative_summary = (
                        _rederive_summary_for_authenticated_fiducial_bound(
                            path,
                            authenticated_fiducial_bound_s=operative_bound,
                            _instrument_calibration_physics_cache=physics_cache,
                        )
                    )
                except (
                    BundleReadError,
                    OSError,
                    OverflowError,
                    TypeError,
                    ValueError,
                ):
                    reasons.add("instrument_calibration_invalid")
                    continue
                if operative_summary.get("status") != "succeeded":
                    reasons.add("instrument_calibration_invalid")
                    continue

            global_refusals, local_refusals = (
                _classify_precheck_refusals(operative_summary)
            )
            reasons.update(global_refusals)
            if global_refusals:
                continue
            if local_refusals:
                path_refusals[bundle_id] = local_refusals

            minted_envelopes = stored_summary.get(
                "energy_anchor_shift_envelopes"
            )
            operative_envelopes = operative_summary.get(
                "energy_anchor_shift_envelopes"
            )
            if not isinstance(minted_envelopes, Mapping) or not isinstance(
                operative_envelopes, Mapping
            ):
                reasons.add("anchor_energy_envelope_unrecorded")
                continue
            complete: dict[str, dict[str, Any]] = {}
            coverage_failed = False
            for pointer, minted_value in minted_envelopes.items():
                minted_record = _complete_envelope_record(minted_value)
                operative_record = _complete_envelope_record(
                    operative_envelopes.get(pointer)
                )
                if (
                    not isinstance(pointer, str)
                    or minted_record is None
                    or operative_record is None
                ):
                    coverage_failed = True
                    continue
                if (
                    operative_record["point_j"] != minted_record["point_j"]
                    or operative_record["lower_j"]
                    > minted_record["lower_j"] + 1e-12
                    or operative_record["upper_j"]
                    < minted_record["upper_j"] - 1e-12
                    or operative_record["half_width_j"]
                    + 1e-12
                    < minted_record["half_width_j"]
                ):
                    coverage_failed = True
                    continue
                complete[pointer] = operative_record
            if coverage_failed or set(complete) != set(minted_envelopes):
                reasons.add("anchor_energy_envelope_unrecorded")
                continue
            self._summaries[bundle_id] = operative_summary
            self._provenance[bundle_id] = {
                "consumption_semantics_id": (
                    MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
                ),
                "minted_bound_dominated": dominated,
                "minted_fiducial_bound_s": minted_bound,
                "operative_fiducial_bound_s": operative_bound,
                "calibration_bracket": {
                    "pre": (
                        dict(bracket["pre"])
                        if isinstance(bracket.get("pre"), Mapping)
                        else None
                    ),
                    "post": (
                        dict(bracket["post"])
                        if isinstance(bracket.get("post"), Mapping)
                        else None
                    ),
                },
                "operative_envelopes": complete,
            }

        if reasons or any(
            bundle_id not in self._summaries
            for bundle_id, *_rest in pending
        ):
            self._fail_global(
                reasons or {"instrument_calibration_invalid"}
            )
            return
        self.path_refusal_reasons = path_refusals
        self.refusal_reasons = ()

    def summary_for(self, bundle_id: str) -> Mapping[str, Any] | None:
        """Return the operative in-memory summary only after full discharge."""

        if not self.ready:
            return None
        return self._summaries.get(bundle_id)

    def provenance_for(self, bundle_id: str) -> Mapping[str, Any] | None:
        """Return the durable per-member discharge record."""

        if not self.ready:
            return None
        return self._provenance.get(bundle_id)

    def provenance_by_bundle(self) -> Mapping[str, Mapping[str, Any]]:
        """Return complete basis provenance for a non-clobbering verdict row."""

        if not self.ready:
            return {}
        return {
            bundle_id: dict(record)
            for bundle_id, record in sorted(self._provenance.items())
        }


@dataclass(frozen=True)
class CustodyTelemetryIdentity:
    """Config-authoritative telemetry identity for a bundle consumption path."""

    custody_bound_config: bool
    config_backend_class: str | None
    metadata_backend_class: str | None
    summary_backend_class: str | None
    triangle_agrees: bool

    @property
    def mock_config(self) -> bool:
        return (
            self.custody_bound_config
            and self.config_backend_class == TelemetryBackend.MOCK.value
        )

    @property
    def production_predicate_exempt(self) -> bool:
        # No custody-bound config is fixture/non-production evidence. Its
        # summary label is never promoted into a production identity.
        return not self.custody_bound_config or self.mock_config


def _telemetry_backend_class(value: object) -> str | None:
    """Normalize governed telemetry labels to their backend class."""

    if not isinstance(value, str):
        return None
    if value == TelemetryBackend.MOCK.value or value.startswith("mock:"):
        return TelemetryBackend.MOCK.value
    try:
        return TelemetryBackend(value).value
    except ValueError:
        return None


def custody_telemetry_identity(
    bundle_path: Path,
    *,
    summary: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> CustodyTelemetryIdentity:
    """Derive mockness and config/metadata/summary triangle agreement.

    Config authority exists only when ``metadata.config_sha256`` authenticates
    the exact ``config.json`` bytes. Without that custody binding, the result
    is explicitly non-production and callers may retain fixture-only behavior.
    """

    path = Path(bundle_path)
    if metadata is None:
        metadata = _read_json_object(path / "metadata.json")
    if summary is None:
        summary = _read_json_object(path / "summary_metrics.json")
    quality = (
        summary.get("measurement_quality")
        if isinstance(summary, Mapping)
        else None
    )
    summary_class = _telemetry_backend_class(
        quality.get("telemetry_source")
        if isinstance(quality, Mapping)
        else None
    )
    adapters = (
        metadata.get("adapters")
        if isinstance(metadata, Mapping)
        else None
    )
    telemetry = (
        adapters.get("telemetry")
        if isinstance(adapters, Mapping)
        else None
    )
    metadata_class = _telemetry_backend_class(
        telemetry.get("name") if isinstance(telemetry, Mapping) else None
    )
    if metadata_class is None and isinstance(metadata, Mapping):
        # Frozen AXI mock fixtures predate metadata.adapters.telemetry but do
        # carry the governed tagged primary source identity. Preserve that
        # fixture wire while keeping the compatibility projection mock-only;
        # production backends still require the adapter identity vertex.
        runtime = metadata.get("runtime")
        legacy_mock_class = _telemetry_backend_class(
            runtime.get("primary_source_identity")
            if isinstance(runtime, Mapping)
            else None
        )
        if legacy_mock_class == TelemetryBackend.MOCK.value:
            metadata_class = legacy_mock_class
    try:
        config_raw = (path / "config.json").read_bytes()
    except OSError:
        config_raw = None
    custody_bound = bool(
        config_raw is not None
        and isinstance(metadata, Mapping)
        and metadata.get("config_sha256")
        == hashlib.sha256(config_raw).hexdigest()
    )
    if not custody_bound:
        return CustodyTelemetryIdentity(
            custody_bound_config=False,
            config_backend_class=None,
            metadata_backend_class=metadata_class,
            summary_backend_class=summary_class,
            triangle_agrees=True,
        )
    try:
        raw_config = json.loads(config_raw)
        config = BenchmarkConfig.from_mapping(raw_config)
        config_class = _telemetry_backend_class(
            config.hardware_target.telemetry_backend.value
        )
    except (TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        config_class = None
    triangle_agrees = bool(
        config_class is not None
        and config_class == metadata_class == summary_class
    )
    return CustodyTelemetryIdentity(
        custody_bound_config=True,
        config_backend_class=config_class,
        metadata_backend_class=metadata_class,
        summary_backend_class=summary_class,
        triangle_agrees=triangle_agrees,
    )


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


def _nested_named_mappings(
    value: Any, name: str
) -> list[Mapping[str, Any]]:
    matches: list[Mapping[str, Any]] = []
    if isinstance(value, Mapping):
        candidate = value.get(name)
        if isinstance(candidate, Mapping):
            matches.append(candidate)
        for child in value.values():
            matches.extend(_nested_named_mappings(child, name))
    elif isinstance(value, Sequence) and not isinstance(
        value, (str, bytes, bytearray)
    ):
        for child in value:
            matches.extend(_nested_named_mappings(child, name))
    return matches


def neg8_freshness_bindings_from_metadata(
    metadata: Any,
) -> dict[str, str] | None:
    """Derive the revalidation binding vector from one reference bundle."""

    if not isinstance(metadata, Mapping):
        return None
    snapshots: list[Mapping[str, Any]] = []
    # Prefer the member's run-time observation over the campaign-start
    # preflight. A power supply can renegotiate after preflight; using the
    # stale first snapshot would hide exactly the trigger this binding owns.
    environment = metadata.get("environment")
    if isinstance(environment, Mapping):
        snapshots.append(environment)
    preflight = metadata.get("campaign_environment_preflight")
    if isinstance(preflight, Mapping):
        snapshot = preflight.get("snapshot")
        if isinstance(snapshot, Mapping):
            snapshots.append(snapshot)
        evaluation = preflight.get("evaluation")
        evaluated_snapshot = (
            evaluation.get("snapshot")
            if isinstance(evaluation, Mapping)
            else None
        )
        if isinstance(evaluated_snapshot, Mapping):
            snapshots.append(evaluated_snapshot)
    platform = metadata.get("platform")
    if isinstance(platform, Mapping):
        snapshots.append(platform)

    os_build = next(
        (
            value
            for snapshot in snapshots
            if isinstance((value := snapshot.get("build_version")), str)
            and value
        ),
        None,
    )
    power_identity: dict[str, Any] | None = None
    for snapshot in snapshots:
        power = snapshot.get("power")
        if not isinstance(power, Mapping):
            continue
        power_source = snapshot.get("power_source")
        watts = power.get("adapter_watts")
        description = power.get("adapter_description")
        if (
            isinstance(power_source, str)
            and power_source
            and not isinstance(watts, bool)
            and isinstance(watts, int | float)
            and math.isfinite(float(watts))
            and float(watts) > 0.0
            and isinstance(description, str)
            and description
        ):
            power_identity = {
                "power_source": power_source,
                "adapter_watts": float(watts),
                "adapter_description": description,
            }
            break

    calibration_sha = next(
        (
            artifact_sha
            for calibration in _nested_named_mappings(
                metadata, "instrument_calibration"
            )
            if _sha256_text(
                artifact_sha := calibration.get("artifact_sha256")
            )
        ),
        None,
    )
    if (
        os_build is None
        or power_identity is None
        or calibration_sha is None
    ):
        return None
    return {
        "os_build": os_build,
        "power_supply_identity_sha256": canonical_sha256(power_identity),
        "calibration_identity_sha256": calibration_sha,
    }


def build_neg8_freshness_observation(
    metadata_values: Sequence[Any],
    *,
    evaluated_at_s: Any = None,
) -> dict[str, Any]:
    """Build the current binding observation used by the freshness gate."""

    timestamp = _finite_number(
        time.time() if evaluated_at_s is None else evaluated_at_s
    )
    bindings = [
        neg8_freshness_bindings_from_metadata(metadata)
        for metadata in metadata_values
    ]
    resolved = [binding for binding in bindings if binding is not None]
    unique = {
        canonical_sha256(binding): binding
        for binding in resolved
    }
    if len(resolved) != len(bindings) or not bindings:
        binding_status = "missing"
        observed = None
    elif len(unique) != 1:
        binding_status = "conflict"
        observed = None
    else:
        binding_status = "resolved"
        observed = dict(next(iter(unique.values())))
    return {
        "evaluated_at_s": timestamp,
        "binding_status": binding_status,
        "bindings": observed,
        "member_count": len(bindings),
        "resolved_member_count": len(resolved),
    }


def evaluate_neg8_bound_freshness(
    artifact: Mapping[str, Any],
    observation: Any,
) -> dict[str, Any]:
    """Evaluate horizon and exact binding triggers for one bound artifact."""

    freshness = artifact.get("freshness")
    observed = (
        observation.get("bindings")
        if isinstance(observation, Mapping)
        else None
    )
    evaluated_at = (
        _finite_number(observation.get("evaluated_at_s"))
        if isinstance(observation, Mapping)
        else None
    )
    triggers: list[str] = []
    derived_at: float | None = None
    expires_at: float | None = None
    artifact_bindings: Mapping[str, Any] | None = None
    if not isinstance(freshness, Mapping):
        triggers.append("freshness_fields_missing")
    else:
        derived_at = _finite_number(freshness.get("derived_at_s"))
        max_age = _finite_number(freshness.get("max_age_s"), positive=True)
        artifact_bindings = (
            freshness.get("bindings")
            if isinstance(freshness.get("bindings"), Mapping)
            else None
        )
        if (
            derived_at is None
            or max_age != float(NEG8_DRIFT_BOUND_MAX_AGE_S)
            or artifact_bindings is None
        ):
            triggers.append("freshness_fields_invalid")
        else:
            expires_at = derived_at + max_age
    if (
        not isinstance(observation, Mapping)
        or observation.get("binding_status") != "resolved"
        or not isinstance(observed, Mapping)
        or evaluated_at is None
    ):
        triggers.append("freshness_observation_unresolved")
    if (
        derived_at is not None
        and evaluated_at is not None
        and evaluated_at < derived_at
    ):
        triggers.append("evaluation_precedes_derivation")
    if (
        expires_at is not None
        and evaluated_at is not None
        and evaluated_at > expires_at
    ):
        triggers.append("validity_horizon_expired")
    for field, trigger in (
        ("os_build", "os_build_change"),
        ("power_supply_identity_sha256", "power_supply_change"),
        ("calibration_identity_sha256", "calibration_identity_change"),
    ):
        if (
            isinstance(artifact_bindings, Mapping)
            and isinstance(observed, Mapping)
            and artifact_bindings.get(field) != observed.get(field)
        ):
            triggers.append(trigger)
    unique_triggers = list(dict.fromkeys(triggers))
    return {
        "decision": "stale" if unique_triggers else "fresh",
        "condition": (
            CONDITION_NEG8_DRIFT_BOUND_STALE
            if unique_triggers
            else None
        ),
        "evaluated_at_s": evaluated_at,
        "derived_at_s": derived_at,
        "expires_at_s": expires_at,
        "max_age_s": (
            freshness.get("max_age_s")
            if isinstance(freshness, Mapping)
            else None
        ),
        "artifact_bindings": (
            dict(artifact_bindings)
            if isinstance(artifact_bindings, Mapping)
            else None
        ),
        "observed_bindings": (
            dict(observed) if isinstance(observed, Mapping) else None
        ),
        "observation_binding_status": (
            observation.get("binding_status")
            if isinstance(observation, Mapping)
            else None
        ),
        "triggered_rederivation_reasons": unique_triggers,
    }


def build_neg8_drift_bound_artifact(
    *,
    corpus_id: str,
    condition_id: str,
    manifest_sha256: str,
    scientific_config_sha256: str,
    members: Sequence[Mapping[str, Any]],
    derivation_timestamp_s: Any,
    freshness_bindings: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the dual-family D-054-style point-contrast guard artifact."""

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
    derived_at = _finite_number(derivation_timestamp_s)
    if derived_at is None or derived_at < 0.0:
        raise ValueError(
            "NEG-8 derivation_timestamp_s must be finite and nonnegative"
        )
    freshness_binding_keys = {
        "os_build",
        "power_supply_identity_sha256",
        "calibration_identity_sha256",
    }
    if (
        not isinstance(freshness_bindings, Mapping)
        or set(freshness_bindings) != freshness_binding_keys
        or not isinstance(freshness_bindings.get("os_build"), str)
        or not freshness_bindings.get("os_build")
        or not _sha256_text(
            freshness_bindings.get("power_supply_identity_sha256")
        )
        or not _sha256_text(
            freshness_bindings.get("calibration_identity_sha256")
        )
    ):
        raise ValueError("NEG-8 freshness bindings are invalid")
    normalized_members: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for member in members:
        if not isinstance(member, Mapping) or set(member) != {
            "bundle_id",
            "point_gross_j",
            "point_idle_subtracted_j",
            "bundle_evidence_sha256",
        }:
            raise ValueError(
                "NEG-8 reference members require bundle_id, point_gross_j, "
                "point_idle_subtracted_j, and bundle_evidence_sha256"
            )
        bundle_id = member.get("bundle_id")
        gross_point = _finite_number(member.get("point_gross_j"), positive=True)
        idle_subtracted_point = _finite_number(
            member.get("point_idle_subtracted_j")
        )
        evidence_sha = member.get("bundle_evidence_sha256")
        if (
            not isinstance(bundle_id, str)
            or not bundle_id
            or bundle_id in seen_ids
            or gross_point is None
            or idle_subtracted_point is None
            or not _sha256_text(evidence_sha)
        ):
            raise ValueError("NEG-8 reference corpus member is invalid or duplicated")
        seen_ids.add(bundle_id)
        normalized_members.append(
            {
                "bundle_id": bundle_id,
                "point_gross_j": gross_point,
                "point_idle_subtracted_j": idle_subtracted_point,
                "bundle_evidence_sha256": evidence_sha,
            }
        )
    n = len(normalized_members)
    if n < NEG8_DRIFT_MINIMUM_N:
        raise ValueError(
            f"NEG-8 reference corpus requires n >= {NEG8_DRIFT_MINIMUM_N}"
        )
    def family_estimator(point_field: str) -> dict[str, Any]:
        points = [member[point_field] for member in normalized_members]
        sample_range = max(points) - min(points)
        sample_stddev = statistics.stdev(points)
        t_critical = student_t_critical_95(n - 1)
        single_prediction = t_critical * sample_stddev * math.sqrt(2.0)
        single_bound = max(sample_range, single_prediction)
        ordered = sorted(points)
        replicated_range = (
            statistics.fmean(ordered[-NEG8_REPLICATED_ENDPOINT_N:])
            - statistics.fmean(ordered[:NEG8_REPLICATED_ENDPOINT_N])
        )
        replicated_prediction = (
            t_critical
            * sample_stddev
            * math.sqrt(2.0 / NEG8_REPLICATED_ENDPOINT_N)
        )
        replicated_bound = max(replicated_range, replicated_prediction)
        if single_bound <= 0.0 or replicated_bound <= 0.0:
            raise ValueError(
                "NEG-8 reference corpus must derive strictly positive bounds"
            )
        return {
            "id": NEG8_DRIFT_ESTIMATOR_ID,
            "minimum_n": NEG8_DRIFT_MINIMUM_N,
            "n": n,
            "sample_range_j": sample_range,
            "sample_stddev_j": sample_stddev,
            "student_t_critical_95": t_critical,
            "prediction_two_point_j": single_prediction,
            "single_member_endpoint_bound_j": single_bound,
            "replicated_endpoint_n": NEG8_REPLICATED_ENDPOINT_N,
            "replicated_endpoint_sample_range_j": replicated_range,
            "prediction_two_endpoint_means_j": replicated_prediction,
            "replicated_endpoint_bound_j": replicated_bound,
            "single_member_formula": (
                "max(sample_range_j,"
                "t_0.975,n-1*sample_stddev_j*sqrt(2))"
            ),
            "replicated_endpoint_formula": (
                "max(mean(largest_3)-mean(smallest_3),"
                "t_0.975,n-1*sample_stddev_j*sqrt(2/3))"
            ),
        }

    gross_estimator = family_estimator("point_gross_j")
    idle_subtracted_estimator = family_estimator("point_idle_subtracted_j")
    family_bounds = {
        NEG8_CLAIM_FAMILY_GROSS: {
            "estimand": NEG8_POINT_DRIFT_ESTIMAND,
            "point_field": "point_gross_j",
            "estimator": gross_estimator,
        },
        NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED: {
            "estimand": NEG8_IDLE_SUB_POINT_DRIFT_ESTIMAND,
            "point_field": "point_idle_subtracted_j",
            "estimator": idle_subtracted_estimator,
        },
    }
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
        # Gross top-level aliases preserve the amended-v1 pair-window wire.
        "estimator": gross_estimator,
        "bound_j": gross_estimator["single_member_endpoint_bound_j"],
        "claim_family_bounds": family_bounds,
        "freshness": {
            "derived_at_s": derived_at,
            "max_age_s": NEG8_DRIFT_BOUND_MAX_AGE_S,
            "bindings": dict(freshness_bindings),
            "rederivation_triggers": [
                "os_build_change",
                "power_supply_change",
                "calibration_identity_change",
                "validity_horizon_expired",
            ],
        },
    }
    return {**payload, "derivation_sha256": canonical_sha256(payload)}


def validate_neg8_drift_bound_artifact(value: Any) -> bool:
    """Validate the seal and arithmetic for current or replayable v1 wires.

    A sealed pre-freshness v1 wire remains parseable so the evaluator can
    classify it as stale with the dedicated condition. It is never fresh.
    """

    base_keys = {
        "schema_version",
        "estimand",
        "reference_corpus",
        "estimator",
        "bound_j",
        "claim_family_bounds",
        "derivation_sha256",
    }
    if (
        not isinstance(value, Mapping)
        or frozenset(value)
        not in {frozenset(base_keys), frozenset(base_keys | {"freshness"})}
    ):
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
        or not isinstance(value.get("claim_family_bounds"), Mapping)
    ):
        return False
    members = corpus.get("members")
    member_ids = corpus.get("member_ids")
    if not isinstance(members, list) or not isinstance(member_ids, list):
        return False
    try:
        freshness = value.get("freshness")
        current = isinstance(freshness, Mapping)
        expected = build_neg8_drift_bound_artifact(
            corpus_id=corpus.get("corpus_id"),
            condition_id=corpus.get("condition_id"),
            manifest_sha256=corpus.get("manifest_sha256"),
            scientific_config_sha256=corpus.get("scientific_config_sha256"),
            members=members,
            derivation_timestamp_s=(
                freshness.get("derived_at_s") if current else 0.0
            ),
            freshness_bindings=(
                freshness.get("bindings")
                if current
                else {
                    "os_build": "legacy-wire",
                    "power_supply_identity_sha256": "0" * 64,
                    "calibration_identity_sha256": "0" * 64,
                }
            ),
        )
    except (TypeError, ValueError, statistics.StatisticsError):
        return False
    if not current:
        expected.pop("freshness")
        expected["derivation_sha256"] = canonical_sha256(
            {
                key: item
                for key, item in expected.items()
                if key != "derivation_sha256"
            }
        )
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


def _as_reference_values(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(
        value, (str, bytes, bytearray, Mapping)
    ):
        return list(value)
    return [] if value is None else [value]


def _endpoint_point_summary(values: Sequence[Any]) -> dict[str, Any] | None:
    points = [_finite_number(value) for value in values]
    if not points or any(point is None for point in points):
        return None
    normalized = [float(point) for point in points]
    return {
        "n": len(normalized),
        "mean_j": statistics.fmean(normalized),
        "standard_error_j": (
            statistics.stdev(normalized) / math.sqrt(len(normalized))
            if len(normalized) > 1
            else None
        ),
        "member_points_j": normalized,
    }


def _endpoint_admissible_summary(values: Sequence[Any]) -> dict[str, Any] | None:
    sets = [_admissible_energy_set(value) for value in values]
    if not sets or any(item is None for item in sets):
        return None
    normalized = [item for item in sets if item is not None]
    points = [item[0] for item in normalized]
    return {
        "n": len(normalized),
        "mean_j": statistics.fmean(points),
        "standard_error_j": (
            statistics.stdev(points) / math.sqrt(len(points))
            if len(points) > 1
            else None
        ),
        "member_points_j": points,
        "mean_admissible_set_j": {
            "point_j": statistics.fmean(points),
            "lower_j": statistics.fmean(item[1] for item in normalized),
            "upper_j": statistics.fmean(item[2] for item in normalized),
        },
    }


def _family_bound(
    artifact: Mapping[str, Any] | None, family: str, protocol: str
) -> float | None:
    families = (
        artifact.get("claim_family_bounds")
        if isinstance(artifact, Mapping)
        else None
    )
    family_record = families.get(family) if isinstance(families, Mapping) else None
    estimator = (
        family_record.get("estimator")
        if isinstance(family_record, Mapping)
        else None
    )
    field = (
        "replicated_endpoint_bound_j"
        if protocol == "replicated_endpoints_with_midpoint"
        else "single_member_endpoint_bound_j"
    )
    return (
        _finite_number(estimator.get(field), positive=True)
        if isinstance(estimator, Mapping)
        else None
    )


def neg8_claim_family_for_metric(metric_name: Any) -> str:
    """Map governed energy metrics onto the two NEG-8 claim families."""

    return (
        NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED
        if metric_name in {"energy_request_j", "idle_subtracted_energy_j"}
        else NEG8_CLAIM_FAMILY_GROSS
    )


def _family_drift_record(
    *,
    family: str,
    start: Mapping[str, Any],
    midpoint: Mapping[str, Any] | None,
    end: Mapping[str, Any],
    protocol: str,
    artifact: Mapping[str, Any] | None,
    duration_s: float | None,
) -> dict[str, Any]:
    point_delta = abs(float(end["mean_j"]) - float(start["mean_j"]))
    trajectory_points = [float(start["mean_j"]), float(end["mean_j"])]
    if midpoint is not None:
        trajectory_points.insert(1, float(midpoint["mean_j"]))
    excursion = max(trajectory_points) - min(trajectory_points)
    derived_bound = _family_bound(artifact, family, protocol)
    allowance = (
        max(excursion, derived_bound)
        if derived_bound is not None
        else None
    )
    return {
        "claim_family": family,
        "endpoint_protocol": protocol,
        "start": dict(start),
        "midpoint": dict(midpoint) if midpoint is not None else None,
        "end": dict(end),
        "point_delta_j": point_delta,
        "combined_endpoint_standard_error_j": (
            math.sqrt(
                float(start["standard_error_j"]) ** 2
                + float(end["standard_error_j"]) ** 2
            )
            if start.get("standard_error_j") is not None
            and end.get("standard_error_j") is not None
            else None
        ),
        "screen_statistic_j": point_delta,
        "screen_statistic_definition": "abs(end_endpoint_mean-start_endpoint_mean)",
        "derived_repeatability_bound_j": derived_bound,
        "screen_passed": (
            point_delta <= derived_bound
            if derived_bound is not None
            else False
        ),
        "trajectory_excursion_max_j": excursion,
        "drift_allowance_j": allowance,
        "allowance_formula": (
            "max(trajectory_excursion_max_j,derived_repeatability_bound_j)"
        ),
        "window_duration_s": duration_s,
        "duration_scaling": "not_applied_no_governed_time_law",
        "provenance": {
            "bound_derivation_sha256": (
                artifact.get("derivation_sha256")
                if isinstance(artifact, Mapping)
                else None
            ),
            "observed_component": "trajectory_excursion_max_j",
            "derived_component": "derived_repeatability_bound_j",
        },
    }


def evaluate_neg8_point_drift(
    start_gross_j: Any,
    end_gross_j: Any,
    policy: Neg8BracketPolicy,
    drift_bound_artifact: Any,
    *,
    start_idle_subtracted_j: Any = None,
    end_idle_subtracted_j: Any = None,
    midpoint_gross_j: Any = None,
    midpoint_idle_subtracted_j: Any = None,
    window_duration_s: Any = None,
    bound_freshness_observation: Any = None,
) -> dict[str, Any]:
    """Gate both claim families and mint non-vanishing drift allowances."""

    conditions: set[str] = set()
    artifact = (
        dict(drift_bound_artifact)
        if validate_neg8_drift_bound_artifact(drift_bound_artifact)
        else None
    )
    if artifact is None:
        conditions.add(CONDITION_NEG8_DRIFT_BOUND_UNDERIVED)
        conditions.add(CONDITION_NEG8_IDLE_SUB_DRIFT_BOUND_UNDERIVED)
        bound_freshness = {
            "decision": "underived",
            "condition": None,
            "evaluated_at_s": None,
            "derived_at_s": None,
            "expires_at_s": None,
            "max_age_s": None,
            "artifact_bindings": None,
            "observed_bindings": None,
            "observation_binding_status": None,
            "triggered_rederivation_reasons": [],
        }
    else:
        bound_freshness = evaluate_neg8_bound_freshness(
            artifact, bound_freshness_observation
        )
        if bound_freshness["decision"] != "fresh":
            conditions.add(CONDITION_NEG8_DRIFT_BOUND_STALE)

    start_gross_values = _as_reference_values(start_gross_j)
    midpoint_gross_values = _as_reference_values(midpoint_gross_j)
    end_gross_values = _as_reference_values(end_gross_j)
    start_idle_values = _as_reference_values(start_idle_subtracted_j)
    midpoint_idle_values = _as_reference_values(midpoint_idle_subtracted_j)
    end_idle_values = _as_reference_values(end_idle_subtracted_j)
    gross_counts = (
        len(start_gross_values),
        len(midpoint_gross_values),
        len(end_gross_values),
    )
    idle_counts = (
        len(start_idle_values),
        len(midpoint_idle_values),
        len(end_idle_values),
    )
    if gross_counts == (1, 0, 1) and idle_counts == (1, 0, 1):
        protocol = "legacy_single_member_endpoints"
    elif (
        gross_counts
        == (
            NEG8_REPLICATED_ENDPOINT_N,
            1,
            NEG8_REPLICATED_ENDPOINT_N,
        )
        and idle_counts == gross_counts
    ):
        protocol = "replicated_endpoints_with_midpoint"
    else:
        protocol = "invalid"
    if not start_gross_values or not end_gross_values:
        conditions.add("neg8_bracket_missing")
    if protocol == "invalid":
        conditions.add("neg8_bracket_reference_invalid")

    start_gross = _endpoint_admissible_summary(start_gross_values)
    midpoint_gross = _endpoint_admissible_summary(midpoint_gross_values)
    end_gross = _endpoint_admissible_summary(end_gross_values)
    start_idle = _endpoint_point_summary(start_idle_values)
    midpoint_idle = _endpoint_point_summary(midpoint_idle_values)
    end_idle = _endpoint_point_summary(end_idle_values)
    required_summaries = (start_gross, end_gross, start_idle, end_idle)
    if protocol == "replicated_endpoints_with_midpoint":
        required_summaries = (*required_summaries, midpoint_gross, midpoint_idle)
    if any(summary is None for summary in required_summaries):
        conditions.add("neg8_bracket_reference_invalid")

    duration = _finite_number(window_duration_s)
    if duration is not None and duration < 0.0:
        duration = None
    family_records: dict[str, dict[str, Any]] = {}
    if (
        protocol != "invalid"
        and start_gross is not None
        and end_gross is not None
        and start_idle is not None
        and end_idle is not None
        and (
            protocol == "legacy_single_member_endpoints"
            or (midpoint_gross is not None and midpoint_idle is not None)
        )
    ):
        family_records[NEG8_CLAIM_FAMILY_GROSS] = _family_drift_record(
            family=NEG8_CLAIM_FAMILY_GROSS,
            start=start_gross,
            midpoint=midpoint_gross,
            end=end_gross,
            protocol=protocol,
            artifact=artifact,
            duration_s=duration,
        )
        family_records[NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED] = _family_drift_record(
            family=NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED,
            start=start_idle,
            midpoint=midpoint_idle,
            end=end_idle,
            protocol=protocol,
            artifact=artifact,
            duration_s=duration,
        )
        if (
            artifact is not None
            and not family_records[NEG8_CLAIM_FAMILY_GROSS]["screen_passed"]
        ):
            conditions.add(CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED)
        if (
            artifact is not None
            and not family_records[NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED][
                "screen_passed"
            ]
        ):
            conditions.add(CONDITION_NEG8_IDLE_SUB_POINT_DRIFT_EXCEEDED)

    point_delta = (
        family_records.get(NEG8_CLAIM_FAMILY_GROSS, {}).get("point_delta_j")
    )
    point_relative = (
        point_delta / float(start_gross["mean_j"])
        if point_delta is not None
        and start_gross is not None
        and float(start_gross["mean_j"]) != 0.0
        else None
    )
    corner_delta: float | None = None
    corner_relative: float | None = None
    if start_gross is not None and end_gross is not None:
        start_set = start_gross["mean_admissible_set_j"]
        end_set = end_gross["mean_admissible_set_j"]
        start_point, start_lower, start_upper = (
            start_set["point_j"],
            start_set["lower_j"],
            start_set["upper_j"],
        )
        end_point, end_lower, end_upper = (
            end_set["point_j"],
            end_set["lower_j"],
            end_set["upper_j"],
        )
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
    evidence_failure = conditions & {
        CONDITION_NEG8_DRIFT_BOUND_UNDERIVED,
        CONDITION_NEG8_IDLE_SUB_DRIFT_BOUND_UNDERIVED,
        CONDITION_NEG8_DRIFT_BOUND_STALE,
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
        "endpoint_protocol": protocol,
        "decision": decision,
        "passed": decision == "passed",
        "conditions": sorted(conditions),
        "start_gross_j": (
            float(start_gross["mean_j"]) if start_gross is not None else None
        ),
        "end_gross_j": (
            float(end_gross["mean_j"]) if end_gross is not None else None
        ),
        "start_admissible_set_j": (
            dict(start_gross["mean_admissible_set_j"])
            if start_gross is not None
            else None
        ),
        "end_admissible_set_j": (
            dict(end_gross["mean_admissible_set_j"])
            if end_gross is not None
            else None
        ),
        "abs_delta_j": point_delta,
        "rel_delta": point_relative,
        "corner_abs_delta_j": corner_delta,
        "corner_rel_delta": corner_relative,
        "corner_statistic_role": "diagnostic_not_gating",
        "idle_subtracted_companion": {
            "start_point_j": (
                float(start_idle["mean_j"]) if start_idle is not None else None
            ),
            "end_point_j": (
                float(end_idle["mean_j"]) if end_idle is not None else None
            ),
            "abs_delta_j": family_records.get(
                NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED, {}
            ).get("point_delta_j"),
            "role": "claim_family_screen_and_budget",
        },
        "claim_families": family_records,
        "drift_allowances": {
            family: {
                "claim_family": family,
                "allowance_j": record["drift_allowance_j"],
                "observed_trajectory_excursion_j": record[
                    "trajectory_excursion_max_j"
                ],
                "derived_repeatability_bound_j": record[
                    "derived_repeatability_bound_j"
                ],
                "provenance": dict(record["provenance"]),
            }
            for family, record in family_records.items()
        },
        # The v1 sidecar fields remain recorded for legacy wire compatibility;
        # neither numeric tolerance gates this amended estimand.
        "policy": {
            "require_bracket": policy.require_bracket,
            "max_abs_delta_j": policy.max_abs_delta_j,
            "max_rel_delta": policy.max_rel_delta,
        },
        "drift_bound_artifact": artifact,
        "bound_freshness": bound_freshness,
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
    consumption_semantics_id: str = MINTED_CONSUMPTION_SEMANTICS_ID,
    consumption_provenance: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Bind one verdict to physical member bytes and its calibration pair."""

    if consumption_semantics_id not in {
        MINTED_CONSUMPTION_SEMANTICS_ID,
        MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    }:
        raise ValueError(
            f"unknown whole-window consumption semantics: {consumption_semantics_id!r}"
        )
    if (
        consumption_semantics_id == MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
        and not isinstance(consumption_provenance, Mapping)
    ):
        raise ValueError(
            "max-bracket consumption semantics require complete provenance"
        )

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
        "consumption_semantics_id": consumption_semantics_id,
    }
    if consumption_semantics_id == MAX_BRACKET_CONSUMPTION_SEMANTICS_ID:
        assert isinstance(consumption_provenance, Mapping)
        expected_ids = {
            value.get("bundle_id")
            for value in occurrences
            if isinstance(value.get("bundle_id"), str)
        }
        if set(consumption_provenance) != expected_ids:
            raise ValueError(
                "max-bracket consumption provenance must cover every basis member"
            )
        payload["consumption_provenance"] = {
            bundle_id: dict(consumption_provenance[bundle_id])
            for bundle_id in sorted(consumption_provenance)
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
        and member.get("execution") in {"invoked", "existing"}
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


def occurrence_descriptor_identity(
    value: Any,
) -> tuple[str, int, int] | None:
    """Reduce one occurrence descriptor to its manifest-position identity.

    The triple is the only thing two joins can compare without re-reading
    manifests: the runs-root-relative source manifest path plus the member
    and bundle indices inside it.  Anything malformed returns ``None`` so
    callers fail closed rather than matching on a partial identity.
    """

    if not isinstance(value, Mapping):
        return None
    source = value.get("source_manifest")
    path = source.get("path") if isinstance(source, Mapping) else None
    member_index = value.get("member_index")
    bundle_index = value.get("bundle_index")
    if (
        not isinstance(path, str)
        or not path
        or isinstance(member_index, bool)
        or not isinstance(member_index, int)
        or member_index < 0
        or isinstance(bundle_index, bool)
        or not isinstance(bundle_index, int)
        or bundle_index < 0
    ):
        return None
    return (path, member_index, bundle_index)


def supersession_entry_validation_results(
    runs_root: Path, log_path: Path | None = None
) -> tuple[list[dict[str, Any]], list[bool]] | None:
    """Return recognizable raw supersessions and their current validations.

    ``None`` is the global fail-closed result: the log was unreadable, a
    non-empty line was not JSON/object-shaped, or a supersession-shaped row
    could not be assigned to a non-empty ``bundle_id``.  A recognizable row
    with a bundle id remains visible even when its custody validation fails;
    callers therefore cannot erase ambiguity by filtering malformed records.
    A missing log is the ordinary no-supersession case.
    """

    path = (
        Path(log_path)
        if log_path is not None
        else Path(runs_root) / "campaign_log.jsonl"
    )
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return ([], [])
    except (OSError, UnicodeDecodeError):
        return None
    entries: list[dict[str, Any]] = []
    validations: list[bool] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            return None
        if not isinstance(value, dict):
            return None
        recognizable = (
            value.get("record_type") == "campaign_occurrence_supersession"
            or value.get("schema_version") == OCCURRENCE_SUPERSESSION_SCHEMA
        )
        if not recognizable:
            continue
        bundle_id = value.get("bundle_id")
        if not isinstance(bundle_id, str) or not bundle_id:
            return None
        entries.append(value)
        validations.append(validate_occurrence_supersession_entry(value, runs_root))
    return entries, validations


def validated_supersession_entries(
    runs_root: Path, log_path: Path | None = None
) -> list[dict[str, Any]]:
    """Return campaign-log supersessions that validate against current bytes.

    Every entry is re-checked against current bytes by
    :func:`supersession_entry_validation_results`.  This compatibility view
    intentionally filters invalid rows; ambiguity-sensitive joins must use
    that raw-plus-validation reader instead.
    """

    result = supersession_entry_validation_results(runs_root, log_path)
    if result is None:
        return []
    entries, validations = result
    return [entry for entry, valid in zip(entries, validations, strict=True) if valid]


def supersession_selected_occurrence_identity(
    entries: Sequence[Mapping[str, Any]],
    bundle_id: str,
    declared: Sequence[tuple[str, int, int]],
) -> tuple[str, int, int] | None:
    """Name the selected occurrence when a record covers all declarations.

    Duplicate occurrence records are ambiguous evidence by default, and that
    default is what stops outlier laundering.  The single licensed exception
    is an explicit operator supersession artifact -- hash-bound, reason-
    bearing, and naming the quarantined copy -- and it licenses nothing wider
    than the declarations it actually names.  The record must therefore
    account for every declared occurrence and name no occurrence that was not
    declared; a partial record, an extra record, two competing records, or a
    repeated declared identity all return ``None`` and leave the caller's
    existing refusal in place.  Whether emitted rows equal this declaration
    set is the owning join's responsibility.
    """

    declared_key = sorted(declared)
    if len(declared_key) < 2 or len(set(declared_key)) != len(declared_key):
        return None
    candidates = [
        entry
        for entry in entries
        if isinstance(entry, Mapping) and entry.get("bundle_id") == bundle_id
    ]
    if len(candidates) != 1:
        return None
    entry = candidates[0]
    selected = occurrence_descriptor_identity(entry.get("selected_occurrence"))
    superseded_values = entry.get("superseded_occurrences")
    if selected is None or not isinstance(superseded_values, list):
        return None
    superseded = [
        occurrence_descriptor_identity(value) for value in superseded_values
    ]
    if any(value is None for value in superseded):
        return None
    named = sorted([selected, *(value for value in superseded if value)])
    if len(set(named)) != len(named) or named != declared_key:
        return None
    return selected


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
            _read_json_object(runs_root / bundle_id / "summary_metrics.json"),
            runs_root / bundle_id,
        )
        for bundle_id in result
    ):
        return None
    return result


def _neg8_position(role: Any, sentinel_position: Any) -> str | None:
    """Interpret the governed campaign-manifest NEG-8 role spellings."""

    if role == "neg8_daily_reference_start":
        return "start" if sentinel_position in (None, "start") else "invalid"
    if role == "neg8_daily_reference_end":
        return "end" if sentinel_position in (None, "end") else "invalid"
    if role == "neg8_daily_reference_midpoint":
        return (
            "midpoint"
            if sentinel_position in (None, "midpoint")
            else "invalid"
        )
    if role == "neg8_daily_reference":
        return (
            sentinel_position
            if sentinel_position in {"start", "midpoint", "end"}
            else "invalid"
        )
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


def _current_strict_summary(
    summary: Any, bundle_path: Path | None = None
) -> bool:
    """Identify current-mint, non-mock summaries that can bear strict claims."""

    quality = summary.get("measurement_quality") if isinstance(summary, Mapping) else None
    summary_class = _telemetry_backend_class(
        quality.get("telemetry_source") if isinstance(quality, Mapping) else None
    )
    if bundle_path is not None:
        identity = custody_telemetry_identity(
            bundle_path,
            summary=summary if isinstance(summary, Mapping) else None,
        )
        non_mock = (
            identity.triangle_agrees
            and identity.config_backend_class is not None
            and identity.config_backend_class != TelemetryBackend.MOCK.value
            if identity.custody_bound_config
            else summary_class != TelemetryBackend.MOCK.value
        )
    else:
        # Compatibility for pure summary fixtures. Real bundle dispatch passes
        # a path and therefore uses the custody-bound config when available.
        non_mock = summary_class != TelemetryBackend.MOCK.value
    return (
        _summary_reducer_version(summary) in CURRENT_MINT_REDUCER_VERSIONS
        and non_mock
    )


def _custody_strict_invalid(
    bundle_path: Path,
    summary: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> bool:
    """Identify custody-bound bundles whose telemetry triangle disagrees."""

    identity = custody_telemetry_identity(
        bundle_path,
        summary=summary,
        metadata=metadata,
    )
    return identity.custody_bound_config and not identity.triangle_agrees


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


def _reference_energy_evidence(
    bundle_path: Path,
    *,
    require_idle_subtracted: bool = True,
) -> tuple[dict[str, float] | None, float | None, str | None]:
    """Re-derive both current NEG-8 claim-family points from primary bytes."""

    stored_summary = _read_json_object(bundle_path / "summary_metrics.json")
    stored_gross = _gross_fields(stored_summary)
    stored_idle = (
        _finite_number(stored_summary.get("idle_subtracted_energy_j"))
        if isinstance(stored_summary, Mapping)
        else None
    )
    reducer_version = _summary_reducer_version(stored_summary)
    if not _current_strict_summary(stored_summary, bundle_path):
        return (
            stored_gross,
            stored_idle,
            None
            if stored_gross is not None
            and (stored_idle is not None or not require_idle_subtracted)
            else "provenance",
        )
    try:
        # Deliberately output-free: reduce_bundle is pure over the bundle and
        # returns an in-memory summary.  Minutes-scale claim verification cost
        # is accepted for primary-evidence NEG-8 re-derivation.
        from joulewise.reduce import reduce_bundle

        reduced = reduce_bundle(bundle_path, reducer_version=reducer_version).to_dict()
    except Exception:  # noqa: BLE001 - any reducer/evidence failure refuses.
        return None, None, "provenance"
    fresh_gross = _gross_fields(reduced)
    fresh_idle = _finite_number(reduced.get("idle_subtracted_energy_j"))
    prechecks = reduced.get("window_evidence_precheck")
    gross_gate = None
    idle_gate = None
    if isinstance(prechecks, Mapping):
        gross_gate = prechecks.get("gross_request")
        if not isinstance(gross_gate, Mapping):
            gross_gate = prechecks.get("gross_batch_group")
        idle_gate = prechecks.get("idle_subtracted_request")
    if (
        reduced.get("status") != "succeeded"
        or fresh_gross is None
        or (require_idle_subtracted and fresh_idle is None)
        or not isinstance(gross_gate, Mapping)
        or gross_gate.get("eligible") is not True
        or (
            require_idle_subtracted
            and (
                not isinstance(idle_gate, Mapping)
                or idle_gate.get("eligible") is not True
            )
        )
    ):
        return None, None, "provenance"
    if stored_gross is None or any(
        not math.isclose(
            stored_gross[field], fresh_gross[field], rel_tol=1e-9, abs_tol=1e-9
        )
        for field in ("point_j", "lower_j", "upper_j")
    ) or (
        require_idle_subtracted
        and (
            stored_idle is None
            or fresh_idle is None
            or not math.isclose(
                stored_idle, fresh_idle, rel_tol=1e-9, abs_tol=1e-9
            )
        )
    ):
        return None, None, "conflict"
    return fresh_gross, fresh_idle, None


def _gross_energy_evidence(
    bundle_path: Path,
) -> tuple[dict[str, float] | None, str | None]:
    """Compatibility projection for frozen gross-only replay callers."""

    gross, _idle_subtracted, problem = _reference_energy_evidence(
        bundle_path, require_idle_subtracted=False
    )
    return gross, problem


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
    freshness_bindings: list[dict[str, str]] = []
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
        metadata = _read_json_object(bundle_path / "metadata.json")
        if _custody_strict_invalid(bundle_path, summary, metadata):
            raise ValueError(
                f"NEG-8 corpus member {bundle_id} custody telemetry triangle disagrees"
            )
        if not _current_strict_summary(summary, bundle_path):
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
        gross, idle_subtracted, problem = _reference_energy_evidence(bundle_path)
        if problem is not None or gross is None or idle_subtracted is None:
            raise ValueError(
                f"NEG-8 corpus member {bundle_id} dual-family evidence is invalid"
            )
        binding = neg8_freshness_bindings_from_metadata(metadata)
        if binding is None:
            raise ValueError(
                f"NEG-8 corpus member {bundle_id} freshness bindings are unavailable"
            )
        freshness_bindings.append(binding)
        evidence_members.append(
            {
                "bundle_id": bundle_id,
                "point_gross_j": gross["point_j"],
                "point_idle_subtracted_j": idle_subtracted,
                "bundle_evidence_sha256": _bundle_evidence_sha256(bundle_path),
            }
        )
    assert scientific_identity is not None
    unique_freshness = {
        canonical_sha256(binding): binding for binding in freshness_bindings
    }
    if len(unique_freshness) != 1:
        raise ValueError(
            "NEG-8 reference corpus freshness bindings are not identical"
        )
    return build_neg8_drift_bound_artifact(
        corpus_id=manifest.get("corpus_id"),
        condition_id=manifest.get("condition_id"),
        manifest_sha256=hashlib.sha256(raw).hexdigest(),
        scientific_config_sha256=scientific_identity,
        members=evidence_members,
        derivation_timestamp_s=time.time(),
        freshness_bindings=next(iter(unique_freshness.values())),
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
    return_bracket: bool = False,
    freshness_evaluated_at_s: Any = None,
) -> tuple[Any, str | None]:
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
    references: dict[
        str, list[tuple[dict[str, float] | None, float | None]]
    ] = {
        "start": [],
        "midpoint": [],
        "end": [],
    }
    reference_metadata: list[Mapping[str, Any] | None] = []
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
                    if point_drift:
                        frozen_gross, frozen_idle, _frozen_problem = (
                            _reference_energy_evidence(
                                runs_root / bundle_id,
                                require_idle_subtracted=True,
                            )
                        )
                    else:
                        frozen_gross, _frozen_problem = _gross_energy_evidence(
                            runs_root / bundle_id,
                        )
                        frozen_idle = None
                    references[position].append((frozen_gross, frozen_idle))
                    if point_drift:
                        reference_metadata.append(
                            _read_json_object(
                                runs_root / bundle_id / "metadata.json"
                            )
                        )
                    continue
                stored_summary = _read_json_object(bundle_path / "summary_metrics.json")
                if _custody_strict_invalid(bundle_path, stored_summary):
                    return None, "bundle_strict_invalid"
                if _current_strict_summary(stored_summary, bundle_path):
                    scientific_sha, canonical = _scientific_config_identity(bundle_path)
                    if (
                        member.get("canonical_neg8_workload") is not True
                        or not canonical
                        or scientific_sha is None
                        or member.get("scientific_config_sha256") != scientific_sha
                    ):
                        return None, "provenance"
                if point_drift:
                    gross, idle_subtracted, problem = (
                        _reference_energy_evidence(
                            bundle_path,
                            require_idle_subtracted=True,
                        )
                    )
                else:
                    gross, problem = _gross_energy_evidence(bundle_path)
                    idle_subtracted = None
                if problem is not None:
                    return None, problem
                references[position].append((gross, idle_subtracted))
                if point_drift:
                    reference_metadata.append(
                        _read_json_object(bundle_path / "metadata.json")
                    )
    legacy_pair = (
        len(references["start"]) == 1
        and not references["midpoint"]
        and len(references["end"]) == 1
    )
    replicated = (
        len(references["start"]) == NEG8_REPLICATED_ENDPOINT_N
        and len(references["midpoint"]) == 1
        and len(references["end"]) == NEG8_REPLICATED_ENDPOINT_N
    )
    shape_valid = legacy_pair or (point_drift and replicated)
    start_gross = (
        [item[0] for item in references["start"]]
        if shape_valid
        else None
    )
    midpoint_gross = (
        [item[0] for item in references["midpoint"]]
        if shape_valid and references["midpoint"]
        else None
    )
    end_gross = (
        [item[0] for item in references["end"]]
        if shape_valid
        else None
    )
    if invalid_role:
        start_gross = midpoint_gross = end_gross = None
    if point_drift:
        bracket = evaluate_neg8_point_drift(
            start_gross,
            end_gross,
            policy,
            drift_bound_artifact,
            start_idle_subtracted_j=(
                [item[1] for item in references["start"]]
                if shape_valid
                else None
            ),
            midpoint_gross_j=midpoint_gross,
            midpoint_idle_subtracted_j=(
                [item[1] for item in references["midpoint"]]
                if shape_valid and references["midpoint"]
                else None
            ),
            end_idle_subtracted_j=(
                [item[1] for item in references["end"]]
                if shape_valid
                else None
            ),
            bound_freshness_observation=build_neg8_freshness_observation(
                reference_metadata,
                evaluated_at_s=freshness_evaluated_at_s,
            ),
        )
        return (bracket if return_bracket else bracket["decision"], None)
    start = start_gross[0] if legacy_pair and start_gross else None
    end = end_gross[0] if legacy_pair and end_gross else None
    bracket = evaluate_neg8_bracket(start, end, policy)
    return (bracket if return_bracket else bracket["decision"], None)


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
                    _read_json_object(path / "summary_metrics.json"),
                    path,
                ) or _current_strict_summary(
                    _read_json_object(result[bundle_id] / "summary_metrics.json"),
                    result[bundle_id],
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
    consumption_session: AuthenticatedConsumptionSession | None = None,
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
    if any(
        (path := probe_paths.get(bundle_id)) is not None
        and _custody_strict_invalid(
            path,
            _read_json_object(path / "summary_metrics.json"),
            _read_json_object(path / "metadata.json"),
        )
        for bundle_id in bundle_ids
    ):
        reasons.add("bundle_strict_invalid")
    strict_current_ids = {
        bundle_id
        for bundle_id in bundle_ids
        if (path := probe_paths.get(bundle_id)) is not None
        and _current_strict_summary(
            _read_json_object(path / "summary_metrics.json"),
            path,
        )
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
        reasons.add("whole_window_verdict_provenance_invalid")
        return reasons
    try:
        extension = IdleAdmissionExtension.from_mapping(
            dict(extension_value) if isinstance(extension_value, Mapping) else None,
            profile=profile,
        )
    except (TypeError, ValueError):
        reasons.add("whole_window_verdict_provenance_invalid")
        return reasons
    try:
        registered_typed_policy = CampaignPolicy.from_mapping(dict(registered))
    except (TypeError, ValueError):
        reasons.add("whole_window_verdict_provenance_invalid")
        return reasons
    if paths is None:
        reasons.add("whole_window_verdict_provenance_invalid")
        return reasons

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
        if consumption_session is not None:
            consumption_session._prepare(
                bundle_paths={
                    bundle_id: path
                    for bundle_id, path, _metadata, _cpu in derived_members
                },
                policy=registered_typed_policy,
            )
            calibration_bracket = (
                dict(consumption_session.calibration_bracket)
                if isinstance(
                    consumption_session.calibration_bracket, Mapping
                )
                else None
            )
            calibration_reasons = consumption_session.refusal_reasons
        else:
            calibration_bracket, calibration_reasons = (
                calibration_bracket_for_bundles(
                    runs_root,
                    [
                        path
                        for _bundle_id, path, _metadata, _cpu in derived_members
                    ],
                    registered_typed_policy.calibration_bracketing,
                )
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
        if (
            consumption_session is None
            and not isinstance(bracket_bound, bool)
            and isinstance(bracket_bound, int | float)
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


def _row_consumption_semantics_id(row: Mapping[str, Any]) -> str:
    basis = row.get("evaluation_basis")
    value = (
        basis.get("consumption_semantics_id")
        if isinstance(basis, Mapping)
        else None
    )
    if value is None:
        value = row.get("consumption_semantics_id")
    return (
        value
        if isinstance(value, str)
        else MINTED_CONSUMPTION_SEMANTICS_ID
    )


def _consumption_provenance_valid(
    basis: Mapping[str, Any],
    occurrences: Sequence[Mapping[str, Any]],
    *,
    runs_root: Path,
    consumption_session: AuthenticatedConsumptionSession | None,
) -> bool:
    semantics_id = basis.get(
        "consumption_semantics_id",
        MINTED_CONSUMPTION_SEMANTICS_ID,
    )
    provenance = basis.get("consumption_provenance")
    if semantics_id == MINTED_CONSUMPTION_SEMANTICS_ID:
        return provenance is None
    if semantics_id != MAX_BRACKET_CONSUMPTION_SEMANTICS_ID or not isinstance(
        provenance, Mapping
    ):
        return False
    session_ready = (
        consumption_session is not None
        and consumption_session.ready
        and Path(runs_root) == consumption_session.runs_root
    )
    occurrence_ids = {
        value.get("bundle_id")
        for value in occurrences
        if isinstance(value.get("bundle_id"), str)
    }
    occurrences_by_id = {
        value.get("bundle_id"): value
        for value in occurrences
        if isinstance(value, Mapping)
        and isinstance(value.get("bundle_id"), str)
    }
    # Explicit digest selection deliberately permits a basis whose
    # occurrences cover more than the requested replay subset. The ordinary
    # path remains exact-set selection.
    if (
        len(occurrence_ids) != len(occurrences)
        or len(occurrences_by_id) != len(occurrences)
        or set(provenance) != occurrence_ids
        or (
            session_ready
            and (
                (
                    consumption_session.evaluation_basis_sha256 is not None
                    and not set(
                        consumption_session.referenced_bundle_ids
                    ).issubset(occurrence_ids)
                )
                or (
                    consumption_session.evaluation_basis_sha256 is None
                    and occurrence_ids
                    != set(consumption_session.referenced_bundle_ids)
                )
            )
        )
    ):
        return False
    bracket_set = basis.get("calibration_bracket_set")
    authenticated_bracket = (
        consumption_session.calibration_bracket
        if session_ready
        else bracket_set
    )
    if (
        not isinstance(bracket_set, Mapping)
        or not isinstance(authenticated_bracket, Mapping)
        or (
            session_ready
            and {
                "pre": bracket_set.get("pre"),
                "post": bracket_set.get("post"),
            }
            != {
                "pre": authenticated_bracket.get("pre"),
                "post": authenticated_bracket.get("post"),
            }
        )
    ):
        return False
    pre_bound = _finite_number(
        (
            authenticated_bracket.get("pre") or {}
        ).get("b_fiducial_s")
        if isinstance(authenticated_bracket.get("pre"), Mapping)
        else None
    )
    post_bound = _finite_number(
        (
            authenticated_bracket.get("post") or {}
        ).get("b_fiducial_s")
        if isinstance(authenticated_bracket.get("post"), Mapping)
        else None
    )
    persisted_bracket_max = (
        max(pre_bound, post_bound)
        if pre_bound is not None and post_bound is not None
        else None
    )
    authenticated_operative = _finite_number(
        consumption_session.operative_fiducial_bound_s
        if session_ready
        else persisted_bracket_max
    )
    if (
        pre_bound is None
        or pre_bound < 0.0
        or post_bound is None
        or post_bound < 0.0
        or authenticated_operative is None
        or not math.isclose(
            authenticated_operative,
            max(pre_bound, post_bound),
            rel_tol=0.0,
            abs_tol=1e-12,
        )
    ):
        return False
    root = Path(runs_root).resolve()
    for bundle_id in sorted(occurrence_ids):
        record = provenance.get(bundle_id)
        expected_record = (
            consumption_session.provenance_for(bundle_id)
            if session_ready
            else record
        )
        if not isinstance(record, Mapping) or record.get(
            "consumption_semantics_id"
        ) != MAX_BRACKET_CONSUMPTION_SEMANTICS_ID:
            return False
        if (
            not isinstance(expected_record, Mapping)
            or dict(record) != dict(expected_record)
        ):
            return False
        dominated = record.get("minted_bound_dominated")
        minted = _finite_number(record.get("minted_fiducial_bound_s"))
        operative = _finite_number(record.get("operative_fiducial_bound_s"))
        calibration = record.get("calibration_bracket")
        envelopes = record.get("operative_envelopes")
        if (
            not isinstance(dominated, bool)
            or minted is None
            or minted < 0.0
            or operative is None
            or not math.isclose(
                operative,
                authenticated_operative,
                rel_tol=0.0,
                abs_tol=1e-12,
            )
            or operative < minted - 1e-12
            or dominated != (operative > minted + 1e-12)
            or not isinstance(calibration, Mapping)
            or {
                "pre": calibration.get("pre"),
                "post": calibration.get("post"),
            }
            != {
                "pre": bracket_set.get("pre"),
                "post": bracket_set.get("post"),
            }
            or not isinstance(envelopes, Mapping)
            or not envelopes
        ):
            return False
        for descriptor in (calibration.get("pre"), calibration.get("post")):
            if (
                not isinstance(descriptor, Mapping)
                or not _sha256_text(descriptor.get("manifest_sha256"))
                or not _sha256_text(descriptor.get("evidence_sha256"))
            ):
                return False
        if any(
            not isinstance(pointer, str)
            or not pointer.startswith("/")
            or _complete_envelope_record(envelope) is None
            or "half_width_j" not in envelope
            or not math.isclose(
                float(envelope["half_width_j"]),
                float(_complete_envelope_record(envelope)["half_width_j"]),
                rel_tol=0.0,
                abs_tol=1e-12,
            )
            for pointer, envelope in envelopes.items()
        ):
            return False
        occurrence_path = _safe_source_path(
            root, occurrences_by_id[bundle_id].get("bundle_path")
        )
        minted_summary = (
            _read_json_object(occurrence_path / "summary_metrics.json")
            if occurrence_path is not None
            else None
        )
        minted_envelopes = (
            minted_summary.get("energy_anchor_shift_envelopes")
            if isinstance(minted_summary, Mapping)
            else None
        )
        if not isinstance(minted_envelopes, Mapping) or set(envelopes) != set(
            minted_envelopes
        ):
            return False
    return True


def _validated_evaluation_basis(
    row: Mapping[str, Any],
    runs_root: Path,
    *,
    consumption_session: AuthenticatedConsumptionSession | None = None,
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
        or not _consumption_provenance_valid(
            basis,
            occurrences,
            runs_root=runs_root,
            consumption_session=consumption_session,
        )
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
    row: Mapping[str, Any],
    runs_root: Path,
    referenced: set[str],
    *,
    consumption_session: AuthenticatedConsumptionSession | None = None,
) -> tuple[bool, tuple[str, ...]]:
    """Authenticate a verdict row once per collection-scoped session."""

    cache_key: tuple[str, str, tuple[str, ...], str | None] | None = None
    if consumption_session is not None and not consumption_session.ready:
        consumption_session._row_validation_results.clear()
    if (
        consumption_session is not None
        and Path(runs_root) == consumption_session.runs_root
        and frozenset(referenced)
        == consumption_session.referenced_bundle_ids
    ):
        try:
            cache_key = (
                canonical_sha256(row),
                str(Path(runs_root).resolve()),
                tuple(sorted(referenced)),
                consumption_session.evaluation_basis_sha256,
            )
        except (TypeError, ValueError):
            cache_key = None
        if (
            cache_key is not None
            and consumption_session.ready
            and cache_key in consumption_session._row_validation_results
        ):
            return consumption_session._row_validation_results[cache_key]

    result = _validate_row_uncached(
        row,
        runs_root,
        referenced,
        consumption_session=consumption_session,
    )
    if (
        cache_key is not None
        and result[0]
        and consumption_session is not None
        and consumption_session.ready
    ):
        consumption_session._row_validation_results[cache_key] = result
    return result


def _validate_row_uncached(
    row: Mapping[str, Any],
    runs_root: Path,
    referenced: set[str],
    *,
    consumption_session: AuthenticatedConsumptionSession | None = None,
) -> tuple[bool, tuple[str, ...]]:
    reasons: set[str] = set()
    basis_present = "evaluation_basis" in row
    basis = _validated_evaluation_basis(
        row,
        runs_root,
        consumption_session=consumption_session,
    )
    if basis_present and basis is None:
        reasons.add("whole_window_verdict_provenance_invalid")
    if row.get("schema_version") != WHOLE_WINDOW_SCHEMA:
        reasons.add("whole_window_verdict_provenance_invalid")
    row_semantics = _row_consumption_semantics_id(row)
    if row_semantics not in {
        MINTED_CONSUMPTION_SEMANTICS_ID,
        MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
    }:
        reasons.add("whole_window_verdict_provenance_invalid")
    if row_semantics == MAX_BRACKET_CONSUMPTION_SEMANTICS_ID and (
        not isinstance(row.get("evaluation_basis"), Mapping)
        or row["evaluation_basis"].get("consumption_semantics_id")
        != MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
    ):
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
                consumption_session=consumption_session,
            )
        )
    if (
        row_semantics == MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
        and (
            basis is None
            or consumption_session is None
            or not consumption_session.ready
            or not _consumption_provenance_valid(
                basis,
                basis.get("member_occurrences", []),
                runs_root=runs_root,
                consumption_session=consumption_session,
            )
        )
    ):
        reasons.add("whole_window_verdict_provenance_invalid")

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
                current_evidence = (
                    any(
                        isinstance(occurrence, Mapping)
                        and (
                            path := _safe_source_path(
                                runs_root, occurrence.get("bundle_path")
                            )
                        )
                        is not None
                        and _current_strict_summary(
                            _read_json_object(path / "summary_metrics.json"),
                            path,
                        )
                        for occurrence in basis.get(
                            "member_occurrences", []
                        )
                    )
                    if basis is not None
                    else _row_references_current_strict_member(
                        row, runs_root, referenced
                    )
                )
                # Protocol selection is evidence-authenticated. A basis-bearing
                # or current-strict row can never downgrade itself to the
                # frozen gross-only evaluator by deleting amended wire fields.
                point_drift = basis is not None or current_evidence
                requires_point_drift_shape = (
                    basis_present or current_evidence
                )
                if (
                    requires_point_drift_shape
                    and (
                        bracket.get("estimand")
                        != NEG8_POINT_DRIFT_ESTIMAND
                        or not isinstance(
                            bracket.get("claim_families"), Mapping
                        )
                        or "drift_bound_artifact" not in bracket
                        or not isinstance(
                            bracket.get("bound_freshness"), Mapping
                        )
                    )
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
                derived_value, derived_problem = _derived_neg8_decision(
                    verified_source_manifests,
                    runs_root,
                    registered_policy,
                    current=current_evidence,
                    point_drift=point_drift,
                    drift_bound_artifact=drift_bound_artifact,
                    return_bracket=point_drift,
                    freshness_evaluated_at_s=(
                        bracket.get("bound_freshness", {}).get(
                            "evaluated_at_s"
                        )
                        if isinstance(
                            bracket.get("bound_freshness"), Mapping
                        )
                        else None
                    ),
                )
                if derived_problem == "conflict":
                    reasons.add("whole_window_verdict_conflict")
                elif derived_problem == "bundle_strict_invalid":
                    reasons.add("bundle_strict_invalid")
                elif derived_problem is not None or derived_value is None:
                    reasons.add("whole_window_verdict_provenance_invalid")
                elif point_drift:
                    if not isinstance(derived_value, Mapping):
                        reasons.add("whole_window_verdict_provenance_invalid")
                    else:
                        stored_families = bracket.get("claim_families")
                        derived_families = derived_value.get("claim_families")
                        if (
                            not isinstance(stored_families, Mapping)
                            or not isinstance(derived_families, Mapping)
                            or set(stored_families)
                            != {
                                NEG8_CLAIM_FAMILY_GROSS,
                                NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED,
                            }
                            or set(derived_families) != set(stored_families)
                            or any(
                                not isinstance(stored_families[family], Mapping)
                                or not isinstance(derived_families[family], Mapping)
                                or _finite_number(
                                    stored_families[family].get(
                                        "drift_allowance_j"
                                    ),
                                    positive=True,
                                )
                                is None
                                or {
                                    key: value
                                    for key, value in stored_families[
                                        family
                                    ].items()
                                    if key != "window_duration_s"
                                }
                                != {
                                    key: value
                                    for key, value in derived_families[
                                        family
                                    ].items()
                                    if key != "window_duration_s"
                                }
                                for family in stored_families
                            )
                        ):
                            reasons.add("whole_window_verdict_conflict")
                        if (
                            bracket.get("decision")
                            != derived_value.get("decision")
                        ):
                            reasons.add("whole_window_verdict_conflict")
                        if (
                            bracket.get("bound_freshness")
                            != derived_value.get("bound_freshness")
                        ):
                            reasons.add("whole_window_verdict_conflict")
                elif bracket.get("decision") != derived_value:
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
                _read_json_object(path / "summary_metrics.json"),
                path,
            )
            for bundle_id, path in paths.items()
        )
    )


def whole_window_refusal_reasons(
    runs_root: Path,
    referenced_bundle_ids: set[str],
    *,
    evaluation_basis_sha256: str | None = None,
    consumption_session: AuthenticatedConsumptionSession | None = None,
) -> tuple[str, ...]:
    """Return refusals from the verdict governing the requested exact basis."""

    missing = (
        "whole_window_neg8_verdict_missing",
        "adapter_continuity_evidence_missing",
        "cpu_admission_core_missing",
    )
    if consumption_session is not None and (
        Path(runs_root) != consumption_session.runs_root
        or frozenset(referenced_bundle_ids)
        != consumption_session.referenced_bundle_ids
        or evaluation_basis_sha256
        != consumption_session.evaluation_basis_sha256
    ):
        return ("whole_window_verdict_provenance_invalid",)
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
    widened_rows = [
        row
        for row in overlapping
        if _row_consumption_semantics_id(row)
        == MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
    ]
    if widened_rows:
        # Semantic dispatch is explicit.  A max-bracket row supersedes no
        # mint-time history; it is selected because the consumer requests
        # these semantics, independent of append order.
        overlapping = widened_rows
    valid: list[Mapping[str, Any]] = []
    invalid_reasons: set[str] = set()
    for row in overlapping:
        ok, reasons = _validate_row(
            row,
            Path(runs_root),
            referenced_bundle_ids,
            consumption_session=consumption_session,
        )
        if ok:
            valid.append(row)
        else:
            invalid_reasons.update(reasons)
    current_referenced = any(
        _current_strict_summary(
            _read_json_object(Path(runs_root) / bundle_id / "summary_metrics.json"),
            Path(runs_root) / bundle_id,
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


def whole_window_drift_allowances(
    runs_root: Path,
    referenced_bundle_ids: set[str],
    *,
    evaluation_basis_sha256: str | None = None,
    consumption_session: AuthenticatedConsumptionSession | None = None,
) -> WholeWindowDriftAllowanceResult:
    """Return authenticated family allowances for the selected passing basis.

    ``legacy`` is reserved for basis-less frozen replay. ``absent`` means a
    current/basis-bearing row did not preserve a complete authenticated
    allowance wire; callers must refuse rather than treating it as zero.
    """

    root = Path(runs_root)
    if whole_window_refusal_reasons(
        root,
        referenced_bundle_ids,
        evaluation_basis_sha256=evaluation_basis_sha256,
        consumption_session=consumption_session,
    ):
        return WholeWindowDriftAllowanceResult("absent", {})
    try:
        rows = [
            value
            for line in (root / "campaign_log.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
            and isinstance((value := json.loads(line)), Mapping)
            and value.get("record_type")
            == "idle_admission_whole_window_verdict"
        ]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return WholeWindowDriftAllowanceResult("absent", {})
    overlapping_rows = []
    for row in rows:
        bundle_ids = row.get("bundle_ids")
        ids = (
            {item for item in bundle_ids if isinstance(item, str)}
            if isinstance(bundle_ids, list)
            else set()
        )
        if ids.intersection(referenced_bundle_ids):
            overlapping_rows.append(row)
    basis_rows = [
        row
        for row in overlapping_rows
        if isinstance(row.get("evaluation_basis"), Mapping)
    ]
    if basis_rows:
        selected_basis_rows: list[Mapping[str, Any]] = []
        for row in basis_rows:
            basis = row["evaluation_basis"]
            occurrences = basis.get("member_occurrences")
            ids = (
                {
                    item.get("bundle_id")
                    for item in occurrences
                    if isinstance(item, Mapping)
                    and isinstance(item.get("bundle_id"), str)
                }
                if isinstance(occurrences, list)
                else set()
            )
            if evaluation_basis_sha256 is not None:
                selected = (
                    basis.get("sha256") == evaluation_basis_sha256
                    and referenced_bundle_ids.issubset(ids)
                )
            else:
                selected = ids == referenced_bundle_ids
            if selected:
                selected_basis_rows.append(row)
    else:
        selected_basis_rows = []
    semantic_rows = [
        row
        for row in (
            selected_basis_rows
            or (overlapping_rows if not basis_rows else [])
        )
        if _row_consumption_semantics_id(row)
        == MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
    ]
    candidates: list[Mapping[str, Any]] = []
    for row in (
        semantic_rows
        or selected_basis_rows
        or (overlapping_rows if not basis_rows else [])
    ):
        basis = row.get("evaluation_basis")
        if isinstance(basis, Mapping):
            occurrences = basis.get("member_occurrences")
            ids = (
                {
                    item.get("bundle_id")
                    for item in occurrences
                    if isinstance(item, Mapping)
                    and isinstance(item.get("bundle_id"), str)
                }
                if isinstance(occurrences, list)
                else set()
            )
            if evaluation_basis_sha256 is not None:
                selected = (
                    basis.get("sha256") == evaluation_basis_sha256
                    and referenced_bundle_ids.issubset(ids)
                )
            else:
                selected = ids == referenced_bundle_ids
        else:
            bundle_ids = row.get("bundle_ids")
            ids = (
                {item for item in bundle_ids if isinstance(item, str)}
                if isinstance(bundle_ids, list)
                else set()
            )
            selected = bool(ids.intersection(referenced_bundle_ids))
        if selected and _validate_row(
            row,
            root,
            referenced_bundle_ids,
            consumption_session=consumption_session,
        )[0]:
            candidates.append(row)
    if not candidates:
        return WholeWindowDriftAllowanceResult("absent", {})
    bracket = candidates[0].get("idle_admission_core", {}).get("neg8_bracket")
    basis = candidates[0].get("evaluation_basis")
    current = isinstance(basis, Mapping) or _row_references_current_strict_member(
        candidates[0], root, referenced_bundle_ids
    )
    if not current:
        return WholeWindowDriftAllowanceResult("legacy", {})
    if (
        not isinstance(basis, Mapping)
        or not _sha256_text(basis.get("sha256"))
    ):
        return WholeWindowDriftAllowanceResult("absent", {})
    allowances = (
        bracket.get("drift_allowances")
        if isinstance(bracket, Mapping)
        else None
    )
    claim_families = (
        bracket.get("claim_families")
        if isinstance(bracket, Mapping)
        else None
    )
    if not isinstance(allowances, Mapping) or set(allowances) != {
        NEG8_CLAIM_FAMILY_GROSS,
        NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED,
    } or not isinstance(claim_families, Mapping):
        return WholeWindowDriftAllowanceResult("absent", {})
    result: dict[str, dict[str, Any]] = {}
    for family, value in allowances.items():
        family_record = claim_families.get(family)
        expected = (
            {
                "claim_family": family,
                "allowance_j": family_record.get("drift_allowance_j"),
                "observed_trajectory_excursion_j": family_record.get(
                    "trajectory_excursion_max_j"
                ),
                "derived_repeatability_bound_j": family_record.get(
                    "derived_repeatability_bound_j"
                ),
                "provenance": family_record.get("provenance"),
            }
            if isinstance(family_record, Mapping)
            else None
        )
        if (
            not isinstance(value, Mapping)
            or expected is None
            or dict(value) != expected
            or _finite_number(value.get("allowance_j"), positive=True) is None
        ):
            return WholeWindowDriftAllowanceResult("absent", {})
        result[family] = {
            **dict(value),
            "whole_window_evaluation_basis_sha256": (
                basis.get("sha256") if isinstance(basis, Mapping) else None
            ),
        }
    return WholeWindowDriftAllowanceResult("allowances", result)


__all__ = [
    "AuthenticatedConsumptionSession",
    "CONDITION_NEG8_DRIFT_BOUND_STALE",
    "CONDITION_NEG8_IDLE_SUB_DRIFT_BOUND_UNDERIVED",
    "CONDITION_NEG8_IDLE_SUB_POINT_DRIFT_EXCEEDED",
    "CONDITION_NEG8_DRIFT_BOUND_UNDERIVED",
    "CONDITION_NEG8_GROSS_POINT_DRIFT_EXCEEDED",
    "NEG8_CLAIM_FAMILY_GROSS",
    "NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED",
    "NEG8_DRIFT_BOUND_SCHEMA",
    "NEG8_DRIFT_BOUND_MAX_AGE_S",
    "NEG8_DRIFT_ESTIMATOR_ID",
    "NEG8_POINT_DRIFT_ESTIMAND",
    "CustodyTelemetryIdentity",
    "WholeWindowDriftAllowanceResult",
    "NEG8_POINT_DRIFT_CONDITION_CODES",
    "NEG8_REFERENCE_CORPUS_SCHEMA",
    "NEG8_WHOLE_WINDOW_ALLOWANCE_TERM",
    "CONSUMPTION_PROVENANCE_PRECHECK_KEY",
    "MAX_BRACKET_CONSUMPTION_SEMANTICS_ID",
    "MINTED_CONSUMPTION_SEMANTICS_ID",
    "OCCURRENCE_SUPERSESSION_SCHEMA",
    "WHOLE_WINDOW_EVALUATION_BASIS_SCHEMA",
    "WHOLE_WINDOW_PROVENANCE_SCHEMA",
    "WHOLE_WINDOW_SCHEMA",
    "build_evaluation_basis",
    "build_neg8_freshness_observation",
    "build_neg8_drift_bound_artifact",
    "build_row_provenance",
    "canonical_sha256",
    "custody_telemetry_identity",
    "evaluate_neg8_point_drift",
    "evaluate_neg8_bound_freshness",
    "load_neg8_drift_bound_artifact",
    "mint_neg8_drift_bound_artifact",
    "neg8_claim_family_for_metric",
    "neg8_freshness_bindings_from_metadata",
    "ordinary_present_bundle_paths",
    "source_manifest_descriptors",
    "supersession_entry_sha256",
    "supersession_entry_validation_results",
    "validate_occurrence_supersession_entry",
    "validated_supersession_entries",
    "validate_neg8_drift_bound_artifact",
    "whole_window_refusal_reasons",
    "whole_window_drift_allowances",
]
