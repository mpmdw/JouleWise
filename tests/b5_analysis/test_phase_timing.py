"""D-188 TIMERS: two-tier phase timers (joulewise/b5_analysis/phase_timing.py).

Synthetic only. A fake clock and a fake frame source give deterministic
tables; raising seams prove the timers can lose timing but never change a run.
"""
from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

from joulewise.b5_analysis import phase_timing as pt

ROOT = Path(__file__).resolve().parents[2]


class FakeClock:
    def __init__(self, start=10 ** 12):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds=0, ms=0):
        self.now += seconds * 10 ** 9 + ms * 10 ** 6


class FakeUsage:
    ru_maxrss = 300 * (1 << 20) if sys.platform == 'darwin' else 300 * 1024


def _code(module, qualname):
    target = importlib.import_module(module)
    for part in qualname.split('.'):
        target = getattr(target, part)
    while hasattr(target, '__wrapped__'):
        target = target.__wrapped__
    return target.__code__


def _lines(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


class _Scratch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='phase-timing-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.restricted = self.root / 'custody/dry-run/restricted'
        (self.restricted / 'logs').mkdir(parents=True)
        self.structure = self.root / 'outside/phases.jsonl'
        self.structure.parent.mkdir()
        self.assertIsNone(pt.current())

    def tearDown(self):
        self.assertIsNone(pt.current())

    def open_log(self):
        return pt.open_structure_log(self.structure, custody=self.root / 'custody', repo=ROOT)


class DeterministicTableTests(_Scratch):
    """Fake clock and fake sampler seam: exact tables in both tiers."""

    def make(self, **kw):
        self.clock, self.cpu = FakeClock(), FakeClock(5 * 10 ** 9)
        self.stack = []
        options = dict(clock=self.clock, cpu_clock=self.cpu, frames=lambda: list(self.stack),
                       rusage=lambda: FakeUsage, loadavg=lambda: (2.5, 0, 0), start_sampler=False,
                       sample_ms=1000, heartbeat_s=300, mode='blind-dry-run')
        options.update(kw)
        return pt.session(self.open_log(), **options)

    def test_structure_and_restricted_tables(self):
        reduce_code = _code('joulewise.reduce', '_reduce')
        strict_code = _code('joulewise.cli', '_strict_problems')
        unlabelled = _code('json', 'dumps')
        with self.make() as timer:
            pt.attach_restricted(self.restricted)
            pt.step_begin('5')
            program = type('M', (), {'__module__': 'scripts.mint_floor_artifact_generalized'})()
            with pt.program_span(program, ['--x']):
                self.stack[:] = [strict_code, reduce_code]   # innermost first
                self.clock.advance(seconds=2); self.cpu.advance(seconds=1)
                timer.sample()
                self.stack[:] = [unlabelled]
                self.clock.advance(seconds=1)
                timer.sample()
                with pt.pool_wait():
                    self.stack[:] = [strict_code]
                    self.clock.advance(seconds=4)
                    timer.sample()
                pt.pool_batch('joulewise.cli:_strict_problems',
                              [{'wall_ns': 3 * 10 ** 9, 'cpu_ns': 2 * 10 ** 9,
                                'phases': {'k.strict': [3 * 10 ** 9, 3 * 10 ** 9]}},
                               {'wall_ns': 5 * 10 ** 9, 'cpu_ns': 4 * 10 ** 9, 'phases': {}}, None],
                              4 * 10 ** 9, 3)
            pt.merge_child({'wall_ns': 7 * 10 ** 9, 'cpu_ns': 6 * 10 ** 9,
                            'phases': {'k.reduce': [6 * 10 ** 9, 7 * 10 ** 9], 'not-a-label': [1, 1]},
                            'programs': [['prog.cli.reduce', 7 * 10 ** 9, 6 * 10 ** 9]], 'member': {}, 'pool': {}})
            pt.step_end('5')
            pt.run_end()
        structure = _lines(self.structure)
        self.assertEqual(structure, [
            {'event': 'run_start', 'mode': 'blind-dry-run', 'schema': pt.SCHEMA},
            {'elapsed_s': 0, 'event': 'step_begin', 'step': '5'},
            {'event': 'step_end', 'step': '5', 'wall_s': 7},
            {'event': 'run_end', 'total_s': 7}])
        rows = _lines(self.restricted / 'logs' / pt.RESTRICTED_LOG)
        self.assertEqual([row['event'] for row in rows], ['run_start', 'step_begin', 'step_end', 'run_end'])
        end = rows[2]
        self.assertEqual(end['wall_ms'], 7000)
        self.assertEqual(end['cpu_ms'], 1000)
        self.assertEqual(end['serial_ms'], 3000)          # 7 s wall minus the exact 4 s pool wait
        self.assertEqual(end['spans_ms'], {'pool.wait': 4000})
        self.assertEqual(end['maxrss_mib'], 300)
        self.assertEqual(end['load_x100'], {'start': 250, 'end': 250, 'max': 250})
        self.assertEqual(end['programs'], {
            'child:prog.cli.reduce': {'count': 1, 'wall_ms': 7000, 'cpu_ms': 6000, 'max_ms': 7000},
            'driver:prog.mint': {'count': 1, 'wall_ms': 7000, 'cpu_ms': 1000, 'max_ms': 7000}})
        driver = end['phases']['driver']
        self.assertEqual(driver['k.strict'], [2000, 6000])     # self: innermost labelled frame; incl: on stack
        self.assertEqual(driver['k.reduce'], [0, 2000])        # inclusive only
        self.assertEqual(driver['pool.wait'], [4000, 4000])    # explicit span wins over the frame label
        self.assertEqual(driver['other'], [1000, 0])
        self.assertEqual(driver['prog.mint'], [0, 7000])
        self.assertEqual(end['unattributed_ms'], 1000)
        self.assertEqual(end['sampled_ms'], 7000)
        self.assertEqual(end['phases']['child'], {'k.reduce': [6000, 7000]})
        self.assertEqual(end['phases']['member'], {'k.strict': [3000, 3000]})
        self.assertEqual(end['pool'], {'k.strict': {'batches': 1, 'tasks': 2, 'wall_ms': 4000, 'busy_ms': 8000,
                                                    'cpu_ms': 6000, 'max_task_ms': 5000, 'pool_size': 3,
                                                    'busy_permille': 666}})
        self.assertEqual(end['children'], {'tasks': 1, 'wall_ms': 7000, 'cpu_ms': 6000})
        self.assertEqual(end['top'][0], ['cli:_strict_problems', 6000])
        for line in (self.restricted / 'logs' / pt.RESTRICTED_LOG).read_bytes().splitlines(keepends=True):
            pt.validate_phase_line(line, 'restricted')
        from scripts import b5_phase_report as report
        out = io.StringIO()
        self.assertEqual(report.main(['--detail', str(self.restricted / 'logs' / pt.RESTRICTED_LOG)], out=out), 0)
        text = out.getvalue()
        self.assertIn('step 5: wall 7 s, driver cpu 1 s, serial 3 s, unattributed 1 s', text)
        self.assertIn('driver self: pool.wait 4s, k.strict 2s, other 1s', text)
        self.assertIn('pool k.strict: batches 1, busy 8 s over 4 s x 3 (66.6%)', text)
        self.assertIn('programs: child:prog.cli.reduce x1 7s, driver:prog.mint x1 7s', text)

    def test_heartbeat_is_step_level_outside_and_labelled_inside(self):
        strict_code = _code('joulewise.cli', '_strict_problems')
        with self.make(heartbeat_s=300) as timer:
            pt.attach_restricted(self.restricted)
            pt.step_begin('3b')
            pt.pool_progress(3, 12)
            self.stack[:] = [strict_code]
            for _ in range(6):
                self.clock.advance(seconds=100)
                timer.sample()
            pt.step_end('3b')
        structure = _lines(self.structure)
        beats = [row for row in structure if row['event'] == 'heartbeat']
        self.assertEqual(beats, [{'elapsed_s': 300, 'event': 'heartbeat', 'step': '3b', 'step_s': 300},
                                 {'elapsed_s': 600, 'event': 'heartbeat', 'step': '3b', 'step_s': 600}])
        inside = [row for row in _lines(self.restricted / 'logs' / pt.RESTRICTED_LOG) if row['event'] == 'heartbeat']
        self.assertEqual(inside[0]['label'], 'k.strict')
        self.assertEqual(inside[0]['progress_permille'], 250)
        self.assertEqual(inside[0]['top'], [['k.strict', 300000]])

    def test_unknown_step_and_span_labels_are_ignored(self):
        with self.make() as timer:
            pt.step_begin('7')
            with pt.span('k.invented'):
                pass
            self.assertIsNone(timer.step)
            pt.step_begin('2')
            pt.step_end('4')        # not the open step: ignored
            self.assertEqual(timer.step, '2')
            pt.step_end('2')
        self.assertEqual([row['event'] for row in _lines(self.structure)],
                         ['run_start', 'step_begin', 'step_end', 'run_end'])


def _workload(log):
    """A miniature driver: fixed outputs, every hook called."""
    out = []
    for step in ('0', '1', '5'):
        pt.step_begin(step)
        main = type('M', (), {'__module__': 'joulewise.cli'})()
        with pt.program_span(main, ['reduce']):
            out.append(sum(range(1000)) + len(step))
        try:
            with pt.span('k.vdl.verify'):
                raise KeyError('body exception must pass through unchanged')
        except KeyError as exc:
            out.append(str(exc))
        with pt.pool_wait():
            out.append(json.dumps({'step': step}))
        pt.pool_batch('joulewise.reduce:_reduce', [{'wall_ns': 1, 'cpu_ns': 1}], 1, 2)
        pt.merge_child({'wall_ns': 1})
        pt.step_end(step)
        log.append(step)
    pt.run_end()
    return out


class FailClosedTimingTests(_Scratch):
    """A raising clock, sink or sampler leaves the run identical and silent."""

    def baseline(self):
        log = []
        return _workload(log), log

    def run_with(self, **options):
        stderr = io.StringIO()
        hook = mock.Mock()
        with contextlib.redirect_stderr(stderr), mock.patch.object(threading, 'excepthook', hook):
            fd = self.open_log()
            with pt.session(fd, mode='release', **options) as timer:
                pt.attach_restricted(self.restricted)
                log = []
                result = _workload(log)
                if timer is not None and timer.thread is not None:
                    deadline = time.monotonic() + 5
                    while timer.on and time.monotonic() < deadline:
                        time.sleep(0.01)
        self.assertEqual(stderr.getvalue(), '')
        hook.assert_not_called()
        return (result, log), timer

    def test_raising_clock(self):
        calls = {'n': 0}

        def clock():
            calls['n'] += 1
            if calls['n'] > 3:
                raise OSError('clock')
            return time.perf_counter_ns()
        result, timer = self.run_with(clock=clock, start_sampler=False)
        self.assertEqual(result, self.baseline())
        self.assertFalse(timer.on)

    def test_raising_sampler(self):
        def frames():
            raise RuntimeError('frames')
        result, timer = self.run_with(frames=frames, sample_ms=1)
        self.assertEqual(result, self.baseline())
        self.assertFalse(timer.on)

    def test_raising_sink(self):
        with mock.patch.object(pt.os, 'write', side_effect=OSError('disk')):
            result, timer = self.run_with(start_sampler=False)
        self.assertEqual(result, self.baseline())
        self.assertEqual(timer.sinks, {'structure': None, 'restricted': None})

    def test_invalid_line_turns_only_that_sink_off(self):
        with pt.session(self.open_log(), mode='release', start_sampler=False) as timer:
            pt.attach_restricted(self.restricted)
            timer.write('structure', {'event': 'step_end', 'step': '5', 'wall_s': 1.5})
            self.assertIsNone(timer.sinks['structure'])
            timer.write('restricted', {'event': 'run_end', 'total_ms': 3, 'cpu_ms': 1, 'phases': {}, 'top': []})
            self.assertIsNotNone(timer.sinks['restricted'])
            self.assertTrue(timer.on)
        self.assertEqual(_lines(self.structure), [{'event': 'run_start', 'mode': 'release', 'schema': pt.SCHEMA}])

    def test_restricted_dir_missing_is_silent(self):
        with pt.session(self.open_log(), mode='release', start_sampler=False) as timer:
            pt.attach_restricted(self.root / 'absent')
            self.assertIsNone(timer.sinks['restricted'])
            self.assertIsNone(timer.stack_fd)
            pt.step_begin('0'); pt.step_end('0')
        self.assertEqual(len(_lines(self.structure)), 4)

    def test_no_timer_hooks_are_noops(self):
        self.assertFalse(pt.enabled())
        self.assertEqual(self.baseline(), self.baseline())
        # Review of #631 (LOW): with no timer, pool_batch never touches costs.
        consumed = []

        def raising():
            consumed.append(1)
            raise RuntimeError('caller generator')
            yield {}
        for costs in (5, raising(), iter([{'wall_ns': 1}]), object()):
            with self.subTest(costs=type(costs).__name__):
                self.assertIsNone(pt.pool_batch('x', costs, 0, 1))
        self.assertEqual(consumed, [])

    def test_active_pool_batch_never_iterates_a_caller_iterator(self):
        consumed = []

        def raising():
            consumed.append(1)
            raise RuntimeError('caller generator')
            yield {}
        with pt.session(None, mode='release', start_sampler=False) as timer:
            pt.step_begin('5')
            for costs in (5, raising(), iter([{'wall_ns': 1}]), None):
                pt.pool_batch('joulewise.reduce:_reduce', costs, 7, 2)
            pt.pool_batch('joulewise.reduce:_reduce', ({'wall_ns': 3, 'cpu_ns': 1},), 7, 2)
            self.assertTrue(timer.on)
            self.assertEqual(timer.acc.pool['k.reduce'], [5, 1, 35, 3, 1, 3, 2])
            pt.step_end('5')
        self.assertEqual(consumed, [])
        with pt.task_cost(False) as cost:
            self.assertIsNone(cost)
        self.assertIsNone(pt.child_table())


class ValidatePhaseLineTests(unittest.TestCase):
    good = {'event': 'step_end', 'step': '9b', 'wall_s': 12}

    def test_good_lines(self):
        pt.validate_phase_line(pt.canonical_line(self.good))
        pt.validate_phase_line({'event': 'heartbeat', 'step': '-', 'step_s': 0, 'elapsed_s': 3})
        pt.validate_phase_line({'event': 'run_start', 'schema': pt.SCHEMA, 'mode': 'release'})

    def test_structure_rejections(self):
        bad = [
            dict(self.good, wall_s=1.5), dict(self.good, wall_s=True), dict(self.good, wall_s=-1),
            dict(self.good, wall_s='12'), dict(self.good, step='12'), dict(self.good, step='ok'),
            dict(self.good, label='k.strict'), dict(self.good, tasks=3), dict(self.good, status='ok'),
            {'event': 'step_end', 'step': '5'}, {'event': 'pool', 'step': '5', 'wall_s': 1},
            {'event': 'run_start', 'schema': pt.SCHEMA, 'mode': 'outcome_class'},
            {'event': 'run_start', 'schema': 'other', 'mode': 'release'},
            dict(self.good, wall_s=10 ** 16), dict(self.good, wall_s=None),
            {'event': 'heartbeat', 'step': '5', 'step_s': 1, 'elapsed_s': 1, 'fallbacks': 2},
        ]
        for document in bad:
            with self.subTest(document=document), self.assertRaises(pt.PhaseLineError):
                pt.validate_phase_line(document)
        raw = [b'{"event":"step_end","step":"5","wall_s":1.0}\n', b'{"event":"step_end","step":"5","wall_s":1e3}\n',
               b'{"event": "step_end", "step": "5", "wall_s": 1}\n', b'{"event":"step_end","step":"5","wall_s":1}',
               b'{"event":"step_end","step":"5","wall_s":1,"wall_s":2}\n', b'[1]\n', b'nan\n',
               b'{"event":"step_end","step":"5","wall_s":NaN}\n', '{"event":"step_end","step":"é","wall_s":1}\n'.encode(),
               b'{"event":"step_end","step":"5","wall_s":1}\n{"event":"run_end","total_s":1}\n']
        for line in raw:
            with self.subTest(line=line), self.assertRaises(pt.PhaseLineError):
                pt.validate_phase_line(line)

    restricted_end = {
        'event': 'step_end', 'step': '5', 'wall_ms': 9, 'cpu_ms': 3, 'serial_ms': 8,
        'spans_ms': {'pool.wait': 1}, 'maxrss_mib': 40, 'load_x100': {'start': 1, 'end': 2, 'max': 3},
        'programs': {'driver:prog.mint': {'count': 1, 'wall_ms': 2, 'cpu_ms': 1, 'max_ms': 2}},
        'pool': {'child:k.strict': {'batches': 1, 'tasks': 2, 'wall_ms': 3, 'busy_ms': 4, 'cpu_ms': 5,
                                    'max_task_ms': 6, 'pool_size': 2, 'busy_permille': 666}},
        'children': {'tasks': 1, 'wall_ms': 2, 'cpu_ms': 3},
        'phases': {'driver': {'k.strict': [1, 2], 'other': [3, 0]}, 'child': {}, 'member': {}},
        'sampled_ms': 9, 'unattributed_ms': 3, 'top': [['cli:_strict_problems', 3], ['qualname', 1]]}
    restricted_beat = {'event': 'heartbeat', 'step': '-', 'step_ms': 0, 'elapsed_ms': 5, 'label': 'other',
                       'program': None, 'top': [['k.reduce', 1]], 'progress_permille': None}

    def test_restricted_rejections(self):
        pt.validate_phase_line(self.restricted_end, 'restricted')
        pt.validate_phase_line(self.restricted_beat, 'restricted')
        pt.validate_phase_line(dict(self.restricted_beat, step='9b', program='prog.mint', progress_permille=500),
                               'restricted')
        end, beat = self.restricted_end, self.restricted_beat
        bad = [
            {'event': 'step_end', 'x': 1.5}, {'event': 'step_end', 'x': False},
            {'event': 'step_end', 'x': 'has space'}, {'event': 'step_end', 'x': 'a:2.5'},
            {'event': 'invented'}, {'event': 'step_end', 'bad key': 1}, {'event': 'step_end', 'x': -3},
            # Review of #631 (LOW): arbitrary keys and outcome words are refused.
            {'event': 'heartbeat', 'outcome': 'outcome_class', 'status': 'refused', 'decision': 'accepted'},
            {'event': 'step_end', 'arbitrary_key': ['tooling_refusal', 'calibration_wall_deadline_fired']},
            dict(end, outcome='x'), {k: v for k, v in end.items() if k != 'wall_ms'},
            dict(end, step='-'), dict(end, wall_ms=1.5), dict(end, wall_ms=True),
            dict(end, spans_ms={'tooling_refusal': 1}), dict(end, spans_ms={'pool.wait': -1}),
            dict(end, load_x100={'start': 1, 'end': 2}), dict(end, load_x100={'start': 1, 'end': 2, 'max': 3, 'x': 4}),
            dict(end, programs={'driver:refused': {'count': 1, 'wall_ms': 2, 'cpu_ms': 1, 'max_ms': 2}}),
            dict(end, programs={'outcome:prog.mint': {'count': 1, 'wall_ms': 2, 'cpu_ms': 1, 'max_ms': 2}}),
            dict(end, programs={'driver:prog.mint': {'count': 1, 'wall_ms': 2, 'cpu_ms': 1, 'status': 2}}),
            dict(end, pool={'decision': end['pool']['child:k.strict']}),
            dict(end, children={'tasks': 1, 'wall_ms': 2, 'cpu_ms': 3, 'refusals': 1}),
            dict(end, phases={'driver': {}, 'child': {}}),
            dict(end, phases={'driver': {'calibration_wall_deadline': [1, 1]}, 'child': {}, 'member': {}}),
            dict(end, phases={'driver': {'k.strict': [1]}, 'child': {}, 'member': {}}),
            dict(end, top=[['dry_run:_refuse_tooling', 3]]), dict(end, top=[['nocolon', 3]]),
            dict(end, top=[['x:outcome_class', 3]]), dict(end, top=[['cli:_strict_problems', 3, 4]]),
            dict(beat, label='tooling_refusal'), dict(beat, program='observer_unavailable'),
            dict(beat, top=[['cli:_strict_problems', 1]]), dict(beat, progress_permille='half'),
            dict(beat, step='12'),
            {'event': 'run_start', 'schema': pt.RESTRICTED_SCHEMA, 'mode': 'accepted', 'sample_ms': 1,
             'heartbeat_s': 1, 'pid': 1, 'cpu_count': 1},
            {'event': 'run_start', 'schema': pt.SCHEMA, 'mode': None, 'sample_ms': 1, 'heartbeat_s': 1,
             'pid': 1, 'cpu_count': 1},
            {'event': 'run_end', 'total_ms': 3},
            {'event': 'run_end', 'total_ms': 3, 'cpu_ms': 1, 'phases': {}, 'top': [], 'status': 'refused'},
        ]
        for document in bad:
            with self.subTest(document=document), self.assertRaises(pt.PhaseLineError):
                pt.validate_phase_line(document, 'restricted')
        pt.validate_phase_line({'event': 'run_end', 'total_ms': 3, 'cpu_ms': 1, 'phases': {}, 'top': []},
                               'restricted')

    def test_outcome_qualnames_collapse_when_sampled(self):
        def code(filename, qualname):
            return type('Code', (), {'co_filename': filename, 'co_qualname': qualname, 'co_name': qualname})()
        self.assertEqual(pt._qualname_key(code('/x/dry_run.py', 'RunState.prepare')), 'dry_run:RunState.prepare')
        for qualname in ('_refuse_tooling', 'outcome_class', 'wall_deadline_fired', 'Status.check'):
            self.assertEqual(pt._qualname_key(code('/x/dry_run.py', qualname)), 'qualname')

        with self.assertRaises(pt.PhaseLineError):
            pt.validate_phase_line(self.good, 'neither')


class StructureLogSchemaT3bTests(unittest.TestCase):
    """T3b: the structure log (outside custody) is checked by schema, not by a marker scan.

    A real (double-driven) block-5 driver run through scripts/run_b5_analysis.py
    --phase-log with the sampler running every 2 ms: every line passes the
    closed schema, no line carries anything but step ids and integer seconds,
    and the record, stdout and stderr equal a run without --phase-log.
    """

    @classmethod
    def setUpClass(cls):
        from tests.b5_analysis import test_dry_run as td
        cls.td = td
        cls.harness = td.DriverAcceptanceTests
        cls.harness.setUpClass()
        cls.addClassCleanup(cls.harness.doClassCleanups)

    def execute(self, argv_extra, env=None):
        td, h = self.td, self.harness
        h.serial += 1
        custody = h.root / ('timed-custody-' + str(h.serial))
        from joulewise.b5_analysis import dry_run as d
        from scripts import run_b5_analysis as script

        def real_run(mode, index, custody_path, **kw):
            return d.run(mode, h.index, custody_path, _test_pack_table=h.table, _test_repo_root=h.repo,
                         _runner=td.DriverDouble, _git=lambda repo: 'b' * 40, **kw)
        for key, value in {'calls': [], 'refusal': None, 'outcome': False, 'exception_at': None,
                           'change_at': None, 'fail_bundle': False, 'p42': False, 'target_refusal': False,
                           'target_reasons': ('marker_self_digest_mismatch',), 'bad_projection': False,
                           'release_change': None}.items():
            setattr(td.DriverDouble, key, value)
        out, err = io.StringIO(), io.StringIO()
        environment = {pt.SAMPLE_ENV: '2', pt.HEARTBEAT_ENV: '1'}
        environment.update(env or {})
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                mock.patch.object(script, 'run', side_effect=real_run), mock.patch.dict(os.environ, environment):
            code = script.main(['--mode', 'blind-dry-run', '--index', str(h.index), '--custody', str(custody)]
                               + argv_extra)
        record = (custody / 'dry-run/B5-BLIND-DRY-RUN-RECORD.json')
        return code, record.read_bytes() if record.exists() else None, out.getvalue(), err.getvalue(), custody

    def test_T3b_structure_log_schema_and_identical_run(self):
        log = self.harness.root / 'outside-phases.jsonl'
        timed = self.execute(['--phase-log', str(log)])
        plain = self.execute([])
        self.assertEqual(timed[0], 0, timed[3])
        self.assertEqual(timed[0], plain[0])
        self.assertEqual(timed[1].replace(str(timed[4]).encode(), b'<c>'), plain[1].replace(str(plain[4]).encode(), b'<c>'))
        self.assertEqual(timed[3], plain[3])
        self.assertEqual(timed[2].replace(str(timed[4]), '<c>'), plain[2].replace(str(plain[4]), '<c>'))
        data = log.read_bytes()
        rows = [pt.validate_phase_line(line) for line in data.splitlines(keepends=True)]
        self.assertEqual(rows[0], {'event': 'run_start', 'mode': 'blind-dry-run', 'schema': pt.SCHEMA})
        self.assertEqual(rows[-1]['event'], 'run_end')
        for row in rows:
            self.assertLessEqual(set(row), {'event', 'schema', 'mode', 'step', 'elapsed_s', 'step_s',
                                            'wall_s', 'total_s'})
        # Nothing new in custody outside restricted/logs/runtime-*.
        timed_files = sorted(p.relative_to(timed[4]).as_posix() for p in timed[4].rglob('*') if p.is_file())
        plain_files = sorted(p.relative_to(plain[4]).as_posix() for p in plain[4].rglob('*') if p.is_file())
        # D-188 SHIP: the restricted tier (runtime-phases, runtime-vdl-counters) is
        # written with or without --phase-log, so both sides drop runtime-* names.
        self.assertEqual([n for n in timed_files if '/logs/runtime-' not in n],
                         [n for n in plain_files if '/logs/runtime-' not in n])
        self.assertIn('dry-run/restricted/logs/runtime-phases.jsonl', timed_files)

    def test_env_fallback_and_invalid_paths_refuse_before_anything(self):
        log = self.harness.root / 'env-phases.jsonl'
        code, record, _out, _err, _custody = self.execute([], env={'JOULEWISE_B5_PHASE_LOG': str(log)})
        self.assertEqual(code, 0)
        self.assertTrue(log.is_file())
        os.symlink(self.harness.root, self.harness.root / 'link')
        for bad in ('relative.jsonl', str(log), str(self.harness.root / 'link' / 'x.jsonl'),
                    str(self.harness.root / 'missing-dir' / 'x.jsonl'), str(ROOT / 'inside-repo.jsonl'),
                    str(self.harness.root / 'a' / '..' / 'x.jsonl')):
            with self.subTest(bad=bad):
                code, record, out, err, custody = self.execute(['--phase-log', bad])
                self.assertEqual((code, record, out, err), (2, None, '', 'step 0 - tooling_refusal\n'))
                self.assertFalse(custody.exists())
        # Review of #631 (MEDIUM): a case-variant spelling of an existing custody
        # root is refused at step 0 too, and nothing is written into custody.
        swapped = Path(str(self.harness.root).swapcase())
        if os.path.exists(swapped) and os.path.samefile(swapped, self.harness.root):
            existing = self.harness.root / ('cased-custody-' + str(self.harness.serial))
            existing.mkdir()
            from scripts import run_b5_analysis as script
            err = io.StringIO()
            with contextlib.redirect_stderr(err), mock.patch.object(script, 'run') as run:
                self.assertEqual(script.main(['--mode', 'blind-dry-run', '--index', 'i', '--custody', str(existing),
                                              '--phase-log', str(swapped / existing.name.upper() / 'DRY-RUN')]), 2)
            run.assert_not_called()
            self.assertEqual(err.getvalue(), 'step 0 - tooling_refusal\n')
            self.assertEqual(os.listdir(existing), [])
        custody = self.harness.root / 'inside-custody'
        from scripts import run_b5_analysis as script
        err = io.StringIO()
        with contextlib.redirect_stderr(err), mock.patch.object(script, 'run') as run:
            self.assertEqual(script.main(['--mode', 'release', '--index', 'i', '--custody', str(custody),
                                          '--phase-log', str(custody / 'x.jsonl')]), 2)
        run.assert_not_called()
        self.assertEqual(err.getvalue(), 'step 0 - tooling_refusal\n')


class TimedDriverAcceptanceTests(unittest.TestCase):
    """T2, T3 and T19 of test_dry_run, unchanged, with a timer session and a 2 ms sampler active."""

    @classmethod
    def setUpClass(cls):
        from tests.b5_analysis import test_dry_run as td
        base = td.DriverAcceptanceTests
        cls.base = base
        base.setUpClass()
        cls.addClassCleanup(base.doClassCleanups)

    def _run(self, name):
        base = self.base
        case = base(name)
        case.setUp()
        original = case.execute
        logs = []

        def timed(**kw):
            log = base.root / ('t-phases-' + str(base.serial + 1) + '.jsonl')
            fd = pt.open_structure_log(log, custody=base.root / 'c', repo=ROOT)
            with pt.session(fd, mode='blind-dry-run', sample_ms=2, heartbeat_s=1) as timer:
                result = original(**kw)
                self.assertTrue(timer.on)
            logs.append(log)
            return result
        case.execute = timed
        getattr(case, name)()
        self.assertTrue(logs)
        for log in logs:
            for line in log.read_bytes().splitlines(keepends=True):
                pt.validate_phase_line(line)

    def test_T2_under_timer(self):
        self._run('test_T2_driver_streams_are_one_commitment_and_closed_step_lines')

    def test_T3_under_timer(self):
        self._run('test_T3_every_unrestricted_byte_has_no_marker_or_float_token')

    def test_T19_under_timer(self):
        self._run('test_T19_no_step0_or_step3_file_contains_a_float_token')

    def test_runtime_log_names_satisfy_T19_split(self):
        for name in (pt.RESTRICTED_LOG, pt.STACK_LOG.format(pid=12345)):
            self.assertNotIn(name.split('-')[1], ('0', '3'))
            self.assertTrue(name.startswith('runtime-'))


class DeadlineObserverIndependenceTests(unittest.TestCase):
    def test_timer_takes_no_monitoring_tool_id(self):
        monitoring = sys.monitoring
        free = [n for n in range(6) if monitoring.get_tool(n) is None]
        with pt.session(None, mode='release', sample_ms=1):
            time.sleep(0.02)
            self.assertEqual([n for n in range(6) if monitoring.get_tool(n) is None], free)
            from joulewise.b5_analysis.deadline_observer import observe_wall_deadline
            with observe_wall_deadline() as observer:
                self.assertIsNotNone(observer) if free else self.assertIsNone(observer)

    def test_deadline_accounting_unchanged_when_every_tool_id_is_taken(self):
        from joulewise.b5_analysis.deadline_observer import observe_wall_deadline
        monitoring = sys.monitoring
        taken = []
        try:
            for n in range(6):
                if monitoring.get_tool(n) is None:
                    monitoring.use_tool_id(n, 'phase-timing-test')
                    taken.append(n)
            with observe_wall_deadline() as without_timer:
                pass
            with pt.session(None, mode='release', sample_ms=1) as timer:
                time.sleep(0.02)
                with observe_wall_deadline() as with_timer:
                    pass
                self.assertTrue(timer.on)
            self.assertIsNone(without_timer)
            self.assertIsNone(with_timer)
        finally:
            for n in taken:
                monitoring.free_tool_id(n)


class LabelVocabularyTests(unittest.TestCase):
    def test_every_label_resolves_to_a_code_object(self):
        for module in {module for module, _q, _l, _p in pt.LABELS}:
            importlib.import_module(module)
        timer = pt._Timer(start_sampler=False)
        timer._resolve()
        self.assertEqual(sorted(timer.code_labels.values()), sorted(label for _m, _q, label, _p in pt.LABELS))

    def test_vocabulary_is_closed_and_safe(self):
        labels = [label for _m, _q, label, _p in pt.LABELS]
        self.assertEqual(len(labels), len(set(labels)))
        self.assertTrue(set(labels) | set(pt.SPAN_LABELS) <= pt.VOCABULARY)
        self.assertEqual({policy for _m, _q, _l, policy in pt.LABELS}, {'none', 'plan'})
        for label in pt.VOCABULARY:
            self.assertRegex(label, r'^[a-z][a-z0-9_.]*$')
            self.assertIsNone(pt._FLOAT_TOKEN.search(label))

    def test_step_ids_match_the_driver(self):
        from joulewise.b5_analysis import dry_run as d
        self.assertEqual(pt.STEP_IDS, tuple(d.STEP_IDS))
        self.assertEqual(pt.STEP_IDS, tuple(step for step, _f in d.STEPS))

    def test_program_labels(self):
        def fn(module, name='main', **attrs):
            f = type('P', (), {'__module__': module, '__name__': name, **attrs})()
            return f
        self.assertEqual(pt.program_label(fn('joulewise.cli'), ['validate-bundle', '--strict', 'b']), 'prog.cli.validate')
        self.assertEqual(pt.program_label(fn('joulewise.cli'), ['reduce', 'b']), 'prog.cli.reduce')
        self.assertEqual(pt.program_label(fn('joulewise.cli'), ['analyze-claims']), 'prog.cli.claims')
        self.assertEqual(pt.program_label(fn('joulewise.cli'), ['/secret/path']), 'prog.cli.other')
        self.assertEqual(pt.program_label(fn('joulewise.cli'), []), 'prog.cli.other')
        self.assertEqual(pt.program_label(fn('scripts.emit_floor_mint_pinset'), ['--x']), 'prog.pinset')
        self.assertEqual(pt.program_label(fn('scripts.unknown'), []), 'prog.other')
        self.assertEqual(pt.program_label(fn('x', _operation='prepare_brackets'), []), 'op.brackets')
        self.assertEqual(pt.program_label(fn('x', _operation='invented'), []), 'op.other')
        self.assertEqual(pt.program_label(fn('joulewise.b5_analysis.dry_run', 'fail'), []), 'op.fail')
        for module in pt.PROGRAM_LABELS:
            importlib.import_module(module)
        from joulewise.b5_analysis import dry_run as d
        state = d.RunState('blind-dry-run', Path('i'), Path('/nonexistent/restricted'), 'a' * 40)
        self.assertEqual(pt.program_label(state.guarded(state.prepare_kept), []), 'op.kept')


class ChildAndMemberTests(unittest.TestCase):
    def test_task_cost_in_a_worker_like_process(self):
        with pt.task_cost(True) as cost:
            sum(range(10000))
        self.assertEqual(set(cost), {'wall_ns', 'cpu_ns', 'phases'})
        self.assertGreater(cost['wall_ns'], 0)
        timer = pt.current()
        self.assertEqual(timer.group, 'member')
        timer.close()
        pt._TIMER = None

    def test_child_session_table_merges_into_the_driver(self):
        with pt.child_session(True) as child:
            self.assertIs(pt.current(), child)
            main = type('M', (), {'__module__': 'scripts.issue_reported_energy'})()
            with pt.program_span(main, []):
                time.sleep(0.005)
        table = pt.child_table()
        self.assertIsNone(pt.current())
        json.dumps(table)
        self.assertEqual(table['programs'][0][0], 'prog.issuer')
        with pt.session(None, mode='release', start_sampler=False) as driver:
            with pt.child_session(True) as nested:
                self.assertIsNone(nested)       # in-process: no-op
            self.assertIsNone(pt.child_table())
            pt.step_begin('10')
            pt.merge_child(table)
            self.assertEqual(driver.acc.children[0], 1)
            self.assertEqual(driver.acc.programs[0][:2], ['child', 'prog.issuer'])
            pt.step_end('10')

    def test_sigusr1_dump_goes_to_restricted_logs(self):
        import signal
        with tempfile.TemporaryDirectory(prefix='phase-stack-') as tmp:
            logs = Path(tmp) / 'logs'
            logs.mkdir()
            with pt.session(None, mode='release', start_sampler=False):
                pt.attach_restricted(tmp)
                os.kill(os.getpid(), signal.SIGUSR1)
                time.sleep(0.05)
            stack = logs / pt.STACK_LOG.format(pid=os.getpid())
            self.assertIn('test_sigusr1_dump_goes_to_restricted_logs', stack.read_text())
            self.assertEqual(sorted(p.name for p in logs.iterdir()), sorted([pt.RESTRICTED_LOG, stack.name]))


class OpenStructureLogTests(unittest.TestCase):
    def test_admissible_and_inadmissible_paths(self):
        with tempfile.TemporaryDirectory(prefix='phase-log-') as tmp:
            root = Path(tmp).resolve()
            custody = root / 'custody'
            fd = pt.open_structure_log(root / 'ok.jsonl', custody=custody, repo=ROOT)
            os.close(fd)
            os.symlink(root, root / 'alias')
            (custody / 'sub').mkdir(parents=True)
            for bad in ('ok.jsonl', root / 'ok.jsonl', root / 'alias' / 'n.jsonl', custody / 'n.jsonl',
                        custody, ROOT / 'n.jsonl', root / 'missing' / 'n.jsonl', root / 'x' / '..' / 'n.jsonl'):
                with self.subTest(bad=bad), self.assertRaises((ValueError, OSError)):
                    pt.open_structure_log(bad, custody=custody, repo=ROOT)
            self.assertFalse((custody / 'n.jsonl').exists())

    # Review of #631 (MEDIUM): "outside" is decided by identity, not spelling.
    def _case_insensitive(self, path):
        swapped = str(path).swapcase()
        return swapped != str(path) and os.path.exists(swapped) and os.path.samefile(swapped, path)

    def test_case_variant_and_firmlink_spellings_refused(self):
        with tempfile.TemporaryDirectory(prefix='phase-log-') as tmp:
            root = Path(tmp).resolve()
            custody = root / 'custody'
            (custody / 'sub').mkdir(parents=True)
            spellings = []
            if self._case_insensitive(custody):
                spellings += [root / 'CUSTODY' / 'b.jsonl', root / 'Custody' / 'sub' / 'b.jsonl',
                              root / 'CUSTODY' / 'DRY-RUN']
            if self._case_insensitive(ROOT):
                spellings += [Path(str(ROOT).swapcase()) / 'd.jsonl']
            data = Path('/System/Volumes/Data')
            if data.is_dir() and os.path.exists(str(data) + str(custody)) \
                    and os.path.samefile(str(data) + str(custody), custody):
                spellings += [Path(str(data) + str(custody)) / 'c.jsonl']
            if os.path.exists(str(data) + str(ROOT)) and os.path.samefile(str(data) + str(ROOT), ROOT):
                spellings += [Path(str(data) + str(ROOT)) / 'e.jsonl']
            if not spellings:
                self.skipTest('no case-insensitive volume and no firmlink alias here')
            for bad in spellings:
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    pt.open_structure_log(bad, custody=custody, repo=ROOT)
            self.assertEqual(sorted(os.listdir(custody)), ['sub'])
            self.assertEqual(sorted(os.listdir(custody / 'sub')), [])

    def test_log_may_not_take_a_missing_custody_name(self):
        with tempfile.TemporaryDirectory(prefix='phase-log-') as tmp:
            root = Path(tmp).resolve()
            bad = [(root / 'custody', root / 'custody' / 'x' / 'y'), (root / 'outer', root / 'outer' / 'custody')]
            if self._case_insensitive(root):
                bad += [(root / 'CUSTODY', root / 'custody'), (root / 'Outer', root / 'outer' / 'custody')]
            for log, custody in bad:
                with self.subTest(log=log, custody=custody), self.assertRaises(ValueError):
                    pt.open_structure_log(log, custody=custody, repo=ROOT)
            self.assertEqual(os.listdir(root), [])
            os.close(pt.open_structure_log(root / 'custody-phases.jsonl', custody=root / 'custody', repo=ROOT))


class PhaseReportTests(unittest.TestCase):
    def write(self, path, rows):
        Path(path).write_bytes(b''.join(pt.canonical_line(row) for row in rows))

    def test_table_compare_budget_eta(self):
        from scripts import b5_phase_report as report
        with tempfile.TemporaryDirectory(prefix='phase-report-') as tmp:
            old, new, running, budget = (Path(tmp) / n for n in ('old.jsonl', 'new.jsonl', 'run.jsonl', 'b.json'))
            start = {'event': 'run_start', 'schema': pt.SCHEMA, 'mode': 'blind-dry-run'}
            self.write(old, [start, {'event': 'step_begin', 'step': '0', 'elapsed_s': 0},
                             {'event': 'step_end', 'step': '0', 'wall_s': 100},
                             {'event': 'step_begin', 'step': '5', 'elapsed_s': 100},
                             {'event': 'step_end', 'step': '5', 'wall_s': 5000},
                             {'event': 'run_end', 'total_s': 5100}])
            self.write(new, [start, {'event': 'step_end', 'step': '0', 'wall_s': 90},
                             {'event': 'step_end', 'step': '5', 'wall_s': 2500}, {'event': 'run_end', 'total_s': 2590}])
            self.write(running, [start, {'event': 'step_end', 'step': '0', 'wall_s': 90},
                                 {'event': 'step_begin', 'step': '5', 'elapsed_s': 90},
                                 {'event': 'heartbeat', 'step': '5', 'step_s': 4000, 'elapsed_s': 4090}])
            budget.write_text(json.dumps({'default_s': 3600}))
            out = io.StringIO()
            self.assertEqual(report.main([str(old)], out=out), 0)
            self.assertIn('    5     5000   1:23:20   98.0%', out.getvalue())
            out = io.StringIO()
            self.assertEqual(report.main(['--compare', str(old), str(new)], out=out), 0)
            self.assertIn('    5     5000     2500    -2500    0.50', out.getvalue())
            out = io.StringIO()
            self.assertEqual(report.main([str(old), '--budget', str(budget)], out=out), 1)
            self.assertIn('OVER BUDGET step 5: 5000 s > 3600 s', out.getvalue())
            out = io.StringIO()
            self.assertEqual(report.main([str(running), '--eta', str(old), '--budget', str(budget)], out=out), 1)
            self.assertIn('ETA (estimate from prior log): 1000 s', out.getvalue())
            self.assertIn('step 5 running for 4000 s', out.getvalue())
            Path(old).write_bytes(Path(old).read_bytes() + b'{"event":"step_end","step":"5","wall_s":1.5}\n')
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(report.main([str(old)], out=io.StringIO()), 2)
            self.assertIn('invalid line', err.getvalue())


class NormalizedCompareCopyTests(unittest.TestCase):
    def test_runtime_logs_are_excluded_and_r1_evidence_is_untouched(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        try:
            import normalized_compare as nc
        finally:
            sys.path.remove(str(ROOT / 'tools'))
        with tempfile.TemporaryDirectory(prefix='phase-compare-') as tmp:
            roots = []
            for name, extra in (('a', b'1'), ('b', b'2')):
                run = Path(tmp) / name / 'dry-run'
                (run / 'restricted/logs').mkdir(parents=True)
                (run / nc.RECORD).write_text('{}')
                (run / 'restricted/logs/0001-1-alpha.stdout.log').write_text('same')
                (run / 'restricted/logs/runtime-phases.jsonl').write_bytes(extra)
                (run / 'restricted/logs/runtime-stack-1.txt').write_bytes(extra)
                roots.append(Path(tmp) / name)
            for flags in ([], ['--logs']):
                with self.subTest(flags=flags), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(nc.main([str(roots[0]), str(roots[1])] + flags), 0)
            self.assertNotIn('restricted/logs/runtime-phases.jsonl', nc.load(roots[0], True))
            (roots[1] / 'dry-run/restricted/logs/0001-1-alpha.stdout.log').write_text('other')
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(nc.main([str(roots[0]), str(roots[1]), '--logs']), 1)
        original = (ROOT / 'docs/process_traces/2026-11-01-l9-speedup-r1/normalized_compare.py').read_text()
        self.assertNotIn('runtime-', original)


if __name__ == '__main__':
    unittest.main()
