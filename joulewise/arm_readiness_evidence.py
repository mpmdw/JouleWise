"""Temporary compatibility alias during Stage 2 extraction."""
import sys
from joulewise import evidence_replay as _implementation
sys.modules[__name__] = _implementation
