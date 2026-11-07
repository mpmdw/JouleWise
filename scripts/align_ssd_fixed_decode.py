#!/usr/bin/env python3
"""Fixed-work greedy decode for the SSD qualification's decode segments.

Run in the measurement venv (mlx 0.31.2 / mlx-lm 0.31.3) with a model that is
on the INTERNAL disk (default: the Qwen3-30B-A3B 4-bit anchor). Loads, warms
up, then decodes exactly --tokens greedy tokens with no EOS stop
(``mlx_lm.generate.generate_step``) and prints one JSON line:

  {"work_start_epoch_s": ..., "work_end_epoch_s": ..., "tokens": N, ...}

stamped around the decode only. ``scripts/align_ssd_qualification.py run
--decode-argv <python> scripts/align_ssd_fixed_decode.py --model <dir>`` calls
it once per decode segment. --dry-run prints the plan and imports nothing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

PROMPT = ("Write a long, detailed technical history of the measurement of electrical energy, "
          "from early calorimetry to modern on-chip power telemetry, with many sections.")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", type=Path, required=True, help="local MLX model directory (internal disk)")
    parser.add_argument("--tokens", type=int, default=4096, help="about 90-120 s on the 30B anchor")
    parser.add_argument("--warmup-tokens", type=int, default=32)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.tokens < 1 or args.warmup_tokens < 1:
        parser.error("token counts must be positive")
    if not args.model.is_absolute():
        parser.error("--model must be an absolute local path")
    if args.dry_run:
        print(json.dumps({"model": str(args.model), "tokens": args.tokens, "warmup_tokens": args.warmup_tokens,
                          "prompt": PROMPT, "sampler": "greedy", "eos_stop": False}, sort_keys=True))
        return 0

    import mlx.core as mx
    from mlx_lm import load
    from mlx_lm.generate import generate_step

    model, tokenizer = load(str(args.model))
    mx.eval(model.parameters())
    ids = tokenizer.encode(PROMPT)
    prompt = mx.array(ids)
    greedy = lambda logprobs: mx.argmax(logprobs, axis=-1)  # noqa: E731
    for _ in generate_step(prompt, model, max_tokens=args.warmup_tokens, sampler=greedy):
        pass
    mx.synchronize()
    count = 0
    start = time.time()
    last = None
    for token, _logprobs in generate_step(prompt, model, max_tokens=args.tokens, sampler=greedy):
        last = token
        count += 1
    if last is not None:
        mx.eval(last)
    mx.synchronize()
    end = time.time()
    print(json.dumps({"work_start_epoch_s": start, "work_end_epoch_s": end, "tokens": count,
                      "prompt_tokens": len(ids), "model": str(args.model)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
