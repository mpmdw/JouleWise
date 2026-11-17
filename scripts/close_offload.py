#!/usr/bin/env python3
"""Synchronous after-Check close, using the shared span-offload backend."""
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from joulewise import close_offload  # noqa: E402
from scripts import span_offload  # noqa: E402


if __name__ == "__main__":
    if sys.argv[1:2] and sys.argv[1] not in {"after-check", "reclaim", "-h", "--help"}:
        # Retain #804's explicit single-OUT entry point for its native probe and existing callers.
        sys.exit(span_offload.main(["close", *sys.argv[1:]]))
    sys.exit(close_offload.main())
