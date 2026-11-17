#!/usr/bin/env python3
"""RL-174 D.2 close entry point. Shares span_offload's backend, marker, encryption and checks."""
from __future__ import annotations

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.span_offload import main  # noqa: E402


if __name__ == "__main__":
    sys.exit(main(["close", *sys.argv[1:]]))
