#!/usr/bin/env python3
"""Local-only fixed-token replay; --dry-run uses tiny synthetic NumPy weights."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.interp_energy.forced_decode import (  # noqa: E402
    MLXBackend, NumpyBackend, replay, token_ids, weight_file_identity,
)


def _read_tokens(path: Path) -> list[int]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("token file must be a JSON array of integer IDs")
    return token_ids(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="synthetic NumPy replay; no MLX or model files")
    parser.add_argument("--model", type=Path, help="existing local mlx-lm safetensors directory; never a hub ID")
    prompt = parser.add_mutually_exclusive_group()
    prompt.add_argument("--prompt", help="raw text, encoded without added special tokens or chat template")
    prompt.add_argument("--prompt-tokens", type=Path, help="JSON array of exact prompt IDs (preferred for paired arms)")
    parser.add_argument("--tokens", type=Path, help="JSON array of FIXED continuation IDs, including any EOS")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--prefill-chunk-size", type=int, default=512)
    parser.add_argument("--output", type=Path, help="new JSONL file (exclusive creation); default stdout")
    args = parser.parse_args(argv)
    if args.dry_run and (args.model is not None or args.prompt is not None):
        parser.error("--dry-run takes synthetic weights and prompt IDs; use --prompt-tokens to override the prompt")
    if not args.dry_run and (args.model is None or args.tokens is None or (
        args.prompt is None and args.prompt_tokens is None
    )):
        parser.error("native replay requires --model, --tokens and --prompt or --prompt-tokens")
    try:
        forced = _read_tokens(args.tokens) if args.tokens else [5, 4, 0, 8]
        prompt_ids = _read_tokens(args.prompt_tokens) if args.prompt_tokens else None
        if args.dry_run:
            from joulewise.interp_energy.reference import NumpyReferenceModel
            model = NumpyReferenceModel()
            backend = NumpyBackend()
            vocab_size = model.vocab_size
            weights = {"scheme": "synthetic-numpy-parameter-manifest-v1", "sha256": model.weights_sha256()}
            prompt_ids = prompt_ids if prompt_ids is not None else [1, 2, 3]
            config_sha = None
        else:
            # Resolve only a user-supplied existing local path. Offline flags and
            # tokenizer local_files_only also prohibit fallback to a hub fetch.
            model_dir = args.model.resolve(strict=True)
            if not model_dir.is_dir():
                raise ValueError("--model must be an existing local directory")
            weights = weight_file_identity(model_dir)
            config_sha = hashlib.sha256((model_dir / "config.json").read_bytes()).hexdigest()
            os.environ["HF_HUB_OFFLINE"] = "1"
            os.environ["TRANSFORMERS_OFFLINE"] = "1"
            from mlx_lm.utils import load
            model, tokenizer, config = load(
                str(model_dir), tokenizer_config={"local_files_only": True}, return_config=True,
            )
            backend = MLXBackend()
            model_config = config.get("text_config", config)
            vocab_size = model_config["vocab_size"]
            if prompt_ids is None:
                prompt_ids = token_ids(tokenizer.encode(args.prompt, add_special_tokens=False), "prompt")
        result = replay(
            model, prompt_ids, forced, backend=backend, vocab_size=vocab_size,
            model_weights_sha256=weights["sha256"], top_k=args.top_k,
            prefill_chunk_size=args.prefill_chunk_size,
        )
        result.metadata.update({"dry_run": args.dry_run, "weight_identity": weights,
                                "weights_identity_source": weights["scheme"],
                                "model_config_sha256": config_sha})
        if args.output is None:
            result.write_jsonl(sys.stdout)
        else:
            with args.output.open("x", encoding="utf-8") as stream:
                result.write_jsonl(stream)
        return 0
    except (ImportError, OSError, ValueError, KeyError, RuntimeError) as exc:
        print(json.dumps({"status": "error", "error_type": type(exc).__name__, "message": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
