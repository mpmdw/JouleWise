"""Tests for the run-bundle writer (Slice 2A; D-001, D-010, D-011, D-018)."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.bundle import (
    BundleError,
    RunBundleWriter,
    generate_run_id,
    sanitize_id_component,
    write_experiment_manifest,
    write_derived_artifact,
    write_raw_artifact,
)
from joulewise.clock import FakeClock
from joulewise.interfaces import PowerSample, RunContext, RuntimeEvent
from joulewise.schemas import (
    BenchmarkConfig,
    FailureReason,
    RunStatus,
    SummaryMetrics,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_local.json"

EVENT_KEYS = {"timestamp_s", "event_type", "phase", "message", "metadata"}


def load_example_config(**overrides) -> BenchmarkConfig:
    config = BenchmarkConfig.from_mapping(json.loads(EXAMPLE_CONFIG_PATH.read_text()))
    if overrides:
        config = dataclasses.replace(config, **overrides)
    return config


def make_summary() -> SummaryMetrics:
    return SummaryMetrics(
        status=RunStatus.SUCCEEDED,
        energy_request_j=1.25,
        energy_token_j=0.03125,
        ttft_s=0.05,
        throughput_tokens_s=80.0,
    )


class SanitizeIdComponentTests(unittest.TestCase):
    def test_uppercase_is_lowered(self) -> None:
        self.assertEqual(sanitize_id_component("MacBook"), "macbook")

    def test_spaces_become_dashes(self) -> None:
        self.assertEqual(sanitize_id_component("my run name"), "my-run-name")

    def test_dots_become_dashes(self) -> None:
        self.assertEqual(sanitize_id_component("v0.1.2"), "v0-1-2")

    def test_allowed_chars_pass_through(self) -> None:
        self.assertEqual(sanitize_id_component("abc_09-z"), "abc_09-z")

    def test_mixed_case_spaces_and_dots(self) -> None:
        self.assertEqual(sanitize_id_component("My Run.ID v2"), "my-run-id-v2")

    def test_empty_input_raises(self) -> None:
        with self.assertRaises(BundleError):
            sanitize_id_component("")


class GenerateRunIdTests(unittest.TestCase):
    def test_config_run_id_used_verbatim_after_sanitize(self) -> None:
        clock = FakeClock(start=1_768_000_000.0)
        config = load_example_config(run_id="My Custom.Run ID")
        run_id = generate_run_id(config, clock)
        self.assertEqual(run_id, "my-custom-run-id")

    def test_config_run_id_gets_no_timestamp_or_suffix(self) -> None:
        clock = FakeClock(start=1_768_000_000.0)
        config = load_example_config()
        self.assertEqual(generate_run_id(config, clock), "example-mock-local")

    def test_generated_id_matches_d010_pattern(self) -> None:
        clock = FakeClock(start=1_768_000_000.0)
        config = load_example_config(run_id=None)
        run_id = generate_run_id(config, clock)
        self.assertRegex(
            run_id,
            r"^\d{8}T\d{6}Z__mock_target__mock_smoke__[0-9a-f]{4}$",
        )

    def test_generated_id_timestamp_comes_from_clock(self) -> None:
        # 2026-01-10T00:26:40Z == epoch 1768004800
        clock = FakeClock(start=1_768_004_800.0)
        config = load_example_config(run_id=None)
        run_id = generate_run_id(config, clock)
        self.assertTrue(run_id.startswith("20260110T002640Z__"))

    def test_generated_id_suffix_is_deterministic_for_same_config(self) -> None:
        # D-022: the 4-hex suffix is derived from the config content hash, not a
        # random token, so identical config + clock yields a byte-identical
        # run_id across calls (the determinism that makes runs reproducible).
        clock = FakeClock(start=1_768_000_000.0)
        config = load_example_config(run_id=None)
        ids = {generate_run_id(config, clock) for _ in range(16)}
        self.assertEqual(len(ids), 1)

    def test_generated_id_suffix_differs_for_different_config(self) -> None:
        # A different config (different model name) changes the hash-derived
        # suffix, so distinct configs still get distinct run IDs.
        clock = FakeClock(start=1_768_000_000.0)
        data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        data["run_id"] = None
        config_a = BenchmarkConfig.from_mapping(data)
        data_b = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        data_b["run_id"] = None
        data_b["model"]["name"] = "other-model"
        config_b = BenchmarkConfig.from_mapping(data_b)
        self.assertNotEqual(
            generate_run_id(config_a, clock), generate_run_id(config_b, clock)
        )


class RunBundleWriterTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runs_root = Path(self._tmp.name) / "runs"
        self.clock = FakeClock(start=1_768_000_000.0)
        self.config = load_example_config()

    def make_writer(self, **config_overrides) -> RunBundleWriter:
        config = load_example_config(**config_overrides) if config_overrides else self.config
        return RunBundleWriter.create(self.runs_root, config, self.clock)

    def event(self, event_type: str = "stage_started", phase: str = "validate") -> RuntimeEvent:
        return RuntimeEvent(
            timestamp_s=self.clock.now(),
            event_type=event_type,
            phase=phase,
            message=f"{phase} {event_type}",
            metadata={"stage": phase},
        )

    def test_create_builds_layout_and_seed_artifacts(self) -> None:
        writer = self.make_writer()
        self.assertEqual(writer.run_id, "example-mock-local")
        self.assertEqual(writer.path, self.runs_root / "example-mock-local")
        for subdir in ("raw", "logs", "outputs"):
            self.assertTrue((writer.path / subdir).is_dir(), subdir)
        self.assertTrue((writer.path / "config.json").is_file())
        self.assertEqual((writer.path / "events.jsonl").read_text(), "")

    def test_config_json_is_sorted_normalized_form(self) -> None:
        writer = self.make_writer()
        text = (writer.path / "config.json").read_text()
        expected = json.dumps(self.config.to_dict(), indent=2, sort_keys=True) + "\n"
        self.assertEqual(text, expected)

    def test_config_sha256_matches_independent_recomputation(self) -> None:
        writer = self.make_writer()
        recomputed = hashlib.sha256((writer.path / "config.json").read_bytes()).hexdigest()
        self.assertEqual(writer.config_sha256, recomputed)

    def test_existing_directory_collision_raises(self) -> None:
        self.make_writer()
        with self.assertRaises(BundleError):
            self.make_writer()

    def test_full_artifact_set_for_synthetic_run(self) -> None:
        writer = self.make_writer()
        writer.append_event(self.event("run_started", "run"))
        for phase in ("validate", "prepare", "measured_run"):
            self.clock.sleep(0.5)
            writer.append_event(self.event("stage_started", phase))
            self.clock.sleep(0.5)
            writer.append_event(self.event("stage_completed", phase))
        writer.write_power_trace(
            [
                PowerSample(timestamp_s=1_768_000_000.5, power_w=5.0, source="mock", rail="mock"),
                PowerSample(timestamp_s=1_768_000_001.0, power_w=7.5, source="mock", rail="mock"),
            ]
        )
        writer.write_output("response.txt", "hello world\n")
        writer.write_output("tokens.jsonl", '{"index": 0, "timestamp_s": 1768000000.6}\n')
        log = writer.log_path("controller.log")
        log.write_text("controller ran\n")
        writer.write_metadata({"runtime_adapter": "mock", "telemetry_adapter": "mock"})
        writer.write_summary(make_summary())
        result = writer.finalize()

        self.assertEqual(result, writer.path)
        # Every artifact named in run_bundle_layout.md exists.
        for artifact in (
            "config.json",
            "metadata.json",
            "events.jsonl",
            "power_trace.csv",
            "summary_metrics.json",
            "logs/controller.log",
            "outputs/response.txt",
            "outputs/tokens.jsonl",
        ):
            self.assertTrue((writer.path / artifact).is_file(), artifact)
        self.assertTrue((writer.path / "raw").is_dir())

        summary = json.loads((writer.path / "summary_metrics.json").read_text())
        self.assertEqual(summary["status"], "succeeded")
        self.assertEqual(summary["energy_request_j"], 1.25)

    def test_events_jsonl_lines_parse_with_exact_key_set(self) -> None:
        writer = self.make_writer()
        writer.append_event(self.event("run_started", "run"))
        writer.append_event(self.event("stage_started", "validate"))
        writer.write_metadata({})
        writer.write_summary(make_summary())
        writer.finalize()
        lines = (writer.path / "events.jsonl").read_text().splitlines()
        self.assertEqual(len(lines), 3)
        for line in lines:
            record = json.loads(line)
            self.assertEqual(set(record), EVENT_KEYS)

    def test_finalize_appends_run_finalized_event_last(self) -> None:
        writer = self.make_writer()
        writer.append_event(self.event("run_started", "run"))
        writer.write_metadata({})
        writer.write_summary(make_summary())
        self.clock.sleep(2.0)
        writer.finalize()
        lines = (writer.path / "events.jsonl").read_text().splitlines()
        last = json.loads(lines[-1])
        self.assertEqual(last["event_type"], "run_finalized")
        self.assertEqual(last["phase"], "run")
        self.assertEqual(last["message"], "bundle finalized")
        self.assertEqual(last["timestamp_s"], 1_768_000_002.0)
        self.assertEqual(last["metadata"], {})

    def test_power_trace_header_exact_and_rail_none_empty(self) -> None:
        writer = self.make_writer()
        writer.write_power_trace(
            [
                PowerSample(timestamp_s=1.0, power_w=5.0, source="mock", rail="mock"),
                PowerSample(timestamp_s=1.5, power_w=6.25, source="mock", rail=None),
            ]
        )
        lines = (writer.path / "power_trace.csv").read_text().splitlines()
        self.assertEqual(lines[0], "timestamp_s,power_w,source,rail")
        self.assertEqual(lines[1], "1.0,5.0,mock,mock")
        self.assertEqual(lines[2], "1.5,6.25,mock,")
        self.assertEqual(len(lines), 3)

    def test_double_write_power_trace_raises(self) -> None:
        writer = self.make_writer()
        writer.write_power_trace([])
        with self.assertRaises(BundleError):
            writer.write_power_trace([])

    def test_metadata_contents(self) -> None:
        writer = self.make_writer()
        writer.write_metadata({"runtime_adapter": "mock"})
        metadata = json.loads((writer.path / "metadata.json").read_text())
        self.assertEqual(metadata["schema_version"], "0.1")
        self.assertEqual(metadata["config_sha256"], writer.config_sha256)
        self.assertEqual(metadata["run_id"], writer.run_id)
        self.assertEqual(metadata["runtime_adapter"], "mock")
        self.assertEqual(metadata["clock"], {"kind": "fake", "start_s": 1_768_000_000.0})
        for key in ("platform", "machine", "python_version", "joulewise_version"):
            self.assertIsInstance(metadata[key], str, key)
        self.assertTrue(
            metadata["git_commit"] == "unknown"
            or re.fullmatch(r"[0-9a-f]{40}", metadata["git_commit"]),
            metadata["git_commit"],
        )

    def test_metadata_extra_collision_raises(self) -> None:
        writer = self.make_writer()
        with self.assertRaises(BundleError):
            writer.write_metadata({"run_id": "sneaky-override"})
        # The failed call must not consume the single metadata write.
        writer.write_metadata({})

    def test_double_write_metadata_raises(self) -> None:
        writer = self.make_writer()
        writer.write_metadata({})
        with self.assertRaises(BundleError):
            writer.write_metadata({})

    def test_write_suite_manifest_sorted_json_once(self) -> None:
        writer = self.make_writer()
        path = writer.write_suite_manifest({"b": 1, "a": {"z": 2}})
        self.assertEqual(path, writer.path / "suite_manifest.json")
        self.assertEqual(path.read_text(), '{\n  "a": {\n    "z": 2\n  },\n  "b": 1\n}\n')
        with self.assertRaises(BundleError):
            writer.write_suite_manifest({"again": True})

    def test_write_summary_before_metadata_raises(self) -> None:
        writer = self.make_writer()
        with self.assertRaises(BundleError):
            writer.write_summary(make_summary())

    def test_write_summary_stages_only(self) -> None:
        writer = self.make_writer()
        writer.write_metadata({})
        writer.write_summary(make_summary())
        self.assertFalse((writer.path / "summary_metrics.json").exists())

    def test_write_summary_validates_via_to_dict(self) -> None:
        writer = self.make_writer()
        writer.write_metadata({})
        invalid = SummaryMetrics(status=RunStatus.FAILED)  # missing failure_reason
        with self.assertRaises(Exception):
            writer.write_summary(invalid)

    def test_failed_summary_with_reason_is_writable(self) -> None:
        writer = self.make_writer()
        writer.write_metadata({})
        writer.write_summary(
            SummaryMetrics(
                status=RunStatus.FAILED,
                failure_reason=FailureReason.PERMISSION_DENIED,
                failure_message="telemetry denied",
            )
        )
        writer.finalize()
        summary = json.loads((writer.path / "summary_metrics.json").read_text())
        self.assertEqual(summary["status"], "failed")
        self.assertEqual(summary["failure_reason"], "permission_denied")

    def test_finalize_without_staged_summary_raises(self) -> None:
        writer = self.make_writer()
        writer.write_metadata({})
        with self.assertRaises(BundleError):
            writer.finalize()

    def test_summary_metrics_json_written_last_by_finalize(self) -> None:
        writer = self.make_writer()
        writer.write_metadata({})
        writer.write_summary(make_summary())
        writer.finalize()
        text = (writer.path / "summary_metrics.json").read_text()
        expected = json.dumps(make_summary().to_dict(), indent=2, sort_keys=True) + "\n"
        self.assertEqual(text, expected)

    def test_any_write_after_finalize_raises(self) -> None:
        writer = self.make_writer()
        writer.write_metadata({})
        writer.write_summary(make_summary())
        writer.finalize()
        with self.assertRaises(BundleError):
            writer.append_event(self.event())
        with self.assertRaises(BundleError):
            writer.write_power_trace([])
        with self.assertRaises(BundleError):
            writer.write_metadata({})
        with self.assertRaises(BundleError):
            writer.write_suite_manifest({})
        with self.assertRaises(BundleError):
            writer.write_output("late.txt", "no")
        with self.assertRaises(BundleError):
            writer.write_summary(make_summary())
        with self.assertRaises(BundleError):
            writer.finalize()

    def test_write_output_returns_path(self) -> None:
        writer = self.make_writer()
        path = writer.write_output("response.txt", "hi\n")
        self.assertEqual(path, writer.path / "outputs" / "response.txt")
        self.assertEqual(path.read_text(), "hi\n")

    def test_log_path_does_not_write(self) -> None:
        writer = self.make_writer()
        path = writer.log_path("runtime.log")
        self.assertEqual(path, writer.path / "logs" / "runtime.log")
        self.assertTrue(path.parent.is_dir())
        self.assertFalse(path.exists())

    def test_generated_run_id_used_for_directory(self) -> None:
        writer = self.make_writer(run_id=None)
        self.assertRegex(
            writer.run_id,
            r"^\d{8}T\d{6}Z__mock_target__mock_smoke__[0-9a-f]{4}$",
        )
        self.assertTrue((self.runs_root / writer.run_id).is_dir())


class RawEvidenceTests(unittest.TestCase):
    """Writer-side raw-evidence counterpart of the D-024 context seam (2N.1)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runs_root = Path(self._tmp.name) / "runs"
        self.clock = FakeClock(start=1_768_000_000.0)
        self.writer = RunBundleWriter.create(
            self.runs_root, load_example_config(), self.clock
        )

    def test_write_raw_text_and_bytes_land_under_raw(self) -> None:
        text_path = self.writer.write_raw("sampler_output.txt", "verbatim text\n")
        bytes_path = self.writer.write_raw("sampler_output.plist", b"\x00\x01binary")
        self.assertEqual(text_path, self.writer.path / "raw" / "sampler_output.txt")
        self.assertEqual(text_path.read_text(), "verbatim text\n")
        self.assertEqual(bytes_path.read_bytes(), b"\x00\x01binary")

    def test_raw_path_returns_location_without_writing(self) -> None:
        path = self.writer.raw_path("powermetrics.plist")
        self.assertEqual(path, self.writer.path / "raw" / "powermetrics.plist")
        self.assertFalse(path.exists())

    def test_write_raw_collision_raises(self) -> None:
        self.writer.write_raw("once.json", "{}")
        with self.assertRaises(BundleError):
            self.writer.write_raw("once.json", "{}")

    def test_write_raw_after_finalize_raises(self) -> None:
        self.writer.write_metadata({})
        self.writer.write_summary(make_summary())
        self.writer.finalize()
        with self.assertRaises(BundleError):
            self.writer.write_raw("late.json", "{}")

    def test_raw_name_must_be_plain_file_name(self) -> None:
        for bad in ("", ".", "..", "a/b.json", "..\\evil", "/abs.json"):
            with self.assertRaises(BundleError, msg=bad):
                self.writer.raw_path(bad)

    def _context(self) -> RunContext:
        return RunContext(
            config=load_example_config(),
            clock=self.clock,
            run_id=self.writer.run_id,
            bundle_path=self.writer.path,
            raw_dir=self.writer.path / "raw",
            logs_dir=self.writer.path / "logs",
            outputs_dir=self.writer.path / "outputs",
        )

    def test_write_derived_artifact_lands_at_bundle_top_level(self) -> None:
        path = write_derived_artifact(self._context(), "rich_telemetry.jsonl", "{}\n")
        self.assertEqual(path, self.writer.path / "rich_telemetry.jsonl")
        self.assertEqual(path.read_text(), "{}\n")

    def test_write_derived_artifact_rejects_reserved_names_and_collisions(self) -> None:
        context = self._context()
        for reserved in (
            "config.json",
            "metadata.json",
            "events.jsonl",
            "power_trace.csv",
            "summary_metrics.json",
        ):
            with self.assertRaises(BundleError, msg=reserved):
                write_derived_artifact(context, reserved, "{}\n")
        write_derived_artifact(context, "rich_telemetry.jsonl", "{}\n")
        with self.assertRaises(BundleError):
            write_derived_artifact(context, "rich_telemetry.jsonl", "{}\n")

    def test_write_derived_artifact_name_must_be_plain_file_name(self) -> None:
        context = self._context()
        for bad in ("", ".", "..", "a/b.json", "..\\evil", "/abs.json"):
            with self.assertRaises(BundleError, msg=bad):
                write_derived_artifact(context, bad, "{}\n")

    def test_adapter_helper_writes_validates_and_refuses_overwrite(self) -> None:
        # 2026-07-06 status review P3: adapters get the same validation and
        # no-overwrite rule as the writer, without the writer's authority.
        context = self._context()
        path = write_raw_artifact(context, "sampler.plist", b"\x00raw")
        self.assertEqual(path, self.writer.path / "raw" / "sampler.plist")
        self.assertEqual(path.read_bytes(), b"\x00raw")
        with self.assertRaises(BundleError):
            write_raw_artifact(context, "sampler.plist", b"again")
        with self.assertRaises(BundleError):
            write_raw_artifact(context, "../escape.plist", b"nope")

    def test_adapter_helper_and_writer_share_the_collision_space(self) -> None:
        self.writer.write_raw("shared.json", "{}")
        with self.assertRaises(BundleError):
            write_raw_artifact(self._context(), "shared.json", "{}")


class ExperimentManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.runs_root = Path(self._tmp.name) / "runs"

    def test_writes_manifest_under_experiments(self) -> None:
        manifest = {
            "experiment_id": "exp-001",
            "config_sha256": "abc",
            "members": ["exp-001__r1"],
        }
        path = write_experiment_manifest(self.runs_root, manifest)
        self.assertEqual(path, self.runs_root / "experiments" / "exp-001.json")
        self.assertEqual(json.loads(path.read_text()), manifest)

    def test_filename_uses_sanitized_experiment_id(self) -> None:
        path = write_experiment_manifest(self.runs_root, {"experiment_id": "Exp One.v2"})
        self.assertEqual(path.name, "exp-one-v2.json")

    def test_overwrite_is_allowed(self) -> None:
        first = {"experiment_id": "exp-001", "members": ["exp-001__r1"]}
        extended = {"experiment_id": "exp-001", "members": ["exp-001__r1", "exp-001__r2"]}
        write_experiment_manifest(self.runs_root, first)
        path = write_experiment_manifest(self.runs_root, extended)
        self.assertEqual(json.loads(path.read_text()), extended)

    def test_missing_experiment_id_raises(self) -> None:
        with self.assertRaises(BundleError):
            write_experiment_manifest(self.runs_root, {"members": []})

    def test_overwrite_is_atomic_replace(self) -> None:
        # P2-040 FIX-6 (ARC-5): the rewrite goes through a same-directory temp
        # file + os.replace, so a failure mid-rewrite leaves the previous
        # manifest intact rather than a truncated JSON file.
        first = {"experiment_id": "exp-001", "members": ["exp-001__r1"]}
        extended = {"experiment_id": "exp-001", "members": ["exp-001__r1", "exp-001__r2"]}
        path = write_experiment_manifest(self.runs_root, first)

        def failing_replace(src: object, dst: object) -> None:
            raise OSError("simulated crash during manifest replacement")

        with mock.patch("joulewise.bundle.os.replace", side_effect=failing_replace):
            with self.assertRaises(OSError):
                write_experiment_manifest(self.runs_root, extended)

        # Destination untouched by the failed rewrite; no temp litter left.
        self.assertEqual(json.loads(path.read_text()), first)
        leftovers = [
            entry.name
            for entry in (self.runs_root / "experiments").iterdir()
            if entry.name != path.name
        ]
        self.assertEqual(leftovers, [])

    def test_successful_overwrite_leaves_no_temp_files(self) -> None:
        write_experiment_manifest(self.runs_root, {"experiment_id": "exp-001", "members": []})
        write_experiment_manifest(
            self.runs_root, {"experiment_id": "exp-001", "members": ["exp-001__r1"]}
        )
        entries = sorted(p.name for p in (self.runs_root / "experiments").iterdir())
        self.assertEqual(entries, ["exp-001.json"])


if __name__ == "__main__":
    unittest.main()
