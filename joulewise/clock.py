"""Injectable clock seam (decision D-019).

All timestamps in JouleWise artifacts are epoch UTC floats obtained from an
injected clock (decision D-003). ``SystemClock`` is the only place in the
package allowed to call ``time.time()``/``time.sleep()``; ``FakeClock``
advances simulated time instantly so mock runs and tests are fast, exact,
and exercise the identical controller code path.
"""

from __future__ import annotations

import time
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """Minimal time source: wall-clock reads and blocking waits."""

    def now(self) -> float:
        """Return the current time as epoch UTC seconds."""

    def sleep(self, seconds: float) -> None:
        """Block (or simulate blocking) for the given duration."""

    def info(self) -> dict[str, Any]:
        """Return clock metadata for ``metadata.json`` (D-003)."""


class SystemClock:
    """Real wall-clock time. The package's sole caller of ``time``."""

    def now(self) -> float:
        return time.time()

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def info(self) -> dict[str, Any]:
        # Per-process monotonic-vs-wall offset detects wall-clock steps
        # mid-run when compared across artifacts (D-003).
        return {
            "kind": "system",
            "monotonic_minus_wall_s": time.monotonic() - time.time(),
        }


class FakeClock:
    """Simulated time starting at ``start``; ``sleep`` advances instantly."""

    def __init__(self, start: float = 0.0) -> None:
        self._start = float(start)
        self._now = float(start)

    def now(self) -> float:
        return self._now

    def sleep(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("cannot sleep a negative duration")
        self._now += seconds

    def info(self) -> dict[str, Any]:
        return {"kind": "fake", "start_s": self._start}
