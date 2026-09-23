#!/usr/bin/env python3
"""Exhibit E generator — per-slot rows of a bench replay, read from the raw JSON.

Usage:
    python3 exhibit-E-generator.py <bench-replay.json> [--sidecars]

Prints a per-slot table, the two maxima, and the driver's own verdict status and
statement VERBATIM.  Reads nothing but the JSON given to it.

`first_write_delay_s` lives in the feeder's sidecar, not in the bench JSON: the
bench script carries only four sidecar fields into each row
(`bench_replay_start_drift.py:282-285`).  Reading it therefore means opening
files under the run's custody root.  That is OFF by default (`n/a (--sidecars
off)`) so this generator can be run while a replay is in flight without
touching the custody tree; pass `--sidecars` once the run has ended.  With the
flag, the sidecar path is taken from each envelope's
`session.json -> replay.sidecar` (the same field the bench script reads).

The `archived_v3.1_class` / `fidelity` pair compares each slot's replayed
anchor CLASS (bounded vs anything else) against the archived night's own v3.1
projection for that envelope, which is a constant in this file (see
`ARCHIVED_V31_CLASS`).  It is a fidelity measure, not a pass/fail: the archived
night itself left five envelopes unresolved, so a faithful replay is expected
to leave the same five unresolved.

No judgement is made here.  Admissibility fields are printed as recorded; the
verdict block is the driver's, quoted, not recomputed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load(path: Path):
    with path.open() as handle:
        return json.load(handle)


def fmt(value, spec="{:.3f}"):
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, float):
        return spec.format(value)
    return str(value)


def sidecar_first_write_delay(report, index: int):
    """Return (value, note) for slot `index`'s feeder first_write_delay_s."""
    night = report.get("night_dir")
    if not night:
        return None, "no night_dir in the JSON"
    session_path = Path(night) / "evidence" / f"envelope-{index:02d}" / "session.json"
    try:
        session = load(session_path)
    except (OSError, ValueError) as exc:
        return None, f"{session_path}: {exc.__class__.__name__}"
    replay = (session.get("replay") or {})
    sidecar_path = replay.get("sidecar")
    if not sidecar_path:
        return None, f"{session_path}: no replay.sidecar"
    try:
        sidecar = load(Path(sidecar_path))
    except (OSError, ValueError) as exc:
        return None, f"{sidecar_path}: {exc.__class__.__name__}"
    return sidecar.get("first_write_delay_s"), ""


# The archived night's own v3.1 forward projection over its twelve envelopes,
# executed at 447fd6bf and recorded at
# docs/process_traces/2026-09-22-activation-e4b4ead6/01-launch-and-resume-record.md:29
# (step 10): bounded {02, 05, 06, 08, 09, 11, 12}; 01/03/04/10
# `affine_clock_fit_empty` (a real slew inside the capture); 07 the 15 ms
# backstop.  A FAITHFUL replay of that archive reproduces these CLASSES -- the
# five unresolved envelopes carry real clock behaviour of the archived night,
# not a replay artefact, and a replay that resolved them would be the
# suspicious one.  The detail string may legitimately differ (the replay's
# clock relation is the archived labels against live pacing), so only the
# two-way class is compared.  The mapping is a constant here, never read from
# the run, so the fidelity column cannot be bent by the run it judges.
ARCHIVED_V31_CLASS = {
    1: "unresolved", 2: "bounded", 3: "unresolved", 4: "unresolved",
    5: "bounded", 6: "bounded", 7: "unresolved", 8: "bounded",
    9: "bounded", 10: "unresolved", 11: "bounded", 12: "bounded",
}


def replay_class(anchor_status):
    """Collapse a replay row's anchor_status to the two archived classes."""
    if anchor_status is None:
        return "-"
    return "bounded" if anchor_status == "bounded" else "unresolved"


COLUMNS = [
    ("idx", 3), ("scheduled_mono_s", 16), ("actual_mono_s", 16),
    ("chain_drift_s", 13), ("sess_drift_s", 12), ("exit", 4),
    ("cleanup", 7), ("attest_state", 14), ("attest_wall_s", 13),
    ("anchor", 9), ("anchor_detail", 34), ("interior", 8),
    ("archived_v3.1_class", 19), ("fidelity", 9), ("first_write_delay_s", 19),
]


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    path = Path(argv[0])
    want_sidecars = "--sidecars" in argv[1:]
    report = load(path)

    print(f"source              {path}")
    print(f"schema              {report.get('schema')}")
    print(f"kind                {report.get('kind')}   label_shift {report.get('label_shift')}")
    print(f"head                {report.get('head')}  (expect {report.get('expect_sha')}, "
          f"clean_tree {report.get('clean_tree')})")
    print(f"transaction_merge   {report.get('transaction_merge')} "
          f"(is_ancestor {report.get('transaction_merge_is_ancestor')})")
    print(f"archive             {report.get('archive')}")
    print(f"bench_script_sha256 {report.get('bench_script_sha256')}")
    print(f"feeder_sha256       {report.get('feeder_sha256')}")
    print(f"registration_sha256 {report.get('registration_sha256')}")
    print(f"chain_source_sha256 {report.get('chain_source_sha256')}")
    print(f"custody_root        {report.get('custody_root')}")
    print(f"outcome             {report.get('outcome')}  rc {report.get('returncode')}  "
          f"summary_status {report.get('summary_status')}")
    if report.get("outcome_error"):
        print(f"outcome_error       {report['outcome_error']}")
    print(f"machine_start       {(report.get('machine_start') or {}).get('uptime')}")
    print(f"machine_end         {(report.get('machine_end') or {}).get('uptime')}")
    print(f"argv                {' '.join(report.get('bench_argv') or [])}")
    print()

    rows = report.get("slots") or []
    header = "  ".join(name.ljust(width) for name, width in COLUMNS)
    print(header)
    print("-" * len(header))
    notes = []
    for row in rows:
        index = row.get("index")
        if want_sidecars:
            delay, note = sidecar_first_write_delay(report, index)
            if note:
                notes.append(f"slot {index}: first_write_delay_s unavailable — {note}")
            delay_text = fmt(delay)
        else:
            delay_text = "n/a (--sidecars off)"
        archived = ARCHIVED_V31_CLASS.get(index, "-")
        observed = replay_class(row.get("anchor_status"))
        cells = [
            fmt(index), fmt(row.get("scheduled_mono_s"), "{:.6f}"),
            fmt(row.get("actual_mono_s"), "{:.6f}"),
            fmt(row.get("chain_start_drift_s")), fmt(row.get("session_start_drift_s")),
            fmt(row.get("collector_exit")), fmt(row.get("cleanup_proven")),
            fmt(row.get("attestation_state")), fmt(row.get("network_time_attestation_wall_s")),
            fmt(row.get("anchor_status")), fmt(row.get("anchor_detail")),
            fmt(row.get("interior_complete_support")),
            archived, "MATCH" if observed == archived else "MISMATCH",
            delay_text,
        ]
        print("  ".join(cell.ljust(width) for cell, (_, width) in zip(cells, COLUMNS)))
    for note in notes:
        print(f"  ! {note}")
    print()

    chain = [r["chain_start_drift_s"] for r in rows if r.get("chain_start_drift_s") is not None]
    session = [r["session_start_drift_s"] for r in rows if r.get("session_start_drift_s") is not None]
    print(f"slots recorded          {len(rows)} of {(report.get('protocol') or {}).get('envelopes')}")
    print(f"max chain start_drift   {fmt(max(chain)) if chain else '-'} s   "
          f"(bar 0.5 s; over the bar: {[r['index'] for r in rows if (r.get('chain_start_drift_s') or 0) > 0.5]})")
    print(f"max session start_drift {fmt(max(session)) if session else '-'} s   "
          f"(over 0.5 s: {[r['index'] for r in rows if (r.get('session_start_drift_s') or 0) > 0.5]})")
    print(f"tail_s per slot         {[fmt(r.get('tail_s')) for r in rows]}")
    mismatches = [r["index"] for r in rows
                  if replay_class(r.get("anchor_status")) != ARCHIVED_V31_CLASS.get(r["index"])]
    print(f"anchor-class fidelity   {len(rows) - len(mismatches)}/{len(rows)} recorded slots "
          f"match the archived v3.1 class; mismatched slots: {mismatches}")
    print("  (archived v3.1 class, constant in this generator: bounded "
          "{02,05,06,08,09,11,12}; unresolved {01,03,04,07,10})")
    print()

    verdict = report.get("verdict") or {}
    print("DRIVER VERDICT (verbatim, recomputed by nobody):")
    print(f"  status                            {verdict.get('status')}")
    print(f"  statement                         {verdict.get('statement')}")
    print(f"  max_chain_start_drift_s           {verdict.get('max_chain_start_drift_s')}")
    print(f"  max_session_start_drift_s         {verdict.get('max_session_start_drift_s')}")
    print(f"  slots_over_bar                    {verdict.get('slots_over_bar')}")
    print(f"  session_bar_exceeded              {verdict.get('session_bar_exceeded')}")
    print(f"  session_slots_over_bar            {verdict.get('session_slots_over_bar')}")
    print(f"  escalate_chain_pass_session_fail  {verdict.get('escalate_chain_pass_session_fail')}")
    print(f"  smoke_exempt_fields               {verdict.get('smoke_exempt_fields')}")
    print("  slot_defects:")
    for defect in verdict.get("slot_defects") or []:
        print(f"    slot {defect.get('index')}  {defect.get('field')} = "
              f"{defect.get('value')!r}  (required {defect.get('required')!r})")
    if not (verdict.get("slot_defects") or []):
        print("    (none)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
