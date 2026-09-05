"""Localized corruption across actual admission paths, without hardware work.

N/A: extraction reports are not floor artifacts (bytes is a wrong-schema control),
so they have no resolver/aggregation path. Components reach those paths through
byte admission before projection. A pure resolver checks its selected cell/group;
canonical cross-carrier mixtures belong to byte admission, not local resolution.
Generalized output tests stub unrelated custody/recomputation, retaining real
admission, rendering, both output branches, and public exception translation.
"""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from contextlib import ExitStack
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from joulewise import detection_floor as df
from joulewise.analysis_engine import _combined_floor
from joulewise.analysis_engine.artifact import (
    ClaimArtifactError, finalize_claim_verdicts, validate_claim_verdicts,
    write_claim_verdicts_atomic,
)
from joulewise.analysis_engine.inputs import (
    AnalysisInputError, FloorRequest, FloorResolution,
    authenticate_floor_artifact_bytes, resolve_floor,
)
from joulewise.floor_extraction import validate_d117_mint_consumption_report
from scripts import mint_floor_artifact as mint
from scripts import mint_floor_artifact_generalized as generalized
from tests.test_analysis_claims import evaluation, minimal_artifact
from tests.test_detection_floor import make_artifact, make_cell, make_consumer
from tests.test_mint_floor_artifact import authenticated_components

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = (df.SINGLE_COUNT_DISCIPLINE_ID_V1, df.SINGLE_COUNT_DISCIPLINE_ID)
MISSING = object()
FLOOR_PATHS = {
    "cell": ("cells", 0),
    "absolute": ("cells", 0, "absolute"),
    "comparative": ("cells", 0, "comparative"),
    "group": ("transport_groups", 0),
}


def at(value, path):
    for key in path:
        value = value[key]
    return value


def versioned(value, rule_id):
    value = copy.deepcopy(value)
    def visit(node):
        if isinstance(node, dict):
            for key, child in node.items():
                if key == "single_count_discipline":
                    node[key] = df.attribution_single_count_discipline(rule_id)
                else:
                    visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)
    visit(value)
    return value


def shapes(rule_id):
    canonical = df.attribution_single_count_discipline(rule_id)
    other = df.attribution_single_count_discipline(next(v for v in VERSIONS if v != rule_id))
    return {
        "null": None, "array": [], "empty_object": {}, "string": "bad",
        "missing": MISSING,
        "list_id": {**canonical, "rule_id": []},
        "dict_id": {**canonical, "rule_id": {}},
        "null_id": {**canonical, "rule_id": None},
        "integer_id": {**canonical, "rule_id": 1},
        "unknown_id": {**canonical, "rule_id": "unknown.v9"},
        "id_body_swap": {**canonical, "rule_id": other["rule_id"]},
        "extra": {**canonical, "extra": True},
        "true_as_one": {**canonical, "both_terms_required": 1},
        "false_as_zero": {**canonical, "apparent_double_count_removal_forbidden": 0},
        "mixed_versions": other,
        **({"gating_as_zero": {**canonical, "gating": 0}} if rule_id == VERSIONS[1] else {}),
    }


def corrupt(value, path, bad):
    result = copy.deepcopy(value)
    carrier = at(result, path)
    if bad is MISSING:
        del carrier["single_count_discipline"]
    else:
        carrier["single_count_discipline"] = copy.deepcopy(bad)
    return result


def request_for(artifact, *, exact):
    consumer = make_consumer()
    if exact:
        key = artifact["cells"][0]["key"]
        consumer.update({k: key[k] for k in ("condition_family_id", "condition_family_sha256")})
    fields = {k: consumer.pop(k) for k in (
        "backend", "metric", "window_class", "condition_family_id",
        "condition_family_sha256", "stack_identity_sha256",
    )}
    return FloorRequest(**fields, consumer_stress=consumer)


def resolution(rule_id, **overrides):
    values = dict(
        status="exact", artifact_id="floor", artifact_sha256="0" * 64,
        source_cell_ids=("floor-cell",), transport_group_id="tg-1",
        transport_rule_id=df.TRANSPORT_RULE_ID, floor_abs_j=.5, floor_cmp_j=1.,
        floor_gate_j=1., reason_codes=(), floor_source=df.ATTRIBUTION_FLOOR_SOURCE,
        floor_limit_class=df.ATTRIBUTION_LIMIT_CLASS,
        point_floor_diagnostics={"label": "repeatability_diagnostic",
            "published_claim_floor": False, "unguarded_floor_j": .1,
            "guard_factor": 1.5, "guarded_floor_j": .15},
        single_count_discipline=df.attribution_single_count_discipline(rule_id),
    )
    values.update(overrides)
    return FloorResolution(**values)


def claim_artifact(rule_id):
    artifact = minimal_artifact()
    contrast = artifact["contrasts"][0]
    floor = _combined_floor([resolution(rule_id)])
    contrast["floor"] = floor
    contrast["claim_evaluation"]["floor_limit"] = {
        k: copy.deepcopy(floor[k]) for k in (
            "floor_source", "floor_limit_class", "point_floor_diagnostics",
            "single_count_discipline",
        )
    }
    contrast["claim_evaluation"]["floor_limit"]["published_floor_j"] = 1.
    return finalize_claim_verdicts(artifact)


class DisciplineMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cell = make_cell(energies=[0.] * 5, deltas=[0.] * 5,
                         absolute_half_widths=[.5] * 5, comparative_half_widths=[.5] * 5)
        cls.floor = make_artifact([cell])
        cls.floor["calibration_scope"] = "window_a"
        cls.extraction = json.loads((ROOT / "docs/paper/fill-rehearsal/dominance-reproduced-alpha-extraction.json").read_text())
        golden = json.loads((ROOT / "tests/fixtures/d117_postcollection_trust/extraction_report.json").read_text())
        for row in cls.extraction["cells"]:
            row["floor"] = copy.deepcopy(golden["cells"][0]["floor"])
        cls.output_core = generalized._fresh_original_core()

    def test_schema_valid_baselines_preserve_versions_and_prose(self):
        for rule_id in VERSIONS:
            with self.subTest(version=rule_id):
                floor = versioned(self.floor, rule_id)
                self.assertEqual(df.validate_floor_artifact(floor), [])
                authenticate_floor_artifact_bytes(json.dumps(floor).encode())
                for exact in (False, True):
                    result = resolve_floor(floor, "0" * 64, request_for(floor, exact=exact))
                    self.assertEqual(result.status, "exact" if exact else "transported")
                    combined = _combined_floor([result])
                    self.assertEqual(combined["single_count_discipline"], df.attribution_single_count_discipline(rule_id))
                extraction = versioned(self.extraction, rule_id)
                self.assertEqual(validate_d117_mint_consumption_report(extraction), [])
                for artifact in (floor, extraction):
                    prose = mint.render_single_count_statement(artifact)
                    self.assertIn("Planning sizing expression:" if rule_id == VERSIONS[1] else "effective clearable effect", prose)
                self.assertEqual(validate_claim_verdicts(claim_artifact(rule_id)), [])

    def test_floor_shape_matrix_bytes_and_preprojection_chains(self):
        for rule_id in VERSIONS:
            baseline = versioned(self.floor, rule_id)
            for carrier, path in FLOOR_PATHS.items():
                for shape, bad in shapes(rule_id).items():
                    value = corrupt(baseline, path, bad)
                    for admission in ("bytes", "resolver_chain", "aggregation_chain"):
                        with self.subTest(version=rule_id, carrier=carrier, shape=shape, admission=admission):
                            with self.assertRaisesRegex(AnalysisInputError, "single.count.*discipline"):
                                authenticate_floor_artifact_bytes(json.dumps(value).encode())
                                if admission != "bytes":
                                    result = resolve_floor(value, "0" * 64, request_for(value, exact=carrier != "group"))
                                    if admission == "aggregation_chain":
                                        _combined_floor([result])
                    if carrier in ("cell", "group") and shape != "mixed_versions":
                        with self.subTest(carrier=carrier, shape=shape, admission="pure_resolver", version=rule_id):
                            result = resolve_floor(value, "0" * 64, request_for(value, exact=carrier == "cell"))
                            self.assertEqual(result.status, "refused")
                            self.assertIn("artifact_schema_invalid", result.reason_codes)
                            self.assertEqual((result.floor_abs_j, result.floor_cmp_j, result.floor_gate_j), (None, None, None))

    def test_mint_shape_matrix_refuses_before_any_output(self):
        profiles = ((self.floor, FLOOR_PATHS), (self.extraction, {"extraction_root": (), "extraction_cell": ("cells", 0)}))
        for rule_id in VERSIONS:
            for source, paths in profiles:
                baseline = versioned(source, rule_id)
                for carrier, path in paths.items():
                    for shape, bad in shapes(rule_id).items():
                        value = corrupt(baseline, path, bad)
                        with self.subTest(version=rule_id, carrier=carrier, shape=shape), tempfile.TemporaryDirectory() as tmp:
                            outputs = tuple(Path(tmp) / name for name in ("floor.json", "statement.txt", "replay.json"))
                            with self.assertRaisesRegex(mint.MintError, "single.count.*discipline"):
                                mint.render_single_count_statement(value)
                            with mock.patch.object(mint, "_exclusive_write") as write:
                                with self.assertRaisesRegex(mint.MintError, "single.count.*discipline"):
                                    mint.write_outputs_exclusive(value, *outputs[:2])
                                write.assert_not_called()
                            with mock.patch.object(self.output_core, "_exclusive_write") as write:
                                with self.assertRaisesRegex(self.output_core.MintError, "single.count.*discipline"):
                                    generalized._write_v2_artifact_outputs(output_core=self.output_core,
                                        artifact=value, sidecar={}, floor_path=outputs[0],
                                        statement_path=outputs[1], d165_replay_out=outputs[2])
                                write.assert_not_called()
                            self.assertFalse(any(path.exists() for path in outputs))

    def test_aggregation_injections_all_statuses_order_and_diagnostics(self):
        for rule_id in VERSIONS:
            for shape, bad in shapes(rule_id).items():
                for status in ("exact", "transported", "refused"):
                    for diagnostics in ({}, None):
                        for reverse in (False, True):
                            with self.subTest(version=rule_id, shape=shape, status=status, diagnostics=diagnostics, reverse=reverse):
                                broken = resolution(rule_id, status=status, point_floor_diagnostics=diagnostics,
                                                    single_count_discipline=None if bad is MISSING else bad)
                                rows = [resolution(rule_id), broken]
                                if reverse:
                                    rows.reverse()
                                with self.assertRaisesRegex(AnalysisInputError, "single.count.*discipline"):
                                    _combined_floor(rows)

    def test_extraction_admission_before_reconstruction(self):
        for rule_id in VERSIONS:
            baseline = versioned(self.extraction, rule_id)
            for path in ((), ("cells", 0)):
                for shape, bad in shapes(rule_id).items():
                    value = corrupt(baseline, path, bad)
                    with self.subTest(version=rule_id, path=path, shape=shape), tempfile.TemporaryDirectory() as tmp:
                        report_path = Path(tmp) / "report.json"
                        report_path.write_text(json.dumps(value))
                        # Both generalized ingress routes must fail before a builder can normalize the cache.
                        with self.assertRaisesRegex(generalized.MintError, "single.count.*discipline"):
                            generalized._pre_admit_legacy_report(report_path, "extraction report")
                        components = SimpleNamespace(absolute=SimpleNamespace(report=value), comparative=SimpleNamespace(report=baseline))
                        with mock.patch.object(generalized, "_v2_authenticate_bracket_binding") as compute:
                            with self.assertRaisesRegex(generalized.MintError, "single.count.*discipline"):
                                generalized._v2_gate_postcollection(producer={}, cell_pins={}, cell_inputs=components,
                                                                   producer_inputs=None, ledger_snapshot=None)
                            compute.assert_not_called()
                        with self.assertRaisesRegex(mint.MintError, "single.count.*discipline"):
                            mint._target_report_cell(value, "unused", "comparative")
                        plan, absolute, comparative = authenticated_components()
                        with self.assertRaisesRegex(mint.MintError, "single.count.*discipline"):
                            mint.mint_authenticated_artifact(artifact_id="test", plan=plan, plan_sha256=mint.PLAN_SHA256,
                                calibration_plan_relative_path="plan.json", absolute=replace(absolute, report=value),
                                comparative=comparative, project_commit="0" * 40, project_tree_state="clean")
                        with mock.patch.object(generalized, "_load_v1_pinset", return_value=None), \
                             mock.patch.object(generalized, "_configured_core", return_value=self.output_core):
                            with self.assertRaisesRegex(generalized.MintError, "single.count.*discipline"):
                                generalized.mint_authenticated_artifact(pinset_path=Path("fixture"), pinset_sha256="0" * 64,
                                    artifact_id="test", plan=plan, plan_sha256=mint.PLAN_SHA256,
                                    calibration_plan_relative_path="plan.json", absolute=replace(absolute, report=value),
                                    comparative=comparative, project_commit="0" * 40, project_tree_state="clean")

    def test_claims_finalize_and_write_matrix(self):
        for rule_id in VERSIONS:
            baseline = claim_artifact(rule_id)
            paths = (("contrasts", 0, "floor"), ("contrasts", 0, "floor", "resolutions", 0),
                     ("contrasts", 0, "claim_evaluation", "floor_limit"))
            metadata = {k: copy.deepcopy(baseline["contrasts"][0]["floor"][k]) for k in (
                "floor_source", "floor_limit_class", "point_floor_diagnostics", "single_count_discipline")}
            for shape, bad in shapes(rule_id).items():
                if shape != "mixed_versions":  # One supplied canonical version is a positive direct-claim control.
                    result = evaluation(floor_metadata=corrupt(metadata, (), bad))
                    self.assertEqual(result["outcome"], "not_estimable")
                    self.assertIn("floor_artifact_invalid", result["reason_codes"])
                    self.assertFalse(result["claim_ready_for_l2_l3"])
                for path in paths:
                    with self.subTest(version=rule_id, shape=shape, path=path), tempfile.TemporaryDirectory() as tmp:
                        value = corrupt(baseline, path, bad)
                        with self.assertRaisesRegex(ClaimArtifactError, "single.count.*discipline"):
                            finalize_claim_verdicts(value)
                        with mock.patch("joulewise.analysis_engine.artifact.tempfile.NamedTemporaryFile") as write:
                            with self.assertRaisesRegex(ClaimArtifactError, "single.count.*discipline"):
                                write_claim_verdicts_atomic(Path(tmp) / "claim.json", value)
                            write.assert_not_called()
                        self.assertEqual(list(Path(tmp).iterdir()), [])

    def _public_generalized_output(self, artifact, outputs, replay):
        """Drive the real public writer selection with unrelated custody stubbed."""
        cell = self.floor["cells"][0]
        producer = {"plan": {"plan_id": "p", "declared_calibration_scope": "window_a"},
                    "cells": [{"cell_id": cell["cell_id"], "transport_group_id": cell["transport_group_id"], "role": "r"}]}
        pinset = generalized.V2Pinset({"producer_plans": [producer],
            "aggregate": {"component_artifacts": [{"sha256": "stub", "plan_id": "p"}]}})
        component = SimpleNamespace(comparative=None)
        inputs = {"p": SimpleNamespace(cells={"r": component}, evidence_root=outputs[0].parent,
            calibration_acceptance={}, calibration_acceptance_sha256="0" * 64,
            calibration_allowance_projection={}, bracket_binding=None)}
        patches = {
            "_actual_v2_git_state": ("0" * 40, True), "load_pinset": pinset,
            "_validate_v2_pin_hashes": None,
            "_load_v2_input_manifest": {"calibration_ledger_head_pin": str(outputs[0].parent / "head")},
            "_authenticate_v2_inputs": (inputs, {}, None),
            "_head_pin_commit_containment_in_origin_main": True,
            "_build_v2_artifacts": (artifact, [self.floor]),
            "_artifact_sha256_containment_variants": {"stub"},
            "_v2_mint_pinset": None, "_configured_core": self.output_core,
            "_fresh_original_core": self.output_core,
            "_validate_v2_recomputation_census": None,
            "validate_floor_artifact": [],
        }
        with ExitStack() as stack:
            for name, value in patches.items():
                stack.enter_context(mock.patch.object(generalized, name, return_value=value))
            stack.enter_context(mock.patch.object(generalized.mint_estimator, "bind_v2_floor_artifact_evidence",
                return_value=(None, SimpleNamespace(estimator_path="common_mode"))))
            stack.enter_context(mock.patch.object(generalized.dominance_closeout, "build_d165_replay_sidecar", return_value={}))
            return generalized.mint_multi_cell_floor_artifact(
                pinset_path=Path("fixture-pinset"), pinset_sha256="0" * 64,
                input_manifest_path=Path("fixture-manifest"), floor_path=outputs[0], statement_path=outputs[1],
                project_commit="0" * 40, project_tree_state="clean", strict_validator=lambda *_: [],
                d165_replay_out=outputs[2] if replay else None)

    def test_public_generalized_both_writer_branches_translate_core_error(self):
        for rule_id in VERSIONS:
            baseline = versioned(self.floor, rule_id)
            for replay in (False, True):
                # The same public seam must produce usable outputs for the valid control.
                with tempfile.TemporaryDirectory() as tmp:
                    outputs = tuple(Path(tmp) / n for n in ("floor.json", "statement.txt", "replay.json"))
                    self._public_generalized_output(baseline, outputs, replay)
                    self.assertTrue(all(p.exists() for p in outputs[:3 if replay else 2]))
                for carrier, path in FLOOR_PATHS.items():
                    for shape, bad in shapes(rule_id).items():
                        with self.subTest(version=rule_id, replay=replay, carrier=carrier, shape=shape), tempfile.TemporaryDirectory() as tmp:
                            outputs = tuple(Path(tmp) / n for n in ("floor.json", "statement.txt", "replay.json"))
                            with mock.patch.object(self.output_core, "_exclusive_write") as write:
                                with self.assertRaisesRegex(generalized.MintError, "single.count.*discipline"):
                                    self._public_generalized_output(corrupt(baseline, path, bad), outputs, replay)
                                write.assert_not_called()
                            self.assertFalse(any(p.exists() for p in outputs))

    def test_malformed_containers_and_optional_absence_controls(self):
        for profile, baseline, names in (("floor", self.floor, ("cells", "transport_groups")),
                                          ("extraction", self.extraction, ("cells",))):
            for name in names:
                for bad in (None, {}, "bad", [None], [[]], ["bad"]):
                    with self.subTest(profile=profile, name=name, bad=bad):
                        value = copy.deepcopy(baseline)
                        value[name] = bad
                        with self.assertRaisesRegex(mint.MintError, "single.count.*discipline"):
                            mint.render_single_count_statement(value)
        for component in ("absolute", "comparative"):
            for bad in ([], "bad", 1):
                value = copy.deepcopy(self.floor)
                value["cells"][0][component] = bad
                with self.assertRaisesRegex(AnalysisInputError, "single.count.*discipline"):
                    authenticate_floor_artifact_bytes(json.dumps(value).encode())
        for rule_id in VERSIONS:
            extraction = versioned(self.extraction, rule_id)
            with self.assertRaises(AnalysisInputError):  # Wrong-schema control, not discipline coverage.
                authenticate_floor_artifact_bytes(json.dumps(extraction).encode())
            metadata = {"floor_source": df.ATTRIBUTION_FLOOR_SOURCE,
                "floor_limit_class": df.ATTRIBUTION_LIMIT_CLASS, "point_floor_diagnostics": {},
                "single_count_discipline": df.attribution_single_count_discipline(rule_id)}
            self.assertTrue(evaluation(floor_metadata=metadata)["claim_ready_for_l2_l3"])
        self.assertEqual(df.read_single_count_profile({"cells": [{"absolute": None, "comparative": None}],
            "transport_groups": [{}]}, profile="floor", where="optional"), ())

    def test_required_parent_absence_and_nonmapping_claim_metadata(self):
        for source, path in ((self.floor, ("cells", 0)), (self.floor, ("transport_groups", 0)),
                             (self.extraction, ())):
            value = copy.deepcopy(source)
            carrier = at(value, path)
            for key in ("single_count_discipline", "floor_source", "floor_limit_class"):
                carrier.pop(key, None)
            with self.assertRaisesRegex(mint.MintError, "required metadata is absent"):
                mint.render_single_count_statement(value)
        for bad in ([], "bad", 1, {}):
            result = evaluation(floor_metadata=bad)
            self.assertEqual(result["outcome"], "not_estimable")
            self.assertIn("floor_artifact_invalid", result["reason_codes"])
            self.assertFalse(result["claim_ready_for_l2_l3"])

    def test_absence_and_detached_frozen_view_controls(self):
        self.assertIsNone(df.read_single_count_discipline({}, where="optional"))
        for carrier in (None, [], "bad", {"floor_limit_class": df.ATTRIBUTION_LIMIT_CLASS},
                        {"floor_source": df.ATTRIBUTION_FLOOR_SOURCE}):
            with self.assertRaises(df.SingleCountDisciplineError):
                df.read_single_count_discipline(carrier, where="required")
        with self.assertRaises(df.SingleCountDisciplineError):
            df.read_single_count_discipline({}, where="required", required=True)
        unlabelled = resolution(VERSIONS[1], floor_source=None, floor_limit_class=None,
                                point_floor_diagnostics=None, single_count_discipline=None)
        self.assertEqual(_combined_floor([unlabelled])["status"], "resolved")
        for rule_id in VERSIONS:
            wire = dict(reversed(list(df.attribution_single_count_discipline(rule_id).items())))
            view = df.read_single_count_discipline({"single_count_discipline": wire}, where="control")
            self.assertEqual(list(view.copy_wire()), list(wire))
            self.assertEqual(view.copy_wire(), wire)
            wire["both_terms_required"] = False
            detached = view.copy_wire()
            detached["rule_id"] = "bad"
            self.assertEqual(view.rule_id, rule_id)
            self.assertIs(view.copy_wire()["both_terms_required"], True)
            with self.assertRaises(FrozenInstanceError):
                view.rule_id = "bad"
            with self.assertRaises(TypeError):
                view._items[0] = ("bad", True)
            self.assertFalse(df.attribution_single_count_discipline_is_canonical(wire))


class DisciplineMutationTests(unittest.TestCase):
    def test_twelve_in_memory_mutations_fail_the_intended_assertions(self):
        import contextlib, copy, inspect, json, tempfile
        from pathlib import Path
        from unittest import mock
        from joulewise import detection_floor as df
        import joulewise.analysis_engine as ae
        from joulewise.analysis_engine import inputs
        from scripts import mint_floor_artifact as mint
        from scripts import mint_floor_artifact_generalized as gen
        from tests.test_single_count_discipline_matrix import DisciplineMatrixTests, versioned, corrupt, request_for, resolution, VERSIONS
        from tests.test_single_count_discipline_census import SingleCountCensusTests

        killed_labels = []
        DisciplineMatrixTests.setUpClass()
        case=DisciplineMatrixTests()
        v2=versioned(case.floor,VERSIONS[1]);v1=versioned(case.floor,VERSIONS[0])
        bad=corrupt(v2,('cells',0),{**df.attribution_single_count_discipline(),'rule_id':[]})
        read=df.read_single_count_discipline

        def mutant(module,name,old,new):
            source=inspect.getsource(getattr(module,name));assert old in source,(name,old)
            namespace=dict(module.__dict__);exec(compile(source.replace(old,new),f'<mutation:{name}>','exec'),namespace)
            return namespace[name]

        def refuse(call, family):
            try:call()
            except family:return
            except Exception as exc:raise AssertionError(f'wrong error family: {type(exc).__name__}') from exc
            raise AssertionError('named refusal missing')

        def admit(value):
            try:inputs.authenticate_floor_artifact_bytes(json.dumps(value).encode())
            except Exception as exc:raise AssertionError(f'valid version refused: {type(exc).__name__}') from exc

        def rejected(value):
            refuse(lambda:inputs.authenticate_floor_artifact_bytes(json.dumps(value).encode()),inputs.AnalysisInputError)

        def killed(label,patches,witness):
            with contextlib.ExitStack() as stack:
                for patch in patches:stack.enter_context(patch)
                try:witness()
                except AssertionError:
                    killed_labels.append(label)
                else:raise RuntimeError(f'SURVIVED {label}')

        canonical_view=read({'single_count_discipline':df.attribution_single_count_discipline()},where='control')
        killed('bypass accessor',[mock.patch.object(df,'read_single_count_discipline',return_value=canonical_view)],lambda:rejected(bad))
        profile=inspect.getsource(df.read_single_count_profile)
        ns=dict(df.__dict__);exec(profile.replace('root_view = admit(carrier, where)','root_view = None').replace('if profile == "extraction" and views and root_view is None:', 'if False:'),ns)
        root_bad=corrupt(versioned(case.extraction,VERSIONS[1]),(),[])
        killed('skip extraction root',[mock.patch.object(df,'read_single_count_profile',ns['read_single_count_profile']),mock.patch.object(mint,'read_single_count_profile',ns['read_single_count_profile'])],lambda:refuse(lambda:mint.render_single_count_statement(root_bad),mint.MintError))
        components=mutant(df,'read_single_count_profile','if profile == "floor" and name == "cells":','if False:')
        component_bad=corrupt(v2,('cells',0,'comparative'),[])
        killed('skip component',[mock.patch.object(df,'read_single_count_profile',components)],lambda:rejected(component_bad))
        combined=mutant(ae,'_combined_floor','for value in resolutions]','for value in resolutions if value.status != "refused"]')
        killed('skip refused resolution',[mock.patch.object(ae,'_combined_floor',combined)],lambda:refuse(lambda:ae._combined_floor([resolution(VERSIONS[1]),resolution(VERSIONS[1],status='refused',single_count_discipline=[])]),inputs.AnalysisInputError))
        hashing=mutant(df,'read_single_count_discipline','if not isinstance(rule_id, str):','hash(rule_id)\n    if not isinstance(rule_id, str):')
        killed('hash unchecked rule ID',[mock.patch.object(df,'read_single_count_discipline',hashing)],lambda:rejected(bad))
        v2only=mutant(df,'read_single_count_discipline','view_type = DisciplineV1 if rule_id == SINGLE_COUNT_DISCIPLINE_ID_V1 else DisciplineV2','if rule_id == SINGLE_COUNT_DISCIPLINE_ID_V1:\n        raise SingleCountDisciplineError("v2 only")\n    view_type = DisciplineV2')
        killed('force v2 only',[mock.patch.object(df,'read_single_count_discipline',v2only)],lambda:admit(v1))
        normalize=mutant(df,'read_single_count_discipline','return view_type(rule_id, tuple(value.items()))','return DisciplineV2(SINGLE_COUNT_DISCIPLINE_ID, tuple(attribution_single_count_discipline().items()))')
        def preserved():
            result=inputs.resolve_floor(v1,'0'*64,request_for(v1,exact=True))
            assert result.single_count_discipline==df.attribution_single_count_discipline(VERSIONS[0]),'v1 wire normalized'
        killed('normalize v1 copy',[mock.patch.object(inputs,'read_single_count_discipline',normalize)],preserved)
        mixed=corrupt(v2,('cells',0),df.attribution_single_count_discipline(VERSIONS[0]))
        killed('remove cohort',[mock.patch.object(df,'check_single_count_cohort',return_value=None)],lambda:rejected(mixed))
        equality=mutant(df,'read_single_count_discipline','type(value[key]) is not type(atom) or ','')
        bool_bad=corrupt(v2,('cells',0),{**df.attribution_single_count_discipline(),'both_terms_required':1})
        killed('restore bool/int equality',[mock.patch.object(df,'read_single_count_discipline',equality)],lambda:rejected(bool_bad))
        early=mutant(mint,'write_outputs_exclusive','statement_payload = render_single_count_statement(artifact).encode("utf-8")','_exclusive_write(floor_path, artifact_payload)\n    statement_payload = render_single_count_statement(artifact).encode("utf-8")')
        def writes():
            with tempfile.TemporaryDirectory() as tmp, mock.patch.object(mint,'_exclusive_write') as write:
                early.__globals__['_exclusive_write']=write
                refuse(lambda:early(bad,Path(tmp)/'f',Path(tmp)/'s'),mint.MintError)
                write.assert_not_called()
        killed('write before validation',[],writes)
        translation=mutant(gen,'_mint_multi_cell_floor_artifact_active','except output_core.MintError as exc:\n            raise MintError(str(exc)) from exc','except output_core.MintError:\n            raise')
        # Use the live module globals so the existing test seam patches the mutated body.
        import types
        translation=types.FunctionType(translation.__code__,gen.__dict__,translation.__name__,translation.__defaults__,translation.__closure__)
        translation.__kwdefaults__=gen._mint_multi_cell_floor_artifact_active.__kwdefaults__
        def public_refusal():
            with tempfile.TemporaryDirectory() as tmp:
                outputs=tuple(Path(tmp)/n for n in ('floor','statement','replay'))
                refuse(lambda:case._public_generalized_output(bad,outputs,False),gen.MintError)
        killed('lose generalized translation',[mock.patch.object(gen,'_mint_multi_cell_floor_artifact_active',translation)],public_refusal)
        original=Path.read_text
        def stale(path,*a,**kw):
            text=original(path,*a,**kw)
            return text.replace('attribution_floor_plus_claim_side_bound.v2','attribution_floor_plus_claim_side_bound.v1') if str(path).endswith('docs/site/adapter_contracts.html') else text
        killed('restore stale HTML',[mock.patch.object(Path,'read_text',stale)],SingleCountCensusTests().test_generated_contract_keeps_the_canonical_v2_object)
        self.assertEqual(len(killed_labels), 12)


if __name__ == "__main__":
    unittest.main()
