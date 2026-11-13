#!/usr/bin/env python3
"""Weekly pipeline-time report (RL-127 term 9), each Monday.

    pipeline_time_report.py [--days 7] [--end ISO] [--out PATH | --no-write]

Summarises the timing ledger, CI run durations (`gh run list`), merged-PR
cycle times (`gh pr list`) and MBP utilisation estimated from origin/main
RUN_STATE item stamps, against the RL-127 budgets. Writes Markdown to
docs/run_reports/<end date>-pipeline-time.md (or --out) and prints a short
summary. Reads structure only: no measurement, custody or result file.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.pipeline_time import alarms, ledger, report, runstate, sources  # noqa: E402

REPO = Path(__file__).resolve().parents[1]


def gh_json(runner, argv):
    rc, out, _ = runner(argv, timeout=120)
    if rc != 0:
        return None
    try:
        return json.loads(out)
    except ValueError:
        return None


def gather(args, runner=alarms.default_runner) -> report.Inputs:
    end = runstate.parse_time(args.end) if args.end else time.time()
    if end is None:
        raise SystemExit("--end must be ISO 8601 with an offset")
    start = end - args.days * 86400
    text = None
    if args.run_state:
        text = Path(args.run_state).read_text()
    else:
        rc, _, _ = runner(["git", "-C", str(REPO), "fetch", "--quiet", "--no-tags", "origin",
                           f"+refs/heads/main:{sources.PRIVATE_REF}"], timeout=120)
        rc, out, _ = runner(["git", "-C", str(REPO), "show", f"{sources.PRIVATE_REF}:RUN_STATE.md"], timeout=60)
        text = out if rc == 0 else None
    runs = gh_json(runner, ["gh", "run", "list", "--repo", args.repo, "--limit", str(args.run_limit), "--json",
                            "databaseId,workflowName,event,headBranch,headSha,status,conclusion,createdAt,"
                            "startedAt,updatedAt,attempt"])
    prs = gh_json(runner, ["gh", "pr", "list", "--repo", args.repo, "--state", "merged", "--limit", "300",
                           "--json", "number,createdAt,mergedAt,title"])
    state_only = {}
    for run in runs or []:
        if run.get("workflowName") == "ci" and run.get("event") == "push" and run.get("headSha"):
            state_only.setdefault(run["headSha"], sources.state_only_commit(REPO, run["headSha"], runner))
    return report.Inputs(start=start, end=end, ledger_rows=ledger.read_ledger(args.ledger), ci_runs=runs, prs=prs,
                         run_state=runstate.read(text) if text else None, state_only=state_only)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--days", type=float, default=7)
    parser.add_argument("--end", help="window end, ISO 8601 with offset (default now)")
    parser.add_argument("--repo", default="mpmdw/JouleWise")
    parser.add_argument("--ledger", help="ledger path (default /Volumes/JW-EXT/ledger/timing.jsonl)")
    parser.add_argument("--run-state", help="read this RUN_STATE file instead of origin/main")
    parser.add_argument("--run-limit", type=int, default=1000)
    parser.add_argument("--out")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    inputs = gather(args)
    markdown, summary = report.build(inputs)
    if not args.no_write:
        out = Path(args.out) if args.out else REPO / "docs/run_reports" / (
            time.strftime("%Y-%m-%d", time.localtime(inputs.end)) + "-pipeline-time.md")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(markdown)
        summary.append(f"written: {out}")
    print("\n".join(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
