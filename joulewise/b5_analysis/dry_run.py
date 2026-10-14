"""Outcome-blind block-5 dispatch, restricted custody and byte commitments."""
from __future__ import annotations

from contextlib import contextmanager, redirect_stderr, redirect_stdout
from dataclasses import dataclass, replace
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import traceback

from .steps import require_primary_context, StepRecord, step_record, classify_step4_exit
from .windows import AnalysisRefusal

ROOT = Path(__file__).resolve().parents[2]
STEP_IDS = ('0', '1', '2', '3', '3b', '4', '5', '8', '6', '9', '9b', '10', '11')
_TOKEN = re.compile(r'[A-Za-z][A-Za-z0-9_.]*')


def refusal_token(text: str) -> str | None:
    """Parse the last error line, or a bare final output line, without detail."""
    lines = text.splitlines()
    errors = [line[len('error: '):] for line in lines if line.startswith('error: ')]
    candidate = errors[-1] if errors else lines[-1] if lines else ''
    token = candidate.split(':', 1)[0]
    return token if _TOKEN.fullmatch(token) else None


def analysis_checkout(repo_root: Path = ROOT) -> str:
    """The single git seam: bind HEAD and reject every tracked change."""
    try:
        head = subprocess.run(['git', '-C', str(repo_root), 'rev-parse', 'HEAD'],
                              check=True, capture_output=True, text=True).stdout.strip()
        changes = subprocess.run(['git', '-C', str(repo_root), 'status', '--porcelain',
                                  '--untracked-files=no'], check=True,
                                 capture_output=True, text=True).stdout
        if re.fullmatch(r'[0-9a-f]{40}', head) is None or changes:
            refusal=AnalysisRefusal('analysis_checkout_not_clean')
            if re.fullmatch(r'[0-9a-f]{40}',head):refusal.analysis_commit=head
            raise refusal
        return head
    except (OSError, subprocess.SubprocessError):
        raise AnalysisRefusal('analysis_checkout_not_clean') from None


@contextmanager
def without_backup_roots():
    """Remove the environment override for the entire run and restore it."""
    existed = 'JOULEWISE_BACKUP_ROOTS' in os.environ
    original = os.environ.pop('JOULEWISE_BACKUP_ROOTS', None)
    try:
        yield existed
    finally:
        if existed:
            os.environ['JOULEWISE_BACKUP_ROOTS'] = original
        else:
            os.environ.pop('JOULEWISE_BACKUP_ROOTS', None)


@dataclass(frozen=True)
class RunnerResult:
    exit_status: int
    stdout_path: Path
    stderr_path: Path
    exception: bool = False

    def token(self) -> str | None:
        if self.exception:
            return None
        error = self.stderr_path.read_text(encoding='utf-8')
        output = self.stdout_path.read_text(encoding='utf-8')
        if any(line.startswith('error: ') for line in error.splitlines()):
            return refusal_token(error)
        return refusal_token(output)


class StepRunner:
    """Call a real main(argv), capturing Python and descriptor-level streams.

    Instances belong to one fresh run directory. A caller must supply a path
    under that run's restricted custody; run() preflights that directory.
    """
    def __init__(self, restricted: Path):
        self.restricted = Path(restricted)
        self.logs = self.restricted / 'logs'
        self.logs.mkdir(parents=True, exist_ok=True)
        self._counter = 0

    def run(self, main, argv, *, step: str, window: str | None = None,
            stdout_path: Path | None = None) -> RunnerResult:
        if step not in STEP_IDS or window not in (None, 'alpha', 'beta', 'gamma'):
            raise ValueError('step runner requires a registered step and window')
        self._counter += 1
        stem = f'{self._counter:04d}-{step}-{window or "block"}'
        stdout_path = Path(stdout_path) if stdout_path is not None else self.logs/(stem+'.stdout.log')
        if (not stdout_path.absolute().is_relative_to(self.restricted.absolute())
                or stdout_path.resolve() != stdout_path.absolute()):
            raise AnalysisRefusal('custody_path_invalid')
        stderr_path = self.logs/(stem+'.stderr.log')
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        exit_status, escaped = 2, False
        with stdout_path.open('x', encoding='utf-8', errors='backslashreplace') as out, \
             stderr_path.open('x', encoding='utf-8', errors='backslashreplace') as err:
            sys.stdout.flush(); sys.stderr.flush()
            saved_out, saved_err = os.dup(1), os.dup(2)
            try:
                os.dup2(out.fileno(), 1); os.dup2(err.fileno(), 2)
                with redirect_stdout(out), redirect_stderr(err):
                    try:
                        value = main(list(argv))
                        exit_status = value if type(value) is int else 0 if value is None else 2
                    except SystemExit as exc:
                        exit_status = exc.code if type(exc.code) is int else 0 if exc.code is None else 2
                    except BaseException:
                        escaped = True
                        traceback.print_exc()
                    finally:
                        out.flush(); err.flush()
            finally:
                try:
                    os.dup2(saved_out, 1); os.dup2(saved_err, 2)
                finally:
                    os.close(saved_out); os.close(saved_err)
        return RunnerResult(exit_status, stdout_path, stderr_path, escaped)


def require_step_inputs(restricted: Path, outputs) -> None:
    """Re-authenticate earlier output commitments before a consuming step."""
    from joulewise.authentication_io import read_authentication_input_nofollow
    for record in outputs:
        try:
            raw = read_authentication_input_nofollow(Path(restricted), record['name'],
                grammar='raw', label='earlier block-5 step output')
            actual = hashlib.sha256(raw).hexdigest()
            if actual != record['sha256']:
                raise AnalysisRefusal('step_input_digest_mismatch')
        except (OSError, ValueError, RuntimeError):
            raise AnalysisRefusal('step_input_digest_mismatch') from None


def release_difference(dry_run, release) -> dict | None:
    """First census or output difference, for already-validated records only.

    The caller validates both records before invoking this comparison.
    No output, including either disclosure view, receives an exemption here.
    """
    before, after = dry_run['input_census'], release['input_census']
    for i in range(max(len(before), len(after))):
        left = before[i] if i < len(before) else None
        right = after[i] if i < len(after) else None
        if left != right:
            return {'path': (left if left is not None else right)['path']}
    before, after = dry_run['steps'], release['steps']
    for i in range(max(len(before), len(after))):
        left = before[i] if i < len(before) else None
        right = after[i] if i < len(after) else None
        rows_a, rows_b = left['outputs'] if left else [], right['outputs'] if right else []
        for j in range(max(len(rows_a), len(rows_b))):
            a = rows_a[j] if j < len(rows_a) else None
            b = rows_b[j] if j < len(rows_b) else None
            if a != b:
                owner = left if left is not None else right
                return {'step': owner['step'], 'output': (a if a is not None else b)['name']}
    return None


def require_release_equality(dry_run, release) -> None:
    difference = release_difference(dry_run, release)
    if difference is not None:
        refusal = AnalysisRefusal('release_digest_differs_from_dry_run')
        refusal.difference = difference
        raise refusal


def primary_contexts(archives, kept_units, brackets, rows, *, synthetic=False):
    from .context import build_context

    contexts = {pack: build_context(archive, kept_units[pack], brackets[pack], rows[pack],
                test_only_allow_synthetic_binding=synthetic) for pack, archive in archives.items()}
    require_primary_context(contexts)
    return contexts


def sensitivity_contexts(contexts, bounds):
    return {pack: replace(context, sensitivity_bound_s=bounds[pack]) for pack, context in contexts.items()}


def writer_handoff(writer, contexts, *args, **kwargs):
    require_primary_context(contexts)
    return writer(*args, **kwargs)

SCHEMA = 'joulewise.b5_blind_dry_run.v1'
PACKS = ('alpha', 'beta', 'gamma')
SEAL_KEYS = ('registration_sha256', 'analysis_plan_sha256', 'flag_catalog_sha256',
             'erratum_2_sha256', 'erratum_3_sha256')
STATUSES = ('ok', 'tooling_refusal', 'outcome_class', 'unclassified_refusal', 'not_run')
FLAGS = ('backup_roots_env_ignored', 'runs_root_has_unlisted_file', 'harvest_checkout_status_not_clean')
CHECKS = ('input_census', 'window_index', 'harvest_outputs', 'sources_sha256sums', 'withheld_no_harvest_digest', 'withheld',
          'plan_tree_binding:sealed', 'plan_tree_binding:synthetic', 'ledger_prefix_of_live')
_FLOAT_TOKEN = re.compile(r'(?<![A-Za-z0-9])(?:\d+\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+)(?![A-Za-z0-9])')


def _plain(value):
    from collections.abc import Mapping
    if isinstance(value, Mapping):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def _canonical(value):
    from joulewise.calibration_ledger import canonical_json_bytes
    return canonical_json_bytes(_plain(value))


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def refusal_classes():
    return json.loads((ROOT/'configs/analysis/b5/dry_run_refusal_classes.json').read_bytes())


def custody_preflight(mode, custody, repo_root):
    """Reject aliases and occupied run directories before invoking any program."""
    if mode not in ('blind-dry-run', 'release'):
        raise AnalysisRefusal('analysis_mode_invalid')
    root = Path(custody).absolute()
    if (any(char.isspace() for char in str(root)) or '..' in root.parts
            or root.resolve() != root or any(p.is_symlink() for p in (root, *root.parents))):
        raise AnalysisRefusal('custody_path_invalid')
    if root.is_relative_to(Path(repo_root).resolve()):
        raise AnalysisRefusal('custody_inside_repository')
    if root.exists() and (not root.is_dir() or any(p.is_symlink() for p in root.rglob('*'))):
        raise AnalysisRefusal('custody_path_invalid')
    target = root/('dry-run' if mode == 'blind-dry-run' else 'release')
    if target.exists():
        raise AnalysisRefusal('custody_run_directory_exists')
    if mode == 'release':
        previous = root/'dry-run/B5-BLIND-DRY-RUN-RECORD.json'
        try:
            record = json.loads(previous.read_bytes())
            if record['completed_without_tooling_refusal'] is not True:
                raise ValueError()
        except (OSError, ValueError, KeyError, TypeError):
            raise AnalysisRefusal('dry_run_record_missing_or_incomplete') from None
    return target


def build_dry_run_record(*, mode, analysis_commit, window_index_sha256, sealed,
                         attempts=(), windows=(), input_census=(), steps=(), difference=None):
    record = {'schema_version': SCHEMA, 'mode': mode, 'analysis_commit': analysis_commit,
        'window_index_sha256': window_index_sha256, 'sealed': dict(sealed),
        'attempts': _plain(attempts), 'windows': _plain(windows), 'input_census': _plain(input_census),
        'steps': [s.as_dict() if isinstance(s, StepRecord) else _plain(s) for s in steps]}
    record['completed_without_tooling_refusal'] = bool(record['steps']) and not any(
        s['status'] in ('tooling_refusal', 'unclassified_refusal') for s in record['steps'])
    if difference is not None:
        record['release_difference'] = dict(difference)
    return record


def _validate_dry_run_record(record, *, index=None, kept_units=None):
    """Closed shape and trusted identifier vocabulary; no arbitrary JSON leaf.

    Callers validating an external index supply its already validated WindowIndex.
    Without that vocabulary only records without attempts/windows are accepted.
    Cell identifiers come from authenticated KeptUnits, never from this record.
    """
    def need(condition):
        if not condition:
            raise AnalysisRefusal('dry_run_record_invalid')
    def keys(obj, expected):
        need(type(obj) is dict and set(obj) == set(expected))
    def digest(value, width=64):
        need(type(value) is str and re.fullmatch('[0-9a-f]{'+str(width)+'}', value) is not None)
    def integer(value):
        need(type(value) is int and value >= 0)
    def boolean(value):
        need(type(value) is bool)
    def path(value):
        need(type(value) is str and bool(value) and '\\' not in value and '\x00' not in value
             and not _FLOAT_TOKEN.search(value) and not Path(value).is_absolute()
             and all(p not in ('', '.', '..') for p in value.split('/')))
    keys(record, {'schema_version','mode','analysis_commit','window_index_sha256','sealed',
        'attempts','windows','input_census','steps','completed_without_tooling_refusal'} |
        ({'release_difference'} if 'release_difference' in record else set()))
    need(record['schema_version'] == SCHEMA and record['mode'] in ('blind-dry-run','release'))
    digest(record['analysis_commit'], 40); digest(record['window_index_sha256'])
    keys(record['sealed'], SEAL_KEYS)
    for value in record['sealed'].values(): digest(value)
    entries = tuple(index.entries) if index is not None else ()
    plans = {entry.plan_id for entry in entries}
    census_paths = {'binding/plan_tree', 'ledger/live/calibration_observation_ledger.jsonl'}
    for entry in entries:
        if entry.archive_root is not None:
            # Archive inventory names are trusted only from the index-pinned harvest.
            try:
                raw = (entry.archive_root/'harvest.json').read_bytes()
                if hashlib.sha256(raw).hexdigest() == entry.harvest_record_sha256:
                    census_paths.update(json.loads(raw)['outputs'])
            except (OSError, ValueError, KeyError, TypeError): pass
    for name in ('attempts','windows','input_census','steps'): need(type(record[name]) is list)
    for row in record['attempts']:
        keys(row, ('pack','seal','attempt','plan_id','record_shape','verdict','claim_usable','analysed'))
        need(row['pack'] in PACKS and row['seal'] in ('first','second') and row['plan_id'] in plans)
        integer(row['attempt']); need(row['attempt'] > 0)
        need(row['record_shape'] in (None,'pin1','pin2','pin3','pin4'))
        need(row['verdict'] in ('COLLECTED','NULL','HARVEST_FAULT','NO_COLLECTION'))
        boolean(row['claim_usable']); boolean(row['analysed'])
    for row in record['windows']:
        keys(row, ('pack','plan_id','harvest_record_sha256','harvest_pin','kept_counts'))
        need(row['pack'] in PACKS and row['plan_id'] in plans)
        digest(row['harvest_record_sha256']); digest(row['harvest_pin'],40)
        need(type(row['kept_counts']) is dict)
        cells = set(kept_units.get(row['pack']).cells) if kept_units and row['pack'] in kept_units else set()
        need(set(row['kept_counts']) <= cells)
        for counts in row['kept_counts'].values():
            keys(counts, ('n_r','n_b')); integer(counts['n_r']); integer(counts['n_b'])
    for row in record['input_census']:
        keys(row, ('window','path','sha256','check'))
        need(row['window'] in PACKS and row['check'] in CHECKS)
        path(row['path']); digest(row['sha256'])
        # Source names and original-root names are inventory-relative paths.
        need(row['path'] in census_paths or row['path'].startswith(('sources/','original/claim-runs/','withheld/'))
             or (row['check'] == 'window_index' and row['path'] == 'harvest.json'))
    classes = refusal_classes()['tooling_refusal']
    order=[]
    for row in record['steps']:
        if not order or order[-1]!=row.get('step'):order.append(row.get('step'))
    need(tuple(order)==STEP_IDS)
    stopped=False
    for row in record['steps']:
        keys(row, ('step','window','status','exit_status','registered_exit','schema_valid','outputs','refusal','flags'))
        need(row['step'] in STEP_IDS and row['window'] in (None,*PACKS) and row['status'] in STATUSES)
        if row['exit_status'] is not None: integer(row['exit_status'])
        need(row['registered_exit'] in (None,'p42_floor_cells_only'))
        need(row['schema_valid'] is None or type(row['schema_valid']) is bool)
        need(type(row['flags']) is list and all(type(f) is str and f in FLAGS for f in row['flags']))
        need(type(row['outputs']) is list)
        for output in row['outputs']:
            keys(output, ('name','sha256')); path(output['name']); digest(output['sha256'])
            need(output['name'].split('/')[0] in ('outputs','rereduced','attempts','supply-census',
                'kept-units','tripwires','brackets','mint','finalized','inputs','disclosures','custody') or
                re.fullmatch(r'analysed-attempt-exclusions-[0-9a-f]{64}\.json',output['name']) is not None or
                re.fullmatch(r'am-[0-9a-f]{64}\.finalized\.json',output['name']) is not None)
        expected = (None if row['status'] in ('ok','not_run') else
            'outcome-class refusal at step '+row['step'] if row['status'] == 'outcome_class' else
            'unclassified refusal at step '+row['step'] if row['status'] == 'unclassified_refusal' else row['refusal'])
        need(row['refusal'] == expected)
        if row['status'] == 'tooling_refusal':
            need(type(row['refusal']) is str and row['refusal'] in classes and _TOKEN.fullmatch(row['refusal']) is not None)
        if row['status'] == 'not_run':
            need(stopped and row['exit_status'] is None and row['outputs'] == [] and row['schema_valid'] is None)
        elif stopped:
            # A release-equality refusal is reported at the last registered
            # step even when a prior outcome ended the analysis.
            need(record['mode']=='release' and row['step']=='11' and
                 row['refusal']=='release_digest_differs_from_dry_run')
        if row['status']=='ok':
            need(row['exit_status']==0 or (row['step']=='4' and row['exit_status']==1
                 and row['registered_exit']=='p42_floor_cells_only'))
        if row['status'] not in ('ok','not_run'):stopped=True
    boolean(record['completed_without_tooling_refusal'])
    need(record['completed_without_tooling_refusal'] == (bool(record['steps']) and not any(
        s['status'] in ('tooling_refusal','unclassified_refusal') for s in record['steps'])))
    if 'release_difference' in record:
        diff = record['release_difference']
        if type(diff) is dict and set(diff) == {'path'}: path(diff['path'])
        else:
            keys(diff, ('step','output')); need(diff['step'] in STEP_IDS); path(diff['output'])


def validate_dry_run_record(record, *, index=None, kept_units=None):
    try:
        if index is None:
            tracked=ROOT/'configs/analysis/b5/analysed_windows.json'
            if tracked.is_file():
                from .windows import load_window_index
                index=load_window_index(tracked)
        if kept_units is None and index is not None:
            from types import SimpleNamespace
            kept_units={}
            for entry in index.entries:
                if entry.archive_root is None or not entry.claim_usable:continue
                raw=(entry.archive_root/'harvest.json').read_bytes()
                if hashlib.sha256(raw).hexdigest()!=entry.harvest_record_sha256:continue
                harvest=json.loads(raw)
                raw=(entry.archive_root/'derived/exclusions.json').read_bytes()
                if hashlib.sha256(raw).hexdigest()!=harvest['outputs']['derived/exclusions.json']:continue
                kept_units[entry.pack]=SimpleNamespace(cells={row['cell_id']:None for row in json.loads(raw)['cells']})
        _validate_dry_run_record(record,index=index,kept_units=kept_units)
    except AnalysisRefusal:
        raise
    except (OSError,KeyError,TypeError,ValueError,AttributeError,RecursionError):
        raise AnalysisRefusal('dry_run_record_invalid') from None


class RunState:
    def __init__(self, mode, index_path, restricted, commit, *, pack_table=None, seal_pins=None, repo_root=ROOT):
        from .windows import SealPins
        self.mode, self.index_path, self.restricted, self.commit = mode, Path(index_path), Path(restricted), commit
        self.repo_root, self.pack_table, self.pins = Path(repo_root), pack_table, seal_pins or SealPins.load()
        self.index = None
        self.records, self.windows, self.archives = (), {}, {}
        self.kept, self.specs, self.rows, self.brackets, self.contexts = {}, {}, {}, {}, {}
        self.outputs, self.step_records, self.ledger_rows = {}, [], []
        self.b_max = None
        self.flags = []
        self.ignored_backup = False
        self.classes = refusal_classes()

    def path(self, relative):
        if (type(relative) is not str or not relative or '\\' in relative or '\x00' in relative
                or Path(relative).is_absolute() or any(part in ('','.','..') for part in relative.split('/'))):
            raise AnalysisRefusal('custody_path_invalid')
        path = self.restricted/relative
        if path.resolve()!=path.absolute() or not path.absolute().is_relative_to(self.restricted.absolute()):
            raise AnalysisRefusal('custody_path_invalid')
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def register(self, role, path):
        path = Path(path)
        if not path.absolute().is_relative_to(self.restricted.absolute()) or path.resolve() != path.absolute():
            raise AnalysisRefusal('custody_path_invalid')
        digest=_sha(path)
        fixed=(role in ('pinset','mint_inputs','plan_alpha','plan_beta','finalized_manifest','rendered_fills','closeout','ratio_table')
               or role.startswith('role_census_')
               or role.startswith(('rereduced_','gamma_pack_')) or path.parent.name=='disclosures')
        if not fixed and not path.name.startswith(digest):
            destination=path.with_name(digest+'-'+path.name)
            if destination.exists():
                raise AnalysisRefusal('custody_run_directory_exists')
            path.rename(destination)
            path=destination
        item = {'name':path.relative_to(self.restricted).as_posix(),'sha256':digest}
        self.outputs[role] = item
        return item

    def write(self, role, relative, value=None, *, raw=None, addressed=False):
        raw = _canonical(value) if raw is None else raw
        if role.startswith(('attempt_','census_','kept_','tripwire_')):
            # P9 readers' own records are structure only even in restricted
            # custody. Unlike analysis artifacts, they have no float token.
            if _FLOAT_TOKEN.search(raw.decode('utf-8')):
                raise AnalysisRefusal('reader_record_not_structure_only')
        if addressed:
            original = Path(relative)
            relative = (original.parent/(hashlib.sha256(raw).hexdigest()+original.suffix)).as_posix()
        path = self.path(relative)
        with path.open('xb') as out: out.write(raw)
        return self.register(role,path)

    def output(self, role):
        return self.restricted/self.outputs[role]['name']

    def read(self, role):
        require_step_inputs(self.restricted,[self.outputs[role]])
        return json.loads(self.output(role).read_bytes())

    def rehash(self):
        # Re-reduction probes are commitments for the cold gate; later steps
        # never consume them. Other registered files are re-authenticated as
        # a superset of the following program's artifact dependencies.
        require_step_inputs(self.restricted,[output for role,output in self.outputs.items()
                                             if not role.startswith('rereduced_')])

    def invoke(self, runner, main, argv, *, step, window=None, outputs=(), stdout_path=None):
        require_primary_context(self.contexts)
        self.rehash()
        result = runner.run(main, [str(x) for x in argv], step=step,window=window,
                            **({'stdout_path':stdout_path} if stdout_path is not None else {}))
        found=[]
        for role,path in outputs:
            if Path(path).is_file(): found.append(self.register(role,path))
        missing = len(found) != len(outputs)
        code = result.token() if result.exit_status or result.exception else None
        exit_status = result.exit_status
        if result.exception or (missing and exit_status == 0):
            code, exit_status = None, 2
        return result, found, code, exit_status

    def record(self, step, *, window=None, exit_status=0, code=None, outputs=(), flags=(), registered_exit=None):
        return step_record(step, window=window, exit_status=exit_status, refusal_code=code,
            classes=self.classes, outputs=tuple(outputs), flags=flags,
            schema_valid=True if outputs else None, registered_exit=registered_exit)

    def guarded(self, method):
        """Structure-only helper errors, including step-0/3 restricted logs."""
        def main(argv):
            try:
                return method(argv)
            except AnalysisRefusal as exc:
                print('error: '+(refusal_token(exc.code) or 'unclassified'),file=sys.stderr)
                return 2
            except Exception as exc:
                from joulewise.paper_custody import PaperCustodyRefusal
                if isinstance(exc,PaperCustodyRefusal):
                    print('error: '+(refusal_token(exc.code) or 'unclassified'),file=sys.stderr)
                    return 2
                if method.__name__ in ('prepare_initial','prepare_tripwires'):
                    print('error: unclassified',file=sys.stderr)
                    return 2
                raise
        main._state = self
        main._operation = method.__name__
        return main

    def prepare_initial(self, argv):
        from .windows import load_window_index, open_attempt_record, select_analysed_attempts
        from .archive import open_archive
        from .bracket import require_ledger_copies_are_prefixes
        self.index = load_window_index(self.index_path,seal_pins=self.pins,pack_table=self.pack_table)
        self.records = tuple(open_attempt_record(e,seal_pins=self.pins,pack_table=self.pack_table) for e in self.index.entries)
        for record in self.records:self.flags.extend(record.checkout_flags)
        self.windows = select_analysed_attempts(self.index,self.records,seal_pins=self.pins)
        for pack,window in self.windows.items():
            tree = 'sources/repo/configs/campaigns/'+window.pack_id+'/plan_tree.json'
            # A test pack table authorizes synthetic ids only. Bind its archived
            # tree explicitly; sealed pack ids remain protected by open_archive.
            tree_sha = _sha(window.archive_root/tree) if self.pack_table is not None else None
            archive = open_archive(window,seal_pins=self.pins,pack_table=self.pack_table,
                                   synthetic_plan_tree_sha256=tree_sha)
            self.archives[pack] = archive
            flags = archive.compare_runs_root()
            self.flags.extend(f['code'] for f in flags)
            # Capture the archive-owned input census, including all bytes the
            # child programs will reopen through their own authenticated handles.
            for name in archive.source_names():
                archive.source_bytes('sources/'+name)
            for name in archive.record['outputs']:
                archive.output_bytes(name)
            for name in ('withheld/member-assessments.json','withheld/neg8-rescreen-bracket.json','withheld/bracket-evaluation.json'):
                if (window.archive_root/name).is_file():archive.withheld_bytes(name)
            live = window.measurement_root/'runs/calibration_observation_ledger.jsonl'
            require_ledger_copies_are_prefixes([archive],live)
            self.ledger_rows.append({'window':pack,'path':'ledger/live/calibration_observation_ledger.jsonl',
                'sha256':_sha(live),'check':'ledger_prefix_of_live'})
            self.write('census_'+pack,'supply-census/'+pack+'.json',
                [{'path':r.path,'sha256':r.sha256,'check':r.check} for r in archive.census()])
        # Deliberately omit the numerical calibration_bracket/yield objects.
        for record in self.records:
            self.write('attempt_'+record.entry.plan_id,'attempts/'+record.entry.plan_id+'.json',
                {'pack':record.entry.pack,'plan_id':record.entry.plan_id,'attempt':record.entry.attempt,
                 'record_shape':record.record_shape,'verdict':record.verdict,'claim_usable':record.claim_usable,
                 'release_blocked':record.release_blocked,'window_reasons':record.window_reasons,
                 'flag_total':record.flag_total,'flags_by_family':record.flags_by_family,
                 'g10_codes':record.g10_codes,'unclassified_count':len(record.unclassified)})
        return 0

    def prepare_kept(self, argv):
        from joulewise.analysis_engine.inputs import planned_contrast_units
        from scripts.produce_b5_disclosures import _planned_floor
        from .kept_units import load_kept_units
        for pack,archive in self.archives.items():
            prefix='sources/repo/configs/campaigns/'+archive.window.pack_id+'/'
            name='analysis_manifest_v3.json' if pack=='gamma' else 'extraction_spec.json'
            raw=archive.source_bytes(prefix+name)
            local=self.repo_root/'configs/campaigns'/archive.window.pack_id/name
            if local.read_bytes()!=raw:
                raise AnalysisRefusal('extraction_spec_differs_from_archive' if pack!='gamma' else 'consumer_pack_differs_from_archive')
            document=json.loads(raw)
            if pack!='gamma': self.specs[pack]=document
            planned=planned_contrast_units(document) if pack=='gamma' else _planned_floor(document)
            self.kept[pack]=load_kept_units(archive,sealed_catalog_sha256=self.pins.sealed['catalog_sha256'],planned_units=planned)
        return 0

    def prepare_tripwires(self, argv):
        from joulewise.analysis_engine.inputs import archived_verdict_row
        from .context import TripwireRefusal
        # build_context needs a bracket but does not evaluate it. Step 3 supplies
        # the already authenticated stored assessment for its structural tripwires;
        # step 3b then evaluates and replaces every primary context.
        for pack,archive in self.archives.items():
            self.rows[pack]=archived_verdict_row(archive)
            bracket=self.rows[pack]['idle_admission_core']['instrument_calibration_bracket']
            try:
                self.contexts.update(primary_contexts({pack:archive},self.kept,{pack:bracket},self.rows,
                                                     synthetic=self.pack_table is not None))
            except TripwireRefusal as exc:
                record=exc.to_record()
                # The row writer's strict problem strings can quote data.
                # Retain their count; the public stop projection already
                # carries the closed bundle_strict_invalid code when present.
                problems=record.pop('problems',None)
                if problems is not None:record['problem_count']=len(problems)
                self.write('tripwire_'+pack,'tripwires/'+pack+'.json',record)
                raise
            self.write('kept_'+pack,'kept-units/'+pack+'.json',self.kept[pack].to_record())
        return 0

    def prepare_brackets(self, argv):
        from .bracket import evaluate_window_bracket, block_b_max_for_archives, b_sens
        self.brackets={p:evaluate_window_bracket(a,repo_root=self.repo_root) for p,a in self.archives.items()}
        self.b_max=block_b_max_for_archives(list(self.archives.values()))
        self.contexts=primary_contexts(self.archives,self.kept,self.brackets,self.rows,synthetic=self.pack_table is not None)
        for pack,bracket in self.brackets.items():
            self.write('bracket_'+pack,'brackets/'+pack+'.json',
                {'evaluation':bracket.evaluation,
                 'b_sens':b_sens(bracket,self.b_max)})
        self.write('b_max','brackets/block.json',self.b_max.__dict__)
        return 0

    def prepare_finalization(self, argv):
        from .bracket import LEDGER_COPY, TERMINAL_PIN, ledger_prefix
        archive=self.archives['gamma'];window=self.windows['gamma']
        prefix='sources/repo/configs/campaigns/'+window.pack_id+'/'
        # Preserve the entire sealed pack, including referenced config fileself.
        for name in archive.source_names():
            if name.startswith(prefix.removeprefix('sources/')):
                source='sources/'+name
                self.write('gamma_pack_'+name,'inputs/gamma-pack/'+name.removeprefix(prefix.removeprefix('sources/')),
                        raw=archive.source_bytes(source))
        prospective=self.restricted/'inputs/gamma-pack/analysis_manifest_v3.json'
        tree=self.restricted/'inputs/gamma-pack/plan_tree.json'
        self.write('gamma_verdict','inputs/gamma-verdict.json',self.rows['gamma'])
        self.write('gamma_binding','inputs/gamma-bracket-binding.json',raw=archive.output_bytes('derived/bracket-binding.json'))
        self.write('gamma_ledger','inputs/gamma-ledger.jsonl',raw=ledger_prefix(archive.source_bytes(LEDGER_COPY),
            json.loads(archive.output_bytes(TERMINAL_PIN))))
        return 0

    def kept_bundles(self):
        for pack in PACKS:
            ids=sorted({run for cid in self.kept[pack].cells for run in self.kept[pack].kept_run_ids(cid)})
            for run_id in ids: yield pack,run_id,self.windows[pack].claim_runs_root/run_id

    def evidence_roots(self):
        from scripts.produce_b5_disclosures import _evidence_roots
        artifact=self.read('floor_artifact')
        return _evidence_roots(artifact,{p:self.read('extraction_'+p) for p in ('alpha','beta')},self.windows)


def _internal_step(state, runner, step, operation, *, flags=()):
    before=set(state.outputs)
    result=runner.run(state.guarded(operation),[],step=step)
    outputs=[state.outputs[k] for k in state.outputs if k not in before]
    return [state.record(step,exit_status=result.exit_status,code=result.token() if result.exit_status else None,
                         outputs=outputs,flags=flags)]


def step_0(s,r):
    result=_internal_step(s,r,'0',s.prepare_initial,flags=('backup_roots_env_ignored',) if s.ignored_backup else ())
    if result[0].status=='ok':
        result=[replace(result[0],flags=tuple(sorted(set((*result[0].flags,*s.flags)))))]
    return result


def step_1(s,r):
    from joulewise.cli import main
    prepared=_internal_step(s,r,'1',s.prepare_kept)
    if prepared[0].status!='ok': return prepared
    for pack,run_id,bundle in s.kept_bundles():
        result,_,_,exit_status=s.invoke(r,main,['validate-bundle','--strict',bundle],step='1',window=pack)
        if exit_status:
            return [s.record('1',window=pack,exit_status=2,code='kept_bundle_strict_validation_failed')]
    return [s.record('1')]


def step_2(s,r):
    from joulewise.cli import main
    outputs=[]
    for pack,run_id,bundle in s.kept_bundles():
        output=s.path('rereduced/'+pack+'/'+run_id+'.rereduced.json')
        result,found,code,exit_status=s.invoke(r,main,['reduce',bundle,'--output',output],step='2',window=pack,
                                             outputs=[('rereduced_'+pack+'_'+run_id,output)])
        outputs.extend(found)
        if exit_status: return [s.record('2',window=pack,exit_status=exit_status,code=code,outputs=outputs)]
    return [s.record('2',outputs=outputs)]


def step_3(s,r): return _internal_step(s,r,'3',s.prepare_tripwires)


def step_3b(s,r): return _internal_step(s,r,'3b',s.prepare_brackets)


def step_4(s,r):
    from scripts.extract_detection_floors import main
    records=[]
    for pack in ('alpha','beta'):
        output=s.path('mint/extraction-'+pack+'.json')
        result,outputs,code,exit_status=s.invoke(r,main,['--window-index',s.index_path,'--pack',pack,'--out',output,
            '--hash-bundles'],step='4',window=pack,outputs=[('extraction_'+pack,output)])
        registered=None
        if outputs and not result.exception:
            classification=classify_step4_exit(exit_status,s.read('extraction_'+pack),s.specs[pack])
            if classification=='p42_floor_cells_only': code,registered=None,classification
            elif classification=='refused' and exit_status==0: exit_status=2
        records.append(s.record('4',window=pack,exit_status=exit_status,code=code,outputs=outputs,registered_exit=registered))
        if records[-1].status!='ok': break
    return records


def step_5(s,r):
    from scripts import emit_floor_mint_pinset as emit, mint_floor_artifact_generalized as mint
    directory=s.path('mint/floor-mint-pinset.json').parent
    expected=[('pinset',directory/'floor-mint-pinset.json'),('mint_inputs',directory/'floor-mint-inputs.json'),
              ('plan_alpha',directory/'alpha/calibration_plan.json'),('plan_beta',directory/'beta/calibration_plan.json')]
    result,outputs,code,exit_status=s.invoke(r,emit.main,['--window-index',s.index_path,
        '--alpha-report',s.output('extraction_alpha'),'--beta-report',s.output('extraction_beta'),
        '--out-dir',directory,'--project-commit',s.commit],step='5',outputs=expected)
    if exit_status:return [s.record('5',exit_status=exit_status,code=code,outputs=outputs)]
    s.rehash()
    floor,statement,sidecar=[s.path('mint/'+name) for name in ('aggregate-floor.json','single-count.md','dominance-replay.json')]
    result,found,code,exit_status=s.invoke(r,mint.main,['--window-index',s.index_path,'--pinset',s.output('pinset'),
        '--pinset-sha256',s.outputs['pinset']['sha256'],'--v2-input-manifest',s.output('mint_inputs'),
        '--out',floor,'--single-count-out',statement,'--d165-replay-out',sidecar,'--project-commit',s.commit,
        '--project-tree-state','clean'],step='5',outputs=[('floor_artifact',floor),('single_count',statement),('sidecar',sidecar)])
    return [s.record('5',exit_status=exit_status,code=code,outputs=outputs+found)]


def step_8(s,r):
    from scripts.finalize_analysis_manifest import main
    from joulewise.analysis_manifest_v3 import FINALIZED_BASENAME_SUFFIX
    before=set(s.outputs)
    staged=_internal_step(s,r,'8',s.prepare_finalization)
    if staged[0].status!='ok':return staged
    archive=s.archives['gamma'];window=s.windows['gamma']
    prospective=s.restricted/'inputs/gamma-pack/analysis_manifest_v3.json'
    tree=s.restricted/'inputs/gamma-pack/plan_tree.json'
    directory=s.restricted
    manifest=json.loads(prospective.read_bytes())
    output=directory/(manifest['manifest_id']+FINALIZED_BASENAME_SUFFIX)
    result,found,code,exit_status=s.invoke(r,main,['--window-index',s.index_path,'--prospective-manifest',prospective,
        '--plan-tree',tree,'--custody-root',s.restricted,'--runs-root',window.claim_runs_root,
        '--whole-window-verdict',s.output('gamma_verdict'),'--bracket-binding',s.output('gamma_binding'),
        '--calibration-ledger',s.output('gamma_ledger'),'--aggregate-floor-artifact',s.output('floor_artifact'),
        '--dominance-replay-sidecar',s.output('sidecar'),'--output-dir',directory],step='8',outputs=[('finalized_manifest',output)])
    if exit_status and not result.exception:
        try:
            message=json.loads(result.stdout_path.read_text().splitlines()[-1])
            if set(message)=={'status','reason','detail'} and message['status']=='REFUSE':
                code=refusal_token(message['reason'])
        except (ValueError,TypeError,KeyError,IndexError):pass
    # Finalization also writes a content-addressed exclusions attachment.
    for path in s.restricted.glob('analysed-attempt-exclusions-*.json'):
        s.register('finalized_exclusions',path)
    return [s.record('8',exit_status=exit_status,code=code,outputs=[s.outputs[k] for k in s.outputs if k not in before])]


def step_6(s,r):
    from scripts.run_d165_closeout_from_custody import main
    output=s.path('outputs/closeout.json');ratio=output.with_name(output.stem+'.ratio-table.json')
    result,outputs,code,exit_status=s.invoke(r,main,['--window-index',s.index_path,'--finalized-manifest',
        s.output('finalized_manifest'),'--custody-root',s.restricted,'--output',output],step='6',
        outputs=[('closeout',output),('ratio_table',ratio)])
    # This program emits a StepRecord JSON, not a bare refusal token.
    try:
        child=json.loads(result.stdout_path.read_text().splitlines()[-1])
        if child['status']=='outcome_class' and exit_status==3 and len(outputs)==2:
            code='dominance_ratio_zero_denominator'
        elif child['status']=='tooling_refusal': code=refusal_token(child['refusal'])
    except (ValueError,KeyError,TypeError,IndexError): pass
    if output.with_suffix('.step.json').is_file():
        outputs.append(s.register('closeout_step',output.with_suffix('.step.json')))
    return [s.record('6',exit_status=exit_status,code=code,outputs=outputs)]


def step_9(s,r):
    from joulewise.cli import main
    output=s.path('outputs/claim-verdicts.json')
    argv=['analyze-claims','--window-index',s.index_path,'--analysis-manifest',s.output('finalized_manifest'),
          '--runs-root',s.windows['gamma'].claim_runs_root,'--floor-artifact',s.output('floor_artifact'),
          '--neg8-harvest-archive',s.windows['gamma'].archive_root,'--output',output]
    for root_id,root in sorted(s.evidence_roots().items()):argv.extend(['--evidence-root',root_id+'='+str(root)])
    result,outputs,code,exit_status=s.invoke(r,main,argv,step='9',outputs=[('claim_verdicts',output)])
    return [s.record('9',exit_status=exit_status,code=code,outputs=outputs)]


def _custody_documents(s, *, pack, family, role, inputs, census_name):
    """Build production inventory/receipt bytes; the opener owns admission.

    Bind the role's registered files and tracked index anchor. Original bundles
    and archives are authenticated by the gate's indexed replay, not census rows.
    open_paper_input still owns the production admission and reopen checks.
    """
    from joulewise import paper_custody as c
    s.rehash()
    source_rows=[]
    for relative in (c._B5_WINDOW_INDEX_PATH,):
        path=s.repo_root/relative
        if path.is_file():
            source_rows.append({'base':'repository','path':relative,'authority':'git_blob','expected_sha256':_sha(path)})
    # The source validator's whole-module census supplies every code dependency
    # of the role; these files are read by the production validator itself.
    # Validator source digests are bound by the receipt's registered helper;
    # its callable census is not a filesystem inventory.

    source_rows=sorted({(row['base'],row['path']):row for row in source_rows}.values(),key=lambda row:(row['base'],row['path']))
    bindings=[]
    for input_role,path in sorted(inputs.items()):
        path=Path(path)
        try:
            relative=path.relative_to(s.restricted).as_posix();base='runs_root';authority='generated'
        except ValueError:
            relative=path.relative_to(s.repo_root).as_posix();base='repository';authority='git_blob'
        bindings.append({'role':input_role,'base':base,'path':relative,'authority':authority,'expected_sha256':_sha(path)})
    if family=='claim_evidence':
        acceptance={'schema_version':c._FLOOR_ACCEPTANCE_SCHEMA,'floor_sha256':s.outputs['floor_artifact']['sha256'],
            'sources':[{'path':row['base']+'/'+row['path'],'sha256':row['expected_sha256']} for row in source_rows],
            'binder_source_sha256':c._floor_binder_source_sha256(),'anchor_head':s.commit,'status':'PASS'}
        item=s.write('floor_acceptance','custody/claim-floor-acceptance.json',raw=c._canonical_json_bytes(acceptance),addressed=True)
        bindings.append({'role':'floor_acceptance','base':'runs_root','path':item['name'],
                         'authority':'generated','expected_sha256':item['sha256']})
    spec=next(spec for spec in c._FAMILY_SPECS.values() if spec.family==family)
    by_role={row['role']:row for row in bindings}
    bindings=[by_role[role.value] for role in spec.roles_for('production')]
    consumed=[*bindings,*[{'role':'authenticated_source',**row} for row in source_rows]]
    receipt={'schema_version':c._RECEIPT_SCHEMA,'family':family,'validator':'joulewise.paper_custody.'+family+'.v1',
        'validator_source_sha256':c._validator_source_sha256(family),'status':'PASS','replay_codes':[],
        'inputs':sorted([{'role':row['role'],'path':row['path'],'sha256':row['expected_sha256']} for row in consumed],
                        key=lambda row:(row['role'],row['path']))}
    item=s.write('receipt_'+pack,'custody/'+pack+'-receipt.json',raw=c._canonical_json_bytes(receipt),addressed=True)
    receipt_binding={'base':'runs_root','path':item['name'],'expected_sha256':item['sha256']}
    inventory={'schema_version':c._INVENTORY_SCHEMA,'family':family,'inventory_id':'b5-'+pack+'-'+family,
        'mode':'production','files':[{'role':row['role'],'path':row['path'],'authority':row['authority'],
                                    'sha256':row['expected_sha256']} for row in consumed]+[
            {'role':'validator_receipt','path':item['name'],'authority':'generated','sha256':item['sha256']}]}
    item=s.write('inventory_'+pack,'custody/'+pack+'-inventory.json',raw=c._canonical_json_bytes(inventory),addressed=True)
    s.write('role_census_'+pack,'supply-census/'+census_name+'.json',
        {'schema_version':'joulewise.paper_supply_census.v1','supply_role':role,'inputs':bindings,
         'source_census':source_rows,'inventory':{'base':'runs_root','path':item['name'],
                                               'expected_sha256':item['sha256']},'receipt':receipt_binding})


def _claim_open(s,argv):
    from joulewise import paper_custody as c
    from joulewise.analysis_engine.claim_side_bound import produce_claim_side_bound
    before=set(s.outputs)
    manifest,floor=s.read('finalized_manifest'),s.read('floor_artifact')
    raw=produce_claim_side_bound(s.output('claim_verdicts').read_bytes(),finalized_manifest=manifest,floor_artifact=floor)
    s.write('claim_side_bound','custody/claim-side-bound.json',raw=raw,addressed=True)
    owners={str(root):pack for pack,window in s.windows.items() for root in (window.claim_runs_root,)}
    request=c.claim_replay_request(claim_verdicts_sha256=s.outputs['claim_verdicts']['sha256'],
        analysis_manifest_sha256=s.outputs['finalized_manifest']['sha256'],floor_artifact_sha256=s.outputs['floor_artifact']['sha256'],
        window_index_sha256=s.index.sha256,evidence_roots={rid:owners[str(root)] for rid,root in s.evidence_roots().items()})
    s.write('claim_request','custody/claim-replay-request.json',raw=request,addressed=True)
    role='production.claim_evidence.gamma.v5'
    _custody_documents(s,pack='gamma',family='claim_evidence',role=role,census_name='claim-evidence-gamma',
        inputs={name:s.output(name) for name in ('claim_verdicts','claim_side_bound','finalized_manifest','floor_artifact')} |
               {'claim_replay_request':s.output('claim_request')})
    s.rehash()
    c.open_paper_input(c.ClaimEvidenceRef(role=role,runs_root=s.restricted))
    return 0


def step_9b(s,r):
    return _internal_step(s,r,'9b',lambda argv:_claim_open(s,argv))


def require_step10_admission(step4, projection, report):
    """Step 4 owns member gates; step 10 must use exactly its window binding."""
    binding=report.get('kept_units_binding',{})
    # The issuer calls its binding `window`; the extractor nests it in
    # kept_units_binding. Use their real, independently produced wire keys.
    actual={**projection.get('window',{}),'exclusions_sha256':projection.get('exclusions_sha256')}
    if (step4 is None or step4.status!='ok' or not binding or
            not binding.get('exclusions_sha256') or not binding.get('harvest_pin') or
            actual.get('exclusions_sha256')!=binding.get('exclusions_sha256') or
            actual.get('harvest_pin')!=binding.get('harvest_pin')):
        raise AnalysisRefusal('step10_window_not_admitted_by_step4')


def _reported_open(s,pack):
    from joulewise import paper_custody as c
    from joulewise.paper_rendering import _thaw
    prefix=s.repo_root/'configs/campaigns'/s.windows[pack].pack_id
    s.write('basis_'+pack,'custody/'+pack+'-whole-window-basis.json',s.rows[pack]['evaluation_basis'],addressed=True)
    role='production.reported_energy_parents.'+('qwen3-1p7b' if pack=='alpha' else 'qwen3-8b')+'.v5'
    inputs={'extraction_report':s.output('extraction_'+pack),'whole_window_basis':s.output('basis_'+pack)}
    for input_role,relative in (('extraction_spec','extraction_spec.json'),
                                ('g2a_selection','prefill_pin/selection.json'),
                                ('prompt_pin','prefill_pin/prefill_prompt_pin.json')):
        registered_role=input_role+'_'+pack
        s.write(registered_role,'custody/registered-inputs/'+pack+'/'+input_role+'/input.json',
                raw=(prefix/relative).read_bytes(),addressed=True)
        inputs[input_role]=s.output(registered_role)
    _custody_documents(s,pack=pack,family='reported_energy_parents',role=role,census_name='reported-energy-'+pack,
        inputs=inputs)
    s.rehash()
    opened=c.open_paper_input(c.ReportedEnergyParentsRef(role=role,runs_root=s.restricted))
    if _thaw(opened.reported_energy_projection)!=s.read('projection_'+pack):
        raise AnalysisRefusal('reported_energy_projection_replay_mismatch')
    return 0


def step_10(s,r):
    from scripts.issue_reported_energy import main
    records=[]
    for pack in ('alpha','beta'):
        output=s.path('outputs/projection-'+pack+'.json')
        result,outputs,code,exit_status=s.invoke(r,main,['--window-index',s.index_path,'--pack',pack,'--output',output],
            step='10',window=pack,outputs=[('projection_'+pack,output)])
        if exit_status==0:
            step4=next((record for record in s.step_records if record.step=='4' and record.window==pack),None)
            require_step10_admission(step4,s.read('projection_'+pack),s.read('extraction_'+pack))
            before=set(s.outputs)
            result=r.run(s.guarded(lambda argv:_reported_open(s,pack)),[],step='10',window=pack)
            exit_status=result.exit_status;code=result.token() if exit_status else None
            outputs.extend(s.outputs[k] for k in s.outputs if k not in before)
        records.append(s.record('10',window=pack,exit_status=exit_status,code=code,outputs=outputs))
        if records[-1].status!='ok':break
    return records


def _step_results(s):
    from .context import rebuilt_roster, survivor_set
    from joulewise.flags.catalog import load_catalog
    catalog=load_catalog(s.repo_root/'configs/campaigns/v5_claim_25g83/flag_catalog.json')
    result={'windows':{},'no_analysed_window_harvested_twice':not any(
        window.record.entry.superseded_archive_roots for window in s.windows.values())}
    for pack,window in s.windows.items():
        row=s.rows[pack];core=row['idle_admission_core'];context=s.contexts[pack]
        roster=rebuilt_roster(s.archives[pack],row)
        survivors=survivor_set(s.archives[pack],row,roster)
        spares={member['run_id'] for member in roster['members'] if member.get('spare_slot') in ('start','midpoint','end')}
        from .context import _excluded
        excluded_codes=_excluded(s.archives[pack])
        reasons=[]
        grouped={}
        dropped={run:unit for cell in s.kept[pack].cells.values() for unit in cell.dropped for run in unit.run_ids}
        for failure in core.get('member_failures',row.get('member_failures',[])):
            code=failure.get('reason_code');run=failure.get('member_id',failure.get('bundle_id'));grouped.setdefault(code,[]).append(run)
        for reason,ids in sorted(grouped.items()):
            units=[dropped[bid] for bid in ids if bid in dropped]
            codes={code for bid in ids for code in excluded_codes.get(bid,())}
            reasons.append({'reason':reason,'count':len(ids),'all_removed':all(bid in context.removed_bundle_ids for bid in ids),
                'families':sorted({catalog.entry(code)['family'] for code in codes}),
                'codes':sorted(codes)})
        # The owning validator decides which conditions were answered. Copy
        # that result; the driver does not apply a second admission policy.
        from joulewise.whole_window import (AuthenticatedConsumptionSession,
            MAX_BRACKET_CONSUMPTION_SEMANTICS_ID, validate_whole_window_verdict_row)
        from joulewise.analysis_engine.inputs import archive_snapshot
        ids={run for cid in s.kept[pack].cells for run in s.kept[pack].kept_run_ids(cid)}
        require_primary_context(context)
        session=AuthenticatedConsumptionSession(window.claim_runs_root,ids,mode='read_replay',
            evaluation_basis_sha256=row['evaluation_basis']['sha256'],
            consumption_semantics_id=MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
            calibration_ledger_snapshot=archive_snapshot(context),archive_context=context)
        validation=validate_whole_window_verdict_row(row,window.claim_runs_root,ids,
            consumption_session=session,archive_context=context)
        if not validation.admitted:
            raise AnalysisRefusal(validation.reasons[0] if validation.reasons else 'whole_window_verdict_provenance_invalid')
        conditions=[]
        for condition in core.get('conditions',[]):
            if condition not in validation.answered_conditions:
                raise AnalysisRefusal('whole_window_verdict_provenance_invalid')
            if condition.startswith('neg8_'):answered='neg8_allowance'
            elif condition=='calibration_acceptance_bound_stale':answered='window_bracket'
            elif condition=='whole_window_campaign_membership_unresolved':answered='sources_replay'
            elif condition in (core.get('adapter_wattage_continuity') or {}).get('conditions',[]):answered='adapter_continuity'
            else:answered='member_exclusions'
            conditions.append({'condition':condition,'answered_by':answered})
        excluded=row.get('excluded_bundles',[])
        excluded_ids=[item.get('bundle_id') if isinstance(item,dict) else item for item in excluded]
        families={}
        for bid in excluded_ids:
            member_families={catalog.entry(code)['family'] for code in excluded_codes.get(bid,())}
            for family in member_families:
                families[family]=families.get(family,0)+1
        result['windows'][pack]={'stored_verdict':{'status':row['status'],'conditions':conditions},
            'member_reasons':reasons,'adapter_continuity':(core.get('adapter_wattage_continuity') or {}).get('decision','not_applicable'),
            'tripwires':{'excluded_reference_in_screen':'clear','kept_member_outside_verdict_membership':'clear'},
            'deciding_references':len(survivors.bundle_ids-spares),
            'deciding_spares':len(survivors.bundle_ids & spares),'writer_excluded_count':len(excluded_ids),
            'writer_excluded_by_family':families,'writer_excluded_all_removed':all(bid in context.removed_bundle_ids for bid in excluded_ids),
            # build_context installs this callback only after replay_claim_sources
            # returns without a problem; the validator above must also admit it.
            'reference_parity':'passed' if context.sources_replay is not None else 'not_applicable',
            'ledger_prefix_test':'passed'}
    if not result['no_analysed_window_harvested_twice']:
        # No invented before/after survivor counts. A forced re-harvest needs
        # its director-owned deciding record, absent from today's index schema.
        raise AnalysisRefusal('reharvest_disclosure_record_required')
    return result


def _sensitivity(s,argv):
    from .sensitivity import sensitivity_pass
    from .bracket import BMax
    from joulewise.cli import validate_bundle
    kwargs={'extraction_specs':s.specs,'primary_projections':{p:s.read('projection_'+p) for p in ('alpha','beta')},
        'primary_extraction_reports':{p:s.read('extraction_'+p) for p in ('alpha','beta')},
        'floor_artifact':s.read('floor_artifact'),'floor_artifact_path':s.output('floor_artifact'),
        'gamma_manifest_path':s.output('finalized_manifest'),'primary_claim_verdicts':s.read('claim_verdicts'),
        'evidence_roots':s.evidence_roots(),'strict_validator':validate_bundle,'gamma_archive':s.archives['gamma']}
    # The merged pass accepts PRIMARY contexts and owns construction of fresh
    # wider contexts internally. Our separated seam hands it primary copies;
    # no sensitivity copy is ever handed to a registered writer.
    contexts=sensitivity_contexts(s.contexts,{pack:None for pack in PACKS})
    sensitivity_pass(s.windows,s.kept,contexts,s.brackets,BMax(0.0,None,s.b_max.T),**kwargs)
    record=sensitivity_pass(s.windows,s.kept,contexts,s.brackets,s.b_max,**kwargs)
    s.write('sensitivity','outputs/sensitivity.json',record,addressed=True)
    s.write('step_results','outputs/step-results.json',_step_results(s),addressed=True)
    return 0


def step_11(s,r):
    from scripts import produce_b5_disclosures as disclosures, build_results_fill_input as fill, render_results_fills as render
    before=set(s.outputs)
    records=_internal_step(s,r,'11',lambda argv:_sensitivity(s,argv))
    if records[0].status!='ok':return records
    roles=disclosures.ROLES
    s.write('step_outputs','outputs/step-outputs.json',
        {role:{'path':s.outputs[role]['name'],'sha256':s.outputs[role]['sha256']} for role in roles},addressed=True)
    result,_,code,exit_status=s.invoke(r,disclosures.main,['--window-index',s.index_path,'--custody',s.restricted,
        '--step-outputs',s.output('step_outputs')],step='11')
    if exit_status==0:
        files=sorted((s.restricted/'disclosures').glob('*'))
        for path in files:
            role='disclosure_record' if path.suffix=='.json' else 'disclosure_released' if path.name.endswith('.released.txt') else 'disclosure_unreleased'
            s.register(role,path)
        if len(files)!=3:exit_status,code=2,None
    if exit_status==0:
        s.rehash();output=s.path('outputs/results-fill-input.json')
        result,_,code,exit_status=s.invoke(r,fill.main,['--window-index',s.index_path,'--custody-root',s.restricted,
            '--finalized-manifest',s.output('finalized_manifest'),'--claim-verdicts',s.output('claim_verdicts'),
            '--out',output],step='11',outputs=[('fill_input',output)])
    if exit_status==0:
        s.rehash();output=s.path('outputs/results-fills.md')
        result,_,code,exit_status=s.invoke(r,render.main,[s.output('fill_input')],step='11',
            stdout_path=output,outputs=[('rendered_fills',output)])
    if exit_status==0:
        s.rehash()
        result,_,code,exit_status=s.invoke(r,render.main,['--validate-rendered',s.output('rendered_fills')],step='11')
    return [s.record('11',exit_status=exit_status,code=code,
                     outputs=[s.outputs[k] for k in s.outputs if k not in before])]


STEPS = (('0',step_0),('1',step_1),('2',step_2),('3',step_3),('3b',step_3b),('4',step_4),
         ('5',step_5),('8',step_8),('6',step_6),('9',step_9),('9b',step_9b),('10',step_10),('11',step_11))


def _record_parts(s):
    selected={w.plan_id for w in s.windows.values()}
    attempts=[{'pack':r.entry.pack,'seal':r.entry.seal,'attempt':r.entry.attempt,'plan_id':r.entry.plan_id,
        'record_shape':r.record_shape,'verdict':r.verdict,'claim_usable':r.claim_usable,'analysed':r.entry.plan_id in selected}
        for r in s.records]
    windows=[{'pack':pack,'plan_id':w.plan_id,'harvest_record_sha256':w.harvest_record_sha256,'harvest_pin':w.harvest_pin,
        'kept_counts':{cid:{'n_r':cell.n_r,'n_b':cell.n_b} for cid,cell in s.kept[pack].cells.items()} if pack in s.kept else {}}
        for pack,w in sorted(s.windows.items())]
    census={}
    # Include every attempt's authenticated structural reads, with a plan-owned
    # archive-relative prefix for history-only attempts of the same pack.
    for r in s.records:
        for row in r.census:
            name=row.path if r.entry.plan_id in selected else 'sources/attempts/'+r.entry.plan_id+'/'+row.path
            item={'window':r.entry.pack,'path':name,'sha256':row.sha256,'check':row.check}
            census[(item['window'],item['path'])]=item
    for pack,archive in s.archives.items():
        for row in archive.census():
            item={'window':pack,'path':row.path,'sha256':row.sha256,'check':row.check}
            census[(pack,row.path)]=item
    for item in s.ledger_rows:census[(item['window'],item['path'])]=item
    return attempts,windows,[census[k] for k in sorted(census)]


def _released_input_difference(s, previous):
    """Detect a changed indexed input before authentication itself refuses."""
    by_pack={e.pack:e for e in s.index.entries if any(w['plan_id']==e.plan_id for w in previous['windows'])}
    history={e.plan_id:e for e in s.index.entries}
    current=[]
    for row in previous['input_census']:
        entry=by_pack.get(row['window'])
        if entry is None:continue
        relative=row['path']
        if relative=='binding/plan_tree':
            current.append(dict(row));continue
        if relative.startswith('sources/attempts/'):
            _,_,plan,*parts=relative.split('/');entry=history.get(plan);relative='/'.join(parts)
            if entry is None:continue
        if relative.startswith('original/claim-runs/'):
            path=entry.claim_runs_root/relative.removeprefix('original/claim-runs/')
        elif relative=='ledger/live/calibration_observation_ledger.jsonl':
            path=entry.measurement_root/'runs/calibration_observation_ledger.jsonl'
        else:path=entry.archive_root/relative
        try:actual=_sha(path)
        except OSError:actual=None
        current.append({**row,'sha256':actual})
    return release_difference({'input_census':previous['input_census'],'steps':[]},
                              {'input_census':current,'steps':[]})


def _index_digest(path):
    try:return _sha(path)
    except OSError:return '0'*64


def run(mode,index,custody,*,_test_pack_table=None,_test_seal_pins=None,_test_repo_root=None,_runner=None,_git=None):
    """Run all registered steps. Return 0, 3 (registered outcome), or 2.

    The only public outputs are the closed record and two structure streams.
    The Python-only seams never appear as command-line options.
    """
    repo_root=Path(_test_repo_root) if _test_repo_root is not None else ROOT
    try:
        directory=custody_preflight(mode,custody,repo_root)
    except (AnalysisRefusal,OSError,RuntimeError):
        # An invalid root cannot safely receive a record. Its closed refusal is
        # exposed only as the same structure step line; no exception text leaks.
        print('step 0 - tooling_refusal',file=sys.stderr)
        return 2
    checkout_code=None;checkout_failed=False
    try:
        commit=(_git or analysis_checkout)(repo_root)
    except AnalysisRefusal as exc:
        checkout_code=refusal_token(exc.code);checkout_failed=True
        # Retain a readable HEAD even when its tracked checkout was dirty.
        # A zero pin marks an unavailable HEAD on a refused preflight only.
        commit=getattr(exc,'analysis_commit','0'*40)
    except Exception:
        checkout_failed=True;commit='0'*40
    try:
        directory.mkdir(parents=True)
        restricted=directory/'restricted';restricted.mkdir()
    except OSError:
        print('step 0 - tooling_refusal',file=sys.stderr)
        return 2
    runner=_runner(restricted) if _runner is not None else StepRunner(restricted)
    s=RunState(mode,index,restricted,commit,pack_table=_test_pack_table,seal_pins=_test_seal_pins,repo_root=repo_root)
    stopped=False;difference=None;previous=None
    with without_backup_roots() as ignored:
        s.ignored_backup=ignored
        if mode=='release':
            from .windows import load_window_index
            try:
                previous=json.loads((Path(custody)/'dry-run/B5-BLIND-DRY-RUN-RECORD.json').read_bytes())
                s.index=load_window_index(Path(index),seal_pins=s.pins,pack_table=s.pack_table)
                from types import SimpleNamespace
                old_root=Path(custody)/'dry-run/restricted'
                trusted_kept={}
                for row in previous['steps']:
                    if row['step']=='3':
                        require_step_inputs(old_root,row['outputs'])
                        for item in row['outputs']:
                            if item['name'].startswith('kept-units/'):
                                kept_record=json.loads((old_root/item['name']).read_bytes())
                                trusted_kept[kept_record['pack']]=SimpleNamespace(cells=kept_record['cells'])
                validate_dry_run_record(previous,index=s.index,kept_units=trusted_kept)
                difference=_released_input_difference(s,previous)
                if difference is None and previous['analysis_commit']!=commit:
                    difference={'path':'binding/analysis_commit'}
                if difference is None and previous['window_index_sha256']!=s.index.sha256:
                    difference={'path':'binding/window_index'}
            except (AnalysisRefusal,OSError,ValueError,TypeError,KeyError):
                previous=None
        for step,function in STEPS:
            if stopped:
                records=[StepRecord(step,None,'not_run')]
            elif step=='0' and checkout_failed:
                records=[s.record('0',exit_status=2,code=checkout_code)]
            elif mode=='release' and step=='0' and (previous is None or difference is not None):
                records=[s.record('0',exit_status=2,code='release_digest_differs_from_dry_run' if difference else 'dry_run_record_missing_or_incomplete')]
            else:
                try:
                    before=set(s.outputs)
                    s.rehash()
                    records=function(s,runner)
                except AnalysisRefusal as exc:
                    records=[s.record(step,exit_status=2,code=refusal_token(exc.code),
                        outputs=[s.outputs[k] for k in s.outputs if k not in before])]
                except Exception:
                    # Exception diagnostics belong only to restricted custody.
                    def fail(argv):
                        traceback.print_exc();return 2
                    runner.run(fail,[],step=step)
                    records=[s.record(step,exit_status=2,outputs=[s.outputs[k] for k in s.outputs if k not in before])]
            for record in records:
                s.step_records.append(record)
                if record.step!='11':
                    print('step '+record.step+' '+(record.window or '-')+' '+record.status,file=sys.stderr)
            if any(record.status!='ok' for record in records):stopped=True
        attempts,windows,census=_record_parts(s)
        sealed={key:s.pins.sealed[{'flag_catalog_sha256':'catalog_sha256'}.get(key,key)] for key in SEAL_KEYS}
        record=build_dry_run_record(mode=mode,analysis_commit=commit,window_index_sha256=s.index.sha256 if s.index else _index_digest(index),
            sealed=sealed,attempts=attempts,windows=windows,input_census=census,steps=s.step_records,difference=difference)
        if mode=='release' and previous is not None and difference is None:
            difference=release_difference(previous,record)
            if difference is None and (previous['analysis_commit']!=commit or previous['window_index_sha256']!=record['window_index_sha256']):
                difference={'path':'binding/plan_tree'}
            if difference is not None:
                record['release_difference']=difference
                # Comparison is a step-11 tooling refusal, including a prior
                # registered outcome; no extra unregistered step id is emitted.
                record['steps'][-1]=s.record('11',exit_status=2,code='release_digest_differs_from_dry_run',
                    outputs=record['steps'][-1]['outputs']).as_dict()
                record['completed_without_tooling_refusal']=False
        validate_dry_run_record(record,index=s.index,kept_units=s.kept)
        output=directory/('B5-BLIND-DRY-RUN-RECORD.json' if mode=='blind-dry-run' else 'B5-RELEASE-RECORD.json')
        with output.open('xb') as out:out.write(_canonical(record))
        last=record['steps'][-1]
        print('step 11 '+(last['window'] or '-')+' '+last['status'],file=sys.stderr)
    print(str(output)+' '+_sha(output))
    if not record['completed_without_tooling_refusal']:return 2
    return 3 if any(row['status']=='outcome_class' for row in record['steps']) else 0
