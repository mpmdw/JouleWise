"""Compatibility import; ALIGN thermometry lives in joulewise.align.apple.smc_enumeration."""
import sys
from joulewise.align.apple import smc_enumeration as _implementation
sys.modules[__name__] = _implementation
