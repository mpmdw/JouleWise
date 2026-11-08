"""Synthetic-only timing experiment, no capture/data/file reads or writes.

python3.13 -B -m tests.align.benchmark_window_timing --members 22 --repeats 5

The scan baseline is a deliberately simple accounting implementation, NOT a
previous production pipeline. Compare complete report/worksheet bytes before
timing. No pre-existing capture/analysis pipeline is modified by this feature.
"""
import argparse
import hashlib
import json
import platform
from statistics import median
from time import perf_counter
from unittest.mock import patch

from joulewise.align import window_timing as timing
from tests.align.window_timing_synthetic import campaign


def scan_partition(start_ns, end_ns, intervals):
    """Independent O(edges * intervals) scan oracle, with all provenance."""
    edges = {start_ns, end_ns}
    for span in intervals:
        if max(start_ns, span.start_ns) < min(end_ns, span.end_ns):
            edges.update((max(start_ns, span.start_ns), min(end_ns, span.end_ns)))
    points = sorted(edges)
    result = []
    for a, b in zip(points, points[1:]):
        active = [span for span in intervals if span.start_ns <= a and span.end_ns >= b]
        top_priority = max((span.priority for span in active), default=-1)
        candidates = {(span.phase, span.member, span.activity or span.phase)
                      for span in active if span.priority == top_priority}
        if len(candidates) == 1:
            phase, member, activity = candidates.pop()
            ambiguous = False
            if any(span.phase == "references" for span in active):
                phase = "references"
        else:
            phase, member, activity = "unattributed", None, "unattributed"
            ambiguous = len(candidates) > 1
        row = dict(start_ns=a, end_ns=b, phase=phase, member=member, activity=activity,
                   ambiguous=ambiguous, sources=sorted({span.source for span in active}))
        if result and all(result[-1][key] == value for key, value in row.items() if key not in ("start_ns", "end_ns")):
            result[-1]["end_ns"] = b
        else:
            result.append(row)
    return result


def compare(members=22, repeats=5):
    docs, opts = campaign(members)
    sweep = timing.partition
    def run(partitioner):
        with patch.object(timing, "partition", partitioner):
            return timing.read_window(docs.__getitem__, **opts)
    before, after = run(scan_partition), run(sweep)
    dump = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    old_bytes, new_bytes = dump(before), dump(after)
    if old_bytes != new_bytes or timing.worksheet(before) != timing.worksheet(after):
        raise AssertionError("scan/sweep complete output inequality")
    samples = {"scan_before_s": [], "sweep_after_s": []}
    for _ in range(repeats):
        for key, partitioner in (("scan_before_s", scan_partition), ("sweep_after_s", sweep)):
            start = perf_counter()
            run(partitioner)
            samples[key].append(perf_counter()-start)
    start = perf_counter()
    dump(after)
    json_s = perf_counter()-start
    start = perf_counter()
    timing.worksheet(after)
    worksheet_s = perf_counter()-start
    return dict(python=platform.python_version(), members=members, input_files=len(docs),
                input_bytes=sum(map(len, docs.values())), ledger_rows=len(after["ledger"]),
                repeats=repeats, exact_report_and_worksheet_equality=True,
                report_sha256=hashlib.sha256(new_bytes).hexdigest(), samples=samples,
                medians={key: median(values) for key, values in samples.items()},
                json_render_s=json_s, worksheet_render_s=worksheet_s)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--members", type=int, default=22)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    if not 1 <= args.members <= 1000 or not 1 <= args.repeats <= 20:
        parser.error("members must be 1..1000; repeats 1..20")
    print(json.dumps(compare(args.members, args.repeats), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
