from __future__ import annotations

import ast
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


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_LADDER = ROOT / "tests/fixtures/g2a/pin/prefill-prompt-ladder.json"
GENERATOR = ROOT / "configs/campaigns/d117_contrast_v5/generate_configs.py"
PANEL = ROOT / "configs/model_panels/qwen3_4bit.json"
WORKLOAD = ROOT / "configs/workloads/real_prompts_v1.json"
RULING = ROOT / issuer.d117_v5.PREFILL_RULING_TRACE_PATH


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
        root = Path(temporary) / "window-plan"
        root.mkdir()
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
        selection_path = root / "d166-prefill-selection.json"
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
            "panel": fixture_inventory["panel"],
            "prompt_ladder": {
                "path": str(ladder_path),
                "sha256": hashlib.sha256(ladder_path.read_bytes()).hexdigest(),
            },
            "stages": fixture_inventory["stages"],
        }
        inventory_path = root / "g2a-input-inventory.json"
        inventory_raw = (json.dumps(inventory, indent=2, sort_keys=True) + "\n").encode()
        inventory_path.write_bytes(inventory_raw)
        receipt_runs = []
        for stage in inventory["stages"]:
            rung = next(row for row in ladder["rungs"] if row["prefill_tokens"] == stage["prefill_tokens"])
            for member in stage["members"]:
                receipt_runs.append(
                    {
                        "run_id": member["run_id"],
                        "stage_id": stage["stage_id"],
                        "config_sha256": member["config_sha256"],
                        "realized_prompt_token_count": rung["prefill_tokens"],
                        "realized_prompt_token_ids_sha256": rung["prompt_token_ids_sha256"],
                        "in_window_sample_count": 6,
                    }
                )
        receipt_path = root / "g2a-counts-receipt.json"
        receipt_path.write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.g2a_probe_counts_receipt.v1",
                    "input_inventory_sha256": hashlib.sha256(inventory_raw).hexdigest(),
                    "prompt_ladder_sha256": hashlib.sha256(ladder_path.read_bytes()).hexdigest(),
                    "runs_root": str(root / "runs"),
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

    def issue(
        self,
        root: Path,
        selection: Path,
        summary: Path,
        ladder_path: Path,
        ladder: dict[str, object],
        name: str = "prefill-prompt-pin.json",
    ) -> tuple[int, Path]:
        output = root / name
        with mock.patch.object(
            issuer,
            "runtime_prompt_token_ids",
            side_effect=self.fixture_tokenizer(ladder),
        ):
            code = issuer.main(
                [
                    "--selection-record",
                    str(selection),
                    "--summary",
                    str(summary),
                    "--prompt-ladder",
                    str(ladder_path),
                    "--input-inventory",
                    str(self.input_inventory),
                    "--counts-receipt",
                    str(self.counts_receipt),
                    "--ruling-trace",
                    str(RULING),
                    "--output",
                    str(output),
                ]
            )
        return code, output

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
                "d166-prefill-selection.json",
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
                code = issuer.main(
                    [
                        "--selection-record",
                        str(selection),
                        "--summary",
                        str(summary),
                        "--prompt-ladder",
                        str(ladder_path),
                        "--input-inventory",
                        str(self.input_inventory),
                        "--counts-receipt",
                        str(self.counts_receipt),
                        "--ruling-trace",
                        str(RULING),
                        "--output",
                        str(output),
                    ]
                )
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
                with mock.patch.object(
                    issuer,
                    "runtime_prompt_token_ids",
                    side_effect=self.fixture_tokenizer(ladder),
                ), self.assertRaisesRegex(issuer.PromptPinError, reason):
                    issuer.issue_pin(
                        selection_record=selection,
                        summary_path=summary,
                        prompt_ladder_path=ladder_path,
                        input_inventory=self.input_inventory,
                        counts_receipt=self.counts_receipt,
                        ruling_trace=RULING,
                        bundle_dir=root,
                    )

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
            with mock.patch.object(
                issuer,
                "runtime_prompt_token_ids",
                side_effect=self.fixture_tokenizer(ladder),
            ), self.assertRaises(issuer.PromptPinError) as raised:
                issuer.issue_pin(
                    selection_record=selection,
                    summary_path=summary,
                    prompt_ladder_path=ladder_path,
                    input_inventory=self.input_inventory,
                    counts_receipt=self.counts_receipt,
                    ruling_trace=RULING,
                    bundle_dir=root,
                )
        self.assertEqual(
            str(raised.exception),
            "receipt_run_id_unknown: g2a-small-p0512-unknown",
        )


if __name__ == "__main__":
    unittest.main()
