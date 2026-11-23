"""Verify a dated issue against the public arm snapshot and pinned child receipt.

Inputs are projections from the caller's authenticated public records. The
caller resolves main, verifies any freeze naming record and predecessor close,
and validates the committed queue on the pinned tool. This verifier binds those
facts to one issue and receipt. It performs no I/O or clock reads.
"""

from collections.abc import Mapping
from datetime import date, datetime, timedelta
from fractions import Fraction
from hashlib import sha256
import json
import re

from date_rules import (MAX_DATES, NS_PER_SECOND, ZONE, VerifiedTransferStart,
                        date_places, local_day, midnight)


def _present(value):
    return isinstance(value, str) and bool(value.strip())


def _hex(value, width):
    return isinstance(value, str) and re.fullmatch(f"[0-9a-f]{{{width}}}", value) is not None


def _epoch_ns(value, label):
    if type(value) is not int or value <= 0:
        raise ValueError(f"unknown {label} epoch")
    return value


def _effective_freeze_ns(freeze, main, issued_hash):
    if (freeze["main_commit"] != main or freeze["look_id"] != "lm-interim-01"
            or not _hex(issued_hash, 64) or freeze["coefficients_sha256"] != issued_hash
            or not _hex(freeze["public_sha256"], 64)):
        raise ValueError("public freeze does not match the issue and main")
    published_at = _epoch_ns(freeze["published_at_ns"], "freeze publication")
    twin = freeze["twin_agrees"]
    if twin == "yes":
        return published_at
    naming = freeze.get("naming")
    if (twin not in ("no", "not_evaluable") or not isinstance(naming, Mapping)
            or naming.get("verified") is not True or not _present(naming.get("ruling"))
            or any(naming.get(key) != freeze[key] for key in
                   ("main_commit", "look_id", "coefficients_sha256", "public_sha256"))):
        raise ValueError("no effective public freeze or verified naming ruling")
    named_at = _epoch_ns(naming["named_at_ns"], "freeze naming")
    if named_at < published_at:
        raise ValueError("freeze naming precedes publication")
    return named_at


def _registered_ns(registration, main, issued_hash, checked_at):
    if (not _hex(issued_hash, 64) or registration["main_commit"] != main
            or registration["sha256"] != issued_hash or registration["ledger_sha256"] != issued_hash
            or _epoch_ns(registration["checked_at_ns"], "registration refresh") != checked_at):
        raise ValueError("no fresh, matching public registration and main ledger row")
    return _epoch_ns(registration["registered_at_ns"], "registration")


def _predecessor_close(issue, arm):
    predecessor = arm["predecessor"]
    if (predecessor != issue["predecessor"] or not _present(predecessor["span_id"])
            or not _present(predecessor["close_receipt"])):
        raise ValueError("issue does not bind the known latest predecessor")
    exact_close = _epoch_ns(predecessor["close_ns"], "predecessor close")
    latest_close = _epoch_ns(arm["latest_close_ns"], "latest proven close")
    if latest_close < exact_close:
        raise ValueError("latest proven close precedes predecessor close")
    return exact_close, latest_close


def _check_queue(issue, raw_queue, day, upper):
    if not isinstance(raw_queue, bytes) or sha256(raw_queue).hexdigest() != issue["queue_sha256"]:
        raise ValueError("committed queue digest differs from issue")
    queue = json.loads(raw_queue)
    if queue["schema"] != "joulewise.cadence_queue.v1" or queue["halt"] is not None:
        raise ValueError("no unhalted pinned issue queue")
    expiry = datetime.fromisoformat(queue["expires_at"])
    local_cutoff = datetime.fromtimestamp(upper, ZONE)
    if expiry != local_cutoff or expiry.utcoffset() != local_cutoff.utcoffset():
        raise ValueError("issue queue must expire at the bound date's local midnight")

    span = issue["span"]
    legs = span["legs"]
    if (not _present(span["span_id"]) or not _present(span["kit"]["path"])
            or not _hex(span["kit"]["sha256"], 64) or not _hex(issue["runner_pin"], 40)
            or type(span["seq"]) is not int or span["seq"] < 1
            or type(span["attempt"]) is not int or not 1 <= span["attempt"] <= 9
            or span["not_before"] != day.isoformat() or span.get("rerun_of") is not None
            or not isinstance(legs, list) or len(legs) != 6
            or not all(_present(leg) for leg in legs) or len(set(legs)) != 6):
        raise ValueError("invalid dated six-leg span binding")
    selected = [entry for entry in queue["spans"]
                if entry["span_id"] == span["span_id"] or entry["seq"] == span["seq"]]
    if selected != [span] or any(type(selected[0][key]) is not int for key in ("seq", "attempt")):
        raise ValueError("committed queue does not bind exactly one matching span")


def _check_date(windows, prior, issue, authority, checked_at, freeze_at):
    day, place = issue["day"], issue["place"]
    if (not _present(issue["issue_id"]) or authority["issue_ids"] != (issue["issue_id"],)
            or _epoch_ns(authority["checked_at_ns"], "date refresh") != checked_at or authority["day"] != day
            or type(authority["place"]) is not int or authority["place"] != place):
        raise ValueError("no fresh date authority for exactly one matching issue")
    for start in prior:
        if not isinstance(start, VerifiedTransferStart) or start.t0_ns > checked_at:
            raise ValueError("prior transfer starts require verified evidence as of arm")
        if day == start.day or issue["issue_id"] == start.issue_id or issue["span"]["span_id"] == start.span_id:
            raise ValueError("date, issue or span already served by a verified transfer start")

    freeze_day = local_day(freeze_at // NS_PER_SECOND)
    places = date_places(windows, prior, freeze_date=freeze_day, as_of=Fraction(checked_at, NS_PER_SECOND))
    if places.get(day) != (place, authority["window_attempts"]):
        raise ValueError("no remaining dated capacity with the issued place and window evidence")
    observed_at = _epoch_ns(authority["observed_at_ns"], "date authority observation")
    observed = date_places(windows, prior, freeze_date=freeze_day, as_of=Fraction(observed_at, NS_PER_SECOND))
    current_sources = authority["window_attempts"]
    if day not in observed or not set(observed[day][1]).intersection(current_sources):
        raise ValueError("date authority predates its supporting eligibility evidence")
    return observed_at


def _child_t0(issue, receipt, day, upper, exact_close, required_lower, checked_at):
    bounds = issue["t0_authority"]
    lower_s = bounds["t0_not_before"]
    if (bounds["authorized_t0_date"] != day.isoformat()
            or type(lower_s) is not int or not 0 < lower_s < upper
            or type(bounds["t0_before"]) is not int or bounds["t0_before"] != upper
            or type(bounds["t0_not_before_ns"]) is not int or bounds["t0_not_before_ns"] != exact_close):
        raise ValueError("original child bounds must bind the date and exact close")
    lower = max(lower_s * NS_PER_SECOND, exact_close)
    if lower < required_lower or not lower <= checked_at < upper * NS_PER_SECOND:
        raise ValueError("original child bounds do not authorize the refreshed arm")

    span = issue["span"]
    if (receipt["schema"] != "joulewise.cadence_span_receipt.v1"
            or receipt["span_id"] != span["span_id"] or receipt["roster"] != span["legs"]
            or receipt["kit"]["sha256"] != span["kit"]["sha256"]
            or receipt["kit"]["frozen_commit"] != issue["runner_pin"]):
        raise ValueError("child receipt does not bind the issued span, roster, kit and pin")
    child_bounds = receipt["t0_authority"]
    if (child_bounds != bounds
            or any(type(child_bounds[key]) is not int for key in ("t0_not_before", "t0_not_before_ns", "t0_before"))):
        raise ValueError("child receipt changed the original t0 authority")
    t0 = _epoch_ns(receipt["started"]["epoch_ns"], "child t0")
    if not checked_at <= t0 < upper * NS_PER_SECOND or local_day(t0 // NS_PER_SECOND) != day:
        raise ValueError("child t0 falls outside its dated authority")
    return t0


def verify_transfer_start(*, windows, prior_starts, issue, arm, queue_bytes, receipt):
    """Return the verified start to count, or raise ValueError for a refusal.

    Supply the original issue and its original child arguments, the arm's fresh
    registration and date observations at one checked_at_ns, and the child's
    structural receipt. Epochs with an _ns suffix are integer nanoseconds.
    Verify in arm order and pass the earlier verified starts as prior_starts.
    An effective t0 can count even if the child aborts after t0.
    """
    try:
        day = issue["day"]
        place = issue["place"]
        if type(day) is not date or type(place) is not int or not 1 <= place <= MAX_DATES:
            raise ValueError("issue is outside the dated place cap")
        checked_at = _epoch_ns(arm["checked_at_ns"], "arm refresh")
        main = arm["main_commit"]
        if not _hex(main, 40):
            raise ValueError("unknown main snapshot")
        freeze_at = _effective_freeze_ns(arm["freeze"], main, issue["freeze_sha256"])
        registered_at = _registered_ns(arm["registration"], main, issue["registration_sha256"], checked_at)
        exact_close, latest_close = _predecessor_close(issue, arm)
        observed_at = _check_date(tuple(windows), tuple(prior_starts), issue, arm["date_authority"],
                                  checked_at, freeze_at)
        upper = midnight(day + timedelta(days=1))
        _check_queue(issue, queue_bytes, day, upper)

        release_at = arm["released_at_ns"]
        if release_at is not None:
            release_at = _epoch_ns(release_at, "release")
        lower = max(midnight(day) * NS_PER_SECOND, observed_at, freeze_at, registered_at,
                    _epoch_ns(issue["issued_at_ns"], "issue"),
                    _epoch_ns(issue["queue_committed_at_ns"], "queue commit"),
                    latest_close, release_at or 0)
        t0 = _child_t0(issue, receipt, day, upper, exact_close, lower, checked_at)
    except (KeyError, TypeError, AttributeError, OverflowError) as error:
        raise ValueError("missing or malformed dated transfer authority") from error
    return VerifiedTransferStart(issue["issue_id"], issue["span"]["span_id"], day, place, t0)
