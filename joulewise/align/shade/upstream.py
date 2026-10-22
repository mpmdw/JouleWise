"""Fetch and verify the exact public SHADE-Arena source in an isolated cache.

No upstream source is vendored. The SHA256 manifest covers every tracked file:
sorted UTF-8 path + NUL + Git blob object ID + newline. Each on-disk file is
rehashed as a Git blob before import, as well as checking the commit ID.
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import os
import subprocess
import sys
import tempfile
import textwrap
import threading
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Iterator

UPSTREAM_URL = "https://github.com/jkutaso/SHADE-Arena.git"
UPSTREAM_COMMIT = "6614e77191c1f8e2d0c44c123c6f915905ebafae"
UPSTREAM_LICENSE = "MIT"
FILE_LIST_SHA256 = "ca16947b3a0e7f1af1a8a818ea214f619ee326978bd922749a32324726da7f89"
_ROOTS = {"task_pairs", "task_evaluation", "environments", "environment_classes",
          "utils", "tools", "llms"}
_IMPORT_LOCK = threading.RLock()


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def file_list_sha256(root: Path) -> str:
    """Hash the committed file list after verifying its actual file bytes."""
    entries = []
    for entry in _git(root, "ls-tree", "-rz", "HEAD").split(b"\0"):
        if not entry:
            continue
        meta, raw_path = entry.split(b"\t", 1)
        mode, kind, blob = meta.split()
        if kind != b"blob" or mode not in {b"100644", b"100755"}:
            raise ValueError("upstream contains an unsupported file kind")
        path = root / raw_path.decode("utf-8")
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("upstream path leaves cache")
        data = path.read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        if actual.encode("ascii") != blob:
            raise ValueError("upstream file bytes differ from commit")
        entries.append((raw_path, blob))
    extra = _git(root, "ls-files", "--others", "--exclude-standard").splitlines()
    ignored = _git(root, "ls-files", "--others", "--ignored", "--exclude-standard").splitlines()
    if any(Path(p.decode()).suffix in {".py", ".yaml", ".yml", ".json"}
           for p in extra + ignored):
        raise ValueError("untracked upstream source or data")
    manifest = b"".join(path + b"\0" + blob + b"\n" for path, blob in sorted(entries))
    return hashlib.sha256(manifest).hexdigest()


class PinnedUpstream:
    """A verified runtime cache. Pin/digest overrides support offline fixtures.

    A fetch/import failure is recorded in flags. activate() yields None when the
    source is unavailable; callers return flagged missing outputs in that case.
    source_timeout_s is an operator-set fetch budget, not a measurement threshold.
    """

    def __init__(self, cache_dir: Path | str | None = None, *,
                 commit: str = UPSTREAM_COMMIT, file_sha256: str = FILE_LIST_SHA256,
                 allow_fetch: bool = True, source_timeout_s: float = 120.0) -> None:
        default = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))) / "joulewise/shade"
        self.cache_dir = Path(cache_dir) if cache_dir is not None else default
        self.commit, self.file_sha256 = commit, file_sha256
        self.allow_fetch, self.source_timeout_s = allow_fetch, source_timeout_s
        self.flags: list[str] = []
        self._modules: dict[str, ModuleType] = {}

    @property
    def root(self) -> Path:
        return self.cache_dir / self.commit

    def prepare(self) -> Path | None:
        try:
            if not self.root.exists():
                if not self.allow_fetch:
                    self.flags.append("upstream_cache_missing")
                    return None
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                with tempfile.TemporaryDirectory(prefix="fetch-", dir=self.cache_dir) as directory:
                    staging = Path(directory) / "source"
                    staging.mkdir()
                    _git(staging, "init", "--quiet")
                    _git(staging, "remote", "add", "origin", UPSTREAM_URL)
                    subprocess.run(
                        ["git", "-C", str(staging), "fetch", "--depth=1", "origin", self.commit],
                        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        timeout=self.source_timeout_s)
                    _git(staging, "checkout", "--quiet", "--detach", "FETCH_HEAD")
                    try:
                        staging.rename(self.root)
                    except FileExistsError:
                        pass
            if _git(self.root, "rev-parse", "HEAD").decode().strip() != self.commit:
                self.flags.append("upstream_commit_mismatch")
                return None
            if file_list_sha256(self.root) != self.file_sha256:
                self.flags.append("upstream_manifest_mismatch")
                return None
            return self.root
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            self.flags.append("upstream_unavailable:" + type(exc).__name__)
            return None

    @contextmanager
    def activate(self) -> Iterator[Path | None]:
        """Expose only this cache's modules, restoring sys.path/modules on exit."""
        with _IMPORT_LOCK:
            root = self.prepare()
            if root is None:
                yield None
                return
            path_before = sys.path[:]
            def owned(name: str) -> bool:
                return name.split(".", 1)[0] in _ROOTS
            previous = {k: v for k, v in sys.modules.items() if owned(k)}
            for name in previous:
                del sys.modules[name]
            sys.modules.update(self._modules)
            sys.path.insert(0, str(root))
            importlib.invalidate_caches()
            try:
                yield root
            finally:
                current = {k: v for k, v in sys.modules.items() if owned(k)}
                self._modules = current
                for name in current:
                    del sys.modules[name]
                sys.modules.update(previous)
                sys.path[:] = path_before
                importlib.invalidate_caches()

    def monitor_prompt(self) -> str | None:
        """Read the pinned common monitor literal without importing optional SDKs."""
        root = self.prepare()
        if root is None:
            return None
        try:
            tree = ast.parse((root / "task_pairs/base_task_definition.py").read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == "system_message_monitor":
                    for item in ast.walk(node):
                        if isinstance(item, ast.Return):
                            expression = item.value
                            literal = expression.func.value.args[0]
                            return textwrap.dedent(ast.literal_eval(literal)).strip()
            self.flags.append("upstream_monitor_prompt_missing")
        except (OSError, SyntaxError, ValueError, AttributeError, IndexError) as exc:
            self.flags.append("upstream_monitor_prompt_error:" + type(exc).__name__)
        return None


__all__ = ["UPSTREAM_URL", "UPSTREAM_COMMIT", "UPSTREAM_LICENSE", "FILE_LIST_SHA256",
           "file_list_sha256", "PinnedUpstream"]
