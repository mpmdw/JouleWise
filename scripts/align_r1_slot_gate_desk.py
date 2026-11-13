#!/usr/bin/env python3
"""B1: the slot-session gate desk (RL-131 gate table, floor census, U2 pair, S6, start state; RL-135).

Usage:
  python3.13 -B -s -E scripts/align_r1_slot_gate_desk.py TREE RUN_DIR --record out/record.json \
      [--kit-desk out/kit_desk.json] [--force-s6-replay] --json-out out/gate_desk.json > out/gate_desk.txt
  python3.13 -B -s -E scripts/align_r1_slot_gate_desk.py --census-journal JOURNAL [--classification FILE] \
      --json-out out.json          (floor census of one journal only; step 0 runs it on step-D's inventory)

TREE is ``git archive a6a09e6d7`` extracted (the night commit). The gate module
``joulewise/align/apple/thermal_gates.py`` is imported from TREE only and its
sha256 is asserted (c72937bd...918d); it is never imported from the working
tree. The gate decision is not reimplemented: ``ThermalSession._wait`` runs
unmodified against each journal's rows through the 11-12 harness
(``load_member``, ``ReplayClock``, ``StubSidecar``, ``replay_wait``, lifted from
/Volumes/JW-EXT/scratch/r1fu-desk/scripts/desk_replay.py unchanged in
behaviour). Every recorded G0, G1 and H is replayed first (validation); on any
disagreement the tool writes the validation block only and exits 1 before any
table is printed.

Blind-safe. From each journal line only: kind, read stamps, values.sensors,
values.errors, values.status, and gate / hold begin and end records.
events.jsonl is projected to stage_started / stage_completed (type, phase,
timestamp); config.json to workload_profile.prompt_text -> thermal and
condition; outputs/align_window_reference.json; record.json for the duty
verdicts and the driver's G1 median; kit_desk.json for its Tf08 excess. No
energy, power, meter, transcript or episode file is opened.

Definitions: the desk spec (/Volumes/JW-EXT/scratch/fable-r1-slot-desk-spec.md
section 2.1) and RL-135. Output is deterministic: sorted keys, no wall clock,
every input file listed with its sha256.
"""
import argparse
import bisect
import hashlib
import importlib.util
import json
import math
import re
import sys
from pathlib import Path
from statistics import median as _median
from types import SimpleNamespace

SCHEMA = 'joulewise.align_r1_slot_gate_desk.v1'
NIGHT_COMMIT = 'a6a09e6d7c3c756551c3e5c3546311c96fe8d3fe'
THERMAL_GATES_SHA256 = 'c72937bd8bf7b5553c1ffd70e76018ffbf25f32578533c8749aa88419837918d'
THERMAL_GATES_PATH = 'joulewise/align/apple/thermal_gates.py'
THERMAL_REPLAY_PATH = 'scripts/align_r1_thermal_replay.py'
NS = 10**9
JOURNAL = 'align_thermal.jsonl'
FAST_KEY, SLOW_KEY, TF08 = 'TV0h', 'TVh0', 'Tf08'          # census keys (RL-131 item 2.5)
STEP_D = 'step_D_prefill_10k_decode_4096'
GATED_D_RUNS = ('D_bank_benign_s1_gated_held', 'D_spam_benign_s1_gated_held_a',
                'D_spam_benign_s1_gated_held_b')               # r1_phase_table.GATED_D_RUNS
X_G = 'X_G_contrast'
SCHEDULE_MEMBERS = (STEP_D,) + GATED_D_RUNS + (X_G,)
PLANNING = re.compile(r'^planning_turn_R_plus_(0|2|4)C$')
SUPERSEDED = re.compile(r'\.(?:rejected|g0_timeout)\d+$')
PLANNING_FAST_CEILING_C = 150.0      # r1_runtime.py: planning gates band S_slow only
SLOPE_BAR_C_PER_MIN = 0.2            # thermal_gates.py _wait (G0 slope clause)
PM_FRESH_NS = 2 * NS                 # thermal_gates.py _wait (pm observation <= 2 s)
SLOPE_MISMATCH_C_PER_MIN = 0.05      # spec 2.1(b)
SKEW_NEIGHBOUR_NS = 2_500_000_000    # spec 2.1(e)
SKEW_SLACK_C = 0.05                  # spec 2.1(e)
FLOOR_STEP_C = 5.0
FLOORED_LOW_C = 35.0                 # T1 arm: floored row with TV0h < 35.0
T1_SKEW_FRACTION = 0.01              # T1 arm: skew rows above 1 % of all rows
T3_BAR_C = 3.0                       # U2 registered bar (RL-135 item 9)
S6_MEDIAN_BAR_S = 90.0               # RL-122 item 3b
S6_STEPS_C = (1.5, 2.0)
S6_REPLAY_CAP_S = 300.0
ALT_LABEL = 'alternative, not registered'
CLAUSES_G0 = ('valid', 'status', 'band_fast', 'band_slow', 'slope_slow')
CLAUSES_TURN = ('valid', 'band_fast', 'band_slow')
# clause_last tie-break (released gates): the first of this order among clauses
# sharing the largest last_violation_s; every tie is listed in clause_last_ties.
CLAUSE_TIE_ORDER = ('valid', 'status', 'band_fast', 'band_slow', 'slope_slow')

# ---- LAYOUT ASSUMPTION (spec "Not checked"; the lead confirms it in step 0) ----
# The quiet span that follows a released G0 (r1_runtime.reference_hook, quiet_s):
# the code at a6a09e6d7 writes its absolute bounds only in the step's inventory
# classification (classify_step phase_bounds_ns.quiet = [prefill - 300 s, prefill]);
# runtime_result.json carries thermometry.phases in seconds relative to that origin
# only. The span that starts at the G0's end ends at prefill = quiet[1].
QUIET_SPAN_FILE = 'inventory/r1_classification.json'      # relative to RUN_DIR/<phase>/
QUIET_SPAN_FIELD = ('classification', 'phase_bounds_ns', 'quiet')
QUIET_SPAN_MEMBERS = ('step_30b', STEP_D)                  # members whose driver idles quiet_s after G0


class DeskError(RuntimeError):
    """Unusable input or unconfirmed layout: exit 2."""


class ValidationFailed(RuntimeError):
    """The module replay does not reproduce a recorded gate: exit 1."""


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def median(values):
    """gate_wait_medians / statistics.median: even count = mean of the two middle values."""
    values = list(values)
    return _median(values) if values else None


# ---------------------------------------------------------------- tree loading
def load_tree(tree):
    """Import thermal_gates (and the 11-12 night_desk module) from TREE only, hash-asserted."""
    tree = Path(tree).resolve()
    path = tree / THERMAL_GATES_PATH
    if not path.is_file():
        raise DeskError(f'{path}: TREE has no thermal_gates.py (expected `git archive {NIGHT_COMMIT[:9]}`)')
    digest = sha256_bytes(path.read_bytes())
    if digest != THERMAL_GATES_SHA256:
        raise DeskError(f'{path}: sha256 {digest} != {THERMAL_GATES_SHA256} (night commit gate module)')
    if 'joulewise' in sys.modules:
        loaded = Path(getattr(sys.modules['joulewise'], '__file__', '') or '').resolve()
        if tree not in loaded.parents:
            raise DeskError(f'joulewise already imported from {loaded}; refusing to mix it with TREE')
    sys.path.insert(0, str(tree))
    from joulewise.align.apple import thermal_gates as tg
    if Path(tg.__file__).resolve() != path:
        raise DeskError(f'thermal_gates imported from {tg.__file__}, not from TREE')
    replay_path = tree / THERMAL_REPLAY_PATH
    spec = importlib.util.spec_from_file_location('jw_tree_align_r1_thermal_replay', replay_path)
    replay = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(replay)
    return tg, replay, {'tree': str(tree), 'thermal_gates_sha256': digest,
                        'thermal_replay_sha256': sha256_bytes(replay_path.read_bytes())}


def load_sibling(name):
    path = Path(__file__).resolve().with_name(name + '.py')
    spec = importlib.util.spec_from_file_location('jw_slot_desk_' + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Inputs:
    def __init__(self, root=None):
        self.root, self.files = root, {}

    def read(self, path):
        path = Path(path)
        raw = path.read_bytes()
        name = str(path.relative_to(self.root)) if self.root and Path(self.root) in path.parents else str(path)
        self.files[name] = sha256_bytes(raw)
        return raw

    def json(self, path):
        return json.loads(self.read(path))

    def listing(self):
        return [{'path': p, 'sha256': d} for p, d in sorted(self.files.items())]


# ---------------------------------------------------------------- journal access (11-12 load_member, lifted)
def base_phase(phase):
    return SUPERSEDED.sub('', phase)


def project_journal(tg, raw):
    """desk_replay.load_member's projection: readings (sensors, errors, status) and gate records."""
    raw_readings, gates, begins, start = [], [], [], None
    for line in raw.decode().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        k = r.get('kind')
        if k == 'reading':
            v = r['values']
            raw_readings.append({'module': 'temperature', 'kind': 'reading',
                                 'started': r['started'], 'finished': r['finished'],
                                 'values': {'sensors': v.get('sensors', {}), 'errors': v.get('errors', {}),
                                            'status': v.get('status', {})}})
        elif k in ('align_thermal_gate', 'align_thermal_hold'):
            v = r['values']
            if v.get('state') == 'end':
                gates.append(v['gate'])
            else:
                begins.append((k, v.get('gate_kind'), v.get('turn'), r['started']['monotonic_ns']))
        elif k == 'session_start' and start is None:
            thermal = (r.get('values') or {}).get('thermal') or {}
            start = {k2: thermal.get(k2) for k2 in ('s_fast', 's_slow', 'fan_keys', 'record_keys')}
    rows = tg.sample_rows(raw_readings)
    if not rows:
        raise DeskError('journal has no reading rows')
    off = raw_readings[0]['started']['wall_ns'] - raw_readings[0]['started']['monotonic_ns']
    return rows, gates, begins, off, start or {}


def load_member(tg, inputs, phase, bundle, path):
    rows, gates, begins, off, start = project_journal(tg, inputs.read(path))
    stages = {}
    events = bundle / 'events.jsonl'
    if events.is_file():
        for line in inputs.read(events).decode().splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            if e.get('event_type') in ('stage_started', 'stage_completed'):
                stages[(e['event_type'], e['phase'])] = e['timestamp_s']
    wref_path = bundle / 'outputs' / 'align_window_reference.json'
    wref = inputs.json(wref_path) if wref_path.is_file() else None
    cfg = inputs.json(bundle / 'config.json')
    spec = json.loads(cfg['workload_profile']['prompt_text'])
    return SimpleNamespace(seg=phase, base=base_phase(phase), bundle=bundle, path=path, kind='member',
                           attempt='superseded' if SUPERSEDED.search(phase) else 'final',
                           rows=rows, gates=gates, begins=begins, off=off, stages=stages, wref=wref,
                           thermal=spec['thermal'], policy_source='member config.json thermal',
                           condition=spec.get('condition'), session=start,
                           fin=[r['finished']['monotonic_after_ns'] for r in rows],
                           times=[r['monotonic_ns'] for r in rows])


def aux_policy(inputs, phase_dir, session, gates, fallback):
    """An auxiliary session's armed bands and caps (r1_runtime observe_policy is not journaled)."""
    sources, pol = [], {'sensors': {'s_fast': session.get('s_fast'), 's_slow': session.get('s_slow')},
                        'turn_cap_s': 300.0}
    result = {}
    rr = phase_dir / 'runtime_result.json'
    if rr.is_file():
        result = inputs.json(rr)
    bands = result.get('bands_c') if isinstance(result.get('bands_c'), dict) else {}
    for name in ('delta_fast_c', 'delta_slow_c'):
        value = result.get(name, bands.get(name))
        if type(value) in (int, float):
            pol[name] = float(value)
            sources.append(f'{name}: runtime_result.json')
        elif fallback is not None and name in fallback:
            pol[name] = float(fallback[name])
            sources.append(f'{name}: step-D member config (fallback)')
        else:
            pol[name] = 1.0
            sources.append(f'{name}: 1.0 (default; no source)')
    cap = result.get('g0_timeout_s')
    if type(cap) in (int, float):
        pol['g0_cap_s'] = float(cap)
        sources.append('g0_cap_s: runtime_result.json g0_timeout_s')
    else:
        pol['g0_cap_s'] = None
        sources.append('g0_cap_s: recorded duration (floor) for a non-released G0; 1200 s otherwise')
    return pol, '; '.join(sources)


def load_auxiliary(tg, inputs, root, path, fallback):
    rel = path.relative_to(root)
    phase = rel.parts[0]
    rows, gates, begins, off, start = project_journal(tg, inputs.read(path))
    pol, source = aux_policy(inputs, root / phase, start, gates, fallback)
    return SimpleNamespace(seg=str(rel.parent), base=base_phase(phase), phase=phase, bundle=None, path=path,
                           kind='auxiliary', attempt='auxiliary', rows=rows, gates=gates, begins=begins,
                           off=off, stages={}, wref=None, thermal=pol, policy_source=source, condition=None,
                           session=start, fin=[r['finished']['monotonic_after_ns'] for r in rows],
                           times=[r['monotonic_ns'] for r in rows])


def discover(tg, inputs, root):
    root = Path(root)
    members, aux = [], []
    member_paths = set()
    for phase_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        runs = sorted((phase_dir / 'runs').glob(f'*/outputs/{JOURNAL}')) if (phase_dir / 'runs').is_dir() else []
        if len(runs) > 1:
            raise DeskError(f'{phase_dir.name}: {len(runs)} runs with a thermal journal; exactly one per phase')
        if runs:
            member_paths.add(runs[0])
            members.append(load_member(tg, inputs, phase_dir.name, runs[0].parent.parent, runs[0]))
    if not members:
        raise DeskError(f'{root}: no <phase>/runs/<run>/outputs/{JOURNAL}')
    step_d = next((m for m in members if m.seg == STEP_D), None)
    fallback = step_d.thermal if step_d is not None else None
    for path in sorted(root.glob(f'*/**/{JOURNAL}')):
        if path in member_paths or 'runs' in path.relative_to(root).parts[1:2]:
            continue
        aux.append(load_auxiliary(tg, inputs, root, path, fallback))
    return members, aux


# ---------------------------------------------------------------- replay harness (11-12, lifted unchanged)
class Stamp:
    def __init__(self, t_ns, off_ns):
        s = t_ns / NS
        self.epoch_s = (t_ns + off_ns) / NS
        self.monotonic_before_s = s
        self.monotonic_after_s = s
        self.wall_resolution_s = 1e-6
        self.monotonic_resolution_s = 1e-9


class ReplayClock:
    def __init__(self, t_ns, off_ns):
        self.t, self.off = int(t_ns), off_ns

    def stamp(self):
        return Stamp(self.t, self.off)

    def sleep(self, d):
        self.t += max(1, round(d * NS))


class _Never:
    def is_set(self):
        return False


class StubSidecar:
    """Exposes exactly what _wait touches; the background thread is 'alive'."""
    def __init__(self, member, clock):
        self.m, self.clock = member, clock
        self._error, self._closed, self._stop, self._thread, self._seq = None, False, _Never(), object(), 0

    def snapshot(self):
        i = bisect.bisect_right(self.m.fin, self.clock.t)
        return self.m.rows[:i]

    def event(self, *_a, **_k):
        pass


def replay_wait(tg, member, kind, start_ns, *, s_fast, s_slow, reference, delta_fast=1.0, delta_slow=1.0,
                cap_s=None, turn=0):
    clock = ReplayClock(start_ns, member.off)
    s = object.__new__(tg.ThermalSession)
    s.policy = {'sensors': {'s_fast': s_fast, 's_slow': s_slow}, 'delta_fast_c': delta_fast,
                'delta_slow_c': delta_slow, 'turn_cap_s': cap_s if kind != 'G0' else 300.0,
                'g0_cap_s': cap_s if kind == 'G0' else 1200}
    s.clock, s.context, s.status_reader = clock, None, None
    s.intervals, s.events, s.flags, s.custody = [], [], [], None
    s.reference = reference if kind == 'G0' else None
    s.episode_reference = reference if kind != 'G0' else None
    s.sidecar = StubSidecar(member, clock)
    row = s._wait(kind, turn=turn)
    return {'outcome': row['outcome'], 'duration_s': row['duration_s'], 'exit_sample_ns': row['exit_sample_ns'],
            'release': row['release'], 'slope_c_per_min': row['slope_c_per_min'], 'flags': list(s.flags)}


# ---------------------------------------------------------------- row helpers
def keys_of(j):
    pol = j.thermal['sensors']
    return pol['s_fast'], pol['s_slow']


def row_at(j, t_ns):
    i = bisect.bisect_left(j.times, t_ns)
    return j.rows[i] if i < len(j.rows) and j.times[i] == t_ns else None


def at_or_before(j, t_ns):
    i = bisect.bisect_right(j.times, t_ns) - 1
    return j.rows[i] if i >= 0 else None


def value(row, key):
    if row is None:
        return None
    v = row['sensors'].get(key)
    return v if type(v) in (int, float) and math.isfinite(v) else None


def slope_at(tg, j, t_ns, key):
    """The module's slow_slope over the rows up to t_ns (exactly: rows[0] fixes Coverage's grid,
    and only rows from t - 61 s can enter the 60 s window or its coverage count)."""
    hi = bisect.bisect_right(j.times, t_ns)
    lo = bisect.bisect_left(j.times, t_ns - 61 * NS)
    subset = j.rows[:hi] if lo <= 1 else [j.rows[0]] + j.rows[lo:hi]
    return tg.slow_slope(subset, t_ns, key)


def gate_rows(j, g):
    end = g['exit_sample_ns'] if g['outcome'] == 'released' else g['end_ns']
    if end is None:
        end = g['end_ns']
    lo = bisect.bisect_left(j.times, g['start_ns'])
    hi = bisect.bisect_right(j.times, end)
    return j.rows[lo:hi]


def is_planning(j):
    return bool(PLANNING.match(j.base)) and j.kind == 'member'


def gate_cap(j, g):
    pol = j.thermal
    if g['kind'] != 'G0':
        return pol['turn_cap_s']
    cap = pol.get('g0_cap_s', 1200) if j.kind == 'member' else pol.get('g0_cap_s')
    if cap is None:
        cap = math.floor(g['duration_s']) if g['outcome'] != 'released' else 1200
    return cap


# ---------------------------------------------------------------- (a) validation
def validate(tg, journals):
    rows, fails = [], []
    for j in journals:
        pol = j.thermal
        fast, slow = keys_of(j)
        for g in j.gates:
            if g['kind'] not in ('G0', 'G1', 'H'):
                continue
            rep = replay_wait(tg, j, g['kind'], g['start_ns'], s_fast=fast, s_slow=slow, reference=g['reference'],
                              delta_fast=pol['delta_fast_c'], delta_slow=pol['delta_slow_c'],
                              cap_s=gate_cap(j, g), turn=g['turn'])
            if g['outcome'] == 'deadman':
                # The replay has no deadman; it must not release before the recorded deadman exit.
                ok = rep['outcome'] != 'released' or rep['exit_sample_ns'] > g['end_ns']
            else:
                ok = rep['outcome'] == g['outcome'] and rep['exit_sample_ns'] == g['exit_sample_ns']
            rows.append({'member': j.seg, 'journal_kind': j.kind, 'kind': g['kind'], 'turn': g['turn'],
                         'bands': [pol['delta_fast_c'], pol['delta_slow_c']], 'policy_source': j.policy_source,
                         'recorded': [g['outcome'], g['duration_s'], g['exit_sample_ns']],
                         'replayed': [rep['outcome'], rep['duration_s'], rep['exit_sample_ns']], 'agree': ok})
            if not ok:
                fails.append((j.seg, g['kind'], g['turn']))
    return {'rows': rows, 'all_agree': not fails,
            'counts': {'member': sum(1 for r in rows if r['journal_kind'] == 'member'),
                       'auxiliary': sum(1 for r in rows if r['journal_kind'] == 'auxiliary'),
                       'agree': sum(1 for r in rows if r['agree'])}}, fails


# ---------------------------------------------------------------- (b) gate table
def clause_results(tg, j, g, row, *, delta_fast, delta_slow, reference=None):
    """Per-row clause verdicts for one gate (True = holds). The status clause uses the row time."""
    fast, slow = keys_of(j)
    ref = g['reference'] if reference is None else reference
    t = row['monotonic_ns']
    vf, vs = row['sensors'].get(fast), row['sensors'].get(slow)
    out = {'valid': tg.valid_value(fast, vf) and tg.valid_value(slow, vs)}
    if out['valid']:
        out['band_fast'] = vf <= ref['fast_c'] + delta_fast
        out['band_slow'] = vs <= ref['slow_c'] + delta_slow
    if g['kind'] == 'G0':
        status = row.get('status') or {}
        pm = status.get('pm_observed_ns')
        out['status'] = (status.get('os_level') == 0 and status.get('pm_state') == 'Nominal'
                         and type(pm) is int and 0 <= t - pm <= PM_FRESH_NS)
        s = slope_at(tg, j, t, slow)
        out['slope_slow'] = s is not None and abs(s) <= SLOPE_BAR_C_PER_MIN
    return out


def last_violations(tg, j, g, rows, *, delta_fast, delta_slow, reference=None):
    clauses = CLAUSES_G0 if g['kind'] == 'G0' else CLAUSES_TURN
    last = {c: None for c in clauses}
    t2 = 0
    final = None
    for row in rows:
        res = clause_results(tg, j, g, row, delta_fast=delta_fast, delta_slow=delta_slow, reference=reference)
        final = res
        for c in clauses:
            if c in res and not res[c]:
                last[c] = (row['monotonic_ns'] - g['start_ns']) / NS
        if res['valid'] and res['band_fast'] and (g['kind'] != 'G0' or res['status']) and (
                not res['band_slow'] or (g['kind'] == 'G0' and not res['slope_slow'])):
            t2 += 1
    return last, t2, final


def clause_last_of(g, last, final):
    if g['outcome'] == 'released':
        failed = {c: v for c, v in last.items() if v is not None}
        if not failed:
            return 'none', []
        top = max(failed.values())
        ties = [c for c in CLAUSE_TIE_ORDER if failed.get(c) == top]
        return ties[0], ties if len(ties) > 1 else []
    return sorted(c for c, ok in (final or {}).items() if not ok), []


def r_fast_of(j, step_d_wref_fast):
    g0 = next((g for g in j.gates if g['kind'] == 'G0'), None)
    ref = (g0 or {}).get('reference') or {}
    fast = ref.get('fast_c')
    if type(fast) in (int, float) and fast < PLANNING_FAST_CEILING_C:
        return fast
    return step_d_wref_fast


def quiet_span_end(inputs, root, j, g, found):
    """End of the quiet span that starts at this G0's end, from the layout constant; else None."""
    if j.kind != 'member' or j.attempt != 'final' or j.base not in QUIET_SPAN_MEMBERS:
        return None, 'no quiet span after this member\'s G0 (driver quiet_s = 0)'
    path = Path(root) / j.seg / QUIET_SPAN_FILE
    if not path.is_file():
        return None, f'{QUIET_SPAN_FILE} absent'
    node = inputs.json(path)
    for key in QUIET_SPAN_FIELD:
        node = node.get(key) if isinstance(node, dict) else None
    if not (isinstance(node, list) and len(node) == 2 and all(type(x) is int for x in node)):
        return None, f'{QUIET_SPAN_FILE} has no {".".join(QUIET_SPAN_FIELD)}'
    found.append(j.seg)
    if not (g['end_ns'] <= node[0] <= node[1]):
        return None, f'quiet span {node} does not start at or after this G0 end {g["end_ns"]}'
    return node[1], 'quiet span end (prefill), ' + '.'.join(QUIET_SPAN_FIELD)


def alt_g0(tg, j, g, r_fast_c, censor_ns, censor_reason):
    fast, _ = keys_of(j)
    pol = j.thermal
    planning = is_planning(j)
    reference = {'fast_c': g['reference']['fast_c'],
                 'slow_c': g['reference']['slow_c'] if planning else r_fast_c}
    out = {'label': ALT_LABEL, 's_fast': fast, 's_slow': fast, 'reference': reference}
    if reference['slow_c'] is None:
        return {**out, 'outcome': 'censored', 'duration_s': None, 'exit_tv0h_c': None, 'exit_tf08_c': None,
                'censor_reason': 'no window reference on TV0h'}
    policy_cap = gate_cap(j, g)
    if censor_ns is None:
        censor_ns, censor_reason = g['end_ns'], 'G0 end_ns (' + censor_reason + ')'
    cap = min(policy_cap, (censor_ns - g['start_ns']) / NS)
    if cap <= 0:
        return {**out, 'outcome': 'censored', 'duration_s': 0.0, 'exit_tv0h_c': None, 'exit_tf08_c': None,
                'censor_reason': censor_reason, 'cap_s': cap}
    rep = replay_wait(tg, j, 'G0', g['start_ns'], s_fast=fast, s_slow=fast, reference=reference,
                      delta_fast=pol['delta_fast_c'], delta_slow=pol['delta_slow_c'], cap_s=cap, turn=g['turn'])
    ex = row_at(j, rep['exit_sample_ns']) if rep['exit_sample_ns'] is not None else None
    released = rep['outcome'] == 'released'
    return {**out, 'outcome': 'released' if released else 'censored', 'replay_outcome': rep['outcome'],
            'duration_s': rep['duration_s'], 'exit_sample_ns': rep['exit_sample_ns'],
            'exit_tv0h_c': value(ex, FAST_KEY), 'exit_tf08_c': value(ex, TF08), 'cap_s': cap,
            'censor_reason': None if released else (censor_reason if cap < policy_cap else 'policy cap'),
            'slope_tv0h_at_registered_exit_c_per_min': None}


def gate_table(tg, inputs, root, journals, step_d_wref_fast):
    table, mismatches, quiet_found = [], [], []
    for j in journals:
        pol = j.thermal
        fast, slow = keys_of(j)
        r_fast = r_fast_of(j, step_d_wref_fast)
        for g in j.gates:
            if g['kind'] not in ('G0', 'G1', 'H'):
                continue
            rows = gate_rows(j, g)
            exit_ns = g['exit_sample_ns']
            ex = row_at(j, exit_ns) if exit_ns is not None else None
            last, t2, final = last_violations(tg, j, g, rows, delta_fast=pol['delta_fast_c'],
                                              delta_slow=pol['delta_slow_c'])
            clause_last, ties = clause_last_of(g, last, final)
            slope_rec = g.get('slope_c_per_min')
            slope_re = slope_at(tg, j, exit_ns, slow) if exit_ns is not None else None
            tv0h_slope = slope_at(tg, j, exit_ns, fast) if exit_ns is not None else None
            mismatch = ((slope_rec is None) != (slope_re is None) or
                        (slope_rec is not None and abs(slope_rec - slope_re) > SLOPE_MISMATCH_C_PER_MIN))
            e_fast, e_slow, e_tf = value(ex, fast), value(ex, slow), value(ex, TF08)
            entry = at_or_before(j, g['start_ns'])
            row = {'member': j.seg, 'member_base': j.base, 'journal': str(Path(j.path).relative_to(root)),
                   'journal_kind': j.kind, 'attempt': j.attempt, 'kind': g['kind'], 'turn': g['turn'],
                   'outcome': g['outcome'], 'duration_s': g['duration_s'], 'start_ns': g['start_ns'],
                   'end_ns': g['end_ns'], 'exit_sample_ns': exit_ns,
                   'planning_turn': is_planning(j), 'gated_d': j.base in GATED_D_RUNS and j.kind == 'member',
                   'x_g': j.base == X_G and j.kind == 'member', 's_fast': fast, 's_slow': slow,
                   'bands': [pol['delta_fast_c'], pol['delta_slow_c']],
                   'reference_fast_c': g['reference']['fast_c'], 'reference_slow_c': g['reference']['slow_c'],
                   'r_fast_c': r_fast, 'exit_tv0h_c': e_fast, 'exit_tvh0_c': e_slow, 'exit_tf08_c': e_tf,
                   'tv0h_minus_r_fast_c': (e_fast - r_fast) if e_fast is not None and r_fast is not None else None,
                   'tv0h_slope_c_per_min': tv0h_slope,
                   'slow_slope_recorded': slope_rec, 'slow_slope_recomputed': slope_re,
                   'slope_recompute_mismatch': mismatch,
                   'on_step_at_exit': (e_slow != e_fast) if e_fast is not None and e_slow is not None else None,
                   'last_violation_s': last, 'clause_last': clause_last, 'clause_last_ties': ties,
                   't2_samples': t2, 'tf08_entry_c': value(entry, TF08),
                   'd_tv0h_minus_tvh0_at_exit_c': (e_fast - e_slow) if e_fast is not None and e_slow is not None
                   else None}
            if mismatch:
                mismatches.append({k: row[k] for k in ('member', 'kind', 'turn', 'slow_slope_recorded',
                                                       'slow_slope_recomputed')})
            if g['kind'] == 'G0':
                censor_ns, reason = quiet_span_end(inputs, root, j, g, quiet_found)
                row['alt'] = alt_g0(tg, j, g, r_fast, censor_ns, reason)
                row['alt']['slope_tv0h_at_registered_exit_c_per_min'] = tv0h_slope
            table.append(row)
    present = [j.seg for j in journals if j.kind == 'member' and j.attempt == 'final' and j.base in QUIET_SPAN_MEMBERS
               and any(g['kind'] == 'G0' for g in j.gates)]
    if present and not quiet_found:
        raise DeskError(f'layout assumption not confirmed: no member of {list(present)} has '
                        f'{QUIET_SPAN_FILE}:{".".join(QUIET_SPAN_FIELD)} (QUIET_SPAN_FILE / QUIET_SPAN_FIELD in '
                        f'{Path(__file__).name}); confirm the quiet-span field in step 0')
    return table, mismatches


# ---------------------------------------------------------------- (d) U2
def u2_pair(table):
    u = [r for r in table if r['kind'] == 'G0' and r['attempt'] == 'final' and r['outcome'] == 'released'
         and not r['planning_turn'] and r['journal_kind'] == 'member']

    def span(field):
        values = [r[field] for r in u if r[field] is not None]
        return (max(values) - min(values)) if values else None
    return {'members': sorted(r['member'] for r in u), 'registered_tvh0_c': span('exit_tvh0_c'),
            'registered_key': sorted({r['s_slow'] for r in u}), 'tv0h_c': span('exit_tv0h_c'),
            'tf08_release_range_c': span('exit_tf08_c'), 'bar_c': T3_BAR_C,
            'values': [{k: r[k] for k in ('member', 'exit_tv0h_c', 'exit_tvh0_c', 'exit_tf08_c')}
                       for r in sorted(u, key=lambda r: r['member'])]}


# ---------------------------------------------------------------- (e) floor census
def classify_census_row(tv0h, tvh0, lo, hi):
    if tvh0 == tv0h:
        return 'equal'
    if tvh0 == FLOOR_STEP_C * math.floor(tv0h / FLOOR_STEP_C):
        return 'floored'
    multiple = tvh0 % FLOOR_STEP_C == 0
    if (multiple and FLOOR_STEP_C * math.floor(lo / FLOOR_STEP_C) <= tvh0 <= FLOOR_STEP_C * math.floor(hi / FLOOR_STEP_C)) \
            or (lo - SKEW_SLACK_C <= tvh0 <= hi + SKEW_SLACK_C):
        return 'skew'
    return 'unexplained'


def _valid(key, row):
    v = row['sensors'].get(key)
    return (key not in (row.get('errors') or {}) and type(v) in (int, float) and math.isfinite(v)
            and -40 <= v <= 150)


def census_rows(rows, *, stage_of=None, fan_keys=()):
    """rows: dicts with monotonic_ns, sensors, errors, status (time-ordered). Returns classified rows."""
    out = []
    times = [r['monotonic_ns'] for r in rows]
    for i, r in enumerate(rows):
        if not (_valid(FAST_KEY, r) and _valid(SLOW_KEY, r)):
            continue
        t = r['monotonic_ns']
        tv0h, tvh0 = r['sensors'][FAST_KEY], r['sensors'][SLOW_KEY]
        near = [tv0h]
        for k in (i - 1, i + 1):
            if 0 <= k < len(rows) and abs(rows[k]['monotonic_ns'] - t) <= SKEW_NEIGHBOUR_NS and _valid(FAST_KEY, rows[k]):
                near.append(rows[k]['sensors'][FAST_KEY])
        cls = classify_census_row(tv0h, tvh0, min(near), max(near))
        j = bisect.bisect_right(times, t - 10 * NS) - 1
        trend = 'unknown'
        if j >= 0 and t - times[j] <= 12 * NS and _valid(FAST_KEY, rows[j]):
            d = tv0h - rows[j]['sensors'][FAST_KEY]
            trend = 'rising' if d > 0.05 else 'falling' if d < -0.05 else 'flat'
        fans = [r['sensors'].get(k) for k in fan_keys if type(r['sensors'].get(k)) in (int, float)]
        status = r.get('status') or {}
        out.append({'t': t, 'tv0h': tv0h, 'tvh0': tvh0, 'class': cls, 'trend': trend,
                    'stage': stage_of(t) if stage_of else None, 'fan': sum(fans) / len(fans) if fans else None,
                    'pm': f"{status.get('pm_state')}/{status.get('os_level')}"})
    return out


def census_counts(classified):
    counts = {'equal': 0, 'floored': 0, 'skew': 0, 'unexplained': 0}
    for c in classified:
        counts[c['class']] += 1
    diffs = [c['tvh0'] - c['tv0h'] for c in classified]
    n = len(classified)
    return {**counts, 'rows': n, 'tvh0_above_tv0h': sum(1 for d in diffs if d > 0),
            'floored_below_35': sum(1 for c in classified if c['class'] == 'floored' and c['tv0h'] < FLOORED_LOW_C),
            'skew_fraction': counts['skew'] / n if n else None,
            'max_diff_c': max(diffs) if diffs else None, 'min_diff_c': min(diffs) if diffs else None}


def tv0h_bin(v):
    return '<35' if v < 35 else '35-40' if v < 40 else '40-45' if v < 45 else '>=45'


def census_conditions(classified):
    dims = {'tv0h_bin': lambda c: tv0h_bin(c['tv0h']), 'trend': lambda c: c['trend'],
            'stage': lambda c: c['stage'] or 'unstaged', 'pm_state/os_level': lambda c: c['pm']}
    fans = sorted(c['fan'] for c in classified if c['fan'] is not None)
    if fans:
        a, b = fans[len(fans) // 3], fans[(2 * len(fans)) // 3]
        dims['fan_tercile'] = lambda c: ('none' if c['fan'] is None else 'low' if c['fan'] < a
                                         else 'mid' if c['fan'] < b else 'high')
    out = {}
    for name, fn in dims.items():
        bins = {}
        for c in classified:
            b = bins.setdefault(fn(c), {'rows': 0, 'floored': 0})
            b['rows'] += 1
            b['floored'] += c['class'] == 'floored'
        for b in bins.values():
            b['floored_share'] = b['floored'] / b['rows'] if b['rows'] else None
        out[name] = dict(sorted(bins.items()))
    if fans:
        out['fan_tercile_cuts'] = [a, b]
    return out


def stage_function(j):
    if j.kind != 'member':
        return lambda t: 'auxiliary'
    marks = sorted((round(ts * NS) - j.off, phase) for (ev, phase), ts in j.stages.items()
                   if ev == 'stage_started' and phase in ('idle_baseline', 'warmup', 'measured_run'))
    stamps = [m[0] for m in marks]

    def stage(t):
        i = bisect.bisect_right(stamps, t) - 1
        return marks[i][1] if i >= 0 else 'before_idle_baseline'
    return stage


def floor_census(journals):
    by_journal, everything = {}, []
    skipped = []
    for j in journals:
        keys = set()
        for r in j.rows:
            keys |= set(r['sensors'])
        if not {FAST_KEY, SLOW_KEY} <= keys:
            skipped.append(j.seg)
            continue
        classified = census_rows(j.rows, stage_of=stage_function(j), fan_keys=tuple(j.session.get('fan_keys') or ()))
        by_journal[j.seg] = census_counts(classified)
        everything += classified
    if not by_journal:
        return {'status': f'not applicable: {SLOW_KEY} not journaled', 'total': None, 'by_journal': {},
                'conditions': {}, 'journals_without_both_keys': sorted(skipped)}
    return {'status': 'computed', 'total': census_counts(everything), 'by_journal': dict(sorted(by_journal.items())),
            'conditions': census_conditions(everything), 'journals_without_both_keys': sorted(skipped),
            'offending_rows': [{'journal_t_ns': c['t'], 'tv0h': c['tv0h'], 'tvh0': c['tvh0'], 'class': c['class']}
                               for c in everything if c['class'] == 'unexplained' or c['tvh0'] > c['tv0h']
                               or (c['class'] == 'floored' and c['tv0h'] < FLOORED_LOW_C)][:200]}


def census_journal_file(path, classification=None):
    """Census of one journal (e.g. step-D inventory/inventory_journal.jsonl), optionally split by phase."""
    inputs = Inputs()
    rows = []
    for line in inputs.read(path).decode().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        v = r.get('values') or {}
        if r.get('kind') in ('session_start', 'session_end', 'align_thermal_gate', 'align_thermal_hold'):
            continue
        if not isinstance(v.get('sensors'), dict) or 'started' not in r:
            continue
        rows.append({'monotonic_ns': r['started']['monotonic_ns'],
                     'sensors': {k: v['sensors'].get(k) for k in (FAST_KEY, SLOW_KEY)},
                     'errors': {k: e for k, e in (v.get('errors') or {}).items() if k in (FAST_KEY, SLOW_KEY)},
                     'status': v.get('status') if isinstance(v.get('status'), dict) else {}})
    rows.sort(key=lambda r: r['monotonic_ns'])
    classified = census_rows(rows)
    out = {'schema': SCHEMA + '#census', 'journal': str(path), 'total': census_counts(classified),
           'conditions': census_conditions(classified)}
    if classification is not None:
        bounds = inputs.json(classification)['classification']['phase_bounds_ns']
        first = rows[0]['monotonic_ns'] if rows else 0
        spans = [('pre_quiet', (first, bounds['quiet'][0]))] + [(n, tuple(bounds[n])) for n in
                                                                ('quiet', 'load', 'recovery') if n in bounds]
        out['by_phase'] = {n: census_counts([c for c in classified if a <= c['t'] < b]) for n, (a, b) in spans}
    out['inputs'] = inputs.listing()
    return out


# ---------------------------------------------------------------- (f) S6
def s6_block(tg, journals, table, driver_g1_median, force):
    by_seg = {j.seg: j for j in journals}
    finals = [r for r in table if r['attempt'] == 'final' and r['journal_kind'] == 'member']
    g = [r for r in finals if r['gated_d'] and r['kind'] == 'G1']
    h = [r for r in finals if r['gated_d'] and r['kind'] == 'H']
    xg = [r for r in finals if r['x_g'] and r['kind'] in ('G1', 'H')]
    g1_median = median(r['duration_s'] for r in g)
    out = {'g1_waits': [{k: r[k] for k in ('member', 'turn', 'duration_s', 'outcome')} for r in g],
           'h_waits': [{k: r[k] for k in ('member', 'turn', 'duration_s', 'outcome')} for r in h],
           'x_g_waits': [{k: r[k] for k in ('member', 'kind', 'turn', 'duration_s', 'outcome')} for r in xg],
           'g1_median_s': g1_median, 'h_median_s': median(r['duration_s'] for r in h),
           'driver_g1_median_s': driver_g1_median, 'median_bar_s': S6_MEDIAN_BAR_S,
           'replays': {}, 'g1_median_at': {}, 's6_reachable_step_c': None,
           'replay_ran': False, 'replay_reason': None}
    if g1_median is None:
        out['replay_reason'] = 'no G1 wait in the gated D runs'
        return out
    if not (g1_median > S6_MEDIAN_BAR_S or force):
        out['replay_reason'] = 'g1_median_s <= 90: S6 rule not engaged'
        return out
    out['replay_ran'] = True
    out['replay_reason'] = 'g1_median_s > 90' if g1_median > S6_MEDIAN_BAR_S else '--force-s6-replay (D2 packet)'
    for step in S6_STEPS_C:
        rows = []
        for r in g + h + xg:
            j = by_seg[r['member']]
            fast, slow = keys_of(j)
            gate = next(x for x in j.gates if x['kind'] == r['kind'] and x['turn'] == r['turn']
                        and x['start_ns'] == r['start_ns'])
            rep = replay_wait(tg, j, gate['kind'], gate['start_ns'], s_fast=fast, s_slow=slow,
                              reference=gate['reference'], delta_fast=j.thermal['delta_fast_c'], delta_slow=step,
                              cap_s=S6_REPLAY_CAP_S, turn=gate['turn'])
            end = rep['exit_sample_ns'] if rep['exit_sample_ns'] is not None else gate['start_ns']
            span = j.rows[bisect.bisect_left(j.times, gate['start_ns']):bisect.bisect_right(j.times, end)]
            last, _, _ = last_violations(tg, j, gate, span, delta_fast=j.thermal['delta_fast_c'], delta_slow=step)
            bands = {c: last[c] for c in ('band_fast', 'band_slow') if last.get(c) is not None}
            rows.append({'member': r['member'], 'kind': r['kind'], 'turn': r['turn'], 'in_median': r in g,
                         'outcome': rep['outcome'], 'duration_s': rep['duration_s'],
                         'last_out_of_band_key': max(bands, key=bands.get) if bands else None,
                         'last_out_of_band_s': bands})
        out['replays'][str(step)] = rows
        out['g1_median_at'][str(step)] = median(x['duration_s'] for x in rows if x['in_median'])
    if g1_median > S6_MEDIAN_BAR_S:
        out['s6_reachable_step_c'] = next((s for s in S6_STEPS_C if out['g1_median_at'][str(s)] <= S6_MEDIAN_BAR_S),
                                          None)
    return out


# ---------------------------------------------------------------- (g) start state
def start_state(tg, replay, ssd, inputs, root, members, table, step_d_wref_fast, u2):
    """Per final member with a sidecar; Tf08 derived as night_desk derives it (TREE's own module)."""
    window_ref, rows = None, []
    for j in members:
        if j.attempt != 'final':
            continue
        journal = replay.read_journal(j.path, extra_fields=(TF08,))
        session = replay.Session(journal['rows'], journal['s_fast'], journal['s_slow'])
        anchor = replay.warmup_anchor(j.bundle, session)
        tf_ref = session.good_window(anchor, (TF08,), session.visible(anchor))
        tf_cov = session.coverage(anchor, (TF08,), session.visible(anchor))
        tf_pre = (_median(r['sensors'][TF08] for r in tf_ref) if tf_ref and tf_cov is not None and tf_cov >= .9
                  else None)
        if j.seg == STEP_D:
            window_ref = tf_pre
        measured = None
        if journal['g0']:
            start_ns, definition = journal['g0'][0].get('exit_sample_ns'), 'G0 exit sample'
        else:
            definition = 'measured-run entry'
            for line in (j.bundle / 'events.jsonl').read_text().splitlines():
                e = json.loads(line)
                if e.get('event_type') == 'stage_started' and e.get('phase') == 'measured_run':
                    measured = e
                    break
            start_ns = session.mono_from_epoch(measured['timestamp_s']) if measured else None
        at = [r for r in journal['rows'] if start_ns is not None and 0 <= start_ns - r['monotonic_ns'] <= 2 * NS
              and TF08 not in r['errors'] and replay.valid_value(TF08, r['sensors'].get(TF08))]
        start_row = at[-1] if at else None
        r_fast = r_fast_of(j, step_d_wref_fast)
        tv0h = value(row_at(j, start_row['monotonic_ns']), FAST_KEY) if start_row else None
        rows.append({'member': j.seg, 'condition': j.condition, 'start_definition': definition,
                     'start_ns': start_row['monotonic_ns'] if start_row else None,
                     'tf08_pre_warmup_c': tf_pre,
                     'tf08_start_c': start_row['sensors'][TF08] if start_row else None,
                     'tv0h_slope_c_per_min': slope_at(tg, j, start_row['monotonic_ns'], FAST_KEY) if start_row else None,
                     'tv0h_minus_r_fast_c': tv0h - r_fast if tv0h is not None and r_fast is not None else None})
    return ssd.start_state_disclosure(rows, window_ref, u2_tv0h_c=u2['tv0h_c'],
                                      tf08_release_range_c=u2['tf08_release_range_c'], window='R1 session')


def tf08_check(disclosure, kit_desk):
    if kit_desk is None:
        return None, 'not checked: no --kit-desk (E1 refused or not supplied)'
    kit = {m['member']: m.get('Tf08_start_excess_c') for m in kit_desk.get('members', [])}
    ours = {m['member']: m['tf08_excess_c'] for m in disclosure['members']}
    bad = []
    for name in sorted(set(kit) | set(ours)):
        a, b = ours.get(name), kit.get(name)
        if name not in ours and b is None:
            continue          # E1 lists members with no thermal journal; nothing to compare
        if (a is None) != (b is None) or (a is not None and abs(a - b) > 1e-9):
            bad.append({'member': name, 'desk': a, 'kit_desk': b})
    return not bad, bad


# ---------------------------------------------------------------- (h) schedule
def schedule(members):
    out = []
    for j in members:
        if j.attempt != 'final' or j.seg not in SCHEDULE_MEMBERS:
            continue
        fast, slow = keys_of(j)
        w = j.stages.get(('stage_started', 'warmup'))
        rw = at_or_before(j, round(w * NS) - j.off) if w is not None else None
        g0 = next((g for g in j.gates if g['kind'] == 'G0'), None)
        rg = at_or_before(j, g0['start_ns']) if g0 else None
        out.append({'member': j.seg, 'keys': [fast, slow, TF08],
                    'warmup_entry': None if rw is None else [value(rw, k) for k in (fast, slow, TF08)],
                    'g0_entry': None if rg is None else [value(rg, k) for k in (fast, slow, TF08)]})
    return sorted(out, key=lambda r: SCHEDULE_MEMBERS.index(r['member']))


# ---------------------------------------------------------------- triggers
def triggers(table, census, u2, duty):
    total = census.get('total')
    if total is None:
        t1 = {'fired': None, 'reasons': [census['status']]}
    else:
        reasons = []
        if total['tvh0_above_tv0h'] > 0:
            reasons.append(f"{total['tvh0_above_tv0h']} row(s) with TVh0 > TV0h")
        if total['unexplained'] > 0:
            reasons.append(f"{total['unexplained']} unexplained row(s)")
        if total['floored_below_35'] > 0:
            reasons.append(f"{total['floored_below_35']} floored row(s) with TV0h < 35.0")
        if total['skew_fraction'] is not None and total['skew_fraction'] > T1_SKEW_FRACTION:
            reasons.append(f"skew fraction {total['skew_fraction']:.4f} > {T1_SKEW_FRACTION}")
        t1 = {'fired': bool(reasons), 'reasons': reasons}
    candidates = []
    for r in table:
        verdict = duty.get(r['member_base']) if r['attempt'] == 'final' else None
        if r['t2_samples'] > 0 and (r['outcome'] == 'timeout' or verdict == 'fail'):
            candidates.append({'member': r['member'], 'member_base': r['member_base'], 'attempt': r['attempt'],
                               'kind': r['kind'], 'turn': r['turn'], 'outcome': r['outcome'],
                               't2_samples': r['t2_samples'], 'duty_verdict': verdict,
                               'planning_turn': r['planning_turn']})
    t2 = {'fired': bool(candidates), 'gates': candidates,
          'note': 'before the planning exclusion of RL-135 item 1; B4 applies it with out/3a.json'}
    u = u2['tv0h_c']
    t3 = {'fired': None if u is None else u > T3_BAR_C, 'u2_tv0h_c': u, 'bar_c': T3_BAR_C}
    return {'T1': t1, 'T2': t2, 'T3': t3}


def record_fields(record):
    if record is None:
        return {}, None
    duty = {r['run']: r['verdict'] for r in (record.get('duty') or {}).get('runs') or []}
    s6 = record.get('s6') or {}
    return duty, s6.get('G1_median_s')


# ---------------------------------------------------------------- desk
def desk(tg, replay, ssd, tree_info, run_dir, *, record=None, kit_desk=None, force_s6=False, inputs=None,
         tree_commit=NIGHT_COMMIT):
    root = Path(run_dir)
    inputs = inputs or Inputs(root)
    members, aux = discover(tg, inputs, root)
    journals = members + aux
    validation, fails = validate(tg, journals)
    out = {'schema': SCHEMA, 'night': root.name, 'tree_commit': tree_commit, **{
        'thermal_gates_sha256': tree_info['thermal_gates_sha256'],
        'thermal_replay_sha256': tree_info.get('thermal_replay_sha256')}, 'validation': validation}
    if fails:
        out['inputs'] = inputs.listing()
        raise ValidationFailedWith(out, fails)
    step_d = next((m for m in members if m.seg == STEP_D), None)
    step_d_wref_fast = (step_d.wref or {}).get('fast_c') if step_d else None
    table, mismatches = gate_table(tg, inputs, root, journals, step_d_wref_fast)
    u2 = u2_pair(table)
    census = floor_census(journals)
    duty, driver_g1 = record_fields(record)
    s6 = s6_block(tg, journals, table, driver_g1, force_s6)
    s6_agrees = (None if driver_g1 is None or s6['g1_median_s'] is None
                 else abs(s6['g1_median_s'] - driver_g1) <= 1e-6)
    disclosure = start_state(tg, replay, ssd, inputs, root, members, table, step_d_wref_fast, u2)
    tf_ok, tf_bad = tf08_check(disclosure, kit_desk)
    out.update(gates=table, u2=u2, floor_census=census, s6=s6, start_state=disclosure, schedule=schedule(members),
               triggers=triggers(table, census, u2, duty),
               tool_checks={'slope_recompute_mismatch': mismatches,
                            's6_median_agrees': s6_agrees,
                            'tf08_excess_agrees': tf_ok,
                            'tf08_excess_disagreements': tf_bad},
               policy_sources={j.seg: j.policy_source for j in journals},
               layout={'quiet_span': f'{QUIET_SPAN_FILE}:{".".join(QUIET_SPAN_FIELD)}'})
    out['inputs'] = inputs.listing()
    return out


class ValidationFailedWith(ValidationFailed):
    def __init__(self, partial, fails):
        super().__init__(f'VALIDATION FAILED: module replay does not reproduce the night: {fails}')
        self.partial = partial


# ---------------------------------------------------------------- text render
def _f(v, fmt='{:.3f}'):
    return '-' if v is None else fmt.format(v)


def render(out):
    lines = [f"R1 slot gate desk: night {out['night']}; tree {out['tree_commit'][:9]}; thermal_gates "
             f"{out['thermal_gates_sha256'][:8]}...",
             'validation: %d of %d agree (member %d, auxiliary %d)' % (
                 out['validation']['counts']['agree'], len(out['validation']['rows']),
                 out['validation']['counts']['member'], out['validation']['counts']['auxiliary']), '',
             'GATE TABLE (RL-131 2.3; RL-90)',
             'member | attempt | kind | turn | outcome | dur_s | ref_f/ref_s | exit fast/slow/Tf08 | fast-R_f | '
             'slope fast | slope slow rec/re | on_step | clause_last | last_violation_s | t2 | Tf08 entry']
    for r in out['gates']:
        lv = ' '.join(f'{k}={_f(v, "{:.1f}")}' for k, v in r['last_violation_s'].items() if v is not None)
        lines.append(' | '.join([
            r['member'], r['attempt'], r['kind'], str(r['turn']), r['outcome'], _f(r['duration_s'], '{:.2f}'),
            f"{_f(r['reference_fast_c'])}/{_f(r['reference_slow_c'])}",
            f"{_f(r['exit_tv0h_c'])}/{_f(r['exit_tvh0_c'])}/{_f(r['exit_tf08_c'])}",
            _f(r['tv0h_minus_r_fast_c'], '{:+.3f}'), _f(r['tv0h_slope_c_per_min'], '{:+.3f}'),
            f"{_f(r['slow_slope_recorded'], '{:+.3f}')}/{_f(r['slow_slope_recomputed'], '{:+.3f}')}"
            + (' MISMATCH' if r['slope_recompute_mismatch'] else ''),
            str(r['on_step_at_exit']), str(r['clause_last']) + (f" (ties {r['clause_last_ties']})"
                                                                 if r['clause_last_ties'] else ''),
            lv or '-', str(r['t2_samples']), _f(r['tf08_entry_c'])]))
        if 'alt' in r:
            a = r['alt']
            lines.append(f"    alt G0 [{a['label']}]: {a['outcome']} {_f(a['duration_s'], '{:.1f}')} s, TV0h "
                         f"{_f(a['exit_tv0h_c'])}, Tf08 {_f(a['exit_tf08_c'])}"
                         + (f"; censored: {a['censor_reason']}" if a['outcome'] == 'censored' else ''))
    u = out['u2']
    lines += ['', f"U2 (T3): members {u['members']}", f"  registered ({','.join(u['registered_key'])}) "
              f"{_f(u['registered_tvh0_c'])} C; TV0h {_f(u['tv0h_c'])} C (bar {u['bar_c']}); Tf08 release range "
              f"{_f(u['tf08_release_range_c'])} C (no bar)"]
    c = out['floor_census']
    lines += ['', f"FLOOR CENSUS (T1): {c['status']}"]
    if c['total']:
        t = c['total']
        lines.append(f"  total rows {t['rows']}: equal {t['equal']}, floored {t['floored']}, skew {t['skew']}, "
                     f"unexplained {t['unexplained']}; TVh0>TV0h {t['tvh0_above_tv0h']}; floored<35 "
                     f"{t['floored_below_35']}; skew fraction {_f(t['skew_fraction'], '{:.4f}')}; diff range "
                     f"{_f(t['min_diff_c'])}..{_f(t['max_diff_c'])}")
        for name, t in c['by_journal'].items():
            lines.append(f"  {name}: rows {t['rows']} equal {t['equal']} floored {t['floored']} skew {t['skew']} "
                         f"unexplained {t['unexplained']} above {t['tvh0_above_tv0h']} floored<35 "
                         f"{t['floored_below_35']}")
        for dim, bins in c['conditions'].items():
            if dim == 'fan_tercile_cuts':
                continue
            lines.append(f"  floored share by {dim}: " + ', '.join(
                f"{k} {v['floored']}/{v['rows']}" for k, v in bins.items()))
    s = out['s6']
    lines += ['', f"S6: G1 median {_f(s['g1_median_s'], '{:.2f}')} s (driver {_f(s['driver_g1_median_s'], '{:.2f}')});"
              f" H median {_f(s['h_median_s'], '{:.2f}')} s; replay: {s['replay_reason']}"]
    for step, rows in s['replays'].items():
        lines.append(f"  delta_slow {step}: median {_f(s['g1_median_at'].get(step), '{:.2f}')} s; " + '; '.join(
            f"{x['member']} {x['kind']}{x['turn']} {x['outcome']} {_f(x['duration_s'], '{:.0f}')} s last "
            f"{x['last_out_of_band_key']}" for x in rows))
    lines.append(f"  s6_reachable_step_c: {s['s6_reachable_step_c']}")
    d = out['start_state']
    lines += ['', f"START STATE (disclosure): window Tf08 reference {_f(d['window_tf08_reference_c'])} C"]
    for m in d['members']:
        lines.append(f"  {m['member']} [{m['condition']}] {m['start_definition']}: Tf08 excess "
                     f"{_f(m['tf08_excess_c'], '{:+.3f}')}, TV0h slope {_f(m['tv0h_slope_c_per_min'], '{:+.3f}')}, "
                     f"TV0h-R_f {_f(m['tv0h_minus_r_fast_c'], '{:+.3f}')}")
    for diff in d['differences']:
        lines.append(f"  {diff['condition_a']} - {diff['condition_b']}: " + ', '.join(
            f"{k} {_f(v, '{:+.3f}')}" for k, v in diff.items() if k.endswith('_a_minus_b')))
    lines += ['', 'SCHEDULE (RL-119 print 4): member: warmup entry / G0 entry']
    for r in out['schedule']:
        lines.append(f"  {r['member']} {r['keys']}: {r['warmup_entry']} / {r['g0_entry']}")
    tr = out['triggers']
    lines += ['', 'TRIGGERS', f"  T1 fired {tr['T1']['fired']}: {tr['T1']['reasons']}",
              f"  T2 fired (before planning exclusion) {tr['T2']['fired']}: " + '; '.join(
                  f"{g['member']} {g['kind']}{g['turn']} {g['outcome']} t2={g['t2_samples']} duty={g['duty_verdict']}"
                  for g in tr['T2']['gates']),
              f"  T3 fired {tr['T3']['fired']}: u2_tv0h_c {_f(tr['T3']['u2_tv0h_c'])}"]
    tc = out['tool_checks']
    lines += ['TOOL CHECKS', f"  slope_recompute_mismatch: {len(tc['slope_recompute_mismatch'])}",
              f"  s6_median_agrees: {tc['s6_median_agrees']}",
              f"  tf08_excess_agrees: {tc['tf08_excess_agrees']}"]
    return '\n'.join(lines)


# ---------------------------------------------------------------- CLI
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('tree', nargs='?', type=Path)
    parser.add_argument('run_dir', nargs='?', type=Path)
    parser.add_argument('--record', type=Path)
    parser.add_argument('--kit-desk', type=Path)
    parser.add_argument('--tree-commit', default=NIGHT_COMMIT,
                        help='the commit TREE was archived from (recorded; step 0 uses 99622e96c)')
    parser.add_argument('--force-s6-replay', action='store_true',
                        help='run the S6 replays at 1.5 and 2.0 C even when the G1 median is <= 90 s (D2 packet)')
    parser.add_argument('--census-journal', type=Path)
    parser.add_argument('--classification', type=Path)
    parser.add_argument('--json-out', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.census_journal is not None:
            out = census_journal_file(args.census_journal, args.classification)
            args.json_out.write_text(json.dumps(out, indent=1, sort_keys=True) + '\n')
            print(json.dumps(out['total'], sort_keys=True))
            for name, t in (out.get('by_phase') or {}).items():
                print(name, json.dumps(t, sort_keys=True))
            return 0
        if args.tree is None or args.run_dir is None:
            parser.error('TREE and RUN_DIR are required')
        tg, replay, info = load_tree(args.tree)
        ssd = load_sibling('align_start_state_disclosure')
        inputs = Inputs(args.run_dir.resolve())
        record = inputs.json(args.record) if args.record else None
        kit = inputs.json(args.kit_desk) if args.kit_desk else None
        out = desk(tg, replay, ssd, info, args.run_dir.resolve(), record=record, kit_desk=kit,
                   force_s6=args.force_s6_replay, inputs=inputs, tree_commit=args.tree_commit)
    except ValidationFailedWith as error:
        args.json_out.write_text(json.dumps(error.partial, indent=1, sort_keys=True) + '\n')
        print(str(error), file=sys.stderr)
        return 1
    except (DeskError, OSError, KeyError, ValueError) as error:
        print(f'gate desk: {type(error).__name__}: {error}', file=sys.stderr)
        return 2
    args.json_out.write_text(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print(render(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
