"""Specified clock observations for ARM tests; never machine-readiness evidence."""

from joulewise.clock_reference import ClockAnchor


REALTIME_OFFSET_NS = 2_000_000_000_000_000_000


def coherent_clock_anchor(
    *, raw_ns: int = 1_000_000_000_000, skew_ns: int = 1_000, drift_ns: int = 0
) -> ClockAnchor:
    """Keep RAW independent of ordinary monotonic capability deadlines."""
    return ClockAnchor(
        realtime_ns=REALTIME_OFFSET_NS + raw_ns + drift_ns,
        monotonic_raw_ns=raw_ns,
        read_skew_ns=skew_ns,
    )
