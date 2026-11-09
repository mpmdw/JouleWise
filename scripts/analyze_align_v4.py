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
        calibration = load(args.input, calibration_only=True, through_window=args.through_window,
                           cache_dir=args.cache, workers=args.workers, document=document, source_session=sources)
        frozen = strict_json(input_path(args.thresholds).read_bytes()) if args.thresholds else None
        if args.calibration_only:
            fill, verdict = analyze(calibration, workers=args.workers, frozen_thresholds=frozen)
        else:
            has_tests = (args.through_window is None or args.through_window.startswith('T')) and any(w['window'].startswith('T') for w in document['windows'])
            if has_tests and (frozen is None or any(frozen.get(k) != v for k, v in freeze_bindings(calibration).items())):
                raise ValueError('test sources require a matching prospective threshold freeze')
            # C records are already verified/materialized in this invocation.
            # Open only T now; do not rehash or reduce C a second time.
            test_document = {**document, 'windows': [w for w in document['windows'] if w['window'].startswith('T')]}
            # W1 was loaded with C above. Dropping any redundant selection
            # field keeps the T-only document from tripping the selection-only
            # refusal; the field is never read.
            for key in ('selection_source', 'selection_desk'):
                test_document.pop(key, None)
            payload = load(args.input, through_window=args.through_window, cache_dir=args.cache,
                           workers=args.workers, document=test_document, source_session=sources)
            payload['windows'] = [*calibration['windows'], *payload['windows']]
            seen = set()
            payload['input_census'] = [r for r in [*calibration['input_census'], *payload['input_census']]
                if (r['path'],r['sha256']) not in seen and not seen.add((r['path'],r['sha256']))]
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
    parser.add_argument('--workers', type=int, choices=range(0, 9), default=0, help='0: conservative free-core/memory auto size')
    parser.add_argument('--calibration-only', action='store_true')
    parser.add_argument('--thresholds', type=Path)
    parser.add_argument('--through-window', choices=['W1', *('C'+str(i) for i in range(1,15)), *('T'+str(i) for i in range(1,4))],
                        help='recompute only the landed prefix; never open later exports')
    parser.add_argument('--cache', type=input_path, help='observation columns only; no decision cache')
    return run(parser.parse_args(argv))


if __name__ == '__main__':
    raise SystemExit(main())
