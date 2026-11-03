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
leaf id, the leaf's scalar arguments, for every tree argument its resolved
path (or, for a path-free leaf, its final name) together with the caller's
absolute spelling when that differs (a leaf may build a value from the
spelling it was given), its tree digest, and whether a V2 session is active.

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
the leaf returned normally; no V2AuthenticationInputError was raised inside it,
even if the leaf caught it (observed by a sys.monitoring RAISE callback, or by
AUTH-IO failure rows; with neither, nothing is stored); the run's wall-deadline
firings did not change and the observer was available;
``note_clock()``/``note_unstorable()`` was not called inside it; the recorder saw no write-mode open, file mutation,
subprocess, thread start, chdir or network use; every read and listing could be
attributed (an ``os.open`` of a relative name, as the no-follow ``dir_fd`` walk
makes, is attributed only through an authentication_io no-follow row); the
scalar arguments are unchanged by the call; every tree's lstat signature is
unchanged across the call; the physics view behaves as the J2 premise needs.
Reads outside the leaf's trees and outside the Python installation and the
``joulewise`` sources are kept as (path, sha256) extras, and listings as name
digests; both are re-verified on every hit (cached per scope, lstat-guarded).
Each is bound to the pathname the leaf used (Sol wave-2 #2): a pathname that
is not its own target is kept as an alias and re-resolved on every hit, and a
read into a tree through any pathname but one of that tree's spellings is
unstorable. A path-free leaf's value must
not contain any spelling of its tree's location or parent (searched in the
pickled bytes and in every string and path inside the value).

V2 authentication rows. An entry carries the V2 registration rows a session
would hold after the leaf: from the session's own record delta for an
in-session fill, and from authentication_io's read recorder for a session-less
fill only when that recorder declares it represents capability
(``V2AuthenticationPath``) reads too (``RECORDS_CAPABILITY_READS``), and only
when that recording scope is not marked ``unrepresented`` (a session entered
inside the fill, a session-presence query the store does not represent, a
text read a session would decode differently), no hit served inside the fill
lacked rows, and the value holds no capability path. Otherwise the entry
cannot serve a call inside a session. A hit inside a session first
obtains, for every json/jsonl row, a grammar verdict under the consumer's own
effective grammar and vocabulary flag (``_parse_strict`` on the just re-read
and re-hashed bytes, through authentication_io's depth-aware
``bridged_grammar_verdict``); any failure discards the hit and the leaf runs in
the session, so the same V2 refusal fires at the same read. Every row carries
the depth of its read's parse below the fill (``_Row.depth``); the verdict is
decided for the depth the serial read would parse at (the consumer's headroom
less that depth), and a verdict that may depend on the stack there (a read
near the recursion limit, bytes the memo marks stack-dependent) is not served
(D-188 AUTH-IO-2). A recording twin argument is keyed as a capability only
outside a session. The rows are then pre-checked against
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
admitted only if the caller's visible value V is ABSENT or equals P exactly.
D-188 VDL-FIX (Sol wave-2 #1): a fill also records, per key, what its leaf
provably did to every caller-visible layer (a run view's local dict and its
run partition, or a plain dict; ``_PHYSICS_KINDS``), and a hit replays
exactly the serial effect for the caller's current layers: a partition entry
promoted into an empty local dict, P written where nothing is visible only
after a fill that fitted P itself, nothing otherwise; where the serial effect
is not determined by the fill, the hit is declined and the leaf runs.

Shadow. A sampled hit is first served by the identical ``_apply`` into a
scratch copy of the consumer's session (no real registration, no insert); if
that refuses, the call is a plain miss, exactly as in ``on`` mode. Otherwise the
leaf runs in the real session and its value, physics and resulting session
records are compared with what serving the hit produced.

Defects. Nothing in this module raises into a caller's ``except`` clauses: a
hit anomaly falls through to the leaf, a poisoned key (two fills disagree) falls
back to the leaf, and a shadow mismatch returns the freshly computed value and
sets a run-level defect flag. ``check_defects()`` raises ``VerifiedStoreDefect``
(a ``BaseException``) and is meant for the driver's step boundaries, outside
every leaf; the flag also travels in ``export_entries`` payloads. On a blind
(real) run (``BLIND_ON``, what ``resolve_mode`` gives for real data) a defect is
never raised: it is counted in the restricted tier and the store stops serving
for the rest of the run (lead ruling: no new refusal path on real data).

Blinding. Hit, miss, poison and shadow counts live only in process memory and
are read only through ``restricted_counters()``, for the custody root's
restricted tier. This module prints and logs nothing.
"""
from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import contextmanager, nullcontext
import contextvars
import copy
from dataclasses import dataclass, field, fields, is_dataclass, replace
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
    # A real blind run: a store defect never becomes a refusal there (lead
    # ruling, no new refusal path on real data); it is counted in the
    # restricted tier and the store stops serving for the rest of the run.
    blind: bool = False

    @property
    def active(self) -> bool:
        return self.name != "off"


OFF = Mode("off")
ON = Mode("on")
BLIND_ON = Mode("on", blind=True)


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
    real data): there an unset value, ``on`` or a shadow request all run
    ``BLIND_ON`` (defects counted in the restricted tier, never raised), and a
    malformed value runs ``off`` (the R2 behaviour).
    """

    if raw is None:
        return Mode("shadow", 1000) if synthetic else BLIND_ON
    if synthetic:
        return parse_mode(raw)
    try:
        mode = parse_mode(raw)
    except ValueError:
        return OFF
    return OFF if mode.name == "off" else BLIND_ON


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
        self.v2_failed = False  # a V2AuthenticationInputError, RecursionError or MemoryError was raised inside
        self.reads: list[str] = []
        self.relative_opens: list[str] = []
        self.listings: list[str] = []
        self.forwarded_trees: list[tuple[str, bool, str]] = []
        self.forwarded_extras: list[tuple[str, str]] = []
        self.forwarded_listings: list[tuple[str, str]] = []
        self.forwarded_aliases: list[tuple[str, str]] = []
        # A hit served inside this fill carried no session rows: this fill's
        # rows cannot stand for a session's either.
        self.rows_incomplete = False
        # ``_stack_headroom`` at the ``_fill`` frame (the leaf runs one below).
        self.headroom: int | None = None


_FILLS: contextvars.ContextVar[tuple[_Fill, ...]] = contextvars.ContextVar("joulewise_vdl_fills", default=())
_SUSPENDED: contextvars.ContextVar[bool] = contextvars.ContextVar("joulewise_vdl_suspended", default=False)
_HOOK_INSTALLED = [False]
_HOOK_LOCK = threading.Lock()
_IN_HOOK = threading.local()


class _DepthUnknown(Exception):
    """A row's read depth is unknown: its entry cannot serve a session."""


def _stack_headroom() -> int:
    """Python frames the caller may still push before ``RecursionError``.

    The same measure as ``authentication_io._python_stack_headroom``: the
    recursion limit minus the depth of the caller's frame chain. ``_fill``
    and ``_apply`` take it at their own frames so a row's depth below the
    fill can be replayed below the consumer (D-188 AUTH-IO-2).
    """

    depth = 0
    frame = sys._getframe(1)
    while frame is not None:
        depth += 1
        frame = frame.f_back
    return sys.getrecursionlimit() - depth


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
            # The leaf's own pathname, exactly as spelled: no lexical
            # normalization (a ``..`` after a symlink is the kernel's to
            # resolve), and a relative spelling stays relative so that a hit
            # re-resolves it against the cwd of the hit (review of #639).
            for fill in fills:
                fill.reads.append(path)
        elif event in ("os.listdir", "os.scandir"):
            path = args[0] if args else None
            if path is None:
                path = "."
            if isinstance(path, bytes):
                path = os.fsdecode(path)
            if not isinstance(path, str):
                _mark(fills, "unattributable_listing")
                return
            for fill in fills:
                fill.listings.append(path)
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


# A leaf may catch a V2 read failure and return normally (a "refused" value).
# Whether such a read fails can depend on session presence or session state
# (an earlier conflicting registration, the vocabulary flag), which the key
# does not carry, and a failed read leaves no registration row for the bridge
# to re-check. So a fill inside which any V2AuthenticationInputError was raised
# is never stored. Nor is one inside which a RecursionError or MemoryError was
# raised (a leaf may catch those too): whether they fire depends on the stack
# depth or the memory at the call, which the key does not carry either (D-188
# AUTH-IO-2, review of #638). The raise is observed with a sys.monitoring RAISE
# callback (enabled only while a fill is active); without one (no sys.monitoring, or
# fewer than three free tool ids, so the wall-deadline observer always finds
# one) a fill is storable only if the AUTH-IO recorder declares that it emits a
# ``failed`` row for every raised read (``RECORDS_FAILURES``).
_RAISE_MONITOR: dict[str, Any] = {"tool": None, "active": 0, "error": None}
_RAISE_LOCK = threading.Lock()
_RAISE_TOOL_NAME = "joulewise-vdl-v2-failure-observer"


def _on_raise(_code: Any, _offset: int, exception: BaseException) -> None:
    fills = _FILLS.get()
    if fills and isinstance(exception, _RAISE_MONITOR["error"]):
        for fill in fills:
            fill.v2_failed = True


def _raise_monitor_enter() -> bool:
    """Count one active fill; true when V2 raises inside it are observed."""

    monitoring = getattr(sys, "monitoring", None)
    if monitoring is None:
        return False
    with _RAISE_LOCK:
        try:
            if _RAISE_MONITOR["tool"] is None:
                error = getattr(_AUTH.module(), "V2AuthenticationInputError", None)
                if not (isinstance(error, type) and issubclass(error, BaseException)):
                    return False
                free = [tool for tool in range(6) if monitoring.get_tool(tool) is None]
                if len(free) < 3:
                    return False
                tool = free[-1]  # the observer scans from 0: never contend for its id
                monitoring.use_tool_id(tool, _RAISE_TOOL_NAME)
                _RAISE_MONITOR["error"] = (error, RecursionError, MemoryError)
                monitoring.register_callback(tool, monitoring.events.RAISE, _on_raise)
                _RAISE_MONITOR["tool"] = tool
            tool = _RAISE_MONITOR["tool"]
            if monitoring.get_tool(tool) != _RAISE_TOOL_NAME:
                _RAISE_MONITOR["tool"] = None
                _RAISE_MONITOR["active"] = 0
                return False
            if _RAISE_MONITOR["active"] == 0:
                monitoring.set_events(tool, monitoring.events.RAISE)
            _RAISE_MONITOR["active"] += 1
            return True
        except (AttributeError, RuntimeError, ValueError):
            return False


def _raise_monitor_exit() -> None:
    monitoring = getattr(sys, "monitoring", None)
    with _RAISE_LOCK:
        tool = _RAISE_MONITOR["tool"]
        if monitoring is None or tool is None or _RAISE_MONITOR["active"] <= 0:
            return
        _RAISE_MONITOR["active"] -= 1
        if _RAISE_MONITOR["active"] == 0:
            try:
                monitoring.set_events(tool, 0)
            except (RuntimeError, ValueError):
                pass


# ------------------------------------------------------ authentication_io adapter


class _AuthAdapter:
    """The minimal AUTH-IO interface this store codes against (see the PR).

    * ``recording_authentication_reads()``: a context manager yielding a list
      that receives one row per successful authentication_io read (attributes
      api, identity, sha256, grammar, caller_grammar, label, in_session,
      relative); absent: no rows.
    * ``RECORDS_CAPABILITY_READS``: true only when session-less recording also
      represents every read an active session would register (capability-path
      reads, pinned no-follow reads, git ingests); absent: false. The yielded
      list may carry ``unrepresented`` (a non-empty list when the scope's
      session-less code does not stand for a session's: a session entered
      inside it, an unrepresented session-presence query, a text read whose
      session decode differs); such a fill never serves a session.
    * ``RECORDS_FAILURES``: true only when the recorder also appends a row with
      a true ``failed`` attribute for every read that raised; absent: false
      (the store then relies on its own RAISE observer).
    * ``bridged_grammar_verdict`` on the session or module: the identical
      ``_parse_strict`` behind the success-only memo, decided for the serial
      read's stack headroom (rows carry ``parse_headroom``); it declines
      (returns a false value) where the verdict may depend on the stack.
      Absent: a json/jsonl row is never served into a session.
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

    def records_failures(self) -> bool:
        """Whether the recorder emits a row with a true ``failed`` for every raised read."""

        return bool(getattr(self.module(), "RECORDS_FAILURES", False))

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
                       caller_grammar: str, label: str, read_headroom: int | None) -> str | None:
        """The consumer's effective grammar if a serial read at ``read_headroom`` would pass.

        Raises exactly the grammar refusal ``session.read`` would raise for
        these bytes and label. Returns None when the verdict may depend on the
        stack (a serial read near the recursion limit, bytes the memo marks
        stack-dependent), or when authentication_io offers no depth-aware
        verdict: the hit is then not served. ``read_headroom`` is a lower bound
        on the headroom of the serial read's parse, or None when the serial
        computation runs no parse at this position.
        """

        bridge = getattr(session, "bridged_grammar_verdict", None)
        if callable(bridge):
            return bridge(identity, raw, caller_grammar=caller_grammar, label=label, sha256=digest,
                          read_headroom=read_headroom)
        verdict = getattr(self.module(), "bridged_grammar_verdict", None)
        if not callable(verdict):
            return None
        effective = self.module()._forced_grammar(identity, caller_grammar)
        flag = self.vocabulary_flag(session, identity)
        return effective if verdict(raw, digest, effective, flag, label, read_headroom=read_headroom) else None

    def forward_rows(self, rows: Sequence["_Row"], headroom: int) -> None:
        """Hand a hit's rows to any enclosing authentication_io recorder, in order.

        Each forwarded row's ``parse_headroom`` is ``headroom`` (taken in
        ``_apply``) less the row's depth below its own fill: a lower bound on
        where the replaced read would have parsed.
        """

        module = self.module()
        holder = getattr(module, "_READ_RECORDER", None)
        row_type = getattr(module, "AuthenticationReadRow", None)
        sinks = None if holder is None else holder.get()
        if not sinks or row_type is None:
            return
        for row in rows:
            parse_headroom = None if row.depth is None else headroom - row.depth
            record = row_type(api="vdl.hit", identity=row.identity, sha256=row.sha256,
                              grammar=row.grammar, caller_grammar=row.caller_grammar, label=row.label,
                              in_session=True, grammar_verified=False, vocabulary_flag=False,
                              parse_headroom=parse_headroom)
            for sink in sinks:
                sink.append(record)


_AUTH = _AuthAdapter()


@dataclass(frozen=True)
class _Row:
    """One V2 registration: (identity, sha256, effective grammar, caller grammar, label, depth).

    ``depth`` is an upper bound on how many frames below the frame that took
    the reference headroom (``_fill``; ``_apply`` for a served hit) the
    serial read's strict parse runs, or None when the serial computation runs
    no parse at this position (a registration replayed from elsewhere).
    """

    identity: str
    sha256: str
    grammar: str
    caller_grammar: str
    label: str
    depth: int | None = None


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
            # The leaf builds its own view over a fresh local dict: only the
            # run partition is caller-visible (VDL-FIX: a private local layer).
            view = physics_cache_for_call(_PrivateLocal(), metadata)
            if not hasattr(view, "_store"):
                view = None  # no run partition: the leaf's own cache is None, as before
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
    view = physics_cache_for_call(_PrivateLocal(), arguments["metadata"])
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
    # Identity in the key. A leaf may build values from the caller's own
    # spelling of the path (not the resolved one), so the key carries the
    # absolute spelling too when it differs: ``spelled\0root``, or for a
    # path-free leaf ``spelled-name\0root-name`` (only the final names).
    name: str
    content_only: bool
    spellings: tuple[str, ...] = ()  # every spelling a value could embed (leak guard)


def _identity_root(identity: str) -> str:
    """The resolved root of a non-path-free key identity."""

    return identity.rsplit("\0", 1)[-1]


@dataclass(frozen=True)
class Entry:
    leaf_id: str
    value: bytes  # pickle
    trees: tuple[tuple[str, str], ...]  # (key identity, digest)
    extras: tuple[tuple[str, str], ...]  # (absolute path, sha256)
    listings: tuple[tuple[str, str], ...]  # (absolute path, names digest)
    extra_trees: tuple[tuple[str, bool, str], ...]  # (absolute root, content_only, digest)
    physics: tuple[tuple[str, Any, Any], ...]  # (cache key, V0, P)
    # (tree index or -1, identity, sha, grammar, caller grammar, label, parse depth below the fill or None)
    rows: tuple[tuple[int, str, str, str, str, str, int | None], ...] | None
    # D-188 VDL-FIX (Sol wave-2 #1): per physics key, what the fill's leaf
    # provably did to the caller-visible layers (``_PHYSICS_KINDS``). A key
    # with no kind is ``opaque``.
    physics_kinds: tuple[tuple[str, str], ...] = ()
    # D-188 VDL-FIX (Sol wave-2 #2): (original absolute pathname, resolved
    # target) of every extra read or listing whose pathname is not its own
    # target; each binding is re-checked on every hit.
    aliases: tuple[tuple[str, str], ...] = ()


# What a fill's leaf did to one physics key, from the caller-visible layers
# (a run view's own local dict and its run partition; a plain dict) before
# and after it. The reducer's only operations on a physics cache are
# ``get(key)`` (a run view copies a partition entry into its local dict) and,
# after a ``get`` that found nothing and a successful fresh fit, ``cache[key] =
# bound`` (a run view writes local and partition).
#   absent    nothing visible before or after: nothing to replay.
#   set       nothing visible before, P after: the leaf consulted the key and
#             fitted P on these very bytes. A hit promotes a partition entry
#             into an empty local layer, or writes P where nothing is visible.
#   promote   local empty, partition P: the leaf consulted and promoted. A hit
#             promotes where the local layer is empty and the partition holds
#             P; with nothing visible it is declined (no fit was observed).
#   noconsult local empty, partition P, unchanged: the leaf never consulted
#             the key. A hit changes nothing.
#   opaque    a visible value nothing changed, consulting unknown. A hit is
#             served only where a caller-visible value is already in front
#             (the serial ``get`` then changes nothing); otherwise declined.
_PHYSICS_KINDS = ("absent", "set", "promote", "noconsult", "opaque")
_KIND_RANK = {"opaque": 0, "promote": 1, "set": 2, "noconsult": 2, "absent": 2}


class _PrivateLocal(dict):
    """A probe's own local layer for a view the leaf rebuilds itself: no caller sees it."""


@dataclass
class _Prepared:
    spec: LeafSpec
    key: str
    arguments: dict[str, Any]
    scalars: bytes
    trees: tuple[_TreeRef, ...]
    verdicts: tuple[TreeVerdict, ...]
    views: list[tuple[Any, str]] = field(default_factory=list)
    # Inside a session: the session-less key, whose entry may serve this call
    # only through complete capability rows (the bridge re-checks them).
    fallback_key: str | None = None


class _Hit:
    """A verified, not yet applied hit (``probe`` returns one; ``apply`` serves it)."""

    def __init__(self, store: "VerifiedStore", entry: Entry, prepared: _Prepared,
                 views: list[tuple[Any, str]], *, deferred: bool = False, key: str | None = None) -> None:
        self.store, self.entry, self.prepared, self.views = store, entry, prepared, views
        self.deferred = deferred
        self.key = prepared.key if key is None else key  # the key the entry is stored under

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
        self._serving_disabled = False  # a blind run's store after any defect

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
        """Record a defect. On a blind (real) run it is never raised: it is
        counted in the restricted tier and the store serves nothing more."""

        with self._lock:
            if self.mode.blind:
                self._counters[f"defect:{kind}"] = self._counters.get(f"defect:{kind}", 0) + 1
                self._serving_disabled = True
                return
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
                raw = os.fspath(value)
                if not isinstance(raw, str):
                    raise _Bypass("tree argument is not a text path")
                root = os.fspath(Path(raw).resolve(strict=False))
                spelled = os.path.abspath(raw)
                if spec.path_free:
                    spelled_name, root_name = os.path.basename(spelled), os.path.basename(root)
                    name = root_name if spelled_name == root_name else f"{spelled_name}\0{root_name}"
                else:
                    name = root if spelled == root else f"{spelled}\0{root}"
                spellings = tuple(dict.fromkeys((raw, str(Path(raw)), spelled, root)))
                trees.append(_TreeRef(root, name, spec.path_free, spellings))
        scope = _current_scope()
        verdicts: list[TreeVerdict] = []
        with _suspended():
            for tree in trees:
                verdict = scope.verify_tree(tree.root, tree.content_only)
                if verdict is None:
                    raise _Bypass("tree not hashable")
                verdicts.append(verdict)
        # A capability path and, outside a session, its session-less recording
        # twin (``v2_authentication_path`` while recording) are one kind: the
        # twin's reads are recorded exactly where the capability's register.
        # Inside a session the twin is a plain path (it never routes through a
        # session, so its reads register nothing) and is keyed as one.
        module = _AUTH.module()
        in_session = _AUTH.session() is not None
        kinds = ("V2AuthenticationPath",) if in_session else ("V2AuthenticationPath", "_RecordedAuthenticationPath")
        capabilities = tuple(kind for kind in (getattr(module, name, None) for name in kinds)
                             if isinstance(kind, type))
        tree_types = tuple(
            "v2-capability" if capabilities and isinstance(arguments[name], capabilities) else "path"
            for name, role in spec.params if role == TREE)
        prepared = _Prepared(spec, "", arguments, scalars, tuple(trees), tuple(verdicts))
        prepared.views = self._views(prepared)
        # Which physics entries the call consults (not their values) is call
        # context: a session cache, a run-partition view, or none.
        # Session presence is part of the key: a leaf's value may depend on it
        # (a read that is strict only in a session). A call inside a session
        # may still use a session-less entry, but only through its complete
        # capability rows, which the bridge re-checks (``fallback_key``).
        material = (
            SCHEMA, self.commit, code_digest(), environment_digest(), spec.leaf_id, scalars,
            tree_types, tuple((tree.name, verdict.digest) for tree, verdict in zip(trees, verdicts)),
            tuple(sorted(key for _, key in prepared.views)),
        )
        prepared.key = canonical_digest(material + ("session" if in_session else "sessionless",))
        if in_session:
            prepared.fallback_key = canonical_digest(material + ("sessionless",))
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

    @staticmethod
    def _layers(view: Any, key: str) -> tuple[Any, Any]:
        """(local layer, partition layer) for ``key``: a value, ABSENT, or None (no such visible layer).

        A run view has both (its local layer is None when it is a probe's
        ``_PrivateLocal``); a plain dict is a local layer only (None when private).
        """

        local = getattr(view, "_local", None)
        store = getattr(view, "_store", None)
        if isinstance(local, dict) and isinstance(store, dict):
            partition = store.get(getattr(view, "_key", None))
            shared = partition.get(key, ABSENT) if isinstance(partition, dict) else ABSENT
            return (None if isinstance(local, _PrivateLocal) else local.get(key, ABSENT)), shared
        if isinstance(view, dict):
            return (None if isinstance(view, _PrivateLocal) else dict.get(view, key, ABSENT)), None
        raise _Bypass("unknown physics view")

    @classmethod
    def _layer_same(cls, left: Any, right: Any) -> bool:
        if left is None or right is None:
            return left is right
        return cls._same(left, right)

    @classmethod
    def _kind(cls, before: tuple[Any, Any], after: tuple[Any, Any], visible_before: Any,
              visible_after: Any) -> str:
        """The fill's ``_PHYSICS_KINDS`` for one key; raises ``_Bypass`` for any other pattern."""

        (local_before, shared_before), (local_after, shared_after) = before, after
        if visible_before is ABSENT and visible_after is ABSENT:
            if cls._layer_same(local_before, local_after) and cls._layer_same(shared_before, shared_after):
                return "absent"
            raise _Bypass("physics layers changed while nothing was visible")
        if visible_before is ABSENT:
            if ((local_before is None or cls._same(local_after, visible_after))
                    and (shared_before is None or cls._same(shared_after, visible_after))):
                return "set"
            raise _Bypass("physics write outside the reducer's pattern")
        if local_before is ABSENT:
            if cls._same(local_after, visible_after) and cls._layer_same(shared_after, shared_before):
                return "promote"
            if local_after is ABSENT and cls._layer_same(shared_after, shared_before):
                return "noconsult"
            raise _Bypass("physics promotion outside the reducer's pattern")
        if cls._layer_same(local_after, local_before) and cls._layer_same(shared_after, shared_before):
            return "opaque"
        raise _Bypass("a visible physics value changed")

    def _physics_plan(self, entry: Entry, views: list[tuple[Any, str]]) -> list[tuple[Any, str, str, Any]]:
        """What serving ``entry`` must do to each view so its layers end as the serial call's would.

        Returns (view, key, operation, value) with operation ``promote`` (copy
        the partition entry into the empty local layer, as ``get`` does) or
        ``write`` (``view[key] = P``, as the reducer's insert does); raises
        ``_Bypass`` where the serial effect is not determined by the fill.
        """

        posts = {key: after for key, _, after in entry.physics}
        kinds = dict(entry.physics_kinds)
        plan: list[tuple[Any, str, str, Any]] = []
        for view, key in views:
            kind = kinds.get(key, "opaque")
            if kind not in _PHYSICS_KINDS:
                raise _Bypass("unknown physics kind")
            post = posts[key]
            if kind in ("absent", "noconsult"):
                continue
            local, shared = self._layers(view, key)
            if local is not None and local is not ABSENT:
                continue  # the serial get reads the local layer and changes nothing
            if shared is not None and shared is not ABSENT:
                if local is None:
                    continue  # no caller-visible local layer to promote into
                if kind == "opaque":
                    raise _Bypass("promotion depends on whether the leaf consulted the key")
                plan.append((view, key, "promote", shared))
                continue
            if local is None and shared is None:
                continue  # nothing caller-visible
            if kind != "set":
                raise _Bypass("nothing visible and no fit observed")
            plan.append((view, key, "write", post))
        return plan

    @staticmethod
    def _planned_layers(layers: tuple[Any, Any], operation: str | None, value: Any) -> tuple[Any, Any]:
        local, shared = layers
        if operation == "promote":
            return value, shared
        if operation == "write":
            return (None if local is None else value), (None if shared is None else value)
        return layers

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
            if self._serving_disabled or prepared.key in self._poisoned:
                return None
            key = prepared.key
            entry = self._entries.get(key)
            if entry is None and prepared.fallback_key is not None and prepared.fallback_key not in self._poisoned:
                fallback = self._entries.get(prepared.fallback_key)
                if fallback is not None and fallback.rows is not None:
                    key, entry = prepared.fallback_key, fallback
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
        return _Hit(self, entry, prepared, views, key=key)

    def _verify(self, entry: Entry, prepared: _Prepared) -> list[tuple[Any, str]] | None:
        scope = _current_scope()
        with _suspended():
            if not scope.prefetched:
                scope.prefetched = True
                self._prefetch_siblings(scope, prepared)
            # Sol wave-2 #2: every extra read and listing reached through a
            # pathname that is not its own target must still reach that target.
            for original, resolved in entry.aliases:
                if os.path.realpath(original) != resolved:
                    return None
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
        try:
            self._physics_plan(entry, views)
        except _Bypass:
            return None  # Sol wave-2 #1: the serial layer effect is not replayable here
        if _AUTH.session() is not None and entry.rows is None:
            return None
        return views

    def _prefetch_siblings(self, scope: _Scope, prepared: _Prepared) -> None:
        if prepared.spec.path_free or not prepared.trees:
            return
        parents = {os.path.dirname(tree.root) for tree in prepared.trees}
        with self._lock:
            roots = sorted({_identity_root(identity) for entry in self._entries.values() if not _path_free(entry)
                            for identity, _ in entry.trees
                            if os.path.dirname(_identity_root(identity)) in parents})
        scope.prefetch([(root, False) for root in roots])

    @staticmethod
    def _relocate(prepared: _Prepared, index: int, identity: str, label: str) -> tuple[str, str]:
        if index < 0:
            return identity, label
        root = prepared.trees[index].root
        return (os.path.join(root, identity) if identity else root), label.replace(_ROOT_MARK, root)

    def _apply(self, hit: _Hit, *, dry: bool = False, session: Any = None) -> Any:
        """Serve the hit: register its rows, insert its physics, return a fresh value.

        ``dry`` (shadow mode) runs the identical admission, bridge and
        registration against ``session`` (a scratch copy of the consumer's
        session, or None) and returns ``(value, {key: (operation, value)})`` without
        touching the real session, the views or any recorder.
        """

        entry, prepared = hit.entry, hit.prepared
        if hit.deferred:
            # Probed earlier (a pool pre-filter): re-verify at the serial position.
            with self._lock:
                if (hit.key in self._poisoned or prepared.key in self._poisoned
                        or self._entries.get(hit.key) is not entry):
                    raise _Bypass("entry changed since the probe")
            scope = _current_scope()
            with _suspended():
                for tree, verdict in zip(prepared.trees, prepared.verdicts):
                    current = scope.verify_tree(tree.root, tree.content_only)
                    if current is None or current.digest != verdict.digest:
                        raise _Bypass("tree changed since the probe")
            if self._verify(entry, prepared) is None:
                raise _Bypass("hit no longer admissible")
        # The serial leaf would run where this frame is (or shallower): a
        # row's depth below its fill, replayed below here, bounds its read.
        headroom = _stack_headroom()
        if not dry:
            session = _AUTH.session()
        rows: list[_Row] = []
        if entry.rows is not None:
            for index, identity, digest, grammar, caller_grammar, label, depth in entry.rows:
                identity, label = self._relocate(prepared, index, identity, label)
                rows.append(_Row(identity, digest, grammar, caller_grammar, label, depth))
        # Sol wave-2 #1: leave every caller-visible layer exactly as the
        # serial call would (a promotion into an empty local layer included).
        # Planned before any registration: a plan that refuses touches nothing.
        plan = self._physics_plan(entry, hit.views)
        if session is not None:
            if entry.rows is None:
                raise _Bypass("rows incomplete for a session")
            self._bridge(session, rows, prepared, headroom)
        value = pickle.loads(entry.value)
        if dry:
            return value, {key: (operation, stored) for _, key, operation, stored in plan}
        for view, key, operation, stored in plan:
            if operation == "promote":
                view._local[key] = stored
            else:
                view[key] = stored
        with self._lock:
            self._served[hit.key] = self._served.get(hit.key, 0) + 1
        self._forward(entry, prepared, rows, headroom)
        return value

    def _bridge(self, session: Any, rows: list[_Row], prepared: _Prepared, headroom: int) -> None:
        """Grammar verdicts under the consumer's grammar, then pre-checked registration.

        Each json/jsonl verdict is decided at the depth the serial read would
        parse at (``headroom`` less the row's depth): a verdict that may depend
        on the stack there is not served (D-188 AUTH-IO-2).
        """

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
                    read_headroom = None if row.depth is None else headroom - row.depth
                    grammar = _AUTH.ensure_verdict(session, row.identity, raw, digest, row.caller_grammar,
                                                   row.label, read_headroom)
                    if grammar is None:
                        raise _Bypass("grammar verdict may depend on the stack")
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

    def _forward(self, entry: Entry, prepared: _Prepared, rows: list[_Row], headroom: int) -> None:
        fills = _FILLS.get()
        if not fills:
            return
        trees = [(tree.root, tree.content_only, verdict.digest)
                 for tree, verdict in zip(prepared.trees, prepared.verdicts)]
        for fill in fills:
            if entry.rows is None:
                fill.rows_incomplete = True
            fill.forwarded_trees.extend(trees)
            fill.forwarded_trees.extend(entry.extra_trees)
            fill.forwarded_extras.extend(entry.extras)
            fill.forwarded_listings.extend(entry.listings)
            fill.forwarded_aliases.extend(entry.aliases)
        if rows:
            _AUTH.forward_rows(rows, headroom)

    # -- shadow -----------------------------------------------------------------

    def _shadow(self, hit: _Hit, fn: Callable[..., Any], args: tuple, kwargs: dict) -> Any:
        """Serve a sampled hit into a scratch copy, recompute it for real, compare.

        First the hit goes through the identical ``_apply`` (admission, bridge
        verdicts, pre-checked registration, physics inserts) against a scratch
        copy of the consumer's session. If that refuses, the hit would not have
        been served in ``on`` mode either: the call is a plain miss (the leaf
        runs, any V2 refusal is the serial one, no defect). Otherwise the leaf
        runs in the real session, and a defect is recorded if it raises, or if
        its value, its physics post-values, the physics the caller now sees or
        the session's records (identity, sha256, grammar, read count, strict
        parse) differ from what serving the hit would have produced. The
        caller always gets the freshly computed value.
        """

        leaf_id = hit.prepared.spec.leaf_id
        session = _AUTH.session()
        try:
            scratch = None if session is None else _scratch_session(session)
            _, planned = self._apply(hit, dry=True, session=scratch)
        except Exception:  # noqa: BLE001 - not admissible here: exactly an on-mode discarded hit
            self._count(f"{leaf_id}:hit_discarded")
            return self._fill(hit.prepared, fn, args, kwargs)
        self._count(f"{leaf_id}:shadow")
        layers_before = {key: self._layers(view, key) for view, key in hit.views}
        outcome: dict[str, Any] = {}
        try:
            value = self._fill(hit.prepared, fn, args, kwargs, outcome=outcome)
        except BaseException:
            if not isinstance(sys.exc_info()[1], (KeyboardInterrupt, SystemExit)):
                self._shadow_defect(hit, "shadow_raised")
            raise
        if not outcome.get("comparable"):
            self._count(f"{leaf_id}:shadow_incomparable")
            return value
        stored_physics = {key: after for key, _, after in hit.entry.physics}
        same_physics = all(self._same(stored_physics.get(key, ABSENT), after)
                           for key, after in outcome.get("physics", {}).items())
        try:
            # Every caller-visible layer (not only the visible value): an
            # omitted promotion into a local layer is a mismatch (Sol wave-2 #1).
            same_visible = True
            for view, key in hit.views:
                expected = self._planned_layers(layers_before[key], *planned.get(key, (None, None)))
                actual = self._layers(view, key)
                same_visible = same_visible and all(self._layer_same(left, right)
                                                    for left, right in zip(expected, actual))
        except Exception:  # noqa: BLE001 - an unreadable view after the recompute is a mismatch
            same_visible = False
        same_records = scratch is None or _record_map(scratch) == _record_map(session)
        if not (_same_value(outcome.get("value"), hit.entry.value) and same_physics
                and same_visible and same_records):
            self._shadow_defect(hit, "shadow_mismatch")
        return value

    def _shadow_defect(self, hit: _Hit, kind: str) -> None:
        leaf_id = hit.prepared.spec.leaf_id
        self._count(f"{leaf_id}:shadow_mismatch")
        self._defect(f"{leaf_id}:{kind}")
        with self._lock:
            self._poisoned.add(hit.key)
            self._entries.pop(hit.key, None)
            self._new.discard(hit.key)

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
            layers_before = [self._layers(view, key) for view, key in views]
            dicts = _physics_dicts(prepared, views)
            physics_before = [(item, dict(item)) for item in dicts]
        except Exception:  # noqa: BLE001 - an unprobeable call is computed, never stored
            views, before, layers_before, physics_before, storable = [], [], [], [], False
        session = _AUTH.session()
        snapshot = None
        if session is not None:
            with session._lock:
                snapshot = {identity: record.read_count for identity, record in session._records.items()}
        fill = _Fill()
        fill.headroom = _stack_headroom()
        _install_hook()
        token = _FILLS.set(_FILLS.get() + (fill,))
        observed = _raise_monitor_enter()
        if not observed and not _AUTH.records_failures():
            fill.unstorable.add("v2_failures_unobservable")
        try:
            with _AUTH.recording() as recorded:
                value = fn(*args, **kwargs)
        finally:
            if observed:
                _raise_monitor_exit()
            _FILLS.reset(token)
        if fill.v2_failed or any(getattr(row, "failed", False) for row in recorded or ()):
            storable = False
        if not storable:
            self._count(f"{leaf_id}:unstorable")
            return value
        try:
            entry = self._entry(prepared, fill, value, views, before, session, snapshot, recorded,
                                caches, deadline, firings_before, physics_before, layers_before)
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
               physics_before: list[tuple[dict, dict]],
               layers_before: list[tuple[Any, Any]]) -> Entry | None:
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
            kinds: list[tuple[str, str]] = []
            for (view, key), visible_before, layers in zip(views, before, layers_before):
                after = self._peek(view, key)
                if after is not ABSENT and type(after) is not float:
                    return None
                if visible_before is not ABSENT and not self._same(visible_before, after):
                    return None
                physics.append((key, visible_before, after))
                kinds.append((key, self._kind(layers, self._layers(view, key), visible_before, after)))
            extras, listings, extra_trees, aliases = self._classify(prepared, fill, recorded)
            try:
                payload = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
            except Exception:  # noqa: BLE001 - an unpicklable value is not stored
                return None
            rows = self._rows(prepared, session, snapshot, recorded, fill=fill, payload=payload)
            if prepared.spec.path_free and _embeds_location(prepared.trees, value, payload):
                return None
        return Entry(
            prepared.spec.leaf_id, payload,
            tuple((tree.name, verdict.digest) for tree, verdict in zip(prepared.trees, prepared.verdicts)),
            extras, listings, extra_trees, tuple(physics), rows,
            physics_kinds=tuple(kinds), aliases=aliases,
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
        # Sol wave-2 #2: a read is bound to the pathname the leaf used, not
        # only to its target. A pathname that is not its own target is kept
        # as an alias (re-resolved on every hit); a relative pathname is
        # always kept, so a hit re-resolves it against its own cwd; a read
        # into a tree is covered by the tree only through one of that tree's
        # own absolute spellings (a relative read into a tree is unstorable).
        spellings = [tuple(dict.fromkeys([tree.root] + [os.path.normpath(spelling) for spelling in tree.spellings
                                                       if os.path.isabs(spelling)]))
                     for tree in prepared.trees]
        aliases: dict[str, str] = {}

        def bind(original: str, resolved: str) -> None:
            if original != resolved and aliases.setdefault(original, resolved) != resolved:
                raise _Bypass("a pathname reached two targets during the fill")

        def in_tree(original: str, resolved: str) -> bool:
            lexical = os.path.normpath(original)
            direct = os.pardir not in Path(original).parts
            if direct and any(within(lexical, spelling) for spelled in spellings for spelling in spelled):
                return True
            if any(within(resolved, root) for root in roots):
                raise _Bypass("tree read through an alias")
            return False

        extras: dict[str, str] = {}
        for path in fill.reads:
            resolved = os.path.realpath(path)
            if in_tree(path, resolved) or is_code(resolved):
                continue
            if os.path.isdir(resolved):
                # Review of #639: a directory opened by pathname (the no-follow
                # route reads a row relative to it) is bound like a file read,
                # so retargeting any component of that pathname is a miss.
                bind(path, resolved)
                continue
            if any(within(resolved, parent) or within(os.path.normpath(path), parent) for parent in parents):
                raise _Bypass("path-free leaf read beside its tree")
            digest = scope.verify_file(resolved)
            if digest is None:
                raise _Bypass("extra read not hashable")
            extras[resolved] = digest
            bind(path, resolved)
        for row in recorded or ():
            identity = getattr(row, "identity", None)
            if identity and not identity.startswith("git:"):
                target = identity if identity in extras else os.path.realpath(identity)
                if target in extras and getattr(row, "sha256", None) != extras[target]:
                    raise _Bypass("extra read changed during the fill")
        listings: dict[str, str] = {}
        for path in fill.listings:
            resolved = os.path.realpath(path)
            if in_tree(path, resolved) or is_code(resolved):
                continue
            if any(within(resolved, parent) or resolved == parent or within(os.path.normpath(path), parent)
                   for parent in parents):
                raise _Bypass("path-free leaf listed beside its tree")
            digest = scope.verify_listing(resolved)
            if digest is None:
                raise _Bypass("listing not hashable")
            listings[resolved] = digest
            bind(path, resolved)
        for original, resolved in fill.forwarded_aliases:
            bind(original, resolved)
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
                tuple(sorted((root, content_only, digest) for (root, content_only), digest in extra_trees.items())),
                tuple(sorted(aliases.items())))

    def _rows(self, prepared: _Prepared, session: Any, snapshot: dict[str, int] | None, recorded: Any,
              *, fill: _Fill | None = None, payload: bytes = b""):
        try:
            return self._rows_with_depth(prepared, session, snapshot, recorded, fill=fill, payload=payload)
        except _DepthUnknown:
            return None

    def _rows_with_depth(self, prepared: _Prepared, session: Any, snapshot: dict[str, int] | None,
                         recorded: Any, *, fill: _Fill | None, payload: bytes):
        """The V2 registration rows a session would hold after the leaf, or None (session use barred).

        A session-less fill's rows serve a session only if the recorder says
        they are complete (``RECORDS_CAPABILITY_READS``) and none of these
        holds: the recording scope is ``unrepresented``; a row came from a
        session entered inside the fill; a hit served inside the fill had no
        rows; the value holds a capability path (a session's computation would
        return a registering ``V2AuthenticationPath`` there). Every row carries
        the depth of its read's parse below this fill (``_Row.depth``); an API
        row without a recorded ``parse_headroom`` bars session use.
        """

        reference = None if fill is None else fill.headroom

        def depth(row: Any) -> int | None:
            # Frames from the fill's reference down to the read's parse (an
            # upper bound); an API row without a usable headroom bars sessions.
            # A forwarded hit row without one stands for a replayed
            # registration (no parse at this position) and stays without.
            parse_headroom = getattr(row, "parse_headroom", None)
            if parse_headroom is None and getattr(row, "api", None) == "vdl.hit":
                return None
            if not isinstance(reference, int) or type(parse_headroom) is not int:
                raise _DepthUnknown
            return max(0, reference - parse_headroom)

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
                rows = [_Row(row.identity, row.sha256, row.grammar, row.caller_grammar, row.label, depth(row))
                        for row in api_rows]
            else:
                # A registration no API row accounts for was replayed from
                # elsewhere (no parse at this position: depth None); an identity
                # some API read also registered takes that read's deepest depth.
                deepest: dict[str, int] = {}
                for row in api_rows:
                    deepest[row.identity] = max(deepest.get(row.identity, 0), depth(row))
                for identity, increase in delta.items():
                    record = records[identity]
                    rows.extend(_Row(identity, record.sha256, record.grammar, record.grammar,
                                     f"member derivation input {identity}", deepest.get(identity))
                                for _ in range(increase))
        else:
            if recorded is None or not _AUTH.capability_complete():
                return None
            if getattr(recorded, "unrepresented", None) or (fill is not None and fill.rows_incomplete):
                return None
            if b"AuthenticationPath" in payload:
                return None
            for row in recorded:
                if str(getattr(row, "api", "")).startswith("session."):
                    return None
                if getattr(row, "identity", None) is None:
                    return None
                rows.append(_Row(row.identity, row.sha256, row.grammar, row.caller_grammar, row.label, depth(row)))
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
            stored.append((index, identity, row.sha256, row.grammar, row.caller_grammar, label, row.depth))
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
                base = entry if current.rows is None and entry.rows is not None else current
                kinds = _merged_kinds(current, entry)
                if base is not current or kinds != dict(current.physics_kinds):
                    self._entries[key] = replace(base, physics_kinds=tuple(sorted(kinds.items())))
                    self._new.add(key)
                return
            self._poison(key)

    def _poison(self, key: str) -> None:
        self._poisoned.add(key)
        self._entries.pop(key, None)
        self._new.discard(key)
        self._count("poison")
        if self._served.get(key):
            self._defect("poisoned_after_serving")

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
                    self._defect(defect)
            for key in payload.get("poisoned", ()):
                if isinstance(key, str) and key not in self._poisoned:
                    self._poison(key)
            for key, entry in dict(payload.get("entries", {})).items():
                if isinstance(key, str) and isinstance(entry, Entry):
                    self._insert(key, entry)
                    self._new.discard(key)


def _embeds_location(trees: Sequence[_TreeRef], value: Any, payload: bytes) -> bool:
    """Whether a path-free leaf's value may carry where its tree lives.

    Every spelling the caller could have used (its own argument, its absolute
    spelling, the resolved root) and each one's parent is searched for, both in
    the pickled bytes and in every string or path inside the value (a pickled
    ``Path`` stores its parts separately, so the bytes alone would miss it).
    """

    needles: set[str] = set()
    for tree in trees:
        for spelling in tree.spellings or (tree.root,):
            for needle in (spelling, os.path.dirname(spelling)):
                if needle and needle not in (os.sep, os.curdir):
                    needles.add(needle)
    if any(needle.encode("utf-8", "surrogatepass") in payload for needle in needles):
        return True
    return any(needle in text for text in _value_strings(value) for needle in needles)


def _value_strings(value: Any, depth: int = 0) -> Iterator[str]:
    """Every string, path and exception text reachable in a value (bounded depth)."""

    if depth > 64:
        yield ""  # too deep to inspect: the caller's search finds nothing here
        return
    if isinstance(value, str):
        yield value
    elif isinstance(value, PurePath):
        yield str(value)
    elif isinstance(value, (bytes, bytearray)):
        yield bytes(value).decode("utf-8", "surrogateescape")
    elif isinstance(value, Mapping):
        for key, item in value.items():
            yield from _value_strings(key, depth + 1)
            yield from _value_strings(item, depth + 1)
    elif isinstance(value, (list, tuple, set, frozenset)):
        for item in value:
            yield from _value_strings(item, depth + 1)
    elif isinstance(value, BaseException):
        yield str(value)
        yield from _value_strings(value.args, depth + 1)
    elif is_dataclass(value) and not isinstance(value, type):
        for item in fields(value):
            yield from _value_strings(getattr(value, item.name), depth + 1)
    elif hasattr(value, "__dict__") and not isinstance(value, type):
        yield from _value_strings(vars(value), depth + 1)


def _scratch_session(session: Any) -> Any:
    """A detached copy of a V2 session: same records and vocabulary, own lock, never active."""

    scratch = copy.copy(session)
    with session._lock:
        scratch._records = dict(session._records)
        vocabulary = getattr(session, "_governed_spec_vocabulary_identities", None)
        if isinstance(vocabulary, set):
            scratch._governed_spec_vocabulary_identities = set(vocabulary)
    scratch._lock = threading.RLock()
    if hasattr(scratch, "_token"):
        scratch._token = None
    return scratch


def _record_map(session: Any) -> dict[str, tuple[Any, ...]]:
    with session._lock:
        return {identity: (getattr(record, "sha256", None), getattr(record, "grammar", None),
                           getattr(record, "read_count", None), getattr(record, "strict_parse_succeeded", None))
                for identity, record in session._records.items()}


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


def _merged_kinds(current: Entry, entry: Entry) -> dict[str, str]:
    """Per physics key, the more informative kind of two agreeing fills (a tie keeps ``current``'s)."""

    merged = dict(current.physics_kinds)
    for key, kind in entry.physics_kinds:
        if _KIND_RANK.get(kind, 0) > _KIND_RANK.get(merged.get(key, "opaque"), 0):
            merged[key] = kind
    return merged


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
