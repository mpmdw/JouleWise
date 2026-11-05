#!/usr/bin/env python3
"""Deferred desk inventory, conversion, and load/quality/memory/rate screening.

No command installs packages or downloads anything. Only inventory/server-command
are stdlib operations. convert/probe require an approved, pinned Mac venv.
"""
from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path
import resource
import re
import subprocess
import time

from scripts.align_flashnext_common import approved_runtime, inventory, sha256, verify_inventory


def quant_recipe(path, recipe):
    if recipe not in ("q4", "e4_ple4_other8", "e3_ple4_other8"):
        raise ValueError("unknown quantization recipe")
    if path.endswith("mlp.gate"):
        return False
    bits = 8
    if recipe == "q4":
        bits = 4
    elif ".switch_mlp." in path or ".shared_expert." in path or path.endswith("shared_expert_gate"):
        bits = 3 if recipe.startswith("e3_") else 4
    if ".ngram_embedding.shards." in path:
        bits = 4
    return {"bits": bits, "group_size": 32 if ".ngram_embedding.shards." in path else 64, "mode": "affine"}


def has_product_answer(text):
    return re.search(r"(?<![\d.,])\b391\b(?![.,]\d)", text) is not None


def server_command(python, model, port, effort):
    if not Path(python).is_absolute() or not Path(model).is_absolute() or not 1024 <= port <= 65535:
        raise ValueError("absolute venv Python/model and unprivileged valid port required")
    if effort not in ("low", "medium", "xhigh"):
        raise ValueError("unsupported reasoning effort")
    return [str(python), "-m", "mlx_lm.server", "--model", str(model),
            "--host", "127.0.0.1", "--port", str(port), "--decode-concurrency", "1",
            "--prompt-concurrency", "1", "--prefill-step-size", "512",
            "--prompt-cache-size", "1", "--chat-template-args",
            json.dumps({"enable_thinking": True, "reasoning_effort": effort, "preserve_thinking": True}, sort_keys=True)]


def write_new(path, data):
    with Path(path).open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


def convert(args):
    import mlx.core as mx
    from mlx_lm.utils import load, quantize_model, save
    config = json.loads((args.model / "config.json").read_text())
    if config.get("quantization") or config.get("quantization_config") or config.get("model_file"):
        raise ValueError("convert only reviewed original unquantized HF checkpoint; no requantization/custom code")
    if config.get("model_type") != "qwen4_exp":
        raise ValueError("expected qwen4_exp original config")
    if args.destination.exists():
        raise ValueError("destination exists; preserve it")
    # Lazy loading and save's shard donation reduce residency, but are NOT a
    # proof that a 354+ GB BF16 source converts within this Mac's memory.
    model, tokenizer, config = load(str(args.model), lazy=True, return_config=True,
                                    tokenizer_config={"trust_remote_code": False})
    model, config = quantize_model(model, config, 32, 4, mode="affine",
                                  quant_predicate=lambda p, m: quant_recipe(p, args.recipe))
    save(args.destination, args.model, model, tokenizer, config)
    return {"recipe": args.recipe, "peak_mlx_bytes": mx.get_peak_memory(),
            "artifact": {"files": inventory(args.destination)},
            "status": "CONVERTED_REQUIRES_FRESH_PROCESS_QUALITY_AND_IDENTITY_CHECKS"}


def swap_used_mb():
    import re
    raw = subprocess.check_output(["/usr/sbin/sysctl", "vm.swapusage"], text=True)
    match = re.search(r"used\s*=\s*([0-9.]+)M", raw)
    if not match:
        raise ValueError("cannot parse swap usage: " + raw)
    return float(match.group(1))


def probe(args, report):
    import mlx.core as mx
    from mlx_lm import stream_generate
    from mlx_lm.sample_utils import make_sampler
    from mlx_lm.utils import load
    from joulewise.align.apple.endpoint import parse_completion

    def record(name, fn):
        try:
            report["checks"].append({"check": name, "status": "PASS", "detail": fn()})
        except Exception as exc:
            report["checks"].append({"check": name, "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"})

    baseline_swap = swap_used_mb()
    report["device_info"] = mx.device_info()
    report["swap_before_mb"] = baseline_swap
    started = time.perf_counter()
    model, tokenizer = load(str(args.model), tokenizer_config={"trust_remote_code": False})
    model.eval()
    report["load_s"] = time.perf_counter() - started

    def memory():
        peak = mx.get_peak_memory()
        swap = swap_used_mb()
        detail = {"mlx_peak_bytes": peak, "process_maxrss_bytes_macos": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  "swap_used_mb": swap}
        if peak > args.max_peak_gb * 1e9 or swap > baseline_swap:
            raise ValueError("memory admission failed: " + json.dumps(detail))
        return detail

    report["checks"] = []
    # A load already over budget stops the probe before longer allocations.
    report["load_memory"] = memory()
    if sha256(args.nll_text) != args.nll_sha256:
        raise ValueError("NLL corpus sha256 mismatch")
    corpus = tokenizer.encode(args.nll_text.read_text(), add_special_tokens=False)
    if len(corpus) < 2049:
        raise ValueError("frozen SHADE text must provide >=2049 tokens for 2048 scored positions")
    report["nll_text_sha256"] = args.nll_sha256
    report["nll_token_ids"] = corpus[:2049]

    def nll():
        cache = model.make_cache()
        total, count = 0.0, 0
        for start in range(0, 2048, args.chunk):
            stop = min(start + args.chunk, 2048)
            logits = model(mx.array([corpus[start:stop]]), cache=cache).astype(mx.float32)
            targets = mx.array(corpus[start+1:stop+1])[None, :, None]
            losses = mx.logsumexp(logits, axis=-1) - mx.take_along_axis(logits, targets, axis=-1).squeeze(-1)
            total += losses.sum().item()
            count += stop - start
            del logits, losses
        value = total / count
        if not 0 <= value <= 3.0:
            raise AssertionError(f"NLL {value} exceeds 3.0 nats/token")
        return {"nats_per_token": value, "positions": count}
    record("fixed_SHADE_NLL", nll)

    def render(messages, effort, tools=None):
        return tokenizer.apply_chat_template(messages, tools=tools, tokenize=True, add_generation_prompt=True,
                                             enable_thinking=True, reasoning_effort=effort, preserve_thinking=True)

    def generate(prompt, max_tokens, greedy=False):
        ids, texts, last = [], [], None
        mx.random.seed(20261105)
        for part in stream_generate(model, tokenizer, prompt, max_tokens=max_tokens,
                                    prefill_step_size=args.chunk,
                                    sampler=make_sampler(temp=0 if greedy else 1.0, top_p=0.95, top_k=20)):
            last = part
            ids.append(part.token)
            texts.append(part.text)
        if last is None:
            raise AssertionError("no generated response")
        return "".join(texts), ids, {"prompt_tokens": last.prompt_tokens,
                                    "generation_tokens": last.generation_tokens,
                                    "prefill_tok_s": last.prompt_tps, "decode_tok_s": last.generation_tps,
                                    "finish_reason": last.finish_reason, **memory()}

    tools = [{"type": "function", "function": {"name": "engine_product", "description": "Multiply two integers.",
              "parameters": {"type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}, "required": ["a", "b"]}}}]
    for effort in ("low", "medium", "xhigh"):
        for repeat in range(args.repeats):
            def coherence():
                prompt = render([{"role": "user", "content": "Compute 17 times 23. End with the integer answer."}], effort)
                text, ids, rates = generate(prompt, args.decode_tokens, greedy=True)
                visible, hidden, _, flags = parse_completion(text, reasoning_open=True)
                if not has_product_answer(visible) or rates["finish_reason"] == "length":
                    raise AssertionError("coherence/incomplete reasoning: " + json.dumps({"text": text, "rates": rates}))
                return {"text": text, "ids": ids, "rates": rates, "parser_flags": flags}
            record(f"{effort}/coherence_rates/{repeat}", coherence)

        def tool_roundtrip():
            messages = [{"role": "user", "content": "Call engine_product with a=17 and b=23, then report its result."}]
            first = render(messages, effort, tools)
            text, ids, rates = generate(first, args.decode_tokens)
            kwargs = {"reasoning_open": True}
            if "tools" in inspect.signature(parse_completion).parameters:
                kwargs["tools"] = tools
            visible, hidden, calls, flags = parse_completion(text, **kwargs)
            bad_flags = any(f.startswith(("malformed_tool_call", "unsupported_tool_call_format")) for f in flags)
            if len(calls) != 1 or calls[0].name != "engine_product" or bad_flags or rates["finish_reason"] == "length":
                raise AssertionError("XML parser/tool selection failed: " + json.dumps({"text": text, "flags": flags, "rates": rates}))
            arguments = json.loads(calls[0].arguments_json)
            if arguments != {"a": 17, "b": 23} or any(type(v) is not int for v in arguments.values()):
                raise AssertionError("schema-typed tool arguments failed")
            result = str(arguments["a"] * arguments["b"])  # harmless real local function
            content = re.sub(r"<tool_call>.*?</tool_call>", "", visible, flags=re.DOTALL).strip()
            messages += [{"role": "assistant", "content": content, "reasoning_content": hidden,
                          "tool_calls": [{"type": "function", "function": {"name": calls[0].name, "arguments": arguments}}]},
                         {"role": "tool", "content": result}]
            second = render(messages, effort, tools)
            expected = list(first) + ids
            common = next((i for i, (a, b) in enumerate(zip(expected, second)) if a != b), min(len(expected), len(second)))
            rewritten = len(expected) - common
            answer, answer_ids, second_rates = generate(second, args.decode_tokens)
            answer_visible = parse_completion(answer, reasoning_open=True)[0]
            detail = {"tool_response": result, "generated": text, "response": answer,
                      "first_ids": ids, "second_ids": answer_ids, "prefix_rewritten_tokens": rewritten,
                      "first_rates": rates, "second_rates": second_rates, "flags": flags}
            if rewritten or not has_product_answer(answer_visible) or second_rates["finish_reason"] == "length":
                raise AssertionError("tool/history roundtrip failed: " + json.dumps(detail))
            return detail
        record(effort + "/XML_tool_roundtrip", tool_roundtrip)

    def cap_prefill():
        # Synthetic capacity input, no measurement corpus or energy claim.
        cap_ids = (corpus * ((args.context + len(corpus) - 1) // len(corpus)))[:args.context]
        cache = model.make_cache()
        start_time = time.perf_counter()
        for start in range(0, args.context, args.chunk):
            out = model(mx.array([cap_ids[start:start+args.chunk]]), cache=cache)
            mx.eval(out)
            memory()  # stop promptly on peak or swap growth
            del out
        offsets = [int(c.offset) for c in cache if hasattr(c, "offset")]
        if not offsets or any(n != args.context for n in offsets):
            raise AssertionError("context cap not represented by attention caches")
        return {"context_tokens": args.context, "kind": "SYNTHETIC_CAPACITY_ONLY",
                "prefill_tok_s": args.context / (time.perf_counter() - start_time), **memory()}
    record("context_cap_prefill", cap_prefill)
    report["all_checks_pass"] = all(r["status"] == "PASS" for r in report["checks"])
    report["swap_after_mb"] = swap_used_mb()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("inventory", "convert", "probe", "server-command"))
    p.add_argument("--approved-desk", action="store_true")
    p.add_argument("--pins", type=Path)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--artifact-manifest", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--destination", type=Path)
    p.add_argument("--recipe", choices=("q4", "e4_ple4_other8", "e3_ple4_other8"), default="e3_ple4_other8")
    p.add_argument("--nll-text", type=Path)
    p.add_argument("--nll-sha256")
    p.add_argument("--python", type=Path)
    p.add_argument("--port", type=int, default=8091)
    p.add_argument("--effort", choices=("low", "medium", "xhigh"), default="xhigh")
    p.add_argument("--context", type=int, default=40960)
    p.add_argument("--chunk", type=int, default=512)
    p.add_argument("--decode-tokens", type=int, default=4096)
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--max-peak-gb", type=float, default=103.86)
    args = p.parse_args()
    if args.command == "server-command":
        if args.python is None:
            p.error("--python is required")
        print(json.dumps(server_command(args.python, args.model, args.port, args.effort), indent=2))
        return 0
    if not args.output or args.output.exists():
        p.error("a new --output file is required")
    if args.command == "inventory":
        write_new(args.output, {"files": inventory(args.model), "status": "OBSERVED_NOT_AUTHENTICATED"})
        return 0
    if not args.pins or not args.artifact_manifest:
        p.error("--pins and --artifact-manifest are required")
    if args.command == "convert" and not args.destination:
        p.error("convert requires --destination")
    if args.command == "probe" and (not args.nll_text or not args.nll_sha256):
        p.error("probe requires frozen --nll-text and --nll-sha256")
    if min(args.context, args.chunk, args.decode_tokens, args.repeats) < 1 or args.max_peak_gb <= 0:
        p.error("positive sizes/repeats/memory limit required")
    pins = approved_runtime(args.approved_desk, args.pins)
    verify_inventory(args.model, json.loads(args.artifact_manifest.read_text())["files"])
    report = {"status": "DESK_SCREEN_NOT_HARDWARE_OR_WINDOW_QUALIFICATION", "pins": pins,
              "artifact_manifest_sha256": sha256(args.artifact_manifest), "checks": []}
    try:
        if args.command == "convert":
            report.update(convert(args))
            report["all_checks_pass"] = False  # conversion alone never qualifies a model
        else:
            probe(args, report)
    except Exception as exc:
        report["fatal_error"] = f"{type(exc).__name__}: {exc}"
        report["all_checks_pass"] = False
    write_new(args.output, report)
    success = (args.command == "convert" and "fatal_error" not in report) or report["all_checks_pass"]
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
