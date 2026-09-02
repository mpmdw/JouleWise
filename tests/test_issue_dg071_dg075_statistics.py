"""Focused tests for the DG-071 / DG-075 issued-statistics producer."""

from __future__ import annotations

import csv
from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "issue_dg071_dg075_statistics.py"
SPEC = importlib.util.spec_from_file_location(
    "issue_dg071_dg075_statistics", SCRIPT_PATH
)
assert SPEC is not None and SPEC.loader is not None
ISSUER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ISSUER
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
                ("10.0", "9.0", "10.0"),
                ("12.0", "10.0", "12.0"),
                ("15.0", "12.0", "15.0"),
                ("19.0", "15.0", "19.0"),
                ("24.0", "19.0", "24.0"),
            ]
        )

    def _write_rows(
        self, rows: list[tuple[str, str, str, str]]
    ) -> None:
        with self.bundle.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(ISSUER.EXPECTED_RECORD_SCHEMA)
            for index, (timestamp, rail, start, end) in enumerate(rows):
                writer.writerow(
                    [timestamp, f"{index + 1}.0", "fixture", rail, start, end]
                )

    def _write_records(
        self,
        records: list[tuple[str, str, str]],
        *,
        rails: tuple[str, ...] = (
            "cpu_power",
            "gpu_power",
            "ane_power",
        ),
    ) -> None:
        self._write_rows(
            [
                (timestamp, rail, start, end)
                for timestamp, start, end in records
                for rail in rails
            ]
        )

    def _sha256(self, path: Path | None = None) -> str:
        target = path or self.bundle
        return hashlib.sha256(target.read_bytes()).hexdigest()

    def _issue(self, out: Path, *, expected_sha256: str | None = None):
        return ISSUER.issue_artifacts(
            self.bundle,
            out,
            expected_bundle_path=self.bundle,
            expected_bundle_sha256=expected_sha256 or self._sha256(),
            repository_root=ROOT,
            script_path=SCRIPT_PATH,
        )

    def _run_main(
        self,
        out: Path,
        *,
        bundle_argument: Path | None = None,
        pinned_path: Path | None = None,
        pinned_sha256: str | None = None,
        repository_root: Path = ROOT,
    ) -> tuple[int, str, str]:
        expected_path = pinned_path or self.bundle
        expected_sha = pinned_sha256 or (
            self._sha256(expected_path) if expected_path.is_file() else "0" * 64
        )
        argv = [
            "--repository-root",
            str(repository_root),
            "--out",
            str(out),
        ]
        if bundle_argument is not None:
            argv[0:0] = ["--bundle", str(bundle_argument)]
        stderr = io.StringIO()
        stdout = io.StringIO()
        with (
            mock.patch.object(ISSUER, "PINNED_BUNDLE_PATH", expected_path),
            mock.patch.object(ISSUER, "PINNED_BUNDLE_SHA256", expected_sha),
            redirect_stderr(stderr),
            redirect_stdout(stdout),
        ):
            exit_code = ISSUER.main(argv)
        return exit_code, stderr.getvalue(), stdout.getvalue()

    def _assert_main_refusal(
        self,
        reason: str,
        out_name: str,
        **main_kwargs: object,
    ) -> str:
        out = self.root / out_name
        exit_code, stderr, _ = self._run_main(out, **main_kwargs)
        self.assertEqual(exit_code, ISSUER.REFUSAL_EXIT_CODE)
        self.assertIn(f"REFUSED {reason}:", stderr)
        self.assertIn("no output written", stderr)
        self.assertFalse(out.exists())
        self.assertFalse(out.with_suffix(".md").exists())
        return stderr

    def test_five_records_have_hand_computable_statistics(self) -> None:
        out = self.root / "issued.json"
        payload = self._issue(out)

        # Record widths [1, 2, 3, 4, 5]: Q1 2, median 3, Q3 4, IQR 2.
        dg071 = payload["statistics"]["DG-071"]
        self.assertEqual(
            tuple(Decimal(dg071[key]) for key in (
                "median_s", "q1_s", "q3_s", "iqr_s"
            )),
            (Decimal(3), Decimal(2), Decimal(4), Decimal(2)),
        )

        # Distinct stamps [10, 12, 15, 19, 24] -> [2, 3, 4, 5].
        dg075 = payload["statistics"]["DG-075"]
        self.assertEqual(
            tuple(Decimal(dg075[key]) for key in (
                "median_s", "q1_s", "q3_s", "iqr_s"
            )),
            (
                Decimal("3.5"),
                Decimal("2.75"),
                Decimal("4.25"),
                Decimal("1.5"),
            ),
        )
        self.assertEqual(payload["sampler_record_count"], 5)
        self.assertEqual(payload["rail_row_count"], 15)
        self.assertEqual(
            payload["rails"], ["ane_power", "cpu_power", "gpu_power"]
        )
        self.assertEqual(payload["max_tiling_gap_s"], "0.0")
        self.assertEqual(payload["tiling_gap_nonzero_boundaries"], 0)
        self.assertEqual(payload["schema_version"], ISSUER.SCHEMA_VERSION)
        self.assertEqual(json.loads(out.read_text(encoding="utf-8")), payload)
        self.assertTrue(
            all(
                isinstance(dg071[key], str)
                for key in (
                    "q1_s", "median_s", "q3_s", "iqr_s",
                    "q1_ms", "median_ms", "q3_ms", "iqr_ms",
                )
            )
        )
        self.assertIn(
            "| DG-071 | 5 | 2000.0000 | 3000.0000 | "
            "4000.0000 | 2000.0000 |",
            out.with_suffix(".md").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            payload["input_bundle"]["path"],
            "runs_window_a10_20260725/"
            "p2015-df-ph-decode-abs-r03/power_trace.csv",
        )
        self.assertFalse(payload["input_bundle"]["path"].startswith("/"))

    def test_type_7_quantile_interpolates_exactly(self) -> None:
        self._write_records(
            [
                ("10", "9", "10"),
                ("12", "10", "12"),
                ("15", "12", "15"),
                ("19", "15", "19"),
                ("24", "19", "24"),
                ("30", "24", "30"),
            ]
        )
        payload = self._issue(self.root / "type-7.json")
        dg071 = payload["statistics"]["DG-071"]
        self.assertEqual(dg071["q1_s"], "2.25")
        self.assertEqual(dg071["median_s"], "3.5")
        self.assertEqual(dg071["q3_s"], "4.75")

    def test_precision_regression_uses_exact_epoch_literals(self) -> None:
        self._write_records(
            [
                (
                    "1784978889.1000000",
                    "1784978889.0000000",
                    "1784978889.1000000",
                ),
                (
                    "1784978889.2209139",
                    "1784978889.0999991",
                    "1784978889.2209139",
                ),
                (
                    "1784978889.3418353",
                    "1784978889.2209129",
                    "1784978889.3418353",
                ),
                (
                    "1784978889.4818343",
                    "1784978889.3418343",
                    "1784978889.4818343",
                ),
            ]
        )
        payload = self._issue(self.root / "precision.json")
        self.assertEqual(
            payload["statistics"]["DG-071"]["median_ms"], "120.9186"
        )

        records, _ = ISSUER._read_records(self.bundle.read_bytes())
        float_widths = sorted(
            float(record.interval_end_literal)
            - float(record.interval_start_literal)
            for record in records
        )
        float_median_ms = (float_widths[1] + float_widths[2]) * 500
        self.assertEqual(f"{float_median_ms:.4f}", "120.9185")

    def test_method_disclosure_is_replicable_from_both_artifacts(self) -> None:
        out = self.root / "method.json"
        payload = self._issue(out)
        method = payload["method"]
        self.assertIn("h = (n - 1) * p", method["quantile"])
        self.assertIn("mean of the two middle", method["median"])
        self.assertIn("round-half-even", method["millisecond_rendering"])
        self.assertIn("numpy `linear`, R type 7", method["float64_replication"])
        markdown = out.with_suffix(".md").read_text(encoding="utf-8")
        self.assertIn("## Method", markdown)
        self.assertIn("h = (n−1)·p", markdown)
        self.assertIn("Hyndman–Fan type 7", markdown)
        self.assertIn(
            "median 120.9186 ms exact vs 120.9185 ms float64", markdown
        )
        self.assertIn(
            "DG-075 is the DG-071 distribution minus the first record",
            markdown,
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

    def test_two_checkout_roots_produce_byte_identical_json(self) -> None:
        checkouts = [self.root / "checkout-a", self.root / "checkout-b"]
        fixture_raw = self.bundle.read_bytes()
        git_environment = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Fixture Author",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+00:00",
            "GIT_COMMITTER_NAME": "Fixture Committer",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+00:00",
        }
        outputs = []
        for checkout in checkouts:
            fixture = checkout / ISSUER.PINNED_BUNDLE_REPOSITORY_PATH
            fixture.parent.mkdir(parents=True)
            fixture.write_bytes(fixture_raw)
            subprocess.run(
                ["git", "init", "--quiet"], cwd=checkout, check=True
            )
            subprocess.run(
                [
                    "git",
                    "-c",
                    "commit.gpgSign=false",
                    "commit",
                    "--quiet",
                    "--allow-empty",
                    "-m",
                    "fixture",
                ],
                cwd=checkout,
                env=git_environment,
                check=True,
            )
            out = checkout / "issued.json"
            exit_code, stderr, _ = self._run_main(
                out,
                pinned_path=fixture,
                pinned_sha256=hashlib.sha256(fixture_raw).hexdigest(),
                repository_root=checkout,
            )
            self.assertEqual(exit_code, 0, stderr)
            outputs.append(out.read_bytes())

        self.assertEqual(outputs[0], outputs[1])
        payload = json.loads(outputs[0])
        self.assertEqual(
            payload["input_bundle"]["path"],
            "runs_window_a10_20260725/"
            "p2015-df-ph-decode-abs-r03/power_trace.csv",
        )
        self.assertFalse(payload["input_bundle"]["path"].startswith("/"))

    def test_bundle_path_mismatch_refusal_reaches_main(self) -> None:
        """Counterfactual: --bundle names a file other than the path pin."""

        self._assert_main_refusal(
            "bundle_path_mismatch",
            "path-mismatch.json",
            bundle_argument=self.bundle,
            pinned_path=self.root / "different" / "power_trace.csv",
        )

    def test_bundle_path_unavailable_refusal_reaches_main(self) -> None:
        """Counterfactual: the exact pinned bundle path is not a file."""

        self._assert_main_refusal(
            "bundle_path_unavailable",
            "path-unavailable.json",
            pinned_path=self.root / "absent" / "power_trace.csv",
        )

    def test_bundle_sha256_mismatch_refusal_reaches_main(self) -> None:
        """Counterfactual: pinned bytes do not match the pinned SHA-256."""

        self._assert_main_refusal(
            "bundle_sha256_mismatch",
            "sha-mismatch.json",
            pinned_sha256="0" * 64,
        )

    def test_record_schema_mismatch_refusal_reaches_main(self) -> None:
        """Counterfactual: the CSV header omits the pinned rail column."""

        self.bundle.write_text(
            "timestamp_s,power_w,source,interval_start_s,interval_end_s\n",
            encoding="utf-8",
        )
        self._assert_main_refusal(
            "record_schema_mismatch", "schema-mismatch.json"
        )

    def test_record_field_missing_refusal_reaches_main(self) -> None:
        """Counterfactual: a rail row has an empty interval_end_s field."""

        self.bundle.write_text(
            "timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
            "10,1,fixture,cpu_power,9,\n",
            encoding="utf-8",
        )
        stderr = self._assert_main_refusal(
            "record_field_missing", "field-missing.json"
        )
        self.assertIn("missing interval_end_s", stderr)

    def test_record_field_invalid_refusal_reaches_main(self) -> None:
        """Counterfactual: timestamp_s is a non-finite Decimal literal."""

        self.bundle.write_text(
            "timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
            "NaN,1,fixture,cpu_power,9,10\n",
            encoding="utf-8",
        )
        self._assert_main_refusal(
            "record_field_invalid", "field-invalid.json"
        )

    def test_timestamps_non_monotone_refusal_reaches_main(self) -> None:
        """Counterfactual: a complete timestamp group follows a later one."""

        self._write_records(
            [("10", "9", "10"), ("9", "8", "9")]
        )
        self._assert_main_refusal(
            "timestamps_non_monotone", "non-monotone.json"
        )

    def test_records_not_contiguous_refusal_reaches_main(self) -> None:
        """Counterfactual: rows for timestamp 10 straddle timestamp 11."""

        self._write_rows(
            [
                ("10", "cpu_power", "9", "10"),
                ("11", "cpu_power", "10", "11"),
                ("10", "gpu_power", "9", "10"),
            ]
        )
        self._assert_main_refusal(
            "records_not_contiguous", "not-contiguous.json"
        )

    def test_record_interval_not_positive_refusal_reaches_main(self) -> None:
        """Counterfactual: one three-rail record has zero interval width."""

        self._write_records(
            [("10", "10", "10"), ("11", "10", "11")]
        )
        self._assert_main_refusal(
            "record_interval_not_positive", "non-positive.json"
        )

    def test_record_rail_set_mismatch_refusal_reaches_main(self) -> None:
        """Counterfactuals: a record lacks a rail or one sibling end differs."""

        fixtures = {
            "missing-rail": [
                ("10", "cpu_power", "9", "10"),
                ("10", "gpu_power", "9", "10"),
                ("11", "cpu_power", "10", "11"),
                ("11", "gpu_power", "10", "11"),
                ("11", "ane_power", "10", "11"),
            ],
            "different-end": [
                ("10", "cpu_power", "9", "10"),
                ("10", "gpu_power", "9", "10.0000001"),
                ("10", "ane_power", "9", "10"),
                ("11", "cpu_power", "10", "11"),
                ("11", "gpu_power", "10", "11"),
                ("11", "ane_power", "10", "11"),
            ],
        }
        for name, rows in fixtures.items():
            self._write_rows(rows)
            self._assert_main_refusal(
                "record_rail_set_mismatch", f"rail-{name}.json"
            )

    def test_record_set_empty_refusal_reaches_main(self) -> None:
        """Counterfactual: the pinned CSV contains a header and no rows."""

        self.bundle.write_text(
            ",".join(ISSUER.EXPECTED_RECORD_SCHEMA) + "\n", encoding="utf-8"
        )
        self._assert_main_refusal("record_set_empty", "empty.json")

    def test_insufficient_unique_timestamps_refusal_reaches_main(self) -> None:
        """Counterfactual: the CSV contains only one complete sampler record."""

        self._write_records([("10", "9", "10")])
        self._assert_main_refusal(
            "insufficient_unique_timestamps", "one-record.json"
        )

    def test_records_do_not_tile_refusal_reaches_main(self) -> None:
        """Counterfactuals: a 5 ms pause or an end/timestamp mismatch."""

        self._write_records(
            [("10", "9", "10"), ("11", "10.005", "11")]
        )
        self._assert_main_refusal(
            "records_do_not_tile", "does-not-tile-gap.json"
        )
        self._write_records(
            [("10", "9", "9.9999999"), ("11", "10", "11")]
        )
        self._assert_main_refusal(
            "records_do_not_tile", "does-not-tile-end.json"
        )

    def test_git_commit_unavailable_refusal_reaches_main(self) -> None:
        """Counterfactual: git cannot read HEAD for an otherwise valid input."""

        with mock.patch.object(
            ISSUER.subprocess, "run", side_effect=OSError("git unavailable")
        ):
            self._assert_main_refusal(
                "git_commit_unavailable", "git-unavailable.json"
            )

    def test_git_commit_invalid_refusal_reaches_main(self) -> None:
        """Counterfactual: git returns a non-40-hex HEAD for valid input."""

        completed = mock.Mock(stdout="not-a-commit\n")
        with mock.patch.object(
            ISSUER.subprocess, "run", return_value=completed
        ):
            self._assert_main_refusal(
                "git_commit_invalid", "git-invalid.json"
            )

    def test_output_path_invalid_refusal_reaches_main(self) -> None:
        """Counterfactual: --out has a suffix other than .json."""

        self._assert_main_refusal("output_path_invalid", "issued.txt")


if __name__ == "__main__":
    unittest.main()
