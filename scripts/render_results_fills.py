#!/usr/bin/env python3
"""Fail-closed renderer for the registered Results prose template.

The positional input is a small orchestration manifest.  It names the issued
whole-window verdict, detection-floor mint, and extraction JSON files by
semantic campaign role rather than guessing identifiers that have not yet
been frozen::

    {
      "schema_version": "joulewise.results_fill_input.v1",
      "campaigns": {
        "alpha": {
          "verdict": "alpha-verdict.json",
          "floor_artifact": "alpha-floor.json",
          "extraction": "alpha-extraction.json",
          "cells": {
            "prompt": {
              "floor_cell_id": "...",
              "absolute_extraction_cell_id": "...",
              "comparative_extraction_cell_id": "..."
            },
            "decode": {"...": "..."}
          }
        },
        "beta": {"...": "..."}
      },
      "gamma": null,
      "characterization": {"funded": false, "run": false, "verdict": null}
    }

Paths are resolved relative to the input manifest.  Successful rendering is
written only to stdout.  STOP_FILL is written only to stderr and returns 2;
it is never represented by a placeholder in prose.  The historical template
linter is imported read-only for its frozen vocabulary.  Its unfilled-scaffold
checks remain untouched; :func:`validate_rendered` owns final single-variant
output validation.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, NamedTuple, Sequence


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_LINTER_PATH = (
    ROOT
    / "docs"
    / "process_traces"
    / "2026-08-07-plan-factory"
    / "lint_results_prose_template.py"
)
REGISTRY_PATH = ROOT / "docs" / "paper" / "results-fill-registry.md"
INPUT_SCHEMA_VERSION = "joulewise.results_fill_input.v1"
FLOOR_SCHEMA_VERSION = "joulewise.detection_floor_artifact.v2"
EXTRACTION_SCHEMA_VERSION = "joulewise.detection_floor_extraction.v1"
VERDICT_SCHEMA_VERSION = "joulewise.idle_admission_whole_window_verdict.v1"
DOMINANCE_CODE = "admissible_set_uncertainty_dominates_point_floor"
ATTRIBUTION_LIMIT_CLASS = "attribution_limited"
ATTRIBUTION_FLOOR_SOURCE = "E_clock_anchor_shift_bound_j"
GLOBAL_INPUT_ROW = "[REFUSAL_REASON_1p5B_floor_window]"


def _load_canonical_linter() -> Any:
    spec = importlib.util.spec_from_file_location(
        "results_prose_canonical_linter", CANONICAL_LINTER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the canonical Results prose linter")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CANONICAL = _load_canonical_linter()
TEMPLATE_TEXT = CANONICAL.TEMPLATE_PATH.read_text(encoding="utf-8")

# These public copies deliberately form a small compatibility surface for the
# renderer.  tests/test_render_results_fills.py pins each one back to the
# custodied linter so vocabulary drift cannot be silent.
TERMINAL_REASON_CODES = frozenset(CANONICAL.TERMINAL_REASON_CODES)
NONTERMINAL_CODES = frozenset(CANONICAL.NONTERMINAL_CODES)
S7_HEADINGS = dict(CANONICAL.S7_HEADINGS)
S6_HEADINGS = dict(CANONICAL.S6_HEADINGS)
S6_GUARDS = dict(CANONICAL.S6_GUARDS)

FILL_TOKEN_RE = re.compile(r"\[([A-Z][A-Za-z0-9_*.-]*)\]")
NUMBER_RE = r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?"
INTEGER_RE = r"(?:0|[1-9][0-9]*)"
SAFE_REASON_RE = r"[^\[\]\n]+"


def _registry_rows() -> tuple[frozenset[str], frozenset[str], frozenset[str]]:
    rows: set[str] = set()
    supplier_unknown: set[str] = set()
    value_unissued: set[str] = set()
    for line in REGISTRY_PATH.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\| `(\[[^\]]+\])` \|", line)
        if match is None:
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) == 7 and " — Appendix " in cells[0] and cells[4] == "DERIVE":
                marker = re.fullmatch(r"`(\[FILL:[A-Z][A-Z0-9]*-[0-9]+\])`", cells[1])
                if marker is not None:
                    row = marker.group(1)
                    rows.add(row)
                    value_unissued.add(row)
            continue
        row = match.group(1)
        rows.add(row)
        if "SUPPLIER_UNKNOWN" in line:
            supplier_unknown.add(row)
        if "VALUE_UNISSUED" in line:
            value_unissued.add(row)
    return frozenset(rows), frozenset(supplier_unknown), frozenset(value_unissued)


REGISTRY_ROWS, SUPPLIER_UNKNOWN_ROWS, VALUE_UNISSUED_ROWS = _registry_rows()
APPENDIX_DERIVE_ROWS = frozenset(row for row in REGISTRY_ROWS if row.startswith("[FILL:"))


class StopFill(ValueError):
    """A registry-governed refusal to emit any Results prose."""

    def __init__(self, registry_row: str, label: str, reason: str):
        if registry_row not in REGISTRY_ROWS:
            raise ValueError(f"unknown Results fill registry row: {registry_row}")
        super().__init__(reason)
        self.registry_row = registry_row
        self.label = label
        self.reason = reason

    def as_dict(self) -> dict[str, str]:
        return {
            "label": self.label,
            "reason": self.reason,
            "registry_row": self.registry_row,
        }

    def __str__(self) -> str:
        return "STOP_FILL " + json.dumps(
            self.as_dict(), ensure_ascii=False, sort_keys=True
        )


class RenderedValidationError(ValueError):
    """Final prose is not a canonical filled single-variant rendering."""


def _stop(row: str, label: str, reason: str) -> StopFill:
    return StopFill(row, label, reason)


def _supplier_unknown(row: str) -> None:
    if row not in SUPPLIER_UNKNOWN_ROWS:
        raise RuntimeError(f"renderer misclassified non-SUPPLIER_UNKNOWN row {row}")
    raise _stop(
        row,
        "SUPPLIER_UNKNOWN",
        "the registry freezes this token but defines no producing artifact field",
    )


def _value_unissued(row: str) -> None:
    if row not in VALUE_UNISSUED_ROWS:
        raise RuntimeError(f"renderer misclassified non-VALUE_UNISSUED row {row}")
    raise _stop(
        row,
        "VALUE_UNISSUED",
        "the registry binds this token to a producing field, but no issued "
        "artifact carries a value for it yet",
    )


def _pairs_without_duplicates(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_nonfinite_json(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value!r}")


def load_json(path: Path, *, row: str = GLOBAL_INPUT_ROW) -> Any:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise _stop(row, "ABSENT_ARTIFACT", f"cannot read {path}: {exc}") from exc
    try:
        return json.loads(
            raw,
            parse_float=Decimal,
            parse_int=Decimal,
            parse_constant=_reject_nonfinite_json,
            object_pairs_hook=_pairs_without_duplicates,
        )
    except (InvalidOperation, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise _stop(row, "MALFORMED_INPUT", f"malformed JSON in {path}: {exc}") from exc


def _mapping(value: Any, row: str, where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise _stop(row, "MALFORMED_INPUT", f"{where} must be an object")
    return value


def _string(value: Any, row: str, where: str) -> str:
    if not isinstance(value, str) or not value or "\n" in value or "\r" in value:
        raise _stop(row, "MALFORMED_INPUT", f"{where} must be a nonempty single-line string")
    return value


def _string_list(value: Any, row: str, where: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise _stop(row, "MALFORMED_INPUT", f"{where} must be an array")
    result = tuple(_string(item, row, f"{where}[]") for item in value)
    if len(set(result)) != len(result):
        raise _stop(row, "MALFORMED_INPUT", f"{where} contains duplicates")
    return result


def _reason_code(value: Any, row: str, where: str) -> str:
    code = _string(value, row, where)
    if re.fullmatch(r"[a-z0-9_]+", code) is None:
        raise _stop(row, "MALFORMED_INPUT", f"{where} must be a reason-code spelling")
    return code


def _decimal(
    value: Any,
    row: str,
    where: str,
    *,
    nonnegative: bool = False,
) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, int, str)):
        raise _stop(row, "MALFORMED_INPUT", f"{where} must be a finite exact number")
    try:
        number = value if isinstance(value, Decimal) else Decimal(str(value))
    except InvalidOperation as exc:
        raise _stop(row, "MALFORMED_INPUT", f"{where} must be a finite exact number") from exc
    if not number.is_finite():
        raise _stop(row, "MALFORMED_INPUT", f"{where} must be finite")
    if nonnegative and number < 0:
        raise _stop(row, "MALFORMED_INPUT", f"{where} must be nonnegative")
    return number


def format_decimal(value: Decimal) -> str:
    if value == 0:
        return "0"
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def _artifact_path(base: Path, value: Any, row: str, where: str) -> Path:
    raw = _string(value, row, where)
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", raw):
        raise _stop(row, "MALFORMED_INPUT", f"{where} must be a local path")
    path = Path(raw)
    return path if path.is_absolute() else base / path


def _load_artifact(
    base: Path,
    value: Any,
    row: str,
    where: str,
    schema_version: str,
) -> Mapping[str, Any]:
    if value is None:
        raise _stop(row, "ABSENT_ARTIFACT", f"{where} is absent")
    path = _artifact_path(base, value, row, where)
    artifact = _mapping(load_json(path, row=row), row, where)
    if artifact.get("schema_version") != schema_version:
        raise _stop(
            row,
            "MALFORMED_INPUT",
            f"{where}.schema_version must equal {schema_version!r}",
        )
    return artifact


class WindowVerdict(NamedTuple):
    status: str
    reason: str | None

    @property
    def passed(self) -> bool:
        return self.status == "passed"


def _render_code_list(values: Sequence[str]) -> str:
    if not values:
        return "none recorded"
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return ", ".join(values[:-1]) + f", and {values[-1]}"


def load_window_verdict(
    base: Path, campaign: Mapping[str, Any], role: str
) -> WindowVerdict:
    row = f"[REFUSAL_REASON_{'1p5B' if role == 'alpha' else '7B'}_floor_window]"
    artifact = _load_artifact(
        base,
        campaign.get("verdict"),
        row,
        f"campaigns.{role}.verdict",
        VERDICT_SCHEMA_VERSION,
    )
    if artifact.get("record_type") != "idle_admission_whole_window_verdict":
        raise _stop(row, "MALFORMED_INPUT", f"campaigns.{role}.verdict.record_type is invalid")
    status = _string(artifact.get("status"), row, f"campaigns.{role}.verdict.status")
    if status not in {"passed", "failed", "flagged", "invalid"}:
        raise _stop(row, "UNKNOWN_FIELD", f"unknown whole-window status {status!r}")
    core = _mapping(
        artifact.get("idle_admission_core"),
        row,
        f"campaigns.{role}.verdict.idle_admission_core",
    )
    conditions = _string_list(
        core.get("conditions"), row, f"campaigns.{role}.verdict.idle_admission_core.conditions"
    )
    conditions = tuple(
        _reason_code(value, row, f"campaigns.{role}.verdict condition")
        for value in conditions
    )
    failures = artifact.get("member_failures")
    if not isinstance(failures, list) or any(not isinstance(item, Mapping) for item in failures):
        raise _stop(row, "MALFORMED_INPUT", f"campaigns.{role}.verdict.member_failures must be an object array")
    failure_codes: list[str] = []
    for index, failure in enumerate(failures):
        assert isinstance(failure, Mapping)
        code = next(
            (
                failure.get(key)
                for key in ("reason", "condition", "reason_code", "status")
                if isinstance(failure.get(key), str) and failure.get(key)
            ),
            None,
        )
        if code is None:
            raise _stop(row, "MALFORMED_INPUT", f"member_failures[{index}] lacks a reason code")
        failure_codes.append(
            _reason_code(code, row, f"member_failures[{index}].reason")
        )
    if status == "passed":
        if artifact.get("claim_licensing") is not True or conditions or failure_codes:
            raise _stop(
                row,
                "FAILED_PREDICATE",
                "a passed whole-window verdict must be claim-licensing with no conditions or member failures",
            )
        return WindowVerdict(status="passed", reason=None)
    reason_parts = [f"the issued whole-window verdict status was {status}"]
    if conditions:
        reason_parts.append(f"conditions: {_render_code_list(conditions)}")
    if failure_codes:
        reason_parts.append(f"member failures: {_render_code_list(failure_codes)}")
    return WindowVerdict(status=status, reason="; ".join(reason_parts))


class ComponentState(NamedTuple):
    classification: str
    value: Decimal | None
    terminal_reasons: tuple[str, ...]
    normalized_reason: str | None
    dominance: bool
    point_diagnostic: Decimal | None


class CellFill(NamedTuple):
    stem: str
    branch: str
    fills: Mapping[str, str]
    reason: str | None

    @property
    def published(self) -> bool:
        return self.branch in {"L", "U"}


def _unique_index(rows: Any, key: str, row: str, where: str) -> dict[str, Mapping[str, Any]]:
    if not isinstance(rows, list):
        raise _stop(row, "MALFORMED_INPUT", f"{where} must be an array")
    result: dict[str, Mapping[str, Any]] = {}
    for index, value in enumerate(rows):
        item = _mapping(value, row, f"{where}[{index}]")
        identity = _string(item.get(key), row, f"{where}[{index}].{key}")
        if identity in result:
            raise _stop(row, "MALFORMED_INPUT", f"duplicate {where} {identity!r}")
        result[identity] = item
    return result


def _component_state(
    component: Mapping[str, Any], expected_kind: str, stem: str
) -> ComponentState:
    component_row = f"[F_{stem}_{'abs' if expected_kind == 'absolute' else 'cmp'}_J]"
    if component.get("kind") != expected_kind:
        raise _stop(component_row, "MALFORMED_INPUT", f"extraction component kind must be {expected_kind!r}")
    reasons = _string_list(component.get("refusal_reasons"), component_row, "component.refusal_reasons")
    known = TERMINAL_REASON_CODES | {DOMINANCE_CODE}
    unknown = set(reasons) - known
    if unknown:
        raise _stop(component_row, "UNKNOWN_FIELD", f"unknown extraction reason code(s): {_render_code_list(sorted(unknown))}")
    terminal = tuple(reason for reason in reasons if reason in TERMINAL_REASON_CODES)
    floor = component.get("floor")
    operative = component.get("operative_floor_j")
    extractable = component.get("extractable")
    if not isinstance(extractable, bool):
        raise _stop(
            component_row,
            "MALFORMED_INPUT",
            "component.extractable must be a boolean",
        )
    if (floor is None) != (operative is None):
        raise _stop(
            component_row,
            "MALFORMED_INPUT",
            "component floor and operative_floor_j must be present or absent together",
        )
    if floor is not None:
        floor_map = _mapping(floor, component_row, "component.floor")
        available = _decimal(
            operative,
            component_row,
            "component.operative_floor_j",
            nonnegative=True,
        )
        expected_available = floor_map.get(
            "drift_widened_guarded_floor_j", floor_map.get("guarded_floor_j")
        )
        if available != _decimal(
            expected_available,
            component_row,
            "component.floor final guarded value",
            nonnegative=True,
        ):
            raise _stop(
                component_row,
                "FAILED_PREDICATE",
                "extraction operative floor disagrees with its final guarded floor",
            )
    if terminal:
        if extractable:
            raise _stop(
                component_row,
                "MALFORMED_INPUT",
                "component with a terminal reason cannot be extractable",
            )
        return ComponentState("terminal", None, terminal, None, False, None)
    if reasons == (DOMINANCE_CODE,) and floor is None:
        if component.get("extractable") is not False or operative is not None or component.get("floor_conditions") not in (None, []):
            raise _stop(component_row, "MALFORMED_INPUT", "exact-unavailable component metadata is inconsistent")
        code = (
            "exact_corner_widened_absolute_floor_unavailable"
            if expected_kind == "absolute"
            else "exact_corner_widened_comparative_floor_unavailable"
        )
        if code not in NONTERMINAL_CODES:
            raise RuntimeError("canonical nonterminal vocabulary drifted")
        phrase = (
            "the absolute component did not yield an exact corner-widened floor"
            if expected_kind == "absolute"
            else "the comparative component did not yield an exact corner-widened floor"
        )
        return ComponentState("exact_unavailable", None, (), phrase, False, None)
    if reasons:
        raise _stop(component_row, "MALFORMED_INPUT", "unmatched nonterminal component reason state")
    assert floor is not None and operative is not None
    floor_map = _mapping(floor, component_row, "component.floor")
    if not extractable:
        raise _stop(component_row, "FAILED_PREDICATE", "exact component must be extractable")
    value = _decimal(operative, component_row, "component.operative_floor_j", nonnegative=True)
    expected_value = floor_map.get(
        "drift_widened_guarded_floor_j", floor_map.get("guarded_floor_j")
    )
    if value != _decimal(expected_value, component_row, "component.floor final guarded value", nonnegative=True):
        raise _stop(component_row, "FAILED_PREDICATE", "extraction operative floor disagrees with its final guarded floor")
    conditions = component.get("floor_conditions", [])
    conditions_tuple = _string_list(conditions, component_row, "component.floor_conditions")
    if conditions_tuple not in {(), (DOMINANCE_CODE,)}:
        raise _stop(component_row, "UNKNOWN_FIELD", "component floor_conditions is outside the closed selector")
    dominance = conditions_tuple == (DOMINANCE_CODE,)
    point: Decimal | None = None
    if dominance:
        if (
            component.get("floor_limit_class") != ATTRIBUTION_LIMIT_CLASS
            or component.get("floor_source") != ATTRIBUTION_FLOOR_SOURCE
        ):
            raise _stop(component_row, "FAILED_PREDICATE", "dominance licence metadata is incomplete")
        diagnostic = _mapping(component.get("point_floor_diagnostic"), component_row, "component.point_floor_diagnostic")
        if diagnostic.get("published_claim_floor") is not False:
            raise _stop(component_row, "FAILED_PREDICATE", "point diagnostic must not be a published claim floor")
        point = _decimal(diagnostic.get("guarded_floor_j"), component_row, "point diagnostic guarded_floor_j", nonnegative=True)
    elif any(
        key in component
        for key in ("floor_limit_class", "floor_source", "point_floor_diagnostic")
    ):
        raise _stop(component_row, "FAILED_PREDICATE", "unlabelled exact component carries attribution-limit metadata")
    return ComponentState("exact", value, (), None, dominance, point)


def derive_numeric(
    token: str,
    parents: Sequence[Decimal],
    *,
    stored: Decimal | None = None,
    predicate: str | None = None,
) -> Decimal:
    """Execute one registry-named numeric DERIVE rule, never an open formula."""

    row = f"[{token}]"
    if any(not isinstance(parent, Decimal) or not parent.is_finite() for parent in parents):
        raise _stop(row, "MALFORMED_INPUT", "DERIVE parents must be finite exact decimals")
    if stored is not None and (
        not isinstance(stored, Decimal) or not stored.is_finite()
    ):
        raise _stop(row, "MALFORMED_INPUT", "stored DERIVE check must be a finite exact decimal")
    operative = re.fullmatch(r"F_(?:1p5B|7B)_(?:prompt|decode)_operative_J", token)
    if operative or token == "F_claim_decode_armwise_max_J":
        if len(parents) != 2:
            raise _stop(row, "ABSENT_ARTIFACT", "max derivation requires both exact parents")
        if any(parent < 0 for parent in parents):
            raise _stop(row, "MALFORMED_INPUT", "floor parents must be nonnegative")
        result = max(parents)
    elif token == "M_decode_contrast_abs_J_per_request":
        if len(parents) != 1:
            raise _stop(row, "ABSENT_ARTIFACT", "absolute-magnitude derivation requires the signed parent")
        result = abs(parents[0])
    elif token == "C_decode_floor_clearance_J":
        if predicate != "floor_gate_pass" or len(parents) != 2:
            raise _stop(row, "FAILED_PREDICATE", "clearance is licensed only after floor-gate passage")
        if any(parent < 0 for parent in parents):
            raise _stop(row, "MALFORMED_INPUT", "clearance parents must be nonnegative")
        result = parents[0] - parents[1]
        if result <= 0:
            raise _stop(row, "FAILED_PREDICATE", "floor-gate passage requires positive clearance")
    elif token == "S_decode_floor_shortfall_J":
        if predicate != "floor_gate_refused" or len(parents) != 2:
            raise _stop(row, "FAILED_PREDICATE", "shortfall is licensed only on floor-gate refusal")
        if any(parent < 0 for parent in parents):
            raise _stop(row, "MALFORMED_INPUT", "shortfall parents must be nonnegative")
        result = parents[0] - parents[1]
        if result < 0:
            raise _stop(row, "FAILED_PREDICATE", "floor-gate refusal cannot have negative shortfall")
    elif token == "R_decode_effect_x_floor":
        if len(parents) != 2 or parents[0] < 0 or parents[1] <= 0:
            raise _stop(row, "FAILED_PREDICATE", "effect-to-floor ratio requires an exact nonzero floor")
        numerator_n, numerator_d = parents[0].as_integer_ratio()
        denominator_n, denominator_d = parents[1].as_integer_ratio()
        fraction = Fraction(numerator_n, numerator_d) / Fraction(
            denominator_n, denominator_d
        )
        remainder = fraction.denominator
        for factor in (2, 5):
            while remainder % factor == 0:
                remainder //= factor
        if remainder != 1:
            raise _stop(
                row,
                "FAILED_PREDICATE",
                "registry defines no rounding rule for a non-terminating exact ratio",
            )
        result = Decimal(fraction.numerator) / Decimal(fraction.denominator)
    elif token == "S_decode_joint_J":
        _supplier_unknown("[B_decode_claim_J]")
        raise AssertionError("unreachable")
    else:
        raise _stop(row, "UNKNOWN_FIELD", "no registry-named DERIVE rule exists for this token")
    if stored is not None and stored != result:
        raise _stop(row, "FAILED_PREDICATE", "stored value disagrees with the registry derivation")
    return result


def _point_clause(states: Sequence[tuple[str, ComponentState]]) -> str:
    clauses = []
    for label, state in states:
        if state.point_diagnostic is None:
            continue
        clauses.append(
            f"The {label} point-only repeatability diagnostic was "
            f"{format_decimal(state.point_diagnostic)} J; it is retained as a "
            "diagnostic and cannot support a claim."
        )
    return " ".join(clauses)


def _available_diagnostic_clause(states: Sequence[tuple[str, ComponentState]]) -> str:
    clauses = []
    for label, state in states:
        if state.value is not None:
            clauses.append(
                f"The available {label} component was {format_decimal(state.value)} J. "
                "Because no operative cell floor exists, that component is "
                "diagnostic only and cannot support a claim."
            )
    for label, state in states:
        if state.point_diagnostic is not None:
            clauses.append(
                f"The {label} point-only repeatability diagnostic was "
                f"{format_decimal(state.point_diagnostic)} J; it is retained as a "
                "diagnostic and cannot support a claim."
            )
    return " ".join(clauses) or (
        "No authenticated numeric component or point-only repeatability "
        "diagnostic is available for this cell."
    )


def _mint_point_diagnostics(
    mint_cell: Mapping[str, Any],
    states: Sequence[tuple[str, ComponentState]],
    row: str,
) -> None:
    diagnostics = _mapping(mint_cell.get("point_floor_diagnostics"), row, "mint point_floor_diagnostics")
    expected_labels = {label for label, state in states if state.dominance}
    if set(diagnostics) != expected_labels:
        raise _stop(row, "FAILED_PREDICATE", "mint point diagnostics do not match licensed components")
    for label, state in states:
        if not state.dominance:
            continue
        diagnostic = _mapping(diagnostics[label], row, f"mint point_floor_diagnostics.{label}")
        if diagnostic.get("published_claim_floor") is not False:
            raise _stop(row, "FAILED_PREDICATE", "mint point diagnostic is marked as a published claim floor")
        value = _decimal(diagnostic.get("guarded_floor_j"), row, "mint point diagnostic guarded_floor_j", nonnegative=True)
        if value != state.point_diagnostic:
            raise _stop(row, "FAILED_PREDICATE", "mint and extraction point diagnostics disagree")


def _cell_fill(
    stem: str,
    mint_cell: Mapping[str, Any],
    absolute: Mapping[str, Any],
    comparative: Mapping[str, Any],
) -> CellFill:
    states = (
        ("absolute", _component_state(absolute, "absolute", stem)),
        ("comparative", _component_state(comparative, "comparative", stem)),
    )
    terminal = tuple(reason for _, state in states for reason in state.terminal_reasons)
    if terminal:
        reason = _render_code_list(sorted(set(terminal)))
        return CellFill(
            stem,
            "T",
            {f"TERMINAL_REFUSAL_REASON_{stem}": reason},
            reason,
        )
    inexact = [state for _, state in states if state.classification != "exact"]
    if inexact:
        if any(state.classification != "exact_unavailable" for state in inexact):
            raise _stop(f"[NO_EXACT_FLOOR_REASON_{stem}]", "FAILED_PREDICATE", "generic absence cannot select the no-exact-floor branch")
        for label, state in states:
            suffix = "abs" if label == "absolute" else "cmp"
            row = f"[F_{stem}_{suffix}_J]"
            stored = mint_cell.get(f"floor_{suffix}_j")
            if state.classification == "exact":
                assert state.value is not None
                measured = _decimal(
                    stored, row, f"mint floor_{suffix}_j", nonnegative=True
                )
                if measured != state.value:
                    raise _stop(
                        row,
                        "FAILED_PREDICATE",
                        f"mint {label} component disagrees with extraction",
                    )
            elif stored is not None:
                raise _stop(
                    row,
                    "FAILED_PREDICATE",
                    f"mint {label} component must be absent when exact-unavailable",
                )
        if mint_cell.get("floor_gate_j") is not None:
            raise _stop(
                f"[F_{stem}_operative_J]",
                "FAILED_PREDICATE",
                "mint operative floor must be absent on the no-exact-floor path",
            )
        if any(state.dominance for _, state in states):
            _mint_point_diagnostics(
                mint_cell, states, f"[POINT_DIAGNOSTIC_CLAUSE_{stem}]"
            )
        reasons = [state.normalized_reason for state in inexact if state.normalized_reason]
        reason = _render_code_list(reasons)
        return CellFill(
            stem,
            "N",
            {
                f"NO_EXACT_FLOOR_REASON_{stem}": reason,
                f"AVAILABLE_DIAGNOSTIC_CLAUSE_{stem}": _available_diagnostic_clause(states),
            },
            reason,
        )
    absolute_state = states[0][1]
    comparative_state = states[1][1]
    assert absolute_state.value is not None and comparative_state.value is not None
    abs_row = f"[F_{stem}_abs_J]"
    cmp_row = f"[F_{stem}_cmp_J]"
    op_row = f"[F_{stem}_operative_J]"
    mint_abs = _decimal(mint_cell.get("floor_abs_j"), abs_row, "mint floor_abs_j", nonnegative=True)
    mint_cmp = _decimal(mint_cell.get("floor_cmp_j"), cmp_row, "mint floor_cmp_j", nonnegative=True)
    if mint_abs != absolute_state.value:
        raise _stop(abs_row, "FAILED_PREDICATE", "mint absolute component disagrees with extraction")
    if mint_cmp != comparative_state.value:
        raise _stop(cmp_row, "FAILED_PREDICATE", "mint comparative component disagrees with extraction")
    stored_gate = _decimal(mint_cell.get("floor_gate_j"), op_row, "mint floor_gate_j", nonnegative=True)
    operative = derive_numeric(op_row[1:-1], (mint_abs, mint_cmp), stored=stored_gate)
    eligibility = _mapping(mint_cell.get("eligibility"), op_row, "mint eligibility")
    if eligibility.get("status") != "claim_ready" or eligibility.get("claim_usable") is not True:
        raise _stop(op_row, "FAILED_PREDICATE", "mint cell is not claim-ready and claim-usable")
    eligibility_reasons = _string_list(
        eligibility.get("reason_codes"), op_row, "mint eligibility.reason_codes"
    )
    if eligibility_reasons:
        raise _stop(
            op_row,
            "FAILED_PREDICATE",
            "claim-ready mint eligibility must not retain reason codes",
        )
    any_dominance = any(state.dominance for _, state in states)
    limit_keys = {"floor_limit_class", "floor_source", "point_floor_diagnostics"} & set(mint_cell)
    if any_dominance:
        if (
            mint_cell.get("floor_limit_class") != ATTRIBUTION_LIMIT_CLASS
            or mint_cell.get("floor_source") != ATTRIBUTION_FLOOR_SOURCE
        ):
            reason = "attribution_dominance_unlicensed"
            return CellFill(stem, "T", {f"TERMINAL_REFUSAL_REASON_{stem}": reason}, reason)
        _mint_point_diagnostics(mint_cell, states, op_row)
        branch = "L"
    elif limit_keys:
        reason = "attribution_dominance_unlicensed"
        return CellFill(stem, "T", {f"TERMINAL_REFUSAL_REASON_{stem}": reason}, reason)
    else:
        branch = "U"
    fills = {
        f"F_{stem}_abs_J": format_decimal(mint_abs),
        f"F_{stem}_cmp_J": format_decimal(mint_cmp),
        f"F_{stem}_operative_J": format_decimal(operative),
    }
    if branch == "L":
        fills[f"POINT_DIAGNOSTIC_CLAUSE_{stem}"] = _point_clause(states)
    return CellFill(stem, branch, fills, None)


def load_campaign_cells(
    base: Path, campaign: Mapping[str, Any], role: str
) -> dict[str, CellFill]:
    model = "1p5B" if role == "alpha" else "7B"
    first_row = f"[F_{model}_prompt_abs_J]"
    floor = _load_artifact(
        base,
        campaign.get("floor_artifact"),
        first_row,
        f"campaigns.{role}.floor_artifact",
        FLOOR_SCHEMA_VERSION,
    )
    extraction = _load_artifact(
        base,
        campaign.get("extraction"),
        first_row,
        f"campaigns.{role}.extraction",
        EXTRACTION_SCHEMA_VERSION,
    )
    mint_cells = _unique_index(floor.get("cells"), "cell_id", first_row, "floor_artifact.cells")
    extracted_cells = _unique_index(extraction.get("cells"), "cell_id", first_row, "extraction.cells")
    bindings = _mapping(campaign.get("cells"), first_row, f"campaigns.{role}.cells")
    if set(bindings) != {"prompt", "decode"}:
        raise _stop(first_row, "MALFORMED_INPUT", f"campaigns.{role}.cells must bind prompt and decode exactly")
    result: dict[str, CellFill] = {}
    for phase in ("prompt", "decode"):
        stem = f"{model}_{phase}"
        row = f"[F_{stem}_abs_J]"
        binding = _mapping(bindings[phase], row, f"campaigns.{role}.cells.{phase}")
        required = {
            "floor_cell_id",
            "absolute_extraction_cell_id",
            "comparative_extraction_cell_id",
        }
        if set(binding) != required:
            raise _stop(row, "MALFORMED_INPUT", f"campaigns.{role}.cells.{phase} has invalid binding keys")
        floor_id = _string(binding["floor_cell_id"], row, "floor_cell_id")
        absolute_id = _string(binding["absolute_extraction_cell_id"], row, "absolute_extraction_cell_id")
        comparative_id = _string(binding["comparative_extraction_cell_id"], row, "comparative_extraction_cell_id")
        try:
            result[phase] = _cell_fill(
                stem,
                mint_cells[floor_id],
                extracted_cells[absolute_id],
                extracted_cells[comparative_id],
            )
        except KeyError as exc:
            raise _stop(row, "ABSENT_ARTIFACT", f"bound cell identifier is absent: {exc.args[0]}") from exc
    return result


def select_variant_from_atoms(section: str, atoms: Mapping[str, bool]) -> str:
    """Select exactly one canonical predicate branch from explicit atoms."""

    if section == "7":
        trees, _ = CANONICAL.parse_variant_predicates(TEMPLATE_TEXT)
    elif section == "6":
        trees = CANONICAL.parse_section6_predicates(TEMPLATE_TEXT)
    else:
        raise ValueError("section must be '6' or '7'")
    selected = [name for name, tree in trees.items() if CANONICAL.eval_expr(tree, dict(atoms))]
    if len(selected) != 1:
        raise _stop(GLOBAL_INPUT_ROW, "FAILED_PREDICATE", f"section {section} selected {selected!r}, expected exactly one variant")
    return selected[0]


def _replace_tokens(text: str, fills: Mapping[str, str]) -> str:
    _refuse_appendix_derivations(text)
    seen: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        token = match.group(1)
        if token not in fills:
            raise _stop(f"[{token}]", "ABSENT_ARTIFACT", "selected prose token has no authenticated fill")
        value = fills[token]
        if not value or "\n" in value or "\r" in value:
            raise _stop(f"[{token}]", "MALFORMED_INPUT", "fill must be a nonempty single-line value")
        seen.add(token)
        return value

    rendered = FILL_TOKEN_RE.sub(replace, text)
    unused = set(fills) - seen
    if unused:
        raise RuntimeError(f"renderer supplied unused fills: {sorted(unused)}")
    return rendered


def _branch_text(block: str, branch: str) -> str:
    labels, parts = CANONICAL.branch_parts(block)
    if labels != ["T", "N", "L", "U"]:
        raise RuntimeError("canonical branch schema changed")
    part = parts[branch]
    start = part.find("**TEXT:**")
    end = part.find("**BINDS:**", start)
    if start < 0 or end < 0:
        raise RuntimeError("canonical branch TEXT/BINDS markers changed")
    value = part[start + len("**TEXT:**"):end].strip()
    return re.sub(r"\n  ", "\n", value)


def _render_section7_d(cells: Mapping[str, CellFill]) -> str:
    heading = S7_HEADINGS["7_D"]
    body = CANONICAL.section(TEMPLATE_TEXT, heading)
    lead_start = body.index("**Lead-in replacement.**") + len("**Lead-in replacement.**")
    lead_end = body.index("<!-- CELL_BRANCH_SET:", lead_start)
    parts = [heading, body[lead_start:lead_end].strip()]
    fills: dict[str, str] = {}
    for match in CANONICAL.CELL_RE.finditer(body):
        stem = CANONICAL.cell_stem(match.group("id"))
        cell = cells[stem]
        block = match.group("body")
        first_branch = CANONICAL.BRANCH_RE.search(block)
        if first_branch is None:
            raise RuntimeError("canonical cell label/branch schema changed")
        cell_label = block[: first_branch.start()].strip()
        parts.append(cell_label + "\n\n" + _branch_text(block, cell.branch))
        fills.update(cell.fills)
    nonpublication = []
    for stem, display in (
        ("1p5B_decode", "the 1.5B token-generation cell"),
        ("7B_decode", "the 7B token-generation cell"),
    ):
        cell = cells[stem]
        if cell.branch in {"T", "N"}:
            assert cell.reason is not None
            nonpublication.append(f"{display}: {cell.reason}")
    if not nonpublication:
        raise _stop("[CELL_NONPUBLICATION_SUMMARY]", "FAILED_PREDICATE", "Variant D requires at least one decode nonpublication branch")
    fills["CELL_NONPUBLICATION_SUMMARY"] = _render_code_list(nonpublication)
    last_end = max(match.end() for match in CANONICAL.CELL_RE.finditer(body))
    ending = body[last_end:]
    ending = ending[: ending.index("Do not emit")].strip()
    parts.append(ending)
    return _replace_tokens("\n\n".join(parts).strip() + "\n", fills)


def _without_predicate_and_guard(section: str) -> str:
    section = re.sub(r"<!-- VARIANT_PREDICATE .*?-->\n*", "", section, count=1, flags=re.S)
    section = re.sub(r"\*\*SELECTION GUARD[^\n]*\*\*.*?(?=\n\n)", "", section, count=1, flags=re.S)
    return re.sub(r"\n{3,}", "\n\n", section).strip() + "\n"


def _render_section7_c3(alpha: WindowVerdict, beta: WindowVerdict) -> str:
    if alpha.reason is None or beta.reason is None:
        raise _stop(GLOBAL_INPUT_ROW, "FAILED_PREDICATE", "Variant C3 requires two refused verdicts")
    source = CANONICAL.section(TEMPLATE_TEXT, S7_HEADINGS["7_C3"])
    return _replace_tokens(
        _without_predicate_and_guard(source),
        {
            "REFUSAL_REASON_1p5B_floor_window": alpha.reason,
            "REFUSAL_REASON_7B_floor_window": beta.reason,
        },
    )


def _render_section6_zero() -> str:
    source = CANONICAL.section(TEMPLATE_TEXT, S6_HEADINGS["0"])
    start = source.index("No characterization result")
    end = source.index("At fill time", start)
    return S6_HEADINGS["0"] + "\n\n" + source[start:end].strip() + "\n"


def _select_section6(
    base: Path, characterization: Mapping[str, Any]
) -> str:
    funded = characterization.get("funded")
    run = characterization.get("run")
    if not isinstance(funded, bool) or not isinstance(run, bool):
        raise _stop("[PLAIN_LANGUAGE_RESULT_linearity]", "MALFORMED_INPUT", "characterization funded/run must be booleans")
    verdict_ref = characterization.get("verdict")
    if not (funded and run and verdict_ref is not None):
        return _render_section6_zero()
    artifact = _load_artifact(
        base,
        verdict_ref,
        "[REFUSAL_REASON_window_C]",
        "characterization.verdict",
        VERDICT_SCHEMA_VERSION,
    )
    status = artifact.get("status")
    if status == "passed":
        # The characterization result schema froze every row field on
        # 2026-08-24, so these rows are no longer SUPPLIER_UNKNOWN; they stop
        # because no characterization report has been issued.
        _value_unissued("[PLAIN_LANGUAGE_RESULT_linearity]")
    if status in {"failed", "flagged", "invalid"}:
        _value_unissued("[D_C_linearity_diagnostic_J_per_token]")
    raise _stop("[REFUSAL_REASON_window_C]", "UNKNOWN_FIELD", f"unknown characterization verdict status {status!r}")


def render_from_manifest(path: Path) -> str:
    manifest = _mapping(load_json(path), GLOBAL_INPUT_ROW, "input")
    allowed = {"schema_version", "fixture_label", "campaigns", "gamma", "characterization"}
    if set(manifest) - allowed:
        raise _stop(GLOBAL_INPUT_ROW, "MALFORMED_INPUT", f"unknown input key(s): {sorted(set(manifest) - allowed)}")
    if manifest.get("schema_version") != INPUT_SCHEMA_VERSION:
        raise _stop(GLOBAL_INPUT_ROW, "MALFORMED_INPUT", f"input.schema_version must equal {INPUT_SCHEMA_VERSION!r}")
    campaigns = _mapping(manifest.get("campaigns"), GLOBAL_INPUT_ROW, "campaigns")
    if set(campaigns) != {"alpha", "beta"}:
        raise _stop(GLOBAL_INPUT_ROW, "MALFORMED_INPUT", "campaigns must contain alpha and beta exactly")
    alpha_campaign = _mapping(campaigns["alpha"], GLOBAL_INPUT_ROW, "campaigns.alpha")
    beta_campaign = _mapping(campaigns["beta"], GLOBAL_INPUT_ROW, "campaigns.beta")
    base = path.parent
    alpha_verdict = load_window_verdict(base, alpha_campaign, "alpha")
    beta_verdict = load_window_verdict(base, beta_campaign, "beta")

    if not alpha_verdict.passed and not beta_verdict.passed:
        section7 = _render_section7_c3(alpha_verdict, beta_verdict)
    elif alpha_verdict.passed and beta_verdict.passed:
        alpha_cells = load_campaign_cells(base, alpha_campaign, "alpha")
        beta_cells = load_campaign_cells(base, beta_campaign, "beta")
        cells = {
            "1p5B_prompt": alpha_cells["prompt"],
            "1p5B_decode": alpha_cells["decode"],
            "7B_prompt": beta_cells["prompt"],
            "7B_decode": beta_cells["decode"],
        }
        if not cells["1p5B_decode"].published or not cells["7B_decode"].published:
            section7 = _render_section7_d(cells)
        else:
            # Every A/B predicate requires the claim-side bound.  The registry
            # explicitly forbids binding the tempting deterministic total.
            _supplier_unknown("[B_decode_claim_J]")
            raise AssertionError("unreachable")
    else:
        passing_role = "alpha" if alpha_verdict.passed else "beta"
        passing_campaign = alpha_campaign if alpha_verdict.passed else beta_campaign
        load_campaign_cells(base, passing_campaign, passing_role)
        first_mean = (
            "[E_1p5B_prompt_J_per_request]"
            if alpha_verdict.passed
            else "[E_7B_prompt_J_per_request]"
        )
        _supplier_unknown(first_mean)
        raise AssertionError("unreachable")

    characterization = _mapping(
        manifest.get("characterization"),
        "[PLAIN_LANGUAGE_RESULT_linearity]",
        "characterization",
    )
    section6 = _select_section6(base, characterization)
    rendered = section7.rstrip() + "\n\n" + section6
    validate_rendered(rendered)
    return rendered


def _token_value_pattern(token: str) -> str:
    if token.startswith("N_bundles_") or token == "N_C_eligible_sessions":
        return INTEGER_RE
    if token.startswith(("TERMINAL_REFUSAL_REASON_", "NO_EXACT_FLOOR_REASON_", "REFUSAL_REASON_")):
        return SAFE_REASON_RE
    if token == "CELL_NONPUBLICATION_SUMMARY":
        return SAFE_REASON_RE
    if token.startswith(("AVAILABLE_DIAGNOSTIC_CLAUSE_", "POINT_DIAGNOSTIC_CLAUSE_")):
        return SAFE_REASON_RE
    if token.startswith("PLAIN_LANGUAGE_RESULT_"):
        return (
            r"(?:supported the registered behavior|did not support a conclusion under the registered criterion|"
            r"showed that the registered expected behavior did not hold|"
            r"remains pending because fewer than three eligible sessions are available)"
        )
    return NUMBER_RE


def _line_pattern(line: str) -> re.Pattern[str]:
    parts: list[str] = []
    position = 0
    for match in FILL_TOKEN_RE.finditer(line):
        parts.append(re.escape(line[position:match.start()]))
        parts.append(_token_value_pattern(match.group(1)))
        position = match.end()
    parts.append(re.escape(line[position:]))
    return re.compile("^" + "".join(parts) + "$")


def _canonical_render_line_patterns(source: str) -> tuple[re.Pattern[str], ...]:
    patterns: dict[str, re.Pattern[str]] = {}
    prefixes = (
        "**TEXT:**",
        "**PRESENT TEXT:**",
        "**ABSENT TEXT:**",
        "**COMPANION TEXT:**",
        "**NO-COMPANION TEXT:**",
        "**Lead-in replacement.**",
        "**Lead-in action.**",
    )
    for raw in source.splitlines():
        line = raw.strip()
        if not line:
            continue
        candidates = [line]
        for prefix in prefixes:
            if line.startswith(prefix):
                remainder = line[len(prefix):].strip()
                candidates = [remainder] if remainder else []
                break
        for candidate in candidates:
            if candidate:
                pattern = _line_pattern(candidate)
                patterns[pattern.pattern] = pattern
    return tuple(patterns.values())


CANONICAL_RENDER_LINE_PATTERNS = {
    **{
        f"7:{key}": _canonical_render_line_patterns(
            CANONICAL.section(TEMPLATE_TEXT, heading)
        )
        for key, heading in S7_HEADINGS.items()
    },
    **{
        f"6:{key}": _canonical_render_line_patterns(
            CANONICAL.section(TEMPLATE_TEXT, heading)
        )
        for key, heading in S6_HEADINGS.items()
    },
}


def _refuse_appendix_derivations(text: str) -> None:
    for row in sorted(APPENDIX_DERIVE_ROWS):
        if row in text:
            _value_unissued(row)


def validate_rendered(text: str) -> dict[str, str]:
    """Validate filled prose independently of the unfilled-scaffold linter."""

    if not isinstance(text, str) or not text.strip():
        raise RenderedValidationError("rendered output is empty")
    _refuse_appendix_derivations(text)
    seven = [key for key, heading in S7_HEADINGS.items() if text.count(heading) == 1]
    six = [key for key, heading in S6_HEADINGS.items() if text.count(heading) == 1]
    if len(seven) != 1 or len(six) != 1:
        raise RenderedValidationError(
            f"rendered output must contain exactly one §7 and one §6 variant; got {seven!r} and {six!r}"
        )
    if len(re.findall(r"^## §7 Variant", text, re.M)) != 1 or len(re.findall(r"^## §6 Variant", text, re.M)) != 1:
        raise RenderedValidationError("rendered output contains an unknown or duplicate variant heading")
    remaining = FILL_TOKEN_RE.findall(text)
    if remaining:
        raise RenderedValidationError(f"rendered output retains fill token(s): {sorted(set(remaining))}")
    forbidden = (
        "SELECTION GUARD",
        "VARIANT_PREDICATE",
        "CELL_BRANCH_SET",
        "END_CELL_BRANCH_SET",
        "**BRANCH ",
        "**GUARD:**",
        "**BINDS:**",
        "**TEXT:**",
        "PRESENT GUARD",
        "PRESENT TEXT",
        "ABSENT TEXT",
        "COMPANION GUARD",
        "COMPANION TEXT",
        "NO-COMPANION TEXT",
        "ROW_RENDER",
        "PRESENT_DIAGNOSTICS_RENDER",
        "STOP_FILL",
        "SUPPLIER_UNKNOWN",
        "If the predicate is false",
        "Choose this variant if and only if",
        "Select iff",
        "Select this branch",
    )
    found = [marker for marker in forbidden if marker in text]
    if found or "<!--" in text or "-->" in text:
        raise RenderedValidationError(f"rendered output retains authoring marker(s): {found!r}")
    section7_offset = text.index(S7_HEADINGS[seven[0]])
    section6_offset = text.index(S6_HEADINGS[six[0]])
    if section7_offset != 0 or section6_offset <= section7_offset:
        raise RenderedValidationError("§7 must be first and §6 must follow it")
    absolute_offset = 0
    for line_number, raw in enumerate(text.splitlines(keepends=True), 1):
        line = raw.strip()
        if not line:
            absolute_offset += len(raw)
            continue
        key = f"7:{seven[0]}" if absolute_offset < section6_offset else f"6:{six[0]}"
        if not any(pattern.fullmatch(line) for pattern in CANONICAL_RENDER_LINE_PATTERNS[key]):
            raise RenderedValidationError(
                f"line {line_number} is outside the canonical Results vocabulary: {line!r}"
            )
        absolute_offset += len(raw)
    return {"section7": seven[0], "section6": six[0]}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("input", nargs="?", type=Path, help="results-fill input manifest")
    group.add_argument(
        "--validate-rendered",
        type=Path,
        metavar="PATH",
        help="validate an already-rendered Markdown file without changing it",
    )
    args = parser.parse_args(argv)
    try:
        if args.validate_rendered is not None:
            text = args.validate_rendered.read_text(encoding="utf-8")
            selected = validate_rendered(text)
            print(
                "results prose rendered lint: PASS "
                f"(§7 {selected['section7']}; §6 {selected['section6']}; zero fill tokens)"
            )
        else:
            assert args.input is not None
            sys.stdout.write(render_from_manifest(args.input))
    except StopFill as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (OSError, UnicodeError, RenderedValidationError, RuntimeError) as exc:
        print(f"results prose rendered lint: REFUSED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
