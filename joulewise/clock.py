"""Injectable clock seam (decision D-019).

All timestamps in JouleWise artifacts are epoch UTC floats obtained from an
injected clock (decision D-003). ``SystemClock`` is the only place in the
package allowed to call ``time.time()``/``time.sleep()``; ``FakeClock``
advances simulated time instantly so mock runs and tests are fast, exact,
and exercise the identical controller code path.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from joulewise.validation import is_finite_number


@dataclass(frozen=True)
class ClockStamp:
    """A direct epoch read bracketed by controller-monotonic observations."""

    epoch_s: float
    monotonic_before_s: float
    monotonic_after_s: float
    wall_resolution_s: float
    monotonic_resolution_s: float


@runtime_checkable
class Clock(Protocol):
    """Minimal time source: wall-clock reads and blocking waits."""

    def now(self) -> float:
        """Return the current time as epoch UTC seconds."""

    def stamp(self) -> ClockStamp:
        """Return an epoch timestamp with a monotonic read bracket."""

    def sleep(self, seconds: float) -> None:
        """Block (or simulate blocking) for the given duration."""

    def info(self) -> dict[str, Any]:
        """Return clock metadata for ``metadata.json`` (D-003)."""


class SystemClock:
    """Real wall-clock time. The package's sole caller of ``time``."""

    def __init__(self) -> None:
        self._wall_resolution_s = time.get_clock_info("time").resolution
        self._monotonic_resolution_s = time.get_clock_info("monotonic").resolution
        self._info_start = self.stamp()

    def now(self) -> float:
        return time.time()

    def stamp(self) -> ClockStamp:
        monotonic_before_s = time.monotonic()
        epoch_s = time.time()
        monotonic_after_s = time.monotonic()
        return ClockStamp(
            epoch_s=epoch_s,
            monotonic_before_s=monotonic_before_s,
            monotonic_after_s=monotonic_after_s,
            wall_resolution_s=getattr(self, "_wall_resolution_s", time.get_clock_info("time").resolution),
            monotonic_resolution_s=getattr(
                self,
                "_monotonic_resolution_s",
                time.get_clock_info("monotonic").resolution,
            ),
        )

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def info(self) -> dict[str, Any]:
        end = self.stamp()
        return {
            "kind": "system",
            "monotonic_minus_wall_s": end.monotonic_after_s - end.epoch_s,
            "wall_resolution_s": self._wall_resolution_s,
            "monotonic_resolution_s": self._monotonic_resolution_s,
            "wall_minus_monotonic_start_s": (
                self._info_start.epoch_s - self._info_start.monotonic_after_s
            ),
            "wall_minus_monotonic_end_s": end.epoch_s - end.monotonic_after_s,
        }


class FakeClock:
    """Simulated time starting at ``start``; ``sleep`` advances instantly."""

    def __init__(self, start: float = 0.0) -> None:
        self._start = float(start)
        self._now = float(start)

    def now(self) -> float:
        return self._now

    def stamp(self) -> ClockStamp:
        return ClockStamp(
            epoch_s=self._now,
            monotonic_before_s=self._now,
            monotonic_after_s=self._now,
            wall_resolution_s=0.0,
            monotonic_resolution_s=0.0,
        )

    def sleep(self, seconds: float) -> None:
        if not is_finite_number(seconds):
            raise ValueError("sleep duration must be a finite number")
        if seconds < 0:
            raise ValueError("cannot sleep a negative duration")
        self._now += seconds

    def info(self) -> dict[str, Any]:
        return {"kind": "fake", "start_s": self._start}
