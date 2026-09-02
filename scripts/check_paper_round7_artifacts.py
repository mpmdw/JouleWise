#!/usr/bin/env python3
"""Fence the round-7 diagnostic desk artifacts registered as DX rows.

The always-on half parses the DX registry subsection as the single source of
digest, field-path, rendering, and row-value truth.  It checks the five pinned
files, every supplier field, all artifact gates, every placed DX literal in the
successor skeleton, and all 118 Figure 4 marks.  Figure coordinates are printed
to 0.01 px; inverting the 326 px / 50 ms y scale therefore permits 0.0008 ms
(0.005 * 50 / 326, rounded upward).  The x tolerance is the analogous 0.00035
pulse index (0.005 * 58 / 844, rounded upward).

The default invocation additionally re-runs both producers into a directory
under TMPDIR and requires byte identity for XD, AQ, and the XS-produced F4.
An absent retained corpus exits 3 and names the missing path; it is never a
pass.  ``--literals-only`` runs only the always-on digest/field/literal half.

Exit codes: 0 for agreement, 2 for any mismatch, 3 for an absent corpus.
Successful full replay ends with ``R7F COMPARED n / MISMATCHES m``;
``--literals-only`` uses the distinct ``R7F LITERALS-ONLY COMPARED`` token.
An unavailable corpus instead ends with ``R7F CORPUS UNAVAILABLE: <path>``
and prints no ``COMPARED`` line.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
from typing import Any, Iterable
import xml.etree.ElementTree as ET


REGISTRY_RELATIVE_PATH = Path("docs/paper/results-fill-registry.md")
SKELETON_RELATIVE_PATH = Path("docs/paper/draft-v2-skeleton.md")
DX_HEADING = "#### Successor-draft desk analyses (round 7) — DX rows"
EXPECTED_SOURCE_PATHS = {
    "XD": Path("docs/paper/round7/excursion-decomposition.json"),
    "XS": Path("scripts/paper_excursion_decomposition.py"),
    "F4": Path("docs/paper/figures/fig4_edge_excursions.svg"),
    "AQ": Path("docs/paper/round7/anchor-correction-quantified.json"),
    "AS": Path("scripts/paper_anchor_correction_quantified.py"),
}
EXPECTED_R7F_PATH = Path("scripts/check_paper_round7_artifacts.py")
EXPECTED_DX_IDS = (
    "DX-001",
    "DX-002",
    "DX-003",
    "DX-010",
    "DX-011",
    "DX-012",
    "DX-013",
    "DX-014",
    "DX-015",
    "DX-016",
    "DX-017",
    "DX-020",
    "DX-021",
    "DX-022",
    "DX-023",
    "DX-024",
    "DX-025",
    "DX-026",
    "DX-027",
)
IDENTITY_ROWS = {"DX-001": "XD", "DX-002": "AQ", "DX-003": "F4"}
DERIVED_ROWS = {"DX-016", "DX-017"}
FREEZE_LABEL = (
    "DIAGNOSTIC_ERA / R7_FENCED; NOT RF-FENCED; NON_CLAIM_BEARING; "
    "SUCCESSOR_DRAFT_ONLY"
)
XD_CAMPAIGN = "retained 20260722 capture / 59-pulse calibration"
AQ_CAMPAIGN = "15 retained instrument_validation captures, v2 era"
Y_VALUE_TOLERANCE_MS = 0.0008
X_INDEX_TOLERANCE = 0.00035
F4_REPLAY_COMMAND = (
    "python3 scripts/paper_excursion_decomposition.py --corpus-root "
    "/Users/edr/code/JouleWise --out "
    "docs/paper/round7/excursion-decomposition.json --svg "
    "docs/paper/figures/fig4_edge_excursions.svg"
)

# The two calibration-gate predicates are producer integrity checks without a
# registry row of their own.  The worked-capture gate governs the AQ identity
# row.  Tests bind every governed entry back to the parsed registry.
GATE_SPECS: tuple[tuple[str, str, str | None], ...] = (
    ("XD", "calibration_gate.b_fiducial_s_matches_exactly", None),
    ("XD", "calibration_gate.projection_evaluated_cell_count_matches_exactly", None),
    ("AQ", "worked_capture_gate.matches_exactly", "DX-002"),
)

SOURCE_RE = re.compile(
    r"^- (?P<code>XD|XS|F4|AQ|AS) = (?P<path>[^,]+), sha256 "
    r"(?P<sha>[0-9a-f]{64})(?: \((?P<meta>[^)]+)\))?"
    r"(?:, schema (?P<schema>[^\s]+))?$",
    re.M,
)
FIELD_RE = re.compile(r"\b(?P<source>XD|AQ)#(?P<path>[A-Za-z0-9_.]+)")
RENDER_RE = re.compile(r"R7F_RENDER=(?P<rule>[a-z0-9_]+)")
FILL_RE = re.compile(r"\[FILL:(DX-[0-9]{3})\]")


class RegistryError(RuntimeError):
    """The registry cannot be interpreted without guessing."""


class ArtifactsUnavailable(RuntimeError):
    """The retained replay corpus is absent."""


@dataclass(frozen=True)
class SourcePin:
    code: str
    path: Path
    sha256: str
    size: int | None
    schema: str | None
    metadata: str | None


@dataclass(frozen=True)
class FieldRef:
    source: str
    path: str

    @property
    def label(self) -> str:
        return f"{self.source}#{self.path}"


@dataclass(frozen=True)
class DXRow:
    row_id: str
    site: str
    marker: str
    supplier: str
    campaign: str
    fill_rule: str
    freeze_status: str
    sources: str
    render_rule: str
    field_refs: tuple[FieldRef, ...]


@dataclass(frozen=True)
class RegistrySpec:
    sources: dict[str, SourcePin]
    r7f_path: Path
    rows: dict[str, DXRow]


@dataclass(frozen=True)
class Comparison:
    label: str
    expected: str
    observed: str
    match: bool


def _comparison(label: str, expected: Any, observed: Any) -> Comparison:
    return Comparison(label, str(expected), str(observed), expected == observed)


def _source_size(metadata: str | None) -> int | None:
    if metadata is None:
        return None
    match = re.fullmatch(r"([0-9,]+) B", metadata)
    return int(match.group(1).replace(",", "")) if match else None


def parse_registry_text(text: str) -> RegistrySpec:
    """Parse the one DX subsection and reject any malformed or missing row."""

    if text.count(DX_HEADING) != 1:
        raise RegistryError(
            f"expected exactly one {DX_HEADING!r} heading, found {text.count(DX_HEADING)}"
        )
    section = text.split(DX_HEADING, 1)[1]
    section = section.split("\n### ", 1)[0]

    source_matches = list(SOURCE_RE.finditer(section))
    sources: dict[str, SourcePin] = {}
    for match in source_matches:
        code = match.group("code")
        if code in sources:
            raise RegistryError(f"duplicate source definition {code}")
        pin = SourcePin(
            code=code,
            path=Path(match.group("path")),
            sha256=match.group("sha"),
            size=_source_size(match.group("meta")),
            schema=match.group("schema"),
            metadata=match.group("meta"),
        )
        sources[code] = pin
    if set(sources) != set(EXPECTED_SOURCE_PATHS):
        raise RegistryError(
            f"source set differs: expected {sorted(EXPECTED_SOURCE_PATHS)}, "
            f"found {sorted(sources)}"
        )
    for code, expected_path in EXPECTED_SOURCE_PATHS.items():
        if sources[code].path != expected_path:
            raise RegistryError(
                f"{code} path is {sources[code].path}, expected {expected_path}"
            )
    if sources["XD"].size is None or sources["AQ"].size is None:
        raise RegistryError("XD and AQ source definitions must pin byte sizes")
    if not sources["XD"].schema:
        raise RegistryError("XD source definition must pin its schema")
    if not sources["XS"].metadata or not sources["AS"].metadata:
        raise RegistryError("XS and AS source definitions must carry commit/PR metadata")

    r7f_matches = re.findall(r"^- R7F = ([^\n]+)$", section, re.M)
    if r7f_matches != [str(EXPECTED_R7F_PATH)]:
        raise RegistryError(
            f"R7F path definition is {r7f_matches!r}, expected {[str(EXPECTED_R7F_PATH)]!r}"
        )

    rows: dict[str, DXRow] = {}
    for line in section.splitlines():
        if not line.startswith("| DX-"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 7:
            raise RegistryError(f"DX row has {len(cells)} cells, expected 7: {line}")
        site, marker, supplier, campaign, fill_rule, freeze_status, row_sources = cells
        site_match = re.fullmatch(r"(DX-[0-9]{3}) — .+", site)
        if not site_match:
            raise RegistryError(f"malformed DX site cell {site!r}")
        row_id = site_match.group(1)
        if row_id in rows:
            raise RegistryError(f"duplicate DX row {row_id}")
        if row_id == "DX-003" and f"full replay is `{F4_REPLAY_COMMAND}`." not in supplier:
            raise RegistryError(
                "DX-003 must carry the exact full F4 replay command including --svg"
            )
        render_matches = RENDER_RE.findall(supplier)
        if len(render_matches) != 1:
            raise RegistryError(
                f"{row_id} must carry exactly one R7F_RENDER directive, found {render_matches}"
            )
        if row_id == "DX-027" and render_matches != ["signed_2_percent"]:
            raise RegistryError("DX-027 must use R7F_RENDER=signed_2_percent")
        field_refs = tuple(
            FieldRef(match.group("source"), match.group("path"))
            for match in FIELD_RE.finditer(supplier)
        )
        expected_fill = "DERIVE" if row_id in DERIVED_ROWS else "MEASURED"
        if fill_rule != expected_fill:
            raise RegistryError(
                f"{row_id} fill rule is {fill_rule!r}, expected {expected_fill!r}"
            )
        if freeze_status != FREEZE_LABEL:
            raise RegistryError(f"{row_id} has malformed freeze label {freeze_status!r}")
        if "[PENDING" in line:
            raise RegistryError(f"{row_id} illegally carries a PENDING marker")
        expected_campaign = AQ_CAMPAIGN if row_id >= "DX-020" or row_id == "DX-002" else XD_CAMPAIGN
        if campaign != expected_campaign:
            raise RegistryError(
                f"{row_id} campaign is {campaign!r}, expected {expected_campaign!r}"
            )
        if row_id not in IDENTITY_ROWS and not field_refs:
            raise RegistryError(f"{row_id} has no supplier field path")
        rows[row_id] = DXRow(
            row_id=row_id,
            site=site,
            marker=marker,
            supplier=supplier,
            campaign=campaign,
            fill_rule=fill_rule,
            freeze_status=freeze_status,
            sources=row_sources,
            render_rule=render_matches[0],
            field_refs=field_refs,
        )

    if tuple(rows) != EXPECTED_DX_IDS:
        raise RegistryError(
            f"DX row order/set differs: expected {EXPECTED_DX_IDS}, found {tuple(rows)}"
        )
    for row_id, source in IDENTITY_ROWS.items():
        if rows[row_id].marker != sources[source].sha256:
            raise RegistryError(
                f"{row_id} marker does not equal the {source} source-block digest"
            )
    return RegistrySpec(sources=sources, r7f_path=EXPECTED_R7F_PATH, rows=rows)


def parse_registry(path: Path) -> RegistrySpec:
    return parse_registry_text(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _byte_comparison(label: str, expected: bytes, observed: bytes) -> Comparison:
    expected_summary = f"sha256={hashlib.sha256(expected).hexdigest()} bytes={len(expected)}"
    observed_summary = f"sha256={hashlib.sha256(observed).hexdigest()} bytes={len(observed)}"
    return Comparison(label, expected_summary, observed_summary, expected == observed)


def check_file_pins(repository_root: Path, spec: RegistrySpec) -> list[Comparison]:
    comparisons: list[Comparison] = []
    for code, pin in spec.sources.items():
        path = repository_root / pin.path
        if not path.is_file():
            comparisons.append(_comparison(f"digest {code}", pin.sha256, f"MISSING {path}"))
            if pin.size is not None:
                comparisons.append(_comparison(f"size {code}", pin.size, f"MISSING {path}"))
            continue
        comparisons.append(_comparison(f"digest {code}", pin.sha256, _sha256(path)))
        if pin.size is not None:
            comparisons.append(_comparison(f"size {code}", pin.size, path.stat().st_size))
    r7f = repository_root / spec.r7f_path
    comparisons.append(_comparison("R7F path", True, r7f.is_file()))
    for row_id, code in IDENTITY_ROWS.items():
        path = repository_root / spec.sources[code].path
        observed = _sha256(path) if path.is_file() else f"MISSING {path}"
        comparisons.append(_comparison(f"identity {row_id}", spec.rows[row_id].marker, observed))
    return comparisons


def load_json_artifacts(
    repository_root: Path, spec: RegistrySpec
) -> tuple[dict[str, Any], list[Comparison]]:
    artifacts: dict[str, Any] = {}
    comparisons: list[Comparison] = []
    for code in ("XD", "AQ"):
        path = repository_root / spec.sources[code].path
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            comparisons.append(_comparison(f"JSON {code}", "valid JSON", f"{type(exc).__name__}: {exc}"))
        else:
            artifacts[code] = payload
            comparisons.append(_comparison(f"JSON {code}", "valid JSON", "valid JSON"))
    if "XD" in artifacts:
        comparisons.append(
            _comparison("XD schema", spec.sources["XD"].schema, artifacts["XD"].get("schema"))
        )
    return artifacts, comparisons


def resolve_field(payload: Any, path: str) -> Any:
    value = payload
    for component in path.split("."):
        if not isinstance(value, dict) or component not in value:
            raise KeyError(path)
        value = value[component]
    return value


def check_supplier_fields(
    spec: RegistrySpec, artifacts: dict[str, Any]
) -> list[Comparison]:
    comparisons: list[Comparison] = []
    for row in spec.rows.values():
        for field in row.field_refs:
            if field.source not in artifacts:
                comparisons.append(
                    _comparison(f"field {row.row_id} {field.label}", "resolves", "artifact unavailable")
                )
                continue
            try:
                resolve_field(artifacts[field.source], field.path)
            except KeyError:
                comparisons.append(
                    _comparison(f"field {row.row_id} {field.label}", "resolves", "MISSING")
                )
            else:
                comparisons.append(
                    _comparison(f"field {row.row_id} {field.label}", "resolves", "resolves")
                )
    return comparisons


def _decimal(value: Any) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"not a decimal scalar: {value!r}")
    return Decimal(str(value))


def _fixed(value: Any, places: int) -> str:
    return f"{_decimal(value):.{places}f}"


def _signed(value: Any, places: int) -> str:
    decimal = _decimal(value)
    sign = "−" if decimal < 0 else "+"
    return f"{sign}{abs(decimal):.{places}f}"


def _exact_int(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"not an exact integer: {value!r}")
    return value


def _exact_int_field(value: Any, field: str) -> int:
    try:
        return _exact_int(value)
    except ValueError as exc:
        raise ValueError(f"{field}: {exc}") from exc


def _row_values(row: DXRow, artifacts: dict[str, Any]) -> list[Any]:
    return [resolve_field(artifacts[ref.source], ref.path) for ref in row.field_refs]


def render_row(row: DXRow, spec: RegistrySpec, artifacts: dict[str, Any]) -> str:
    rule = row.render_rule
    values = _row_values(row, artifacts)
    if rule == "signed_1_ms" and len(values) == 1:
        return f"{_signed(values[0], 1)} ms"
    if rule in {"positive_count_of_count", "negative_count_of_count"} and len(values) == 2:
        first = _exact_int_field(values[0], row.field_refs[0].label)
        count = _exact_int_field(values[1], row.field_refs[1].label)
        return f"{first} of {count}"
    if rule == "fixed_1_ms" and len(values) == 1:
        return f"{_fixed(values[0], 1)} ms"
    if rule == "ratio_percent_1" and len(values) == 2:
        value = Decimal(100) * _decimal(values[0]) / _decimal(values[1])
        return f"{value:.1f} %"
    if rule == "difference_1_ms" and len(values) == 2:
        return f"{_decimal(values[0]) - _decimal(values[1]):.1f} ms"
    if rule == "integer" and len(values) == 1:
        return str(_exact_int_field(values[0], row.field_refs[0].label))
    if rule == "derived_refused_counts" and len(values) == 3:
        derived, refused, _ = values
        summary = artifacts["AQ"].get("summary")
        buckets = summary.get("v3_refusals_by_token") if isinstance(summary, dict) else None
        if not isinstance(buckets, dict) or set(buckets) != {"anchor_unresolved"}:
            raise ValueError(
                "AQ#summary.v3_refusals_by_token is not exclusively anchor_unresolved"
            )
        derived_i = _exact_int_field(derived, "AQ#summary.v3_derived_count")
        refused_i = _exact_int_field(refused, "AQ#summary.v3_refused_count")
        population = summary.get("population_size")
        population_i = _exact_int_field(population, "AQ#summary.population_size")
        if derived_i + refused_i != population_i:
            raise ValueError(
                "AQ#summary v3_derived_count + v3_refused_count does not equal population_size"
            )
        refusal_ids = buckets["anchor_unresolved"]
        if not isinstance(refusal_ids, list) or len(refusal_ids) != refused_i:
            raise ValueError("anchor_unresolved list does not match v3_refused_count")
        bucket_word = "both" if refused_i == 2 else "all"
        return (
            f"{derived_i} derived / {refused_i} refused "
            f"({bucket_word} anchor_unresolved)"
        )
    if rule == "flip_count_refused_by_v3" and len(values) == 2:
        count, flips = values
        count_i = _exact_int_field(count, "AQ#summary.admissibility_flip_count")
        if not isinstance(flips, list) or len(flips) != count_i:
            raise ValueError("admissibility_flips does not match admissibility_flip_count")
        if any(
            not isinstance(flip, dict) or flip.get("flip_direction") != "refused_by_v3"
            for flip in flips
        ):
            raise ValueError("not every admissibility flip is refused_by_v3")
        bucket_word = "both" if count_i == 2 else "all"
        return f"{count_i} ({bucket_word} refused_by_v3)"
    if rule == "control_count" and len(values) == 3:
        reproduced, population, failures = values
        reproduced_i = _exact_int_field(
            reproduced, "AQ#summary.control_v2_reproduces_stored_count"
        )
        population_i = _exact_int_field(population, "AQ#summary.population_size")
        if not isinstance(failures, list):
            raise ValueError("control reproduction failure count is unavailable: not a list")
        if len(failures) != 1:
            raise ValueError(
                f"control reproduction failure count is {len(failures)}, expected 1"
            )
        return f"{reproduced_i} of {population_i}; failure {failures[0]}"
    if rule == "signed_6_ms" and len(values) == 1:
        return f"{_signed(values[0], 6)} ms"
    if rule == "fixed_6_ms" and len(values) == 1:
        return f"{_fixed(values[0], 6)} ms"
    if rule == "fixed_2_percent" and len(values) == 1:
        return f"{_fixed(values[0], 2)} %"
    if rule == "signed_2_percent" and len(values) == 1:
        return f"{_signed(values[0], 2)} %"
    raise ValueError(f"unsupported or ill-shaped renderer {rule} with {len(values)} values")


def check_rendered_rows(
    spec: RegistrySpec, artifacts: dict[str, Any]
) -> list[Comparison]:
    comparisons: list[Comparison] = []
    for row in spec.rows.values():
        if row.row_id in IDENTITY_ROWS:
            continue
        try:
            rendered = render_row(row, spec, artifacts)
        except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
            comparisons.append(
                _comparison(f"row {row.row_id}", row.marker, f"REFUSED: {type(exc).__name__}: {exc}")
            )
        else:
            comparisons.append(_comparison(f"row {row.row_id}", row.marker, rendered))
    return comparisons


def check_gates(artifacts: dict[str, Any]) -> list[Comparison]:
    comparisons: list[Comparison] = []
    for source, path, _row_id in GATE_SPECS:
        try:
            value = resolve_field(artifacts[source], path)
        except (KeyError, TypeError):
            value = "MISSING"
        comparisons.append(_comparison(f"gate {source}#{path}", True, value))
    return comparisons


def _svg_shapes(root: ET.Element, fill: str, tag: str) -> list[ET.Element]:
    namespace = "{http://www.w3.org/2000/svg}"
    groups = [element for element in root.iter(f"{namespace}g") if element.get("fill") == fill]
    if len(groups) != 1:
        raise ValueError(f"expected one SVG group with fill {fill}, found {len(groups)}")
    return [child for child in groups[0] if child.tag == f"{namespace}{tag}"]


def check_figure(
    repository_root: Path, spec: RegistrySpec, artifacts: dict[str, Any]
) -> list[Comparison]:
    path = repository_root / spec.sources["F4"].path
    if "XD" not in artifacts:
        return [_comparison("figure data", "XD available", "XD unavailable")]
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8"))
        onset = _svg_shapes(root, "#2a78d6", "circle")
        offset = _svg_shapes(root, "#eb6834", "rect")
    except (OSError, UnicodeError, ET.ParseError, ValueError) as exc:
        return [_comparison("figure parse", "valid registered SVG", f"{type(exc).__name__}: {exc}")]

    comparisons = [
        _comparison("figure onset mark count", 59, len(onset)),
        _comparison("figure offset mark count", 59, len(offset)),
    ]
    pulses = artifacts["XD"].get("per_pulse")
    if not isinstance(pulses, list) or len(pulses) != 59:
        comparisons.append(_comparison("figure XD pulse count", 59, len(pulses) if isinstance(pulses, list) else "MISSING"))
        return comparisons

    series: tuple[tuple[str, list[ET.Element], str, str, str], ...] = (
        ("onset", onset, "cx", "cy", "onset_best_fit_lag_ms"),
        ("offset", offset, "x", "y", "offset_best_fit_lag_ms"),
    )
    for name, shapes, x_key, y_key, value_key in series:
        positioned: list[tuple[float, float]] = []
        for shape in shapes:
            try:
                if name == "onset":
                    x = float(shape.attrib[x_key])
                    y = float(shape.attrib[y_key])
                else:
                    x = float(shape.attrib[x_key]) + float(shape.attrib["width"]) / 2.0
                    y = float(shape.attrib[y_key]) + float(shape.attrib["height"]) / 2.0
            except (KeyError, ValueError):
                positioned.append((float("nan"), float("nan")))
            else:
                positioned.append((x, y))
        positioned.sort(key=lambda pair: pair[0])
        for index in range(59):
            if index >= len(positioned):
                comparisons.append(_comparison(f"figure {name} mark {index}", "present and matching", "MISSING"))
                continue
            x, y = positioned[index]
            recovered_index = (x - 118.0) * 58.0 / (962.0 - 118.0)
            recovered_value = (476.0 - y) * 50.0 / (476.0 - 150.0) - 20.0
            pulse = pulses[index]
            if not isinstance(pulse, dict) or value_key not in pulse:
                observed = (
                    f"REFUSED: per_pulse[{index}] is not a dict"
                    if not isinstance(pulse, dict)
                    else f"REFUSED: per_pulse[{index}] lacks {value_key}"
                )
                comparisons.append(
                    _comparison(
                        f"figure {name} mark {index}",
                        f"per_pulse dict with {value_key}",
                        observed,
                    )
                )
                continue
            expected_value = float(pulse[value_key])
            match = (
                abs(recovered_index - index) <= X_INDEX_TOLERANCE
                and abs(recovered_value - expected_value) <= Y_VALUE_TOLERANCE_MS
            )
            comparisons.append(
                Comparison(
                    f"figure {name} mark {index}",
                    f"index={index}, value={expected_value:.6f}",
                    f"index={recovered_index:.6f}, value={recovered_value:.6f}",
                    match,
                )
            )
    return comparisons


def check_skeleton_literals(text: str, spec: RegistrySpec) -> list[Comparison]:
    """Check canonical ``[FILL:DX-nnn] <literal>`` placements, if present."""

    comparisons: list[Comparison] = []
    for match in FILL_RE.finditer(text):
        row_id = match.group(1)
        if row_id not in spec.rows:
            comparisons.append(_comparison(f"literal {row_id}", "registered row", "UNREGISTERED"))
            continue
        if row_id in IDENTITY_ROWS:
            comparisons.append(_comparison(f"literal {row_id}", "no draft site", "identity row placed"))
            continue
        line_end = text.find("\n", match.end())
        suffix = text[match.end() : line_end if line_end >= 0 else len(text)]
        suffix = suffix.lstrip()
        if suffix.startswith("`"):
            end = suffix.find("`", 1)
            observed = suffix[1:end] if end >= 0 else suffix
        else:
            expected = spec.rows[row_id].marker
            continuation = suffix[len(expected) :] if suffix.startswith(expected) else ""
            next_character = continuation[:1]
            if (
                suffix.startswith(expected)
                and (
                    not next_character
                    or (
                        not next_character.isalnum()
                        and next_character not in ".%"
                    )
                )
            ):
                observed = expected
            else:
                observed = suffix
        comparisons.append(_comparison(f"literal {row_id}", spec.rows[row_id].marker, observed))
    return comparisons


def digest_half(
    repository_root: Path, registry_path: Path, skeleton_path: Path
) -> tuple[RegistrySpec | None, list[Comparison]]:
    try:
        spec = parse_registry(registry_path)
    except (OSError, UnicodeError, RegistryError) as exc:
        return None, [_comparison("registry", "valid fail-closed DX registry", f"{type(exc).__name__}: {exc}")]

    comparisons = check_file_pins(repository_root, spec)
    artifacts, json_comparisons = load_json_artifacts(repository_root, spec)
    comparisons.extend(json_comparisons)
    comparisons.extend(check_supplier_fields(spec, artifacts))
    comparisons.extend(check_rendered_rows(spec, artifacts))
    comparisons.extend(check_gates(artifacts))
    comparisons.extend(check_figure(repository_root, spec, artifacts))
    try:
        skeleton_text = skeleton_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        comparisons.append(_comparison("successor skeleton", "readable", f"{type(exc).__name__}: {exc}"))
    else:
        comparisons.extend(check_skeleton_literals(skeleton_text, spec))
    return spec, comparisons


def _required_corpus_paths(corpus_root: Path, repository_root: Path, spec: RegistrySpec) -> list[Path]:
    required = [
        corpus_root
        / "runs_window_a_20260722"
        / "instrument_validation"
        / "20260722T145535-e941c821"
        / "instrument_evidence.json",
        corpus_root
        / "runs_window_a_20260722"
        / "instrument_validation"
        / "20260722T145535-e941c821"
        / "raw"
        / "powermetrics.plist",
        corpus_root / "runs" / "instrument_validation",
    ]
    try:
        aq = json.loads((repository_root / spec.sources["AQ"].path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return required
    captures = aq.get("captures", [])
    if isinstance(captures, list):
        for capture in captures:
            if isinstance(capture, dict) and isinstance(capture.get("validation_id"), str):
                required.append(
                    corpus_root
                    / "runs"
                    / "instrument_validation"
                    / capture["validation_id"]
                    / "instrument_evidence.json"
                )
    return required


def _run_producer(command: list[str], repository_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=repository_root,
        text=True,
        capture_output=True,
        check=False,
    )


def _producer_failure(label: str, completed: subprocess.CompletedProcess[str]) -> Comparison:
    output = (completed.stdout + completed.stderr).strip().splitlines()
    tail = " | ".join(output[-4:]) if output else "no output"
    return _comparison(f"replay {label} exit", 0, f"{completed.returncode}: {tail}")


def _replace_command_value(command: list[str], flag: str, value: Path) -> None:
    if command.count(flag) != 1:
        raise ValueError(f"pinned F4 command must contain exactly one {flag}")
    index = command.index(flag)
    if index + 1 >= len(command) or command[index + 1].startswith("--"):
        raise ValueError(f"pinned F4 command has no value for {flag}")
    command[index + 1] = str(value)


def _f4_replay_argv(
    repository_root: Path, corpus_root: Path, xd_out: Path, f4_out: Path
) -> list[str]:
    """Materialize the actual XS replay argv from the registry-pinned command."""

    command = shlex.split(F4_REPLAY_COMMAND)
    if len(command) < 2 or command[0] != "python3":
        raise ValueError("pinned F4 command must start with python3 and the XS path")
    expected_script = str(EXPECTED_SOURCE_PATHS["XS"])
    if command[1] != expected_script:
        raise ValueError(
            f"pinned F4 command script is {command[1]!r}, expected {expected_script!r}"
        )
    command[0] = sys.executable
    command[1] = str(repository_root / expected_script)
    _replace_command_value(command, "--corpus-root", corpus_root)
    _replace_command_value(command, "--out", xd_out)
    _replace_command_value(command, "--svg", f4_out)
    return command


def replay_half(
    repository_root: Path, corpus_root: Path, spec: RegistrySpec
) -> list[Comparison]:
    for path in _required_corpus_paths(corpus_root, repository_root, spec):
        if not path.exists():
            raise ArtifactsUnavailable(str(path))

    tmp_parent = Path(os.environ.get("TMPDIR", tempfile.gettempdir()))
    tmp_parent.mkdir(parents=True, exist_ok=True)
    comparisons: list[Comparison] = []
    with tempfile.TemporaryDirectory(prefix="joulewise-r7f-", dir=tmp_parent) as directory:
        temp = Path(directory)
        xd_out = temp / "excursion-decomposition.json"
        f4_out = temp / "fig4_edge_excursions.svg"
        aq_out = temp / "anchor-correction-quantified.json"

        try:
            xs_command = _f4_replay_argv(
                repository_root, corpus_root, xd_out, f4_out
            )
        except ValueError as exc:
            comparisons.append(_comparison("replay F4 command", "valid pinned argv", str(exc)))
            return comparisons
        xs = _run_producer(xs_command, repository_root)
        if xs.returncode != 0:
            if xs.returncode == 3:
                raise ArtifactsUnavailable((xs.stdout + xs.stderr).strip() or str(corpus_root))
            comparisons.append(_producer_failure("XS", xs))
            return comparisons

        for code, output_path in (("XD", xd_out), ("F4", f4_out)):
            committed = repository_root / spec.sources[code].path
            comparisons.append(
                _byte_comparison(
                    f"replay {code} bytes", committed.read_bytes(), output_path.read_bytes()
                )
            )

        anchor = _run_producer(
            [
                sys.executable,
                str(repository_root / spec.sources["AS"].path),
                "--repository-root",
                str(repository_root),
                "--corpus-root",
                str(corpus_root),
                "--out",
                str(aq_out),
            ],
            repository_root,
        )
        if anchor.returncode != 0:
            if anchor.returncode == 3:
                raise ArtifactsUnavailable((anchor.stdout + anchor.stderr).strip() or str(corpus_root))
            comparisons.append(_producer_failure("AS", anchor))
            return comparisons
        committed_aq = repository_root / spec.sources["AQ"].path
        comparisons.append(
            _byte_comparison("replay AQ bytes", committed_aq.read_bytes(), aq_out.read_bytes())
        )
    return comparisons


def _print_comparisons(comparisons: Iterable[Comparison]) -> None:
    for comparison in comparisons:
        if comparison.match:
            print(f"ok   {comparison.label}")
        else:
            print(
                f"MISMATCH {comparison.label}: expected {comparison.expected!r}, "
                f"observed {comparison.observed!r}"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="checkout containing the registry and committed artifacts",
    )
    parser.add_argument(
        "--corpus-root",
        type=Path,
        default=None,
        help="root containing both retained diagnostic corpus trees (default: repository root)",
    )
    parser.add_argument("--registry", type=Path, default=None, help="alternate registry for audit tests")
    parser.add_argument("--skeleton", type=Path, default=None, help="alternate successor skeleton")
    parser.add_argument(
        "--literals-only",
        action="store_true",
        help="run the always-on digest/field/figure/literal half without corpus replay",
    )
    args = parser.parse_args(argv)

    repository_root = args.repository_root.resolve()
    corpus_root = (args.corpus_root or repository_root).resolve()
    registry_path = args.registry or repository_root / REGISTRY_RELATIVE_PATH
    skeleton_path = args.skeleton or repository_root / SKELETON_RELATIVE_PATH
    spec, comparisons = digest_half(repository_root, registry_path, skeleton_path)
    if any(not comparison.match for comparison in comparisons) or spec is None:
        _print_comparisons(comparisons)
        mismatches = sum(not comparison.match for comparison in comparisons)
        token = "R7F LITERALS-ONLY COMPARED" if args.literals_only else "R7F COMPARED"
        print(f"{token} {len(comparisons)} / MISMATCHES {mismatches}")
        return 2

    if not args.literals_only:
        try:
            comparisons.extend(replay_half(repository_root, corpus_root, spec))
        except ArtifactsUnavailable as exc:
            _print_comparisons(comparisons)
            print(f"R7F CORPUS UNAVAILABLE: {exc}")
            return 3

    _print_comparisons(comparisons)
    mismatches = sum(not comparison.match for comparison in comparisons)
    token = "R7F LITERALS-ONLY COMPARED" if args.literals_only else "R7F COMPARED"
    print(f"{token} {len(comparisons)} / MISMATCHES {mismatches}")
    return 0 if mismatches == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
