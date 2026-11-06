"""Run the pinned MLX generation method with an ALIGN-local stream receiver.

The prepared adapter and its native module remain untouched. Only this view's
stream is wrapped; all other attributes and bound helpers use the same runtime.
"""
from __future__ import annotations

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter


class _GenerationRuntime:
    def __init__(self, runtime, stream):
        self._runtime = runtime
        self._mlx_lm = stream

    def __getattr__(self, name):
        return getattr(self._runtime, name)


def generate_turn(runtime, stream, *args, **kwargs):
    """Use the unchanged core loop without rebinding runtime/module attributes."""
    return MlxRuntimeAdapter._generate(_GenerationRuntime(runtime, stream), *args, **kwargs)
