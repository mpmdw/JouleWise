#!/usr/bin/env python3
"""Primary v4 engine. Explicit desk exports only; stdout is structure-only.

Run --calibration-only to freeze C1-C8 thresholds before opening test sources.
For a complete run, --thresholds must match that prospective frozen artifact.
The native scorer/claim qualification remains a lead-owned unresolved gate.
"""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.align.v4_analysis import analyze, canonical
from joulewise.align.v4_analysis.engine import freeze_bindings
from joulewise.align.v4_analysis.io import input_path, load, strict_json


def run(args):
    output = input_path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    try:
        # C-only loading refuses a native T entry BEFORE opening a T export.
        document = strict_json(input_path(args.input).read_bytes())
        sources = {}
        calibration = load(args.input, calibration_only=True, document=document, source_session=sources)
        frozen = strict_json(input_path(args.thresholds).read_bytes()) if args.thresholds else None
        if args.calibration_only:
            fill, verdict = analyze(calibration, workers=args.workers, frozen_thresholds=frozen)
        else:
            has_tests = any(w['window'].startswith('T') for w in document['windows'])
            if has_tests and (frozen is None or any(frozen.get(k) != v for k, v in freeze_bindings(calibration).items())):
                raise ValueError('test sources require a matching prospective threshold freeze')
            payload = load(args.input, document=document, source_session=sources)
            fill, verdict = analyze(payload, workers=args.workers, frozen_thresholds=frozen)
        (output/'fill.json').write_bytes(canonical(fill))
        (output/'thresholds.json').write_bytes(canonical(fill['threshold_freeze']))
        (output/'verdict.json').write_bytes(canonical(verdict))
    except (ValueError, KeyError, TypeError, OSError, ArithmeticError) as exc:
        # Input content and diagnostic details belong only in the numeric fill
        # directory. Never interpolate an exception into stdout/stderr.
        (output/'refusal-detail.json').write_bytes(canonical(dict(type=type(exc).__name__, detail=str(exc))))
        verdict = dict(schema='joulewise.align_v4.analysis_verdict.v1', status='refused', codes=['input_refused'])
        (output/'verdict.json').write_bytes(canonical(verdict))
        print(canonical(verdict).decode(), end='')
        return 2
    print(canonical(verdict).decode(), end='')
    # A completed provisional numeric engine run is not claim certification.
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='new output directory')
    parser.add_argument('--workers', type=int, choices=range(1, 5), default=1)
    parser.add_argument('--calibration-only', action='store_true')
    parser.add_argument('--thresholds', type=Path)
    return run(parser.parse_args(argv))


if __name__ == '__main__':
    raise SystemExit(main())
