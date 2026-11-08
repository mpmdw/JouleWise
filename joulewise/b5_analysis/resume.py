"""Step-boundary checkpoints, resume, step-level tooling retries and the one-pass
defect sweep of the block-5 analysis driver (lane/2026-11-06-b5-robust).

Nothing here decides a step, a status, a refusal or a record byte. It exists so
that an interruption, a transient tooling refusal or a data defect costs one
step (or one extra sweep), not a whole ~150 min run.

Checkpoint (``restricted/resume/checkpoint.json``, restricted tier, explicit
JSON; no pickled run state). Written atomically after every completed step and
once before step 0. It holds the run binding (mode, analysis commit, checkout
refusal, window-index digest, store mode, synthetic), the number of completed
steps, the step records and their raw codes, the registered outputs in
registration order, the runner's log counter, the bundle run ids behind the
step-1/2 logs, the record's attempts/windows/census parts, and the sha256 of
every regular file under ``restricted/`` (live timer logs and ``resume/``
excepted).

Rebuild. Four steps also build in-memory run state with in-process builders:
step 0 ``prepare_initial``, step 1 ``prepare_kept``, step 3
``prepare_tripwires`` and step 3b ``prepare_brackets``. Resume re-runs exactly
those builders whose step ran, through the same runner seam, in a scratch
directory, and requires every output they register to have the checkpointed
name and sha256 (verification by re-hashing). The checkpointed records, raw
codes, outputs, counter and members are then restored, and the rebuilt
attempts, windows and flags must equal the checkpoint (its census must contain
the rebuilt census). Every other step contributes only files and the restored
fields.

Rollback. Before a step is (re)run from a checkpoint, every checkpointed file is
re-hashed and every file the interrupted or refused attempt left behind is
moved to ``restricted/resume/abandoned/<n>/`` (restricted evidence, never
deleted), so the attempt's partial outputs cannot collide with the rerun.

Retry (at most MAX_RETRIES per step, serial, budgets unchanged). Only the
step-level tooling refusals that have a producer in this driver are retried:
``calibration_wall_deadline_fired`` (the run's observer saw a firing),
``calibration_deadline_observer_unavailable`` while the run's own observer
exists (a worker could not observe), and an escaped ``BrokenProcessPool``
(a child-pool worker died). See docs/run_reports/2026-11-06-b5-robust.md.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys

SCHEMA = 'joulewise.b5_analysis_checkpoint.v1'
RETRY_SCHEMA = 'joulewise.b5_recovery_event.v1'
DEFECTS_SCHEMA = 'joulewise.b5_defect_sweep.v1'
RESUME_DIR = 'resume'
CHECKPOINT = 'checkpoint.json'
ABANDONED = 'abandoned'
RETRIES = 'recovery.jsonl'
MAX_RETRIES = 2
# step id -> the RunState builder its registered function runs in-process.
BUILDERS = {'0': 'prepare_initial', '1': 'prepare_kept', '3': 'prepare_tripwires', '3b': 'prepare_brackets'}
RETRY_EXCEPTION_CLASSES = frozenset({'BrokenProcessPool'})
_KEYS = frozenset({'schema_version', 'binding', 'position', 'stopped', 'ran', 'counter', 'outputs',
                   'step_records', 'raw_codes', 'members', 'parts', 'files', 'dirs'})


class ResumeError(Exception):
    """A checkpoint that cannot be resumed; ``reason`` is a fixed structure token."""

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def _canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)
            + '\n').encode('ascii')


def _sha(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def is_live(name):
    """Restricted timer/counter logs that a live process appends to (never checkpointed)."""
    return (name in ('logs/runtime-phases.jsonl', 'logs/runtime-vdl-counters.json')
            or (name.startswith('logs/runtime-stack-') and name.endswith('.txt')))


def _walk(restricted):
    """(regular files {relative: lstat}, directories) under restricted, outside resume/; no link followed."""
    restricted = Path(restricted)
    files, dirs = {}, []

    def fail(error):
        raise error
    for directory, children, names in os.walk(restricted, followlinks=False, onerror=fail):
        base = Path(directory)
        if base == restricted:
            children[:] = [c for c in children if c != RESUME_DIR]
            names = [n for n in names if n != RESUME_DIR]
        for name in children + names:
            path = base / name
            info = path.lstat()
            relative = path.relative_to(restricted).as_posix()
            if stat.S_ISDIR(info.st_mode):
                dirs.append(relative)
            elif stat.S_ISREG(info.st_mode):
                files[relative] = info
            else:
                raise ResumeError('custody_entry_not_regular')
    return files, sorted(dirs)


def _atomic(path, raw):
    # Atomic against a killed process (the case this exists for). No fsync: after
    # a power loss a torn checkpoint fails load() and the run starts over.
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name('.' + path.name + '.tmp')
    with open(temporary, 'wb') as out:
        out.write(raw)
    os.replace(temporary, path)


def _record(row):
    from .steps import StepRecord
    return StepRecord(**{**row, 'outputs': tuple(row['outputs']), 'flags': tuple(row['flags'])})


def state_parts(s):
    """The record's attempts/windows/census parts and the run flags (None when not computable)."""
    from .dry_run import _plain, _record_parts
    try:
        attempts, windows, census = _record_parts(s)
        return json.loads(_canonical({'attempts': _plain(attempts), 'windows': _plain(windows),
                                      'census': _plain(census), 'flags': _plain(list(s.flags))}))
    except Exception:  # noqa: BLE001 - a partial state (a refused builder) may not be summarisable
        return None


def merged_census(census, checkpoint):
    """A resumed run's census: the live one plus the checkpointed rows (same keys, same order rule)."""
    if checkpoint is None or checkpoint.get('parts') is None:
        return census
    rows = {(row['window'], row['path']): row for row in checkpoint['parts']['census']}
    for row in census:
        rows[(row['window'], row['path'])] = row
    return [rows[key] for key in sorted(rows)]


class Checkpoints:
    """The run's checkpoint writer. A failed write only skips that checkpoint."""

    def __init__(self, restricted, binding):
        self.restricted = Path(restricted)
        self.root = self.restricted / RESUME_DIR
        self.binding = binding
        self.last = None
        self._cache = {}

    def inventory(self):
        files, dirs = _walk(self.restricted)
        digests, cache = {}, {}
        for name, info in sorted(files.items()):
            if is_live(name):
                continue
            identity = (info.st_size, info.st_mtime_ns, info.st_ino)
            old = self._cache.get(name)
            digest = old[1] if old is not None and old[0] == identity else _sha(self.restricted / name)
            digests[name] = digest
            cache[name] = (identity, digest)
        self._cache = cache
        return digests, dirs

    def write(self, s, runner, *, position, stopped, ran):
        try:
            files, dirs = self.inventory()
            document = {
                'schema_version': SCHEMA, 'binding': self.binding, 'position': position, 'stopped': bool(stopped),
                'ran': list(ran), 'counter': runner._counter,
                'outputs': [[role, item['name'], item['sha256']] for role, item in s.outputs.items()],
                'step_records': [record.as_dict() for record in s.step_records],
                'raw_codes': [[record.as_dict(), code, exception] for record, code, exception in s._raw_codes],
                'members': sorted([name, member] for name, member in s._members.items()),
                'parts': state_parts(s), 'files': files, 'dirs': dirs}
            raw = _canonical(document)
            _atomic(self.root / CHECKPOINT, raw)
            self.last = json.loads(raw)
        except Exception as exc:  # noqa: BLE001 - recovery is optional; the run never fails here
            self.last = None
            note(self.restricted, {'event': 'checkpoint_skipped', 'position': position,
                                   'exception_class': type(exc).__qualname__})

    def finish(self):
        """After the record write: drop the checkpoint; keep retry and abandoned evidence."""
        try:
            (self.root / CHECKPOINT).unlink(missing_ok=True)
            self.root.rmdir()
        except OSError:
            pass


def note(restricted, row):
    """Append one restricted recovery diagnostic (never raises)."""
    try:
        path = Path(restricted) / RESUME_DIR / RETRIES
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'ab') as out:
            out.write(_canonical({'schema_version': RETRY_SCHEMA, **row}))
    except Exception:  # noqa: BLE001
        pass


def _strings(value, length=None):
    return (type(value) is list and (length is None or len(value) == length)
            and all(type(item) is str for item in value))


def _well_formed(document):
    """The nested shapes restore(), verify_state() and rollback() read: a malformed one is a closed refusal."""
    from .dry_run import STEPS
    parts = document['parts']
    if type(document['step_records']) is not list or type(document['raw_codes']) is not list:
        return False
    try:
        for row in document['step_records']:
            _record(row)
        for row, code, exception in document['raw_codes']:
            _record(row)
            if (code is not None and type(code) is not str) or (exception is not None and type(exception) is not str):
                return False
    except (TypeError, ValueError, KeyError, AttributeError):
        return False
    return (type(document['binding']) is dict and type(document['stopped']) is bool
            and 0 <= document['position'] <= len(STEPS) and document['counter'] >= 0
            and _strings(document['ran']) and _strings(document['dirs'])
            and all(type(value) is str for value in document['files'].values())
            and type(document['outputs']) is list and all(_strings(item, 3) for item in document['outputs'])
            and type(document['members']) is list and all(_strings(item, 2) for item in document['members'])
            and (parts is None or (type(parts) is dict and set(parts) == {'attempts', 'windows', 'census', 'flags'}
                                   and all(type(parts[key]) is list for key in parts)
                                   and all(type(row) is dict and type(row.get('window')) is str
                                           and type(row.get('path')) is str for row in parts['census']))))


def load(restricted, binding):
    """The checkpoint of an interrupted run, checked against this invocation's binding."""
    path = Path(restricted) / RESUME_DIR / CHECKPOINT
    try:
        document = json.loads(path.read_bytes())
    except FileNotFoundError:
        raise ResumeError('checkpoint_missing') from None
    except (OSError, ValueError):
        raise ResumeError('checkpoint_unreadable') from None
    if (type(document) is not dict or set(document) != _KEYS or document['schema_version'] != SCHEMA
            or type(document['position']) is not int or type(document['counter']) is not int
            or type(document['files']) is not dict or type(document['dirs']) is not list
            or not _well_formed(document)):
        raise ResumeError('checkpoint_invalid')
    for key in sorted(binding):
        if document['binding'].get(key) != binding[key]:
            raise ResumeError(key + '_differs')
    if set(document['binding']) != set(binding):
        raise ResumeError('checkpoint_invalid')
    return document


def rollback(restricted, checkpoint, *, move_live, verify_only=False):
    """Re-hash every checkpointed file, then move everything newer aside.

    ``move_live`` (a resume in a new process) also moves the previous process's
    timer logs; a retry in this process keeps its open logs in place.
    """
    restricted = Path(restricted)
    files, dirs = _walk(restricted)
    for name, digest in checkpoint['files'].items():
        if name not in files or _sha(restricted / name) != digest:
            raise ResumeError('checkpointed_file_differs')
    if verify_only:
        return 0
    extras = sorted(name for name in files
                    if name not in checkpoint['files'] and (move_live or not is_live(name)))
    moved = 0
    if extras:
        root = restricted / RESUME_DIR / ABANDONED
        number = 1
        while (root / str(number)).exists():
            number += 1
        for name in extras:
            destination = root / str(number) / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(restricted / name, destination)
            moved += 1
    for name in sorted(set(dirs) - set(checkpoint['dirs']), key=lambda n: len(Path(n).parts), reverse=True):
        try:
            (restricted / name).rmdir()
        except OSError:
            pass
    return moved


def restore(s, runner, checkpoint):
    """The checkpoint's explicit fields onto ``s`` and ``runner``."""
    s.outputs = {role: {'name': name, 'sha256': digest} for role, name, digest in checkpoint['outputs']}
    s.step_records = [_record(row) for row in checkpoint['step_records']]
    s._raw_codes = [(_record(row), code, exception) for row, code, exception in checkpoint['raw_codes']]
    s._members = {name: member for name, member in checkpoint['members']}
    runner._counter = checkpoint['counter']
    runner.last_exception_class = None


def verify_state(s, checkpoint):
    """Rebuilt in-memory state must summarise to the checkpointed record parts."""
    expected, live = checkpoint['parts'], state_parts(s)
    if expected is None or live is None:
        if expected is not live:
            raise ResumeError('rebuilt_state_differs')
        return
    if any(live[key] != expected[key] for key in ('attempts', 'windows', 'flags')):
        raise ResumeError('rebuilt_state_differs')
    rows = {json.dumps(row, sort_keys=True) for row in expected['census']}
    if any(json.dumps(row, sort_keys=True) not in rows for row in live['census']):
        raise ResumeError('rebuilt_state_differs')


def rebuild(s, runner, runner_factory, checkpoint, *, deadline, caches):
    """Re-run the checkpoint's in-process builders in scratch custody and verify them."""
    expected = {role: (name, digest) for role, name, digest in checkpoint['outputs']}
    scratch = s.restricted / RESUME_DIR / 'rebuild'
    restricted = s.restricted
    shutil.rmtree(scratch, ignore_errors=True)
    scratch.mkdir(parents=True)
    firings = deadline.firings if deadline is not None else None
    try:
        s.restricted = scratch
        builder_runner = runner_factory(scratch)
        for step in checkpoint['ran']:
            operation = BUILDERS.get(step)
            if operation is None:
                continue
            before = set(s.outputs)
            result = builder_runner.run(s.guarded(getattr(s, operation)), [], step=step)
            if deadline is None or deadline.firings != firings or caches.worker_observer_unavailable:
                raise ResumeError('rebuild_deadline_fired')
            rows = [row for row in checkpoint['step_records'] if row['step'] == step]
            if any(row['status'] == 'ok' for row in rows) and (result.exit_status or result.exception):
                raise ResumeError('rebuilt_builder_refused')
            produced = [item for role, item in s.outputs.items() if role not in before]
            if sorted((item['name'], item['sha256']) for item in produced) != sorted(
                    (item['name'], item['sha256']) for row in rows for item in row['outputs']):
                raise ResumeError('rebuilt_output_differs')
            for role, item in s.outputs.items():
                if role not in before and expected.get(role) != (item['name'], item['sha256']):
                    raise ResumeError('rebuilt_output_differs')
    finally:
        s.restricted = restricted
        shutil.rmtree(scratch, ignore_errors=True)
    if deadline is None or deadline.firings != firings or caches.worker_observer_unavailable:
        raise ResumeError('rebuild_deadline_fired')
    restore(s, runner, checkpoint)
    verify_state(s, checkpoint)


def retry_reason(s, records, deadline):
    """The registered tooling refusal of this attempt that a serial rerun may clear, or None."""
    from .deadline_observer import CALIBRATION_WALL_DEADLINE, OBSERVER_UNAVAILABLE
    from .dry_run import _raw_code, is_nonstopping_outcome
    failed = next((r for r in records if r.status != 'ok' and not is_nonstopping_outcome(r)), None)
    if failed is None or failed.status not in ('tooling_refusal', 'unclassified_refusal'):
        return None
    code, exception = _raw_code(s, failed.as_dict())
    if code == CALIBRATION_WALL_DEADLINE:
        return code
    if code == OBSERVER_UNAVAILABLE and deadline is not None:
        return code
    if code is None and exception in RETRY_EXCEPTION_CLASSES:
        return exception
    return None


def serial(s, caches):
    """Run the next attempt serially: no child, pack or member pool."""
    s.workers = caches.workers = 1
    caches.worker_observer_unavailable = False
    pool, caches.pool = caches.pool, None
    if pool is not None:
        try:
            pool.shutdown(wait=True, cancel_futures=True)
        except Exception:  # noqa: BLE001
            pass


# -- one-pass defect sweep ---------------------------------------------------

SWEPT_STEPS = ('1', '2')


def _stopping(record):
    from .dry_run import is_nonstopping_outcome
    return next((row for row in record['steps'] if row['status'] not in ('ok', 'not_run')
                 and not is_nonstopping_outcome(row)), None)


def defect_sweep(s, runner_factory, record, *, deadline, caches, workers):
    """After a step-1/2 data refusal: run every independent kept bundle through steps 1 and 2.

    Runs after the record is written and changes nothing in it. A unit is a
    kept bundle; step 2 of a bundle depends only on its own step 1. Output is
    restricted (``restricted/defects/DEFECTS.json`` plus the sweep's own
    logs); stderr carries counts per step and window only. Never excludes.
    """
    from .dry_run import (AnalysisRefusal, REREDUCTION_REFIT_DIFFERS, RunnerResult, StepRunner,
                          require_rereduction_matches_stored)
    stop = _stopping(record)
    if stop is None or stop['step'] not in SWEPT_STEPS or stop['status'] == 'outcome_class':
        return None
    if retry_reason(s, [_record(stop)], deadline) is not None:
        return None
    units = list(s.kept_bundles())
    root = s.restricted / 'defects'
    number = 1
    while root.exists():
        number += 1
        root = s.restricted / ('defects-' + str(number))
    root.mkdir()
    pooled = workers > 1 and len(units) > 1 and runner_factory is StepRunner
    defects, tooling = [], []
    passed = []

    def program(step, argv, pack):
        """[(exit_status, exception_class, stderr name, firings)] for each task."""
        if pooled:
            from .parallel import dispatch
            results, _ = dispatch([('joulewise.cli:main', a, step, p) for a, p in zip(argv, pack)],
                                  restricted=root, first_counter=program.counter + 1, workers=workers,
                                  physics_store=s.physics_store, vdl=None)
            program.counter += len(results)
            return [(RunnerResult(r.exit_status, Path(r.stdout_path), Path(r.stderr_path), r.exception,
                                  r.exception_class), r.firings) for r in results]
        from joulewise.cli import main
        out = []
        for a, p in zip(argv, pack):
            before = deadline.firings if deadline is not None else None
            unavailable = caches.worker_observer_unavailable
            result = runner.run(main, a, step=step, window=p)
            firings = (None if deadline is None or caches.worker_observer_unavailable != unavailable
                       else deadline.firings - before)
            out.append((result, firings))
        return out
    program.counter = 0
    runner = None if pooled else runner_factory(root)
    if runner is not None:
        runner.state = s  # the driver's runner seam (synthetic doubles read it; StepRunner ignores it)

    def row(step, pack, run_id, result, code, firings):
        item = {'step': step, 'window': pack, 'member': run_id, 'raw_code': code,
                'program_code': None if result.exception else result.token(),
                'exit_status': result.exit_status, 'exception_class': result.exception_class,
                'log': Path(result.stderr_path).name}
        (tooling if firings != 0 else defects).append(item)

    validated = program('1', [['validate-bundle', '--strict', str(bundle)] for _, _, bundle in units],
                        [pack for pack, _, _ in units])
    for (pack, run_id, bundle), (result, firings) in zip(units, validated):
        if result.exit_status or result.exception or firings != 0:
            row('1', pack, run_id, result, 'kept_bundle_strict_validation_failed', firings)
        else:
            passed.append((pack, run_id, bundle))
    outputs = []
    for pack, run_id, _ in passed:
        output = root / 'rereduced' / pack / (run_id + '.rereduced.json')
        output.parent.mkdir(parents=True, exist_ok=True)
        outputs.append(output)
    reduced = program('2', [['reduce', str(bundle), '--output', str(output)]
                            for (_, _, bundle), output in zip(passed, outputs)], [pack for pack, _, _ in passed])
    for (pack, run_id, bundle), output, (result, firings) in zip(passed, outputs, reduced):
        code = result.token() if result.exit_status or result.exception else None
        failed = bool(result.exit_status or result.exception)
        if not failed:
            try:
                require_rereduction_matches_stored(bundle, output)
            except AnalysisRefusal:
                failed, code = True, REREDUCTION_REFIT_DIFFERS
            except Exception:  # noqa: BLE001
                failed = True
        if failed or firings != 0:
            row('2', pack, run_id, result, None if result.exception else code, firings)
    document = {'schema_version': DEFECTS_SCHEMA, 'stopped_step': stop['step'], 'stopped_window': stop['window'],
                'units': len(units), 'defects': defects, 'tooling_inconclusive': tooling}
    (root / 'DEFECTS.json').write_bytes(_canonical(document))
    counts = {}
    for item in defects:
        counts[(item['step'], item['window'])] = counts.get((item['step'], item['window']), 0) + 1
    for (step, window), count in sorted(counts.items()):
        print('defects step ' + step + ' ' + (window or '-') + ' ' + str(count), file=sys.stderr)
    print('defect sweep: ' + str(len(units)) + ' units, ' + str(len(defects)) + ' defects, '
          + str(len(tooling)) + ' inconclusive (restricted/' + root.name + '/DEFECTS.json)', file=sys.stderr)
    return document
