#!/usr/bin/env python3
"""WP15 R1 runtime entrypoint (``inputs.WP15.runtime_entrypoint``).

    python -B scripts/align_r1_runtime.py --config configs/align/v4/r1_runtime.json \
        --r1-kind KIND --output DIR [--duration-s N] [--soak-reference FILE]

Prints one JSON object (docs/align/r1_runtime_contract.md) on stdout. The
implementation is ``joulewise.align.apple.r1_runtime``.
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.align.apple.r1_runtime import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
