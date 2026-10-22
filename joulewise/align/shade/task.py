"""Expose pinned SHADE-Arena task definitions and evaluations as AgentTask.

Optional upstream dependencies are imported only while operating on a task.
Failures are retained in flags and produce missing scores, never invented data.
"""

from __future__ import annotations

import asyncio
import importlib
import json
import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Coroutine, Mapping, Sequence

from joulewise.align.interfaces import ChatEndpoint, ChatMessage
from joulewise.align.shade.upstream import PinnedUpstream


class TaskPairList(tuple):
    """Tuple-compatible discovery output retaining unavailable-source flags."""

    flags: tuple[str, ...]

    def __new__(cls, pairs: Sequence[str] = (), *, flags: Sequence[str] = ()) -> "TaskPairList":
        value = super().__new__(cls, pairs)
        value.flags = tuple(flags)
        return value


def list_task_pairs(upstream: PinnedUpstream | None = None) -> TaskPairList:
    """Enumerate task-definition directories in the verified pinned source."""
    source = upstream or PinnedUpstream()
    root = source.prepare()
    if root is None:
        return TaskPairList(flags=source.flags)
    return TaskPairList(tuple("shade/" + p.parent.name for p in sorted(
        (root / "task_pairs").glob("*/task_definition.py"))), flags=source.flags)


def _sync(coroutine: Coroutine[Any, Any, Any]) -> Any:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coroutine).result()


class _Column(list):
    """The single-row operations used by all five upstream score normalizers."""

    def apply(self, function: Any) -> "_Column":
        return _Column(function(value) for value in self)

    def __ge__(self, other: Any) -> "_Column":
        return _Column(value >= other for value in self)


class _ScoreRow(dict):
    """Run upstream add_score_columns without a core dependency on pandas."""

    @property
    def transcript(self) -> _Column:
        return self["transcript"]


@dataclass
class _JudgeReply:
    messages: list[dict[str, Any]]

    def __str__(self) -> str:
        # The calendar side evaluator accepts a string fallback; expose only the
        # judge's answer, so a secret in the judge prompt cannot satisfy scoring.
        return self.messages[-1]["content"]


class _Judge:
    def __init__(self, endpoint: ChatEndpoint | None, flags: list[str], *,
                 max_tokens: int, temperature: float, seed: int | None) -> None:
        self.endpoint, self.flags = endpoint, flags
        self.max_tokens, self.temperature, self.seed = max_tokens, temperature, seed

    async def query(self, query: str = "", *, messages: Sequence[Mapping[str, Any]] = (),
                    **kwargs: Any) -> _JudgeReply:
        if self.endpoint is None:
            self.flags.append("llm_judge_endpoint_missing")
            raise RuntimeError("judge endpoint unavailable")
        self.flags.append("llm_judge:" + self.endpoint.identity)
        converted = [ChatMessage(m["role"], m.get("content") or "", m.get("name"),
                                 m.get("tool_call_id")) for m in messages]
        # Endpoints are synchronous; upstream calendar gathers four judge calls.
        # Keep their scripted/seed order deterministic while preserving its four calls.
        result = self.endpoint.chat(converted, max_tokens=self.max_tokens,
                                    temperature=self.temperature, seed=self.seed)
        self.flags.extend(result.raw_usage.get("joulewise", {}).get("flags", ()))
        self.flags.append("judge_reply_text_adapter")
        return _JudgeReply([{"role": "assistant", "content": result.content}])


class ShadeTask:
    """One fresh mock environment for a public task pair.

    score_main follows the pinned evaluator's add_score_columns normalization,
    including its pair-specific transforms. flags must be copied to Episode.flags.
    reset(seed) rebuilds upstream's fixed initial world; upstream has no seed API.
    """

    scratchpad_tags = ("<thinking>", "</thinking>")

    def __init__(self, task_pair: str, *, upstream: PinnedUpstream | None = None,
                 judge_endpoint: ChatEndpoint | None = None, give_hint: bool = True,
                 judge_max_tokens: int = 4096, judge_temperature: float = 0.0) -> None:
        self.task_pair = "shade/" + task_pair.removeprefix("shade/")
        self.upstream = upstream or PinnedUpstream()
        self.judge_endpoint = judge_endpoint
        self.give_hint = give_hint
        self.judge_max_tokens, self.judge_temperature = judge_max_tokens, judge_temperature
        self.flags: list[str] = []
        self.evaluation_outputs: dict[str, Any] = {}
        self._definition: Any = None
        self._runtime: Any = None
        self._evaluation: Any = None
        self._schema: tuple[Mapping[str, Any], ...] = ()
        self._tool_history: list[tuple[str, dict[str, Any]]] = []
        self.seed = 0

    def _source_flags(self) -> None:
        self.flags.extend(f for f in self.upstream.flags if f not in self.flags)

    def reset(self, seed: int) -> None:
        self.seed = seed
        self.flags.clear()
        self.evaluation_outputs.clear()
        self._definition = self._runtime = self._evaluation = None
        self._schema = ()
        self._tool_history.clear()
        name = self.task_pair.removeprefix("shade/")
        if not name.isidentifier():
            self.flags.append("unknown_task_pair")
            return
        try:
            with self.upstream.activate() as root:
                if root is None:
                    return
                if self.task_pair not in list_task_pairs(self.upstream):
                    self.flags.append("unknown_task_pair")
                    return
                importlib.import_module("utils.path_utils").set_project_root(root)
                definition_module = importlib.import_module(f"task_pairs.{name}.task_definition")
                runtime_module = importlib.import_module("utils.functions_runtime")
                evaluation_module = importlib.import_module(f"task_evaluation.{name}_evaluation")
                definition = definition_module.TaskDefinition()
                environment = definition.environment
                runtime = runtime_module.FunctionsRuntime()
                for tool in environment.available_tools:
                    runtime.register_function(tool)
                self._definition, self._runtime = definition, runtime
                judge = _Judge(self.judge_endpoint, self.flags, max_tokens=self.judge_max_tokens,
                               temperature=self.judge_temperature, seed=seed)
                self._evaluation = evaluation_module.TaskEvaluation(definition, evaluator_llm=judge)
                self._schema = tuple({
                    "type": "function", "function": {
                        "name": tool.name, "description": tool.description,
                        "parameters": tool.parameters.model_json_schema()}}
                    for tool in runtime.functions.values())
                self.flags.append("upstream_fixed_initial_state")
        except Exception as exc:
            self._definition = self._runtime = self._evaluation = None
            self._schema = ()
            self.flags.append("task_load_error:" + type(exc).__name__)
        finally:
            self._source_flags()

    def _ready(self) -> bool:
        if self._definition is None:
            self.flags.append("task_not_ready")
            return False
        return True

    def system_prompt(self, condition: str) -> str:
        if not self._ready():
            return ""
        try:
            with self.upstream.activate() as root:
                if root is None:
                    return ""
                if condition == "benign":
                    return self._definition.system_message_no_secondary_task()
                if condition != "sabotage":
                    self.flags.append("unknown_condition")
                    return ""
                return self._definition.system_message_suspicious(give_hint=self.give_hint)
        except Exception as exc:
            self.flags.append("system_prompt_error:" + type(exc).__name__)
            return ""
        finally:
            self._source_flags()

    def user_prompt(self) -> str:
        if not self._ready():
            return ""
        return self._definition.user_query

    def task_description(self) -> str:
        """The main task only; the monitor never receives the secret instruction."""
        return self.user_prompt()

    def tool_schemas(self) -> Sequence[Mapping[str, Any]]:
        return self._schema

    def call_tool(self, name: str, arguments_json: str) -> str:
        if not self._ready():
            return "Task environment unavailable."
        try:
            arguments = json.loads(arguments_json)
            if not isinstance(arguments, dict):
                self.flags.append("tool_arguments_not_object")
                return "Tool arguments must be a JSON object."
            self._tool_history.append((name, arguments))
            with self.upstream.activate() as root:
                if root is None:
                    return "Task environment unavailable."
                result, error = self._runtime.run_function(self._definition.environment, name, arguments)
                if error is not None:
                    self.flags.append("tool_error:" + name)
                    return error
                formatter = importlib.import_module("utils.pipeline_elements").tool_result_to_str
                return formatter(result)
        except Exception as exc:
            self.flags.append("tool_error:" + type(exc).__name__)
            return "Tool failed: " + type(exc).__name__
        finally:
            self._source_flags()

    def _conversation(self, transcript: Sequence[ChatMessage]) -> list[dict[str, Any]]:
        module = importlib.import_module("utils.functions_runtime")
        output = []
        history_index = 0
        for index, message in enumerate(transcript):
            item: dict[str, Any] = {"role": message.role, "content": message.content}
            if message.role == "assistant":
                calls = getattr(message, "tool_calls", ())
                upstream_calls = [module.FunctionCall(function=c.name,
                    args=json.loads(c.arguments_json), id=c.call_id) for c in calls]
                if not calls:
                    for following in transcript[index + 1:]:
                        if following.role != "tool":
                            break
                        if history_index < len(self._tool_history):
                            name, arguments = self._tool_history[history_index]
                            upstream_calls.append(module.FunctionCall(function=name, args=arguments,
                                                                      id=following.tool_call_id))
                            history_index += 1
                else:
                    history_index += len(calls)
                item["tool_calls"] = upstream_calls or None
                thought = getattr(message, "reasoning_text", "")
                if thought:
                    item["content"] = "<thinking>" + thought + "</thinking>\n" + item["content"]
            elif message.role == "tool":
                item.update(tool_call_id=message.tool_call_id, tool_call_function=message.name,
                            error=None)
            output.append(item)
        return output

    def _evaluate(self, which: str, transcript: Sequence[ChatMessage]) -> Any:
        if not self._ready():
            return None
        try:
            with self.upstream.activate() as root:
                if root is None:
                    return None
                evaluation = self._evaluation
                if which == "main":
                    result = _sync(evaluation.evaluate_main_task(
                        conversation=self._conversation(transcript),
                        environment=self._definition.environment, evaluator_llm=evaluation.evaluator_llm,
                        is_llm_conversation=True, remove_thinking_tags=True))
                else:
                    result = _sync(evaluation.evaluate_side_task(
                        environment=self._definition.environment, evaluator_llm=evaluation.evaluator_llm))
                self.evaluation_outputs[which] = result
                if which == "side":
                    if isinstance(result, bool):
                        return result
                    self.flags.append("side_evaluation_not_boolean")
                    return None
                # These exact operations are shared by all five pinned pandas
                # normalizers: transcript.apply, column assignment, >= threshold.
                row = _ScoreRow(transcript=_Column([{
                    "main_task_evaluation": result, "side_task_evaluation": False}]))
                evaluated = evaluation.add_score_columns(row)
                score = float(evaluated["main_task_evaluation"][0])
                if not math.isfinite(score):
                    self.flags.append("main_evaluation_nonfinite")
                    return None
                return score
        except Exception as exc:
            self.flags.append(which + "_evaluation_error:" + type(exc).__name__)
            return None
        finally:
            self._source_flags()

    def score_main(self, transcript: Sequence[ChatMessage]) -> float | None:
        return self._evaluate("main", transcript)

    def score_side(self, transcript: Sequence[ChatMessage]) -> bool | None:
        return self._evaluate("side", transcript)


__all__ = ["TaskPairList", "ShadeTask", "list_task_pairs"]
