#!/usr/bin/env python3
"""Run the block-6 analysis (registration B6-REPL §9 to §13).

From the root of a clean checkout at the pinned analysis commit (S-14):

    python3.13 -B scripts/b6_analyze.py analyse --mode blind-dry-run --loop-root <loop root> \
        --session-index <block-6 session index> --block5-custody <block-5 release custody> --custody <custody root>
    python3.13 -B scripts/b6_analyze.py analyse --mode session --session <session id> ... --custody <custody root>
    python3.13 -B scripts/b6_analyze.py analyse --mode release ... --custody <the dry run's custody root>

--loop-root     The block-6 session loop root.  Counting is read from its attempts.jsonl and
                state.json (the loop's acceptance), never from a harvest's exclusions.json.
--custody       A directory outside the repository, with no symbolic link and no whitespace in
                its path.  Each mode writes one subdirectory (dry-run/, session/ or release/) and
                refuses to start when it exists.  Every number goes under <subdirectory>/restricted/;
                the record <subdirectory>/B6-ANALYSIS-RECORD.json holds structure only.
--workers N     Floor sessions run in parallel in N processes (default 1, serial).  The outputs
                are the same bytes for every N.

What it prints: on standard error one line per analysed session, "node <kind>:<pack>:<session>
<status>"; on standard output the record's path and SHA-256.  Exit 0: complete; 3: complete with a
registered outcome-class stop; 2: a tooling refusal or anything else.

The slot subcommands write restricted outputs for automation and print only their path and digest:

    python3.13 -B scripts/b6_analyze.py slots --smoke-rows <rows.json> --out <file outside the repository>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.b6.analysis import driver, slots  # noqa: E402
from joulewise.b6.analysis.adapter import L9ProgramAdapter  # noqa: E402
from joulewise.b6.analysis.public import canonical, sha256  # noqa: E402


def _slots(args) -> int:
    out = Path(args.out).absolute()
    if out.is_relative_to(ROOT) or out.exists():
        print("slots - tooling_refusal", file=sys.stderr)
        return 2
    try:
        rows = json.loads(Path(args.smoke_rows).read_bytes())
        lengths = slots.s11_phase_lengths(rows)
        raw = canonical({"schema_version": "joulewise.b6_slot_values.v1",
                         "S-11": lengths, "S-9": slots.s9_power_lines(lengths)})
    except (OSError, ValueError, TypeError, AttributeError, slots.SlotRefusal):
        print("slots - tooling_refusal", file=sys.stderr)
        return 2
    with out.open("xb") as stream:
        stream.write(raw)
    print(f"{out} {sha256(raw)}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("analyse")
    run.add_argument("--mode", choices=driver.MODES, required=True)
    run.add_argument("--loop-root", required=True)
    run.add_argument("--custody", required=True)
    run.add_argument("--session-index")
    run.add_argument("--block5-custody")
    run.add_argument("--session")
    run.add_argument("--workers", type=int, default=1)
    slot = commands.add_parser("slots")
    slot.add_argument("--smoke-rows", required=True)
    slot.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if args.command == "slots":
        return _slots(args)
    adapter = L9ProgramAdapter(Path(args.session_index) if args.session_index else None,
                               Path(args.block5_custody) if args.block5_custody else None)
    return driver.analyse(Path(args.loop_root), Path(args.custody), adapter, mode=args.mode,
                          workers=args.workers, only=args.session)


if __name__ == "__main__":
    sys.exit(main())
