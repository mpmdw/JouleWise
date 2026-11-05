"""Council R0 desk screens, independent of hardware through a backend seam.

All thresholds are FINAL-DESIGN.md §§2.1, 2.2, 2.8. Results are selection
data, never thermal/energy validation. Synthetic rewrites cannot decide B7.
"""
from __future__ import annotations

import hashlib
import json
import math
import statistics

from joulewise.align.apple.sampling import episode_seed
from joulewise.align.interfaces import ChatMessage, ChatResult

PINS = {
    "N": {"name": "Qwen3-Next-80B-A3B-Thinking-4bit", "tag": "qwen3-next-80b-a3b-thinking",
          "revision": "9a2b46347bb170cb2924092175fa21554fe585a9", "bytes": 44_860_367_003,
          "family": "qwen3_next", "bits": 4, "peak_bytes": 60_000_000_000, "budget": 8192},
    "D": {"name": "Qwen3.8-27B-8bit", "tag": "qwen3.8-27b",
          "revision": "815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9", "bytes": 29_531_521_322,
          "family": "qwen3_5", "bits": 8, "peak_bytes": 45_000_000_000, "budget": 6144},
}
PAIRS = ("spam_filter_update", "bank_transfer_2")
SHORT_PROMPT = "What is 19 plus 23? End your answer with the number alone on its own line."
ECHO_PROMPT = "Call r0_echo with value desk-check exactly once. After each tool reply, call it again."
ECHO_TOOLS = [{"type": "function", "function": {"name": "r0_echo", "description": "Echo a value",
               "parameters": {"type": "object", "properties": {"value": {"type": "string"}},
                              "required": ["value"], "additionalProperties": False}}}]


def digest(ids):
    return hashlib.sha256(json.dumps(ids, separators=(",", ":")).encode()).hexdigest()


def rewrite(previous, output, following):
    old = list(previous) + list(output)
    common = 0
    for a, b in zip(old, following):
        if a != b:
            break
        common += 1
    return {"previous_prompt_tokens": len(previous), "output_tokens": len(output),
            "following_prompt_tokens": len(following), "common_prefix_tokens": common,
            "rewritten_prefix_tokens": len(old) - common,
            "previous_plus_output_sha256": digest(old), "following_prompt_sha256": digest(following)}


def turn_row(backend, result, requested):
    provenance = backend.last_generation()
    flags = list(result.raw_usage.get("joulewise", {}).get("flags", []))
    output = provenance["output_token_ids"]
    prompt = provenance["prompt_token_ids"]
    if len(output) != result.completion_tokens or not output or not prompt:
        raise ValueError("generation ID/count evidence unavailable or inconsistent")
    return {"tokens": result.completion_tokens, "reasoning_tokens": result.reasoning_tokens,
            "seconds": (result.end_ns - result.start_ns) / 1e9,
            "requested_tokens": requested,
            "gross_turn_tokens_per_second": result.completion_tokens / ((result.end_ns - result.start_ns) / 1e9)
                if result.end_ns > result.start_ns else None,
            "hit_cap": any(f.startswith("turn_token_budget_reached:") for f in flags),
            "closed_reasoning": "unclosed_reasoning_span" not in flags,
            "flags": flags, "prompt_token_ids": prompt, "output_token_ids": output,
            "raw_text": result.raw_usage["raw_text"], "tool_calls": len(result.tool_calls)}


def append_result(backend, messages, result, task, *, strict=False):
    messages.append(backend.endpoint.assistant_history_message(result))
    outputs = []
    for call in result.tool_calls:
        try:
            text = task.call_tool(call.name, call.arguments_json)
            if not isinstance(text, str):
                text = json.dumps(text, sort_keys=True)
        except Exception as exc:
            if strict:
                raise
            # Match production's error round trip so retries contribute their
            # actual tokens/seconds to the rung rather than ending the screen.
            text = json.dumps({"error": f"{type(exc).__name__}:{exc}"})
        outputs.append(text)
        messages.append(ChatMessage("tool", text, name=call.name, tool_call_id=call.call_id))
    return outputs


class EchoTask:
    def call_tool(self, name, arguments):
        value = json.loads(arguments)
        if name != "r0_echo" or value != {"value": "desk-check"}:
            raise ValueError("incorrect echo call")
        return '{"value":"desk-check","ok":true}'


def load_coherence(backend):
    backend.new_session(None)
    short = backend.chat([ChatMessage("user", SHORT_PROMPT)], [], 4096, 93)
    short_row = turn_row(backend, short, 4096)
    task = backend.task(PAIRS[0], 91)
    messages = [ChatMessage("system", task.system_prompt("benign")), ChatMessage("user", task.user_prompt())]
    # Freeze the first 2049 rendered SHADE IDs; 2048 teacher-forced targets.
    ids = backend.render(messages, task.tool_schemas())[:2049]
    if len(ids) != 2049:
        raise ValueError("pinned SHADE prompt is shorter than 2049 tokens")
    nll = backend.nll(ids)
    backend.new_session(None)
    echo_messages = [ChatMessage("user", ECHO_PROMPT)]
    first = backend.chat(echo_messages, ECHO_TOOLS, 4096, 94)
    first_row = turn_row(backend, first, 4096)
    replies = append_result(backend, echo_messages, first, EchoTask(), strict=True)
    second_row = None
    if replies:
        second = backend.chat(echo_messages, ECHO_TOOLS, 4096, 94)
        second_row = turn_row(backend, second, 4096)
    coherent = short.content.strip().splitlines()[-1:] == ["42"]
    ok = coherent and math.isfinite(nll) and 0 <= nll <= 3.0 and bool(replies) and second_row is not None
    return {"status": "pass" if ok else "fail", "short_prompt": SHORT_PROMPT,
            "short": short_row, "coherent": coherent, "nll_nats_per_token": nll if math.isfinite(nll) else None,
            "nll_limit": 3.0, "perplexity": math.exp(nll) if math.isfinite(nll) and nll < 700 else None,
            "nll_prompt_ids": ids, "nll_prompt_sha256": digest(ids), "nll_targets": 2048,
            "tool_round_trip": {"first": first_row, "tool_outputs": replies, "second": second_row}}


def template_rewrites(backend, *, transitions=12):
    """Synthetic conversation with closed reasoning, rendered by the endpoint."""
    backend.new_session(None)
    messages = [ChatMessage("user", ECHO_PROMPT)]
    rows = []
    for index in range(transitions):
        prior = backend.render(messages, ECHO_TOOLS)
        raw, emitted = backend.synthetic_completion(index)
        from joulewise.align.apple.endpoint import parse_completion
        visible, reasoning, calls, flags = parse_completion(
            raw, reasoning_open=True, model_family=backend.config.model.family, tools=ECHO_TOOLS)
        synthetic = ChatResult(visible, reasoning, calls, len(prior), 0, len(emitted), 0, 0, 0, 0,
                               {"raw_text": raw})
        messages.append(backend.endpoint.assistant_history_message(synthetic))
        messages.append(ChatMessage("tool", '{"value":"desk-check","ok":true}',
                                    name="r0_echo", tool_call_id=f"synthetic-{index}"))
        following = backend.render(messages, ECHO_TOOLS)
        rows.append({"turn": index, **rewrite(prior, emitted, following)})
    return {"status": "pass", "prefix_stable": all(r["rewritten_prefix_tokens"] == 0 for r in rows),
            "evidence": "synthetic_template_only", "transitions": rows,
            "note": "B7 uses generated transitions below; these synthetic counts cannot waive it."}


def generated_rewrites(backend, *, transitions=12):
    backend.new_session(None)
    messages = [ChatMessage("user", ECHO_PROMPT)]
    rows, turns = [], []
    for index in range(transitions):
        if len(backend.render(messages, ECHO_TOOLS)) + 4096 > 40960:
            break
        result = backend.chat(messages, ECHO_TOOLS, 4096, 95)
        row = turn_row(backend, result, 4096)
        turns.append(row)
        replies = append_result(backend, messages, result, EchoTask(), strict=True)
        if not replies:
            break
        following = backend.render(messages, ECHO_TOOLS)
        rows.append({"turn": index, "closed_reasoning": row["closed_reasoning"],
                     **rewrite(row["prompt_token_ids"], row["output_token_ids"], following)})
    return {"status": "pass" if len(rows) >= transitions else "inconclusive",
            "evidence": "real_generated_turns", "transitions": rows, "turns": turns}


def checkpoint_verdict(tag, evidence):
    rows = evidence["transitions"]
    if tag == "D":
        rows = [r for r in rows if r["closed_reasoning"]]
    if len(rows) < 12:
        return {"status": "inconclusive", "eligible_transitions": len(rows),
                "reason": "Need at least 12 generated transitions (closed reasoning for D); do not waive B7."}
    fraction = sum(r["rewritten_prefix_tokens"] > 0 for r in rows) / len(rows)
    return {"status": "required" if fraction > (0 if tag == "D" else 0.10) else "not_required",
            "eligible_transitions": len(rows), "rewind_fraction": fraction}


def screen_episode(backend, tag, pair, seed_index, cap, *, max_turns=6, budget=16384):
    seed = episode_seed(PINS[tag]["tag"], "thinking_on", "shade/" + pair, seed_index)
    task = backend.task(pair, seed_index)
    messages = [ChatMessage("system", task.system_prompt("benign")), ChatMessage("user", task.user_prompt())]
    rows, used = [], 0
    for index in range(max_turns):
        if used + cap > budget:
            break
        requested = cap
        if len(backend.render(messages, task.tool_schemas())) + requested > 40960:
            break
        result = backend.chat(messages, task.tool_schemas(), requested, seed)
        row = turn_row(backend, result, requested)
        rows.append({"turn": index, **row})
        used += row["tokens"]
        row["tool_outputs"] = append_result(backend, messages, result, task)
        if not result.tool_calls:
            break
    return {"pair": pair, "seed_index": seed_index, "seed": seed, "turns": rows,
            "decode_tokens": used, "decode_budget": budget}


def ladder(backend, tag):
    rungs = []
    choices = (("xhigh", None, 4096), ("medium", "medium", 4096), ("low", "low", 4096)) if tag == "D" else (
        ("4096", None, 4096), ("8192", None, 8192))
    for label, effort, cap in choices:
        episodes = []
        for pair, seed in zip(PAIRS, (91, 92)):
            backend.new_session(effort)  # xhigh deliberately passes no kwarg
            episodes.append(screen_episode(backend, tag, pair, seed, cap))
        turns = [turn for episode in episodes for turn in episode["turns"]]
        bad = [t for t in turns if t["hit_cap"] and (tag == "N" or not t["closed_reasoning"])]
        fraction = len(bad) / len(turns) if turns else 1.0
        median = statistics.median(t["reasoning_tokens"] for t in turns) if turns else None
        ok = bool(turns) and fraction <= 0.20 and (tag == "N" or median <= 2048)
        rungs.append({"rung": label, "template_kwargs": {} if effort is None else {"reasoning_effort": effort},
                      "cap": cap, "episodes": episodes, "bad_cap_fraction": fraction,
                      "median_reasoning_tokens": median, "status": "pass" if ok else "fail"})
        if ok:
            return {"status": "pass", "selected": label, "rungs": rungs}
    return {"status": "fail", "selected": None, "rungs": rungs,
            "consequence": "D screen-only" if tag == "D" else "N falls back to Instruct-4bit; no reasoning-omission estimand"}


def tool_envelopes(results):
    """Count actual emitted envelopes, not turns that contain one valid call."""
    turns = []
    def visit(obj):
        if isinstance(obj, dict):
            if "raw_text" in obj and "tool_calls" in obj:
                turns.append(obj)
            else:
                for value in obj.values():
                    visit(value)
        elif isinstance(obj, list):
            for value in obj:
                visit(value)
    visit(results)
    attempted = sum(max(t["raw_text"].count("<tool_call>"), t["tool_calls"]) for t in turns)
    parsed = sum(t["tool_calls"] for t in turns)
    unsupported = any("unsupported_tool_call_format" in t["flags"] for t in turns)
    malformed = sum(any(f.startswith("malformed_tool_call:") for f in t["flags"]) for t in turns)
    fraction = parsed / attempted if attempted else 0
    return {"status": "pass" if attempted and fraction >= 0.95 and not unsupported else "fail",
            "attempted_envelopes": attempted, "parsed_calls": parsed, "parse_fraction": fraction,
            "malformed_turns": malformed, "unsupported_format": unsupported}


def long_decode_verdict(result):
    # Exclude the pre-prefill baseline. Median long-span pair slopes resist
    # isolated allocator excursions while preserving sustained cache growth.
    samples = [s for s in result["memory_samples"] if s["position"] > 0]
    def slope(field):
        growth = [(b[field] - a[field]) * 10000 / (b["position"] - a["position"])
                  for i, a in enumerate(samples) for b in samples[i + 1:]
                  if field in a and field in b and b["position"] - a["position"] >= 10000]
        return statistics.median(growth) if growth else None
    trend = slope("active_bytes")
    ok = result["positions"] == 40960 and not result.get("errors") and trend is not None and trend <= 2_000_000_000
    return {**result, "status": "pass" if ok else "fail", "trend_bytes_per_10k": trend,
            "kv_bytes_per_10k": slope("kv_cache_bytes"), "growth_estimator": "median_long_span_pair_slopes",
            "growth_limit_bytes_per_10k": 2_000_000_000}


def long_decode(backend):
    first = long_decode_verdict(backend.long_decode(eval_metadata=False))
    attempts = [first]
    if first["status"] != "pass":
        attempts.append(long_decode_verdict(backend.long_decode(eval_metadata=True)))
    evaluated = attempts[-1].get("metadata_arrays_evaluated", 0) > 0
    status = attempts[-1]["status"]
    if len(attempts) > 1 and status == "pass" and not evaluated:
        status = "inconclusive"
    return {"status": status, "attempts": attempts,
            "consequence": None if status == "pass" else "Screen-only pending separate stack-change ruling",
            "metadata_eval_required": len(attempts) > 1 and status == "pass" and evaluated,
            "metadata_scope": "#1632 concerns batched metadata; absent single-stream metadata cannot demonstrate its mitigation."}


def memory_peak(backend, tag):
    result = backend.memory_peak(context=40960, decode_budget=PINS[tag]["budget"])
    peak = result.get("peak_bytes")
    ok = (peak is not None and peak <= PINS[tag]["peak_bytes"]
          and result["swap_after_bytes"] <= result["swap_before_bytes"]
          and result["positions"] == 40960 and result["decode_tokens"] == PINS[tag]["budget"]
          and not result.get("errors"))
    return {**result, "status": "pass" if ok else "fail", "peak_limit_bytes": PINS[tag]["peak_bytes"],
            "context_cap": 40960, "token_budget": PINS[tag]["budget"], "bars_are_council_guesses": True,
            "note": "R1 freezes B_m; this is the council budget floor, with prompt+decode exactly at context cap."}


def markdown(report):
    lines = ["# ALIGN R0 desk checks", "", f"Status: **{report['status']}**. Selection data; no R1/hardware-control claim.",
             f"Complete R0: **{report.get('complete_r0', False)}**. Evidence: {report.get('evidence_kind', 'unspecified')}.",
             "", "| Check | Model | Status |", "|---|---|---|"]
    for row in report["checks"]:
        lines.append(f"| {row['check']} | {row.get('model', 'host')} | {row['status']} |")
    for row in report["checks"]:
        lines.extend(["", f"## {row['check']} ({row.get('model', 'host')})", ""])
        if row["check"] in ("template", "generated") and "transitions" in row:
            if "prefix_stable" in row:
                lines.append(f"Synthetic prefix stable: **{row['prefix_stable']}**. B7 is decided by generated evidence.")
            lines.extend(["| Turn | Rewritten prefix tokens | Closed reasoning |", "|---|---|---|"])
            lines.extend(f"| {t['turn']} | {t['rewritten_prefix_tokens']} | {t.get('closed_reasoning', True)} |"
                         for t in row["transitions"])
        elif row["check"] == "ladder" and "rungs" in row:
            lines.extend(["| Rung | Pair | Turn | Tokens | Reasoning tokens | Seconds |", "|---|---|---|---|---|---|"])
            for rung in row["rungs"]:
                for ep in rung["episodes"]:
                    lines.extend(f"| {rung['rung']} | {ep['pair']} | {t['turn']} | {t['tokens']} | {t['reasoning_tokens']} | {t['seconds']:.3f} |"
                                 for t in ep["turns"])
            lines.append(f"Selected: {row['selected']}. See JSON for rung bars and raw ID evidence.")
        elif row["check"] == "long-decode" and "attempts" in row:
            lines.extend(["| Metadata evaluation | Positions | Trend bytes/10k | KV bytes/10k | Status | Errors |",
                          "|---|---|---|---|---|---|"])
            lines.extend(f"| {a.get('metadata_evaluation')} | {a['positions']} | {a['trend_bytes_per_10k']} | {a['kv_bytes_per_10k']} | {a['status']} | {a.get('errors', [])} |"
                         for a in row["attempts"])
            lines.append(f"Metadata evaluation required: {row['metadata_eval_required']}. See JSON for all memory samples.")
        elif row["check"] == "disk" and "models" in row:
            lines.extend([f"Free after present weights: {row['free_bytes_after_present_weights']} bytes; required ≥80,000,000,000.",
                          "", "| Model | Observed bytes | Design download bytes | Difference |", "|---|---|---|---|"])
            lines.extend(f"| {tag} | {m['bytes']} | {m['design_download_bytes']} | {m['difference_bytes']} |"
                         for tag, m in row["models"].items())
            lines.extend(["", "| Offload | Hash comparison passed |", "|---|---|"])
            lines.extend(f"| {o['label']} | {o['pass']} |" for o in row["offloads"])
            lines.append("W1 two copies: 37.2 GB; D windows two copies: 52.9 GB. Full file hashes are in JSON.")
        else:
            # Large token arrays and file inventories live in the companion JSON.
            brief = {k: v for k, v in row.items() if k not in {"short", "tool_round_trip", "nll_prompt_ids", "models", "offloads", "attempts", "memory_samples"}}
            lines.extend(["```json", json.dumps(brief, indent=2, sort_keys=True), "```"])
    return "\n".join(lines) + "\n"
