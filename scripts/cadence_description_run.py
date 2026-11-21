#!/usr/bin/env python3
"""Dedicated process for the registered cadence description reads."""

from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from joulewise.cadence_looks.description_worker import main


if __name__ == "__main__":
    main()
