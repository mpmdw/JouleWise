#!/usr/bin/env python3
"""Report a block-5 phase-timer structure log (D-188 TIMERS).

Reads only the structure log written by ``scripts/run_b5_analysis.py --phase-log``
(step ids and integer wall seconds; every line is schema-checked first).

    python3.13 -I scripts/b5_phase_report.py LOG                 per-step table
    python3.13 -I scripts/b5_phase_report.py LOG --budget FILE   flag steps over budget (exit 1 if any)
    python3.13 -I scripts/b5_phase_report.py LOG --eta PRIOR     remaining time of a running LOG from a prior log
    python3.13 -I scripts/b5_phase_report.py --compare OLD NEW   per-step deltas between two logs
    python3.13 -I scripts/b5_phase_report.py --detail RESTRICTED_JSONL
        per-step top labels from a restricted runtime-phases.jsonl. Restricted
        custody only: run it where the custody operator may read restricted/.

A budget FILE is JSON: {"default_s": 3600, "steps": {"5": 3600, ...}}.
Exit status: 0, or 1 when a budget is exceeded, or 2 on an unreadable or
invalid log.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise.b5_analysis.phase_timing import (  # noqa: E402
    STEP_IDS, PhaseLineError, validate_phase_line)


class LogError(Exception):
    pass


def load(path, tier='structure'):
    rows = []
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise LogError(f'{path}: unreadable') from exc
    lines = data.splitlines(keepends=True)
    for number, line in enumerate(lines, 1):
        if number == len(lines) and not line.endswith(b'\n'):
            break  # a running log's partial last line
        try:
            rows.append(validate_phase_line(line, tier))
        except PhaseLineError as exc:
            raise LogError(f'{path}:{number}: invalid line ({exc})') from exc
    return rows


def summarize(rows):
    walls, order = {}, []
    total = None
    current = None
    last = None
    for row in rows:
        event = row['event']
        if event == 'step_begin':
            current = row['step']
            last = row
        elif event == 'heartbeat':
            last = row
        elif event == 'step_end':
            walls[row['step']] = walls.get(row['step'], 0) + row['wall_s']
            if row['step'] not in order:
                order.append(row['step'])
            current = None
        elif event == 'run_end':
            total = row['total_s']
    return {'walls': walls, 'order': order, 'total': total, 'current': current, 'last': last}


def _fmt(seconds):
    if seconds is None:
        return '-'
    hours, rest = divmod(int(seconds), 3600)
    minutes, secs = divmod(rest, 60)
    return f'{hours}:{minutes:02d}:{secs:02d}'


def table(summary, out):
    walls = summary['walls']
    total = summary['total'] if summary['total'] is not None else sum(walls.values())
    out.write(f'{"step":>5} {"wall_s":>8} {"h:mm:ss":>9} {"share":>7}\n')
    for step in summary['order']:
        share = 100 * walls[step] / total if total else 0
        out.write(f'{step:>5} {walls[step]:>8} {_fmt(walls[step]):>9} {share:>6.1f}%\n')
    out.write(f'{"total":>5} {total:>8} {_fmt(total):>9}\n')
    if summary['total'] is None:
        out.write('run not ended')
        if summary['current'] is not None:
            last = summary['last'] or {}
            out.write(f'; step {summary["current"]} running for {last.get("step_s", 0)} s'
                      f' (log at {last.get("elapsed_s", 0)} s)')
        out.write('\n')


def compare(old, new, out):
    a, b = old['walls'], new['walls']
    out.write(f'{"step":>5} {"old_s":>8} {"new_s":>8} {"delta_s":>8} {"ratio":>7}\n')
    for step in [s for s in STEP_IDS if s in a or s in b]:
        x, y = a.get(step), b.get(step)
        delta = '-' if x is None or y is None else f'{y - x:+d}'
        ratio = '-' if not x or y is None else f'{y / x:.2f}'
        out.write(f'{step:>5} {x if x is not None else "-":>8} {y if y is not None else "-":>8} {delta:>8} {ratio:>7}\n')
    ta, tb = old['total'], new['total']
    delta = '-' if ta is None or tb is None else f'{tb - ta:+d}'
    out.write(f'{"total":>5} {ta if ta is not None else "-":>8} {tb if tb is not None else "-":>8} {delta:>8}\n')


def budget(summary, path, out):
    try:
        spec = json.loads(Path(path).read_text())
        default = spec.get('default_s')
        steps = spec.get('steps', {})
        if (default is not None and type(default) is not int) or not isinstance(steps, dict) \
                or any(type(v) is not int for v in steps.values()):
            raise ValueError
    except (OSError, ValueError, AttributeError) as exc:
        raise LogError(f'{path}: invalid budget file') from exc
    over = []
    for step in summary['order']:
        limit = steps.get(step, default)
        if limit is not None and summary['walls'][step] > limit:
            over.append(step)
            out.write(f'OVER BUDGET step {step}: {summary["walls"][step]} s > {limit} s\n')
    current = summary['current']
    last = summary['last']
    if current is not None and last is not None and last.get('event') == 'heartbeat':
        limit = steps.get(current, default)
        if limit is not None and last['step_s'] > limit:
            over.append(current)
            out.write(f'OVER BUDGET step {current} (running): {last["step_s"]} s > {limit} s\n')
    if not over:
        out.write('all steps within budget\n')
    return over


def eta(summary, prior, out):
    """Remaining seconds of a running log, from a prior complete log's step walls (an estimate)."""
    walls = prior['walls']
    done = set(summary['order'])
    current = summary['current']
    last = summary['last'] or {}
    remaining = 0
    unknown = []
    for step in STEP_IDS:
        if step in done:
            continue
        if step not in walls:
            unknown.append(step)
            continue
        if step == current:
            remaining += max(0, walls[step] - last.get('step_s', 0))
        else:
            remaining += walls[step]
    out.write(f'ETA (estimate from prior log): {remaining} s ({_fmt(remaining)}) remaining')
    if unknown:
        out.write(f'; no prior wall for steps {",".join(unknown)}')
    out.write('\n')
    return remaining


def detail(path, out, top=8):
    rows = load(path, 'restricted')
    for row in rows:
        if row['event'] != 'step_end':
            continue
        wall = row['wall_ms']
        out.write(f'\nstep {row["step"]}: wall {wall // 1000} s, driver cpu {row["cpu_ms"] // 1000} s, '
                  f'serial {row["serial_ms"] // 1000} s, unattributed {row["unattributed_ms"] // 1000} s'
                  f' ({100 * row["unattributed_ms"] / max(1, row["sampled_ms"]):.1f}% of sampled)\n')
        for group in ('driver', 'child', 'member'):
            phases = row['phases'][group]
            if not phases:
                continue
            ranked = sorted(phases.items(), key=lambda item: -item[1][0])[:top]
            out.write(f'  {group:6} self: ' + ', '.join(f'{label} {s // 1000}s' for label, (s, _i) in ranked) + '\n')
            ranked = sorted(phases.items(), key=lambda item: -item[1][1])[:top]
            out.write(f'  {group:6} incl: ' + ', '.join(f'{label} {i // 1000}s' for label, (_s, i) in ranked) + '\n')
        for label, pool in row['pool'].items():
            out.write(f'  pool {label}: batches {pool["batches"]}, busy {pool["busy_ms"] // 1000} s over '
                      f'{pool["wall_ms"] // 1000} s x {pool["pool_size"]} ({pool["busy_permille"] / 10:.1f}%)\n')
        if row['programs']:
            ranked = sorted(row['programs'].items(), key=lambda item: -item[1]['wall_ms'])[:top]
            out.write('  programs: ' + ', '.join(f'{key} x{p["count"]} {p["wall_ms"] // 1000}s'
                                                 for key, p in ranked) + '\n')


def main(argv=None, out=sys.stdout):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('log', nargs='?')
    parser.add_argument('--compare', nargs=2, metavar=('OLD', 'NEW'))
    parser.add_argument('--budget')
    parser.add_argument('--eta', metavar='PRIOR')
    parser.add_argument('--detail', metavar='RESTRICTED_JSONL')
    args = parser.parse_args(argv)
    try:
        if args.detail:
            detail(args.detail, out)
            return 0
        if args.compare:
            compare(summarize(load(args.compare[0])), summarize(load(args.compare[1])), out)
            return 0
        if not args.log:
            parser.error('LOG is required')
        summary = summarize(load(args.log))
        table(summary, out)
        status = 0
        if args.eta:
            eta(summary, summarize(load(args.eta)), out)
        if args.budget and budget(summary, args.budget, out):
            status = 1
        return status
    except LogError as exc:
        sys.stderr.write(f'b5_phase_report: {exc}\n')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
