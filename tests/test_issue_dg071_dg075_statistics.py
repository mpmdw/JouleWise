"""Focused tests for the DG-071 / DG-075 issued-statistics producer."""

from __future__ import annotations

import csv
from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import warnings


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "issue_dg071_dg075_statistics.py"
SPEC = importlib.util.spec_from_file_location(
    "issue_dg071_dg075_statistics", SCRIPT_PATH
)
assert SPEC is not None and SPEC.loader is not None
ISSUER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ISSUER
SPEC.loader.exec_module(ISSUER)


def _independent_reference(raw: bytes) -> dict[str, object]:
    groups: list[tuple[str, list[dict[str, str]]]] = []
    for row in csv.DictReader(raw.decode("utf-8").splitlines()):
        if not groups or row["timestamp_s"] != groups[-1][0]:
            groups.append((row["timestamp_s"], []))
        groups[-1][1].append(row)
    timestamps = [Decimal(group[0]) for group in groups]
    widths = [Decimal(group[1][0]["interval_end_s"]) - Decimal(group[1][0]["interval_start_s"]) for group in groups]
    spacings = [later - earlier for earlier, later in zip(timestamps, timestamps[1:])]
    gaps = [abs(Decimal(groups[i][1][0]["interval_start_s"]) - timestamps[i - 1]) for i in range(1, len(groups))]
    def describe(values: list[Decimal]) -> dict[str, object]:
        ordered = sorted(values)
        def quantile(fraction: Decimal) -> Decimal:
            position = Decimal(len(ordered) - 1) * fraction
            lower = int(position)
            return ordered[lower] if position == lower else ordered[lower] + (position - lower) * (ordered[lower + 1] - ordered[lower])
        q1, median, q3 = (quantile(fraction) for fraction in (Decimal("0.25"), Decimal("0.5"), Decimal("0.75")))
        iqr = q3 - q1
        render = lambda value: format((value * Decimal(1000)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_EVEN), "f")
        return {"sample_count": len(ordered), "q1_s": format(q1, "f"), "median_s": format(median, "f"), "q3_s": format(q3, "f"), "iqr_s": format(iqr, "f"), "q1_ms": render(q1), "median_ms": render(median), "q3_ms": render(q3), "iqr_ms": render(iqr)}
    return {"statistics": {"DG-071": describe(widths), "DG-075": describe(spacings)}, "max_tiling_gap_s": format(max(gaps, default=Decimal(0)), "f"), "tiling_gap_nonzero_boundaries": sum(gap != 0 for gap in gaps)}


def _verify_asymmetric_replay(
    *,
    checkout: Path,
    bundle: Path,
    issued_json: Path,
    replay_json: Path,
) -> dict[str, str]:
    """Authenticate immutable provenance, then replay by content identity."""

    issued_payload = json.loads(issued_json.read_text(encoding="utf-8"))
    producer = issued_payload["producer"]
    stored_commit = producer["git_commit"]
    stored_script_sha256 = producer["script_sha256"]
    script_repository_path = producer["script_path"]
    current_script = checkout / script_repository_path

    current_script_sha256 = hashlib.sha256(current_script.read_bytes()).hexdigest()
    if current_script_sha256 != stored_script_sha256:
        raise AssertionError(
            "current_script_sha256_mismatch: "
            f"stored={stored_script_sha256} current={current_script_sha256}"
        )

    historical_script = subprocess.run(
        ["git", "show", f"{stored_commit}:{script_repository_path}"],
        cwd=checkout,
        check=True,
        capture_output=True,
    ).stdout
    historical_script_sha256 = hashlib.sha256(historical_script).hexdigest()
    if historical_script_sha256 != stored_script_sha256:
        raise AssertionError(
            "historical_script_sha256_mismatch: "
            f"stored={stored_script_sha256} historical={historical_script_sha256}"
        )

    replayed_payload = ISSUER.issue_artifacts(
        bundle,
        replay_json,
        expected_bundle_path=bundle,
        expected_bundle_sha256=issued_payload["input_bundle"]["sha256"],
        repository_root=checkout,
        script_path=current_script,
    )
    current_last_touch = replayed_payload["producer"]["git_commit"]

    normalized_payload = json.loads(json.dumps(replayed_payload))
    normalized_payload["producer"]["git_commit"] = stored_commit
    normalized_json = (
        json.dumps(normalized_payload, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")
    if normalized_json != issued_json.read_bytes():
        raise AssertionError("semantic_json_replay_mismatch")
    if (
        ISSUER.render_markdown(normalized_payload).encode("utf-8")
        != issued_json.with_suffix(".md").read_bytes()
    ):
        raise AssertionError("semantic_markdown_replay_mismatch")

    warning_record = {
        "reason": "producer_last_touch_divergence",
        "stored_commit": stored_commit,
        "current_last_touch": current_last_touch,
    }
    if current_last_touch != stored_commit:
        warnings.warn(
            "producer_last_touch_divergence: "
            f"stored={stored_commit} current={current_last_touch}; "
            "replay accepted by content identity",
            RuntimeWarning,
            stacklevel=2,
        )
    return warning_record


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

    def _write_literal_rows(
        self, rows: list[tuple[str, str, str, str, str, str]]
    ) -> None:
        with self.bundle.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(ISSUER.EXPECTED_RECORD_SCHEMA)
            writer.writerows(rows)

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

    def test_golden_bundle_pins_every_reported_field(self) -> None:
        golden_rows = [
            ("1784978889.10000000", "1.0", "fixture", "cpu_power", "1784978888.99959995", "1784978889.10000000"),
            ("1784978889.10000000", "2.0", "fixture", "gpu_power", "1784978888.99959995", "1784978889.10000000"),
            ("1784978889.10000000", "3.0", "fixture", "ane_power", "1784978888.99959995", "1784978889.10000000"),
            ("1784978889.19900020", "4.0", "fixture", "cpu_power", "1784978889.10000020", "1784978889.19900020"),
            ("1784978889.19900020", "5.0", "fixture", "gpu_power", "1784978889.10000020", "1784978889.19900020"),
            ("1784978889.19900020", "6.0", "fixture", "ane_power", "1784978889.10000020", "1784978889.19900020"),
            ("1784978889.30000029", "7.0", "fixture", "cpu_power", "1784978889.19899990", "1784978889.30000029"),
            ("1784978889.30000029", "8.0", "fixture", "gpu_power", "1784978889.19899990", "1784978889.30000029"),
            ("1784978889.30000029", "9.0", "fixture", "ane_power", "1784978889.19899990", "1784978889.30000029"),
            ("1784978889.40000024", "10.0", "fixture", "cpu_power", "1784978889.30000029", "1784978889.40000024"),
            ("1784978889.40000024", "11.0", "fixture", "gpu_power", "1784978889.30000029", "1784978889.40000024"),
            ("1784978889.40000024", "12.0", "fixture", "ane_power", "1784978889.30000029", "1784978889.40000024"),
            ("1784978889.50200074", "13.0", "fixture", "cpu_power", "1784978889.40000074", "1784978889.50200074"),
            ("1784978889.50200074", "14.0", "fixture", "gpu_power", "1784978889.40000074", "1784978889.50200074"),
            ("1784978889.50200074", "15.0", "fixture", "ane_power", "1784978889.40000074", "1784978889.50200074"),
            ("1784978889.60200041", "16.0", "fixture", "cpu_power", "1784978889.50200034", "1784978889.60200041"),
            ("1784978889.60200041", "17.0", "fixture", "gpu_power", "1784978889.50200034", "1784978889.60200041"),
            ("1784978889.60200041", "18.0", "fixture", "ane_power", "1784978889.50200034", "1784978889.60200041"),
            ("1784978889.70300110", "19.0", "fixture", "cpu_power", "1784978889.60200111", "1784978889.70300110"),
            ("1784978889.70300110", "20.0", "fixture", "gpu_power", "1784978889.60200111", "1784978889.70300110"),
            ("1784978889.70300110", "21.0", "fixture", "ane_power", "1784978889.60200111", "1784978889.70300110"),
            ("1784978889.80360015", "22.0", "fixture", "cpu_power", "1784978889.70300010", "1784978889.80360015"),
            ("1784978889.80360015", "23.0", "fixture", "gpu_power", "1784978889.70300010", "1784978889.80360015"),
            ("1784978889.80360015", "24.0", "fixture", "ane_power", "1784978889.70300010", "1784978889.80360015"),
        ]
        self._write_literal_rows(golden_rows)
        golden_sha256 = (
            "cc31866f096948d8af0e8c55f80a432086dfb753f907d52825fea00da9e2d58f"
        )
        self.assertEqual(self._sha256(), golden_sha256)
        payload = ISSUER.build_payload(
            self.bundle,
            expected_bundle_path=self.bundle,
            expected_bundle_sha256=golden_sha256,
            repository_root=ROOT,
            script_path=SCRIPT_PATH,
        )
        actual = json.loads(json.dumps(payload))
        del actual["producer"]["git_commit"]
        del actual["producer"]["script_sha256"]

        # Hand derivation from Sol 250 §Q3; expected values are literals.
        # Sorted DG-071 widths:
        # 0.09900000, 0.09999995, 0.10000007, 0.10040005,
        # 0.10060005, 0.10099999, 0.10100039, 0.10200000
        # h25 = 7×0.25 = 1.75
        # Q1 = 0.09999995 + 0.75×(0.10000007−0.09999995)
        #    = 0.1000000400
        # h50 = 3.5
        # median = 0.10040005 + 0.5×(0.10060005−0.10040005)
        #         = 0.100500050
        # h75 = 5.25
        # Q3 = 0.10099999 + 0.25×(0.10100039−0.10099999)
        #    = 0.1010000900
        # IQR = 0.1010000900−0.1000000400 = 0.0010000500
        # Renderings: Q1 100.0000400 → 100.0000, median 100.500050 →
        # 100.5000, Q3 101.0000900 → 101.0001, IQR 1.0000500 → 1.0000.
        # render(IQR) = 1.0000, while render(Q3)−render(Q1) = 1.0001.
        # DG-075 spacings: 0.09900020, 0.10100009, 0.09999995,
        # 0.10200050, 0.09999967, 0.10100069, 0.10059905.
        # Sorted: 0.09900020, 0.09999967, 0.09999995, 0.10059905,
        # 0.10100009, 0.10100069, 0.10200050.
        # h25 = 6×0.25 = 1.5; Q1 = (0.09999967+0.09999995)/2 = 0.0999998100
        # h50 = 3; median = 0.10059905
        # h75 = 4.5; Q3 = (0.10100009+0.10100069)/2 = 0.1010003900
        # IQR = 0.1010003900−0.0999998100 = 0.0010005800.
        # Renderings: Q1=99.9998, median=100.5990, Q3=101.0004, IQR=1.0006.
        # Signed gaps: +0.00000020, −0.00000030, 0.00000000,
        # +0.00000050, −0.00000040, +0.00000070, −0.00000100.
        # max(abs(gap)) = 0.00000100; nonzero boundaries = 6.
        expected = {
            "input_bundle": {
                "path": "runs_window_a10_20260725/"
                "p2015-df-ph-decode-abs-r03/power_trace.csv",
                "record_schema": [
                    "timestamp_s",
                    "power_w",
                    "source",
                    "rail",
                    "interval_start_s",
                    "interval_end_s",
                ],
                "sha256": (
                    "cc31866f096948d8af0e8c55f80a432086dfb753f907d52825fea00da9e2d58f"
                ),
            },
            "max_tiling_gap_s": "0.00000100",
            "method": {
                "population": (
                    "A sampler record is one contiguous group of CSV rows — "
                    "consecutive rows in file order — that share one `timestamp_s` "
                    "literal. A literal is the character string exactly as written "
                    "in the file, before any numeric conversion; two literals are "
                    "equal only when their characters are identical. Every group "
                    "must contain exactly one row for each of `ane_power`, "
                    "`cpu_power` and `gpu_power`, and the three rows' `interval_start_s` "
                    "and `interval_end_s` literals must be identical; a timestamp "
                    "literal that reappears after another group has begun is refused. "
                    "DG-071 uses one interval width, `interval_end_s − "
                    "interval_start_s`, per sampler record."
                ),
                "arithmetic": (
                    "The timestamp and endpoint literals are parsed directly as exact "
                    "decimals. Widths, spacings, quantiles and IQR never pass through "
                    "binary floating point."
                ),
                "quantile": (
                    "For the n values sorted ascending, the quantile at probability p "
                    "uses the exact 0-based position h = (n−1)·p and exact linear "
                    "interpolation between the two neighbouring order statistics — "
                    "the sorted values at positions ⌊h⌋ and ⌊h⌋+1 (Hyndman–Fan type 7; "
                    "numpy `linear` and R type 7 are cross-references)."
                ),
                "median": (
                    "The median is the p = 0.5 quantile, which is the mean of the two "
                    "middle values for even n."
                ),
                "iqr": (
                    "IQR is Q3 − Q1, computed exactly before rendering. Because "
                    "rounding is applied after subtraction, a rendered IQR can differ "
                    "from the difference of the rendered quartiles by one unit in the "
                    "last place."
                ),
                "millisecond_rendering": (
                    "The exact seconds in the second table are the values of record: "
                    "the authoritative numbers, which nothing downstream re-derives. "
                    "The millisecond columns are renderings of them — value × 1000, "
                    "rounded to four decimal places with round-half-even, meaning a "
                    "value exactly halfway between two four-decimal neighbours goes "
                    "to the one whose last digit is even — and are never re-used as "
                    "inputs."
                ),
                "float64_replication": (
                    "A float64 replication (numpy `linear`, R type 7) is guaranteed "
                    "to agree only to three decimals because a float64 at 1.78e9 s "
                    "has spacing 2.4e-7 s, coarser than the file's 1e-7 s literals; "
                    "the digits characterise the retained bytes, not the sampler's "
                    "physical timing resolution. Worked example: median 120.9186 ms "
                    "exact vs 120.9185 ms float64."
                ),
                "tiling": (
                    "Tiling. The records tile when each record's interval ends exactly "
                    "at its own timestamp (`interval_end_s` literal identical to "
                    "`timestamp_s` literal) and begins where the previous record ended "
                    "(`interval_start_s` of record k within 0.000001 s of `timestamp_s` "
                    "of record k−1); the producer refuses otherwise. The tiling gap at "
                    "a boundary is |interval_start_s(k) − timestamp_s(k−1)| in exact "
                    "decimal seconds; the header reports the largest gap and the "
                    "number of boundaries whose gap is not zero. In this bundle 6 of "
                    "7 boundaries have a nonzero gap, the largest 0.00000100 s: the "
                    "writer formatted the interval endpoints and the timestamp from "
                    "two separately rounded binary floats, so the seventh decimal can "
                    "differ. This is the endpoint convention referred to next."
                ),
                "dg075_dependence": (
                    "DG-075 is the DG-071 distribution minus the first record: its "
                    "consecutive timestamp differences equal the widths of records "
                    "2–n up to the endpoint convention above, i.e. to within the "
                    "largest tiling gap."
                ),
                "provenance": (
                    "Provenance. The producer commit is the last commit in the "
                    "repository's history that changed the producer script (`git "
                    "log -1 --format=%H -- scripts/issue_dg071_dg075_statistics.py`), "
                    "not the commit the issuer happened to have checked out. A "
                    "committed artifact cannot name the commit that contains it, so "
                    "recording the checkout would make byte-exact replay impossible "
                    "at exactly the commit a reader checks out; recording the "
                    "script's last commit means re-running the producer from any "
                    "checkout in which the script is unchanged since that commit "
                    "reproduces both files byte for byte. The producer SHA-256 is "
                    "recorded beside it and must equal the SHA-256 of the script as "
                    "committed there (`git show <producer commit>:"
                    "scripts/issue_dg071_dg075_statistics.py`); an uncommitted edit "
                    "to the producer shows as the two hashes differing."
                ),
            },
            "producer": {
                "script_path": "scripts/issue_dg071_dg075_statistics.py"
            },
            "rail_row_count": 24,
            "rails": ["ane_power", "cpu_power", "gpu_power"],
            "registry_row_ids": ["DG-071", "DG-075"],
            "sampler_record_count": 8,
            "schema_version": "joulewise.paper.dg071-dg075-statistics.v2",
            "statistics": {
                "DG-071": {
                    "iqr_ms": "1.0000",
                    "iqr_s": "0.0010000500",
                    "median_ms": "100.5000",
                    "median_s": "0.100500050",
                    "q1_ms": "100.0000",
                    "q1_s": "0.1000000400",
                    "q3_ms": "101.0001",
                    "q3_s": "0.1010000900",
                    "sample_count": 8,
                    "statistic": "interval_end_s - interval_start_s per sampler record",
                },
                "DG-075": {
                    "iqr_ms": "1.0006",
                    "iqr_s": "0.0010005800",
                    "median_ms": "100.5990",
                    "median_s": "0.10059905",
                    "q1_ms": "99.9998",
                    "q1_s": "0.0999998100",
                    "q3_ms": "101.0004",
                    "q3_s": "0.1010003900",
                    "sample_count": 7,
                    "statistic": "consecutive differences of sorted distinct timestamp_s literals",
                },
            },
            "tiling_gap_nonzero_boundaries": 6,
        }
        self.assertEqual(actual, expected)

        out = self.root / "golden-issued.json"
        exit_code, stderr, stdout = self._run_main(
            out, pinned_sha256=golden_sha256
        )
        self.assertEqual(exit_code, 0, stderr)
        markdown_lines = out.with_suffix(".md").read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            markdown_lines[4:9],
            [
                "- Sampler records: 8",
                "- Rail rows: 24",
                "- Rails: ane_power, cpu_power, gpu_power",
                "- Largest tiling gap (s; defined under Method): 0.00000100",
                "- Boundaries with a nonzero tiling gap (see Method): 6",
            ],
        )
        table1 = [
            "| Registry row | Sample count | Q1 (ms) | Median (ms) | Q3 (ms) | IQR (ms) |",
            "|---|---:|---:|---:|---:|---:|",
            "| DG-071 | 8 | 100.0000 | 100.5000 | 101.0001 | 1.0000 |",
            "| DG-075 | 7 | 99.9998 | 100.5990 | 101.0004 | 1.0006 |",
        ]
        table2 = [
            "| Registry row | Q1 (s) | Median (s) | Q3 (s) | IQR (s) |",
            "|---|---:|---:|---:|---:|",
            "| DG-071 | 0.1000000400 | 0.100500050 | 0.1010000900 | 0.0010000500 |",
            "| DG-075 | 0.0999998100 | 0.10059905 | 0.1010003900 | 0.0010005800 |",
        ]
        table1_start = markdown_lines.index(table1[0])
        table2_start = markdown_lines.index(table2[0])
        self.assertEqual(markdown_lines[table1_start:table1_start + 4], table1)
        self.assertEqual(markdown_lines[table2_start:table2_start + 4], table2)
        self.assertEqual(
            stdout.splitlines()[-2:],
            [
                "DG-071 median_ms=100.5000 iqr_ms=1.0000",
                "DG-075 median_ms=100.5990 iqr_ms=1.0006",
            ],
        )

    def test_differential_against_independent_reference(self) -> None:
        rng = random.Random(20260902)
        gaps = [Decimal(value) for value in ("0", "0.0000001", "-0.0000001", "0.0000003", "-0.0000003", "0.000001", "-0.000001")]
        numeric_fields = ("sample_count", "q1_s", "median_s", "q3_s", "iqr_s", "q1_ms", "median_ms", "q3_ms", "iqr_ms")
        # Bundle 0 has more records than the retained bundle (406) so that a
        # computation which is right below some record count and wrong above
        # it (e.g. a cap `sorted(values[:N])`, N < 406) cannot agree with the
        # reference here while changing the published values; the other
        # bundles stay small enough to be read by hand.
        for bundle_number in range(12):
            records = []
            previous = None
            record_total = 500 if bundle_number == 0 else rng.randint(2, 8)
            for record_number in range(record_total):
                width = Decimal(rng.randint(900000, 1300000)) / Decimal("10000000")
                start = Decimal("1784978888.0000000") if previous is None else previous + rng.choice(gaps)
                end = start + width
                start_literal, end_literal = f"{start:.7f}", f"{end:.7f}"
                records.append((end_literal, start_literal, end_literal))
                previous = Decimal(end_literal)
            self._write_records(records)
            expected = _independent_reference(self.bundle.read_bytes())
            payload = self._issue(self.root / f"differential-{bundle_number}.json")
            for row_id in ("DG-071", "DG-075"):
                self.assertEqual(
                    {field: payload["statistics"][row_id][field] for field in numeric_fields},
                    expected["statistics"][row_id],
                )
            self.assertEqual(payload["max_tiling_gap_s"], expected["max_tiling_gap_s"])
            self.assertEqual(payload["tiling_gap_nonzero_boundaries"], expected["tiling_gap_nonzero_boundaries"])

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
            float(record.interval_end_s)
            - float(record.interval_start_s)
            for record in records
        )
        float_median_ms = (float_widths[1] + float_widths[2]) * 500
        self.assertEqual(f"{float_median_ms:.4f}", "120.9185")

    def test_millisecond_rendering_ties_round_half_even_through_main(
        self,
    ) -> None:
        """Counterfactual: ROUND_HALF_UP would print 1.2345 for 1.23445 ms.

        Two records of identical width make every quantile equal that width,
        so the rendering rule alone decides the digits. terra 248 SF-EXEC-01.
        """

        cases = {
            # 1.23445 ms: preceding digit even -> stays 1.2344 (half-up: 1.2345)
            "even": ("0.00123445", "1.2344"),
            # 1.23455 ms: preceding digit odd -> rounds to 1.2346 (both rules)
            "odd": ("0.00123455", "1.2346"),
        }
        for name, (width_s, expected_ms) in cases.items():
            first_end = Decimal("1") + Decimal(width_s)
            second_end = first_end + Decimal(width_s)
            self._write_records(
                [
                    (str(first_end), "1", str(first_end)),
                    (str(second_end), str(first_end), str(second_end)),
                ]
            )
            out = self.root / f"tie-{name}.json"
            exit_code, stderr, _ = self._run_main(out)
            self.assertEqual(exit_code, 0, stderr)
            payload = json.loads(out.read_text(encoding="utf-8"))
            for row_id in ("DG-071", "DG-075"):
                self.assertEqual(
                    payload["statistics"][row_id]["median_ms"], expected_ms
                )

    def test_method_disclosure_is_replicable_from_both_artifacts(self) -> None:
        out = self.root / "method.json"
        payload = self._issue(out)
        method = payload["method"]
        self.assertIn("h = (n−1)·p", method["quantile"])
        self.assertIn("mean of the two middle", method["median"])
        self.assertIn("round-half-even", method["millisecond_rendering"])
        self.assertIn("last place", method["iqr"])
        self.assertIn("numpy `linear`, R type 7", method["float64_replication"])
        self.assertIn("Tiling.", method["tiling"])
        self.assertIn("Provenance.", method["provenance"])
        self.assertIn("last commit", method["provenance"])
        docstring = " ".join((ISSUER.__doc__ or "").split())
        for phrase in (
            "the last commit that changed this script",
            "A literal is the character string exactly as written in the file",
            "parsed directly as exact decimals",
            "h = (n−1)·p",
            "the values of record",
            "Worked example: median 120.9186 ms exact vs 120.9185 ms float64",
            "Tiling. The records tile",
            "DG-075 is the DG-071 distribution minus the first record",
        ):
            self.assertIn(phrase, docstring)
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
        self.assertIn("- Producer commit (last commit that changed", markdown)
        self.assertIn("Provenance. The producer commit is the last commit", markdown)

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

    def test_git_commit_uses_the_disclosed_path_query(self) -> None:
        """Counterfactual: any argv substitution violates the published contract."""

        expected_commit = "a" * 40
        completed = mock.Mock(stdout=f"{expected_commit}\n")
        with mock.patch.object(
            ISSUER.subprocess, "run", return_value=completed
        ) as run:
            self.assertEqual(ISSUER._git_commit(self.root), expected_commit)

        run.assert_called_once_with(
            [
                "git",
                "log",
                "-1",
                "--format=%H",
                "--",
                ISSUER.SCRIPT_REPOSITORY_PATH,
            ],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_producer_commit_on_axis_derived_history_pair(self) -> None:
        """Exercise the disclosed query on the ruled F2 repository pair.

        Both repositories share root -> add -> L, where L changes the producer
        to the bytes on disk. Repository A stops at L. Repository B merges L
        with ``--no-ff``, changes another script, adds an empty commit, and has
        a later producer change on an unreachable ref. Distinct pinned commit
        times make the query independent of timestamp tie-breaking.
        """

        checkouts = [self.root / "checkout-a", self.root / "checkout-b"]
        fixture_raw = self.bundle.read_bytes()
        script_raw = SCRIPT_PATH.read_bytes()
        path = ISSUER.SCRIPT_REPOSITORY_PATH

        def environment(date: str) -> dict[str, str]:
            return {
                **os.environ,
                "GIT_AUTHOR_NAME": "Fixture Author",
                "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                "GIT_AUTHOR_DATE": date,
                "GIT_COMMITTER_NAME": "Fixture Committer",
                "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
                "GIT_COMMITTER_DATE": date,
            }

        def git(
            checkout: Path,
            *arguments: str,
            date: str = "2000-01-01T00:00:00+00:00",
        ) -> str:
            completed = subprocess.run(
                ["git", "-c", "commit.gpgSign=false", *arguments],
                cwd=checkout,
                env=environment(date),
                check=True,
                capture_output=True,
                text=True,
            )
            return completed.stdout.strip()

        def commit(checkout: Path, message: str, *, date: str) -> str:
            git(checkout, "add", "-A", date=date)
            git(
                checkout,
                "commit",
                "--quiet",
                "--allow-empty",
                "-m",
                message,
                date=date,
            )
            return git(checkout, "rev-parse", "HEAD")

        def stamp(second: int) -> str:
            return f"2000-01-01T00:00:{second:02d}+00:00"

        def sha256_at(checkout: Path, commit_id: str) -> str:
            blob = subprocess.run(
                ["git", "show", f"{commit_id}:{path}"],
                cwd=checkout,
                check=True,
                capture_output=True,
            ).stdout
            return hashlib.sha256(blob).hexdigest()

        outputs: list[bytes] = []
        producer_commits: list[str] = []
        for index, checkout in enumerate(checkouts):
            fixture = checkout / ISSUER.PINNED_BUNDLE_REPOSITORY_PATH
            fixture.parent.mkdir(parents=True)
            fixture.write_bytes(fixture_raw)
            script = checkout / path
            script.parent.mkdir(parents=True)
            git(checkout, "init", "--quiet")
            git(checkout, "checkout", "--quiet", "-b", "trunk")
            commit(checkout, "root", date=stamp(0))
            script.write_bytes(script_raw + b"# earlier revision\n")
            add_commit = commit(checkout, "add producer", date=stamp(1))
            script.write_bytes(script_raw)
            producer = commit(checkout, "modify producer", date=stamp(2))
            producer_commits.append(producer)

            if index == 1:
                git(checkout, "checkout", "--quiet", "-B", "trunk", add_commit)
                git(
                    checkout,
                    "merge",
                    "--quiet",
                    "--no-ff",
                    "-m",
                    "merge producer",
                    producer,
                    date=stamp(3),
                )
                merge_commit = git(checkout, "rev-parse", "HEAD")
                (checkout / "scripts" / "other.py").write_text(
                    "x = 1\n", encoding="utf-8"
                )
                commit(checkout, "other script", date=stamp(4))
                empty_commit = commit(checkout, "later", date=stamp(5))
                git(checkout, "checkout", "--quiet", "-b", "unreachable", producer)
                script.write_bytes(script_raw + b"# unreachable later revision\n")
                commit(
                    checkout,
                    "unreachable producer change",
                    date=stamp(6),
                )
                git(checkout, "checkout", "--quiet", "trunk")

            head = git(checkout, "rev-parse", "HEAD")
            out = checkout / "issued.json"
            exit_code, stderr, _ = self._run_main(
                out,
                pinned_path=fixture,
                pinned_sha256=hashlib.sha256(fixture_raw).hexdigest(),
                repository_root=checkout,
            )
            self.assertEqual(exit_code, 0, stderr)
            outputs.append(out.read_bytes())
            payload = json.loads(outputs[-1])
            recorded = payload["producer"]["git_commit"]
            self.assertEqual(recorded, producer)
            self.assertEqual(
                sha256_at(checkout, recorded),
                payload["producer"]["script_sha256"],
            )
            self.assertEqual(
                git(checkout, "rev-list", f"{recorded}..HEAD", "--", path),
                "",
            )
            self.assertNotEqual(add_commit, recorded)

            dates = git(checkout, "log", "--all", "--format=%aI").splitlines()
            self.assertEqual(len(dates), len(set(dates)))
            if index == 0:
                self.assertEqual(head, recorded)
            else:
                merge_parents = git(
                    checkout, "show", "-s", "--format=%P", merge_commit
                ).split()
                self.assertEqual(len(merge_parents), 2)
                self.assertEqual(merge_parents[1], recorded)
                self.assertEqual(
                    git(checkout, "rev-parse", f"{empty_commit}^{{tree}}"),
                    git(checkout, "rev-parse", f"{empty_commit}^^{{tree}}"),
                )
                for depth in ("HEAD", "HEAD^", "HEAD~2", "HEAD~3"):
                    self.assertNotEqual(git(checkout, "rev-parse", depth), recorded)
                for candidate in (
                    git(checkout, "log", "-1", "--format=%H"),
                    git(
                        checkout,
                        "log",
                        "-1",
                        "--format=%H",
                        "--",
                        "scripts/",
                    ),
                    git(
                        checkout,
                        "log",
                        "-1",
                        "--format=%H",
                        "--",
                        "scripts/*.py",
                    ),
                    git(
                        checkout,
                        "log",
                        "--first-parent",
                        "-1",
                        "--format=%H",
                        "--",
                        path,
                    ),
                    git(
                        checkout,
                        "log",
                        "--all",
                        "-1",
                        "--format=%H",
                        "--",
                        path,
                    ),
                ):
                    self.assertNotEqual(candidate, recorded)
                self.assertNotEqual(
                    git(checkout, "rev-list", "HEAD..unreachable", "--", path),
                    "",
                )

        self.assertEqual(producer_commits[0], producer_commits[1])
        self.assertEqual(outputs[0], outputs[1])
        payload = json.loads(outputs[0])
        self.assertEqual(
            payload["input_bundle"]["path"],
            "runs_window_a10_20260725/"
            "p2015-df-ph-decode-abs-r03/power_trace.csv",
        )
        self.assertFalse(payload["input_bundle"]["path"].startswith("/"))

    def test_change_then_exact_restore_replays_with_divergence_warning(self) -> None:
        """Current last-touch divergence warns; content-identity replay passes."""

        checkout = self.root / "checkout"
        checkout.mkdir()
        fixture_raw = self.bundle.read_bytes()
        fixture = checkout / ISSUER.PINNED_BUNDLE_REPOSITORY_PATH
        fixture.parent.mkdir(parents=True)
        fixture.write_bytes(fixture_raw)
        script_raw = SCRIPT_PATH.read_bytes()
        script = checkout / ISSUER.SCRIPT_REPOSITORY_PATH
        script.parent.mkdir(parents=True)
        script.write_bytes(script_raw)

        def git_environment(date: str) -> dict[str, str]:
            return {
                **os.environ,
                "GIT_AUTHOR_NAME": "Fixture Author",
                "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                "GIT_AUTHOR_DATE": date,
                "GIT_COMMITTER_NAME": "Fixture Committer",
                "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
                "GIT_COMMITTER_DATE": date,
            }

        def git(*arguments: str, date: str) -> str:
            completed = subprocess.run(
                ["git", "-c", "commit.gpgSign=false", *arguments],
                cwd=checkout,
                env=git_environment(date),
                check=True,
                capture_output=True,
                text=True,
            )
            return completed.stdout.strip()

        git("init", "--quiet", date="2000-01-01T00:00:00+00:00")
        git(
            "add",
            ISSUER.SCRIPT_REPOSITORY_PATH,
            date="2000-01-01T00:00:00+00:00",
        )
        git(
            "commit",
            "--quiet",
            "-m",
            "producer P",
            date="2000-01-01T00:00:00+00:00",
        )
        producer_commit = git(
            "rev-parse", "HEAD", date="2000-01-01T00:00:00+00:00"
        )
        issued_json = self.root / "issued.json"
        issued_payload = ISSUER.issue_artifacts(
            fixture,
            issued_json,
            expected_bundle_path=fixture,
            expected_bundle_sha256=hashlib.sha256(fixture_raw).hexdigest(),
            repository_root=checkout,
            script_path=script,
        )
        self.assertEqual(issued_payload["producer"]["git_commit"], producer_commit)

        script.write_bytes(script_raw + b"# counterfactual producer edit\n")
        git(
            "add",
            ISSUER.SCRIPT_REPOSITORY_PATH,
            date="2000-01-02T00:00:00+00:00",
        )
        git(
            "commit",
            "--quiet",
            "-m",
            "producer edit",
            date="2000-01-02T00:00:00+00:00",
        )
        script.write_bytes(script_raw)
        git(
            "add",
            ISSUER.SCRIPT_REPOSITORY_PATH,
            date="2000-01-03T00:00:00+00:00",
        )
        git(
            "commit",
            "--quiet",
            "-m",
            "exact restoration R",
            date="2000-01-03T00:00:00+00:00",
        )
        restoration_commit = git(
            "rev-parse", "HEAD", date="2000-01-03T00:00:00+00:00"
        )
        self.assertNotEqual(restoration_commit, producer_commit)
        self.assertEqual(ISSUER._git_commit(checkout), restoration_commit)

        replay_json = self.root / "replayed.json"
        with self.assertWarnsRegex(
            RuntimeWarning,
            r"producer_last_touch_divergence: stored=[0-9a-f]{40} "
            r"current=[0-9a-f]{40}; replay accepted by content identity",
        ):
            warning_record = _verify_asymmetric_replay(
                checkout=checkout,
                bundle=fixture,
                issued_json=issued_json,
                replay_json=replay_json,
            )
        self.assertEqual(
            warning_record,
            {
                "reason": "producer_last_touch_divergence",
                "stored_commit": producer_commit,
                "current_last_touch": restoration_commit,
            },
        )

    def test_producer_commit_when_script_was_only_added(self) -> None:
        """Counterfactual: a modification-only path query returns no commit."""

        checkout = self.root / "add-only"
        fixture_raw = self.bundle.read_bytes()
        fixture = checkout / ISSUER.PINNED_BUNDLE_REPOSITORY_PATH
        fixture.parent.mkdir(parents=True)
        fixture.write_bytes(fixture_raw)
        script = checkout / ISSUER.SCRIPT_REPOSITORY_PATH
        script.parent.mkdir(parents=True)
        script.write_bytes(SCRIPT_PATH.read_bytes())
        environment = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Fixture Author",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+00:00",
            "GIT_COMMITTER_NAME": "Fixture Committer",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+00:00",
        }

        def git(*arguments: str) -> str:
            completed = subprocess.run(
                ["git", "-c", "commit.gpgSign=false", *arguments],
                cwd=checkout,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            return completed.stdout.strip()

        git("init", "--quiet")
        git("add", ISSUER.SCRIPT_REPOSITORY_PATH)
        git("commit", "--quiet", "-m", "add producer")
        producer = git("rev-parse", "HEAD")
        self.assertEqual(
            git(
                "log",
                "--diff-filter=A",
                "-1",
                "--format=%H",
                "--",
                ISSUER.SCRIPT_REPOSITORY_PATH,
            ),
            producer,
        )
        self.assertEqual(
            git(
                "log",
                "--diff-filter=M",
                "-1",
                "--format=%H",
                "--",
                ISSUER.SCRIPT_REPOSITORY_PATH,
            ),
            "",
        )

        out = checkout / "issued.json"
        exit_code, stderr, _ = self._run_main(
            out,
            pinned_path=fixture,
            pinned_sha256=hashlib.sha256(fixture_raw).hexdigest(),
            repository_root=checkout,
        )
        self.assertEqual(exit_code, 0, stderr)
        payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(payload["producer"]["git_commit"], producer)

    def test_retained_bundle_values_of_record(self) -> None:
        """Pin the numbers the paper prints, on the retained bundle itself.

        The retained corpus is gitignored, so this runs only where it exists
        (the bench); CI enforces the same cardinality regime through the
        500-record differential bundle instead.
        """

        if not ISSUER.PINNED_BUNDLE_PATH.is_file():
            self.skipTest(
                "runs_window corpus absent (clean checkout without bundles)"
            )
        out = self.root / "retained.json"
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = ISSUER.main(
                ["--repository-root", str(ROOT), "--out", str(out)]
            )
        self.assertEqual(exit_code, 0)
        self.assertIn("DG-071 median_ms=120.9186 iqr_ms=5.9508", stdout.getvalue())
        self.assertIn("DG-075 median_ms=120.9224 iqr_ms=5.8949", stdout.getvalue())
        payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(payload["input_bundle"]["sha256"], ISSUER.PINNED_BUNDLE_SHA256)
        self.assertEqual(payload["sampler_record_count"], 406)
        self.assertEqual(payload["max_tiling_gap_s"], "0.0000004")
        self.assertEqual(payload["tiling_gap_nonzero_boundaries"], 100)
        dg071 = payload["statistics"]["DG-071"]
        dg075 = payload["statistics"]["DG-075"]
        self.assertEqual(
            [dg071[key] for key in ("sample_count", "q1_ms", "median_ms", "q3_ms", "iqr_ms")],
            [406, "116.9720", "120.9186", "122.9227", "5.9508"],
        )
        self.assertEqual(
            [dg075[key] for key in ("sample_count", "q1_ms", "median_ms", "q3_ms", "iqr_ms")],
            [405, "117.0321", "120.9224", "122.9270", "5.8949"],
        )
        self.assertEqual(
            [dg071[key] for key in ("q1_s", "median_s", "q3_s", "iqr_s")],
            ["0.116971950", "0.12091860", "0.122922700", "0.005950750"],
        )
        self.assertEqual(
            [dg075[key] for key in ("q1_s", "median_s", "q3_s", "iqr_s")],
            ["0.1170321", "0.1209224", "0.122927", "0.0058949"],
        )

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
        """Counterfactuals: a record lacks a rail, or one sibling end or
        start literal differs (the start case kills the `len(starts) != 1`
        guard mutant — terra 248 SF-EXEC-02)."""

        fixtures = {
            "different-start": [
                ("10", "cpu_power", "9", "10"),
                ("10", "gpu_power", "9.0000001", "10"),
                ("10", "ane_power", "9", "10"),
                ("11", "cpu_power", "10", "11"),
                ("11", "gpu_power", "10", "11"),
                ("11", "ane_power", "10", "11"),
            ],
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
        """Counterfactual: git returns a non-40-hex commit for valid input."""

        completed = mock.Mock(stdout="not-a-commit\n")
        with mock.patch.object(
            ISSUER.subprocess, "run", return_value=completed
        ):
            self._assert_main_refusal(
                "git_commit_invalid", "git-invalid.json"
            )

    def test_uncommitted_script_refusal_reaches_main(self) -> None:
        """Counterfactual: the producer script has no commit (git log is empty)."""

        completed = mock.Mock(stdout="\n")
        with mock.patch.object(
            ISSUER.subprocess, "run", return_value=completed
        ):
            self._assert_main_refusal(
                "git_commit_invalid", "git-uncommitted.json"
            )

    def test_output_path_invalid_refusal_reaches_main(self) -> None:
        """Counterfactual: --out has a suffix other than .json."""

        self._assert_main_refusal("output_path_invalid", "issued.txt")


if __name__ == "__main__":
    unittest.main()
