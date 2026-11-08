#!/usr/bin/env python3
"""Compress, restore, or inspect a session's desk compression record."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.desk_compress import main

if __name__ == "__main__":
    raise SystemExit(main())
