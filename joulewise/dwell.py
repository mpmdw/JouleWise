"""Temporary compatibility alias during Stage 2 extraction."""
import sys
from joulewise.hazards import dwell as _implementation
sys.modules[__name__] = _implementation
