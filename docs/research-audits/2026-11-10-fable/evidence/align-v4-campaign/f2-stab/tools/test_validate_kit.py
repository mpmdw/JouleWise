import json
from pathlib import Path
import unittest

from validate_kit import BASE, CELL_FIELDS, validate_cells


class ValidateCellsTests(unittest.TestCase):
    def setUp(self):
        self.base = json.loads(BASE.read_bytes())
        self.kit = json.loads((Path(__file__).resolve().parents[1] / "f2-stab-01.v1.1.json").read_bytes())

    def test_regenerated_kit_matches_every_cell(self):
        validate_cells(self.kit, self.base)

    def test_refuses_one_changed_cell(self):
        for field, value in zip(CELL_FIELDS, (256, 128, "span", "q0"), strict=True):
            with self.subTest(field=field):
                original = self.kit["legs"][0][field]
                self.kit["legs"][0][field] = value
                with self.assertRaisesRegex(ValueError, rf"legs\[0\]\.{field}"):
                    validate_cells(self.kit, self.base)
                self.kit["legs"][0][field] = original

    def test_refuses_changed_leg_count(self):
        self.kit["legs"].pop()
        with self.assertRaisesRegex(ValueError, "expected 12 positions"):
            validate_cells(self.kit, self.base)

    def test_refuses_changed_power_mode_guard(self):
        self.kit["checklist"] = [
            line for line in self.kit["checklist"] if line["kind"] != "powermode_zero"
        ]
        with self.assertRaisesRegex(ValueError, "Automatic power mode"):
            validate_cells(self.kit, self.base)


if __name__ == "__main__":
    unittest.main()
