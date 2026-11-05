#!/usr/bin/env python3
"""Prepare B5 reader checks, render a complete Results candidate, or verify it.

Post-release operator only on study outputs. This command never runs analysis.
See docs/process/b5_results_renderer.md; candidates retain STOP_FILL/NEEDS-LEAD.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from joulewise.b5_analysis import results_renderer as r


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-dir', required=True, type=Path)
    parser.add_argument('--artifacts-dir', required=True, type=Path,
                        help='explicit root for record-relative outputs/ and disclosures/ paths')
    parser.add_argument('--comparison', required=True, type=Path)
    parser.add_argument('--recompute', required=True, type=Path)
    parser.add_argument('--window-index', type=Path, help='index used for the release; read as text only')
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare-checks', type=Path, metavar='NEW_JSON')
    modes.add_argument('--out', type=Path, metavar='NEW_DIRECTORY')
    modes.add_argument('--preview', type=Path, metavar='NEW_DIRECTORY', help='candidate with pending reader checks')
    modes.add_argument('--validate-rendered', type=Path, metavar='DIRECTORY')
    parser.add_argument('--checks', type=Path)
    args = parser.parse_args(argv)
    try:
        inputs = r.load_inputs(args.release_dir, args.artifacts_dir, args.comparison, args.recompute, args.window_index)
        if args.prepare_checks:
            with args.prepare_checks.open('xb') as stream:
                stream.write(r.canonical(r.prepare_review(inputs)) + b'\n')
        else:
            r.need(args.checks is not None, 'checks_required')
            expected = r.render(inputs, r.loads(r.read_file(args.checks)), allow_pending=bool(args.preview))
            if args.out or args.preview:
                r.publish(args.out or args.preview, expected)
            else:
                r.validate_rendered(args.validate_rendered, expected)
        return 0
    except Exception as exc:
        # No paths, values, or tracebacks on stdout/stderr.
        code = str(exc) if isinstance(exc, r.RendererRefusal) else 'input_or_output_invalid'
        if not re.fullmatch(r'[a-z_]+', code):
            code = 'input_or_output_invalid'
        print('B5_RESULTS_REFUSED ' + code, file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
