"""Start-state equivalence (SSE) and idle-shadow timing for ALIGN v4 condition waits.

Design: docs/align/v4/CONDITION-WAITS-opus.md (proposals P1 and P3). Stdlib
only. This is an ANALYSIS and REPLAY tool, not an arm gate: it reads 1 Hz
thermal journals (SMC temperatures, fans, OS/PM status, optional package power
and battery state) and reports TIMING and PREDICATE outcomes only. It reads no
energy, residual, score or alarm field and writes nothing into custody.

Two questions it answers from a journal:

* ``start-state``: after a window's terminal completion, when would the
  proposed between-window cool-down end (released / ceiling_level /
  hold_level_offset / ceiling_unsettled / unobserved)?
* ``idle-shadow``: inside a member's configured idle, when did the G0 release
  predicate (bands relative to the window reference R, 60 s slow slope within
  +-0.2 C/min, OS level 0, PM Nominal) first hold for 10 consecutive samples?
  Print-only evidence for the D5 question (300 s idle), no control effect.

Row format (one JSON object per line), either the gate projection
``{"monotonic_ns": int, "sensors": {key: float|null}, "status": {...}}`` or a
raw Sidecar row ``{"module": "temperature", "kind": "reading", "started":
{"monotonic_ns": int, ...}, "values": {"sensors": {...}, "status": {...}}}``.
Optional per-row fields: ``power_w`` (powermetrics CPU+GPU+ANE, W) and
``battery`` ``{"is_charging": bool, "instant_amperage_ma": number}``.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import math
import sys
from pathlib import Path

NS = 1_000_000_000
SCHEMA = 'joulewise.align_v4.start_state_replay.v1'
OUTCOMES = ('released', 'ceiling_level', 'hold_level_offset', 'ceiling_unsettled', 'unobserved')


@dataclasses.dataclass(frozen=True)
class Policy:
    """Proposed SSE defaults (CONDITION-WAITS-opus.md section 2, P1).

    ``ref_*_c`` and ``delta_*_c`` come from R1's 30-min idle soak (S5 slots);
    ``fan_idle_rpm`` from the same soak's fan medians plus a margin.
    """
    s_fast: str
    s_slow: str
    ref_fast_c: float
    ref_slow_c: float
    delta_fast_c: float
    delta_slow_c: float
    fan_keys: tuple = ()
    fan_idle_rpm: float = math.inf
    slope_window_s: float = 300.0
    slope_max_c_per_min: float = 0.1
    stability_s: float = 300.0
    floor_s: float = 600.0
    ceiling_s: float = 2700.0
    ceiling_after_quiet_s: float = 1200.0
    power_p95_max_w: float | None = 1.0
    max_abs_current_ma: float = 200.0
    max_failed_fraction: float = 0.1
    level_offset_hold_c: float = 3.0
    require_status: bool = True

    @classmethod
    def from_mapping(cls, value):
        fields = {f.name for f in dataclasses.fields(cls)}
        unknown = set(value) - fields
        if unknown:
            raise ValueError('unknown policy fields: ' + ', '.join(sorted(unknown)))
        data = dict(value)
        if 'fan_keys' in data:
            data['fan_keys'] = tuple(data['fan_keys'])
        policy = cls(**data)
        for name in ('ref_fast_c', 'ref_slow_c', 'delta_fast_c', 'delta_slow_c', 'slope_window_s',
                     'slope_max_c_per_min', 'stability_s', 'floor_s', 'ceiling_s', 'ceiling_after_quiet_s'):
            number = getattr(policy, name)
            if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(number):
                raise ValueError(f'policy {name} must be a finite number')
        if policy.stability_s <= 0 or policy.slope_window_s < 10 or policy.ceiling_s < policy.floor_s:
            raise ValueError('policy needs stability_s > 0, slope_window_s >= 10 and ceiling_s >= floor_s')
        return policy


def _finite(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


def project(rows):
    """Normalize rows to ``(t_s, sensors, status, power_w, battery)`` in time order."""
    out = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get('module') == 'temperature' and row.get('kind') == 'reading':
            values = row.get('values') or {}
            mono = (row.get('started') or {}).get('monotonic_ns')
            sensors, status = values.get('sensors') or {}, values.get('status') or {}
        elif 'monotonic_ns' in row or 't_s' in row:
            mono = row.get('monotonic_ns')
            sensors, status = row.get('sensors') or {}, row.get('status') or {}
        else:
            continue
        t_s = row['t_s'] if _finite(row.get('t_s')) else (mono / NS if isinstance(mono, int) else None)
        if t_s is None:
            continue
        out.append((float(t_s), dict(sensors), dict(status), row.get('power_w'), row.get('battery')))
    out.sort(key=lambda item: item[0])
    return out


def ols_slope_per_min(points):
    """OLS slope in C/min over ``[(t_s, value)]``; None for fewer than 3 points."""
    if len(points) < 3:
        return None
    xm = sum(t for t, _ in points) / len(points)
    ym = sum(v for _, v in points) / len(points)
    denom = sum((t - xm) ** 2 for t, _ in points)
    if denom == 0:
        return None
    return 60.0 * sum((t - xm) * (v - ym) for t, v in points) / denom


def _p95(values):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1)]


class _Window:
    """Rows inside a trailing span, for slope and coverage."""

    def __init__(self, span_s):
        self.span_s, self.items = span_s, []

    def add(self, item):
        self.items.append(item)
        while self.items and self.items[0][0] < item[0] - self.span_s:
            self.items.pop(0)


def _status_ok(status, policy):
    if not policy.require_status:
        return True
    return status.get('os_level') == 0 and status.get('pm_state') in (None, 'Nominal')


def _battery_ok(battery, policy):
    if battery is None:
        return True
    current = battery.get('instant_amperage_ma')
    return battery.get('is_charging') is False and _finite(current) and abs(current) <= policy.max_abs_current_ma


def start_state(rows, policy, *, terminal_t_s, quiet_from_t_s=None):
    """Replay the proposed SSE cool-down on a journal. Timing/predicate output only.

    ``terminal_t_s``: authenticated terminal completion of the previous window.
    ``quiet_from_t_s``: end of finalize/push/offload (MBP evidence traffic);
    the stability interval must lie wholly after it. Defaults to terminal.
    """
    quiet_from = terminal_t_s if quiet_from_t_s is None else max(terminal_t_s, quiet_from_t_s)
    ceiling_t = max(terminal_t_s + policy.ceiling_s, quiet_from + policy.ceiling_after_quiet_s)
    floor_t = terminal_t_s + policy.floor_s
    window = _Window(policy.slope_window_s)
    run_start, last_t = None, None
    recent = []          # (t, good_except_level, level_ok, observed, s_slow, power)
    first_pass = {name: None for name in ('level', 'slope', 'fans', 'status', 'battery')}
    for t, sensors, status, power, battery in project(rows):
        if t < terminal_t_s - policy.slope_window_s:
            continue
        fast, slow = sensors.get(policy.s_fast), sensors.get(policy.s_slow)
        observed = _finite(fast) and _finite(slow)
        if _finite(slow):
            window.add((t, float(slow)))
        if t < terminal_t_s:
            last_t = t
            continue
        span = [p for p in window.items if p[0] >= t - policy.slope_window_s]
        coverage = len(span) / max(1.0, policy.slope_window_s)
        slope = ols_slope_per_min(span) if coverage >= 1 - policy.max_failed_fraction else None
        checks = {
            'level': observed and fast <= policy.ref_fast_c + policy.delta_fast_c
            and slow <= policy.ref_slow_c + policy.delta_slow_c,
            'slope': slope is not None and abs(slope) <= policy.slope_max_c_per_min,
            'fans': all(_finite(sensors.get(k)) and sensors[k] <= policy.fan_idle_rpm for k in policy.fan_keys),
            'status': _status_ok(status, policy),
            'battery': _battery_ok(battery, policy),
        }
        for name, ok in checks.items():
            if ok and first_pass[name] is None:
                first_pass[name] = t - terminal_t_s
        continuous = last_t is None or t - last_t <= 2.0
        last_t = t
        others = observed and all(ok for name, ok in checks.items() if name != 'level')
        recent.append((t, others, checks['level'], observed, slow if _finite(slow) else None,
                       power if _finite(power) else None))
        while recent and recent[0][0] < t - policy.stability_s:
            recent.pop(0)
        good = others and checks['level'] and continuous and t >= quiet_from
        run_start = (run_start if run_start is not None else t) if good else None
        if good and t - run_start >= policy.stability_s and t >= floor_t:
            powers = [r[5] for r in recent if r[0] >= run_start and r[5] is not None]
            if policy.power_p95_max_w is None or (powers and _p95(powers) <= policy.power_p95_max_w):
                return _result('released', t, terminal_t_s, quiet_from, ceiling_t, first_pass, policy, recent)
        if t >= ceiling_t:
            return _ceiling(t, terminal_t_s, quiet_from, ceiling_t, first_pass, policy, recent)
    return {'schema': SCHEMA, 'outcome': None, 'reason': 'journal ended before release or ceiling',
            'first_pass_s': first_pass, 'ceiling_t_s': ceiling_t}


def _offset(policy, recent):
    tail = [r[4] for r in recent if r[4] is not None]
    if not tail:
        return None
    tail = sorted(tail[-60:])
    return tail[len(tail) // 2] - (policy.ref_slow_c + policy.delta_slow_c)


def _result(outcome, t, terminal, quiet_from, ceiling_t, first_pass, policy, recent):
    return {'schema': SCHEMA, 'outcome': outcome, 'release_after_terminal_s': round(t - terminal, 3),
            'release_after_quiet_s': round(t - quiet_from, 3), 'ceiling_t_s': ceiling_t,
            'first_pass_s': {k: (round(v, 3) if v is not None else None) for k, v in first_pass.items()},
            'slow_offset_above_band_c': _offset(policy, recent)}


def _ceiling(t, terminal, quiet_from, ceiling_t, first_pass, policy, recent):
    observed = sum(1 for r in recent if r[3]) / max(1, len(recent))
    powers = [r[5] for r in recent if r[5] is not None]
    power_ok = policy.power_p95_max_w is None or (bool(powers) and _p95(powers) <= policy.power_p95_max_w)
    if not recent or observed < 1 - policy.max_failed_fraction:
        outcome = 'unobserved'
    elif power_ok and all(r[1] for r in recent):
        offset = _offset(policy, recent)
        outcome = 'ceiling_level' if offset is not None and offset <= policy.level_offset_hold_c else 'hold_level_offset'
    else:
        outcome = 'ceiling_unsettled'
    return _result(outcome, t, terminal, quiet_from, ceiling_t, first_pass, policy, recent)


def idle_shadow(rows, *, idle_start_t_s, idle_end_t_s, s_fast, s_slow, ref_fast_c, ref_slow_c,
                delta_fast_c, delta_slow_c, required=10, slope_window_s=60.0, slope_max=0.2,
                require_status=True):
    """First time inside an idle span that G0's predicate held ``required`` samples in a row.

    Mirrors ``thermal_gates`` G0 (bands one-sided vs R, |60 s OLS slope| <= 0.2
    C/min with >= 90 % coverage, OS 0, PM Nominal, samples <= 2 s apart).
    Returns seconds from idle start, or None. Print-only evidence.
    """
    window, consecutive, last_t = _Window(slope_window_s), 0, None
    policy = Policy(s_fast=s_fast, s_slow=s_slow, ref_fast_c=ref_fast_c, ref_slow_c=ref_slow_c,
                    delta_fast_c=delta_fast_c, delta_slow_c=delta_slow_c, require_status=require_status)
    for t, sensors, status, _power, _battery in project(rows):
        if t > idle_end_t_s:
            break
        fast, slow = sensors.get(s_fast), sensors.get(s_slow)
        if _finite(slow):
            window.add((t, float(slow)))
        if t < idle_start_t_s:
            last_t = t
            continue
        span = [p for p in window.items if p[0] >= t - slope_window_s]
        slope = ols_slope_per_min(span) if len(span) >= 0.9 * slope_window_s else None
        good = (_finite(fast) and _finite(slow) and (last_t is None or t - last_t <= 2.0)
                and fast <= ref_fast_c + delta_fast_c and slow <= ref_slow_c + delta_slow_c
                and slope is not None and abs(slope) <= slope_max and _status_ok(status, policy))
        last_t = t
        consecutive = consecutive + 1 if good else 0
        if consecutive >= required:
            return round(t - idle_start_t_s, 3)
    return None


def _read_jsonl(path):
    rows = []
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = parser.add_subparsers(dest='command', required=True)
    sse = sub.add_parser('start-state', help='replay the proposed SSE cool-down on a journal')
    sse.add_argument('--journal', type=Path, required=True)
    sse.add_argument('--policy', type=Path, required=True, help='JSON object of Policy fields')
    sse.add_argument('--terminal-t-s', type=float, required=True)
    sse.add_argument('--quiet-from-t-s', type=float)
    sse.add_argument('--grid', action='store_true',
                     help='also report slope_max x stability_s sensitivity (0.1/0.2 C/min x 120/300/600 s)')
    shadow = sub.add_parser('idle-shadow', help='G0-predicate first-hold time inside idle spans')
    shadow.add_argument('--journal', type=Path, required=True)
    shadow.add_argument('--spans', type=Path, required=True,
                        help='JSON list of {member, idle_start_t_s, idle_end_t_s}')
    shadow.add_argument('--policy', type=Path, required=True)
    args = parser.parse_args(argv)
    rows = _read_jsonl(args.journal)
    policy = Policy.from_mapping(json.loads(args.policy.read_text()))
    if args.command == 'start-state':
        result = start_state(rows, policy, terminal_t_s=args.terminal_t_s, quiet_from_t_s=args.quiet_from_t_s)
        if args.grid:
            result['grid'] = [
                {'slope_max_c_per_min': s, 'stability_s': w,
                 **{k: v for k, v in start_state(rows, dataclasses.replace(policy, slope_max_c_per_min=s,
                                                                         stability_s=w),
                                                 terminal_t_s=args.terminal_t_s,
                                                 quiet_from_t_s=args.quiet_from_t_s).items()
                    if k in ('outcome', 'release_after_terminal_s')}}
                for s in (0.1, 0.2) for w in (120.0, 300.0, 600.0)]
    else:
        result = {'schema': SCHEMA, 'idle_shadow': [
            {'member': span.get('member'),
             'configured_idle_s': span['idle_end_t_s'] - span['idle_start_t_s'],
             'g0_predicate_first_hold_s': idle_shadow(
                 rows, idle_start_t_s=span['idle_start_t_s'], idle_end_t_s=span['idle_end_t_s'],
                 s_fast=policy.s_fast, s_slow=policy.s_slow, ref_fast_c=policy.ref_fast_c,
                 ref_slow_c=policy.ref_slow_c, delta_fast_c=policy.delta_fast_c,
                 delta_slow_c=policy.delta_slow_c, require_status=policy.require_status)}
            for span in json.loads(args.spans.read_text())]}
    json.dump(result, sys.stdout, indent=2, sort_keys=True, allow_nan=False)
    sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
