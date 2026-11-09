#!/usr/bin/env python3
"""Dynamic execution closure of the synthetic W1/D/R1 paths (delta2 receipt completeness).

The static walk of ``tests/align/test_v4_executed_closure.py`` keeps missing entry
points (configured argv, ``-m`` launches). This traces what the synthetic paths
actually execute, under ``sys.addaudithook``:

* every ``open`` of a ``.py``/``.zsh``/``.sh`` file (and ``.pyc``, mapped back to its
  source) inside the repository, and every ``compile``/``exec`` code object whose
  filename is a repository script;
* (informational) every ``open`` of a script is listed separately as ``opened``;
* every ``subprocess.Popen`` / ``os.exec*`` / ``os.posix_spawn`` / ``os.system`` target
  and any repository script named in its argv;
* every repository module in ``sys.modules`` at the end of each scenario;
* child Python processes started by a scenario record the same events (a
  ``sitecustomize`` on ``PYTHONPATH`` writes one file per child).

Test files (``tests/``), ``.git`` and this tracer are excluded. The executed set is modules,
compiled/exec'd code and launch targets; plain opens are recorded as evidence only. Nothing is launched
natively: the scenarios are the repository's own synthetic tests.

  python3.13 -B scripts/align_v4_dynamic_trace.py --out docs/align/v4/dynamic_closure_trace.json
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = ('.py', '.zsh', '.sh')
SCHEMA = 'joulewise.align_v4.dynamic_closure_trace.v1'
EXCLUDED_PREFIXES = ('tests/', '.git/', 'docs/')
# The harvest-off pack tooling runs after a window on the verified copy, never on the arm or window path (its
# lane kept it out of EXECUTED_CLOSURE on purpose); tests/align/test_v4_next_arm_packet.py imports both only to
# assert that shared constants are equal, which would otherwise list them as executed-but-unbound.
EXCLUDED_FILES = ('scripts/align_v4_dynamic_trace.py', 'joulewise/align/apple/harvest_offload.py',
                  'scripts/align_v4_harvest_off.py')

# (scenario id, environment, unittest ids). Each is a synthetic path of the W1/D/R1 chain.
SCENARIOS = (
    # first: the production-session replays read process-global tiny-model state that earlier scenarios' temp dirs leave stale
    ('dct_series_window', {}, ['tests.align.test_v4_series', 'tests.align.test_v4_series_e2e',
                               'tests.align.test_v4_series_r20', 'tests.align.test_v4_replacement_windows']),
    ('wp22_synthetic_w1_chain', {'JW_WP22_FULL': '1'}, ['tests.align.test_v4_w1_synthetic']),
    ('r1_synthetic_arm', {}, ['tests.align.test_r1_rehearsal', 'tests.align.test_r1_runtime_e2e']),
    ('r1_to_w1_chain', {}, ['tests.align.test_r1_turn_counts_export', 'tests.align.test_r1_to_w1_chain',
                            'tests.align.test_w1_kit_r10']),
    ('desk_dc_session', {}, ['tests.align.test_km003c.MemberTests', 'tests.align.test_km003c.DeskTests',
                             'tests.align.test_v4_topup', 'tests.align.test_v4_record_binding']),
    ('arm_install_session', {}, ['tests.align.test_v4_kit', 'tests.align.test_v4_next_arm_packet']),
    ('night_driver_hazard_pack', {}, ['tests.align.test_km003c.NightChainTests']),
    # LOW-5 (Opus cold review of the timing-receipts fix): the single-module minimal W1 execution that binds
    # joulewise/timing_receipts.py in the trace; the earlier regeneration dropped it.
    ('timing_receipts_delta', {}, ['tests.align.test_timing_receipts_opus_witnesses']),
)


def _relative(path, root, cwd=None):
    try:
        text = os.fspath(path)
    except TypeError:
        return None
    if not isinstance(text, str) or not text:
        return None
    candidate = Path(text)
    if not candidate.is_absolute():
        candidate = Path(cwd or os.getcwd()) / candidate
    candidate = Path(os.path.normpath(candidate))
    if candidate.suffix == '.pyc' and candidate.parent.name == '__pycache__':
        candidate = candidate.parent.parent / (candidate.name.split('.')[0] + '.py')
    if candidate.suffix not in SUFFIXES or not candidate.is_file():
        return None
    try:
        relative = candidate.relative_to(root).as_posix()
    except ValueError:
        try:
            relative = candidate.resolve().relative_to(root).as_posix()
        except (ValueError, OSError):
            return None
    if relative.startswith(EXCLUDED_PREFIXES) or relative in EXCLUDED_FILES:
        return None
    return relative


class Recorder:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.enabled = False
        self.opened, self.compiled, self.exec_targets, self.argv_scripts, self.modules = (set() for _ in range(5))

    def hook(self, event, args):
        if not self.enabled:
            return
        try:
            if event == 'open':
                self._add(self.opened, args[0])
            elif event == 'compile':
                self._add(self.compiled, args[1])
            elif event == 'exec' and args:
                self._add(self.compiled, getattr(args[0], 'co_filename', None))
            elif event == 'subprocess.Popen':
                executable, argv, cwd = args[0], args[1], args[2]
                self._add(self.exec_targets, executable, cwd)
                for token in argv or ():
                    self._add(self.argv_scripts, token, cwd)
            elif event in ('os.exec', 'os.posix_spawn', 'os.spawn'):
                self._add(self.exec_targets, args[-3] if event == 'os.spawn' else args[0])
                for token in (args[1] if len(args) > 1 and isinstance(args[1], (list, tuple)) else ()):
                    self._add(self.argv_scripts, token)
            elif event == 'os.system':
                for token in str(args[0]).split():
                    self._add(self.argv_scripts, token)
        except Exception:      # a tracer never breaks the run
            pass

    def _add(self, bucket, value, cwd=None):
        if isinstance(value, (bytes, os.PathLike)):
            value = os.fsdecode(value)
        relative = _relative(value, self.root, cwd) if isinstance(value, str) else None
        if relative:
            bucket.add(relative)

    def sweep_modules(self):
        for module in list(sys.modules.values()):
            self._add(self.modules, getattr(module, '__file__', None))

    def paths(self):
        """Executed: imported modules, compiled/exec'd code, launched targets and argv scripts.

        ``opened`` (every .py/.zsh/.sh opened for reading, including bulk readers such as hash
        inventories) is evidence only; an opened-for-read file is not executed.
        """
        return sorted(self.compiled | self.exec_targets | self.argv_scripts | self.modules)

    def to_json(self):
        return {name: sorted(getattr(self, name)) for name in
                ('opened', 'compiled', 'exec_targets', 'argv_scripts', 'modules')}


_RECORDER = None


def install(root=ROOT):
    """Install (once per process) and return the recorder; its hook cannot be removed."""
    global _RECORDER
    if _RECORDER is None:
        _RECORDER = Recorder(root)
        sys.addaudithook(_RECORDER.hook)
    return _RECORDER


def install_child(trace_dir, root=ROOT):
    """Called from a child's sitecustomize: record to one file per process at exit."""
    import atexit
    recorder = install(root)
    recorder.enabled = True

    def write():
        recorder.sweep_modules()
        Path(trace_dir, f'child-{os.getpid()}.json').write_text(json.dumps(recorder.to_json()))
    atexit.register(write)


def child_environment(trace_dir):
    """A directory with a sitecustomize that traces child Python processes; returns its path."""
    directory = Path(trace_dir) / 'sitecustomize_dir'
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'sitecustomize.py').write_text(
        'import sys\n'
        f'sys.path.insert(0, {str(ROOT)!r})\n'
        'try:\n'
        '    from scripts.align_v4_dynamic_trace import install_child\n'
        f'    install_child({str(trace_dir)!r})\n'
        'except Exception:\n'
        '    pass\n')
    return directory


def run_scenarios(scenarios=SCENARIOS, trace_dir=None):
    import tempfile
    import unittest
    trace_dir = Path(trace_dir or tempfile.mkdtemp(prefix='v4-trace-'))
    recorder = install()
    previous = os.environ.get('PYTHONPATH')
    os.environ['PYTHONPATH'] = os.pathsep.join(filter(None, [str(child_environment(trace_dir)), previous]))
    report = {}
    try:
        for scenario, env, ids in scenarios:
            saved = {k: os.environ.get(k) for k in env}
            os.environ.update(env)
            before = set(recorder.paths())
            recorder.enabled = True
            try:
                suite = unittest.defaultTestLoader.loadTestsFromNames(ids)
                result = unittest.TextTestRunner(stream=open(os.devnull, 'w'), verbosity=0).run(suite)
            finally:
                recorder.enabled = False
                recorder.sweep_modules()
                for key, value in saved.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value
            report[scenario] = {'tests_run': result.testsRun, 'ok': result.wasSuccessful(),
                                'new_paths': len(set(recorder.paths()) - before)}
    finally:
        if previous is None:
            os.environ.pop('PYTHONPATH', None)
        else:
            os.environ['PYTHONPATH'] = previous
    children = set()
    for path in trace_dir.glob('child-*.json'):
        data = json.loads(path.read_text())
        children |= {p for bucket in data.values() for p in bucket}
    return report, recorder, sorted(children)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    sys.path.insert(0, str(ROOT))
    report, recorder, children = run_scenarios()
    from joulewise.align.apple import v4_registration as registration
    executed = sorted(set(recorder.paths()) | set(children))
    trace = {'schema': SCHEMA, 'scenarios': report, 'executed': executed,
             'by_event': recorder.to_json(), 'child_process_paths': children,
             'not_bound': [p for p in executed if p not in registration.ARTIFACTS],
             'not_strict': [p for p in executed if p in registration.ARTIFACTS and not registration.is_strict(p)]}
    with args.out.open('x') as handle:
        handle.write(json.dumps(trace, indent=1, sort_keys=True) + '\n')
    print(json.dumps({'executed': len(executed), 'not_bound': trace['not_bound'],
                      'not_strict': trace['not_strict'], 'scenarios': report}, indent=1))
    return 0 if all(s['ok'] for s in report.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
