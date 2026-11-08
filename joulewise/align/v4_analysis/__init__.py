"""Primary registered-design v4 analysis; synthetic qualification only so far."""
from .engine import analyze, threshold
from .io import canonical

__all__ = ['analyze', 'threshold', 'canonical']
