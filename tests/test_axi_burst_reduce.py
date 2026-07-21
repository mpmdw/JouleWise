from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

from joulewise.cli import (
    ADDED_DURING_0_5_0,
    ADDED_SINCE_0_4_1,
    _strict_summary_differences,
)
from joulewise.reduce import AXI_REDUCER_VERSION, reduce_bundle
from joulewise.schemas import SummaryMetricsV060


ROOT = Path(__file__).resolve().parents[1]
AXI_FIXTURE = ROOT / "tests" / "fixtures" / "axi_valid_burst"
LEGACY_FIXTURE = ROOT / "tests" / "fixtures" / "legacy_reducer_current_behavior"
GOLDENS = ROOT / "tests" / "goldens"
BASE_HEAD = "9ee87102c04530e874909d077d842a4573f9f065"


def load_json(path: Path) -> dict:
    return json.loads(path.read_bytes())


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
            + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )


def expanded_legacy_golden(version: str) -> dict:
    value = load_json(GOLDENS / "legacy_reducer_041.json")
    if version == "0.4.1":
        return value
    patch = load_json(
        GOLDENS
        / ("legacy_reducer_042.patch.json" if version == "0.4.2" else "legacy_reducer_050.patch.json")
    )
    for pointer, replacement in patch["replacements"].items():
        target = value
        components = pointer.removeprefix("/").split("/")
        for component in components[:-1]:
            target = target[component]
        target[components[-1]] = replacement
    return value


class AxiBurstReduceTests(unittest.TestCase):
    def copied(self, source: Path = AXI_FIXTURE) -> tuple[tempfile.TemporaryDirectory, Path]:
        temporary = tempfile.TemporaryDirectory()
        path = Path(temporary.name) / "bundle"
        shutil.copytree(source, path)
        return temporary, path

    def test_frozen_historical_arms_match_observed_current_behavior_goldens(self) -> None:
        for version in ("0.4.1", "0.4.2", "0.5.0"):
            with self.subTest(version=version):
                expected = expanded_legacy_golden(version)
                actual = reduce_bundle(
                    LEGACY_FIXTURE,
                    reducer_version=version,
                ).to_dict()
                self.assertEqual(actual, expected)
                self.assertNotIn("event_semantics_version", actual["summary_provenance"])
                self.assertNotIn("decode_counter_rollup", actual)
                self.assertIsNone(actual["idle_baseline"]["gpu_freq_mhz_mean"])

                stored = copy.deepcopy(expected)
                stored["idle_baseline"].pop("gpu_freq_mhz_mean")
                tolerance = set(ADDED_DURING_0_5_0)
                if version == "0.4.1":
                    stored.pop("inter_token_throughput_tokens_s")
                    tolerance.update(ADDED_SINCE_0_4_1)
                self.assertEqual(
                    _strict_summary_differences(
                        actual,
                        stored,
                        absent_tolerance=tolerance,
                    ),
                    [],
                )

    def test_legacy_golden_provenance_replays_pristine_base_head(self) -> None:
        archive = subprocess.run(
            ["git", "archive", BASE_HEAD],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
        ).stdout
        source = subprocess.run(
            ["git", "show", f"{BASE_HEAD}:joulewise/reduce.py"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
        ).stdout
        with tempfile.TemporaryDirectory() as temporary:
            head_root = Path(temporary) / "head"
            head_root.mkdir()
            with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
                bundle.extractall(head_root, filter="data")
            self.assertEqual(
                (head_root / "joulewise" / "reduce.py").read_bytes(), source
            )
            source_sha = hashlib.sha256(source).hexdigest()
            cases = {
                "0.4.1": "legacy_reducer_041.provenance.json",
                "0.4.2": "legacy_reducer_042.patch.provenance.json",
                "0.5.0": "legacy_reducer_050.patch.provenance.json",
            }
            for version, provenance_name in cases.items():
                with self.subTest(version=version):
                    provenance_path = GOLDENS / provenance_name
                    provenance = load_json(provenance_path)
                    self.assertEqual(provenance_path.read_bytes(), (
                        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True)
                        + "\n"
                    ).encode("utf-8"))
                    self.assertEqual(provenance["base_head"], BASE_HEAD)
                    self.assertEqual(
                        provenance["source_module_command"],
                        f"git show {BASE_HEAD}:joulewise/reduce.py",
                    )
                    self.assertEqual(
                        provenance["source_module_sha256"], source_sha
                    )
                    env = dict(os.environ)
                    env["PYTHONPATH"] = str(head_root)
                    completed = subprocess.run(
                        [
                            sys.executable,
                            str(ROOT / "tests" / "observe_legacy_reducer_base.py"),
                            "--source-root",
                            str(head_root),
                            "--fixture",
                            str(LEGACY_FIXTURE),
                            "--version",
                            version,
                        ],
                        cwd=head_root,
                        env=env,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    observed_bytes = completed.stdout.encode("utf-8")
                    self.assertEqual(
                        hashlib.sha256(observed_bytes).hexdigest(),
                        provenance["expanded_observation_sha256"],
                    )
                    self.assertEqual(
                        json.loads(observed_bytes), expanded_legacy_golden(version)
                    )
                    golden_path = ROOT / provenance["golden_path"]
                    self.assertEqual(
                        hashlib.sha256(golden_path.read_bytes()).hexdigest(),
                        provenance["golden_sha256"],
                    )

    def test_dispatch_uses_recorded_version_and_fails_closed(self) -> None:
        temporary, path = self.copied(LEGACY_FIXTURE)
        self.addCleanup(temporary.cleanup)
        write_json(path / "summary_metrics.json", expanded_legacy_golden("0.4.1"))
        self.assertEqual(
            reduce_bundle(path).summary_provenance["reducer_version"],
            "0.4.1",
        )

        summary = load_json(path / "summary_metrics.json")
        del summary["summary_provenance"]
        write_json(path / "summary_metrics.json", summary)
        with self.assertRaisesRegex(ValueError, "version is missing"):
            reduce_bundle(path)

        summary["summary_provenance"] = {
            "summary_schema_version": "0.1",
            "reducer_id": "joulewise.reduce_bundle",
            "reducer_version": "9.9.9",
            "config_schema_version": "0.1",
        }
        write_json(path / "summary_metrics.json", summary)
        with self.assertRaisesRegex(ValueError, "unsupported reducer version"):
            reduce_bundle(path)
        with self.assertRaisesRegex(ValueError, "requires AXI config"):
            reduce_bundle(path, reducer_version=AXI_REDUCER_VERSION)

    def test_spoofed_old_label_cannot_enter_historical_arm(self) -> None:
        temporary, path = self.copied()
        self.addCleanup(temporary.cleanup)
        summary = load_json(path / "summary_metrics.json")
        summary["summary_provenance"].pop("event_semantics_version")
        summary["summary_provenance"]["reducer_version"] = "0.5.0"
        write_json(path / "summary_metrics.json", summary)
        with self.assertRaisesRegex(ValueError, "0.6.0-only bundle shape"):
            reduce_bundle(path)
        with self.assertRaisesRegex(ValueError, "0.6.0-only bundle shape"):
            reduce_bundle(path, reducer_version="0.5.0")

    def test_single_request_reducer_matches_hand_calculated_byte_oracle(self) -> None:
        summary = reduce_bundle(AXI_FIXTURE)
        self.assertIsInstance(summary, SummaryMetricsV060)
        expected_bytes = (AXI_FIXTURE / "summary_metrics.json").read_bytes()
        actual_bytes = (
            json.dumps(summary.to_dict(), indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        self.assertEqual(actual_bytes, expected_bytes)
        value = summary.to_dict()
        self.assertEqual(value["gross_energy_j"], 10.0 * 2.2)
        self.assertEqual(value["phase_energy_j"]["decode"], 10.0 * 1.0)
        self.assertEqual(value["decode_counter_rollup"]["acceptance_rate"], 2 / 4)
        self.assertEqual(value["decode_emission_burst_size_p50_tokens"], 1.5)
        self.assertEqual(value["decode_emission_burst_size_p95_tokens"], 1.95)
        self.assertEqual(value["gross_energy_per_committed_output_token_j"], 22 / 3)
        self.assertEqual(value["gross_energy_per_accepted_draft_token_j"], 22 / 2)

    def make_static_batch(self, path: Path, *, second_source: bool = False) -> None:
        (path / "summary_metrics.json").unlink()
        roster = load_json(path / "request_roster.json")
        second = copy.deepcopy(roster["requests"][0])
        second["request_ordinal"] = 1
        second["request_input_id"] = "prompt-001"
        roster["requests"].append(second)
        write_json(path / "request_roster.json", roster)
        roster_hash = hashlib.sha256((path / "request_roster.json").read_bytes()).hexdigest()

        config = load_json(path / "config.json")
        config["batch_policy"].update(
            mode="static_batch",
            requested_batch_size=2,
            admission_policy="admit_roster_together",
            synchronization_policy="barrier_before_prefill",
            dispatch_policy="one_native_batch_call",
            request_roster_sha256=roster_hash,
        )
        write_json(path / "config.json", config)
        config_hash = hashlib.sha256((path / "config.json").read_bytes()).hexdigest()

        metadata = load_json(path / "metadata.json")
        metadata["config_sha256"] = config_hash
        metadata["batch"].update(
            configured_batch_size=2,
            realized_batch_size=2,
            submitted_request_count=2,
            admitted_request_count=2,
            terminal_request_count=2,
            batch_group_id="batch-000",
            request_roster_sha256=roster_hash,
        )
        if second_source:
            metadata["device"]["rail_manifest"] = ["system", "system2"]
        write_json(path / "metadata.json", metadata)

        original_events = load_jsonl(path / "events.jsonl")
        globals_ = [row for row in original_events if "request_id" not in row["metadata"]]
        request_zero = [row for row in original_events if "request_id" in row["metadata"]]
        for row in request_zero:
            row["metadata"]["batch_group_id"] = "batch-000"
            row["metadata"]["request_roster_sha256"] = roster_hash
        request_one = copy.deepcopy(request_zero)
        for row in request_one:
            row["metadata"].update(
                request_id="request-001",
                request_ordinal=1,
                request_input_id="prompt-001",
                source_identity=("mock:second" if second_source else "mock:target"),
            )
        all_events = globals_ + request_zero + request_one
        all_events.sort(
            key=lambda row: (
                row["timestamp_s"],
                0 if row["event_type"] == "sampling_started" else 2 if row["event_type"] in {"sampling_stopped", "run_finalized"} else 1,
                row["metadata"].get("request_event_ordinal", -1),
                row["metadata"].get("request_ordinal", -1),
                row["event_type"],
            )
        )
        # At the shared final timestamp, sampling_stopped precedes run_finalized.
        all_events.sort(
            key=lambda row: (
                row["timestamp_s"],
                1 if row["event_type"] == "run_finalized" else 0,
                row["metadata"].get("request_event_ordinal", -1),
                row["metadata"].get("request_ordinal", -1),
            )
        )
        write_jsonl(path / "events.jsonl", all_events)

        request_rows = load_jsonl(path / "outputs" / "requests.jsonl")
        request_rows[0]["batch_group_id"] = "batch-000"
        request_rows[0]["request_roster_sha256"] = roster_hash
        second_row = copy.deepcopy(request_rows[0])
        second_row.update(
            request_id="request-001",
            request_ordinal=1,
            request_input_id="prompt-001",
        )
        write_jsonl(path / "outputs" / "requests.jsonl", request_rows + [second_row])

        token_rows = load_jsonl(path / "outputs" / "request_tokens.jsonl")
        second_tokens = copy.deepcopy(token_rows)
        for row in second_tokens:
            row.update(
                request_id="request-001",
                request_ordinal=1,
                request_input_id="prompt-001",
            )
        write_jsonl(path / "outputs" / "request_tokens.jsonl", token_rows + second_tokens)

        if second_source:
            trace = (path / "power_trace.csv").read_text().splitlines()
            extra = [
                line.replace("mock:target,system", "mock:second,system2")
                for line in trace[1:]
            ]
            rows = [trace[0]]
            for left, right in zip(trace[1:], extra):
                rows.extend((left, right))
            (path / "power_trace.csv").write_text("\n".join(rows) + "\n")

    def test_synchronized_static_batch_windows_union_once_without_request_energy(self) -> None:
        temporary, path = self.copied()
        self.addCleanup(temporary.cleanup)
        self.make_static_batch(path)
        value = reduce_bundle(path).to_dict()
        self.assertEqual(value["gross_energy_j"], 22.0)
        self.assertEqual(value["batch_group_gross_energy_j"], 22.0)
        self.assertEqual(value["phase_energy_j"]["decode"], 10.0)
        self.assertEqual(value["decode_counter_rollup"]["emitted_count"], 6)
        self.assertEqual(value["decode_phase_output_throughput_tokens_s"], 6.0)
        self.assertEqual(value["gross_energy_per_committed_output_token_j"], 22 / 6)
        self.assertIsNone(value["energy_request_j"])
        self.assertIsNone(value["energy_output_token_j"])
        for request in value["request_decode_metrics"]:
            self.assertFalse(any("energy" in key for key in request))
        self.assertIn("gross_batch_group", value["window_evidence_precheck"])
        self.assertNotIn("gross_request", value["window_evidence_precheck"])

    def test_distinct_meter_phase_windows_sum_across_sources(self) -> None:
        temporary, path = self.copied()
        self.addCleanup(temporary.cleanup)
        self.make_static_batch(path, second_source=True)
        value = reduce_bundle(path).to_dict()
        self.assertEqual(value["gross_energy_j"], 44.0)
        self.assertEqual(value["phase_energy_j"]["decode"], 20.0)

    def test_zero_proposal_and_zero_accepted_censor_only_accepted_ratio(self) -> None:
        temporary, path = self.copied()
        self.addCleanup(temporary.cleanup)
        (path / "summary_metrics.json").unlink()
        events = load_jsonl(path / "events.jsonl")
        for row in events:
            if row["event_type"] == "decode_emission":
                row["metadata"]["tokens_proposed"] = 0
                row["metadata"]["tokens_accepted"] = 0
                row["metadata"]["target_emitted_count"] = row["metadata"]["emitted_count"]
        write_jsonl(path / "events.jsonl", events)
        requests = load_jsonl(path / "outputs" / "requests.jsonl")
        requests[0].update(
            tokens_proposed=0,
            tokens_accepted=0,
            target_emitted_count=3,
            acceptance_rate=None,
        )
        write_jsonl(path / "outputs" / "requests.jsonl", requests)
        value = reduce_bundle(path).to_dict()
        self.assertEqual(value["decode_counter_rollup"]["tokens_proposed"], 0)
        self.assertIsNone(value["decode_counter_rollup"]["acceptance_rate"])
        self.assertIsNone(value["gross_energy_per_accepted_draft_token_j"])

    def test_zero_output_has_zero_window_rates_and_null_size_ratios(self) -> None:
        temporary, path = self.copied()
        self.addCleanup(temporary.cleanup)
        (path / "summary_metrics.json").unlink()

        roster = load_json(path / "request_roster.json")
        roster["requests"][0]["requested_output_tokens"] = 0
        write_json(path / "request_roster.json", roster)
        roster_hash = hashlib.sha256((path / "request_roster.json").read_bytes()).hexdigest()
        config = load_json(path / "config.json")
        config["batch_policy"]["request_roster_sha256"] = roster_hash
        write_json(path / "config.json", config)

        metadata = load_json(path / "metadata.json")
        metadata["config_sha256"] = hashlib.sha256((path / "config.json").read_bytes()).hexdigest()
        metadata["batch"]["request_roster_sha256"] = roster_hash
        write_json(path / "metadata.json", metadata)

        events = [
            row
            for row in load_jsonl(path / "events.jsonl")
            if row["event_type"] not in {"decode_emission", "token"}
        ]
        request_ordinal = 0
        for row in events:
            if "request_id" not in row["metadata"]:
                continue
            row["metadata"]["request_event_ordinal"] = request_ordinal
            row["metadata"]["request_roster_sha256"] = roster_hash
            request_ordinal += 1
            if row["event_type"] == "request_terminal":
                row["metadata"]["realized_output_token_count"] = 0
        write_jsonl(path / "events.jsonl", events)

        request = load_jsonl(path / "outputs" / "requests.jsonl")[0]
        request.update(
            request_roster_sha256=roster_hash,
            requested_output_tokens=0,
            output_token_count=0,
            response_text="",
            response_text_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            emitted_token_ids_sha256="544ca93c6bfa8ab35f4d26ada966212e3cef9d95312dac24c3292dae82997c82",
            tokens_proposed=0,
            tokens_accepted=0,
            target_emitted_count=0,
            acceptance_rate=None,
        )
        write_jsonl(path / "outputs" / "requests.jsonl", [request])
        (path / "outputs" / "request_tokens.jsonl").write_text("")

        value = reduce_bundle(path).to_dict()
        self.assertEqual(value["decode_counter_rollup"]["emitted_count"], 0)
        self.assertIsNone(value["gross_energy_per_committed_output_token_j"])
        self.assertIsNone(value["gross_energy_per_accepted_draft_token_j"])
        self.assertEqual(value["decode_phase_output_throughput_tokens_s"], 0.0)
        self.assertEqual(value["decode_emission_event_rate_events_s"], 0.0)
        self.assertIsNone(value["decode_emission_burst_size_mean_tokens"])
        self.assertEqual(
            value["request_decode_metrics"][0]["decode_phase_output_throughput_tokens_s"],
            0.0,
        )

    def test_single_emission_type7_quantiles_equal_the_one_burst(self) -> None:
        temporary, path = self.copied()
        self.addCleanup(temporary.cleanup)
        (path / "summary_metrics.json").unlink()
        events = load_jsonl(path / "events.jsonl")
        first = next(row for row in events if row["event_type"] == "decode_emission")
        first["metadata"].update(
            emitted_count=3,
            emitted_token_ids=[10, 11, 12],
            emitted_token_ids_sha256="c561702b69aa308e48ecda406eea33f382995e91faaa8ce45bbf8bafedb1fd4c",
            tokens_proposed=4,
            tokens_accepted=2,
            target_emitted_count=1,
        )
        second = [row for row in events if row["event_type"] == "decode_emission"][1]
        removed_ordinal = second["metadata"]["request_event_ordinal"]
        events.remove(second)
        for row in events:
            ordinal = row["metadata"].get("request_event_ordinal")
            if isinstance(ordinal, int) and ordinal > removed_ordinal:
                row["metadata"]["request_event_ordinal"] = ordinal - 1
            if row["event_type"] == "token" and row["metadata"]["output_token_ordinal"] == 2:
                row["metadata"]["decode_step_ordinal"] = 0
        write_jsonl(path / "events.jsonl", events)
        tokens = load_jsonl(path / "outputs" / "request_tokens.jsonl")
        tokens[2]["decode_step_ordinal"] = 0
        write_jsonl(path / "outputs" / "request_tokens.jsonl", tokens)

        value = reduce_bundle(path).to_dict()
        self.assertEqual(value["decode_emission_event_rate_events_s"], 1.0)
        self.assertEqual(value["decode_emission_burst_size_mean_tokens"], 3.0)
        self.assertEqual(value["decode_emission_burst_size_p50_tokens"], 3.0)
        self.assertEqual(value["decode_emission_burst_size_p95_tokens"], 3.0)
        self.assertEqual(value["decode_emission_burst_size_max_tokens"], 3)

    def test_missing_genuine_per_token_timestamp_censors_inter_token_metric(self) -> None:
        temporary, path = self.copied()
        self.addCleanup(temporary.cleanup)
        (path / "summary_metrics.json").unlink()
        tokens = load_jsonl(path / "outputs" / "request_tokens.jsonl")
        tokens[0]["timestamp_s"] = None
        tokens[0]["timestamp_provenance"] = None
        write_jsonl(path / "outputs" / "request_tokens.jsonl", tokens)
        events = load_jsonl(path / "events.jsonl")
        removed = next(
            index
            for index, row in enumerate(events)
            if row["event_type"] == "token" and row["metadata"]["output_token_ordinal"] == 0
        )
        del events[removed]
        for row in events:
            ordinal = row["metadata"].get("request_event_ordinal")
            if isinstance(ordinal, int) and ordinal > 6:
                row["metadata"]["request_event_ordinal"] = ordinal - 1
        write_jsonl(path / "events.jsonl", events)
        value = reduce_bundle(path).to_dict()
        self.assertIsNone(value["inter_token_throughput_tokens_s"])
        self.assertAlmostEqual(value["request_decode_metrics"][0]["ttft_s"], 1.1)


if __name__ == "__main__":
    unittest.main()


class AxiV061AnchorEraTests(unittest.TestCase):
    """D-078: 0.6.1 is the anchor-era AXI arm; 0.6.0 stays byte-frozen."""

    def test_new_event_v2_default_is_0_6_2_and_0_6_0_is_historical_only(self) -> None:
        # W8 defect shape: deleting the stored historical summary made a new
        # event-v2 bundle default to the defective 0.6.0 wire.
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "bundle"
        shutil.copytree(AXI_FIXTURE, path)
        (path / "summary_metrics.json").unlink()
        summary = reduce_bundle(path)
        self.assertEqual(summary.summary_provenance["reducer_version"], "0.6.2")
        self.assertEqual(AXI_REDUCER_VERSION, "0.6.2")
        explicit = reduce_bundle(path, reducer_version="0.6.1")
        self.assertEqual(
            explicit.summary_provenance["reducer_version"], "0.6.1"
        )
        with self.assertRaisesRegex(ValueError, "historical re-reduction only"):
            reduce_bundle(path, reducer_version="0.6.0")

    def test_0_6_1_matches_golden_and_0_6_0_stays_byte_frozen(self) -> None:
        frozen = reduce_bundle(AXI_FIXTURE, reducer_version="0.6.0")
        self.assertEqual(
            frozen.canonical_bytes(),
            (AXI_FIXTURE / "summary_metrics.json").read_bytes(),
        )
        current = reduce_bundle(AXI_FIXTURE, reducer_version="0.6.1").to_dict()
        golden = load_json(GOLDENS / "axi_summary_v061.json")
        self.assertEqual(current, golden)
        self.assertEqual(
            current["summary_provenance"]["reducer_version"], "0.6.1"
        )
        # Mock telemetry has no native-stamped raw capture: the anchor-era
        # machinery is powermetrics-only, so 0.6.1 differs from 0.6.0 solely
        # by its recorded provenance on this fixture.
        gate = current["window_evidence_precheck"]["gross_request"]
        self.assertFalse(gate["eligible"])
        self.assertNotIn("energy_anchor_shift_envelopes", current)
        self.assertNotIn(
            "E_clock_anchor_shift_bound_j", current["energy_bound_terms_j"]
        )
        frozen_payload = frozen.to_dict()
        self.assertNotIn(
            "E_clock_anchor_shift_bound_j", frozen_payload["energy_bound_terms_j"]
        )
        self.assertNotIn("energy_anchor_shift_envelopes", frozen_payload)

    def test_0_6_2_matches_its_identity_locked_golden(self) -> None:
        current = reduce_bundle(AXI_FIXTURE, reducer_version="0.6.2")
        self.assertEqual(
            current.canonical_bytes(),
            (GOLDENS / "axi_summary_v062.json").read_bytes(),
        )
        self.assertEqual(
            current.summary_provenance["reducer_version"], "0.6.2"
        )
