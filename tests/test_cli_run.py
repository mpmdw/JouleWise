"""Tests for the ``run`` and ``validate-bundle`` CLI verbs (Slice 2E).

Every test drives the CLI in-process via ``cli.main(argv)``, writes bundles
into a per-test temp directory, and uses a fresh ``run_id`` per test so the
all-mock vertical slice never collides on the deterministic config-supplied
run id. The mock path binds a ``FakeClock`` at the CLI boundary (D-020), so
these runs are instant and deterministic.
"""

from __future__ import annotations

import io
import json
import math
import re
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any
from unittest.mock import patch

from joulewise.adapters.powermetrics import (
    RAW_IDLE_NAME,
    RAW_SAMPLES_NAME,
    parse_powermetrics_records,
)
from joulewise.clock import FakeClock
from joulewise.cli import _STRICT_LEGACY_BUNDLE_IDENTITIES, main, validate_bundle
from joulewise.bundle_read import Window
from joulewise.controller import run_benchmark
from joulewise.reduce import reduce_bundle
from joulewise.schemas import BenchmarkConfig, RunStatus

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_local.json"
EXAMPLE_SUITE_CONFIG_PATH = (
    REPO_ROOT / "configs" / "examples" / "mock_suite_local.json"
)
POWERMETRICS_FIXTURE = (
    REPO_ROOT / "tests" / "fixtures" / "powermetrics_sample.plist"
)

#: The single machine-greppable success line shape the contract pins.
SUCCEEDED_LINE = re.compile(r"^bundle: (\S+) status=succeeded$")
LEGACY_ALLOWLIST_PAIR = (
    "example-mac-mlx-local__r1",
    "ee80585a2f6cee6aa7e12eb83c318fd88a934be02d5fa2fb2eb7509630640fd5",
)


def _run(argv: list[str]) -> tuple[int, str, str]:
    """Invoke ``cli.main(argv)`` capturing exit code, stdout, stderr."""
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        exit_code = main(argv)
    return exit_code, out.getvalue(), err.getvalue()


def _completed(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=b"")


class CliRunTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.runs_dir = self.tmp / "runs"

    def write_config(self, run_id: str, **overrides: Any) -> Path:
        """Write a temp config derived from the example with ``run_id`` set.

        ``overrides`` are shallow-merged into the top-level mapping; nested
        edits (model name, hardware notes) are applied by the helpers below.
        """
        data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        data["run_id"] = run_id
        for key, value in overrides.items():
            data[key] = value
        path = self.tmp / f"{run_id}.json"
        path.write_text(json.dumps(data))
        return path

    def write_suite_config(self, run_id: str) -> Path:
        data = json.loads(EXAMPLE_SUITE_CONFIG_PATH.read_text())
        data["run_id"] = run_id
        data["workload_profile"]["suite_manifest_ref"] = str(
            REPO_ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json"
        )
        path = self.tmp / f"{run_id}.json"
        path.write_text(json.dumps(data))
        return path

    def write_unsupported_config(self, run_id: str) -> Path:
        data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        data["run_id"] = run_id
        data["model"]["name"] = "mock-unsupported"
        path = self.tmp / f"{run_id}.json"
        path.write_text(json.dumps(data))
        return path

    def write_denied_config(self, run_id: str) -> Path:
        data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        data["run_id"] = run_id
        data["hardware_target"]["notes"] = "telemetry-denied"
        path = self.tmp / f"{run_id}.json"
        path.write_text(json.dumps(data))
        return path

    def run_verb(self, config_path: Path) -> tuple[int, str, str]:
        return _run(["run", str(config_path), "--runs-dir", str(self.runs_dir)])

    def bundle_path_from_line(self, line: str) -> Path:
        """Parse the bundle path the contract way: from the printed line."""
        stripped = line.strip()
        self.assertTrue(stripped.startswith("bundle: "), stripped)
        rest = stripped[len("bundle: ") :]
        return Path(rest.split(" ", 1)[0])


class RunVerbTests(CliRunTestCase):
    def test_mock_e2e_succeeds_with_greppable_line(self) -> None:
        config_path = self.write_config("cli-run-success")
        exit_code, stdout, stderr = self.run_verb(config_path)
        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(stderr, "")
        line = stdout.strip()
        self.assertRegex(line, SUCCEEDED_LINE)
        bundle = self.bundle_path_from_line(line)
        self.assertTrue(bundle.is_dir())
        self.assertTrue((bundle / "summary_metrics.json").is_file())

    def test_succeeded_bundle_validates(self) -> None:
        config_path = self.write_config("cli-run-validate")
        exit_code, stdout, _ = self.run_verb(config_path)
        self.assertEqual(exit_code, 0)
        bundle = self.bundle_path_from_line(stdout)
        code, out, _ = _run(["validate-bundle", str(bundle)])
        self.assertEqual(code, 0, out)
        self.assertIn(f"valid bundle: {bundle}", out)

    def test_default_runs_dir_value(self) -> None:
        # The default --runs-dir is "runs/" (we still pass an explicit one in
        # other tests to keep bundles inside the temp dir).
        config_path = self.write_config("cli-run-default-check")
        # Run with explicit temp runs-dir so we never write into the repo.
        exit_code, stdout, _ = self.run_verb(config_path)
        self.assertEqual(exit_code, 0)
        bundle = self.bundle_path_from_line(stdout)
        self.assertEqual(bundle.parent, self.runs_dir)

    def test_unsupported_run_exits_3_and_bundle_validates(self) -> None:
        config_path = self.write_unsupported_config("cli-run-unsupported")
        exit_code, stdout, stderr = self.run_verb(config_path)
        self.assertEqual(exit_code, 3, stderr)
        line = stdout.strip()
        self.assertTrue(
            line.endswith(" reason=did_not_fit"),
            line,
        )
        self.assertIn("status=unsupported", line)
        bundle = self.bundle_path_from_line(line)
        self.assertEqual(validate_bundle(bundle), [])

    def test_denied_run_exits_3_failed_and_bundle_validates(self) -> None:
        config_path = self.write_denied_config("cli-run-denied")
        exit_code, stdout, stderr = self.run_verb(config_path)
        self.assertEqual(exit_code, 3, stderr)
        line = stdout.strip()
        self.assertIn("status=failed", line)
        self.assertTrue(line.endswith(" reason=permission_denied"), line)
        bundle = self.bundle_path_from_line(line)
        # No power trace is required for a failed run; it must still validate.
        self.assertFalse((bundle / "power_trace.csv").exists())
        self.assertEqual(validate_bundle(bundle), [])

    def test_invalid_json_config_exits_2_no_bundle(self) -> None:
        bad = self.tmp / "broken.json"
        bad.write_text("{ this is not valid json ")
        exit_code, stdout, stderr = _run(
            ["run", str(bad), "--runs-dir", str(self.runs_dir)]
        )
        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr.startswith("error: "), stderr)
        self.assertFalse(self.runs_dir.exists())

    def test_schema_invalid_config_exits_2_no_bundle(self) -> None:
        # Valid JSON, but fails schema validation: an ssh transport target with
        # no host. run_benchmark's config.validate() raises SchemaError, which
        # the CLI maps to exit 2 with no bundle written.
        data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        data["run_id"] = "cli-run-schema-invalid"
        data["hardware_target"]["transport"] = "ssh"
        data["hardware_target"].pop("host", None)
        path = self.tmp / "schema-invalid.json"
        path.write_text(json.dumps(data))

        exit_code, stdout, stderr = _run(
            ["run", str(path), "--runs-dir", str(self.runs_dir)]
        )
        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr.startswith("error: "), stderr)
        self.assertIn("host is required", stderr)
        self.assertFalse(self.runs_dir.exists())

    def test_run_id_collision_exits_2(self) -> None:
        config_path = self.write_config("cli-run-collision")
        first_code, _, _ = self.run_verb(config_path)
        self.assertEqual(first_code, 0)
        second_code, stdout, stderr = self.run_verb(config_path)
        self.assertEqual(second_code, 2)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr.startswith("error: "), stderr)
        self.assertIn("already exists", stderr)


class ValidateBundleTests(CliRunTestCase):
    def make_bundle(self, run_id: str) -> Path:
        config_path = self.write_config(run_id)
        exit_code, stdout, _ = self.run_verb(config_path)
        self.assertEqual(exit_code, 0)
        return self.bundle_path_from_line(stdout)

    def assert_invalid(self, bundle: Path) -> str:
        code, out, _ = _run(["validate-bundle", str(bundle)])
        self.assertEqual(code, 2, out)
        self.assertIn("invalid:", out)
        return out

    def test_nonexistent_path_invalid(self) -> None:
        self.assert_invalid(self.tmp / "does-not-exist")

    def test_non_directory_path_invalid(self) -> None:
        target = self.tmp / "a-file"
        target.write_text("not a bundle")
        self.assert_invalid(target)

    def test_summary_deleted(self) -> None:
        bundle = self.make_bundle("vb-summary-deleted")
        (bundle / "summary_metrics.json").unlink()
        out = self.assert_invalid(bundle)
        self.assertIn("summary_metrics.json", out)

    def test_missing_events(self) -> None:
        bundle = self.make_bundle("vb-missing-events")
        (bundle / "events.jsonl").unlink()
        out = self.assert_invalid(bundle)
        self.assertIn("events.jsonl", out)

    def test_last_event_not_run_finalized(self) -> None:
        bundle = self.make_bundle("vb-last-event")
        events_path = bundle / "events.jsonl"
        lines = [
            line for line in events_path.read_text().splitlines() if line.strip()
        ]
        records = [json.loads(line) for line in lines]
        # Drop the trailing run_finalized event so the last is something else.
        self.assertEqual(records[-1]["event_type"], "run_finalized")
        kept = records[:-1]
        events_path.write_text("".join(json.dumps(rec) + "\n" for rec in kept))
        out = self.assert_invalid(bundle)
        self.assertIn("run_finalized", out)

    def test_bad_trace_header(self) -> None:
        bundle = self.make_bundle("vb-bad-header")
        trace_path = bundle / "power_trace.csv"
        body = trace_path.read_text().splitlines()
        body[0] = "t,p,s,r"
        trace_path.write_text("\n".join(body) + "\n")
        out = self.assert_invalid(bundle)
        self.assertIn("power_trace.csv header", out)

    def test_corrupt_summary_json(self) -> None:
        bundle = self.make_bundle("vb-corrupt-summary")
        (bundle / "summary_metrics.json").write_text("{ not json")
        out = self.assert_invalid(bundle)
        self.assertIn("summary_metrics.json", out)

    # --- config/metadata JSON-parse + re-validation (Finding 5) ---

    def test_config_not_json(self) -> None:
        bundle = self.make_bundle("vb-config-not-json")
        (bundle / "config.json").write_text("{ not json")
        problems = validate_bundle(bundle)
        self.assertTrue(
            any("config.json is not valid JSON" in p for p in problems), problems
        )
        self.assert_invalid(bundle)

    def test_metadata_not_json(self) -> None:
        bundle = self.make_bundle("vb-metadata-not-json")
        (bundle / "metadata.json").write_text("{ not json")
        problems = validate_bundle(bundle)
        self.assertTrue(
            any("metadata.json is not valid JSON" in p for p in problems), problems
        )
        self.assert_invalid(bundle)

    def test_config_valid_json_but_schema_invalid_does_not_revalidate(self) -> None:
        bundle = self.make_bundle("vb-config-revalidate")
        config = json.loads((bundle / "config.json").read_text())
        config["run_id"] = 123  # valid JSON, but from_mapping rejects a non-str
        (bundle / "config.json").write_text(json.dumps(config))
        problems = validate_bundle(bundle)
        self.assertTrue(
            any("config.json does not re-validate" in p for p in problems), problems
        )
        self.assert_invalid(bundle)

    # --- events.jsonl record-level checks (Finding 6) ---

    def _events_lines(self, bundle: Path) -> list[str]:
        return [
            line
            for line in (bundle / "events.jsonl").read_text().splitlines()
            if line.strip()
        ]

    def test_events_line_not_json(self) -> None:
        bundle = self.make_bundle("vb-events-not-json")
        lines = self._events_lines(bundle)
        lines[0] = "{ not json"
        (bundle / "events.jsonl").write_text("\n".join(lines) + "\n")
        problems = validate_bundle(bundle)
        self.assertTrue(any("is not valid JSON" in p for p in problems), problems)
        self.assert_invalid(bundle)

    def test_events_record_wrong_key_set(self) -> None:
        bundle = self.make_bundle("vb-events-keys")
        lines = self._events_lines(bundle)
        record = json.loads(lines[0])
        record.pop("metadata")  # key set != the five required keys
        lines[0] = json.dumps(record)
        (bundle / "events.jsonl").write_text("\n".join(lines) + "\n")
        problems = validate_bundle(bundle)
        self.assertTrue(any("keys are" in p for p in problems), problems)
        self.assert_invalid(bundle)

    def test_events_decreasing_timestamps(self) -> None:
        bundle = self.make_bundle("vb-events-timestamps")
        records = [json.loads(line) for line in self._events_lines(bundle)]
        # Rewrite timestamps strictly decreasing while keeping the last event a
        # run_finalized record, isolating the non-decreasing check.
        n = len(records)
        for index, record in enumerate(records):
            record["timestamp_s"] = float(n - index)
        (bundle / "events.jsonl").write_text(
            "".join(json.dumps(rec) + "\n" for rec in records)
        )
        problems = validate_bundle(bundle)
        self.assertIn(
            "events.jsonl timestamps are not non-decreasing", problems
        )
        self.assert_invalid(bundle)

    def test_events_nonnumeric_timestamp_is_problem_not_crash(self) -> None:
        # 2026-07-06 status review P1: a nonnumeric timestamp must produce an
        # invalid: problem, never a raw TypeError from the ordering check.
        bundle = self.make_bundle("vb-events-bad-ts")
        lines = self._events_lines(bundle)
        record = json.loads(lines[0])
        record["timestamp_s"] = "not-a-number"
        lines[0] = json.dumps(record)
        (bundle / "events.jsonl").write_text("\n".join(lines) + "\n")
        problems = validate_bundle(bundle)
        self.assertTrue(
            any("timestamp_s is not a finite number" in p for p in problems),
            problems,
        )
        self.assert_invalid(bundle)

    def test_events_mixed_type_timestamps_no_type_error(self) -> None:
        bundle = self.make_bundle("vb-events-mixed-ts")
        records = [json.loads(line) for line in self._events_lines(bundle)]
        records[1]["timestamp_s"] = True  # bool: JSON-valid, not a time
        (bundle / "events.jsonl").write_text(
            "".join(json.dumps(rec) + "\n" for rec in records)
        )
        problems = validate_bundle(bundle)  # must not raise
        self.assertTrue(
            any("timestamp_s is not a finite number" in p for p in problems),
            problems,
        )

    def test_validate_bundle_helper_is_importable_and_pure(self) -> None:
        bundle = self.make_bundle("vb-helper")
        problems = validate_bundle(bundle)
        self.assertEqual(problems, [])
        # Deleting an artifact yields a specific problem string, not an exception.
        (bundle / "metadata.json").unlink()
        problems = validate_bundle(bundle)
        self.assertTrue(any("metadata.json" in problem for problem in problems))


class StrictValidateTests(CliRunTestCase):
    """D-030 (2026-07-06 status review P2): --strict catches succeeded
    bundles whose summary no longer follows from the raw evidence."""

    def make_bundle(self, run_id: str) -> Path:
        exit_code, out, _ = self.run_verb(self.write_config(run_id))
        self.assertEqual(exit_code, 0)
        return self.bundle_path_from_line(out.splitlines()[0])

    def mark_allowlisted_legacy_identity(
        self, bundle: Path, identity: tuple[str, str] = LEGACY_ALLOWLIST_PAIR
    ) -> None:
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["run_id"], metadata["config_sha256"] = identity
        (bundle / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n"
        )

    def make_synchronized_idle_metadata_mismatch_bundle(
        self, run_id: str
    ) -> Path:
        """Build a stored summary synchronized to mismatching idle metadata."""
        bundle = self.make_bundle(run_id)
        raw = POWERMETRICS_FIXTURE.read_bytes()
        (bundle / "raw" / RAW_IDLE_NAME).write_bytes(raw)
        records = parse_powermetrics_records(raw)
        powers_w = [record.combined_power_w for record in records]
        mean_w = math.fsum(powers_w) / len(powers_w)
        stddev_w = math.sqrt(
            math.fsum((power_w - mean_w) ** 2 for power_w in powers_w)
            / (len(powers_w) - 1)
        )
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["idle_baseline"].update(
            {
                "power_w_mean": mean_w,
                "power_w_stddev": stddev_w,
                "duration_s": math.fsum(
                    record.elapsed_ns / 1_000_000_000.0 for record in records
                ),
                # Deliberately disagree with the five-record raw artifact.
                "sample_count": len(records) + 1,
                "telemetry_backend": "powermetrics",
            }
        )
        (bundle / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n"
        )
        # Synchronize every stored governed field to the mismatching metadata;
        # strict must still reject based on the fresh raw derivation itself.
        summary = reduce_bundle(bundle).to_dict()
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        return bundle

    def test_fresh_succeeded_bundle_passes_strict(self) -> None:
        bundle = self.make_bundle("strict-clean")
        self.assertEqual(validate_bundle(bundle, strict=True), [])
        exit_code, out, _ = _run(["validate-bundle", "--strict", str(bundle)])
        self.assertEqual(exit_code, 0)
        self.assertIn("valid bundle:", out)

    def test_negative_succeeded_measured_window_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-negative-window")
        # A negative interpreted window cannot be serialized by the normal
        # ordered-event writer, so pin strict's independent guard at its reader
        # boundary while the reducer fixture covers the on-disk failure path.
        with patch(
            "joulewise.cli.BundleReader.measured_window",
            return_value=Window(start_s=2.0, end_s=1.0),
        ):
            problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any("measured window duration must be > 0 s" in p for p in problems),
            problems,
        )

    def test_legacy_dispatch_tolerates_governed_additive_absence(self) -> None:
        bundle = self.make_bundle("strict-p2029-additive-absent")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary.pop("summary_provenance")
        for key in (
            "energy_uncertainty_status",
            "idle_mean_uncertainty",
            "energy_variance_terms_j2",
            "energy_bound_terms_j",
            "window_evidence_precheck",
        ):
            summary.pop(key)
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        self.mark_allowlisted_legacy_identity(bundle)

        with patch("joulewise.bundle_read._check_config_sha256", return_value=[]):
            self.assertEqual(validate_bundle(bundle, strict=True), [])

    def test_reducer_0_4_1_dispatch_requires_exact_summary(self) -> None:
        bundle = self.make_bundle("strict-v041-exact")
        self.assertEqual(validate_bundle(bundle, strict=True), [])

    def test_current_era_reducer_0_4_0_requires_re_reduction(self) -> None:
        bundle = self.make_bundle("strict-v040-rejected")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["summary_provenance"]["reducer_version"] = "0.4.0"
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )

        self.assertIn(
            "strict: unsupported reducer version; re-reduction required",
            validate_bundle(bundle, strict=True),
        )

    def test_current_era_reducer_0_3_0_requires_re_reduction(self) -> None:
        bundle = self.make_bundle("strict-v030-rejected")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["summary_provenance"]["reducer_version"] = "0.3.0"
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )

        self.assertIn(
            "strict: unsupported reducer version; re-reduction required",
            validate_bundle(bundle, strict=True),
        )

    def test_current_era_reducer_0_3_1_requires_re_reduction(self) -> None:
        bundle = self.make_bundle("strict-v031-rejected")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["summary_provenance"]["reducer_version"] = "0.3.1"
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )

        self.assertIn(
            "strict: unsupported reducer version; re-reduction required",
            validate_bundle(bundle, strict=True),
        )

    def test_reducer_0_4_1_old_field_only_fails_exact_comparison(self) -> None:
        bundle = self.make_bundle("strict-v041-old-field")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["claim_eligibility"] = summary.pop("window_evidence_precheck")
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )

        problems = validate_bundle(bundle, strict=True)

        self.assertTrue(
            any("claim_eligibility" in problem for problem in problems),
            problems,
        )
        self.assertTrue(
            any("window_evidence_precheck" in problem for problem in problems),
            problems,
        )

    def test_reducer_0_2_x_dispatch_requires_re_reduction(self) -> None:
        bundle = self.make_bundle("strict-v02-rejected")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["summary_provenance"]["reducer_version"] = "0.2.9"
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        self.assertIn(
            "strict: unsupported reducer version; re-reduction required",
            validate_bundle(bundle, strict=True),
        )

    def test_exact_reducer_0_2_0_is_rejected(self) -> None:
        bundle = self.make_bundle("strict-v020-rejected")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["summary_provenance"]["reducer_version"] = "0.2.0"
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        self.assertIn(
            "strict: unsupported reducer version; re-reduction required",
            validate_bundle(bundle, strict=True),
        )

    def test_missing_null_and_non_string_reducer_versions_are_rejected(self) -> None:
        for value in ("missing", None, ["0.4.0"]):
            with self.subTest(value=value):
                bundle = self.make_bundle(f"strict-bad-version-{str(value)}")
                summary = json.loads((bundle / "summary_metrics.json").read_text())
                if value == "missing":
                    del summary["summary_provenance"]["reducer_version"]
                else:
                    summary["summary_provenance"]["reducer_version"] = value
                (bundle / "summary_metrics.json").write_text(
                    json.dumps(summary, indent=2, sort_keys=True) + "\n"
                )
                self.assertIn(
                    "strict: unsupported reducer version; re-reduction required",
                    validate_bundle(bundle, strict=True),
                )

    def test_unknown_reducer_version_dispatch_requires_re_reduction(self) -> None:
        bundle = self.make_bundle("strict-vunknown-rejected")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["summary_provenance"]["reducer_version"] = "future"
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        self.assertIn(
            "strict: unsupported reducer version; re-reduction required",
            validate_bundle(bundle, strict=True),
        )

    def test_claimed_0_4_1_missing_governed_field_fails_exact_dispatch(self) -> None:
        bundle = self.make_bundle("strict-v041-governed-absence")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        del summary["window_evidence_precheck"]["gross_request"]
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )

        problems = validate_bundle(bundle, strict=True)

        self.assertTrue(
            any(
                "window_evidence_precheck.gross_request" in problem
                for problem in problems
            ),
            problems,
        )

    def test_mock_suite_bundle_passes_strict(self) -> None:
        exit_code, stdout, stderr = self.run_verb(
            self.write_suite_config("strict-suite-clean")
        )
        self.assertEqual(exit_code, 0, stderr)
        bundle = self.bundle_path_from_line(stdout)
        self.assertEqual(validate_bundle(bundle, strict=True), [])

        exit_code, out, err = _run(["validate-bundle", "--strict", str(bundle)])
        self.assertEqual(exit_code, 0, err)
        self.assertEqual(out.strip(), f"valid bundle: {bundle}")

    def test_suite_bundle_wrong_prompt_hash_domain_fails_strict(self) -> None:
        # A tampered SUITE bundle domain must fail strict (the suite branch of
        # the domain check must not silently accept arbitrary strings).
        exit_code, stdout, stderr = self.run_verb(
            self.write_suite_config("strict-suite-tampered")
        )
        self.assertEqual(exit_code, 0, stderr)
        bundle = self.bundle_path_from_line(stdout)
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["workload_provenance"]["prompt"]["token_hash_domain"] = (
            "joulewise.prompt_token_ids.v1"  # single-prompt domain: wrong here
        )
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))
        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any(
                "token_hash_domain" in p and "suite_prompt_token_ids" in p
                for p in problems
            ),
            problems,
        )

    def test_suite_bundle_prompt_rollup_is_recomputed_from_suite_items(self) -> None:
        exit_code, stdout, stderr = self.run_verb(
            self.write_suite_config("strict-suite-rollup-tampered")
        )
        self.assertEqual(exit_code, 0, stderr)
        bundle = self.bundle_path_from_line(stdout)
        suite_items_path = bundle / "outputs" / "suite_items.jsonl"
        records = [
            json.loads(line)
            for line in suite_items_path.read_text().splitlines()
            if line.strip()
        ]
        records[0]["prompt"]["token_ids_sha256"] = "0" * 64
        records[0]["prompt_tokens"] += 1
        suite_items_path.write_text(
            "".join(json.dumps(record, sort_keys=True) + "\n" for record in records)
        )

        problems = validate_bundle(bundle, strict=True)

        digest_problem = next(
            (
                p
                for p in problems
                if "prompt.token_ids_sha256 does not match outputs/suite_items.jsonl rollup" in p
            ),
            None,
        )
        count_problem = next(
            (
                p
                for p in problems
                if "prompt.realized_token_count does not match outputs/suite_items.jsonl rollup" in p
            ),
            None,
        )
        self.assertIsNotNone(digest_problem, problems)
        self.assertIn("metadata has", digest_problem)
        self.assertIn("recomputed has", digest_problem)
        self.assertIsNotNone(count_problem, problems)
        self.assertIn("metadata has", count_problem)
        self.assertIn("recomputed has", count_problem)

    def test_emptied_rail_manifest_fails_strict_only(self) -> None:
        # Review repro (a): default validation blesses it; strict must not.
        bundle = self.make_bundle("strict-manifest")
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["device"]["rail_manifest"] = []
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))
        self.assertEqual(validate_bundle(bundle), [])
        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any("reducer-consumable" in p for p in problems), problems
        )
        self.assertTrue(
            any("does not match a fresh re-reduction" in p for p in problems),
            problems,
        )

    def test_tampered_summary_metric_fails_strict_only(self) -> None:
        # Review repro (b): a nonsense energy_request_j must not be blessed.
        bundle = self.make_bundle("strict-tampered")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["energy_request_j"] = 999999.0
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        self.assertEqual(validate_bundle(bundle), [])
        problems = validate_bundle(bundle, strict=True)
        self.assertEqual(len(problems), 1)
        self.assertIn("does not match a fresh re-reduction", problems[0])
        self.assertIn("energy_request_j", problems[0])
        exit_code, out, _ = _run(["validate-bundle", "--strict", str(bundle)])
        self.assertEqual(exit_code, 2)
        self.assertIn("invalid: strict:", out)

    def test_legacy_summary_missing_additive_null_keys_passes_strict(self) -> None:
        bundle = self.make_bundle("strict-legacy-null-additive")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        del summary["summary_provenance"]
        del summary["idle_baseline"]["gpu_freq_hz_mean"]
        del summary["idle_baseline"]["gpu_idle_ratio_mean"]
        del summary["idle_baseline"]["gpu_idle_ratio_min"]
        del summary["idle_baseline"]["idle_window_suspect"]
        del summary["measurement_quality"]["idle_window_suspect"]
        del summary["measurement_quality"]["remote_cleanup_failed"]
        del summary["measurement_quality"]["runtime_cleanup_ok"]
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        self.mark_allowlisted_legacy_identity(bundle)
        with patch("joulewise.bundle_read._check_config_sha256", return_value=[]):
            self.assertEqual(validate_bundle(bundle, strict=True), [])

    def test_new_summary_missing_summary_provenance_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-new-missing-summary-provenance")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        del summary["summary_provenance"]
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )

        problems = validate_bundle(bundle, strict=True)

        self.assertTrue(
            any("summary_metrics.summary_provenance" in p for p in problems),
            problems,
        )

    def test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics(self) -> None:
        self.assertEqual(len(_STRICT_LEGACY_BUNDLE_IDENTITIES), 6)
        for index, identity in enumerate(sorted(_STRICT_LEGACY_BUNDLE_IDENTITIES)):
            with self.subTest(identity=identity):
                bundle = self.make_bundle(f"strict-allowlisted-legacy-{index}")
                summary = json.loads((bundle / "summary_metrics.json").read_text())
                summary.pop("summary_provenance")
                summary.pop("idle_mean_uncertainty")
                (bundle / "summary_metrics.json").write_text(
                    json.dumps(summary, indent=2, sort_keys=True) + "\n"
                )
                metadata = json.loads((bundle / "metadata.json").read_text())
                metadata.pop("workload_provenance")
                (bundle / "metadata.json").write_text(
                    json.dumps(metadata, indent=2, sort_keys=True) + "\n"
                )
                self.mark_allowlisted_legacy_identity(bundle, identity)

                with patch(
                    "joulewise.bundle_read._check_config_sha256", return_value=[]
                ):
                    self.assertEqual(validate_bundle(bundle, strict=True), [])

    def test_allowlisted_legacy_fresh_idle_metadata_mismatch_fails_strict(self) -> None:
        bundle = self.make_synchronized_idle_metadata_mismatch_bundle(
            "strict-legacy-fresh-idle-mismatch"
        )
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        self.assertEqual(
            summary["idle_mean_uncertainty"]["reason_codes"],
            ["idle_trace_span_below_three_bandwidths", "idle_metadata_mismatch"],
        )
        summary.pop("summary_provenance")
        summary.pop("idle_mean_uncertainty")
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata.pop("workload_provenance")
        (bundle / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n"
        )
        self.mark_allowlisted_legacy_identity(bundle)

        with patch("joulewise.bundle_read._check_config_sha256", return_value=[]):
            problems = validate_bundle(bundle, strict=True)

        self.assertEqual(
            problems,
            [
                "strict: raw idle trace does not match metadata.idle_baseline "
                "(idle_metadata_mismatch)"
            ],
        )

    def test_current_idle_metadata_mismatch_diagnostic_is_deduplicated(self) -> None:
        bundle = self.make_synchronized_idle_metadata_mismatch_bundle(
            "strict-current-fresh-idle-mismatch"
        )

        problems = validate_bundle(bundle, strict=True)

        self.assertEqual(
            problems,
            [
                "strict: raw idle trace does not match metadata.idle_baseline "
                "(idle_metadata_mismatch)"
            ],
        )

    def test_idle_metadata_mismatch_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-idle-metadata-mismatch")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["idle_mean_uncertainty"]["reason_codes"] = [
            "idle_metadata_mismatch"
        ]
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any("idle_metadata_mismatch" in problem for problem in problems),
            problems,
        )

    def test_allowlisted_legacy_present_null_provenance_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-legacy-present-null-provenance")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["summary_provenance"] = None
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        self.mark_allowlisted_legacy_identity(bundle)
        with patch("joulewise.bundle_read._check_config_sha256", return_value=[]):
            problems = validate_bundle(bundle, strict=True)
        self.assertTrue(any("missing or not an object" in p for p in problems), problems)

    def test_allowlisted_legacy_present_non_object_provenance_fails_strict(self) -> None:
        for value in ("legacy", ["legacy"]):
            with self.subTest(value=value):
                bundle = self.make_bundle(f"strict-legacy-present-{type(value).__name__}")
                summary = json.loads((bundle / "summary_metrics.json").read_text())
                summary["summary_provenance"] = value
                (bundle / "summary_metrics.json").write_text(
                    json.dumps(summary, indent=2, sort_keys=True) + "\n"
                )
                self.mark_allowlisted_legacy_identity(bundle)
                with patch("joulewise.bundle_read._check_config_sha256", return_value=[]):
                    problems = validate_bundle(bundle, strict=True)
                self.assertTrue(any("missing or not an object" in p for p in problems), problems)

    def test_allowlisted_legacy_recorded_value_mutations_fail_strict(self) -> None:
        mutations = (
            ("energy_token_j", lambda s: s.__setitem__("energy_token_j", 999.0)),
            (
                "measurement_quality.token_count_source",
                lambda s: s["measurement_quality"].__setitem__(
                    "token_count_source", "edited"
                ),
            ),
            ("gross_energy_j", lambda s: s.__setitem__("gross_energy_j", 999.0)),
        )
        for label, mutate in mutations:
            with self.subTest(field=label):
                bundle = self.make_bundle(f"strict-legacy-mutation-{label}")
                summary = json.loads((bundle / "summary_metrics.json").read_text())
                del summary["summary_provenance"]
                mutate(summary)
                (bundle / "summary_metrics.json").write_text(
                    json.dumps(summary, indent=2, sort_keys=True) + "\n"
                )
                self.mark_allowlisted_legacy_identity(bundle)
                with patch("joulewise.bundle_read._check_config_sha256", return_value=[]):
                    problems = validate_bundle(bundle, strict=True)
                self.assertTrue(any(label in p for p in problems), problems)

    def test_current_bundle_spoofed_as_legacy_with_absent_provenance_passes(self) -> None:
        """Pin the adjudicated identity-classification boundary (FIX-B4)."""
        bundle = self.make_bundle("strict-mixed-era-spoof")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        del summary["summary_provenance"]
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        self.mark_allowlisted_legacy_identity(bundle)
        with patch("joulewise.bundle_read._check_config_sha256", return_value=[]):
            self.assertEqual(validate_bundle(bundle, strict=True), [])

    def test_reducer_0_4_1_missing_either_added_field_fails_strict(self) -> None:
        for field in ("remote_cleanup_failed", "runtime_cleanup_ok"):
            with self.subTest(field=field):
                bundle = self.make_bundle("strict-v041-missing-" + field)
                summary = json.loads((bundle / "summary_metrics.json").read_text())
                del summary["measurement_quality"][field]
                (bundle / "summary_metrics.json").write_text(
                    json.dumps(summary, indent=2, sort_keys=True) + "\n"
                )

                problems = validate_bundle(bundle, strict=True)

                self.assertEqual(len(problems), 1)
                self.assertIn("measurement_quality." + field, problems[0])

    def test_tampered_reducer_0_4_1_summary_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-v041-tampered")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["energy_request_j"] = 999999.0
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )

        problems = validate_bundle(bundle, strict=True)

        self.assertEqual(len(problems), 1)
        self.assertIn("energy_request_j", problems[0])

    def test_legacy_summary_missing_honesty_fields_keeps_strict_tolerance(self) -> None:
        bundle = self.make_bundle("strict-legacy-missing-honesty")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        del summary["summary_provenance"]
        del summary["measurement_quality"]["token_counts_source"]
        del summary["measurement_quality"]["phase_identifiability"]
        del summary["measurement_quality"]["remote_cleanup_failed"]
        del summary["measurement_quality"]["runtime_cleanup_ok"]
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        self.mark_allowlisted_legacy_identity(bundle)

        with patch("joulewise.bundle_read._check_config_sha256", return_value=[]):
            self.assertEqual(validate_bundle(bundle, strict=True), [])

    def test_stored_value_drift_still_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-stored-drift")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["idle_baseline"]["gpu_freq_hz_mean"] = 123.0
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        problems = validate_bundle(bundle, strict=True)
        self.assertEqual(len(problems), 1)
        self.assertIn("idle_baseline.gpu_freq_hz_mean", problems[0])

    def test_non_null_fresh_value_missing_from_stored_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-missing-non-null")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        del summary["idle_baseline"]["power_w_mean"]
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        problems = validate_bundle(bundle, strict=True)
        self.assertEqual(len(problems), 1)
        self.assertIn("idle_baseline.power_w_mean", problems[0])

    def test_stored_extra_key_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-stored-extra")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary["stored_extra"] = None
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        problems = validate_bundle(bundle, strict=True)
        self.assertEqual(len(problems), 1)
        self.assertIn("stored_extra", problems[0])

    def test_strict_adds_nothing_for_non_succeeded_bundles(self) -> None:
        # Failed/unsupported summaries are controller-written from partial
        # evidence; strict only judges claims of success.
        exit_code, out, _ = self.run_verb(
            self.write_unsupported_config("strict-unsupported")
        )
        self.assertEqual(exit_code, 3)
        bundle = self.bundle_path_from_line(out.splitlines()[0])
        self.assertEqual(validate_bundle(bundle, strict=True), [])

    def _make_powermetrics_bundle(self, run_id: str) -> Path:
        fixture = POWERMETRICS_FIXTURE.read_bytes()
        config_data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        config_data["run_id"] = run_id
        config_data["hardware_target"]["telemetry_backend"] = "powermetrics"
        config_data["workload_profile"]["output_tokens"] = 300
        config_data["sampling"] = {"power_hz": 2.0, "idle_seconds": 5.0}
        config = BenchmarkConfig.from_mapping(config_data)

        def fake_run(command, **kwargs):
            if "-o" in command:
                Path(command[command.index("-o") + 1]).write_bytes(fixture)
            return _completed(command)

        class FakePopen:
            def __init__(self, command, **kwargs):
                self.path = Path(command[command.index("-o") + 1])
                self.path.write_bytes(fixture)
                self.returncode = None

            def poll(self):
                return self.returncode

            def terminate(self):
                self.returncode = 0

            def kill(self):
                self.returncode = -9

            def communicate(self, timeout=None):
                self.returncode = 0
                return b"", b""

        with (
            patch("joulewise.adapters.powermetrics.subprocess.run", side_effect=fake_run),
            patch("joulewise.adapters.powermetrics.subprocess.Popen", FakePopen),
        ):
            bundle, summary = run_benchmark(
                config,
                self.runs_dir,
                FakeClock(start=1_783_394_100.0),
            )
        self.assertEqual(summary.status, RunStatus.SUCCEEDED)
        self.assertTrue((bundle / "raw" / RAW_SAMPLES_NAME).is_file())
        return bundle

    def _trace_rows(self, bundle: Path) -> list[list[str]]:
        return [
            line.split(",")
            for line in (bundle / "power_trace.csv").read_text().splitlines()
        ]

    def _tamper_gpu_power_row(self, bundle: Path) -> None:
        rows = self._trace_rows(bundle)
        self.assertEqual(rows[2][3], "gpu_power")
        rows[2][1] = str(float(rows[2][1]) + 1.0)
        (bundle / "power_trace.csv").write_text(
            "".join(",".join(row) + "\n" for row in rows)
        )

    def test_powermetrics_raw_to_trace_matching_bundle_passes_strict(self) -> None:
        bundle = self._make_powermetrics_bundle("strict-pm-clean")
        self.assertEqual(validate_bundle(bundle, strict=True), [])
        code, out, err = _run(["validate-bundle", "--strict", str(bundle)])
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), f"valid bundle: {bundle}")

    def test_powermetrics_raw_to_trace_value_tamper_fails_with_row_and_rail(self) -> None:
        bundle = self._make_powermetrics_bundle("strict-pm-tamper")
        self._tamper_gpu_power_row(bundle)

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(any("strict: raw-to-trace:" in p for p in problems), problems)
        problem = next(p for p in problems if "strict: raw-to-trace:" in p)
        self.assertIn("row 3", problem)
        self.assertIn("gpu_power", problem)
        self.assertIn("power_w", problem)

    def test_raw_to_trace_ignores_tampered_metadata_adapter_name(self) -> None:
        bundle = self._make_powermetrics_bundle("strict-pm-metadata-tampered")
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["adapters"]["telemetry"]["name"] = "mock"
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))
        self._tamper_gpu_power_row(bundle)

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(any("strict: raw-to-trace:" in p for p in problems), problems)

    def test_raw_to_trace_runs_without_metadata_adapters_block(self) -> None:
        bundle = self._make_powermetrics_bundle("strict-pm-no-adapters")
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata.pop("adapters")
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))
        self._tamper_gpu_power_row(bundle)

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(any("strict: raw-to-trace:" in p for p in problems), problems)

    def test_config_powermetrics_missing_raw_plist_fails_strict(self) -> None:
        bundle = self._make_powermetrics_bundle("strict-pm-missing-raw")
        (bundle / "raw" / RAW_SAMPLES_NAME).unlink()

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any(f"missing raw/{RAW_SAMPLES_NAME}" in p for p in problems),
            problems,
        )

    def test_powermetrics_raw_to_trace_formatting_only_variant_passes_strict(self) -> None:
        bundle = self._make_powermetrics_bundle("strict-pm-format")
        rows = self._trace_rows(bundle)
        for row in rows[1:]:
            row[0] = row[0] + "0"
            row[1] = row[1] + "0"
        (bundle / "power_trace.csv").write_text(
            "".join(",".join(row) + "\n" for row in rows)
        )
        self.assertEqual(validate_bundle(bundle, strict=True), [])

    def test_raw_to_trace_mock_backend_has_explicit_strict_exemption(self) -> None:
        bundle = self.make_bundle("strict-non-pm-skip")
        self.assertFalse((bundle / "raw" / RAW_SAMPLES_NAME).exists())
        rows = self._trace_rows(bundle)
        rows[1][1] = str(float(rows[1][1]) + 1.0)
        (bundle / "power_trace.csv").write_text(
            "".join(",".join(row) + "\n" for row in rows)
        )
        problems = validate_bundle(bundle, strict=True)
        self.assertFalse(any("raw-to-trace" in p for p in problems), problems)

    def test_raw_to_trace_unregistered_production_backend_hard_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-unregistered-production")
        config = json.loads((bundle / "config.json").read_text(encoding="utf-8"))
        config["hardware_target"]["telemetry_backend"] = "jetson_rails"
        (bundle / "config.json").write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        problems = validate_bundle(bundle, strict=True)

        self.assertTrue(
            any(
                problem
                == "strict: raw-to-trace: no verifier registered for production backend jetson_rails"
                for problem in problems
            ),
            problems,
        )

    def test_new_summary_missing_workload_provenance_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-missing-workload-provenance")
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata.pop("workload_provenance")
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any("metadata.workload_provenance" in p for p in problems),
            problems,
        )

    def test_non_allowlisted_bundle_missing_provenance_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-non-allowlisted-missing-provenance")
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        summary.pop("summary_provenance")
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata.pop("workload_provenance")
        (bundle / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n"
        )

        problems = validate_bundle(bundle, strict=True)

        self.assertTrue(
            any("summary_metrics.summary_provenance" in p for p in problems),
            problems,
        )
        self.assertTrue(
            any("metadata.workload_provenance" in p for p in problems),
            problems,
        )

    def test_new_summary_wrong_prompt_hash_domain_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-wrong-prompt-domain")
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["workload_provenance"]["prompt"]["token_hash_domain"] = (
            "joulewise.prompt_token_ids.v2"
        )
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any("prompt.token_hash_domain" in p for p in problems),
            problems,
        )

    def test_new_summary_missing_generator_block_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-missing-generator")
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["workload_provenance"].pop("generator")
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any("workload_provenance.generator" in p for p in problems),
            problems,
        )

    def test_new_summary_malformed_prompt_hash_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-malformed-prompt-hash")
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["workload_provenance"]["prompt"]["token_ids_sha256"] = "A" * 64
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any("prompt.token_ids_sha256" in p for p in problems),
            problems,
        )

    def test_new_summary_missing_tokenizer_revision_key_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-missing-tokenizer-revision")
        metadata = json.loads((bundle / "metadata.json").read_text())
        del metadata["workload_provenance"]["tokenizer"]["revision"]
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any("tokenizer" in p and "revision" in p for p in problems),
            problems,
        )

    def test_new_summary_missing_tokenizer_vocab_size_key_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-missing-tokenizer-vocab-size")
        metadata = json.loads((bundle / "metadata.json").read_text())
        del metadata["workload_provenance"]["tokenizer"]["vocab_size"]
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any("tokenizer" in p and "vocab_size" in p for p in problems),
            problems,
        )

    def test_new_summary_null_tokenizer_vocab_size_passes_strict(self) -> None:
        bundle = self.make_bundle("strict-null-tokenizer-vocab-size")
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["workload_provenance"]["tokenizer"]["vocab_size"] = None
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))

        self.assertEqual(validate_bundle(bundle, strict=True), [])

    def test_new_summary_missing_prompt_realized_token_count_key_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-missing-prompt-realized-count")
        metadata = json.loads((bundle / "metadata.json").read_text())
        del metadata["workload_provenance"]["prompt"]["realized_token_count"]
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any("prompt" in p and "realized_token_count" in p for p in problems),
            problems,
        )

    def test_new_summary_non_positive_prompt_realized_token_count_fails_strict(
        self,
    ) -> None:
        bundle = self.make_bundle("strict-bad-prompt-realized-count")
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["workload_provenance"]["prompt"]["realized_token_count"] = 0
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any("prompt.realized_token_count" in p for p in problems),
            problems,
        )

    def test_new_summary_non_positive_tokenizer_vocab_size_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-bad-tokenizer-vocab-size")
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["workload_provenance"]["tokenizer"]["vocab_size"] = 0
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any("tokenizer.vocab_size" in p for p in problems),
            problems,
        )

    def test_new_summary_malformed_prompt_text_hash_fails_strict(self) -> None:
        bundle = self.make_bundle("strict-malformed-prompt-text-hash")
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["workload_provenance"]["prompt"]["text_sha256"] = "not-a-sha"
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))

        problems = validate_bundle(bundle, strict=True)
        self.assertTrue(
            any("prompt.text_sha256" in p for p in problems),
            problems,
        )

    def test_new_summary_null_present_model_source_passes_strict(self) -> None:
        bundle = self.make_bundle("strict-null-model-source")
        metadata = json.loads((bundle / "metadata.json").read_text())
        metadata["workload_provenance"]["model"]["source"] = None
        (bundle / "metadata.json").write_text(json.dumps(metadata, indent=2))

        self.assertEqual(validate_bundle(bundle, strict=True), [])


class ReduceVerbTests(CliRunTestCase):
    """Slice 2N.6 (D-028): post-hoc re-reduction of an existing bundle."""

    def make_bundle(self, run_id: str) -> Path:
        exit_code, out, _ = self.run_verb(self.write_config(run_id))
        self.assertEqual(exit_code, 0)
        return self.bundle_path_from_line(out.splitlines()[0])

    def test_reduce_rederives_identical_summary_exit_0(self) -> None:
        bundle = self.make_bundle("reduce-identical")
        original = json.loads((bundle / "summary_metrics.json").read_text())
        # Clobber the summary to prove reduce rewrites it from raw evidence.
        (bundle / "summary_metrics.json").write_text('{"status": "failed"}')
        exit_code, out, err = _run(["reduce", str(bundle)])
        self.assertEqual(exit_code, 0, err)
        self.assertRegex(out.splitlines()[0], SUCCEEDED_LINE)
        rederived = json.loads((bundle / "summary_metrics.json").read_text())
        self.assertEqual(rederived, original)
        # The re-reduced bundle still validates structurally.
        self.assertEqual(validate_bundle(bundle), [])

    def test_reduce_corrupt_metadata_exit_3_structured_summary(self) -> None:
        bundle = self.make_bundle("reduce-corrupt")
        (bundle / "metadata.json").write_text("{broken")
        exit_code, out, _ = _run(["reduce", str(bundle)])
        self.assertEqual(exit_code, 3)
        self.assertIn("status=failed", out)
        self.assertIn("reason=unknown_error", out)
        summary = json.loads((bundle / "summary_metrics.json").read_text())
        self.assertEqual(summary["status"], "failed")
        self.assertIn("metadata.json", summary["failure_message"])

    def test_reduce_non_bundle_directory_exit_2_no_write(self) -> None:
        not_a_bundle = self.tmp / "not-a-bundle"
        not_a_bundle.mkdir()
        exit_code, _, err = _run(["reduce", str(not_a_bundle)])
        self.assertEqual(exit_code, 2)
        self.assertIn("not a run bundle", err)
        # Evidence is never invented inside an arbitrary directory.
        self.assertFalse((not_a_bundle / "summary_metrics.json").exists())

    def test_reduce_missing_path_exit_2(self) -> None:
        exit_code, _, err = _run(["reduce", str(self.tmp / "missing")])
        self.assertEqual(exit_code, 2)
        self.assertIn("error:", err)

    def test_reduce_help_names_the_verb(self) -> None:
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit) as ctx:
            main(["--help"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("reduce", out.getvalue())


if __name__ == "__main__":
    unittest.main()
