#!/usr/bin/env python3
"""Run the block-6 analysis (registration B6-REPL §9 to §13; design §14).

From the root of a clean checkout at the pinned analysis commit (S-14), on the
analysis host, never with an agent session alive there:

    python3.13 -B scripts/b6_analyze.py index --loop-root <loop root> --measurement <measurement checkout> \
        --out <index file outside the repository>
    python3.13 -B scripts/b6_analyze.py analyse --mode per-session --run 1 --loop-root <loop root> \
        --index <index file> --custody <custody root>
    ... --mode per-session --run 2 ...                                (same host, after run 1; must match it)
    ... --mode cross-block --run 1 --block5-release-record <B5-RELEASE-RECORD.json> --block5-custody <dir> ...
    ... --mode cross-block --run 2 ...                                (must match cross-block run 1)
    ... --mode session --session <session id> ...                     (one newly harvested session, §12.2)

--custody     A directory outside the repository, with no symbolic link and no whitespace in its path.
              Each run writes one subdirectory (per-session-1, per-session-2, cross-block-1, cross-block-2,
              session-<id>) and refuses to start when it exists.  Every number goes under
              <subdirectory>/restricted/; <subdirectory>/B6-BLIND-DRY-RUN-RECORD.json holds structure only.
--workers N   Units run in parallel in N processes (default 1, serial).  Outputs are the same bytes for every N.

Each session's desk-compressed bytes are restored before its first unit and compressed again after its last,
once per run.  With JW_B5_SYNTHETIC_ONLY=1 every root must lie under $TMPDIR.

What it prints: on standard error one line per unit, "node <kind>:<pack>:<session> <status>"; on standard
output the record's path and SHA-256.  Exit 0: complete; 3: complete with a registered outcome-class stop;
2: a tooling refusal or anything else.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from joulewise.b6.analysis import driver, session_index  # noqa: E402
from joulewise.b6.analysis.adapter import L9ProgramAdapter  # noqa: E402
from joulewise.b6.analysis.public import canonical, sha256  # noqa: E402


def _index(args) -> int:
    out = Path(args.out).absolute()
    try:
        driver.require_synthetic_roots([args.loop_root, args.measurement, out])
        if out.is_relative_to(ROOT) or out.exists():
            raise driver.DriverRefusal("index_output_invalid")
        raw = canonical(session_index.build_session_index(
            Path(args.loop_root), measurement=Path(args.measurement),
            block_root=Path(args.block_root) if args.block_root else None))
    except (session_index.IndexRefusal, driver.census_module.CensusRefusal, driver.DriverRefusal) as exc:
        print(f"index - tooling_refusal {exc.code}", file=sys.stderr)
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
    run.add_argument("--run", type=int, choices=(1, 2), default=1)
    run.add_argument("--loop-root", required=True)
    run.add_argument("--index", required=True)
    run.add_argument("--custody", required=True)
    run.add_argument("--block5-release-record")
    run.add_argument("--block5-custody")
    run.add_argument("--session")
    run.add_argument("--workers", type=int, default=1)
    index = commands.add_parser("index")
    index.add_argument("--loop-root", required=True)
    index.add_argument("--measurement", required=True)
    index.add_argument("--block-root")
    index.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if args.command == "index":
        return _index(args)
    adapter = L9ProgramAdapter(Path(args.index), Path(args.block5_custody) if args.block5_custody else None)
    return driver.analyse(Path(args.loop_root), Path(args.index), Path(args.custody), adapter, mode=args.mode,
                          run=args.run, only=args.session, workers=args.workers,
                          block5_release_record=Path(args.block5_release_record) if args.block5_release_record else None)


if __name__ == "__main__":
    sys.exit(main())
