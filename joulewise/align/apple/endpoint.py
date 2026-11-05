"""In-process ChatEndpoint using JouleWise's existing MLX generation machinery.

No server or second model copy is launched. The same prepared runtime, tokenizer,
stream_generate, sampler pin, detokenizer and phase events serve each agent turn.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, replace
from functools import wraps
from typing import Any, Mapping, Sequence

from joulewise.align.endpoints import _coalesce_assistant_calls
from joulewise.align.interfaces import ChatMessage, ChatResult, ToolCallRequest
from joulewise.align.apple.sampler import monotonic_ns, seconds_ns, stamp_mapping
from joulewise.align.apple.sampling import turn_seed
from joulewise.align.apple.xml_tool_calls import XML_MODEL_FAMILIES, parse_xml_calls
from joulewise.clock import Clock
from joulewise.schemas import BenchmarkConfig, RuntimeBackend


def reasoning_tokens_from_ids(tokenizer, output_ids, *, reasoning_open=False, split_at=None):
    """Count reasoning content in the emitted IDs; delimiters/EOS are not content.

    Only the fixed delimiters are encoded to locate their ID sequences. The
    generated text is never retokenized, including at native stop or length cut.
    """
    from joulewise.adapters.mlx_runtime import _encode
    opening = _encode(tokenizer, "<think>", add_special_tokens=False)
    closing = _encode(tokenizer, "</think>", add_special_tokens=False)
    ids = list(output_ids)
    eos = getattr(tokenizer, "eos_token_ids", None)
    if eos is None:
        eos = getattr(tokenizer, "eos_token_id", ())
    eos = {eos} if isinstance(eos, int) else set(eos or ())
    if ids and ids[-1] in eos:
        ids.pop()
    def first(sequence):
        return next((i for i in range(len(ids)) if ids[i:i+len(sequence)] == list(sequence)), len(ids)) if sequence else len(ids)
    # Some templates prefill the opening tag; a leading close in the emitted
    # IDs is also exact evidence that the initial content was reasoning.
    active = reasoning_open or first(closing) < first(opening)
    count, index = 0, 0
    cached_count = 0
    while index < len(ids):
        if opening and ids[index:index + len(opening)] == list(opening):
            active = True
            index += len(opening)
        elif closing and ids[index:index + len(closing)] == list(closing):
            active = False
            index += len(closing)
        else:
            count += int(active)
            cached_count += int(active and split_at is not None and index < split_at)
            index += 1
    return (cached_count, count - cached_count) if split_at is not None else count

_TOOL_CALL = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.DOTALL)


def _split_reasoning(text: str, *, stop_at_tool_call: bool = False) -> tuple[str, str, tuple[str, ...]]:
    """Separate reasoning, including an unclosed tail and a prefilled opener."""
    visible: list[str] = []
    hidden: list[str] = []
    flags: list[str] = []
    cursor = 0
    while cursor < len(text):
        opening = text.find("<think>", cursor)
        closing = text.find("</think>", cursor)
        if stop_at_tool_call:
            call = text.find("<tool_call>", cursor)
            if call >= 0 and (opening < 0 or call < opening) and (closing < 0 or call < closing):
                # XML arguments are literal strings. Reasoning delimiters in
                # a parameter value must survive the outer reasoning split.
                visible.append(text[cursor:])
                break
        if closing >= 0 and (opening < 0 or closing < opening):
            if cursor == 0:
                hidden.append(text[:closing])
                flags.append("reasoning_open_tag_prefilled_or_missing")
            else:
                visible.append(text[cursor:closing + len("</think>")])
                flags.append("unmatched_reasoning_close")
            cursor = closing + len("</think>")
        elif opening >= 0:
            visible.append(text[cursor:opening])
            closing = text.find("</think>", opening + len("<think>"))
            if closing < 0:
                hidden.append(text[opening + len("<think>"):])
                flags.append("unclosed_reasoning_span")
                break
            hidden.append(text[opening + len("<think>"):closing])
            cursor = closing + len("</think>")
        else:
            visible.append(text[cursor:])
            break
    return "".join(visible), "\n".join(hidden), tuple(flags)


@dataclass(frozen=True)
class _XmlAssistantMessage(ChatMessage):
    """Template-ready history, distinguished from legacy raw completions."""

    reasoning_content: str = ""
    tool_calls: tuple[ToolCallRequest, ...] = ()


def _xml_history_reasoning(message, tools):
    # The endpoint already split generated text using the actual prompt's
    # think opener. Do not reinterpret visible prose in structured history.
    if isinstance(message, _XmlAssistantMessage):
        return message.content, message.reasoning_content, ()
    if getattr(message, "reasoning_text", ""):
        return message.content, message.reasoning_text, ()
    text = message.content
    parts = _split_reasoning(text, stop_at_tool_call=True)
    # Stored raw completions can omit the template-prefilled opening think
    # tag. A thought may itself quote a call. Prefer the explicit close only
    # when the ordinary interpretation cannot form a valid visible turn.
    if "</think>" in text and not text.startswith("<think>") and parse_xml_calls(parts[0], tools)[1]:
        candidate = _split_reasoning("<think>" + text, stop_at_tool_call=True)
        if not parse_xml_calls(candidate[0], tools)[1]:
            return candidate
    return parts


def parse_completion(
    text: str, *, reasoning_tokens: int = 0, reasoning_open: bool = False,
    model_family: str | None = None, tools: Sequence[Mapping[str, Any]] = (),
) -> tuple[str, str, tuple[ToolCallRequest, ...], tuple[str, ...]]:
    """Parse think spans, Qwen envelopes and bare Llama name/parameters JSON.

    XML is enabled only by a configured Qwen3.5/3.8 family and its tool schemas.
    Unknown tool-like syntax remains text with a flag. Retokenization is an
    estimate of hidden generation, never a server-provided ground-truth count.
    """
    if model_family in XML_MODEL_FAMILIES:
        visible, reasoning, reasoning_flags = _split_reasoning(
            "<think>" + text if reasoning_open else text, stop_at_tool_call=True)
        calls, xml_flags = parse_xml_calls(visible, tools)
        flags = list(reasoning_flags)
        if reasoning_open:
            flags.append("reasoning_open_tag_prefilled_or_missing")
        flags.extend(xml_flags)
        if reasoning and reasoning_tokens == 0:
            flags.append("reasoning_token_count_unavailable")
        return visible, reasoning, calls, tuple(flags)
    visible, reasoning, reasoning_flags = _split_reasoning("<think>" + text if reasoning_open else text)
    flags = list(reasoning_flags)
    if reasoning_open:
        flags.append("reasoning_open_tag_prefilled_or_missing")
    calls: list[ToolCallRequest] = []

    def add_call(obj: Any, emitted: str) -> None:
        try:
            name = obj["name"]
            if not isinstance(name, str) or not name:
                raise ValueError("tool name is not a nonempty string")
            arguments = obj.get("arguments", obj.get("parameters", {}))
            arguments_json = arguments if isinstance(arguments, str) else json.dumps(
                arguments, sort_keys=True, separators=(",", ":"), allow_nan=False
            )
            # Transcript identity derives from emitted bytes and ordinal.
            call_id = hashlib.sha256(
                f"{len(calls)}\0{emitted}".encode("utf-8")
            ).hexdigest()
            calls.append(ToolCallRequest(call_id, name, arguments_json))
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            flags.append(f"malformed_tool_call:{type(exc).__name__}")

    matches = list(_TOOL_CALL.finditer(visible))
    for match in matches:
        try:
            obj = json.loads(match.group(1))
        except ValueError as exc:
            flags.append(f"malformed_tool_call:{type(exc).__name__}")
        else:
            add_call(obj, match.group(0))
    # Recognized envelopes left outside complete matches are incomplete even
    # if the stream stopped normally; cuts must not look like final answers.
    remainder = _TOOL_CALL.sub("", visible)
    if "<tool_call>" in remainder or "</tool_call>" in remainder:
        flags.append("malformed_tool_call:unclosed_or_unmatched_envelope")
    candidate = visible.strip()
    if not matches:
        candidate = candidate.removeprefix("<|python_tag|>").removesuffix("<|eom_id|>").strip()
        try:
            obj = json.loads(candidate)
        except ValueError:
            obj = None
            if candidate.startswith("{") and '"name"' in candidate and any(
                marker in candidate for marker in ('"parameters"', '"arguments"')
            ):
                flags.append("malformed_tool_call:invalid_or_truncated_json")
        if isinstance(obj, dict) and "name" in obj and (
            "parameters" in obj or "arguments" in obj
        ):
            add_call(obj, visible)
        elif any(marker in visible for marker in (
            "<tool", "<function", "<|python_tag|>", "[TOOL_CALLS]",
            '"tool_calls"', '"name"', '"parameters"', '"arguments"',
        )) and not any(flag.startswith("malformed_tool_call:") for flag in flags):
            flags.append("unsupported_tool_call_format")
    if reasoning and reasoning_tokens == 0:
        flags.append("reasoning_token_count_unavailable")
    return visible, reasoning, tuple(calls), tuple(flags)


class _StreamObservation:
    """Observe native finish reasons without replacing MLX's generation loop."""

    def __init__(self, native: Any) -> None:
        self.native = native
        self.finish_reason: str | None = None

        @wraps(native.stream_generate)
        def stream_generate(*args: Any, **kwargs: Any):
            for response in native.stream_generate(*args, **kwargs):
                reason = getattr(response, "finish_reason", None)
                self.finish_reason = reason if isinstance(reason, str) else None
                yield response

        self.stream_generate = stream_generate

    def __getattr__(self, name: str) -> Any:
        return getattr(self.native, name)


class MlxEndpoint:
    """ChatEndpoint over a prepared MlxRuntimeAdapter or the existing mock runtime.

    An explicit sampler policy opts into categorical sampling and per-turn seeds.
    Legacy callers retain the pinned greedy path.
    Mock scripts replace response text only AFTER real mock generation ran.
    """

    def __init__(
        self, runtime: Any, config: BenchmarkConfig, clock: Clock, *,
        episode_domain: str, prepare_metadata: Mapping[str, Any] | None = None,
        mock_turns: Sequence[Mapping[str, Any]] = (),
        enable_thinking: bool | None = None,
        prompt_cache: str | None = None,
        sampler: Mapping[str, Any] | None = None,
    ) -> None:
        self.runtime = runtime
        self.config = config
        self.clock = clock
        self.episode_domain = episode_domain
        self.mock_turns = tuple(mock_turns)
        self.enable_thinking = enable_thinking
        from joulewise.align.apple.sampling import validate_policy
        self.sampler = validate_policy(dict(sampler)) if sampler is not None else None
        if prompt_cache not in (None, "episode_prefix"):
            raise ValueError("unknown prompt cache policy")
        self.cache_policy = prompt_cache or "full_prompt_each_turn"
        self._episode_cache = None
        self.events: list[Any] = []
        self.turn_provenance: list[Mapping[str, Any]] = []
        self.flags: list[str] = []
        self.prompt_token_ids: list[int] = []
        self.tokenizer_provenance: dict[str, Any] = {
            "backend": config.hardware_target.runtime_backend.value,
            "identifier": None, "revision": None, "class": None, "vocab_size": None,
        }
        self._turn = 0
        prepared = dict(prepare_metadata or {})
        if config.model.revision is None:
            self.flags.append("model_revision_unpinned")
        if config.hardware_target.runtime_backend == RuntimeBackend.MLX:
            for version_key in ("mlx_version", "mlx_lm_version"):
                if prepared.get(version_key) is None:
                    self.flags.append(f"{version_key}_unavailable")
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
        self._prepare_flags = tuple(self.flags)

    def assistant_history_message(self, result: ChatResult) -> ChatMessage:
        """Retain separate reasoning for templates that require that field.

        JSON families keep their original raw-completion history byte for byte.
        """
        if self.config.model.family in XML_MODEL_FAMILIES:
            content = result.content
            if result.tool_calls and "<tool_call>" in content:
                content = content[:content.index("<tool_call>")].rstrip()
            return _XmlAssistantMessage("assistant", content,
                reasoning_content=result.reasoning_text, tool_calls=result.tool_calls)
        return ChatMessage("assistant", str(result.raw_usage.get("raw_text", result.content)))

    def _mock_prompt_text(self, messages):
        return json.dumps([
            asdict(message) if isinstance(message, _XmlAssistantMessage) else message.__dict__
            for message in messages
        ], sort_keys=True)

    def _render_prompt(self, messages, tools):
        if self.config.model.family in XML_MODEL_FAMILIES:
            return self._render_xml_prompt(messages, tools)
        return self.runtime._tokenizer.apply_chat_template(
            [{"role": m.role, "content": m.content,
              **({"name": m.name} if m.name else {}),
              **({"tool_call_id": m.tool_call_id} if m.tool_call_id else {}),
              **({"tool_calls": [{"id": c.call_id, "type": "function", "function": {
                  "name": c.name, "arguments": c.arguments_json}} for c in getattr(m, "tool_calls", ())]}
                 if getattr(m, "tool_calls", ()) else {})} for m in _coalesce_assistant_calls(messages)],
            tools=list(tools) or None, tokenize=False, add_generation_prompt=True,
            **({"enable_thinking": self.enable_thinking} if self.enable_thinking is not None else {}),
        )

    def _render_xml_prompt(self, messages, tools):
        history = []
        for message in _coalesce_assistant_calls(messages):
            item = {"role": message.role, "content": message.content}
            if message.name:
                item["name"] = message.name
            if message.tool_call_id:
                item["tool_call_id"] = message.tool_call_id
            if message.role == "assistant":
                visible, reasoning, _ = _xml_history_reasoning(message, tools)
                calls = getattr(message, "tool_calls", ())
                if "<tool_call>" in visible:
                    parsed, flags = parse_xml_calls(visible, tools)
                    if calls and (flags or [(c.name, json.loads(c.arguments_json)) for c in parsed] != [
                        (c.name, json.loads(c.arguments_json)) for c in calls
                    ]):
                        raise ValueError("xml_history_tool_calls_disagree")
                    if not flags:
                        # The workload stores raw completions. Structured
                        # callers may also retain them. Render each action once.
                        calls = calls or parsed
                        visible = visible[:visible.index("<tool_call>")].rstrip()
                item["content"] = visible
                item["reasoning_content"] = reasoning
                if calls:
                    item["tool_calls"] = [{"id": call.call_id, "type": "function", "function": {
                        "name": call.name, "arguments": json.loads(call.arguments_json),
                    }} for call in calls]
            history.append(item)
        return self.runtime._tokenizer.apply_chat_template(
            history, tools=list(tools) or None, tokenize=False, add_generation_prompt=True,
            **({"enable_thinking": self.enable_thinking} if self.enable_thinking is not None else {}),
        )

    def rendered_prompt_length(self, messages, *, tools=()):
        """Count the exact next template without generation or native model work."""
        if self.config.hardware_target.runtime_backend == RuntimeBackend.MOCK:
            script = self.mock_turns[self._turn] if self._turn < len(self.mock_turns) else {}
            if "prompt_tokens" in script:
                count = int(script["prompt_tokens"])
            else:
                count = len(self._mock_prompt_text(messages).split())
            return count
        from joulewise.adapters.mlx_runtime import _encode
        return len(_encode(self.runtime._tokenizer, self._render_prompt(messages, tools), add_special_tokens=False))

    def chat(
        self, messages: Sequence[ChatMessage], *, tools: Sequence[Mapping[str, Any]] = (),
        max_tokens: int, temperature: float, seed: int | None,
    ) -> ChatResult:
        start_stamp = self.clock.stamp()
        start_ns = monotonic_ns(start_stamp)
        turn_index = self._turn
        self._turn += 1
        flags: list[str] = []
        if self.sampler is None and temperature != 0.0:
            # Existing workloads are pinned greedy; 0 is the exact sampler
            # identity, not a numerical comparison tolerance.
            flags.append("requested_temperature_differs_from_pinned_greedy")
        if self.sampler is None and seed is not None:
            flags.append("seed_recorded_greedy_generation")
        text = ""
        prompt_tokens = completion_tokens = reasoning_tokens = cached_tokens = 0
        first_epoch: float | None = None
        provenance: dict[str, Any] = {}
        finish_reason: str | None = None
        reasoning_open_from_template = False
        xml_family = self.config.model.family in XML_MODEL_FAMILIES

        def history_reasoning(message):
            return (_xml_history_reasoning(message, tools) if xml_family
                    else _split_reasoning(message.content))

        prior_hidden = any(
            message.role == "assistant" and (history_reasoning(message)[0] != message.content
                or (xml_family and bool(history_reasoning(message)[1])))
            for message in messages
        )
        prior_hidden_prefill_tokens: int | None = None if prior_hidden else 0
        try:
            if self.config.hardware_target.runtime_backend == RuntimeBackend.MOCK:
                script = self.mock_turns[turn_index] if turn_index < len(self.mock_turns) else {}
                requested_tokens = int(script.get("completion_tokens", max_tokens))
                emitted_tokens = min(requested_tokens, max_tokens)
                finish_reason = script.get("finish_reason", "stop")
                if requested_tokens > max_tokens:
                    finish_reason = "length"
                profile = replace(
                    self.config.workload_profile, name="align_turn",
                    prompt_text=None, dataset_ref=None, suite_manifest_ref=None,
                    suite_manifest_sha256=None, generator_sidecar_ref=None,
                    prompt_token_expectation=None,
                    prompt_tokens=int(script["prompt_tokens"]) if "prompt_tokens" in script else None,
                    output_tokens=emitted_tokens,
                )
                if profile.prompt_tokens is None:
                    profile = replace(profile, prompt_text=self._mock_prompt_text(messages))
                result = self.runtime.run_workload(replace(self.config, workload_profile=profile))
                new_events = result.events
                text = str(script.get("content", result.output_artifacts.get("response.txt", "")))
                if requested_tokens > max_tokens:
                    # Synthetic text is spread uniformly over scripted tokens.
                    # The ratio is a fixture construction, not tokenizer inference.
                    text = text[:len(text) * max_tokens // requested_tokens]
                    flags.append("mock_text_truncated_proportionally")
                prompt_tokens = (result.token_count or 0) - (result.output_token_count or 0)
                completion_tokens = result.output_token_count or 0
                reasoning_tokens = int(script.get("reasoning_tokens", 0))
                if reasoning_tokens < 0 or reasoning_tokens > completion_tokens:
                    flags.append("mock_reasoning_count_outside_completion")
                    reasoning_tokens = 0
                if "prior_hidden_prefill_tokens" in script:
                    count = script["prior_hidden_prefill_tokens"]
                    if type(count) is int and 0 <= count <= prompt_tokens:
                        prior_hidden_prefill_tokens = count
                    else:
                        flags.append("mock_prior_hidden_prefill_count_invalid")
                elif prior_hidden:
                    flags.append("prior_hidden_prefill_count_unavailable:mock_scripted_prompt")
                provenance = dict(result.workload_provenance or {})
                provenance["output_token_ids"] = provenance.get("response", {}).get("emitted_token_ids")
                actual_ids = self.runtime._prompt_token_ids(prompt_tokens)
                self.prompt_token_ids.extend(actual_ids)
                provenance["prompt_token_ids"] = actual_ids
                self.tokenizer_provenance = dict(provenance.get("tokenizer", self.tokenizer_provenance))
                flags.append("synthetic_mock_runtime")
            elif self.config.hardware_target.runtime_backend == RuntimeBackend.MLX:
                from joulewise.adapters.mlx_runtime import _encode, _tokenizer_identity

                tokenizer = self.runtime._tokenizer

                def render_prompt(chat: Sequence[ChatMessage]) -> str:
                    return self._render_prompt(chat, tools)

                cache_metadata = {}
                cache_setup_metadata = {}
                stream_options = {}

                def prepare_prompt():
                    nonlocal prior_hidden_prefill_tokens, reasoning_open_from_template
                    rendered = render_prompt(messages)
                    reasoning_open_from_template = rendered.rstrip().endswith("<think>")
                    # Chat templates already contain their special tokens.
                    ids = _encode(tokenizer, rendered, add_special_tokens=False)
                    if prior_hidden:
                        scrubbed = [
                            replace(message, content=history_reasoning(message)[0], **(
                                {field: "" for field in ("reasoning_text", "reasoning_content")
                                 if xml_family and hasattr(message, field)}
                            ))
                            if message.role == "assistant" else message
                            for message in messages
                        ]
                        hidden_free_ids = _encode(
                            tokenizer, render_prompt(scrubbed), add_special_tokens=False
                        )
                        prior_hidden_prefill_tokens = len(ids) - len(hidden_free_ids)
                        if prior_hidden_prefill_tokens < 0:
                            flags.append("prior_hidden_prefill_token_delta_negative")
                    return ids, ids, rendered

                def reconcile_prompt(ids):
                    from joulewise.align.apple.prompt_cache import EpisodePromptCache
                    if self._episode_cache is None:
                        self._episode_cache = EpisodePromptCache(self.runtime._model)
                    delta, observed = self._episode_cache.prepare(ids)
                    cache_metadata.update(observed)
                    cache_setup_metadata.update({k: v for k, v in observed.items() if k != "fed_delta_ids"})
                    stream_options["prompt_cache"] = self._episode_cache.cache
                    if observed["cache_rebuilt"]:
                        flags.append(f"cache.rebuilt_untrimmable:{turn_index}")
                    cached = observed["cached_prompt_tokens"]
                    # Independent ID annotations; the legacy rendered
                    # counterfactual above retains its original meaning.
                    cached_hidden, fresh_hidden = reasoning_tokens_from_ids(tokenizer, ids, split_at=cached)
                    cache_metadata.update(
                        cached_hidden_context_tokens=cached_hidden,
                        fresh_hidden_prefill_tokens=fresh_hidden,
                        hidden_cache_accounting_method="prompt_ids_between_think_delimiters",
                    )
                    return delta

                native = self.runtime._mlx_lm
                observation = _StreamObservation(native)
                # Sequential in-process turns own this prepared runtime. Restore
                # the module even on a native fault; identity/probes see it intact.
                self.runtime._mlx_lm = observation
                try:
                    record = self.runtime._generate(
                        None, [], None, max_tokens, suppress_eos=False,
                        prepare_prompt=prepare_prompt,
                        **({"sampler_policy": dict(self.sampler), "per_turn_seed": turn_seed(seed, turn_index)} if self.sampler is not None else {}),
                        **({"stream_options": stream_options, "cache_accounting": True,
                            "setup_metadata": cache_setup_metadata, "reconcile_prompt": reconcile_prompt}
                           if self.cache_policy == "episode_prefix" else {}),
                    )
                finally:
                    self.runtime._mlx_lm = native
                if self.cache_policy == "episode_prefix":
                    self._episode_cache.finish(record.prompt_token_ids, record.output_token_ids, cache_metadata)
                    cached_tokens = cache_metadata["cached_prompt_tokens"]
                finish_reason = observation.finish_reason
                text = record.text
                prompt_tokens = record.prompt_tokens
                completion_tokens = record.output_tokens
                new_events = record.events
                self.prompt_token_ids.extend(record.prompt_token_ids)
                self.tokenizer_provenance = _tokenizer_identity(tokenizer, self.config)
                provenance = {
                    "prompt_token_ids": record.prompt_token_ids,
                    "sampler": record.sampler_provenance,
                    "prompt_token_ids_sha256": hashlib.sha256(
                        json.dumps(record.prompt_token_ids, separators=(",", ":")).encode("utf-8")
                    ).hexdigest(),
                    "output_token_ids": record.output_token_ids,
                    "stop_condition": finish_reason or record.stop_condition,
                    "runtime_stop_condition": record.stop_condition,
                }
                provenance.update(cache_metadata)
                reasoning_tokens = reasoning_tokens_from_ids(
                    tokenizer, record.output_token_ids, reasoning_open=reasoning_open_from_template)
                provenance["reasoning_token_accounting"] = "output_ids_between_think_delimiters_excluding_trailing_eos"
            else:
                raise ValueError("align_episode supports only mock and mlx backends")
            for event in new_events:
                self.events.append(replace(
                    event, metadata={**event.metadata, "align_turn_index": turn_index}
                ))
                # records.Turn.first_token_ns means prefill end, before the
                # first decode step (10 ms later in the D-019 mock world).
                if first_epoch is None and event.event_type == "phase_end" and event.phase == "prefill":
                    first_epoch = event.timestamp_s
        except Exception as exc:
            self._episode_cache = None  # never reuse partial/unknown native state
            flags.append(f"endpoint_error:{type(exc).__name__}:{exc}")
        # A native stop is authoritative even at the exact integer budget.
        # With no finish reason, equality is the only available cut evidence.
        if not isinstance(finish_reason, str) or not finish_reason:
            finish_reason = None
        cut = finish_reason in ("length", "max_tokens", "max_new_tokens") or (
            finish_reason is None and completion_tokens == max_tokens
        )
        if cut:
            flags.append(f"turn_token_budget_reached:{turn_index}")
        provenance.update(
            finish_reason=finish_reason,
            stop_condition=("requested_tokens_emitted" if cut else finish_reason or provenance.get("stop_condition")),
            prior_hidden_prefill_tokens=prior_hidden_prefill_tokens,
            prior_hidden_prefill_method=(
                "chat_template_token_count_difference"
                if self.config.hardware_target.runtime_backend == RuntimeBackend.MLX
                else "scripted_prompt_count"
            ),
        )
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
            text, reasoning_tokens=reasoning_tokens, reasoning_open=reasoning_open_from_template,
            model_family=self.config.model.family, tools=tools,
        )
        flags.extend(parse_flags)
        if cut and "unclosed_reasoning_span" in parse_flags:
            # The first parse already hides the entire unfinished span using
            # the template's opener. Reparsing at a quoted/nested <think>
            # would expose the draft before it and could execute a draft call.
            flags.append("reasoning_censored_at_token_limit")
        calls = tuple(replace(call, call_id=f"{turn_index}-{call.call_id}") for call in calls)
        self.flags.extend(flags)
        self.turn_provenance.append({
            "turn": turn_index, "flags": flags, "generation": provenance,
            "start_stamp": start_stamp.__dict__, "end_stamp": end_stamp.__dict__,
            "clock_mapping": mapping.__dict__,
        })
        return ChatResult(
            content=visible, reasoning_text=reasoning, tool_calls=calls,
            prompt_tokens=prompt_tokens, cached_prompt_tokens=cached_tokens,
            completion_tokens=completion_tokens, reasoning_tokens=reasoning_tokens,
            start_ns=start_ns, first_token_ns=first_ns, end_ns=end_ns,
            raw_usage={"joulewise": {"flags": list(dict.fromkeys([*self._prepare_flags, *flags])),
                                     "finish_reason": finish_reason}, "cache_policy": self.cache_policy,
                       **({"cache": cache_metadata} if self.cache_policy == "episode_prefix" and self.config.hardware_target.runtime_backend == RuntimeBackend.MLX else {}), "raw_text": text},
        )
