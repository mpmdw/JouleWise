"""Focused tests for the DG-071 / DG-075 issued-statistics producer."""

from __future__ import annotations

import csv
from contextlib import redirect_stderr
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "issue_dg071_dg075_statistics.py"
SPEC = importlib.util.spec_from_file_location(
    "issue_dg071_dg075_statistics", SCRIPT_PATH
)
assert SPEC is not None and SPEC.loader is not None
ISSUER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ISSUER)


class Dg071Dg075StatisticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.bundle = self.root / "fixture" / "power_trace.csv"
        self.bundle.parent.mkdir(parents=True)
        self._write_records(
            [
                (10.0, 0.0, 1.0),
                (10.0, 1.0, 3.0),
                (12.0, 3.0, 6.0),
                (15.0, 6.0, 10.0),
                (19.0, 10.0, 15.0),
            ]
        )

    def _write_records(self, rows: list[tuple[float, float, float]]) -> None:
        with self.bundle.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(ISSUER.EXPECTED_RECORD_SCHEMA)
            for index, (timestamp, start, end) in enumerate(rows):
                writer.writerow(
                    [timestamp, 1.0 + index, "fixture", "cpu_power", start, end]
                )

    def _sha256(self) -> str:
        return hashlib.sha256(self.bundle.read_bytes()).hexdigest()

    def _issue(self, out: Path, *, expected_sha256: str | None = None):
        return ISSUER.issue_artifacts(
            self.bundle,
            out,
            expected_bundle_path=self.bundle,
            expected_bundle_sha256=expected_sha256 or self._sha256(),
            repository_root=ROOT,
            script_path=SCRIPT_PATH,
        )

    def test_five_records_have_hand_computable_statistics(self) -> None:
        out = self.root / "issued.json"
        payload = self._issue(out)

        # Widths [1, 2, 3, 4, 5]: median 3, Q1 2, Q3 4, IQR 2.
        dg071 = payload["statistics"]["DG-071"]
        self.assertEqual(
            (dg071["median_s"], dg071["q1_s"], dg071["q3_s"], dg071["iqr_s"]),
            (3.0, 2.0, 4.0, 2.0),
        )

        # Unique stamps [10, 12, 15, 19] -> differences [2, 3, 4].
        dg075 = payload["statistics"]["DG-075"]
        self.assertEqual(
            (dg075["median_s"], dg075["q1_s"], dg075["q3_s"], dg075["iqr_s"]),
            (3.0, 2.5, 3.5, 1.0),
        )
        self.assertEqual(payload["record_count"], 5)
        self.assertEqual(payload["distinct_timestamp_count"], 4)
        self.assertEqual(payload["duplicate_timestamp_count"], 1)
        self.assertEqual(json.loads(out.read_text(encoding="utf-8")), payload)
        self.assertIn(
            "| DG-071 | 5 | 3000.000000 | 2000.000000 |",
            out.with_suffix(".md").read_text(encoding="utf-8"),
        )

    def test_two_runs_are_byte_identical(self) -> None:
        first = self.root / "first" / "issued.json"
        second = self.root / "second" / "issued.json"
        self._issue(first)
        self._issue(second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(
            first.with_suffix(".md").read_bytes(),
            second.with_suffix(".md").read_bytes(),
        )

    def test_wrong_sha_is_refused_without_output(self) -> None:
        out = self.root / "wrong-sha.json"
        with self.assertRaisesRegex(
            ISSUER.IssuanceRefused, "expected 0{64}, observed"
        ) as raised:
            self._issue(out, expected_sha256="0" * 64)
        self.assertEqual(raised.exception.reason, "bundle_sha256_mismatch")
        self.assertFalse(out.exists())
        self.assertFalse(out.with_suffix(".md").exists())

    def test_missing_required_field_is_refused_without_output(self) -> None:
        self.bundle.write_text(
            "timestamp_s,power_w,source,rail,interval_start_s\n"
            "10,1,fixture,cpu_power,0\n",
            encoding="utf-8",
        )
        out = self.root / "missing-field.json"
        with self.assertRaises(ISSUER.IssuanceRefused) as raised:
            self._issue(out)
        self.assertEqual(raised.exception.reason, "record_schema_mismatch")
        self.assertFalse(out.exists())

    def test_non_monotone_timestamps_are_refused_without_output(self) -> None:
        self._write_records([(10.0, 0.0, 1.0), (9.0, 1.0, 2.0)])
        out = self.root / "non-monotone.json"
        with self.assertRaises(ISSUER.IssuanceRefused) as raised:
            self._issue(out)
        self.assertEqual(raised.exception.reason, "timestamps_non_monotone")
        self.assertFalse(out.exists())

    def test_wrong_bundle_path_is_refused_without_output(self) -> None:
        out = self.root / "wrong-path.json"
        with self.assertRaises(ISSUER.IssuanceRefused) as raised:
            ISSUER.issue_artifacts(
                self.bundle,
                out,
                expected_bundle_path=self.root / "other" / "power_trace.csv",
                expected_bundle_sha256=self._sha256(),
                repository_root=ROOT,
                script_path=SCRIPT_PATH,
            )
        self.assertEqual(raised.exception.reason, "bundle_path_mismatch")
        self.assertFalse(out.exists())

    def test_cli_refusal_is_nonzero_and_names_reason(self) -> None:
        out = self.root / "cli-refusal.json"
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = ISSUER.main(
                ["--bundle", str(self.bundle), "--out", str(out)]
            )
        self.assertEqual(exit_code, ISSUER.REFUSAL_EXIT_CODE)
        self.assertIn("REFUSED bundle_path_mismatch:", stderr.getvalue())
        self.assertIn("no output written", stderr.getvalue())
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
