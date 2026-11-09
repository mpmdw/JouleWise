#!/usr/bin/env python3
"""Off-measurement-Mac pre-qualification for ALIGN v4; see docs/align/v4/PREQUAL.md.

With --w1-next {r1,w1}: the next-arm extension (docs/align/v4/W1-SMOKE.md) instead.

Exit codes: 0 pass (every check ran and passed), 1 fail, 3 incomplete (no failure,
but a check did not run, e.g. no model backend or --offline), 2 usage error.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.align import prequal  # noqa: E402

EXIT = {"pass": 0, "fail": 1, "incomplete": 3}


def main(argv=None):
    raw = list(sys.argv[1:] if argv is None else argv)
    if any(a.split('=', 1)[0] in ('--w1-next', '--w1-probe') for a in raw):
        # W1 / next-arm extension (docs/align/v4/W1-SMOKE.md): its own checks, table and report.
        from joulewise.align import w1_prequal
        return w1_prequal.cli(raw, script=Path(__file__).resolve())
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, required=True, help="new report directory")
    parser.add_argument("--work", type=Path, help="scratch dir (default: <output>.work)")
    parser.add_argument("--hf-cache", type=Path, default=os.environ.get("JW_PREQUAL_HF"),
                        help="HF cache root for D non-weight files and the sibling")
    parser.add_argument("--stage", choices=("r0", "r1", "w1"), default="r0")
    parser.add_argument("--python-bin", default=sys.executable,
                        help="stand-in for the Mac's $M/.venv/bin/python; passed to the launcher unresolved")
    parser.add_argument("--launcher", type=Path, help="path to launch_align_r0.py (default: this checkout)")
    parser.add_argument("--launcher-ref", help="git ref to extract launch_align_r0.py + wrapper from (e.g. origin/main)")
    parser.add_argument("--model-backend", choices=("none", *prequal.BACKENDS), default="none")
    parser.add_argument("--sibling-repo", default=prequal.SIBLING_REPO)
    parser.add_argument("--sibling-revision", default=prequal.SIBLING_REVISION)
    parser.add_argument("--generated-transitions", type=int, default=12)
    parser.add_argument("--r0-report", type=Path, help="an R0 report.json to run the D pin verifier against")
    parser.add_argument("--offline", action="store_true", help="no network: HF listing not run, caches only")
    parser.add_argument("--only", help="comma-separated subset (the report is then incomplete)")
    args = parser.parse_args(argv)
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    if args.output.exists():
        parser.error("--output must be a new directory")
    if not 1 <= args.generated_transitions <= 12:
        parser.error("--generated-transitions must be in [1, 12]")
    names = {n for n, _ in prequal.AIR_CHECKS + prequal.MODEL_CHECKS}
    only = set(args.only.split(",")) if args.only else None
    if only and not only <= names:
        parser.error(f"unknown checks: {sorted(only - names)}")
    work = args.work or args.output.with_name(args.output.name + ".work")
    work.mkdir(parents=True, exist_ok=True)
    ctx = prequal.Context(repo=ROOT, work=work, hf_cache=args.hf_cache, stage=args.stage,
                          python_bin=args.python_bin, launcher=args.launcher, launcher_ref=args.launcher_ref,
                          model_backend=args.model_backend, sibling_repo=args.sibling_repo,
                          sibling_revision=args.sibling_revision,
                          generated_transitions=args.generated_transitions, offline=args.offline,
                          r0_report=args.r0_report)
    report = prequal.run(ctx, only=only)
    prequal.write(report, args.output)
    print(f"{report['status']}: {args.output / 'prequal.json'}; failed={report['failed']} not_run={report['not_run']}")
    return EXIT[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
