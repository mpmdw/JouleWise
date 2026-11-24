"""Private synthetic export and commitment fixtures for the real BYTES CLIs."""
import contextlib
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PIN = '18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71'
ORIGIN_REF = 'refs/remotes/origin/records/2026-11-bytes-stage1'
REMOTE_REF = 'refs/heads/records/2026-11-bytes-stage1'
_admission_fixtures = None


def copy_cli_checkout(destination):
    """Copy the executable modules and their registered inputs into an isolated checkout."""
    shutil.copytree(ROOT / 'joulewise', destination / 'joulewise')
    shutil.copytree(ROOT / 'configs/bytes', destination / 'configs/bytes')
    shutil.copytree(ROOT / 'configs/campaign_policies', destination / 'configs/campaign_policies')
    scripts = destination / 'scripts'
    scripts.mkdir()
    for name in ('bytes_analyze.py', 'bytes_twin.py', 'bytes_commitment.py'):
        shutil.copyfile(ROOT / 'scripts' / name, scripts / name)


class SyntheticExport:
    """Give a synthetic export layout a private Git capture and fit release."""

    def __init__(self, manifest, exports, *, checkout=ROOT, tag=''):
        from joulewise.b6 import bytes_integrity

        self.integrity = bytes_integrity
        self.manifest = Path(manifest).resolve()
        self.root = self.manifest.parent
        self.exports = sorted({Path(path).resolve() for path in exports})
        self.checkout = Path(checkout).resolve()
        self.campaign = json.loads(self.manifest.read_text())
        archives = [Path(session['archive']).resolve() for session in self.campaign['sessions']]
        if (self.campaign.get('synthetic') is not True
                or any(not path.is_relative_to(self.root) for path in [*self.exports, *archives])):
            raise ValueError('synthetic BYTES fixture requires a generated export')
        identity = hashlib.sha256(os.fsencode(str((self.checkout, self.exports, tag)))).hexdigest()[:20]
        self.work = self.root / '.bytes-seal-fixtures' / identity
        self.repo = self.work / 'git'
        self.private = self.root / 'private-keys'
        self.fit_names = {'pack.json', bytes_integrity._key_name('neg8_reference')}
        self.fit_names.update(bytes_integrity._key_name(model['config_key'])
                              for model in self.campaign['models'] if model['role'] == 'fit')
        if not (self.repo / bytes_integrity.NAME).exists():
            self.capture()

    def capture(self):
        # The registration/policy paths in an isolated mutant must resolve to
        # its checkout. Every subprocess still runs the unmodified verifier.
        with mock.patch.object(self.integrity, 'ROOT', self.checkout):
            sidecars = [p for directory in self.exports for p in directory.rglob('*.session.json')]
            if sidecars and all(json.loads(path.read_text())['blinding'].get('group') == 'bytes'
                                for path in sidecars):
                self.integrity.capture(self.repo, self.manifest, self.exports, self.private)
            else:
                self.capture_legacy(sidecars)

    def capture_legacy(self, sidecars):
        """Seal deliberately unsplit synthetic controls used by the agreement tests."""
        # First derive the archive census from a fit-only projection through
        # the production capture. Then bind the actual legacy tables that
        # the compatibility cases exercise, leaving that census intact.
        fit_cells = {cell for model in self.campaign['models'] if model['role'] == 'fit'
                     for cell in model['cell_ids']}
        private = self.work / 'legacy-records'
        bindings = private / 'bytes/blinding-sessions'
        bindings.mkdir(parents=True)
        projection = self.work / 'legacy-fit-visible'
        projection.mkdir()
        source = self.private / 'bytes/blinding'
        digests = {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in self.fit_names}
        for path in sidecars:
            session = path.name.removesuffix('.session.json')
            (bindings / (session + '.json')).write_text(json.dumps({'session_id': session, 'key_sha256': digests}))
            sidecar = json.loads(path.read_text())
            sidecar['blinding']['key_sha256'] = digests
            (projection / path.name).write_text(json.dumps(sidecar))
            table_name = session + '.runs.csv'
            with path.with_name(table_name).open(newline='') as stream, (projection / table_name).open('w', newline='') as out:
                rows = csv.DictReader(stream)
                writer = csv.DictWriter(out, rows.fieldnames)
                writer.writeheader()
                writer.writerows(row for row in rows if row['role'] in self.integrity.REFERENCE_ROLES
                                 or set(row['cell_ids'].split(';')) <= fit_cells)
        commit = self.integrity.capture(self.repo, self.manifest, [projection], private)
        document = self.integrity.verify(self.repo, commit, phase='captured')
        tables = {f'tables:{index}': self.integrity._root(path, 'tables')
                  for index, path in enumerate(self.exports)}
        old_roots = {name for name, scope in document['roots'].items() if scope['kind'] == 'tables'}
        members = self.integrity._membership(tables)
        document['roots'] = {**{name: scope for name, scope in document['roots'].items() if name not in old_roots}, **tables}
        entries = [row for row in document['files'] if row['root'] not in old_roots]
        document['files'] = sorted(entries + self.integrity._entries(members), key=lambda row: (row['root'], row['path']))
        document['table_files'] = sorted(str(path) for path in members.values() if path.name.endswith('.runs.csv'))
        self.integrity._publish(self.repo, document)

    def captured(self):
        document = json.loads((self.repo / self.integrity.NAME).read_bytes())
        # The working manifest follows the latest phase. Each CLI consumes
        # one phase at the same point as the desk's workflow.
        if document['phase'] != 'captured':
            raise ValueError('synthetic export has already released fit keys')
        return self.integrity.options(self.repo, git(self.repo, 'rev-parse', 'HEAD'))

    def finalized(self, key_dir=None):
        document = json.loads((self.repo / self.integrity.NAME).read_bytes())
        commit = git(self.repo, 'rev-parse', 'HEAD')
        if document['phase'] == 'finalized':
            return self.integrity.options(self.repo, commit), Path(document['roots']['release']['path'])
        if key_dir is None:
            raise ValueError('synthetic export needs a fit release before admission')
        key_dir = Path(key_dir)
        allowed = self.fit_names | {'release.json'}
        if {path.name for path in key_dir.iterdir()} - allowed:
            # Older fixtures release all generated keys. Stage a private fit
            # subset without changing their stage-2 key location.
            subset = self.work / 'fit-release'
            subset.mkdir()
            for name in sorted(self.fit_names):
                shutil.copyfile(key_dir / name, subset / name)
            key_dir = subset
        with mock.patch.object(self.integrity, 'ROOT', self.checkout):
            commit = self.integrity.finalize(self.repo, commit, key_dir)
        return self.integrity.options(self.repo, commit), key_dir


def empty_synthetic_export(root):
    """Publish a valid empty session for tests of CLI error reporting."""
    from joulewise.b6 import bytes_integrity

    manifest = root / 'manifest.json'
    exports = root / 'export'
    if manifest.exists():
        return SyntheticExport(manifest, [exports])
    archive = root / 'archive'
    (archive / 'derived').mkdir(parents=True)
    roster = archive / 'derived/roster.json'
    roster.write_text('{"members": []}\n')
    (archive / 'harvest.json').write_text(json.dumps({
        'outputs': {'derived/roster.json': hashlib.sha256(roster.read_bytes()).hexdigest()}}))
    exports.mkdir()
    manifest.write_text(json.dumps({'synthetic': True, 'models': [],
                                    'sessions': [{'session_id': 'synthetic', 'archive': str(archive)}]}))
    binding = root / 'private-keys/bytes/blinding-sessions'
    binding.mkdir(parents=True)
    digests = {name: hashlib.sha256(b'{}\n').hexdigest()
               for name in ('pack.json', bytes_integrity._key_name('neg8_reference'))}
    keys = root / 'fit-keys'
    keys.mkdir()
    for name in digests:
        (keys / name).write_bytes(b'{}\n')
    (binding / 'synthetic.json').write_text(json.dumps({'session_id': 'synthetic', 'key_sha256': digests}))
    (exports / 'synthetic.session.json').write_text(json.dumps({'blinding': {'group': 'bytes', 'key_sha256': digests}}))
    (exports / 'synthetic.runs.csv').write_text('run_id,role,cell_ids\n')
    return SyntheticExport(manifest, [exports])


def activity_json(commit):
    """Recorded synthetic GitHub response shape; no request is sent."""
    return json.dumps([{'id': 123, 'ref': REMOTE_REF, 'activity_type': 'push',
                        'timestamp': '2026-11-01T10:01:00+00:00', 'after': commit,
                        'force_push': False}], indent=2) + '\n'


def git(repo, *args, date='2026-11-01T10:00:00+00:00'):
    env = {**os.environ, 'GIT_AUTHOR_DATE': date, 'GIT_COMMITTER_DATE': date,
           'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
           'GIT_TERMINAL_PROMPT': '0', 'GIT_NO_LAZY_FETCH': '1'}
    return subprocess.check_output(['git', '-c', 'user.name=BYTES Synthetic', '-c',
                                    'user.email=synthetic@example.invalid', *args],
                                   cwd=repo, env=env, stderr=subprocess.PIPE).decode().strip()


def commitment_fixture(root, predictions=None):
    repo = Path(root) / 'commitment-repo'
    repo.mkdir()
    # Imported here: this module also runs as a script (--run-cli) before tests/ is importable.
    from tests.git_fixture import init_git_fixture
    init_git_fixture(repo, '-q')
    git(repo, 'config', 'user.name', 'BYTES Synthetic')
    git(repo, 'config', 'user.email', 'synthetic@example.invalid')
    git(repo, 'remote', 'add', 'origin', 'https://github.com/synthetic/bytes.git')
    metadata = repo / 'docs/bytes/stage1'
    metadata.mkdir(parents=True)
    path = metadata / 'predictions.json'
    path.write_bytes(Path(predictions).read_bytes() if predictions else json.dumps({'bytes_analysis_sha256': PIN}).encode())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    path.with_suffix('.sha256').write_text(digest + '\n')
    estimator = repo / 'joulewise/bytes_analysis.py'
    estimator.parent.mkdir()
    estimator.write_bytes((ROOT / 'joulewise/bytes_analysis.py').read_bytes())
    (metadata / 'unblinding.jsonl').write_text('')
    git(repo, 'add', '.')
    git(repo, 'commit', '-qm', 'Synthetic prediction commitment')
    commit = git(repo, 'rev-parse', 'HEAD')
    git(repo, 'update-ref', ORIGIN_REF, commit)
    receipt = metadata / 'push-receipt.json'
    receipt.write_text(json.dumps({'schema': 'joulewise.bytes_push_receipt.v1', 'stage1_commit': commit,
                                  'predictions_path': 'docs/bytes/stage1/predictions.json',
                                  'origin_ref': ORIGIN_REF, 'origin_tip': commit,
                                  'github_activity_raw': activity_json(commit), 'force_push': False,
                                  'github_repository': 'synthetic/bytes',
                                  'pushed_utc': '2026-11-01T10:01:00+00:00'}) + '\n')
    return repo, path, receipt, commit


def commitment_args(repo, predictions, receipt, commit):
    return ['--commitment-repo', str(repo), '--predictions', str(predictions),
            '--stage1-receipt', str(receipt), '--stage1-commit', commit]


def fixture_options(root, predictions=None):
    """Persist fixture evidence, then run the production verifier afresh on every use."""
    global _admission_fixtures
    root = Path(root).resolve()
    admission_only = not (root / 'manifest.json').exists()
    if admission_only:
        # Reader fixtures can copy their entire input world. Keep the
        # checkout and its absolute seal bindings outside that copied tree.
        if _admission_fixtures is None:
            _admission_fixtures = tempfile.TemporaryDirectory(prefix='bytes-admission-fixtures-')
        world = hashlib.sha256(os.fsencode(root)).hexdigest()[:20]
        root = Path(_admission_fixtures.name).resolve() / world
    raw = Path(predictions).read_bytes() if predictions is not None else b'synthetic-provenance'
    directory = root / ('synthetic-commitment-' + hashlib.sha256(raw).hexdigest()[:16])
    repo = directory / 'commitment-repo'
    if not repo.exists():
        directory.mkdir(parents=True)
        repo, path, receipt, commit = commitment_fixture(directory, predictions)
    else:
        receipt = repo / 'docs/bytes/stage1/push-receipt.json'
        commit = json.loads(receipt.read_text())['stage1_commit']
        path = repo / 'docs/bytes/stage1/predictions.json'
    seal = []
    if admission_only:
        # Admission-only tests still verify an actual private export commit.
        export = root / 'export-fixture'
        seal, _ = empty_synthetic_export(export).finalized(export / 'fit-keys')
    return [*seal, *commitment_args(repo, path, receipt, commit)]


def commit_journal(repo):
    """Synthetic operator's local durability step between held-out fixture commands."""
    name = 'docs/bytes/stage1/unblinding.jsonl'
    if git(repo, 'status', '--porcelain', '--', name):
        git(repo, 'add', '--', name)
        git(repo, 'commit', '--only', '-qm', 'Synthetic admission journal', '--', name)


def _seal_cli(script, argv, tag):
    if '--export-seal-repo' in argv or '--manifest' not in argv:
        return argv
    manifest = Path(argv[argv.index('--manifest') + 1])
    if script.name == 'bytes_twin.py':
        exports = [argv[argv.index('--export-dir') + 1]]
    else:
        start = argv.index('--export') + 1
        end = next((i for i in range(start, len(argv)) if argv[i].startswith('--')), len(argv))
        exports = argv[start:end]
    desk = SyntheticExport(manifest, exports, checkout=script.resolve().parents[1], tag=tag)
    stage = argv[argv.index('--stage') + 1]
    key_index = argv.index('--key-dir') + 1 if '--key-dir' in argv else None
    key_dir = Path(argv[key_index]) if key_index is not None else desk.root / 'released-keys/bytes/blinding'

    if stage == 'blinded' and '--stage1-commit' not in argv:
        return [*argv, *desk.captured()]
    if stage in {'fit', '1'} and key_dir.is_dir() and not any(key_dir.iterdir()):
        if key_index is None:
            argv += ['--key-dir', str(key_dir)]
        return [*argv, *desk.captured(), '--no-key-probe']
    options, released = desk.finalized(key_dir)
    if stage in {'fit', '1', 'all'}:
        if key_index is not None:
            argv[key_index] = str(released)
        else:
            argv += ['--key-dir', str(released)]
    elif stage == 'heldout' and key_index is None:
        argv += ['--key-dir', str(key_dir)]
    return [*argv, *options]


def synthetic_cli_args(script, arguments, *, seal_tag=''):
    """Prepare an in-process CLI invocation with the same private export fixture."""
    return _seal_cli(ROOT / 'scripts' / script, list(map(str, arguments)), seal_tag)


def commitment_command(command, *, seal_tag=''):
    """Patch ROOT only in test processes, never add a production bypass for R-04."""
    args = list(map(str, command))
    if '-c' in args:
        return args
    script = next((i for i, a in enumerate(args) if a.endswith('.py')), None)
    if script is None:
        return args
    path = Path(args[script])
    if path.name in {'bytes_analyze.py', 'bytes_twin.py'}:
        args[script + 1:] = _seal_cli(path, args[script + 1:], seal_tag)
    if '--commitment-repo' not in args:
        return args
    if path.name in {'b6_release_subset.py', 'b6_unblind.py'} and '--export-seal-repo' not in args:
        repo = Path(args[args.index('--commitment-repo') + 1])
        root = repo.parent.parent
        desk = SyntheticExport(root / 'manifest.json', [root / 'export'], checkout=path.resolve().parents[1])
        options, _ = desk.finalized()
        args += options
    return [*args[:script], str(Path(__file__).resolve()), '--run-cli', *args[script:]]


@contextlib.contextmanager
def synthetic_checkout(options):
    """Bind the loaded guard to a temporary repo; emulate committing after each command."""
    from scripts import bytes_commitment as bc
    args = list(map(str, options))
    with contextlib.ExitStack() as stack:
        if '--commitment-repo' not in args:
            yield
            return
        repo = Path(args[args.index('--commitment-repo') + 1])
        run = subprocess.run

        def wrapped(command, *positional, **kwargs):
            return run(commitment_command(command), *positional, **kwargs)

        stack.enter_context(mock.patch.object(bc, 'ROOT', repo))
        stack.enter_context(mock.patch.object(subprocess, 'run', side_effect=wrapped))
        stack.callback(commit_journal, repo)
        yield


if __name__ == '__main__':
    import runpy
    if sys.argv[1] != '--run-cli':
        raise SystemExit('test-only CLI wrapper requires --run-cli')
    script, arguments = sys.argv[2], sys.argv[3:]
    sys.path.insert(0, str(Path(script).resolve().parents[1]))
    sys.argv = [script, *arguments]
    with synthetic_checkout(arguments):
        if Path(script).name in {'bytes_analyze.py', 'bytes_twin.py', 'bytes_commitment.py'}:
            import importlib
            module = importlib.import_module('scripts.' + Path(script).stem)
            if Path(module.__file__).resolve() != Path(script).resolve():
                raise RuntimeError('synthetic CLI checkout resolved the wrong executable')
            raise SystemExit(module.main(arguments))
        runpy.run_path(script, run_name='__main__')
