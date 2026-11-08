"""Logical zeros and storage-bit statistics, using optional NumPy.

Bits mean the supplied array's *stored representation*, including sign and
exponent bits for floats, and two's-complement bits for signed integers.
These are host-buffer descriptors, not a model of GPU traversal or bus toggles.
"""

from __future__ import annotations

from functools import lru_cache


def _numpy():
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("operand statistics require optional NumPy") from exc
    return np


def _array(values):
    np = _numpy()
    array = np.asarray(values)
    if array.dtype.kind not in "biuf":
        raise TypeError("expected a real numeric or boolean array")
    return array


@lru_cache(maxsize=1)
def _popcounts():
    np = _numpy()
    return np.array([i.bit_count() for i in range(256)], dtype=np.uint8)


def _bytes(array):
    np = _numpy()
    return np.ascontiguousarray(array).reshape(-1).view(np.uint8)


def hamming_weight(values):
    """Return per-element set-bit counts with the input shape (NumPy uint64)."""
    array = _array(values)
    counts = _popcounts()[_bytes(array)].reshape(-1, array.dtype.itemsize)
    return counts.sum(axis=1, dtype="uint64").reshape(array.shape)


def zero_fraction(values) -> float | None:
    """Fraction of numerical zeros, including -0.0; None for empty input."""
    array = _array(values)
    return float((array == 0).sum()) / array.size if array.size else None


def _toggle_counts(array, tile_elements: int) -> tuple[int, int, int]:
    if isinstance(tile_elements, bool) or not isinstance(tile_elements, int) or tile_elements < 1:
        raise ValueError("tile_elements must be a positive integer")
    complete, tail = divmod(array.size, tile_elements)
    if complete < 2:
        return 0, 0, tail
    tile_bytes = tile_elements * array.dtype.itemsize
    tiles = _bytes(array)[:complete * tile_bytes].reshape(complete, tile_bytes)
    toggles = int(_popcounts()[tiles[1:] ^ tiles[:-1]].sum(dtype="uint64"))
    return toggles, (complete - 1) * tile_bytes * 8, tail


def bit_toggle_rate(values, *, tile_elements: int = 256) -> float | None:
    """XOR density of aligned positions in consecutive C-order full tiles.

    Ignore the final incomplete tile. None means fewer than two full tiles;
    zero means a valid comparison with no bit changes. This is a placement
    proxy: MLX's actual kernel tile order is deliberately not inferred.
    """
    toggles, compared, _ = _toggle_counts(_array(values), tile_elements)
    return toggles / compared if compared else None


def bfloat16_bits(values):
    """Encode float32 as bf16 words, round to nearest, ties to even (NumPy)."""
    np = _numpy()
    values = np.asarray(values, dtype=np.float32)
    words = values.view(np.uint32)
    rounded = (words + np.uint32(0x7FFF) + ((words >> 16) & 1)) >> 16
    # Rounding a NaN must not accidentally turn it into infinity or zero.
    rounded = np.where(np.isnan(values), (words >> 16) | 0x40, rounded)
    return rounded.astype(np.uint16)


def bfloat16_values(words):
    """Decode uint16 bf16 words as float32 without requiring MLX."""
    np = _numpy()
    return (np.asarray(words, dtype=np.uint16).astype(np.uint32) << 16).view(np.float32)


def operand_statistics(values, *, storage=None, tile_elements: int = 256) -> dict:
    """Describe numerical values and, optionally, a different storage encoding.

    For bf16 pass decoded float32 values and uint16 ``storage``; for affine
    quantization pass dequantized values and packed uint32 codes. Scales and
    biases should be described separately, never counted as packed codes.
    """
    logical = _array(values)
    encoded = logical if storage is None else _array(storage)
    toggles, compared, tail = _toggle_counts(encoded, tile_elements)
    ones = int(hamming_weight(encoded).sum(dtype="uint64"))
    bits = encoded.size * encoded.dtype.itemsize * 8
    return {
        "elements": int(logical.size),
        "zero_count": int((logical == 0).sum()),
        "zero_fraction": zero_fraction(logical),
        "storage_dtype": encoded.dtype.str,
        "storage_elements": int(encoded.size),
        "storage_bits": int(bits),
        "one_bits": ones,
        "mean_hamming_weight": ones / encoded.size if encoded.size else None,
        "one_bit_fraction": ones / bits if bits else None,
        "toggle_bits": toggles,
        "compared_bits": compared,
        "bit_toggle_rate": toggles / compared if compared else None,
        "tile_elements": tile_elements,
        "ignored_tail_elements": tail,
    }


def combine_statistics(parts: list[dict]) -> dict:
    """Pool exact counts across matrices; do not invent cross-matrix toggles."""
    if not parts:
        raise ValueError("at least one statistics record is required")
    first = parts[0]
    if any((p["storage_dtype"], p["tile_elements"]) !=
           (first["storage_dtype"], first["tile_elements"]) for p in parts):
        raise ValueError("storage dtype and tile size must agree")
    keys = ("elements", "zero_count", "storage_elements", "storage_bits", "one_bits",
            "toggle_bits", "compared_bits", "ignored_tail_elements")
    result = {key: sum(p[key] for p in parts) for key in keys}
    result.update(storage_dtype=first["storage_dtype"], tile_elements=first["tile_elements"],
                  matrices=len(parts), toggle_boundary="within each matrix only")
    for name, numerator, denominator in (
        ("zero_fraction", "zero_count", "elements"),
        ("mean_hamming_weight", "one_bits", "storage_elements"),
        ("one_bit_fraction", "one_bits", "storage_bits"),
        ("bit_toggle_rate", "toggle_bits", "compared_bits"),
    ):
        result[name] = result[numerator] / result[denominator] if result[denominator] else None
    return result
