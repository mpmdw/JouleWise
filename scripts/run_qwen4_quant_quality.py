#!/usr/bin/env python3
"""Compact bf16 reference capture and quantized-variant scoring (Qwen4 quant quality)."""
import sys
from pathlib import Path

# ``python3 -B scripts/run_qwen4_quant_quality.py`` puts scripts/ (not the repo
# root) on sys.path; the package import needs the root, as in the sibling runners.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.align.qwen4_quant_quality import main

if __name__ == "__main__":
    raise SystemExit(main())
