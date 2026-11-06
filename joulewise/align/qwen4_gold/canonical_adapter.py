"""Quantization-drift extension points for the canonical Qwen4 gold adapter.

Quantization drift is descriptive evidence, never a parity verdict.  Keeping
its identity in a separate fingerprint is important: adding this optional
measurement must not invalidate or silently resume an ordinary parity run.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence


QUANT_DRIFT = "QUANT_DRIFT"


@dataclass(frozen=True)
class GoldRequest:
    trace_id: str
    payload: Mapping[str, Any]
    quantize_experts: int | None = None

    def __post_init__(self) -> None:
        if self.quantize_experts not in (None, 5, 6):
            raise ValueError("quantize_experts must be null, 5, or 6")

    def parity_fingerprint(self) -> str:
        # Intentionally excludes the measurement-only field.
        body = {"trace_id": self.trace_id, "payload": self.payload}
        return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def quant_drift_fingerprint(self) -> str | None:
        if self.quantize_experts is None:
            return None
        body = {"parity_fingerprint": self.parity_fingerprint(), "quantize_experts": self.quantize_experts,
                "group_size": 64, "mode": "affine"}
        return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def with_quant_drift(request: GoldRequest, bits: int | None) -> GoldRequest:
    return replace(request, quantize_experts=bits)


def drift_metrics(reference: Sequence[float], measured: Sequence[float], *,
                  reference_experts: Sequence[int] = (), measured_experts: Sequence[int] = ()) -> dict[str, Any]:
    if len(reference) != len(measured) or not reference:
        raise ValueError("drift vectors must have equal non-zero size")
    delta = [float(b) - float(a) for a, b in zip(reference, measured)]
    rn = math.sqrt(sum(float(x) ** 2 for x in reference))
    mn = math.sqrt(sum(float(x) ** 2 for x in measured))
    dot = sum(float(a) * float(b) for a, b in zip(reference, measured))
    union = set(reference_experts) | set(measured_experts)
    return {"max_abs": max(map(abs, delta)),
            "relative_l2": math.sqrt(sum(x * x for x in delta)) / max(rn, 1e-30),
            "cosine": dot / max(rn * mn, 1e-30),
            "expert_set_agreement_rate": (len(set(reference_experts) & set(measured_experts)) / len(union)
                                           if union else 1.0)}


def quantized_gather_qmm(x: Any, weight: Any, indices: Any, *, path: str, bits: int) -> Any:
    """Apply the converter's exact expert recipe, then MLX ``gather_qmm``.

    Imports stay lazy so documentation, comparison, and unit tests work on
    non-Apple hosts.  The caller supplies one routed expert matrix as read by
    the streaming adapter and the already-selected expert indices.
    """
    if bits not in (5, 6):
        raise ValueError("expert drift supports only 5 or 6 bits")
    import mlx.core as mx
    from joulewise.align.models import qwen4_exp as rules
    profile = "maxfit" if bits == 6 else "maxfit5"
    quant = rules.quantization_for(path, weight.shape, profile, group_size=64)
    if quant is None or quant["bits"] != bits:
        raise ValueError(f"matrix is not a routed expert under {profile}: {path}")
    packed, scales, biases = mx.quantize(weight, group_size=64, bits=bits)
    return mx.gather_qmm(x, packed, scales, biases, indices=indices, transpose=True,
                         group_size=64, bits=bits, mode="affine")


def quant_drift_record(request: GoldRequest, metrics_by_trace: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    if request.quantize_experts is None:
        raise ValueError("QUANT_DRIFT requires quantize_experts")
    return {"kind": QUANT_DRIFT, "verdict": None, "bits": request.quantize_experts,
            "fingerprint": request.quant_drift_fingerprint(), "traces": dict(metrics_by_trace)}
