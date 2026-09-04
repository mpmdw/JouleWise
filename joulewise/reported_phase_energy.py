"""D-123 reported phase-energy artifact construction and validation.

The result is a content-addressed projection over an authenticated extraction
specification and report.  It deliberately does not read or mutate detection-
floor artifacts: D-123 shares physical members with the floor calculation but
has a disjoint output domain.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
from collections.abc import Mapping, Sequence
from decimal import Decimal
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "joulewise.reported_phase_energy.v1"
SOURCE_SCHEMA_VERSION = "joulewise.reported_phase_energy_source.v1"
EXTRACTION_SPEC_SCHEMA_VERSION = "joulewise.detection_floor_extraction_spec.v1"
EXTRACTION_REPORT_SCHEMA_VERSION = "joulewise.detection_floor_extraction.v1"
G2A_SCHEMA_VERSION = "joulewise.g2a_prefill_selection.v1"
PROMPT_PIN_SCHEMA_VERSION = "joulewise.prefill_prompt_pin.v2"

DEFAULT_COMPOSITION_RULE = "composed_member_envelope_mean.v1"
T95_WINDOW_COMPOSITION_RULE = "composed_member_envelope_mean_t95_window.v1"
COMPOSITION_RULES = frozenset(
    {DEFAULT_COMPOSITION_RULE, T95_WINDOW_COMPOSITION_RULE}
)
MEMBER_REDUCER = "arithmetic_mean_over_fixed_member_universe.v1"
MEMBER_ADMISSION_RULE = "fixed_registered_universe_all_or_refuse.v1"
TOKEN_AGGREGATION_RULE = "ratio_of_sums_over_same_fixed_members.v1"
PROMPT_DENOMINATOR_KIND = "runtime_observed_prompt_tokens"
OUTPUT_DENOMINATOR_KIND = "runtime_observed_output_tokens"
TOKEN_COUNT_SOURCES = frozenset({"runtime_observed", "server_usage"})
EXPECTED_N = 50
DECODE_OUTPUT_TOKENS = 512
PREFILL_LENGTHS = frozenset({512, 1024, 2048, 4096})
STOP_FILL = "STOP_FILL"

_HEX40 = re.compile(r"[0-9a-f]{40}")
_HEX64 = re.compile(r"[0-9a-f]{64}")
_REASON = re.compile(r"[a-z0-9_]+")

_TOP_KEYS = {
    "schema_version",
    "artifact_id",
    "campaign_role",
    "producer",
    "inputs",
    "cells",
}
_PRODUCER_KEYS = {"implementation", "source_commit", "source_sha256"}
_INPUT_KEYS = {
    "extraction_spec",
    "extraction_report",
    "g2a_selection",
    "prompt_pin",
}
_SPEC_REFERENCE_KEYS = {
    "schema_version",
    "path",
    "file_sha256",
    "floor_projection_sha256",
}
_REPORT_REFERENCE_KEYS = {
    "schema_version",
    "file_sha256",
    "consumption_semantics_id",
}
_G2A_REFERENCE_KEYS = {
    "schema_version",
    "file_sha256",
    "collection_prefill_tokens",
}
_PROMPT_REFERENCE_KEYS = {
    "schema_version",
    "file_sha256",
    "prefill_length",
    "g2a_record_sha256",
}
_CELL_KEYS = {
    "cell_id",
    "metric",
    "status",
    "registered_member_count",
    "admitted_independent_bundle_count",
    "member_admission_rule",
    "mean_j_per_request",
    "interval",
    "per_token",
    "members",
    "refusal_reasons",
}
_INTERVAL_KEYS = {
    "lower_j",
    "upper_j",
    "composition_rule",
    "t95_critical_value",
    "point_standard_deviation_j",
    "repeatability_half_width_j",
    "window_allowance_j",
}
_PER_TOKEN_KEYS = {
    "value_j_per_token",
    "numerator_energy_j",
    "observed_token_count",
    "denominator_kind",
    "aggregation_rule",
    "token_count_source",
}
_MEMBER_KEYS = {
    "ordinal",
    "bundle_id",
    "config_sha256",
    "bundle_sha256",
    "summary_sha256",
    "metadata_sha256",
    "whole_window_evaluation_basis_sha256",
    "admitted",
    "reasons",
    "energy_j",
    "energy_interval_j",
    "observed_token_denominator",
}
_ENERGY_INTERVAL_KEYS = {"lower_j", "upper_j"}
_DENOMINATOR_KEYS = {
    "kind",
    "count",
    "token_count_source",
    "observed_total_token_count",
    "observed_output_token_count",
    "prompt_realized_token_count",
    "tokenize_prompt_token_count",
    "prefill_prompt_token_count",
}


class StopFill(ValueError):
    """The authenticated parents cannot license an artifact or value."""


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def canonical_json_sha256(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _source_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _pairs_without_duplicates(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StopFill(f"duplicate_json_key:{key}")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise StopFill(f"nonfinite_json_number:{value}")


def _decode_object(raw: bytes, label: str) -> dict[str, Any]:
    if not isinstance(raw, bytes):
        raise StopFill(f"{label}_bytes_required")
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_pairs_without_duplicates,
            parse_constant=_reject_nonfinite,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise StopFill(f"{label}_malformed") from exc
    if not isinstance(value, dict):
        raise StopFill(f"{label}_object_required")
    return value


def _exact_keys(value: object, expected: set[str], where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != expected:
        raise StopFill(f"{where}_closed_keys_mismatch")
    return value


def _string(value: object, where: str) -> str:
    if not isinstance(value, str) or not value or "\n" in value or "\r" in value:
        raise StopFill(f"{where}_invalid")
    return value


def _sha256(value: object, where: str) -> str:
    text = _string(value, where)
    if _HEX64.fullmatch(text) is None:
        raise StopFill(f"{where}_invalid")
    return text


def _nonnegative(value: object, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise StopFill(f"{where}_invalid")
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise StopFill(f"{where}_invalid")
    return result


def _positive_int(value: object, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise StopFill(f"{where}_invalid")
    return value


def _nonnegative_int(value: object, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise StopFill(f"{where}_invalid")
    return value


def _reason_list(value: object, where: str) -> list[str]:
    if not isinstance(value, list):
        raise StopFill(f"{where}_invalid")
    result: list[str] = []
    for item in value:
        text = _string(item, where)
        if _REASON.fullmatch(text) is None or text in result:
            raise StopFill(f"{where}_invalid")
        result.append(text)
    return result


def _wrapped_document(
    source: Mapping[str, Any],
    key: str,
    *,
    expected_schema: str,
) -> tuple[dict[str, Any], str]:
    wrapper = _exact_keys(
        source.get(key), {"path", "file_sha256", "document"}, f"source.{key}"
    )
    path = _string(wrapper["path"], f"source.{key}.path")
    if path.startswith("/") or ".." in path.split("/"):
        raise StopFill(f"source.{key}.path_invalid")
    document = wrapper["document"]
    if not isinstance(document, dict):
        raise StopFill(f"source.{key}.document_invalid")
    supplied = _sha256(wrapper["file_sha256"], f"source.{key}.file_sha256")
    actual = canonical_json_sha256(document)
    if supplied != actual:
        raise StopFill(f"source.{key}.file_sha256_mismatch")
    if document.get("schema_version") != expected_schema:
        raise StopFill(f"source.{key}.schema_mismatch")
    return document, path


def _optional_wrapped_document(
    source: Mapping[str, Any], key: str, *, expected_schema: str
) -> tuple[dict[str, Any] | None, str | None]:
    if source.get(key) is None:
        return None, None
    return _wrapped_document(source, key, expected_schema=expected_schema)


def _report_artifact_id(report: Mapping[str, Any]) -> str:
    preimage = dict(report)
    preimage["artifact_id"] = ""
    return "dfer-" + canonical_json_sha256(preimage)


def _cell_refusal(
    spec_cell: Mapping[str, Any],
    report_cell: Mapping[str, Any] | None,
    reason: str,
) -> dict[str, Any]:
    members: list[dict[str, Any]] = []
    report_members = report_cell.get("members") if isinstance(report_cell, Mapping) else None
    report_by_id = {
        row.get("bundle_id"): row
        for row in report_members
        if isinstance(row, Mapping) and isinstance(row.get("bundle_id"), str)
    } if isinstance(report_members, list) else {}
    for registered in spec_cell.get("members", []):
        if not isinstance(registered, Mapping):
            continue
        row = report_by_id.get(registered.get("bundle_id"), {})
        members.append(
            {
                "ordinal": registered.get("ordinal"),
                "bundle_id": registered.get("bundle_id"),
                "config_sha256": registered.get("config_sha256"),
                "bundle_sha256": row.get("bundle_sha256", "0" * 64),
                "summary_sha256": row.get("summary_sha256", "0" * 64),
                "metadata_sha256": row.get("metadata_sha256", "0" * 64),
                "whole_window_evaluation_basis_sha256": row.get(
                    "whole_window_evaluation_basis_sha256", "0" * 64
                ),
                "admitted": False,
                "reasons": [reason],
                "energy_j": None,
                "energy_interval_j": None,
                "observed_token_denominator": None,
            }
        )
    return {
        "cell_id": spec_cell.get("cell_id"),
        "metric": spec_cell.get("metric"),
        "status": "refused",
        "registered_member_count": EXPECTED_N,
        "admitted_independent_bundle_count": 0,
        "member_admission_rule": MEMBER_ADMISSION_RULE,
        "mean_j_per_request": None,
        "interval": None,
        "per_token": None,
        "members": members,
        "refusal_reasons": [reason],
    }


def _validated_denominator(
    value: object, *, metric: str, where: str
) -> dict[str, Any]:
    row = _exact_keys(value, _DENOMINATOR_KEYS, where)
    kind = _string(row["kind"], f"{where}.kind")
    source = _string(row["token_count_source"], f"{where}.token_count_source")
    if source not in TOKEN_COUNT_SOURCES:
        raise StopFill("runtime_token_denominator_source_invalid")
    count = _positive_int(row["count"], f"{where}.count")
    total = _positive_int(
        row["observed_total_token_count"], f"{where}.observed_total_token_count"
    )
    output = _nonnegative_int(
        row["observed_output_token_count"], f"{where}.observed_output_token_count"
    )
    realized = _positive_int(
        row["prompt_realized_token_count"], f"{where}.prompt_realized_token_count"
    )
    tokenize = _positive_int(
        row["tokenize_prompt_token_count"], f"{where}.tokenize_prompt_token_count"
    )
    prefill = _positive_int(
        row["prefill_prompt_token_count"], f"{where}.prefill_prompt_token_count"
    )
    if metric == "phase_energy_j.prefill":
        if kind != PROMPT_DENOMINATOR_KIND or not (
            count == total - output == realized == tokenize == prefill
        ):
            raise StopFill("prefill_four_surface_denominator_mismatch")
    elif metric == "phase_energy_j.decode":
        if (
            kind != OUTPUT_DENOMINATOR_KIND
            or count != output
            or output != DECODE_OUTPUT_TOKENS
        ):
            raise StopFill("decode_output_denominator_not_512")
    else:
        raise StopFill("reported_phase_metric_invalid")
    return dict(row)


def _build_cell(
    spec_cell: Mapping[str, Any],
    report_cell: Mapping[str, Any] | None,
    *,
    selected_prefill_tokens: int | None,
) -> dict[str, Any]:
    try:
        if set(spec_cell) != {
            "cell_id",
            "metric",
            "window_class",
            "target_precheck_path",
            "measurand",
            "reducer",
            "expected_n",
            "members",
            "missing_or_invalid_member",
            "numeric_value",
        }:
            raise StopFill("registered_cell_closed_keys_mismatch")
        cell_id = _string(spec_cell["cell_id"], "registered_cell.cell_id")
        metric = _string(spec_cell["metric"], "registered_cell.metric")
        if (
            spec_cell["window_class"] != "phase"
            or spec_cell["measurand"] != "gross_phase_energy_j"
            or spec_cell["reducer"] != MEMBER_REDUCER
            or spec_cell["expected_n"] != EXPECTED_N
            or spec_cell["missing_or_invalid_member"] != "refuse_reported_mean"
            or spec_cell["numeric_value"] is not None
        ):
            raise StopFill("registered_cell_contract_mismatch")
        expected_path = (
            ["phase", "prefill"]
            if metric == "phase_energy_j.prefill"
            else ["phase", "decode"]
        )
        if spec_cell["target_precheck_path"] != expected_path:
            raise StopFill("registered_cell_precheck_path_mismatch")
        registered = spec_cell["members"]
        if not isinstance(registered, list) or len(registered) != EXPECTED_N:
            raise StopFill("registered_member_census_mismatch")
        if report_cell is None or set(report_cell) != {
            "cell_id",
            "metric",
            "outcome",
            "expected_n",
            "observed_n",
            "admitted_n",
            "interval_policy",
            "members",
        }:
            raise StopFill("reported_cell_absent_or_malformed")
        if report_cell["cell_id"] != cell_id or report_cell["metric"] != metric:
            raise StopFill("reported_cell_identity_mismatch")
        if report_cell["outcome"] != "issued":
            raise StopFill("reported_cell_outcome_not_issued")
        if not (
            report_cell["expected_n"]
            == report_cell["observed_n"]
            == report_cell["admitted_n"]
            == EXPECTED_N
        ):
            raise StopFill("reported_cell_census_mismatch")
        observed = report_cell["members"]
        if not isinstance(observed, list) or len(observed) != EXPECTED_N:
            raise StopFill("reported_member_census_mismatch")

        policy = _exact_keys(
            report_cell["interval_policy"],
            {"composition_rule", "t95_critical_value", "window_allowance_j"},
            "reported_cell.interval_policy",
        )
        composition_rule = policy["composition_rule"]
        if composition_rule not in COMPOSITION_RULES:
            raise StopFill("interval_composition_rule_unregistered")

        members: list[dict[str, Any]] = []
        points: list[float] = []
        lowers: list[float] = []
        uppers: list[float] = []
        denominators: list[dict[str, Any] | None] = []
        denominator_sources: set[str] = set()
        for index, (registered_row, observed_row) in enumerate(
            zip(registered, observed), start=1
        ):
            if not isinstance(registered_row, Mapping) or set(registered_row) != {
                "ordinal",
                "bundle_id",
                "config_sha256",
            }:
                raise StopFill("registered_member_malformed")
            if not isinstance(observed_row, Mapping) or set(observed_row) != {
                "ordinal",
                "bundle_id",
                "config_sha256",
                "bundle_sha256",
                "summary_sha256",
                "metadata_sha256",
                "whole_window_evaluation_basis_sha256",
                "outcome",
                "reasons",
                "point_j",
                "energy_anchor_shift_envelope",
                "observed_token_denominator",
            }:
                raise StopFill("reported_member_malformed")
            if registered_row["ordinal"] != index or observed_row["ordinal"] != index:
                raise StopFill("reported_member_ordinal_mismatch")
            bundle_id = _string(registered_row["bundle_id"], "registered.bundle_id")
            if observed_row["bundle_id"] != bundle_id:
                raise StopFill("reported_member_identity_mismatch")
            config_sha = _sha256(
                registered_row["config_sha256"], "registered.config_sha256"
            )
            if observed_row["config_sha256"] != config_sha:
                raise StopFill("reported_member_config_sha256_mismatch")
            if observed_row["outcome"] != "admitted":
                raise StopFill("reported_member_outcome_not_admitted")
            reasons = _reason_list(observed_row["reasons"], "reported_member.reasons")
            if reasons:
                raise StopFill("admitted_member_has_reasons")
            bundle_sha = _sha256(observed_row["bundle_sha256"], "member.bundle_sha256")
            summary_sha = _sha256(observed_row["summary_sha256"], "member.summary_sha256")
            metadata_sha = _sha256(
                observed_row["metadata_sha256"], "member.metadata_sha256"
            )
            basis_sha = _sha256(
                observed_row["whole_window_evaluation_basis_sha256"],
                "member.whole_window_evaluation_basis_sha256",
            )
            point = _nonnegative(observed_row["point_j"], "member.point_j")
            envelope = _exact_keys(
                observed_row["energy_anchor_shift_envelope"],
                {"point_j", "lower_j", "upper_j"},
                "member.energy_anchor_shift_envelope",
            )
            envelope_point = _nonnegative(envelope["point_j"], "envelope.point_j")
            lower = _nonnegative(envelope["lower_j"], "envelope.lower_j")
            upper = _nonnegative(envelope["upper_j"], "envelope.upper_j")
            if point != envelope_point or not lower <= point <= upper:
                raise StopFill("member_energy_envelope_inconsistent")
            try:
                denominator = _validated_denominator(
                    observed_row["observed_token_denominator"],
                    metric=metric,
                    where="member.observed_token_denominator",
                )
                denominator_sources.add(denominator["token_count_source"])
            except StopFill:
                denominator = None
            denominators.append(denominator)
            points.append(point)
            lowers.append(lower)
            uppers.append(upper)
            members.append(
                {
                    "ordinal": index,
                    "bundle_id": bundle_id,
                    "config_sha256": config_sha,
                    "bundle_sha256": bundle_sha,
                    "summary_sha256": summary_sha,
                    "metadata_sha256": metadata_sha,
                    "whole_window_evaluation_basis_sha256": basis_sha,
                    "admitted": True,
                    "reasons": [] if denominator is not None else [
                        "runtime_token_denominator_invalid"
                    ],
                    "energy_j": point,
                    "energy_interval_j": {"lower_j": lower, "upper_j": upper},
                    "observed_token_denominator": denominator,
                }
            )

        if len({row["bundle_id"] for row in members}) != EXPECTED_N:
            raise StopFill("reported_member_identity_duplicate")
        if metric == "phase_energy_j.prefill" and "prefill-p42" not in cell_id:
            if selected_prefill_tokens is None or (
                f"prefill-p{selected_prefill_tokens}" not in cell_id
            ):
                raise StopFill("g2a_prompt_pin_cell_join_mismatch")
            if any(
                denominator is not None
                and denominator["count"] != selected_prefill_tokens
                for denominator in denominators
            ):
                denominators = [None for _ in denominators]
                for member in members:
                    member["observed_token_denominator"] = None
                    member["reasons"] = ["runtime_token_denominator_invalid"]

        mean = math.fsum(points) / EXPECTED_N
        lower_mean = math.fsum(lowers) / EXPECTED_N
        upper_mean = math.fsum(uppers) / EXPECTED_N
        if composition_rule == DEFAULT_COMPOSITION_RULE:
            if policy["t95_critical_value"] is not None or policy["window_allowance_j"] is not None:
                raise StopFill("default_interval_has_surplus_parameters")
            t95: float | None = None
            standard_deviation: float | None = None
            repeatability: float | None = None
            allowance: float | None = None
            composed_lower = lower_mean
            composed_upper = upper_mean
        else:
            t95 = _nonnegative(policy["t95_critical_value"], "interval.t95")
            allowance = _nonnegative(
                policy["window_allowance_j"], "interval.window_allowance_j"
            )
            standard_deviation = statistics.stdev(points)
            repeatability = t95 * standard_deviation / math.sqrt(EXPECTED_N)
            composed_lower = lower_mean - repeatability - allowance
            composed_upper = upper_mean + repeatability + allowance
            if composed_lower < 0.0:
                raise StopFill("composed_interval_lower_negative")
        interval = {
            "lower_j": composed_lower,
            "upper_j": composed_upper,
            "composition_rule": composition_rule,
            "t95_critical_value": t95,
            "point_standard_deviation_j": standard_deviation,
            "repeatability_half_width_j": repeatability,
            "window_allowance_j": allowance,
        }
        valid_denominators = [row for row in denominators if row is not None]
        if len(valid_denominators) == EXPECTED_N and len(denominator_sources) == 1:
            numerator = math.fsum(points)
            observed_token_count = sum(row["count"] for row in valid_denominators)
            per_token: dict[str, Any] | None = {
                "value_j_per_token": numerator / observed_token_count,
                "numerator_energy_j": numerator,
                "observed_token_count": observed_token_count,
                "denominator_kind": (
                    PROMPT_DENOMINATOR_KIND
                    if metric == "phase_energy_j.prefill"
                    else OUTPUT_DENOMINATOR_KIND
                ),
                "aggregation_rule": TOKEN_AGGREGATION_RULE,
                "token_count_source": next(iter(denominator_sources)),
            }
            refusal_reasons: list[str] = []
        else:
            per_token = None
            refusal_reasons = [
                "runtime_token_denominator_ambiguous"
                if len(valid_denominators) == EXPECTED_N
                else "runtime_token_denominator_invalid"
            ]
        return {
            "cell_id": cell_id,
            "metric": metric,
            "status": "issued",
            "registered_member_count": EXPECTED_N,
            "admitted_independent_bundle_count": EXPECTED_N,
            "member_admission_rule": MEMBER_ADMISSION_RULE,
            "mean_j_per_request": mean,
            "interval": interval,
            "per_token": per_token,
            "members": members,
            "refusal_reasons": refusal_reasons,
        }
    except StopFill as exc:
        return _cell_refusal(spec_cell, report_cell, str(exc))


def build_reported_phase_energy(source_bytes: bytes) -> dict[str, Any]:
    """Build one alpha or beta artifact from exact authenticated source bytes."""

    source = _decode_object(source_bytes, "source")
    _exact_keys(
        source,
        {
            "schema_version",
            "campaign_role",
            "source_commit",
            "extraction_spec",
            "extraction_report",
            "g2a_selection",
            "prompt_pin",
        },
        "source",
    )
    if source["schema_version"] != SOURCE_SCHEMA_VERSION:
        raise StopFill("source_schema_mismatch")
    campaign_role = source["campaign_role"]
    if campaign_role not in {"alpha", "beta"}:
        raise StopFill("campaign_role_invalid")
    source_commit = _string(source["source_commit"], "source.source_commit")
    if _HEX40.fullmatch(source_commit) is None:
        raise StopFill("source_commit_invalid")

    spec, spec_path = _wrapped_document(
        source, "extraction_spec", expected_schema=EXTRACTION_SPEC_SCHEMA_VERSION
    )
    report, _ = _wrapped_document(
        source, "extraction_report", expected_schema=EXTRACTION_REPORT_SCHEMA_VERSION
    )
    g2a, _ = _optional_wrapped_document(
        source, "g2a_selection", expected_schema=G2A_SCHEMA_VERSION
    )
    prompt_pin, _ = _optional_wrapped_document(
        source, "prompt_pin", expected_schema=PROMPT_PIN_SCHEMA_VERSION
    )
    if (g2a is None) != (prompt_pin is None):
        raise StopFill("g2a_prompt_pin_pair_incomplete")
    selected_prefill_tokens: int | None = None
    if g2a is not None and prompt_pin is not None:
        selected_prefill_tokens = g2a.get("collection_prefill_tokens")
        if selected_prefill_tokens not in PREFILL_LENGTHS:
            raise StopFill("g2a_selected_prefill_invalid")
        g2a_sha = canonical_json_sha256(g2a)
        if not (
            prompt_pin.get("prefill_length")
            == prompt_pin.get("prompt_tokens")
            == selected_prefill_tokens
            and prompt_pin.get("g2a_record_sha256") == g2a_sha
        ):
            raise StopFill("g2a_prompt_pin_join_mismatch")

    registration = spec.get("reported_energy_registration")
    if not isinstance(registration, Mapping):
        raise StopFill("reported_energy_registration_missing")
    if (
        registration.get("authority") != "D-123"
        or registration.get("procedure_only") is not True
        or registration.get("postcollection_numeric_values")
        != "structurally_absent_until_governed_reduction"
    ):
        raise StopFill("reported_energy_registration_invalid")
    floor_projection_sha = _sha256(
        registration.get("floor_projection_sha256"),
        "reported_energy_registration.floor_projection_sha256",
    )
    if canonical_json_sha256(spec.get("cells")) != floor_projection_sha:
        raise StopFill("floor_projection_sha256_mismatch")
    if report.get("artifact_id") != _report_artifact_id(report):
        raise StopFill("extraction_report_artifact_id_mismatch")
    if report.get("campaign_role") != campaign_role or report.get("outcome") != "issued":
        raise StopFill("extraction_report_identity_or_outcome_mismatch")
    consumption_semantics_id = _string(
        report.get("consumption_semantics_id"),
        "extraction_report.consumption_semantics_id",
    )
    report_cells = report.get("reported_energy_cells")
    if not isinstance(report_cells, list):
        raise StopFill("extraction_report_cells_invalid")
    report_by_id: dict[str, Mapping[str, Any]] = {}
    for row in report_cells:
        if not isinstance(row, Mapping) or not isinstance(row.get("cell_id"), str):
            raise StopFill("extraction_report_cell_malformed")
        if row["cell_id"] in report_by_id:
            raise StopFill("extraction_report_cell_duplicate")
        report_by_id[row["cell_id"]] = row
    spec_cells = spec.get("reported_energy_cells")
    if not isinstance(spec_cells, list) or len(spec_cells) != 3:
        raise StopFill("registered_reported_cell_census_mismatch")
    spec_ids = [row.get("cell_id") for row in spec_cells if isinstance(row, Mapping)]
    if len(spec_ids) != 3 or len(set(spec_ids)) != 3 or set(report_by_id) != set(spec_ids):
        raise StopFill("reported_cell_identity_census_mismatch")

    cells = [
        _build_cell(
            spec_cell,
            report_by_id.get(spec_cell.get("cell_id")),
            selected_prefill_tokens=selected_prefill_tokens,
        )
        for spec_cell in spec_cells
    ]
    artifact: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": "",
        "campaign_role": campaign_role,
        "producer": {
            "implementation": "joulewise.reported_phase_energy",
            "source_commit": source_commit,
            "source_sha256": _source_sha256(),
        },
        "inputs": {
            "extraction_spec": {
                "schema_version": EXTRACTION_SPEC_SCHEMA_VERSION,
                "path": spec_path,
                "file_sha256": canonical_json_sha256(spec),
                "floor_projection_sha256": floor_projection_sha,
            },
            "extraction_report": {
                "schema_version": EXTRACTION_REPORT_SCHEMA_VERSION,
                "file_sha256": canonical_json_sha256(report),
                "consumption_semantics_id": consumption_semantics_id,
            },
            "g2a_selection": None
            if g2a is None
            else {
                "schema_version": G2A_SCHEMA_VERSION,
                "file_sha256": canonical_json_sha256(g2a),
                "collection_prefill_tokens": selected_prefill_tokens,
            },
            "prompt_pin": None
            if prompt_pin is None
            else {
                "schema_version": PROMPT_PIN_SCHEMA_VERSION,
                "file_sha256": canonical_json_sha256(prompt_pin),
                "prefill_length": prompt_pin["prefill_length"],
                "g2a_record_sha256": prompt_pin["g2a_record_sha256"],
            },
        },
        "cells": cells,
    }
    artifact["artifact_id"] = "rpe-" + canonical_json_sha256(artifact)
    errors = validate_reported_phase_energy(artifact)
    if errors:
        raise StopFill(errors[0])
    return artifact


def _cell_validation_error(cell: object, index: int) -> str | None:
    where = f"cells[{index}]"
    try:
        row = _exact_keys(cell, _CELL_KEYS, where)
        _string(row["cell_id"], f"{where}.cell_id")
        metric = _string(row["metric"], f"{where}.metric")
        if metric not in {"phase_energy_j.prefill", "phase_energy_j.decode"}:
            raise StopFill(f"{where}.metric_invalid")
        if row["status"] not in {"issued", "refused"}:
            raise StopFill(f"{where}.status_invalid")
        if row["registered_member_count"] != EXPECTED_N:
            raise StopFill(f"{where}.registered_member_count_invalid")
        admitted_count = _nonnegative_int(
            row["admitted_independent_bundle_count"],
            f"{where}.admitted_independent_bundle_count",
        )
        if admitted_count > EXPECTED_N or row["member_admission_rule"] != MEMBER_ADMISSION_RULE:
            raise StopFill(f"{where}.member_census_invalid")
        reasons = _reason_list(row["refusal_reasons"], f"{where}.refusal_reasons")
        members = row["members"]
        if not isinstance(members, list) or len(members) != EXPECTED_N:
            raise StopFill(f"{where}.members_census_invalid")
        points: list[float] = []
        lowers: list[float] = []
        uppers: list[float] = []
        denominators: list[Mapping[str, Any]] = []
        ids: list[str] = []
        admitted_observed = 0
        for ordinal, member in enumerate(members, start=1):
            member_where = f"{where}.members[{ordinal - 1}]"
            member_row = _exact_keys(member, _MEMBER_KEYS, member_where)
            if member_row["ordinal"] != ordinal:
                raise StopFill(f"{member_where}.ordinal_invalid")
            ids.append(_string(member_row["bundle_id"], f"{member_where}.bundle_id"))
            for key in (
                "config_sha256",
                "bundle_sha256",
                "summary_sha256",
                "metadata_sha256",
                "whole_window_evaluation_basis_sha256",
            ):
                _sha256(member_row[key], f"{member_where}.{key}")
            if not isinstance(member_row["admitted"], bool):
                raise StopFill(f"{member_where}.admitted_invalid")
            member_reasons = _reason_list(member_row["reasons"], f"{member_where}.reasons")
            admitted_observed += int(member_row["admitted"])
            if row["status"] == "issued":
                if not member_row["admitted"]:
                    raise StopFill(f"{member_where}.issued_not_admitted")
                point = _nonnegative(member_row["energy_j"], f"{member_where}.energy_j")
                envelope = _exact_keys(
                    member_row["energy_interval_j"],
                    _ENERGY_INTERVAL_KEYS,
                    f"{member_where}.energy_interval_j",
                )
                lower = _nonnegative(envelope["lower_j"], f"{member_where}.lower_j")
                upper = _nonnegative(envelope["upper_j"], f"{member_where}.upper_j")
                if not lower <= point <= upper:
                    raise StopFill(f"{member_where}.energy_interval_invalid")
                points.append(point)
                lowers.append(lower)
                uppers.append(upper)
                if member_row["observed_token_denominator"] is not None:
                    denominator = _validated_denominator(
                        member_row["observed_token_denominator"],
                        metric=metric,
                        where=f"{member_where}.observed_token_denominator",
                    )
                    denominators.append(denominator)
                    if member_reasons:
                        raise StopFill(f"{member_where}.valid_denominator_has_reasons")
                elif member_reasons != ["runtime_token_denominator_invalid"]:
                    raise StopFill(f"{member_where}.denominator_refusal_reason_invalid")
            else:
                if member_row["admitted"] or member_row["energy_j"] is not None or member_row["energy_interval_j"] is not None or member_row["observed_token_denominator"] is not None:
                    raise StopFill(f"{member_where}.refused_payload_not_null")
                if not member_reasons:
                    raise StopFill(f"{member_where}.refused_reason_missing")
        if len(set(ids)) != EXPECTED_N or admitted_observed != admitted_count:
            raise StopFill(f"{where}.member_identity_or_admission_census_invalid")
        if row["status"] == "refused":
            if not reasons or any(
                row[key] is not None for key in ("mean_j_per_request", "interval", "per_token")
            ):
                raise StopFill(f"{where}.refused_cell_invalid")
            return None
        if admitted_count != EXPECTED_N:
            raise StopFill(f"{where}.issued_admission_census_invalid")
        mean = _nonnegative(row["mean_j_per_request"], f"{where}.mean")
        if mean != math.fsum(points) / EXPECTED_N:
            raise StopFill(f"{where}.mean_relation_invalid")
        interval = _exact_keys(row["interval"], _INTERVAL_KEYS, f"{where}.interval")
        rule = interval["composition_rule"]
        if rule not in COMPOSITION_RULES:
            raise StopFill(f"{where}.composition_rule_invalid")
        lower_mean = math.fsum(lowers) / EXPECTED_N
        upper_mean = math.fsum(uppers) / EXPECTED_N
        if rule == DEFAULT_COMPOSITION_RULE:
            if any(
                interval[key] is not None
                for key in (
                    "t95_critical_value",
                    "point_standard_deviation_j",
                    "repeatability_half_width_j",
                    "window_allowance_j",
                )
            ):
                raise StopFill(f"{where}.default_interval_parameters_invalid")
            expected_lower, expected_upper = lower_mean, upper_mean
        else:
            t95 = _nonnegative(interval["t95_critical_value"], f"{where}.t95")
            standard_deviation = _nonnegative(
                interval["point_standard_deviation_j"], f"{where}.stdev"
            )
            repeatability = _nonnegative(
                interval["repeatability_half_width_j"], f"{where}.repeatability"
            )
            allowance = _nonnegative(
                interval["window_allowance_j"], f"{where}.allowance"
            )
            if standard_deviation != statistics.stdev(points) or repeatability != t95 * standard_deviation / math.sqrt(EXPECTED_N):
                raise StopFill(f"{where}.t95_relation_invalid")
            expected_lower = lower_mean - repeatability - allowance
            expected_upper = upper_mean + repeatability + allowance
        if interval["lower_j"] != expected_lower or interval["upper_j"] != expected_upper:
            raise StopFill(f"{where}.interval_relation_invalid")
        if row["per_token"] is None:
            denominator_sources = {
                denominator["token_count_source"] for denominator in denominators
            }
            valid_refusal = (
                reasons == ["runtime_token_denominator_invalid"]
                and len(denominators) < EXPECTED_N
            ) or (
                reasons == ["runtime_token_denominator_ambiguous"]
                and len(denominators) == EXPECTED_N
                and len(denominator_sources) > 1
            )
            if not valid_refusal:
                raise StopFill(f"{where}.per_token_refusal_invalid")
        else:
            per_token = _exact_keys(row["per_token"], _PER_TOKEN_KEYS, f"{where}.per_token")
            if reasons or len(denominators) != EXPECTED_N:
                raise StopFill(f"{where}.per_token_parent_invalid")
            sources = {denominator["token_count_source"] for denominator in denominators}
            kinds = {denominator["kind"] for denominator in denominators}
            expected_kind = PROMPT_DENOMINATOR_KIND if metric == "phase_energy_j.prefill" else OUTPUT_DENOMINATOR_KIND
            numerator = math.fsum(points)
            denominator_count = sum(denominator["count"] for denominator in denominators)
            if (
                sources != {per_token["token_count_source"]}
                or kinds != {expected_kind}
                or per_token["denominator_kind"] != expected_kind
                or per_token["aggregation_rule"] != TOKEN_AGGREGATION_RULE
                or per_token["numerator_energy_j"] != numerator
                or per_token["observed_token_count"] != denominator_count
                or per_token["value_j_per_token"] != numerator / denominator_count
            ):
                raise StopFill(f"{where}.ratio_of_sums_relation_invalid")
    except StopFill as exc:
        return str(exc)
    return None


def validate_reported_phase_energy(artifact: object) -> list[str]:
    """Return closed-schema and arithmetic errors for one artifact."""

    try:
        root = _exact_keys(artifact, _TOP_KEYS, "artifact")
        if root["schema_version"] != SCHEMA_VERSION:
            raise StopFill("artifact_schema_mismatch")
        if root["campaign_role"] not in {"alpha", "beta"}:
            raise StopFill("artifact_campaign_role_invalid")
        producer = _exact_keys(root["producer"], _PRODUCER_KEYS, "producer")
        if producer["implementation"] != "joulewise.reported_phase_energy":
            raise StopFill("producer_implementation_invalid")
        if _HEX40.fullmatch(str(producer["source_commit"])) is None:
            raise StopFill("producer_source_commit_invalid")
        if producer["source_sha256"] != _source_sha256():
            raise StopFill("producer_source_sha256_mismatch")
        inputs = _exact_keys(root["inputs"], _INPUT_KEYS, "inputs")
        spec = _exact_keys(inputs["extraction_spec"], _SPEC_REFERENCE_KEYS, "inputs.extraction_spec")
        report = _exact_keys(inputs["extraction_report"], _REPORT_REFERENCE_KEYS, "inputs.extraction_report")
        if spec["schema_version"] != EXTRACTION_SPEC_SCHEMA_VERSION or report["schema_version"] != EXTRACTION_REPORT_SCHEMA_VERSION:
            raise StopFill("input_schema_reference_invalid")
        _string(spec["path"], "inputs.extraction_spec.path")
        _sha256(spec["file_sha256"], "inputs.extraction_spec.file_sha256")
        _sha256(spec["floor_projection_sha256"], "inputs.extraction_spec.floor_projection_sha256")
        _sha256(report["file_sha256"], "inputs.extraction_report.file_sha256")
        _string(report["consumption_semantics_id"], "inputs.extraction_report.consumption_semantics_id")
        g2a = inputs["g2a_selection"]
        pin = inputs["prompt_pin"]
        if (g2a is None) != (pin is None):
            raise StopFill("artifact_g2a_prompt_pair_invalid")
        if g2a is not None and pin is not None:
            g2a_row = _exact_keys(g2a, _G2A_REFERENCE_KEYS, "inputs.g2a_selection")
            pin_row = _exact_keys(pin, _PROMPT_REFERENCE_KEYS, "inputs.prompt_pin")
            if g2a_row["schema_version"] != G2A_SCHEMA_VERSION or pin_row["schema_version"] != PROMPT_PIN_SCHEMA_VERSION:
                raise StopFill("artifact_prompt_schema_invalid")
            _sha256(g2a_row["file_sha256"], "inputs.g2a_selection.file_sha256")
            _sha256(pin_row["file_sha256"], "inputs.prompt_pin.file_sha256")
            _sha256(pin_row["g2a_record_sha256"], "inputs.prompt_pin.g2a_record_sha256")
            if (
                g2a_row["collection_prefill_tokens"] not in PREFILL_LENGTHS
                or pin_row["prefill_length"] != g2a_row["collection_prefill_tokens"]
                or pin_row["g2a_record_sha256"] != g2a_row["file_sha256"]
            ):
                raise StopFill("artifact_g2a_prompt_join_invalid")
        cells = root["cells"]
        if not isinstance(cells, list) or len(cells) != 3:
            raise StopFill("artifact_cell_census_invalid")
        ids: list[str] = []
        for index, cell in enumerate(cells):
            error = _cell_validation_error(cell, index)
            if error:
                raise StopFill(error)
            ids.append(cell["cell_id"])
        if len(set(ids)) != 3:
            raise StopFill("artifact_cell_identity_duplicate")
        model_id = (
            "qwen3-1p7b" if root["campaign_role"] == "alpha" else "qwen3-8b"
        )
        required_ids = {
            f"d117-reported-mean-ph-decode-{model_id}",
            f"d117-reported-mean-ph-prefill-p42-{model_id}",
        }
        if g2a is None:
            selected_ids = {
                cell_id
                for cell_id in ids
                if re.fullmatch(
                    rf"d117-reported-mean-ph-prefill-p(?:512|1024|2048|4096)-{model_id}",
                    cell_id,
                )
            }
            if len(selected_ids) != 1:
                raise StopFill("artifact_selected_prefill_identity_invalid")
            required_ids.update(selected_ids)
        else:
            required_ids.add(
                "d117-reported-mean-ph-prefill-p"
                f"{g2a['collection_prefill_tokens']}-{model_id}"
            )
        if set(ids) != required_ids:
            raise StopFill("artifact_cell_identity_invalid")
        artifact_id = root["artifact_id"]
        if not isinstance(artifact_id, str) or not artifact_id.startswith("rpe-"):
            raise StopFill("artifact_id_invalid")
        preimage = dict(root)
        preimage["artifact_id"] = ""
        if artifact_id != "rpe-" + canonical_json_sha256(preimage):
            raise StopFill("artifact_id_content_mismatch")
    except (StopFill, TypeError, ValueError, OverflowError) as exc:
        return [str(exc)]
    return []


def _render_number(value: object) -> str:
    number = Decimal(str(value))
    rendered = format(number, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"


def _role_tokens(role: str) -> dict[str, str]:
    prefix = "1p7B" if role == "alpha" else "8B"
    return {
        "prefill_mean": f"[E_{prefix}_prefill_p[PREFILL_LENGTH]_J_per_request]",
        "prefill_lower": f"[E_{prefix}_prefill_p[PREFILL_LENGTH]_lower_J]",
        "prefill_upper": f"[E_{prefix}_prefill_p[PREFILL_LENGTH]_upper_J]",
        "prefill_token": f"[E_{prefix}_prefill_p[PREFILL_LENGTH]_J_per_token]",
        "prefill_n": f"[N_bundles_{prefix}_prefill_p[PREFILL_LENGTH]]",
        "decode_mean": f"[E_{prefix}_decode_J_per_request]",
        "decode_lower": f"[E_{prefix}_decode_lower_J]",
        "decode_upper": f"[E_{prefix}_decode_upper_J]",
        "decode_token": f"[E_{prefix}_decode_J_per_token]",
        "decode_n": f"[N_bundles_{prefix}_decode]",
    }


def reported_phase_energy_token_values(artifacts: Sequence[object]) -> dict[str, str]:
    """Project all 20 registered D-123 tokens, returning STOP_FILL per level."""

    values: dict[str, str] = {}
    by_role = {
        artifact.get("campaign_role"): artifact
        for artifact in artifacts
        if isinstance(artifact, Mapping)
        and artifact.get("campaign_role") in {"alpha", "beta"}
    }
    for role in ("alpha", "beta"):
        tokens = _role_tokens(role)
        values.update({token: STOP_FILL for token in tokens.values()})
        artifact = by_role.get(role)
        if artifact is None or validate_reported_phase_energy(artifact):
            continue
        g2a = artifact["inputs"]["g2a_selection"]
        selected = None if g2a is None else g2a["collection_prefill_tokens"]
        cells = artifact["cells"]
        decode = next(
            (cell for cell in cells if cell["metric"] == "phase_energy_j.decode"),
            None,
        )
        prefill = next(
            (
                cell
                for cell in cells
                if cell["metric"] == "phase_energy_j.prefill"
                and selected is not None
                and f"prefill-p{selected}" in cell["cell_id"]
            ),
            None,
        )
        for phase, cell in (("prefill", prefill), ("decode", decode)):
            if not isinstance(cell, Mapping) or cell["status"] != "issued":
                continue
            values[tokens[f"{phase}_mean"]] = _render_number(cell["mean_j_per_request"])
            values[tokens[f"{phase}_lower"]] = _render_number(cell["interval"]["lower_j"])
            values[tokens[f"{phase}_upper"]] = _render_number(cell["interval"]["upper_j"])
            values[tokens[f"{phase}_n"]] = str(cell["admitted_independent_bundle_count"])
            if cell["per_token"] is not None:
                values[tokens[f"{phase}_token"]] = _render_number(
                    cell["per_token"]["value_j_per_token"]
                )
    return values


__all__ = [
    "SCHEMA_VERSION",
    "SOURCE_SCHEMA_VERSION",
    "DEFAULT_COMPOSITION_RULE",
    "T95_WINDOW_COMPOSITION_RULE",
    "STOP_FILL",
    "StopFill",
    "build_reported_phase_energy",
    "canonical_json_bytes",
    "canonical_json_sha256",
    "reported_phase_energy_token_values",
    "validate_reported_phase_energy",
]
