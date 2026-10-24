import copy
import json
import unittest

from joulewise.b6 import model_files
from tests.b6.support import IDENTITY, ROOT


class ModelFileTests(unittest.TestCase):
    def test_sampler_comparison_projects_each_registered_setting(self):
        settings = {"temperature": 0.0, "top_p": 1.0, "top_k": 0, "kind": "greedy"}
        policy = {"sampler": settings, "output_policy": {"name": "fixed"}}
        self.pins["units"]["one"]["stack_identity"]["sampler_output_policy"] = policy
        expected = model_files.expected(self.pins)
        observed = {**IDENTITY, "sampler_output_policy": copy.deepcopy(policy)}
        observed["sampler_output_policy"]["sampler"]["provenance_note"] = "new adapter detail"
        self.assertEqual(model_files.compare(expected, model_files.run_identity(observed)), [])
        for key, value in (("temperature", 0.7), ("top_p", 0.9), ("top_k", 20), ("kind", "top_p")):
            with self.subTest(key=key):
                changed = copy.deepcopy(observed)
                changed["sampler_output_policy"]["sampler"][key] = value
                self.assertEqual(model_files.compare(expected, model_files.run_identity(changed)),
                                 [{"code": "model.stack_differs_from_registered", "fields": ["sampler_output_policy"]}])
        for value in ([], "garbled", None):
            changed = copy.deepcopy(observed)
            changed["sampler_output_policy"]["sampler"] = value
            self.assertEqual(model_files.compare(expected, changed),
                             [{"code": "model.stack_differs_from_registered", "fields": ["sampler_output_policy"]}])

    def test_malformed_runtime_record_is_unrecorded_identity(self):
        for value in ({'adapters': []}, {'environment': {'python_packages': []}},
                      {'adapters': {'runtime': {'prepare_metadata': ['bad']}}}):
            self.assertEqual(model_files.compare({}, model_files.run_identity(value)),
                             [{'code': 'model.identity_unrecorded', 'fields': []}])

    def setUp(self):
        self.pins = {"runtime_versions": {"packages": {**IDENTITY["packages"],
            "mlx-metal": "metal-1", "tokenizers": "tok-1"}}, "units": {"one": {
            "model_source": IDENTITY["model_source"], "model_artifact_sha256": IDENTITY["model_artifact_sha256"],
            "stack_identity": {"runtime_version": {"name": "mlx"}, "quantization": IDENTITY["quantization"]}}}}
        self.expected = model_files.expected(self.pins)

    def test_absent_pins_do_not_invent_a_stack_difference(self):
        self.assertEqual(model_files.compare(model_files.expected({}), IDENTITY),
                         [{'code': 'model.source_unpinned', 'fields': ['model_source']}])

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

    def test_registered_policy_os_hardware_and_telemetry_compare_from_metadata(self):
        stack = self.pins["units"]["one"]["stack_identity"]
        policy = {"sampler": {"temperature": 0.0}, "output_policy": {
            "name": "fixed_budget_exact", "requested_tokens": 512, "stop_condition": "requested_tokens_emitted"}}
        stack.update(sampler_output_policy=policy, os_version="registered-os",
                     hardware_unit={"device": "registered-device", "machine": "arm64"}, telemetry_backend="meter")
        metadata = {"model_artifact_sha256": IDENTITY["model_artifact_sha256"], **IDENTITY,
                    "sampler_output_policy": copy.deepcopy(policy), "os_version": "registered-os",
                    "hardware_unit": {"device": "registered-device", "machine": "arm64"}, "telemetry_backend": "meter"}
        expected = model_files.expected(self.pins)
        self.assertEqual(model_files.compare(expected, model_files.run_identity(metadata)), [])
        for field, value in (("sampler_output_policy", {"sampler": {"temperature": 0.7}}),
                             ("os_version", "changed"), ("hardware_unit", {"machine": "other"}),
                             ("telemetry_backend", "changed")):
            with self.subTest(field=field):
                self.assertEqual(model_files.compare(expected, model_files.run_identity({**metadata, field: value}))[0]["code"],
                                 "model.stack_differs_from_registered")
        raw = {"quantization": IDENTITY["quantization"], "adapters": {"runtime": {
            "name": "mlx", "prepare_metadata": {"model_source": IDENTITY["model_source"],
            "model_artifact_identity": {"status": "ok", "folded_sha256": IDENTITY["model_artifact_sha256"]}}},
            "telemetry": {"name": "meter"}}, "platform": "registered-os", "machine": "arm64",
            "device": {"device": "registered-device"}, "workload_provenance": policy}
        observed = model_files.run_identity(raw)
        for field in ("sampler_output_policy", "os_version", "hardware_unit", "telemetry_backend"):
            self.assertEqual(observed[field], metadata[field])
        self.assertEqual(model_files.compare(expected, observed), [])

    def test_actual_prepare_metadata_shape(self):
        metadata = {"quantization": IDENTITY["quantization"], "adapters": {"runtime": {
            "name": "mlx", "prepare_metadata": {"model_source": "synthetic-model",
                "model_artifact_identity": {"status": "ok", "folded_sha256": "a" * 64},
                "mlx_version": "1", "mlx_lm_version": "2", "transformers_version": "3"}}}}
        self.assertEqual(model_files.run_identity(metadata), {**IDENTITY, "runtime_version": "1"})

    def test_unpinned_source_discloses_without_byte_exclusion(self):
        self.assertEqual(model_files.compare(self.expected, {**IDENTITY, "model_source": "unpinned"}),
                         [{"code": "model.source_unpinned", "fields": ["model_source"]}])

    def test_missing_recorded_fields_are_not_mismatches(self):
        observed = {key: IDENTITY[key] for key in ("model_source", "model_artifact_sha256", "status")}
        self.assertEqual(model_files.compare(self.expected, observed), [])
        self.assertEqual(model_files.compare(self.expected, {**observed, "kernel_library": "unavailable"}), [])

    def test_kernel_tokenizer_and_mlx_metal_from_metadata(self):
        self.pins["runtime_versions"]["packages"] = {**IDENTITY["packages"], "mlx-metal": "1"}
        stack = self.pins["units"]["one"]["stack_identity"]
        stack.update(kernel_library="metal-kernels", runtime_version={"name": "mlx", "version": "1"},
                     tokenizer_identity={"identifier": "tokenizer", "revision": "r1", "vocab_size": 123})
        metadata = {"quantization": IDENTITY["quantization"], "environment": {"python_packages": {
            "mlx-metal": {"present": True, "version": "1"}}}, "workload_provenance": {"tokenizer": {
            "identifier": "/another/location/tokenizer", "revision": "r1", "vocab_size": 123}},
            "adapters": {"runtime": {"name": "mlx", "prepare_metadata": {
                "model_source": "synthetic-model", "model_artifact_identity": {"status": "ok", "folded_sha256": "a" * 64},
                "mlx_version": "1", "mlx_lm_version": "2", "transformers_version": "3", "kernel_library": "metal-kernels"}}}}
        expected = model_files.expected(self.pins)
        self.assertEqual(model_files.compare(expected, model_files.run_identity(metadata)), [])
        for field in ("kernel_library", "runtime_version", "mlx-metal", "tokenizer.identifier", "tokenizer.revision", "tokenizer.vocab_size"):
            observed = model_files.run_identity(metadata)
            if field.startswith("tokenizer."):
                observed["tokenizer"][field.split(".")[1]] = "changed"
            elif field == "mlx-metal":
                observed["packages"][field] = "changed"
            else:
                observed[field] = "changed"
            with self.subTest(field=field):
                self.assertEqual(model_files.compare(expected, observed),
                                 [{"code": "model.stack_differs_from_registered", "fields": [field]}])
        metadata["environment"] = {}
        metadata["adapters"]["runtime"]["prepare_metadata"]["mlx_metal_version"] = "changed"
        self.assertIn("mlx-metal", model_files.compare(expected, model_files.run_identity(metadata))[0]["fields"])

    def test_tokenizer_matches_the_unit_with_the_same_digest(self):
        one = self.pins["units"]["one"]
        one["stack_identity"]["tokenizer_identity"] = {"revision": "first"}
        two = copy.deepcopy(one)
        two["model_artifact_sha256"] = "b" * 64
        two["stack_identity"]["tokenizer_identity"] = {"revision": "second"}
        self.pins["units"]["two"] = two
        rows = model_files.compare(model_files.expected(self.pins), {**IDENTITY, "tokenizer": {"revision": "second"}})
        self.assertEqual(rows, [{"code": "model.stack_differs_from_registered", "fields": ["tokenizer.revision"]}])

    def test_per_run_distribution_versions_come_from_environment(self):
        self.pins["runtime_versions"]["packages"].update({"mlx-metal": "metal-1", "tokenizers": "tok-1"})
        metadata = {"adapters": {"runtime": {"name": "mlx", "prepare_metadata": {
            "model_source": IDENTITY["model_source"],
            "model_artifact_identity": {"status": "ok", "folded_sha256": "a" * 64}}}},
            "environment": {"python_packages": {
                "mlx-metal": {"present": True, "version": "metal-1"},
                "tokenizers": {"present": True, "version": "tok-1"}}}}
        expected = model_files.expected(self.pins)
        observed = model_files.run_identity(metadata)
        self.assertEqual(model_files.compare(expected, observed), [])
        for package in ("mlx-metal", "tokenizers"):
            changed = copy.deepcopy(metadata)
            changed["environment"]["python_packages"][package]["version"] = "different"
            self.assertEqual(model_files.compare(expected, model_files.run_identity(changed)),
                             [{"code": "model.stack_differs_from_registered", "fields": [package]}])
        metadata["environment"]["python_packages"]["tokenizers"] = {"present": False, "version": None}
        self.assertEqual(model_files.compare(expected, model_files.run_identity(metadata)), [])

    def test_unregistered_stack_fields_do_not_invent_differences(self):
        self.assertEqual(model_files.compare(self.expected, {**IDENTITY, "platform": "other", "sampler": "other",
                                                             "output_policy": "other"}), [])

    def test_existing_pin_document_parses_without_opening_sources(self):
        expected = model_files.expected(json.loads((ROOT / "configs/campaigns/v5_claim_25g83/identity_pins.json").read_text()))
        self.assertEqual(len(expected["models"]), 3)
        self.assertTrue(all(x["sha256s"] for x in expected["models"].values()))
