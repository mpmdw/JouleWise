#!/usr/bin/env python3
"""Regenerate the Q3 production-kernel versus mpmath oracle grid."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import mpmath as mp


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_bracketing import decimal_student_t_quantile


MP_DPS = 120
ORACLE_BRACKET_TOLERANCE = mp.mpf("1e-110")
PROBABILITIES = ("0.975", "0.995")
DEFAULT_OUTPUT = Path(__file__).with_name("Q3-MPMATH-ORACLE-GRID.json")


def _student_t_cdf(value: mp.mpf, df: int) -> mp.mpf:
    argument = mp.mpf(df) / (mp.mpf(df) + value * value)
    survival = mp.betainc(
        mp.mpf(df) / 2,
        mp.mpf("0.5"),
        0,
        argument,
        regularized=True,
    ) / 2
    return 1 - survival


def _oracle_quantile(probability: str, df: int) -> mp.mpf:
    target = mp.mpf(probability)
    lower = mp.mpf(0)
    upper = mp.mpf(1)
    while _student_t_cdf(upper, df) < target:
        upper *= 2
    while upper - lower > ORACLE_BRACKET_TOLERANCE:
        midpoint = (lower + upper) / 2
        if _student_t_cdf(midpoint, df) < target:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2


def _full_precision(value: mp.mpf) -> str:
    return mp.nstr(value, MP_DPS, strip_zeros=False)


def build_grid() -> list[dict[str, int | str]]:
    mp.mp.dps = MP_DPS
    rows: list[dict[str, int | str]] = []
    for df in range(1, 81):
        for probability in PROBABILITIES:
            kernel = decimal_student_t_quantile(
                probability,
                df,
                use_compatibility_pin=False,
            )
            kernel_text = format(kernel, "f")
            oracle = _oracle_quantile(probability, df)
            absolute_deviation = abs(mp.mpf(kernel_text) - oracle)
            rows.append(
                {
                    "df": df,
                    "p": probability,
                    "kernel": kernel_text,
                    "oracle": _full_precision(oracle),
                    "absdev": _full_precision(absolute_deviation),
                }
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = json.dumps(
        build_grid(),
        ensure_ascii=False,
        allow_nan=False,
        indent=2,
    ) + "\n"
    args.output.write_text(payload, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
