"""Tests for the run-bundle writer (Slice 2A; D-001, D-010, D-011, D-018)."""

from __future__ import annotations

import concurrent.futures
import dataclasses
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import joulewise
import joulewise.bundle as bundle_module
from joulewise.bundle import (
    BundleError,
    RunBundleWriter,
    generate_run_id,
    sanitize_id_component,
    write_experiment_manifest,
    write_experiment_rejection_verdict,
    write_derived_artifact,
    write_raw_artifact,
)
from joulewise.clock import FakeClock
from joulewise.interfaces import PowerSample, RunContext, RuntimeEvent
from joulewise.schemas import (
    BenchmarkConfig,
    EnergyEvidence,
    FailureReason,
    RunStatus,
    SchemaError,
    SummaryMetrics,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_local.json"

EVENT_KEYS = {"timestamp_s", "event_type", "phase", "message", "metadata"}

_CLEAN_SOURCE_STATE = {
    "git_commit": "a" * 40,
    "tracked": "clean",
    "staged": "clean",
    "untracked": "clean",
    "diff_sha256": "0" * 64,
}


class StrReprTrap:
    """Poison value whose textual fallback must never be consulted."""

    str_calls = 0
    repr_calls = 0

    def __str__(self) -> str:
        type(self).str_calls += 1
        raise AssertionError("metadata quarantine called str()")

    def __repr__(self) -> str:
        type(self).repr_calls += 1
        raise AssertionError("metadata quarantine called repr()")
def source_state(
    *,
    commit: str = "1" * 40,
    tracked: str = "clean",
    staged: str = "clean",
    untracked: str = "clean",
    diff_sha256: str = "2" * 64,
) -> dict[str, str]:
    return {
        "git_commit": commit,
        "tracked": tracked,
        "staged": staged,
        "untracked": untracked,
        "diff_sha256": diff_sha256,
    }


def load_example_config(**overrides) -> BenchmarkConfig:
    config = BenchmarkConfig.from_mapping(json.loads(EXAMPLE_CONFIG_PATH.read_text()))
    if overrides:
        config = dataclasses.replace(config, **overrides)
    return config


def make_summary() -> SummaryMetrics:
    return SummaryMetrics(
        status=RunStatus.SUCCEEDED,
        gross_energy_j=1.25,
        ttft_s=0.05,
        throughput_tokens_s=80.0,
        window_evidence_precheck={
            "idle_subtracted_request": {
                "energy_evidence": EnergyEvidence.ABSENT.value,
                "eligible": False,
                "reasons": ["idle_baseline_unrecorded"],
            }
        },
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

    def make_source_checkout(self) -> tuple[Path, Path, Path]:
        root = Path(self._tmp.name) / "source-checkout"
        source_path = root / "joulewise" / "bundle.py"
        outside_path = root / "scripts" / "outside.py"
        source_path.parent.mkdir(parents=True)
        outside_path.parent.mkdir(parents=True)
        source_path.write_text("# source marker\n")
        outside_path.write_text("# outside marker\n")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "bundle-test@example.invalid"],
            cwd=root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Bundle Test"],
            cwd=root,
            check=True,
        )
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", "fixture"],
            cwd=root,
            check=True,
        )
        return root, source_path, outside_path

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
        self.assertEqual(summary["gross_energy_j"], 1.25)
        self.assertIsNone(summary["energy_request_j"])
        self.assertEqual(
            summary["window_evidence_precheck"]["idle_subtracted_request"][
                "energy_evidence"
            ],
            "absent",
        )

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
        self.assertEqual(
            metadata["source_provenance"]["start"]["git_commit"],
            metadata["git_commit"],
        )

    def test_source_provenance_is_captured_at_creation_and_compared_at_metadata(self) -> None:
        start = source_state()
        probe_outputs = [
            str(self._tmp.name).encode() + b"\n",
            b"1" * 40 + b"\n",
            b"",
            b"",
            b"",
            str(self._tmp.name).encode() + b"\n",
            b"1" * 40 + b"\n",
            b"",
            b"",
            b"new-source.py\0",
        ]

        def fake_git(*args, **kwargs):
            return mock.Mock(
                returncode=0,
                communicate=mock.Mock(return_value=(probe_outputs.pop(0), b"")),
            )

        with mock.patch("joulewise.bundle._GIT_POPEN", side_effect=fake_git) as capture:
            writer = self.make_writer(run_id="source-change")
            self.assertEqual(capture.call_count, 5)
            writer.append_event(self.event(phase="adapter-executed"))
            (Path(self._tmp.name) / "new-source.py").write_text("changed\n")
            writer.write_metadata({})

        source_dir = Path(bundle_module.__file__).resolve().parent
        expected_cwds = [source_dir, *([Path(self._tmp.name)] * 4)] * 2
        self.assertEqual(
            [call.kwargs["cwd"] for call in capture.call_args_list],
            expected_cwds,
        )

        provenance = json.loads(
            (writer.path / "metadata.json").read_text()
        )["source_provenance"]
        self.assertEqual(capture.call_count, 10)
        self.assertEqual(provenance["start"]["git_commit"], start["git_commit"])
        self.assertEqual(provenance["start"]["tracked"], "clean")
        self.assertEqual(provenance["end"]["untracked"], "dirty")
        self.assertNotEqual(
            provenance["start"]["diff_sha256"],
            provenance["end"]["diff_sha256"],
        )
        self.assertIs(provenance["changed_during_run"], True)
        self.assertIs(provenance["claim_eligible"], False)
        self.assertEqual(
            provenance["reason_codes"],
            ["end_untracked_dirty", "source_changed_during_run"],
        )

    def test_writer_creation_captures_tracked_change_outside_package_tree(self) -> None:
        root, source_path, outside_path = self.make_source_checkout()
        outside_path.write_text("# changed outside package\n")

        with mock.patch.object(bundle_module, "__file__", str(source_path)):
            writer = self.make_writer(run_id="outside-package-dirty")
            writer.write_metadata({})

        provenance = json.loads(
            (writer.path / "metadata.json").read_text()
        )["source_provenance"]
        self.assertEqual(provenance["start"]["tracked"], "dirty")
        self.assertEqual(provenance["end"]["tracked"], "dirty")
        self.assertEqual(
            provenance["reason_codes"],
            ["start_tracked_dirty", "end_tracked_dirty"],
        )
        self.assertEqual(root, source_path.parent.parent)

    def test_writer_creation_resolves_root_untracked_path_from_checkout_root(self) -> None:
        root, source_path, _ = self.make_source_checkout()
        (root / "root-note.txt").write_text("root-relative content\n")

        with (
            mock.patch.object(bundle_module, "__file__", str(source_path)),
            mock.patch(
                "joulewise.bundle._untracked_identity",
                wraps=bundle_module._untracked_identity,
            ) as untracked_identity,
        ):
            writer = self.make_writer(run_id="root-untracked")
            writer.write_metadata({})

        provenance = json.loads(
            (writer.path / "metadata.json").read_text()
        )["source_provenance"]
        self.assertEqual(provenance["start"]["untracked"], "dirty")
        self.assertEqual(provenance["end"]["untracked"], "dirty")
        self.assertEqual(untracked_identity.call_count, 2)
        for call in untracked_identity.call_args_list:
            self.assertEqual(call.args, (root.resolve(), b"root-note.txt\0"))

    def test_dirty_and_unknown_source_provenance_do_not_block_bundle_completion(self) -> None:
        for label in ("dirty", "unknown"):
            if label == "dirty":
                probe_outputs = [
                    value
                    for _ in range(2)
                    for value in (
                        str(REPO_ROOT).encode() + b"\n",
                        b"1" * 40 + b"\n",
                        b"tracked diff bytes",
                        b"staged diff bytes",
                        b"",
                    )
                ]

                def fake_git(*args, **kwargs):
                    return mock.Mock(
                        returncode=0,
                        communicate=mock.Mock(return_value=(probe_outputs.pop(0), b"")),
                    )
            else:
                def fake_git(*args, **kwargs):
                    return mock.Mock(
                        returncode=1,
                        communicate=mock.Mock(return_value=(b"", b"")),
                    )

            with self.subTest(label=label), mock.patch(
                "joulewise.bundle._GIT_POPEN",
                side_effect=fake_git,
            ):
                writer = self.make_writer(run_id=f"source-{label}")
                writer.write_metadata({})
                writer.write_summary(make_summary())
                finalized = writer.finalize()
                metadata = json.loads((finalized / "metadata.json").read_text())
                self.assertIs(
                    metadata["source_provenance"]["claim_eligible"],
                    False,
                )
                self.assertTrue((finalized / "summary_metrics.json").is_file())

    def test_valid_metadata_serialization_is_byte_unchanged(self) -> None:
        extra = {
            "runtime_adapter": "mock",
            "nested": {"enabled": True, "samples": [1, 2.5, None]},
        }
        with (
            mock.patch("joulewise.bundle.platform.platform", return_value="test-platform"),
            mock.patch("joulewise.bundle.platform.machine", return_value="test-machine"),
            mock.patch(
                "joulewise.bundle.platform.python_version", return_value="3.test"
            ),
            mock.patch("joulewise.bundle._capture_source_state", return_value=dict(_CLEAN_SOURCE_STATE)),
        ):
            writer = self.make_writer()
            writer.write_metadata(extra)
        expected = {
            "platform": "test-platform",
            "machine": "test-machine",
            "python_version": "3.test",
            "joulewise_version": joulewise.__version__,
            "schema_version": self.config.schema_version,
            "config_sha256": writer.config_sha256,
            "run_id": writer.run_id,
            "git_commit": "a" * 40,
            "clock": self.clock.info(),
            "source_provenance": {
                "schema": bundle_module.SOURCE_PROVENANCE_SCHEMA,
                "diff_identity": {
                    "algorithm": bundle_module.SOURCE_DIFF_IDENTITY_ALGORITHM,
                    "version": bundle_module.SOURCE_DIFF_IDENTITY_VERSION,
                },
                "start": _CLEAN_SOURCE_STATE,
                "end": _CLEAN_SOURCE_STATE,
                "changed_during_run": False,
                "claim_eligible": True,
                "reason_codes": [],
            },
            **extra,
        }
        self.assertEqual(
            (writer.path / "metadata.json").read_text(),
            json.dumps(expected, indent=2, sort_keys=True) + "\n",
        )

    def test_malformed_metadata_is_recursively_quarantined_deterministically(
        self,
    ) -> None:
        StrReprTrap.str_calls = 0
        StrReprTrap.repr_calls = 0

        def poison_payload(reverse: bool) -> dict:
            cycle: list[object] = []
            cycle.append(cycle)
            nested_items = [
                ("valid", {"kept": "evidence"}),
                ("nan", float("nan")),
                ("positive_infinity", float("inf")),
                ("negative_infinity", float("-inf")),
                (7, "invalid-key value must not leak"),
                ((1, 2), StrReprTrap()),
            ]
            root_items = [
                ("z_poison", StrReprTrap()),
                ("a/cycle~", cycle),
                ("nested", dict(reversed(nested_items) if reverse else nested_items)),
            ]
            return dict(reversed(root_items) if reverse else root_items)

        writer_a = self.make_writer()
        writer_a.write_metadata(poison_payload(False))
        other_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(other_tmp.cleanup)
        writer_b = RunBundleWriter.create(
            Path(other_tmp.name) / "runs", self.config, FakeClock(self.clock.now())
        )
        writer_b.write_metadata(poison_payload(True))

        bytes_a = (writer_a.path / "metadata.json").read_bytes()
        bytes_b = (writer_b.path / "metadata.json").read_bytes()
        self.assertEqual(bytes_a, bytes_b)
        self.assertNotIn(b"invalid-key value must not leak", bytes_a)
        self.assertEqual(StrReprTrap.str_calls, 0)
        self.assertEqual(StrReprTrap.repr_calls, 0)

        metadata = json.loads(bytes_a)
        self.assertIsNone(metadata["z_poison"])
        self.assertEqual(metadata["a/cycle~"], [None])
        self.assertEqual(metadata["nested"]["valid"], {"kept": "evidence"})
        self.assertIsNone(metadata["nested"]["nan"])
        self.assertIsNone(metadata["nested"]["positive_infinity"])
        self.assertIsNone(metadata["nested"]["negative_infinity"])
        self.assertNotIn("7", metadata["nested"])
        diagnostics = metadata["serialization_quarantine"]
        self.assertEqual(
            [(item["path"], item["reason"]) for item in diagnostics],
            [
                ("/a~1cycle~0/0", "cycle"),
                ("/nested", "non_string_key"),
                ("/nested", "non_string_key"),
                ("/nested/nan", "non_finite_number"),
                ("/nested/negative_infinity", "non_finite_number"),
                ("/nested/positive_infinity", "non_finite_number"),
                ("/z_poison", "unsupported_type"),
            ],
        )
        non_string = [
            item for item in diagnostics if item["reason"] == "non_string_key"
        ]
        self.assertEqual(
            [(item["key_type"], item["count"]) for item in non_string],
            [("builtins.int", 1), ("builtins.tuple", 1)],
        )

    def test_metadata_quarantine_field_is_writer_owned(self) -> None:
        writer = self.make_writer()
        with self.assertRaises(BundleError):
            writer.write_metadata({"serialization_quarantine": []})
        writer.write_metadata({})

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

    def test_failed_summary_with_non_numeric_energy_is_rejected(self) -> None:
        writer = self.make_writer()
        writer.write_metadata({})
        summary = SummaryMetrics(
            status=RunStatus.FAILED,
            failure_reason=FailureReason.UNKNOWN_ERROR,
            gross_energy_j="bad",  # type: ignore[arg-type]
        )

        with self.assertRaisesRegex(
            SchemaError, "energy field gross_energy_j.*finite number"
        ):
            writer.write_summary(summary)

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
        original_bytes = path.read_bytes()

        def failing_replace(src: object, dst: object) -> None:
            raise OSError("simulated crash during manifest replacement")

        with mock.patch("joulewise.bundle.os.replace", side_effect=failing_replace):
            with self.assertRaises(OSError):
                write_experiment_manifest(self.runs_root, extended)

        # Destination untouched by the failed rewrite; no temp litter left.
        self.assertEqual(json.loads(path.read_text()), first)
        self.assertEqual(path.read_bytes(), original_bytes)
        leftovers = [
            entry.name
            for entry in (self.runs_root / "experiments").iterdir()
            if entry.name not in {path.name, ".custody.lock"}
        ]
        self.assertEqual(leftovers, [])

    def test_atomic_manifest_durability_order_and_same_directory_temp(self) -> None:
        events: list[str] = []
        real_fdopen = os.fdopen
        real_fsync = os.fsync
        real_replace = os.replace

        class TrackedHandle:
            def __init__(self, handle):
                self.handle = handle

            def __enter__(self):
                self.handle.__enter__()
                return self

            def __exit__(self, *args):
                return self.handle.__exit__(*args)

            def write(self, value):
                return self.handle.write(value)

            def flush(self):
                events.append("flush")
                return self.handle.flush()

            def fileno(self):
                return self.handle.fileno()

        def tracked_fdopen(*args, **kwargs):
            return TrackedHandle(real_fdopen(*args, **kwargs))

        def tracked_fsync(fd):
            events.append("fsync")
            return real_fsync(fd)

        def tracked_replace(src, dst):
            events.append("replace")
            self.assertEqual(Path(src).parent, Path(dst).parent)
            return real_replace(src, dst)

        with mock.patch("joulewise.bundle.os.fdopen", side_effect=tracked_fdopen), mock.patch(
            "joulewise.bundle.os.fsync", side_effect=tracked_fsync
        ), mock.patch("joulewise.bundle.os.replace", side_effect=tracked_replace):
            write_experiment_manifest(self.runs_root, {"experiment_id": "durable"})

        self.assertLess(events.index("flush"), events.index("fsync"))
        self.assertLess(events.index("fsync"), events.index("replace"))
        self.assertEqual(events[-1], "fsync")  # directory fsync after replace

    def test_directory_fsync_is_best_effort_after_replace(self) -> None:
        real_fsync = os.fsync
        calls = 0

        def fail_second_fsync(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("directory fsync unsupported")
            return real_fsync(fd)

        with mock.patch("joulewise.bundle.os.fsync", side_effect=fail_second_fsync):
            path = write_experiment_manifest(
                self.runs_root, {"experiment_id": "best-effort"}
            )
        self.assertTrue(path.is_file())
        self.assertEqual(calls, 2)

    def test_successful_overwrite_leaves_no_temp_files(self) -> None:
        write_experiment_manifest(self.runs_root, {"experiment_id": "exp-001", "members": []})
        write_experiment_manifest(
            self.runs_root, {"experiment_id": "exp-001", "members": ["exp-001__r1"]}
        )
        entries = sorted(
            p.name
            for p in (self.runs_root / "experiments").iterdir()
            if p.name != ".custody.lock"
        )
        self.assertEqual(entries, ["exp-001.json"])
        self.assertTrue(
            (self.runs_root / "experiments" / ".custody.lock").is_file()
        )

    def test_rejection_collision_preserves_manifest_and_uses_unique_artifacts(
        self,
    ) -> None:
        manifest_path = write_experiment_manifest(
            self.runs_root,
            {"experiment_id": "exp-001", "members": ["exp-001__r1"]},
        )
        original_bytes = manifest_path.read_bytes()
        rejection = {
            "experiment_id": "exp-001",
            "members": [],
            "terminal_verdict": {
                "schema_version": "joulewise.cooldown_anchor_verdict.v1",
                "record_type": "cooldown_anchor_verdict",
                "decision": "fail_closed",
            },
        }

        first = write_experiment_rejection_verdict(self.runs_root, rejection)
        second = write_experiment_rejection_verdict(self.runs_root, rejection)

        self.assertEqual(manifest_path.read_bytes(), original_bytes)
        self.assertEqual(
            first,
            self.runs_root
            / "experiments"
            / "rejections"
            / "exp-001__cooldown_anchor_rejection.json",
        )
        self.assertEqual(
            second,
            self.runs_root
            / "experiments"
            / "rejections"
            / "exp-001__cooldown_anchor_rejection__2.json",
        )
        self.assertEqual(json.loads(first.read_text()), rejection)
        self.assertEqual(json.loads(second.read_text()), rejection)

    def test_first_rejection_may_claim_absent_manifest_path(self) -> None:
        rejection = {
            "experiment_id": "exp-001",
            "members": [],
            "terminal_verdict": {
                "schema_version": "joulewise.cooldown_anchor_verdict.v1",
                "record_type": "cooldown_anchor_verdict",
                "decision": "fail_closed",
            },
        }

        path = write_experiment_rejection_verdict(self.runs_root, rejection)

        self.assertEqual(path, self.runs_root / "experiments" / "exp-001.json")
        self.assertEqual(json.loads(path.read_text()), rejection)

    def test_manifest_relocates_canonical_rejection_before_publication(self) -> None:
        rejection = {
            "experiment_id": "exp-001",
            "members": [],
            "terminal_verdict": {
                "schema_version": "joulewise.cooldown_anchor_verdict.v1",
                "record_type": "cooldown_anchor_verdict",
                "decision": "fail_closed",
            },
        }
        canonical_path = write_experiment_rejection_verdict(
            self.runs_root, rejection
        )
        rejection_bytes = canonical_path.read_bytes()
        manifest = {
            "experiment_id": "exp-001",
            "members": ["exp-001__r1"],
        }

        manifest_path = write_experiment_manifest(self.runs_root, manifest)

        relocated_path = (
            self.runs_root
            / "experiments"
            / "rejections"
            / "exp-001__cooldown_anchor_rejection.json"
        )
        self.assertEqual(manifest_path, canonical_path)
        self.assertEqual(json.loads(manifest_path.read_text()), manifest)
        self.assertEqual(relocated_path.read_bytes(), rejection_bytes)
        self.assertEqual(json.loads(relocated_path.read_text()), rejection)

    def test_manifest_relocation_failure_preserves_canonical_rejection(
        self,
    ) -> None:
        rejection = {
            "experiment_id": "exp-relocation-failure",
            "members": [],
            "terminal_verdict": {
                "schema_version": "joulewise.cooldown_anchor_verdict.v1",
                "record_type": "cooldown_anchor_verdict",
                "decision": "fail_closed",
            },
        }
        canonical_path = write_experiment_rejection_verdict(
            self.runs_root, rejection
        )
        rejection_bytes = canonical_path.read_bytes()

        with mock.patch(
            "joulewise.bundle._claim_staged_json",
            side_effect=OSError("simulated relocation failure"),
        ):
            with self.assertRaisesRegex(OSError, "relocation failure"):
                write_experiment_manifest(
                    self.runs_root,
                    {
                        "experiment_id": "exp-relocation-failure",
                        "members": ["exp-relocation-failure__r1"],
                    },
                )

        self.assertEqual(canonical_path.read_bytes(), rejection_bytes)
        self.assertEqual(json.loads(canonical_path.read_text()), rejection)
        extra_files = [
            entry
            for entry in (self.runs_root / "experiments").rglob("*")
            if (
                entry.is_file()
                and entry != canonical_path
                and entry.name != ".custody.lock"
            )
        ]
        self.assertEqual(extra_files, [])

    def test_unparsable_canonical_artifact_fails_closed_without_replacement(
        self,
    ) -> None:
        experiments_dir = self.runs_root / "experiments"
        experiments_dir.mkdir(parents=True)
        canonical_path = experiments_dir / "corrupt-custody.json"
        corrupt_bytes = b'{"experiment_id":"corrupt-custody","members":['
        canonical_path.write_bytes(corrupt_bytes)

        with self.assertRaisesRegex(
            BundleError,
            rf"{re.escape(str(canonical_path))}.*unparsable JSON",
        ):
            write_experiment_manifest(
                self.runs_root,
                {
                    "experiment_id": "corrupt-custody",
                    "members": ["corrupt-custody__r1"],
                },
            )

        self.assertEqual(canonical_path.read_bytes(), corrupt_bytes)
        self.assertEqual(
            sorted(path.name for path in experiments_dir.glob("*.json")),
            ["corrupt-custody.json"],
        )

    def test_sixty_four_concurrent_rejections_claim_unique_complete_paths(
        self,
    ) -> None:
        rejection = {
            "experiment_id": "concurrent-claim",
            "members": [],
            "terminal_verdict": {
                "schema_version": "joulewise.cooldown_anchor_verdict.v1",
                "record_type": "cooldown_anchor_verdict",
                "decision": "fail_closed",
            },
        }

        with concurrent.futures.ThreadPoolExecutor(max_workers=64) as pool:
            paths = list(
                pool.map(
                    lambda _index: write_experiment_rejection_verdict(
                        self.runs_root, rejection
                    ),
                    range(64),
                )
            )

        self.assertEqual(len(paths), 64)
        self.assertEqual(len(set(paths)), 64)
        self.assertEqual(
            sum(
                path == self.runs_root / "experiments" / "concurrent-claim.json"
                for path in paths
            ),
            1,
        )
        for path in paths:
            self.assertEqual(json.loads(path.read_text()), rejection)

    def test_process_custody_lock_blocks_rejection_during_manifest_claim(
        self,
    ) -> None:
        manifest_child = r'''
import sys
import time
from pathlib import Path
from unittest import mock

import joulewise.bundle as bundle

runs_root = Path(sys.argv[1])
lock_held = Path(sys.argv[2])
release_lock = Path(sys.argv[3])
real_classify = bundle._existing_cooldown_anchor_rejection_payload
call_count = [0]

def pause_during_authoritative_inspection(path):
    result = real_classify(path)
    call_count[0] += 1
    if call_count[0] == 2:
        lock_held.write_text("ready\n")
        deadline = time.monotonic() + 15.0
        while not release_lock.exists():
            if time.monotonic() >= deadline:
                raise RuntimeError("timed out waiting to release custody lock")
            time.sleep(0.001)
    return result

with mock.patch.object(
    bundle,
    "_existing_cooldown_anchor_rejection_payload",
    side_effect=pause_during_authoritative_inspection,
):
    bundle.write_experiment_manifest(
        runs_root,
        {
            "experiment_id": "custody-race",
            "members": ["custody-race__r1"],
        },
    )
'''
        rejection_child = r'''
import sys
import time
from pathlib import Path

from joulewise.bundle import write_experiment_rejection_verdict

runs_root = Path(sys.argv[1])
attempt_started = Path(sys.argv[2])
attempt_started.write_text("ready\n")
write_experiment_rejection_verdict(
    runs_root,
    {
        "experiment_id": "custody-race",
        "members": [],
        "writer_index": 1,
        "terminal_verdict": {
            "schema_version": "joulewise.cooldown_anchor_verdict.v1",
            "record_type": "cooldown_anchor_verdict",
            "decision": "fail_closed",
        },
    },
)
'''
        lock_held = self.runs_root / "manifest-lock-held"
        release_lock = self.runs_root / "release-manifest-lock"
        attempt_started = self.runs_root / "rejection-attempt-started"
        manifest_process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                manifest_child,
                str(self.runs_root),
                str(lock_held),
                str(release_lock),
            ],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        rejection_process: subprocess.Popen[str] | None = None
        processes = [manifest_process]
        try:
            deadline = time.monotonic() + 15.0
            while not lock_held.exists() and manifest_process.poll() is None:
                if time.monotonic() >= deadline:
                    break
                time.sleep(0.001)
            self.assertTrue(
                lock_held.exists(),
                "manifest did not pause in its authoritative custody window",
            )

            rejection_process = subprocess.Popen(
                [
                    sys.executable,
                    "-c",
                    rejection_child,
                    str(self.runs_root),
                    str(attempt_started),
                ],
                cwd=REPO_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            processes.append(rejection_process)
            deadline = time.monotonic() + 15.0
            while (
                not attempt_started.exists()
                and rejection_process.poll() is None
            ):
                if time.monotonic() >= deadline:
                    break
                time.sleep(0.001)
            self.assertTrue(
                attempt_started.exists(),
                "rejection writer did not begin its custody claim",
            )
            with self.assertRaises(
                subprocess.TimeoutExpired,
                msg="rejection writer bypassed the held process custody lock",
            ):
                rejection_process.wait(timeout=1.0)

            release_lock.write_text("release\n")
            manifest_stdout, manifest_stderr = manifest_process.communicate(
                timeout=15
            )
            rejection_stdout, rejection_stderr = rejection_process.communicate(
                timeout=15
            )
            self.assertEqual(
                manifest_process.returncode,
                0,
                f"manifest child failed: {manifest_stdout}\n{manifest_stderr}",
            )
            self.assertEqual(
                rejection_process.returncode,
                0,
                f"rejection child failed: {rejection_stdout}\n{rejection_stderr}",
            )
        finally:
            release_lock.touch(exist_ok=True)
            for process in processes:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=5)

        experiments_dir = self.runs_root / "experiments"
        canonical_path = experiments_dir / "custody-race.json"
        self.assertEqual(
            json.loads(canonical_path.read_text()),
            {
                "experiment_id": "custody-race",
                "members": ["custody-race__r1"],
            },
        )
        rejection_paths = sorted(
            (experiments_dir / "rejections").glob(
                "custody-race__cooldown_anchor_rejection*.json"
            )
        )
        self.assertEqual(len(rejection_paths), 1)
        self.assertEqual(json.loads(rejection_paths[0].read_text())["writer_index"], 1)
        self.assertTrue((experiments_dir / ".custody.lock").is_file())
        self.assertNotIn(
            experiments_dir / ".custody.lock",
            set(experiments_dir.rglob("*.json")),
        )

    def test_exclusive_rejection_closes_raw_fd_when_fdopen_rejects_ownership(
        self,
    ) -> None:
        rejection = {
            "experiment_id": "fdopen-failure",
            "members": [],
            "terminal_verdict": {
                "schema_version": "joulewise.cooldown_anchor_verdict.v1",
                "record_type": "cooldown_anchor_verdict",
                "decision": "fail_closed",
            },
        }
        captured_fd: int | None = None

        def rejecting_fdopen(fd: int, *args, **kwargs):
            nonlocal captured_fd
            captured_fd = fd
            raise OSError("simulated fdopen ownership failure")

        try:
            with mock.patch(
                "joulewise.bundle.os.fdopen", side_effect=rejecting_fdopen
            ):
                with self.assertRaisesRegex(OSError, "ownership failure"):
                    write_experiment_rejection_verdict(self.runs_root, rejection)

            self.assertIsNotNone(captured_fd)
            with self.assertRaises(OSError):
                os.fstat(captured_fd)
            self.assertFalse(
                (self.runs_root / "experiments" / "fdopen-failure.json").exists()
            )
        finally:
            if captured_fd is not None:
                try:
                    os.close(captured_fd)
                except OSError:
                    pass

    def test_killed_exclusive_rejection_never_leaves_truncated_destination(
        self,
    ) -> None:
        marker_path = Path(self._tmp.name) / "partial-write-ready"
        rejection = {
            "experiment_id": "atomic-claim",
            "members": [],
            "terminal_verdict": {
                "schema_version": "joulewise.cooldown_anchor_verdict.v1",
                "record_type": "cooldown_anchor_verdict",
                "decision": "fail_closed",
            },
        }
        child = r'''
import os
import sys
import time
from pathlib import Path
from unittest import mock

from joulewise.bundle import write_experiment_rejection_verdict

runs_root = Path(sys.argv[1])
marker_path = Path(sys.argv[2])
real_fdopen = os.fdopen

class PartialWriteHandle:
    def __init__(self, fd, *args, **kwargs):
        self._handle = real_fdopen(fd, *args, **kwargs)

    def __enter__(self):
        self._handle.__enter__()
        return self

    def __exit__(self, *args):
        return self._handle.__exit__(*args)

    def write(self, payload):
        self._handle.write(payload[:17])
        self._handle.flush()
        os.fsync(self._handle.fileno())
        marker_path.write_text("ready\n")
        while True:
            time.sleep(60)

    def flush(self):
        return self._handle.flush()

    def fileno(self):
        return self._handle.fileno()

with mock.patch("joulewise.bundle.os.fdopen", side_effect=PartialWriteHandle):
    write_experiment_rejection_verdict(
        runs_root,
        {
            "experiment_id": "atomic-claim",
            "members": [],
            "terminal_verdict": {
                "schema_version": "joulewise.cooldown_anchor_verdict.v1",
                "record_type": "cooldown_anchor_verdict",
                "decision": "fail_closed",
            },
        },
    )
'''
        process = subprocess.Popen(
            [sys.executable, "-c", child, str(self.runs_root), str(marker_path)],
            cwd=REPO_ROOT,
        )
        self.addCleanup(
            lambda: process.kill() if process.poll() is None else None
        )
        for _ in range(500):
            if marker_path.exists() or process.poll() is not None:
                break
            time.sleep(0.01)
        self.assertTrue(marker_path.exists(), "child did not reach partial write")

        process.kill()
        process.wait(timeout=5)

        destination = self.runs_root / "experiments" / "atomic-claim.json"
        if destination.exists():
            self.assertEqual(json.loads(destination.read_text()), rejection)


if __name__ == "__main__":
    unittest.main()
