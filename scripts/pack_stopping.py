#!/usr/bin/env python3
"""Write the pack's registered stopping decision."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.pack_stopping import main

if __name__ == "__main__":
    raise SystemExit(main())
