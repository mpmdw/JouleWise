"""Compatibility import; ALIGN thermometry lives in joulewise.align.apple.thermal."""
import sys
from joulewise.align.apple import thermal as _implementation
sys.modules[__name__] = _implementation
