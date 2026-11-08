"""CW-1 run-kit and offline timing/thermal parser. No outcome/data discovery."""
from __future__ import annotations

from copy import deepcopy
import math
import statistics

from joulewise.align.apple import condition_waits as cw

CW1 = 'joulewise.align.condition_waits.cw1.v1'
IDLE_SOURCES = ('r0_rerun11_idle', 'r1_soak', 'cw1_soak')


def run_kit(*, python, r0_config, output, r1_sha256, reference_authority):
    """A concrete, reviewable plan. Creating it never probes the machine."""
    if not cw.is_digest(r1_sha256) or not reference_authority.strip():
        raise ValueError('R1 evidence and prospective Q authority required')
    return {'schema': CW1, 'status': 'PROVISIONAL', 'owner': 'measurement-MBP magistrate',
        'maximum_s': 7200, 'r1_sha256': r1_sha256, 'reference_authority': reference_authority,
        'preconditions': ['after R1 final mode/sensors', 'declared quiet gap; no competing jobs/agents',
                          'existing resident D weights only; offline; measured batch 1',
                          'frozen charger/support/cooler/display and qualified native channels'],
        'phases': [
            {'phase': 'preflight', 'cap_s': 300},
            {'phase': 'soak', 'duration_s': 1200},
            {'phase': 'pulse_d', 'cap_s': 900, 'argv': [python, '-B', '-m', 'joulewise.align.r0_runner',
                '--config', r0_config, '--output', output+'/r0-pulse', '--checks', 'long-decode',
                '--models', 'D', '--long-decode-attempts', '1', '--timeout', '900']},
            {'phase': 'recovery_d', 'duration_s': 1800},
            {'phase': 'pulse_finalize', 'cap_s': 900, 'argv': [python, '-B',
                'scripts/align_v4_condition_waits.py', 'finalize-standin', '--output', output+'/standin'],
             'display_transition': ['wake during pulse', 'sleep at actual pulse end']},
            {'phase': 'recovery_finalize', 'duration_s': 1800},
            {'phase': 'cleanup', 'cap_s': 300}],
        'logging': '1 Hz native sample schema, guard intervals, actual pulse-end boundaries; no scores/joules',
        'recovery_rule': 'observe all 1800 s even after first shadow release; never arm',
        'monitor_budget_cpu_s_per_s': .005, 'planning_credit_minutes': 0}


def q_candidates(template, rows):
    """Candidates only: never replaces a signed Q, never auto-registers deltas."""
    q = deepcopy(template)
    if not rows:
        return {'qualified': False, 'reason': 'no reference observations'}
    end = rows[-1]['finished']['monotonic_ns']
    selected = [r for r in rows if end-1200*cw.NS <= r['finished']['monotonic_ns'] <= end]
    times = [r['finished']['monotonic_ns'] for r in selected]
    if not cw._coverage(times, end-1200*cw.NS, end, origin=times[0]):
        return {'qualified': False, 'reason': 'reference needs complete last 1200 s'}
    for r in selected:
        t = r['finished']['monotonic_ns']
        pm = r.get('pm_observed_ns')
        if (r.get('display_asleep') is not True or r.get('screensaver_engaged') is not False
                or r.get('os_level') != 0 or r.get('pm_state') != 'Nominal'
                or type(pm) is not int or not 0 <= t-pm <= 2*cw.NS
                or r.get('ac_powermode') != q['ac_powermode']
                or r.get('setup_sha256') != q['setup_sha256']):
            return {'qualified': False, 'reason': 'reference setup/status/display unqualified'}
        battery = cw.battery_arm(r.get('battery') or {}, r.get('obc_off_attested_by'), r.get('topup'),
                                 now_epoch_s=r['finished']['wall_ns']/cw.NS)
        if not battery['admitted']:
            return {'qualified': False, 'reason': 'reference battery/topup unqualified'}
    candidates = {'temperatures': {}, 'fans': {}, 'power': {}}
    for role, c in q['temperatures'].items():
        values = [r.get('sensors', {}).get(c['key']) for r in selected]
        if any(not cw.finite(v) for v in values):
            return {'qualified': False, 'reason': 'reference channel missing:' + c['key']}
        times_s = [(t-end)/cw.NS for t in times]
        xm, ym = statistics.mean(times_s), statistics.mean(values)
        slope = sum((x-xm)*(y-ym) for x, y in zip(times_s, values))/sum((x-xm)**2 for x in times_s)
        residual = [y-(ym+slope*(x-xm)) for x, y in zip(times_s, values)]
        sd = statistics.pstdev(residual)
        candidates['temperatures'][role] = {**c, 'q': statistics.median(values), 'sd': sd,
            'delta_candidate': max(1, 3*sd), 'soak_slope_c_per_min': 60*slope}
        if abs(60*slope) > .2:
            return {'qualified': False, 'reason': 'reference soak unstable', 'candidates': candidates}
    for key, c in q['fans'].items():
        values = [r.get('sensors', {}).get(key) for r in selected]
        if any(not cw.finite(v) or v < 0 for v in values):
            return {'qualified': False, 'reason': 'reference fan missing:' + key}
        sd, med = statistics.pstdev(values), statistics.median(values)
        candidates['fans'][key] = {**c, 'q': med, 'sd': sd, 'delta_candidate': max(100, 3*sd)}
    segments = [p for r in selected for p in r.get('power_intervals', [])]
    means = [cw._mean_power(segments, t) for t in times if t >= times[0]+30*cw.NS]
    if not means or any(v is None or v <= 0 for v in means):
        return {'qualified': False, 'reason': 'reference power incomplete/nonpositive'}
    med, sd = statistics.median(means), statistics.pstdev(means)
    candidates['power'] = {**q['power'], 'q': med, 'sd': sd,
                            'delta_candidate': max(.25, .1*med, 3*sd)}
    return {'qualified': True, 'print_only': True, 'registration_authority': False,
            'source_sha256': cw.digest(rows), 'candidates': candidates}


def recovery(policy, header, rows):
    """Counterfactual release and re-exits. Full horizon is always required."""
    attempt = cw.Attempt(policy, **header)
    first, reexits, last_failure, last = None, [], None, None
    for row in rows:
        # Characterization is a shadow, never GO; keep observing after READY.
        row = {**row, 'go': False}
        last = attempt.feed(row)
        if last['band_ready']:
            if first is None:
                first = last['finished']['monotonic_ns']
        else:
            last_failure = {'monotonic_ns': last['finished']['monotonic_ns'], 'reasons': last['reasons']}
            failures = [r for r in last['reasons'] if r != 'ceiling'
                        and (r != 'guard_not_joint_ready' or row.get('guard_intervals'))]
            if first is not None and failures:
                reexits.append({'monotonic_ns': last_failure['monotonic_ns'], 'reasons': failures})
        if attempt.closed:
            break
    end = last['finished']['monotonic_ns'] if last else header['started']['monotonic_ns']
    horizon = (end-header['quiet_start_ns'])/cw.NS
    # The ceiling row is censoring, not an in-band release or a re-exit.
    qualified = first is not None and horizon >= 1800 and not reexits and end-first >= 180*cw.NS
    return {'qualified': qualified, 'first_release_ns': first, 'right_censored': first is None,
            'post_release_s': (end-first)/cw.NS if first is not None else None,
            'horizon_s': horizon, 'reexits': reexits, 'last_failure': last_failure,
            'trace_sha256': cw.digest(rows), 'samples': len(rows)}


def guard_replay(policy, idle_traces):
    """Zero *eligible idle* holds for all three named sources; empty isn't pass.

    Ignore only prescribed acquisition floors. Evaluate every subsequent native
    30 s guard boundary, so a later failure is visible even after first release.
    """
    reports = {}
    for source in IDLE_SOURCES:
        traces = idle_traces.get(source, [])
        eligible, holds = 0, []
        for record in traces:
            attempt = cw.Attempt(policy, **record['header'])
            for row in record['rows']:
                last = attempt.feed({**row, 'go': False})
                t = last['finished']['monotonic_ns']
                if 300*cw.NS <= t-attempt.start < 1800*cw.NS and row.get('guard_intervals'):
                    eligible += 1
                    if not last['band_ready']:
                        holds.append({'attempt_id': record['header']['attempt_id'],
                                      'monotonic_ns': t, 'reasons': last['reasons']})
                if attempt.closed:
                    break
        reports[source] = {'eligible': eligible, 'holds': holds, 'hold_count': len(holds),
                           'qualified': eligible > 0 and not holds}
    return {'qualified': all(r['qualified'] for r in reports.values()), 'sources': reports,
            'evidence_sha256': cw.digest(idle_traces)}


def parse_run(policy, run, idle_traces):
    """Off-MBP only. Each recovery uses its actual disruptive-end boundary."""
    if run.get('schema') != CW1:
        raise ValueError('CW-1 schema required')
    phases = run.get('recoveries', {})
    reports = {name: recovery(policy, phases[name]['header'], phases[name]['rows'])
               for name in ('recovery_d', 'recovery_finalize') if name in phases}
    replay = guard_replay(policy, idle_traces)
    budget = run.get('observer_cpu_s_per_s')
    wall = run.get('elapsed_s')
    qualified = (set(reports) == {'recovery_d', 'recovery_finalize'}
        and all(r['qualified'] for r in reports.values()) and replay['qualified']
        and cw.finite(budget) and 0 <= budget <= .005 and cw.finite(wall) and 0 < wall <= 7200
        and run.get('final_reads_undisturbed') is True and run.get('pulse_d_r0_passed') is True
        and run.get('display_transition_observed') is True
        and run.get('r1_sha256') == (policy.get('q') or {}).get('r1_sha256')
        and run.get('band_sha256') == policy['band_sha256'])
    return {'schema': CW1, 'qualified': qualified, 'band_sha256': policy['band_sha256'],
            'evidence_sha256': cw.digest(run), 'guard_replay': replay, 'recoveries': reports,
            'q_candidates': q_candidates(policy['q'] or run.get('reference_template'), run.get('soak', []))
                if policy['q'] or run.get('reference_template') else None,
            'observer_cpu_s_per_s': budget, 'planning_credit_minutes': 0,
            'limitations': ['two recoveries do not establish a recovery tail quantile or residual equivalence',
                            'Q/delta candidates require prospective lead approval; never auto-adopted']}


def execute_kit(kit, policy, sampler, *, pulse, preflight, display_transition,
                final_checks, journal, save, cancelled=lambda: False, observer_cost=lambda: None):
    """Magistrate-only orchestration with bounded, injected pulse handles.

    pulse(phase) returns a handle with poll()/terminate()/wait(); it must enforce
    the phase argv timeout and process-group cleanup. Sampling stays in this
    thread through pulses/recovery. No hardware is run by plan generation or
    parsing. Both recoveries continue for the full horizon after early release.
    """
    import time
    if kit.get('schema') != CW1 or kit.get('maximum_s') != 7200:
        raise ValueError('frozen CW-1 kit required')
    template = getattr(sampler, 'channels', None) or policy.get('q') or {}
    if kit.get('r1_sha256') != template.get('r1_sha256'):
        raise ValueError('CW-1 must follow the Q-linked final R1')
    ctx = sampler.ctx
    start = ctx.clocks.monotonic_ns()
    cpu_start = time.process_time()
    report = {'schema': CW1, 'r1_sha256': kit['r1_sha256'], 'band_sha256': policy['band_sha256'],
              'reference_template': template,
              'recoveries': {}, 'soak': [], 'phase_boundaries': [], 'status': 'running',
              'observer_cpu_s_per_s': None, 'final_reads_undisturbed': False,
              'pulse_d_r0_passed': False, 'display_transition_observed': False}
    child = None

    def check():
        if cancelled():
            raise InterruptedError('CW-1 cancelled')
        if ctx.clocks.monotonic_ns()-start >= 7200*cw.NS:
            raise TimeoutError('CW-1 hard two-hour ceiling')

    def boundary(phase):
        stamp = ctx.stamp().to_json()
        cw.marker(journal, phase, stamp)
        report['phase_boundaries'].append({'phase': phase, **stamp})
        return stamp

    try:
        if preflight() is not True:
            raise ValueError('CW-1 native preflight failed')
        check()
        if ctx.clocks.monotonic_ns()-start > 300*cw.NS:
            raise TimeoutError('CW-1 preflight exceeded 300 s')
        sampler.start()
        boot = sampler.boot_id()
        for phase in kit['phases'][1:-1]:
            check()
            name = phase['phase']
            stamp = boundary(name)
            phase_start = stamp['monotonic_ns']
            header = dict(attempt_id='cw1-'+name, boot_id=boot, started=stamp,
                          quiet_start_ns=phase_start)
            rows = []
            # Each recovery has a fresh guard origin on the same clock.
            sampler.previous = None
            sampler.previous_over = {}
            sampler.root_identities = {}
            if name.startswith('pulse'):
                if name == 'pulse_finalize':
                    display_transition('wake')
                child = pulse(phase)
            while True:
                check()
                tick = ctx.clocks.monotonic_ns()
                row = sampler.sample(attempt_id=header['attempt_id'], boot_id=boot)
                row['power_intervals'] = [p for p in row.get('power_intervals', []) if p['start_ns'] >= phase_start]
                rows.append(row)
                elapsed = (ctx.clocks.monotonic_ns()-phase_start)/cw.NS
                if name.startswith('pulse'):
                    code = child.poll()
                    if code is not None:
                        if code != 0:
                            raise ValueError(name+' failed')
                        if name == 'pulse_d':
                            report['pulse_d_r0_passed'] = True
                        child = None
                        break
                    if elapsed >= phase['cap_s']:
                        raise TimeoutError(name+' exceeded cap')
                else:
                    # Cost/disturbance of native final checks is in both traces.
                    if name.startswith('recovery') and elapsed >= 1500 and 'final_read_check' not in header:
                        header['final_read_check'] = final_checks() is True
                    if elapsed >= phase['duration_s']:
                        break
                ctx.clocks.sleep(max(0, 1-(ctx.clocks.monotonic_ns()-tick)/cw.NS))
            boundary(name+'_end')
            if name == 'soak':
                report['soak'] = rows
                report['soak_header'] = header
            elif name.startswith('recovery'):
                final_ok = header.pop('final_read_check', False)
                report['recoveries'][name] = {'header': header, 'rows': rows, 'final_checks_passed': final_ok}
            if name == 'pulse_finalize':
                report['display_transition_observed'] = (display_transition('sleep') is True
                    and any(r.get('display_asleep') is False for r in rows))
        report['final_reads_undisturbed'] = all(r['final_checks_passed'] for r in report['recoveries'].values())
        report['status'] = 'complete'
    except BaseException as exc:
        report['status'], report['error'] = 'inconclusive', f'{type(exc).__name__}:{exc}'
        raise
    finally:
        try:
            if child is not None:
                import subprocess
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=5)
        finally:
            try:
                sampler.close()
            finally:
                report['elapsed_s'] = (ctx.clocks.monotonic_ns()-start)/cw.NS
                report['observer_self_cpu_s_per_s'] = (time.process_time()-cpu_start)/max(1e-9, report['elapsed_s'])
                report['observer_cpu_s_per_s'] = observer_cost()
                report['observer_cost_note'] = 'total observer tree cost required; self diagnostic alone never qualifies'
                save(report)
    return report
