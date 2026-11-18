"""Run the pinned MLX generation method with an ALIGN-local stream receiver.

The prepared adapter and its native module remain untouched. The ALIGN view
wraps the stream and lets the cached path share its prefill/decode marker.
"""
from __future__ import annotations

from dataclasses import replace

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter


class _GenerationRuntime:
    def __init__(self, runtime, stream, *, cache_accounting):
        self._runtime = runtime
        self._mlx_lm = stream
        self._cache_accounting = cache_accounting
        self._prefill_end = None

    def _event(self, event_type, phase, message, metadata=None):
        # Both phase markers describe the same boundary. Reuse its stamp
        # so token 0 is stamped on the very next clock read (RL-182a).
        if self._prefill_end is not None and (event_type, phase) == ("phase_start", "decode"):
            return replace(self._prefill_end, event_type=event_type, phase=phase,
                           message=message, metadata=metadata or {})
        event = self._runtime._event(event_type, phase, message, metadata)
        if self._cache_accounting and (event_type, phase) == ("phase_end", "prefill"):
            self._prefill_end = event
        return event

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
    view = _GenerationRuntime(owner, stream, cache_accounting=kwargs.get("cache_accounting", False))
    return MlxRuntimeAdapter._generate(view, *args, **kwargs)
