"""D-179 adversarial synthetic controls; these confer no production acceptance."""
from contextlib import contextmanager
from copy import deepcopy
import json
import math
from pathlib import Path
import statistics
import subprocess
import tempfile
import unittest
from unittest import mock

from joulewise import paper_reported_energy as energy
from joulewise import paper_custody as custody
from joulewise.paper_rendering import render_reported_energy
from tests.test_paper_custody import _FamilyFixture, _json_bytes, _sha
from tests.git_fixture import init_git_fixture


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

    @contextmanager
    def assert_code(self, reason):
        with self.assertRaises(energy.PaperReportedEnergyRefusal) as raised:
            yield
        self.assertEqual(raised.exception.code, "paper_reported_energy_" + reason)
        self.assertEqual(raised.exception.rendered_output, ())

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
        with self.assert_code("member_count_invalid"):
            self.project()

    def test_omitted_registered_member_refuses(self):
        self.cell["members"].pop()
        with self.assert_code("member_count_invalid"):
            self.project()

    def test_equal_block_repeat_weighting_changes_value(self):
        self.assertEqual((14.5 + 49.5) / 2, 32)
        self.assertNotEqual(self.project()["mean_j"], 32)
        self.cell["projection_registration"]["stratum_weights"] = [0.5, 0.5]
        with self.assert_code("registration_invalid"):
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
        with self.assert_code("schema_invalid"):
            self.project()

    def test_prediction_term_substitution_refuses_by_name(self):
        self.cell["projection_registration"]["interval_method"] = energy.EXCLUDED_PREDICTION_TERM
        with self.assert_code("registration_invalid"):
            self.project()
        self.cell["projection_registration"] = energy.reported_energy_registration(self.cell["cell_id"])
        value = self.rows[0]["bounds_j"].pop(energy.BOUND_KINDS[0])
        self.rows[0]["bounds_j"][energy.EXCLUDED_PREDICTION_TERM] = value
        with self.assert_code("schema_invalid"):
            self.project()

    def test_configured_absent_zero_and_malformed_denominators_refuse_ratio_only(self):
        for key, value in (("source", "config"), ("source", "fallback"), ("output", 0),
                           ("output", None), ("output", True)):
            with self.subTest(key=key, value=value):
                saved = deepcopy(self.rows)
                self.rows[0]["tokens"][key] = value
                result = self.project()
                self.assertEqual(result["mean_j"], 42.5)
                self.assertEqual(result["per_token"]["status"], "refused")
                self.assertIsNone(result["per_token"]["j_per_token"])
                self.assertIsNone(result["per_token"]["observed_token_sum"])
                self.assertEqual(result["per_token"]["reason"], "paper_reported_energy_denominator_invalid")
                self.rows = saved

    def test_decode_ignores_prompt_surfaces_but_prefill_requires_agreement(self):
        for mutation in ({"tokenize_end": (42, 99)}, {"total": None},
                         {"prompt_realized": 0, "prefill_start": ()}):
            for index in (0, 1):
                data = synthetic_input()
                data["cells"][index]["rows"][0]["tokens"].update(mutation)
                result = energy._project_cell(data["spec"]["reported_energy_cells"][index], **data["cells"][index])
                with self.subTest(index=index, mutation=mutation):
                    self.assertEqual(result["mean_j"], 42.5)
                    self.assertEqual(result["per_token"]["status"], "computed" if index == 0 else "refused")
                    expected_reason = (None if index == 0 else "paper_reported_energy_" +
                                       ("prompt_surfaces_disagree" if "tokenize_end" in mutation else "denominator_invalid"))
                    self.assertEqual(result["per_token"]["reason"], expected_reason)
                    if index == 0:
                        self.assertAlmostEqual(result["per_token"]["j_per_token"], 2125 / 1275)
        for row in self.rows:
            row["tokens"] = {key: row["tokens"][key] for key in
                             ("source", "output", "tokenizer_sha256", "output_policy_sha256")}
        self.assertEqual(self.project()["per_token"]["status"], "computed")

    def test_prefill_tuple_surfaces_collapse_or_refuse_named_code(self):
        data = self.input["cells"][1]
        cell = self.input["spec"]["reported_energy_cells"][1]
        for row in data["rows"]:
            row["tokens"].update(tokenize_end=(42, 42), prefill_start=(42, 42, 42))
        self.assertEqual(energy._collapse_prompt_tokens(data["rows"][0]["tokens"]), 42)
        self.assertEqual(energy._project_cell(cell, **data)["per_token"]["status"], "computed")
        data["rows"][0]["tokens"]["prefill_start"] = (42, 43)
        with self.assert_code("prompt_surfaces_disagree"):
            energy._collapse_prompt_tokens(data["rows"][0]["tokens"])
        result = energy._project_cell(cell, **data)
        self.assertEqual(result["per_token"]["reason"], "paper_reported_energy_prompt_surfaces_disagree")
        self.assertEqual(result["mean_j"], 42.5)

    def test_nonpositive_prefill_denominator_precedes_surface_disagreement(self):
        for total in (0, 1):
            with self.subTest(total=total):
                data = synthetic_input()
                record = data["cells"][1]
                tokens = record["rows"][0]["tokens"]
                tokens.update(total=total, output=1, prompt_realized=42,
                              tokenize_end=(42, 42), prefill_start=(42, 42))
                with self.assert_code("denominator_invalid"):
                    energy._collapse_prompt_tokens(tokens)
                result = energy._project_cell(data["spec"]["reported_energy_cells"][1], **record)
                self.assertEqual(result["mean_j"], 42.5)
                self.assertEqual(result["per_token"]["status"], "refused")
                self.assertIsNone(result["per_token"]["j_per_token"])
                self.assertEqual(result["per_token"]["reason"], "paper_reported_energy_denominator_invalid")

    def test_closed_refusal_vocabulary_matches_contract(self):
        import re
        contract = (Path(__file__).resolve().parents[1] / "docs/contracts/paper_reported_energy.md").read_text()
        self.assertEqual(set(re.findall(r"`(paper_reported_energy_[a-z_]+)`", contract)),
                         energy.PAPER_REPORTED_ENERGY_REFUSAL_CODES)
        self.assertEqual(energy.PaperReportedEnergyRefusal("invented").code,
                         "paper_reported_energy_request_invalid")
        with self.assert_code("request_invalid"):
            energy._validate_projection({"bad": object()}, self.cell, self.rows, self.binding)

    def test_gate_registration_and_dispatch_require_ordering_for_both_models(self):
        from types import SimpleNamespace
        key = ("reported_energy_parents", "synthetic-ordering.v1")
        gate = mock.Mock(return_value=custody._FamilyReplay(True, False, (), ()))
        repository = Path("synthetic-repository")
        ctx = SimpleNamespace(family=key[0], issuance_gate_id=key[1],
                              mode="production", repository=repository)
        def proof(repo, model):
            self.assertEqual(repo, repository)
            return {"registration_commit": "a" * 40, "spec_commit": "b" * 40,
                    "registration_sha256": energy.registration_sha256(model)}
        with mock.patch.dict(custody._ISSUANCE_GATES, clear=True):
            for missing in (True, False):
                with self.subTest(missing=missing):
                    def check(repo, model):
                        if model == energy.MODELS[0]:
                            return proof(repo, model)
                        if missing:
                            return None
                        raise energy.PaperReportedEnergyRefusal(
                            "paper_reported_energy_registration_not_before_spec")
                    reason = "ordering_history_invalid" if missing else "registration_not_before_spec"
                    with mock.patch.object(energy, "verify_registration_ordering", side_effect=check):
                        with self.assert_code(reason):
                            custody._register_reported_energy_gate(key[1], gate, repository=repository)
                        self.assertNotIn(key, custody._ISSUANCE_GATES)
                        # A direct insertion still cannot invoke an unchecked gate.
                        custody._ISSUANCE_GATES[key] = gate
                        with self.assert_code(reason):
                            custody._run_issuance_gate(ctx)
                        gate.assert_not_called()
                        del custody._ISSUANCE_GATES[key]
            with mock.patch.object(energy, "verify_registration_ordering", side_effect=proof) as checked:
                custody._register_reported_energy_gate(key[1], gate, repository=repository)
                self.assertEqual(checked.call_args_list,
                                 [mock.call(repository, model) for model in energy.MODELS])
                checked.reset_mock()
                self.assertIs(custody._run_issuance_gate(ctx), gate.return_value)
                self.assertEqual(checked.call_args_list,
                                 [mock.call(repository, model) for model in energy.MODELS])
                gate.assert_called_once_with(ctx)

    def test_registration_ordering_in_synthetic_git_repositories(self):
        source = Path(energy.__file__).read_bytes()
        for model in energy.MODELS:
            for order in ("registration_first", "spec_first", "same_commit", "digest_mismatch", "absent_spec"):
                with self.subTest(model=model, order=order), tempfile.TemporaryDirectory() as tmp:
                    repo = Path(tmp)
                    def git(*args):
                        return subprocess.check_output(["git", "-C", tmp, *args], stderr=subprocess.STDOUT, text=True).strip()
                    init_git_fixture(repo, "-q")
                    git("config", "user.email", "synthetic@example.invalid")
                    git("config", "user.name", "Synthetic test")
                    registration = repo / "joulewise/paper_reported_energy.py"
                    spec = repo / f"configs/campaigns/d117_floor_{model}_v5/extraction_spec.json"
                    registration.parent.mkdir(parents=True)
                    spec.parent.mkdir(parents=True)
                    spec_bytes = json.dumps({"reported_energy_registration": {"registration_sha256":
                        "0" * 64 if order == "digest_mismatch" else energy.registration_sha256(model)}}).encode()
                    paths = [(registration, source), (spec, spec_bytes)]
                    if order == "spec_first":
                        paths.reverse()
                    if order == "absent_spec":
                        paths = paths[:1]
                    for path, raw in paths:
                        path.write_bytes(raw)
                        if order != "same_commit":
                            git("add", ".")
                            git("commit", "-qm", path.name)
                    if order == "same_commit":
                        git("add", ".")
                        git("commit", "-qm", "both")
                    if order == "registration_first":
                        result = energy.verify_registration_ordering(repo, model)
                        self.assertEqual(result["registration_sha256"], energy.registration_sha256(model))
                        self.assertNotEqual(result["registration_commit"], result["spec_commit"])
                    else:
                        reason = {"digest_mismatch": "registration_digest_mismatch", "absent_spec": "ordering_history_invalid"}.get(
                            order, "registration_not_before_spec")
                        with self.assert_code(reason):
                            energy.verify_registration_ordering(repo, model)

    def test_mean_of_ratios_changes_decode_value(self):
        wrong = statistics.fmean(row["energy_j"] / row["tokens"]["output"] for row in self.rows)
        self.assertGreater(abs(wrong - self.project()["per_token"]["j_per_token"]), 0.2)
        result = self.project()
        result["per_token"]["j_per_token"] = wrong
        with self.assert_code("projection_mismatch"):
            energy._validate_projection(result, self.cell, self.rows, self.binding)

    def test_reordered_and_duplicated_member_refuse(self):
        for duplicate in (False, True):
            saved = deepcopy(self.rows)
            if duplicate:
                self.rows[1] = deepcopy(self.rows[0])
            else:
                self.rows[0], self.rows[1] = self.rows[1], self.rows[0]
            with self.assert_code("record_identity_mismatch"):
                self.project()
            self.rows = saved

    def test_swapped_model_phase_stale_pin_basis_and_invalid_member_refuse(self):
        for key, value in (("model", "qwen3-8b"), ("phase", "prefill"), ("prompt_pin_sha256", "f" * 64),
                           ("selection_sha256", "f" * 64), ("whole_window_basis_sha256", "f" * 64), ("strict_valid", False)):
            saved = deepcopy(self.rows)
            self.rows[0][key] = value
            with self.subTest(key=key), self.assert_code("record_invalid" if key == "strict_valid" else "record_identity_mismatch"):
                self.project()
            self.rows = saved

    def test_incorrect_endpoint_token_denominator_and_floor_count_refuse(self):
        for key, value in (("lower_j", 42.4), ("upper_j", 42.6), ("n_bundles", 10), ("extra", 1)):
            result = self.project()
            result[key] = value
            with self.subTest(key=key), self.assert_code("projection_mismatch"):
                energy._validate_projection(result, self.cell, self.rows, self.binding)
        result = self.project()
        result["per_token"]["observed_token_sum"] = 50 * 512
        with self.assert_code("projection_mismatch"):
            energy._validate_projection(result, self.cell, self.rows, self.binding)

    def test_missing_token_object_and_scope_drift_preserve_mean(self):
        for tokens in (None, {}, {**self.rows[0]["tokens"], "tokenizer_sha256": "f" * 64},
                       {**self.rows[0]["tokens"], "output_policy_sha256": "f" * 64}):
            saved = deepcopy(self.rows)
            self.rows[0]["tokens"] = tokens
            result = self.project()
            self.assertEqual(result["mean_j"], 42.5)
            self.assertEqual(result["per_token"]["status"], "refused")
            self.assertEqual(result["per_token"]["reason"], "paper_reported_energy_" +
                             ("denominator_invalid" if not tokens else "token_scope_mismatch"))
            self.rows = saved

    def test_floor_cell_swapped_model_refuses(self):
        spec = self.input["spec"]
        spec["cells"][0]["cell_id"] = "d117-df-ph-decode-qwen3-8b-absolute"
        with self.assert_code("floor_identity_mismatch"):
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
            with self.assert_code("cell_identity_invalid" if mutation["cell_id"] == "prefill" else "ratio_estimand_invalid"):
                energy.validate_phase_ratio_estimand(mutation)

    def test_independent_floor_census_rejects_coordinated_report_reordering(self):
        spec = self.input["spec"]
        energy._validate_registered_spec(spec)
        members = spec["reported_energy_cells"][0]["members"]
        members[0], members[1] = members[1], members[0]
        members[0]["ordinal"], members[1]["ordinal"] = 1, 2
        with self.assert_code("floor_member_mismatch"):
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
        projection = value.reported_energy_projection
        self.assertIn("cells", dict(projection.fields))
        with self.assertRaises(custody.PaperCustodyRefusal):
            render_reported_energy(value)
        for bypass in (self.input, path, _sha(path.read_bytes())):
            with self.assertRaises(custody.PaperCustodyRefusal):
                custody.open_paper_input(bypass)


if __name__ == "__main__":
    unittest.main()
