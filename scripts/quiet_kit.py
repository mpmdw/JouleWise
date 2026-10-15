#!/opt/homebrew/bin/python3.13
"""Quiet kit entry point. No hardware work at import time."""
import sys
sys.dont_write_bytecode = True
import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.quiet_kit.cli import main

if __name__ == '__main__':
    raise SystemExit(main())
