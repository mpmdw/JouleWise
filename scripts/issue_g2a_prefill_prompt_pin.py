#!/usr/bin/env python3
"""Issue the harvest-bound G2-a prefill prompt pin consumed by D-117 v5."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from configs.campaigns.d117_contrast_v5 import generate_configs as d117_v5
from joulewise.adapters.mlx_runtime import _encode
from joulewise.provenance import prompt_token_ids_sha256
from joulewise.night_gate import chain_literal
from scripts.generate_g2a_probe_inputs import LADDER_KEYS as PROMPT_LADDER_KEYS
from scripts import select_g2a_prefill_length as selector
from scripts import summarize_g2a_prefill_probe as summarizer


PROMPT_LADDER_SCHEMA = "joulewise.g2a_prefill_prompt_ladder.v1"
PROMPT_PIN_SCHEMA = "joulewise.prefill_prompt_pin.v2"
SPECIAL_TOKEN_POLICY = "add_special_tokens=true"
PROMPT_PIN_KEYS = frozenset(
    {
        "schema_version",
        "selection_authority",
        "ladder_prompt_tokens",
        "min_small_model_members_per_rung",
        "min_overlapping_power_interval_count",
        "min_phase_samples_pinned",
        "sample_count_margin_floor",
        "selection_expression",
        "g2a_record_sha256",
        "selection_record",
        "prompt_ladder",
        "panel_sha256",
        "exhausted_ladder_branch",
        "prefill_length",
        "tokenizer_json_sha256",
        "special_token_policy",
        "prompt_text",
        "prompt_text_utf8_sha256",
        "prompt_token_ids",
        "prompt_token_ids_sha256",
        "prompt_tokens",
        "repeat_count",
        "closing_sentence",
        "generation_method",
    }
)
DEFAULT_MODEL_MIRROR = Path(
    "/Users/edr/jw_models/mlx-community/Qwen3-1.7B-4bit"
)
REPO_ROOT = Path(__file__).resolve().parents[1]
BLOCK3_REGISTRATION_SHA256 = "84dd04268a2aed17118bd98b87c10ebe38e5f1bce2ea330a02048537b0342476"
BLOCK3_POLICY_PATH = "configs/campaign_policies/quiet_mac_p2_g2a_b3.json"
BLOCK3_POLICY_SHA256 = "04bdbec45cf3b609b33886c1487e9982f030564b3212e636f8cf4631b5d4edc7"
LIVE_WINDOWS_ROOT = Path("/Users/edr/night-g2a")
END_STATE_SCHEMA = "joulewise.g2a_prefill_end_state.v1"


def _read_bytes(path: Path, *, label: str) -> bytes:
    # Refuse even a direct CLI coordinate or a symlink into the live tree.
    if path.resolve().is_relative_to(LIVE_WINDOWS_ROOT):
        raise PromptPinError("live_root_path_outside_mapping")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise PromptPinError(f"{label}_unreadable:{path}:{exc}") from exc


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
    raw = _read_bytes(path, label=label)
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


def _archive_file(root: Path, path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise PromptPinError("archive_path_outside_root")
    if not resolved.is_file():
        raise PromptPinError("archive_file_missing")
    return resolved


def _copied_path(recorded: Any, *, source: Path, target: Path) -> Path:
    """Invert harvest_g2a_window.archive's copytree(source, stage / name).

    The harvester has no mapping helper. Its sources['g2a-root'] is the
    pinned chain's G2A_ROOT: every relative suffix is preserved verbatim.
    Never resolve or open the source coordinate (it may no longer exist).
    """
    if not isinstance(recorded, str) or ".." in Path(recorded).parts:
        raise PromptPinError("live_root_path_outside_mapping")
    try:
        suffix = Path(recorded).relative_to(source)
    except ValueError as exc:
        raise PromptPinError("live_root_path_outside_mapping") from exc
    return target / suffix


@dataclass(frozen=True)
class _Harvest:
    path: Path
    raw: bytes
    record: dict[str, Any]
    root: Path
    live_root: Path
    window_label: str
    t0: float
    inventory_path: Path
    inventory: dict[str, Any]

    def mapped(self, path: Any) -> Path:
        candidate = _copied_path(path, source=self.live_root, target=self.root / "g2a-root")
        if not candidate.resolve().is_relative_to(self.root / "g2a-root"):
            raise PromptPinError("archive_path_outside_root")
        return candidate

    def file(self, relative: str) -> Path:
        return _archive_file(self.root, self.root / relative)

    def derived(self, name: str) -> tuple[Any, bytes]:
        value, raw = _load_json(self.file(f"derived/{name}"), label="harvest_output")
        outputs = self.record.get("outputs")
        if not isinstance(outputs, dict) or outputs.get(name) != _sha256(raw):
            raise PromptPinError("harvest_output_sha256_mismatch")
        return value, raw


def _load_harvest(path: Path, *, verdict: str) -> _Harvest:
    path = path.resolve()
    record, raw = _load_json(path, label="harvest")
    if not isinstance(record, dict) or record.get("schema") != "joulewise.harvest_g2a_window.v1":
        raise PromptPinError("harvest_schema_invalid")
    archive_root = record.get("archive_root")
    if (not isinstance(archive_root, str) or not Path(archive_root).is_absolute()
            or Path(archive_root).resolve() != path.parent):
        raise PromptPinError("harvest_archive_root_mismatch")
    if record.get("verdict") != verdict:
        raise PromptPinError("harvest_verdict_not_select" if verdict == "SELECT" else "harvest_recover_required")
    if verdict == "SELECT" and record.get("cause_codes") != []:
        raise PromptPinError("harvest_select_has_causes")
    if verdict == "RECOVER" and record.get("capture_made") is not True:
        raise PromptPinError("harvest_recover_capture_required")
    root = path.parent
    plan, plan_raw = _load_json(_archive_file(root, root / "night-custody/night_plan.json"), label="night_plan")
    if record.get("plan_sha256") != _sha256(plan_raw):
        raise PromptPinError("harvest_plan_sha256_mismatch")
    plan_id = record.get("plan_id")
    if (not isinstance(plan, dict) or not isinstance(plan_id, str)
            or not plan_id or Path(plan_id).name != plan_id or plan_id in {".", ".."}
            or plan.get("schema") != "joulewise.night_plan.v2"
            or plan.get("plan_id") != plan_id or plan.get("receipt_class") != "DIAGNOSTIC_NO_PACK"
            or not isinstance(plan.get("measurement_root"), str)
            or not Path(plan["measurement_root"]).is_absolute()
            or not isinstance(plan.get("custody_root"), str)
            or not Path(plan["custody_root"]).is_absolute()
            or type(plan.get("t0_epoch_s")) not in (float, int)):
        raise PromptPinError("harvest_plan_binding_invalid")
    inventory_path = _archive_file(root, root / "g2a-root/window-plan/g2a-input-inventory.json")
    inventory, _ = _load_json(inventory_path, label="input_inventory")
    if (not isinstance(inventory, dict)
            or inventory.get("campaign_policy") != {"path": BLOCK3_POLICY_PATH, "sha256": BLOCK3_POLICY_SHA256}
            or inventory.get("window_id") != plan_id
            or inventory.get("session_id") != plan_id + "-calibration"):
        raise PromptPinError("harvest_block3_binding_mismatch")
    # Labels are the sealed arm recipe's WINDOW_LABEL (b3w1 then b3w2),
    # retained in the authenticated plan's measurement clone coordinate.
    label = Path(plan["measurement_root"]).name.rsplit("-g2a-", 1)[-1]
    if label not in {"b3w1", "b3w2"}:
        raise PromptPinError("harvest_block3_binding_mismatch")
    custody = Path(plan["custody_root"])
    chain_path = _archive_file(root, _copied_path(plan.get("chain_path"), source=custody, target=root / "night-custody"))
    sidecar = _archive_file(root, _copied_path(plan.get("chain_sha256_path"), source=custody, target=root / "night-custody"))
    chain_raw = _read_bytes(chain_path, label="chain")
    try:
        if _read_bytes(sidecar, label="chain_sha256").decode().split()[0] != _sha256(chain_raw):
            raise PromptPinError("harvest_chain_sha256_mismatch")
        text = chain_raw.decode("utf-8")
        live_root = Path(chain_literal(text, "G2A_ROOT"))
        if (chain_literal(text, "NIGHT_CHAIN_INTERFACE") != "g2a-reservation-v1"
                or live_root != LIVE_WINDOWS_ROOT / plan_id):
            raise ValueError("chain binding")
        if chain_literal(text, "POLICY") != str(Path(plan["measurement_root"]) / BLOCK3_POLICY_PATH):
            raise PromptPinError("harvest_block3_binding_mismatch")
    except (ValueError, IndexError) as exc:
        if isinstance(exc, PromptPinError):
            raise
        raise PromptPinError("harvest_chain_binding_invalid") from exc
    harvest = _Harvest(path, raw, record, root, live_root, label, plan["t0_epoch_s"], inventory_path, inventory)

    def check_paths(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"path", "config_path", "config_root", "runs_root"} and isinstance(item, str):
                    if Path(item).is_absolute() or key in {"config_root", "runs_root"}:
                        harvest.mapped(item)
                check_paths(item)
        elif isinstance(value, list):
            for item in value:
                check_paths(item)

    check_paths(inventory)
    return harvest


def _registration(path: Path) -> None:
    if _sha256(_read_bytes(path, label="registration")) != BLOCK3_REGISTRATION_SHA256:
        raise PromptPinError("registration_sha256_mismatch")


def _harvest_ladder(harvest: _Harvest) -> tuple[Path, Any, bytes]:
    path = harvest.file("g2a-root/window-plan/prefill-prompt-ladder.json")
    ladder, raw = _load_json(path, label="prompt_ladder")
    binding = harvest.inventory.get("prompt_ladder")
    if (not isinstance(binding, dict) or harvest.mapped(binding.get("path")).resolve() != path
            or binding.get("sha256") != _sha256(raw)):
        raise PromptPinError("input_inventory_prompt_ladder_sha256_mismatch")
    return path, ladder, raw


def _harvest_summary(harvest: _Harvest) -> tuple[Any, bytes, Path]:
    copies = harvest.record.get("chain_summary_copy")
    names = {"d166-prefill-resolvability-summary.json": "summary.json",
             "d166-prefill-counts-receipt.json": "counts.json"}
    if not isinstance(copies, dict) or set(copies) != set(names):
        raise PromptPinError("harvest_chain_summary_copy_invalid")
    for chain_name, derived_name in names.items():
        _, derived_raw = harvest.derived(derived_name)
        chain_path = harvest.file(f"g2a-root/window-plan/{chain_name}")
        chain_raw = _read_bytes(chain_path, label="chain_summary")
        status = copies[chain_name]
        if not isinstance(status, str) or status not in {"equal", "differs_invalid_members_excluded"}:
            raise PromptPinError("harvest_chain_summary_copy_invalid")
        if status == "equal" and chain_raw != derived_raw:
            raise PromptPinError("harvest_chain_summary_byte_mismatch")
    # Registration §8 lines 300-306: regenerated valid-member copies are
    # authoritative; chain copies are checks even when large members differ.
    summary, raw = harvest.derived("summary.json")
    return summary, raw, harvest.file("derived/counts.json")


def _end_state_record(harvests: list[_Harvest]) -> bytes:
    if not 1 <= len(harvests) <= 2:
        raise PromptPinError("end_state_recover_count_invalid")
    first = harvests[0]
    if (first.window_label != "b3w1" or (len(harvests) == 2 and (
            harvests[1].window_label != "b3w2" or harvests[1].t0 <= first.t0
            or harvests[1].record["plan_id"] == first.record["plan_id"]))):
        raise PromptPinError("end_state_window_order_invalid")
    members = first.record.get("members")
    if (not isinstance(members, list) or any(
            not isinstance(member, dict) or not isinstance(member.get("clock_anchor_status"), str)
            or not isinstance(member.get("run_id"), str) for member in members)
            or len({member["run_id"] for member in members}) != len(members)):
        raise PromptPinError("end_state_members_invalid")
    recorded = [member["clock_anchor_status"] for member in members
                if member["clock_anchor_status"] != "not recorded"]
    # Registration §7 lines 276-293: strictly more than half, minimum five
    # recorded anchors; captureless RECOVERs never consume the allowance.
    systematic = len(recorded) >= 5 and 2 * sum(status != "bounded" for status in recorded) > len(recorded)
    if systematic and len(harvests) == 1:
        trigger = "first_recover_systematic_clock_anchor_failure"
    elif not systematic and len(harvests) == 2:
        trigger = "recovery_window_also_recover"
    else:
        raise PromptPinError("end_state_trigger_not_met")
    return _pin_bytes({
        "schema_version": END_STATE_SCHEMA,
        "registration_sha256": BLOCK3_REGISTRATION_SHA256,
        "recover_harvests": [{"path": str(item.path), "sha256": _sha256(item.raw)} for item in harvests],
        "trigger": trigger,
    })


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
        set(PROMPT_LADDER_KEYS),
        label="prompt_ladder",
    )
    if value["schema_version"] != PROMPT_LADDER_SCHEMA:
        raise PromptPinError("prompt_ladder_schema_version_invalid")
    sentence = value["prompt_sentence"]
    if sentence != d117_v5.PROMPT_SENTENCE:
        raise PromptPinError("prompt_ladder_sentence_mismatch")
    if (
        value["rendering_mode"] != "raw_prompt_text"
        or value["chat_template_applied"] is not False
        or value["thinking_policy"] != "not_applicable_raw_prefill"
    ):
        raise PromptPinError("prompt_ladder_rendering_policy_invalid")
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


def _validate_pin(pin: Any) -> dict[str, Any]:
    value = _require_exact_keys(pin, set(PROMPT_PIN_KEYS), label="prompt_pin")
    if value["schema_version"] != PROMPT_PIN_SCHEMA:
        raise PromptPinError("prompt_pin_schema_version_invalid")
    if value["special_token_policy"] != SPECIAL_TOKEN_POLICY:
        raise PromptPinError("prompt_pin_special_token_policy_invalid")
    return value


def _validate_receipt(
    *,
    harvest: _Harvest,
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
    runs_root = harvest.mapped(receipt["runs_root"])
    config_root = harvest.mapped(inventory.get("config_root"))
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
    expected_members: dict[str, tuple[str, dict[str, Any]]] = {}
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
                    member,
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
            if run["run_id"] not in expected_members:
                raise PromptPinError(f"receipt_run_id_unknown: {run['run_id']}")
            expected_stage, member = expected_members[run["run_id"]]
            try:
                config_path = summarizer._confined_path(
                    config_root,
                    str(harvest.mapped(member["config_path"]))
                    if isinstance(member.get("config_path"), str) and Path(member["config_path"]).is_absolute()
                    else member.get("config_path"),
                    label="receipt_config_path",
                )
                config, config_raw = _load_json(
                    _archive_file(harvest.root, config_path), label="receipt_config"
                )
                metadata, _ = _load_json(
                    _archive_file(harvest.root, runs_root / run["run_id"] / "metadata.json"), label="receipt_metadata",
                )
                _archive_file(harvest.root, runs_root / run["run_id"] / "config.json")
                if not isinstance(metadata, dict) or metadata.get("run_id") != run["run_id"]:
                    raise summarizer.ProbeSummaryError("metadata_run_id_mismatch")
                expected_config_sha = summarizer._authenticated_run_config_sha256(
                    config=config, config_raw=config_raw,
                    expected_input_sha256=member.get("config_sha256"), metadata=metadata,
                    run_id=run["run_id"], runs_root=runs_root,
                )
            except summarizer.ProbeSummaryError as exc:
                raise PromptPinError("counts_receipt_run_provenance_mismatch") from exc
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


def _bundle_reference(name: str, raw: bytes, *, bundle_dir: Path, label: str) -> tuple[str, str]:
    destination = bundle_dir / name
    try:
        relative = destination.resolve().relative_to(bundle_dir.resolve()).as_posix()
    except ValueError as exc:
        raise PromptPinError(f"{label}_relative_path_invalid") from exc
    return relative, _sha256(raw)


def _prepare_pin(
    *,
    harvest_path: Path | None = None,
    end_state: bool = False,
    recover_harvests: Sequence[Path] = (),
    registration: Path,
    ruling_trace: Path,
    bundle_dir: Path,
) -> tuple[dict[str, Any], dict[str, bytes]]:
    _registration(registration)
    if end_state:
        if harvest_path is not None:
            raise PromptPinError("issuer_mode_inputs_invalid")
        if not 1 <= len(recover_harvests) <= 2:
            raise PromptPinError("end_state_recover_count_invalid")
        records = [_load_harvest(path, verdict="RECOVER") for path in recover_harvests]
        selection_raw = _end_state_record(records)
        selection_name = "end-state-record.json"
        harvest = records[0]
        length = 4096
    else:
        if harvest_path is None or recover_harvests:
            raise PromptPinError("issuer_mode_inputs_invalid")
        harvest = _load_harvest(harvest_path, verdict="SELECT")
        binding = harvest.record.get("selection")
        if (not isinstance(binding, dict) or set(binding) != {"path", "sha256"}
                or not isinstance(binding["path"], str) or not _is_sha256(binding["sha256"])):
            raise PromptPinError("harvest_selection_binding_invalid")
        selection_path = Path(binding["path"])
        if not selection_path.is_absolute():
            selection_path = harvest.root / selection_path
        selection, selection_raw = _load_json(_archive_file(harvest.root, selection_path), label="selection_record")
        if _sha256(selection_raw) != binding["sha256"]:
            raise PromptPinError("harvest_selection_sha256_mismatch")
        outputs = harvest.record.get("outputs")
        if not isinstance(outputs, dict) or outputs.get("selection.json") != binding["sha256"]:
            raise PromptPinError("harvest_output_sha256_mismatch")
        selection_name = "selection.json"
        summary, summary_raw, counts_receipt = _harvest_summary(harvest)
        length = _selection_from_inputs(selection, summary=summary, summary_sha256=_sha256(summary_raw))
    prompt_ladder_path, ladder, ladder_raw = _harvest_ladder(harvest)
    tokenizer_hash, rungs = _validate_ladder(ladder)
    rung = rungs[length]
    if not end_state:
        _validate_receipt(
            harvest=harvest,
            input_inventory=harvest.inventory_path,
            counts_receipt=counts_receipt,
            summary_raw=summary_raw,
            ladder_raw=ladder_raw,
            ladder=ladder,
            selected_length=length,
        )
    else:
        panel = harvest.inventory.get("panel")
        if not isinstance(panel, dict) or ladder["panel_thinking_policy"]["panel_sha256"] != panel.get("sha256"):
            raise PromptPinError("ladder_panel_binding_mismatch")
    observed_ids = runtime_prompt_token_ids(
        rung["prompt_text"], tokenizer_json_sha256=tokenizer_hash
    )
    if observed_ids != rung["prompt_token_ids"]:
        raise PromptPinError(f"runtime_prompt_token_ids_mismatch:{length}")
    if len(observed_ids) != length:
        raise PromptPinError(f"runtime_prompt_token_count_mismatch:{length}")
    if end_state:
        # NEEDS_RULING: the unchanged v2 loader requires an exhausted-ladder
        # condition that the implementation brief forbids for this mode.
        # Validate the authority and tokenizer, but publish no conflicting pin.
        raise PromptPinError("end_state_schema_ruling_required")
    ruling_paths = _ruling_trace_paths(ruling_trace)
    selection_hash = _sha256(selection_raw)
    selection_relative, selection_copy_hash = _bundle_reference(
        selection_name, selection_raw, bundle_dir=bundle_dir, label="selection_record"
    )
    ladder_relative, ladder_copy_hash = _bundle_reference(
        prompt_ladder_path.name, ladder_raw, bundle_dir=bundle_dir, label="prompt_ladder"
    )

    pin = {
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
        "special_token_policy": SPECIAL_TOKEN_POLICY,
        "prompt_text": rung["prompt_text"],
        "prompt_text_utf8_sha256": rung["prompt_text_utf8_sha256"],
        "prompt_token_ids": list(rung["prompt_token_ids"]),
        "prompt_token_ids_sha256": rung["prompt_token_ids_sha256"],
        "prompt_tokens": length,
        "repeat_count": rung["repeat_count"],
        "closing_sentence": rung["closing_sentence"],
        "generation_method": rung["generation_method"],
    }
    return _validate_pin(pin), {selection_relative: selection_raw, ladder_relative: ladder_raw}


def issue_pin(**kwargs: Any) -> dict[str, Any]:
    """Validate harvest-bound authority and return the closed v2 pin."""
    return _prepare_pin(**kwargs)[0]


def _pin_bytes(pin: dict[str, Any]) -> bytes:
    return (
        json.dumps(pin, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--harvest", type=Path)
    mode.add_argument("--end-state", action="store_true")
    parser.add_argument("--recover-harvest", action="append", default=[], type=Path)
    parser.add_argument("--registration", required=True, type=Path)
    parser.add_argument("--ruling-trace", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.output.exists():
            raise PromptPinError("output_already_exists")
        pin, copies = _prepare_pin(
            harvest_path=args.harvest,
            end_state=args.end_state,
            recover_harvests=args.recover_harvest,
            registration=args.registration,
            ruling_trace=args.ruling_trace,
            bundle_dir=args.output.parent,
        )
        for name, raw in copies.items():
            destination = args.output.parent / name
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
