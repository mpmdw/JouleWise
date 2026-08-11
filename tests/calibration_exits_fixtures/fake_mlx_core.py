"""Yielding MLX process fixture for public calibration-writer tests."""

import time


__version__ = "test-mlx-1"


class _Array:
    def astype(self, _dtype):
        return self


class _Random:
    def normal(self, _shape):
        return _Array()


random = _Random()
float16 = object()


def matmul(_left, _right):
    return _Array()


def eval(*_values):
    # The production pulse remains a real timed loop, but the fake backend
    # yields instead of turning the entire interval into a busy-spin.
    time.sleep(0.0005)

