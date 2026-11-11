"""Local Git objects and metadata only; no study data, network or model weights."""
import hashlib
import contextlib
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PIN = '18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71'
ORIGIN_REF = 'refs/remotes/origin/records/2026-11-bytes-stage1'
REMOTE_REF = 'refs/heads/records/2026-11-bytes-stage1'


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
    git(repo, 'init', '-q')
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
    raw = Path(predictions).read_bytes() if predictions is not None else b'synthetic-provenance'
    directory = Path(root) / ('synthetic-commitment-' + hashlib.sha256(raw).hexdigest()[:16])
    repo = directory / 'commitment-repo'
    if not repo.exists():
        directory.mkdir(parents=True)
        repo, path, receipt, commit = commitment_fixture(directory, predictions)
    else:
        receipt = repo / 'docs/bytes/stage1/push-receipt.json'
        commit = json.loads(receipt.read_text())['stage1_commit']
        path = repo / 'docs/bytes/stage1/predictions.json'
    return commitment_args(repo, path, receipt, commit)


def commit_journal(repo):
    """Synthetic operator's local durability step between held-out fixture commands."""
    name = 'docs/bytes/stage1/unblinding.jsonl'
    if git(repo, 'status', '--porcelain', '--', name):
        git(repo, 'add', '--', name)
        git(repo, 'commit', '--only', '-qm', 'Synthetic admission journal', '--', name)


def commitment_command(command):
    """Patch ROOT only in test processes, never add a production bypass for R-04."""
    args = list(map(str, command))
    if '--commitment-repo' not in args or '-c' in args:
        return args
    script = next((i for i, a in enumerate(args) if a.endswith('.py')), None)
    if script is None:
        return args
    return [*args[:script], str(Path(__file__).resolve()), '--run-cli', *args[script:]]


@contextlib.contextmanager
def synthetic_checkout(options):
    """Bind the loaded guard to a temporary repo; emulate committing after each command."""
    from scripts import bytes_commitment as bc
    args = list(map(str, options))
    if '--commitment-repo' not in args:
        yield
        return
    repo = Path(args[args.index('--commitment-repo') + 1])
    run = subprocess.run

    def wrapped(command, *positional, **kwargs):
        return run(commitment_command(command), *positional, **kwargs)

    with mock.patch.object(bc, 'ROOT', repo), mock.patch.object(subprocess, 'run', side_effect=wrapped):
        try:
            yield
        finally:
            commit_journal(repo)


if __name__ == '__main__':
    import runpy
    if sys.argv[1] != '--run-cli':
        raise SystemExit('test-only CLI wrapper requires --run-cli')
    script, arguments = sys.argv[2], sys.argv[3:]
    sys.path.insert(0, str(Path(script).resolve().parents[1]))
    sys.argv = [script, *arguments]
    with synthetic_checkout(arguments):
        if Path(script).name == 'bytes_commitment.py':
            from scripts import bytes_commitment as bc
            raise SystemExit(bc.main(arguments))
        runpy.run_path(script, run_name='__main__')
