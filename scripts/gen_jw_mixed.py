#!/usr/bin/env python3
"""Offline jw_mixed_v1 manifest generator.

The core generator is stdlib-only.  When ``--tokenizer-path`` is supplied this
script imports transformers lazily, so CI can import the module without MLX or
tokenizer dependencies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from joulewise.gensuite import build_jw_mixed_manifest, build_sentinel_manifest
from joulewise.suite import suite_manifest_sha256


TOKENIZER_FILES = ("tokenizer.json", "tokenizer_config.json", "merges.txt", "vocab.json")


def tokenizer_manifest(tokenizer_path: Path) -> list[tuple[str, str]]:
    rows = []
    for name in TOKENIZER_FILES:
        path = tokenizer_path / name
        if path.exists():
            rows.append((name, hashlib.sha256(path.read_bytes()).hexdigest()))
    if not rows:
        raise SystemExit(f"no tokenizer files found under {tokenizer_path}")
    return rows


def load_tokenizer(tokenizer_path: Path) -> Any:
    try:
        from transformers import AutoTokenizer  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "--tokenizer-path requires transformers in the active environment"
        ) from exc
    return AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=["mixed", "sentinel"], default="mixed")
    parser.add_argument("--master-seed", default="jw-mixed-v1")
    parser.add_argument("--tokenizer-path", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--sidecar", default=None)
    parser.add_argument("--items-per-category", type=int, default=6)
    args = parser.parse_args()

    tokenizer_path = Path(args.tokenizer_path).expanduser().resolve()
    out = Path(args.out)
    sidecar = Path(args.sidecar) if args.sidecar else out.with_suffix(".annotations.json")
    tokenizer = load_tokenizer(tokenizer_path)
    manifest_files = tokenizer_manifest(tokenizer_path)
    if args.suite == "mixed":
        manifest = build_jw_mixed_manifest(
            args.master_seed,
            tokenizer,
            tokenizer_manifest=manifest_files,
            sidecar_path=sidecar,
            items_per_category=args.items_per_category,
        )
    else:
        manifest = build_sentinel_manifest(
            args.master_seed,
            tokenizer,
            tokenizer_manifest=manifest_files,
            sidecar_path=sidecar,
        )
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"manifest": str(out), "sidecar": str(sidecar), "sha256": suite_manifest_sha256(manifest)}))


if __name__ == "__main__":
    main()
