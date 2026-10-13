"""S6 kept-unit mint arithmetic and refusals; synthetic inputs only.

The historical mint fixture and each derived arithmetic case are cached once.
No fixture builder runs per test. Production arithmetic and validators run intact.
"""
import atexit
import contextlib
import copy
from dataclasses import replace
import hashlib
import io
import inspect
import json
import math
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import detection_floor as df, floor_extraction as fe, floor_mint_estimator as estimator, whole_window as ww
from joulewise.authentication_io import V2AuthenticationReadSession
from joulewise.b5_analysis.windows import AnalysisRefusal, SealPins
from joulewise.b5_analysis.bracket import WindowBracket
from scripts import mint_floor_artifact as core, mint_floor_artifact_generalized as mint, emit_floor_mint_pinset as emit
from tests import test_mint_floor_artifact_generalized as old
from tests.test_emit_floor_mint_pinset import contracts_from_pins
from tests.b5_analysis.test_floor_kept_units import units_for, indexed_fixture, ABS, DELTAS
from tests.b5_analysis import fixtures as fx, fixtures_s2 as s2

_CACHE = {}


def base():
    if "base" not in _CACHE:
        _CACHE["base"] = old.synthetic_v2_fixture()
    return copy.deepcopy(_CACHE["base"])


@contextlib.contextmanager
def registered(entries):
    previous = dict(mint.BLOCK5_PRODUCERS)
    previous_core = core.BLOCK5_PRODUCERS
    mint.BLOCK5_PRODUCERS.clear()
    mint.BLOCK5_PRODUCERS.update(entries)
    core.BLOCK5_PRODUCERS = mint.BLOCK5_PRODUCERS
    try:
        yield
    finally:
        mint.BLOCK5_PRODUCERS.clear()
        mint.BLOCK5_PRODUCERS.update(previous)
        core.BLOCK5_PRODUCERS = previous_core


def synthetic_bracket(window, evaluation):
    return WindowBracket(window, "synthetic", evaluation, evaluation["b_fiducial_s"], 0, "0"*64, "synthetic", "0"*64)


def case(name="t1", *, minimum=5, target=True):
    key = name, minimum, target
    if key in _CACHE:
        return _CACHE[key]
    pins, inputs, ledger = base()
    removed_a = (5,) if name == "abs9" else range(5, 10) if name == "t3" else range(4, 10) if name == "n4" else ()
    removed_b = (4, 8) if name == "t1" else range(5, 10) if name == "t2" else ()
    entries, snapshots = {}, {}
    for producer in pins["producer_plans"]:
        pid = producer["plan"]["plan_id"]
        source = inputs[pid]
        all_cells = [copy.deepcopy(component.spec_cell) for cell in source.cells.values()
                     for component in (cell.absolute, cell.comparative)]
        spec = {**copy.deepcopy(source.cells["decode"].absolute.spec), "cells": all_cells}
        removed = {all_cells[0]["members"][i]["bundle_id"] for i in removed_a}
        removed.update(all_cells[1]["blocks"][i]["block_id"] for i in removed_b)
        window = SimpleNamespace(harvest_pin="a"*40, pack="alpha" if pid.endswith("0") else "beta",
                                 plan_id="v5-b5-" + ("alpha" if pid.endswith("0") else "beta") + "-a1-test", claim_runs_root=source.evidence_root)
        kept = units_for(spec, removed=removed, minimum=minimum, target=target, window=window)
        bracket = copy.deepcopy(source.cells["decode"].absolute.whole_window_calibration_bracket)
        bracket.update(b_fiducial_s=0.04 if pid.endswith("0") else 0.05,
                       calibration_drift_allowance_s=float(source.calibration_allowance_projection["applied_allowance_s"]))
        context = ww.ArchiveContext(source.evidence_root, window_bracket=bracket)
        snapshot = copy.deepcopy(ledger)
        snapshot.head_digest = source.authenticated_post_observation.receipt_digest
        snapshot.head_sequence = source.authenticated_post_observation.sequence
        snapshots[pid] = snapshot
        entry = SimpleNamespace(window=window, kept_units=kept, archive_context=context,
                                ledger_snapshot=snapshot, verdict_row={}, producer_plan_id=pid)
        entries[str(source.evidence_root.resolve())] = entry
        bindings, _ids = core._kept_spec_bindings(spec, entry)
        converted, report_cells = {}, []
        for role, cell_inputs in source.cells.items():
            pair = []
            for component in (cell_inputs.absolute, cell_inputs.comparative):
                spec_cell = next(cell for cell in all_cells if cell["cell_id"] == component.calibration_cell_id)
                binding = bindings[component.calibration_cell_id]
                removed_ids = set(binding["removed_unit_ids"])
                members, rows, widths = [], [], []
                if component.kind == "absolute":
                    layout = [(m["bundle_id"], [(m["bundle_id"], None, value, 0.05)])
                              for m, value in zip(spec_cell["members"], ABS, strict=True)]
                else:
                    layout = [(b["block_id"], [(b["members"][p], p, value, width) for p, value, width in
                               (("A1", 0.0, 0.0), ("B1", 2.0, 0.3), ("B2", -2.0, 0.3), ("A2", -2*d, 0.0))])
                              for b, d in zip(spec_cell["blocks"], DELTAS, strict=True)]
                original = {m.bundle_id: m for m in component.members}
                for uid, unit in layout:
                    for bid, position, value, width in unit:
                        if uid in removed_ids:
                            rows.append(fe._unevaluated_member(slot=bid, bundle_id=bid,
                                block_id=uid if position else None, position=position).as_row())
                        else:
                            members.append(replace(original[bid], metric_value_j=value, admissible_half_width_j=width))
                            rows.append({**component.cell["members"][0], "slot": bid, "bundle_id": bid,
                                "block_id": uid if position else None, "position": position, "metric_value_j": value,
                                "anchor_shift_bound_j": width, "bundle_sha256": original[bid].bundle_sha256,
                                "config_sha256": original[bid].config_sha256, "excluded": False, "reasons": [],
                                "consumption_provenance": {"operative_fiducial_bound_s": bracket["b_fiducial_s"]}})
                    if uid not in removed_ids:
                        widths.append(0.05 if component.kind == "absolute" else 0.3)
                allowance = {**component.whole_window_drift_allowance, "allowance_j": 0.8,
                             "observed_trajectory_excursion_j": 0.8, "derived_repeatability_bound_j": 0.79}
                updated = replace(component, spec=spec, spec_cell=spec_cell, members=tuple(members), widths_j=tuple(widths),
                                  whole_window_drift_allowance=allowance, whole_window_calibration_bracket=bracket)
                if component.kind == "absolute":
                    estimate = df.absolute_false_effect_floor([m.metric_value_j for m in members], admissible_half_widths_j=widths)
                else:
                    estimate = df.comparative_false_effect_floor([d for i, d in enumerate(DELTAS) if i not in removed_b],
                                                                admissible_half_widths_j=widths)
                row = old._production_report_cell(updated, estimate=estimate)
                row.update(members=rows, n_planned=10, n_admitted=len(widths), excluded_slots=sorted(removed_ids))
                updated = replace(updated, cell=row)
                report_cells.append(row)
                pair.append(updated)
            converted[role] = replace(cell_inputs, absolute=pair[0], comparative=pair[1])
        report = copy.deepcopy(source.cells["decode"].absolute.report)
        report.update(cells=report_cells, kept_units_binding={"schema_version": "joulewise.floor_extraction_kept_units.v1",
            "exclusions_sha256": kept.exclusions_sha256, "catalog_sha256": kept.catalog_sha256,
            "harvest_pin": kept.window.harvest_pin, "sensitivity_label": None, "cells": bindings})
        digest = hashlib.sha256(mint._artifact_payload(report)).hexdigest()
        for role, cell_inputs in converted.items():
            converted[role] = replace(cell_inputs,
                absolute=replace(cell_inputs.absolute, report=report, report_sha256=digest),
                comparative=replace(cell_inputs.comparative, report=report, report_sha256=digest))
        source = replace(source, cells=converted)
        inputs[pid] = source
        for cell_pin in producer["cells"]:
            selected = converted[cell_pin["role"]]
            for kind in ("absolute", "comparative"):
                cell_pin[kind] = emit._component_pins(getattr(selected, kind))
            cell_pin["postcollection"] = emit._postcollection(
                {**selected.absolute.cell, **cell_pin["absolute"]}, {**selected.comparative.cell, **cell_pin["comparative"]},
                source.bracket_binding, source.bracket_binding_sha256, digest, snapshot, source.calibration_allowance_projection)
    old._repair_v2_pinset_self_hashes(pins)
    result = SimpleNamespace(pins=pins, inputs=inputs, entries=entries, snapshots=snapshots)
    _CACHE[key] = result
    return result


def build(fixture, *, indexed=True):
    with tempfile.TemporaryDirectory(prefix="s6-build-") as tmp:
        path = Path(tmp) / "floor-mint-pinset.json"
        raw = mint._artifact_payload(fixture.pins)
        path.write_bytes(raw)
        with registered(fixture.entries if indexed else {}):
            artifact, components = mint._build_v2_artifacts(pinset=mint._parse_v2_pinset(fixture.pins), pinset_path=path,
                pinset_sha256=hashlib.sha256(raw).hexdigest(), producer_inputs=fixture.inputs,
                calibration_ledger_snapshot=fixture.snapshots, project_commit="0"*40, project_tree_state="clean")
        return artifact, components


class ArithmeticTests(unittest.TestCase):
    def test_t1_eight_quads_ten_repeats(self):
        fixture = case()
        artifact, _ = build(fixture)
        for cell in artifact["cells"]:
            self.assertEqual(cell["comparative"]["n_blocks"], 8)
            self.assertEqual(cell["comparative"]["guard_factor"], 1.1338934190276817)
            self.assertEqual(cell["comparative"]["unguarded_floor_j"], 1.0895584748159575)
            self.assertEqual(cell["comparative"]["t_critical"], 2.365)
            self.assertEqual(cell["comparative"]["guarded_floor_j"], 1.2354431842396523)
            self.assertEqual(cell["absolute"]["unguarded_floor_j"], 0.5729903925896154)
            self.assertEqual(cell["absolute"]["guard_factor"], 1.0)
            self.assertEqual(cell["absolute"]["t_critical"], 2.262)
            self.assertEqual(cell["floor_cmp_j"], 2.0354431842396523)
            self.assertEqual(cell["floor_abs_j"], 1.3729903925896154)
            self.assertEqual(cell["floor_gate_j"], 2.0354431842396523)
            self.assertEqual(cell["eligibility"]["minimum_claim_n"], 5)
        for producer in fixture.pins["producer_plans"]:
            for cell in producer["cells"]:
                self.assertEqual((cell["absolute"]["expected_n"], len(cell["absolute"]["members"])), (10, 10))
                self.assertEqual((cell["comparative"]["expected_n"], len(cell["comparative"]["members"])), (8, 32))

    def test_t2_ten_over_five(self):
        artifact, _ = build(case("t2"))
        for cell in artifact["cells"]:
            self.assertEqual(cell["floor_gate_j"], 2.899596205228953)
            self.assertEqual(cell["comparative"]["unguarded_floor_j"], 1.3997308034859683)
            self.assertEqual(cell["comparative"]["guard_factor"], 1.5)
            self.assertEqual(cell["comparative"]["guarded_floor_j"], 2.0995962052289525)
            self.assertEqual(cell["comparative"]["t_critical"], 2.776)
            self.assertEqual(cell["eligibility"]["minimum_claim_n"], 5)

    def test_t3_five_over_ten(self):
        artifact, _ = build(case("t3"))
        for cell in artifact["cells"]:
            self.assertEqual(cell["floor_abs_j"], 1.5495200000000016)
            self.assertEqual(cell["absolute"]["unguarded_floor_j"], 0.49968000000000096)
            self.assertEqual(cell["absolute"]["guard_factor"], 1.5)
            self.assertEqual(cell["absolute"]["guarded_floor_j"], 0.7495200000000014)
            self.assertEqual(cell["absolute"]["t_critical"], 2.776)
            self.assertEqual(cell["comparative"]["unguarded_floor_j"], 1.0348999613670127)
            self.assertEqual(cell["comparative"]["guard_factor"], 1.0)
            self.assertEqual(cell["comparative"]["t_critical"], 2.262)
            self.assertEqual(cell["floor_cmp_j"], 1.8348999613670127)
            self.assertEqual(cell["floor_gate_j"], 1.8348999613670127)
            self.assertEqual(cell["eligibility"]["minimum_claim_n"], 5)

    def test_nine_repeats_worked_value(self):
        artifact, _ = build(case("abs9"))
        for cell in artifact["cells"]:
            self.assertEqual(cell["absolute"]["n"], 9)
            self.assertEqual(cell["absolute"]["t_critical"], 2.306)
            self.assertEqual(cell["absolute"]["unguarded_floor_j"], 0.5435294124720607)
            self.assertEqual(cell["absolute"]["guard_factor"], 1.0606601717798212)
            self.assertEqual(cell["absolute"]["guarded_floor_j"], 0.5765000000000011)
            self.assertEqual(cell["floor_abs_j"], 1.3765000000000012)

    def test_t4_all_kept_canonical_cell_parity(self):
        fixture = case("all")
        indexed, _ = build(fixture)
        legacy, _ = build(fixture, indexed=False)
        for actual, expected in zip(indexed["cells"], legacy["cells"], strict=True):
            self.assertEqual(actual["eligibility"]["minimum_claim_n"], 5)
            self.assertEqual(expected["eligibility"]["minimum_claim_n"], 10)
            expected["eligibility"]["minimum_claim_n"] = 5
            self.assertEqual(mint._artifact_payload(actual), mint._artifact_payload(expected))

    def test_t6_emitted_sibling_pinset_and_r15_repository_fallback(self):
        fixture = case()
        with tempfile.TemporaryDirectory(prefix="s6-sibling-") as tmp, registered(fixture.entries):
            path = Path(tmp) / "floor-mint-pinset.json"
            pins = emit.build_pinset(contracts=contracts_from_pins(fixture.pins), producer_inputs=fixture.inputs,
                ledger_snapshot=fixture.snapshots, relative_plan_paths=[p["plan"]["relative_path"] for p in fixture.pins["producer_plans"]],
                pinset_path=path, project_commit="0"*40,
                kept_units={e.producer_plan_id: e.kept_units for e in fixture.entries.values()},
                window_brackets={e.producer_plan_id: e.archive_context.window_bracket for e in fixture.entries.values()})
            raw = mint._artifact_payload(pins)
            path.write_bytes(raw)
            digest = hashlib.sha256(raw).hexdigest()
            parsed = mint._parse_v2_pinset(pins)
            artifact, _ = mint._build_v2_artifacts(pinset=parsed, pinset_path=path, pinset_sha256=digest,
                producer_inputs=fixture.inputs, calibration_ledger_snapshot=fixture.snapshots,
                project_commit="0"*40, project_tree_state="clean")
            self.assertEqual(df.validate_floor_artifact(artifact, pinset_path=path, expected_pinset_sha256=digest), [])
            self.assertIsNotNone(df._project_floor_mint_pinset_v2(pins))
            self.assertTrue(any("pinset" in error for error in df.validate_floor_artifact(artifact)))

    def test_t7_schema_acceptance_enums(self):
        value = json.loads((core.REPO_ROOT / "scripts/floor_mint_pinsets/schema_v2.json").read_bytes())
        props = value["$defs"]["finalPostcollection"]["properties"]
        self.assertIn("max(observed_drift_s,0.014531)", props["allowance_rule"]["enum"])
        self.assertIn("0.014531", props["bracket_screen_s"]["enum"])
        for branch in value["$defs"]["finalProducer"]["allOf"]:
            post = branch.get("then", {}).get("properties", {}).get("cells", {}).get("items", {}).get("properties", {}).get("postcollection", {}).get("properties", {})
            for key in ("allowance_rule", "bracket_screen_s"):
                if key in post:
                    self.assertIn(post[key]["const"], props[key]["enum"])


class MembershipTests(unittest.TestCase):
    def component(self):
        fixture = case()
        source = next(iter(fixture.inputs.values()))
        return fixture, source.cells["decode"].comparative

    def test_r1_removed_member_pinned(self):
        fixture, component = self.component()
        row = copy.deepcopy(component.cell)
        removed = next(m for m in row["members"] if m["excluded"])
        removed.update(excluded=False, metric_value_j=1.0, anchor_shift_bound_j=0.0)
        with self.assertRaisesRegex(core.MintError, "^floor_mint_kept_unit_mismatch"):
            core._report_members(row, component.spec_cell, "comparative", frozenset(component.report["kept_units_binding"]["cells"][component.calibration_cell_id]["removed_unit_ids"]))

    def test_r2_kept_missing_and_binding_hidden(self):
        fixture, component = self.component()
        entry = fixture.entries[str(Path(component.report["runs_root"]).resolve())]
        row = copy.deepcopy(component.cell)
        row["members"] = row["members"][4:]
        removed = frozenset(component.report["kept_units_binding"]["cells"][component.calibration_cell_id]["removed_unit_ids"])
        with self.assertRaisesRegex(core.MintError, "^floor_mint_kept_unit_mismatch"):
            core._report_members(row, component.spec_cell, "comparative", removed)
        report = copy.deepcopy(component.report)
        report["kept_units_binding"]["cells"][component.calibration_cell_id]["kept_unit_ids"].pop(0)
        with self.assertRaisesRegex(core.MintError, "^floor_mint_kept_unit_mismatch"):
            core._authenticate_kept_binding(report, component.spec, entry)

        absolute = next(iter(fixture.inputs.values())).cells["decode"].absolute
        absolute_row = copy.deepcopy(absolute.cell)
        absolute_row["members"].pop(0)
        with self.assertRaisesRegex(core.MintError, "^floor_mint_kept_unit_mismatch"):
            core._report_members(absolute_row, absolute.spec_cell, "absolute", frozenset())

    def test_r3_unregistered_exclusion(self):
        _fixture, component = self.component()
        row = copy.deepcopy(component.cell)
        row["members"][0]["excluded"] = True
        removed = frozenset(component.report["kept_units_binding"]["cells"][component.calibration_cell_id]["removed_unit_ids"])
        with self.assertRaisesRegex(core.MintError, "^floor_mint_kept_unit_mismatch"):
            core._report_members(row, component.spec_cell, "comparative", removed)

    def test_r4_partial_quad_core_and_layout(self):
        fixture, component = self.component()
        row = copy.deepcopy(component.cell)
        row["members"][0]["excluded"] = True
        removed = frozenset(component.report["kept_units_binding"]["cells"][component.calibration_cell_id]["removed_unit_ids"])
        with self.assertRaisesRegex(core.MintError, "^floor_mint_kept_unit_mismatch"):
            core._report_members(row, component.spec_cell, "comparative", removed)
        with registered(fixture.entries), self.assertRaisesRegex(estimator._MintEstimatorError, "^floor_mint_kept_unit_mismatch"):
            estimator._comparative_layout(replace(component, members=component.members[1:]), core)

    def test_r5_n4_validator_both_minima(self):
        fixture = case("all")
        producer = fixture.pins["producer_plans"][0]
        source = fixture.inputs[producer["plan"]["plan_id"]]
        pair = source.cells["decode"]
        with tempfile.TemporaryDirectory(prefix="s6-n4-") as tmp, registered(fixture.entries):
            path = Path(tmp) / "floor-mint-pinset.json"
            raw = mint._artifact_payload(fixture.pins)
            path.write_bytes(raw)
            testing_core = mint._configured_core(mint._v2_mint_pinset(producer, producer["cells"][0]),
                pinset_path=path, expected_pinset_sha256=hashlib.sha256(raw).hexdigest())
            recomputation = mint._v2_gate_postcollection(producer=producer, cell_pins=producer["cells"][0],
                cell_inputs=pair, producer_inputs=source, ledger_snapshot=fixture.snapshots[producer["plan"]["plan_id"]])
            for minimum, message in ((4, "minimum_claim_n must be an integer >= 5"),
                                     (5, "claim_ready absolute n is below minimum_claim_n")):
                absolute = replace(pair.absolute, members=pair.absolute.members[:4], widths_j=pair.absolute.widths_j[:4],
                                   report=copy.deepcopy(pair.absolute.report))
                for component in (absolute, pair.comparative):
                    absolute.report["kept_units_binding"]["cells"][component.calibration_cell_id]["minimum"] = minimum
                comparative = replace(pair.comparative, report=absolute.report)
                with self.subTest(minimum=minimum), self.assertRaisesRegex(mint.MintError,
                        "constructed v2 cell artifact is invalid:.*" + message):
                    mint._mint_v2_cell_artifact(core=testing_core, producer=producer, cell_pins=producer["cells"][0], plan=source.plan,
                        project_commit="0"*40, project_tree_state="clean", origin_main_contains_head=False,
                        head_pin_commit_contained_in_origin_main=False, absolute=absolute, comparative=comparative,
                        recomputation=recomputation, calibration_ledger_snapshot=fixture.snapshots[producer["plan"]["plan_id"]])

    def test_r6_binding_digest_and_sensitive_view(self):
        fixture, component = self.component()
        entry = next(iter(fixture.entries.values()))
        for field in ("exclusions_sha256", "catalog_sha256", "harvest_pin", "sensitivity_label"):
            report = copy.deepcopy(component.report)
            report["kept_units_binding"][field] = "changed"
            with self.subTest(field=field), self.assertRaisesRegex(core.MintError, "^floor_mint_kept_unit_mismatch"):
                core._authenticate_kept_binding(report, component.spec, entry)

    def test_r13_non_target(self):
        with self.assertRaisesRegex(mint.MintError, "^floor_mint_cell_not_a_target"):
            build(case("all", target=False))

    def test_r9_unindexed_hazard_before_opening_bundles(self):
        with tempfile.TemporaryDirectory(prefix="s6-empty-root-") as tmp:
            root = Path(tmp)
            paths = core.ComponentPaths("missing", root, root / "missing-report", root / "missing-spec", root / "missing-order", "abs", "absolute")
            with mock.patch.object(core, "_is_hazard_runs_root", return_value=True):
                with self.assertRaisesRegex(core.MintError, "^window_index_required"):
                    core._authenticate_component(paths, expected_cell_id="abs", expected_basis_sha256="a"*64, strict_validator=lambda *_: ())
                with self.assertRaisesRegex(core.MintError, "^window_index_required"):
                    core.bind_floor_artifact_evidence({}, root / "floor.json", {"missing": root}, strict_validator=lambda *_: ())
            self.assertEqual(list(root.iterdir()), [])

    def test_r10_provenance_bound_exact_and_missing(self):
        entry = next(iter(case().entries.values()))
        for value in (0.02, 0.05, math.nextafter(0.04, 0), None, float("nan")):
            provenance = {} if value is None else {"operative_fiducial_bound_s": value}
            with self.subTest(value=value), self.assertRaisesRegex(core.MintError, "^operative_bound_not_the_window_bracket"):
                core._require_window_bound(entry, provenance)
        core._require_window_bound(entry, {"operative_fiducial_bound_s": 0.04})


class SessionSpy:
    """Only the consumption class is replaced; callers and argument flow are real."""
    calls = []
    summaries = {}
    bound_override = None

    def __init__(self, root, ids, **kwargs):
        self.calls.append((Path(root), set(ids), kwargs))
        self.ready = True
        self.refusal_reasons = ()
        self.path_refusal_reasons = {}
        self.consumption_semantics_id = kwargs.get("consumption_semantics_id", ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID)
        self.context = kwargs.get("archive_context")
        self.calibration_bracket = ww._archive_thaw(self.context.window_bracket) if self.context is not None else None
        self.operative_fiducial_bound_s = (self.calibration_bracket or {}).get("b_fiducial_s")

    def summary_for(self, bid):
        return self.summaries.get(bid, {})

    def provenance_for(self, bid):
        value = self.operative_fiducial_bound_s if self.bound_override is None else self.bound_override
        return {} if value == "missing" else {"operative_fiducial_bound_s": value}


def common_case():
    if "common" in _CACHE:
        return _CACHE["common"]
    original = case()
    result = SimpleNamespace(pins=copy.deepcopy(original.pins), inputs=copy.deepcopy(original.inputs),
                             entries={}, snapshots=original.snapshots)
    for root, entry in original.entries.items():
        bracket = ww._archive_thaw(entry.archive_context.window_bracket)
        bound = bracket["b_fiducial_s"]
        allowance = bracket["calibration_drift_allowance_s"]
        bracket.update(status="passed", endpoint_max_b_fiducial_s=bound-allowance, operative_b_fiducial_s=bound,
            acceptance={"allowance": {"rule": "max(observed_drift_s,bracket_screen_s)", "value_s": str(allowance),
                                      "embedding_count": 1, "embedded_in": "b_fiducial_s"}})
        result.entries[root] = SimpleNamespace(**{**vars(entry), "archive_context": ww.ArchiveContext(entry.window.claim_runs_root, window_bracket=bracket)})
    for source in result.inputs.values():
        for pair in source.cells.values():
            pair.comparative.spec_cell.update(estimator=df.COMMON_MODE_ESTIMATOR_ID,
                estimator_registration=df.two_shared_edge_common_mode_registration(), calibration_basis=old._mixed_calibration_basis(source))
    _CACHE["common"] = result
    return result


def common_block_input(members, **kwargs):
    fixture = common_case()
    for source in fixture.inputs.values():
        for pair in source.cells.values():
            by_id = {m.bundle_id: m.metric_value_j for m in pair.comparative.members}
            if all(m.bundle_id in by_id for m in members):
                values = [by_id[m.bundle_id] for m in members]
                delta = df.abba_delta(*values)
                return fe._CommonModeBlockInputs(onset_values_j=(delta, delta, delta), offset_values_j=(delta, delta, delta),
                    zero_point_contrast_j=delta, # The frozen D-124 outward pad adds 132 binary64 ulps here.
                    # This synthetic residual input makes the final quad width exactly 0.30 J.
                    bundle_residual_half_widths_j=(0.14999999999999633,)*4,
                    member_window_bounds_s=((-1.0, 1.0),)*4, member_envelope_integral_sum_j=max(1.0, abs(delta)+0.3))
    raise AssertionError("unknown synthetic block")


common_block_input.__signature__ = inspect.signature(fe._common_mode_block_inputs_from_evidence)


@contextlib.contextmanager
def common_seams():
    SessionSpy.calls.clear()
    with V2AuthenticationReadSession(), mock.patch.object(estimator, "AuthenticatedConsumptionSession", SessionSpy), \
         mock.patch.object(estimator, "whole_window_refusal_reasons", return_value=()), \
         mock.patch.object(fe, "_common_mode_block_inputs_from_evidence", new=common_block_input):
        yield


class CommonModeTests(unittest.TestCase):
    def built(self):
        fixture = common_case()
        with tempfile.TemporaryDirectory(prefix="s6-common-") as tmp, registered(fixture.entries), common_seams():
            path = Path(tmp) / "floor-mint-pinset.json"
            raw = mint._artifact_payload(fixture.pins)
            path.write_bytes(raw)
            sink = {}
            artifact, _components = mint._build_v2_artifacts(pinset=mint._parse_v2_pinset(fixture.pins), pinset_path=path,
                pinset_sha256=hashlib.sha256(raw).hexdigest(), producer_inputs=fixture.inputs,
                calibration_ledger_snapshot=fixture.snapshots, project_commit="0"*40, project_tree_state="clean",
                recomputation_sink=sink, d165_replay_out=Path(tmp) / "replay.json")
            sidecar = mint.dominance_closeout.build_d165_replay_sidecar(artifact, sink)
            mint._validate_block5_sidecar(sidecar, mint._parse_v2_pinset(fixture.pins), fixture.inputs)
        return fixture, artifact, sidecar

    def test_t5_kept_quads_real_sidecar_and_session(self):
        fixture, artifact, sidecar = self.built()
        for cell in artifact["cells"]:
            self.assertEqual(cell["comparative"]["n_blocks"], 8)
            self.assertEqual(cell["comparative"]["guard_factor"], 1.1338934190276817)
        for producer in fixture.pins["producer_plans"]:
            for cell in producer["cells"]:
                source = fixture.inputs[producer["plan"]["plan_id"]].cells[cell["role"]].comparative
                expected = [b["block_id"] for b in source.spec_cell["blocks"] if b["block_id"] in source.report["kept_units_binding"]["cells"][source.calibration_cell_id]["kept_unit_ids"]]
                observed = next(c for c in sidecar["cells"] if c["cell_id"] == cell["cell_id"])["comparative"]["common_mode_replay"]["inputs"]["blocks"]
                self.assertEqual([b["block_id"] for b in observed], expected)
        for root, ids, kwargs in SessionSpy.calls:
            entry = fixture.entries[str(root.resolve())]
            self.assertEqual(ids, core._producer_bundle_ids(entry))
            self.assertIs(kwargs["archive_context"], entry.archive_context)

    def test_r12_sidecar_return_value_extra_or_missing(self):
        fixture, _artifact, sidecar = self.built()
        for change in ("extra", "missing"):
            bad = copy.deepcopy(sidecar)
            blocks = bad["cells"][0]["comparative"]["common_mode_replay"]["inputs"]["blocks"]
            if change == "extra":
                blocks.append({**blocks[0], "block_id": "removed-quad"})
            else:
                blocks.pop()
            with self.subTest(change=change), registered(fixture.entries), self.assertRaisesRegex(mint.MintError, "^floor_mint_kept_unit_mismatch"):
                mint._validate_block5_sidecar(bad, mint._parse_v2_pinset(fixture.pins), fixture.inputs)

    def test_r10_shared_bound_and_session_provenance(self):
        fixture = common_case()
        producer = fixture.pins["producer_plans"][0]
        source = fixture.inputs[producer["plan"]["plan_id"]]
        kwargs = dict(core=core, comparative_component=source.cells["decode"].comparative, runs_root=source.evidence_root,
            calibration_acceptance=source.calibration_acceptance, calibration_acceptance_sha256=source.calibration_acceptance_sha256,
            calibration_allowance_projection=source.calibration_allowance_projection, declared_calibration_scope="production_window",
            calibration_ledger_snapshot=fixture.snapshots[producer["plan"]["plan_id"]], calibration_bracket_binding=source.bracket_binding)
        for value in (0.02, 0.05, "missing", math.nextafter(0.04, 0)):
            with self.subTest(value=value), registered(fixture.entries), common_seams(), \
                 mock.patch.object(SessionSpy, "bound_override", value), \
                 self.assertRaisesRegex(estimator._MintEstimatorError, "^operative_bound_not_the_window_bracket"):
                estimator.recompute_comparative_estimate(**kwargs)
        with registered(fixture.entries), common_seams(), \
             mock.patch.object(df, "registered_common_mode_operative_bound", return_value=math.nextafter(0.04, 0)), \
             self.assertRaisesRegex(estimator._MintEstimatorError, "^operative_bound_not_the_window_bracket"):
            estimator.recompute_comparative_estimate(**kwargs)


def block5_manifest(fixture):
    return {"schema_version": mint.BLOCK5_INPUT_SCHEMA, "producer_plans": [
        {"plan_id": entry.producer_plan_id, "pack": entry.window.pack,
         "exclusions_sha256": entry.kept_units.exclusions_sha256, "report": "synthetic-report.json",
         "cells": [{"role": role, "allowed_consumer_condition_families": []} for role in ("decode", "prefill")]}
        for entry in fixture.entries.values()]}


def manifest_entries(fixture):
    return {root: SimpleNamespace(**{**vars(entry),
        "window": SimpleNamespace(**{**vars(entry.window), "archive_root": core.REPO_ROOT / ".scratch-s6" / entry.window.pack}),
        "pack_path": core.REPO_ROOT / ".scratch-s6" / (entry.window.pack + "-pack")})
        for root, entry in fixture.entries.items()}


class ManifestTests(unittest.TestCase):
    def test_r6_manifest_exclusions_and_plan_identity(self):
        fixture = case()
        for field, changed, message in (("exclusions_sha256", "0"*64, "floor_mint_kept_unit_mismatch"),
                                        ("plan_id", "wrong-plan", "block5 producer plan_id mismatch")):
            manifest = block5_manifest(fixture)
            manifest["producer_plans"][0][field] = changed
            with self.subTest(field=field), registered(manifest_entries(fixture)), self.assertRaisesRegex(mint.MintError, "^" + message):
                mint._expand_block5_manifest(manifest)

    def test_closed_manifest_no_free_inputs(self):
        fixture = case()
        for field in ("evidence_root", "calibration_ledger", "calibration_ledger_head_pin", "acceptance", "spec", "order_manifest", "archive_root"):
            manifest = block5_manifest(fixture)
            manifest["producer_plans"][0][field] = "caller-selected"
            with self.subTest(field=field), registered(fixture.entries), self.assertRaises(mint.MintError):
                mint._expand_block5_manifest(manifest)

    def test_r14_floor_sibling_and_repository_directory(self):
        with tempfile.TemporaryDirectory(prefix="s6-directory-") as tmp:
            root = Path(tmp)
            for pinset, floor in ((root / "pinset.json", root / "another/floor.json"),
                                  (mint.REPO_ROOT / "scripts/floor_mint_pinsets/not-written.json",
                                   mint.REPO_ROOT / "scripts/floor_mint_pinsets/not-written-floor.json")):
                with self.subTest(pinset=pinset), self.assertRaisesRegex(mint.MintError, "^floor_pinset_not_beside_floor"):
                    mint._require_block5_floor_directory(pinset, floor)
            mint._require_block5_floor_directory(root / "pinset.json", root / "floor.json")

    def test_r16_each_producer_own_terminal_pin(self):
        fixture = case()
        artifact, _ = build(fixture)
        heads = [source.head_digest for source in fixture.snapshots.values()]
        self.assertNotEqual(*heads)
        self.assertEqual(len(artifact["cells"]), 4)
        bad = SimpleNamespace(pins=fixture.pins, inputs=fixture.inputs, entries=fixture.entries,
                              snapshots={pid: next(iter(fixture.snapshots.values())) for pid in fixture.snapshots})
        with self.assertRaisesRegex(mint.MintError, "postcollection_evidence_mismatch: terminal_ledger_head_sha256 mismatch"):
            build(bad)
        for producer in fixture.pins["producer_plans"]:
            for cell in producer["cells"]:
                self.assertEqual(cell["postcollection"]["terminal_ledger_head_sha256"], fixture.snapshots[producer["plan"]["plan_id"]].head_digest)

    def test_c10_archive_terminal_pin_containment_is_null(self):
        artifact, components = build(case())
        self.assertIsNone(artifact["provenance"]["implementation"]["head_pin_commit_contained_in_origin_main"])
        for component in components:
            self.assertIsNone(component["provenance"]["implementation"]["head_pin_commit_contained_in_origin_main"])

    def test_registry_installed_on_every_fresh_core(self):
        fixture = case()
        with registered(fixture.entries):
            a, b = mint._fresh_original_core(), mint._fresh_original_core()
            self.assertIs(a.BLOCK5_PRODUCERS, mint.BLOCK5_PRODUCERS)
            self.assertIs(b.BLOCK5_PRODUCERS, mint.BLOCK5_PRODUCERS)
        self.assertEqual(a.BLOCK5_PRODUCERS, {})


class CliTests(unittest.TestCase):
    def invoke(self, fn, args):
        err, out = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            result = fn(args)
        return result, err.getvalue(), out.getvalue()

    def mint_args(self, root):
        return ["--pinset", str(root / "pins.json"), "--pinset-sha256", "a"*64,
                "--v2-input-manifest", str(root / "inputs.json"), "--out", str(root / "floor.json"),
                "--single-count-out", str(root / "statement.md"), "--project-commit", "0"*40, "--project-tree-state", "clean"]

    def test_r17_mint_conflicting_legacy_flags(self):
        with tempfile.TemporaryDirectory(prefix="s6-cli-") as tmp:
            root = Path(tmp)
            for flag in ("--artifact-id", "--absolute-root", "--absolute-report", "--absolute-spec", "--absolute-order-manifest",
                         "--comparative-root", "--comparative-report", "--comparative-spec", "--comparative-order-manifest",
                         "--calibration-plan", "--calibration-plan-relative-path", "--calibration-custody-store"):
                with self.subTest(flag=flag):
                    self.assertEqual(self.invoke(mint.main, self.mint_args(root) + ["--window-index", "index.json", flag, "conflict"]),
                                     (2, "error: window_index_conflicting_arguments\n", ""))
            self.assertEqual(list(root.iterdir()), [])

    def test_r17_mint_analysis_refusal_code_only(self):
        fixture = case()
        with tempfile.TemporaryDirectory(prefix="s6-cli-") as tmp:
            root = Path(tmp)
            with mock.patch.object(mint, "load_pinset", return_value=mint._parse_v2_pinset(fixture.pins)), \
                 mock.patch.object(mint, "compose_indexed_producers", side_effect=AnalysisRefusal("window_bracket_not_passed")):
                self.assertEqual(self.invoke(mint.main, self.mint_args(root) + ["--window-index", "index.json"]),
                                 (2, "error: window_bracket_not_passed\n", ""))
            self.assertFalse(mint.BLOCK5_PRODUCERS)
            self.assertEqual(list(root.iterdir()), [])

    def test_r17_manifest_schema_flag_mismatches_and_registry_cleanup(self):
        fixture = case()
        with tempfile.TemporaryDirectory(prefix="s6-cli-") as tmp:
            root = Path(tmp)
            (root / "inputs.json").write_text(json.dumps({"schema_version": "joulewise.floor_mint_inputs.v2"}))
            with mock.patch.object(mint, "load_pinset", return_value=mint._parse_v2_pinset(fixture.pins)), \
                 mock.patch.object(mint, "compose_indexed_producers", return_value={e.window.pack: e for e in fixture.entries.values()}), \
                 mock.patch.object(mint, "_load_v2_input_manifest", return_value={"schema_version": "joulewise.floor_mint_inputs.v2"}):
                self.assertEqual(self.invoke(mint.main, self.mint_args(root) + ["--window-index", "index.json"]),
                                 (2, "error: window_index_conflicting_arguments\n", ""))
            self.assertFalse(mint.BLOCK5_PRODUCERS)
            with mock.patch.object(mint, "load_pinset", return_value=mint._parse_v2_pinset(fixture.pins)), \
                 mock.patch.object(mint, "_actual_v2_git_state", return_value=("0"*40, False)), \
                 mock.patch.object(mint, "_validate_v2_pin_hashes"), \
                 mock.patch.object(mint, "_load_v2_input_manifest", return_value=block5_manifest(fixture)):
                self.assertEqual(self.invoke(mint.main, self.mint_args(root)), (2, "error: window_index_required\n", ""))
            self.assertFalse((root / "floor.json").exists())

    def test_r17_emitter_conflicts_and_analysis_refusal(self):
        with tempfile.TemporaryDirectory(prefix="s6-cli-") as tmp:
            root = Path(tmp)
            args = ["--window-index", "index.json", "--alpha-report", "alpha.json", "--beta-report", "beta.json",
                    "--out-dir", str(root), "--project-commit", "0"*40]
            for flag in ("--producer-pack", "--runs-root", "--extraction-report", "--bracket-binding", "--plan-relative-path",
                         "--prefill-role", "--consumer-pack", "--calibration-acceptance", "--calibration-ledger",
                         "--calibration-ledger-head-pin", "--pinset-out", "--input-manifest-out", "--calibration-custody-store"):
                with self.subTest(flag=flag):
                    self.assertEqual(self.invoke(emit.main, args + [flag, "conflict"]), (2, "error: window_index_conflicting_arguments\n", ""))
            with mock.patch.object(mint, "compose_indexed_producers", side_effect=AnalysisRefusal("context_window_mismatch")):
                self.assertEqual(self.invoke(emit.main, args), (2, "error: context_window_mismatch\n", ""))
            self.assertFalse(mint.BLOCK5_PRODUCERS)
            self.assertEqual(list(root.iterdir()), [])

    def test_d4_legacy_emitter_hazard_root(self):
        args = ["--project-commit", "0"*40]
        for flag in ("producer-pack", "runs-root", "extraction-report", "bracket-binding", "plan-relative-path",
                     "consumer-pack", "calibration-acceptance", "calibration-ledger", "calibration-ledger-head-pin", "pinset-out", "input-manifest-out"):
            args.extend(["--" + flag, "absent"])
        with mock.patch.object(ww, "_is_hazard_runs_root", return_value=True):
            self.assertEqual(self.invoke(emit.main, args), (2, "error: window_index_required\n", ""))

    def test_d3_four_outputs_exact_and_rollback(self):
        with tempfile.TemporaryDirectory(prefix="s6-output-") as tmp:
            root = Path(tmp)
            plans = {"alpha": b"alpha sealed bytes\n", "beta": b"beta sealed bytes\n"}
            emit._write_block5_outputs(root, {"pins": "synthetic"}, {"inputs": "synthetic"}, plans)
            self.assertEqual((root / "alpha/calibration_plan.json").read_bytes(), plans["alpha"])
            self.assertEqual((root / "beta/calibration_plan.json").read_bytes(), plans["beta"])
            with self.assertRaises(mint.MintError):
                emit._write_block5_outputs(root, {}, {}, plans)
        with tempfile.TemporaryDirectory(prefix="s6-output-") as tmp:
            root = Path(tmp)
            actual = Path.open
            def fail(path, *args, **kwargs):
                if path.name == "calibration_plan.json":
                    raise OSError("synthetic write failure")
                return actual(path, *args, **kwargs)
            with mock.patch.object(Path, "open", new=fail), self.assertRaises(OSError):
                emit._write_block5_outputs(root, {}, {}, plans)
            self.assertFalse(any(path.is_file() for path in root.rglob("*")))


def authentication_case():
    """Cache one physical synthetic mint corpus, reusing the historical writer."""
    if "authentication" in _CACHE:
        return _CACHE["authentication"]
    import shutil
    temp = tempfile.TemporaryDirectory(prefix="s6-auth-")
    atexit.register(temp.cleanup)
    directory = Path(temp.name)
    full = case("all")
    trimmed = case()
    pid = next(iter(full.inputs))
    root = directory / "runs"
    paths = {}
    for kind in ("absolute", "comparative"):
        paths[kind] = old._install_component_fixture(directory, kind,
            getattr(full.inputs[pid].cells["decode"], kind), evidence_root=root)
    for component_paths in paths.values():
        spec = json.loads(component_paths.spec_path.read_bytes())
        for cell in spec["cells"]:
            for binding in cell["condition_family_definitions"].values():
                binding["condition_family_definition"]["measurement_target"]["metric"] = cell["metric"]
                binding["condition_family_sha256"] = df.canonical_domain_sha256(df.CONDITION_FAMILY_DOMAIN,
                    binding["condition_family_definition"])
        component_paths.spec_path.write_bytes(mint._artifact_payload(spec))
        order = json.loads(component_paths.order_manifest_path.read_bytes())
        order["executed_order"] = [{"run_id": bid} for bid in dict.fromkeys(row["run_id"] for row in order["executed_order"])]
        component_paths.order_manifest_path.write_bytes(mint._artifact_payload(order))
    log = json.loads((root / "campaign_log.jsonl").read_bytes())
    log["evaluation_basis"]["member_occurrences"] = [{"bundle_id": bid} for bid in
        dict.fromkeys(row["bundle_id"] for row in log["evaluation_basis"]["member_occurrences"])]
    (root / "campaign_log.jsonl").write_bytes(json.dumps(log, sort_keys=True, separators=(",", ":")).encode() + b"\n")
    source = trimmed.inputs[pid]
    report = copy.deepcopy(source.cells["decode"].absolute.report)
    report["runs_root"] = str(root)
    for cell in report["cells"]:
        for row in cell["members"]:
            if row["excluded"]:
                continue
            bundle = root / row["bundle_id"]
            summary = json.loads((bundle / "summary_metrics.json").read_bytes())
            for envelope in summary["energy_anchor_shift_envelopes"].values():
                value, width = envelope["point_j"], envelope["max_abs_delta_j"]
                envelope["lower_j"] = math.nextafter(value-width, value) if width else value
                envelope["upper_j"] = math.nextafter(value+width, value) if width else value
            (bundle / "summary_metrics.json").write_bytes(mint._artifact_payload(summary))
            row["anchor_shift_bound_j"] = 0.05 if cell["kind"] == "absolute" else 0.15
            row["bundle_sha256"] = df.complete_bundle_sha256(bundle)
            row["config_sha256"] = hashlib.sha256((bundle / "config.json").read_bytes()).hexdigest()
    report_path = directory / "report.json"
    report_path.write_bytes(mint._artifact_payload(report))
    removed = sorted(next(iter(trimmed.entries.values())).kept_units.removed_run_ids())
    shutil.rmtree(root / removed[0])
    (root / removed[1] / "summary_metrics.json").write_text("invalid JSON of a removed member")
    entry = next(iter(trimmed.entries.values()))
    entries = {str(root.resolve()): entry}
    _CACHE["authentication"] = SimpleNamespace(directory=directory, root=root, report=report, report_path=report_path,
        paths=paths, source=source, entry=entry, entries=entries, removed=set(removed))
    return _CACHE["authentication"]


@contextlib.contextmanager
def authenticated_core(fixture):
    with registered(fixture.entries):
        instance = mint._fresh_original_core()
        instance.BLOCK5_PRODUCERS = mint.BLOCK5_PRODUCERS
        instance.PLAN_SHA256 = fixture.source.plan_sha256
        SessionSpy.calls.clear()
        SessionSpy.summaries = {bid: json.loads((fixture.root / bid / "summary_metrics.json").read_bytes())
                                for bid in instance._producer_bundle_ids(fixture.entry)}
        with mock.patch.object(instance, "AuthenticatedConsumptionSession", SessionSpy), \
             mock.patch.object(instance, "whole_window_refusal_reasons", return_value=()), \
             mock.patch.object(instance, "build_stack_identity", side_effect=lambda *_: old.stack_identity()), \
             mock.patch.object(instance, "scientific_config_identity", side_effect=lambda *_: {"synthetic": "same"}):
            yield instance


def authenticate_physical(instance, fixture, kind="comparative", report_path=None):
    source = getattr(fixture.source.cells["decode"], kind)
    paths = fixture.paths[kind]
    return instance._authenticate_component(instance.ComponentPaths(source.evidence_root_id, fixture.root,
        report_path or fixture.report_path, paths.spec_path, paths.order_manifest_path, source.calibration_cell_id, kind),
        expected_cell_id=source.calibration_cell_id, expected_basis_sha256=source.whole_window_evaluation_basis_sha256,
        strict_validator=lambda *_: (), calibration_ledger_snapshot=next(iter(case().snapshots.values())),
        expected_consumption_semantics_id=ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
        allowance_deriver=lambda *_args, **_kwargs: SimpleNamespace(status="allowances",
            allowances={"gross_energy": source.whole_window_drift_allowance}))


class PhysicalAuthenticationTests(unittest.TestCase):
    def test_r11_core_consumption_and_allowance_sessions_kept_only(self):
        fixture = authentication_case()
        with authenticated_core(fixture) as instance:
            component = authenticate_physical(instance, fixture)
            self.assertEqual(len(component.members), 32)
            self.assertEqual(len(SessionSpy.calls), 2)
            for root, ids, kwargs in SessionSpy.calls:
                self.assertEqual(root, fixture.root)
                self.assertEqual(ids, instance._producer_bundle_ids(fixture.entry))
                self.assertIs(kwargs["archive_context"], fixture.entry.archive_context)
                self.assertEqual(kwargs["consumption_semantics_id"], ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID)
                self.assertFalse(ids & fixture.removed)

    def test_r1_r2_r3_r4_authentication_call_site(self):
        fixture = authentication_case()
        for change in ("pinned_removed", "missing_kept", "hidden_kept", "silent_exclusion", "partial_quad"):
            report = copy.deepcopy(fixture.report)
            cell = next(c for c in report["cells"] if c["kind"] == "comparative")
            if change == "pinned_removed":
                next(r for r in cell["members"] if r["excluded"]).update(excluded=False, metric_value_j=1.0)
            elif change in ("missing_kept", "hidden_kept"):
                cell["members"] = cell["members"][4:]
                if change == "hidden_kept":
                    report["kept_units_binding"]["cells"][cell["cell_id"]]["kept_unit_ids"].pop(0)
            else:
                cell["members"][0]["excluded"] = True
            path = fixture.directory / (change + ".json")
            path.write_bytes(mint._artifact_payload(report))
            with self.subTest(change=change), authenticated_core(fixture) as instance, \
                 self.assertRaisesRegex(instance.MintError, "^floor_mint_kept_unit_mismatch"):
                authenticate_physical(instance, fixture, report_path=path)
            self.assertEqual(SessionSpy.calls, [])

    def test_r7_swapped_entries_first_check(self):
        fixture = authentication_case()
        other = list(case().entries.values())[1]
        with authenticated_core(fixture) as instance:
            instance.BLOCK5_PRODUCERS = {str(fixture.root.resolve()): other}
            with self.assertRaisesRegex(instance.MintError, "^floor_mint_kept_unit_mismatch: exclusions_cell_unknown"):
                authenticate_physical(instance, fixture)

    def test_r10_each_report_and_session_bound(self):
        fixture = authentication_case()
        for value in (0.02, 0.05, "missing", math.nextafter(0.04, 0)):
            with self.subTest(value=value), authenticated_core(fixture) as instance, \
                 mock.patch.object(SessionSpy, "bound_override", value), \
                 self.assertRaisesRegex(instance.MintError, "^operative_bound_not_the_window_bracket"):
                authenticate_physical(instance, fixture)
            report = copy.deepcopy(fixture.report)
            row = next(c for c in report["cells"] if c["kind"] == "comparative")["members"][0]
            row["consumption_provenance"] = {} if value == "missing" else {"operative_fiducial_bound_s": value}
            path = fixture.directory / "bad-bound.json"
            path.write_bytes(mint._artifact_payload(report))
            with self.subTest(report_value=value), authenticated_core(fixture) as instance, \
                 self.assertRaisesRegex(instance.MintError, "^operative_bound_not_the_window_bracket"):
                authenticate_physical(instance, fixture, report_path=path)


def governed_case():
    if "governed" in _CACHE:
        return _CACHE["governed"]
    import shutil
    fixture = indexed_fixture()
    pack = fixture.window.archive / "sources/repo/configs/campaigns" / fixture.window.entry.pack_id
    plan = pack / "calibration_plan.json"
    # S0's small synthetic pack never supplied these two mint inputs. Extend
    # only its temporary archive, then rebind its source census and index.
    (pack / "calibration_plan.sha256").write_text(hashlib.sha256(plan.read_bytes()).hexdigest() + "  calibration_plan.json\n")
    ids = list(dict.fromkeys(mint._v2_spec_member_ids(fixture.spec)))
    fx.put(pack / "order_manifest.json", {"executed_order": [{"run_id": bid} for bid in ids]})
    for name in ("calibration_plan.json", "calibration_plan.sha256", "order_manifest.json"):
        shutil.copyfile(pack / name, fixture.local_spec.parent / name)
    # Exercise Erratum 3's stored-failed basis with no calibration pair.
    row = copy.deepcopy(fixture.row)
    row["idle_admission_core"]["instrument_calibration_bracket"] = None
    row["evaluation_basis"]["calibration_bracket_set"] = ww._calibration_bracket_basis(None)
    row["evaluation_basis"].pop("launch_lineage", None)
    basis = row["evaluation_basis"]
    basis["sha256"] = ww.canonical_sha256({key: value for key, value in basis.items() if key != "sha256"})
    fixture.row = row
    for path in (fixture.window.claim / "whole-window-verdict.json", fixture.window.archive / "sources/claim-runs/whole-window-verdict.json"):
        fx.put(path, row)
    log_path = fixture.window.archive / "sources/claim-runs/campaign_log.jsonl"
    rows = [json.loads(line) for line in log_path.read_bytes().splitlines() if line.strip()]
    rows = [row if item.get("record_type") == "idle_admission_whole_window_verdict" else item for item in rows]
    raw = b"".join(json.dumps(item, sort_keys=True, separators=(",", ":")).encode() + b"\n" for item in rows)
    log_path.write_bytes(raw)
    (fixture.window.claim / "campaign_log.jsonl").write_bytes(raw)
    allowance_path = fixture.window.archive / ww.NEG8_HARVEST_ALLOWANCE_RECORD
    allowance = json.loads(allowance_path.read_bytes())
    allowance["verdict"]["row_sha256"] = ww.canonical_sha256(row)
    allowance["verdict"]["evaluation_basis_sha256"] = basis["sha256"]
    fx.put(allowance_path, allowance)
    # Attempt identity is independent of the archived producer plan identity.
    attempt_id = f"v5-b5-beta-a{fixture.window.entry_data['attempt']}-test"
    fixture.window.entry_data["plan_id"] = attempt_id
    for relative in ("harvest.json", "derived/roster.json", "derived/exclusions.json"):
        path = fixture.window.archive / relative
        value = json.loads(path.read_bytes())
        value["plan_id"] = attempt_id
        fx.put(path, value)
    flags_path = fixture.window.archive / "derived/window_flags.json"
    flags = json.loads(flags_path.read_bytes())
    flags["window"]["plan_id"] = attempt_id
    fx.put(flags_path, flags)
    s2.refresh(fixture.window)
    index = json.loads(fixture.index.read_bytes())
    for entry in index["attempts"]:
        if entry["pack"] == "beta":
            entry["plan_id"] = f"v5-b5-beta-a{entry['attempt']}-test"
            if entry.get("archive_root") == str(fixture.window.archive):
                entry.update(fixture.window.entry_data)
    fx.put(fixture.index, index)
    with s2.capture_adapter():
        table = {**fx.PACK_TABLE, "beta": {fixture.window.entry_data["pack_id"]: "v5-b5-beta-a{attempt}-"}}
        entry = mint.compose_indexed_producers(fixture.index, seal_pins=SealPins.load(), pack_table=table,
            test_only_allow_synthetic_binding=True, repo_root=fixture.local_repo, packs=("beta",))["beta"]
    _CACHE["governed"] = fixture, entry
    return fixture, entry


class GovernedTests(unittest.TestCase):
    def test_real_composition_bracket_shape_and_allowance(self):
        fixture, entry = governed_case()
        self.assertEqual(entry.verdict_row["status"], "failed")
        self.assertEqual(entry.verdict_row["evaluation_basis"]["calibration_bracket_set"], {"pre": None, "post": None})
        bracket = entry.archive_context.window_bracket
        component = SimpleNamespace(whole_window_calibration_bracket=bracket)
        projected = mint._v2_component_verdict_bracket(component, label="synthetic governed window")
        for index, role in enumerate(("pre", "post")):
            self.assertEqual(projected.endpoint_attempt_ids[index], bracket[role]["attempt_id"])
            self.assertEqual(projected.endpoint_receipt_sha256s[index], bracket[role]["ledger_receipt_digest"])
            self.assertEqual(projected.endpoint_content_sha256s[index], bracket[role]["content_id"])
        acceptance_path = entry.window.archive_root / "sources/inputs/acceptance.json"
        acceptance, raw = mint._strict_json_file(acceptance_path, "synthetic acceptance")
        observations = entry.ledger_snapshot.bracket_session_by_id[projected.session_id].finalized_slots
        inputs = mint.V2ProducerInputs(plan={}, cells={}, evidence_root=entry.window.claim_runs_root, plan_sha256="0"*64,
            plan_declared_sha256="0"*64, plan_sidecar_sha256="0"*64, calibration_acceptance=acceptance,
            calibration_acceptance_sha256=hashlib.sha256(raw).hexdigest(), bracket_binding={}, bracket_binding_sha256="0"*64)
        with registered({str(entry.window.claim_runs_root.resolve()): entry}):
            projection = mint._v2_allowance_projection(inputs, observations["pre"], observations["post"])
        self.assertEqual(projection["applied_allowance_s"], "0.014531")
        self.assertEqual(bracket["calibration_drift_allowance_s"], 0.014531)

    def test_governed_real_session_records_mock_dispatch_limit(self):
        _fixture, entry = governed_case()
        with registered({str(entry.window.claim_runs_root.resolve()): entry}), s2.capture_adapter(), \
             self.assertRaisesRegex(core.MintError, "authenticated whole-window consumption refused: whole_window_neg8_verdict_missing"):
            core._authenticated_consumption_summaries(entry.window.claim_runs_root, core._producer_bundle_ids(entry),
                entry.verdict_row["evaluation_basis"]["sha256"], target_bundle_ids=core._producer_bundle_ids(entry),
                consumption_semantics_id=ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID, calibration_ledger_snapshot=entry.ledger_snapshot)

    def test_governed_spy_retains_real_context_and_units(self):
        _fixture, entry = governed_case()
        ids = core._producer_bundle_ids(entry)
        SessionSpy.calls.clear()
        with registered({str(entry.window.claim_runs_root.resolve()): entry}), \
             mock.patch.object(core, "AuthenticatedConsumptionSession", SessionSpy), \
             mock.patch.object(core, "whole_window_refusal_reasons", return_value=()):
            summaries, semantics = core._authenticated_consumption_summaries(entry.window.claim_runs_root, ids,
                entry.verdict_row["evaluation_basis"]["sha256"], target_bundle_ids=ids,
                consumption_semantics_id=ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID, calibration_ledger_snapshot=entry.ledger_snapshot)
        self.assertEqual(set(summaries), ids)
        self.assertEqual(semantics, ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID)
        root, actual_ids, kwargs = SessionSpy.calls[0]
        self.assertEqual((root, actual_ids), (entry.window.claim_runs_root, ids))
        self.assertIs(kwargs["archive_context"], entry.archive_context)

    def test_r8_report_without_context_first_refusal(self):
        from scripts import extract_detection_floors
        fixture, entry = governed_case()
        with s2.capture_adapter(), mock.patch.object(fe, "_block5_runs_root", return_value=True):
            report = fe.extract_cells(entry.window.claim_runs_root, fixture.spec, kept_units=entry.kept_units,
                evaluation_basis_sha256=entry.verdict_row["evaluation_basis"]["sha256"],
                consumption_semantics_id=ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID, mode="read_replay")
        cell = fixture.spec["cells"][0]
        self.assertFalse(report["cells"][0]["extractable"])
        self.assertIn("whole_window_drift_allowance_unrecorded", report["cells"][0]["refusal_reasons"])
        with self.assertRaisesRegex(core.MintError, "extraction report is not an extractable target"):
            core._target_report_cell(report, cell["cell_id"], cell["kind"])


class BinderSessionTests(unittest.TestCase):
    def test_r11_binder_session_kept_scope_and_context(self):
        fixture = authentication_case()
        with authenticated_core(fixture) as instance:
            absolute = authenticate_physical(instance, fixture, "absolute")
            comparative = authenticate_physical(instance, fixture)
            abs_record = instance.build_absolute_record(instance.absolute_false_effect_floor(
                [m.metric_value_j for m in absolute.members], admissible_half_widths_j=absolute.widths_j),
                instance._absolute_observations(absolute), consumption_semantics_id=absolute.consumption_semantics_id,
                whole_window_drift_allowance=absolute.whole_window_drift_allowance)
            blocks, deltas = instance._comparative_blocks(comparative)
            cmp_record = instance.build_comparative_record(instance.comparative_false_effect_floor(
                deltas, admissible_half_widths_j=comparative.widths_j), blocks,
                consumption_semantics_id=comparative.consumption_semantics_id,
                whole_window_drift_allowance=comparative.whole_window_drift_allowance)
            template, components = build(case())
            artifact = copy.deepcopy(components[0])
            cell = artifact["cells"][0]
            cell.update(absolute=abs_record, comparative=cmp_record,
                provenance={"absolute": instance._component_provenance(absolute), "comparative": instance._component_provenance(comparative)},
                source_regime=absolute.source_regime)
            artifact["cells"] = [cell]
            artifact["transport_groups"] = artifact["transport_groups"][:1]
            plan_path = fixture.directory / artifact["provenance"]["calibration_plan"]["relative_path"]
            plan_path.parent.mkdir(parents=True, exist_ok=True)
            plan_raw = mint._artifact_payload(fixture.source.plan)
            plan_path.write_bytes(plan_raw)
            artifact["provenance"]["calibration_plan"]["sha256"] = hashlib.sha256(plan_raw).hexdigest()
            SessionSpy.calls.clear()
            # Arithmetic and v2 pinset validation have separate real tests above.
            # This binder-only test isolates the third construction using real
            # stored bundle/config hashes and the real pinned binder body.
            with mock.patch.object(instance, "validate_floor_artifact", return_value=[]), \
                 mock.patch.object(instance, "_authenticated_consumption_summaries", wraps=instance._authenticated_consumption_summaries) as consume:
                bound = instance.bind_floor_artifact_evidence(artifact, fixture.directory / "floor.json",
                    {absolute.evidence_root_id: fixture.root}, strict_validator=lambda *_: (),
                    calibration_ledger_snapshot=next(iter(case().snapshots.values())))
            self.assertTrue(bound)
            self.assertEqual(len(consume.call_args_list), 2)
            for call in consume.call_args_list:
                self.assertEqual(call.args[1], instance._producer_bundle_ids(fixture.entry))
            self.assertEqual(len(SessionSpy.calls), 2)
            for root, ids, kwargs in SessionSpy.calls:
                self.assertEqual((root, ids), (fixture.root, instance._producer_bundle_ids(fixture.entry)))
                self.assertIs(kwargs["archive_context"], fixture.entry.archive_context)
                self.assertFalse(ids & fixture.removed)


def issued_common_case():
    if "issued_common" not in _CACHE:
        fixture = common_case()
        with tempfile.TemporaryDirectory(prefix="s6-common-pins-") as tmp, registered(fixture.entries), common_seams():
            pins = emit.build_pinset(contracts=contracts_from_pins(fixture.pins), producer_inputs=fixture.inputs,
                ledger_snapshot=fixture.snapshots, relative_plan_paths=[p["plan"]["relative_path"] for p in fixture.pins["producer_plans"]],
                pinset_path=Path(tmp) / "floor-mint-pinset.json", project_commit="0"*40,
                kept_units={e.producer_plan_id: e.kept_units for e in fixture.entries.values()},
                window_brackets={e.producer_plan_id: e.archive_context.window_bracket for e in fixture.entries.values()})
        _CACHE["issued_common"] = pins
    return _CACHE["issued_common"]


class AtomicReplayTests(unittest.TestCase):
    def test_r12_builder_return_checked_before_all_three_outputs(self):
        fixture = common_case()
        pins = issued_common_case()
        original_build = mint._build_v2_artifacts
        original_sidecar = mint.dominance_closeout.build_d165_replay_sidecar
        for change in ("extra", "missing"):
            with self.subTest(change=change), tempfile.TemporaryDirectory(prefix="s6-atomic-") as tmp:
                root = Path(tmp)
                pinset_path = root / "floor-mint-pinset.json"
                raw = mint._artifact_payload(pins)
                pinset_path.write_bytes(raw)
                manifest_path = root / "floor-mint-inputs.json"
                manifest_path.write_bytes(mint._artifact_payload(block5_manifest(fixture)))
                sink = {}
                def build_with_sink(**kwargs):
                    result = original_build(**kwargs)
                    sink.update(kwargs["recomputation_sink"])
                    return result
                def bind(**kwargs):
                    return {}, sink[kwargs["artifact"]["cells"][0]["cell_id"]]
                def sidecar(*args):
                    value = original_sidecar(*args)
                    blocks = value["cells"][0]["comparative"]["common_mode_replay"]["inputs"]["blocks"]
                    if change == "extra":
                        blocks.append({**blocks[0], "block_id": "removed-quad"})
                    else:
                        blocks.pop()
                    return value
                with registered(fixture.entries), common_seams(), \
                     mock.patch.object(mint, "_actual_v2_git_state", return_value=("0"*40, False)), \
                     mock.patch.object(mint, "_authenticate_v2_inputs", return_value=(fixture.inputs,
                         {p["evidence_root_id"]: fixture.inputs[p["plan"]["plan_id"]].evidence_root for p in pins["producer_plans"]}, fixture.snapshots)), \
                     mock.patch.object(mint, "_build_v2_artifacts", side_effect=build_with_sink), \
                     mock.patch.object(estimator, "bind_v2_floor_artifact_evidence", side_effect=bind), \
                     mock.patch.object(mint.dominance_closeout, "build_d165_replay_sidecar", side_effect=sidecar), \
                     self.assertRaisesRegex(mint.MintError, "^floor_mint_kept_unit_mismatch"):
                    mint.mint_multi_cell_floor_artifact(pinset_path=pinset_path, pinset_sha256=hashlib.sha256(raw).hexdigest(),
                        input_manifest_path=manifest_path, floor_path=root / "floor.json", statement_path=root / "statement.md",
                        d165_replay_out=root / "replay.json", project_commit="0"*40, project_tree_state="clean",
                        strict_validator=lambda *_: ())
                for name in ("floor.json", "statement.md", "replay.json"):
                    self.assertFalse((root / name).exists())


class AdditionalRefusalTests(unittest.TestCase):
    def test_r13_core_non_target_before_session(self):
        fixture = authentication_case()
        kept = replace(fixture.entry.kept_units, cells={cid: replace(cell, target=False) for cid, cell in fixture.entry.kept_units.cells.items()})
        entry = SimpleNamespace(**{**vars(fixture.entry), "kept_units": kept})
        report = copy.deepcopy(fixture.report)
        spec = json.loads(fixture.paths["comparative"].spec_path.read_bytes())
        binding, _ids = core._kept_spec_bindings(spec, entry)
        report["kept_units_binding"]["cells"] = binding
        path = fixture.directory / "non-target.json"
        path.write_bytes(mint._artifact_payload(report))
        with authenticated_core(fixture) as instance:
            instance.BLOCK5_PRODUCERS = {str(fixture.root.resolve()): entry}
            with self.assertRaisesRegex(instance.MintError, "^floor_mint_cell_not_a_target"):
                authenticate_physical(instance, fixture, report_path=path)
        self.assertEqual(SessionSpy.calls, [])

    def test_block5_manifest_requires_index_before_git_issuance(self):
        fixture = case()
        with tempfile.TemporaryDirectory(prefix="s6-no-index-") as tmp:
            root = Path(tmp)
            args = CliTests().mint_args(root)
            with mock.patch.object(mint, "load_pinset", return_value=mint._parse_v2_pinset(fixture.pins)), \
                 mock.patch.object(mint, "_load_v2_input_manifest", return_value=block5_manifest(fixture)), \
                 mock.patch.object(mint, "_actual_v2_git_state", side_effect=mint.MintError("Git gate reached before required index")):
                self.assertEqual(CliTests().invoke(mint.main, args), (2, "error: window_index_required\n", ""))
            self.assertFalse((root / "floor.json").exists())

    def test_allowance_matches_window_decimal_and_endpoint_identities(self):
        fixture = case()
        source = next(iter(fixture.inputs.values()))
        root = str(source.evidence_root.resolve())
        entry = fixture.entries[root]
        for change in ("allowance", "endpoint"):
            bracket = ww._archive_thaw(entry.archive_context.window_bracket)
            if change == "allowance":
                bracket["calibration_drift_allowance_s"] = math.nextafter(bracket["calibration_drift_allowance_s"], math.inf)
            else:
                bracket["pre"]["attempt_id"] = "other-window-pre"
            bad = SimpleNamespace(**{**vars(entry), "archive_context": ww.ArchiveContext(source.evidence_root, window_bracket=bracket)})
            with self.subTest(change=change), registered({root: bad}), self.assertRaisesRegex(mint.MintError, "^postcollection_evidence_mismatch"):
                mint._v2_allowance_projection(source, source.authenticated_pre_observation, source.authenticated_post_observation)


class MaximumSemanticsTests(unittest.TestCase):
    def test_block5_cannot_request_minted_semantics(self):
        fixture = case()
        root = next(iter(fixture.inputs.values())).evidence_root
        with registered(fixture.entries), self.assertRaisesRegex(core.MintError, "^floor_mint_kept_unit_mismatch"):
            core._authenticated_consumption_summaries(root, set(), "0"*64, target_bundle_ids=set(),
                consumption_semantics_id=ww.MINTED_CONSUMPTION_SEMANTICS_ID)


class ContinuationTests(unittest.TestCase):
    def test_f1_sealed_config_identity_and_attempt_prefix(self):
        from joulewise.b5_analysis.windows import sealed_pack_table
        for pack, rows in sealed_pack_table().items():
            if pack == "gamma":
                continue
            for pack_id, prefix in rows.items():
                path = core.REPO_ROOT / "configs/campaigns" / pack_id
                plan = json.loads((path / "calibration_plan.json").read_bytes())
                contract = json.loads((path / "producer_contract.json").read_bytes())
                tree = json.loads((path / "plan_tree.json").read_bytes())
                self.assertEqual(plan["plan_id"], contract["plan"]["plan_id"])
                self.assertEqual(plan["plan_id"], tree["plan"]["plan_id"])
                self.assertFalse(plan["plan_id"].startswith(prefix.format(attempt=1)))
        for entry in case().entries.values():
            self.assertNotEqual(entry.window.plan_id, entry.producer_plan_id)
            with registered(case().entries):
                self.assertIs(mint._producer_by_plan_id(entry.producer_plan_id), entry)
                with self.assertRaises(mint.MintError):
                    mint._producer_by_plan_id(entry.window.plan_id)

    def test_f1_composed_identity_and_mismatch(self):
        _fixture, entry = governed_case()
        self.assertNotEqual(entry.producer_plan_id, entry.window.plan_id)
        prefix = f"sources/repo/configs/campaigns/{entry.window.pack_id}/"
        raw = {name: entry.archive.source_bytes(prefix + name)
               for name in ("calibration_plan.json", "plan_tree.json")}
        tree = json.loads(raw["plan_tree.json"])
        tree["plan"]["plan_id"] = "wrong-producer"
        raw["plan_tree.json"] = mint._artifact_payload(tree)
        archive = SimpleNamespace(plan_tree_binding_kind="synthetic", source_bytes=lambda name: raw[name.removeprefix(prefix)])
        with self.assertRaisesRegex(AnalysisRefusal, "^producer_plan_identity_mismatch"):
            mint._producer_plan_identity(entry.pack_path, archive, prefix)

    def test_f1_missing_ledger_key_is_mint_error(self):
        with self.assertRaisesRegex(mint.MintError, "producer ledger snapshot missing"):
            mint._producer_ledger(case().snapshots, "unregistered-producer")
        with registered(case().entries), self.assertRaises(mint.MintError):
            mint._producer_by_plan_id("unregistered-producer")

    def test_ca_archive_changed_after_real_composition(self):
        _fixture, entry = governed_case()
        entries = {str(entry.window.claim_runs_root.resolve()): entry,
                   "synthetic-alpha": replace(entry, window=replace(entry.window, pack="alpha"))}
        manifest = {"schema_version": mint.BLOCK5_INPUT_SCHEMA, "producer_plans": [
            {"plan_id": e.producer_plan_id, "pack": e.window.pack,
             "exclusions_sha256": e.kept_units.exclusions_sha256, "report": "synthetic-report.json",
             "cells": [{"role": role, "allowed_consumer_condition_families": []}
                       for role in ("decode", "prefill")]} for e in entries.values()]}
        for relative in ("sources/inputs/acceptance.json", "derived/bracket-binding.json"):
            path = entry.window.archive_root / relative
            original = path.read_bytes()
            try:
                path.write_bytes(original + b"\n")
                with self.subTest(relative=relative), registered(entries), \
                     self.assertRaisesRegex(mint.MintError, "^archive_input_changed_after_authentication"):
                    mint._expand_block5_manifest(manifest)
            finally:
                path.write_bytes(original)

    def test_cc_launch_dispatch_kept_members(self):
        entry = next(iter(case().entries.values()))
        component = next(iter(case().inputs.values())).cells["decode"].comparative
        kept = core._producer_bundle_ids(entry)
        for governed in (False, True):
            selected = SimpleNamespace(**{**vars(entry), "archive_context": ww.ArchiveContext(
                entry.window.claim_runs_root, window_bracket=entry.archive_context.window_bracket,
                governed_e3=governed)})
            with self.subTest(governed=governed), \
                 mock.patch.object(estimator, "authenticate_window_launch_lineage", return_value=None) as sealed, \
                 mock.patch.object(ww, "_authenticated_bundle_launch_lineage_set", return_value=None) as recomputed:
                estimator._authenticate_mint_launch_lineage(component, runs_root=entry.window.claim_runs_root,
                    producer_entry=selected)
            # Lead's rule after the continuation round: every block-5 producer,
            # governed or not, authenticates lineage from the kept members'
            # bundles; the sealed resolver, which opens removed members'
            # directories, is never called on this path.
            sealed.assert_not_called()
            self.assertEqual(set(recomputed.call_args.args[0]), {entry.window.claim_runs_root / bid for bid in kept})
            self.assertFalse(kept & entry.kept_units.removed_run_ids())

    def test_cc_ungoverned_stored_lineage_must_equal_the_kept_members_lineage(self):
        entry = next(iter(case().entries.values()))
        component = next(iter(case().inputs.values())).cells["decode"].comparative
        lineage = {"schema": "synthetic-lineage", "launch_id": "L1"}
        component = replace(component, report={**component.report, "launch_lineage": lineage})

        def run(governed, row):
            selected = SimpleNamespace(**{**vars(entry), "verdict_row": row, "archive_context": ww.ArchiveContext(
                entry.window.claim_runs_root, window_bracket=entry.archive_context.window_bracket,
                governed_e3=governed)})
            with mock.patch.object(estimator, "authenticate_window_launch_lineage") as sealed, \
                 mock.patch.object(ww, "_authenticated_bundle_launch_lineage_set", return_value=dict(lineage)), \
                 mock.patch.object(ww, "harvest_neg8_allowance_bracket", return_value=({}, None)), \
                 mock.patch.object(ww, "_authenticate_whole_window_launch_sources", return_value=dict(lineage)) as sources:
                result = estimator._authenticate_mint_launch_lineage(component, runs_root=entry.window.claim_runs_root,
                    producer_entry=selected)
            sealed.assert_not_called()
            self.assertEqual(sources.call_args.kwargs["calibration_bracket"],
                             ww._archive_thaw(entry.archive_context.window_bracket))
            return result

        self.assertEqual(run(False, {"evaluation_basis": {"launch_lineage": dict(lineage)}}), lineage)
        # A governed window's stored basis carries no lineage (Erratum 3 item 9).
        self.assertEqual(run(True, {"evaluation_basis": {}}), lineage)
        for row in ({"evaluation_basis": {"launch_lineage": {**lineage, "launch_id": "L2"}}},
                    {"evaluation_basis": {}}, {}):
            with self.subTest(row=row), self.assertRaisesRegex(estimator._MintEstimatorError, "^launch_lineage_conflict"):
                run(False, row)

    def test_cd_spec_and_producer_kept_member_sets_must_agree(self):
        fixture = authentication_case()
        with authenticated_core(fixture) as instance, \
             mock.patch.object(instance, "_producer_bundle_ids", return_value=core._producer_bundle_ids(fixture.entry) | {"extra-kept"}), \
             self.assertRaisesRegex(instance.MintError, "^floor_mint_kept_unit_mismatch"):
            authenticate_physical(instance, fixture)
        self.assertEqual(SessionSpy.calls, [])

    def test_v2_r13_p42_pin_through_gate(self):
        fixture = case(target=False)
        source = next(iter(fixture.inputs.values()))
        actual = source.cells["prefill"].absolute
        pins = copy.deepcopy(fixture.pins["producer_plans"][0]["cells"][1]["absolute"])
        pins["calibration_cell_id"] = "p42-" + actual.calibration_cell_id
        actual = replace(actual, calibration_cell_id=pins["calibration_cell_id"],
            spec_cell={**actual.spec_cell, "cell_id": pins["calibration_cell_id"]})
        spec = {**actual.spec, "cells": [actual.spec_cell if c["cell_id"] == source.cells["prefill"].absolute.calibration_cell_id
                                          else c for c in actual.spec["cells"]]}
        entry = next(iter(fixture.entries.values()))
        bindings, _ = core._kept_spec_bindings(spec, entry)
        report = {**actual.report, "kept_units_binding": {**actual.report["kept_units_binding"], "cells": bindings}}
        actual = replace(actual, spec=spec, report=report)
        with registered(fixture.entries), self.assertRaisesRegex(mint.MintError, "^floor_mint_cell_not_a_target"):
            mint._v2_gate_component(actual, pins, label="prefill p42", metric=actual.spec_cell["metric"], window_class="phase")

    def test_v2_r1_removed_pin_through_gate(self):
        fixture = case()
        actual = next(iter(fixture.inputs.values())).cells["decode"].comparative
        pins = copy.deepcopy(fixture.pins["producer_plans"][0]["cells"][0]["comparative"])
        removed = next(row for row in actual.cell["members"] if row["excluded"])
        pins["members"].append({"bundle_id": removed["bundle_id"], "config_sha256": "0"*64})
        pins["expected_n"] += 1
        with registered(fixture.entries), self.assertRaisesRegex(mint.MintError, "^floor_mint_kept_unit_mismatch"):
            mint._v2_gate_component(actual, pins, label="removed pin", metric=actual.spec_cell["metric"], window_class="phase")

    def test_v2_r6_report_digest_repinned_through_authentication(self):
        fixture = authentication_case()
        report = copy.deepcopy(fixture.report)
        report["kept_units_binding"]["exclusions_sha256"] = "0"*64
        raw = mint._artifact_payload(report)
        path = fixture.directory / "repinned-report.json"
        path.write_bytes(raw)
        pins = copy.deepcopy(case().pins)
        pins["producer_plans"][0]["cells"][0]["postcollection"]["extraction_report_sha256"] = hashlib.sha256(raw).hexdigest()
        self.assertEqual(pins["producer_plans"][0]["cells"][0]["postcollection"]["extraction_report_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        with authenticated_core(fixture) as instance, self.assertRaisesRegex(instance.MintError,
                "^floor_mint_kept_unit_mismatch: exclusions_sha256 differs from report binding"):
            authenticate_physical(instance, fixture, report_path=path)


# Independent ALPHA synthetic archive, following S4's same composition.
from tests.b5_analysis.test_floor_kept_units import family, canonical
import shutil
def alpha_indexed_fixture():
    """One cached S2 bracket + S3 roster projection, with explicit rebindings."""
    if "alpha_indexed" in _CACHE:
        return _CACHE["alpha_indexed"]
    from joulewise.b5 import harvest
    from joulewise.flags.catalog import load_catalog
    from joulewise.flags.exclusions import compute
    window = s2.build_named("ALPHA_QUAD_MEMBER_REMOVED")
    old_root = Path(window.entry_data["bound_runs_root"]).parent
    fx._relocate_archive(window.archive, old_root, window.root)
    for field in ("bound_runs_root", "custody_root", "measurement_root"):
        window.entry_data[field] = str(window.root / Path(window.entry_data[field]).relative_to(old_root))
    for source in (window.archive / "sources/claim-runs").iterdir():
        if source.name == "instrument_validation":
            continue  # retain S2's explicit capture stubs
        target = window.claim / source.name
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copyfile(source, target)
    repo = window.archive / "sources/repo"
    pack = repo / "configs/campaigns" / window.entry.pack_id
    spec_path = pack / "extraction_spec.json"
    spec = json.loads(spec_path.read_bytes())
    for cell in spec["cells"]:
        cell["window_class"] = "phase"
        family(cell, "df-b5t-family")
    aliases = copy.deepcopy(spec["cells"])
    for cell in aliases:
        cell["cell_id"] = "p42-" + cell["cell_id"]
        cell["metric"] = "phase_energy_j.prefill"
        cell["target_precheck_path"] = ["phase", "prefill"]
        family(cell, "df-b5t-p42")
    spec["cells"].extend(aliases)
    fx.put(spec_path, spec)
    tree_path = pack / "plan_tree.json"
    tree = json.loads(tree_path.read_bytes())
    tree["downstream_contract"]["extraction_spec"]["sha256"] = fx.sha(spec_path)
    # S0 ALPHA predates the explicit reference-slot stages used by S3.
    for slot in ("start", "midpoint", "end"):
        tree["stage_graph"].append({"stage_id": "s6-" + slot, "ordinal": 10 + len(tree["stage_graph"]),
            "kind": "campaign_collection", "input_ref": {"kind": "external_input", "input_id": slot + "_reference"},
            "spare_retry": {"slot": slot, "members": []}})
    fx.put(tree_path, tree)
    rebuilt = harvest.build_roster(pack, repo)
    projection, _ = harvest.l4_exclusion_inputs(rebuilt, {}, plan_id=window.entry.plan_id, attempt=window.entry.attempt)
    projection.pop("bundles", None)
    projection.pop("chain_started_monotonic_ns", None)
    fx.put(window.archive / "derived/roster.json", projection)
    flags = [json.loads(line) for line in (window.archive / "derived/flags.jsonl").read_bytes().splitlines() if line.strip()]
    exclusions = compute(flags, projection, {}, load_catalog(core.REPO_ROOT / "configs/campaigns/v5_claim_25g83/flag_catalog.json"))
    record = json.loads((window.archive / "harvest.json").read_bytes())
    exclusions["harvest_checkout"] = record["harvest_checkout"]
    fx.put(window.archive / "derived/exclusions.json", exclusions)
    # S2 changed synthetic metadata. Rebind the exact occurrence bytes rather
    # than letting an unrelated basis or unrecorded replacement enter context.
    row_path = window.archive / "sources/claim-runs/whole-window-verdict.json"
    row = json.loads(row_path.read_bytes())
    for occurrence in row["evaluation_basis"]["member_occurrences"]:
        path = window.claim / occurrence["bundle_path"]
        for name, field in (("config.json", "config_sha256"), ("metadata.json", "metadata_sha256"), ("summary_metrics.json", "summary_sha256")):
            occurrence[field] = fx.sha(path / name)
    basis = row["evaluation_basis"]
    basis["sha256"] = ww.canonical_sha256({k: v for k, v in basis.items() if k != "sha256"})
    fx.put(row_path, row)
    fx.put(window.claim / "whole-window-verdict.json", row)
    log_path = window.archive / "sources/claim-runs/campaign_log.jsonl"
    rows = [json.loads(line) for line in log_path.read_bytes().splitlines() if line.strip()]
    rows = [row if item.get("record_type") == "idle_admission_whole_window_verdict" else item for item in rows]
    log_raw = b"".join(canonical(item) + b"\n" for item in rows)
    log_path.write_bytes(log_raw)
    (window.claim / "campaign_log.jsonl").write_bytes(log_raw)
    allowance_path = window.archive / ww.NEG8_HARVEST_ALLOWANCE_RECORD
    allowance = json.loads(allowance_path.read_bytes())
    allowance["verdict"]["row_sha256"] = ww.canonical_sha256(row)
    allowance["verdict"]["evaluation_basis_sha256"] = basis["sha256"]
    fx.put(allowance_path, allowance)
    # Keep the reader's public wrappers in exact agreement with recomputation.
    window_flags = json.loads((window.archive / "derived/window_flags.json").read_bytes())
    window_flags["exclusions"] = {key: exclusions[key] for key in ("claim_usable", "release_blocked", "reasons", "unclassified")}
    fx.put(window.archive / "derived/window_flags.json", window_flags)
    s2.refresh(window)
    temp = tempfile.TemporaryDirectory(prefix="s4-indexed-")
    atexit.register(temp.cleanup)
    directory = Path(temp.name)
    entries = [window.entry_data]
    entries.extend({**window.entry_data, "attempt": attempt, "entry_kind": "no_archive",
        "archive_root": None, "harvest_record_sha256": None, "verdict": "NO_COLLECTION", "claim_usable": False,
        "record_citation": "synthetic-s4-history.md:1"} for attempt in range(1, window.entry.attempt))
    for pack_name in ("beta", "gamma"):
        entry = fx.structural_archive(directory / pack_name, pack=pack_name)
        entries.append({key: str(value) if isinstance(value, Path) else list(value) if isinstance(value, tuple) else value
                        for key, value in entry.__dict__.items()})
    index = directory / "index.json"
    fx.put(index, {"schema": "joulewise.b5_window_index.v1", "attempts": entries})
    local_repo = directory / "repo"
    local_spec = local_repo / "configs/campaigns" / window.entry.pack_id / "extraction_spec.json"
    local_spec.parent.mkdir(parents=True)
    shutil.copyfile(spec_path, local_spec)
    _CACHE["alpha_indexed"] = SimpleNamespace(window=window, index=index, spec=spec, row=row, local_repo=local_repo,
        local_spec=local_spec, directory=directory)
    return _CACHE["alpha_indexed"]


class ComposedSessionSpy(ww.AuthenticatedConsumptionSession):
    calls = []
    summaries = {}

    def __init__(self, root, ids, **kwargs):
        self.calls.append((Path(root), set(ids), kwargs))
        super().__init__(root, ids, **kwargs)
        self.calibration_bracket = ww._archive_thaw(self.archive_context.window_bracket)
        self.operative_fiducial_bound_s = self.calibration_bracket["b_fiducial_s"]
        self._prepared = True
        self._summaries = {bid: self.summaries[bid] for bid in ids}
        self._provenance = {bid: {"operative_fiducial_bound_s": self.operative_fiducial_bound_s} for bid in ids}

    def _prepare(self, **kwargs):
        pass


def alpha_composed_case():
    if "alpha_composed" in _CACHE:
        return _CACHE["alpha_composed"]
    fixture = alpha_indexed_fixture()
    pack = fixture.window.archive / "sources/repo/configs/campaigns" / fixture.window.entry.pack_id
    plan = pack / "calibration_plan.json"
    (pack / "calibration_plan.sha256").write_text(hashlib.sha256(plan.read_bytes()).hexdigest() + "  calibration_plan.json\n")
    fx.put(pack / "order_manifest.json", {"executed_order": [{"run_id": bid} for bid in dict.fromkeys(mint._v2_spec_member_ids(fixture.spec))]})
    for name in ("calibration_plan.json", "calibration_plan.sha256", "order_manifest.json"):
        shutil.copyfile(pack / name, fixture.local_spec.parent / name)
    attempt_id = f"v5-b5-alpha-a{fixture.window.entry_data['attempt']}-test"
    fixture.window.entry_data["plan_id"] = attempt_id
    for relative in ("harvest.json", "derived/roster.json", "derived/exclusions.json"):
        path = fixture.window.archive / relative
        value = json.loads(path.read_bytes())
        value["plan_id"] = attempt_id
        fx.put(path, value)
    flags_path = fixture.window.archive / "derived/window_flags.json"
    flags = json.loads(flags_path.read_bytes())
    flags["window"]["plan_id"] = attempt_id
    fx.put(flags_path, flags)
    s2.refresh(fixture.window)
    index = json.loads(fixture.index.read_bytes())
    for row in index["attempts"]:
        if row["pack"] == "alpha":
            row["plan_id"] = f"v5-b5-alpha-a{row['attempt']}-test"
            if row.get("archive_root") == str(fixture.window.archive):
                row.update(fixture.window.entry_data)
    fx.put(fixture.index, index)
    table = {**fx.PACK_TABLE, "alpha": {fixture.window.entry_data["pack_id"]: "v5-b5-alpha-a{attempt}-"}}
    with s2.capture_adapter():
        entry = mint.compose_indexed_producers(fixture.index, seal_pins=SealPins.load(), pack_table=table,
            test_only_allow_synthetic_binding=True, repo_root=fixture.local_repo, packs=("alpha",))["alpha"]
    _CACHE["alpha_composed"] = fixture, entry
    return fixture, entry


def legacy_manifest_case():
    if "legacy_manifest" not in _CACHE:
        temp = tempfile.TemporaryDirectory(prefix="s6-legacy-manifest-")
        atexit.register(temp.cleanup)
        root = Path(temp.name)
        pinset_path, digest, manifest_path, loader = old.install_v2_cli_fixture(root)
        _CACHE["legacy_manifest"] = SimpleNamespace(root=root, pinset_path=pinset_path, digest=digest,
            manifest_path=manifest_path, manifest=json.loads(manifest_path.read_bytes()), loader=loader)
    return _CACHE["legacy_manifest"]


class LegacyContinuationTests(unittest.TestCase):
    def test_v2_r13_third_legacy_cell_is_refused(self):
        fixture = legacy_manifest_case()
        manifest = copy.deepcopy(fixture.manifest)
        manifest["producer_plans"][0]["cells"].append(copy.deepcopy(manifest["producer_plans"][0]["cells"][0]))
        with mock.patch.object(mint, "_fresh_original_core", side_effect=fixture.loader), \
             self.assertRaisesRegex(mint.MintError, "must contain two cells"):
            mint._authenticate_v2_inputs(pinset=mint.load_pinset(fixture.pinset_path, fixture.digest),
                pinset_path=fixture.pinset_path, pinset_sha256=fixture.digest, input_manifest_path=fixture.manifest_path,
                input_manifest=manifest, strict_validator=lambda *_: (), consumption_semantics_id=None)

    def test_v2_c3_legacy_manifest_hazard_root_through_public_mint(self):
        fixture = legacy_manifest_case()
        manifest = copy.deepcopy(fixture.manifest)
        hazard_root = Path(manifest["producer_plans"][0]["cells"][0]["absolute"]["evidence_root"])
        path = fixture.root / "hazard-manifest.json"
        path.write_bytes(mint._artifact_payload(manifest))
        floor, statement = fixture.root / "hazard-floor.json", fixture.root / "hazard-statement.md"
        with mock.patch.object(mint, "_fresh_original_core", side_effect=fixture.loader), \
             mock.patch.object(mint, "_actual_v2_git_state", return_value=("0"*40, False)), \
             mock.patch.object(ww, "_is_hazard_runs_root", side_effect=lambda root: Path(root).resolve() == hazard_root.resolve()), \
             self.assertRaisesRegex(mint.MintError, "^window_index_required$"):
            mint.mint_multi_cell_floor_artifact(pinset_path=fixture.pinset_path, pinset_sha256=fixture.digest,
                input_manifest_path=path, floor_path=floor, statement_path=statement,
                project_commit="0"*40, project_tree_state="clean", strict_validator=lambda *_: ())
        self.assertFalse(floor.exists())
        self.assertFalse(statement.exists())


def public_arithmetic_case():
    """Materialize the arithmetic fixture for the real pinned binder."""
    if "public_arithmetic" in _CACHE:
        return _CACHE["public_arithmetic"]
    temp = tempfile.TemporaryDirectory(prefix="s6-public-arithmetic-")
    atexit.register(temp.cleanup)
    directory = Path(temp.name)
    fixture = common_case()
    entries, inputs = {}, {}
    snapshots = copy.deepcopy(fixture.snapshots)
    for index, (pid, source) in enumerate(fixture.inputs.items()):
        root = directory / f"producer-{index}"
        full_source = case("all").inputs[pid]
        for kind in ("absolute", "comparative"):
            (directory / f"producer-{index}-inputs-{kind}").mkdir()
            old._install_component_fixture(directory / f"producer-{index}-inputs-{kind}", kind,
                getattr(full_source.cells["decode"], kind), evidence_root=root)
        plan_raw = mint._artifact_payload(source.plan)
        plan_hash = hashlib.sha256(plan_raw).hexdigest()
        sidecar_hash = hashlib.sha256((plan_hash + "  calibration_plan.json\n").encode()).hexdigest()
        binding, _receipts, observations, session = old._synthetic_bracket_evidence(index, plan_id=pid,
            plan_sha256=plan_hash, evidence_root_id=source.cells["decode"].absolute.evidence_root_id,
            runs_root=root, sequence_start=1+3*index)
        snapshot = snapshots[pid]
        snapshot.observations = tuple(observations)
        snapshot.bracket_session_by_id = {session.session_id: session}
        bracket = ww._archive_thaw(fixture.entries[str(source.evidence_root.resolve())].archive_context.window_bracket)
        bracket.update(old._synthetic_verdict_bracket(observations))
        entry = fixture.entries[str(source.evidence_root.resolve())]
        entry = SimpleNamespace(**{**vars(entry), "window": SimpleNamespace(**{**vars(entry.window), "claim_runs_root": root}),
            "archive_context": ww.ArchiveContext(root, window_bracket=bracket), "ledger_snapshot":snapshot,
            "window_bracket":synthetic_bracket(entry.window, bracket)})
        archive_root = directory / (entry.window.pack + "-archive")
        pack_path = directory / (entry.window.pack + "-pack")
        pack_path.mkdir()
        (pack_path / "calibration_plan.json").write_bytes(plan_raw)
        pinned = {"sources/inputs/acceptance.json":mint._artifact_payload(source.calibration_acceptance),
                  "derived/bracket-binding.json":mint._artifact_payload(binding)}
        for relative, raw in pinned.items():
            path = archive_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        entry = SimpleNamespace(**{**vars(entry), "window":SimpleNamespace(**{**vars(entry.window), "archive_root":archive_root}),
            "pack_path":pack_path, "archive":SimpleNamespace(source_bytes=lambda relative, data=pinned:data[relative],
                output_bytes=lambda relative, data=pinned:data[relative])})
        entries[str(root.resolve())] = entry
        kept = core._producer_bundle_ids(entry)
        comparative = source.cells["decode"].comparative
        original_values = {m.bundle_id:m.metric_value_j for m in comparative.members}
        nonnegative_values = {}
        for block in comparative.spec_cell["blocks"]:
            if not set(block["members"].values()) <= kept:
                continue
            delta = df.abba_delta(*(original_values[block["members"][p]] for p in core._ABBA_POSITIONS))
            values = (0.0, 2*delta, 0.0, 0.0) if delta >= 0 else (-2*delta, 0.0, 0.0, 0.0)
            nonnegative_values.update(zip((block["members"][p] for p in core._ABBA_POSITIONS), values, strict=True))
        for bid in kept:
            path = root / bid / "summary_metrics.json"
            summary = json.loads(path.read_bytes())
            if bid in nonnegative_values:
                value = nonnegative_values[bid]
                summary["phase_energy_j"]["decode"] = value
                summary["energy_anchor_shift_envelopes"]["/phase_energy_j/decode"]["point_j"] = value
            summary["phase_energy_j"]["prefill"] = summary["phase_energy_j"]["decode"]
            summary["energy_anchor_shift_envelopes"]["/phase_energy_j/prefill"] = copy.deepcopy(summary["energy_anchor_shift_envelopes"]["/phase_energy_j/decode"])
            summary["window_evidence_precheck"]["phase"]["prefill"] = copy.deepcopy(summary["window_evidence_precheck"]["phase"]["decode"])
            for envelope in summary["energy_anchor_shift_envelopes"].values():
                value, width = envelope["point_j"], envelope["max_abs_delta_j"]
                envelope["lower_j"] = math.nextafter(value-width, value) if width else value
                envelope["upper_j"] = math.nextafter(value+width, value) if width else value
            path.write_bytes(mint._artifact_payload(summary))
        removed = entry.kept_units.removed_run_ids()
        for bid in removed:
            if (root / bid).exists():
                shutil.rmtree(root / bid)
        report = copy.deepcopy(source.cells["decode"].absolute.report)
        report["runs_root"] = str(root)
        pairs = {}
        for role, pair in source.cells.items():
            changed = []
            for component in (pair.absolute, pair.comparative):
                cell = next(c for c in report["cells"] if c["cell_id"] == component.calibration_cell_id)
                members = []
                for row in cell["members"]:
                    if row["excluded"]:
                        continue
                    bid = row["bundle_id"]
                    summary = json.loads((root / bid / "summary_metrics.json").read_bytes())
                    row["metric_value_j"] = summary["phase_energy_j"][role]
                    row["anchor_shift_bound_j"] = summary["energy_anchor_shift_envelopes"]["/phase_energy_j/" + role]["max_abs_delta_j"]
                    row["bundle_sha256"] = df.complete_bundle_sha256(root / bid)
                    row["config_sha256"] = hashlib.sha256((root / bid / "config.json").read_bytes()).hexdigest()
                    members.append(core.AuthenticatedMember(bundle_id=bid, bundle_sha256=row["bundle_sha256"], config_sha256=row["config_sha256"],
                        metric_value_j=row["metric_value_j"], raw_config=json.loads((root / bid / "config.json").read_bytes()),
                        metadata={}, summary=summary, admissible_half_width_j=row["anchor_shift_bound_j"]))
                original_core = mint._fresh_original_core()
                original_core.build_stack_identity = lambda *_: old.stack_identity()
                original_core.scientific_config_identity = lambda *_: {"synthetic": "same"}
                regime, scientific, backend = original_core._source_regime(members)
                component = replace(component, members=tuple(members), cell=cell, source_regime=regime,
                    scientific_config_identity_sha256=scientific, backend=backend,
                    whole_window_calibration_bracket=bracket,
                    order_manifest={**component.order_manifest, "calibration_plan_sha256":plan_hash},
                    campaign_log_sha256=hashlib.sha256((root / "campaign_log.jsonl").read_bytes()).hexdigest())
                changed.append(component)
            pairs[role] = replace(pair, absolute=changed[0], comparative=changed[1])
        raw = mint._artifact_payload(report)
        for role, pair in pairs.items():
            pairs[role] = replace(pair, absolute=replace(pair.absolute, report=report, report_sha256=hashlib.sha256(raw).hexdigest()),
                comparative=replace(pair.comparative, report=report, report_sha256=hashlib.sha256(raw).hexdigest()))
        inputs[pid] = replace(source, cells=pairs, evidence_root=root, plan_sha256=plan_hash, plan_declared_sha256=plan_hash,
            plan_sidecar_sha256=sidecar_hash, bracket_binding=binding, bracket_binding_sha256=hashlib.sha256(mint._artifact_payload(binding)).hexdigest(),
            authenticated_pre_observation=observations[0], authenticated_post_observation=observations[1])
    result = SimpleNamespace(pins=copy.deepcopy(fixture.pins), entries=entries, inputs=inputs,
        snapshots=snapshots, directory=directory)
    _CACHE["public_arithmetic"] = result
    return result


class PublicContinuationTests(unittest.TestCase):
    def test_v3_build_pinset_then_public_indexed_mint(self):
        fixture = public_arithmetic_case()
        with tempfile.TemporaryDirectory(prefix="s6-public-chain-") as tmp:
            root = Path(tmp)
            pinset_path = root / "floor-mint-pinset.json"
            with registered(fixture.entries), common_seams():
                pins = emit.build_pinset(contracts=contracts_from_pins(fixture.pins), producer_inputs=fixture.inputs,
                    ledger_snapshot=fixture.snapshots, relative_plan_paths=[e.window.pack + "/calibration_plan.json" for e in fixture.entries.values()],
                    pinset_path=pinset_path, project_commit="0"*40,
                    kept_units={e.producer_plan_id: e.kept_units for e in fixture.entries.values()},
                    window_brackets={e.producer_plan_id: e.archive_context.window_bracket for e in fixture.entries.values()})
            plans = {e.window.pack: mint._artifact_payload(fixture.inputs[e.producer_plan_id].plan) for e in fixture.entries.values()}
            manifest = block5_manifest(fixture)
            digest = emit._write_block5_outputs(root, pins, manifest, plans)
            self.assertEqual(sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()),
                ["alpha/calibration_plan.json", "beta/calibration_plan.json", "floor-mint-inputs.json", "floor-mint-pinset.json"])
            self.assertEqual(set(manifest), {"schema_version", "producer_plans"})
            for row, entry in zip(manifest["producer_plans"], fixture.entries.values(), strict=True):
                self.assertEqual(set(row), {"plan_id", "pack", "exclusions_sha256", "report", "cells"})
                self.assertEqual(row["plan_id"], entry.producer_plan_id)
                self.assertNotEqual(row["plan_id"], entry.window.plan_id)
            original_loader = mint._fresh_original_core
            def loader():
                instance = original_loader()
                instance.AuthenticatedConsumptionSession = SessionSpy
                instance.whole_window_refusal_reasons = lambda *_args, **_kwargs: ()
                instance.build_stack_identity = lambda *_: old.stack_identity()
                instance.scientific_config_identity = lambda *_: {"synthetic": "same"}
                return instance
            SessionSpy.summaries = {m.bundle_id: m.summary for s in fixture.inputs.values() for pair in s.cells.values()
                                    for component in (pair.absolute, pair.comparative) for m in component.members}
            roots = {p["evidence_root_id"]: fixture.inputs[p["plan"]["plan_id"]].evidence_root for p in pins["producer_plans"]}
            with common_seams(), mock.patch.object(mint, "_fresh_original_core", side_effect=loader), \
                 mock.patch.object(mint, "compose_indexed_producers", return_value={e.window.pack: e for e in fixture.entries.values()}), \
                 mock.patch.object(mint, "_actual_v2_git_state", return_value=("0"*40, False)), \
                 mock.patch.object(mint, "_authenticate_v2_inputs", return_value=(fixture.inputs, roots, fixture.snapshots)):
                artifact = mint.mint_multi_cell_floor_artifact(pinset_path=pinset_path, pinset_sha256=digest,
                    input_manifest_path=root / "floor-mint-inputs.json", window_index=Path("arithmetic-index.json"),
                    floor_path=root / "floor.json", statement_path=root / "statement.md", d165_replay_out=root / "replay.json",
                    project_commit="0"*40, project_tree_state="clean", strict_validator=lambda *_: ())
            for name in ("floor.json", "statement.md", "replay.json"):
                self.assertTrue((root / name).is_file())
            self.assertEqual(df.validate_floor_artifact(artifact, pinset_path=pinset_path, expected_pinset_sha256=digest), [])
            for producer in pins["producer_plans"]:
                for cell in producer["cells"]:
                    self.assertEqual(cell["postcollection"]["terminal_ledger_head_sha256"], fixture.snapshots[producer["plan"]["plan_id"]].head_digest)
            self.assertFalse(mint.BLOCK5_PRODUCERS)


def composed_manual_report(pack):
    """Fallback report over the composed window's spec, kept units and summaries.

    The lane's mock report cannot be admitted; no producer artifact is issued here.
    All numbers are synthetic. The copied allowance is marked test construction.
    """
    key = "composed_manual", pack
    if key in _CACHE:
        return _CACHE[key]
    fixture, entry = governed_case() if pack == "beta" else alpha_composed_case()
    instance = mint._fresh_original_core()
    spec = copy.deepcopy(fixture.spec)
    bindings, ids = instance._kept_spec_bindings(spec, entry)
    template = next(iter(case().inputs.values())).cells["decode"].absolute
    basis = entry.verdict_row["evaluation_basis"]["sha256"]
    components, cells = {}, []
    for cell in spec["cells"]:
        if cell["cell_id"].startswith("p42-"):
            # The binding keeps all spec cells, but a p42 cell is never minted.
            continue
        instance.METRIC = cell["metric"]
        selected = bindings[cell["cell_id"]]
        removed = set(selected["removed_unit_ids"])
        layout = ([(m["bundle_id"], [(m["bundle_id"], None)]) for m in cell["members"]] if cell["kind"] == "absolute" else
            [(b["block_id"], [(b["members"][p], p) for p in core._ABBA_POSITIONS]) for b in cell["blocks"]])
        rows, members = [], []
        for uid, unit in layout:
            for bid, position in unit:
                if uid in removed:
                    rows.append(fe._unevaluated_member(slot=bid, bundle_id=bid,
                        block_id=uid if position else None, position=position).as_row())
                    continue
                path = entry.window.claim_runs_root / bid
                summary = json.loads((path / "summary_metrics.json").read_bytes())
                row = {"slot": bid, "bundle_id": bid, "block_id": uid if position else None, "position": position,
                    "metric_value_j": instance._metric_value(summary), "anchor_shift_bound_j": instance._source_admissible_half_width(summary, bid),
                    "excluded": False, "reasons": [], "cooldown_result": "completed", "cooldown_verified": True, "cap_hit": False,
                    "operative_anchor_envelope": None, "summary_sha256": hashlib.sha256((path / "summary_metrics.json").read_bytes()).hexdigest(),
                    "bundle_sha256": df.complete_bundle_sha256(path), "config_sha256": hashlib.sha256((path / "config.json").read_bytes()).hexdigest(),
                    "consumption_provenance": {"operative_fiducial_bound_s": entry.window_bracket.b_fiducial_s}}
                rows.append(row)
                members.append(instance._strict_bundle(entry.window.claim_runs_root, bid, row, lambda *_: (), operative_summary=summary))
        provisional = {"members": rows}
        _kept_rows, widths = instance._report_members(provisional, cell, cell["kind"], removed_unit_ids=frozenset(removed))
        allowance = {**template.whole_window_drift_allowance, "whole_window_evaluation_basis_sha256": basis}
        try:
            regime, scientific, backend = instance._source_regime(members)
        except instance.MintError:
            # Keep the refusal visible when the call below needs source regime.
            regime, scientific, backend = template.source_regime, template.scientific_config_identity_sha256, template.backend
        component = replace(template, evidence_root_id="synthetic-"+pack, calibration_cell_id=cell["cell_id"], kind=cell["kind"],
            spec=spec, spec_cell=cell, members=tuple(members), widths_j=tuple(widths),
            source_regime=regime, scientific_config_identity_sha256=scientific, backend=backend,
            whole_window_evaluation_basis_sha256=basis, evaluation_basis_member_count=len(entry.verdict_row["evaluation_basis"]["member_occurrences"]),
            whole_window_drift_allowance=allowance, whole_window_calibration_bracket=ww._archive_thaw(entry.archive_context.window_bracket),
            campaign_log_sha256=hashlib.sha256((entry.window.claim_runs_root / "campaign_log.jsonl").read_bytes()).hexdigest(),
            order_manifest={"manifest_id":"s6-composed-order", "executed_order":[{"run_id": bid} for bid in dict.fromkeys(core._spec_member_ids(spec))]})
        if cell["kind"] == "absolute":
            estimate = df.absolute_false_effect_floor([m.metric_value_j for m in members], admissible_half_widths_j=widths)
        else:
            by_id = {m.bundle_id:m.metric_value_j for m in members}
            deltas = [df.abba_delta(*(by_id[b["members"][p]] for p in core._ABBA_POSITIONS))
                      for b in cell["blocks"] if b["block_id"] not in removed]
            estimate = df.comparative_false_effect_floor(deltas, admissible_half_widths_j=widths)
        cell_report = old._production_report_cell(component, estimate=estimate)
        cell_report.update(members=rows, excluded_slots=sorted(removed), n_planned=len(layout), n_admitted=len(widths))
        components[cell["kind"]] = replace(component, cell=cell_report)
        cells.append(cell_report)
    report = copy.deepcopy(template.report)
    report.update(runs_root=str(entry.window.claim_runs_root), cells=cells,
        kept_units_binding={"schema_version":"joulewise.floor_extraction_kept_units.v1", "exclusions_sha256":entry.kept_units.exclusions_sha256,
            "catalog_sha256":entry.kept_units.catalog_sha256, "harvest_pin":entry.window.harvest_pin, "sensitivity_label":None, "cells":bindings})
    directory = fixture.directory / "s6-composed-report"
    directory.mkdir(exist_ok=True)
    report_path = directory / "report.json"
    raw = mint._artifact_payload(report)
    report_path.write_bytes(raw)
    order_path = directory / "order.json"
    order_path.write_bytes(mint._artifact_payload(components["absolute"].order_manifest))
    for kind, component in components.items():
        components[kind] = replace(component, report=report, report_sha256=hashlib.sha256(raw).hexdigest(),
            spec_sha256=hashlib.sha256(fixture.local_spec.read_bytes()).hexdigest(),
            order_manifest_sha256=hashlib.sha256(order_path.read_bytes()).hexdigest())
    result = SimpleNamespace(fixture=fixture, entry=entry, components=components, report_path=report_path, order_path=order_path,
        ids=ids, directory=directory)
    _CACHE[key] = result
    return result


class ComposedContinuationTests(unittest.TestCase):
    def test_v1_real_compositions_and_exact_unadmitted_report_refusals(self):
        for pack in ("beta", "alpha"):
            fixture, entry = governed_case() if pack == "beta" else alpha_composed_case()
            ids = core._producer_bundle_ids(entry)
            ComposedSessionSpy.calls.clear()
            ComposedSessionSpy.summaries = {bid: json.loads((entry.window.claim_runs_root / bid / "summary_metrics.json").read_bytes()) for bid in ids}
            with self.subTest(pack=pack), s2.capture_adapter(), \
                 mock.patch.object(fe, "AuthenticatedConsumptionSession", ComposedSessionSpy), \
                 mock.patch.object(fe, "whole_window_refusal_reasons", return_value=()), \
                 mock.patch.object(ww, "whole_window_refusal_reasons", return_value=()):
                report = fe.extract_cells(entry.window.claim_runs_root, fixture.spec, kept_units=entry.kept_units,
                    archive_context=entry.archive_context, evaluation_basis_sha256=entry.verdict_row["evaluation_basis"]["sha256"],
                    consumption_semantics_id=ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID, mode="read_replay", calibration_ledger_snapshot=entry.ledger_snapshot)
            self.assertEqual(entry.archive_context.governed_e3, pack == "beta")
            self.assertEqual(ww._archive_thaw(entry.archive_context.window_bracket), {**ww._archive_thaw(entry.window_bracket.evaluation), "reasons": []})
            self.assertFalse(report["cells"][0]["extractable"])
            self.assertIn("whole_window_drift_allowance_unrecorded", report["cells"][0]["refusal_reasons"])
            self.assertEqual(len(ComposedSessionSpy.calls), 1)
            root, actual_ids, kwargs = ComposedSessionSpy.calls[0]
            self.assertEqual((root, actual_ids), (entry.window.claim_runs_root, ids))
            self.assertIs(kwargs["archive_context"], entry.archive_context)
            self.assertFalse(actual_ids & entry.kept_units.removed_run_ids())


class IndexedEmitterContinuationTests(unittest.TestCase):
    def test_f1_indexed_emitter_routes_producer_identity(self):
        fixture = public_arithmetic_case()
        contracts = contracts_from_pins(fixture.pins)
        by_pack = {e.window.pack:e for e in fixture.entries.values()}
        triples = []
        for contract, producer in zip(contracts, fixture.pins["producer_plans"], strict=True):
            triples.append((contract, producer, {"cells":[{"role":c["role"],
                "allowed_consumer_condition_families":c["allowed_consumer_condition_families"]} for c in producer["cells"]]}))
        original_loader=mint._fresh_original_core
        def loader():
            instance=original_loader()
            instance.load_calibration_acceptance_bound=lambda *_: next(iter(fixture.inputs.values())).calibration_acceptance
            return instance
        with tempfile.TemporaryDirectory(prefix="s6-emitter-identity-") as tmp, \
             mock.patch.object(mint,"_fresh_original_core",side_effect=loader), \
             mock.patch.object(estimator,"AuthenticatedConsumptionSession",SessionSpy), \
             mock.patch.object(estimator,"whole_window_refusal_reasons",return_value=()), \
             mock.patch.object(fe,"_common_mode_block_inputs_from_evidence",new=common_block_input), \
             mock.patch.object(mint, "compose_indexed_producers", return_value={**by_pack,"gamma":SimpleNamespace(pack_path=Path(tmp))}), \
             mock.patch.object(emit, "_consumer_bindings", return_value={}), \
             mock.patch.object(emit, "_bootstrap_producer", side_effect=triples), \
             mock.patch.object(mint, "_authenticate_v2_inputs", return_value=(fixture.inputs, {}, fixture.snapshots)) as authenticate:
            root = Path(tmp)
            emit.emit_indexed_pinset(window_index=Path("synthetic-index.json"),alpha_report=Path("alpha-report.json"),
                beta_report=Path("beta-report.json"),out_dir=root,project_commit="0"*40)
            manifest = json.loads((root / "floor-mint-inputs.json").read_bytes())
            self.assertEqual([row["plan_id"] for row in manifest["producer_plans"]], [e.producer_plan_id for e in fixture.entries.values()])
            self.assertEqual(authenticate.call_args.kwargs["input_manifest"], manifest)
            self.assertEqual(sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()),
                ["alpha/calibration_plan.json", "beta/calibration_plan.json", "floor-mint-inputs.json", "floor-mint-pinset.json"])
        self.assertFalse(mint.BLOCK5_PRODUCERS)

    def test_ca_emitter_changed_archive_inputs(self):
        fixture = public_arithmetic_case()
        by_pack = {e.window.pack:e for e in fixture.entries.values()}
        entry = by_pack["alpha"]
        for relative in ("sources/inputs/acceptance.json", "derived/bracket-binding.json"):
            path = entry.window.archive_root / relative
            original = path.read_bytes()
            try:
                path.write_bytes(original + b"\n")
                with self.subTest(relative=relative), tempfile.TemporaryDirectory(prefix="s6-emitter-changed-") as tmp, \
                     mock.patch.object(mint, "compose_indexed_producers", return_value={**by_pack,"gamma":SimpleNamespace(pack_path=Path(tmp))}), \
                     mock.patch.object(emit, "_consumer_bindings", return_value={}), \
                     self.assertRaisesRegex(mint.MintError,"^archive_input_changed_after_authentication"):
                    emit.emit_indexed_pinset(window_index=Path("synthetic-index.json"),alpha_report=Path("alpha-report.json"),
                        beta_report=Path("beta-report.json"),out_dir=Path(tmp),project_commit="0"*40)
            finally:
                path.write_bytes(original)
        self.assertFalse(mint.BLOCK5_PRODUCERS)

    def test_v3_composed_synthetic_packs_lack_bootstrap_contract(self):
        for pack in ("beta", "alpha"):
            fixture, entry = governed_case() if pack == "beta" else alpha_composed_case()
            self.assertFalse((entry.pack_path / "producer_contract.json").exists())
            with self.subTest(pack=pack), tempfile.TemporaryDirectory(prefix="s6-bootstrap-limit-") as tmp:
                root=Path(tmp)
                prefix=f"sources/repo/configs/campaigns/{entry.window.pack_id}/"
                raw=entry.archive.source_bytes(prefix+"plan_tree.json")
                (root/"plan_tree.json").write_bytes(raw)
                (root/"plan_tree.sha256").write_text(hashlib.sha256(raw).hexdigest()+"  plan_tree.json\n")
                with self.assertRaisesRegex(mint.MintError,"producer_contract.json cannot be read"):
                    emit._bootstrap_producer(root,entry.window.claim_runs_root,fixture.directory/"absent-report.json",
                        entry.window.archive_root/"derived/bracket-binding.json",{}, {},"0"*64,entry.ledger_snapshot,
                        pack+"/calibration_plan.json","prefill_p2048",kept_units=entry.kept_units)


class ComposedSessionSiteTests(unittest.TestCase):
    def test_v1_first_and_fourth_sites_keep_real_context_until_fixture_refusal(self):
        from joulewise.detection_floor import CommonModeEstimatorRefusal
        import builtins
        for pack in ("beta", "alpha"):
            fixture = composed_manual_report(pack)
            entry = fixture.entry
            root = entry.window.claim_runs_root
            ComposedSessionSpy.summaries = {bid:json.loads((root/bid/"summary_metrics.json").read_bytes()) for bid in fixture.ids}
            opened=[]
            original_open=builtins.open
            original_path_open=Path.open
            def record_open(path, *args, **kwargs):
                if isinstance(path, (str, Path)):
                    opened.append(Path(path).resolve())
                return original_open(path, *args, **kwargs)
            def record_path_open(path, *args, **kwargs):
                opened.append(path.resolve())
                return original_path_open(path, *args, **kwargs)
            with self.subTest(pack=pack), registered({str(root.resolve()):entry}), V2AuthenticationReadSession():
                instance=mint._fresh_original_core()
                instance.PLAN_SHA256=hashlib.sha256((entry.pack_path/"calibration_plan.json").read_bytes()).hexdigest()
                with mock.patch.object(instance,"AuthenticatedConsumptionSession",ComposedSessionSpy), \
                     mock.patch.object(instance,"whole_window_refusal_reasons",return_value=()), \
                     mock.patch.object(estimator,"AuthenticatedConsumptionSession",ComposedSessionSpy), \
                     mock.patch.object(estimator,"whole_window_refusal_reasons",return_value=()), \
                     mock.patch.object(builtins,"open",new=record_open), mock.patch.object(Path,"open",new=record_path_open):
                    for kind,component in fixture.components.items():
                        ComposedSessionSpy.calls.clear()
                        with self.assertRaisesRegex(instance.MintError,"source calibration-plan tag mismatch$"):
                            instance._authenticate_component(instance.ComponentPaths(component.evidence_root_id,root,fixture.report_path,
                                fixture.fixture.local_spec,fixture.order_path,component.calibration_cell_id,kind),
                                expected_cell_id=component.calibration_cell_id,expected_basis_sha256=entry.verdict_row["evaluation_basis"]["sha256"],
                                strict_validator=lambda *_:(),calibration_ledger_snapshot=entry.ledger_snapshot,
                                expected_consumption_semantics_id=ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID)
                        self.assertEqual(len(ComposedSessionSpy.calls),1)
                        actual_root,ids,kwargs=ComposedSessionSpy.calls[0]
                        self.assertEqual((actual_root,ids),(root,fixture.ids))
                        self.assertIs(kwargs["archive_context"],entry.archive_context)
                        self.assertEqual(component.whole_window_calibration_bracket,ww._archive_thaw(entry.archive_context.window_bracket))
                    acceptance_raw=entry.archive.source_bytes("sources/inputs/acceptance.json")
                    acceptance=json.loads(acceptance_raw)
                    acceptance_hash=hashlib.sha256(acceptance_raw).hexdigest()
                    bracket=ww._archive_thaw(entry.archive_context.window_bracket)
                    session=entry.ledger_snapshot.bracket_session_by_id[bracket["pre"]["bracket_session_id"]]
                    projection=mint._v2_allowance_projection(SimpleNamespace(calibration_acceptance=acceptance,evidence_root=root),
                        session.finalized_slots["pre"],session.finalized_slots["post"])
                    comparative=fixture.components["comparative"]
                    spec_cell={**comparative.spec_cell,"estimator":df.COMMON_MODE_ESTIMATOR_ID,
                        "estimator_registration":df.two_shared_edge_common_mode_registration(),
                        "calibration_basis":old._mixed_calibration_basis(SimpleNamespace(calibration_acceptance=acceptance,
                            calibration_acceptance_sha256=acceptance_hash))}
                    comparative=replace(comparative,spec_cell=spec_cell,spec={**comparative.spec,"cells":[
                        spec_cell if c["cell_id"]==spec_cell["cell_id"] else c for c in comparative.spec["cells"]]})
                    ComposedSessionSpy.calls.clear()
                    with self.assertRaisesRegex(CommonModeEstimatorRefusal,"one nonnegative interval-support phase window is required$"):
                        estimator.recompute_comparative_estimate(core=instance,comparative_component=comparative,runs_root=root,
                            calibration_acceptance=acceptance,calibration_acceptance_sha256=acceptance_hash,
                            calibration_allowance_projection=projection,declared_calibration_scope="production_window",
                            calibration_ledger_snapshot=entry.ledger_snapshot,calibration_bracket_binding=bracket["bracket_binding"])
                    self.assertEqual(len(ComposedSessionSpy.calls),1)
                    actual_root,ids,kwargs=ComposedSessionSpy.calls[0]
                    self.assertEqual((actual_root,ids),(root,fixture.ids))
                    self.assertIs(kwargs["archive_context"],entry.archive_context)
            removed=entry.kept_units.removed_run_ids()
            self.assertFalse(any(path.is_relative_to(root) and path.relative_to(root).parts[0] in removed for path in opened),
                (pack, sorted({str(path.relative_to(root)) for path in opened if path.is_relative_to(root) and path.relative_to(root).parts[0] in removed})))
            if pack=="beta":
                self.assertEqual(entry.verdict_row["evaluation_basis"]["calibration_bracket_set"],{"pre":None,"post":None})


class ProducerIdentityContinuationTests(unittest.TestCase):
    def test_f1_all_existing_plan_declarations_must_agree(self):
        with tempfile.TemporaryDirectory(prefix="s6-plan-identity-") as tmp:
            pack=Path(tmp)
            data={"calibration_plan.json":mint._artifact_payload({"plan_id":"producer-plan"}),
                "plan_tree.json":mint._artifact_payload({"plan":{"plan_id":"producer-plan"}}),
                "producer_contract.json":mint._artifact_payload({"plan":{"plan_id":"wrong-producer"}})}
            (pack/"plan_tree.json").write_bytes(data["plan_tree.json"])
            (pack/"producer_contract.json").write_bytes(data["producer_contract.json"])
            archive=SimpleNamespace(plan_tree_binding_kind="sealed",source_bytes=lambda relative:data[relative])
            with self.assertRaisesRegex(AnalysisRefusal,"^producer_plan_identity_mismatch$"):
                mint._producer_plan_identity(pack,archive,"")
            (pack/"producer_contract.json").unlink()
            with self.assertRaisesRegex(AnalysisRefusal,"^producer_plan_identity_mismatch$"):
                mint._producer_plan_identity(pack,archive,"")
            archive.plan_tree_binding_kind="synthetic"
            self.assertEqual(mint._producer_plan_identity(pack,archive,""),"producer-plan")


# Append-only B1 fixture adapter: old test bodies continue to use case().
_case_with_attempt_identity = case


def case(name="t1", *, minimum=5, target=True):
    fixture = _case_with_attempt_identity(name, minimum=minimum, target=target)
    for entry in fixture.entries.values():
        if not hasattr(entry, "window_bracket"):
            entry.window_bracket = synthetic_bracket(entry.window, entry.archive_context.window_bracket)
    return fixture


class InitialArchiveOwnerContinuationTests(unittest.TestCase):
    def test_f1_initial_archive_owner_does_not_follow_manifest_order(self):
        fixture=public_arithmetic_case()
        manifest=block5_manifest(fixture)
        manifest["producer_plans"].reverse()
        pins=copy.deepcopy(fixture.pins)
        for producer in pins["producer_plans"]:
            source=fixture.inputs[producer["plan"]["plan_id"]]
            producer["plan"].update(sha256=source.plan_sha256,declared_sha256=source.plan_sha256,
                sidecar_sha256=source.plan_sidecar_sha256)
        old._repair_v2_pinset_self_hashes(pins)
        original_loader=mint._fresh_original_core
        def loader():
            instance=original_loader()
            instance.load_calibration_acceptance_bound=lambda *_: next(iter(fixture.inputs.values())).calibration_acceptance
            return instance
        seen=[]
        authenticate=mint._authenticate_archive_input
        def record(entry, relative, raw):
            if relative=="sources/inputs/acceptance.json":
                seen.append(entry.window.pack)
            return authenticate(entry,relative,raw)
        with registered(fixture.entries),mock.patch.object(mint,"_fresh_original_core",side_effect=loader), \
             mock.patch.object(mint,"_authenticate_archive_input",side_effect=record), \
             self.assertRaisesRegex(mint.MintError,"plan sidecar cannot be read"):
            mint._authenticate_v2_inputs(pinset=mint._parse_v2_pinset(pins),pinset_path=fixture.directory/"pinset.json",
                pinset_sha256="0"*64,input_manifest_path=fixture.directory/"inputs.json",input_manifest=manifest,
                strict_validator=lambda *_:(),consumption_semantics_id=None)
        self.assertEqual(seen[:3],["beta","alpha","alpha"])


class ChangedArchiveGrammarContinuationTests(unittest.TestCase):
    def test_ca_emitter_changed_non_json_input_is_bound_before_parse(self):
        fixture=public_arithmetic_case()
        by_pack={e.window.pack:e for e in fixture.entries.values()}
        entry=by_pack["alpha"]
        for relative in ("sources/inputs/acceptance.json","derived/bracket-binding.json"):
            path=entry.window.archive_root/relative
            original=path.read_bytes()
            try:
                path.write_bytes(b"changed input is not JSON")
                with self.subTest(relative=relative),tempfile.TemporaryDirectory(prefix="s6-emitter-grammar-") as tmp, \
                     mock.patch.object(mint,"compose_indexed_producers",return_value={**by_pack,"gamma":SimpleNamespace(pack_path=Path(tmp))}), \
                     mock.patch.object(emit,"_consumer_bindings",return_value={}), \
                     self.assertRaisesRegex(mint.MintError,"^archive_input_changed_after_authentication"):
                    emit.emit_indexed_pinset(window_index=Path("synthetic-index.json"),alpha_report=Path("alpha-report.json"),
                        beta_report=Path("beta-report.json"),out_dir=Path(tmp),project_commit="0"*40)
            finally:
                path.write_bytes(original)
