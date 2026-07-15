#!/usr/bin/env python3
"""Cross-process spike for mlx-lm prompt-cache persistence.

This script deliberately splits the experiment into separate OS processes:
``monolithic`` decodes from a fresh prompt, ``prefill`` writes the prompt cache
after prefill, and ``decode`` loads that cache in a new process before
resuming decode. The top-level ``run`` command invokes those stages with
``subprocess.run([sys.executable, __file__, ...], check=True)`` so Python,
MLX, and mlx-lm process state cannot be shared between prefill and resume.

The resume boundary is intentionally trim-by-1. mlx-lm's ``generate_step``
prefills ``prompt[:-1]`` in bulk and then steps the final prompt token, so a
cache saved after ``max_tokens=0`` has already advanced through the full
prompt. To reproduce a monolithic decode exactly after loading that cache, the
decode process trims one token from the cache and feeds only the last prompt
token. Feeding the last token without that trim double-counts it and changes
the generated tokens.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "~/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit"
CACHE_FILENAME = "prompt_cache.safetensors"
PROMPT_TOKENS_FILENAME = "prompt_tokens.json"
MIN_PROMPT_LEN = 512
MAX_PROMPT_LEN = 2048
MAX_DECODE_TOKENS = 64
KV_SIZE_TOLERANCE_PCT = 2.0


def json_dump(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def json_load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def require_int_list(data: Any, *, name: str) -> list[int]:
    if not isinstance(data, list) or any(
        isinstance(item, bool) or not isinstance(item, int) for item in data
    ):
        raise ValueError(f"{name} must be a list of ints")
    return list(data)


def model_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def validate_model_dir(path: Path) -> None:
    if not path.is_dir():
        raise ValueError(f"model directory does not exist: {path}")
    config_path = path / "config.json"
    if not config_path.is_file():
        raise ValueError(f"model directory is missing config.json: {config_path}")


def validate_prompt_len(prompt_len: int) -> None:
    if prompt_len < MIN_PROMPT_LEN or prompt_len > MAX_PROMPT_LEN:
        raise ValueError(
            f"prompt length must be in [{MIN_PROMPT_LEN}, {MAX_PROMPT_LEN}], got {prompt_len}"
        )


def validate_decode_tokens(decode_tokens: int) -> None:
    if decode_tokens < 1 or decode_tokens > MAX_DECODE_TOKENS:
        raise ValueError(f"decode tokens must be in [1, {MAX_DECODE_TOKENS}], got {decode_tokens}")


def package_version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def version_meta() -> dict[str, str | None]:
    return {
        "mlx_lm_version": package_version("mlx-lm"),
        "mlx_version": package_version("mlx"),
    }


def import_mlx_runtime() -> tuple[Any, Any, Any, Any, Any, Any, Any, Any]:
    import mlx.core as mx
    from mlx_lm.generate import generate_step
    from mlx_lm.models.cache import (
        can_trim_prompt_cache,
        load_prompt_cache,
        make_prompt_cache,
        save_prompt_cache,
        trim_prompt_cache,
    )
    from mlx_lm.utils import load

    return (
        mx,
        load,
        generate_step,
        make_prompt_cache,
        save_prompt_cache,
        load_prompt_cache,
        trim_prompt_cache,
        can_trim_prompt_cache,
    )


def tokenizer_encode(tokenizer: Any, text: str) -> list[int]:
    try:
        tokens = tokenizer.encode(text, add_special_tokens=False)
    except TypeError:
        tokens = tokenizer.encode(text)
    token_ids = [int(token) for token in tokens]
    if not token_ids:
        raise ValueError("tokenizer produced no tokens for the fixed prompt recipe")
    return token_ids


def build_prompt(tokenizer: Any, prompt_len: int) -> list[int]:
    """Build a deterministic prompt of exactly ``prompt_len`` token IDs."""
    validate_prompt_len(prompt_len)
    seed_text = (
        "JouleWise prompt-cache persistence spike. "
        "This deterministic prompt repeats a fixed technical sentence so token "
        "identity can be compared across independent operating-system processes. "
    )
    seed_tokens = tokenizer_encode(tokenizer, seed_text)
    repeats = (prompt_len + len(seed_tokens) - 1) // len(seed_tokens)
    return (seed_tokens * repeats)[:prompt_len]


def cache_offset(prompt_cache: Any) -> int:
    if not prompt_cache:
        raise ValueError("prompt cache is empty")
    offset = getattr(prompt_cache[0], "offset", None)
    if offset is None:
        raise ValueError("prompt cache entry has no offset")
    return int(offset)


def collect_decode_tokens(
    mx: Any,
    generate_step: Any,
    model: Any,
    prompt_ids: list[int],
    prompt_cache: Any,
    max_tokens: int,
) -> list[int]:
    validate_decode_tokens(max_tokens)
    prompt_array = mx.array(prompt_ids)
    tokens: list[int] = []
    for token, _ in generate_step(
        prompt_array,
        model,
        max_tokens=max_tokens,
        prompt_cache=prompt_cache,
    ):
        tokens.append(int(token))
    return tokens


def cmd_monolithic(args: argparse.Namespace) -> int:
    validate_prompt_len(args.prompt_len)
    validate_decode_tokens(args.decode)
    model_dir = model_path(args.model)
    validate_model_dir(model_dir)
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    mx, load, generate_step, make_prompt_cache, *_ = import_mlx_runtime()
    started = time.perf_counter()
    load_started = time.perf_counter()
    model, tokenizer = load(str(model_dir))
    load_s = time.perf_counter() - load_started

    prompt_ids = build_prompt(tokenizer, args.prompt_len)
    prompt_cache = make_prompt_cache(model)
    decode_started = time.perf_counter()
    tokens = collect_decode_tokens(
        mx, generate_step, model, prompt_ids, prompt_cache, args.decode
    )
    decode_s = time.perf_counter() - decode_started

    json_dump(workdir / "mono_tokens.json", {"tokens": tokens})
    json_dump(
        workdir / "mono_meta.json",
        {
            **version_meta(),
            "model": str(model_dir),
            "prompt_len": args.prompt_len,
            "decode_tokens": args.decode,
            "timings": {
                "load_s": load_s,
                "decode_s": decode_s,
                "total_s": time.perf_counter() - started,
            },
        },
    )
    return 0


def cmd_prefill(args: argparse.Namespace) -> int:
    validate_prompt_len(args.prompt_len)
    model_dir = model_path(args.model)
    validate_model_dir(model_dir)
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    cache_path = workdir / CACHE_FILENAME

    (
        mx,
        load,
        generate_step,
        make_prompt_cache,
        save_prompt_cache,
        *_,
    ) = import_mlx_runtime()
    started = time.perf_counter()
    load_started = time.perf_counter()
    model, tokenizer = load(str(model_dir))
    load_s = time.perf_counter() - load_started

    prompt_ids = build_prompt(tokenizer, args.prompt_len)
    prompt_cache = make_prompt_cache(model)
    prompt_array = mx.array(prompt_ids)
    prefill_started = time.perf_counter()
    for _ in generate_step(prompt_array, model, max_tokens=0, prompt_cache=prompt_cache):
        pass
    mx.eval([cache.state for cache in prompt_cache])
    prefill_s = time.perf_counter() - prefill_started
    offset = cache_offset(prompt_cache)
    if offset != len(prompt_ids):
        raise ValueError(f"unexpected prefill offset: {offset}; expected {len(prompt_ids)}")

    save_started = time.perf_counter()
    save_prompt_cache(
        str(cache_path),
        prompt_cache,
        {
            "model": str(model_dir),
            "prompt_len": str(args.prompt_len),
            "offset": str(offset),
        },
    )
    save_s = time.perf_counter() - save_started
    cache_bytes = cache_path.stat().st_size

    json_dump(
        workdir / PROMPT_TOKENS_FILENAME,
        {
            "tokens": prompt_ids,
            "model": str(model_dir),
            "prompt_len": args.prompt_len,
        },
    )
    json_dump(
        workdir / "prefill_meta.json",
        {
            **version_meta(),
            "model": str(model_dir),
            "prompt_len": args.prompt_len,
            "offset": offset,
            "cache_bytes": cache_bytes,
            "timings": {
                "load_s": load_s,
                "prefill_s": prefill_s,
                "save_s": save_s,
                "total_s": time.perf_counter() - started,
            },
        },
    )
    return 0


def cmd_decode(args: argparse.Namespace) -> int:
    validate_decode_tokens(args.decode)
    workdir = Path(args.workdir)
    prompt_payload = json_load(workdir / PROMPT_TOKENS_FILENAME)
    prompt_ids = require_int_list(prompt_payload.get("tokens"), name="prompt tokens")
    prompt_len = prompt_payload.get("prompt_len")
    if isinstance(prompt_len, bool) or not isinstance(prompt_len, int):
        raise ValueError("prompt_tokens.json prompt_len must be an int")
    if len(prompt_ids) != prompt_len:
        raise ValueError(
            f"prompt_tokens.json length mismatch: len(tokens)={len(prompt_ids)} prompt_len={prompt_len}"
        )
    model_from_prompt = prompt_payload.get("model")
    if not isinstance(model_from_prompt, str) or not model_from_prompt:
        raise ValueError("prompt_tokens.json model must be a non-empty string")
    model_dir = model_path(model_from_prompt)
    if args.model is not None and model_path(args.model) != model_dir:
        raise ValueError(
            f"--model does not match persisted prompt model: {model_path(args.model)} != {model_dir}"
        )
    validate_model_dir(model_dir)

    (
        mx,
        load,
        generate_step,
        _make_prompt_cache,
        _save_prompt_cache,
        load_prompt_cache,
        trim_prompt_cache,
        can_trim_prompt_cache,
    ) = import_mlx_runtime()
    started = time.perf_counter()
    load_started = time.perf_counter()
    model, _tokenizer = load(str(model_dir))
    load_s = time.perf_counter() - load_started

    cache_started = time.perf_counter()
    prompt_cache, cache_metadata = load_prompt_cache(
        str(workdir / CACHE_FILENAME), return_metadata=True
    )
    cacheload_s = time.perf_counter() - cache_started
    pre_trim_offset = cache_offset(prompt_cache)
    if pre_trim_offset != len(prompt_ids):
        raise ValueError(
            f"unexpected loaded offset: {pre_trim_offset}; expected {len(prompt_ids)}"
        )
    if not can_trim_prompt_cache(prompt_cache):
        raise ValueError("loaded prompt cache cannot be trimmed")

    trim_started = time.perf_counter()
    # Load-bearing boundary fix: the saved cache already includes the final
    # prompt token, so trim it and feed only that token to match monolithic
    # generation exactly.
    trim_prompt_cache(prompt_cache, 1)
    post_trim_offset = cache_offset(prompt_cache)
    trim_s = time.perf_counter() - trim_started
    if post_trim_offset != len(prompt_ids) - 1:
        raise ValueError(
            f"unexpected post-trim offset: {post_trim_offset}; expected {len(prompt_ids) - 1}"
        )

    decode_started = time.perf_counter()
    tokens = collect_decode_tokens(
        mx,
        generate_step,
        model,
        prompt_ids[-1:],
        prompt_cache,
        args.decode,
    )
    decode_s = time.perf_counter() - decode_started

    json_dump(workdir / "resume_tokens.json", {"tokens": tokens})
    json_dump(
        workdir / "decode_meta.json",
        {
            **version_meta(),
            "model": str(model_dir),
            "prompt_len": prompt_len,
            "decode_tokens": args.decode,
            "cache_metadata": cache_metadata if isinstance(cache_metadata, dict) else None,
            "pre_trim_offset": pre_trim_offset,
            "post_trim_offset": post_trim_offset,
            "timings": {
                "load_s": load_s,
                "cacheload_s": cacheload_s,
                "trim_s": trim_s,
                "decode_s": decode_s,
                "total_s": time.perf_counter() - started,
            },
        },
    )
    return 0


def predict_cache_bytes(model_dir: Path, prompt_len: int) -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from joulewise.kv_size import bytes_per_token, extract_kv_params, prompt_totals

    config_path = model_dir / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError(f"config JSON must be an object: {config_path}")
    params = extract_kv_params(config)
    bytes_per_tok = bytes_per_token(params.n_layers, params.n_kv_heads, params.head_dim)
    return prompt_totals(bytes_per_tok, [prompt_len])[0][1]


def first_divergence(left: list[int], right: list[int]) -> int | None:
    for index, (left_token, right_token) in enumerate(zip(left, right)):
        if left_token != right_token:
            return index
    if len(left) != len(right):
        return min(len(left), len(right))
    return None


def run_stage(command: list[str]) -> float:
    started = time.perf_counter()
    env = os.environ.copy()
    env["PYTHONPATH"] = (
        str(ROOT)
        if not env.get("PYTHONPATH")
        else str(ROOT) + os.pathsep + env["PYTHONPATH"]
    )
    subprocess.run(command, check=True, env=env, cwd=str(ROOT))
    return time.perf_counter() - started


def stage_command(
    stage: str,
    workdir: Path,
    model_dir: Path,
    prompt_len: int,
    decode_tokens_count: int,
) -> list[str]:
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        stage,
        "--workdir",
        str(workdir),
        "--model",
        str(model_dir),
    ]
    if stage in {"monolithic", "prefill"}:
        command.extend(["--prompt-len", str(prompt_len)])
    if stage in {"monolithic", "decode"}:
        command.extend(["--decode", str(decode_tokens_count)])
    return command


def verdict_for(
    tokens_identical: bool,
    cache_pct: float,
    first_bad: int | None,
    *,
    monolithic_emitted_tokens: int,
    resumed_emitted_tokens: int,
    requested_tokens: int,
) -> str:
    cache_ok = abs(cache_pct) < KV_SIZE_TOLERANCE_PCT
    decode_complete = (
        monolithic_emitted_tokens == requested_tokens
        and resumed_emitted_tokens == requested_tokens
    )
    reasons: list[str] = []
    if not tokens_identical:
        reasons.append(f"tokens_diverged_at_{first_bad}")
    if not cache_ok:
        reasons.append(f"cache_size_delta_{cache_pct:.6f}_pct")
    if not decode_complete:
        reasons.append(
            "decode_count_"
            f"mono_{monolithic_emitted_tokens}_"
            f"resume_{resumed_emitted_tokens}_"
            f"requested_{requested_tokens}"
        )
    if tokens_identical and cache_ok and decode_complete:
        return "replay_supported"
    if not tokens_identical or not decode_complete:
        return f"replay_unsupported({','.join(reasons)})"
    return f"partial({','.join(reasons)})"


def assemble_report(
    workdir: Path,
    model_dir: Path,
    prompt_len: int,
    decode_tokens_count: int,
    subprocess_timings: dict[str, float],
) -> dict[str, Any]:
    mono_tokens = require_int_list(json_load(workdir / "mono_tokens.json").get("tokens"), name="mono tokens")
    resume_tokens = require_int_list(
        json_load(workdir / "resume_tokens.json").get("tokens"), name="resume tokens"
    )
    mono_meta = json_load(workdir / "mono_meta.json")
    prefill_meta = json_load(workdir / "prefill_meta.json")
    decode_meta = json_load(workdir / "decode_meta.json")

    cache_bytes_measured = int(prefill_meta["cache_bytes"])
    cache_bytes_predicted = predict_cache_bytes(model_dir, prompt_len)
    cache_bytes_delta = cache_bytes_measured - cache_bytes_predicted
    cache_bytes_pct = (cache_bytes_delta / cache_bytes_predicted) * 100.0
    first_bad = first_divergence(mono_tokens, resume_tokens)
    tokens_identical = first_bad is None
    monolithic_emitted_tokens = len(mono_tokens)
    resumed_emitted_tokens = len(resume_tokens)

    return {
        "model": str(model_dir),
        "prompt_len": prompt_len,
        "decode_tokens": decode_tokens_count,
        "monolithic_emitted_tokens": monolithic_emitted_tokens,
        "resumed_emitted_tokens": resumed_emitted_tokens,
        "mlx_lm_version": mono_meta.get("mlx_lm_version"),
        "mlx_version": mono_meta.get("mlx_version"),
        "cache_bytes_measured": cache_bytes_measured,
        "cache_bytes_predicted": cache_bytes_predicted,
        "cache_bytes_delta": cache_bytes_delta,
        "cache_bytes_pct": cache_bytes_pct,
        "prefill_offset": prefill_meta.get("offset"),
        "resume_pre_trim_offset": decode_meta.get("pre_trim_offset"),
        "resume_post_trim_offset": decode_meta.get("post_trim_offset"),
        "tokens_identical": tokens_identical,
        "first_divergence_index": first_bad,
        "timings": {
            "monolithic": mono_meta.get("timings"),
            "prefill": prefill_meta.get("timings"),
            "decode": decode_meta.get("timings"),
            "subprocess": subprocess_timings,
        },
        "verdict": verdict_for(
            tokens_identical,
            cache_bytes_pct,
            first_bad,
            monolithic_emitted_tokens=monolithic_emitted_tokens,
            resumed_emitted_tokens=resumed_emitted_tokens,
            requested_tokens=decode_tokens_count,
        ),
    }


def cmd_run(args: argparse.Namespace) -> int:
    validate_prompt_len(args.prompt_len)
    validate_decode_tokens(args.decode)
    model_dir = model_path(args.model)
    validate_model_dir(model_dir)

    cleanup = False
    if args.workdir:
        workdir = Path(args.workdir).expanduser().resolve()
        workdir.mkdir(parents=True, exist_ok=True)
    else:
        workdir = Path(tempfile.mkdtemp(prefix="jw_mlx_prompt_cache_"))
        cleanup = not args.keep

    subprocess_timings: dict[str, float] = {}
    try:
        for stage in ("monolithic", "prefill", "decode"):
            command = stage_command(stage, workdir, model_dir, args.prompt_len, args.decode)
            subprocess_timings[stage] = run_stage(command)

        report = assemble_report(workdir, model_dir, args.prompt_len, args.decode, subprocess_timings)
        json_dump(workdir / "spike_report.json", report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    finally:
        if cleanup:
            shutil.rmtree(workdir, ignore_errors=True)


def add_common_model_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"local model directory (default: {DEFAULT_MODEL})")


def add_workdir_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workdir", required=True, help="work directory for stage artifacts")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    monolithic = subparsers.add_parser("monolithic", help="decode from a fresh prompt cache")
    add_workdir_arg(monolithic)
    add_common_model_arg(monolithic)
    monolithic.add_argument("--prompt-len", type=int, default=1024, help="prompt tokens")
    monolithic.add_argument("--decode", type=int, default=64, help="tokens to decode")
    monolithic.set_defaults(func=cmd_monolithic)

    prefill = subparsers.add_parser("prefill", help="prefill and persist prompt cache")
    add_workdir_arg(prefill)
    add_common_model_arg(prefill)
    prefill.add_argument("--prompt-len", type=int, default=1024, help="prompt tokens")
    prefill.set_defaults(func=cmd_prefill)

    decode = subparsers.add_parser("decode", help="load persisted cache and resume decode")
    add_workdir_arg(decode)
    decode.add_argument("--model", help="optional assertion against model path in prompt_tokens.json")
    decode.add_argument("--decode", type=int, default=64, help="tokens to decode")
    decode.set_defaults(func=cmd_decode)

    run = subparsers.add_parser("run", help="orchestrate all stages in fresh subprocesses")
    add_common_model_arg(run)
    run.add_argument("--prompt-len", type=int, default=1024, help="prompt tokens")
    run.add_argument("--decode", type=int, default=64, help="tokens to decode")
    run.add_argument("--workdir", help="work directory; created if needed")
    run.add_argument("--keep", action="store_true", help="keep auto-created temporary workdir")
    run.set_defaults(func=cmd_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except subprocess.CalledProcessError as exc:
        print(f"error: subprocess failed with exit {exc.returncode}: {exc.cmd}", file=sys.stderr)
        return exc.returncode or 1
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
