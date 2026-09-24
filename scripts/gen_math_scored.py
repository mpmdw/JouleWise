#!/usr/bin/env python3
"""Produce untracked full MATH manifests and a tracked hash-only receipt."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.benchmark_import_math import (
    build_math_annotations, build_math_manifest, build_math_suite_manifest,
    canonical_json_sha256, eligible_records, hash_only_manifest,
    load_math_test, render_prompts, select_items, select_pilot,
)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    source = Path.home() / "jw_data/math-prm800k-7ecc7947"
    parser.add_argument("--test-jsonl", type=Path, default=source / "prm_test.jsonl")
    parser.add_argument("--train-jsonl", type=Path, default=source / "prm_train.jsonl")
    parser.add_argument("--pointer-test", type=Path, default=source / "ptr_test.txt")
    parser.add_argument("--pointer-train", type=Path, default=source / "ptr_train.txt")
    parser.add_argument("--license", type=Path, default=source / "prm_LICENSE")
    parser.add_argument("--out-dir", type=Path, default=Path.home() / "jw_data/math-scored-v1")
    parser.add_argument("--hash-only-out", type=Path, default=ROOT / "tests/fixtures/math/hash_only_manifest.json")
    parser.add_argument("--tokenizer-dir", action="append", default=[])
    parser.add_argument("--arm", choices=("off", "on"), default="off")
    parser.add_argument("--output-cap", type=int, help="registered output cap for native suite manifests")
    args = parser.parse_args(argv)
    if args.tokenizer_dir and (args.output_cap is None or args.output_cap <= 0):
        parser.error("--output-cap is required with --tokenizer-dir")
    if args.out_dir.resolve().is_relative_to(ROOT.resolve()):
        parser.error("full manifests containing problem text must be written outside the repository")
    rows, receipts = load_math_test(args.test_jsonl, args.train_jsonl, pointer_test=args.pointer_test, pointer_train=args.pointer_train, license_path=args.license)
    eligible, stats = eligible_records(rows)
    pilot = select_pilot(eligible)
    selected = {"pilot": pilot, "n64": select_items(eligible, pilot, 64), "n128": select_items(eligible, pilot, 128)}
    summaries = {}
    for set_label, records in selected.items():
        rendered = render_prompts(records, args.tokenizer_dir, enable_thinking=args.arm == "on") if args.tokenizer_dir else None
        full = build_math_manifest(rows, receipts, set_name="pilot" if set_label == "pilot" else "test", n=None if set_label == "pilot" else int(set_label[1:]), enable_thinking=args.arm == "on", rendered=rendered)
        path = args.out_dir / f"math_{args.arm}_{set_label}.json"
        write_json(path, full)
        summaries[set_label] = hash_only_manifest(full)
        print(f"{set_label} {full['selected_item_ids_sha256']} {path}")
        if rendered is not None:
            native = build_math_suite_manifest(rows, receipts, set_name="pilot" if set_label == "pilot" else "test", n=None if set_label == "pilot" else int(set_label[1:]), enable_thinking=args.arm == "on", rendered=rendered, output_cap=args.output_cap)
            annotations = build_math_annotations(native, records)
            write_json(args.out_dir / f"math_{args.arm}_{set_label}.suite.json", native)
            write_json(args.out_dir / f"math_{args.arm}_{set_label}.annotations.json", annotations)
    hash_only = {"schema_version": "math_hash_only_bundle.v1", "source_files": receipts, "population": stats, "sets": summaries, "set_hashes": {name: value["selected_item_ids_sha256"] for name, value in summaries.items()}}
    write_json(args.hash_only_out, hash_only)
    print(f"hash_only_sha256 {canonical_json_sha256(hash_only)} {args.hash_only_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
