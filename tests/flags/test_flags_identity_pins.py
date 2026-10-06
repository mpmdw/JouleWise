"""The sealed identity pins file reaches the arm-time model collector (integration).

L6 seals one ``joulewise.b5_identity_pins.v1`` file beside the flag catalog.
The driver passes it to ``scripts/collect_window_flags.py --identity-pins``
and the harvest reads it at the same default path, so the model and runtime
pins have one home. Without it every arm records ``model.identity_unpinned``
(EXCLUDE_WINDOW); a file that cannot be read is ``model.identity_unmeasured``.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from joulewise.flags.collect import (
    IDENTITY_PINS_SCHEMA,
    CollectorError,
    collect_model_identity,
    read_identity_pins,
    run_collectors,
)
from joulewise.flags.sink import FlagSink, read_flags
from joulewise.provenance import model_artifact_identity
from tests.flags.test_flags_collect import RUNTIME_PIN, PackFixture, fake_probe

ROOT = Path(__file__).resolve().parents[2]


def codes(result: dict) -> list[tuple[str, str]]:
    return sorted((flag["code"], flag["observed"].get("check")) for flag in result["flags"])


class IdentityPinsFileTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.fixture = PackFixture(self.root)  # its plan tree carries no model pin
        self.observed = model_artifact_identity(str(self.fixture.model))["folded_sha256"]
        self.pins = self.root / "identity_pins.json"

    def write_pins(self, units: dict, runtime: str | None) -> Path:
        self.pins.write_text(json.dumps({"schema": IDENTITY_PINS_SCHEMA, "units": units,
                                         "runtime_versions_sha256": runtime}))
        return self.pins

    def collect(self, **extra) -> dict:
        return collect_model_identity(self.fixture.params(**extra), probe_runtime=fake_probe)

    def test_no_file_leaves_both_pins_missing(self) -> None:
        self.assertEqual({"model_artifact_sha256": {}, "runtime_versions_sha256": None}, read_identity_pins(None))
        self.assertEqual([("model.identity_unpinned", "model_artifact"),
                          ("model.identity_unpinned", "runtime_versions")], codes(self.collect()))

    def test_sealed_file_supplies_the_model_and_runtime_pins(self) -> None:
        path = self.write_pins({"u1": {"model_artifact_sha256": self.observed}}, RUNTIME_PIN)
        self.assertEqual([], codes(self.collect(identity_pins_path=str(path))))

    def test_sealed_pins_that_differ_are_mismatches(self) -> None:
        path = self.write_pins({"u1": {"model_artifact_sha256": "1" * 64}}, "2" * 64)
        self.assertEqual([("model.identity_mismatch", "model_artifact"),
                          ("model.identity_mismatch", "runtime_versions")],
                         codes(self.collect(identity_pins_path=str(path))))

    def test_explicit_arguments_win_over_the_file(self) -> None:
        path = self.write_pins({"u1": {"model_artifact_sha256": "1" * 64}}, "2" * 64)
        result = self.collect(identity_pins_path=str(path), expected_model_artifact_sha256={"u1": self.observed},
                              expected_runtime_versions_sha256=RUNTIME_PIN)
        self.assertEqual([], codes(result))

    def test_unreadable_or_malformed_file_is_unmeasured_not_unpinned(self) -> None:
        cases = {
            "absent": None,
            "not json": "{",
            "wrong schema": json.dumps({"schema": "other", "units": {}}),
            "units not an object": json.dumps({"schema": IDENTITY_PINS_SCHEMA, "units": []}),
            "upper-case pin": json.dumps({"schema": IDENTITY_PINS_SCHEMA,
                                          "units": {"u1": {"model_artifact_sha256": "A" * 64}}}),
            "bad runtime pin": json.dumps({"schema": IDENTITY_PINS_SCHEMA, "units": {},
                                           "runtime_versions_sha256": "short"}),
        }
        for label, text in cases.items():
            with self.subTest(label):
                path = self.root / f"pins-{label.replace(' ', '-')}.json"
                if text is not None:
                    path.write_text(text)
                with self.assertRaises(CollectorError):
                    read_identity_pins(path)
                with self.assertRaises(CollectorError):
                    self.collect(identity_pins_path=str(path))
        # Through the collector runner (its own subprocess): the error leaves the
        # model collector's unmeasured flag, never a silent pass.
        bad = self.root / "pins-bad.json"
        bad.write_text("{")
        sink = FlagSink(self.root / "flags" / "arm.jsonl")
        outcomes = run_collectors([("model_identity", self.fixture.params(identity_pins_path=str(bad)))],
                                  stage="arm", sink=sink)
        self.assertEqual(["error"], [outcome.status for outcome in outcomes])
        written, problems = read_flags(sink.path)
        self.assertEqual([], problems)
        self.assertIn(("model.identity_unmeasured", "collector_run"),
                      [(flag["code"], flag["observed"].get("check")) for flag in written])


class CommandLineTests(unittest.TestCase):
    def test_identity_pins_argument_reaches_the_model_collector(self) -> None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("collect_window_flags_under_test",
                                                      ROOT / "scripts/collect_window_flags.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        args = module.build_parser().parse_args(
            ["--stage", "arm", "--custody", "/c", "--pack", "/p", "--identity-pins", "/sealed/identity_pins.json"])
        specs = dict(module.build_specs(args, None))
        self.assertEqual("/sealed/identity_pins.json", specs["model_identity"]["identity_pins_path"])
        args = module.build_parser().parse_args(["--stage", "arm", "--custody", "/c", "--pack", "/p"])
        self.assertIsNone(dict(module.build_specs(args, None))["model_identity"]["identity_pins_path"])


if __name__ == "__main__":
    unittest.main()
