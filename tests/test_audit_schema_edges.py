from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from joulewise.schemas import BenchmarkConfig, SchemaError

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

    def test_unknown_workload_keys_are_ignored(self) -> None:
        data = example_data()
        data["workload_profile"]["bogus_key"] = 99

        config = BenchmarkConfig.from_mapping(data)

        self.assertEqual(config.workload_profile.name, "mock_smoke")
        self.assertEqual(config.workload_profile.prompt_tokens, 32)
        self.assertEqual(config.workload_profile.output_tokens, 8)
        self.assertFalse(hasattr(config.workload_profile, "bogus_key"))


class SchemaBugPins(unittest.TestCase):
    # S1: unsupported schema_version values are accepted by the v0.1 parser.
    @unittest.expectedFailure
    def test_rejects_unsupported_schema_version(self) -> None:
        data = example_data()
        data["schema_version"] = "0.2"
        with self.assertRaisesRegex(SchemaError, "schema_version"):
            BenchmarkConfig.from_mapping(data)

    # S3: multiple prompt sources are accepted, making runtime/reducer token counts ambiguous.
    @unittest.expectedFailure
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
    @unittest.expectedFailure
    def test_config_schema_power_hz_minimum_matches_loader(self) -> None:
        power_hz = BenchmarkConfig.json_schema()["$defs"]["sampling"]["properties"]["power_hz"]
        self.assertEqual(power_hz.get("minimum"), 0.001)

    # S7: exported JSON Schema allows empty strings that the loader rejects.
    @unittest.expectedFailure
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


if __name__ == "__main__":
    unittest.main()
