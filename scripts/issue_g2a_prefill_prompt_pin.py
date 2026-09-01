#!/usr/bin/env python3
"""Issue the post-selection G2-a prefill prompt pin consumed by D-117 v5."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Sequence

from configs.campaigns.d117_contrast_v5 import generate_configs as d117_v5
from joulewise.adapters.mlx_runtime import _encode
from joulewise.provenance import prompt_token_ids_sha256
from scripts import select_g2a_prefill_length as selector


PROMPT_LADDER_SCHEMA = "joulewise.g2a_prefill_prompt_ladder.v1"
PROMPT_PIN_SCHEMA = "joulewise.prefill_prompt_pin.v2"
DEFAULT_MODEL_MIRROR = Path(
    "/Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit"
)
REPO_ROOT = Path(__file__).resolve().parents[1]


class PromptPinError(ValueError):
    """The supplied G2-a artifacts cannot authorize a prompt pin."""


def _strict_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise PromptPinError(f"duplicate_key:{key}")
        value[key] = item
    return value


def _load_json(path: Path, *, label: str) -> tuple[Any, bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise PromptPinError(f"{label}_unreadable:{path}:{exc}") from exc
    try:
        value = json.loads(
            raw,
            object_pairs_hook=_strict_object_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                PromptPinError(f"non_finite_number:{token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PromptPinError(f"{label}_invalid_json:{path}:{exc}") from exc
    return value, raw


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _require_exact_keys(value: Any, keys: set[str], *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise PromptPinError(f"{label}_closed_schema_mismatch")
    return value


def _require_positive_int(value: Any, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise PromptPinError(f"{label}_invalid")
    return value


def runtime_prompt_token_ids(
    prompt_text: str,
    *,
    tokenizer_json_sha256: str,
    model_mirror: Path = DEFAULT_MODEL_MIRROR,
) -> list[int]:
    """Load the local tokenizer and use the MLX adapter's raw-text encode seam."""

    tokenizer_path = model_mirror / "tokenizer.json"
    try:
        observed_hash = _sha256(tokenizer_path.read_bytes())
    except OSError as exc:
        raise PromptPinError(f"runtime_tokenizer_unreadable:{tokenizer_path}:{exc}") from exc
    if observed_hash != tokenizer_json_sha256:
        raise PromptPinError("runtime_tokenizer_sha256_mismatch")
    try:
        from transformers import AutoTokenizer
    except ImportError as exc:
        raise PromptPinError("runtime_tokenizer_loader_unavailable:transformers") from exc
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            str(model_mirror),
            local_files_only=True,
        )
        return _encode(tokenizer, prompt_text, add_special_tokens=True)
    except Exception as exc:  # noqa: BLE001 - adapters vary, refusal must stay closed
        raise PromptPinError(
            f"runtime_tokenization_failed:{type(exc).__name__}:{exc}"
        ) from exc


def _validate_summary(summary: Any) -> None:
    if not isinstance(summary, list) or len(summary) != len(selector.LADDER):
        raise PromptPinError("summary_expected_four_row_array")
    keys = {
        "length",
        "small_members",
        "large_members",
        "small_minimum_count",
        "all_small_count_ge_5",
    }
    for row in summary:
        _require_exact_keys(row, keys, label="summary_row")
        large = row["large_members"]
        if isinstance(large, bool) or not isinstance(large, int) or large < 1:
            raise PromptPinError("summary_large_members_invalid")


def _selection_from_inputs(
    selection: Any,
    *,
    summary: Any,
    summary_sha256: str,
) -> int:
    _validate_summary(summary)
    try:
        expected = selector.select(summary, summary_sha256=summary_sha256)
    except selector.SummaryError as exc:
        raise PromptPinError(f"summary_refused:{exc}") from exc
    if selection != expected:
        raise PromptPinError("selection_record_does_not_match_summary_and_rule")
    length = selection.get("collection_prefill_tokens")
    if length not in selector.LADDER:
        raise PromptPinError("selection_collection_prefill_tokens_unknown")
    if selection["status"] == "selected":
        if selection["selected_prefill_tokens"] != length or selection["refusal"] is not None:
            raise PromptPinError("selection_selected_branch_malformed")
    elif selection["status"] == "refused":
        refusal = selection["refusal"]
        if (
            length != 4096
            or selection["selected_prefill_tokens"] is not None
            or not isinstance(refusal, dict)
            or refusal.get("fallback_action") != "collect_at_4096"
        ):
            raise PromptPinError("selection_no_clear_branch_malformed")
    else:
        raise PromptPinError("selection_status_invalid")
    return length


def _validate_ladder(ladder: Any) -> tuple[str, dict[int, dict[str, Any]]]:
    value = _require_exact_keys(
        ladder,
        {
            "schema_version",
            "prompt_sentence",
            "tokenizer_json_sha256",
            "panel_thinking_policy",
            "rungs",
        },
        label="prompt_ladder",
    )
    if value["schema_version"] != PROMPT_LADDER_SCHEMA:
        raise PromptPinError("prompt_ladder_schema_version_invalid")
    sentence = value["prompt_sentence"]
    if sentence != d117_v5.PROMPT_SENTENCE:
        raise PromptPinError("prompt_ladder_sentence_mismatch")
    tokenizer_hash = value["tokenizer_json_sha256"]
    if not _is_sha256(tokenizer_hash):
        raise PromptPinError("prompt_ladder_tokenizer_sha256_invalid")
    thinking = _require_exact_keys(
        value["panel_thinking_policy"],
        {"enable_thinking", "panel_sha256"},
        label="prompt_ladder_panel_thinking_policy",
    )
    if thinking["enable_thinking"] != "false" or not _is_sha256(
        thinking["panel_sha256"]
    ):
        raise PromptPinError("prompt_ladder_thinking_policy_invalid")
    rungs = value["rungs"]
    if not isinstance(rungs, list) or len(rungs) != len(selector.LADDER):
        raise PromptPinError("prompt_ladder_expected_four_rungs")
    by_length: dict[int, dict[str, Any]] = {}
    rung_keys = {
        "prefill_tokens",
        "repeat_count",
        "closing_sentence",
        "prompt_text",
        "prompt_text_utf8_sha256",
        "prompt_token_ids",
        "prompt_token_ids_sha256",
        "generation_method",
    }
    for rung in rungs:
        rung = _require_exact_keys(rung, rung_keys, label="prompt_ladder_rung")
        length = rung["prefill_tokens"]
        if length not in selector.LADDER or length in by_length:
            raise PromptPinError("prompt_ladder_rung_length_invalid_or_duplicate")
        repeat_count = _require_positive_int(
            rung["repeat_count"], label=f"repeat_count:{length}"
        )
        closing = rung["closing_sentence"]
        prompt_text = rung["prompt_text"]
        if not isinstance(closing, str) or not closing.strip():
            raise PromptPinError(f"closing_sentence_invalid:{length}")
        if not isinstance(prompt_text, str) or not prompt_text:
            raise PromptPinError(f"prompt_text_invalid:{length}")
        expected_text = " ".join([sentence] * repeat_count + [closing])
        if prompt_text != expected_text:
            raise PromptPinError(f"prompt_text_construction_mismatch:{length}")
        if _sha256(prompt_text.encode("utf-8")) != rung["prompt_text_utf8_sha256"]:
            raise PromptPinError(f"prompt_text_sha256_mismatch:{length}")
        token_ids = rung["prompt_token_ids"]
        if (
            not isinstance(token_ids, list)
            or len(token_ids) != length
            or any(
                isinstance(item, bool) or not isinstance(item, int) or item < 0
                for item in token_ids
            )
        ):
            raise PromptPinError(f"prompt_token_ids_invalid:{length}")
        if prompt_token_ids_sha256(token_ids) != rung["prompt_token_ids_sha256"]:
            raise PromptPinError(f"prompt_token_ids_sha256_mismatch:{length}")
        expected_method = (
            f"{repeat_count} x '{sentence}' + '{closing}' under tokenizer "
            f"sha256:{tokenizer_hash}"
        )
        if rung["generation_method"] != expected_method:
            raise PromptPinError(f"generation_method_mismatch:{length}")
        by_length[length] = rung
    if tuple(sorted(by_length)) != selector.LADDER:
        raise PromptPinError("prompt_ladder_lengths_mismatch")
    return tokenizer_hash, by_length


def _ruling_trace_paths(path: Path) -> list[str]:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise PromptPinError("ruling_trace_outside_repository") from exc
    if relative != d117_v5.PREFILL_RULING_TRACE_PATH or not resolved.is_file():
        raise PromptPinError("ruling_trace_path_mismatch_or_missing")
    required = [
        REPO_ROOT / trace for trace in d117_v5.PREFILL_RULING_TRACE_PATHS
    ]
    if not all(item.is_file() for item in required):
        raise PromptPinError("ruling_trace_path_mismatch_or_missing")
    return list(d117_v5.PREFILL_RULING_TRACE_PATHS)


def _validate_receipt(
    *,
    input_inventory: Path,
    counts_receipt: Path,
    summary_raw: bytes,
    ladder_raw: bytes,
    ladder: dict[str, Any],
    selected_length: int,
) -> None:
    inventory, inventory_raw = _load_json(input_inventory, label="input_inventory")
    receipt, _receipt_raw = _load_json(counts_receipt, label="counts_receipt")
    if not isinstance(inventory, dict) or not isinstance(receipt, dict):
        raise PromptPinError("input_inventory_or_counts_receipt_malformed")
    if receipt.get("schema_version") != "joulewise.g2a_probe_counts_receipt.v1":
        raise PromptPinError("counts_receipt_schema_version_invalid")
    if receipt.get("input_inventory_sha256") != _sha256(inventory_raw):
        raise PromptPinError("counts_receipt_input_inventory_sha256_mismatch")
    if receipt.get("summary_output_sha256") != _sha256(summary_raw):
        raise PromptPinError("counts_receipt_summary_output_sha256_mismatch")
    if not isinstance(receipt.get("runs_root"), str) or not receipt["runs_root"].strip():
        raise PromptPinError("counts_receipt_runs_root_invalid")
    prompt_ladder = inventory.get("prompt_ladder")
    panel = inventory.get("panel")
    if (
        not isinstance(prompt_ladder, dict)
        or prompt_ladder.get("sha256") != _sha256(ladder_raw)
        or receipt.get("prompt_ladder_sha256") != _sha256(ladder_raw)
    ):
        raise PromptPinError("input_inventory_prompt_ladder_sha256_mismatch")
    if (
        not isinstance(panel, dict)
        or not _is_sha256(panel.get("sha256"))
        or ladder["panel_thinking_policy"]["panel_sha256"] != panel["sha256"]
    ):
        raise PromptPinError("ladder_panel_binding_mismatch")
    stages = inventory.get("stages")
    runs = receipt.get("runs")
    if not isinstance(stages, list) or not isinstance(runs, list):
        raise PromptPinError("counts_receipt_runs_malformed")
    expected: set[str] = set()
    expected_members: dict[str, tuple[str, str]] = {}
    for role in ("small", "large"):
        stage_id = f"{role}-p{selected_length}"
        stage = next(
            (item for item in stages if isinstance(item, dict) and item.get("stage_id") == stage_id),
            None,
        )
        if not isinstance(stage, dict) or not isinstance(stage.get("members"), list):
            raise PromptPinError("input_inventory_selected_stage_missing")
        expected.update(
            member.get("run_id")
            for member in stage["members"]
            if isinstance(member, dict) and isinstance(member.get("run_id"), str)
        )
        for member in stage["members"]:
            if isinstance(member, dict) and isinstance(member.get("run_id"), str):
                expected_members[member["run_id"]] = (
                    stage_id,
                    member.get("config_sha256"),
                )
    observed: set[str] = set()
    run_keys = {
        "run_id",
        "stage_id",
        "config_sha256",
        "realized_prompt_token_count",
        "realized_prompt_token_ids_sha256",
        "in_window_sample_count",
    }
    for run in runs:
        if not isinstance(run, dict) or set(run) != run_keys:
            raise PromptPinError("counts_receipt_run_malformed")
        if run["stage_id"] in {f"small-p{selected_length}", f"large-p{selected_length}"}:
            if not isinstance(run["run_id"], str) or run["run_id"] in observed:
                raise PromptPinError("counts_receipt_run_id_invalid")
            observed.add(run["run_id"])
            expected_stage, expected_config_sha = expected_members[run["run_id"]]
            selected_rung = next(
                item
                for item in ladder["rungs"]
                if item["prefill_tokens"] == selected_length
            )
            if (
                run["stage_id"] != expected_stage
                or run["config_sha256"] != expected_config_sha
                or run["realized_prompt_token_count"] != selected_length
                or run["realized_prompt_token_ids_sha256"]
                != selected_rung["prompt_token_ids_sha256"]
                or isinstance(run["in_window_sample_count"], bool)
                or not isinstance(run["in_window_sample_count"], int)
                or run["in_window_sample_count"] < 0
            ):
                raise PromptPinError("counts_receipt_run_provenance_mismatch")
    if observed != expected:
        raise PromptPinError("counts_receipt_selected_rung_run_set_mismatch")


def _bundle_reference(path: Path, *, bundle_dir: Path, label: str) -> tuple[str, str]:
    destination = bundle_dir / path.name
    try:
        relative = destination.resolve().relative_to(bundle_dir.resolve()).as_posix()
    except ValueError as exc:
        raise PromptPinError(f"{label}_relative_path_invalid") from exc
    return relative, _sha256(path.read_bytes())


def issue_pin(
    *,
    selection_record: Path,
    summary_path: Path,
    prompt_ladder_path: Path,
    input_inventory: Path,
    counts_receipt: Path,
    ruling_trace: Path,
    bundle_dir: Path,
) -> dict[str, Any]:
    selection, selection_raw = _load_json(selection_record, label="selection_record")
    summary, summary_raw = _load_json(summary_path, label="summary")
    ladder, ladder_raw = _load_json(prompt_ladder_path, label="prompt_ladder")
    summary_hash = _sha256(summary_raw)
    length = _selection_from_inputs(
        selection,
        summary=summary,
        summary_sha256=summary_hash,
    )
    tokenizer_hash, rungs = _validate_ladder(ladder)
    rung = rungs[length]
    _validate_receipt(
        input_inventory=input_inventory,
        counts_receipt=counts_receipt,
        summary_raw=summary_raw,
        ladder_raw=ladder_raw,
        ladder=ladder,
        selected_length=length,
    )
    observed_ids = runtime_prompt_token_ids(
        rung["prompt_text"], tokenizer_json_sha256=tokenizer_hash
    )
    if observed_ids != rung["prompt_token_ids"]:
        raise PromptPinError(f"runtime_prompt_token_ids_mismatch:{length}")
    if len(observed_ids) != length:
        raise PromptPinError(f"runtime_prompt_token_count_mismatch:{length}")
    ruling_paths = _ruling_trace_paths(ruling_trace)
    selection_hash = _sha256(selection_raw)
    try:
        selection_record.resolve().relative_to(prompt_ladder_path.resolve().parent)
    except ValueError as exc:
        raise PromptPinError("selection_record_outside_window_plan_root") from exc
    selection_relative, selection_copy_hash = _bundle_reference(
        selection_record, bundle_dir=bundle_dir, label="selection_record"
    )
    ladder_relative, ladder_copy_hash = _bundle_reference(
        prompt_ladder_path, bundle_dir=bundle_dir, label="prompt_ladder"
    )

    return {
        "schema_version": PROMPT_PIN_SCHEMA,
        "selection_authority": {
            "g2a_record": {
                "record_id": f"sha256:{selection_hash}",
                "path": selection_relative,
            },
            "ruling_trace_paths": ruling_paths,
        },
        "ladder_prompt_tokens": list(d117_v5.PREFILL_LADDER_PROMPT_TOKENS),
        "min_small_model_members_per_rung": (
            d117_v5.PREFILL_MIN_SMALL_MODEL_MEMBERS_PER_RUNG
        ),
        "min_overlapping_power_interval_count": (
            d117_v5.PREFILL_MIN_OVERLAPPING_POWER_INTERVAL_COUNT
        ),
        "min_phase_samples_pinned": d117_v5.PREFILL_MIN_PHASE_SAMPLES_PINNED,
        "sample_count_margin_floor": d117_v5.PREFILL_SAMPLE_COUNT_MARGIN_FLOOR,
        "selection_expression": d117_v5.PREFILL_SELECTION_EXPRESSION,
        "g2a_record_sha256": selection_hash,
        "selection_record": {"path": selection_relative, "sha256": selection_copy_hash},
        "prompt_ladder": {"path": ladder_relative, "sha256": ladder_copy_hash},
        "panel_sha256": ladder["panel_thinking_policy"]["panel_sha256"],
        "exhausted_ladder_branch": d117_v5.PREFILL_EXHAUSTED_LADDER_BRANCH,
        "prefill_length": length,
        "tokenizer_json_sha256": tokenizer_hash,
        "prompt_text": rung["prompt_text"],
        "prompt_text_utf8_sha256": rung["prompt_text_utf8_sha256"],
        "prompt_token_ids": list(rung["prompt_token_ids"]),
        "prompt_token_ids_sha256": rung["prompt_token_ids_sha256"],
        "prompt_tokens": length,
        "repeat_count": rung["repeat_count"],
        "closing_sentence": rung["closing_sentence"],
        "generation_method": rung["generation_method"],
    }


def _pin_bytes(pin: dict[str, Any]) -> bytes:
    return (
        json.dumps(pin, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection-record", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--prompt-ladder", required=True, type=Path)
    parser.add_argument("--input-inventory", required=True, type=Path)
    parser.add_argument("--counts-receipt", required=True, type=Path)
    parser.add_argument("--ruling-trace", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.output.exists():
            raise PromptPinError("output_already_exists")
        pin = issue_pin(
            selection_record=args.selection_record,
            summary_path=args.summary,
            prompt_ladder_path=args.prompt_ladder,
            input_inventory=args.input_inventory,
            counts_receipt=args.counts_receipt,
            ruling_trace=args.ruling_trace,
            bundle_dir=args.output.parent,
        )
        for source in (args.selection_record, args.prompt_ladder):
            destination = args.output.parent / source.name
            raw = source.read_bytes()
            if destination.exists():
                if destination.read_bytes() != raw:
                    raise PromptPinError(f"bundle_copy_mismatch:{destination}")
                continue
            try:
                with destination.open("xb") as handle:
                    handle.write(raw)
                    handle.flush()
                    os.fsync(handle.fileno())
            except OSError as exc:
                raise PromptPinError(f"bundle_copy_unwritable:{destination}:{exc}") from exc
        try:
            with args.output.open("xb") as handle:
                handle.write(_pin_bytes(pin))
        except OSError as exc:
            raise PromptPinError(f"output_unwritable:{args.output}:{exc}") from exc
    except PromptPinError as exc:
        print(f"G2-a prompt pin refused: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
