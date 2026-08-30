#!/usr/bin/env python3
"""Generate the pinned GSM8K scored-v6 suite manifest and sidecar.

This is the canonical producer. ``scripts/gsm8k_import.py`` is a deprecated
stall-era duplicate retained only for lead-owned deletion; do not add consumers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.benchmark_import import (
    K_ITEMS,
    OUTPUT_CAP,
    build_gsm8k_scored_annotations,
    build_gsm8k_scored_manifest,
    load_gsm8k_test,
    render_prompts,
    select_items,
)
from joulewise.suite import suite_manifest_sha256


def _write_json(path: Path, payload: Mapping[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialized, encoding="utf-8")
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-jsonl", required=True)
    parser.add_argument(
        "--tokenizer-dir",
        action="append",
        required=True,
        help="local tokenizer mirror (repeat to assert cross-model equality)",
    )
    parser.add_argument(
        "--out-manifest",
        default="configs/suite_manifests/gsm8k_scored_v6_qwen3.json",
    )
    parser.add_argument(
        "--out-annotations",
        default="configs/suite_manifests/gsm8k_scored_v6_qwen3_annotations.json",
    )
    args = parser.parse_args(argv)

    records = load_gsm8k_test(args.test_jsonl)
    selected = select_items(records, K_ITEMS)
    rendered = render_prompts(selected, [Path(value) for value in args.tokenizer_dir])
    manifest = build_gsm8k_scored_manifest(
        records,
        rendered,
        k=K_ITEMS,
        output_cap=OUTPUT_CAP,
    )
    annotations = build_gsm8k_scored_annotations(manifest, records)

    manifest_path = Path(args.out_manifest)
    annotations_path = Path(args.out_annotations)
    manifest_file_sha256 = _write_json(manifest_path, manifest)
    annotations_file_sha256 = _write_json(annotations_path, annotations)

    print(f"wrote {manifest_path}")
    print(f"wrote {annotations_path}")
    print(f"suite_manifest_sha256 {suite_manifest_sha256(manifest)}")
    print(f"manifest_file_sha256 {manifest_file_sha256}")
    print(f"annotations_file_sha256 {annotations_file_sha256}")
    print(
        "selected_item_ids_sha256 "
        f"{manifest['benchmark_import']['selected_item_ids_sha256']}"
    )
    print(
        "canonical_subset_json_sha256 "
        f"{manifest['benchmark_import']['canonical_subset_json_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
