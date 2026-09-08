"""D-179 adversarial synthetic controls; these confer no production acceptance."""
from copy import deepcopy
import json
import math
from pathlib import Path
import statistics
import subprocess
import unittest
from unittest import mock

from joulewise import paper_reported_energy as energy
from joulewise import paper_custody as custody
from joulewise.paper_rendering import render_reported_energy
from tests.test_paper_custody import _FamilyFixture, _json_bytes, _sha


def synthetic_spec(model="qwen3-1p7b"):
    reported, floor = [], []
    for role in ("decode", "prefill-p42", "prefill-p512"):
        cell_id = f"d117-reported-mean-ph-{role}-{model}"
        phase = "decode" if role == "decode" else "prefill"
        reg = energy.reported_energy_registration(cell_id)
        members = [{"ordinal": i + 1, "bundle_id": f"{'p512' if role.endswith('p512') else 'shared'}-{i}",
                    "config_sha256": f"{i:064x}"} for i in range(50)]
        reported.append({"cell_id": cell_id, "metric": f"phase_energy_j.{phase}", "window_class": "phase",
                         "target_precheck_path": ["phase", phase], "measurand": "gross_phase_energy_j",
                         "reducer": reg["reducer"], "expected_n": 50, "members": members,
                         "missing_or_invalid_member": "refuse_reported_mean", "numeric_value": None,
                         "projection_registration": reg, "phase_ratio_estimand": reg["phase_ratio_estimand"]})
        common = {"metric": f"phase_energy_j.{phase}", "window_class": "phase"}
        pins = [{k: row[k] for k in ("bundle_id", "config_sha256")} for row in members]
        floor += [{**common, "cell_id": f"d117-df-ph-{role}-{model}-absolute", "kind": "absolute", "expected_n": 10,
                   "members": [{"slot": row["bundle_id"], "bundle_id": row["bundle_id"]} for row in members[:10]],
                   "member_config_sha256": pins[:10]},
                  {**common, "cell_id": f"d117-df-cmp-abba-ph-{role}-{model}", "kind": "comparative", "expected_n": 10,
                   "blocks": [{"block_id": f"b{i}", "members": dict(zip(("A1", "B1", "B2", "A2"),
                               [row["bundle_id"] for row in members[10 + i * 4:14 + i * 4]]))} for i in range(10)],
                   "member_config_sha256": pins[10:]}]
    return {"schema_version": "joulewise.detection_floor_extraction_spec.v1", "cells": floor,
            "reported_energy_cells": reported,
            "reported_energy_registration": {"registration_sha256": energy.registration_sha256(model)}}


def synthetic_input(model="qwen3-1p7b"):
    spec = synthetic_spec(model)
    data = []
    for cell in spec["reported_energy_cells"]:
        phase = cell["projection_registration"]["phase"]
        binding = {"cell_id": cell["cell_id"], "model": model, "extraction_spec_sha256": energy._digest(spec),
                   "selection_sha256": "a" * 64, "prompt_pin_sha256": "b" * 64,
                   "whole_window_basis_sha256": "c" * 64, "attribution_floor_j": 1.0}
        rows = []
        for i, member in enumerate(cell["members"]):
            unit = ({"kind": "repeat", "index": i + 1, "position": None} if i < 10 else
                    {"kind": "abba", "index": (i - 10) // 4 + 1, "position": ("A1", "B1", "B2", "A2")[(i - 10) % 4]})
            # Repeat stratum 10..19, block means 31.5,35.5,...67.5.
            value = 10 + i if i < 10 else 30 + (i - 10)
            output = i + 1
            prompt = 512 if "p512" in cell["cell_id"] else 42
            rows.append({"member": deepcopy(member), "model": model, "phase": phase,
                         **{k: binding[k] for k in ("selection_sha256", "prompt_pin_sha256", "whole_window_basis_sha256")},
                         "strict_valid": True, "unit": unit, "energy_j": value,
                         "bounds_j": dict(zip(energy.BOUND_KINDS, (0.1, 0.2, 0.3))),
                         "tokens": {"source": "runtime_observed", "total": prompt + output, "output": output,
                                    "prompt_realized": prompt, "tokenize_end": prompt, "prefill_start": prompt,
                                    "tokenizer_sha256": "d" * 64, "output_policy_sha256": "e" * 64}})
        data.append({"rows": rows, "binding": binding})
    return {"spec": spec, "cells": data}


class ReportedEnergyTests(unittest.TestCase):
    def setUp(self):
        self.input = synthetic_input()
        self.cell = self.input["spec"]["reported_energy_cells"][0]
        self.rows = self.input["cells"][0]["rows"]
        self.binding = self.input["cells"][0]["binding"]

    def project(self):
        return energy._project_cell(self.cell, self.rows, self.binding)

    def test_complete_control_and_stratified_half_width_not_pooled(self):
        result = self.project()
        # Independent closed sums: s_r²=55/6, s_b²=440/3, weighted mean=42.5.
        variance = 0.04 * (55 / 6) / 10 + 0.64 * (440 / 3) / 10
        half = 2.262157162798205 * math.sqrt(variance)
        self.assertAlmostEqual(result["mean_j"], 42.5)
        self.assertAlmostEqual(result["interval"]["variance"], variance)
        self.assertAlmostEqual(result["interval"]["h_j"], half)
        self.assertAlmostEqual(result["lower_j"], 42.5 - half - 0.6)
        self.assertAlmostEqual(result["upper_j"], 42.5 + half + 0.6)
        self.assertAlmostEqual(result["upper_j"] - result["lower_j"], 2 * (half + 0.6))
        self.assertAlmostEqual(result["per_token"]["j_per_token"], 2125 / 1275)
        units = list(range(10, 20)) + [31.5 + 4 * i for i in range(10)]
        pooled = 2.262157162798205 * statistics.stdev(units) / math.sqrt(20)
        self.assertGreater(abs(pooled - half), 1.0)
        self.assertEqual((result["n_bundles"], result["independence_units"]), (50, 20))

    def test_49_member_mean_refuses(self):
        self.rows.pop()
        with self.assertRaisesRegex(ValueError, "never 49"):
            self.project()

    def test_omitted_registered_member_refuses(self):
        self.cell["members"].pop()
        with self.assertRaisesRegex(ValueError, "50-member"):
            self.project()

    def test_equal_block_repeat_weighting_changes_value(self):
        self.assertEqual((14.5 + 49.5) / 2, 32)
        self.assertNotEqual(self.project()["mean_j"], 32)
        self.cell["projection_registration"]["stratum_weights"] = [0.5, 0.5]
        with self.assertRaisesRegex(ValueError, "semantics"):
            self.project()

    def test_zeroed_bound_kind_moves_endpoints(self):
        before = self.project()
        for row in self.rows:
            row["bounds_j"][energy.BOUND_KINDS[1]] = 0
        after = self.project()
        self.assertEqual(after["mean_j"], before["mean_j"])
        self.assertAlmostEqual(after["lower_j"] - before["lower_j"], 0.2)
        self.assertAlmostEqual(before["upper_j"] - after["upper_j"], 0.2)

    def test_absent_bound_kind_refuses(self):
        del self.rows[0]["bounds_j"][energy.BOUND_KINDS[1]]
        with self.assertRaisesRegex(ValueError, "bounds_j"):
            self.project()

    def test_prediction_term_substitution_refuses_by_name(self):
        self.cell["projection_registration"]["interval_method"] = energy.EXCLUDED_PREDICTION_TERM
        with self.assertRaisesRegex(ValueError, "prediction-term substitution"):
            self.project()
        self.cell["projection_registration"] = energy.reported_energy_registration(self.cell["cell_id"])
        value = self.rows[0]["bounds_j"].pop(energy.BOUND_KINDS[0])
        self.rows[0]["bounds_j"][energy.EXCLUDED_PREDICTION_TERM] = value
        with self.assertRaisesRegex(ValueError, "prediction term forbidden"):
            self.project()

    def test_configured_absent_zero_and_malformed_denominators_refuse_ratio_only(self):
        for key, value in (("source", "config"), ("source", "fallback"), ("output", 0),
                           ("output", None), ("output", True), ("tokenize_end", 99)):
            with self.subTest(key=key, value=value):
                saved = deepcopy(self.rows)
                self.rows[0]["tokens"][key] = value
                result = self.project()
                self.assertEqual(result["mean_j"], 42.5)
                self.assertEqual(result["per_token"]["status"], "refused")
                self.assertIsNone(result["per_token"]["j_per_token"])
                self.assertIsNone(result["per_token"]["observed_token_sum"])
                self.rows = saved

    def test_mean_of_ratios_changes_decode_value(self):
        wrong = statistics.fmean(row["energy_j"] / row["tokens"]["output"] for row in self.rows)
        self.assertGreater(abs(wrong - self.project()["per_token"]["j_per_token"]), 0.2)
        result = self.project()
        result["per_token"]["j_per_token"] = wrong
        with self.assertRaisesRegex(ValueError, "recomputation mismatch"):
            energy._validate_projection(result, self.cell, self.rows, self.binding)

    def test_reordered_and_duplicated_member_refuse(self):
        for duplicate in (False, True):
            saved = deepcopy(self.rows)
            if duplicate:
                self.rows[1] = deepcopy(self.rows[0])
            else:
                self.rows[0], self.rows[1] = self.rows[1], self.rows[0]
            with self.assertRaisesRegex(ValueError, "ordered identity"):
                self.project()
            self.rows = saved

    def test_swapped_model_phase_stale_pin_basis_and_invalid_member_refuse(self):
        for key, value in (("model", "qwen3-8b"), ("phase", "prefill"), ("prompt_pin_sha256", "f" * 64),
                           ("selection_sha256", "f" * 64), ("whole_window_basis_sha256", "f" * 64), ("strict_valid", False)):
            saved = deepcopy(self.rows)
            self.rows[0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.project()
            self.rows = saved

    def test_incorrect_endpoint_token_denominator_and_floor_count_refuse(self):
        for key, value in (("lower_j", 42.4), ("upper_j", 42.6), ("n_bundles", 10), ("extra", 1)):
            result = self.project()
            result[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "recomputation mismatch"):
                energy._validate_projection(result, self.cell, self.rows, self.binding)
        result = self.project()
        result["per_token"]["observed_token_sum"] = 50 * 512
        with self.assertRaisesRegex(ValueError, "recomputation mismatch"):
            energy._validate_projection(result, self.cell, self.rows, self.binding)

    def test_missing_token_object_and_scope_drift_preserve_mean(self):
        for tokens in (None, {}, {**self.rows[0]["tokens"], "tokenizer_sha256": "f" * 64},
                       {**self.rows[0]["tokens"], "output_policy_sha256": "f" * 64}):
            saved = deepcopy(self.rows)
            self.rows[0]["tokens"] = tokens
            result = self.project()
            self.assertEqual(result["mean_j"], 42.5)
            self.assertEqual(result["per_token"]["status"], "refused")
            self.rows = saved

    def test_floor_cell_swapped_model_refuses(self):
        spec = self.input["spec"]
        spec["cells"][0]["cell_id"] = "d117-df-ph-decode-qwen3-8b-absolute"
        with self.assertRaisesRegex(ValueError, "model/phase cell identity"):
            energy._validate_registered_spec(spec)

    def test_attribution_floor_is_beside_never_composed(self):
        before = self.project()
        self.binding["attribution_floor_j"] = 1000
        after = self.project()
        self.assertEqual((before["lower_j"], before["upper_j"]), (after["lower_j"], after["upper_j"]))
        self.assertFalse(after["attribution_floor_composed"])

    def test_registration_binds_cell_and_existing_ratio_remains_closed(self):
        from joulewise.analysis_engine.ratio import validate_ratio_estimand
        ratio = energy.phase_ratio_estimand(self.cell["cell_id"])
        self.assertEqual(energy.validate_phase_ratio_estimand(ratio), ratio)
        with self.assertRaises(ValueError):
            validate_ratio_estimand(ratio)
        for mutation in ({**ratio, "denominator": "configured_output_tokens"}, {**ratio, "extra": 1},
                         {**ratio, "cell_id": "prefill"}, {**ratio, "form": "mean_of_request_ratios"}):
            with self.assertRaises(ValueError):
                energy.validate_phase_ratio_estimand(mutation)

    def test_independent_floor_census_rejects_coordinated_report_reordering(self):
        spec = self.input["spec"]
        energy._validate_registered_spec(spec)
        members = spec["reported_energy_cells"][0]["members"]
        members[0], members[1] = members[1], members[0]
        members[0]["ordinal"], members[1]["ordinal"] = 1, 2
        with self.assertRaisesRegex(ValueError, "floor/config census"):
            energy._validate_registered_spec(spec)

    def test_both_models_three_cells_and_prefill_observed_totals(self):
        for model in energy.MODELS:
            result = energy._synthetic_projection(synthetic_input(model))
            self.assertEqual(len(result["cells"]), 3)
            self.assertAlmostEqual(result["cells"][1]["per_token"]["j_per_token"], 2125 / 2100)
            self.assertAlmostEqual(result["cells"][2]["per_token"]["j_per_token"], 2125 / 25600)
            self.assertEqual(result["mode"], "test_fixture_non_issuing")

    def test_source_census_covers_owner_and_gate_stays_absent(self):
        census = dict(custody._validator_source_census("reported_energy_parents"))
        for name in ("module:joulewise.paper_reported_energy", "module:joulewise.bundle_read",
                     "module:joulewise.whole_window", "paper_reported_energy._validate_projection"):
            self.assertIn(name, census)
        self.assertNotIn(("reported_energy_parents", "reported-energy.v1"), custody._ISSUANCE_GATES)

    def test_d173_is_only_evidence_entry_and_fixture_cannot_render(self):
        fixture = _FamilyFixture("reported_energy_parents")
        self.addCleanup(fixture.close)
        row = fixture.entry["inputs"][0]
        path = fixture.anchor_root / row["path"]
        document = json.loads(path.read_bytes())
        document["projection_input"] = self.input
        path.write_bytes(_json_bytes(document))
        # Reseal the temporary synthetic authority, never production data.
        supply_path = fixture.anchor_root / custody._SUPPLY_MAP_PATH
        supply = json.loads(supply_path.read_bytes())
        entry = supply["roles"][fixture.role]
        entry["inputs"][0]["expected_sha256"] = _sha(path.read_bytes())
        receipt_path = fixture.runs_root / entry["receipt"]["path"]
        receipt = json.loads(receipt_path.read_bytes())
        next(r for r in receipt["inputs"] if r["role"] == "extraction_spec")["sha256"] = _sha(path.read_bytes())
        receipt_path.write_bytes(_json_bytes(receipt))
        entry["receipt"]["expected_sha256"] = _sha(receipt_path.read_bytes())
        inv_path = fixture.runs_root / entry["inventory"]["path"]
        inv = json.loads(inv_path.read_bytes())
        for r in inv["files"]:
            if r["role"] == "extraction_spec": r["sha256"] = _sha(path.read_bytes())
            if r["role"] == "validator_receipt": r["sha256"] = _sha(receipt_path.read_bytes())
        inv_path.write_bytes(_json_bytes(inv))
        entry["inventory"]["expected_sha256"] = _sha(inv_path.read_bytes())
        supply_path.write_bytes(_json_bytes(supply))
        subprocess.run(["git", "add", "."], cwd=fixture.anchor_root, check=True)
        subprocess.run(["git", "commit", "-qm", "synthetic projection"], cwd=fixture.anchor_root, check=True)
        fixture.head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=fixture.anchor_root, text=True).strip()
        value = custody.open_paper_input(fixture.ref)
        self.assertIs(type(value), custody.FixtureReportedEnergyParents)
        projection = dict(value._payload.fields)["reported_energy_projection"]
        self.assertIn("cells", dict(projection.fields))
        with self.assertRaises(custody.PaperCustodyRefusal):
            render_reported_energy(value)
        for bypass in (self.input, path, _sha(path.read_bytes())):
            with self.assertRaises(custody.PaperCustodyRefusal):
                custody.open_paper_input(bypass)


if __name__ == "__main__":
    unittest.main()
