#!/usr/bin/env python3
"""Offline behaviour-channel predictions from explicit JSON inputs only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from joulewise.interp_energy.behaviour_channel import (
    Answer, CapScenario, EnergyModel, compare_answers, compare_scenarios,
)


def _object(value: object, name: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object")
    return value


def _model(value: object) -> EnergyModel:
    data = _object(value, "energy model")
    if not {"source", "coefficient_basis"}.issubset(data):
        raise ValueError("each model requires explicit source and coefficient_basis")
    return EnergyModel(**data)


def _answers(value: object, name: str) -> list[Answer]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a JSON array")
    return [Answer(**_object(row, f"{name} answer")) for row in value]


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    compare = commands.add_parser("compare", help="analyze supplied per-answer JSON")
    compare.add_argument("input", type=Path)
    compare.add_argument("--confidence", type=float, default=0.95)
    compare.add_argument("--bootstrap-samples", type=int, default=2000)
    compare.add_argument("--seed", type=int, default=0)
    compare.add_argument("--unpaired", action="store_true", help="independent-arm resampling")
    scenario = commands.add_parser("scenario", help="Astra-style cap-mixture projection; no CIs")
    scenario.add_argument("input", type=Path, help="JSON containing base_model and optional edited_model")
    scenario.add_argument("--noncap-tokens", nargs="+", type=int, default=[3000, 5000, 8000])
    scenario.add_argument("--prefill-tokens", type=int, default=0)
    scenario.add_argument("--cap-tokens", type=int, default=32768)
    scenario.add_argument("--base-cap-hit-fraction", type=float, default=0.93)
    scenario.add_argument("--edited-cap-hit-fraction", type=float, default=0.331)
    scenario.add_argument("--base-accuracy", type=float, default=0.079)
    scenario.add_argument("--edited-accuracy", type=float, default=0.481)
    scenario.add_argument("--base-duration-s", type=float)
    scenario.add_argument("--edited-duration-s", type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        # No config discovery, source-string dereferencing, network or data pipeline.
        data = _object(json.loads(args.input.read_text(encoding="utf-8"),
                                  parse_constant=_reject_constant,
                                  object_pairs_hook=_unique_object), "input")
        allowed = {"base_model", "edited_model"}
        if args.command == "compare":
            allowed |= {"base", "edited"}
        unknown = set(data) - allowed
        if unknown:
            raise ValueError(f"unknown input keys: {', '.join(sorted(unknown))}")
        base_model = _model(data["base_model"])
        edited_model = _model(data["edited_model"]) if "edited_model" in data else base_model
        if args.command == "compare":
            result = compare_answers(_answers(data["base"], "base"),
                                     _answers(data["edited"], "edited"),
                                     base_model, edited_model, paired=not args.unpaired,
                                     confidence=args.confidence,
                                     bootstrap_samples=args.bootstrap_samples, seed=args.seed)
        else:
            result = {"status": "assumption_based_projection_not_measurement", "scenarios": []}
            for length in args.noncap_tokens:
                base = CapScenario(args.base_cap_hit_fraction, args.base_accuracy, length,
                                   args.prefill_tokens, args.cap_tokens, args.base_duration_s)
                edited = CapScenario(args.edited_cap_hit_fraction, args.edited_accuracy, length,
                                     args.prefill_tokens, args.cap_tokens, args.edited_duration_s)
                result["scenarios"].append(compare_scenarios(base, edited, base_model, edited_model))
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
