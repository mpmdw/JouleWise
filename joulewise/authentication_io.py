"""Registration-at-read for the generalized v2 authentication route.

The active session is deliberately context-local.  Shared readers can use
the helpers in this module without changing historical/v1 behavior: when no
session is active they delegate directly to :class:`pathlib.Path`.  During a
v2 mint, every returned byte string has already been strict-parsed when its
wire grammar is JSON/JSONL and registered against its first observed digest.
"""

from __future__ import annotations

import ast
import builtins
import hashlib
import io
import json
import math
import os
import stat
import threading
from contextvars import ContextVar, Token
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, BinaryIO, Literal, Mapping, TextIO


AuthenticationGrammar = Literal["json", "jsonl", "raw"]
V2_AUTHENTICATION_INPUT_CHANGED = "v2_authentication_input_changed"


class V2AuthenticationInputError(RuntimeError):
    """A v2 authentication read failed before its bytes could be consumed."""

    def __init__(self, reason: str, detail: str) -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(f"{reason}: {detail}")


@dataclass(frozen=True)
class AuthenticationInputRecord:
    """The first digest and cumulative read count for one input identity."""

    normalized_path: str
    sha256: str
    grammar: AuthenticationGrammar
    read_count: int
    strict_parse_succeeded: bool


_ACTIVE_SESSION: ContextVar[V2AuthenticationReadSession | None] = ContextVar(
    "joulewise_v2_authentication_read_session", default=None
)


class V2AuthenticationPath(type(Path())):
    """A ``Path`` capability whose readable operations register returned bytes.

    ``pathlib`` preserves concrete subclasses through ``/``, ``parent``, and
    ``resolve``.  Those are the derivations used by the issued-pinned reducer,
    so an injected bundle root remains registration-aware all the way to the
    reducer's historical direct reads.  The methods retain ordinary ``Path``
    behavior when no v2 session is active.
    """

    __slots__ = ()

    def read_bytes(self) -> bytes:
        session = _ACTIVE_SESSION.get()
        if session is None:
            return super().read_bytes()
        return session.read(
            Path(self),
            grammar="raw",
            label=f"v2 path capability {self}",
        )

    def read_text(
        self,
        encoding: str | None = None,
        errors: str | None = None,
    ) -> str:
        session = _ACTIVE_SESSION.get()
        if session is None:
            return super().read_text(encoding=encoding, errors=errors)
        raw = session.read(
            Path(self),
            grammar="raw",
            label=f"v2 path capability {self}",
        )
        return raw.decode(encoding or "utf-8", errors or "strict")

    def open(
        self,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> BinaryIO | TextIO:
        session = _ACTIVE_SESSION.get()
        readable = "r" in mode or "+" in mode
        if session is None or not readable:
            return super().open(
                mode=mode,
                buffering=buffering,
                encoding=encoding,
                errors=errors,
                newline=newline,
            )
        if any(flag in mode for flag in ("w", "a", "x", "+")):
            raise ValueError("V2AuthenticationPath only supports read modes")
        raw = session.read(
            Path(self),
            grammar="raw",
            label=f"v2 path capability {self}",
        )
        buffer = io.BytesIO(raw)
        if "b" in mode:
            return buffer
        return io.TextIOWrapper(
            buffer,
            encoding=encoding or "utf-8",
            errors=errors or "strict",
            newline=newline,
        )


def v2_authentication_path(path: Path | str) -> Path:
    """Inject a registration-aware path only for an active v2 session."""

    if _ACTIVE_SESSION.get() is None:
        return Path(path)
    return V2AuthenticationPath(path)


def _duplicate_key(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise V2AuthenticationInputError(
                "v2_authentication_duplicate_json_key",
                f"duplicate JSON key {key!r}",
            )
        result[key] = value
    return result


def _nonfinite_number(value: str) -> None:
    raise V2AuthenticationInputError(
        "v2_authentication_nonfinite_json_number",
        f"non-finite JSON number {value!r}",
    )


def _finite_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        _nonfinite_number(value)
    return parsed


def _finite_int(value: str) -> int:
    parsed = int(value)
    try:
        finite_projection = math.isfinite(float(parsed))
    except OverflowError:
        finite_projection = False
    if not finite_projection:
        _nonfinite_number(value)
    return parsed


def _reserved_vocabulary_path(value: object, where: str) -> str | None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{where}.{key}"
            if key == "estimator_registration":
                return child_path
            nested = _reserved_vocabulary_path(child, child_path)
            if nested is not None:
                return nested
    elif isinstance(value, list):
        for index, child in enumerate(value):
            nested = _reserved_vocabulary_path(child, f"{where}[{index}]")
            if nested is not None:
                return nested
    return None


def _strict_json(
    raw: bytes,
    label: str,
    *,
    allow_governed_spec_vocabulary: bool = False,
) -> None:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_duplicate_key,
            parse_constant=_nonfinite_number,
            parse_float=_finite_float,
            parse_int=_finite_int,
        )
    except V2AuthenticationInputError as exc:
        raise V2AuthenticationInputError(exc.reason, f"{label}: {exc.detail}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise V2AuthenticationInputError(
            "v2_authentication_invalid_json",
            f"{label} is not valid UTF-8 JSON: {exc}",
        ) from exc
    forbidden = _reserved_vocabulary_path(value, label)
    if forbidden is not None and not allow_governed_spec_vocabulary:
        raise V2AuthenticationInputError(
            "v2_authentication_forbidden_json_key",
            "forbidden key 'estimator_registration' at " + forbidden,
        )


def _strict_jsonl(
    raw: bytes,
    label: str,
    *,
    allow_governed_spec_vocabulary: bool = False,
) -> None:
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise V2AuthenticationInputError(
            "v2_authentication_invalid_jsonl",
            f"{label} is not valid UTF-8 JSONL: {exc}",
        ) from exc
    for index, line in enumerate(lines, start=1):
        if line.strip():
            _strict_json(
                line.encode("utf-8"),
                f"{label} line {index}",
                allow_governed_spec_vocabulary=(
                    allow_governed_spec_vocabulary
                ),
            )


def _forced_grammar(identity: str, grammar: AuthenticationGrammar) -> AuthenticationGrammar:
    """Prevent JSON-looking paths from being downgraded to raw."""

    path_identity = identity.split(":", 2)[-1] if identity.startswith("git:") else identity
    suffix = Path(path_identity).suffix.lower()
    if suffix == ".json":
        return "json"
    if suffix == ".jsonl":
        return "jsonl"
    return grammar


def _parse_strict(
    raw: bytes,
    grammar: AuthenticationGrammar,
    label: str,
    *,
    allow_governed_spec_vocabulary: bool = False,
) -> None:
    if grammar == "json":
        _strict_json(
            raw,
            label,
            allow_governed_spec_vocabulary=allow_governed_spec_vocabulary,
        )
    elif grammar == "jsonl":
        _strict_jsonl(
            raw,
            label,
            allow_governed_spec_vocabulary=allow_governed_spec_vocabulary,
        )


def _read_nofollow_bytes(directory: Path | str, relative: str) -> bytes:
    root = Path(directory)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory_flags = flags | getattr(os, "O_DIRECTORY", 0) | nofollow
    descriptor = os.open(root, directory_flags)
    try:
        components = Path(relative).parts
        if not components or any(item in {"", ".", ".."} for item in components):
            raise ValueError("authentication input path is not contained")
        parent = descriptor
        owned_parent = False
        try:
            for component in components[:-1]:
                child = os.open(component, directory_flags, dir_fd=parent)
                if owned_parent:
                    os.close(parent)
                parent = child
                owned_parent = True
            artifact = os.open(components[-1], flags | nofollow, dir_fd=parent)
            try:
                if not stat.S_ISREG(os.fstat(artifact).st_mode):
                    raise ValueError(
                        f"authentication input is not a regular file: {root / relative}"
                    )
                chunks: list[bytes] = []
                while True:
                    chunk = os.read(artifact, 1024 * 1024)
                    if not chunk:
                        break
                    chunks.append(chunk)
                return b"".join(chunks)
            finally:
                os.close(artifact)
        finally:
            if owned_parent:
                os.close(parent)
    finally:
        os.close(descriptor)


class V2AuthenticationReadSession:
    """Context-scoped, first-digest-enforcing v2 input registry."""

    def __init__(self) -> None:
        self._records: dict[str, AuthenticationInputRecord] = {}
        self._governed_spec_vocabulary_identities: set[str] = set()
        self._lock = threading.RLock()
        self._token: Token[V2AuthenticationReadSession | None] | None = None
        self.instrument_calibration_physics_cache: dict[str, float] = {}

    def __enter__(self) -> V2AuthenticationReadSession:
        if self._token is not None:
            raise RuntimeError("V2AuthenticationReadSession cannot be re-entered")
        active = _ACTIVE_SESSION.get()
        if active is not None and active is not self:
            raise RuntimeError("a different V2AuthenticationReadSession is already active")
        self._token = _ACTIVE_SESSION.set(self)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self._token is None:
            raise RuntimeError("V2AuthenticationReadSession is not active")
        _ACTIVE_SESSION.reset(self._token)
        self._token = None

    @property
    def records(self) -> Mapping[str, AuthenticationInputRecord]:
        with self._lock:
            return MappingProxyType(dict(self._records))

    def allow_governed_extraction_spec(self, path: Path | str) -> None:
        """Allow registration declarations only for one named governed spec."""

        identity = str(Path(path).resolve(strict=False))
        if Path(identity).suffix.lower() != ".json":
            raise ValueError("governed extraction spec must be a JSON file")
        with self._lock:
            if identity in self._records:
                if identity in self._governed_spec_vocabulary_identities:
                    return
                raise RuntimeError(
                    "governed extraction spec vocabulary must be authorized "
                    "before the first authentication read"
                )
            self._governed_spec_vocabulary_identities.add(identity)

    def _register(
        self,
        identity: str,
        digest: str,
        grammar: AuthenticationGrammar,
        label: str,
    ) -> None:
        previous = self._records.get(identity)
        if previous is not None:
            if previous.sha256 != digest:
                raise V2AuthenticationInputError(
                    V2_AUTHENTICATION_INPUT_CHANGED,
                    f"{label} ({identity}) changed after its first authentication read",
                )
            if previous.grammar != grammar:
                raise V2AuthenticationInputError(
                    "v2_authentication_input_grammar_changed",
                    f"{label} ({identity}) changed grammar from "
                    f"{previous.grammar!r} to {grammar!r}",
                )
            self._records[identity] = AuthenticationInputRecord(
                normalized_path=identity,
                sha256=digest,
                grammar=grammar,
                read_count=previous.read_count + 1,
                strict_parse_succeeded=previous.strict_parse_succeeded,
            )
            return
        self._records[identity] = AuthenticationInputRecord(
            normalized_path=identity,
            sha256=digest,
            grammar=grammar,
            read_count=1,
            strict_parse_succeeded=grammar in {"json", "jsonl"},
        )

    def read(
        self,
        path: Path | str,
        *,
        grammar: AuthenticationGrammar,
        label: str,
    ) -> bytes:
        normalized = str(Path(path).resolve(strict=False))
        effective = _forced_grammar(normalized, grammar)
        with self._lock:
            with builtins.open(path, "rb") as handle:
                raw = handle.read()
            _parse_strict(
                raw,
                effective,
                label,
                allow_governed_spec_vocabulary=(
                    normalized in self._governed_spec_vocabulary_identities
                ),
            )
            self._register(
                normalized, hashlib.sha256(raw).hexdigest(), effective, label
            )
            return raw

    def read_nofollow(
        self,
        directory: Path | str,
        relative: str,
        *,
        grammar: AuthenticationGrammar,
        label: str,
    ) -> bytes:
        """Read a contained regular file without following any symlink."""

        root = Path(directory)
        identity = str((root / relative).resolve(strict=False))
        effective = _forced_grammar(identity, grammar)
        with self._lock:
            raw = _read_nofollow_bytes(root, relative)
            _parse_strict(
                raw,
                effective,
                label,
                allow_governed_spec_vocabulary=(
                    identity in self._governed_spec_vocabulary_identities
                ),
            )
            self._register(
                identity, hashlib.sha256(raw).hexdigest(), effective, label
            )
            return raw

    def ingest(
        self,
        identity: str,
        raw: bytes,
        *,
        grammar: AuthenticationGrammar,
        label: str,
    ) -> bytes:
        if not identity.startswith("git:"):
            raise ValueError("non-filesystem authentication identities must use git:")
        effective = _forced_grammar(identity, grammar)
        with self._lock:
            _parse_strict(
                raw,
                effective,
                label,
                allow_governed_spec_vocabulary=(
                    identity in self._governed_spec_vocabulary_identities
                ),
            )
            self._register(
                identity, hashlib.sha256(raw).hexdigest(), effective, label
            )
            return raw

    def sha256_streaming_raw(
        self,
        path: Path | str,
        *,
        label: str,
        chunk_size: int = 1024 * 1024,
    ) -> str:
        """Hash one large raw input and finish through the same registry."""

        normalized = str(Path(path).resolve(strict=False))
        effective = _forced_grammar(normalized, "raw")
        if effective != "raw":
            return hashlib.sha256(
                self.read(path, grammar=effective, label=label)
            ).hexdigest()
        with self._lock:
            digest = hashlib.sha256()
            with builtins.open(path, "rb") as handle:
                while True:
                    chunk = handle.read(chunk_size)
                    if not chunk:
                        break
                    digest.update(chunk)
            hexdigest = digest.hexdigest()
            self._register(normalized, hexdigest, "raw", label)
            return hexdigest


def active_v2_authentication_session() -> V2AuthenticationReadSession | None:
    return _ACTIVE_SESSION.get()


def read_authentication_input(
    path: Path | str,
    *,
    grammar: AuthenticationGrammar,
    label: str,
) -> bytes:
    session = _ACTIVE_SESSION.get()
    if session is None:
        return Path(path).read_bytes()
    return session.read(path, grammar=grammar, label=label)


def read_authentication_text(
    path: Path | str,
    *,
    grammar: AuthenticationGrammar,
    label: str,
    encoding: str | None = None,
    errors: str | None = None,
) -> str:
    session = _ACTIVE_SESSION.get()
    if session is None:
        kwargs: dict[str, str] = {}
        if encoding is not None:
            kwargs["encoding"] = encoding
        if errors is not None:
            kwargs["errors"] = errors
        return Path(path).read_text(**kwargs)
    raw = session.read(path, grammar=grammar, label=label)
    return raw.decode(encoding or "utf-8", errors or "strict")


def open_authentication_input(
    path: Path | str,
    mode: str = "r",
    *,
    grammar: AuthenticationGrammar,
    label: str,
    encoding: str | None = None,
    errors: str | None = None,
    newline: str | None = None,
) -> BinaryIO | TextIO:
    """Open an input while preserving ordinary file semantics outside v2."""

    if any(flag in mode for flag in ("w", "a", "x", "+")):
        raise ValueError("open_authentication_input only supports read modes")
    session = _ACTIVE_SESSION.get()
    if session is None:
        kwargs: dict[str, str | None] = {}
        if "b" not in mode:
            kwargs.update(encoding=encoding, errors=errors, newline=newline)
        return Path(path).open(mode, **kwargs)
    raw = session.read(path, grammar=grammar, label=label)
    buffer = io.BytesIO(raw)
    if "b" in mode:
        return buffer
    return io.TextIOWrapper(
        buffer,
        encoding=encoding or "utf-8",
        errors=errors or "strict",
        newline=newline,
    )


def read_authentication_input_nofollow(
    directory: Path | str,
    relative: str,
    *,
    grammar: AuthenticationGrammar,
    label: str,
) -> bytes:
    session = _ACTIVE_SESSION.get()
    if session is None:
        return _read_nofollow_bytes(directory, relative)
    return session.read_nofollow(
        directory, relative, grammar=grammar, label=label
    )


def ingest_git_authentication_input(
    relative_path: str,
    raw: bytes,
    *,
    grammar: AuthenticationGrammar = "json",
    label: str,
) -> bytes:
    session = _ACTIVE_SESSION.get()
    if session is None:
        return raw
    return session.ingest(
        f"git:HEAD:{relative_path}", raw, grammar=grammar, label=label
    )


def sha256_authentication_input(
    path: Path | str,
    *,
    label: str,
) -> str:
    session = _ACTIVE_SESSION.get()
    if session is None:
        digest = hashlib.sha256()
        with Path(path).open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()
    return session.sha256_streaming_raw(path, label=label)


def direct_read_violations(
    source: str,
    *,
    marked_functions: set[str] | frozenset[str],
) -> tuple[str, ...]:
    """Return direct readable-I/O calls inside a named authentication surface."""

    def _literal_mode(call: ast.Call, *, method: bool) -> str | None:
        mode_node: ast.AST | None = None
        position = 0 if method else 1
        if len(call.args) > position:
            mode_node = call.args[position]
        for keyword in call.keywords:
            if keyword.arg == "mode":
                mode_node = keyword.value
        if isinstance(mode_node, ast.Constant) and isinstance(mode_node.value, str):
            return mode_node.value
        return None

    def _readable_open(call: ast.Call, *, method: bool) -> bool:
        mode = _literal_mode(call, method=method)
        if mode is None:
            # builtins.open/Path.open default to readable text mode.  A dynamic
            # mode cannot be proven output-only and must therefore be rejected.
            return True
        return "r" in mode or "+" in mode

    def _readable_os_open(call: ast.Call) -> bool:
        flags_node: ast.AST | None = call.args[1] if len(call.args) >= 2 else None
        for keyword in call.keywords:
            if keyword.arg == "flags":
                flags_node = keyword.value
        if flags_node is None:
            return True
        write_only = False
        read_write = False
        for part in ast.walk(flags_node):
            if not isinstance(part, ast.Attribute) or not isinstance(
                part.value, ast.Name
            ) or part.value.id != "os":
                continue
            if part.attr == "O_WRONLY":
                write_only = True
            elif part.attr == "O_RDWR":
                read_write = True
        return read_write or not write_only

    tree = ast.parse(source)
    violations: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name not in marked_functions:
            continue
        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue
            target = child.func
            name: str | None = None
            if (
                isinstance(target, ast.Name)
                and target.id == "open"
                and _readable_open(child, method=False)
            ):
                name = "open"
            elif isinstance(target, ast.Attribute) and target.attr in {
                "read_bytes",
                "read_text",
            }:
                name = target.attr
            elif isinstance(target, ast.Attribute) and target.attr == "open":
                if isinstance(target.value, ast.Name) and target.value.id == "os":
                    if _readable_os_open(child):
                        name = "os.open"
                elif isinstance(target.value, ast.Name) and target.value.id in {
                    "io",
                    "codecs",
                }:
                    # Module-level open functions take (path, mode); reading
                    # args[0] as a bound-method mode would misparse the PATH
                    # as the mode string.
                    if _readable_open(child, method=False):
                        name = f"{target.value.id}.open"
                elif _readable_open(child, method=True):
                    name = "open"
            elif (
                isinstance(target, ast.Attribute)
                and target.attr == "fdopen"
                and isinstance(target.value, ast.Name)
                and target.value.id == "os"
                and _readable_open(child, method=False)
            ):
                name = "os.fdopen"
            if name is not None:
                violations.append(f"{node.name}:{child.lineno}:{name}")
    return tuple(sorted(set(violations)))


__all__ = [
    "AuthenticationInputRecord",
    "V2AuthenticationPath",
    "V2AuthenticationInputError",
    "V2AuthenticationReadSession",
    "V2_AUTHENTICATION_INPUT_CHANGED",
    "active_v2_authentication_session",
    "direct_read_violations",
    "ingest_git_authentication_input",
    "open_authentication_input",
    "read_authentication_input",
    "read_authentication_input_nofollow",
    "read_authentication_text",
    "sha256_authentication_input",
    "v2_authentication_path",
]
