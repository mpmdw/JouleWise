"""Generate counterbalanced alignment members through the existing matrix path.

Shared rendering/write-boundary checks and scripts.run_campaign remain the
execution path. Pack identities survive regeneration; nothing is registered,
armed or installed here.
"""

from __future__ import annotations

import json
import uuid
from collections import deque
from pathlib import Path
from typing import Any, Sequence

from joulewise.align.apple.workload import EpisodeSpec, WORKLOAD_KIND
from joulewise.campaign_generator_core import (
    render_json, sha256_bytes, validate_generation_write_boundary,
)
from joulewise.schemas import BenchmarkConfig


def _counterbalanced(specs: Sequence[EpisodeSpec]) -> tuple[tuple[EpisodeSpec, ...], tuple[str, ...]]:
    """Match task/seed/control cells, alternate AB and BA, retain unmatched cells."""
    cells: dict[str, dict[str, deque[EpisodeSpec]]] = {}
    for spec in specs:
        key = json.dumps({
            "task_factory": spec.task_factory, "task_kwargs": spec.task_kwargs,
            "seed": spec.seed, "max_turns": spec.max_turns,
            "max_tokens": spec.max_tokens, "temperature": spec.temperature,
        }, sort_keys=True)
        cell = cells.setdefault(key, {"benign": deque(), "sabotage": deque()})
        cell[spec.condition].append(spec)
    pairs = []
    unmatched = []
    for cell in cells.values():
        while cell["benign"] and cell["sabotage"]:
            pairs.append((cell["benign"].popleft(), cell["sabotage"].popleft()))
        unmatched.extend(cell["benign"])
        unmatched.extend(cell["sabotage"])
    ordered = []
    for index, pair in enumerate(pairs):
        # Two matched pairs form ABBA; reverse the second pair to cancel
        # linear order drift without duplicating or removing any episode.
        ordered.extend(pair if index % 2 == 0 else reversed(pair))
    ordered.extend(unmatched)
    flags = ("unmatched_condition_cells_retained",) if unmatched else ()
    return tuple(ordered), flags


def generate_campaign(
    base: BenchmarkConfig, specs: Sequence[EpisodeSpec], output_root: Path, *,
    model_tag: str, counterbalance: bool = True,
) -> tuple[Path, ...]:
    """Write one config per episode and the runner's explicit order_manifest.

    Seed replication is another spec, never a repetition of a whole episode.
    A fresh pack gets a UUID persisted in align_pack.json so independent packs
    sharing a model_tag cannot collide in the runs directory.
    """
    from scripts.generate_matrix import build_config

    root = Path(output_root)
    manifest_path = root / "align_pack.json"
    if manifest_path.exists():
        pack_id = json.loads(manifest_path.read_text())["pack_id"]
    else:
        pack_id = uuid.uuid4().hex
    ordered, order_flags = _counterbalanced(specs) if counterbalance else (
        tuple(specs), ("caller_supplied_condition_order",)
    )
    outputs: dict[Path, bytes] = {}
    members: list[dict[str, Any]] = []
    executed_order = []
    for ordinal, spec in enumerate(ordered, 1):
        # build_config needs provisional token shapes; remove them before
        # emitting the episode's canonical spec and one-episode semantics.
        value = build_config(
            base.to_dict(), model_tag, WORKLOAD_KIND,
            spec.max_tokens, spec.max_tokens, ordinal,
        )
        value["run_id"] = f"{model_tag}-{pack_id}-episode-{ordinal}"
        value["run_metadata"]["tags"] = [
            *base.to_dict()["run_metadata"].get("tags", []),
            "align", WORKLOAD_KIND, f"episode{ordinal}", spec.condition,
        ]
        value["workload_profile"] = {
            "name": WORKLOAD_KIND, "prompt_text": spec.to_text(),
            "repetitions": 1, "warmup_runs": base.workload_profile.warmup_runs,
        }
        config = BenchmarkConfig.from_mapping(value)
        relative = Path("members") / f"{ordinal:06d}.json"
        raw = render_json(config.to_dict(), lambda item: item)
        outputs[relative] = raw
        members.append({
            "path": relative.as_posix(), "run_id": config.run_id,
            "sha256": sha256_bytes(raw), "task_factory": spec.task_factory,
            "condition": spec.condition, "seed": spec.seed,
        })
        executed_order.append({
            "index": ordinal, "config": relative.name, "run_id": config.run_id,
            "model_tag": model_tag, "workload": WORKLOAD_KIND, "rep": 1,
        })
    outputs[Path("members/order_manifest.json")] = render_json({
        "order_policy": "matched_condition_abba" if counterbalance else "caller_supplied",
        "executed_order": executed_order, "flags": list(order_flags),
    }, lambda item: item)
    outputs[Path("align_pack.json")] = render_json({
        "schema": "joulewise.align.apple.campaign_pack.v1",
        "status": "PROVISIONAL_UNREGISTERED", "pack_id": pack_id,
        "members": members,
        "flags": ["not_a_registered_measurement_plan", *order_flags],
    }, lambda item: item)
    validate_generation_write_boundary(root, outputs)
    for relative, raw in outputs.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != raw:
            raise FileExistsError(path)
        if not path.exists():
            with path.open("xb") as handle:
                handle.write(raw)
    return tuple(root / Path(row["path"]) for row in members)
