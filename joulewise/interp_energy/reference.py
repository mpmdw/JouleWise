"""Tiny pure-NumPy causal attention model for desk tests, never hardware evidence."""

from __future__ import annotations

from typing import Any

from ._common import require_numpy
from .weight_edits import weights_sha256


class NumpyKVCache:
    def __init__(self) -> None:
        self.keys = None
        self.values = None
        self.offset = 0

    @property
    def state(self) -> tuple[Any, Any]:
        return self.keys, self.values


class NumpyReferenceModel:
    """One causal attention layer, batch one, with actual growing K/V tensors.

    ``__call__(tokens, cache=...)`` follows the mlx-lm model interface. A full
    uncached forward is an independent reference for every cached step's logits.
    Fixed synthetic parameters only; no tokenizer, download, or weight files.
    """

    def __init__(self, *, seed: int = 0, vocab_size: int = 11, width: int = 8) -> None:
        np = require_numpy()
        if vocab_size <= 0 or width <= 0:
            raise ValueError("vocab_size and width must be positive")
        self.np = np
        self.vocab_size = vocab_size
        self.width = width
        rng = np.random.default_rng(seed)
        self.weights = {
            name: (rng.standard_normal(shape) / width**0.5).astype(np.float32)
            for name, shape in (
                ("embedding", (vocab_size, width)), ("query", (width, width)),
                ("key", (width, width)), ("value", (width, width)),
                ("output", (width, vocab_size)),
            )
        }

    def make_cache(self) -> list[NumpyKVCache]:
        return [NumpyKVCache()]

    def weights_sha256(self) -> str:
        return weights_sha256(self.weights)

    def __call__(self, tokens: Any, *, cache: list[NumpyKVCache] | None = None) -> Any:
        np = self.np
        if tokens.ndim != 2 or tokens.shape[0] != 1 or tokens.shape[1] == 0:
            raise ValueError("reference model requires a nonempty [1, length] input")
        x = self.weights["embedding"][tokens]
        q, keys, values = (x @ self.weights[name] for name in ("query", "key", "value"))
        offset = 0
        if cache is not None:
            entry = cache[0]
            offset = entry.offset
            if entry.keys is not None:
                keys = np.concatenate((entry.keys, keys), axis=1)
                values = np.concatenate((entry.values, values), axis=1)
            entry.keys, entry.values = keys, values
            entry.offset += tokens.shape[1]
        scores = q @ keys.transpose(0, 2, 1) / self.width**0.5
        mask = np.arange(keys.shape[1])[None, :] > (offset + np.arange(tokens.shape[1]))[:, None]
        scores = np.where(mask[None, :, :], -np.inf, scores)
        scores -= scores.max(axis=-1, keepdims=True)
        attention = np.exp(scores)
        attention /= attention.sum(axis=-1, keepdims=True)
        return (x + attention @ values) @ self.weights["output"]
