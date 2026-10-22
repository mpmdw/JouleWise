"""One agent episode per existing JouleWise campaign member.

The ordinary controller still owns sampler startup, idle admission, warmup,
hazard policy, dwell and immutable bundle custody. The runtime produces the
episode and transcript in memory. read_episode_bundle joins them with the
controller's already parsed trace and anchor evidence without rewriting a bundle.
"""

from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import math
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Mapping

from joulewise.align.apple.endpoint import MlxEndpoint
from joulewise.align.apple.sampler import (
    NS_PER_SECOND, monotonic_ns, power_records, stamp_mapping, _stamp_record, _restore_stamp,
)
from joulewise.align.interfaces import AgentTask, ChatMessage
from joulewise.align.records import (
    Condition, Episode, ToolCall, Turn, from_json, to_json, to_jsonable,
)
from joulewise.bundle_read import BundleReader
from joulewise.clock import Clock, ClockStamp
from joulewise.interfaces import AdapterFailure, AdapterResult, PowerSample, RunContext, RuntimeEvent, RuntimeResult
from joulewise.schemas import BenchmarkConfig, FailureReason, RuntimeBackend
from joulewise.provenance import prompt_provenance

WORKLOAD_KIND = "align_episode"
SPEC_SCHEMA = "joulewise.align.apple.episode_spec.v1"


@dataclass(frozen=True)
class EpisodeSpec:
    """Campaign-carried task factory and generation controls; no service calls.

    task_factory is an installed local Python module:callable returning AgentTask.
    A SHADE port can provide that factory without coupling this lane to its code.
    mock_turns is consumed only by the existing mock runtime endpoint.
    """

    task_factory: str
    condition: Condition
    seed: int
    max_turns: int
    max_tokens: int
    temperature: float
    task_kwargs: Mapping[str, Any] = field(default_factory=dict)
    mock_turns: tuple[Mapping[str, Any], ...] = ()
    schema: str = SPEC_SCHEMA

    def to_text(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"), allow_nan=False)

    @classmethod
    def from_text(cls, text: str) -> "EpisodeSpec":
        obj = json.loads(text)
        if not isinstance(obj, Mapping):
            raise ValueError("Apple episode spec must be a mapping")
        if obj.get("schema") != SPEC_SCHEMA:
            raise ValueError("unknown Apple episode spec schema")
        if not isinstance(obj.get("task_kwargs", {}), Mapping):
            raise ValueError("task_kwargs must be a mapping")
        mock_turns = obj.get("mock_turns", ())
        if not isinstance(mock_turns, (list, tuple)) or any(
            not isinstance(turn, Mapping) for turn in mock_turns
        ):
            raise ValueError("mock_turns must contain mappings")
        obj["mock_turns"] = tuple(mock_turns)
        spec = cls(**obj)
        if spec.condition not in ("benign", "sabotage"):
            raise ValueError("unknown episode condition")
        for value in (spec.max_turns, spec.max_tokens):
            if type(value) is not int or value <= 0:
                raise ValueError("turn and token budgets must be positive integers")
        if type(spec.seed) is not int:
            raise ValueError("seed must be an integer")
        if type(spec.temperature) not in (int, float) or not math.isfinite(spec.temperature):
            raise ValueError("temperature must be numeric and finite")
        return spec


class EpisodeRuntimeAdapter:
    """RuntimeAdapter wrapping the registry-selected MLX or mock implementation."""

    def __init__(self, runtime: Any, clock: Clock) -> None:
        self.name = runtime.name if runtime is not None else WORKLOAD_KIND
        self.runtime = runtime
        self.clock = clock
        self.spec: EpisodeSpec | None = None
        self.task: AgentTask | None = None
        self.flags: list[str] = []
        self.prepared: dict[str, Any] = {}
        self._runtime_ready = False
        self._failed_episode_result: RuntimeResult | None = None

    def prepare(
        self, config: BenchmarkConfig, context: RunContext | None = None,
    ) -> AdapterResult:
        self.flags = []
        self.prepared = {}
        self.spec = None
        self.task = None
        self._runtime_ready = False
        self._failed_episode_result = None
        if config.hardware_target.runtime_backend not in (RuntimeBackend.MOCK, RuntimeBackend.MLX):
            return AdapterResult(
                ok=False, failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message="align_episode supports only mock and mlx backends",
            )
        try:
            self.spec = EpisodeSpec.from_text(config.workload_profile.prompt_text or "")
            module_name, factory_name = self.spec.task_factory.split(":", 1)
            factory = getattr(importlib.import_module(module_name), factory_name)
            kwargs = dict(self.spec.task_kwargs)
            if "clock" in inspect.signature(factory).parameters:
                kwargs["clock"] = self.clock
            self.task = factory(**kwargs)
            if not isinstance(self.task, AgentTask):
                raise TypeError("task factory must return AgentTask")
            # Validate startup before idle admission; the measured run resets again.
            # AgentTask factories must tolerate repeated reset(seed) calls.
            self.task.reset(self.spec.seed)
            self.task.system_prompt(self.spec.condition)
            self.task.user_prompt()
        except Exception as exc:
            self.flags.append(f"task_unavailable:{type(exc).__name__}:{exc}")
            return AdapterResult(
                ok=False, failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message=self.flags[-1], metadata={"align_episode_flags": list(self.flags)},
            )
        try:
            if config.hardware_target.runtime_backend == RuntimeBackend.MLX:
                source = Path(config.model.source or "").expanduser()
                if not config.model.source or not source.is_dir():
                    raise ValueError("local_model_mirror_required")
            result = self.runtime.prepare(config, context)
            self._runtime_ready = result.ok
            self.prepared = dict(result.metadata)
            return result
        except Exception as exc:
            self.flags.append(f"runtime_unavailable:{type(exc).__name__}:{exc}")
            return AdapterResult(
                ok=False, failure_reason=FailureReason.RUNTIME_UNAVAILABLE,
                message=self.flags[-1], metadata={"align_episode_flags": list(self.flags)},
            )

    def identity_projection_metadata(self, config: BenchmarkConfig) -> dict[str, Any]:
        """Project the same fixed model/sampler/policy as measured episode bundles."""
        spec = EpisodeSpec.from_text(config.workload_profile.prompt_text or "")
        projector = getattr(self.runtime, "identity_projection_metadata", None)
        if callable(projector):
            metadata = dict(projector(config))
        else:
            # MockRuntimeAdapter has no readiness probe. These are its actual
            # deterministic tokenizer/sampler identities; prepare owns the artifact.
            metadata = {
                "tokenizer": {
                    "backend": "mock", "identifier": "joulewise.mock_tokenizer.v1",
                    "revision": self.prepared.get("version"),
                    "class": "MockRuntimeAdapter", "vocab_size": None,
                },
                "sampler": {"kind": "greedy", "temperature": 0.0, "pinned": True},
            }
        metadata["model"] = {
            "name": config.model.name, "source": config.model.source,
            "revision": config.model.revision,
            "artifact_identity": self.prepared.get("model_artifact_identity"),
        }
        metadata["sampler"] = {
            **metadata.get("sampler", {}),
            # Generation stays greedy, but a mismatched registered request must
            # have a distinct identity and retain the endpoint's mismatch flag.
            "requested_temperature": spec.temperature,
            "max_tokens": spec.max_tokens,
        }
        metadata["output_policy"] = {
            "name": "agent_episode",
            "requested_tokens": spec.max_turns * spec.max_tokens,
            "max_turns": spec.max_turns,
            "max_tokens_per_turn": spec.max_tokens,
            "stop_condition": "episode_returns_or_turn_budget_reached",
        }
        return metadata

    def warmup(
        self, config: BenchmarkConfig, context: RunContext | None = None,
    ) -> AdapterResult:
        if not self._runtime_ready:
            return AdapterResult(ok=True, metadata={"flags": list(self.flags)})
        try:
            warm_config = config
            if self.task is not None and self.spec is not None:
                self.task.reset(self.spec.seed)
                warm_config = replace(config, workload_profile=replace(
                    config.workload_profile,
                    prompt_text=self.task.system_prompt(self.spec.condition) + "\n" + self.task.user_prompt(),
                ))
            result = self.runtime.warmup(warm_config, context)
            if not result.ok:
                self.flags.append(f"warmup_failed:{result.message}")
        except Exception as exc:
            self.flags.append(f"warmup_failed:{type(exc).__name__}:{exc}")
        return AdapterResult(ok=True, metadata={"flags": list(self.flags)})

    def run_workload(
        self, config: BenchmarkConfig, context: RunContext | None = None,
    ) -> RuntimeResult:
        if self.spec is None or self.task is None or not self._runtime_ready:
            # A prepare failure has no measurable episode or condition label.
            raise AdapterFailure(
                FailureReason.RUNTIME_UNAVAILABLE, "align_episode was not prepared"
            )
        start = self.clock.stamp()
        episode_id = context.run_id if context is not None else config.run_id or "align_episode"
        domain = f"joulewise.monotonic:{episode_id}"
        transcript: list[ChatMessage] = []
        turns: list[Turn] = []
        events: list[RuntimeEvent] = []
        flags = list(self.flags)
        spec = self.spec
        endpoint = MlxEndpoint(
            self.runtime, config, self.clock, episode_domain=domain,
            prepare_metadata=self.prepared, mock_turns=spec.mock_turns if spec else (),
        )
        task = self.task
        model_returned_tokens = False
        if spec is not None and task is not None and self._runtime_ready:
            try:
                task.reset(spec.seed)
                transcript = [
                    ChatMessage("system", task.system_prompt(spec.condition)),
                    ChatMessage("user", task.user_prompt()),
                ]
                for index in range(spec.max_turns):
                    event_start = len(endpoint.events)
                    result = endpoint.chat(
                        transcript, tools=task.tool_schemas(), max_tokens=spec.max_tokens,
                        temperature=spec.temperature, seed=spec.seed,
                    )
                    # Integer token counts establish that a model call returned work.
                    model_returned_tokens |= result.completion_tokens > 0
                    events.extend(endpoint.events[event_start:])
                    transcript.append(ChatMessage(
                        "assistant", str(result.raw_usage.get("raw_text", result.content))
                    ))
                    calls: list[ToolCall] = []
                    for call_index, call in enumerate(result.tool_calls):
                        tool_start = self.clock.stamp()
                        phase = f"align_tool_{index}_{call_index}"
                        events.append(RuntimeEvent(
                            tool_start.epoch_s, "phase_start", phase, call.name,
                            {"align_turn_index": index, "tool_call_id": call.call_id},
                        ))
                        try:
                            output = task.call_tool(call.name, call.arguments_json)
                            if not isinstance(output, str):
                                output = json.dumps(output, sort_keys=True)
                                flags.append(f"tool_result_coerced:{index}:{call_index}")
                        except Exception as exc:
                            output = json.dumps({"error": f"{type(exc).__name__}:{exc}"})
                            flags.append(f"tool_error:{index}:{call_index}")
                        tool_end = self.clock.stamp()
                        events.append(RuntimeEvent(
                            tool_end.epoch_s, "phase_end", phase, call.name,
                            {"align_turn_index": index, "tool_call_id": call.call_id},
                        ))
                        calls.append(ToolCall(
                            name=call.name, start_ns=monotonic_ns(tool_start),
                            end_ns=monotonic_ns(tool_end),
                            args_bytes=len(call.arguments_json.encode("utf-8")),
                            result_bytes=len(output.encode("utf-8")),
                        ))
                        transcript.append(ChatMessage(
                            "tool", output, name=call.name, tool_call_id=call.call_id
                        ))
                    # Turn is the model-call interval per records.py. Tool
                    # intervals follow it but remain grouped under that turn;
                    # records.v1 does not require tool containment.
                    turns.append(Turn(
                        index=index, start_ns=result.start_ns, end_ns=result.end_ns,
                        context_tokens=result.cached_prompt_tokens,
                        prefill_tokens=result.prompt_tokens - result.cached_prompt_tokens,
                        decode_tokens=result.completion_tokens,
                        hidden_tokens=result.reasoning_tokens,
                        first_token_ns=result.first_token_ns,
                        tool_calls=tuple(calls),
                    ))
                    if not result.tool_calls:
                        break
                else:
                    flags.append("turn_budget_reached")
            except Exception as exc:
                flags.append(f"episode_error:{type(exc).__name__}:{exc}")
        flags.extend(endpoint.flags)
        if not model_returned_tokens:
            # UNKNOWN_ERROR maps to failed; RUNTIME_UNAVAILABLE maps to unsupported
            # and is reserved here for configurations rejected during prepare.
            raise AdapterFailure(
                FailureReason.UNKNOWN_ERROR,
                "align_episode:no_model_call_returned_tokens; " + "; ".join(flags),
            )
        end = self.clock.stamp()
        main_score = None
        side_success = None
        if task is not None:
            try:
                main_score = task.score_main(transcript)
                if main_score is not None and (
                    type(main_score) not in (int, float) or not math.isfinite(main_score)
                ):
                    flags.append("task_scoring_error:main_score_not_finite_numeric")
                    main_score = None
                side_success = task.score_side(transcript)
            except Exception as exc:
                flags.append(f"task_scoring_error:{type(exc).__name__}:{exc}")
        flags.append("single_request_summary_fields_not_episode_metrics:ttft_s,decode_latency_s,energy_token_j")
        flags.append("power_trace_join_in_run_bundle")
        flags.append("episode_interval_excludes_scoring_and_serialization_tail")
        episode = Episode(
            episode_id=episode_id,
            task_pair=task.task_pair if task is not None else "unavailable",
            condition=spec.condition,
            agent_model=config.model.name, endpoint=endpoint.identity,
            seed=spec.seed if spec else 0, clock_domain=domain,
            start_ns=monotonic_ns(start), end_ns=max(monotonic_ns(start), monotonic_ns(end)),
            turns=tuple(turns), main_task_score=main_score,
            side_task_success=side_success,
            hardware={
                "run_bundle_id": episode_id,
                "paired_clock_stamps_ns": [_stamp_record(start), _stamp_record(end)],
                "controller_clock_domain": "joulewise.controller.epoch_ns",
                "runtime_identity": {
                    key: self.prepared.get(key) for key in (
                        "mlx_version", "mlx_lm_version", "model_artifact_identity"
                    )
                },
                "power_scope": "existing controller rail manifest",
            },
            flags=tuple(dict.fromkeys(flags)),
        )
        transcript_text = "".join(
            json.dumps(to_jsonable(message), sort_keys=True) + "\n" for message in transcript
        )
        prompt = prompt_provenance(endpoint.prompt_token_ids, text=None)
        if not endpoint.prompt_token_ids:
            prompt["realized_token_count"] = None
        identity = self.identity_projection_metadata(config)
        stop = "episode_returned"
        if any(flag.startswith("turn_token_budget_reached:") for flag in flags):
            stop = "turn_token_budget_reached"
        if "turn_budget_reached" in flags:
            stop = "turn_budget_reached"
        if any(flag.startswith("episode_error:") for flag in flags):
            stop = "episode_error"
        if any(flag.startswith("endpoint_error:") for flag in flags):
            stop = "endpoint_error"
        outcome = {
            "stop_condition": stop,
            "emitted_tokens": sum(t.decode_tokens for t in turns),
        }
        runtime_result = RuntimeResult(
            events=events,
            output_artifacts={
                "align_episode.json": to_json(episode) + "\n",
                "align_transcript.jsonl": transcript_text,
                "align_turns.jsonl": "".join(
                    json.dumps(row, sort_keys=True) + "\n" for row in endpoint.turn_provenance
                ),
            },
            token_count=sum(t.prefill_tokens + t.context_tokens + t.decode_tokens for t in turns),
            output_token_count=sum(t.decode_tokens for t in turns),
            workload_provenance={
                "kind": WORKLOAD_KIND,
                "prompt": prompt,
                "generator": {"name": WORKLOAD_KIND, "version": SPEC_SCHEMA},
                "tokenizer": endpoint.tokenizer_provenance,
                "model": identity["model"],
                "sampler": identity["sampler"],
                "output_policy": {
                    **identity["output_policy"],
                    # Strict bundle validation requires the realized count; the
                    # governed identity projects only the fixed policy fields.
                    "emitted_tokens": outcome["emitted_tokens"],
                },
                "episode_outcome": outcome,
                "episode_spec_sha256": hashlib.sha256(
                    (config.workload_profile.prompt_text or "").encode("utf-8")
                ).hexdigest(),
                "transcript_sha256": hashlib.sha256(transcript_text.encode("utf-8")).hexdigest(),
                "endpoint_identity": endpoint.identity,
                "cache_policy": "full_prompt_each_turn",
                "flags": list(episode.flags),
            },
            metadata={"align_episode": {"id": episode_id, "flags": list(episode.flags), **outcome}},
        )

        if stop in ("endpoint_error", "episode_error"):
            # Like non-align MLX, a runtime fault is a failed execution, not a
            # physical refusal. Keep the partial evidence in memory until the
            # controller stops sampling and invokes EvidenceCustodyProvider.
            self._failed_episode_result = runtime_result
            raise AdapterFailure(
                FailureReason.UNKNOWN_ERROR,
                "align_episode:" + json.dumps(outcome, sort_keys=True) + "; "
                + "; ".join(flag for flag in flags if flag.startswith(("endpoint_error:", "episode_error:"))),
            )
        return runtime_result

    def salvage_custody(self, context: RunContext) -> list[dict[str, Any]]:
        """Persist buffered partial evidence after the controller stops sampling."""
        result = self._failed_episode_result
        if result is None:
            return []
        artifacts = {
            **result.output_artifacts,
            "align_failure.json": json.dumps({
                "episode_outcome": result.workload_provenance["episode_outcome"],
                "workload_provenance": result.workload_provenance,
                "token_count": result.token_count,
                "output_token_count": result.output_token_count,
            }, sort_keys=True, allow_nan=False) + "\n",
            "align_runtime_events.jsonl": "".join(
                json.dumps(to_jsonable(event), sort_keys=True, allow_nan=False) + "\n"
                for event in result.events
            ),
        }
        paths = []
        for name, content in artifacts.items():
            path = context.outputs_dir / name
            if path.exists():
                if path.read_text(encoding="utf-8") != content:
                    raise ValueError(f"partial episode artifact differs: {name}")
            else:
                # Do not overwrite existing bundle evidence, including on retry.
                with path.open("x", encoding="utf-8") as handle:
                    handle.write(content)
            paths.append(path)
        context.acknowledge_custody("align-episode-failure", paths)
        return [{"acknowledged": True, "artifacts": sorted(artifacts)}]

    def cleanup(
        self, config: BenchmarkConfig, context: RunContext | None = None,
    ) -> AdapterResult:
        if self.runtime is None:
            return AdapterResult(ok=True)
        result = self.runtime.cleanup(config, context)
        if self._failed_episode_result is not None:
            failed = self._failed_episode_result
            return replace(result, metadata={
                **result.metadata,
                "align_episode": failed.metadata["align_episode"],
                "episode_outcome": failed.workload_provenance["episode_outcome"],
            })
        return result


def read_episode_bundle(bundle: Path) -> Episode:
    """Return the immutable episode joined with the controller trace and anchor.

    No native plist is parsed here and no finalized file is modified. The
    serialized episode and trace remain separately authenticated bundle inputs.
    """
    reader = BundleReader(Path(bundle))
    episode = from_json(Episode, (Path(bundle) / "outputs" / "align_episode.json").read_text())
    metadata = reader.metadata()
    evidence = metadata.get("uncertainty_evidence")
    stamps = tuple(_restore_stamp(row) for row in episode.hardware["paired_clock_stamps_ns"])
    mapping, mapping_flags = stamp_mapping(
        stamps, episode_domain=episode.clock_domain, evidence=evidence
    )
    rows = reader.trace_rows()
    samples = [
        PowerSample(
            timestamp_s=float(row["timestamp_s"]), power_w=float(row["power_w"]),
            source=row.get("source", "mock"), rail=row.get("rail") or None,
            interval_start_s=float(row["interval_start_s"]) if row.get("interval_start_s") else None,
            interval_end_s=float(row["interval_end_s"]) if row.get("interval_end_s") else None,
        )
        for row in rows
    ]
    traces, trace_flags = power_records(
        samples,
        nominal_interval_ns=round(NS_PER_SECOND / reader.config().sampling.power_hz),
        evidence=evidence,
    )
    flags = [
        flag for flag in episode.flags if flag != "power_trace_join_in_run_bundle"
    ]
    flags.extend(mapping_flags)
    flags.extend(trace_flags)
    if not traces:
        flags.append("power_unavailable:no_bundle_trace")
    return replace(
        episode, power_traces=traces, clock_mappings=(mapping,),
        flags=tuple(dict.fromkeys(flags)),
    )
