"""Two-tier phase timers for the block-5 analysis driver (D-188 TIMERS lane).

A run explains its own runtime without changing a byte of what it decides or
records. The timers read only clocks, ``getrusage``, ``getloadavg`` and the
code objects of the sampled thread's frames; they never read an argument
value (other than a program's closed ``argv[0]`` sub-command), a local, or a
file. No ``sys.monitoring`` tool id is taken, so the calibration wall-deadline
observer keeps its id and its firings. Nothing is wrapped or replaced: every
hook is an explicit call from unpinned driver code.

Two tiers (lead ruling for this build, within D-188):

STRUCTURE (outside custody, ``scripts/run_b5_analysis.py --phase-log PATH``):
    step-level integer wall seconds only. Schema ``joulewise.b5_phase_timing.v1``,
    one canonical JSON object per line, closed keys per event:

        run_start   {event, schema, mode}
        step_begin  {event, step, elapsed_s}
        heartbeat   {event, step, step_s, elapsed_s}   (every JOULEWISE_B5_PHASE_HEARTBEAT_S, default 300)
        step_end    {event, step, wall_s}
        run_end     {event, total_s}
        step_retry  {event, step, attempt}             (lane b5-robust: a serial rerun of the step)
        run_resume  {event, step}                      (lane b5-robust: first step of a resumed run)

    No label, phase, program, pool or count column ever reaches this tier;
    ``validate_phase_line`` refuses any other key or value before a write.

RESTRICTED (``<custody>/<mode dir>/restricted/logs/runtime-phases.jsonl``):
    everything at millisecond resolution: driver CPU, driver-serial time
    (wall minus exact pool and dispatch waits), RSS, load, per-program wall and
    CPU, per-pool batches (busy, CPU, max task), sampled self and inclusive
    time per closed label for the driver, child and member groups, a sampled
    per-qualname histogram (a crude built-in profiler), heartbeats naming the
    innermost label and current program, and a SIGUSR1 stack dump to
    ``restricted/logs/runtime-stack-<pid>.txt``.

Failure model: every hook catches its own ``Exception``. A raising clock,
sampler or frame walk switches the timer off; a sink write error or a line
that fails validation switches that sink off. No path ever refuses, prints,
or changes a status, a refusal or its serial position.

API contract (all no-ops unless a timer is active in this process; SHIP and
the leaf lanes code against these names):

    session(structure_fd=None, *, mode=None)     context manager: activate a timer
                                                 (nested call: no-op, yields the active one)
    attach_restricted(restricted)                driver, after restricted.mkdir()
    step_begin(step) / step_end(step)            driver, around each registered step
    run_end()                                    driver, after the record write (idempotent)
    program_span(main, argv)                     context manager inside StepRunner.run's body
    span(label)                                  context manager; label from SPAN_LABELS
    pool_wait() / dispatch_wait()                context managers around a result loop
    pool_progress(done, total)                   restricted heartbeat progress only
    pool_batch(reference, costs, wall_ns, pool_size)   driver, after a member/child batch; costs is a
                                                 list or tuple of task_cost dicts (anything else
                                                 counts as no tasks and is never iterated)
    enabled()                                    True when a timer is active (sets *.timing)
    task_cost(enabled)                           context manager in a worker; yields a dict or None
    child_session(enabled)                       context manager around a child program
    child_table()                                the last child session's table (picklable) or None
    merge_child(table)                           driver, per ChildResult.timing
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
import time

SCHEMA = 'joulewise.b5_phase_timing.v1'
RESTRICTED_SCHEMA = 'joulewise.b5_phase_timing.restricted.v1'
RESTRICTED_LOG = 'runtime-phases.jsonl'
STACK_LOG = 'runtime-stack-{pid}.txt'
SAMPLE_ENV = 'JOULEWISE_B5_PHASE_SAMPLE_MS'
HEARTBEAT_ENV = 'JOULEWISE_B5_PHASE_HEARTBEAT_S'
DEFAULT_SAMPLE_MS = 1000
DEFAULT_HEARTBEAT_S = 300

STEP_IDS = ('0', '1', '2', '3', '3b', '4', '5', '8', '6', '9', '9b', '10', '11')
MODES = ('blind-dry-run', 'release')

# (module, qualname, label, count_policy). Resolved lazily, only from modules
# already imported, with __wrapped__ unwrapped. count_policy 'plan' marks the
# sites whose member counts are fixed by the plan; under the lead ruling no
# count reaches the structure tier, so it only annotates the restricted tier.
# The blinding owner signs off on this tuple.
LABELS = (
    ('joulewise.cli', '_strict_problems', 'k.strict', 'none'),
    ('joulewise.cli', 'validate_bundle', 'k.strict.bundle', 'none'),
    ('joulewise.reduce', '_reduce', 'k.reduce', 'none'),
    ('joulewise.uncertainty_evidence', 'derive_powermetrics_anchor_v3', 'k.anchor', 'none'),
    ('joulewise.environment_admission', 'current_environment_refusals', 'k.env', 'none'),
    ('joulewise.adapters.powermetrics', '_powermetrics_documents', 'k.pm_parse', 'none'),
    ('joulewise.powermetrics_fiducial', 'detect_pulses', 'k.detect', 'none'),
    ('joulewise.powermetrics_fiducial', 'verify_stored_evidence_physics', 'k.refit', 'none'),
    ('joulewise.powermetrics_fiducial', 'rederive_detection_from_artifacts', 'k.rederive', 'none'),
    ('joulewise.calibration_bracketing', 'discover_calibration_candidates', 'k.calib', 'none'),
    ('joulewise.b5_analysis.bracket', 'evaluate_window_bracket', 'k.bracket', 'none'),
    ('joulewise.b5_analysis.bracket', '_window_inputs', 'k.bracket.inputs', 'plan'),
    ('joulewise.b5_analysis.bracket', '_strict_problems', 'k.bracket.strict', 'none'),
    ('joulewise.whole_window', 'whole_window_refusal_reasons', 'k.ww.refusal', 'none'),
    ('joulewise.whole_window', '_validate_row', 'k.ww.validate', 'none'),
    ('joulewise.whole_window', '_validate_row_uncached', 'k.ww.validate_uncached', 'none'),
    ('joulewise.whole_window', '_current_core_rederivation_reasons', 'k.ww.rederive', 'none'),
    ('joulewise.whole_window', 'AuthenticatedConsumptionSession._prepare', 'k.ww.prepare', 'none'),
    ('joulewise.whole_window', 'whole_window_drift_allowances', 'k.ww.drift', 'none'),
    ('joulewise.authentication_io', 'V2AuthenticationReadSession.read', 'k.auth_read', 'none'),
    ('joulewise.authentication_io', '_parse_strict', 'k.auth_parse', 'none'),
    ('scripts.mint_floor_artifact_generalized', '_authenticate_v2_inputs', 'k.mint.auth', 'none'),
    ('scripts.mint_floor_artifact_generalized', 'compose_indexed_producers', 'k.mint.compose', 'none'),
    ('scripts.mint_floor_artifact_generalized', '_build_v2_artifacts', 'k.mint.build', 'none'),
    ('scripts.mint_floor_artifact_generalized', '_v2_gate_postcollection', 'k.mint.gate', 'none'),
    ('scripts.emit_floor_mint_pinset', 'emit_indexed_pinset', 'k.pinset', 'none'),
    ('joulewise.floor_mint_estimator', 'bind_v2_floor_artifact_evidence', 'k.floorbind.bind', 'none'),
    ('joulewise.floor_mint_estimator', '_authenticated_common_mode_session', 'k.floorbind.session', 'none'),
    ('joulewise.floor_mint_estimator', 'recompute_comparative_estimate', 'k.floorbind.estimate', 'none'),
    ('joulewise.floor_extraction', 'extract_cells', 'k.extract', 'plan'),
    ('joulewise.analysis_engine.inputs', 'block5_claim_gate_inputs', 'k.inputs.gate', 'none'),
    ('joulewise.analysis_engine.inputs', 'load_analysis_inputs', 'k.inputs.load', 'none'),
    ('joulewise.analysis_engine', 'analyze_claims', 'k.claims', 'none'),
    ('joulewise.analysis_manifest_v3', 'validate_finalized_analysis_manifest_v3', 'k.manifest', 'none'),
    ('joulewise.paper_custody', '_replay_family', 'k.replay', 'none'),
    ('joulewise.paper_reported_energy_issuer', 'project_pack', 'k.issuer', 'none'),
    ('joulewise.b5_analysis.sensitivity', 'sensitivity_pass', 'k.sens', 'none'),
    ('joulewise.b5_analysis.dry_run', 'require_step_inputs', 'k.rehash', 'none'),
    ('joulewise.b5_analysis.windows', 'load_window_index', 'k.index', 'none'),
    ('joulewise.b5_analysis.archive', 'open_attempt_record', 'k.archive.record', 'none'),
    ('joulewise.b5_analysis.archive', 'open_archive', 'k.archive.open', 'none'),
    ('joulewise.b5_analysis.archive', 'ArchiveHandle.compare_runs_root', 'k.archive.runs_root', 'none'),
    ('joulewise.b5_analysis.archive', '_read', 'k.archive.read', 'none'),
    # Driver-side waits on a process pool, seen by the sampler before (or
    # without) the explicit pool_wait/dispatch_wait spans.
    ('concurrent.futures._base', 'Future.result', 'w.future', 'none'),
)
# Labels entered only through span(): D-188 VDL paths and leaf hooks.
SPAN_LABELS = ('pool.wait', 'dispatch.wait', 'k.vdl.verify', 'k.vdl.prefetch', 'k.vdl.hit',
               'k.vdl.ship', 'k.vdl.merge', 'k.prefill')
WAIT_LABELS = frozenset({'pool.wait', 'dispatch.wait', 'w.future'})
EXACT_WAIT_LABELS = ('pool.wait', 'dispatch.wait')

# Program spans: main's module (and for joulewise.cli the closed argv[0]).
PROGRAM_LABELS = {
    'scripts.extract_detection_floors': 'prog.extract_floors',
    'scripts.emit_floor_mint_pinset': 'prog.pinset',
    'scripts.mint_floor_artifact_generalized': 'prog.mint',
    'scripts.finalize_analysis_manifest': 'prog.finalize',
    'scripts.run_d165_closeout_from_custody': 'prog.d165',
    'scripts.issue_reported_energy': 'prog.issuer',
    'scripts.produce_b5_disclosures': 'prog.disclosures',
    'scripts.build_results_fill_input': 'prog.fill',
}
CLI_LABELS = {'validate-bundle': 'prog.cli.validate', 'reduce': 'prog.cli.reduce',
              'analyze-claims': 'prog.cli.claims'}
# Guarded RunState operations (RunState.guarded sets main._operation).
OPERATION_LABELS = {
    'prepare_initial': 'op.initial', 'prepare_kept': 'op.kept', 'prepare_tripwires': 'op.tripwires',
    'prepare_brackets': 'op.brackets', 'prepare_finalization': 'op.finalization',
    '<lambda>': 'op.inline',
}
OTHER = 'other'
VOCABULARY = frozenset(
    {label for _m, _q, label, _p in LABELS} | set(SPAN_LABELS) | set(PROGRAM_LABELS.values())
    | set(CLI_LABELS.values()) | set(OPERATION_LABELS.values())
    | {OTHER, 'prog.cli.other', 'prog.other', 'op.other', 'op.fail', 'member.other', 'dispatch'})

_STRUCTURE_KEYS = {
    'run_start': frozenset({'event', 'schema', 'mode'}),
    'step_begin': frozenset({'event', 'step', 'elapsed_s'}),
    'heartbeat': frozenset({'event', 'step', 'step_s', 'elapsed_s'}),
    'step_end': frozenset({'event', 'step', 'wall_s'}),
    'run_end': frozenset({'event', 'total_s'}),
    # Lane b5-robust: a step rerun serially after a host tooling refusal, and a
    # resumed run's first step ('-' when only the record remained).
    'step_retry': frozenset({'event', 'step', 'attempt'}),
    'run_resume': frozenset({'event', 'step'}),
}
_STRUCTURE_INTS = frozenset({'elapsed_s', 'step_s', 'wall_s', 'total_s', 'attempt'})
_RESTRICTED_KEYS = {
    'run_start': frozenset({'event', 'schema', 'mode', 'sample_ms', 'heartbeat_s', 'pid', 'cpu_count'}),
    'step_begin': frozenset({'event', 'step', 'elapsed_ms'}),
    'heartbeat': frozenset({'event', 'step', 'step_ms', 'elapsed_ms', 'label', 'program', 'top',
                            'progress_permille'}),
    'step_end': frozenset({'event', 'step', 'wall_ms', 'cpu_ms', 'serial_ms', 'spans_ms', 'maxrss_mib',
                           'load_x100', 'programs', 'pool', 'children', 'phases', 'sampled_ms',
                           'unattributed_ms', 'top'}),
    'run_end': frozenset({'event', 'total_ms', 'cpu_ms', 'phases', 'top'}),
    'step_retry': frozenset({'event', 'step', 'attempt', 'elapsed_ms'}),
    'run_resume': frozenset({'event', 'step', 'elapsed_ms'}),
}
_RESTRICTED_EVENTS = frozenset(_RESTRICTED_KEYS)
_GROUPS = ('driver', 'child', 'member')
_LOAD_KEYS = frozenset({'start', 'end', 'max'})
_PROGRAM_KEYS = frozenset({'count', 'wall_ms', 'cpu_ms', 'max_ms'})
_POOL_KEYS = frozenset({'batches', 'tasks', 'wall_ms', 'busy_ms', 'cpu_ms', 'max_task_ms', 'pool_size',
                        'busy_permille'})
_CHILDREN_KEYS = frozenset({'tasks', 'wall_ms', 'cpu_ms'})
# Sampled-histogram keys are '<file base>:<qualname>' code locations. A key that
# spells an outcome or refusal word is collapsed to 'qualname' when sampled and
# refused by the validator, so the restricted tier never carries such a token.
_QUALNAME_KEY = re.compile(r'[A-Za-z0-9_.<>/-]{1,199}:[A-Za-z0-9_.:<>/-]{1,199}')
_OUTCOME_TOKEN = re.compile(r'(?i)refus|outcome|verdict|decision|accept|reject|deadline|unavailable|status')
_SAFE = re.compile(r'[A-Za-z0-9_.:<>/-]{1,200}')
_FLOAT_TOKEN = re.compile(r'(?<![A-Za-z0-9])(?:\d+\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+)(?![A-Za-z0-9])')
_MAX_INT = 10 ** 15
_TOP_N = 25


class PhaseLineError(ValueError):
    """A timer line that must not be written."""


def _reject_constant(token):
    raise PhaseLineError('non-finite constant')


def _reject_float(token):
    raise PhaseLineError('float token')


def _pairs(pairs):
    keys = [key for key, _value in pairs]
    if len(set(keys)) != len(keys):
        raise PhaseLineError('duplicate key')
    return dict(pairs)


def canonical_line(document) -> bytes:
    return (json.dumps(document, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                       allow_nan=False) + '\n').encode('ascii')


def _is_count(value) -> bool:
    return type(value) is int and 0 <= value < _MAX_INT


def validate_phase_line(line, tier: str = 'structure') -> dict:
    """Parse and check one timer line; return the document or raise PhaseLineError.

    STRUCTURE: closed keys per event, non-negative ints for durations (no
    float, no bool), the step vocabulary, the mode vocabulary, canonical bytes.
    RESTRICTED: closed keys per event and per nested object (exactly what
    _Timer writes); non-negative ints; label strings from VOCABULARY only;
    sampled-histogram keys must be code locations that spell no outcome or
    refusal word; no float token anywhere.
    """
    if tier not in ('structure', 'restricted'):
        raise PhaseLineError('tier')
    if isinstance(line, dict):
        line = canonical_line(line)
    if isinstance(line, str):
        line = line.encode('utf-8')
    if not isinstance(line, bytes) or not line.endswith(b'\n') or line.count(b'\n') != 1:
        raise PhaseLineError('not one line')
    try:
        text = line.decode('ascii')
        document = json.loads(text, parse_float=_reject_float, parse_constant=_reject_constant,
                              object_pairs_hook=_pairs)
    except PhaseLineError:
        raise
    except (UnicodeDecodeError, ValueError) as exc:
        raise PhaseLineError('not JSON') from exc
    if not isinstance(document, dict) or canonical_line(document) != line:
        raise PhaseLineError('not a canonical object')
    if _FLOAT_TOKEN.search(text):
        raise PhaseLineError('float token')
    event = document.get('event')
    if tier == 'structure':
        keys = _STRUCTURE_KEYS.get(event) if isinstance(event, str) else None
        if keys is None or set(document) != keys:
            raise PhaseLineError('keys')
        for key, value in document.items():
            if key in _STRUCTURE_INTS:
                if not _is_count(value):
                    raise PhaseLineError(key)
            elif key == 'schema':
                if value != SCHEMA:
                    raise PhaseLineError(key)
            elif key == 'mode':
                if value not in MODES:
                    raise PhaseLineError(key)
            elif key == 'step':
                if value not in STEP_IDS and value != '-':
                    raise PhaseLineError(key)
            elif key != 'event':
                raise PhaseLineError(key)
        return document
    keys = _RESTRICTED_KEYS.get(event) if isinstance(event, str) else None
    if keys is None or set(document) != keys:
        raise PhaseLineError('keys')
    _check_restricted(document)
    return document


def _need(condition, what):
    if not condition:
        raise PhaseLineError(what)


def _int_map(value, keys, what):
    _need(type(value) is dict and set(value) == keys and all(_is_count(v) for v in value.values()), what)


def _label(value, what, *, none=False):
    _need((none and value is None) or (type(value) is str and value in VOCABULARY), what)


def _top_rows(value, what, *, qualname):
    _need(type(value) is list, what)
    for row in value:
        _need(type(row) is list and len(row) == 2 and _is_count(row[1]), what)
        if qualname:
            key = row[0]
            _need(type(key) is str and (key == 'qualname' or (_QUALNAME_KEY.fullmatch(key) is not None
                                                             and not _OUTCOME_TOKEN.search(key))), what)
        else:
            _label(row[0], what)


def _phase_table(value, what):
    _need(type(value) is dict, what)
    for label, pair in value.items():
        _label(label, what)
        _need(type(pair) is list and len(pair) == 2 and all(_is_count(v) for v in pair), what)


def _check_restricted(document):
    """The restricted tier's closed schema: exactly what _Timer writes, nothing else."""
    event = document['event']
    if 'step' in document:
        _need(document['step'] in STEP_IDS or (event in ('heartbeat', 'run_resume') and document['step'] == '-'),
              'step')
    for key in ('sample_ms', 'heartbeat_s', 'pid', 'cpu_count', 'elapsed_ms', 'step_ms', 'wall_ms', 'cpu_ms', 'attempt',
                'serial_ms', 'maxrss_mib', 'sampled_ms', 'unattributed_ms', 'total_ms'):
        if key in document:
            _need(_is_count(document[key]), key)
    if event == 'run_start':
        _need(document['schema'] == RESTRICTED_SCHEMA, 'schema')
        _need(document['mode'] is None or document['mode'] in MODES, 'mode')
    elif event == 'heartbeat':
        _label(document['label'], 'label')
        _label(document['program'], 'program', none=True)
        _top_rows(document['top'], 'top', qualname=False)
        _need(document['progress_permille'] is None or _is_count(document['progress_permille']),
              'progress_permille')
    elif event == 'step_end':
        spans = document['spans_ms']
        _need(type(spans) is dict, 'spans_ms')
        for label, value in spans.items():
            _label(label, 'spans_ms')
            _need(_is_count(value), 'spans_ms')
        _int_map(document['load_x100'], _LOAD_KEYS, 'load_x100')
        programs = document['programs']
        _need(type(programs) is dict, 'programs')
        for key, value in programs.items():
            group, _sep, label = key.partition(':')
            _need(group in _GROUPS, 'programs')
            _label(label, 'programs')
            _int_map(value, _PROGRAM_KEYS, 'programs')
        pool = document['pool']
        _need(type(pool) is dict, 'pool')
        for key, value in pool.items():
            _label(key[len('child:'):] if key.startswith('child:') else key, 'pool')
            _int_map(value, _POOL_KEYS, 'pool')
        _int_map(document['children'], _CHILDREN_KEYS, 'children')
        phases = document['phases']
        _need(type(phases) is dict and set(phases) == set(_GROUPS), 'phases')
        for group in _GROUPS:
            _phase_table(phases[group], 'phases')
        _top_rows(document['top'], 'top', qualname=True)
    elif event == 'run_end':
        _phase_table(document['phases'], 'phases')
        _top_rows(document['top'], 'top', qualname=True)


def _env_int(name, default):
    text = os.environ.get(name, '')
    return int(text) if text.isdigit() and len(text) < 9 else default


def _main_frames_for(ident):
    def frames():
        frame = sys._current_frames().get(ident)
        codes = []
        try:
            while frame is not None:
                codes.append(frame.f_code)
                frame = frame.f_back
        finally:
            del frame
        return codes
    return frames


def _qualname_key(code) -> str:
    base = os.path.basename(code.co_filename)
    if base.endswith('.py'):
        base = base[:-3]
    key = base + ':' + getattr(code, 'co_qualname', code.co_name)
    key = re.sub(r'[^A-Za-z0-9_.:<>/-]', '_', key)[:200]
    if _FLOAT_TOKEN.search(key) or _OUTCOME_TOKEN.search(key) or not _QUALNAME_KEY.fullmatch(key):
        return 'qualname'
    return key


def _static_code(module, qualname):
    """The code object of module.qualname, found through __dict__ lookups only.

    Runs on the sampler thread: it must never call a module __getattr__, a
    descriptor or a property, so it can never import or execute driver code.
    """
    import types
    target = module
    for part in qualname.split('.'):
        if not isinstance(target, (type, types.ModuleType)):
            return None
        target = vars(target).get(part)
    if isinstance(target, (staticmethod, classmethod)):
        target = target.__func__
    for _ in range(16):
        try:
            # Generic lookup: never a class __getattr__.
            namespace = object.__getattribute__(target, '__dict__')
        except (AttributeError, TypeError):
            break
        wrapped = namespace.get('__wrapped__') if isinstance(namespace, dict) else None
        if wrapped is None:
            break
        target = wrapped
    return target.__code__ if isinstance(target, types.FunctionType) else None


def _maxrss_mib(rusage) -> int:
    value = rusage().ru_maxrss
    # macOS reports bytes, Linux kibibytes.
    return int(value // (1 << 20)) if sys.platform == 'darwin' else int(value // 1024)


def _load_x100(loadavg) -> int:
    return max(0, int(round(loadavg()[0] * 100)))


def _rusage():
    import resource
    return resource.getrusage(resource.RUSAGE_SELF)


class _Acc:
    """Accumulators for one step (or the time outside steps)."""
    __slots__ = ('phases', 'hist', 'sampled', 'unattributed', 'spans', 'programs', 'pool', 'child',
                 'member', 'load_max', 'children')

    def __init__(self):
        self.phases = {}        # label -> [self_ns, incl_ns]
        self.hist = {}          # module:qualname -> self_ns
        self.sampled = 0
        self.unattributed = 0
        self.spans = {}         # exact span label -> ns
        self.programs = []      # [group, label, wall_ns, cpu_ns]
        self.pool = {}          # label -> [batches, tasks, wall_ns, busy_ns, cpu_ns, max_task_ns, pool_size]
        self.child = {}         # label -> [self_ns, incl_ns]
        self.member = {}        # label -> [self_ns, incl_ns]
        self.load_max = 0
        self.children = [0, 0, 0]   # tasks, wall_ns, cpu_ns


def _add_phase(table, label, self_ns, incl_ns):
    row = table.get(label)
    if row is None:
        table[label] = [self_ns, incl_ns]
    else:
        row[0] += self_ns
        row[1] += incl_ns


def _ms(ns) -> int:
    return max(0, int(ns)) // 1_000_000


def _s(ns) -> int:
    return max(0, int(ns)) // 1_000_000_000


class _Span:
    """Class-based context manager: never alters the body's exception."""
    __slots__ = ('timer', 'label', 'kind', 't0', 'c0')

    def __init__(self, timer, label, kind):
        self.timer, self.label, self.kind = timer, label, kind
        self.t0 = self.c0 = None

    def __enter__(self):
        timer = self.timer
        if timer is None or not timer.on:
            return None
        try:
            self.t0, self.c0 = timer.clock(), timer.cpu_clock()
            if self.kind == 'program':
                timer.program_stack.append(self.label)
            else:
                timer.span_stack.append(self.label)
        except Exception:  # noqa: BLE001 - timing never affects the run
            timer.disable()
        return None

    def __exit__(self, exc_type, exc, tb):
        timer = self.timer
        if timer is None or self.t0 is None:
            return False
        try:
            stack = timer.program_stack if self.kind == 'program' else timer.span_stack
            if stack and stack[-1] == self.label:
                stack.pop()
            elif self.label in stack:
                stack.remove(self.label)
            if timer.on:
                wall, cpu = timer.clock() - self.t0, timer.cpu_clock() - self.c0
                with timer.lock:
                    acc = timer.acc
                    if self.kind == 'program':
                        acc.programs.append([timer.group, self.label, wall, cpu])
                    else:
                        acc.spans[self.label] = acc.spans.get(self.label, 0) + wall
        except Exception:  # noqa: BLE001
            timer.disable()
        return False


class _Timer:
    def __init__(self, *, structure_fd=None, mode=None, group='driver', sample_ms=None, heartbeat_s=None,
                 clock=None, cpu_clock=None, frames=None, rusage=None, loadavg=None, start_sampler=True):
        self.on = True
        self.lock = threading.RLock()
        self.group = group
        self.mode = mode if mode in MODES else None
        self.clock = clock or time.perf_counter_ns
        self.cpu_clock = cpu_clock or time.process_time_ns
        self.rusage = rusage or _rusage
        self.loadavg = loadavg or os.getloadavg
        self.frames = frames or _main_frames_for(threading.get_ident())
        self.sample_ms = _env_int(SAMPLE_ENV, DEFAULT_SAMPLE_MS) if sample_ms is None else sample_ms
        hb = _env_int(HEARTBEAT_ENV, DEFAULT_HEARTBEAT_S) if heartbeat_s is None else heartbeat_s
        self.heartbeat_ns = hb * 1_000_000_000
        self.sinks = {'structure': structure_fd, 'restricted': None}
        self.stack_fd = None
        self.stack_registered = False
        self.span_stack = []
        self.program_stack = []
        self.code_labels = {}
        self.modules_seen = -1
        self.step = None
        self.acc = _Acc()
        self.outside = self.acc
        self.total_phases = {}
        self.total_hist = {}
        self.ended = False
        self.progress = None
        self.innermost = OTHER
        self.thread = None
        self.stop_event = threading.Event()
        self.t0 = self.clock()
        self.c0 = self.cpu_clock()
        self.last_sample = self.t0
        self.last_heartbeat = self.t0
        self.step_t0 = self.step_c0 = self.step_load0 = None
        if start_sampler and self.sample_ms > 0:
            self.thread = threading.Thread(target=self._loop, name='joulewise-b5-phase-sampler', daemon=True)
            self.thread.start()

    # -- control -------------------------------------------------------
    def disable(self):
        self.on = False
        self.stop_event.set()

    def _loop(self):
        try:
            period = self.sample_ms / 1000
            while not self.stop_event.wait(period):
                if not self.on:
                    return
                self.sample()
        except BaseException:  # noqa: BLE001 - nothing reaches threading.excepthook or stderr
            self.on = False

    def stop(self):
        self.stop_event.set()
        thread = self.thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=5 + 2 * self.sample_ms / 1000)

    # -- labels ----------------------------------------------------------
    def _resolve(self):
        count = len(sys.modules)
        if count == self.modules_seen:
            return
        self.modules_seen = count
        mapping = {}
        for module, qualname, label, _policy in LABELS:
            target = sys.modules.get(module)
            if target is None:
                continue
            try:
                code = _static_code(target, qualname)
            except Exception:  # noqa: BLE001 - an unresolved label stays unresolved
                code = None
            if code is not None:
                mapping[code] = label
        self.code_labels = mapping

    # -- sampling ----------------------------------------------------------
    def sample(self):
        if not self.on:
            return
        self._resolve()
        codes = self.frames()
        now = self.clock()
        labels = [self.code_labels.get(code) for code in codes]
        spans = tuple(self.span_stack)
        programs = tuple(self.program_stack)
        frame_label = next((label for label in labels if label is not None), None)
        explicit = spans[-1] if spans else None
        self_label = explicit or frame_label
        inclusive = {label for label in labels if label is not None} | set(spans) | set(programs)
        if self_label is not None:
            inclusive.add(self_label)
        qual = _qualname_key(codes[0]) if codes else None
        try:
            load = _load_x100(self.loadavg)
        except Exception:  # noqa: BLE001
            load = 0
        with self.lock:
            weight = max(0, now - self.last_sample)
            self.last_sample = max(self.last_sample, now)
            acc = self.acc
            acc.sampled += weight
            if self_label is None:
                acc.unattributed += weight
                _add_phase(acc.phases, OTHER, weight, 0)
            for label in inclusive:
                _add_phase(acc.phases, label, weight if label == self_label else 0, weight)
            if qual is not None:
                acc.hist[qual] = acc.hist.get(qual, 0) + weight
            acc.load_max = max(acc.load_max, load)
        self.innermost = self_label or OTHER
        if self.heartbeat_ns and now - self.last_heartbeat >= self.heartbeat_ns:
            self.last_heartbeat = now
            self._heartbeat(now)

    def _heartbeat(self, now):
        step = self.step or '-'
        step_ns = now - self.step_t0 if self.step_t0 is not None else 0
        self.write('structure', {'event': 'heartbeat', 'step': step, 'step_s': _s(step_ns),
                                 'elapsed_s': _s(now - self.t0)})
        with self.lock:
            top = sorted(((row[0], label) for label, row in self.acc.phases.items()), reverse=True)[:5]
        self.write('restricted', {
            'event': 'heartbeat', 'step': step, 'step_ms': _ms(step_ns), 'elapsed_ms': _ms(now - self.t0),
            'label': self.innermost, 'program': self.program_stack[-1] if self.program_stack else None,
            'top': [[label, _ms(ns)] for ns, label in top],
            'progress_permille': self.progress})

    # -- sinks -------------------------------------------------------------
    def write(self, tier, document):
        fd = self.sinks.get(tier)
        if fd is None:
            return
        try:
            data = canonical_line(document)
            validate_phase_line(data, tier)
            with self.lock:
                view = memoryview(data)
                while view:
                    view = view[os.write(fd, view):]
        except Exception:  # noqa: BLE001 - a bad line or a sink error turns that sink off
            self.sinks[tier] = None
            if tier == 'restricted':
                try:
                    os.close(fd)
                except OSError:
                    pass

    def attach_restricted(self, restricted):
        logs = os.path.join(os.fspath(restricted), 'logs')
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
        if self.sinks['restricted'] is None:
            try:
                self.sinks['restricted'] = os.open(os.path.join(logs, RESTRICTED_LOG), flags, 0o644)
            except OSError:
                self.sinks['restricted'] = None
            else:
                self.write('restricted', {'event': 'run_start', 'schema': RESTRICTED_SCHEMA, 'mode': self.mode,
                                          'sample_ms': self.sample_ms, 'heartbeat_s': self.heartbeat_ns // 10 ** 9,
                                          'pid': os.getpid(), 'cpu_count': os.cpu_count() or 0})
        if self.stack_fd is None:
            try:
                import faulthandler
                import signal
                fd = os.open(os.path.join(logs, STACK_LOG.format(pid=os.getpid())), flags, 0o644)
                try:
                    faulthandler.register(signal.SIGUSR1, file=fd, all_threads=True, chain=False)
                except Exception:  # noqa: BLE001
                    os.close(fd)
                    raise
                self.stack_fd, self.stack_registered = fd, True
            except Exception:  # noqa: BLE001
                self.stack_fd = None

    # -- steps -------------------------------------------------------------
    def step_begin(self, step):
        if step not in STEP_IDS:
            return
        now = self.clock()
        self.sample_now(now)
        with self.lock:
            self._fold(self.acc)
            self.acc = _Acc()
            self.step = step
            self.progress = None
        self.step_t0, self.step_c0 = now, self.cpu_clock()
        try:
            self.step_load0 = _load_x100(self.loadavg)
        except Exception:  # noqa: BLE001
            self.step_load0 = 0
        self.write('structure', {'event': 'step_begin', 'step': step, 'elapsed_s': _s(now - self.t0)})
        self.write('restricted', {'event': 'step_begin', 'step': step, 'elapsed_ms': _ms(now - self.t0)})

    def sample_now(self, now):
        """Close the open sampling interval at an exact edge (no frame walk)."""
        with self.lock:
            weight = max(0, now - self.last_sample)
            self.last_sample = max(self.last_sample, now)
            # The interval since the last sample belongs to the label seen last.
            label = self.innermost
            acc = self.acc
            acc.sampled += weight
            if label == OTHER:
                acc.unattributed += weight
            _add_phase(acc.phases, label, weight, 0 if label == OTHER else weight)

    def _fold(self, acc):
        for label, (self_ns, incl_ns) in acc.phases.items():
            _add_phase(self.total_phases, label, self_ns, incl_ns)
        for key, ns in acc.hist.items():
            self.total_hist[key] = self.total_hist.get(key, 0) + ns

    def step_end(self, step):
        if step != self.step or self.step_t0 is None:
            return
        now = self.clock()
        cpu = self.cpu_clock() - self.step_c0
        self.sample_now(now)
        wall = now - self.step_t0
        with self.lock:
            acc = self.acc
            self._fold(acc)
            self.acc = _Acc()
            self.step = None
        self.step_t0 = None
        self.write('structure', {'event': 'step_end', 'step': step, 'wall_s': _s(wall)})
        try:
            rss = _maxrss_mib(self.rusage)
        except Exception:  # noqa: BLE001
            rss = 0
        try:
            load_end = _load_x100(self.loadavg)
        except Exception:  # noqa: BLE001
            load_end = 0
        waits = sum(acc.spans.get(label, 0) for label in EXACT_WAIT_LABELS)
        self.write('restricted', {
            'event': 'step_end', 'step': step, 'wall_ms': _ms(wall), 'cpu_ms': _ms(cpu),
            'serial_ms': _ms(wall - waits), 'spans_ms': {k: _ms(v) for k, v in sorted(acc.spans.items())},
            'maxrss_mib': rss,
            'load_x100': {'start': self.step_load0 or 0, 'end': load_end,
                          'max': max(acc.load_max, self.step_load0 or 0, load_end)},
            'programs': _programs_ms(acc.programs),
            'pool': {label: {'batches': r[0], 'tasks': r[1], 'wall_ms': _ms(r[2]), 'busy_ms': _ms(r[3]),
                             'cpu_ms': _ms(r[4]), 'max_task_ms': _ms(r[5]), 'pool_size': r[6],
                             'busy_permille': (r[3] * 1000 // (r[2] * r[6])) if r[2] and r[6] else 0}
                     for label, r in sorted(acc.pool.items())},
            'children': {'tasks': acc.children[0], 'wall_ms': _ms(acc.children[1]),
                         'cpu_ms': _ms(acc.children[2])},
            'phases': {'driver': _phase_ms(acc.phases), 'child': _phase_ms(acc.child),
                       'member': _phase_ms(acc.member)},
            'sampled_ms': _ms(acc.sampled), 'unattributed_ms': _ms(acc.unattributed),
            'top': _top(acc.hist)})

    def step_retry(self, step, attempt):
        if step not in STEP_IDS or not _is_count(attempt):
            return
        now = self.clock()
        self.write('structure', {'event': 'step_retry', 'step': step, 'attempt': attempt})
        self.write('restricted', {'event': 'step_retry', 'step': step, 'attempt': attempt,
                                  'elapsed_ms': _ms(now - self.t0)})

    def run_resume(self, step):
        if step not in STEP_IDS and step != '-':
            return
        now = self.clock()
        self.write('structure', {'event': 'run_resume', 'step': step})
        self.write('restricted', {'event': 'run_resume', 'step': step, 'elapsed_ms': _ms(now - self.t0)})

    def run_end(self):
        if self.ended:
            return
        self.ended = True
        if self.step is not None:
            self.step_end(self.step)
        now = self.clock()
        with self.lock:
            self._fold(self.acc)
            self.acc = _Acc()
        self.write('structure', {'event': 'run_end', 'total_s': _s(now - self.t0)})
        self.write('restricted', {'event': 'run_end', 'total_ms': _ms(now - self.t0),
                                  'cpu_ms': _ms(self.cpu_clock() - self.c0),
                                  'phases': _phase_ms(self.total_phases), 'top': _top(self.total_hist)})

    def close(self):
        self.stop()
        if self.stack_registered:
            try:
                import faulthandler
                import signal
                faulthandler.unregister(signal.SIGUSR1)
            except Exception:  # noqa: BLE001
                pass
            self.stack_registered = False
        for fd in (self.sinks.get('restricted'), self.stack_fd):
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
        self.sinks['restricted'] = None
        self.stack_fd = None

    # -- pools and children -------------------------------------------------
    def pool_batch(self, reference, costs, wall_ns, pool_size):
        label = _member_label(reference)
        costs = [cost for cost in list(costs) if isinstance(cost, dict)] if isinstance(costs, (list, tuple)) else []
        busy = sum(int(cost.get('wall_ns', 0)) for cost in costs)
        cpu = sum(int(cost.get('cpu_ns', 0)) for cost in costs)
        longest = max((int(cost.get('wall_ns', 0)) for cost in costs), default=0)
        with self.lock:
            row = self.acc.pool.setdefault(label, [0, 0, 0, 0, 0, 0, 0])
            row[0] += 1
            row[1] += len(costs)
            row[2] += max(0, int(wall_ns))
            row[3] += busy
            row[4] += cpu
            row[5] = max(row[5], longest)
            row[6] = max(row[6], int(pool_size))
            for cost in costs:
                for phase, pair in (cost.get('phases') or {}).items():
                    if phase in VOCABULARY:
                        _add_phase(self.acc.member, phase, int(pair[0]), int(pair[1]))

    def merge_child(self, table):
        if not isinstance(table, dict):
            return
        with self.lock:
            acc = self.acc
            acc.children[0] += 1
            acc.children[1] += max(0, int(table.get('wall_ns', 0)))
            acc.children[2] += max(0, int(table.get('cpu_ns', 0)))
            for phase, pair in (table.get('phases') or {}).items():
                if phase in VOCABULARY:
                    _add_phase(acc.child, phase, int(pair[0]), int(pair[1]))
            for phase, pair in (table.get('member') or {}).items():
                if phase in VOCABULARY:
                    _add_phase(acc.member, phase, int(pair[0]), int(pair[1]))
            for label, wall, cpu in table.get('programs') or ():
                if label in VOCABULARY:
                    acc.programs.append(['child', label, int(wall), int(cpu)])
            for label, row in (table.get('pool') or {}).items():
                if label in VOCABULARY and isinstance(row, list) and len(row) == 7:
                    mine = acc.pool.setdefault('child:' + label, [0, 0, 0, 0, 0, 0, 0])
                    for index in range(5):
                        mine[index] += int(row[index])
                    mine[5] = max(mine[5], int(row[5]))
                    mine[6] = max(mine[6], int(row[6]))

    def table(self):
        """This (child or worker) timer's accumulated table: plain ints and strings, picklable."""
        now = self.clock()
        self.sample_now(now)
        with self.lock:
            acc = self.acc
            return {'wall_ns': max(0, now - self.t0), 'cpu_ns': max(0, self.cpu_clock() - self.c0),
                    'phases': {label: list(row) for label, row in acc.phases.items()},
                    'member': {label: list(row) for label, row in acc.member.items()},
                    'programs': [[label, wall, cpu] for _group, label, wall, cpu in acc.programs],
                    'pool': {label: list(row) for label, row in acc.pool.items()}}

    def reset(self):
        now = self.clock()
        with self.lock:
            self.acc = _Acc()
            self.last_sample = now
            self.t0, self.c0 = now, self.cpu_clock()


def _phase_ms(table):
    rows = sorted(table.items(), key=lambda item: (-item[1][0], item[0]))
    return {label: [_ms(self_ns), _ms(incl_ns)] for label, (self_ns, incl_ns) in rows}


def _programs_ms(programs):
    """Program spans aggregated per group:label as {count, wall_ms, cpu_ms, max_ms}."""
    rows = {}
    for group, label, wall, cpu in programs:
        row = rows.setdefault(group + ':' + label, [0, 0, 0, 0])
        row[0] += 1
        row[1] += wall
        row[2] += cpu
        row[3] = max(row[3], wall)
    return {key: {'count': n, 'wall_ms': _ms(w), 'cpu_ms': _ms(c), 'max_ms': _ms(m)}
            for key, (n, w, c, m) in sorted(rows.items(), key=lambda item: (-item[1][1], item[0]))}


def _top(hist):
    rows = sorted(hist.items(), key=lambda item: (-item[1], item[0]))[:_TOP_N]
    return [[key, _ms(ns)] for key, ns in rows]


def _member_label(reference) -> str:
    if reference == 'dispatch':
        return 'dispatch'
    if callable(reference):
        reference = f'{getattr(reference, "__module__", "")}:{getattr(reference, "__qualname__", "")}'
    if isinstance(reference, str) and ':' in reference:
        module, qualname = reference.split(':', 1)
        for label_module, label_qualname, label, _policy in LABELS:
            if (module, qualname) == (label_module, label_qualname):
                return label
    return 'member.other'


def program_label(main, argv) -> str:
    """The closed label of a program run by StepRunner.run (no argument value beyond argv[0])."""
    operation = getattr(main, '_operation', None)
    if isinstance(operation, str):
        return OPERATION_LABELS.get(operation, 'op.other')
    module = getattr(main, '__module__', None)
    if module == 'joulewise.cli':
        first = argv[0] if argv else None
        return CLI_LABELS.get(first, 'prog.cli.other') if isinstance(first, str) else 'prog.cli.other'
    if module in PROGRAM_LABELS:
        return PROGRAM_LABELS[module]
    if module == 'joulewise.b5_analysis.dry_run' and getattr(main, '__name__', None) == 'fail':
        return 'op.fail'
    return 'prog.other'


# -- module-level timer and the public hooks ---------------------------------
_TIMER: _Timer | None = None
_LAST_CHILD_TABLE: dict | None = None


def current() -> _Timer | None:
    return _TIMER


def enabled() -> bool:
    timer = _TIMER
    return timer is not None and timer.on


def _call(name, *args):
    timer = _TIMER
    if timer is None or not timer.on:
        return None
    try:
        return getattr(timer, name)(*args)
    except Exception:  # noqa: BLE001 - timing never affects the run
        timer.disable()
        return None


class session:
    """Activate a timer in this process (nested: a no-op that yields the active timer)."""

    def __init__(self, structure_fd=None, *, mode=None, **options):
        self.structure_fd, self.mode, self.options = structure_fd, mode, options
        self.timer = None
        self.owner = False

    def __enter__(self):
        global _TIMER
        if _TIMER is not None:
            if self.structure_fd is not None:
                try:
                    os.close(self.structure_fd)
                except OSError:
                    pass
            return _TIMER
        try:
            self.timer = _Timer(structure_fd=self.structure_fd, mode=self.mode, **self.options)
            self.owner = True
            _TIMER = self.timer
            if self.mode in MODES:
                self.timer.write('structure', {'event': 'run_start', 'schema': SCHEMA, 'mode': self.mode})
        except Exception:  # noqa: BLE001
            self.timer, self.owner = None, False
            if self.structure_fd is not None:
                try:
                    os.close(self.structure_fd)
                except OSError:
                    pass
        return self.timer

    def __exit__(self, exc_type, exc, tb):
        global _TIMER
        if not self.owner:
            return False
        timer = self.timer
        _TIMER = None
        try:
            if timer.on:
                timer.run_end()
        except Exception:  # noqa: BLE001
            pass
        try:
            timer.close()
        except Exception:  # noqa: BLE001
            pass
        fd = timer.sinks.get('structure') if timer is not None else None
        structure_fd = self.structure_fd
        for candidate in {fd, structure_fd} - {None}:
            try:
                os.close(candidate)
            except OSError:
                pass
        return False


def attach_restricted(restricted) -> None:
    _call('attach_restricted', restricted)


def step_begin(step) -> None:
    _call('step_begin', step)


def step_end(step) -> None:
    _call('step_end', step)


def run_end() -> None:
    _call('run_end')


def step_retry(step, attempt) -> None:
    _call('step_retry', step, attempt)


def run_resume(step) -> None:
    _call('run_resume', step)


def program_span(main, argv) -> _Span:
    timer = _TIMER
    if timer is None or not timer.on:
        return _Span(None, None, 'program')
    try:
        label = program_label(main, argv)
    except Exception:  # noqa: BLE001
        label = 'prog.other'
    return _Span(timer, label, 'program')


def span(label) -> _Span:
    timer = _TIMER
    if timer is None or not timer.on or label not in SPAN_LABELS:
        return _Span(None, None, 'span')
    return _Span(timer, label, 'span')


def pool_wait() -> _Span:
    return span('pool.wait')


def dispatch_wait() -> _Span:
    return span('dispatch.wait')


def pool_progress(done, total) -> None:
    timer = _TIMER
    if timer is None or not timer.on:
        return
    try:
        timer.progress = int(done) * 1000 // int(total) if int(total) > 0 else None
    except Exception:  # noqa: BLE001
        timer.progress = None


def pool_batch(reference, costs, wall_ns, pool_size=0) -> None:
    _call('pool_batch', reference, costs, wall_ns, pool_size)


def merge_child(table) -> None:
    _call('merge_child', table)


class task_cost:
    """In a worker: exact wall/CPU and sampled phases of one task, when enabled.

    Yields a dict that is filled on exit ({'wall_ns', 'cpu_ns', 'phases'}), or
    None when disabled. The first enabled task starts the process's sampler.
    """

    def __init__(self, enabled=True):
        self.enabled = bool(enabled)
        self.cost = None
        self.timer = None
        self.t0 = self.c0 = None

    def __enter__(self):
        global _TIMER
        if not self.enabled:
            return None
        try:
            if _TIMER is None:
                _TIMER = _Timer(group='member')
            timer = _TIMER
            if not timer.on or timer.group != 'member':
                return None
            timer.reset()
            self.timer, self.cost = timer, {}
            self.t0, self.c0 = timer.clock(), timer.cpu_clock()
        except Exception:  # noqa: BLE001
            self.cost = None
        return self.cost

    def __exit__(self, exc_type, exc, tb):
        if self.cost is None or self.timer is None:
            return False
        try:
            timer = self.timer
            wall, cpu = timer.clock() - self.t0, timer.cpu_clock() - self.c0
            table = timer.table()
            self.cost.update(wall_ns=max(0, wall), cpu_ns=max(0, cpu), phases=table['phases'])
        except Exception:  # noqa: BLE001
            pass
        return False


class child_session:
    """Around a child program (parallel.run_child): a sinkless child-group timer.

    In-process (a timer already active) it is a no-op and child_table() is None.
    """

    def __init__(self, enabled=True):
        self.enabled = bool(enabled)
        self.timer = None

    def __enter__(self):
        global _TIMER, _LAST_CHILD_TABLE
        _LAST_CHILD_TABLE = None
        if not self.enabled or _TIMER is not None:
            return None
        try:
            self.timer = _Timer(group='child')
            _TIMER = self.timer
        except Exception:  # noqa: BLE001
            self.timer = None
        return self.timer

    def __exit__(self, exc_type, exc, tb):
        global _TIMER, _LAST_CHILD_TABLE
        timer = self.timer
        if timer is None:
            return False
        _TIMER = None
        try:
            if timer.on:
                _LAST_CHILD_TABLE = timer.table()
        except Exception:  # noqa: BLE001
            _LAST_CHILD_TABLE = None
        try:
            timer.close()
        except Exception:  # noqa: BLE001
            pass
        return False


def child_table():
    return _LAST_CHILD_TABLE


# -- structure log path (scripts/run_b5_analysis.py --phase-log) --------------
def _identity(path):
    """(st_dev, st_ino) of an existing path (following links), or None if it does not exist."""
    try:
        info = os.stat(path)
    except FileNotFoundError:
        return None
    return info.st_dev, info.st_ino


def _fold_name(name) -> str:
    import unicodedata
    return unicodedata.normalize('NFD', name).casefold()


def _root_guard(root):
    """Identity of a root, or of its nearest existing ancestor plus the first missing component."""
    text = os.path.abspath(os.fspath(root))
    missing = []
    while True:
        ident = _identity(text)
        if ident is not None:
            return ident, (missing[-1] if missing else None)
        parent, name = os.path.split(text)
        if parent == text:
            return None, None
        missing.append(name)
        text = parent


def open_structure_log(path, *, custody, repo) -> int:
    """Open the structure log before step 0; raise ValueError or OSError if it is not admissible.

    The path must be absolute, contain no '..' and no symbolic link, not exist
    yet, and lie outside both the custody root and the repository. "Outside"
    is decided by identity, not by spelling: no existing ancestor of the log
    may be the custody root or the repository by (st_dev, st_ino), which also
    covers a case-variant spelling on a case-insensitive volume and a firmlink
    alias such as /System/Volumes/Data on macOS. When the custody root does not
    exist yet, the log may not take the name (case- and normalization-folded)
    of its first missing component in the directory where it would be created.
    """
    text = os.fspath(path)
    if not isinstance(text, str) or not os.path.isabs(text) or '\0' in text:
        raise ValueError('phase log path must be absolute')
    parts = text.split('/')
    if any(part in ('.', '..') for part in parts[1:]) or text.endswith('/'):
        raise ValueError('phase log path must be normal')
    import stat
    prefix = ''
    for part in parts[1:-1]:
        if not part:
            raise ValueError('phase log path must be normal')
        prefix += '/' + part
        if stat.S_ISLNK(os.lstat(prefix).st_mode):
            raise ValueError('phase log path has a symbolic link')
    if os.path.lexists(text):
        raise ValueError('phase log path exists')
    from pathlib import Path
    candidate = Path(text)
    for root in (custody, repo):
        root = Path(root)
        for form in {root.absolute(), root.resolve()}:
            if candidate == form or candidate.is_relative_to(form):
                raise ValueError('phase log path inside custody or repository')
    parent, name = os.path.split(text)
    ancestors = []
    walk = parent
    while True:
        ancestors.append(_identity(walk))
        up = os.path.dirname(walk)
        if up == walk:
            break
        walk = up
    for root in (custody, repo):
        ident, first_missing = _root_guard(root)
        if ident is None:
            raise ValueError('phase log root unresolvable')
        if first_missing is None:
            if ident in ancestors:
                raise ValueError('phase log path inside custody or repository')
        elif ident == ancestors[0] and _fold_name(name) == _fold_name(first_missing):
            raise ValueError('phase log path would take the custody or repository name')
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
    return os.open(text, flags, 0o644)
