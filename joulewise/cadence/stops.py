"""Named stops: the only conditions that page the lead and the research lead per span.

``evaluate_named_stops`` takes a span's operational summary (no energy) and the
campaign history, and returns the stops that fire. Anything else a span shows
is recorded by its predeclared disposition and does not page anyone.

| Code | Fires when |
|---|---|
| REFUSAL | the results ref is not a clean completion (chain exit code non-zero, outcome not COMPLETE, or no result by the deadline). ``verdict: GO`` alone is never success |
| INSTRUMENT_FAULT | ``fault`` true, the KM003C capture missing, a feed not proven stopped, meter bad polls or USB errors above zero |
| CONTAMINATED_REDOS | contaminated redos (scope span or campaign) reach ``contaminated_redos_max`` |
| BAND_UNREACHABLE | one start band is unreachable ``band_unreachable_max`` times (scope span or campaign) |
| LEG_OVERTIME | a leg's wall time exceeds ``leg_time_factor`` x its budget |

Span summary shape (all operational): ``{"result": {chain_exit_code, chain_outcome, fault, outcome},
"meter": {present, proven_stopped, bad_polls, usb_errors}, "feeds_proven_stopped": bool,
"legs": [{leg_id, wall_s, budget_s, start_band, band_reached, contaminated_redos}]}``.
"""
from __future__ import annotations

from collections import Counter

from joulewise.cadence.queue import result_ok

CODES = ("REFUSAL", "INSTRUMENT_FAULT", "CONTAMINATED_REDOS", "BAND_UNREACHABLE", "LEG_OVERTIME")


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def evaluate_named_stops(rules, span, history=()):
    """Return [{code, detail}] for one span. ``history`` holds earlier span summaries of the campaign."""
    stops = []
    result = span.get("result")
    if result is None:
        stops.append({"code": "REFUSAL", "detail": "no terminal result"})
    elif not result_ok(result) and result.get("fault") is not True:
        stops.append({"code": "REFUSAL", "detail": (
            f"chain_exit_code={result.get('chain_exit_code')} chain_outcome={result.get('chain_outcome')} "
            f"outcome={result.get('outcome')}")})
    meter = span.get("meter") or {}
    faults = []
    if result is not None and result.get("fault") is True:
        faults.append("result fault")
    if meter.get("present") is not True:
        faults.append("KM003C capture missing")
    if meter.get("proven_stopped") is not True:
        faults.append("meter feed not proven stopped")
    for key in ("bad_polls", "usb_errors"):
        if not _num(meter.get(key)) or meter[key] > 0:
            faults.append(f"meter {key} {meter.get(key)}")
    if span.get("feeds_proven_stopped") is not True:
        faults.append("a feed not proven stopped")
    if faults:
        stops.append({"code": "INSTRUMENT_FAULT", "detail": "; ".join(faults)})

    legs = span.get("legs") or []
    pool = list(legs)
    if rules["contaminated_redos_scope"] == "campaign":
        pool = [leg for past in history for leg in past.get("legs") or []] + pool
    redos = sum(int(leg.get("contaminated_redos") or 0) for leg in pool)
    if redos >= rules["contaminated_redos_max"]:
        stops.append({"code": "CONTAMINATED_REDOS",
                      "detail": f"{redos} contaminated redos ({rules['contaminated_redos_scope']})"})

    band_pool = list(legs)
    if rules["band_unreachable_scope"] == "campaign":
        band_pool = [leg for past in history for leg in past.get("legs") or []] + band_pool
    misses = Counter(leg.get("start_band") for leg in band_pool if leg.get("band_reached") is False)
    for band, n in sorted(misses.items(), key=lambda kv: str(kv[0])):
        if n >= rules["band_unreachable_max"]:
            stops.append({"code": "BAND_UNREACHABLE", "detail": f"band {band} unreachable {n} times "
                                                                f"({rules['band_unreachable_scope']})"})
    for leg in legs:
        wall, budget = leg.get("wall_s"), leg.get("budget_s")
        if not (_num(wall) and _num(budget) and budget > 0):
            stops.append({"code": "LEG_OVERTIME", "detail": f"{leg.get('leg_id')}: wall or budget not recorded"})
        elif wall > rules["leg_time_factor"] * budget:
            stops.append({"code": "LEG_OVERTIME",
                          "detail": f"{leg.get('leg_id')}: {wall:.0f} s > {rules['leg_time_factor']} x {budget:.0f} s"})
    return stops
