"""Verified derivation layer (D-188 VDL-CORE): a run-scoped, content-addressed leaf store.

Principle: decisions stay above, verified leaves sit below. Only a closed set of
pure, expensive leaf functions (``LEAVES``) is ever served from this store.
Every caller still runs its own loops, refusal mapping, census rows and record
writes; a leaf call returns, at the caller's own position, either the value a
verified earlier computation of the same leaf on the same bytes returned, or the
value of calling the leaf itself, there and then. Exceptions are never stored,
so every exception-type refusal is raised by the unchanged serial code.

Nothing is active outside ``analysis_run_cache.analysis_run_caches(...,
vdl_mode=...)``: ``call`` then is exactly ``fn(*args, **kwargs)``.

Key. sha256 over an injective, type-tagged encoding of: the schema, the run
commit (if the driver supplies one) and a content digest of the ``joulewise``
package sources, a digest of every ``JOULEWISE_*`` environment variable, the
leaf id, the leaf's scalar arguments, and for every tree argument its resolved
path (or, for a path-free leaf, its final name) and its tree digest.

Tree digest. An lstat walk that follows no symlink: per file (relpath, kind,
mode, size, sha256), per directory (relpath, mode, sorted listing). A path-free
leaf uses the content-only form (relpath, kind, sha256 and listings): bracket
copies get their modes from the umask. A symlink, a special file or any error
bypasses the store for that call.

Verification scope. A tree, file or listing hashed once in a program is reused
in that program only while its lstat signature (st_dev, st_ino, st_mode,
st_size, st_mtime_ns, st_ctime_ns of every entry) is unchanged. A program scope
is entered with ``enter_program_scope()`` (the block-5 StepRunner, per program).
Outside one, a context-local scope lives only as long as the analysis-run
activation and the program generation it was created under, so a fresh
``contextvars.Context()`` replay, a member task and a new program re-hash.

A fill (a miss) runs the leaf and is stored only when all of these hold:
the leaf returned normally; the run's wall-deadline firings did not change and
the observer was available; ``note_clock()``/``note_unstorable()`` was not
called inside it; the recorder saw no write-mode open, file mutation,
subprocess, thread start, chdir or network use; every read and listing could be
attributed (an ``os.open`` of a relative name, as the no-follow ``dir_fd`` walk
makes, is attributed only through an authentication_io no-follow row); the
scalar arguments are unchanged by the call; every tree's lstat signature is
unchanged across the call; the physics view behaves as the J2 premise needs.
Reads outside the leaf's trees and outside the Python installation and the
``joulewise`` sources are kept as (path, sha256) extras, and listings as name
digests; both are re-verified on every hit (cached per scope, lstat-guarded).

V2 authentication rows. An entry carries the V2 registration rows a session
would hold after the leaf: from the session's own record delta for an
in-session fill, and from authentication_io's read recorder for a session-less
fill only when that recorder declares it represents capability
(``V2AuthenticationPath``) reads too (``RECORDS_CAPABILITY_READS``). Otherwise
the entry cannot serve a call inside a session. A hit inside a session first
obtains, for every json/jsonl row, a grammar verdict under the consumer's own
effective grammar and vocabulary flag (``_parse_strict`` on the just re-read
and re-hashed bytes, through authentication_io's success-only memo when
present); any failure discards the hit and the leaf runs in the session, so the
same V2 refusal fires at the same read. The rows are then pre-checked against
the session's first digests and grammars and registered in order. Path-free
rows inside a tree are stored relative to the tree and relocated to the
consumer's tree.

Pool pre-filters use ``probe()``: a side-effect-free check (no registration,
no physics insert) whose returned hit is applied at the member's serial
position with ``hit.apply()``, which re-verifies the trees, extras and physics
admission there and raises (the caller then computes the leaf) if anything
changed. Inside a fill, ``fill_active()`` is true: a member pool must stay
serial there, because a worker process's reads are invisible to this recorder.

Physics. A leaf's probe names the physics-cache entries it may read or insert;
which entries a call consults (not their values) is part of the key.
A fill records the visible value before (V0) and after (P). A lookup is
admitted only if the caller's visible value V is ABSENT or equals P exactly;
P is inserted where V is ABSENT.

Defects. Nothing in this module raises into a caller's ``except`` clauses: a
hit anomaly falls through to the leaf, a poisoned key (two fills disagree) falls
back to the leaf, and a shadow mismatch returns the freshly computed value and
sets a run-level defect flag. ``check_defects()`` raises ``VerifiedStoreDefect``
(a ``BaseException``) and is meant for the driver's step boundaries, outside
every leaf; the flag also travels in ``export_entries`` payloads.

Blinding. Hit, miss, poison and shadow counts live only in process memory and
are read only through ``restricted_counters()``, for the custody root's
restricted tier. This module prints and logs nothing.
"""
from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import contextmanager, nullcontext
import contextvars
from dataclasses import dataclass, field, fields, is_dataclass
import enum
import hashlib
import importlib
import inspect
import itertools
import math
import os
from pathlib import Path, PurePath
import pickle
import stat
import sys
import threading
from types import MappingProxyType
from typing import Any, Callable, Iterator, Mapping, Sequence

SCHEMA = "joulewise-vdl/1"
ENV_VARIABLE = "JOULEWISE_B5_VDL"
GRAMMAR_VERDICT_MEMO = "authentication_io.grammar_ok"
HASH_THREADS = 4
_CHUNK = 1 << 20


class _Absent:
    """The physics view held no entry for a key."""

    _instance: "_Absent | None" = None

    def __new__(cls) -> "_Absent":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __reduce__(self) -> str:
        return "ABSENT"

    def __repr__(self) -> str:
        return "ABSENT"


ABSENT = _Absent()


class VerifiedStoreDefect(BaseException):
    """A store defect (a shadow mismatch, or a hit served from a key later poisoned).

    A ``BaseException`` so that no ``except Exception`` refusal site can turn it
    into a study refusal. Only ``check_defects()`` raises it, at a step boundary.
    """


class _Bypass(Exception):
    """This call cannot use the store; run the leaf unchanged."""


# --------------------------------------------------------------------------- modes


@dataclass(frozen=True)
class Mode:
    name: str  # "off" | "on" | "shadow"
    permille: int = 0

    @property
    def active(self) -> bool:
        return self.name != "off"


OFF = Mode("off")
ON = Mode("on")


def parse_mode(raw: str | None) -> Mode:
    """``off``, ``on`` or ``shadow:<permille>`` (an integer 0..1000)."""

    if raw is None:
        raise ValueError("no VDL mode")
    text = raw.strip()
    if text == "off":
        return OFF
    if text == "on":
        return ON
    if text.startswith("shadow:"):
        digits = text[len("shadow:"):]
        if digits.isdigit() and digits.isascii():
            permille = int(digits)
            if 0 <= permille <= 1000:
                return Mode("shadow", permille)
    raise ValueError(f"malformed {ENV_VARIABLE}")


def resolve_mode(raw: str | None, *, synthetic: bool) -> Mode:
    """The run's mode. Lead ruling: shadow verification is on by default for
    synthetic runs and never runs on a real blind run (no new refusal path on
    real data): there an unset value is ``on``, a shadow request runs ``on``,
    and a malformed value runs ``off`` (the R2 behaviour).
    """

    if raw is None:
        return Mode("shadow", 1000) if synthetic else ON
    if synthetic:
        return parse_mode(raw)
    try:
        mode = parse_mode(raw)
    except ValueError:
        return OFF
    return ON if mode.name == "shadow" else mode


# ----------------------------------------------------------- canonical encoding


def _qualified(kind: type) -> bytes:
    return f"{kind.__module__}.{kind.__qualname__}".encode()


def _resolve_reference(reference: str) -> Any:
    module, _, name = reference.partition(":")
    target: Any = importlib.import_module(module)
    for part in name.split("."):
        target = getattr(target, part)
    return target


def _frame(tag: bytes, payload: bytes) -> bytes:
    return tag + str(len(payload)).encode() + b":" + payload


def canonical_bytes(value: Any) -> bytes:
    """An injective, type-tagged encoding (no float/mapping collision).

    Raises ``TypeError`` for a value with no exact canonical form; the store is
    then bypassed for that call.
    """

    if value is None:
        return b"N"
    if value is True:
        return b"T"
    if value is False:
        return b"F"
    kind = type(value)
    if kind is int:
        return _frame(b"i", str(value).encode())
    if kind is float:
        return _frame(b"f", value.hex().encode())
    if kind is str:
        return _frame(b"s", value.encode("utf-8", "surrogatepass"))
    if kind is bytes:
        return _frame(b"b", value)
    if isinstance(value, enum.Enum):
        return _frame(b"e", _qualified(kind) + b"\0" + canonical_bytes(value.value))
    if isinstance(value, PurePath):
        return _frame(b"p", _qualified(kind) + b"\0" + str(value).encode("utf-8", "surrogatepass"))
    if isinstance(value, (int, float, str, bytes)):
        # A subclass (IntEnum handled above, bool above): tag its type.
        base = int if isinstance(value, int) else float if isinstance(value, float) else str if isinstance(value, str) else bytes
        return _frame(b"x", _qualified(kind) + b"\0" + canonical_bytes(base(value)))
    if is_dataclass(value) and not isinstance(value, type):
        parts = [_qualified(kind)]
        for item in fields(value):
            parts.append(canonical_bytes(item.name) + canonical_bytes(getattr(value, item.name)))
        return _frame(b"D", b"\0".join(parts))
    if isinstance(value, (Mapping, MappingProxyType)):
        items = sorted((canonical_bytes(key), canonical_bytes(item)) for key, item in value.items())
        return _frame(b"d", _qualified(kind) + b"\0" + b"".join(_frame(b"k", k) + _frame(b"v", v) for k, v in items))
    if isinstance(value, (list, tuple)):
        return _frame(b"l", _qualified(kind) + b"\0" + b"".join(_frame(b"m", canonical_bytes(item)) for item in value))
    if isinstance(value, (set, frozenset)):
        items = sorted(canonical_bytes(item) for item in value)
        return _frame(b"S", _qualified(kind) + b"\0" + b"".join(_frame(b"m", item) for item in items))
    if callable(value) and hasattr(value, "__module__") and hasattr(value, "__qualname__"):
        reference = f"{value.__module__}:{value.__qualname__}"
        if "<" not in reference:
            try:
                if _resolve_reference(reference) is value:
                    return _frame(b"c", reference.encode())
            except (ImportError, AttributeError):
                pass
    raise TypeError(f"no canonical form for {kind.__name__}")


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


# --------------------------------------------------------------- code and env

_CODE_DIGEST: str | None = None
_CODE_LOCK = threading.Lock()
_PACKAGE_ROOT = Path(__file__).resolve().parent


def code_digest() -> str:
    """Content digest of every ``joulewise/**/*.py`` (once per process)."""

    global _CODE_DIGEST
    with _CODE_LOCK:
        if _CODE_DIGEST is None:
            digest = hashlib.sha256()
            for path in sorted(_PACKAGE_ROOT.rglob("*.py")):
                relative = path.relative_to(_PACKAGE_ROOT).as_posix()
                digest.update(_frame(b"r", relative.encode()))
                digest.update(_frame(b"h", hashlib.sha256(path.read_bytes()).digest()))
            _CODE_DIGEST = digest.hexdigest()
        return _CODE_DIGEST


def environment_digest(environ: Mapping[str, str] | None = None) -> str:
    source = os.environ if environ is None else environ
    items = sorted((key, value) for key, value in source.items() if key.startswith("JOULEWISE_"))
    return canonical_digest(tuple(items))


def _code_roots() -> tuple[str, ...]:
    roots = {sys.prefix, sys.base_prefix, sys.exec_prefix, sys.base_exec_prefix}
    for entry in sys.path:
        if entry and ("site-packages" in entry or "dist-packages" in entry):
            roots.add(entry)
    return tuple(sorted(os.path.realpath(root) for root in roots if root))


# ----------------------------------------------------------------- tree digest

_HASH_POOL: ThreadPoolExecutor | None = None
_HASH_POOL_LOCK = threading.Lock()


def _hash_pool() -> ThreadPoolExecutor:
    global _HASH_POOL
    with _HASH_POOL_LOCK:
        if _HASH_POOL is None:
            _HASH_POOL = ThreadPoolExecutor(max_workers=HASH_THREADS, thread_name_prefix="vdl-hash")
        return _HASH_POOL


def _hash_file_nofollow(path: str) -> str:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise OSError("not a regular file")
        digest = hashlib.sha256()
        while True:
            chunk = os.read(descriptor, _CHUNK)
            if not chunk:
                break
            digest.update(chunk)
        return digest.hexdigest()
    finally:
        os.close(descriptor)


def _signature_row(st: os.stat_result) -> tuple[int, ...]:
    return (st.st_dev, st.st_ino, st.st_mode, st.st_size, st.st_mtime_ns, st.st_ctime_ns)


@dataclass(frozen=True)
class _Walk:
    signature: str
    files: tuple[tuple[str, int, int], ...]  # (relpath, mode, size)
    directories: tuple[tuple[str, int, tuple[str, ...]], ...]  # (relpath, mode, sorted names)


def _walk(root: str) -> _Walk | None:
    """An lstat walk following no symlink; ``None`` for a symlink, special file or error."""

    try:
        top = os.lstat(root)
    except OSError:
        return None
    if not stat.S_ISDIR(top.st_mode):
        return None
    signature = hashlib.sha256()
    signature.update(repr(("", "d") + _signature_row(top)).encode())
    files: list[tuple[str, int, int]] = []
    directories: list[tuple[str, int, tuple[str, ...]]] = []
    pending = [("", root, top)]
    try:
        while pending:
            relative, absolute, st = pending.pop()
            names = sorted(os.listdir(absolute))
            directories.append((relative, stat.S_IMODE(st.st_mode), tuple(names)))
            for name in names:
                child_relative = f"{relative}/{name}" if relative else name
                child_absolute = os.path.join(absolute, name)
                child = os.lstat(child_absolute)
                signature.update(repr((child_relative,) + _signature_row(child)).encode())
                if stat.S_ISDIR(child.st_mode):
                    pending.append((child_relative, child_absolute, child))
                elif stat.S_ISREG(child.st_mode):
                    files.append((child_relative, stat.S_IMODE(child.st_mode), child.st_size))
                else:
                    return None
    except OSError:
        return None
    return _Walk(signature.hexdigest(), tuple(sorted(files)), tuple(sorted(directories)))


def _tree_digest_from(walk: _Walk, shas: Mapping[str, str], content_only: bool) -> str:
    rows: list[tuple] = []
    for relative, mode, names in walk.directories:
        rows.append(("d", relative, names) if content_only else ("d", relative, mode, names))
    for relative, mode, size in walk.files:
        rows.append(("f", relative, shas[relative]) if content_only else ("f", relative, mode, size, shas[relative]))
    return canonical_digest(("content" if content_only else "full", tuple(rows)))


@dataclass(frozen=True)
class TreeVerdict:
    digest: str
    signature: str
    files: Mapping[str, str]  # relpath -> sha256


def tree_digest(root: Path | str, *, content_only: bool = False) -> TreeVerdict | None:
    """Hash a directory tree (4 threads); ``None`` means bypass the store."""

    absolute = os.fspath(root)
    before = _walk(absolute)
    if before is None:
        return None
    pool = _hash_pool()
    futures = {relative: pool.submit(_hash_file_nofollow, os.path.join(absolute, relative))
               for relative, _, _ in before.files}
    try:
        shas = {relative: future.result() for relative, future in futures.items()}
    except OSError:
        return None
    after = _walk(absolute)
    if after is None or after.signature != before.signature:
        return None
    return TreeVerdict(_tree_digest_from(before, shas, content_only), before.signature, MappingProxyType(shas))


def _file_signature(path: str) -> str | None:
    try:
        st = os.lstat(path)
    except OSError:
        return None
    if not stat.S_ISREG(st.st_mode):
        return None
    return repr(_signature_row(st))


def _listing(path: str) -> tuple[str, str] | None:
    """(names digest, signature) of a directory listing, following no symlink."""

    try:
        st = os.lstat(path)
        if not stat.S_ISDIR(st.st_mode):
            return None
        names = sorted(os.listdir(path))
        after = os.lstat(path)
    except OSError:
        return None
    if _signature_row(st) != _signature_row(after):
        return None
    return canonical_digest(tuple(names)), repr(_signature_row(st))


# ------------------------------------------------------------ verification scope


class _Scope:
    """Verified trees, files and listings of one program (lstat-guarded)."""

    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.trees: dict[tuple[str, bool], TreeVerdict] = {}
        self.files: dict[str, tuple[str, str]] = {}  # path -> (sha256, signature)
        self.listings: dict[str, tuple[str, str]] = {}  # path -> (digest, signature)
        self.pending: dict[tuple[str, bool], Future] = {}
        self.prefetched = False

    def verify_tree(self, root: str, content_only: bool) -> TreeVerdict | None:
        key = (root, content_only)
        with self.lock:
            future = self.pending.pop(key, None)
            known = self.trees.get(key)
        if future is not None:
            try:
                prefetched = future.result()
            except Exception:  # noqa: BLE001 - a failed prefetch only means re-hash
                prefetched = None
            if prefetched is not None:
                known = prefetched
        if known is not None:
            walk = _walk(root)
            if walk is not None and walk.signature == known.signature:
                with self.lock:
                    self.trees[key] = known
                return known
        verdict = tree_digest(root, content_only=content_only)
        with self.lock:
            if verdict is None:
                self.trees.pop(key, None)
            else:
                self.trees[key] = verdict
        return verdict

    def verify_file(self, path: str) -> str | None:
        signature = _file_signature(path)
        if signature is None:
            return None
        with self.lock:
            known = self.files.get(path)
        if known is not None and known[1] == signature:
            return known[0]
        try:
            digest = _hash_file_nofollow(path)
        except OSError:
            return None
        if _file_signature(path) != signature:
            return None
        with self.lock:
            self.files[path] = (digest, signature)
        return digest

    def verify_listing(self, path: str) -> str | None:
        try:
            signature = repr(_signature_row(os.lstat(path)))
        except OSError:
            return None
        with self.lock:
            known = self.listings.get(path)
        if known is not None and known[1] == signature:
            return known[0]
        result = _listing(path)
        if result is None:
            return None
        with self.lock:
            self.listings[path] = result
        return result[0]

    def seed(self, root: str, verdict: TreeVerdict, content_only: bool) -> None:
        with self.lock:
            self.trees[(root, content_only)] = verdict

    def prefetch(self, roots: Sequence[tuple[str, bool]]) -> None:
        pool = _prefetch_pool()
        with self.lock:
            for root, content_only in roots:
                key = (root, content_only)
                if key in self.trees or key in self.pending:
                    continue
                self.pending[key] = pool.submit(tree_digest, root, content_only=content_only)


_PREFETCH_POOL: ThreadPoolExecutor | None = None


def _prefetch_pool() -> ThreadPoolExecutor:
    global _PREFETCH_POOL
    with _HASH_POOL_LOCK:
        if _PREFETCH_POOL is None:
            _PREFETCH_POOL = ThreadPoolExecutor(max_workers=HASH_THREADS, thread_name_prefix="vdl-prefetch")
        return _PREFETCH_POOL


_PROGRAM_SCOPE: contextvars.ContextVar[_Scope | None] = contextvars.ContextVar(
    "joulewise_vdl_program_scope", default=None)
_LAZY_SCOPE: contextvars.ContextVar[tuple[tuple[int, int], _Scope] | None] = contextvars.ContextVar(
    "joulewise_vdl_lazy_scope", default=None)
_GENERATION = itertools.count(1)
_CURRENT_GENERATION = [0]


@contextmanager
def enter_program_scope() -> Iterator[_Scope]:
    """One program's verification scope (the block-5 StepRunner, around main())."""

    scope = _Scope()
    token = _PROGRAM_SCOPE.set(scope)
    _CURRENT_GENERATION[0] = next(_GENERATION)
    try:
        yield scope
    finally:
        _PROGRAM_SCOPE.reset(token)
        _CURRENT_GENERATION[0] = next(_GENERATION)


def _current_scope() -> _Scope:
    scope = _PROGRAM_SCOPE.get()
    if scope is not None:
        return scope
    from joulewise import analysis_run_cache

    caches = analysis_run_cache.current()
    tag = (getattr(caches, "serial", 0), _CURRENT_GENERATION[0])
    lazy = _LAZY_SCOPE.get()
    if lazy is not None and lazy[0] == tag:
        return lazy[1]
    scope = _Scope()
    _LAZY_SCOPE.set((tag, scope))
    return scope


def seed_verified(root: Path | str, file_sha256: Mapping[str, str], *, content_only: bool = False) -> bool:
    """Seed the current scope with a tree whose file digests the caller just authenticated.

    ``file_sha256`` maps every regular file's relative path (posix) to its
    sha256; the tree is lstat-walked (no bytes read) and must hold exactly those
    files. Returns whether the seed was taken.
    """

    absolute = os.fspath(Path(root).resolve(strict=False))
    walk = _walk(absolute)
    if walk is None or {relative for relative, _, _ in walk.files} != set(file_sha256):
        return False
    verdict = TreeVerdict(_tree_digest_from(walk, file_sha256, content_only), walk.signature,
                          MappingProxyType(dict(file_sha256)))
    _current_scope().seed(absolute, verdict, content_only)
    return True


def prefetch_verify(roots: Sequence[Path | str], *, content_only: bool = False) -> None:
    """Start hashing ``roots`` in the background for the current scope."""

    _current_scope().prefetch([(os.fspath(Path(root).resolve(strict=False)), content_only) for root in roots])


# --------------------------------------------------------------------- recorder

_O_WRITE = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
_WRITE_EVENTS = frozenset({
    "os.remove", "os.unlink", "os.rename", "os.replace", "os.rmdir", "os.mkdir", "os.truncate",
    "os.chmod", "os.chown", "os.utime", "os.symlink", "os.link", "os.chflags", "os.lchflags",
    "os.lchmod", "os.lchown", "os.setxattr", "os.removexattr", "os.putenv", "os.unsetenv",
    "os.mkfifo", "os.mknod", "shutil.copyfile", "shutil.copymode", "shutil.copystat",
    "shutil.copytree", "shutil.move", "shutil.rmtree", "shutil.chown", "shutil.make_archive",
    "shutil.unpack_archive", "tempfile.mkstemp", "tempfile.mkdtemp", "os.truncate",
})
_PROCESS_EVENTS = frozenset({
    "subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork",
    "os.forkpty", "os.startfile", "pty.spawn", "os.kill", "os.killpg",
})
_THREAD_EVENTS = frozenset({"_thread.start_new_thread", "_thread.start_joinable_thread"})
_DIRECTORY_EVENTS = frozenset({"os.chdir", "os.fchdir", "os.chroot"})


class _Fill:
    """What one in-flight leaf computation did (appended to by the audit hook)."""

    def __init__(self) -> None:
        self.unstorable: set[str] = set()
        self.clock = False
        self.reads: list[str] = []
        self.relative_opens: list[str] = []
        self.listings: list[str] = []
        self.forwarded_trees: list[tuple[str, bool, str]] = []
        self.forwarded_extras: list[tuple[str, str]] = []
        self.forwarded_listings: list[tuple[str, str]] = []


_FILLS: contextvars.ContextVar[tuple[_Fill, ...]] = contextvars.ContextVar("joulewise_vdl_fills", default=())
_SUSPENDED: contextvars.ContextVar[bool] = contextvars.ContextVar("joulewise_vdl_suspended", default=False)
_HOOK_INSTALLED = [False]
_HOOK_LOCK = threading.Lock()
_IN_HOOK = threading.local()


def _mark(fills: tuple[_Fill, ...], reason: str) -> None:
    for fill in fills:
        fill.unstorable.add(reason)


def _audit(event: str, args: tuple) -> None:
    fills = _FILLS.get()
    if not fills or _SUSPENDED.get() or getattr(_IN_HOOK, "active", False):
        return
    _IN_HOOK.active = True
    try:
        if event == "open":
            path, mode, flags = (tuple(args) + (None, None, None))[:3]
            if isinstance(path, int):
                return
            if isinstance(path, bytes):
                path = os.fsdecode(path)
            if not isinstance(path, str):
                _mark(fills, "unattributable_open")
                return
            writes = (isinstance(flags, int) and flags & _O_WRITE) or (
                isinstance(mode, str) and any(flag in mode for flag in "wax+"))
            if writes:
                _mark(fills, "write")
                return
            if mode is None and not os.path.isabs(path):
                for fill in fills:
                    fill.relative_opens.append(path)
                return
            absolute = os.path.abspath(path)
            for fill in fills:
                fill.reads.append(absolute)
        elif event in ("os.listdir", "os.scandir"):
            path = args[0] if args else None
            if path is None:
                path = "."
            if isinstance(path, bytes):
                path = os.fsdecode(path)
            if not isinstance(path, str):
                _mark(fills, "unattributable_listing")
                return
            absolute = os.path.abspath(path)
            for fill in fills:
                fill.listings.append(absolute)
        elif event in _WRITE_EVENTS:
            _mark(fills, "write")
        elif event in _PROCESS_EVENTS or event.startswith("os.exec") or event.startswith("os.spawn"):
            _mark(fills, "subprocess")
        elif event in _THREAD_EVENTS:
            _mark(fills, "thread")
        elif event in _DIRECTORY_EVENTS:
            _mark(fills, "chdir")
        elif event.startswith("socket."):
            _mark(fills, "network")
    except Exception:  # noqa: BLE001 - an audit hook must never raise into the audited call
        _mark(fills, "recorder_error")
    finally:
        _IN_HOOK.active = False


def _install_hook() -> None:
    with _HOOK_LOCK:
        if not _HOOK_INSTALLED[0]:
            sys.addaudithook(_audit)
            _HOOK_INSTALLED[0] = True


@contextmanager
def _suspended() -> Iterator[None]:
    token = _SUSPENDED.set(True)
    try:
        yield
    finally:
        _SUSPENDED.reset(token)


def note_clock() -> None:
    """The wall clock was consulted: no enclosing fill may be stored."""

    for fill in _FILLS.get():
        fill.clock = True


def note_unstorable(reason: str) -> None:
    """A leaf-lane guard (e.g. a timed or negative custody probe): do not store."""

    for fill in _FILLS.get():
        fill.unstorable.add(f"noted:{reason}")


def fill_active() -> bool:
    """Whether a leaf computation is being recorded here (pools should stay serial)."""

    return bool(_FILLS.get())


# ------------------------------------------------------ authentication_io adapter


class _AuthAdapter:
    """The minimal AUTH-IO interface this store codes against (see the PR).

    * ``recording_authentication_reads()``: a context manager yielding a list
      that receives one row per successful authentication_io read (attributes
      api, identity, sha256, grammar, caller_grammar, label, in_session,
      relative); absent: no rows.
    * ``RECORDS_CAPABILITY_READS``: true only when session-less recording also
      represents every read an active session would register (capability-path
      reads, pinned no-follow reads, git ingests); absent: false.
    * ``ensure_grammar_verdict`` on the session or module: the identical
      ``_parse_strict`` behind a success-only memo; absent: ``_parse_strict``.
    """

    @staticmethod
    def module() -> Any:
        from joulewise import authentication_io

        return authentication_io

    def recording(self) -> Any:
        recorder = getattr(self.module(), "recording_authentication_reads", None)
        return nullcontext(None) if recorder is None else recorder()

    def capability_complete(self) -> bool:
        return bool(getattr(self.module(), "RECORDS_CAPABILITY_READS", False))

    def session(self) -> Any:
        return self.module().active_v2_authentication_session()

    def forced_grammar(self, identity: str, grammar: str) -> str:
        return self.module()._forced_grammar(identity, grammar)

    def vocabulary_flag(self, session: Any, identity: str) -> bool:
        flag = getattr(session, "vocabulary_flag", None)
        if callable(flag):
            return bool(flag(identity))
        with session._lock:
            return identity in session._governed_spec_vocabulary_identities

    def ensure_verdict(self, session: Any, identity: str, raw: bytes, digest: str,
                       caller_grammar: str, label: str) -> str:
        """Raise exactly what ``session.read`` would raise for these bytes; else the grammar."""

        module = self.module()
        bridge = getattr(session, "ensure_grammar_verdict", None)
        if callable(bridge):
            return bridge(identity, raw, caller_grammar=caller_grammar, label=label, sha256=digest)
        effective = module._forced_grammar(identity, caller_grammar)
        flag = self.vocabulary_flag(session, identity)
        from joulewise import analysis_run_cache

        memo = analysis_run_cache.memo(GRAMMAR_VERDICT_MEMO)
        key = (digest, effective, flag)
        if memo is not None and memo.get(key) is True and hashlib.sha256(raw).hexdigest() == digest:
            return effective
        module._parse_strict(raw, effective, label, allow_governed_spec_vocabulary=flag)
        if memo is not None and hashlib.sha256(raw).hexdigest() == digest:
            memo[key] = True
        return effective

    def forward_rows(self, rows: Sequence["_Row"]) -> None:
        """Hand a hit's rows to any enclosing authentication_io recorder, in order."""

        module = self.module()
        holder = getattr(module, "_READ_RECORDER", None)
        row_type = getattr(module, "AuthenticationReadRow", None)
        sinks = None if holder is None else holder.get()
        if not sinks or row_type is None:
            return
        for row in rows:
            record = row_type(api="vdl.hit", identity=row.identity, sha256=row.sha256,
                              grammar=row.grammar, caller_grammar=row.caller_grammar, label=row.label,
                              in_session=True, grammar_verified=False, vocabulary_flag=False)
            for sink in sinks:
                sink.append(record)


_AUTH = _AuthAdapter()


@dataclass(frozen=True)
class _Row:
    """One V2 registration: (identity, sha256, effective grammar, caller grammar, label)."""

    identity: str
    sha256: str
    grammar: str
    caller_grammar: str
    label: str


# ------------------------------------------------------------------ leaf specs

TREE, TREES, SCALAR, PHYSICS = "tree", "trees", "scalar", "physics"


@dataclass(frozen=True)
class LeafSpec:
    leaf_id: str
    qualnames: tuple[str, ...]  # module:qualname of every callable this spec describes
    params: tuple[tuple[str, str], ...]  # (parameter, role): every parameter, exactly once
    path_free: bool = False
    physics_probe: Callable[[Mapping[str, Any]], list[tuple[Any, str]]] | None = None

    def roles(self) -> dict[str, str]:
        return dict(self.params)


def _calibration_key(metadata: Any) -> str | None:
    calibration = metadata.get("instrument_calibration") if isinstance(metadata, Mapping) else None
    digest = calibration.get("artifact_sha256") if isinstance(calibration, Mapping) else None
    return digest if isinstance(digest, str) else None


def _bundle_metadata(path: Any) -> Any:
    import json

    with _suspended():
        return json.loads((Path(path) / "metadata.json").read_bytes())


def _probe_strict(arguments: Mapping[str, Any]) -> list[tuple[Any, str]]:
    """L1: the view ``cli._strict_problems`` gives the reducer for this call."""

    from joulewise.analysis_run_cache import physics_cache_for_call

    metadata = _bundle_metadata(arguments["path"])
    key = _calibration_key(metadata)
    if key is None:
        return []
    explicit = arguments.get("physics_cache")
    if explicit is None:
        session = _AUTH.session()
        view = session.instrument_calibration_physics_cache if session is not None else None
        if view is None:
            view = physics_cache_for_call(None, metadata)
    else:
        view = physics_cache_for_call(explicit, metadata)
    return [] if view is None else [(view, key)]


def _probe_explicit(view_parameter: str, key_from: Callable[[Mapping[str, Any]], str | None]):
    def probe(arguments: Mapping[str, Any]) -> list[tuple[Any, str]]:
        view = arguments.get(view_parameter)
        key = key_from(arguments)
        return [] if view is None or key is None else [(view, key)]

    return probe


def _probe_operative(arguments: Mapping[str, Any]) -> list[tuple[Any, str]]:
    """L2: ``_member_operative_summary`` reads ``physics_cache_for_call({}, metadata)``."""

    from joulewise.analysis_run_cache import physics_cache_for_call

    key = _calibration_key(arguments["metadata"])
    view = physics_cache_for_call({}, arguments["metadata"])
    return [] if view is None or key is None else [(view, key)]


def reduce_bundle_dict(
    path: Path,
    *,
    reducer_version: str | None = None,
    physics_cache: dict[str, float] | None = None,
) -> dict[str, Any]:
    """L3 leaf body: ``reduce_bundle(path, ...).to_dict()``.

    Both stages raise exactly as before; a caller whose serial code separates
    the reduction and serialization failures (``cli._cmd_reduce``) must keep
    them separate around this leaf.
    """

    from joulewise.reduce import reduce_bundle

    if physics_cache is None:
        return reduce_bundle(path, reducer_version=reducer_version).to_dict()
    return reduce_bundle(path, reducer_version=reducer_version,
                         _instrument_calibration_physics_cache=physics_cache).to_dict()


def verify_instrument_calibration_at(
    bundle_path: Path,
    metadata: dict[str, Any],
    calibration: dict[str, Any],
    *,
    strict_physics: bool = True,
    physics_cache: dict[str, float] | None = None,
) -> tuple[float | None, str | None]:
    """L6 leaf body: ``_verify_instrument_calibration`` on a reader built here.

    Both whole_window sites pass a fresh ``BundleReader``; building it inside
    the leaf keeps the reader's parse cache out of the leaf's arguments.
    """

    from joulewise.bundle_read import BundleReader
    from joulewise.reduce import _verify_instrument_calibration

    return _verify_instrument_calibration(BundleReader(Path(bundle_path)), metadata, calibration,
                                          strict_physics=strict_physics, physics_cache=physics_cache)


LEAVES: tuple[LeafSpec, ...] = (
    LeafSpec(
        "L1_strict_validation",
        ("joulewise.cli:validate_bundle",),
        (("path", TREE), ("strict", SCALAR), ("physics_cache", PHYSICS)),
        path_free=True,
        physics_probe=_probe_strict,
    ),
    LeafSpec(
        "L2_operative_summary",
        ("joulewise.whole_window:_member_operative_summary",),
        (("rederive", SCALAR), ("path", TREE), ("authenticated_fiducial_bound_s", SCALAR),
         ("metadata", SCALAR)),
        physics_probe=_probe_operative,
    ),
    LeafSpec(
        "L3_reduce_dict",
        ("joulewise.analysis_verified_store:reduce_bundle_dict",),
        (("path", TREE), ("reducer_version", SCALAR), ("physics_cache", PHYSICS)),
        physics_probe=_probe_explicit(
            "physics_cache", lambda arguments: _calibration_key(_bundle_metadata(arguments["path"]))),
    ),
    LeafSpec(
        "L4_calibration_bracket",
        ("joulewise.calibration_bracketing:calibration_bracket_for_bundles",),
        (("runs_root", SCALAR), ("bundle_paths", TREES), ("policy", SCALAR), ("mode", SCALAR),
         ("ledger_snapshot", SCALAR), ("bracket_binding", SCALAR), ("bracket_window_id", SCALAR),
         ("bracket_plan_id", SCALAR), ("bracket_plan_sha256", SCALAR),
         ("bracket_evidence_root_id", SCALAR), ("diagnostics", SCALAR), ("trigger_scope", SCALAR),
         ("_allow_unissued_fixture", SCALAR)),
        path_free=True,
    ),
    LeafSpec(
        "L5_environment_refusals",
        ("joulewise.environment_admission:current_environment_refusals",),
        (("metadata", SCALAR), ("bundle_path", TREE), ("measured_window_start_s", SCALAR),
         ("measured_window_end_s", SCALAR), ("post_run_collector_raised_unmeasured", SCALAR)),
    ),
    LeafSpec(
        "L6_verify_instrument_calibration",
        ("joulewise.analysis_verified_store:verify_instrument_calibration_at",),
        (("bundle_path", TREE), ("metadata", SCALAR), ("calibration", SCALAR),
         ("strict_physics", SCALAR), ("physics_cache", PHYSICS)),
        physics_probe=_probe_explicit(
            "physics_cache",
            lambda arguments: (arguments["calibration"].get("artifact_sha256")
                               if isinstance(arguments["calibration"], Mapping) else None)),
    ),
)
# L7 (the V2 strict-JSON grammar verdict) is authentication_io's own success-only
# memo, analysis_run_cache.memo(GRAMMAR_VERDICT_MEMO); it is not a stored leaf.

_LEAVES_BY_ID: dict[str, LeafSpec] = {spec.leaf_id: spec for spec in LEAVES}


@contextmanager
def _registered(*specs: LeafSpec) -> Iterator[None]:
    """Tests only: register synthetic leaves for the duration of the block."""

    saved = dict(_LEAVES_BY_ID)
    _LEAVES_BY_ID.update({spec.leaf_id: spec for spec in specs})
    try:
        yield
    finally:
        _LEAVES_BY_ID.clear()
        _LEAVES_BY_ID.update(saved)


# ----------------------------------------------------------------------- entries


@dataclass(frozen=True)
class _TreeRef:
    root: str  # resolved absolute root (consumer side)
    name: str  # identity in the key: the root, or its final name for a path-free leaf
    content_only: bool


@dataclass(frozen=True)
class Entry:
    leaf_id: str
    value: bytes  # pickle
    trees: tuple[tuple[str, str], ...]  # (key identity, digest)
    extras: tuple[tuple[str, str], ...]  # (absolute path, sha256)
    listings: tuple[tuple[str, str], ...]  # (absolute path, names digest)
    extra_trees: tuple[tuple[str, bool, str], ...]  # (absolute root, content_only, digest)
    physics: tuple[tuple[str, Any, Any], ...]  # (cache key, V0, P)
    rows: tuple[tuple[int, str, str, str, str, str], ...] | None  # (tree index or -1, identity, sha, grammar, caller grammar, label)


@dataclass
class _Prepared:
    spec: LeafSpec
    key: str
    arguments: dict[str, Any]
    scalars: bytes
    trees: tuple[_TreeRef, ...]
    verdicts: tuple[TreeVerdict, ...]
    views: list[tuple[Any, str]] = field(default_factory=list)


class _Hit:
    """A verified, not yet applied hit (``probe`` returns one; ``apply`` serves it)."""

    def __init__(self, store: "VerifiedStore", entry: Entry, prepared: _Prepared,
                 views: list[tuple[Any, str]], *, deferred: bool = False) -> None:
        self.store, self.entry, self.prepared, self.views = store, entry, prepared, views
        self.deferred = deferred

    def apply(self) -> Any:
        """Register, insert and return a fresh value; raises ``_Bypass`` if no longer valid."""

        return self.store._apply(self)


_ROOT_MARK = "\0vdl-root\0"


class VerifiedStore:
    """The run's verified derivation store (one per analysis-run activation)."""

    def __init__(self, mode: Mode = ON, *, commit: str | None = None) -> None:
        if not isinstance(mode, Mode):
            raise TypeError("VDL mode must be a Mode")
        self.mode = mode
        self.commit = commit
        self._lock = threading.RLock()
        self._entries: dict[str, Entry] = {}
        self._poisoned: set[str] = set()
        self._served: dict[str, int] = {}
        self._new: set[str] = set()
        self._defects: list[str] = []
        self._counters: dict[str, int] = {}
        self._signatures: dict[Callable[..., Any], inspect.Signature] = {}

    # -- restricted-tier state ------------------------------------------------

    def _count(self, name: str) -> None:
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + 1

    def restricted_counters(self) -> dict[str, int]:
        """Hit/miss/poison/shadow counts: restricted tier only (custody root's restricted/)."""

        with self._lock:
            return dict(self._counters)

    def defect_pending(self) -> bool:
        with self._lock:
            return bool(self._defects)

    def _defect(self, kind: str) -> None:
        with self._lock:
            self._defects.append(kind)

    def check_defects(self) -> None:
        """Raise ``VerifiedStoreDefect`` if any defect was recorded (driver step boundary)."""

        with self._lock:
            if self._defects:
                raise VerifiedStoreDefect(f"verified store defect ({len(self._defects)})")

    # -- key -------------------------------------------------------------------

    def _signature(self, fn: Callable[..., Any]) -> inspect.Signature:
        signature = self._signatures.get(fn)
        if signature is None:
            signature = inspect.signature(fn)
            self._signatures[fn] = signature
        return signature

    def _prepare(self, spec: LeafSpec, fn: Callable[..., Any], args: tuple, kwargs: dict) -> _Prepared:
        reference = f"{getattr(fn, '__module__', None)}:{getattr(fn, '__qualname__', None)}"
        if reference not in spec.qualnames:
            raise _Bypass("not the registered leaf")
        try:
            if _resolve_reference(reference) is not fn:
                raise _Bypass("not the genuine leaf")
        except (ImportError, AttributeError):
            raise _Bypass("unresolvable leaf") from None
        signature = self._signature(fn)
        roles = spec.roles()
        if set(roles) != set(signature.parameters):
            raise _Bypass("leaf signature drifted from its spec")
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        arguments = dict(bound.arguments)
        scalars = canonical_bytes(tuple((name, arguments[name]) for name, role in spec.params if role == SCALAR))
        trees: list[_TreeRef] = []
        for name, role in spec.params:
            if role == TREE:
                values = [arguments[name]]
            elif role == TREES:
                values = list(arguments[name])
            else:
                continue
            for value in values:
                if not isinstance(value, (str, PurePath)):
                    raise _Bypass("tree argument is not a path")
                root = os.fspath(Path(value).resolve(strict=False))
                trees.append(_TreeRef(root, Path(root).name if spec.path_free else root, spec.path_free))
        scope = _current_scope()
        verdicts: list[TreeVerdict] = []
        with _suspended():
            for tree in trees:
                verdict = scope.verify_tree(tree.root, tree.content_only)
                if verdict is None:
                    raise _Bypass("tree not hashable")
                verdicts.append(verdict)
        capability = getattr(_AUTH.module(), "V2AuthenticationPath", None)
        tree_types = tuple(
            "v2-capability" if capability is not None and isinstance(arguments[name], capability) else "path"
            for name, role in spec.params if role == TREE)
        prepared = _Prepared(spec, "", arguments, scalars, tuple(trees), tuple(verdicts))
        prepared.views = self._views(prepared)
        # Which physics entries the call consults (not their values) is call
        # context: a session cache, a run-partition view, or none.
        material = (
            SCHEMA, self.commit, code_digest(), environment_digest(), spec.leaf_id, scalars,
            tree_types, tuple((tree.name, verdict.digest) for tree, verdict in zip(trees, verdicts)),
            tuple(sorted(key for _, key in prepared.views)),
        )
        prepared.key = canonical_digest(material)
        return prepared

    # -- physics ---------------------------------------------------------------

    @staticmethod
    def _peek(view: Any, key: str) -> Any:
        local = getattr(view, "_local", None)
        store = getattr(view, "_store", None)
        partition = getattr(view, "_key", None)
        if isinstance(local, dict) and isinstance(store, dict):
            if key in local:
                return local[key]
            return store.get(partition, {}).get(key, ABSENT)
        if isinstance(view, dict):
            return view.get(key, ABSENT)
        raise _Bypass("unknown physics view")

    @staticmethod
    def _same(left: Any, right: Any) -> bool:
        if left is ABSENT or right is ABSENT:
            return left is right
        return type(left) is type(right) is float and left.hex() == right.hex()

    def _views(self, prepared: _Prepared) -> list[tuple[Any, str]]:
        probe = prepared.spec.physics_probe
        if probe is None:
            return []
        with _suspended():
            views = probe(prepared.arguments)
        keys = [key for _, key in views]
        if len(set(keys)) != len(keys):
            raise _Bypass("duplicate physics keys")
        return views

    # -- the call --------------------------------------------------------------

    def call(self, leaf_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        spec = _LEAVES_BY_ID.get(leaf_id)
        if spec is None or not self.mode.active:
            return fn(*args, **kwargs)
        try:
            prepared = self._prepare(spec, fn, args, kwargs)
        except _Bypass:
            self._count(f"{leaf_id}:bypass")
            return fn(*args, **kwargs)
        except Exception:  # noqa: BLE001 - a store failure never changes the leaf's semantics
            self._count(f"{leaf_id}:bypass")
            return fn(*args, **kwargs)
        hit = self._find(prepared)
        if hit is not None:
            if self.mode.name == "shadow" and int(prepared.key[:8], 16) % 1000 < self.mode.permille:
                return self._shadow(hit, fn, args, kwargs)
            try:
                value = self._apply(hit)
            except Exception:  # noqa: BLE001 - any anomaly: the leaf runs at this position
                self._count(f"{leaf_id}:hit_discarded")
            else:
                self._count(f"{leaf_id}:hit")
                return value
        return self._fill(prepared, fn, args, kwargs)

    def probe(self, leaf_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> _Hit | None:
        """A side-effect-free hit check (for pool pre-filters): no registration, no insert.

        The caller applies the returned hit at the member's serial position
        (``hit.apply()``) and computes the leaf there if that raises.
        """

        spec = _LEAVES_BY_ID.get(leaf_id)
        if spec is None or not self.mode.active:
            return None
        try:
            prepared = self._prepare(spec, fn, args, kwargs)
        except Exception:  # noqa: BLE001 - not servable
            return None
        hit = self._find(prepared)
        if hit is not None:
            hit.deferred = True
        return hit

    def _find(self, prepared: _Prepared) -> _Hit | None:
        with self._lock:
            if prepared.key in self._poisoned:
                return None
            entry = self._entries.get(prepared.key)
        if entry is None:
            self._count(f"{prepared.spec.leaf_id}:miss")
            return None
        try:
            views = self._verify(entry, prepared)
        except Exception:  # noqa: BLE001 - a hit that cannot be verified is a miss
            views = None
        if views is None:
            self._count(f"{prepared.spec.leaf_id}:verify_miss")
            return None
        return _Hit(self, entry, prepared, views)

    def _verify(self, entry: Entry, prepared: _Prepared) -> list[tuple[Any, str]] | None:
        scope = _current_scope()
        with _suspended():
            if not scope.prefetched:
                scope.prefetched = True
                self._prefetch_siblings(scope, prepared)
            for path, digest in entry.extras:
                if scope.verify_file(path) != digest:
                    return None
            for path, digest in entry.listings:
                if scope.verify_listing(path) != digest:
                    return None
            for root, content_only, digest in entry.extra_trees:
                verdict = scope.verify_tree(root, content_only)
                if verdict is None or verdict.digest != digest:
                    return None
        views = prepared.views
        stored = {key: (before, after) for key, before, after in entry.physics}
        if set(stored) != {key for _, key in views}:
            return None
        for view, key in views:
            visible = self._peek(view, key)
            if not (visible is ABSENT or self._same(visible, stored[key][1])):
                return None
        if _AUTH.session() is not None and entry.rows is None:
            return None
        return views

    def _prefetch_siblings(self, scope: _Scope, prepared: _Prepared) -> None:
        if prepared.spec.path_free or not prepared.trees:
            return
        parents = {os.path.dirname(tree.root) for tree in prepared.trees}
        with self._lock:
            roots = sorted({identity for entry in self._entries.values() if not _path_free(entry)
                            for identity, _ in entry.trees if os.path.dirname(identity) in parents})
        scope.prefetch([(root, False) for root in roots])

    @staticmethod
    def _relocate(prepared: _Prepared, index: int, identity: str, label: str) -> tuple[str, str]:
        if index < 0:
            return identity, label
        root = prepared.trees[index].root
        return (os.path.join(root, identity) if identity else root), label.replace(_ROOT_MARK, root)

    def _apply(self, hit: _Hit) -> Any:
        entry, prepared = hit.entry, hit.prepared
        if hit.deferred:
            # Probed earlier (a pool pre-filter): re-verify at the serial position.
            with self._lock:
                if prepared.key in self._poisoned or self._entries.get(prepared.key) is not entry:
                    raise _Bypass("entry changed since the probe")
            scope = _current_scope()
            with _suspended():
                for tree, verdict in zip(prepared.trees, prepared.verdicts):
                    current = scope.verify_tree(tree.root, tree.content_only)
                    if current is None or current.digest != verdict.digest:
                        raise _Bypass("tree changed since the probe")
            if self._verify(entry, prepared) is None:
                raise _Bypass("hit no longer admissible")
        session = _AUTH.session()
        rows: list[_Row] = []
        if entry.rows is not None:
            for index, identity, digest, grammar, caller_grammar, label in entry.rows:
                identity, label = self._relocate(prepared, index, identity, label)
                rows.append(_Row(identity, digest, grammar, caller_grammar, label))
        if session is not None:
            if entry.rows is None:
                raise _Bypass("rows incomplete for a session")
            self._bridge(session, rows, prepared)
        value = pickle.loads(entry.value)
        for view, key in hit.views:
            stored = {k: after for k, _, after in entry.physics}[key]
            if self._peek(view, key) is ABSENT and stored is not ABSENT:
                view[key] = stored
        with self._lock:
            self._served[prepared.key] = self._served.get(prepared.key, 0) + 1
        self._forward(entry, prepared, rows)
        return value

    def _bridge(self, session: Any, rows: list[_Row], prepared: _Prepared) -> None:
        """Grammar verdicts under the consumer's grammar, then pre-checked registration."""

        effective: list[str] = []
        scope = _current_scope()
        with _suspended():
            for row in rows:
                grammar = _AUTH.forced_grammar(row.identity, row.caller_grammar)
                if grammar in ("json", "jsonl"):
                    if row.identity.startswith("git:"):
                        raise _Bypass("git rows are not re-readable here")
                    raw = Path(row.identity).read_bytes()
                    digest = hashlib.sha256(raw).hexdigest()
                    if digest != row.sha256 or scope.verify_file(row.identity) != row.sha256:
                        raise _Bypass("row bytes changed")
                    grammar = _AUTH.ensure_verdict(session, row.identity, raw, digest, row.caller_grammar, row.label)
                effective.append(grammar)
        with session._lock:
            known = dict(session._records)
            pending: dict[str, tuple[str, str]] = {}
            for row, grammar in zip(rows, effective):
                previous = known.get(row.identity)
                first = (previous.sha256, previous.grammar) if previous is not None else pending.get(row.identity)
                if first is not None and first != (row.sha256, grammar):
                    raise _Bypass("row conflicts with the session's first read")
                pending.setdefault(row.identity, (row.sha256, grammar))
            for row, grammar in zip(rows, effective):
                session._register(row.identity, row.sha256, grammar, row.label)

    def _forward(self, entry: Entry, prepared: _Prepared, rows: list[_Row]) -> None:
        fills = _FILLS.get()
        if not fills:
            return
        trees = [(tree.root, tree.content_only, verdict.digest)
                 for tree, verdict in zip(prepared.trees, prepared.verdicts)]
        for fill in fills:
            fill.forwarded_trees.extend(trees)
            fill.forwarded_trees.extend(entry.extra_trees)
            fill.forwarded_extras.extend(entry.extras)
            fill.forwarded_listings.extend(entry.listings)
        if rows:
            _AUTH.forward_rows(rows)

    # -- shadow -----------------------------------------------------------------

    def _shadow(self, hit: _Hit, fn: Callable[..., Any], args: tuple, kwargs: dict) -> Any:
        """Recompute a sampled hit at its position; the fresh value is what the caller gets."""

        leaf_id = hit.prepared.spec.leaf_id
        self._count(f"{leaf_id}:shadow")
        outcome: dict[str, Any] = {}
        try:
            value = self._fill(hit.prepared, fn, args, kwargs, outcome=outcome)
        except BaseException:
            if not isinstance(sys.exc_info()[1], (KeyboardInterrupt, SystemExit)):
                self._count(f"{leaf_id}:shadow_mismatch")
                self._defect(f"{leaf_id}:shadow_raised")
                with self._lock:
                    self._poisoned.add(hit.prepared.key)
            raise
        if not outcome.get("comparable"):
            self._count(f"{leaf_id}:shadow_incomparable")
            return value
        stored_physics = {key: after for key, _, after in hit.entry.physics}
        same_physics = all(self._same(stored_physics.get(key, ABSENT), after)
                           for key, after in outcome.get("physics", {}).items())
        if not _same_value(outcome.get("value"), hit.entry.value) or not same_physics:
            self._count(f"{leaf_id}:shadow_mismatch")
            self._defect(f"{leaf_id}:shadow_mismatch")
            with self._lock:
                self._poisoned.add(hit.prepared.key)
        return value

    # -- fill ---------------------------------------------------------------------

    def _fill(self, prepared: _Prepared, fn: Callable[..., Any], args: tuple, kwargs: dict,
              *, outcome: dict[str, Any] | None = None) -> Any:
        from joulewise import analysis_run_cache

        leaf_id = prepared.spec.leaf_id
        caches = analysis_run_cache.current()
        deadline = getattr(caches, "deadline", None)
        firings_before = getattr(deadline, "firings", None)
        unavailable_before = bool(getattr(caches, "worker_observer_unavailable", False))
        storable = deadline is not None and isinstance(firings_before, int) and not unavailable_before
        try:
            views = prepared.views
            before = [self._peek(view, key) for view, key in views]
            dicts = _physics_dicts(prepared, views)
            physics_before = [(item, dict(item)) for item in dicts]
        except Exception:  # noqa: BLE001 - an unprobeable call is computed, never stored
            views, before, physics_before, storable = [], [], [], False
        session = _AUTH.session()
        snapshot = None
        if session is not None:
            with session._lock:
                snapshot = {identity: record.read_count for identity, record in session._records.items()}
        fill = _Fill()
        _install_hook()
        token = _FILLS.set(_FILLS.get() + (fill,))
        try:
            with _AUTH.recording() as recorded:
                value = fn(*args, **kwargs)
        finally:
            _FILLS.reset(token)
        if not storable:
            self._count(f"{leaf_id}:unstorable")
            return value
        try:
            entry = self._entry(prepared, fill, value, views, before, session, snapshot, recorded,
                                caches, deadline, firings_before, physics_before)
        except _Bypass:
            entry = None
        except Exception:  # noqa: BLE001 - a store failure never changes the leaf's value
            entry = None
        if entry is None:
            self._count(f"{leaf_id}:unstorable")
            return value
        if outcome is not None:
            outcome["comparable"] = True
            outcome["value"] = entry.value
            outcome["physics"] = {key: after for key, _, after in entry.physics}
            return value
        self._insert(prepared.key, entry)
        self._count(f"{leaf_id}:fill")
        return value

    def _entry(self, prepared: _Prepared, fill: _Fill, value: Any, views: list[tuple[Any, str]],
               before: list[Any], session: Any, snapshot: dict[str, int] | None, recorded: Any,
               caches: Any, deadline: Any, firings_before: int,
               physics_before: list[tuple[dict, dict]]) -> Entry | None:
        if fill.clock or fill.unstorable:
            return None
        if getattr(deadline, "firings", None) != firings_before or getattr(caches, "deadline", None) is not deadline:
            return None
        if getattr(caches, "worker_observer_unavailable", False):
            return None
        with _suspended():
            if canonical_bytes(tuple((name, prepared.arguments[name]) for name, role in prepared.spec.params
                                     if role == SCALAR)) != prepared.scalars:
                return None
            for tree, verdict in zip(prepared.trees, prepared.verdicts):
                walk = _walk(tree.root)
                if walk is None or walk.signature != verdict.signature:
                    return None
            allowed = {key for _, key in views}
            for item, copy in physics_before:
                changed = {key for key in set(item) | set(copy)
                           if key not in copy or key not in item or not _unchanged(copy[key], item[key])}
                if not changed <= allowed:
                    return None
            for view, _ in views:
                store, partition = getattr(view, "_store", None), getattr(view, "_key", None)
                if isinstance(store, dict) and all(store.get(partition) is not item for item, _ in physics_before):
                    created = store.get(partition)
                    if isinstance(created, dict) and not set(created) <= allowed:
                        return None
            physics: list[tuple[str, Any, Any]] = []
            for (view, key), visible_before in zip(views, before):
                after = self._peek(view, key)
                if after is not ABSENT and type(after) is not float:
                    return None
                if visible_before is not ABSENT and not self._same(visible_before, after):
                    return None
                physics.append((key, visible_before, after))
            extras, listings, extra_trees = self._classify(prepared, fill, recorded)
            rows = self._rows(prepared, session, snapshot, recorded)
            try:
                payload = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
            except Exception:  # noqa: BLE001 - an unpicklable value is not stored
                return None
            if prepared.spec.path_free:
                for tree in prepared.trees:
                    for needle in (tree.root, os.path.dirname(tree.root)):
                        if needle and needle != os.sep and needle.encode("utf-8", "surrogatepass") in payload:
                            return None
        return Entry(
            prepared.spec.leaf_id, payload,
            tuple((tree.name, verdict.digest) for tree, verdict in zip(prepared.trees, prepared.verdicts)),
            extras, listings, extra_trees, tuple(physics), rows,
        )

    def _classify(self, prepared: _Prepared, fill: _Fill, recorded: Any):
        roots = [tree.root for tree in prepared.trees]
        code = _code_roots()
        package = os.fspath(_PACKAGE_ROOT)
        scope = _current_scope()

        def within(path: str, root: str) -> bool:
            return path == root or path.startswith(root.rstrip(os.sep) + os.sep)

        def is_code(path: str) -> bool:
            if any(within(path, root) for root in code):
                return True
            return within(path, package) and (path.endswith((".py", ".pyc")) or "__pycache__" in path
                                              or os.path.isdir(path))

        parents = {os.path.dirname(root) for root in roots} if prepared.spec.path_free else set()
        nofollow: set[str] = set()
        for row in recorded or ():
            relative = getattr(row, "relative", None)
            identity = getattr(row, "identity", None)
            if relative:
                nofollow.update(Path(relative).parts)
                if identity:
                    fill.reads.append(identity)
                    nofollow.add(os.fspath(Path(identity).parent))
            elif getattr(row, "identity", None) is None:
                raise _Bypass("unattributable authentication read")
        for name in fill.relative_opens:
            if name not in nofollow:
                raise _Bypass("unattributable relative open")
        extras: dict[str, str] = {}
        for path in fill.reads:
            resolved = os.path.realpath(path)
            if any(within(path, root) or within(resolved, root) for root in roots) or is_code(resolved):
                continue
            if os.path.isdir(resolved):
                continue
            if any(within(resolved, parent) for parent in parents):
                raise _Bypass("path-free leaf read beside its tree")
            digest = scope.verify_file(resolved)
            if digest is None:
                raise _Bypass("extra read not hashable")
            extras[resolved] = digest
        for row in recorded or ():
            identity = getattr(row, "identity", None)
            if identity and not identity.startswith("git:") and identity in extras:
                if getattr(row, "sha256", None) != extras[identity]:
                    raise _Bypass("extra read changed during the fill")
        listings: dict[str, str] = {}
        for path in fill.listings:
            resolved = os.path.realpath(path)
            if any(within(resolved, root) for root in roots) or is_code(resolved):
                continue
            if any(within(resolved, parent) or resolved == parent for parent in parents):
                raise _Bypass("path-free leaf listed beside its tree")
            digest = scope.verify_listing(resolved)
            if digest is None:
                raise _Bypass("listing not hashable")
            listings[resolved] = digest
        for path, digest in fill.forwarded_extras:
            if extras.setdefault(path, digest) != digest:
                raise _Bypass("forwarded extra disagrees")
        for path, digest in fill.forwarded_listings:
            if listings.setdefault(path, digest) != digest:
                raise _Bypass("forwarded listing disagrees")
        extra_trees = {}
        for root, content_only, digest in fill.forwarded_trees:
            if any(within(root, own) for own in roots):
                continue
            if any(within(root, parent) for parent in parents):
                raise _Bypass("path-free leaf used a tree beside its own")
            if extra_trees.setdefault((root, content_only), digest) != digest:
                raise _Bypass("forwarded tree disagrees")
        return (tuple(sorted(extras.items())), tuple(sorted(listings.items())),
                tuple(sorted((root, content_only, digest) for (root, content_only), digest in extra_trees.items())))

    def _rows(self, prepared: _Prepared, session: Any, snapshot: dict[str, int] | None, recorded: Any):
        """The V2 registration rows a session would hold after the leaf, or None (session use barred)."""

        rows: list[_Row] = []
        if session is not None:
            with session._lock:
                after = list(session._records.items())
            delta: dict[str, int] = {}
            for identity, record in after:
                increase = record.read_count - (snapshot or {}).get(identity, 0)
                if increase > 0:
                    delta[identity] = increase
            api_rows = [row for row in recorded or () if getattr(row, "in_session", False)]
            counted: dict[str, int] = {}
            for row in api_rows:
                counted[row.identity] = counted.get(row.identity, 0) + 1
            records = dict(after)
            if api_rows and counted == delta and all(
                    records[row.identity].sha256 == row.sha256 and records[row.identity].grammar == row.grammar
                    for row in api_rows):
                rows = [_Row(row.identity, row.sha256, row.grammar, row.caller_grammar, row.label)
                        for row in api_rows]
            else:
                for identity, increase in delta.items():
                    record = records[identity]
                    rows.extend(_Row(identity, record.sha256, record.grammar, record.grammar,
                                     f"member derivation input {identity}") for _ in range(increase))
        else:
            if recorded is None or not _AUTH.capability_complete():
                return None
            for row in recorded:
                if getattr(row, "identity", None) is None:
                    return None
                rows.append(_Row(row.identity, row.sha256, row.grammar, row.caller_grammar, row.label))
        stored = []
        for row in rows:
            index, identity = -1, row.identity
            for position, tree in enumerate(prepared.trees):
                if row.identity == tree.root or row.identity.startswith(tree.root.rstrip(os.sep) + os.sep):
                    index = position
                    identity = os.path.relpath(row.identity, tree.root) if row.identity != tree.root else ""
                    break
            if index < 0 and prepared.spec.path_free and not row.identity.startswith("git:"):
                for tree in prepared.trees:
                    if row.identity.startswith(os.path.dirname(tree.root).rstrip(os.sep) + os.sep):
                        raise _Bypass("path-free leaf registered a read beside its tree")
            label = row.label
            if index >= 0:
                label = label.replace(prepared.trees[index].root, _ROOT_MARK)
            stored.append((index, identity, row.sha256, row.grammar, row.caller_grammar, label))
        return tuple(stored)

    # -- insert-once, export, merge ------------------------------------------------

    def _insert(self, key: str, entry: Entry) -> None:
        with self._lock:
            if key in self._poisoned:
                return
            current = self._entries.get(key)
            if current is None:
                self._entries[key] = entry
                self._new.add(key)
                return
            same_post = _posts(current) == _posts(entry)
            if not same_post:
                return  # a different physics post-value: a different computation, keep the first
            if _same_value(current.value, entry.value):
                if current.rows is None and entry.rows is not None:
                    self._entries[key] = entry
                    self._new.add(key)
                return
            self._poison(key)

    def _poison(self, key: str) -> None:
        self._poisoned.add(key)
        self._entries.pop(key, None)
        self._new.discard(key)
        self._count("poison")
        if self._served.get(key):
            self._defects.append("poisoned_after_serving")

    def export_entries(self, selector: Callable[[str, Entry], bool] | None = None,
                       *, new_only: bool = False) -> dict[str, Any]:
        """A picklable payload for SHIP: entries (optionally only new ones), poison and defects."""

        with self._lock:
            keys = self._new if new_only else self._entries
            entries = {key: self._entries[key] for key in list(keys)
                       if key in self._entries and (selector is None or selector(key, self._entries[key]))}
            return {"schema": SCHEMA, "entries": entries, "poisoned": sorted(self._poisoned),
                    "defects": list(self._defects)}

    def merge_entries(self, payload: Mapping[str, Any]) -> None:
        """Merge an export: never overwrites; disagreement poisons; defects always carry."""

        if not isinstance(payload, Mapping) or payload.get("schema") != SCHEMA:
            return
        with self._lock:
            for defect in payload.get("defects", ()):
                if isinstance(defect, str):
                    self._defects.append(defect)
            for key in payload.get("poisoned", ()):
                if isinstance(key, str) and key not in self._poisoned:
                    self._poison(key)
            for key, entry in dict(payload.get("entries", {})).items():
                if isinstance(key, str) and isinstance(entry, Entry):
                    self._insert(key, entry)
                    self._new.discard(key)


def _strict_equal(left: Any, right: Any) -> bool:
    """Exact structural equality: same types, same order, floats bit for bit."""

    if type(left) is not type(right):
        return False
    if isinstance(left, float):
        return left.hex() == right.hex()
    if isinstance(left, Mapping):
        return (list(left) == list(right)
                and all(_strict_equal(left[key], right[key]) for key in left))
    if isinstance(left, (list, tuple)):
        return len(left) == len(right) and all(_strict_equal(a, b) for a, b in zip(left, right))
    if is_dataclass(left) and not isinstance(left, type):
        return all(_strict_equal(getattr(left, item.name), getattr(right, item.name)) for item in fields(left))
    try:
        return bool(left == right)
    except Exception:  # noqa: BLE001 - incomparable values are not equal
        return False


def _same_value(left: bytes, right: bytes) -> bool:
    if left == right:
        return True
    try:
        return _strict_equal(pickle.loads(left), pickle.loads(right))
    except Exception:  # noqa: BLE001 - unreadable values are not equal
        return False


def _unchanged(before: Any, after: Any) -> bool:
    if before is after:
        return True
    return type(before) is type(after) is float and before.hex() == after.hex()


def _posts(entry: Entry) -> dict[str, str]:
    return {key: ("ABSENT" if after is ABSENT else after.hex()) for key, _, after in entry.physics}


def _physics_dicts(prepared: _Prepared, views: list[tuple[Any, str]]) -> list[dict]:
    """Every dict a physics insert could land in: physics arguments and the views' layers."""

    found: list[dict] = []
    for name, role in prepared.spec.params:
        value = prepared.arguments.get(name)
        if role == PHYSICS and isinstance(value, dict):
            found.append(value)
    for view, _ in views:
        local = getattr(view, "_local", None)
        store = getattr(view, "_store", None)
        if isinstance(local, dict) and isinstance(store, dict):
            found.append(local)
            partition = store.get(getattr(view, "_key", None))
            if isinstance(partition, dict):
                found.append(partition)
        elif isinstance(view, dict):
            found.append(view)
    unique: dict[int, dict] = {}
    for item in found:
        unique.setdefault(id(item), item)
    return list(unique.values())


def _path_free(entry: Entry) -> bool:
    spec = _LEAVES_BY_ID.get(entry.leaf_id)
    return spec is None or spec.path_free


def active_store() -> VerifiedStore | None:
    from joulewise import analysis_run_cache

    caches = analysis_run_cache.current()
    return None if caches is None else getattr(caches, "vdl", None)


def call(leaf_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """The leaf's value at this position: verified from the store, or ``fn(*args, **kwargs)``."""

    store = active_store()
    if store is None:
        return fn(*args, **kwargs)
    return store.call(leaf_id, fn, *args, **kwargs)


def probe(leaf_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> _Hit | None:
    store = active_store()
    return None if store is None else store.probe(leaf_id, fn, *args, **kwargs)


def check_defects() -> None:
    store = active_store()
    if store is not None:
        store.check_defects()
