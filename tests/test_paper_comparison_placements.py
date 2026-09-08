"""Independent fallback safeguards; X1–X22 agreement awaits its source crosswalk."""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/paper/results-fill-registry.md"
RETIRED = ("DS-32", "PG-08", "OB-01", "OR-01")


def check_retired_rows(text):
    for row_id in RETIRED:
        rows = [line for line in text.splitlines()
                if line.startswith(f"| {row_id} — ")]
        if len(rows) != 1:
            raise ValueError(f"{row_id}: missing or duplicate retirement row")
        cells = re.split(r"(?<!\\)\|", rows[0])[1:-1]
        if len(cells) != 7 or cells[4].strip() != "RETIRED_FALLBACK":
            raise ValueError(f"{row_id}: retired row treated as active")
        if not cells[5].strip().startswith("RETIRED_FALLBACK 2026-09-05 (D-174):"):
            raise ValueError(f"{row_id}: dated retirement lost")


class ComparisonPlacementFallbackTests(unittest.TestCase):
    def test_retired_successor_rows_remain_non_fillable(self):
        check_retired_rows(REGISTRY.read_text(encoding="utf-8"))

    def test_reactivation_counterfactual_rejected(self):
        text = REGISTRY.read_text(encoding="utf-8")
        for row_id in RETIRED:
            with self.subTest(row=row_id):
                row = next(line for line in text.splitlines()
                           if line.startswith(f"| {row_id} — "))
                changed = row.replace("| RETIRED_FALLBACK |", "| MEASURED |", 1)
                self.assertNotEqual(row, changed)
                with self.assertRaisesRegex(ValueError, "treated as active"):
                    check_retired_rows(text.replace(row, changed, 1))

    def test_missing_and_duplicate_retirement_rejected(self):
        text = REGISTRY.read_text(encoding="utf-8")
        for row_id in RETIRED:
            row = next(line for line in text.splitlines()
                       if line.startswith(f"| {row_id} — "))
            for changed in (text.replace(row, "", 1), text + "\n" + row):
                with self.subTest(row=row_id), self.assertRaisesRegex(
                        ValueError, "missing or duplicate"):
                    check_retired_rows(changed)
