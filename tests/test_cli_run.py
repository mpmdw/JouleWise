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
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any

from joulewise.cli import main, validate_bundle

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_local.json"

#: The single machine-greppable success line shape the contract pins.
SUCCEEDED_LINE = re.compile(r"^bundle: (\S+) status=succeeded$")


def _run(argv: list[str]) -> tuple[int, str, str]:
    """Invoke ``cli.main(argv)`` capturing exit code, stdout, stderr."""
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        exit_code = main(argv)
    return exit_code, out.getvalue(), err.getvalue()


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

    def test_validate_bundle_helper_is_importable_and_pure(self) -> None:
        bundle = self.make_bundle("vb-helper")
        problems = validate_bundle(bundle)
        self.assertEqual(problems, [])
        # Deleting an artifact yields a specific problem string, not an exception.
        (bundle / "metadata.json").unlink()
        problems = validate_bundle(bundle)
        self.assertTrue(any("metadata.json" in problem for problem in problems))


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
