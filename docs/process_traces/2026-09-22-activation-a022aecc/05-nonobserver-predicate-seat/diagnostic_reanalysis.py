#!/usr/bin/env python3
"""DIAGNOSTIC ONLY — registration v3's non-observer rule over two archived nights.

Cold gate QPE01-DAEMON-CONTAMINATION-01 ruling 10 §4 (Q3(a)) authorises the v3
per-envelope rule to be run after the fact over night 20260922-2100, and
REQUIRES this script to state its observer set explicitly, because no row in
either archived journal carries ``observer: true``: the recorder ran without
the chain root pid, so `sample_interval` marked only the recorder's own
descendants and the power sampler -- a sibling -- read as part of the machine.
Registration v3 replaces this basename assumption with pid ancestry.

The join is the RULING's (§1): rows whose observation begins inside
[scheduled, scheduled + envelope_s), which is what reproduces the judge's
recomputed integrals exactly.  The production rule in `pilot_summary` uses the
registration's own support join (intervals fully inside the envelope), which
is stricter by one row per envelope; both give the same twelve exclusions.

This output is not a registered result and sizes nothing.

Usage: diagnostic_reanalysis.py [ARCHIVE_ROOT]   (default ~/night-archive)
"""

import json
import os
import sys
from pathlib import Path

BAR_CORE_SECONDS = 30  # registration v3 `non_observer_process_busy.bar_core_seconds`
ENVELOPE_S = 600
# The assumption registration v3 replaces with pid ancestry (ruling 10 §4).
OBSERVER_BASENAMES = {"powermetrics", "Python", "top", "sudo", "ps", "pgrep", "sysctl"}
LABEL = ("DIAGNOSTIC ONLY — registration v3 rule applied after the fact to night "
         "20260922-2100 under an explicit observer basename set; not a registered "
         "result, sizes nothing.")
NIGHTS = ("qpe01-pilot-n1-20260922-2100-harvest-20260922",
          "qpe01-pilot-n1-20260922-0217-harvest-20260922")


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def analyse(night):
    rows = read_jsonl(night / "evidence_busy_cores.jsonl")
    envelopes = read_jsonl(night / "evidence_envelopes.jsonl")
    marked = sum(1 for row in rows if row.get("observation")
                 for consumer in row["observation"]["metrics"]["top_consumers"]
                 if consumer["observer"])
    result = {"rows": len(rows), "rows_carrying_observer_true": marked, "envelopes": []}
    for envelope in envelopes:
        scheduled = envelope["scheduled_mono_s"]
        support = [row for row in rows if row.get("observation")
                   and scheduled <= row["observation"]["monotonic_start"] < scheduled + ENVELOPE_S]
        totals, names = {}, {}
        for row in support:
            observation = row["observation"]
            for consumer in observation["metrics"]["top_consumers"]:
                basename = os.path.basename(consumer["command"])
                if consumer["observer"] or basename in OBSERVER_BASENAMES:
                    continue
                identity = (consumer["pid"], consumer["start_identity"])
                totals[identity] = (totals.get(identity, 0.)
                                    + consumer["busy_cores"] * observation["interval_s"])
                names[identity] = basename
        hits = sorted(((total, identity) for identity, total in totals.items()
                       if total >= BAR_CORE_SECONDS), reverse=True)
        result["envelopes"].append({
            "index": envelope["index"], "support_rows": len(support),
            "largest_non_observer_core_seconds": round(max(totals.values(), default=0.), 1),
            "excluded": [{"process": names[identity], "pid": identity[0],
                          "core_seconds": round(total, 1)} for total, identity in hits]})
    result["excluded_envelopes"] = sum(1 for e in result["envelopes"] if e["excluded"])
    return result


def main(argv):
    root = Path(argv[1] if len(argv) > 1 else Path.home() / "night-archive")
    report = {"label": LABEL, "bar_core_seconds": BAR_CORE_SECONDS,
              "observer_basenames": sorted(OBSERVER_BASENAMES),
              "join": "observation.monotonic_start in [scheduled, scheduled + 600)",
              "nights": {}}
    for name in NIGHTS:
        night = root / name / "night"
        if not night.is_dir():
            report["nights"][name] = {"error": f"not present: {night}"}
            continue
        report["nights"][name] = analyse(night)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
