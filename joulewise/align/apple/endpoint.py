"""In-process ChatEndpoint using JouleWise's existing MLX generation machinery.

No server or second model copy is launched. The same prepared runtime, tokenizer,
stream_generate, sampler pin, detokenizer and phase events serve each agent turn.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import replace
from typing import Any, Mapping, Sequence

from joulewise.align.interfaces import ChatMessage, ChatResult, ToolCallRequest
from joulewise.align.apple.sampler import monotonic_ns, seconds_ns, stamp_mapping
from joulewise.clock import Clock
from joulewise.schemas import BenchmarkConfig, RuntimeBackend

_TOOL_CALL = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)


def parse_completion(
    text: str, *, reasoning_tokens: int = 0,
) -> tuple[str, str, tuple[ToolCallRequest, ...], tuple[str, ...]]:
    """Parse Qwen-style explicit tool envelopes; retain malformed text and flags.

    Tool schemas and tokenizer chat templates remain task/model owned. Unknown
    formats are visible text rather than silently invented tool invocations.
    """
    flags: list[str] = []
    reasoning = ""
    visible = text
    if "<think>" in text:
        before, _, rest = text.partition("<think>")
        hidden, close, after = rest.partition("</think>")
        if close:
            reasoning = hidden
            visible = before + after
        else:
            flags.append("unclosed_reasoning_span")
    calls: list[ToolCallRequest] = []
    for index, match in enumerate(_TOOL_CALL.finditer(visible)):
        try:
            obj = json.loads(match.group(1))
            name = obj["name"]
            if not isinstance(name, str):
                raise ValueError("tool name is not a string")
            arguments = obj.get("arguments", {})
            arguments_json = arguments if isinstance(arguments, str) else json.dumps(
                arguments, sort_keys=True, separators=(",", ":")
            )
            # Call ids are transcript identity, derived from emitted bytes and
            # ordinal; they are not randomness or a claim about upstream ids.
            call_id = hashlib.sha256(
                f"{index}\0{match.group(0)}".encode("utf-8")
            ).hexdigest()
            calls.append(ToolCallRequest(call_id, name, arguments_json))
        except (KeyError, TypeError, ValueError) as exc:
            flags.append(f"malformed_tool_call:{type(exc).__name__}")
    if reasoning and reasoning_tokens == 0:
        flags.append("reasoning_token_count_unavailable")
    return visible, reasoning, tuple(calls), tuple(flags)


class MlxEndpoint:
    """ChatEndpoint over a prepared MlxRuntimeAdapter or the existing mock runtime.

    The real adapter's sampler is pinned greedy. Nonzero requested temperature
    is recorded as a mismatch instead of changing the existing measurement path.
    Mock scripts replace response text only AFTER real mock generation ran.
    """

    def __init__(
        self, runtime: Any, config: BenchmarkConfig, clock: Clock, *,
        episode_domain: str, prepare_metadata: Mapping[str, Any] | None = None,
        mock_turns: Sequence[Mapping[str, Any]] = (),
    ) -> None:
        self.runtime = runtime
        self.config = config
        self.clock = clock
        self.episode_domain = episode_domain
        self.mock_turns = tuple(mock_turns)
        self.events: list[Any] = []
        self.turn_provenance: list[Mapping[str, Any]] = []
        self.flags: list[str] = []
        self._turn = 0
        prepared = dict(prepare_metadata or {})
        self.identity = json.dumps({
            "backend": config.hardware_target.runtime_backend.value,
            "execution": "in_process",
            "model": config.model.name,
            "source": config.model.source,
            "revision": config.model.revision,
            "mlx_version": prepared.get("mlx_version"),
            "mlx_lm_version": prepared.get("mlx_lm_version"),
            "model_artifact_identity": prepared.get("model_artifact_identity"),
        }, sort_keys=True)

    def chat(
        self, messages: Sequence[ChatMessage], *, tools: Sequence[Mapping[str, Any]] = (),
        max_tokens: int, temperature: float, seed: int | None,
    ) -> ChatResult:
        start_stamp = self.clock.stamp()
        start_ns = monotonic_ns(start_stamp)
        turn_index = self._turn
        self._turn += 1
        flags: list[str] = []
        if temperature != 0.0:
            # Existing workloads are pinned greedy; 0 is the exact sampler
            # identity, not a numerical comparison tolerance.
            flags.append("requested_temperature_differs_from_pinned_greedy")
        if seed is not None:
            flags.append("seed_recorded_greedy_generation")
        text = ""
        prompt_tokens = completion_tokens = reasoning_tokens = 0
        first_epoch: float | None = None
        provenance: Mapping[str, Any] = {}
        try:
            if self.config.hardware_target.runtime_backend == RuntimeBackend.MOCK:
                script = self.mock_turns[turn_index] if turn_index < len(self.mock_turns) else {}
                profile = replace(
                    self.config.workload_profile, name="align_turn",
                    prompt_text=None, dataset_ref=None, suite_manifest_ref=None,
                    suite_manifest_sha256=None, generator_sidecar_ref=None,
                    prompt_token_expectation=None,
                    prompt_tokens=int(script["prompt_tokens"]) if "prompt_tokens" in script else None,
                    output_tokens=int(script.get("completion_tokens", max_tokens)),
                )
                if profile.prompt_tokens is None:
                    profile = replace(profile, prompt_text=json.dumps(
                        [message.__dict__ for message in messages], sort_keys=True
                    ))
                result = self.runtime.run_workload(replace(self.config, workload_profile=profile))
                new_events = result.events
                text = str(script.get("content", result.output_artifacts.get("response.txt", "")))
                prompt_tokens = (result.token_count or 0) - (result.output_token_count or 0)
                completion_tokens = result.output_token_count or 0
                reasoning_tokens = int(script.get("reasoning_tokens", 0))
                if reasoning_tokens < 0 or reasoning_tokens > completion_tokens:
                    flags.append("mock_reasoning_count_outside_completion")
                    reasoning_tokens = 0
                provenance = result.workload_provenance or {}
                flags.append("synthetic_mock_runtime")
            else:
                from joulewise.adapters.mlx_runtime import _encode

                tokenizer = self.runtime._tokenizer

                def prepare_prompt():
                    rendered = tokenizer.apply_chat_template(
                        [
                            {
                                "role": message.role, "content": message.content,
                                **({"name": message.name} if message.name else {}),
                                **({"tool_call_id": message.tool_call_id} if message.tool_call_id else {}),
                            }
                            for message in messages
                        ],
                        tools=list(tools) or None, tokenize=False,
                        add_generation_prompt=True,
                    )
                    # Chat templates already contain their special tokens.
                    ids = _encode(tokenizer, rendered, add_special_tokens=False)
                    return ids, ids, rendered

                record = self.runtime._generate(
                    None, [], None, max_tokens, suppress_eos=False,
                    prepare_prompt=prepare_prompt,
                )
                text = record.text
                prompt_tokens = record.prompt_tokens
                completion_tokens = record.output_tokens
                new_events = record.events
                provenance = {
                    "sampler": record.sampler_provenance,
                    "prompt_token_ids_sha256": hashlib.sha256(
                        json.dumps(record.prompt_token_ids, separators=(",", ":")).encode("utf-8")
                    ).hexdigest(),
                    "output_token_ids": record.output_token_ids,
                    "stop_condition": record.stop_condition,
                }
                _, hidden, _, _ = parse_completion(text)
                if hidden:
                    # Retokenization is labelled because token boundaries at
                    # the reasoning delimiters need not match the stream.
                    reasoning_tokens = min(
                        completion_tokens, len(_encode(tokenizer, hidden, add_special_tokens=False))
                    )
                    flags.append("reasoning_tokens_retokenized")
            for event in new_events:
                self.events.append(replace(
                    event, metadata={**event.metadata, "align_turn_index": turn_index}
                ))
                if first_epoch is None and event.event_type == "token":
                    first_epoch = event.timestamp_s
        except Exception as exc:
            flags.append(f"endpoint_error:{type(exc).__name__}:{exc}")
        end_stamp = self.clock.stamp()
        end_ns = max(start_ns, monotonic_ns(end_stamp))
        mapping, _ = stamp_mapping(
            (start_stamp, end_stamp), episode_domain=self.episode_domain
        )
        first_ns = (
            seconds_ns(first_epoch) + mapping.offset_ns if first_epoch is not None else None
        )
        if first_ns is not None and not start_ns <= first_ns <= end_ns:
            flags.append("first_token_clock_outside_turn")
            first_ns = max(start_ns, min(end_ns, first_ns))
        visible, reasoning, calls, parse_flags = parse_completion(
            text, reasoning_tokens=reasoning_tokens
        )
        flags.extend(parse_flags)
        self.flags.extend(flags)
        self.turn_provenance.append({
            "turn": turn_index, "flags": flags, "generation": provenance,
            "start_stamp": start_stamp.__dict__, "end_stamp": end_stamp.__dict__,
            "clock_mapping": mapping.__dict__,
        })
        return ChatResult(
            content=visible, reasoning_text=reasoning, tool_calls=calls,
            prompt_tokens=prompt_tokens, cached_prompt_tokens=0,
            completion_tokens=completion_tokens, reasoning_tokens=reasoning_tokens,
            start_ns=start_ns, first_token_ns=first_ns, end_ns=end_ns,
            raw_usage={"flags": flags, "cache_policy": "full_prompt_each_turn", "raw_text": text},
        )
