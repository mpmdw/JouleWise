"""Reversible edits of dense floating point parameters; no model or data I/O.

An edit is applied with ``edit.apply(parameters)`` and undone with
``edit.revert()``. Parameters are a flat mutable mapping of names to NumPy or
MLX arrays. Reversion restores saved values, never an arithmetic inverse, and
checks SHA-256 of every touched parameter's raw bytes. Exclusive ownership is
required while an edit or swap is active; overlapping edits are not supported.

Sparse indices are unique C-order flat offsets, or a tuple of coordinate
vectors (as in NumPy advanced indexing). Ablation accepts a boolean mask of
exactly the parameter shape (True means zero), or explicit axis selections.
Head selections use contiguous groups along an explicitly specified axis;
there is no assumption about a model's Q/K/V packing or matrix orientation.
Dense zeros retain the original shape/dtype and do not imply sparse kernels.

WeightSwap prepares and hashes both states once. NumPy switches scatter only
changed elements into the original arrays: O(changed bytes), plus parameter
bookkeeping. MLX does not promise partial physical buffer writes: it switches
pre-evaluated resident tensor references in the SAME mapping/model, with no
per-switch tensor construction or reload. MLX array identity changes. Pass a
``bind(changed_parameters)`` callback to update an actual model's leaves (e.g.
``model.update(tree_unflatten(list(changed.items())))``). A detached parameters
mapping alone cannot update a model. Compiled functions that capture weights
are unsupported; use an uncompiled forward and validate natively.

Every successful switch request (including a same-state no-op) records start
and completion monotonic nanoseconds. MLX is evaluated and synchronized before
and after binding. These are host boundaries, not an atomic device clock stamp
or proof of an energy effect. Callers own the schedule, fixed-token replay,
cache isolation, inference exclusion during swaps, and durable event storage.
Forward results must be evaluated/submitted before switching: synchronization
cannot discover an inference expression that is still only a lazy Python value.
Hashing/verification scans full parameters and belongs outside measured chips.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib
import math
import operator
import time
from typing import Any, Callable, Mapping, MutableMapping, Sequence

Parameters = MutableMapping[str, Any]


class WeightConflictError(RuntimeError):
    """Parameters no longer match the state owned by an edit/swap."""


class _Backend:
    def __init__(self, array: Any):
        self.kind = type(array).__module__.split(".")[0]
        if self.kind == "numpy":
            self.xp = importlib.import_module("numpy")
            if not isinstance(array, self.xp.ndarray):
                raise TypeError("expected an ndarray")
            if array.dtype.kind != "f":
                raise TypeError("only dense floating point parameters are supported")
            if not array.flags.c_contiguous:
                raise ValueError("NumPy parameters must be C-contiguous")
        elif self.kind == "mlx":
            self.xp = importlib.import_module("mlx.core")
            if array.dtype not in (self.xp.float16, self.xp.bfloat16, self.xp.float32):
                raise TypeError("MLX parameters must be float16, bfloat16 or float32")
        else:
            raise TypeError("expected a NumPy or MLX array")

    def copy(self, a: Any) -> Any:
        return a.copy() if self.kind == "numpy" else self.xp.array(a)

    def sync(self, arrays: Sequence[Any]) -> None:
        if self.kind == "mlx":
            if arrays:
                self.xp.eval(*arrays)
            self.xp.synchronize()

    def take(self, a: Any, indices: tuple[int, ...]) -> Any:
        dtype = self.xp.int64 if self.kind == "numpy" else self.xp.int32
        return self.copy(a.reshape(-1)[self.xp.array(indices, dtype=dtype)])

    def put(self, a: Any, indices: tuple[int, ...], values: Any) -> Any:
        dtype = self.xp.int64 if self.kind == "numpy" else self.xp.int32
        flat = a.reshape(-1)
        flat[self.xp.array(indices, dtype=dtype)] = values
        return a if self.kind == "numpy" else flat.reshape(a.shape)

    def values(self, values: Any, count: int, dtype: Any) -> Any:
        result = self.xp.array(values, dtype=dtype)
        if tuple(result.shape) != (count,):
            raise ValueError("values must have exactly one entry per selected element")
        if not bool(self.xp.all(self.xp.isfinite(result)).item()):
            raise ValueError("edit values must be finite")
        return result

    def arithmetic_dtype(self, a: Any) -> Any:
        # Avoid rounding a small delta to fp16/bf16 before adding it to W.
        return self.xp.float32 if int(a.itemsize) < 4 else a.dtype


def _raw_chunks(a: Any, backend: _Backend):
    if not int(a.size):
        return
    if backend.kind == "numpy":
        yield memoryview(a).cast("B")
    else:
        backend.sync([a])
        raw = a.reshape(-1).view(backend.xp.uint8).reshape(-1)
        # Bounded host staging, including bf16 without a lossy float conversion.
        for start in range(0, int(raw.size), 65536):
            yield bytes(raw[start:start + 65536].tolist())


def parameter_sha256(array: Any) -> str:
    """SHA-256 of C-order raw parameter bytes (no dtype/shape framing)."""
    backend = _Backend(array)
    digest = hashlib.sha256()
    for chunk in _raw_chunks(array, backend):
        digest.update(chunk)
    return digest.hexdigest()


def parameter_hashes(parameters: Mapping[str, Any]) -> dict[str, str]:
    """Per-parameter raw-byte hashes; this intentionally scans all weights."""
    return {name: parameter_sha256(a) for name, a in parameters.items()}


def _integer(value: Any) -> int:
    if isinstance(value, bool):
        raise TypeError("boolean is not an integer index")
    return operator.index(value)


def _indices(indices: Any, shape: tuple[int, ...]) -> tuple[int, ...]:
    size = math.prod(shape)
    if isinstance(indices, tuple) and indices and all(hasattr(i, "__iter__") for i in indices):
        if len(indices) != len(shape):
            raise ValueError("coordinate vectors must match parameter rank")
        vectors = [tuple(_integer(v) for v in axis) for axis in indices]
        if len({len(v) for v in vectors}) != 1:
            raise ValueError("coordinate vectors must have equal length")
        offsets = []
        for coordinate in zip(*vectors):
            offset = 0
            for value, dimension in zip(coordinate, shape):
                if not 0 <= value < dimension:
                    raise IndexError("coordinate outside parameter")
                offset = offset * dimension + value
            offsets.append(offset)
    else:
        offsets = [_integer(i) for i in indices]
    if any(i < 0 or i >= size for i in offsets):
        raise IndexError("flat index outside parameter")
    if len(set(offsets)) != len(offsets):
        raise ValueError("duplicate indices are ambiguous; combine deltas first")
    return tuple(offsets)


def _validate_parameters(parameters: Mapping[str, Any]) -> None:
    arrays = []
    for name, a in parameters.items():
        if not isinstance(name, str) or not name:
            raise ValueError("parameter names must be nonempty strings")
        b = _Backend(a)
        if b.kind == "numpy" and not a.flags.writeable:
            raise ValueError("active NumPy parameters must be writable")
        for other, ob in arrays:
            if a is other or (b.kind == ob.kind == "numpy" and b.xp.shares_memory(a, other)):
                raise ValueError("aliased parameters are unsupported")
        arrays.append((a, b))


def _different_indices(a: Any, b: Any, backend: _Backend) -> tuple[int, ...]:
    # Numeric equality misses signed zero and distinct NaN payloads.
    width = int(a.itemsize)
    xp = backend.xp
    aa = a.reshape(-1).view(xp.uint8).reshape(-1, width)
    bb = b.reshape(-1).view(xp.uint8).reshape(-1, width)
    if backend.kind == "numpy":
        return tuple(int(i) for i in xp.flatnonzero(xp.any(aa != bb, axis=1)))
    result = []
    for start in range(0, int(a.size), 65536):
        mask = xp.any(aa[start:start + 65536] != bb[start:start + 65536], axis=1)
        result.extend(start + i for i, changed in enumerate(mask.tolist()) if changed)
    return tuple(result)


@dataclass
class _Patch:
    name: str
    backend: _Backend
    indices: tuple[int, ...]
    before: Any
    after: Any
    base_tensor: Any
    edited_tensor: Any
    base_hash: str
    edited_hash: str
    active_tensor: Any
    shape: tuple[int, ...]
    dtype: Any

    @classmethod
    def prepare(cls, name: str, a: Any, indices: tuple[int, ...], values: Any):
        backend = _Backend(a)
        before = backend.take(a, indices)
        after = backend.copy(values.astype(a.dtype))
        base = backend.copy(a) if backend.kind == "mlx" else a
        edited = backend.put(backend.copy(a), indices, after)
        backend.sync([base, edited, before, after])
        return cls(name, backend, indices, before, after, base,
                   edited if backend.kind == "mlx" else None,
                   parameter_sha256(a), parameter_sha256(edited), a, tuple(a.shape), a.dtype)

    @property
    def changed_bytes(self) -> int:
        return len(self.indices) * int(self.before.itemsize)

    def check_binding(self, parameters: Parameters) -> None:
        a = parameters[self.name]
        if (a is not self.active_tensor or tuple(a.shape) != self.shape or a.dtype != self.dtype
                or (self.backend.kind == "numpy" and
                    (not a.flags.c_contiguous or not a.flags.writeable))):
            raise WeightConflictError(f"parameter {self.name!r} binding or layout changed externally")

    def install(self, parameters: Parameters, edited: bool) -> None:
        self.check_binding(parameters)
        if self.backend.kind == "numpy":
            self.backend.put(self.active_tensor, self.indices, self.after if edited else self.before)
        else:
            parameters[self.name] = self.edited_tensor if edited else self.base_tensor
            self.active_tensor = parameters[self.name]


def _sync(patches: Sequence[_Patch]) -> None:
    mlx = [p for p in patches if p.backend.kind == "mlx"]
    if mlx:
        mlx[0].backend.sync([p.active_tensor for p in mlx])


def _install(parameters: Parameters, patches: Sequence[_Patch], edited: bool,
             bind: Callable[[Mapping[str, Any]], None] | None) -> None:
    for p in patches:
        p.check_binding(parameters)
    _sync(patches)  # Drain submitted work under the old state before rebinding.
    installed = []
    try:
        for p in patches:
            p.install(parameters, edited)
            installed.append(p)
        if bind and patches:
            bind({p.name: parameters[p.name] for p in patches})
        _sync(patches)
    except Exception:
        for p in reversed(installed):
            p.install(parameters, not edited)
        if bind and installed:
            bind({p.name: parameters[p.name] for p in installed})
        _sync(patches)
        raise


class ReversibleEdit:
    """Base lifecycle: prepare everything before writing; reject external edits.

    ``before_hashes`` and ``after_hashes`` cover touched parameters. Repeated
    apply/revert in the same state raises rather than silently stacking edits.
    A bind callback has the same model-update role as WeightSwap's callback.
    """

    def __init__(self) -> None:
        self._parameters: Parameters | None = None
        self._patches: list[_Patch] = []
        self._bind = None
        self.before_hashes: dict[str, str] = {}
        self.after_hashes: dict[str, str] = {}

    def _plans(self, parameters: Parameters):
        raise NotImplementedError

    def apply(self, parameters: Parameters, *, bind=None) -> ReversibleEdit:
        if self._parameters is not None:
            raise RuntimeError("edit is already applied")
        _validate_parameters(parameters)
        patches = []
        for name, indices, values in self._plans(parameters):
            if any(p.name == name for p in patches):
                raise ValueError("an edit must plan each parameter only once")
            patches.append(_Patch.prepare(name, parameters[name], indices, values))
        _install(parameters, patches, True, bind)
        self._patches, self._parameters, self._bind = patches, parameters, bind
        self.before_hashes = {p.name: p.base_hash for p in patches}
        self.after_hashes = {p.name: p.edited_hash for p in patches}
        if any(parameter_sha256(parameters[p.name]) != p.edited_hash for p in patches):
            raise WeightConflictError("applied bytes differ from the prepared edit")
        return self

    def revert(self) -> None:
        if self._parameters is None:
            raise RuntimeError("edit is not applied")
        for p in self._patches:
            p.check_binding(self._parameters)
            if parameter_sha256(self._parameters[p.name]) != p.edited_hash:
                raise WeightConflictError(f"parameter {p.name!r} changed outside this edit")
        _install(self._parameters, self._patches, False, self._bind)
        if any(parameter_sha256(self._parameters[p.name]) != p.base_hash for p in self._patches):
            raise WeightConflictError("restored bytes differ from the original weights")
        self._parameters, self._patches, self._bind = None, [], None


class SparseDelta(ReversibleEdit):
    """Add ``{parameter: (indices, deltas)}`` and cast back to parameter dtype.

    Arithmetic uses at least float32, retaining float64 for float64 parameters.
    """

    def __init__(self, patch: Mapping[str, tuple[Any, Any]]):
        super().__init__()
        self.patch = patch

    def _plans(self, parameters):
        for name, (indices, values) in self.patch.items():
            a = parameters[name]
            b = _Backend(a)
            selected = _indices(indices, tuple(a.shape))
            dtype = b.arithmetic_dtype(a)
            deltas = b.values(values, len(selected), dtype)
            yield name, selected, b.take(a, selected).astype(dtype) + deltas


class RankOneUpdate(ReversibleEdit):
    """Add ``alpha * u[:, None] * v[None, :]`` to one explicitly oriented matrix.

    Arithmetic uses at least float32 before casting back to parameter dtype.
    This is the update primitive, not the ROME/MEMIT fitting algorithm.
    """

    def __init__(self, parameter: str, u: Any, v: Any, *, alpha: float = 1.0):
        super().__init__()
        self.parameter, self.u, self.v, self.alpha = parameter, u, v, _finite(alpha)

    def _plans(self, parameters):
        a = parameters[self.parameter]
        if len(a.shape) != 2:
            raise ValueError("rank-one update requires a matrix")
        b = _Backend(a)
        dtype = b.arithmetic_dtype(a)
        u, v = b.values(self.u, a.shape[0], dtype), b.values(self.v, a.shape[1], dtype)
        result = a.astype(dtype) + self.alpha * u[:, None] * v[None, :]
        yield self.parameter, tuple(range(int(a.size))), result.reshape(-1)


def _finite(value: Any) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("edit scalar must be finite")
    return value


class AblationMask(ReversibleEdit):
    """Zero a shape-matched bool mask OR the union of explicit axis selections.

    ``rows`` selects axis 0 and ``columns`` axis 1 of a matrix. ``neurons``
    selects ``axis``. ``heads`` selects contiguous ``head_size`` groups along
    ``axis``, which must divide that dimension exactly. All offsets are strict,
    nonnegative, and unique. Omitted selections select nothing.
    """

    def __init__(self, parameter: str, mask: Any = None, *, rows=None, columns=None,
                 neurons=None, heads=None, axis: int = 0, head_size: int | None = None):
        super().__init__()
        self.parameter, self.mask = parameter, mask
        self.rows, self.columns, self.neurons, self.heads = rows, columns, neurons, heads
        self.axis, self.head_size = axis, head_size

    def _plans(self, parameters):
        a = parameters[self.parameter]
        b = _Backend(a)
        xp, shape = b.xp, tuple(a.shape)
        if self.mask is not None:
            if any(s is not None for s in (self.rows, self.columns, self.neurons, self.heads)):
                raise ValueError("provide either a mask or axis selections")
            mask = xp.array(self.mask)
            if tuple(mask.shape) != shape or mask.dtype != xp.bool_:
                raise ValueError("ablation mask must be boolean and match parameter shape")
        else:
            mask = xp.zeros(shape, dtype=xp.bool_)
            selections = []
            for axis, values in ((0, self.rows), (1, self.columns)):
                if values is not None:
                    if len(shape) != 2:
                        raise ValueError("rows/columns require a matrix")
                    selections.append((axis, _indices(values, (shape[axis],))))
            if self.neurons is not None or self.heads is not None:
                axis = _integer(self.axis)
                if not 0 <= axis < len(shape):
                    raise ValueError("axis outside parameter rank")
                if self.neurons is not None:
                    selections.append((axis, _indices(self.neurons, (shape[axis],))))
                if self.heads is not None:
                    width = _integer(self.head_size)
                    if width <= 0 or shape[axis] % width:
                        raise ValueError("head_size must be positive and divide the axis")
                    heads = _indices(self.heads, (shape[axis] // width,))
                    selections.append((axis, tuple(h * width + i for h in heads for i in range(width))))
            for axis, values in selections:
                for value in values:
                    slices = [slice(None)] * len(shape)
                    slices[axis] = value
                    mask[tuple(slices)] = True
        # Set bytes to +0, including existing -0 values.
        zeroed = xp.where(mask, xp.zeros_like(a), a)
        indices = _different_indices(a, zeroed, b)
        yield self.parameter, indices, b.take(zeroed, indices)


class MagnitudePruning(ReversibleEdit):
    """Zero floor(fraction * size) smallest magnitudes per named parameter.

    Ties use C-order offset, including existing zeros. This specifies selected
    elements, not a promise of exactly that final zero fraction. Nonfinite
    weights are rejected because their magnitude ordering is ambiguous.
    """

    def __init__(self, parameter: str, fraction: float):
        super().__init__()
        self.parameter, self.fraction = parameter, _finite(fraction)
        if not 0 <= self.fraction <= 1:
            raise ValueError("fraction must be in [0, 1]")

    def _plans(self, parameters):
        a = parameters[self.parameter]
        b = _Backend(a)
        if not bool(b.xp.all(b.xp.isfinite(a)).item()):
            raise ValueError("magnitude pruning requires finite weights")
        count = math.floor(self.fraction * int(a.size))
        if b.kind == "numpy":
            indices = tuple(int(i) for i in b.xp.argsort(b.xp.abs(a.reshape(-1)), kind="stable")[:count])
        else:
            # Python's stable sort gives the same tie rule on every backend.
            magnitudes = b.xp.abs(a.reshape(-1)).tolist()
            indices = tuple(sorted(range(int(a.size)), key=magnitudes.__getitem__)[:count])
        yield self.parameter, indices, b.xp.zeros((count,), dtype=a.dtype)


class Scale(ReversibleEdit):
    """Multiply all/selected elements by factor, using at least float32."""

    def __init__(self, parameter: str, factor: float, indices: Any = None):
        super().__init__()
        self.parameter, self.factor, self.indices = parameter, _finite(factor), indices

    def _plans(self, parameters):
        a = parameters[self.parameter]
        b = _Backend(a)
        indices = tuple(range(int(a.size))) if self.indices is None else _indices(self.indices, tuple(a.shape))
        yield self.parameter, indices, b.take(a, indices).astype(b.arithmetic_dtype(a)) * self.factor


class SignFlip(Scale):
    """Flip signs at all elements or explicit indices; undo from saved bytes."""

    def __init__(self, parameter: str, indices: Any = None):
        super().__init__(parameter, -1.0, indices)

    def _plans(self, parameters):
        a = parameters[self.parameter]
        b = _Backend(a)
        indices = tuple(range(int(a.size))) if self.indices is None else _indices(self.indices, tuple(a.shape))
        yield self.parameter, indices, -b.take(a, indices)


@dataclass(frozen=True)
class SwapRecord:
    sequence: int
    from_state: str
    to_state: str
    started_ns: int
    monotonic_ns: int  # Completed synchronization/binding boundary.
    changed_bytes: int  # Logical bytes differing; MLX binds resident references.


class WeightSwap:
    """Two prepared states, switched synchronously in one process.

    Both mappings must have identical keys/shapes/dtypes/backends; ``parameters``
    starts in the base state. Inputs are snapshotted at construction. Changed
    bytes are compared bitwise, preserving signed zero and NaN payloads. NumPy
    retains the mapping and array objects; MLX retains the mapping/model only.
    ``bind`` must install exactly the supplied changed leaves and be reversible.
    No full hashes are computed during a switch; call ``verify`` between runs.
    This class is single-writer and is not thread safe.
    """

    def __init__(self, parameters: Parameters, edited: Mapping[str, Any], *,
                 bind: Callable[[Mapping[str, Any]], None] | None = None,
                 clock_ns: Callable[[], int] = time.monotonic_ns):
        if parameters.keys() != edited.keys():
            raise ValueError("weight states must have identical parameter names")
        _validate_parameters(parameters)
        self._parameters, self._patches = parameters, []
        self._bind, self._clock_ns = bind, clock_ns
        self._state, self._history = "base", []
        self._mlx_backend = None
        self._layouts = {}
        self.base_hashes, self.edited_hashes = {}, {}
        for name, a in parameters.items():
            b, other = _Backend(a), edited[name]
            if b.kind == "mlx":
                self._mlx_backend = b
            self._layouts[name] = (tuple(a.shape), a.dtype)
            ob = _Backend(other)
            if b.kind != ob.kind or a.shape != other.shape or a.dtype != other.dtype:
                raise ValueError(f"parameter {name!r} has incompatible states")
            self.base_hashes[name] = parameter_sha256(a)
            self.edited_hashes[name] = parameter_sha256(other)
            indices = _different_indices(a, other, b)
            if indices:
                self._patches.append(_Patch.prepare(name, a, indices, b.take(other, indices)))

    @property
    def state(self) -> str:
        return self._state

    @property
    def history(self) -> tuple[SwapRecord, ...]:
        return tuple(self._history)

    @property
    def changed_bytes(self) -> int:
        return sum(p.changed_bytes for p in self._patches)

    def switch(self, state: str) -> SwapRecord:
        if state not in ("base", "edited"):
            raise ValueError("state must be 'base' or 'edited'")
        start = _integer(self._clock_ns())
        if start < 0:
            raise ValueError("clock must return nonnegative monotonic nanoseconds")
        if self._history and start < self._history[-1].monotonic_ns:
            raise ValueError("clock must be monotonic")
        previous = self._state
        if previous != state:
            _install(self._parameters, self._patches, state == "edited", self._bind)
        if self._mlx_backend and (previous == state or not self._patches):
            self._mlx_backend.sync([])
        try:
            end = _integer(self._clock_ns())
            if end < start:
                raise ValueError("clock must be monotonic")
        except Exception:
            if previous != state:
                _install(self._parameters, self._patches, previous == "edited", self._bind)
            raise
        self._state = state
        record = SwapRecord(len(self._history), previous, state, start, end,
                            self.changed_bytes if previous != state else 0)
        self._history.append(record)
        return record

    def toggle(self) -> SwapRecord:
        return self.switch("edited" if self.state == "base" else "base")

    def apply(self) -> SwapRecord:
        return self.switch("edited")

    def revert(self) -> SwapRecord:
        return self.switch("base")

    def verify(self) -> None:
        """Full byte hash audit of the current state, outside timed switches."""
        expected = self.edited_hashes if self.state == "edited" else self.base_hashes
        if self._parameters.keys() != expected.keys():
            raise WeightConflictError("parameter names changed")
        for name, a in self._parameters.items():
            if (tuple(a.shape), a.dtype) != self._layouts[name]:
                raise WeightConflictError(f"parameter {name!r} shape/dtype changed")
        for p in self._patches:
            p.check_binding(self._parameters)
        if parameter_hashes(self._parameters) != expected:
            raise WeightConflictError("weights differ from the prepared state")
