"""Synthetic compression custody and free-space seams for desk restore tests."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def compress_member(path, archive):
    raw = path.read_bytes()
    subprocess.run([shutil.which('zstd') or '/opt/homebrew/bin/zstd', '-q', str(path),
                    '-o', str(path) + '.zst'], check=True)
    journal = Path(str(archive) + '.desk') / 'compression.jsonl'
    journal.parent.mkdir(parents=True, exist_ok=True)
    with journal.open('a') as stream:
        stream.write(json.dumps({'event': 'compress', 'path': str(path.resolve()), 'root': 'archive',
                                 'sha256': hashlib.sha256(raw).hexdigest(), 'size': len(raw),
                                 'zst_size': Path(str(path) + '.zst').stat().st_size, 't': 0}) + '\n')
    path.unlink()
    return journal


def ample_space_command(command, *, free=1024**4):
    """Patch only free-space observations in a fixture subprocess, on both sides."""
    command = list(command)
    if command[1:2] == ["-B"]:
        del command[1]
    return [command[0], '-B', '-c',
            'import runpy,shutil,sys; from types import SimpleNamespace; '
            f'shutil.disk_usage=lambda p: SimpleNamespace(free={free}); '
            'sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name="__main__")', *command[1:]]
