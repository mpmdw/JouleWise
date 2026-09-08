"""D-178 copy-boundary controls; all values here are synthetic, non-issuing."""
from __future__ import annotations

import copy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import unittest

from joulewise.analysis_engine import claim_side_bound as bound
from joulewise.analysis_engine.ratio import RATIO_ESTIMAND_KEYS, validate_ratio_estimand
from tests.test_analysis_manifest import ratio_estimand
from joulewise.analysis_engine.estimators import (
    DeterministicBoundTerm, PairedObservation, estimate_paired_blocks,
)


def encoded(value):
    return json.dumps(value, separators=(",", ":"), allow_nan=False).encode()


def source_fixture():
    # Two blocks: the anchor has an explicit contrast bound (precedence matters).
    # Anchor mean = 1, other-kind mean = 3, B = 4; summing blocks gives 8.
    observations = [PairedObservation(
        block_id=f"b{i}", value_a=0, value_b=10 + i,
        deterministic_terms=(
            DeterministicBoundTerm(bound._ANCHOR, 7, 8, contrast_bound=anchor),
            DeterministicBoundTerm("interpolation", edge, 0),
        )) for i, (anchor, edge) in enumerate(((0.5, 2), (1.5, 4)))]
    estimate = estimate_paired_blocks(observations)
    contrast = {"contrast_id": "synthetic", "metric": {"unit": "J", "ratio_estimand": None},
                "estimator": {"name": estimate.estimator,
                              "metrology_aware_CI95": asdict(estimate.metrology_aware_ci95)},
                "deterministic_bounds": {"total": estimate.deterministic_bound_total,
                                         "terms": [asdict(term) for term in estimate.deterministic_bounds],
                                         "decision_interval": asdict(estimate.decision_interval)},
                "floor": {"resolutions": [{"status": "transported", "source_cell_ids": ["a", "b"]},
                                            {"status": "exact", "source_cell_ids": ["a"]}]}}
    manifest = {"contrasts": [{"contrast_id": "synthetic", "floor_estimator_registration": {}}]}
    floor = {"artifact_id": "synthetic-floor", "cells": [{"cell_id": "a"}, {"cell_id": "b"}]}
    return {"contrasts": [contrast]}, manifest, floor


class ClaimSideBoundTests(unittest.TestCase):
    def setUp(self):
        self.verdicts, self.manifest, self.floor = source_fixture()
        self.raw = encoded(self.verdicts)
        self.sidecar_raw = self.produce()
        self.sidecar = json.loads(self.sidecar_raw)

    def produce(self, raw=None):
        return bound.produce_claim_side_bound(
            self.raw if raw is None else raw, finalized_manifest=self.manifest, floor_artifact=self.floor)

    def validate(self, raw, verdicts_raw=None):
        return bound.validate_claim_side_bound(
            raw, claim_verdicts_raw=self.raw if verdicts_raw is None else verdicts_raw,
            finalized_manifest=self.manifest, floor_artifact=self.floor)

    def mutate(self, change, code="paper_claim_side_bound_copy_mismatch"):
        self.assertEqual(self.validate(self.sidecar_raw), ())
        bad = copy.deepcopy(self.sidecar)
        change(bad["contrasts"][0])
        self.assertEqual(self.validate(encoded(bad)), (code,))

    def test_copy_only_control(self):
        contrast = self.verdicts["contrasts"][0]
        row = self.sidecar["contrasts"][0]
        self.assertEqual(contrast["deterministic_bounds"]["total"], 4.0)
        self.assertEqual(row["deterministic_widening_total"], 4.0)
        self.assertEqual(row["deterministic_terms"], contrast["deterministic_bounds"]["terms"])
        self.assertEqual(row["decision_interval"], contrast["deterministic_bounds"]["decision_interval"])
        self.assertEqual(row["metrology_aware_CI95"], contrast["estimator"]["metrology_aware_CI95"])
        self.assertEqual(row["source_cell_ids"], ["a", "b", "a"])
        self.assertNotIn("source_cell_ids", self.manifest["contrasts"][0])
        self.assertEqual(self.sidecar["schema_version"], "joulewise.claim_side_bound.v2")
        self.assertEqual(self.sidecar["claim_verdicts_sha256"], hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(self.produce(), self.sidecar_raw)
        self.assertEqual(self.validate(self.sidecar_raw), ())
        self.assertEqual(bound.claim_side_bound_diagnostics(self.sidecar_raw), ())

    def test_anchor_only_substitution(self):
        self.mutate(lambda row: row.update(deterministic_widening_total=1.0))

    def test_dropped_kind(self):
        self.mutate(lambda row: row["deterministic_terms"].pop())

    def test_sum_for_mean(self):
        self.mutate(lambda row: row.update(deterministic_widening_total=8.0))

    def test_precedence_flip(self):
        self.mutate(lambda row: row.update(deterministic_widening_total=18.0))

    def test_decision_fed_as_ci95(self):
        self.mutate(lambda row: row.update(metrology_aware_CI95=copy.deepcopy(row["decision_interval"])))

    def test_double_widen(self):
        def change(row):
            row["decision_interval"]["lower"] -= 4.0
            row["decision_interval"]["upper"] += 4.0
        self.mutate(change)

    def test_edited_interval_matching_scalar(self):
        def change(row):
            row["deterministic_widening_total"] = 5.0
            row["decision_interval"]["lower"] -= 1.0
            row["decision_interval"]["upper"] += 1.0
        self.mutate(change)

    def test_ci_recomputed_from_decision(self):
        # Coherent arithmetic cannot replace endpoint provenance.
        def change(row):
            row["metrology_aware_CI95"] = copy.deepcopy(row["decision_interval"])
            row["decision_interval"]["lower"] -= 4.0
            row["decision_interval"]["upper"] += 4.0
        self.mutate(change)

    def test_drift_1e13(self):
        self.mutate(lambda row: row.update(deterministic_widening_total=4.0 + 1e-13))

    def test_sign_flip(self):
        self.mutate(lambda row: row["decision_interval"].update(
            lower=row["metrology_aware_CI95"]["lower"] + 4.0))

    def test_permuted_cells(self):
        self.mutate(lambda row: row.update(source_cell_ids=["b", "a", "a"]),
                    "paper_claim_side_bound_cell_mismatch")

    def test_deduplicated_cells(self):
        self.mutate(lambda row: row.update(source_cell_ids=["a", "b"]),
                    "paper_claim_side_bound_cell_mismatch")

    def test_refused_resolution(self):
        self.verdicts["contrasts"][0]["floor"]["resolutions"][0]["status"] = "refused"
        self.assert_source_refuses("paper_claim_side_bound_cell_mismatch")

    def assert_source_refuses(self, code):
        raw = encoded(self.verdicts)
        with self.assertRaises(bound.ClaimSideBoundRefusal) as raised:
            self.produce(raw)
        self.assertEqual(raised.exception.code, code)
        self.assertEqual(self.validate(self.sidecar_raw, raw), (code,))

    def test_anchor_required(self):
        self.verdicts["contrasts"][0]["deterministic_bounds"]["terms"].pop(0)
        self.assert_source_refuses("paper_claim_side_bound_anchor_missing")

    def test_join_injective(self):
        other = copy.deepcopy(self.verdicts["contrasts"][0]); other["contrast_id"] = "other"
        self.verdicts["contrasts"].append(other)
        self.manifest["contrasts"].append({"contrast_id": "other", "floor_estimator_registration": {}})
        self.assert_source_refuses("paper_claim_side_bound_join_not_injective")

    def registry_units(self):
        root = Path(__file__).resolve().parents[1] / "configs/analysis_registry"
        vocabularies = [
            {row["unit"] for row in json.loads((root / name).read_bytes())["estimands"]}
            for name in ("ap_spec_draft_front.v2.json", "ap_spec_native_mtp_front.v2.json")
        ]
        self.assertEqual(vocabularies[0], vocabularies[1])
        return vocabularies[0]

    def test_unit_vocabulary_matches_both_registries(self):
        self.assertEqual(bound._UNITS, self.registry_units())
        for unit in ("J/token", "kJ", "", None):
            with self.subTest(unit=unit):
                self.verdicts["contrasts"][0]["metric"]["unit"] = unit
                self.assert_source_refuses("paper_claim_side_bound_unit_mismatch")

    def test_ratio_in_j_cell(self):
        for unit in sorted(self.registry_units() - {"J"}):
            for form, estimator in (("mean_of_request_ratios", "paired_mean_student_t_v1"),
                                    ("ratio_of_totals", "ratio_of_totals_delete_one_block_jackknife_t_v1")):
                with self.subTest(unit=unit, form=form):
                    # Use the existing B8 fixture and validate it with its owner.
                    ratio = ratio_estimand(form)
                    self.assertEqual(set(ratio), RATIO_ESTIMAND_KEYS)
                    self.assertEqual(validate_ratio_estimand(ratio), ratio)
                    row = self.verdicts["contrasts"][0]
                    row["metric"].update(unit=unit, ratio_estimand=ratio)
                    row["estimator"]["name"] = estimator
                    self.raw = encoded(self.verdicts)
                    self.sidecar_raw = self.produce(); self.sidecar = json.loads(self.sidecar_raw)
                    self.assertEqual(self.sidecar["contrasts"][0]["ratio_estimand"], ratio)
                    self.assertEqual(self.sidecar["contrasts"][0]["unit"], unit)
                    self.mutate(lambda row: row.update(unit="J"), "paper_claim_side_bound_unit_mismatch")
                    for key in ("claim_side_bound_j", "another_j", "B_decode_claim_J"):
                        bad = copy.deepcopy(self.sidecar)
                        bad["contrasts"][0][key] = bad["contrasts"][0].pop("deterministic_widening_total")
                        self.assertEqual(self.validate(encoded(bad)), ("paper_claim_side_bound_shape_invalid",))
        self.verdicts["contrasts"][0]["metric"]["unit"] = "J"
        self.assert_source_refuses("paper_claim_side_bound_unit_mismatch")

    def test_ratio_requires_exact_b8_object(self):
        valid = ratio_estimand("ratio_of_totals")
        for ratio in (None, "ratio_of_totals", {"form": "ratio_of_totals"},
                      dict(valid, extra="value"), dict(valid, denominator="invented")):
            with self.subTest(ratio=ratio):
                self.verdicts["contrasts"][0]["metric"].update(
                    unit="J/committed_output_token", ratio_estimand=ratio)
                self.assert_source_refuses("paper_claim_side_bound_unit_mismatch")

    def test_companion_estimands_share_ordered_cells(self):
        for form in ("mean_of_request_ratios", "ratio_of_totals"):
            companion = copy.deepcopy(self.verdicts["contrasts"][0])
            companion["contrast_id"] = form
            companion["metric"].update(unit="J/committed_output_token", ratio_estimand=ratio_estimand(form))
            self.verdicts["contrasts"].append(companion)
            self.manifest["contrasts"].append({"contrast_id": form, "floor_estimator_registration": {}})
        raw = encoded(self.verdicts)
        result = self.produce(raw)
        self.assertEqual(self.validate(result, raw), ())
        rows = json.loads(result)["contrasts"]
        self.assertEqual(len(rows), 3)
        self.assertIsNone(rows[0]["ratio_estimand"])
        self.assertTrue(all(row["source_cell_ids"] == ["a", "b", "a"] for row in rows))
        # Same ratio kind still collides even if the registered unit differs.
        duplicate = copy.deepcopy(self.verdicts["contrasts"][-1])
        duplicate["contrast_id"] = "same-kind-other-unit"
        duplicate["metric"]["unit"] = "J/accepted_draft_token"
        self.verdicts["contrasts"].append(duplicate)
        self.manifest["contrasts"].append({"contrast_id": duplicate["contrast_id"]})
        self.assert_source_refuses("paper_claim_side_bound_join_not_injective")

    def test_extreme_exponents_refuse_through_both_apis(self):
        for token in (b"0e9999999999999999999", b"1e-9999999999999999999"):
            for old in (b'"total":4.0', b'"lower":4.147', b'"upper":16.853'):
                with self.subTest(token=token, field=old):
                    raw = self.raw.replace(old, old.split(b":")[0] + b":" + token)
                    self.assertNotEqual(raw, self.raw)
                    with self.assertRaises(bound.ClaimSideBoundRefusal) as raised:
                        self.produce(raw)
                    self.assertEqual(raised.exception.code, "paper_claim_side_bound_numeral_unparseable")
                    self.assertEqual(self.validate(self.sidecar_raw, raw),
                                     ("paper_claim_side_bound_numeral_unparseable",))

    def test_bool_rejected(self):
        for key in ("deterministic_widening_total", "decision_interval", "metrology_aware_CI95", "deterministic_terms"):
            def change(row):
                if key in {"decision_interval", "metrology_aware_CI95"}:
                    row[key]["lower"] = True
                elif key == "deterministic_terms":
                    row[key][0]["bound"] = True
                else:
                    row[key] = True
            self.mutate(change)
        self.verdicts["contrasts"][0]["deterministic_bounds"]["total"] = True
        self.assert_source_refuses("paper_claim_side_bound_shape_invalid")

    def test_numeral_bytes_not_numeric_equality(self):
        # Includes equivalent spellings and values that collapse to one float.
        for old, new in ((b'"total":4.0', b'"total":4.00000000000000000001'),
                         (b'"total":4.0', b'"total":4e0')):
            with self.subTest(new=new):
                source = self.raw.replace(old, new)
                self.assertNotEqual(source, self.raw)
                result = self.produce(source)
                token = new.split(b":")[1]
                self.assertIn(b'"deterministic_widening_total":' + token, result)
                self.assertEqual(self.validate(result, source), ())
                altered = result.replace(b'"deterministic_widening_total":' + token,
                                         b'"deterministic_widening_total":4.0')
                self.assertEqual(self.validate(altered, source), ("paper_claim_side_bound_copy_mismatch",))
        for key in (b'"lower":', b'"upper":', b'"bound":'):
            # No serializer may normalize interval/component numeral spelling either.
            import re
            altered = re.sub(rb'(' + key + rb')(-?\d+(?:\.\d+)?)', rb'\g<1>\g<2>e0', self.sidecar_raw, count=1)
            self.assertNotEqual(altered, self.sidecar_raw)
            self.assertEqual(self.validate(altered), ("paper_claim_side_bound_copy_mismatch",))

    def test_source_number_domains_do_not_round_before_validation(self):
        tiny_negative = self.raw.replace(b'"total":4.0', b'"total":-1e-9999')
        self.assertNotEqual(tiny_negative, self.raw)
        self.assertEqual(self.validate(self.sidecar_raw, tiny_negative),
                         ("paper_claim_side_bound_shape_invalid",))
        self.verdicts["contrasts"][0]["estimator"]["metrology_aware_CI95"] = {"lower": 1.0, "upper": 1.0}
        inverted = encoded(self.verdicts).replace(b'"lower":1.0', b'"lower":1.00000000000000000001')
        self.assertEqual(self.validate(self.sidecar_raw, inverted),
                         ("paper_claim_side_bound_shape_invalid",))

    def test_gate_reevaluates_verdicts_with_real_copy_validator(self):
        # Isolate the gate from the stale committed fixture receipt pins. The
        # owner/disk/acceptance boundaries are mocks, so this is NOT custody proof.
        import base64
        from pathlib import Path
        from types import SimpleNamespace
        from unittest import mock
        from joulewise import paper_custody as custody
        from joulewise.analysis_engine.claims import evaluate_claim
        contrast = self.verdicts["contrasts"][0]
        contrast.update(claim_role="primary", sampling={"confirmatory_status": "confirmatory"},
                        multiplicity={"rejected": False},
                        claim_evaluation={"reason_codes": [], "claim_ready_for_l2_l3": True})
        contrast["estimator"]["estimate"] = 10.5
        contrast["floor"]["active_floor_j"] = 2
        floor_raw = encoded(self.floor)
        self.verdicts.update(evidence_class="current", inputs={"floor_artifact": {
            "embedded_bytes_base64": base64.b64encode(floor_raw).decode()}})
        self.raw = encoded(self.verdicts)
        raws = {custody.InputRole.CLAIM_VERDICTS: self.raw,
                custody.InputRole.CLAIM_SIDE_BOUND: self.produce(),
                custody.InputRole.FLOOR_ARTIFACT: floor_raw,
                custody.InputRole.FINALIZED_MANIFEST: encoded(self.manifest)}
        binding = SimpleNamespace(role=custody.InputRole.FINALIZED_MANIFEST,
                                  base="repository", path=Path("synthetic-manifest.json"))
        ctx = SimpleNamespace(raws=raws, sources=(binding,), repository=Path("."),
                              runs_root=Path("."), subjects=("synthetic",))
        with (mock.patch("joulewise.analysis_engine.artifact.validate_claim_verdicts", return_value=[]),
              mock.patch("joulewise.analysis_manifest_v3.validate_finalized_analysis_manifest_v3", return_value=[]),
              mock.patch.object(custody, "_validate_floor_acceptance") as acceptance,
              mock.patch("joulewise.analysis_engine.claims.evaluate_claim", wraps=evaluate_claim) as evaluate):
            result = custody._claim_issuance_gate(ctx)
            self.assertTrue(result.authentic)
            self.assertTrue(result.admitted)
            self.assertEqual([(grant.kind, grant.subject_id) for grant in result.grants], [("outcome", "synthetic")])
            self.assertEqual(evaluate.call_args.kwargs["decision_interval"], contrast["deterministic_bounds"]["decision_interval"])
            self.assertEqual(evaluate.call_args.kwargs["metrology_aware_ci95"], contrast["estimator"]["metrology_aware_CI95"])
            acceptance.assert_called_once_with(ctx)
            bad = json.loads(raws[custody.InputRole.CLAIM_SIDE_BOUND])
            bad["contrasts"][0]["deterministic_widening_total"] += 1e-13
            raws[custody.InputRole.CLAIM_SIDE_BOUND] = encoded(bad)
            evaluate.reset_mock()
            self.assertFalse(custody._claim_issuance_gate(ctx).authentic)
            evaluate.assert_not_called()

    def test_shape_digest_lineage_and_identity(self):
        for key, value, code in (("contrast_id", "other", "contrast_mismatch"),
                                 ("floor_artifact_id", "other", "lineage_mismatch"),
                                 ("estimator_id", "other", "unit_mismatch"),
                                 ("ratio_estimand", "ratio_of_totals", "unit_mismatch")):
            self.mutate(lambda row: row.update({key: value}), "paper_claim_side_bound_" + code)
        for key, value, code in (("schema_version", "joulewise.claim_side_bound.v1", "shape_invalid"),
                                 ("claim_verdicts_sha256", "0" * 64, "reader_digest_mismatch"),
                                 ("contrasts", [], "contrast_mismatch")):
            bad = copy.deepcopy(self.sidecar); bad[key] = value
            self.assertEqual(self.validate(encoded(bad)), ("paper_claim_side_bound_" + code,))
        for raw in (b'{"a":1,"a":2}', b'{"a":NaN}', b'[]', b'\xff', self.sidecar):
            self.assertEqual(self.validate(raw), ("paper_claim_side_bound_shape_invalid",))
        with self.assertRaises(bound.ClaimSideBoundRefusal):
            self.produce(self.verdicts)


if __name__ == "__main__":
    unittest.main()
