#!/usr/bin/env python3
"""Generate Slice 2M workload-matrix configs from one base config.

The output is intentionally hash-stable for the same base file: no timestamps,
no randomness, fixed top-level key order, two-space JSON indentation, and a
trailing newline. Nested key order follows the base config, and ``sort_keys`` is
deliberately not used so generated configs keep the repo's hand-authored style.

The Slice 2M footnote's target-memory cap is out of scope for this static
generator. Only ``model.context_window`` is applied to the long_short prompt;
memory-driven caps must be pre-applied by the operator in the base config.
The four built-in profiles are baseline shapes, not a representative workload
corpus; P2-010/P2-012 own workload expansion.

Generated baseline run IDs are ``<model-tag>-r<rep>-<profile>``. Drift
sentinel run IDs are ``<model-tag>-r<rep>-short_short_sentinel-start`` and
``<model-tag>-r<rep>-short_short_sentinel-end``. When multiple targets share
one runs directory, include the target in ``--model-tag`` (for example,
``mac-qwen25-1p5b``) so the resulting run IDs remain distinct.

The generated ``order_manifest.json`` records the deterministic execution
order. Each ``(model_tag, rep)`` block contains one start sentinel, the four
rotated baseline workloads, and one end sentinel. Sentinel entries carry
``role: "drift_sentinel"`` and ``sentinel_position: "start"|"end"``; every
entry carries ``block_index`` and ``position_in_block``.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.schemas import BenchmarkConfig  # noqa: E402
from joulewise.analysis_manifest import (  # noqa: E402
    ANALYSIS_MANIFEST_NAME,
    build_slice_2m_analysis_manifest,
    write_manifest_atomic,
)


PROFILE_MATRIX = (
    ("short_short", 128, 64),
    ("long_short", 4096, 64),
    ("short_long", 128, 512),
    ("mid_mid", 1024, 256),
)
SENTINEL_PROFILE = ("short_short_sentinel", 128, 64)
SENTINEL_PROFILE_NAME = SENTINEL_PROFILE[0]
SENTINEL_POSITIONS = ("start", "end")
SENTINEL_ROLE = "drift_sentinel"
REPETITIONS = 5
ORDER_MANIFEST_NAME = "order_manifest.json"
ORDER_SEED = 2000005
MODEL_TAG_RE = re.compile(r"^[a-z0-9_-]+$")
PROFILE_NAMES = tuple(profile_name for profile_name, _, _ in PROFILE_MATRIX)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Base config JSON path")
    parser.add_argument("--model-tag", required=True, help="Lowercase model tag for run_id")
    parser.add_argument("--out-dir", required=True, help="Directory for generated configs")
    return parser.parse_args(argv)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"failed to read base config {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"base config is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"base config must be a JSON object: {path}")
    return data


def profile_prompt_tokens(base: dict[str, Any], profile_name: str, prompt_tokens: int) -> tuple[int, str | None]:
    if profile_name != "long_short":
        return prompt_tokens, None
    model = base.get("model")
    if not isinstance(model, dict):
        return prompt_tokens, None
    context_window = model.get("context_window")
    if isinstance(context_window, bool) or not isinstance(context_window, int):
        return prompt_tokens, None
    if context_window < prompt_tokens:
        return context_window, f"prompt_capped_{context_window}"
    return prompt_tokens, None


def build_config(
    base: dict[str, Any],
    model_tag: str,
    profile_name: str,
    prompt_tokens: int,
    output_tokens: int,
    rep: int,
    run_id_suffix: str | None = None,
) -> dict[str, Any]:
    run_id = f"{model_tag}-r{rep}-{profile_name}"
    if run_id_suffix is not None:
        run_id = f"{run_id}-{run_id_suffix}"
    effective_prompt_tokens, cap_tag = profile_prompt_tokens(base, profile_name, prompt_tokens)

    run_metadata = copy.deepcopy(base.get("run_metadata", {"project": "joulewise"}))
    if not isinstance(run_metadata, dict):
        raise ValueError("run_metadata must be an object")
    tags = run_metadata.get("tags", [])
    if not isinstance(tags, list):
        raise ValueError("run_metadata.tags must be a list")
    extra_tags = ["2m", profile_name, f"rep{rep}"]
    if profile_name == SENTINEL_PROFILE_NAME:
        if run_id_suffix not in SENTINEL_POSITIONS:
            raise ValueError(
                f"{SENTINEL_PROFILE_NAME} requires run_id_suffix in {SENTINEL_POSITIONS}"
            )
        extra_tags.extend([SENTINEL_ROLE, f"sentinel_{run_id_suffix}"])
    if cap_tag:
        extra_tags.append(cap_tag)
    run_metadata["tags"] = list(tags) + extra_tags

    config = {
        "schema_version": copy.deepcopy(base.get("schema_version")),
        "run_id": run_id,
        "model": copy.deepcopy(base.get("model")),
        "quantization": copy.deepcopy(base.get("quantization")),
        "hardware_target": copy.deepcopy(base.get("hardware_target")),
        "workload_profile": {
            "name": profile_name,
            "prompt_tokens": effective_prompt_tokens,
            "output_tokens": output_tokens,
            "repetitions": 1,
            "warmup_runs": 1,
        },
        "interconnect": copy.deepcopy(base.get("interconnect")),
        "sampling": copy.deepcopy(base.get("sampling")),
        "run_metadata": run_metadata,
    }
    BenchmarkConfig.from_mapping(config).validate()
    return config


def write_config(path: Path, config: dict[str, Any]) -> None:
    rendered = json.dumps(config, indent=2) + "\n"
    path.write_text(rendered, encoding="utf-8", newline="\n")


def expected_output_paths(out_dir: Path, model_tag: str) -> set[Path]:
    baseline_paths = {
        out_dir / f"{model_tag}-r{rep}-{profile_name}.json"
        for rep in range(1, REPETITIONS + 1)
        for profile_name, _, _ in PROFILE_MATRIX
    }
    sentinel_paths = {
        out_dir / f"{model_tag}-r{rep}-{SENTINEL_PROFILE_NAME}-{position}.json"
        for rep in range(1, REPETITIONS + 1)
        for position in SENTINEL_POSITIONS
    }
    return baseline_paths | sentinel_paths


def stale_same_tag_paths(out_dir: Path, model_tag: str, expected_paths: set[Path]) -> list[Path]:
    expected_names = {path.name for path in expected_paths}
    stale_paths: list[Path] = []
    for path in sorted(out_dir.glob(f"{model_tag}-*.json")):
        if path.name in expected_names:
            continue
        generated_tag = model_tag_from_generated_filename(path.name)
        if generated_tag is not None and generated_tag != model_tag:
            continue
        stale_paths.append(path)
    return stale_paths


def model_tag_from_generated_filename(filename: str) -> str | None:
    parsed = parse_generated_filename(filename)
    if parsed is not None:
        return parsed[0]
    return None


def parse_generated_filename(filename: str) -> tuple[str, int, str] | None:
    for position in SENTINEL_POSITIONS:
        sentinel_profile = f"{SENTINEL_PROFILE_NAME}-{position}"
        suffix = f"-{sentinel_profile}.json"
        parsed = parse_generated_filename_with_suffix(filename, suffix, sentinel_profile)
        if parsed is not None:
            return parsed
    for profile_name in PROFILE_NAMES:
        suffix = f"-{profile_name}.json"
        parsed = parse_generated_filename_with_suffix(filename, suffix, profile_name)
        if parsed is not None:
            return parsed
    return None


def parse_generated_filename_with_suffix(
    filename: str,
    suffix: str,
    profile_name: str,
) -> tuple[str, int, str] | None:
    if not filename.endswith(suffix):
        return None
    prefix = filename[: -len(suffix)]
    marker = "-r"
    marker_index = prefix.rfind(marker)
    if marker_index == -1:
        return None
    model_tag = prefix[:marker_index]
    rep_text = prefix[marker_index + len(marker):]
    if not model_tag or not rep_text.isdigit():
        return None
    rep = int(rep_text)
    if 1 <= rep <= REPETITIONS:
        return model_tag, rep, profile_name
    return None


def workload_order_for_rep(rep: int) -> list[str]:
    names = list(PROFILE_NAMES)
    if rep < REPETITIONS:
        offset = rep - 1
        return names[offset:] + names[:offset]
    rng = random.Random(ORDER_SEED)
    seeded = names[:]
    rng.shuffle(seeded)
    return seeded


def model_order_for_rep(model_tags: list[str], rep: int) -> list[str]:
    if len(model_tags) <= 1:
        return model_tags[:]
    if rep in {1, 4}:
        return model_tags[:]
    if rep in {2, 3}:
        return list(reversed(model_tags))
    rng = random.Random(ORDER_SEED + rep)
    seeded = model_tags[:]
    rng.shuffle(seeded)
    return seeded


def generated_matrix_entries(out_dir: Path) -> list[tuple[Path, str, int, str, str]]:
    entries: list[tuple[Path, str, int, str, str]] = []
    for path in sorted(out_dir.glob("*.json")):
        if path.name in {ORDER_MANIFEST_NAME, ANALYSIS_MANIFEST_NAME}:
            continue
        parsed = parse_generated_filename(path.name)
        if parsed is None:
            continue
        model_tag, rep, profile_name = parsed
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        run_id = payload.get("run_id")
        if not isinstance(run_id, str):
            run_id = path.stem
        entries.append((path, model_tag, rep, profile_name, run_id))
    return entries


def build_order_manifest(out_dir: Path) -> dict[str, Any]:
    """Build the generated execution-order manifest.

    ``rotation_scheme.workloads`` intentionally lists only the four rotated
    baseline workloads. The distinct ``short_short_sentinel`` profile is fixed
    at the start and end of each model block, not rotated with the baseline
    workload sequence.
    """
    entries = generated_matrix_entries(out_dir)
    by_key = {
        (model_tag, rep, profile_name): (path, run_id)
        for path, model_tag, rep, profile_name, run_id in entries
    }
    model_tags = sorted({model_tag for _, model_tag, _, _, _ in entries})
    missing_sentinels: list[str] = []
    for model_tag in model_tags:
        for rep in range(1, REPETITIONS + 1):
            missing_positions = [
                position
                for position in SENTINEL_POSITIONS
                if (model_tag, rep, f"{SENTINEL_PROFILE_NAME}-{position}") not in by_key
            ]
            if missing_positions:
                missing_sentinels.append(
                    f"(model_tag={model_tag}, rep={rep}: {', '.join(missing_positions)})"
                )
    if missing_sentinels:
        raise ValueError(
            "missing drift sentinel config(s) for block(s): "
            + "; ".join(missing_sentinels)
        )

    executed_order: list[dict[str, Any]] = []
    rep_workload_order: dict[str, list[str]] = {}
    rep_model_order: dict[str, list[str]] = {}
    index = 1
    block_index = 1
    for rep in range(1, REPETITIONS + 1):
        workload_order = workload_order_for_rep(rep)
        model_order = model_order_for_rep(model_tags, rep)
        rep_workload_order[str(rep)] = workload_order
        rep_model_order[str(rep)] = model_order
        for model_tag in model_order:
            block_position = 1
            start_entry = by_key.get((model_tag, rep, f"{SENTINEL_PROFILE_NAME}-start"))
            if start_entry is not None:
                path, run_id = start_entry
                executed_order.append(
                    {
                        "index": index,
                        "config": path.name,
                        "run_id": run_id,
                        "model_tag": model_tag,
                        "rep": rep,
                        "workload": SENTINEL_PROFILE_NAME,
                        "role": SENTINEL_ROLE,
                        "sentinel_position": "start",
                        "block_index": block_index,
                        "position_in_block": block_position,
                    }
                )
                index += 1
                block_position += 1
            for workload in workload_order:
                entry = by_key.get((model_tag, rep, workload))
                if entry is None:
                    continue
                path, run_id = entry
                executed_order.append(
                    {
                        "index": index,
                        "config": path.name,
                        "run_id": run_id,
                        "model_tag": model_tag,
                        "rep": rep,
                        "workload": workload,
                        "block_index": block_index,
                        "position_in_block": block_position,
                    }
                )
                index += 1
                block_position += 1
            end_entry = by_key.get((model_tag, rep, f"{SENTINEL_PROFILE_NAME}-end"))
            if end_entry is not None:
                path, run_id = end_entry
                executed_order.append(
                    {
                        "index": index,
                        "config": path.name,
                        "run_id": run_id,
                        "model_tag": model_tag,
                        "rep": rep,
                        "workload": SENTINEL_PROFILE_NAME,
                        "role": SENTINEL_ROLE,
                        "sentinel_position": "end",
                        "block_index": block_index,
                        "position_in_block": block_position,
                    }
                )
                index += 1
            block_index += 1
    if len(model_tags) == 2:
        imbalance_note = (
            "Two-model block order is A-B, B-A, B-A, A-B, then seeded for rep5; "
            "the first four reps are balanced and rep5 records the deterministic "
            "seeded imbalance."
        )
    else:
        imbalance_note = (
            f"{len(model_tags)} model tag(s) present; model block order uses sorted, "
            "reversed, reversed, sorted, then seeded order by repetition."
        )
    return {
        "schema_version": "joulewise.order_manifest.v1",
        "seed": ORDER_SEED,
        "rotation_scheme": {
            "workloads": list(PROFILE_NAMES),
            "rep_workload_order": rep_workload_order,
            "rep_model_order": rep_model_order,
        },
        "imbalance_note": imbalance_note,
        "executed_order": executed_order,
    }


def write_order_manifest(out_dir: Path) -> Path:
    manifest = build_order_manifest(out_dir)
    path = out_dir / ORDER_MANIFEST_NAME
    write_manifest_atomic(path, manifest)
    return path


def write_analysis_manifest(out_dir: Path) -> Path:
    manifest = build_slice_2m_analysis_manifest(out_dir, repository_root=ROOT)
    path = out_dir / ANALYSIS_MANIFEST_NAME
    write_manifest_atomic(path, manifest)
    return path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not MODEL_TAG_RE.fullmatch(args.model_tag):
        print(
            "error: --model-tag must match [a-z0-9_-]+ so run_id survives bundle sanitization",
            file=sys.stderr,
        )
        return 2

    try:
        base = load_json(Path(args.base))
        BenchmarkConfig.from_mapping(base).validate()
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        expected_paths = expected_output_paths(out_dir, args.model_tag)
        stale_paths = stale_same_tag_paths(out_dir, args.model_tag, expected_paths)
        if stale_paths:
            stale_list = ", ".join(str(path) for path in stale_paths)
            raise ValueError(
                f"refusing to write into {out_dir}: stale same-tag JSON file(s) "
                f"would be left in place: {stale_list}"
            )
        written: list[Path] = []
        for rep in range(1, REPETITIONS + 1):
            for profile_name, prompt_tokens, output_tokens in PROFILE_MATRIX:
                config = build_config(
                    base, args.model_tag, profile_name, prompt_tokens, output_tokens, rep
                )
                path = out_dir / f"{args.model_tag}-r{rep}-{profile_name}.json"
                write_config(path, config)
                written.append(path)
            for position in SENTINEL_POSITIONS:
                profile_name, prompt_tokens, output_tokens = SENTINEL_PROFILE
                config = build_config(
                    base,
                    args.model_tag,
                    profile_name,
                    prompt_tokens,
                    output_tokens,
                    rep,
                    run_id_suffix=position,
                )
                path = out_dir / f"{args.model_tag}-r{rep}-{profile_name}-{position}.json"
                write_config(path, config)
                written.append(path)
        manifest_path = write_order_manifest(out_dir)
        analysis_manifest_path = write_analysis_manifest(out_dir)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for path in written:
        print(path)
    print(manifest_path)
    print(analysis_manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
