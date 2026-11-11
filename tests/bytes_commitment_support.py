"""Local Git objects and metadata only; no study data, network or model weights."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PIN = '18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71'


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
    git(repo, 'update-ref', 'refs/remotes/origin/synthetic', commit)
    receipt = metadata / 'push-receipt.json'
    receipt.write_text(json.dumps({'schema': 'joulewise.bytes_push_receipt.v1', 'stage1_commit': commit,
                                  'predictions_path': 'docs/bytes/stage1/predictions.json',
                                  'origin_ref': 'refs/remotes/origin/synthetic', 'origin_tip': commit,
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
