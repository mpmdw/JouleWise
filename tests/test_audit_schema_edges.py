from __future__ import annotations

import copy
import json
import unittest
import warnings
from pathlib import Path

from joulewise.schemas import BenchmarkConfig, ConfigKeyWarning, SchemaError

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"


def example_data() -> dict:
    return json.loads(EXAMPLE_CONFIG.read_text())


class SchemaCoverageGapTests(unittest.TestCase):
    def test_required_sections_must_be_objects(self) -> None:
        for section in ("model", "quantization", "hardware_target", "workload_profile"):
            for value in (None, [], "bad"):
                data = example_data()
                if value is None:
                    data.pop(section)
                else:
                    data[section] = value
                with self.subTest(section=section, value=value):
                    with self.assertRaisesRegex(SchemaError, f"{section} must be an object"):
                        BenchmarkConfig.from_mapping(data)

    def test_bool_and_negative_numeric_optionals_are_rejected(self) -> None:
        cases = [
            ("sampling", {"power_hz": True}, "sampling.power_hz must be a number"),
            ("sampling", {"idle_seconds": -1}, "sampling.idle_seconds must be >="),
            ("sampling", {"warmup_seconds": -1}, "sampling.warmup_seconds must be >="),
            ("interconnect", {"name": "pcie", "link_speed_mbps": -1}, "interconnect.link_speed_mbps must be >="),
        ]
        for section, value, message in cases:
            data = example_data()
            data[section] = value
            with self.subTest(section=section, value=value):
                with self.assertRaisesRegex(SchemaError, message):
                    BenchmarkConfig.from_mapping(data)

    def test_run_metadata_tags_invalid_lists_are_rejected(self) -> None:
        for tags in ("smoke", [1, "ok"], [None]):
            data = example_data()
            data["run_metadata"]["tags"] = tags
            with self.subTest(tags=tags):
                with self.assertRaisesRegex(SchemaError, "run_metadata.tags"):
                    BenchmarkConfig.from_mapping(data)

    def test_unknown_workload_keys_warn_and_are_ignored(self) -> None:
        data = example_data()
        data["workload_profile"]["bogus_key"] = 99

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            config = BenchmarkConfig.from_mapping(data)

        self.assertEqual(len(caught), 1)
        warning = caught[0].message
        self.assertIsInstance(warning, ConfigKeyWarning)
        self.assertEqual(warning.code, "unknown_config_key")
        self.assertEqual(warning.path, "workload_profile.bogus_key")
        self.assertEqual(
            str(warning),
            "unknown config key 'workload_profile.bogus_key' ignored by schema 0.1",
        )
        self.assertEqual(config.workload_profile.name, "mock_smoke")
        self.assertEqual(config.workload_profile.prompt_tokens, 32)
        self.assertEqual(config.workload_profile.output_tokens, 8)
        self.assertFalse(hasattr(config.workload_profile, "bogus_key"))

    def test_sampling_typo_warns_before_defaulting(self) -> None:
        data = example_data()
        data["sampling"].pop("power_hz")
        data["sampling"]["power_hzz"] = 10

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            config = BenchmarkConfig.from_mapping(data)

        self.assertEqual(config.sampling.power_hz, 1.0)
        self.assertEqual(config.config_warnings[0]["code"], "unknown_config_key")
        self.assertEqual(len(caught), 1)
        self.assertIsInstance(caught[0].message, ConfigKeyWarning)
        self.assertIn("sampling.power_hzz", str(caught[0].message))

    def test_unknown_keys_warn_in_deterministic_order_at_every_schema_level(self) -> None:
        data = example_data()
        data["root_typo"] = 1
        sections = (
            "model",
            "quantization",
            "hardware_target",
            "workload_profile",
            "interconnect",
            "sampling",
            "run_metadata",
        )
        for section in sections:
            data[section]["z_typo"] = section

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            config = BenchmarkConfig.from_mapping(data)

        expected = sorted(
            ["root_typo"] + [f"{section}.z_typo" for section in sections]
        )
        self.assertEqual([warning.message.path for warning in caught], expected)
        self.assertEqual(
            [warning["path"] for warning in config.config_warnings], expected
        )
        emitted = config.to_dict()
        self.assertNotIn("root_typo", emitted)
        for section in sections:
            self.assertNotIn("z_typo", emitted[section])

    def test_non_object_section_fails_without_child_key_inspection(self) -> None:
        data = example_data()
        data["sampling"] = ["not", "an", "object"]

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with self.assertRaisesRegex(SchemaError, "sampling must be an object"):
                BenchmarkConfig.from_mapping(data)

        self.assertEqual(caught, [])


class SchemaBugPins(unittest.TestCase):
    # S1: unsupported schema_version values are accepted by the v0.1 parser.
    def test_rejects_unsupported_schema_version(self) -> None:
        data = example_data()
        data["schema_version"] = "0.2"
        with self.assertRaisesRegex(SchemaError, "schema_version"):
            BenchmarkConfig.from_mapping(data)

    # S3: multiple prompt sources are accepted, making runtime/reducer token counts ambiguous.
    def test_workload_rejects_multiple_prompt_sources(self) -> None:
        data = example_data()
        data["workload_profile"]["prompt_text"] = "hello"
        with self.assertRaisesRegex(SchemaError, "prompt"):
            BenchmarkConfig.from_mapping(data)

    # S4: _optional_float accepts NaN/Infinity from Python's JSON parser.
    def test_sampling_rejects_non_finite_numbers(self) -> None:
        data = example_data()
        data["sampling"] = {"power_hz": float("nan")}
        with self.assertRaisesRegex(SchemaError, "finite"):
            BenchmarkConfig.from_mapping(data)

    # S6: exported JSON Schema minimum is weaker than the loader's 0.001 Hz minimum.
    def test_config_schema_power_hz_minimum_matches_loader(self) -> None:
        power_hz = BenchmarkConfig.json_schema()["$defs"]["sampling"]["properties"]["power_hz"]
        self.assertEqual(power_hz.get("minimum"), 0.001)

    # S7: exported JSON Schema allows empty strings that the loader rejects.
    def test_config_schema_required_strings_are_non_empty(self) -> None:
        schema = BenchmarkConfig.json_schema()
        for section, field in (
            ("model", "name"),
            ("quantization", "name"),
            ("hardware_target", "id"),
            ("workload_profile", "name"),
        ):
            with self.subTest(section=section, field=field):
                prop = copy.deepcopy(schema["$defs"][section]["properties"][field])
                self.assertEqual(prop.get("minLength"), 1)

    def test_config_schema_declares_warn_and_ignore_unknown_key_policy(self) -> None:
        schema = BenchmarkConfig.json_schema()
        self.assertEqual(
            schema["x-joulewise-unknown-key-policy"], "warn-and-ignore"
        )
        self.assertNotIn("additionalProperties", schema)


if __name__ == "__main__":
    unittest.main()
