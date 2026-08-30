from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.select_g2a_prefill_length import LADDER, main


def _summary(first_qualifying: int | None) -> list[dict[str, object]]:
    rows = []
    for length in reversed(LADDER):
        qualifies = first_qualifying is not None and length >= first_qualifying
        rows.append(
            {
                "all_small_count_ge_5": qualifies,
                "large_members": 1,
                "length": length,
                "small_members": 5 if qualifies else 4,
                "small_minimum_count": 5 if qualifies else 4,
            }
        )
    return rows


class SelectG2APrefillLengthTests(unittest.TestCase):
    def _run(self, root: Path, summary: object, name: str = "selection.json"):
        summary_path = root / "summary.json"
        output_path = root / name
        summary_path.write_text(json.dumps(summary, indent=1) + "\n")
        code = main(["--summary", str(summary_path), "--output", str(output_path)])
        return code, json.loads(output_path.read_text()), output_path.read_bytes()

    def test_each_rung_can_be_selected(self) -> None:
        for expected in LADDER:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as tmp:
                code, record, _raw = self._run(Path(tmp), _summary(expected))
                self.assertEqual(code, 0)
                self.assertEqual(record["status"], "selected")
                self.assertEqual(record["selected_prefill_tokens"], expected)
                self.assertEqual(record["collection_prefill_tokens"], expected)
                self.assertEqual(record["qualifying_prefill_tokens"][0], expected)
                self.assertIsNone(record["refusal"])

    def test_zero_qualifying_emits_ruled_collect_at_4096_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, record, _raw = self._run(Path(tmp), _summary(None))
        self.assertEqual(code, 0)
        self.assertEqual(record["status"], "refused")
        self.assertIsNone(record["selected_prefill_tokens"])
        self.assertEqual(record["collection_prefill_tokens"], 4096)
        refusal = record["refusal"]
        self.assertEqual(refusal["fallback_action"], "collect_at_4096")
        self.assertEqual(refusal["fallback_label"], "collect-at-4096")
        split = refusal["result_reporting"]
        self.assertEqual(
            split["count_below_reducer_minimum"]["refusal"],
            "not_resolvable_sample_count",
        )
        self.assertEqual(
            split["count_below_pre_registered_floor"]["refusal"],
            "below the pre-registered count floor of 5",
        )
        self.assertTrue(
            split["count_below_pre_registered_floor"][
                "disclose_reducer_resolvable_result"
            ]
        )

    def test_malformed_summary_emits_refusal_and_nonzero(self) -> None:
        malformed_values = (
            {"not": "an array"},
            _summary(512)[:-1],
            [
                {**row, "all_small_count_ge_5": "yes"}
                if row["length"] == 512
                else row
                for row in _summary(512)
            ],
        )
        for index, value in enumerate(malformed_values):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as tmp:
                code, record, _raw = self._run(Path(tmp), value)
                self.assertEqual(code, 2)
                self.assertEqual(record["status"], "refused")
                self.assertEqual(
                    record["refusal"]["code"],
                    "malformed_g2a_prefill_summary",
                )
                self.assertIsNone(record["collection_prefill_tokens"])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary_path = root / "summary.json"
            output_path = root / "selection.json"
            summary_path.write_text("{not-json\n")
            code = main(
                ["--summary", str(summary_path), "--output", str(output_path)]
            )
            record = json.loads(output_path.read_text())
        self.assertEqual(code, 2)
        self.assertEqual(record["refusal"]["code"], "malformed_g2a_prefill_summary")
        self.assertEqual(record["refusal"]["reason"], "invalid_json")

    def test_output_is_byte_deterministic_and_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code1, record1, raw1 = self._run(root, _summary(1024), "first.json")
            code2, record2, raw2 = self._run(root, _summary(1024), "second.json")
        self.assertEqual((code1, code2), (0, 0))
        self.assertEqual(record1, record2)
        self.assertEqual(raw1, raw2)
        expected = (json.dumps(record1, indent=2, sort_keys=True) + "\n").encode()
        self.assertEqual(raw1, expected)


if __name__ == "__main__":
    unittest.main()
