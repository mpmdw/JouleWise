#!/usr/bin/env python3
"""Offline real-weight Qwen4 gold parity. See docs/align/qwen4_exp_port/gold_parity.md."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.align.qwen4_gold.runner import main

if __name__ == "__main__":
    raise SystemExit(main())
