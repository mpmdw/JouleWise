#!/usr/bin/env python3
"""Generate Slice 2M workload-matrix configs from one base config.

The output is intentionally hash-stable for the same base file: no timestamps,
no randomness, fixed top-level key order, two-space JSON indentation, and a
trailing newline. Nested key order follows the base config, and ``sort_keys`` is
deliberately not used so generated configs keep the repo's hand-authored style.

The Slice 2M footnote's target-memory cap is out of scope for this static
generator. Only ``model.context_window`` is applied to the long_short prompt;
memory-driven caps must be pre-applied by the operator in the base config.

Generated run IDs are ``<model-tag>-<profile>``. When multiple targets share one
runs directory, include the target in ``--model-tag`` (for example,
``mac-qwen25-1p5b``) so the resulting run IDs remain distinct.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.schemas import BenchmarkConfig  # noqa: E402


PROFILE_MATRIX = (
    ("short_short", 128, 64),
    ("long_short", 4096, 64),
    ("short_long", 128, 512),
    ("mid_mid", 1024, 256),
)
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


def build_config(base: dict[str, Any], model_tag: str, profile_name: str, prompt_tokens: int, output_tokens: int) -> dict[str, Any]:
    run_id = f"{model_tag}-{profile_name}"
    effective_prompt_tokens, cap_tag = profile_prompt_tokens(base, profile_name, prompt_tokens)

    run_metadata = copy.deepcopy(base.get("run_metadata", {"project": "joulewise"}))
    if not isinstance(run_metadata, dict):
        raise ValueError("run_metadata must be an object")
    tags = run_metadata.get("tags", [])
    if not isinstance(tags, list):
        raise ValueError("run_metadata.tags must be a list")
    run_metadata["tags"] = list(tags) + ["2m", profile_name] + ([cap_tag] if cap_tag else [])

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
            "repetitions": 5,
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
    path.write_text(rendered, encoding="utf-8")


def expected_output_paths(out_dir: Path, model_tag: str) -> set[Path]:
    return {
        out_dir / f"{model_tag}-{profile_name}.json"
        for profile_name, _, _ in PROFILE_MATRIX
    }


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
    for profile_name in PROFILE_NAMES:
        suffix = f"-{profile_name}.json"
        if filename.endswith(suffix):
            return filename[: -len(suffix)]
    return None


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
        for profile_name, prompt_tokens, output_tokens in PROFILE_MATRIX:
            config = build_config(base, args.model_tag, profile_name, prompt_tokens, output_tokens)
            path = out_dir / f"{args.model_tag}-{profile_name}.json"
            write_config(path, config)
            written.append(path)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
