#!/usr/bin/env python3
"""Extract A267 replay fixtures from the READ-ONLY pilot-night harvest archive.

Cold-gate ruling 10 Q4 / rebuttal 14 R3: the regressions replay the archived
clock stamps and native records of every envelope of
``qpe01-pilot-n1-20260922-0217`` under both anchor methods, and assert the
default method reproduces the recorded ``power.anchor`` dict exactly.  This
script is the reproducible bridge from the archive to the checked-in fixtures;
it only reads the archive and only writes this directory.

Usage (about 80 s; the twelve plists are ~1.5 GB in total):

    env PYTHONDONTWRITEBYTECODE=1 python3 -B \
        tests/fixtures/qpe01_pilot_n1_20260922/extract_fixtures.py

Each ``envelope-NN.json`` carries:
  clock_stamps    ``power.anchor.clock_stamps`` verbatim from session.json
  recorded_anchor ``power.anchor`` verbatim (the night's own derived record)
  records         ``[elapsed_ns, native_timestamp_ns, rail_sum_w, energy_j,
                  is_delta]`` per native frame, in capture order
  interior        the collector's own interior-reduction inputs (start stamp,
                  start drift, ``--interior-offset-s``/``--interior-s``), so a
                  regression can rebuild the exact interior window
The float fields ``elapsed_s``/``native_timestamp_s`` are NOT stored: they are
``elapsed_ns / 1e9`` and ``native_timestamp_ns / 1e9`` exactly (native labels
are whole seconds), which ``load_records`` reproduces.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ARCHIVE = Path(
    "/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922"
)
EVIDENCE = ARCHIVE / "night/evidence"
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
ENVELOPES = range(1, 13)


def argument(argv, flag):
    return argv[argv.index(flag) + 1] if flag in argv else None


def extract(index):
    sys.path.insert(0, str(REPO_ROOT))
    from scripts import sample_quiet_predicate_evidence as harness

    out = EVIDENCE / f"envelope-{index:02d}"
    session_bytes = (out / "session.json").read_bytes()
    session = json.loads(session_bytes)
    anchor = session["power"]["anchor"]
    plist = out / "raw" / f"powermetrics-idle-{index}.plist"
    frames, dropped = harness.parse_frames(plist.read_bytes())
    if dropped is not None:
        raise ValueError(f"envelope {index}: truncated recorder tail {dropped}")
    records = [
        [
            frame["elapsed_ns"],
            frame["native_timestamp_ns"],
            frame["power"]["rail_sum_w"],
            frame["energy_j"],
            frame["is_delta"],
        ]
        for frame in frames
    ]
    argv = session["argv"]
    fixture = {
        "envelope": index,
        "clock_stamps": anchor["clock_stamps"],
        "recorded_anchor": anchor,
        "interior": {
            "start_stamp": session["start_stamp"],
            "start_drift_s": session["start_drift_s"],
            "interior_offset_s": float(argument(argv, "--interior-offset-s")),
            "interior_s": float(argument(argv, "--interior-s")),
        },
        "records": records,
    }
    (HERE / f"envelope-{index:02d}.json").write_text(
        json.dumps(fixture, sort_keys=True, allow_nan=False) + "\n"
    )
    return {
        "envelope": index,
        "records": len(records),
        "session_sha256": hashlib.sha256(session_bytes).hexdigest(),
        "plist_sha256": hashlib.sha256(plist.read_bytes()).hexdigest(),
        "anchor_status": anchor["status"],
        "anchor_detail": anchor.get("detail", anchor["status"]),
    }


def main():
    rows = [extract(index) for index in ENVELOPES]
    lines = [
        "# Fixture sources — qpe01-pilot-n1-20260922-0217 (READ-ONLY archive)",
        "",
        f"Archive root: `{ARCHIVE}`",
        "",
        "Extracted by `extract_fixtures.py` in this directory.  The archive was",
        "verified byte-exact against the live custody root by the harvesting",
        "activation (`SHA256SUMS-check-against-live-root.txt`, 15801 OK); the",
        "session digests below match exhibit C1 of the cold-gate packet",
        "(`docs/process_traces/2026-09-22-activation-d9990b3c/"
        "01-coldgate-packet-a267-clock-discipline-anchor/"
        "exhibit-C-executed-evidence.md`).",
        "",
        "| envelope | records | recorded anchor | session.json sha256 | "
        "powermetrics plist sha256 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['envelope']:02d} | {row['records']} | "
            f"{row['anchor_detail']} | `{row['session_sha256']}` | "
            f"`{row['plist_sha256']}` |"
        )
    lines += [
        "",
        "`exhibit-D-timed-log.txt` is a verbatim copy of the packet's",
        "`exhibit-D-timed-log-0210-0435.txt` (191 lines, sha256",
        "`70218c4a41b0ee87e20f032790e442451f36d713df49933ccbaba907395797b6`),",
        "used by the timed-log attestation scanner regression.",
        "",
    ]
    (HERE / "SOURCES.md").write_text("\n".join(lines))
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
