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
    """Use the unchanged core loop without rebinding runtime/module attributes.

    The core runs against the runtime that owns ``runtime._generate``, exactly
    as the former ``runtime._generate(...)`` dispatch did. For a prepared
    adapter that is the adapter itself; for a delegating view (for example the
    D3 budget endpoint's render-only ``_RuntimeView``) it is the wrapped native
    runtime, so native generation still receives the real tokenizer while
    prompt rendering keeps using the view.
    """
    owner = getattr(getattr(runtime, '_generate', None), '__self__', runtime)
    return MlxRuntimeAdapter._generate(_GenerationRuntime(owner, stream), *args, **kwargs)
