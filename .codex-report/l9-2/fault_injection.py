"""Per-site wall-deadline fault injection over the real joined dry run (N3; ED-RULING item 6 condition).

Synthetic S10 windows only (JW_B5_SYNTHETIC_ONLY=1 JW_B5_S10_REAL_PROGRAMS=1).

One clean parent drives tests.b5_analysis.joined_s10's real joined harness. At
every step boundary (no StepRunner file open) it snapshots custody and forks one
child per refit site k = 0, 1, ... of that step, for two variants:

  cached    the run's shared calibration cache as the driver keeps it;
  uncached  the cache is emptied at the step start, so every calibration the
            step touches (including each NEG-8 reference's) is refitted.

A child makes the governed projection see a jumping clock (a host that blew
the 120 s wall deadline) inside its k-th detect_pulses call of the step and in
every later call ("from site k onward"). Nothing else is replaced; the deadline
constant and budgets are untouched. The child runs to the end and writes its
record. When the step has no k-th call the child reports no_site and exits at
the step's end. The parent waits, restores custody and carries on clean.

Per child the condition is checked against the clean parent record:
  * the first non-ok step is a refusal (tooling or unclassified), at or after N;
  * every output of every step that completed ok in the child has the clean
    digest: kept units (step 3), NEG-8 screens and loss lists, floors, closeout,
    claim verdicts and step-11 numbers cannot differ.

usage: fault_injection.py <out-dir> [plan.json]
plan.json: {"<step>": {"cached_k": <children with the run cache>, "uncached_k": <children with it emptied>}};
steps absent from the plan get no children. A child whose step has no k-th refit reports no_site and ends the
step's sequence. Without a plan every step gets both variants for every refit.
"""
import hashlib
import json
import os
import shutil
import sys
import time
import traceback
import types
from pathlib import Path
from unittest import mock

OUT = Path(sys.argv[1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
PLAN = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else None

from joulewise import powermetrics_fiducial as pf, whole_window as ww  # noqa: E402
from joulewise.b5_analysis import dry_run as d  # noqa: E402
from tests.b5_analysis.joined_s10 import JoinedHarness, require_windows  # noqa: E402

ROOT = Path(d.__file__).resolve().parents[2]
STATE = dict(step=None, step_ordinal=-1, calls_in_step=0, child=None, fired=[], calls=[], timings=[])


def log(*parts):
    with open(OUT / 'parent.log', 'a') as handle:
        handle.write(time.strftime('%H:%M:%S ') + ' '.join(str(p) for p in parts) + '\n')


class JumpingClock(types.ModuleType):
    def __init__(self):
        super().__init__('time')
        self._now = time.monotonic()

    def monotonic(self):
        self._now += 1000.0
        return self._now

    def __getattr__(self, name):
        return getattr(time, name)


def site():
    frames, frame = [], sys._getframe(2)
    while frame is not None and len(frames) < 8:
        path = frame.f_code.co_filename
        if (path.startswith(str(ROOT)) and not path.endswith('powermetrics_fiducial.py')
                and '/tests/' not in path and '.codex-report' not in path):
            frames.append(f'{Path(path).relative_to(ROOT)}:{frame.f_code.co_name}:{frame.f_lineno}')
        frame = frame.f_back
    return frames


ORIGINAL_DETECT = pf.detect_pulses


def detect(*args, **kwargs):
    index = STATE['calls_in_step']
    STATE['calls_in_step'] += 1
    where = site()
    child = STATE['child']
    fire = child is not None and (
        STATE['step_ordinal'] > child['ordinal'] or (STATE['step_ordinal'] == child['ordinal'] and index >= child['k']))
    if child is None:
        STATE['calls'].append(dict(step=STATE['step'], k=index, site=where))
    if not fire:
        return ORIGINAL_DETECT(*args, **kwargs)
    STATE['fired'].append(dict(step=STATE['step'], k=index, site=where))
    original = pf.time
    pf.time = JumpingClock()
    try:
        result = ORIGINAL_DETECT(*args, **kwargs)
    finally:
        pf.time = original
    STATE['fired'][-1]['disposition'] = result.projection_disposition
    STATE['fired'][-1]['trigger'] = result.projection_budget_trigger
    return result


detect.__wrapped__ = ORIGINAL_DETECT  # the run's deadline observer watches the real projection


def child_exit(payload):
    path = OUT / 'children' / (STATE['child']['name'] + '.json')
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(payload, indent=1, default=str))
    os._exit(0)


def wrap(step, ordinal, function):
    def step_function(s, r):
        if STATE['child'] is None and (PLAN is None or step in PLAN):
            fork_children(step, ordinal)
        STATE.update(step=step, step_ordinal=ordinal, calls_in_step=0)
        if STATE['child'] is not None and STATE['child']['ordinal'] == ordinal and STATE['child']['uncached']:
            cache = ww.shared_physics_cache()
            if cache is not None:
                cache.clear()
        started = time.monotonic()
        records = function(s, r)
        if STATE['child'] is None:
            STATE['timings'].append(dict(step=step, wall_s=round(time.monotonic() - started, 3),
                                         refits=STATE['calls_in_step']))
        child = STATE['child']
        if child is not None and child['ordinal'] == ordinal and not any(f['step'] == step for f in STATE['fired']):
            child_exit(dict(child=child, outcome='no_site', calls_in_step=STATE['calls_in_step']))
        return records
    return step_function


def fork_children(step, ordinal):
    custody = HARNESS.root / 'first'
    backup = HARNESS.root / 'first.snapshot'
    plan = (PLAN or {}).get(step, {'cached_k': 10**6, 'uncached_k': 10**6})
    for uncached in (False, True):
        k = 0
        while k < plan.get('uncached_k' if uncached else 'cached_k', 0):
            name = f'{ordinal:02d}-{step}-{"uncached" if uncached else "cached"}-k{k:02d}'
            done = OUT / 'children' / (name + '.json')
            if done.exists():
                # Resumed after a restart: this child already reported.
                outcome = json.loads(done.read_text())['outcome']
                log(name, outcome, 'resumed')
                if outcome != 'ran':
                    break
                k += 1
                continue
            if backup.exists():
                shutil.rmtree(backup)
            shutil.copytree(custody, backup, symlinks=True)
            sys.stdout.flush(); sys.stderr.flush()
            started = time.monotonic()
            pid = os.fork()
            if pid == 0:
                STATE['child'] = dict(name=name, step=step, ordinal=ordinal, k=k, uncached=uncached)
                STATE['fired'] = []
                return
            _, status = os.waitpid(pid, 0)
            shutil.rmtree(custody)
            shutil.move(str(backup), str(custody))
            result_path = OUT / 'children' / (name + '.json')
            outcome = json.loads(result_path.read_text())['outcome'] if result_path.exists() else f'no_result_status_{status}'
            log(name, outcome, f'{time.monotonic() - started:.1f}s')
            if outcome != 'ran':
                break
            k += 1


def digests(record):
    return {(row['step'], row['window'], output['name']): output['sha256']
            for row in record['steps'] for output in row['outputs']}


def main():
    global HARNESS
    fixture = require_windows()
    HARNESS = JoinedHarness(fixture.index)
    steps = tuple((step, wrap(step, ordinal, function)) for ordinal, (step, function) in enumerate(d.STEPS))
    started = time.monotonic()
    try:
        with mock.patch.object(pf, 'detect_pulses', detect), mock.patch.object(d, 'STEPS', steps):
            result = HARNESS.execute()
        payload = dict(outcome='ran', code=result.code, record=result.record, stderr=result.stderr[-4000:],
                       fired=STATE['fired'], wall_s=round(time.monotonic() - started, 1))
    except BaseException:
        payload = dict(outcome='exception', traceback=traceback.format_exc(), fired=STATE['fired'])
    if STATE['child'] is not None:
        child_exit(dict(payload, child=STATE['child']))
    (OUT / 'parent.json').write_text(json.dumps(dict(payload, calls=STATE['calls'], timings=STATE['timings']),
                                                indent=1, default=str))
    log('parent done', payload.get('code'), payload.get('wall_s'))


if __name__ == '__main__':
    main()
