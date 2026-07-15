"""Tests for the static HTML report generator (Slice 2J; D-006, D-009, D-011).

Bundles are built the real way - via ``run_benchmark`` on a ``FakeClock`` (the
all-mock vertical slice) into a temp runs dir - so the report renders genuine
artifact shapes, not hand-rolled fixtures.

Matplotlib is the ``[analysis]`` extra and CI installs no extras, so the
chart-producing tests are gated on ``HAS_MPL`` and skip cleanly when it is
absent: the suite must be green both with and without matplotlib. The always-run
tests cover the missing-matplotlib failure path (forced by masking the module in
``sys.modules`` so the import raises even when matplotlib happens to be
installed) through both ``generate_report`` and ``cli.main``.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from joulewise.clock import FakeClock
from joulewise.controller import run_benchmark
from joulewise.report import ReportError, generate_report
from joulewise.schemas import BenchmarkConfig

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_local.json"

#: matplotlib is the [analysis] extra; the chart tests skip when it is absent.
HAS_MPL = importlib.util.find_spec("matplotlib") is not None


def _build_bundle(runs_dir: Path, run_id: str, *, unsupported: bool = False) -> Path:
    """Run one mock benchmark into ``runs_dir`` and return the bundle path."""
    data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
    data["run_id"] = run_id
    if unsupported:
        data["model"]["name"] = "mock-unsupported"
    config = BenchmarkConfig.from_mapping(data)
    bundle_path, _summary = run_benchmark(config, runs_dir, FakeClock())
    return bundle_path


class ReportTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.runs_dir = self.tmp / "runs"
        self.output_dir = self.tmp / "report"
        # One succeeded run and one unsupported run, the contract's two shapes.
        _build_bundle(self.runs_dir, "report-success")
        _build_bundle(self.runs_dir, "report-unsupported", unsupported=True)


# ---------------------------------------------------------------------------
# Missing-matplotlib path (always runs - masks the module so the import raises)


class MissingMatplotlibTests(ReportTestCase):
    """matplotlib absent => ReportError naming [analysis], before any output."""

    def test_generate_report_raises_report_error_naming_extra(self) -> None:
        with mock.patch.dict(
            sys.modules, {"matplotlib": None, "matplotlib.pyplot": None}
        ):
            with self.assertRaises(ReportError) as caught:
                generate_report(self.runs_dir, self.output_dir)
        self.assertIn("[analysis]", str(caught.exception))
        # No output may be written when the extra is missing.
        self.assertFalse(self.output_dir.exists())

    def test_cli_report_missing_matplotlib_exits_2(self) -> None:
        from joulewise.cli import main

        out = io.StringIO()
        err = io.StringIO()
        with mock.patch.dict(
            sys.modules, {"matplotlib": None, "matplotlib.pyplot": None}
        ):
            with redirect_stdout(out), redirect_stderr(err):
                exit_code = main(
                    ["report", str(self.runs_dir), "--output", str(self.output_dir)]
                )
        self.assertEqual(exit_code, 2)
        self.assertEqual(out.getvalue(), "")
        self.assertTrue(err.getvalue().startswith("error: "), err.getvalue())
        self.assertIn("[analysis]", err.getvalue())


class BadRunsDirTests(unittest.TestCase):
    """A non-existent runs dir is a ReportError regardless of matplotlib."""

    def test_missing_runs_dir_raises_before_matplotlib(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        missing = Path(tmp.name) / "no-such-runs"
        with self.assertRaises(ReportError):
            generate_report(missing, Path(tmp.name) / "report")


class PublicReportSecurityTests(unittest.TestCase):
    def test_generate_report_escapes_malicious_metadata_and_summary_values(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        runs_dir = root / "runs"
        output_dir = root / "report"
        bundle = _build_bundle(runs_dir, "report-malicious")

        metadata_path = bundle / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        metadata["notes"] = "<script>alert(1)</script>"
        metadata_path.write_text(json.dumps(metadata, indent=2))
        summary_path = bundle / "summary_metrics.json"
        summary = json.loads(summary_path.read_text())
        summary["failure_message"] = "<b>bad</b>"
        summary_path.write_text(json.dumps(summary, indent=2))

        with mock.patch(
            "joulewise.report._require_matplotlib", return_value=object()
        ), mock.patch("joulewise.report._render_chart", return_value=False):
            generate_report(runs_dir, output_dir)

        page = (output_dir / "run" / "report-malicious.html").read_text()
        self.assertNotIn("<script>", page)
        self.assertNotIn("<b>bad</b>", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertIn("&lt;b&gt;bad&lt;/b&gt;", page)


class DiagnosticBrowserContractTests(unittest.TestCase):
    """WO-029 safeguards exercise the production ``generate_report`` path."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.runs_dir = self.root / "runs"
        self.output_dir = self.root / "report"

    def generate(self) -> Path:
        with mock.patch(
            "joulewise.report._require_matplotlib", return_value=object()
        ), mock.patch("joulewise.report._render_chart", return_value=False):
            return generate_report(self.runs_dir, self.output_dir)

    def test_token_metric_is_co_displayed_with_diagnostic_state_and_provenance(
        self,
    ) -> None:
        _build_bundle(self.runs_dir, "report-provenance")

        index_html = self.generate().read_text()

        self.assertIn("Diagnostic browser only.", index_html)
        self.assertIn("artifact consistency only", index_html)
        self.assertIn("strict validation", index_html)
        self.assertIn("pass", index_html)
        self.assertIn("request energy (J)", index_html)
        self.assertIn("tokenizer-scoped energy/token (J)", index_html)
        self.assertIn("measurement boundary", index_html)
        self.assertIn("joulewise.mock_tokenizer.v1", index_html)
        self.assertIn("total-token denominator source", index_html)
        self.assertIn("runtime_observed", index_html)
        # The mock single-request bundle has no recorded D-046 suite fields;
        # the diagnostic browser must say so rather than silently omit them.
        self.assertIn("<strong>prompt source:</strong> unknown", index_html)
        self.assertIn("<strong>BOS present:</strong> unknown", index_html)

        page = (self.output_dir / "run" / "report-provenance.html").read_text()
        self.assertIn("Summary metrics and provenance", page)
        self.assertIn("diagnostic.request_energy_j", page)
        self.assertIn("diagnostic.measurement_boundary", page)
        self.assertIn("tokenizer identifier", page)
        self.assertIn("total-token denominator source", page)
        self.assertIn("energy_token_j", page)

    def test_strict_invalid_and_incomplete_bundles_remain_visible(self) -> None:
        bundle = _build_bundle(self.runs_dir, "report-strict-invalid")
        summary_path = bundle / "summary_metrics.json"
        summary = json.loads(summary_path.read_text())
        summary["energy_request_j"] += 1.0
        summary_path.write_text(json.dumps(summary, indent=2))

        incomplete = self.runs_dir / "report-incomplete"
        incomplete.mkdir()
        (incomplete / "config.json").write_text(
            json.dumps({"schema_version": "0.1"})
        )

        index_html = self.generate().read_text()

        self.assertIn("report-strict-invalid", index_html)
        self.assertIn("report-incomplete", index_html)
        self.assertGreaterEqual(index_html.count("validation-fail"), 2)
        self.assertTrue(
            (self.output_dir / "run" / "report-strict-invalid.html").is_file()
        )
        self.assertFalse(
            (self.output_dir / "run" / "report-incomplete.html").exists()
        )
        invalid_page = (
            self.output_dir / "run" / "report-strict-invalid.html"
        ).read_text()
        self.assertIn("Strict-validation diagnostics", invalid_page)
        self.assertIn("does not match a fresh re-reduction", invalid_page)
        # WO-029 pinned disposition: the diagnostic browser must never imply
        # claim readiness or eligibility — for ANY bundle state (lead-added
        # negative assertion per the order's checker).
        for page in (invalid_page, *(
            path.read_text()
            for path in (self.output_dir / "run").glob("report-*.html")
        )):
            lowered = page.lower()
            for banned in ("claim-ready", "claim ready", "claim-eligible",
                           "claim eligible", "eligible for claims",
                           "readiness"):
                self.assertNotIn(banned, lowered)

    def test_absent_request_energy_is_explicitly_unknown_beside_token_metrics(
        self,
    ) -> None:
        bundle = _build_bundle(self.runs_dir, "report-unknown-request-energy")
        summary_path = bundle / "summary_metrics.json"
        summary = json.loads(summary_path.read_text())
        for key in (
            "energy_request_j",
            "energy_token_j",
            "energy_output_token_j",
            "idle_subtracted_energy_j",
            "idle_baseline",
        ):
            summary[key] = None
        summary["window_evidence_precheck"]["idle_subtracted_request"] = {
            "energy_evidence": "absent",
            "eligible": False,
            "reasons": ["idle_baseline_unrecorded"],
        }
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

        index_html = self.generate().read_text()
        self.assertIn("<td>unknown</td><td>unknown</td>", index_html)
        self.assertNotIn("<td>-</td><td>unknown</td>", index_html)

        page = (
            self.output_dir / "run" / "report-unknown-request-energy.html"
        ).read_text()
        self.assertIn(
            "<code>diagnostic.request_energy_j</code></td><td>unknown</td>",
            page,
        )
        self.assertIn("<code>energy_request_j</code></td><td>unknown</td>", page)
        self.assertIn("<code>energy_token_j</code></td><td>unknown</td>", page)


# ---------------------------------------------------------------------------
# Chart-producing rendering (gated on matplotlib)


@unittest.skipUnless(HAS_MPL, "matplotlib ([analysis] extra) not installed")
class RenderWithMatplotlibTests(ReportTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.index_path = generate_report(self.runs_dir, self.output_dir)
        self.index_html = self.index_path.read_text()

    def test_index_exists_and_lists_both_runs_and_statuses(self) -> None:
        self.assertTrue(self.index_path.is_file())
        self.assertEqual(self.index_path, self.output_dir / "index.html")
        self.assertIn("report-success", self.index_html)
        self.assertIn("report-unsupported", self.index_html)
        self.assertIn("succeeded", self.index_html)
        self.assertIn("unsupported", self.index_html)

    def test_per_run_pages_exist(self) -> None:
        success_page = self.output_dir / "run" / "report-success.html"
        unsupported_page = self.output_dir / "run" / "report-unsupported.html"
        self.assertTrue(success_page.is_file())
        self.assertTrue(unsupported_page.is_file())

    def test_succeeded_run_has_png_chart(self) -> None:
        png = self.output_dir / "run" / "report-success.png"
        self.assertTrue(png.is_file())
        self.assertGreater(png.stat().st_size, 0)
        page = (self.output_dir / "run" / "report-success.html").read_text()
        self.assertIn("report-success.png", page)

    def test_unsupported_page_has_failure_box_with_reason(self) -> None:
        page = (self.output_dir / "run" / "report-unsupported.html").read_text()
        self.assertIn("failure-box", page)
        self.assertIn("did_not_fit", page)
        # An unsupported run wrote no power trace, so the chart is omitted with
        # a note rather than a broken <img>.
        self.assertNotIn("report-unsupported.png", page)
        self.assertFalse((self.output_dir / "run" / "report-unsupported.png").exists())

    def test_incomplete_dir_listed_without_detail_page(self) -> None:
        # A bare directory with only config.json is an incomplete bundle (the
        # harness died, D-011): listed as incomplete, no detail page.
        incomplete = self.runs_dir / "report-incomplete"
        incomplete.mkdir()
        (incomplete / "config.json").write_text(json.dumps({"schema_version": "0.1"}))

        index_path = generate_report(self.runs_dir, self.output_dir)
        index_html = index_path.read_text()
        self.assertIn("report-incomplete", index_html)
        self.assertIn("incomplete", index_html)
        self.assertFalse((self.output_dir / "run" / "report-incomplete.html").exists())

    def test_experiments_dir_excluded_from_discovery(self) -> None:
        # runs/experiments holds manifests, not bundles; it is never listed.
        experiments = self.runs_dir / "experiments"
        experiments.mkdir()
        (experiments / "exp.json").write_text(json.dumps({"experiment_id": "exp"}))
        index_html = generate_report(self.runs_dir, self.output_dir).read_text()
        self.assertNotIn(">experiments<", index_html)
        self.assertFalse((self.output_dir / "run" / "experiments.html").exists())

    def test_index_is_self_contained_no_javascript(self) -> None:
        self.assertNotIn("<script", self.index_html.lower())
        self.assertIn("<style", self.index_html.lower())

    def test_manifest_mismatch_omits_chart_instead_of_fallback_sum(self) -> None:
        # 2N.7 (D-025): the report reads the same summed curve the reducer
        # integrated. A bundle whose manifest matches no trace rail must NOT
        # fall back to summing all rails - the chart is omitted with a note.
        bundle = self.runs_dir / "report-success"
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["device"]["rail_manifest"] = ["no-such-rail"]
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))

        generate_report(self.runs_dir, self.output_dir)
        page = (self.output_dir / "run" / "report-success.html").read_text()
        self.assertIn("No power-trace chart", page)
        self.assertNotIn('src="report-success.png"', page)


@unittest.skipUnless(HAS_MPL, "matplotlib ([analysis] extra) not installed")
class CliReportSuccessTests(ReportTestCase):
    def test_cli_report_prints_index_and_run_count(self) -> None:
        from joulewise.cli import main

        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            exit_code = main(
                ["report", str(self.runs_dir), "--output", str(self.output_dir)]
            )
        self.assertEqual(exit_code, 0, err.getvalue())
        # matplotlib may print an unrelated one-time "building the font cache"
        # notice to stderr on first import; the verb itself must not emit an
        # "error:" line on success.
        self.assertNotIn("error:", err.getvalue())
        line = out.getvalue().strip()
        self.assertTrue(line.startswith("report: "), line)
        self.assertIn(str(self.output_dir / "index.html"), line)
        self.assertIn("runs=2", line)


if __name__ == "__main__":
    unittest.main()
