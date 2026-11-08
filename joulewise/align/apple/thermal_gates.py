"""ALIGN gates/holds over the fixed thermometry Sidecar.

Runtime/deadman dependencies stay here so the diagnostic collector and its
legacy hazards.temperature alias retain their isolated import boundary.
"""
from __future__ import annotations
from collections.abc import Mapping
from contextlib import nullcontext
import hashlib
import json
import math
import os
from statistics import median
from types import GeneratorType

from joulewise.align.apple import thermal
from joulewise.align.apple.thermal import NS, Coverage, validate_policy, valid_value
from joulewise.align.apple.sampler import monotonic_ns, _stamp_record
from joulewise.align.apple.budget import DeadmanExpired
from joulewise.interfaces import RuntimeEvent

REFERENCE_SCHEMA = 'joulewise.align_window_reference.v1'
G0_CAP_DEFAULT_S = 600
G0_CAP_MAX_S = 1200
# LEAD-RULINGS-2 R10-2(a): a D member's W1 G0 cap may fall below the 600 s
# floor only under the lead's committed ruling 1(f) receipt; the policy then
# names it (g0_cap_receipt), and the kit binds that digest to the receipt bytes.
R10_G0_CAP_AUTHORITY = 'LEAD-RULINGS-2 R10-2(a)'
G0_UNOBSERVED_LIMIT_S = 300


class WindowReferenceRefused(RuntimeError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


class ThermalFault(RuntimeError):
    """A gate cannot be evaluated at all; the member fails instead of waiting.

    Raised for a dead collector (WP8 F2) or a missing status source at G0
    (WP8 F5). The matching flag is also left on the session.
    """
    def __init__(self, code, detail=None):
        self.code = code
        super().__init__(code if detail is None else f'{code}: {detail}')


def _status_observed(status):
    """A bound status source always reports os_level and/or pm_observed_ns keys."""
    return isinstance(status, Mapping) and ('os_level' in status or 'pm_observed_ns' in status)


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode()


def _policy_digest(sensors):
    return hashlib.sha256(_canonical(sensors)).hexdigest()


class _EpisodeClocks:
    """Synthetic-clock seam. Production sidecars use the real three clocks."""
    def __init__(self, session):
        self.session = session

    def monotonic_ns(self):
        return monotonic_ns(self.session.clock.stamp())

    def stamp(self):
        from joulewise.hazards.base import Stamp
        stamp = self.session.clock.stamp()
        mono = monotonic_ns(stamp)
        return Stamp(round(stamp.epoch_s * NS), mono, mono)


def sample_rows(rows):
    """Normalize Sidecar or legacy sample rows for gates and the thermal desk.

    Journal custody stays in the Sidecar's three-clock schema. This projection
    retains the SMC read bracket and never turns a phase boundary into a sample.
    """
    result = []
    for row in rows:
        if row.get('kind') == 'sample':
            result.append(row)
        elif row.get('module') == 'temperature' and row.get('kind') == 'reading':
            def stamp(value):
                return {'epoch_ns': value['wall_ns'], 'monotonic_before_ns': value['monotonic_ns'],
                        'monotonic_after_ns': value['monotonic_ns']}
            started, finished = row['started'], row['finished']
            result.append({'kind': 'sample', 'monotonic_ns': started['monotonic_ns'],
                           'epoch_ns': started['wall_ns'], 'started': stamp(started),
                           'finished': stamp(finished), **row['values'],
                           'status': row['values'].get('status', {})})
    return result


def validate_gate_policy(value):
    required = {'sensors', 'delta_fast_c', 'delta_slow_c', 'turn_cap_s', 'per_turn', 'heavy', 'chunk_tokens'}
    if (not isinstance(value, Mapping) or not required <= value.keys()
            or 'window_reference' not in value
            or set(value) - required - {'window_reference', 'g0_cap_s', 'g0_cap_receipt'}):
        raise ValueError('thermal policy has missing or unknown fields')
    policy = dict(value)
    policy['sensors'] = validate_policy(policy['sensors'])
    receipt = policy.get('g0_cap_receipt')
    if 'g0_cap_receipt' in policy:
        # R10-2(a): the receipt travels only with a cap below the 600 s floor.
        if (not isinstance(receipt, Mapping) or set(receipt) != {'authority', 'receipt_sha256'}
                or receipt['authority'] != R10_G0_CAP_AUTHORITY
                or not isinstance(receipt['receipt_sha256'], str) or len(receipt['receipt_sha256']) != 64
                or any(c not in '0123456789abcdef' for c in receipt['receipt_sha256'])):
            raise ValueError('thermal.g0_cap_receipt must be {authority: '
                             f'{R10_G0_CAP_AUTHORITY!r}, receipt_sha256: 64-hex}}')
        policy['g0_cap_receipt'] = dict(receipt)
    if 'g0_cap_s' in policy:
        cap = policy['g0_cap_s']
        if type(cap) not in (int, float) or not math.isfinite(cap) or not 0 < cap <= G0_CAP_MAX_S:
            raise ValueError(f'thermal.g0_cap_s must be finite and in [{G0_CAP_DEFAULT_S}, {G0_CAP_MAX_S}], or in '
                             f'(0, {G0_CAP_MAX_S}] with a g0_cap_receipt ({R10_G0_CAP_AUTHORITY})')
        if cap < G0_CAP_DEFAULT_S and receipt is None:
            raise ValueError(f'thermal.g0_cap_s must be finite and in [{G0_CAP_DEFAULT_S}, {G0_CAP_MAX_S}]; '
                             f'a cap below {G0_CAP_DEFAULT_S} s needs the lead\'s ruling 1(f) receipt '
                             f'(thermal.g0_cap_receipt, {R10_G0_CAP_AUTHORITY})')
    if receipt is not None and not (policy.get('g0_cap_s', G0_CAP_DEFAULT_S) < G0_CAP_DEFAULT_S):
        raise ValueError(f'thermal.g0_cap_receipt only accompanies a g0_cap_s below {G0_CAP_DEFAULT_S} s '
                         f'({R10_G0_CAP_AUTHORITY})')
    for name in ('delta_fast_c', 'delta_slow_c', 'turn_cap_s'):
        v = policy[name]
        if type(v) not in (int, float) or not math.isfinite(v) or v <= 0:
            raise ValueError(f'thermal.{name} must be finite and positive')
    if policy['turn_cap_s'] > 300:
        raise ValueError('thermal.turn_cap_s exceeds 300')
    for name in ('per_turn', 'heavy'):
        if type(policy[name]) is not bool:
            raise ValueError(f'thermal.{name} must be boolean')
    chunk = policy['chunk_tokens']
    if type(chunk) is not int or chunk < 256 or chunk % 256:
        raise ValueError('thermal.chunk_tokens must be a positive multiple of 256')
    if policy['heavy'] and not policy['per_turn']:
        raise ValueError('heavy cells require per-turn gates and holds')
    ref = policy['window_reference']
    if not isinstance(ref, Mapping) or ref.get('role') not in ('capture', 'consume'):
        raise ValueError('thermal.window_reference requires a capture or consume role')
    if ref['role'] == 'capture' and set(ref) != {'role'}:
        raise ValueError('capture window_reference has unknown source fields')
    if ref['role'] == 'consume':
        if set(ref) != {'role', 'source_run_id', 'source_config_sha256'}:
            raise ValueError('consume window_reference requires both source fields')
        if (not isinstance(ref['source_run_id'], str) or not ref['source_run_id']
                or not isinstance(ref['source_config_sha256'], str)
                or len(ref['source_config_sha256']) != 64
                or any(c not in '0123456789abcdef' for c in ref['source_config_sha256'])):
            raise ValueError('consume window_reference source fields are invalid')
    policy['window_reference'] = dict(ref)
    return policy


def load_window_reference(policy, context):
    """Load and independently verify a consumer's source-bundle custody record."""
    ref = policy['window_reference']
    if ref['role'] == 'capture':
        return None, None
    from joulewise.bundle import sanitize_id_component
    source_id = ref['source_run_id']
    if sanitize_id_component(source_id) != source_id or source_id == context.run_id:
        raise WindowReferenceRefused('thermal.window_reference_path_refused')
    root = context.bundle_path.parent.resolve()
    source = context.bundle_path.parent / source_id
    output = source / 'outputs'
    path = output / 'align_window_reference.json'
    try:
        if any(p.is_symlink() for p in (source, output, path)):
            raise WindowReferenceRefused('thermal.window_reference_path_refused')
        resolved = path.resolve()
        if root not in resolved.parents:
            raise WindowReferenceRefused('thermal.window_reference_path_refused')
        raw = path.read_bytes()
    except WindowReferenceRefused:
        raise
    except FileNotFoundError as exc:
        raise WindowReferenceRefused('thermal.window_reference_missing') from exc
    except OSError as exc:
        raise WindowReferenceRefused('thermal.window_reference_path_refused') from exc
    try:
        record = json.loads(raw)
        digest = record.pop('record_sha256')
        fields = {'schema', 'status', 'source', 'sensors', 'sensors_policy_sha256', 'rule',
                  'span_ns', 'span_epoch_ns', 'coverage_fraction', 'samples', 'fast_c',
                  'slow_c', 'journal'}
        if (set(record) != fields or record.get('schema') != REFERENCE_SCHEMA
                or record.get('status') not in ('captured', 'unobserved')
                or hashlib.sha256(_canonical(record)).hexdigest() != digest):
            raise ValueError
        complete = {**record, 'record_sha256': digest}
        if raw != _canonical(complete) + b'\n':
            raise ValueError
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise WindowReferenceRefused('thermal.window_reference_corrupt') from exc
    config_path = source / 'config.json'
    try:
        config_digest = hashlib.sha256(config_path.read_bytes()).hexdigest()
    except OSError as exc:
        raise WindowReferenceRefused('thermal.window_reference_binding_mismatch') from exc
    expected_source = {'run_id': source_id, 'config_sha256': ref['source_config_sha256']}
    if (record.get('source') != expected_source or config_digest != ref['source_config_sha256']
            or record.get('sensors') != policy['sensors']
            or record.get('sensors_policy_sha256') != _policy_digest(policy['sensors'])):
        raise WindowReferenceRefused('thermal.window_reference_binding_mismatch')
    if record.get('journal') != 'outputs/align_thermal.jsonl':
        raise WindowReferenceRefused('thermal.window_reference_corrupt')
    journal_path = source / record['journal']
    try:
        journal_raw = journal_path.read_bytes()
        journal_digest = hashlib.sha256(journal_raw).hexdigest()
    except OSError as exc:
        raise WindowReferenceRefused('thermal.window_reference_unverified') from exc
    if record['status'] == 'captured':
        try:
            journal_rows = sample_rows([json.loads(line) for line in journal_raw.splitlines() if line.strip()])
            end = record['span_ns'][1]
            keys = (policy['sensors']['s_fast'], policy['sensors']['s_slow'])
            good = _good_window_rows(journal_rows, end, keys)
            coverage = _window_coverage(journal_rows, end, keys)['sample_fraction']
            samples = [[r['monotonic_ns'], r['sensors'][keys[0]], r['sensors'][keys[1]]] for r in good]
            if (coverage is None or coverage < .9 or samples != record['samples']
                    or median(x[1] for x in samples) != record['fast_c']
                    or median(x[2] for x in samples) != record['slow_c']):
                raise ValueError
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise WindowReferenceRefused('thermal.window_reference_unverified') from exc
        value = {'fast_c': record['fast_c'], 'slow_c': record['slow_c'],
                 'source_member': source_id, 'span_ns': record['span_ns']}
    else:
        value = None
    custody = {'record_sha256': digest, 'source_run_id': source_id,
               'source_config_sha256': ref['source_config_sha256'],
               'source_journal_sha256': journal_digest}
    return value, custody


def _good_window_rows(rows, end_ns, keys):
    start = end_ns - 60 * NS
    return [r for r in rows if start <= r['monotonic_ns'] < end_ns
            and 0 <= r['finished']['monotonic_after_ns'] - r['monotonic_ns'] <= NS
            and all(k not in r.get('errors', {}) and valid_value(k, r['sensors'].get(k)) for k in keys)]


def _window_coverage(rows, end_ns, selected):
    counter = Coverage(end_ns - 60 * NS, selected)
    if rows:
        counter.grid_ns = rows[0]['monotonic_ns']
    for row in rows:
        if counter.start_ns - NS <= row['monotonic_ns'] <= end_ns + NS:
            counter.observe(row['monotonic_ns'], row['finished']['monotonic_after_ns'], row)
    return counter.report(end_ns)['all_keys']


def slow_slope(rows, end_ns, key):
    """OLS °C/min on actual times in the preceding 60 seconds; no interpolation."""
    selected = _good_window_rows(rows, end_ns, (key,))
    good = [(r['monotonic_ns'], r['sensors'][key]) for r in selected]
    fraction = _window_coverage(rows, end_ns, (key,))['sample_fraction']
    if fraction is None or fraction < .9:
        return None
    x = [(t - end_ns) / NS for t, _ in good]
    y = [v for _, v in good]
    xm, ym = sum(x) / len(x), sum(y) / len(y)
    denom = sum((t - xm) ** 2 for t in x)
    return 60 * sum((t - xm) * (v - ym) for t, v in zip(x, y)) / denom if denom else None


def drain_decode(stream, mx=None):
    """Evaluate live generator arrays, including MLX's asynchronous lookahead.

    Only suspended generator locals and their built-in containers are visited;
    model objects are not traversed. This drains queued work before hold entry,
    without requesting a token or consuming RNG state. R1 must qualify this on
    pinned mlx-lm 0.31.3, including token identity and resume transients.
    """
    if mx is None:
        import mlx.core as mx
    seen, arrays, streams = set(), [], []
    native_frame = False
    stream_type = getattr(mx, 'Stream', None)

    def visit(value):
        nonlocal native_frame
        if id(value) in seen:
            return
        seen.add(id(value))
        if isinstance(value, mx.array):
            arrays.append(value)
        elif isinstance(value, GeneratorType):
            if value.gi_frame is not None:
                globals_ = value.gi_frame.f_globals
                native_frame |= str(globals_.get('__name__', '')).startswith('mlx_lm')
                # The inner generate_step iterator can live only on Python's
                # evaluation stack, outside f_locals. Its queued lookahead is
                # still covered by the module's explicit generation stream.
                for candidate in tuple(globals_.values()):
                    if isinstance(stream_type, type) and isinstance(candidate, stream_type):
                        if all(candidate is not s for s in streams):
                            streams.append(candidate)
                generation_stream = globals_.get('generation_stream')
                if generation_stream is not None and all(generation_stream is not s for s in streams):
                    streams.append(generation_stream)
                for child in tuple(value.gi_frame.f_locals.values()):
                    visit(child)
            visit(value.gi_yieldfrom)
        elif isinstance(value, (tuple, list)):
            for child in value:
                visit(child)
        elif isinstance(value, dict):
            for child in value.values():
                visit(child)
    visit(stream)
    if arrays:
        mx.eval(*arrays)
    if native_frame and not streams:
        raise RuntimeError('thermal.lookahead_generation_stream_unobserved')
    for stream_ in streams:
        mx.synchronize(stream_)
    mx.synchronize()


class ThermalSession:
    """One prepare-to-cleanup sidecar, using the same injected clock as turns.

    SystemClock uses a 1 Hz thread. Fake clocks explicitly call sample() as
    time advances. status_reader returns observed os_level / pm_state, plus
    their source stamps (PM observation time is required at G0); it may be
    bound by an ALIGN launch adapter.
    With no callback a bundle-local outputs/align_thermal_status.json supplies
    {os_level, pm_state, pm_observed_ns, monotonic_ns}.
    No path in the episode spec is followed.
    """
    def __init__(self, policy, clock, context=None, *, reader=None, status_reader=None):
        from joulewise.hazards.base import Context
        from joulewise.clock import SystemClock
        self.policy = validate_gate_policy(policy)
        self.clock, self.context = clock, context
        self.status_reader = status_reader
        self.intervals, self.events, self.flags = [], [], []
        self.reference, self.custody = (load_window_reference(self.policy, context)
                                        if context is not None else (None, None))
        if self.policy['window_reference']['role'] == 'consume' and self.reference is None:
            self.flags.append('thermal.window_reference_unobserved')
        self.episode_reference = None
        if isinstance(clock, SystemClock):
            ctx = Context()  # Real monotonic/raw/epoch stamps; never synthesize RAW.
            if context is None:
                raise ValueError('thermal collection requires bundle outputs')
        else:
            ctx = Context(clocks=_EpisodeClocks(self))
        self.sidecar = thermal.Sidecar(context.outputs_dir if context is not None else None,
                               self.policy['sensors'], reader=reader, ctx=ctx,
                               status_reader=self._status)

    @property
    def reader(self):
        return self.sidecar.reader

    @property
    def rows(self):
        return sample_rows(self.sidecar.snapshot())

    def start(self):
        from joulewise.clock import SystemClock
        background = isinstance(self.clock, SystemClock)
        self.sidecar.start(background=background)
        if not background:
            self.sample()

    def _status(self):
        if self.status_reader is not None:
            return dict(self.status_reader())
        if self.context is None:
            return {}
        try:
            value = json.loads((self.context.outputs_dir / 'align_thermal_status.json').read_text())
            age = monotonic_ns(self.clock.stamp()) - value['monotonic_ns']
            return value if 0 <= age <= 2 * NS else {}
        except (OSError, ValueError, KeyError, TypeError):
            return {}

    def sample(self):
        """Deterministic seam: the sole collector owns the read and journal."""
        return sample_rows([self.sidecar.tick()])[0]

    def _collector_fault(self):
        """A dead or stopped 1 Hz collector can never satisfy any gate (WP8 F2)."""
        sidecar = self.sidecar
        if sidecar._error is not None:
            return f'{type(sidecar._error).__name__}:{sidecar._error}'
        if sidecar._closed:
            return 'collector_closed'
        thread = sidecar._thread
        if thread is not None:
            if sidecar._stop.is_set():
                return 'collector_stopped'
            if hasattr(thread, 'is_alive') and not thread.is_alive():
                return 'collector_thread_dead'
        return None

    @property
    def holds_suppressed(self):
        """No further hold once the member is certain to be thermally excluded.

        After thermal.state_unobserved, or after a G0 that did not release (no
        episode reference), every hold could only be a full-cap blind wait for
        a member the desk already excludes (WP8 F2).
        """
        return ('thermal.state_unobserved' in self.flags
                or (self.episode_reference is None
                    and any(r['kind'] == 'G0' for r in self.intervals)))

    def capture_reference(self, member):
        """Called at warmup entry: the final 60 s of first member's idle."""
        if self.policy['window_reference']['role'] != 'capture' or self.reference is not None:
            return
        now = monotonic_ns(self.clock.stamp())
        rows = [r for r in self.rows if now - 60 * NS <= r['monotonic_ns'] < now]
        sensors = self.policy['sensors']
        # Missing baseline never becomes a guessed release reference.
        good = _good_window_rows(rows, now, (sensors['s_fast'], sensors['s_slow']))
        fraction = _window_coverage(self.rows, now, (sensors['s_fast'], sensors['s_slow']))['sample_fraction']
        captured = fraction is not None and fraction >= .9
        if not captured:
            self.flags.append('thermal.state_unobserved')
            fast_c = slow_c = None
        else:
            fast_c = median(r['sensors'][sensors['s_fast']] for r in good)
            slow_c = median(r['sensors'][sensors['s_slow']] for r in good)
            self.reference = {'fast_c': fast_c, 'slow_c': slow_c,
                              'source_member': member, 'span_ns': [now - 60 * NS, now]}
        if self.context is None:
            return
        config_raw = (self.context.bundle_path / 'config.json').read_bytes()
        stamp = self.clock.stamp()
        epoch_end = round(stamp.epoch_s * NS)
        record = {'schema': REFERENCE_SCHEMA, 'status': 'captured' if captured else 'unobserved',
                  'source': {'run_id': self.context.run_id,
                             'config_sha256': hashlib.sha256(config_raw).hexdigest()},
                  'sensors': sensors, 'sensors_policy_sha256': _policy_digest(sensors),
                  'rule': {'anchor': 'warmup_entry', 'window_s': 60, 'statistic': 'median',
                           'min_coverage': .9},
                  'span_ns': [now-60*NS, now], 'span_epoch_ns': [epoch_end-60*NS, epoch_end],
                  'coverage_fraction': fraction, 'samples': [[r['monotonic_ns'],
                      r['sensors'][sensors['s_fast']], r['sensors'][sensors['s_slow']]] for r in good]
                      if captured else [],
                  'fast_c': fast_c, 'slow_c': slow_c,
                  'journal': 'outputs/align_thermal.jsonl'}
        record['record_sha256'] = hashlib.sha256(_canonical(record)).hexdigest()
        data = _canonical(record) + b'\n'
        final = self.context.outputs_dir / 'align_window_reference.json'
        temporary = self.context.outputs_dir / f'.align_window_reference.{os.getpid()}.tmp'
        try:
            fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                os.write(fd, data)
                os.fsync(fd)
            finally:
                os.close(fd)
            os.link(temporary, final)
            directory = os.open(self.context.outputs_dir, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        except OSError as exc:
            self.flags.append('thermal.window_reference_write_failed')
            raise WindowReferenceRefused('thermal.window_reference_write_failed') from exc
        finally:
            temporary.unlink(missing_ok=True)
        self.custody = {'record_sha256': record['record_sha256'],
                        'source_run_id': self.context.run_id,
                        'source_config_sha256': record['source']['config_sha256'],
                        'source_journal_sha256': None}

    def wait(self, kind, *, turn=0, token_count=None, deadman=None, defer_resume=False):
        """G0 proceeds on timeout; unobserved gates wait then proceed with X4.

        G1/H stop only on an actual timeout or the member deadman.
        """
        if kind not in ('G0', 'G1', 'H'):
            raise ValueError('unknown thermal gate')
        entry = self.clock.stamp()
        fault = self._collector_fault()
        if fault is not None:
            self.flags.append('thermal.collector_failed')
            raise ThermalFault('thermal.collector_failed', fault)
        if kind == 'G0':
            # Without a bound status source G0 can never release; fail the
            # member now rather than after the G0 timeout (WP8 F5). Judge
            # only recent rows; a coverage gap is left to the X4 path.
            entry_ns = monotonic_ns(entry)
            recent = [r for r in self.rows if 0 <= entry_ns - r['monotonic_ns'] <= 10 * NS]
            if recent and not any(_status_observed(r.get('status')) for r in recent):
                self.flags.append('thermal.status_source_missing')
                raise ThermalFault('thermal.status_source_missing')
        self.sidecar.event('align_thermal_hold' if kind == 'H' else 'align_thermal_gate',
                           {'state': 'begin', 'gate_kind': kind, 'turn': turn, 'token_count': token_count,
                            'entry_stamp': _stamp_record(entry)})
        start = monotonic_ns(entry)
        entry_slope = slow_slope(self.rows, start, self.policy['sensors']['s_slow'])
        cap = self.policy.get('g0_cap_s', G0_CAP_DEFAULT_S) if kind == 'G0' else self.policy['turn_cap_s']
        reference = self.reference if kind == 'G0' else self.episode_reference
        required = 10 if kind == 'G0' else 5
        fast, slow = (self.policy['sensors'][k] for k in ('s_fast', 's_slow'))
        # G1/H without an episode reference: G0 did not release (WP8 F6).
        unreferenced = kind != 'G0' and reference is None
        consecutive, last_ns, unobserved = 0, None, reference is None
        release = None
        reason = 'timeout'
        latest, slope = None, None
        try:
            with deadman.guard() if deadman is not None else nullcontext():
                while True:
                    fault = self._collector_fault()
                    if fault is not None:
                        self.flags.append('thermal.collector_failed')
                        raise ThermalFault('thermal.collector_failed', fault)
                    now = monotonic_ns(self.clock.stamp())
                    rows = self.rows
                    latest = rows[-1] if rows else None
                    # Missing slots, late reads and missing keys all count as failed reads.
                    fraction = _window_coverage(rows, now, (fast, slow))['sample_fraction']
                    if fraction is None or fraction < .9:
                        unobserved = True
                        unreferenced = False
                    slope = slow_slope(rows, now, slow)
                    # Consume every queued observation in order. Checking only
                    # the last row can hide an intervening out-of-band sample.
                    new_rows = (rows[-1:] if last_ns is None else
                                [r for r in rows if r['monotonic_ns'] > last_ns])
                    for sample in new_rows:
                        continuous = last_ns is None or 0 < sample['monotonic_ns'] - last_ns <= 2 * NS
                        last_ns = sample['monotonic_ns']
                        good = (not unobserved and continuous and 0 <= now - last_ns <= 2 * NS
                                and all(valid_value(k, sample['sensors'].get(k)) for k in (fast, slow))
                                and sample['sensors'][fast] <= reference['fast_c'] + self.policy['delta_fast_c']
                                and sample['sensors'][slow] <= reference['slow_c'] + self.policy['delta_slow_c'])
                        if kind == 'G0':
                            status = sample['status']
                            pm_ns = status.get('pm_observed_ns')
                            sample_slope = slow_slope(rows, last_ns, slow)
                            good = (good and sample_slope is not None and abs(sample_slope) <= .2
                                    and status.get('os_level') == 0 and status.get('pm_state') == 'Nominal'
                                    and type(pm_ns) is int and 0 <= now - pm_ns <= 2 * NS)
                        consecutive = consecutive + 1 if good else 0
                    if new_rows and consecutive >= required:
                        release, reason = new_rows[-1], 'released'
                        break
                    if deadman is not None and deadman.expired():
                        reason = 'deadman'
                        break
                    elapsed = (now - start) / NS
                    # The unobserved G0 wait never outlasts the armed cap: under
                    # R10-2(a) the cap can be below 300 s, and ruling 1(f)'s G0
                    # term is the armed cap.
                    limit = min(G0_UNOBSERVED_LIMIT_S, cap) if unobserved and kind == 'G0' else cap
                    if elapsed >= limit:
                        break
                    delay = min(1, limit - elapsed)
                    if self.sidecar._thread is None:
                        # Deterministic clocks tick the same collector on its
                        # absolute grid. Parsing/phase costs must not drift it.
                        grid = self.sidecar.counter.start_ns
                        due = grid + ((now - grid) // NS + 1) * NS
                        delay = min(delay, (due - now) / NS)
                    if deadman is not None:
                        delay = min(delay, max(0, deadman.remaining_s()))
                    prior_seq = self.sidecar._seq
                    self.clock.sleep(delay)
                    if self.sidecar._thread is None and self.sidecar._seq == prior_seq:
                        self.sample()
        except DeadmanExpired:
            reason = 'deadman'
        exit_stamp = self.clock.stamp()
        if unobserved and unreferenced:
            # Sensors were observed; the member is already excluded by its G0
            # flag. Keep it in the desk's observed set (U1 coverage/G0 counts).
            if 'thermal.episode_reference_unobserved' not in self.flags:
                self.flags.append('thermal.episode_reference_unobserved')
        elif unobserved:
            if 'thermal.state_unobserved' not in self.flags:
                self.flags.append('thermal.state_unobserved')
        elif reason == 'timeout':
            self.flags.append('thermal.start_gate_timeout' if kind == 'G0' else
                              f'thermal.{"hold" if kind == "H" else "gate"}_timeout:{turn}')
        if reason == 'deadman':
            self.flags.append(f'episode.deadman:{turn}')
        values = release or latest
        release_values = ({'fast_c': values['sensors'].get(fast), 'slow_c': values['sensors'].get(slow)}
                          if values else {'fast_c': None, 'slow_c': None})
        if kind == 'G0':
            # Only a released G0 defines the episode reference; a hot sample
            # after a timeout/unobserved/deadman exit never does (WP8 F6).
            self.episode_reference = (release_values if reason == 'released'
                                      and all(v is not None for v in release_values.values()) else None)
        row = {'kind': kind, 'turn': turn, 'token_count': token_count,
               'start_ns': start, 'end_ns': monotonic_ns(exit_stamp),
               'entry_stamp': _stamp_record(entry), 'exit_stamp': _stamp_record(exit_stamp),
               'entry_epoch_s': entry.epoch_s, 'exit_epoch_s': exit_stamp.epoch_s,
               'clock': 'episode_monotonic_ns', 'duration_s': (monotonic_ns(exit_stamp) - start) / NS,
               'reference': reference, 'release': release_values, 'slope_c_per_min': slope,
               'entry_slope_c_per_min': entry_slope,
               'entry_sensors': self._entry_values(start),
               'exit_sample_ns': values['monotonic_ns'] if values else None,
               'outcome': 'unobserved' if unobserved and reason != 'deadman' else reason}
        self.intervals.append(row)
        if not (kind == 'H' and defer_resume and (reason == 'released' or (unobserved and reason != 'deadman'))):
            self.persist_interval(row)
        phase = 'align_thermal_hold' if kind == 'H' else 'align_thermal_gate'
        self.events.extend([RuntimeEvent(entry.epoch_s, 'phase_start', phase, kind, row),
                            RuntimeEvent(exit_stamp.epoch_s, 'phase_end', phase, kind, row)])
        return row

    def resume_hold(self, row):
        """Stamp at the stream dispatch boundary; perform no journal I/O here."""
        from dataclasses import replace
        stamp = self.clock.stamp()
        row['condition_met_stamp'] = row['exit_stamp']
        row.update(exit_stamp=_stamp_record(stamp), exit_epoch_s=stamp.epoch_s,
                   end_ns=monotonic_ns(stamp), duration_s=(monotonic_ns(stamp)-row['start_ns'])/NS)
        for i in range(len(self.events)-1, -1, -1):
            if self.events[i].metadata is row and self.events[i].event_type == 'phase_end':
                self.events[i] = replace(self.events[i], timestamp_s=stamp.epoch_s)
                break

    def persist_interval(self, row):
        """Publish a finalized interval after dispatch (or after cancellation)."""
        phase = 'align_thermal_hold' if row['kind'] == 'H' else 'align_thermal_gate'
        self.sidecar.event(phase, {'state': 'end', 'gate': row})

    def _entry_values(self, start):
        prior = [r for r in self.rows if r['monotonic_ns'] <= start]
        return prior[-1]['sensors'] if prior else {}

    def record(self):
        return {'policy': self.policy, 'window_reference': self.reference,
                'episode_reference': self.episode_reference, 'intervals': list(self.intervals),
                'flags': list(dict.fromkeys(self.flags)), 'custody': self.custody}

    def close(self):
        try:
            self.sidecar.stop()
        finally:
            close = getattr(self.status_reader, 'close', None)
            if close is not None:
                close()


class PowermetricsStatus:
    """Read-only tap of the already-running telemetry adapter; starts no sampler.

    Bind with bind_thermal_status at v4 adapter construction. Read only that
    adapter's current capture capability, including complete NUL-framed plists;
    never search for a capture or infer Nominal from an absent status.
    """
    def __init__(self, telemetry, clock, *, notify_reader=None):
        self.telemetry, self.clock = telemetry, clock
        self.notify = notify_reader
        self.path, self.position, self.pending = None, 0, b''
        self.pm_state, self.pm_observed_ns = None, None

    def __call__(self):
        import plistlib
        from joulewise.hazards.thermal import NotifyReader
        if self.notify is None:
            self.notify = NotifyReader()
        level = self.notify.read()
        path = getattr(self.telemetry, '_capture_path', None)
        if path != self.path:
            self.path, self.position, self.pending = path, 0, b''
            self.pm_state, self.pm_observed_ns = None, None
        if path is not None:
            with path.open('rb') as handle:
                handle.seek(self.position)
                chunk = handle.read(8*1024*1024)
                self.position += len(chunk)
            self.pending += chunk
            if len(self.pending) > 8*1024*1024:
                raise ValueError('powermetrics status tap incomplete frame exceeds bound')
            # A complete XML document may precede its NUL separator.
            if b'</plist>' in self.pending:
                end = self.pending.rindex(b'</plist>') + len(b'</plist>')
                complete, self.pending = self.pending[:end], self.pending[end:].lstrip(b'\0\n\r ')
                previous = complete.rfind(b'</plist>', 0, end-len(b'</plist>'))
                raw = complete[previous+len(b'</plist>') if previous >= 0 else 0:].strip(b'\0\n\r ')
                document = plistlib.loads(raw)
                self.pm_state = document.get('thermal_pressure')
                self.pm_observed_ns = monotonic_ns(self.clock.stamp())
        return {'os_level': level, 'pm_state': self.pm_state,
                'pm_observed_ns': self.pm_observed_ns, 'monotonic_ns': monotonic_ns(self.clock.stamp())}

    def close(self):
        if self.notify is not None:
            self.notify.close()


def bind_thermal_status(episode_adapter, telemetry_adapter):
    """v4 launcher wiring; no pinned controller/telemetry changes required."""
    feed = PowermetricsStatus(telemetry_adapter, episode_adapter.clock)
    episode_adapter.thermal_status_reader = feed
    return feed


class ThermalRegistry:
    """Per-run ALIGN registry which binds the runtime to its actual telemetry.

    Pass registry=ThermalRegistry() to the existing run_benchmark. Delegates
    every other adapter method unchanged. The v4 launcher must select this
    registry; the legacy runner and anchors keep their default registry.
    """
    def __init__(self, delegate=None, *, thermal_factory=None, status_factory=None,
                 powermode_reader=None):
        if delegate is None:
            from joulewise import adapters
            delegate = adapters
        self.delegate = delegate
        self.runtime = self.telemetry = None
        self.thermal_factory = thermal_factory
        self.status_factory = status_factory or PowermetricsStatus
        # Council ruling 7: the episode bundle records the observed AC
        # powermode; None keeps the adapter's read-only pmset default.
        self.powermode_reader = powermode_reader

    def __getattr__(self, name):
        return getattr(self.delegate, name)

    def _bind(self):
        if self.runtime is None or self.telemetry is None:
            return
        from joulewise.align.apple.workload import EpisodeRuntimeAdapter
        if isinstance(self.runtime, EpisodeRuntimeAdapter):
            self.runtime.thermal_factory = self.thermal_factory
            self.runtime.thermal_status_reader = self.status_factory(self.telemetry, self.runtime.clock)
            if self.powermode_reader is not None:
                self.runtime.powermode_reader = self.powermode_reader

    def resolve_runtime(self, config, clock):
        self.runtime, failure = self.delegate.resolve_runtime(config, clock)
        self._bind()
        return self.runtime, failure

    def resolve_telemetry(self, config, clock):
        self.telemetry, failure = self.delegate.resolve_telemetry(config, clock)
        self._bind()
        return self.telemetry, failure


def split_decode_events(events, holds):
    """Represent holds beside decode phases, preserving pinned phase validation.

    The controller/reducer forbids overlapping phases on one power source.
    Keep native token/prefill events and split only decode start/end support;
    the thermal session supplies the intervening hold phase events.
    """
    from dataclasses import replace
    starts = [e for e in events if e.phase == 'decode' and e.event_type == 'phase_start']
    ends = [e for e in events if e.phase == 'decode' and e.event_type == 'phase_end']
    if not holds:
        return events
    if len(starts) != 1 or len(ends) != 1:
        raise ValueError('held decode needs exactly one native decode phase')
    first, last = starts[0], ends[0]
    result = [e for e in events if not (e.phase == 'decode' and e.event_type in ('phase_start', 'phase_end'))]
    cursor = first.timestamp_s
    for hold in holds:
        a = hold.get('entry_epoch_s', hold['entry_stamp']['epoch_ns']/NS)
        b = hold.get('exit_epoch_s', hold['exit_stamp']['epoch_ns']/NS)
        if not cursor <= a <= b <= last.timestamp_s:
            raise ValueError('hold outside native decode phase')
        if cursor < a:
            result.extend([replace(first, timestamp_s=cursor), replace(last, timestamp_s=a)])
        cursor = b
    if cursor < last.timestamp_s:
        result.extend([replace(first, timestamp_s=cursor), last])
    return sorted(result, key=lambda e: e.timestamp_s)
