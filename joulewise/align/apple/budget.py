"""Opt-in ALIGN admission and safety limits (council FINAL-DESIGN §2.2).

The decode budget admits whole turns; it never shortens an admitted turn.
The deadman uses the episode's monotonic deadline. On the production main
thread a POSIX timer also interrupts a stalled Python/native stream call.
An uninterruptible device/OS call still needs the runner's outer member cap.
"""
from __future__ import annotations

from contextlib import contextmanager
import signal
import threading

from joulewise.align.apple.sampler import monotonic_ns, NS_PER_SECOND
from joulewise.clock import SystemClock


class DeadmanExpired(BaseException):
    """Cancellation that generic model/tool ``except Exception`` cannot hide."""


class EpisodeDeadman:
    def __init__(self, clock, start, seconds):
        self.clock = clock
        self.deadline_ns = monotonic_ns(start) + round(seconds * NS_PER_SECOND)

    def remaining_s(self):
        return (self.deadline_ns - monotonic_ns(self.clock.stamp())) / NS_PER_SECOND

    def expired(self):
        return self.remaining_s() <= 0

    @contextmanager
    def guard(self):
        """Bound one blocking operation, without leaving a timer in the caller.

        Fake clocks use checks at operation/token boundaries. Refuse an unsafe
        production timer environment rather than silently losing hang coverage.
        """
        remaining = self.remaining_s()
        if remaining <= 0:
            raise DeadmanExpired()
        real = isinstance(self.clock, SystemClock)
        if real:
            if threading.current_thread() is not threading.main_thread():
                raise RuntimeError("ALIGN deadman requires the main thread")
            if not hasattr(signal, "setitimer"):
                raise RuntimeError("ALIGN deadman requires POSIX setitimer")
            if signal.getitimer(signal.ITIMER_REAL) != (0.0, 0.0):
                raise RuntimeError("ALIGN deadman cannot replace an active timer")
            previous = signal.getsignal(signal.SIGALRM)
            armed = True

            def expire(signum, frame):
                if armed:
                    raise DeadmanExpired()

        try:
            if real:
                signal.signal(signal.SIGALRM, expire)
                signal.setitimer(signal.ITIMER_REAL, remaining)
            yield
        finally:
            if real:
                # The operation has returned. A pending alarm delivered during
                # disarm must not discard its result or interrupt restoration.
                armed = False
                try:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                finally:
                    signal.signal(signal.SIGALRM, previous)


def budget_record(spec, turns, stop_reason, *, incomplete=False, effective_context_cap=None):
    """Member evidence; absent for legacy specs so their records stay identical."""
    if spec.max_episode_decode_tokens is None and spec.deadman_s is None:
        return {}
    return {"token_budget": {
        "max_episode_decode_tokens": spec.max_episode_decode_tokens,
        "max_tokens_per_turn": spec.max_tokens,
        "max_context_tokens": spec.max_context_tokens,
        "effective_context_cap": effective_context_cap,
        "deadman_s": spec.deadman_s,
        "decode_tokens_used": sum(t.decode_tokens for t in turns),
        "prefill_tokens_used": sum(t.prefill_tokens for t in turns),
        "cached_context_tokens_used": sum(t.context_tokens for t in turns),
        "stop_reason": stop_reason,
        "incomplete": incomplete,
    }}
