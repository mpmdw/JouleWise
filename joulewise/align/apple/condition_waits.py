"""R16 P1/P2: pre-GO admission only; never a member/runtime thermal gate.

Inputs are frozen at registration. Decisions are recomputed from observations,
including at GO. Journals and receipts contain no task, score or energy fields.
All times are native, bracketed clocks; power is watts over explicit intervals.
"""
from __future__ import annotations

from collections import deque
from copy import deepcopy
import hashlib
import json
import math
import re

from joulewise.hazards.base import Stamp
from joulewise.hazards import contention
from joulewise.align.apple.v4_registration import battery_arm

NS = 1_000_000_000
POLICY = 'joulewise.align.condition_waits.policy.v1'
SAMPLE = 'joulewise.align.condition_waits.sample.v1'
RECEIPT = 'joulewise.align.condition_waits.receipt.v1'
FLOOR_S, STABLE_S, DISPLAY_S, CEILING_S = 300, 180, 300, 1800


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def is_digest(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def validate_q(q):
    """No bootstrap sensor names or initial-mode soak are implicitly qualified."""
    if not isinstance(q, dict) or q.get('schema') != 'joulewise.align.condition_waits.q.v1':
        raise ValueError('Q is missing/unqualified')
    for field in ('source_sha256', 'r1_sha256', 'classification_sha256', 'setup_sha256'):
        if not is_digest(q.get(field)):
            raise ValueError('Q needs ' + field)
    if (not isinstance(q.get('reference_authority'), str) or not q['reference_authority'].strip()
            or q.get('ac_powermode') not in (0, 2) or type(q['ac_powermode']) is not int
            or q.get('reference_seconds') != 1200 or q.get('qualified') is not True):
        raise ValueError('Q must bind a ruled, qualified 1200 s reference in the final R1 mode')
    sensors = q.get('temperatures', {})
    if set(sensors) != {'fast', 'slow'}:
        raise ValueError('Q requires final fast and slow channels')
    seen = set()
    for role in ('fast', 'slow'):
        c = sensors[role]
        if (not isinstance(c, dict) or not re.fullmatch(r'T[!-~]{3}', str(c.get('key', '')))
                or c.get('unit') != 'degC' or not c.get('decoder')
                or not finite(c.get('q')) or not -40 <= c['q'] <= 150
                or not finite(c.get('sd')) or c['sd'] < 0
                or not finite(c.get('delta')) or c['delta'] <= 0):
            raise ValueError('invalid Q temperature channel')
        aliases = {c['key'], *c.get('aliases', [])}
        if seen & aliases:
            raise ValueError('fast/slow aliases cannot be independent sensors')
        seen |= aliases
    if not isinstance(q.get('fans'), dict) or not q['fans']:
        raise ValueError('measurement MBP requires qualified fan channels')
    for key, c in q['fans'].items():
        if (not re.fullmatch(r'F[!-~]Ac', key) or c.get('unit') != 'rpm' or not c.get('decoder')
                or not finite(c.get('q')) or c['q'] < 0
                or not finite(c.get('sd')) or c['sd'] < 0):
            raise ValueError('invalid Q fan channel')
    p = q.get('power', {})
    if (p.get('channel') != 'processor_combined_power' or p.get('unit') != 'W'
            or p.get('decoder') != 'powermetrics.processor.combined_power_mW/1000'
            or not finite(p.get('q')) or p['q'] <= 0
            or not finite(p.get('sd')) or p['sd'] < 0
            or not finite(p.get('idle_upper_w')) or p['idle_upper_w'] <= 0):
        raise ValueError('qualified powermetrics power channel required (not DC-in)')
    if q.get('display_decoder') != 'IODisplayWrangler.CurrentPowerState<=1':
        raise ValueError('qualified display decoder required')
    return deepcopy(q)


def band_digest(q, guard):
    return digest({'q': q, 'guard': guard, 'floor_s': FLOOR_S, 'stable_s': STABLE_S,
                   'display_s': DISPLAY_S, 'ceiling_s': CEILING_S, 'slope_s': 60,
                   'slope_c_per_min': .2, 'power_mean_s': 30, 'coverage': .99, 'max_gap_s': 2})


def registration_policy(*, cohort, q, cw1, incumbent_policy_sha256, guard=None):
    """Freeze cohort fallback; never upgrade it because a later window passes."""
    guard = dict(guard or contention.DEFAULT_THRESHOLDS)
    if not isinstance(cohort, str) or not cohort.strip() or not is_digest(incumbent_policy_sha256):
        raise ValueError('cohort and incumbent policy digest required; no invented fixed cooldown')
    if q is not None:
        q = validate_q(q)
    band = band_digest(q, guard)
    qualified = (q is not None and isinstance(cw1, dict) and cw1.get('qualified') is True
                 and cw1.get('band_sha256') == band and is_digest(cw1.get('evidence_sha256'))
                 and cw1.get('guard_replay', {}).get('qualified') is True)
    return validate_policy({'schema': POLICY, 'cohort': cohort, 'q': q, 'guard': guard,
        'mode': 'condition' if qualified else 'incumbent_shadow', 'band_sha256': band,
        'cw1': cw1, 'incumbent_policy_sha256': incumbent_policy_sha256})


def validate_policy(p):
    if (not isinstance(p, dict) or p.get('schema') != POLICY
            or p.get('mode') not in ('condition', 'incumbent_shadow')
            or not isinstance(p.get('cohort'), str) or not p['cohort'].strip()
            or not is_digest(p.get('incumbent_policy_sha256'))):
        raise ValueError('invalid frozen condition-waits policy')
    q = validate_q(p['q']) if p.get('q') is not None else None
    limits = p.get('guard', {})
    for key, value in (('clean_s', 180), ('interval_s', 30), ('cap_s', 2700),
                       ('cpu_limit_s_per_s', .05)):
        if limits.get(key) != value:
            raise ValueError('R16 retains native guard ' + key)
    aggregate = limits.get('aggregate_cpu_limit_s_per_s')
    if aggregate is not None and (not finite(aggregate) or aggregate <= 0):
        raise ValueError('invalid registered aggregate condition')
    if p.get('band_sha256') != band_digest(q, limits):
        raise ValueError('band digest differs from frozen inputs')
    if p['mode'] == 'condition':
        cw = p.get('cw1') or {}
        if (q is None or cw.get('qualified') is not True or cw.get('band_sha256') != p['band_sha256']
                or not is_digest(cw.get('evidence_sha256'))
                or cw.get('guard_replay', {}).get('qualified') is not True):
            raise ValueError('active band requires Q and CW-1 including zero-hold guard replay')
    return deepcopy(p)


def _coverage(times, start, end, fraction=.99, origin=0):
    """One-second occupied cells, actual stamps, including both end brackets."""
    selected = sorted(t for t in times if start <= t <= end)
    if not selected or selected[0] - start > 2*NS or end-selected[-1] > 2*NS:
        return False
    if any(b-a > 2*NS for a, b in zip(selected, selected[1:])):
        return False
    # Fixed attempt grid, nearest nominal tick. Anchoring cells on each moving
    # window's final timestamp causes microsecond probe jitter at every native
    # 30 s boundary to invent empty cells on an otherwise complete 1 Hz trace.
    first, last = (start-origin)//NS, math.ceil((end-origin)/NS)-1
    cells = {min(max((t-origin+NS//2)//NS, first), last) for t in selected}
    return len(cells) / max(1, math.ceil((end-start)/NS)) >= fraction


def _slope(rows, end, key, origin=0):
    selected = [(t, s.get(key)) for t, s in rows if end-60*NS <= t <= end]
    if (any(not finite(v) for _, v in selected)
            or not _coverage([t for t, _ in selected], end-60*NS, end, fraction=.9, origin=origin)):
        return None
    x, y = [(t-end)/NS for t, _ in selected], [v for _, v in selected]
    xm, ym = sum(x)/len(x), sum(y)/len(y)
    den = sum((v-xm)**2 for v in x)
    return 60*sum((a-xm)*(b-ym) for a, b in zip(x, y))/den if den else None


def _mean_power(segments, end):
    start, cursor, total = end-30*NS, end-30*NS, 0.0
    for s in sorted(segments, key=lambda v: v['start_ns']):
        a, b, w = s['start_ns'], s['end_ns'], s['watts']
        if b <= start or a >= end:
            continue
        if a > cursor or (a < cursor and cursor > start) or not finite(w) or w < 0 or b <= a:
            return None
        left, right = max(start, a), min(b, end)
        total += (right-left)/NS*w
        cursor = right
    return total/30 if cursor == end else None


class Attempt:
    """Single bounded attempt. feed() continues through final GO reads.

    ``guard_intervals`` are the native contention.interval results, once each.
    Native Dwell is retained, including its counter-regression semantics. The
    *joint* interval additionally needs continuous measured clean time.
    """
    def __init__(self, policy, *, attempt_id, boot_id, started, quiet_start_ns,
                 attempt_number=1, ambient_check=None):
        self.policy = validate_policy(policy)
        self.started = Stamp.from_json(started).to_json()
        self.start = self.started['monotonic_ns']
        if (not isinstance(attempt_id, str) or not attempt_id or not isinstance(boot_id, str) or not boot_id
                or type(quiet_start_ns) is not int or quiet_start_ns > self.start):
            raise ValueError('attempt/boot identity and last disruptive boundary required')
        if attempt_number not in (1, 2) or type(attempt_number) is not int:
            raise ValueError('two attempts maximum; return to lead')
        if attempt_number == 2 and (not isinstance(ambient_check, dict)
                or not is_digest(ambient_check.get('previous_not_ready_sha256'))
                or not is_digest(ambient_check.get('check_sha256'))
                or not isinstance(ambient_check.get('checked_by'), str)
                or not ambient_check['checked_by'].strip()
                or not finite(ambient_check.get('checked_at_epoch_s'))
                or not 0 <= self.started['wall_ns']/NS-ambient_check['checked_at_epoch_s'] <= 1800):
            raise ValueError('retry requires fresh ambient check and previous not_ready receipt')
        self.identity = dict(attempt_id=attempt_id, boot_id=boot_id, attempt_number=attempt_number,
                             ambient_check=deepcopy(ambient_check))
        self.quiet = quiet_start_ns
        self.temperatures, self.good_times, self.display_times = deque(), deque(), deque()
        self.power = deque()
        self.guard = contention.Dwell(self.policy['guard'], started_ns=self.start)
        self.guard_from = self.guard_end = None
        self.display_from = self.stable_from = None
        self.previous = None
        self.hash = hashlib.sha256()
        self.samples = 0
        self.last_failure = None
        self.fatal = None
        self.closed = False
        self.last_result = None

    def feed(self, row, *, go=False, incumbent_ready=False):
        if self.closed:
            raise ValueError('attempt is closed; no work or sampling after GO')
        # Bad brackets are evidence and cannot become an apparently fresh sample.
        reasons = []
        try:
            a, b = Stamp.from_json(row['started']), Stamp.from_json(row['finished'])
            now = b.monotonic_ns
            if row.get('schema') != SAMPLE or any(row.get(k) != self.identity[k] for k in ('attempt_id', 'boot_id')):
                self.fatal = 'sample_identity'
            if (a.monotonic_ns > now or now-a.monotonic_ns > 2*NS or a.monotonic_ns < self.start
                    or abs((b.wall_ns-a.wall_ns)-(now-a.monotonic_ns)) > NS//10
                    or abs((b.monotonic_raw_ns-a.monotonic_raw_ns)-(now-a.monotonic_ns)) > NS//10):
                self.fatal = 'sample_clock_bracket'
            if self.previous is not None:
                prev = self.previous
                if (a.monotonic_ns <= prev.monotonic_ns
                        or abs((b.wall_ns-prev.wall_ns)-(now-prev.monotonic_ns)) > NS//10
                        or abs((b.monotonic_raw_ns-prev.monotonic_raw_ns)-(now-prev.monotonic_ns)) > NS//10):
                    self.fatal = 'clock_discontinuity'
                if now-prev.monotonic_ns > 2*NS:
                    self.stable_from = self.display_from = None
                    self.good_times.clear()
                    self.display_times.clear()
                    reasons.append('sample_gap')
            self.previous = b
        except (ValueError, KeyError, TypeError):
            self.fatal = 'sample_clock_bracket'
            now = self.previous.monotonic_ns if self.previous else self.start
        self.hash.update(canonical(row) + b'\n')
        self.samples += 1
        disruption = row.get('last_disruptive_ns')
        if disruption is not None:
            if type(disruption) is not int or disruption > now or disruption < self.quiet:
                self.fatal = 'disruptive_boundary'
            elif disruption > self.quiet:
                self.quiet = disruption
                self.stable_from = None
                self.good_times.clear()
        for interval in row.get('guard_intervals', []):
            x, y = interval['interval']['monotonic_ns']
            if (type(x) is not int or type(y) is not int or y <= x or y > now
                    or x < self.start or self.guard_end is not None and x < self.guard_end):
                self.fatal = 'guard_interval_clock'
                continue
            self.guard.add(interval)
            clean = (interval.get('clean') is True and not interval.get('error')
                     and not interval.get('outside_over_limit') and not interval.get('aggregate_over_limit'))
            if not clean:
                self.guard_from = None
            elif self.guard_from is None or self.guard_end != x:
                self.guard_from = x
            self.guard_end = y
        guard_good = (self.guard.ready and self.guard_from is not None
                      and self.guard_end is not None and 0 <= now-self.guard_end <= 2*NS
                      and now-max(self.guard_from, self.quiet) >= STABLE_S*NS)
        if not guard_good:
            reasons.append('guard_not_joint_ready')
        if row.get('display_asleep') is True and row.get('screensaver_engaged') is False:
            if self.display_from is None:
                self.display_from = now
            self.display_times.append(now)
        else:
            self.display_from = None
            self.display_times.clear()
            # A wake/sleep transition is disruptive; unknown cannot earn dwell.
            self.quiet = now
            reasons.append('display_unobserved_or_awake')
        if (self.display_from is None or now-self.display_from < DISPLAY_S*NS
                or not _coverage(self.display_times, now-DISPLAY_S*NS, now, origin=self.start)):
            reasons.append('display_floor')
        q = self.policy['q']
        physical = []
        sensors = row.get('sensors', {})
        self.temperatures.append((now, sensors))
        for segment in row.get('power_intervals', []):
            if (not all(type(segment.get(k)) is int for k in ('start_ns', 'end_ns'))
                    or segment['end_ns'] > now or segment['start_ns'] < self.start
                    or segment['end_ns'] <= segment['start_ns']):
                self.fatal = 'power_interval_clock'
            else:
                self.power.append(segment)
        power_end = self.power[-1]['end_ns'] if self.power else None
        power_mean = (_mean_power(self.power, power_end) if power_end is not None
                      and 0 <= now-power_end <= 2*NS else None)
        slope = None
        if q is None:
            physical.append('q_unavailable')
        else:
            for c in q['temperatures'].values():
                v = sensors.get(c['key'])
                if not finite(v) or abs(v-c['q']) > c['delta']:
                    physical.append('temperature:' + c['key'])
            slope = _slope(self.temperatures, now, q['temperatures']['slow']['key'], origin=self.start)
            if slope is None or abs(slope) > .2 + 1e-12:
                physical.append('slow_slope')
            for key, c in q['fans'].items():
                v = sensors.get(key)
                if (not finite(v) or v < 0 or (v != 0 if c['q'] == 0
                        else abs(v-c['q']) > max(100, 3*c['sd']))):
                    physical.append('fan:' + key)
            p = q['power']
            if (power_mean is None or abs(power_mean-p['q']) > max(.25, .1*p['q'], 3*p['sd'])
                    or power_mean > p['idle_upper_w']):
                physical.append('power')
            if row.get('ac_powermode') != q['ac_powermode'] or row.get('setup_sha256') != q['setup_sha256']:
                physical.append('setup_or_powermode')
        pm = row.get('pm_observed_ns')
        if (row.get('os_level') != 0 or type(row.get('os_level')) is not int
                or row.get('pm_state') != 'Nominal' or type(pm) is not int or not 0 <= now-pm <= 2*NS):
            physical.append('os_or_pm')
        battery = battery_arm(row.get('battery') or {}, row.get('obc_off_attested_by'),
                              row.get('topup'), now_epoch_s=self.previous.wall_ns/NS if self.previous else None)
        if not battery['admitted']:
            physical.append('battery')
        observed = row.get('battery_observed_ns')
        if type(observed) is not int or not 0 <= now-observed <= 2*NS:
            physical.append('battery_stale')
        if row.get('final_checks_passed') is not True:
            physical.append('final_checks')
        if self.fatal:
            physical.append(self.fatal)
        if not physical and row.get('display_asleep') is True and row.get('screensaver_engaged') is False:
            if self.stable_from is None:
                self.stable_from = now
            self.good_times.append(now)
        else:
            self.stable_from = None
            self.good_times.clear()
        if (self.stable_from is None or now-max(self.stable_from, self.quiet) < STABLE_S*NS
                or not _coverage(self.good_times, now-STABLE_S*NS, now, origin=self.start)):
            reasons.append('physical_stability')
        if now-self.quiet < FLOOR_S*NS:
            reasons.append('quiet_floor')
        reasons += physical
        expired = now-self.start >= CEILING_S*NS
        if expired:
            reasons.append('ceiling')
        if reasons:
            self.last_failure = {'monotonic_ns': now, 'reasons': list(reasons)}
        band_ready = not reasons
        # Shadow band has no authority over incumbent release or timing.
        ready = band_ready if self.policy['mode'] == 'condition' else incumbent_ready is True
        enforcing = self.policy['mode'] == 'condition'
        if enforcing and (self.fatal or expired):
            ready = False
        status = 'released' if ready else 'not_ready' if enforcing and (expired or self.fatal) else 'waiting'
        result = {'schema': RECEIPT, **self.identity, 'cohort': self.policy['cohort'],
            'policy_sha256': digest(self.policy), 'band_sha256': self.policy['band_sha256'],
            'q_sha256': digest(q) if q is not None else None,
            'mode': self.policy['mode'], 'started': self.started, 'finished': self.previous.to_json() if self.previous else self.started,
            'quiet_start_ns': self.quiet, 'stable_from_ns': self.stable_from,
            'display_from_ns': self.display_from, 'guard_clean_from_ns': self.guard_from,
            'guard_end_ns': self.guard_end, 'guard_ready': self.guard.ready,
            'status': status, 'go': bool(go and ready), 'band_ready': band_ready,
            'incumbent_ready': incumbent_ready is True, 'power_mean_w': power_mean,
            'slow_slope_c_per_min': slope, 'reasons': reasons, 'last_failure': self.last_failure,
            'samples': self.samples, 'trace_sha256': self.hash.hexdigest(),
            'next_action': ('ambient_check_then_one_retry' if self.identity['attempt_number'] == 1 else 'lead_ruling')
                if status == 'not_ready' else None}
        self.last_result = result
        self.closed = result['go'] or status == 'not_ready'
        for queue, span in ((self.temperatures, 61), (self.power, 32),
                            (self.good_times, STABLE_S+2), (self.display_times, DISPLAY_S+2)):
            while queue and (queue[0][0] if queue is self.temperatures else
                             queue[0]['end_ns'] if queue is self.power else queue[0]) < now-span*NS:
                queue.popleft()
        return deepcopy(result)


def replay(policy, header, rows):
    attempt = Attempt(policy, **header)
    result = None
    for row in rows:
        result = attempt.feed(row, go=row.get('go') is True,
                              incumbent_ready=row.get('incumbent_ready') is True)
    if result is None:
        raise ValueError('empty start-state trace')
    return result


def verify_binding(policy, header, rows, receipt, entry, *, at_ns=None):
    """Recompute, never trust a packet boolean or a cached decision.

    Native caller passes at_ns at actual GO. Static triage can omit it, but
    a receipt is evidence only, never permission to skip native final reads.
    """
    try:
        rebuilt = replay(policy, header, rows)
        return (rebuilt == receipt and receipt['status'] == 'released'
                and entry.get('receipt_sha256') == digest(receipt)
                and entry.get('policy_sha256') == digest(policy)
                and entry.get('attempt_id') == header['attempt_id']
                and entry.get('boot_id') == header['boot_id']
                and (at_ns is None or receipt['go'] is True
                     and 0 <= at_ns-receipt['finished']['monotonic_ns'] <= 2*NS))
    except (ValueError, TypeError, KeyError, AttributeError):
        return False


def marker(journal, phase, stamp):
    """Boundary marker only, on an already-open journal; no fsync or ledger."""
    journal.write(json.dumps({'phase': phase, 'monotonic_ns': stamp['monotonic_ns'],
                              'wall_ns': stamp['wall_ns']}, sort_keys=True) + '\n')
