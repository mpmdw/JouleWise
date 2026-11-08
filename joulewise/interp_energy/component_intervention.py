"""Explicit array-output component seams for desk JOULE-MAP experiments.

No architecture discovery, file I/O, telemetry, or numerical imports. An adapter
must place the seam at a residual *branch output*, not around the residual add.
For embeddings/LM heads the seam is the array output itself. Array tapes are
resident caller-owned values, built outside measurement; never activation hooks
that copy to the CPU inside a measured episode.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Callable, Iterable


class ComponentGate:
    """Keep weights resident while switching full / clamped / removed execution.

    full: run the component and return its output.
    clamped: run AND evaluate it, discard that output, return a tape entry.
    removed: never call it, return the SAME tape entry.

    A zero tape gives branch ablation; a base-output tape approximates the
    natural trajectory. The clamped/removed pair has identical downstream
    outputs, including during prefill. Cache writes inside the removed branch
    are intentionally absent; no other component may share that cache. MoE,
    tuple outputs, compiled graphs, and hybrid shared-state caches need an
    architecture-specific adapter and are not supported by this array seam.

    ``evaluate`` must force execution of a discarded lazy result. ``barrier``
    runs at both edges in ALL arms. This instrumented schedule is not a native
    fused decode: evaluation/dispatch overhead needs a separate null/bound.
    A gate is exclusive to one serial replay, never concurrent forwards.
    """

    def __init__(self, component_id: str, *, evaluate: Callable[[Any], None],
                 barrier: Callable[[], None] = lambda: None):
        if not isinstance(component_id, str) or not component_id:
            raise ValueError("component_id must be nonempty")
        self.component_id = component_id
        self.evaluate = evaluate
        self.barrier = barrier
        self._active = False

    @contextmanager
    def episode(self, arm: str, replacements: Iterable[Any] = ()):
        """Reset the call cursor; refuse short/unused tapes and nested replays."""
        if arm not in ("full", "clamped", "removed"):
            raise ValueError("arm must be full, clamped or removed")
        if self._active:
            raise RuntimeError("component gate already in use")
        tape = tuple(replacements)
        if arm == "full" and tape:
            raise ValueError("full arm does not consume a replacement tape")
        if arm != "full" and not tape:
            raise ValueError("clamped/removed arms require a nonempty tape")
        self._active, self._arm, self._tape, self._cursor = True, arm, tape, 0
        self.outputs = []
        try:
            yield self
            if arm != "full" and self._cursor != len(tape):
                raise ValueError("unused replacement tape entries: replay shape changed")
        finally:
            self._active = False
            self._tape = ()

    def invoke(self, component: Callable, *args, **kwargs):
        if not self._active:
            raise RuntimeError("component call outside an episode")
        replacement = None
        if self._arm != "full":
            if self._cursor >= len(self._tape):
                raise ValueError("replacement tape exhausted")
            replacement = self._tape[self._cursor]
            self._signature(replacement)
        self.barrier()
        actual = None
        if self._arm != "removed":
            actual = component(*args, **kwargs)
            self._signature(actual)
            # Required even when the result is discarded: defeat lazy DCE.
            self.evaluate(actual)
        if self._arm == "clamped" and self._signature(actual) != self._signature(replacement):
            raise ValueError("replacement must match component output shape and dtype")
        output = actual if self._arm == "full" else replacement
        self.evaluate(output)
        self.barrier()
        self._cursor += 1
        self.outputs.append(output)
        return output

    @staticmethod
    def _signature(value):
        if not hasattr(value, "shape") or not hasattr(value, "dtype"):
            raise TypeError("component seam supports a single array output only")
        return tuple(value.shape), str(value.dtype)


def wrap_mlx_component(component, gate: ComponentGate):
    """Lazily construct an mlx.nn.Module that retains the original parameters.

    Install this ONCE before hashing/warmup, in every arm. Use uncompiled
    forwards. Gate construction for MLX: evaluate=mx.eval, barrier=mx.synchronize.
    Natively validate parameters(), cache isolation, logits, and dispatch count
    on a tiny random model before proposing any measurement window.
    """
    import mlx.nn as nn

    class WrappedComponent(nn.Module):
        def __init__(self):
            super().__init__()
            self.inner = component

        def __call__(self, *args, **kwargs):
            return gate.invoke(self.inner, *args, **kwargs)

    return WrappedComponent()
