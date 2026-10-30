"""S4 arithmetic and structural tripwires; every input is synthetic.

Expensive lane windows and the arithmetic corpus are cached once per module.
Counterfactuals copy only small arithmetic bundles or structural archive files.
"""
import atexit
import contextlib
import copy
from dataclasses import replace
import hashlib
import io
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise import floor_extraction as fe, whole_window as ww, window_lineage as wl
from joulewise.b5_analysis.kept_units import CellKeptUnits, DroppedUnit, KeptUnits, Unit
from joulewise.b5_analysis.windows import AnalysisRefusal, SealPins
from joulewise.b5_analysis.steps import classify_step4_exit
from joulewise.detection_floor import canonical_domain_sha256, CONDITION_FAMILY_DOMAIN, two_shared_edge_common_mode_registration
from scripts import extract_detection_floors as cli
from tests import test_floor_extraction as old
from tests.b5_analysis import fixtures as fx, fixtures_s2 as s2
from tests.b5_analysis.fixtures_s1 import s0_planned

ROOT = Path(__file__).resolve().parents[2]
ABS = [10.0, 10.2, 9.9, 10.1, 10.0, 10.3, 9.8, 10.1, 10.0, 9.6]
DELTAS = [0.10, -0.05, 0.20, 0.00, -0.10, 0.05, 0.15, -0.05, 0.10, 0.00]
_CACHE = {}
_KEPT_REPORTS = []


def setUpModule():
    """Collect every kept-units report, including the CLI's direct call path."""
    _KEPT_REPORTS.clear()
    extract = fe.extract_cells

    def record(*args, **kwargs):
        report = extract(*args, **kwargs)
        if "kept_units_binding" in report:
            _KEPT_REPORTS.append(copy.deepcopy(report))
        return report

    for module in (fe, cli):
        patch = mock.patch.object(module, "extract_cells", side_effect=record)
        patch.start()
        unittest.addModuleCleanup(patch.stop)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def family(cell, cid):
    template = json.loads((ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json").read_bytes())
    definition = copy.deepcopy(template["cells"][0]["condition_family_definitions"]["all"]["condition_family_definition"])
    definition["condition_family_id"] = cid
    definition["measurement_target"] = {"metric": cell["metric"], "window_class": cell["window_class"]}
    binding = {"condition_family_id": cid, "condition_family_definition": definition,
               "condition_family_sha256": canonical_domain_sha256(CONDITION_FAMILY_DOMAIN, definition)}
    cell.update(condition_family_id=cid, condition_family_definitions={arm: copy.deepcopy(binding)
                for arm in (("all",) if cell["kind"] == "absolute" else ("A", "B"))})
    return cell


def arithmetic():
    if "arithmetic" not in _CACHE:
        tmp = tempfile.TemporaryDirectory(prefix="s4-arithmetic-")
        atexit.register(tmp.cleanup)
        root = Path(tmp.name)
        absolute = family(dict(cell_id="abs", kind="absolute", metric="gross_energy_j", window_class="request",
            members=[dict(slot=f"r{i:02d}", bundle_id=f"r{i:02d}") for i in range(1, 11)]), "df-s4")
        comparative = family(dict(cell_id="cmp", kind="comparative", metric="gross_energy_j", window_class="request",
            blocks=[dict(block_id=f"b{i:02d}", members={p: f"b{i:02d}-{p}" for p in ("A1", "B1", "B2", "A2")})
                    for i in range(1, 11)]), "df-s4")
        def write(bundle, value, width):
            summary = old.make_summary(value, anchor_bound=width)
            envelope = summary["energy_anchor_shift_envelopes"]["/gross_energy_j"]
            # Round the endpoints inward so max_abs_delta_j owns the exact
            # decimal width, instead of subtraction rounding widening it.
            envelope["lower_j"] = math.nextafter(value - width, value) if width else value
            envelope["upper_j"] = math.nextafter(value + width, value) if width else value
            old.write_bundle(root, bundle, summary)
        for member, value in zip(absolute["members"], ABS):
            write(member["bundle_id"], value, 0.05)
        for block, delta in zip(comparative["blocks"], DELTAS):
            # Exact floating-point d: (2 + (-2) - 0 - (-2*d))/2.
            for position, value, width in (("A1", 0.0, 0.0), ("B1", 2.0, 0.3), ("B2", -2.0, 0.3), ("A2", -2*delta, 0.0)):
                write(block["members"][position], value, width)
        ids = sorted(fe._spec_referenced_bundle_ids([absolute, comparative]))
        old.install_synthetic_recovered_manifest(root, ids)
        _CACHE["arithmetic"] = root, {"schema_version": fe.EXTRACTION_SPEC_SCHEMA_VERSION, "cells": [absolute, comparative]}
    return _CACHE["arithmetic"]


def units_for(spec, *, removed=(), minimum=5, target=True, window=None):
    cells = {}
    for cell in spec["cells"]:
        cid = cell["condition_family_id"]
        stratum = "repeat" if cell["kind"] == "absolute" else "quad"
        planned = ({m["bundle_id"]: (m["bundle_id"],) for m in cell["members"]} if stratum == "repeat" else
                   {b["block_id"]: tuple(b["members"][p] for p in ("A1", "B1", "B2", "A2")) for b in cell["blocks"]})
        kept, dropped = [], []
        for index, (uid, runs) in enumerate(planned.items()):
            args = (cid, stratum, uid, runs, tuple(range(index*len(runs), (index+1)*len(runs))), (None,)*len(runs))
            if uid in removed:
                dropped.append(DroppedUnit(*args, ("synthetic.removed",), ("synthetic",)))
            else:
                kept.append(Unit(*args))
        previous = cells.get(cid)
        planned_counts = {**(previous.planned if previous else {}), stratum: len(planned)}
        minima = {**(previous.minimum if previous else {}), stratum: minimum}
        strata = {**(previous.kept if previous else {}), stratum: tuple(kept)}
        cells[cid] = CellKeptUnits(cid, target, planned_counts, minima, strata,
            (*(previous.dropped if previous else ()), *dropped), len(strata.get("repeat", ())), len(strata.get("quad", ())))
    return KeptUnits(window or SimpleNamespace(harvest_pin="a"*40), "e"*64, "r"*64, "c"*64, cells, {}, {})


@contextlib.contextmanager
def arithmetic_seams():
    with mock.patch.object(fe, "_default_strict_validator", return_value=[]), \
         mock.patch.object(fe, "_whole_window_extraction_refusals", return_value=()), \
         mock.patch.object(fe, "whole_window_drift_allowances", return_value=ww.WholeWindowDriftAllowanceResult("legacy", {})), \
         mock.patch.object(fe, "AuthenticatedConsumptionSession", side_effect=old.prepared_minted_consumption_session):
        yield


class ArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        arithmetic()

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="s4-case-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "runs"
        base, self.spec = arithmetic()
        self.spec = copy.deepcopy(self.spec)
        shutil.copytree(base, self.root)
        seams = arithmetic_seams()
        seams.__enter__()
        self.addCleanup(seams.__exit__, None, None, None)

    def extract(self, removed=(), **kwargs):
        return fe.extract_cells(self.root, self.spec, kept_units=units_for(self.spec, removed=removed), **kwargs)

    def assert_t2(self, floor):
        expected = dict(n=9, t_critical=2.306, prediction_component_j=0.4382074217131016,
            unguarded_floor_j=0.5435294124720607, guard_factor=1.0606601717798212, guarded_floor_j=0.5765000000000011)
        for key, value in expected.items():
            self.assertEqual(floor[key], value, key)

    def test_t1_comparative_eight(self):
        cell = self.extract(("b05", "b09"))["cells"][1]
        self.assertTrue(cell["extractable"])
        self.assertEqual(cell["n_admitted"], 8)
        expected = dict(n=8, t_critical=2.365, mean_j=0.05, prediction_component_j=0.28223838968365494,
            unguarded_floor_j=1.0895584748159575, guard_factor=1.1338934190276817, guarded_floor_j=1.2354431842396523)
        for key, value in expected.items():
            self.assertEqual(cell["floor"][key], value, key)
        self.assertEqual(cell["excluded_slots"], ["b05", "b09"])
        removed = [m for m in cell["members"] if m["excluded"]]
        self.assertEqual(len(removed), 8)
        self.assertTrue(all(m["metric_value_j"] is None for m in removed))

    def test_t2_r2_removed_absent_repeat(self):
        shutil.rmtree(self.root / "r06")
        with mock.patch.object(fe, "_evaluate_member", wraps=fe._evaluate_member) as evaluate:
            report = self.extract(("r06",))
        cell = report["cells"][0]
        self.assertTrue(cell["extractable"], cell["refusal_reasons"])
        self.assert_t2(cell["floor"])
        self.assertEqual(cell["n_admitted"], 9)
        self.assertEqual(report["spec_membership_refusals"], [])
        self.assertEqual(fe.validate_d117_mint_consumption_report(report), [])
        self.assertNotIn("r06", {call.kwargs["bundle_id"] for call in evaluate.call_args_list})
        row = next(m for m in cell["members"] if m["bundle_id"] == "r06")
        self.assertEqual(row, fe._unevaluated_member(slot="r06", bundle_id="r06").as_row())

    def test_r3_extreme_removed_member_is_never_read_or_hashed(self):
        original = self.extract(("r06",), hash_bundles=True)
        old.write_bundle(self.root, "r06", old.make_summary(1e6, anchor_bound=0.01))
        digest = hashlib.sha256((self.root / "r06/summary_metrics.json").read_bytes()).hexdigest()
        with mock.patch.object(fe, "_evaluate_member", wraps=fe._evaluate_member) as evaluate:
            report = self.extract(("r06",), hash_bundles=True)
        self.assertEqual(report["cells"][0]["floor"], original["cells"][0]["floor"])
        raw = canonical(report)
        self.assertNotIn(b"1000000", raw)
        self.assertNotIn(digest.encode(), raw)
        self.assertNotIn("r06", {call.kwargs["bundle_id"] for call in evaluate.call_args_list})

    def test_t3_guard_at_five(self):
        cell = self.extract(tuple(f"b{i:02d}" for i in range(6, 11)))["cells"][1]
        self.assertEqual(cell["floor"]["n"], 5)
        self.assertEqual(cell["floor"]["t_critical"], 2.776)
        self.assertEqual(cell["floor"]["guard_factor"], 1.5)
        self.assertEqual(cell["floor"]["guarded_floor_j"], 2.0995962052289525)

    def test_t4_all_kept_bytes_and_default_call_path(self):
        before = fe.extract_cells(self.root, self.spec)
        after = self.extract()
        explicit_defaults = fe.extract_cells(self.root, self.spec, kept_units=None, archive_context=None, b_override_s=None)
        self.assertEqual(canonical(before), canonical(explicit_defaults))
        self.assertEqual(canonical(before["cells"]), canonical(after["cells"]))
        after.pop("kept_units_binding")
        self.assertEqual(canonical(before), canonical(after))
        self.assertEqual(before["cells"][0]["floor"]["guarded_floor_j"], 0.5729903925896154)
        self.assertEqual(before["cells"][1]["floor"]["guarded_floor_j"], 1.0348999613670127)
        self.assertEqual([c["floor"]["guard_factor"] for c in before["cells"]], [1.0, 1.0])

    def test_r1_unit_equality_membership_and_overlap_before_any_io(self):
        kept = units_for(self.spec)
        cell = kept.cells["df-s4"]
        repeat = cell.kept["repeat"]
        variants = [replace(cell, kept={**cell.kept, "repeat": (*repeat, replace(repeat[0], unit_id="extra"))}),
            replace(cell, kept={**cell.kept, "repeat": repeat[1:]}),
            replace(cell, kept={**cell.kept, "repeat": (replace(repeat[0], run_ids=("other",)), *repeat[1:])}),
            replace(cell, dropped=(DroppedUnit(**repeat[0].__dict__, codes=(), families=()),))]
        with mock.patch.object(fe, "campaign_cooldown_evidence", wraps=fe.campaign_cooldown_evidence) as cooldown, mock.patch.object(fe, "_evaluate_member", wraps=fe._evaluate_member) as evaluate:
            for bad in variants:
                with self.subTest(bad=bad), self.assertRaisesRegex(fe.FloorExtractionError, "kept_units_spec_mismatch"):
                    fe.extract_cells(self.root, self.spec, kept_units=replace(kept, cells={"df-s4": bad}))
            with self.assertRaises(fe.FloorExtractionError):
                fe.extract_cells(self.root, self.spec, kept_units=replace(kept, cells={}))
        cooldown.assert_not_called()
        evaluate.assert_not_called()

    def cap_hit(self, bundle="r06"):
        manifest_path = self.root / "campaign_manifests/synthetic-session.json"
        manifest = json.loads(manifest_path.read_bytes())
        member = next(m for m in manifest["members"] if m["run_id"] == bundle)
        cooldown = member["preceding_campaign_cooldown"]
        raw_path = manifest_path.parent / cooldown["raw_artifact"]["path"]
        raw = canonical(dict(release=False, release_criteria_met_late=False, rolling_mean_power_w=0.2)) + b"\n"
        raw_path.write_bytes(raw)
        cooldown["result"] = "cap_hit"
        cooldown["raw_artifact"]["sha256"] = hashlib.sha256(raw).hexdigest()
        manifest_path.write_bytes(canonical(manifest))
        joined = fe.campaign_cooldown_evidence(self.root)
        self.assertTrue(joined[bundle]["verified"])
        self.assertEqual(joined[bundle]["result"], "cap_hit")

    def test_r4_verified_cap_hit_stops_kept_and_legacy_still_excludes(self):
        self.cap_hit()
        with mock.patch.object(KeptUnits, "stop_if_member_code_on_kept_unit", autospec=True,
                               side_effect=KeptUnits.stop_if_member_code_on_kept_unit) as stop:
            with self.assertRaisesRegex(AnalysisRefusal, "^member_code_on_kept_unit$"):
                self.extract()
        self.assertEqual(stop.call_args.args[1:], ("df-s4", "r06", "cooldown_cap_hit"))
        self.assertEqual(stop.call_args.kwargs, {})
        legacy = fe.extract_cells(self.root, self.spec)
        self.assertEqual(legacy["cells"][0]["excluded_slots"], ["r06"])

    def test_r5_anchor_fallback_stops_kept_and_legacy_still_excludes(self):
        with mock.patch.object(fe, "anchor_fallback_member_unusable", side_effect=lambda summary, metadata, path: Path(path).name == "r06"):
            with self.assertRaisesRegex(AnalysisRefusal, "^member_code_on_kept_unit$"):
                self.extract()
            legacy = fe.extract_cells(self.root, self.spec)
        self.assertEqual(legacy["cells"][0]["excluded_slots"], ["r06"])

    def test_r6_removed_cap_hit_and_anchor_evidence_never_consulted(self):
        self.cap_hit()
        with mock.patch.object(fe, "anchor_fallback_member_unusable", wraps=fe.anchor_fallback_member_unusable) as fallback, \
             mock.patch.object(fe, "_evaluate_member", wraps=fe._evaluate_member) as evaluate:
            report = self.extract(("r06",))
        self.assertTrue(report["cells"][0]["extractable"])
        self.assert_t2(report["cells"][0]["floor"])
        self.assertNotIn("r06", {call.kwargs["bundle_id"] for call in evaluate.call_args_list})
        self.assertNotIn("r06", {Path(call.args[2]).name for call in fallback.call_args_list})

    def test_f1_kept_quad_cap_hit_stops_and_removed_quad_extracts(self):
        self.cap_hit("b04-B1")
        with self.assertRaisesRegex(AnalysisRefusal, "^member_code_on_kept_unit$"):
            self.extract()
        with mock.patch.object(fe, "_evaluate_member", wraps=fe._evaluate_member) as evaluate:
            cell = self.extract(("b04",))["cells"][1]
        self.assertTrue(cell["extractable"], cell["refusal_reasons"])
        self.assertEqual((cell["n_admitted"], cell["floor"]["n"]), (9, 9))
        self.assertFalse({f"b04-{p}" for p in fe._ABBA_POSITIONS}
                         & {call.kwargs["bundle_id"] for call in evaluate.call_args_list})

    def test_f1_kept_quad_anchor_fallback_stops_and_removed_quad_extracts(self):
        with mock.patch.object(fe, "anchor_fallback_member_unusable",
                side_effect=lambda summary, metadata, path: Path(path).name == "b04-B1"):
            with self.assertRaisesRegex(AnalysisRefusal, "^member_code_on_kept_unit$"):
                self.extract()
            cell = self.extract(("b04",))["cells"][1]
        self.assertTrue(cell["extractable"], cell["refusal_reasons"])
        self.assertEqual((cell["n_admitted"], cell["floor"]["n"]), (9, 9))

    def test_f2_absolute_document_minimum_seven_refuses_eight_extracts(self):
        for removed, count in ((("r08", "r09", "r10"), 7), (("r09", "r10"), 8)):
            with self.subTest(count=count):
                report = fe.extract_cells(self.root, self.spec,
                    kept_units=units_for(self.spec, removed=removed, minimum=8))
                cell = report["cells"][0]
                if count == 7:
                    self.assertIn("kept_units_below_minimum", cell["refusal_reasons"])
                    self.assertIsNone(cell["floor"])
                    self.assertEqual(cell["n_admitted"], 0)
                else:
                    self.assertTrue(cell["extractable"], cell["refusal_reasons"])
                    self.assertEqual((cell["n_admitted"], cell["floor"]["n"]), (8, 8))

    def context_case(self, *, ready=True, provenance=None):
        session = SimpleNamespace(ready=ready, refusal_reasons=(),
            provenance_for=lambda run: provenance, summary_for=lambda run: None,
            consumption_semantics_id=ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
            calibration_bracket=None)
        context = ww.ArchiveContext(self.root, window_bracket={"b_fiducial_s": 0.04})
        return session, context

    def test_f3a_unready_context_without_window_refusal_stops_missing_bound(self):
        (self.root / wl.LOCATOR_BASENAME).write_text(json.dumps({"schema_version": wl.HAZARD_LOCATOR_SCHEMA}))
        session, context = self.context_case(ready=False)
        allowance = ww.WholeWindowDriftAllowanceResult("allowances", {
            ww.NEG8_CLAIM_FAMILY_GROSS: {"allowance_j": 0.8},
            ww.NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED: {"allowance_j": 0.8}})
        with mock.patch.object(fe, "AuthenticatedConsumptionSession", return_value=session), \
             mock.patch.object(fe, "whole_window_drift_allowances", return_value=allowance), \
             self.assertRaisesRegex(AnalysisRefusal, "^operative_bound_not_the_window_bracket$"):
            self.extract(archive_context=context)

    @unittest.skipIf(os.geteuid() == 0, "root can read mode-000 files")
    def test_f3b_unreadable_locator_context_stops_before_bundle_io(self):
        locator = self.root / wl.LOCATOR_BASENAME
        locator.write_text(json.dumps({"schema_version": wl.HAZARD_LOCATOR_SCHEMA}))
        mode = locator.stat().st_mode
        self.addCleanup(os.chmod, locator, mode)
        os.chmod(locator, 0)
        session, context = self.context_case(provenance={"operative_fiducial_bound_s": 0.026})
        real = fe._evaluate_member
        def member(**kwargs):
            return replace(real(**kwargs), consumption_provenance=session.provenance_for(kwargs["bundle_id"]))
        with mock.patch.object(fe, "AuthenticatedConsumptionSession", return_value=session), \
             mock.patch.object(fe, "_evaluate_member", side_effect=member) as evaluate, \
             mock.patch.object(fe, "campaign_cooldown_evidence", wraps=fe.campaign_cooldown_evidence) as cooldown, \
             self.assertRaisesRegex(fe.FloorExtractionError, "^launch_lineage_locator_unreadable$"):
            self.extract(archive_context=context)
        evaluate.assert_not_called()
        cooldown.assert_not_called()

    def test_f3b_no_locator_context_stops_wrong_bound(self):
        self.assertFalse(os.path.lexists(self.root / wl.LOCATOR_BASENAME))
        session, context = self.context_case(provenance={"operative_fiducial_bound_s": 0.026})
        real = fe._evaluate_member
        def member(**kwargs):
            return replace(real(**kwargs), consumption_provenance=session.provenance_for(kwargs["bundle_id"]))
        with mock.patch.object(fe, "AuthenticatedConsumptionSession", return_value=session), \
             mock.patch.object(fe, "_evaluate_member", side_effect=member), \
             self.assertRaisesRegex(AnalysisRefusal, "^operative_bound_not_the_window_bracket$"):
            self.extract(archive_context=context)

    @unittest.skipIf(os.geteuid() == 0, "root can read mode-000 files")
    def test_f3c_unreadable_locator_legacy_stops_before_bundle_io(self):
        locator = self.root / wl.LOCATOR_BASENAME
        locator.write_text(json.dumps({"schema_version": wl.HAZARD_LOCATOR_SCHEMA}))
        mode = locator.stat().st_mode
        self.addCleanup(os.chmod, locator, mode)
        os.chmod(locator, 0)
        with mock.patch.object(fe, "_read_summary", wraps=fe._read_summary) as read, \
             self.assertRaisesRegex(fe.FloorExtractionError, "^launch_lineage_locator_unreadable$"):
            fe.extract_cells(self.root, self.spec)
        read.assert_not_called()

    def test_f3c_invalid_json_and_nonobject_locator_stop(self):
        locator = self.root / wl.LOCATOR_BASENAME
        for raw in (b"{not json", b"[]", b"null", b'"schema"', b"\xff"):
            locator.write_bytes(raw)
            with self.subTest(raw=raw), mock.patch.object(fe, "_read_summary", wraps=fe._read_summary) as read, \
                 self.assertRaisesRegex(fe.FloorExtractionError, "^launch_lineage_locator_unreadable$"):
                fe.extract_cells(self.root, self.spec)
            read.assert_not_called()

    def test_f3c_readable_other_schema_locator_keeps_legacy_bytes(self):
        before = fe.extract_cells(self.root, self.spec)
        (self.root / wl.LOCATOR_BASENAME).write_text('{"schema_version": "joulewise.launch_lineage_locator.v1"}')
        self.assertEqual(canonical(before), canonical(fe.extract_cells(self.root, self.spec)))

    def test_f3d_context_without_locator_requires_kept_units_before_io(self):
        _, context = self.context_case()
        with mock.patch.object(fe, "_evaluate_member", wraps=fe._evaluate_member) as evaluate, \
             mock.patch.object(fe, "AuthenticatedConsumptionSession", wraps=fe.AuthenticatedConsumptionSession) as session:
            report = fe.extract_cells(self.root, self.spec, archive_context=context)
        for cell in report["cells"]:
            self.assertEqual(cell["refusal_reasons"], ["kept_units_required"])
            self.assertIsNone(cell["floor"])
            self.assertEqual(cell["n_admitted"], 0)
        evaluate.assert_not_called()
        session.assert_not_called()

    @unittest.skipIf(os.geteuid() == 0, "root can read mode-000 files")
    def test_f3e_cli_unreadable_locator_exit_two_without_output(self):
        locator = self.root / wl.LOCATOR_BASENAME
        locator.write_text(json.dumps({"schema_version": wl.HAZARD_LOCATOR_SCHEMA}))
        mode = locator.stat().st_mode
        self.addCleanup(os.chmod, locator, mode)
        os.chmod(locator, 0)
        spec_path, out = self.root.parent / "spec.json", self.root.parent / "out.json"
        spec_path.write_bytes(canonical(self.spec))
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), \
             mock.patch.object(cli, "extract_indexed_pack", wraps=cli.extract_indexed_pack) as extract:
            code = cli.main(["--runs-root", str(self.root), "--spec", str(spec_path), "--out", str(out)])
        self.assertEqual((code, stderr.getvalue()), (2, "error: launch_lineage_locator_unreadable\n"))
        self.assertFalse(out.exists())
        extract.assert_not_called()

    def context_report(self, status, allowances):
        provenance = {"operative_fiducial_bound_s": 0.04}
        session, context = self.context_case(provenance=provenance)
        def member(**kwargs):
            return replace(fe._unevaluated_member(slot=kwargs["slot"], bundle_id=kwargs["bundle_id"],
                block_id=kwargs["block_id"], position=kwargs["position"], excluded=False),
                value_j=10.0, anchor_shift_bound_j=0.0, consumption_provenance=provenance)
        with mock.patch.object(fe, "AuthenticatedConsumptionSession", return_value=session), \
             mock.patch.object(fe, "_evaluate_member", side_effect=member), \
             mock.patch.object(fe, "whole_window_drift_allowances",
                return_value=ww.WholeWindowDriftAllowanceResult(status, allowances)):
            return self.extract(archive_context=context)

    def test_f4_context_legacy_allowance_refuses_both_forms(self):
        report = self.context_report("legacy", {})
        for cell in report["cells"]:
            self.assertEqual(cell["refusal_reasons"], ["whole_window_drift_allowance_unrecorded"])
            self.assertIsNone(cell["floor"])
            self.assertEqual(cell["n_admitted"], 0)

    def test_f4_context_missing_claim_family_refuses_both_forms(self):
        report = self.context_report("allowances", {ww.NEG8_CLAIM_FAMILY_IDLE_SUBTRACTED: {"allowance_j": 0.8}})
        for cell in report["cells"]:
            self.assertEqual(cell["refusal_reasons"], ["whole_window_drift_allowance_unrecorded"])
            self.assertIsNone(cell["floor"])
            self.assertEqual(cell["n_admitted"], 0)

    def test_f4_context_allowance_is_whole_in_both_forms(self):
        allowance = {"allowance_j": 0.8, "source": "survivor_rescreen"}
        report = self.context_report("allowances", {ww.NEG8_CLAIM_FAMILY_GROSS: allowance})
        for cell in report["cells"]:
            self.assertTrue(cell["extractable"], cell["refusal_reasons"])
            floor = cell["floor"]
            self.assertEqual(floor["whole_window_drift_allowance_j"], 0.8)
            self.assertEqual(floor["drift_widened_guarded_floor_j"], floor["guarded_floor_j"] + 0.8)
            self.assertEqual(floor["whole_window_drift_allowance_provenance"], allowance)

    def test_f5_sensitivity_view_is_labelled_and_not_mintable(self):
        primary = units_for(self.spec, removed=("r06",))
        view = primary.with_units_restored("df-s4", ["r06"], label="sensitivity-o13")
        report = fe.extract_cells(self.root, self.spec, kept_units=view)
        self.assertEqual(report["kept_units_binding"].get("sensitivity_label"), "sensitivity-o13")
        self.assertEqual(fe.validate_d117_mint_consumption_report(report),
            ["kept_units_binding.sensitivity_label: a sensitivity view is not mintable"])

    def test_f5_primary_label_null_validates_and_missing_key_refuses(self):
        report = self.extract()
        binding = report["kept_units_binding"]
        self.assertIn("sensitivity_label", binding)
        self.assertIsNone(binding["sensitivity_label"])
        self.assertEqual(fe.validate_d117_mint_consumption_report(report), [])
        del binding["sensitivity_label"]
        self.assertTrue(fe.validate_d117_mint_consumption_report(report))

    def test_f6_attribution_labelled_floor_keeps_n_in_both_forms(self):
        for run in fe._spec_referenced_bundle_ids(self.spec["cells"]):
            old.write_bundle(self.root, run, old.make_summary(10.0, anchor_bound=1.0))
        report = self.extract(("r06", "b04"))
        for cell in report["cells"]:
            self.assertIn("admissible_set_uncertainty_dominates_point_floor", cell["floor_conditions"])
            self.assertEqual(cell["n_admitted"], 9)
            self.assertEqual(cell["floor"]["n"], 9)
            self.assertEqual(report["kept_units_binding"]["cells"][cell["cell_id"]]["n_kept"], 9)
        self.assertEqual(fe.validate_d117_mint_consumption_report(report), [])

    def test_f6_relabelled_kept_count_cannot_keep_n_ten_floor(self):
        report = self.extract()
        binding = report["kept_units_binding"]["cells"]["abs"]
        binding["kept_unit_ids"].remove("r06")
        binding.update(removed_unit_ids=["r06"], n_kept=9)
        cell = report["cells"][0]
        cell["members"] = [fe._unevaluated_member(slot="r06", bundle_id="r06").as_row()
                           if m["bundle_id"] == "r06" else m for m in cell["members"]]
        self.assertEqual((cell["n_admitted"], cell["floor"]["n"], binding["n_kept"]), (10, 10, 9))
        self.assertIn("kept_units_binding.cells.abs: floor n differs from kept units",
                      fe.validate_d117_mint_consumption_report(report))

    def test_f6_each_floor_count_field_is_bound_in_both_forms(self):
        original = self.extract()
        for index in (0, 1):
            for field in ("n_admitted", "floor.n"):
                report = copy.deepcopy(original)
                cell = report["cells"][index]
                if field == "n_admitted":
                    cell["n_admitted"] = 9
                else:
                    cell["floor"]["n"] = 9
                with self.subTest(cell=cell["cell_id"], field=field):
                    self.assertIn(f"kept_units_binding.cells.{cell['cell_id']}: floor n differs from kept units",
                                  fe.validate_d117_mint_consumption_report(report))

    def test_f7_absolute_kept_units_require_stop_before_evaluation(self):
        self.cap_hit("r06")
        with mock.patch.object(fe, "_evaluate_member", wraps=fe._evaluate_member) as evaluate, \
             self.assertRaisesRegex(fe.FloorExtractionError, "^kept_units_stop_required$"):
            fe.extract_absolute_cell(cell_id="abs", metric="gross_energy_j", window_class="request",
                members=self.spec["cells"][0]["members"], runs_root=self.root,
                cooldowns=fe.campaign_cooldown_evidence(self.root), strict_validator=lambda p, s: [],
                kept_unit_ids=frozenset(f"r{i:02d}" for i in range(1, 11)), minimum_kept=5)
        evaluate.assert_not_called()

    def test_f7_comparative_kept_units_require_stop_before_evaluation(self):
        self.cap_hit("b04-B1")
        with mock.patch.object(fe, "_evaluate_member", wraps=fe._evaluate_member) as evaluate, \
             self.assertRaisesRegex(fe.FloorExtractionError, "^kept_units_stop_required$"):
            fe.extract_comparative_cell(cell_id="cmp", metric="gross_energy_j", window_class="request",
                blocks=self.spec["cells"][1]["blocks"], runs_root=self.root,
                cooldowns=fe.campaign_cooldown_evidence(self.root), strict_validator=lambda p, s: [],
                kept_unit_ids=frozenset(f"b{i:02d}" for i in range(1, 11)), minimum_kept=5)
        evaluate.assert_not_called()

    def test_r7_minimum_is_document_value_and_p42_has_none(self):
        removed = ("b08", "b09", "b10")
        kept = units_for(self.spec, removed=removed, minimum=8)
        report = fe.extract_cells(self.root, self.spec, kept_units=kept)
        cell = report["cells"][1]
        self.assertIn("kept_units_below_minimum", cell["refusal_reasons"])
        self.assertIsNone(cell["floor"])
        self.assertEqual(cell["n_admitted"], 0)
        p42 = copy.deepcopy(self.spec)
        for spec_cell in p42["cells"]:
            family(spec_cell, "df-s4-p42")
        report = fe.extract_cells(self.root, p42, kept_units=units_for(p42, removed=removed, minimum=8, target=False))
        self.assertNotIn("kept_units_below_minimum", report["cells"][1]["refusal_reasons"])
        self.assertTrue(report["cells"][1]["extractable"])
        self.assertIsNone(report["kept_units_binding"]["cells"]["cmp"]["minimum"])

    def test_non_target_kept_count_below_two_refuses_both_forms(self):
        for count in (0, 1, 2, 3):
            removed = tuple(f"{prefix}{index:02d}" for prefix in ("r", "b")
                            for index in range(count + 1, 11))
            report = fe.extract_cells(self.root, self.spec,
                kept_units=units_for(self.spec, removed=removed, target=False))
            for cell in report["cells"]:
                with self.subTest(count=count, kind=cell["kind"]):
                    self.assertIsNone(report["kept_units_binding"]["cells"][cell["cell_id"]]["minimum"])
                    if count < 2:
                        self.assertEqual(cell["refusal_reasons"], ["kept_units_below_minimum"])
                        self.assertFalse(cell["extractable"])
                        self.assertIsNone(cell["floor"])
                        self.assertEqual(cell["n_admitted"], 0)
                    else:
                        self.assertTrue(cell["extractable"], cell["refusal_reasons"])
                        self.assertEqual(cell["n_admitted"], count)
                        self.assertEqual(cell["floor"]["n"], count)
                        self.assertIsNone(cell["floor"]["guarded_floor_j"])

    def test_r12_membership_counts_removed_records(self):
        report = self.extract(("r06", "b05"))
        self.assertEqual(report["spec_membership_refusals"], [])

    def test_r13_binding_skips_removed_lineage_and_is_closed(self):
        lineage = old.LaunchLineageExtractionTests._lineage()
        real = fe._evaluate_member
        def member(**kwargs):
            return replace(real(**kwargs), launch_lineage=lineage)
        with mock.patch.object(fe, "_evaluate_member", side_effect=member):
            report = self.extract(("r06", "b05"))
        self.assertNotIn("launch_lineage_conflict", report["cells"][0]["refusal_reasons"])
        self.assertNotIn("launch_lineage_conflict", report["cells"][1]["refusal_reasons"])
        self.assertEqual(fe.validate_d117_mint_consumption_report(report), [])
        no_binding = copy.deepcopy(report)
        del no_binding["kept_units_binding"]
        self.assertIn("extraction report.launch_lineage: must equal every member lineage", fe.validate_d117_mint_consumption_report(no_binding))
        bad = copy.deepcopy(report)
        bad["kept_units_binding"]["unknown"] = True
        self.assertTrue(fe.validate_d117_mint_consumption_report(bad))
        bad = copy.deepcopy(report)
        bad["kept_units_binding"]["cells"]["abs"]["unknown"] = True
        self.assertTrue(fe.validate_d117_mint_consumption_report(bad))

    def test_binding_shape_counts_and_removed_evidence_fail_closed(self):
        report = self.extract(("r06",))
        def invalid(change):
            bad = copy.deepcopy(report)
            change(bad)
            self.assertTrue(fe.validate_d117_mint_consumption_report(bad))
        invalid(lambda r: r["kept_units_binding"]["cells"]["abs"].update(n_kept=True))
        invalid(lambda r: r["kept_units_binding"]["cells"]["abs"].update(minimum=True))
        invalid(lambda r: r["kept_units_binding"]["cells"]["abs"].update(kept_unit_ids=["r01", "r01"]))
        invalid(lambda r: r["kept_units_binding"]["cells"]["abs"].update(stratum="quad"))
        invalid(lambda r: r["cells"][0].update(members=None))
        invalid(lambda r: r["cells"][0].update(cell_id=[]))
        invalid(lambda r: r["cells"][0]["members"][0].update(bundle_id=[]))
        invalid(lambda r: next(m for m in r["cells"][0]["members"] if m["excluded"]).update(summary_sha256="a"*64))

    def test_override_unsupported_before_any_bundle_io(self):
        with mock.patch.object(fe, "_evaluate_member") as evaluate, mock.patch.object(fe, "campaign_cooldown_evidence") as cooldown:
            with self.assertRaisesRegex(fe.FloorExtractionError, "^b_override_s_unsupported$"):
                fe.extract_cells(self.root, self.spec, kept_units=units_for(self.spec), b_override_s=0.04)
        evaluate.assert_not_called()
        cooldown.assert_not_called()


class TenCommonMode:
    DELTAS = DELTAS
    OPERATIVE_BOUND_S = old.RegisteredCommonModeExtractionTests.OPERATIVE_BOUND_S
    blocks = classmethod(old.RegisteredCommonModeExtractionTests.blocks.__func__)
    bracket = classmethod(old.RegisteredCommonModeExtractionTests.bracket.__func__)
    session = classmethod(old.RegisteredCommonModeExtractionTests.session.__func__)
    evaluated_member = classmethod(old.RegisteredCommonModeExtractionTests.evaluated_member.__func__)
    calibration_basis = staticmethod(old.RegisteredCommonModeExtractionTests.calibration_basis)
    common_inputs = staticmethod(old.RegisteredCommonModeExtractionTests.common_inputs)


class CommonModeKeptTests(unittest.TestCase):
    def test_t5_d124_only_kept_block_inputs_with_removed_evidence_absent(self):
        with tempfile.TemporaryDirectory(prefix="s4-d124-") as tmp:
            root = Path(tmp)
            blocks = TenCommonMode.blocks()
            cell = family(dict(cell_id="cmp", kind="comparative", metric="phase_energy_j.decode", window_class="phase",
                blocks=blocks, estimator=fe.COMMON_MODE_ESTIMATOR_ID,
                estimator_registration=two_shared_edge_common_mode_registration(),
                calibration_basis=TenCommonMode.calibration_basis()), "df-s4")
            spec = dict(schema_version=fe.EXTRACTION_SPEC_SCHEMA_VERSION, cells=[cell])
            removed = ("b4", "b8")
            for block in blocks:
                if block["block_id"] not in removed:
                    for run in block["members"].values():
                        old.write_bundle(root, run, old.make_summary(10.0, metric="phase_energy_j.decode"))
            session = TenCommonMode.session()
            session.provenance_for = lambda run: {}
            seen = []
            def inputs(members, **kwargs):
                for member in members:
                    self.assertTrue((root / member.bundle_id / "summary_metrics.json").is_file())
                seen.append(members[0].block_id)
                return TenCommonMode.common_inputs(members, **kwargs)
            with mock.patch.object(fe, "AuthenticatedConsumptionSession", return_value=session), \
                 mock.patch.object(fe, "_whole_window_extraction_refusals", return_value=()), \
                 mock.patch.object(fe, "whole_window_drift_allowances", return_value=ww.WholeWindowDriftAllowanceResult("legacy", {})), \
                 mock.patch.object(fe, "_evaluate_member", side_effect=TenCommonMode.evaluated_member) as evaluate, \
                 mock.patch.object(fe, "_common_mode_block_inputs_from_evidence", side_effect=inputs):
                report = fe.extract_cells(root, spec, kept_units=units_for(spec, removed=removed))
            row = report["cells"][0]
            self.assertTrue(row["extractable"], row["refusal_reasons"])
            self.assertEqual(row["floor"]["n"], 8)
            self.assertEqual(row["floor"]["guard_factor"], 1.1338934190276817)
            self.assertEqual(set(seen), {b["block_id"] for b in blocks} - set(removed))
            self.assertEqual(evaluate.call_count, 32)
            self.assertTrue(all(not (root/run).exists() for b in blocks if b["block_id"] in removed for run in b["members"].values()))


class BlockFiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if "beta" not in _CACHE:
            _CACHE["beta"] = fx.build_named("BETA_STD")
            atexit.register(_CACHE["beta"].close)
        cls.window = _CACHE["beta"]
        if "gamma" not in _CACHE:
            _CACHE["gamma"] = fx.build_named("GAMMA_STD")
            atexit.register(_CACHE["gamma"].close)
        cls.other_window = _CACHE["gamma"]
        cls.spec = json.loads((cls.window.measurement / "configs/campaigns" / cls.window.entry.pack_id / "extraction_spec.json").read_bytes())
        # The archived S0 spec predates the extractor's strict condition-family
        # wire. Build its current structural projection over identical ids.
        for cell in cls.spec["cells"]:
            cell["window_class"] = "phase"
            family(cell, "df-b5t-family")
        cls.kept = units_for(cls.spec, window=cls.window.entry)

    def test_r8_block5_kept_required_without_bundle_reads(self):
        unused_session, unused_context, member = self.ready_case(0.04, {"operative_fiducial_bound_s": 0.04})
        unused_session.ready = False
        with mock.patch("joulewise.window_lineage.is_hazard_runs_root", return_value=True), \
             mock.patch.object(fe, "_evaluate_member", side_effect=member) as evaluate, \
             mock.patch.object(fe, "campaign_cooldown_evidence", return_value={}) as cooldown, \
             mock.patch.object(fe, "_whole_window_extraction_refusals", return_value=()), \
             mock.patch.object(fe, "whole_window_drift_allowances", return_value=ww.WholeWindowDriftAllowanceResult("legacy", {})), \
             mock.patch.object(fe, "AuthenticatedConsumptionSession", return_value=unused_session) as session:
            first = fe.extract_cells(self.window.claim, self.spec)
            with_context = fe.extract_cells(self.window.claim, self.spec, archive_context=unused_context)
            self.assertEqual(first, with_context)
            with tempfile.TemporaryDirectory(prefix="s4-empty-window-") as empty:
                second = fe.extract_cells(Path(empty), self.spec)
        second["runs_root"] = first["runs_root"]
        self.assertEqual(first, second)
        for cell in first["cells"]:
            self.assertEqual(cell["refusal_reasons"], ["kept_units_required"])
            self.assertFalse(cell["extractable"])
            self.assertIsNone(cell["floor"])
            self.assertEqual(cell["n_admitted"], 0)
        evaluate.assert_not_called()
        cooldown.assert_not_called()
        session.assert_not_called()

    def test_r9_block5_context_absent_refuses_allowance(self):
        with mock.patch("joulewise.window_lineage.is_hazard_runs_root", return_value=True), \
             mock.patch.object(fe, "_whole_window_extraction_refusals", return_value=()), \
             mock.patch.object(fe, "whole_window_drift_allowances", return_value=ww.WholeWindowDriftAllowanceResult("legacy", {})), \
             mock.patch.object(fe, "_evaluate_member", side_effect=lambda **kw: replace(fe._unevaluated_member(
                 slot=kw["slot"], bundle_id=kw["bundle_id"], block_id=kw["block_id"], position=kw["position"], excluded=False),
                 value_j=10.0, anchor_shift_bound_j=0.0)):
            report = fe.extract_cells(self.window.claim, self.spec, kept_units=self.kept)
        for cell in report["cells"]:
            self.assertIn("whole_window_drift_allowance_unrecorded", cell["refusal_reasons"])
            self.assertEqual(cell["n_admitted"], 0)
            self.assertIsNone(cell["floor"])

    def ready_case(self, bound, provenance):
        session = SimpleNamespace(ready=True, refusal_reasons=(), provenance_for=lambda run: provenance,
            consumption_semantics_id=ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID)
        context = ww.ArchiveContext(self.window.archive, window_bracket={"b_fiducial_s": bound})
        def member(**kw):
            return replace(fe._unevaluated_member(slot=kw["slot"], bundle_id=kw["bundle_id"],
                block_id=kw["block_id"], position=kw["position"], excluded=False),
                value_j=10.0, anchor_shift_bound_j=0.0, consumption_provenance=provenance)
        return session, context, member

    def test_r10_exact_window_bound_pre_capture_other_missing_nonfinite(self):
        wrapper = json.loads((self.window.archive / "withheld/bracket-evaluation.json").read_bytes())
        bound = wrapper["assessment"]["b_fiducial_s"]
        pre_capture_bound = float(fx.PRE_CAPTURE_BOUNDS_S["beta"])
        other_window_bound = json.loads((self.other_window.archive / "withheld/bracket-evaluation.json").read_bytes())["assessment"]["b_fiducial_s"]
        self.assertNotEqual(bound, pre_capture_bound)
        self.assertNotEqual(bound, other_window_bound)
        for provenance in ({"operative_fiducial_bound_s": pre_capture_bound},
                {"operative_fiducial_bound_s": other_window_bound},
                {"operative_fiducial_bound_s": math.nextafter(bound, math.inf)}, {}, None,
                {"operative_fiducial_bound_s": math.inf}, {"operative_fiducial_bound_s": True}):
            session, context, member = self.ready_case(bound, provenance)
            with self.subTest(provenance=provenance), \
                 mock.patch("joulewise.window_lineage.is_hazard_runs_root", return_value=True), \
                 mock.patch.object(fe, "AuthenticatedConsumptionSession", return_value=session), \
                 mock.patch.object(fe, "_whole_window_extraction_refusals", return_value=()), \
                 mock.patch.object(fe, "_evaluate_member", side_effect=member), \
                 mock.patch.object(fe, "whole_window_drift_allowances", return_value=ww.WholeWindowDriftAllowanceResult("legacy", {})), \
                 self.assertRaisesRegex(AnalysisRefusal, "^operative_bound_not_the_window_bracket$"):
                fe.extract_cells(self.window.claim, self.spec, kept_units=self.kept, archive_context=context)

    def test_b1_checks_a_single_kept_member_in_each_form(self):
        bound = json.loads((self.window.archive / "withheld/bracket-evaluation.json").read_bytes())["assessment"]["b_fiducial_s"]
        for bad_run in ("s0-mock-r10", "s0-mock-b10-a2"):
            session, context, member = self.ready_case(bound, {"operative_fiducial_bound_s": bound})
            def evaluated(**kwargs):
                result = member(**kwargs)
                if kwargs["bundle_id"] == bad_run:
                    result = replace(result, consumption_provenance={})
                return result
            with self.subTest(run=bad_run), \
                 mock.patch("joulewise.window_lineage.is_hazard_runs_root", return_value=True), \
                 mock.patch.object(fe, "AuthenticatedConsumptionSession", return_value=session), \
                 mock.patch.object(fe, "_whole_window_extraction_refusals", return_value=()), \
                 mock.patch.object(fe, "_evaluate_member", side_effect=evaluated), \
                 self.assertRaisesRegex(AnalysisRefusal, "^operative_bound_not_the_window_bracket$"):
                fe.extract_cells(self.window.claim, self.spec, kept_units=self.kept, archive_context=context)

    def test_r10_unready_session_uses_own_refusals(self):
        session, context, member = self.ready_case(0.04, None)
        session.ready = False
        session.refusal_reasons = ("window_bracket_differs_from_harvest",)
        with mock.patch("joulewise.window_lineage.is_hazard_runs_root", return_value=True), \
             mock.patch.object(fe, "AuthenticatedConsumptionSession", return_value=session), \
             mock.patch.object(fe, "_whole_window_extraction_refusals", return_value=session.refusal_reasons), \
             mock.patch.object(fe, "_evaluate_member", side_effect=member):
            report = fe.extract_cells(self.window.claim, self.spec, kept_units=self.kept, archive_context=context)
        self.assertTrue(all("window_bracket_differs_from_harvest" in c["refusal_reasons"] for c in report["cells"]))

    def test_r11_kept_scope_and_context_at_real_consumption_call_sites(self):
        kept = units_for(self.spec, removed=("s0-mock-r06", "s0-mock-b05"), window=self.window.entry)
        expected = set(kept.kept_run_ids("df-b5t-family"))
        session, context, member = self.ready_case(0.04, {"operative_fiducial_bound_s": 0.04})
        calls = []
        real_session = fe.AuthenticatedConsumptionSession
        def constructor(root, ids, **kwargs):
            calls.append(("session", set(ids), kwargs["archive_context"]))
            actual = real_session(root, ids, **kwargs)
            self.assertIs(actual.archive_context, context)
            self.assertEqual(actual.referenced_bundle_ids, frozenset(expected))
            return session
        real_refusal = ww.whole_window_refusal_reasons
        def refusal(root, ids, **kwargs):
            calls.append(("refusal", set(ids), kwargs["consumption_session"]))
            # Invoke the real API boundary against a real session to prove its
            # exact identity checks, while synthetic admission remains a seam.
            real_refusal(root, ids, consumption_session=real_session(root, ids, archive_context=context))
            return ()
        def allowance(root, ids, **kwargs):
            calls.append(("allowance", set(ids), kwargs["consumption_session"]))
            return ww.WholeWindowDriftAllowanceResult("allowances", {ww.neg8_claim_family_for_metric("phase_energy_j.decode"):
                {"allowance_j": 0.8, "source": "survivor_rescreen"}})
        with mock.patch("joulewise.window_lineage.is_hazard_runs_root", return_value=True), \
             mock.patch.object(fe, "AuthenticatedConsumptionSession", side_effect=constructor), \
             mock.patch.object(fe, "whole_window_refusal_reasons", side_effect=refusal), \
             mock.patch.object(fe, "whole_window_drift_allowances", side_effect=allowance), \
             mock.patch.object(fe, "_evaluate_member", side_effect=member):
            report = fe.extract_cells(self.window.claim, self.spec, kept_units=kept, archive_context=context)
        self.assertEqual([x[0] for x in calls], ["session", "refusal", "allowance"])
        self.assertTrue(all(x[1] == expected for x in calls))
        self.assertEqual(set(report["consumption_provenance"]), expected)
        self.assertTrue(all(c["floor"]["drift_widened_guarded_floor_j"] == c["floor"]["guarded_floor_j"] + 0.8 for c in report["cells"]))


    def test_context_allowance_absent_refuses_every_cell(self):
        session, context, member = self.ready_case(0.04, {"operative_fiducial_bound_s": 0.04})
        with mock.patch("joulewise.window_lineage.is_hazard_runs_root", return_value=True), \
             mock.patch.object(fe, "AuthenticatedConsumptionSession", return_value=session), \
             mock.patch.object(fe, "_whole_window_extraction_refusals", return_value=()), \
             mock.patch.object(fe, "whole_window_drift_allowances", return_value=ww.WholeWindowDriftAllowanceResult("absent", {})), \
             mock.patch.object(fe, "_evaluate_member", side_effect=member):
            report = fe.extract_cells(self.window.claim, self.spec, kept_units=self.kept, archive_context=context)
        for cell in report["cells"]:
            self.assertIn("whole_window_drift_allowance_unrecorded", cell["refusal_reasons"])
            self.assertIsNone(cell["floor"])
            self.assertEqual(cell["n_admitted"], 0)


def indexed_fixture():
    """One cached S2 bracket + S3 roster projection, with explicit rebindings."""
    if "indexed" in _CACHE:
        return _CACHE["indexed"]
    from joulewise.b5 import harvest
    from joulewise.flags.catalog import load_catalog
    from joulewise.flags.exclusions import compute
    window = s2.build_named("BETA_STD_S3B_ROSTER")
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
    fx.put(tree_path, tree)
    rebuilt = harvest.build_roster(pack, repo)
    projection, _ = harvest.l4_exclusion_inputs(rebuilt, {}, plan_id=window.entry.plan_id, attempt=window.entry.attempt)
    projection.pop("bundles", None)
    projection.pop("chain_started_monotonic_ns", None)
    fx.put(window.archive / "derived/roster.json", projection)
    flags = [json.loads(line) for line in (window.archive / "derived/flags.jsonl").read_bytes().splitlines() if line.strip()]
    exclusions = compute(flags, projection, {}, load_catalog(ROOT / "configs/campaigns/v5_claim_25g83/flag_catalog.json"))
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
    for pack_name in ("alpha", "gamma"):
        entry = fx.structural_archive(directory / pack_name, pack=pack_name)
        entries.append({key: str(value) if isinstance(value, Path) else list(value) if isinstance(value, tuple) else value
                        for key, value in entry.__dict__.items()})
    index = directory / "index.json"
    fx.put(index, {"schema": "joulewise.b5_window_index.v1", "attempts": entries})
    local_repo = directory / "repo"
    local_spec = local_repo / "configs/campaigns" / window.entry.pack_id / "extraction_spec.json"
    local_spec.parent.mkdir(parents=True)
    shutil.copyfile(spec_path, local_spec)
    _CACHE["indexed"] = SimpleNamespace(window=window, index=index, spec=spec, row=row, local_repo=local_repo,
        local_spec=local_spec, directory=directory)
    return _CACHE["indexed"]


class IndexedCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = indexed_fixture()

    def composition(self, *args, **kwargs):
        return self.real_composition(*args, **kwargs, seal_pins=SealPins.load(), pack_table=fx.PACK_TABLE,
            test_only_allow_synthetic_binding=True, repo_root=self.fixture.local_repo)

    def real_output(self, target_refused=False, target_reason="window_evidence_precheck_missing"):
        root, spec = arithmetic()
        spec = copy.deepcopy(spec)
        aliases = copy.deepcopy(spec["cells"])
        for index, cell in enumerate(spec["cells"]):
            cell["cell_id"] = self.fixture.spec["cells"][index]["cell_id"]
        for index, cell in enumerate(aliases):
            cell["cell_id"] = self.fixture.spec["cells"][index+2]["cell_id"]
            family(cell, "df-s4-p42")
        spec["cells"].extend(aliases)
        real = fe._evaluate_member
        def member(**kwargs):
            result = real(**kwargs)
            # These cell calls share a metric; the named precheck seam records
            # a p42 outcome on the two later calls, with real arithmetic elsewhere.
            if self._evaluated_cell >= 2:
                return replace(result, reasons=("window_evidence_precheck_missing",))
            if target_refused and self._evaluated_cell == 0:
                return replace(result, reasons=(target_reason,))
            return result
        real_abs, real_cmp = fe.extract_absolute_cell, fe.extract_comparative_cell
        def absolute(**kwargs):
            self._evaluated_cell = 0 if not kwargs["cell_id"].startswith("p42-") else 2
            return real_abs(**kwargs)
        def comparative(**kwargs):
            self._evaluated_cell = 1 if not kwargs["cell_id"].startswith("p42-") else 3
            return real_cmp(**kwargs)
        with arithmetic_seams(), mock.patch.object(fe, "_evaluate_member", side_effect=member),              mock.patch.object(fe, "extract_absolute_cell", side_effect=absolute),              mock.patch.object(fe, "extract_comparative_cell", side_effect=comparative):
            return fe.extract_cells(root, spec, kept_units=units_for(spec), hash_bundles=True)

    def test_r14_real_index_context_composition_with_registered_p42_exit(self):
        self.real_composition = cli.extract_indexed_pack
        # L9-STEP4-3: a refused target is a stop named by its reasons' class. The seam's
        # window_evidence_precheck_missing is tooling; cadence_ratio_below_threshold is a plan
        # section 2.2 R3 code. Both were floor_cell_not_extractable at origin/main 0a9ff42.
        for target_refused, reason, expected in (
                (False, None, "p42_floor_cells_only"),
                (True, "window_evidence_precheck_missing", "extraction_cell_tooling_refusal"),
                (True, "cadence_ratio_below_threshold", "extraction_cell_r3_refusal")):
            with self.subTest(target_refused=target_refused, reason=reason):
                output = self.real_output(target_refused, reason)
                out = self.fixture.directory / ("target-refused-%s.json" % reason if target_refused else "p42-only.json")
                if out.exists():
                    out.unlink()
                stderr, stdout = io.StringIO(), io.StringIO()
                with s2.capture_adapter(), mock.patch.object(cli, "extract_indexed_pack", side_effect=self.composition),                  mock.patch.object(cli, "extract_cells", return_value=output) as extract,                  contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
                    code = cli.main(["--window-index", str(self.fixture.index), "--pack", "beta", "--hash-bundles", "--out", str(out)])
                self.assertEqual(code, 1, stderr.getvalue())
                report = json.loads(out.read_bytes())
                self.assertEqual(classify_step4_exit(code, report, self.fixture.spec), expected)
                self.assertEqual(report["spec_membership_refusals"], [])
                self.assertEqual(stdout.getvalue(), "")
                args, kwargs = extract.call_args
                self.assertEqual(args[0], self.fixture.window.claim)
                self.assertEqual(args[1], self.fixture.spec)
                self.assertEqual(kwargs["evaluation_basis_sha256"], self.fixture.row["evaluation_basis"]["sha256"])
                self.assertEqual(kwargs["consumption_semantics_id"], ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID)
                self.assertEqual(kwargs["mode"], "read_replay")
                self.assertIs(kwargs["hash_bundles"], True)
                self.assertIsInstance(kwargs["kept_units"], KeptUnits)
                self.assertIsInstance(kwargs["archive_context"], ww.ArchiveContext)
                self.assertEqual(kwargs["archive_context"].neg8_harvest_archive, self.fixture.window.archive)

    def test_r15_archive_spec_mismatch_exit_two_before_extraction(self):
        self.real_composition = cli.extract_indexed_pack
        original = self.fixture.local_spec.read_bytes()
        out = self.fixture.directory / "mismatch.json"
        try:
            self.fixture.local_spec.write_bytes(original + b" ")
            stderr = io.StringIO()
            with (
                s2.capture_adapter(),
                mock.patch.object(cli, "extract_indexed_pack", side_effect=self.composition),
                mock.patch.object(cli, "extract_cells", return_value={"cells": [], "spec_membership_refusals": []}) as extract,
                contextlib.redirect_stderr(stderr),
            ):
                code = cli.main(["--window-index", str(self.fixture.index), "--pack", "beta", "--out", str(out)])
            self.assertEqual((code, stderr.getvalue()), (2, "error: extraction_spec_differs_from_archive\n"))
            self.assertFalse(out.exists())
            extract.assert_not_called()
        finally:
            self.fixture.local_spec.write_bytes(original)

    def test_f8_allowance_verdict_digest_mismatch_stops_script_without_output(self):
        from joulewise.b5_analysis import kept_units as ku_module
        self.real_composition = cli.extract_indexed_pack
        strict_json = ku_module._strict_json
        for field in ("row_sha256", "evaluation_basis_sha256"):
            # Inventory authenticates the stored allowance bytes first. Inject
            # only its parsed read so this reaches the script's own digest gate.
            def read(raw, code):
                value = strict_json(raw, code)
                if code == "neg8_allowance_record_invalid":
                    value["verdict"][field] = "0" * 64
                return value
            out = self.fixture.directory / ("f8-" + field + ".json")
            stderr = io.StringIO()
            with self.subTest(digest=field), s2.capture_adapter(), \
                 mock.patch.object(ku_module, "_strict_json", side_effect=read), \
                 mock.patch.object(cli, "extract_indexed_pack", side_effect=self.composition), \
                 mock.patch.object(cli, "extract_cells", wraps=cli.extract_cells) as extract, \
                 contextlib.redirect_stderr(stderr):
                code = cli.main(["--window-index", str(self.fixture.index), "--pack", "beta", "--out", str(out)])
                self.assertEqual((code, stderr.getvalue()),
                                 (2, "error: whole_window_verdict_provenance_invalid\n"))
                self.assertFalse(out.exists())
                extract.assert_not_called()

    def test_s10_production_shaped_extraction_admits_every_target_cell(self):
        # Inverted at S10. The S0 mock-adapter corpus authenticated structure and
        # context but could not be re-reduced (every cell refused, among others
        # capture_pipeline_superseded). The S10 windows are collected through the
        # production reduction path: on the sealed BETA pack every target cell is
        # extractable through a real ready session and only the registered p42
        # floor cells refuse. Runs only with JW_B5_S10_REAL_PROGRAMS=1.
        from tests.b5_analysis.fixtures_s10 import ROOT as S10_ROOT, chain_fixture
        chain = chain_fixture()
        if "beta" not in chain.windows:
            self.skipTest("window not built")
        with chain.seams():
            report = cli.extract_indexed_pack(chain.index, "beta", seal_pins=SealPins.load(),
                repo_root=chain.repo_root, mode="read_replay")
        pack_id = chain.windows["beta"].entry_data["pack_id"]
        spec = json.loads((S10_ROOT / "configs/campaigns" / pack_id / "extraction_spec.json").read_bytes())
        self.assertFalse(report["all_cells_extractable"])
        self.assertEqual(classify_step4_exit(1, report, spec), "p42_floor_cells_only",
                         {c["cell_id"]: c["refusal_reasons"] for c in report["cells"]})
        self.assertTrue(any(c["extractable"] for c in report["cells"]))
        self.assertNotIn("capture_pipeline_superseded",
                         {reason for cell in report["cells"] for reason in cell["refusal_reasons"]})


class CliRefusalTests(unittest.TestCase):
    def invoke(self, args):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = cli.main(args)
        return code, stderr.getvalue()

    def test_r15_conflicting_flags_gamma_and_block5_legacy(self):
        with tempfile.TemporaryDirectory(prefix="s4-cli-") as tmp:
            out = Path(tmp) / "out.json"
            for flag, value in (("--runs-root", tmp), ("--spec", "spec.json"), ("--manifest-id", "caller"),
                    ("--evaluation-basis-sha256", "a"*64), ("--consumption-semantics-id", ww.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID)):
                with self.subTest(flag=flag):
                    code, error = self.invoke(["--window-index", "index.json", "--pack", "beta", flag, value, "--out", str(out)])
                    self.assertEqual((code, error), (2, "error: window_index_conflicting_arguments\n"))
                    self.assertFalse(out.exists())
            with mock.patch.object(cli, "extract_indexed_pack", return_value={"cells": [], "spec_membership_refusals": []}) as composition:
                self.assertEqual(self.invoke(["--window-index", "index.json", "--pack", "gamma", "--out", str(out)]),
                                 (2, "error: floor_pack_required\n"))
                composition.assert_not_called()
            with mock.patch("joulewise.window_lineage.is_hazard_runs_root", return_value=True):
                self.assertEqual(self.invoke(["--runs-root", tmp, "--spec", "spec.json", "--out", str(out)]),
                                 (2, "error: window_index_required\n"))
            self.assertFalse(out.exists())

    def test_output_parent_input_error_is_code_only(self):
        with tempfile.TemporaryDirectory(prefix="s4-cli-output-") as tmp:
            parent = Path(tmp) / "file"
            parent.write_text("counterfactual parent is a regular file")
            out = parent / "out.json"
            with mock.patch.object(cli, "extract_indexed_pack", return_value={"cells": [], "spec_membership_refusals": []}):
                self.assertEqual(self.invoke(["--window-index", "index.json", "--pack", "beta", "--out", str(out)]),
                    (2, "error: extraction_output_unwritable\n"))
            self.assertFalse(out.exists())

    def test_r16_analysis_refusal_code_only_and_no_output(self):
        with tempfile.TemporaryDirectory(prefix="s4-cli-") as tmp:
            out = Path(tmp) / "out.json"
            with mock.patch.object(cli, "extract_indexed_pack", side_effect=AnalysisRefusal("member_code_on_kept_unit")):
                self.assertEqual(self.invoke(["--window-index", "index.json", "--pack", "beta", "--hash-bundles", "--out", str(out)]),
                                 (2, "error: member_code_on_kept_unit\n"))
            self.assertFalse(out.exists())


class ZKeptReportInvariantTests(unittest.TestCase):
    def test_every_kept_report_refused_cell_names_a_reason(self):
        if not _KEPT_REPORTS:
            root, spec = arithmetic()
            with arithmetic_seams():
                fe.extract_cells(root, spec, kept_units=units_for(spec))
        self.assertTrue(_KEPT_REPORTS)
        for index, report in enumerate(_KEPT_REPORTS):
            for cell in report["cells"]:
                with self.subTest(report=index, cell=cell["cell_id"]):
                    self.assertTrue(cell["extractable"] or cell["refusal_reasons"])

    def test_f6_collected_kept_reports_validate_with_bound_counts(self):
        self.assertTrue(_KEPT_REPORTS)
        for index, report in enumerate(_KEPT_REPORTS):
            with self.subTest(report=index):
                expected = (["kept_units_binding.sensitivity_label: a sensitivity view is not mintable"]
                            if report["kept_units_binding"]["sensitivity_label"] is not None else [])
                self.assertEqual(fe.validate_d117_mint_consumption_report(report), expected)


if __name__ == "__main__":
    unittest.main()
