"""Deterministic workload generators and scorers.

The affine ladder prompt is rendered as raw completion text. The suite harness
does not apply a chat template for prompt_text items; adapter tokenization owns
the model-specific wrapping behavior.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from joulewise.suite import (
    ORDER_POLICY_MANIFEST,
    SUITE_SCHEMA_VERSION,
    SuiteManifest,
    suite_manifest_sha256,
)


DOMAIN = "joulewise.workload.affine_mod_ladder.v1"
ANSWER_HASH_DOMAIN = "joulewise.affine_answer.v1"
SCORER_ID = "affine_mod_ladder_v1/score_v1"
GENERATOR_NAME = "affine_mod_ladder_v1"
GENERATOR_VERSION = "1.0.0"
PROMPT_TEMPLATE_ID = "affine_mod_ladder_v1/raw_completion_v1"
PLANNED_OUTPUT_TOKENS = 16
OUTPUT_POLICY = "natural_eos"
DEFAULT_SMOKE_LEVELS = (1, 8, 64)
DEFAULT_SMOKE_ITEMS_PER_LEVEL = 8
FULL_LEVELS = (1, 2, 4, 8, 16, 32, 64)
DEFAULT_SMOKE_SUITE_SEED = "affine-smoke-v1-2026-07-08"
DEFAULT_PLANNED_PROMPT_TOKENS = 80
SENTINEL_ITEM_ID = "affine_v1_sentinel"
SENTINEL_N_ITER = 1
SENTINEL_ITEM_INDEX = 8


@dataclass(frozen=True)
class AffineItem:
    a: int
    b: int
    m: int
    x0: int
    n_iter: int
    item_index: int
    expected: int


@dataclass(frozen=True)
class ScoreResult:
    parse_status: str
    parsed_value: int | None
    correct: bool


def _require_nonnegative_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be an integer >= 0")


def _require_positive_int(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")


def derive_item(suite_seed: str, n_iter: int, item_index: int) -> AffineItem:
    """Derive one affine modular recurrence item exactly from the v1 spec."""
    if not isinstance(suite_seed, str) or not suite_seed:
        raise ValueError("suite_seed must be a non-empty string")
    _require_positive_int(n_iter, "n_iter")
    _require_nonnegative_int(item_index, "item_index")
    msg = f"{DOMAIN}\0{suite_seed}\0{n_iter}\0{item_index}".encode("utf-8")
    digest = hashlib.sha256(msg).digest()
    m = 100 + int.from_bytes(digest[0:8], "big") % 900
    a = 10 + int.from_bytes(digest[8:16], "big") % 90
    b = 10 + int.from_bytes(digest[16:24], "big") % 90
    x0 = 100 + int.from_bytes(digest[24:32], "big") % 900
    x = x0
    for _ in range(n_iter):
        x = (a * x + b) % m
    return AffineItem(
        a=a,
        b=b,
        m=m,
        x0=x0,
        n_iter=n_iter,
        item_index=item_index,
        expected=x,
    )


def render_prompt(item: AffineItem) -> str:
    """Render raw completion prompt text; no chat template is applied here."""
    return (
        "Compute a modular recurrence.\n"
        f"Start with x = {item.x0}.\n"
        f"At each step, replace x with ({item.a} * x + {item.b}) mod {item.m}.\n"
        f"Perform exactly {item.n_iter} steps.\n"
        "Answer with only the final value of x as a decimal integer. "
        "Output nothing except that integer."
    )


def score_response(text: str, expected: int) -> ScoreResult:
    """Score an answer-only affine response by exact integer parsing."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if isinstance(expected, bool) or not isinstance(expected, int):
        raise TypeError("expected must be an integer")
    stripped = text.strip(" \t\n\r\x0b\x0c")
    if not re.fullmatch(r"[+-]?[0-9]+", stripped):
        return ScoreResult(parse_status="malformed", parsed_value=None, correct=False)
    parsed = int(stripped)
    return ScoreResult(
        parse_status="parsed",
        parsed_value=parsed,
        correct=(parsed == expected),
    )


def lenient_correct(text: str, expected: int) -> bool:
    """Diagnostic-only first-integer check; never part of the primary score."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if isinstance(expected, bool) or not isinstance(expected, int):
        raise TypeError("expected must be an integer")
    match = re.search(r"[+-]?[0-9]+", text)
    return bool(match and int(match.group(0)) == expected)


def expected_answer_sha256(item_id: str, expected: int) -> str:
    if not isinstance(item_id, str) or not item_id:
        raise ValueError("item_id must be a non-empty string")
    if isinstance(expected, bool) or not isinstance(expected, int):
        raise TypeError("expected must be an integer")
    payload = f"{ANSWER_HASH_DOMAIN}\0{item_id}\0{expected}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def affine_parameters_block(
    *,
    levels: tuple[int, ...] | list[int] = DEFAULT_SMOKE_LEVELS,
    items_per_level: int = DEFAULT_SMOKE_ITEMS_PER_LEVEL,
) -> dict[str, Any]:
    for level in levels:
        _require_positive_int(level, "levels[]")
    _require_positive_int(items_per_level, "items_per_level")
    return {
        "domain": DOMAIN,
        "m_range": [100, 999],
        "a_range": [10, 99],
        "b_range": [10, 99],
        "x0_range": [100, 999],
        "levels": list(levels),
        "items_per_level": items_per_level,
    }


def parameters_hash(
    *,
    levels: tuple[int, ...] | list[int] = DEFAULT_SMOKE_LEVELS,
    items_per_level: int = DEFAULT_SMOKE_ITEMS_PER_LEVEL,
    order_policy: str = ORDER_POLICY_MANIFEST,
) -> str:
    block = affine_parameters_block(levels=levels, items_per_level=items_per_level)
    if order_policy != ORDER_POLICY_MANIFEST:
        block["order_policy"] = order_policy
    payload = json.dumps(block, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def affine_item_id(n_iter: int, item_index: int) -> str:
    _require_positive_int(n_iter, "n_iter")
    _require_nonnegative_int(item_index, "item_index")
    return f"affine_v1_L{n_iter:02d}_i{item_index:02d}"


def affine_level_id(n_iter: int) -> str:
    _require_positive_int(n_iter, "n_iter")
    return f"L{n_iter:02d}"


def _difficulty(n_iter: int) -> dict[str, Any]:
    return {
        "axis": "iteration_count",
        "value": n_iter,
        "scale": "count",
        "label": f"{n_iter} iteration" if n_iter == 1 else f"{n_iter} iterations",
        "source": "generator_designed",
        "quarantine_note": (
            "C-004/C-015: designed effort proxy for stratified envelope analysis; "
            "licenses no 'difficulty causes energy' or intelligence-per-joule wording."
        ),
    }


def _shape() -> dict[str, Any]:
    return {
        "planned_prompt_tokens": DEFAULT_PLANNED_PROMPT_TOKENS,
        "planned_output_tokens": PLANNED_OUTPUT_TOKENS,
        "prompt_level": "affine_fixed_text_raw_completion",
        "decode_level": "answer_only_natural_eos_budget_16",
    }


def _item_mapping(
    *,
    suite_seed: str,
    n_iter: int,
    item_index: int,
    block_id: str,
    level_id: str,
    category: str = "affine_mod_ladder",
    tags: list[str] | None = None,
    condition_id: str | None = None,
    item_id_override: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    item = derive_item(suite_seed, n_iter, item_index)
    item_id = item_id_override or affine_item_id(n_iter, item_index)
    prompt = render_prompt(item)
    source_hash = _sha256_text(prompt)
    manifest_item = {
        "item_id": item_id,
        "item_type": "prompt_text",
        "category": category,
        "difficulty": _difficulty(n_iter),
        "shape": _shape(),
        "source": {
            "source_item_id": item_id,
            "source_sha256": source_hash,
            "prompt_template_id": PROMPT_TEMPLATE_ID,
            "license": "synthetic-internal",
            "contamination_note": "seed-derived synthetic arithmetic item",
            "prompt_text": prompt,
        },
        "grouping": {
            "condition_id": condition_id or level_id,
            "block_id": block_id,
            "level_id": level_id,
            "prefix_group_id": None,
        },
        "output_policy": OUTPUT_POLICY,
        "tags": list(tags or []),
    }
    annotation = {
        "item_id": item_id,
        "n_iter": n_iter,
        "item_index": item_index,
        "expected_answer": item.expected,
        "expected_answer_sha256": expected_answer_sha256(item_id, item.expected),
        "scorer_id": SCORER_ID,
        "source_sha256": source_hash,
        "tags": list(tags or []),
    }
    return manifest_item, annotation


def build_affine_smoke_manifest(
    suite_seed: str = DEFAULT_SMOKE_SUITE_SEED,
    order_policy: str = ORDER_POLICY_MANIFEST,
) -> dict[str, Any]:
    """Build the effective affine smoke suite manifest mapping."""
    items: list[dict[str, Any]] = []

    sentinel_start, _ = _item_mapping(
        suite_seed=suite_seed,
        n_iter=SENTINEL_N_ITER,
        item_index=SENTINEL_ITEM_INDEX,
        block_id="sentinel_start",
        level_id="sentinel_start",
        category="sentinel",
        tags=["sentinel"],
        condition_id="sentinel_start",
        item_id_override=SENTINEL_ITEM_ID,
    )
    items.append(sentinel_start)

    for n_iter in DEFAULT_SMOKE_LEVELS:
        level_id = affine_level_id(n_iter)
        for item_index in range(DEFAULT_SMOKE_ITEMS_PER_LEVEL):
            item, _ = _item_mapping(
                suite_seed=suite_seed,
                n_iter=n_iter,
                item_index=item_index,
                block_id=level_id,
                level_id=level_id,
            )
            items.append(item)

    sentinel_end, _ = _item_mapping(
        suite_seed=suite_seed,
        n_iter=SENTINEL_N_ITER,
        item_index=SENTINEL_ITEM_INDEX,
        block_id="sentinel_end",
        level_id="sentinel_end",
        category="sentinel",
        tags=["sentinel"],
        condition_id="sentinel_end",
        item_id_override=SENTINEL_ITEM_ID,
    )
    items.append(sentinel_end)

    subset_block: dict[str, Any] = {
        "suite_seed": suite_seed,
        "levels": list(DEFAULT_SMOKE_LEVELS),
        "items_per_level": DEFAULT_SMOKE_ITEMS_PER_LEVEL,
        "sentinel": {
            "item_id": SENTINEL_ITEM_ID,
            "n_iter": SENTINEL_N_ITER,
            "item_index": SENTINEL_ITEM_INDEX,
            "executions": 2,
        },
    }
    if order_policy != ORDER_POLICY_MANIFEST:
        subset_block["order_policy"] = order_policy
    subset_material = json.dumps(
        subset_block,
        sort_keys=True,
        separators=(",", ":"),
    )
    manifest = {
        "schema_version": SUITE_SCHEMA_VERSION,
        "suite_id": "affine_smoke_v1",
        "suite_profile": "affine_mod_ladder_v1_smoke",
        "suite_revision": "2026-07-08.p2-010b-unit1",
        "suite_seed": suite_seed,
        "generator": {
            "name": GENERATOR_NAME,
            "version": GENERATOR_VERSION,
            "parameters_hash": parameters_hash(
                levels=DEFAULT_SMOKE_LEVELS,
                items_per_level=DEFAULT_SMOKE_ITEMS_PER_LEVEL,
                order_policy=order_policy,
            ),
        },
        "analysis_contract": {
            "independent_unit": "bundle",
            "primary_window_class": "level_window",
            "allowed_aggregation_levels": ["level", "suite"],
        },
        "execution_policy": {
            "order_policy": order_policy,
            "within_bundle_repeats": 1,
            "cooldown_policy": "bundle_only",
            "declared_cache_policy": "warm_cache",
            "cache_policy_verification": "declared_not_verified",
            "warmup_policy": "adapter_default",
            "default_output_policy": OUTPUT_POLICY,
        },
        "source_manifest": {
            "source_id": "affine_mod_ladder_v1",
            "source_kind": "synthetic",
            "revision": GENERATOR_VERSION,
            "subset_id": "smoke_levels_1_8_64_x8",
            "subset_sha256": _sha256_text(subset_material),
            "license": "synthetic-internal",
            "contamination_note": "seed-derived synthetic arithmetic prompts",
        },
        "items": items,
    }
    return SuiteManifest.from_mapping(manifest).to_dict()


def build_affine_smoke_annotations(
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Build quarantined scorer sidecar annotations for a manifest."""
    suite = SuiteManifest.from_mapping(manifest)
    annotations: list[dict[str, Any]] = []
    for execution_index, suite_item in enumerate(suite.items):
        if suite_item.item_id == SENTINEL_ITEM_ID:
            n_iter = SENTINEL_N_ITER
            item_index = SENTINEL_ITEM_INDEX
        else:
            n_iter = int(suite_item.difficulty.value)
            marker = "_i"
            item_index = int(suite_item.item_id.split(marker, 1)[1])
        _, annotation = _item_mapping(
            suite_seed=suite.suite_seed,
            n_iter=n_iter,
            item_index=item_index,
            block_id=suite_item.grouping.block_id,
            level_id=suite_item.grouping.level_id,
            category=suite_item.category,
            tags=suite_item.tags,
            condition_id=suite_item.grouping.condition_id,
            item_id_override=(
                SENTINEL_ITEM_ID if suite_item.item_id == SENTINEL_ITEM_ID else None
            ),
        )
        annotation["execution_index"] = execution_index
        annotations.append(annotation)
    return {
        "schema_version": "affine_smoke_annotations.v1",
        "suite_id": suite.suite_id,
        "suite_seed": suite.suite_seed,
        "manifest_sha256": suite_manifest_sha256(suite.to_dict()),
        "quarantine": "expected answers are scorer inputs, not manifest fields",
        "consumer_note": (
            "Use this sidecar as the affine_mod_ladder_v1 scorer input; "
            "the suite manifest intentionally contains no expected answers "
            "or scoring fields."
        ),
        "scorer": {
            "scorer_id": SCORER_ID,
            "answer_hash_domain": ANSWER_HASH_DOMAIN,
            "prompt_template_id": PROMPT_TEMPLATE_ID,
        },
        "annotations": annotations,
    }


def write_affine_smoke_files(
    manifest_path: str | Path = "configs/suite_manifests/affine_smoke_v1.json",
    sidecar_path: str | Path | None = None,
    *,
    suite_seed: str = DEFAULT_SMOKE_SUITE_SEED,
    order_policy: str = ORDER_POLICY_MANIFEST,
) -> tuple[Path, Path, str]:
    manifest_file = Path(manifest_path)
    sidecar_file = (
        Path(sidecar_path)
        if sidecar_path is not None
        else manifest_file.with_name(manifest_file.stem + "_annotations.json")
    )
    manifest = build_affine_smoke_manifest(
        suite_seed=suite_seed,
        order_policy=order_policy,
    )
    annotations = build_affine_smoke_annotations(manifest)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    sidecar_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    sidecar_file.write_text(
        json.dumps(annotations, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_file, sidecar_file, suite_manifest_sha256(manifest)
