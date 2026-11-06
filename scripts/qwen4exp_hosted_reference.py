#!/usr/bin/env python3
"""Hosted-reference logprob comparison for the qwen4_exp MLX port (GOAL item 7).

Three steps, only the second touches the network, and only with ``--live``:

  plan     render the fixed prompts (configs/qwen4_exp_port/hosted_reference_prompts.json)
           with the official chat template, build the exact request bodies for a
           provider, and estimate tokens and cost. No network. Default command.
  collect  send them. DRY RUN unless ``--live`` is given; refuses without the
           provider's API key in the environment (never read from code or argv),
           and refuses when the estimate exceeds ``--max-cost-usd``. Writes
           normalized traces (JSONL); the Authorization header is never stored.
  compare  offline: score each hosted greedy completion teacher-forced through
           a local adapter (mlx / scripted / module:callable, as in
           qwen4exp_e2e_eval.py) and report top-1 agreement, hosted-token rank,
           top-k overlap and a bucketed KL on the first N tokens, against the
           quantization profile's tolerance.

Why teacher forcing: the hosted model's greedy path is a fixed token sequence.
Scoring that exact sequence locally gives a distribution at every position
conditioned on the same prefix, so the comparison does not stop at the first
divergence of two free-running greedy decodes.

Bucketed KL: providers return only the top-k (k <= 5 on Alibaba) logprobs. We
compare P_hosted and P_local on the buckets {each hosted top-k token} + {all
other tokens}. By the data-processing inequality this is a LOWER bound on the
full KL, so passing it is necessary, not sufficient; top-1 agreement and rank
carry the rest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from scripts import qwen4exp_e2e_eval as e2e
except ImportError:  # run as a file from outside the repo root
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts import qwen4exp_e2e_eval as e2e

PROMPTS_PATH = e2e.REPO_ROOT / "configs" / "qwen4_exp_port" / "hosted_reference_prompts.json"
TRACE_SCHEMA = "qwen4exp-hosted-trace/v1"


@dataclass(frozen=True)
class Provider:
    """One hosted endpoint, as researched on 2026-11-05 (see e2e_validation.md)."""

    name: str
    base_url: str
    api_key_env: str
    model: str
    route: str  # "chat" (messages) or "completions" (raw rendered prompt)
    weights: str
    weight_identical: bool
    precision: str
    logprobs: str
    max_top_logprobs: int
    usd_per_m_input: float
    usd_per_m_output: float
    thinking_off: str
    extra_body: Mapping[str, Any] = field(default_factory=dict)
    notes: str = ""


# Deterministic decoding for every route: greedy, every penalty neutral.
# DashScope defaults presence_penalty to 1.5 for Qwen3.8 non-thinking mode,
# so the neutral values are sent explicitly, never left to provider defaults.
NEUTRAL_SAMPLING = {"temperature": 0.0, "top_p": 1.0, "presence_penalty": 0.0, "frequency_penalty": 0.0}

PROVIDERS: dict[str, Provider] = {
    "featherless": Provider(
        name="featherless", base_url="https://api.featherless.ai/v1", api_key_env="FEATHERLESS_API_KEY",
        model="Qwen/Qwen3.8-Flash-Next", route="completions",
        weights="official open weights Qwen/Qwen3.8-Flash-Next (the only Hugging Face Inference Provider listed)",
        weight_identical=True, precision="FP8 (provider model page)",
        logprobs="not documented: /v1/completions example shows logprobs: null; collect probes it",
        max_top_logprobs=5, usd_per_m_input=0.15, usd_per_m_output=0.50,
        thinking_off="raw /v1/completions prompt rendered locally with enable_thinking=False "
                     "(chat route would use chat_template_kwargs)",
        extra_body={"repetition_penalty": 1.0},
        notes="seed documented as 'not reliable, as we use multiple servers'; greedy repeats measure it"),
    "dashscope-intl": Provider(
        name="dashscope-intl", base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        api_key_env="DASHSCOPE_API_KEY", model="qwen3.8-flash", route="chat",
        weights="production Qwen3.8-Flash, 'based on' Flash-Next with 1M context and built-in tools; "
                "NOT shown to be weight-identical to the open checkpoint",
        weight_identical=False, precision="not stated",
        logprobs="logprobs + top_logprobs in [0, 5] documented for listed families (qwen3.8-flash not "
                 "named; 'only Qwen3 non-thinking'); collect probes it",
        max_top_logprobs=5, usd_per_m_input=0.15, usd_per_m_output=0.47,
        thinking_off="top-level enable_thinking=false (Qwen Cloud form, not chat_template_kwargs)",
        extra_body={"enable_thinking": False}),
    "openrouter-alibaba": Provider(
        name="openrouter-alibaba", base_url="https://openrouter.ai/api/v1", api_key_env="OPENROUTER_API_KEY",
        model="qwen/qwen3.8-flash", route="chat",
        weights="same production Qwen3.8-Flash as dashscope-intl (Alibaba endpoints only)",
        weight_identical=False, precision="'unknown' in OpenRouter endpoint metadata",
        logprobs="logprobs and top_logprobs listed in supported_parameters for both Alibaba endpoints",
        max_top_logprobs=5, usd_per_m_input=0.15, usd_per_m_output=0.47,
        thinking_off="reasoning.enabled=false (OpenRouter unified reasoning parameter)",
        extra_body={"reasoning": {"enabled": False},
                    "provider": {"only": ["alibaba"], "allow_fallbacks": False, "require_parameters": True}},
        notes="require_parameters makes OpenRouter refuse routes that would drop logprobs"),
    "requesty-tensorx": Provider(
        name="requesty-tensorx", base_url="https://router.requesty.ai/v1", api_key_env="REQUESTY_API_KEY",
        model="tensorx/qwen3.8-flash-next", route="chat",
        weights="open weights served by TensorX (EU), per the Requesty listing", weight_identical=True,
        precision="not stated", logprobs="not documented; collect probes it", max_top_logprobs=5,
        usd_per_m_input=0.20, usd_per_m_output=0.50,
        thinking_off="chat_template_kwargs.enable_thinking=false (vLLM/SGLang convention; unverified here)",
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        notes="pay-as-you-go adds 5 %"),
    "vllm-selfhost": Provider(
        name="vllm-selfhost", base_url="http://127.0.0.1:8000/v1", api_key_env="VLLM_API_KEY",
        model="Qwen/Qwen3.8-Flash-Next", route="completions",
        weights="whatever checkpoint the server loads; use the official BF16 repo for a gold reference",
        weight_identical=True, precision="as served (BF16 recommended; no MTP, --kv-cache-dtype auto)",
        logprobs="vLLM: completion logprobs (<= --max-logprobs, default 20), prompt_logprobs, token ids",
        max_top_logprobs=20, usd_per_m_input=0.0, usd_per_m_output=0.0,
        thinking_off="raw prompt rendered locally with enable_thinking=False",
        extra_body={"repetition_penalty": 1.0, "return_tokens_as_token_ids": True,
                    "skip_special_tokens": False},
        notes="rented-GPU option (8 x 80 GB for BF16); the only route with prompt logprobs"),
}


# --------------------------------------------------------------------------
# Prompts and requests
# --------------------------------------------------------------------------

def load_prompts(path: Path = PROMPTS_PATH, items_path: Path = e2e.ITEMS_PATH) -> dict[str, Any]:
    raw = path.read_bytes()
    spec = json.loads(raw)
    if spec.get("schema") != "qwen4exp-hosted-prompts/v1":
        raise SystemExit("unexpected prompts schema")
    texts = {}
    if any("context_from" in p for p in spec["prompts"]):
        texts = {entry["id"]: entry["text"] for entry in e2e.load_items(items_path)["nll"]}
    for prompt in spec["prompts"]:
        if "context_from" in prompt:
            context = texts[prompt["context_from"]]
            prompt["messages"] = [dict(m, content=m["content"].replace("{context}", context))
                                  for m in prompt["messages"]]
    spec["_file_sha256"] = hashlib.sha256(raw).hexdigest()
    return spec


def build_requests(provider: Provider, prompts: Mapping[str, Any], template: e2e.ChatTemplate,
                   *, max_new_tokens: int | None = None, top_logprobs: int | None = None) -> list[dict[str, Any]]:
    max_new = max_new_tokens or prompts["max_new_tokens"]
    k = min(top_logprobs or prompts["top_logprobs"], provider.max_top_logprobs)
    requests = []
    for prompt in prompts["prompts"]:
        rendered = template.render(prompt["messages"], prompt.get("tools"), add_generation_prompt=True,
                                   enable_thinking=False)
        if provider.route == "completions":
            body: dict[str, Any] = {"model": provider.model, "prompt": rendered, "max_tokens": max_new,
                                    "logprobs": k, "echo": False, "n": 1, **NEUTRAL_SAMPLING,
                                    "stop_token_ids": list(e2e.EOS_IDS)}
            if provider.name == "vllm-selfhost":
                body["prompt_logprobs"] = k
            path = "/completions"
        else:
            body = {"model": provider.model, "messages": prompt["messages"], "max_tokens": max_new,
                    "logprobs": True, "top_logprobs": k, "n": 1, "stream": False, **NEUTRAL_SAMPLING}
            if prompt.get("tools"):
                body["tools"] = prompt["tools"]
            path = "/chat/completions"
        body.update(provider.extra_body)
        canonical = json.dumps(body, sort_keys=True, ensure_ascii=False)
        requests.append({"prompt_id": prompt["id"], "url": provider.base_url.rstrip("/") + path, "body": body,
                         "request_sha256": e2e.sha256_text(canonical),
                         "rendered_prompt": rendered, "rendered_prompt_sha256": e2e.sha256_text(rendered),
                         "top_logprobs": k, "max_new_tokens": max_new})
    return requests


def estimate(requests: Sequence[Mapping[str, Any]], provider: Provider, repeats: int,
             adapter: Any | None = None) -> dict[str, Any]:
    """Token and cost estimate. Exact prompt tokens with an adapter; otherwise
    chars/3 (conservative for English, close for CJK)."""
    prompt_tokens = 0
    for request in requests:
        text = request["rendered_prompt"]
        prompt_tokens += len(adapter.encode(text)) if adapter is not None else math.ceil(len(text) / 3)
    output_tokens = sum(r["max_new_tokens"] for r in requests)
    usd = repeats * (prompt_tokens * provider.usd_per_m_input + output_tokens * provider.usd_per_m_output) / 1e6
    return {"requests": len(requests) * repeats, "prompt_tokens": prompt_tokens * repeats,
            "max_output_tokens": output_tokens * repeats, "usd_upper_bound": round(usd, 6),
            "token_count_method": "adapter" if adapter is not None else "chars/3"}


# --------------------------------------------------------------------------
# Response normalization
# --------------------------------------------------------------------------

def _token_id_from_vllm(token: str | None) -> int | None:
    if isinstance(token, str) and token.startswith("token_id:"):
        try:
            return int(token.split(":", 1)[1])
        except ValueError:
            return None
    return None


def normalize_response(provider: Provider, request: Mapping[str, Any], response: Mapping[str, Any],
                       repeat: int) -> dict[str, Any]:
    """Map a chat or legacy-completions response to one trace record."""
    flags: list[str] = []
    choice = (response.get("choices") or [{}])[0]
    tokens: list[dict[str, Any]] = []
    if provider.route == "chat":
        message = choice.get("message") or {}
        text = message.get("content") or ""
        if message.get("reasoning_content") or message.get("reasoning"):
            flags.append("hosted_reasoning_present_with_thinking_off")
        if message.get("tool_calls"):
            flags.append("hosted_parsed_tool_calls")  # server-side parser consumed the XML
        content = (choice.get("logprobs") or {}).get("content")
        if content:
            for entry in content:
                tokens.append({"token": entry.get("token"), "bytes": entry.get("bytes"),
                               "token_id": None, "logprob": entry.get("logprob"),
                               "top": [{"token": t.get("token"), "bytes": t.get("bytes"), "token_id": None,
                                        "logprob": t.get("logprob")} for t in entry.get("top_logprobs") or ()]})
        else:
            flags.append("logprobs_unavailable")
    else:
        text = choice.get("text") or ""
        logprobs = choice.get("logprobs")
        if logprobs and logprobs.get("tokens"):
            tops = logprobs.get("top_logprobs") or [None] * len(logprobs["tokens"])
            for token, lp, top in zip(logprobs["tokens"], logprobs.get("token_logprobs") or (), tops):
                tokens.append({"token": token, "bytes": None, "token_id": _token_id_from_vllm(token),
                               "logprob": lp,
                               "top": [{"token": t, "bytes": None, "token_id": _token_id_from_vllm(t), "logprob": v}
                                       for t, v in (top or {}).items()]})
        else:
            flags.append("logprobs_unavailable")
    usage = response.get("usage") or {}
    return {
        "schema": TRACE_SCHEMA, "provider": provider.name, "model_requested": provider.model,
        "model_reported": response.get("model"), "prompt_id": request["prompt_id"], "repeat": repeat,
        "request_sha256": request["request_sha256"], "rendered_prompt_sha256": request["rendered_prompt_sha256"],
        "route": provider.route, "response_id": response.get("id"),
        "response_sha256": e2e.sha256_text(json.dumps(response, sort_keys=True, ensure_ascii=False)),
        "text": text, "finish_reason": choice.get("finish_reason"), "usage": usage,
        "prompt_tokens_reported": usage.get("prompt_tokens"), "tokens": tokens,
        "prompt_logprobs": choice.get("prompt_logprobs"), "flags": flags,
        "weight_identical": provider.weight_identical,
    }


# --------------------------------------------------------------------------
# Live collection (paid; guarded)
# --------------------------------------------------------------------------

class CollectRefused(RuntimeError):
    pass


def post_json(url: str, body: Mapping[str, Any], api_key: str | None, timeout: float) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "joulewise-qwen4exp-reference/1"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - provider URL from table
        return json.loads(response.read().decode("utf-8"))


def collect(provider: Provider, requests: Sequence[Mapping[str, Any]], *, repeats: int, live: bool,
            max_cost_usd: float, cost: Mapping[str, Any], out: Path | None, timeout: float = 120.0,
            env: Mapping[str, str] | None = None, poster=post_json, log=print) -> list[dict[str, Any]]:
    """Send each request ``repeats`` times. Without ``live`` nothing is sent.
    A failed request is recorded and never retried (a paid call may have run)."""
    env = os.environ if env is None else env
    if not live:
        log(f"DRY RUN: {cost['requests']} requests to {provider.base_url} (not sent); "
            f"estimate <= ${cost['usd_upper_bound']:.4f}. Add --live to send.")
        return []
    if cost["usd_upper_bound"] > max_cost_usd:
        raise CollectRefused(f"estimate ${cost['usd_upper_bound']:.4f} exceeds --max-cost-usd {max_cost_usd}")
    api_key = env.get(provider.api_key_env)
    if not api_key and provider.name != "vllm-selfhost":
        raise CollectRefused(f"set {provider.api_key_env} in the environment (keys are never taken from argv/code)")
    records = []
    handle = out.open("a", encoding="utf-8") if out else None
    try:
        for repeat in range(repeats):
            for request in requests:
                started = time.time()
                try:
                    response = poster(request["url"], request["body"], api_key, timeout)
                    record = normalize_response(provider, request, response, repeat)
                except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
                    record = {"schema": TRACE_SCHEMA, "provider": provider.name, "prompt_id": request["prompt_id"],
                              "repeat": repeat, "request_sha256": request["request_sha256"],
                              "error": f"{type(exc).__name__}: {exc}", "flags": ["request_failed"]}
                record["seconds"] = round(time.time() - started, 3)
                records.append(record)
                if handle:
                    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                    handle.flush()
                log(f"{provider.name} {request['prompt_id']} r{repeat}: "
                    f"{'error' if 'error' in record else str(len(record['tokens'])) + ' logprob tokens'}")
    finally:
        if handle:
            handle.close()
    return records


# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------

class TokenMapper:
    """Hosted token -> local id: vLLM token ids, else exact bytes, else the
    UTF-8 of the token string; built lazily from the adapter's vocabulary."""

    def __init__(self, adapter: Any) -> None:
        self.adapter = adapter
        self._reverse: dict[bytes, int] | None = None

    def _lookup(self, data: bytes) -> int | None:
        direct = e2e.require(self.adapter, "token_id_for_bytes")
        if direct is not None:
            return direct(data)
        if self._reverse is None:
            token_bytes = e2e.require(self.adapter, "token_bytes")
            if token_bytes is None:
                self._reverse = {}
            else:
                self._reverse = {}
                for token_id in range(int(getattr(self.adapter, "vocab_size", e2e.VOCAB_SIZE))):
                    try:
                        self._reverse.setdefault(token_bytes(token_id), token_id)
                    except (KeyError, ValueError, TypeError, IndexError):
                        continue
        return self._reverse.get(data)

    def map(self, entry: Mapping[str, Any]) -> int | None:
        if entry.get("token_id") is not None:
            return int(entry["token_id"])
        if entry.get("bytes"):
            found = self._lookup(bytes(entry["bytes"]))
            if found is not None:
                return found
        token = entry.get("token")
        if isinstance(token, str):
            if token.startswith("bytes:"):  # vLLM partial UTF-8 form, e.g. bytes:\xe4\xb8
                try:
                    return self._lookup(token[len("bytes:"):].encode("latin-1").decode("unicode_escape").encode("latin-1"))
                except (UnicodeError, ValueError):
                    return None
            return self._lookup(token.encode("utf-8"))
        return None


def bucketed_kl(hosted: Sequence[tuple[int, float]], local: Mapping[int, float]) -> float | None:
    """KL(P_hosted || P_local) over {hosted top-k ids} + {rest}; a lower bound
    on the full-vocabulary KL (data-processing inequality)."""
    if not hosted or any(token not in local for token, _ in hosted):
        return None
    p = [math.exp(lp) for _, lp in hosted]
    q = [math.exp(local[token]) for token, _ in hosted]
    p_rest, q_rest = max(0.0, 1.0 - sum(p)), max(1e-12, 1.0 - sum(q))
    kl = sum(pi * (math.log(pi) - math.log(max(qi, 1e-30))) for pi, qi in zip(p, q) if pi > 0)
    if p_rest > 1e-12:
        kl += p_rest * (math.log(p_rest) - math.log(q_rest))
    return max(kl, 0.0)


def compare_trace(trace: Mapping[str, Any], adapter: Any, mapper: TokenMapper, rendered_prompt: str,
                  *, positions: int, top_k: int) -> dict[str, Any]:
    flags = list(trace.get("flags", ()))
    prompt_ids = adapter.encode(rendered_prompt)
    reported = trace.get("prompt_tokens_reported")
    if reported is not None and reported != len(prompt_ids):
        flags.append(f"prompt_token_count_mismatch:{reported}!={len(prompt_ids)}")
    entries = trace.get("tokens") or []
    has_logprobs = bool(entries)
    if has_logprobs:
        ids = [mapper.map(entry) for entry in entries]
        if any(i is None for i in ids):
            flags.append("unmappable_hosted_tokens")
            cut = ids.index(None)
            entries, ids = entries[:cut], ids[:cut]
    else:
        ids = adapter.encode(trace.get("text") or "")
        flags.append("retokenized_hosted_text")
    entries, ids = entries[:positions], ids[:positions]
    if not ids:
        return {"prompt_id": trace["prompt_id"], "positions": 0, "flags": flags + ["no_positions"]}
    queries = None
    if has_logprobs:
        queries = []
        for entry in entries:
            wanted = [mapper.map(t) for t in entry.get("top") or ()]
            queries.append([i for i in wanted if i is not None])
    scored = adapter.score(prompt_ids, ids, top_k=top_k, query_ids=queries)
    top1 = rank5 = 0
    overlaps, kls, dlps = [], [], []
    for index, token in enumerate(ids):
        top1 += int(scored.argmax_ids[index] == token)
        local_top = [t for t, _ in (scored.top_logprobs or [[]] * len(ids))[index]]
        rank5 += int(token in local_top[:5])
        if has_logprobs:
            hosted_top = [(mapper.map(t), t["logprob"]) for t in entries[index].get("top") or ()
                          if t.get("logprob") is not None]
            hosted_top = [(i, lp) for i, lp in hosted_top if i is not None]
            k = min(len(hosted_top), top_k)
            if k:
                overlaps.append(len({i for i, _ in hosted_top[:k]} & set(local_top[:k])) / k)
            local = dict(scored.query_logprobs[index]) if scored.query_logprobs else {}
            local.setdefault(token, scored.token_logprobs[index])
            kl = bucketed_kl(hosted_top, local)
            if kl is not None:
                kls.append(kl)
            if entries[index].get("logprob") is not None:
                dlps.append(abs(scored.token_logprobs[index] - entries[index]["logprob"]))
    n = len(ids)
    return {
        "prompt_id": trace["prompt_id"], "repeat": trace.get("repeat"), "positions": n,
        "top1_agreement": top1 / n, "hosted_token_in_local_top5": rank5 / n,
        "local_nll_of_hosted_path": -sum(scored.token_logprobs) / n,
        "topk_overlap": sum(overlaps) / len(overlaps) if overlaps else None,
        "bucketed_kl_mean": sum(kls) / len(kls) if kls else None,
        "bucketed_kl_max": max(kls) if kls else None,
        "chosen_abs_dlogprob_mean": sum(dlps) / len(dlps) if dlps else None,
        "has_hosted_logprobs": has_logprobs, "flags": flags,
        "_counts": {"top1": top1, "rank5": rank5, "n": n, "overlap_sum": sum(overlaps),
                    "overlap_n": len(overlaps), "kl_sum": sum(kls), "kl_n": len(kls)},
    }


def hosted_determinism(traces: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_prompt: dict[str, list[str]] = {}
    for trace in traces:
        if "error" not in trace:
            by_prompt.setdefault(trace["prompt_id"], []).append(trace.get("text") or "")
    identical = sum(1 for texts in by_prompt.values() if len(texts) > 1 and len(set(texts)) == 1)
    multi = sum(1 for texts in by_prompt.values() if len(texts) > 1)
    return {"prompts_with_repeats": multi, "identical_repeats": identical}


def compare(traces: Sequence[Mapping[str, Any]], adapter: Any, requests: Mapping[str, Mapping[str, Any]],
            *, profile: str, positions: int = 64, top_k: int = 5) -> dict[str, Any]:
    tolerance = e2e.THRESHOLDS["profiles"][profile]
    mapper = TokenMapper(adapter)
    per_prompt = []
    for trace in traces:
        if "error" in trace or trace.get("repeat", 0) != 0:
            continue
        request = requests.get(trace["prompt_id"])
        if request is None:
            continue
        per_prompt.append(compare_trace(trace, adapter, mapper, request["rendered_prompt"],
                                        positions=positions, top_k=top_k))
    totals = {key: sum(r.get("_counts", {}).get(key, 0) for r in per_prompt)
              for key in ("top1", "rank5", "n", "overlap_sum", "overlap_n", "kl_sum", "kl_n")}
    for record in per_prompt:
        record.pop("_counts", None)
    n = totals["n"]
    aggregate = {
        "positions": n,
        "top1_agreement": totals["top1"] / n if n else None,
        "hosted_token_in_local_top5": totals["rank5"] / n if n else None,
        "topk_overlap": totals["overlap_sum"] / totals["overlap_n"] if totals["overlap_n"] else None,
        "bucketed_kl_mean": totals["kl_sum"] / totals["kl_n"] if totals["kl_n"] else None,
    }
    checks = []
    if n:
        checks.append({"check": f"top1_agreement >= {tolerance['hosted_top1_min']}",
                       "ok": aggregate["top1_agreement"] >= tolerance["hosted_top1_min"]})
        checks.append({"check": f"hosted_token_in_local_top5 >= {tolerance['hosted_rank5_min']}",
                       "ok": aggregate["hosted_token_in_local_top5"] >= tolerance["hosted_rank5_min"]})
    if aggregate["topk_overlap"] is not None:
        checks.append({"check": f"topk_overlap >= {tolerance['hosted_topk_overlap_min']}",
                       "ok": aggregate["topk_overlap"] >= tolerance["hosted_topk_overlap_min"]})
    if aggregate["bucketed_kl_mean"] is not None:
        checks.append({"check": f"bucketed_kl_mean <= {tolerance['hosted_kl_max']}",
                       "ok": aggregate["bucketed_kl_mean"] <= tolerance["hosted_kl_max"]})
    weight_identical = all(t.get("weight_identical", True) for t in traces if "error" not in t)
    verdict = "no_data" if not checks else ("pass" if all(c["ok"] for c in checks) else "fail")
    return {"profile": profile, "tolerance": tolerance, "aggregate": aggregate, "checks": checks,
            "verdict": verdict,
            "verdict_kind": "gating" if weight_identical else "advisory: hosted weights not shown identical",
            "hosted_determinism": hosted_determinism(traces), "per_prompt": per_prompt,
            "adapter_identity": getattr(adapter, "identity", type(adapter).__name__),
            # Hosted agreement is a secondary screen; quantization quality is decided by
            # the quant-quality POLICY against the bf16 gold reference (one table).
            "quality_policy": e2e.quality_policy_record()}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="qwen4_exp hosted-reference logprob comparison")
    parser.add_argument("command", nargs="?", default="plan", choices=("providers", "plan", "collect", "compare"))
    parser.add_argument("--provider", default="featherless", choices=sorted(PROVIDERS))
    parser.add_argument("--base-url", help="override the provider base URL (self-hosted vLLM, test servers)")
    parser.add_argument("--prompts", default=str(PROMPTS_PATH))
    parser.add_argument("--items", default=str(e2e.ITEMS_PATH))
    parser.add_argument("--chat-template")
    parser.add_argument("--max-new-tokens", type=int)
    parser.add_argument("--top-logprobs", type=int)
    parser.add_argument("--repeats", type=int)
    parser.add_argument("--live", action="store_true", help="actually send requests (paid)")
    parser.add_argument("--max-cost-usd", type=float, default=0.25)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--traces", help="trace JSONL (collect writes, compare reads)")
    parser.add_argument("--show-bodies", action="store_true", help="plan: print full request bodies")
    parser.add_argument("--positions", type=int, default=64)
    parser.add_argument("--quant-profile", default="bf16", choices=sorted(e2e.THRESHOLDS["profiles"]))
    # Adapter options for compare (same meaning as in qwen4exp_e2e_eval.py).
    parser.add_argument("--adapter", default="mlx")
    parser.add_argument("--model")
    parser.add_argument("--model-file")
    parser.add_argument("--lazy", action="store_true")
    parser.add_argument("--prefill-step", type=int, default=2048)
    parser.add_argument("--score-chunk", type=int, default=256)
    parser.add_argument("--out", help="compare: write the report JSON here")
    return parser.parse_args(argv)


def provider_from_args(args: argparse.Namespace) -> Provider:
    provider = PROVIDERS[args.provider]
    if args.base_url:
        provider = Provider(**{**asdict(provider), "base_url": args.base_url})
    return provider


def main(argv: Sequence[str] | None = None, *, adapter: Any | None = None, poster=post_json) -> int:
    args = parse_args(argv)
    if args.command == "providers":
        print(json.dumps({name: asdict(p) for name, p in PROVIDERS.items()}, indent=1))
        return 0
    provider = provider_from_args(args)
    template = e2e.ChatTemplate(Path(args.chat_template) if args.chat_template else None)
    prompts = load_prompts(Path(args.prompts), Path(args.items))
    requests = build_requests(provider, prompts, template, max_new_tokens=args.max_new_tokens,
                              top_logprobs=args.top_logprobs)
    repeats = args.repeats or prompts["repeats"]
    if args.command == "compare":
        if not args.traces:
            raise SystemExit("compare needs --traces")
        adapter = adapter or e2e.build_adapter(args)
        traces = [json.loads(line) for line in Path(args.traces).read_text(encoding="utf-8").splitlines() if line.strip()]
        report = compare(traces, adapter, {r["prompt_id"]: r for r in requests}, profile=args.quant_profile,
                         positions=args.positions, top_k=requests[0]["top_logprobs"] if requests else 5)
        report["prompts_sha256"] = prompts["_file_sha256"]
        text = json.dumps(report, indent=1, ensure_ascii=False)
        if args.out:
            Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(json.dumps({k: report[k] for k in ("verdict", "verdict_kind", "aggregate", "checks")}, indent=1))
        return 0 if report["verdict"] != "fail" else 1
    cost = estimate(requests, provider, repeats, adapter)
    summary = {"provider": asdict(provider), "prompts_sha256": prompts["_file_sha256"],
               "template_sha256": template.sha256, "estimate": cost,
               "requests": [{k: v for k, v in r.items() if k not in ("body", "rendered_prompt")} for r in requests]}
    if args.show_bodies:
        summary["bodies"] = [r["body"] for r in requests]
    if args.command == "plan":
        print(json.dumps(summary, indent=1, ensure_ascii=False))
        return 0
    try:
        collect(provider, requests, repeats=repeats, live=args.live, max_cost_usd=args.max_cost_usd, cost=cost,
                out=Path(args.traces) if args.traces else None, timeout=args.timeout, poster=poster,
                log=lambda message: print(message, file=sys.stderr))
    except CollectRefused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
