#!/usr/bin/env python3
"""Provisional, local-only calibration-night desk feasibility smoke.

Run from the repository root with the intended MLX Python: python -B smoke.py.
All output stays beside this script. No energy measurement or night capture occurs.
"""

import gc
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).with_name("results.json")
PANEL = ROOT / "configs/model_panels/qwen3_4bit.json"
RUNGS = (512, 2048, 8192, 16384, 32768)
REPS = (1, 2, 3)
OUTPUT_TOKENS = 512
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


def command(argv):
    try:
        proc = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True,
                              timeout=20, check=False)
        return {"argv": argv, "exit_code": proc.returncode,
                "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}
    except Exception as exc:
        return {"argv": argv, "error": f"{type(exc).__name__}: {exc}"}


def load_snapshot():
    consumers = command(["ps", "-axo", "pid,pcpu,comm", "-r"])
    if consumers.get("exit_code") == 0:
        consumers["stdout"] = "\n".join(consumers["stdout"].splitlines()[:9])
    return {"utc": datetime.now(timezone.utc).isoformat(),
            "uptime": command(["uptime"]),
            "top_cpu": consumers}


def save(data):
    temp = OUT.with_suffix(".json.tmp")
    temp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(OUT)


def peak_memory(mx):
    # ru_maxrss is bytes on macOS; it is a process high-water mark.
    return {"max_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "metal_peak_bytes": mx.metal.get_peak_memory(),
            "metal_active_bytes": mx.metal.get_active_memory()}


def prompt_for(tokenizer, length):
    seed = tokenizer.encode("Calibration night pinned smoke.", add_special_tokens=False)
    if not seed:
        raise RuntimeError("empty tokenizer seed")
    prompt = (seed * ((length + len(seed) - 1) // len(seed)))[:length]
    digest = hashlib.sha256(json.dumps(prompt, separators=(",", ":")).encode()).hexdigest()
    return prompt, digest


def generate(mlx_lm, model, tokenizer, prompt, sampler, max_tokens):
    original_eos = getattr(tokenizer, "eos_token_ids", None)
    if original_eos is None:
        raise RuntimeError("tokenizer.eos_token_ids absent")
    tokenizer.eos_token_ids = set()
    try:
        started = time.monotonic()
        first = None
        emitted = 0
        # A new stream starts with empty KV state. Exhaustion releases it.
        for _response in mlx_lm.stream_generate(model, tokenizer, prompt,
                                                 max_tokens=max_tokens, sampler=sampler):
            emitted += 1
            if first is None:
                first = time.monotonic()
        ended = time.monotonic()
    finally:
        tokenizer.eos_token_ids = original_eos
    return {"prefill_to_first_s": first - started if first is not None else None,
            "decode_s": ended - first if first is not None else None,
            "wall_s": ended - started, "emitted": emitted}


def failure_rows(reason):
    return [{"model": model, "L": length, "rep": rep, "success": False,
             "reason": reason, "prefill_s": None, "decode_512_s": None,
             "decode_tokens_per_s": None, "emitted": None,
             "max_rss_bytes": None, "metal_peak_bytes": None}
            for rep in REPS for model in ("qwen3-1p7b", "qwen3-8b") for length in RUNGS]


def budget(data):
    """Conservative lower bound; marker/logger overhead is still unknown."""
    if len(data["rows"]) != len(REPS) * 2 * len(RUNGS) or not all(
            row["success"] for row in data["rows"]):
        return {"status": "unavailable", "reason": "missing successful rung timings"}
    if len(data["sustained"]) != len(REPS) * 2 or not all(
            row["success"] for row in data["sustained"]):
        return {"status": "unavailable", "reason": "missing sustained prefill timings"}
    results = {}
    for model in ("qwen3-1p7b", "qwen3-8b"):
        load = max(row["load_s"] for row in data["load_rows"] if row["model"] == model)
        excess = max(row["excess_wall_s"] for row in data["sustained"] if row["model"] == model)
        upper = {length: max(row["prefill_s"] + row["decode_512_s"]
                             for row in data["rows"] if row["model"] == model
                             and row["L"] == length) for length in RUNGS}
        options = {}
        for label, rungs in (("five", RUNGS),
                             ("drop_16384", (512, 2048, 8192, 32768)),
                             ("drop_16384_then_32768", (512, 2048, 8192))):
            base = 30 + 30 * len(rungs) + 60 + 30
            lower = base + load + excess + sum(upper[length] for length in rungs)
            options[label] = {"rungs": list(rungs), "projected_lower_bound_s": lower,
                              "headroom_to_570_s": 570 - lower,
                              "lower_bound_exceeds_570": lower > 570}
        results[model] = {"load_upper_s": load,
                          "sustained_excess_upper_s": excess,
                          "rung_upper_s": upper, "options": options}
    return {"status": "lower_bounds_only", "models": results,
            "reason": "markers, logger receipts, and full payload close are not timed"}


def main():
    panel_bytes = PANEL.read_bytes()
    panel = json.loads(panel_bytes)
    entries = panel["entries"]
    data = {
        "schema": "calnight-desk-smoke/v1", "status": "preflight",
        "head": command(["git", "rev-parse", "HEAD"]),
        "branch": command(["git", "branch", "--show-current"]),
        "os": command(["sw_vers"]), "python": sys.executable,
        "python_version": platform.python_version(),
        "panel_sha256": hashlib.sha256(panel_bytes).hexdigest(),
        "physical_bytes": command(["sysctl", "-n", "hw.memsize"]),
        "swap_before": command(["sysctl", "vm.swapusage"]),
        "load_at_start": load_snapshot(), "rows": [], "sustained": [],
        "load_rows": [], "errors": [], "budget": {"status": "unavailable"},
        "timing_boundary": "first yielded token ends prefill; decode_512_s follows that boundary",
        "prompt_kind": "provisional repeated token-ID seed, not the final sealed prompt",
        "excluded_operations": ["powermetrics", "ioreg", "KM003C", "night capture"],
    }
    save(data)
    expected = ["qwen3-1p7b", "qwen3-8b"]
    try:
        if [entry["model_id"] for entry in entries] != expected:
            raise RuntimeError("model panel differs from the two admitted models")
        for entry in entries:
            if entry["admission"]["status"] != "admitted":
                raise RuntimeError(f"model not admitted: {entry['model_id']}")
            source = Path(entry["source"])
            if not source.is_dir():
                raise RuntimeError(f"local model absent: {entry['model_id']}")
            tok = source / "tokenizer.json"
            if hashlib.sha256(tok.read_bytes()).hexdigest() != entry["tokenizer_json_sha256"]:
                raise RuntimeError(f"tokenizer hash mismatch: {entry['model_id']}")
            if RUNGS[-1] + OUTPUT_TOKENS > entry["context_window"]:
                raise RuntimeError(f"context window too small: {entry['model_id']}")
        import mlx.core as mx
        import mlx_lm
        data["package_versions"] = {
            name: importlib.metadata.version(name) for name in ("mlx", "mlx-lm")}
        if not callable(getattr(mlx_lm, "make_sampler", None)):
            raise RuntimeError("mlx_lm.make_sampler unavailable")
        if not callable(getattr(mlx_lm, "stream_generate", None)):
            raise RuntimeError("mlx_lm.stream_generate unavailable")
        for name in ("get_peak_memory", "get_active_memory"):
            if not callable(getattr(mx.metal, name, None)):
                raise RuntimeError(f"mx.metal.{name} unavailable")
        data["status"] = "running"
        save(data)
        for rep in REPS:
            for entry in entries:
                model_id = entry["model_id"]
                source = Path(entry["source"])
                before_load = load_snapshot()
                started = time.monotonic()
                model, tokenizer = mlx_lm.load(str(source))
                load_s = time.monotonic() - started
                after_load = load_snapshot()
                data["load_rows"].append({"rep": rep, "model": model_id,
                                          "load_s": load_s, "before": before_load,
                                          "after": after_load, **peak_memory(mx)})
                save(data)
                sampler = mlx_lm.make_sampler(temp=0.0)
                for length in RUNGS:
                    row = {"rep": rep, "model": model_id, "L": length,
                           "success": False, "reason": None,
                           "prefill_s": None, "decode_512_s": None,
                           "decode_tokens_per_s": None, "emitted": None,
                           "max_rss_bytes": None, "metal_peak_bytes": None}
                    try:
                        prompt, digest = prompt_for(tokenizer, length)
                        row["prompt_sha256"] = digest
                        row["before"] = load_snapshot()
                        timing = generate(mlx_lm, model, tokenizer, prompt,
                                          sampler, OUTPUT_TOKENS)
                        row["after"] = load_snapshot()
                        row.update({"prefill_s": timing["prefill_to_first_s"],
                                    "decode_512_s": timing["decode_s"],
                                    "emitted": timing["emitted"], **peak_memory(mx)})
                        if timing["emitted"] != OUTPUT_TOKENS:
                            raise RuntimeError(f"emitted {timing['emitted']}, expected 512")
                        if not timing["decode_s"] or timing["decode_s"] <= 0:
                            raise RuntimeError("decode duration unavailable")
                        row["decode_tokens_per_s"] = OUTPUT_TOKENS / timing["decode_s"]
                        row["success"] = True
                    except Exception as exc:
                        row["reason"] = f"{type(exc).__name__}: {exc}"
                        data["errors"].append(row["reason"])
                    data["rows"].append(row)
                    save(data)
                    if not row["success"]:
                        raise RuntimeError(f"rung failed: {model_id} rep={rep} L={length}")
                prompt, digest = prompt_for(tokenizer, 8192)
                sustained = {"rep": rep, "model": model_id, "L": 8192,
                             "prompt_sha256": digest, "repeats": 0,
                             "active_prefill_s": 0.0, "wall_s": 0.0,
                             "one_token_tail_s": 0.0, "success": False,
                             "before": load_snapshot()}
                wall_start = time.monotonic()
                while sustained["active_prefill_s"] < 60.0:
                    timing = generate(mlx_lm, model, tokenizer, prompt, sampler, 1)
                    if timing["emitted"] != 1:
                        raise RuntimeError(f"sustained prefill emitted {timing['emitted']}")
                    sustained["repeats"] += 1
                    sustained["active_prefill_s"] += timing["prefill_to_first_s"]
                    sustained["one_token_tail_s"] += timing["decode_s"]
                    gc.collect()
                sustained["wall_s"] = time.monotonic() - wall_start
                sustained["excess_wall_s"] = sustained["wall_s"] - sustained["active_prefill_s"]
                sustained["after"] = load_snapshot()
                sustained.update(peak_memory(mx))
                sustained["success"] = True
                data["sustained"].append(sustained)
                save(data)
                del model, tokenizer
                gc.collect()
        data["budget"] = budget(data)
        data["status"] = "complete"
    except Exception as exc:
        reason = f"{type(exc).__name__}: {exc}"
        data["errors"].append(reason)
        present = {(row["rep"], row["model"], row["L"]) for row in data["rows"]}
        data["rows"].extend(row for row in failure_rows("not run after: " + reason)
                            if (row["rep"], row["model"], row["L"]) not in present)
        if not present:
            for row in data["rows"]:
                row["reason"] = "preflight: " + reason
        data["budget"] = budget(data)
        data["status"] = "failed"
    finally:
        data["swap_after"] = command(["sysctl", "vm.swapusage"])
        data["load_at_end"] = load_snapshot()
        save(data)
    return 0 if data["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
