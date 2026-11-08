#!/usr/bin/env python3
"""Offline energy/capability frontier from one explicit JSON file or a tiny demo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from joulewise.interp_energy.behaviour_channel import Answer, EnergyModel
from joulewise.interp_energy.edit_frontier import Variant, analyze_variants


def _object(value: object, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _unique_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def _variant(value: object) -> Variant:
    data = dict(_object(value, "variant"))
    model = _object(data.pop("model"), "model")
    if not {"source", "coefficient_basis"}.issubset(model):
        raise ValueError("each model requires explicit source and coefficient_basis")
    answers = data.pop("answers")
    if not isinstance(answers, list):
        raise ValueError("answers must be a JSON array")
    return Variant(model=EnergyModel(**model),
                   answers=[Answer(**_object(row, "answer")) for row in answers], **data)


def synthetic_demo() -> dict:
    """Small arithmetic fixture, unrelated to any model, benchmark or real result."""
    variants = []
    for name, length, n_correct in (("base_on", 120, 12), ("length_lower", 60, 15),
                                     ("base_off", 50, 12), ("length_raise", 180, 19)):
        variants.append({
            "name": name, "cap_tokens": 200,
            "model": {"prefill_j_per_token": 0.02, "decode_j_per_token": 0.1,
                      "context_j_per_token_squared": 0.0005,
                      "coefficient_basis": "gross", "source": "synthetic demo; not calibrated"},
            "answers": [{"problem_id": f"synthetic-{i:02d}", "prefill_tokens": 20 + i,
                         "decode_tokens": length + i % 5, "correct": i < n_correct}
                        for i in range(24)],
        })
    return {"model_id": "synthetic-only", "evaluation_id": "invented arithmetic fixture",
            "boundary": "dc", "baseline": "base_on", "variants": variants}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, nargs="?")
    parser.add_argument("--demo", action="store_true", help="tiny synthetic items, no file input")
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)
    if (args.input is None) == (not args.demo):
        parser.error("supply exactly one input JSON path or --demo")
    try:
        # No path discovery or source-string dereferencing. Only this named JSON is read.
        data = (synthetic_demo() if args.demo else json.loads(
            args.input.read_text(encoding="utf-8"), parse_constant=_reject_constant,
            object_pairs_hook=_unique_object))
        data = dict(_object(data, "input"))
        raw_variants = data.pop("variants")
        if not isinstance(raw_variants, list):
            raise ValueError("variants must be a JSON array")
        result = analyze_variants([_variant(value) for value in raw_variants], **data,
                                  confidence=args.confidence,
                                  bootstrap_samples=args.bootstrap_samples, seed=args.seed)
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
