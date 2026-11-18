"""Desk-only draft checks on structural window facts, with no live I/O."""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

ZONE = ZoneInfo("America/Los_Angeles")
MAX_DATES = 20
MAX_LEGS = MAX_DATES * 6
WINDOW_KINDS = frozenset(("W1", "C", "T"))


@dataclass(frozen=True)
class Window:
    """One actual window attempt, identified by its authenticated operational record."""

    attempt_id: str
    kind: str
    t0: int | None
    close: int | None = None
    held_at_midnight: bool = False


@dataclass(frozen=True)
class CountedClose:
    """One structurally verified counted close from this campaign on this host."""

    span_id: str
    stop: str
    soak_end: int
    predicted_batch: int | None
    close: int


def local_day(epoch):
    return datetime.fromtimestamp(epoch, ZONE).date()


def midnight(day):
    return int(datetime.combine(day, time.min, ZONE).timestamp())


def _transfer_start_days(transfer_t0s, as_of):
    served = set()
    for t0 in transfer_t0s:
        if t0 <= as_of:
            day = local_day(t0)
            if day in served:
                raise ValueError(f"multiple transfer starts on {day}")
            served.add(day)
    if len(served) > MAX_DATES:
        raise ValueError(f"transfer starts exceed the {MAX_DATES}-place cap")
    return served


def date_places(windows, transfer_t0s, *, freeze_date: date, as_of):
    """Map eligible dates to the first 20 ordinal places and their supporting attempt IDs.

    A running rollover can suppress its originating date. Its close date replaces the
    originating date when the structural close exists, including for the last window.
    """
    attempts = set()
    eligible = {}
    served = _transfer_start_days(transfer_t0s, as_of)
    starts = [window for window in windows
              if window.kind in WINDOW_KINDS and window.t0 is not None and window.t0 <= as_of]
    for window in starts:
        if window.attempt_id in attempts:
            raise ValueError("use one structural record per window attempt")
        attempts.add(window.attempt_id)
        day = local_day(window.t0)
        cutoff = midnight(day + timedelta(days=1))
        close = window.close if window.close is not None and window.close <= as_of else None
        if close is not None and close < window.t0:
            raise ValueError("window close precedes its t0")
        if window.held_at_midnight and as_of >= cutoff and day not in served:
            if close is None:
                continue
            if close <= cutoff:
                raise ValueError("midnight occupancy conflicts with window close")
            day = local_day(close)
        if day >= freeze_date:
            eligible.setdefault(day, set()).add(window.attempt_id)

    ordered = sorted(eligible)[:MAX_DATES]
    if served.difference(ordered):
        raise ValueError("transfer start outside the eligible date places")
    return {day: (place, tuple(sorted(eligible[day]))) for place, day in enumerate(ordered, 1)}


def arm_bounds(day, *, eligible_at, freeze_at, registered_at, close_proven_at):
    """Inclusive lower and exclusive upper bounds for the launcher and the effective child t0."""
    lower = max(midnight(day), eligible_at, freeze_at, registered_at, close_proven_at)
    upper = midnight(day + timedelta(days=1))
    if lower >= upper:
        raise ValueError("no authorized t0 remains on this date")
    return lower, upper


def permits_t0(epoch, bounds):
    return bounds[0] <= epoch < bounds[1]


def date_dispositions(places, transfer_t0s, *, as_of):
    """Give each eligible date its place, source attempts and as-of disposition."""
    served = _transfer_start_days(transfer_t0s, as_of)
    if served.difference(places):
        raise ValueError("transfer start outside the eligible date places")
    today = local_day(as_of)
    result = {}
    for day, (place, attempts) in places.items():
        status = "served" if day in served else ("missed" if day < today else "pending")
        result[day] = {"place": place, "window_attempts": attempts, "status": status}
    return result


def lower_priority_fits(available_at, projected_span_and_close, pending):
    """Use worst-case availability after lower work and each span's full close overhead.

    Each pending tuple is (earliest t0, exclusive t0 cutoff, worst time from t0 through close).
    A qualification block remains consecutive, including its second span.
    """
    available_at += projected_span_and_close
    for earliest, cutoff, through_close in pending:
        start = max(earliest, available_at)
        if start >= cutoff:
            return False
        available_at = start + through_close
    return True


def counted_batch_hold(closes, *, soak_end, expected_close, predicted_batch):
    """RL-180 row 8 persists for the campaign once triggered by two distinct spans."""
    stops = {row.span_id for row in closes
             if row.stop == "CONTAMINATED_REDOS" and row.predicted_batch is not None
             and row.soak_end <= row.predicted_batch <= row.close}
    return (len(stops) >= 2 and predicted_batch is not None
            and soak_end <= predicted_batch <= expected_close)
