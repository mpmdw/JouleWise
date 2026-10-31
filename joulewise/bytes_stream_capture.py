"""Isolated, non-claim known-bytes stage and desk preparation.

Hardware lives at the existing telemetry adapter/probe seams. The night driver
owns the meter, hazard arm, census and teardown. This module never opens a
measurement checkout's ledger or a blinding key.
"""
from __future__ import annotations

import argparse
import dataclasses
from fractions import Fraction
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
ORDER = ('R', 'C', 'C', 'R')
CALL_S = {'R':759.2,'C':759.2}  # Rule §1: (3573.6 - 4*134.2)/4.
IDLE_S, SETTLE_S = 57.6, 3
# Rule §1 R5: all eight rungs ~270 s plus one ~10 s allocation/fill.
CHECK_PLANNED_S = 270 + 10
# Rule §§1/2: four streams + eight idles + twelve gaps + four ~10 s
# preparations = 3573.6 s; stage planning adds the worst-case residency check.
MEASURED_PLANNED_S = float(sum(Fraction(str(CALL_S[a]))+2*Fraction(str(IDLE_S))+
                               3*Fraction(str(SETTLE_S))+10 for a in ORDER))
CAPTURE_PLANNED_S = MEASURED_PLANNED_S + CHECK_PLANNED_S


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


def run_residency(archive, *, device, mx, clock, probe):
    """Retain the completed prefix even if view-building or a probe raises."""
    from scripts import bytes_stream_test as bt
    try:
        return _run_residency(archive,device=device,mx=mx,clock=clock,probe=probe)
    except Exception as exc:
        receipts = [read(path) for path in sorted((archive/'check').glob('*.json'))]
        reason = (f'allocation failed ({bt.RING_BYTES} B ring)' if isinstance(exc,MemoryError)
                  else f'check-status fault ({type(exc).__name__}: {exc})')
        result = bt.check_failure(reason,receipts,bt.residency_check(receipts)['rungs'])
        if not (archive/'CHECK_RECEIPTS.json').exists():
            write(archive/'CHECK_RECEIPTS.json',receipts)
        if not (archive/'CHECK.json').exists():
            write(archive/'CHECK.json',result)
        if isinstance(exc,MemoryError):
            return result
        raise


def _run_residency(archive, *, device, mx, clock, probe):
    """One allocation, one ordered check; every completed receipt is durable."""
    from scripts import bytes_stream_test as bt
    receipts = []
    raw_ns = getattr(clock,"raw_ns",lambda: round(clock.stamp().monotonic_after_s*1e9))
    def finish(result):
        write(archive/'CHECK_RECEIPTS.json',receipts)
        write(archive/'CHECK.json',result)
        return result
    try:
        ring = bt.allocate_ring(mx)
    except MemoryError as exc:
        return finish(bt.check_failure(str(exc),receipts))
    for k,b in enumerate(bt.LADDER):
        rows = bt.ring_views(mx,ring,b)
        for arm in ('C','R'):
            count = bt.RING_BYTES//b
            for j in range(4):  # One pilot, then the admitted three timing calls.
                receipt = probe(b,count,device=device,arm='check-'+arm,idle_s=0,settle_s=0,
                    mx=mx,clock_ns=raw_ns,sleep=clock.sleep,prepared_views=rows,warm=j == 0,
                    rung_index=k,check_phase='pilot' if j == 0 else 'timing')
                receipts.append(receipt)
                write(archive/f'check/{k}-{arm}-{j}.json',receipt)
                error = bt.geometry_error(receipt,b)
                if error:
                    return finish(bt.residency_check(receipts))
                try:
                    bt.clock_duration_bound_ns(receipt)
                except ValueError:
                    return finish(bt.residency_check(receipts))
                if j == 0:
                    t = (receipt['end_ns']-receipt['start_ns'])/1e9/receipt['repeats']
                    count = bt.planned_repeats(b,t,bt.CHECK_CALL_S,at_least_one=True)
        result = bt.residency_check(receipts)
        if result['status'] == 'residency resolved':
            return finish(result)
        # The only expected partial status after a complete unresolved rung
        # is the not-yet-run next rung. Other faults stop immediately.
        if result['reason'] != f'check-status fault (incomplete rung {k+1})':
            return finish(result)
    return finish(bt.residency_check(receipts))


def run_stage(archive, *, device, adapter=None, clock=None, mx=None, probe=None):
    """One residency check, at most one palindrome, durable failure evidence.

    Only the palindrome needs continuous energy capture. All completed receipts
    survive an exception, and a started capture always gets its teardown attempt.
    """
    from scripts import bytes_stream_test as bt
    from joulewise.adapters.powermetrics import PowermetricsTelemetryAdapter
    from joulewise.interfaces import RunContext
    from joulewise.schemas import BenchmarkConfig
    if os.environ.get('JW_B5_SYNTHETIC_ONLY') == '1' and (adapter is None or mx is None):
        raise ValueError('synthetic-only stage requires injected capture and array hardware seams')
    if mx is None:
        import mlx.core as mx
    archive = Path(archive)
    archive.mkdir(parents=True,exist_ok=False)
    config = BenchmarkConfig.from_mapping(read(ROOT/KIT/'telemetry.json'))
    clock = clock or RawClock()
    adapter = adapter or PowermetricsTelemetryAdapter(clock)
    context = RunContext(config,clock,'known-bytes',archive,archive/'raw',archive/'logs',archive/'outputs')
    probe = probe or bt.stream
    raw_ns = getattr(clock,"raw_ns",lambda: round(clock.stamp().monotonic_after_s*1e9))
    calls = []
    result = {'non_claim':True,'status':'started','device':device}
    write(archive/'capture_config.json',config.to_dict())
    started = False
    start = clock.stamp()
    try:
        check = run_residency(archive,device=device,mx=mx,clock=clock,probe=probe)
        result['check_status'] = check['status']
        if check['status'] != 'residency resolved':
            result.update(status='residency not resolved',reason=check['reason'])
            if check['reason'].startswith('allocation failed'):
                result['allocation_stop'] = {'bytes':bt.RING_BYTES,'reason':check['reason']}
            return result
        counts = {a:bt.planned_repeats(check['b'],check['rungs'][-1][a]['t_s'],CALL_S[a]) for a in ('R','C')}
        if any(n <= 0 for n in counts.values()):
            raise ValueError('planned duration is shorter than one whole sweep')
        result['planned_repeats'] = counts
        admission = adapter.start_sampling(config,context)
        started = True
        result['capture_start'] = {'ok':admission.ok,'message':admission.message}
        if not admission.ok:
            raise ValueError('continuous capture could not start: '+str(admission.message))
        start = clock.stamp()
        result['measured_session_start_ns'] = raw_ns()
        for i,arm in enumerate(ORDER):
            receipt = probe(check['b'],counts[arm],device=device,arm=arm,idle_s=IDLE_S,
                            settle_s=SETTLE_S,mx=mx,clock_ns=raw_ns,sleep=clock.sleep)
            calls.append(receipt)
            write(archive/f'calls/{i+1:02d}-{arm}.json',receipt)
            error = bt.geometry_error(receipt,check['b'])
            if error:
                result.update(status='incomplete',reason=error)
                break
        else:
            result['status'] = 'completed'
        result['measured_session_end_ns'] = raw_ns()
    except MemoryError as exc:
        result.update(status='incomplete',reason=str(exc),error=f'MemoryError: {exc}')
        result['allocation_stop'] = {'bytes':bt.RING_BYTES,'reason':str(exc)}
    except Exception as exc:
        result.update(status='incomplete',error=f'{type(exc).__name__}: {exc}')
    finally:
        stop = clock.stamp()
        if started:
            try:
                stopped = adapter.stop_sampling_with_evidence(config,context,
                    sampling_started=start,sampling_stopped=stop)
                write(archive/'capture_stop.json',{'samples':[dataclasses.asdict(s) for s in stopped.samples],
                    'uncertainty_evidence':stopped.uncertainty_evidence,
                    'start_stamp':dataclasses.asdict(start),'stop_stamp':dataclasses.asdict(stop),
                    'device_metadata':adapter.device_metadata(config)})
            except Exception as exc:
                result['capture_stop_error'] = f'{type(exc).__name__}: {exc}'
        result['call_count'] = len(calls)
        write(archive/'STAGE.json',result)
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
        T_stream_max_s=CAPTURE_PLANNED_S, planned_bytes=disk_bytes, member_count=len(ORDER), thresholds=thresholds,
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
                'one residency check and palindrome, no BYTES data/keys; exit all agents before t0; Ed NO overrides.')
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
        return 0 if run_stage(a.archive, device=a.device)['status'] in ('completed','residency not resolved') else 2
    else:
        p.error('choose prepare or stage')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
