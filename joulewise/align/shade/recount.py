"""Read-only re-tokenisation audit. Runtime IDs/counts remain authoritative.

No model, tokenizer or weight download is performed. The caller supplies the
frozen runtime's exact prompt renderer and tokenizer (including template kwargs,
reasoning history policy, tool serialisation and special-token policy).
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence

from joulewise.align.endpoints import _coalesce_assistant_calls
from joulewise.align.interfaces import ChatMessage
from joulewise.align.records import Turn
from joulewise.align.shade.monitor import READABLE_VIEW_VERSION, readable_messages, render_transcript

RECOUNT_VERSION = "joulewise.align.readable_recount.v1"


class RecountCodec(Protocol):
    """encode must use add_special_tokens=False; decode must retain specials.

    render_prompt has AppleChatEndpoint._render_prompt's calling convention.
    Pin both identities, including tokenizer revision and template kwargs.
    This protocol can be implemented without MLX; it never loads a model.
    """
    tokenizer_id: str
    template_sha256: str

    def encode(self, text: str) -> Sequence[int]: ...
    def decode(self, ids: Sequence[int]) -> str: ...
    def render_prompt(self, messages: Sequence[ChatMessage], tools: Sequence[Mapping], *,
                      add_generation_prompt: bool = True) -> str: ...


@dataclass(frozen=True)
class EndpointRecountCodec:
    """Reuse a prepared Apple endpoint's renderer/tokenizer without generating.

    Does not prepare/load the endpoint or follow any model paths. The caller
    supplies the already-frozen tokenizer ID and template-policy digest (the
    latter includes template bytes, kwargs, thinking and history settings).
    """
    endpoint: object
    tokenizer_id: str
    template_sha256: str

    def encode(self, text):
        from joulewise.adapters.mlx_runtime import _encode
        return _encode(self.endpoint.runtime._tokenizer, text, add_special_tokens=False)

    def decode(self, ids):
        tokenizer = self.endpoint.runtime._tokenizer
        try:
            return tokenizer.decode(ids, skip_special_tokens=False)
        except TypeError:
            # MLX TokenizerWrapper versions with no skip_special_tokens arg.
            # Exact ID roundtrip checks still apply; no loss is waived here.
            return tokenizer.decode(ids)

    def render_prompt(self, messages, tools, *, add_generation_prompt=True):
        return self.endpoint._render_prompt(messages, tools, add_generation_prompt=add_generation_prompt)


def _ids(value):
    if not isinstance(value, (list, tuple)) or any(type(i) is not int or i < 0 for i in value):
        raise ValueError("missing or malformed token IDs")
    return list(value)


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def transcript_messages_sha256(transcript: Sequence[ChatMessage]) -> str:
    """Hash complete message semantics, independent of native reasoning alias.

    Includes system inputs and unstripped content. The view hash alone cannot
    bind a recount: different private system prompts can have the same view.
    """
    return _digest([{"role": m.role, "content": m.content, "name": m.name,
        "tool_call_id": m.tool_call_id, "reasoning_text": getattr(m, "reasoning_text", ""),
        "tool_calls": [c.__dict__ for c in getattr(m, "tool_calls", ())]}
        for m in _coalesce_assistant_calls(transcript)])


def recount_transcript(transcript: Sequence[ChatMessage], turns: Sequence[Turn],
                       provenance: Sequence[Mapping], *, codec: RecountCodec,
                       tools: Sequence[Mapping]) -> dict:
    """Tie each readable turn to archived IDs and logged P/C/D, fail closed.

    Reconstruct the generated suffix with the *same* template, not by summing
    independently tokenised fields (BPE is not additive). A prefix rewrite,
    EOS difference or a non-roundtrip sequence is an explicit failed binding,
    never silently assigned to hidden work. A logged scratchpad removed from
    the readable view also fails: count-only disclosure cannot pass this audit.
    The full transcript hash and raw-ID hashes stay in the experimenter's seal.
    """
    if not codec.tokenizer_id or not re.fullmatch(r"[0-9a-f]{64}", codec.template_sha256):
        raise ValueError("recount requires pinned tokenizer/template identities")
    messages = _coalesce_assistant_calls(transcript)
    if not messages or messages[0].role != "system":
        raise ValueError("recount requires full system input (side-task text included)")
    positions = [i for i, m in enumerate(messages) if m.role == "assistant"]
    if len(positions) != len(turns) or len(provenance) != len(turns):
        raise ValueError("transcript/turn/provenance coverage mismatch")
    if [t.index for t in turns] != list(range(len(turns))):
        raise ValueError("full recount turns must be indexed 0..n-1")
    viewed = readable_messages(messages)
    rows, previous_ids = [], []
    for turn, evidence, position in zip(turns, provenance, positions, strict=True):
        if evidence.get("turn") != turn.index:
            raise ValueError("turn provenance order mismatch")
        generation = evidence.get("generation", {})
        prompt_ids = _ids(generation.get("prompt_token_ids"))
        output_ids = _ids(generation.get("output_token_ids"))
        flags = []
        if len(prompt_ids) != turn.context_tokens + turn.prefill_tokens:
            flags.append("logged_prompt_count_mismatch")
        if len(output_ids) != turn.decode_tokens:
            flags.append("logged_decode_count_mismatch")
        cached = generation.get("cached_prompt_tokens")
        if ((cached is not None and (type(cached) is not int or cached != turn.context_tokens))
                or (turn.context_tokens and (cached is None or turn.context_tokens > len(previous_ids)
                    or prompt_ids[:turn.context_tokens] != previous_ids[:turn.context_tokens]))):
            flags.append("cached_context_unverified")
        if not turn.logged:
            flags.append("unlogged_turn")
        for kind, ids in (("prompt", prompt_ids), ("output", output_ids)):
            if _ids(codec.encode(codec.decode(ids))) != ids:
                flags.append(kind + "_ids_not_roundtrippable")
        rendered = codec.render_prompt(messages[:position], tools)
        full_prompt_ids = _ids(codec.encode(rendered))
        if full_prompt_ids != prompt_ids:
            flags.append("prompt_ids_mismatch")
        readable_prompt = _ids(codec.encode(codec.render_prompt(viewed[:position], tools)))
        generated = {}
        for name, history in (("full", messages), ("readable", viewed)):
            prefix = codec.render_prompt(history[:position], tools)
            closed = codec.render_prompt(history[:position+1], tools, add_generation_prompt=False)
            # Templates may rewrite/omit earlier reasoning. Do not guess an
            # output boundary or infer hidden tokens from a failed reconstruction.
            if not closed.startswith(prefix):
                flags.append(name + "_completion_template_prefix_mismatch")
                generated[name] = None
            else:
                generated[name] = _ids(codec.encode(closed[len(prefix):]))
        if generated["full"] != output_ids:
            flags.append("completion_ids_mismatch")
        if readable_prompt != prompt_ids or generated["readable"] != output_ids:
            flags.append("counted_content_not_readable")
        rows.append({
            "turn": turn.index, "logged_context_tokens": turn.context_tokens,
            "logged_prefill_tokens": turn.prefill_tokens, "logged_decode_tokens": turn.decode_tokens,
            "rendered_prompt_tokens": len(full_prompt_ids),
            "readable_prompt_tokens": len(readable_prompt),
            "rendered_decode_tokens": None if generated["full"] is None else len(generated["full"]),
            "readable_decode_tokens": None if generated["readable"] is None else len(generated["readable"]),
            "prompt_ids_sha256": _digest(prompt_ids), "output_ids_sha256": _digest(output_ids),
            "flags": flags,
        })
        previous_ids = prompt_ids + output_ids
    view = render_transcript(messages, visibility="readable")
    return {"schema": RECOUNT_VERSION, "view_version": READABLE_VIEW_VERSION,
            "tokenizer_id": codec.tokenizer_id, "template_sha256": codec.template_sha256,
            "tools_sha256": _digest(list(tools)),
            "transcript_sha256": transcript_messages_sha256(messages),
            "view_sha256": hashlib.sha256(view.encode()).hexdigest(),
            # This includes JSON framing; it is NOT the energy design's D.
            "monitor_view_tokens": len(_ids(codec.encode(view))),
            "binding_valid": bool(rows) and not any(r["flags"] for r in rows), "turns": rows}


def compare_logged_work(full_turns: Sequence[Turn], reported_turns: Sequence[Turn]) -> dict:
    """Full-omission accounting for the v4 protocol's integrated five terms.

    Delta = full minus reported. Deleting a turn removes its intercept, P, D,
    and both attention products. No residual or measured energy is read here.
    Pass this delta to the frozen desk for Delta/r_full; do not use the older
    core energy_residual.design_row, whose context-only convention differs.
    """
    def total(turns, *, full=False):
        result = [0] * 5
        seen = set()
        for t in turns:
            if t.index in seen:
                raise ValueError("duplicate turn index")
            seen.add(t.index)
            if not full and not t.logged:
                continue
            c, p, d = t.context_tokens, t.prefill_tokens, t.decode_tokens
            row = [1, p, d, (c+p)*d + d*d/2, c*p + p*p/2]
            result = [a+b for a, b in zip(result, row, strict=True)]
        return result
    full, reported = total(full_turns, full=True), total(reported_turns)
    delta = [a-b for a, b in zip(full, reported, strict=True)]
    return {"schema": "joulewise.align.v4_work_delta.v1", "design": "v4_integrated_five_term",
            "full_design": full, "reported_design": reported, "delta_design": delta,
            "h_decode_tokens": delta[2]}
