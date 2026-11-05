#!/usr/bin/env python3
"""Download, verify, compare, and retire one official Qwen4 text unit at a time."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.align.qwen4_gold.stream import main

if __name__ == "__main__":
    raise SystemExit(main())
