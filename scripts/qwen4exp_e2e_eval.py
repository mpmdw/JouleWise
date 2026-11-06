#!/usr/bin/env python3
"""End-to-end validation harness for the qwen4_exp (Qwen3.8-Flash-Next) MLX port.

GOAL item 7 (docs/align/qwen4_exp_port/GOAL.md). The harness drives any model
through a small pluggable adapter (``generate`` plus optional ``score``) and
runs pinned, hash-verified items:

  consistency  greedy generate() vs teacher-forced score() on the same tokens
               (prefill vs stepwise, including a prompt past the 2048-token
               QSA indexer budget)
  nll          NLL on pinned public-domain texts plus a shuffled control
  coherence    short factual / format / multi-turn / thinking-mode checks
  math         GSM8K test items (first 30, pinned commit)
  ifeval       IFEval items with instructions verifiable without nltk/langdetect
  toolcall     BFCL-style calls and round trips through the REAL chat template
               (XML tool format), parsed strictly
  shade        one benign SHADE-Arena task through the ALIGN kit's
               ``run_episode`` (needs an ALIGN checkout; see --align-checkout)

Pass thresholds are derived in ``THRESHOLDS`` from model-card numbers with a
stated quantization slack per ``--quant-profile``; benchmark thresholds are
one-sided binomial lower bounds, so a small n cannot fail a model that is
performing at the stated floor more than ``alpha`` of the time.

Adapters: ``--adapter mlx`` (pinned mlx-lm 0.31.3 ``load`` with an optional
``model_file`` hook), ``--adapter scripted:FILE.json`` (deterministic stub for
dry runs and tests), or ``--adapter module:callable`` (custom; the callable
receives the parsed CLI namespace and returns an adapter).

The harness itself needs only the standard library plus jinja2 for the chat
template. It never quantizes the KV cache, never pads, and always runs batch 1
(the engine feasibility review lists all three as unsafe for this model).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import platform
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

HARNESS_VERSION = "qwen4exp-e2e/v1"
REPO_ROOT = Path(__file__).resolve().parent.parent
ITEMS_PATH = REPO_ROOT / "configs" / "qwen4_exp_port" / "e2e_items.json"
ITEMS_SCHEMA = "qwen4exp-e2e-items/v1"

# Pinned identities of the official artifacts (.engine/hf-flashnext).
TEMPLATE_SHA256 = "c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041"
CONFIG_SHA256 = "889658f2508e8c61d409b02e70e0d78d8d4452ec65aaafbe129805d213d2e74b"
MODEL_CARD_SHA256 = "35ca37ccc366f1ba478dab33841a2c0c18ce53fd62f291ca05341f7728b225b2"
TEMPLATE_PATHS = (
    REPO_ROOT / ".engine" / "hf-flashnext" / "chat_template.jinja",
    REPO_ROOT / "tests" / "fixtures" / "qwen4exp_chat_template.jinja",
)

# tokenizer_config.json added tokens; generation_config.json eos_token_id.
SPECIAL_TOKENS = {
    "<|endoftext|>": 248044, "<|im_start|>": 248045, "<|im_end|>": 248046,
    "<tool_call>": 248058, "</tool_call>": 248059,
    "<tool_response>": 248066, "</tool_response>": 248067,
    "<think>": 248068, "</think>": 248069,
}
EOS_IDS = (248046, 248044)
VOCAB_SIZE = 248320
LN_VOCAB = math.log(VOCAB_SIZE)
STAGES = ("consistency", "nll", "coherence", "math", "ifeval", "toolcall", "shade")


# --------------------------------------------------------------------------
# Thresholds
# --------------------------------------------------------------------------

THRESHOLDS: dict[str, Any] = {
    "alpha": 0.05,
    "model_card_sha256": MODEL_CARD_SHA256,
    "benchmarks": {
        # p_reference: expected pass rate of the unquantized model on THESE items
        # under the harness's mode; the profile's slack is subtracted, then the
        # pass threshold is the one-sided binomial lower bound at alpha.
        "coherence": {
            "p_reference": 0.98,
            "slack_scale": 0.33,
            "basis": "Trivial factual/format items any model at the card's level answers; "
                     "0.98 leaves room for one formatting miss. Only a third of the profile's "
                     "quantization slack applies: a quantized model that misses these is broken.",
        },
        "math": {
            "p_reference": {"nothinking": 0.92, "thinking": 0.95},
            "basis": "The card reports no GSM8K. Card GPQA-Diamond 91.7 and HLE 35.9 (thinking, xhigh) "
                     "put grade-school arithmetic at ceiling; an external NVFP4 (4-bit) run measured "
                     "GSM8K 193/200 = 0.965 greedy (HF discussion #47). 0.95 for thinking; minus 0.03 "
                     "for non-thinking mode (judgment, no card number).",
        },
        "ifeval": {
            "p_reference": 0.813,
            "basis": "Card IFBench 81.3 (thinking). IFEval-strict prompt-level is the easier, older "
                     "benchmark, so the IFBench number is a conservative proxy for these items in "
                     "either mode.",
        },
        "toolcall": {
            "p_reference": 0.90,
            "basis": "Card Toolathlon Verified 73.5 is long-horizon multi-tool work; single-turn "
                     "BFCL-style AST calls are far easier. 0.90 is a conservative floor (judgment).",
        },
    },
    "nll": {
        "natural_max_nats_per_token": 2.5,
        "control_margin_min_nats": 2.0,
        "long_tail_excess_max_nats": 0.5,
        "basis": "Absolute, provisional (no reference run yet): the natural texts are famous public-"
                 "domain passages a model at this level largely memorizes (expected well under 1.5 "
                 "nats/token); a broken port sits near ln(V)=12.4 or loses the natural-vs-shuffled "
                 "gap. long_tail_excess bounds NLL past token 2048 (the QSA indexer budget) against "
                 "the first 2048 tokens of the same text.",
    },
    "consistency": {
        "near_tie_nats": 0.1,
        "max_abs_dlogprob": 0.25,
        "mean_abs_dlogprob": 0.03,
        "basis": "Same weights, same tokens: prefill and stepwise differ only by kernel order. "
                 "Argmax must agree except at near-ties; logprob bounds allow bf16 accumulation.",
    },
    # Quantization profiles. All numbers PROVISIONAL until GOAL item 11 measures
    # the drift of the chosen recipe against layer-streamed bf16 on these
    # prompts; then replace with (measured value x 2) plus the FP8 allowance.
    # Anchors (dense models, llama.cpp k-quants, KL vs bf16): Q8_0 ~0.02 KLD /
    # 97.8 % same-top-1; Q4_K_M ~91.9 % same-top-1; Q3_K_M ~0.10-0.13 KLD /
    # ~90 %. MLX affine RTN at group 64 is a cruder quantizer than k-quants,
    # hence the wider bounds for the 3-bit-expert recipe.
    "profiles": {
        # Saturday maxfit screening uses the existing, stricter 8-bit bounds.
        # These are PROVISIONAL screens, not measured 6/5-bit error budgets.
        "maxfit": {"benchmark_slack": 0.01, "nll_rel_max": 0.02, "hosted_kl_max": 0.05,
                   "hosted_top1_min": 0.95, "hosted_topk_overlap_min": 0.85, "hosted_rank5_min": 0.99},
        "maxfit5": {"benchmark_slack": 0.01, "nll_rel_max": 0.02, "hosted_kl_max": 0.05,
                    "hosted_top1_min": 0.95, "hosted_topk_overlap_min": 0.85, "hosted_rank5_min": 0.99},
        "bf16": {"benchmark_slack": 0.00, "nll_rel_max": 0.01, "hosted_kl_max": 0.03,
                 "hosted_top1_min": 0.97, "hosted_topk_overlap_min": 0.90, "hosted_rank5_min": 0.995},
        "8bit": {"benchmark_slack": 0.01, "nll_rel_max": 0.02, "hosted_kl_max": 0.05,
                 "hosted_top1_min": 0.95, "hosted_topk_overlap_min": 0.85, "hosted_rank5_min": 0.99},
        "e4_ple4_other8": {"benchmark_slack": 0.03, "nll_rel_max": 0.05, "hosted_kl_max": 0.12,
                           "hosted_top1_min": 0.90, "hosted_topk_overlap_min": 0.80, "hosted_rank5_min": 0.98},
        "e3_ple4_other8": {"benchmark_slack": 0.06, "nll_rel_max": 0.10, "hosted_kl_max": 0.25,
                           "hosted_top1_min": 0.85, "hosted_topk_overlap_min": 0.70, "hosted_rank5_min": 0.97},
    },
}


def binomial_cdf_below(k: int, n: int, p: float) -> float:
    """P(X < k) for X ~ Binomial(n, p)."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, max(0, k)))


def binomial_pass_threshold(n: int, p: float, alpha: float) -> int:
    """Largest k with P(X < k) <= alpha: a model at pass rate p fails <= alpha."""
    if n <= 0:
        return 0
    p = min(max(p, 0.0), 1.0)
    k = 0
    while k < n and binomial_cdf_below(k + 1, n, p) <= alpha:
        k += 1
    return k


def benchmark_threshold(stage: str, n: int, profile: str, thinking: bool = False) -> dict[str, Any]:
    spec = THRESHOLDS["benchmarks"][stage]
    p_ref = spec["p_reference"]
    if isinstance(p_ref, Mapping):
        p_ref = p_ref["thinking" if thinking else "nothinking"]
    slack = THRESHOLDS["profiles"][profile]["benchmark_slack"] * spec.get("slack_scale", 1.0)
    p_floor = max(0.0, p_ref - slack)
    alpha = THRESHOLDS["alpha"]
    return {"n": n, "p_reference": p_ref, "slack": round(slack, 4), "p_floor": round(p_floor, 4),
            "alpha": alpha, "min_pass": binomial_pass_threshold(n, p_floor, alpha),
            "profile": profile, "basis": spec["basis"]}


# --------------------------------------------------------------------------
# Adapter contract
# --------------------------------------------------------------------------

@dataclass
class Generation:
    """One greedy completion. ``top_logprobs[i]`` is [(token_id, logprob)]."""

    token_ids: list[int]
    text: str
    finish_reason: str  # "stop" | "length"
    token_logprobs: list[float] | None = None
    top_logprobs: list[list[tuple[int, float]]] | None = None
    prompt_tokens: int = 0
    seconds: float = 0.0


@dataclass
class Scored:
    """Teacher-forced log-probabilities of ``continuation`` given ``prompt``."""

    token_logprobs: list[float]
    argmax_ids: list[int]
    top_logprobs: list[list[tuple[int, float]]] | None = None
    query_logprobs: list[dict[int, float]] | None = None
    # Raw-logit full-vocabulary normalizer at each scored position.  Optional
    # for legacy/scripted adapters; gold-stream capture requires it.
    logsumexp: list[float] | None = None


class AdapterContract:
    """Documentation of the duck-typed adapter (not a base class requirement).

    identity: str           backend, model artifact and version; never a secret
    encode(text) -> ids      no BOS (tokenizer_config add_bos_token = false);
                             special-token text maps to its single id
    decode(ids) -> str
    generate(prompt_ids, *, max_tokens, stop_ids, top_k=0) -> Generation
                             greedy (argmax) decoding, batch 1, stop on stop_ids
                             (the stop token is included in token_ids)
    score(prompt_ids, continuation_ids, *, top_k=0, query_ids=None) -> Scored
                             optional; teacher-forced; prompt_ids non-empty
    token_bytes(token_id) -> bytes      optional (hosted-reference mapping)
    vocab_size: int                     optional
    """


def require(adapter: Any, method: str) -> Callable[..., Any] | None:
    fn = getattr(adapter, method, None)
    return fn if callable(fn) else None


# --------------------------------------------------------------------------
# Chat template (rendered exactly as transformers 5.22.1 does)
# --------------------------------------------------------------------------

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TemplateError(RuntimeError):
    pass


class ChatTemplate:
    """The official chat_template.jinja, compiled like
    transformers.utils.chat_template_utils._cached_compile_jinja_template:
    ImmutableSandboxedEnvironment(trim_blocks, lstrip_blocks, loopcontrols),
    json.dumps-based ``tojson`` (ensure_ascii=False), ``raise_exception``.
    The sha256 must match the pinned official template unless
    ``allow_unpinned`` is set (recorded in results)."""

    def __init__(self, path: Path | None = None, *, allow_unpinned: bool = False) -> None:
        candidates = [path] if path else [p for p in TEMPLATE_PATHS if p.exists()]
        if not candidates or not candidates[0].exists():
            raise TemplateError("chat template not found: " + ", ".join(str(p) for p in TEMPLATE_PATHS))
        self.path = candidates[0]
        self.source = self.path.read_text(encoding="utf-8")
        self.sha256 = sha256_text(self.source)
        self.pinned = self.sha256 == TEMPLATE_SHA256
        if not self.pinned and not allow_unpinned:
            raise TemplateError(f"template sha256 {self.sha256} != pinned {TEMPLATE_SHA256}")
        try:
            import jinja2
            import jinja2.ext
            from jinja2.sandbox import ImmutableSandboxedEnvironment
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise TemplateError("jinja2 is required to render the chat template") from exc

        def raise_exception(message):
            raise jinja2.exceptions.TemplateError(message)

        def tojson(x, ensure_ascii=False, indent=None, separators=None, sort_keys=False):
            return json.dumps(x, ensure_ascii=ensure_ascii, indent=indent, separators=separators,
                              sort_keys=sort_keys)

        env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True,
                                            extensions=[jinja2.ext.loopcontrols])
        env.filters["tojson"] = tojson
        env.globals["raise_exception"] = raise_exception
        env.globals["strftime_now"] = lambda fmt: time.strftime(fmt)
        self._compiled = env.from_string(self.source)
        self._jinja_error = jinja2.exceptions.TemplateError

    def render(self, messages: Sequence[Mapping[str, Any]], tools: Sequence[Mapping[str, Any]] | None = None,
               *, add_generation_prompt: bool = True, enable_thinking: bool = False,
               reasoning_effort: str | None = None, preserve_thinking: bool | None = None) -> str:
        kwargs: dict[str, Any] = {"enable_thinking": enable_thinking}
        if reasoning_effort is not None:
            kwargs["reasoning_effort"] = reasoning_effort
        if preserve_thinking is not None:
            kwargs["preserve_thinking"] = preserve_thinking
        try:
            return self._compiled.render(messages=list(messages), tools=list(tools) if tools else None,
                                         documents=None, add_generation_prompt=add_generation_prompt,
                                         **kwargs)
        except self._jinja_error as exc:
            raise TemplateError(str(exc)) from exc


# --------------------------------------------------------------------------
# Completion parsing: reasoning split and strict XML tool calls
# --------------------------------------------------------------------------

def split_reasoning(completion: str, *, thinking: bool) -> tuple[str, str, list[str]]:
    """Return (reasoning, visible, flags).

    With thinking on the template prefills ``<think>\\n``, so the completion
    begins inside the reasoning span and must close it with ``</think>``. With
    thinking off the template prefills an empty closed span; any ``<think>``
    the model still emits is reported, not hidden.
    """
    flags: list[str] = []
    text = completion
    for stop in ("<|im_end|>", "<|endoftext|>"):
        if text.endswith(stop):
            text = text[: -len(stop)]
    if thinking:
        end = text.find("</think>")
        if end < 0:
            return text.strip(), "", ["reasoning_unclosed"]
        reasoning, visible = text[:end], text[end + len("</think>"):]
        if "<think>" in visible or "</think>" in visible:
            flags.append("reasoning_tag_in_visible")
        return reasoning.strip(), visible.strip(), flags
    if "<think>" in text or "</think>" in text:
        flags.append("reasoning_tag_with_thinking_off")
    return "", text.strip(), flags


_FUNCTION_OPEN = re.compile(r"<function=([^<>\s=]+)>")
_PARAMETER_OPEN = re.compile(r"<parameter=([^<>\s=]+)>")
_CONTROL_TAG = re.compile(r"</?(?:tool_call|function|parameter)\b")


def _schema_types(schema: Mapping[str, Any]) -> set[str]:
    kind = schema.get("type")
    if isinstance(kind, str):
        return {kind}
    if isinstance(kind, list):
        return set(kind)
    return set()


def _decode_parameter(raw: str, schema: Mapping[str, Any]) -> tuple[Any, list[str]]:
    """The template writes strings literally and everything else as JSON
    (``args_value | tojson``); decode by the declared schema type."""
    raw = raw.removeprefix("\n").removesuffix("\n")
    types = _schema_types(schema)
    if types == {"string"} or (not types and "enum" in schema and all(isinstance(v, str) for v in schema["enum"])):
        return raw, []
    try:
        value = json.loads(raw)
    except ValueError:
        return raw, ["parameter_not_json"]
    if types and not _type_ok(value, types):
        return value, ["parameter_type_mismatch"]
    return value, []


def _type_ok(value: Any, types: set[str]) -> bool:
    checks = {
        "string": isinstance(value, str), "boolean": type(value) is bool,
        "integer": type(value) is int, "number": type(value) in (int, float),
        "null": value is None, "object": isinstance(value, dict), "array": isinstance(value, list),
    }
    return any(checks.get(t, False) for t in types)


def parse_tool_calls(visible: str, tools: Sequence[Mapping[str, Any]]) -> tuple[str, list[dict[str, Any]], list[str]]:
    """Parse ``<tool_call><function=NAME><parameter=K>V</parameter></function></tool_call>``.

    Returns (text before the first call, calls, flags). Strict: unknown
    functions or parameters, unclosed tags, nested control tags and trailing
    text after the calls are flags; a malformed turn returns no calls.
    """
    first = visible.find("<tool_call>")
    if first < 0:
        flags = ["unmatched_control_tag"] if _CONTROL_TAG.search(visible) else []
        return visible, [], flags
    schemas = {}
    for tool in tools:
        function = tool.get("function", tool)
        schemas[function["name"]] = function.get("parameters", {"type": "object", "properties": {}})
    calls: list[dict[str, Any]] = []
    flags: list[str] = []
    cursor = first

    def skip_ws(pos: int) -> int:
        while pos < len(visible) and visible[pos].isspace():
            pos += 1
        return pos

    try:
        while cursor < len(visible):
            if not visible.startswith("<tool_call>", cursor):
                raise ValueError("trailing_text_after_tool_call")
            cursor = skip_ws(cursor + len("<tool_call>"))
            match = _FUNCTION_OPEN.match(visible, cursor)
            if match is None:
                raise ValueError("expected_function")
            name = match[1]
            if name not in schemas:
                raise ValueError("unknown_function")
            properties = schemas[name].get("properties", {})
            arguments: dict[str, Any] = {}
            cursor = skip_ws(match.end())
            while (param := _PARAMETER_OPEN.match(visible, cursor)) is not None:
                key = param[1]
                if key in arguments:
                    raise ValueError("duplicate_parameter")
                if key not in properties:
                    raise ValueError("unknown_parameter")
                end = visible.find("</parameter>", param.end())
                if end < 0:
                    raise ValueError("unclosed_parameter")
                raw = visible[param.end():end]
                if _CONTROL_TAG.search(raw):
                    raise ValueError("nested_control_tag")
                value, value_flags = _decode_parameter(raw, properties[key])
                flags.extend(value_flags)
                arguments[key] = value
                cursor = skip_ws(end + len("</parameter>"))
            if not visible.startswith("</function>", cursor):
                raise ValueError("expected_function_close")
            cursor = skip_ws(cursor + len("</function>"))
            if not visible.startswith("</tool_call>", cursor):
                raise ValueError("expected_tool_call_close")
            cursor = skip_ws(cursor + len("</tool_call>"))
            missing = [k for k in schemas[name].get("required", ()) if k not in arguments]
            if missing:
                flags.append("missing_required_parameter")
            calls.append({"name": name, "arguments": arguments})
    except ValueError as exc:
        return visible[:first], [], [f"malformed_tool_call:{exc}"]
    return visible[:first], calls, flags


# --------------------------------------------------------------------------
# Matching helpers
# --------------------------------------------------------------------------

def _norm_string(value: str) -> str:
    value = " ".join(value.casefold().split())
    return value.rstrip(".!? ")


def value_matches(actual: Any, allowed: Sequence[Any], omit: str) -> bool:
    for option in allowed:
        if isinstance(option, Mapping) and "unordered" in option:
            if isinstance(actual, list) and sorted(map(_norm_any, actual)) == sorted(map(_norm_any, option["unordered"])):
                return True
            continue
        if option == omit:
            continue
        if isinstance(option, bool) or isinstance(actual, bool):
            if actual is option:
                return True
            continue
        if isinstance(option, (int, float)) and isinstance(actual, (int, float)):
            if abs(float(actual) - float(option)) <= 1e-6 * max(1.0, abs(float(option))):
                return True
            continue
        if isinstance(option, str) and isinstance(actual, str) and _norm_string(actual) == _norm_string(option):
            return True
    return False


def _norm_any(value: Any) -> str:
    return _norm_string(value) if isinstance(value, str) else json.dumps(value, sort_keys=True)


def call_matches(actual: Mapping[str, Any], expected: Mapping[str, Any], omit: str) -> bool:
    if actual["name"] != expected["name"]:
        return False
    args = actual["arguments"]
    spec = expected["args"]
    if any(key not in spec for key in args):
        return False  # BFCL: unexpected parameters fail
    for key, allowed in spec.items():
        if key not in args:
            if omit not in allowed:
                return False
            continue
        if not value_matches(args[key], allowed, omit):
            return False
    return True


def calls_match(actual: Sequence[Mapping[str, Any]], expected: Sequence[Mapping[str, Any]], omit: str) -> bool:
    """Order-free one-to-one matching (parallel calls may come in any order)."""
    if len(actual) != len(expected):
        return False
    remaining = list(expected)
    for call in actual:
        for index, candidate in enumerate(remaining):
            if call_matches(call, candidate, omit):
                del remaining[index]
                break
        else:
            return False
    return True


# --------------------------------------------------------------------------
# IFEval strict checkers (google-research instruction_following_eval @26d8ccd)
# --------------------------------------------------------------------------

def _count_words(text: str) -> int:
    return len(re.findall(r"\w+", text))  # nltk RegexpTokenizer(r"\w+")


def _relation(actual: int, relation: str, target: int) -> bool:
    if relation == "less than":
        return actual < target
    if relation == "at least":
        return actual >= target
    raise ValueError("unknown relation " + relation)


def _paragraphs_divider(value: str, n: int) -> bool:
    paragraphs = re.split(r"\s?\*\*\*\s?", value)
    count = len(paragraphs)
    for index, paragraph in enumerate(paragraphs):
        if not paragraph.strip():
            if index == 0 or index == len(paragraphs) - 1:
                count -= 1
            else:
                return False
    return count == n


def _nth_paragraph_first_word(value: str, num_paragraphs: int, nth_paragraph: int, first_word: str) -> bool:
    paragraphs = re.split(r"\n\n", value)
    count = len(paragraphs) - sum(1 for p in paragraphs if not p.strip())
    if nth_paragraph > count:
        return False
    paragraph = paragraphs[nth_paragraph - 1].strip()
    if not paragraph:
        return False
    word = paragraph.split()[0].strip().lstrip("'").lstrip('"')
    found = ""
    for letter in word:
        if letter in {".", ",", "?", "!", "'", '"'}:
            break
        found += letter.lower()
    return count == num_paragraphs and found == first_word.lower()


def _two_responses(value: str) -> bool:
    valid = []
    parts = value.split("******")
    for index, part in enumerate(parts):
        if not part.strip():
            if index not in (0, len(parts) - 1):
                return False
        else:
            valid.append(part)
    return len(valid) == 2 and valid[0].strip() != valid[1].strip()


def _postscript(value: str, marker: str) -> bool:
    value = value.lower()
    marker = marker.strip()
    if marker == "P.P.S":
        pattern = r"\s*p\.\s?p\.\s?s.*$"
    elif marker == "P.S.":
        pattern = r"\s*p\.\s?s\..*$"
    else:
        pattern = r"\s*" + marker.lower() + r".*$"
    return bool(re.findall(pattern, value, flags=re.MULTILINE))


def _highlights(value: str, n: int) -> bool:
    count = sum(1 for h in re.findall(r"\*[^\n\*]*\*", value) if h.strip("*").strip())
    count += sum(1 for h in re.findall(r"\*\*[^\n\*]*\*\*", value)
                 if h.removeprefix("**").removesuffix("**").strip())
    return count >= n


def _json_ok(value: str) -> bool:
    value = (value.strip().removeprefix("```json").removeprefix("```Json").removeprefix("```JSON")
             .removeprefix("```").removesuffix("```").strip())
    try:
        json.loads(value)
    except ValueError:
        return False
    return True


IFEVAL_CHECKS: dict[str, Callable[..., bool]] = {
    "punctuation:no_comma": lambda v: not re.search(r"\,", v),
    "length_constraints:number_words": lambda v, num_words, relation: _relation(_count_words(v), relation, num_words),
    "keywords:forbidden_words": lambda v, forbidden_words: not any(
        re.search(r"\b" + w + r"\b", v, flags=re.IGNORECASE) for w in set(forbidden_words)),
    "detectable_format:number_highlighted_sections": lambda v, num_highlights: _highlights(v, num_highlights),
    "keywords:frequency": lambda v, keyword, frequency, relation: _relation(
        len(re.findall(keyword.strip(), v, flags=re.IGNORECASE)), relation, frequency),
    "combination:repeat_prompt": lambda v, prompt_to_repeat: v.strip().lower().startswith(
        prompt_to_repeat.strip().lower()),
    "startend:quotation": lambda v: len(v.strip()) > 1 and v.strip()[0] == '"' and v.strip()[-1] == '"',
    # IFEval also requires langdetect == "en"; not available here (recorded).
    "change_case:english_lowercase": lambda v: v.islower(),
    "change_case:english_capital": lambda v: v.isupper(),
    "keywords:existence": lambda v, keywords: all(re.search(k, v, flags=re.IGNORECASE) for k in keywords),
    "detectable_format:title": lambda v: any(t.lstrip("<").rstrip(">").strip()
                                             for t in re.findall(r"<<[^\n]+>>", v)),
    "keywords:letter_frequency": lambda v, letter, let_frequency, let_relation: _relation(
        v.lower().count(letter.strip().lower()), let_relation, let_frequency),
    "detectable_format:number_bullet_lists": lambda v, num_bullets: (
        len(re.findall(r"^\s*\*[^\*].*$", v, flags=re.MULTILINE))
        + len(re.findall(r"^\s*-.*$", v, flags=re.MULTILINE))) == num_bullets,
    "detectable_content:number_placeholders": lambda v, num_placeholders: len(re.findall(r"\[.*?\]", v)) >= num_placeholders,
    "length_constraints:number_paragraphs": lambda v, num_paragraphs: _paragraphs_divider(v, num_paragraphs),
    "startend:end_checker": lambda v, end_phrase: v.strip().strip('"').lower().endswith(end_phrase.strip().lower()),
    "detectable_content:postscript": lambda v, postscript_marker: _postscript(v, postscript_marker),
    "combination:two_responses": _two_responses,
    "detectable_format:json_format": _json_ok,
    "detectable_format:multiple_sections": lambda v, section_spliter, num_sections: (
        len(re.split(r"\s?" + section_spliter.strip() + r"\s?\d+\s?", v)) - 1) >= num_sections,
    "length_constraints:nth_paragraph_first_word": _nth_paragraph_first_word,
    "detectable_format:constrained_response": lambda v: any(
        option in v.strip() for option in ("My answer is yes.", "My answer is no.", "My answer is maybe.")),
}


def ifeval_follow(response: str, instruction_ids: Sequence[str], kwargs: Sequence[Mapping[str, Any]]) -> list[bool]:
    results = []
    for instruction, args in zip(instruction_ids, kwargs):
        check = IFEVAL_CHECKS[instruction]
        results.append(bool(check(response, **args)) if response.strip() else False)
    return results


# --------------------------------------------------------------------------
# Math answer extraction
# --------------------------------------------------------------------------

def _last_boxed(text: str) -> str | None:
    index = text.rfind("\\boxed{")
    if index < 0:
        return None
    depth, start = 0, index + len("\\boxed{")
    for pos in range(start, len(text)):
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            if depth == 0:
                return text[start:pos]
            depth -= 1
    return None


def _number(text: str) -> float | None:
    cleaned = (text.replace(",", "").replace("\\$", "").replace("$", "").replace("\\%", "")
               .replace("%", ""))
    cleaned = re.sub(r"\\(?:text|mathrm)\{[^}]*\}", "", cleaned)
    cleaned = cleaned.replace("\\!", "").replace("\\,", "").strip()
    match = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*", cleaned)
    if match is None:
        fraction = re.fullmatch(r"\s*\\[dt]?frac\{(-?\d+)\}\{(\d+)\}\s*", cleaned)
        if fraction is None:
            return None
        return int(fraction[1]) / int(fraction[2])
    return float(match[1])


def extract_math_answer(visible: str) -> tuple[float | None, str]:
    boxed = _last_boxed(visible)
    if boxed is not None:
        return _number(boxed), "boxed"
    numbers = re.findall(r"-?\d[\d,]*(?:\.\d+)?", visible)
    if numbers:
        return _number(numbers[-1]), "last_number_fallback"
    return None, "none"


# --------------------------------------------------------------------------
# Items
# --------------------------------------------------------------------------

class ItemsError(RuntimeError):
    pass


def _item_digest(item: Mapping[str, Any]) -> str:
    return sha256_text(json.dumps({k: v for k, v in item.items() if k != "sha256"},
                                  sort_keys=True, ensure_ascii=False))


def load_items(path: Path = ITEMS_PATH) -> dict[str, Any]:
    """Load and re-verify every item hash; any mismatch is fatal."""
    raw = path.read_bytes()
    items = json.loads(raw)
    if items.get("schema") != ITEMS_SCHEMA:
        raise ItemsError(f"unexpected items schema {items.get('schema')!r}")
    bad = []
    for entry in items["nll"]:
        if sha256_text(entry["text"]) != entry["sha256"]:
            bad.append(entry["id"])
    for entry in items["math"]:
        if sha256_text(entry["question"] + "\x00" + entry["answer"]) != entry["sha256"]:
            bad.append(entry["id"])
    for entry in items["ifeval"]:
        if sha256_text(json.dumps([entry["prompt"], entry["instruction_id_list"], entry["kwargs"]],
                                  sort_keys=True, ensure_ascii=False)) != entry["sha256"]:
            bad.append(entry["id"])
        unknown = set(entry["instruction_id_list"]) - set(IFEVAL_CHECKS)
        if unknown:
            raise ItemsError(f"{entry['id']}: unsupported instructions {sorted(unknown)}")
    for group in ("toolcall", "coherence"):
        for entry in items[group]:
            if _item_digest(entry) != entry["sha256"]:
                bad.append(entry["id"])
    if bad:
        raise ItemsError("item sha256 mismatch: " + ", ".join(bad))
    items["_file_sha256"] = hashlib.sha256(raw).hexdigest()
    items["_path"] = str(path)
    return items


# --------------------------------------------------------------------------
# Harness core
# --------------------------------------------------------------------------

@dataclass
class RunConfig:
    profile: str = "bf16"
    math_thinking: bool = False
    ifeval_thinking: bool = False
    toolcall_thinking: bool = False
    reasoning_effort: str = "low"
    max_tokens_math: int = 1024
    max_tokens_math_thinking: int = 8192
    max_tokens_ifeval: int = 1280
    max_tokens_toolcall: int = 512
    limit: int | None = None
    top_k: int = 5


class Harness:
    def __init__(self, adapter: Any, template: ChatTemplate, items: Mapping[str, Any], config: RunConfig,
                 *, log: Callable[[str], None] | None = None) -> None:
        if config.profile not in THRESHOLDS["profiles"]:
            raise ValueError(f"unknown quant profile {config.profile!r}")
        self.adapter = adapter
        self.template = template
        self.items = items
        self.config = config
        self.log = log or (lambda message: None)

    # -- primitives -------------------------------------------------------
    def chat(self, messages, tools=None, *, thinking: bool, max_tokens: int, top_k: int = 0):
        prompt = self.template.render(messages, tools, add_generation_prompt=True, enable_thinking=thinking,
                                      reasoning_effort=self.config.reasoning_effort if thinking else None)
        prompt_ids = list(self.adapter.encode(prompt))
        started = time.perf_counter()
        generation = self.adapter.generate(prompt_ids, max_tokens=max_tokens, stop_ids=EOS_IDS, top_k=top_k)
        if not generation.seconds:
            generation.seconds = time.perf_counter() - started
        generation.prompt_tokens = generation.prompt_tokens or len(prompt_ids)
        reasoning, visible, flags = split_reasoning(generation.text, thinking=thinking)
        if generation.finish_reason != "stop":
            flags.append("finish_length")
        record = {
            "prompt_sha256": sha256_text(prompt), "prompt_tokens": len(prompt_ids),
            "completion_tokens": len(generation.token_ids), "finish_reason": generation.finish_reason,
            "seconds": round(generation.seconds, 3), "visible": visible,
            "reasoning_chars": len(reasoning), "flags": flags,
        }
        return generation, reasoning, visible, record, prompt_ids

    def _limited(self, entries):
        return list(entries)[: self.config.limit] if self.config.limit else list(entries)

    @staticmethod
    def _summarize(stage: str, records: list[dict[str, Any]], threshold: dict[str, Any] | None) -> dict[str, Any]:
        passed = sum(1 for r in records if r.get("pass"))
        verdict = "pass"
        if threshold is not None:
            verdict = "pass" if passed >= threshold["min_pass"] else "fail"
        elif not all(r.get("pass") for r in records):
            verdict = "fail"
        return {"stage": stage, "n": len(records), "passed": passed, "threshold": threshold,
                "verdict": verdict, "items": records}

    # -- consistency ------------------------------------------------------
    def run_consistency(self) -> dict[str, Any]:
        if require(self.adapter, "score") is None:
            return {"stage": "consistency", "verdict": "skipped", "reason": "adapter has no score()"}
        spec = THRESHOLDS["consistency"]
        texts = {entry["id"]: entry["text"] for entry in self.items["nll"]}
        records = []
        for entry in self._limited(self.items["consistency"]):
            messages = entry["messages"]
            if "context_from" in entry:
                context = texts[entry["context_from"]]
                messages = [dict(m, content=m["content"].replace("{context}", context)) for m in messages]
            generation, _, _, record, prompt_ids = self.chat(messages, thinking=False,
                                                              max_tokens=entry["max_tokens"], top_k=2)
            scored = self.adapter.score(prompt_ids, generation.token_ids, top_k=2)
            mismatches, deltas = [], []
            for index, token in enumerate(generation.token_ids):
                if generation.token_logprobs is not None:
                    deltas.append(abs(generation.token_logprobs[index] - scored.token_logprobs[index]))
                if scored.argmax_ids[index] != token:
                    gaps = []
                    for tops in (scored.top_logprobs, generation.top_logprobs):
                        if tops and len(tops[index]) >= 2:
                            gaps.append(tops[index][0][1] - tops[index][1][1])
                    near_tie = bool(gaps) and min(gaps) <= spec["near_tie_nats"]
                    mismatches.append({"position": index, "near_tie": near_tie})
            hard = [m for m in mismatches if not m["near_tie"]]
            max_delta = max(deltas) if deltas else 0.0
            mean_delta = sum(deltas) / len(deltas) if deltas else 0.0
            ok = (not hard and max_delta <= spec["max_abs_dlogprob"] and mean_delta <= spec["mean_abs_dlogprob"]
                  and len(generation.token_ids) > 0)
            record.update({"id": entry["id"], "argmax_mismatches": mismatches,
                           "max_abs_dlogprob": round(max_delta, 6), "mean_abs_dlogprob": round(mean_delta, 6),
                           "logprobs_compared": bool(deltas), "pass": ok,
                           "past_qsa_budget": record["prompt_tokens"] > 2048})
            records.append(record)
            self.log(f"consistency {entry['id']}: pass={ok} max_dlp={max_delta:.4f}")
        summary = self._summarize("consistency", records, None)
        summary["criteria"] = spec
        return summary

    # -- nll --------------------------------------------------------------
    def run_nll(self, reference: Mapping[str, Any] | None = None) -> dict[str, Any]:
        if require(self.adapter, "score") is None:
            return {"stage": "nll", "verdict": "skipped", "reason": "adapter has no score()"}
        spec = THRESHOLDS["nll"]
        prefix = [SPECIAL_TOKENS["<|endoftext|>"]]  # document boundary; no BOS in this tokenizer
        results: dict[str, dict[str, Any]] = {}
        for entry in self.items["nll"]:
            ids = list(self.adapter.encode(entry["text"]))
            scored = self.adapter.score(prefix, ids)
            lps = scored.token_logprobs
            nll = -sum(lps) / len(lps)
            record = {"id": entry["id"], "kind": entry["kind"], "tokens": len(ids),
                      "bytes": len(entry["text"].encode("utf-8")), "nll_per_token": round(nll, 5),
                      "bits_per_byte": round(-sum(lps) / math.log(2) / len(entry["text"].encode("utf-8")), 5),
                      "argmax_hit_rate": round(sum(1 for a, t in zip(scored.argmax_ids, ids) if a == t) / len(ids), 4)}
            if len(ids) > 2048:
                head, tail = lps[:2048], lps[2048:]
                record["nll_first_2048"] = round(-sum(head) / len(head), 5)
                record["nll_after_2048"] = round(-sum(tail) / len(tail), 5)
            results[entry["id"]] = record
            self.log(f"nll {entry['id']}: {nll:.4f} nats/token over {len(ids)} tokens")
        checks = []
        for record in results.values():
            if record["kind"] == "natural":
                checks.append({"check": f"{record['id']}: nll <= natural_max",
                               "ok": record["nll_per_token"] <= spec["natural_max_nats_per_token"]})
            if "nll_after_2048" in record:
                checks.append({"check": f"{record['id']}: nll after 2048 <= first 2048 + long_tail_excess_max",
                               "ok": record["nll_after_2048"] <= record["nll_first_2048"] + spec["long_tail_excess_max_nats"]})
        for entry in self.items["nll"]:
            if entry["kind"] == "control":
                base = results[entry["source"]["derived_from"]]["nll_per_token"]
                checks.append({"check": f"{entry['id']} - {entry['source']['derived_from']} >= control_margin_min",
                               "ok": results[entry["id"]]["nll_per_token"] - base >= spec["control_margin_min_nats"]})
        if reference:
            rel = THRESHOLDS["profiles"][self.config.profile]["nll_rel_max"]
            ref_records = {r["id"]: r for r in reference.get("items", [])}
            for record in results.values():
                ref = ref_records.get(record["id"])
                if ref is None or record["kind"] != "natural":
                    continue
                ratio = record["nll_per_token"] / max(ref["nll_per_token"], 1e-9)
                record["reference_nll_per_token"] = ref["nll_per_token"]
                record["nll_ratio_to_reference"] = round(ratio, 5)
                # Absolute floor so a near-zero memorized NLL cannot fail on noise.
                ok = record["nll_per_token"] <= ref["nll_per_token"] * (1 + rel) + 0.02
                checks.append({"check": f"{record['id']}: nll <= reference*(1+{rel})+0.02", "ok": ok})
        verdict = "pass" if all(c["ok"] for c in checks) else "fail"
        return {"stage": "nll", "verdict": verdict, "criteria": spec, "checks": checks,
                "items": list(results.values()), "ln_vocab": round(LN_VOCAB, 4)}

    # -- coherence --------------------------------------------------------
    def run_coherence(self) -> dict[str, Any]:
        records = []
        for entry in self._limited(self.items["coherence"]):
            thinking = entry["thinking"]
            _, _, visible, record, _ = self.chat(entry["messages"], thinking=thinking,
                                                 max_tokens=entry["max_tokens"])
            check = entry["check"]
            reasons = []
            for pattern in check.get("regex_all", ()):
                if not re.search(pattern, visible):
                    reasons.append("missing:" + pattern)
            if "min_keywords" in check:
                need, keywords = check["min_keywords"]
                if sum(1 for k in keywords if k in visible.lower()) < need:
                    reasons.append("keywords")
            words = re.findall(r"\w+", visible.lower())
            if "words_between" in check:
                low, high = check["words_between"]
                if not low <= len(words) <= high:
                    reasons.append(f"word_count:{len(words)}")
            if "distinct_trigram_min" in check:
                trigrams = list(zip(words, words[1:], words[2:]))
                ratio = len(set(trigrams)) / len(trigrams) if trigrams else 0.0
                record["distinct_trigram_ratio"] = round(ratio, 4)
                if ratio < check["distinct_trigram_min"]:
                    reasons.append("repetitive")
            if "max_word_run" in check:
                run = longest = 1
                for a, b in zip(words, words[1:]):
                    run = run + 1 if a == b else 1
                    longest = max(longest, run)
                if words and longest > check["max_word_run"]:
                    reasons.append("word_run")
            if check.get("reasoning_closed") and "reasoning_unclosed" in record["flags"]:
                reasons.append("reasoning_unclosed")
            if "finish_length" in record["flags"]:
                reasons.append("finish_length")
            if "reasoning_tag_with_thinking_off" in record["flags"]:
                reasons.append("reasoning_tag_with_thinking_off")
            record.update({"id": entry["id"], "thinking": thinking, "pass": not reasons, "reasons": reasons})
            records.append(record)
            self.log(f"coherence {entry['id']}: pass={not reasons} {reasons}")
        return self._summarize("coherence", records,
                               benchmark_threshold("coherence", len(records), self.config.profile))

    # -- math -------------------------------------------------------------
    def run_math(self) -> dict[str, Any]:
        thinking = self.config.math_thinking
        max_tokens = self.config.max_tokens_math_thinking if thinking else self.config.max_tokens_math
        records = []
        for entry in self._limited(self.items["math"]):
            question = entry["question"] + "\nPlease reason step by step, and put your final answer within \\boxed{}."
            _, _, visible, record, _ = self.chat([{"role": "user", "content": question}], thinking=thinking,
                                                 max_tokens=max_tokens)
            value, how = extract_math_answer(visible)
            expected = float(entry["answer"])
            ok = value is not None and abs(value - expected) <= 1e-6 * max(1.0, abs(expected))
            record.update({"id": entry["id"], "expected": entry["answer"], "extracted": value,
                           "extraction": how, "pass": ok})
            records.append(record)
            self.log(f"math {entry['id']}: pass={ok} got={value} want={entry['answer']}")
        return self._summarize("math", records, benchmark_threshold("math", len(records), self.config.profile,
                                                                     thinking=thinking))

    # -- ifeval -----------------------------------------------------------
    def run_ifeval(self) -> dict[str, Any]:
        thinking = self.config.ifeval_thinking
        records = []
        instruction_total = instruction_ok = 0
        for entry in self._limited(self.items["ifeval"]):
            _, _, visible, record, _ = self.chat([{"role": "user", "content": entry["prompt"]}], thinking=thinking,
                                                 max_tokens=self.config.max_tokens_ifeval)
            followed = ifeval_follow(visible, entry["instruction_id_list"], entry["kwargs"])
            instruction_total += len(followed)
            instruction_ok += sum(followed)
            record.update({"id": entry["id"], "instructions": dict(zip(entry["instruction_id_list"], followed)),
                           "pass": all(followed)})
            if any(i.startswith("change_case:english") for i in entry["instruction_id_list"]):
                record["flags"].append("langdetect_not_applied")
            records.append(record)
            self.log(f"ifeval {entry['id']}: pass={all(followed)}")
        summary = self._summarize("ifeval", records, benchmark_threshold("ifeval", len(records), self.config.profile))
        summary["instruction_level_accuracy"] = round(instruction_ok / instruction_total, 4) if instruction_total else None
        return summary

    # -- toolcall ---------------------------------------------------------
    def run_toolcall(self) -> dict[str, Any]:
        thinking = self.config.toolcall_thinking
        records = []
        for entry in self._limited(self.items["toolcall"]):
            _, _, visible, record, _ = self.chat(entry["messages"], entry["tools"], thinking=thinking,
                                                 max_tokens=self.config.max_tokens_toolcall)
            prefix, calls, flags = parse_tool_calls(visible, entry["tools"])
            record["flags"].extend(flags)
            reasons = []
            if any(f.startswith("malformed_tool_call") for f in flags):
                reasons.append("malformed")
            if entry["expected_calls"]:
                if not calls_match(calls, entry["expected_calls"], entry["omit_sentinel"]):
                    reasons.append("call_mismatch")
            else:
                if calls:
                    reasons.append("unexpected_call")
                for needle in entry.get("must_contain", ()):
                    if needle.lower() not in visible.lower():
                        reasons.append("missing:" + needle)
            if "finish_length" in record["flags"]:
                reasons.append("finish_length")
            # Round trip of our own rendering: re-render the parsed calls as an
            # assistant turn and re-parse; must be the identity.
            if calls:
                echo = self.template.render(
                    [{"role": "user", "content": "x"},
                     {"role": "assistant", "content": "", "tool_calls": [{"type": "function", "function": c} for c in calls]}],
                    entry["tools"], add_generation_prompt=False)
                tail = echo.split("</think>\n\n", 1)[-1].removesuffix("<|im_end|>\n")
                _, reparsed, _ = parse_tool_calls(tail, entry["tools"])
                if reparsed != calls:
                    reasons.append("template_roundtrip_mismatch")
            record.update({"id": entry["id"], "category": entry["category"], "calls": calls,
                           "pass": not reasons, "reasons": reasons})
            records.append(record)
            self.log(f"toolcall {entry['id']}: pass={not reasons} {reasons}")
        summary = self._summarize("toolcall", records,
                                  benchmark_threshold("toolcall", len(records), self.config.profile))
        by_category: dict[str, list[int]] = {}
        for record in records:
            by_category.setdefault(record["category"], [0, 0])
            by_category[record["category"]][0] += int(record["pass"])
            by_category[record["category"]][1] += 1
        summary["by_category"] = {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_category.items())}
        return summary


# --------------------------------------------------------------------------
# SHADE-Arena smoke through the ALIGN kit's run_episode
# --------------------------------------------------------------------------

class ShadeUnavailable(RuntimeError):
    pass


def import_align(checkout: Path):
    """Import joulewise.align from an ALIGN checkout (this branch has no ALIGN
    kit). The harness itself never imports joulewise, so the checkout's
    package is the only one; a pre-imported foreign joulewise is refused."""
    checkout = checkout.resolve()
    loaded = sys.modules.get("joulewise")
    if loaded is not None:
        origin = Path(getattr(loaded, "__file__", "") or "").resolve()
        if checkout not in origin.parents:
            raise ShadeUnavailable(f"joulewise already imported from {origin}; run the shade stage in a fresh process")
    if not (checkout / "joulewise" / "align" / "runner.py").exists():
        raise ShadeUnavailable(f"{checkout} has no joulewise/align/runner.py")
    sys.path.insert(0, str(checkout))
    interfaces = importlib.import_module("joulewise.align.interfaces")
    runner = importlib.import_module("joulewise.align.runner")
    shade = importlib.import_module("joulewise.align.shade")
    upstream = importlib.import_module("joulewise.align.shade.upstream")
    if checkout not in Path(runner.__file__).resolve().parents:
        raise ShadeUnavailable("joulewise.align resolved outside the ALIGN checkout")
    return interfaces, runner, shade, upstream


class AdapterChatEndpoint:
    """ALIGN ChatEndpoint over a generate() adapter and the real template.

    The runner's history is: system, user, assistant text, then for each call
    an assistant message (content = arguments JSON, name, tool_call_id) and a
    tool message. That history is folded back into template messages with
    ``tool_calls`` so the model sees exactly the official XML rendering.
    """

    def __init__(self, harness: Harness, interfaces: Any, *, thinking: bool) -> None:
        self.harness = harness
        self.interfaces = interfaces
        self.thinking = thinking
        self.identity = "qwen4exp-e2e:" + str(getattr(harness.adapter, "identity", type(harness.adapter).__name__))
        self.turn_flags: list[list[str]] = []

    def _messages(self, history) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = []
        for message in history:
            if message.role == "assistant" and message.tool_call_id is not None:
                if not messages or messages[-1]["role"] != "assistant":
                    messages.append({"role": "assistant", "content": ""})
                # run_episode stores the call's arguments JSON as the content.
                messages[-1].setdefault("tool_calls", []).append(
                    {"type": "function", "function": {"name": message.name,
                                                      "arguments": json.loads(message.content)}})
            elif message.role == "tool":
                messages.append({"role": "tool", "content": message.content})
            else:
                messages.append({"role": message.role, "content": message.content})
        return messages

    def chat(self, messages, *, tools=(), max_tokens, temperature, seed):
        start = time.monotonic_ns()
        flags = [] if temperature == 0 else ["temperature_ignored_greedy_only"]
        generation, reasoning, visible, record, prompt_ids = self.harness.chat(
            self._messages(messages), list(tools) or None, thinking=self.thinking, max_tokens=max_tokens)
        prefix, calls, parse_flags = parse_tool_calls(visible, list(tools))
        flags.extend(record["flags"] + parse_flags)
        self.turn_flags.append(flags)
        requests = []
        for index, call in enumerate(calls):
            arguments_json = json.dumps(call["arguments"], separators=(",", ":"), ensure_ascii=False)
            call_id = hashlib.sha256(f"{index}\0{call['name']}\0{arguments_json}".encode()).hexdigest()
            requests.append(self.interfaces.ToolCallRequest(call_id, call["name"], arguments_json))
        end = time.monotonic_ns()
        think_close = SPECIAL_TOKENS["</think>"]
        reasoning_tokens = (generation.token_ids.index(think_close) if self.thinking and think_close in generation.token_ids
                            else (len(generation.token_ids) if self.thinking else 0))
        return self.interfaces.ChatResult(
            content=prefix.strip() if calls else visible, reasoning_text=reasoning, tool_calls=tuple(requests),
            prompt_tokens=len(prompt_ids), cached_prompt_tokens=0, completion_tokens=len(generation.token_ids),
            reasoning_tokens=reasoning_tokens, start_ns=start, first_token_ns=None, end_ns=end,
            raw_usage={"joulewise": {"flags": flags, "finish_reason": generation.finish_reason}})


def fixture_upstream(upstream_module: Any, fixture_dir: Path, workdir: Path):
    """Commit an original SHADE-shaped fixture into a local pinned cache, the
    way tests/align/test_shade.py does, so the production verifier runs."""
    import shutil
    import subprocess

    def git(root, *args, data=None):
        return subprocess.run(["git", "-C", str(root), *args], input=data, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    staging = workdir / "source"
    shutil.copytree(fixture_dir, staging, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    git(staging, "init", "--quiet")
    for key, value in (("maintenance.auto", "false"), ("gc.auto", "0")):
        git(staging, "config", "--local", key, value)
    git(staging, "add", "--all")
    tree = git(staging, "write-tree").decode().strip()
    data = ("tree " + tree + "\nauthor Fixture <> 0 +0000\ncommitter Fixture <> 0 +0000\n\nSynthetic source.\n").encode()
    commit = git(staging, "hash-object", "-t", "commit", "-w", "--stdin", data=data).decode().strip()
    git(staging, "update-ref", "HEAD", commit)
    root = workdir / commit
    staging.rename(root)
    return upstream_module.PinnedUpstream(workdir, commit=commit, file_sha256=upstream_module.file_list_sha256(root),
                                          allow_fetch=False)


def run_shade_smoke(harness: Harness, *, align_checkout: Path, task_pair: str, fixture_dir: Path | None,
                    max_turns: int, max_tokens: int, thinking: bool, seed: int = 1) -> dict[str, Any]:
    import tempfile
    try:
        interfaces, runner, shade, upstream_module = import_align(align_checkout)
    except (ShadeUnavailable, ImportError) as exc:
        return {"stage": "shade", "verdict": "skipped", "reason": f"{type(exc).__name__}: {exc}"}
    with tempfile.TemporaryDirectory(prefix="qwen4exp-shade-") as workdir:
        upstream = (fixture_upstream(upstream_module, fixture_dir, Path(workdir)) if fixture_dir
                    else upstream_module.PinnedUpstream(allow_fetch=False))
        task = shade.ShadeTask(task_pair, upstream=upstream)
        endpoint = AdapterChatEndpoint(harness, interfaces, thinking=thinking)
        episode, transcript = runner.run_episode(task, "benign", endpoint, seed=seed, max_turns=max_turns,
                                                 max_tokens=max_tokens, temperature=0.0,
                                                 clock_domain="monotonic_ns")
        try:
            score_main = task.score_main(transcript)
        except Exception as exc:  # scoring is informational for a smoke
            score_main = f"error:{type(exc).__name__}"
    flags = list(episode.flags) if hasattr(episode, "flags") else []
    tool_calls = [call for turn in episode.turns for call in turn.tool_calls]
    tool_errors = [f for f in flags if f.startswith("tool.error.")]
    fatal = [f for f in flags if f.startswith(("task.setup_error.", "endpoint.error.", "runner.error."))]
    malformed_turns = sum(1 for turn_flags in endpoint.turn_flags
                          if any(f.startswith("malformed_tool_call") for f in turn_flags))
    ended = any(f.startswith("episode.end_task") for f in flags)
    checks = [
        {"check": "no setup/endpoint/runner errors", "ok": not fatal},
        {"check": "at least one tool call executed", "ok": bool(tool_calls)},
        {"check": "malformed tool-call turns <= 1", "ok": malformed_turns <= 1},
        {"check": "end_task called, or >= 3 successful calls by max_turns",
         "ok": ended or (len(tool_calls) - len(tool_errors) >= 3)},
    ]
    return {"stage": "shade", "verdict": "pass" if all(c["ok"] for c in checks) else "fail",
            "task_pair": task.task_pair, "fixture": bool(fixture_dir), "thinking": thinking,
            "turns": len(episode.turns), "tool_calls": [c.name for c in tool_calls],
            "malformed_turns": malformed_turns, "ended_by_end_task": ended,
            "score_main": score_main, "episode_flags": flags, "checks": checks,
            "align_runner": str(Path(runner.__file__).resolve())}


# --------------------------------------------------------------------------
# Adapters
# --------------------------------------------------------------------------

def _bytes_to_unicode() -> dict[int, str]:
    """GPT-2 byte-level BPE table (Qwen2Tokenizer uses the same mapping)."""
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("\xa1"), ord("\xac") + 1)) + list(range(ord("\xae"), ord("\xff") + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return dict(zip(bs, map(chr, cs)))


BYTE_DECODER = {v: k for k, v in _bytes_to_unicode().items()}


class MlxAdapter:
    """Pinned mlx-lm 0.31.3 adapter. Greedy, batch 1, unquantized KV cache.

    ``load`` goes through ``mlx_lm.utils.load``; a ``model_file`` is passed as
    ``model_config={"model_file": ...}`` (the GOAL's no-pin-bump hook), which
    load_model resolves relative to the model directory.
    """

    def __init__(self, model: Any, tokenizer: Any, *, identity: str, prefill_step: int = 2048,
                 score_chunk: int = 256) -> None:
        self.model, self.tokenizer, self.identity = model, tokenizer, identity
        self.prefill_step, self.score_chunk = prefill_step, score_chunk
        self._special = None

    @classmethod
    def load(cls, model_path: str, *, model_file: str | None = None, lazy: bool = False, **kwargs: Any) -> "MlxAdapter":
        from mlx_lm.utils import load
        config = {"model_file": model_file} if model_file else None
        model, tokenizer = load(model_path, model_config=config, lazy=lazy)
        path = Path(model_path)
        digests = {name: sha256_file(path / name) for name in ("config.json", model_file or "")
                   if name and (path / name).exists()}
        identity = f"mlx:{path.name}:" + ",".join(f"{k}={v[:12]}" for k, v in sorted(digests.items()))
        return cls(model, tokenizer, identity=identity, **kwargs)

    @property
    def vocab_size(self) -> int:
        return int(getattr(self.tokenizer, "vocab_size", VOCAB_SIZE))

    def encode(self, text: str) -> list[int]:
        return list(self.tokenizer.encode(text, add_special_tokens=False))

    def decode(self, ids: Sequence[int]) -> str:
        return self.tokenizer.decode(list(ids))

    def token_bytes(self, token_id: int) -> bytes:
        if self._special is None:
            added = getattr(self.tokenizer, "added_tokens_decoder", {}) or {}
            self._special = {int(i): getattr(t, "content", str(t)) for i, t in added.items()}
        if token_id in self._special:
            return self._special[token_id].encode("utf-8")
        piece = self.tokenizer.convert_ids_to_tokens(int(token_id))
        return bytes(BYTE_DECODER[ch] for ch in piece)

    @staticmethod
    def _topk(mx: Any, row: Any, k: int) -> list[tuple[int, float]]:
        if k <= 0:
            return []
        idx = mx.argpartition(-row, kth=k - 1)[:k]
        vals = row[idx]
        pairs = sorted(zip(idx.tolist(), vals.tolist()), key=lambda p: (-p[1], p[0]))
        return [(int(i), float(v)) for i, v in pairs]

    def generate(self, prompt_ids: Sequence[int], *, max_tokens: int, stop_ids: Sequence[int] = EOS_IDS,
                 top_k: int = 0) -> Generation:
        import mlx.core as mx
        from mlx_lm.generate import generate_step
        started = time.perf_counter()
        ids: list[int] = []
        lps: list[float] = []
        tops: list[list[tuple[int, float]]] = []
        finish = "length"
        stops = set(stop_ids)
        for token, logprobs in generate_step(mx.array(list(prompt_ids)), self.model, max_tokens=max_tokens,
                                             prefill_step_size=self.prefill_step):
            row = logprobs.astype(mx.float32)
            ids.append(int(token))
            lps.append(float(row[int(token)].item()))
            tops.append(self._topk(mx, row, max(top_k, 0)))
            if int(token) in stops:
                finish = "stop"
                break
        return Generation(ids, self.decode(ids), finish, lps, tops if top_k else None,
                          len(prompt_ids), time.perf_counter() - started)

    def score(self, prompt_ids: Sequence[int], continuation_ids: Sequence[int], *, top_k: int = 0,
              query_ids: Sequence[Sequence[int]] | None = None) -> Scored:
        import mlx.core as mx
        from mlx_lm.models.cache import make_prompt_cache
        if not prompt_ids:
            raise ValueError("score() needs at least one prompt token")
        cache = make_prompt_cache(self.model)
        sequence = list(prompt_ids) + list(continuation_ids)
        head = sequence[: len(prompt_ids) - 1]
        for start in range(0, len(head), self.prefill_step):
            self.model(mx.array(head[start:start + self.prefill_step])[None], cache=cache)
            try:  # as generate_step does; a port cache without .state is evaluated lazily instead
                mx.eval([c.state for c in cache])
            except (AttributeError, TypeError, ValueError):
                pass
        inputs = sequence[len(prompt_ids) - 1: -1]
        targets = list(continuation_ids)
        chosen: list[float] = []
        argmax: list[int] = []
        tops: list[list[tuple[int, float]]] = []
        queries: list[dict[int, float]] = []
        normalizers: list[float] = []
        for start in range(0, len(inputs), self.score_chunk):
            logits = self.model(mx.array(inputs[start:start + self.score_chunk])[None], cache=cache)[0]
            rows = logits.astype(mx.float32)
            norms = mx.logsumexp(rows, axis=-1)
            rows = rows - norms[:, None]
            chunk_targets = mx.array(targets[start:start + self.score_chunk])
            picked = mx.take_along_axis(rows, chunk_targets[:, None], axis=-1)[:, 0]
            best = mx.argmax(rows, axis=-1)
            mx.eval(rows, picked, best, norms)
            normalizers.extend(float(x) for x in norms.tolist())
            chosen.extend(float(x) for x in picked.tolist())
            argmax.extend(int(x) for x in best.tolist())
            for offset in range(rows.shape[0]):
                if top_k:
                    tops.append(self._topk(mx, rows[offset], top_k))
                if query_ids is not None:
                    wanted = [int(i) for i in query_ids[start + offset]]
                    values = rows[offset][mx.array(wanted)].tolist() if wanted else []
                    queries.append(dict(zip(wanted, (float(v) for v in values))))
        return Scored(chosen, argmax, tops if top_k else None,
                      queries if query_ids is not None else None, normalizers)


class TransformersAdapter:
    """Official-reference adapter: any transformers causal LM (for qwen4_exp,
    transformers 5.22.1 ``Qwen4ExpForCausalLM``), greedy, batch 1, the model's
    own cache. Same contract as MlxAdapter, so a reference run's results JSON
    can be passed to ``--reference``. The full model does not fit in laptop or
    Mac memory; use it on tiny configs, or wrap it in a layer-streaming loader
    (GOAL item 11) through ``--adapter module:callable``.
    """

    def __init__(self, model: Any, tokenizer: Any, *, identity: str, prefill_step: int = 2048,
                 score_chunk: int = 256) -> None:
        self.model, self.tokenizer, self.identity = model, tokenizer, identity
        self.prefill_step, self.score_chunk = prefill_step, score_chunk
        self._special = None

    vocab_size = property(lambda self: int(getattr(self.tokenizer, "vocab_size", VOCAB_SIZE)))
    encode = MlxAdapter.encode
    decode = MlxAdapter.decode
    token_bytes = MlxAdapter.token_bytes

    def _step(self, ids: Sequence[int], cache: Any) -> tuple[Any, Any]:
        import torch
        with torch.no_grad():
            out = self.model(input_ids=torch.tensor([list(ids)], dtype=torch.long), past_key_values=cache,
                             use_cache=True)
        return out.logits[0].float(), out.past_key_values

    @staticmethod
    def _topk(row: Any, k: int) -> list[tuple[int, float]]:
        if k <= 0:
            return []
        values, indices = row.topk(k)
        return [(int(i), float(v)) for i, v in zip(indices.tolist(), values.tolist())]

    def generate(self, prompt_ids: Sequence[int], *, max_tokens: int, stop_ids: Sequence[int] = EOS_IDS,
                 top_k: int = 0) -> Generation:
        started = time.perf_counter()
        cache, logits = None, None
        for start in range(0, len(prompt_ids), self.prefill_step):
            logits, cache = self._step(prompt_ids[start:start + self.prefill_step], cache)
        ids: list[int] = []
        lps: list[float] = []
        tops: list[list[tuple[int, float]]] = []
        finish, stops = "length", set(stop_ids)
        for _ in range(max_tokens):
            row = logits[-1].log_softmax(-1)
            token = int(row.argmax())
            ids.append(token)
            lps.append(float(row[token]))
            tops.append(self._topk(row, top_k))
            if token in stops:
                finish = "stop"
                break
            logits, cache = self._step([token], cache)
        return Generation(ids, self.decode(ids), finish, lps, tops if top_k else None, len(prompt_ids),
                          time.perf_counter() - started)

    def score(self, prompt_ids: Sequence[int], continuation_ids: Sequence[int], *, top_k: int = 0,
              query_ids: Sequence[Sequence[int]] | None = None) -> Scored:
        if not prompt_ids:
            raise ValueError("score() needs at least one prompt token")
        sequence = list(prompt_ids) + list(continuation_ids)
        head = sequence[: len(prompt_ids) - 1]
        cache = None
        for start in range(0, len(head), self.prefill_step):
            _, cache = self._step(head[start:start + self.prefill_step], cache)
        inputs, targets = sequence[len(prompt_ids) - 1: -1], list(continuation_ids)
        chosen: list[float] = []
        argmax: list[int] = []
        tops: list[list[tuple[int, float]]] = []
        queries: list[dict[int, float]] = []
        normalizers: list[float] = []
        for start in range(0, len(inputs), self.score_chunk):
            logits, cache = self._step(inputs[start:start + self.score_chunk], cache)
            norms = logits.float().logsumexp(-1)
            rows = logits.log_softmax(-1)
            normalizers.extend(float(value) for value in norms.tolist())
            for offset in range(rows.shape[0]):
                row, target = rows[offset], targets[start + offset]
                chosen.append(float(row[target]))
                argmax.append(int(row.argmax()))
                if top_k:
                    tops.append(self._topk(row, top_k))
                if query_ids is not None:
                    queries.append({int(q): float(row[int(q)]) for q in query_ids[start + offset]})
        return Scored(chosen, argmax, tops if top_k else None,
                      queries if query_ids is not None else None, normalizers)


class ScriptedAdapter:
    """Deterministic stub for dry runs and tests (no model).

    Tokens are Unicode code points, except the special tokens, which map to
    their real ids. ``responses`` maps a regex (searched against the rendered
    prompt) to the completion text; the first match wins; the completion is
    followed by <|im_end|>. ``memory`` texts get a high-probability score so
    the NLL control behaves like a model that knows the natural texts.
    """

    def __init__(self, responses: Sequence[tuple[str, str]], *, memory: Sequence[str] = (),
                 identity: str = "scripted-stub", default: str = "I am not sure.") -> None:
        self.responses = [(re.compile(pattern, re.S), text) for pattern, text in responses]
        self.memory = list(memory)
        self.identity = identity
        self.default = default
        self.vocab_size = 0x110000
        self._special = sorted(SPECIAL_TOKENS.items(), key=lambda kv: -len(kv[0]))
        self._by_id = {v: k for k, v in SPECIAL_TOKENS.items()}

    @classmethod
    def from_file(cls, path: str) -> "ScriptedAdapter":
        spec = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls([tuple(pair) for pair in spec["responses"]], memory=spec.get("memory", ()),
                   identity=spec.get("identity", "scripted-stub:" + Path(path).name),
                   default=spec.get("default", "I am not sure."))

    def encode(self, text: str) -> list[int]:
        ids, i = [], 0
        while i < len(text):
            for token, token_id in self._special:
                if text.startswith(token, i):
                    ids.append(token_id)
                    i += len(token)
                    break
            else:
                ids.append(ord(text[i]))
                i += 1
        return ids

    def decode(self, ids: Sequence[int]) -> str:
        return "".join(self._by_id.get(i) or chr(i) for i in ids)

    def token_bytes(self, token_id: int) -> bytes:
        return self.decode([token_id]).encode("utf-8")

    def token_id_for_bytes(self, data: bytes) -> int | None:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            return None
        if text in SPECIAL_TOKENS:
            return SPECIAL_TOKENS[text]
        return ord(text) if len(text) == 1 else None

    def _completion(self, prompt: str) -> str:
        for pattern, text in self.responses:
            if pattern.search(prompt):
                return text
        return self.default

    def generate(self, prompt_ids, *, max_tokens, stop_ids=EOS_IDS, top_k=0) -> Generation:
        prompt = self.decode(prompt_ids)
        ids = self.encode(self._completion(prompt)) + [SPECIAL_TOKENS["<|im_end|>"]]
        finish = "stop"
        if len(ids) > max_tokens:
            ids, finish = ids[:max_tokens], "length"
        lps = [math.log(0.9)] * len(ids)
        tops = [[(t, math.log(0.9)), (self._alt(t), math.log(0.05))] for t in ids] if top_k else None
        return Generation(ids, self.decode(ids), finish, lps, tops, len(prompt_ids), 0.001)

    @staticmethod
    def _alt(token: int) -> int:
        """The stub's runner-up token: a space (or '!' when the token is a space)."""
        return 33 if token == 32 else 32

    def _known_prefix(self, continuation_ids: Sequence[int], prompt_ids: Sequence[int]) -> tuple[int, float]:
        """Leading tokens of the continuation this stub 'knows', and their logprob.

        Its own scripted completion for the prompt scores exactly as generate()
        reported it (so prefill and stepwise agree); otherwise a memory text
        that the continuation starts with scores 0.8 per token.
        """
        own = self.encode(self._completion(self.decode(prompt_ids))) + [SPECIAL_TOKENS["<|im_end|>"]]
        best, value = 0, math.log(0.8)
        length = 0
        while length < min(len(own), len(continuation_ids)) and own[length] == continuation_ids[length]:
            length += 1
        if length:
            best, value = length, math.log(0.9)
        for text in self.memory:
            ids = self.encode(text)
            length = 0
            while length < min(len(ids), len(continuation_ids)) and ids[length] == continuation_ids[length]:
                length += 1
            if length > best:
                best, value = length, math.log(0.8)
        return best, value

    def score(self, prompt_ids, continuation_ids, *, top_k=0, query_ids=None) -> Scored:
        known, hit_lp = self._known_prefix(list(continuation_ids), list(prompt_ids))
        lps, argmax, tops, queries = [], [], [], []
        # Stub distribution: at known positions the token gets hit_lp and the
        # runner-up 0.05; elsewhere the runner-up is the confident argmax.
        for index, token in enumerate(continuation_ids):
            hit = index < known
            alt = self._alt(token)
            lp = hit_lp if hit else math.log(1e-4)
            alt_lp = math.log(0.05) if hit else math.log(0.8)
            lps.append(lp)
            argmax.append(token if hit else alt)
            if top_k:
                tops.append([(token, lp), (alt, alt_lp)] if hit else [(alt, alt_lp), (token, lp)])
            if query_ids is not None:
                queries.append({int(q): (lp if q == token else alt_lp if q == alt else math.log(1e-3))
                                for q in query_ids[index]})
        return Scored(lps, argmax, tops if top_k else None, queries if query_ids is not None else None)


def build_adapter(args: argparse.Namespace) -> Any:
    spec = args.adapter
    if spec == "mlx":
        if not args.model:
            raise SystemExit("--adapter mlx needs --model")
        return MlxAdapter.load(args.model, model_file=args.model_file, lazy=args.lazy,
                               prefill_step=args.prefill_step, score_chunk=args.score_chunk)
    if spec.startswith("scripted:"):
        return ScriptedAdapter.from_file(spec.split(":", 1)[1])
    if ":" in spec:
        module_name, attr = spec.split(":", 1)
        return getattr(importlib.import_module(module_name), attr)(args)
    raise SystemExit(f"unknown adapter {spec!r}")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def environment_record(adapter: Any) -> dict[str, Any]:
    record = {"python": sys.version.split()[0], "platform": platform.platform(),
              "adapter_identity": getattr(adapter, "identity", type(adapter).__name__)}
    # Only modules the run already imported; recording must not load MLX.
    for module in ("mlx.core", "mlx_lm", "jinja2", "transformers", "torch"):
        loaded = sys.modules.get(module)
        if loaded is not None:
            record[module] = getattr(loaded, "__version__", "unknown")
    return record


def tokenizer_preflight(adapter: Any) -> dict[str, Any]:
    """Each template control token must encode to its single official id, and
    decode back, or the rendered prompts and EOS_IDS mean something else."""
    mismatches = {}
    for text, token_id in SPECIAL_TOKENS.items():
        encoded = list(adapter.encode(text))
        if encoded != [token_id] or adapter.decode([token_id]) != text:
            mismatches[text] = {"encoded": encoded[:8], "expected": token_id}
    return {"ok": not mismatches, "mismatches": mismatches, "checked": len(SPECIAL_TOKENS)}


def run(args: argparse.Namespace, adapter: Any | None = None, log: Callable[[str], None] | None = None) -> dict[str, Any]:
    items = load_items(Path(args.items))
    template = ChatTemplate(Path(args.chat_template) if args.chat_template else None,
                            allow_unpinned=args.allow_unpinned_template)
    adapter = adapter or build_adapter(args)
    config = RunConfig(profile=args.quant_profile, math_thinking=args.math_thinking,
                       ifeval_thinking=args.ifeval_thinking, toolcall_thinking=args.toolcall_thinking,
                       reasoning_effort=args.reasoning_effort, limit=args.limit)
    harness = Harness(adapter, template, items, config, log=log)
    reference = json.loads(Path(args.reference).read_text()) if args.reference else None
    stages = [s.strip() for s in args.stages.split(",") if s.strip()]
    unknown = set(stages) - set(STAGES)
    if unknown:
        raise SystemExit(f"unknown stages {sorted(unknown)}")
    results: dict[str, Any] = {
        "harness": HARNESS_VERSION, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "items_sha256": items["_file_sha256"], "template": {"path": str(template.path), "sha256": template.sha256,
                                                             "pinned": template.pinned},
        "quant_profile": args.quant_profile, "thresholds": THRESHOLDS, "config": asdict(config),
        "environment": environment_record(adapter), "stages": {},
    }
    preflight = tokenizer_preflight(adapter)
    results["tokenizer_preflight"] = preflight
    if not preflight["ok"]:
        # The template's control tokens and the stop ids would not mean what
        # the harness assumes; every downstream number would be uninterpretable.
        results["verdict"] = "fail"
        return results
    for stage in stages:
        started = time.perf_counter()
        if stage == "consistency":
            result = harness.run_consistency()
        elif stage == "nll":
            ref = reference["stages"].get("nll") if reference else None
            result = harness.run_nll(ref)
        elif stage == "coherence":
            result = harness.run_coherence()
        elif stage == "math":
            result = harness.run_math()
        elif stage == "ifeval":
            result = harness.run_ifeval()
        elif stage == "toolcall":
            result = harness.run_toolcall()
        else:
            if not args.align_checkout:
                result = {"stage": "shade", "verdict": "skipped",
                          "reason": "no --align-checkout (the ALIGN kit is not on this branch)"}
            else:
                result = run_shade_smoke(harness, align_checkout=Path(args.align_checkout),
                                         task_pair=args.shade_task,
                                         fixture_dir=Path(args.shade_fixture) if args.shade_fixture else None,
                                         max_turns=args.shade_max_turns, max_tokens=args.shade_max_tokens,
                                         thinking=args.shade_thinking)
        result["seconds"] = round(time.perf_counter() - started, 3)
        results["stages"][stage] = result
    if reference:
        results["reference_comparison"] = compare_to_reference(results, reference)
    verdicts = [r["verdict"] for r in results["stages"].values()]
    results["verdict"] = "fail" if "fail" in verdicts else ("pass" if "pass" in verdicts else "skipped")
    return results


def compare_to_reference(results: Mapping[str, Any], reference: Mapping[str, Any]) -> dict[str, Any]:
    """Per-item agreement with a reference run on the same items (for example
    a layer-streamed bf16 transformers adapter): identical greedy text and
    identical pass/fail, reported per stage (informational)."""
    out = {"reference_identity": reference.get("environment", {}).get("adapter_identity"),
           "reference_items_sha256": reference.get("items_sha256"),
           "same_items": reference.get("items_sha256") == results.get("items_sha256"), "stages": {}}
    for stage, result in results["stages"].items():
        ref = reference.get("stages", {}).get(stage)
        if not ref or "items" not in result or "items" not in ref:
            continue
        ref_items = {r["id"]: r for r in ref["items"]}
        same_text = same_pass = total = texts = 0
        for record in result["items"]:
            other = ref_items.get(record["id"])
            if other is None:
                continue
            total += 1
            if "visible" in record and "visible" in other:
                texts += 1
                same_text += int(record["visible"] == other["visible"])
            same_pass += int(record.get("pass") == other.get("pass"))
        out["stages"][stage] = {"compared": total, "texts_compared": texts, "identical_visible_text": same_text,
                                "same_pass": same_pass}
    return out


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="qwen4_exp end-to-end validation harness (GOAL item 7)")
    parser.add_argument("--adapter", default="mlx", help="mlx | scripted:FILE.json | module:callable")
    parser.add_argument("--model", help="model directory for --adapter mlx")
    parser.add_argument("--model-file", help="model_file hook (relative to --model), e.g. qwen4_exp.py")
    parser.add_argument("--lazy", action="store_true", help="lazy weight load (mlx)")
    parser.add_argument("--prefill-step", type=int, default=2048)
    parser.add_argument("--score-chunk", type=int, default=256)
    parser.add_argument("--items", default=str(ITEMS_PATH))
    parser.add_argument("--chat-template", help="defaults to .engine/hf-flashnext then the test fixture copy")
    parser.add_argument("--allow-unpinned-template", action="store_true")
    parser.add_argument("--quant-profile", default="bf16", choices=sorted(THRESHOLDS["profiles"]))
    parser.add_argument("--stages", default=",".join(s for s in STAGES if s != "shade"))
    parser.add_argument("--limit", type=int, help="first N items per stage (smoke runs; thresholds rescale)")
    parser.add_argument("--reasoning-effort", default="low", choices=("low", "medium", "xhigh"))
    parser.add_argument("--math-thinking", action="store_true")
    parser.add_argument("--ifeval-thinking", action="store_true")
    parser.add_argument("--toolcall-thinking", action="store_true")
    parser.add_argument("--reference", help="results JSON of a reference adapter on the same items")
    parser.add_argument("--align-checkout", help="checkout with joulewise/align (for --stages shade)")
    parser.add_argument("--shade-task", default="spam_filter_update")
    parser.add_argument("--shade-fixture", help="SHADE-shaped fixture directory (tests/dry runs)")
    parser.add_argument("--shade-max-turns", type=int, default=12)
    parser.add_argument("--shade-max-tokens", type=int, default=2048)
    parser.add_argument("--shade-thinking", action="store_true")
    parser.add_argument("--out", help="write results JSON here")
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    log = None if args.quiet else (lambda message: print(message, file=sys.stderr, flush=True))
    results = run(args, log=log)
    text = json.dumps(results, indent=1, ensure_ascii=False, default=str)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    summary = {stage: {k: r.get(k) for k in ("verdict", "passed", "n") if k in r}
               for stage, r in results["stages"].items()}
    print(json.dumps({"verdict": results["verdict"], "stages": summary}, indent=1))
    return 0 if results["verdict"] != "fail" else 1


if __name__ == "__main__":
    sys.exit(main())
