#!/usr/bin/env python3
"""Argument front-end for Qwen4 gold parity and optional drift measurement.

The complete streamed runner may import :func:`apply_quant_drift_flag`; this
small front-end also makes the request/fingerprint contract independently
testable on hosts without MLX or real weights.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from joulewise.align.qwen4_gold.canonical_adapter import GoldRequest, with_quant_drift


def apply_quant_drift_flag(request: GoldRequest, bits: int | None) -> GoldRequest:
    return with_quant_drift(request, bits)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--quant-drift-bits", type=int, choices=(5, 6))
    args = parser.parse_args(argv)
    raw = json.loads(args.request.read_text())
    request = GoldRequest(raw["trace_id"], raw.get("payload", {}))
    request = apply_quant_drift_flag(request, args.quant_drift_bits)
    print(json.dumps({"parity_fingerprint": request.parity_fingerprint(),
                      "quant_drift_fingerprint": request.quant_drift_fingerprint()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
