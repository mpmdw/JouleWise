"""Only source/config blobs, extracted under the authorized draft folder; no checkout."""
from contextlib import contextmanager
import io
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parents[1]
ROOT = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=HERE, text=True).strip())
SOURCE = '6010985a3312c77bb8e4bb4bf5c920c4d49b8512'
PIN = 'ab32a6c915a9a78f92554a89c5d0eb93333b7a39'
W1 = 'c3f4bacd8013ca98c19cf8d41f830c701930cd41'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

@contextmanager
def pinned():
    # No worktree, ref or configuration writes; only approved source files.
    paths = git('ls-tree', '-r', '--name-only', PIN, 'scripts', 'joulewise').decode().splitlines()
    paths = [p for p in paths if p.endswith(('.py', '.sh'))]
    paths += ['configs/align/v4/r1_runtime.json',
              'configs/campaigns/align_v4/registration/inputs.json']
    with tempfile.TemporaryDirectory(prefix='.pinned-', dir=HERE) as temp:
        root = Path(temp)
        raw = git('archive', '--format=tar', PIN, *paths)
        with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
            for member in tar:
                if member.isfile():
                    assert member.name in paths
                    dest = root / member.name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(tar.extractfile(member).read())
        yield root

def call(repo, *args, ok=True, **env_overrides):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', JW_B5_SYNTHETIC_ONLY='1', TMPDIR=str(repo))
    env.update(env_overrides)
    result = subprocess.run([sys.executable, '-B', *map(str, args)], cwd=repo,
                            env=env, text=True, capture_output=True)
    if ok and result.returncode:
        raise AssertionError((args, result.returncode, result.stdout, result.stderr))
    return result
