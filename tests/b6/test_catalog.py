import ast
import json
import subprocess
import sys
import unittest

from joulewise.flags.catalog import catalog_from_bytes
from scripts import build_b6_flag_catalog as builder
from tests.b6.support import ROOT


class CatalogTests(unittest.TestCase):
    def test_reproduces_and_loads(self):
        self.assertEqual(builder.build(), builder.TARGET.read_bytes())
        self.assertEqual(catalog_from_bytes(builder.build()).cell_unit_minimum, 5)
        entry = catalog_from_bytes(builder.build()).entry("bytes.decode_battery_assist")
        self.assertEqual((entry["family"], entry["klass"], entry["effect"]),
                         ("RECORDS", "REPRESENTATION", "DISCLOSE"))
        result = subprocess.run([sys.executable, str(ROOT / "scripts/build_b6_flag_catalog.py"), "--check"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_kept_excluding_codes_and_all_new_exclusions_have_reasons(self):
        source = json.loads(builder.SOURCE.read_bytes())["codes"]
        actual = json.loads(builder.build())["codes"]
        retained = {code for code, entry in actual.items() if entry["effect"] == "EXCLUDE_WINDOW" and code in source}
        self.assertEqual(retained, {"calibration.capture_battery_span", "calibration.capture_battery_pair_failed",
            "calibration.capture_battery_unmeasured", "clock.step_overlap_calibration", "cell.below_minimum",
            "roster.no_science_bundles", "records.source_changed_during_harvest"})
        self.assertEqual(sum(source[c]["effect"] == "EXCLUDE_WINDOW" for c in builder.RECLASSIFY), 25)
        self.assertNotIn("calibration.capture_bytes_changed", actual)
        for code, entry in actual.items():
            if entry["effect"].startswith("EXCLUDE"):
                self.assertTrue(entry.get("note"), code)
        self.assertTrue(all(actual[code]["effect"] == "DISCLOSE" for code in builder.RECLASSIFY))

    def test_harvest_emitters_and_b6_codes_are_classified(self):
        actual = json.loads(builder.build())["codes"]
        harvest = ast.parse((ROOT / "joulewise/b5/harvest.py").read_text())
        codes = set()
        for node in ast.walk(harvest):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "emit":
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    codes.add(node.args[0].value)
        self.assertEqual(codes - set(actual), set())
        self.assertTrue(set(builder.NEW_CODES) <= set(actual))

    def test_block_six_exclusions_are_registered(self):
        document = json.loads((ROOT / "configs/gates/hazard_refusals.json").read_text())
        for section, effect in (("window_exclusions", "EXCLUDE_WINDOW"), ("member_exclusions", "EXCLUDE_MEMBER")):
            for code, entry in json.loads(builder.build())["codes"].items():
                if entry["effect"] == effect:
                    self.assertIn(code, document[section])
