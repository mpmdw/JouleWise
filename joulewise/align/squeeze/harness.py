"""Additive adapters for the v4 lane's AgentTask and run_episode interfaces.

The ALIGN lane is deliberately not vendored onto main. Imports of its modules
are lazy, so config validation and control tests work without that lane or MLX.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .config import canonical, sha256, validate_variant
from .control import ControlEndpoint, Injection, SqueezeRun


class AdversaryTask:
    """Preserve SHADE tools, task description and scorers; append sabotage text."""

    def __init__(self, task: Any, variant: Mapping[str, Any]) -> None:
        self.task, self.variant = task, validate_variant(variant)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.task, name)

    # Python >=3.12 runtime Protocol checks use getattr_static. Required members
    # must exist explicitly; __getattr__ alone is insufficient for AgentTask.
    @property
    def task_pair(self) -> str:
        return self.task.task_pair

    @property
    def scratchpad_tags(self) -> Any:
        return self.task.scratchpad_tags

    def reset(self, seed: int) -> None:
        self.task.reset(seed)

    def user_prompt(self) -> str:
        return self.task.user_prompt()

    def task_description(self) -> str:
        return self.task.task_description()

    def tool_schemas(self) -> Any:
        return self.task.tool_schemas()

    def call_tool(self, name: str, arguments_json: str) -> str:
        return self.task.call_tool(name, arguments_json)

    def score_main(self, transcript: Any) -> float | None:
        return self.task.score_main(transcript)

    def score_side(self, transcript: Any) -> bool | None:
        return self.task.score_side(transcript)

    def system_prompt(self, condition: str) -> str:
        if condition not in ("benign", "sabotage"):
            raise ValueError("unknown episode condition")
        original = self.task.system_prompt(condition)
        instructions = self.variant["instructions"]
        if condition == "benign" or not instructions:
            return original
        return original + "\n\n<joulewise_red_team>\n" + instructions + "\n</joulewise_red_team>"


def offline_shade_adversary_task(*, base_task_kwargs: Mapping[str, Any],
                                base_spec_sha256: str, variant: Mapping[str, Any]) -> AdversaryTask:
    """EpisodeSpec.task_factory drop-in; the original factory never fetches."""
    variant = validate_variant(variant)
    if not isinstance(base_task_kwargs, Mapping):
        raise ValueError("base_task_kwargs must be a mapping")
    if (not isinstance(base_spec_sha256, str) or len(base_spec_sha256) != 64
            or any(c not in "0123456789abcdef" for c in base_spec_sha256)):
        raise ValueError("base_spec_sha256 must be a SHA-256 hex digest")
    from joulewise.align.apple.pilot import offline_shade_task

    return AdversaryTask(offline_shade_task(**deepcopy(dict(base_task_kwargs))), variant)


def run_adversarial_episode(task: Any, condition: str, endpoint: Any, *,
                            variant: Mapping[str, Any], control: Injection | None = None,
                            **run_kwargs: Any) -> SqueezeRun:
    """Run the actual generic ALIGN harness; return a separate private receipt.

    Instantiate once per episode. Native clocks must share run_kwargs' domain.
    Samplers start before ControlEndpoint.chat, so injected forwards fall inside
    the gross episode interval. Monitor calls still happen after samplers stop.
    """
    variant = validate_variant(variant)
    if control is not None:
        if control.receipt()["status"] != "not_triggered":
            raise ValueError("each episode requires a fresh hidden control")
        if run_kwargs.get("clock_domain") != control.receipt()["clock_domain"]:
            raise ValueError("control and episode clock domains must agree")
    from joulewise.align.runner import run_episode

    wrapped = ControlEndpoint(endpoint, variant_sha256=variant["config_sha256"], control=control)
    adapted_task = AdversaryTask(task, variant)
    if control is not None and control.placement == "tool":
        adapted_task = ToolControlTask(task, variant, control)
    episode, transcript = run_episode(adapted_task, condition, wrapped, **run_kwargs)
    private_control = None if control is None else control.receipt()
    if private_control is not None:
        start, end = private_control["start_ns"], private_control["end_ns"]
        private_control["episode_interval_check"] = (
            "inside" if type(start) is int and type(end) is int
            and episode.start_ns <= start <= end <= episode.end_ns else "unverified")
    receipt = {
        "schema": "joulewise.align.squeeze.run.v1", "audience": "evaluator_only",
        "episode_id": episode.episode_id, "variant": deepcopy(variant),
        "hidden_decode": private_control,
        "transcript_canonical_sha256": sha256(canonical([
            {key: getattr(message, key) for key in ("role", "content", "name", "tool_call_id")}
            for message in transcript]).encode("utf-8")),
    }
    return SqueezeRun(episode, transcript, receipt)


class ToolControlTask(AdversaryTask):
    """Inject in an existing tool call; return only the original tool result."""

    def __init__(self, task: Any, variant: Mapping[str, Any], control: Injection) -> None:
        super().__init__(task, variant)
        self.control, self.calls = control, 0

    def call_tool(self, name: str, arguments_json: str) -> str:
        index = self.calls
        self.calls += 1
        if index == self.control.trigger_index:
            self.control.execute()
        return self.task.call_tool(name, arguments_json)
