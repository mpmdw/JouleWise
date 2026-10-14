#!/usr/bin/env python3
"""Run the pinned block-5 analysis with restricted output custody.

/opt/homebrew/bin/python3.13 -B scripts/run_b5_analysis.py --mode blind-dry-run --index <window index> --custody <custody root>
/opt/homebrew/bin/python3.13 -B scripts/run_b5_analysis.py --mode release       --index <window index> --custody <the same custody root>

--mode chooses the before-release commitment or its after-release replay.
--index names the authenticated window index (every attempt and source root).
--custody names an existing or creatable directory outside the repository,
without symbolic links or whitespace (the commitment line uses one path token).
All child outputs and logs remain in restricted/.
A repeat after a blind tooling repair requires a new custody root: existing
mode directories are never overwritten. Release needs a completed dry record.
No other scientific input or private synthetic seam is a command-line option.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from joulewise.b5_analysis.dry_run import run
from joulewise.b5_analysis.windows import AnalysisRefusal


class _Parser(argparse.ArgumentParser):
    def error(self,message):
        raise AnalysisRefusal('analysis_arguments_invalid')


def main(argv=None):
    parser=_Parser(description=__doc__,add_help=False)
    parser.add_argument('--mode',choices=('blind-dry-run','release'),required=True)
    parser.add_argument('--index',type=Path,required=True)
    parser.add_argument('--custody',type=Path,required=True)
    try:
        args=parser.parse_args(argv)
    except AnalysisRefusal:
        print('step 0 - tooling_refusal',file=sys.stderr)
        return 2
    return run(args.mode,args.index,args.custody)


if __name__=='__main__':raise SystemExit(main())
