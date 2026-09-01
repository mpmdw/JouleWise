"""Tests for the Qwen3-small successor transfer-fiducial plan generator."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stderr
from unittest.mock import patch

from joulewise.provenance import prompt_token_ids_sha256
from scripts.select_g2a_prefill_length import select


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "configs/diagnostics/transfer_fiducial_v2/generate_plan.py"
FIXTURE = (
    ROOT
    / "tests/fixtures/transfer_fiducial_v2/synthetic-selected-g2a-record.json"
)
SUMMARY_FIXTURE = (
    ROOT / "tests/fixtures/transfer_fiducial_v2/synthetic-g2a-summary.json"
)
CONTRACT_PATH = ROOT / "docs/contracts/transfer_fiducial.md"
SPEC = importlib.util.spec_from_file_location("transfer_fiducial_v2_plan", GENERATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


def _fixture_prompt(rung: int) -> str:
    return " ".join(f"fixture-token-{index}" for index in range(rung))


def _fixture_tokenize(_model: object, prompt_text: str) -> list[int]:
    """Deterministic stand-in for the runtime tokenizer, used only under patch."""

    return [1000 + index for index, _ in enumerate(prompt_text.split())]


def _prompt_pin(
    selection_path: Path,
    *,
    rung: int,
    ruled_generation_method: bool = True,
) -> dict[str, object]:
    model, _ = generator.v5_small_model_identity()
    prompt_text = _fixture_prompt(rung)
    token_ids = _fixture_tokenize(model, prompt_text)
    selection_sha256 = hashlib.sha256(selection_path.read_bytes()).hexdigest()
    generation_method = (
        "71 x 'The plan remains easy to audit.' + "
        "'The final check closes cleanly.' under tokenizer sha256:"
        f"{model['tokenizer_json_sha256']}"
        if ruled_generation_method
        else "synthetic fixture only; never a live prompt pin"
    )
    return {
        "schema_version": "joulewise.prefill_prompt_pin.v2",
        "selection_authority": {
            "g2a_record": {
                "record_id": f"sha256:{selection_sha256}",
                "path": selection_path.name,
            },
            "ruling_trace_path": generator.v5.PREFILL_RULING_TRACE_PATH,
        },
        "ladder_prompt_tokens": generator.v5.PREFILL_LADDER_PROMPT_TOKENS,
        "min_small_model_members_per_rung": (
            generator.v5.PREFILL_MIN_SMALL_MODEL_MEMBERS_PER_RUNG
        ),
        "min_overlapping_power_interval_count": (
            generator.v5.PREFILL_MIN_OVERLAPPING_POWER_INTERVAL_COUNT
        ),
        "min_phase_samples_pinned": generator.v5.PREFILL_MIN_PHASE_SAMPLES_PINNED,
        "sample_count_margin_floor": generator.v5.PREFILL_SAMPLE_COUNT_MARGIN_FLOOR,
        "selection_expression": generator.v5.PREFILL_SELECTION_EXPRESSION,
        "g2a_record_sha256": selection_sha256,
        "exhausted_ladder_branch": generator.v5.PREFILL_EXHAUSTED_LADDER_BRANCH,
        "prefill_length": rung,
        "tokenizer_json_sha256": model["tokenizer_json_sha256"],
        "prompt_text": prompt_text,
        "prompt_text_utf8_sha256": hashlib.sha256(
            prompt_text.encode("utf-8")
        ).hexdigest(),
        "prompt_token_ids": token_ids,
        "prompt_token_ids_sha256": prompt_token_ids_sha256(token_ids),
        "prompt_tokens": rung,
        "repeat_count": 1,
        "generation_method": generation_method,
    }


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


class TransferFiducialV2PlanTests(unittest.TestCase):
    def _write_inputs(self, root: Path) -> tuple[Path, Path, Path]:
        summary = root / "synthetic-g2a-summary.json"
        summary.write_bytes(SUMMARY_FIXTURE.read_bytes())
        selection = root / "synthetic-selected-g2a-record.json"
        selection.write_bytes(FIXTURE.read_bytes())
        prompt_pin = root / "synthetic-prefill-prompt-pin.json"
        _write_json(prompt_pin, _prompt_pin(selection, rung=512))
        return summary, selection, prompt_pin

    def test_generates_ten_configs_after_runtime_retokenization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary, selection, prompt_pin = self._write_inputs(root)
            with patch.object(
                generator, "_runtime_tokenize_prompt", side_effect=_fixture_tokenize
            ) as tokenize:
                generator.generate(
                    root,
                    summary=summary,
                    selection_record=selection,
                    prefill_prompt_pin=prompt_pin,
                )
                destination = root / generator.OUTPUT_REL
                plan = json.loads((destination / "plan.json").read_text())
                configs = sorted(destination.glob("tf-q3s-p512-o512-r*.json"))
                self.assertEqual(len(configs), 10)
                self.assertEqual(
                    [path.name for path in configs],
                    [
                        f"tf-q3s-p512-o512-r{index:02d}.json"
                        for index in range(1, 11)
                    ],
                )
                self.assertEqual(
                    plan["schema_version"],
                    generator.TRANSFER_FIDUCIAL_PLAN_SCHEMA_V2,
                )
                self.assertEqual(
                    plan["diagnostic_kind"],
                    generator.TRANSFER_FIDUCIAL_DIAGNOSTIC_KIND_V2,
                )
                self.assertEqual(plan["strata"][0]["prompt_tokens"], 512)
                expected_model, _ = generator.v5_small_model_identity()
                for config_path in configs:
                    model = json.loads(config_path.read_text())["model"]
                    self.assertEqual(model["revision"], expected_model["revision"])
                    self.assertEqual(
                        model["tokenizer_json_sha256"],
                        expected_model["tokenizer_json_sha256"],
                    )
                    self.assertEqual(
                        model["chat_template_sha256"],
                        expected_model["chat_template_sha256"],
                    )
                generator.check(
                    root,
                    summary=summary,
                    selection_record=selection,
                    prefill_prompt_pin=prompt_pin,
                )
            self.assertEqual(tokenize.call_count, 2)

    def test_synthetic_self_hashed_prompt_pin_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary, selection, prompt_pin = self._write_inputs(root)
            synthetic = _prompt_pin(
                selection, rung=512, ruled_generation_method=False
            )
            synthetic["prompt_token_ids"] = [17] * 512
            synthetic["prompt_token_ids_sha256"] = prompt_token_ids_sha256(
                synthetic["prompt_token_ids"]
            )
            _write_json(prompt_pin, synthetic)
            with self.assertRaisesRegex(
                generator.PlanGenerationError,
                "prefill_prompt_pin_generation_method_invalid",
            ):
                generator.generate(
                    root,
                    summary=summary,
                    selection_record=selection,
                    prefill_prompt_pin=prompt_pin,
                )

    def test_selection_summary_exact_bytes_are_authenticated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary, selection, prompt_pin = self._write_inputs(root)
            summary.write_bytes(summary.read_bytes() + b" ")
            with self.assertRaisesRegex(
                generator.PlanGenerationError,
                "selection_record_summary_sha256_mismatch",
            ):
                generator.generate(
                    root,
                    summary=summary,
                    selection_record=selection,
                    prefill_prompt_pin=prompt_pin,
                )
            self.assertEqual(
                generator.main(
                    [
                        "--summary",
                        str(summary),
                        "--selection-record",
                        str(selection),
                        "--prefill-prompt-pin",
                        str(prompt_pin),
                        "--output-root",
                        str(root),
                    ]
                ),
                2,
            )

    def test_selection_fixture_matches_selector_output_shape(self) -> None:
        summary_raw = SUMMARY_FIXTURE.read_bytes()
        self.assertEqual(
            json.loads(FIXTURE.read_text()),
            select(
                json.loads(summary_raw),
                summary_sha256=hashlib.sha256(summary_raw).hexdigest(),
            ),
        )

    def test_operator_contract_names_ruled_producers_and_calibration_selector(self) -> None:
        contract = CONTRACT_PATH.read_text()
        for required_text in (
            "D-167's `_v5` chain",
            "`V5-NIGHTLY-G3-01`",
            "scripts/summarize_g2a_prefill_probe.py",
            "--counts-output \"$G2A_COUNTS\"",
            "--summary-output \"$G2A_SUMMARY\"",
            "scripts/issue_g2a_prefill_prompt_pin.py",
            "--prompt-ladder \"$G2A_PROMPT_LADDER\"",
            "--ruling-trace docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md",
            "regex SHAPE check only",
            "ruling-39b construction check lands",
            "### Sequencing note",
            "Pin-to-ladder binding from ruling 39b",
            "not a threat-model deferral",
            "ladder is the pre-registration record",
            "D-161's fail-closed carve-out",
            "`transformers.AutoTokenizer`",
            "`mlx_lm.load`",
            "The post-merge round's `WRITE_SCOPE` must include",
            "`--config-root`,",
            "`--input-inventory`,",
            "`--runs-root`,",
            "`--counts-output`,",
            "`--summary-output`",
            "verified against `feat/2026-09-01-g2a-probe` @ `82e7519d`; absent from this branch until that branch merges.",
            'TF_CAL_DIR="$($JW_PY - "$TF_CAL_ROOT"',
            "expected exactly one valid calibration",
            'bash scripts/backup_runs.sh "$TF_RUNS_ROOT" "$TF_BACKUP_DEST"',
        ):
            self.assertIn(required_text, contract)

    def test_refuses_missing_unauthenticated_and_unknown_selection_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary, selection, prompt_pin = self._write_inputs(root)
            with self.assertRaisesRegex(
                generator.PlanGenerationError, "selection_record_missing"
            ):
                generator.generate(
                    root,
                    summary=summary,
                    selection_record=root / "missing.json",
                    prefill_prompt_pin=prompt_pin,
                )
            self.assertEqual(
                generator.main(
                    [
                        "--summary",
                        str(summary),
                        "--selection-record",
                        str(root / "missing.json"),
                        "--prefill-prompt-pin",
                        str(prompt_pin),
                        "--output-root",
                        str(root),
                    ]
                ),
                2,
            )

            unauthenticated = json.loads(selection.read_text())
            unauthenticated["summary_sha256"] = "not-a-digest"
            _write_json(selection, unauthenticated)
            with self.assertRaisesRegex(
                generator.PlanGenerationError,
                "selection_record_unauthenticated_summary_sha256",
            ):
                generator.generate(
                    root,
                    summary=summary,
                    selection_record=selection,
                    prefill_prompt_pin=prompt_pin,
                )

            unknown = json.loads(FIXTURE.read_text())
            unknown["selected_prefill_tokens"] = 256
            unknown["collection_prefill_tokens"] = 256
            _write_json(selection, unknown)
            with self.assertRaisesRegex(
                generator.PlanGenerationError, "selection_record_rung_not_supported"
            ):
                generator.generate(
                    root,
                    summary=summary,
                    selection_record=selection,
                    prefill_prompt_pin=prompt_pin,
                )

    def test_collect_at_4096_refusal_record_cli_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = root / "g2a-summary.json"
            refused_rows = json.loads(SUMMARY_FIXTURE.read_text())
            for row in refused_rows:
                row["all_small_count_ge_5"] = False
                row["small_minimum_count"] = 4
            _write_json(summary, refused_rows)
            summary_raw = summary.read_bytes()
            record = select(
                refused_rows,
                summary_sha256=hashlib.sha256(summary_raw).hexdigest(),
            )
            selection = root / "g2a-selection.json"
            _write_json(selection, record)
            prompt_pin = root / "prompt-pin.json"
            _write_json(prompt_pin, _prompt_pin(selection, rung=4096))
            self.assertEqual(
                generator.main(
                    [
                        "--summary",
                        str(summary),
                        "--selection-record",
                        str(selection),
                        "--prefill-prompt-pin",
                        str(prompt_pin),
                        "--output-root",
                        str(root),
                    ]
                ),
                2,
            )

    def test_prompt_pin_authority_and_runtime_mismatches_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary, selection, prompt_pin = self._write_inputs(root)
            cases = {
                "record_id": "prefill_prompt_pin_record_id_mismatch",
                "path": "prefill_prompt_pin_selection_record_path_mismatch",
                "g2a_digest": "prefill_prompt_pin_selection_record_mismatch",
            }
            for case, reason in cases.items():
                pin = _prompt_pin(selection, rung=512)
                if case == "record_id":
                    pin["selection_authority"]["g2a_record"]["record_id"] = (
                        "sha256:" + "0" * 64
                    )
                elif case == "path":
                    pin["selection_authority"]["g2a_record"]["path"] = "other.json"
                else:
                    pin["g2a_record_sha256"] = "0" * 64
                _write_json(prompt_pin, pin)
                with self.assertRaisesRegex(generator.PlanGenerationError, reason):
                    generator.generate(
                        root,
                        summary=summary,
                        selection_record=selection,
                        prefill_prompt_pin=prompt_pin,
                    )
                self.assertEqual(
                    generator.main(
                        [
                            "--summary",
                            str(summary),
                            "--selection-record",
                            str(selection),
                            "--prefill-prompt-pin",
                            str(prompt_pin),
                            "--output-root",
                            str(root),
                        ]
                    ),
                    2,
                )

            pin = _prompt_pin(selection, rung=512)
            _write_json(prompt_pin, pin)
            with patch.object(
                generator,
                "_runtime_tokenize_prompt",
                return_value=[9999, *_fixture_tokenize(None, pin["prompt_text"])[1:]],
            ):
                stderr = io.StringIO()
                with redirect_stderr(stderr):
                    result = generator.main(
                        [
                            "--summary",
                            str(summary),
                            "--selection-record",
                            str(selection),
                            "--prefill-prompt-pin",
                            str(prompt_pin),
                            "--output-root",
                            str(root),
                        ]
                    )
                self.assertEqual(result, 2)
                self.assertIn(
                    "prefill_prompt_pin_runtime_token_ids_mismatch",
                    stderr.getvalue(),
                )

    def test_prompt_pin_rung_and_tokenizer_mismatches_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary, selection, prompt_pin = self._write_inputs(root)
            wrong_rung = _prompt_pin(selection, rung=1024)
            _write_json(prompt_pin, wrong_rung)
            with self.assertRaisesRegex(
                generator.PlanGenerationError,
                "prefill_prompt_pin_unauthenticated:prefill_prompt_pin_length_mismatch",
            ):
                generator.generate(
                    root,
                    summary=summary,
                    selection_record=selection,
                    prefill_prompt_pin=prompt_pin,
                )
            self.assertEqual(
                generator.main(
                    [
                        "--summary",
                        str(summary),
                        "--selection-record",
                        str(selection),
                        "--prefill-prompt-pin",
                        str(prompt_pin),
                        "--output-root",
                        str(root),
                    ]
                ),
                2,
            )
            wrong_tokenizer = _prompt_pin(selection, rung=512)
            wrong_tokenizer["tokenizer_json_sha256"] = "0" * 64
            _write_json(prompt_pin, wrong_tokenizer)
            with self.assertRaisesRegex(
                generator.PlanGenerationError,
                "prefill_prompt_pin_unauthenticated:prefill_prompt_pin_tokenizer_sha256_mismatch",
            ):
                generator.generate(
                    root,
                    summary=summary,
                    selection_record=selection,
                    prefill_prompt_pin=prompt_pin,
                )
            self.assertEqual(
                generator.main(
                    [
                        "--summary",
                        str(summary),
                        "--selection-record",
                        str(selection),
                        "--prefill-prompt-pin",
                        str(prompt_pin),
                        "--output-root",
                        str(root),
                    ]
                ),
                2,
            )


if __name__ == "__main__":
    unittest.main()
