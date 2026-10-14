import copy
import json
import unittest

from joulewise.b6 import model_files
from tests.b6.support import IDENTITY, ROOT


class ModelFileTests(unittest.TestCase):
    def setUp(self):
        self.pins = {"runtime_versions": {"packages": IDENTITY["packages"]}, "units": {"one": {
            "model_source": IDENTITY["model_source"], "model_artifact_sha256": IDENTITY["model_artifact_sha256"],
            "stack_identity": {"runtime_version": {"name": "mlx"}, "quantization": IDENTITY["quantization"]}}}}
        self.expected = model_files.expected(self.pins)

    def test_clean_and_multiple_units_for_one_source(self):
        self.pins["units"]["two"] = copy.deepcopy(self.pins["units"]["one"])
        self.assertEqual(model_files.compare(model_files.expected(self.pins), IDENTITY), [])
        self.assertEqual(len(self.expected["models"]["synthetic-model"]["sha256s"]), 1)

    def test_files_differ(self):
        rows = model_files.compare(self.expected, {**IDENTITY, "model_artifact_sha256": "b" * 64})
        self.assertEqual(rows[0]["code"], "model.files_differ_from_registered")

    def test_each_computation_field_differs(self):
        changes = [{"runtime": "other"}, {"quantization": {"name": "int8"}}]
        changes.extend({"packages": {**IDENTITY["packages"], key: "other"}} for key in model_files.PACKAGES)
        for change in changes:
            with self.subTest(change=change):
                self.assertEqual(model_files.compare(self.expected, {**IDENTITY, **change})[0]["code"],
                                 "model.stack_differs_from_registered")

    def test_missing_identity_only_discloses(self):
        self.assertEqual(model_files.compare(self.expected, {"status": "missing"}),
                         [{"code": "model.identity_unrecorded", "fields": []}])

    def test_actual_prepare_metadata_shape(self):
        metadata = {"quantization": IDENTITY["quantization"], "adapters": {"runtime": {
            "name": "mlx", "prepare_metadata": {"model_source": "synthetic-model",
                "model_artifact_identity": {"status": "ok", "folded_sha256": "a" * 64},
                "mlx_version": "1", "mlx_lm_version": "2", "transformers_version": "3"}}}}
        self.assertEqual(model_files.run_identity(metadata), IDENTITY)

    def test_os_sampler_output_policy_not_compared(self):
        self.assertEqual(model_files.compare(self.expected, {**IDENTITY, "platform": "other", "sampler": "other",
                                                             "output_policy": "other"}), [])

    def test_existing_pin_document_parses_without_opening_sources(self):
        expected = model_files.expected(json.loads((ROOT / "configs/campaigns/v5_claim_25g83/identity_pins.json").read_text()))
        self.assertEqual(len(expected["models"]), 3)
        self.assertTrue(all(x["sha256s"] for x in expected["models"].values()))
