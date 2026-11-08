"""ABLATION-ARTIFACT desk planning and synthetic descriptors; no acquisition.

No models/files are loaded and there is no native measurement CLI. Reuse the
weight edit, operand statistics, lock-in, rail-ladder and replay tools. All
predictions concern explicit host storage traversals, not measured GPU toggles
or energy. Numerical functions load NumPy lazily; make_plan is stdlib-only.
"""

from __future__ import annotations

import argparse
import json
import math
import random

from ._common import require_numpy
from .operand_stats import combine_statistics, operand_statistics
from .weight_edits import AblationReplacement, _Backend, parameter_hashes


def replace_activation(values, mask, replacement):
    """Common runtime where for all styles and clean-residual patch controls.

    All operands must already be prepared on the same backend, with exactly
    matching shapes, and values/replacement dtypes. True means replace. This
    runs no calibration, sampling, hash, synchronization or model I/O. Callers
    own native evaluation, residency, graph auditing and measurement boundaries.
    """
    backend = _Backend(values)
    if any(type(a).__module__.split(".")[0] != backend.kind for a in (mask, replacement)):
        raise TypeError("activation operands must use the same array backend")
    if tuple(mask.shape) != tuple(values.shape) or mask.dtype != backend.xp.bool_:
        raise ValueError("activation mask must be bool and exactly match values")
    if tuple(replacement.shape) != tuple(values.shape) or replacement.dtype != values.dtype:
        raise ValueError("replacement shape/dtype must exactly match values")
    return backend.xp.where(mask, replacement, values)


def toggle_statistics(values, *, storage=None) -> dict:
    """Report row-to-row and within-row feature transitions separately.

    Rows represent tokens/samples, columns features. For bf16, supply decoded
    float32 values and shape-matched uint16 storage words. Within-row counts
    exclude row boundaries. These two traversal proxies need not have the same
    ordering; neither identifies a Metal kernel's physical operand sequence.
    """
    np = require_numpy()
    values = np.asarray(values)
    encoded = values if storage is None else np.asarray(storage)
    if values.ndim != 2 or not all(values.shape) or encoded.shape != values.shape:
        raise ValueError("values/storage must be matching nonempty matrices")
    return {
        "row_to_row": operand_statistics(values, storage=encoded, tile_elements=values.shape[1]),
        "within_row": combine_statistics([
            operand_statistics(row, storage=bits, tile_elements=1)
            for row, bits in zip(values, encoded)
        ]),
        "interpretation": "host storage proxies only; no energy calibration",
    }


def make_plan(*, layers=(0, 3, 7, 11), quads: int = 12, member_seconds: float = 10.0,
              seed: int = 1212) -> dict:
    """Produce a proposed per-layer prefill grid, without loading NumPy/MLX.

    Durations size budgets only. Native members must use equal fixed dispatch
    counts, chosen from independent timing work; never equalize runtime by
    changing work. Each cell's schedule is materialized by
    lockin.make_schedule(**cell['schedule']) after numerical deps are present.
    """
    layers = tuple(layers)
    if (not layers or any(type(i) is not int or i < 0 for i in layers)
            or len(set(layers)) != len(layers)):
        raise ValueError("layers must be distinct nonnegative integers")
    if type(quads) is not int or quads < 1 or type(seed) is not int or seed < 0:
        raise ValueError("quads must be positive and seed nonnegative integers")
    if isinstance(member_seconds, bool) or not math.isfinite(member_seconds) or member_seconds <= 0:
        raise ValueError("member_seconds must be finite and positive")
    cells = []
    for layer in layers:
        for a, b in (("zero", "mean"), ("mean", "resample"), ("zero", "resample"),
                     ("constant", "resample"), ("sham", "sham_copy")):
            for mode in ("patched", "propagated"):
                cells.append({
                    "id": len(cells), "layer": layer, "mode": mode,
                    "a": a, "b": b, "contrast": "B minus A",
                    "schedule": {"n_blocks": quads, "chip_seconds": member_seconds,
                                 "kind": "randomized_abba", "seed": seed + len(cells)},
                })
    random.Random(seed).shuffle(cells)
    return {
        "status": "DRAFT NOT REGISTERED; desk plan only; no collection authority",
        "scope": "per-layer down-projection input; teacher-forced prefill; batch one",
        "primary_boundary": "gross DC input plus signed battery assist",
        "cells": cells, "members": len(cells) * quads * 4,
        "nominal_work_hours": len(cells) * quads * 4 * member_seconds / 3600,
        "budget_excludes": ["positive-control gate", "calibration", "warmup", "idle",
                            "transitions", "instrument checks"],
        "gate": "reuse rail_data_dependence block P before any layer grid",
        "prediction": "direct energy: zero <= mean < resample, conditional on block P; constant unranked",
        "sham_copy": "byte-identical replacement in a distinct prepared buffer; same where/patch graph",
        "open_pins": ["model/config and layer map", "disjoint calibration/evaluation tokens",
                      "dtype/kernel graph", "masks, donors, indices, constant and hashes",
                      "fixed dispatch count", "null SD and non-averaging uncertainty bounds",
                      "timing/frequency tolerances", "claim scale and minimum material effect",
                      "independent sessions, multiplicity and fixed sample size"],
    }


def synthetic_demo(*, seed: int = 1212) -> dict:
    """Tiny reproducible synthetic activation edits and exact byte restoration."""
    np = require_numpy()
    rng = np.random.default_rng(seed)
    template = rng.normal(size=(64, 8)).astype(np.float32)
    calibration = rng.normal(loc=np.linspace(.25, 1.0, 8), size=(128, 8)).astype(np.float32)
    indices = rng.integers(0, len(calibration), size=len(template)).tolist()
    rows = {}
    for style in AblationReplacement.STYLES:
        kwargs = {}
        if style in ("mean", "resample"):
            kwargs["calibration"] = calibration
        if style == "resample":
            kwargs["donor_indices"] = indices
        if style == "constant":
            kwargs["constant"] = 1.0
        state = {"activation": template.copy()}
        before = parameter_hashes(state)
        edit = AblationReplacement("activation", style, np.ones(template.shape, dtype=bool), **kwargs)
        edit.apply(state)
        rows[style] = toggle_statistics(state["activation"])
        edit.revert()
        rows[style]["restored_exact_bytes"] = parameter_hashes(state) == before
    return {"status": "SYNTHETIC ONLY; no power/energy observations", "seed": seed,
            "shape": list(template.shape), "styles": rows,
            "prediction_scope": "repeated per-feature means tie zero on row transitions; resample varies"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan-only", action="store_true")
    mode.add_argument("--synthetic", action="store_true")
    parser.add_argument("--seed", type=int, default=1212)
    parser.add_argument("--layers", nargs="+", type=int, default=[0, 3, 7, 11])
    parser.add_argument("--quads", type=int, default=12)
    parser.add_argument("--member-seconds", type=float, default=10.0)
    args = parser.parse_args(argv)
    result = (make_plan(layers=args.layers, quads=args.quads, member_seconds=args.member_seconds,
                        seed=args.seed) if args.plan_only else synthetic_demo(seed=args.seed))
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
