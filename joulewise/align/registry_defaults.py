"""Default runner factories for the lane components (integration wiring).

List ``"joulewise.align.registry_defaults"`` under a matrix's ``imports`` to
install, besides the mock world's own ``mock.*`` factories (``mock.power`` is
the synthetic sampler):

- task ``shade``: ``ShadeTask``; config keys ``task_pair`` (default: the
  cell's task pair), ``upstream`` (``PinnedUpstream`` keyword arguments),
  ``judge_endpoint`` (``OpenAICompatEndpoint`` keyword arguments) and the
  remaining ``ShadeTask`` keyword arguments.
- endpoint ``openai_compat``: ``OpenAICompatEndpoint(**config)``.
- samplers ``nvml`` and ``ina3221``: ``NvmlSampler`` and ``Ina3221Sampler``.
  Unless the config names its own ``clock_domain``, a sampler timestamps with
  the episode clock in the episode clock domain, so the runner needs no clock
  mapping for it.

Each lane module is imported only when its factory runs.
"""

from __future__ import annotations

from typing import Any, Mapping

from joulewise.align.runner import (
    FactoryContext, register_endpoint_factory, register_sampler_factory, register_task_factory,
)


def _openai_compat(config: Mapping[str, Any], context: FactoryContext | None = None) -> Any:
    from joulewise.align.endpoints import OpenAICompatEndpoint
    parameters = dict(config)
    return OpenAICompatEndpoint(parameters.pop("base_url"), parameters.pop("model"), **parameters)


def _shade_task(config: Mapping[str, Any], context: FactoryContext) -> Any:
    from joulewise.align.shade import PinnedUpstream, ShadeTask
    parameters = dict(config)
    pair = parameters.pop("task_pair", parameters.pop("pair", context.task_pair))
    upstream = parameters.pop("upstream", None)
    judge = parameters.pop("judge_endpoint", None)
    return ShadeTask(pair, upstream=PinnedUpstream(**upstream) if upstream is not None else None,
                     judge_endpoint=_openai_compat(judge) if judge is not None else None,
                     **parameters)


def _episode_clock(config: Mapping[str, Any], context: FactoryContext,
                   clock_key: str) -> dict[str, Any]:
    parameters = dict(config)
    if "clock_domain" not in parameters:
        parameters["clock_domain"] = context.clock_domain
        parameters[clock_key] = context.clock
    return parameters


def _nvml(config: Mapping[str, Any], context: FactoryContext) -> Any:
    from joulewise.align.power.nvml import NvmlSampler
    return NvmlSampler(**_episode_clock(config, context, "clock_ns"))


def _ina3221(config: Mapping[str, Any], context: FactoryContext) -> Any:
    from joulewise.align.power.ina3221 import Ina3221Sampler
    return Ina3221Sampler(**_episode_clock(config, context, "clock"))


def register_defaults() -> None:
    """Install the default factories; repeated calls are idempotent."""
    from joulewise.align.mock_world import register_mock_factories
    register_mock_factories()
    register_task_factory("shade", _shade_task)
    register_endpoint_factory("openai_compat", _openai_compat)
    register_sampler_factory("nvml", _nvml)
    register_sampler_factory("ina3221", _ina3221)


register_defaults()

__all__ = ["register_defaults"]
