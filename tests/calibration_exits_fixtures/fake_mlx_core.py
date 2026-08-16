"""MLX process fixture for public calibration-writer tests."""

import json
import os
from pathlib import Path
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
_fence_count = 0


def matmul(_left, _right):
    return _Array()


def eval(*_values):
    global _fence_count
    # Buffer allocation fences two arrays. Pulse fences one product, which
    # gives the suspension-immunity regression a precise producer-mid-pulse
    # delay seam without altering the logical command clock.
    if len(_values) == 1:
        _fence_count += 1
        delay_target = int(os.environ.get("JW_FAKE_MLX_DELAY_ON_FENCE", "0"))
        if delay_target == _fence_count:
            delay_s = float(os.environ.get("JW_FAKE_MLX_DELAY_S", "0"))
            marker = os.environ.get("JW_FAKE_MLX_DELAY_RESULT_PATH")
            if marker:
                Path(marker).write_text(
                    json.dumps(
                        {"delay_s": delay_s, "fence": _fence_count},
                        sort_keys=True,
                    )
                    + "\n",
                    encoding="utf-8",
                )
            time.sleep(delay_s)
    time.sleep(0.0005)
