from __future__ import annotations

import ast
import contextlib
import io
import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.provenance import prompt_token_ids_sha256
from scripts import issue_g2a_prefill_prompt_pin as issuer
from scripts import select_g2a_prefill_length as selector
from tests.test_summarize_g2a_prefill_probe import runner_config_bytes


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_LADDER = ROOT / "tests/fixtures/g2a/pin/prefill-prompt-ladder.json"
GENERATOR = ROOT / "configs/campaigns/d117_contrast_v5/generate_configs.py"
PANEL = ROOT / "configs/model_panels/qwen3_4bit.json"
WORKLOAD = ROOT / "configs/workloads/real_prompts_v1.json"
RULING = ROOT / issuer.d117_v5.PREFILL_RULING_TRACE_PATH
REGISTRATION = ROOT / "configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md"


def load_generator():
    spec = importlib.util.spec_from_file_location("d117_v5_issued_pin_test", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def summary_for(first_qualifying: int | None) -> list[dict[str, object]]:
    rows = []
    for length in selector.LADDER:
        qualifies = first_qualifying is not None and length >= first_qualifying
        rows.append(
            {
                "length": length,
                "small_members": 5,
                "large_members": 1,
                "small_minimum_count": 6 if qualifies else 4,
                "all_small_count_ge_5": qualifies,
            }
        )
    return rows


class IssueG2APrefillPromptPinTests(unittest.TestCase):
    maxDiff = None

    def prepare(
        self,
        temporary: str,
        first_qualifying: int | None,
    ) -> tuple[Path, Path, Path, dict[str, object]]:
        self.archive = Path(temporary) / "archive"
        g2a = self.archive / "g2a-root"
        root = g2a / "window-plan"
        root.mkdir(parents=True)
        derived = self.archive / "derived"
        derived.mkdir()
        self.live_root = issuer.LIVE_WINDOWS_ROOT / "fixture-b3w1"
        ladder_path = root / "prefill-prompt-ladder.json"
        shutil.copyfile(FIXTURE_LADDER, ladder_path)
        summary = summary_for(first_qualifying)
        summary_raw = (
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        summary_path = root / "d166-prefill-resolvability-summary.json"
        summary_path.write_bytes(summary_raw)
        selection = selector.select(
            summary, summary_sha256=hashlib.sha256(summary_raw).hexdigest()
        )
        selection_path = derived / "selection.json"
        selection_path.write_text(
            json.dumps(selection, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        ladder = json.loads(ladder_path.read_text(encoding="utf-8"))
        ladder.update(
            rendering_mode="raw_prompt_text",
            chat_template_applied=False,
            thinking_policy="not_applicable_raw_prefill",
        )
        ladder_path.write_text(
            json.dumps(ladder, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        fixture_inventory = json.loads(
            (ROOT / "tests/fixtures/g2a/pin/g2a-input-inventory.json").read_text()
        )
        inventory = {
            "config_root": str(self.live_root / "prefill-probe-configs"),
            "window_id": "fixture-b3w1",
            "session_id": "fixture-b3w1-calibration",
            "campaign_policy": {"path": issuer.BLOCK3_POLICY_PATH, "sha256": issuer.BLOCK3_POLICY_SHA256},
            "panel": fixture_inventory["panel"],
            "prompt_ladder": {
                "path": str(self.live_root / "window-plan/prefill-prompt-ladder.json"),
                "sha256": hashlib.sha256(ladder_path.read_bytes()).hexdigest(),
            },
            "stages": fixture_inventory["stages"],
        }
        shutil.copytree(ROOT / "tests/fixtures/g2a/pin/config-root", g2a / "prefill-probe-configs")
        inventory_path = root / "g2a-input-inventory.json"
        inventory_raw = (json.dumps(inventory, indent=2, sort_keys=True) + "\n").encode()
        inventory_path.write_bytes(inventory_raw)
        receipt_runs = []
        for stage in inventory["stages"]:
            rung = next(row for row in ladder["rungs"] if row["prefill_tokens"] == stage["prefill_tokens"])
            for member in stage["members"]:
                run_root = g2a / "runs" / member["run_id"]
                run_root.mkdir(parents=True)
                config_raw = runner_config_bytes((g2a / "prefill-probe-configs" / member["config_path"]).read_bytes())
                config_sha = hashlib.sha256(config_raw).hexdigest()
                (run_root / "config.json").write_bytes(config_raw)
                (run_root / "metadata.json").write_text(json.dumps({
                    "run_id": member["run_id"], "config_sha256": config_sha,
                }) + "\n")
                receipt_runs.append(
                    {
                        "run_id": member["run_id"],
                        "stage_id": stage["stage_id"],
                        "config_sha256": config_sha,
                        "realized_prompt_token_count": rung["prefill_tokens"],
                        "realized_prompt_token_ids_sha256": rung["prompt_token_ids_sha256"],
                        "in_window_sample_count": 6,
                    }
                )
        receipt_path = root / "d166-prefill-counts-receipt.json"
        receipt_path.write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.g2a_probe_counts_receipt.v1",
                    "input_inventory_sha256": hashlib.sha256(inventory_raw).hexdigest(),
                    "prompt_ladder_sha256": hashlib.sha256(ladder_path.read_bytes()).hexdigest(),
                    "runs_root": str(self.live_root / "runs"),
                    "runs": receipt_runs,
                    "summary_output_sha256": hashlib.sha256(summary_raw).hexdigest(),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        self.input_inventory = inventory_path
        self.counts_receipt = receipt_path
        custody = self.archive / "night-custody"
        custody.mkdir()
        chain_raw = (
            "export NIGHT_CHAIN_INTERFACE=g2a-reservation-v1\n"
            f"export G2A_ROOT={self.live_root}\n"
            f"export POLICY=/fixture-measurement-g2a-b3w1/{issuer.BLOCK3_POLICY_PATH}\n"
        ).encode()
        (custody / "chain.zsh").write_bytes(chain_raw)
        (custody / "chain.zsh.sha256").write_text(issuer._sha256(chain_raw) + "  chain.zsh\n")
        plan = {"schema": "joulewise.night_plan.v2", "plan_id": "fixture-b3w1",
                "receipt_class": "DIAGNOSTIC_NO_PACK", "t0_epoch_s": 1000,
                "measurement_root": "/fixture-measurement-g2a-b3w1",
                "custody_root": "/fixture-custody",
                "chain_path": "/fixture-custody/chain.zsh",
                "chain_sha256_path": "/fixture-custody/chain.zsh.sha256"}
        (custody / "night_plan.json").write_bytes(issuer._pin_bytes(plan))
        self.harvest = self.archive / "harvest.json"
        self.harvest.write_bytes(issuer._pin_bytes({
            "schema": "joulewise.harvest_g2a_window.v1", "archive_root": str(self.archive.resolve()),
            "plan_id": "fixture-b3w1", "plan_sha256": issuer._sha256((custody / "night_plan.json").read_bytes()),
            "verdict": "SELECT", "cause_codes": [], "capture_made": True,
            "members": [{"run_id": f"member-{i}", "clock_anchor_status": "bounded"} for i in range(6)],
            "selection": {"path": str(selection_path.resolve()), "sha256": "0" * 64},
            "outputs": {}, "chain_summary_copy": {
                "d166-prefill-counts-receipt.json": "equal",
                "d166-prefill-resolvability-summary.json": "equal"},
        }))
        self.refresh_harvest()
        return selection_path, summary_path, ladder_path, ladder

    @staticmethod
    def fixture_tokenizer(ladder: dict[str, object]):
        by_text = {
            rung["prompt_text"]: list(rung["prompt_token_ids"])
            for rung in ladder["rungs"]
        }

        def tokenize(prompt_text: str, **_kwargs: object) -> list[int]:
            return list(by_text[prompt_text])

        return tokenize

    def refresh_harvest(self) -> None:
        """Reseal synthetic inputs so legacy mutation tests reach their target check."""
        derived = self.archive / "derived"
        wp = self.archive / "g2a-root/window-plan"
        for source, target in (("d166-prefill-resolvability-summary.json", "summary.json"),
                               ("d166-prefill-counts-receipt.json", "counts.json")):
            shutil.copyfile(wp / source, derived / target)
        record = json.loads(self.harvest.read_bytes())
        record["selection"]["sha256"] = issuer._sha256((derived / "selection.json").read_bytes())
        record["outputs"] = {path.name: issuer._sha256(path.read_bytes()) for path in derived.iterdir()}
        self.harvest.write_bytes(issuer._pin_bytes(record))

    def arguments(self, output: Path) -> list[str]:
        return ["--harvest", str(self.harvest), "--registration", str(REGISTRATION),
                "--ruling-trace", str(RULING), "--output", str(output)]

    def issue(self, root, selection, summary, ladder_path, ladder, name="prefill-prompt-pin.json"):
        self.refresh_harvest()
        output = root / name
        with mock.patch.object(issuer, "runtime_prompt_token_ids", side_effect=self.fixture_tokenizer(ladder)):
            code = issuer.main(self.arguments(output))
        return code, output

    def issue_direct(self):
        return issuer.issue_pin(harvest_path=self.harvest, registration=REGISTRATION,
                                ruling_trace=RULING, bundle_dir=self.archive.parent)

    def test_all_selected_rungs_and_ruled_4096_no_clear_branch(self) -> None:
        for first_qualifying in (*selector.LADDER, None):
            with self.subTest(first_qualifying=first_qualifying), tempfile.TemporaryDirectory() as temporary:
                selection, summary, ladder_path, ladder = self.prepare(
                    temporary, first_qualifying
                )
                code, output = self.issue(
                    Path(temporary), selection, summary, ladder_path, ladder
                )
                pin = json.loads(output.read_text(encoding="utf-8"))
                selection_hash = hashlib.sha256(selection.read_bytes()).hexdigest()
            expected = first_qualifying if first_qualifying is not None else 4096
            self.assertEqual(code, 0)
            self.assertEqual(pin["prefill_length"], expected)
            self.assertEqual(pin["prompt_tokens"], expected)
            self.assertEqual(pin["g2a_record_sha256"], selection_hash)
            self.assertEqual(
                pin["special_token_policy"], "add_special_tokens=true"
            )
            self.assertEqual(set(pin), issuer.PROMPT_PIN_KEYS)
            self.assertEqual(
                pin["selection_authority"]["g2a_record"]["record_id"],
                f"sha256:{selection_hash}",
            )
            self.assertEqual(
                pin["selection_authority"]["g2a_record"]["path"],
                "selection.json",
            )

    def test_prompt_shorter_than_requested_length_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selection, summary, ladder_path, ladder = self.prepare(temporary, 1024)
            rung = next(row for row in ladder["rungs"] if row["prefill_tokens"] == 1024)
            rung["prompt_token_ids"] = rung["prompt_token_ids"][:-1]
            rung["prompt_token_ids_sha256"] = prompt_token_ids_sha256(
                rung["prompt_token_ids"]
            )
            ladder_path.write_text(json.dumps(ladder) + "\n", encoding="utf-8")
            code, output = self.issue(
                root, selection, summary, ladder_path, ladder
            )
        self.assertEqual(code, 2)
        self.assertFalse(output.exists())

    def test_issuer_pin_validator_refuses_special_token_policy_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selection, summary, ladder_path, ladder = self.prepare(temporary, 512)
            code, output = self.issue(
                root, selection, summary, ladder_path, ladder
            )
            pin = json.loads(output.read_text())
            pin["special_token_policy"] = "add_special_tokens=false"
            with self.assertRaises(issuer.PromptPinError) as raised:
                issuer._validate_pin(pin)
        self.assertEqual(code, 0)
        self.assertEqual(
            str(raised.exception), "prompt_pin_special_token_policy_invalid"
        )

    def test_issuer_special_token_policy_matches_v5_loader_accepted_value(self) -> None:
        tree = ast.parse(GENERATOR.read_text(encoding="utf-8"))
        loader = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "_load_prefill_prompt_pin"
        )
        comparisons = []
        for node in ast.walk(loader):
            if (
                isinstance(node, ast.Compare)
                and len(node.ops) == 1
                and isinstance(node.left, ast.Subscript)
                and isinstance(node.left.slice, ast.Constant)
                and node.left.slice.value == "special_token_policy"
                and len(node.comparators) == 1
                and isinstance(node.comparators[0], ast.Constant)
            ):
                comparisons.append(
                    (type(node.ops[0]).__name__, node.comparators[0].value)
                )
        self.assertEqual(comparisons, [("NotEq", issuer.SPECIAL_TOKEN_POLICY)])

    def test_text_that_does_not_retokenize_to_stored_ids_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selection, summary, ladder_path, ladder = self.prepare(temporary, 2048)
            output = root / "pin.json"

            def mismatched(prompt_text: str, **_kwargs: object) -> list[int]:
                rung = next(
                    row for row in ladder["rungs"] if row["prompt_text"] == prompt_text
                )
                ids = list(rung["prompt_token_ids"])
                ids[-1] += 1
                return ids

            with mock.patch.object(
                issuer, "runtime_prompt_token_ids", side_effect=mismatched
            ):
                code = issuer.main(self.arguments(output))
        self.assertEqual(code, 2)
        self.assertFalse(output.exists())

    def test_bad_selection_and_summary_hashes_refuse(self) -> None:
        for mutation in ("selection", "summary"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                selection, summary, ladder_path, ladder = self.prepare(temporary, 512)
                if mutation == "selection":
                    record = json.loads(selection.read_text(encoding="utf-8"))
                    record["summary_sha256"] = "0" * 64
                    selection.write_text(json.dumps(record) + "\n", encoding="utf-8")
                else:
                    value = json.loads(summary.read_text(encoding="utf-8"))
                    value[0]["small_minimum_count"] = 7
                    summary.write_text(json.dumps(value) + "\n", encoding="utf-8")
                code, output = self.issue(
                    root, selection, summary, ladder_path, ladder
                )
                self.assertEqual(code, 2)
                self.assertFalse(output.exists())

    def test_unknown_length_malformed_branch_and_inconsistent_floor_refuse(self) -> None:
        mutations = {
            "unknown_length": lambda record: record.update(
                {"collection_prefill_tokens": 8192}
            ),
            "malformed_branch": lambda record: record.update({"status": "unknown"}),
            "inconsistent_floor": lambda record: record["rule"].update(
                {"minimum_overlapping_power_interval_count": 6}
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                selection, summary, ladder_path, ladder = self.prepare(temporary, 512)
                record = json.loads(selection.read_text(encoding="utf-8"))
                mutate(record)
                selection.write_text(json.dumps(record) + "\n", encoding="utf-8")
                code, output = self.issue(
                    root, selection, summary, ladder_path, ladder
                )
                self.assertEqual(code, 2)
                self.assertFalse(output.exists())

    def test_issued_selected_and_no_clear_pins_are_accepted_by_v5_loader(self) -> None:
        for first_qualifying, expected in ((1024, 1024), (None, 4096)):
            with self.subTest(first_qualifying=first_qualifying), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                selection, summary, ladder_path, ladder = self.prepare(
                    temporary, first_qualifying
                )
                code, output = self.issue(
                    root, selection, summary, ladder_path, ladder
                )
                generator = load_generator()
                generator.configure_model_pair(
                    PANEL,
                    "qwen3-1p7b",
                    "qwen3-8b",
                    decode_workload_path=WORKLOAD,
                    prefill_length=expected,
                    prefill_prompt_pin_path=output,
                )
            self.assertEqual(code, 0)
            self.assertEqual(generator.PREFILL_LENGTH, expected)
            self.assertEqual(len(generator.PREFILL_TOKEN_IDS["A"]), expected)

    def test_output_is_deterministic_and_existing_output_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selection, summary, ladder_path, ladder = self.prepare(temporary, 512)
            code1, first = self.issue(
                root, selection, summary, ladder_path, ladder, "first.json"
            )
            code2, second = self.issue(
                root, selection, summary, ladder_path, ladder, "second.json"
            )
            raw1 = first.read_bytes()
            raw2 = second.read_bytes()
            code3, _existing = self.issue(
                root, selection, summary, ladder_path, ladder, "first.json"
            )
        self.assertEqual((code1, code2, code3), (0, 0, 2))
        self.assertEqual(raw1, raw2)

    def test_receipt_and_inventory_linkage_refuse_each_mutation(self) -> None:
        cases = {
            "receipt_inventory": (
                lambda receipt, inventory: receipt.__setitem__(
                    "input_inventory_sha256", "0" * 64
                ),
                "counts_receipt_input_inventory_sha256_mismatch",
            ),
            "receipt_summary": (
                lambda receipt, inventory: receipt.__setitem__(
                    "summary_output_sha256", "0" * 64
                ),
                "counts_receipt_summary_output_sha256_mismatch",
            ),
            "receipt_ladder": (
                lambda receipt, inventory: receipt.__setitem__(
                    "prompt_ladder_sha256", "0" * 64
                ),
                "input_inventory_prompt_ladder_sha256_mismatch",
            ),
            "receipt_run_set": (
                lambda receipt, inventory: receipt.__setitem__("runs", receipt["runs"][1:]),
                "counts_receipt_selected_rung_run_set_mismatch",
            ),
        }
        for name, (mutate, reason) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                selection, summary, ladder_path, ladder = self.prepare(temporary, 512)
                receipt = json.loads(self.counts_receipt.read_text())
                inventory = json.loads(self.input_inventory.read_text())
                mutate(receipt, inventory)
                self.counts_receipt.write_text(json.dumps(receipt) + "\n")
                self.refresh_harvest()
                with mock.patch.object(
                    issuer,
                    "runtime_prompt_token_ids",
                    side_effect=self.fixture_tokenizer(ladder),
                ), self.assertRaisesRegex(issuer.PromptPinError, reason):
                    self.issue_direct()

    def test_run_config_binding_refuses_input_hash_content_and_metadata_mutations(self) -> None:
        for mutation in ("input_hash_in_receipt", "nondefault_run_config", "input_bytes", "metadata_hash"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                selection, summary, ladder_path, ladder = self.prepare(temporary, 512)
                inventory = json.loads(self.input_inventory.read_bytes())
                receipt = json.loads(self.counts_receipt.read_bytes())
                member = inventory["stages"][0]["members"][0]
                run = next(row for row in receipt["runs"] if row["run_id"] == member["run_id"])
                run_root = self.archive / "g2a-root/runs" / member["run_id"]
                metadata = json.loads((run_root / "metadata.json").read_bytes())
                if mutation == "input_hash_in_receipt":
                    run["config_sha256"] = member["config_sha256"]
                elif mutation == "nondefault_run_config":
                    config = json.loads((run_root / "config.json").read_bytes())
                    config["sampling"]["power_hz"] += 1
                    raw = runner_config_bytes(json.dumps(config).encode())
                    (run_root / "config.json").write_bytes(raw)
                    run["config_sha256"] = metadata["config_sha256"] = hashlib.sha256(raw).hexdigest()
                elif mutation == "input_bytes":
                    path = self.archive / "g2a-root/prefill-probe-configs" / member["config_path"]
                    path.write_bytes(path.read_bytes() + b" ")
                else:
                    metadata["config_sha256"] = member["config_sha256"]
                (run_root / "metadata.json").write_text(json.dumps(metadata) + "\n")
                self.counts_receipt.write_text(json.dumps(receipt) + "\n")
                self.refresh_harvest()
                with self.assertRaisesRegex(issuer.PromptPinError, "counts_receipt_run_provenance_mismatch"):
                    self.issue_direct()

    def test_unknown_receipt_run_id_refuses_by_exact_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selection, summary, ladder_path, ladder = self.prepare(temporary, 512)
            receipt = json.loads(self.counts_receipt.read_text())
            selected = next(
                row for row in receipt["runs"] if row["stage_id"] == "small-p512"
            )
            selected["run_id"] = "g2a-small-p0512-unknown"
            self.counts_receipt.write_text(json.dumps(receipt) + "\n")
            self.refresh_harvest()
            with mock.patch.object(
                issuer,
                "runtime_prompt_token_ids",
                side_effect=self.fixture_tokenizer(ladder),
            ), self.assertRaises(issuer.PromptPinError) as raised:
                self.issue_direct()
        self.assertEqual(
            str(raised.exception),
            "receipt_run_id_unknown: g2a-small-p0512-unknown",
        )

    @staticmethod
    def rewrite(path: Path, **updates) -> None:
        value = json.loads(path.read_bytes())
        value.update(updates)
        path.write_bytes(issuer._pin_bytes(value))

    def test_harvest_refusals_have_specific_codes(self) -> None:
        cases = [
            ("harvest_schema_invalid", "schema"),
            ("harvest_archive_root_mismatch", "archive_root"),
            ("harvest_verdict_not_select", "verdict"),
            ("harvest_select_has_causes", "causes"),
            ("harvest_selection_binding_invalid", "selection_binding"),
            ("harvest_selection_sha256_mismatch", "selection_hash"),
            ("harvest_selection_sha256_mismatch", "selection_bytes"),
            ("harvest_output_sha256_mismatch", "selection_output_hash"),
            ("harvest_output_sha256_mismatch", "summary_output_hash"),
            ("harvest_plan_sha256_mismatch", "plan_hash"),
            ("harvest_plan_binding_invalid", "plan_identity"),
            ("harvest_chain_sha256_mismatch", "chain_hash"),
            ("harvest_chain_binding_invalid", "chain_interface"),
            ("harvest_block3_binding_mismatch", "block2_inventory"),
            ("harvest_block3_binding_mismatch", "block2_chain"),
            ("harvest_block3_binding_mismatch", "block2_label"),
            ("harvest_block3_binding_mismatch", "wrong_policy_hash"),
            ("archive_path_outside_root", "selection_escape"),
            ("archive_path_outside_root", "selection_symlink"),
            ("counts_receipt_run_provenance_mismatch", "config_symlink"),
            ("live_root_path_outside_mapping", "config_root_escape"),
            ("live_root_path_outside_mapping", "runs_root_escape"),
            ("live_root_path_outside_mapping", "ladder_escape"),
            ("live_root_path_outside_mapping", "other_inventory_escape"),
            ("live_root_path_outside_mapping", "traversal"),
            ("harvest_chain_summary_copy_invalid", "chain_copy_status"),
            ("harvest_chain_summary_byte_mismatch", "chain_copy_bytes"),
        ]
        for code, mutation in cases:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                selection, summary, ladder_path, ladder = self.prepare(temporary, 512)
                record = json.loads(self.harvest.read_bytes())
                inventory = json.loads(self.input_inventory.read_bytes())
                plan_path = self.archive / "night-custody/night_plan.json"
                plan = json.loads(plan_path.read_bytes())
                chain = self.archive / "night-custody/chain.zsh"
                if mutation == "schema": record["schema"] = "wrong"
                elif mutation == "archive_root": record["archive_root"] = str(self.archive.parent)
                elif mutation == "verdict": record["verdict"] = "RECOVER"
                elif mutation == "causes": record["cause_codes"] = ["bracket_incomplete"]
                elif mutation == "selection_binding": record["selection"] = {}
                elif mutation == "selection_hash": record["selection"]["sha256"] = "0" * 64
                elif mutation == "selection_bytes": selection.write_bytes(selection.read_bytes() + b" ")
                elif mutation == "selection_output_hash": record["outputs"]["selection.json"] = "0" * 64
                elif mutation == "summary_output_hash": record["outputs"]["summary.json"] = "0" * 64
                elif mutation == "plan_hash": record["plan_sha256"] = "0" * 64
                elif mutation == "plan_identity": plan["plan_id"] = "other-window"
                elif mutation == "chain_hash": chain.write_bytes(chain.read_bytes() + b"# changed\n")
                elif mutation == "chain_interface": chain.write_bytes(chain.read_bytes().replace(b"g2a-reservation-v1", b"wrong"))
                elif mutation == "block2_inventory": inventory["campaign_policy"]["path"] = "configs/campaign_policies/quiet_mac_p2_g2a_b2.json"
                elif mutation == "block2_chain": chain.write_bytes(chain.read_bytes().replace(b"quiet_mac_p2_g2a_b3", b"quiet_mac_p2_g2a_b2"))
                elif mutation == "block2_label":
                    plan["measurement_root"] = plan["measurement_root"].replace("b3w1", "b2w1")
                    chain.write_bytes(chain.read_bytes().replace(b"fixture-measurement-g2a-b3w1", b"fixture-measurement-g2a-b2w1"))
                elif mutation == "wrong_policy_hash": inventory["campaign_policy"]["sha256"] = "0" * 64
                elif mutation == "selection_escape": record["selection"]["path"] = str(self.archive.parent / "outside.json")
                elif mutation in {"selection_symlink", "config_symlink"}:
                    source = selection if mutation == "selection_symlink" else self.archive / "g2a-root/prefill-probe-configs" / inventory["stages"][0]["members"][0]["config_path"]
                    outside = self.archive.parent / "outside.json"
                    outside.write_bytes(source.read_bytes())
                    source.unlink()
                    source.symlink_to(outside)
                elif mutation == "config_root_escape": inventory["config_root"] = str(self.live_root.parent / "other-window/prefill-probe-configs")
                elif mutation == "runs_root_escape":
                    self.rewrite(self.counts_receipt, runs_root=str(self.live_root.parent / "other-window/runs"))
                    self.refresh_harvest()
                    record = json.loads(self.harvest.read_bytes())
                elif mutation == "ladder_escape": inventory["prompt_ladder"]["path"] = "/unmapped/ladder.json"
                elif mutation == "other_inventory_escape": inventory["calibration_plan"] = {"path": "/unmapped/calibration_plan.json"}
                elif mutation == "traversal": inventory["config_root"] = str(self.live_root / "../other-window/configs")
                elif mutation == "chain_copy_status": record["chain_summary_copy"] = {}
                elif mutation == "chain_copy_bytes": summary.write_bytes(summary.read_bytes() + b" ")
                self.input_inventory.write_bytes(issuer._pin_bytes(inventory))
                if mutation in {"plan_identity", "block2_label"}:
                    plan_path.write_bytes(issuer._pin_bytes(plan))
                    record["plan_sha256"] = issuer._sha256(plan_path.read_bytes())
                if mutation in {"chain_interface", "block2_chain", "block2_label"}:
                    (chain.parent / "chain.zsh.sha256").write_text(issuer._sha256(chain.read_bytes()))
                self.harvest.write_bytes(issuer._pin_bytes(record))
                with self.assertRaisesRegex(issuer.PromptPinError, "^" + code + "$"):
                    self.issue_direct()

    def test_missing_archive_files_refuse_without_live_fallback(self) -> None:
        paths = ["derived/selection.json", "derived/summary.json", "derived/counts.json",
                 "night-custody/night_plan.json", "night-custody/chain.zsh",
                 "g2a-root/window-plan/g2a-input-inventory.json",
                 "g2a-root/window-plan/prefill-prompt-ladder.json",
                 "g2a-root/window-plan/d166-prefill-counts-receipt.json",
                 "g2a-root/window-plan/d166-prefill-resolvability-summary.json",
                 "g2a-root/runs/g2a-small-p0512-r01/config.json",
                 "g2a-root/runs/g2a-small-p0512-r01/metadata.json",
                 "g2a-root/prefill-probe-configs/small-p512/g2a-small-p0512-r01.json"]
        for path in paths:
            with self.subTest(path=path), tempfile.TemporaryDirectory() as temporary:
                self.prepare(temporary, 512)
                (self.archive / path).unlink()
                with self.assertRaisesRegex(issuer.PromptPinError, "^archive_file_missing$"):
                    self.issue_direct()

    def test_registration_digest_and_strict_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            self.prepare(temporary, 512)
            wrong = Path(temporary) / "registration.md"
            wrong.write_bytes(REGISTRATION.read_bytes() + b" ")
            with self.assertRaisesRegex(issuer.PromptPinError, "^registration_sha256_mismatch$"):
                issuer.issue_pin(harvest_path=self.harvest, registration=wrong, ruling_trace=RULING, bundle_dir=Path(temporary))
            raw = self.harvest.read_bytes().rstrip()
            self.harvest.write_bytes(raw[:-1] + b', "verdict": "SELECT"}')
            with self.assertRaisesRegex(issuer.PromptPinError, "^duplicate_key:verdict$"):
                self.issue_direct()

    def test_archive_only_reads_when_live_window_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            selection, summary, ladder_path, ladder = self.prepare(temporary, 512)
            self.assertFalse(self.live_root.exists())
            read_bytes = Path.read_bytes
            opened = []
            def guarded(path):
                self.assertFalse(path.is_relative_to(issuer.LIVE_WINDOWS_ROOT), str(path))
                opened.append(path)
                return read_bytes(path)
            with mock.patch.object(Path, "read_bytes", guarded), mock.patch.object(
                    issuer, "runtime_prompt_token_ids", side_effect=self.fixture_tokenizer(ladder)):
                pin = self.issue_direct()
            self.assertEqual(pin["g2a_record_sha256"], issuer._sha256(selection.read_bytes()))
            self.assertIn((self.archive / "g2a-root/runs/g2a-small-p0512-r01/config.json").resolve(), opened)
            with self.assertRaisesRegex(issuer.PromptPinError, "^live_root_path_outside_mapping$"):
                issuer._read_bytes(self.live_root / "never-open.json", label="test")

    def test_harvest_summary_is_authoritative_when_chain_differs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            selection, summary, ladder_path, ladder = self.prepare(temporary, 512)
            summary.write_bytes(b"[]\n")
            self.rewrite(self.harvest, chain_summary_copy={
                "d166-prefill-counts-receipt.json": "equal",
                "d166-prefill-resolvability-summary.json": "differs_invalid_members_excluded"})
            with mock.patch.object(issuer, "runtime_prompt_token_ids", side_effect=self.fixture_tokenizer(ladder)):
                pin = self.issue_direct()
            self.assertEqual(pin["g2a_record_sha256"], issuer._sha256(selection.read_bytes()))

    def recover(self, *, label="b3w1", statuses=None, t0=1000) -> Path:
        statuses = statuses if statuses is not None else ["bounded"] * 6
        record = json.loads(self.harvest.read_bytes())
        plan_path = self.archive / "night-custody/night_plan.json"
        plan = json.loads(plan_path.read_bytes())
        plan_id = "fixture-" + label
        previous_live = str(self.live_root)
        self.live_root = issuer.LIVE_WINDOWS_ROOT / plan_id
        plan.update(plan_id=plan_id, measurement_root="/fixture-measurement-g2a-" + label, t0_epoch_s=t0)
        plan_path.write_bytes(issuer._pin_bytes(plan))
        inventory = json.loads(self.input_inventory.read_bytes())
        inventory.update(window_id=plan_id, session_id=plan_id + "-calibration")
        inventory["config_root"] = str(self.live_root / "prefill-probe-configs")
        inventory["prompt_ladder"]["path"] = str(self.live_root / "window-plan/prefill-prompt-ladder.json")
        self.input_inventory.write_bytes(issuer._pin_bytes(inventory))
        chain = self.archive / "night-custody/chain.zsh"
        chain.write_text(chain.read_text().replace(previous_live, str(self.live_root)).replace(
            "/fixture-measurement-g2a-b3w1/", plan["measurement_root"] + "/"))
        (chain.parent / "chain.zsh.sha256").write_text(issuer._sha256(chain.read_bytes()))
        record.update(plan_id=plan_id, plan_sha256=issuer._sha256(plan_path.read_bytes()), verdict="RECOVER",
                      cause_codes=["synthetic_recovery"], capture_made=True,
                      members=[{"run_id": f"member-{i}", "clock_anchor_status": status} for i, status in enumerate(statuses)])
        record.pop("selection", None)
        self.harvest.write_bytes(issuer._pin_bytes(record))
        return self.harvest

    def test_end_state_clock_trigger_matches_registered_boundaries(self) -> None:
        cases = [(["failed"] * 3 + ["bounded"] * 2, True),
                 (["failed"] * 3 + ["bounded"] * 3, False),
                 (["failed"] * 4 + ["not recorded"] * 2, False),
                 (["failed"] * 3 + ["bounded"] * 2 + ["not recorded"] * 10, True),
                 (["bounded"] * 6, False)]
        for statuses, accepted in cases:
            with self.subTest(statuses=statuses), tempfile.TemporaryDirectory() as temporary:
                self.prepare(temporary, 512)
                path = self.recover(statuses=statuses)
                record = issuer._load_harvest(path, verdict="RECOVER")
                if accepted:
                    raw = issuer._end_state_record([record])
                    binding = json.loads(raw)
                    self.assertEqual(set(binding), {"schema_version", "registration_sha256", "recover_harvests", "trigger"})
                    self.assertEqual(binding["trigger"], "first_recover_systematic_clock_anchor_failure")
                    self.assertEqual(binding["registration_sha256"], issuer.BLOCK3_REGISTRATION_SHA256)
                    self.assertEqual(binding["recover_harvests"], [{"path": str(path.resolve()), "sha256": issuer._sha256(path.read_bytes())}])
                    self.assertNotIn(b"no_rung", raw)
                    self.assertNotIn(b"selection", raw)
                else:
                    with self.assertRaisesRegex(issuer.PromptPinError, "^end_state_trigger_not_met$"):
                        issuer._end_state_record([record])

    def test_end_state_two_recover_windows_and_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first_root, second_root = Path(temporary) / "first", Path(temporary) / "second"
            self.prepare(str(first_root), 512)
            first = self.recover()
            self.prepare(str(second_root), 512)
            second = self.recover(label="b3w2", t0=2000)
            records = [issuer._load_harvest(path, verdict="RECOVER") for path in (first, second)]
            binding = json.loads(issuer._end_state_record(records))
            self.assertEqual(binding["trigger"], "recovery_window_also_recover")
            self.assertEqual(len(binding["recover_harvests"]), 2)
            for invalid in (records[::-1], [records[0], records[0]], [records[1]]):
                with self.assertRaisesRegex(issuer.PromptPinError, "^end_state_window_order_invalid$"):
                    issuer._end_state_record(invalid)

    def test_end_state_refusals_and_cli_make_no_output(self) -> None:
        cases = [("verdict", "harvest_recover_required"),
                 ("capture", "harvest_recover_capture_required"),
                 ("members", "end_state_members_invalid"),
                 ("one_bounded", "end_state_trigger_not_met"),
                 ("zero", "end_state_recover_count_invalid"),
                 ("three", "end_state_recover_count_invalid"),
                 ("mixed_mode", "issuer_mode_inputs_invalid")]
        for mutation, code in cases:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                self.prepare(temporary, 512)
                path = self.recover()
                if mutation == "verdict": self.rewrite(path, verdict="NULL")
                elif mutation == "capture": self.rewrite(path, capture_made=False)
                elif mutation == "members": self.rewrite(path, members=[{}])
                paths = [] if mutation == "zero" else [path] * (3 if mutation == "three" else 1)
                kwargs = {"harvest_path": path} if mutation == "mixed_mode" else {}
                with self.assertRaisesRegex(issuer.PromptPinError, "^" + code + "$"):
                    issuer.issue_pin(end_state=True, recover_harvests=paths, registration=REGISTRATION,
                                     ruling_trace=RULING, bundle_dir=Path(temporary), **kwargs)
                output = Path(temporary) / "end-state-pin.json"
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    result = issuer.main(["--end-state", "--recover-harvest", str(path),
                                          "--registration", str(REGISTRATION), "--ruling-trace", str(RULING),
                                          "--output", str(output)])
                self.assertEqual(result, 2)
                self.assertFalse(output.exists())
                self.assertFalse((output.parent / "end-state-record.json").exists())

    def test_end_state_reencodes_default_and_refuses_pending_schema_ruling(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            _, _, ladder_path, ladder = self.prepare(temporary, 512)
            path = self.recover(statuses=["failed"] * 5)
            rung = next(item for item in ladder["rungs"] if item["prefill_tokens"] == 4096)
            with mock.patch.object(issuer, "runtime_prompt_token_ids", side_effect=self.fixture_tokenizer(ladder)) as tokenizer:
                with self.assertRaisesRegex(issuer.PromptPinError, "^end_state_schema_ruling_required$"):
                    issuer.issue_pin(end_state=True, recover_harvests=[path], registration=REGISTRATION,
                                     ruling_trace=RULING, bundle_dir=Path(temporary))
                tokenizer.assert_called_once_with(rung["prompt_text"], tokenizer_json_sha256=ladder["tokenizer_json_sha256"])
            with mock.patch.object(issuer, "runtime_prompt_token_ids", return_value=[]):
                with self.assertRaisesRegex(issuer.PromptPinError, "^runtime_prompt_token_ids_mismatch:"):
                    issuer.issue_pin(end_state=True, recover_harvests=[path], registration=REGISTRATION,
                                     ruling_trace=RULING, bundle_dir=Path(temporary))


if __name__ == "__main__":
    unittest.main()
