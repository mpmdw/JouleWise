from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.bundle import RunBundleWriter
from joulewise.clock import FakeClock
from joulewise.schemas import BenchmarkConfig
from scripts import generate_g2a_probe_inputs as probe
from scripts import issue_g2a_prefill_prompt_pin as issuer
from scripts import select_g2a_prefill_length as selector
from scripts import summarize_g2a_prefill_probe as summarizer


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/g2a/pin"
PANEL = ROOT / "configs/model_panels/qwen3_4bit.json"
POLICY = ROOT / "configs/campaign_policies/quiet_mac_p2_production.json"
WORKLOAD = ROOT / "configs/workloads/real_prompts_v1.json"
RULING = ROOT / issuer.d117_v5.PREFILL_RULING_TRACE_PATH

# Copied from the retained production bundle
# runs_window_metrologyA_20260731_bound/neg8-refcorpus-r12.
RETAINED_METADATA_KEYS = frozenset(
    {
        "adapters",
        "campaign_environment_preflight",
        "campaign_policy",
        "clock",
        "clock_anchor_bound_s",
        "config_sha256",
        "config_warnings",
        "connection",
        "device",
        "environment",
        "environment_admission",
        "git_commit",
        "idle_baseline",
        "idle_drift_bound_w",
        "instrument_calibration",
        "joulewise_version",
        "machine",
        "marker_to_first_sample_phase_bound_s",
        "marker_to_last_sample_phase_bound_s",
        "model",
        "platform",
        "python_version",
        "quantization",
        "run_id",
        "schema_version",
        "source_provenance",
        "thermal_post",
        "thermal_pre",
        "trace_window_margins",
        "uncertainty_evidence",
        "workload_observed",
        "workload_provenance",
    }
)
RETAINED_SUMMARY_KEYS = frozenset(
    {
        "decode_latency_s",
        "energy_anchor_shift_envelopes",
        "energy_bound_terms_j",
        "energy_output_token_j",
        "energy_request_j",
        "energy_token_j",
        "energy_uncertainty_status",
        "energy_variance_terms_j2",
        "failure_message",
        "failure_reason",
        "gross_energy_j",
        "idle_baseline",
        "idle_mean_uncertainty",
        "idle_subtracted_energy_j",
        "inter_token_throughput_tokens_s",
        "measurement_quality",
        "phase_energy_j",
        "status",
        "suite_metrics",
        "summary_provenance",
        "throughput_tokens_s",
        "ttft_s",
        "uncertainty",
        "window_evidence_precheck",
    }
)


def runner_config_bytes(config_raw: bytes) -> bytes:
    """Get real bundle-writer bytes without running a workload or telemetry."""
    config = BenchmarkConfig.from_mapping(json.loads(config_raw))
    with tempfile.TemporaryDirectory() as temporary, mock.patch(
        "joulewise.bundle._capture_source_state", return_value={}
    ):
        writer = RunBundleWriter.create(Path(temporary), config, FakeClock())
        raw = (writer.path / "config.json").read_bytes()
        assert writer.config_sha256 == hashlib.sha256(raw).hexdigest()
        return raw


def retained_metadata(run_id: str, rung: dict[str, object], config_raw: bytes) -> dict[str, object]:
    value: dict[str, object] = {key: None for key in RETAINED_METADATA_KEYS}
    value.update(
        run_id=run_id,
        config_sha256=hashlib.sha256(config_raw).hexdigest(),
        workload_provenance={
            "prompt": {
                "realized_token_count": rung["prefill_tokens"],
                "token_ids_sha256": rung["prompt_token_ids_sha256"],
            }
        },
    )
    return value


def retained_summary(count: int) -> dict[str, object]:
    value: dict[str, object] = {key: None for key in RETAINED_SUMMARY_KEYS}
    value["window_evidence_precheck"] = {
        "phase": {
            "prefill": {
                "windows": [{"in_window_sample_count": count}],
            }
        }
    }
    return value


class _DeskChainTokenizer:
    def encode(self, text: str, add_special_tokens: bool = True) -> list[int]:
        if not add_special_tokens:
            raise AssertionError("the desk chain must use add_special_tokens=True")
        if text == probe.PROMPT_SENTENCE:
            return list(range(7))
        for length, closing in probe.CLOSING_SENTENCES.items():
            if text == closing:
                return list(range(probe.EXPECTED_CLOSING_TOKEN_COUNTS[length]))
            closing_count = probe.EXPECTED_CLOSING_TOKEN_COUNTS[length]
            repeat_count = (length - closing_count) // 7
            if text == " ".join([probe.PROMPT_SENTENCE] * repeat_count + [closing]):
                return [index % 151936 for index in range(length)]
        return [0]


class SummarizeG2APrefillProbeTests(unittest.TestCase):
    maxDiff = None

    def copy_fixture(self, temporary: str) -> tuple[Path, Path, Path]:
        root = Path(temporary) / "fixture"
        shutil.copytree(FIXTURE, root)
        inventory_path = root / "g2a-input-inventory.json"
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        inventory["config_root"] = str(root / "config-root")
        ladder_path = root / "prefill-prompt-ladder.json"
        ladder = json.loads(ladder_path.read_text(encoding="utf-8"))
        ladder.update(
            rendering_mode="raw_prompt_text",
            chat_template_applied=False,
            thinking_policy="not_applicable_raw_prefill",
        )
        ladder_path.write_text(json.dumps(ladder) + "\n", encoding="utf-8")
        inventory.update(
            runtime_adapter={
                "path": "joulewise/adapters/mlx_runtime.py",
                "sha256": hashlib.sha256(
                    (ROOT / "joulewise/adapters/mlx_runtime.py").read_bytes()
                ).hexdigest(),
            },
            repo_head="a" * 40,
            rendering_mode="raw_prompt_text",
            chat_template_applied=False,
            thinking_policy="not_applicable_raw_prefill",
        )
        inventory["prompt_ladder"]["path"] = str(ladder_path)
        inventory["prompt_ladder"]["sha256"] = hashlib.sha256(
            ladder_path.read_bytes()
        ).hexdigest()
        by_length = {rung["prefill_tokens"]: rung for rung in ladder["rungs"]}
        for stage in inventory["stages"]:
            rung = by_length[stage["prefill_tokens"]]
            for member in stage["members"]:
                run_root = root / "summary-root" / member["run_id"]
                config_raw = (root / "config-root" / member["config_path"]).read_bytes()
                run_config_raw = runner_config_bytes(config_raw)
                (run_root / "config.json").write_bytes(run_config_raw)
                summary_path = run_root / "summary_metrics.json"
                original = json.loads(summary_path.read_text(encoding="utf-8"))
                count = original["window_evidence_precheck"]["phase"]["prefill"][
                    "windows"
                ][0]["in_window_sample_count"]
                summary_path.write_text(
                    json.dumps(retained_summary(count)) + "\n", encoding="utf-8"
                )
                (run_root / "metadata.json").write_text(
                    json.dumps(retained_metadata(member["run_id"], rung, run_config_raw)) + "\n",
                    encoding="utf-8",
                )
        inventory_path.write_text(
            json.dumps(inventory, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        return root / "config-root", inventory_path, root / "summary-root"

    def run_summary(
        self,
        root: Path,
        config_root: Path,
        inventory: Path,
        runs_root: Path,
    ) -> tuple[int, Path, Path]:
        counts = root / "counts.jsonl"
        summary = root / "summary.json"
        code = summarizer.main(
            [
                "--config-root",
                str(config_root),
                "--input-inventory",
                str(inventory),
                "--runs-root",
                str(runs_root),
                "--counts-output",
                str(counts),
                "--summary-output",
                str(summary),
            ]
        )
        return code, counts, summary

    def rewrite_count(self, runs_root: Path, run_id: str, count: int) -> None:
        path = runs_root / run_id / "summary_metrics.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["window_evidence_precheck"]["phase"]["prefill"]["windows"][0][
            "in_window_sample_count"
        ] = count
        path.write_text(json.dumps(value) + "\n", encoding="utf-8")

    def test_five_passing_small_members_qualify_and_large_below_five_does_not_gate(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            self.rewrite_count(runs_root, "g2a-large-p0512-r01", 0)
            code, counts_path, summary_path = self.run_summary(
                root, config_root, inventory, runs_root
            )
            rows = json.loads(summary_path.read_text(encoding="utf-8"))
            counts = json.loads(counts_path.read_text(encoding="utf-8"))
        self.assertEqual(code, 0)
        self.assertEqual(counts["schema_version"], "joulewise.g2a_probe_counts_receipt.v1")
        self.assertEqual(len(counts["runs"]), 24)
        self.assertEqual([row["length"] for row in rows], [512, 1024, 2048, 4096])
        self.assertTrue(rows[0]["all_small_count_ge_5"])
        self.assertEqual(rows[0]["small_minimum_count"], 6)
        self.assertEqual(rows[0]["large_members"], 1)
        large = next(
            row for row in counts["runs"] if row["run_id"] == "g2a-large-p0512-r01"
        )
        self.assertEqual(large["in_window_sample_count"], 0)

    def test_one_small_member_below_five_makes_only_that_rung_nonqualifying(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            self.rewrite_count(runs_root, "g2a-small-p1024-r03", 4)
            code, _counts, summary_path = self.run_summary(
                root, config_root, inventory, runs_root
            )
            rows = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(code, 0)
        by_length = {row["length"]: row for row in rows}
        self.assertFalse(by_length[1024]["all_small_count_ge_5"])
        self.assertEqual(by_length[1024]["small_minimum_count"], 4)
        self.assertTrue(by_length[512]["all_small_count_ge_5"])

    def test_small_count_below_three_is_preserved_in_member_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            run_id = "g2a-small-p2048-r04"
            self.rewrite_count(runs_root, run_id, 2)
            code, counts_path, summary_path = self.run_summary(
                root, config_root, inventory, runs_root
            )
            counts = json.loads(counts_path.read_text(encoding="utf-8"))["runs"]
            rows = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(code, 0)
        member = next(row for row in counts if row["run_id"] == run_id)
        self.assertEqual(member["in_window_sample_count"], 2)
        rung = next(row for row in rows if row["length"] == 2048)
        self.assertEqual(rung["small_minimum_count"], 2)
        self.assertFalse(rung["all_small_count_ge_5"])

    def test_missing_small_run_remains_a_below_floor_row(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory_path, runs_root = self.copy_fixture(temporary)
            (runs_root / "g2a-small-p0512-r05" / "summary_metrics.json").unlink()
            code, counts, summary = self.run_summary(
                root, config_root, inventory_path, runs_root
            )
            row = next(
                item for item in json.loads(summary.read_text()) if item["length"] == 512
            )
        self.assertEqual(code, 0)
        self.assertEqual(row["small_members"], 4)
        self.assertEqual(row["small_minimum_count"], 0)
        self.assertFalse(row["all_small_count_ge_5"])

    def test_missing_summary_emits_zero_below_floor_row(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            (runs_root / "g2a-small-p2048-r02" / "summary_metrics.json").unlink()
            code, _counts, summary = self.run_summary(
                root, config_root, inventory, runs_root
            )
            row = next(
                item for item in json.loads(summary.read_text()) if item["length"] == 2048
            )
        self.assertEqual(code, 0)
        self.assertEqual(row["small_minimum_count"], 0)
        self.assertFalse(row["all_small_count_ge_5"])

    def test_empty_rungs_stay_fail_closed_for_the_standalone_selector(self) -> None:
        # An incomplete ladder must never authorize a selection outside the
        # harvest's RECOVER gate (registration section 8; PR #463 review F1).
        with tempfile.TemporaryDirectory() as temporary:
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            members, rows = summarizer.summarize(config_root=config_root, input_inventory=inventory,
                                                runs_root=runs_root, valid_run_ids=set())
            self.assertEqual(members, [])
            self.assertTrue(all(row["small_members"] == 0 and row["small_minimum_count"] == 0
                                and row["all_small_count_ge_5"] is False for row in rows))
            summary = Path(temporary) / "empty-summary.json"
            summary.write_bytes(summarizer._summary_bytes(rows))
            output = Path(temporary) / "empty-selection.json"
            self.assertEqual(selector.main(["--summary", str(summary), "--output", str(output)]), 2)
            record = json.loads(output.read_bytes())
            self.assertIsNone(record.get("selected_prefill_tokens"))
            self.assertNotEqual(record.get("status"), "selected")

    def test_valid_filter_excludes_nongating_large_member_without_rejecting_select(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config_root, inventory_path, runs_root = self.copy_fixture(temporary)
            inventory = json.loads(inventory_path.read_bytes())
            valid = {member["run_id"] for stage in inventory["stages"] for member in stage["members"]}
            excluded = next(stage["members"][0]["run_id"] for stage in inventory["stages"]
                            if stage["stage_id"] == "large-p512")
            valid.remove(excluded)
            # Invalid provenance must not be inspected or counted.
            (runs_root / excluded / "metadata.json").write_bytes(b"invalid excluded metadata")
            members, rows = summarizer.summarize(config_root=config_root, input_inventory=inventory_path,
                                                runs_root=runs_root, valid_run_ids=valid)
            self.assertNotIn(excluded, {member["run_id"] for member in members})
            self.assertEqual(rows[0]["large_members"], 0)
            issuer._validate_summary(rows)
            selection = selector.select(rows, summary_sha256=hashlib.sha256(summarizer._summary_bytes(rows)).hexdigest())
            self.assertEqual(selection["collection_prefill_tokens"], 512)
            self.assertEqual(selection["status"], "selected")

    def test_wrong_run_id_refuses_even_when_the_mutated_config_hash_is_rebound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory_path, runs_root = self.copy_fixture(temporary)
            run_id = "g2a-small-p0512-r01"
            metadata_path = runs_root / run_id / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["run_id"] = "wrong-run-id"
            metadata_path.write_text(json.dumps(metadata) + "\n", encoding="utf-8")
            code, _counts, _summary = self.run_summary(
                root, config_root, inventory_path, runs_root
            )
        self.assertEqual(code, 2)

    def test_altered_config_hash_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            path = config_root / "large-p4096/g2a-large-p4096-r01.json"
            path.write_bytes(path.read_bytes() + b" \n")
            code, _counts, _summary = self.run_summary(
                root, config_root, inventory, runs_root
            )
        self.assertEqual(code, 2)

    def test_recorded_run_config_hash_mismatch_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            run_id = "g2a-small-p0512-r01"
            path = runs_root / run_id / "config.json"
            path.write_bytes(path.read_bytes() + b" ")
            code, _counts, _summary = self.run_summary(
                root, config_root, inventory, runs_root
            )
        self.assertEqual(code, 2)

    def test_runner_normalized_config_binds_input_run_and_metadata_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config_root, inventory_path, runs_root = self.copy_fixture(temporary)
            inventory = json.loads(inventory_path.read_bytes())
            member = inventory["stages"][0]["members"][0]
            input_raw = (config_root / member["config_path"]).read_bytes()
            run_raw = (runs_root / member["run_id"] / "config.json").read_bytes()
            normalized = json.loads(run_raw)
            self.assertNotEqual(input_raw, run_raw)
            self.assertNotEqual(member["config_sha256"], hashlib.sha256(run_raw).hexdigest())
            for section, field in (("hardware_target", "host"), ("interconnect", "link_speed_mbps"),
                                   ("interconnect", "notes"), ("run_metadata", "ambient_temp_c"),
                                   ("run_metadata", "notes"), ("workload_profile", "dataset_ref"),
                                   ("workload_profile", "prompt_tokens")):
                self.assertNotIn(field, json.loads(input_raw)[section])
                self.assertIsNone(normalized[section][field])
            rows, _ = summarizer.summarize(config_root=config_root, input_inventory=inventory_path,
                                          runs_root=runs_root)
            self.assertEqual(rows[0]["config_sha256"], hashlib.sha256(run_raw).hexdigest())
            self.assertEqual(rows[0]["config_sha256"],
                             json.loads((runs_root / member["run_id"] / "metadata.json").read_bytes())["config_sha256"])

    def test_nondefault_run_config_change_refuses_even_with_metadata_hash_rebound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            run_root = runs_root / "g2a-small-p0512-r01"
            config = json.loads((run_root / "config.json").read_bytes())
            config["sampling"]["power_hz"] += 1
            raw = runner_config_bytes(json.dumps(config).encode())
            (run_root / "config.json").write_bytes(raw)
            metadata = json.loads((run_root / "metadata.json").read_bytes())
            metadata["config_sha256"] = hashlib.sha256(raw).hexdigest()
            (run_root / "metadata.json").write_text(json.dumps(metadata) + "\n")
            with self.assertRaisesRegex(summarizer.ProbeSummaryError, "run_provenance_mismatch: .*: config_sha256"):
                summarizer.summarize(config_root=config_root, input_inventory=inventory, runs_root=runs_root)

    def test_metadata_config_hash_must_bind_observed_run_bytes(self) -> None:
        for digest in (None, "0" * 64):
            with self.subTest(digest=digest), tempfile.TemporaryDirectory() as temporary:
                config_root, inventory, runs_root = self.copy_fixture(temporary)
                path = runs_root / "g2a-small-p0512-r01" / "metadata.json"
                metadata = json.loads(path.read_bytes())
                metadata["config_sha256"] = digest
                path.write_text(json.dumps(metadata) + "\n")
                with self.assertRaisesRegex(summarizer.ProbeSummaryError, "metadata.config_sha256"):
                    summarizer.summarize(config_root=config_root, input_inventory=inventory, runs_root=runs_root)

    def test_extra_config_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            (config_root / "small-p4096/extra.json").write_text("{}\n", encoding="utf-8")
            code, _counts, _summary = self.run_summary(
                root, config_root, inventory, runs_root
            )
        self.assertEqual(code, 2)

    def test_exact_four_row_output_is_accepted_by_selector(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            code, _counts, summary = self.run_summary(
                root, config_root, inventory, runs_root
            )
            selection = root / "selection.json"
            select_code = selector.main(
                ["--summary", str(summary), "--output", str(selection)]
            )
            record = json.loads(selection.read_text(encoding="utf-8"))
        self.assertEqual((code, select_code), (0, 0))
        self.assertEqual(record["selected_prefill_tokens"], 512)

    def test_fixture_copies_retained_top_level_artifact_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            _config_root, _inventory, runs_root = self.copy_fixture(temporary)
            run_root = runs_root / "g2a-small-p0512-r01"
            metadata = json.loads((run_root / "metadata.json").read_text())
            summary = json.loads((run_root / "summary_metrics.json").read_text())
        self.assertEqual(set(metadata), RETAINED_METADATA_KEYS)
        self.assertEqual(set(summary), RETAINED_SUMMARY_KEYS)
        self.assertNotIn("run_id", summary)
        self.assertNotIn("workload_provenance", summary)

    def test_missing_metadata_refuses_by_name(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            (runs_root / "g2a-small-p0512-r01" / "metadata.json").unlink()
            with self.assertRaises(summarizer.ProbeSummaryError) as raised:
                summarizer.summarize(
                    config_root=config_root,
                    input_inventory=inventory,
                    runs_root=runs_root,
                )
        self.assertTrue(str(raised.exception).startswith("metadata_unreadable:"))

    def test_run_id_removed_from_metadata_refuses_by_exact_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config_root, inventory, runs_root = self.copy_fixture(temporary)
            run_id = "g2a-small-p0512-r01"
            metadata_path = runs_root / run_id / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            del metadata["run_id"]
            metadata_path.write_text(json.dumps(metadata) + "\n")
            with self.assertRaises(summarizer.ProbeSummaryError) as raised:
                summarizer.summarize(
                    config_root=config_root,
                    input_inventory=inventory,
                    runs_root=runs_root,
                )
        self.assertEqual(
            str(raised.exception),
            "run_provenance_mismatch: g2a-small-p0512-r01: run_id",
        )

    def test_desk_chain_actual_artifacts_reach_v5_loader(self) -> None:
        # `build-probes` hashes each panel entry's on-disk `tokenizer.json`
        # (`_validate_panel`), so the desk chain needs the local model mirrors;
        # CI has none and must skip by name rather than fail on a missing
        # artifact.
        panel = json.loads(PANEL.read_text(encoding="utf-8"))
        missing = [
            entry["model_id"]
            for entry in panel["entries"]
            if not Path(entry["source"]).expanduser().joinpath("tokenizer.json").is_file()
        ]
        if missing:
            self.skipTest(f"local model mirrors absent (CI environment): {missing}")
        identity = {
            "os_build": "25F84",
            "hardware_model": "Mac15,9",
            "power_policy": "ac_high_power",
            "sampling_interval_ms": 100,
            "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
            "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
        }
        t1 = {
            **identity,
            "powermetrics_sha256": "1" * 64,
            "anchor_method_version": "clock_anchor_v3",
            "mlx_version": "0.test",
            "protocol_sha256": "2" * 64,
        }
        acceptance = {
            "acceptance_id": "d079_calibration_acceptance_v2_n17_r6",
            "ledger_cutoff": {"sequence": 76, "head_digest": "3" * 64},
        }
        ledger_binding = {
            "ledger": {
                "path": "/test/calibration_observation_ledger.jsonl",
                "sha256": "4" * 64,
                "head_sequence": 76,
                "head_digest": "3" * 64,
            },
            "head_pin": {
                "path": "configs/calibration/calibration_ledger_head.json",
                "sha256": "5" * 64,
            },
        }
        tokenizer = _DeskChainTokenizer()
        with tempfile.TemporaryDirectory(prefix="g2a-desk-chain-") as temporary:
            root = Path(temporary) / "g2a"
            plan_id = "fixture-desk-chain-b3w1"
            block3_policy = ROOT / issuer.BLOCK3_POLICY_PATH
            with mock.patch.object(
                probe, "_load_runtime_tokenizer", return_value=tokenizer
            ):
                build_code = probe.main(
                    [
                        "build-probes",
                        "--root",
                        str(root),
                        "--panel",
                        str(PANEL),
                        "--small-members",
                        "5",
                        "--large-members",
                        "1",
                    ]
                )
                self.assertEqual(build_code, 0)
                plan_root = root / "window-plan"
                ladder_path = plan_root / "prefill-prompt-ladder.json"
                ladder = json.loads(ladder_path.read_text())
                issuer._validate_ladder(ladder)
                with mock.patch.object(
                    probe,
                    "_derive_live_vectors",
                    return_value=(
                        copy.deepcopy(identity),
                        copy.deepcopy(t1),
                        copy.deepcopy(acceptance),
                    ),
                ), mock.patch.object(
                    probe,
                    "_authenticate_ledger_and_acceptance",
                    return_value=copy.deepcopy(ledger_binding),
                ):
                    bind_code = probe.main(
                        [
                            "bind-window",
                            "--root",
                            str(root),
                            "--ledger",
                            "/test/calibration_observation_ledger.jsonl",
                            "--head-pin",
                            str(ROOT / "configs/calibration/calibration_ledger_head.json"),
                            "--campaign-policy",
                            str(block3_policy),
                            "--power-policy",
                            "ac_high_power",
                            "--window-id",
                            plan_id,
                            "--session-id",
                            plan_id + "-calibration",
                            "--evidence-root-id",
                            "evidence-g2a-chain",
                        ]
                    )
            self.assertEqual((build_code, bind_code), (0, 0))

            config_root = root / "prefill-probe-configs"
            inventory_path = plan_root / "g2a-input-inventory.json"
            inventory = json.loads(inventory_path.read_text())
            by_length = {row["prefill_tokens"]: row for row in ladder["rungs"]}
            runs_root = root / "runs"
            for stage in inventory["stages"]:
                rung = by_length[stage["prefill_tokens"]]
                for member in stage["members"]:
                    run_root = runs_root / member["run_id"]
                    run_root.mkdir(parents=True)
                    run_config_raw = runner_config_bytes((config_root / member["config_path"]).read_bytes())
                    (run_root / "config.json").write_bytes(run_config_raw)
                    (run_root / "metadata.json").write_text(
                        json.dumps(retained_metadata(member["run_id"], rung, run_config_raw)) + "\n"
                    )
                    (run_root / "summary_metrics.json").write_text(
                        json.dumps(retained_summary(6)) + "\n"
                    )

            counts_path = plan_root / "d166-prefill-counts-receipt.json"
            summary_path = plan_root / "d166-prefill-resolvability-summary.json"
            summary_code = summarizer.main(
                [
                    "--config-root",
                    str(config_root),
                    "--input-inventory",
                    str(inventory_path),
                    "--runs-root",
                    str(runs_root),
                    "--counts-output",
                    str(counts_path),
                    "--summary-output",
                    str(summary_path),
                ]
            )
            selection_path = plan_root / "d166-prefill-selection.json"
            selection_code = selector.main(
                ["--summary", str(summary_path), "--output", str(selection_path)]
            )
            self.assertEqual((summary_code, selection_code), (0, 0))

            # Wrap the generated artifacts in the harvester's copytree layout.
            # Only scratch coordinates and their receipt hash change: configs,
            # run bundles, ladder, summary and selector output retain their bytes.
            archive = Path(temporary) / "harvest"
            archived_g2a = archive / "g2a-root"
            shutil.copytree(root, archived_g2a)
            archived_plan = archived_g2a / "window-plan"
            live_root = issuer.LIVE_WINDOWS_ROOT / plan_id
            inventory["config_root"] = str(live_root / "prefill-probe-configs")
            for key in ("prompt_ladder", "identity_epoch", "t1_bindings", "calibration_plan"):
                inventory[key]["path"] = str(live_root / Path(inventory[key]["path"]).relative_to(root.resolve()))
            archived_inventory = archived_plan / inventory_path.name
            archived_inventory.write_bytes(issuer._pin_bytes(inventory))
            self.assertEqual(inventory["campaign_policy"], {
                "path": issuer.BLOCK3_POLICY_PATH, "sha256": issuer.BLOCK3_POLICY_SHA256,
            })
            counts = json.loads(counts_path.read_bytes())
            counts["input_inventory_sha256"] = hashlib.sha256(archived_inventory.read_bytes()).hexdigest()
            counts["runs_root"] = str(live_root / "runs")
            (archived_plan / counts_path.name).write_bytes(issuer._pin_bytes(counts))
            derived = archive / "derived"
            derived.mkdir()
            for source, name in ((archived_plan / counts_path.name, "counts.json"),
                                 (summary_path, "summary.json"), (selection_path, "selection.json")):
                shutil.copyfile(source, derived / name)
            custody = archive / "night-custody"
            custody.mkdir()
            chain_raw = (
                "export NIGHT_CHAIN_INTERFACE=g2a-reservation-v1\n"
                f"export G2A_ROOT={live_root}\n"
                f"export POLICY=/fixture-measurement-g2a-b3w1/{issuer.BLOCK3_POLICY_PATH}\n"
            ).encode()
            (custody / "chain.zsh").write_bytes(chain_raw)
            (custody / "chain.zsh.sha256").write_text(hashlib.sha256(chain_raw).hexdigest() + "  chain.zsh\n")
            night_plan = {
                "schema": "joulewise.night_plan.v2", "plan_id": plan_id,
                "receipt_class": "DIAGNOSTIC_NO_PACK", "t0_epoch_s": 1000,
                "measurement_root": "/fixture-measurement-g2a-b3w1", "custody_root": "/fixture-custody",
                "chain_path": "/fixture-custody/chain.zsh", "chain_sha256_path": "/fixture-custody/chain.zsh.sha256",
            }
            (custody / "night_plan.json").write_bytes(issuer._pin_bytes(night_plan))
            selection_sha256 = hashlib.sha256(selection_path.read_bytes()).hexdigest()
            harvest_path = archive / "harvest.json"
            harvest_path.write_bytes(issuer._pin_bytes({
                "schema": "joulewise.harvest_g2a_window.v1", "archive_root": str(archive.resolve()),
                "plan_id": plan_id, "plan_sha256": hashlib.sha256((custody / "night_plan.json").read_bytes()).hexdigest(),
                "verdict": "SELECT", "cause_codes": [], "capture_made": True,
                "members": [{"run_id": member["run_id"], "clock_anchor_status": "bounded", "valid": True}
                            for stage in inventory["stages"] for member in stage["members"]],
                "selection": {"path": str((derived / "selection.json").resolve()), "sha256": selection_sha256},
                "outputs": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in derived.iterdir()},
                "chain_summary_copy": {"d166-prefill-counts-receipt.json": "equal",
                                       "d166-prefill-resolvability-summary.json": "equal"},
            }))
            reviewed_root = Path(temporary) / "reviewed-windows"
            reviewed_window = reviewed_root / plan_id
            reviewed_window.mkdir(parents=True)
            shutil.copyfile(harvest_path, reviewed_window / "harvest.json")
            shutil.copyfile(derived / "selection.json", reviewed_window / "selection.json")
            source_files = sorted(path for path in archive.rglob("*") if path.is_file()
                                  and path.name != "harvest.json" and "derived" not in path.relative_to(archive).parts)
            (archive / "SHA256SUMS").write_text("".join(
                f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(archive).as_posix()}\n"
                for path in source_files))
            # The issuer must now succeed with only the archive present.
            shutil.rmtree(root)
            bundle = Path(temporary) / "pin-bundle"
            bundle.mkdir()
            pin_path = bundle / "prefill-prompt-pin.json"
            by_text = {
                row["prompt_text"]: list(row["prompt_token_ids"])
                for row in ladder["rungs"]
            }
            with mock.patch.object(
                issuer,
                "runtime_prompt_token_ids",
                side_effect=lambda prompt_text, **_kwargs: list(by_text[prompt_text]),
            ), mock.patch.object(issuer, "BLOCK3_WINDOWS_PATH", reviewed_root), \
                    mock.patch.object(issuer, "_committed_record_bytes", side_effect=lambda path: path.read_bytes()):
                issue_code = issuer.main(
                    [
                        "--harvest",
                        str(harvest_path),
                        "--registration",
                        str(ROOT / "configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md"),
                        "--ruling-trace",
                        str(RULING),
                        "--output",
                        str(pin_path),
                    ]
                )
            self.assertEqual((summary_code, selection_code, issue_code), (0, 0, 0))
            self.assertEqual(set(json.loads(pin_path.read_text())), issuer.PROMPT_PIN_KEYS)
            loaded = issuer.d117_v5._load_prefill_prompt_pin(
                pin_path,
                prefill_length=512,
                tokenizer_json_sha256=ladder["tokenizer_json_sha256"],
                panel_sha256=hashlib.sha256(PANEL.read_bytes()).hexdigest(),
            )
            self.assertEqual(loaded["special_token_policy"], "add_special_tokens=true")
            self.assertEqual(loaded["g2a_record_sha256"], selection_sha256)


if __name__ == "__main__":
    unittest.main()
