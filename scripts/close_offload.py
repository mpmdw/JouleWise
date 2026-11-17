#!/usr/bin/env python3
"""Run JouleWise's synchronous close offload from the magistrate GUI session."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.close_offload import main

if __name__ == "__main__":
    raise SystemExit(main())
