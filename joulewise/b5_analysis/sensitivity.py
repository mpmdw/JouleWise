"""Restricted, non-issuing bracket sensitivity recomputation (J6).

Every consumer receives a fresh sensitivity context. The authenticated bracket,
primary projections, mint and verdicts retain their original authority and bytes.
Only ``to_structure_record`` may leave restricted custody before release.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, replace
import math
from pathlib import Path
from typing import Any, Callable, Mapping

from joulewise import analysis_engine as engine
from joulewise.authentication_io import read_authentication_input
from joulewise.floor_extraction import extract_cells
from joulewise.paper_reported_energy_issuer import project_pack
from joulewise.whole_window import (
    ArchiveContext, MAX_BRACKET_CONSUMPTION_SEMANTICS_ID, canonical_sha256,
)

from .archive import ArchiveHandle
from .bracket import BMax, WindowBracket, b_sens
from .kept_units import KeptUnits, _strict_json
from .windows import AnalysisRefusal, AnalysedWindow

SCHEMA = "joulewise.b5_bracket_sensitivity.v1"
_PACKS = ("alpha", "beta", "gamma")
_FLOOR_PACKS = _PACKS[:2]
_FLOOR_KEYS = ("floor_abs_j", "floor_cmp_j", "floor_gate_j")


def _invalid() -> None:
    raise AnalysisRefusal("sensitivity_inputs_invalid")


def _get(value, *keys):
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, IndexError, TypeError):
        _invalid()


def _number(value):
    try:
        if type(value) not in (int, float) or not math.isfinite(value):
            _invalid()
    except OverflowError:
        _invalid()
    return value


def _same(left, right) -> bool:
    # The issuer's canonical digest distinguishes signed zero and JSON number
    # representations, unlike Python numeric equality. No serializer is added.
    return canonical_sha256(left) == canonical_sha256(right)


def _at_primary_bound(equal_bound, primary, sensitivity):
    if equal_bound and not _same(primary, sensitivity):
        raise AnalysisRefusal("sensitivity_differs_at_primary_bound")


def _by_id(rows, key="cell_id"):
    if not isinstance(rows, (list, tuple)):
        _invalid()
    result = {}
    for row in rows:
        identifier = _get(row, key)
        if not isinstance(identifier, str) or not identifier or identifier in result:
            _invalid()
        result[identifier] = row
    return result


def _reported_values(cell):
    return {"mean_j": _number(_get(cell, "mean_j")),
            "h_j": _number(_get(cell, "interval", "h_j")),
            "B_j": _number(_get(cell, "interval", "B_j")),
            "lower_j": _number(_get(cell, "lower_j")),
            "upper_j": _number(_get(cell, "upper_j")),
            "attribution_floor_j": _number(_get(cell, "attribution_floor", "value_j"))}


def _projection_cells(projection, spec):
    computed = _by_id(_get(projection, "cells"))
    refused = _by_id(_get(projection, "refused_cells"))
    expected = list(_by_id(_get(spec, "reported_energy_cells")))
    if set(computed) & set(refused) or set(computed) | set(refused) != set(expected):
        _invalid()
    return computed, refused, expected


def _projection_parents(projection):
    names = ("selection_sha256", "prompt_pin_sha256", "whole_window_basis_sha256")
    bindings = [_get(cell, "binding") for cell in _get(projection, "cells")]
    if not bindings:
        _invalid()
    parents = {key: _get(bindings[0], key) for key in names}
    if any(not _same({key: _get(binding, key) for key in names}, parents)
           for binding in bindings):
        _invalid()
    return {"selection_sha256": parents["selection_sha256"],
            "prompt_pin_sha256": parents["prompt_pin_sha256"],
            "evaluation_basis_sha256": parents["whole_window_basis_sha256"]}


def _floor_sources(artifact, reports, specs, windows, evidence_roots):
    """Map by the mint's own component provenance, never by cell spelling."""
    roots = {str(Path(window.claim_runs_root).resolve()): pack for pack, window in windows.items()
             if pack in _FLOOR_PACKS}
    report_cells = {pack: _by_id(_get(reports[pack], "cells")) for pack in _FLOOR_PACKS}
    spec_orders = {pack: {cid: i for i, cid in enumerate(_by_id(_get(specs[pack], "cells")))}
                   for pack in _FLOOR_PACKS}
    result = []
    for cell_id, cell in _by_id(_get(artifact, "cells")).items():
        components = {}
        owners = []
        for kind in ("absolute", "comparative"):
            provenance = _get(cell, "provenance", kind)
            root_id = _get(provenance, "evidence_root_id")
            root = _get(evidence_roots, root_id)
            pack = roots.get(str(Path(root).resolve()))
            calibration_id = _get(provenance, "calibration_cell_id")
            if pack not in _FLOOR_PACKS or calibration_id not in report_cells[pack]:
                _invalid()
            if calibration_id not in spec_orders[pack] or _get(report_cells[pack][calibration_id], "kind") != kind:
                _invalid()
            owners.append(pack)
            components[kind] = calibration_id
        if owners[0] != owners[1]:
            _invalid()
        pack = owners[0]
        result.append((pack, cell_id, components,
                       min(spec_orders[pack][cid] for cid in components.values())))
    result.sort(key=lambda row: (_FLOOR_PACKS.index(row[0]), row[3]))
    return result


def _compose_floor(report, components):
    cells = _by_id(_get(report, "cells"))
    absolute = _get(cells, components["absolute"])
    comparative = _get(cells, components["comparative"])
    floor_abs = _number(_get(absolute, "floor", "drift_widened_guarded_floor_j"))
    floor_cmp = _number(_get(comparative, "floor", "drift_widened_guarded_floor_j"))
    allowance = _number(_get(absolute, "whole_window_drift_allowance", "allowance_j"))
    if not _same(allowance, _number(_get(comparative, "whole_window_drift_allowance", "allowance_j"))):
        raise AnalysisRefusal("sensitivity_changed_bound_independent_value")
    return {"floor_abs_j": floor_abs, "floor_cmp_j": floor_cmp,
            "floor_gate_j": max(floor_abs, floor_cmp), "allowance_j": allowance}


def _engine_contrasts(*, gamma_manifest_path, runs_root, floor_artifact_path,
                      kept_units, archive_contexts, gamma_archive, evidence_roots,
                      strict_validator, sensitivity_floors):
    """Production B4 composition; all statistical and decision math is the engine's."""
    inputs = engine.load_analysis_inputs(Path(gamma_manifest_path), Path(runs_root),
        Path(floor_artifact_path), mode="read_replay", strict_validator=strict_validator,
        evidence_roots=evidence_roots, kept_units=kept_units,
        archive_contexts=archive_contexts, gamma_archive=gamma_archive,
        neg8_harvest_archive=gamma_archive.window.archive_root)
    sentinels = engine._sentinel_entries_by_block(inputs.manifest)
    prepared = {contrast["contrast_id"]: engine._prepare_contrast(
        inputs, contrast, sentinels, None, None, evidence_class="current")
        for contrast in inputs.manifest["contrasts"]}
    _, adjusted = engine._family_adjustments(inputs.manifest, prepared)
    rows = []
    for contrast in inputs.manifest["contrasts"]:
        cid = contrast["contrast_id"]
        item = prepared[cid]
        resolutions = []
        for resolution in item["floor_resolutions"]:
            if not resolution.source_cell_ids:
                _invalid()
            values = [_get(sensitivity_floors, source_id) for source_id in resolution.source_cell_ids]
            resolutions.append(replace(resolution, **{
                key: max(_get(value, key) for value in values) for key in _FLOOR_KEYS}))
        floor = engine._combined_floor(resolutions)
        reasons = engine._analysis_reasons(item, item["estimate"], floor,
                                           resolutions, item["randomization_check"])
        evaluation = engine._evaluation(item, item["estimate"], adjusted[cid], reasons, floor=floor)
        rows.append(engine._contrast_row({**item, "floor": floor}, adjusted[cid], evaluation, [], "not_run"))
    return rows


@dataclass(frozen=True)
class SensitivityConsumers:
    """Tests may replace these callables; production uses these defaults."""
    project: Callable = project_pack
    extract: Callable = extract_cells
    contrasts: Callable = _engine_contrasts


_DEFAULT_CONSUMERS = SensitivityConsumers()


def _contrast_values(row):
    return {"floor_abs_j": _number(_get(row, "floor", "floor_abs_j")),
            "floor_cmp_j": _number(_get(row, "floor", "floor_cmp_j")),
            "floor_gate_j": _number(_get(row, "floor", "active_floor_j")),
            "D_j": _number(_get(row, "deterministic_bounds", "total")),
            "outcome": _get(row, "claim_evaluation", "outcome")}


def _independent_contrast_values(row):
    # The whole estimator carries dbar, s_d, every SE, both metrology and repeat
    # intervals, and raw p. Multiplicity adds adjusted p and rejection.
    return {"estimator": _get(row, "estimator"), "multiplicity": _get(row, "multiplicity")}


def sensitivity_pass(windows, kept_units, contexts, brackets, b_max, *,
                     extraction_specs, primary_projections, primary_extraction_reports,
                     floor_artifact, floor_artifact_path, gamma_manifest_path,
                     primary_claim_verdicts, evidence_roots, strict_validator,
                     gamma_archive, consumers=_DEFAULT_CONSUMERS) -> dict:
    """Recompute under each window's own b_sens; write no file and issue nothing.

    Primary outputs are parsed mappings, except ``primary_claim_verdicts`` may
    also be an authenticated-input path. ``gamma_archive`` reuses the caller's
    authenticated handle for the selected GAMMA window.
    """
    for mapping, kind in ((windows, AnalysedWindow), (kept_units, KeptUnits),
                          (contexts, ArchiveContext), (brackets, WindowBracket)):
        if not isinstance(mapping, Mapping) or set(mapping) != set(_PACKS):
            _invalid()
        if any(not isinstance(value, kind) for value in mapping.values()):
            _invalid()
    if not isinstance(gamma_archive, ArchiveHandle) or gamma_archive.window != windows["gamma"]:
        _invalid()
    for mapping in (extraction_specs, primary_projections, primary_extraction_reports):
        if not isinstance(mapping, Mapping) or set(mapping) != set(_FLOOR_PACKS):
            _invalid()
    if (not isinstance(b_max, BMax) or _number(b_max.value_s) < 0
            or type(b_max.T) is not int or b_max.T < 1
            or (b_max.attained_by_sequence is not None and
                (type(b_max.attained_by_sequence) is not int or
                 not 1 <= b_max.attained_by_sequence <= b_max.T))):
        _invalid()
    if not isinstance(evidence_roots, Mapping) or not callable(strict_validator):
        _invalid()
    if any(not callable(getattr(consumers, name, None)) for name in ("project", "extract", "contrasts")):
        _invalid()
    for pack in _PACKS:
        window, context, bracket = windows[pack], contexts[pack], brackets[pack]
        if (window.pack != pack or kept_units[pack].window != window or bracket.window != window
                or Path(context.neg8_harvest_archive).resolve() != Path(window.archive_root).resolve()
                or context.sensitivity_bound_s is not None
                or not _same(_get(context.window_bracket, "b_fiducial_s"), bracket.b_fiducial_s)):
            _invalid()
    specs, projections, reports, artifact = (deepcopy(value) for value in
        (extraction_specs, primary_projections, primary_extraction_reports, floor_artifact))
    if isinstance(primary_claim_verdicts, (str, Path)):
        verdicts = _strict_json(read_authentication_input(Path(primary_claim_verdicts),
            grammar="json", label="primary claim verdicts"), "sensitivity_inputs_invalid")
    else:
        verdicts = deepcopy(primary_claim_verdicts)
    if _get(verdicts, "schema_version") != "joulewise.claim_verdicts.v1":
        _invalid()
    primary_contrasts = _by_id(_get(verdicts, "contrasts"), "contrast_id")
    sources = _floor_sources(artifact, reports, specs, windows, evidence_roots)
    minted = _by_id(_get(artifact, "cells"))
    primary_floors = {}
    # This complete primary self-check precedes every sensitivity consumer.
    for pack, cid, components, _order in sources:
        primary_floors[cid] = _compose_floor(reports[pack], components)
        if not _same({key: primary_floors[cid][key] for key in _FLOOR_KEYS},
                     {key: _get(minted[cid], key) for key in _FLOOR_KEYS}):
            raise AnalysisRefusal("sensitivity_floor_composition_differs_from_mint")
    sens = {pack: replace(contexts[pack], sensitivity_bound_s=b_sens(brackets[pack], b_max))
            for pack in _PACKS}
    equal_bounds = {pack: sens[pack].sensitivity_bound_s == brackets[pack].b_fiducial_s for pack in _PACKS}
    record = {"schema_version": SCHEMA, "label": "sensitivity", "b_max": asdict(b_max),
        "windows": {pack: {"plan_id": windows[pack].plan_id,
                           "b_op_s": brackets[pack].b_fiducial_s,
                           "b_sens_s": sens[pack].sensitivity_bound_s,
                           "widened": sens[pack].sensitivity_bound_s > brackets[pack].b_fiducial_s}
                    for pack in _PACKS}, "reported_cells": [], "floor_cells": [], "contrasts": []}
    sensitivity_reports = {}
    for pack in _FLOOR_PACKS:
        primary, refused, order = _projection_cells(projections[pack], specs[pack])
        parents = _projection_parents(projections[pack])
        projection = consumers.project(deepcopy(specs[pack]), kept_units[pack], context=sens[pack],
            runs_root=windows[pack].claim_runs_root, strict_validator=strict_validator, **parents)
        computed, sensitivity_refused, _ = _projection_cells(projection, specs[pack])
        for cid in order:
            if cid in refused:
                if cid not in sensitivity_refused or _get(refused[cid], "code") != _get(sensitivity_refused[cid], "code"):
                    raise AnalysisRefusal("sensitivity_changed_bound_independent_value")
                record["reported_cells"].append({"pack": pack, "cell_id": cid, "status": "refused",
                                                  "code": _get(refused[cid], "code")})
                continue
            if cid not in computed:
                raise AnalysisRefusal("sensitivity_changed_bound_independent_value")
            before, after = _reported_values(primary[cid]), _reported_values(computed[cid])
            _at_primary_bound(equal_bounds[pack], before, after)
            if not _same([before["mean_j"], before["h_j"]], [after["mean_j"], after["h_j"]]):
                raise AnalysisRefusal("sensitivity_changed_bound_independent_value")
            record["reported_cells"].append({"pack": pack, "cell_id": cid, "status": "computed",
                "primary": before, "sensitivity": after, "mean_and_half_width_equal_primary": True,
                "equals_primary": _same(before, after),
                "not_below_primary": after["attribution_floor_j"] >= before["attribution_floor_j"]})
        sensitivity_reports[pack] = consumers.extract(windows[pack].claim_runs_root, deepcopy(specs[pack]),
            kept_units=kept_units[pack], archive_context=sens[pack],
            evaluation_basis_sha256=parents["evaluation_basis_sha256"],
            consumption_semantics_id=MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
            manifest_id=_get(reports[pack], "manifest_id"), mode="read_replay", hash_bundles=True,
            strict_validator=strict_validator)
    sensitivity_floors = {}
    for pack, cid, components, _order in sources:
        before = primary_floors[cid]
        after = _compose_floor(sensitivity_reports[pack], components)
        _at_primary_bound(equal_bounds[pack], before, after)
        if not _same(before["allowance_j"], after["allowance_j"]):
            raise AnalysisRefusal("sensitivity_changed_bound_independent_value")
        sensitivity_floors[cid] = after
        record["floor_cells"].append({"pack": pack, "cell_id": cid, "primary": before,
            "sensitivity": after, "equals_primary": _same(before, after),
            "not_below_primary": all(after[key] >= before[key] for key in _FLOOR_KEYS)})
    archive_contexts = {str(Path(windows[pack].claim_runs_root).resolve()):
                        sens[pack] if pack == "gamma" else contexts[pack] for pack in _PACKS}
    rows = consumers.contrasts(gamma_manifest_path=gamma_manifest_path,
        runs_root=windows["gamma"].claim_runs_root, floor_artifact_path=floor_artifact_path,
        kept_units=kept_units["gamma"], archive_contexts=archive_contexts, gamma_archive=gamma_archive,
        evidence_roots=dict(evidence_roots), strict_validator=strict_validator,
        sensitivity_floors=deepcopy(sensitivity_floors))
    computed_contrasts = _by_id(rows, "contrast_id")
    if set(computed_contrasts) != set(primary_contrasts):
        _invalid()
    for cid, row in computed_contrasts.items():
        before, after = _contrast_values(primary_contrasts[cid]), _contrast_values(row)
        independent_before = _independent_contrast_values(primary_contrasts[cid])
        independent_after = _independent_contrast_values(row)
        _at_primary_bound(all(equal_bounds.values()), [before, independent_before], [after, independent_after])
        if not _same(independent_before, independent_after):
            raise AnalysisRefusal("sensitivity_changed_bound_independent_value")
        source_ids = list(dict.fromkeys(source for resolution in _get(row, "floor", "resolutions")
                                      for source in _get(resolution, "source_cell_ids")))
        if any(source not in sensitivity_floors for source in source_ids):
            _invalid()
        record["contrasts"].append({"contrast_id": cid, "floor_cell_ids": source_ids,
            "primary": before, "sensitivity": after, "bound_independent_values_equal_primary": True,
            "outcome_equals_primary": after["outcome"] == before["outcome"],
            "not_below_primary": all(after[key] >= before[key] for key in (*_FLOOR_KEYS, "D_j"))})
    canonical_sha256(record)  # Validate against the issuer's canonical wire.
    return record


def to_structure_record(record) -> dict:
    """Only the schema, canonical digest and counts are safe before release."""
    if _get(record, "schema_version") != SCHEMA:
        _invalid()
    return {"schema_version": SCHEMA, "record_sha256": canonical_sha256(record),
            "counts": {key: len(_get(record, key))
                       for key in ("reported_cells", "floor_cells", "contrasts")}}
