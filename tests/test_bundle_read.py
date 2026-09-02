"""Tests for the shared bundle read layer (Slice 2N.8; D-025, D-026, D-027).

The reader owns bundle parsing and interpretation policy for every consumer
(reducer, report, validate-bundle). Fixtures are assembled with the real
``RunBundleWriter`` under a ``FakeClock`` plus hand-authored artifacts, the
same way the reducer suite builds its bundles.
"""

from __future__ import annotations

import json
import hashlib
import tempfile
import unittest
from pathlib import Path

from joulewise.bundle import RunBundleWriter
from joulewise.bundle_read import (
    BundleReader,
    BundleReadError,
    Window,
    _marker_pair_problems,
)
from joulewise.cli import (
    _strict_budgeted_suite_prompt_count_problems,
    _strict_emitted_token_ids_problems,
    validate_bundle,
)
from joulewise.clock import FakeClock
from joulewise.interfaces import PowerSample, RuntimeEvent
from joulewise.schemas import (
    BenchmarkConfig,
    FailureReason,
    RunStatus,
    SummaryMetrics,
)
from joulewise.suite import (
    BLOCK_END,
    BLOCK_START,
    LEVEL_END,
    LEVEL_START,
    LEGACY_SUITE_SCHEMA_VERSION,
    SuiteManifest,
    canonical_effective_manifest,
    order_seed,
    realized_order,
    suite_manifest_sha256,
)
from joulewise.adapters.mock_runtime import MockRuntimeAdapter
from joulewise.provenance import prompt_token_ids_sha256, sha256_hex

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_local.json"
SUITE_CONFIG_PATH = REPO_ROOT / "configs" / "examples" / "mock_suite_local.json"
SUITE_MANIFEST_PATH = REPO_ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json"


def load_config(**overrides) -> BenchmarkConfig:
    data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
    for key, value in overrides.items():
        data[key] = value
    return BenchmarkConfig.from_mapping(data)


def load_suite_config(run_id: str) -> BenchmarkConfig:
    data = json.loads(SUITE_CONFIG_PATH.read_text())
    manifest = json.loads(SUITE_MANIFEST_PATH.read_text())
    data["run_id"] = run_id
    data["workload_profile"]["suite_manifest_ref"] = str(SUITE_MANIFEST_PATH)
    data["workload_profile"]["suite_manifest_sha256"] = suite_manifest_sha256(manifest)
    return BenchmarkConfig.from_mapping(data)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records))


def rewrite_suite_manifest_and_hashes(writer: RunBundleWriter, raw_manifest: dict) -> None:
    effective = canonical_effective_manifest(raw_manifest)
    manifest_hash = suite_manifest_sha256(effective)
    (writer.path / "suite_manifest.json").write_text(
        json.dumps(effective, indent=2, sort_keys=True) + "\n"
    )
    config = json.loads((writer.path / "config.json").read_text())
    config["workload_profile"]["suite_manifest_sha256"] = manifest_hash
    (writer.path / "config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n"
    )
    metadata = json.loads((writer.path / "metadata.json").read_text())
    metadata["config_sha256"] = hashlib.sha256(
        (writer.path / "config.json").read_bytes()
    ).hexdigest()
    metadata["suite"]["manifest_sha256"] = manifest_hash
    (writer.path / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    )


def suite_related(problems: list[str]) -> list[str]:
    needles = (
        "suite",
        "block_",
        "block ",
        "level_",
        "level ",
        "item_",
        "item ",
        "manifest item",
        "paired item",
    )
    return [problem for problem in problems if any(needle in problem for needle in needles)]


class ReaderTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs_root = Path(tmp.name) / "runs"
        self.clock = FakeClock(start=0.0)

    def make_bundle(self, run_id: str) -> RunBundleWriter:
        return RunBundleWriter.create(
            self.runs_root, load_config(run_id=run_id), self.clock
        )

    def add_event(
        self,
        writer: RunBundleWriter,
        event_type: str,
        phase: str,
        timestamp_s: float,
        *,
        metadata: dict | None = None,
    ) -> None:
        writer.append_event(
            RuntimeEvent(
                timestamp_s=timestamp_s,
                event_type=event_type,
                phase=phase,
                message=f"{event_type} {phase}",
                metadata=metadata or {},
            )
        )

    def write_metadata(self, writer: RunBundleWriter, rail_manifest: list[str]) -> None:
        writer.write_metadata(
            {"device": {"telemetry": "mock", "rail_manifest": rail_manifest}}
        )


class StrictAccessorTests(ReaderTestCase):
    def test_legacy_v1_suite_manifest_names_synthesized_cache_marker(self) -> None:
        writer = self.make_bundle("legacy-suite-manifest")
        legacy = json.loads(SUITE_MANIFEST_PATH.read_text())
        self.assertEqual(legacy["schema_version"], LEGACY_SUITE_SCHEMA_VERSION)
        writer.write_suite_manifest(canonical_effective_manifest(legacy))

        manifest = BundleReader(writer.path).suite_manifest()

        self.assertIsNotNone(manifest)
        assert manifest is not None
        self.assertEqual(
            manifest.execution_policy.cache_policy_verification,
            "declared_not_verified",
        )
        self.assertEqual(
            manifest.synthesized_fields,
            ("execution_policy.cache_policy_verification",),
        )

    def test_missing_config_is_structured_read_error(self) -> None:
        reader = BundleReader(self.runs_root / "does-not-exist")
        with self.assertRaises(BundleReadError) as ctx:
            reader.config()
        self.assertIn("config.json", str(ctx.exception))

    def test_corrupt_config_is_structured_read_error(self) -> None:
        writer = self.make_bundle("corrupt-config")
        (writer.path / "config.json").write_text("{not json")
        with self.assertRaises(BundleReadError) as ctx:
            BundleReader(writer.path).config()
        self.assertIn("not valid JSON", str(ctx.exception))

    def test_schema_invalid_config_is_structured_read_error(self) -> None:
        writer = self.make_bundle("schema-invalid-config")
        (writer.path / "config.json").write_text(json.dumps({"schema_version": "x"}))
        with self.assertRaises(BundleReadError) as ctx:
            BundleReader(writer.path).config()
        self.assertIn("does not re-validate", str(ctx.exception))

    def test_missing_metadata_is_structured_read_error(self) -> None:
        writer = self.make_bundle("no-metadata")
        with self.assertRaises(BundleReadError) as ctx:
            BundleReader(writer.path).metadata()
        self.assertIn("metadata.json", str(ctx.exception))

    def test_malformed_event_line_is_structured_read_error(self) -> None:
        writer = self.make_bundle("bad-events")
        (writer.path / "events.jsonl").write_text(
            '{"timestamp_s": 1.0, "event_type": "token", "phase": '
            '"measured_run", "message": "", "metadata": {}}\nnot json\n'
        )
        with self.assertRaises(BundleReadError) as ctx:
            BundleReader(writer.path).events()
        self.assertIn("line 2", str(ctx.exception))

    def test_bad_event_timestamps_are_structured_read_errors(self) -> None:
        # 2026-07-06 status review P1: nonnumeric, missing, bool, and
        # non-finite timestamps must become BundleReadError, never a raw
        # ValueError/TypeError from a float() cast downstream.
        cases = [
            (
                "nonnumeric",
                '{"timestamp_s": "not-a-number", "event_type": "token", '
                '"phase": "measured_run", "message": "", "metadata": {}}\n',
                "timestamp_s is not a finite number",
            ),
            (
                "missing-timestamp_s",
                '{"event_type": "token", "phase": "measured_run", '
                '"message": "", "metadata": {}}\n',
                "keys are",
            ),
            (
                "bool",
                '{"timestamp_s": true, "event_type": "token", '
                '"phase": "measured_run", "message": "", "metadata": {}}\n',
                "timestamp_s is not a finite number",
            ),
            (
                "nonfinite",
                '{"timestamp_s": Infinity, "event_type": "token", '
                '"phase": "measured_run", "message": "", "metadata": {}}\n',
                "timestamp_s is not a finite number",
            ),
            (
                "nan",
                '{"timestamp_s": NaN, "event_type": "token", '
                '"phase": "measured_run", "message": "", "metadata": {}}\n',
                "timestamp_s is not a finite number",
            ),
        ]
        for label, line, expected in cases:
            writer = self.make_bundle(f"bad-ts-{label}")
            (writer.path / "events.jsonl").write_text(line)
            with self.subTest(label=label):
                with self.assertRaises(BundleReadError) as ctx:
                    BundleReader(writer.path).events()
                self.assertIn(expected, str(ctx.exception))

    def test_valid_bundle_parses_config_and_metadata(self) -> None:
        writer = self.make_bundle("valid")
        self.write_metadata(writer, ["mock"])
        reader = BundleReader(writer.path)
        self.assertEqual(reader.config().run_id, "valid")
        self.assertEqual(reader.rail_manifest(), ["mock"])


class PhasePairingTests(ReaderTestCase):
    def test_unmatched_phase_markers_are_rejected(self) -> None:
        cases = (
            ("phase_start", "no paired phase_end"),
            ("phase_end", "no paired phase_start"),
        )
        for event_type, expected in cases:
            with self.subTest(event_type=event_type):
                writer = self.make_bundle(f"unmatched-{event_type}")
                self.add_event(writer, event_type, "decode", 1.0)

                with self.assertRaisesRegex(BundleReadError, expected):
                    BundleReader(writer.path).phase_windows()

    def test_reversed_phase_pair_is_rejected(self) -> None:
        writer = self.make_bundle("reversed-phase")
        self.add_event(writer, "phase_start", "decode", 2.0)
        self.add_event(writer, "phase_end", "decode", 1.0)

        with self.assertRaisesRegex(BundleReadError, "reversed"):
            BundleReader(writer.path).phase_windows()

    def test_same_source_overlapping_same_phase_windows_are_rejected(self) -> None:
        writer = self.make_bundle("overlapping-same-source-phase")
        first = {"node_id": "node-a", "node_role": "prefill"}
        second = {"node_id": "node-a", "node_role": "decode"}
        self.add_event(writer, "phase_start", "decode", 1.0, metadata=first)
        self.add_event(writer, "phase_start", "decode", 2.0, metadata=second)
        self.add_event(writer, "phase_end", "decode", 3.0, metadata=first)
        self.add_event(writer, "phase_end", "decode", 4.0, metadata=second)

        with self.assertRaisesRegex(BundleReadError, "same_source_phase_overlap"):
            BundleReader(writer.path).phase_windows()

    def test_parallel_sources_pair_and_filter_tokens_by_source(self) -> None:
        writer = self.make_bundle("parallel-node-phase")
        node_a = {"node_role": "decode", "node_identity": {"host": "node-a"}}
        node_b = {"node_role": "decode", "node_identity": {"host": "node-b"}}
        self.add_event(writer, "phase_start", "decode", 1.0, metadata=node_a)
        self.add_event(writer, "phase_end", "decode", 3.0, metadata=node_a)
        self.add_event(writer, "phase_start", "decode", 2.0, metadata=node_b)
        self.add_event(writer, "phase_end", "decode", 4.0, metadata=node_b)
        self.add_event(
            writer,
            "token",
            "decode",
            3.5,
            metadata={**node_a, "index": 0},
        )
        self.add_event(
            writer,
            "token",
            "decode",
            3.5,
            metadata={**node_b, "index": 1},
        )

        reader = BundleReader(writer.path)
        self.assertEqual(
            reader.phase_windows(),
            {"decode": [Window(1.0, 3.0), Window(2.0, 4.0)]},
        )
        self.assertEqual(reader.token_timestamps(), [3.5])

    def test_parallel_role_only_streams_pair_without_false_overlap(self) -> None:
        writer = self.make_bundle("parallel-role-only-phase")
        prefill_role = {"node_role": "prefill"}
        decode_role = {"node_role": "decode"}
        self.add_event(
            writer, "phase_start", "decode", 1.0, metadata=prefill_role
        )
        self.add_event(writer, "phase_end", "decode", 3.0, metadata=prefill_role)
        self.add_event(writer, "phase_start", "decode", 2.0, metadata=decode_role)
        self.add_event(writer, "phase_end", "decode", 4.0, metadata=decode_role)
        self.add_event(
            writer,
            "token",
            "decode",
            3.5,
            metadata={**prefill_role, "index": 0},
        )
        self.add_event(
            writer,
            "token",
            "decode",
            3.5,
            metadata={**decode_role, "index": 1},
        )

        reader = BundleReader(writer.path)
        self.assertEqual(
            reader.phase_windows(),
            {"decode": [Window(1.0, 3.0), Window(2.0, 4.0)]},
        )
        self.assertEqual(reader.token_timestamps(), [3.5])


class CompletionStateTests(ReaderTestCase):
    def test_bundle_without_summary_is_incomplete(self) -> None:
        writer = self.make_bundle("incomplete")
        self.assertFalse(BundleReader(writer.path).is_complete())

    def test_status_only_succeeded_summary_is_incomplete(self) -> None:
        writer = self.make_bundle("complete")
        (writer.path / "summary_metrics.json").write_text('{"status": "succeeded"}')
        self.assertFalse(BundleReader(writer.path).is_complete())

    def test_corrupt_summary_is_incomplete_and_tolerant_none(self) -> None:
        writer = self.make_bundle("corrupt-summary")
        (writer.path / "summary_metrics.json").write_text("{broken")
        reader = BundleReader(writer.path)
        self.assertFalse(reader.is_complete())
        self.assertIsNone(reader.raw_summary())

    def test_inter_token_throughput_must_be_null_or_finite(self) -> None:
        writer = self.make_bundle("nonfinite-inter-token-throughput")
        summary = SummaryMetrics(
            status=RunStatus.SUCCEEDED,
            energy_request_j=1.0,
            gross_energy_j=1.0,
        ).to_dict()
        summary["inter_token_throughput_tokens_s"] = float("inf")
        (writer.path / "summary_metrics.json").write_text(json.dumps(summary))

        problems = BundleReader(writer.path).problems()

        self.assertTrue(
            any(
                "inter_token_throughput_tokens_s is not null or finite"
                in problem
                for problem in problems
            ),
            problems,
        )


class ProblemCollectionTests(ReaderTestCase):
    def test_invalid_utf8_json_artifact_is_reported_not_raised(self) -> None:
        for artifact in ("config.json", "metadata.json", "summary_metrics.json"):
            with self.subTest(artifact=artifact):
                writer = self.make_bundle(f"invalid-utf8-{artifact}")
                writer.path.joinpath(artifact).write_bytes(b"\xff")

                problems = BundleReader(writer.path).problems()

                self.assertTrue(
                    any(artifact in problem and "not valid JSON" in problem for problem in problems),
                    problems,
                )


class PromptRealizationExpectationTests(ReaderTestCase):
    EXPECTED_HASH = prompt_token_ids_sha256([1, 2, 3])

    def make_prompt_bundle(
        self,
        run_id: str,
        *,
        expectation: bool = True,
        expected_count: int = 3,
        expected_hash: str | None = None,
        expected_domain: str = "joulewise.prompt_token_ids.v1",
        realized_count: int = 3,
        realized_hash: str | None = None,
        realized_domain: str = "joulewise.prompt_token_ids.v1",
        realized_text_hash: str | None = None,
        provenance_present: bool = True,
        tokenize_count: int | None = 3,
        prefill_count: int | None = 3,
        observed_prompt_count: int = 3,
    ) -> RunBundleWriter:
        data = json.loads(EXAMPLE_CONFIG_PATH.read_text())
        data["run_id"] = run_id
        data["workload_profile"]["prompt_tokens"] = None
        data["workload_profile"]["prompt_text"] = "test"
        data["workload_profile"]["output_tokens"] = 2
        if expectation:
            data["workload_profile"]["prompt_token_expectation"] = {
                "schema_version": "joulewise.prompt_token_expectation.v1",
                "token_hash_domain": expected_domain,
                "token_count": expected_count,
                "token_ids_sha256": expected_hash or self.EXPECTED_HASH,
            }
        writer = RunBundleWriter.create(
            self.runs_root,
            BenchmarkConfig.from_mapping(data),
            self.clock,
        )
        self.add_event(writer, "phase_start", "tokenize", 0.0)
        self.add_event(
            writer,
            "phase_end",
            "tokenize",
            0.1,
            metadata=(
                {"prompt_tokens": tokenize_count}
                if tokenize_count is not None
                else {}
            ),
        )
        self.add_event(
            writer,
            "phase_start",
            "prefill",
            0.1,
            metadata=(
                {"prompt_tokens": prefill_count}
                if prefill_count is not None
                else {}
            ),
        )
        self.add_event(writer, "phase_end", "prefill", 0.5)
        prompt = (
            {
                "token_hash_domain": realized_domain,
                "token_ids_sha256": realized_hash or self.EXPECTED_HASH,
                "realized_token_count": realized_count,
                "text_sha256": realized_text_hash or sha256_hex("test"),
            }
            if provenance_present
            else None
        )
        writer.write_metadata(
            {
                "device": {"telemetry": "mock", "rail_manifest": ["mock"]},
                "workload_observed": {
                    "token_count": observed_prompt_count + 2,
                    "output_token_count": 2,
                },
                "workload_provenance": {"prompt": prompt},
            }
        )
        writer.write_power_trace(
            [PowerSample(timestamp_s=0.0, power_w=1.0, source="mock", rail="mock")]
        )
        writer.write_summary(
            SummaryMetrics(
                status=RunStatus.SUCCEEDED,
                energy_request_j=1.0,
                gross_energy_j=1.0,
            )
        )
        writer.finalize()
        return writer

    @staticmethod
    def prompt_problems(writer: RunBundleWriter) -> list[str]:
        return [
            problem
            for problem in BundleReader(writer.path).problems()
            if problem.startswith("prompt_realization_")
        ]

    def test_coherent_count_mutation_is_one_mismatch(self) -> None:
        writer = self.make_prompt_bundle(
            "prompt-count-mismatch",
            realized_count=4,
            tokenize_count=4,
            prefill_count=4,
            observed_prompt_count=4,
        )

        problems = self.prompt_problems(writer)

        self.assertEqual(len(problems), 1, problems)
        self.assertIn("prompt_realization_mismatch", problems[0])
        self.assertIn("token_count", problems[0])
        self.assertNotIn("token_ids_sha256", problems[0])

    def test_equal_counts_different_hash_names_hash_mismatch(self) -> None:
        writer = self.make_prompt_bundle(
            "prompt-hash-mismatch", realized_hash="b" * 64
        )

        problems = self.prompt_problems(writer)

        self.assertEqual(len(problems), 1, problems)
        self.assertIn("prompt_realization_mismatch", problems[0])
        self.assertIn("token_ids_sha256", problems[0])
        self.assertNotIn("token_count", problems[0])

    def test_hash_comparison_binds_every_character_not_a_prefix(self) -> None:
        # Mutation guard: a prefix-only comparison would accept two hashes
        # that share their first 56 characters and differ only in the tail;
        # a case-folded comparison would accept an upper-case realized hash.
        # Neither may pass: the tail difference is a mismatch, and the
        # upper-case form is ill-formed evidence (the lowercase validator
        # refuses it before any comparison).
        cases = (
            ("a" * 56 + "b" * 8, "prompt_realization_mismatch"),
            ("A" * 64, "prompt_realization_evidence_missing"),
        )
        for index, (realized_hash, expected_code) in enumerate(cases):
            writer = self.make_prompt_bundle(
                f"prompt-hash-tail-mismatch-{index}",
                expected_hash="a" * 64,
                realized_hash=realized_hash,
            )

            problems = self.prompt_problems(writer)

            self.assertEqual(len(problems), 1, (realized_hash, problems))
            self.assertIn(expected_code, problems[0])
            self.assertIn("token_ids_sha256", problems[0])

    def test_count_and_hash_mutation_is_one_problem_naming_both(self) -> None:
        writer = self.make_prompt_bundle(
            "prompt-count-hash-mismatch",
            realized_count=4,
            realized_hash="b" * 64,
            tokenize_count=4,
            prefill_count=4,
            observed_prompt_count=4,
        )

        problems = self.prompt_problems(writer)

        self.assertEqual(len(problems), 1, problems)
        self.assertIn("token_count", problems[0])
        self.assertIn("token_ids_sha256", problems[0])

    def test_domain_mutation_is_mismatch(self) -> None:
        writer = self.make_prompt_bundle(
            "prompt-domain-mismatch", realized_domain="other.domain.v1"
        )

        problems = self.prompt_problems(writer)

        self.assertEqual(len(problems), 1, problems)
        self.assertIn("prompt_realization_mismatch", problems[0])
        self.assertIn("token_hash_domain", problems[0])

    def test_one_count_surface_mutation_is_evidence_inconsistent(self) -> None:
        writer = self.make_prompt_bundle(
            "prompt-count-inconsistent", tokenize_count=4
        )

        problems = self.prompt_problems(writer)

        self.assertEqual(len(problems), 1, problems)
        self.assertIn("prompt_realization_evidence_inconsistent", problems[0])
        self.assertIn("count surfaces disagree", problems[0])

    def test_changed_prompt_text_without_updated_hash_is_inconsistent(self) -> None:
        writer = self.make_prompt_bundle("prompt-text-inconsistent")
        config_path = writer.path / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["workload_profile"]["prompt_text"] = "changed prompt"
        config_path.write_text(json.dumps(config) + "\n", encoding="utf-8")

        problems = self.prompt_problems(writer)

        self.assertEqual(len(problems), 1, problems)
        self.assertIn("prompt_realization_evidence_inconsistent", problems[0])
        self.assertIn("text_sha256", problems[0])

    def test_missing_provenance_and_marker_are_never_a_pass(self) -> None:
        cases = (
            ("provenance-null", {"provenance_present": False}),
            ("tokenize-count-missing", {"tokenize_count": None}),
            ("prefill-count-missing", {"prefill_count": None}),
        )
        for label, changes in cases:
            with self.subTest(label=label):
                writer = self.make_prompt_bundle(label, **changes)
                problems = self.prompt_problems(writer)
                self.assertEqual(len(problems), 1, problems)
                self.assertIn("prompt_realization_evidence_missing", problems[0])

    def test_legacy_config_without_expectation_gets_zero_new_problems(self) -> None:
        writer = self.make_prompt_bundle("legacy-prompt", expectation=False)

        self.assertEqual(self.prompt_problems(writer), [])

    def test_real_validate_bundle_preserves_exact_named_refusal(self) -> None:
        writer = self.make_prompt_bundle(
            "validate-prompt-mismatch", realized_hash="d" * 64
        )
        before = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in writer.path.iterdir()
            if path.is_file()
        }

        problems = validate_bundle(writer.path)

        self.assertTrue(
            any(
                problem.startswith("prompt_realization_mismatch:")
                for problem in problems
            ),
            problems,
        )
        self.assertEqual(
            before,
            {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in writer.path.iterdir()
                if path.is_file()
            },
        )

    def test_mismatch_reaches_floor_and_analysis_admission_as_neither_branch(self) -> None:
        from joulewise.analysis_engine.inputs import _read_bundle
        from joulewise.floor_extraction import _evaluate_member

        writer = self.make_prompt_bundle(
            "consumer-prompt-mismatch", realized_hash="e" * 64
        )
        named_problems: list[str] = []

        def strict_validator(path: Path, strict: bool) -> list[str]:
            problems = validate_bundle(path, strict=strict)
            named_problems.extend(
                problem
                for problem in problems
                if problem.startswith("prompt_realization_")
            )
            return problems

        floor_member = _evaluate_member(
            slot="prefill-r1",
            bundle_id=writer.path.name,
            block_id=None,
            position=None,
            runs_root=writer.path.parent,
            metric="gross_energy_j",
            window_class="request",
            cooldowns={},
            hash_bundles=False,
            strict_validator=strict_validator,
        )
        raw_config = json.loads((writer.path / "config.json").read_text())
        analysis_evidence = _read_bundle(
            {},
            writer.path,
            writer.path.parent,
            raw_config,
            strict_validator,
        )

        self.assertTrue(
            any(
                problem.startswith("prompt_realization_mismatch:")
                for problem in named_problems
            ),
            named_problems,
        )
        self.assertIn("bundle_strict_invalid", floor_member.reasons)
        self.assertFalse(analysis_evidence.included)
        self.assertTrue(
            any(
                problem.startswith("prompt_realization_mismatch:")
                for problem in analysis_evidence.strict_problems
            ),
            analysis_evidence.strict_problems,
        )


class MeasuredWindowTests(ReaderTestCase):
    def test_markers_preferred_over_stage_boundaries(self) -> None:
        writer = self.make_bundle("markers")
        self.add_event(writer, "stage_started", "measured_run", 10.0)
        self.add_event(writer, "sampling_started", "measured_run", 13.0)
        self.add_event(writer, "sampling_stopped", "measured_run", 20.0)
        self.add_event(writer, "stage_completed", "measured_run", 22.0)
        window = BundleReader(writer.path).measured_window()
        self.assertEqual((window.start_s, window.end_s), (13.0, 20.0))

    def test_stage_boundaries_are_the_pre_2n_fallback(self) -> None:
        writer = self.make_bundle("stage-fallback")
        self.add_event(writer, "stage_started", "measured_run", 10.0)
        self.add_event(writer, "stage_completed", "measured_run", 22.0)
        window = BundleReader(writer.path).measured_window()
        self.assertEqual((window.start_s, window.end_s), (10.0, 22.0))

    def test_no_window_when_events_missing(self) -> None:
        writer = self.make_bundle("no-window")
        self.assertIsNone(BundleReader(writer.path).measured_window())


class RuntimeCleanupQualityTests(ReaderTestCase):
    def add_cleanup(self, writer: RunBundleWriter, value: object) -> None:
        writer.append_event(
            RuntimeEvent(
                timestamp_s=self.clock.now(),
                event_type="stage_completed",
                phase="cleanup",
                message="cleanup complete",
                metadata={"cleanup_ok": value},
            )
        )

    def test_runtime_cleanup_ok_is_none_without_boolean_evidence(self) -> None:
        writer = self.make_bundle("cleanup-unknown")
        self.assertIsNone(BundleReader(writer.path).runtime_cleanup_ok())
        self.add_cleanup(writer, True)
        self.add_cleanup(writer, "true")
        self.assertIsNone(BundleReader(writer.path).runtime_cleanup_ok())

    def test_runtime_cleanup_ok_is_true_when_all_completions_are_true(self) -> None:
        writer = self.make_bundle("cleanup-true")
        self.add_cleanup(writer, True)
        self.add_cleanup(writer, True)
        self.assertIs(BundleReader(writer.path).runtime_cleanup_ok(), True)

    def test_runtime_cleanup_ok_is_false_when_any_completion_is_false(self) -> None:
        writer = self.make_bundle("cleanup-false")
        self.add_cleanup(writer, True)
        self.add_cleanup(writer, False)
        self.add_cleanup(writer, "damaged")
        self.assertIs(BundleReader(writer.path).runtime_cleanup_ok(), False)


class RailAlignmentTests(ReaderTestCase):
    """D-027: per-rail rows for one sample instant must share one timestamp."""

    def _write_trace(self, writer: RunBundleWriter, samples: list[PowerSample]) -> None:
        writer.write_power_trace(samples)

    def test_aligned_multi_rail_sums_exactly(self) -> None:
        writer = self.make_bundle("aligned")
        self.write_metadata(writer, ["a", "b"])
        samples = []
        for t in (0.0, 1.0, 2.0):
            samples.append(PowerSample(timestamp_s=t, power_w=3.0, source="m", rail="a"))
            samples.append(PowerSample(timestamp_s=t, power_w=4.0, source="m", rail="b"))
        self._write_trace(writer, samples)
        curve = BundleReader(writer.path).summed_curve()
        self.assertEqual([point.t for point in curve], [0.0, 1.0, 2.0])
        for point in curve:
            self.assertAlmostEqual(point.power_w, 7.0, places=9)

    def test_skewed_multi_rail_is_structured_failure_naming_the_gap(self) -> None:
        writer = self.make_bundle("skewed")
        self.write_metadata(writer, ["a", "b"])
        samples = [
            PowerSample(timestamp_s=0.0, power_w=3.0, source="m", rail="a"),
            PowerSample(timestamp_s=0.001, power_w=4.0, source="m", rail="b"),
            PowerSample(timestamp_s=1.0, power_w=3.0, source="m", rail="a"),
            PowerSample(timestamp_s=1.001, power_w=4.0, source="m", rail="b"),
        ]
        self._write_trace(writer, samples)
        with self.assertRaises(BundleReadError) as ctx:
            BundleReader(writer.path).summed_curve()
        message = str(ctx.exception)
        self.assertIn("misaligned", message)
        self.assertIn("D-027", message)
        self.assertIn("'b'", message)  # the missing rail at the first timestamp

    def test_single_rail_never_misaligns(self) -> None:
        writer = self.make_bundle("single-rail")
        self.write_metadata(writer, ["mock"])
        self._write_trace(
            writer,
            [
                PowerSample(timestamp_s=0.0, power_w=5.0, source="m", rail="mock"),
                PowerSample(timestamp_s=1.0, power_w=5.0, source="m", rail="mock"),
            ],
        )
        curve = BundleReader(writer.path).summed_curve()
        self.assertEqual(len(curve), 2)

    def test_empty_manifest_yields_empty_curve_no_fallback(self) -> None:
        # 2N.7: no consumer may invent a fallback summation policy.
        writer = self.make_bundle("empty-manifest")
        self.write_metadata(writer, [])
        self._write_trace(
            writer,
            [
                PowerSample(timestamp_s=0.0, power_w=5.0, source="m", rail="mock"),
                PowerSample(timestamp_s=1.0, power_w=5.0, source="m", rail="mock"),
            ],
        )
        self.assertEqual(BundleReader(writer.path).summed_curve(), [])

    def test_non_manifest_rail_ignored(self) -> None:
        writer = self.make_bundle("extra-rail")
        self.write_metadata(writer, ["a"])
        self._write_trace(
            writer,
            [
                PowerSample(timestamp_s=0.0, power_w=3.0, source="m", rail="a"),
                PowerSample(timestamp_s=0.5, power_w=99.0, source="m", rail="c"),
                PowerSample(timestamp_s=1.0, power_w=3.0, source="m", rail="a"),
            ],
        )
        curve = BundleReader(writer.path).summed_curve()
        self.assertEqual([point.t for point in curve], [0.0, 1.0])


class ProblemsParityTests(ReaderTestCase):
    """BundleReader.problems is the validate-bundle policy (one home, D-025)."""

    def test_problems_matches_cli_validate_bundle(self) -> None:
        from joulewise.cli import validate_bundle

        writer = self.make_bundle("parity")
        # Structurally broken on purpose: no metadata/summary yet.
        reader_problems = BundleReader(writer.path).problems()
        self.assertEqual(reader_problems, validate_bundle(writer.path))
        self.assertTrue(
            any("metadata.json" in problem for problem in reader_problems)
        )

    def test_pre_suite_bundle_problem_list_is_exact(self) -> None:
        writer = self.make_bundle("pre-suite-problems")
        self.assertEqual(
            BundleReader(writer.path).problems(),
            [
                "missing required artifact: metadata.json",
                "missing required artifact: summary_metrics.json",
                "events.jsonl has no event records",
            ],
        )


class SuiteReaderTests(ReaderTestCase):
    def make_suite_bundle(
        self,
        run_id: str = "suite-reader",
        *,
        order_policy: str = "manifest_order",
        order_row: int | None = None,
    ) -> RunBundleWriter:
        raw_manifest = json.loads(SUITE_MANIFEST_PATH.read_text())
        raw_manifest["execution_policy"]["order_policy"] = order_policy
        effective = canonical_effective_manifest(raw_manifest)
        manifest = SuiteManifest.from_mapping(raw_manifest)
        manifest_hash = suite_manifest_sha256(effective)
        data = json.loads(SUITE_CONFIG_PATH.read_text())
        data["run_id"] = run_id
        data["workload_profile"]["suite_manifest_ref"] = str(SUITE_MANIFEST_PATH)
        data["workload_profile"]["suite_manifest_sha256"] = manifest_hash
        config = BenchmarkConfig.from_mapping(data)
        writer = RunBundleWriter.create(self.runs_root, config, self.clock)
        derived_order_seed = order_seed(
            manifest.suite_seed,
            manifest.execution_policy.order_policy,
            order_row or 0,
        )
        writer.write_suite_manifest(effective)
        writer.append_event(
            RuntimeEvent(0.0, "sampling_started", "measured_run", "", {})
        )
        runtime = MockRuntimeAdapter(FakeClock(start=1.0))
        runtime_result = runtime.run_suite(
            config,
            manifest,
            order_seed=derived_order_seed,
            order_row=order_row,
        )
        for event in runtime_result.events:
            writer.append_event(event)
        for name, text in runtime_result.output_artifacts.items():
            writer.write_output(name, text)
        writer.append_event(
            RuntimeEvent(10.0, "sampling_stopped", "measured_run", "", {})
        )
        writer.write_metadata(
            {
                "device": {"telemetry": "mock", "rail_manifest": ["mock"]},
                "suite": {
                    "suite_id": manifest.suite_id,
                    "suite_profile": manifest.suite_profile,
                    "suite_revision": manifest.suite_revision,
                    "manifest_sha256": manifest_hash,
                    "source_file_sha256": "0" * 64,
                    "item_count": len(manifest.items),
                    "order_policy": manifest.execution_policy.order_policy,
                    "order_seed": derived_order_seed,
                    **({} if order_row is None else {"order_row": order_row}),
                },
            }
        )
        writer.append_event(RuntimeEvent(11.0, "run_finalized", "run", "", {}))
        (writer.path / "summary_metrics.json").write_text(
            json.dumps(
                {
                    "status": "failed",
                    "failure_reason": "unknown_error",
                    "failure_message": "synthetic validation fixture",
                }
            )
            + "\n"
        )
        return writer

    def test_suite_accessors_pair_items_fifo_and_levels_per_block(self) -> None:
        writer = self.make_suite_bundle()
        reader = BundleReader(writer.path)
        items = reader.item_windows()
        self.assertEqual([item.item_index for item in items], list(range(5)))
        self.assertEqual(items[3].item_id, items[4].item_id)
        self.assertIn(("block_a", "level_1"), reader.level_windows())
        self.assertIn(("block_b", "level_1"), reader.level_windows())
        self.assertEqual(reader.problems(), [])

    def test_rotated_suite_bundle_records_and_validates_realized_order(self) -> None:
        writer = self.make_suite_bundle(
            "suite-rotated",
            order_policy="block_round_robin_v1",
            order_row=1,
        )
        raw_manifest = json.loads((writer.path / "suite_manifest.json").read_text())
        manifest = SuiteManifest.from_mapping(raw_manifest)
        expected = [entry.item_index for entry in realized_order(manifest, order_row=1)]
        events = read_jsonl(writer.path / "events.jsonl")
        starts = [event for event in events if event["event_type"] == "item_start"]
        records = read_jsonl(writer.path / "outputs" / "suite_items.jsonl")
        metadata = json.loads((writer.path / "metadata.json").read_text())

        self.assertEqual([event["metadata"]["item_index"] for event in starts], expected)
        self.assertEqual([event["metadata"]["position"] for event in starts], list(range(5)))
        self.assertEqual([record["item_index"] for record in records], expected)
        self.assertEqual([record["position"] for record in records], list(range(5)))
        self.assertEqual(metadata["suite"]["order_policy"], "block_round_robin_v1")
        self.assertEqual(metadata["suite"]["order_row"], 1)
        self.assertEqual(BundleReader(writer.path).problems(), [])

    def test_rotation_requires_order_row(self) -> None:
        writer = self.make_suite_bundle(
            "suite-missing-order-row",
            order_policy="block_round_robin_v1",
            order_row=1,
        )
        metadata = json.loads((writer.path / "metadata.json").read_text())
        del metadata["suite"]["order_row"]
        (writer.path / "metadata.json").write_text(json.dumps(metadata, sort_keys=True) + "\n")
        events = read_jsonl(writer.path / "events.jsonl")
        for event in events:
            if event["event_type"] == "suite_start":
                event["metadata"].pop("order_row", None)
        write_jsonl(writer.path / "events.jsonl", events)

        problems = BundleReader(writer.path).problems()

        self.assertTrue(any("order_row is required" in problem for problem in problems), problems)

    def test_rotation_rejects_order_seed_that_does_not_match_order_row(self) -> None:
        writer = self.make_suite_bundle(
            "suite-wrong-derived-order-seed",
            order_policy="block_round_robin_v1",
            order_row=1,
        )
        metadata = json.loads((writer.path / "metadata.json").read_text())
        metadata["suite"]["order_seed"] = "deadbeef"
        (writer.path / "metadata.json").write_text(json.dumps(metadata, sort_keys=True) + "\n")
        events = read_jsonl(writer.path / "events.jsonl")
        for event in events:
            if event["event_type"] == "suite_start":
                event["metadata"]["order_seed"] = "deadbeef"
        write_jsonl(writer.path / "events.jsonl", events)

        problems = BundleReader(writer.path).problems()

        self.assertTrue(
            any("does not match derived order seed" in problem for problem in problems),
            problems,
        )
        self.assertFalse(
            any("metadata.suite.order_seed mismatch" in problem for problem in problems),
            problems,
        )

    def test_manifest_order_without_order_row_does_not_recompute_legacy_order_seed(self) -> None:
        writer = self.make_suite_bundle("suite-legacy-order-seed", order_row=None)
        legacy_order_seed = order_seed("mock-suite-seed", "manifest_order", 5)
        metadata = json.loads((writer.path / "metadata.json").read_text())
        metadata["suite"]["order_seed"] = legacy_order_seed
        (writer.path / "metadata.json").write_text(json.dumps(metadata, sort_keys=True) + "\n")
        events = read_jsonl(writer.path / "events.jsonl")
        for event in events:
            if event["event_type"] == "suite_start":
                event["metadata"]["order_seed"] = legacy_order_seed
        write_jsonl(writer.path / "events.jsonl", events)

        self.assertEqual(BundleReader(writer.path).problems(), [])

    def test_rotation_rejects_wrong_realized_order_prev_item_and_positions(self) -> None:
        def wrong_order(starts: list[dict]) -> None:
            starts[0]["metadata"], starts[-1]["metadata"] = (
                starts[-1]["metadata"],
                starts[0]["metadata"],
            )

        def wrong_prev(starts: list[dict]) -> None:
            starts[1]["metadata"]["prev_item"] = "wrong"

        def duplicate_position(starts: list[dict]) -> None:
            starts[1]["metadata"]["position"] = 0

        mutations = {
            "wrong-order": wrong_order,
            "wrong-prev": wrong_prev,
            "duplicate-position": duplicate_position,
        }
        expected_needles = {
            "wrong-order": "realized item_start order mismatch",
            "wrong-prev": "prev_item mismatch",
            "duplicate-position": "position is duplicated",
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                writer = self.make_suite_bundle(
                    f"suite-{name}",
                    order_policy="block_round_robin_v1",
                    order_row=1,
                )
                events = read_jsonl(writer.path / "events.jsonl")
                starts = [event for event in events if event["event_type"] == "item_start"]
                mutate(starts)
                write_jsonl(writer.path / "events.jsonl", events)

                problems = BundleReader(writer.path).problems()

                self.assertTrue(
                    any(expected_needles[name] in problem for problem in problems),
                    problems,
                )

    def test_validate_bundle_skips_missing_manifest_for_unreadable_manifest_failed_suite(self) -> None:
        writer = RunBundleWriter.create(
            self.runs_root, load_suite_config("suite-failed-before-prepare"), self.clock
        )
        config = json.loads((writer.path / "config.json").read_text())
        config["workload_profile"]["suite_manifest_ref"] = "/no/such/unreadable-suite.json"
        (writer.path / "config.json").write_text(json.dumps(config, sort_keys=True) + "\n")
        writer.write_metadata({"device": {"telemetry": "mock", "rail_manifest": ["mock"]}})
        writer.append_event(RuntimeEvent(1.0, "run_finalized", "run", "", {}))
        (writer.path / "summary_metrics.json").write_text(
            json.dumps(
                {
                    "status": RunStatus.FAILED.value,
                    "failure_reason": FailureReason.UNKNOWN_ERROR.value,
                    "failure_message": "failed before prepare wrote suite_manifest.json",
                }
            )
            + "\n"
        )
        self.assertEqual(suite_related(validate_bundle(writer.path)), [])

    def test_validate_bundle_skips_missing_manifest_for_unsupported_no_run_suite(self) -> None:
        writer = RunBundleWriter.create(
            self.runs_root, load_suite_config("suite-unsupported-before-prepare"), self.clock
        )
        writer.write_metadata({"device": {"telemetry": "mock", "rail_manifest": ["mock"]}})
        writer.append_event(RuntimeEvent(1.0, "run_finalized", "run", "", {}))
        (writer.path / "summary_metrics.json").write_text(
            json.dumps(
                {
                    "status": RunStatus.UNSUPPORTED.value,
                    "failure_reason": FailureReason.UNSUPPORTED_WORKLOAD.value,
                    "failure_message": "runtime adapter does not support suite workloads",
                }
            )
            + "\n"
        )
        self.assertEqual(suite_related(validate_bundle(writer.path)), [])

    def test_unpaired_item_start_is_skipped_by_accessor_but_reported(self) -> None:
        writer = self.make_suite_bundle("suite-unpaired")
        writer.append_event(
            RuntimeEvent(
                9.0,
                "item_start",
                "suite",
                "",
                {"item_id": "dangling", "item_index": 99},
            )
        )
        reader = BundleReader(writer.path)
        self.assertNotIn(99, [item.item_index for item in reader.item_windows()])
        self.assertTrue(
            any("has no paired item_end" in problem for problem in reader.problems())
        )

    def test_reordered_sentinel_item_ends_pair_by_index_in_accessor(self) -> None:
        writer = self.make_suite_bundle("suite-reordered-sentinel-ends")
        events_path = writer.path / "events.jsonl"
        events = read_jsonl(events_path)
        sentinel = [
            event
            for event in events
            if event["event_type"] in {"item_start", "item_end"}
            and event["metadata"].get("item_id") == "mock_sentinel_repeat"
        ]
        self.assertEqual(
            [(event["event_type"], event["metadata"]["item_index"]) for event in sentinel],
            [("item_start", 3), ("item_end", 3), ("item_start", 4), ("item_end", 4)],
        )
        start3, end3, start4, end4 = sentinel
        start4["timestamp_s"] = start3["timestamp_s"] + 0.001
        end4["timestamp_s"] = start4["timestamp_s"] + 0.001
        end3["timestamp_s"] = end4["timestamp_s"] + 0.001
        replacement = [start3, start4, end4, end3]
        replaced = 0
        reordered: list[dict] = []
        for event in events:
            if (
                event["event_type"] in {"item_start", "item_end"}
                and event["metadata"].get("item_id") == "mock_sentinel_repeat"
            ):
                if replaced == 0:
                    reordered.extend(replacement)
                replaced += 1
                continue
            reordered.append(event)
        write_jsonl(events_path, reordered)

        sentinel_windows = [
            item
            for item in BundleReader(writer.path).item_windows()
            if item.item_id == "mock_sentinel_repeat"
        ]

        self.assertEqual([item.item_index for item in sentinel_windows], [3, 4])
        self.assertAlmostEqual(sentinel_windows[3 - 3].window.end_s, end3["timestamp_s"])
        self.assertAlmostEqual(sentinel_windows[4 - 3].window.end_s, end4["timestamp_s"])

    def test_inconsistent_item_index_pairing_is_reported(self) -> None:
        writer = self.make_suite_bundle("suite-item-index-mismatch")
        events_path = writer.path / "events.jsonl"
        events = read_jsonl(events_path)
        for event in events:
            if event["event_type"] == "item_end" and event["metadata"].get("item_index") == 0:
                event["metadata"]["item_index"] = 99
                break
        write_jsonl(events_path, events)
        problems = BundleReader(writer.path).problems()
        self.assertTrue(
            any("start item_index 0, end item_index 99" in problem for problem in problems),
            problems,
        )

    def test_keyed_marker_pairing_reports_count_mismatch(self) -> None:
        problems = _marker_pair_problems(
            [
                {"event_type": BLOCK_START, "metadata": {"block_id": "A", "block_index": 0}},
            ],
            BLOCK_START,
            BLOCK_END,
            "block_id",
        )
        self.assertTrue(any("count mismatch" in problem for problem in problems), problems)

    def test_keyed_marker_pairing_reports_interleaved_lifo_violation(self) -> None:
        problems = _marker_pair_problems(
            [
                {"event_type": BLOCK_START, "metadata": {"block_id": "A", "block_index": 0}},
                {"event_type": BLOCK_START, "metadata": {"block_id": "B", "block_index": 1}},
                {"event_type": BLOCK_END, "metadata": {"block_id": "A", "block_index": 0}},
                {"event_type": BLOCK_END, "metadata": {"block_id": "B", "block_index": 1}},
            ],
            BLOCK_START,
            BLOCK_END,
            "block_id",
        )
        self.assertTrue(any("closes while block_start for 'B' is still open" in p for p in problems), problems)

    def test_keyed_marker_pairing_reports_missing_required_metadata(self) -> None:
        problems = _marker_pair_problems(
            [
                {"event_type": LEVEL_START, "metadata": {}},
                {"event_type": LEVEL_END, "metadata": {}},
            ],
            LEVEL_START,
            LEVEL_END,
            "level_id",
        )
        self.assertTrue(any("level_start marker metadata.level_id is missing" in p for p in problems), problems)
        self.assertTrue(any("level_end marker metadata.level_index is missing" in p for p in problems), problems)

    def test_illegal_status_and_underrun_guard_are_validation_errors(self) -> None:
        writer = self.make_suite_bundle("suite-illegal-status")
        events_path = writer.path / "events.jsonl"
        text = events_path.read_text()
        text = text.replace('"status": "succeeded"', '"status": "below_floor"', 1)
        text = text.replace('"emitted_tokens": 3', '"emitted_tokens": 2', 1)
        events_path.write_text(text)
        problems = BundleReader(writer.path).problems()
        self.assertTrue(any("runtime-assignable" in problem for problem in problems))

    def test_excluded_from_claim_status_is_validation_error(self) -> None:
        writer = self.make_suite_bundle("suite-excluded-status")
        events_path = writer.path / "events.jsonl"
        events_path.write_text(
            events_path.read_text().replace(
                '"status": "succeeded"', '"status": "excluded_from_claim"', 1
            )
        )
        self.assertTrue(
            any("runtime-assignable" in problem for problem in BundleReader(writer.path).problems())
        )

    def test_summary_suite_item_status_must_be_reducer_assignable(self) -> None:
        writer = self.make_suite_bundle("suite-summary-illegal-status")
        summary = json.loads((writer.path / "summary_metrics.json").read_text())
        summary["suite_metrics"] = {
            "items": [{"item_index": 0, "status": "excluded_from_claim"}]
        }
        (writer.path / "summary_metrics.json").write_text(json.dumps(summary) + "\n")
        problems = BundleReader(writer.path).problems()
        self.assertTrue(
            any("suite_metrics.items[0].status is not reducer-assignable" in p for p in problems),
            problems,
        )

    def test_summary_suite_status_counts_must_be_reducer_assignable(self) -> None:
        writer = self.make_suite_bundle("suite-summary-counts-illegal-status")
        summary = json.loads((writer.path / "summary_metrics.json").read_text())
        summary["suite_metrics"] = {
            "status_counts": {"excluded_from_claim": 1},
            "items": [],
        }
        (writer.path / "summary_metrics.json").write_text(json.dumps(summary) + "\n")
        problems = BundleReader(writer.path).problems()
        self.assertTrue(
            any("suite_metrics.status_counts contains non-reducer-assignable" in p for p in problems),
            problems,
        )

    def test_summary_block_status_counts_must_be_reducer_assignable(self) -> None:
        writer = self.make_suite_bundle("suite-summary-block-counts-illegal-status")
        summary = json.loads((writer.path / "summary_metrics.json").read_text())
        summary["suite_metrics"] = {
            "blocks": [{"group_id": "block_a", "status_counts": {"excluded_from_claim": 1}}],
            "items": [],
        }
        (writer.path / "summary_metrics.json").write_text(json.dumps(summary) + "\n")
        problems = BundleReader(writer.path).problems()
        self.assertTrue(
            any("suite_metrics.blocks[0].status_counts contains non-reducer-assignable" in p for p in problems),
            problems,
        )

    def test_summary_level_status_counts_must_be_reducer_assignable(self) -> None:
        writer = self.make_suite_bundle("suite-summary-level-counts-illegal-status")
        summary = json.loads((writer.path / "summary_metrics.json").read_text())
        summary["suite_metrics"] = {
            "levels": [{"group_id": "block_a/level_1", "status_counts": {"excluded_from_claim": 1}}],
            "items": [],
        }
        (writer.path / "summary_metrics.json").write_text(json.dumps(summary) + "\n")
        problems = BundleReader(writer.path).problems()
        self.assertTrue(
            any("suite_metrics.levels[0].status_counts contains non-reducer-assignable" in p for p in problems),
            problems,
        )

    def test_fixed_budget_succeeded_underrun_is_validation_error(self) -> None:
        writer = self.make_suite_bundle("suite-underrun")
        events_path = writer.path / "events.jsonl"
        events_path.write_text(
            events_path.read_text().replace('"emitted_tokens": 3', '"emitted_tokens": 2', 1)
        )
        self.assertTrue(
            any("fixed_budget_exact item succeeded" in problem for problem in BundleReader(writer.path).problems())
        )

    def test_missing_suite_marker_is_validation_error(self) -> None:
        writer = self.make_suite_bundle("suite-missing-marker")
        events_path = writer.path / "events.jsonl"
        lines = [
            line for line in events_path.read_text().splitlines()
            if '"event_type": "suite_start"' not in line
        ]
        events_path.write_text("\n".join(lines) + "\n")
        self.assertTrue(
            any("suite_start" in problem or "suite markers" in problem for problem in BundleReader(writer.path).problems())
        )

    def test_non_monotonic_item_index_is_validation_error(self) -> None:
        writer = self.make_suite_bundle("suite-nonmonotonic")
        events_path = writer.path / "events.jsonl"
        text = events_path.read_text()
        first = text.find('"event_type": "item_start"')
        prefix, suffix = text[:first], text[first:]
        suffix = suffix.replace('"item_index": 0', '"item_index": 99', 1)
        events_path.write_text(prefix + suffix)
        self.assertTrue(
            any(
                "realized item_start order mismatch" in problem
                for problem in BundleReader(writer.path).problems()
            )
        )

    def test_metadata_suite_block_is_validated(self) -> None:
        writer = self.make_suite_bundle("suite-metadata-validation")
        metadata = json.loads((writer.path / "metadata.json").read_text())
        metadata["suite"].pop("suite_revision")
        metadata["suite"]["source_file_sha256"] = "not-a-sha"
        metadata["suite"]["item_count"] = 4
        metadata["suite"]["order_seed"] = "wrong-seed"
        (writer.path / "metadata.json").write_text(json.dumps(metadata, sort_keys=True) + "\n")
        problems = BundleReader(writer.path).problems()
        self.assertTrue(any("metadata.suite.suite_revision is missing" in p for p in problems), problems)
        self.assertTrue(any("source_file_sha256 is not a 64-character hex string" in p for p in problems), problems)
        self.assertTrue(any("metadata.suite.item_count mismatch" in p for p in problems), problems)
        self.assertTrue(any("metadata.suite.order_seed mismatch" in p for p in problems), problems)

    def test_suite_end_arithmetic_must_match_paired_item_windows(self) -> None:
        writer = self.make_suite_bundle("suite-end-arithmetic")
        events_path = writer.path / "events.jsonl"
        events = read_jsonl(events_path)
        for event in events:
            if event["event_type"] == "suite_end":
                event["metadata"]["items_executed"] = 4
                event["metadata"]["status_counts"] = {"succeeded": 4}
                break
        write_jsonl(events_path, events)
        problems = BundleReader(writer.path).problems()
        self.assertTrue(any("suite_end.metadata.items_executed mismatch" in p for p in problems), problems)
        self.assertTrue(any("suite_end.metadata.status_counts mismatch" in p for p in problems), problems)

    def test_manifest_declared_blocks_and_levels_require_paired_markers(self) -> None:
        writer = self.make_suite_bundle("suite-missing-group-markers")
        events_path = writer.path / "events.jsonl"
        events = [
            event
            for event in read_jsonl(events_path)
            if event["event_type"] not in {BLOCK_START, BLOCK_END, LEVEL_START, LEVEL_END}
        ]
        write_jsonl(events_path, events)

        problems = BundleReader(writer.path).problems()

        self.assertTrue(
            any("manifest block_id 'block_a' is missing paired block markers" in p for p in problems),
            problems,
        )
        self.assertTrue(
            any("manifest level grouping ('block_a', 'level_1') is missing paired level markers" in p for p in problems),
            problems,
        )

    def test_ids_native_suite_item_hash_mismatch_from_output_is_validation_error(self) -> None:
        writer = self.make_suite_bundle("suite-ids-output-mismatch")
        output_path = writer.path / "outputs" / "suite_items.jsonl"
        records = read_jsonl(output_path)
        for record in records:
            if record["item_id"] == "mock_item_002":
                record["prompt"]["token_ids_sha256"] = "0" * 64
                break
        write_jsonl(output_path, records)

        problems = BundleReader(writer.path).problems()

        self.assertTrue(
            any("prompt.token_ids_sha256 mismatch for ids-native" in p and "actual '0000" in p for p in problems),
            problems,
        )

    def test_ids_native_suite_item_hash_mismatch_from_manifest_is_validation_error(self) -> None:
        writer = self.make_suite_bundle("suite-ids-manifest-mismatch")
        manifest_path = writer.path / "suite_manifest.json"
        raw_manifest = json.loads(manifest_path.read_text())
        for item in raw_manifest["items"]:
            if item["item_id"] == "mock_item_002":
                item["source"]["prompt_token_ids"] = [6, 7, 8, 9]
                break
        manifest_path.write_text(json.dumps(raw_manifest, indent=2, sort_keys=True) + "\n")
        new_hash = suite_manifest_sha256(canonical_effective_manifest(raw_manifest))
        config = json.loads((writer.path / "config.json").read_text())
        config["workload_profile"]["suite_manifest_sha256"] = new_hash
        (writer.path / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
        metadata = json.loads((writer.path / "metadata.json").read_text())
        metadata["suite"]["manifest_sha256"] = new_hash
        (writer.path / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")

        problems = BundleReader(writer.path).problems()

        self.assertTrue(
            any(
                "prompt.token_ids_sha256 mismatch for ids-native" in p
                and prompt_token_ids_sha256([6, 7, 8, 9]) in p
                for p in problems
            ),
            problems,
        )

    def test_text_suite_item_token_domain_hash_mismatch_is_validation_error(self) -> None:
        writer = self.make_suite_bundle("suite-text-token-domain-mismatch")
        manifest_path = writer.path / "suite_manifest.json"
        raw_manifest = json.loads(manifest_path.read_text())
        for item in raw_manifest["items"]:
            if item["item_id"] == "mock_item_003":
                item["source"]["source_sha256"] = sha256_hex("unrelated source")
                break
        rewrite_suite_manifest_and_hashes(writer, raw_manifest)

        problems = BundleReader(writer.path).problems()

        self.assertTrue(
            any("prompt.token_ids_sha256 mismatch for text manifest" in p for p in problems),
            problems,
        )

    def test_text_suite_item_token_domain_hash_match_validates(self) -> None:
        writer = self.make_suite_bundle("suite-text-token-domain-valid")
        output_records = read_jsonl(writer.path / "outputs" / "suite_items.jsonl")
        token_hash = next(
            record["prompt"]["token_ids_sha256"]
            for record in output_records
            if record["item_id"] == "mock_item_003"
        )
        manifest_path = writer.path / "suite_manifest.json"
        raw_manifest = json.loads(manifest_path.read_text())
        for item in raw_manifest["items"]:
            if item["item_id"] == "mock_item_003":
                item["source"]["source_sha256"] = token_hash
                break
        rewrite_suite_manifest_and_hashes(writer, raw_manifest)

        self.assertEqual(BundleReader(writer.path).problems(), [])

    def test_text_suite_item_text_domain_hash_validates(self) -> None:
        writer = self.make_suite_bundle("suite-text-domain-valid")
        manifest_path = writer.path / "suite_manifest.json"
        raw_manifest = json.loads(manifest_path.read_text())
        for item in raw_manifest["items"]:
            if item["item_id"] == "mock_item_003":
                item["source"]["source_sha256"] = sha256_hex(
                    item["source"]["prompt_text"]
                )
                break
        rewrite_suite_manifest_and_hashes(writer, raw_manifest)

        self.assertEqual(BundleReader(writer.path).problems(), [])

    def test_uppercase_text_source_sha_still_checks_prompt_closure(self) -> None:
        writer = self.make_suite_bundle("suite-text-uppercase-hash-mismatch")
        manifest_path = writer.path / "suite_manifest.json"
        raw_manifest = json.loads(manifest_path.read_text())
        for item in raw_manifest["items"]:
            if item["item_id"] == "mock_item_003":
                item["source"]["source_sha256"] = sha256_hex("unrelated source").upper()
                break
        rewrite_suite_manifest_and_hashes(writer, raw_manifest)

        problems = BundleReader(writer.path).problems()

        self.assertTrue(
            any("prompt.token_ids_sha256 mismatch for text manifest" in p for p in problems),
            problems,
        )

    def test_strict_suite_emitted_token_ids_length_mismatch_is_problem(self) -> None:
        writer = self.make_suite_bundle("suite-emitted-token-ids-mismatch")
        output_path = writer.path / "outputs" / "suite_items.jsonl"
        records = read_jsonl(output_path)
        records[0]["emitted_token_ids"] = [1]
        write_jsonl(output_path, records)
        output_path.write_text("\nnot-json\n" + output_path.read_text())

        problems = _strict_emitted_token_ids_problems(BundleReader(writer.path))

        self.assertTrue(
            any(
                "outputs/suite_items.jsonl line 3.emitted_token_ids length 1 "
                "does not equal emitted_tokens 3" in problem
                for problem in problems
            ),
            problems,
        )

    def test_strict_suite_without_emitted_token_ids_is_unchanged(self) -> None:
        writer = self.make_suite_bundle("suite-no-emitted-token-ids")
        output_path = writer.path / "outputs" / "suite_items.jsonl"
        records = read_jsonl(output_path)
        for record in records:
            record.pop("emitted_token_ids", None)
        write_jsonl(output_path, records)

        self.assertEqual(_strict_emitted_token_ids_problems(BundleReader(writer.path)), [])

    def test_strict_single_prompt_emitted_token_ids_length_mismatch_is_problem(self) -> None:
        writer = self.make_bundle("single-emitted-token-ids-mismatch")
        writer.write_metadata(
            {
                "workload_provenance": {
                    "response": {"emitted_token_ids": [1, 2]},
                    "output_policy": {"emitted_tokens": 3},
                }
            }
        )

        problems = _strict_emitted_token_ids_problems(BundleReader(writer.path))

        self.assertTrue(
            any("metadata.workload_provenance.response.emitted_token_ids length 2" in p for p in problems),
            problems,
        )

    def test_strict_budgeted_text_prompt_count_mismatch_is_problem(self) -> None:
        writer = self.make_suite_bundle("suite-budgeted-prompt-mismatch")
        manifest_path = writer.path / "suite_manifest.json"
        raw_manifest = json.loads(manifest_path.read_text())
        raw_manifest["suite_id"] = "jw_mixed_v1"
        raw_manifest["suite_profile"] = "jw_mixed_v1_common_512_256"
        raw_manifest["source_manifest"]["source_id"] = "jw_mixed_v1:test"
        for item in raw_manifest["items"]:
            if item["item_id"] == "mock_item_003":
                item["shape"]["planned_prompt_tokens"] = 99
                item["source"]["source_sha256"] = sha256_hex(item["source"]["prompt_text"])
                break
        rewrite_suite_manifest_and_hashes(writer, raw_manifest)

        problems = _strict_budgeted_suite_prompt_count_problems(BundleReader(writer.path))

        self.assertTrue(
            any(
                "planned_prompt_tokens_mismatch" in problem
                and "planned_prompt_tokens 99" in problem
                and "realized_prompt_tokens 5" in problem
                for problem in problems
            ),
            problems,
        )

    def test_strict_affine_text_prompt_count_mismatch_is_ignored(self) -> None:
        writer = self.make_suite_bundle("suite-affine-prompt-mismatch")
        manifest_path = writer.path / "suite_manifest.json"
        raw_manifest = json.loads(manifest_path.read_text())
        raw_manifest["suite_id"] = "affine_smoke_v1"
        raw_manifest["suite_profile"] = "affine_mod_ladder_v1_smoke"
        raw_manifest["source_manifest"]["source_id"] = "affine_mod_ladder_v1"
        for item in raw_manifest["items"]:
            if item["item_id"] == "mock_item_003":
                item["shape"]["planned_prompt_tokens"] = 99
                item["source"]["source_sha256"] = sha256_hex(item["source"]["prompt_text"])
                break
        rewrite_suite_manifest_and_hashes(writer, raw_manifest)

        self.assertEqual(
            _strict_budgeted_suite_prompt_count_problems(BundleReader(writer.path)),
            [],
        )

    def test_suite_hash_mismatches_are_validation_errors(self) -> None:
        writer = self.make_suite_bundle("suite-hash-mismatch")
        config = json.loads((writer.path / "config.json").read_text())
        config["workload_profile"]["suite_manifest_sha256"] = "bad"
        (writer.path / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
        metadata = json.loads((writer.path / "metadata.json").read_text())
        metadata["suite"]["manifest_sha256"] = "bad"
        (writer.path / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        raw_manifest = json.loads((writer.path / "suite_manifest.json").read_text())
        file_hash = suite_manifest_sha256(canonical_effective_manifest(raw_manifest))
        problems = BundleReader(writer.path).problems()
        digest_problems = [problem for problem in problems if "hashes to" in problem]
        self.assertEqual(len(digest_problems), 2, problems)
        self.assertTrue(all("'bad'" in problem for problem in digest_problems), digest_problems)
        self.assertTrue(all(file_hash in problem for problem in digest_problems), digest_problems)


if __name__ == "__main__":
    unittest.main()
