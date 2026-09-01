from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.doctor import inspect_configs
from scripts import generate_g2a_probe_inputs as probe
from scripts import issue_g2a_prefill_prompt_pin as issuer


ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "configs/model_panels/qwen3_4bit.json"
POLICY = ROOT / "configs/campaign_policies/quiet_mac_p2_production.json"
TOKENIZER_JSON = Path(
    "/Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit/tokenizer.json"
)


class _FakeRuntimeTokenizer:
    def encode(self, text: str, add_special_tokens: bool = True) -> list[int]:
        if not add_special_tokens:
            raise AssertionError("the producer must request runtime raw mode")
        if text == "LONG TEST PROMPT SOURCE":
            return list(range(4096))
        if text.startswith("This source is deliberately too short"):
            return list(range(12))
        if text == probe.PROMPT_SENTENCE:
            return list(range(7))
        for length, closing in probe.CLOSING_SENTENCES.items():
            if text == closing:
                return list(range(probe.EXPECTED_CLOSING_TOKEN_COUNTS[length]))
            closing_count = probe.EXPECTED_CLOSING_TOKEN_COUNTS[length]
            repeat_count = (length - closing_count) // 7
            expected = " ".join(
                [probe.PROMPT_SENTENCE] * repeat_count + [closing]
            )
            if text == expected:
                return [index % 151936 for index in range(length)]
        return [0]


IDENTITY = {
    "os_build": "25F84",
    "hardware_model": "Mac15,9",
    "power_policy": "ac_high_power",
    "sampling_interval_ms": 100,
    "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
    "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
}
T1 = {
    **IDENTITY,
    "powermetrics_sha256": "1" * 64,
    "anchor_method_version": "clock_anchor_v3",
    "mlx_version": "0.test",
    "protocol_sha256": "2" * 64,
}
ACCEPTANCE = {
    "acceptance_id": "d079_calibration_acceptance_v2_n17_r6",
    "ledger_cutoff": {"sequence": 76, "head_digest": "3" * 64},
}
LEDGER_BINDING = {
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


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GenerateG2AProbeInputsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "g2a"
        self.tokenizer_patch = mock.patch.object(
            probe, "_load_runtime_tokenizer", return_value=_FakeRuntimeTokenizer()
        )
        self.tokenizer_patch.start()
        self.addCleanup(self.tokenizer_patch.stop)

    def _build(self, **overrides: object) -> None:
        arguments = {
            "root": self.root,
            "panel_path": PANEL,
            "small_members": 5,
            "large_members": 1,
            "lengths": probe.PREFILL_LENGTHS,
        }
        arguments.update(overrides)
        probe.build_probes(**arguments)

    def _bind(self) -> None:
        with (
            mock.patch.object(
                probe,
                "_derive_live_vectors",
                return_value=(copy.deepcopy(IDENTITY), copy.deepcopy(T1), copy.deepcopy(ACCEPTANCE)),
            ),
            mock.patch.object(
                probe,
                "_authenticate_ledger_and_acceptance",
                return_value=copy.deepcopy(LEDGER_BINDING),
            ),
        ):
            probe.bind_window(
                root=self.root,
                ledger=Path("/test/calibration_observation_ledger.jsonl"),
                head_pin=ROOT / "configs/calibration/calibration_ledger_head.json",
                campaign_policy=POLICY,
                power_policy="ac_high_power",
                window_id="window-g2a-test",
                session_id="session-g2a-test",
                evidence_root_id="evidence-g2a-test",
            )

    def _check(self) -> None:
        with (
            mock.patch.object(
                probe,
                "_derive_live_vectors",
                return_value=(copy.deepcopy(IDENTITY), copy.deepcopy(T1), copy.deepcopy(ACCEPTANCE)),
            ),
            mock.patch.object(
                probe,
                "_authenticate_ledger_and_acceptance",
                return_value=copy.deepcopy(LEDGER_BINDING),
            ),
        ):
            probe.check_inputs(
                root=self.root,
                panel_path=PANEL,
                ledger=Path("/test/calibration_observation_ledger.jsonl"),
                head_pin=ROOT / "configs/calibration/calibration_ledger_head.json",
                campaign_policy=POLICY,
            )

    def _build_and_bind(self) -> None:
        self._build()
        self._bind()

    def _inventory(self) -> dict:
        return json.loads(
            (self.root / "window-plan/g2a-input-inventory.json").read_text()
        )

    def _mutated_panel(self, mutate) -> Path:
        value = json.loads(PANEL.read_text())
        mutate(value)
        path = Path(self.temporary.name) / "panel.json"
        _write_json(path, value)
        return path

    def test_exact_five_small_one_large_across_four_rungs(self) -> None:
        self._build_and_bind()
        inventory = self._inventory()
        self.assertEqual(
            [stage["stage_id"] for stage in inventory["stages"]],
            [
                "small-p512",
                "small-p1024",
                "small-p2048",
                "small-p4096",
                "large-p512",
                "large-p1024",
                "large-p2048",
                "large-p4096",
            ],
        )
        self.assertEqual(
            [len(stage["members"]) for stage in inventory["stages"]],
            [5, 5, 5, 5, 1, 1, 1, 1],
        )
        self.assertEqual(
            len({member["run_id"] for stage in inventory["stages"] for member in stage["members"]}),
            24,
        )

    def test_fewer_than_five_small_members_refuses(self) -> None:
        with self.assertRaisesRegex(probe.G2AProbeError, "small_member_count_below_five"):
            self._build(small_members=4)

    def test_zero_large_members_refuses(self) -> None:
        with self.assertRaisesRegex(probe.G2AProbeError, "large_member_count_below_one"):
            self._build(large_members=0)

    def test_length_outside_ruled_set_refuses(self) -> None:
        with self.assertRaisesRegex(probe.G2AProbeError, "prefill_length_set_invalid"):
            self._build(lengths=(512, 1024, 2048, 8192))

    def test_panel_revision_mismatch_refuses(self) -> None:
        path = self._mutated_panel(
            lambda value: value["entries"][0].__setitem__("revision", "0" * 40)
        )
        with self.assertRaisesRegex(probe.G2AProbeError, "model_revision_mismatch"):
            self._build(panel_path=path)

    def test_panel_thinking_mismatch_refuses(self) -> None:
        path = self._mutated_panel(
            lambda value: value["entries"][0].__setitem__("enable_thinking", "true")
        )
        with self.assertRaisesRegex(
            probe.G2AProbeError, "panel_thinking_policy_mismatch|model_panel_refused"
        ):
            self._build(panel_path=path)

    def test_panel_tokenizer_mismatch_refuses(self) -> None:
        path = self._mutated_panel(
            lambda value: value["entries"][0].__setitem__(
                "tokenizer_json_sha256", "0" * 64
            )
        )
        with self.assertRaisesRegex(
            probe.G2AProbeError,
            "model_panel_refused|pair_tokenizer_identity_mismatch|model_tokenizer_json_sha256_mismatch",
        ):
            self._build(panel_path=path)

    def test_duplicate_run_id_refuses(self) -> None:
        self._build_and_bind()
        inventory_path = self.root / "window-plan/g2a-input-inventory.json"
        inventory = json.loads(inventory_path.read_text())
        stage = inventory["stages"][0]
        manifest_path = self.root / "prefill-probe-configs" / stage["manifest"]["path"]
        manifest = json.loads(manifest_path.read_text())
        manifest["executed_order"][1]["run_id"] = manifest["executed_order"][0]["run_id"]
        _write_json(manifest_path, manifest)
        stage["manifest"]["sha256"] = _sha256(manifest_path)
        _write_json(inventory_path, inventory)
        with self.assertRaisesRegex(probe.G2AProbeError, "duplicate_run_id"):
            self._check()

    def test_mutated_member_hash_refuses(self) -> None:
        self._build_and_bind()
        path = self.root / "prefill-probe-configs/small-p512/g2a-small-p0512-r01.json"
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaisesRegex(probe.G2AProbeError, "config_sha256_mismatch"):
            self._check()

    def test_runtime_adapter_and_campaign_policy_bindings_refuse_drift(self) -> None:
        self._build_and_bind()
        inventory_path = self.root / "window-plan/g2a-input-inventory.json"
        inventory = json.loads(inventory_path.read_text())
        inventory["runtime_adapter"]["sha256"] = "0" * 64
        _write_json(inventory_path, inventory)
        with self.assertRaisesRegex(probe.G2AProbeError, "runtime_adapter_sha256_mismatch"):
            self._check()

        inventory["runtime_adapter"]["sha256"] = _sha256(
            ROOT / "joulewise/adapters/mlx_runtime.py"
        )
        _write_json(inventory_path, inventory)
        alternate = Path(self.temporary.name) / "same-policy.json"
        alternate.write_bytes(POLICY.read_bytes())
        with (
            mock.patch.object(
                probe,
                "_derive_live_vectors",
                return_value=(copy.deepcopy(IDENTITY), copy.deepcopy(T1), copy.deepcopy(ACCEPTANCE)),
            ),
            mock.patch.object(
                probe,
                "_authenticate_ledger_and_acceptance",
                return_value=copy.deepcopy(LEDGER_BINDING),
            ),
            self.assertRaisesRegex(probe.G2AProbeError, "campaign_policy_mismatch"),
        ):
            probe.check_inputs(
                root=self.root,
                panel_path=PANEL,
                ledger=Path("/test/calibration_observation_ledger.jsonl"),
                head_pin=ROOT / "configs/calibration/calibration_ledger_head.json",
                campaign_policy=alternate,
            )

    def test_marker_bearing_config_refuses_even_when_hashes_are_rebound(self) -> None:
        self._build_and_bind()
        inventory_path = self.root / "window-plan/g2a-input-inventory.json"
        inventory = json.loads(inventory_path.read_text())
        stage = inventory["stages"][0]
        config_path = self.root / "prefill-probe-configs" / stage["members"][0]["config_path"]
        config = json.loads(config_path.read_text())
        config["run_metadata"]["tags"].append("launch_lineage_required")
        _write_json(config_path, config)
        config_sha = _sha256(config_path)
        stage["members"][0]["config_sha256"] = config_sha
        manifest_path = self.root / "prefill-probe-configs" / stage["manifest"]["path"]
        manifest = json.loads(manifest_path.read_text())
        manifest["executed_order"][0]["config_sha256"] = config_sha
        _write_json(manifest_path, manifest)
        stage["manifest"]["sha256"] = _sha256(manifest_path)
        _write_json(inventory_path, inventory)
        with self.assertRaisesRegex(
            probe.G2AProbeError,
            "benchmark_config_content_mismatch|launch_lineage_marker_forbidden",
        ):
            self._check()

    def test_unknown_stage_json_refuses(self) -> None:
        self._build_and_bind()
        _write_json(
            self.root / "prefill-probe-configs/small-p512/unlisted.json",
            {"run_id": "unlisted"},
        )
        with self.assertRaisesRegex(probe.G2AProbeError, "stage_json_cover_mismatch"):
            self._check()

    def test_preexisting_mismatched_output_refuses(self) -> None:
        self._build()
        ladder_path = self.root / "window-plan/prefill-prompt-ladder.json"
        ladder_path.write_bytes(ladder_path.read_bytes() + b" ")
        with self.assertRaisesRegex(probe.G2AProbeError, "preexisting_output_mismatch"):
            self._build()

    def test_generated_configs_pass_doctor_with_no_warnings(self) -> None:
        self._build()
        paths = sorted(
            path
            for path in (self.root / "prefill-probe-configs").glob("*/*.json")
            if path.name != "order_manifest.json"
        )
        report = inspect_configs(paths)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["warnings"], [])
        self.assertEqual(len(report["configs"]), 24)

    def test_inventory_field_names_match_shared_schema_exactly(self) -> None:
        self._build_and_bind()
        inventory = self._inventory()
        self.assertEqual(set(inventory), probe.INVENTORY_KEYS)
        for name in (
            "panel",
            "campaign_policy",
            "runtime_adapter",
            "prompt_ladder",
            "identity_epoch",
            "t1_bindings",
        ):
            self.assertEqual(set(inventory[name]), probe.HASH_REFERENCE_KEYS)
        self.assertEqual(set(inventory["calibration_plan"]), probe.PLAN_REFERENCE_KEYS)
        self.assertEqual(inventory["runtime_adapter"]["path"], "joulewise/adapters/mlx_runtime.py")
        self.assertRegex(inventory["repo_head"], r"^[0-9a-f]{40}$")
        self.assertEqual(inventory["rendering_mode"], "raw_prompt_text")
        self.assertFalse(inventory["chat_template_applied"])
        self.assertEqual(inventory["thinking_policy"], "not_applicable_raw_prefill")
        for stage in inventory["stages"]:
            self.assertEqual(set(stage), probe.STAGE_KEYS)
            self.assertEqual(set(stage["manifest"]), probe.HASH_REFERENCE_KEYS)
            for member in stage["members"]:
                self.assertEqual(set(member), probe.MEMBER_KEYS)

    def test_ladder_field_names_and_2048_construction_are_exact(self) -> None:
        self._build()
        ladder = json.loads(
            (self.root / "window-plan/prefill-prompt-ladder.json").read_text()
        )
        self.assertEqual(set(ladder), probe.LADDER_KEYS)
        self.assertEqual(ladder["rendering_mode"], "raw_prompt_text")
        self.assertFalse(ladder["chat_template_applied"])
        self.assertEqual(ladder["thinking_policy"], "not_applicable_raw_prefill")
        for rung in ladder["rungs"]:
            self.assertEqual(set(rung), probe.RUNG_KEYS)
        rung = next(row for row in ladder["rungs"] if row["prefill_tokens"] == 2048)
        self.assertEqual(rung["repeat_count"], 291)
        self.assertEqual(rung["closing_sentence"], probe.PROMPT_FINAL_SENTENCE)
        self.assertEqual(
            rung["prompt_text"],
            " ".join([probe.PROMPT_SENTENCE] * 291 + [probe.PROMPT_FINAL_SENTENCE]),
        )

    def test_actual_emitted_ladder_is_accepted_by_issuer_closed_schema(self) -> None:
        self._build()
        ladder = json.loads(
            (self.root / "window-plan/prefill-prompt-ladder.json").read_text()
        )
        self.assertEqual(issuer.PROMPT_LADDER_KEYS, probe.LADDER_KEYS)
        tokenizer_hash, by_length = issuer._validate_ladder(ladder)
        self.assertEqual(tokenizer_hash, ladder["tokenizer_json_sha256"])
        self.assertEqual(tuple(sorted(by_length)), probe.PREFILL_LENGTHS)

    def test_actual_emitted_ladder_extra_key_refuses_at_issuer_by_name(self) -> None:
        self._build()
        ladder = json.loads(
            (self.root / "window-plan/prefill-prompt-ladder.json").read_text()
        )
        ladder["unexpected"] = True
        with self.assertRaises(issuer.PromptPinError) as raised:
            issuer._validate_ladder(ladder)
        self.assertEqual(str(raised.exception), "prompt_ladder_closed_schema_mismatch")

    def test_probe_workload_shape_matches_v5_prefill_except_diagnostic_name(self) -> None:
        self._build()
        config = json.loads(
            (
                self.root
                / "prefill-probe-configs/small-p512/g2a-small-p0512-r01.json"
            ).read_text()
        )
        probe_workload = config["workload_profile"]
        with mock.patch.multiple(
            issuer.d117_v5,
            PREFILL_LENGTH=512,
            PREFILL_PROMPT_TEXT=probe_workload["prompt_text"],
        ):
            v5_workload = issuer.d117_v5.workload_for("prefill")
        self.assertEqual(
            {key: value for key, value in probe_workload.items() if key != "name"},
            {key: value for key, value in v5_workload.items() if key != "name"},
        )
        self.assertEqual(probe_workload["name"], "g2a_prefill_p512_diagnostic")
        self.assertEqual(v5_workload["name"], "df_ph_prefill_p512_candidate")

    def test_check_is_read_only(self) -> None:
        self._build_and_bind()

        def digest_tree() -> dict[str, str]:
            return {
                path.relative_to(self.root).as_posix(): _sha256(path)
                for path in sorted(self.root.rglob("*"))
                if path.is_file()
            }

        before = digest_tree()
        self._check()
        self.assertEqual(digest_tree(), before)

    @unittest.skipUnless(
        importlib.util.find_spec("tokenizers") is not None and TOKENIZER_JSON.is_file(),
        "real Qwen3 tokenizer test requires the optional tokenizers library and local tokenizer.json",
    )
    def test_real_tokenizer_retokenizes_each_rung_to_exact_length(self) -> None:
        from tokenizers import Tokenizer

        tokenizer = Tokenizer.from_file(str(TOKENIZER_JSON))
        for length in probe.PREFILL_LENGTHS:
            closing = probe.CLOSING_SENTENCES[length]
            closing_count = len(tokenizer.encode(closing, add_special_tokens=True).ids)
            self.assertEqual(
                closing_count,
                probe.EXPECTED_CLOSING_TOKEN_COUNTS[length],
                closing,
            )
            repeat_count = (length - closing_count) // 7
            text = " ".join([probe.PROMPT_SENTENCE] * repeat_count + [closing])
            self.assertEqual(
                len(tokenizer.encode(text, add_special_tokens=True).ids), length, text[-80:]
            )


if __name__ == "__main__":
    unittest.main()
