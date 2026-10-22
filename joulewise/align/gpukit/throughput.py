"""Single-stream BF16 roofline ceilings from dated hardware and model sources.

These deliberately omit attention FLOPs, KV reads and serving overhead. They
are optimistic bounds under the stated weight-read model, never benchmarks.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_EVEN
from typing import Any, Mapping


def ceilings(matrix: Mapping[str, Any], gpu_class: str, model: str) -> tuple[float, float] | None:
    """Return (prefill, decode) tokens/s, or None for an unavailable source."""
    hardware = matrix["gpu_classes"][gpu_class]["hardware"]
    params = matrix["model_parameters"][model]["active_parameters"]
    decode_params = matrix["model_parameters"][model].get("decode_weight_parameters")
    bandwidth = hardware["memory_bandwidth_bytes_s"]["value"]
    flops = hardware["dense_bf16_flops_s"]["value"]
    if any(value is None for value in (params, decode_params, bandwidth, flops)):
        return None
    # BF16 stores 16 bits / 8 bits per byte = 2 bytes per active weight.
    # A matrix multiply uses one multiply and one add = 2 FLOPs per weight.
    return flops / (2 * params), bandwidth / (2 * decode_params)


def display_number(value: float | None, *, lower_bound: bool = False) -> float | None:
    """Two significant digits; round bounds down, planning values to nearest.

    Active counts such as 4.0B and 3.3B have only two significant digits.
    Downward rounding preserves the direction of a displayed time lower bound.
    Full precision remains available in the arithmetic API.
    """
    if value is None or value == 0:
        return value
    decimal = Decimal(str(value))
    quantum = Decimal(1).scaleb(decimal.copy_abs().adjusted() - 1)
    return float(decimal.quantize(quantum, rounding=ROUND_FLOOR if lower_bound else ROUND_HALF_EVEN))
