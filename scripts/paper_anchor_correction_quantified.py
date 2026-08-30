#!/usr/bin/env python3
"""How much did the corrected clock-anchor model move the calibration bound?

WHAT THIS ANSWERS.  The paper's first contribution is a correction to the
*clock anchor*: the estimator that decides which instant of real (wall-clock)
time the first row of a ``powermetrics`` trace corresponds to.  Every capture in
the retained diagnostic population was originally stamped by the earlier
estimator (registered under the identity string
``powermetrics_native_second_censored_intersection_v1``, referred to in the code
as ``CLOCK_METHOD_V2`` and below as **the v2 anchor**).  The corrected estimator
is ``powermetrics_native_second_rate_aware_set_membership_v1``
(``CLOCK_METHOD_V3``, **the v3 anchor**).

A reviewer of the frozen draft asked, in effect: *the numbers that motivate the
paper were produced by the estimator the paper then fixes -- so how far off were
they?*  This script answers that by re-deriving, from the retained primary bytes
of every capture in the population, the calibration bound ``B_fiducial`` under
both anchors, and reporting the distribution of the change.

``B_fiducial`` is the capture's calibration bound: the largest timing
disagreement, in seconds, between when the experiment *commanded* a power pulse
and when the instrument's trace *shows* that pulse, maximised over every
commanded edge and then widened by the clock-anchor term.  A smaller
``B_fiducial`` means the instrument's timeline is pinned more tightly to the
experiment's timeline.

THREE QUANTITIES PER CAPTURE, and why all three are needed:

  ``stored``          the bound written into ``instrument_evidence.json`` at
                      capture time, by the v2 anchor and the code of that day.
  ``rederived_v2``    the bound recomputed *today* from the same primary bytes,
                      holding the anchor at v2.
  ``rederived_v3``    the bound recomputed today under the corrected v3 anchor.

``rederived_v3 - stored`` is what a reader of the draft cares about, but on its
own it cannot distinguish the anchor correction from any unrelated drift in the
detector code between capture day and today.  ``rederived_v2`` is the control
that separates them: if ``rederived_v2`` equals ``stored`` exactly, then the
detector is unchanged and the entire difference is the anchor model.  This
script checks that equality per capture and reports it, rather than assuming it.

ADMISSIBILITY.  A capture is *admissible* when its calibration evidence can be
used at all: the anchor must resolve to a bounded interval, every commanded
pulse must be detected, and the detector must return no refusal reasons.  A
capture that is admissible under one anchor and refused under the other is an
**admissibility flip**, and this script reports flips separately from the
numeric deltas -- a refusal is a result, not a missing measurement.

SCOPE AND STANDING.  The energy values from this diagnostic era are VOIDED for
claim use under decision D-078 (a time-anchor defect voided claim use of all
powermetrics corpora collected before the repair).  Nothing here un-voids them.
This analysis treats the population purely as PILOT evidence about the size and
character of the anchor correction itself.

Replay:

    /Users/edr/code/JouleWise/.venv/bin/python \\
        scripts/paper_anchor_correction_quantified.py \\
        --corpus-root /Users/edr/code/JouleWise \\
        --out docs/paper/round7/anchor-correction-quantified.json

Output is deterministic: sorted JSON keys, fixed decimal places on all
millisecond and percent quantities, and full binary64 ``repr`` on any quantity
the frozen draft prints, so it can be compared digit-for-digit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------

# The population: every retained instrument-validation capture under this
# subdirectory of the corpus root.
POPULATION_SUBDIRECTORY = Path("runs") / "instrument_validation"

# The worked capture the frozen draft prints, and the value it prints for it.
# The v3 re-derivation must reproduce this exactly or the whole run is void.
WORKED_CAPTURE_ID = "20260722T145535-e941c821"
DRAFT_B_FIDUCIAL_S = 0.030067931757111657

# Additional roots searched for the raw plists.  Each is ~88 MB and none are in
# git; the repository keeps them out of tree and mirrors them to iCloud.  This
# mirrors scripts/paper_excursion_decomposition.py and
# scripts/check_paper_replay_fence.py.
BACKUP_ROOTS = (
    Path("/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup"),
)

# Fixed float formatting for byte-reproducible output.
MS_DECIMALS = 6
PCT_DECIMALS = 6


class PopulationUnavailable(RuntimeError):
    """The retained capture population is not present on this machine."""


class CalibrationGateFailed(RuntimeError):
    """The v3 re-derivation did not reproduce the frozen draft's value."""


# ---------------------------------------------------------------------------
# Small helpers.
# ---------------------------------------------------------------------------


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _ms(seconds: float) -> float:
    """Seconds to milliseconds at fixed precision (deterministic output)."""

    return round(seconds * 1000.0, MS_DECIMALS)


def _quantile(ordered: list[float], fraction: float) -> float:
    """Linear-interpolated quantile of an already-sorted sample."""

    if not ordered:
        raise ValueError("empty sample")
    if len(ordered) == 1:
        return ordered[0]
    position = fraction * (len(ordered) - 1)
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return ordered[lower_index]
    weight = position - lower_index
    return ordered[lower_index] * (1.0 - weight) + ordered[upper_index] * weight


def describe(values: list[float], decimals: int, unit: str) -> dict[str, Any]:
    """Median, inter-quartile spread, extremes, and sign counts for one sample.

    ``unit`` is a bare suffix (``ms`` or ``pct``) appended to every key so the
    JSON never carries a unitless number.
    """

    if not values:
        return {"count": 0}
    ordered = sorted(values)
    median = statistics.median(ordered)
    q1 = _quantile(ordered, 0.25)
    q3 = _quantile(ordered, 0.75)
    return {
        "count": len(ordered),
        f"min_{unit}": round(ordered[0], decimals),
        f"q1_{unit}": round(q1, decimals),
        f"median_{unit}": round(median, decimals),
        f"q3_{unit}": round(q3, decimals),
        f"max_{unit}": round(ordered[-1], decimals),
        f"iqr_{unit}": round(q3 - q1, decimals),
        f"mean_{unit}": round(statistics.fmean(ordered), decimals),
        f"stdev_{unit}": (
            round(statistics.stdev(ordered), decimals) if len(ordered) > 1 else 0.0
        ),
        f"max_absolute_{unit}": round(max(abs(value) for value in ordered), decimals),
        "count_positive": sum(1 for value in ordered if value > 0.0),
        "count_negative": sum(1 for value in ordered if value < 0.0),
        "count_zero": sum(1 for value in ordered if value == 0.0),
    }


def _refusal_token(exc: BaseException) -> str:
    """A short, stable slug naming *why* a re-derivation refused.

    The full exception text is reported alongside; this token exists so refusals
    can be counted and grouped without string-matching prose.
    """

    text = str(exc).lower()
    table = (
        ("trace anchor is unresolved", "anchor_unresolved"),
        ("anchor method is unregistered", "anchor_method_unregistered"),
        ("anchor evidence is malformed", "anchor_evidence_malformed"),
        ("clock anchor is missing", "anchor_block_missing"),
        ("clock stamps are missing", "anchor_stamps_missing"),
        ("pulse", "pulse_detection_failure"),
        ("protocol", "protocol_mismatch"),
    )
    for needle, token in table:
        if needle in text:
            return token
    return f"unclassified_{type(exc).__name__}"


# ---------------------------------------------------------------------------
# Locating primary bytes.
# ---------------------------------------------------------------------------


def locate_raw_powermetrics(
    corpus_root: Path, validation_id: str, expected_sha256: str
) -> tuple[bytes, str]:
    """Return the retained raw plist bytes, hash-verified against the evidence.

    Returns the bytes and the path they came from.  A file whose sha256 does not
    match the evidence is never used: the evidence hash is the custody record,
    so a mismatching file is a different artifact wearing the same name.
    """

    candidates: list[Path] = []
    for parent in sorted(corpus_root.glob("runs*")):
        candidates.append(
            parent / "instrument_validation" / validation_id / "raw" / "powermetrics.plist"
        )
        candidates.append(
            parent
            / "runs"
            / "instrument_validation"
            / validation_id
            / "raw"
            / "powermetrics.plist"
        )
    for root in BACKUP_ROOTS:
        if not root.is_dir():
            continue
        candidates.extend(
            sorted(
                root.glob(
                    f"*/instrument_validation/{validation_id}/raw/powermetrics.plist"
                )
            )
        )
        candidates.extend(
            sorted(
                root.glob(
                    f"*/*/instrument_validation/{validation_id}/raw/powermetrics.plist"
                )
            )
        )
    inspected: list[str] = []
    for candidate in candidates:
        if not candidate.is_file():
            continue
        raw = candidate.read_bytes()
        if _sha256(raw) == expected_sha256:
            return raw, str(candidate)
        inspected.append(f"{candidate} (sha256 {_sha256(raw)})")
    raise FileNotFoundError(
        f"no raw/powermetrics.plist matching sha256 {expected_sha256} for "
        f"{validation_id}; inspected: {inspected or 'no candidate path existed'}"
    )


# ---------------------------------------------------------------------------
# Per-capture work.
# ---------------------------------------------------------------------------


def _classify_generation(method: Any, v2: str, v3: str) -> str:
    if method == v2:
        return "v2_era"
    if method == v3:
        return "v3_era"
    return "unregistered"


def _derive_anchors(raw: bytes, anchor_block: Any) -> dict[str, Any]:
    """Derive the clock anchor alone under each estimator, and report why.

    The full calibration path raises a single opaque error when the anchor does
    not resolve.  Running the two anchor derivations directly, from one parse of
    the trace, records *which* estimator resolved and the estimator's own reason
    when it did not -- so a refusal in this file is traceable to a named cause
    rather than to the word "refused".

    The ``effective_clock_anchor_bound_s`` reported here is the anchor term: the
    residual uncertainty, in seconds, about where the trace's first sample sits
    on the wall clock.  It is one additive component of ``B_fiducial``.
    """

    from joulewise.adapters.powermetrics import (  # noqa: PLC0415
        anchor_records_from_powermetrics,
        parse_powermetrics_records,
    )
    from joulewise.uncertainty_evidence import (  # noqa: PLC0415
        CLOCK_METHOD_V2,
        CLOCK_METHOD_V3,
        derive_powermetrics_anchor_v2,
        derive_powermetrics_anchor_v3,
        stamp_from_mapping,
    )

    stamps = {
        name: stamp_from_mapping(row)
        for name, row in (anchor_block.get("clock_stamps") or {}).items()
        if isinstance(row, dict)
    }
    records = anchor_records_from_powermetrics(parse_powermetrics_records(raw))
    out: dict[str, Any] = {}
    for key, method, deriver in (
        ("v2", CLOCK_METHOD_V2, derive_powermetrics_anchor_v2),
        ("v3", CLOCK_METHOD_V3, derive_powermetrics_anchor_v3),
    ):
        derived = deriver(stamps=stamps, records=records)
        bound = derived.get("effective_clock_anchor_bound_s")
        out[key] = {
            "anchor_method": method,
            "status": derived.get("status"),
            "reason": derived.get("reason"),
            "detail": derived.get("detail"),
            "records_checked": derived.get("records_checked"),
            "native_rollover_count": derived.get("native_rollover_count"),
            "effective_clock_anchor_bound_s": bound,
            "effective_clock_anchor_bound_ms": (
                _ms(bound) if isinstance(bound, int | float) else None
            ),
        }
    return out


def _rederive_under(
    raw: bytes, events_raw: bytes, anchor_block: Any, method: str
) -> dict[str, Any]:
    """Re-derive one capture under one named anchor method.

    A refusal (any exception the calibration path raises) is captured and
    reported, never re-raised: the reviewer's question is partly *whether* the
    corrected anchor admits each capture, so a refusal is one of the answers.
    """

    from joulewise.powermetrics_fiducial import (  # noqa: PLC0415
        rederive_detection_from_artifacts,
    )

    try:
        detection = rederive_detection_from_artifacts(
            raw, events_raw, anchor_block, anchor_method=method
        )
    except Exception as exc:  # noqa: BLE001 - refusal is a reportable outcome
        return {
            "anchor_method": method,
            "status": "refused",
            "refusal_token": _refusal_token(exc),
            "refusal_detail": str(exc),
            "refusal_exception_type": type(exc).__name__,
            "b_fiducial_s": None,
        }
    reasons = sorted(str(reason) for reason in detection.reasons)
    admissible = bool(
        detection.all_pulses_detected
        and not reasons
        and detection.b_fiducial_s is not None
    )
    return {
        "anchor_method": method,
        "status": "derived",
        "admissible": admissible,
        "all_pulses_detected": bool(detection.all_pulses_detected),
        "pulse_fit_count": len(detection.fits),
        "reasons": reasons,
        "b_fiducial_s": detection.b_fiducial_s,
        "b_fiducial_ms": (
            _ms(detection.b_fiducial_s) if detection.b_fiducial_s is not None else None
        ),
        "projection_evaluated_cell_count": detection.projection_evaluated_cell_count,
    }


def _delta(new_s: Any, old_s: Any) -> dict[str, Any]:
    """Signed change from ``old_s`` to ``new_s``, in ms and percent of old."""

    if new_s is None or old_s is None:
        return {"available": False}
    difference = float(new_s) - float(old_s)
    row: dict[str, Any] = {
        "available": True,
        "absolute_ms": _ms(difference),
        "absolute_s_repr": repr(difference),
    }
    if old_s:
        row["relative_pct"] = round(100.0 * difference / float(old_s), PCT_DECIMALS)
    else:
        row["relative_pct"] = None
    return row


def analyse_capture(
    directory: Path, corpus_root: Path, v2_method: str, v3_method: str
) -> dict[str, Any]:
    """Everything this analysis records about one retained capture."""

    validation_id = directory.name
    row: dict[str, Any] = {"validation_id": validation_id}

    evidence_path = directory / "instrument_evidence.json"
    if not evidence_path.is_file():
        row["rederivable"] = False
        row["not_rederivable_reason"] = f"{evidence_path.name} is not present"
        return row
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    anchor_block = evidence.get("clock_anchor")
    stored_method = evidence.get("anchor_method_version")

    row["stored"] = {
        "b_fiducial_s": evidence.get("b_fiducial_s"),
        "b_fiducial_ms": (
            _ms(evidence["b_fiducial_s"])
            if isinstance(evidence.get("b_fiducial_s"), int | float)
            else None
        ),
        "anchor_method_version": stored_method,
        "anchor_generation": _classify_generation(stored_method, v2_method, v3_method),
        "clock_anchor_method": (
            anchor_block.get("method") if isinstance(anchor_block, dict) else None
        ),
        "clock_anchor_status": (
            anchor_block.get("status") if isinstance(anchor_block, dict) else None
        ),
        "clock_anchor_resolved": evidence.get("clock_anchor_resolved"),
        "evidence_status": evidence.get("status"),
        "all_pulses_detected": evidence.get("all_pulses_detected"),
        "reasons": sorted(str(reason) for reason in evidence.get("reasons") or []),
        "pulse_count": evidence.get("pulse_count"),
        "protocol_id": evidence.get("protocol_id"),
        "estimator_revision": (evidence.get("bindings") or {}).get(
            "estimator_revision"
        ),
        # Admissible as stamped: the capture-day pipeline marked it usable.
        "admissible": bool(
            evidence.get("status") == "valid"
            and evidence.get("clock_anchor_resolved")
            and evidence.get("all_pulses_detected")
            and not (evidence.get("reasons") or [])
        ),
    }

    hashes = evidence.get("artifact_sha256") or {}
    events_path = directory / "events.jsonl"
    if not events_path.is_file():
        row["rederivable"] = False
        row["not_rederivable_reason"] = "events.jsonl is not present"
        return row
    events_raw = events_path.read_bytes()
    events_sha256 = _sha256(events_raw)
    if events_sha256 != hashes.get("events.jsonl"):
        row["rederivable"] = False
        row["not_rederivable_reason"] = (
            "events.jsonl does not match its retained sha256 "
            f"(found {events_sha256}, evidence records {hashes.get('events.jsonl')!r})"
        )
        return row

    try:
        raw, raw_path = locate_raw_powermetrics(
            corpus_root, validation_id, hashes.get("raw/powermetrics.plist", "")
        )
    except FileNotFoundError as exc:
        row["rederivable"] = False
        row["not_rederivable_reason"] = str(exc)
        return row

    row["rederivable"] = True
    row["primary_bytes"] = {
        "events_jsonl_sha256": events_sha256,
        "raw_powermetrics_sha256": hashes.get("raw/powermetrics.plist"),
        "raw_powermetrics_path": raw_path,
        "raw_powermetrics_bytes": len(raw),
    }

    row["anchor_derivation"] = _derive_anchors(raw, anchor_block)
    v2 = _rederive_under(raw, events_raw, anchor_block, v2_method)
    v3 = _rederive_under(raw, events_raw, anchor_block, v3_method)
    row["rederived_v2"] = v2
    row["rederived_v3"] = v3

    stored_b = row["stored"]["b_fiducial_s"]
    # The control: does today's code, held at the v2 anchor, reproduce the value
    # written on capture day?  If yes, no detector drift confounds the delta.
    row["control_v2_reproduces_stored"] = (
        v2.get("b_fiducial_s") is not None
        and stored_b is not None
        and v2["b_fiducial_s"] == stored_b
    )
    row["delta_v3_vs_stored"] = _delta(v3.get("b_fiducial_s"), stored_b)
    row["delta_v3_vs_rederived_v2"] = _delta(
        v3.get("b_fiducial_s"), v2.get("b_fiducial_s")
    )

    stored_admissible = bool(row["stored"]["admissible"])
    v3_admissible = bool(v3.get("admissible", False))
    row["admissibility"] = {
        "stored_admissible": stored_admissible,
        "rederived_v2_admissible": bool(v2.get("admissible", False)),
        "rederived_v3_admissible": v3_admissible,
        "flipped": stored_admissible != v3_admissible,
        "flip_direction": (
            "none"
            if stored_admissible == v3_admissible
            else ("admitted_by_v3" if v3_admissible else "refused_by_v3")
        ),
    }
    return row


# ---------------------------------------------------------------------------
# Gate and summary.
# ---------------------------------------------------------------------------


def check_worked_capture_gate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Hard stop unless the worked capture's v3 bound equals the draft's value.

    The frozen draft prints one calibration bound.  If this script's v3 path
    cannot reproduce that exact binary64 value, the script is not re-deriving
    what the draft re-derived, and no other number it prints can be trusted.
    """

    for row in rows:
        if row["validation_id"] != WORKED_CAPTURE_ID:
            continue
        derived = (row.get("rederived_v3") or {}).get("b_fiducial_s")
        if derived != DRAFT_B_FIDUCIAL_S:
            raise CalibrationGateFailed(
                f"worked capture {WORKED_CAPTURE_ID}: v3 b_fiducial_s {derived!r} "
                f"!= frozen draft {DRAFT_B_FIDUCIAL_S!r}"
            )
        return {
            "capture_id": WORKED_CAPTURE_ID,
            "draft_b_fiducial_s": repr(DRAFT_B_FIDUCIAL_S),
            "rederived_v3_b_fiducial_s": repr(derived),
            "matches_exactly": True,
        }
    raise CalibrationGateFailed(
        f"worked capture {WORKED_CAPTURE_ID} is absent from the population"
    )


def summarise(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Population counts, the delta distribution, and the admissibility findings."""

    rederivable = [row for row in rows if row.get("rederivable")]
    delta_pct: list[float] = []
    delta_ms: list[float] = []
    for row in rederivable:
        delta = row.get("delta_v3_vs_stored") or {}
        if delta.get("available") and delta.get("relative_pct") is not None:
            delta_pct.append(float(delta["relative_pct"]))
            delta_ms.append(float(delta["absolute_ms"]))

    generations: dict[str, int] = {}
    for row in rows:
        generation = (row.get("stored") or {}).get("anchor_generation", "unknown")
        generations[generation] = generations.get(generation, 0) + 1

    refusals: dict[str, list[str]] = {}
    causes: dict[str, list[str]] = {}
    for row in rederivable:
        v3 = row.get("rederived_v3") or {}
        if v3.get("status") == "refused":
            refusals.setdefault(v3["refusal_token"], []).append(row["validation_id"])
            anchor_v3 = (row.get("anchor_derivation") or {}).get("v3") or {}
            cause = str(anchor_v3.get("detail") or anchor_v3.get("reason") or "unknown")
            causes.setdefault(cause, []).append(row["validation_id"])

    flips = [
        {
            "validation_id": row["validation_id"],
            "flip_direction": row["admissibility"]["flip_direction"],
            "stored_admissible": row["admissibility"]["stored_admissible"],
            "rederived_v3_admissible": row["admissibility"]["rederived_v3_admissible"],
        }
        for row in rederivable
        if row.get("admissibility", {}).get("flipped")
    ]

    control_failures = [
        row["validation_id"]
        for row in rederivable
        if not row.get("control_v2_reproduces_stored")
    ]

    return {
        "population_size": len(rows),
        "rederivable_count": len(rederivable),
        "not_rederivable": sorted(
            {
                row["validation_id"]: row.get("not_rederivable_reason", "")
                for row in rows
                if not row.get("rederivable")
            }.items()
        ),
        "stored_anchor_generation_counts": dict(sorted(generations.items())),
        "v3_derived_count": sum(
            1
            for row in rederivable
            if (row.get("rederived_v3") or {}).get("status") == "derived"
        ),
        "v3_refused_count": sum(
            1
            for row in rederivable
            if (row.get("rederived_v3") or {}).get("status") == "refused"
        ),
        "v3_refusals_by_token": {
            token: sorted(ids) for token, ids in sorted(refusals.items())
        },
        "v3_refusals_by_anchor_cause": {
            cause: sorted(ids) for cause, ids in sorted(causes.items())
        },
        "control_v2_reproduces_stored_count": sum(
            1 for row in rederivable if row.get("control_v2_reproduces_stored")
        ),
        "control_v2_reproduction_failures": sorted(control_failures),
        "delta_v3_vs_stored_relative": describe(delta_pct, PCT_DECIMALS, "pct"),
        "delta_v3_vs_stored_absolute": describe(delta_ms, MS_DECIMALS, "ms"),
        "admissibility_flips": flips,
        "admissibility_flip_count": len(flips),
        "stored_admissible_count": sum(
            1 for row in rows if (row.get("stored") or {}).get("admissible")
        ),
        "rederived_v3_admissible_count": sum(
            1
            for row in rederivable
            if row.get("admissibility", {}).get("rederived_v3_admissible")
        ),
    }


# ---------------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------------


def build_payload(repository_root: Path, corpus_root: Path) -> dict[str, Any]:
    sys.path.insert(0, str(repository_root))
    sys.dont_write_bytecode = True

    from joulewise.uncertainty_evidence import (  # noqa: PLC0415
        CLAIM_BEARING_ANCHOR_METHODS,
        CLOCK_METHOD_V2,
        CLOCK_METHOD_V3,
    )

    population_root = corpus_root / POPULATION_SUBDIRECTORY
    if not population_root.is_dir():
        raise PopulationUnavailable(f"{population_root} is not a directory")
    directories = sorted(
        path for path in population_root.iterdir() if path.is_dir()
    )
    if not directories:
        raise PopulationUnavailable(f"{population_root} holds no capture directories")

    rows = [
        analyse_capture(directory, corpus_root, CLOCK_METHOD_V2, CLOCK_METHOD_V3)
        for directory in directories
    ]
    gate = check_worked_capture_gate(rows)

    return {
        "analysis": "anchor-correction-quantified",
        "question": (
            "Over the retained diagnostic capture population, how far does the "
            "calibration bound B_fiducial move when it is re-derived under the "
            "corrected (v3) clock anchor instead of the v2 anchor that stamped "
            "it, and does any capture's admissibility flip?"
        ),
        "anchor_methods": {
            "v2_identity": CLOCK_METHOD_V2,
            "v3_identity": CLOCK_METHOD_V3,
            "claim_bearing": sorted(CLAIM_BEARING_ANCHOR_METHODS),
        },
        "standing": {
            "d078_energy_values_voided_for_claims": True,
            "note": (
                "Decision D-078 voids claim use of every powermetrics energy "
                "value collected before the time-anchor repair. This analysis "
                "does not un-void them; the population is used only as pilot "
                "evidence about the size and character of the anchor correction."
            ),
            "out_of_scope": (
                "Floor-level ratios (10.92 / 5.92 / 7.02) are not recomputed "
                "here. They depend on floor re-extraction, which is a separate "
                "piece of work; no approximation of them is offered."
            ),
        },
        "population_root": str(population_root),
        "worked_capture_gate": gate,
        "captures": rows,
        "summary": summarise(rows),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus-root",
        type=Path,
        default=Path("/Users/edr/code/JouleWise"),
        help="root holding runs/instrument_validation (the retained corpus)",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="checkout supplying the joulewise package used for re-derivation",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="path to write the JSON result to",
    )
    args = parser.parse_args(argv)

    payload = build_payload(
        args.repository_root.resolve(), args.corpus_root.resolve()
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary = payload["summary"]
    print(f"wrote {args.out}")
    print(
        f"population {summary['population_size']}, "
        f"re-derivable {summary['rederivable_count']}, "
        f"v3 derived {summary['v3_derived_count']}, "
        f"v3 refused {summary['v3_refused_count']}, "
        f"admissibility flips {summary['admissibility_flip_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
