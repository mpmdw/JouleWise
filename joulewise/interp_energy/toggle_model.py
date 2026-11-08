"""Function-preserving affine encodings and conditional toggle-cost estimates.

Desk tools only: no file access, model loading, acquisition or device selection.
NumPy and MLX are lazy optional imports. Storage Hamming distances are proxies,
not observations of physical bus activity. See the H4 run plan for claim gates.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

from ._common import require_numpy as _numpy
from . import lockin, operand_stats, rail_data_dependence


def _integer(name, value, minimum=1):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def pack_codes(codes, *, bits=4):
    """MLX affine layout: low-order code first in each uint32 word, last axis."""
    np = _numpy()
    if bits not in (4, 8):
        raise ValueError("bits must be 4 or 8")
    codes = np.asarray(codes)
    width = 32 // bits
    if (codes.ndim != 2 or not all(codes.shape) or codes.shape[1] % width or
            codes.dtype.kind not in "iu" or np.any(codes < 0) or
            np.any(codes > (1 << bits) - 1)):
        raise ValueError("codes must be a nonempty integer matrix in range, with complete words")
    words = codes.astype(np.uint32).reshape(codes.shape[0], -1, width)
    shifts = np.arange(width, dtype=np.uint32) * bits
    return np.bitwise_or.reduce(words << shifts, axis=-1)


@dataclass(frozen=True, eq=False)
class AffineWeight:
    """Owned host snapshot of W[N,K] = scale[N,K/G]*code + bias[N,K/G].

    Metadata is float16 or float32; codes are packed uint32. This deliberately
    supports only affine 4/8-bit, not MLX's other quantization modes. Reference
    dequantization uses float64 arithmetic, then ONE rounding to metadata dtype.
    It specifies the host contract, not a promise about fused native kernels.
    """

    packed: Any
    scales: Any
    biases: Any
    group_size: int = 64
    bits: int = 4

    def __post_init__(self):
        np = _numpy()
        if self.bits not in (4, 8):
            raise ValueError("bits must be 4 or 8")
        _integer("group_size", self.group_size)
        packed, scales, biases = (np.array(a, copy=True, order="C") for a in
                                  (self.packed, self.scales, self.biases))
        if packed.dtype != np.dtype(np.uint32) or packed.ndim != 2 or not all(packed.shape):
            raise ValueError("packed must be a nonempty uint32 matrix")
        k = packed.shape[1] * (32 // self.bits)
        if self.group_size % (32 // self.bits) or k % self.group_size:
            raise ValueError("groups must contain complete packed words and divide K")
        if (scales.shape != (packed.shape[0], k // self.group_size) or
                biases.shape != scales.shape or scales.dtype != biases.dtype or
                scales.dtype not in (np.dtype(np.float16), np.dtype(np.float32)) or
                not np.isfinite(scales).all() or not np.isfinite(biases).all()):
            raise ValueError("scales/biases must be matching finite float16/float32 group matrices")
        for name, array in (("packed", packed), ("scales", scales), ("biases", biases)):
            array.flags.writeable = False
            object.__setattr__(self, name, array)
        if not np.isfinite(self.dequantize()).all():
            raise ValueError("dequantized values must be finite")

    @property
    def shape(self):
        return self.packed.shape[0], self.packed.shape[1] * (32 // self.bits)

    def codes(self):
        np = _numpy()
        shifts = np.arange(32 // self.bits, dtype=np.uint32) * self.bits
        return ((self.packed[..., None] >> shifts) & ((1 << self.bits) - 1)).reshape(self.shape)

    def dequantize(self):
        np = _numpy()
        groups = self.codes().astype(np.float64).reshape(*self.scales.shape, self.group_size)
        with np.errstate(over="ignore", invalid="ignore"):
            return (groups * self.scales.astype(np.float64)[..., None] +
                    self.biases.astype(np.float64)[..., None]).astype(self.scales.dtype).reshape(self.shape)

    def to_mlx(self):
        """Materialize resident operands outside chips; reuse rail.MLXBackend.cycle.

        Does not select a device. Native dequantization/output validation remains
        mandatory; call verify_mlx_pair before native use of a re-encoding.
        """
        import mlx.core as mx

        if self.group_size not in (32, 64, 128):
            raise ValueError("native MLX group_size must be 32, 64 or 128")
        operands = tuple(mx.array(a) for a in (self.packed, self.scales, self.biases))
        mx.eval(*operands)
        return operands

    @classmethod
    def from_mlx(cls, packed, scales, biases, *, group_size=64, bits=4):
        """Snapshot already supplied MLX operands; never quantize or load weights."""
        import mlx.core as mx

        np = _numpy()
        mx.eval(packed, scales, biases)
        return cls(np.array(packed), np.array(scales), np.array(biases), group_size, bits)


@dataclass(frozen=True, eq=False)
class Reencoding:
    weight: AffineWeight
    # New column j contains old column input_order[j]. X gathers the same order;
    # canonical W is recovered by the inverse order. No gather belongs in chips.
    input_order: tuple[int, ...]
    kind: str

    def canonical_dequantized(self):
        return self.weight.dequantize()[:, _numpy().argsort(self.input_order)]

    def inputs(self, values):
        np = _numpy()
        values = np.asarray(values)
        if values.ndim < 1 or values.shape[-1] != self.weight.shape[1]:
            raise ValueError("input last dimension must equal K")
        return values[..., list(self.input_order)].copy()


def _checked(base, candidate, order, kind):
    result = Reencoding(candidate, tuple(int(i) for i in order), kind)
    expected, actual = base.dequantize(), result.canonical_dequantized()
    if expected.dtype != actual.dtype or expected.tobytes() != actual.tobytes():
        raise ValueError("re-encoding changes reference dequantized bytes (rounding or signed zero)")
    return result


def affine_reencode(weight, *, multiplier=1, offset=0):
    """q' = m*q+c, s' = s/m, bias' = bias-c*s', per group or scalar.

    Integer m must be nonzero and codes must stay in range WITHOUT clipping.
    This includes code offsets, scale/bias changes and sign complementation.
    Arbitrary floating metadata need not preserve values: refuse if rounding
    changes even one dequantized byte. Inputs and original buffers stay intact.
    """
    np = _numpy()
    parameters = []
    limit = (1 << weight.bits) - 1
    for name, value in (("multiplier", multiplier), ("offset", offset)):
        array = np.asarray(value)
        if array.dtype.kind not in "iu" or np.any(array < -limit) or np.any(array > limit):
            raise ValueError(f"{name} must contain small integers in [-{limit}, {limit}]")
        try:
            parameters.append(np.broadcast_to(array, weight.scales.shape).astype(np.int64))
        except ValueError as exc:
            raise ValueError(f"{name} must broadcast to group metadata shape") from exc
    m, c = parameters
    if np.any(m == 0):
        raise ValueError("multiplier must be nonzero")
    codes = weight.codes().astype(np.int64).reshape(*weight.scales.shape, weight.group_size)
    codes = m[..., None] * codes + c[..., None]
    if np.any(codes < 0) or np.any(codes > limit):
        raise ValueError("re-encoded codes out of range; clipping would change the function")
    scales = weight.scales.astype(np.float64) / m
    biases = weight.biases.astype(np.float64) - c * scales
    with np.errstate(over="ignore", invalid="ignore"):
        candidate = AffineWeight(pack_codes(codes.reshape(weight.shape), bits=weight.bits),
                                 scales.astype(weight.scales.dtype), biases.astype(weight.biases.dtype),
                                 weight.group_size, weight.bits)
    return _checked(weight, candidate, range(weight.shape[1]), "affine")


def complement(weight, *, groups=None):
    """q' = Q-q, s' = -s, bias' = bias+Q*s (Q=15 or 255).

    Whole-array complement flips code Hamming weight and preserves code XOR
    distances. A boolean group mask gives mixed polarities, moving distances
    at mask boundaries. Metadata toggles must be measured separately.
    """
    np = _numpy()
    if groups is None:
        return affine_reencode(weight, multiplier=-1, offset=(1 << weight.bits) - 1)
    groups = np.asarray(groups)
    if groups.dtype.kind != "b" or groups.shape != weight.scales.shape:
        raise ValueError("groups must be a boolean mask with the metadata shape")
    return affine_reencode(weight, multiplier=np.where(groups, -1, 1),
                           offset=np.where(groups, (1 << weight.bits) - 1, 0))


def permute_groups(weight, order):
    """Reorder whole input groups and return the compensating input gather.

    Histogram/Hamming weight are invariant; traversal distances can change.
    This preserves the real linear map. Reordered floating reductions need not
    yield bit-identical native outputs; tiny exact-dyadic fixtures do.
    """
    np = _numpy()
    order = np.asarray(order)
    count = weight.scales.shape[1]
    if (order.shape != (count,) or order.dtype.kind not in "iu" or
            sorted(order.tolist()) != list(range(count))):
        raise ValueError("order must be a permutation of all input groups")
    columns = (order[:, None] * weight.group_size + np.arange(weight.group_size)).ravel()
    candidate = AffineWeight(pack_codes(weight.codes()[:, columns], bits=weight.bits),
                             weight.scales[:, order], weight.biases[:, order],
                             weight.group_size, weight.bits)
    return _checked(weight, candidate, columns, "group_permutation")


def verify_mlx_pair(base, reencoding):
    """Refuse unequal native dequantized bytes; returns prepared resident tuples.

    This checks the actual MLX dequantizer, NOT quantized_matmul's accumulation
    order or a model's logits. Verify those separately on every candidate.
    """
    import mlx.core as mx

    np = _numpy()
    candidate = reencoding.weight
    if (candidate.shape != base.shape or candidate.bits != base.bits or
            candidate.group_size != base.group_size or candidate.scales.dtype != base.scales.dtype or
            sorted(reencoding.input_order) != list(range(base.shape[1]))):
        raise ValueError("native pair must have matching affine formats and a complete input permutation")
    left, right = base.to_mlx(), reencoding.weight.to_mlx()
    a = mx.dequantize(*left, group_size=base.group_size, bits=base.bits)
    b = mx.dequantize(*right, group_size=base.group_size, bits=base.bits)
    mx.eval(a, b)
    host_a = np.array(a)
    host_b = np.array(b)[:, np.argsort(reencoding.input_order)]
    if host_a.dtype != host_b.dtype or host_a.tobytes() != host_b.tobytes():
        raise ValueError("native MLX dequantized bytes differ")
    return left, right


def storage_statistics(weight, *, strides_bytes=(2, 4, 8, 16, 32, 64, 128)):
    """Exact counts for packed codes, scales and biases, never pooled implicitly.

    At byte stride d: sum popcount(byte[i] XOR byte[i+d]) for every i < L-d
    in C-order. Row boundaries are included; buffer/dispatch boundaries are
    excluded. No wrap, padding or assumed initial bus state. Counts per repeat
    are descriptor exposures, not physical transition counts. Metadata and
    input/output streams can confound any single-coefficient model.
    """
    np = _numpy()
    strides = tuple(strides_bytes)
    if not strides or len(set(strides)) != len(strides):
        raise ValueError("strides must be nonempty and unique")
    for stride in strides:
        _integer("stride_bytes", stride)
    result = {}
    for name, array in (("packed", weight.packed), ("scales", weight.scales), ("biases", weight.biases)):
        raw = np.ascontiguousarray(array).reshape(-1).view(np.uint8)
        by_stride = {}
        for stride in strides:
            count = max(0, raw.size - stride)
            xor = raw[:-stride] ^ raw[stride:] if count else raw[:0]
            toggles = int(operand_stats.hamming_weight(xor).sum(dtype=np.uint64))
            by_stride[stride] = {"toggle_bits": toggles, "compared_bits": count * 8,
                                 "rate": toggles / (count * 8) if count else None}
        result[name] = {"operand": operand_stats.operand_statistics(array), "strides": by_stride}
    return result


def make_schedule(n_blocks, *, chip_seconds=10.0, seed=714):
    """Reuse the rail ladder's randomized ABBA/BAAB schedule and lock-in model."""
    _integer("n_blocks", n_blocks)
    slots = rail_data_dependence.abba_schedule(("normal", "reencoded"), rounds=n_blocks, seed=seed)
    return lockin.Schedule(tuple(-1 if s["arm"] == "A" else 1 for s in slots),
                           chip_seconds, "toggle_randomized_abba")


@dataclass(frozen=True)
class TransitionCost:
    joules_per_transition: float
    standard_error: float
    ci_low: float
    ci_high: float
    delta_transitions_per_second: float
    boundary: str
    power_contrast: lockin.Estimate
    interpretation: str = "PROVISIONAL conditional storage-proxy slope; not physical bus calibration"


def estimate_transition_cost(trace, *, transitions_a_per_dispatch, transitions_b_per_dispatch,
                             dispatches_per_second, boundary, method="abba", **ci_options):
    """Estimate (P_B-P_A) / ((T_B-T_A)*dispatch_rate), in J/proxy transition.

    Supply interval-average gross powers and matching sampling windows in a
    lockin.SyntheticTrace container (the container also accepts measured arrays).
    The common fixed dispatch rate and descriptor exposures are caller-asserted
    constants. Unequal work, clock, duration, metadata or input distributions
    defeat a causal toggle reading. No meter/data loading is done here.

    HAC and moving-block bootstrap reuse chronological four-chip lock-in
    scores, never iid samples. CIs condition on counts/rate and omit instrument,
    timing and model systematic bounds. Signed slopes/CIs are retained; an
    unidentifiable zero contrast (e.g. whole complement) is rejected.
    """
    np = _numpy()
    for name, value in (("transitions_a_per_dispatch", transitions_a_per_dispatch),
                        ("transitions_b_per_dispatch", transitions_b_per_dispatch),
                        ("dispatches_per_second", dispatches_per_second)):
        if isinstance(value, bool) or not math.isfinite(value) or value < 0:
            raise ValueError(f"{name} must be finite and nonnegative")
    delta = (transitions_b_per_dispatch - transitions_a_per_dispatch) * dispatches_per_second
    if not math.isfinite(delta) or delta == 0:
        raise ValueError("nonzero finite transition-rate contrast is required")
    if boundary not in ("dc", "gpu", "rails", "rest"):
        raise ValueError("boundary must be dc, gpu, rails or rest")
    expected = trace.schedule.window_reference(trace.starts_seconds, trace.ends_seconds)
    reference = np.asarray(trace.reference)
    if expected.shape != reference.shape or not np.allclose(expected, reference, rtol=0, atol=1e-12):
        raise ValueError("trace reference must match the commanded schedule windows")
    if method == "abba":
        power = lockin.estimate_abba(trace, **ci_options)
    elif method == "demodulate":
        power = lockin.demodulate(trace, **ci_options)
    else:
        raise ValueError("method must be abba or demodulate")
    low, high = sorted((power.ci_low_w / delta, power.ci_high_w / delta))
    return TransitionCost(power.contrast_w / delta, power.standard_error_w / abs(delta),
                          low, high, delta, boundary, power)
