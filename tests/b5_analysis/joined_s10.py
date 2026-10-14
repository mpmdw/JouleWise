"""Real joined-driver harness. Synthetic inputs and Git observations only.

The cache is shared by JoinedRunTests and JoinedProbeTests. Class cleanup
removes its repository (including .git); the immutable outputs survive until
interpreter exit so the probes do not execute a second driver run.
"""
from __future__ import annotations

import atexit
import ast
from contextlib import ExitStack, contextmanager, redirect_stderr, redirect_stdout
from dataclasses import dataclass
import hashlib
import inspect
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from joulewise.b5_analysis import dry_run as d
from joulewise.b5_analysis.windows import SealPins
from tests.b5_analysis.fixtures_s10 import chain_fixture, FIXTURES, CONDITIONAL_SEAMS, conditional_seams

JOINED_SEAMS = (
    ('dry_run._test_repo_root', 'Scratch Git repository with identical sealed packs, supply map and tracked synthetic index.'),
    ('dry_run._test_seal_pins', 'Use the real SealPins loaded from the analysis checkout.'),
    ('dry_run._test_pack_table', 'None for joined S10; S0 and the partial-index census use only the explicit RealReaderDriverTests table.'),
    ('dry_run._git', 'Assert the scratch repository is clean and returns its actual anchor H.'),
    ('mint_floor_artifact_generalized._actual_v2_git_state', 'Supply scratch H and synthetic origin/main containment; mint computation stays real.'),
    ('identity_pins._load_mint_module()._actual_v2_git_state', 'The independently loaded mint module observes the same scratch H.'),
    ('identity_pins._load_mint_module().REPO_ROOT', 'Custody reads actual Git blobs from the scratch repository.'),
    ('paper_reported_energy.verify_registration_ordering', 'Replay the existing registered ordering history in the source repository; the one-commit scratch repository has no such history.'),
) + tuple((name, reason) for _side, name, reason in CONDITIONAL_SEAMS)


def require_windows():
    # The loader can only build windows with these archives. Avoid an expensive
    # ALPHA restore just to skip a whole-block class on a partial fixture.
    if any(not (FIXTURES / pack / 'archive.tar.xz').is_file() for pack in d.PACKS):
        raise unittest.SkipTest('window not built')
    fixture = chain_fixture()
    if set(d.PACKS) - set(fixture.windows):
        raise unittest.SkipTest('window not built')
    return fixture


@contextmanager
def capture_driver_streams():
    """Capture both Python and descriptor writes, including nested runners."""
    captured = {}
    with tempfile.TemporaryFile(mode='w+', encoding='utf-8', errors='backslashreplace') as out, \
         tempfile.TemporaryFile(mode='w+', encoding='utf-8', errors='backslashreplace') as err:
        sys.stdout.flush()
        sys.stderr.flush()
        saved_out, saved_err = os.dup(1), os.dup(2)
        try:
            os.dup2(out.fileno(), 1)
            os.dup2(err.fileno(), 2)
            with redirect_stdout(out), redirect_stderr(err):
                yield captured
        finally:
            out.flush()
            err.flush()
            try:
                os.dup2(saved_out, 1)
                os.dup2(saved_err, 2)
            finally:
                os.close(saved_out)
                os.close(saved_err)
            out.seek(0)
            err.seek(0)
            captured.update(stdout=out.read(), stderr=err.read())


@dataclass
class RunResult:
    code: int
    custody: Path
    path: Path
    record: dict | None
    stdout: str
    stderr: str
    wall_s: float
    state: object
    calls: list
    disclosure_reads: list
    disclosure_builds: list
    restored_contexts: list
    validations: list
    tripwires: list
    reader_failures: list


@contextmanager
def observe_run():
    """Read-only CPython return observation; no program callable is replaced."""
    from joulewise import whole_window as ww
    from joulewise.b5_analysis import context, kept_units
    from scripts import produce_b5_disclosures as disclosures

    evidence = dict(state=None, calls=[], disclosure_reads=[], disclosure_builds=[], restored_contexts=[],
                    validations=[], tripwires=[], reader_failures=[])
    sources = {
        d.RunState.__init__.__code__: 'state',
        d.StepRunner.run.__code__: 'calls',
        disclosures.load_step_outputs.__code__: 'disclosure_reads',
        disclosures.build_disclosure_inputs.__code__: 'disclosure_builds',
        context.build_context.__code__: 'restored_contexts',
        ww.validate_whole_window_verdict_row.__code__: 'validations',
        kept_units.require_kept_members_in_verdict.__code__: 'tripwires',
    }

    def returned(code, offset, result):
        frame = sys._getframe(1)
        args = frame.f_locals
        kind = sources[code]
        if kind == 'state':
            evidence[kind] = args['self']
        elif kind == 'calls':
            evidence[kind].append(dict(main=args['main'], argv=list(args['argv']),
                step=args['step'], window=args['window'], result=result))
        elif kind == 'disclosure_reads':
            evidence[kind].append(dict(custody=args['custody'], registry=args['step_outputs'],
                values=result[0], paths=result[1]))
        elif kind == 'disclosure_builds':
            evidence[kind].append(dict(index=args['window_index'], paths=args['paths'], result=result))
        elif kind == 'restored_contexts':
            view = args['kept_units']
            if view.sensitivity_label == 'load-correlated':
                evidence[kind].append(dict(view=view, context=result, row=args['row']))
        elif kind == 'validations':
            evidence[kind].append(dict(args=dict(args), result=result))
        elif kind == 'tripwires':
            view = args['kept_units']
            if view.sensitivity_label == 'load-correlated':
                evidence[kind].append(dict(view=view, bundle_ids=args['bundle_ids']))

    def unwound(code, offset, exception):
        if code is not d._sha.__code__:
            return
        frame = sys._getframe(1)
        evidence['reader_failures'].append(dict(path=str(frame.f_locals['path']),
                                               error=type(exception).__name__))

    tool = next(number for number in range(6) if sys.monitoring.get_tool(number) is None)
    sys.monitoring.use_tool_id(tool, 's10-joined-readonly-observer')
    event = sys.monitoring.events.PY_RETURN
    unwind = sys.monitoring.events.PY_UNWIND
    try:
        sys.monitoring.register_callback(tool, event, returned)
        for source in sources:
            sys.monitoring.set_local_events(tool, source, event)
        sys.monitoring.register_callback(tool, unwind, unwound)
        # PY_UNWIND is a global event in CPython 3.13; filter to this reader.
        sys.monitoring.set_events(tool, unwind)
        yield evidence
    finally:
        for source in sources:
            sys.monitoring.set_local_events(tool, source, 0)
        sys.monitoring.set_events(tool, 0)
        sys.monitoring.register_callback(tool, event, None)
        sys.monitoring.register_callback(tool, unwind, None)
        sys.monitoring.free_tool_id(tool)


class JoinedHarness:
    def __init__(self, index, *, windows=(), pack_table=None):
        self.temporary = tempfile.TemporaryDirectory(prefix='s10-joined-')
        atexit.register(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.repo = self.root / 'repository'
        self.repo.mkdir()
        self.pins = SealPins.load()
        self.pack_table = pack_table
        from joulewise import paper_custody as custody
        shutil.copytree(d.ROOT / 'configs/campaigns', self.repo / 'configs/campaigns')
        supply = self.repo / custody._SUPPLY_MAP_PATH
        supply.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(d.ROOT / custody._SUPPLY_MAP_PATH, supply)
        # S0 packs are producer-owned synthetic packs, outside the sealed tree.
        for window in windows:
            pack_id = window.entry_data['pack_id']
            source = window.archive / 'sources/repo/configs/campaigns' / pack_id
            destination = self.repo / 'configs/campaigns' / pack_id
            if not destination.exists():
                shutil.copytree(source, destination)
        self.index = self.repo / custody._B5_WINDOW_INDEX_PATH
        self.index.parent.mkdir(parents=True, exist_ok=True)
        self.index.write_bytes(Path(index).read_bytes())
        self.git('init', '-q')
        self.git('add', '--all')
        self.git('-c', 'user.name=S10 synthetic harness', '-c', 'user.email=s10@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'Synthetic joined inputs')
        self.head = self.git('rev-parse', 'HEAD').strip()

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], check=True,
                              capture_output=True, text=True).stdout

    def remove_repository(self):
        if self.repo.exists():
            shutil.rmtree(self.repo)

    def close(self):
        self.temporary.cleanup()

    @contextmanager
    def git_seams(self):
        from joulewise import identity_pins, paper_reported_energy as energy
        from scripts import mint_floor_artifact_generalized as mint
        identity_mint = identity_pins._load_mint_module()
        ordering = energy.verify_registration_ordering

        def registered_history(repository, model):
            if Path(repository) != self.repo:
                raise AssertionError('ordering repository differs from joined repository')
            return ordering(d.ROOT, model)

        def checkout(repository):
            if Path(repository) != self.repo:
                raise AssertionError('driver repository differs from joined repository')
            head = d.analysis_checkout(self.repo)
            if head != self.head:
                raise AssertionError('joined anchor changed')
            return head

        with ExitStack() as seams:
            seams.enter_context(patch.object(mint, '_actual_v2_git_state', return_value=(self.head, True)))
            seams.enter_context(patch.object(identity_mint, '_actual_v2_git_state', return_value=(self.head, True)))
            seams.enter_context(patch.object(identity_mint, 'REPO_ROOT', self.repo))
            seams.enter_context(patch.object(energy, 'verify_registration_ordering', registered_history))
            seams.enter_context(conditional_seams())
            yield checkout

    def execute(self, name='first', *, mode='blind-dry-run', custody=None):
        custody = Path(custody) if custody is not None else self.root / name
        started = time.monotonic()
        with self.git_seams() as checkout, observe_run() as observed:
            with capture_driver_streams() as streams:
                code = d.run(mode, self.index, custody, _test_pack_table=self.pack_table,
                    _test_seal_pins=self.pins, _test_repo_root=self.repo, _runner=None, _git=checkout)
        path = custody / ('dry-run/B5-BLIND-DRY-RUN-RECORD.json' if mode == 'blind-dry-run'
                          else 'release/B5-RELEASE-RECORD.json')
        return RunResult(code, custody, path, json.loads(path.read_bytes()) if path.exists() else None,
                         streams['stdout'], streams['stderr'], time.monotonic() - started, **observed)


_PRIMARY = None


def cached_primary():
    global _PRIMARY
    fixture = require_windows()
    if _PRIMARY is None:
        harness = JoinedHarness(fixture.index)
        try:
            result = harness.execute()
        except BaseException:
            harness.close()
            raise
        _PRIMARY = fixture, harness, result
    return _PRIMARY


def output_digests(result):
    return {(row['step'], row['window'], output['name']): output['sha256']
            for row in result.record['steps'] for output in row['outputs']}


def chain_entries(fixture):
    """Primary window descriptors, never a later-listed historical attempt."""
    attempts = json.loads(fixture.program_index.read_bytes())['attempts']
    result = {}
    for pack in d.PACKS:
        if pack in fixture.windows:
            result[pack] = fixture.windows[pack].entry_data
        else:
            peers = [row for row in attempts if row['pack'] == pack and row['claim_usable']]
            if len(peers) != 1:
                raise AssertionError('partial program index must have one explicit peer per missing pack')
            result[pack] = peers[0]
    return result


def parse_program_argv(main, argv):
    """Use a program's own parser declarations without executing its main.

    Several scripts construct their parser inside main. Extract exactly that
    construction prefix, ending before parse_args, into a parser factory. No
    instruction following parse_args is compiled or executed. Exported parser
    factories are used directly where available.
    """
    from joulewise import cli
    from scripts import finalize_analysis_manifest as finalize
    from scripts import mint_floor_artifact_generalized as mint
    from scripts import run_d165_closeout_from_custody as closeout
    if main is cli.main:
        parser = cli.build_parser()
    elif main is finalize.main:
        parser = finalize.build_parser()
    elif main is mint.main:
        parser = mint._parser()
    elif main is closeout.main:
        parser = closeout._parser(include_window_index=True)
    else:
        function = ast.parse(inspect.getsource(main)).body[0]
        prefix = []
        for statement in function.body:
            # The disclosure parser keeps parse_args inside its try block.
            nested = statement.body if isinstance(statement, ast.Try) else [statement]
            if any(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                   and node.func.attr == 'parse_args'
                   for item in nested for node in ast.walk(item)):
                break
            prefix.append(statement)
        else:
            raise AssertionError('program has no parse_args boundary')
        factory = ast.FunctionDef(name='_joined_parser_factory', args=function.args,
            body=prefix + [ast.Return(value=ast.Name(id='parser', ctx=ast.Load()))],
            decorator_list=[], returns=None, type_params=[])
        module = ast.fix_missing_locations(ast.Module(body=[factory], type_ignores=[]))
        namespace = dict(main.__globals__)
        exec(compile(module, inspect.getsourcefile(main), 'exec'), namespace)
        parser = namespace['_joined_parser_factory'](list(argv))
    return parser.parse_args([str(arg) for arg in argv])


def assert_public_bytes(test, result, restricted_floats):
    public = [result.path.read_bytes(), result.stdout.encode(), result.stderr.encode()]
    restricted_roots = [result.custody / name / 'restricted' for name in ('dry-run', 'release')]
    public.extend(path.read_bytes() for path in result.custody.rglob('*')
                  if path.is_file() and not any(path.is_relative_to(root) for root in restricted_roots))
    # Numeric token boundaries avoid treating an admitted hex digest as data.
    import re
    tokens = re.compile(r'(?<![A-Za-z0-9])[-+]?(?:\d+\.\d*(?:[eE][-+]?\d+)?|\.\d+(?:[eE][-+]?\d+)?|\d+[eE][-+]?\d+)(?![A-Za-z0-9])')
    for raw in public:
        text = raw.decode('utf-8')
        test.assertIsNone(d._FLOAT_TOKEN.search(text), 'public float token')
        test.assertIsNone(tokens.search(text), 'public float token in alternate notation')
        for token in tokens.findall(text):
            test.assertNotIn(float(token), restricted_floats, 'restricted value in public numeric token')
    for output in result.record['steps']:
        for item in output['outputs']:
            path = result.path.parent / 'restricted' / item['name']
            test.assertTrue(path.is_file())
            test.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item['sha256'])
