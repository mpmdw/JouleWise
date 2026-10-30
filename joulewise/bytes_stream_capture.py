"""Isolated, non-claim known-bytes stage and desk preparation.

Hardware lives at the existing telemetry adapter/probe seams. The night driver
owns the meter, hazard arm, census and teardown. This module never opens a
measurement checkout's ledger or a blinding key.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
KIT = Path('configs/campaigns/bytes_stream_test')
ORDER = ('S', 'C1', 'C3', 'C2', 'C2', 'C3', 'C1', 'S')
# Reading rule §1: 22 powers, three ~2 s timing calls per size.
SCAN_EXPONENTS = range(14, 36)
SCAN_CALL_S = 2
# Reading rule §1 planned call lengths; §2 own idle and three settle gaps.
CALL_S = {'S': 500, 'C1': 250, 'C3': 250, 'C2': 250}
IDLE_S, SETTLE_S = 57.6, 3
# Rule §§1/2, same terms as the lifecycle span: palindrome 3573.6 s
# (calls + 16 idles + 24 settles + eight 10 s preparations), plus 22 sizes
# with three 2 s calls, four 10 s preparations and a 2 s pilot allowance.
CAPTURE_PLANNED_S = (sum(CALL_S[a] + 2*IDLE_S + 3*SETTLE_S + 10 for a in ORDER)
                     + len(SCAN_EXPONENTS)*(3*SCAN_CALL_S + 4*10 + SCAN_CALL_S))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class RawClock:
    """Adapter Clock interface using the receipt's RAW clock for its brackets."""
    def raw_ns(self):
        return time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)

    def now(self):
        return time.time()

    def stamp(self):
        from joulewise.clock import ClockStamp
        before = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
        epoch = time.time()
        after = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
        return ClockStamp(epoch, before, after, time.get_clock_info('time').resolution,
                          time.clock_getres(time.CLOCK_MONOTONIC_RAW))

    def sleep(self, seconds):
        time.sleep(seconds)

    def info(self):
        return {'kind': 'CLOCK_MONOTONIC_RAW', 'stamp': dataclasses.asdict(self.stamp())}


def run_stage(archive, *, device, adapter=None, clock=None, mx=None, probe=None):
    """One capture, one scan, at most one complete palindrome, durable receipts.

    Adapter/clock/mx injection is the hardware seam, not a second stage path.
    An exception retains completed receipts and a stage diagnostic; finally
    stops and preserves the continuous capture before returning.
    """
    from scripts import bytes_stream_test as bt
    from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
    from joulewise.interfaces import RunContext
    from joulewise.schemas import BenchmarkConfig
    if os.environ.get('JW_B5_SYNTHETIC_ONLY') == '1' and (adapter is None or mx is None):
        raise ValueError('synthetic-only stage requires injected capture and array hardware seams')
    archive = Path(archive)
    archive.mkdir(parents=True, exist_ok=False)
    config = BenchmarkConfig.from_mapping(read(ROOT / KIT / 'telemetry.json'))
    clock = clock or RawClock()
    adapter = adapter or PowermetricsTelemetryAdapter(clock)
    context = RunContext(config, clock, 'known-bytes', archive, archive/'raw', archive/'logs', archive/'outputs')
    probe = probe or bt.stream
    raw_ns = getattr(clock, "raw_ns", lambda: round(clock.stamp().monotonic_after_s*1e9))
    scan_calls, pilots, calls = [], [], []
    result = {'non_claim': True, 'status': 'started', 'device': device}
    write(archive/'capture_config.json', config.to_dict())
    start = clock.stamp()
    started = False
    try:
        admission = adapter.start_sampling(config, context)
        started = True
        result['capture_start'] = {'ok': admission.ok, 'message': admission.message}
        if not admission.ok:
            raise ValueError('continuous capture could not start: ' + str(admission.message))
        start = clock.stamp()
        for exponent in SCAN_EXPONENTS:
            size = 2 ** exponent
            try:
                pilot = probe(size, 1, device=device, idle_s=0, settle_s=0, mx=mx,
                              clock_ns=raw_ns, sleep=clock.sleep)
                pilots.append(pilot)
                write(archive/f'pilots/{exponent}.json', pilot)
                count = max(1, math.floor(SCAN_CALL_S / (pilot['duration_s']/pilot['repeats'])))
                for replicate in range(3):
                    receipt = probe(size, count, device=device, idle_s=0, settle_s=0, mx=mx,
                                    clock_ns=raw_ns, sleep=clock.sleep)
                    scan_calls.append(receipt)
                    write(archive/f'scan/{exponent}-{replicate}.json', receipt)
            except MemoryError as exc:
                result['allocation_stop'] = {'bytes': size, 'reason': str(exc)}
                # Incomplete triplets cannot enter the scan, but remain in raw receipts.
                scan_calls = [r for r in scan_calls if r['bytes_per_read'] != size]
                break
        scan = bt.knee_scan(scan_calls)
        write(archive/'SCAN_RECEIPTS.json', scan_calls)
        write(archive/'SCAN.json', scan)
        if scan['status'] == 'knee found':
            sizes = dict(zip(('S','C1','C3','C2'), (scan[k] for k in ('B','Bc1','Bc3','Bc2'))))
            counts = {}
            for arm, size in sizes.items():
                own = [r for r in scan_calls if r['bytes_per_read'] == size]
                if len(own) != 3:
                    raise ValueError('planned arm payload has no allocatable scan triplet: ' + arm)
                t_dispatch = math.fsum(r['duration_s']/r['repeats'] for r in own) / len(own)
                counts[arm] = math.floor(CALL_S[arm]/t_dispatch)
                if counts[arm] <= 0:
                    raise ValueError('planned duration is shorter than one dispatch: ' + arm)
            result['planned_repeats'] = counts
            result['measured_session_start_ns'] = raw_ns()
            for i, arm in enumerate(ORDER):
                receipt = probe(sizes[arm], counts[arm], device=device, idle_s=IDLE_S,
                                settle_s=SETTLE_S, mx=mx,
                                clock_ns=raw_ns, sleep=clock.sleep)
                calls.append(receipt)
                write(archive/f'calls/{i+1:02d}-{arm}.json', receipt)
            result['measured_session_end_ns'] = raw_ns()
        result['status'] = 'completed' if calls else 'knee not found'
    except Exception as exc:
        result.update(status='incomplete', error=f'{type(exc).__name__}: {exc}')
    finally:
        stop = clock.stamp()
        if started:
            try:
                stopped = adapter.stop_sampling_with_evidence(config, context,
                    sampling_started=start, sampling_stopped=stop)
                write(archive/'capture_stop.json', {'samples': [dataclasses.asdict(s) for s in stopped.samples],
                      'uncertainty_evidence': stopped.uncertainty_evidence,
                      'start_stamp': dataclasses.asdict(start), 'stop_stamp': dataclasses.asdict(stop),
                      'device_metadata': adapter.device_metadata(config)})
            except Exception as exc:
                result['capture_stop_error'] = f'{type(exc).__name__}: {exc}'
        result['call_count'] = len(calls)
        write(archive/'STAGE.json', result)
    return result


def prepare(checkout, session, *, t0, adapter_max_w, adapter_source, disk_bytes,
            programmed_span_s, span_derivation, disk_derivation):
    """Author a HAZARD_PACK plan in an existing independent non-claim clone.

    Explicit sizing inputs are recorded (never silently guessed). The clone
    must be clean; no source measurement checkout, ledger, models or keys are
    accepted. Local roots and the ledger are create-once inside session.
    """
    from joulewise.b5 import chain, plan as bp
    from joulewise import night_gate as ng
    from joulewise.hazards.arm import default_thresholds
    checkout, session = Path(checkout).resolve(), Path(session).resolve()
    if checkout != ROOT or not (checkout/'.git').is_dir():
        raise ValueError('prepare must run from its own ordinary clone (no linked checkout)')
    if session.exists():
        raise ValueError('session already exists; preserve it and use a fresh root')
    if subprocess.check_output(['git','status','--porcelain'], cwd=checkout).strip():
        raise ValueError('non-claim checkout must be clean')
    if adapter_max_w <= 0 or disk_bytes <= 0 or programmed_span_s <= 0 or not adapter_source or not span_derivation or not disk_derivation:
        raise ValueError('adapter rating/source, disk budget and derived duration are required')
    if t0 - time.time() < 300:
        # Existing installer requires 300 s before t0; not a new measurement bar.
        raise ValueError('t0 must leave the existing installer minimum lead of 300 s')
    pack = checkout/KIT
    tree = read(pack/'plan_tree.json')
    stages = chain.stage_plan(tree)
    session.mkdir(parents=True)
    roots = {role: session/tree['roots'][role+'_root_leaf'] for role in ('claim','bound')}
    for path in roots.values():
        path.mkdir()
    custody = session/'custody'
    custody.mkdir()
    write(session/'identity.json', {})  # Existing HAZARD reservation measures both vectors.
    write(session/'t1.json', {})
    head = subprocess.check_output(['git','rev-parse','HEAD'], cwd=checkout, text=True).strip()
    sid = session.name
    bindings = dict(repo_root=str(checkout), ledger_path=str(roots['claim']/'calibration_ledger.jsonl'),
                    claim_runs_root=str(roots['claim']), bound_runs_root=str(roots['bound']),
                    operator_log_root=str(custody/'operator-logs'),
                    pre_calibration_dir=str(roots['claim']/'instrument_validation/pre'),
                    post_calibration_dir=str(roots['claim']/'instrument_validation/post'),
                    claim_backup_destination=str(session/'backup-claim'), bound_backup_destination=str(session/'backup-bound'),
                    bracket_session_id=sid, pre_attempt_id='pre', post_attempt_id='post',
                    identity_epoch_json=str(session/'identity.json'), t1_bindings_json=str(session/'t1.json'))
    reg = read(checkout/'configs/b6/registration/acceptance.json')
    bindings['capture_screen'] = {k: reg['calibration'][k] for k in
        ('alignment_reference_s','bracket_screen_s','operative_bound_stop_s')}
    # Existing b5 window env interface. No default ledger paths are used.
    env = dict(zip(bp.WINDOW_ENV_KEYS, ['none']*len(bp.WINDOW_ENV_KEYS)))
    env.update(MEASUREMENT_REPO=str(checkout), WINDOW_ID='bytes-stream-test', BRACKET_SESSION_ID=sid,
               FROZEN_PLAN=str(pack/'collection_plan.json'), PACK_ROOT=str(pack), PACK_ID=pack.name,
               PLAN_ID='bytes-stream-test', EVIDENCE_ROOT_ID='bytes-stream-test',
               IDENTITY_EPOCH_JSON=bindings['identity_epoch_json'], T1_BINDINGS_JSON=bindings['t1_bindings_json'],
               PRE_ATTEMPT_ID='pre', POST_ATTEMPT_ID='post', RUNS_ROOT=str(roots['claim']),
               BOUND_RUNS_ROOT=str(roots['bound']), CALIBRATION_LEDGER=bindings['ledger_path'],
               LEDGER_HEAD_PIN=str(pack/'genesis_pin.json'), ARM_READINESS_CUSTODY_ROOT=str(custody/'hazards'),
               CUSTODY_ROOT=str(custody), WINDOW_CUSTODY_ROOT=str(custody), QUARANTINE_ROOT=str(custody/'quarantine'),
               CLAIM_BACKUP_DEST=bindings['claim_backup_destination'], BOUND_BACKUP_DEST=bindings['bound_backup_destination'],
               POWER_POLICY='ac_high_power', SETTLE_S=str(chain.SETTLE_S))
    env_raw = bp.window_env_bytes(env)
    (custody/'window.env').write_bytes(env_raw)
    raw = chain.render_chain(tree=tree, tree_sha256=sha(pack/'plan_tree.json'), stages=stages,
                             bindings=bindings, measurement_root=checkout, pack_root=pack,
                             plan_id=sid, runbook_text=(checkout/chain.RUNBOOK_RELATIVE).read_text())
    (custody/'chain.zsh').write_bytes(raw)
    (custody/'chain.zsh.sha256').write_bytes(chain.sidecar_bytes(raw, 'chain.zsh'))
    thresholds = default_thresholds()
    thresholds['clock']['t_stream_max_s'] = CAPTURE_PLANNED_S
    thresholds['disk']['planned_bytes'] = disk_bytes
    # Existing arm's stage cap plus explicit planned span, rounded to minutes as b5.
    maximum = 60 * math.ceil((programmed_span_s + bp.T0_STAGE_CAP_S)/60)
    hazard = dict(schema=ng.HAZARD_WINDOW_SCHEMA, attempt=1,
        pack=dict(pack_id=pack.name, pack_root=str(pack), pack_sha256=None,
                  plan_tree_sha256=sha(pack/'plan_tree.json'), pack_plan_id='bytes-stream-test',
                  window_id='bytes-stream-test', evidence_root_id='bytes-stream-test'),
        bracket_session_id=sid, bindings=bindings, runs_roots={k:str(v) for k,v in roots.items()},
        T_stream_max_s=CAPTURE_PLANNED_S, planned_bytes=disk_bytes, member_count=8, thresholds=thresholds,
        g10=False, programmed_span_s=programmed_span_s, t0_stage_cap_s=bp.T0_STAGE_CAP_S,
        settle_s=chain.SETTLE_S, window_env=dict(path=str(custody/'window.env'),sha256=sha(custody/'window.env')),
        registration=None, chain_deviations=list(chain.DEVIATIONS), disk_volumes=[str(v) for v in roots.values()],
        stages=[s.summary() for s in stages])
    plan = dict(schema=ng.HAZARD_PLAN_SCHEMA, schema_version=ng.HAZARD_PLAN_SCHEMA_VERSION,
                plan_id=sid, receipt_class=ng.HAZARD_PACK, t0_epoch_s=t0, window_max_s=maximum,
                authored_epoch_s=time.time(), repo_head=head, measurement_root=str(checkout), measurement_head=head,
                chain_path=str(custody/'chain.zsh'), chain_sha256_path=str(custody/'chain.zsh.sha256'),
                custody_root=str(custody), registration_path=None, hazard_window=hazard)
    ng.NightPlan.from_mapping(plan)
    write(session/'night_plan.json', plan)
    write(session/'SESSION.json', dict(non_claim=True, checkout=str(checkout), head=head,
        adapter_max_w=adapter_max_w, adapter_source=adapter_source, programmed_span_s=programmed_span_s,
        span_derivation=span_derivation, disk_bytes=disk_bytes, disk_derivation=disk_derivation, calibration_registration=reg,
        roots={k:str(v) for k,v in roots.items()}))
    notice = dict(plan_id=sid, head=head, plan_sha256=sha(session/'night_plan.json'), t0_epoch_s=t0,
        window_max_s=maximum, roots={k:str(v) for k,v in roots.items()}, non_claim=True,
        message='Lead sends Ed: known-bytes non-claim test; these exact head/plan/root/t0/duration values; '
                'one scan and palindrome, no BYTES data/keys; exit all agents before t0; Ed NO overrides.')
    print(json.dumps(notice, indent=2))
    return plan


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command')
    prep = sub.add_parser('prepare')
    prep.add_argument('--checkout', type=Path, required=True)
    prep.add_argument('--session', type=Path, required=True)
    prep.add_argument('--t0', type=float, required=True)
    prep.add_argument('--adapter-max-w', type=float, required=True)
    prep.add_argument('--adapter-source', required=True)
    prep.add_argument('--disk-bytes', type=int, required=True)
    prep.add_argument('--programmed-span-s', type=int, required=True)
    prep.add_argument('--span-derivation', required=True)
    prep.add_argument('--disk-derivation', required=True)
    stage = sub.add_parser('stage')
    stage.add_argument('--archive', type=Path, required=True)
    stage.add_argument('--device', required=True)
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == '--archive':
        args.insert(0, 'stage')
    a = p.parse_args(args)
    if a.command == 'prepare':
        prepare(a.checkout, a.session, t0=a.t0, adapter_max_w=a.adapter_max_w,
                adapter_source=a.adapter_source, disk_bytes=a.disk_bytes,
                programmed_span_s=a.programmed_span_s, span_derivation=a.span_derivation,
                disk_derivation=a.disk_derivation)
    elif a.command == 'stage':
        def interrupted(signum, frame):
            raise InterruptedError('night driver stopped the known-bytes stage')
        signal.signal(signal.SIGTERM, interrupted)
        return 0 if run_stage(a.archive, device=a.device)['status'] in ('completed','knee not found') else 2
    else:
        p.error('choose prepare or stage')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
