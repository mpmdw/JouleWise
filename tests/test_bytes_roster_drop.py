"""Registration §§2/10 alternative-roster regressions; synthetic desk work only."""
from __future__ import annotations

import copy
import unittest
from pathlib import Path

from joulewise import bytes_analysis as ba

ROOT = Path(__file__).resolve().parents[1]
DROP = "Qwen3-8B-8bit"


def manifest_without_drop():
    manifest = ba.read_json(ROOT / "tests/fixtures/bytes/campaign_design.json")
    manifest["models"] = [m for m in manifest["models"] if m["model"] != DROP]
    return manifest


class RegisteredRosterTests(unittest.TestCase):
    def test_only_registered_alternative_and_full_roster_are_accepted(self):
        manifest = manifest_without_drop()
        self.assertIs(ba.validate_manifest(manifest), manifest)
        full = ba.read_json(ROOT / "tests/fixtures/bytes/campaign_design.json")
        self.assertIs(ba.validate_manifest(full), full)
        wrong_nine = copy.deepcopy(full)
        wrong_nine["models"] = [m for m in wrong_nine["models"]
                                if m["model"] != "Llama-3.3-70B-Instruct-4bit"]
        eleven = copy.deepcopy(full)
        extra = copy.deepcopy(eleven["models"][0])
        extra["model"] = "unregistered-model"
        eleven["models"].append(extra)
        for invalid in (wrong_nine, eleven):
            with self.subTest(count=len(invalid["models"])):
                with self.assertRaises(ba.AnalysisError):
                    ba.validate_manifest(invalid)

    def test_frozen_families_follow_registered_roster(self):
        manifest = manifest_without_drop()
        frozen = ba.frozen_predictions([], manifest)
        self.assertEqual(frozen["H1_checks"], 18)
        self.assertEqual(frozen["H2_intervals"], {"rails": 8, "DC input": 8, "rest": 10})
        full = ba.read_json(ROOT / "tests/fixtures/bytes/campaign_design.json")
        control = ba.frozen_predictions([], full)
        self.assertEqual(control["H1_checks"], 21)
        self.assertEqual(control["H2_intervals"], {"rails": 9, "DC input": 9, "rest": 11})


if __name__ == "__main__":
    unittest.main()
