#!/usr/bin/env python3
"""Run the block-5 analysis: once blind before the release event, once after it.

The two commands, run from the root of a clean checkout at the pinned analysis commit:

    /opt/homebrew/bin/python3.13 -B scripts/run_b5_analysis.py --mode blind-dry-run --index configs/analysis/b5/analysed_windows.json --custody <custody root>
    /opt/homebrew/bin/python3.13 -B scripts/run_b5_analysis.py --mode release --index configs/analysis/b5/analysed_windows.json --custody <the same custody root>

The arguments, each the only thing of its kind the run takes:

--mode blind-dry-run   Runs steps 0 to 11 of the sealed analysis plan (section 3.1, in the order
                       0, 1, 2, 3, 3b, 4, 5, 8, 6, 9, 9b, 10, 11) on the real windows before the
                       release event. Every output of every step is written under
                       <custody root>/dry-run/restricted/; the only file written outside it is the
                       record <custody root>/dry-run/B5-BLIND-DRY-RUN-RECORD.json, which holds step
                       names, status words, exit statuses, kept-unit counts, digests, paths and
                       tooling refusal codes, and no number of any measurement.
--mode release         After the release event: runs the same steps again from the same bytes into
                       <custody root>/release/ and compares every input digest and every output
                       digest with the dry run's record. Any difference stops the run with
                       release_digest_differs_from_dry_run. It refuses to start unless the dry-run
                       record exists in the same custody root and says the dry run completed with
                       no tooling refusal.
--index PATH           The window index: the tracked file naming every attempt of block 5 with its
                       harvest archive and runs roots. Everything else a step reads (archives,
                       runs roots, ledger copies, sealed pack files, the project commit) is derived
                       from this file, the archives it names and the checkout; nothing else is a
                       command-line argument.
--custody DIR          The analysis custody root: a directory outside the repository, given as a
                       path with no symbolic link in it (on macOS write /private/tmp, not /tmp)
                       and no whitespace. It is created if absent. A mode refuses to start when its
                       own subdirectory (dry-run/ or release/) already exists, so a dry run that
                       must be repeated after a blind repair takes a new custody root.

What the run prints: on standard error one line per step as it ends, "step <id> <pack or -> <status>",
where the status is one of ok, tooling_refusal, outcome_class, unclassified_refusal, not_run; on
standard output one line, the record's path and its SHA-256. A refusal code reaches the record only
if the tracked table configs/analysis/b5/dry_run_refusal_classes.json lists it as a tooling refusal;
an outcome-class refusal prints only "outcome-class refusal at step N" and any code in neither list
only "unclassified refusal at step N". Exit status: 0 when every step completed (step 4's registered
p42 outcome counts as completed), 3 when the run ended at an outcome-class refusal, 2 otherwise.
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
