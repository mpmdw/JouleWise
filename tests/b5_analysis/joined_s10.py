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
from tests.b5_analysis.fixtures_s10 import chain_fixture, FIXTURES
from tests.git_fixture import init_git_fixture

JOINED_SEAMS = (
    ('dry_run._test_repo_root', 'Scratch Git repository with identical sealed packs, supply map and tracked synthetic index.'),
    ('dry_run._test_seal_pins', 'Use the real SealPins loaded from the analysis checkout.'),
    ('dry_run._test_pack_table', 'None for joined S10; S0 and the partial-index census use only the explicit RealReaderDriverTests table.'),
    ('dry_run._git', 'Assert the scratch repository is clean and returns its actual anchor H.'),
    ('mint_floor_artifact_generalized._actual_v2_git_state', 'Supply scratch H and synthetic origin/main containment; mint computation stays real.'),
    ('identity_pins._load_mint_module()._actual_v2_git_state', 'The independently loaded mint module observes the same scratch H.'),
    ('identity_pins._load_mint_module().REPO_ROOT', 'Custody reads actual Git blobs from the scratch repository.'),
    ('paper_reported_energy.verify_registration_ordering', 'Replay the existing registered ordering history in the source repository; the one-commit scratch repository has no such history.'),
)


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
        init_git_fixture(self.repo, '-q')
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


def replay_synthetic_stages(root):
    """Join real arithmetic stages on small synthetic operands, without collection.

    Boundary seams: S6's synthetic consumption summaries and primary common-mode
    operands; S5's already-loaded claim bundles, metric/precheck/variance/bound
    observations; synthetic realized consumer stacks at finalization; and the
    engine's documented pure-resolver request factory. No stage result, floor
    resolution, estimate, multiplicity calculation or fill validator is replaced.
    This is separate from the opt-in complete joined CLI/reader acceptance run.
    """
    import copy
    from dataclasses import replace
    from types import SimpleNamespace
    from unittest import mock
    from joulewise import analysis_engine as engine, analysis_manifest_v3 as finalizer
    from joulewise import dominance_closeout as closeout
    from joulewise.analysis_engine.inputs import FloorRequest, authenticate_floor_artifact_bytes
    from joulewise.analysis_engine.artifact import render_claim_verdicts, validate_claim_verdicts
    from joulewise.results_fill_adapter import adapt_claim_verdicts, validate_results_fill_projection
    from scripts import mint_floor_artifact_generalized as mint, emit_floor_mint_pinset as emit
    from tests.b5_analysis.fixtures_s10 import synthetic_stage_fixture
    from tests.b5_analysis import test_mint_kept_units as s6, fixtures_s5 as s5
    from tests.test_emit_floor_mint_pinset import contracts_from_pins

    root = Path(root)
    fixture = synthetic_stage_fixture()
    producers = fixture.producers
    pinset_path = root/'floor-mint-pinset.json'
    with s6.registered(producers.entries), s6.common_seams():
        pins = emit.build_pinset(contracts=contracts_from_pins(producers.pins),
            producer_inputs=producers.inputs, ledger_snapshot=producers.snapshots,
            relative_plan_paths=['alpha/calibration_plan.json', 'beta/calibration_plan.json'],
            pinset_path=pinset_path, project_commit='0'*40,
            kept_units={e.producer_plan_id: e.kept_units for e in producers.entries.values()},
            window_brackets={e.producer_plan_id: e.archive_context.window_bracket
                             for e in producers.entries.values()})
        pinset_raw = mint._artifact_payload(pins)
        pinset_path.write_bytes(pinset_raw)
        pinset_sha = hashlib.sha256(pinset_raw).hexdigest()
        sink = {}
        floor, components = mint._build_v2_artifacts(pinset=mint._parse_v2_pinset(pins),
            pinset_path=pinset_path, pinset_sha256=pinset_sha, producer_inputs=producers.inputs,
            calibration_ledger_snapshot=producers.snapshots, project_commit='0'*40,
            project_tree_state='clean', recomputation_sink=sink, d165_replay_out=root/'replay.json')
        sidecar = closeout.build_d165_replay_sidecar(floor, sink)
        mint._validate_block5_sidecar(sidecar, mint._parse_v2_pinset(pins), producers.inputs)
    mint._write_v2_artifact_outputs(output_core=mint._fresh_original_core(), artifact=floor,
        sidecar=sidecar, floor_path=root/'floor.json', statement_path=root/'single-count.md',
        d165_replay_out=root/'replay.json')
    floor_raw = (root/'floor.json').read_bytes()
    authenticated = authenticate_floor_artifact_bytes(floor_raw, pinset_path=pinset_path,
        expected_pinset_sha256=pinset_sha)

    loaded = fixture.claims
    manifest = copy.deepcopy(loaded.manifest)
    cells = {cell['cell_id']: cell for cell in floor['cells']}
    arms, contexts = [], {}
    # Synthetic consumers use the actual emitted families and stacks. Nothing
    # is added to a minted cell's family admission or stress envelope.
    for role in ('decode', 'prefill'):
        for index, label in enumerate(('A', 'B')):
            cell = cells[f'cell-{index}-{role}']
            key = cell['key']
            family = key['condition_family_id']
            arm = copy.deepcopy(manifest['arms'][index])
            arm.update(condition_family_id=family, condition_family_sha256=key['condition_family_sha256'],
                arm_id=role+':'+label, floor_cell_id=cell['cell_id'],
                floor_stack_identity=cell['source_regime']['stack_identity'])
            arms.append(arm)
            contexts[family] = (key['backend'], cell['source_regime']['stack_identity_sha256'],
                                cell['source_regime']['stack_identity'])
    for contrast in manifest['contrasts']:
        role = contrast['contrast_id']
        sources = [cells[f'cell-{index}-{role}'] for index in (0, 1)]
        families = [cell['key']['condition_family_id'] for cell in sources]
        contrast.update(condition_a_id=families[0], condition_b_id=families[1], measurement_arm=role)
        contrast['metric']['name'] = 'phase_energy_j.'+role
        contrast['floor_selector'].update(metric='phase_energy_j.'+role, condition_family_ids=families)
        bindings = []
        for cell in sources:
            group = next(g for g in floor['transport_groups']
                         if g['transport_group_id'] == cell['transport_group_id'])
            bindings.append(dict(transport_group_id=group['transport_group_id'],
                condition_family_id=cell['key']['condition_family_id'],
                condition_domain_sha256=cell['key']['condition_family_sha256'], group_rule_id=group['rule_id']))
        contrast['floor_dependency'] = dict(floor_selector=copy.deepcopy(contrast['floor_selector']),
            transport=dict(mode='exact_stack_only', transport_groups=bindings))
    for entry in manifest['entries']:
        role = 'prefill' if entry['entry_id'].startswith('prefill-') else 'decode'
        index = 0 if entry['arm_id'] == 'A' else 1
        entry['condition_id'] = cells[f'cell-{index}-{role}']['key']['condition_family_id']
    entries = {entry['entry_id']: entry for entry in manifest['entries']}
    for collection in (loaded.effective, loaded.registered):
        for entry_id, evidence in collection.items():
            evidence.entry = entries[entry_id]
    prospective = dict(condition_families=[dict(condition_family_id=arm['condition_family_id'],
        canonical_domain_sha256=arm['condition_family_sha256']) for arm in arms], contrasts=manifest['contrasts'])
    with mock.patch.object(finalizer, '_floor_consumer_contexts', return_value=contexts):
        dependencies = finalizer._authenticate_floor_dependencies(prospective, floor, bundle_paths={})
    manifest['arms'] = [{**arm, **dependencies[arm['arm_id']]} for arm in arms]
    closeout_error = closeout._contrast_floor_binding_error(manifest, floor, sidecar)
    manifest['evidence'] = dict(
        analysed_attempt_exclusions=dict(sha256=loaded.kept_units.exclusions_sha256),
        aggregate_floor_artifact=dict(path='floor.json', sha256=hashlib.sha256(floor_raw).hexdigest()))
    manifest_raw = mint._artifact_payload(manifest)
    (root/'manifest.json').write_bytes(manifest_raw)
    roots = {}
    for cell in floor['cells']:
        for kind in ('absolute', 'comparative'):
            component = cell['provenance'][kind]
            roots.setdefault(component['evidence_root_id'], set()).add(component['campaign_log']['sha256'])
    audit = [loaded.supersession_audit[0]] + [dict(scope='floor_evidence', evidence_root_id=rid,
        authenticated_basis=dict(kind='floor_component_campaign_log_sha256', sha256s=sorted(hashes)),
        raw_count=0, validated_count=0, status='clean') for rid, hashes in roots.items()]
    loaded = replace(loaded, manifest=manifest, manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
        floor_artifact=floor, floor_artifact_bytes=floor_raw, floor_sha256=hashlib.sha256(floor_raw).hexdigest(),
        supersession_audit=tuple(audit))

    def request(contrast, family, evidence, artifact):
        # The documented engine injection supplies synthetic request operands;
        # the production resolver still selects and copies the actual cell.
        cell = next(c for c in artifact['cells'] if c['key']['condition_family_id'] == family)
        key = cell['key']
        return FloorRequest(backend=key['backend'], metric=key['metric'], window_class=key['window_class'],
            condition_family_id=family, condition_family_sha256=key['condition_family_sha256'],
            stack_identity_sha256=cell['source_regime']['stack_identity_sha256'], consumer_stress={})

    resolver = engine._resolve_contrast_floor
    with s5.arithmetic_seams(loaded), mock.patch.object(engine, '_resolve_contrast_floor', resolver), \
         mock.patch.object(engine, 'sibling_floor_pinset', return_value=pinset_path):
        verdict = engine.analyze_claims(root/'manifest.json', Path('runs'), root/'floor.json',
            strict_validator=lambda *_: (), _floor_request_factory=request)
    validation = validate_claim_verdicts(verdict, frozen_manifest=manifest, floor_pinset_path=pinset_path)
    verdict_raw = render_claim_verdicts(verdict)
    (root/'verdicts.json').write_bytes(verdict_raw)
    fill = adapt_claim_verdicts(verdict_raw, campaigns={'alpha': {}, 'beta': {}},
        floor_pinset_path=pinset_path, finalized_manifest_raw=manifest_raw, floor_artifact_raw=floor_raw,
        exclusions_sha256=loaded.kept_units.exclusions_sha256, kept_quads=loaded.kept_quads,
        expected_contrast_ids=tuple(row['contrast_id'] for row in manifest['contrasts']))
    validate_results_fill_projection(fill, verdict)
    (root/'fill.json').write_bytes(mint._artifact_payload(fill))
    return SimpleNamespace(fixture=fixture, floor=floor, components=components, authenticated=authenticated,
        sidecar=sidecar, dependencies=dependencies, closeout_error=closeout_error, loaded=loaded,
        verdict=verdict, validation=validation, fill=fill, root=root)
