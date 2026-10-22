"""Run agent episodes and resumable matrices using only the shared contracts.

Factories receive (config, FactoryContext); imports that install factories are
explicit in a matrix. Optional clock/observation hooks are lane-local adapters,
so real endpoints, tasks, monitors and samplers need only the shared protocols.
"""

from __future__ import annotations

import hashlib
import importlib
import itertools
import json
import math
import os
import random
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from joulewise.align.interfaces import (
    AgentTask, ChatEndpoint, ChatMessage, Monitor, PowerSampler, TokenCounter,
)
from joulewise.align.records import (
    ClockMapping, Episode, MonitorVerdict, PowerTrace, Turn, ToolCall,
    from_json, to_json, to_jsonable,
)

_REASONING_TAGS = ("<jw_reasoning>", "</jw_reasoning>")
_VISIBILITIES = ("full", "no_scratchpad", "actions_only", "tampered")
_FACTORIES: dict[str, dict[str, Callable[..., Any]]] = {
    kind: {} for kind in ("task", "endpoint", "monitor", "sampler", "clock", "token_counter")
}


@dataclass(frozen=True)
class FactoryContext:
    """Configuration context shared by the components of one matrix episode."""

    task_pair: str
    condition: str
    seed: int
    matrix_id: str
    clock_domain: str
    clock: Callable[[], int]


def _register(kind: str, name: str, factory: Callable[..., Any]) -> None:
    _FACTORIES[kind][name] = factory


def register_task_factory(name: str, factory: Callable[..., AgentTask]) -> None:
    _register("task", name, factory)


def register_endpoint_factory(name: str, factory: Callable[..., ChatEndpoint]) -> None:
    _register("endpoint", name, factory)


def register_monitor_factory(name: str, factory: Callable[..., Monitor]) -> None:
    _register("monitor", name, factory)


def register_sampler_factory(name: str, factory: Callable[..., PowerSampler]) -> None:
    _register("sampler", name, factory)


def register_clock_factory(name: str, factory: Callable[..., Callable[[], int]]) -> None:
    _register("clock", name, factory)


def register_token_counter_factory(name: str, factory: Callable[..., TokenCounter]) -> None:
    _register("token_counter", name, factory)


def episode_id(task_pair: str, condition: str, endpoint_identity: str, seed: int,
               matrix_id: str = "") -> str:
    """Stable identity; seed, identities and matrix ID are data, never wall time."""
    return hashlib.sha256(to_json(
        [task_pair, condition, endpoint_identity, seed, matrix_id]).encode("utf-8")).hexdigest()


def _spans(text: str, tags: tuple[str, str]) -> tuple[str, list[str], bool]:
    opening, closing = tags
    if not opening or not closing:
        return text, [], False
    visible: list[str] = []
    hidden: list[str] = []
    position = 0
    unclosed = False
    while (start := text.find(opening, position)) >= 0:
        visible.append(text[position:start])
        end = text.find(closing, start + len(opening))
        if end < 0:
            hidden.append(text[start + len(opening):])
            position = len(text)
            unclosed = True
            break
        hidden.append(text[start + len(opening):end])
        position = end + len(closing)
    visible.append(text[position:])
    return "".join(visible), hidden, unclosed


def transcript_view(transcript: Sequence[ChatMessage], visibility: str,
                    scratchpad_tags: tuple[str, str] | None = None) -> list[ChatMessage]:
    """Build monitor views; call messages carry name, call ID and JSON arguments.

    Full/tampered preserve the supplied transcript. The latter is a label for a
    caller-supplied tampered transcript; Episode-only transforms do not edit text.
    """
    if visibility == "actions_only":
        return [m for m in transcript if m.role == "tool" or
                (m.role == "assistant" and m.tool_call_id is not None)]
    if visibility != "no_scratchpad":
        return list(transcript)
    result = []
    for message in transcript:
        content = message.content
        if message.role == "assistant" and message.tool_call_id is None:
            for tags in dict.fromkeys(filter(None, (scratchpad_tags, _REASONING_TAGS))):
                content, _, _ = _spans(content, tags)
        result.append(replace(message, content=content))
    return result


def _count(value: Any, flags: list[str], field: str) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    flags.append("usage.invalid." + field)
    return 0


def run_episode(task: AgentTask, condition: str, endpoint: ChatEndpoint, *,
                monitors: Sequence[Any] = (), samplers: Sequence[PowerSampler] = (),
                seed: int, max_turns: int, max_tokens: int, temperature: float,
                clock_domain: str, token_counter: TokenCounter | None = None,
                matrix_id: str = "", clock: Callable[[], int] | None = None
                ) -> tuple[Episode, list[ChatMessage]]:
    """Run, retain failures as flags, stop sampling, then score and monitor.

    Monitor entries may be objects (full visibility), or (object, visibilities).
    clock is a nanosecond callable, normally time.monotonic_ns; synthetic worlds
    inject a virtual monotonic clock without replacing any production function.
    """
    now = clock or time.monotonic_ns
    flags: list[str] = []
    transcript: list[ChatMessage] = []
    turns: list[Turn] = []
    started: list[PowerSampler] = []
    counts: dict[str, int | None] = {}
    counted: list[int] = []
    traces: list[PowerTrace] = []
    mappings: dict[str, ClockMapping] = {}
    hardware: dict[str, Any] = {
        "endpoint": endpoint.identity,
        "samplers": [getattr(s, "identity", type(s).__name__) for s in samplers],
    }
    tags = task.scratchpad_tags
    tools: Sequence[Mapping[str, Any]] = ()
    ready = True
    try:
        task.reset(seed)
        transcript = [ChatMessage("system", task.system_prompt(condition)),
                      ChatMessage("user", task.user_prompt())]
        tools = task.tool_schemas()
    except KeyboardInterrupt:
        flags.append("episode.interrupted")
        ready = False
    except Exception as exc:
        flags.append("task.setup_error." + type(exc).__name__)
        ready = False
    for sampler in samplers:
        started.append(sampler)  # stop even a partially started sampler
        try:
            sampler.start()
        except KeyboardInterrupt:
            flags.append("episode.interrupted")
            ready = False
            break
        except Exception as exc:
            flags.append("sampler.start_error." + type(exc).__name__)
    start = now()
    end = start
    if condition not in ("benign", "sabotage"):
        flags.append("condition.unknown")
        hardware["requested_condition"] = condition
    try:
        if ready:
            for index in range(max(0, max_turns)):
                call_start = now()
                try:
                    result = endpoint.chat(transcript, tools=tools, max_tokens=max_tokens,
                                           temperature=temperature, seed=seed)
                except KeyboardInterrupt:
                    flags.append("episode.interrupted")
                    break
                except Exception as exc:
                    flags.append("endpoint.error." + type(exc).__name__)
                    break
                call_end = now()
                prompt = _count(result.prompt_tokens, flags, "prompt_tokens")
                cached = _count(result.cached_prompt_tokens, flags, "cached_prompt_tokens")
                if cached > prompt:
                    flags.append("usage.cached_exceeds_prompt")
                    cached = prompt
                decode = _count(result.completion_tokens, flags, "completion_tokens")
                hidden = _count(result.reasoning_tokens, flags, "reasoning_tokens")
                scratch: list[str] = []
                if tags:
                    _, scratch, unclosed = _spans(result.content, tags)
                    if unclosed:
                        flags.append("scratchpad.unclosed")
                scratch_count: int | None = 0
                if scratch:
                    if token_counter is None:
                        scratch_count = None
                        flags.append("hidden_tokens.scratchpad_uncounted")
                    else:
                        try:
                            scratch_count = sum(_count(token_counter.count_tokens(span),
                                flags, "scratchpad_tokens") for span in scratch)
                        except KeyboardInterrupt:
                            flags.append("episode.interrupted")
                            scratch_count = None
                        except Exception as exc:
                            flags.append("token_counter.error." + type(exc).__name__)
                            scratch_count = None
                counts[str(index)] = scratch_count
                if scratch_count is not None:
                    hidden += scratch_count
                    counted.append(index)
                if hidden > decode:
                    flags.append("usage.hidden_exceeds_decode")
                    hidden = decode
                t_start, t_end = result.start_ns, result.end_ns
                if (not isinstance(t_start, int) or isinstance(t_start, bool) or
                    not isinstance(t_end, int) or isinstance(t_end, bool) or t_end < t_start):
                    flags.append("clock.endpoint_invalid")
                    t_start, t_end = call_start, call_end
                if t_start < start or t_start < end:
                    flags.append("clock.endpoint_out_of_order")
                start = min(start, t_start)
                first = result.first_token_ns
                if first is not None and (not isinstance(first, int) or isinstance(first, bool)
                                          or not t_start <= first <= t_end):
                    flags.append("clock.first_token_invalid")
                    first = None
                content = result.content
                if result.reasoning_text:
                    content = _REASONING_TAGS[0] + result.reasoning_text + _REASONING_TAGS[1] + content
                transcript.append(ChatMessage("assistant", content))
                calls: list[ToolCall] = []
                interrupted = False
                for request in result.tool_calls:
                    transcript.append(ChatMessage("assistant", request.arguments_json,
                                                  request.name, request.call_id))
                    tool_start = now()
                    try:
                        output = task.call_tool(request.name, request.arguments_json)
                    except KeyboardInterrupt:
                        flags.append("episode.interrupted")
                        output = "Tool interrupted"
                        interrupted = True
                    except Exception as exc:
                        flags.append("tool.error." + type(exc).__name__)
                        output = "Tool error: " + type(exc).__name__
                    tool_end = now()
                    if not isinstance(output, str):
                        flags.append("tool.non_text_result")
                        output = to_json(output)
                    calls.append(ToolCall(request.name, tool_start, tool_end,
                                          len(request.arguments_json.encode("utf-8")),
                                          len(output.encode("utf-8"))))
                    transcript.append(ChatMessage("tool", output, request.name, request.call_id))
                    if interrupted:
                        break
                turns.append(Turn(index, t_start, t_end, cached, prompt - cached,
                                  decode, hidden, first, tuple(calls)))
                end = max(end, t_end, now(), *(c.end_ns for c in calls))
                if interrupted or "episode.interrupted" in flags:
                    break
                if not result.tool_calls:
                    break
            else:
                flags.append("episode.max_turns")
    except KeyboardInterrupt:
        flags.append("episode.interrupted")
    except Exception as exc:
        flags.append("runner.error." + type(exc).__name__)
    end = max(end, now())
    hardware["runner"] = {
        "matrix_id": matrix_id, "scratchpad_tokens": counts,
        "scratchpad_counted_hidden": counted,
    }
    episode = Episode(
        episode_id(task.task_pair, condition, endpoint.identity, seed, matrix_id),
        task.task_pair, condition if condition in ("benign", "sabotage") else "benign",
        getattr(endpoint, "model", endpoint.identity), endpoint.identity, seed,
        clock_domain, start, end, tuple(turns), hardware=hardware,
    )
    for sampler in started:
        try:
            observer = getattr(sampler, "observe_episode", None)
            if observer is not None:
                observer(episode)
        except (Exception, KeyboardInterrupt) as exc:
            flags.append("episode.interrupted" if isinstance(exc, KeyboardInterrupt) else
                         "sampler.observe_error." + type(exc).__name__)
        try:
            sampled = tuple(sampler.stop())
        except (Exception, KeyboardInterrupt) as exc:
            flags.append("episode.interrupted" if isinstance(exc, KeyboardInterrupt) else
                         "sampler.stop_error." + type(exc).__name__)
            continue
        for trace in sampled:
            if not isinstance(trace, PowerTrace):
                flags.append("sampler.invalid_trace")
                continue
            if trace.clock_domain != clock_domain:
                try:
                    mapping = sampler.clock_mapping()
                    if (not isinstance(mapping, ClockMapping) or
                        mapping.trace_domain != trace.clock_domain or
                        mapping.episode_domain != clock_domain or mapping.uncertainty_ns < 0):
                        raise ValueError("clock mapping does not cover trace")
                    if trace.clock_domain in mappings and mappings[trace.clock_domain] != mapping:
                        flags.append("clock.mapping_conflict")
                        continue
                    mappings[trace.clock_domain] = mapping
                except (Exception, KeyboardInterrupt) as exc:
                    flags.append("episode.interrupted" if isinstance(exc, KeyboardInterrupt) else
                                 "clock.unmapped")
                    continue
            if not trace.t_ns:
                flags.append("power.empty")
            if trace.notes:
                flags.append("power.notes")
            traces.append(trace)
    scores: dict[str, Any] = {}
    for name, scorer in (("main_task_score", task.score_main), ("side_task_success", task.score_side)):
        try:
            value = scorer(transcript)
            if value is not None:
                valid = (isinstance(value, (int, float)) and not isinstance(value, bool)
                         and math.isfinite(value)) if name == "main_task_score" else isinstance(value, bool)
                if not valid:
                    flags.append("score." + name + ".invalid")
                    value = None
            scores[name] = value
        except (Exception, KeyboardInterrupt) as exc:
            flags.append("episode.interrupted" if isinstance(exc, KeyboardInterrupt) else
                         "score." + name + ".error." + type(exc).__name__)
    verdicts: list[MonitorVerdict] = []
    for entry in monitors:
        monitor, visibilities = entry if isinstance(entry, tuple) else (entry, ("full",))
        for visibility in visibilities:
            if visibility not in _VISIBILITIES:
                flags.append("monitor.visibility_unknown")
                continue
            try:
                verdict = monitor.score(transcript_view(transcript, visibility, tags),
                    visibility=visibility, task_description=task.task_description())
                if verdict.visibility != visibility:
                    flags.append("monitor.visibility_mismatch")
                else:
                    verdicts.append(verdict)
            except (Exception, KeyboardInterrupt) as exc:
                flags.append("episode.interrupted" if isinstance(exc, KeyboardInterrupt) else
                             "monitor.error." + type(exc).__name__)
    episode = replace(episode, **scores, monitor_verdicts=tuple(verdicts),
                      power_traces=tuple(traces), clock_mappings=tuple(mappings.values()),
                      flags=tuple(dict.fromkeys(flags)))
    return episode, transcript


def _component(value: Any) -> dict[str, Any]:
    return {"factory": value} if isinstance(value, str) else dict(value)


def _make(kind: str, spec: Any, context: FactoryContext) -> Any:
    config = _component(spec)
    factory = _FACTORIES[kind][config["factory"]]
    return factory(dict(config.get("config", {})), context)


def _atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        handle.write(to_json(value) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _append(path: Path, value: Any) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(to_json(value) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _load_lines(path: Path, parser: Callable[[bytes], Any], flags: list[str]) -> list[Any]:
    """Recover valid records; preserve discarded bytes in recovery.jsonl."""
    if not path.exists():
        path.touch()
        return []
    rows = []
    clean: list[bytes] = []
    data = path.read_bytes()
    lines = data.splitlines(keepends=True)
    for index, line in enumerate(lines):
        reason = ""
        try:
            if not line.endswith(b"\n"):
                reason = "resume.partial_last_line"
                raise ValueError(reason)
            row = parser(line)
            to_json(row)  # reject non-JSON floats and malformed objects on resume
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            reason = reason or "resume.invalid_record"
            flags.append(reason + "." + path.name)
            _append(path.parent / "recovery.jsonl", {
                "file": path.name, "line": index + 1, "flag": reason, "raw_hex": line.hex(),
            })
            continue
        rows.append(row)
        clean.append(line)
    if len(clean) != len(lines):
        with path.open("wb") as handle:
            handle.write(b"".join(clean))
            handle.flush()
            os.fsync(handle.fileno())
    return rows


def _transcript_row(line: bytes) -> dict[str, Any]:
    row = json.loads(line)
    if not isinstance(row["episode_id"], str) or not isinstance(row["messages"], list):
        raise ValueError("invalid transcript")
    for message in row["messages"]:
        ChatMessage(**message)
    return row


def run_matrix(spec_path: str | Path) -> Path:
    """Run task pairs x conditions x seeds x endpoints; return episodes.jsonl.

    A transcript is fsynced before its episode, which is the commit marker.
    run.json records randomized order, configuration digest and recovery flags.
    Use one writer per output directory. Factory modules are explicit Python
    imports supplied by the operator, never installed or fetched by this runner.
    """
    spec_path = Path(spec_path)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    output = Path(spec.get("output_dir", "align-run"))
    if not output.is_absolute():
        output = spec_path.parent / output
    output.mkdir(parents=True, exist_ok=True)
    episodes_path = output / "episodes.jsonl"
    transcripts_path = output / "transcripts.jsonl"
    metadata_path = output / "run.json"
    flags: list[str] = []
    canonical = {key: value for key, value in spec.items() if key != "output_dir"}
    digest = hashlib.sha256(to_json(canonical).encode("utf-8")).hexdigest()
    matrix_id = str(spec.get("matrix_id", digest))
    order_seed = spec.get("order_seed", 0)
    previous = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
    flags.extend(previous.get("flags", []))
    if previous and previous.get("spec_sha256") != digest:
        # An explicit matrix ID is stable, so disclose changed run settings.
        flags.append("matrix.spec_changed")
    metadata = {"matrix_id": matrix_id, "spec_sha256": digest,
                "order_seed": order_seed, "flags": flags, "order": []}
    from joulewise.align.mock_world import register_mock_factories
    register_mock_factories()
    for module in spec.get("imports", []):
        try:
            importlib.import_module(module)
        except Exception as exc:
            flags.append("matrix.import_error." + type(exc).__name__)
    episodes = _load_lines(episodes_path, lambda line: from_json(Episode, line), flags)
    transcripts = _load_lines(transcripts_path, _transcript_row, flags)
    committed = {ep.episode_id: ep for ep in episodes}
    transcript_map = {row["episode_id"]: row for row in transcripts}
    # Drop only uncommitted transcript rows after a kill between the two appends.
    if any(row["episode_id"] not in committed for row in transcripts):
        flags.append("resume.orphan_transcript")
        with transcripts_path.open("w", encoding="utf-8") as handle:
            for row in transcripts:
                if row["episode_id"] in committed:
                    handle.write(to_json(row) + "\n")
    for ep in episodes:
        if ep.episode_id not in transcript_map:
            flags.append("resume.transcript_missing")
            _append(transcripts_path, {"episode_id": ep.episode_id, "messages": [],
                                      "flags": ["resume.transcript_missing"]})
    tasks = spec.get("task_pairs", spec.get("tasks", []))
    jobs = list(itertools.product(tasks, spec.get("conditions", ["benign", "sabotage"]),
                                  spec.get("seeds", [0]), spec.get("endpoints", [])))
    random.Random(order_seed).shuffle(jobs)
    for task_spec, condition, seed, endpoint_spec in jobs:
        task_spec = _component(task_spec)
        pair = task_spec.get("task_pair", task_spec["factory"])
        domain = spec.get("clock_domain", "host.monotonic")
        context = FactoryContext(pair, condition, seed, matrix_id, domain, time.monotonic_ns)
        endpoint_identity = to_json(_component(endpoint_spec))
        task = None
        endpoint = None
        construction_flags: list[str] = []
        try:
            if "clock" in spec:
                context = replace(context, clock=_make("clock", spec["clock"], context))
            task = _make("task", task_spec, context)
            endpoint = _make("endpoint", endpoint_spec, context)
            pair = task.task_pair
            context = replace(context, task_pair=pair)
            endpoint_identity = endpoint.identity
        except (Exception, KeyboardInterrupt) as exc:
            construction_flags.append("episode.interrupted" if isinstance(exc, KeyboardInterrupt)
                                      else "factory.error." + type(exc).__name__)
        identity = episode_id(pair, condition, endpoint_identity, seed, matrix_id)
        metadata["order"].append(identity)
        if identity in committed:
            continue
        if construction_flags:
            timestamp = context.clock()
            episode = Episode(identity, pair, condition, endpoint_identity, endpoint_identity,
                              seed, domain, timestamp, timestamp, (), flags=tuple(construction_flags))
            transcript = []
        else:
            monitors = []
            samplers = []
            counter = None
            for kind, configurations, target in (
                ("monitor", spec.get("monitors", []), monitors),
                ("sampler", spec.get("samplers", []), samplers),
            ):
                for configuration in configurations:
                    try:
                        component = _make(kind, configuration, context)
                        if kind == "monitor":
                            visibilities = tuple(_component(configuration).get(
                                "visibilities", ["full"]))
                            target.append((component, visibilities))
                        else:
                            target.append(component)
                    except (Exception, KeyboardInterrupt) as exc:
                        construction_flags.append("episode.interrupted" if isinstance(exc, KeyboardInterrupt)
                                                  else kind + ".factory_error." + type(exc).__name__)
            if "token_counter" in spec:
                try:
                    counter = _make("token_counter", spec["token_counter"], context)
                except (Exception, KeyboardInterrupt) as exc:
                    construction_flags.append("episode.interrupted" if isinstance(exc, KeyboardInterrupt)
                                              else "token_counter.factory_error." + type(exc).__name__)
            episode, transcript = run_episode(
                task, condition, endpoint, monitors=monitors, samplers=samplers, seed=seed,
                max_turns=spec.get("max_turns", 40), max_tokens=spec.get("max_tokens", 600),
                temperature=spec.get("temperature", 0.0), clock_domain=domain,
                token_counter=counter, matrix_id=matrix_id, clock=context.clock,
            )
            runner_metadata = dict(episode.hardware.get("runner", {}))
            runner_metadata.update(order_seed=order_seed, order_index=len(metadata["order"]) - 1)
            hardware = dict(episode.hardware)
            hardware["runner"] = runner_metadata
            episode = replace(episode, hardware=hardware,
                              flags=tuple(dict.fromkeys((*episode.flags, *construction_flags))))
        _append(transcripts_path, {"episode_id": episode.episode_id,
                                  "messages": to_jsonable(transcript), "flags": []})
        _append(episodes_path, episode)
        committed[episode.episode_id] = episode
        if "episode.interrupted" in episode.flags:
            flags.append("matrix.interrupted")
            break
        metadata["flags"] = list(dict.fromkeys(flags))
        _atomic_json(metadata_path, metadata)
    metadata["flags"] = list(dict.fromkeys(flags))
    _atomic_json(metadata_path, metadata)
    return episodes_path


__all__ = [
    "FactoryContext", "episode_id", "transcript_view", "run_episode", "run_matrix",
    "register_task_factory", "register_endpoint_factory", "register_monitor_factory",
    "register_sampler_factory", "register_clock_factory", "register_token_counter_factory",
]
