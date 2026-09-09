"""Specified clock observations for ARM tests; never machine-readiness evidence.

REALTIME_OFFSET_NS places the synthetic REALTIME reading about seven years
ahead of the wall clock. That is admissible because every production consumer
of a ClockAnchor compares only REALTIME minus MONOTONIC_RAW (the offset
cancels): joulewise/arm_readiness.py _clock_probe_predicate_passes (authored
and live deltas), joulewise/arm_readiness_evidence_t0.py _derive_clock_attestation,
joulewise/t0_rehearsal.py. No predicate compares an anchor's realtime against
wall-clock now; if one is ever added, these fixtures will start refusing and
this note says why (Opus review 90 N-2).
"""

from joulewise.clock_reference import ClockAnchor


REALTIME_OFFSET_NS = 2_000_000_000_000_000_000


def coherent_clock_anchor(
    clock_gettime_ns=None,
    *,
    raw_ns: int = 1_000_000_000_000,
    skew_ns: int = 1_000,
    drift_ns: int = 0,
) -> ClockAnchor:
    """Keep RAW independent of ordinary monotonic capability deadlines.

    The positional ``clock_gettime_ns`` mirrors the real seam
    ``joulewise.clock_reference.sample_anchor(clock_gettime_ns)`` so a
    side_effect patch cannot raise TypeError at a positional call site and be
    swallowed into a fail-closed refusal (Opus review 90 N-1); it is ignored.
    """
    return ClockAnchor(
        realtime_ns=REALTIME_OFFSET_NS + raw_ns + drift_ns,
        monotonic_raw_ns=raw_ns,
        read_skew_ns=skew_ns,
    )
