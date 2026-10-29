"""Run ``python -m unittest -v <module>`` with a passive step-9b sampler.

Read-only observation: a daemon thread inspects ``sys._current_frames()``,
/proc and gc counters. It replaces no callable, installs no trace, profile,
monitoring or gc callback, and writes only to the JSONL path in
L9_2_SAMPLE_LOG. The test program and its arguments are unchanged.

While a pulse projection (``_ProjectionWorkBudget``) is live on the main
thread it samples every 0.5 s: evaluated cells, budget elapsed, load, RSS,
swap, thread count, main-thread CPU, gc state and the innermost frames. Each
new projection also records the SHA-256 of the raw powermetrics and events
bytes it is projecting, plus the driver step/window on the stack.
"""
import collections
import gc
import hashlib
import json
import os
import runpy
import sys
import threading
import time

LOG = os.environ['L9_2_SAMPLE_LOG']
MAIN = threading.main_thread().ident


def proc_status():
    out = {}
    with open('/proc/self/status') as handle:
        for line in handle:
            key, _, value = line.partition(':')
            if key in ('VmRSS', 'VmHWM', 'VmSwap', 'Threads', 'voluntary_ctxt_switches',
                       'nonvoluntary_ctxt_switches'):
                out[key] = value.strip()
    return out


def thread_cpu(tid):
    try:
        native = threading.main_thread().native_id
        with open(f'/proc/self/task/{native}/stat') as handle:
            fields = handle.read().rsplit(')', 1)[1].split()
        tick = os.sysconf('SC_CLK_TCK')
        return round((int(fields[11]) + int(fields[12])) / tick, 2)
    except OSError:
        return None


def vmstat():
    keep = ('pswpin', 'pswpout', 'pgmajfault')
    out = {}
    with open('/proc/vmstat') as handle:
        for line in handle:
            key, value = line.split()
            if key in keep:
                out[key] = int(value)
    return out


def host_cpu():
    with open('/proc/stat') as handle:
        fields = handle.readline().split()[1:]
    values = list(map(int, fields))
    return sum(values), values[3] + values[4]


def walk(frame):
    found = dict(budget=None, rederive=None, step=None, window=None, stack=[])
    depth = 0
    while frame is not None:
        code = frame.f_code
        if depth < 6:
            found['stack'].append(f'{code.co_name}:{frame.f_lineno}')
        local = frame.f_locals if code.co_name in (
            'consume_cell', 'detect_pulses', 'rederive_detection_from_artifacts', 'run') else None
        if local is not None:
            if code.co_name == 'consume_cell' and found['budget'] is None:
                found['budget'] = local.get('self')
            elif code.co_name == 'detect_pulses' and found['budget'] is None:
                found['budget'] = local.get('projection_work_budget')
            elif code.co_name == 'rederive_detection_from_artifacts' and found['rederive'] is None:
                found['rederive'] = local
            elif code.co_name == 'run' and 'step' in local and found['step'] is None \
                    and type(local.get('self')).__name__ == 'StepRunner':
                found['step'], found['window'] = local.get('step'), local.get('window')
        frame = frame.f_back
        depth += 1
    return found


def sampler():
    started = time.time()
    last_heartbeat = 0.0
    current = None
    previous_cpu = host_cpu()
    with open(LOG, 'a', buffering=1) as log:
        def emit(kind, **row):
            row.update(kind=kind, t=round(time.time() - started, 3), wall=time.time(),
                       load=os.getloadavg(), proc=proc_status(), vm=vmstat(),
                       main_cpu_s=thread_cpu(MAIN), threads_py=threading.active_count(),
                       gc_count=gc.get_count(),
                       gc_collections=[s['collections'] for s in gc.get_stats()])
            log.write(json.dumps(row, default=str) + '\n')

        emit('start', argv=sys.argv, pid=os.getpid(), nproc=os.cpu_count())
        while True:
            time.sleep(0.5)
            frame = sys._current_frames().get(MAIN)
            if frame is None:
                continue
            found = walk(frame)
            del frame
            budget = found['budget']
            now_cpu = host_cpu()
            busy = None
            if now_cpu[0] > previous_cpu[0]:
                total = now_cpu[0] - previous_cpu[0]
                busy = round(1 - (now_cpu[1] - previous_cpu[1]) / total, 3)
            previous_cpu = now_cpu
            if budget is not None:
                key = id(budget)
                if current != key:
                    current = key
                    inputs = {}
                    rederive = found['rederive']
                    if rederive is not None:
                        for name in ('raw_powermetrics', 'events_jsonl'):
                            value = rederive.get(name)
                            if isinstance(value, bytes | bytearray):
                                inputs[name] = dict(sha256=hashlib.sha256(value).hexdigest(),
                                                    size=len(value))
                        inputs['protocol_id'] = rederive.get('protocol_id')
                        inputs['derivation_role'] = rederive.get('derivation_role')
                    emit('projection_start', step=found['step'], window=found['window'],
                         inputs=inputs, stack=found['stack'])
                emit('projection', step=found['step'], window=found['window'],
                     cells=budget.evaluated_cell_count,
                     budget_elapsed_s=round(time.monotonic() - budget.started_monotonic_s, 3),
                     host_busy=busy, stack=found['stack'])
            else:
                if current is not None:
                    emit('projection_end')
                    current = None
                if time.time() - last_heartbeat >= 60:
                    last_heartbeat = time.time()
                    emit('heartbeat', step=found['step'], window=found['window'], host_busy=busy,
                         stack=found['stack'])


if __name__ == '__main__':
    threading.Thread(target=sampler, name='l9-2-sampler', daemon=True).start()
    sys.argv = ['python3.13 -m unittest', *sys.argv[1:]]
    runpy.run_module('unittest', run_name='__main__', alter_sys=True)
