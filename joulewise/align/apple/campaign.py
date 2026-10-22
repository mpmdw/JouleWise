"""Generate alignment members through the existing workload-matrix generator.

Only the member payload changes. Shared campaign rendering/write checks and
scripts.run_campaign remain the generator and execution paths used in tests.
No plan is armed or installed by this module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

from joulewise.align.apple.workload import EpisodeSpec, WORKLOAD_KIND
from joulewise.campaign_generator_core import (
    render_json, sha256_bytes, validate_generation_write_boundary,
)
from joulewise.schemas import BenchmarkConfig


def generate_campaign(
    base: BenchmarkConfig, specs: Sequence[EpisodeSpec], output_root: Path, *,
    model_tag: str,
) -> tuple[Path, ...]:
    """Write one ordinary config per task/condition/seed, plus a pack manifest.

    The returned paths go to the existing run_campaign.py. They use exactly one
    repetition: seed replication is expressed as another episode specification.
    Scientific policy, hazards and calibration remain the caller's campaign
    policy and launch bindings.
    """
    from scripts.generate_matrix import build_config

    outputs: dict[Path, bytes] = {}
    members: list[dict[str, Any]] = []
    for ordinal, spec in enumerate(specs, 1):
        # build_config requires positive provisional token shapes. The declared
        # token budget is used only while creating the ordinary matrix template;
        # both provisional counts are removed before emitting the episode spec.
        value = build_config(
            base.to_dict(), model_tag, WORKLOAD_KIND,
            spec.max_tokens, spec.max_tokens, ordinal,
        )
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
    outputs[Path("align_pack.json")] = render_json({
        "schema": "joulewise.align.apple.campaign_pack.v1",
        "status": "PROVISIONAL_UNREGISTERED",
        "members": members,
        "flags": ["not_a_registered_measurement_plan"],
    }, lambda item: item)
    root = Path(output_root)
    validate_generation_write_boundary(root, outputs)
    for relative, raw in outputs.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != raw:
            # Immutable campaign identity: never silently replace earlier
            # generated members. Caller chooses a fresh pack destination.
            raise FileExistsError(path)
        if not path.exists():
            with path.open("xb") as handle:
                handle.write(raw)
    return tuple(root / Path(row["path"]) for row in members)
