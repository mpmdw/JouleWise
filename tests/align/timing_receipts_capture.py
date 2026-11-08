"""Deterministic, synthetic-only cross-tree capture subprocess (no hardware/data).

Executed with the selected tree first on sys.path. The only shared seams are
synthetic battery readings, RSS/provenance and traceback source locations.
No receipt code or collector decision is patched out.
"""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch


def normalize_metadata(value):
    if isinstance(value, dict):
        return {key: (None if key == 'process_rss_bytes' else normalize_metadata(item))
                for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_metadata(item) for item in value]
    return value


def capture(out):
    import subprocess
    import traceback
    from joulewise import bundle, controller
    from joulewise.cli import validate_bundle
    from scripts import align_v4_w1_synthetic as dry
    from tests import battery_float_fixture
    real_run = controller.run_benchmark

    def fresh_ioreg(*, now_s):
        return ('+-o AppleSmartBattery  <class AppleSmartBattery, id 0x1, registered, matched, active, busy 0 (0 ms), retain 1>\n'
                '    {\n      "ExternalConnected" = Yes\n      "IsCharging" = No\n'
                '      "InstantAmperage" = 0\n      "UpdateTime" = '+str(int(now_s))+'\n    }\n').encode()

    def run(config, runs_root, clock, **kwargs):
        kwargs.setdefault('battery_clock', clock)
        kwargs.setdefault('battery_runner', lambda argv: subprocess.CompletedProcess(
            argv, 0, fresh_ioreg(now_s=clock.now()), b''))
        return real_run(config, runs_root, clock, **kwargs)

    # Provenance is deliberately synthetic and equal in both trees. This also
    # avoids hashing unrelated files during the blinded capture test.
    provenance = dict(git_commit='a'*40, tracked='clean', staged='clean',
                      untracked='clean', diff_sha256='b'*64)
    out.mkdir()
    with patch.object(battery_float_fixture, 'fresh_ioreg', side_effect=fresh_ioreg), \
         patch.object(controller, 'run_benchmark', side_effect=run), \
         patch.object(bundle, '_capture_source_state', return_value=provenance), \
         patch.object(controller.traceback, 'format_exc', side_effect=lambda: ''.join(
             traceback.format_exception_only(*sys.exc_info()[:2]))), \
         redirect_stdout(io.StringIO()):
        dry.collect(SimpleNamespace(variant='kit', inject='all', leak=0.004, members='all'), out)
    problems = {}
    for path in sorted([*(out / 'runs').glob('*/metadata.json'), *(out / 'pilot7').glob('*/metadata.json')]):
        problems[path.parent.name] = validate_bundle(path.parent)
    markers, manifest = [], {}
    for path in sorted(out.rglob('*')):
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if path.name == 'events.jsonl':
            kept = []
            for line in raw.splitlines(keepends=True):
                row = json.loads(line)
                if row.get('event_type') == 'timing_boundary':
                    markers.append(row)
                else:
                    kept.append(line)
            raw = b''.join(kept)
        if path.name == 'metadata.json':
            raw = (json.dumps(normalize_metadata(json.loads(raw)), indent=2, sort_keys=True)+'\n').encode()
        # Same output path is used for both captures. Only source-worktree
        # paths can differ; no clock, numeric result or error is normalized.
        raw = raw.replace(str(Path.cwd()).encode(), b'<source-tree>')
        manifest[str(path.relative_to(out))] = hashlib.sha256(raw).hexdigest()
        normalized = out.parent / (out.name + '.normalized') / path.relative_to(out)
        normalized.parent.mkdir(parents=True, exist_ok=True)
        normalized.write_bytes(raw)
    reader_summary = None
    if markers:
        from joulewise.align.window_timing import read_window
        report = read_window(lambda path: (out/path).read_bytes(),
                             bundles=[str(p.parent.relative_to(out)) for p in sorted((out/'runs').glob('*/metadata.json'))])
        reader_summary = dict(unattributed_in_member_ns=sum(
            member['phase_ns']['unattributed'] for member in report['members'].values()),
            wall_ns=report['wall_ns'], warnings=report['warnings'],
            unknown={name: member['phase_ns']['unattributed'] for name, member in report['members'].items()})
    return dict(manifest=manifest, markers=len(markers), problems=problems, reader=reader_summary)


def desk(root):
    from joulewise.b5 import harvest
    from tests.test_session_structure import SessionStructureTests
    try:
        from joulewise import timing_receipts as timing
        from scripts import run_night as driver
    except ImportError:  # the pinned base predates markers
        timing = driver = None
    result = {}
    for refused in (False, True):
        fixture = SessionStructureTests()
        fixture.setUp()
        try:
            night = fixture.custody / 'night'
            journal = night / 'chain-stages.jsonl'
            if refused:
                journal.unlink()
            # This is the driver's pre-existing journal in either tree.
            (fixture.custody / 'night.log').write_text('synthetic driver started\n')
            if timing is not None:
                plan = SimpleNamespace(plan_id='W1', hazard_window=None)
                with driver._timing_journal(night, plan), timing.span('arm', 'admission'):
                    pass
            h = harvest._Harvest.__new__(harvest._Harvest)
            h.inputs = SimpleNamespace(night_dir=night)
            h.roster, h.members, h._campaign_rows = {'members': []}, {}, {}
            h.derived = fixture.archive / 'derived'
            h.outputs = {}
            flags = []
            h.emit = lambda code, **kw: flags.append(dict(code=code, **kw))
            # Exercise the real stage reader, collection-presence decision,
            # yield serializer, and complete structure checker. This fixture
            # intentionally has an empty roster; it reads no member evidence.
            presence = h.collection_presence()
            (h.derived / 'yield.json').unlink()
            h.yield_summary()
            record = fixture.check()
            result[str(refused)] = dict(presence=presence, flags=flags,
                stage_journal=h.stage_journal(), yield_bytes=(h.derived/'yield.json').read_text(),
                structure_bytes=json.dumps(record, sort_keys=True), journal_exists=journal.exists())
        finally:
            fixture.doCleanups()
    return result


if __name__ == '__main__':
    operation, output = sys.argv[1:]
    result = capture(Path(output)) if operation == 'capture' else desk(Path(output))
    Path(str(output)+'.json').write_text(json.dumps(result, sort_keys=True))
