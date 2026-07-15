"""Backend-neutral suite traversal and marker bookkeeping.

Runtime adapters retain prompt materialization, generation, and status
decisions.  This module only sequences realized items, frames block/level
markers, and accumulates the already-decided per-item results.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from joulewise.interfaces import RuntimeEvent
from joulewise.suite import (
    BLOCK_END,
    BLOCK_START,
    LEVEL_END,
    LEVEL_START,
    SUITE_END,
    SUITE_PHASE,
    SUITE_START,
    SuiteItem,
    SuiteManifest,
    realized_order,
    suite_manifest_sha256,
)

EventFactory = Callable[[str, str, str, dict[str, Any] | None], RuntimeEvent]


@dataclass(frozen=True)
class SuiteItemResult:
    """An adapter-decided item outcome consumed by suite bookkeeping."""

    status: str
    prompt_tokens: int
    planned_output_tokens: int
    emitted_tokens: int
    prompt_hash: str
    output: dict[str, Any]
    backend_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SuiteControlResult:
    """Bookkeeping accumulated around backend-owned item execution."""

    events: list[RuntimeEvent]
    output_jsonl: str
    manifest_sha256: str
    total_prompt_tokens: int
    total_planned_output_tokens: int
    total_output_tokens: int
    prompt_hashes: list[str]
    status_counts: dict[str, int]
    item_results: list[SuiteItemResult]
    suite_provenance: dict[str, Any]


def execute_suite(
    manifest: SuiteManifest,
    *,
    backend_name: str,
    order_seed: str,
    order_row: int | None,
    event_factory: EventFactory,
    run_item: Callable[
        [SuiteItem, int, int, str | None, list[RuntimeEvent]], SuiteItemResult
    ],
) -> SuiteControlResult:
    """Traverse and frame a suite while delegating every item outcome."""

    manifest_sha256 = suite_manifest_sha256(manifest.to_dict())
    suite_start_metadata: dict[str, Any] = {
        "suite_id": manifest.suite_id,
        "suite_profile": manifest.suite_profile,
        "suite_revision": manifest.suite_revision,
        "suite_manifest_sha256": manifest_sha256,
        "item_count": len(manifest.items),
        "order_policy": manifest.execution_policy.order_policy,
        "order_seed": order_seed,
    }
    if order_row is not None:
        suite_start_metadata["order_row"] = order_row

    events = [
        event_factory(
            SUITE_START,
            SUITE_PHASE,
            f"{backend_name} suite started",
            suite_start_metadata,
        )
    ]
    output_lines: list[str] = []
    status_counts: dict[str, int] = {}
    total_prompt_tokens = 0
    total_planned_output_tokens = 0
    total_output_tokens = 0
    prompt_hashes: list[str] = []
    item_results: list[SuiteItemResult] = []
    previous_item_id: str | None = None
    current_block: str | None = None
    current_level: str | None = None
    block_indices: dict[str, int] = {}
    level_indices: dict[tuple[str, str], int] = {}

    def end_level(block_id: str, level_id: str) -> None:
        events.append(
            event_factory(
                LEVEL_END,
                SUITE_PHASE,
                f"{backend_name} level {level_id} ended",
                {
                    "level_id": level_id,
                    "level_index": level_indices[(block_id, level_id)],
                },
            )
        )

    def end_block(block_id: str) -> None:
        events.append(
            event_factory(
                BLOCK_END,
                SUITE_PHASE,
                f"{backend_name} block {block_id} ended",
                {"block_id": block_id, "block_index": block_indices[block_id]},
            )
        )

    for realized in realized_order(manifest, order_row=order_row):
        item = realized.item
        item_index = realized.item_index
        position = realized.position
        block_id = item.grouping.block_id
        level_id = item.grouping.level_id

        if block_id != current_block:
            if current_level is not None and current_block is not None:
                end_level(current_block, current_level)
                current_level = None
            if current_block is not None:
                end_block(current_block)
            block_indices.setdefault(block_id, len(block_indices))
            events.append(
                event_factory(
                    BLOCK_START,
                    SUITE_PHASE,
                    f"{backend_name} block {block_id} started",
                    {"block_id": block_id, "block_index": block_indices[block_id]},
                )
            )
            current_block = block_id

        if level_id != current_level:
            if current_level is not None:
                end_level(block_id, current_level)
            level_key = (block_id, level_id)
            level_indices.setdefault(level_key, len(level_indices))
            events.append(
                event_factory(
                    LEVEL_START,
                    SUITE_PHASE,
                    f"{backend_name} level {level_id} started",
                    {"level_id": level_id, "level_index": level_indices[level_key]},
                )
            )
            current_level = level_id

        item_result = run_item(
            item,
            item_index,
            position,
            previous_item_id,
            events,
        )
        item_results.append(item_result)
        previous_item_id = item.item_id
        output_lines.append(json.dumps(item_result.output, sort_keys=True) + "\n")
        status_counts[item_result.status] = status_counts.get(item_result.status, 0) + 1
        total_prompt_tokens += item_result.prompt_tokens
        total_planned_output_tokens += item_result.planned_output_tokens
        total_output_tokens += item_result.emitted_tokens
        prompt_hashes.append(item_result.prompt_hash)

    if current_level is not None and current_block is not None:
        end_level(current_block, current_level)
    if current_block is not None:
        end_block(current_block)
    events.append(
        event_factory(
            SUITE_END,
            SUITE_PHASE,
            f"{backend_name} suite completed",
            {
                "suite_id": manifest.suite_id,
                "items_executed": len(manifest.items),
                "status_counts": status_counts,
            },
        )
    )

    return SuiteControlResult(
        events=events,
        output_jsonl="".join(output_lines),
        manifest_sha256=manifest_sha256,
        total_prompt_tokens=total_prompt_tokens,
        total_planned_output_tokens=total_planned_output_tokens,
        total_output_tokens=total_output_tokens,
        prompt_hashes=prompt_hashes,
        status_counts=status_counts,
        item_results=item_results,
        suite_provenance={
            "suite_id": manifest.suite_id,
            "manifest_sha256": manifest_sha256,
            "item_count": len(manifest.items),
            "order_policy": manifest.execution_policy.order_policy,
            "order_seed": order_seed,
            "order_row": order_row,
        },
    )
